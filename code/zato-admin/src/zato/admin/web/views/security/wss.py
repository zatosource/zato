# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

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
from json import dumps
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import RequestContext

# lxml
from lxml.objectify import Element

# Validate
from validate import is_boolean

# Zato
from zato.admin.web.forms import ChangePasswordForm, ChooseClusterForm
from zato.admin.web.forms.security.wss import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, meth_allowed
from zato.common import zato_namespace, zato_path, ZATO_WSS_PASSWORD_TYPES
from zato.admin.web import invoke_admin_service
from zato.common.odb.model import Cluster, WSSDefinition
from zato.common.util import TRACE1

logger = logging.getLogger(__name__)

def _edit_create_response(zato_message, action, name, password_type):
    return_data = {'id': zato_message.data.item.id.text,
        'message': 'Successfully {0} the WS-Security definition [{1}]'.format(action, name),
        'password_type_raw':password_type,
        'password_type':ZATO_WSS_PASSWORD_TYPES[password_type]}
    
    return HttpResponse(dumps(return_data), mimetype='application/javascript')

def _get_edit_create_message(params, prefix=''):
    """ Creates a base document which can be used by both 'edit' and 'create' actions.
    """
    zato_message = Element('{%s}zato_message' % zato_namespace)
    zato_message.data = Element('data')
    zato_message.data.id = params.get('id')
    zato_message.data.cluster_id = params['cluster_id']
    zato_message.data.name = params[prefix + 'name']
    zato_message.data.is_active = bool(params.get(prefix + 'is_active'))
    zato_message.data.username = params[prefix + 'username']
    zato_message.data.password_type = 'clear_text'
    zato_message.data.reject_empty_nonce_creat = bool(params.get(prefix + 'reject_empty_nonce_creat'))
    zato_message.data.reject_stale_tokens = bool(params.get(prefix + 'reject_stale_tokens'))
    zato_message.data.reject_expiry_limit = params[prefix + 'reject_expiry_limit']
    zato_message.data.nonce_freshness_time = params[prefix + 'nonce_freshness_time']

    return zato_message

@meth_allowed('GET')
def index(req):

    zato_clusters = req.odb.query(Cluster).order_by('name').all()
    choose_cluster_form = ChooseClusterForm(zato_clusters, req.GET)
    cluster_id = req.GET.get('cluster')
    items = []
    
    create_form = CreateForm()
    edit_form = EditForm(prefix='edit')
    change_password_form = ChangePasswordForm()

    if cluster_id and req.method == 'GET':
        cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()

        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.data = Element('data')
        zato_message.data.cluster_id = cluster_id

        _ignored, zato_message, soap_response  = invoke_admin_service(cluster,
                'zato:security.wss.get-list', zato_message)

        if zato_path('data.item_list.item').get_from(zato_message) is not None:
            for definition_elem in zato_message.data.item_list.item:

                id = definition_elem.id.text
                name = definition_elem.name.text
                is_active = is_boolean(definition_elem.is_active.text)
                username = definition_elem.username.text
                password_type = ZATO_WSS_PASSWORD_TYPES[definition_elem.password_type.text]
                password_type_raw = definition_elem.password_type.text
                reject_empty_nonce_creat = definition_elem.reject_empty_nonce_creat
                reject_stale_tokens = definition_elem.reject_stale_tokens
                reject_expiry_limit = definition_elem.reject_expiry_limit
                nonce_freshness_time = definition_elem.nonce_freshness_time

                wss = WSSDefinition(id, name, is_active, username, None,
                        password_type, reject_empty_nonce_creat, reject_stale_tokens,
                        reject_expiry_limit, nonce_freshness_time, password_type_raw=password_type_raw)

                items.append(wss)

    return_data = {'zato_clusters':zato_clusters,
        'cluster_id':cluster_id,
        'choose_cluster_form':choose_cluster_form,
        'items':items,
        'create_form': create_form,
        'edit_form': edit_form,
        'change_password_form': change_password_form
        }

    # TODO: Should really be done by a decorator.
    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, 'Returning render_to_response [%s]' % return_data)

    return render_to_response('zato/security/wss.html', return_data,
                              context_instance=RequestContext(req))

@meth_allowed('POST')
def edit(req):
    """ Updates WS-S definitions's parameters (everything except for the password).
    """
    try:
        cluster_id = req.POST.get('cluster_id')
        cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()
        zato_message = _get_edit_create_message(req.POST, prefix='edit-')

        _, zato_message, soap_response = invoke_admin_service(cluster,
                                    'zato:security.wss.edit', zato_message)

        return _edit_create_response(zato_message, 'updated', 
            req.POST['edit-name'], req.POST['edit-password_type'])
        
    except Exception, e:
        msg = "Could not update the WS-Security definition, e=[{e}]".format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

@meth_allowed('POST')
def create(req):
    try:
        cluster_id = req.POST.get('cluster_id')
        cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()

        zato_message = _get_edit_create_message(req.POST)

        _, zato_message, soap_response = invoke_admin_service(cluster,
                            'zato:security.wss.create', zato_message)

        return _edit_create_response(zato_message, 'created', 
            req.POST['name'], req.POST['password_type'])
        
    except Exception, e:
        msg = "Could not create a WS-Security definition, e=[{e}]".format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

    
@meth_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato:security.wss.change-password')

@meth_allowed('POST')
def delete(req, wss_id, cluster_id):
    
    cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()
    
    try:
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.data = Element('data')
        zato_message.data.wss_id = wss_id
        
        _, zato_message, soap_response = invoke_admin_service(cluster,
                        'zato:security.wss.delete', zato_message)
    
    except Exception, e:
        msg = "Could not delete the WS-Security definition, e=[{e}]".format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        return HttpResponse()