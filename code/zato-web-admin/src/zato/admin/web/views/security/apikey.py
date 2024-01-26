# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.security.apikey import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.odb.model import APIKeySecurity

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'security-apikey'
    template = 'zato/security/apikey.html'
    service_name = 'zato.security.apikey.get-list'
    output_class = APIKeySecurity
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'is_active', 'username'
        output_optional = 'is_rate_limit_active', 'rate_limit_type', 'rate_limit_def', 'rate_limit_check_parent_def', 'header'
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm()
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'name', 'is_active', 'username'
        input_optional = 'is_rate_limit_active', 'rate_limit_type', 'rate_limit_def', 'rate_limit_check_parent_def'
        output_required = 'id', 'name'

    def success_message(self, item):
        return 'Successfully {} API key `{}`'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'security-apikey-create'
    service_name = 'zato.security.apikey.create'

class Edit(_CreateEdit):
    url_name = 'security-apikey-edit'
    form_prefix = 'edit-'
    service_name = 'zato.security.apikey.edit'

class Delete(_Delete):
    url_name = 'security-apikey-delete'
    error_message = 'Could not delete the API key'
    service_name = 'zato.security.apikey.delete'

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.security.apikey.change-password', success_msg='API key updated')
