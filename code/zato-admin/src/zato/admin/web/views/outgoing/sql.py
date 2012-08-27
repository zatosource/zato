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
from django.template.response import TemplateResponse

# Validate
from validate import is_boolean

# anyjson
from anyjson import dumps

# Zato
from zato.admin.settings import odb_engine_friendly_name
from zato.admin.web import invoke_admin_service
from zato.admin.web.views import change_password as _change_password
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.outgoing.sql import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, meth_allowed
from zato.common.odb.model import SQLConnectionPool
from zato.common import zato_path

logger = logging.getLogger(__name__)

def _get_edit_create_message(params, prefix=''):
    """ Creates a base dictionary which can be used by both 'edit' and 'create' actions.
    """
    return {
        'id': params.get('id'),
        'cluster_id': params['cluster_id'],
        'name': params[prefix + 'name'],
        'is_active': bool(params.get(prefix + 'is_active')),
        'engine': params[prefix + 'engine'],
        'host': params[prefix + 'host'],
        'port': params[prefix + 'port'],
        'db_name': params[prefix + 'db_name'],
        'username': params[prefix + 'username'],
        'pool_size': params[prefix + 'pool_size'],
        'extra': params.get(prefix + 'extra'),
    }

def _edit_create_response(verb, id, name, engine, cluster_id):
    """ A common function for producing return data for create and edit actions.
    """
    return_data = {'id': id,
                   'message': 'Successfully {0} the outgoing SQL connection [{1}]'.format(verb, name.encode('utf-8')),
                   'engine_text': odb_engine_friendly_name[engine],
                   'cluster_id': cluster_id,
                }

    return HttpResponse(dumps(return_data), mimetype='application/javascript')

@meth_allowed('GET')
def index(req):
    """ Lists all the SQL connections.
    """
    items = []
    create_form = CreateForm()
    edit_form = EditForm(prefix='edit')
    change_password_form = ChangePasswordForm()

    if req.zato.cluster_id and req.method == 'GET':
        zato_message, soap_response  = invoke_admin_service(req.zato.cluster, 'zato:outgoing.sql.get-list', {'cluster_id': req.zato.cluster_id})
        if zato_path('response.item_list.item').get_from(zato_message) is not None:

            for msg_item in zato_message.response.item_list.item:

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

    return_data = {'zato_clusters':req.zato.clusters,
        'cluster_id':req.zato.cluster_id,
        'choose_cluster_form':req.zato.choose_cluster_form,
        'items':items,
        'create_form':create_form,
        'edit_form':edit_form,
        'change_password_form': change_password_form
        }

    return TemplateResponse(req, 'zato/outgoing/sql.html', return_data)

@meth_allowed('POST')
def create(req):
    """ Creates a new SQL connection.
    """
    try:
        zato_message = _get_edit_create_message(req.POST)
        engine = zato_message['engine']
        zato_message, soap_response = invoke_admin_service(req.zato.cluster, 'zato:outgoing.sql.create', zato_message)

        return _edit_create_response('created', zato_message.response.item.id.text, req.POST['name'], engine, req.zato.cluster.id)

    except Exception, e:
        msg = 'Could not create an outgoing SQL connection, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)


@meth_allowed('POST')
def edit(req):
    """ Updates an SQL connection.
    """
    try:
        zato_message = _get_edit_create_message(req.POST, 'edit-')
        engine = zato_message['engine']
        zato_message, soap_response = invoke_admin_service(req.zato.cluster, 'zato:outgoing.sql.edit', zato_message)

        return _edit_create_response('updated', req.POST['id'], req.POST['edit-name'], engine, req.zato.cluster.id)

    except Exception, e:
        msg = 'Could not update the outgoing SQL connection, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

class Delete(_Delete):
    url_name = 'out-sql-delete'
    error_message = 'Could not delete the SQL connection'
    soap_action = 'zato:outgoing.sql.delete'

@meth_allowed('POST')
def ping(req, cluster_id, id):
    """ Pings a database and returns the time it took, in milliseconds.
    """
    try:
        zato_message, soap_response = invoke_admin_service(req.zato.cluster, 'zato:outgoing.sql.ping', {'id':id})
        response_time = zato_path('response.item.response_time', True).get_from(zato_message)
    except Exception, e:
        msg = 'Ping failed. e:[{}]'.format(format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        return TemplateResponse(req, 'zato/outgoing/sql-ping-ok.html', {'response_time':'%.3f' % float(response_time)})

@meth_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato:outgoing.sql.change-password')
