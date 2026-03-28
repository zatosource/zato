# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
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

        response = req.zato.client.invoke('file-transfer.pgp-key.get-list', {})

        return TemplateResponse(req, 'zato/file_transfer/pgp_key/index.html', {
            'pgp_keys': response.data if response.ok else [],
        })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET', 'POST')
def pgp_key_import(req:'HttpRequest') -> 'HttpResponse':

    if req.method == 'POST':
        data = {
            'name': req.POST.get('name', ''),
            'key_data': req.POST.get('key_data', ''),
            'is_enabled': req.POST.get('is_enabled') == 'on',
        }

        response = req.zato.client.invoke('file-transfer.pgp-key.import', data)

        if response.ok:
            return HttpResponseRedirect(reverse('file-transfer-pgp-key'))
        else:
            return HttpResponseServerError(response.details)

    return TemplateResponse(req, 'zato/file_transfer/pgp_key/import.html', {})

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET', 'POST')
def pgp_key_generate(req:'HttpRequest') -> 'HttpResponse':

    if req.method == 'POST':
        data = {
            'name': req.POST.get('name', ''),
            'email': req.POST.get('email', ''),
            'algorithm': req.POST.get('algorithm', 'RSA'),
            'key_size': int(req.POST.get('key_size', 4096)),
            'passphrase': req.POST.get('passphrase', ''),
        }

        response = req.zato.client.invoke('file-transfer.pgp-key.generate', data)

        if response.ok:
            return HttpResponseRedirect(reverse('file-transfer-pgp-key'))
        else:
            return HttpResponseServerError(response.details)

    return TemplateResponse(req, 'zato/file_transfer/pgp_key/generate.html', {})

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET', 'POST')
def pgp_key_edit(req:'HttpRequest', key_id:'str') -> 'HttpResponse':

    if req.method == 'POST':
        data = {
            'id': key_id,
            'name': req.POST.get('name', ''),
            'is_enabled': req.POST.get('is_enabled') == 'on',
        }

        response = req.zato.client.invoke('file-transfer.pgp-key.edit', data)

        if response.ok:
            return HttpResponseRedirect(reverse('file-transfer-pgp-key'))
        else:
            return HttpResponseServerError(response.details)

    response = req.zato.client.invoke('file-transfer.pgp-key.get', {'id': key_id})

    if not response.ok:
        return HttpResponseServerError('PGP key not found')

    return TemplateResponse(req, 'zato/file_transfer/pgp_key/edit.html', {
        'pgp_key': response.data,
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def pgp_key_delete(req:'HttpRequest', key_id:'str') -> 'HttpResponse':

    response = req.zato.client.invoke('file-transfer.pgp-key.delete', {'id': key_id})

    if response.ok:
        return HttpResponse('{"ok": true}', content_type='application/json')
    else:
        return HttpResponseServerError(f'{{"ok": false, "error": "{response.details}"}}', content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################
