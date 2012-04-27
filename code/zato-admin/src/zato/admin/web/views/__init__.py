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
from lxml import etree
from lxml.objectify import Element

# Validate
from validate import is_boolean

# Zato
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms import ChooseClusterForm
from zato.common import zato_namespace, zato_path
from zato.common.odb.model import Cluster
from zato.common.util import TRACE1

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
            req = args[1]
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
    cluster.all_down = False

    # Note: currently we support only the 'http_plain' access_type.
    for access_type in('http_plain',):
        up.extend(servers_state['UP'][access_type])
        down.extend(servers_state['DOWN'][access_type])
        maint.extend(servers_state['MAINT'][access_type])

    # Do we have any servers at all?
    if any((up, down, maint)):
        if not(up or maint) and down:
            cluster.all_down = True
        else:
            if down:
                cluster.some_down = True
            if maint:
                cluster.some_maint = True

def change_password(req, service_name, field1='password1', field2='password2', success_msg='Password updated'):

    cluster_id = req.POST.get('cluster_id')
    id = req.POST.get('id')

    password1 = req.POST.get(field1, '')
    password2 = req.POST.get(field2, '')

    cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()

    try:
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.request = Element('request')
        zato_message.request.id = id
        zato_message.request.password1 = password1
        zato_message.request.password2 = password2

        _, zato_message, soap_response = invoke_admin_service(cluster,
                        service_name, zato_message)

    except Exception, e:
        msg = 'Could not change the password, e=[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        return HttpResponse(dumps({'message':success_msg}))

class View(object):
    """ A base class upon which other views are based. Takes care of all the tedious
    repetitive stuff common to almost all of the views.
    """
    meth_allowed = 'meth_allowed-must-be-defined-in-a-subclass'
    url_name = 'url_name-must-be-defined-in-a-subclass'
    template = 'template-must-be-defined-in-a-subclass'
    
    needs_clusters = False
    service = None
    output_class = None

    class SimpleIO:
        input_required = []
        output_required = []
        output_optional = []
        output_repeated = False
        
    def __init__(self):
        self.req = None
        self.cluster_id = None
        self.items = []
        self.item = None
        
    def fetch_cluster_id(self):
        # Doesn't look overtly smart right now but more code will follow to sanction
        # the existence of this function
        cluster_id = self.req.GET.get('cluster')
        
        if cluster_id:
            self.cluster_id = cluster_id
        
    def invoke_admin_service(self):
        cluster = self.req.zato.odb.query(Cluster).filter_by(id=self.cluster_id).first()
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.request = Element('request')
        zato_message.request.cluster_id = self.cluster_id
        
        zato_message, soap_response  = invoke_admin_service(cluster, self.service, zato_message)
        
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Request:[{}], response:[{}]'.format(etree.tostring(zato_message), soap_response))
            
        return zato_message
    
    def _handle_item_list(self, item_list):
        for msg_item in item_list.item:
            id = msg_item.id.text
            name = msg_item.name.text
            is_active = is_boolean(msg_item.is_active.text)
            impl_name = msg_item.impl_name.text
            is_internal = is_boolean(msg_item.is_internal.text)
            usage_count = msg_item.usage_count.text if hasattr(msg_item, 'usage_count') else 'TODO'
            
            item =  self.output_class(id, name, is_active, impl_name, is_internal, None, usage_count)
            self.items.append(item)
    
    def _handle_item(self, item):
        pass
    
    def __call__(self, req, *args, **kwargs):
        """ Handles the request, taking care of common things and delegating 
        control to the subclass for fetching this view-specific data.
        """
        self.req = req
        self.fetch_cluster_id()
        return_data = {'cluster_id':self.cluster_id}
        
        if self.needs_clusters:
            zato_clusters = req.zato.odb.query(Cluster).order_by('name').all()
            return_data['zato_clusters'] = zato_clusters
            return_data['choose_cluster_form'] = ChooseClusterForm(zato_clusters, self.req.GET)
            
        output_repeated = getattr(self.SimpleIO, 'output_repeated', False)
        zato_path_needed = 'response.item_list.item' if output_repeated else 'response.item'
        
        if self.service and self.cluster_id:
            zato_message = self.invoke_admin_service()
            if zato_path(zato_path_needed).get_from(zato_message) is not None:
                if output_repeated:
                    self._handle_item_list(zato_message.response.item_list)
                else:
                    self._handle_item(zato_message.response.item)

        return_data['items'] = self.items
        return_data['item'] = self.item

        view_specific = self.handle()
        if view_specific:
            return_data.update(view_specific)
        
        if logger.isEnabledFor(TRACE1):
            logger.log(TRACE1, 'Returning render_to_response [{0}]'.format(return_data))
    
        return render_to_response(self.template, return_data, context_instance=RequestContext(req))

    def handle(self, req, *args, **kwargs):
        raise NotImplementedError('Must be overloaded by a subclass')
    