# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.admin.web.forms.pubsub.client import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import PubSubPermission

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-client'
    template = 'zato/pubsub/client.html'
    service_name = 'zato.pubsub.client.get-list'
    output_class = PubSubPermission
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'pattern', 'access_type', 'is_active'
        output_repeated = True

    def handle(self):
        # Get existing basic auth definitions for the dropdown
        response = self.req.zato.client.invoke('zato.security.basic-auth.get-list', {
            'cluster_id': self.req.zato.cluster_id,
        })

        choices = []
        if response.ok:
            for item in response.data:
                choices.append((item['id'], item['name']))

        create_form = CreateForm(sec_base_choices=choices)
        edit_form = EditForm(sec_base_choices=choices, prefix='edit')

        return {
            'create_form': create_form,
            'edit_form': edit_form,
        }

# ################################################################################################################################

class _CreateEdit(CreateEdit):

    method_allowed = 'POST'
    form_prefix = 'pubsub_permission'

    def get_form_kwargs(self):
        # Get existing basic auth definitions for the dropdown
        response = self.req.zato.client.invoke('zato.security.basic-auth.get-list', {
            'cluster_id': self.req.zato.cluster_id,
        })

        choices = []
        if response.ok:
            for item in response.data:
                choices.append((item['id'], item['name']))

        return {'sec_base_choices': choices}

# ################################################################################################################################

class Create(_CreateEdit):
    action = 'create'
    error_message = 'Could not create the PubSub client assignment'
    success_message = 'Successfully created the PubSub client assignment'
    url_name = 'pubsub-client-create'
    service_name = 'zato.pubsub.client.create'
    form_class = CreateForm

# ################################################################################################################################

class Edit(_CreateEdit):
    action = 'edit'
    error_message = 'Could not update the PubSub client assignment'
    success_message = 'Successfully updated the PubSub client assignment'
    url_name = 'pubsub-client-edit'
    service_name = 'zato.pubsub.client.edit'
    form_class = EditForm

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'pubsub-client-delete'
    error_message = 'Could not delete the PubSub client assignment'
    success_message = 'Successfully deleted the PubSub client assignment'
    service_name = 'zato.pubsub.client.delete'

# ################################################################################################################################
