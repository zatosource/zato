# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from http.client import BAD_REQUEST, OK, UNAUTHORIZED
from unittest import main, TestCase

# Requests
import requests

# Make the shared test helpers importable
sys.path.insert(0, os.path.dirname(__file__))

# Zato
from private_key_jwt_helpers import Client_ID, Client_Secret, make_manager
from zato.common.api import OAuth
from zato.common.exception import BackendInvocationError
from zato.common.private_key_jwt import build_assertion, get_public_key_pem, load_private_key
from zato.common.test.fhir import FHIRTestServer
from zato.common.test.fhir.common import auth_type_oauth
from zato.common.test.private_key_jwt import generate_rsa_private_key_pem

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

Key_ID = 'fhir-test-key'

# Timeout for HTTP requests to the fake server, in seconds
_http_timeout = 10

# ################################################################################################################################
# ################################################################################################################################

class FHIRFakeServerPrivateKeyJWT(TestCase):
    """ The fake FHIR server's token endpoint accepts a client assertion the way SMART Backend Services do,
    and the token manager logs in to it with a private key JWT definition.
    """

    def setUp(self) -> 'None':
        self.private_key_pem = generate_rsa_private_key_pem()
        self.private_key = load_private_key(self.private_key_pem)
        public_key_pem = get_public_key_pem(self.private_key)

        self.server = FHIRTestServer(Client_ID, Client_Secret, auth_type_oauth, public_key_pem=public_key_pem)
        self.server.start()

        _ = self.server.import_resource({'resourceType': 'Patient', 'id': 'pkjwt-1', 'active': True})

    def tearDown(self) -> 'None':
        self.server.stop()

# ################################################################################################################################

    def _make_sec_def(self, **extra:'any_') -> 'stranydict':
        """ A private key JWT definition pointed at the fake server's token endpoint.
        """
        out:'stranydict' = {
            'name': 'test.bearer.fhir.private.key.jwt',
            'username': Client_ID,
            'password': '',
            'auth_server_url': self.server.token_endpoint,
            'client_id_field': OAuth.Default.Client_ID_Field,
            'client_secret_field': OAuth.Default.Client_Secret_Field,
            'grant_type': OAuth.Default.Grant_Type,
            'scopes': '',
            'extra_fields': '',
            'data_format': 'form',
            'client_auth_method': OAuth.Client_Auth_Method.Private_Key_JWT,
            'private_key': self.private_key_pem,
            'jwt_algorithm': OAuth.JWT_Algorithm.RS384,
            'key_id': Key_ID,
        }
        out.update(extra)
        return out

# ################################################################################################################################

    def _post_token_request(self, body:'stranydict') -> 'any_':
        out = requests.post(self.server.token_endpoint, data=body, timeout=_http_timeout)
        return out

# ################################################################################################################################

    def _make_assertion_request(self, audience:'str'='') -> 'stranydict':
        """ A token request carrying a freshly signed assertion for the fake server.
        """
        if not audience:
            audience = self.server.token_endpoint

        assertion = build_assertion(self.private_key, OAuth.JWT_Algorithm.RS384, Client_ID, audience, Key_ID)

        out = {
            'grant_type': OAuth.Default.Grant_Type,
            'client_id': Client_ID,
            'client_assertion_type': OAuth.Assertion_Type,
            'client_assertion': assertion,
        }
        return out

# ################################################################################################################################

    def test_manager_logs_in_with_an_assertion(self) -> 'None':

        manager, _ = make_manager()
        sec_def = self._make_sec_def()

        result = manager._get_bearer_token_info(sec_def, '', 'form')

        self.assertFalse(result.is_cache_hit)
        self.assertTrue(result.info.token)

        # The token the fake server issued opens its resources
        headers = {'Authorization': f'Bearer {result.info.token}'}
        response = requests.get(f'{self.server.address}/Patient/pkjwt-1', headers=headers, timeout=_http_timeout)

        self.assertEqual(response.status_code, OK, response.text)

# ################################################################################################################################

    def test_manager_with_a_wrong_key_is_refused(self) -> 'None':

        manager, _ = make_manager()
        sec_def = self._make_sec_def(private_key=generate_rsa_private_key_pem())

        with self.assertRaises(BackendInvocationError) as ctx:
            _ = manager._get_bearer_token_info(sec_def, '', 'form')

        self.assertIn('invalid_client', str(ctx.exception))
        self.assertIn('Signature verification failed', str(ctx.exception))

# ################################################################################################################################

    def test_assertion_is_good_once_only(self) -> 'None':

        request = self._make_assertion_request()

        first = self._post_token_request(request)
        second = self._post_token_request(request)

        self.assertEqual(first.status_code, OK, first.text)
        self.assertEqual(second.status_code, BAD_REQUEST, second.text)

        error = second.json()

        self.assertEqual(error['error'], 'invalid_client')
        self.assertIn('replayed', error['error_description'])

# ################################################################################################################################

    def test_wrong_audience_is_refused(self) -> 'None':

        request = self._make_assertion_request(audience='https://example.com/not-this-server')
        response = self._post_token_request(request)

        self.assertEqual(response.status_code, BAD_REQUEST, response.text)
        self.assertIn('Audience', response.json()['error_description'])

# ################################################################################################################################

    def test_secret_and_assertion_together_are_refused(self) -> 'None':

        request = self._make_assertion_request()
        request['client_secret'] = Client_Secret

        response = self._post_token_request(request)

        self.assertEqual(response.status_code, BAD_REQUEST, response.text)
        self.assertIn('Both', response.json()['error_description'])

# ################################################################################################################################

    def test_unknown_assertion_type_is_refused(self) -> 'None':

        request = self._make_assertion_request()
        request['client_assertion_type'] = 'urn:ietf:params:oauth:client-assertion-type:saml2-bearer'

        response = self._post_token_request(request)

        self.assertEqual(response.status_code, BAD_REQUEST, response.text)
        self.assertIn('Unsupported client assertion type', response.json()['error_description'])

# ################################################################################################################################

    def test_secret_login_still_works(self) -> 'None':

        response = self._post_token_request({
            'grant_type': OAuth.Default.Grant_Type,
            'client_id': Client_ID,
            'client_secret': Client_Secret,
        })

        self.assertEqual(response.status_code, OK, response.text)
        self.assertTrue(response.json()['access_token'])

# ################################################################################################################################

    def test_resources_stay_closed_without_a_token(self) -> 'None':

        response = requests.get(f'{self.server.address}/Patient/pkjwt-1', timeout=_http_timeout)

        self.assertEqual(response.status_code, UNAUTHORIZED, response.text)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
