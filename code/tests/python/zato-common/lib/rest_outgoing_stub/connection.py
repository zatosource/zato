# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The part of a server that an outgoing REST connection reads, and the configuration a server builds
# such a connection from, for tests that build connections without a running server.

# stdlib
from json import dumps, loads

# Zato
from zato.common.api import DATA_FORMAT, URL_TYPE
from zato.common.bearer_token import BearerTokenManager
from zato.common.facade import SecurityFacade
from zato.common.marshal_.api import MarshalAPI
from zato.common.soap.common import SOAPVersion
from zato.common.typing_ import cast_
from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict
    from zato.server.base.parallel import ParallelServer
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

# The server the connections are created under
Server_Name = 'test.rest.outgoing.server'

# The OAuth client the token endpoint is invoked as
Client_ID     = 'test.client'
Client_Secret = 'Test.Client.Secret.2026'

# ################################################################################################################################
# ################################################################################################################################

class CacheStub:
    """ A cache with the interface of the server's cache API, holding its values in memory
    the way the server's cache serializes them.
    """

    def __init__(self) -> 'None':
        self.values:'stranydict' = {}
        self.expiry:'dict[str, int]' = {}

    def get(self, key:'str') -> 'any_':
        if serialized := self.values.get(key):
            out = loads(serialized)
        else:
            out = None

        return out

    def set(self, key:'str', value:'any_', expiry:'int'=0) -> 'None':
        self.values[key] = dumps(value)
        self.expiry[key] = expiry

    def clear(self) -> 'None':
        self.values.clear()
        self.expiry.clear()

# ################################################################################################################################

class _URLDataStub:
    """ The part of a server's URL data that the security facade reads.
    """

    def __init__(self) -> 'None':
        self.oauth_config:'stranydict' = {}

# ################################################################################################################################

class _ConfigManagerStub:
    """ The part of a server's configuration manager that the bearer token manager reads.
    """

    def __init__(self, cache_api:'CacheStub') -> 'None':
        self.cache_api = cache_api

# ################################################################################################################################

class ServerStub:
    """ The part of a server that an outgoing connection reads - its name, the security facade,
    the bearer token manager with its cache, and the marshaling API that models are built with.
    """

    def __init__(self) -> 'None':
        self.name = Server_Name
        self.url_data = _URLDataStub()
        self.cache = CacheStub()
        self.config_manager = _ConfigManagerStub(self.cache)
        self.marshal_api = MarshalAPI()

        # What the services that callbacks invoke received
        self.invocations:'anylist' = []

        server = cast_('ParallelServer', self)

        self.security_facade = SecurityFacade(server)
        self.bearer_token_manager = BearerTokenManager(server)

# ################################################################################################################################

    def invoke(self, name:'str', data:'any_') -> 'None':
        self.invocations.append((name, data))

# ################################################################################################################################

    def add_static_token(
        self,
        name:'str',
        token:'str',
        *,
        header:'str'='Authorization',
        prefix:'str'='Bearer',
        in_password:'bool'=False,
        ) -> 'None':
        """ Registers a bearer token definition with a static token, either in its own field
        or in the password column, as definitions created before the field existed keep it.
        """
        config:'anydict' = {
            'id': len(self.url_data.oauth_config) + 1,
            'name': name,
            'static_header': header,
            'static_prefix': prefix,
        }

        if in_password:
            config['is_static_token'] = True
            config['password'] = token
        else:
            config['static_token'] = token

        self.url_data.oauth_config[name] = {'config': config}

# ################################################################################################################################

    def add_oauth(
        self,
        name:'str',
        auth_server_url:'str',
        *,
        scopes:'str'='',
        data_format:'str'=DATA_FORMAT.JSON,
        ) -> 'None':
        """ Registers a bearer token definition that obtains its tokens from a token endpoint.
        """
        config:'anydict' = {
            'id': len(self.url_data.oauth_config) + 1,
            'name': name,
            'username': Client_ID,
            'password': Client_Secret,
            'grant_type': 'client_credentials',
            'auth_server_url': auth_server_url,
            'client_id_field': 'client_id',
            'client_secret_field': 'client_secret',
            'scopes': scopes,
            'extra_fields': '',
            'data_format': data_format,
        }

        self.url_data.oauth_config[name] = {'config': config}

# ################################################################################################################################

    def edit_bearer_token(self, name:'str', connections:'anylist', **changes:'any_') -> 'None':
        """ Changes a bearer token definition the way the server applies an edit - the definition is updated,
        the tokens obtained with it are invalidated and the connections that use it rebuild their credentials.
        """
        config = self.url_data.oauth_config[name]['config']
        config.update(changes)

        self.bearer_token_manager.invalidate(name)

        for connection in connections:
            connection.set_auth()

# ################################################################################################################################
# ################################################################################################################################

def new_config(
    address_host:'str',
    path:'str',
    *,
    name:'str'='test.rest.outgoing',
    sec_type:'str'='',
    security_name:'str'='',
    username:'str'='',
    password:'str'='',
    data_format:'str'='',
    content_type:'str'='',
    transport:'str'=URL_TYPE.PLAIN_HTTP,
    timeout:'any_'=10,
    pool_size:'any_'=1,
    validate_tls:'bool'=True,
    ca_certs_path:'str'='',
    tls_client_cert:'str'='',
    tls_client_key:'str'='',
    **extra:'any_',
    ) -> 'stranydict':
    """ Returns the configuration of one outgoing REST connection, as a server builds it from what is stored.
    """
    out:'stranydict' = {
        'id': 1,
        'name': name,
        'is_internal': False,
        'is_active': True,
        'is_audit_log_active': False,
        'use_queue': False,
        'timeout': timeout,
        'pool_size': pool_size,
        'sec_type': sec_type,
        'security_name': security_name,
        'username': username,
        'orig_username': '',
        'password': password,
        'transport': transport,
        'address_host': address_host,
        'address_url_path': path,
        'content_type': content_type,
        'data_format': data_format,
        'method': 'GET',
        'ping_method': 'GET',
        'soap_version': SOAPVersion.V11,
        'soap_action': '',
        'validate_tls': validate_tls,
        'tls_client_cert': tls_client_cert,
        'tls_client_key': tls_client_key,
    }

    if ca_certs_path:
        out['ca_certs_path'] = ca_certs_path

    out.update(extra)

    return out

# ################################################################################################################################

def new_connection(server:'ServerStub', address_host:'str', path:'str', **kwargs:'any_') -> 'HTTPSOAPWrapper':
    """ Builds one outgoing REST connection exactly as a server builds it from its configuration.
    """
    config = new_config(address_host, path, **kwargs)
    parallel_server = cast_('ParallelServer', server)

    out = HTTPSOAPWrapper(parallel_server, config)
    return out

# ################################################################################################################################
# ################################################################################################################################
