# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from random import choice, randint
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

# six
from six import string_types

# SQLAlchemy
from sqlalchemy import create_engine

# Python 2/3 compatibility
from past.builtins import basestring, cmp, xrange

# Zato
from zato.common import CHANNEL, DATA_FORMAT, SIMPLE_IO
from zato.common.log_message import CID_LENGTH
from zato.common.odb import model
from zato.common.util import is_port_taken, new_cid

# ################################################################################################################################

def rand_bool():
    return choice((True, False))

# ################################################################################################################################

def rand_csv(count=3):
    return ','.join(str(elem) for elem in rand_int(count=count))

# ################################################################################################################################

def rand_dict():
    out = {}
    funcs = [rand_bool, rand_int, rand_string]

    for x in range(rand_int(30)):
        out[choice(funcs)()] = choice(funcs)()

    return out

# ################################################################################################################################

def rand_list():
    out = []
    funcs = [rand_bool, rand_int, rand_string]

    for x in range(rand_int(30)):
        out.append(choice(funcs)())

    return out

# ################################################################################################################################

def rand_list_of_dicts():
    out = []
    for x in range(rand_int(30)):
        out.append(rand_dict())
    return out

# ################################################################################################################################

def rand_opaque():
    return rand_object()

rand_nested = rand_opaque

# ################################################################################################################################

def rand_datetime():
    return datetime.utcnow().isoformat() # Random in the sense of not repeating

# ################################################################################################################################

def rand_int(start=1, stop=100, count=1):
    if count == 1:
        return randint(start, stop)
    else:
        return [randint(start, stop) for x in range(count)]

# ################################################################################################################################

def rand_float(start=1.0, stop=100.0):
    return float(rand_int(start, stop))

# ################################################################################################################################

def rand_string(count=1):
    if count == 1:
        return 'a' + uuid4().hex
    else:
        return ['a' + uuid4().hex for x in range(count)]

# ################################################################################################################################

def rand_unicode():
    return u'ϠϡϢϣϤϥϦϧϨϩϪϫϬϭ'

# ################################################################################################################################

def rand_object():
    return object()

# ################################################################################################################################

def rand_date_utc(as_string=False):
    value = datetime.utcnow() # Now is as random as any other date
    if as_string:
        return value.isoformat()
    return value

# ################################################################################################################################

def is_like_cid(cid):
    """ Raises ValueError if the cid given on input does not look like a genuine CID
    produced by zato.common.util.new_cid
    """
    if not isinstance(cid, string_types):
        raise ValueError('CID `{}` should be string like instead of `{}`'.format(cid, type(cid)))

    len_given = len(cid)

    if len_given != CID_LENGTH:
        raise ValueError('CID `{}` should have length `{}` instead of `{}`'.format(cid, CID_LENGTH, len_given))

    return True

# ################################################################################################################################

def get_free_tcp_port(start=40000, stop=40500):
    """ Iterates between start and stop, returning first free TCP port. Must not be used except for tests because
    it comes with a race condition - another process may want to bind the port we find before our caller does.
    """
    for port in xrange(start, stop):
        if not is_port_taken(port):
            return port
    else:
        raise Exception('Could not find any free TCP port between {} and {}'.format(start, stop))

# ################################################################################################################################

def enrich_with_static_config(object_):
    """ Adds to an object (service instance or class) all attributes that are added by service store.
    Useful during tests since there is no service store around to do it.
    """
    object_.component_enabled_ibm_mq = True
    object_.component_enabled_zeromq = True
    object_.component_enabled_patterns = True
    object_.component_enabled_target_matcher = True
    object_.component_enabled_invoke_matcher = True
    object_.component_enabled_sms = True
    object_.get_name()

    def target_match(*args, **kwargs):
        return True

    is_allowed = target_match

    object_._worker_config = Bunch(out_odoo=None, out_soap=None)
    object_._worker_store = Bunch(
        sql_pool_store=None, stomp_outconn_api=None, outgoing_web_sockets=None, cassandra_api=None,
        cassandra_query_api=None, email_smtp_api=None, email_imap_api=None, search_es_api=None, search_solr_api=None,
        target_matcher=Bunch(target_match=target_match, is_allowed=is_allowed), invoke_matcher=Bunch(is_allowed=is_allowed),
        vault_conn_api=None, sms_twilio_api=None)

# ################################################################################################################################

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

# ################################################################################################################################

class FakeBrokerClient(object):

    def __init__(self):
        self.publish_args = []
        self.publish_kwargs = []
        self.invoke_async_args = []
        self.invoke_async_kwargs = []

    def publish(self, *args, **kwargs):
        raise NotImplementedError()

    def invoke_async(self, *args, **kwargs):
        self.invoke_async_args.append(args)
        self.invoke_async_kwargs.append(kwargs)

# ################################################################################################################################

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

# ################################################################################################################################

class FakeServices(object):
    def __getitem__(self, ignored):
        return {'slow_threshold': 1234}

# ################################################################################################################################

class FakeServiceStore(object):
    def __init__(self, name_to_impl_name=None, impl_name_to_service=None):
        self.services = FakeServices()
        self.name_to_impl_name = name_to_impl_name or {}
        self.impl_name_to_service = impl_name_to_service or {}

    def new_instance(self, impl_name, is_active=True):
        return self.impl_name_to_service[impl_name](), is_active

# ################################################################################################################################

class FakeServer(object):
    """ A fake mock server used in test cases.
    """
    def __init__(self, service_store_name_to_impl_name=None, service_store_impl_name_to_service=None, worker_store=None):
        self.kvdb = FakeKVDB()
        self.service_store = FakeServiceStore(service_store_name_to_impl_name, service_store_impl_name_to_service)
        self.worker_store = worker_store
        self.fs_server_config = Bunch()
        self.fs_server_config.misc = Bunch()
        self.fs_server_config.misc.zeromq_connect_sleep = 0.1
        self.fs_server_config.misc.internal_services_may_be_deleted = False
        self.repo_location = rand_string()
        self.delivery_store = None
        self.user_config = Bunch()
        self.static_config = Bunch()
        self.time_util = Bunch()
        self.servers = []
        self.ipc_api = None
        self.component_enabled = Bunch()

# ################################################################################################################################

class ForceTypeWrapper(object):
    """ Makes comparison between two ForceType elements use their names.
    """
    def __init__(self, value):
        self.value = value

    def __cmp__(self, other):
        # Compare to either other's name or to other directly. In the latter case it means it's a plain string name
        # of a SIO attribute.
        return cmp(self.value.name, getattr(other, 'name', other))

# ################################################################################################################################

class ServiceTestCase(TestCase):

    def __init__(self, *args, **kwargs):
        self.maxDiff = None
        super(ServiceTestCase, self).__init__(*args, **kwargs)

    def invoke(self, class_, request_data, expected, mock_data={}, channel=CHANNEL.HTTP_SOAP, job_type=None,
        data_format=DATA_FORMAT.JSON, service_store_name_to_impl_name=None, service_store_impl_name_to_service=None):
        """ Sets up a service's invocation environment, then invokes and returns
        an instance of the service.
        """
        class_.component_enabled_cassandra = True
        class_.component_enabled_email = True
        class_.component_enabled_search = True
        class_.component_enabled_msg_path = True
        class_.has_sio = getattr(class_, 'SimpleIO', False)

        instance = class_()

        server = MagicMock()
        server.component_enabled.stats = False

        worker_store = MagicMock()
        worker_store.worker_config = MagicMock
        worker_store.worker_config.outgoing_connections = MagicMock(return_value=(None, None, None, None))
        worker_store.worker_config.cloud_openstack_swift = MagicMock(return_value=None)
        worker_store.worker_config.cloud_aws_s3 = MagicMock(return_value=None)
        worker_store.invoke_matcher.is_allowed = MagicMock(return_value=True)

        simple_io_config = {
            'int_parameters': SIMPLE_IO.INT_PARAMETERS.VALUES,
            'int_parameter_suffixes': SIMPLE_IO.INT_PARAMETERS.SUFFIXES,
            'bool_parameter_prefixes': SIMPLE_IO.BOOL_PARAMETERS.SUFFIXES,
        }

        class_.update(
            instance, channel, FakeServer(service_store_name_to_impl_name, service_store_impl_name_to_service, worker_store),
            None, worker_store, new_cid(), request_data, request_data, simple_io_config=simple_io_config,
            data_format=data_format, job_type=job_type)

        def get_data(self, *ignored_args, **ignored_kwargs):
            return expected.get_data()

        instance.get_data = get_data

        for attr_name, mock_path_data_list in mock_data.items():
            setattr(instance, attr_name, Mock())
            attr = getattr(instance, attr_name)

            for mock_path_data in mock_path_data_list:
                for path, value in mock_path_data.items():
                    split = path.split('.')
                    new_path = '.return_value.'.join(elem for elem in split) + '.return_value'
                    attr.configure_mock(**{new_path:value})

        broker_client_publish = getattr(self, 'broker_client_publish', None)
        if broker_client_publish:
            instance.broker_client = FakeBrokerClient()
            instance.broker_client.publish = broker_client_publish

        def set_response_func(*args, **kwargs):
            pass

        instance.handle()
        #instance.update_handle(
        #    set_response_func, instance, request_data, channel, data_format, None, server, None, worker_store, new_cid(),
        #    None)
        return instance

    def _check_sio_request_input(self, instance, request_data):
        for k, v in request_data.items():
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

# ################################################################################################################################

class ODBTestCase(TestCase):

    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        model.Base.metadata.create_all(self.engine)

    def tearDown(self):
        model.Base.metadata.drop_all(self.engine)

# ################################################################################################################################
