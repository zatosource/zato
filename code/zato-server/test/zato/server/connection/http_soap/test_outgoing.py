# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import ssl
from datetime import datetime
from http.client import OK
from logging import getLogger
from tempfile import NamedTemporaryFile
from time import sleep
from unittest import TestCase

# bunch
from bunch import Bunch

# lxml
from lxml import etree

# nose
from nose.tools import eq_

# requests
import requests
requests.packages.urllib3.disable_warnings()

# Zato
from zato.common.util import get_component_name
from zato.common import CONTENT_TYPE, DATA_FORMAT, SEC_DEF_TYPE, soapenv11_namespace, soapenv12_namespace, URL_TYPE, ZATO_NONE
from zato.common.test import rand_float, rand_int, rand_string
from zato.common.test.tls import TLSServer
from zato.common.test.tls_material import ca_cert, ca_cert_invalid, client1_cert, client1_key
from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper

logger = getLogger(__name__)

# ################################################################################################################################

class _FakeSession(object):
    def __init__(self, *ignored, **kwargs):
        self.pool_size = kwargs.get('pool_maxsize', 'missing')
        self.request_args = None
        self.request_kwargs = None

    def request(self, *args, **kwargs):
        self.request_args = args
        self.request_kwargs = kwargs

        return Bunch({'status_code':rand_string(), 'text':'"{}"'.format(rand_string())})

    def mount(self, *ignored):
        pass

# ################################################################################################################################

class _FakeRequestsModule(object):
    def __init__(self):
        self.session_obj = None

    def session(self, *args, **kwargs):
        self.session_obj = _FakeSession(*args, **kwargs)
        return self.session_obj

# ################################################################################################################################

class Base(object):

    def _get_config(self, needs_data_format=True):
        return {'is_active':True, 'sec_type':rand_string(), 'address_host':rand_string(),
            'address_url_path':rand_string(), 'ping_method':rand_string(), 'soap_version':'1.1',
            'pool_size':rand_int(), 'serialization_type':'string', 'timeout':rand_int(),
            'tls_verify':ZATO_NONE, 'data_format':'', 'content_type':'',
            'data_format':DATA_FORMAT.JSON if needs_data_format else None, 'transport':'plain_http'}

# ################################################################################################################################

class HTTPSOAPWrapperTestCase(TestCase, Base):

    def setUp(self):
        self.maxDiff = None

    def test_soap_body(self):
        """ https://github.com/zatosource/zato/issues/475 (Body ignored in string-based outgoing SOAP connections)
        """
        config = self._get_config()
        config['transport'] = URL_TYPE.SOAP

        requests_module = _FakeRequestsModule()
        wrapper = HTTPSOAPWrapper(config, requests_module)

        body_text = rand_string()

        wrapper.post(rand_int(), body_text)

        data = etree.fromstring(wrapper.requests_module.session_obj.request_kwargs['data'])
        body = data.xpath('//*[local-name() = "Body"]')[0]
        self.assertEquals(body.text, body_text)

    def test_soap_ns(self):
        """ https://github.com/zatosource/zato/issues/474 (SOAP namespace in string-based messages)
        """
        config = self._get_config()
        requests_module = _FakeRequestsModule()
        wrapper = HTTPSOAPWrapper(config, requests_module)

        soap11 = etree.fromstring(wrapper.soap['1.1']['message'].encode('utf-8'))
        root = soap11.xpath('/*')[0]
        self.assertEquals(root.nsmap['s11'], soapenv11_namespace)

        soap12 = etree.fromstring(wrapper.soap['1.2']['message'].encode('utf-8'))
        root = soap12.xpath('/*')[0]
        self.assertEquals(root.nsmap['s12'], soapenv12_namespace)

    def test_ping_method(self):
        """ https://github.com/zatosource/zato/issues/44 (outconn HTTP/SOAP ping method)
        """
        config = self._get_config()
        expected_ping_method = 'ping-{}'.format(rand_string())
        config['ping_method'] = expected_ping_method
        requests_module = _FakeRequestsModule()

        wrapper = HTTPSOAPWrapper(config, requests_module)
        wrapper.ping(rand_string())

        ping_method = requests_module.session_obj.request_args[0]
        eq_(expected_ping_method, ping_method)

    def test_pool_size(self):
        """ https://github.com/zatosource/zato/issues/77 (outconn HTTP/SOAP pool size)
        """
        config = self._get_config()
        expected_pool_size = rand_int()
        config['pool_size'] = expected_pool_size
        requests_module = _FakeRequestsModule()

        wrapper = HTTPSOAPWrapper(config, requests_module)
        wrapper.ping(rand_string())

        eq_(expected_pool_size, requests_module.session_obj.pool_size)

    def test_timeout(self):
        """ https://github.com/zatosource/zato/issues/112 (HTTP timeouts)
        """
        for name in 'ping', 'get', 'delete', 'options', 'post', 'send', 'put', 'patch':
            for transport in URL_TYPE:
                config = self._get_config()
                config['transport'] = transport
                expected_timeout = rand_float()
                config['timeout'] = expected_timeout
                requests_module = _FakeRequestsModule()

                wrapper = HTTPSOAPWrapper(config, requests_module)
                func = getattr(wrapper, name)
                func(rand_string())

                self.assertIn('timeout', requests_module.session_obj.request_kwargs)
                eq_(expected_timeout, requests_module.session_obj.request_kwargs['timeout'])

    def test_set_address(self):
        address_host = rand_string()
        config = self._get_config()
        config['address_host'] = address_host
        requests_module = _FakeRequestsModule()

        for address_url_path in('/zzz', '/cust/{customer}/order/{order}/pid{process}/',):
            config['address_url_path'] = address_url_path
            wrapper = HTTPSOAPWrapper(config, requests_module)

            eq_(wrapper.address, '{}{}'.format(address_host, address_url_path))

            if address_url_path == '/zzz':
                eq_(wrapper.path_params, [])
            else:
                eq_(wrapper.path_params, ['customer', 'order', 'process'])

    def test_format_address(self):
        cid = rand_string()
        address_host = rand_string()
        address_url_path = '/a/{a}/b{b}/c-{c}/{d}d/'

        config = self._get_config()
        config['address_host'] = address_host
        config['address_url_path'] = address_url_path

        requests_module = _FakeRequestsModule()
        wrapper = HTTPSOAPWrapper(config, requests_module)

        try:
            wrapper.format_address(cid, None)
        except ValueError as e:
            eq_(e.message, 'CID:[{}] No parameters given for URL path'.format(cid))
        else:
            self.fail('Expected ValueError (params is None)')

        a = rand_string()
        b = rand_string()
        c = rand_string()
        d = rand_string()
        e = rand_string()
        f = rand_string()

        params = {'a':a, 'b':b, 'c':c, 'd':d, 'e':e, 'f':f}
        address, non_path_params = wrapper.format_address(cid, params)
        eq_(address, '{}/a/{}/b{}/c-{}/{}d/'.format(address_host, a, b, c, d))
        eq_(non_path_params, {'e':e, 'f':f})

        params = {'a':a, 'b':b}

        try:
            address, non_path_params = wrapper.format_address(cid, params)
        except ValueError as e:
            eq_(e.message, 'CID:[{}] Could not build URL path'.format(cid))
        else:
            self.fail('Expected ValueError (not enough keys in params)')

    def test_http_methods(self):
        address_host = rand_string()

        config = self._get_config()
        config['is_active'] = True
        config['soap_version'] = '1.2'
        config['address_host'] = address_host

        requests_module = _FakeRequestsModule()
        wrapper = HTTPSOAPWrapper(config, requests_module)

        for address_url_path in('/zzz', '/a/{a}/b/{b}'):
            for transport in('soap', rand_string()):
                for name in('get', 'delete', 'options', 'post', 'put', 'patch'):
                    config['transport'] = transport

                    _cid = rand_string()
                    _data = rand_string()

                    expected_http_request_value = rand_string()
                    expected_http_request_value = rand_string()

                    expected_params = rand_string()

                    expected_args1 = rand_string()
                    expected_args2 = rand_string()

                    expected_kwargs1 = rand_string()
                    expected_kwargs2 = rand_string()

                    def http_request(method, cid, data='', params=None, *args, **kwargs):

                        eq_(method, name.upper())
                        eq_(cid, _cid)

                        if name in('get', 'delete', 'options'):
                            eq_(data, '')
                        else:
                            eq_(data, _data)

                        eq_(params, expected_params)
                        eq_(args, (expected_args1, expected_args2))
                        eq_(sorted(kwargs.items()), [('bar', expected_kwargs2), ('foo', expected_kwargs1)])

                        return expected_http_request_value

                    def format_address(cid, params):
                        return expected_http_request_value

                    wrapper.http_request = http_request
                    wrapper.format_address = format_address

                    func = getattr(wrapper, name)

                    if name in('get', 'delete', 'options'):
                        http_request_value = func(
                            _cid, expected_params, expected_args1, expected_args2,
                            foo=expected_kwargs1, bar=expected_kwargs2)
                    else:
                        http_request_value = func(
                            _cid, _data, expected_params, expected_args1, expected_args2,
                            foo=expected_kwargs1, bar=expected_kwargs2)

                    eq_(http_request_value, expected_http_request_value)

    def test_create_headers_json(self):

        cid = rand_string()
        now = datetime.utcnow().isoformat()
        requests_module = _FakeRequestsModule()

        config = self._get_config()
        config['data_format'] = DATA_FORMAT.JSON
        config['transport'] = URL_TYPE.PLAIN_HTTP

        wrapper = HTTPSOAPWrapper(config, requests_module)
        user_headers = {rand_string():rand_string(), rand_string():rand_string()}

        headers = wrapper._create_headers(cid, user_headers, now)

        eq_(headers.pop('X-Zato-CID'), cid)
        eq_(headers.pop('X-Zato-Msg-TS'), now)
        eq_(headers.pop('X-Zato-Component'), get_component_name())
        eq_(headers.pop('Content-Type'), CONTENT_TYPE.JSON)

        # Anything that is left must be user headers
        self.assertDictEqual(headers, user_headers)

    def test_create_headers_plain_xml(self):

        cid = rand_string()
        now = datetime.utcnow().isoformat()
        requests_module = _FakeRequestsModule()

        config = self._get_config()
        config['data_format'] = DATA_FORMAT.XML
        config['transport'] = URL_TYPE.PLAIN_HTTP

        wrapper = HTTPSOAPWrapper(config, requests_module)
        user_headers = {rand_string():rand_string(), rand_string():rand_string()}

        headers = wrapper._create_headers(cid, user_headers, now)

        eq_(headers.pop('X-Zato-CID'), cid)
        eq_(headers.pop('X-Zato-Msg-TS'), now)
        eq_(headers.pop('X-Zato-Component'), get_component_name())
        eq_(headers.pop('Content-Type'), CONTENT_TYPE.PLAIN_XML)

        # Anything that is left must be user headers
        self.assertDictEqual(headers, user_headers)

    def test_create_headers_soap11(self):

        cid = rand_string()
        now = datetime.utcnow().isoformat()
        soap_action = rand_string()
        requests_module = _FakeRequestsModule()

        config = self._get_config()
        config['data_format'] = DATA_FORMAT.XML
        config['transport'] = URL_TYPE.SOAP
        config['soap_action'] = soap_action

        wrapper = HTTPSOAPWrapper(config, requests_module)
        user_headers = {rand_string():rand_string(), rand_string():rand_string()}

        headers = wrapper._create_headers(cid, user_headers, now)

        eq_(headers.pop('X-Zato-CID'), cid)
        eq_(headers.pop('X-Zato-Msg-TS'), now)
        eq_(headers.pop('X-Zato-Component'), get_component_name())
        eq_(headers.pop('SOAPAction'), soap_action)
        eq_(headers.pop('Content-Type'), CONTENT_TYPE.SOAP11)

        # Anything that is left must be user headers
        self.assertDictEqual(headers, user_headers)

    def test_create_headers_soap12(self):

        cid = rand_string()
        now = datetime.utcnow().isoformat()
        soap_action = rand_string()
        requests_module = _FakeRequestsModule()

        config = self._get_config()
        config['data_format'] = DATA_FORMAT.XML
        config['transport'] = URL_TYPE.SOAP
        config['soap_action'] = soap_action
        config['soap_version'] = '1.2'

        wrapper = HTTPSOAPWrapper(config, requests_module)
        user_headers = {rand_string():rand_string(), rand_string():rand_string()}

        headers = wrapper._create_headers(cid, user_headers, now)

        eq_(headers.pop('X-Zato-CID'), cid)
        eq_(headers.pop('X-Zato-Msg-TS'), now)
        eq_(headers.pop('X-Zato-Component'), get_component_name())
        eq_(headers.pop('SOAPAction'), soap_action)
        eq_(headers.pop('Content-Type'), CONTENT_TYPE.SOAP12)

        # Anything that is left must be user headers
        self.assertDictEqual(headers, user_headers)

    def test_create_headers_no_data_format(self):

        cid = rand_string()
        now = datetime.utcnow().isoformat()
        requests_module = _FakeRequestsModule()

        config = self._get_config(False)

        wrapper = HTTPSOAPWrapper(config, requests_module)
        user_headers = {rand_string():rand_string(), rand_string():rand_string()}

        headers = wrapper._create_headers(cid, user_headers, now)

        eq_(headers.pop('X-Zato-CID'), cid)
        eq_(headers.pop('X-Zato-Msg-TS'), now)
        eq_(headers.pop('X-Zato-Component'), get_component_name())

        # Anything that is left must be user headers
        # (note that there was no Content-Type because there was no data_format)
        self.assertDictEqual(headers, user_headers)

    def test_create_headers_user_default_data_format(self):

        cid = rand_string()
        now = datetime.utcnow().isoformat()
        content_type = rand_string()
        requests_module = _FakeRequestsModule()

        config = self._get_config()
        config['content_type'] = content_type

        wrapper = HTTPSOAPWrapper(config, requests_module)
        user_headers = {rand_string():rand_string(), rand_string():rand_string()}

        headers = wrapper._create_headers(cid, user_headers, now)

        eq_(headers.pop('X-Zato-CID'), cid)
        eq_(headers.pop('X-Zato-Msg-TS'), now)
        eq_(headers.pop('X-Zato-Component'), get_component_name())
        eq_(headers.pop('Content-Type'), content_type)

        # Anything that is left must be user headers
        self.assertDictEqual(headers, user_headers)

    def test_create_headers_user_headers_data_format(self):

        cid = rand_string()
        now = datetime.utcnow().isoformat()
        content_type = rand_string()
        requests_module = _FakeRequestsModule()

        config = self._get_config()

        wrapper = HTTPSOAPWrapper(config, requests_module)
        user_headers = {rand_string():rand_string(), rand_string():rand_string(), 'Content-Type':content_type}

        headers = wrapper._create_headers(cid, user_headers, now)

        eq_(headers.pop('X-Zato-CID'), cid)
        eq_(headers.pop('X-Zato-Msg-TS'), now)
        eq_(headers.pop('X-Zato-Component'), get_component_name())
        eq_(headers.pop('Content-Type'), content_type)

        # Anything that is left must be user headers
        self.assertDictEqual(headers, user_headers)

# ################################################################################################################################

class TLSPingTestCase(TestCase, Base):

    def tearDown(self):
        sleep(0.2) # So the server's thread can shut down cleanly

    def test_ping_unknown_ca_verify_false(self):
        server = TLSServer()
        server.start()

        sleep(0.3)

        port = server.get_port()

        config = self._get_config()
        config['address_host'] = 'https://localhost:{}/'.format(port)
        config['address_url_path'] = ''
        config['ping_method'] = 'GET'
        config['tls_verify'] = ZATO_NONE

        wrapper = HTTPSOAPWrapper(config, requests)

        self.assertIn('Code: 200', wrapper.ping(rand_string()))

    def test_ping_unknown_ca_verify_invalid_ca_cert(self):

        with NamedTemporaryFile(prefix='zato-tls', delete=False) as ca_cert_tf:

            ca_cert_tf.write(ca_cert_invalid)
            ca_cert_tf.flush()

            server = TLSServer()
            server.start()

            sleep(0.2)

            port = server.get_port()

            config = self._get_config()
            config['address_host'] = 'https://localhost:{}/'.format(port)
            config['address_url_path'] = ''
            config['ping_method'] = 'GET'
            config['tls_verify'] = ca_cert_tf.name

            wrapper = HTTPSOAPWrapper(config, requests)

            try:
                wrapper.ping(rand_string())
            except Exception as e:
                details = e.message[0][1][0][0]
                try:
                    self.assertEquals(details, ('SSL routines', 'SSL3_GET_SERVER_CERTIFICATE', 'certificate verify failed'))
                except AssertionError:
                    self.assertEquals(details, ('SSL routines', 'tls_process_server_certificate', 'certificate verify failed'))
            else:
                self.fail('Excepted a TLS error here because the CA is invalid')

    def test_ping_client_cert_required_no_client_cert(self):

        with NamedTemporaryFile(prefix='zato-tls', delete=False) as ca_cert_tf:

            ca_cert_tf.write(ca_cert)
            ca_cert_tf.flush()

            server = TLSServer(cert_reqs=ssl.CERT_REQUIRED)
            server.start()

            sleep(0.3)

            port = server.get_port()

            config = self._get_config()
            config['address_host'] = 'https://localhost:{}/'.format(port)
            config['address_url_path'] = ''
            config['ping_method'] = 'GET'
            config['tls_verify'] = ca_cert_tf.name

            wrapper = HTTPSOAPWrapper(config, requests)

            try:
                wrapper.ping(rand_string())
            except Exception as e:
                details = e.message[0][1][0][0]
                try:
                    self.assertEquals(details, ('SSL routines', 'SSL3_READ_BYTES', 'sslv3 alert handshake failure'))
                except AssertionError:
                    self.assertEquals(details, ('SSL routines', 'ssl3_read_bytes', 'sslv3 alert handshake failure'))
            else:
                self.fail('Excepted a TLS error here because no TLS cert has been provided by client')

    def test_ping_client_cert_required_has_client_cert(self):

        with NamedTemporaryFile(prefix='zato-tls', delete=False) as ca_cert_tf:

            ca_cert_tf.write(ca_cert)
            ca_cert_tf.flush()

            with NamedTemporaryFile(prefix='zato-tls', delete=False) as client_cert_tf:

                client_cert_tf.write(client1_key)
                client_cert_tf.write('\n')
                client_cert_tf.write(client1_cert)
                client_cert_tf.flush()

                server = TLSServer(cert_reqs=ssl.CERT_REQUIRED)
                server.start()

                sleep(0.3)

                port = server.get_port()

                config = self._get_config()
                config['address_host'] = 'https://localhost:{}/'.format(port)
                config['address_url_path'] = ''
                config['ping_method'] = 'GET'
                config['tls_verify'] = ca_cert_tf.name
                config['tls_key_cert_full_path'] = client_cert_tf.name
                config['sec_type'] = SEC_DEF_TYPE.TLS_KEY_CERT

                wrapper = HTTPSOAPWrapper(config, requests)

                wrapper.ping(rand_string())

# ################################################################################################################################

class TLSHTTPTestCase(TestCase, Base):

    def test_http_get_unknown_ca_verify_false(self):
        server = TLSServer()
        server.start()

        sleep(0.3)

        port = server.get_port()

        config = self._get_config()
        config['address_host'] = 'https://localhost:{}/'.format(port)
        config['address_url_path'] = ''
        config['ping_method'] = 'GET'
        config['transport'] = URL_TYPE.PLAIN_HTTP
        config['tls_verify'] = ZATO_NONE

        wrapper = HTTPSOAPWrapper(config, requests)

        self.assertEquals(OK, wrapper.get('123').status_code)

    def test_http_get_unknown_ca_verify_invalid_ca_cert(self):

        with NamedTemporaryFile(prefix='zato-tls', delete=False) as ca_cert_tf:

            ca_cert_tf.write(ca_cert_invalid)
            ca_cert_tf.flush()

            server = TLSServer()
            server.start()

            sleep(0.3)

            port = server.get_port()

            config = self._get_config()
            config['address_host'] = 'https://localhost:{}/'.format(port)
            config['address_url_path'] = ''
            config['ping_method'] = 'GET'
            config['transport'] = URL_TYPE.PLAIN_HTTP
            config['tls_verify'] = ca_cert_tf.name

            wrapper = HTTPSOAPWrapper(config, requests)

            try:
                wrapper.get('123')
            except Exception as e:
                details = e.message[0][1][0][0]
                try:
                    self.assertEquals(details, ('SSL routines', 'SSL3_GET_SERVER_CERTIFICATE', 'certificate verify failed'))
                except AssertionError:
                    self.assertEquals(details, ('SSL routines', 'tls_process_server_certificate', 'certificate verify failed'))
            else:
                self.fail('Excepted a TLS error here because the CA is invalid')

    def test_http_get_client_cert_required_no_client_cert(self):

        with NamedTemporaryFile(prefix='zato-tls', delete=False) as ca_cert_tf:

            ca_cert_tf.write(ca_cert)
            ca_cert_tf.flush()

            server = TLSServer(cert_reqs=ssl.CERT_REQUIRED)
            server.start()

            sleep(0.3)

            port = server.get_port()

            config = self._get_config()
            config['address_host'] = 'https://localhost:{}/'.format(port)
            config['address_url_path'] = ''
            config['ping_method'] = 'GET'
            config['transport'] = URL_TYPE.PLAIN_HTTP
            config['tls_verify'] = ca_cert_tf.name

            wrapper = HTTPSOAPWrapper(config, requests)

            try:
                wrapper.get('123')
            except Exception as e:
                details = e.message[0][1][0][0]
                try:
                    self.assertEquals(details, ('SSL routines', 'SSL3_READ_BYTES', 'sslv3 alert handshake failure'))
                except AssertionError:
                    self.assertEquals(details, ('SSL routines', 'ssl3_read_bytes', 'sslv3 alert handshake failure'))
            else:
                self.fail('Excepted a TLS error here because no TLS cert has been provided by client')

    def test_http_get_client_cert_required_has_client_cert(self):

        with NamedTemporaryFile(prefix='zato-tls', delete=False) as ca_cert_tf:

            ca_cert_tf.write(ca_cert)
            ca_cert_tf.flush()

            with NamedTemporaryFile(prefix='zato-tls', delete=False) as client_cert_tf:

                client_cert_tf.write(client1_key)
                client_cert_tf.write('\n')
                client_cert_tf.write(client1_cert)
                client_cert_tf.flush()

                server = TLSServer(cert_reqs=ssl.CERT_REQUIRED)
                server.start()

                sleep(0.3)

                port = server.get_port()

                config = self._get_config()
                config['ping_method'] = 'GET'
                config['tls_verify'] = ca_cert_tf.name
                config['tls_key_cert_full_path'] = client_cert_tf.name
                config['sec_type'] = SEC_DEF_TYPE.TLS_KEY_CERT
                config['address_host'] = 'https://localhost:{}/'.format(port)

                uni_data = u'uni_data'
                string_data = b'string_data'
                needs_data = 'post', 'send', 'put', 'patch'

                for url_type in URL_TYPE:
                    config['transport'] = url_type

                    for data_format in DATA_FORMAT:
                        config['data_format'] = data_format

                        for data in uni_data, string_data:

                            for name in('get', 'delete', 'options', 'post', 'send', 'put', 'patch'):
                                cid = '{}_{}'.format(name, data)

                                config['address_url_path'] = '{}-{}-{}'.format(url_type, data_format, data)
                                wrapper = HTTPSOAPWrapper(config, requests)
                                func = getattr(wrapper, name)

                                if name in needs_data:
                                    func(cid, data=data)
                                else:
                                    func(cid)

# ################################################################################################################################
