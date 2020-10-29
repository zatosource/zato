# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from operator import itemgetter
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms.http_soap import SearchForm, CreateForm, EditForm
from zato.admin.web.views import get_http_channel_security_id, get_security_id_from_select, get_tls_ca_cert_list, \
     id_only_service, method_allowed, parse_response_data, SecurityList
from zato.common.api import CACHE, DEFAULT_HTTP_PING_METHOD, DEFAULT_HTTP_POOL_SIZE, DELEGATED_TO_RBAC, \
     HTTP_SOAP_SERIALIZATION_TYPE, MISC, PARAMS_PRIORITY, SEC_DEF_TYPE, SEC_DEF_TYPE_NAME, SOAP_CHANNEL_VERSIONS, \
     SOAP_VERSIONS, URL_PARAMS_PRIORITY, URL_TYPE
from zato.common.exception import ZatoException
from zato.common.json_internal import dumps
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
    'plain_http': 'REST',
    'soap': 'SOAP',
    }

CACHE_TYPE = {
    CACHE.TYPE.BUILTIN: 'Built-in',
    CACHE.TYPE.MEMCACHED: 'Memcached',
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
        'match_slash': bool(params.get(prefix + 'match_slash')),
        'http_accept': params.get(prefix + 'http_accept'),
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
        'content_type': params.get(prefix + 'content_type'),
        'cache_id': params.get(prefix + 'cache_id'),
        'cache_expiry': params.get(prefix + 'cache_expiry'),
        'content_encoding': params.get(prefix + 'content_encoding'),
        'is_rate_limit_active': params.get(prefix + 'is_rate_limit_active'),
        'rate_limit_type': params.get(prefix + 'rate_limit_type'),
        'rate_limit_def': params.get(prefix + 'rate_limit_def'),
        'rate_limit_check_parent_def': params.get(prefix + 'rate_limit_check_parent_def'),
    }

def _edit_create_response(req, id, verb, transport, connection, name):

    return_data = {
        'id': id,
        'transport': transport,
        'message': 'Successfully {} the {} {} `{}`, check server logs for details'.format(
            verb, TRANSPORT[transport], CONNECTION[connection], name),
    }

    # If current item has a cache assigned, provide its human-friendly name to the caller
    response = req.zato.client.invoke('zato.http-soap.get', {
        'cluster_id': req.zato.cluster_id,
        'id': id,
    })

    if response.data.cache_id:
        cache_type = response.data.cache_type
        cache_name = '{}/{}'.format(CACHE_TYPE[cache_type], response.data.cache_name)
    else:
        cache_type = None
        cache_name = None

    return_data['cache_type'] = cache_type
    return_data['cache_name'] = cache_name

    return HttpResponse(dumps(return_data), content_type='application/javascript')

@method_allowed('GET')
def index(req):
    connection = req.GET.get('connection')
    transport = req.GET.get('transport')
    query = req.GET.get('query', '')
    items = []
    _security = SecurityList()

    if not all((connection, transport)):
        log_msg = "Redirecting to / because at least one of ('connection', 'transport') GET parameters was missing"
        logger.debug(log_msg)
        return HttpResponseRedirect('/')

    create_form = None
    edit_form = None
    meta = None

    colspan = 17

    if transport == 'soap':
        colspan += 2

    if req.zato.cluster_id:
        for def_item in req.zato.client.invoke('zato.security.get-list', {'cluster_id': req.zato.cluster.id}):
            if connection == 'outgoing':
                if transport == URL_TYPE.PLAIN_HTTP and def_item.sec_type not in (
                    SEC_DEF_TYPE.BASIC_AUTH, SEC_DEF_TYPE.TLS_KEY_CERT, SEC_DEF_TYPE.APIKEY):
                    continue
                elif transport == URL_TYPE.SOAP and def_item.sec_type not in (
                    SEC_DEF_TYPE.BASIC_AUTH, SEC_DEF_TYPE.NTLM, SEC_DEF_TYPE.WSS):
                    continue

            _security.append(def_item)

        _soap_versions = SOAP_CHANNEL_VERSIONS if connection == 'channel' else SOAP_VERSIONS

        tls_ca_cert_list = get_tls_ca_cert_list(req.zato.client, req.zato.cluster)

        cache_list = []

        for cache_type in (CACHE.TYPE.BUILTIN, CACHE.TYPE.MEMCACHED):
            service_name = 'zato.cache.{}.get-list'.format(cache_type)
            response = req.zato.client.invoke(service_name, {'cluster_id': req.zato.cluster.id})

            for item in sorted(response, key=itemgetter('name')):
                cache_list.append({'id':item.id, 'name':'{}/{}'.format(CACHE_TYPE[cache_type], item.name)})

        create_form = CreateForm(_security, tls_ca_cert_list, cache_list, _soap_versions, req=req)
        edit_form = EditForm(_security, tls_ca_cert_list, cache_list, _soap_versions, prefix='edit', req=req)

        input_dict = {
            'cluster_id': req.zato.cluster_id,
            'connection': connection,
            'transport': transport,
            'paginate': True,
            'cur_page': req.GET.get('cur_page', 1),
            'query': req.GET.get('query', ''),
        }

        data, meta = parse_response_data(req.zato.client.invoke('zato.http-soap.get-list', input_dict))

        for item in data:
            if query not in item.name:
                continue

            _security_name = item.security_name
            if _security_name:
                security_name = '{0}<br/>{1}'.format(SEC_DEF_TYPE_NAME[item.sec_type], _security_name)
            else:
                if item.sec_use_rbac:
                    security_name = DELEGATED_TO_RBAC
                else:
                    security_name = '<span class="form_hint">---</span>'

            security_id = get_http_channel_security_id(item)

            if item.cache_id:
                cache_name = '{}/{}'.format(CACHE_TYPE[item.cache_type], item.cache_name)
            else:
                cache_name = None

            # New in 3.0, hence optional
            match_slash = item.get('match_slash')
            if match_slash == '':
                match_slash = True

            # New in 3.1
            http_accept = item.get('http_accept') or ''

            http_soap = HTTPSOAP(item.id, item.name, item.is_active, item.is_internal, connection,
                    transport, item.host, item.url_path, item.method, item.soap_action,
                    item.soap_version, item.data_format, item.ping_method,
                    item.pool_size, item.merge_url_params_req, item.url_params_pri, item.params_pri,
                    item.serialization_type, item.timeout, item.sec_tls_ca_cert_id, service_id=item.service_id,
                    service_name=item.service_name, security_id=security_id, has_rbac=item.has_rbac,
                    security_name=security_name, content_type=item.content_type,
                    cache_id=item.cache_id, cache_name=cache_name, cache_type=item.cache_type, cache_expiry=item.cache_expiry,
                    content_encoding=item.content_encoding, match_slash=match_slash, http_accept=http_accept)

            for name in 'is_rate_limit_active', 'rate_limit_type', 'rate_limit_def', 'rate_limit_check_parent_def':
                setattr(http_soap, name, item.get(name))

            items.append(http_soap)

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
        'meta': meta,
        'req':req
        }

    return TemplateResponse(req, 'zato/http_soap/index.html', return_data)

@method_allowed('POST')
def create(req):
    try:
        response = req.zato.client.invoke('zato.http-soap.create', _get_edit_create_message(req.POST))
        if response.has_data:
            return _edit_create_response(req, response.data.id, 'created',
                req.POST['transport'], req.POST['connection'], req.POST['name'])
        else:
            raise ZatoException(msg=response.details)
    except Exception:
        msg = 'Object could not be created, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

@method_allowed('POST')
def edit(req):
    try:
        response = req.zato.client.invoke('zato.http-soap.edit', _get_edit_create_message(req.POST, 'edit-'))
        if response.has_data:
            return _edit_create_response(req, response.data.id, 'updated',
                req.POST['transport'], req.POST['connection'], req.POST['edit-name'])
        else:
            raise ZatoException(msg=response.details)
    except Exception:
        msg = 'Update error, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

@method_allowed('POST')
def delete(req, id, cluster_id):
    id_only_service(req, 'zato.http-soap.delete', id, 'Object could not be deleted, e:`{}`')
    return HttpResponse()

@method_allowed('POST')
def ping(req, id, cluster_id):
    response = id_only_service(req, 'zato.http-soap.ping', id, 'Could not ping the connection, e:`{}`')

    if isinstance(response, HttpResponseServerError):
        return response
    else:
        if response.data.is_success:
            return HttpResponse(response.data.info)
        else:
            return HttpResponseServerError(response.data.info)

@method_allowed('POST')
def reload_wsdl(req, id, cluster_id):
    ret = id_only_service(req, 'zato.http-soap.reload-wsdl', id, 'WSDL could not be reloaded, e:`{}`')
    if isinstance(ret, HttpResponseServerError):
        return ret
    return HttpResponse('WSDL reloaded, check server logs for details')
