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

@method_allowed('GET')
def index(req:'HttpRequest') -> 'HttpResponse':

    response = req.zato.client.invoke('file-transfer.settings.get', {})

    return TemplateResponse(req, 'zato/file_transfer/settings/index.html', {
        'settings': response.data if response.ok else {},
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def settings_update(req:'HttpRequest') -> 'HttpResponse':

    data = {
        'default_retry_count': int(req.POST.get('default_retry_count', 3)),
        'default_retry_wait_ms': int(req.POST.get('default_retry_wait_ms', 60000)),
        'default_backoff_factor': float(req.POST.get('default_backoff_factor', 2.0)),
        'default_save_policy': req.POST.get('default_save_policy', 'All'),
        'max_search_results': int(req.POST.get('max_search_results', 20000)),
        'archive_after_days': int(req.POST.get('archive_after_days', 90)),
        'log_retention_days': int(req.POST.get('log_retention_days', 365)),
        'checksum_algorithm': req.POST.get('checksum_algorithm', 'SHA-256'),
    }

    response = req.zato.client.invoke('file-transfer.settings.update', data)

    if response.ok:
        return HttpResponse('{"ok": true}', content_type='application/json')
    else:
        return HttpResponseServerError(f'{{"ok": false, "error": "{response.details}"}}', content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################
