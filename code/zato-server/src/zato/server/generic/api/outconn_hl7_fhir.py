# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode
from logging import getLogger
from traceback import format_exc

# fhirpy
from fhirpy import SyncFHIRClient

# Zato
from zato.common.api import HL7
from zato.common.typing_ import cast_
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import stranydict
    from zato.server.base.parallel import ParallelServer
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_basic_auth = HL7.Const.FHIR_Auth_Type.Basic_Auth.id
_oauth = HL7.Const.FHIR_Auth_Type.OAuth.id

# ################################################################################################################################
# ################################################################################################################################

# Defaults applied by the config manager when the create path does not supply a field,
# e.g. when an outconn is created directly through zato.generic.connection.create.
outconn_fhir_config_defaults:'dict[str, object]' = {
    'auth_type': HL7.Const.FHIR_Auth_Type.No_Auth.id,
    'security_id': 0,
    'username': '',
    'secret': '',
    'pool_size': HL7.Default.pool_size,
}

# Config keys that must be integers but may arrive as strings from opaque storage
outconn_fhir_int_config_keys = ('security_id', 'pool_size')

# ################################################################################################################################
# ################################################################################################################################

class _HL7FHIRConnection(SyncFHIRClient):
    zato_config: 'stranydict'

    def __init__(self, config:'stranydict') -> 'None':

        self.zato_config = config
        self.zato_security_id = self.zato_config['security_id']
        self.zato_auth_type = self.zato_config['auth_type']

        # This can be built in advance in case we are using Basic Auth
        if self.zato_auth_type == _basic_auth:
            self.zato_basic_auth_header = self.zato_get_basic_auth_header()
        else:
            self.zato_basic_auth_header = None

        address = self.zato_config['address']
        super().__init__(address)

# ################################################################################################################################

    def _build_request_headers(self):

        # This is constant
        headers = {
            'Accept': 'application/json'
        }

        # This is inherited from the parent class
        if self.extra_headers is not None:
            headers = {**headers, **self.extra_headers}

        # This is already available ..
        if self.zato_auth_type == _basic_auth:
            auth_header = self.zato_basic_auth_header

        # .. while this needs to be dynamically created ..
        elif self.zato_auth_type == _oauth:
            auth_header = self.zato_get_oauth_header()

        else:
            auth_header = None

        # .. now, it can be assigned ..
        if auth_header:
            headers['Authorization'] = auth_header

        # .. and the whole set of headers can be returned.
        return headers

# ################################################################################################################################

    def zato_get_basic_auth_header(self) -> 'str':

        username = self.zato_config['username']
        password = self.zato_config['secret']

        auth_header = f'{username}:{password}'
        auth_header = auth_header.encode('ascii')
        auth_header = b64encode(auth_header)
        auth_header = auth_header.decode('ascii')
        auth_header = f'Basic {auth_header}'

        return auth_header

# ################################################################################################################################

    def zato_get_oauth_header(self) -> 'str':

        # The server gives us access to security definitions and the bearer token manager
        server = self.zato_config['server'] # type: ParallelServer

        # Each OAuth definition specifies its own data format and scopes ..
        sec_def = server.security_facade.get_bearer_token_by_id(self.zato_security_id)
        data_format = sec_def['data_format']

        if scopes := sec_def.get('scopes'):
            scopes = ' '.join(scopes.splitlines())
        else:
            scopes = ''

        # .. this returns the token from the server's cache or fetches a new one from the auth server ..
        result = server.bearer_token_manager.get_bearer_token_info_by_sec_def_id(self.zato_security_id, scopes, data_format)

        # .. and now the header can be built.
        out = f'Bearer {result.info.token}'
        return out

# ################################################################################################################################

    def zato_ping(self):
        self.execute(path='/CapabilityStatement', method='get')

# ################################################################################################################################
# ################################################################################################################################

class OutconnHL7FHIRWrapper(Wrapper):
    """ Wraps a queue of connections to HL7 FHIR servers.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        config.auth_url = config.address
        config.server = server
        super(OutconnHL7FHIRWrapper, self).__init__(config, 'HL7 FHIR', server)

# ################################################################################################################################

    def add_client(self) -> 'None':

        try:
            conn = _HL7FHIRConnection(self.config)
            _ = self.client.put_client(conn)
        except Exception:
            logger.warning('Caught an exception while adding an HL7 FHIR client (%s); e:`%s`',
                self.config['name'], format_exc())

# ################################################################################################################################

    def ping(self) -> 'None':
        with self.client() as client:
            client = cast_('_HL7FHIRConnection', client)
            client.zato_ping()

# ################################################################################################################################
# ################################################################################################################################
