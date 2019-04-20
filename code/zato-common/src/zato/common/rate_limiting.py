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
from future.utils import iterkeys
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
    __slots__ = 'current_idx', 'lock', 'api', 'object_info', 'definition', 'has_from_any', 'from_any_rate', 'from_any_unit', \
        'is_limit_reached', 'ip_address_cache', 'current_period_func', 'by_period', 'parent_type', 'parent_name'

    def __init__(self):
        self.current_idx = 0
        self.lock = RLock()
        self.api = None            # type: RateLimiting
        self.object_info = None    # type: ObjectInfo
        self.definition = None     # type: list
        self.has_from_any = None   # type: bool
        self.from_any_rate = None  # type: int
        self.from_any_unit = None  # type: unicode
        self.ip_address_cache = {} # type: dict
        self.by_period = {}        # type: dict
        self.parent_type = None    # type: unicode
        self.parent_name = None    # type: unicode

        self.current_period_func = {
            Const.Unit.day: self._get_current_day,
            Const.Unit.hour: self._get_current_hour,
            Const.Unit.minute: self._get_current_minute,
        }

# ################################################################################################################################

    @property
    def has_parent(self):
        return self.parent_type and self.parent_name

# ################################################################################################################################

    def cleanup(self):
        """ Cleans up time periods that are no longer needed.
        """
        with self.lock:
            now = datetime.utcnow()
            current_minute = self._get_current_minute(now)
            current_hour = self._get_current_hour(now)
            current_day = self._get_current_day(now)

            # We need a copy so as not to modify the dict in place
            periods = list(iterkeys(self.by_period))
            to_delete = set()

            period_map = {
                Const.Unit.minute: current_minute,
                Const.Unit.hour: current_hour,
                Const.Unit.day: current_day
            }

            for period in periods: # type: unicode
                period_unit = period[0] # type: unicode # One of Const.Unit instances
                current_period = period_map[period_unit]

                # If this period is in the past, add it to the ones to be deleted
                if period < current_period:
                    to_delete.add(period)

            for item in to_delete: # item: unicode
                del self.by_period[item]

# ################################################################################################################################

    def rewrite_rate_data(self, old_config):
        """ Writes rate limiting information from old configuration to our own. Used by RateLimiting.edit action.
        """
        # type: (ObjectConfig)

        # Already collected rate limits
        self.by_period.clear()
        self.by_period.update(old_config.by_period)

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

        # Above, we checked our own rate limit but it is still possible that we have a parent
        # that also wants to check it.
        if self.has_parent:
            self.api.check_limit(cid, self.parent_type, self.parent_name, orig_from)

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

    def _get_config_key(self, object_type, object_name):
        # type: (unicode, unicode) -> unicode
        return '{}:{}'.format(object_type, object_name)

# ################################################################################################################################

    def _get_config_by_object(self, object_type, object_name):
        # type: (unicode, unicode) -> ObjectConfig
        return self.config_store.get(self._get_config_key(object_type, object_name))

# ################################################################################################################################

    def _create_config(self, object_dict, definition):
        # type: (dict, unicode) -> ObjectConfig

        info = ObjectInfo()
        info.type_ = object_dict['type_']
        info.name = object_dict['name']

        parsed = self.parser.parse(definition)
        def_first = parsed[0]
        has_from_any = def_first.from_ == Const.from_any

        config = ObjectConfig()
        config.api = self
        config.object_info = info
        config.definition = parsed
        config.parent_type = object_dict['parent_type']
        config.parent_name = object_dict['parent_name']

        if has_from_any:
            config.has_from_any = has_from_any
            config.from_any_rate = def_first.rate
            config.from_any_unit = def_first.unit

        return config

# ################################################################################################################################

    def create(self, object_dict, definition):
        # type: (dict, unicode)
        config = self._create_config(object_dict, definition)
        self.config_store[config.get_config_key()] = config

# ################################################################################################################################

    def check_limit(self, cid, object_type, object_name, from_):
        """ Checks if input object has already reached its allotted usage limit.
        """
        # type: (unicode, unicode, unicode, unicode)

        with self.lock:
            config = self._get_config_by_object(object_type, object_name)

        # It is possible that we do not have configuration for such an object,
        # in which case we will log a warning.
        if config:
            with config.lock:
                config.check_limit(cid, from_)
        else:
            logger.warn('No such rate limiting object `%s` (%s)', object_name, object_type)

# ################################################################################################################################

    def _delete(self, object_type, object_name, remove_parent):
        """ Deletes configuration for input data, optionally deleting references to it from all objects that depended on it.
        Must be called with self.lock held.
        """
        # type: (unicode, unicode, bool)

        config_key = self._get_config_key(object_type, object_name)
        del self.config_store[config_key]

        if remove_parent:
            self._set_new_parent(object_type, old_object_name, None, None)

# ################################################################################################################################

    def _set_new_parent(self, parent_type, old_parent_name, new_parent_type, new_parent_name):
        """ Sets new parent for all configuration entries matching the old one. Must be called with self.lock held.
        """
        # type: (unicode, unicode, unicode, unicode)

        for child_config in self.config_store.values(): # type: ObjectConfig
            object_info = child_config.object_info

            # This is our own config
            if object_info.type_ == parent_type and object_info.name == old_parent_name:
                continue

            # This object has a parent, possibly it is our very configuration
            if child_config.has_parent:

                # Yes, this is our config ..
                if child_config.parent_type == parent_type and child_config.parent_name == old_parent_name:

                    # We typically want to change the parent's name but it is possible
                    # that both type and name will be None (in case we are removing a parent from a child object)
                    # which is why both are set here.
                    child_config.parent_type = new_parent_type
                    child_config.parent_name = new_parent_name

# ################################################################################################################################

    def edit(self, object_type, old_object_name, object_dict, definition):
        """ Changes, in place, an existing configuration entry to input data.
        """
        # type: (unicode, unicode, dict, unicode)

        # Note the whole of this operation is under self.lock to make sure the update is atomic
        # from our callers' perspective.
        with self.lock:
            old_config = self._get_config_by_object(object_type, old_object_name)

            if not old_config:
                raise ValueError('Rate limiting object not found `{}` ({})'.format(old_object_name, object_type))

            # Just to be sure we are doing the right thing, compare object types, old and new
            if object_type != old_config.object_info.type_:
                raise ValueError('Unexpected object_type, old:`{}`, new:`{}` ({}) ({})'.format(
                    old_config.object_info.type_, object_type, old_object_name, object_dict))

            # Now, create a new config object ..
            new_config = self._create_config(object_dict, definition)

            # .. move existing rate limiting data from the old config object to the new one
            new_config.rewrite_rate_data(old_config)

            # .. in case it was a rename ..
            if old_config.object_info.name != new_config.object_info.name:

                # .. make all child objects depend on the new name, in case it changed
                self._set_new_parent(object_type, old_object_name, new_config.object_info.type_, new_config.object_info.name)

                # First, delete the old configuration, but do not delete any objects that depended on it
                # because we are just editing the former, not deleting it altogether.
                self._delete(object_type, old_object_name, False)

                #
                self.config_store[new_config.get_config_key()] = new_config

# ################################################################################################################################

    def delete(self, object_type, object_name):
        """ Deletes configuration for input object and clears out parent references to it.
        """
        with self.lock:
            self._delete(object_type, object_name, True)

# ################################################################################################################################

    def cleanup(self):
        """ Invoked periodically by the scheduler - goes through all configuration elements and cleans up
        all time periods that are no longer needed.
        """
        for config in self.config_store.values(): # type: ObjectConfig
            config.cleanup()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    def get_channel_config():
        return {
            'id': 333,
            'parent_type': 'sso_user',
            'parent_name': 'Joan Doe',
            'type_': 'http_soap',
            'name': 'My Endpoint',
        }

    def get_channel_definition():
        return """
        192.168.1.123 = 11/m
        127.0.0.1/32  = 6/m
        """

    def get_sec_def_config():
        return {
            'id': 222,
            'parent_type': 'sso_user',
            'parent_name': 'Joan Doe',
            'type_': 'api_key',
            'name': 'API Key',
        }

    def get_sec_def_definition():
        return """
        127.0.0.1/32  = 6/m
        """

    def get_user_config(name_suffix=''):
        return {
            'id': 111,
            'parent_type': None,
            'parent_name': None,
            'type_': 'sso_user',
            'name': 'Joan Doe' + name_suffix,
        }

    def get_user_definition(prefix=''):
        return """
        10.210.0.0/18 = 22/h
        #127.0.0.1/32  = {}1/m
        * = 2/m
        """.format(prefix)

    user_config        = get_user_config()
    user_definition    = get_user_definition()

    channel_config     = get_channel_config()
    channel_definition = get_channel_definition()

    sec_def_config     = get_sec_def_config()
    sec_def_definition = get_sec_def_definition()

    rate_limiting = RateLimiting()

    rate_limiting.create(user_config, user_definition)
    rate_limiting.create(channel_config, channel_definition)
    rate_limiting.create(sec_def_config, sec_def_definition)

    cid = 123
    rate_limiting.check_limit(cid, 'http_soap', 'My Endpoint', '127.0.0.1')

    cid = 456
    rate_limiting.check_limit(cid, 'api_key', 'API Key', '127.0.0.1')

    rate_limiting.edit('sso_user', 'Joan Doe', get_user_config(' 2'), get_user_definition(2))
    rate_limiting.edit('sso_user', 'Joan Doe 2', get_user_config(' 3'), get_user_definition(3))

    cid = 789
    rate_limiting.check_limit(cid, 'api_key', 'API Key', '127.0.0.1')

    rate_limiting.cleanup()

# ################################################################################################################################
