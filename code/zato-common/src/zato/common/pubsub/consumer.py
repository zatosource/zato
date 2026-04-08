# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass
from json import loads
from logging import getLogger

# gevent
from gevent import sleep, spawn

# zato-broker-core (Rust extension)
from zato_broker_core import (
    BrokerConfig,
    fs_init,
    fs_init_logging,
    fs_poll,
    fs_read_cursor,
    fs_update_cursor,
)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, strdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Channel_Prefix = ''

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

        broker_dir = os.environ.get('Zato_Broker_Dir') or os.path.expanduser('~/env/qs-1/data/broker')
        log_dir = os.environ.get('Zato_Broker_Log_Dir') or os.path.expanduser('~/env/qs-1/server1/logs')

        os.makedirs(log_dir, exist_ok=True)

        self._cfg = BrokerConfig(broker_dir, log_dir)
        self._poll_interval = float(os.environ.get('Zato_Broker_Poll_Interval', '0.05'))
        self.channel_name = f'{ModuleCtx.Channel_Prefix}{config.queue_name}'

# ################################################################################################################################

    def start(self) -> 'None':
        self.is_connected = True

        logger.info('Consumer subscribed to channel: %s', self.channel_name)

        try:
            cursor = fs_read_cursor(self._cfg, self.channel_name, self.config.queue_name)
        except Exception:
            cursor = 0

        while self.keep_running:
            try:
                messages = fs_poll(self._cfg, self.channel_name, cursor)
                for seq, meta_str, data_bytes in messages:
                    self._process_message(meta_str)
                    cursor = seq
                    try:
                        fs_update_cursor(self._cfg, self.channel_name, self.config.queue_name, cursor)
                    except Exception:
                        pass
            except Exception as e:
                if self.keep_running:
                    logger.warning('Error in consumer loop: %s', e)
            sleep(self._poll_interval)

# ################################################################################################################################

    def _process_message(self, data:'str') -> 'None':
        try:
            body = loads(data)

            class _Msg:
                def ack(self):
                    pass
                def reject(self, requeue=False):
                    pass

            msg = _Msg()

            self.config.on_msg_callback(body, msg, self.config.name, {})

        except Exception as e:
            logger.warning('Error processing message: %s', e)

# ################################################################################################################################

    def stop(self) -> 'None':
        self.keep_running = False
        self.is_connected = False
        logger.info('Consumer stopped for channel: %s', self.channel_name)

# ################################################################################################################################
# ################################################################################################################################

def start_consumer(consumer_config:'ConsumerConfig') -> 'Consumer':
    visibility = 'internal' if consumer_config.is_internal else 'public'
    cid_prefix = f'[{consumer_config.cid}] ' if consumer_config.cid else ''

    consumer = Consumer(consumer_config)

    try:
        if consumer_config.should_start:
            logger.info('%sStarting %s consumer for channel=%s', cid_prefix, visibility, consumer_config.queue_name)

            _ = spawn(consumer.start)

            if consumer_config.wait_for_connection:
                while not consumer.is_connected:
                    if not consumer.keep_running:
                        break
                    sleep(0.2)

    except KeyboardInterrupt:
        consumer.stop()
        logger.info('%sStopped %s consumer for channel=%s', cid_prefix, visibility, consumer_config.queue_name)

    except Exception as e:
        logger.warning('%s CONSUMER %s', cid_prefix, e)

    finally:
        return consumer

# ################################################################################################################################
# ################################################################################################################################

def start_internal_consumer(
    name: 'str',
    queue_name: 'str',
    consumer_tag_prefix: 'str',
    on_msg_callback: 'callable_',
) -> 'Consumer':
    config = ConsumerConfig()
    config.name = name
    config.is_internal = True
    config.queue_name = queue_name
    config.consumer_tag_prefix = consumer_tag_prefix
    config.on_msg_callback = on_msg_callback
    config.wait_for_connection = True
    config.should_start = True

    consumer = start_consumer(config)
    return consumer

# ################################################################################################################################
# ################################################################################################################################
