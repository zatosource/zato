# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

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

    logger.info('Toggle streaming called')
    response = req.zato.client.invoke('zato.log.streaming.toggle', {})
    logger.info('Toggle streaming response: {}'.format(response.data))

    return HttpResponse(dumps(response.data), content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_status(req):

    logger.info('Get status called')
    response = req.zato.client.invoke('zato.log.streaming.status', {})
    logger.info('Get status response: {}'.format(response.data))

    return HttpResponse(dumps(response.data), content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def log_stream(req):

    logger.info('Log stream endpoint called')

    def event_stream():

        # Redis
        import redis
        import time

        redis_client = None
        pubsub = None

        try:
            logger.info('Connecting to Redis')
            redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            pubsub = redis_client.pubsub()
            pubsub.subscribe('zato.logs')
            logger.info('Subscribed to zato.logs channel')

            last_keepalive = time.time()

            while True:
                message = pubsub.get_message()
                if message:
                    if message['type'] == 'message':
                        log_data = message['data']
                        yield 'data: {}\n\n'.format(log_data)
                        last_keepalive = time.time()

                current_time = time.time()
                if current_time - last_keepalive > 15:
                    yield ': keepalive\n\n'
                    last_keepalive = current_time

                time.sleep(0.1)

        except GeneratorExit:
            logger.info('Client disconnected, cleaning up')
        except Exception as e:
            logger.warning('Log streaming error: {}'.format(e))
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
