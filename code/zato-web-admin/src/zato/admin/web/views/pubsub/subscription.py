# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Bunch
from bunch import Bunch

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.forms.pubsub.subscription import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import PubSubEndpoint

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-subscription'
    template = 'zato/pubsub/subscription.html'
    service_name = 'zato.pubsub.subscription.get-endpoint-summary-list'
    output_class = PubSubEndpoint
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'endpoint_name', 'endpoint_type', 'subscription_count', 'is_active', 'is_internal')
        output_optional = ('security_id', 'sec_type', 'sec_name', 'ws_channel_id', 'ws_channel_name',
            'service_id', 'service_name', 'last_seen', 'last_deliv_time', 'role')
        output_repeated = True

    def on_before_append_item(self, item):

        if item.last_seen:
            item.last_seen = from_utc_to_user(item.last_seen+'+00:00', self.req.zato.user_profile)

        if item.last_deliv_time:
            item.last_deliv_time = from_utc_to_user(item.last_deliv_time+'+00:00', self.req.zato.user_profile)

        return item

    def handle(self):

        data_list = Bunch()
        data_list.security_list = []
        data_list.service_list = []

        select_data_target = Bunch()

        if self.req.zato.cluster_id:

            for item in self.items:
                targets = select_data_target.setdefault(item.endpoint_type, [])
                targets.append({b'id':item.id, b'name':item.endpoint_name})

            # Security definitions
            data_list.security_list = self.get_sec_def_list('basic_auth').def_items

            # Services
            data_list.service_list = self.req.zato.client.invoke(
                'zato.service.get-list', {'cluster_id': self.req.zato.cluster_id}).data

        return {
            'create_form': CreateForm(self.req, data_list),
            'edit_form': EditForm(self.req, data_list, prefix='edit'),
            'select_data_target': select_data_target,
        }

# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('endpoint_id', 'is_active')
        input_optional = ('topic_list_text', 'topic_list_json')
        output_required = ('id',)

    def post_process_return_data(self, return_data):

        response = self.req.zato.client.invoke('zato.pubsub.subscription.get', {
            'cluster_id': self.req.zato.cluster_id,
            'id': return_data['id'],
        }).data['response']

    def success_message(self, item):
        return 'Pub/sub subscription {} successfully'.format(self.verb)

# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'pubsub-subscription-create'
    service_name = 'zato.pubsub.subscription.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'pubsub-subscription-edit'
    form_prefix = 'edit-'
    service_name = 'zato.pubsub.subscription.edit'

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'pubsub-subscription-delete'
    error_message = 'Could not delete pub/sub subscription'
    service_name = 'zato.pubsub.subscription.delete'

# ################################################################################################################################
