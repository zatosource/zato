# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.admin.web.forms.cloud.microsoft_365 import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, \
    method_allowed, ping_connection
from zato.common.api import GENERIC, generic_attrs
from zato.common.model.microsoft_365 import Microsoft365ConfigObject

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'cloud-microsoft-365'
    template = 'zato/cloud/microsoft-365.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = Microsoft365ConfigObject
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id', 'type_'
        output_required = 'id', 'name', 'is_active', 'client_id', 'secret_value', 'scopes', 'tenant_id'
        output_optional = generic_attrs
        output_repeated = True

# ################################################################################################################################

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'id', 'name', 'is_active', 'client_id', 'secret_value', 'scopes', 'tenant_id'
        output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_365
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outgoing'] = True
        initial_input_dict['is_outconn'] = False
        initial_input_dict['sec_use_rbac'] = False
        initial_input_dict['recv_timeout'] = 250
        initial_input_dict['pool_size'] = 20

# ################################################################################################################################

    def success_message(self, item):
        return 'Successfully {} Microsoft 365 cloud connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'cloud-microsoft-365-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'cloud-microsoft-365-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'cloud-microsoft-365-delete'
    error_message = 'Could not delete Microsoft 365 connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def reset_oauth2_scopes(req):

    reset_oauth2_scopes_url_step_2 = req.POST['reset_oauth2_scopes_url_step_2']

    data = {
        'id': req.POST['id'],
        'password1': reset_oauth2_scopes_url_step_2,
        'password2': reset_oauth2_scopes_url_step_2,
        'type_': GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_365,
    }

    return _change_password(req, 'zato.generic.connection.change-password', success_msg='OAuth2 scopes reset', data=data)

# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id):
    return ping_connection(req, 'zato.generic.connection.ping', id, 'Microsoft 365 connection')

# ################################################################################################################################
