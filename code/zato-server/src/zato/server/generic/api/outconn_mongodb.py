# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from uuid import uuid4

# Bunch
from bunch import bunchify

# PyMongo
from pymongo import MongoClient

# Zato
from zato.server.connection.wrapper import Wrapper

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class OutconnMongoDBWrapper(Wrapper):
    """ Wraps a MongoDB connection client.
    """
    wrapper_type = 'MongoDB connection'

    def __init__(self, *args, **kwargs):
        super(OutconnMongoDBWrapper, self).__init__(*args, **kwargs)
        self._impl = None  # type: MongoClient

# ################################################################################################################################

    def _init_impl(self):

        with self.update_lock:

            write_to_replica = self.config.write_to_replica
            if not isinstance(write_to_replica, int) or isinstance(write_to_replica, bool):
                try:
                    write_to_replica = int(write_to_replica)
                except(ValueError, TypeError):
                    write_to_replica = 0

            # Configuration of the underlying client
            client_config = bunchify({
                'host': self.config.server_list.splitlines(),
                'tz_aware': self.config.is_tz_aware,
                'connect': True,
                'maxPoolSize': self.config.pool_size_max,
                'minPoolSize': 0,
                'maxIdleTimeMS': self.config.max_idle_time * 1000,
                'socketTimeoutMS': self.config.socket_timeout * 1000,
                'connectTimeoutMS': self.config.connect_timeout * 1000,
                'serverSelectionTimeoutMS': self.config.server_select_timeout * 1000,
                'waitQueueTimeoutMS': self.config.wait_queue_timeout * 1000,
                'heartbeatFrequencyMS': self.config.hb_frequency * 1000,
                'appname': self.config.app_name,
                'retryWrites': self.config.should_retry_write,
                'zlibCompressionLevel': self.config.zlib_level,
                'w': write_to_replica,
                'wTimeoutMS': self.config.write_timeout,
                'journal': self.config.is_write_journal_enabled,
                'fsync': self.config.is_write_fsync_enabled,
                'replicaSet': self.config.replica_set or None,
                'readPreference': self.config.read_pref_type,
                'readPreferenceTags': self.config.read_pref_tag_list or '',
                'maxStalenessSeconds': self.config.read_pref_max_stale,
                'username': self.config.username,
                'password': self.config.secret or self.config.get('password') or '{}.{}'.format(self.__class__.__name__, uuid4().hex),
                'authSource': self.config.auth_source,
                'authMechanism': self.config.auth_mechanism,
            })

            client_config.password = self.server.decrypt(client_config.password) # type: ignore

            if self.config.document_class:
                client_config.document_class = self.config.document_class

            if self.config.compressor_list:
                client_config.compressors = self.config.compressor_list

            if self.config.is_tls_enabled:
                client_config.ssl = self.config.is_tls_enabled
                client_config.ssl_certfile = self.config.tls_cert_file
                client_config.ssl_keyfile = self.config.tls_private_key_file
                client_config.ssl_pem_passphrase = self.config.tls_pem_passphrase
                client_config.ssl_cert_reqs = self.config.tls_validate
                client_config.ssl_ca_certs = self.config.tls_ca_certs_file
                client_config.ssl_crlfile = self.config.tls_crl_file
                client_config.ssl_match_hostname = self.config.is_tls_match_hostname_enabled

            # Create the actual connection object
            self._impl = MongoClient(**client_config)

            # Confirm the connection was established
            self.ping()

            # We can assume we are connected now
            self.is_connected = True

# ################################################################################################################################

    def _delete(self):
        self._impl.close()

# ################################################################################################################################

    def _ping(self):
        self._impl.admin.command('ismaster')

# ################################################################################################################################
# ################################################################################################################################
