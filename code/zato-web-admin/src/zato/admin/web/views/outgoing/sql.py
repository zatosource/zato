# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import change_password as _change_password, parse_response_data
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.outgoing.sql import CreateForm, EditForm
from zato.admin.web.views import Delete as _Delete, method_allowed
from zato.common.api import engine_display_name
from zato.common.json_internal import dumps
from zato.common.odb.model import SQLConnectionPool

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

def _edit_create_response(verb, id, name, engine_display_name, cluster_id):
    """ A common function for producing return data for create and edit actions.
    """
    return_data = {'id': id,
                   'message': 'Successfully {} outgoing SQL connection `{}`'.format(verb, name),
                   'engine_display_name': engine_display_name,
                   'cluster_id': cluster_id,
                }

    return HttpResponse(dumps(return_data), content_type='application/javascript')

@method_allowed('GET')
def index(req):
    """ Lists all the SQL connections.
    """
    items = []
    create_form = CreateForm(req)
    edit_form = EditForm(req, prefix='edit')
    change_password_form = ChangePasswordForm()
    meta = None

    if req.zato.cluster_id and req.method == 'GET':

        request = {
            'cluster_id': req.zato.cluster_id,
            'paginate': True,
            'cur_page': req.GET.get('cur_page', 1)
        }

        data, meta = parse_response_data(req.zato.client.invoke('zato.outgoing.sql.get-list', request))

        for item in data:

            _item = SQLConnectionPool()
            for name in('id', 'name', 'is_active', 'engine', 'host', 'port', 'db_name', 'username', 'pool_size', 'engine'):
                value = getattr(item, name)
                setattr(_item, name, value)

            _item.engine_display_name = engine_display_name[_item.engine]

            _item.extra = item.extra or ''
            items.append(_item)

    return_data = {'zato_clusters':req.zato.clusters,
        'cluster_id':req.zato.cluster_id,
        'search_form':req.zato.search_form,
        'items':items,
        'create_form':create_form,
        'edit_form':edit_form,
        'change_password_form': change_password_form,
        'paginate':True,
        'meta': meta,
        'req': req,
        }

    return TemplateResponse(req, 'zato/outgoing/sql.html', return_data)

@method_allowed('POST')
def create(req):
    """ Creates a new SQL connection.
    """
    try:
        request = _get_edit_create_message(req.POST)
        response = req.zato.client.invoke('zato.outgoing.sql.create', request)

        return _edit_create_response(
            'created', response.data.id, req.POST['name'], response.data.display_name, req.zato.cluster.id)

    except Exception:
        msg = 'Could not create an outgoing SQL connection, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)


@method_allowed('POST')
def edit(req):
    """ Updates an SQL connection.
    """
    try:
        request = _get_edit_create_message(req.POST, 'edit-')
        response = req.zato.client.invoke('zato.outgoing.sql.edit', request)

        return _edit_create_response(
            'updated', req.POST['id'], req.POST['edit-name'], response.data.display_name, req.zato.cluster.id)

    except Exception:
        msg = 'Could not update the outgoing SQL connection, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

class Delete(_Delete):
    url_name = 'out-sql-delete'
    error_message = 'Could not delete the SQL connection'
    service_name = 'zato.outgoing.sql.delete'

@method_allowed('POST')
def ping(req, cluster_id, id):
    """ Pings a database and returns the time it took, in milliseconds.
    """
    try:
        response = req.zato.client.invoke('zato.outgoing.sql.ping', {
            'id':id,
            'should_raise_on_error': True,
        })

        if response.ok:

            if not response.data.response_time:
                return HttpResponseServerError('No response time received')
            else:
                return TemplateResponse(req, 'zato/outgoing/sql-ping-ok.html',
                    {'response_time':'%.3f' % float(response.data.response_time)})
        else:
            return HttpResponseServerError(response.details)
    except Exception:
        msg = 'Could not ping the outgoing SQL connection, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.outgoing.sql.change-password')
