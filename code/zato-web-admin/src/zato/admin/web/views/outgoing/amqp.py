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

# anyjson
from anyjson import dumps

# Zato
from zato.admin.settings import delivery_friendly_name
from zato.admin.web.forms.outgoing.amqp import CreateForm, EditForm
from zato.admin.web.views import Delete as _Delete, get_definition_list, \
     Index as _Index, method_allowed
from zato.common.odb.model import OutgoingAMQP
from zato.common import zato_path

logger = logging.getLogger(__name__)
        
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

def _edit_create_response(client, verb, id, name, delivery_mode_text, def_id):
    response = client.invoke('zato.definition.amqp.get-by-id', {'id':def_id})
    return_data = {'id': id,
                   'message': 'Successfully {0} the outgoing AMQP connection [{1}]'.format(verb, name),
                   'delivery_mode_text': delivery_mode_text,
                   'def_name': response.data.name
                }
    return HttpResponse(dumps(return_data), mimetype='application/javascript')

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-amqp'
    template = 'zato/outgoing/amqp.html'
    
    service_name = 'zato.outgoing.amqp.get-list'
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
            def_ids = get_definition_list(self.req.zato.client, self.req.zato.cluster, 'amqp')
            create_form.set_def_id(def_ids)
            edit_form.set_def_id(def_ids)
        
        return {
            'create_form': create_form,
            'edit_form': edit_form,
        }

@method_allowed('POST')
def create(req):
    try:
        request = _get_edit_create_message(req.POST)
        response = req.zato.client.invoke('zato.outgoing.amqp.create', request)
        delivery_mode_text = delivery_friendly_name[int(req.POST['delivery_mode'])]

        return _edit_create_response(req.zato.client, 'created', response.data.id, 
            req.POST['name'], delivery_mode_text, req.POST['def_id'])
    except Exception, e:
        msg = 'Could not create an outgoing AMQP connection, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

@method_allowed('POST')
def edit(req):
    try:
        request = _get_edit_create_message(req.POST, 'edit-')
        response = req.zato.client.invoke('zato.outgoing.amqp.edit', request)
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
    service_name = 'zato.outgoing.amqp.delete'
