# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from traceback import format_exc

# gevent
from gevent.lock import RLock

# python-swiftclient
from swiftclient.client import Connection

# Zato
from zato.common.util import parse_extra_into_dict
from zato.server.connection.queue import ConnectionQueue

class SwiftWrapper(object):
    """ Wraps a queue of connections to OpenStack Swift.
    """
    def __init__(self, config, server):
        self.config = config
        self.server = server

        self.client = ConnectionQueue(
            self.config.pool_size, self.config.queue_build_cap, self.config.name, 'OpenStack Swift', self.config.auth_url,
            self.add_client)

        self.update_lock = RLock()
        self.logger = getLogger(self.__class__.__name__)

    def build_queue(self):
        with self.update_lock:
            self.client.build_queue()

    def add_client(self):
        conn = Connection(authurl=self.config.auth_url, user=self.config.user, key=self.config.key, retries=self.config.retries,
                 snet=self.config.is_snet, starting_backoff=float(self.config.starting_backoff),
                 max_backoff=float(self.config.max_backoff), tenant_name=self.config.tenant_name,
                 os_options=parse_extra_into_dict(self.config.custom_options), auth_version=self.config.auth_version,
                 cacert=self.config.cacert, insecure=not self.config.should_validate_cert,
                 ssl_compression=self.config.needs_tls_compr, retry_on_ratelimit=self.config.should_retr_ratelimit)
        try:
            conn.head_account()
        except Exception:
            self.logger.warn('Could not HEAD an account (%s), e:`%s`', self.config.name, format_exc())

        self.client.put_client(conn)
