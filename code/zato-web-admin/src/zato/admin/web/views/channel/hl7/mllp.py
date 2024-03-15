# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.admin.web.forms.channel.hl7.mllp import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.api import GENERIC, generic_attrs, HL7
from zato.common.model.hl7 import HL7MLLPConfigObject

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-hl7-mllp'
    template = 'zato/channel/hl7/mllp.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = HL7MLLPConfigObject
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id', 'type_'
        output_required = 'id', 'name', 'is_active', 'is_internal', 'service', 'security_name', 'address'
        output_optional = ('should_parse_on_input', 'should_validate', 'should_return_errors') + generic_attrs
        output_repeated = True

# ################################################################################################################################

    def handle(self):
        return {
            'create_form': CreateForm(req=self.req),
            'edit_form': EditForm(prefix='edit', req=self.req),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'name', 'is_internal', 'service', 'address'
        input_optional = ('is_active', 'should_parse_on_input', 'should_validate', 'should_return_errors') + generic_attrs
        output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = True
        initial_input_dict['is_outconn'] = False
        initial_input_dict['sec_use_rbac'] = False
        initial_input_dict['pool_size'] = 1
        initial_input_dict['should_validate'] = True
        initial_input_dict['should_parse_on_input'] = True
        initial_input_dict['data_format'] = HL7.Const.Version.v2.id
        initial_input_dict['hl7_version'] = HL7.Const.Version.v2.id
        initial_input_dict['data_encoding'] = 'utf-8'

# ################################################################################################################################

    def pre_process_item(self, name, value):
        if name == 'recv_timeout':
            return int(value)
        else:
            return value

# ################################################################################################################################

    def success_message(self, item):
        return 'Successfully {} HL7 MLLP channel `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'channel-hl7-mllp-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'channel-hl7-mllp-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'channel-hl7-mllp-delete'
    error_message = 'Could not delete HL7 MLLP channel'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################
