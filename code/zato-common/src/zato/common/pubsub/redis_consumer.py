# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass
from json import loads
from logging import getLogger

# gevent
from gevent import sleep, spawn

# redis
from redis import Redis

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
    Channel_Prefix = 'zato:broker:channel:'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RedisConsumerConfig:
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

class RedisConsumer:

    def __init__(self, config:'RedisConsumerConfig', redis_conn:'Redis | None'=None) -> 'None':
        self.config = config
        self.is_connected = False
        self.keep_running = True
        self._greenlet = None

        # Get Redis connection
        if redis_conn:
            self.redis = redis_conn
        else:
            redis_host = os.environ.get('Zato_Redis_Host', 'localhost')
            redis_port = int(os.environ.get('Zato_Redis_Port', '6379'))
            redis_db = int(os.environ.get('Zato_Redis_DB', '0'))
            redis_password = os.environ.get('Zato_Redis_Password', None)
            self.redis = Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=True
            )

        self.channel_name = f'{ModuleCtx.Channel_Prefix}{config.queue_name}'
        self._pubsub = None

# ################################################################################################################################

    def start(self) -> 'None':
        """ Start consuming messages from Redis channel.
        """
        self._pubsub = self.redis.pubsub()
        self._pubsub.subscribe(self.channel_name)
        self.is_connected = True

        logger.info(f'Redis consumer subscribed to channel: {self.channel_name}')

        while self.keep_running:
            try:
                message = self._pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    self._process_message(message)
            except Exception as e:
                if self.keep_running:
                    logger.warning(f'Error in Redis consumer loop: {e}')
                sleep(0.1)

# ################################################################################################################################

    def _process_message(self, message:'dict') -> 'None':
        """ Process a received message.
        """
        try:
            data = message['data']

            if isinstance(data, bytes):
                data = data.decode('utf-8')

            body = loads(data)

            class _RedisMsg:
                def ack(self):
                    pass
                def reject(self, requeue=False):
                    pass

            redis_msg = _RedisMsg()

            # Call the callback
            self.config.on_msg_callback(body, redis_msg, self.config.name, {})

        except Exception as e:
            logger.warning(f'Error processing Redis message: {e}')

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stop the consumer.
        """
        self.keep_running = False
        self.is_connected = False

        if self._pubsub:
            try:
                self._pubsub.unsubscribe()
                self._pubsub.close()
            except Exception:
                pass
            self._pubsub = None

        logger.info(f'Redis consumer stopped for channel: {self.channel_name}')

# ################################################################################################################################
# ################################################################################################################################

def start_redis_consumer(consumer_config:'RedisConsumerConfig', redis_conn:'Redis | None'=None) -> 'RedisConsumer':
    """ Start a Redis consumer.
    """
    visibility = 'internal' if consumer_config.is_internal else 'public'
    cid_prefix = f'[{consumer_config.cid}] ' if consumer_config.cid else ''

    consumer = RedisConsumer(consumer_config, redis_conn)

    try:
        if consumer_config.should_start:
            logger.info(f'{cid_prefix}Starting {visibility} Redis consumer for channel={consumer_config.queue_name}')

            _ = spawn(consumer.start)

            if consumer_config.wait_for_connection:
                while not consumer.is_connected:
                    if not consumer.keep_running:
                        break
                    sleep(0.2)

    except KeyboardInterrupt:
        consumer.stop()
        logger.info(f'{cid_prefix}Stopped {visibility} Redis consumer for channel={consumer_config.queue_name}')

    except Exception as e:
        logger.warning(f'{cid_prefix} REDIS CONSUMER {e}')

    finally:
        return consumer

# ################################################################################################################################
# ################################################################################################################################

def start_internal_redis_consumer(
    name: 'str',
    queue_name: 'str',
    consumer_tag_prefix: 'str',
    on_msg_callback: 'callable_',
    redis_conn: 'Redis | None' = None
) -> 'RedisConsumer':
    """ Start an internal Redis consumer.
    """
    config = RedisConsumerConfig()
    config.name = name
    config.is_internal = True
    config.queue_name = queue_name
    config.consumer_tag_prefix = consumer_tag_prefix
    config.on_msg_callback = on_msg_callback
    config.wait_for_connection = True
    config.should_start = True

    consumer = start_redis_consumer(config, redis_conn)
    return consumer

# ################################################################################################################################
# ################################################################################################################################
