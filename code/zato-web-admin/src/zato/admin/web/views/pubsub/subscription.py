# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Bunch
from bunch import Bunch

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.forms import Initial_Choices_Dict_Attrs
from zato.admin.web.forms.pubsub.subscription import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, django_url_reverse, Index as _Index, slugify
from zato.common.api import PUBSUB
from zato.common.odb.model import PubSubEndpoint

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-subscription'
    template = 'zato/pubsub/subscription.html'
    service_name = 'zato.pubsub.endpoint.get-endpoint-summary-list'
    output_class = PubSubEndpoint
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        input_optional = ('topic_id',)
        output_required = ('id', 'endpoint_name', 'endpoint_type', 'subscription_count', 'is_active', 'is_internal')
        output_optional = ('security_id', 'sec_type', 'sec_name', 'ws_channel_id', 'ws_channel_name',
            'service_id', 'service_name', 'last_seen', 'last_deliv_time', 'role', 'endpoint_type_name')
        output_repeated = True

    def on_before_append_item(self, item): # type: ignore

        if item.last_seen:
            item.last_seen = from_utc_to_user(item.last_seen+'+00:00', self.req.zato.user_profile)

        if item.last_deliv_time:
            item.last_deliv_time = from_utc_to_user(item.last_deliv_time+'+00:00', self.req.zato.user_profile)

        return item # type: ignore

    def handle(self): # type: ignore

        data_list = Bunch()
        data_list.security_list = []
        data_list.service_list = []
        select_data_target = Bunch()
        topic_name = None
        create_form = None
        edit_form = None

        for endpoint_type in PUBSUB.ENDPOINT_TYPE():
            select_data_target[endpoint_type] = [Initial_Choices_Dict_Attrs]

        if self.req.zato.cluster_id:

            for item in self.items: # type: ignore
                targets = select_data_target[item.endpoint_type] # type: ignore

                id_key = 'id'
                name_key = 'name'
                endpoint_name = item.endpoint_name # type: ignore

                targets.append({id_key:item.id, name_key:endpoint_name})

            # Security definitions
            data_list.security_list = self.get_sec_def_list('basic_auth').def_items # type: ignore

            # Services
            data_list.service_list = self.req.zato.client.invoke('zato.service.get-list', {
                'cluster_id': self.req.zato.cluster_id
            }).data

            data_list.out_amqp_list = self.req.zato.client.invoke('zato.outgoing.amqp.get-list', {
                'cluster_id': self.req.zato.cluster_id
            }).data

            # Topic
            if self.input.topic_id:
                topic_name = self.req.zato.client.invoke('zato.pubsub.topic.get', {
                    'cluster_id': self.req.zato.cluster_id,
                    'id': self.input.topic_id
                }).data.response.name

            create_form = CreateForm(self.req, data_list)
            edit_form = EditForm(self.req, data_list, prefix='edit')

        return {
            'create_form': create_form,
            'edit_form': edit_form,
            'select_data_target': select_data_target,
            'topic_name': topic_name,
            'topic_id': self.input.topic_id,
        } # type: ignore

# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('endpoint_id', 'is_active', 'cluster_id', 'server_id', 'is_internal')
        input_optional = ('has_gd', 'topic_list_json', 'endpoint_type', 'endpoint_id', 'active_status',
            'delivery_method', 'delivery_data_format', 'delivery_batch_size', 'wrap_one_msg_in_list', 'delivery_max_retry',
            'delivery_err_should_block', 'wait_sock_err', 'wait_non_sock_err', 'out_amqp_id', 'amqp_exchange',
            'amqp_routing_key', 'files_directory_list', 'ftp_directory_list', 'out_rest_http_soap_id', 'rest_delivery_endpoint',
            'service_id', 'sms_twilio_from', 'sms_twilio_to_list', 'smtp_is_html', 'smtp_subject', 'smtp_from', 'smtp_to_list',
            'smtp_body', 'out_soap_http_soap_id', 'soap_delivery_endpoint', 'out_http_method')
        output_required = ('id',)

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict): # type: ignore

        topic_list = []

        for key in sorted(self.req.POST):
            if key.startswith('topic_checkbox_'):
                topic_name = key.replace('topic_checkbox_', '')
                topic_list.append(topic_name)

        initial_input_dict['topic_list_json'] = topic_list

# ################################################################################################################################

    def post_process_return_data(self, return_data): # type: ignore

        response = self.req.zato.client.invoke('zato.pubsub.endpoint.get-endpoint-summary', {
            'cluster_id': self.req.zato.cluster_id,
            'endpoint_id': self.input.endpoint_id,
        }).data

        if response['last_seen']:
            response['last_seen'] = from_utc_to_user(response['last_seen']+'+00:00', self.req.zato.user_profile)

        if response['last_deliv_time']:
            response['last_deliv_time'] = from_utc_to_user(response['last_deliv_time']+'+00:00', self.req.zato.user_profile)

        response['pubsub_endpoint_queues_link'] = \
            django_url_reverse('pubsub-endpoint-queues',
                    kwargs={
                        'cluster_id':self.req.zato.cluster_id,
                        'endpoint_id':response['id'],
                        'name_slug':slugify(response['endpoint_name'])}
                    ),

        return_data.update(response)

    def success_message(self, _ignored_item): # type: ignore
        return 'Pub/sub configuration updated successfully'

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
    id_elem = 'endpoint_id'
    url_name = 'pubsub-subscription-delete-all'
    error_message = 'Could not delete pub/sub subscriptions'
    service_name = 'zato.pubsub.subscription.delete-all'

# ################################################################################################################################
