# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.bearer_token_verifier import build_verify_config, extract_bearer_token, parse_claims

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

class ExtractBearerToken(TestCase):
    """ Extraction of tokens from Authorization headers with a case-insensitive Bearer prefix.
    """

    def test_lowercase_prefix(self) -> 'None':
        out = extract_bearer_token('bearer test-token-value')
        self.assertEqual(out, 'test-token-value')

# ################################################################################################################################

    def test_capitalized_prefix(self) -> 'None':
        out = extract_bearer_token('Bearer test-token-value')
        self.assertEqual(out, 'test-token-value')

# ################################################################################################################################

    def test_uppercase_prefix(self) -> 'None':
        out = extract_bearer_token('BEARER test-token-value')
        self.assertEqual(out, 'test-token-value')

# ################################################################################################################################

    def test_surrounding_whitespace_is_stripped(self) -> 'None':
        out = extract_bearer_token('Bearer   test-token-value  ')
        self.assertEqual(out, 'test-token-value')

# ################################################################################################################################

    def test_empty_header(self) -> 'None':
        out = extract_bearer_token('')
        self.assertEqual(out, '')

# ################################################################################################################################

    def test_basic_auth_header_does_not_match(self) -> 'None':
        out = extract_bearer_token('Basic dGVzdC11c2VyOnRlc3QtcGFzc3dvcmQ=')
        self.assertEqual(out, '')

# ################################################################################################################################

    def test_prefix_without_token(self) -> 'None':
        out = extract_bearer_token('Bearer ')
        self.assertEqual(out, '')

# ################################################################################################################################
# ################################################################################################################################

class ParseClaims(TestCase):
    """ Claims configuration arrives as a dict, a list of name=value entries or a multi-line string.
    """

    def test_dict_is_used_as_is(self) -> 'None':
        out = parse_claims({'department': 'Accounting'})
        self.assertEqual(out, {'department': 'Accounting'})

# ################################################################################################################################

    def test_list_of_name_value_entries(self) -> 'None':
        out = parse_claims(['department=Accounting', 'region=test-east'])
        self.assertEqual(out, {'department': 'Accounting', 'region': 'test-east'})

# ################################################################################################################################

    def test_multi_line_string(self) -> 'None':
        out = parse_claims('department=Accounting\nregion=test-east')
        self.assertEqual(out, {'department': 'Accounting', 'region': 'test-east'})

# ################################################################################################################################

    def test_empty_input(self) -> 'None':
        out = parse_claims(None)
        self.assertEqual(out, {})

# ################################################################################################################################
# ################################################################################################################################

class BuildVerifyConfig(TestCase):
    """ Building a verification config out of a security definition, with derived defaults.
    """

    def _make_sec_def(self) -> 'stranydict':
        out:'stranydict' = {
            'id': 123,
            'name': 'test.bearer.def',
        }
        return out

# ################################################################################################################################

    def test_explicit_fields_are_used(self) -> 'None':
        sec_def = self._make_sec_def()
        sec_def['issuer'] = 'https://idp.example.com/realms/test'
        sec_def['jwks_url'] = 'https://idp.example.com/realms/test/certs'
        sec_def['audience'] = 'test-audience'
        sec_def['claims'] = ['department=Accounting']

        out = build_verify_config(sec_def)

        self.assertEqual(out.security_id, 123)
        self.assertEqual(out.sec_def_name, 'test.bearer.def')
        self.assertEqual(out.issuer, 'https://idp.example.com/realms/test')
        self.assertEqual(out.jwks_url, 'https://idp.example.com/realms/test/certs')
        self.assertEqual(out.audience, 'test-audience')
        self.assertEqual(out.claims, {'department': 'Accounting'})

# ################################################################################################################################

    def test_issuer_derived_from_auth_server_url(self) -> 'None':
        sec_def = self._make_sec_def()
        sec_def['auth_server_url'] = 'https://idp.example.com/realms/test/protocol/openid-connect/token'

        out = build_verify_config(sec_def)

        self.assertEqual(out.issuer, 'https://idp.example.com')

# ################################################################################################################################

    def test_jwks_url_derived_from_issuer(self) -> 'None':
        sec_def = self._make_sec_def()
        sec_def['issuer'] = 'https://idp.example.com/realms/test'

        out = build_verify_config(sec_def)

        self.assertEqual(out.jwks_url, 'https://idp.example.com/realms/test/.well-known/openid-configuration')

# ################################################################################################################################

    def test_static_definition(self) -> 'None':
        sec_def = self._make_sec_def()
        sec_def['static_token'] = 'test-static-token'

        out = build_verify_config(sec_def)

        self.assertEqual(out.static_token, 'test-static-token')
        self.assertEqual(out.audience, '')

# ################################################################################################################################

    def test_outgoing_only_definition(self) -> 'None':
        """ A definition with no inbound fields at all builds a config that never matches inbound traffic.
        """
        sec_def = self._make_sec_def()

        out = build_verify_config(sec_def)

        self.assertEqual(out.static_token, '')
        self.assertEqual(out.issuer, '')
        self.assertEqual(out.jwks_url, '')
        self.assertEqual(out.audience, '')
        self.assertEqual(out.claims, {})

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
