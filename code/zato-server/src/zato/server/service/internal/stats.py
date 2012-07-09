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

# Bunch
from bunch import Bunch

# SciPy
from scipy import stats as sp_stats

# Zato
from zato.common import KVDB
from zato.server.service.internal import AdminService

class _AggregatingService(AdminService):
    """ A base class for all services that process raw timers into aggregates values.
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
            
        timers = [int(elem) for elem in self.server.kvdb.conn.lrange(key, 0, batch_size)]
        
        mean_percentile = int(self.server.kvdb.conn.hget(KVDB.SERVICE_TIMER_BASIC + service_name, 'mean_percentile') or 0)
        max_score = int(sp_stats.scoreatpercentile(timers, mean_percentile))
        
        return min(timers), max(timers), (sp_stats.tmean(timers, (None, max_score)) or 0), len(timers)

class ProcessRawTimers(_AggregatingService):
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

        for key in self.server.kvdb.conn.keys(KVDB.SERVICE_TIMER_RAW + '*'):
            
            service_name = key.replace(KVDB.SERVICE_TIMER_RAW, '')
            
            current_mean = float(self.server.kvdb.conn.hget(KVDB.SERVICE_TIMER_BASIC + service_name, 'mean_all_time') or 0)
            current_min = float(self.server.kvdb.conn.hget(KVDB.SERVICE_TIMER_BASIC + service_name, 'min_all_time') or 0)
            current_max = float(self.server.kvdb.conn.hget(KVDB.SERVICE_TIMER_BASIC + service_name, 'max_all_time') or 0)
            
            batch_min, batch_max, batch_mean, batch_total = self._aggregate(key, service_name, config.max_batch_size)
            
            self.server.kvdb.conn.hset(KVDB.SERVICE_TIMER_BASIC + service_name, 'mean_all_time', sp_stats.tmean((batch_mean, current_mean)))
            self.server.kvdb.conn.hset(KVDB.SERVICE_TIMER_BASIC + service_name, 'min_all_time', min(current_min, batch_min))
            self.server.kvdb.conn.hset(KVDB.SERVICE_TIMER_BASIC + service_name, 'max_all_time', max(current_max, batch_max))
            
            # Services use RPUSH for storing raw timers so we are safe to use LTRIM
            # in order to do away with the already processed ones
            self.server.kvdb.conn.ltrim(key, batch_total, -1)

class AggregateByMinute(_AggregatingService):
    """ Aggregates per-miunte timers.
    """
    def handle(self):
        
        # Get all keys from a minute that is sure to have passed, for instance,
        # say it's 13:19 right now (regardless of the seconds part), we'll process everything
        # that happened in 13:17. Hence it's also important that any changes in the minutes
        # to be picked up here below be kept in sync with the EXPIRE command Service._post_handle uses.
        
        now = datetime.utcnow()
        key_suffix = (now - timedelta(minutes=2)).strftime('%Y:%m:%d:%H:%M')
        
        for key in self.server.kvdb.conn.keys('{}*:{}'.format(KVDB.SERVICE_TIMER_RAW_BY_MINUTE, key_suffix)):
            
            service_name = key.replace(KVDB.SERVICE_TIMER_RAW_BY_MINUTE, '').replace(':' + key_suffix, '')
            aggr_key = '{}{}:{}'.format(KVDB.SERVICE_TIMER_AGGREGATED_BY_MINUTE, service_name, key_suffix)
            
            batch_min, batch_max, batch_mean, batch_total = self._aggregate(key, service_name)
            
            self.server.kvdb.conn.hset(aggr_key, 'min', batch_min)
            self.server.kvdb.conn.hset(aggr_key, 'max', batch_max)
            self.server.kvdb.conn.hset(aggr_key, 'mean', batch_mean)
            self.server.kvdb.conn.hset(aggr_key, 'total', batch_total)
            self.server.kvdb.conn.hset(aggr_key, 'rate', batch_total / 60.0) # I.e. req/s
            
            # Per-minute statistic keys will expire by themselves, we don't need
            # to delete them manually.
