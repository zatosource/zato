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
from zato.admin.web import alerts_tab
from zato.admin.web.forms import add_http_soap_select, add_select_from_service
from zato.admin.web.forms.http_soap import SearchForm, CreateForm, EditForm
from zato.admin.web.views import get_group_list as common_get_group_list, get_http_channel_security_id, \
    get_js_dt_format, get_security_id_from_select, id_only_service, method_allowed, ping_json_response, SecurityList
from zato.admin.web.views.http_soap_message import fill_row_from_item, get_edit_create_message
from zato.common.alerting.object_config import get_alert_type
from zato.common.api import Groups, MISC, SEC_DEF_TYPE, Sec_Def_Type_Name, SOAP_CHANNEL_VERSIONS, URL_TYPE, ZATO_NONE
from zato.common.content_type import format_content, get_content_type
from zato.common.exception import ZatoException
from zato.common.json_internal import dumps, loads
from zato.common.typing_ import any_
from zato.common.util.api import asbool
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
    SEC_DEF_TYPE.MTLS,
    SEC_DEF_TYPE.NTLM,
    SEC_DEF_TYPE.OAUTH,
    SEC_DEF_TYPE.SPNEGO,
}

# Security types an outgoing connection uses to authenticate itself elsewhere - they verify
# nobody on the way in, so the server refuses them on a channel and the select does not offer them
_outgoing_only_security_types = {
    SEC_DEF_TYPE.NTLM,
    SEC_DEF_TYPE.SPNEGO,
}

# The flag a row of the listing turns over where it stands.
_inline_flag_names = ['is_active']

# Everything a row of the listing may change without the edit form being opened -
# the security definition and the security groups travel separately.
_inline_field_names = ['is_active', 'name', 'url_path', 'service']

# ################################################################################################################################
# ################################################################################################################################

def _format_security_groups_info(group_count:'int', group_member_count:'int') -> 'str':
    """ The counts of a channel's security groups and their members, worded the way the listing shows them.
    """
    if (group_count == 0) or (group_count > 1):
        group_count_suffix = 's'
    else:
        group_count_suffix = ''

    if (group_member_count == 0) or (group_member_count > 1):
        group_member_count_suffix = 's'
    else:
        group_member_count_suffix = ''

    out = f'{group_count} group{group_count_suffix}, {group_member_count} client{group_member_count_suffix}'
    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_security_href(cluster_id:'int', sec_type:'str', security_name:'str') -> 'str':
    """ Where the page of the security definition a row uses is found.
    """
    sec_type_as_link = sec_type.replace('_', '-')

    if sec_type == SEC_DEF_TYPE.OAUTH:
        direction = 'outconn/client-credentials/'
    else:
        direction = ''

    out = f'/zato/security/{sec_type_as_link}/{direction}?cluster={cluster_id}&query={security_name}'
    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_security_groups_info(req:'any_', id:'str') -> 'str':
    """ Counts the security groups assigned to a channel and their members, worded the way the listing shows them.
    """
    groups = common_get_group_list(req, Groups.Type.API_Clients, http_soap_channel_id=id)

    group_count = 0
    group_member_count = 0

    for item in groups:
        if item.is_assigned:
            group_count += 1
            group_member_count += item.member_count

    out = _format_security_groups_info(group_count, group_member_count)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _edit_create_response(req, id, verb, transport, connection, name): # type: ignore

    # The security cell of the row rebuilt by the listing renders the canonical name and href,
    # so the object is read anew and both are computed the way the listing computes them.
    response = req.zato.client.invoke('zato.http-soap.get', {
        'cluster_id': req.zato.cluster_id,
        'id': id,
    })
    updated = response.data

    # Connections without security carry no name at all here.
    if security_name := updated.get('security_name'):
        security_href = _get_security_href(req.zato.cluster_id, updated['sec_type'], security_name)
    else:
        security_name = ''
        security_href = ''

    return_data = {
        'id': id,
        'transport': transport,
        'message': 'Successfully {} {} {} `{}`'.format(verb, TRANSPORT[transport], CONNECTION[connection], name),
        'security_name': security_name,
        'security_href': security_href,
        'security_groups_info': _get_security_groups_info(req, id),
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

    # The alert type this page's rows carry settings under, empty for a page whose rows carry none
    alert_type = get_alert_type(connection, transport)

    if req.zato.cluster_id:
        for def_item in req.zato.client.invoke('zato.security.get-list', {'cluster_id': req.zato.cluster.id}):
            if connection == 'outgoing':
                if transport == URL_TYPE.PLAIN_HTTP and def_item.sec_type not in _rest_security_type_supported:
                    continue

            elif def_item.sec_type in _outgoing_only_security_types:
                continue

            _security.append(def_item)

        create_form = CreateForm(_security, SOAP_CHANNEL_VERSIONS, req=req, alert_type=alert_type)
        edit_form = EditForm(_security, SOAP_CHANNEL_VERSIONS, prefix='edit', req=req, alert_type=alert_type)

        if connection == 'outgoing':
            create_form.fields['url_path'].required = False
            edit_form.fields['url_path'].required = False

        # The callback tab lets outgoing REST connections deliver responses to other outgoing REST connections ..
        if connection == 'outgoing' and transport == URL_TYPE.PLAIN_HTTP:
            add_http_soap_select(create_form, 'callback_rest', req, 'outgoing', URL_TYPE.PLAIN_HTTP, by_id=False)
            add_http_soap_select(edit_form, 'callback_rest', req, 'outgoing', URL_TYPE.PLAIN_HTTP, by_id=False)

            # .. and to pub/sub topics, selected by name from the topics that currently exist.
            add_select_from_service(create_form, req, 'zato.pubsub.topic.get-list', 'callback_topic', by_id=False)
            add_select_from_service(edit_form, req, 'zato.pubsub.topic.get-list', 'callback_topic', by_id=False)

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
                security_href = _get_security_href(req.zato.cluster_id, item.sec_type, _security_name)
            else:
                _security_name = ''
                security_href = ''

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
            http_soap.security_name = _security_name
            http_soap.security_href = security_href
            http_soap.content_type = item.content_type
            http_soap.timeout = item.timeout

            if connection == 'channel':
                http_soap.service_id = item.service_id
                http_soap.service_name = item.service_name
                http_soap.merge_url_params_req = item.merge_url_params_req
                http_soap.url_params_pri = item.url_params_pri
                http_soap.params_pri = item.params_pri

                # Channels that never had groups assigned carry no counts at all
                group_count = item.get('security_group_count')
                group_member_count = item.get('security_group_member_count')

                if not group_count:
                    group_count = 0

                if not group_member_count:
                    group_member_count = 0

                http_soap.security_group_count = group_count
                http_soap.security_groups_info = _format_security_groups_info(group_count, group_member_count)

                match_slash = item.get('match_slash')
                if match_slash == '':
                    match_slash = True

                http_soap.match_slash = match_slash
                http_soap.http_accept = item.get('http_accept') or ''

                # The OpenAPI flag is an opaque attribute, so channels that predate it carry no value,
                # which means they are included in OpenAPI documents.
                should_include_in_openapi = item.get('should_include_in_openapi')
                if should_include_in_openapi is None:
                    should_include_in_openapi = True

                http_soap.should_include_in_openapi = should_include_in_openapi

                # The deprecation attributes are opaque ones too, so channels that predate them
                # carry no values, which means they are not deprecated.
                is_deprecated = item.get('is_deprecated')
                if is_deprecated is None:
                    is_deprecated = False

                http_soap.is_deprecated = is_deprecated
                http_soap.deprecation_sunset = item.get('deprecation_sunset', '')
                http_soap.deprecation_successor = item.get('deprecation_successor', '')
            else:
                http_soap.ping_method = item.ping_method
                http_soap.pool_size = item.pool_size
                http_soap.validate_tls = item.get('validate_tls', True)

            fill_row_from_item(http_soap, item, alert_type, connection, transport, req.zato.user_profile)

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
        'default_http_ping_method':MISC.DEFAULT_HTTP_PING_METHOD,
        'default_http_pool_size':MISC.DEFAULT_HTTP_POOL_SIZE,
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

    # REST and SOAP channels and outgoing REST connections carry the Alerts tab, the template asks this one flag,
    # and a channel's dialog gets a Main and Alerts strip of its own where an outgoing connection's has one already
    has_alerts_tab = bool(alert_type)
    return_data['has_alerts_tab'] = has_alerts_tab
    return_data['has_channel_tabs'] = has_alerts_tab and connection == 'channel'

    if has_alerts_tab:
        return_data['create_alerts_tab'] = alerts_tab.get_alerts_tab_context(create_form, alert_type)
        return_data['edit_alerts_tab'] = alerts_tab.get_alerts_tab_context(edit_form, alert_type)
        return_data['alerts_tab_config'] = alerts_tab.get_alerts_tab_config(alert_type)

    return TemplateResponse(req, 'zato/http_soap/index.html', return_data)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def create(req): # type: ignore
    try:
        msg_data = get_edit_create_message(req.POST, user_profile=req.zato.user_profile)
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
        edit_create_request = get_edit_create_message(req.POST, 'edit-', user_profile=req.zato.user_profile)
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
def inline_edit(req:'any_', id:'str') -> 'JsonResponse':
    """ Stores what the listing edited without leaving the page - only the fields posted change.
    """
    connection = req.POST['connection']
    transport = req.POST['transport']

    # Read the object as it currently stands - the edit service needs the full picture,
    # so the stored values travel along with the ones that changed ..
    response = req.zato.client.invoke('zato.http-soap.get', {
        'cluster_id': req.zato.cluster_id,
        'id': id,
    })

    if not response.ok:
        raise Exception(f'Object with id `{id}` could not be read')

    item_dict = response.data

    # .. the edit service reads these from its own input rather than from what the read returned ..
    item_dict['id'] = id
    item_dict['cluster_id'] = req.zato.cluster_id
    item_dict['connection'] = connection
    item_dict['transport'] = transport

    # .. the edit service knows a channel's service under this name ..
    if service_name := item_dict.get('service_name'):
        item_dict['service'] = service_name

    # .. a flag travels as the word it is written with, a text line as itself ..
    for name in _inline_field_names:
        if name in req.POST:
            value = req.POST[name]

            if name in _inline_flag_names:
                value = asbool(value)

            item_dict[name] = value

    # .. the security definition arrives as the composite value the security select uses ..
    if 'security' in req.POST:
        item_dict['security_id'] = get_security_id_from_select(req.POST, '')

    # .. the security groups arrive as one JSON list of their ids ..
    if 'security_groups' in req.POST:
        item_dict['security_groups'] = loads(req.POST['security_groups'])

    # .. and the object is saved with the merged values.
    response = req.zato.client.invoke('zato.http-soap.edit', item_dict)

    if not response.ok:
        raise Exception(f'Object with id `{id}` could not be saved -> {response.details}')

    # Read the object anew so the reply carries the canonical values the row renders.
    response = req.zato.client.invoke('zato.http-soap.get', {
        'cluster_id': req.zato.cluster_id,
        'id': id,
    })
    updated = response.data

    # Connections without security carry no name at all here.
    if security_name := updated.get('security_name'):
        security_href = _get_security_href(req.zato.cluster_id, updated['sec_type'], security_name)
        sec_type_name = Sec_Def_Type_Name[updated['sec_type']]
    else:
        security_name = ''
        security_href = ''
        sec_type_name = ''

    # The composite value the security select and the hidden security cell use.
    if security_id := updated.get('security_id'):
        security_id = f'{updated["sec_type"]}/{security_id}'
    else:
        security_id = ZATO_NONE

    # Only channels have security groups.
    if connection == 'channel':
        security_groups_info = _get_security_groups_info(req, id)
    else:
        security_groups_info = ''

    # Only channels have a service.
    if not (service_name := updated.get('service_name')):
        service_name = ''

    # What the row now says of itself.
    out = JsonResponse({
        'name': updated['name'],
        'url_path': updated['url_path'],
        'is_active': asbool(updated['is_active']),
        'service_name': service_name,
        'security_id': security_id,
        'security_name': security_name,
        'security_href': security_href,
        'sec_type_name': sec_type_name,
        'security_groups_info': security_groups_info,
    })

    return out

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
        return ping_json_response(False, err)

    data = response.data
    return ping_json_response(data.is_success, data.info)

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
