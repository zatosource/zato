# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.cloud.aws import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, \
    method_allowed, ping_connection
from zato.common.api import AWS, GENERIC, generic_attrs
from zato.common.model.aws_ import AWSConfigObject

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'cloud-aws'
    template = 'zato/cloud/aws.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = AWSConfigObject
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active'
    output_optional = generic_attrs + ('region', 'access_key_id', 'endpoint_url')
    output_repeated = True

# ################################################################################################################################

    def handle(self) -> 'strdict':
        return {
            'show_search_form': True,
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm()
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'is_active', 'region', 'access_key_id', 'endpoint_url'
    output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict:'strdict') -> 'None':
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.CLOUD_AWS
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outgoing'] = True
        initial_input_dict['is_outconn'] = False
        initial_input_dict['recv_timeout'] = AWS.Default.Recv_Timeout
        initial_input_dict['pool_size'] = AWS.Default.Pool_Size

# ################################################################################################################################

    def success_message(self, item:'any_') -> 'str':
        return f'Successfully {self.verb} AWS cloud connection `{item.name}`'

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'cloud-aws-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'cloud-aws-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'cloud-aws-delete'
    error_message = 'Could not delete AWS connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def change_password(req:'any_') -> 'any_':
    return _change_password(req, 'zato.generic.connection.change-password', success_msg='Secret access key updated')

# ################################################################################################################################

@method_allowed('POST')
def ping(req:'any_', id:'int', cluster_id:'int') -> 'any_':
    return ping_connection(req, 'zato.generic.connection.ping', id, 'AWS connection')

# ################################################################################################################################
