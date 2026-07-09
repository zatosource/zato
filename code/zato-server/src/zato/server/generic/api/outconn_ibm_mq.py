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

class OutconnIBMMQWrapper:
    """ Config holder for an outgoing IBM MQ connection - actual connections are in Rust (QueueBridge).
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        self.config = config
        self.server = server
        logger.info('Outgoing IBM MQ connection `%s` registered', config.name)

    def delete(self) -> 'None':
        pass

    def build_wrapper(self) -> 'None':
        pass
