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

# lxml
from lxml.objectify import Element

# Zato
from zato.admin.web import invoke_admin_service
from zato.common import zato_namespace
from zato.common.odb.model import Cluster

logger = logging.getLogger(__name__)

# Zato
from zato.admin.settings import ssl_key_file, ssl_cert_file, ssl_ca_certs, \
     LB_AGENT_CONNECT_TIMEOUT
from zato.common.util import get_lb_client as _get_lb_client

logger = logging.getLogger(__name__)

def get_lb_client(cluster):
    """ A convenience wrapper over the function for creating a load-balancer client
    which may use ZatoAdmin's SSL material (the client from zato.common can't use
    it because it would make it dependent on the zato.admin package).
    """
    return _get_lb_client(cluster.lb_host, cluster.lb_agent_port, ssl_ca_certs,
                          ssl_key_file, ssl_cert_file, LB_AGENT_CONNECT_TIMEOUT)

def meth_allowed(*meths):
    """ Accepts a list (possibly one-element long) of HTTP methods allowed
    for a given view. An exception will be raised if a request has been made
    with a method outside of those allowed, otherwise the view executes
    unchanged.
    TODO: Make it return a custom Exception so that whoever called us can catch
    catch it and return a correct HTTP status (405 Method not allowed).
    """
    def inner_meth_allowed(view):
        def inner_view(*args, **kwargs):
            req = args[0]
            if req.method not in meths:
                msg = "Method [{method}] is not allowed here [{view}], methods allowed=[{meths}]"
                msg = msg.format(method=req.method, view=view.func_name, meths=meths)
                logger.error(msg)
                raise Exception(msg)
            return view(*args, **kwargs)
        return inner_view
    return inner_meth_allowed

def set_servers_state(cluster, client):
    """ Assignes 3 flags to the cluster indicating whether load-balancer
    believes the servers are UP, DOWN or in the MAINT mode.
    """
    servers_state = client.get_servers_state()

    up = []
    down = []
    maint = []
    
    cluster.some_down = False
    cluster.some_maint = False
    cluster.all_up = False
    
    # Note: currently we support only the 'http_plain' access_type.
    for access_type in("http_plain",):
        up.extend(servers_state["UP"][access_type])
        down.extend(servers_state["DOWN"][access_type])
        maint.extend(servers_state["MAINT"][access_type])

    # Do we have any servers at all?
    if any((up, down, maint)):
        if not(up or maint) and down:
            cluster.all_up = True
        else:
            if down:
                cluster.some_down = True
            if maint:
                cluster.some_maint = True
                
            # We know not all are down so maybe all are up?
            if not(cluster.some_down or cluster.some_maint):
                cluster.all_up = True

def change_password(req, service_name):
    
    cluster_id = req.POST.get('cluster_id')
    id = req.POST.get('id')
    
    password1 = req.POST.get('password1', '')
    password2 = req.POST.get('password2', '')
    
    cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()
    
    try:
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.data = Element('data')
        zato_message.data.id = id
        zato_message.data.password1 = password1
        zato_message.data.password2 = password2
        
        _, zato_message, soap_response = invoke_admin_service(cluster,
                        service_name, zato_message)
    
    except Exception, e:
        msg = 'Could not change the password, e=[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        return HttpResponse(dumps({'message':'Password updated'}))