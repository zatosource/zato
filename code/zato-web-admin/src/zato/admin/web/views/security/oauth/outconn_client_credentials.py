# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.security.oauth.outconn_client_credentials import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, \
     CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.odb.model import OAuth

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'security-oauth-outconn-client-credentials'
    template = 'zato/security/oauth/outconn-client-credentials.html'
    service_name = 'zato.security.oauth.get-list'
    output_class = OAuth
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'is_active', 'username', 'auth_server_url', 'scopes', \
            'client_id_field', 'client_secret_field', 'grant_type', 'extra_fields', 'data_format'
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm(),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'name', 'is_active', 'username', 'auth_server_url', 'scopes', \
            'client_id_field', 'client_secret_field', 'grant_type', 'extra_fields', 'data_format'
        output_required = 'id', 'name'

    def success_message(self, item):
        return 'Bearer token definition `{}` {} successfully'.format(item.name, self.verb)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'security-oauth-outconn-client-credentials-create'
    service_name = 'zato.security.oauth.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'security-oauth-outconn-client-credentials-edit'
    form_prefix = 'edit-'
    service_name = 'zato.security.oauth.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'security-oauth-outconn-client-credentials-delete'
    error_message = 'Bearer token definition could not be deleted'
    service_name = 'zato.security.oauth.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def change_secret(req):
    return _change_password(req, 'zato.security.oauth.change-password', success_msg='Secret updated')

# ################################################################################################################################
# ################################################################################################################################
