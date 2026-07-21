# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Bunch
from zato.common.ext.bunch import Bunch

# Zato
from zato.admin.web.forms.security.spnego import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'security-spnego'
    template = 'zato/security/spnego.html'
    service_name = 'zato.security.spnego.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id',
    output_required = 'id', 'name'
    output_optional = 'is_active', 'principal', 'keytab_path', 'target_spn', 'needs_delegation'
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

    input_required = 'name', 'principal', 'keytab_path'
    input_optional = 'target_spn', 'needs_delegation'
    output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['is_active'] = True

    def success_message(self, item):
        return 'Successfully {} Kerberos definition `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'security-spnego-create'
    service_name = 'zato.security.spnego.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'security-spnego-edit'
    form_prefix = 'edit-'
    service_name = 'zato.security.spnego.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'security-spnego-delete'
    error_message = 'Could not delete the Kerberos definition'
    service_name = 'zato.security.spnego.delete'

# ################################################################################################################################
# ################################################################################################################################
