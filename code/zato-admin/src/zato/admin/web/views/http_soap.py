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
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template.response import TemplateResponse

# Validate
from validate import is_boolean

# anyjson
from anyjson import dumps

# Zato
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms.http_soap import ChooseClusterForm, CreateForm, EditForm
from zato.admin.web.views import meth_allowed
from zato.common import SECURITY_TYPES, URL_TYPE, ZATO_NONE, zato_path
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

def _get_security_list(cluster):
    zato_message, _  = invoke_admin_service(cluster, 'zato.security.get-list', {'cluster_id': cluster.id})
    return zato_message

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
        'method': params.get(prefix + 'method'),
        'soap_action': params.get(prefix + 'soap_action', ''),
        'soap_version': params.get(prefix + 'soap_version', ''),
        'data_format': params.get(prefix + 'data_format', None),
        'service': params.get(prefix + 'service'),
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

@meth_allowed('GET')
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
        security_list = _get_security_list(req.zato.cluster)
        if zato_path('item_list.item').get_from(security_list) is not None:
            for def_item in security_list.item_list.item:
                
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
        
        create_form = CreateForm(_security)
        edit_form = EditForm(_security, prefix='edit')
    
        input_dict = {
            'cluster_id': req.zato.cluster_id,
            'connection': connection,
            'transport': transport,
        }
        zato_message, soap_response = invoke_admin_service(req.zato.cluster, 'zato.http-soap.get-list', input_dict)
    
        if zato_path('item_list.item').get_from(zato_message) is not None:
            for msg_item in zato_message.item_list.item:
                id = msg_item.id.text
                name = msg_item.name.text
                is_active = is_boolean(msg_item.is_active.text)
                is_internal = is_boolean(msg_item.is_internal.text)
                host = msg_item.host.text
                url_path = msg_item.url_path.text
                method = msg_item.method.text if msg_item.method else ''
                soap_action = msg_item.soap_action.text if msg_item.soap_action else ''
                soap_version = msg_item.soap_version.text if msg_item.soap_version else ''
                data_format = msg_item.data_format.text if msg_item.data_format else ''
                service_id = msg_item.service_id.text
                service_name = msg_item.service_name.text
                sec_type = msg_item.sec_type.text
                
                _security_name = msg_item.security_name.text
                if _security_name:
                    security_name = '{0}<br/>{1}'.format(SECURITY_TYPES[sec_type], _security_name)
                else:
                    security_name = 'No security'
                
                _security_id = msg_item.security_id.text
                if _security_id:
                    security_id = '{0}/{1}'.format(sec_type, _security_id)
                else:
                    security_id = ZATO_NONE
                
                item = HTTPSOAP(id, name, is_active, is_internal, connection, 
                        transport, host, url_path, method, soap_action, soap_version, 
                        data_format, service_id=service_id, service_name=service_name,
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
        'colspan': colspan
        }

    return TemplateResponse(req, 'zato/http_soap.html', return_data)

@meth_allowed('POST')
def create(req):
    try:
        zato_message, soap_response = invoke_admin_service(req.zato.cluster, 'zato.http-soap.create', _get_edit_create_message(req.POST))
        return _edit_create_response(zato_message.item.id.text, 'created',
            req.POST['transport'], req.POST['connection'], req.POST['name'])
    except Exception, e:
        msg = 'Could not create the object, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)


@meth_allowed('POST')
def edit(req):
    try:
        zato_message, soap_response = invoke_admin_service(req.zato.cluster, 'zato.http-soap.edit', _get_edit_create_message(req.POST, 'edit-'))
        return _edit_create_response(zato_message.item.id.text, 'updated',
            req.POST['transport'], req.POST['connection'], req.POST['edit-name'])
    except Exception, e:
        msg = 'Could not perform the update, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

def _delete_ping(req, id, cluster_id, service, error_template):
    try:
        zato_message, soap_response = invoke_admin_service(req.zato.cluster, service, {'id': id})
        return zato_message
    except Exception, e:
        msg = error_template.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

@meth_allowed('POST')
def delete(req, id, cluster_id):
    _delete_ping(req, id, cluster_id, 'zato.http-soap.delete', 'Could not delete the object, e:[{e}]')
    return HttpResponse()

@meth_allowed('POST')
def ping(req, id, cluster_id):
    ret = _delete_ping(req, id, cluster_id, 'zato.http-soap.ping', 'Could not ping the connection, e:[{e}]')
    if isinstance(ret, HttpResponseServerError):
        return ret
    return HttpResponse(ret.response.item.info.text)
