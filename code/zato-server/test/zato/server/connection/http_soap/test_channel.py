# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from http.client import OK
from io import StringIO
from unittest import TestCase
from uuid import uuid4

# anyjson
from anyjson import loads

# arrow
import arrow

# Bunch
from bunch import Bunch

# lxml
from lxml import etree

# nose
from nose.tools import eq_

# Python 2/3 compatibility
from future.utils import iteritems

# Zato
from zato.common import CHANNEL, DATA_FORMAT, SIMPLE_IO, URL_PARAMS_PRIORITY, URL_TYPE, zato_namespace, ZATO_NONE, ZATO_OK
from zato.common.test import rand_string
from zato.common.util import new_cid
from zato.server.connection.http_soap import channel
from zato.server.service.internal import AdminService, Service

# ##############################################################################

# Tokyo
NON_ASCII_STRING = '東京'

NS_MAP = {
    'zato': zato_namespace,
    'soap': 'http://schemas.xmlsoap.org/soap/envelope/'
}

# ##############################################################################

class DummyPayload(object):
    def __init__(self, value):
        self.value = value

    def getvalue(self, *ignored_args, **ignored_kwargs):
        return self.value

class DummyResponse(object):
    def __init__(self, payload, result=ZATO_OK, result_details=''):
        self.payload = payload
        self.result = result
        self.result_details = result_details if result_details else uuid4().hex
        self.content_type = 'text/plain'
        self.status_code = OK
        self.headers = {}

class DummyService(Service):
    def __init__(self, response=None, cid=None):
        self.response = response
        self.cid = cid if cid else new_cid()

class DummyAdminService(DummyService, AdminService):
    class SimpleIO:
        response_elem = 'zzz'
        namespace = zato_namespace

class DummySecurity(object):
    def url_sec_get(self, *ignored_args, **ignored_kwargs):
        pass

class DummyURLData(object):
    def __init__(self, match_return_value, channel_item_return_value):
        self.match_return_value = match_return_value
        self.channel_item_return_value = channel_item_return_value
        self.cid = None
        self.channel_item = None
        self.path_info = None
        self.payload = None
        self.wsgi_environ = None
        self.url_sec = {}

    def match(self, *ignored_args, **ignored_kwargs):
        return self.match_return_value, self.channel_item_return_value

    def check_security(self, sec, cid, channel_item, path_info, payload, wsgi_environ, post_data, worker_store):
        self.sec = sec
        self.cid = cid
        self.channel_item = channel_item
        self.path_info = path_info
        self.payload = payload
        self.wsgi_environ = wsgi_environ
        self.post_data = post_data

def get_dummy_server():
    server = Bunch()
    server.fs_server_config = Bunch()
    server.fs_server_config.misc = Bunch()
    server.fs_server_config.misc.use_soap_envelope = True
    return server

# ##############################################################################

class MessageHandlingBase(TestCase):
    """ Base class for tests for functionality common to SOAP and plain HTTP messages.
    """
    def get_data(self, data_format, transport, add_string=NON_ASCII_STRING, needs_payload=True,
            payload='', service_class=DummyAdminService):
        handler = channel.RequestHandler(get_dummy_server())

        expected = {
            'key': 'a' + uuid4().hex + add_string,
            'value': uuid4().hex + NON_ASCII_STRING,
            'result': uuid4().hex,
            'details': uuid4().hex,
            'cid': new_cid(),
            'zato':zato_namespace
        }

        if needs_payload:
            if not payload:
                if data_format == SIMPLE_IO.FORMAT.JSON:
                    payload_value = {expected['key']: expected['value']}
                else:
                    # NOTE: str.format can't handle Unicode arguments http://bugs.python.org/issue7300
                    payload_value = """<%(key)s xmlns="%(zato)s">%(value)s<zato_env>
                          <cid>%(cid)s</cid>
                          <result>%(result)s</result>
                          <details>%(details)s</details>
                        </zato_env>
                      </%(key)s>""" % (expected)
                payload = DummyPayload(payload_value)
        else:
            payload = None

        response = DummyResponse(payload, expected['result'], expected['details'])
        service = service_class(response, expected['cid'])

        handler.set_payload(response, data_format, transport, service)

        return expected, service

# ##############################################################################

class TestSetPayloadAdminServiceTestCase(MessageHandlingBase):

    def _test_xml(self, url_type, needs_payload):
        expected, service = self.get_data(SIMPLE_IO.FORMAT.XML, url_type, '', needs_payload)
        payload = etree.fromstring(service.response.payload)

        parent_path = '/soap:Envelope/soap:Body' if url_type == URL_TYPE.SOAP else ''

        if needs_payload:
            path = parent_path + '/zato:{}/text()'.format(expected['key'])
            xpath = etree.XPath(path, namespaces=NS_MAP)
            value = xpath(payload)[0]
            eq_(value, expected['value'])
        else:
            path = parent_path + '//zato:{}'.format(DummyAdminService.SimpleIO.response_elem)
            xpath = etree.XPath(path, namespaces=NS_MAP)
            value = xpath(payload)[0]
            eq_(value.text.strip(), '')

        zato_env_path_elem = expected['key'] if needs_payload else DummyAdminService.SimpleIO.response_elem

        for name in('cid', 'result', 'details'):
            if not needs_payload and name == 'details':
                continue

            path = parent_path + '/zato:{}/zato:zato_env/zato:{}/text()'.format(zato_env_path_elem, name)
            xpath = etree.XPath(path, namespaces=NS_MAP)

            value = xpath(payload)[0]

            if needs_payload:
                eq_(value, expected[name])
            else:
                if name == 'result':
                    eq_(value, ZATO_OK)
                elif name == 'cid':
                    eq_(value, expected['cid'])

    def test_payload_provided_json_plain_http(self):
        expected, service = self.get_data(SIMPLE_IO.FORMAT.JSON, URL_TYPE.PLAIN_HTTP)
        payload = loads(service.response.payload)

        # Will fail with KeyError so it's a good indicator whether it worked at all or not
        payload[expected['key']]
        eq_(payload[expected['key']], expected['value'])

        zato_env = payload['zato_env']

        for name in('cid', 'result', 'details'):
            eq_(zato_env[name], expected[name])

    def test_payload_provided_xml_plain_http(self):
        self._test_xml(URL_TYPE.PLAIN_HTTP, True)

    def test_payload_provided_xml_soap(self):
        self._test_xml(URL_TYPE.SOAP, True)

    def test_no_payload_xml_plain_http(self):
        self._test_xml(URL_TYPE.PLAIN_HTTP, False)

    def test_no_payload_xml_soap(self):
        self._test_xml(URL_TYPE.SOAP, False)

# ##############################################################################

class TestSetPayloadNonAdminServiceTestCase(MessageHandlingBase):

    def test_payload_provided_basestring(self):
        payload = uuid4().hex
        ignored, service = self.get_data(None, None, '', payload=payload, service_class=DummyService)
        eq_(payload, service.response.payload)

    def test_payload_provided_non_basestring(self):
        payload = DummyPayload(uuid4().hex)
        ignored, service = self.get_data(None, None, '', payload=payload, service_class=DummyService)
        eq_(payload.value, service.response.payload)

# ##############################################################################

class TestRequestDispatcher(MessageHandlingBase):
    def test_soap_quotes(self):
        rd = channel.RequestDispatcher()

        soap_action = '"aaa"'
        soap_action = rd._handle_quotes_soap_action(soap_action)
        self.assertEquals(soap_action, 'aaa')

        soap_action = 'aaa"'
        soap_action = rd._handle_quotes_soap_action(soap_action)
        self.assertEquals(soap_action, 'aaa"')

        soap_action = '"aaa'
        soap_action = rd._handle_quotes_soap_action(soap_action)
        self.assertEquals(soap_action, '"aaa')

        soap_action = 'aaa'
        soap_action = rd._handle_quotes_soap_action(soap_action)
        self.assertEquals(soap_action, 'aaa')

    def test_dispatch_no_url_data(self):
        rd = channel.RequestDispatcher(DummyURLData(False, Bunch()))
        rd.security = DummySecurity()

        cid = uuid4().hex
        ts = arrow.now()

        path_info = uuid4().hex
        wsgi_input = StringIO()
        wsgi_input.write('zzz')

        wsgi_environ = {'PATH_INFO':path_info, 'wsgi.input': wsgi_input}

        response = rd.dispatch(cid, ts, wsgi_environ, None)

        self.assertEquals(wsgi_environ['zato.http.response.status'], '404 Not Found')
        self.assertEquals(
            response, 'CID:`{}` Unknown URL:`{}` or SOAP action:`{}`'.format(cid, path_info, ''))

    def test_check_security_request_handler_handle_are_called(self):

        class DummyRequestHandler(object):
            def __init__(self):
                self.cid = None
                self.url_match = {ZATO_NONE:ZATO_NONE}
                self.channel_item = None
                self.wsgi_environ = {ZATO_NONE:ZATO_NONE}
                self.payload = None
                self.worker_store = None
                self.simple_io_config = None

            def handle(self, cid, url_match, channel_item, wsgi_environ, payload, worker_store, simple_io_config, post_data,
                    path_info=None, soap_action=None, channel_type=None, _response_404=None):
                self.cid = cid
                self.url_match = url_match
                self.channel_item = channel_item
                self.wsgi_environ = wsgi_environ
                self.payload = payload
                self.worker_store = worker_store
                self.simple_io_config = simple_io_config

                return DummyResponse('dummy_response')

        class DummySecDef(object):
            sec_type = 'basic_auth'

        cid = uuid4().hex
        req_timestamp = uuid4().hex
        path_info = uuid4().hex
        soap_action = uuid4().hex
        worker_store = uuid4().hex
        simple_io_config = uuid4().hex

        match_return_value = Bunch()
        match_return_value.is_active = True
        match_return_value.transport = uuid4().hex
        match_return_value.data_format = uuid4().hex

        channel_item_return_value = Bunch()
        channel_item_return_value.is_active = True
        channel_item_return_value.transport = uuid4().hex
        channel_item_return_value.data_format = uuid4().hex
        channel_item_return_value.match_target = uuid4().hex
        channel_item_return_value.method = ''

        payload = uuid4().hex

        wsgi_input = StringIO()
        wsgi_input.write(payload)
        wsgi_input.seek(0)

        wsgi_environ = {
            'PATH_INFO':path_info,
            'HTTP_SOAPACTION':soap_action,
            'wsgi.input':wsgi_input,
            'zato.http.response.headers': {},
        }

        ud = DummyURLData(match_return_value, channel_item_return_value)
        ud.url_sec[channel_item_return_value.match_target] = Bunch(sec_def=DummySecDef())

        rd = channel.RequestDispatcher(ud)
        rd.simple_io_config = simple_io_config
        rd.request_handler = DummyRequestHandler()
        rd.dispatch(cid, req_timestamp, wsgi_environ, worker_store)

        eq_(ud.cid, cid)
        eq_(ud.channel_item, channel_item_return_value)
        eq_(ud.path_info, path_info)
        eq_(ud.payload, payload)
        eq_(sorted(ud.wsgi_environ.items()), sorted(wsgi_environ.items()))

        eq_(rd.request_handler.cid, cid)
        eq_(sorted(rd.request_handler.url_match.items()), sorted(match_return_value.items()))
        eq_(rd.request_handler.channel_item, channel_item_return_value)
        eq_(sorted(rd.request_handler.wsgi_environ.items()), sorted(wsgi_environ.items()))
        eq_(rd.request_handler.payload, payload)
        eq_(rd.request_handler.worker_store, worker_store)
        eq_(rd.request_handler.simple_io_config, simple_io_config)

# ##############################################################################

class TestRequestHandler(TestCase):
    def test_handle(self):
        expected_cid = uuid4().hex
        expected_url_match = uuid4().hex
        expected_wsgi_environ = uuid4().hex
        expected_raw_request = uuid4().hex
        expected_simple_io_config = uuid4().hex
        expected_channel = CHANNEL.HTTP_SOAP

        expected_channel_item = Bunch()
        expected_channel_item.service_impl_name = Bunch()
        expected_channel_item.data_format = uuid4().hex
        expected_channel_item.transport = uuid4().hex
        expected_channel_item.params_pri = uuid4().hex
        expected_channel_item.cache_type = None

        expected_worker_store = Bunch()
        expected_worker_store.broker_client = uuid4().hex

        expected_channel_params = uuid4().hex

        def _create_channel_params(url_match, channel_item, wsgi_environ, raw_request, post_data=None):
            eq_(url_match, expected_url_match)
            eq_(channel_item, expected_channel_item)
            eq_(wsgi_environ, expected_wsgi_environ)
            eq_(raw_request, expected_raw_request)
            return expected_channel_params

        for merge_url_params_req in(True, False):
            expected_channel_item.merge_url_params_req = merge_url_params_req

            rh = channel.RequestHandler(get_dummy_server())

            class _Service:
                def update_handle(_self, _set_response_data, service, raw_request,
                        channel, data_format, transport, server, broker_client,
                        worker_store, cid, simple_io_config, wsgi_environ,
                        url_match, channel_item, channel_params,
                        merge_channel_params, params_priority):

                    eq_(_set_response_data, rh._set_response_data)
                    eq_(_self, service)
                    eq_(raw_request, expected_raw_request)
                    eq_(channel, expected_channel)
                    eq_(data_format, expected_channel_item.data_format)
                    eq_(transport, expected_channel_item.transport)
                    eq_(server, rh.server)
                    eq_(broker_client, expected_worker_store.broker_client)
                    eq_(sorted(worker_store.items()), sorted(expected_worker_store.items()))
                    eq_(cid, expected_cid)
                    eq_(simple_io_config, expected_simple_io_config)
                    eq_(wsgi_environ, expected_wsgi_environ)
                    eq_(url_match, expected_url_match)
                    eq_(sorted(channel_item.items()), sorted(expected_channel_item.items()))

                    if merge_url_params_req:
                        eq_(channel_params, expected_channel_params)
                    else:
                        eq_(channel_params, None)

                    eq_(merge_channel_params, merge_url_params_req)
                    eq_(params_priority, expected_channel_item.params_pri)

            class _server:
                class service_store:
                    @staticmethod
                    def new_instance(service_impl_name):
                        _server.service_impl_name = service_impl_name
                        return _Service(), True

            rh.server = _server
            rh.create_channel_params = _create_channel_params
            rh.handle(expected_cid, expected_url_match, expected_channel_item,
                expected_wsgi_environ, expected_raw_request, expected_worker_store,
                expected_simple_io_config, None, None, None)

    def test_create_channel_params(self):

        url_match = Bunch()
        url_match.url_key1 = 'path-{}'.format(uuid4().hex)
        url_match.url_key2 = 'path-{}'.format(uuid4().hex)

        qs_key1, qs_value1 = 'url_key1', 'qs-aaa-{}'.format(uuid4().hex)
        qs_key2, qs_value2 = 'url_key2', 'qs-bbbb-{}'.format(uuid4().hex)

        # Same key, different values
        qs_key3_1, qs_value3_1 = 'url_key3', 'qs-key3_1-{}'.format(uuid4().hex)
        qs_key3_2, qs_value3_2 = 'url_key3', 'qs-key3_2-{}'.format(uuid4().hex)

        post_key1, post_value1 = 'post_key1', uuid4().hex
        post_key2, post_value2 = 'post_key2', uuid4().hex

        raw_request = '{}={}&{}={}'.format(post_key1, post_value1, post_key2, post_value2)

        wsgi_environ = {}
        wsgi_environ['QUERY_STRING'] = '{}={}&{}={}&{}={}&{}={}'.format(
            qs_key1, qs_value1, qs_key2, qs_value2, qs_key3_1, qs_value3_1,
            qs_key3_2, qs_value3_2)

        for data_format in DATA_FORMAT:
            for url_params_pri in URL_PARAMS_PRIORITY:

                channel_item = Bunch()
                channel_item.data_format = data_format
                channel_item.url_params_pri = url_params_pri

                rh = channel.RequestHandler(get_dummy_server())
                channel_params = rh.create_channel_params(url_match, channel_item, wsgi_environ, raw_request)

                get = wsgi_environ['zato.http.GET']

                eq_(get[qs_key1], qs_value1)
                eq_(get[qs_key2], qs_value2)
                eq_(get[qs_key3_1], [qs_value3_1, qs_value3_2])
                eq_(get[qs_key3_2], [qs_value3_1, qs_value3_2])

                if data_format == DATA_FORMAT.POST:
                    eq_(sorted(iteritems(wsgi_environ['zato.http.POST'])), [(post_key1, post_value1), (post_key2, post_value2)])

                if url_params_pri == URL_PARAMS_PRIORITY.PATH_OVER_QS:
                    eq_(channel_params['url_key1'], url_match.url_key1)
                    eq_(channel_params['url_key2'], url_match.url_key2)
                else:
                    eq_(channel_params['url_key1'], qs_value1)
                    eq_(channel_params['url_key2'], qs_value2)

    def test_set_content_type(self):

        class FakeServer(object):
            soap11_content_type = 'soap11_content_type-' + rand_string()
            soap12_content_type = 'soap12_content_type-' + rand_string()
            plain_xml_content_type = 'plain_xml_content_type-' + rand_string()
            json_content_type = 'json_content_type-' + rand_string()
            fs_server_config = Bunch(misc=Bunch(use_soap_envelope=True))

        class FakeResponse(object):
            def __init__(self, content_type_changed=False):
                self.content_type_changed = content_type_changed
                self.content_type = ZATO_NONE

        class FakeChannelItem(object):
            def __init__(self, soap_version='1.1'):
                self.soap_version = soap_version

        rh = channel.RequestHandler(FakeServer())

        #
        # Here are the scenarios we support
        #
        # 1) User sets their own content-type
        # 2) SOAP 1.1
        # 3) SOAP 1.2
        # 4) Plain XML
        # 5) JSON
        # 6) No content-type specified - we need to use default value
        #

        #
        # 1)
        #
        response = FakeResponse(True)
        user_content_type = rand_string()
        response.content_type = user_content_type

        rh.set_content_type(response, rand_string(), rand_string(), None, FakeChannelItem())
        eq_(response.content_type, user_content_type)

        #
        # 2)
        #
        response = FakeResponse()
        rh.set_content_type(response, SIMPLE_IO.FORMAT.XML, URL_TYPE.SOAP, None, FakeChannelItem())
        eq_(response.content_type, FakeServer.soap11_content_type)

        #
        # 3)
        #
        response = FakeResponse()
        rh.set_content_type(response, SIMPLE_IO.FORMAT.XML, URL_TYPE.SOAP, None, FakeChannelItem('1.2'))
        eq_(response.content_type, FakeServer.soap12_content_type)

        #
        # 4)
        #
        response = FakeResponse()
        rh.set_content_type(response, SIMPLE_IO.FORMAT.XML, URL_TYPE.PLAIN_HTTP, None, FakeChannelItem())
        eq_(response.content_type, FakeServer.plain_xml_content_type)

        #
        # 5)
        #
        response = FakeResponse()
        rh.set_content_type(response, SIMPLE_IO.FORMAT.JSON, URL_TYPE.PLAIN_HTTP, None, FakeChannelItem())
        eq_(response.content_type, FakeServer.json_content_type)

        #
        # 6)
        #
        response = FakeResponse(False)
        user_content_type = rand_string()
        response.content_type = user_content_type

        rh.set_content_type(response, rand_string(), rand_string(), None, FakeChannelItem())
        eq_(response.content_type, user_content_type)
