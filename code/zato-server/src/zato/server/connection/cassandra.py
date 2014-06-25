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
from cassandra.cluster import Cluster

# gevent
from gevent.lock import RLock

# Zato
from zato.common import PASSWORD_SHADOW

logger = getLogger(__name__)

class CassandraAPI(object):
    def __init__(self, conn_store):
        self.conn = conn_store

class CassandraConnStore(object):
    """ Stores connections to Cassandra.
    """
    def __init__(self):
        self.sessions = {}
        self.lock = RLock()

    def __getitem__(self, name):
        return self.sessions[name]

    def get(self, name):
        return self.sessions.get(name)

    def _add(self, name, config):
        """ Actually adds a new definition, must be called with self.lock held.
        """
        config_no_sensitive = deepcopy(config)
        config_no_sensitive['password'] = PASSWORD_SHADOW

        item = Bunch(config=config, config_no_sensitive=config_no_sensitive, is_connected=False, conn=None)

        try:
            cluster = Cluster(
                config.contact_points.splitlines(), int(config.port), cql_version=config.cql_version,
                protocol_version=int(config.proto_version), executor_threads=int(config.exec_size))

            logger.debug('Connecting to `%s`', config_no_sensitive)

            session = cluster.connect()
            session.set_keyspace(config.default_keyspace)

            logger.debug('Connected to `%s`', config_no_sensitive)
        except Exception, e:
            logger.warn('Could not connect to Cassandra `%s`, config:`%s`, e:`%s`', name, config_no_sensitive, format_exc(e))
        else:
            item.conn = session
            item.is_connected = True

        self.sessions[name] = item

    def create(self, name, config):
        """ Adds a new connection definition.
        """
        with self.lock:
            self._add(name, config)

    def _delete(self, name):
        """ Actually deletes a definition. Must be called with self.lock held.
        """
        try:
            if self.sessions[name].is_connected:
                self.sessions[name].conn.shutdown()
        except Exception, e:
            logger.warn('Error while shutting down session `%s`, e:`%s`', name, format_exc(e))
        finally:
            del self.sessions[name]

    def delete(self, name):
        """ Deletes an existing connection.
        """
        with self.lock:
            self._delete(name)

    def edit(self, del_name, config):
        with self.lock:
            self._delete(del_name)
            self._add(config.name, config)
