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
from contextlib import closing
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from heapq import nlargest
from itertools import izip, tee
from operator import itemgetter

# Bunch
from bunch import Bunch

# dateutil
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from dateutil.rrule import DAILY, MINUTELY, rrule

# SciPy
from scipy import stats as sp_stats

# Zato
from zato.common import KVDB, ZatoException
from zato.common.broker_message import MESSAGE_TYPE, STATS
from zato.common.odb.model import Service
from zato.common.odb.query import job_by_name
from zato.server.service.internal import AdminService

class _AggregatingService(AdminService):
    """ A base class for all services that process raw times into aggregates values.
    """
    def _aggregate(self, key, service_name, max_batch_size=None):
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
        
        mean_percentile = int(self.server.kvdb.conn.hget(KVDB.SERVICE_TIME_BASIC + service_name, 'mean_percentile') or 0)
        max_score = int(sp_stats.scoreatpercentile(times, mean_percentile))
        
        return min(times), max(times), (sp_stats.tmean(times, (None, max_score)) or 0), len(times)

class ProcessRawTimes(_AggregatingService):
    def handle(self):
        
        # 
        # Sample config values
        # 
        # global_slow_threshold=120
        # max_batch_size=100000
        #
        config = Bunch()
        for item in self.request.payload.splitlines():
            key, value = item.split('=')
            config[key] = int(value)

        for key in self.server.kvdb.conn.keys(KVDB.SERVICE_TIME_RAW + '*'):
            
            service_name = key.replace(KVDB.SERVICE_TIME_RAW, '')
            
            current_mean = float(self.server.kvdb.conn.hget(KVDB.SERVICE_TIME_BASIC + service_name, 'mean_all_time') or 0)
            current_min = float(self.server.kvdb.conn.hget(KVDB.SERVICE_TIME_BASIC + service_name, 'min_all_time') or 0)
            current_max = float(self.server.kvdb.conn.hget(KVDB.SERVICE_TIME_BASIC + service_name, 'max_all_time') or 0)
            
            batch_min, batch_max, batch_mean, batch_total = self._aggregate(key, service_name, config.max_batch_size)
            
            self.server.kvdb.conn.hset(KVDB.SERVICE_TIME_BASIC + service_name, 'mean_all_time', sp_stats.tmean((batch_mean, current_mean)))
            self.server.kvdb.conn.hset(KVDB.SERVICE_TIME_BASIC + service_name, 'min_all_time', min(current_min, batch_min))
            self.server.kvdb.conn.hset(KVDB.SERVICE_TIME_BASIC + service_name, 'max_all_time', max(current_max, batch_max))
            
            # Services use RPUSH for storing raw times so we are safe to use LTRIM
            # in order to do away with the already processed ones
            self.server.kvdb.conn.ltrim(key, batch_total, -1)

class AggregateByMinute(_AggregatingService):
    """ Aggregates per-miunte times.
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
            
            batch_min, batch_max, batch_mean, batch_total = self._aggregate(key, service_name)
            
            self.server.kvdb.conn.hset(aggr_key, 'min', batch_min)
            self.server.kvdb.conn.hset(aggr_key, 'max', batch_max)
            self.server.kvdb.conn.hset(aggr_key, 'mean', batch_mean)
            self.server.kvdb.conn.hset(aggr_key, 'usage', batch_total)
            self.server.kvdb.conn.hset(aggr_key, 'rate', batch_total / 60.0) # I.e. req/s
            
            # Per-minute statistic keys will expire by themselves, we don't need
            # to delete them manually.


class GetTopN(AdminService):
    """ Returns top N slowest or most commonly used services for a given period.
    """
    class SimpleIO:
        input_required = ('start', 'stop', 'n', 'granularity', 'trend_elems', 'stat_type')
        output_optional = ('position', 'service_name', 'value', 'trend', 'avg', 'total') 
        
    def handle(self):
    
        start = parse(self.request.input.start)
        stop = parse(self.request.input.stop)
        
        n = int(self.request.input.n)
        trend_elems = int(self.request.input.trend_elems)

        sort_order = (1, 0) # idx[1] = value, idx[0] = name
        
        stat_types = {'highest_mean':'mean', 'highest_usage':'usage'}
        if self.request.input.stat_type not in stat_types:
            msg = 'stat_type must be one of:[{}]'.format(stat_types.keys())
            self.logger.error(msg)
            raise ZatoException(self.cid, msg)

        # For now we always return the /largest/ N but it may well be true in the
        # future that we will return the opposite. In any case, mapping the stat
        # type to a stat attribute somewhat insulates us from changes in the Redis keyspace
        # even though the mapping isn't too impressive for now.
        stat_attr = stat_types[self.request.input.stat_type]

        overall = {stat_attr: 0}
        services = {}
        trends = {}
        suffixes = (elem.strftime(':%Y:%m:%d:%H:%M') for elem in rrule(MINUTELY, dtstart=start, until=stop))
        
        for suffix in suffixes:
            for key in self.server.kvdb.conn.keys('{}*{}'.format(KVDB.SERVICE_TIME_AGGREGATED_BY_MINUTE, suffix)):
                service_name = key.replace(KVDB.SERVICE_TIME_AGGREGATED_BY_MINUTE, '').replace(suffix, '')
                
                values = self.server.kvdb.conn.hgetall(key)
                services.setdefault(service_name, 0)
                trends.setdefault(service_name, [])
                
                value = int(float(values[stat_attr]))
                
                if stat_attr == 'mean':
                    services[service_name] = sp_stats.tmean((value, services[service_name]))
                else:
                    services[service_name] += value
                
                trends[service_name].append(str(value))
                
        services = nlargest(n, services.items(), key=itemgetter(1))
        services = sorted(services, key=itemgetter(*sort_order), reverse=True)
        
        values = [elem[1] for elem in services]
        if stat_attr == 'mean':
            avg = sp_stats.tmean(values)
        else:
            total = sum(values)
        
        for idx, (service_name, value) in enumerate(services):
            trend = trends[service_name]
            trend_template = ['0'] * trend_elems
            trend_template[trend_elems-len(trend):] = trend
            item = {'position':idx+1, 'service_name':service_name, 'value':value, 'trend':','.join(trend_template)}
            
            if stat_attr == 'mean':
                item['avg'] = avg
                item['total'] = ''
            else:
                item['avg'] = ''
                item['total'] = total
                
            self.response.payload.append(item)

class GetByService(AdminService):
    """ Returns basic statistics regarding a service, going back up to the period,
    expressed in minutes. The data returned is:
    - usage count
    - min, max and mean response time
    - CSV data for the period requested representing mean response time trend
    - CSV data for the period requested representing request rate (req/s) trend
    """
    class SimpleIO:
        input_required = ('service_id', 'minutes')
        output_required = ('usage', 'min', 'max', 'mean', 'rate', 'trend_mean', 'trend_rate')
        
    def handle(self):
        with closing(self.odb.session()) as session:
            service = session.query(Service).\
                filter_by(id=self.request.input.service_id).\
                one()
            
            minutes = int(self.request.input.minutes)
            now = datetime.utcnow()
            suffixes = ((now - timedelta(minutes=minute)).strftime('%Y:%m:%d:%H:%M') for minute in range(minutes, 1, -1))
            
            usage = 0
            min_ = None
            max_ = None
            mean = 0
            rate = 0
            trend_mean = []
            trend_rate = []
            
            for suffix in suffixes:
                key = '{}{}:{}'.format(KVDB.SERVICE_TIME_AGGREGATED_BY_MINUTE, service.name, suffix)
                items = self.server.kvdb.conn.hgetall(key)
                
                if items:
                    if not min_:
                        min_ = float(items['min'])
                    else:
                        min_ = min(min_, float(items['min']))
                        
                    if not max_:
                        max_ = float(items['max'])
                    else:
                        max_ = max(max_, float(items['max']))
                        
                    item_mean = float(items['mean'])
                    item_rate = float(items['rate'])

                    usage += int(items['usage'])
                    mean += item_mean
                    rate += item_rate
                    
                    trend_mean.append('{:.0f}'.format(item_mean))
                    trend_rate.append('{:.0f}'.format(item_rate))
                    
                else:
                    trend_mean.append('0')
                    trend_rate.append('0')
                    
            mean = mean / float(minutes)
            if mean and mean < 1:
                mean = '1'
            else:
                mean = '{:.0f}'.format(mean)
                
            rate = rate / float(minutes)
            if rate and rate < 0.01:
                rate = '<0.01'
            else:
                rate = '{:.2f}'.format(rate)
            
            self.response.payload.usage = usage
            self.response.payload.min = min_
            self.response.payload.max = max_
            self.response.payload.mean = mean
            self.response.payload.rate = rate
            self.response.payload.trend_mean = ','.join(trend_mean)
            self.response.payload.trend_rate = ','.join(trend_rate)

'''
from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from collections import OrderedDict
from copy import deepcopy
from cStringIO import StringIO
from datetime import datetime, timedelta
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from dateutil.rrule import MINUTELY, DAILY, rrule, WEEKLY
from heapq import nlargest
from operator import itemgetter
from itertools import izip, tee
from sys import maxint

# Bunch
from bunch import Bunch

# SciPy
from scipy import stats as sp_stats

# redis
from redis import StrictRedis

# Zato
from zato.common import KVDB

conn = StrictRedis()

class StatsElem(object):
    """ A single element of a statistics query result. All values make sense
    only within the time interval of the original query, e.g. a 'min_resp_time'
    may be 18 ms in this element because it represents statistics regarding, say,
    the last hour yet in a different period the 'min_resp_time' may be a completely
    different value. Likewise, 'all' in the description of parameters below means
    'all that matched given query criteria' rather than 'all that ever existed'.
    
    service_name - name of the service this element describes
    usage - how many times the service has been invoked
    avg_mean - an arithmetical average of all the mean response times  (in ms)
    rate - usage rate in requests/s (up to 1 decimal point)
    usage_trend - a CSV list of values representing the service usage 
    mean_trend - a CSV list of values representing mean response times (in ms)
    min_resp_time - minimum service response time (in ms)
    max_resp_time - maximum service response time (in ms)
    all_services_usage - how many times all the services have been invoked
    mean_all_services - an arithmetical average of all the mean response times  of all services (in ms)
    usage_perc_all_services - this service's usage as a percentage of all_services_usage (up to 2 decimal points)
    expected_time_elems - an OrderedDict of all the time slots mapped to a mean time and rate 
    """
    def __init__(self, service_name=None):
        self.service_name = service_name
        self.usage = 0
        self.avg_mean = 0
        self.rate = 0.0
        self.usage_trend = []
        self.mean_trend = []
        self.min_resp_time = maxint # Hoping there will be at least response timer lower than that, if any! :-)
        self.max_resp_time = 0
        self.all_services_usage = 0
        self.mean_all_services = 0
        self.usage_perc_all_services = 0
        self.expected_time_elems = OrderedDict()
        
    def __repr__(self):
        buff = StringIO()
        buff.write('<{} at {} '.format(self.__class__.__name__, hex(id(self))))
        
        attrs = (attr for attr in dir(self) if not attr.startswith('__'))
        attrs = ('{}=[{}]'.format(attr, getattr(self, attr)) for attr in attrs)
        buff.write(', '.join(attrs))
        
        buff.write('>')
        
        value = buff.getvalue()
        buff.close()
        
        return value
    
def get_stats(start, stop, service='*', n=None):
    """ Returns statistics for a given interval, as defined by 'start' and 'stop'.
    service default to '*' for all services in that period and may be set to return
    a one-element list of information regarding that particular service. Setting 'n' 
    to a positive integer will make it return only top n services.
    """
    
    stats_elems = {}
    all_services_usage = 0

    # All mean values
    mean_all_services_list = []
    
    # A mean value of all the mean value
    mean_all_services = 0

    start = parse(start)
    stop = parse(stop)
    
    delta_seconds = (stop - start).seconds
    
    time_elems = [elem.strftime('%Y:%m:%d:%H:%M') for elem in rrule(MINUTELY, dtstart=start, until=stop)]
    
    # We make several passes. First two passes are over Redis keys, one gathers the services, if any at all,
    # and another one actually collects statistics for each service found. Next pass computes trends
    # for mean response time and service usage. Another one computes each of the service's
    # average rate and updates other attributes basing on values collected in the previous step.
    
    # 1st pass
    for suffix in time_elems:
        keys = conn.keys('{}{}:{}'.format(KVDB.SERVICE_TIME_AGGREGATED_BY_MINUTE, service, suffix))
        for key in keys:
            service_name = key.replace(KVDB.SERVICE_TIME_AGGREGATED_BY_MINUTE, '').replace(':{}'.format(suffix), '')
        
            stats_elem = StatsElem(service_name)
            stats_elems[service_name] = stats_elem
            
            # When building trends, we can't expect there will be data for all the time
            # elems built above so to guard against it, this is a dictionary whose keys are the
            # said elems and values are mean/usage for each elem. The values will remain
            # 0/0.0 if there is no data for the time elem, which may mean that in this
            # particular time slice the service wasn't invoked at all.
            stats_elem.expected_time_elems = OrderedDict((elem, Bunch({'mean':0, 'usage':0.0})) for elem in time_elems)
            
    # 2nd pass
    for service, stats_elem in stats_elems.items():
        for suffix in time_elems:
            key = '{}{}:{}'.format(KVDB.SERVICE_TIME_AGGREGATED_BY_MINUTE, service, suffix)
            
            # We can convert all the values to floats here to ease with computing
            # all the stuff and convert them still to integers later on, when necessary.
            key_values = Bunch(((name, float(value)) for (name, value) in conn.hgetall(key).items()))
        
            if key_values:
                
                all_services_usage += key_values.usage
                mean_all_services_list.append(key_values.mean)
                
                stats_elem.usage += key_values.usage
                
                stats_elem.min_resp_time = min(stats_elem.min_resp_time, key_values.min)
                stats_elem.max_resp_time = max(stats_elem.max_resp_time, key_values.max)
                
                for attr in('mean', 'usage'):
                    stats_elem.expected_time_elems[suffix][attr] = key_values[attr]
                    
    mean_all_services = '{:.0f}'.format(sp_stats.tmean(mean_all_services_list)) if mean_all_services_list else 0
                    
    # 3rd pass
    for stats_elem in stats_elems.values():
        values = stats_elem.expected_time_elems.values()
        stats_elem.mean_trend = ','.join(['{:.0f}'.format(elem.mean) for elem in values])
        
        usage_trend = [int(elem.usage) for elem in values]
        stats_elem.rate = '{:.1f}'.format(sum(usage_trend) / delta_seconds)
        stats_elem.usage_trend = ','.join(str(elem) for elem in usage_trend)
            
        stats_elem.mean_all_services = mean_all_services
        stats_elem.all_services_usage = all_services_usage
        
        # Don't divide by 0
        if all_services_usage:
            stats_elem.usage_perc_all_services = '{:.2f}'.format(100.0 * stats_elem.usage / all_services_usage)
        
    return stats_elems
        
start = '2012-07-14T20:00:54.442517'
stop = '2012-07-14T21:00:54.442517'           
            
stats_elems = get_stats(start, stop, '*')

for stats_elem in stats_elems.values():
    print()
    print(stats_elem)
    '''

class Delete(AdminService):
    """ Deletes aggregated statistics from a given interval.
    """
    class SimpleIO:
        input_required = ('start', 'stop')

    def handle(self):
        self.broker_client.send_json({'action':STATS.DELETE, 'start':self.request.input.start, 'stop':self.request.input.stop}, 
                                     MESSAGE_TYPE.TO_PARALLEL_PULL)
