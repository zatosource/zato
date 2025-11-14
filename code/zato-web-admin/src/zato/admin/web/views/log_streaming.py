# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
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

        redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        pubsub = redis_client.pubsub()
        pubsub.subscribe('zato.logs')

        try:
            for message in pubsub.listen():
                if message['type'] == 'subscribe':
                    yield 'data: {}\n\n'.format('{}')
                elif message['type'] == 'message':
                    log_data = message['data']
                    yield 'data: {}\n\n'.format(log_data)

        except GeneratorExit:
            pubsub.unsubscribe('zato.logs')
            pubsub.close()
            redis_client.close()

    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    return response

# ################################################################################################################################
# ################################################################################################################################
