# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from cStringIO import StringIO
from itertools import izip

# regex
from regex import compile as re_compile

# ################################################################################################################################

class _Base(object):
    len = None
    name = None

    def __init__(self, len=None, name=None):
        self.len = self.len or len
        self._name = self.name or name
        self.pattern = '(?P<{}>.{{{}}})'.format(self._name, self.len)

# ################################################################################################################################

class String(_Base):
    """ Converts from/to string without any modifications - essentially, a catch-all data type.
    """

# ################################################################################################################################

class Integer(_Base):
    pass

# ################################################################################################################################

class Decimal(_Base):
    pass

# ################################################################################################################################

class Timestamp(_Base):
    pass

# ################################################################################################################################

class Date(_Base):
    pass

# ################################################################################################################################

class Time(_Base):
    pass

# ################################################################################################################################

class FixedWidth(object):
    """ Parses fixed-width data, whole files and individual lines alike, and returns iterators or lists to read contents from.
    """
    def __init__(self, raw_data, definition):
        self.raw_data = raw_data
        self.definition = definition
        self.matcher = re_compile(''.join(elem.pattern for elem in self.definition))
        self.keys = [elem._name for elem in self.definition]
        self.line_class = self.get_line_class(self.keys)

    def get_line_class(self, keys):
        """ Returns a class whose instance in runtime will represent a single line of fixed-width data.
        """
        class FWLine(object):
            __slots__ = keys

        return FWLine

    def __iter__(self):
        data = StringIO(self.raw_data)

        for line in data:
            line = line.rstrip('\n')
            m = self.matcher.match(line)
            if m:
                instance = self.line_class()
                for key, value in izip(self.keys, m.groups()):
                    setattr(instance, key, value)
                yield instance
            else:
                yield None

# ################################################################################################################################