# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads
from logging import getLogger
from threading import RLock

# MSAL
from msal import ConfidentialClientApplication

# Office-365
from O365 import Account
from O365.connection import MSGraphProtocol
from O365.utils.token import MemoryTokenBackend

# Zato
from zato.common.api import Microsoft365

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_default = Microsoft365.Default

# ################################################################################################################################
# ################################################################################################################################

class Microsoft365Client:
    """ Client for Microsoft 365 cloud APIs. All the attributes of the underlying O365 account,
    e.g. mailbox, schedule, directory or connection, are available directly on this class.
    """
    def __init__(self, config:'stranydict') -> 'None':

        self.config = config
        self.name = config['name']

        # The OAuth scopes to request tokens for - the actual value is extracted from the config in _build_impl.
        self.scopes = []

        # The underlying O365 account is built lazily, on first use,
        # so that a misconfigured connection does not break server startup.
        self.impl = None

        # Makes sure only one caller builds the account or renews its token.
        self.impl_lock = RLock()

# ################################################################################################################################

    def __getattr__(self, name:'str') -> 'any_':

        # Dunder lookups, e.g. during copy or pickle operations, must never
        # trigger the account's construction because that would mean network calls.
        if name.startswith('__'):
            raise AttributeError(name)

        # This method is called only for attributes not found on this class,
        # in which case they are looked up on the underlying O365 account.
        impl = self._get_impl()

        out = getattr(impl, name)
        return out

# ################################################################################################################################

    def _build_impl(self) -> 'Account':

        config = self.config

        # Extra configuration options are kept in an opaque JSON attribute - flatten them into the config dict.
        opaque1 = config.pop('opaque1', None) or '{}'
        opaque1 = loads(opaque1)
        config.update(opaque1)

        tenant_id = config['tenant_id']
        client_id = config['client_id']
        secret_value = config.get('secret_value') or config.get('secret') or config.get('password')

        if not secret_value:
            raise Exception(f'Secret value not found in {dict(config)}')

        credentials = (client_id, secret_value)

        # Whether TLS certificates should be verified - turned off only when testing against local servers.
        verify_tls = config.get('verify_tls')
        if verify_tls is None:
            verify_tls = _default.Verify_TLS

        # The base address of the Graph API - it is the public cloud unless configured otherwise.
        api_address = config.get('address') or _default.Address
        api_address = api_address.rstrip('/')

        # Build the protocol object pointing to the Graph API address ..
        protocol = MSGraphProtocol()

        # .. a non-default address means we need to rewrite the URLs the protocol builds ..
        if api_address != _default.Address:
            protocol.protocol_url = f'{api_address}/'
            protocol.protocol_scope_prefix = f'{api_address}/'
            protocol.service_url = f'{api_address}/{protocol.api_version}/'

        # .. the client credentials grant always requests the API's .default scope - the actual
        # .. permissions are the application ones granted to the app registration in the tenant ..
        default_scope = protocol.prefix_scope('.default')
        self.scopes = [default_scope]

        # .. each account keeps its tokens in its own in-memory backend
        # .. so that multiple connections never step on each other ..
        token_backend = MemoryTokenBackend()

        # .. now, the account object itself can be created ..
        account = Account(
            credentials,
            auth_flow_type='credentials',
            tenant_id=tenant_id,
            protocol=protocol,
            token_backend=token_backend,
            verify_ssl=verify_tls,
        )

        # .. the server that issues OAuth tokens is Microsoft's unless configured otherwise,
        # .. in which case the MSAL authority needs to point to the custom one ..
        auth_server_url = config.get('auth_server_url') or _default.Auth_Server_URL
        auth_server_url = auth_server_url.rstrip('/')

        if auth_server_url != _default.Auth_Server_URL:
            self._set_custom_auth_server(account, auth_server_url, tenant_id, verify_tls)

        # .. obtain the initial token, e.g. wrong credentials will be rejected here ..
        is_authenticated = account.authenticate(requested_scopes=self.scopes)

        if not is_authenticated:
            raise Exception(f'Could not authenticate to Microsoft 365 ({self.name})')

        # .. and hand the account back to our caller.
        return account

# ################################################################################################################################

    def _set_custom_auth_server(
        self,
        account:'Account',
        auth_server_url:'str',
        tenant_id:'str',
        verify_tls:'bool'
        ) -> 'None':
        """ Points the account's MSAL client to a non-default authorization server, e.g. a test one.
        """
        connection = account.con
        authority = f'{auth_server_url}/{tenant_id}'
        connection._msal_authority = authority

        # Instance discovery must be off because the custom server is not in Microsoft's list of known hosts.
        connection._msal_client = ConfidentialClientApplication(
            client_id=connection.auth[0],
            client_credential=connection.auth[1],
            authority=authority,
            token_cache=connection.token_backend,
            instance_discovery=False,
            verify=verify_tls,
        )

# ################################################################################################################################

    def _get_impl(self) -> 'Account':

        # Build the account on first use, making sure only one caller does it ..
        with self.impl_lock:
            if self.impl is None:
                self.impl = self._build_impl()

            # .. client-credentials tokens cannot be refreshed in place,
            # .. so when the current one expires, a new one is requested.
            connection = self.impl.con
            if connection.token_backend.token_is_expired():
                is_renewed = connection.request_token(None, requested_scopes=self.scopes)

                if not is_renewed:
                    raise Exception(f'Could not renew a Microsoft 365 token ({self.name})')

        return self.impl

# ################################################################################################################################

    def zato_delete_impl(self, reason:'str'='') -> 'None':

        # There is nothing to close in the O365 account and, more importantly, having this method here
        # means that deleting the connection never triggers a lazy build of an account via __getattr__.
        with self.impl_lock:
            self.impl = None

# ################################################################################################################################

    def ping(self) -> 'None':

        # Get the underlying account ..
        impl = self._get_impl()

        # .. and confirm the credentials work by listing one user from the directory.
        url = f'{impl.protocol.service_url}users'
        response = impl.con.get(url, params={'$top': 1})

        logger.info('Microsoft 365 ping OK (%s) -> %s', self.name, response.status_code)

# ################################################################################################################################
# ################################################################################################################################
