# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.security.vault.connection import CreateForm, EditForm
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
        output_optional = ('token', 'service_id', 'service_name')
        output_repeated = True

    def on_before_append_item(self, item):
        item.token = item.token or ''
        item.default_auth_method = item.default_auth_method or ''
        return item

    def handle(self):

        return {
            'create_form': CreateForm(self.req),
            'edit_form': EditForm(self.req, prefix='edit'),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('id', 'name', 'is_active', 'url',  'default_auth_method',  'timeout',  'allow_redirects', 'sec_type',
            'tls_verify', 'cluster_id')
        input_optional = ('token', 'service_id')
        output_required = ('id', 'service_name')

    def post_process_return_data(self, return_data):
        if self.input.service_id:
            response = self.req.zato.client.invoke('zato.service.get-by-id', {
                'id': self.input.service_id,
                'cluster_id': self.req.zato.cluster_id
            })

            return_data['service_id'] = response.data.id
            return_data['service_name'] = response.data.name

        return return_data

    def success_message(self, item):
        return 'Successfully {} Vault connection `{}`'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'security-vault-conn-create'
    service_name = 'zato.security.vault.connection.create'

class Edit(_CreateEdit):
    url_name = 'security-vault-conn-edit'
    form_prefix = 'edit-'
    service_name = 'zato.security.vault.connection.edit'

class Delete(_Delete):
    url_name = 'security-vault-conn-delete'
    error_message = 'Could not delete the role permission'
    service_name = 'zato.security.vault.connection.delete'
