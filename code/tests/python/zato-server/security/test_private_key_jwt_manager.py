# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from json import loads
from unittest import main, TestCase

# PyJWT
import jwt

# Make the shared test helpers importable
sys.path.insert(0, os.path.dirname(__file__))

# Zato
from private_key_jwt_helpers import Client_Secret, FakeTokenEndpoint, make_manager, make_private_key_jwt_sec_def, \
    make_sec_def, Token_Prefix
from zato.common.api import OAuth
from zato.common.exception import BackendInvocationError
from zato.common.private_key_jwt import PrivateKeyJWTError
from zato.common.test.private_key_jwt import generate_ec_private_key_pem, generate_rsa_private_key_pem, \
    generate_self_signed_certificate_pem

# ################################################################################################################################
# ################################################################################################################################

Key_ID = 'test-key-id'
Auth0_Audience = 'https://test-tenant.auth0.com/'

# ################################################################################################################################
# ################################################################################################################################

class TokenRequestBody(TestCase):
    """ What leaves the server for the token endpoint under each authentication method.
    """

    def setUp(self) -> 'None':
        self.endpoint = FakeTokenEndpoint()
        self.endpoint.start()
        self.manager, self.server = make_manager()

    def tearDown(self) -> 'None':
        self.endpoint.stop()

# ################################################################################################################################

    def _get_token(self, sec_def:'dict', scopes:'str'='', data_format:'str'='form') -> 'str':
        result = self.manager._get_bearer_token_info(sec_def, scopes, data_format)
        out = result.info.token
        return out

# ################################################################################################################################

    def test_client_secret_body(self) -> 'None':
        sec_def = make_sec_def(self.endpoint)
        token = self._get_token(sec_def)

        self.assertTrue(token.startswith(Token_Prefix))

        body = self.endpoint.requests[0].body
        self.assertEqual(body['client_secret'], Client_Secret)
        self.assertNotIn('client_assertion', body)
        self.assertNotIn('client_assertion_type', body)

# ################################################################################################################################

    def test_private_key_jwt_body(self) -> 'None':
        private_key_pem = generate_rsa_private_key_pem()
        self.endpoint.register_private_key(private_key_pem, Key_ID)

        sec_def = make_private_key_jwt_sec_def(self.endpoint, private_key_pem, OAuth.JWT_Algorithm.RS384, Key_ID)
        token = self._get_token(sec_def)

        self.assertTrue(token.startswith(Token_Prefix))

        body = self.endpoint.requests[0].body
        self.assertEqual(body['client_id'], sec_def['username'])
        self.assertEqual(body['grant_type'], OAuth.Default.Grant_Type)
        self.assertEqual(body['client_assertion_type'], OAuth.Assertion_Type)
        self.assertNotIn('client_secret', body)

        header = jwt.get_unverified_header(body['client_assertion'])
        self.assertEqual(header['alg'], OAuth.JWT_Algorithm.RS384)
        self.assertEqual(header['kid'], Key_ID)

# ################################################################################################################################

    def test_custom_client_secret_field_is_not_sent(self) -> 'None':
        """ A renamed secret field still stays home when assertions are in use.
        """
        private_key_pem = generate_rsa_private_key_pem()
        self.endpoint.register_private_key(private_key_pem)

        sec_def = make_private_key_jwt_sec_def(self.endpoint, private_key_pem, client_secret_field='app_secret')
        _ = self._get_token(sec_def)

        body = self.endpoint.requests[0].body
        self.assertNotIn('app_secret', body)
        self.assertNotIn('client_secret', body)

# ################################################################################################################################

    def test_json_body(self) -> 'None':
        private_key_pem = generate_rsa_private_key_pem()
        self.endpoint.register_private_key(private_key_pem)

        sec_def = make_private_key_jwt_sec_def(self.endpoint, private_key_pem, data_format='json')
        _ = self._get_token(sec_def, data_format='json')

        request = self.endpoint.requests[0]
        self.assertTrue(request.headers['Content-Type'].startswith('application/json'))
        self.assertIn('client_assertion', request.body)

# ################################################################################################################################

    def test_scopes_are_sent(self) -> 'None':
        private_key_pem = generate_rsa_private_key_pem()
        self.endpoint.register_private_key(private_key_pem)

        sec_def = make_private_key_jwt_sec_def(self.endpoint, private_key_pem, scopes='system/Patient.read\nsystem/Observation.read')
        _ = self._get_token(sec_def)

        body = self.endpoint.requests[0].body
        self.assertEqual(body['scope'], 'system/Patient.read system/Observation.read')

# ################################################################################################################################

    def test_es384(self) -> 'None':
        private_key_pem = generate_ec_private_key_pem()
        self.endpoint.register_private_key(private_key_pem, Key_ID)

        sec_def = make_private_key_jwt_sec_def(self.endpoint, private_key_pem, OAuth.JWT_Algorithm.ES384, Key_ID)
        token = self._get_token(sec_def)

        self.assertTrue(token.startswith(Token_Prefix))

        header = jwt.get_unverified_header(self.endpoint.requests[0].body['client_assertion'])
        self.assertEqual(header['alg'], OAuth.JWT_Algorithm.ES384)

# ################################################################################################################################

    def test_ps256_with_certificate(self) -> 'None':
        private_key_pem = generate_rsa_private_key_pem()
        certificate_pem = generate_self_signed_certificate_pem(private_key_pem)
        self.endpoint.register_private_key(private_key_pem)

        sec_def = make_private_key_jwt_sec_def(
            self.endpoint, private_key_pem, OAuth.JWT_Algorithm.PS256, certificate=certificate_pem)
        _ = self._get_token(sec_def)

        header = jwt.get_unverified_header(self.endpoint.requests[0].body['client_assertion'])
        self.assertEqual(header['alg'], OAuth.JWT_Algorithm.PS256)
        self.assertIn('x5t', header)
        self.assertIn('x5t#S256', header)

# ################################################################################################################################

    def test_assertion_audience_override(self) -> 'None':
        """ Auth0 wants its tenant URL as the audience rather than the token endpoint.
        """
        private_key_pem = generate_rsa_private_key_pem()
        self.endpoint.register_private_key(private_key_pem)
        self.endpoint.expected_audience = Auth0_Audience

        sec_def = make_private_key_jwt_sec_def(self.endpoint, private_key_pem, assertion_audience=Auth0_Audience)
        token = self._get_token(sec_def)

        self.assertTrue(token.startswith(Token_Prefix))

        claims = jwt.decode(self.endpoint.requests[0].body['client_assertion'], options={'verify_signature': False})
        self.assertEqual(claims['aud'], Auth0_Audience)

# ################################################################################################################################

    def test_default_audience_is_the_token_endpoint(self) -> 'None':
        private_key_pem = generate_rsa_private_key_pem()
        self.endpoint.register_private_key(private_key_pem)

        sec_def = make_private_key_jwt_sec_def(self.endpoint, private_key_pem)
        _ = self._get_token(sec_def)

        claims = jwt.decode(self.endpoint.requests[0].body['client_assertion'], options={'verify_signature': False})
        self.assertEqual(claims['aud'], self.endpoint.url)

# ################################################################################################################################

    def test_unknown_key_id_is_an_error(self) -> 'None':
        private_key_pem = generate_rsa_private_key_pem()
        self.endpoint.register_private_key(private_key_pem, Key_ID)

        sec_def = make_private_key_jwt_sec_def(self.endpoint, private_key_pem, key_id='not-registered')

        with self.assertRaises(BackendInvocationError) as ctx:
            _ = self._get_token(sec_def)

        self.assertIn('Unknown key ID', str(ctx.exception))

# ################################################################################################################################

    def test_unregistered_key_is_an_error(self) -> 'None':
        self.endpoint.register_private_key(generate_rsa_private_key_pem())

        sec_def = make_private_key_jwt_sec_def(self.endpoint, generate_rsa_private_key_pem())

        with self.assertRaises(BackendInvocationError) as ctx:
            _ = self._get_token(sec_def)

        self.assertIn('Assertion rejected', str(ctx.exception))

# ################################################################################################################################

    def test_missing_private_key_is_an_error(self) -> 'None':
        sec_def = make_private_key_jwt_sec_def(self.endpoint, '')

        with self.assertRaises(PrivateKeyJWTError) as ctx:
            _ = self._get_token(sec_def)

        self.assertIn('has no private key', str(ctx.exception))
        self.assertEqual(len(self.endpoint.requests), 0)

# ################################################################################################################################

    def test_definition_without_method_is_client_secret(self) -> 'None':
        """ Definitions created before the method existed carry none of its fields and keep sending their secret.
        """
        sec_def = make_sec_def(self.endpoint)
        for name in ('client_auth_method', 'private_key', 'jwt_algorithm', 'key_id', 'assertion_audience', 'certificate'):
            self.assertNotIn(name, sec_def)

        config = self.manager._get_bearer_token_config(sec_def)

        self.assertEqual(config.client_auth_method, OAuth.Client_Auth_Method.Client_Secret)
        self.assertEqual(config.jwt_algorithm, OAuth.Default.JWT_Algorithm)
        self.assertEqual(config.private_key, '')

        _ = self._get_token(sec_def)
        self.assertEqual(self.endpoint.requests[0].body['client_secret'], Client_Secret)

# ################################################################################################################################
# ################################################################################################################################

class KeyAndTokenCaching(TestCase):
    """ The parsed key and the token are both reused until the definition changes.
    """

    def setUp(self) -> 'None':
        self.endpoint = FakeTokenEndpoint()
        self.endpoint.start()
        self.manager, self.server = make_manager()

        self.private_key_pem = generate_rsa_private_key_pem()
        self.endpoint.register_private_key(self.private_key_pem, Key_ID)
        self.sec_def = make_private_key_jwt_sec_def(self.endpoint, self.private_key_pem, OAuth.JWT_Algorithm.RS384, Key_ID)

    def tearDown(self) -> 'None':
        self.endpoint.stop()

# ################################################################################################################################

    def _get_result(self, scopes:'str'='') -> 'tuple':
        result = self.manager._get_bearer_token_info(self.sec_def, scopes, 'form')
        out = result.info.token, result.is_cache_hit
        return out

# ################################################################################################################################

    def test_token_is_served_from_cache(self) -> 'None':
        token1, is_hit1 = self._get_result()
        token2, is_hit2 = self._get_result()

        self.assertFalse(is_hit1)
        self.assertTrue(is_hit2)
        self.assertEqual(token1, token2)
        self.assertEqual(len(self.endpoint.requests), 1)

# ################################################################################################################################

    def test_key_is_decrypted_and_parsed_once(self) -> 'None':
        _ = self._get_result('scope-a')
        _ = self._get_result('scope-b')

        self.assertEqual(len(self.endpoint.requests), 2)
        self.assertEqual(self.server.decrypt_calls, 1)

# ################################################################################################################################

    def test_invalidation_drops_token_and_key(self) -> 'None':
        token1, _ = self._get_result()
        self.manager.invalidate(self.sec_def['name'])

        token2, is_hit2 = self._get_result()

        self.assertFalse(is_hit2)
        self.assertNotEqual(token1, token2)
        self.assertEqual(len(self.endpoint.requests), 2)
        self.assertEqual(self.server.decrypt_calls, 2)

# ################################################################################################################################

    def test_cache_key_carries_the_revision(self) -> 'None':
        key_before = self.manager._get_cache_key(self.sec_def['name'], '')
        self.manager.invalidate(self.sec_def['name'])
        key_after = self.manager._get_cache_key(self.sec_def['name'], '')

        self.assertNotEqual(key_before, key_after)

# ################################################################################################################################

    def test_changed_key_text_is_parsed_anew(self) -> 'None':
        _ = self._get_result('scope-a')

        rotated_pem = generate_rsa_private_key_pem()
        self.endpoint.register_private_key(rotated_pem, Key_ID)
        self.sec_def['private_key'] = rotated_pem

        _ = self._get_result('scope-b')

        self.assertEqual(self.server.decrypt_calls, 2)
        self.assertEqual(len(self.endpoint.requests), 2)

# ################################################################################################################################
# ################################################################################################################################

class GetTokenFromRawParams(TestCase):
    """ The Dashboard's Get token link sends the form's fields as raw parameters.
    """

    def setUp(self) -> 'None':
        self.endpoint = FakeTokenEndpoint()
        self.endpoint.start()
        self.manager, self.server = make_manager()

    def tearDown(self) -> 'None':
        self.endpoint.stop()

# ################################################################################################################################

    def _raw_params(self, **extra:'str') -> 'dict':
        out = {
            'name': 'test.raw',
            'username': make_sec_def(self.endpoint)['username'],
            'secret': '',
            'auth_server_url': self.endpoint.url,
            'client_id_field': OAuth.Default.Client_ID_Field,
            'client_secret_field': OAuth.Default.Client_Secret_Field,
            'grant_type': OAuth.Default.Grant_Type,
            'data_format': 'form',
        }
        out.update(extra)
        return out

# ################################################################################################################################

    def test_private_key_from_form(self) -> 'None':
        private_key_pem = generate_rsa_private_key_pem()
        self.endpoint.register_private_key(private_key_pem)

        raw_params = self._raw_params(
            client_auth_method=OAuth.Client_Auth_Method.Private_Key_JWT,
            private_key=private_key_pem,
            jwt_algorithm=OAuth.JWT_Algorithm.RS384,
        )

        response = loads(self.manager.get_bearer_token_from_odb(None, '', raw_params))

        self.assertTrue(response['is_ok'])
        self.assertTrue(response['token'].startswith(Token_Prefix))

# ################################################################################################################################

    def test_bad_key_from_form_is_reported(self) -> 'None':
        raw_params = self._raw_params(
            client_auth_method=OAuth.Client_Auth_Method.Private_Key_JWT,
            private_key='not a key',
            jwt_algorithm=OAuth.JWT_Algorithm.RS384,
        )

        response = loads(self.manager.get_bearer_token_from_odb(None, '', raw_params))

        self.assertFalse(response['is_ok'])
        self.assertIn('could not be parsed', response['response_body'])

# ################################################################################################################################

    def test_client_secret_from_form(self) -> 'None':
        raw_params = self._raw_params(secret=Client_Secret)

        response = loads(self.manager.get_bearer_token_from_odb(None, '', raw_params))

        self.assertTrue(response['is_ok'])
        self.assertEqual(self.endpoint.requests[0].body['client_secret'], Client_Secret)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
