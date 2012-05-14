# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

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

# stdlib
from random import choice, randint
from unittest import TestCase
from uuid import uuid4

# anyjson
from anyjson import dumps, loads

# mock
from mock import MagicMock

# nose
from nose.tools import assert_true, eq_

# Bunch
from bunch import Bunch

# Zato
from zato.common.odb.model import Service
from zato.common.util import new_cid
from zato.server.service.internal.service import GetByName

class Expected(object):
    """ A container for the data a test expects the service to return.
    """
    def __init__(self):
        self.data = []
        
    def add(self, item):
        self.data.append(item)
        
    def get_data(self):
        if not self.data or len(self.data) > 1:
            return self.data
        else:
            return self.data[0]
        
class ServiceTestCase(TestCase):
    
    def invoke(self, class_, request, expected):
        """ Sets up a service's invocation environment, then invokes and returns
        an instance of the service.
        """
        request_string = dumps(request)
        instance = class_()
        worker_store = MagicMock()
        worker_store.worker_config = MagicMock
        worker_store.worker_config.outgoing_connections = MagicMock(return_value=(None, None, None))
        
        class_.update(instance, None, None, worker_store, new_cid(), request, request_string, 
            simple_io_config={})

        def get_data(self, *ignored_args, **ignored_kwargs):
            return expected.get_data()

        instance.get_data = get_data
        instance.handle()
        
        return instance

class GetByNameTestCase(ServiceTestCase):
    def test(self):

        request = {'cluster_id': randint(1, 100), 'name': uuid4().hex}
        
        expected_id = randint(1, 100)
        expected_name = uuid4().hex
        expected_is_active = choice((True, False))
        expected_impl_name = uuid4().hex
        expected_is_internal = choice((True, False))
        
        service = Service()
        service.id = expected_id
        service.name = expected_name
        service.is_active = expected_is_active
        service.impl_name = expected_impl_name
        service.is_internal = expected_is_internal
        
        expected = Expected()
        expected.add(service)
        
        instance = self.invoke(GetByName, request, expected)
        response = Bunch(loads(instance.response.payload.getvalue())['response'])
        
        eq_(response.id, expected_id)
        eq_(response.name, expected_name)
        eq_(response.is_active, expected_is_active)
        eq_(response.impl_name, expected_impl_name)
        eq_(response.is_internal, expected_is_internal)
        eq_(response.usage_count, 0)
