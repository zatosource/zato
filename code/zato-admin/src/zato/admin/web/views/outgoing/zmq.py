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
from zato.admin.web.forms.outgoing.zmq import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import OutgoingZMQ

logger = logging.getLogger(__name__)

class Index(_Index):
    meth_allowed = 'GET'
    url_name = 'out-zmq'
    template = 'zato/outgoing/zmq.html'
    
    soap_action = 'zato:outgoing.zmq.get-list'
    output_class = OutgoingZMQ
    
    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'address', 'socket_type')
        output_repeated = True
    
    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

class _CreateEdit(CreateEdit):
    meth_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'address', 'socket_type')
        output_required = ('id',)
        
    def success_message(self, item):
        return 'Successfully {0} the outgoing Zero MQ connection [{1}]'.format(self.verb, item.name.text)

class Create(_CreateEdit):
    url_name = 'out-zmq-create'
    soap_action = 'zato:outgoing.zmq.create'

class Edit(_CreateEdit):
    url_name = 'out-zmq-edit'
    form_prefix = 'edit-'
    soap_action = 'zato:outgoing.zmq.edit'

class Delete(_Delete):
    url_name = 'out-zmq-delete'
    error_message = 'Could not delete the outgoing Zero MQ connection'
    soap_action = 'zato:outgoing.zmq.delete'
