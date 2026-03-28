# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging

# Django
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template.response import TemplateResponse
from django.urls import reverse

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

        response = req.zato.client.invoke('file-transfer.rule.get-list', {})

        return TemplateResponse(req, 'zato/file_transfer/rule/index.html', {
            'rules': response.data if response.ok else [],
        })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET', 'POST')
def rule_create(req:'HttpRequest') -> 'HttpResponse':

    if req.method == 'POST':
        data = {
            'name': req.POST.get('name', ''),
            'description': req.POST.get('description', ''),
            'is_enabled': req.POST.get('is_enabled') == 'on',
            'criteria_sender': {
                'match': req.POST.get('criteria_sender_match', 'Any'),
                'values': [v.strip() for v in req.POST.get('criteria_sender_values', '').split(',') if v.strip()],
            },
            'criteria_receiver': {
                'match': req.POST.get('criteria_receiver_match', 'Any'),
                'values': [v.strip() for v in req.POST.get('criteria_receiver_values', '').split(',') if v.strip()],
            },
            'criteria_doc_type': {
                'match': req.POST.get('criteria_doc_type_match', 'Any'),
                'values': [v.strip() for v in req.POST.get('criteria_doc_type_values', '').split(',') if v.strip()],
            },
            'criteria_errors': req.POST.get('criteria_errors', 'Any'),
        }

        response = req.zato.client.invoke('file-transfer.rule.create', data)

        if response.ok:
            return HttpResponseRedirect(reverse('file-transfer-rule'))
        else:
            return HttpResponseServerError(response.details)

    doc_types_response = req.zato.client.invoke('file-transfer.doc-type.get-list', {})

    return TemplateResponse(req, 'zato/file_transfer/rule/create.html', {
        'doc_types': doc_types_response.data if doc_types_response.ok else [],
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET', 'POST')
def rule_edit(req:'HttpRequest', rule_id:'str') -> 'HttpResponse':

    if req.method == 'POST':
        data = {
            'id': rule_id,
            'name': req.POST.get('name', ''),
            'description': req.POST.get('description', ''),
            'is_enabled': req.POST.get('is_enabled') == 'on',
            'criteria_sender': {
                'match': req.POST.get('criteria_sender_match', 'Any'),
                'values': [v.strip() for v in req.POST.get('criteria_sender_values', '').split(',') if v.strip()],
            },
            'criteria_receiver': {
                'match': req.POST.get('criteria_receiver_match', 'Any'),
                'values': [v.strip() for v in req.POST.get('criteria_receiver_values', '').split(',') if v.strip()],
            },
            'criteria_doc_type': {
                'match': req.POST.get('criteria_doc_type_match', 'Any'),
                'values': [v.strip() for v in req.POST.get('criteria_doc_type_values', '').split(',') if v.strip()],
            },
            'criteria_errors': req.POST.get('criteria_errors', 'Any'),
        }

        actions_json = req.POST.get('actions_json', '[]')
        try:
            data['actions'] = json.loads(actions_json)
        except json.JSONDecodeError:
            data['actions'] = []

        response = req.zato.client.invoke('file-transfer.rule.edit', data)

        if response.ok:
            return HttpResponseRedirect(reverse('file-transfer-rule'))
        else:
            return HttpResponseServerError(response.details)

    response = req.zato.client.invoke('file-transfer.rule.get', {'id': rule_id})
    doc_types_response = req.zato.client.invoke('file-transfer.doc-type.get-list', {})

    if not response.ok:
        return HttpResponseServerError('Rule not found')

    return TemplateResponse(req, 'zato/file_transfer/rule/edit.html', {
        'rule': response.data,
        'doc_types': doc_types_response.data if doc_types_response.ok else [],
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def rule_delete(req:'HttpRequest', rule_id:'str') -> 'HttpResponse':

    response = req.zato.client.invoke('file-transfer.rule.delete', {'id': rule_id})

    if response.ok:
        return HttpResponse('{"ok": true}', content_type='application/json')
    else:
        return HttpResponseServerError(f'{{"ok": false, "error": "{response.details}"}}', content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def rule_reorder(req:'HttpRequest') -> 'HttpResponse':

    ordered_ids = req.POST.get('ordered_ids', '')

    response = req.zato.client.invoke('file-transfer.rule.reorder', {'ordered_ids': ordered_ids})

    if response.ok:
        return HttpResponse('{"ok": true}', content_type='application/json')
    else:
        return HttpResponseServerError(f'{{"ok": false, "error": "{response.details}"}}', content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################
