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
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.channel.ibm_mq import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, \
     method_allowed

# Bunch
from zato.common.ext.bunch import Bunch

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-ibm-mq'
    template = 'zato/channel/ibm-mq.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active', 'address', 'queue_manager', 'mq_channel_name', 'queue', 'service'
    output_optional = 'username', 'ssl', 'cipher_spec', 'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file', 'remove_jms_headers'
    output_repeated = True

    def handle(self):
        return {
            'show_search_form': True,
            'create_form': CreateForm(req=self.req),
            'edit_form': EditForm(prefix='edit', req=self.req),
            'change_password_form': ChangePasswordForm(),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'address', 'queue_manager', 'mq_channel_name', 'queue', 'service'
    input_optional = 'is_active', 'username', 'ssl', 'cipher_spec', 'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file', \
        'remove_jms_headers'
    output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.CHANNEL_IBM_MQ
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = True
        initial_input_dict['is_outconn'] = False

    def success_message(self, item):
        return 'Successfully {} IBM MQ channel `{}`'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'channel-ibm-mq-create'
    service_name = 'zato.generic.connection.create'

class Edit(_CreateEdit):
    url_name = 'channel-ibm-mq-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

class Delete(_Delete):
    url_name = 'channel-ibm-mq-delete'
    error_message = 'Could not delete IBM MQ channel'
    service_name = 'zato.generic.connection.delete'

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.generic.connection.change-password')

@method_allowed('GET')
def import_demo_config(req):
    response = req.zato.client.invoke('zato.server.invoker', {'func_name': 'import_demo_ibm_mq'})
    out = HttpResponse()
    out.content = str(response.data)
    return out
