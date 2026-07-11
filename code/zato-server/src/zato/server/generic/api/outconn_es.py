# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Elasticsearch
from elasticsearch import Elasticsearch

# Zato
from zato.common.api import ES
from zato.common.typing_ import cast_
from zato.server.connection.wrapper import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import stranydict, strlist
    from zato.server.base.parallel import ParallelServer
    Bunch = Bunch
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Default values applied when a configuration key is missing or None
outconn_es_config_defaults:'dict[str, object]' = {
    'address_list': ES.Default.Address_List,
    'username': '',
    'timeout': ES.Default.Timeout,
    'tls_ca_certs_file': '',
    'tls_cert_key_file': '',
    'is_tls_validation_enabled': True,
}

# Config keys that must be integers but may arrive as strings from opaque storage
outconn_es_int_config_keys = ('timeout',)

# Config keys that must be booleans but may arrive as strings from opaque storage
outconn_es_bool_config_keys = ('is_tls_validation_enabled',)

# ################################################################################################################################
# ################################################################################################################################

class OutconnESWrapper(Wrapper):
    """ Wraps an Elasticsearch connection client.
    """
    wrapper_type = 'Elasticsearch connection'

    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        super(OutconnESWrapper, self).__init__(config, server)
        self._impl:'Elasticsearch' = cast_('Elasticsearch', None)

# ################################################################################################################################

    def _init_impl(self) -> 'None':

        with self.update_lock:

            # Each line of the configuration is one full http(s):// URL to connect to -
            # whether TLS is used follows from the scheme of each URL. Duplicates
            # are removed because the underlying client rejects repeated addresses.
            address_list:'strlist' = list(dict.fromkeys(self.config.address_list.splitlines()))

            # The password may still be encrypted if it went through a path
            # that did not decrypt it - decrypting a plain string is a no-op.
            password = self.server.decrypt(self.config.secret)

            # Configuration of the underlying client
            client_config:'stranydict' = {
                'hosts': address_list,
                'request_timeout': self.config.timeout,
            }

            # Credentials are given to the client only if a username was configured -
            # otherwise the server is assumed to accept unauthenticated connections.
            if self.config.username:
                client_config['basic_auth'] = (self.config.username, password)

            # A CA certificates file to verify the server's certificate against
            if self.config.tls_ca_certs_file:
                client_config['ca_certs'] = self.config.tls_ca_certs_file

            # A combined client certificate and private key file, for mutual TLS
            if self.config.tls_cert_key_file:
                client_config['client_cert'] = self.config.tls_cert_key_file

            # Turning validation off also silences the warning the client would emit otherwise
            if not self.config.is_tls_validation_enabled:
                client_config['verify_certs'] = False
                client_config['ssl_show_warn'] = False

            # Create the actual connection object - the client connects lazily,
            # which is why there is no ping here - pinging would block the init
            # greenlet when a server is down and it would race with edits
            # or deletes that close the client mid-flight. Explicit pings,
            # e.g. from the dashboard, still go through self._ping.
            self._impl = Elasticsearch(**client_config)
            self.is_connected = True

# ################################################################################################################################

    def _delete(self) -> 'None':
        self._impl.close()

# ################################################################################################################################

    def _ping(self) -> 'None':
        _ = self._impl.info()

# ################################################################################################################################
# ################################################################################################################################
