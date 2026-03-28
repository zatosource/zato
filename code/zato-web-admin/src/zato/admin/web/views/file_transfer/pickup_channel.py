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

        response = req.zato.client.invoke('file-transfer.pickup-channel.get-list', {})

        return TemplateResponse(req, 'zato/file_transfer/pickup_channel/index.html', {
            'channels': response.data if response.ok else [],
        })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET', 'POST')
def pickup_channel_create(req:'HttpRequest') -> 'HttpResponse':

    if req.method == 'POST':
        data = {
            'name': req.POST.get('name', ''),
            'source_type': req.POST.get('source_type', 'Sftp'),
            'connection_name': req.POST.get('connection_name', ''),
            'remote_path': req.POST.get('remote_path', ''),
            'file_pattern': req.POST.get('file_pattern', '*'),
            'poll_interval_seconds': float(req.POST.get('poll_interval_seconds', 60)),
            'post_processing_action': req.POST.get('post_processing_action', 'Delete'),
            'archive_path': req.POST.get('archive_path', ''),
            'is_enabled': req.POST.get('is_enabled') == 'on',
        }

        response = req.zato.client.invoke('file-transfer.pickup-channel.create', data)

        if response.ok:
            return HttpResponseRedirect(reverse('file-transfer-pickup-channel'))
        else:
            return HttpResponseServerError(response.details)

    return TemplateResponse(req, 'zato/file_transfer/pickup_channel/create.html', {})

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET', 'POST')
def pickup_channel_edit(req:'HttpRequest', channel_id:'str') -> 'HttpResponse':

    if req.method == 'POST':
        data = {
            'id': channel_id,
            'name': req.POST.get('name', ''),
            'source_type': req.POST.get('source_type', 'Sftp'),
            'connection_name': req.POST.get('connection_name', ''),
            'remote_path': req.POST.get('remote_path', ''),
            'file_pattern': req.POST.get('file_pattern', '*'),
            'poll_interval_seconds': float(req.POST.get('poll_interval_seconds', 60)),
            'post_processing_action': req.POST.get('post_processing_action', 'Delete'),
            'archive_path': req.POST.get('archive_path', ''),
            'is_enabled': req.POST.get('is_enabled') == 'on',
        }

        response = req.zato.client.invoke('file-transfer.pickup-channel.edit', data)

        if response.ok:
            return HttpResponseRedirect(reverse('file-transfer-pickup-channel'))
        else:
            return HttpResponseServerError(response.details)

    response = req.zato.client.invoke('file-transfer.pickup-channel.get', {'id': channel_id})

    if not response.ok:
        return HttpResponseServerError('Pickup channel not found')

    return TemplateResponse(req, 'zato/file_transfer/pickup_channel/edit.html', {
        'channel': response.data,
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def pickup_channel_delete(req:'HttpRequest', channel_id:'str') -> 'HttpResponse':

    response = req.zato.client.invoke('file-transfer.pickup-channel.delete', {'id': channel_id})

    if response.ok:
        return HttpResponse('{"ok": true}', content_type='application/json')
    else:
        return HttpResponseServerError(f'{{"ok": false, "error": "{response.details}"}}', content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################
