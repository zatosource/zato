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
from zato.admin.settings import delivery_friendly_name
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms import ChooseClusterForm
from zato.admin.web.forms.service import CreateForm, EditForm
from zato.admin.web.views import meth_allowed
from zato.common.odb.model import Cluster, Service
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
    zato_message.data.is_active = bool(params.get(prefix + 'is_active'))
    
    return zato_message

def _edit_create_response(verb, service_elem):

    return_data = {'id': str(service_elem.id),
                   'is_internal':is_boolean(service_elem.is_internal.text),
                   'impl_name':service_elem.impl_name.text,
                   'usage_count':str(service_elem.usage_count.text),
                   'message': 'Successfully {0} the service [{1}]'.format(verb, service_elem.name.text),
                }

    print(dumps(return_data))
    
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
        
        _, zato_message, soap_response  = invoke_admin_service(cluster, 'zato:service.get-list', zato_message)
        
        if zato_path('data.item_list.item').get_from(zato_message) is not None:
            
            for msg_item in zato_message.data.item_list.item:
                
                id = msg_item.id.text
                name = msg_item.name.text
                is_active = is_boolean(msg_item.is_active.text)
                impl_name = msg_item.impl_name.text
                is_internal = is_boolean(msg_item.is_internal.text)
                usage_count = msg_item.usage_count.text
                
                item =  Service(id, name, is_active, impl_name, is_internal, None, usage_count)
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

    return render_to_response('zato/service/index.html', return_data, context_instance=RequestContext(req))


@meth_allowed('POST')
def create(req):
    pass

@meth_allowed('POST')
def edit(req):
    cluster = req.odb.query(Cluster).filter_by(id=req.POST['cluster_id']).first()
    try:
        zato_message = _get_edit_create_message(req.POST, 'edit-')
        _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:service.edit', zato_message)

        return _edit_create_response('updated', zato_message.data.service)
    except Exception, e:
        msg = "Could not update the service, e=[{e}]".format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

@meth_allowed('GET')
def details(req, service_id):
    zato_clusters = req.odb.query(Cluster).order_by('name').all()
    choose_cluster_form = ChooseClusterForm(zato_clusters, req.GET)
    cluster_id = req.GET.get('cluster')
    service = None
    
    create_form = CreateForm()
    edit_form = EditForm(prefix='edit')

    if cluster_id and req.method == 'GET':
        
        cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.data = Element('data')
        zato_message.data.id = service_id
        zato_message.data.cluster_id = cluster_id
        
        
        _, zato_message, soap_response  = invoke_admin_service(cluster, 'zato:service.get-by-id', zato_message)
        
        if zato_path('data.item').get_from(zato_message) is not None:
            
            msg_item = zato_message.data.item
                
            id = msg_item.id.text
            name = msg_item.name.text
            is_active = is_boolean(msg_item.is_active.text)
            impl_name = msg_item.impl_name.text
            is_internal = is_boolean(msg_item.is_internal.text)
            usage_count = msg_item.usage_count.text
            
            service = Service(id, name, is_active, impl_name, is_internal, None, usage_count)

    return_data = {'zato_clusters':zato_clusters,
        'service': service,
        'cluster_id':cluster_id,
        'choose_cluster_form':choose_cluster_form,
        'create_form':create_form,
        'edit_form':edit_form,
        }
    
    # TODO: Should really be done by a decorator.
    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, 'Returning render_to_response [{0}]'.format(return_data))

    return render_to_response('zato/service/details.html', return_data, context_instance=RequestContext(req))

@meth_allowed('GET')
def invoke(req, service_id, cluster_id):
    pass

@meth_allowed('GET')
def channel(req, service_id, cluster_id):
    pass
    
@meth_allowed('POST')
def delete(req, service_id, cluster_id):
    
    cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()
    
    try:
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.data = Element('data')
        zato_message.data.id = service_id
        
        _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:service.delete', zato_message)
        
        return HttpResponse()
    
    except Exception, e:
        msg = "Could not delete the service, e=[{e}]".format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)