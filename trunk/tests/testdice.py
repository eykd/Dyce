"""dicetest - unit tests for a bag of dice, various shapes and sizes

$Author$
$Rev$
$Date$
"""

__author__ = "$Author$"
__version__ = "$Rev$"
__date__ = "$Date$"

import unittest
from kit import dice
from data import tables

import common

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
            parsed = dice.parse(dstr)
            self.assertEqual(parsed, result, 
                             "%s: %s != %s" % (dstr, result, parsed))

class RollTableTest(unittest.TestCase):
    def testRollTable(self):
        rdict = {'rolls': range(3, 19),
                 'results': range(3, 19),
                 'dice': '3d6'}

        for x in xrange(100):
            r = tables.rollTable(rdict)
            self.assert_(r in rdict['results'], 
                         "%s not in %s" % (r, rdict['results']))

class SimpleDiceTestCase(unittest.TestCase):
    def setUp(self):
        self.d = dice.Dice()
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
        self.assertRaises(dice.NotIntegerError, self.d.roll, 1, 'foo')
    
    def testNegativeD(self):
        """dice should fail on D<0"""
        self.assertRaises(dice.OutOfRangeError, self.d.roll, 1, -1)
        
    def testNonIntegerX(self):
        """dice should fail on non-integer X"""
        self.assertRaises(dice.NotIntegerError, self.d.roll, 'foo')
        
    def testNegativeX(self):
        """dice should fail on X<0"""
        self.assertRaises(dice.OutOfRangeError, self.d.roll, -1)
        
    def testNonIntegerM(self):
        """dice should fail on non-integer M"""
        self.assertRaises(dice.NotIntegerError, self.d.roll, 1, 6, 'foo')

        
        
    
    

suitedicerange = unittest.makeSuite(DiceRanges)
suitedicebadinput = unittest.makeSuite(DiceBadInput)
suite = unittest.TestSuite((suitedicerange, suitedicebadinput))

if __name__ == '__main__':
    import testoob
    testoob.main()
    
