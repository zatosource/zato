# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
from datetime import datetime

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from redis import Redis
    Redis = Redis

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class RedisHandler(logging.Handler):

    def __init__(self, channel='zato.logs', redis_host='localhost', redis_port=6379, redis_db=0):
        super().__init__()
        self.channel = channel
        self.redis_client = None
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db

    def _get_redis_client(self):
        if self.redis_client is None:
            import redis
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                decode_responses=False
            )
        return self.redis_client

    def emit(self, record):
        try:
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': self.format(record),
                'module': record.module,
                'funcName': record.funcName,
                'lineno': record.lineno
            }

            client = self._get_redis_client()
            json_data = json.dumps(log_entry)
            result = client.publish(self.channel, json_data)
            logger.info('Published to Redis channel {}, subscribers: {}, data: {}'.format(self.channel, result, json_data))

        except Exception as e:
            logger.error('Error publishing to Redis: {}'.format(e))
            self.handleError(record)

# ################################################################################################################################
# ################################################################################################################################

class LogStreamingManager:

    def __init__(self, logger_name='zato'):
        self.logger_name = logger_name
        self.logger = logging.getLogger(logger_name)
        self.redis_handler = None

    def configure_logging(self):
        return self.logger

    def get_redis_handler(self):
        if self.redis_handler is None:
            self.redis_handler = RedisHandler(channel='zato.logs')
            self.redis_handler.setLevel(logging.DEBUG)
            redis_formatter = logging.Formatter('%(message)s')
            self.redis_handler.setFormatter(redis_formatter)

        return self.redis_handler

    def is_streaming_enabled(self):
        redis_handler = self.get_redis_handler()
        return redis_handler in self.logger.handlers

    def enable_streaming(self):
        redis_handler = self.get_redis_handler()

        if redis_handler not in self.logger.handlers:
            self.logger.addHandler(redis_handler)
            logger.info('Log streaming enabled, handler added to logger: {}'.format(self.logger_name))
            return True
        logger.info('Log streaming already enabled')
        return False

    def disable_streaming(self):
        redis_handler = self.get_redis_handler()

        if redis_handler in self.logger.handlers:
            self.logger.removeHandler(redis_handler)
            logger.info('Log streaming disabled, handler removed from logger: {}'.format(self.logger_name))
            return True
        logger.info('Log streaming already disabled')
        return False

    def toggle_streaming(self):
        if self.is_streaming_enabled():
            self.disable_streaming()
            return False
        else:
            self.enable_streaming()
            return True

# ################################################################################################################################
# ################################################################################################################################
