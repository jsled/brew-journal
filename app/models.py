import datetime
from django.db import models
from django.contrib import auth
import itertools

step_types = [ ('strike', 'strike water'),  # volume, temp
               ('dough', 'dough-in'), # volume, temp
               ('mash', 'mash'), # temp; more than one
               ('recirc', 'recirculation'), # ?
               ('vourlauf', 'vourlauf'), # mostly time
               ('sparge', 'sparge'), # volume, temp
               ('batch1-start', '1st runnings, start'), # temp, gravity
               ('batch1-end', '1st runnings, end'), # temp, gravity, volume
               ('batch2-start', '2nd runnings, start'),
               ('batch2-end', '2nd runnings, end'),
               ('batch3-start', '3rd runnings, start'),
               ('batch3-end', '3rd runnings, end'),
               ('boil-start', 'boil, start'),
               ('boil-add', 'boil, addition'),
               ('boil-end', 'boil, end'),
               ('pitch', 'pitch'), # only one?
               ('ferm1', 'primary fermentation'),
               ('ferm2', 'secondary fermentation'),
               ('ferm-add', 'addition'),
               ('lager', 'lagering'),
               ('condition', 'conditioning'),
               ('keg', 'kegged'),
               ('bottle', 'bottled'),
               ('aging', 'aging'),
               ('consumed', 'consumed'),
               ]

terminal_step_types = ['aging', 'consumed']

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
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=1000, blank=True)
    type = models.CharField(max_length=6, choices=Types)

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
    style = models.ForeignKey(Style)
    derived_from_recipe_id = models.ForeignKey('self', null=True, blank=True)
    type = models.CharField(max_length=1, choices=Types)
    source = models.CharField(max_length=300, blank=True, default='')
    private = models.BooleanField(default=False)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u'%(name)s - %(style)s %(batch_size)s' % {'name': self.name,
                                                         'style': self.style,
                                                         'batch_size': self.batch_size}

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

    class Admin:
        pass


class Brew (models.Model):
    #recipe_name = models.CharField(max_length=500)
    brew_date = models.DateTimeField('brew date',null=True, blank=True, default=datetime.datetime.now)
    brewer = models.ForeignKey(auth.models.User)
    notes = models.TextField(null=True, blank=True)
    recipe = models.ForeignKey(Recipe, null=True)
    last_update_date = models.DateTimeField(null=True, editable=False)
    last_state = models.CharField(max_length=30, choices=step_types, null=True, editable=False)
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
            if last_step.type in terminal_step_types:
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


def get_likely_next_step_type(last_step_type):
    '''Given the last step, determine the likely next step.'''
    global step_types
    last_step_idx = None
    for i,step in itertools.izip(itertools.count(),step_types):
        if step[0] == last_step_type:
            last_step_idx = i
            break
    if last_step_idx and last_step_idx <= len(step_types):
        return step_types[last_step_idx+1][0]
    return None


class Step (models.Model):
    '''
    Individual steps/events/readings/samples associated with the brew instance.
    '''
    brew = models.ForeignKey(Brew)
    type = models.CharField(max_length=30, choices=step_types)
    date = models.DateTimeField()
    entry_date = models.DateTimeField(editable=False, default=datetime.datetime.now)

    volume = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    volume_units = models.CharField(max_length=2, null=True, blank=True, choices = Volume_Units, default='gl')

    temp = models.IntegerField(null=True, blank=True)
    temp_units = models.CharField(max_length=1, null=True, blank=True, choices = Temp_Units, default='f')

    gravity = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    gravity_orig = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    gravity_orig_temp = models.IntegerField(null=True, blank=True)
    gravity_orig_temp_units = models.CharField(max_length=1, null=True, blank=True, choices = Temp_Units, default='f')

    notes = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u'[%s:%s:%s] vol=%s, temp=%s, gravity=%s, notes [%s]' % (self.brew.recipe.name, self.date.strftime('%x %X'), self.type, self.volume, self.temp, self.gravity, self.notes)

    class Meta:
        ordering = ['date']

    class Admin:
        pass
