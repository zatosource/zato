# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.security.tls.ca_cert import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import TLSCACert

logger = logging.getLogger(__name__)

class Index(_Index):
    output_class = TLSCACert
    url_name = 'security-tls-ca-cert'
    template = 'zato/security/tls/ca-cert.html'
    service_name = 'zato.security.tls.ca-cert.get-list'
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'value', 'info', 'is_active')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'value', 'is_active')
        output_required = ('id', 'name', 'info')

    def success_message(self, item):
        return 'Successfully {} the TLS CA certificate [{}]'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'security-tls-ca-cert-create'
    service_name = 'zato.security.tls.ca-cert.create'

class Edit(_CreateEdit):
    url_name = 'security-tls-ca-cert-edit'
    form_prefix = 'edit-'
    service_name = 'zato.security.tls.ca-cert.edit'

class Delete(_Delete):
    url_name = 'security-tls-ca-cert-delete'
    error_message = 'Could not delete the TLS CA certificate'
    service_name = 'zato.security.tls.ca-cert.delete'
