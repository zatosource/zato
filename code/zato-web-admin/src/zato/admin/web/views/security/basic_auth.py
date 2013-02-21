# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

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
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.security.basic_auth import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.odb.model import HTTPBasicAuth

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'security-basic-auth'
    template = 'zato/security/basic-auth.html'
    
    soap_action = 'zato.security.basic-auth.get-list'
    output_class = HTTPBasicAuth
    
    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'username', 'realm')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm()
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'username', 'realm')
        output_required = ('id', 'name')
        
    def success_message(self, item):
        return 'Successfully {0} the HTTP Basic Auth definition [{1}]'.format(self.verb, item.name.text)

class Create(_CreateEdit):
    url_name = 'security-basic-auth-create'
    soap_action = 'zato.security.basic-auth.create'

class Edit(_CreateEdit):
    url_name = 'security-basic-auth-edit'
    form_prefix = 'edit-'
    soap_action = 'zato.security.basic-auth.edit'

class Delete(_Delete):
    url_name = 'security-basic-auth-delete'
    error_message = 'Could not delete the HTTP Basic Auth definition'
    soap_action = 'zato.security.basic-auth.delete'
    
@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.security.basic-auth.change-password')
