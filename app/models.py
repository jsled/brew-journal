# -*- encoding: utf-8 -*-
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
from decimal import Decimal, Context, ROUND_HALF_UP

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
        pre_brews = [brew for brew in future_brews if pre_brew(brew)]
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
            temp = celsius_to_farenheit(self.gravity_read_temp)
        return correct_gravity(self.gravity_read, temp)

    def _set_gravity(self, gravity):
        self.gravity_read = gravity
        self.gravity_read_temp = 59
        self.gravity_read_temp_units = 'f'

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
    Find a user's pre-brews with a future "buy-ingredients" step, and consolidates the ingredients by type

    Each ingredient type is a list of (Ingredient,[(RecipeIngredient,Brew)])

    E.g., Grains -> (Centenniel, [ (5oz,Brew#42), (2oz,Brew#43), ...])
    
    ''' # '
    
    def __init__(self, user=None, **kwargs):
        self._grains = {}
        self._hops = {}
        self._adjuncts = {}
        self._yeasts = {}

        pre_brews = kwargs.get('pre_brews', None)
        if not pre_brews:
            now = datetime.datetime.now()
            future_buy_steps = Step.objects.filter(brew__brewer__exact=user, date__gt=now, type='buy')
            future_buy_brews = [step.brew.id for step in future_buy_steps]
            pre_brews = Brew.objects.filter(id__in=future_buy_brews)
        self._aggregate_brews(pre_brews)

    def shopping_to_do(self):
        to_buy_count = len(self._grains) + len(self._hops) + len(self._adjuncts) + len(self._yeasts)
        return to_buy_count > 0

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


class TimeConst:
    SECOND = 1000
    MINUTE = 60 * SECOND
    HOUR = 60 * MINUTE
    DAY = 24 * HOUR
    WEEK = 7 * DAY
    
def celsius_to_farenheit(temp):
    '''
    >>> celsius_to_farenheit(0.0)
    Decimal("32.00")
    >>> celsius_to_farenheit(100.0)
    Decimal("212.00")
    >>> celsius_to_farenheit(-17.78)
    Decimal("-0.004")
    '''
    temp = str(temp)
    if temp.lstrip('-').find('.') == -1:
        temp = temp + '.'
    parts = temp.split('.')
    prec = len(parts[0]) + len(parts[1])
    context = Context(prec=prec)
    _1_8 = context.create_decimal('1.8')
    _32 = context.create_decimal('32.')
    temp = context.create_decimal(temp)
    return _1_8 * temp + _32

_c1 = Decimal('1.313454')
_c2 = Decimal('0.132674')
_c3 = Decimal('0.002057793')
_c4 = Decimal('0.000002627634')
_adj = Decimal('0.001')
def correct_gravity(gravity, temp_f):
    '''
    All temperatures are in expressed in degrees F.

    correction = 1.313454 - 0.132674*F + 0.002057793*F*F - 0.000002627634*F*F*F

    SG_corrected = SG + (correction * 0.001)
    - http://www.primetab.com/formulas.html
    - agrees with http://brewery.org/library/HydromCorr0992.html


    >>> correct_gravity(1.042, 108)
    Decimal("1.050")
    >>> correct_gravity(1.050, 82)
    Decimal("1.053")
    >>> correct_gravity(1.0123103856, 59)
    Decimal("1.012")
    >>> correct_gravity(1.070, 41)
    Decimal("1.069")
    '''
    gravity = Decimal(str(gravity))
    F = Decimal(str(temp_f))
    ctx = Context(prec=4, rounding=ROUND_HALF_UP)
    gravity = gravity + (_c1 - _c2 * F + _c3 * F * F - _c4 * F * F *  F) * _adj
    return ctx.create_decimal(gravity)

def convert_volume_to_gls(volume, units):
    '''
    >>> convert_volume_to_gls(Decimal('16'), 'c')
    Decimal("1")
    >>> convert_volume_to_gls(Decimal('19000'), 'ml')
    Decimal("5.019284619855233264648385904")
    '''
    ctx = Context(prec=5)
    volume = ctx.create_decimal(volume)
    if units == 'fl':
        return volume / ctx.create_decimal('128')
    if units == 'c':
        return volume / ctx.create_decimal('16')
    if units == 'q':
        return volume / ctx.create_decimal('4')
    if units == 'ml':
        volume = volume / ctx.create_decimal('1000')
        units = 'l'
        # fallthrough…
    if units == 'l':
        return volume / ctx.create_decimal('3.7854')
    if units == 'gl':
        return volume
    # ('ct', 'count'),
    # ('tsp', 'teaspoon'),
    # ('tbsp', 'tablespoon'),
    # ('pt', 'pint')
    raise Exception('unknown units [%s]' % (units))


def convert_weight_to_lbs(amount, from_units):
    '''
    >>> convert_weight_to_lbs(1, 'kg')
    Decimal("2.20462")
    >>> convert_weight_to_lbs(16, 'oz')
    Decimal("1")
    >>> convert_weight_to_lbs(32, 'oz')
    Decimal("2")
    >>> convert_weight_to_lbs(1500, 'gr')
    Decimal("3.306930")
    '''
    ctx = Context(prec=6)
    if from_units == 'gr':
        amount = amount / ctx.create_decimal('1000.')
        from_units = 'kg'
        # fallthrough…
    if from_units == 'kg':
        return amount * ctx.create_decimal('2.20462')
    if from_units == 'oz':
        return amount / ctx.create_decimal('16.')
    if from_units == 'lb':
        return amount
    raise Exception('unknown units [%s]' % (from_units))


class BrewDerivations (object):
    def __init__(self, brew):
        self._brew = brew

    def _get_sorted_steps(self, allowable_step_types_sorted):
        allowable_types = dict([(type,idx)
                                for type,idx
                                in itertools.izip(allowable_step_types_sorted,itertools.count())])
        steps = self._brew.step_set.all()
        steps = [step for step in steps
                    if allowable_types.has_key(step.type)]
        steps.sort(lambda a,b: allowable_types[a.type] - allowable_types[b.type])
        return steps

    efficiency_needed_steps = ['boil-start', 'sparge', 'pitch']
    def _get_efficiency_steps(self):
        related_steps = self._get_sorted_steps(BrewDerivations.efficiency_needed_steps)
        related_steps = [step for step in related_steps if step.volume and step.gravity]
        return related_steps
    
    def can_not_derive_efficiency(self):
        '''@return A list of Strings describing what needs to be provided, or [] if we can perform the op'''
        rtn = []
        required = self._get_efficiency_steps()
        if len(required) == 0:
            rtn.append('need one step of of type %s with gravity and volume' % (BrewDerivations.efficiency_needed_steps))
        recipe_grains = self._brew.recipe.recipegrain_set.all()
        if len(recipe_grains) == 0:
            rtn.append('need grains on recipe')
        return rtn

    def efficiency(self):
        related_steps = self._get_efficiency_steps()
        if len(related_steps) == 0:
            raise Exception('assertion violation')
        best_step = related_steps[0]
        ctx = Context(prec=3, rounding=ROUND_HALF_UP)
        potential_points = ctx.create_decimal('0')
        for recipe_grain in self._brew.recipe.recipegrain_set.all():
            grain = recipe_grain.grain
            min,max = tuple([ctx.create_decimal(str(x - 1000)) for x in [grain.extract_min,grain.extract_max]])
            grain_potential_per_lb = (min + max) / ctx.create_decimal('2')
            grain_in_lbs = convert_weight_to_lbs(recipe_grain.amount_value, recipe_grain.amount_units)
            recipe_grain_potential = grain_potential_per_lb * grain_in_lbs
            potential_points += recipe_grain_potential
        volume_in_gallons = convert_volume_to_gls(best_step.volume, best_step.volume_units)
        grav = ((best_step.gravity - ctx.create_decimal('1')) * ctx.create_decimal('1000'))
        obtained_points = grav * volume_in_gallons
        efficiency = (obtained_points / potential_points) * ctx.create_decimal('100')
        return efficiency

    abv_start_steps = ['pitch', 'boil-end', 'boil-start']
    abv_end_steps = ['consumed', 'aging', 'bottle', 'keg', 'condition', 'lager', 'ferm-add', 'sample', 'ferm2', 'ferm1']
    def _get_abv_steps(self):
        starting_steps = self._get_sorted_steps(BrewDerivations.abv_start_steps)
        starting_steps = [step for step in starting_steps if step.gravity]
        ending_steps = self._get_sorted_steps(BrewDerivations.abv_end_steps)
        ending_steps = [step for step in ending_steps if step.gravity]
        return starting_steps,ending_steps

    def can_not_derive_abv(self):
        starting_steps,ending_steps = self._get_abv_steps()
        rtn = []
        if len(starting_steps) == 0:
            rtn.append('need a starting-gravity step of type %s with gravity reading' % (BrewDerivations.abv_start_steps))
        if len(ending_steps) == 0:
            rtn.append('need a ending-gravity step of type %s with gravity reading' % (BrewDerivations.abv_end_steps))
        return rtn

    def alcohol_by_volume(self):
        starting_steps,ending_steps = self._get_abv_steps()
        best_start = starting_steps[0]
        best_end = ending_steps[0]
        return (best_start.gravity - best_end.gravity) * Decimal('135')

    def can_not_derive_aa(self):
        return self.can_not_derive_abv()

    def apparent_attenuation(self):
        starting_steps,ending_steps = self._get_abv_steps()
        best_start = starting_steps[0]
        best_end = ending_steps[0]
        fraction_attenuated = (best_end.gravity - Decimal('1.0')) / (best_start.gravity - Decimal('1.0'))
        aa = (Decimal('1.0') - fraction_attenuated) * Decimal('100')
        return aa
