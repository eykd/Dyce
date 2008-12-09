# -*- coding: utf-8 -*-
"""dice - a bag of dice, various shapes and sizes

$Author$
$Rev$
$Date$
"""

__author__ = "$Author$"
__version__ = "$Rev$"
__date__ = "$Date$"


import random

import logging
logger = logging.getLogger('dice')

__all__ = ['D10', 'Dice', 'DiceError', 'NotIntegerError', 
           'OutOfRangeError', 'ParetoLowDice', 'parse', 'roller']

class DiceError(Exception): pass
class OutOfRangeError(DiceError): pass
class NotIntegerError(DiceError): pass

def parse(d):
    """Parse a dice specifier string.  Return a dice specifier tuple.

    6-sided dice are the defaults.

    "3d10+1" returns (3, 10, 1)
    "4d-2" returns (4, 6, -2)
    "1d12" returns (1, 12, 0)
    """
    dice, dtype_mod = d.split('d')

    # Sane defaults.
    dnum = 1
    dtype = 6
    mod = 0
    mult = 1
    
    if dtype_mod:
        if '-' in dtype_mod:
            dtype, mod = dtype_mod.split('-')
            mod = -1*int(mod)
        elif '+' in dtype_mod:
            dtype, mod = dtype_mod.split('+')
            mod = int(mod)
        else:
            dtype = dtype_mod

    if not dtype: dtype = 6
    if not mod: mod = 0

    return (int(dice), int(dtype), int(mod))



class Dice(object):
    """A magic bag of dice.
    """
    def __init__(self, state=random.getstate()):
        self.init_state = state
        self.rand = random.Random()
        self.rand.setstate(state)

        self._cheat_next = []

    def roll(self, num=1, sides=6, mod=0, sort=False):
        """Return a list of num random ints between 1 and sides, each += mod.
        """
        _cn = self._cheat_next
        if _cn:
            return _cn.pop()

        try:
            num = int(num)
            sides = int(sides)
            mod = int(mod)
        except ValueError:
            raise NotIntegerError, 'arguments must be coercable to ints.'
        if num == 0 or sides == 0:
            return [0,]
        if not (num > 0):
            raise OutOfRangeError, 'number of dice out of range; must be >= 0'
        if not (sides > 0):
            raise OutOfRangeError, 'number of sides out of range; must be >= 0'
        results = []
        for i in range(num):
            results.append(self.rand.randrange(1, sides+1)+mod)
        if sort:
            results.sort()
        return results

    def rollsum(self, num=1, sides=6, each_mod=0, total_mod=0):
        """Return the sum of num rolls of sides-sided dice, with modifiers.
        """
        try:
            total_mod = int(total_mod)
        except ValueError:
            raise NotIntegerError, 'arguments must be coercable to ints.'
        results = self.roll(num, sides, each_mod)
        return sum(results) + total_mod

    def rollbell(self, min_num, max_num, dist_ratio=2.0):
        """Roll bell-shaped dice.

        Return a value between min_num and max_num.
        """
        mean_distance = (max_num - min_num) / 2.0
        mean = max_num - mean_distance
        sdev = abs(max_num - min_num) / dist_ratio
        result = self.rand.gauss(mean, sdev)
        # normalize
        result = min(result, max_num)
        result = max(result, min_num)
        return result

    def rollbellFloat(self, min_num, max_num):
        """Roll bell-shaped floating dice.

        Return a value on a bell curve distribution between min_num
        and max_num.
        """
        return float(self.rollbell(min_num, max_num))

    def rollbellInt(self, min_num, max_num):
        """Roll bell-shaped discrete dice.

        Return an integer value on a bell curve distribution between
        min_num and max_num.
        """
        return int(round(self.rollbell(min_num, max_num)))


    def reset(self):
        """Reset the random generator to initial state.
        """
        self.rand.setstate(self.init_state)

    def fuzz(self, num, ratio):
        """Fuzz the given number uniformly by the given ratio or tolerance.
        
        If ratio < 1, return a value within +-ratio*num of num.
        If ratio >= 1, return a value within +-ratio of num.
        
        @param num: any number
        @type num: float or int
        @param ratio: the ratio or distance to fuzz the number by.
        @type ratio: float
        """
        num = float(num)
        ratio = float(ratio)
        sign = self.rand.choice((1, -1))
        
        if ratio < 1:
            distance = (float(ratio))*num
        else:
            distance = ratio
        result = num + (self.rand.uniform(0, distance) * sign)
        return result

class ParetoLowDice(Dice):
    """Weighted dice, defaulting to low-rollers.

    for a = 10, the Pareto distribution falls neatly across the period
    1 < n < 2, with 1 being the most common and probability falling
    off as it approaches and exceeds 2.

    WARNING: This isn't tested very well yet.
    """
    def __init__(self, state=random.getstate(), alpha=10):
        super(ParetoLowDice, self).__init__(state)
        self.alpha = alpha
        
    def randParetoRange(self, low, high, alpha):
        """Pick an integer from the given range, using the pareto distribution.

        We'll distribute the given range across the pareto distribution between 1 and 2.
        """
        the_range = xrange(low, high)
        range_length = len(the_range)
        last_index = range_length-1
        portion = 1.0/range_length

        presult = self.rand.paretovariate(alpha)
        
        the_index = 0
        section = 1.0 + portion
        # Determine which portion the presult falls in.
        while section < presult:
            the_index += 1
            if the_index == last_index:
                # The pareto distribution will sometimes exceed 2.0.
                # We'll default to the last number in the range, in this case.
                break
            section += portion
        
        return the_range[the_index]
        

    def roll(self, num=1, sides=6, mod=0, sort=False, alpha=None):
        """Return a list of num random ints between 1 and sides, each += mod.
        """
        try:
            num = int(num)
            sides = int(sides)
            mod = int(mod)
        except ValueError:
            raise NotIntegerError, 'arguments must be coercable to ints.'
        if not (num >= 1):
            raise OutOfRangeError, 'number of dice out of range; must be > 0'
        if not (sides >= 2):
            raise OutOfRangeError, 'number of sides out of range; must be >= 2'
        if alpha is not None:
            if not (alpha >= 1):
                raise OutOfRangeError, 'alpha shape parameter out of range; must be > 0'
        else:
            # Use our default alpha.
            alpha = self.alpha

        results = []
        for i in range(num):
            results.append(self.randParetoRange(1, sides+1, alpha)+mod)
        if sort:
            results.sort()
        return results

class D10(Dice):
    """Example subclass of dice, implementing a bag of D10s.

    Useful for White Wolf's Storyteller system.
    """
    def roll(self, num, target=6, reroll=False):
        allrolls = []
        thisroll = super(D10, self).roll(num, 10, sort=True)
        successes = self._countSuccesses(thisroll, target)

        allrolls.extend(thisroll)

        if reroll:
            while thisroll.count(10) > 0:
                tens = thisroll.count(10)
                thisroll = super(D10, self).roll(tens, 10, sort=True)
                allrolls.extend(thisroll)
                successes += self._countSuccesses(thisroll, target)

        extra = len(allrolls) - num
        return allrolls, "%s successes (target of %s, re-rolled %s" \
               % (successes, target, extra)

    def _countSuccesses(self, thisroll, target, double_tens=True, subtract_ones=True):
        successes =  sum([int(result >= target) for result in thisroll])
        if double_tens:
            successes += thisroll.count(10)
        if subtract_ones:
            successes -= thisroll.count(1)
        return successes

def _checkVariation(func, args, low, high, num):
    """Helper function to analyze the variation of a function above and below a range.

    Given a function that returns a random number, print how many fell
    outside of the range (low, high) on num tries.

    Returns (num, lowball, highball)
    """
    lowball = 0
    highball = 0
    okay = 0
    
    for x in xrange(num):
        result = func(*args)
        if result < low:
            lowball += 1
        elif result > high:
            highball += 1
        else:
            okay += 1

    print "Out of %s, %s were low, %s were high" % (num, lowball, highball)
    return (num, lowball, highball)

roller = Dice()
