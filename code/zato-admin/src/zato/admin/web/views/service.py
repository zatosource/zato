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
from django.template import RequestContext
from django.shortcuts import render_to_response

# lxml
from lxml import etree

# Pygments
from pygments import highlight
from pygments.lexers.web import JSONLexer
from pygments.lexers import MakoXmlLexer, PythonLexer
from pygments.formatters import HtmlFormatter

# validate
from validate import is_boolean

# anyjson
from anyjson import dumps, loads

# Zato
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms.service import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, meth_allowed
from zato.common import SourceInfo, zato_path
from zato.common.odb.model import Service
from zato.common.util import TRACE1

logger = logging.getLogger(__name__)

Channel = namedtuple('Channel', ['id', 'name', 'url'])
DeploymentInfo = namedtuple('DeploymentInfo', ['server_name', 'details'])

data_format_lexer = {
    'json': JSONLexer,
    'xml': MakoXmlLexer
}

def known_data_format(data):
    data_format = None
    try:
        etree.fromstring(data)
        data_format = 'xml'
    except etree.XMLSyntaxError:
        try:
            loads(data)
            data_format = 'json'
        except ValueError:
            pass

    return data_format

def get_public_wsdl_url(cluster, service_name):
    """ Returns an address under which a service's WSDL is publically available.
    """
    return 'http://{}:{}/zato/wsdl?service={}&cluster_id={}'.format(cluster.lb_host, cluster.lb_port, service_name, cluster.id)

def _get_channels(cluster, id, channel_type):
    """ Returns a list of channels of a given type for the given service.
    """
    input_dict = {
        'id': id,
        'channel_type': channel_type
    }
    zato_message, soap_response  = invoke_admin_service(cluster, 'zato:service.get-channel-list', input_dict)

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

class Index(_Index):
    """ A view for listing the services and their basic management.
    """
    meth_allowed = 'GET'
    url_name = 'service'
    template = 'zato/service/index.html'

    soap_action = 'zato:service.get-list'
    output_class = Service

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'is_internal', 'impl_name', 'may_be_deleted', 'usage')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit')
        }

@meth_allowed('POST')
def create(req):
    pass

class Edit(CreateEdit):
    meth_allowed = 'POST'
    url_name = 'service-edit'
    form_prefix = 'edit-'

    soap_action = 'zato:service.edit'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('is_active',)
        output_required = ('id', 'name', 'impl_name', 'is_internal', 'usage')

    def success_message(self, item):
        return 'Successfully {0} the service [{1}]'.format(self.verb, item.name.text)

@meth_allowed('GET')
def details(req, service_name):
    cluster_id = req.GET.get('cluster')
    service = None

    create_form = CreateForm()
    edit_form = EditForm(prefix='edit')

    if cluster_id and req.method == 'GET':

        input_dict = {
            'name': service_name,
            'cluster_id': req.zato.cluster_id
        }
        
        zato_message, _  = invoke_admin_service(req.zato.cluster, 'zato:service.get-by-name', input_dict)
        if zato_path('response.item').get_from(zato_message) is not None:
            service = Service()
            msg_item = zato_message.response.item
            
            for name in('id', 'name', 'is_active', 'impl_name', 'is_internal', 
                'usage', 'time_last', 'time_min_all_time', 'time_max_all_time', 
                'time_mean_all_time'):

                value = getattr(msg_item, name).text
                if name in('is_active', 'is_internal'):
                    value = is_boolean(value)

                setattr(service, name, value)
                
            zato_message, _  = invoke_admin_service(req.zato.cluster, 'zato:stats.get-by-service', {'service_id':service.id, 'minutes':60})
            if zato_path('response.item').get_from(zato_message) is not None:
                msg_item = zato_message.response.item
                for name in('usage', 'min', 'max', 'mean', 'rate', 'trend_mean', 'trend_rate'):
                    setattr(service, 'time_{}_1h'.format(name), getattr(msg_item, name).text)

            for channel_type in('plain_http', 'soap', 'amqp', 'jms-wmq', 'zmq'):
                channels = _get_channels(req.zato.cluster, service.id, channel_type)
                getattr(service, channel_type.replace('jms-', '') + '_channels').extend(channels)

            zato_message, _ = invoke_admin_service(req.zato.cluster, 'zato:service.get-deployment-info-list', {'id': service.id})

            if zato_path('response.item_list.item').get_from(zato_message) is not None:
                for msg_item in zato_message.response.item_list.item:
                    server_name = msg_item.server_name.text
                    details = msg_item.details.text

                    service.deployment_info.append(DeploymentInfo(server_name, loads(details)))

    return_data = {'zato_clusters':req.zato.clusters,
        'service': service,
        'cluster_id':cluster_id,
        'choose_cluster_form':req.zato.choose_cluster_form,
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
        input_dict = {
            'id': service_id,
            'payload': req.POST.get('payload', ''),
            'data_format': req.POST.get('data_format', ''),
            'transport': req.POST.get('transport', ''),
        }
        zato_message, soap_response = invoke_admin_service(req.zato.cluster, 'zato:service.invoke', input_dict)

    except Exception, e:
        msg = 'Could not invoke the service. id:[{}], cluster_id:[{}], e:[{}]'.format(service_id, cluster_id, format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        response = zato_message.response.item.response.text if zato_message.response.item.response else '(No output)'
        return HttpResponse(response)

@meth_allowed('GET')
def source_info(req, service_name):

    service = Service(name=service_name)
    input_dict = {
        'cluster_id': req.zato.cluster_id,
        'name': service_name
    }

    zato_message, soap_response = invoke_admin_service(req.zato.cluster, 'zato:service.get-source-info', input_dict)

    if zato_path('response.item').get_from(zato_message) is not None:
        msg_item = zato_message.response.item
        service.id = msg_item.service_id.text

        source = msg_item.source.text.decode('base64') if msg_item.source else ''
        if source:
            source_html = highlight(source, PythonLexer(stripnl=False), HtmlFormatter(linenos='table'))

            service.source_info = SourceInfo()
            service.source_info.source = source
            service.source_info.source_html = source_html
            service.source_info.path = msg_item.source_path.text
            service.source_info.hash = msg_item.source_hash.text
            service.source_info.hash_method = msg_item.source_hash_method.text
            service.source_info.server_name = msg_item.server_name.text

    return_data = {
        'cluster_id':req.zato.cluster_id,
        'service':service,
        }

    return render_to_response('zato/service/source-info.html', return_data, context_instance=RequestContext(req))

@meth_allowed('GET')
def wsdl(req, service_name):
    service = Service(name=service_name)
    has_wsdl = False
    wsdl_public_url = get_public_wsdl_url(req.zato.cluster, service_name)

    input_dict = {
        'name': service_name,
        'cluster_id': req.zato.cluster_id
    }
    zato_message, soap_response = invoke_admin_service(req.zato.cluster, 'zato:service.has-wsdl', input_dict)

    if zato_path('response.item').get_from(zato_message) is not None:
        service.id = zato_message.response.item.service_id.text
        has_wsdl = is_boolean(zato_message.response.item.has_wsdl.text)

    return_data = {
        'cluster_id':req.zato.cluster_id,
        'service':service,
        'has_wsdl':has_wsdl,
        'wsdl_public_url':wsdl_public_url,
        }

    return render_to_response('zato/service/wsdl.html', return_data, context_instance=RequestContext(req))

@meth_allowed('POST')
def wsdl_upload(req, service_name, cluster_id):
    """ Handles a WSDL file upload.
    """
    try:
        input_dict = {
            'name': service_name,
            'cluster_id': cluster_id,
            'wsdl': req.read().encode('base64'),
            'wsdl_name': req.GET['qqfile']
        }
        zato_message, soap_response = invoke_admin_service(req.zato.cluster, 'zato:service.set-wsdl', input_dict)

        return HttpResponse(dumps({'success': True}))

    except Exception, e:
        msg = 'Could not upload the WSDL, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

@meth_allowed('GET')
def wsdl_download(req, service_name, cluster_id):
    return HttpResponseRedirect(get_public_wsdl_url(req.zato.cluster, service_name))

@meth_allowed('GET')
def request_response(req, service_name):
    service = Service(name=service_name)
    input_dict = {
        'name': service_name,
        'cluster_id': req.zato.cluster_id
    }
    zato_message, soap_response = invoke_admin_service(req.zato.cluster, 'zato:service.get-request-response', input_dict)

    if zato_path('response.item').get_from(zato_message) is not None:
        item = zato_message.response.item

        request = (item.sample_request.text if item.sample_request.text else '').decode('base64')
        request_data_format = known_data_format(request)
        if request_data_format:
            service.sample_request_html = highlight(request, data_format_lexer[request_data_format](), HtmlFormatter(linenos='table'))

        response = (item.sample_response.text if item.sample_response.text else '').decode('base64')
        response_data_format = known_data_format(response)
        if response_data_format:
            service.sample_response_html = highlight(response, data_format_lexer[response_data_format](), HtmlFormatter(linenos='table'))

        service.sample_request = request
        service.sample_response = response

        service.id = item.service_id.text
        service.sample_cid = item.sample_cid.text
        service.sample_req_timestamp = item.sample_req_timestamp.text
        service.sample_resp_timestamp = item.sample_resp_timestamp.text
        service.sample_req_resp_freq = item.sample_req_resp_freq.text

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'service': service,
        }

    return render_to_response('zato/service/request-response.html', return_data, context_instance=RequestContext(req))

@meth_allowed('POST')
def request_response_configure(req, service_name, cluster_id):
    try:
        input_dict = {
            'name': service_name,
            'cluster_id': req.zato.cluster_id,
            'sample_req_resp_freq': req.POST['sample_req_resp_freq']
        }
        invoke_admin_service(req.zato.cluster, 'zato:service.configure-request-response', input_dict)
        return HttpResponse('Saved successfully')

    except Exception, e:
        msg = 'Could not update the configuration, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

class Delete(_Delete):
    url_name = 'service-delete'
    error_message = 'Could not delete the service'
    soap_action = 'zato:service.delete'


@meth_allowed('POST')
def package_upload(req, cluster_id):
    """ Handles a service package file upload.
    """
    try:
        input_dict = {
            'cluster_id': cluster_id,
            'payload': req.read().encode('base64'),
            'payload_name': req.GET['qqfile']
        }
        zato_message, soap_response = invoke_admin_service(req.zato.cluster, 'zato:service.upload-package', input_dict)

        return HttpResponse(dumps({'success': True}))

    except Exception, e:
        msg = 'Could not upload the service package, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    
@meth_allowed('POST')
def last_stats(req, service_id, cluster_id):
    
    return_data = {
        'rate': '(error)',
        'mean': '(error)',
        'trend_mean': '(error)',
        'trend_rate': '(error)',
        }
    
    try:
        zato_message, _ = invoke_admin_service(req.zato.cluster, 'zato:service.get-last-stats', {'service_id': service_id, 'minutes':60})
        
        if zato_path('response.item').get_from(zato_message) is not None:
            item = zato_message.response.item
            for key in return_data:
                value = getattr(item, key).text or ''
                if value and key.startswith('trend'):
                    value = [int(float(elem)) for elem in value.split(',')]
                return_data[key] = value

    except Exception, e:
        msg = 'Caught an exception while invoking zato:service.get-last-stats, e:[{}]'.format(format_exc(e))
        logger.error(msg)
    
    return HttpResponse(dumps(return_data), mimetype='application/javascript')
