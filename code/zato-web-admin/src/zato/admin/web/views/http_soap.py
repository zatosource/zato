# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from http import HTTPStatus
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError, JsonResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web import from_user_to_utc, from_utc_to_user
from zato.admin.web.forms import add_http_soap_select
from zato.admin.web.forms.http_soap import SearchForm, CreateForm, EditForm
from zato.admin.web.views import get_group_list as common_get_group_list, get_http_channel_security_id, \
    get_js_dt_format, get_security_id_from_select, get_security_groups_from_checkbox_list, id_only_service, \
        method_allowed, SecurityList
from zato.common.api import DEFAULT_HTTP_PING_METHOD, DEFAULT_HTTP_POOL_SIZE, \
     generic_attrs, Groups, HTTP_SOAP_SERIALIZATION_TYPE, MISC, PARAMS_PRIORITY, SEC_DEF_TYPE, \
     SOAP_CHANNEL_VERSIONS, URL_PARAMS_PRIORITY, URL_TYPE
from zato.common.content_type import format_content, get_content_type
from zato.common.exception import ZatoException
from zato.common.json_internal import dumps
# Bunch
from zato.common.ext.bunch import Bunch
from zato.common.util import openapi_ as openapi_module

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

CONNECTION = {
    'channel': 'API endpoint',
    'outgoing': 'outgoing connection',
    }

CONNECTION_PLURAL = {
    'channel': 'API endpoints',
    'outgoing': 'outgoing connections',
    }

TRANSPORT = {
    'plain_http': 'REST',
    'soap': 'SOAP',
    }

# Channels whose service is this one are API gateways and get a badge in the channel list
Gateway_Trigger_Service = 'helpers.service-gateway'

_rest_security_type_supported = {
    SEC_DEF_TYPE.APIKEY,
    SEC_DEF_TYPE.BASIC_AUTH,
    SEC_DEF_TYPE.NTLM,
    SEC_DEF_TYPE.OAUTH,
}

# Names of the fields that describe the declarative invocation profile of an outgoing REST connection
_invocation_field_names = (
    'scheduler_run_every',
    'scheduler_run_unit',
    'scheduler_start_date',
    'scheduler_job_id',
    'request_method',
    'request_query_string',
    'request_path_params',
    'request_headers',
    'request_data',
    'request_data_mode',
    'response_map',
    'response_map_mode',
    'callback_type',
    'callback_name',
    'health_check_run_every',
    'health_check_run_unit',
    'health_check_notify_on',
    'health_check_job_id',
    'health_check_callback_type',
    'health_check_callback_name',
)

# The callback name arrives from the widget that matches the callback type selected
_callback_widget_names = {
    'service': 'callback_service',
    'topic': 'callback_topic',
    'rest': 'callback_rest',
}

# The same pattern applies to the health check tab's callback widgets
_health_check_callback_widget_names = {
    'service': 'health_check_callback_service',
    'topic': 'health_check_callback_topic',
    'rest': 'health_check_callback_rest',
}

# ################################################################################################################################
# ################################################################################################################################

def _get_edit_create_message(params, prefix='', user_profile=None): # type: ignore
    """ A bunch of attributes that can be used by both 'edit' and 'create' actions
    for channels and outgoing connections.
    """
    security_id = get_security_id_from_select(params, prefix)
    security_groups = get_security_groups_from_checkbox_list(params, prefix)

    message = {
        'is_internal': False,
        'connection': params['connection'],
        'transport': params['transport'],
        'id': params.get('id'),
        'cluster_id': params['cluster_id'],
        'name': params[prefix + 'name'],
        'is_active': bool(params.get(prefix + 'is_active')),
        'host': params.get(prefix + 'host'),
        'url_path': params.get(prefix + 'url_path', '/'),
        'merge_url_params_req': bool(params.get(prefix + 'merge_url_params_req')),
        'match_slash': bool(params.get(prefix + 'match_slash')),
        'http_accept': params.get(prefix + 'http_accept'),
        'url_params_pri': params.get(prefix + 'url_params_pri', URL_PARAMS_PRIORITY.DEFAULT),
        'params_pri': params.get(prefix + 'params_pri', PARAMS_PRIORITY.DEFAULT),
        'serialization_type': params.get(prefix + 'serialization_type', HTTP_SOAP_SERIALIZATION_TYPE.DEFAULT.id),
        'method': params.get(prefix + 'method'),
        'soap_action': params.get(prefix + 'soap_action', ''),
        'soap_version': params.get(prefix + 'soap_version', None),
        'use_mtom': bool(params.get(prefix + 'use_mtom')),
        'data_format': params.get(prefix + 'data_format') or None,
        'service': params.get(prefix + 'service'),
        'ping_method': params.get(prefix + 'ping_method'),
        'pool_size': params.get(prefix + 'pool_size'),
        'timeout': params.get(prefix + 'timeout'),
        'security_id': security_id,
        'security_groups': security_groups,
        'content_type': params.get(prefix + 'content_type'),
        'validate_tls': params.get(prefix + 'validate_tls'),
        'data_encoding': params.get(prefix + 'data_encoding'),
        'gateway_service_list': params.get(prefix + 'gateway_service_list'),
    }

    # The declarative invocation fields exist only in the forms of outgoing connections
    for name in _invocation_field_names:
        message[name] = params.get(prefix + name)

    # The start date is entered in the user's own timezone and format and it is stored in UTC
    if scheduler_start_date := message['scheduler_start_date']:
        message['scheduler_start_date'] = from_user_to_utc(scheduler_start_date, user_profile).isoformat()

    # The callback name comes from whichever widget matches the callback type selected
    if callback_type := message['callback_type']:
        widget_name = _callback_widget_names[callback_type]
        message['callback_name'] = params.get(prefix + widget_name)

    # The health check tab's callback widgets work the same way
    if health_check_callback_type := message['health_check_callback_type']:
        widget_name = _health_check_callback_widget_names[health_check_callback_type]
        message['health_check_callback_name'] = params.get(prefix + widget_name)

    return message

# ################################################################################################################################
# ################################################################################################################################

def _edit_create_response(req, id, verb, transport, connection, name): # type: ignore

    groups = common_get_group_list(req, Groups.Type.API_Clients, http_soap_channel_id=id)

    group_count = 0
    group_member_count = 0

    for item in groups:
        if item.is_assigned:
            group_count += 1
            group_member_count += item.member_count

    if (group_count == 0) or (group_count > 1):
        group_count_suffix = 's'
    else:
        group_count_suffix = ''

    if (group_member_count == 0) or (group_member_count > 1):
        group_member_count_suffix = 's'
    else:
        group_member_count_suffix = ''

    return_data = {
        'id': id,
        'transport': transport,
        'message': 'Successfully {} {} {} `{}`'.format(verb, TRANSPORT[transport], CONNECTION[connection], name),
        'security_groups_info': f'{group_count} group{group_count_suffix}, {group_member_count} client{group_member_count_suffix}'
    }

    return HttpResponse(dumps(return_data), content_type='application/javascript')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req): # type: ignore
    connection = req.GET.get('connection')
    transport = req.GET.get('transport')
    query = req.GET.get('query', '')
    items = []
    _security = SecurityList()

    if not all((connection, transport)):
        log_msg = "Redirecting to / because at least one of ('connection', 'transport') GET parameters was missing"
        logger.debug(log_msg)
        return HttpResponseRedirect('/')

    # Outgoing SOAP connections have their own dedicated page
    if connection == 'outgoing' and transport == 'soap':
        return HttpResponseRedirect(f'/zato/outgoing/soap/?cluster={req.zato.cluster_id}')

    create_form = None
    edit_form = None
    meta = {}
    response = None

    colspan = 17

    if transport == 'soap':
        colspan += 3

    if req.zato.cluster_id:
        for def_item in req.zato.client.invoke('zato.security.get-list', {'cluster_id': req.zato.cluster.id}):
            if connection == 'outgoing':
                if transport == URL_TYPE.PLAIN_HTTP and def_item.sec_type not in _rest_security_type_supported:
                    continue

            _security.append(def_item)

        create_form = CreateForm(_security, SOAP_CHANNEL_VERSIONS, req=req)
        edit_form = EditForm(_security, SOAP_CHANNEL_VERSIONS, prefix='edit', req=req)

        if connection == 'outgoing':
            create_form.fields['url_path'].required = False
            edit_form.fields['url_path'].required = False

        # The callback tabs let outgoing REST connections deliver responses
        # and health check outcomes to other outgoing REST connections
        if connection == 'outgoing' and transport == URL_TYPE.PLAIN_HTTP:
            add_http_soap_select(create_form, 'callback_rest', req, 'outgoing', URL_TYPE.PLAIN_HTTP, by_id=False)
            add_http_soap_select(edit_form, 'callback_rest', req, 'outgoing', URL_TYPE.PLAIN_HTTP, by_id=False)
            add_http_soap_select(create_form, 'health_check_callback_rest', req, 'outgoing', URL_TYPE.PLAIN_HTTP, by_id=False)
            add_http_soap_select(edit_form, 'health_check_callback_rest', req, 'outgoing', URL_TYPE.PLAIN_HTTP, by_id=False)

        input_dict = {
            'cluster_id': req.zato.cluster_id,
            'connection': connection,
            'transport': transport,
        }

        response = req.zato.client.invoke('zato.http-soap.get-list', input_dict)

        for item in response.data:
            if query not in item.name:
                continue

            _security_name = item.security_name
            if _security_name:
                sec_type_as_link = item.sec_type.replace('_', '-')
                if item.sec_type == SEC_DEF_TYPE.OAUTH:
                    direction = 'outconn/client-credentials/'
                else:
                    direction = ''
                security_href   = f'/zato/security/{sec_type_as_link}/{direction}'
                security_href  += f'?cluster={req.zato.cluster_id}&amp;query={_security_name}'
                security_link = f'<a href="{security_href}">{_security_name}</a>'
                security_name = security_link
            else:
                security_name = '<span class="form_hint">---</span>'

            security_id = get_http_channel_security_id(item)

            http_soap = Bunch()
            http_soap.id = item.id
            http_soap.name = item.name
            http_soap.is_active = item.is_active
            http_soap.is_internal = item.is_internal
            http_soap.connection = connection
            http_soap.transport = transport
            http_soap.host = item.host
            http_soap.url_path = item.url_path
            http_soap.method = item.method
            http_soap.soap_action = item.soap_action
            http_soap.soap_version = item.soap_version

            # The MTOM flag is an opaque attribute, so it is absent from channels that never set it.
            if transport == 'soap':
                use_mtom = item.get('use_mtom')
                if use_mtom is None:
                    use_mtom = False
                http_soap.use_mtom = use_mtom
            http_soap.data_format = item.data_format
            http_soap.security_id = security_id
            http_soap.security_name = security_name
            http_soap.content_type = item.content_type
            http_soap.serialization_type = item.serialization_type
            http_soap.timeout = item.timeout

            if connection == 'channel':
                http_soap.service_id = item.service_id
                http_soap.service_name = item.service_name
                http_soap.merge_url_params_req = item.merge_url_params_req
                http_soap.url_params_pri = item.url_params_pri
                http_soap.params_pri = item.params_pri

                match_slash = item.get('match_slash')
                if match_slash == '':
                    match_slash = True

                http_soap.match_slash = match_slash
                http_soap.http_accept = item.get('http_accept') or ''
            else:
                http_soap.ping_method = item.ping_method
                http_soap.pool_size = item.pool_size
                http_soap.validate_tls = item.get('validate_tls', True)

            for name in generic_attrs:
                setattr(http_soap, name, item.get(name))

            # The declarative invocation details are opaque attributes so they are absent
            # from connections that never set them.
            if connection == 'outgoing' and transport == URL_TYPE.PLAIN_HTTP:
                for name in _invocation_field_names:
                    setattr(http_soap, name, item.get(name))

                # The start date is stored in UTC and displayed in the user's own timezone and format
                if scheduler_start_date := http_soap.get('scheduler_start_date'):
                    http_soap.scheduler_start_date = from_utc_to_user(
                        scheduler_start_date + '+00:00', req.zato.user_profile)

            items.append(http_soap)

        meta = response.meta

    openapi_sample_data = ''
    if connection == 'outgoing' and transport == 'plain_http':
        openapi_dir = os.path.dirname(os.path.abspath(openapi_module.__file__))
        samples_dir = os.path.join(openapi_dir, 'samples')
        docusign_path = os.path.join(samples_dir, 'docusign-v2.yaml')
        with open(docusign_path, 'r', encoding='utf-8') as f:
            openapi_sample_data = f.read()

    internal_service_prefixes = ('zato.', 'pub.zato.', 'demo.', 'pubsub.')
    internal_services = sorted({
        item.service_name for item in items
        if getattr(item, 'service_name', None) and item.service_name.startswith(internal_service_prefixes)
    })

    return_data = {'zato_clusters':req.zato.clusters,
        'cluster_id':req.zato.cluster_id,
        'search_form':SearchForm(req.zato.clusters, req.GET),
        'items':items,
        'create_form':create_form,
        'edit_form':edit_form,
        'connection':connection,
        'transport':transport,
        'connection_label':CONNECTION[connection],
        'connection_label_plural':CONNECTION_PLURAL[connection],
        'transport_label':TRANSPORT[transport],
        'colspan': colspan,
        'default_http_ping_method':DEFAULT_HTTP_PING_METHOD,
        'default_http_pool_size':DEFAULT_HTTP_POOL_SIZE,
        'default_http_timeout':MISC.DEFAULT_HTTP_TIMEOUT,
        'paginate':True,
        'show_search_form':True,
        'meta': meta,
        'req':req,
        'openapi_sample_data': openapi_sample_data,
        'internal_services': internal_services,
        'gateway_trigger_service': Gateway_Trigger_Service,
        'zato_template_name': 'zato/http_soap/index.html',
        }

    # The scheduler tab's start date picker needs the user's date and time format
    return_data.update(get_js_dt_format(req.zato.user_profile))

    return TemplateResponse(req, 'zato/http_soap/index.html', return_data)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def create(req): # type: ignore
    try:
        msg_data = _get_edit_create_message(req.POST, user_profile=req.zato.user_profile)
        response = req.zato.client.invoke('zato.http-soap.create', msg_data)
        if response.has_data:
            return _edit_create_response(req, response.data.id, 'created',
                req.POST['transport'], req.POST['connection'], req.POST['name'])
        else:
            raise ZatoException(msg=response.details)
    except Exception:
        msg = 'Object could not be created, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def edit(req): # type: ignore
    try:
        edit_create_request = _get_edit_create_message(req.POST, 'edit-', user_profile=req.zato.user_profile)
        response = req.zato.client.invoke('zato.http-soap.edit', edit_create_request)
        if response.has_data:
            return _edit_create_response(req, response.data.id, 'updated',
                req.POST['transport'], req.POST['connection'], req.POST['edit-name'])
        else:
            raise ZatoException(msg=response.details)
    except Exception as e:
        msg = 'Update error: {}'.format(e.args[0])
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def delete(req, id, cluster_id): # type: ignore
    _ = id_only_service(req, 'zato.http-soap.delete', id, 'Object could not be deleted, e:`{}`')
    return HttpResponse()

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id): # type: ignore
    response = id_only_service(req, 'zato.http-soap.ping', id, 'Could not ping the connection, e:`{}`')

    if isinstance(response, HttpResponseServerError):
        err = response.content.decode('utf-8', 'replace')
        return JsonResponse({
            'is_success': False,
            'info': err,
        })

    data = response.data
    return JsonResponse({
        'is_success': data.is_success,
        'info': data.info,
    })

# ################################################################################################################################
# ################################################################################################################################

def _extract_invoke_params(req):
    return {
        'payload': req.POST.get('data-request', ''),
        'request_method': req.POST.get('request_method', 'POST'),
        'query_params': req.POST.get('query_params', ''),
        'path_params': req.POST.get('path_params', ''),
    }

# ################################################################################################################################

def _build_invoke_response(service_response):
    if service_response.ok:
        data = service_response.data
        response_body = data.response_body
        content_type = get_content_type(response_body)
        formatted_body = format_content(response_body, content_type)

        return JsonResponse({
            'data': formatted_body,
            'response_time_human': data.response_time,
            'content_type': content_type,
        })

    return JsonResponse({
        'data': str(service_response.details),
        'response_time_human': '',
        'content_type': 'text/plain',
    }, status=HTTPStatus.INTERNAL_SERVER_ERROR)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def invoke_channel(req, id):
    try:
        params = _extract_invoke_params(req)
        params['id'] = id
        response = req.zato.client.invoke('zato.http-soap.invoke-channel', params)
        return _build_invoke_response(response)
    except Exception as e:
        logger.error('invoke_channel error: %s', format_exc())
        return JsonResponse({'data': str(e), 'response_time_human': '', 'content_type': 'text/plain'}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def invoke_outconn(req, id):
    try:
        params = _extract_invoke_params(req)
        params['id'] = id
        response = req.zato.client.invoke('zato.http-soap.invoke-outconn', params)
        return _build_invoke_response(response)
    except Exception as e:
        logger.error('invoke_outconn error: %s', format_exc())
        return JsonResponse({'data': str(e), 'response_time_human': '', 'content_type': 'text/plain'}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def rate_limiting(req, id): # type: ignore
    response = req.zato.client.invoke('zato.http-soap.get', {
        'cluster_id': req.zato.cluster_id,
        'id': id,
    })

    rules_response = req.zato.client.invoke('zato.http-soap.rate-limiting.get', {
        'id': id,
    })

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'channel_id': id,
        'channel_name': response.data.name,
        'channel_url_path': response.data.url_path,
        'transport': response.data.transport,
        'rules_json': dumps(rules_response.data.rate_limiting),
        'zato_template_name': 'zato/http_soap/rate-limiting.html',
    }

    return TemplateResponse(req, 'zato/http_soap/rate-limiting.html', return_data)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def rate_limiting_save(req, id): # type: ignore
    try:
        rules_json = req.POST['rules_json']
        logger.info('rate_limiting_save; channel_id:%s, rules_json:%s', id, rules_json)
        response = req.zato.client.invoke('zato.http-soap.rate-limiting.save', {
            'id': id,
            'rules_json': rules_json,
        })
        logger.info('rate_limiting_save; channel_id:%s, response.ok:%s', id, response.ok)
        if response.ok:
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'error', 'message': response.details}, status=HTTPStatus.BAD_REQUEST)
    except Exception:
        msg = 'Rate limiting rules could not be saved, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################
# ################################################################################################################################

def rate_limiting_clear_counters(req, id): # type: ignore
    try:
        rule_index = req.POST['rule_index']
        response = req.zato.client.invoke('zato.http-soap.rate-limiting.clear-counters', {
            'id': id,
            'rule_index': rule_index,
        })
        if response.ok:
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'error', 'message': response.details}, status=HTTPStatus.BAD_REQUEST)
    except Exception:
        msg = 'Rate limiting counters could not be cleared, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################
# ################################################################################################################################
