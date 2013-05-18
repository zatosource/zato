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
from zato.common.test import rand_int, rand_string, rand_bool, ServiceTestCase
from zato.server.service import Boolean, Integer
from zato.server.service.internal import Ping, Ping2, ChangePasswordBase

##############################################################################

class PingTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Ping
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return {'pong':rand_string()}
    
    def get_response_data(self):
        return Bunch({})
    
    def test_sio(self):
        
        self.assertEquals(self.sio.response_elem, 'zato_ping_response')
        self.assertEquals(self.sio.output_required, ('pong',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.ping')
        
###################################################################################

class Ping2TestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Ping2
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return {'pong':rand_string()}
    
    def get_response_data(self):
        return Bunch({})
    
    def test_sio(self):
        
        self.assertEquals(self.sio.response_elem, 'zato_ping2_response')
        self.assertEquals(self.sio.output_required, ('pong',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.ping2')
        
###############################################################################         

class ChangePasswordBaseTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = ChangePasswordBase
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return {'id':rand_int(), 'password1':rand_string(), 'password2':rand_string()}
    
    def get_response_data(self):
        return Bunch()    
    
    def test_sio(self):
        self.assertEquals(self.sio.input_required, ('id', 'password1', 'password2'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.change-password-base')