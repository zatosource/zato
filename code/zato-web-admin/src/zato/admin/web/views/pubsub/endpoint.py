# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from json import dumps
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms.pubsub.endpoint import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.odb.model import PubSubEndpoint

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-endpoint'
    template = 'zato/pubsub/endpoint.html'
    service_name = 'endpoint1.get-list'
    output_class = PubSubEndpoint
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_internal', 'role', 'is_active')
        output_optional = ('topic_patterns', 'queue_patterns', 'security_id', 'ws_channel_id', 'hook_service_id')
        output_repeated = True

    def handle(self):

        if self.req.zato.cluster_id:
            sec_list = self.get_sec_def_list('basic_auth').def_items
            sec_list.extend(self.get_sec_def_list('jwt'))
            sec_list.extend(self.get_sec_def_list('vault_conn_sec'))
            ws_channel_list = result = self.req.zato.client.invoke(
                'zato.channel.web-socket.get-list', {'cluster_id': self.req.zato.cluster_id})
        else:
            sec_list = []
            ws_channel_list = []

        return {
            'create_form': CreateForm(sec_list, ws_channel_list, req=self.req),
            'edit_form': EditForm(sec_list, ws_channel_list, prefix='edit', req=self.req),
        }

# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_internal', 'role', 'is_active')
        input_optional = ('topic_patterns', 'queue_patterns', 'security_id', 'ws_channel_id', 'hook_service_id')
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Successfully {} the pub/sub endpoint `{}`'.format(self.verb, item.name)

# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'pubsub-endpoint-create'
    service_name = 'endpoint1.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'pubsub-endpoint-edit'
    form_prefix = 'edit-'
    service_name = 'endpoint1.edit'

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'pubsub-endpoint-delete'
    error_message = 'Could not delete the pub/sub endpoint'
    service_name = 'endpoint1.delete'

# ################################################################################################################################
