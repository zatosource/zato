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
from zato.common.test import rand_int, rand_string, rand_bool, ServiceTestCase
from zato.server.service import Boolean, Integer
from zato.server.service.internal.security import GetList

##############################################################################

class GetListTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = GetList
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return {'cluste_id':rand_int()}
    
    def get_response_data(self):
        return Bunch({'id':rand_int(), 'name':rand_string, 'is_active':rand_bool(), 'sec_type':rand_string(), 'username':rand_string(),
                      'realm':rand_string(), 'password_type':rand_string(), 'reject_empty_nonce_creat':rand_bool(),
                      'reject_stale_tokens':rand_bool(),'reject_expiry_limit':rand_int(), 'nonce_freshness_time':rand_int()})
    
    def test_sio(self):
        
        self.assertEquals(self.sio.request_elem, 'zato_security_get_list_request')
        self.assertEquals(self.sio.response_elem, 'zato_security_get_list_response')
        self.assertEquals(self.sio.input_required, ('cluster_id',))
        self.assertEquals(self.sio.output_required, ('id', 'name', 'is_active', 'sec_type'))
        self.assertEquals(self.sio.output_optional, ('username', 'realm', 'password_type', self.wrap_force_type(Boolean('reject_empty_nonce_creat')),
                                                     self.wrap_force_type(Boolean('reject_stale_tokens')),
                                                     self.wrap_force_type(Integer('reject_expiry_limit')),
                                                     self.wrap_force_type(Integer('nonce_freshness_time'))))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.security.get-list')