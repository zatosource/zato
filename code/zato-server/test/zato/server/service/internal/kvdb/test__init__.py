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
from zato.common.test import rand_string, ServiceTestCase
from zato.server.service.internal.kvdb import ExecuteCommand

##############################################################################

class ExecuteCommandTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = ExecuteCommand
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return {'command':rand_string()}
    
    def get_response_data(self):
        return Bunch({'result':rand_string})
    
    def test_sio(self):
        
        self.assertEquals(self.sio.request_elem, 'zato_kvdb_remote_command_execute_request')
        self.assertEquals(self.sio.response_elem, 'zato_kvdb_remote_command_execute_response')
        self.assertEquals(self.sio.input_required, ('command',))
        self.assertEquals(self.sio.output_required, ('result',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.kvdb.remote-command.execute')
        
    def test_fixup_parameters(self):
        params1 = ['mykey']
        params2 = ['"mykey"']
        params3 = ['mykey', '"myvalue"']
        
        service = self.service_class()
        
        # Pass-through
        params = service._fixup_parameters(params1)
        self.assertEquals(params, params1)
        
        # Single param
        params = service._fixup_parameters(params2)
        self.assertEquals(params[0], 'mykey')
        
        # Multiple params
        params = service._fixup_parameters(params3)
        self.assertEquals(params[-1], 'myvalue')
