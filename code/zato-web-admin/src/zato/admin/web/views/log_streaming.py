# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc
from threading import Lock

# Django
from django.http import HttpResponse, StreamingHttpResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# Track active SSE connections
_active_connections = 0
_connections_lock = Lock()

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def toggle_streaming(req):

    logger.info('toggle_streaming: called from client: {}'.format(req.META.get('REMOTE_ADDR')))
    response = req.zato.client.invoke('zato.log.streaming.toggle', {})
    logger.info('toggle_streaming: service response: {}'.format(response.data))

    return HttpResponse(dumps(response.data), content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_status(req):

    logger.info('get_status: called from client: {}'.format(req.META.get('REMOTE_ADDR')))
    response = req.zato.client.invoke('zato.log.streaming.status', {})
    logger.info('get_status: service response: {}'.format(response.data))

    return HttpResponse(dumps(response.data), content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def log_stream(req):

    global _active_connections
    stream_logger = getLogger('zato.sse_stream')
    stream_logger.info('log_stream: VIEW CALLED, client: {}'.format(req.META.get('REMOTE_ADDR')))

    def event_stream():

        global _active_connections

        # Redis
        import redis
        import time

        redis_client = None
        pubsub = None

        with _connections_lock:
            _active_connections += 1
            stream_logger.info('log_stream: connection opened, active_connections={}'.format(_active_connections))

        try:
            stream_logger.info('log_stream: GENERATOR STARTED')
            stream_logger.info('log_stream: attempting Redis connection')

            redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            stream_logger.info('log_stream: Redis client created, testing connection')

            _ = redis_client.ping()
            stream_logger.info('log_stream: Redis ping successful')

            pubsub = redis_client.pubsub()
            stream_logger.info('log_stream: pubsub created')

            pubsub.subscribe('zato.logs')
            stream_logger.info('log_stream: subscribed to zato.logs channel')

            yield ': connected\n\n'
            stream_logger.info('log_stream: sent initial connected message')
            stream_logger.info('log_stream: entering main message loop')

            last_keepalive = time.time()
            message_count = 0

            keepalive_count = 0
            while True:
                current_time = time.time()

                if current_time - last_keepalive >= 5:
                    keepalive_count += 1
                    stream_logger.info('log_stream: yielding keepalive #{}, time since last: {}'.format(
                        keepalive_count, current_time - last_keepalive))
                    yield ': keepalive\n\n'
                    last_keepalive = current_time

                message = pubsub.get_message()
                if message:
                    stream_logger.info('log_stream: got message from pubsub, type: {}'.format(message.get('type')))
                if message and message['type'] == 'message':
                    message_count += 1
                    log_data = message['data']
                    stream_logger.info('log_stream: processing message #{}, data length: {}'.format(message_count, len(log_data)))

                    import json
                    try:
                        parsed = json.loads(log_data)
                        stream_logger.info('log_stream: message #{}, level={}, message preview={}'.format(
                            message_count, parsed.get('level'), parsed.get('message', '')[:100]))
                    except Exception:
                        stream_logger.info('log_stream: yielding log message #{}'.format(message_count))

                    stream_logger.info('log_stream: yielding message #{}'.format(message_count))
                    yield 'data: {}\n\n'.format(log_data)
                    last_keepalive = current_time
                    stream_logger.info('log_stream: message #{} yielded successfully'.format(message_count))

                time.sleep(0.1)

        except GeneratorExit:
            stream_logger.info('log_stream: GENERATOR EXIT (client disconnected)')
            stream_logger.info('log_stream: total messages sent: {}'.format(message_count))
        except Exception:
            stream_logger.error('log_stream: EXCEPTION in generator: {}'.format(format_exc()))
            stream_logger.info('log_stream: total messages before exception: {}'.format(message_count))
        finally:
            stream_logger.info('log_stream: FINALLY block, cleaning up')
            if pubsub:
                pubsub.unsubscribe('zato.logs')
                pubsub.close()
                stream_logger.info('log_stream: pubsub closed')
            if redis_client:
                redis_client.close()
                stream_logger.info('log_stream: redis_client closed')

            with _connections_lock:
                _active_connections -= 1
                stream_logger.info('log_stream: connection closed, active_connections={}'.format(_active_connections))
                should_disable = _active_connections == 0

            if should_disable:
                try:
                    stream_logger.info('log_stream: last connection closed, checking if streaming is enabled')
                    status_response = req.zato.client.invoke('zato.log.streaming.status', {})
                    is_enabled = status_response.data.get('streaming_enabled', False)
                    stream_logger.info('log_stream: streaming enabled status: {}'.format(is_enabled))

                    if is_enabled:
                        stream_logger.info('log_stream: disabling log streaming')
                        response = req.zato.client.invoke('zato.log.streaming.toggle', {})
                        stream_logger.info('log_stream: log streaming disabled, response: {}'.format(response.data))
                    else:
                        stream_logger.info('log_stream: streaming already disabled, skipping toggle')
                except Exception:
                    stream_logger.error('log_stream: failed to disable streaming: {}'.format(format_exc()))
            else:
                stream_logger.info('log_stream: other connections still active, not disabling streaming')

            stream_logger.info('log_stream: GENERATOR ENDED')

    stream_logger.info('log_stream: creating StreamingHttpResponse')
    response = StreamingHttpResponse(
        event_stream(), # type: ignore
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    response['Content-Encoding'] = 'identity'
    stream_logger.info('log_stream: returning response to client')
    return response

# ################################################################################################################################
# ################################################################################################################################
