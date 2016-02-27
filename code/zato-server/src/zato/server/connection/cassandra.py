# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Cassandra
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.io.geventreactor import GeventConnection
from cassandra.query import dict_factory

# Zato
from zato.common.broker_message import DEFINITION
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
    conn_name = 'Cassandra'
    dispatcher_events = [DEFINITION.CASSANDRA_DELETE, DEFINITION.CASSANDRA_EDIT]

# ################################################################################################################################

    def create_session(self, name, config, config_no_sensitive):
        auth_provider = PlainTextAuthProvider(config.username, config.password) if config.get('username') else None

        tls_options = {}
        for msg_name, stdlib_name in msg_to_stdlib.items():
            if config.get(msg_name):
                tls_options[stdlib_name] = config[msg_name]

        cluster = Cluster(
            config.contact_points.splitlines(), int(config.port), cql_version=config.cql_version,
            protocol_version=int(config.proto_version), executor_threads=int(config.exec_size),
            auth_provider=auth_provider, ssl_options=tls_options, control_connection_timeout=3,
            connection_class=GeventConnection)

        session = cluster.connect()
        session.row_factory = dict_factory
        session.set_keyspace(config.default_keyspace)

        return session

# ################################################################################################################################

    def delete_session(self, name):
        """ Deletes a connection session. Must be called with self.lock held.
        """
        session = self.sessions.get(name)
        if session:
            try:
                self.keep_connecting.remove(session.config.id)
            except KeyError:
                pass # It's OK, no ongoing connection attempt at the moment

            session.conn.shutdown()

        logger.debug('Could not delete session `%s` - not among `%s`', name, self.sessions)

# ################################################################################################################################

    def on_dispatcher_events(self, events):
        """ Handles in-process dispatcher events. If it's a DELETE, the connection is removed
        from a list of connections to be established. If an EDIT, the connection's config is updated.
        In either case all subsequent dispatcher events are discarded.
        """
        # Only check the latest event
        event = events[-1]
        is_delete = event.event_info.event == DEFINITION.CASSANDRA_DELETE

        if is_delete:
            self.keep_connecting.remove(event.item.config.id)
        else:
            new_config = event.event_info.ctx

        # We always delete all the events because we processed the last one anyway
        for event in events:
            self.dispatcher_backlog.remove(event.event_info)

        # Stop connecting if we have just been deleted
        return (False, None) if is_delete else (True, new_config)

# ################################################################################################################################
