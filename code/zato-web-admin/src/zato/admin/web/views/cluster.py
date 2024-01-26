# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from string import whitespace
from traceback import format_exc

# Bunch
from bunch import Bunch

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template import loader
from django.template.response import TemplateResponse

# pytz
from pytz import UTC

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.forms.cluster import DeleteClusterForm, EditClusterForm, EditServerForm
from zato.admin.web.views import Delete as _Delete, get_lb_client, method_allowed, set_servers_state
from zato.common.api import SERVER_UP_STATUS
from zato.common.json_internal import dumps
from zato.common.odb.model import Cluster, Server
from zato.common.util.platform_ import is_windows, is_non_windows

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

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

    return HttpResponse(dumps(return_data), content_type='application/javascript')

# ################################################################################################################################
# ################################################################################################################################

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

        item.lb_host = req.POST[prefix + join + 'lb_host'].strip()
        item.lb_port = req.POST[prefix + join + 'lb_port'].strip()
        item.lb_agent_port = req.POST[prefix + join + 'lb_agent_port'].strip()

        try:
            req.zato.odb.add(item)
            req.zato.odb.commit()

            try:
                item.lb_config = get_lb_client(item).get_config()
            except Exception:
                item.lb_config = None
                msg = "Exception caught while fetching the load balancer's config, e:`{}`".format(format_exc())
                logger.error(msg)

            return _edit_create_response(item, verb)

        except Exception:
            msg = 'Exception caught, e:`{}`'.format(format_exc())
            logger.error(msg)

            return HttpResponseServerError(msg)

    except Exception:
        req.zato.odb.rollback()
        return HttpResponseServerError(str(format_exc()))

# ################################################################################################################################
# ################################################################################################################################

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

# ################################################################################################################################
# ################################################################################################################################

def _common_edit_message(client, success_msg, id, name, host, up_status, up_mod_date, cluster_id, user_profile,
    fetch_lb_data=True):
    """ Returns a common JSON message for both the actual 'edit' and 'add/remove to/from LB' actions.
    """
    return_data = {
        'id': id,
        'name': name,

        'host': host if host else '(unknown)',
        'up_status': up_status if up_status else '(unknown)',
        'up_mod_date': from_utc_to_user(up_mod_date+'+00:00', user_profile) if up_mod_date else '(unknown)',
        'cluster_id': cluster_id if cluster_id else '',

        'lb_state': '(unknown)',
        'lb_address': '(unknown)',
        'in_lb': '(unknown)',
        'message': success_msg.format(name)
    }

    if fetch_lb_data:
        lb_server_data = _get_server_data(client, name)

        return_data.update({
            'lb_state': lb_server_data.state,
            'lb_address': lb_server_data.lb_address,
            'in_lb': lb_server_data.in_lb,
        })

    return HttpResponse(dumps(return_data), content_type='application/javascript')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req):

    delete_form = DeleteClusterForm(prefix='delete')
    items = req.zato.odb.query(Cluster).order_by(Cluster.name).all()

    for item in items:

        if is_non_windows:

            client = get_lb_client(item)

            try:
                lb_config = client.get_config()
                item.lb_config = lb_config

                # Assign the flags indicating whether servers are DOWN or in the MAINT mode.
                set_servers_state(item, client)

            except Exception:
                msg = 'Could not invoke agent, client:`{!r}`, e:`{}`'.format(client, format_exc())
                logger.error(msg)
                item.lb_config = None

    return_data = {
        'delete_form':delete_form,
        'edit_form':EditClusterForm(prefix='edit'),
        'items':items,
        'lb_use_tls': req.zato.lb_use_tls,
        'lb_tls_verify': req.zato.lb_tls_verify,
        'is_windows': is_windows,
    }

    return TemplateResponse(req, 'zato/cluster/index.html', return_data)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def edit(req):
    return _create_edit(req, 'updated',
        req.zato.odb.query(Cluster).filter_by(id=req.POST['id']).one(), EditClusterForm, 'edit')

# ################################################################################################################################
# ################################################################################################################################

def _get(req, **filter):
    cluster = req.zato.odb.query(Cluster).filter_by(**filter).one()
    return HttpResponse(cluster.to_json(), content_type='application/javascript')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_by_id(req, cluster_id):
    return _get(req, id=cluster_id)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_by_name(req, cluster_name):
    return _get(req, name=cluster_name)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_servers_state(req, cluster_id):
    cluster = req.zato.odb.query(Cluster).filter_by(id=cluster_id).one()
    client = get_lb_client(cluster)

    # Assign the flags indicating whether servers are DOWN or in the MAINT mode.
    try:
        set_servers_state(cluster, client)
    except Exception:
        msg = 'Failed to invoke the load-balancer\'s agent and set the state of servers, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

    return TemplateResponse(req, 'zato/cluster/servers_state.html', {'cluster':cluster})

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def delete(req, id):
    """ Deletes a cluster *permanently*.
    """
    try:
        cluster = req.zato.odb.query(Cluster).filter_by(id=id).one()

        req.zato.odb.delete(cluster)
        req.zato.odb.commit()

    except Exception:
        msg = 'Cluster could not be deleted, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        return HttpResponse()

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def servers(req):
    """ A view for server management.
    """
    items = req.zato.odb.query(Server).order_by(Server.name).all()

    for item in items:
        if item.up_mod_date:
            item.up_mod_date_user = from_utc_to_user(item.up_mod_date.replace(tzinfo=UTC).isoformat(), req.zato.user_profile)

    try:
        client = get_lb_client(req.zato.get('cluster'))
        server_data_dict = client.get_server_data_dict()
        bck_http_plain = client.get_config()['backend']['bck_http_plain']
        lb_client_invoked = True
    except Exception:
        logger.error(format_exc())
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
        'search_form':req.zato.search_form,
        'zato_clusters':req.zato.clusters,
        'cluster':req.zato.get('cluster'),
        'edit_form':EditServerForm(prefix='edit')
    }

    return TemplateResponse(req, 'zato/cluster/servers.html', return_data)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def servers_edit(req):
    """ Updates a server in both ODB and the load balancer.
    """
    try:
        client = get_lb_client(req.zato.cluster)

        server_id = req.POST['id']
        server = req.zato.odb.query(Server).filter_by(id=server_id).one()

        if client.get_server_data_dict(server.name):
            fetch_lb_data = True
            client.rename_server(req.POST['edit-old_name'], req.POST['edit-name'])
        else:
            fetch_lb_data = False

        response = req.zato.client.invoke('zato.server.edit', {'id':server_id, 'name':req.POST['edit-name']})

        return _common_edit_message(client, 'Server [{}] updated',
            response.data.id, response.data.name, response.data.host,
            response.data.up_status, response.data.up_mod_date,
            req.zato.cluster_id, req.zato.user_profile, fetch_lb_data)

    except Exception:
        return HttpResponseServerError(format_exc())

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def servers_add_remove_lb(req, action, server_id):
    """ Adds or removes a server from the load balancer's configuration.
    """
    server = req.zato.odb.query(Server).filter_by(id=server_id).one()
    up_mod_date = server.up_mod_date.isoformat() if server.up_mod_date else ''

    client = get_lb_client(req.zato.cluster)
    client.add_remove_server(action, server.name)

    if action == 'add':
        success_msg = 'added to'
        fetch_lb_data = True
    else:
        success_msg = 'removed from'
        fetch_lb_data = False

    return _common_edit_message(client,
        'Server [{{}}] {} the load balancer'.format(success_msg),
        server.id, server.name, server.host, server.up_status, up_mod_date,
        server.cluster_id, req.zato.user_profile, fetch_lb_data)

# ################################################################################################################################
# ################################################################################################################################

class ServerDelete(_Delete):
    url_name = 'cluster-servers-delete'
    error_message = 'Could not delete the server'
    service_name = 'zato.server.delete'

    def __call__(self, req, *args, **kwargs):
        response = req.zato.client.invoke('zato.server.get-by-id', {'id':req.zato.id})

        server = req.zato.odb.query(Server).filter_by(id=req.zato.id).one()

        client = get_lb_client(req.zato.cluster) # Checks whether the server is known by LB
        if client.get_server_data_dict(server.name):
            client.add_remove_server('remove', response.data.name)

        return super(ServerDelete, self).__call__(req, *args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################
