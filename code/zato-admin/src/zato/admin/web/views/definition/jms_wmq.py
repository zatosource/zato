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
from lxml import etree
from lxml.objectify import Element

# Validate
from validate import is_boolean

# anyjson
from anyjson import dumps

# Zato
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms import ChangePasswordForm, ChooseClusterForm
from zato.admin.web.forms.definition.jms_wmq import CreateForm, EditForm
from zato.admin.web.views import meth_allowed
from zato.common.odb.model import Cluster, ConnDefWMQ
from zato.common import zato_namespace, zato_path, ZatoException, ZATO_NOT_GIVEN
from zato.common.util import TRACE1

logger = logging.getLogger(__name__)

def _get_edit_create_message(params, prefix=''):
    """ Creates a base document which can be used by both 'edit' and 'create' actions.
    """
    zato_message = Element('{%s}zato_message' % zato_namespace)
    zato_message.data = Element('data')
    zato_message.data.id = params.get('id')
    zato_message.data.cluster_id = params['cluster_id']
    zato_message.data.name = params[prefix + 'name']
    zato_message.data.host = params[prefix + 'host']
    zato_message.data.port = int(params[prefix + 'port'])
    zato_message.data.queue_manager = params[prefix + 'queue_manager']
    zato_message.data.channel = params[prefix + 'channel']
    zato_message.data.cache_open_send_queues = bool(params.get(prefix + 'cache_open_send_queues'))
    zato_message.data.cache_open_receive_queues = bool(params.get(prefix + 'cache_open_receive_queues'))
    zato_message.data.use_shared_connections = bool(params.get(prefix + 'use_shared_connections'))
    zato_message.data.ssl = bool(params.get(prefix + 'ssl'))
    zato_message.data.ssl_cipher_spec = params.get(prefix + 'ssl_cipher_spec')
    zato_message.data.ssl_key_repository = params.get(prefix + 'ssl_key_repository')
    zato_message.data.needs_mcd = bool(params.get(prefix + 'needs_mcd'))
    zato_message.data.max_chars_printed = params[prefix + 'max_chars_printed']

    return zato_message

def _edit_create_response(zato_message, action, name):
    return_data = {'id': zato_message.data.def_jms_wmq.id.text,
                   'message': 'Successfully {0} the JMS WebSphere MQ definition [{1}]'.format(action, name)}
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
        
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.data = Element('data')
        zato_message.data.cluster_id = cluster_id
        
        _, zato_message, soap_response  = invoke_admin_service(cluster,
                'zato:definition.jms_wmq.get-list', zato_message)
        
        if zato_path('data.definition_list.definition').get_from(zato_message) is not None:
            
            for definition_elem in zato_message.data.definition_list.definition:

                id = definition_elem.id.text
                name = definition_elem.name.text
                host = definition_elem.host.text
                port = definition_elem.port.text
                queue_manager = definition_elem.queue_manager.text
                channel = definition_elem.channel.text
                cache_open_send_queues = is_boolean(definition_elem.cache_open_send_queues.text)
                cache_open_receive_queues = is_boolean(definition_elem.cache_open_receive_queues.text)
                use_shared_connections = is_boolean(definition_elem.use_shared_connections.text)
                ssl = is_boolean(definition_elem.ssl.text)
                ssl_cipher_spec = definition_elem.ssl_cipher_spec.text
                ssl_key_repository = definition_elem.ssl_key_repository.text
                needs_mcd = is_boolean(definition_elem.needs_mcd.text)
                max_chars_printed = definition_elem.max_chars_printed.text
                
                def_jms_wmq = ConnDefWMQ(id, name, host, port, queue_manager, channel,
                    cache_open_send_queues, cache_open_receive_queues, use_shared_connections, 
                    ssl, ssl_cipher_spec, ssl_key_repository, needs_mcd, max_chars_printed)
                
                items.append(def_jms_wmq)
                

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

    return render_to_response('zato/definition/jms_wmq.html', return_data,
                              context_instance=RequestContext(req))

@meth_allowed('POST')
def create(req):
    
    cluster = req.odb.query(Cluster).filter_by(id=req.POST['cluster_id']).first()
    
    try:
        zato_message = _get_edit_create_message(req.POST)
        _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:definition.jms_wmq.create', zato_message)

        return _edit_create_response(zato_message, 'created', req.POST['name'])        
        
    except Exception, e:
        msg = "Could not create a JMS WebSphere MQ definition, e=[{e}]".format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

    
@meth_allowed('POST')
def edit(req):
    
    cluster = req.odb.query(Cluster).filter_by(id=req.POST['cluster_id']).first()
    
    try:
        zato_message = _get_edit_create_message(req.POST, 'edit-')
        _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:definition.jms_wmq.edit', zato_message)

        return _edit_create_response(zato_message, 'updated', req.POST['edit-name'])        
        
    except Exception, e:
        msg = "Could not update a JMS WebSphere MQ definition, e=[{e}]".format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    
@meth_allowed('POST')
def delete(req, id, cluster_id):
    
    cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()
    
    try:
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.data = Element('data')
        zato_message.data.id = id
        
        _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:definition.jms_wmq.delete', zato_message)
        
        return HttpResponse()
    
    except Exception, e:
        msg = "Could not delete the JMS WebSphere MQ definition, e=[{e}]".format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    