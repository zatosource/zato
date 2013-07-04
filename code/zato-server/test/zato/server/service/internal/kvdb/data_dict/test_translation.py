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
#from zato.server.service import Boolean, Integer
from zato.server.service.internal.kvdb.data_dict.translation import GetList, Create, Edit, Delete, Translate, GetLastID

################################################################################

class GetListTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = GetList
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return {}
    
    def get_response_data(self):
        return Bunch({'id':rand_int(), 'system1':rand_string(), 'key1':rand_string(), 'value1':rand_string,
                      'system2':rand_string(), 'key2':rand_string(), 'value2':rand_string,
                      'id1':rand_int(), 'id2':rand_int()})
    
    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_kvdb_data_dict_translation_get_list_request')
        self.assertEquals(self.sio.response_elem, 'zato_kvdb_data_dict_translation_get_list_response')
        self.assertEquals(self.sio.output_required, ('id', 'system1', 'key1', 'value1', 'system2', 'key2', 'value2', 'id1', 'id2'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_required')    
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.kvdb.data-dict.translation.get-list')
       
##############################################################################

class CreateTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Create
        self.sio = self.service_class.SimpleIO
        
        def get_request_data(self):
            return {'system1':rand_string(), 'key1':rand_string(), 'value1':rand_string(),
                    'system2':rand_string(), 'key2':rand_string(), 'value2':rand_string()}
           
        def get_response_data(self):
            return Bunch({'id':rand_int()})    
    
    def test_sio(self):
        
        self.assertEquals(self.sio.request_elem, 'zato_kvdb_data_dict_translation_create_request')
        self.assertEquals(self.sio.response_elem, 'zato_kvdb_data_dict_translation_create_response')
        self.assertEquals(self.sio.input_required, ('system1', 'key1', 'value1', 'system2', 'key2', 'value2'))
        self.assertEquals(self.sio.output_required, ('id',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')        

    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.kvdb.data-dict.translation.create')

############################################################################### 
          
class EditTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Edit
        self.sio = self.service_class.SimpleIO
        
        def get_request_data(self):
            return {'id':rand_int(), 'system1':rand_string(), 'key1':rand_string(), 'value1':rand_string(),
                    'system2':rand_string(),'key2':rand_string(), 'value2':rand_string()}
                   
        def get_response_data(self):
            return Bunch({'id':rand_int()})        
    
    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_kvdb_data_dict_translation_edit_request')
        self.assertEquals(self.sio.response_elem, 'zato_kvdb_data_dict_translation_edit_response')
        self.assertEquals(self.sio.input_required, ('id', 'system1', 'key1', 'value1', 'system2', 'key2', 'value2'))
        self.assertEquals(self.sio.output_required, ('id',))        
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')        

    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.kvdb.data-dict.translation.edit')

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
        self.assertEquals(self.sio.request_elem, 'zato_kvdb_data_dict_translation_delete_request')
        self.assertEquals(self.sio.response_elem, 'zato_kvdb_data_dict_translation_delete_response')
        self.assertEquals(self.sio.input_required, ('id',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.kvdb.data-dict.translation.delete')
        
##############################################################################

class TranslateTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Translate
        self.sio = self.service_class.SimpleIO
        
        def get_request_data(self):
            return {'system1':rand_string(), 'key1':rand_string(), 'value1':rand_string(), 'system2':rand_string(), 'key2':rand_string()}
            
        def get_response_data(self):
            return Bunch({'value2':rand_string(), 'repr':rand_string(), 'hex':rand_string(), 'sha1':rand_string(), 'sha256':rand_string()})        
    
    def test_sio(self):
        
        self.assertEquals(self.sio.request_elem, 'zato_kvdb_data_dict_translation_translate_request')
        self.assertEquals(self.sio.response_elem, 'zato_kvdb_data_dict_translation_translate_response')
        self.assertEquals(self.sio.input_required, ('system1', 'key1', 'value1', 'system2', 'key2'))
        self.assertEquals(self.sio.output_optional, ('value2', 'repr', 'hex', 'sha1', 'sha256'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')  
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')        
        self.assertEquals(self.sio.namespace, zato_namespace)
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.kvdb.data-dict.translation.translate')

############################################################################### 
        
class GetLastIDCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = GetLastID
        self.sio = self.service_class.SimpleIO
  
    def get_request_data(self):
        return {}
    
    def get_response_data(self):
        return Bunch({'value':rand_int()})
    
    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_kvdb_data_dict_translation_get_last_id_request')
        self.assertEquals(self.sio.response_elem, 'zato_kvdb_data_dict_translation_get_last_id_response')
        self.assertEquals(self.sio.output_optional, ('value',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.kvdb.data-dict.translation.get-last-id')
