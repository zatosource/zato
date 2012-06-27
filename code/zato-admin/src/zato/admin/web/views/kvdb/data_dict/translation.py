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

# Zato
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms.kvdb.data_dict.translation import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index

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
        for item in zato_message.response.item_list.item:
            systems.append([item.system.text] * 2)
            
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
        return 'Successfully {} the translation system1:[{}], key1:[{}], value1:[{}] system2:[{}], key2:[{}], value2:[{}]'.format(
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
