# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.settings import delivery_friendly_name
from zato.admin.web.forms.outgoing.jms_wmq import CreateForm, EditForm
from zato.admin.web.views import Delete as _Delete, get_definition_list, method_allowed, parse_response_data
from zato.admin.web.util import get_template_response
from zato.common.json_internal import dumps
from zato.common.odb.model import OutgoingWMQ

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

send_attrs = ('id', 'queue_name', 'data', 'delivery_mode', 'priority', 'expiration', 'reply_to', 'msg_id', 'correl_id')

# ################################################################################################################################

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

# ################################################################################################################################

def _edit_create_response(client, verb, id, name, delivery_mode_text, cluster_id, def_id):
    response = client.invoke('zato.definition.jms-wmq.get-by-id', {'id':def_id, 'cluster_id':cluster_id})
    return_data = {'id': id,
                   'message': 'Successfully {} outgoing IBM MQ connection `{}`'.format(verb, name),
                   'delivery_mode_text': delivery_mode_text,
                   'def_name': response.data.name
                }

    return HttpResponse(dumps(return_data), content_type='application/javascript')

# ################################################################################################################################

@method_allowed('GET')
def index(req):
    items = []
    create_form = CreateForm()
    edit_form = EditForm(prefix='edit')
    meta = None

    if req.zato.cluster_id and req.method == 'GET':
        def_ids = get_definition_list(req.zato.client, req.zato.cluster, 'jms-wmq')
        create_form.set_def_id(def_ids)
        edit_form.set_def_id(def_ids)

        request = {
            'cluster_id': req.zato.cluster_id,
            'paginate': True,
            'cur_page': req.GET.get('cur_page', 1)
        }

        data, meta = parse_response_data(req.zato.client.invoke('zato.outgoing.jms-wmq.get-list', request))

        for item in data:
            _item = OutgoingWMQ(
                item.id,
                item.name,
                item.is_active,
                item.delivery_mode,
                item.priority,
                item.expiration,
                item.def_id,
                delivery_mode_text=delivery_friendly_name[str(item.delivery_mode)],
                def_name=item.def_name
            )
            items.append(_item)

    return_data = {'zato_clusters':req.zato.clusters,
        'cluster_id':req.zato.cluster_id,
        'search_form':req.zato.search_form,
        'items':items,
        'create_form':create_form,
        'edit_form':edit_form,
        'paginate':True,
        'meta': meta,
        'req': req,
        }

    return get_template_response(req, 'zato/outgoing/jms-wmq.html', return_data)

# ################################################################################################################################

@method_allowed('POST')
def create(req):
    try:
        response = req.zato.client.invoke('zato.outgoing.jms-wmq.create', _get_edit_create_message(req.POST))
        delivery_mode_text = delivery_friendly_name[str(req.POST['delivery_mode'])]

        return _edit_create_response(req.zato.client, 'created', response.data.id,
            req.POST['name'], delivery_mode_text, req.POST['cluster_id'], req.POST['def_id'])
    except Exception:
        msg = 'Could not create outgoing IBM MQ connection, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################

@method_allowed('POST')
def edit(req):
    try:
        request = _get_edit_create_message(req.POST, 'edit-')
        req.zato.client.invoke('zato.outgoing.jms-wmq.edit', request)
        delivery_mode_text = delivery_friendly_name[str(req.POST['edit-delivery_mode'])]

        return _edit_create_response(req.zato.client, 'updated', req.POST['id'], req.POST['edit-name'],
            delivery_mode_text, req.POST['cluster_id'], req.POST['edit-def_id'])

    except Exception:
        msg = 'Could not update outgoing IBM MQ connection, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'out-jms-wmq-delete'
    error_message = 'Could not delete the outgoing IBM MQ connection'
    service_name = 'zato.outgoing.jms-wmq.delete'

# ################################################################################################################################

@method_allowed('GET')
def send_message(req, cluster_id, conn_id, name_slug):

    response = req.zato.client.invoke('zato.outgoing.jms-wmq.get', {
        'cluster_id': cluster_id,
        'id': conn_id,
    })

    if not response.ok:
        raise Exception(response.details)

    return_data = {
        'cluster_id': cluster_id,
        'name_slug': name_slug,
        'item': response.data,
        'conn_id': conn_id
    }

    return TemplateResponse(req, 'zato/outgoing/jms-wmq-send-message.html', return_data)

# ################################################################################################################################

@method_allowed('POST')
def send_message_action(req, cluster_id, conn_id, name_slug):

    try:
        request = {
            'cluster_id': req.zato.cluster_id
        }

        for name in send_attrs:
            request[name] = req.POST.get(name, '')

        response = req.zato.client.invoke('zato.outgoing.jms-wmq.send-message', request)

        if response.ok:
            return HttpResponse(dumps({'msg': 'OK, message sent successfully.'}), content_type='application/javascript')
        else:
            raise Exception(response.details)
    except Exception:
        msg = 'Caught an exception, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################
