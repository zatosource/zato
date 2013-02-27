# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at gefira.pl>

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
from unittest import TestCase
from uuid import uuid4

# Nose
from nose.tools import eq_

# Zato
from zato.common import StatsElem

class StatsElemTestCase(TestCase):
    def test_from_json(self):
        item = {'usage_perc_all_services': 1.22, 'all_services_time': 4360, 
         'time_perc_all_services': 17.64, 
         'mean_trend': '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,769,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', 
         'min_resp_time': 769.0, 'service_name': 'zato.stats.summary.create-summary-by-year', 
         'max_resp_time': 769.0, 'rate': 0.0, 'mean_all_services': '63', 
         'all_services_usage': 82, 'time': 769.0, 'usage': 1, 
         'usage_trend': '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', 
         'mean': 12.61}
        
        stats_elem = StatsElem.from_json(item)
        
        for k, v in item.items():
            value = getattr(stats_elem, k)
            eq_(v, value)
