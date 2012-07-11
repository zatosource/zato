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
from datetime import datetime, timedelta
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
from zato.common import KVDB, ZatoException
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
    """ Returns top N slowest and most commonly used services for a given period.
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

