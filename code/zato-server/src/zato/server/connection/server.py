# -*- coding: utf-8 -*-

"""
Copyright (C) 2015 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from logging import getLogger

# Zato
from zato.common.util import make_repr
from zato.common.odb.query import server_list

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class _Server(object):
    """ API through which it is possible to invoke services directly on other servers or clusters.
    """
    def __init__(self, cluster_id, cluster_name, name, preferred_address, port, crypto_use_tls):
        self.cluster_id = cluster_id
        self.cluster_name = cluster_name
        self.name = name
        self.preferred_address = preferred_address
        self.port = port
        self.crypto_use_tls = crypto_use_tls
        self.address = 'http{}://{}:{}/zato/internal/invoke'.format(
            's' if self.crypto_use_tls else '', self.preferred_address, self.port)

    def __repr__(self):
        return make_repr(self)

    def invoke(self, service, request=None, *args, **kwargs):
        logger.warn('eee %r', self)

    def invoke_async(self, service, request=None, *args, **kwargs):
        raise NotImplementedError()

# ################################################################################################################################

class Servers(object):
    """ A cache of servers already known to exist.
    """
    def __init__(self, odb, cluster_name):
        self.odb = odb
        self.cluster_name = cluster_name
        self._servers = {}

    def __getitem__(self, address):
        return self._servers.setdefault(address, self._add_server(address))

    def get(self, name):
        return self._servers.get(address)

    def _add_server(self, address):

        # It must be server@cluster
        if '@' in address:
            server, cluster = address.split('@')
        else:
            server = address
            cluster = self.cluster_name

        with closing(self.odb.session()) as session:
            for item in server_list(session, None, self.cluster_name, False):
                return _Server(
                    item.cluster_id, self.cluster_name, item.name, item.preferred_address, item.bind_port, item.crypto_use_tls)

# ################################################################################################################################