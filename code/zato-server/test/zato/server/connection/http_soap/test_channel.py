# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from cStringIO import StringIO
from unittest import TestCase
from uuid import uuid4

# anyjson
from anyjson import loads

# arrow
import arrow

# lxml
from lxml import etree

# nose
from nose.tools import eq_

# Zato
from zato.common import SIMPLE_IO, URL_TYPE, zato_namespace, ZATO_OK
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

# ##############################################################################

class MessageHandlingBase(TestCase):
    """ Base class for tests for functionality common to SOAP and plain HTTP messages.
    """
    def get_data(self, data_format, transport, add_string=NON_ASCII_STRING, needs_payload=True,
            payload='', service_class=DummyAdminService):
        bmh = channel._BaseMessageHandler()
        
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

        bmh.set_payload(response, data_format, transport, service)
        
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
        rd = channel.RequestDispatcher()
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
            response, "[{}] URL:[{}] or SOAP action:[{}] doesn't exist".format(
                cid, path_info, ''))
        
# ##############################################################################
