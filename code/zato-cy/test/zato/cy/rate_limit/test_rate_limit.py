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
import logging
from ipaddress import ip_network
from logging import getLogger

# gevent
from gevent.lock import RLock

# Python 2/3 compatibility
from past.builtins import unicode

# ################################################################################################################################

log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
logger = getLogger(__name__)

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

class ObjectInfo(object):
    """ Information about an individual object covered by rate limiting.
    """
    __slots__ = 'type_', 'name'

    def __init__(self):
        self.type_ = None # type: unicode
        self.name = None  # type: unicode

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

class ObjectConfig(object):
    """ A container for configuration pertaining to a particular object and its definition.
    """
    __slots__ = 'object_info', 'definition', 'has_from_any', 'from_any_rate', 'from_any_unit', 'lock', 'current_idx', \
        'is_limit_reached'

    def __init__(self):
        self.current_idx = 0
        self.object_info = None   # type: ObjectInfo
        self.definition = None    # type: list
        self.has_from_any = None  # type: bool
        self.from_any_rate = None # type: int
        self.from_any_unit = None # type: unicode
        self.is_limit_reached = False # type: bool
        self.lock = RLock()

# ################################################################################################################################

    def get_config_key(self):
        # type: () -> unicode
        return '{}:{}'.format(self.object_info.type_, self.object_info.name)

# ################################################################################################################################

    def check_limit(self, from_):
        with self.lock:
            pass

# ################################################################################################################################
# ################################################################################################################################

class DefinitionParser(object):
    """ Parser for user-provided rate limiting definitions.
    """
    def _get_lines(self, definition):
        # type: (unicode) -> list

        out = []
        definition = definition if isinstance(definition, unicode) else definition.decode('utf8')

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
        # type: (unicode) -> list
        return self._get_lines(definition.strip())

# ################################################################################################################################
# ################################################################################################################################

class RateLimiting(object):
    """ Main API for the management of rate limiting functionality.
    """
    __slots__ = 'parser', 'config_store', 'lock'

    def __init__(self):
        self.parser = DefinitionParser()
        self.config_store = {}
        self.lock = RLock()

# ################################################################################################################################

    def create(self, object_dict, definition):
        # type: (dict, unicode)

        info = ObjectInfo()
        info.type_ = object_dict['type_']
        info.name = object_dict['name']

        parsed = self.parser.parse(definition)
        def_first = parsed[0]
        has_from_any = def_first.from_ == Const.from_any

        config = ObjectConfig()
        config.object_info = info
        config.definition = parsed

        if has_from_any:
            config.has_from_any = has_from_any
            config.from_any_rate = def_first.rate
            config.from_any_unit = def_first.unit

        self.config_store[config.get_config_key()] = config

# ################################################################################################################################

    def check_limit(self, object_type, object_name, from_):
        """ Checks if input object has already reached its allotted usage limit.
        """
        # type: (unicode, unicode, unicode)

        with self.lock:
            key = self._get_config_key(object_type, object_name)
            config = self.config_store.get(key) # type: ObjectConfig

        # It is possible that we do not have configuration for such an object,
        # in which case we will log a warning.
        if config:
            with config.lock:
                config.check_limit(from_)
        else:
            logger.warn('No such rate limiting object `%s` (%s)', object_name, object_type)

# ################################################################################################################################

    def _get_config_key(self, object_type, object_name):
        # type: (unicode, unicode) -> unicode

        return '{}:{}'.format(object_type, object_name)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    object_type = 'http_soap'
    object_name = 'My Channel'

    object_dict = {
        'id':    123,
        'type_': object_type,
        'name':  object_name
    }

    definition = """
    * = 1/m
    * = 2/h
    * = 3/d

    192.168.1.123 = 11/m
    #10.210.0.0/18 = 22/h
    127.0.0.1/32  = 33/d
    """

    rate_limiting = RateLimiting()
    rate_limiting.create(object_dict, definition)

    rate_limiting.check_limit(object_type, object_name, '127.0.0.1')

# ################################################################################################################################
'''
