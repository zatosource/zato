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
from zato.admin.web.forms.channel.amqp import CreateForm, EditForm
from zato.admin.web.views import meth_allowed
from zato.common.odb.model import Cluster, ChannelAMQP
from zato.common import zato_namespace, zato_path
from zato.common.util import TRACE1

logger = logging.getLogger(__name__)

def _get_def_ids(cluster):
    out = {}
    
    zato_message = Element('{%s}zato_message' % zato_namespace)
    zato_message.request = Element('request')
    zato_message.request.cluster_id = cluster.id        
    _, zato_message, soap_response  = invoke_admin_service(cluster, 'zato:definition.amqp.get-list', zato_message)
    
    if zato_path('response.item_list.item').get_from(zato_message) is not None:
        for definition_elem in zato_message.response.item_list.item:
            id = definition_elem.id.text
            name = definition_elem.name.text
            out[id] = name
        
    return out
        
def _get_edit_create_message(params, prefix=''):
    """ Creates a base document which can be used by both 'edit' and 'create' actions.
    """
    zato_message = Element('{%s}zato_message' % zato_namespace)
    zato_message.request = Element('request')
    zato_message.request.id = params.get('id')
    zato_message.request.cluster_id = params['cluster_id']
    zato_message.request.name = params[prefix + 'name']
    zato_message.request.is_active = bool(params.get(prefix + 'is_active'))
    zato_message.request.def_id = params[prefix + 'def_id']
    zato_message.request.queue = params[prefix + 'queue']
    zato_message.request.consumer_tag_prefix = params[prefix + 'consumer_tag_prefix']
    zato_message.request.service = params[prefix + 'service']
    zato_message.request.request_format = params.get(prefix + 'request_format')

    return zato_message

def _edit_create_response(cluster, verb, id, name, def_id):

    zato_message = Element('{%s}zato_message' % zato_namespace)
    zato_message.request = Element('request')
    zato_message.request.id = def_id
    
    _, zato_message, soap_response  = invoke_admin_service(cluster, 'zato:definition.amqp.get-by-id', zato_message)    
    
    return_data = {'id': id,
                   'message': 'Successfully {0} the AMQP channel [{1}]'.format(verb, name),
                   'def_name': zato_message.response.item.name.text
                }
    
    return HttpResponse(dumps(return_data), mimetype='application/javascript')

@meth_allowed('GET')
def index(req):
    zato_clusters = req.odb.query(Cluster).order_by('name').all()
    choose_cluster_form = ChooseClusterForm(zato_clusters, req.GET)
    cluster_id = req.GET.get('cluster')
    items = []
    
    create_form = CreateForm()
    edit_form = EditForm(prefix='edit')

    if cluster_id and req.method == 'GET':
        
        cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()
        
        def_ids = _get_def_ids(cluster)
        create_form.set_def_id(def_ids)
        edit_form.set_def_id(def_ids)

        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.request = Element('request')
        zato_message.request.cluster_id = cluster_id
        
        _, zato_message, soap_response  = invoke_admin_service(cluster, 'zato:channel.amqp.get-list', zato_message)
        
        if zato_path('response.item_list.item').get_from(zato_message) is not None:
            
            for msg_item in zato_message.response.item_list.item:
                
                id = msg_item.id.text
                name = msg_item.name.text
                is_active = is_boolean(msg_item.is_active.text)
                queue = msg_item.queue.text
                consumer_tag_prefix = msg_item.consumer_tag_prefix.text
                def_name = msg_item.def_name.text
                def_id = msg_item.def_id.text
                service_name = msg_item.service_name.text
                data_format = msg_item.data_format.text
                
                item =  ChannelAMQP(id, name, is_active, queue, consumer_tag_prefix, def_id, def_name, service_name, data_format)
                items.append(item)
                
    return_data = {'zato_clusters':zato_clusters,
        'cluster_id':cluster_id,
        'choose_cluster_form':choose_cluster_form,
        'items':items,
        'create_form':create_form,
        'edit_form':edit_form,
        }
    
    # TODO: Should really be done by a decorator.
    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, 'Returning render_to_response [{0}]'.format(return_data))

    return render_to_response('zato/channel/amqp.html', return_data,
                              context_instance=RequestContext(req))

@meth_allowed('POST')
def create(req):
    
    cluster = req.odb.query(Cluster).filter_by(id=req.POST['cluster_id']).first()
    
    try:
        zato_message = _get_edit_create_message(req.POST)
        _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:channel.amqp.create', zato_message)

        return _edit_create_response(cluster, 'created', zato_message.response.item.id.text, 
            req.POST['name'], req.POST['def_id'])
    except Exception, e:
        msg = 'Could not create an AMQP channel, e=[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

    
@meth_allowed('POST')
def edit(req):
    
    cluster = req.odb.query(Cluster).filter_by(id=req.POST['cluster_id']).first()
    
    try:
        zato_message = _get_edit_create_message(req.POST, 'edit-')
        _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:channel.amqp.edit', zato_message)

        return _edit_create_response(cluster, 'updated', req.POST['id'], req.POST['edit-name'], req.POST['edit-def_id'])
        
    except Exception, e:
        msg = 'Could not update the AMQP channel, e=[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    
@meth_allowed('POST')
def delete(req, id, cluster_id):
    
    cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()
    
    try:
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.request = Element('request')
        zato_message.request.id = id
        
        _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:channel.amqp.delete', zato_message)
        
        return HttpResponse()
    
    except Exception, e:
        msg = 'Could not delete the AMQP channel, e=[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)