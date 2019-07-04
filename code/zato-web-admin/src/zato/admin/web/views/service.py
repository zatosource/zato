# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
import json as stdlib_json
from base64 import b64decode
from collections import namedtuple
from datetime import datetime
from traceback import format_exc

# anyjson
from anyjson import dumps, loads

# dateutil
from dateutil.relativedelta import relativedelta

# Django
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError
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
from zato.admin.web import from_utc_to_user, last_hour_start_stop
from zato.admin.web.forms.service import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed, upload_to_server
from zato.common import DATA_FORMAT, SourceCodeInfo, ZATO_NONE
from zato.common.odb.model import Service

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

ExposedThrough = namedtuple('ExposedThrough', ['id', 'name', 'url'])
DeploymentInfo = namedtuple('DeploymentInfo', ['server_name', 'details'])

# ################################################################################################################################

class SlowResponse(object):
    def __init__(self, cid=None, service_name=None, threshold=None, req_ts=None,
            resp_ts=None, proc_time=None, req=None, resp=None, req_html=None, resp_html=None):
        self.cid = cid
        self.service_name = service_name
        self.threshold = threshold
        self.req_ts = req_ts
        self.resp_ts = resp_ts
        self.proc_time = proc_time
        self.req = req
        self.resp = resp
        self.req_html = req_html
        self.resp_html = resp_html

# ################################################################################################################################

data_format_lexer = {
    'json': JSONLexer,
    'xml': MakoXmlLexer
}

# ################################################################################################################################

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

# ################################################################################################################################

def get_public_wsdl_url(cluster, service_name):
    """ Returns an address under which a service's WSDL is publically available.
    """
    return 'http://{}:{}/zato/wsdl?service={}&cluster_id={}'.format(cluster.lb_host,
        cluster.lb_port, service_name, cluster.id)

# ################################################################################################################################

def _get_channels(client, cluster, id, channel_type):
    """ Returns a list of channels of a given type for the given service.
    """
    input_dict = {
        'id': id,
        'channel_type': channel_type
    }
    out = []

    for item in client.invoke('zato.service.get-channel-list', input_dict):

        if channel_type in('plain_http', 'soap'):
            url = reverse('http-soap')
            url += '?connection=channel&transport={}'.format(channel_type)
            url += '&cluster={}'.format(cluster.id)
        else:
            url = reverse('channel-' + channel_type)
            url += '?cluster={}'.format(cluster.id)

        url += '&highlight={}'.format(item.id)

        channel = ExposedThrough(item.id, item.name, url)
        out.append(channel)

    return out

# ################################################################################################################################

def _get_service(req, name):
    """ Returns service details by its name.
    """
    service = Service(name=name)

    input_dict = {
        'name': name,
        'cluster_id': req.zato.cluster_id
    }
    response = req.zato.client.invoke('zato.service.get-by-name', input_dict)

    if response.has_data:
        for name in('id', 'slow_threshold'):
            setattr(service, name, getattr(response.data, name))

    return service

# ################################################################################################################################

def get_pretty_print(value, data_format):
    if data_format == 'xml':
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(value, parser)
        return etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    else:
        value = loads(value)
        return stdlib_json.dumps(value, sort_keys=True, indent=2)

# ################################################################################################################################

class Index(_Index):
    """ A view for listing the services along with their basic statistics.
    """
    method_allowed = 'GET'
    url_name = 'service'
    template = 'zato/service/index.html'
    service_name = 'zato.service.get-list'
    output_class = Service
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id',
        input_optional = 'query',
        output_required = 'id', 'name', 'is_active', 'is_internal', 'impl_name', 'may_be_deleted', 'usage', 'slow_threshold'
        output_optional = 'is_json_schema_enabled', 'needs_json_schema_err_details', 'is_rate_limit_active', \
            'rate_limit_type', 'rate_limit_def', 'rate_limit_check_parent_def'
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit')
        }

# ################################################################################################################################

@method_allowed('POST')
def create(req):
    pass

# ################################################################################################################################

class Edit(CreateEdit):
    method_allowed = 'POST'
    url_name = 'service-edit'
    form_prefix = 'edit-'
    service_name = 'zato.service.edit'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'id', 'is_active', 'slow_threshold'
        input_optional = 'is_json_schema_enabled', 'needs_json_schema_err_details', 'is_rate_limit_active', \
            'rate_limit_type', 'rate_limit_def', 'rate_limit_check_parent_def'
        output_required = 'id', 'name', 'impl_name', 'is_internal', 'usage', 'may_be_deleted'

    def success_message(self, item):
        return 'Successfully {} service `{}`'.format(self.verb, item.name)

# ################################################################################################################################

@method_allowed('GET')
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

        response = req.zato.client.invoke('zato.service.get-by-name', input_dict)
        if response.has_data:
            service = Service()

            for name in('id', 'name', 'is_active', 'impl_name', 'is_internal',
                  'usage', 'time_last', 'time_min_all_time', 'time_max_all_time',
                  'time_mean_all_time'):

                value = getattr(response.data, name)
                if name in('is_active', 'is_internal'):
                    value = is_boolean(value)

                setattr(service, name, value)

            now = datetime.utcnow()
            start = now+relativedelta(minutes=-60)

            response = req.zato.client.invoke('zato.stats.get-by-service', {'service_id':service.id, 'start':start, 'stop':now})
            if response.has_data:
                for name in('mean_trend', 'usage_trend', 'min_resp_time', 'max_resp_time', 'mean', 'usage', 'rate'):
                    value = getattr(response.data, name)
                    if not value or value == ZATO_NONE:
                        value = ''

                    setattr(service, 'time_{}_1h'.format(name), value)

            for channel_type in('plain_http', 'soap', 'amqp', 'jms-wmq', 'zmq'):
                channels = _get_channels(req.zato.client, req.zato.cluster, service.id, channel_type)
                getattr(service, channel_type.replace('jms-', '') + '_channels').extend(channels)

            for item in req.zato.client.invoke('zato.service.get-deployment-info-list', {'id': service.id}):
                service.deployment_info.append(DeploymentInfo(item.server_name, item.details))

            # TODO: There needs to be a new service added zato.service.scheduler.job.get-by-service
            #       or .get-list should start accept a service name. Right now we pull all the
            #       jobs which is suboptimal.
            response = req.zato.client.invoke('zato.scheduler.job.get-list', {'cluster_id':cluster_id})
            if response.has_data:
                for item in response.data:
                    if item.service_name == service_name:
                        url = reverse('scheduler')
                        url += '?cluster={}'.format(cluster_id)
                        url += '&highlight={}'.format(item.id)
                        service.scheduler_jobs.append(ExposedThrough(item.id, item.name, url))

    return_data = {'zato_clusters':req.zato.clusters,
        'service': service,
        'cluster_id':cluster_id,
        'search_form':req.zato.search_form,
        'create_form':create_form,
        'edit_form':edit_form,
        }

    return TemplateResponse(req, 'zato/service/overview.html', return_data)

# ################################################################################################################################

@method_allowed('GET')
def source_info(req, service_name):

    service = Service(name=service_name)
    input_dict = {
        'cluster_id': req.zato.cluster_id,
        'name': service_name
    }

    response = req.zato.client.invoke('zato.service.get-source-info', input_dict)

    if response.has_data:
        service.id = response.data.service_id

        source = b64decode(response.data.source) if response.data.source else ''
        if source:
            source_html = highlight(source, PythonLexer(stripnl=False), HtmlFormatter(linenos='table'))

            service.source_info = SourceCodeInfo()
            service.source_info.source = source
            service.source_info.source_html = source_html
            service.source_info.path = response.data.source_path
            service.source_info.hash = response.data.source_hash
            service.source_info.hash_method = response.data.source_hash_method
            service.source_info.server_name = response.data.server_name

    return_data = {
        'cluster_id':req.zato.cluster_id,
        'service':service,
        }

    return TemplateResponse(req, 'zato/service/source-info.html', return_data)

# ################################################################################################################################

@method_allowed('GET')
def request_response(req, service_name):
    service = Service(name=service_name)
    pretty_print = asbool(req.GET.get('pretty_print'))

    input_dict = {
        'name': service_name,
        'cluster_id': req.zato.cluster_id
    }

    service_response = req.zato.client.invoke('zato.service.get-request-response', input_dict)
    if service_response.ok:
        request = b64decode(service_response.data.sample_req if service_response.data.sample_req else '')
        request = request.decode('utf8')
        request_data_format = known_data_format(request)
        if request_data_format:
            if pretty_print:
                request = get_pretty_print(request, request_data_format)
            service.sample_req_html = highlight(request, data_format_lexer[request_data_format](),
                HtmlFormatter(linenos='table'))

        response = b64decode(service_response.data.sample_resp if service_response.data.sample_resp else '')
        response = response.decode('utf8')
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
            value = getattr(service_response.data, full_name, '')
            if value:
                value = from_utc_to_user(value+'+00:00', req.zato.user_profile)
            ts[full_name] = value

        service.id = service_response.data.service_id
        service.sample_cid = service_response.data.sample_cid
        service.sample_req_ts = ts['sample_req_ts']
        service.sample_resp_ts = ts['sample_resp_ts']
        service.sample_req_resp_freq = service_response.data.sample_req_resp_freq

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'service': service,
        'pretty_print': not pretty_print,
        }

    return TemplateResponse(req, 'zato/service/request-response.html', return_data)

# ################################################################################################################################

@method_allowed('POST')
def request_response_configure(req, service_name, cluster_id):
    try:
        input_dict = {
            'name': service_name,
            'cluster_id': req.zato.cluster_id,
            'sample_req_resp_freq': req.POST['sample_req_resp_freq']
        }
        req.zato.client.invoke('zato.service.configure-request-response', input_dict)
        return HttpResponse('Saved successfully')

    except Exception:
        msg = 'Could not update the configuration, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'service-delete'
    error_message = 'Service could not be deleted'
    service_name = 'zato.service.delete'

# ################################################################################################################################

@method_allowed('POST')
def package_upload(req, cluster_id):
    """ Handles a service package file upload.
    """
    return upload_to_server(req, cluster_id, 'zato.service.upload-package', 'Could not upload the service package, e:`{}`')

# ################################################################################################################################

@method_allowed('POST')
def last_stats(req, service_id, cluster_id):

    return_data = {
        'rate': '(error)',
        'mean': '(error)',
        'mean_trend': '(error)',
        }

    try:
        start, stop = last_hour_start_stop(datetime.utcnow())
        response = req.zato.client.invoke('zato.stats.get-by-service', {'service_id': service_id, 'start':start, 'stop':stop})

        if response.has_data:
            for key in return_data:
                value = getattr(response.data, key) or ''

                if value and key.endswith('trend') and value != ZATO_NONE:
                    value = [int(float(elem)) for elem in value.split(',')]

                if value == '0.0':
                    value = '<0.1'

                return_data[key] = value if value != ZATO_NONE else '0'

    except Exception:
        msg = 'Caught an exception while invoking zato.service.get-by-service, e:`{}`'.format(format_exc())
        logger.error(msg)

    return HttpResponse(dumps(return_data), content_type='application/javascript')

# ################################################################################################################################

@method_allowed('GET')
def slow_response(req, service_name):

    items = []
    input_dict = {
        'name': service_name,
    }

    for _item in req.zato.client.invoke('zato.service.slow-response.get-list', input_dict):
        item = SlowResponse()
        item.cid = _item.cid
        item.req_ts = from_utc_to_user(_item.req_ts+'+00:00', req.zato.user_profile)
        item.resp_ts = from_utc_to_user(_item.resp_ts+'+00:00', req.zato.user_profile)
        item.proc_time = _item.proc_time
        item.service_name = service_name

        items.append(item)

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'service': _get_service(req, service_name),
        'items': items,
        }

    return TemplateResponse(req, 'zato/service/slow-response.html', return_data)

# ################################################################################################################################

@method_allowed('GET')
def slow_response_details(req, cid, service_name):

    item = None
    service = _get_service(req, service_name)
    pretty_print = asbool(req.GET.get('pretty_print'))

    input_dict = {
        'cid': cid,
        'name': service_name,
    }
    response = req.zato.client.invoke('zato.service.slow-response.get', input_dict)

    if response.has_data:
        cid = response.data.cid
        if cid != ZATO_NONE:
            item = SlowResponse()
            item.cid = response.data.cid
            item.req_ts = from_utc_to_user(response.data.req_ts+'+00:00', req.zato.user_profile)
            item.resp_ts = from_utc_to_user(response.data.resp_ts+'+00:00', req.zato.user_profile)
            item.proc_time = response.data.proc_time
            item.service_name = service_name
            item.threshold = service.slow_threshold

            for name in('req', 'resp'):
                value = getattr(response.data, name)
                if value:
                    if isinstance(value, dict):
                        value = dumps(value)
                        data_format = 'json'
                    else:
                        data_format = known_data_format(value)

                    if data_format:
                        if pretty_print:
                            value = get_pretty_print(value, data_format)
                        attr_name = name + '_html'
                        setattr(item, attr_name, highlight(value,
                             data_format_lexer[data_format](), HtmlFormatter(linenos='table')))

                    else:
                        # Regular raw value
                        setattr(item, name, value)

                        # We do not have an HTML version but we need to populate it anyway for pretty-print toggling
                        setattr(item, name + '_html', value)

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'service': service,
        'item': item,
        'pretty_print': not pretty_print,
        }

    return TemplateResponse(req, 'zato/service/slow-response-details.html', return_data)

# ################################################################################################################################

@method_allowed('GET')
def invoker(req, service_name):

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'service': _get_service(req, service_name),
        }

    return TemplateResponse(req, 'zato/service/invoker.html', return_data)

# ################################################################################################################################

@method_allowed('POST')
def invoke(req, name, cluster_id):
    """ Executes a service directly, even if it isn't exposed through any channel.
    """
    try:
        input_dict = {}
        for attr in('payload', 'data_format', 'transport'):
            input_dict[attr] = req.POST.get(attr, '')
            input_dict['to_json'] = True if input_dict.get('data_format') == DATA_FORMAT.JSON else False

        response = req.zato.client.invoke(name, **input_dict)

    except Exception:
        msg = 'Could not invoke the service. name:`{}`, cluster_id:`{}`, e:`{}`'.format(name, cluster_id, format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        try:
            if response.ok:
                return HttpResponse(response.inner_service_response or '(None)')
            else:
                return HttpResponseServerError(response.details)
        except Exception:
            return HttpResponseServerError(format_exc())

# ################################################################################################################################
