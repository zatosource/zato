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
from django.template import RequestContext

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

def _edit_create_response(id, verb, name):
    return_data = {'id': id,
                   'message': 'Successfully {0} the cluster [{1}]'.format(verb, name)}
    return HttpResponse(dumps(return_data), mimetype='application/javascript')

def _create_edit(req, verb, cluster, form_class, prefix=''):

    join = '-' if prefix else ''
    form = form_class(req.POST, prefix=prefix)

    try:
        if form.is_valid():
            for s in whitespace:
                if s in req.POST[prefix + join + 'name']:
                    return HttpResponseServerError('Cluster name must not contain whitespace.')

            description = req.POST[prefix + join + 'description'].strip()
            description = description if description else None

            cluster.name = req.POST[prefix + join + 'name'].strip()
            cluster.description = description
            cluster.odb_type = req.POST[prefix + join + 'odb_engine'].strip()
            cluster.odb_host = req.POST[prefix + join + 'odb_host'].strip()
            cluster.odb_port = req.POST[prefix + join + 'odb_port'].strip()
            cluster.odb_user = req.POST[prefix + join + 'odb_user'].strip()
            cluster.odb_db_name = req.POST[prefix + join + 'odb_db_name'].strip()
            cluster.odb_schema = req.POST[prefix + join + 'odb_schema'].strip()
            cluster.lb_host = req.POST[prefix + join + 'lb_host'].strip()
            cluster.lb_port = req.POST[prefix + join + 'lb_port'].strip()
            cluster.lb_agent_port = req.POST[prefix + join + 'lb_agent_port'].strip()
            cluster.broker_host = req.POST[prefix + join + 'broker_host'].strip()
            cluster.broker_start_port = req.POST[prefix + join + 'broker_start_port'].strip()
            cluster.broker_token = req.POST[prefix + join + 'broker_token'].strip()

            try:
                req.odb.add(cluster)
                req.odb.commit()
            except IntegrityError, e:
                msg = 'Cluster name [{0}] is not unique'.format(cluster.name)
                logger.error(msg + ', e=[{0}], cluster=[{1!r}]'.format(format_exc(e), cluster))

                return HttpResponseServerError(msg)

            return _edit_create_response(cluster.id, verb, cluster.name)

        else:
            logger.error('form.errors=[%s]' % form.errors)
            return HttpResponseServerError('Invalid data submitted, req.POST=[%s]' % req.POST)
    except Exception, e:
        req.odb.rollback()
        return HttpResponseServerError(str(format_exc(e)))


@meth_allowed('GET')
def index(req):

    initial = {}
    initial['odb_engine'] = sqlalchemy_django_engine[DATABASE_ENGINE]
    initial['odb_host'] = DATABASE_HOST
    initial['odb_port'] = DATABASE_PORT
    initial['odb_user'] = DATABASE_USER
    initial['odb_db_name'] = DATABASE_NAME

    create_form = CreateClusterForm(initial=initial)
    delete_form = DeleteClusterForm(prefix='delete')

    clusters = req.odb.query(Cluster).order_by('name').all()
    for cluster in clusters:
        client = get_lb_client(cluster)

        try:
            lb_config = client.get_config()
            cluster.lb_config = lb_config

            # Assign the flags indicating whether servers are DOWN or in the MAINT mode.
            set_servers_state(cluster, client)

        except Exception, e:
            msg = 'Could not invoke agent, client=[{client!r}], e=[{e}]'.format(client=client,
                                                                e=format_exc(e))
            logger.error(msg)
            cluster.lb_config = None

    return_data = {'create_form':create_form, 'delete_form':delete_form,
                   'edit_form':EditClusterForm(prefix='edit'), 'clusters':clusters}

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
        req.odb.query(Cluster).filter_by(id=req.POST['cluster_id']).one(), EditClusterForm, 'edit')

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
def delete(req):

    prefix = 'delete'
    form = DeleteClusterForm(req.POST, prefix=prefix)

    try:
        if form.is_valid():
            cluster = req.odb.query(Cluster).filter_by(id=req.POST[prefix + '-' + 'cluster_id']).one()

            req.odb.delete(cluster)
            req.odb.commit()
        else:
            msg = 'Could not delete the cluster, req.POST=[{post}], errors=[{errors}]'.format(
                post=req.POST, errors=form._errors.items())
            raise Exception(msg)

    except Exception, e:
        msg = 'Could not delete the cluster, e=[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        return HttpResponse()