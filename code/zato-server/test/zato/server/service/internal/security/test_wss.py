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
from zato.server.service.internal.security.wss import GetList, Create, Edit, ChangePassword, Delete

################################################################################

class GetListTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = GetList
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return {'cluster_id': rand_int()}
    
    def get_response_data(self):
        return Bunch({'id':rand_int(), 'name':self.name, 'is_active':rand_bool(), 'password_type':rand_string(), 'username':rand_string(),
                      'reject_empty_nonce_creat':rand_bool(), 'reject_stale_tokens':rand_bool(), 'reject_expiry_limit':rand_int(),
                      'nonce_freshness_time':rand_int()}
        )
    
    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_security_wss_get_list_request')
        self.assertEquals(self.sio.response_elem, 'zato_security_wss_get_list_response')
        self.assertEquals(self.sio.input_required, ('cluster_id',))
        self.assertEquals(self.sio.output_required, ('id', 'name', 'is_active', 'password_type', 'username',
                                                     self.wrap_force_type(Boolean('reject_empty_nonce_creat')),
                                                     self.wrap_force_type(Boolean('reject_stale_tokens')),
                                                     self.wrap_force_type(Integer('reject_expiry_limit')),
                                                     self.wrap_force_type(Integer('nonce_freshness_time'))))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.security.wss.get-list')
   
###############################################################################

class CreateTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Create
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return ({'cluster_id':rand_int(), 'name':rand_string(), 'is_active':rand_bool(), 'username':rand_string(),
                 'password_type':rand_string(), 'reject_empty_nonce_creat':rand_bool(), 'reject_stale_tokens':rand_bool(), 'reject_expiry_limit':rand_int(),
                      'nonce_freshness_time':rand_int()}
                )
        
    def get_response_data(self):
        return Bunch({'id':rand_int(), 'name':rand_string()})        
        
    def test_sio(self):
        
        self.assertEquals(self.sio.request_elem, 'zato_security_wss_create_request')
        self.assertEquals(self.sio.response_elem, 'zato_security_wss_create_response')
        self.assertEquals(self.sio.input_required, ('cluster_id', 'name', 'is_active', 'username', 'password_type',
                                                     self.wrap_force_type(Boolean('reject_empty_nonce_creat')),
                                                     self.wrap_force_type(Boolean('reject_stale_tokens')),
                                                     self.wrap_force_type(Integer('reject_expiry_limit')),
                                                     self.wrap_force_type(Integer('nonce_freshness_time'))))
        self.assertEquals(self.sio.output_required, ('id', 'name'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.security.wss.create')
        
###############################################################################

class EditTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Edit
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return ({'id':rand_int(), 'cluster_id':rand_int(), 'name':rand_string(), 'is_active':rand_bool(), 'username':rand_string(),
                 'password_type':rand_string(), 'reject_empty_nonce_creat':rand_bool(), 'reject_stale_tokens':rand_bool(), 'reject_expiry_limit':rand_int(),
                 'nonce_freshness_time':rand_int()}
                )
        
    def get_response_data(self):
        return Bunch({'id':rand_int(), 'name':rand_string()})        
    
    def test_sio(self):        
        self.assertEquals(self.sio.request_elem, 'zato_security_wss_edit_request')
        self.assertEquals(self.sio.response_elem, 'zato_security_wss_edit_response')
        self.assertEquals(self.sio.input_required, ('id', 'cluster_id', 'name', 'is_active', 'username', 'password_type',
                                                     self.wrap_force_type(Boolean('reject_empty_nonce_creat')),
                                                     self.wrap_force_type(Boolean('reject_stale_tokens')),
                                                     self.wrap_force_type(Integer('reject_expiry_limit')),
                                                     self.wrap_force_type(Integer('nonce_freshness_time'))))
        self.assertEquals(self.sio.output_required, ('id', 'name'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.security.wss.edit')
        
###############################################################################         

class ChangePasswordTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = ChangePassword
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return {'id':rand_int(), 'password1':rand_string(), 'password2':rand_string()}
    
    def get_response_data(self):
        return Bunch()    
    
    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_security_wss_change_password_request')
        self.assertEquals(self.sio.response_elem, 'zato_security_wss_change_password_response')
        self.assertEquals(self.sio.input_required, ('id', 'password1', 'password2'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.security.wss.change-password')

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
        self.assertEquals(self.sio.request_elem, 'zato_security_wss_delete_request')
        self.assertEquals(self.sio.response_elem, 'zato_security_wss_delete_response')
        self.assertEquals(self.sio.input_required, ('id',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.security.wss.delete')
