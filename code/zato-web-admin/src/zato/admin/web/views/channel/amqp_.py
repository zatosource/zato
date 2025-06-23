# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError

# Zato
from zato.admin.web.forms.channel.amqp_ import CreateForm, EditForm
from zato.admin.web.views import Delete as _Delete, Index as _Index, method_allowed
from zato.common.json_internal import dumps
from zato.common.odb.model import ChannelAMQP

logger = logging.getLogger(__name__)

def _get_edit_create_message(params, prefix=''):
    """ Creates a base dictionary which can be used by both 'edit' and 'create' actions.
    """
    return {
        'id': params.get('id'),
        'cluster_id': params['cluster_id'],
        'name': params[prefix + 'name'],
        'is_active': bool(params.get(prefix + 'is_active')),
        'queue': params[prefix + 'queue'],
        'address': params[prefix + 'address'],
        'username': params.get(prefix + 'username'),
        'password': params.get(prefix + 'password'),
        'consumer_tag_prefix': params[prefix + 'consumer_tag_prefix'],
        'service': params[prefix + 'service'],
        'pool_size': params.get(prefix + 'pool_size'),
        'ack_mode': params.get(prefix + 'ack_mode'),
        'prefetch_count': params.get(prefix + 'prefetch_count'),
        'data_format': params.get(prefix + 'data_format'),
    }

def _edit_create_response(client, verb, id, name):
    return_data = {'id': id, 'message': 'Successfully {} AMQP channel `{}`'.format(verb, name)}
    return HttpResponse(dumps(return_data), content_type='application/javascript')

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-amqp'
    template = 'zato/channel/amqp.html'
    service_name = 'zato.channel.amqp.get-list'
    output_class = ChannelAMQP
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'address', 'username', 'password', 'queue', 'consumer_tag_prefix', 'service_name',
            'pool_size', 'ack_mode','prefetch_count', 'data_format')
        output_repeated = True

    def handle(self):
        create_form = CreateForm(req=self.req)
        edit_form = EditForm(prefix='edit', req=self.req)

        return {
            'create_form': create_form,
            'edit_form': edit_form,
        }

@method_allowed('POST')
def create(req):
    try:
        response = req.zato.client.invoke('zato.channel.amqp.create', _get_edit_create_message(req.POST))
        return _edit_create_response(req.zato.client, 'created', response.data.id, req.POST['name'])
    except Exception:
        msg = 'Could not create AMQP channel, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)


@method_allowed('POST')
def edit(req):
    try:
        req.zato.client.invoke('zato.channel.amqp.edit', _get_edit_create_message(req.POST, 'edit-'))
        return _edit_create_response(req.zato.client, 'updated', req.POST['id'], req.POST['edit-name'])

    except Exception:
        msg = 'Could not update AMQP channel, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

class Delete(_Delete):
    url_name = 'channel-amqp-delete'
    error_message = 'Could not delete AMQP channel'
    service_name = 'zato.channel.amqp.delete'
