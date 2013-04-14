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

# Bunch
from bunch import Bunch

# Zato
from zato.common import zato_namespace
from zato.common.test import rand_bool, rand_int, rand_string, ServiceTestCase
from zato.server.service import Boolean, Integer, UTC
from zato.server.service.internal.stats import Delete, StatsReturningService, GetByService

################################################################################

class DeleteTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Delete
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return {'start':rand_string(), 'stop':rand_string()}
    
    def get_response_data(self):
        return Bunch({}
        )
    
    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_stats_delete_request')
        self.assertEquals(self.sio.response_elem, 'zato_stats_delete_response')
        self.assertEquals(self.sio.input_required, (self.wrap_force_type(UTC('start')), self.wrap_force_type(UTC('stop'))))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.stats.delete')
   
###############################################################################

class StatsReturningServiceTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = StatsReturningService
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return ({'start':rand_string(), 'stop':rand_string(), 'service_name':rand_string(), 'n':rand_int(), 'n_type':tand_string()}
                )
        
    def get_response_data(self):
        return Bunch({'service_name':rand_string(), 'usage':rand_long(), 'mean':rand_float(), 'rate':rand_float(), 'time':rand_double(),
                      'usage_trend':rand_string(), 'mean_trend':rand_string(), 'min_resp_time':rand_float(), 'max_resp_time':rand_float(),
                      'all_services_usage':rand_string(), 'all_services_time':rand_string(), 'mean_all_services':rand_string(),
                      'usage_perc_all_services':rand_string(), 'time_perc_all_services':rand_string()})        
    
    
    def test_sio(self):        
        self.assertEquals(self.sio.input_required, (self.wrap_force_type(UTC('start')), self.wrap_force_type(UTC('stop'))))
        self.assertEquals(self.sio.input_optional, ('service_name', self.wrap_force_type(Integer('n')), 'n_type'))
        self.assertEquals(self.sio.output_optional, ('service_name', 'usage', 'mean', 'rate', 'time', 'usage_trend', 'mean_trend',
                                                     'min_resp_time', 'max_resp_time', 'all_services_usage', 'all_services_time',
                                                     'mean_all_services', 'usage_perc_all_services', 'time_perc_all_services'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.stats.stats-returning-service')
        
###############################################################################

class GetByServiceTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = GetByService
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return ({'service_name':rand_string(), 'usage':rand_long(), 'mean':rand_float(), 'rate':rand_float(), 'time':rand_double(),
                 'usage_trend':rand_string(), 'mean_trend':rand_string(), 'min_resp_time':rand_float(), 'max_resp_time':rand_float(),
                 'service_id':rand_int()}
                )
        
    def get_response_data(self):
        return Bunch({'service_name':rand_string(), 'usage':rand_string(), 'mean':rand_string(), 'rate':rand_string(), 'time':rand_string(),
                       'usage_trend':rand_string(), 'mean_trend':rand_string(), 'min_resp_time':rand_string(), 'max_resp_time':rand_string()}
                      )          
    
    
    def test_sio(self):        
        self.assertEquals(self.sio.request_elem, 'zato_stats_get_by_service_request')
        self.assertEquals(self.sio.response_elem, 'zato_stats_get_by_service_response')
        self.assertEquals(self.sio.input_required, (self.wrap_force_type(UTC('start')), self.wrap_force_type(UTC('stop')), 'service_id'))
        self.assertEquals(self.sio.output_optional, ('service_name', 'usage', 'mean', 'rate', 'time', 'usage_trend', 'mean_trend',
                                                     'min_resp_time', 'max_resp_time',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.stats.get-by-service')