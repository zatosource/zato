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

class OutconnKafkaWrapper(Wrapper):
    """ Wraps an outgoing Kafka connection managed by the Rust QueueBridge.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        config.parent = self
        config.auth_url = config.address
        super(OutconnKafkaWrapper, self).__init__(config, 'outgoing Kafka', server)

    def add_client(self):
        logger.info('Outgoing Kafka connection `%s` registered', self.config.name)
