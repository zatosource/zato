# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.forms.pubsub.consumers import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common import PUB_SUB
from zato.common.odb.model import PubSubConsumer

logger = logging.getLogger(__name__)

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-consumers'
    template = 'zato/pubsub/consumers/index.html'
    service_name = 'zato.pubsub.consumers.get-list'
    output_class = PubSubConsumer

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id', 'topic_name')
        output_required = ('id', 'name', 'is_active', 'sec_type', 'client_id', 'last_seen', 'max_depth', 'current_depth',
            'in_flight_depth', 'sub_key', 'delivery_mode')
        output_optional = ('callback_id',)
        output_repeated = True

    def handle(self):
        if self.req.zato.cluster_id:
            client_ids = self.req.zato.client.invoke('zato.security.get-list', {'cluster_id': self.req.zato.cluster.id}).data

            callback_ids = self.req.zato.client.invoke(
                'zato.http-soap.get-list', {
                    'cluster_id': self.req.zato.cluster.id, 'connection':'outgoing', 'transport':'plain_http'
                }).data
        else:
            client_ids = None
            callback_ids = None

        create_form = CreateForm(client_ids=client_ids, callback_ids=callback_ids)
        edit_form = EditForm(prefix='edit', callback_ids=callback_ids)

        return {
            'create_form': create_form,
            'edit_form': edit_form,
            'DEFAULT_MAX_BACKLOG': PUB_SUB.DEFAULT_MAX_BACKLOG
        }

    def _handle_item_list(self, item_list):
        super(Index, self)._handle_item_list(item_list)
        for item in self.items:
            item.callback_id = item.callback_id or ''
            if item.last_seen:
                item.last_seen = from_utc_to_user(item.last_seen + '+00:00', self.req.zato.user_profile)

# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('id', 'cluster_id', 'client_id', 'is_active', 'topic_name', 'max_depth', 'delivery_mode')
        input_optional = ('callback_id',)
        output_required = ('id', 'name', 'last_seen', 'current_depth', 'in_flight_depth', 'sub_key')

    def success_message(self, item):
        # 'message' is implemented in post_process_return_data so that we know the name of the consumer
        pass

    def post_process_return_data(self, return_data):
        is_active = False
        for name in('is_active', 'edit-is_active'):
            if name in self.req.POST:
                is_active = True
                break

        return_data['is_active'] = is_active
        return_data['topic_name'] = self.req.POST['topic_name']
        return_data['message'] = 'Successfully {} consumer `{}`'.format(self.verb, return_data['name'])

        return_data['last_seen'] = None
        return_data['current_depth'] = 0

        client_id = self.req.POST.get('id')
        if client_id:
            response = self.req.zato.client.invoke('zato.pubsub.consumers.get-info', {'id': client_id})

            if response.ok:
                return_data['current_depth'] = response.data.current_depth
                return_data['in_flight_depth'] = response.data.in_flight_depth
                return_data['sub_key'] = response.data.sub_key
                if response.data.last_seen:
                    return_data['last_seen'] = from_utc_to_user(response.data.last_seen + '+00:00', self.req.zato.user_profile)

        return return_data

# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'pubsub-consumers-create'
    service_name = 'zato.pubsub.consumers.create'

    def post_process_return_data(self, return_data):
        return_data['last_seen'] = None
        return super(Create, self).post_process_return_data(return_data)

# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'pubsub-consumers-edit'
    form_prefix = 'edit-'
    service_name = 'zato.pubsub.consumers.edit'

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'pubsub-consumers-delete'
    error_message = 'Could not delete the consumer'
    service_name = 'zato.pubsub.consumers.delete'

# ################################################################################################################################

@method_allowed('POST')
def clear_queue(req, queue_type, client_id, cluster_id):
    try:
        response = req.zato.client.invoke(
            'zato.pubsub.consumers.clear-queue', {'queue_type': queue_type, 'client_id': client_id})
        if response.ok:
            return HttpResponse('OK', content_type='application/javascript')
        else:
            raise Exception(response.details)
    except Exception, e:
        return HttpResponseServerError(format_exc(e))

# ################################################################################################################################
