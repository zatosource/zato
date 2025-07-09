# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging

# Django
from django.http import HttpResponse

# Zato
from zato.admin.web.forms.pubsub.subscription import CreateForm, EditForm
from zato.admin.web.util import get_pubsub_security_definitions
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed, get_outconn_rest_list
from zato.common.odb.model import PubSubSubscription

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-subscription'
    template = 'zato/pubsub/subscription.html'
    service_name = 'zato.pubsub.subscription.get-list'
    output_class = PubSubSubscription
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id',
        output_required = 'id', 'sub_key', 'is_active', 'created', 'topic_name', 'sec_name', 'delivery_type'
        output_repeated = True

    def handle(self):
        create_form = CreateForm(req=self.req)
        edit_form = EditForm(prefix='edit', req=self.req)
        return {
            'create_form': create_form,
            'edit_form': edit_form,
        }

# ################################################################################################################################
# ################################################################################################################################

class Create(CreateEdit):
    method_allowed = 'POST'
    url_name = 'pubsub-subscription-create'
    service_name = 'zato.pubsub.subscription.create'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'cluster_id', 'topic_id_list', 'sec_base_id', 'delivery_type'
        input_optional = 'is_active', 'rest_push_endpoint_id'
        output_required = 'id', 'sub_key', 'is_active', 'created', 'topic_name', 'sec_name', 'delivery_type'

    def handle(self):

        logger.info('[DEBUG] Create.handle: Request method=%s', self.req.method)
        logger.info('[DEBUG] Create.handle: Request POST data=%s', dict(self.req.POST))
        logger.info('[DEBUG] Create.handle: Request GET data=%s', dict(self.req.GET))

        # Check topic_id specifically
        topic_id_list = self.req.POST.getlist('create-topic_id')
        logger.info('[DEBUG] Create.handle: topic_id_list type=%s, value=%s', type(topic_id_list), topic_id_list)

    def _get_input_dict(self):

        input_dict = {}

        # Map topic_id form field (which can be multiple) to topic_id_list service input
        if self.req.method == 'POST':
            topic_ids = self.req.POST.getlist('create-topic_id')
            input_dict['topic_id_list'] = topic_ids
            logger.info('[DEBUG] Create._get_input_dict: Mapped topic_id_list=%s', topic_ids)

        return input_dict

    def pre_process_input_dict(self, input_dict):
        """Override to handle form field mapping before service call"""
        super().pre_process_input_dict(input_dict)

        # Extract topic IDs from form POST data
        if self.req.method == 'POST':
            topic_ids = self.req.POST.getlist('topic_id')
            input_dict['topic_id_list'] = topic_ids
            logger.info('[DEBUG] Create.pre_process_input_dict: Set topic_id_list=%s', topic_ids)

            # Map other form fields
            field_mapping = {
                'sec_base_id': 'sec_base_id',
                'delivery_type': 'delivery_type',
                'is_active': 'is_active',
                'rest_push_endpoint_id': 'rest_push_endpoint_id'
            }

            for form_field, service_field in field_mapping.items():
                value = self.req.POST.get(form_field)
                if value:
                    if service_field == 'is_active':
                        input_dict[service_field] = value == 'on'
                    else:
                        input_dict[service_field] = value
                    logger.info('[DEBUG] Create.pre_process_input_dict: Set %s=%s', service_field, input_dict[service_field])

    def success_message(self, item):
        return 'Successfully created pub/sub subscription'

# ################################################################################################################################
# ################################################################################################################################

class Edit(CreateEdit):
    method_allowed = 'POST'
    url_name = 'pubsub-subscription-edit'
    service_name = 'zato.pubsub.subscription.edit'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'sub_key', 'cluster_id', 'topic_id_list', 'sec_base_id', 'delivery_type'
        input_optional = 'is_active', 'rest_push_endpoint_id'
        output_required = 'id', 'sub_key', 'topic_name', 'sec_name', 'delivery_type', 'is_active'

    def handle(self):
        logger.info('[DEBUG] Edit.handle: Request method=%s', self.req.method)
        logger.info('[DEBUG] Edit.handle: Request POST data=%s', dict(self.req.POST))
        logger.info('[DEBUG] Edit.handle: Request GET data=%s', dict(self.req.GET))

        # Check topic_id specifically
        topic_id_list = self.req.POST.getlist('edit-topic_id')
        logger.info('[DEBUG] Edit.handle: topic_id_list type=%s, value=%s', type(topic_id_list), topic_id_list)


    def _get_input_dict(self):

        input_dict = {}

        # Map topic_id form field (which can be multiple) to topic_id_list service input
        if self.req.method == 'POST':
            topic_ids = self.req.POST.getlist('edit-topic_id')
            input_dict['topic_id_list'] = topic_ids
            logger.info('[DEBUG] Edit._get_input_dict: Mapped topic_id_list=%s', topic_ids)

        return input_dict

    def pre_process_input_dict(self, input_dict):

        super().pre_process_input_dict(input_dict)

        # Extract topic IDs from form POST data
        if self.req.method == 'POST':
            topic_ids = self.req.POST.getlist('edit-topic_id')
            input_dict['topic_id_list'] = topic_ids
            logger.info('[DEBUG] Edit.pre_process_input_dict: Set topic_id_list=%s', topic_ids)

            # Map other form fields
            field_mapping = {
                'edit-sub_key': 'sub_key',
                'edit-sec_base_id': 'sec_base_id',
                'edit-delivery_type': 'delivery_type',
                'edit-is_active': 'is_active',
                'edit-rest_push_endpoint_id': 'rest_push_endpoint_id'
            }

            for form_field, service_field in field_mapping.items():
                value = self.req.POST.get(form_field)
                if value:
                    if service_field == 'is_active':
                        input_dict[service_field] = value == 'on'
                    else:
                        input_dict[service_field] = value
                    logger.info('[DEBUG] Edit.pre_process_input_dict: Set %s=%s', service_field, input_dict[service_field])

    def success_message(self, item):
        return 'Successfully updated pub/sub subscription'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'pubsub-subscription-delete'
    error_message = 'Could not delete pub/sub subscription'
    service_name = 'zato.pubsub.subscription.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_security_definitions(req):
    """ Retrieves a list of security definitions for pubsub subscriptions.
    """
    form_type = req.GET.get('form_type', 'create')

    try:
        security_definitions = get_pubsub_security_definitions(req, form_type, 'subscription')

        return HttpResponse(
            json.dumps({
                'msg': 'Security definitions retrieved successfully',
                'security_definitions': security_definitions
            }),
            content_type='application/json'
        )
    except Exception as e:
        return HttpResponse(
            json.dumps({
                'error': str(e) or 'Error retrieving security definitions'
            }),
            content_type='application/json',
            status=500
        )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_topics(req):
    """ Retrieves a list of topics for pubsub subscriptions.
    """
    cluster_id = req.GET.get('cluster_id')
    form_type = req.GET.get('form_type', 'create')

    logger.info('VIEW get_topics: received request with cluster_id=%s, form_type=%s', cluster_id, form_type)

    try:
        # Call the service directly like in other views
        response = req.zato.client.invoke('zato.pubsub.topic.get-list', {
            'cluster_id': cluster_id
        })

        topics = []
        if response and hasattr(response, 'data'):
            for item in response.data:
                topics.append({
                    'id': item.id,
                    'name': item.name
                })

        logger.info('VIEW get_topics: returning %d topics', len(topics))

        return HttpResponse(
            json.dumps({
                'msg': 'Topics retrieved successfully',
                'topics': topics
            }),
            content_type='application/json'
        )
    except Exception as e:
        logger.error('VIEW get_topics: error=%s', e)
        return HttpResponse(
            json.dumps({
                'error': str(e) or 'Error retrieving topics'
            }),
            content_type='application/json',
            status=500
        )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_rest_endpoints(req):
    """ Retrieves a list of REST outgoing connections for pubsub subscriptions.
    """
    cluster_id = req.GET.get('cluster_id')
    form_type = req.GET.get('form_type', 'create')

    logger.info('VIEW get_rest_endpoints: received request with cluster_id=%s, form_type=%s', cluster_id, form_type)

    try:
        rest_endpoints = get_outconn_rest_list(req, name_to_id=False)
        endpoints_list = []

        for endpoint_id, endpoint_name in rest_endpoints.items():
            endpoints_list.append({
                'id': endpoint_id,
                'name': endpoint_name
            })

        logger.info('VIEW get_rest_endpoints: returning %d endpoints', len(endpoints_list))

        return HttpResponse(
            json.dumps({
                'msg': 'REST endpoints retrieved successfully',
                'rest_endpoints': endpoints_list
            }),
            content_type='application/json'
        )
    except Exception as e:
        logger.error('VIEW get_rest_endpoints: error=%s', e)
        return HttpResponse(
            json.dumps({
                'error': str(e) or 'Error retrieving REST endpoints'
            }),
            content_type='application/json',
            status=500
        )

# ################################################################################################################################
# ################################################################################################################################
