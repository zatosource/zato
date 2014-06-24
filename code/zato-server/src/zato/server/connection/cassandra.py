# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Cassandra
from cassandra.cluster import Cluster

# gevent
from gevent.lock import RLock

class CassandraConnStore(object):
    """ Stores connections to Cassandra.
    """
    def __init__(self):
        self.conns = {}
        self.lock = RLock()

    def add(self, name, config):
        with self.lock:
            pass