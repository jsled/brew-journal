#!/usr/bin/env python

from decimal import Decimal, Context, ROUND_HALF_UP

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
    if temp.lstrip('-').index('.') == -1:
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

if __name__ == '__main__':
    import doctest
    doctest.testmod();
    print 'tests complete'
