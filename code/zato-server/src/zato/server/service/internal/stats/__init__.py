# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

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

# Bunch
from bunch import Bunch

# dateutil
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from dateutil.rrule import MINUTELY, rrule, rruleset

# SciPy
from scipy import stats as sp_stats

# Python 2/3 compatibility
from future.utils import iteritems
from zato.common.py23_ import maxint

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
        key_len = self.server.kvdb.conn.llen(key)
        if max_batch_size:
            batch_size = min(key_len, max_batch_size)
            if batch_size < key_len:
                msg = 'batch_size:`%s` < key_len:`%s`, max_batch_size:`%s`, key:`%s`, ' \
                'consider decreasing the job interval or increasing max_batch_size'
                self.logger.warn(msg, batch_size, key_len, max_batch_size, key)
        else:
            batch_size = key_len

        times = [int(elem) for elem in self.server.kvdb.conn.lrange(key, 0, batch_size)]

        if times:
            mean_percentile = int(self.server.kvdb.conn.hget(KVDB.SERVICE_TIME_BASIC + service_name, 'mean_percentile') or 0)
            max_score = int(sp_stats.scoreatpercentile(times, mean_percentile))

            return min(times), max(times), (sp_stats.tmean(times, (None, max_score)) or 0), len(times)
        else:
            return 0, 0, 0, 0

    def collect_service_stats(self, keys_pattern, key_prefix, key_suffix, total_seconds,
                              suffix_needs_colon=True, chop_off_service_name=True, needs_rate=True):

        service_stats = {}
        if suffix_needs_colon:
            key_suffix = ':' + key_suffix

        for key in self.kvdb.conn.keys(keys_pattern):
            service_name = key.replace(key_prefix, '').replace(key_suffix, '')
            if chop_off_service_name:
                service_name = service_name[:-3]

            values = self.kvdb.conn.hgetall(key)

            stats = service_stats.setdefault(service_name, {})

            for name in STATS_KEYS:

                value = values.get(name)
                if value:
                    if name in('rate', 'mean'):
                        value = float(value)
                    else:
                        value = int(value)

                    if not name in stats:
                        if name == 'mean':
                            stats[name] = []
                        elif name == 'min':
                            stats[name] = maxint
                        else:
                            stats[name] = 0

                    if name == 'usage':
                        stats[name] += value
                    elif name == 'max':
                        stats[name] = max(stats[name], value)
                    elif name == 'mean':
                        stats[name].append(value)
                    elif name == 'min':
                        stats[name] = min(stats[name], value)

        for service_name, values in service_stats.items():
            mean = values.get('mean')
            if mean:
                values['mean'] = sp_stats.tmean(mean)

            if needs_rate:
                values['rate'] = values['usage'] / total_seconds

        return service_stats

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
    """ A low-level services that periodically process raw data collected for statistics.
    """
    def handle(self):

        if not self.stats_enabled():
            return

        #
        # Sample config values
        #
        # global_slow_threshold=120
        # max_batch_size=99999
        #
        config = Bunch()
        for item in self.request.payload.splitlines():
            key, value = item.split('=')
            config[key] = int(value)

        for key in self.server.kvdb.conn.keys(KVDB.SERVICE_TIME_RAW + '*'):

            service_name = key.replace(KVDB.SERVICE_TIME_RAW, '')

            current_mean = float(
                self.server.kvdb.conn.hget(KVDB.SERVICE_TIME_BASIC + service_name, 'mean_all_time') or 0)
            current_min = float(self.server.kvdb.conn.hget(KVDB.SERVICE_TIME_BASIC + service_name, 'min_all_time') or 0)
            current_max = float(self.server.kvdb.conn.hget(KVDB.SERVICE_TIME_BASIC + service_name, 'max_all_time') or 0)

            batch_min, batch_max, batch_mean, batch_total = self.aggregate_raw_times(
                key, service_name, config.max_batch_size)

            self.server.kvdb.conn.hset(
               KVDB.SERVICE_TIME_BASIC + service_name, 'mean_all_time', sp_stats.tmean((batch_mean, current_mean)))
            self.server.kvdb.conn.hset(
               KVDB.SERVICE_TIME_BASIC + service_name, 'min_all_time', min(current_min, batch_min))
            self.server.kvdb.conn.hset(
                KVDB.SERVICE_TIME_BASIC + service_name, 'max_all_time', max(current_max, batch_max))

            # Services use RPUSH for storing raw times so we are safe to use LTRIM
            # in order to do away with the already processed ones
            self.server.kvdb.conn.ltrim(key, batch_total, -1)

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
        """ Returns statistics for a given interval, as defined by 'start' and 'stop'.
        service default to '*' for all services in that period and may be set to return
        a one-element list of information regarding that particular service. Setting 'n'
        to a positive integer will make it return only top n services.
        """
        if not stats_key_prefix:
            stats_key_prefix = self.stats_key_prefix

        stats_elems = {}
        all_services_stats = Bunch({'usage':0, 'time':0})

        # All mean values
        mean_all_services_list = []

        # A mean value of all the mean values (mean_all_services_list)
        mean_all_services = 0

        start = parse(start)
        stop = parse(stop)
        delta = (stop - start)

        if hasattr(delta, 'total_seconds'):
            delta_seconds = delta.total_seconds()
        else:
            delta_seconds = delta.seconds

        if not suffixes:
            suffixes = self.get_suffixes(start, stop)

        # We make several passes. First two passes are made over Redis keys, one gathers the services, if any at all,
        # and another one actually collects statistics for each service found. Next pass, a partly optional one,
        # computes trends for mean response time and service usage. Another one computes each of the service's
        # average rate and updates other attributes basing on values collected in the previous step.
        # Optionally, the last one will pick only top n elements of a given type (top mean response time
        # or top usage).

        # 1st pass
        for suffix in suffixes:
            keys = self.server.kvdb.conn.keys('{}{}:{}'.format(stats_key_prefix, service, suffix))
            for key in keys:
                service_name = key.replace(stats_key_prefix, '').replace(':{}'.format(suffix), '')

                stats_elem = StatsElem(service_name)
                stats_elems[service_name] = stats_elem

                # When building statistics, we can't expect there will be data for all the time
                # elems built above so to guard against it, this is a dictionary whose keys are the
                # said elems and values are mean/usage for each elem. The values will remain
                # 0/0.0 if there is no data for the time elem, which may mean that in this
                # particular time slice the service wasn't invoked at all.
                stats_elem.expected_time_elems = OrderedDict(
                    (elem, Bunch({'mean':0, 'usage':0.0})) for elem in suffixes)

        # 2nd pass
        for service, stats_elem in stats_elems.items():
            for suffix in suffixes:
                key = '{}{}:{}'.format(stats_key_prefix, service, suffix)

                # We can convert all the values to floats here to ease with computing
                # all the stuff and convert them still to integers later on, when necessary.
                key_values = Bunch(
                    ((name, float(value)) for (name, value) in iteritems(self.server.kvdb.conn.hgetall(key))))

                if key_values:

                    time = (key_values.usage * key_values.mean)
                    stats_elem.time += time

                    mean_all_services_list.append(key_values.mean)
                    all_services_stats.time += time
                    all_services_stats.usage += key_values.usage

                    stats_elem.min_resp_time = min(stats_elem.min_resp_time, key_values.min)
                    stats_elem.max_resp_time = max(stats_elem.max_resp_time, key_values.max)

                    for attr in('mean', 'usage'):
                        stats_elem.expected_time_elems[suffix][attr] = key_values[attr]

        mean_all_services = '{:.0f}'.format(sp_stats.tmean(mean_all_services_list)) if mean_all_services_list else 0

        # 3rd pass (partly optional)
        for stats_elem in stats_elems.values():

            stats_elem.mean_all_services = mean_all_services
            stats_elem.all_services_time = int(all_services_stats.time)
            stats_elem.all_services_usage = int(all_services_stats.usage)

            values = stats_elem.expected_time_elems.values()

            stats_elem.mean_trend_int = [int(elem.mean) for elem in values]
            stats_elem.usage_trend_int = [int(elem.usage) for elem in values]

            stats_elem.mean = float('{:.2f}'.format(sp_stats.tmean(stats_elem.mean_trend_int)))
            stats_elem.usage = sum(stats_elem.usage_trend_int)
            stats_elem.rate = float('{:.2f}'.format(sum(stats_elem.usage_trend_int) / delta_seconds))

            self.set_percent_of_all_services(all_services_stats, stats_elem)

            if needs_trends:
                stats_elem.mean_trend = ','.join(str(elem) for elem in stats_elem.mean_trend_int)
                stats_elem.usage_trend = ','.join(str(elem) for elem in stats_elem.usage_trend_int)

        # 4th pass (optional)
        if n:
            for stats_elem in self.yield_top_n(n, n_type, stats_elems):
                yield stats_elem

        else:
            for stats_elem in stats_elems.values():
                yield stats_elem

class GetByService(StatsReturningService):
    """ Returns statistics regarding a particular service.
    """
    class SimpleIO(StatsReturningService.SimpleIO):
        request_elem = 'zato_stats_get_by_service_request'
        response_elem = 'zato_stats_get_by_service_response'
        input_required = StatsReturningService.SimpleIO.input_required + ('service_id',)
        input_optional = ('service_name',)
        output_optional = ('service_name', 'usage', 'mean', 'rate', 'time', 'usage_trend', 'mean_trend',
                    'min_resp_time', 'max_resp_time',)

    def handle(self):
        with closing(self.odb.session()) as session:
            service = session.query(Service).\
                filter(Service.id==self.request.input.service_id).\
                one()

        stats_elem = list(self.get_stats(self.request.input.start, self.request.input.stop, service.name))
        if stats_elem:
            stats_elem = stats_elem[0]
            self.response.payload = Bunch(stats_elem.to_dict())

# ##############################################################################
