# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
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
from dateutil.rrule import MINUTELY, rrule

# SciPy
from scipy import stats as sp_stats

# Zato
from zato.common import KVDB, StatsElem, ZatoException
from zato.common.broker_message import STATS
from zato.common.odb.model import Service
from zato.server.service.internal import AdminService

class Delete(AdminService):
    """ Deletes aggregated statistics from a given interval.
    """
    class SimpleIO:
        input_required = ('start', 'stop')

    def handle(self):
        self.broker_client.send(
            {'action':STATS.DELETE, 'start':self.request.input.start, 'stop':self.request.input.stop})

class _AggregatingService(AdminService):
    """ A base class for all services that process raw times into aggregates values.
    """
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
                msg = ('batch_size:[{}] < key_len:[{}], max_batch_size:[{}], key:[{}], '
                'consider decreasing the job interval or increasing the max_batch_size').format(
                    batch_size, key_len, max_batch_size, key)
                self.logger.warn(msg)
        else:
            batch_size = key_len
            
        times = [int(elem) for elem in self.server.kvdb.conn.lrange(key, 0, batch_size)]
        
        mean_percentile = int(self.server.kvdb.conn.hget(
            KVDB.SERVICE_TIME_BASIC + service_name, 'mean_percentile') or 0)
        max_score = int(sp_stats.scoreatpercentile(times, mean_percentile))
        
        return min(times), max(times), (sp_stats.tmean(times, (None, max_score)) or 0), len(times)
        
    def aggregate_partly_aggregated(self, delta, source_strftime_format, source, target):
        """ Further aggregates service statistics, e.g. turns per-minute statistics
        into per-hour statistcs.
        """
        now = datetime.utcnow()
        delta_diff = (now - delta)
        
        if hasattr(delta, 'total_seconds'):
            total_seconds = delta.total_seconds() 
        else:
            # I.e. number of days in the month * seconds a day has
            total_seconds = mdays[delta_diff.month] * 86400
        
        stats_keys = ('usage', 'max', 'rate', 'mean', 'min')
        key_suffix = (now - delta).strftime(source_strftime_format)

        service_stats = {}
        
        for key in self.server.kvdb.conn.keys('{}*:{}*'.format(source, key_suffix)):

            service_name = key.replace(source, '').replace(':' + key_suffix, '')[:-3]
            values = self.server.kvdb.conn.hgetall(key)
            
            stats = service_stats.setdefault(service_name, {})
            
            for name in stats_keys:
            
                value = values[name]
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
            values['rate'] = values['usage'] / total_seconds
            values['mean'] = sp_stats.tmean(values['mean'])
            
            aggr_key = '{}{}:{}'.format(target, service_name, key_suffix)
            
            for name in stats_keys:
                self.server.kvdb.conn.hset(aggr_key, name, values[name])
        
    def hset_aggr_key(self, aggr_key, hash_key, hash_value):
        self.server.kvdb.conn.hset(aggr_key, hash_key, hash_value)

class ProcessRawTimes(_AggregatingService):
    def handle(self):
        
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

class AggregateByMinute(_AggregatingService):
    """ Aggregates per-minute times.
    """
    def handle(self):
        
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
            
            # Per-minute statistics keys will expire by themselves, we don't need
            # to delete them manually.
            
class AggregateByHour(_AggregatingService):
    """ Creates per-hour stats.
    """
    def handle(self):
        delta = timedelta(hours=1)
        source_strftime_format = '%Y:%m:%d:%H'
        source = KVDB.SERVICE_TIME_AGGREGATED_BY_MINUTE
        target = KVDB.SERVICE_TIME_AGGREGATED_BY_HOUR
        
        self.aggregate_partly_aggregated(delta, source_strftime_format, source, target)
        
class AggregateByDay(_AggregatingService):
    """ Creates per-day stats.
    """
    def handle(self):
        delta = timedelta(days=1)
        source_strftime_format = '%Y:%m:%d'
        source = KVDB.SERVICE_TIME_AGGREGATED_BY_HOUR
        target = KVDB.SERVICE_TIME_AGGREGATED_BY_DAY
        
        self.aggregate_partly_aggregated(delta, source_strftime_format, source, target)
        
class AggregateByMonth(_AggregatingService):
    """ Creates per-month stats.
    """
    def handle(self):
        delta = relativedelta(datetime.utcnow(), months=1)
        source_strftime_format = '%Y:%m'
        source = KVDB.SERVICE_TIME_AGGREGATED_BY_DAY
        target = KVDB.SERVICE_TIME_AGGREGATED_BY_MONTH
        
        self.aggregate_partly_aggregated(delta, source_strftime_format, source, target)
            
class StatsReturningService(AdminService):
    """ A base class for services returning time-oriented statistics.
    """
    class SimpleIO:
        """ Consult StatsElem's docstring for the description of output parameters.
        """
        input_required = ('start', 'stop')
        input_optional = ('service_name', 'n', 'n_type')
        output_optional = ('service_name', 'usage', 'mean', 'rate', 'time', 'usage_trend', 'mean_trend',
            'min_resp_time', 'max_resp_time', 'all_services_usage', 'all_services_time',
            'mean_all_services', 'usage_perc_all_services', 'time_perc_all_services')

    def get_stats(self, start, stop, service='*', n=None, n_type=None):
        """ Returns statistics for a given interval, as defined by 'start' and 'stop'.
        service default to '*' for all services in that period and may be set to return
        a one-element list of information regarding that particular service. Setting 'n' 
        to a positive integer will make it return only top n services.
        """
        stats_elems = {}
        all_services_stats = Bunch({'usage':0, 'time':0})
    
        # All mean values
        mean_all_services_list = []
        
        # A mean value of all the mean values (mean_all_services_list)
        mean_all_services = 0
    
        start = parse(start)
        stop = parse(stop)
        
        delta_seconds = (stop - start).seconds
        
        time_elems = [elem.strftime('%Y:%m:%d:%H:%M') for elem in rrule(MINUTELY, dtstart=start, until=stop)]
        
        # We make several passes. First two passes are made over Redis keys, one gathers the services, if any at all,
        # and another one actually collects statistics for each service found. Next pass computes trends
        # for mean response time and service usage. Another one computes each of the service's
        # average rate and updates other attributes basing on values collected in the previous step.
        # Optionally, the last one will pick only top n elements of a given type (top mean response time
        # or top usage).
        
        # 1st pass
        for suffix in time_elems:
            keys = self.server.kvdb.conn.keys('{}{}:{}'.format(KVDB.SERVICE_TIME_AGGREGATED_BY_MINUTE, service, suffix))
            for key in keys:
                service_name = key.replace(KVDB.SERVICE_TIME_AGGREGATED_BY_MINUTE, '').replace(':{}'.format(suffix), '')
            
                stats_elem = StatsElem(service_name)
                stats_elems[service_name] = stats_elem
                
                # When building trends, we can't expect there will be data for all the time
                # elems built above so to guard against it, this is a dictionary whose keys are the
                # said elems and values are mean/usage for each elem. The values will remain
                # 0/0.0 if there is no data for the time elem, which may mean that in this
                # particular time slice the service wasn't invoked at all.
                stats_elem.expected_time_elems = OrderedDict(
                    (elem, Bunch({'mean':0, 'usage':0.0})) for elem in time_elems)
                
        # 2nd pass
        for service, stats_elem in stats_elems.items():
            for suffix in time_elems:
                key = '{}{}:{}'.format(KVDB.SERVICE_TIME_AGGREGATED_BY_MINUTE, service, suffix)
                
                # We can convert all the values to floats here to ease with computing
                # all the stuff and convert them still to integers later on, when necessary.
                key_values = Bunch(
                    ((name, float(value)) for (name, value) in self.server.kvdb.conn.hgetall(key).items()))
                
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
                        
        # 3rd pass
        for stats_elem in stats_elems.values():
            values = stats_elem.expected_time_elems.values()
            
            stats_elem.mean_trend_int = [int(elem.mean) for elem in values]
            stats_elem.mean_trend = ','.join(str(elem) for elem in stats_elem.mean_trend_int)
            stats_elem.mean = float('{:.2f}'.format(sp_stats.tmean(stats_elem.mean_trend_int)))
    
            stats_elem.usage_trend_int = [int(elem.usage) for elem in values]
            stats_elem.usage = sum(stats_elem.usage_trend_int)
            stats_elem.usage_trend = ','.join(str(elem) for elem in stats_elem.usage_trend_int)
    
            stats_elem.rate = float('{:.1f}'.format(sum(stats_elem.usage_trend_int) / delta_seconds))
    
            stats_elem.mean_all_services = mean_all_services
            stats_elem.all_services_time = int(all_services_stats.time)
            stats_elem.all_services_usage = int(all_services_stats.usage)
            
            for name in('time', 'usage'):
                if all_services_stats[name]:
                    value = float('{:.2f}'.format(100.0 * getattr(stats_elem, name) / all_services_stats[name]))
                    setattr(stats_elem, '{}_perc_all_services'.format(name), value)
    
        # 4th pass (optional)
        if n:
            if not n_type:
                msg = 'n_type must not be not None if n is neither, n:[{}], n_type:[{}]'.format(n, n_type)
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
        else:
            for stats_elem in stats_elems.values():
                yield stats_elem

class GetTopN(StatsReturningService):
    """ Returns top N slowest or most commonly used services for a given period.
    """
    class SimpleIO(StatsReturningService.SimpleIO):
        input_required = StatsReturningService.SimpleIO.input_required + ('n', 'n_type')

    def handle(self):
        self.response.payload[:] = (elem.to_dict() for elem in self.get_stats(self.request.input.start, 
            self.request.input.stop, n=int(self.request.input.n), n_type=self.request.input.n_type))

class GetByService(StatsReturningService):
    """ Returns statistics regarding a particular service.
    """
    class SimpleIO(StatsReturningService.SimpleIO):
        input_required = StatsReturningService.SimpleIO.input_required + ('service_id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            service = session.query(Service).\
                filter(Service.id==self.request.input.service_id).\
                one()
                
        stats_elem = list(self.get_stats(self.request.input.start, self.request.input.stop, service.name))
        if stats_elem:
            stats_elem = stats_elem[0]
            self.response.payload = Bunch(stats_elem.to_dict())
            
