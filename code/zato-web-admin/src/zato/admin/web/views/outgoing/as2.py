# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.outgoing.as2 import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, \
    invoke_action_handler, method_allowed, ping_connection
from zato.admin.web.views.as2_keystore import get_expiry_info
from zato.common.api import AS2, GENERIC, generic_attrs
from zato.common.ext.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

# The identities the two parties exchange messages under - required to route anything at all.
_as2_required_field_names = ('endpoint_url', 'as2_from', 'as2_to')

# Text and select fields, stored in the connection's opaque attributes.
_as2_string_field_names = ('isa_qualifier', 'isa_id', 'gs_id', 'unb_id', 'sign_algorithm', 'encryption_algorithm',
    'mdn_mode', 'async_mdn_url', 'subject', 'content_type', 'as2_version', 'content_transfer_encoding',
    'http_transfer_mode', 'inbound_topic', 'inbound_service', 'as2_partner_cert', 'as2_partner_next_cert',
    'as2_partner_next_cert_from', 'as2_signing_key', 'as2_signing_cert_chain', 'as2_decryption_key',
    'as2_next_decryption_key', 'as2_next_decryption_cert', 'as2_peer_signing_cert', 'as2_peer_encryption_cert',
    'as2_trust_anchors')

# Checkbox fields - they arrive from the form as 'on' or not at all and need real booleans.
_as2_bool_field_names = ('sign', 'encrypt', 'compress', 'compress_before_signing', 'mdn_signed', 'preserve_filename',
    'verify_tls', 'force_base64', 'prevent_canonicalization', 'warn_on_duplicate_filename')

# Numeric fields - an empty input means zero, which keeps the partnership's own default in place.
_as2_int_field_names = ('http_timeout_seconds', 'chunked_threshold_bytes', 'ack_overdue_after', 'resend_max_retries')

_as2_field_names = _as2_required_field_names + _as2_string_field_names + _as2_bool_field_names + _as2_int_field_names

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-as2'
    template = 'zato/outgoing/as2.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active'
    output_optional = ('username', 'pool_size') + _as2_field_names + generic_attrs
    output_repeated = True

# ################################################################################################################################

    def handle(self):
        return {
            'show_search_form': True,
            'create_form': CreateForm(req=self.req),
            'edit_form': EditForm(prefix='edit', req=self.req),
            'change_password_form': ChangePasswordForm(),
        }

# ################################################################################################################################

    def on_before_append_item(self, item):

        # The expiry of the partner's pasted certificate is computed for display only -
        # an expired partner certificate is the single most common AS2 operational failure.
        partner_cert = getattr(item, 'as2_partner_cert', '')
        expiry = get_expiry_info(partner_cert)

        item.cert_expiry = expiry['date']
        item.cert_expiry_is_warning = expiry['is_warning']

        # The audit log of this connection's exchanges is filed under its AS2 identity pair.
        as2_from = getattr(item, 'as2_from', '')
        as2_to = getattr(item, 'as2_to', '')
        item.audit_log_object_name = f'{as2_from.strip()}:{as2_to.strip()}'

        return item

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = ('name',) + _as2_required_field_names
    input_optional = ('is_active', 'username', 'pool_size') + _as2_string_field_names + _as2_bool_field_names + \
        _as2_int_field_names + generic_attrs
    output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_AS2
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outconn'] = True
        initial_input_dict['is_outgoing'] = True

# ################################################################################################################################

    def pre_process_input_dict(self, input_dict):

        # Checkboxes arrive as 'on' or not at all - the backend expects real booleans ..
        for name in _as2_bool_field_names:
            input_dict[name] = bool(input_dict.get(name))

        # .. numeric fields arrive as strings, with an empty input meaning zero,
        # which keeps the partnership's own default in place ..
        for name in _as2_int_field_names:
            if value := input_dict.get(name):
                input_dict[name] = int(value)
            else:
                input_dict[name] = 0

        # .. and the pool size defaults to the connection type's own setting.
        if value := input_dict.get('pool_size'):
            input_dict['pool_size'] = int(value)
        else:
            input_dict['pool_size'] = AS2.Default.Pool_Size

# ################################################################################################################################

    def success_message(self, item):
        return 'Successfully {} outgoing AS2 connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'out-as2-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'out-as2-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'out-as2-delete'
    error_message = 'Could not delete outgoing AS2 connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.generic.connection.change-password')

# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id):
    return ping_connection(req, 'zato.generic.connection.ping', id, 'AS2 connection')

# ################################################################################################################################

@method_allowed('POST')
def send_test_message(req):
    out = invoke_action_handler(req, 'zato.outgoing.as2.send-test-message', ('name',))
    return out

# ################################################################################################################################
# ################################################################################################################################
