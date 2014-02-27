# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from json import dumps
from traceback import format_exc

# Django
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template.response import TemplateResponse

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
        output_required = ('id', 'name', 'is_active', 'last_seen', 'max_backlog', 'current_depth', 'sub_key', 'delivery_mode')
        output_optional = ('callback',)
        output_repeated = True

    def handle(self):
        create_form = CreateForm()
        edit_form = EditForm(prefix='edit')

        if self.req.zato.cluster_id:
            client_ids = self.req.zato.client.invoke('zato.security.get-list', {'cluster_id': self.req.zato.cluster.id})
            create_form.set_client_id(client_ids.data)

        return {
            'create_form': create_form,
            'edit_form': edit_form,
            'DEFAULT_MAX_BACKLOG': PUB_SUB.DEFAULT_MAX_BACKLOG
        }

    def _handle_item_list(self, item_list):
        super(Index, self)._handle_item_list(item_list)
        for item in self.items:
            if item.last_seen:
                item.last_seen = from_utc_to_user(item.last_seen + '+00:00', self.req.zato.user_profile)

# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('id', 'cluster_id', 'client_id', 'is_active', 'topic_name', 'max_backlog', 'delivery_mode')
        input_optional = ('callback',)
        output_required = ('id', 'name', 'last_seen', 'sub_key')

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

        client_id = self.req.POST.get('id')
        if client_id:
            response = self.req.zato.client.invoke('zato.pubsub.consumers.get-info', {'id': client_id})

            if response.ok:
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
