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
from zato.admin.settings import delivery_friendly_name
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms import ChooseClusterForm
from zato.admin.web.forms.outgoing.amqp import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, meth_allowed
from zato.common.odb.model import Cluster, OutgoingAMQP
from zato.common import zato_namespace, zato_path
from zato.common.util import TRACE1

logger = logging.getLogger(__name__)

def _get_def_ids(cluster):
    out = {}
    zato_message, soap_response  = invoke_admin_service(cluster, 'zato:definition.amqp.get-list', {'cluster_id': cluster.id})
    
    if zato_path('response.item_list.item').get_from(zato_message) is not None:
        for definition_elem in zato_message.response.item_list.item:
            id = definition_elem.id.text
            name = definition_elem.name.text
            out[id] = name
        
    return out
        
def _get_edit_create_message(params, prefix=''):
    """ Creates a base dictionary which can be used by both 'edit' and 'create' actions.
    """
    return {
        'id': params.get('id'),
        'cluster_id': params['cluster_id'],
        'name': params[prefix + 'name'],
        'is_active': bool(params.get(prefix + 'is_active')),
        'def_id': params[prefix + 'def_id'],
        'delivery_mode': params[prefix + 'delivery_mode'],
        'priority': params[prefix + 'priority'],
        'content_type': params.get(prefix + 'content_type'),
        'content_encoding': params.get(prefix + 'content_encoding'),
        'expiration': params.get(prefix + 'expiration'),
        'user_id': params.get(prefix + 'user_id'),
        'app_id': params.get(prefix + 'app_id'),
    }

def _edit_create_response(cluster, verb, id, name, delivery_mode_text, def_id):
    zato_message, soap_response  = invoke_admin_service(cluster, 'zato:definition.amqp.get-by-id', {'id':def_id})
    return_data = {'id': id,
                   'message': 'Successfully {0} the outgoing AMQP connection [{1}]'.format(verb, name),
                   'delivery_mode_text': delivery_mode_text,
                   'def_name': zato_message.response.item.name.text
                }
    return HttpResponse(dumps(return_data), mimetype='application/javascript')

class Index(_Index):
    meth_allowed = 'GET'
    url_name = 'out-amqp'
    template = 'zato/outgoing/amqp.html'
    
    soap_action = 'zato:outgoing.amqp.get-list'
    output_class = OutgoingAMQP
    
    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'delivery_mode', 'priority',
            'content_type', 'content_encoding', 'expiration', 'user_id', 'app_id', 'delivery_mode_text', 'def_name', 'def_id')
        output_repeated = True
    
    def handle(self):
        create_form = CreateForm()
        edit_form = EditForm(prefix='edit')
        
        if self.req.zato.cluster_id:
            def_ids = _get_def_ids(self.req.zato.cluster)
            create_form.set_def_id(def_ids)
            edit_form.set_def_id(def_ids)
        
        return {
            'create_form': create_form,
            'edit_form': edit_form,
        }


@meth_allowed('POST')
def create(req):
    try:
        zato_message = _get_edit_create_message(req.POST)
        zato_message, soap_response = invoke_admin_service(req.zato.cluster, 'zato:outgoing.amqp.create', zato_message)
        delivery_mode_text = delivery_friendly_name[int(req.POST['delivery_mode'])]

        return _edit_create_response(req.zato.cluster, 'created', zato_message.response.item.id.text, 
            req.POST['name'], delivery_mode_text, req.POST['def_id'])
    except Exception, e:
        msg = 'Could not create an outgoing AMQP connection, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

    
@meth_allowed('POST')
def edit(req):
    try:
        zato_message = _get_edit_create_message(req.POST, 'edit-')
        zato_message, soap_response = invoke_admin_service(req.zato.cluster, 'zato:outgoing.amqp.edit', zato_message)
        delivery_mode_text = delivery_friendly_name[int(req.POST['edit-delivery_mode'])]

        return _edit_create_response(req.zato.cluster, 'updated', req.POST['id'], req.POST['edit-name'],
            delivery_mode_text, req.POST['edit-def_id'])
    except Exception, e:
        msg = 'Could not update the outgoing AMQP connection, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    
class Delete(_Delete):
    url_name = 'out-amqp-delete'
    error_message = 'Could not delete the outgoing AMQP connection'
    soap_action = 'zato:outgoing.amqp.delete'
