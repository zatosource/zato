# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from calendar import mdays
from collections import OrderedDict
from contextlib import closing
from datetime import datetime, timedelta
from heapq import nlargest
from operator import itemgetter
from sys import maxint

# Bunch
from bunch import Bunch

# dateutil
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from dateutil.rrule import MINUTELY, rrule, rruleset

# Zato
from zato.common import KVDB, SECONDS_IN_DAY, StatsElem, ZatoException
from zato.common.broker_message import STATS
from zato.common.odb.model import Service
from zato.server.service import Integer, UTC
from zato.server.service.internal import AdminService, AdminSIO

STATS_KEYS = ('usage', 'max', 'rate', 'mean', 'min')

def stop_excluding_rrset(freq, start, stop):
    rrs = rruleset()
    rrs.rrule(rrule(freq, dtstart=start, until=stop))
    rrs.exdate(stop)

    return rrs

# ##############################################################################

class Delete(AdminService):
    """ Deletes aggregated statistics from a given interval.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_stats_delete_request'
        response_elem = 'zato_stats_delete_response'
        input_required = (UTC('start'), UTC('stop'))

    def handle(self):
        self.broker_client.invoke_async(
            {'action':STATS.DELETE.value, 'start':self.request.input.start, 'stop':self.request.input.stop})

# ##############################################################################

class BaseAggregatingService(AdminService):
    """ A base class for all services that process statistics into aggregated values.
    """
    def stats_enabled(self):
        return self.server.component_enabled.stats

    def aggregate_raw_times(self, key, service_name, max_batch_size=None):
        """ Aggregates values from a list living under a given key. Returns its
        min, max, mean and an overall usage count. 'max_batch_size' controls how
        many items will be fetched from the list so it's possible to fetch less
        items than its LLEN returns.
        """
        return 0, 0, 0, 0

    def collect_service_stats(self, keys_pattern, key_prefix, key_suffix, total_seconds,
                              suffix_needs_colon=True, chop_off_service_name=True, needs_rate=True):
        return {}

    def aggregate_partly_aggregated(self, delta, source_strftime_format, source, target, now=None):
        """ Further aggregates service statistics, e.g. turns per-minute statistics
        into per-hour statistcs.
        """
        if not now:
            now = datetime.utcnow()
        delta_diff = (now - delta)

        if hasattr(delta, 'total_seconds'):
            total_seconds = delta.total_seconds()
        else:
            # I.e. number of days in the month * seconds a day has
            total_seconds = mdays[delta_diff.month] * SECONDS_IN_DAY # TODO: Use calendar.monthrange instead of mdays so leap years are taken into account

        key_suffix = delta_diff.strftime(source_strftime_format)
        service_stats = self.collect_service_stats(
            '{}*:{}*'.format(source, key_suffix), source, key_suffix, total_seconds)

        self.hset_aggr_keys(service_stats, target, key_suffix)

    def hset_aggr_keys(self, service_stats, key_prefix, key_suffix):
        for service_name, values in service_stats.items():
            if service_name.endswith(':'):
                service_name = service_name[:-1]

            aggr_key = '{}{}:{}'.format(key_prefix, service_name, key_suffix)
            for name in STATS_KEYS:
                self.hset_aggr_key(aggr_key, name, values[name])

    def hset_aggr_key(self, aggr_key, hash_key, hash_value):
        self.server.kvdb.conn.hset(aggr_key, hash_key, hash_value)

        # Expire the aggregated key after that many hours
        expire_after = int(self.server.fs_server_config.get('stats', {}).get('expire_after', 24))
        expire_after = expire_after * 60 * 60 # Hours times minutes in an hour and seconds in a minute
        self.server.kvdb.conn.expire(aggr_key, expire_after)

# ##############################################################################

class ProcessRawTimes(BaseAggregatingService):
    def handle(self):
        pass

# ##############################################################################

class AggregateByMinute(BaseAggregatingService):
    """ Aggregates per-minute times.
    """
    def handle(self):

        if not self.stats_enabled():
            return

        # Get all keys from a minute that is sure to have passed, for instance,
        # say it's 13:19 right now (regardless of the seconds part), we'll process everything
        # that happened in 13:17. Hence it's also important that any changes in the minutes
        # to be picked up here below be kept in sync with the EXPIRE command Service._post_handle uses.

        now = datetime.utcnow()
        key_suffix = (now - timedelta(minutes=2)).strftime('%Y:%m:%d:%H:%M')

        for key in self.server.kvdb.conn.keys('{}*:{}'.format(KVDB.SERVICE_TIME_RAW_BY_MINUTE, key_suffix)):

            service_name = key.replace(KVDB.SERVICE_TIME_RAW_BY_MINUTE, '').replace(':' + key_suffix, '')
            aggr_key = '{}{}:{}'.format(KVDB.SERVICE_TIME_AGGREGATED_BY_MINUTE, service_name, key_suffix)

            batch_min, batch_max, batch_mean, batch_total = self.aggregate_raw_times(key, service_name)

            self.hset_aggr_key(aggr_key, 'min', batch_min)
            self.hset_aggr_key(aggr_key, 'max', batch_max)
            self.hset_aggr_key(aggr_key, 'mean', batch_mean)
            self.hset_aggr_key(aggr_key, 'usage', batch_total)
            self.hset_aggr_key(aggr_key, 'rate', batch_total / 60.0) # I.e. req/s

            # Raw per-minute statistics keys will expire by themselves, we don't need
            # to delete them manually.

class AggregateByHour(BaseAggregatingService):
    """ Creates per-hour stats.
    """
    def handle(self):

        if not self.stats_enabled():
            return

        delta = timedelta(hours=1)
        source_strftime_format = '%Y:%m:%d:%H'
        source = KVDB.SERVICE_TIME_AGGREGATED_BY_MINUTE
        target = KVDB.SERVICE_TIME_AGGREGATED_BY_HOUR

        self.aggregate_partly_aggregated(delta, source_strftime_format, source, target)

class AggregateByDay(BaseAggregatingService):
    """ Creates per-day stats.
    """
    def handle(self):

        if not self.stats_enabled():
            return

        delta = timedelta(days=1)
        source_strftime_format = '%Y:%m:%d'
        source = KVDB.SERVICE_TIME_AGGREGATED_BY_HOUR
        target = KVDB.SERVICE_TIME_AGGREGATED_BY_DAY

        self.aggregate_partly_aggregated(delta, source_strftime_format, source, target)

class AggregateByMonth(BaseAggregatingService):
    """ Creates per-month stats.
    """
    def handle(self):

        if not self.stats_enabled():
            return

        delta = relativedelta(datetime.utcnow(), months=1)
        source_strftime_format = '%Y:%m'
        source = KVDB.SERVICE_TIME_AGGREGATED_BY_DAY
        target = KVDB.SERVICE_TIME_AGGREGATED_BY_MONTH

        self.aggregate_partly_aggregated(delta, source_strftime_format, source, target)

# ##############################################################################

class StatsReturningService(AdminService):
    """ A base class for services returning time-oriented statistics.
    """
    class SimpleIO(AdminSIO):
        """ Consult StatsElem's docstring for the description of output parameters.
        """
        input_required = (UTC('start'), UTC('stop'))
        input_optional = ('service_name', Integer('n'), 'n_type')
        output_optional = ('service_name', 'usage', 'mean', 'rate', 'time', 'usage_trend', 'mean_trend',
            'min_resp_time', 'max_resp_time', 'all_services_usage', 'all_services_time',
            'mean_all_services', 'usage_perc_all_services', 'time_perc_all_services')

    stats_key_prefix = KVDB.SERVICE_TIME_AGGREGATED_BY_MINUTE

    def set_percent_of_all_services(self, all_services_stats, stats_elem):
        """ Sets how many per cent out of a total of all services this particular service constitutes.
        """
        for name in('time', 'usage'):
            if all_services_stats[name]:
                value = float('{:.2f}'.format(100.0 * getattr(stats_elem, name) / all_services_stats[name]))
                setattr(stats_elem, '{}_perc_all_services'.format(name), value)

    def yield_top_n(self, n, n_type, stats_elems):
        """ Yields top N services.
        """
        if not n_type:
            msg = 'n_type must not be None if n is neither, n:[{}], n_type:[{}]'.format(n, n_type)
            self.logger.error(msg)
            raise ZatoException(self.cid, msg)

        else:
            data = dict.fromkeys(stats_elems, 0)
            for name in data:
                data[name] = getattr(stats_elems[name], n_type)

            # It's itemgetter(1 ,0) because idx=1 is the actual value and idx=0
            # is a name so in the end nlargest returns values in ascending order
            # while also sorting lexicographically services that happen to have equal values.
            names = nlargest(n, data.items(), key=itemgetter(1, 0))
            for name, value in names:
                yield stats_elems[name]

    def get_suffixes(self, start, stop):
        return [elem.strftime('%Y:%m:%d:%H:%M') for elem in stop_excluding_rrset(MINUTELY, start, stop)]

    def get_stats(self, start, stop, service='*', n=None, n_type=None, needs_trends=True,
            stats_key_prefix=None, suffixes=None):
        pass

class GetByService(StatsReturningService):
    """ Returns statistics regarding a particular service.
    """
    class SimpleIO(StatsReturningService.SimpleIO):
        request_elem = 'zato_stats_get_by_service_request'
        response_elem = 'zato_stats_get_by_service_response'
        input_required = StatsReturningService.SimpleIO.input_required + ('service_id',)
        output_optional = ('service_name', 'usage', 'mean', 'rate', 'time', 'usage_trend', 'mean_trend',
                    'min_resp_time', 'max_resp_time',)

    def handle(self):
        pass

# ##############################################################################
