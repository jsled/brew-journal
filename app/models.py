import datetime
from django.db import models
from django.contrib import auth
import itertools

class Brew (models.Model):
    recipe_name = models.CharField(max_length=500)
    brew_date = models.DateTimeField('brew date',null=True, blank=True)
    brewer = models.ForeignKey(auth.models.User)
    recipe = models.TextField(null=True, blank=True)
    # last_updated date <= steps[-1].date
    # 'closed' <= steps[-1].is_terminal()

    def __str__(self):
        return self.__unicode__()
    def __unicode__(self):
        return u'%s (%s)' % (self.recipe_name, self.brewer.username)

    class Admin:
        pass


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
               ('condition', 'conditioning'), # terminal
               ('keg', 'kegged'), # terminal
               ('bottle', 'bottled'), # terminal
               ]

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
    volume = models.FloatField(null=True, blank=True)
    pre_temp = models.IntegerField(null=True, blank=True)
    post_temp = models.IntegerField(null=True, blank=True)
    gravity = models.FloatField(null=True, blank=True)
    notes = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u'[%s:%s:%s] vol=%s, temp %s -> %s, %s, [%s]' % (self.brew.recipe_name, self.date.strftime('%x %X'), self.type, self.volume, self.pre_temp, self.post_temp, self.gravity, self.notes)

    class Admin:
        pass
