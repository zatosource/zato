# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Bunch
from zato.common.ext.bunch import Bunch

# Zato
from zato.admin.web.forms.security.mtls import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'security-mtls'
    template = 'zato/security/mtls.html'
    service_name = 'zato.security.mtls.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id',
    output_required = 'id', 'name'
    output_optional = 'is_active', 'cert_path', 'key_path', 'ca_certs_path', 'client_cert_fingerprint', \
        'client_cert_subject_dn'
    output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'show_search_form': True,
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name',
    input_optional = 'cert_path', 'key_path', 'ca_certs_path', 'client_cert_fingerprint', 'client_cert_subject_dn'
    output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['is_active'] = True

    def success_message(self, item):
        return 'Successfully {} mTLS definition `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'security-mtls-create'
    service_name = 'zato.security.mtls.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'security-mtls-edit'
    form_prefix = 'edit-'
    service_name = 'zato.security.mtls.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'security-mtls-delete'
    error_message = 'Could not delete the mTLS definition'
    service_name = 'zato.security.mtls.delete'

# ################################################################################################################################
# ################################################################################################################################
