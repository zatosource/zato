# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from logging import getLogger

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, strdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ConsumerConfig:
    cid: 'str' = ''
    name: 'str' = ''
    is_internal: 'bool' = True
    queue_name: 'str' = ''
    consumer_tag_prefix: 'str' = ''
    on_msg_callback: 'callable_' = None
    wait_for_connection: 'bool' = True
    should_start: 'bool' = True

# ################################################################################################################################
# ################################################################################################################################

class Consumer:

    def __init__(self, config:'ConsumerConfig') -> 'None':
        self.config = config
        self.is_connected = False
        self.keep_running = True
        self._greenlet = None

# ################################################################################################################################

    def start(self) -> 'None':
        logger.warning('Consumer.start needs to be ported to streams')

# ################################################################################################################################

    def stop(self) -> 'None':
        self.keep_running = False
        self.is_connected = False

# ################################################################################################################################
# ################################################################################################################################

def start_consumer(consumer_config:'ConsumerConfig') -> 'Consumer':
    logger.warning('start_consumer needs to be ported to streams')
    return Consumer(consumer_config)

# ################################################################################################################################
# ################################################################################################################################

def start_internal_consumer(
    name: 'str',
    queue_name: 'str',
    consumer_tag_prefix: 'str',
    on_msg_callback: 'callable_',
) -> 'Consumer':
    logger.warning('start_internal_consumer needs to be ported to streams')
    config = ConsumerConfig()
    config.name = name
    config.queue_name = queue_name
    config.consumer_tag_prefix = consumer_tag_prefix
    config.on_msg_callback = on_msg_callback
    return Consumer(config)

# ################################################################################################################################
# ################################################################################################################################
