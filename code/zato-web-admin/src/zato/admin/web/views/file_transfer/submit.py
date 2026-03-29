# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import base64
import logging

# Django
from django.http import HttpResponse, JsonResponse
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

        return TemplateResponse(req, 'zato/file_transfer/submit/index.html', {
            'page_config': {
                'title': 'Submit a file',
                'section_title': 'Submit a file',
                'action_button_label': 'Submit',
            },
        })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def submit_file(req:'HttpRequest') -> 'HttpResponse':

    logger.info('submit_file called')

    uploaded_file = req.FILES.get('file')
    if not uploaded_file:
        logger.warning('No file uploaded')
        return JsonResponse({'success': False, 'error': 'No file uploaded'}, status=400)

    filename = req.POST.get('filename') or uploaded_file.name
    source_protocol = req.POST.get('source_protocol', 'Manual upload')
    source_detail = req.POST.get('source_detail', 'Uploaded via Dashboard')

    content = uploaded_file.read()
    content_b64 = base64.b64encode(content).decode('utf-8')

    data = {
        'filename': filename,
        'content': content_b64,
        'is_base64': True,
        'source_protocol': source_protocol,
        'source_detail': source_detail,
    }

    logger.info('Invoking file-transfer.submit with filename=%s, content_length=%d', filename, len(content_b64))

    response = req.zato.client.invoke('file-transfer.submit', data)

    logger.info('Response ok=%s, data=%s', response.ok, response.data)

    if response.ok:
        transaction_id = response.data.get('transaction_id', '')
        logger.info('Transaction created: %s', transaction_id)
        return JsonResponse({'success': True, 'transaction_id': transaction_id})
    else:
        logger.error('Submit failed: %s', response.details)
        return JsonResponse({'success': False, 'error': response.details}, status=500)

# ################################################################################################################################
# ################################################################################################################################
