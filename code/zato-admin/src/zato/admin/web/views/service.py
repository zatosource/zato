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
import json as stdlib_json
from collections import namedtuple
from datetime import datetime
from traceback import format_exc

# anyjson
from anyjson import dumps, loads

# dateutil
from dateutil.relativedelta import relativedelta

# Django
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template.response import TemplateResponse

# lxml
from lxml import etree

# Paste
from paste.util.converters import asbool

# Pygments
from pygments import highlight
from pygments.lexers.web import JSONLexer
from pygments.lexers import MakoXmlLexer, PythonLexer
from pygments.formatters import HtmlFormatter

# validate
from validate import is_boolean

# Zato
from zato.admin.web import from_utc_to_user, invoke_admin_service, last_hour_start_stop
from zato.admin.web.forms.service import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, meth_allowed
from zato.common import SourceInfo, ZATO_NONE, zato_path
from zato.common.odb.model import Service

logger = logging.getLogger(__name__)

Channel = namedtuple('Channel', ['id', 'name', 'url'])
DeploymentInfo = namedtuple('DeploymentInfo', ['server_name', 'details'])

class SlowResponse(object):
    def __init__(self, cid=None, service_name=None, threshold=None, req_ts=None, 
            resp_ts=None, proc_time=None, req=None, resp=None, req_html=None, resp_html=None):
        self.cid = cid
        self.service_name = service_name
        self.threshold = threshold
        self.req_ts = req_ts
        self.resp_ts = resp_ts
        self.proc_time = proc_time
        self.req  = req
        self.resp = resp
        self.req_html = req_html 
        self.resp_html = resp_html

data_format_lexer = {
    'json': JSONLexer,
    'xml': MakoXmlLexer
}

def known_data_format(data):
    data_format = None
    try:
        etree.fromstring(data)
        data_format = 'xml'
    except etree.XMLSyntaxError, e:
        try:
            loads(data)
            data_format = 'json'
        except ValueError:
            pass

    return data_format

def get_public_wsdl_url(cluster, service_name):
    """ Returns an address under which a service's WSDL is publically available.
    """
    return 'http://{}:{}/zato/wsdl?service={}&cluster_id={}'.format(cluster.lb_host, 
        cluster.lb_port, service_name, cluster.id)

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
    
def _get_service(req, name):
    """ Returns a service details by its name.
    """
    service = Service(name=name)
    
    input_dict = {
        'name': name,
        'cluster_id': req.zato.cluster_id
    }
    zato_message, soap_response = invoke_admin_service(req.zato.cluster, 'zato:service.get-by-name', input_dict)
    
    if zato_path('response.item').get_from(zato_message) is not None:
        for name in('id', 'slow_threshold'):
            setattr(service, name, getattr(zato_message.response.item, name).text)
        
    return service
    
def get_pretty_print(value, data_format):
    if data_format == 'xml':
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(value, parser)
        return etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    else:
        value = loads(value)
        return stdlib_json.dumps(value, sort_keys=True, indent=2)

class Index(_Index):
    """ A view for listing the services along with their basic statistics.
    """
    meth_allowed = 'GET'
    url_name = 'service'
    template = 'zato/service/index.html'

    soap_action = 'zato:service.get-list'
    output_class = Service

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'is_internal', 'impl_name', 
            'may_be_deleted', 'usage', 'slow_threshold')
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
        input_required = ('is_active', 'slow_threshold')
        output_required = ('id', 'name', 'impl_name', 'is_internal', 'usage')

    def success_message(self, item):
        return 'Successfully {0} the service [{1}]'.format(self.verb, item.name.text)

@meth_allowed('GET')
def overview(req, service_name):
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

            now = datetime.utcnow()
            start = now+relativedelta(minutes=-60)
                
            zato_message, _  = invoke_admin_service(req.zato.cluster, 
                'zato:stats.get-by-service', {'service_id':service.id, 'start':start, 'stop':now})
            if zato_path('response.item').get_from(zato_message) is not None:
                msg_item = zato_message.response.item
                for name in('mean_trend', 'usage_trend', 'min_resp_time', 'max_resp_time', 'mean', 'usage', 'rate'):
                    value = getattr(msg_item, name).text
                    if not value or value == ZATO_NONE:
                        value = ''

                    setattr(service, 'time_{}_1h'.format(name), value)

            for channel_type in('plain_http', 'soap', 'amqp', 'jms-wmq', 'zmq'):
                channels = _get_channels(req.zato.cluster, service.id, channel_type)
                getattr(service, channel_type.replace('jms-', '') + '_channels').extend(channels)

            zato_message, _ = invoke_admin_service(req.zato.cluster, 
                'zato:service.get-deployment-info-list', {'id': service.id})

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

    return TemplateResponse(req, 'zato/service/overview.html', return_data)

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

    return TemplateResponse(req, 'zato/service/source-info.html', return_data)

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

    return TemplateResponse(req, 'zato/service/wsdl.html', return_data)

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
    pretty_print = asbool(req.GET.get('pretty_print'))
    
    input_dict = {
        'name': service_name,
        'cluster_id': req.zato.cluster_id
    }
    zato_message, soap_response = invoke_admin_service(req.zato.cluster, 'zato:service.get-request-response', input_dict)

    if zato_path('response.item').get_from(zato_message) is not None:
        item = zato_message.response.item

        request = (item.sample_req.text if item.sample_req.text else '').decode('base64')
        request_data_format = known_data_format(request)
        if request_data_format:
            if pretty_print:
                request = get_pretty_print(request, request_data_format)
            service.sample_req_html = highlight(request, data_format_lexer[request_data_format](), 
                HtmlFormatter(linenos='table'))

        response = (item.sample_resp.text if item.sample_resp.text else '').decode('base64')
        response_data_format = known_data_format(response)
        if response_data_format:
            if pretty_print:
                response = get_pretty_print(response, response_data_format)
            service.sample_resp_html = highlight(response, data_format_lexer[response_data_format](), 
                HtmlFormatter(linenos='table'))

        service.sample_req = request
        service.sample_resp = response

        ts = {}
        for name in('req', 'resp'):
            full_name = 'sample_{}_ts'.format(name)
            value = getattr(item, full_name).text or ''
            if value:
                value = from_utc_to_user(value+'+00:00', req.zato.user_profile)
            ts[full_name] = value
                
        service.id = item.service_id.text
        service.sample_cid = item.sample_cid.text
        service.sample_req_ts = ts['sample_req_ts']
        service.sample_resp_ts = ts['sample_resp_ts']
        service.sample_req_resp_freq = item.sample_req_resp_freq.text

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'service': service,
        'pretty_print': not pretty_print,
        }

    return TemplateResponse(req, 'zato/service/request-response.html', return_data)

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
        'mean_trend': '(error)',
        }
    
    try:
        start, stop = last_hour_start_stop(datetime.utcnow())
        zato_message, _ = invoke_admin_service(req.zato.cluster, 
            'zato:stats.get-by-service', {'service_id': service_id, 'start':start, 'stop':stop})
        
        if zato_path('response.item').get_from(zato_message) is not None:
            item = zato_message.response.item
            for key in return_data:
                value = getattr(item, key).text or ''
                
                if value and key.endswith('trend') and value != ZATO_NONE:
                    value = [int(float(elem)) for elem in value.split(',')]

                if value == '0.0':
                    value = '<0.1'

                return_data[key] = value if value != ZATO_NONE else '0'

    except Exception, e:
        msg = 'Caught an exception while invoking zato:service.get-last-stats, e:[{}]'.format(format_exc(e))
        logger.error(msg)
    
    return HttpResponse(dumps(return_data), mimetype='application/javascript')


@meth_allowed('GET')
def slow_response(req, service_name):

    items = []
    
    input_dict = {
        'name': service_name,
    }
    zato_message, soap_response = invoke_admin_service(req.zato.cluster, 
        'zato:service.slow-response.get-list', input_dict)
    
    if zato_path('response.item_list.item').get_from(zato_message) is not None:
        for _item in zato_message.response.item_list.item:
            item = SlowResponse()
            item.cid = _item.cid.text
            item.req_ts = from_utc_to_user(_item.req_ts.text+'+00:00', req.zato.user_profile)
            item.resp_ts = from_utc_to_user(_item.resp_ts.text+'+00:00', req.zato.user_profile)
            item.proc_time = _item.proc_time.text
            item.service_name = service_name
            
            items.append(item)
        
    return_data = {
        'cluster_id': req.zato.cluster_id,
        'service': _get_service(req, service_name),
        'items': items,
        }
        
    return TemplateResponse(req, 'zato/service/slow-response.html', return_data)
    
@meth_allowed('GET')
def slow_response_details(req, cid, service_name):

    item = None
    service = _get_service(req, service_name)
    pretty_print = asbool(req.GET.get('pretty_print'))
    
    input_dict = {
        'cid': cid,
        'name': service_name,
    }
    zato_message, soap_response = invoke_admin_service(req.zato.cluster, 
        'zato:service.slow-response.get', input_dict)
    
    if zato_path('response.item').get_from(zato_message) is not None:
        _item = zato_message.response.item
        cid = _item.cid.text
        if cid != ZATO_NONE:
            item = SlowResponse()
            item.cid = _item.cid.text
            item.req_ts = from_utc_to_user(_item.req_ts.text+'+00:00', req.zato.user_profile)
            item.resp_ts = from_utc_to_user(_item.resp_ts.text+'+00:00', req.zato.user_profile)
            item.proc_time = _item.proc_time.text
            item.service_name = service_name
            item.threshold = service.slow_threshold
            
            for name in('req', 'resp'):
                value = getattr(_item, name)
                if value:
                    value = value.text.decode('base64')
                    data_format = known_data_format(value)
                    if data_format:
                        if pretty_print:
                            value = get_pretty_print(value, data_format)
                        attr_name = name + '_html'
                        setattr(item, attr_name, highlight(value, 
                             data_format_lexer[data_format](), HtmlFormatter(linenos='table')))

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'service': service,
        'item': item,
        'pretty_print': not pretty_print,
        }
        
    return TemplateResponse(req, 'zato/service/slow-response-details.html', return_data)

@meth_allowed('GET')
def invoker(req, service_name):

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'service': _get_service(req, service_name),
        }

    return TemplateResponse(req, 'zato/service/invoker.html', return_data)

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
        msg = 'Could not invoke the service. id:[{}], cluster_id:[{}], e:[{}]'.format(
            service_id, cluster_id, format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        response = zato_message.response.item.response.text if zato_message.response.item.response else '(No output)'
        return HttpResponse(response)

