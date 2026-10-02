# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import threading
from http.server import ThreadingHTTPServer
from time import time
from uuid import uuid4

# PyJWT
import jwt as pyjwt

# Zato
from zato.common.api import HL7, OAuth

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.fhir.store import FHIRStore
    from zato.common.typing_ import anytuple, strnone, strset

# ################################################################################################################################
# ################################################################################################################################

# Maps issued OAuth tokens to their expiration time as a Unix timestamp
token_dict = dict[str, float]

# ################################################################################################################################
# ################################################################################################################################

# The FHIR version this server implements
fhir_version = '4.0.1'

# The media type for FHIR JSON, per the spec's http.html#mime-type
fhir_content_type = 'application/fhir+json; charset=utf-8'

# The media type for OAuth token responses, per RFC 6749
json_content_type = 'application/json; charset=utf-8'

# The auth types the server supports, the same IDs the FHIR outgoing connection uses
auth_type_basic = HL7.Const.FHIR_Auth_Type.Basic_Auth.id
auth_type_oauth = HL7.Const.FHIR_Auth_Type.OAuth.id

# Where OAuth tokens are issued, per RFC 6749's client credentials grant
token_path = '/oauth/token'

# How long issued OAuth tokens are valid for, in seconds
token_lifetime = 3600

# The only grant type the token endpoint implements
grant_type_client_credentials = 'client_credentials'

# The claims a client assertion must carry, per RFC 7523 and SMART Backend Services
assertion_required_claims = ['iss', 'sub', 'aud', 'exp', 'jti']

# How a token request that cannot be authenticated is described, per RFC 6749
error_invalid_client = 'invalid_client'

# The bundle types the base-URL POST interaction accepts, per the spec's transaction interaction
bundle_request_types = {
    'transaction': 'transaction-response',
    'batch': 'batch-response',
}

# ################################################################################################################################
# ################################################################################################################################

class OAuthTokenIssuer:
    """ Issues and validates OAuth bearer tokens for the client credentials grant of RFC 6749.
    A client logs in either with its secret or, when a public key is registered, with a client assertion
    signed by the matching private key, per RFC 7523 - the way SMART Backend Services and other EHR token endpoints work.
    """
    def __init__(self, client_id:'str', client_secret:'str', public_key_pem:'str'='', token_endpoint:'str'='') -> 'None':

        # The only credentials the token endpoint accepts
        self._client_id = client_id
        self._client_secret = client_secret

        # The public key client assertions are verified with, and the audience they must name
        self._public_key_pem = public_key_pem
        self._token_endpoint = token_endpoint

        # All the tokens issued so far, together with when they expire
        self._tokens:'token_dict' = {}

        # Every assertion ID seen so far - an assertion is good for one login only
        self._seen_jti:'strset' = set()

        # Serializes access to the token dictionary and the assertion IDs
        self._lock = threading.Lock()

# ################################################################################################################################

    def _issue(self) -> 'str':
        """ Mints a token and remembers when it expires.
        """
        token = uuid4().hex
        expiration_time = time() + token_lifetime

        with self._lock:
            self._tokens[token] = expiration_time

        out = token
        return out

# ################################################################################################################################

    def issue(self, client_id:'str', client_secret:'str') -> 'strnone':
        """ Issues a new token if the credentials are correct, otherwise returns None.
        """
        if client_id != self._client_id:
            return None

        if client_secret != self._client_secret:
            return None

        out = self._issue()
        return out

# ################################################################################################################################

    def issue_with_assertion(self, assertion:'str') -> 'tuple[strnone, str]':
        """ Issues a new token if the client assertion verifies, otherwise returns None and the reason it did not.
        The assertion must be signed by the registered key, name this token endpoint as its audience,
        carry the client ID as both issuer and subject, not be expired and not have been seen before.
        """
        # Without a registered key there is nothing to verify the signature with ..
        if not self._public_key_pem:
            return None, 'Client assertions are not accepted'

        # .. the signature, the audience, the expiry and the presence of every required claim are checked here ..
        try:
            claims = pyjwt.decode(
                assertion,
                self._public_key_pem,
                algorithms=list(OAuth.JWT_Algorithms),
                audience=self._token_endpoint,
                options={'require': assertion_required_claims},
            )
        except pyjwt.PyJWTError as e:
            return None, f'Client assertion rejected -> {e}'

        # .. the assertion must speak for the registered client ..
        if claims['iss'] != self._client_id:
            return None, f'Client assertion issuer does not match -> {claims["iss"]}'

        if claims['sub'] != self._client_id:
            return None, f'Client assertion subject does not match -> {claims["sub"]}'

        # .. and it must not have been used before.
        jti = claims['jti']

        with self._lock:
            if jti in self._seen_jti:
                return None, f'Client assertion replayed -> {jti}'
            self._seen_jti.add(jti)

        out = self._issue()
        return out, ''

# ################################################################################################################################

    def validate(self, token:'str') -> 'bool':
        """ Returns True if the token was issued by this server and has not expired yet.
        """
        with self._lock:
            expiration_time = self._tokens.get(token)

        if expiration_time is None:
            out = False
        else:
            out = time() < expiration_time

        return out

# ################################################################################################################################
# ################################################################################################################################

class FHIRHTTPServer(ThreadingHTTPServer):
    """ ThreadingHTTPServer subclass that carries the store and the optional authentication configuration.
    """

    # A deep listen backlog so bursts of concurrent clients connect without resets
    request_queue_size = 128

    def __init__(
        self,
        address:'anytuple',
        handler:'type',
        store:'FHIRStore',
        base_address:'str',
        auth_type:'str',
        auth_header:'strnone',
        token_issuer:'OAuthTokenIssuer | None'
        ) -> 'None':
        super().__init__(address, handler)
        self.store = store
        self.base_address = base_address
        self.auth_type = auth_type
        self.auth_header = auth_header
        self.token_issuer = token_issuer

# ################################################################################################################################
# ################################################################################################################################
