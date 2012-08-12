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
from string import whitespace
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template import loader
from django.template.response import TemplateResponse

# anyjson
from anyjson import dumps

# Bunch
from bunch import Bunch

# Zato
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms.cluster import CreateClusterForm, DeleteClusterForm, EditClusterForm, EditServerForm
from zato.admin.web.views import Delete as _Delete, get_lb_client, meth_allowed, set_servers_state
from zato.admin.settings import DATABASE_ENGINE, DATABASE_HOST, DATABASE_NAME, DATABASE_PORT, \
     DATABASE_USER, sqlalchemy_django_engine
from zato.common import SERVER_UP_STATUS
from zato.common.odb.model import Cluster, Server

logger = logging.getLogger(__name__)

def _edit_create_response(item, verb):
    if item.lb_config:
        has_lb_config = True
        addresses = loader.render_to_string('zato/cluster/addresses.html', {'item':item})
    else:
        has_lb_config = False
        addresses = ''

    return_data = {
        'id': item.id,
        'message': 'Successfully {0} the cluster [{1}]'.format(verb, item.name),
        'addresses': addresses,
        'has_lb_config': has_lb_config
        }
    return HttpResponse(dumps(return_data), mimetype='application/javascript')

def _create_edit(req, verb, item, form_class, prefix=''):

    join = '-' if prefix else ''

    try:
        for s in whitespace:
            if s in req.POST[prefix + join + 'name']:
                return HttpResponseServerError('Cluster name must not contain whitespace.')

        description = req.POST[prefix + join + 'description'].strip()
        description = description if description else None

        item.name = req.POST[prefix + join + 'name'].strip()
        item.description = description
        item.odb_type = req.POST[prefix + join + 'odb_type'].strip()
        item.odb_host = req.POST[prefix + join + 'odb_host'].strip()
        item.odb_port = req.POST[prefix + join + 'odb_port'].strip()
        item.odb_user = req.POST[prefix + join + 'odb_user'].strip()
        item.odb_db_name = req.POST[prefix + join + 'odb_db_name'].strip()
        item.odb_schema = req.POST[prefix + join + 'odb_schema'].strip()
        item.lb_host = req.POST[prefix + join + 'lb_host'].strip()
        item.lb_port = req.POST[prefix + join + 'lb_port'].strip()
        item.lb_agent_port = req.POST[prefix + join + 'lb_agent_port'].strip()
        item.broker_host = req.POST[prefix + join + 'broker_host'].strip()
        item.broker_start_port = req.POST[prefix + join + 'broker_start_port'].strip()
        item.broker_token = req.POST[prefix + join + 'broker_token'].strip()

        try:
            req.zato.odb.add(item)
            req.zato.odb.commit()
            
            try:
                item.lb_config = get_lb_client(item).get_config()
            except Exception, e:
                item.lb_config = None
                msg = "Exception caught while fetching the load balancer's config, e:[{0}]".format(format_exc(e))
                logger.error(msg)                    
            
            return _edit_create_response(item, verb)
        
        except Exception, e:
            msg = 'Exception caught, e:[{0}]'.format(format_exc(e))
            logger.error(msg)

            return HttpResponseServerError(msg)

    except Exception, e:
        req.zato.odb.rollback()
        return HttpResponseServerError(str(format_exc(e)))

def _get_server_data(client, server_name):
    """ Gets the server's state as seen by the load balancer.
    """
    lb_server_data = client.get_server_data_dict(server_name)
    if lb_server_data:
        in_lb = True
        state = lb_server_data[server_name]['state']
        lb_address = lb_server_data[server_name]['address']
    else:
        in_lb = False
        state = '(unknown)'
        lb_address = '(unknown)'
        
    return Bunch({
        'in_lb': in_lb,
        'state': state,
        'lb_address': lb_address,
        })

def _common_edit_message(client, success_msg, id, name, host, up_status, up_mod_date, cluster_id):
    """ Returns a common JSON message for both the actual 'edit' and 'add/remove to/from LB' actions.
    """
    lb_server_data = _get_server_data(client, name)
    
    return_data = {
        'id': id,
        'name': name,

        'host': host if host else '(unknown)',
        'up_status': up_status if up_status else '(unknown)',
        'up_mod_date': up_mod_date.isoformat() if up_mod_date else '(unknown)',
        'cluster_id': cluster_id if cluster_id else '',

        'lb_state': lb_server_data.state,
        'lb_address': lb_server_data.lb_address,
        'in_lb': lb_server_data.in_lb,
        'message': success_msg.format(name),
    }
    return HttpResponse(dumps(return_data), mimetype='application/javascript')


@meth_allowed('GET')
def index(req):

    initial = {}
    initial['odb_type'] = sqlalchemy_django_engine[DATABASE_ENGINE]
    initial['odb_host'] = DATABASE_HOST
    initial['odb_port'] = DATABASE_PORT
    initial['odb_user'] = DATABASE_USER
    initial['odb_db_name'] = DATABASE_NAME

    create_form = CreateClusterForm(initial=initial)
    delete_form = DeleteClusterForm(prefix='delete')

    items = req.zato.odb.query(Cluster).order_by('name').all()
    for item in items:
        client = get_lb_client(item)

        try:
            lb_config = client.get_config()
            item.lb_config = lb_config

            # Assign the flags indicating whether servers are DOWN or in the MAINT mode.
            set_servers_state(item, client)

        except Exception, e:
            msg = 'Could not invoke agent, client:[{client!r}], e:[{e}]'.format(client=client,
                                                                e=format_exc(e))
            logger.error(msg)
            item.lb_config = None

    return_data = {'create_form':create_form, 'delete_form':delete_form,
                   'edit_form':EditClusterForm(prefix='edit'), 'items':items}

    return TemplateResponse(req, 'zato/cluster/index.html', return_data)

@meth_allowed('POST')
def create(req):
    return _create_edit(req, 'created', Cluster(), CreateClusterForm)

@meth_allowed('POST')
def edit(req):
    return _create_edit(req, 'updated', 
        req.zato.odb.query(Cluster).filter_by(id=req.POST['id']).one(), EditClusterForm, 'edit')

def _get(req, **filter):
    cluster = req.zato.odb.query(Cluster).filter_by(**filter).one()
    return HttpResponse(cluster.to_json(), mimetype='application/javascript')

@meth_allowed('GET')
def get_by_id(req, cluster_id):
    return _get(req, id=cluster_id)

@meth_allowed('GET')
def get_by_name(req, cluster_name):
    return _get(req, name=cluster_name)

@meth_allowed('GET')
def get_servers_state(req, cluster_id):
    cluster = req.zato.odb.query(Cluster).filter_by(id=cluster_id).one()
    client = get_lb_client(cluster)

    # Assign the flags indicating whether servers are DOWN or in the MAINT mode.
    try:
        set_servers_state(cluster, client)
    except Exception, e:
        msg = "Failed to invoke the load-balancer's agent and set the state of servers, e:[{e}]".format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

    return TemplateResponse(req, 'zato/cluster/servers_state.html', {'cluster':cluster})

@meth_allowed('POST')
def delete(req, cluster_id):
    """ Deletes a cluster *permanently*.
    """
    try:
        cluster = req.zato.odb.query(Cluster).filter_by(id=cluster_id).one()

        req.zato.odb.delete(cluster)
        req.zato.odb.commit()

    except Exception, e:
        msg = 'Could not delete the cluster, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        return HttpResponse()
    
@meth_allowed('GET')
def servers(req):
    """ A view for server management.
    """
    items = req.zato.odb.query(Server).order_by('name').all()
    
    try:
        client = get_lb_client(req.zato.get('cluster'))
        server_data_dict = client.get_server_data_dict()
        bck_http_plain = client.get_config()['backend']['bck_http_plain']
        lb_client_invoked = True
    except Exception, e:
        lb_client_invoked = False
    
    if lb_client_invoked:
        def _update_item(server_name, lb_address, lb_state):
            for item in items:
                if item.name == server_name:
                    item.in_lb = True
                    item.lb_address = lb_address
                    item.lb_state = lb_state
                    if item.up_status == SERVER_UP_STATUS.RUNNING:
                        item.may_be_deleted = False
                    else:
                        item.may_be_deleted = True
        
        for server_name in bck_http_plain:
            lb_address = '{}:{}'.format(bck_http_plain[server_name]['address'], bck_http_plain[server_name]['port'])
            _update_item(server_name, lb_address, server_data_dict[server_name]['state'])
    
    return_data = {
        'items':items,
        'choose_cluster_form':req.zato.choose_cluster_form,
        'zato_clusters':req.zato.clusters,
        'cluster':req.zato.get('cluster'),
        'edit_form':EditServerForm(prefix='edit')
    }
    
    return TemplateResponse(req, 'zato/cluster/servers.html', return_data)

@meth_allowed('POST')
def servers_edit(req):
    """ Updates a server in both ODB and the load balancer.
    """
    try:
        client = get_lb_client(req.zato.cluster)
        client.rename_server(req.POST['edit-old_name'], req.POST['edit-name'])

        zato_message, _ = invoke_admin_service(req.zato.cluster, 'zato:cluster.server.edit', 
            {'id':req.POST['id'], 'name':req.POST['edit-name']})
        
        msg_item = zato_message.response.item
        
        return _common_edit_message(client, 'Server [{}] updated', 
            msg_item.id.text, msg_item.name.text, msg_item.host.text,
            msg_item.up_status.text, msg_item.up_mod_date.text,
            msg_item.cluster_id.text if hasattr(msg_item, 'cluster_id') else '')
    
    except Exception, e:
        return HttpResponseServerError(format_exc(e))

@meth_allowed('POST')
def servers_add_remove_lb(req, action, server_id):
    """ Adds or removes a server from the load balancer's configuration.
    """
    server = req.zato.odb.query(Server).filter_by(id=server_id).one()
    
    client = get_lb_client(req.zato.cluster)
    client.add_remove_server(action, server.name)
    
    return _common_edit_message(client, 
        'Server [{{}}] {} the load balancer'.format('removed from' if action == 'remove' else 'added to'),
        server.id, server.name, server.host, server.up_status, server.up_mod_date,
        server.cluster_id)

class ServerDelete(_Delete):
    url_name = 'cluster-servers-delete'
    error_message = 'Could not delete the server'
    soap_action = 'zato:cluster.server.delete'
    
    def __call__(self, req, *args, **kwargs):
        zato_message, _ = invoke_admin_service(req.zato.cluster, 'zato:cluster.server.get-by-id', {'id':req.zato.id})

        client = get_lb_client(req.zato.cluster)
        client.add_remove_server('remove', zato_message.response.item.name.text)

        return super(ServerDelete, self).__call__(req, *args, **kwargs)
