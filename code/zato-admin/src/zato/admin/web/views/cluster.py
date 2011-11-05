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
from pprint import pprint
from string import whitespace
from traceback import format_exc

# Django
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import loader, RequestContext

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# anyjson
from anyjson import dumps

# Zato
from zato.admin.web.forms.cluster import CreateClusterForm, EditClusterForm, DeleteClusterForm
from zato.admin.web.views import get_lb_client, meth_allowed, set_servers_state
from zato.admin.settings import DATABASE_ENGINE, DATABASE_HOST, DATABASE_NAME, DATABASE_PORT, \
     DATABASE_USER, DATABASE_PASSWORD, sqlalchemy_django_engine
from zato.common.odb.model import Cluster
from zato.common.util import TRACE1

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
            req.odb.add(item)
            req.odb.commit()
            
            try:
                item.lb_config = get_lb_client(item).get_config()
            except Exception, e:
                item.lb_config = None
                msg = "Exception caught while fetching the load balancer's config, e=[{0}]".format(format_exc(e))
                logger.error(msg)                    
            
            return _edit_create_response(item, verb)
        
        except Exception, e:
            msg = 'Exception caught, e=[{0}]'.format(format_exc(e))
            logger.error(msg)

            return HttpResponseServerError(msg)

    except Exception, e:
        req.odb.rollback()
        return HttpResponseServerError(str(format_exc(e)))


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

    items = req.odb.query(Cluster).order_by('name').all()
    for item in items:
        client = get_lb_client(item)

        try:
            lb_config = client.get_config()
            item.lb_config = lb_config

            # Assign the flags indicating whether servers are DOWN or in the MAINT mode.
            set_servers_state(item, client)

        except Exception, e:
            msg = 'Could not invoke agent, client=[{client!r}], e=[{e}]'.format(client=client,
                                                                e=format_exc(e))
            logger.error(msg)
            item.lb_config = None

    return_data = {'create_form':create_form, 'delete_form':delete_form,
                   'edit_form':EditClusterForm(prefix='edit'), 'items':items}

    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, 'Returning render_to_response [%s]' % return_data)

    return render_to_response('zato/cluster/index.html', return_data,
                              context_instance=RequestContext(req))


@meth_allowed('POST')
def create(req):
    return _create_edit(req, 'created', Cluster(), CreateClusterForm)

@meth_allowed('POST')
def edit(req):
    return _create_edit(req, 'updated', 
        req.odb.query(Cluster).filter_by(id=req.POST['id']).one(), EditClusterForm, 'edit')

def _get(req, **filter):
    cluster = req.odb.query(Cluster).filter_by(**filter).one()
    return HttpResponse(cluster.to_json(), mimetype='application/javascript')

@meth_allowed('GET')
def get_by_id(req, cluster_id):
    return _get(req, id=cluster_id)

@meth_allowed('GET')
def get_by_name(req, cluster_name):
    return _get(req, name=cluster_name)

@meth_allowed('GET')
def get_servers_state(req, cluster_id):
    cluster = req.odb.query(Cluster).filter_by(id=cluster_id).one()
    client = get_lb_client(cluster)

    # Assign the flags indicating whether servers are DOWN or in the MAINT mode.
    try:
        set_servers_state(cluster, client)
    except Exception, e:
        msg = "Failed to invoke the load-balancer's agent and set the state of servers, e=[{e}]".format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

    return_data = {'cluster':cluster}

    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, 'Returning render_to_response [%s]' % return_data)

    return render_to_response('zato/cluster/servers_state.html', return_data,
                              context_instance=RequestContext(req))

@meth_allowed('POST')
def delete(req, cluster_id):

    try:
        cluster = req.odb.query(Cluster).filter_by(id=cluster_id).one()

        req.odb.delete(cluster)
        req.odb.commit()

    except Exception, e:
        msg = 'Could not delete the cluster, e=[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        return HttpResponse()