# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from logging import getLogger
from traceback import format_exc

# bunch
from bunch import Bunch

# Cassandra
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.query import dict_factory

# Zato
from zato.common import SECRET_SHADOW
from zato.server.connection import BaseConnPoolStore, BasePoolAPI

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

msg_to_stdlib = {
    'tls_ca_certs': 'ca_certs',
    'tls_client_cert': 'certfile',
    'tls_client_priv_key': 'keyfile',
    }

# ################################################################################################################################

class CassandraAPI(BasePoolAPI):
    """ API through which connections to Cassandra can be obtained.
    """

# ################################################################################################################################

class CassandraConnStore(BaseConnPoolStore):
    """ Stores connections to Cassandra.
    """

# ################################################################################################################################

    def create_connection(self, name, config):
        config_no_sensitive = deepcopy(config)
        config_no_sensitive['password'] = SECRET_SHADOW

        item = Bunch(config=config, config_no_sensitive=config_no_sensitive, is_connected=False, conn=None)

        try:
            auth_provider = PlainTextAuthProvider(config.username, config.password) if config.username else None

            tls_options = {}
            for msg_name, stdlib_name in msg_to_stdlib.items():
                if config.get(msg_name):
                    tls_options[stdlib_name] = config[msg_name]

            cluster = Cluster(
                config.contact_points.splitlines(), int(config.port), cql_version=config.cql_version,
                protocol_version=int(config.proto_version), executor_threads=int(config.exec_size),
                auth_provider=auth_provider, ssl_options=tls_options)

            logger.debug('Connecting to `%s`', config_no_sensitive)

            session = cluster.connect()
            session.row_factory = dict_factory
            session.set_keyspace(config.default_keyspace)

            logger.debug('Connected to `%s`', config_no_sensitive)
        except Exception, e:
            logger.warn('Could not connect to Cassandra `%s`, config:`%s`, e:`%s`', name, config_no_sensitive, format_exc(e))
        else:
            item.conn = session
            item.is_connected = True

        self.sessions[name] = item

        return item

# ################################################################################################################################

    def delete_connection(self, name):
        """ Actually deletes a definition. Must be called with self.lock held.
        """
        try:
            if not name in self.sessions:
                raise Exception('No such name `{}` among `{}`'.format(name, self.sessions.keys()))

            if self.sessions[name].is_connected:
                self.sessions[name].conn.shutdown()
        except Exception, e:
            logger.warn('Error while shutting down session `%s`, e:`%s`', name, format_exc(e))
        finally:
            del self.sessions[name]

# ################################################################################################################################