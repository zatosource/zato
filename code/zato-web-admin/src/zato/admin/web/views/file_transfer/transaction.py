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
from zato.common.api import ZatoNotGiven

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
        status = req.GET.get('status', '')
        sender = req.GET.get('sender', '')
        receiver = req.GET.get('receiver', '')
        doc_type_id = req.GET.get('doc_type_id', '')
        query = req.GET.get('query', '')

        request = {
            'date_from': date_from,
            'date_to': date_to,
            'status': status,
            'sender': sender,
            'receiver': receiver,
            'doc_type_id': doc_type_id,
            'limit': 100,
            'offset': 0,
        }

        response = req.zato.client.invoke('file-transfer.transaction.search', request)

        doc_types_response = req.zato.client.invoke('file-transfer.doc-type.get-list', {})

        return TemplateResponse(req, 'zato/file_transfer/transaction/index.html', {
            'transactions': response.data if response.ok else [],
            'doc_types': doc_types_response.data if doc_types_response.ok else [],
            'filters': {
                'date_from': date_from,
                'date_to': date_to,
                'status': status,
                'sender': sender,
                'receiver': receiver,
                'doc_type_id': doc_type_id,
                'query': query,
            },
            'filter_query': req.GET.urlencode(),
        })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def transaction_detail(req:'HttpRequest', tx_id:'str') -> 'HttpResponse':

    response = req.zato.client.invoke('file-transfer.transaction.get', {'id': tx_id})

    if not response.ok:
        return HttpResponseServerError('Transaction not found')

    return TemplateResponse(req, 'zato/file_transfer/transaction/detail.html', {
        'transaction': response.data,
        'back_query': req.GET.urlencode(),
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def transaction_content(req:'HttpRequest', tx_id:'str') -> 'HttpResponse':

    response = req.zato.client.invoke('file-transfer.transaction.get-content', {'id': tx_id})

    if not response.ok:
        return HttpResponseServerError('Content not found')

    content = response.data
    if isinstance(content, bytes):
        try:
            content = content.decode('utf-8')
        except UnicodeDecodeError:
            content = content.decode('latin-1')

    return HttpResponse(content, content_type='text/plain')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def transaction_activity(req:'HttpRequest', tx_id:'str') -> 'HttpResponse':

    response = req.zato.client.invoke('file-transfer.transaction.get-activity', {'id': tx_id})

    return TemplateResponse(req, 'zato/file_transfer/transaction/activity.html', {
        'entries': response.data if response.ok else [],
        'tx_id': tx_id,
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def transaction_tasks(req:'HttpRequest', tx_id:'str') -> 'HttpResponse':

    response = req.zato.client.invoke('file-transfer.transaction.get-tasks', {'id': tx_id})

    return TemplateResponse(req, 'zato/file_transfer/transaction/tasks.html', {
        'tasks': response.data if response.ok else [],
        'tx_id': tx_id,
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def transaction_resubmit(req:'HttpRequest', tx_id:'str') -> 'HttpResponse':

    response = req.zato.client.invoke('file-transfer.transaction.resubmit', {'id': tx_id})

    if response.ok:
        new_id = response.data.get('new_id', '')
        return HttpResponse(f'{{"ok": true, "new_id": "{new_id}"}}', content_type='application/json')
    else:
        return HttpResponseServerError(f'{{"ok": false, "error": "{response.details}"}}', content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def transaction_reprocess(req:'HttpRequest', tx_id:'str') -> 'HttpResponse':

    response = req.zato.client.invoke('file-transfer.transaction.reprocess', {'id': tx_id})

    if response.ok:
        return HttpResponse('{"ok": true}', content_type='application/json')
    else:
        return HttpResponseServerError(f'{{"ok": false, "error": "{response.details}"}}', content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################
