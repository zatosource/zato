# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import ast
from json import loads
from logging import getLogger, INFO
from time import time
from unittest import TestCase
from uuid import uuid4

# Bunch
from bunch import Bunch

# faker
from faker import Faker

# lxml
from lxml import etree, objectify

# nose
from nose.tools import eq_

# retools
from retools.lock import LockTimeout

# Zato
from zato.common import CHANNEL, DATA_FORMAT, KVDB, PARAMS_PRIORITY, \
     SCHEDULER_JOB_TYPE, URL_TYPE
from zato.common.test import FakeKVDB, rand_string, rand_int, ServiceTestCase
from zato.server.service import List, Service
from zato.server.service.reqresp import HTTPRequestData, Request

logger = getLogger(__name__)
faker = Faker()

# ##############################################################################

class HooksTestCase(ServiceTestCase):
    def test_hooks(self):
        
        class MyJob(Service):
            def handle(self):
                pass
            
            def before_handle(self):
                self.environ['before_handle_called'] = True
            
            def before_job(self):
                self.environ['before_job_called'] = True
            
            def before_one_time_job(self):
                self.environ['before_one_time_job_called'] = True
            
            def after_handle(self):
                self.environ['after_handle_called'] = True
            
            def after_job(self):
                self.environ['after_job_called'] = True
            
            def after_one_time_job(self):
                self.environ['after_one_time_job_called'] = True
            
        instance = self.invoke(MyJob, {}, {}, channel=CHANNEL.SCHEDULER, job_type=SCHEDULER_JOB_TYPE.ONE_TIME)
        
        for name in('before_handle', 'before_job', 'before_one_time_job', 'after_handle', 'after_job', 'after_one_time_job'):
            eq_(instance.environ['{}_called'.format(name)], True)

# ##############################################################################

class TestLogInputOutput(ServiceTestCase):
    def test_log_input_output(self):
        
        class MyLogger(object):
            def __init__(self):
                self.level = None
                self.msg = None
                
            def log(self, level, msg):
                self.level = level
                self.msg = msg
                
        class DummyService(Service):
            def handle(self):
                self.logger = MyLogger()
        
        instance = self.invoke(DummyService, {}, {})
        
        level = uuid4().hex
        user_msg = uuid4().hex
        
        instance._log_input_output(user_msg, level, {}, True)
        eq_(instance.logger.level, level)
        self.assertTrue(instance.logger.msg.startswith('{} '.format(user_msg)))
        
        instance.log_input()
        eq_(instance.logger.level, INFO)
        msg = ast.literal_eval(instance.logger.msg)
        eq_(sorted(msg), ['channel', 'cid', 'data_format', 'environ', 
                           'impl_name', 'invocation_time', 'job_type', 'name', 
                           'request.payload', 'slow_threshold', u'usage', 
                           'wsgi_environ'])

        instance.log_output()
        eq_(instance.logger.level, INFO)
        msg = ast.literal_eval(instance.logger.msg)
        eq_(sorted(msg), ['channel', 'cid', 'data_format', 'environ', 
                           'handle_return_time', 'impl_name', 'invocation_time', 
                           'job_type', 'name', 'processing_time', 'processing_time_raw', 
                           'response.payload', 'slow_threshold', 'usage', 
                           'wsgi_environ', 'zato.http.response.headers'])

# ##############################################################################

class TestLock(ServiceTestCase):
    def test_lock_ok(self):
        """ Succesfully grab a service lock.
        """ 
        my_kvdb = FakeKVDB()
        my_kvdb.conn.setnx_return_value = True
        
        lock_name = rand_string()
        expires = 500 + rand_int() # It's 500 which means DummyService.invoke has that many seconds to complete
        timeout = rand_int()
        
        class DummyService(Service):
            kvdb = my_kvdb
            def handle(self):
                with self.lock(lock_name, expires, timeout):
                    pass
                
        instance = DummyService()
        instance.handle()
        
        eq_(my_kvdb.conn.delete_args, KVDB.LOCK_SERVICE_PREFIX + lock_name)
        eq_(my_kvdb.conn.expire_args, (KVDB.LOCK_SERVICE_PREFIX + lock_name, expires))
        
        # First arg is the lock_name that can ne checked directly but the other
        # one is the expiration time that we can check only approximately,
        # anything within 3 seconds range is OK. The value of 3 is the maximum
        # time allowed for execution of DummyService's invoke method which is
        # way more than needed but let's use 3 to be on the safe side when the
        # test is run on a very slow system.
        eq_(my_kvdb.conn.setnx_args[0], KVDB.LOCK_SERVICE_PREFIX + lock_name)
        expires_approx = time() + expires
        self.assertAlmostEquals(my_kvdb.conn.setnx_args[1], expires_approx, delta=3)
        
        
    def test_lock_timeout(self):
        """ A timeout is caught while trying to obtain a service lock.
        """
        my_kvdb = FakeKVDB()
        my_kvdb.conn.setnx_return_value = False
        
        lock_name = rand_string()
        expires = rand_int()
        timeout = -1
        
        class DummyService(Service):
            kvdb = my_kvdb
            def handle(self):
                with self.lock(lock_name, expires, timeout):
                    pass
                
        instance = DummyService()
        
        try:
            instance.handle()
        except LockTimeout, e:
            eq_(e.message, 'Timeout while waiting for lock')
        else:
            self.fail('LockTimeout not raised')
            
# ##############################################################################

class TestHTTPRequestData(TestCase):
    def test_empty(self):
        data = HTTPRequestData()
        self.assertEquals(data.GET, None)
        self.assertEquals(data.POST, None)
        self.assertEquals(data.method, None)
        
    def test_non_empty(self):
        get1, get2 = uuid4().hex, uuid4().hex
        post1, post2 = uuid4().hex, uuid4().hex
        request_method = uuid4().hex
        
        wsgi_environ = {
            'REQUEST_METHOD': request_method,
            'zato.http.GET': {'get1':get1, 'get2':get2},
            'zato.http.POST': {'post1':post1, 'post2':post2},
        }
        
        data = HTTPRequestData()
        data.init(wsgi_environ)
        
        self.assertEquals(data.method, request_method)
        self.assertEquals(sorted(data.GET.items()), [('get1', get1), ('get2', get2)])
        self.assertEquals(sorted(data.POST.items()), [('post1', post1), ('post2', post2)])

# ##############################################################################

class TestRequest(TestCase):
    def test_init_no_sio(self):
        is_sio = False
        cid = uuid4().hex
        data_format = uuid4().hex
        io = uuid4().hex
        
        wsgi_environ = {
            'zato.http.GET': {uuid4().hex:uuid4().hex}, 
            'zato.http.POST': {uuid4().hex:uuid4().hex}, 
            'REQUEST_METHOD': uuid4().hex, 
        }
        
        for transport in(None, URL_TYPE.PLAIN_HTTP, URL_TYPE.SOAP):
            request = Request(None)
            request.http.init(wsgi_environ)
            request.init(is_sio, cid, io, data_format, transport, wsgi_environ)

            eq_(request.http.method, wsgi_environ['REQUEST_METHOD'])
            eq_(sorted(request.http.GET.items()), sorted(wsgi_environ['zato.http.GET'].items()))
            eq_(sorted(request.http.POST.items()), sorted(wsgi_environ['zato.http.POST'].items()))

    def test_init_sio(self):

        is_sio = True
        cid = uuid4().hex
        data_format = uuid4().hex
        transport = uuid4().hex
        
        io_default = {}
        io_custom = Bunch({
            'request_elem': uuid4().hex,
            'input_required': ['a', 'b', 'c'],
            'input_optional': ['d', 'e', 'f'],
            'default_value': uuid4().hex,
            'use_text': uuid4().hex,
        })
        
        wsgi_environ = {
            'zato.http.GET': {uuid4().hex:uuid4().hex}, 
            'zato.http.POST': {uuid4().hex:uuid4().hex}, 
            'REQUEST_METHOD': uuid4().hex, 
        }
        
        def _get_params(request_params, *ignored):
            # 'g' is never overridden
            if request_params is io_custom['input_required']:
                return {'a':'a-req', 'b':'b-req', 'c':'c-req', 'g':'g-msg'}
            else:
                return {'d':'d-opt', 'e':'e-opt', 'f':'f-opt', 'g':'g-msg'}
        
        request = Request(logger)
        request.payload = None
        request.get_params = _get_params
        
        request.channel_params['a'] = 'channel_param_a'
        request.channel_params['b'] = 'channel_param_b'
        request.channel_params['c'] = 'channel_param_c'
        request.channel_params['d'] = 'channel_param_d'
        request.channel_params['e'] = 'channel_param_e'
        request.channel_params['f'] = 'channel_param_f'
        request.channel_params['h'] = 'channel_param_h' # Never overridden
        
        for io in(io_default, io_custom):
            for params_priority in PARAMS_PRIORITY:
                request.params_priority = params_priority
                request.http.init(wsgi_environ)
                request.payload = io
                request.init(is_sio, cid, io, data_format, transport, wsgi_environ)

                if io is io_default:
                    eq_(sorted(request.input.items()), 
                        sorted({'a': 'channel_param_a', 'b': 'channel_param_b', 'c': 'channel_param_c',
                         'd': 'channel_param_d', 'e': 'channel_param_e', 'f': 'channel_param_f',
                         'h':'channel_param_h'}.items()))
                else:
                    if params_priority == PARAMS_PRIORITY.CHANNEL_PARAMS_OVER_MSG:
                        eq_(sorted(request.input.items()), 
                            sorted({'a': 'channel_param_a', 'b': 'channel_param_b', 'c': 'channel_param_c',
                             'd': 'channel_param_d', 'e': 'channel_param_e', 'f': 'channel_param_f',
                             'g': 'g-msg',
                             'h':'channel_param_h'}.items()))
                    else:
                        eq_(sorted(request.input.items()), 
                            sorted({'a': 'a-req', 'b': 'b-req', 'c': 'c-req',
                             'd': 'd-opt', 'e': 'e-opt', 'f': 'f-opt',
                             'g': 'g-msg',
                             'h':'channel_param_h'}.items()))
                        
# ##############################################################################

class TestSIOListDataType(ServiceTestCase):
    # https://github.com/zatosource/zato/issues/114    
    
    def test_sio_list_data_type_input_json(self):
        cid = rand_string()
        data_format = DATA_FORMAT.JSON
        transport = rand_string()
        
        sio_config = {'int_parameters': [rand_string()]} # Not really used but needed
        
        service_sio = Bunch()
        service_sio.input_required = ('first_name', 'last_name', List('emails'))
        
        expected_first_name = faker.first_name()
        expected_last_name = faker.last_name()
        expected_emails = sorted([faker.email(), faker.email()])
        
        r = Request(getLogger(__name__), sio_config)
        r.payload = {
            'first_name': expected_first_name,
            'last_name': expected_last_name,
            'emails': expected_emails,
            }
        
        r.init(True, cid, service_sio, data_format, transport, {})
        
        eq_(r.input.first_name, expected_first_name)
        eq_(r.input.last_name, expected_last_name)
        eq_(r.input.emails, expected_emails)

    def test_sio_list_data_type_input_xml(self):
        cid = rand_string()
        data_format = DATA_FORMAT.XML
        transport = rand_string()
        
        sio_config = {'int_parameters': [rand_string()]} # Not really used but needed
        
        service_sio = Bunch()
        service_sio.input_required = ('first_name', 'last_name', List('emails'))
        
        expected_first_name = faker.first_name()
        expected_last_name = faker.last_name()
        expected_emails = sorted([faker.email(), faker.email()])
        
        r = Request(getLogger(__name__), sio_config)
        r.payload = etree.fromstring("""<request>
          <first_name>{}</first_name>
          <last_name>{}</last_name>
          <emails>
           <item>{}</item>
           <item>{}</item>
          </emails>
        </request>""".format(
            expected_first_name, expected_last_name, expected_emails[0], expected_emails[1]))
        
        r.init(True, cid, service_sio, data_format, transport, {})
        
        eq_(r.input.first_name, expected_first_name)
        eq_(r.input.last_name, expected_last_name)
        eq_(r.input.emails, expected_emails)

    def test_sio_list_data_type_output_json(self):
        expected_first_name = faker.first_name()
        expected_last_name = faker.last_name()
        expected_emails = sorted([faker.email(), faker.email()])

        class MyService(Service):
            class SimpleIO:
                output_required = ('first_name', 'last_name', List('emails'))
                
            def handle(self):
                self.response.payload.first_name = expected_first_name
                self.response.payload.last_name = expected_last_name
                self.response.payload.emails = expected_emails
            
        instance = self.invoke(MyService, {}, None, data_format=DATA_FORMAT.JSON)
        response = loads(instance.response.payload.getvalue(True))['response']
        
        eq_(response['first_name'], expected_first_name)
        eq_(response['last_name'], expected_last_name)
        eq_(response['emails'], expected_emails)
        
    def test_sio_list_data_type_output_xml(self):
        expected_first_name = faker.first_name()
        expected_last_name = faker.last_name()
        expected_emails = sorted([faker.email(), faker.email()])

        class MyService(Service):
            class SimpleIO:
                output_required = ('first_name', 'last_name', List('emails'))
                
            def handle(self):
                self.response.payload.first_name = expected_first_name
                self.response.payload.last_name = expected_last_name
                self.response.payload.emails = expected_emails
                
        instance = self.invoke(MyService, {}, None, data_format=DATA_FORMAT.XML)
        response = instance.response.payload.getvalue(True)
        
        data = objectify.fromstring(response).xpath('/response/item')[0]
        
        eq_(data.first_name.text, expected_first_name)
        eq_(data.last_name.text, expected_last_name)
        eq_(data.emails.xpath('item'), expected_emails)
