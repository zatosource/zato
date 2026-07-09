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
from zato.admin.web.forms.outgoing.ibm_mq import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, \
     method_allowed

# Bunch
from zato.common.ext.bunch import Bunch

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-ibm-mq'
    template = 'zato/outgoing/ibm-mq.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active', 'address', 'queue_manager', 'mq_channel_name', 'queue'
    output_optional = 'username', 'ssl', 'cipher_spec', 'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file'
    output_repeated = True

    def handle(self):
        return {
            'show_search_form': True,
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm(),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'address', 'queue_manager', 'mq_channel_name', 'queue'
    input_optional = 'is_active', 'username', 'ssl', 'cipher_spec', 'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file'
    output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_IBM_MQ
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outconn'] = True

    def success_message(self, item):
        return 'Successfully {} outgoing IBM MQ connection `{}`'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'out-ibm-mq-create'
    service_name = 'zato.generic.connection.create'

class Edit(_CreateEdit):
    url_name = 'out-ibm-mq-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

class Delete(_Delete):
    url_name = 'out-ibm-mq-delete'
    error_message = 'Could not delete outgoing IBM MQ connection'
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
