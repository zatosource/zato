# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.security.jwt import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, \
     method_allowed
from zato.common.odb.model import JWT

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'security-jwt'
    template = 'zato/security/jwt.html'
    service_name = 'zato.security.jwt.get-list'
    output_class = JWT
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'is_active', 'username', 'ttl'
        output_optional = 'is_rate_limit_active', 'rate_limit_type', 'rate_limit_def', 'rate_limit_check_parent_def'
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
        input_required = 'name', 'is_active', 'username', 'ttl'
        input_optional = 'is_rate_limit_active', 'rate_limit_type', 'rate_limit_def', 'rate_limit_check_parent_def'
        output_required = 'id', 'name'

    def success_message(self, item):
        return 'Successfully {} JWT definition `{}`'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'security-jwt-create'
    service_name = 'zato.security.jwt.create'

class Edit(_CreateEdit):
    url_name = 'security-jwt-edit'
    form_prefix = 'edit-'
    service_name = 'zato.security.jwt.edit'

class Delete(_Delete):
    url_name = 'security-jwt-delete'
    error_message = 'Could not delete the JWT definition'
    service_name = 'zato.security.jwt.delete'

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.security.jwt.change-password')
