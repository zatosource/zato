# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode
from logging import getLogger
from traceback import format_exc

# FHIR-py
from fhirpy import SyncFHIRClient

# Zato
from zato.common.api import HL7
from zato.server.connection.queue import Wrapper
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strnone
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_basic_auth = HL7.Const.FHIR_Auth_Type.Basic_Auth.id
_oauth = HL7.Const.FHIR_Auth_Type.OAuth.id

# ################################################################################################################################
# ################################################################################################################################

class _HL7FHIRConnection(SyncFHIRClient):
    zato_config: 'stranydict'

    def __init__(self, config:'stranydict') -> 'None':

        self.zato_config = config
        self.zato_security_id = self.zato_config.get('security_id') or 0
        self.zato_auth_type = self.zato_config.get('auth_type')

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

    def zato_get_oauth_header(self) -> 'strnone':
        server = self.zato_config['server'] # type: ParallelServer
        auth_header = server.oauth_store.get_auth_header(self.zato_security_id)
        return auth_header

# ################################################################################################################################

    def zato_ping(self):
        self.execute(path='/CapabilityStatement', method='get')

# ################################################################################################################################
# ################################################################################################################################

class OutconnHL7FHIRWrapper(Wrapper):
    """ Wraps a queue of connections to HL7 FHIR servers.
    """
    def __init__(self, config, server):
        config.auth_url = config.address
        config.server = server
        super(OutconnHL7FHIRWrapper, self).__init__(config, 'HL7 FHIR', server)

# ################################################################################################################################

    def add_client(self):

        try:
            conn = _HL7FHIRConnection(self.config)
            self.client.put_client(conn)
        except Exception:
            logger.warning('Caught an exception while adding an HL7 FHIR client (%s); e:`%s`',
                self.config['name'], format_exc())

# ################################################################################################################################

    def ping(self):
        with self.client() as client:
            client = cast_('_HL7FHIRConnection', client)
            client.zato_ping()

# ################################################################################################################################
# ################################################################################################################################
