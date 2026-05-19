# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
from traceback import format_exc
from urllib.parse import quote

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.defaults import default_cluster_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict
    any_ = any_
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_default_error_message = 'Error'
_default_active_tab    = 'data'
_default_page          = 1
_default_page_size     = 50
_default_priority      = 5
_default_expiration    = 0
_default_data          = ''
_default_data_class    = ''
_default_data_size     = 0
_default_time_iso      = ''

_poll_url = '/zato/dashboard/detail-poll/'

# ################################################################################################################################
# ################################################################################################################################

def _parse_response_data(response:'any_') -> 'anydict':
    """ Parses the service response data into a dict.
    """

    # Check if the data is a raw string ..
    response_data = response.data

    if isinstance(response_data, str):
        out = json.loads(response_data)
    else:
        out = response_data

    # .. and return it as a dict.
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(request:'any_') -> 'TemplateResponse':
    """ Displays a read-only message browser for a subscription queue.
    """

    # Extract parameters from the request ..
    sub_key = request.GET['sub_key']

    page_raw = request.GET.get('page')
    if page_raw:
        page = int(page_raw)
    else:
        page = _default_page

    # .. invoke the browse service ..
    invoke_payload = {
        'sub_key': sub_key,
        'page': page,
    }

    response = request.zato.client.invoke('zato.pubsub.subscription.browse-queue', invoke_payload)

    if response.ok:
        data = _parse_response_data(response)
    else:
        data = {'rows': [], 'total': 0, 'page': _default_page, 'sub_key': sub_key}

    # .. and render the template.
    depth = data['total']
    page  = data['page']

    out = TemplateResponse(request, 'zato/pubsub/queue.html', {
        'cluster_id':        default_cluster_id,
        'sub_key':           sub_key,
        'queue_data':        data,
        'depth':             depth,
        'page':              page,
        'page_size':         _default_page_size,
        'zato_clusters':     True,
        'zato_template_name': 'zato/pubsub/queue.html',
    })

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def purge(request:'any_') -> 'HttpResponse':
    """ Purges all pending messages from a subscription queue.
    """

    # Our response to produce
    out = None

    # Invoke the purge service ..
    sub_key = request.POST['sub_key']

    try:
        response = request.zato.client.invoke('zato.pubsub.subscription.purge-queue', {
            'sub_key': sub_key,
        })

        if response.ok:
            response_data = _parse_response_data(response)
            response_json = json.dumps(response_data)

            out = HttpResponse(response_json, content_type='application/json')

        # .. the service returned an error ..
        else:
            error_message = response.details
            if not error_message:
                error_message = _default_error_message

            error_json = json.dumps({'error': error_message})

            out = HttpResponse(error_json, content_type='application/json', status=500)

    # .. handle any unexpected transport or connection errors.
    except Exception: # noqa: BLE001
        logger.error('Pub/sub queue purge error: %s', format_exc())

        error_json = json.dumps({'error': _default_error_message})

        out = HttpResponse(error_json, content_type='application/json', status=500)

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def message_detail(request:'any_') -> 'TemplateResponse':
    """ Displays the detail/edit form for a single message.
    """

    # Extract parameters from the request ..
    sub_key         = request.GET['sub_key']
    msg_id          = request.GET['msg_id']
    topic_name      = request.GET['topic_name']
    redis_stream_id = request.GET['redis_stream_id']

    # .. invoke the get-message-detail service ..
    invoke_payload = {
        'msg_id': msg_id,
        'topic_name': topic_name,
        'redis_stream_id': redis_stream_id,
    }

    response = request.zato.client.invoke('zato.pubsub.subscription.get-message-detail', invoke_payload)

    if response.ok:
        message_data = _parse_response_data(response)
    else:
        message_data = {
            'msg_id':              msg_id,
            'topic_name':          topic_name,
            'redis_stream_id':     redis_stream_id,
            'data':                _default_data,
            'data_class':          _default_data_class,
            'priority':            _default_priority,
            'expiration':          _default_expiration,
            'pub_time_iso':        _default_time_iso,
            'recv_time_iso':       _default_time_iso,
            'expiration_time_iso': _default_time_iso,
            'data_size':           _default_data_size,
        }

    # .. resolve the active tab from the URL ..
    active_tab = request.GET.get('tab')
    if not active_tab:
        active_tab = _default_active_tab

    # .. and render the template.
    sub_key_encoded = quote(sub_key, safe='')
    queue_url = f'/zato/pubsub/subscription/queue/?cluster={default_cluster_id}&sub_key={sub_key_encoded}'

    out = TemplateResponse(request, 'zato/pubsub/queue_message.html', {
        'cluster_id':        default_cluster_id,
        'sub_key':           sub_key,
        'msg_id':            msg_id,
        'topic_name':        topic_name,
        'active_tab':        active_tab,
        'message_data_json': message_data,
        'poll_url':          _poll_url,
        'queue_url':         queue_url,
        'zato_clusters':     True,
        'zato_template_name': 'zato/pubsub/queue_message.html',
    })

    return out

# ################################################################################################################################
# ################################################################################################################################
