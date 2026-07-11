# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.admin.web.forms.channel.as4 import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, extract_security_id, Index as _Index
from zato.admin.web.views.outgoing.as4 import get_cert_expiry
from zato.common.api import AS4, CONNECTION, SEC_DEF_TYPE_NAME, URL_TYPE, ZATO_NONE

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict

# ################################################################################################################################
# ################################################################################################################################

_as4_field_names = AS4.Common_Fields + AS4.Channel_Fields

# ################################################################################################################################
# ################################################################################################################################

class ChannelAS4ConfigObject:
    """ A config object for AS4 channels, filled in with attributes from the get-list response.
    """

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-as4'
    template = 'zato/channel/as4.html'
    service_name = 'zato.http-soap.get-list'
    output_class = ChannelAS4ConfigObject
    paginate = True

    input_required = 'cluster_id',
    output_required = 'id', 'name', 'is_active', 'is_internal', 'url_path'
    output_optional = ('service_name', 'security_id', 'security_name', 'sec_type') + _as4_field_names
    output_repeated = True

# ################################################################################################################################

    def get_initial_input(self) -> 'stranydict':

        out = {
            'connection': CONNECTION.CHANNEL,
            'transport': URL_TYPE.AS4,
        }

        return out

# ################################################################################################################################

    def on_before_append_item(self, item:'any_') -> 'any_':

        # The security definition's type name is shown next to its name -
        # the field is optional in the get-list response, so it may be missing entirely.
        if hasattr(item, 'security_id'):
            security_id = item.security_id
        else:
            security_id = None

        if security_id:
            if security_id != ZATO_NONE:
                item.sec_type_name = SEC_DEF_TYPE_NAME[item.sec_type]

        # The edit form's routing field is called service.
        if hasattr(item, 'service_name'):
            item.service = item.service_name
        else:
            item.service = ''

        # The expiry of the pasted signing certificate is computed for display only.
        if hasattr(item, 'as4_signing_cert_chain'):
            signing_cert_chain = item.as4_signing_cert_chain
        else:
            signing_cert_chain = ''

        item.as4_cert_expiry = get_cert_expiry(signing_cert_chain)

        return item

# ################################################################################################################################

    def handle(self) -> 'stranydict':
        security_list = self.get_sec_def_list(None)

        out = {
            'show_search_form': True,
            'create_form': CreateForm(security_list, req=self.req),
            'edit_form': EditForm(security_list, prefix='edit', req=self.req),
        }

        return out

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'url_path'
    input_optional = ('is_active', 'service', 'security_id') + _as4_field_names
    output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict:'anydict') -> 'None':
        initial_input_dict['connection'] = CONNECTION.CHANNEL
        initial_input_dict['transport'] = URL_TYPE.AS4
        initial_input_dict['is_internal'] = False

# ################################################################################################################################

    def pre_process_input_dict(self, input_dict:'anydict') -> 'None':
        input_dict['security_id'] = extract_security_id(input_dict)

# ################################################################################################################################

    def success_message(self, item:'any_') -> 'str':
        out = f'Successfully {self.verb} AS4 channel `{item.name}`'
        return out

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'channel-as4-create'
    service_name = 'zato.http-soap.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'channel-as4-edit'
    form_prefix = 'edit-'
    service_name = 'zato.http-soap.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'channel-as4-delete'
    error_message = 'Could not delete the AS4 channel'
    service_name = 'zato.http-soap.delete'

# ################################################################################################################################
# ################################################################################################################################
