# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template.response import TemplateResponse

# anyjson
from anyjson import dumps

# Zato
from zato.admin.web.forms.http_soap import ChooseClusterForm, CreateForm, EditForm
from zato.admin.web.views import method_allowed
from zato.common import DEFAULT_HTTP_PING_METHOD, DEFAULT_HTTP_POOL_SIZE, \
     PARAMS_PRIORITY, SECURITY_TYPES, SOAP_CHANNEL_VERSIONS, SOAP_VERSIONS, \
     URL_PARAMS_PRIORITY, URL_TYPE, ZatoException, ZATO_NONE
from zato.common.odb.model import HTTPSOAP
from zato.common.util import security_def_type as _security_def_type

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
    security = params[prefix + 'security']
    if security != ZATO_NONE:
        _, security_id = security.split('/')
    else:
        _, security_id = ZATO_NONE, ZATO_NONE
    
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
        '': bool(params.get(prefix + 'merge_url_params_req')),
        'url_params_pri': params.get(prefix + 'url_params_pri', URL_PARAMS_PRIORITY.DEFAULT),
        'params_pri': params.get(prefix + 'params_pri', PARAMS_PRIORITY.DEFAULT),
        'method': params.get(prefix + 'method'),
        'soap_action': params.get(prefix + 'soap_action', ''),
        'soap_version': params.get(prefix + 'soap_version', ''),
        'data_format': params.get(prefix + 'data_format', None),
        'service': params.get(prefix + 'service'),
        'ping_method': params.get(prefix + 'ping_method'),
        'pool_size': params.get(prefix + 'pool_size'),
        'security_id': security_id,
    }

def _edit_create_response(id, verb, transport, connection, name):

    return_data = {'id': id,
                   'transport': transport,
                   'message': 'Successfully {0} the {1} {2} [{3}]'.format(
                       verb,
                       TRANSPORT[transport],
                       CONNECTION[connection],
                       name),
                }

    return HttpResponse(dumps(return_data), mimetype='application/javascript')

@method_allowed('GET')
def index(req):
    connection = req.GET.get('connection')
    transport = req.GET.get('transport')
    items = []
    _security = []

    if not all((connection, transport)):
        log_msg = "Redirecting to / because at least one of ('connection', 'transport') GET parameters was missing"
        logger.debug(log_msg)
        return HttpResponseRedirect('/')
    
    create_form = None
    edit_form = None

    colspan = 14
    
    if transport == 'soap':
        colspan += 2

    if req.zato.cluster_id:
        for def_item in req.zato.client.invoke('zato.security.get-list', {'cluster_id': req.zato.cluster.id}):
            # Outgoing plain HTTP connections may use HTTP Basic Auth only,
            # outgoing SOAP connections may use either WSS or HTTP Basic Auth.
            if connection == 'outgoing':
                if transport == URL_TYPE.PLAIN_HTTP and def_item.sec_type != _security_def_type.basic_auth:
                    continue
                elif transport == URL_TYPE.SOAP and def_item.sec_type \
                     not in(_security_def_type.basic_auth, _security_def_type.wss):
                    continue
            
            value = '{0}/{1}'.format(def_item.sec_type, def_item.id)
            label = '{0}/{1}'.format(SECURITY_TYPES[def_item.sec_type], def_item.name)
            _security.append((value, label))

        _soap_versions = SOAP_CHANNEL_VERSIONS if connection == 'channel' else SOAP_VERSIONS
        
        create_form = CreateForm(_security, _soap_versions)
        edit_form = EditForm(_security, _soap_versions, prefix='edit')
    
        input_dict = {
            'cluster_id': req.zato.cluster_id,
            'connection': connection,
            'transport': transport,
        }
        for item in req.zato.client.invoke('zato.http-soap.get-list', input_dict):

            _security_name = item.security_name
            if _security_name:
                security_name = '{0}<br/>{1}'.format(SECURITY_TYPES[item.sec_type], _security_name)
            else:
                security_name = 'No security'
            
            _security_id = item.security_id
            if _security_id:
                security_id = '{0}/{1}'.format(item.sec_type, _security_id)
            else:
                security_id = ZATO_NONE
            
            item = HTTPSOAP(item.id, item.name, item.is_active, item.is_internal, connection, 
                    transport, item.host, item.url_path, item.method, item.soap_action,
                    item.soap_version, item.data_format, item.ping_method, 
                    item.pool_size, item.merge_url_params_req, item.url_params_pri, item.params_pri, 
                    service_id=item.service_id, service_name=item.service_name,
                    security_id=security_id, security_name=security_name)
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
        }

    return TemplateResponse(req, 'zato/http_soap.html', return_data)

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

def _delete_ping(req, service, id, error_template):
    try:
        return req.zato.client.invoke(service, {'id': id})
    except Exception, e:
        msg = error_template.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

@method_allowed('POST')
def delete(req, id, cluster_id):
    _delete_ping(req, 'zato.http-soap.delete', id, 'Could not delete the object, e:[{e}]')
    return HttpResponse()

@method_allowed('POST')
def ping(req, id, cluster_id):
    ret = _delete_ping(req, 'zato.http-soap.ping', id, 'Could not ping the connection, e:[{e}]')
    if isinstance(ret, HttpResponseServerError):
        return ret
    return HttpResponse(ret.data.info)
