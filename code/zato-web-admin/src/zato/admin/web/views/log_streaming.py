# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Django
from django.http import HttpResponse, StreamingHttpResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def toggle_streaming(req):

    response = req.zato.client.invoke('zato.log.streaming.toggle', {})

    return HttpResponse(dumps(response.data), content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_status(req):

    response = req.zato.client.invoke('zato.log.streaming.status', {})

    return HttpResponse(dumps(response.data), content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def log_stream(req):

    stream_logger = getLogger('zato.sse_stream')
    stream_logger.info('log_stream: VIEW CALLED, client: {}'.format(req.META.get('REMOTE_ADDR')))

    def event_stream():

        # Redis
        import redis
        import time

        redis_client = None
        pubsub = None

        try:
            stream_logger.info('log_stream: GENERATOR STARTED')
            stream_logger.info('log_stream: attempting Redis connection')

            redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            stream_logger.info('log_stream: Redis client created, testing connection')

            redis_client.ping()
            stream_logger.info('log_stream: Redis ping successful')

            pubsub = redis_client.pubsub()
            stream_logger.info('log_stream: pubsub created')

            pubsub.subscribe('zato.logs')
            stream_logger.info('log_stream: subscribed to zato.logs channel')

            yield ': connected\n\n'
            stream_logger.info('log_stream: sent initial connected message')

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
                if message and message['type'] == 'message':
                    message_count += 1
                    log_data = message['data']
                    stream_logger.info('log_stream: yielding log message #{}'.format(message_count))
                    yield 'data: {}\n\n'.format(log_data)
                    last_keepalive = current_time

                time.sleep(0.1)

        except GeneratorExit:
            stream_logger.info('log_stream: GENERATOR EXIT (client disconnected)')
        except Exception:
            stream_logger.error('log_stream: EXCEPTION in generator: {}'.format(format_exc()))
        finally:
            stream_logger.info('log_stream: FINALLY block, cleaning up')
            if pubsub:
                pubsub.unsubscribe('zato.logs')
                pubsub.close()
                stream_logger.info('log_stream: pubsub closed')
            if redis_client:
                redis_client.close()
                stream_logger.info('log_stream: redis_client closed')
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
