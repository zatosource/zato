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
        output_required = 'id', 'name', 'pattern', 'access_type'
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
    error_message = 'Could not create the PubSub API client'
    url_name = 'pubsub-client-create'
    service_name = 'zato.pubsub.client.create'
    form_class = CreateForm
    
    def success_message(self, item):
        return 'Successfully created the PubSub API client'

    class SimpleIO:
        input_required = 'sec_base_id', 'pattern', 'access_type'
        input_optional = 'cluster_id'
        output_required = 'id', 'name'
        output_optional = ()

# ################################################################################################################################

class Edit(_CreateEdit):
    action = 'edit'
    error_message = 'Could not update the PubSub API client'
    url_name = 'pubsub-client-edit'
    service_name = 'zato.pubsub.client.edit'
    form_class = EditForm
    
    def success_message(self, item):
        return 'Successfully updated the PubSub API client'

    class SimpleIO:
        input_required = 'id', 'sec_base_id', 'pattern', 'access_type'
        input_optional = 'cluster_id'
        output_required = ()
        output_optional = ()

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'pubsub-client-delete'
    error_message = 'Could not delete the PubSub API client'
    service_name = 'zato.pubsub.client.delete'
    
    def success_message(self, item):
        return 'Successfully deleted the PubSub API client'

# ################################################################################################################################
