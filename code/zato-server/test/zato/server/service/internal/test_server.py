# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Bunch
from bunch import Bunch

# Zato
from zato.common import zato_namespace
from zato.common.test import rand_int, rand_string, ServiceTestCase
from zato.server.service.internal.server import Edit, Delete, GetByID

################################################################################

class EditestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Edit
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return ({'id':rand_int(), 'name':rand_string()}
                )
        
    def get_response_data(self):
        return Bunch({'id':rand_int(), 'cluste_id':rand_int(), 'name':rand_string(), 'host':rand_string(),
                      'bind_host':rand_string(), 'bind_port':rand_string(), 'last_join_status':rand_string(),
                      'last_join_mod_status':rand_string(), 'up_status':rand_string(), 'up_mod_date':rand_string()})        
    
    def test_sio(self):
        
        self.assertEquals(self.sio.request_elem, 'zato_server_edit_request')
        self.assertEquals(self.sio.response_elem, 'zato_server_edit_response')
        self.assertEquals(self.sio.input_required, ('id', 'name'))
        self.assertEquals(self.sio.output_required, ('id', 'cluster_id', 'name', 'host'))
        self.assertEquals(self.sio.output_optional, ('bind_host', 'bind_port', 'last_join_status',
                                                     'last_join_mod_date', 'last_join_mod_by', 'up_status', 'up_mod_date'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.server.edit')
        
###############################################################################

class GetByIDTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = GetByID
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return ({'id':rand_int()}
                )
        
    def get_response_data(self):
        return Bunch({'id':rand_int(), 'cluste_id':rand_int(), 'name':rand_string(), 'host':rand_string(),
                      'bind_host':rand_string(), 'bind_port':rand_string(), 'last_join_status':rand_string(),
                      'last_join_mod_status':rand_string(), 'up_status':rand_string(), 'up_mod_date':rand_string()})          
    
    def test_sio(self):
        
        self.assertEquals(self.sio.request_elem, 'zato_server_get_by_id_request')
        self.assertEquals(self.sio.response_elem, 'zato_server_get_by_id_response')
        self.assertEquals(self.sio.input_required, ('id',))
        self.assertEquals(self.sio.output_required, ('id', 'cluster_id', 'name', 'host'))
        self.assertEquals(self.sio.output_optional, ('bind_host', 'bind_port', 'last_join_status',
                                                     'last_join_mod_date', 'last_join_mod_by', 'up_status', 'up_mod_date'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.server.get-by-id')

##############################################################################

class DeleteTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Delete
        self.sio = self.service_class.SimpleIO
  
    def get_request_data(self):
        return {'id': rand_int()}
    
    def get_response_data(self):
        return Bunch()
    
    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_server_delete_request')
        self.assertEquals(self.sio.response_elem, 'zato_server_delete_response')
        self.assertEquals(self.sio.input_required, ('id',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.server.delete')
