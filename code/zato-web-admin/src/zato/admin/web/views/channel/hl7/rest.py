# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.admin.web.forms.channel.hl7.rest import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, get_outconn_rest_list, Index as _Index
from zato.common.api import CONNECTION, DATA_FORMAT, HL7, URL_TYPE
from zato.common.json_internal import dumps
from zato.common.model import HL7Channel

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-hl7-rest'
    template = 'zato/channel/hl7/rest.html'
    service_name = 'zato.http-soap.get-list'
    output_class = HL7Channel
    paginate = True

    def get_initial_input(self):
        return {
            'connection': CONNECTION.CHANNEL,
            'transport': URL_TYPE.PLAIN_HTTP,
            'data_format': DATA_FORMAT.HL7
        }

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'is_active', 'is_internal', 'hl7_version', 'url_path', 'service_name', 'security_name', \
            'security_id', 'data_format'
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
        input_required = 'name', 'is_active', 'is_internal', 'hl7_version', 'url_path', 'service', 'security', 'data_format'
        output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['connection'] = CONNECTION.CHANNEL
        initial_input_dict['transport'] = URL_TYPE.PLAIN_HTTP
        initial_input_dict['data_format'] = HL7.Const.Version.v2.id

# ################################################################################################################################

    def success_message(self, item):
        return 'Successfully {} HL7 REST channel `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'channel-hl7-rest-create'
    service_name = 'zato.http-soap.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'channel-hl7-rest-edit'
    form_prefix = 'edit-'
    service_name = 'zato.http-soap.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'channel-hl7-rest-delete'
    error_message = 'Could not delete HL7 REST channel'
    service_name = 'zato.http-soap.delete'

# ################################################################################################################################
# ################################################################################################################################
