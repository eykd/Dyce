# -*- coding: utf-8 -*-
"""tables -- support for loading and rolling dice tables.

Dice tables are written in INI format. See tests/stars.ini for an example.

$Author$\n
$Rev$\n
$Date$
"""

__author__ = "$Author$"[9:-2]
__version__ = "$Rev$"[6:-2]
__date__ = "$Date$"[7:-2]

import os
import configobj
import dice
import dcalc

import logging
logger = logging.getLogger('tables')

_loaded = {}

def getTable(name):
    """Get a results table by name.
    """
    if name in _loaded:
        return _loaded[name]
    else:
        raise NameError, "No table named '%s' loaded" % (name)

def loadTable(fo, name):
    """Load the given file object and name it.

    fo can be an open file object or a pathname; anything acceptable
    to ConfigObj.
    """
    co = configobj.ConfigObj(fo)
    _loaded[name] = co
    return co

def rollTable(tbl, mod=0):
    """Roll against a dice/result table.
    """
    logger.info("Dice spec: %s", tbl['dice'],)
    try:
        rolls = [int(n) for n in tbl['rolls']]
        logger.info("Rolls: %s", rolls,)
        results = tbl['results']
        logger.info("Results: %s", results,)
    except KeyError:
        rolls = []
    
    r = dcalc.calculate(tbl['dice'])
    logger.info("Roll: %s", r,)
    result = r
    if r in rolls:
        i = rolls.index(r)
        try:
            result = results[i]
        except IndexError, e:
            raise IndexError, \
                """Roll: %s
Index: %s in rolls:
%s (length %s)
no corresponding index for roll in
%s (length %s)""" % (r, i, rolls, len(rolls), results, len(results))
    else:
        result = r
        
    if str(result).startswith('reroll'):
        if ':' in result:
            new_tbl = tbl[result.split(':', 1)[1]]
            result = rollTable(new_tbl)
        else:
            result = rollTable(tbl)
    elif result == 'None':
        result = None

    return result
