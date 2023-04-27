# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.vendors.keysight_vision import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, \
    method_allowed, ping_connection
from zato.common.api import Wrapper_Type
from zato.common.model.keysight_ import KeysightVisionConfigObject

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'vendors-keysight-vision'
    template = 'zato/vendors/keysight-vision.html'
    service_name = 'dev.generic.rest-wrapper.get-list'
    output_class = KeysightVisionConfigObject
    paginate = True
    wrapper_type = Wrapper_Type.Keysight_Vision

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'is_active', 'host', 'username', 'sec_tls_ca_cert_id'
        output_repeated = True

# ################################################################################################################################

    def handle(self):
        return {
            'create_form': CreateForm(req=self.req),
            'edit_form': EditForm(req=self.req, prefix='edit'),
            'change_password_form': ChangePasswordForm()
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'id', 'name', 'is_active', 'host', 'username', 'sec_tls_ca_cert_id', 'password'
        output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['wrapper_type'] = Wrapper_Type.Keysight_Vision

# ################################################################################################################################

    def success_message(self, item):
        return 'Successfully {} Keysight Vision Series connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'vendors-keysight-vision-create'
    service_name = 'dev.generic.rest-wrapper.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'vendors-keysight-vision-edit'
    form_prefix = 'edit-'
    service_name = 'dev.generic.rest-wrapper.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'vendors-keysight-vision-delete'
    error_message = 'Could not delete Keysight Vision Series connection'
    service_name = 'dev.generic.rest-wrapper.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'dev.generic.rest-wrapper.change-password', success_msg='Password updated')

# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id):
    return ping_connection(req, 'dev.generic.rest-wrapper.ping', id, 'Keysight Vision Series connection')

# ################################################################################################################################
