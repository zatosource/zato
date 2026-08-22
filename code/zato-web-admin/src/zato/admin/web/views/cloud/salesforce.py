# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.admin.web.forms.cloud.salesforce import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed, ping_connection
from zato.common.api import GENERIC, generic_attrs, SALESFORCE
from zato.common.model.salesforce import SalesforceConfigObject

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'cloud-salesforce'
    template = 'zato/cloud/salesforce/index.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = SalesforceConfigObject
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active', 'is_internal', 'address', 'username', 'api_version', \
        'password', 'consumer_key', 'consumer_secret'
    output_optional = generic_attrs
    output_repeated = True

# ################################################################################################################################

    def handle(self) -> 'anydict':
        return {
            'show_search_form': True,
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'is_internal', 'address', 'username', 'api_version', \
        'password', 'consumer_key', 'consumer_secret'
    input_optional = ('is_active', 'pool_size') + generic_attrs
    output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict:'anydict') -> 'None':
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.CLOUD_SALESFORCE
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outgoing'] = True
        initial_input_dict['is_outconn'] = False
        initial_input_dict['recv_timeout'] = SALESFORCE.Default.Recv_Timeout
        initial_input_dict['pool_size'] = SALESFORCE.Default.Pool_Size

# ################################################################################################################################

    def success_message(self, item:'any_') -> 'str':
        out = f'Successfully {self.verb} Salesforce cloud connection `{item.name}`'
        return out

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'cloud-salesforce-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'cloud-salesforce-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'cloud-salesforce-delete'
    error_message = 'Could not delete Salesforce connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def ping(req:'any_', id:'any_', cluster_id:'any_') -> 'any_':
    out = ping_connection(req, 'zato.generic.connection.ping', id, 'Salesforce connection')
    return out

# ################################################################################################################################
