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

# Django
from django.core.urlresolvers import resolve

# Zato
from zato.admin.web.forms.kvdb.data_dict.system import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, meth_allowed

class System(object):
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

class Index(_Index):
    meth_allowed = 'GET'
    url_name = 'kvdb-data-dict-system'
    template = 'zato/kvdb/data_dict/system.html'
    
    soap_action = 'zato:kvdb.data-dict.system.get-list'
    output_class = System
    
    class SimpleIO(_Index.SimpleIO):
        output_required = ('id', 'name',)
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

class _CreateEdit(CreateEdit):
    meth_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name',)
        
    def success_message(self, item):
        return 'Successfully {0} the system [{1}]'.format(self.verb, item.name.text)

class Create(_CreateEdit):
    url_name = 'kvdb-data-dict-system-create'
    soap_action = 'zato:kvdb.data-dict.system.create'

class Edit(_CreateEdit):
    url_name = 'kvdb-data-dict-system-edit'
    form_prefix = 'edit-'
    soap_action = 'zato:kvdb.data-dict.system.edit'

class Delete(_Delete):
    url_name = 'kvdb-data-dict-system-delete'
    error_message = 'Could not delete the system'
    soap_action = 'zato:kvdb.data-dict.system.delete'

    def __call__(self, req, *args, **kwargs):
        return super(Delete, self).__call__(req, {'name': resolve(req.path).kwargs.get('name')}, *args, **kwargs)
