# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main as unittest_main, TestCase

# ################################################################################################################################
# ################################################################################################################################

class RateLimitTestCace(TestCase):
    pass

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    unittest_main()

# ################################################################################################################################

'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function

# stdlib
from ipaddress import ip_network

# Python 2/3 compatibility
from past.builtins import unicode

# ################################################################################################################################
# ################################################################################################################################

class Const:

    from_any = '*'

    class Unit:
        minute = 'm'
        hour   = 'h'
        day    = 'd'

    @staticmethod
    def all_units():
        return set([Const.Unit.minute, Const.Unit.hour, Const.Unit.day])

# ################################################################################################################################
# ################################################################################################################################

class DefinitionItem(object):
    __slots__ = 'config_line', 'from_', 'rate', 'unit'

    def __init__(self):
        self.config_line = None # type: int
        self.from_ = None # type: unicode
        self.rate = None  # type: int
        self.unit = None  # type: unicode

    def __repr__(self):
        return '<{} at {}; line:{}, from:{}, rate:{}, unit:{}>'.format(self.__class__.__name__, hex(id(self)), self.config_line,
            self.from_, self.rate, self.unit)

# ################################################################################################################################
# ################################################################################################################################

class DefinitionParser(object):
    """ Parser for user-provided rate limiting definitions.
    """
    def _get_lines(self, definition):
        # type: (unicode) -> list

        out = []

        for idx, line in enumerate(definition.splitlines(), 1): # type: int, unicode
            line = line.strip()

            if (not line) or line.startswith('#'):
                continue

            line = line.split('=')
            from_, rate_info = line # type: unicode, unicode

            from_ = from_.strip()

            if from_ != Const.from_any:
                from_ = ip_network(from_)

            rate_info = rate_info.strip()
            rate, unit = rate_info.split('/') # type: unicode, unicode

            rate = int(rate.strip())
            unit = unit.strip()

            if unit not in Const.all_units():
                raise ValueError('Unit `{}` is not one of `{}`'.format(unit, Unit.all))

            item = DefinitionItem()
            item.config_line = idx
            item.from_ = from_
            item.rate = rate
            item.unit = unit

            out.append(item)

        return out

    def parse(self, definition):
        # type: (unicode)

        lines = self._get_lines(definition.strip())

        print(999, lines)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    definition = """
    * = 1/m
    * = 2/h
    * = 3/d

    192.168.1.123 = 11/m
    #10.210.0.0/18 = 22/h
    127.0.0.1/32  = 33/d
    """

    dp = DefinitionParser()
    dp.parse(definition)

# ################################################################################################################################
'''
