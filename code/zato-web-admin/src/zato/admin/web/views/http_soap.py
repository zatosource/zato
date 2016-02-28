# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from cStringIO import StringIO
from pprint import pprint
from traceback import format_exc

# anyjson
from anyjson import dumps, loads

# Django
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template.response import TemplateResponse

# Paste
from paste.util.converters import asbool

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.forms.http_soap import AuditLogEntryList, ChooseClusterForm, CreateForm, EditForm, ReplacePatternsForm
from zato.admin.web.views import get_js_dt_format, get_security_id_from_select, get_tls_ca_cert_list, method_allowed, \
     id_only_service, SecurityList
from zato.common import BATCH_DEFAULTS, DEFAULT_HTTP_PING_METHOD, DEFAULT_HTTP_POOL_SIZE, HTTP_SOAP_SERIALIZATION_TYPE, \
     MSG_PATTERN_TYPE, PARAMS_PRIORITY, SEC_DEF_TYPE_NAME, SOAP_CHANNEL_VERSIONS, SOAP_VERSIONS, URL_PARAMS_PRIORITY, URL_TYPE, \
     ZatoException, ZATO_NONE
from zato.common import MISC, SEC_DEF_TYPE
from zato.common.odb.model import HTTPSOAP

logger = logging.getLogger(__name__)

CONNECTION = {
    'channel': 'channel',
    'outgoing': 'outgoing connection',
    }

CONNECTION_PLURAL = {
    'channel': 'channels',
    'outgoing': 'outgoing connections',
    }

TRANSPORT = {
    'plain_http': 'Plain HTTP',
    'soap': 'SOAP',
    }

def _get_edit_create_message(params, prefix=''):
    """ A bunch of attributes that can be used by both 'edit' and 'create' actions
    for channels and outgoing connections.
    """
    security_id = get_security_id_from_select(params, prefix)

    return {
        'is_internal': False,
        'connection': params['connection'],
        'transport': params['transport'],
        'id': params.get('id'),
        'cluster_id': params['cluster_id'],
        'name': params[prefix + 'name'],
        'is_active': bool(params.get(prefix + 'is_active')),
        'host': params.get(prefix + 'host'),
        'url_path': params[prefix + 'url_path'],
        'merge_url_params_req': bool(params.get(prefix + 'merge_url_params_req')),
        'url_params_pri': params.get(prefix + 'url_params_pri', URL_PARAMS_PRIORITY.DEFAULT),
        'params_pri': params.get(prefix + 'params_pri', PARAMS_PRIORITY.DEFAULT),
        'serialization_type': params.get(prefix + 'serialization_type', HTTP_SOAP_SERIALIZATION_TYPE.DEFAULT.id),
        'method': params.get(prefix + 'method'),
        'soap_action': params.get(prefix + 'soap_action', ''),
        'soap_version': params.get(prefix + 'soap_version', None),
        'data_format': params.get(prefix + 'data_format', None),
        'service': params.get(prefix + 'service'),
        'ping_method': params.get(prefix + 'ping_method'),
        'pool_size': params.get(prefix + 'pool_size'),
        'timeout': params.get(prefix + 'timeout'),
        'sec_tls_ca_cert_id': params.get(prefix + 'sec_tls_ca_cert_id'),
        'security_id': security_id,
        'has_rbac': bool(params.get(prefix + 'has_rbac')),
    }

def _edit_create_response(id, verb, transport, connection, name):

    return_data = {'id': id,
                   'transport': transport,
                   'message': 'Successfully {0} the {1} {2} [{3}], check server logs for details'.format(
                       verb,
                       TRANSPORT[transport],
                       CONNECTION[connection],
                       name),
                }

    return HttpResponse(dumps(return_data), content_type='application/javascript')

@method_allowed('GET')
def index(req):
    connection = req.GET.get('connection')
    transport = req.GET.get('transport')
    items = []
    _security = SecurityList()

    if not all((connection, transport)):
        log_msg = "Redirecting to / because at least one of ('connection', 'transport') GET parameters was missing"
        logger.debug(log_msg)
        return HttpResponseRedirect('/')

    create_form = None
    edit_form = None

    colspan = 17

    if transport == 'soap':
        colspan += 2

    if req.zato.cluster_id:
        for def_item in req.zato.client.invoke('zato.security.get-list', {'cluster_id': req.zato.cluster.id}):
            if connection == 'outgoing':
                if transport == URL_TYPE.PLAIN_HTTP and def_item.sec_type not in (
                    SEC_DEF_TYPE.BASIC_AUTH, SEC_DEF_TYPE.TLS_KEY_CERT):
                    continue
                elif transport == URL_TYPE.SOAP and def_item.sec_type not in (
                    SEC_DEF_TYPE.BASIC_AUTH, SEC_DEF_TYPE.NTLM, SEC_DEF_TYPE.WSS):
                    continue

            _security.append(def_item)

        _soap_versions = SOAP_CHANNEL_VERSIONS if connection == 'channel' else SOAP_VERSIONS

        create_form = CreateForm(_security, get_tls_ca_cert_list(req.zato.client, req.zato.cluster), _soap_versions)
        edit_form = EditForm(_security, get_tls_ca_cert_list(req.zato.client, req.zato.cluster), _soap_versions, prefix='edit')

        input_dict = {
            'cluster_id': req.zato.cluster_id,
            'connection': connection,
            'transport': transport,
        }

        for item in req.zato.client.invoke('zato.http-soap.get-list', input_dict):

            _security_name = item.security_name
            if _security_name:
                security_name = '{0}<br/>{1}'.format(SEC_DEF_TYPE_NAME[item.sec_type], _security_name)
            else:
                security_name = 'No security definition'

            _security_id = item.security_id
            if _security_id:
                security_id = '{0}/{1}'.format(item.sec_type, _security_id)
            else:
                security_id = ZATO_NONE

            item = HTTPSOAP(item.id, item.name, item.is_active, item.is_internal, connection,
                    transport, item.host, item.url_path, item.method, item.soap_action,
                    item.soap_version, item.data_format, item.ping_method,
                    item.pool_size, item.merge_url_params_req, item.url_params_pri, item.params_pri,
                    item.serialization_type, item.timeout, item.sec_tls_ca_cert_id, service_id=item.service_id,
                    service_name=item.service_name, security_id=security_id, has_rbac=item.has_rbac,
                    security_name=security_name)
            items.append(item)

    return_data = {'zato_clusters':req.zato.clusters,
        'cluster_id':req.zato.cluster_id,
        'choose_cluster_form':ChooseClusterForm(req.zato.clusters, req.GET),
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
        }

    return TemplateResponse(req, 'zato/http_soap/index.html', return_data)

@method_allowed('POST')
def create(req):
    try:
        response = req.zato.client.invoke('zato.http-soap.create', _get_edit_create_message(req.POST))
        if response.has_data:
            return _edit_create_response(response.data.id, 'created',
                req.POST['transport'], req.POST['connection'], req.POST['name'])
        else:
            raise ZatoException(msg=response.details)
    except Exception, e:
        msg = 'Could not create the object, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

@method_allowed('POST')
def edit(req):
    try:
        response = req.zato.client.invoke('zato.http-soap.edit', _get_edit_create_message(req.POST, 'edit-'))
        if response.has_data:
            return _edit_create_response(response.data.id, 'updated',
                req.POST['transport'], req.POST['connection'], req.POST['edit-name'])
        else:
            raise ZatoException(msg=response.details)
    except Exception, e:
        msg = 'Could not perform the update, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

@method_allowed('POST')
def delete(req, id, cluster_id):
    id_only_service(req, 'zato.http-soap.delete', id, 'Could not delete the object, e:[{e}]')
    return HttpResponse()

@method_allowed('POST')
def ping(req, id, cluster_id):
    ret = id_only_service(req, 'zato.http-soap.ping', id, 'Could not ping the connection, e:[{e}]')
    if isinstance(ret, HttpResponseServerError):
        return ret
    return HttpResponse(ret.data.info)

@method_allowed('POST')
def reload_wsdl(req, id, cluster_id):
    ret = id_only_service(req, 'zato.http-soap.reload-wsdl', id, 'Could not reload the WSDL, e:[{e}]')
    if isinstance(ret, HttpResponseServerError):
        return ret
    return HttpResponse('WSDL reloaded, check server logs for details')

@method_allowed('GET')
def details(req, **kwargs):
    return_data = kwargs

    audit_config = req.zato.client.invoke('zato.http-soap.get-audit-config', {'id': kwargs['id']})
    return_data.update(audit_config.data)

    patterns_response = req.zato.client.invoke('zato.http-soap.get-audit-replace-patterns', {'id': kwargs['id']})

    if audit_config.data.audit_repl_patt_type == MSG_PATTERN_TYPE.JSON_POINTER.id:
        pattern_list = patterns_response.data.patterns_json_pointer
    else:
        pattern_list = patterns_response.data.patterns_xpath

    return_data['pattern_list'] = '\n'.join(pattern_list)
    return_data['replace_patterns_form'] = ReplacePatternsForm(initial=return_data)

    return TemplateResponse(req, 'zato/http_soap/details.html', return_data)

@method_allowed('POST')
def audit_set_state(req, **kwargs):
    try:
        request = {'id':kwargs['id'], 'audit_enabled': not asbool(req.POST['audit_enabled'])}

        response = req.zato.client.invoke('zato.http-soap.set-audit-state', request)
        if not response.ok:
            raise Exception(response.details)

        return HttpResponse('OK')
    except Exception, e:
        msg = format_exc(e)
        logger.error(msg)
        return HttpResponseServerError(msg)

@method_allowed('POST')
def audit_set_config(req, **kwargs):
    try:
        args = {
            'id':kwargs['id'],
            'pattern_list': req.POST['pattern_list'].splitlines(),
            'audit_repl_patt_type': req.POST['audit_repl_patt_type'],
            'audit_max_payload': req.POST['audit_max_payload'],
        }

        calls = (
            ('zato.http-soap.set-audit-replace-patterns', ('id', 'pattern_list', 'audit_repl_patt_type')),
            ('zato.http-soap.set-audit-config', ('id', 'audit_max_payload')),
        )

        for service_name, keys in calls:
            request = {key: args[key] for key in keys}
            response = req.zato.client.invoke(service_name, request)
            if not response.ok:
                raise Exception(response.details)

        return HttpResponse('OK')
    except Exception, e:
        msg = format_exc(e)
        logger.error(msg)
        return HttpResponseServerError(msg)

@method_allowed('GET')
def audit_log(req, **kwargs):
    out = kwargs
    out['req'] = req

    out.update(get_js_dt_format(req.zato.user_profile))

    for key in('batch_size', 'current_batch', 'start', 'stop', 'state', 'query'):
        value = req.GET.get(key)
        if value:
            out[key] = value

    out['form'] = AuditLogEntryList(initial=out)

    request = {
        'conn_id': out['conn_id'],
        'start': out.get('start', ''),
        'stop': out.get('stop'),
        'current_batch': out.get('current_batch', BATCH_DEFAULTS.PAGE_NO),
        'batch_size': out.get('batch_size', BATCH_DEFAULTS.SIZE),
        'query': out.get('query', ''),
    }

    out['items'] = []

    response = req.zato.client.invoke('zato.http-soap.get-audit-item-list', request)
    if response.ok:
        for item in response.data:
            item.req_time = from_utc_to_user(item.req_time_utc+'+00:00', req.zato.user_profile)
            item.resp_time = from_utc_to_user(item.resp_time_utc+'+00:00', req.zato.user_profile) if item.resp_time_utc else '(None)'
            out['items'].append(item)

    out.update(**req.zato.client.invoke('zato.http-soap.get-audit-batch-info', request).data)

    return TemplateResponse(req, 'zato/http_soap/audit/log.html', out)

@method_allowed('GET')
def audit_item(req, **kwargs):
    try:
        out = kwargs
        response = req.zato.client.invoke('zato.http-soap.get-audit-item', {'id':kwargs['id']})
        if response.ok:
            out.update(**response.data)

            for name in('req', 'resp'):
                headers = '{}_headers'.format(name)
                if out.get(headers):
                    buff = StringIO()
                    pprint(loads(out[headers]), buff, width=160)
                    out['{}_pp'.format(headers)] = buff.getvalue()
                    buff.close()
        else:
            raise Exception(response.details)
        return TemplateResponse(req, 'zato/http_soap/audit/item.html', out)
    except Exception, e:
        msg = format_exc(e)
        logger.error(msg)
        return HttpResponseServerError(msg)
