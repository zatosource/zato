# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import time
import unittest
from base64 import b64encode
from urllib.request import Request, urlopen

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_delivery_poll_timeout  = 10
_delivery_poll_interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

class _AdminClient:
    """ Invokes services via the admin channel (zato.api.invoke) for verification.
    """

    def __init__(self, base_url:'str', password:'str') -> 'None':
        self.base_url = base_url
        self._auth = b64encode(f'admin.invoke:{password}'.encode()).decode()

# ################################################################################################################################

    def invoke(self, service_name:'str', payload:'dict | None'=None) -> 'any_':
        url = f'{self.base_url}/zato/api/invoke/{service_name}'
        body = json.dumps(payload).encode() if payload else b'{}'

        request = Request(url, data=body, method='POST')
        request.add_header('Authorization', f'Basic {self._auth}')
        request.add_header('Content-Type', 'application/json')

        with urlopen(request) as response:
            raw = response.read()

        if not raw:
            return {}

        out = json.loads(raw)
        return out

# ################################################################################################################################
# ################################################################################################################################

class TestDjangoPlugin(unittest.TestCase):

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]

        from zato.common.test.config_django_plugin import TestConfig

        class_.test_config = TestConfig

        # .. admin client for verification calls ..
        class_.admin_client = _AdminClient(TestConfig.base_url, TestConfig.password)

        # .. configure Django settings for the plugin ..
        import django.conf
        django.conf.settings.configure(
            ZATO_URL=TestConfig.base_url + '/zato/api/invoke/django/{}',
            ZATO_USERNAME='django',
            ZATO_PASSWORD=TestConfig.django_password,
            SECRET_KEY='test-secret-key',
            INSTALLED_APPS=[],
            MIDDLEWARE=[],
        )

# ################################################################################################################################

    def setUp(self) -> 'None':
        _ = self.admin_client.invoke('test.django.clear-received')

# ################################################################################################################################

    def _get_received(self) -> 'any_':
        """ Polls the get-received service until at least one entry arrives.
        """
        deadline = time.monotonic() + _delivery_poll_timeout

        while time.monotonic() < deadline:

            result = self.admin_client.invoke('test.django.get-received')
            if isinstance(result, str):
                result = json.loads(result)

            count = result['count']
            if count >= 1:
                return result

            time.sleep(_delivery_poll_interval)

        result = self.admin_client.invoke('test.django.get-received')
        if isinstance(result, str):
            result = json.loads(result)

        return result

# ################################################################################################################################

    def _make_mock_request(self, username:'str'='', remote_addr:'str'='', correlation_id:'str'='') -> 'any_':
        """ Builds a mock Django request with the specified context fields.
        """

        class MockUser:
            is_authenticated = bool(username)

            def __init__(self, username:'str') -> 'None':
                self.username = username

        class MockRequest:
            def __init__(self) -> 'None':
                self.user = MockUser(username)
                self.META = {}
                if remote_addr:
                    self.META['REMOTE_ADDR'] = remote_addr
                if correlation_id:
                    self.META['HTTP_X_ZATO_CORRELATION_ID'] = correlation_id

        out = MockRequest()
        return out

# ################################################################################################################################

    def test_invoke_basic(self) -> 'None':
        """ The Django plugin can invoke a Zato service and the service receives the request data.
        """

        # Zato
        from django_zato import client

        test_value = os.urandom(8).hex()
        data = {'test_key': test_value}

        # .. invoke the echo service via the Django plugin ..
        _ = client.invoke('test.django.echo', data)

        # .. verify the service received the data ..
        received = self._get_received()

        entry_count = received['count']
        self.assertGreaterEqual(entry_count, 1)

        first_entry = received['entries'][0]
        payload = first_entry['payload']

        if isinstance(payload, str):
            payload = json.loads(payload)

        self.assertEqual(payload['test_key'], test_value)

# ################################################################################################################################

    def test_invoke_returns_response(self) -> 'None':
        """ The Django plugin returns the response dict from the Zato service.
        """

        # Zato
        from django_zato import client

        test_value = os.urandom(8).hex()
        data = {'test_key': test_value}

        response = client.invoke('test.django.echo', data)

        if isinstance(response, str):
            response = json.loads(response)

        self.assertIn('payload', response)

# ################################################################################################################################

    def test_invoke_with_request_propagates_user(self) -> 'None':
        """ When a Django request with an authenticated user is passed, the X-Zato-User header arrives.
        """

        # Zato
        from django_zato import client

        test_value = os.urandom(8).hex()
        mock_request = self._make_mock_request(username='testuser_' + test_value)

        _ = client.invoke('test.django.echo', {'test_key': test_value}, request=mock_request)

        received = self._get_received()

        entry_count = received['count']
        self.assertGreaterEqual(entry_count, 1)

        first_entry = received['entries'][0]

        self.assertEqual(first_entry['x-zato-user'], 'testuser_' + test_value)

# ################################################################################################################################

    def test_invoke_with_request_propagates_correlation_id(self) -> 'None':
        """ When a Django request is passed, a correlation ID is auto-generated and arrives.
        """

        # Zato
        from django_zato import client

        test_value = os.urandom(8).hex()
        mock_request = self._make_mock_request(remote_addr='10.0.0.1')

        _ = client.invoke('test.django.echo', {'test_key': test_value}, request=mock_request)

        received = self._get_received()

        entry_count = received['count']
        self.assertGreaterEqual(entry_count, 1)

        first_entry = received['entries'][0]
        correlation_id = first_entry['x-zato-correlation-id']

        # .. the correlation ID should be a non-empty hex string (uuid4 without dashes) ..
        self.assertTrue(correlation_id)

        correlation_id_len = len(correlation_id)
        self.assertEqual(correlation_id_len, 32)

# ################################################################################################################################

    def test_invoke_with_request_propagates_forwarded_for(self) -> 'None':
        """ When a Django request with REMOTE_ADDR is passed, X-Zato-Forwarded-For arrives.
        """

        # Zato
        from django_zato import client

        test_value = os.urandom(8).hex()
        mock_request = self._make_mock_request(remote_addr='192.168.1.42')

        _ = client.invoke('test.django.echo', {'test_key': test_value}, request=mock_request)

        received = self._get_received()

        entry_count = received['count']
        self.assertGreaterEqual(entry_count, 1)

        first_entry = received['entries'][0]

        self.assertEqual(first_entry['x-zato-forwarded-for'], '192.168.1.42')

# ################################################################################################################################

    def test_invoke_with_request_preserves_incoming_correlation_id(self) -> 'None':
        """ When the Django request already has a correlation ID, it is forwarded unchanged.
        """

        # Zato
        from django_zato import client

        test_value = os.urandom(8).hex()
        known_correlation_id = os.urandom(16).hex()
        mock_request = self._make_mock_request(
            remote_addr='10.0.0.1',
            correlation_id=known_correlation_id,
        )

        _ = client.invoke('test.django.echo', {'test_key': test_value}, request=mock_request)

        received = self._get_received()

        entry_count = received['count']
        self.assertGreaterEqual(entry_count, 1)

        first_entry = received['entries'][0]

        self.assertEqual(first_entry['x-zato-correlation-id'], known_correlation_id)

# ################################################################################################################################

    def test_middleware_stores_request(self) -> 'None':
        """ ZatoMiddleware stores the request in ContextVar during view execution and clears it after.
        """

        # Zato
        from django_zato.ctx import get_request
        from django_zato.middleware import ZatoMiddleware

        mock_request = self._make_mock_request(username='middleware_user')
        captured_request = None

        def mock_get_response(request:'any_') -> 'any_':
            nonlocal captured_request
            captured_request = get_request()
            return 'response'

        middleware = ZatoMiddleware(mock_get_response)
        _ = middleware(mock_request)

        # .. during the view, the request should have been available ..
        self.assertIs(captured_request, mock_request)

        # .. after the middleware call, it should be cleared ..
        after_request = get_request()
        self.assertIsNone(after_request)

# ################################################################################################################################

    def test_invoke_without_request_no_headers(self) -> 'None':
        """ When invoke is called without a request and without middleware, no context headers are sent.
        """

        # Zato
        from django_zato.ctx import clear_request
        from django_zato import client

        # .. make sure no request is in context ..
        clear_request()

        test_value = os.urandom(8).hex()

        _ = client.invoke('test.django.echo', {'test_key': test_value})

        received = self._get_received()

        entry_count = received['count']
        self.assertGreaterEqual(entry_count, 1)

        first_entry = received['entries'][0]

        self.assertEqual(first_entry['x-zato-user'], '')
        self.assertEqual(first_entry['x-zato-correlation-id'], '')
        self.assertEqual(first_entry['x-zato-forwarded-for'], '')

# ################################################################################################################################
# ################################################################################################################################
