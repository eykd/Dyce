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
    for x,v in map:  
        if x == name: return v
    if not globalvars.has_key(name): 
        logger.info('Undefined (defaulting to 0): %s', name)
    return globalvars.get(name, 0)


# Begin -- grammar generated by Yapps
import sys, re
import yapps.yappsrt as yappsrt

class DiceCalculatorScanner(yappsrt.Scanner):
    patterns = [
        ('"in"', re.compile('in')),
        ('"="', re.compile('=')),
        ('"let"', re.compile('let')),
        ('"\\\\("', re.compile('\\(')),
        ('"fuzz\\\\("', re.compile('fuzz\\(')),
        ('"bell\\\\{"', re.compile('bell\\{')),
        ('"bell\\\\["', re.compile('bell\\[')),
        ('"\\\\}"', re.compile('\\}')),
        ('"\\\\{"', re.compile('\\{')),
        ('"\\\\]"', re.compile('\\]')),
        ('" "', re.compile(' ')),
        ('"\\\\["', re.compile('\\[')),
        ('"/"', re.compile('/')),
        ('"[*]"', re.compile('[*]')),
        ('"-"', re.compile('-')),
        ('"[+]"', re.compile('[+]')),
        ('"\\\\)"', re.compile('\\)')),
        ('","', re.compile(',')),
        ('"u\\\\("', re.compile('u\\(')),
        ('"set"', re.compile('set')),
        ('[ \r\t\n]+', re.compile('[ \r\t\n]+')),
        ('END', re.compile('$')),
        ('DIE', re.compile('[0-9]+d[0-9]+')),
        ('FLT', re.compile('-?[0-9]+[.][0-9]+')),
        ('INT', re.compile('-?[0-9]+')),
        ('VAR', re.compile('[a-zA-Z_]+')),
    ]
    def __init__(self, str):
        yappsrt.Scanner.__init__(self,None,['[ \r\t\n]+'],str)

class DiceCalculator(yappsrt.Parser):
    Context = yappsrt.Context
    def goal(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'goal', [])
        _token = self._peek('"set"', '"u\\\\("', 'DIE', '"\\\\["', '"\\\\{"', '"bell\\\\["', '"bell\\\\{"', '"fuzz\\\\("', 'VAR', '"\\\\("', '"let"', 'FLT', 'INT')
        if _token not in ['"set"', '"u\\\\("']:
            expr = self.expr([], _context)
            END = self._scan('END')
            logger.debug(' =%s', expr)
            return expr
        elif _token == '"set"':
            self._scan('"set"')
            VAR = self._scan('VAR')
            expr = self.expr([], _context)
            END = self._scan('END')
            globalvars[VAR] = expr
            logger.debug(' %s=%s', VAR, expr)
            return expr
        else: # == '"u\\\\("'
            self._scan('"u\\\\("')
            expr = self.expr([], _context)
            self._scan('","')
            VAR = self._scan('VAR')
            self._scan('"\\\\)"')
            END = self._scan('END')
            logger.debug(' =(%s, "%s")', expr, VAR)
            return (expr, str(VAR))

    def expr(self, V, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'expr', [V])
        factor = self.factor(V, _context)
        n = factor
        while self._peek('"[+]"', '"-"', 'END', '","', '"\\\\)"', '"in"', '"[*]"', '"/"') in ['"[+]"', '"-"']:
            _token = self._peek('"[+]"', '"-"')
            if _token == '"[+]"':
                self._scan('"[+]"')
                factor = self.factor(V, _context)
                n = n+factor
            else: # == '"-"'
                self._scan('"-"')
                factor = self.factor(V, _context)
                n = n-factor
        if self._peek() not in ['"[+]"', '"-"', 'END', '","', '"\\\\)"', '"in"', '"[*]"', '"/"']:
            raise yappsrt.SyntaxError(charpos=self._scanner.get_prev_char_pos(), context=_context, msg='Need one of ' + ', '.join(['"[+]"', '"-"', 'END', '","', '"\\\\)"', '"in"', '"[*]"', '"/"']))
        return n

    def factor(self, V, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'factor', [V])
        term = self.term(V, _context)
        v = term
        while self._peek('"[*]"', '"/"', '"[+]"', '"-"', 'END', '","', '"\\\\)"', '"in"') in ['"[*]"', '"/"']:
            _token = self._peek('"[*]"', '"/"')
            if _token == '"[*]"':
                self._scan('"[*]"')
                term = self.term(V, _context)
                v = v*term
            else: # == '"/"'
                self._scan('"/"')
                term = self.term(V, _context)
                v = v/term
        if self._peek() not in ['"[*]"', '"/"', '"[+]"', '"-"', 'END', '","', '"\\\\)"', '"in"']:
            raise yappsrt.SyntaxError(charpos=self._scanner.get_prev_char_pos(), context=_context, msg='Need one of ' + ', '.join(['"[*]"', '"/"', '"[+]"', '"-"', 'END', '","', '"\\\\)"', '"in"']))
        return v

    def term(self, V, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'term', [V])
        _token = self._peek('DIE', '"\\\\["', '"\\\\{"', '"bell\\\\["', '"bell\\\\{"', '"fuzz\\\\("', 'VAR', '"\\\\("', '"let"', 'FLT', 'INT')
        if _token == 'DIE':
            DIE = self._scan('DIE')
            return dsum(*dparse(DIE))
        elif _token == '"\\\\["':
            self._scan('"\\\\["')
            INT = self._scan('INT')
            a = atoi(INT)
            self._scan('" "')
            INT = self._scan('INT')
            self._scan('"\\\\]"')
            return drandint(a, atoi(INT))
        elif _token == '"\\\\{"':
            self._scan('"\\\\{"')
            number = self.number(_context)
            a = number
            self._scan('" "')
            number = self.number(_context)
            self._scan('"\\\\}"')
            return duni(a, number)
        elif _token == '"bell\\\\["':
            self._scan('"bell\\\\["')
            INT = self._scan('INT')
            a = atoi(INT)
            self._scan('" "')
            INT = self._scan('INT')
            self._scan('"\\\\]"')
            return dbelli(a, atoi(INT))
        elif _token == '"bell\\\\{"':
            self._scan('"bell\\\\{"')
            FLT = self._scan('FLT')
            a = atof(FLT)
            self._scan('" "')
            FLT = self._scan('FLT')
            self._scan('"\\\\}"')
            return dbellf(a, atof(FLT))
        elif _token == '"fuzz\\\\("':
            self._scan('"fuzz\\\\("')
            expr = self.expr(V, _context)
            self._scan('","')
            number = self.number(_context)
            self._scan('"\\\\)"')
            return dfuzz(float(expr), float(number))
        elif _token not in ['VAR', '"\\\\("', '"let"']:
            number = self.number(_context)
            return number
        elif _token == 'VAR':
            VAR = self._scan('VAR')
            return lookup(V, VAR)
        elif _token == '"\\\\("':
            self._scan('"\\\\("')
            expr = self.expr(V, _context)
            self._scan('"\\\\)"')
            return expr
        else: # == '"let"'
            self._scan('"let"')
            VAR = self._scan('VAR')
            self._scan('"="')
            expr = self.expr(V, _context)
            V = [(VAR, expr)] + V
            self._scan('"in"')
            expr = self.expr(V, _context)
            return expr

    def number(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'number', [])
        _token = self._peek('FLT', 'INT')
        if _token == 'FLT':
            FLT = self._scan('FLT')
            return atof(FLT)
        else: # == 'INT'
            INT = self._scan('INT')
            return atoi(INT)


def parse(rule, text):
    P = DiceCalculator(DiceCalculatorScanner(text))
    return yappsrt.wrap_error_reporter(P, rule)

# End -- grammar generated by Yapps



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

