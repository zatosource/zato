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

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from random import choice, randint
from unittest import TestCase
from uuid import uuid4

# anyjson
from anyjson import dumps, loads

# Bunch
from bunch import Bunch

# mock
from mock import MagicMock, Mock

# nose
from nose.tools import eq_

# Zato
from zato.common import CHANNEL, SIMPLE_IO
from zato.common.util import new_cid

def rand_bool():
    return choice((True, False))

def rand_int(start=1, stop=100):
    return randint(start, stop)

def rand_string():
    return 'a' + uuid4().hex

def rand_object():
    return object()

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
        
class FakeBrokerClient(object):
    def publish(self, *args, **kwargs):
        raise NotImplementedError()

class FakeKVDB(object):
    class FakeConn(object):
        def return_none(self, *ignored_args, **ignored_kwargs):
            return None
        
        get = hget = return_none
        
    def __init__(self):
        self.conn = self.FakeConn()
        
    def translate(self, *ignored_args, **ignored_kwargs):
        raise NotImplementedError()

class FakeServices(object):
    def __getitem__(self, ignored):
        return {'slow_threshold': 1234}
    
class FakeServiceStore(object):
    def __init__(self):
        self.services = FakeServices()
        
class FakeServer(object):
    """ A fake mock server used in test cases.
    """
    def __init__(self):
        self.kvdb = FakeKVDB()
        self.service_store = FakeServiceStore()
        self.fs_server_config = Bunch()
        self.fs_server_config.misc = Bunch()
        self.fs_server_config.misc.internal_services_may_be_deleted = False
        self.repo_location = rand_string()
        
class ServiceTestCase(TestCase):
    
    def invoke(self, class_, request_data, expected, mock_data={}, channel=CHANNEL.HTTP_SOAP, job_type=None):
        """ Sets up a service's invocation environment, then invokes and returns
        an instance of the service.
        """
        instance = class_()
        worker_store = MagicMock()
        worker_store.worker_config = MagicMock
        worker_store.worker_config.outgoing_connections = MagicMock(return_value=(None, None, None))
        
        simple_io_config = {
            'int_parameters': SIMPLE_IO.INT_PARAMETERS.VALUES,
            'int_parameter_suffixes': SIMPLE_IO.INT_PARAMETERS.SUFFIXES,
            'bool_parameter_prefixes': SIMPLE_IO.BOOL_PARAMETERS.SUFFIXES,
        }
        
        class_.update(instance, channel, FakeServer(), None, worker_store, new_cid(), request_data, request_data, 
            simple_io_config=simple_io_config, data_format=SIMPLE_IO.FORMAT.JSON, job_type=job_type)

        def get_data(self, *ignored_args, **ignored_kwargs):
            return expected.get_data()
        
        for attr_name, mock_path_data_list in mock_data.iteritems():
            setattr(instance, attr_name, Mock())
            attr = getattr(instance, attr_name)
            
            for mock_path_data in mock_path_data_list:
                for path, value in mock_path_data.iteritems():
                    splitted = path.split('.')
                    new_path = '.return_value.'.join(elem for elem in splitted) + '.return_value'
                    attr.configure_mock(**{new_path:value})
                    
        broker_client_publish = getattr(self, 'broker_client_publish', None)
        if broker_client_publish:
            instance.broker_client = FakeBrokerClient()
            instance.broker_client.publish = broker_client_publish

        instance.call_hooks('before')
        instance.handle()
        instance.call_hooks('after')

        instance.handle()
        
        return instance
    
    def _check_sio_request_input(self, instance, request_data):
        for k, v in request_data.iteritems():
            self.assertEquals(getattr(instance.request.input, k), v)
    
    def check_impl(self, service_class, request_data, response_data, response_elem, mock_data={}):
        
        expected_keys = response_data.keys()
        expected_data = tuple(response_data for x in range(rand_int(10)))
        expected = Expected()
        
        instance = self.invoke(service_class, request_data, expected, mock_data)
        if not isinstance(instance.response.payload, basestring):
            loads(instance.response.payload.getvalue())[response_elem] # Raises KeyError if 'response_elem' doesn't match
        
        self._check_sio_request_input(instance, request_data)
    
    def check_impl_list(self, service_class, item_class, request_data, 
        response_data, request_elem, response_elem, mock_data={}):
        
        expected_keys = response_data.keys()
        expected_data = tuple(response_data for x in range(rand_int(10)))
        expected = Expected()
        
        for datum in expected_data:
            item = item_class()
            for key in expected_keys:
                value = getattr(datum, key)
                setattr(item, key, value)
            expected.add(item)
            
        instance = self.invoke(service_class, request_data, expected, mock_data)
        response = loads(instance.response.payload.getvalue())[response_elem]
        
        for idx, item in enumerate(response):
            expected = expected_data[idx]
            given = Bunch(item)
            
            for key in expected_keys:
                given_value = getattr(given, key)
                expected_value = getattr(expected, key)
                eq_(given_value, expected_value)
                
        self._check_sio_request_input(instance, request_data)
