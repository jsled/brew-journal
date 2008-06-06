import datetime
from django.db import models
from django.contrib import auth
import itertools
import urllib
from brewjournal import util

class StepType (object):
    def __init__(self, id, label, interesting_fields=None, next_steps=None):
        self._id = id
        self._label = label
        if not interesting_fields: interesting_fields = []
        if not next_steps: next_steps = []
        self._interesting_fields = interesting_fields
        self._next_steps = next_steps

    id = property(lambda s: s._id)
    label = property(lambda s: s._label)
    interesting_fields = property(lambda s: s._interesting_fields)
    next_steps = property(lambda s: s._next_steps)

    def is_terminal(self):
        return len(self.next_steps) == 0

# @fixme, add:
# - steep grains (extract, pm)
# - first-wort-hopping
#   - http://brewery.org/library/1stwort.html
# - starter / pre-pitch # time, volume
new_step_types = [ StepType('strike', 'strike water', ['volume', 'temp'], ['dough']),
                   StepType('dough', 'dough-in', ['volume', 'temp'], ['mash']),
                   StepType('mash', 'mash', ['time', 'temp'], ['recirc', 'vourlauf', 'sparge']),
                   StepType('recirc', 'recirculation', [], ['vourlauf', 'sparge']),
                   StepType('vourlauf', 'vourlauf', ['time'], ['sparge']),
                   StepType('sparge', 'sparge', ['volume', 'temp'], ['batch1-start', 'boil-start']),
                   StepType('batch1-start', '1st runnings, start', ['gravity'], ['batch1-end']),
                   StepType('batch1-end', '1st runnings, end', ['gravity', 'volume'], ['batch2-start', 'boil-start']),
                   StepType('batch2-start', '2nd runnings, start', ['gravity'], ['batch2-end']),
                   StepType('batch2-end', '2nd runnings, end', ['gravity', 'volume'], ['batch3-start', 'boil-start']),
                   StepType('batch3-start', '3rd runnings, start', ['gravity'], ['batch3-end']),
                   StepType('batch3-end', '3rd runnings, end', ['gravity', 'volume'], ['boil-start']),
                   StepType('boil-start', 'boil, start', ['time'], ['boil-add', 'boil-end']),
                   StepType('boil-add', 'boil, addition', ['time'], ['boil-add', 'boil-end']),
                   StepType('boil-end', 'boil, end', ['time'], ['pitch']),
                   StepType('pitch', 'pitch', [], ['ferm1']),
                   StepType('ferm1', 'primary fermentation', ['time', 'gravity', 'temp'], ['sample', 'ferm2', 'ferm-add', 'lager', 'keg', 'bottle', 'aging']),
                   StepType('ferm2', 'secondary fermentation', ['time', 'gravity', 'temp'], ['sample', 'ferm-add', 'lager', 'keg', 'bottle', 'aging']),
                   StepType('sample', 'gravity sample', ['gravity'], ['ferm-add', 'ferm2', 'sample','lager', 'keg', 'bottle', 'aging']),
                   StepType('ferm-add', 'addition', ['time'], ['sample', 'ferm-add', 'lager', 'keg', 'bottle', 'aging']),
                   StepType('lager', 'lagering', ['time', 'temp'], ['sample', 'condition', 'keg', 'bottle', 'aging']),
                   StepType('condition', 'conditioning', ['time', 'temp'], ['keg', 'bottle', 'aging']),
                   StepType('keg', 'kegged', ['time', 'temp', 'gravity'], ['consumed']),
                   StepType('bottle', 'bottled', ['time'], ['consumed']),
                   StepType('aging', 'aging', [], ['keg', 'bottle']),
                   StepType('consumed', 'consumed', [], []),
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
    ]

Volume_Units = [
    ('fl', 'fluid ounces'),
    ('c', 'cups'),
    ('q', 'quarts'),
    ('gl', 'gallons'),
    ('ml', 'milliliters'),
    ('l', 'liters')
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

    class Admin:
        pass


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

    class Admin:
        pass


class Hop (models.Model):
    name = models.CharField(max_length=100)
    aau_low = models.DecimalField(max_digits=3, decimal_places=1)
    aau_high = models.DecimalField(max_digits=3, decimal_places=1)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u'%(name)s' % self.__dict__

    class Admin:
        pass


class Adjunct (models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

    class Admin:
        pass


class YeastManufacturer (models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return u'%(name)s' % self.__dict__

    class Admin:
        pass


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

    class Admin:
        pass

class Recipe (models.Model):
    Types = (
        ('e', 'Extract'),
        ('p', 'Partial Mash'),
        ('a', 'All Grain'),
        )

    author = models.ForeignKey(auth.models.User)
    name = models.CharField(max_length=200)
    insert_date = models.DateTimeField(default=datetime.datetime.now)
    batch_size = models.DecimalField(max_digits=3, decimal_places=2)
    batch_size_units = models.CharField(max_length=2, choices = Volume_Units, default='gl')
    style = models.ForeignKey(Style, null=True)
    derived_from_recipe = models.ForeignKey('self', null=True, blank=True)
    type = models.CharField(max_length=1, choices=Types, default='a')
    source = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u'%(name)s - %(style)s %(batch_size)s' % {'name': self.name,
                                                         'style': self.style,
                                                         'batch_size': self.batch_size}

    def url(self):
        return u'/recipe/%d/%s' % (self.id, self.name)

    class Admin:
        pass


class RecipeGrain (models.Model):
    recipe = models.ForeignKey(Recipe)
    grain = models.ForeignKey(Grain)
    amount_value = models.DecimalField(max_digits=4, decimal_places=2)
    amount_units = models.CharField(max_length=2, choices=Weight_Units, default='lb')

    class Admin:
        pass


class RecipeHop (models.Model):
    recipe = models.ForeignKey(Recipe)
    hop = models.ForeignKey(Hop)
    amount_value = models.DecimalField(max_digits=4, decimal_places=2)
    amount_units = models.CharField(max_length=2, choices=Weight_Units)
    boil_time = models.SmallIntegerField()

    class Admin:
        pass


class RecipeYeast (models.Model):
    recipe = models.ForeignKey(Recipe)
    yeast = models.ForeignKey(Yeast)
    ideal = models.BooleanField(default=True)

    class Admin:
        pass


class RecipeAdjunct (models.Model):
    recipe = models.ForeignKey(Recipe)
    adjunct = models.ForeignKey(Adjunct)
    amount_value = models.DecimalField(max_digits=5, decimal_places=2)
    amount_units = models.CharField(max_length=2, choices=All_Units)
    boil_time = models.SmallIntegerField()
    notes = models.CharField(max_length=300, null=True, blank=True)

    class Admin:
        pass


class StarredRecipe (models.Model):
    '''
    A Recipe a User has specifically called out (to be turned into a Brew, or whatever).
    '''
    recipe = models.ForeignKey(Recipe)
    user = models.ForeignKey(auth.models.User)
    when = models.DateTimeField(default=datetime.datetime.now)
    notes = models.CharField(max_length=1000, blank=True, default='')

    class Admin:
        pass


class Brew (models.Model):
    #recipe_name = models.CharField(max_length=500)
    brew_date = models.DateTimeField('brew date',null=True, blank=True, default=datetime.datetime.now)
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

    class Admin:
        pass

    class Meta:
        ordering = ['brew_date', 'last_update_date']
    
    def update_from_steps(self, steps = None):
        '''
        Based on the type and timestamp of the latest step of `steps`, update the state of the Brew.
        It's the caller's responsibility to save the updated object.
        '''
        steps = steps or []
        if len(steps) > 0:
            last_step = steps[len(steps)-1]
            self.last_update_date = last_step.date
            self.last_state = last_step.type
            if step_types_by_id[last_step.type].is_terminal():
                self.is_done = True
            else:
                self.is_done = False
            if not self.brew_date:
                # @fixme; this could be better, taking the first actually-brewing-related step, rather than just index=0.
                self.brew_date = steps[0].date
        else:
            self.brew_date = None
            self.last_update_date = None
            self.last_state =  None
            self.is_done = False

    def next_step_types(self):
        '''@return a list of possible next step types.'''
        if self.last_state == None:
            # @fixme: move to StepType structure, factor out, &c.
            # @fixme: this is really a function of the type of recipe (extract, all-grain, &c.)
            return [step_types_by_id['strike'], step_types_by_id['boil-start']]
        step = step_types_by_id[self.last_state]
        return [step_types_by_id[next] for next in step.next_steps]



def get_likely_next_step_type_id(last_step_type_id):
    '''Given the last step, determine the likely next step, by StepType id'''
    global new_step_types
    global step_types_by_id
    last_step = step_types_by_id[last_step_type_id]
    if len(last_step.next_steps) > 0:
        return last_step.next_steps[0]
    return None


class Step (models.Model):
    '''
    Individual steps/events/readings/samples associated with the brew instance.
    '''
    brew = models.ForeignKey(Brew)
    type = models.CharField(max_length=30, choices=step_types_ui_choices)
    date = models.DateTimeField()
    entry_date = models.DateTimeField(editable=False, default=datetime.datetime.now)

    volume = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    volume_units = models.CharField(max_length=2, null=True, blank=True, choices = Volume_Units, default='gl')

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

    class Meta:
        ordering = ['date']

    class Admin:
        pass
