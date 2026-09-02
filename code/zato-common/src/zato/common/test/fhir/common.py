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

# Zato
from zato.common.api import HL7

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.fhir.store import FHIRStore
    from zato.common.typing_ import anytuple, strnone

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

# The bundle types the base-URL POST interaction accepts, per the spec's transaction interaction
bundle_request_types = {
    'transaction': 'transaction-response',
    'batch': 'batch-response',
}

# ################################################################################################################################
# ################################################################################################################################

class OAuthTokenIssuer:
    """ Issues and validates OAuth bearer tokens for the client credentials grant of RFC 6749.
    """
    def __init__(self, client_id:'str', client_secret:'str') -> 'None':

        # The only credentials the token endpoint accepts
        self._client_id = client_id
        self._client_secret = client_secret

        # All the tokens issued so far, together with when they expire
        self._tokens:'token_dict' = {}

        # Serializes access to the token dictionary
        self._lock = threading.Lock()

# ################################################################################################################################

    def issue(self, client_id:'str', client_secret:'str') -> 'strnone':
        """ Issues a new token if the credentials are correct, otherwise returns None.
        """
        if client_id != self._client_id:
            return None

        if client_secret != self._client_secret:
            return None

        token = uuid4().hex
        expiration_time = time() + token_lifetime

        with self._lock:
            self._tokens[token] = expiration_time

        out = token
        return out

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
