# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Django
from django.http import HttpResponse

# Zato
from zato.common.api import GENERIC
from zato.admin.web.forms.channel.kafka import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed

# Bunch
from bunch import Bunch

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-kafka'
    template = 'zato/channel/kafka.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active', 'address', 'topic', 'group_id', 'service'
    output_optional = 'ssl', 'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file'
    output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(req=self.req),
            'edit_form': EditForm(prefix='edit', req=self.req),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'address', 'topic', 'group_id', 'service'
    input_optional = 'is_active', 'ssl', 'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file'
    output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.CHANNEL_KAFKA
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = True
        initial_input_dict['is_outconn'] = False

    def success_message(self, item):
        return 'Successfully {} Kafka channel `{}`'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'channel-kafka-create'
    service_name = 'zato.generic.connection.create'

class Edit(_CreateEdit):
    url_name = 'channel-kafka-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

class Delete(_Delete):
    url_name = 'channel-kafka-delete'
    error_message = 'Could not delete Kafka channel'
    service_name = 'zato.generic.connection.delete'

@method_allowed('GET')
def import_demo_config(req):
    response = req.zato.client.invoke('zato.server.invoker', {'func_name': 'import_demo_kafka'})
    out = HttpResponse()
    out.content = str(response.data)
    return out
