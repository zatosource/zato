# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from random import choice, randint, random
from unittest import TestCase
from uuid import uuid4

# anyjson
from anyjson import loads

# Bunch
from bunch import Bunch

# mock
from mock import MagicMock, Mock

# nose
from nose.tools import eq_

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common import CHANNEL, DATA_FORMAT, SIMPLE_IO
from zato.common.odb import model
from zato.common.util import new_cid

def rand_bool():
    return choice((True, False))

def rand_datetime():
    return datetime.utcnow().isoformat() # Random in the sense of not repeating

def rand_int(start=1, stop=100):
    return randint(start, stop)
    
def rand_float(start=1.0, stop=100.0):
    return random((start, stop))

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
        def __init__(self):
            self.setnx_args = None
            self.setnx_return_value = True
            self.expire_args = None
            self.delete_args = None
            
        def return_none(self, *ignored_args, **ignored_kwargs):
            return None
        
        get = hget = return_none
        
        def setnx(self, *args):
            self.setnx_args = args
            return self.setnx_return_value
        
        def expire(self, *args):
            self.expire_args = args
            
        def delete(self, args):
            self.delete_args = args
        
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
        self.delivery_store = None

class ForceTypeWrapper(object):
    """ Makes comparison between two ForceType elements use their names.
    """
    def __init__(self, value):
        self.value = value
        
    def __cmp__(self, other):
        return cmp(self.value.name, other.name)
        
class ServiceTestCase(TestCase):
    
    def invoke(self, class_, request_data, expected, mock_data={}, 
               channel=CHANNEL.HTTP_SOAP, job_type=None, data_format=DATA_FORMAT.JSON):
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
        
        class_.update(
            instance, channel, FakeServer(), None, worker_store, new_cid(), request_data, request_data,
            simple_io_config=simple_io_config, data_format=data_format, job_type=job_type)

        def get_data(self, *ignored_args, **ignored_kwargs):
            return expected.get_data()
            
        instance.get_data = get_data
        
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

        sio_keys = set(getattr(instance.SimpleIO, 'input_required', []))
        sio_keys.update(set(getattr(instance.SimpleIO, 'input_optional', [])))
        given_keys = set(request_data.keys())
        
        diff = sio_keys ^ given_keys
        self.assertFalse(diff, 'There should be no difference between sio_keys {} and given_keys {}, diff {}'.format(
            sio_keys, given_keys, diff))
    
    def check_impl(self, service_class, request_data, response_data, response_elem, mock_data={}):

        expected_data = sorted(response_data.items())
        
        instance = self.invoke(service_class, request_data, None, mock_data)
        self._check_sio_request_input(instance, request_data)
        
        if response_data:
            if not isinstance(instance.response.payload, basestring):
                response = loads(instance.response.payload.getvalue())[response_elem] # Raises KeyError if 'response_elem' doesn't match
            else:
                response = loads(instance.response.payload)[response_elem]
                
            self.assertEqual(sorted(response.items()), expected_data)
    
    def check_impl_list(self, service_class, item_class, request_data, # noqa
            response_data, request_elem, response_elem, mock_data={}): # noqa
        
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

    def wrap_force_type(self, elem):
        return ForceTypeWrapper(elem)

class ODBTestCase(TestCase):

    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=self.engine)
        session = Session()
        model.Base.metadata.create_all(self.engine)
        
    def tearDown(self):
        model.Base.metadata.drop_all(self.engine)
