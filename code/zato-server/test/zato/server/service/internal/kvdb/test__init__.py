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

