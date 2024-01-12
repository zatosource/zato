# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms.kvdb.data_dict.translation import CreateForm, EditForm, TranslateForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.api import ZATO_NONE
from zato.common.json_internal import dumps

logger = logging.getLogger(__name__)

def _get_systems(client):
    systems = []
    for item in client.invoke('zato.kvdb.data-dict.dictionary.get-system-list', {}):
        systems.append([item.name] * 2)
    return systems

class DictItem:
    pass

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'kvdb-data-dict-translation'
    template = 'zato/kvdb/data_dict/translation/index.html'
    service_name = 'zato.kvdb.data-dict.translation.get-list'
    output_class = DictItem

    class SimpleIO(_Index.SimpleIO):
        output_required = ('id', 'system1', 'key1', 'value1', 'system2', 'key2', 'value2')
        output_repeated = True

    def handle(self):
        systems = _get_systems(self.req.zato.client)
        return {
            'create_form': CreateForm(systems),
            'edit_form': EditForm(systems, prefix='edit'),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('system1', 'key1', 'value1', 'system2', 'key2', 'value2')
        output_required = ('id',)

    def success_message(self, item):
        return 'Successfully {} the translation between system1:[{}], key1:[{}], value1:[{}] and system2:[{}], key2:[{}], value2:[{}]'.format(
            self.verb, self.input_dict['system1'], self.input_dict['key1'], self.input_dict['value1'],
            self.input_dict['system2'], self.input_dict['key2'], self.input_dict['value2'])

class Create(_CreateEdit):
    url_name = 'kvdb-data-dict-translation-create'
    service_name = 'zato.kvdb.data-dict.translation.create'

class Edit(_CreateEdit):
    url_name = 'kvdb-data-dict-translation-edit'
    form_prefix = 'edit-'
    service_name = 'zato.kvdb.data-dict.translation.edit'

class Delete(_Delete):
    url_name = 'kvdb-data-dict-translation-delete'
    error_message = 'Could not delete the data translation'
    service_name = 'zato.kvdb.data-dict.translation.delete'

def _get_key_value_list(req, service_name, input_dict):
    return_data = []
    for item in req.zato.client.invoke(service_name, input_dict):
        return_data.append({'name':item.name})

    return HttpResponse(dumps(return_data), content_type='application/javascript')

@method_allowed('GET')
def get_key_list(req):
    return _get_key_value_list(req, 'zato.kvdb.data-dict.dictionary.get-key-list', {'system':req.GET['system']})

@method_allowed('GET')
def get_value_list(req):
    return _get_key_value_list(req, 'zato.kvdb.data-dict.dictionary.get-value-list', {'system':req.GET['system'], 'key':req.GET['key']})

@method_allowed('GET', 'POST')
def translate(req):

    result_names = ('system1', 'key1', 'value1', 'system2', 'key2')

    post_data = {}
    for name in result_names:
        post_data[name] = req.POST.get(name, '')

    def _translate():
        result = {}
        response = req.zato.client.invoke('zato.kvdb.data-dict.translation.translate', post_data)

        if response.has_data:
            for name in('value2', 'repr', 'hex', 'sha1', 'sha256'):
                value = getattr(response.data, name, None)
                if value and value != ZATO_NONE:
                    result[name] = value

        return result

    if req.zato.get('cluster'):
        translate_form = TranslateForm(_get_systems(req.zato.client), req.POST)
    else:
        translate_form = None

    return_data = {
        'zato_clusters':req.zato.clusters,
        'cluster_id':req.zato.cluster_id,
        'search_form':req.zato.search_form,
        'translate_form':translate_form,
        'postback':post_data,
        'translation_result': _translate() if req.method == 'POST' else None,
        'show_translation': req.method == 'POST'
    }
    return TemplateResponse(req, 'zato/kvdb/data_dict/translation/translate.html', return_data)
