# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.admin.web.forms.outgoing.hl7.mllp import CreateForm, EditForm
from zato.admin.web.views import get_security_id_from_select, CreateEdit, Delete as _Delete, Index as _Index, \
     invoke_action_handler, method_allowed, SecurityList
from zato.common.odb.model import AWSS3

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'outgoing-hl7-mllp'
    template = 'zato/outgoing/hl7/mllp.html'
    service_name = 'zato.outgoing.hl7.mllp.get-list'
    output_class = AWSS3
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'pool_size', 'address', 'debug_level', 'suppr_cons_slashes',
            'content_type', 'security_id', 'encrypt_at_rest', 'storage_class')
        output_optional = ('metadata_', 'bucket')
        output_repeated = True

    def handle(self):
        if self.req.zato.cluster_id:
            sec_list = SecurityList.from_service(self.req.zato.client, self.req.zato.cluster.id, ['aws'])
        else:
            sec_list = []

        return {
            'create_form': CreateForm(sec_list),
            'edit_form': EditForm(sec_list, prefix='edit'),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('cluster_id', 'name', 'is_active', 'pool_size', 'address', 'debug_level', 'suppr_cons_slashes',
            'content_type', 'security_id', 'encrypt_at_rest', 'storage_class')
        input_optional = ('metadata_', 'bucket')
        output_required = ('id', 'name')

    def on_after_set_input(self):
        self.input_dict['security_id'] = get_security_id_from_select(self.input, '', 'security_id')

    def success_message(self, item):
        return 'HL7 MLLP connection `{}` {} successfully'.format(item.name, self.verb)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'outgoing-hl7-mllp-create'
    service_name = 'zato.outgoing.hl7.mllp.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'outgoing-hl7-mllp-edit'
    form_prefix = 'edit-'
    service_name = 'zato.outgoing.hl7.mllp.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'outgoing-hl7-mllp-delete'
    error_message = 'HL7 MLLP connection could not be deleted'
    service_name = 'zato.outgoing.hl7.mllp.delete'

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################

@method_allowed('GET')
def invoke(req, conn_id, pub_client_id, ext_client_id, ext_client_name, channel_id, channel_name):

    return_data = {
        'conn_id': conn_id,
        'pub_client_id': pub_client_id,
        'pub_client_id_html': pub_client_id.replace('.', '-'),
        'ext_client_id': ext_client_id,
        'ext_client_name': ext_client_name,
        'channel_id': channel_id,
        'channel_name': channel_name,
        'cluster_id': req.zato.cluster_id,
    }

    return TemplateResponse(req, 'zato/outgoing/hl7/mllp.html', return_data)

# ################################################################################################################################

@method_allowed('POST')
def invoke_action(req, pub_client_id):
    return invoke_action_handler(req, 'zato.outgoing.hl7.mllp.invoke', ('id', 'pub_client_id', 'request_data', 'timeout'))

# ################################################################################################################################
