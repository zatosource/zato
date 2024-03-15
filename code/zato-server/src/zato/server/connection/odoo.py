# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from traceback import format_exc

# gevent
from gevent.lock import RLock

# Zato
from zato.common.const import SECRETS
from zato.common.util.api import ping_odoo
from zato.server.connection.queue import ConnectionQueue

# Python 2/3 compatibility
from six import PY2

if PY2:
    import openerplib as client_lib
else:
    import odoolib as client_lib

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class OdooWrapper:
    """ Wraps a queue of connections to Odoo.
    """
    def __init__(self, config, server):
        self.config = config
        self.server = server

        # Decrypt the password if it is encrypted. It will be in clear text when the server is starting up
        # but otherwise for connections created in run-time, it will be decrypted.
        if self.config.password.startswith(SECRETS.PREFIX):
            self.config.password = self.server.decrypt(self.config.password)

        self.url = '{protocol}://{user}:******@{host}:{port}/{database}'.format(**self.config)
        self.client = ConnectionQueue(
            self.server,
            self.config.is_active,
            self.config.pool_size,
            self.config.queue_build_cap,
            self.config.id,
            self.config.name,
            'Odoo',
            self.url,
            self.add_client
        )

        self.update_lock = RLock()
        self.logger = getLogger(self.__class__.__name__)

    def build_queue(self):
        with self.update_lock:
            self.client.build_queue()

    def add_client(self):

        conn = client_lib.get_connection(hostname=self.config.host, protocol=self.config.protocol, port=self.config.port,
            database=self.config.database, login=self.config.user, password=self.config.password)

        try:
            ping_odoo(conn)
        except Exception:
            logger.warning('Could not ping Odoo (%s), e:`%s`', self.config.name, format_exc())

        self.client.put_client(conn)

# ################################################################################################################################
