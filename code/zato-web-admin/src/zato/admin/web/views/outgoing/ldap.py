# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
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
from zato.admin.web.views import change_password as _change_password
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.outgoing.ldap import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.odb.model import LDAPConnectionPool
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
        'host': params[prefix + 'host'],
        'port': params[prefix + 'port'],
        'bind_dn': params[prefix + 'bind_dn'],
        'pool_size': params[prefix + 'pool_size'],
        'extra': params.get(prefix + 'extra'),
    }

def _edit_create_response(verb, id, name, cluster_id):
    """ A common function for producing return data for create and edit actions.
    """
    return_data = {'id': id,
                   'message': 'Successfully {0} the outgoing LDAP connection [{1}]'.format(verb, name.encode('utf-8')),
                   'cluster_id': cluster_id,
                }

    return HttpResponse(dumps(return_data), mimetype='application/javascript')

@method_allowed('GET')
def index(req):
    """ Lists all the LDAP connections.
    """
    items = []
    create_form = CreateForm()
    edit_form = EditForm(prefix='edit')
    change_password_form = ChangePasswordForm()

    if req.zato.cluster_id and req.method == 'GET':
        for item in req.zato.client.invoke('zato.outgoing.ldap.get-list', {'cluster_id': req.zato.cluster_id}):

            _item =  LDAPConnectionPool()

            for name in('id', 'name', 'is_active', 'host', 'port', 'bind_dn', 'pool_size'):
                value = getattr(item, name)
                setattr(_item, name, value)

            _item.extra = item.extra or ''
            items.append(_item)

    return_data = {'zato_clusters':req.zato.clusters,
        'cluster_id':req.zato.cluster_id,
        'choose_cluster_form':req.zato.choose_cluster_form,
        'items':items,
        'create_form':create_form,
        'edit_form':edit_form,
        'change_password_form': change_password_form
        }

    return TemplateResponse(req, 'zato/outgoing/ldap.html', return_data)

@method_allowed('POST')
def create(req):
    """ Creates a new LDAP connection.
    """
    try:
        request = _get_edit_create_message(req.POST)
        response = req.zato.client.invoke('zato.outgoing.ldap.create', request)

        return _edit_create_response('created', response.data.id, req.POST['name'], req.zato.cluster.id)

    except Exception, e:
        msg = 'Could not create an outgoing LDAP connection, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)


@method_allowed('POST')
def edit(req):
    """ Updates an LDAP connection.
    """
    try:
        request = _get_edit_create_message(req.POST, 'edit-')
        response = req.zato.client.invoke('zato.outgoing.ldap.edit', request)

        return _edit_create_response('updated', req.POST['id'], req.POST['edit-name'], req.zato.cluster.id)

    except Exception, e:
        msg = 'Could not update the outgoing LDAP connection, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

class Delete(_Delete):
    url_name = 'out-ldap-delete'
    error_message = 'Could not delete the LDAP connection'
    service_name = 'zato.outgoing.ldap.delete'

@method_allowed('POST')
def ping(req, cluster_id, id):
    """ Pings a database and returns the time it took, in milliseconds.
    """
    response = req.zato.client.invoke('zato.outgoing.ldap.ping', {'id':id})

    if response.ok:
        return TemplateResponse(req, 'zato/outgoing/ldap-ping-ok.html',
            {'response_time':'%.3f' % float(response.data.response_time)})
    else:
        return HttpResponseServerError(response.details)

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.outgoing.ldap.change-password')
