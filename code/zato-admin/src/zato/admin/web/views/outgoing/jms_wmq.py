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
from django.template.response import TemplateResponse

# Validate
from validate import is_boolean

# anyjson
from anyjson import dumps

# Zato
from zato.admin.settings import delivery_friendly_name
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms.outgoing.jms_wmq import CreateForm, EditForm
from zato.admin.web.views import Delete as _Delete, meth_allowed
from zato.common.odb.model import OutgoingWMQ
from zato.common import zato_path

logger = logging.getLogger(__name__)

def _get_def_ids(cluster):
    out = {}
    zato_message, soap_response  = invoke_admin_service(cluster, 'zato:definition.jms_wmq.get-list', {'cluster_id':cluster.id})
    
    if zato_path('item_list.item').get_from(zato_message) is not None:
        for definition_elem in zato_message.item_list.item:
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
        'expiration': params.get(prefix + 'expiration'),
    }

def _edit_create_response(cluster, verb, id, name, delivery_mode_text, cluster_id, def_id):
    zato_message, soap_response  = invoke_admin_service(cluster, 'zato:definition.jms_wmq.get-by-id', {'id':def_id, 'cluster_id':cluster_id})    
    return_data = {'id': id,
                   'message': 'Successfully {0} the outgoing JMS WebSphere MQ connection [{1}]'.format(verb, name),
                   'delivery_mode_text': delivery_mode_text,
                   'def_name': zato_message.item.name.text
                }
    
    return HttpResponse(dumps(return_data), mimetype='application/javascript')

@meth_allowed('GET')
def index(req):
    items = []
    create_form = CreateForm()
    edit_form = EditForm(prefix='edit')

    if req.zato.cluster_id and req.method == 'GET':
        def_ids = _get_def_ids(req.zato.cluster)
        create_form.set_def_id(def_ids)
        edit_form.set_def_id(def_ids)

        zato_message, soap_response  = invoke_admin_service(req.zato.cluster, 'zato:outgoing.jms_wmq.get-list', {'cluster_id': req.zato.cluster_id})
        
        if zato_path('item_list.item').get_from(zato_message) is not None:
            for msg_item in zato_message.item_list.item:
                id = msg_item.id.text
                name = msg_item.name.text
                is_active = is_boolean(msg_item.is_active.text)
                delivery_mode = int(msg_item.delivery_mode.text)
                priority = msg_item.priority.text
                expiration = msg_item.expiration.text
                delivery_mode_text = delivery_friendly_name[delivery_mode]
                def_name = msg_item.def_name.text
                def_id = msg_item.def_id.text
                
                item = OutgoingWMQ(id, name, is_active, delivery_mode, priority, expiration, def_id, delivery_mode_text, def_name)
                items.append(item)

    return_data = {'zato_clusters':req.zato.clusters,
        'cluster_id':req.zato.cluster_id,
        'choose_cluster_form':req.zato.choose_cluster_form,
        'items':items,
        'create_form':create_form,
        'edit_form':edit_form,
        }

    return TemplateResponse(req, 'zato/outgoing/jms_wmq.html', return_data)

@meth_allowed('POST')
def create(req):
    try:
        zato_message, soap_response = invoke_admin_service(req.zato.cluster, 'zato:outgoing.jms_wmq.create', _get_edit_create_message(req.POST))
        delivery_mode_text = delivery_friendly_name[int(req.POST['delivery_mode'])]

        return _edit_create_response(req.zato.cluster, 'created', zato_message.item.id.text, 
            req.POST['name'], delivery_mode_text, req.POST['cluster_id'], req.POST['def_id'])
    except Exception, e:
        msg = 'Could not create an outgoing JMS WebSphere MQ connection, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

    
@meth_allowed('POST')
def edit(req):
    try:
        zato_message = _get_edit_create_message(req.POST, 'edit-')
        zato_message, soap_response = invoke_admin_service(req.zato.cluster, 'zato:outgoing.jms_wmq.edit', zato_message)
        delivery_mode_text = delivery_friendly_name[int(req.POST['edit-delivery_mode'])]

        return _edit_create_response(req.zato.cluster, 'updated', req.POST['id'], req.POST['edit-name'],
            delivery_mode_text, req.POST['cluster_id'], req.POST['edit-def_id'])
        
    except Exception, e:
        msg = 'Could not update the outgoing JMS WebSphere MQ connection, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    
   
class Delete(_Delete):
    url_name = 'out-jms-wmq-delete'
    error_message = 'Could not delete the outgoing JMS WebSphere MQ connection'
    soap_action = 'zato:outgoing.jms_wmq.delete'
