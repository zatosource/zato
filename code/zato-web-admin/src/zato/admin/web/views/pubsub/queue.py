# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
from traceback import format_exc

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_Default_Error_Message = 'Error'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(request:'any_') -> 'TemplateResponse':
    """ Displays a read-only message browser for a subscription queue.
    """

    # Extract parameters from the request ..
    sub_key = request.GET['sub_key']
    cursor = request.GET.get('cursor')

    if not cursor:
        cursor = '-'

    # .. invoke the browse service ..
    invoke_payload = {
        'sub_key': sub_key,
        'cursor': cursor,
    }

    response = request.zato.client.invoke('zato.pubsub.subscription.browse-queue', invoke_payload)

    if response.ok:
        raw = response.data
        if isinstance(raw, str):
            data = json.loads(raw)
        else:
            data = raw
    else:
        data = {'messages': [], 'depth': 0, 'next_cursor': '', 'sub_key': sub_key}

    # .. and render the template.
    out = TemplateResponse(request, 'zato/pubsub/queue.html', {
        'cluster_id': 1,
        'sub_key': sub_key,
        'queue_data': json.dumps(data),
        'next_cursor': data['next_cursor'],
        'depth': data['depth'],
        'zato_clusters': True,
        'zato_template_name': 'zato/pubsub/queue.html',
    })

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def purge(request:'any_') -> 'HttpResponse':
    """ Purges all pending messages from a subscription queue.
    """

    sub_key = request.POST['sub_key']

    try:
        response = request.zato.client.invoke('zato.pubsub.subscription.purge-queue', {
            'sub_key': sub_key,
        })

        if response.ok:
            raw = response.data
            if isinstance(raw, str):
                out = HttpResponse(raw, content_type='application/json')
                return out

            out = HttpResponse(json.dumps(raw), content_type='application/json')
            return out

        # .. the service returned an error.
        error_message = response.details
        if not error_message:
            error_message = _Default_Error_Message

        out = HttpResponse(
            json.dumps({'error': error_message}),
            content_type='application/json',
            status=500,
        )
        return out

    except Exception:
        logger.error('Pub/sub queue purge error: %s', format_exc())

        out = HttpResponse(
            json.dumps({'error': _Default_Error_Message}),
            content_type='application/json',
            status=500,
        )
        return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def message_detail(request:'any_') -> 'TemplateResponse':
    """ Displays the detail/edit form for a single message.
    """

    # Extract parameters from the request ..
    sub_key = request.GET['sub_key']
    msg_id = request.GET['msg_id']
    topic_name = request.GET['topic_name']
    redis_stream_id = request.GET['redis_stream_id']

    # .. invoke the get-message-detail service ..
    invoke_payload = {
        'msg_id': msg_id,
        'topic_name': topic_name,
        'redis_stream_id': redis_stream_id,
    }

    response = request.zato.client.invoke('zato.pubsub.subscription.get-message-detail', invoke_payload)

    if response.ok:
        raw = response.data
        if isinstance(raw, str):
            message_data = json.loads(raw)
        else:
            message_data = raw
    else:
        message_data = {
            'msg_id': msg_id,
            'topic_name': topic_name,
            'redis_stream_id': redis_stream_id,
            'data': '',
            'data_class': '',
            'priority': 5,
            'expiration': 0,
            'pub_time_iso': '',
            'recv_time_iso': '',
            'expiration_time_iso': '',
            'data_size': 0,
        }

    # .. and render the template.
    out = TemplateResponse(request, 'zato/pubsub/queue_message.html', {
        'cluster_id': 1,
        'sub_key': sub_key,
        'msg_id': msg_id,
        'topic_name': topic_name,
        'message_data_json': json.dumps(message_data),
        'poll_url': '/zato/dashboard/detail-poll/',
        'queue_url': f'/zato/pubsub/subscription/queue/?cluster=1&sub_key={sub_key}',
        'zato_clusters': True,
        'zato_template_name': 'zato/pubsub/queue_message.html',
    })

    return out

# ################################################################################################################################
# ################################################################################################################################
