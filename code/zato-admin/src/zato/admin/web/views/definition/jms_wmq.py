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
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import RequestContext

# lxml
from lxml.objectify import Element

# Validate
from validate import is_boolean

# anyjson
from anyjson import dumps

# Zato
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms import ChooseClusterForm
from zato.admin.web.forms.definition.jms_wmq import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, meth_allowed
from zato.common.odb.model import Cluster, ConnDefWMQ
from zato.common import zato_namespace, zato_path
from zato.common.util import TRACE1

logger = logging.getLogger(__name__)

class Index(_Index):
    meth_allowed = 'GET'
    url_name = 'def-jms-wmq'
    template = 'zato/definition/jms_wmq.html'
    
    soap_action = 'zato:definition.jms_wmq.get-list'
    output_class = ConnDefWMQ
    
    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'host', 'port', 'queue_manager', 'channel', 'cache_open_send_queues', 
            'cache_open_receive_queues', 'use_shared_connections', 'ssl', 'ssl_cipher_spec', 'ssl_key_repository', 'needs_mcd', 'max_chars_printed')
        output_repeated = True
        
    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

class _CreateEdit(CreateEdit):
    meth_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'host', 'port', 'queue_manager', 'channel', 'cache_open_send_queues', 'cache_open_receive_queues', 
            'use_shared_connections', 'ssl', 'ssl_cipher_spec', 'ssl_key_repository', 'needs_mcd', 'max_chars_printed')
        output_required = ('id',)
        
    def success_message(self, item):
        return 'Successfully {0} the JMS WebSphere MQ definition [{1}]'.format(self.verb, item.name.text)

class Create(_CreateEdit):
    url_name = 'def-jms-wmq-create'
    soap_action = 'zato:definition.jms_wmq.create'
    
class Edit(_CreateEdit):
    url_name = 'def-jms-wmq-edit'
    form_prefix = 'edit-'
    soap_action = 'zato:definition.jms_wmq.edit'

class Delete(_Delete):
    url_name = 'def-jms-wmq-delete'
    error_message = 'Could not delete the JMS WebSphere MQ definition'
    soap_action = 'zato:definition.jms_wmq.delete'
