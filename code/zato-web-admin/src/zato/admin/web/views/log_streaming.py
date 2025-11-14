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

    def event_stream():

        # Redis
        import redis
        import time

        redis_client = None
        pubsub = None

        try:
            stream_logger = getLogger('zato.sse_stream')
            stream_logger.info('log_stream: connecting to Redis')

            redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            pubsub = redis_client.pubsub()
            pubsub.subscribe('zato.logs')

            stream_logger.info('log_stream: subscribed to zato.logs channel')

            last_keepalive = time.time()
            message_count = 0

            iteration = 0
            while True:
                iteration += 1
                message = pubsub.get_message()
                if message:
                    if message['type'] == 'message':
                        message_count += 1
                        log_data = message['data']
                        yield 'data: {}\n\n'.format(log_data)
                        last_keepalive = time.time()

                current_time = time.time()
                if current_time - last_keepalive > 10:
                    yield ': keepalive\n\n'
                    last_keepalive = current_time

                time.sleep(0.1)

        except GeneratorExit:
            pass
        except Exception:
            logger.warning('Log streaming error: {}'.format(format_exc()))
        finally:
            if pubsub:
                pubsub.unsubscribe('zato.logs')
                pubsub.close()
            if redis_client:
                redis_client.close()

    response = StreamingHttpResponse(
        event_stream(), # type: ignore
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response

# ################################################################################################################################
# ################################################################################################################################
