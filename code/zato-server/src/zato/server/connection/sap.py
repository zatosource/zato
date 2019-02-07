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

# Zato
from zato.common.util import ping_sap
from zato.server.connection.queue import ConnectionQueue

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class SAPWrapper(object):
    """ Wraps a queue of connections to SAP RFC.
    """
    def __init__(self, config, server):

        # Imported here because not everyone will be using SAP
        import pyrfc
        self.pyrfc = pyrfc
        self.config = config
        self.server = server
        self.url = 'rfc://{user}@{host}:{sysnr}/{client}'.format(**self.config)
        self.client = ConnectionQueue(
            self.config.pool_size, self.config.queue_build_cap, self.config.name, 'SAP', self.url, self.add_client)

        self.update_lock = RLock()
        self.logger = getLogger(self.__class__.__name__)

    def build_queue(self):
        with self.update_lock:
            self.client.build_queue()

    def add_client(self):
        conn = self.pyrfc.Connection(user=self.config.user, passwd=self.config.password,
            ashost=self.config.host, sysnr=self.config.sysnr, client=self.config.client)

        try:
            ping_sap(conn)
        except Exception:
            self.logger.warn('Could not ping SAP (%s), e:`%s`', self.config.name, format_exc())

        self.client.put_client(conn)

# ################################################################################################################################
