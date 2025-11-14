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
        self.emit_count = 0

    def _get_redis_client(self):
        if self.redis_client is None:
            import redis
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                decode_responses=True
            )
        return self.redis_client

    def emit(self, record):
        if record.name in ('zato.common.log_streaming', 'zato.redis_handler', 'zato.stream_manager', 'zato.sse_stream', 'zato.admin.web.util'):
            return

        try:
            self.emit_count += 1

            message = self.format(record)
            level = record.levelname

            if 'Caught an exception' in message:
                level = 'ERROR'

            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': level,
                'message': message,
                'module': record.module,
                'funcName': record.funcName,
                'lineno': record.lineno
            }

            client = self._get_redis_client()
            json_data = json.dumps(log_entry)
            client.publish(self.channel, json_data)

        except Exception:
            from traceback import format_exc
            redis_logger = logging.getLogger('zato.redis_handler')
            redis_logger.error('RedisHandler.emit error: {}'.format(format_exc()))
            self.handleError(record)

# ################################################################################################################################
# ################################################################################################################################

class LogStreamingManager:

    loggers_to_stream = {
        'zato_rest',
        'zato.hot-deploy.create',
        # 'zato_access_log',
        # 'zato_kvdb',
        # 'zato_admin'
    }

    def __init__(self, logger_name=''):
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
            stream_logger = logging.getLogger('zato.stream_manager')
            stream_logger.info('LogStreamingManager: enabled streaming on logger "{}", propagate={}'.format(
                self.logger_name, self.logger.propagate))
            stream_logger.info('LogStreamingManager: logger level={}, handler count={}'.format(
                self.logger.level, len(self.logger.handlers)))

            for logger_name in self.loggers_to_stream:
                logger_obj = logging.getLogger(logger_name)
                if redis_handler not in logger_obj.handlers:
                    logger_obj.addHandler(redis_handler)
                    stream_logger.info('LogStreamingManager: added RedisHandler to {} logger'.format(logger_name))

            return True
        stream_logger = logging.getLogger('zato.stream_manager')
        stream_logger.info('LogStreamingManager: streaming already enabled on logger "{}"'.format(self.logger_name))
        return False

    def disable_streaming(self):
        redis_handler = self.get_redis_handler()

        if redis_handler in self.logger.handlers:
            self.logger.removeHandler(redis_handler)

            for logger_name in self.loggers_to_stream:
                logger_obj = logging.getLogger(logger_name)
                if redis_handler in logger_obj.handlers:
                    logger_obj.removeHandler(redis_handler)

            stream_logger = logging.getLogger('zato.stream_manager')
            stream_logger.info('LogStreamingManager: disabled streaming on logger "{}"'.format(self.logger_name))
            return True
        stream_logger = logging.getLogger('zato.stream_manager')
        stream_logger.info('LogStreamingManager: streaming already disabled on logger "{}"'.format(self.logger_name))
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
