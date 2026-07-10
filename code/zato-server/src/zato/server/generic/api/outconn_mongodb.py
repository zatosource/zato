# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# PyMongo
from pymongo import MongoClient

# Zato
from zato.common.api import MongoDB
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

# How many milliseconds one second has - the client expects timeouts in milliseconds
# while the configuration keeps them in seconds.
_ms_per_second = 1000

# Default values applied when a configuration key is missing or None
outconn_mongodb_config_defaults:'dict[str, object]' = {
    'server_list': MongoDB.Default.Server_List,
    'username': '',
    'auth_source': MongoDB.Default.Auth_Source,
    'replica_set': '',
    'app_name': MongoDB.Default.App_Name,
    'pool_size_max': MongoDB.Default.Pool_Size_Max,
    'connect_timeout': MongoDB.Default.Connect_Timeout,
    'server_select_timeout': MongoDB.Default.Server_Select_Timeout,
    'is_tls_enabled': False,
    'tls_ca_certs_file': '',
    'tls_cert_key_file': '',
    'is_tls_validation_enabled': True,
}

# Config keys that must be integers but may arrive as strings from opaque storage
outconn_mongodb_int_config_keys = ('pool_size_max', 'connect_timeout', 'server_select_timeout')

# Config keys that must be booleans but may arrive as strings from opaque storage
outconn_mongodb_bool_config_keys = ('is_tls_enabled', 'is_tls_validation_enabled')

# ################################################################################################################################
# ################################################################################################################################

class OutconnMongoDBWrapper(Wrapper):
    """ Wraps a MongoDB connection client.
    """
    wrapper_type = 'MongoDB connection'

    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        super(OutconnMongoDBWrapper, self).__init__(config, server)
        self._impl:'MongoClient' = cast_('MongoClient', None)

# ################################################################################################################################

    def _init_impl(self) -> 'None':

        with self.update_lock:

            # Each line of the configuration is one host:port pair to connect to
            server_list:'strlist' = self.config.server_list.splitlines()

            # The password may still be encrypted if it went through a path
            # that did not decrypt it - decrypting a plain string is a no-op.
            password = self.server.decrypt(self.config.secret)

            # Timeouts are configured in seconds but the client expects milliseconds
            connect_timeout_ms = self.config.connect_timeout * _ms_per_second
            server_select_timeout_ms = self.config.server_select_timeout * _ms_per_second

            # Configuration of the underlying client
            client_config:'stranydict' = {
                'host': server_list,
                'appname': self.config.app_name,
                'maxPoolSize': self.config.pool_size_max,
                'connectTimeoutMS': connect_timeout_ms,
                'serverSelectionTimeoutMS': server_select_timeout_ms,
            }

            # Credentials are given to the client only if a username was configured -
            # otherwise the server is assumed to accept unauthenticated connections.
            if self.config.username:
                client_config['username'] = self.config.username
                client_config['password'] = password
                client_config['authSource'] = self.config.auth_source

            # A replica set name is optional
            if self.config.replica_set:
                client_config['replicaSet'] = self.config.replica_set

            # TLS is optional too and all of its options use the pymongo 4 names
            if self.config.is_tls_enabled:
                client_config['tls'] = True

                if self.config.tls_ca_certs_file:
                    client_config['tlsCAFile'] = self.config.tls_ca_certs_file

                if self.config.tls_cert_key_file:
                    client_config['tlsCertificateKeyFile'] = self.config.tls_cert_key_file

                if not self.config.is_tls_validation_enabled:
                    client_config['tlsAllowInvalidCertificates'] = True

            # Create the actual connection object - the client connects lazily
            # and repairs its topology in the background, which is why there is
            # no ping here - pinging would block the init greenlet for the whole
            # server-selection timeout when a server is down and it would race
            # with edits or deletes that close the client mid-flight. Explicit
            # pings, e.g. from the dashboard, still go through self._ping.
            self._impl = MongoClient(**client_config)
            self.is_connected = True

# ################################################################################################################################

    def _delete(self) -> 'None':
        self._impl.close()

# ################################################################################################################################

    def _ping(self) -> 'None':
        _ = self._impl.admin.command('ping')

# ################################################################################################################################
# ################################################################################################################################
