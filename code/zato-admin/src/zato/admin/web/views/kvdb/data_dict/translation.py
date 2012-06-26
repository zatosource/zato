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
from zato.admin.web.forms.kvdb.data_dict.dictionary import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index

logger = logging.getLogger(__name__)

class DictItem(object):
    def __init__(self, system, name, value):
        self.system = system
        self.name = name
        self.value = value

class Translation(object):
    def __init__(self, source_system, target_system, source_name, target_name, source_value, target_value):
        self.source_system = source_system
        self.target_system = target_system
        self.source_name = source_name
        self.target_name = target_name
        self.source_value = source_value
        self.target_value = target_value

class Index(_Index):
    meth_allowed = 'GET'
    url_name = 'kvdb-data-dict-translation'
    template = 'zato/kvdb/data_dict/translation.html'
    
    soap_action = 'zato:kvdb.data-dict.translation.get-list'
    output_class = Translation
    
    class SimpleIO(_Index.SimpleIO):
        output_required = ('name', 'source_system', 'target_system', 'source_name', 'target_name', 'source_value', 'target_value')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

class _CreateEdit(CreateEdit):
    meth_allowed = 'POST'
    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'host', 'user', 'timeout', 'acct', 'port', 'dircache')
        output_required = ('id', 'name')
        
    def success_message(self, item):
        return 'Successfully {0} the dictionary [{1}]'.format(self.verb, item.name.text)

class Create(_CreateEdit):
    url_name = 'kvdb-data-dict-translationcreate'
    soap_action = 'zato:kvdb.data-dict.translation.create'

class Edit(_CreateEdit):
    url_name = 'kvdb-data-dict-translation-edit'
    form_prefix = 'edit-'
    soap_action = 'zato:kvdb.data-dict.translation.edit'

class Delete(_Delete):
    url_name = 'kvdb-data-dict-translation-delete'
    error_message = 'Could not delete the data dictionary'
    soap_action = 'zato:kvdb.data-dict.translation.delete'
