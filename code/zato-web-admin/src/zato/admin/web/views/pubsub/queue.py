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
from zato.common.defaults import default_cluster_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Default_Error_Message = 'Error'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(request:'any_') -> 'TemplateResponse':
    """ Displays a read-only message browser for a subscription queue.
    The pagination kit fetches page 1 via AJAX on init, so no service call is needed here.
    """

    sub_key = request.GET['sub_key']

    out = TemplateResponse(request, 'zato/pubsub/queue.html', {
        'cluster_id': default_cluster_id,
        'sub_key': sub_key,
        'poll_url': '/zato/dashboard/detail-poll/',
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

    service_request = {
        'sub_key': sub_key,
    }

    try:
        response = request.zato.client.invoke('zato.pubsub.subscription.purge-queue', service_request)

        if response.ok:
            raw = response.data
            if isinstance(raw, str):
                out = HttpResponse(raw, content_type='application/json')
                return out

            response_json = json.dumps(raw)

            out = HttpResponse(response_json, content_type='application/json')
            return out

        else:
            error_message = response.details
            if not error_message:
                error_message = _Default_Error_Message

            error_json = json.dumps({'error': error_message})

            out = HttpResponse(
                error_json,
                content_type='application/json',
                status=500,
            )
            return out

    except Exception as error:
        error_text = format_exc()
        logger.error('Pub/sub queue purge error: %s', error_text)
        error_json = json.dumps({'error': error_text})

        out = HttpResponse(error_json, content_type='application/json', status=500)
        return out

# ################################################################################################################################
# ################################################################################################################################
