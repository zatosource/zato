# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from datetime import datetime, timedelta, timezone
from unittest import main, TestCase

# PyJWT
from jwt import encode as jwt_encode

# Zato
from zato.common.bearer_token_verifier import JWKS_Cache_TTL

# The directory with the shared bearer token test helpers
_this_directory = os.path.dirname(__file__)
sys.path.insert(0, _this_directory)

# Zato - test helpers
from bearer_token_helpers import FakeCache, make_config, make_jwk, make_token, make_verifier, \
    Issuer, Rotated_Key, Rotated_Key_ID, Signing_Key, Signing_Key_ID, Unpublished_Key  # noqa: E402

# ################################################################################################################################
# ################################################################################################################################

_cid = 'test-cid-1'
_channel_name = 'test.channel'

# How many seconds into the future test tokens expire by default
_default_expires_in = 300

# ################################################################################################################################
# ################################################################################################################################

class StaticTokenVerification(TestCase):
    """ Static bearer tokens are compared in constant time against the configured value.
    """

    def test_static_token_match(self) -> 'None':
        config = make_config(static_token='test-static-token', audience='')
        verifier = make_verifier()

        claims = verifier.verify(_cid, _channel_name, 'test-static-token', config)

        self.assertEqual(claims, {})

# ################################################################################################################################

    def test_static_token_mismatch(self) -> 'None':
        config = make_config(static_token='test-static-token', audience='')
        verifier = make_verifier()

        claims = verifier.verify(_cid, _channel_name, 'test-wrong-token', config)

        self.assertIsNone(claims)

# ################################################################################################################################

    def test_static_token_takes_precedence_over_jwt(self) -> 'None':
        """ A definition with both a static token and an audience is checked in static mode.
        """
        config = make_config(static_token='test-static-token')
        verifier = make_verifier()

        # A perfectly valid JWT must not match a static definition
        token = make_token(Signing_Key)
        claims = verifier.verify(_cid, _channel_name, token, config)

        self.assertIsNone(claims)

# ################################################################################################################################

    def test_outgoing_only_definition_never_matches(self) -> 'None':
        """ A definition with neither a static token nor an audience is outgoing-only.
        """
        config = make_config(audience='')
        verifier = make_verifier()

        token = make_token(Signing_Key)
        claims = verifier.verify(_cid, _channel_name, token, config)

        self.assertIsNone(claims)

# ################################################################################################################################
# ################################################################################################################################

class JWTVerification(TestCase):
    """ JWT verification - signature, expiry, issuer, audience and the pinned algorithm.
    """

    def test_valid_token(self) -> 'None':
        config = make_config()
        verifier = make_verifier()

        token = make_token(Signing_Key, extra_claims={'department': 'Accounting'})
        claims = verifier.verify(_cid, _channel_name, token, config)

        self.assertIsNotNone(claims)
        assert claims is not None
        self.assertEqual(claims['iss'], Issuer)
        self.assertEqual(claims['department'], 'Accounting')

# ################################################################################################################################

    def test_not_a_jwt(self) -> 'None':
        config = make_config()
        verifier = make_verifier()

        claims = verifier.verify(_cid, _channel_name, 'test-not-a-jwt-at-all', config)

        self.assertIsNone(claims)

# ################################################################################################################################

    def test_wrong_algorithm(self) -> 'None':
        """ Only the pinned RS256 algorithm is accepted - HS256 tokens are rejected up front.
        """
        config = make_config()
        verifier = make_verifier()

        now = datetime.now(timezone.utc)
        expiry = now + timedelta(seconds=_default_expires_in)
        claims_in = {'iss': Issuer, 'aud': config.audience, 'exp': expiry}

        token = jwt_encode(claims_in, 'test-shared-secret-0123456789-0123456789', algorithm='HS256',
            headers={'kid': Signing_Key_ID})
        claims = verifier.verify(_cid, _channel_name, token, config)

        self.assertIsNone(claims)

# ################################################################################################################################

    def test_no_key_id(self) -> 'None':
        config = make_config()
        verifier = make_verifier()

        token = make_token(Signing_Key, key_id=None)
        claims = verifier.verify(_cid, _channel_name, token, config)

        self.assertIsNone(claims)

# ################################################################################################################################

    def test_unknown_key_id(self) -> 'None':
        config = make_config()
        verifier = make_verifier()

        token = make_token(Unpublished_Key, key_id='test-unknown-key')
        claims = verifier.verify(_cid, _channel_name, token, config)

        self.assertIsNone(claims)

# ################################################################################################################################

    def test_bad_signature(self) -> 'None':
        """ A token signed by an unpublished key but naming a published key ID must be rejected.
        """
        config = make_config()
        verifier = make_verifier()

        token = make_token(Unpublished_Key, key_id=Signing_Key_ID)
        claims = verifier.verify(_cid, _channel_name, token, config)

        self.assertIsNone(claims)

# ################################################################################################################################

    def test_expired_token(self) -> 'None':
        config = make_config()
        verifier = make_verifier()

        token = make_token(Signing_Key, expires_in=-60)
        claims = verifier.verify(_cid, _channel_name, token, config)

        self.assertIsNone(claims)

# ################################################################################################################################

    def test_wrong_audience(self) -> 'None':
        config = make_config()
        verifier = make_verifier()

        token = make_token(Signing_Key, audience='test-other-audience')
        claims = verifier.verify(_cid, _channel_name, token, config)

        self.assertIsNone(claims)

# ################################################################################################################################

    def test_wrong_issuer(self) -> 'None':
        config = make_config()
        verifier = make_verifier()

        token = make_token(Signing_Key, issuer='https://idp.example.com/realms/other')
        claims = verifier.verify(_cid, _channel_name, token, config)

        self.assertIsNone(claims)

# ################################################################################################################################
# ################################################################################################################################

class ClaimMatching(TestCase):
    """ Configured claims must all be present in the token with the required values.
    """

    def test_scalar_claim_match(self) -> 'None':
        config = make_config(claims={'department': 'Accounting'})
        verifier = make_verifier()

        token = make_token(Signing_Key, extra_claims={'department': 'Accounting'})
        claims = verifier.verify(_cid, _channel_name, token, config)

        self.assertIsNotNone(claims)

# ################################################################################################################################

    def test_scalar_claim_mismatch(self) -> 'None':
        config = make_config(claims={'department': 'Accounting'})
        verifier = make_verifier()

        token = make_token(Signing_Key, extra_claims={'department': 'Sales'})
        claims = verifier.verify(_cid, _channel_name, token, config)

        self.assertIsNone(claims)

# ################################################################################################################################

    def test_missing_claim(self) -> 'None':
        config = make_config(claims={'department': 'Accounting'})
        verifier = make_verifier()

        token = make_token(Signing_Key)
        claims = verifier.verify(_cid, _channel_name, token, config)

        self.assertIsNone(claims)

# ################################################################################################################################

    def test_list_claim_membership(self) -> 'None':
        """ A list-valued claim, such as groups, matches by membership.
        """
        config = make_config(claims={'groups': 'test-admins'})
        verifier = make_verifier()

        token = make_token(Signing_Key, extra_claims={'groups': ['test-users', 'test-admins']})
        claims = verifier.verify(_cid, _channel_name, token, config)

        self.assertIsNotNone(claims)

# ################################################################################################################################

    def test_list_claim_no_membership(self) -> 'None':
        config = make_config(claims={'groups': 'test-admins'})
        verifier = make_verifier()

        token = make_token(Signing_Key, extra_claims={'groups': ['test-users']})
        claims = verifier.verify(_cid, _channel_name, token, config)

        self.assertIsNone(claims)

# ################################################################################################################################

    def test_multiple_claims_all_must_match(self) -> 'None':
        config = make_config(claims={'department': 'Accounting', 'region': 'test-east'})
        verifier = make_verifier()

        # Only one of the two configured claims matches
        token = make_token(Signing_Key, extra_claims={'department': 'Accounting', 'region': 'test-west'})
        claims = verifier.verify(_cid, _channel_name, token, config)

        self.assertIsNone(claims)

# ################################################################################################################################
# ################################################################################################################################

class JWKSCaching(TestCase):
    """ JWKS documents are cached and refetched only on unknown key IDs.
    """

    def test_document_is_cached_after_first_fetch(self) -> 'None':
        config = make_config()
        verifier = make_verifier()

        token = make_token(Signing_Key)

        # The first verification fetches the document ..
        _ = verifier.verify(_cid, _channel_name, token, config)
        self.assertEqual(verifier.fetch_count, 1)

        # .. and the second one is served from the cache.
        _ = verifier.verify(_cid, _channel_name, token, config)
        self.assertEqual(verifier.fetch_count, 1)

# ################################################################################################################################

    def test_document_is_cached_with_ttl(self) -> 'None':
        config = make_config()
        verifier = make_verifier()

        token = make_token(Signing_Key)
        _ = verifier.verify(_cid, _channel_name, token, config)

        cache = verifier.cache
        assert isinstance(cache, FakeCache)

        set_call = cache.set_calls[0]
        self.assertEqual(set_call[2], JWKS_Cache_TTL)

# ################################################################################################################################

    def test_empty_document_is_not_cached(self) -> 'None':
        """ A failed fetch must not lock callers out for the whole TTL.
        """
        config = make_config()
        verifier = make_verifier(keys=[])

        token = make_token(Signing_Key)
        claims = verifier.verify(_cid, _channel_name, token, config)

        self.assertIsNone(claims)

        cache = verifier.cache
        assert isinstance(cache, FakeCache)

        self.assertEqual(cache.set_calls, [])

# ################################################################################################################################

    def test_key_rotation_triggers_refetch(self) -> 'None':
        """ An unknown key ID makes the verifier refetch the JWKS document once,
        which is how IdP key rotation is handled without restarts.
        """
        config = make_config()
        verifier = make_verifier()

        # Warm up the cache with the pre-rotation document ..
        token = make_token(Signing_Key)
        claims = verifier.verify(_cid, _channel_name, token, config)
        self.assertIsNotNone(claims)
        self.assertEqual(verifier.fetch_count, 1)

        # .. rotate the IdP keys - the new document only has the new key ..
        verifier.jwks_document = {'keys': [make_jwk(Rotated_Key, Rotated_Key_ID)]}

        # .. a token signed with the new key forces a refetch and then verifies fine.
        rotated_token = make_token(Rotated_Key, key_id=Rotated_Key_ID)
        claims = verifier.verify(_cid, _channel_name, rotated_token, config)

        self.assertIsNotNone(claims)
        self.assertEqual(verifier.fetch_count, 2)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
