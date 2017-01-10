# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from cStringIO import StringIO
from decimal import Decimal as stdlib_Decimal, localcontext
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

    def from_raw_string(self, value):
        return value

# ################################################################################################################################

class String(_Base):
    """ Converts from/to string without any modifications - essentially, a catch-all data type.
    """

# ################################################################################################################################

class Integer(_Base):
    def from_raw_string(self, value):
        return long(value)

Int = Integer

# ################################################################################################################################

class Decimal(_Base):
    scale = None
    err_if_scale_too_big = None
    ctx_config = None

    def __init__(self, len=None, scale=2, name=None, ctx_config=None, err_if_scale_too_big=False):
        super(Decimal, self).__init__(len, name)
        self._scale = self.scale or scale

        if self.ctx_config is not None:
            self._ctx_config = self.ctx_config
        else:
            self._ctx_config = ctx_config if ctx_config is not None else {}

        self._err_if_scale_too_big = self.err_if_scale_too_big if self.err_if_scale_too_big is not None else err_if_scale_too_big
        self.ctx_prec = self.len - 1 # Substract decimal point since self.len is counted in characters, not digits

    def from_raw_string(self, value):

        with localcontext() as ctx:
            ctx.prec = self.ctx_prec
            for key, value in self._ctx_config.iteritems():
                setattr(ctx, key, value)

            value = stdlib_Decimal(value, ctx)

            # If configured to, raise an error if the resulting scale is too big. For instance, scale was expected to be at most
            # 3 digits but the result has 4 digits.
            if self._err_if_scale_too_big:
                scale = abs(value.as_tuple().exponent)
                if scale > self._scale:
                    raise ValueError('Resulting scale is too big `{}` in input string `{}`, expected scale of `{}`'.format(
                        scale, value, self._scale))

        return value

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
        self.line_class = self.get_line_class([elem._name for elem in self.definition])

    def get_line_class(self, keys):
        """ Returns a class whose instance in runtime will represent a single line of fixed-width data.
        """
        class FWLine(object):
            __slots__ = keys

        return FWLine

    def __iter__(self):
        """ Iterates over all lines of input yielding each one with individual elements converted to business objects.
        """
        data = StringIO(self.raw_data)
        try:
            for line in data:
                line = line.rstrip('\n')
                m = self.matcher.match(line)
                if m:
                    instance = self.line_class()
                    for elem, value in izip(self.definition, m.groups()):
                        setattr(instance, elem._name, elem.from_raw_string(value))
                    yield instance
                else:
                    yield None
        finally:
            data.close()

# ################################################################################################################################