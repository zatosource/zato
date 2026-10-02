# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import urlsafe_b64decode
from hashlib import sha1, sha256
from unittest import main, TestCase

# cryptography
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509 import load_pem_x509_certificate

# PyJWT
import jwt

# Zato
from zato.common.api import OAuth
from zato.common.private_key_jwt import build_assertion, build_assertion_claims, get_public_jwk, get_public_key_pem, \
    get_thumbprint_headers, load_private_key, PrivateKeyJWTError, validate_definition
from zato.common.test.private_key_jwt import generate_ec_private_key_pem, generate_rsa_private_key_pem, \
    generate_self_signed_certificate_pem

# ################################################################################################################################
# ################################################################################################################################

Client_ID = 'test-client-id'
Audience = 'https://auth.example.com/oauth2/token'
Key_ID = 'test-key-id'

# How many distinct assertions are signed when checking that each jti is unique
Unique_JTI_Sample_Size = 50

# ################################################################################################################################
# ################################################################################################################################

def _unpad_base64url(value:'str') -> 'bytes':
    padding = '=' * (-len(value) % 4)
    out = urlsafe_b64decode(value + padding)
    return out

# ################################################################################################################################
# ################################################################################################################################

class AssertionClaims(TestCase):
    """ The claims of a client assertion follow RFC 7523 - iss and sub are the client ID, aud is the token endpoint
    and the assertion is short-lived with a jti of its own.
    """

    def test_claims(self) -> 'None':
        out = build_assertion_claims(Client_ID, Audience)

        self.assertEqual(out['iss'], Client_ID)
        self.assertEqual(out['sub'], Client_ID)
        self.assertEqual(out['aud'], Audience)
        self.assertEqual(out['exp'] - out['iat'], OAuth.Assertion_Lifetime_Seconds)
        self.assertTrue(out['jti'])

# ################################################################################################################################

    def test_custom_lifetime(self) -> 'None':
        out = build_assertion_claims(Client_ID, Audience, lifetime=60)
        self.assertEqual(out['exp'] - out['iat'], 60)

# ################################################################################################################################

    def test_jti_is_unique(self) -> 'None':
        seen = set()

        for _ in range(Unique_JTI_Sample_Size):
            claims = build_assertion_claims(Client_ID, Audience)
            seen.add(claims['jti'])

        self.assertEqual(len(seen), Unique_JTI_Sample_Size)

# ################################################################################################################################
# ################################################################################################################################

class SignedAssertion(TestCase):
    """ Signing with every supported algorithm, with the public half verifying what the private half signed.
    """

    def _sign_and_verify(self, private_key_pem:'str', jwt_algorithm:'str', key_id:'str'='') -> 'tuple':
        key = validate_definition(private_key_pem, jwt_algorithm, '')
        assertion = build_assertion(key, jwt_algorithm, Client_ID, Audience, key_id)

        header = jwt.get_unverified_header(assertion)
        public_key_pem = get_public_key_pem(key)
        claims = jwt.decode(assertion, public_key_pem, algorithms=[jwt_algorithm], audience=Audience)

        out = header, claims
        return out

# ################################################################################################################################

    def test_rsa_algorithms(self) -> 'None':
        private_key_pem = generate_rsa_private_key_pem()

        for jwt_algorithm in (OAuth.JWT_Algorithm.RS256, OAuth.JWT_Algorithm.RS384, OAuth.JWT_Algorithm.PS256):
            with self.subTest(jwt_algorithm=jwt_algorithm):
                header, claims = self._sign_and_verify(private_key_pem, jwt_algorithm)

                self.assertEqual(header['alg'], jwt_algorithm)
                self.assertEqual(claims['iss'], Client_ID)
                self.assertEqual(claims['sub'], Client_ID)
                self.assertEqual(claims['aud'], Audience)

# ################################################################################################################################

    def test_es384(self) -> 'None':
        private_key_pem = generate_ec_private_key_pem()
        header, claims = self._sign_and_verify(private_key_pem, OAuth.JWT_Algorithm.ES384)

        self.assertEqual(header['alg'], OAuth.JWT_Algorithm.ES384)
        self.assertEqual(claims['iss'], Client_ID)

# ################################################################################################################################

    def test_kid_header_when_key_id_is_set(self) -> 'None':
        private_key_pem = generate_rsa_private_key_pem()
        header, _ = self._sign_and_verify(private_key_pem, OAuth.JWT_Algorithm.RS384, Key_ID)

        self.assertEqual(header['kid'], Key_ID)

# ################################################################################################################################

    def test_no_kid_header_without_key_id(self) -> 'None':
        private_key_pem = generate_rsa_private_key_pem()
        header, _ = self._sign_and_verify(private_key_pem, OAuth.JWT_Algorithm.RS384)

        self.assertNotIn('kid', header)
        self.assertNotIn('x5t', header)

# ################################################################################################################################

    def test_expiry_is_the_configured_lifetime(self) -> 'None':
        """ A signed assertion is short-lived - its exp is iat plus the configured lifetime, nothing longer.
        """
        private_key_pem = generate_rsa_private_key_pem()
        key = load_private_key(private_key_pem)
        assertion = build_assertion(key, OAuth.JWT_Algorithm.RS384, Client_ID, Audience)

        claims = jwt.decode(assertion, get_public_key_pem(key), algorithms=[OAuth.JWT_Algorithm.RS384], audience=Audience)

        self.assertEqual(claims['exp'] - claims['iat'], OAuth.Assertion_Lifetime_Seconds)

# ################################################################################################################################

    def test_wrong_audience_does_not_verify(self) -> 'None':
        key = load_private_key(generate_rsa_private_key_pem())
        assertion = build_assertion(key, OAuth.JWT_Algorithm.RS384, Client_ID, Audience)

        with self.assertRaises(jwt.InvalidAudienceError):
            _ = jwt.decode(
                assertion, get_public_key_pem(key), algorithms=[OAuth.JWT_Algorithm.RS384], audience='https://other.example.com')

# ################################################################################################################################

    def test_another_key_does_not_verify(self) -> 'None':
        signing_key = load_private_key(generate_rsa_private_key_pem())
        other_key = load_private_key(generate_rsa_private_key_pem())

        assertion = build_assertion(signing_key, OAuth.JWT_Algorithm.RS384, Client_ID, Audience)

        with self.assertRaises(jwt.InvalidSignatureError):
            _ = jwt.decode(assertion, get_public_key_pem(other_key), algorithms=[OAuth.JWT_Algorithm.RS384], audience=Audience)

# ################################################################################################################################
# ################################################################################################################################

class ThumbprintHeaders(TestCase):
    """ Providers that register certificates find the key by x5t and x5t#S256 - both must match what cryptography computes.
    """

    def test_headers_match_certificate_digests(self) -> 'None':
        private_key_pem = generate_rsa_private_key_pem()
        certificate_pem = generate_self_signed_certificate_pem(private_key_pem)

        certificate = load_pem_x509_certificate(certificate_pem.encode('utf8'))
        der = certificate.public_bytes(Encoding.DER)

        out = get_thumbprint_headers(certificate_pem)

        self.assertEqual(_unpad_base64url(out['x5t']), sha1(der).digest())
        self.assertEqual(_unpad_base64url(out['x5t#S256']), sha256(der).digest())

# ################################################################################################################################

    def test_assertion_carries_thumbprints(self) -> 'None':
        private_key_pem = generate_rsa_private_key_pem()
        certificate_pem = generate_self_signed_certificate_pem(private_key_pem)
        key = validate_definition(private_key_pem, OAuth.JWT_Algorithm.PS256, certificate_pem)

        assertion = build_assertion(key, OAuth.JWT_Algorithm.PS256, Client_ID, Audience, Key_ID, certificate_pem)
        header = jwt.get_unverified_header(assertion)

        expected = get_thumbprint_headers(certificate_pem)

        self.assertEqual(header['alg'], OAuth.JWT_Algorithm.PS256)
        self.assertEqual(header['kid'], Key_ID)
        self.assertEqual(header['x5t'], expected['x5t'])
        self.assertEqual(header['x5t#S256'], expected['x5t#S256'])

# ################################################################################################################################
# ################################################################################################################################

class Validation(TestCase):
    """ What a definition is rejected for before it is stored.
    """

    def test_unparseable_pem(self) -> 'None':
        with self.assertRaises(PrivateKeyJWTError) as ctx:
            _ = validate_definition('not a key at all', OAuth.JWT_Algorithm.RS384, '')

        self.assertIn('could not be parsed', str(ctx.exception))

# ################################################################################################################################

    def test_unknown_algorithm(self) -> 'None':
        with self.assertRaises(PrivateKeyJWTError) as ctx:
            _ = validate_definition(generate_rsa_private_key_pem(), 'HS256', '')

        self.assertIn('Unknown JWT algorithm', str(ctx.exception))

# ################################################################################################################################

    def test_ec_key_with_rsa_algorithm(self) -> 'None':
        with self.assertRaises(PrivateKeyJWTError) as ctx:
            _ = validate_definition(generate_ec_private_key_pem(), OAuth.JWT_Algorithm.RS256, '')

        self.assertIn('needs an RSA private key', str(ctx.exception))

# ################################################################################################################################

    def test_rsa_key_with_ec_algorithm(self) -> 'None':
        with self.assertRaises(PrivateKeyJWTError) as ctx:
            _ = validate_definition(generate_rsa_private_key_pem(), OAuth.JWT_Algorithm.ES384, '')

        self.assertIn('needs an EC private key', str(ctx.exception))

# ################################################################################################################################

    def test_certificate_of_another_key(self) -> 'None':
        private_key_pem = generate_rsa_private_key_pem()
        other_certificate_pem = generate_self_signed_certificate_pem(generate_rsa_private_key_pem())

        with self.assertRaises(PrivateKeyJWTError) as ctx:
            _ = validate_definition(private_key_pem, OAuth.JWT_Algorithm.RS384, other_certificate_pem)

        self.assertIn('does not match', str(ctx.exception))

# ################################################################################################################################

    def test_unparseable_certificate(self) -> 'None':
        with self.assertRaises(PrivateKeyJWTError) as ctx:
            _ = validate_definition(generate_rsa_private_key_pem(), OAuth.JWT_Algorithm.RS384, 'not a certificate')

        self.assertIn('Certificate could not be parsed', str(ctx.exception))

# ################################################################################################################################

    def test_matching_certificate_is_accepted(self) -> 'None':
        private_key_pem = generate_rsa_private_key_pem()
        certificate_pem = generate_self_signed_certificate_pem(private_key_pem)

        key = validate_definition(private_key_pem, OAuth.JWT_Algorithm.RS384, certificate_pem)
        self.assertIsNotNone(key)

# ################################################################################################################################
# ################################################################################################################################

class PublicKeyMaterial(TestCase):
    """ The public half handed to administrators for registration with the authorization server.
    """

    def test_rsa_jwk(self) -> 'None':
        key = load_private_key(generate_rsa_private_key_pem())
        out = get_public_jwk(key, OAuth.JWT_Algorithm.RS384, Key_ID)

        self.assertEqual(out['kty'], 'RSA')
        self.assertEqual(out['alg'], OAuth.JWT_Algorithm.RS384)
        self.assertEqual(out['use'], 'sig')
        self.assertEqual(out['kid'], Key_ID)
        self.assertIn('n', out)
        self.assertIn('e', out)
        self.assertNotIn('d', out)

# ################################################################################################################################

    def test_ec_jwk(self) -> 'None':
        key = load_private_key(generate_ec_private_key_pem())
        out = get_public_jwk(key, OAuth.JWT_Algorithm.ES384)

        self.assertEqual(out['kty'], 'EC')
        self.assertEqual(out['crv'], 'P-384')
        self.assertNotIn('kid', out)
        self.assertNotIn('d', out)

# ################################################################################################################################

    def test_public_pem_verifies_signatures(self) -> 'None':
        key = load_private_key(generate_rsa_private_key_pem())
        assertion = build_assertion(key, OAuth.JWT_Algorithm.RS256, Client_ID, Audience)

        public_key_pem = get_public_key_pem(key)
        self.assertIn('BEGIN PUBLIC KEY', public_key_pem)

        claims = jwt.decode(assertion, public_key_pem, algorithms=[OAuth.JWT_Algorithm.RS256], audience=Audience)
        self.assertEqual(claims['iss'], Client_ID)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
