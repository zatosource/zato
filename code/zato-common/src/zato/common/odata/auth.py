# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode
from http.client import FORBIDDEN, OK
from logging import getLogger
from time import time

# Zato
from zato.common.odata.common import AuthType, ODataException
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response, Session
    from zato.common.typing_ import stranydict, strnone, strstrdict
    Response = Response
    Session = Session

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# How many seconds before its actual expiration a cached token is already considered expired,
# so a token that is about to lapse is never sent out.
_token_expiry_margin = 60

# The lifetime assumed for tokens whose issuer did not say how long they live.
_default_token_lifetime = 3600

# The Azure AD v2.0 endpoint that the tenant_id convenience key expands to.
_azure_ad_token_url = 'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'

# The header SAP systems use to exchange CSRF tokens.
_csrf_token_header = 'X-CSRF-Token'

# What to send in that header to ask for a new token.
_csrf_fetch_value = 'Fetch'

# What a rejection carries in that header when the token is missing or stale.
_csrf_required_value = 'required'

# ################################################################################################################################
# ################################################################################################################################

class AuthHandler:
    """ Applies the configured authentication scheme to outgoing requests - Basic Auth
    and static bearer tokens are computed once, OAuth2 client-credentials tokens are
    fetched from the token endpoint, cached, and refreshed when they expire or when
    the server rejects them.
    """
    def __init__(self, config:'stranydict', session:'Session') -> 'None':
        self.config = config
        self.session = session

        self.auth_type = config.get('auth_type') or AuthType.No_Auth
        self.timeout = config.get('timeout')

        # The cached OAuth2 token and the moment it stops being usable.
        self._token:'strnone' = None
        self._token_expires_at = 0.0

        # Basic Auth and static bearer headers never change, so they are built upfront.
        if self.auth_type == AuthType.Basic:
            self._static_header = self._build_basic_auth_header()

        elif self.auth_type == AuthType.Bearer:
            self._static_header = f'Bearer {config["secret"]}'

        else:
            self._static_header = None

# ################################################################################################################################

    def _build_basic_auth_header(self) -> 'str':
        """ Builds the Authorization header out of the configured username and secret.
        """
        username = self.config['username']
        secret = self.config['secret']

        credentials = f'{username}:{secret}'.encode('utf8')
        encoded = b64encode(credentials).decode('ascii')

        out = f'Basic {encoded}'
        return out

# ################################################################################################################################

    def _token_url(self) -> 'str':
        """ Returns the OAuth2 token endpoint - an explicit token_url wins, otherwise
        the Azure AD one is derived from the configured tenant.
        """
        if token_url := self.config.get('token_url'):
            out = token_url

        elif tenant_id := self.config.get('tenant_id'):
            out = _azure_ad_token_url.format(tenant_id=tenant_id)

        # .. without either, the connection cannot obtain tokens at all.
        else:
            raise ODataException('OAuth2 requires either token_url or tenant_id')

        return out

# ################################################################################################################################

    def _fetch_token(self) -> 'None':
        """ Obtains a new token from the token endpoint with the client-credentials grant
        and caches it along with the moment it expires.
        """
        token_url = self._token_url()

        data = {
            'grant_type': 'client_credentials',
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret'],
        }

        # Scopes are configured one per line, the wire format wants them space-separated.
        if scopes := self.config.get('scopes'):
            data['scope'] = ' '.join(scopes.split())

        response = self.session.post(token_url, data=data, timeout=self.timeout)

        if response.status_code != OK:
            raise ODataException(f'Token request to `{token_url}` failed -> {response.status_code} {response.text}')

        payload = response.json()

        self._token = payload['access_token']

        # An issuer that does not say how long the token lives gets a conservative default.
        expires_in = payload.get('expires_in')
        if expires_in is None:
            expires_in = _default_token_lifetime

        self._token_expires_at = time() + float(expires_in) - _token_expiry_margin

# ################################################################################################################################

    def _oauth2_header(self) -> 'str':
        """ Returns the bearer header with a live token, fetching a fresh one when
        the cache is empty or the cached token has expired.
        """
        now = time()

        if self._token is None or now >= self._token_expires_at:
            self._fetch_token()

        out = f'Bearer {self._token}'
        return out

# ################################################################################################################################

    def apply(self, headers:'strstrdict') -> 'None':
        """ Sets the Authorization header on an outgoing request's headers, if the scheme calls for one.
        """
        if self._static_header:
            headers['Authorization'] = self._static_header

        elif self.auth_type == AuthType.OAuth2:
            headers['Authorization'] = self._oauth2_header()

# ################################################################################################################################

    def invalidate(self) -> 'None':
        """ Discards the cached token so the next request fetches a fresh one -
        what a 401 from the server triggers.
        """
        self._token = None
        self._token_expires_at = 0.0

# ################################################################################################################################

    @property
    def can_retry_on_unauthorized(self) -> 'bool':
        """ Whether a 401 can be retried at all - only OAuth2 tokens can go stale and be refreshed.
        """
        out = self.auth_type == AuthType.OAuth2
        return out

# ################################################################################################################################
# ################################################################################################################################

class CSRFHandler:
    """ Handles the CSRF token exchange SAP systems require for writes - a token is fetched
    with a GET carrying 'X-CSRF-Token: Fetch', cached, attached to every modifying request,
    and refetched once when the server rejects it as stale.
    """
    def __init__(self, session:'Session', address:'str') -> 'None':
        self.session = session
        self.address = address
        self._token:'strnone' = None

# ################################################################################################################################

    def fetch(self, headers:'strstrdict', timeout:'float | None', verify:'bool | str', cert:'str | tuple | None') -> 'None':
        """ Fetches a new CSRF token from the service root - the session keeps the cookies
        that came with it, which SAP requires to accept the token later.
        """
        fetch_headers = dict(headers)
        fetch_headers[_csrf_token_header] = _csrf_fetch_value

        response = self.session.get(self.address, headers=fetch_headers, timeout=timeout, verify=verify, cert=cert)

        token = response.headers.get(_csrf_token_header)
        if not token:
            raise ODataException(f'No CSRF token in response from `{self.address}` -> {response.status_code}')

        self._token = token

# ################################################################################################################################

    def apply(
        self,
        headers:'strstrdict',
        timeout:'float | None',
        verify:'bool | str',
        cert:'str | tuple | None',
        ) -> 'None':
        """ Attaches the cached CSRF token to a modifying request's headers, fetching one first if needed.
        """
        if self._token is None:
            self.fetch(headers, timeout, verify, cert)

        # A missing token raised in fetch, so by now it is always a string.
        headers[_csrf_token_header] = cast_('str', self._token)

# ################################################################################################################################

    def invalidate(self) -> 'None':
        """ Discards the cached token so the next write fetches a fresh one.
        """
        self._token = None

# ################################################################################################################################

    def is_csrf_rejection(self, response:'Response') -> 'bool':
        """ Whether a response is the SAP way of saying the CSRF token was missing or stale -
        a 403 whose X-CSRF-Token header reads 'Required'.
        """
        if response.status_code != FORBIDDEN:
            return False

        header = response.headers.get(_csrf_token_header) or ''

        out = header.lower() == _csrf_required_value
        return out

# ################################################################################################################################
# ################################################################################################################################
