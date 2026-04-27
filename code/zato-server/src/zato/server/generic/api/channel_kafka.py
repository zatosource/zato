# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.server.connection.queue import Wrapper

if 0:
    from bunch import Bunch
    from zato.server.base.parallel import ParallelServer

logger = getLogger(__name__)

class ChannelKafkaWrapper(Wrapper):
    """ Wraps a Kafka channel connection managed by the Rust QueueBridge.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        config.parent = self
        config.auth_url = config.address
        super(ChannelKafkaWrapper, self).__init__(config, 'Kafka channel', server)

    def add_client(self):
        logger.info('Kafka channel `%s` registered', self.config.name)
