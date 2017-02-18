# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from cStringIO import StringIO
from datetime import date, datetime, time
from decimal import Context, Decimal as stdlib_Decimal
from itertools import izip

# dateparser
from dateparser import parse as dateparser_parse

# regex
from regex import compile as re_compile

# Zato
from zato.common import PADDING

# ################################################################################################################################

class _Base(object):
    len = None
    name = None
    padding = PADDING.RIGHT
    fill_char = ' '

    def __init__(self, len=None, name=None, padding=None, fill_char=None):
        self._len = self.len or len
        self._name = self.name or name
        self._padding = padding or self.padding
        _fill_char = fill_char or self.fill_char
        self._fill_char = _fill_char if isinstance(_fill_char, str) else str(_fill_char)
        self.pattern = '(?P<{}>.{{{}}})'.format(self._name, self._len)

    def from_string(self, value):
        return value.strip(self.fill_char)

    def to_string(self, value):
        return value

# ################################################################################################################################

class String(_Base):
    """ Converts from/to string without any modifications - essentially, a catch-all data type.
    """

# ################################################################################################################################

class Integer(_Base):

    def from_string(self, value):
        return long(value)

    def to_string(self, value):
        return str(value)

Int = Integer

# ################################################################################################################################

class Decimal(_Base):
    scale = None
    err_if_scale_too_big = None
    ctx_config = None
    has_dec_sep = None

    def __init__(self, len=None, scale=2, name=None, ctx_config=None, err_if_scale_too_big=False, padding=None, fill_char=None,
                 has_dec_sep=True, _decimal_ten=stdlib_Decimal(10)):
        super(Decimal, self).__init__(len, name, padding, fill_char)
        self._scale = self.scale or scale
        self._err_if_scale_too_big = self.err_if_scale_too_big if self.err_if_scale_too_big is not None else err_if_scale_too_big
        self._has_dec_sep = self.has_dec_sep if self.has_dec_sep is not None else has_dec_sep

        # Make sure this kind of input will actually work.
        # For instance, if scale is given at all and total length is 1 but scale is 2, we cannot possibly parse it, total length
        # should be at least scale+1 (to accommodate decimal separator), or equal to scale (if no decimal separator is used).
        if self._scale:
            if self._has_dec_sep:
                if self._len - self._scale < 1:
                    raise ValueError('Total length must be at least {} if scale is {} and a decimal separator is expected'.format(
                        self._scale+1, self._scale))
            else:
                if self._len - self._scale < 0:
                    raise ValueError(
                        'Total length must be at least {} if scale is {} and no decimal separator is expected'.format(
                            self._scale, self._scale))

        self.ctx = self._get_context(ctx_config)

        # To how many decimal digits possibly round down to
        self._quantize_to = _decimal_ten ** -self._scale

    def _get_context(self, ctx_config):
        """ Returns a decimal.Context object under which all operations on decimal.Decimal objects will be performed.
        This is used instead of getcontext or localcontext so as to have a new Context object each time it's needed instead
        of changing thread-local values.
        """
        if self.ctx_config is not None:
            _ctx_config = self.ctx_config
        else:
            _ctx_config = ctx_config if ctx_config is not None else {}

        if 'prec' not in _ctx_config:
            _ctx_config['prec'] = self._len - 1 # Substract decimal point since self.len is counted in characters, not digits

        return Context(**_ctx_config)

    def from_string(self, value, _decimal=stdlib_Decimal):

        # Strip of filler characters before any parsing takes place
        value = value.lstrip(self.fill_char)

        # If the value lacks a decimal separator, it needs to be added manually before it is converted to string.
        if not self._has_dec_sep:
            value = '{}.{}'.format(value[:len(value)-self._scale], value[:self._scale])

        value = _decimal(value, self.ctx)
        scale = abs(value.as_tuple().exponent)

        if scale > self._scale:

            # If configured to, raise an error if the resulting scale is too big. For instance, scale was expected to be at most
            # 3 digits but the result has 4 digits.
            if self._err_if_scale_too_big:
                raise ValueError('Resulting scale is too big `{}` in input string `{}`, expected scale of `{}`'.format(
                    scale, value, self._scale))

            # Otherwise, we need to round down to the `scale` decimal places.
            else:
                value = value.quantize(self._quantize_to, context=self.ctx)

        return value

    def to_string(self, value, _decimal=stdlib_Decimal, _base_types=(basestring, int, long, float)):

        if isinstance(value, _base_types):
            value = str(_decimal(value).quantize(self._quantize_to, context=self.ctx))

        elif isinstance(value, _decimal):
            value = str(value.quantize(self._quantize_to, context=self.ctx))

        return value

# ################################################################################################################################

class _BaseTime(_Base):
    parse_kwargs = None
    output_format = None
    _stdlib_class = None

    def __init__(self, len=None, name=None, output_format=None, parse_kwargs=None, padding=None, fill_char=None):
        self._parse_kwargs = self.parse_kwargs if self.parse_kwargs else parse_kwargs or {}
        self._output_format = self.output_format or output_format
        super(_BaseTime, self).__init__(len, name, padding, fill_char)

    def from_string(self, value):
        return dateparser_parse(value.strip(self.fill_char), **self._parse_kwargs)

    def to_string(self, value):

        if isinstance(value, basestring):
            return dateparser_parse(value).strftime(self._output_format) if self._output_format else value

        elif isinstance(value, self._stdlib_class):
            return value.strftime(self._output_format) if self._output_format else value.isoformat()

        else:
            raise ValueError('Value `{}` is neither string nor {}'.format(value, self._stdlib_class))

class Timestamp(_BaseTime):
    _stdlib_class = datetime

# ################################################################################################################################

class Date(_BaseTime):
    _stdlib_class = date

    def from_string(self, value):
        return super(Date, self).from_string(value).date()

# ################################################################################################################################

class Time(_BaseTime):
    _stdlib_class = time

    def from_string(self, value):
        return super(Time, self).from_string(value).time()

# ################################################################################################################################

class FixedWidth(object):
    """ Parses fixed-width data, whole files and individual lines alike, and returns iterators or lists to read contents from.
    """
    def __init__(self, definition=None, raw_data=None):
        self.definition = definition
        self.raw_data = raw_data

        if self.definition:
            self.set_up()

# ################################################################################################################################

    def set_up(self):
        self.matcher = re_compile(''.join(elem.pattern for elem in self.definition))
        self.line_class = self.get_line_class([elem._name for elem in self.definition])

# ################################################################################################################################

    def get_line_class(self, keys):
        """ Returns a class whose instance in runtime will represent a single line of fixed-width data.
        """
        class FWLine(object):
            __slots__ = keys

        return FWLine

# ################################################################################################################################

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
                        setattr(instance, elem._name, elem.from_string(value))
                    yield instance
                else:
                    yield None
        finally:
            data.close()

# ################################################################################################################################

    def to_dict(self):
        """ Returns input data serialized to a dictionary.
        """

# ################################################################################################################################

    def _serialize_line(self, line, _right=PADDING.RIGHT, _list_like=(list, tuple)):
        """ Serializes to string a single line out of fixed-width data.
        """
        out = StringIO()
        try:
            is_list = isinstance(line, _list_like)
            for idx, item in enumerate(self.definition):

                value = item.to_string(line[idx] if is_list else getattr(line, item._name))
                value_len = len(value)

                if value_len < item._len:
                    if item.padding == _right:
                        value = value.ljust(item._len, item._fill_char)
                    else:
                        value = value.rjust(item._len, item._fill_char)

                out.write(value)

            return out.getvalue()

        finally:
            out.close()

# ################################################################################################################################

    def serialize(self, response):
        """ Serializes to string one or more lines of fixed-width data.
        """
        if isinstance(response, list):
            out = [self._serialize_line(line) for line in response]
        else:
            out = [self._serialize_line(response)]

        return '\n'.join(out)

# ################################################################################################################################
