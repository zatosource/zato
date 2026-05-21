# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import time

# Django
from django.http import HttpResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.highlight import highlight_data_previews

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

_action_registry = {
    'get-history':        'zato.scheduler.job.get-history',
    'get-log-entries':    'zato.scheduler.job.get-log-entries',
    'get-run-detail':     'zato.scheduler.job.get-run-detail',
    'get-queue-messages': 'zato.pubsub.subscription.browse-queue',
    'get-message-detail': 'zato.pubsub.subscription.get-message-detail',
    'get-message-metadata': 'zato.pubsub.subscription.get-message-metadata',
    'update-message':     'zato.pubsub.subscription.update-message',
}

_slow_invoke_threshold = 2.0

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def detail_poll(request:'any_') -> 'HttpResponse':
    """ Generic AJAX endpoint for dashboard toolkit service invocations.
    """

    # Parse the request body ..
    body = json.loads(request.body)
    action = body['action']
    service_name = _action_registry[action]

    # .. build the service payload from all keys except 'action' ..
    service_payload:'anydict' = {}

    for field_name in body:
        if field_name != 'action':
            service_payload[field_name] = body[field_name]

    # .. invoke the service and measure elapsed time ..
    invoke_start = time.monotonic()

    try:
        response = request.zato.client.invoke(service_name, service_payload)
    except Exception as e:
        logger.warning('detail_poll invoke %s failed -> %s', service_name, e)
        error_json = json.dumps({'error': str(e)})
        out = HttpResponse(error_json, content_type='application/json', status=500)
        return out

    elapsed = time.monotonic() - invoke_start

    if elapsed > _slow_invoke_threshold:
        logger.warning(f'detail_poll invoke {service_name} took {elapsed:.1f}s')

    # .. post-process actions that need server-side enrichment ..
    response_data = response.data
    if isinstance(response_data, str):
        response_data = json.loads(response_data)

    if action == 'get-queue-messages':
        highlight_data_previews(response_data['rows'])

    # .. and return the response as JSON.
    response_json = json.dumps(response_data)

    out = HttpResponse(response_json, content_type='application/json')
    return out

# ################################################################################################################################
# ################################################################################################################################
