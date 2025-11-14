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
            client.publish(self.channel, json_data)

        except Exception:
            from traceback import format_exc
            redis_logger = logging.getLogger('zato.redis_handler')
            redis_logger.error('RedisHandler.emit error: {}'.format(format_exc()))
            self.handleError(record)

# ################################################################################################################################
# ################################################################################################################################

class LogStreamingManager:

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

            zato_rest_logger = logging.getLogger('zato_rest')
            stream_logger.info('LogStreamingManager: zato_rest logger level={}, propagate={}, handler count={}'.format(
                zato_rest_logger.level, zato_rest_logger.propagate, len(zato_rest_logger.handlers)))

            zato_rest_logger.addHandler(redis_handler)
            stream_logger.info('LogStreamingManager: added RedisHandler to zato_rest logger, new handler count={}'.format(
                len(zato_rest_logger.handlers)))

            zato_hotdeploy_logger = logging.getLogger('zato.hot-deploy.create')
            stream_logger.info('LogStreamingManager: zato.hot-deploy.create logger level={}, propagate={}, handler count={}'.format(
                zato_hotdeploy_logger.level, zato_hotdeploy_logger.propagate, len(zato_hotdeploy_logger.handlers)))
            
            zato_hotdeploy_logger.addHandler(redis_handler)
            stream_logger.info('LogStreamingManager: added RedisHandler to zato.hot-deploy.create logger, new handler count={}'.format(
                len(zato_hotdeploy_logger.handlers)))
            
            zato_access_log = logging.getLogger('zato_access_log')
            if redis_handler not in zato_access_log.handlers:
                zato_access_log.addHandler(redis_handler)
                stream_logger.info('LogStreamingManager: added RedisHandler to zato_access_log logger')
            
            zato_kvdb = logging.getLogger('zato_kvdb')
            if redis_handler not in zato_kvdb.handlers:
                zato_kvdb.addHandler(redis_handler)
                stream_logger.info('LogStreamingManager: added RedisHandler to zato_kvdb logger')
            
            zato_admin = logging.getLogger('zato_admin')
            if redis_handler not in zato_admin.handlers:
                zato_admin.addHandler(redis_handler)
                stream_logger.info('LogStreamingManager: added RedisHandler to zato_admin logger')

            return True
        stream_logger = logging.getLogger('zato.stream_manager')
        stream_logger.info('LogStreamingManager: streaming already enabled on logger "{}"'.format(self.logger_name))
        return False

    def disable_streaming(self):
        redis_handler = self.get_redis_handler()

        if redis_handler in self.logger.handlers:
            self.logger.removeHandler(redis_handler)

            zato_rest_logger = logging.getLogger('zato_rest')
            if redis_handler in zato_rest_logger.handlers:
                zato_rest_logger.removeHandler(redis_handler)

            zato_hotdeploy_logger = logging.getLogger('zato.hot-deploy.create')
            if redis_handler in zato_hotdeploy_logger.handlers:
                zato_hotdeploy_logger.removeHandler(redis_handler)
            
            zato_access_log = logging.getLogger('zato_access_log')
            if redis_handler in zato_access_log.handlers:
                zato_access_log.removeHandler(redis_handler)
            
            zato_kvdb = logging.getLogger('zato_kvdb')
            if redis_handler in zato_kvdb.handlers:
                zato_kvdb.removeHandler(redis_handler)
            
            zato_admin = logging.getLogger('zato_admin')
            if redis_handler in zato_admin.handlers:
                zato_admin.removeHandler(redis_handler)

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
