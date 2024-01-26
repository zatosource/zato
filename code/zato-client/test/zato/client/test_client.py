# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode
from unittest import TestCase
from uuid import uuid4

# mock
from mock import patch

# nose
from nose.tools import eq_

# Python 2/3 compatibility
from zato.common.ext.future.utils import iteritems

# Zato
from zato.common.api import ZATO_OK
from zato.common.json_internal import dumps, loads
from zato.common.test import rand_bool, rand_int, rand_object, rand_string
from zato.common.util.api import new_cid, make_repr
from zato.client import AnyServiceInvoker, CID_NO_CLIP, _Client, JSONClient, JSONSIOClient, \
     RawDataClient, _Response, _StructuredResponse

# ##############################################################################

class FakeInnerResponse:
    def __init__(self, headers, ok, text, status_code):
        self.headers = headers
        self.ok = ok
        self.text = text
        self.status_code = status_code

class FakeSession:
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
    class InnerInvokeResponse:
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
        for class_ in AnyServiceInvoker, JSONClient, JSONSIOClient, RawDataClient:
            with patch('zato.client._Client.inner_invoke', self.get_inner_invoke()):

                client = class_(*rand_string(2))

                header1, value1 = rand_string(2)
                header2, value2 = rand_string(2)
                headers = {header1:value1, header2:value2}

                response = client.invoke(rand_string(), headers=headers)
                eq_(sorted(headers.items()), sorted(response.headers.items()))
