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

# stdlib
import logging
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import RequestContext

# lxml
from lxml.objectify import Element

# Validate
from validate import is_boolean

# anyjson
from anyjson import dumps

# Zato
from zato.admin.settings import odb_engine_friendly_name
from zato.admin.web import invoke_admin_service
from zato.admin.web.views import change_password as _change_password
from zato.admin.web.forms import ChangePasswordForm, ChooseClusterForm
from zato.admin.web.forms.outgoing.sql import CreateForm, EditForm
from zato.admin.web.views import meth_allowed
from zato.common.odb.model import Cluster, SQLConnectionPool
from zato.common import zato_namespace, zato_path
from zato.common.util import TRACE1

logger = logging.getLogger(__name__)

def _get_edit_create_message(params, prefix=''):
    """ Creates a base document which can be used by both 'edit' and 'create' actions.
    """
    zato_message = Element('{%s}zato_message' % zato_namespace)
    zato_message.data = Element('data')
    zato_message.data.id = params.get('id')
    zato_message.data.cluster_id = params['cluster_id']
    zato_message.data.name = params[prefix + 'name']
    zato_message.data.is_active = bool(params.get(prefix + 'is_active'))
    zato_message.data.engine = params[prefix + 'engine']
    zato_message.data.host = params[prefix + 'host']
    zato_message.data.port = params[prefix + 'port']
    zato_message.data.db_name = params[prefix + 'db_name']
    zato_message.data.username = params[prefix + 'username']
    zato_message.data.pool_size = params[prefix + 'pool_size']
    zato_message.data.extra = params.get(prefix + 'extra')

    return zato_message

def _edit_create_response(verb, id, name, engine):
    """ A common function for producing return data for create and edit actions.
    """
    return_data = {'id': id,
                   'message': 'Successfully {0} the outgoing SQL connection [{1}]'.format(verb, name),
                   'engine_text': odb_engine_friendly_name[engine],
                }

    return HttpResponse(dumps(return_data), mimetype='application/javascript')

@meth_allowed('GET')
def index(req):
    """ Lists all the SQL connections.
    """
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

        _, zato_message, soap_response  = invoke_admin_service(cluster, 'zato:outgoing.sql.get-list', zato_message)

        if zato_path('data.item_list.item').get_from(zato_message) is not None:

            for msg_item in zato_message.data.item_list.item:

                id = msg_item.id.text
                name = msg_item.name.text
                is_active = is_boolean(msg_item.is_active.text)
                engine = msg_item.engine.text if msg_item.engine else ''
                host = msg_item.host.text if msg_item.host else ''
                port = msg_item.port.text if msg_item.port else ''
                db_name = msg_item.db_name.text if msg_item.db_name else ''
                username = msg_item.username.text if msg_item.username else ''
                pool_size = msg_item.pool_size.text if msg_item.pool_size else ''
                extra = msg_item.extra.text if msg_item.extra else ''
                
                item =  SQLConnectionPool()
                item.id = id
                item.name = name
                item.is_active = is_active
                item.engine = engine
                item.engine_text = odb_engine_friendly_name[engine]
                item.host = host
                item.port = port
                item.db_name = db_name
                item.username = username
                item.pool_size = pool_size
                item.extra = extra
                items.append(item)

    return_data = {'zato_clusters':zato_clusters,
        'cluster_id':cluster_id,
        'choose_cluster_form':choose_cluster_form,
        'items':items,
        'create_form':create_form,
        'edit_form':edit_form,
        'change_password_form': change_password_form
        }

    # TODO: Should really be done by a decorator.
    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, 'Returning render_to_response [{0}]'.format(return_data))

    return render_to_response('zato/outgoing/sql.html', return_data,
                              context_instance=RequestContext(req))

@meth_allowed('POST')
def create(req):
    """ Creates a new SQL connection.
    """
    cluster = req.odb.query(Cluster).filter_by(id=req.POST['cluster_id']).first()

    try:
        zato_message = _get_edit_create_message(req.POST)
        engine = zato_message.data.engine
        _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:outgoing.sql.create', zato_message)

        return _edit_create_response('created', zato_message.data.out_sql.id.text, req.POST['name'], engine)

    except Exception, e:
        msg = 'Could not create an outgoing SQL connection, e=[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)


@meth_allowed('POST')
def edit(req):
    """ Updates an SQL connection.
    """
    cluster = req.odb.query(Cluster).filter_by(id=req.POST['cluster_id']).first()

    try:
        zato_message = _get_edit_create_message(req.POST, 'edit-')
        engine = zato_message.data.engine
        _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:outgoing.sql.edit', zato_message)

        return _edit_create_response('updated', req.POST['id'], req.POST['edit-name'], engine)

    except Exception, e:
        msg = 'Could not update the outgoing SQL connection, e=[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

@meth_allowed('POST')
def delete(req, id, cluster_id):
    """ Deletes an SQL connection.
    """
    cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()

    try:
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.data = Element('data')
        zato_message.data.id = id

        _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:outgoing.sql.delete', zato_message)

        return HttpResponse()

    except Exception, e:
        msg = 'Could not delete the outgoing SQL connection, e=[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)


def ping():
    pass

def change_password():
    pass
