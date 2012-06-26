# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at gefira.pl>

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
from zato.admin.web.views import change_password as _change_password
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.definition.amqp import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, meth_allowed
from zato.common.odb.model import ConnDefAMQP

logger = logging.getLogger(__name__)

class Index(_Index):
    meth_allowed = 'GET'
    url_name = 'def-amqp'
    template = 'zato/definition/amqp.html'
    
    soap_action = 'zato:definition.amqp.get-list'
    output_class = ConnDefAMQP
    
    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'host', 'port', 'vhost', 'username', 'frame_max', 'heartbeat')
        output_repeated = True
    
    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm()
        }

class _CreateEdit(CreateEdit):
    meth_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'host', 'port', 'vhost', 'username', 'frame_max', 'heartbeat')
        output_required = ('id',)
        
    def success_message(self, item):
        return 'Successfully {0} the AMQP definition [{1}]'.format(self.verb, item.name.text)

class Create(_CreateEdit):
    url_name = 'def-amqp-create'
    soap_action = 'zato:definition.amqp.create'

class Edit(_CreateEdit):
    url_name = 'def-amqp-edit'
    form_prefix = 'edit-'
    soap_action = 'zato:definition.amqp.edit'

@meth_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato:definition.amqp.change-password')

class Delete(_Delete):
    url_name = 'def-amqp-delete'
    error_message = 'Could not delete the AMQP definition'
    soap_action = 'zato:definition.amqp.delete'
