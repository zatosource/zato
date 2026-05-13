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
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.admin.web.util import get_pubsub_security_definitions
# Bunch
from zato.common.ext.bunch import Bunch

# ################################################################################################################################

logger = logging.getLogger(__name__)

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

    def handle(self):
        create_form = CreateForm()
        edit_form = EditForm(prefix='edit')

        return {
            'create_form': create_form,
            'edit_form': edit_form,
            'show_search_form': True,
        }

# ################################################################################################################################

class GetSecurityDefinitions(View):
    url_name = 'pubsub-permission-get-security-definitions'

    def get(self, request):
        form_type = request.GET.get('form_type', 'edit')
        choices = get_pubsub_security_definitions(request, form_type, 'permission')
        return JsonResponse({'security_definitions': choices})

# ################################################################################################################################

class _CreateEdit(CreateEdit):

    method_allowed = 'POST'

    def get_form_kwargs(self):
        response = self.req.zato.client.invoke('zato.security.basic-auth.get-list', {
            'cluster_id': self.req.zato.cluster_id,
        })

        choices = []
        if response.ok:
            for item in response.data:
                choices.append((item['id'], item['name']))

        return {'sec_base_choices': choices}

    def _parse_pattern_to_topics(self, pattern):
        """ Parse 'pub=X\nsub=Y' pattern string into pub_topics and sub_topics lists.
        """
        pub_topics = []
        sub_topics = []
        for line in (pattern or '').splitlines():
            line = line.strip()
            if line.startswith('pub='):
                pub_topics.append(line[4:])
            elif line.startswith('sub='):
                sub_topics.append(line[4:])
        return pub_topics, sub_topics

    def _get_input_dict(self):
        input_dict = super()._get_input_dict()
        pattern = input_dict.pop('pattern', '')
        input_dict.pop('access_type', None)
        pub_topics, sub_topics = self._parse_pattern_to_topics(pattern)
        input_dict['pub_topics'] = pub_topics
        input_dict['sub_topics'] = sub_topics
        return input_dict

# ################################################################################################################################

class Create(_CreateEdit):
    action = 'create'
    error_message = 'Could not create the PubSub permission'
    url_name = 'pubsub-permission-create'
    service_name = 'zato.pubsub.permission.create'
    form_class = CreateForm

    input_required = 'sec_base_id',
    input_optional = 'cluster_id', 'pub_topics', 'sub_topics'
    output_required = 'id', 'security'

    def success_message(self, item):
        return 'Successfully created the PubSub permission'

# ################################################################################################################################

class Edit(_CreateEdit):
    action = 'edit'
    error_message = 'Could not update the PubSub permission'
    url_name = 'pubsub-permission-edit'
    service_name = 'zato.pubsub.permission.edit'
    form_class = EditForm
    form_prefix = 'edit-'

    input_required = 'id', 'sec_base_id'
    input_optional = 'cluster_id', 'pub_topics', 'sub_topics'
    output_required = 'id', 'security'

    def success_message(self, item):

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

class Delete(_Delete):
    url_name = 'pubsub-permission-delete'
    error_message = 'Could not delete the PubSub permission'
    service_name = 'zato.pubsub.permission.delete'

    def success_message(self, item):
        return 'Successfully deleted the PubSub permission'

# ################################################################################################################################
