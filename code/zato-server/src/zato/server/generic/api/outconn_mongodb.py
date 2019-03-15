# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from traceback import format_exc
from uuid import uuid4

# Bunch
from bunch import bunchify

# PyMongo
from pymongo import MongoClient

# Zato
from zato.common.util import spawn_greenlet
from zato.server.connection.wrapper import Wrapper

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class OutconnMongoDBWrapper(Wrapper):
    """ Wraps a MongoDB connection client.
    """
    def __init__(self, *args, **kwargs):
        super(OutconnMongoDBWrapper, self).__init__(*args, **kwargs)
        self.client = None  # type: MongoClient

# ################################################################################################################################

    def _init(self):

        if not self.config.is_active:
            logger.info('Skipped building an inactive MongoDB connection `%s`', self.config.name)

        # Configuration of the underlying client
        client_config = bunchify({
            'host': self.config.server_list.splitlines(),
            'tz_aware': self.config.is_tz_aware,
            'connect': True,
            'maxPoolSize': self.config.pool_size_max,
            'minPoolSize': 0,
            'maxIdleTimeMS': self.config.max_idle_time,
            'socketTimeoutMS': self.config.socket_timeout * 1000,
            'connectTimeoutMS': self.config.connect_timeout * 1000,
            'serverSelectionTimeoutMS': self.config.server_select_timeout * 1000,
            'waitQueueTimeoutMS': self.config.wait_queue_timeout * 1000,
            'heartbeatFrequencyMS': self.config.hb_frequency * 1000,
            'appname': self.config.app_name,
            'retryWrites': self.config.should_retry_write,
            'zlibCompressionLevel': self.config.zlib_level,
            'w': self.config.write_to_replica,
            'wtimeout': self.config.write_timeout,
            'j': self.config.is_write_journal_enabled,
            'fsync': self.config.is_write_fsync_enabled,
            'replicaSet': self.config.replica_set,
            'readPreference': self.config.read_pref_type,
            'readPreferenceTags': self.config.read_pref_tag_list or '',
            'maxStalenessSeconds': self.config.read_pref_max_stale,
            'username': self.config.username,
            'password': self.config.secret or '{}.{}'.format(self.__class__.__name__, uuid4().hex),
            'authSource': self.config.auth_source,
            'authMechanism': self.config.auth_mechanism,
        })

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
        self.client = MongoClient(**client_config)

        # Confirm the connection was established
        self.ping()

# ################################################################################################################################

    def _delete(self):
        self.client.close()

# ################################################################################################################################

    def _ping(self):
        self.client.admin.command('ismaster')

# ################################################################################################################################
# ################################################################################################################################
