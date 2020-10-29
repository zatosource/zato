# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.security.oauth import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, \
     CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.api import NONCE_STORE
from zato.common.odb.model import OAuth

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'security-oauth'
    template = 'zato/security/oauth.html'
    service_name = 'zato.security.oauth.get-list'
    output_class = OAuth
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'username',
            'proto_version', 'sig_method', 'max_nonce_log')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm(),
            'default_max_nonce_log': NONCE_STORE.DEFAULT_MAX_LOG,
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'username',
            'proto_version', 'sig_method', 'max_nonce_log')
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Successfully {0} the OAuth definition [{1}]'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'security-oauth-create'
    service_name = 'zato.security.oauth.create'

class Edit(_CreateEdit):
    url_name = 'security-oauth-edit'
    form_prefix = 'edit-'
    service_name = 'zato.security.oauth.edit'

class Delete(_Delete):
    url_name = 'security-oauth-delete'
    error_message = 'Could not delete the OAuth definition'
    service_name = 'zato.security.oauth.delete'

@method_allowed('POST')
def change_secret(req):
    return _change_password(req, 'zato.security.oauth.change-password')
