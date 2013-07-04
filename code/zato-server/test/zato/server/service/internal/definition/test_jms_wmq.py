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
from zato.common.test import rand_bool, rand_int, rand_string, ServiceTestCase
from zato.server.service import Boolean, Integer
from zato.server.service.internal.definition.jms_wmq import Create, GetByID, Edit, Delete, GetList

################################################################################

class GetListTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = GetList
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return {'cluster_id': rand_int()}
    
    def get_response_data(self):
        return Bunch(
            {'id':rand_int(), 'name':self.name, 'host':rand_string(), 'port':rand_int(),
             'queue_manager':rand_int(), 'channel':rand_string(),
             'cache_open_send_queues':rand_bool(), 'cache_open_receive_queues':rand_bool(),
             'use_shared_connections':rand_bool(), 'ssl':rand_bool(),
             'needs_mcd':rand_bool(), 'max_chars_printed':rand_int(),
             'ssl_cipher_spec':rand_string(), 'ssl_key_repository':rand_string()}
        )
    
    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_definition_jms_wmq_get_list_request')
        self.assertEquals(self.sio.response_elem, 'zato_definition_jms_wmq_get_list_response')
        self.assertEquals(self.sio.input_required, ('cluster_id',))
        self.assertEquals(self.sio.output_required, ('id', 'name', 'host', 'port', 'queue_manager', 'channel', 
                                                     self.wrap_force_type(Boolean('cache_open_send_queues')),
                                                     self.wrap_force_type(Boolean('cache_open_receive_queues')),
                                                     self.wrap_force_type(Boolean('use_shared_connections')),
                                                     self.wrap_force_type(Boolean('ssl')), 'needs_mcd',
                                                     self.wrap_force_type(Integer('max_chars_printed'))))
        self.assertEquals(self.sio.output_optional,('ssl_cipher_spec', 'ssl_key_repository'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.definition.jms-wmq.get-list')
        
##############################################################################

class GetByIDTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = GetByID
        self.sio = self.service_class.SimpleIO      
    
    def get_request_data(self):
        return {'id':rand_int(), 'cluster_id':rand_int()}
    
    def get_response_data(self):
        return Bunch({'id':rand_int(), 'name':self.name, 'host':rand_string(), 'port':rand_int(),
             'queue_manager':rand_int(), 'channel':rand_string(),
             'cache_open_send_queues':rand_bool(), 'cache_open_receive_queues':rand_bool(),
             'use_shared_connections':rand_bool(), 'ssl':rand_bool(),
             'needs_mcd':rand_bool(), 'max_chars_printed':rand_int(),
             'ssl_cipher_spec':rand_string(), 'ssl_key_repository':rand_string()})
    
    def test_sio(self):
        
        self.assertEquals(self.sio.request_elem, 'zato_definition_jms_wmq_get_by_id_request')
        self.assertEquals(self.sio.response_elem, 'zato_definition_jms_wmq_get_by_id_response')
        self.assertEquals(self.sio.input_required,('id', 'cluster_id'))
        self.assertEquals(self.sio.output_required, ('id', 'name', 'host', 'port', 'queue_manager', 'channel',
                                                     self.wrap_force_type(Boolean('cache_open_send_queues')),
                                                     self.wrap_force_type(Boolean('cache_open_receive_queues')),
                                                     self.wrap_force_type(Boolean('use_shared_connections')),
                                                     self.wrap_force_type(Boolean('ssl')), 'needs_mcd',
                                                     self.wrap_force_type(Integer('max_chars_printed'))))
        self.assertEquals(self.sio.output_optional,('ssl_cipher_spec', 'ssl_key_repository'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
        def test_impl(self):
            self.assertEquals(self.service_class.get_name(), 'zato.definition.jms-wmq.get-by-id')
       
###############################################################################
class CreateTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Create
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return ({'cluster_id':rand_int(), 'name':self.name, 'host':rand_string(),
                 'port':rand_int(), 'queue_manager':rand_string(), 'channel':rand_string(),
                 'cache_open_send_queues':rand_bool(), 'cache_open_receive_queues':rand_bool(),
                 'use_shared_connections':rand_bool(), 'ssl':rand_bool(), 'needs_mcd':rand_bool(),
                 'max_chars_printed':rand_int(), 'ssl_cipher_spec':rand_string(), 'ssl_key_repository':rand_string()})
        
    def get_response_data(self):
        return Bunch({'id':rand_int(), 'name':rand_string()})        
    
    def test_sio(self):
        
        self.assertEquals(self.sio.request_elem, 'zato_definition_jms_wmq_create_request')
        self.assertEquals(self.sio.response_elem, 'zato_definition_jms_wmq_create_response')
        self.assertEquals(self.sio.input_required, ('cluster_id', 'name', 'host', 'port', 'queue_manager', 'channel',
                                                    self.wrap_force_type(Boolean('cache_open_send_queues')),
                                                    self.wrap_force_type(Boolean('cache_open_receive_queues')),
                                                    self.wrap_force_type(Boolean('use_shared_connections')),
                                                    self.wrap_force_type(Boolean('ssl')), 'needs_mcd',
                                                    self.wrap_force_type(Integer('max_chars_printed'))))
        self.assertEquals(self.sio.input_optional, ('ssl_cipher_spec', 'ssl_key_repository'))
        self.assertEquals(self.sio.output_required, ('id', 'name'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.definition.jms-wmq.create')

############################################################################### 
           
class EditTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Edit
        self.sio = self.service_class.SimpleIO
    
    def get_response_data(self):
            return ({'id':rand_int(), 'cluster_id':rand_int(), 'name':self.name, 'host':rand_string(),
                          'port':rand_int(), 'queue_manager':rand_string(), 'channel':rand_string(),
                          'cache_open_send_queues':rand_bool(), 'cache_open_receive_queues':rand_bool(),
                          'use_shared_connections':rand_bool(), 'ssl':rand_bool(), 'needs_mcd':rand_bool(),
                          'max_chars_printed':rand_int()})
        
    def get_request_data(self):
            return Bunch({'id':rand_int(), 'name':rand_string()})        
    
    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_definition_jms_wmq_edit_request')
        self.assertEquals(self.sio.response_elem, 'zato_definition_jms_wmq_edit_response')
        self.assertEquals(self.sio.input_required, ('id', 'cluster_id', 'name', 'host', 'port', 'queue_manager', 'channel',
                                                    self.wrap_force_type(Boolean('cache_open_send_queues')),
                                                    self.wrap_force_type(Boolean('cache_open_receive_queues')),
                                                    self.wrap_force_type(Boolean('use_shared_connections')),
                                                    self.wrap_force_type(Boolean('ssl')), 'needs_mcd',
                                                    self.wrap_force_type(Integer('max_chars_printed'))))
        self.assertEquals(self.sio.output_required, ('id', 'name'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.definition.jms-wmq.edit')

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
        self.assertEquals(self.sio.request_elem, 'zato_definition_jms_wmq_delete_request')
        self.assertEquals(self.sio.response_elem, 'zato_definition_jms_wmq_delete_response')
        self.assertEquals(self.sio.input_required, ('id',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.definition.jms-wmq.delete')
