# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from datetime import datetime
from logging import getLogger

# datetutil
from dateutil.relativedelta import relativedelta

# gevent
from gevent.lock import RLock

# netaddr
from netaddr import IPAddress, IPNetwork

# Python 2/3 compatibility
from past.builtins import unicode

# ################################################################################################################################

# Type checking
import typing

if typing.TYPE_CHECKING:
    pass

# ################################################################################################################################

log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class BaseException(Exception):
    pass

class FromIPNotAllowed(BaseException):
    pass

class RateLimitReached(BaseException):
    pass

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
        self.from_ = None # type: object
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
    __slots__ = 'current_idx', 'lock', 'object_info', 'definition', 'has_from_any', 'from_any_rate', 'from_any_unit', \
        'is_limit_reached', 'ip_address_cache', 'current_period_func', 'by_period'

    def __init__(self):
        self.current_idx = 0
        self.lock = RLock()
        self.object_info = None   # type: ObjectInfo
        self.definition = None    # type: list
        self.has_from_any = None  # type: bool
        self.from_any_rate = None # type: int
        self.from_any_unit = None # type: unicode
        self.ip_address_cache = {} # type: dict
        self.by_period = {}        # type: dict

        self.current_period_func = {
            Const.Unit.day: self._get_current_day,
            Const.Unit.hour: self._get_current_hour,
            Const.Unit.minute: self._get_current_minute,
        }

# ################################################################################################################################

    def get_config_key(self):
        # type: () -> unicode
        return '{}:{}'.format(self.object_info.type_, self.object_info.name)

# ################################################################################################################################

    def _get_rate_config_by_from(self, orig_from, _from_any=Const.from_any):
        # type: (unicode, unicode) -> DefinitionItem

        # First, periodically clear out the IP cache to limit its size to 1,000 items
        if len(self.ip_address_cache) >= 1000:
            self.ip_address_cache.clear()

        from_ = self.ip_address_cache.setdefault(orig_from, IPAddress(orig_from)) # type: IPAddress
        found = None

        for line in self.definition: # type: DefinitionItem

            # A catch-all * pattern
            if line.from_ == _from_any:
                found = line
                break

            # A network match
            elif from_ in line.from_:
                found = line
                break

        # We did not match any line from configuration
        if not found:
            raise FromIPNotAllowed('From IP address not allowed `{}`'.format(orig_from))

        # We found a matching piece of from IP configuration
        return found

# ################################################################################################################################

    def _get_current_day(self, now, _prefix=Const.Unit.day, _format='%Y-%m-%d'):
        # type: (datetime, unicode, unicode) -> unicode
        return '{}.{}'.format(_prefix, now.strftime(_format))

    def _get_current_hour(self, now, _prefix=Const.Unit.hour, _format='%Y-%m-%dT%H'):
        # type: (datetime, unicode, unicode) -> unicode
        return '{}.{}'.format(_prefix, now.strftime(_format))

    def _get_current_minute(self, now, _prefix=Const.Unit.minute, _format='%Y-%m-%dT%H:%M'):
        # type: (datetime, unicode, unicode) -> unicode
        return '{}.{}'.format(_prefix, now.strftime(_format))

# ################################################################################################################################

    def _format_last_info(self, network_dict):
        # type: (dict) -> unicode

        return 'last_from:`{last_from}; last_request_time_utc:`{last_request_time_utc}; last_cid:`{last_cid}`;'.format(
            **network_dict)

# ################################################################################################################################

    def _check_limit(self, cid, orig_from, network_found, rate, unit, _utcnow=datetime.utcnow):
        # type: (unicode, unicode, int, unicode)

        # Local aliases
        now = _utcnow()

        # Get current period, e.g. current day, hour or minute
        current_period_func = self.current_period_func[unit]
        period = current_period_func(now)

        # Get or create a dictionary of requests information for current period
        period_dict = self.by_period.setdefault(period, {}) # type: dict

        # Get information about already stored requests for that network in current period
        network_dict = period_dict.setdefault(network_found, {
            'requests': 0,
            'last_cid': None,
            'last_request_time_utc': None,
            'last_from': None,
            'last_network': None,
        }) # type: dict

        # We have reached the limit already ..
        if network_dict['requests'] >= rate:
            raise RateLimitReached('Max. rate limit of {}/{} reached; from:`{}`, network:`{}`; {} ({})'.format(
                rate, unit, orig_from, network_found, self._format_last_info(network_dict), cid))

        # .. otherwise, we increase the counter and store metadata.
        else:
            network_dict['requests'] += 1
            network_dict['last_cid'] = cid
            network_dict['last_request_time_utc'] = now.isoformat()
            network_dict['last_from'] = orig_from
            network_dict['last_network'] = str(network_found)

# ################################################################################################################################

    def check_limit(self, cid, orig_from):
        # type: (unicode, unicode)

        with self.lock:

            if self.has_from_any:
                rate = self.from_any_rate
                unit = self.from_any_unit
                network_found = Const.from_any
            else:
                found = self._get_rate_config_by_from(orig_from)
                rate = found.rate
                unit = found.unit
                network_found = found.from_

            # Now, check actual rate limits
            self._check_limit(cid, orig_from, network_found, rate, unit)

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
                from_ = IPNetwork(from_)

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

    def check_limit(self, cid, object_type, object_name, from_):
        """ Checks if input object has already reached its allotted usage limit.
        """
        # type: (unicode, unicode, unicode, unicode)

        with self.lock:
            key = self._get_config_key(object_type, object_name)
            config = self.config_store.get(key) # type: ObjectConfig

        # It is possible that we do not have configuration for such an object,
        # in which case we will log a warning.
        if config:
            with config.lock:
                config.check_limit(cid, from_)
        else:
            logger.warn('No such rate limiting object `%s` (%s)', object_name, object_type)

# ################################################################################################################################

    def _get_config_key(self, object_type, object_name):
        # type: (unicode, unicode) -> unicode
        return '{}:{}'.format(object_type, object_name)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    cid = 'abc123'

    object_type = 'http_soap'
    object_name = 'My Channel'

    object_dict = {
        'id':    123,
        'type_': object_type,
        'name':  object_name
    }

    definition = """
    10.0.0.0 = 1/m
    * = 1/m
    * = 2/d

    192.168.1.123 = 11/m
    10.210.0.0/18 = 22/h
    #127.0.0.1/32  = 1/d
    """

    rate_limiting = RateLimiting()
    rate_limiting.create(object_dict, definition)

    rate_limiting.check_limit(cid, object_type, object_name, '127.0.0.1')
    rate_limiting.check_limit(cid, object_type, object_name, '127.0.0.1')

# ################################################################################################################################
