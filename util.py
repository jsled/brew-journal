#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from decimal import Decimal, Context, ROUND_HALF_UP
import itertools

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
        

if __name__ == '__main__':
    import doctest
    doctest.testmod();
    print 'tests complete'
