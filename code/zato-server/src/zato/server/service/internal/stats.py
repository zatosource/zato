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

# Zato
from zato.common import KVDB
from zato.server.service.internal import AdminService

class ProcessRawTimers(AdminService):
    def handle(self):
        config = Bunch()
        for item in self.request.payload.splitlines():
            key, value = item.split('=')
            config[key] = int(value)

        for item in self.server.kvdb.conn.keys(KVDB.SERVICE_TIMER_RAW + '*'):
            service_name = item.replace(KVDB.SERVICE_TIMER_RAW, '')
            print(333, service_name)
            
            #mean_percentile = 