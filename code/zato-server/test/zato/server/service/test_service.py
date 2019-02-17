# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import ast
from json import loads
from logging import getLogger, INFO
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

# Python 2/3 compatibility
from future.utils import iteritems

# Zato
from zato.common import DATA_FORMAT, PARAMS_PRIORITY, URL_TYPE
from zato.common.test import enrich_with_static_config, rand_string, ServiceTestCase
from zato.server.service import List, Service
from zato.server.service.store import set_up_class_attributes
from zato.server.service.internal.helpers import InputLogger
from zato.server.service.reqresp import HTTPRequestData, Request

logger = getLogger(__name__)
faker = Faker()
enrich_with_static_config(Service)

# ################################################################################################################################

class HooksTestCase(ServiceTestCase):
    def test_hooks_set_up_class_attributes(self):

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

        set_up_class_attributes(MyJob, None)

        eq_(MyJob._has_before_job_hooks, True)
        eq_(MyJob._has_after_job_hooks, True)

        eq_(MyJob._before_job_hooks, [MyJob.before_job, MyJob.before_one_time_job])
        eq_(MyJob._after_job_hooks, [MyJob.after_job, MyJob.after_one_time_job])

# ################################################################################################################################

class TestLogInputOutput(ServiceTestCase):
    def xtest_log_input_output(self):

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

# ################################################################################################################################

class TestHTTPRequestData(TestCase):
    def xtest_empty(self):
        data = HTTPRequestData()
        self.assertEquals(data.GET, None)
        self.assertEquals(data.POST, None)
        self.assertEquals(data.method, None)

    def xtest_non_empty(self):
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

# ################################################################################################################################

class TestRequest(TestCase):
    def xtest_init_no_sio(self):
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
            eq_(sorted(iteritems(request.http.GET)), sorted(iteritems(wsgi_environ['zato.http.GET'])))
            eq_(sorted(iteritems(request.http.POST)), sorted(iteritems(wsgi_environ['zato.http.POST'])))

    def xtest_init_sio(self):

        is_sio = True
        cid = uuid4().hex
        data_format = uuid4().hex
        transport = uuid4().hex

        io_default = {'dummy':'dummy'}
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

        for io in(io_default, io_custom):
            for params_priority in PARAMS_PRIORITY:

                request = Request(logger)
                request.payload = None
                request.raw_request = io_default

                request.channel_params['a'] = 'channel_param_a'
                request.channel_params['b'] = 'channel_param_b'
                request.channel_params['c'] = 'channel_param_c'
                request.channel_params['d'] = 'channel_param_d'
                request.channel_params['e'] = 'channel_param_e'
                request.channel_params['f'] = 'channel_param_f'
                request.channel_params['h'] = 'channel_param_h' # Never overridden

                def _get_params(request_params, *ignored):

                    # Note that 'g' is never overridden

                    if params_priority == PARAMS_PRIORITY.CHANNEL_PARAMS_OVER_MSG:
                        if request_params is io_custom['input_required']:
                            return {'a':request.channel_params['a'], 'b':request.channel_params['b'],
                                    'c':request.channel_params['c'], 'g':'g-msg'}
                        else:
                            return {'d':request.channel_params['d'], 'e':request.channel_params['e'],
                                    'f':request.channel_params['f'], 'g':'g-msg'}
                    else:
                        if request_params is io_custom['input_required']:
                            return {'a':'a-req', 'b':'b-req', 'c':'c-req', 'g':'g-msg'}
                        else:
                            return {'d':'d-opt', 'e':'e-opt', 'f':'f-opt', 'g':'g-msg'}

                request.get_params = _get_params

                request.params_priority = params_priority
                request.http.init(wsgi_environ)
                request.payload = io
                request.init(is_sio, cid, io, data_format, transport, wsgi_environ)

                if io is io_default:

                    eq_(sorted(iteritems(request.input)),
                        sorted(iteritems({'a': 'channel_param_a', 'b': 'channel_param_b',
                         'c':'channel_param_c', 'd': 'channel_param_d', 'e': 'channel_param_e', 'f': 'channel_param_f',
                         'h':'channel_param_h'})))

                else:
                    if params_priority == PARAMS_PRIORITY.CHANNEL_PARAMS_OVER_MSG:

                        eq_(sorted(iteritems(request.input)),
                            sorted(iteritems({'a': 'channel_param_a', 'b': 'channel_param_b', 'c': 'channel_param_c',
                             'd': 'channel_param_d', 'e': 'channel_param_e', 'f': 'channel_param_f',
                             'g': 'g-msg',
                             'h':'channel_param_h'})))

                    else:
                        eq_(sorted(iteritems(request.input)),
                            sorted(iteritems({'a': 'a-req', 'b': 'b-req', 'c': 'c-req',
                             'd': 'd-opt', 'e': 'e-opt', 'f': 'f-opt',
                             'g': 'g-msg',
                             'h':'channel_param_h'})))

# ################################################################################################################################

class TestSIOListDataType(ServiceTestCase):
    # https://github.com/zatosource/zato/issues/114

    def xtest_sio_list_data_type_input_json(self):
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

    def xtest_sio_list_data_type_input_xml(self):
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

    def xtest_sio_list_data_type_output_json(self):
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

    def xtest_sio_list_data_type_output_xml(self):
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

# ################################################################################################################################

class TestNav(TestCase):
    # # https://github.com/zatosource/zato/issues/209

    def xtest_dictnav(self):

        key1, key2, key3 = 'a', 'b', 'c'
        value = rand_string()

        d = {
            'flat': 123,
            'nested':{
                key1: {key2: {key3: value}}
            }
        }

        class MyService(Service):
            def handle(self):
                dn = self.dictnav(self.request.input)

                # 'nopep8' is needed because otherwise flake8 treats .has_key as though
                # it belonged to a dict which is not the case.
                # I.e. W601 .has_key() is deprecated, use 'in'

                response = {
                    'key1': sorted(iteritems(dn.get(['nested', 'a']))),
                    'value': dn.get(['nested', 'a', 'b', 'c']),
                    'has_key_flat_true': dn.has_key('flat', False), # nopep8
                    'has_key_flat_false': dn.has_key(rand_string(), True),
                    'has_key_nested_true': dn.has_key('b'),
                    'has_key_nested_false': dn.has_key(rand_string()),
                    'has_path': dn.has_path(['nested', 'a', 'b', 'c']),
                }
                self.response.payload = response

        service = MyService()
        service.request.input = d
        service.handle()

        eq_(service.response.payload['key1'], [('b', {'c': value})])
        eq_(service.response.payload['value'], value)
        eq_(service.response.payload['has_key_flat_true'], True)
        eq_(service.response.payload['has_key_flat_false'], False)
        eq_(service.response.payload['has_key_nested_true'], True)
        eq_(service.response.payload['has_key_nested_false'], False)
        eq_(service.response.payload['has_path'], True)

    def xtest_listnav(self):
        self.test_dictnav() # Right now dictnav and listnav do the same thing

# ################################################################################################################################

class RESTTargetType(ServiceTestCase):
    # https://github.com/zatosource/zato/issues/177

    def xtest_add_http_method_handlers(self):

        class MyService(Service):

            def handle(self):
                pass

            def handle_GET(self):
                pass

            def handle_POST(self):
                pass

        class MyService2(Service):
            pass

        MyService.add_http_method_handlers()
        self.assertIs(MyService.http_method_handlers['POST'].im_func, MyService.handle_POST.im_func)

        MyService2.add_http_method_handlers()
        self.assertDictEqual(MyService2.http_method_handlers, {})

# ################################################################################################################################

class SelfOutgoingSelfOut(ServiceTestCase):
    def xtest_self_outgoing_is_self_out(self):
        """ GH #712 - self.outgoing should be the same as self.out
        """
        instance = self.invoke(InputLogger, {}, {})
        self.assertIs(instance.outgoing, instance.out)
