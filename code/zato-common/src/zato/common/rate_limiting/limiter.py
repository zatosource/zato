# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from copy import deepcopy
from datetime import datetime

# gevent
from gevent.lock import RLock

# netaddr
from netaddr import IPAddress

# Zato
from zato.common.odb.model import RateLimitState
from zato.common.odb.query.rate_limiting import current_period_list, current_state as current_state_query
from zato.common.rate_limiting.common import Const, AddressNotAllowed, RateLimitReached

# Python 2/3 compatibility
from future.utils import iterkeys

# ################################################################################################################################

if 0:

    # stdlib
    from typing import Callable

    # Zato
    from zato.common.rate_limiting import Approximate as RateLimiterApproximate, RateLimiting
    from zato.common.rate_limiting.common import DefinitionItem, ObjectInfo

    # For pyflakes
    Callable = Callable
    DefinitionItem = DefinitionItem
    ObjectInfo = ObjectInfo
    RateLimiterApproximate = RateLimiterApproximate
    RateLimiting = RateLimiting

# ################################################################################################################################

RateLimitStateTable  = RateLimitState.__table__
RateLimitStateDelete = RateLimitStateTable.delete

# ################################################################################################################################
# ################################################################################################################################

class BaseLimiter(object):
    """ A per-server, approximate, rate limiter object. It is approximate because it does not keep track
    of what current rate limits in other servers are.
    """
    __slots__ = 'current_idx', 'lock', 'api', 'object_info', 'definition', 'has_from_any', 'from_any_rate', 'from_any_unit', \
        'is_limit_reached', 'ip_address_cache', 'current_period_func', 'by_period', 'parent_type', 'parent_name', \
        'is_exact', 'from_any_object_id', 'from_any_object_type', 'from_any_object_name', 'cluster_id', 'is_active', \
        'invocation_no'

    initial_state = {
        'requests': 0,
        'last_cid': None,
        'last_request_time_utc': None,
        'last_from': None,
        'last_network': None,
    }

    def __init__(self, cluster_id):
        # type: (int)
        self.cluster_id = cluster_id
        self.is_active = None
        self.current_idx = 0
        self.lock = RLock()
        self.api = None            # type: RateLimiting
        self.object_info = None    # type: ObjectInfo
        self.definition = None     # type: list
        self.has_from_any = None   # type: bool
        self.from_any_rate = None  # type: int
        self.from_any_unit = None  # type: str
        self.ip_address_cache = {} # type: dict
        self.by_period = {}        # type: dict
        self.parent_type = None    # type: str
        self.parent_name = None    # type: str
        self.is_exact = None       # type: bool
        self.invocation_no = 0     # type: int

        self.from_any_object_id = None   # type: int
        self.from_any_object_type = None # type: str
        self.from_any_object_name = None # type: str

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

            # First, periodically clear out the IP cache to limit its size to 1,000 items
            if len(self.ip_address_cache) >= 1000:
                self.ip_address_cache.clear()

            now = datetime.utcnow()
            current_minute = self._get_current_minute(now)
            current_hour = self._get_current_hour(now)
            current_day = self._get_current_day(now)

            # We need a copy so as not to modify the dict in place
            periods = self._get_current_periods()
            to_delete = set()

            current_periods_map = {
                Const.Unit.minute: current_minute,
                Const.Unit.hour: current_hour,
                Const.Unit.day: current_day
            }

            for period in periods: # type: str
                period_unit = period[0] # type: str # One of Const.Unit instances
                current_period = current_periods_map[period_unit]

                # If this period is in the past, add it to the ones to be deleted
                if period < current_period:
                    to_delete.add(period)

            if to_delete:
                self._delete_periods(to_delete)

# ################################################################################################################################

    def rewrite_rate_data(self, old_config):
        """ Writes rate limiting information from old configuration to our own. Used by RateLimiting.edit action.
        """
        # type: (RateLimiterApproximate)

        # Already collected rate limits
        self.by_period.clear()
        self.by_period.update(old_config.by_period)

# ################################################################################################################################

    def get_config_key(self):
        # type: () -> str
        return '{}:{}'.format(self.object_info.type_, self.object_info.name)

# ################################################################################################################################

    def _get_rate_config_by_from(self, orig_from, _from_any=Const.from_any):
        # type: (str, str) -> DefinitionItem

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
            raise AddressNotAllowed('Address not allowed `{}`'.format(orig_from))

        # We found a matching piece of from IP configuration
        return found

# ################################################################################################################################

    def _get_current_day(self, now, _prefix=Const.Unit.day, _format='%Y-%m-%d'):
        # type: (datetime, str, str) -> str
        return '{}.{}'.format(_prefix, now.strftime(_format))

    def _get_current_hour(self, now, _prefix=Const.Unit.hour, _format='%Y-%m-%dT%H'):
        # type: (datetime, str, str) -> str
        return '{}.{}'.format(_prefix, now.strftime(_format))

    def _get_current_minute(self, now, _prefix=Const.Unit.minute, _format='%Y-%m-%dT%H:%M'):
        # type: (datetime, str, str) -> str
        return '{}.{}'.format(_prefix, now.strftime(_format))

# ################################################################################################################################

    def _format_last_info(self, current_state):
        # type: (dict) -> str

        return 'last_from:`{last_from}; last_request_time_utc:`{last_request_time_utc}; last_cid:`{last_cid}`;'.format(
            **current_state)

# ################################################################################################################################

    def _raise_rate_limit_exceeded(self, rate, unit, orig_from, network_found, current_state, cid,
            def_object_id, def_object_name, def_object_type):

        raise RateLimitReached('Max. rate limit of {}/{} reached; from:`{}`, network:`{}`; {} (cid:{}) (def:{} {} {})'.format(
            rate, unit, orig_from, network_found, self._format_last_info(current_state), cid, def_object_id, def_object_type,
            def_object_name))

# ################################################################################################################################

    def _check_limit(self, cid, orig_from, network_found, rate, unit, def_object_id, def_object_name, def_object_type,
        _rate_any=Const.rate_any, _utcnow=datetime.utcnow):
        # type: (str, str, str, int, str, str, object, str, str)

        # Increase invocation counter
        self.invocation_no += 1

        # Local aliases
        now = _utcnow()

        # Get current period, e.g. current day, hour or minute
        current_period_func = self.current_period_func[unit]
        current_period = current_period_func(now)
        current_state = self._get_current_state(current_period, network_found)

        # Unless we are allowed to have any rate ..
        if rate != _rate_any:

            # We may have reached the limit already ..
            if current_state['requests'] >= rate:
                self._raise_rate_limit_exceeded(rate, unit, orig_from, network_found, current_state, cid,
                    def_object_id, def_object_name, def_object_type)

        # Update current metadata state
        self._set_new_state(current_state, cid, orig_from, network_found, now, current_period)

        # Above, we checked our own rate limit but it is still possible that we have a parent
        # that also wants to check it.
        if self.has_parent:
            self.api.check_limit(cid, self.parent_type, self.parent_name, orig_from)

        # Clean up old entries periodically
        if self.invocation_no % 1000 == 0:
            self.cleanup()

# ################################################################################################################################

    def check_limit(self, cid, orig_from):
        # type: (str, str)

        with self.lock:

            if self.has_from_any:
                rate = self.from_any_rate
                unit = self.from_any_unit
                network_found = Const.from_any
                def_object_id = None
                def_object_type = None
                def_object_name = None
            else:
                found = self._get_rate_config_by_from(orig_from)
                rate = found.rate
                unit = found.unit
                network_found = found.from_
                def_object_id = found.object_id
                def_object_type = found.object_type
                def_object_name = found.object_name

            # Now, check actual rate limits
            self._check_limit(cid, orig_from, network_found, rate, unit, def_object_id, def_object_name, def_object_type)

# ################################################################################################################################

    def _get_current_periods(self):
        raise NotImplementedError()

    _get_current_state = _set_new_state = _delete_periods = _get_current_periods

# ################################################################################################################################
# ################################################################################################################################

class Approximate(BaseLimiter):

    def _get_current_periods(self):
        return list(iterkeys(self.by_period))

# ################################################################################################################################

    def _delete_periods(self, to_delete):
        for item in to_delete: # item: str
            del self.by_period[item]

# ################################################################################################################################

    def _get_current_state(self, current_period, network_found):
        # type: (str, str) -> dict

        # Get or create a dictionary of requests information for current period
        period_dict = self.by_period.setdefault(current_period, {}) # type: dict

        # Get information about already stored requests for that network in current period
        return period_dict.setdefault(network_found, deepcopy(self.initial_state))

# ################################################################################################################################

    def _set_new_state(self, current_state, cid, orig_from, network_found, now, *ignored):
        current_state['requests'] += 1
        current_state['last_cid'] = cid
        current_state['last_request_time_utc'] = now.isoformat()
        current_state['last_from'] = orig_from
        current_state['last_network'] = str(network_found)

# ################################################################################################################################
# ################################################################################################################################

class Exact(BaseLimiter):

    def __init__(self, cluster_id, sql_session_func):
        # type: (int, Callable)
        super(Exact, self).__init__(cluster_id)
        self.sql_session_func = sql_session_func

# ################################################################################################################################

    def _fetch_current_state(self, session, current_period, network_found):
        # type: (str, str) -> RateLimitState

        # We have a complex Python object but for the query we just need its string representation
        network_found = str(network_found)

        return current_state_query(session, self.cluster_id, self.object_info.type_, self.object_info.id,
            current_period, network_found).\
            first()

# ################################################################################################################################

    def _get_current_state(self, current_period, network_found):
        # type: (str, str) -> dict

        current_state = deepcopy(self.initial_state) # type: dict

        with closing(self.sql_session_func()) as session:
            item = self._fetch_current_state(session, current_period, network_found)

        if item:
            current_state.update(item.asdict())

        return current_state

# ################################################################################################################################

    def _set_new_state(self, current_state, cid, orig_from, network_found, now, current_period):

        # We just need a string representation of this object
        network_found = str(network_found)

        with closing(self.sql_session_func()) as session:
            item = self._fetch_current_state(session, current_period, network_found)

            if item:
                item.last_cid = cid
                item.last_from = orig_from
                item.last_request_time_utc = now
            else:
                item = RateLimitState()
                item.cluster_id = self.cluster_id
                item.object_type = self.object_info.type_
                item.object_id = self.object_info.id
                item.requests = 0
                item.period = current_period
                item.network = network_found
                item.last_cid = cid
                item.last_from = orig_from
                item.last_network = network_found
                item.last_request_time_utc = now

            item.requests += 1

            session.add(item)
            session.commit()

# ################################################################################################################################

    def _get_current_periods(self):
        with closing(self.sql_session_func()) as session:
            return [elem[0] for elem in current_period_list(session, self.cluster_id).\
                   all()]

# ################################################################################################################################

    def _delete_periods(self, to_delete):
        with closing(self.sql_session_func()) as session:
            session.execute(RateLimitStateDelete().where(
                RateLimitStateTable.c.period.in_(to_delete)
            ))
            session.commit()

# ################################################################################################################################
# ################################################################################################################################
