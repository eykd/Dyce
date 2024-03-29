# -*- coding: utf-8 -*-
"""dcalc - a calculator parser, with dice syntax.

This calculator supports the usual (numbers, add, subtract,
multiply, divide), global variables (stored in a global variable in
Python), and local variables (stored in an attribute passed around
in the grammar).

The calculator also supports a number of pseudorandom number
expressions:

C{n d s} -> a dice expression, where n is the number of dice, and s is
the number of sides per die (i.e. 2d6 for two six-sided dice. The
result is the sum of the roll.

C{[min - max]} -> return an int between min and max, inclusive, on the
uniform distribution.

C{{min - max}} -> return a float between min and max, inclusive, on the
uniform distribution.

C{bell[min - max]} -> return an int between min and max, inclusive, on
the gaussian, or bell curve distribution.

C{bell{min - max}} -> return a float between min and max, inclusive, on
the gaussian, or bell curve distribution.

C{fuzz(expr, distance)} -> return a 'fuzzed' number within distance of
the expression result.  If distance < 1.0, it is treated as a ratio of
the expression instead.

One can parse a dice expression using C{calculate}:

    >>> calculate('1d6')
    3
    >>> calculate('fuzz(1d6, 1.0)')
    3.523413
    >>> calculate('1d6 + 3d10')
    23

One can use a Dstr object to store a dice expression for convenience:

    >>> d = Dstr('1d6')
    >>> d()
    5
    >>> d.calculate()
    2

This parser is derived from the calc.g example in Yapps 2 and can be
distributed under the terms of the MIT open source license, either
found in the LICENSE file included with the U{Yapps
distribution<http://theory.stanford.edu/~amitp/yapps/>} or at
U{http://www.opensource.org/licenses/mit-license.php}

$Author$\n
$Rev$\n
$Date$
"""

__author__ = "$Author$"[9:-2]
__version__ = "$Rev$"[6:-2]
__date__ = "$Date$"[7:-2]


from string import strip, atoi, atof
import dice
import logging
logger = logging.getLogger('dcalc')

__all__ = ['Dstr', 'calculate']

dparse = dice.parse
dsum = dice.roller.rollsum
dfuzz = dice.roller.fuzz
drand = dice.roller.rand
drandint = drand.randint
dbelli = dice.roller.rollbellInt
dbellf = dice.roller.rollbellFloat
duni = drand.uniform

globalvars = {}       # We will store the calculator variables here


def lookup(map, name):
    for x, v in map:  
        if x == name: return v
    if not name in globalvars:
        logger.info('Undefined (defaulting to 0): %s', name)
    return globalvars.get(name, 0)

%%
parser DiceCalculator:
    ignore:    "[ \r\t\n]+"
    token END: "$"
    token DIE: "[0-9]+d[0-9]+"
    token FLT: "-?[0-9]+[.][0-9]+"
    token INT: "-?[0-9]+"
    token VAR: "[a-zA-Z_]+"

    # Each line can either be an expression or an assignment statement
    rule goal:   expr<<[]>> END            {{ return expr }}
               | "set" VAR expr<<[]>> END  {{ globalvars[VAR] = expr }}
                                           {{ return expr }}

               | "u\\(" expr<<[]>> "," VAR "\\)" END  {{ return (expr, str(VAR)) }}

    # An expression is the sum and difference of factors
    rule expr<<V>>:   factor<<V>>         {{ n = factor }}
                     (  "[+]" factor<<V>> {{ n = n+factor }}
                     |  "-"  factor<<V>>  {{ n = n-factor }}
                     )*                   {{ return n }}

    # A factor is the product and division of terms
    rule factor<<V>>: term<<V>>           {{ v = term }}
                     ( "[*]" term<<V>>    {{ v = v*term }}
                     |  "/"  term<<V>>    {{ v = v/term }}
                     )*                   {{ return v }}

    # A term is a number, variable, or an expression surrounded by parentheses
    rule term<<V>>:   
                 DIE                      {{ return dsum(*dparse(DIE))}}
               | "\\[" INT {{ a = atoi(INT) }} " " INT "\\]" {{ return drandint(a, atoi(INT)) }}
               | "\\{" number {{ a = number }} " " number "\\}" {{ return duni(a, number) }}
               | "bell\\[" INT {{a = atoi(INT) }} " " INT "\\]" {{ return dbelli(a, atoi(INT)) }}
               | "bell\\{" FLT {{a = atof(FLT) }} " " FLT "\\}" {{ return dbellf(a, atof(FLT)) }}
               | "fuzz\\(" expr<<V>> "," number "\\)" {{ return dfuzz(float(expr), float(number)) }}
               | number                      {{ return number }}
               | VAR                      {{ return lookup(V, VAR) }}
               | "\\(" expr<<V>> "\\)"         {{ return expr }}
               | "let" VAR "=" expr<<V>>  {{ V = [(VAR, expr)] + V }}
                 "in" expr<<V>>           {{ return expr }}

    rule number:
                 FLT                       {{ return atof(FLT) }}
               | INT                       {{ return atoi(INT) }}

%%

def calculate(dice_str):
    """Parse the given dice expression, and return an immediate result.
    """
    return parse('goal', dice_str)


class Dstr(object):
    """A class wrapper around a dice expression. 

    Provides dice calculations on demand.
    """
    __slots__ = ('_dstr', '__weakref__')

    def __init__(self, dcalc_str=''):
        self._dstr = dcalc_str

    def __cmp__(self, other):
        return cmp(str(self), str(other))

    def __str__(self):
        return self._dstr

    def __repr__(self):
        return "<dstr %s>" % (str(self),)

    def __call__(self):
        return calculate(self._dstr)

    def __getstate__(self):
        return self._dstr

    def __setstate__(self, dstr):
        self._dstr = dstr

    def calculate(self):
        return self()


if __name__=='__main__':
    print 'Welcome to the dice calculator for dyce!'
    print '  Enter either "<expression>" or "set <var> <expression>",'
    print '  or just press return to exit.  An expression can have'
    print '  local variables:  let x = expr in expr'
    # We could have put this loop into the parser, by making the
    # `goal' rule use (expr | set var expr)*, but by putting the
    # loop into Python code, we can make it interactive (i.e., enter
    # one expression, get the result, enter another expression, etc.)
    DEBUG_LEVEL = 10
    while 1:
        try: s = raw_input('>>> ')
        except EOFError: break
        if not strip(s): break
        parse('goal', s)
    print 'Bye.'
