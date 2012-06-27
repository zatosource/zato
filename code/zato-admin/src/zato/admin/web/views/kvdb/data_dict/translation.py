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

# Zato
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms.kvdb.data_dict.translation import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, meth_allowed
from zato.common import zato_path

logger = logging.getLogger(__name__)

class DictItem(object):
    pass

class Index(_Index):
    meth_allowed = 'GET'
    url_name = 'kvdb-data-dict-translation'
    template = 'zato/kvdb/data_dict/translation.html'
    
    soap_action = 'zato:kvdb.data-dict.translation.get-list'
    output_class = DictItem
    
    class SimpleIO(_Index.SimpleIO):
        output_required = ('id', 'system1', 'key1', 'value1', 'system2', 'key2', 'value2')
        output_repeated = True

    def handle(self):
        zato_message, _  = invoke_admin_service(self.req.zato.cluster, 'zato:kvdb.data-dict.dictionary.get-system-list', {})
        systems = []
        if zato_path('response.item_list.item').get_from(zato_message) is not None:
            for item in zato_message.response.item_list.item:
                systems.append([item.name.text] * 2)

        return {
            'create_form': CreateForm(systems),
            'edit_form': EditForm(systems, prefix='edit'),
        }

class _CreateEdit(CreateEdit):
    meth_allowed = 'POST'
    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('system1', 'key1', 'value1', 'system2', 'key2', 'value2')
        output_required = ('id',)
        
    def success_message(self, item):
        return 'Successfully {} the translation between system1:[{}], key1:[{}], value1:[{}] and system2:[{}], key2:[{}], value2:[{}]'.format(
            self.verb, self.input_dict['system1'], self.input_dict['key1'], self.input_dict['value1'],
            self.input_dict['system2'], self.input_dict['key2'], self.input_dict['value2'])

class Create(_CreateEdit):
    url_name = 'kvdb-data-dict-translation-create'
    soap_action = 'zato:kvdb.data-dict.translation.create'

class Edit(_CreateEdit):
    url_name = 'kvdb-data-dict-translation-edit'
    form_prefix = 'edit-'
    soap_action = 'zato:kvdb.data-dict.translation.edit'

class Delete(_Delete):
    url_name = 'kvdb-data-dict-translation-delete'
    error_message = 'Could not delete the data translation'
    soap_action = 'zato:kvdb.data-dict.translation.delete'


def _get_key_value_list(req, service_name, input_dict):
    return_data = []
    zato_message, _  = invoke_admin_service(req.zato.cluster, service_name, input_dict)
    if zato_path('response.item_list.item').get_from(zato_message) is not None:
        for item in zato_message.response.item_list.item:
            return_data.append({'name':item.name.text})
    
    return HttpResponse(dumps(return_data), mimetype='application/javascript')

@meth_allowed('GET')
def get_key_list(req):
    return _get_key_value_list(req, 'zato:kvdb.data-dict.dictionary.get-key-list', {'system':req.GET['system']})

@meth_allowed('GET')
def get_value_list(req):
    return _get_key_value_list(req, 'zato:kvdb.data-dict.dictionary.get-value-list', {'system':req.GET['system'], 'key':req.GET['key']})
