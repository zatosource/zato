# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
from http import HTTPStatus
from traceback import format_exc
from urllib.parse import quote

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# pygments
from pygments import highlight as pygments_highlight
from pygments.formatters import HtmlFormatter

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.highlight import get_pygments_lexer, highlight_data_previews
from zato.common.content_type import format_content, get_content_type
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

_poll_url    = '/zato/dashboard/detail-poll/'
_payload_url = '/zato/pubsub/subscription/queue/message/payload/'


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
    state   = request.GET['state']

    if page := request.GET.get('page'):
        page = int(page)
    else:
        page = _default_page

    # .. invoke the browse service ..
    invoke_payload = {
        'sub_key': sub_key,
        'page': page,
        'state': state,
    }

    response = request.zato.client.invoke('zato.pubsub.subscription.browse-queue', invoke_payload)

    if response.ok:
        data = _parse_response_data(response)
        highlight_data_previews(data['rows'])
    else:
        data = {'rows': [], 'total': 0, 'page': _default_page, 'sub_key': sub_key}

    # .. read the queue name and depth from the response ..
    depth = data['total']
    page  = data['page']
    queue_name = request.GET['queue_name']

    subscriptions_url = f'/zato/pubsub/subscription/?cluster={default_cluster_id}'

    # .. and render the template.
    out = TemplateResponse(request, 'zato/pubsub/queue.html', {
        'cluster_id':          default_cluster_id,
        'sub_key':             sub_key,
        'queue_name':          queue_name,
        'state':               state,
        'queue_data':          data,
        'depth':               depth,
        'page':                page,
        'page_size':           _default_page_size,
        'poll_url':            _poll_url,
        'subscriptions_url':   subscriptions_url,
        'zato_clusters':       True,
        'zato_template_name':  'zato/pubsub/queue.html',
    })

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def clear_queue(request:'any_') -> 'HttpResponse':
    """ Clears all pending messages from a subscription queue.
    """

    # Invoke the clear queue service ..
    sub_key = request.POST['sub_key']

    try:
        response = request.zato.client.invoke('zato.pubsub.subscription.clear-queue', {
            'sub_key': sub_key,
        })

        if response.ok:
            response_data = _parse_response_data(response)
            response_json = json.dumps(response_data)

            out = HttpResponse(response_json.encode('utf-8'), content_type='application/json')

        # .. the service returned an error ..
        else:
            error_message = response.details
            if not error_message:
                error_message = _default_error_message

            error_json = json.dumps({'error': error_message})

            out = HttpResponse(error_json.encode('utf-8'), content_type='application/json', status=HTTPStatus.INTERNAL_SERVER_ERROR)

    # .. handle any unexpected transport or connection errors.
    except Exception: # noqa: BLE001
        logger.error('Pub/sub queue clear error: %s', format_exc())

        error_json = json.dumps({'error': _default_error_message})

        out = HttpResponse(error_json.encode('utf-8'), content_type='application/json', status=HTTPStatus.INTERNAL_SERVER_ERROR)

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def message_detail(request:'any_') -> 'TemplateResponse':
    """ Displays the detail/edit form for a single message.
    """

    # Extract parameters from the request ..
    sub_key    = request.GET['sub_key']
    msg_id     = request.GET['msg_id']
    topic_name = request.GET['topic_name']

    # .. invoke the detail service - it returns the metadata and the payload in one call ..
    invoke_payload = {
        'msg_id': msg_id,
        'topic_name': topic_name,
    }

    response = request.zato.client.invoke('zato.pubsub.subscription.get-message-detail', invoke_payload)

    if not response.ok:
        raise Exception(response.details)

    message_data = _parse_response_data(response)

    # .. detect content type and pretty-print ..
    raw_data = message_data['data']
    content_type = get_content_type(raw_data)
    data = format_content(raw_data, content_type)

    # .. attach the formatted payload to the response ..
    message_data['data'] = data
    message_data['content_type'] = content_type

    # .. pre-render syntax-highlighted HTML so the page loads without a highlight delay ..
    lexer = get_pygments_lexer(content_type)
    formatter = HtmlFormatter(nowrap=True)
    message_data['data_highlighted'] = pygments_highlight(raw_data, lexer, formatter)

    # .. resolve the active tab from the URL ..
    if active_tab := request.GET.get('tab'):
        pass
    else:
        active_tab = _default_active_tab

    # .. read the queue name from the request ..
    queue_name = request.GET['queue_name']

    # .. and render the template.
    sub_key_encoded = quote(sub_key, safe='')
    queue_name_encoded = quote(queue_name, safe='')
    queue_url = f'/zato/pubsub/subscription/queue/?cluster={default_cluster_id}&sub_key={sub_key_encoded}&queue_name={queue_name_encoded}&state=pending'
    topic_url = f'/zato/pubsub/topic/?cluster={default_cluster_id}'

    out = TemplateResponse(request, 'zato/pubsub/queue_message.html', {
        'cluster_id':        default_cluster_id,
        'sub_key':           sub_key,
        'msg_id':            msg_id,
        'topic_name':        topic_name,
        'queue_name':        queue_name,
        'active_tab':        active_tab,
        'message_data_json': message_data,
        'poll_url':          _poll_url,
        'payload_url':       _payload_url,
        'queue_url':         queue_url,
        'topic_url':         topic_url,
        'zato_clusters':     True,
        'zato_template_name': 'zato/pubsub/queue_message.html',
    })

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def message_payload(request:'any_') -> 'HttpResponse':
    """ Returns the message payload read from the pub/sub database.
    """

    # Parse the request body ..
    body = json.loads(request.body)
    msg_id     = body['msg_id']
    topic_name = body['topic_name']

    # .. invoke the detail service for the payload ..
    invoke_payload = {
        'msg_id': msg_id,
        'topic_name': topic_name,
    }

    response = request.zato.client.invoke('zato.pubsub.subscription.get-message-detail', invoke_payload)

    if not response.ok:
        raise Exception(response.details)

    message_data = _parse_response_data(response)

    response_data = {
        'data': message_data['data'],
        'data_class': message_data['data_class'],
    }

    # .. and return the payload as JSON.
    response_json = json.dumps(response_data)

    out = HttpResponse(response_json.encode('utf-8'), content_type='application/json')
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def delete_message(request:'any_') -> 'HttpResponse':
    """ Deletes a single message from a subscription queue.
    """

    # Parse the request body ..
    body = json.loads(request.body)
    msg_id     = body['msg_id']
    topic_name = body['topic_name']
    sub_key    = body['sub_key']

    try:
        response = request.zato.client.invoke('zato.pubsub.subscription.delete-message', {
            'msg_id': msg_id,
            'topic_name': topic_name,
            'sub_key': sub_key,
        })

        if response.ok:
            response_data = _parse_response_data(response)
            response_json = json.dumps(response_data)

            out = HttpResponse(response_json.encode('utf-8'), content_type='application/json')

        # .. the service returned an error ..
        else:
            error_message = response.details
            if not error_message:
                error_message = _default_error_message

            error_json = json.dumps({'error': error_message})

            out = HttpResponse(error_json.encode('utf-8'), content_type='application/json', status=HTTPStatus.INTERNAL_SERVER_ERROR)

    # .. handle any unexpected transport or connection errors.
    except Exception: # noqa: BLE001
        logger.error('Pub/sub message delete error: %s', format_exc())

        error_json = json.dumps({'error': _default_error_message})

        out = HttpResponse(error_json.encode('utf-8'), content_type='application/json', status=HTTPStatus.INTERNAL_SERVER_ERROR)

    return out

# ################################################################################################################################
# ################################################################################################################################
