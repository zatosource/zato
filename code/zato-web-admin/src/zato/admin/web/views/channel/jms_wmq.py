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

# anyjson
from anyjson import dumps

# Zato
from zato.admin.web.forms.channel.jms_wmq import CreateForm, EditForm
from zato.admin.web.views import Delete as _Delete, get_definition_list, Index as _Index, method_allowed
from zato.common.odb.model import ChannelWMQ

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
        'queue': params[prefix + 'queue'],
        'service': params[prefix + 'service'],
        'data_format': params.get(prefix + 'data_format'),
    }

def _edit_create_response(client, verb, id, name, cluster_id, def_id):
    response = client.invoke('zato.definition.jms-wmq.get-by-id', {'id':def_id, 'cluster_id': cluster_id})
    return_data = {'id': id,
                   'message': 'Successfully {0} the JMS WebSphere MQ channel [{1}]'.format(verb, name),
                   'def_name': response.data.name}

    return HttpResponse(dumps(return_data), content_type='application/javascript')

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-jms-wmq'
    template = 'zato/channel/jms_wmq.html'
    service_name = 'zato.channel.jms-wmq.get-list'
    output_class = ChannelWMQ

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'queue', 'def_name', 'def_id', 'service_name', 'data_format')
        output_repeated = True

    def handle(self):
        create_form = CreateForm()
        edit_form = EditForm(prefix='edit')

        if self.req.zato.cluster_id:
            def_ids = get_definition_list(self.req.zato.client, self.req.zato.cluster, 'jms-wmq')
            create_form.set_def_id(def_ids)
            edit_form.set_def_id(def_ids)

        return {
            'create_form': create_form,
            'edit_form': edit_form,
        }

@method_allowed('POST')
def create(req):
    try:
        response = req.zato.client.invoke('zato.channel.jms-wmq.create', _get_edit_create_message(req.POST))
        return _edit_create_response(req.zato.client, 'created', response.data.id, req.POST['name'], req.POST['cluster_id'], req.POST['def_id'])
    except Exception, e:
        msg = 'Could not create a JMS WebSphere MQ channel, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)


@method_allowed('POST')
def edit(req):
    try:
        req.zato.client.invoke('zato.channel.jms-wmq.edit', _get_edit_create_message(req.POST, 'edit-'))
        return _edit_create_response(req.zato.client, 'updated', req.POST['id'], req.POST['edit-name'], req.POST['cluster_id'], req.POST['edit-def_id'])
    except Exception, e:
        msg = 'Could not update the JMS WebSphere MQ channel, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

class Delete(_Delete):
    url_name = 'channel-jms-wmq-delete'
    error_message = 'Could not delete the JMS WebSphere MQ channel'
    service_name = 'zato.channel.jms-wmq.delete'
