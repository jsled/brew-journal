# Copyright (c) 2008-2009, Joshua Sled <jsled@asynchronous.org>
# 
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
# 
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
# 
#     * The names of its contributors may not be used to endorse or promote
#       products derived from this software without specific prior written
#       permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import datetime
from django.db import models
from django.contrib import auth
import itertools
import urllib
from brewjournal import util
from decimal import Decimal

class StepFilter (object):
    def __init__(self, conditions=None):
        self._conditions = conditions or []

    def eval(self, **kwargs):
        for condition in self._conditions:
            if not condition(**kwargs):
                return False
        return True

class StepType (object):
    def __init__(self, id, label, input_filter, interesting_fields=None, next_steps=None):
        self._id = id
        self._label = label
        self._input_filter = input_filter or StepFilter()
        if not interesting_fields: interesting_fields = []
        if not next_steps: next_steps = []
        self._interesting_fields = interesting_fields
        self._next_steps = next_steps

    id = property(lambda s: s._id)
    label = property(lambda s: s._label)
    interesting_fields = property(lambda s: s._interesting_fields)
    next_steps = property(lambda s: s._next_steps)
    input_filter = property(lambda s: s._input_filter)

    def is_terminal(self):
        return len(self.next_steps) == 0

RecipeTypes = (
    ('e', 'Extract'),
    ('p', 'Partial Mash'),
    ('a', 'All Grain'),
    )

DispenseTypes = (
    ('k', 'kegging'),
    ('b', 'bottling')
    )
    
class UserProfile (models.Model):
    user = models.ForeignKey(auth.models.User, unique=True)

    pref_brew_type = models.CharField(max_length=1, choices=RecipeTypes, default='a')
    pref_make_starter = models.BooleanField(default=False)
    pref_secondary_ferm = models.BooleanField(default=False)
    pref_dispensing_style = models.CharField(max_length=1, choices=DispenseTypes, default='b')

    def __getitem__(self, key):
        return self.__dict__.get(key, None)


def filter_user_pref(preference_name, value=True):
    def _foo(**kwargs):
        user = kwargs['user']
        profile = user.get_profile()
        return profile[preference_name] == value
    return _foo

def filter_recipe_type(types):
    def _foo(**kwargs):
        recipe = kwargs['recipe']
        return recipe.type in types
    return _foo

def filter_recipe_is_lager():
    return lambda **kw: True

def filter_recipe_estimated_og_above(val):
    return lambda **kw: True

no_filter = StepFilter()

# Other possible preferences/variants
# -----------------------------------
# practice fwh?
# typical sparge schedule: 1, 2, 3 steps?
# all_grain journal detail level:
#  - low: dough -> sparge -> boil-start
#  - medium: dough -> batch1-start -> batch1-end [-> batchN-start -> batchN-end] -> boil-start
#  - high:

# to get a graph of step relations/dependencies:
#
# ./manage.py shell
# from app import models
# print 'digraph G {';
# for step in models.new_step_types:
#   for next in step.next_steps:
#     print '%s -> %s;' % (step.id.replace('-', '_'), next.replace('-', '_'))
# print '}'
# | dot -Tpng -o step-graph.png -
new_step_types = [ StepType('buy', 'buy ingredients', no_filter, ['time'], ['starter', 'strike', 'steep']),
                   StepType('starter', 'make starter', StepFilter([filter_user_pref('pref_make_starter')]), ['time', 'volume'], ['strike', 'steep']),
                   StepType('strike', 'strike water', StepFilter([filter_recipe_type(['a', 'p'])]), ['volume', 'temp'],  ['dough', 'mash']),
                   StepType('dough', 'dough-in', no_filter, ['volume', 'temp'], ['mash', 'sparge']),
                   StepType('mash', 'mash', no_filter, ['time', 'temp'], ['recirc', 'vorlauf', 'sparge']),
                   StepType('recirc', 'recirculation', no_filter, [], ['vorlauf', 'sparge']),
                   StepType('vorlauf', 'vorlauf', no_filter, ['time'], ['sparge']),
                   StepType('sparge', 'sparge', no_filter, ['volume', 'temp'], ['batch1-start', 'boil-start']),
                   StepType('fwh', 'first wort hopping', no_filter, ['time'], ['batch1-start', 'boil-start']),
                   StepType('batch1-start', '1st runnings, start', no_filter, ['gravity'], ['batch1-end']),
                   StepType('batch1-end', '1st runnings, end', no_filter, ['gravity', 'volume'], ['batch2-start', 'boil-start']),
                   StepType('batch2-start', '2nd runnings, start', no_filter, ['gravity'], ['batch2-end']),
                   StepType('batch2-end', '2nd runnings, end', no_filter, ['gravity', 'volume'], ['batch3-start', 'boil-start']),
                   StepType('batch3-start', '3rd runnings, start', no_filter, ['gravity'], ['batch3-end']),
                   StepType('batch3-end', '3rd runnings, end', no_filter, ['gravity', 'volume'], ['boil-start']),
                   StepType('steep', 'steep', StepFilter([filter_recipe_type(['e', 'p'])]), ['time', 'volume', 'temp'], ['boil-start']),
                   StepType('boil-start', 'boil, start', StepFilter([filter_recipe_type(['e'])]), ['time'], ['boil-add', 'boil-end']),
                   StepType('boil-add', 'boil, addition', no_filter, ['time'], ['boil-add', 'boil-end']),
                   StepType('boil-end', 'boil, end', no_filter, ['time'], ['pitch']),
                   StepType('pitch', 'pitch', no_filter, ['time', 'gravity', 'volume', 'temp'], ['ferm1']),
                   StepType('ferm1', 'primary fermentation', no_filter, ['time', 'gravity', 'temp'], ['sample', 'ferm2', 'ferm-add', 'lager', 'keg', 'bottle', 'aging']),
                   StepType('ferm2', 'secondary fermentation', StepFilter([filter_user_pref('pref_secondary_ferm')]), ['time', 'gravity', 'temp'],
                            ['sample', 'ferm-add', 'lager', 'keg', 'bottle', 'aging']),
                   StepType('sample', 'gravity sample', no_filter, ['gravity'],
                            ['ferm-add', 'ferm2', 'sample','lager', 'keg', 'bottle', 'aging']),
                   StepType('ferm-add', 'addition', no_filter, ['time'], ['sample', 'ferm-add', 'lager', 'keg', 'bottle', 'aging']),
                   StepType('lager', 'lagering', StepFilter([filter_recipe_is_lager()]), ['time', 'temp'], ['sample', 'condition', 'keg', 'bottle', 'aging']),
                   StepType('condition', 'conditioning', no_filter, ['time', 'temp'], ['keg', 'bottle', 'aging']),
                   StepType('keg', 'kegged', StepFilter([filter_user_pref('pref_dispensing_style', 'k')]), ['time', 'temp', 'gravity'], ['consumed']),
                   StepType('bottle', 'bottled', StepFilter([filter_user_pref('pref_dispensing_style', 'b')]), ['time'], ['consumed']),
                   StepType('aging', 'aging', StepFilter([filter_recipe_estimated_og_above(Decimal('1.100'))]), [], ['keg', 'bottle']),
                   StepType('consumed', 'consumed', no_filter, [], []),
               ]

step_types_by_id = dict([(type.id, type) for type in new_step_types])
step_types_ui_choices = [(type.id, type.label) for type in new_step_types]

def flatten(*args):
    rtn = []
    for arg in args:
        rtn.extend(arg)
    return rtn


Weight_Units = [
    ('gr', 'grams'),
    ('kg', 'kilograms'),
    ('oz', 'ounces'),
    ('lb', 'pounds'),
    ('ct', 'count'),
    ]

Volume_Units = [
    ('fl', 'fluid ounces'),
    ('c', 'cups'),
    ('q', 'quarts'),
    ('gl', 'gallons'),
    ('ml', 'milliliters'),
    ('l', 'liters'),
    ('ct', 'count'),
    ('tsp', 'teaspoon'),
    ('tbsp', 'tablespoon'),
    ('pt', 'pint')
    ]

Temp_Units = [
    ('f', 'Farenheit'),
    ('c', 'Celsius')
    ]

All_Units = flatten(Weight_Units, Volume_Units)

class Style (models.Model):
    name = models.CharField(max_length=100)
    bjcp_code = models.CharField(max_length=8)
    parent = models.ForeignKey('self', null=True)

    def __str__(self):
        return self.__unicode__()
    
    def __unicode__(self):
        return u'%(name)s %(bjcp_code)s' % self.__dict__


class Grain (models.Model):
    name = models.CharField(max_length=200)
    extract_min = models.SmallIntegerField(null=True)
    extract_max = models.SmallIntegerField(null=True)
    lovibond_min = models.SmallIntegerField(null=True)
    lovibond_max = models.SmallIntegerField(null=True)
    description = models.CharField(max_length=200)
    group = models.CharField(max_length=8)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u'%(name)s' % self.__dict__


class Hop (models.Model):
    name = models.CharField(max_length=100)
    aau_low = models.DecimalField(max_digits=3, decimal_places=1)
    aau_high = models.DecimalField(max_digits=3, decimal_places=1)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u'%(name)s' % self.__dict__


class Adjunct (models.Model):
    name = models.CharField(max_length=100)
    group = models.CharField(max_length=30)

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.group)


class YeastManufacturer (models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return u'%(name)s' % self.__dict__


class Yeast (models.Model):
    Types = [
        ('ale', 'Ale'),
        ('belgian', 'Belgian'),
        ('brett', 'Brettanomyces'),
        ('lager', 'Lager'),
        ('lambic', 'Lambic'),
        ('wine', 'Wine'),
        ('mead', 'Mead'),
        ('cider', 'Cider'),
        ('weird', 'Speciality'),
        ]
    manufacturer = models.ForeignKey(YeastManufacturer)
    ident = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, blank=True)
    type = models.CharField(max_length=7, choices=Types)

    # @fixme: attenuation; min/max temp; URL; class
    #Flocc_Types = ['low', 'medium-low', 'medium', 'medium-high', 'high']
    #flocculation = models.CharField(max_length=10, choices=Floc_Types)
    #attenuation_low = models.IntegerField()
    #attenuation_high = models.IntegerField()
    #temp_low = models.IntegerField()
    #temp_high = models.IntegerField()
    #alc_tolerance = models.DecimalField(max_digits=3, decimal_places=1)

    def __unicode__(self):
        return u'%s %s: %s' % (self.manufacturer.name, self.ident, self.name)


class Recipe (models.Model):
    author = models.ForeignKey(auth.models.User)
    name = models.CharField(max_length=200)
    insert_date = models.DateTimeField(default=datetime.datetime.now)
    batch_size = models.DecimalField(max_digits=4, decimal_places=2)
    batch_size_units = models.CharField(max_length=4, choices = Volume_Units, default='gl')
    style = models.ForeignKey(Style, null=True)
    derived_from_recipe = models.ForeignKey('self', null=True, blank=True)
    type = models.CharField(max_length=1, choices=RecipeTypes, default='a')
    source_url = models.URLField(max_length=300, blank=True, null=True, verify_exists=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u'%(name)s - %(style)s %(batch_size)s' % {'name': self.name,
                                                         'style': self.style,
                                                         'batch_size': self.batch_size}

    def url(self):
        return u'/recipe/%d/%s' % (self.id, self.name)


class RecipeGrain (models.Model):
    recipe = models.ForeignKey(Recipe)
    grain = models.ForeignKey(Grain)
    amount_value = models.DecimalField(max_digits=4, decimal_places=2)
    amount_units = models.CharField(max_length=2, choices=Weight_Units, default='lb')


class RecipeHop (models.Model):
    recipe = models.ForeignKey(Recipe)
    hop = models.ForeignKey(Hop)
    amount_value = models.DecimalField(max_digits=4, decimal_places=2)
    amount_units = models.CharField(max_length=2, choices=Weight_Units)
    boil_time = models.SmallIntegerField()


class RecipeYeast (models.Model):
    recipe = models.ForeignKey(Recipe)
    yeast = models.ForeignKey(Yeast)
    ideal = models.BooleanField(default=True)


class RecipeAdjunct (models.Model):
    recipe = models.ForeignKey(Recipe)
    adjunct = models.ForeignKey(Adjunct)
    amount_value = models.DecimalField(max_digits=5, decimal_places=2)
    amount_units = models.CharField(max_length=4, choices=All_Units)
    boil_time = models.SmallIntegerField()
    notes = models.CharField(max_length=300, null=True, blank=True)


class StarredRecipe (models.Model):
    '''
    A Recipe a User has specifically called out (to be turned into a Brew, or whatever).
    '''
    recipe = models.ForeignKey(Recipe)
    user = models.ForeignKey(auth.models.User)
    when = models.DateTimeField(default=datetime.datetime.now)
    notes = models.CharField(max_length=1000, blank=True, default='')


class BrewManager (models.Manager):
    def brews_with_future_steps(self, user):
        brew_ids = [step.brew_id for step in Step.objects.future_steps_for_user(user)]
        return Brew.objects.filter(id__in=brew_ids)

    def brews_pre_brew(self, user):
        # @fixme: if the brew date is in the future, too?
        future_brews = Brew.objects.brews_with_future_steps(user)
        def pre_brew(brew):
            future_steps = brew.future_steps()
            # @fixme, this should probably be step.is_pre_brew() or something.
            substeps = [step for step in future_steps if step.type in ['buy', 'strike', 'steep']]
            return len(substeps) > 0
        pre_brews = [recipe for recipe in future_brews if pre_brew(recipe)]
        return pre_brews
        

class Brew (models.Model):
    # recipe_name = models.CharField(max_length=500)
    brew_date = models.DateTimeField('brew date', null=True, blank=True, default=datetime.datetime.now)
    brewer = models.ForeignKey(auth.models.User)
    notes = models.TextField(null=True, blank=True)
    recipe = models.ForeignKey(Recipe, null=True)
    last_update_date = models.DateTimeField(null=True, editable=False)
    last_state = models.CharField(max_length=30, choices=step_types_ui_choices, null=True, editable=False)
    is_done = models.BooleanField(editable=False, default=False)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u'%s (%s)' % (self.recipe.name, self.brewer.username)

    objects = BrewManager()

    class Meta:
        ordering = ['brew_date', 'last_update_date']
    
    def update_from_steps(self, steps = None):
        '''
        Based on the type and timestamp of the latest step of `steps`, update the state of the Brew.
        It's the caller's responsibility to save the updated object.
        '''
        # only allow non-future steps to update state.
        past_steps = [step for step in steps if not step.in_future()] or []
        if len(past_steps) > 0:
            last_step = past_steps[-1]
            self.last_update_date = last_step.date
            self.last_state = last_step.type
            self.is_done = step_types_by_id[last_step.type].is_terminal()
            if not self.brew_date:
                # @fixme; this could be better, taking the first actually-brewing-related step, rather than just index=0.
                # @fixme: then, get "is_actually_brewing_related" into StepTypes model
                self.brew_date = past_steps[0].date
        else:
            self.brew_date = None
            self.last_update_date = None
            self.last_state =  None
            self.is_done = False

    def next_steps(self):
        gennie = NextStepGenerator(self)
        return gennie.get_next_steps()
    
    def future_steps(self):
        return [step for step in self.step_set.all() if step.in_future()]

    def title(self):
        if not self.recipe:
            return "unnamed"
        return self.recipe.name


class StepManager (models.Manager):
    def future_steps_for_user(self, user):
        now = datetime.datetime.now()
        return Step.objects.filter(brew__brewer__exact=user, date__gt=now)


class Step (models.Model):
    '''
    Individual steps/events/readings/samples associated with the brew instance.
    '''
    brew = models.ForeignKey(Brew)
    type = models.CharField(max_length=30, choices=step_types_ui_choices)
    date = models.DateTimeField()
    entry_date = models.DateTimeField(editable=False, default=datetime.datetime.now)

    volume = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    volume_units = models.CharField(max_length=4, null=True, blank=True, choices = Volume_Units, default='gl')

    temp = models.IntegerField(null=True, blank=True)
    temp_units = models.CharField(max_length=1, null=True, blank=True, choices = Temp_Units, default='f')

    # gravity = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    gravity_read = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    gravity_read_temp = models.IntegerField(null=True, blank=True)
    gravity_read_temp_units = models.CharField(max_length=1, null=True, blank=True, choices = Temp_Units, default='f')

    notes = models.CharField(max_length=500, blank=True)

    def _get_gravity(self):
        if not self.gravity_read or not self.gravity_read_temp:
            return None
        temp = self.gravity_read_temp
        if self.gravity_read_temp_units == 'c':
            temp = util.celsius_to_farenheit(self.gravity_read_temp)
        return util.correct_gravity(self.gravity_read, temp)

    def _set_gravity(self, gravity):
        self._gravity_read = gravity
        self._gravity_read_temp = 59
        self._gravity_read_temp_units = 'f'

    gravity = property(_get_gravity, _set_gravity)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u'[%s:%s:%s] vol=%s, temp=%s, gravity=%s, notes [%s]' % (self.brew.recipe.name, self.date.strftime('%x %X'), self.type, self.volume, self.temp, self.gravity, self.notes)

    def in_future(self):
        # @fixme: inject datetime.datetime for testability
        return self.date > datetime.datetime.now()

    objects = StepManager()

    class Meta:
        ordering = ['date']


class NextStep (object):
    def __init__(self, type, date, existing_step=None):
        self.type = type
        self.date = date
        self.existing_step = existing_step

    def __unicode__(self):
        existing_part = u''
        if self.existing_step:
            existing_part = ' (existing id %d)' % (self.existing_step.id)
        date_part = u''
        if self.date:
            date_part = u' @ %s' % (self.date)
        return u'[%s%s%s]' % (self.type.id, date_part, existing_part)

    def __str__(self):
        return self.__unicode__()


class NextSteps (object):
    def __init__(self, possible=None, maybe=None):
        self.possible = possible or []
        self.maybe = maybe or []

    def __unicode__(self):
        return u'possible: %s, maybe: %s' % ([str(x) for x in self.possible],
                                             [str(x) for x in self.maybe])

    def __str__(self):
        return self.__unicode__()


class NextStepGenerator (object):
    '''
    Encapsulate the process of getting the next-step structure from a brew, user, prefs, &c.
    '''
    def __init__(self, brew, **kwargs):
        self._brew = brew
        self._user = kwargs.get('user', brew.brewer)
        self._recipe = brew.recipe

    def get_next_steps(self):
        next_steps = NextSteps()
        to_try = []
        last_date = None
        if self._brew.last_state:
            last_step_type = step_types_by_id[self._brew.last_state]
            try:
                last_step = [s for s in self._brew.step_set.all() if s.type == self._brew.last_state][0]
            except Exception,e:
                print 'brew,last_state,steps',self._brew,self._brew.last_state,self._brew.step_set.all()
                raise
            # @fixme: assert(last_step is not None)
            last_date = last_step.date
            to_try.extend(last_step_type.next_steps)
        else:
            # @fixme: get these from StepTypes themselves
            to_try.extend(['starter', 'strike', 'steep', 'boil-start'])
        future_steps = [step for step in self._brew.step_set.all() if step.in_future()]
        for typeid in to_try:
            steptype = step_types_by_id[typeid]
            appropriate_list = None
            if steptype.input_filter.eval(brew=self._brew, user=self._user, recipe=self._recipe):
                appropriate_list = next_steps.possible
            else:
                appropriate_list = next_steps.maybe
            #
            existing_step = None
            next_step_date = last_date
            matching_future_steps = [step for step in future_steps if step.type == typeid]
            if len(matching_future_steps) > 0:
                existing_step = matching_future_steps[0]
                if not next_step_date or existing_step.date > next_step_date:
                    next_step_date = existing_step.date
            #
            next_step = NextStep(steptype, next_step_date, existing_step)
            appropriate_list.append(next_step)
        return next_steps
       

class ShoppingList (object):
    '''
    takes a list of pre-brews, and consolidates the ingredients by type

    Each ingredient type is a list of (Ingredient,[(RecipeIngredient,Brew)])

    E.g., Grains -> (Centenniel, [ (5oz,Brew#42), (2oz,Brew#43), ...])
    
    '''
    
    def __init__(self, pre_brews):
        self._grains = {}
        self._hops = {}
        self._adjuncts = {}
        self._yeasts = {}
        self._aggregate_brews(pre_brews)

    def _get_grains(self):
        return [(grain,brews) for grain,brews in self._grains.iteritems()]
    grains = property(_get_grains)

    def _get_hops(self):
        return [(hop,brews) for hop,brews in self._hops.iteritems()]
    hops = property(_get_hops)

    def _get_adjuncts(self):
        return [(adjunct,brews) for adjunct,brews in self._adjuncts.iteritems()]
    adjuncts = property(_get_adjuncts)

    def _get_yeasts(self):
        return [(yeast,brews) for yeast,brews in self._yeasts.iteritems()]
    yeasts = property(_get_yeasts)
    
    def _aggregate_brews(self, pre_brews):
        for brew in pre_brews:
            recipe = brew.recipe
            if not recipe:
                continue
            for collection, recipe_item_getter, item_type_getter in \
                    [(self._grains, lambda: recipe.recipegrain_set.all(), lambda x: x.grain),
                     (self._hops, lambda: recipe.recipehop_set.all(), lambda x: x.hop),
                     (self._adjuncts, lambda: recipe.recipeadjunct_set.all(), lambda x: x.adjunct),
                     (self._yeasts, lambda: recipe.recipeyeast_set.all(), lambda x: x.yeast)]:
                for recipe_item in recipe_item_getter():
                    item = item_type_getter(recipe_item)
                    collection.setdefault(item, []).append((recipe_item,brew))
