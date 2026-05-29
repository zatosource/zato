# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Django
from django.http import JsonResponse
from django.views import View

# Zato
from zato.admin.web.forms.pubsub.permission import CreateForm, EditForm
from zato.admin.web.util import get_pubsub_security_definitions
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.ext.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpRequest
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-permission'
    template = 'zato/pubsub/permission.html'
    service_name = 'zato.pubsub.permission.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id',
    output_required = 'id', 'name', 'pattern', 'access_type', 'sec_base_id', 'subscription_count'
    output_repeated = True

    def handle(self) -> 'anydict':
        create_form = CreateForm()
        edit_form = EditForm(prefix='edit')

        out = {
            'create_form': create_form,
            'edit_form': edit_form,
            'show_search_form': True,
        }

        return out

# ################################################################################################################################
# ################################################################################################################################

class GetSecurityDefinitions(View):
    url_name = 'pubsub-permission-get-security-definitions'

    def get(self, request:'HttpRequest') -> 'JsonResponse':
        form_type = request.GET.get('form_type', 'edit')
        choices = get_pubsub_security_definitions(request, form_type, 'permission')

        out = JsonResponse({'security_definitions': choices})
        return out

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):

    method_allowed = 'POST'

    def get_form_kwargs(self) -> 'anydict':
        response = self.req.zato.client.invoke('zato.security.basic-auth.get-list', {
            'cluster_id': self.req.zato.cluster_id,
        })

        choices = []
        if response.ok:
            for item in response.data:
                choices.append((item['id'], item['name']))

        out = {'sec_base_choices': choices}
        return out

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    action = 'create'
    error_message = 'Could not create the PubSub permission'
    url_name = 'pubsub-permission-create'
    service_name = 'zato.pubsub.permission.create'
    form_class = CreateForm

    input_required = 'sec_base_id', 'pattern', 'access_type'
    input_optional = 'cluster_id',
    output_required = 'id', 'security'

    def success_message(self, item:'any_') -> 'str':
        return 'Successfully created the PubSub permission'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    action = 'edit'
    error_message = 'Could not update the PubSub permission'
    url_name = 'pubsub-permission-edit'
    service_name = 'zato.pubsub.permission.edit'
    form_class = EditForm
    form_prefix = 'edit-'

    input_required = 'id', 'sec_base_id', 'pattern', 'access_type'
    input_optional = 'cluster_id',
    output_required = 'id', 'security'

    def success_message(self, item:'any_') -> 'str':

        sec_base_id = self.input.sec_base_id

        response = self.req.zato.client.invoke('zato.security.get-list', {
            'cluster_id': self.req.zato.cluster_id,
        })

        if response.ok:
            for sec_def in response.data:
                if sec_def.id == int(sec_base_id):
                    return f'Successfully updated permission `{sec_def.name}`'
        else:
            raise Exception(response)

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'pubsub-permission-delete'
    error_message = 'Could not delete the PubSub permission'
    service_name = 'zato.pubsub.permission.delete'

    def success_message(self, item:'any_') -> 'str':
        return 'Successfully deleted the PubSub permission'

# ################################################################################################################################
# ################################################################################################################################
