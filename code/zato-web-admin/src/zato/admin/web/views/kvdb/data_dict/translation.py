# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# anyjson
from anyjson import dumps

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms.kvdb.data_dict.translation import CreateForm, EditForm, TranslateForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common import ZATO_NONE, zato_path

logger = logging.getLogger(__name__)

def _get_systems(cluster):
    systems = []
    zato_message, _  = invoke_admin_service(cluster, 'zato.kvdb.data-dict.dictionary.get-system-list', {})
    if zato_path('item_list.item').get_from(zato_message) is not None:
        for item in zato_message.item_list.item:
            systems.append([item.name.text] * 2)
    return systems

class DictItem(object):
    pass

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'kvdb-data-dict-translation'
    template = 'zato/kvdb/data_dict/translation/index.html'
    
    soap_action = 'zato.kvdb.data-dict.translation.get-list'
    output_class = DictItem
    
    class SimpleIO(_Index.SimpleIO):
        output_required = ('id', 'system1', 'key1', 'value1', 'system2', 'key2', 'value2')
        output_repeated = True

    def handle(self):
        systems = _get_systems(self.req.zato.cluster)
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
    soap_action = 'zato.kvdb.data-dict.translation.create'

class Edit(_CreateEdit):
    url_name = 'kvdb-data-dict-translation-edit'
    form_prefix = 'edit-'
    soap_action = 'zato.kvdb.data-dict.translation.edit'

class Delete(_Delete):
    url_name = 'kvdb-data-dict-translation-delete'
    error_message = 'Could not delete the data translation'
    soap_action = 'zato.kvdb.data-dict.translation.delete'

def _get_key_value_list(req, service_name, input_dict):
    return_data = []
    zato_message, _  = invoke_admin_service(req.zato.cluster, service_name, input_dict)
    if zato_path('item_list.item').get_from(zato_message) is not None:
        for item in zato_message.item_list.item:
            return_data.append({'name':item.name.text})
    
    return HttpResponse(dumps(return_data), mimetype='application/javascript')

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
        zato_message, _  = invoke_admin_service(req.zato.cluster, 'zato.kvdb.data-dict.translation.translate', post_data)
        
        if zato_path('item').get_from(zato_message) is not None:
            for name in('value2', 'repr', 'hex', 'sha1', 'sha256'):
                value = getattr(zato_message.item, name, None)
                if value and value.text != ZATO_NONE:
                    result[name] = value.text
        
        return result

    if req.zato.get('cluster'):
        translate_form = TranslateForm(_get_systems(req.zato.cluster), req.POST)
    else:
        translate_form = None
        
    return_data = {
        'zato_clusters':req.zato.clusters,
        'cluster_id':req.zato.cluster_id,
        'choose_cluster_form':req.zato.choose_cluster_form,
        'translate_form':translate_form,
        'postback':post_data,
        'translation_result': _translate() if req.method == 'POST' else None,
        'show_translation': req.method == 'POST'
    }
    return TemplateResponse(req, 'zato/kvdb/data_dict/translation/translate.html', return_data)
