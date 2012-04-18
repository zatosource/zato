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
from collections import namedtuple
from traceback import format_exc

# Django
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import RequestContext

# lxml
from lxml.objectify import Element

# Pygments
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

# Validate
from validate import is_boolean

# anyjson
from anyjson import dumps, loads

# Zato
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms import ChooseClusterForm
from zato.admin.web.forms.service import CreateForm, EditForm, WSDLUploadForm
from zato.admin.web.views import meth_allowed
from zato.common import SourceInfo, zato_namespace, zato_path
from zato.common.odb.model import Cluster, Service
from zato.common.util import TRACE1

logger = logging.getLogger(__name__)

Channel = namedtuple('Channel', ['id', 'name', 'url'])
DeploymentInfo = namedtuple('DeploymentInfo', ['server_name', 'details'])

def _get_edit_create_message(params, prefix=''):
    """ Creates a base document which can be used by both 'edit' and 'create' actions.
    """
    zato_message = Element('{%s}zato_message' % zato_namespace)
    zato_message.request = Element('request')
    zato_message.request.id = params.get('id')
    zato_message.request.cluster_id = params['cluster_id']
    zato_message.request.name = params[prefix + 'name']
    zato_message.request.is_active = bool(params.get(prefix + 'is_active'))
    
    return zato_message

def _edit_create_response(verb, service_elem):

    return_data = {'id': str(service_elem.id),
                   'is_internal':is_boolean(service_elem.is_internal.text),
                   'impl_name':service_elem.impl_name.text,
                   'usage_count':str(service_elem.usage_count.text),
                   'message': 'Successfully {0} the service [{1}]'.format(verb, service_elem.name.text),
                }
    return HttpResponse(dumps(return_data), mimetype='application/javascript')

def _get_channels(cluster, id, channel_type):
    """ Returns a list of channels of a given type for the given service.
    """
    zato_message = Element('{%s}zato_message' % zato_namespace)
    zato_message.request = Element('request')
    zato_message.request.id = id
    zato_message.request.channel_type = channel_type
    _, zato_message, soap_response  = invoke_admin_service(cluster, 'zato:service.get-channel-list', zato_message)
    
    response = []
    
    if zato_path('response.item_list.item').get_from(zato_message) is not None:
        for msg_item in zato_message.response.item_list.item:

            if channel_type in('plain_http', 'soap'):
                url = reverse('http-soap')
                url += '?connection=channel&transport={}'.format(channel_type)
                url += '&cluster={}'.format(cluster.id)
            else:
                url = reverse('channel-' + channel_type)
                url += '?cluster={}'.format(cluster.id)
                
            url += '&highlight={}'.format(msg_item.id.text)
            
            channel = Channel(msg_item.id.text, msg_item.name.text, url)
            response.append(channel)
            
    return response

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
        zato_message.request = Element('request')
        zato_message.request.cluster_id = cluster_id
        
        _, zato_message, soap_response  = invoke_admin_service(cluster, 'zato:service.get-list', zato_message)
        
        if zato_path('response.item_list.item').get_from(zato_message) is not None:
            
            for msg_item in zato_message.response.item_list.item:
                
                id = msg_item.id.text
                name = msg_item.name.text
                is_active = is_boolean(msg_item.is_active.text)
                impl_name = msg_item.impl_name.text
                is_internal = is_boolean(msg_item.is_internal.text)
                usage_count = msg_item.usage_count.text if hasattr(msg_item, 'usage_count') else 'TODO'
                
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

        return _edit_create_response('updated', zato_message.response.item)
    except Exception, e:
        msg = "Could not update the service, e=[{e}]".format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

@meth_allowed('GET')
def details(req, service_name):
    zato_clusters = req.odb.query(Cluster).order_by('name').all()
    choose_cluster_form = ChooseClusterForm(zato_clusters, req.GET)
    cluster_id = req.GET.get('cluster')
    service = None
    
    create_form = CreateForm()
    edit_form = EditForm(prefix='edit')

    if cluster_id and req.method == 'GET':
        
        cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.request = Element('request')
        zato_message.request.name = service_name
        zato_message.request.cluster_id = cluster_id
        
        _, zato_message, soap_response  = invoke_admin_service(cluster, 'zato:service.get-by-name', zato_message)
        
        if zato_path('response.item').get_from(zato_message) is not None:
            
            msg_item = zato_message.response.item
                
            id = msg_item.id.text
            name = msg_item.name.text
            is_active = is_boolean(msg_item.is_active.text)
            impl_name = msg_item.impl_name.text
            is_internal = is_boolean(msg_item.is_internal.text)
            usage_count = msg_item.usage_count.text
            
            service = Service(id, name, is_active, impl_name, is_internal, None, usage_count)
            
            for channel_type in('plain_http', 'soap', 'amqp', 'jms-wmq', 'zmq'):
                channels = _get_channels(cluster, id, channel_type)
                getattr(service, channel_type.replace('jms-', '') + '_channels').extend(channels)
                
            zato_message = Element('{%s}zato_message' % zato_namespace)
            zato_message.request = Element('request')
            zato_message.request.id = id
            
            _, zato_message, soap_response  = invoke_admin_service(cluster, 'zato:service.get-deployment-info-list', zato_message)
            
            if zato_path('response.item_list.item').get_from(zato_message) is not None:
                for msg_item in zato_message.response.item_list.item:
                    server_name = msg_item.server_name.text
                    details = msg_item.details.text
                    
                    service.deployment_info.append(DeploymentInfo(server_name, loads(details)))

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

@meth_allowed('POST')
def invoke(req, service_id, cluster_id):
    """ Executes a service directly, even if it isn't exposed through any channel.
    """
    try:
        cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.request = Element('request')
        zato_message.request.id = service_id
        zato_message.request.payload = req.POST.get('payload', '')
        zato_message.request.data_format = req.POST.get('data_format', '')
        zato_message.request.transport = req.POST.get('transport', '')

        _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:service.invoke', zato_message)

    except Exception, e:
        msg = 'Could not invoke the service. id:[{}], cluster_id:[{}], e=[{}]'.format(service_id, cluster_id, format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        response = zato_message.response.item.response.text if zato_message.response.item.response else '(No output)'
        return HttpResponse(response)

@meth_allowed('GET')
def source_info(req, service_name):
    cluster_id = req.GET.get('cluster')
    service = Service(name=service_name)
    
    if cluster_id:
        cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.request = Element('request')
        zato_message.request.name = service_name
        zato_message.request.cluster_id = cluster_id

        _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:service.get-source-info', zato_message)
        
        if zato_path('response.item').get_from(zato_message) is not None:
            msg_item = zato_message.response.item
            
            source = msg_item.source.text.decode('base64') if msg_item.source else ''
            if source:
                source_html = highlight(source, PythonLexer(), HtmlFormatter(linenos='table'))
                
                service.source_info = SourceInfo()
                service.source_info.source = source
                service.source_info.source_html = source_html
                service.source_info.path = msg_item.source_path.text
                service.source_info.hash = msg_item.source_hash.text
                service.source_info.hash_method = msg_item.source_hash_method.text
                service.source_info.server_name = msg_item.server_name.text

    return_data = {
        'cluster_id':cluster_id,
        'service':service,
        }
    
    # TODO: Should really be done by a decorator.
    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, 'Returning render_to_response [{0}]'.format(return_data))

    return render_to_response('zato/service/source-info.html', return_data, context_instance=RequestContext(req))

@meth_allowed('GET')
def wsdl(req, service_name):
    cluster_id = req.GET.get('cluster')
    success = req.GET.get('success')
    service = Service(name=service_name)
    
    form = WSDLUploadForm(req.POST, req.FILES)
    
    if cluster_id:
        cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.request = Element('request')
        zato_message.request.name = service_name
        zato_message.request.cluster_id = cluster_id

        _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:service.get-source-info', zato_message)
        
        if zato_path('response.item').get_from(zato_message) is not None:
            msg_item = zato_message.response.item
            
            source = msg_item.source.text.decode('base64') if msg_item.source else ''
            if source:
                source_html = highlight(source, PythonLexer(), HtmlFormatter(linenos='table'))
                
                service.source_info = SourceInfo()
                service.source_info.source = source
                service.source_info.source_html = source_html
                service.source_info.path = msg_item.source_path.text
                service.source_info.hash = msg_item.source_hash.text
                service.source_info.hash_method = msg_item.source_hash_method.text
                service.source_info.server_name = msg_item.server_name.text

    return_data = {
        'cluster_id':cluster_id,
        'service':service,
        'form':form,
        'success':success
        }
    
    return render_to_response('zato/service/wsdl.html', return_data, context_instance=RequestContext(req))

@meth_allowed('POST')
def wsdl_upload(req, service_name):
    cluster_id = req.POST['cluster_id']
    return HttpResponseRedirect(reverse('service-wsdl', args=[service_name]) + '?success=1&cluster=' + cluster_id)

@meth_allowed('GET')
def request_response(req, service_id, cluster_id):
    pass
    
@meth_allowed('POST')
def delete(req, service_id, cluster_id):
    
    cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()
    
    try:
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.request = Element('request')
        zato_message.request.id = service_id
        
        _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:service.delete', zato_message)
        
        return HttpResponse()
    
    except Exception, e:
        msg = "Could not delete the service, e=[{e}]".format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)