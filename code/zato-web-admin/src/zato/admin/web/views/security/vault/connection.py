# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.security.vault.connection import CreateForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import VaultConnection

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    output_class = VaultConnection
    url_name = 'security-vault-conn'
    template = 'zato/security/vault/connection.html'
    service_name = 'zato.security.vault.connection.get-list'
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'url',  'default_auth_method',  'timeout',  'allow_redirects',  'tls_verify')
        output_optional = ('token', 'service_id')
        output_repeated = True

    def handle(self):

        return {
            'create_form': CreateForm(self.req)
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('id', 'name', 'url',  'default_auth_method',  'timeout',  'allow_redirects',  'tls_verify')
        input_optional = ('token', 'service_id')
        output_required = ('id', 'role_name', 'service_name', 'perm_name')

    def success_message(self, item):
        return 'Successfully {} the role permission `{}`'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'security-vault-conn-create'
    service_name = 'zato.security.vault.connection.create'

class Edit(_CreateEdit):
    url_name = 'security-vault-conn-edit'
    service_name = 'zato.security.vault.connection.edit'

class Delete(_Delete):
    url_name = 'security-vault-conn-delete'
    error_message = 'Could not delete the role permission'
    service_name = 'zato.security.vault.connection.delete'
