# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms.outgoing.hl7.fhir import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, \
    invoke_action_handler, method_allowed, ping_connection, SecurityList
from zato.common.api import GENERIC, generic_attrs, SEC_DEF_TYPE
from zato.common.model.hl7 import HL7FHIRConfigObject

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'outgoing-hl7-fhir'
    template = 'zato/outgoing/hl7/fhir.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = HL7FHIRConfigObject
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id', 'type_'
        output_required = 'id', 'name', 'is_active', 'is_internal', 'address', 'security_id', 'sec_tls_ca_cert_id', \
            'pool_size', 'sec_def_type_name', 'security_name'
        output_optional = ('extra',) + generic_attrs
        output_repeated = True

# ################################################################################################################################

    def handle(self):

        security_list = SecurityList.from_service(
            self.req.zato.client,
            self.cluster_id,
            sec_type = [SEC_DEF_TYPE.BASIC_AUTH, SEC_DEF_TYPE.OAUTH],
            needs_def_type_name_label=True
        )

        return {
            'create_form': CreateForm(self.req, security_list),
            'edit_form': EditForm(self.req, security_list, prefix='edit'),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'name', 'is_internal', 'address', 'security_id', 'sec_tls_ca_cert_id', 'pool_size'
        input_optional = ('is_active', 'extra') + generic_attrs
        output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outgoing'] = True
        initial_input_dict['is_outconn'] = False
        initial_input_dict['sec_use_rbac'] = False
        initial_input_dict['recv_timeout'] = 250

# ################################################################################################################################

    def pre_process_input_dict(self, input_dict):
        input_dict['pool_size'] = int(input_dict['pool_size'])

# ################################################################################################################################

    def success_message(self, item):
        return 'Successfully {} HL7 FHIR outgoing connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'outgoing-hl7-fhir-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'outgoing-hl7-fhir-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'outgoing-hl7-fhir-delete'
    error_message = 'Could not delete HL7 FHIR outgoing connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def invoke(req, conn_id, max_wait_time, conn_name, conn_slug):

    return_data = {
        'conn_id': conn_id,
        'conn_name': conn_name,
        'conn_slug': conn_slug,
        'conn_type': GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP,
        'timeout': max_wait_time,
        'cluster_id': req.zato.cluster_id,
    }

    return TemplateResponse(req, 'zato/outgoing/hl7/fhir-invoke.html', return_data)

# ################################################################################################################################

@method_allowed('POST')
def invoke_action(req, conn_name):
    return invoke_action_handler(req, 'zato.generic.connection.invoke', ('conn_name', 'conn_type', 'request_data', 'timeout'))

# ################################################################################################################################

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.generic.connection.change-password', success_msg='Password updated')

# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id):
    return ping_connection(req, 'zato.generic.connection.ping', id, 'HL7 FHIR connection')

# ################################################################################################################################
