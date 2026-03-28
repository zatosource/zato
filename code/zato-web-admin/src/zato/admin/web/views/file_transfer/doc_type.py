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

        response = req.zato.client.invoke('file-transfer.doc-type.get-list', {})

        return TemplateResponse(req, 'zato/file_transfer/doc_type/index.html', {
            'doc_types': response.data if response.ok else [],
        })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET', 'POST')
def doc_type_create(req:'HttpRequest') -> 'HttpResponse':

    if req.method == 'POST':
        data = {
            'name': req.POST.get('name', ''),
            'description': req.POST.get('description', ''),
            'file_type': req.POST.get('file_type', 'Xml'),
            'is_enabled': req.POST.get('is_enabled') == 'on',
            'preprocess_validate': req.POST.get('preprocess_validate') == 'on',
            'preprocess_validate_schema': req.POST.get('preprocess_validate_schema', ''),
            'preprocess_dedup': req.POST.get('preprocess_dedup') == 'on',
            'preprocess_dedup_window_days': int(req.POST.get('preprocess_dedup_window_days', 30)),
            'preprocess_pgp_verify': req.POST.get('preprocess_pgp_verify') == 'on',
            'preprocess_pgp_key_id': req.POST.get('preprocess_pgp_key_id', ''),
            'preprocess_checksum': req.POST.get('preprocess_checksum') == 'on',
            'preprocess_save': req.POST.get('preprocess_save', 'All'),
        }

        recognition_rules_json = req.POST.get('recognition_rules_json', '[]')
        extraction_rules_json = req.POST.get('extraction_rules_json', '[]')

        try:
            data['recognition_rules'] = json.loads(recognition_rules_json)
        except json.JSONDecodeError:
            data['recognition_rules'] = []

        try:
            data['extraction_rules'] = json.loads(extraction_rules_json)
        except json.JSONDecodeError:
            data['extraction_rules'] = []

        response = req.zato.client.invoke('file-transfer.doc-type.create', data)

        if response.ok:
            return HttpResponseRedirect(reverse('file-transfer-doc-type'))
        else:
            return HttpResponseServerError(response.details)

    pgp_keys_response = req.zato.client.invoke('file-transfer.pgp-key.get-list', {})

    return TemplateResponse(req, 'zato/file_transfer/doc_type/create.html', {
        'pgp_keys': pgp_keys_response.data if pgp_keys_response.ok else [],
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET', 'POST')
def doc_type_edit(req:'HttpRequest', dt_id:'str') -> 'HttpResponse':

    if req.method == 'POST':
        data = {
            'id': dt_id,
            'name': req.POST.get('name', ''),
            'description': req.POST.get('description', ''),
            'file_type': req.POST.get('file_type', 'Xml'),
            'is_enabled': req.POST.get('is_enabled') == 'on',
            'preprocess_validate': req.POST.get('preprocess_validate') == 'on',
            'preprocess_validate_schema': req.POST.get('preprocess_validate_schema', ''),
            'preprocess_dedup': req.POST.get('preprocess_dedup') == 'on',
            'preprocess_dedup_window_days': int(req.POST.get('preprocess_dedup_window_days', 30)),
            'preprocess_pgp_verify': req.POST.get('preprocess_pgp_verify') == 'on',
            'preprocess_pgp_key_id': req.POST.get('preprocess_pgp_key_id', ''),
            'preprocess_checksum': req.POST.get('preprocess_checksum') == 'on',
            'preprocess_save': req.POST.get('preprocess_save', 'All'),
        }

        recognition_rules_json = req.POST.get('recognition_rules_json', '[]')
        extraction_rules_json = req.POST.get('extraction_rules_json', '[]')

        try:
            data['recognition_rules'] = json.loads(recognition_rules_json)
        except json.JSONDecodeError:
            data['recognition_rules'] = []

        try:
            data['extraction_rules'] = json.loads(extraction_rules_json)
        except json.JSONDecodeError:
            data['extraction_rules'] = []

        response = req.zato.client.invoke('file-transfer.doc-type.edit', data)

        if response.ok:
            return HttpResponseRedirect(reverse('file-transfer-doc-type'))
        else:
            return HttpResponseServerError(response.details)

    response = req.zato.client.invoke('file-transfer.doc-type.get', {'id': dt_id})
    pgp_keys_response = req.zato.client.invoke('file-transfer.pgp-key.get-list', {})

    if not response.ok:
        return HttpResponseServerError('Document type not found')

    return TemplateResponse(req, 'zato/file_transfer/doc_type/edit.html', {
        'doc_type': response.data,
        'pgp_keys': pgp_keys_response.data if pgp_keys_response.ok else [],
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def doc_type_delete(req:'HttpRequest', dt_id:'str') -> 'HttpResponse':

    response = req.zato.client.invoke('file-transfer.doc-type.delete', {'id': dt_id})

    if response.ok:
        return HttpResponse('{"ok": true}', content_type='application/json')
    else:
        return HttpResponseServerError(f'{{"ok": false, "error": "{response.details}"}}', content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################
