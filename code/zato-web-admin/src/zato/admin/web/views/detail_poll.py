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

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_service_registry = {
    'scheduler-job': 'zato.scheduler.job.get-history',
    'pubsub-topic': 'zato.broker.topic.get-detail',
    'pubsub-queue': 'zato.broker.queue.get-detail',
}

_action_registry = {
    'get-history': 'zato.scheduler.job.get-history',
    'get-log-entries': 'zato.scheduler.job.get-log-entries',
}

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def detail_poll(req):
    content_type = req.content_type

    if 'application/json' in content_type:
        body = json.loads(req.body)
        action = body['action']
        if action in _action_registry:
            service_name = _action_registry[action]

            # .. forward all body fields except 'action' itself
            service_payload = {key: value for key, value in body.items() if key != 'action'}
            t0 = time.monotonic()
            response = req.zato.client.invoke(service_name, service_payload)
            elapsed = time.monotonic() - t0
            if elapsed > 2.0:
                logger.warning('detail_poll invoke %s took %.1fs', service_name, elapsed)
            return HttpResponse(json.dumps(response.data), content_type='application/json')

    service_name = _service_registry[req.POST['object_type']]
    t0 = time.monotonic()
    response = req.zato.client.invoke(service_name, req.POST.dict())
    elapsed = time.monotonic() - t0
    if elapsed > 2.0:
        logger.warning('detail_poll invoke %s took %.1fs', service_name, elapsed)
    return HttpResponse(json.dumps(response.data), content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################
