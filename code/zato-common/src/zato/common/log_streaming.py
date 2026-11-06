# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
from collections import deque
from datetime import datetime
from threading import Event, Thread
from traceback import format_exc

# redis
from redis import Redis

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from logging import LogRecord

    LogRecord = LogRecord

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How many entries the log stream may hold - older ones are trimmed away by Redis itself.
max_log_stream_entries = 1000

# The loggers whose records are never streamed
_excluded_logger_names = {'zato.common.log_streaming', 'zato.stream_manager', 'zato.sse_stream', 'zato.admin.web.util'}

strdeque = deque[str]

# ################################################################################################################################
# ################################################################################################################################

class RedisHandler(logging.Handler):
    """ Adds log records to a capped Redis stream. The handler only queues each entry in memory
    and a writer of its own sends the queue to Redis, so the lock of the handler is never held
    while a greenlet waits for the network.
    """
    def __init__(
        self,
        channel:'str'='zato.logs',
        redis_host:'str'='localhost',
        redis_port:'int'=6379,
        redis_db:'int'=0,
        ) -> 'None':

        super().__init__()

        self.channel = channel
        self.client = Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

        # The queue holds no more entries than the stream itself retains ..
        self.pending:'strdeque' = deque(maxlen=max_log_stream_entries)
        self.has_pending = Event()

        # .. and the writer is the only place that sends them to Redis.
        self.writer = Thread(target=self._write_pending, name='zato-log-streaming', daemon=True)
        self.writer.start()

# ################################################################################################################################

    def _write_pending(self) -> 'None':

        while True:

            # Wait until there is anything to write ..
            _ = self.has_pending.wait()
            self.has_pending.clear()

            # .. collect everything queued so far ..
            pipeline = self.client.pipeline(transaction=False)

            while self.pending:
                data = self.pending.popleft()
                _ = pipeline.xadd(self.channel, {'data': data}, maxlen=max_log_stream_entries, approximate=True)

            # .. and write it in one round trip.
            try:
                _ = pipeline.execute()
            except Exception:
                logger.warning('Could not write log entries to stream `%s` -> %s', self.channel, format_exc())

# ################################################################################################################################

    def emit(self, record:'LogRecord') -> 'None':

        if record.name in _excluded_logger_names:
            return

        try:
            if record.args:
                try:
                    record.msg = record.msg % record.args
                except (TypeError, ValueError):
                    record.msg = str(record.msg)
                record.args = None
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

            # A capped stream, unlike pubsub, retains entries so readers can poll for them later.
            data = json.dumps(log_entry)
            self.pending.append(data)
            self.has_pending.set()

        except Exception:
            self.handleError(record)

# ################################################################################################################################
# ################################################################################################################################

class LogStreamingManager:

    loggers_to_stream = {
        'zato_rest',
        'zato.hot-deploy.create',
        # 'zato_access_log',
        # 'zato_redis',
        # 'zato_admin'
    }

    def __init__(self, logger_name:'str'='') -> 'None':
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

            for logger_name in self.loggers_to_stream:
                logger_obj = logging.getLogger(logger_name)
                if redis_handler not in logger_obj.handlers:
                    logger_obj.addHandler(redis_handler)

            return True
        return False

    def disable_streaming(self):
        redis_handler = self.get_redis_handler()
        stream_logger = logging.getLogger('zato.stream_manager')
        stream_logger.info('LogStreamingManager.disable_streaming: called for logger "{}"'.format(self.logger_name))

        if redis_handler in self.logger.handlers:
            stream_logger.info('LogStreamingManager.disable_streaming: removing redis_handler from logger')
            self.logger.removeHandler(redis_handler)

            for logger_name in self.loggers_to_stream:
                logger_obj = logging.getLogger(logger_name)
                stream_logger.info('LogStreamingManager.disable_streaming: checking logger "{}"'.format(logger_name))
                if redis_handler in logger_obj.handlers:
                    stream_logger.info('LogStreamingManager.disable_streaming: removing RedisHandler from "{}"'.format(logger_name))
                    logger_obj.removeHandler(redis_handler)
                else:
                    stream_logger.info('LogStreamingManager.disable_streaming: RedisHandler not in "{}"'.format(logger_name))

            stream_logger = logging.getLogger('zato.stream_manager')
            stream_logger.info('LogStreamingManager: disabled streaming on logger "{}"'.format(self.logger_name))
            return True
        stream_logger = logging.getLogger('zato.stream_manager')
        stream_logger.info('LogStreamingManager: streaming already disabled on logger "{}"'.format(self.logger_name))
        return False

    def toggle_streaming(self):
        if self.is_streaming_enabled():
            _ = self.disable_streaming()
            return False
        else:
            _ = self.enable_streaming()
            return True

# ################################################################################################################################
# ################################################################################################################################
