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

# Zato
from zato.common import SIMPLE_IO, URL_TYPE, ZATO_OK
from zato.common.util import new_cid
from zato.server.connection.http_soap import channel
from zato.server.service.internal import AdminService

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

class DummyService(AdminService):
    def __init__(self, response=None, cid=None):
        self.response = response
        self.cid = cid if cid else new_cid()

class MessageHandlingBase(TestCase):
    """ Base class for tests for functionality common to SOAP and plain HTTP messages.
    """
    def get_data(self):    
        bmh = channel._BaseMessageHandler()
        
        data_format = SIMPLE_IO.FORMAT.JSON
        transport = URL_TYPE.SOAP
        
        expected = {
            'key': uuid4().hex + NON_ASCII_STRING,
            'value': uuid4().hex + NON_ASCII_STRING,
            'result': uuid4().hex,
            'details': uuid4().hex,
            'cid': new_cid(),
        }

        payload = DummyPayload({expected['key']: expected['value']})
        response = DummyResponse(payload, expected['result'], expected['details'])
        service = DummyService(response, expected['cid'])

        bmh.set_payload(response, data_format, transport, service)
        
        return expected, service

class TestSetPayloadAdminServiceJSONTestCase(MessageHandlingBase):
    def test(self):
        expected, service = self.get_data()
        payload = loads(service.response.payload)
        
        # Will fail with KeyError so it's a good indicator whether it worked at all or not
        payload[expected['key']]
        self.assertEquals(payload[expected['key']], expected['value'])
        
        zato_env = payload['zato_env']
        
        for name in('cid', 'result', 'details'):
            self.assertEquals(zato_env[name], expected[name])
    
    def xtest_set_payload_admin_service_xml_payload_provided(self):
        bmh = channel._BaseMessageHandler()
        
        data_format = SIMPLE_IO.FORMAT.XML
        transport = URL_TYPE.SOAP
        
        expected = {
            'key': 'a' + uuid4().hex + NON_ASCII_STRING,
            'value': 'a' + uuid4().hex + NON_ASCII_STRING,
            'result': uuid4().hex,
            'details': uuid4().hex,
            'cid': new_cid(),
        }
        
        payload = DummyPayload('<{key}>{value}</{key}>'.format(**expected))
        response = DummyResponse(payload, expected['result'], expected['details'])
        service = DummyService(response, expected['cid'])
        
        bmh.set_payload(response, data_format, transport, service)
        payload = etree.fromstring(service.response.payload.encode('utf-8'))
        
        xpath = etree.XPath('//gfr:{}/text()'.format(expected['key']), namespaces=NS_MAP)
        value = xpath(payload)[0]
        self.assertEquals(value, expected['value'])
        
        for name in('cid', 'result', 'details'):
            xpath = etree.XPath('//gfr:zato_env/gfr:{}/text()'.format(name), namespaces=NS_MAP)
            value = xpath(payload)[0]
            self.assertEquals(value, expected[name])

    def xtest_set_payload_admin_service_xml_no_payload_provided(self):
        #raise NotImplementedError('TODO')
        pass
