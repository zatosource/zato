# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpRequest
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Index:

    @staticmethod
    @method_allowed('GET')
    def __call__(req:'HttpRequest') -> 'HttpResponse':

        date_from = req.GET.get('date_from', '')
        date_to = req.GET.get('date_to', '')
        activity_class = req.GET.get('activity_class', '')
        severity = req.GET.get('severity', '')

        request = {
            'limit': 100,
            'offset': 0,
        }

        if date_from:
            request['date_from'] = date_from
        if date_to:
            request['date_to'] = date_to
        if activity_class:
            request['activity_class'] = activity_class
        if severity:
            request['severity'] = severity

        response = req.zato.client.invoke('file-transfer.activity-log.search', request)

        return TemplateResponse(req, 'zato/file_transfer/activity_log/index.html', {
            'entries': response.data if response.ok else [],
            'filters': {
                'date_from': date_from,
                'date_to': date_to,
                'activity_class': activity_class,
                'severity': severity,
            },
        })

# ################################################################################################################################
# ################################################################################################################################
