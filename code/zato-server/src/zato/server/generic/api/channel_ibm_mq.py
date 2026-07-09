# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.server.base.parallel import ParallelServer

logger = getLogger(__name__)

class ChannelIBMMQWrapper:
    """ Config holder for an IBM MQ channel - actual connections are in Rust (QueueBridge).
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        self.config = config
        self.server = server
        logger.info('IBM MQ channel `%s` registered', config.name)

    def delete(self) -> 'None':
        pass

    def build_wrapper(self) -> 'None':
        pass
