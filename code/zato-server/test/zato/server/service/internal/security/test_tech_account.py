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
from zato.server.service.internal.security.tech_account import GetList, GetByID, Create, Edit, ChangePassword, Delete

################################################################################

class GetListTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = GetList
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return {'cluster_id': rand_int()}
    
    def get_response_data(self):
        return Bunch({'id':rand_int(), 'name':self.name, 'is_active':rand_bool()}
        )
    
    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_security_tech_account_get_list_request')
        self.assertEquals(self.sio.response_elem, 'zato_security_tech_account_get_list_response')
        self.assertEquals(self.sio.input_required, ('cluster_id',))
        self.assertEquals(self.sio.output_required, ('id', 'name', 'is_active'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.security.tech-account.get-list')
        
##############################################################################

class GetByIDTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = GetByID
        self.sio = self.service_class.SimpleIO      
    
    def get_request_data(self):
        return {'id':rand_int()}
    
    def get_response_data(self):
        return Bunch({'id':rand_int(), 'name':self.name, 'is_active':rand_bool()})
    
    def test_sio(self):        
        self.assertEquals(self.sio.request_elem, 'zato_security_tech_account_get_by_id_request')
        self.assertEquals(self.sio.response_elem, 'zato_security_tech_account_get_by_id_response')
        self.assertEquals(self.sio.input_required,('id',))
        self.assertEquals(self.sio.output_required, ('id', 'name', 'is_active'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
        def test_impl(self):
            self.assertEquals(self.service_class.get_name(), 'zato.security.tech-account.get-by-id')
       
###############################################################################
class CreateTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Create
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return ({'cluster_id':rand_int(), 'name':rand_string(), 'is_active':rand_bool()})
        
    def get_response_data(self):
        return Bunch({'id':rand_int(), 'name':rand_string()})        
    
    def test_sio(self):
        
        self.assertEquals(self.sio.request_elem, 'zato_security_tech_account_create_request')
        self.assertEquals(self.sio.response_elem, 'zato_security_tech_account_create_response')
        self.assertEquals(self.sio.input_required, ('cluster_id', 'name', 'is_active'))
        self.assertEquals(self.sio.output_required, ('id', 'name'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.security.tech-account.create')
        
###############################################################################

class EditTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Edit
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return ({'id':rand_int(), 'cluster_id':rand_int(), 'name':rand_string(), 'is_active':rand_bool()})
        
    def get_response_data(self):
        return Bunch({'id':rand_int(), 'name':rand_string()})        
    
    def test_sio(self):        
        self.assertEquals(self.sio.request_elem, 'zato_security_tech_account_edit_request')
        self.assertEquals(self.sio.response_elem, 'zato_security_tech_account_edit_response')
        self.assertEquals(self.sio.input_required, ('id', 'cluster_id', 'name', 'is_active'))
        self.assertEquals(self.sio.output_required, ('id', 'name'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.security.tech-account.edit')
        
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
        self.assertEquals(self.sio.request_elem, 'zato_security_tech_account_change_password_request')
        self.assertEquals(self.sio.response_elem, 'zato_security_tech_account_change_password_response')
        self.assertEquals(self.sio.input_required, ('id', 'password1', 'password2'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.security.tech-account.change-password')

##############################################################################

class DeleteTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Delete
        self.sio = self.service_class.SimpleIO
  
    def get_request_data(self):
        return {'id': rand_int(), 'current_tech_account_name':rand_string()}
    
    def get_response_data(self):
        return Bunch()
    
    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_security_tech_account_delete_request')
        self.assertEquals(self.sio.response_elem, 'zato_security_tech_account_delete_response')
        self.assertEquals(self.sio.input_required, ('id',))
        self.assertEquals(self.sio.input_optional, ('current_tech_account_name',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.security.tech-account.delete')
