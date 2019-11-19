# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from base64 import b64encode
from unittest import TestCase
from uuid import uuid4

# anyjson
from anyjson import dumps, loads

# lxml
from lxml import etree

# mock
from mock import patch

# nose
from nose.tools import eq_

# Python 2/3 compatibility
from future.utils import iteritems

# Zato
from zato.common import common_namespaces, ZATO_OK
from zato.common.test import rand_bool, rand_int, rand_object, rand_string
from zato.common.util import new_cid, make_repr
from zato.client import AnyServiceInvoker, CID_NO_CLIP, _Client, JSONClient, JSONSIOClient, \
     RawDataClient, _Response, SOAPClient, SOAPSIOClient, _StructuredResponse, XMLClient

# ##############################################################################

class FakeInnerResponse(object):
    def __init__(self, headers, ok, text, status_code):
        self.headers = headers
        self.ok = ok
        self.text = text
        self.status_code = status_code

class FakeSession(object):
    def __init__(self, response=None, auth=None):
        self.response = response
        self.auth = auth

    def post(self, address, request, headers, *ignored_args, **ignored_kwargs):
        return self.response

# ##############################################################################

class _Base(TestCase):
    client_class = None

    def setUp(self):
        self.url = rand_string()
        self.auth = None
        self.path = rand_string()
        self.session = FakeSession()
        self.to_bunch = rand_bool()
        self.max_response_repr = 10000
        self.max_cid_repr = rand_int()
        self.logger = rand_object()

    def get_client(self, response):
        self.session.response = response

        return self.client_class(
            self.url, self.auth, self.path, self.session,
            self.to_bunch, self.max_response_repr, self.max_cid_repr)

# ##############################################################################

class JSONClientTestCase(_Base):
    client_class = JSONClient

    def test_client(self):

        cid = new_cid()
        headers = {'x-zato-cid':cid}
        ok = True
        text = dumps({rand_string(): rand_string()})
        status_code = rand_int()

        client = self.get_client(FakeInnerResponse(headers, ok, text, status_code))
        response = client.invoke()

        eq_(response.ok, ok)
        eq_(response.inner.text, text)
        eq_(iteritems(response.data), iteritems(loads(text)))
        eq_(response.has_data, True)
        eq_(response.cid, cid)

class XMLClientTestCase(_Base):
    client_class = XMLClient

    def test_client(self):

        cid = new_cid()
        headers = {'x-zato-cid':cid}
        ok = True
        text = '<abc>{}</abc>'.format(rand_string())
        status_code = rand_int()

        client = self.get_client(FakeInnerResponse(headers, ok, text, status_code))
        response = client.invoke()

        eq_(response.ok, ok)
        eq_(response.inner.text, text)
        eq_(etree.tostring(response.data), text)
        eq_(response.has_data, True)
        eq_(response.cid, cid)

class SOAPClientTestCase(_Base):
    client_class = SOAPClient

    def test_client_ok(self):

        cid = new_cid()
        headers = {'x-zato-cid':cid}
        ok = True
        _rand = rand_string()
        soap_action = rand_string()

        text = """
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
             <soapenv:Body>
              <abc>{}</abc>
             </soapenv:Body>
            </soapenv:Envelope>""".format(_rand).strip()
        status_code = rand_int()

        client = self.get_client(FakeInnerResponse(headers, ok, text, status_code))
        response = client.invoke(soap_action)

        expected_response_data = """
            <abc xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">{}</abc>
            """.format(_rand).strip()

        eq_(response.details, None)
        eq_(response.ok, ok)
        eq_(response.inner.text, text)
        eq_(etree.tostring(response.data), expected_response_data)
        eq_(response.has_data, True)
        eq_(response.cid, cid)

    def test_client_no_soap_response(self):

        cid = new_cid()
        headers = {'x-zato-cid':cid}
        ok = False
        soap_action = rand_string()

        text = '<abc/>'
        status_code = rand_int()

        client = self.get_client(FakeInnerResponse(headers, ok, text, status_code))
        response = client.invoke(soap_action)

        eq_(response.ok, ok)
        eq_(response.details, 'No /soapenv:Envelope/soapenv:Body/*[1] in SOAP response')
        eq_(response.inner.text, text)
        eq_(response.has_data, False)
        eq_(response.cid, cid)

# ##############################################################################

class JSONSIOClientTestCase(_Base):
    client_class = JSONSIOClient

    def test_client(self):

        cid = new_cid()
        headers = {'x-zato-cid':cid}
        ok = True

        env = {
            'details': rand_string(),
            'result': ZATO_OK,
            'cid': cid
        }

        sio_payload_key = rand_string()
        sio_payload = {rand_string(): rand_string()}

        sio_response = {
            'zato_env': env,
            sio_payload_key: sio_payload
        }

        text = dumps(sio_response)
        status_code = rand_int()

        client = self.get_client(FakeInnerResponse(headers, ok, text, status_code))
        response = client.invoke()

        eq_(response.ok, ok)
        eq_(response.inner.text, text)
        eq_(iteritems(response.data), iteritems((sio_response[sio_payload_key])))
        eq_(response.has_data, True)
        eq_(response.cid, cid)
        eq_(response.cid, sio_response['zato_env']['cid'])
        eq_(response.details, sio_response['zato_env']['details'])

class SOAPSIOClientTestCase(_Base):
    client_class = SOAPSIOClient

    def test_client_ok(self):

        cid = new_cid()
        headers = {'x-zato-cid':cid}
        ok = True
        status_code = rand_int()
        rand_id, rand_name, soap_action = rand_string(), rand_string(), rand_string()

        sio_response = """<zato_outgoing_amqp_edit_response xmlns="https://zato.io/ns/20130518">
           <zato_env>
            <cid>{}</cid>
            <result>ZATO_OK</result>
           </zato_env>
           <item>
            <id>{}</id>
            <name>crm.account</name>
           </item>
          </zato_outgoing_amqp_edit_response>
        """.format(cid, rand_id, rand_name)

        text = """<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns="https://zato.io/ns/20130518">
             <soap:Body>
              {}
             </soap:Body>
            </soap:Envelope>""".format(sio_response).strip()

        client = self.get_client(FakeInnerResponse(headers, ok, text, status_code))
        response = client.invoke(soap_action, '')

        eq_(response.ok, ok)
        eq_(response.inner.text, text)
        eq_(response.has_data, True)
        eq_(response.cid, cid)

        path_items = (
            ('zato_env', 'cid'),
            ('zato_env', 'result'),
            ('item', 'id'),
            ('item', 'name'),
        )

        for items in path_items:
            path = '//zato:zato_outgoing_amqp_edit_response/zato:' + '/zato:'.join(items)
            xpath = etree.XPath(path, namespaces=common_namespaces)

            expected = xpath(etree.fromstring(text))[0].text
            actual = xpath(response.data)[0]

            self.assertEquals(expected, actual)

    def test_client_soap_fault(self):

        cid = new_cid()
        headers = {'x-zato-cid':cid}
        ok = False
        status_code = rand_int()
        soap_action = rand_string()

        text = b"""<?xml version='1.0' encoding='UTF-8'?>
 <SOAP-ENV:Envelope
   xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
   xmlns:xsi="http://www.w3.org/1999/XMLSchema-instance"
   xmlns:xsd="http://www.w3.org/1999/XMLSchema">
    <SOAP-ENV:Body>
      <SOAP-ENV:Fault>
      <faultcode>SOAP-ENV:Client</faultcode>
 <faultstring><![CDATA[cid [K68438211212681798524426103126], faultstring
 [Traceback (most recent call last):
File
"/opt/zato/code/zato-server/src/zato/server/connection/http_soap/
channel.py", line 126, in dispatch
  service_info, response = handler.handle(cid, wsgi_environ, payload, transport,
  worker_store, self.simple_io_config, data_format, path_info)
File
"/opt/zato/code/zato-server/src/zato/server/connection/http_soap/
channel.py", line 227, in handle
  service_instance.handle()
File
"/opt/zato/code/zato-server/src/zato/server/service/internal/
definition/amqp.py", line 174, in handle
  filter(ConnDefAMQP.id==self.request.input.id).\
File
"/opt/zato/code/eggs/SQLAlchemy-0.7.9-py2.7-linux-x86_64.egg/sqlalchemy/
orm/query.py", line 2190, in one
  raise orm_exc.NoResultFound("No row was found for one()")
NoResultFound: No row was found for one()
]]]></faultstring>
       </SOAP-ENV:Fault>
   </SOAP-ENV:Body>
 </SOAP-ENV:Envelope>"""

        client = self.get_client(FakeInnerResponse(headers, ok, text, status_code))
        response = client.invoke(soap_action, '')

        eq_(response.ok, ok)
        eq_(response.inner.text, text)
        eq_(response.has_data, False)
        eq_(response.cid, cid)
        eq_('NoResultFound: No row was found for one()' in response.details.getchildren()[1].text, True)

# ##############################################################################

class AnyServiceInvokerTestCase(_Base):
    client_class = AnyServiceInvoker

    def test_client(self):

        cid = new_cid()
        headers = {'x-zato-cid':cid}
        ok = True
        status_code = rand_int()

        service_name = rand_string()
        service_response_name = '{}_response'.format(service_name)
        service_response_payload = {'service_id':5207, 'has_wsdl':True}
        service_response_dict = {'zato_service_has_wsdl_response':service_response_payload}
        service_response = b64encode(dumps(service_response_dict))

        text = dumps({
            'zato_env':{'result':ZATO_OK, 'details':''},
            service_response_name: {
                'response':service_response
            }
        })

        client = self.get_client(FakeInnerResponse(headers, ok, text, status_code))
        response = client.invoke(service_name, '')

        eq_(response.ok, ok)
        eq_(response.inner.text, text)
        eq_(response.data.items(), service_response_payload.items())
        eq_(response.has_data, True)
        eq_(response.cid, cid)

# ##############################################################################

class RawDataClientTestCase(_Base):
    client_class = RawDataClient

    def test_client(self):

        cid = new_cid()
        headers = {'x-zato-cid':cid}
        ok = True
        text = rand_string()
        status_code = rand_int()

        client = self.get_client(FakeInnerResponse(headers, ok, text, status_code))
        response = client.invoke()

        eq_(response.ok, ok)
        eq_(response.inner.text, text)
        eq_(response.data, text)
        eq_(response.has_data, True)
        eq_(response.cid, cid)

# ##############################################################################

class NotImplementedErrorTestCase(_Base):

    def test_not_implemented_error(self):
        inner = FakeInnerResponse({}, rand_int(), rand_string(), rand_int())
        response_data = (inner, rand_bool(), rand_int(), rand_int(), None)

        self.assertRaises(NotImplementedError, _Response, *response_data)
        self.assertRaises(NotImplementedError, _StructuredResponse(*response_data).load_func)
        self.assertRaises(NotImplementedError, _StructuredResponse(*response_data).set_has_data)

class TestResponse(TestCase):
    def test_repr(self):

        class MyResponse(_Response):
            def init(self):
                pass

        cid = new_cid()
        ok = True
        text = rand_string()
        status_code = rand_int()
        inner_params = ({'x-zato-cid':cid}, ok, text, status_code)

        max_repr = ((3,3), (len(text), CID_NO_CLIP))
        for(max_response_repr, max_cid_repr) in max_repr:

            inner = FakeInnerResponse(*inner_params)
            response = MyResponse(inner, False, max_response_repr, max_cid_repr, None)
            response.ok = ok

            cid_ellipsis = '' if max_cid_repr == CID_NO_CLIP else '..'

            expected = 'ok:[{}] inner.status_code:[{}] cid:[{}{}{}], inner.text:[{}]>'.format(
                ok, status_code, cid[:max_cid_repr], cid_ellipsis, cid[-max_cid_repr:], text[:max_response_repr])

            eq_(repr(response).endswith(expected), True)

class TestSettingSessionAuth(TestCase):
    def test_setting_session_auth_no_previous_auth(self):
        auth = (uuid4().hex, uuid4().hex)
        client = _Client(uuid4().hex, uuid4().hex, auth)

        self.assertEqual(client.session.auth, auth)

    def test_setting_session_auth_has_previous_auth(self):
        auth1 = (uuid4().hex, uuid4().hex)
        auth2 = (uuid4().hex, uuid4().hex)

        session = FakeSession(uuid4, auth1)
        client = _Client(uuid4().hex, uuid4().hex, auth2, session=session)

        # Make sure we don't override already existing auth
        self.assertNotEqual(client.session.auth, auth2)

        # The previous auth should still be there
        self.assertEqual(client.session.auth, auth1)

class TestHeaders(TestCase):
    """ GH #221 - Clients don't always properly pass headers on to super classes.
    """
    class InnerInvokeResponse(object):
        def __init__(self, request, response_class, is_async, headers):
            self.request = request
            self.response_class = response_class
            self.is_async = is_async
            self.headers = headers

        def __repr__(self):
            return make_repr(self)

    def get_inner_invoke(self):
        return self.InnerInvokeResponse

    def test_clients(self):
        for class_ in AnyServiceInvoker, JSONClient, JSONSIOClient, XMLClient, RawDataClient, SOAPClient, SOAPSIOClient:
            with patch('zato.client._Client.inner_invoke', self.get_inner_invoke()):

                client = class_(*rand_string(2))

                header1, value1 = rand_string(2)
                header2, value2 = rand_string(2)
                headers = {header1:value1, header2:value2}

                response = client.invoke(rand_string(), headers=headers)
                eq_(sorted(headers.items()), sorted(response.headers.items()))
