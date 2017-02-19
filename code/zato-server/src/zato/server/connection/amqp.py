# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Zato
from zato.server.connection.connector import Connector

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class ConnectorAMQP(Connector):
    """ An AMQP connector under which channels or outgoing connections run.
    """
    start_in_greenlet = True

    def _start(self):
        logger.warn('_start %s', self)

    def _stop(self):
        logger.warn('_stop %s', self)

    def get_log_details(self):
        return 'amqp://{}:*****@{}:{}{}'.format(self.config.username, self.config.host, self.config.port, self.config.vhost)

    def invoke(self, name, *args, **kwargs):
        logger.warn('invoke %s', self)

# ################################################################################################################################

