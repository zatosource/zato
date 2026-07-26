# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms.outgoing.hl7.mllp import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, invoke_action_handler, method_allowed
from zato.common.api import GENERIC, generic_attrs
from zato.common.model.hl7 import HL7MLLPOutconnConfigObject

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'outgoing-hl7-mllp'
    template = 'zato/outgoing/hl7/mllp.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = HL7MLLPOutconnConfigObject
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active', 'is_internal', 'security_name', 'address', 'pool_size'
    output_optional = (
        'should_log_messages', 'logging_level',
        'max_msg_size', 'read_buffer_size', 'recv_timeout',
        'start_seq', 'end_seq', 'max_wait_time',
        'max_retries', 'backoff_base_seconds', 'backoff_cap_seconds', 'backoff_jitter_percent',
        'circuit_breaker_threshold_percent', 'circuit_breaker_window_seconds', 'circuit_breaker_reset_seconds',
        'tls_cert_path', 'tls_key_path', 'tls_ca_path',
    ) + generic_attrs
    output_repeated = True

# ################################################################################################################################

    def handle(self):
        return {
            'show_search_form': True,
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'is_internal', 'address'
    input_optional = (
        'is_active', 'pool_size',
        'should_log_messages', 'logging_level',
        'max_msg_size', 'read_buffer_size', 'recv_timeout',
        'start_seq', 'end_seq', 'max_wait_time',
        'max_retries', 'backoff_base_seconds', 'backoff_cap_seconds', 'backoff_jitter_percent',
        'circuit_breaker_threshold_percent', 'circuit_breaker_window_seconds', 'circuit_breaker_reset_seconds',
        'tls_cert_path', 'tls_key_path', 'tls_ca_path',
    ) + generic_attrs
    output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict:'stranydict') -> 'None':
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outgoing'] = True
        initial_input_dict['is_outconn'] = True
        initial_input_dict['sec_use_rbac'] = False

# ################################################################################################################################

    def success_message(self, item:'any_') -> 'str':
        out = 'Successfully {} HL7 MLLP outgoing connection `{}`'.format(self.verb, item.name)
        return out

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'outgoing-hl7-mllp-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'outgoing-hl7-mllp-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'outgoing-hl7-mllp-delete'
    error_message = 'Could not delete HL7 MLLP outgoing connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def invoke(
    req:'any_',
    conn_id:'str',
    max_wait_time:'str',
    conn_name:'str',
    conn_slug:'str',
    ) -> 'TemplateResponse':

    return_data = {
        'conn_id': conn_id,
        'conn_name': conn_name,
        'conn_slug': conn_slug,
        'conn_type': GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP,
        'timeout': max_wait_time,
        'cluster_id': req.zato.cluster_id,
    }

    out = TemplateResponse(req, 'zato/outgoing/hl7/mllp-invoke.html', return_data)
    return out

# ################################################################################################################################

@method_allowed('POST')
def invoke_action(req:'any_', conn_name:'str') -> 'any_':
    field_names = ('conn_name', 'conn_type', 'request_data', 'timeout')

    out = invoke_action_handler(req, 'zato.generic.connection.invoke', field_names)
    return out

# ################################################################################################################################
