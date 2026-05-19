# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging

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

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':
    """ Displays a read-only message browser for a subscription queue.
    The pagination kit fetches page 1 via AJAX on init, so no service call is needed here.
    """

    sub_key = req.GET['sub_key']

    out = TemplateResponse(req, 'zato/pubsub/queue.html', {
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
def purge(req:'any_') -> 'HttpResponse':
    """ Purges all pending messages from a subscription queue.
    """

    sub_key = req.POST['sub_key']

    try:
        response = req.zato.client.invoke('zato.pubsub.subscription.purge-queue', {
            'sub_key': sub_key,
        })
        if response.ok:
            raw = response.data
            if isinstance(raw, str):
                out = HttpResponse(raw, content_type='application/json')
                return out

            out = HttpResponse(json.dumps(raw), content_type='application/json')
            return out

        else:
            error_message = response.details
            if not error_message:
                error_message = 'Error'

            out = HttpResponse(
                json.dumps({'error': error_message}),
                content_type='application/json',
                status=500,
            )
            return out

    except Exception as error:
        logger.error('Pub/sub queue purge error: %s', error)
        out = HttpResponse(json.dumps({'error': str(error)}), content_type='application/json', status=500)
        return out

# ################################################################################################################################
# ################################################################################################################################
