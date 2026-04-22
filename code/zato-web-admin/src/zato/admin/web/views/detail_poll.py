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

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def detail_poll(req):
    service_name = _service_registry[req.POST['object_type']]
    response = req.zato.client.invoke(service_name, req.POST.dict())
    return HttpResponse(json.dumps(response.data), content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################
