"""dicetest - unit tests for a bag of dice, various shapes and sizes

$Author$
$Rev$
$Date$
"""

__author__ = "$Author$"
__version__ = "$Rev$"
__date__ = "$Date$"

import unittest
from StringIO import StringIO

import dyce
from dyce import tables


class DiceStringParserTest(unittest.TestCase):
    def testStrings(self):
        """Can we parse dice strings?
        """
        dstrings = [("3d+6", (3, 6, 6)),
                    ("4d10-2", (4, 10, -2)),
                    ("5d12", (5, 12, 0)),
                    ("5d", (5, 6, 0)),
                    ]

        for dstr, result in dstrings:
            parsed = dyce.parse(dstr)
            self.assertEqual(parsed, result, 
                             "%s: %s != %s" % (dstr, result, parsed))

class RollTableTest(unittest.TestCase):
    def testLoadTable(self):
        """Can we load a table?
        """
        sio = StringIO(STARS_INI)
        self.stars = tables.loadTable(sio, 'stars')
        self.assert_('arity' in self.stars.keys())

    def testGetTable(self):
        """Can we retrieve a loaded table?
        """
        self.testLoadTable()
        stars = tables.getTable('stars')
        self.assertEqual(stars, self.stars)

    def testRollTable(self):
        """Can we roll against a simple table?
        """
        rdict = {'rolls': range(3, 19),
                 'results': range(3, 19),
                 'dice': '3d6'}

        for x in xrange(100):
            r = tables.rollTable(rdict)
            self.assert_(r in rdict['results'], 
                         "%s not in %s" % (r, rdict['results']))

class SimpleDiceTestCase(unittest.TestCase):
    def setUp(self):
        self.d = dyce.Dice()
        self.kinds = [2, 4, 6, 8, 10, 20, 50, 100]
        self.mods = range(-10,10)
        self.nums = range(1,5)

    def testSort(self):
        """dice should be able to sort results."""
        import copy
        results = self.d.roll(num=6, sort=True)
        results_copy = copy.copy(results)
        results_copy.sort()
        self.assertEqual(results, results_copy)
        
        
class DiceRanges(SimpleDiceTestCase):
    def testDefault(self):
        """default die should return 1 <= R <= 6"""
        results = []
        for i in range(50):
            results.append(self.d.roll()[0])
            results.append(self.d.rollsum())
        results.extend(self.d.roll(50))
        for r in results:
            assert r >= 1,  'Default 1d6 rolled less than 1 -- %s' % r
            assert r <= 6, 'Default 1d6 rolled greater than 6 -- %s' % r
            
    def testdD(self):
        """dice of dD should return 1 <= R <= D"""
        for k in self.kinds:
            results = []
            for i in range(50):
                results.append(self.d.rollsum(1,k))
            for r in results:
                assert r >= 1, "1d%s rolled less than 1" % (k)
                assert r <= k, "1d%s rolled greater than %s"  % (k)
        
    def testdDM(self):
        """dice of dD+M should return 1+M <= R <= D+M"""
        for k in self.kinds:
            for m in self.mods:
                results = []
                for i in range(50):
                    results.append(self.d.rollsum(1,k,m))
                for r in results:
                    assert r >= 1+m, "1d%s+%s rolled less than %s" % (k,m,1+m)
                    assert r <= k+m, "1d%s+%s rolled greater than %s" % (k,m,k+m)
        
    def testXdD(self):
        """dice of XdD should return X <= R <= X*D"""
        for k in self.kinds:
            for n in self.nums:
                results = []
                for i in range(50):
                    results.append(self.d.rollsum(n,k))
                for r in results:
                    assert r >= n, "%sd%s rolled less than %s" % (n,k,n)
                    assert r <= n*k, "%sd%s rolled greater than %s" % (n,k,n*k)
        
    def testXdDM(self):
        """dice of XdD+M should return X+M <= R <= X*D+M"""
        for k in self.kinds:
            for m in self.mods:
                for n in self.nums:
                    results = []
                    for i in range(50):
                        results.append(self.d.rollsum(n,k,0,m))
                    for r in results:
                        assert r >= n+m, "%sd%s+%s rolled less than %s" % (n,k,m,n+m)
                        assert r <= n*k+m, "%sd%s+%s rolled greater than %s" % (n,k,m,n*k+m)
    
class DiceBadInput(SimpleDiceTestCase):
    def testNonIntegerD(self):
        """dice should fail on non-integer D"""
        self.assertRaises(dyce.NotIntegerError, self.d.roll, 1, 'foo')
    
    def testNegativeD(self):
        """dice should fail on D<0"""
        self.assertRaises(dyce.OutOfRangeError, self.d.roll, 1, -1)
        
    def testNonIntegerX(self):
        """dice should fail on non-integer X"""
        self.assertRaises(dyce.NotIntegerError, self.d.roll, 'foo')
        
    def testNegativeX(self):
        """dice should fail on X<0"""
        self.assertRaises(dyce.OutOfRangeError, self.d.roll, -1)
        
    def testNonIntegerM(self):
        """dice should fail on non-integer M"""
        self.assertRaises(dyce.NotIntegerError, self.d.roll, 1, 6, 'foo')

        
        
    
    

suitedicerange = unittest.makeSuite(DiceRanges)
suitedicebadinput = unittest.makeSuite(DiceBadInput)
suite = unittest.TestSuite((suitedicerange, suitedicebadinput))

STARS_INI = """# -*- coding: utf-8 -*-
# stars.ini -- dice tables for stellar generation.
#
# Currently relies heavily on GURPS rules.  We need to move way from
# that.
#
#$Author$
#$Rev$
#$Date$

[class_defs]
# Class definitions for stars.
main_sequence = V,
giant = II, III, IV
super_giant = I,
subdwarf = VI,
dwarf = D,

[arity]
# Unary, binary, trinary, etc.
dice = 2d6

rolls = 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
results = 1, 1, 1, 1, 1, 1, 1, 1, 2, 2,  3

[class]
dice = 3d6

rolls = 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18
results = D, D, D, VI, V, V, V, V, V, V, V, V, V, V, V, reroll:giant

[[giant]]
dice = 3d6

rolls = 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18
results = reroll:super, II, III, III, III, III, III, III, III, III, IV, IV, IV, IV, IV, IV

[[[super]]]
dice = 1d3

rolls = 1, 2, 3
results = Ia, Ib, Ib

[main_sequence_type]
dice = 3d6

rolls = 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18
results = O, B, A, F, G, K, M, M, M, M, M, M, M, M, M, M

[giant_type]
dice = 2d6
rolls = 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
results = O, M, B, B, K, K, K, K, A, A, A

[subdwarf_type]
dice = 1d6

rolls = 1, 2, 3, 4, 5, 6
results = G, K, M, M, M, M

[dwarf_type]
dice = 1d1

rolls = 1
results = D,


[system_data]
#mass = 70 -- in sun masses
#biozone = 790, 1190 -- in AU
#inner_limit = 16 -- in AU
#radius = 0.2 -- in sun radii
#planets_on = 0, -- dice roll
#orbit_dice = 1d0 -- dice spec
#life_dice = 3d-12 -- dice -pec
#bode_range = 0.3, 0.4 -- in AU

[[O]]
[[[Ia]]]
mass = 70
biozone = 790, 1190
inner_limit = 16
radius = 0.2
planets_on = 0,
orbit_dice = 1d0
life_dice = 3d-12
bode_range = 0.3, 0.4

[[[Ib]]]
mass = 60
biozone = 630, 950
inner_limit = 13
radius = 0.1
planets_on = 0,
orbit_dice = 1d0
life_dice = 3d-12
bode_range = 0.3, 0.4

[[[V]]]
mass = 50
biozone = 500, 750
inner_limit = 10
radius = 0.0
planets_on = 0,
orbit_dice = 1d0
life_dice = 3d-9
bode_range = 0.3, 0.4

[[B]]
[[[Ia]]]
mass = 50
biozone = 500, 750
inner_limit = 10
radius = 0.2
planets_on = 0,
orbit_dice = 1d0
life_dice = 3d-10
bode_range = 0.3, 0.4

[[[Ib]]]
mass = 40
biozone = 320, 480
inner_limit = 6.3
radius = 0.1
planets_on = 0,
orbit_dice = 1d0
life_dice = 3d-10
bode_range = 0.3, 0.4

[[[II]]]
mass = 35
biozone = 250, 375
inner_limit = 5.0
radius = 0.1
planets_on = 3,
orbit_dice = 3d+1
life_dice = 3d-10
bode_range = 0.3, 0.4


[[[III]]]
mass = 30
biozone = 200, 300
inner_limit = 4.0
radius = 0.0
planets_on = 3,
orbit_dice = 3d+1
life_dice = 3d-10
bode_range = 0.3, 0.4

[[[IV]]]
mass = 20
biozone = 180, 270
inner_limit = 3.8
radius = 0.0
planets_on = 3,
orbit_dice = 3d+1
life_dice = 3d-10
bode_range = 0.3, 0.4

[[[V]]]
mass = 10
biozone = 30, 45
inner_limit = 0.6
radius = 0.0
planets_on = 1, 4
orbit_dice = 3d
life_dice = 3d-9
bode_range = 0.3, 0.4

[[A]]
[[[Ia]]]
mass = 30
biozone = 200, 300
inner_limit = 4.0
radius = 0.6
planets_on = 3,
orbit_dice = 3d+3
life_dice = 3d-10
bode_range = 0.3, 0.4

[[[Ib]]]
mass = 16
biozone = 50-75
inner_limit = 1.0
radius = 0.2
planets_on = 3,
orbit_dice = 3d+2
life_dice = 3d-10
bode_range = 0.3, 0.4

[[[II]]]
mass = 10
biozone = 20, 30
inner_limit = 0.4
radius = 0.0
planets_on = 3,
orbit_dice = 3d+2
life_dice = 3d-10
bode_range = 0.3, 0.4

[[[III]]]
mass = 6.0
biozone = 5.0, 7.5
inner_limit = 0.0
radius = 0.0
planets_on = 3,
orbit_dice = 3d+1
life_dice = 3d-10
bode_range = 0.3, 0.4

[[[IV]]]
mass = 4.0
biozone = 4.0, 6.0
inner_limit = 0.0
radius = 0.0
planets_on = 1, 4
orbit_dice = 3d
life_dice = 3d-10
bode_range = 0.3, 0.4

[[[V]]]
mass = 3.0
biozone = 3.1, 4.7
inner_limit = 0.0
radius = 0.0
planets_on = 1, 5
orbit_dice = 3d-1
life_dice = 3d-9
bode_range = 0.3, 0.4

[[F]]
[[[Ia]]]
mass = 15
biozone = 200, 300
inner_limit = 4.0
radius = 0.8
planets_on = 1, 4
orbit_dice = 3d+3
life_dice = 3d-10
bode_range = 0.3, 0.4

[[[Ib]]]
mass = 13
biozone = 50, 75
inner_limit = 1.0
radius = 0.2
planets_on = 1, 4
orbit_dice = 3d+2
life_dice = 3d-10
bode_range = 0.3, 0.4

[[[II]]]
mass = 8.0
biozone = 13, 19
inner_limit = 0.3
radius = 0.0
planets_on = 1, 4
orbit_dice = 3d+1
life_dice = 3d-9
bode_range = 0.3, 0.4

[[[III]]]
mass = 2.5
biozone = 2.5, 3.7
inner_limit = 0.1
radius = 0.0
planets_on = 1, 4
orbit_dice = 3d
life_dice = 3d-9
bode_range = 0.3, 0.4

[[[IV]]]
mass = 2.2
biozone = 2.0, 3.0
inner_limit = 0.0
radius = 0.0
planets_on = 1, 6
orbit_dice = 3d
life_dice = 3d-9
bode_range = 0.3, 0.4

[[[V]]]
mass = 1.9
biozone = 1.6, 2.4
inner_limit = 0.0
radius = 0.0
planets_on = 1, 13
orbit_dice = 3d-1
life_dice = 3d-8
bode_range = 0.3, 0.4

[[G]]
[[[Ia]]]
mass = 12
biozone = 160, 240
inner_limit = 3.1
radius = 1.4
planets_on = 1, 6
orbit_dice = 3d+3
life_dice = 3d-10
bode_range = 0.3, 0.4

[[[Ib]]]
mass = 10
biozone = 50, 75
inner_limit = 1.0
radius = 0.4
planets_on = 1, 6
orbit_dice = 3d+2
life_dice = 3d-10
bode_range = 0.3, 0.4

[[[II]]]
mass = 6.0
biozone = 13, 19
inner_limit = 0.3
radius = 0.1
planets_on = 1, 6
orbit_dice = 3d+1
life_dice = 3d-9
bode_range = 0.3, 0.4

[[[III]]]
mass = 2.7
biozone = 3.1, 4.7
inner_limit = 0.1
radius = 0.0
planets_on = 1, 6
orbit_dice = 3d
life_dice = 3d-8
bode_range = 0.3, 0.4

[[[IV]]]
mass = 1.8
biozone = 1.0, 1.5
inner_limit = 0.0
radius = 0.0
planets_on = 1, 7
orbit_dice = 3d-1
life_dice = 3d-6
bode_range = 0.3, 0.4

[[[V]]]
mass = 1.1
biozone = 0.8, 1.2
inner_limit = 0.0
radius = 0.0
planets_on = 1, 16
orbit_dice = 3d-2
life_dice = 3d0
bode_range = 0.3, 0.4

[[[VI]]]
mass = 0.8
biozone = 0.5, 0.8
inner_limit = 0.0
radius = 0.0
planets_on = 1, 16
orbit_dice = 2d+1
life_dice = 3d1
bode_range = 0.3, 0.4

[[K]]
[[[Ia]]]
mass = 15
biozone = 125, 190
inner_limit = 2.5
radius = 3.0
planets_on = 1, 10
orbit_dice = 3d+2
life_dice = 3d-10
bode_range = 0.3, 0.4

[[[Ib]]]
mass = 12
biozone = 50, 75
inner_limit = 1.0
radius = 1.0
planets_on = 1, 16
orbit_dice = 3d+2
life_dice = 3d-10
bode_range = 0.3, 0.4

[[[II]]]
mass = 6.0
biozone = 13, 19
inner_limit = 0.3
radius = 0.2
planets_on = 1, 16
orbit_dice = 3d+1
life_dice = 3d-9
bode_range = 0.3, 0.4

[[[III]]]
mass = 3.0
biozone = 4.0, 5.9
inner_limit = 0.1
radius = 0.0
planets_on = 1, 16
orbit_dice = 3d
life_dice = 3d-7
bode_range = 0.3, 0.4

[[[IV]]]
mass = 2.3
biozone = 1.0, 1.5
inner_limit = 0.0
radius = 0.0
planets_on = 1, 16
orbit_dice = 3d-1
life_dice = 3d-5
bode_range = 0.3, 0.4

[[[V]]]
mass = 0.9
biozone = 0.5, 0.6
inner_limit = 0.0
radius = 0.0
planets_on = 1, 16
orbit_dice = 3d-2
life_dice = 3d0
bode_range = 0.3, 0.4

[[[VI]]]
mass = 0.5
biozone = 0.2, 0.3
inner_limit = 0.0
radius = 0.0
planets_on = 1, 16
orbit_dice = 2d+1
life_dice = 3d1
bode_range = 0.3, 0.4

[[M]]
[[[Ia]]]
mass = 20
biozone = 100, 150
inner_limit = 2.0
radius = 7.0
planets_on = 1, 16
orbit_dice = 3d
life_dice = 3d-10
bode_range = 0.3, 0.4

[[[Ib]]]
mass = 16
biozone = 50, 76
inner_limit = 1.0
radius = 4.2
planets_on = 1, 16
orbit_dice = 3d
life_dice = 3d-10
bode_range = 0.3, 0.4

[[[II]]]
mass = 8.0
biozone = 16, 24
inner_limit = 0.3
radius = 1.1
planets_on = 1, 16
orbit_dice = 3d
life_dice = 3d-9
bode_range = 0.3, 0.4

[[[III]]]
mass = 4.0
biozone = 5.0, 7.5
inner_limit = 0.1
radius = 0.3
planets_on = 1, 16
orbit_dice = 3d
life_dice = 3d-6
bode_range = 0.3, 0.4

[[[V]]]
mass = 0.3
biozone = 0.1, 0.2
inner_limit = 0.0
radius = 0.0
planets_on = 1, 16
orbit_dice = 3d-2
life_dice = 3d1
bode_range = 0.3, 0.4

[[[VI]]]
mass = 0.2
biozone = 0.1, 0.1
inner_limit = 0.0
radius = 0.0
planets_on = 1, 16
orbit_dice = 2d+2
life_dice = 3d2
bode_range = 0.2, 0.2

[[D]]
[[[D]]]
mass = 0.8
biozone = 0.03, 0.03
inner_limit = 0.0
radius = 0.0
planets_on = 0,
orbit_dice = 1d0
life_dice = 3d-10
bode_range = 0.3, 0.4
"""

if __name__ == '__main__':
    import testoob
    testoob.main()
    
