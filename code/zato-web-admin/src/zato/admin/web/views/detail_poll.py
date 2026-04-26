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

_action_registry = {
    'get-history':     'zato.scheduler.job.get-history',
    'get-log-entries': 'zato.scheduler.job.get-log-entries',
    'get-run-detail':  'zato.scheduler.job.get-run-detail',
}

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def detail_poll(req):
    body = json.loads(req.body)
    action = body['action']
    service_name = _action_registry[action]
    service_payload = {key: value for key, value in body.items() if key != 'action'}
    t0 = time.monotonic()
    response = req.zato.client.invoke(service_name, service_payload)
    elapsed = time.monotonic() - t0
    if elapsed > 2.0:
        logger.warning('detail_poll invoke %s took %.1fs', service_name, elapsed)
    return HttpResponse(json.dumps(response.data), content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################
