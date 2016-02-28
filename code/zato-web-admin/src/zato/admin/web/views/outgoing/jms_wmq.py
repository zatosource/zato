# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

# anyjson
from anyjson import dumps

# Zato
from zato.admin.settings import delivery_friendly_name
from zato.admin.web.forms.outgoing.jms_wmq import CreateForm, EditForm
from zato.admin.web.views import Delete as _Delete, get_definition_list, method_allowed
from zato.common.odb.model import OutgoingWMQ

logger = logging.getLogger(__name__)

def _get_edit_create_message(params, prefix=''):
    """ Creates a base dictionary which can be used by both 'edit' and 'create' actions.
    """
    return {
        'id': params.get('id'),
        'cluster_id': params['cluster_id'],
        'name': params[prefix + 'name'],
        'is_active': bool(params.get(prefix + 'is_active')),
        'def_id': params[prefix + 'def_id'],
        'delivery_mode': params[prefix + 'delivery_mode'],
        'priority': params[prefix + 'priority'],
        'expiration': params.get(prefix + 'expiration'),
    }

def _edit_create_response(client, verb, id, name, delivery_mode_text, cluster_id, def_id):
    response = client.invoke('zato.definition.jms-wmq.get-by-id', {'id':def_id, 'cluster_id':cluster_id})
    return_data = {'id': id,
                   'message': 'Successfully {0} the outgoing JMS WebSphere MQ connection [{1}]'.format(verb, name),
                   'delivery_mode_text': delivery_mode_text,
                   'def_name': response.data.name
                }

    return HttpResponse(dumps(return_data), content_type='application/javascript')

@method_allowed('GET')
def index(req):
    items = []
    create_form = CreateForm()
    edit_form = EditForm(prefix='edit')

    if req.zato.cluster_id and req.method == 'GET':
        def_ids = get_definition_list(req.zato.client, req.zato.cluster, 'jms-wmq')
        create_form.set_def_id(def_ids)
        edit_form.set_def_id(def_ids)

        for item in req.zato.client.invoke('zato.outgoing.jms-wmq.get-list', {'cluster_id': req.zato.cluster_id}):
            _item = OutgoingWMQ(item.id, item.name, item.is_active, item.delivery_mode,
                item.priority, item.expiration, item.def_id, delivery_friendly_name[item.delivery_mode],
                item.def_name)
            items.append(_item)

    return_data = {'zato_clusters':req.zato.clusters,
        'cluster_id':req.zato.cluster_id,
        'choose_cluster_form':req.zato.choose_cluster_form,
        'items':items,
        'create_form':create_form,
        'edit_form':edit_form,
        }

    return TemplateResponse(req, 'zato/outgoing/jms_wmq.html', return_data)

@method_allowed('POST')
def create(req):
    try:
        response = req.zato.client.invoke('zato.outgoing.jms-wmq.create', _get_edit_create_message(req.POST))
        delivery_mode_text = delivery_friendly_name[int(req.POST['delivery_mode'])]

        return _edit_create_response(req.zato.client, 'created', response.data.id,
            req.POST['name'], delivery_mode_text, req.POST['cluster_id'], req.POST['def_id'])
    except Exception, e:
        msg = 'Could not create an outgoing JMS WebSphere MQ connection, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)


@method_allowed('POST')
def edit(req):
    try:
        request = _get_edit_create_message(req.POST, 'edit-')
        req.zato.client.invoke('zato.outgoing.jms-wmq.edit', request)
        delivery_mode_text = delivery_friendly_name[int(req.POST['edit-delivery_mode'])]

        return _edit_create_response(req.zato.client, 'updated', req.POST['id'], req.POST['edit-name'],
            delivery_mode_text, req.POST['cluster_id'], req.POST['edit-def_id'])

    except Exception, e:
        msg = 'Could not update the outgoing JMS WebSphere MQ connection, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)


class Delete(_Delete):
    url_name = 'out-jms-wmq-delete'
    error_message = 'Could not delete the outgoing JMS WebSphere MQ connection'
    service_name = 'zato.outgoing.jms-wmq.delete'
