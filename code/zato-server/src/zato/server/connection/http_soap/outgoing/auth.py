# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# requests-ntlm
from requests_ntlm import HttpNtlmAuth

# Zato
from zato.common.api import EnvVariable
from zato.common.typing_ import cast_
from zato.server.connection.http_soap.outgoing.common import logger, _API_Key, _Basic_Auth, _MTLS, _NTLM, _SPNEGO

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.bearer_token import BearerTokenInfoResult
    from zato.common.soap.client import SOAPClient
    from zato.common.typing_ import any_, strnone, strstrdict
    SOAPClient = SOAPClient

# ################################################################################################################################
# ################################################################################################################################

class SPNEGOAuth:
    """ A requests auth object that acquires Kerberos credentials from a keytab lazily,
    on the first request, so that a connection can be created and edited before its keytab
    is mounted into the container.
    """
    def __init__(self, principal:'str', keytab_path:'str', target_spn:'strnone', needs_delegation:'bool') -> 'None':
        self.principal = principal
        self.keytab_path = keytab_path
        self.target_spn = target_spn
        self.needs_delegation = needs_delegation
        self._impl = None

    def _build_impl(self) -> 'any_':

        # Imported here because the underlying gssapi package needs system Kerberos
        # libraries which may be absent from installations that never use SPNEGO.
        import gssapi
        from requests_gssapi import HTTPSPNEGOAuth

        # Credentials are acquired explicitly from the keytab, so no external kinit
        # or credential cache is needed - gssapi re-acquires tickets from the keytab
        # on its own when they expire.
        creds = gssapi.Credentials(
            name=gssapi.Name(self.principal, gssapi.NameType.kerberos_principal),
            store={'client_keytab': self.keytab_path},
            usage='initiate',
        )

        # The remote service's SPN is optional - when it is not given,
        # it is derived from the target host name.
        if self.target_spn:
            target_name = gssapi.Name(self.target_spn, gssapi.NameType.hostbased_service)
        else:
            target_name = None

        # The library's own annotation says this is a string, which it never is - it takes a GSSAPI
        # name object or nothing at all, and deriving the name from the target host is exactly what
        # passing nothing means.
        target_name = cast_('str', target_name)

        return HTTPSPNEGOAuth(creds=creds, target_name=target_name, delegate=self.needs_delegation)

    def __call__(self, request:'any_') -> 'any_':

        # The underlying auth object is built on first use - the keytab has to exist
        # only when the connection is actually invoked, not when it is configured.
        if self._impl is None:
            self._impl = self._build_impl()

        return self._impl(request)

# ################################################################################################################################
# ################################################################################################################################

class AuthMixin:
    """ How an outgoing connection authenticates itself - the credentials its security definition
    names, the TLS client certificate and the bearer token an OAuth definition resolves to.
    """

    def _check_password(self) -> 'None':
        """ Notes whether this connection's password is still the placeholder that an import leaves
        behind for a value whose environment variable was not set. Such a connection has no
        credentials at all, which is what invoking it reports rather than sending the placeholder.
        """
        self.missing_password = ''

        # A connection may have no password to begin with - a definition that authenticates
        # with a certificate or a keytab is the usual case.
        password = self.config['password']

        if password:
            if password.startswith(EnvVariable.Missing_Value_Prefix):
                self.missing_password = password
                logger.warning('Connection `%s` has no password, its value was never provided -> `%s`',
                    self.config['name'], password)

# ################################################################################################################################

    def set_auth(self) -> 'None':

        # Local variables
        self.requests_auth = None
        self.username = None

        # The headers that the security definition contributes are rebuilt on each call, so the set
        # always describes the definition as it stands now and not as it once stood.
        base_headers:'strstrdict' = {}

        # The SOAP client is built lazily and dropped here so security changes take effect on the next call.
        self._soap_client:'SOAPClient | None' = None

        self._check_password()

        # #######################################
        #
        # API Keys
        #
        # #######################################
        if self.sec_type == _API_Key:
            username = self.config['orig_username']
            if not username:
                username = self.config['username']
            base_headers[username] = self.config['password']

        # #######################################
        #
        # HTTP Basic Auth
        #
        # #######################################
        elif self.sec_type in {_Basic_Auth}:
            self.requests_auth = self.auth
            self.username = self.requests_auth[0]

        # #######################################
        #
        # NTLM
        #
        # #######################################
        elif self.sec_type == _NTLM:
            _username, _password = self.auth
            _requests_auth = HttpNtlmAuth(_username, _password)
            self.requests_auth = _requests_auth
            self.username = _username

        # #######################################
        #
        # mTLS
        #
        # #######################################
        elif self.sec_type == _MTLS:

            # The definition's certificate material replaces whatever TLS details
            # the connection itself may have been configured with.
            self.config['tls_client_cert'] = self.config['cert_path']
            self.config['tls_client_key'] = self.config['key_path']

            # Pooled connections were established with the material that was in place when they were
            # opened, so they are discarded here - a definition edited to present a different
            # certificate would otherwise keep presenting the previous one for as long as
            # a pooled connection lasted.
            self.https_adapter.clear_pool()

        # #######################################
        #
        # Kerberos (SPNEGO)
        #
        # #######################################
        elif self.sec_type == _SPNEGO:

            principal = self.config['principal']
            keytab_path = self.config['keytab_path']
            target_spn = self.config['target_spn']
            needs_delegation = self.config['needs_delegation']

            # The auth object defers all gssapi work until the first request goes out.
            _requests_auth = SPNEGOAuth(principal, keytab_path, target_spn, bool(needs_delegation))
            self.requests_auth = _requests_auth
            self.username = principal

        # Whatever the definition contributed replaces the previous set in one assignment,
        # so a request being built elsewhere sees either all of the old headers or all of the new ones.
        self.base_headers = base_headers

# ################################################################################################################################

    def _get_auth(self) -> 'any_':
        """ Returns a username and password pair or None, if no security definition has been attached.
        """
        if self.sec_type in {_Basic_Auth, _NTLM}:
            auth = (self.config['username'], self.config['password'])
        else:
            auth = None

        return auth

    auth = property(fget=_get_auth, doc=_get_auth.__doc__)

# ################################################################################################################################

    def _get_tls_client_cert(self) -> 'any_':
        """ Returns what to pass to requests as its client certificate - a single PEM path holding
        both the certificate and its private key, a (certificate, key) path pair when the key lives
        in its own file, or None when the connection does not present a client certificate.
        """
        client_cert = self.config['tls_client_cert']

        if not client_cert:
            return None

        if client_key := self.config['tls_client_key']:
            out = (client_cert, client_key)
        else:
            out = client_cert

        return out

# ################################################################################################################################

    def _get_bearer_token_auth(self, sec_def_name:'str', scopes:'str', data_format:'str') -> 'BearerTokenInfoResult':

        # This will get the token from cache or from the remote auth. server ..
        result = self.server.bearer_token_manager.get_bearer_token_info_by_sec_def_name(sec_def_name, scopes, data_format)

        # .. which we can return to our caller.
        return result

# ################################################################################################################################
# ################################################################################################################################
