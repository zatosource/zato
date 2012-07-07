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

# Bunch
from bunch import Bunch

# SciPy
from scipy import stats as sp_stats

# Zato
from zato.common import KVDB
from zato.server.service.internal import AdminService

class ProcessRawTimers(AdminService):
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

        for item in self.server.kvdb.conn.keys(KVDB.SERVICE_TIMER_RAW + '*'):
            
            service_name = item.replace(KVDB.SERVICE_TIMER_RAW, '')
            
            current_mean = float(self.server.kvdb.conn.hget(KVDB.SERVICE_TIMER_BASIC + service_name, 'mean_all_time') or 0)
            current_min = float(self.server.kvdb.conn.hget(KVDB.SERVICE_TIMER_BASIC + service_name, 'min_all_time') or 0)
            current_max = float(self.server.kvdb.conn.hget(KVDB.SERVICE_TIMER_BASIC + service_name, 'max_all_time') or 0)
            
            item_len = self.server.kvdb.conn.llen(item)
            batch_size = min(item_len, config.max_batch_size)
            if batch_size < item_len:
                msg = ('batch_size:[{}] < item_len:[{}], max_batch_size:[{}], item:[{}], '
                'consider decreasing the job interval or increasing the max_batch_size').format(
                    batch_size, item_len, config.max_batch_size, item)
                self.logger.warn(msg)
            
            timers = [int(elem) for elem in self.server.kvdb.conn.lrange(item, 0, batch_size)]
            
            mean_percentile = int(self.server.kvdb.conn.hget(KVDB.SERVICE_TIMER_BASIC + service_name, 'mean_percentile') or 0)
            max_score = int(sp_stats.scoreatpercentile(timers, mean_percentile))

            # The new mean is a mean of the last batch of timers and of the current mean
            batch_mean = sp_stats.tmean(timers, (None, max_score)) or 0
            self.server.kvdb.conn.hset(KVDB.SERVICE_TIMER_BASIC + service_name, 'mean_all_time', sp_stats.tmean((batch_mean, current_mean)))
            
            self.server.kvdb.conn.hset(KVDB.SERVICE_TIMER_BASIC + service_name, 'min_all_time', min(current_min, min(timers)))
            self.server.kvdb.conn.hset(KVDB.SERVICE_TIMER_BASIC + service_name, 'max_all_time', max(current_max, max(timers)))
            
            # Services use RPUSH for storing raw timers so we are safe to use LTRIM
            # in order to do away with the already processed ones
            self.server.kvdb.conn.ltrim(item, batch_size, -1)
