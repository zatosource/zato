# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.security.tls.key_cert import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import TLSKeyCertSecurity

logger = logging.getLogger(__name__)

class Index(_Index):
    output_class = TLSKeyCertSecurity
    url_name = 'security-tls-key-cert'
    template = 'zato/security/tls/key-cert.html'
    service_name = 'zato.security.tls.key-cert.get-list'
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'info', 'auth_data', 'is_active')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'auth_data', 'is_active')
        output_required = ('id', 'name', 'info')

    def success_message(self, item):
        return 'Successfully {} the TLS key/cert pair [{}]'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'security-tls-key-cert-create'
    service_name = 'zato.security.tls.key-cert.create'

class Edit(_CreateEdit):
    url_name = 'security-tls-key-cert-edit'
    form_prefix = 'edit-'
    service_name = 'zato.security.tls.key-cert.edit'

class Delete(_Delete):
    url_name = 'security-tls-key-cert-delete'
    error_message = 'Could not delete the TLS key/cert pair'
    service_name = 'zato.security.tls.key-cert.delete'
