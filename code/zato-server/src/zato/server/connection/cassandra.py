# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from logging import getLogger

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
        self.conns = {}
        self.lock = RLock()

    def __getitem__(self, name):
        return self.conns[name]

    def get(self, name):
        return self.conns.get(name)

    def add(self, name, config):
        with self.lock:

            config_no_sensitive = deepcopy(config)
            config_no_sensitive['password'] = PASSWORD_SHADOW

            item = Bunch(config=config, config_no_sensitive=config_no_sensitive)

            cluster = Cluster(
                config.contact_points.splitlines(), int(config.port), cql_version=config.cql_version,
                protocol_version=int(config.proto_version), executor_threads=int(config.exec_size))

            logger.debug('Connecting to `%s`', config_no_sensitive)

            session = cluster.connect()
            session.set_keyspace(config.default_keyspace)

            logger.debug('Connected to `%s`', config_no_sensitive)

            item.conn = session
            self.conns[name] = item
