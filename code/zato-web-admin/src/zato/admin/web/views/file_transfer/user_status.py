# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Django
from django.http import HttpResponse, HttpResponseServerError
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

        response = req.zato.client.invoke('file-transfer.user-status.get-list', {})

        return TemplateResponse(req, 'zato/file_transfer/user_status/index.html', {
            'statuses': response.data if response.ok else [],
        })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def user_status_create(req:'HttpRequest') -> 'HttpResponse':

    status = req.POST.get('status', '')

    if not status:
        return HttpResponseServerError('{"ok": false, "error": "Status is required"}', content_type='application/json')

    response = req.zato.client.invoke('file-transfer.user-status.create', {'status': status})

    if response.ok:
        return HttpResponse('{"ok": true}', content_type='application/json')
    else:
        return HttpResponseServerError(f'{{"ok": false, "error": "{response.details}"}}', content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def user_status_delete(req:'HttpRequest', status:'str') -> 'HttpResponse':

    response = req.zato.client.invoke('file-transfer.user-status.delete', {'status': status})

    if response.ok:
        return HttpResponse('{"ok": true}', content_type='application/json')
    else:
        return HttpResponseServerError(f'{{"ok": false, "error": "{response.details}"}}', content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################
