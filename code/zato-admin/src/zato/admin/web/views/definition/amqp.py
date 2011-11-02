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
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import RequestContext

# lxml
from lxml import etree
from lxml.objectify import Element

# Validate
from validate import is_boolean

# anyjson
from anyjson import dumps

# Zato
from zato.admin.web import invoke_admin_service
from zato.admin.web.views import change_password as _change_password
from zato.admin.web.forms import ChangePasswordForm, ChooseClusterForm
from zato.admin.web.forms.definition.amqp import CreateForm, EditForm
from zato.admin.web.views import meth_allowed
from zato.common.odb.model import Cluster, ConnDef, ConnDefAMQP
from zato.common import zato_namespace, zato_path, ZatoException, ZATO_NOT_GIVEN
from zato.common.util import TRACE1, to_form

logger = logging.getLogger(__name__)

def _get_edit_create_message(params, prefix=''):
    """ Creates a base document which can be used by both 'edit' and 'create' actions.
    """
    zato_message = Element('{%s}zato_message' % zato_namespace)
    zato_message.data = Element('data')
    zato_message.data.id = params.get('id')
    zato_message.data.cluster_id = params['cluster_id']
    zato_message.data.name = params[prefix + 'name']
    zato_message.data.host = params[prefix + 'host']
    zato_message.data.port = params[prefix + 'port']
    zato_message.data.vhost = params[prefix + 'vhost']
    zato_message.data.username = params[prefix + 'username']
    zato_message.data.frame_max = params[prefix + 'frame_max']
    zato_message.data.heartbeat = bool(params.get(prefix + 'heartbeat'))

    return zato_message

def _edit_create_response(zato_message, action, name):
    return_data = {'id': zato_message.data.def_amqp.id.text,
                   'message': 'Successfully {0} the AMQP definition [{1}]'.format(action, name)}
    return HttpResponse(dumps(return_data), mimetype='application/javascript')

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
        
        _, zato_message, soap_response  = invoke_admin_service(cluster,
                'zato:definition.amqp.get-list', zato_message)
        
        if zato_path('data.definition_list.definition').get_from(zato_message) is not None:
            
            for definition_elem in zato_message.data.definition_list.definition:
                
                id = definition_elem.id.text
                name = definition_elem.name.text
                host = definition_elem.host.text
                port = definition_elem.port.text
                vhost = definition_elem.vhost.text
                username = definition_elem.username.text
                frame_max = definition_elem.frame_max.text
                heartbeat = is_boolean(definition_elem.heartbeat.text)
                
                def_ = ConnDef(None, name)
                def_amqp =  ConnDefAMQP(id, host, port, vhost, username, None, frame_max, heartbeat)
                def_amqp.def_ = def_
                
                items.append(def_amqp)
                

    return_data = {'zato_clusters':zato_clusters,
        'cluster_id':cluster_id,
        'choose_cluster_form':choose_cluster_form,
        'items':items,
        'create_form':create_form,
        'edit_form':edit_form,
        'change_password_form':change_password_form
        }
    
    # TODO: Should really be done by a decorator.
    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, 'Returning render_to_response [{0}]'.format(return_data))

    return render_to_response('zato/definition/amqp.html', return_data,
                              context_instance=RequestContext(req))

@meth_allowed('POST')
def create(req):
    
    cluster = req.odb.query(Cluster).filter_by(id=req.POST['cluster_id']).first()
    
    try:
        zato_message = _get_edit_create_message(req.POST)
        _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:definition.amqp.create', zato_message)

        return _edit_create_response(zato_message, 'created', req.POST['name'])        
        
    except Exception, e:
        msg = "Could not create an AMQP definition, e=[{e}]".format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)


@meth_allowed('GET')
def get_by_id(req, tech_account_id, cluster_id):
    
    try:
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.data = Element('data')
        zato_message.data.tech_account_id = tech_account_id
        
        cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()
        
        _, zato_message, soap_response = invoke_admin_service(cluster,
                        'zato:security.tech-account.get-by-id', zato_message)
        
    except Exception, e:
        msg = "Could not fetch the technical account, e=[{e}]".format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        tech_account = TechnicalAccount()
        tech_account_elem = zato_message.data.tech_account
        
        tech_account.id = tech_account_elem.id.text
        tech_account.name = tech_account_elem.name.text
        tech_account.is_active = is_boolean(tech_account_elem.is_active.text)

        return HttpResponse(tech_account.to_json(), mimetype='application/javascript')
    
@meth_allowed('POST')
def edit(req):
    
    prefix = 'edit-'

    cluster_id = req.POST['cluster_id']
    tech_account_id = req.POST['id']
    name = req.POST[prefix + 'name']
    is_active = req.POST.get(prefix + 'is_active')
    is_active = True if is_active else False
    
    cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()

    try:
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.data = Element('data')
        zato_message.data.cluster_id = cluster_id
        zato_message.data.tech_account_id = tech_account_id
        zato_message.data.name = name
        zato_message.data.is_active = is_active
        
        _, zato_message, soap_response = invoke_admin_service(cluster,
                        'zato:security.tech-account.edit', zato_message)
    
    except Exception, e:
        msg = "Could not update the technical account, e=[{e}]".format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        return _edit_create_response(zato_message, 'updated', name)

@meth_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato:security.tech-account.change-password')
    
@meth_allowed('POST')
def delete(req, id, cluster_id):
    
    cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()
    
    try:
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.data = Element('data')
        zato_message.data.id = id
        
        _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:definition.amqp.delete', zato_message)
        
        return HttpResponse()
    
    except Exception, e:
        msg = "Could not delete the account, e=[{e}]".format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)