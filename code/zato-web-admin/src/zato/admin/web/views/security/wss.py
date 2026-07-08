# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Bunch
from zato.common.ext.bunch import Bunch

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.security.wss import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, \
     method_allowed

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'security-wss'
    template = 'zato/security/wss.html'
    service_name = 'zato.security.wss.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id',
    output_required = 'id', 'name', 'is_active', 'username'
    output_optional = 'mode', 'use_digest', 'sign', 'encrypt', 'signing_key', 'signing_certificate_chain', \
        'decryption_key', 'peer_certificate', 'trust_anchors', 'issuer', 'subject', 'audience'
    output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm(),
            'show_search_form': True,
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'is_active', 'username', 'mode'
    input_optional = 'use_digest', 'sign', 'encrypt', 'signing_key', 'signing_certificate_chain', \
        'decryption_key', 'peer_certificate', 'trust_anchors', 'issuer', 'subject', 'audience'
    output_required = 'id', 'name'

    def pre_process_input_dict(self, input_dict):

        # Checkboxes arrive as 'on' or not at all - the backend expects real booleans.
        for name in ('use_digest', 'sign', 'encrypt'):
            input_dict[name] = bool(input_dict.get(name))

    def success_message(self, item):
        return 'Successfully {} WS-Security definition `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'security-wss-create'
    service_name = 'zato.security.wss.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'security-wss-edit'
    form_prefix = 'edit-'
    service_name = 'zato.security.wss.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'security-wss-delete'
    error_message = 'Could not delete the WS-Security definition'
    service_name = 'zato.security.wss.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.security.wss.change-password')

# ################################################################################################################################
# ################################################################################################################################
