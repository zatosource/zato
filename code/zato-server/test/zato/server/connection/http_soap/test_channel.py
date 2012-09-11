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
from unittest import TestCase
from uuid import uuid4

# anyjson
from anyjson import loads

# lxml
from lxml import etree

# nose
from nose.tools import eq_

# Zato
from zato.common import SIMPLE_IO, URL_TYPE, ZATO_OK
from zato.common.util import new_cid
from zato.server.connection.http_soap import channel
from zato.server.service import Service
from zato.server.service.internal import AdminService, Service

# Tokyo
NON_ASCII_STRING = '東京'

NS_MAP = {
    'gfr': 'http://gefira.pl/zato',
    'soap': 'http://schemas.xmlsoap.org/soap/envelope/'
}

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
    pass

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
        }
        
        if needs_payload:
            if not payload:
                if data_format == SIMPLE_IO.FORMAT.JSON:
                    payload_value = {expected['key']: expected['value']}
                else:
                    # str.format can't handle Unicode arguments http://bugs.python.org/issue7300
                    payload_value = '<%(key)s>%(value)s</%(key)s>' % (expected)
                payload = DummyPayload(payload_value)
        else:
            payload = None

        response = DummyResponse(payload, expected['result'], expected['details'])
        service = service_class(response, expected['cid'])

        bmh.set_payload(response, data_format, transport, service)
        
        return expected, service

class TestSetPayloadAdminServiceTestCase(MessageHandlingBase):
    
    def _test_xml(self, url_type, needs_payload):
        expected, service = self.get_data(SIMPLE_IO.FORMAT.XML, url_type, '', needs_payload)
        payload = etree.fromstring(service.response.payload)
        
        parent_path = '/soap:Envelope/soap:Body' if url_type == URL_TYPE.SOAP else ''
        
        if needs_payload:
            path = parent_path + '/gfr:zato_message/gfr:{}/text()'.format(expected['key'])
            xpath = etree.XPath(path, namespaces=NS_MAP)
            value = xpath(payload)[0]
            eq_(value, expected['value'])
        else:
            path = parent_path + '/gfr:zato_message/gfr:response'
            xpath = etree.XPath(path, namespaces=NS_MAP)
            value = xpath(payload)[0]
            eq_(value.text, None)
            
        for name in('cid', 'result', 'details'):
            path = parent_path + '/gfr:zato_message/gfr:zato_env/gfr:{}/text()'.format(name)
            xpath = etree.XPath(path, namespaces=NS_MAP)
            
            value = xpath(payload)[0]
            eq_(value, expected[name])

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
        
class TestSetPayloadNonAdminServiceTestCase(MessageHandlingBase):
    
    def test_payload_provided_basestring(self):
        payload = uuid4().hex
        ignored, service = self.get_data(None, None, '', payload=payload, service_class=DummyService)
        eq_(payload, service.response.payload)
        
    def test_payload_provided_non_basestring(self):
        payload = DummyPayload(uuid4().hex)
        ignored, service = self.get_data(None, None, '', payload=payload, service_class=DummyService)
        eq_(payload.value, service.response.payload)