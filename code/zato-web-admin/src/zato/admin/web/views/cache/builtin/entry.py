# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Bunch
from bunch import bunchify

# Django
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import invoke_service_with_json_response, method_allowed
from zato.admin.web.forms.cache.builtin.entry import CreateForm, EditForm
from zato.common import CACHE

# ################################################################################################################################

def _create_edit(req, action, cache_id, cluster_id, _KV_DATATYPE=CACHE.BUILTIN_KV_DATA_TYPE):

    out = {}

    if action == 'create':
        form = CreateForm()
    else:
        key = req.GET['key'].decode('hex')
        entry = bunchify(req.zato.client.invoke('zato.cache.builtin.entry.get', {
                'cluster_id': req.zato.cluster_id,
                'cache_id': cache_id,
                'key': key
            }).data.response)

        form = EditForm({
            'key': key,
            'old_key': key,
            'value': entry.value,
            'key_data_type': _KV_DATATYPE.INT.id if entry.is_key_integer else _KV_DATATYPE.STR.id,
            'value_data_type': _KV_DATATYPE.INT.id if entry.is_value_integer else _KV_DATATYPE.STR.id,
            'expiry': entry.expiry if entry.expiry else 0,
        })

    out.update({
        'zato_clusters': req.zato.clusters,
        'cluster_id': req.zato.cluster_id,
        'form': form,
        'form_action': 'cache-builtin-{}-entry-action'.format(action),
        'action': action,
        'cache_id': cache_id,
        'cache': req.zato.client.invoke('zato.cache.builtin.get', {
                'cluster_id': req.zato.cluster_id,
                'cache_id': cache_id,
            }).data.response
    })

    return TemplateResponse(req, 'zato/cache/builtin/entry.html', out)

# ################################################################################################################################

@method_allowed('GET')
def create(req, cache_id, cluster_id):
    return _create_edit(req, 'create', cache_id, cluster_id)

# ################################################################################################################################

@method_allowed('GET')
def edit(req, cache_id, cluster_id):
    return _create_edit(req, 'edit', cache_id, cluster_id)

# ################################################################################################################################

def _create_edit_action_message(action, post, cache_id, cluster_id):
    message = {
        'cache_id': cache_id,
        'cluster_id': cluster_id,
    }

    # Common request elements
    for name in ('key', 'value', 'replace_existing', 'key_data_type', 'value_data_type', 'expiry'):
        message[name] = post.get(name)

    # Edit will possibly rename the key
    if action == 'edit':
        message['old_key'] = post['old_key']

    return message

# ################################################################################################################################

@method_allowed('POST')
def create_action(req, cache_id, cluster_id):

    return invoke_service_with_json_response(
        req, 'zato.cache.builtin.entry.create', _create_edit_action_message('create', req.POST, cache_id, cluster_id),
        'OK, entry created successfully.', 'Entry could not be created, e:{e}')

# ################################################################################################################################

@method_allowed('POST')
def edit_action(req, cache_id, cluster_id):

    key_encoded = req.POST['key'].encode('utf8').encode('hex')
    new_path = '{}?key={}'.format(req.path.replace('action/', ''), key_encoded)

    extra = {'new_path': new_path}

    return invoke_service_with_json_response(
        req, 'zato.cache.builtin.entry.update', _create_edit_action_message('edit', req.POST, cache_id, cluster_id),
        'OK, entry updated successfully.', 'Entry could not be updated, e:{e}', extra=extra)

# ################################################################################################################################
