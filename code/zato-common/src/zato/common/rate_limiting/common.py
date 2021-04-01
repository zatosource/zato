# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################
# ################################################################################################################################

class BaseException(Exception):
    pass

class AddressNotAllowed(BaseException):
    pass

class RateLimitReached(BaseException):
    pass

# ################################################################################################################################
# ################################################################################################################################

class Const:

    from_any = '*'
    rate_any = '*'

    class Unit:
        minute = 'm'
        hour   = 'h'
        day    = 'd'

    @staticmethod
    def all_units():
        return set([Const.Unit.minute, Const.Unit.hour, Const.Unit.day])

# ################################################################################################################################
# ################################################################################################################################

class ObjectInfo(object):
    """ Information about an individual object covered by rate limiting.
    """
    __slots__ = 'type_', 'id', 'name'

    def __init__(self):
        self.type_ = None # type: str
        self.id    = None # type: int
        self.name  = None # type: str

# ################################################################################################################################
# ################################################################################################################################

class DefinitionItem(object):
    __slots__ = 'config_line', 'from_', 'rate', 'unit', 'object_id', 'object_type', 'object_name'

    def __init__(self):
        self.config_line = None # type: int
        self.from_ = None # type: object
        self.rate = None  # type: int
        self.unit = None  # type: str
        self.object_id = None   # type: int
        self.object_type = None # type: str
        self.object_name = None # type: str

    def __repr__(self):
        return '<{} at {}; line:{}, from:{}, rate:{}, unit:{} ({} {} {})>'.format(
            self.__class__.__name__, hex(id(self)), self.config_line, self.from_, self.rate, self.unit,
            self.object_id, self.object_name, self.object_type)

# ################################################################################################################################
# ################################################################################################################################
