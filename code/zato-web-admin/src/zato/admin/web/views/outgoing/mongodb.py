# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.common.api import GENERIC
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.outgoing.mongodb import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, \
     method_allowed, ping_connection
from zato.common.odb.model import GenericConn

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-mongodb'
    template = 'zato/outgoing/mongodb.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = GenericConn
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id', 'type_')

        output_required = ('id', 'name', 'server_list', 'pool_size_max', 'connect_timeout',
        'socket_timeout', 'server_select_timeout', 'wait_queue_timeout', 'max_idle_time', 'hb_frequency')

        output_optional = ('is_active',  'username', 'app_name', 'replica_set', 'auth_source',  'auth_mechanism',
            'is_tz_aware',  'document_class', 'compressor_list', 'zlib_level', 'write_to_replica', 'write_timeout',
            'is_write_journal_enabled', 'is_write_fsync_enabled', 'read_pref_type', 'read_pref_tag_list',
            'read_pref_max_stale', 'is_tls_enabled', 'tls_private_key_file', 'tls_cert_file', 'tls_ca_certs_file',
            'tls_crl_file', 'tls_version', 'tls_validate', 'tls_pem_passphrase', 'is_tls_match_hostname_enabled',
            'tls_ciphers')

        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm()
        }

# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'server_list', 'pool_size_max', 'connect_timeout',
        'socket_timeout', 'server_select_timeout', 'wait_queue_timeout', 'max_idle_time', 'hb_frequency')

        input_optional = ('is_active',  'username', 'app_name', 'replica_set', 'auth_source',  'auth_mechanism',
            'is_tz_aware',  'document_class', 'compressor_list', 'zlib_level', 'write_to_replica', 'write_timeout',
            'is_write_journal_enabled', 'is_write_fsync_enabled', 'should_retry_write', 'read_pref_type', 'read_pref_tag_list',
            'read_pref_max_stale', 'is_tls_enabled', 'tls_private_key_file', 'tls_cert_file', 'tls_ca_certs_file',
            'tls_crl_file', 'tls_version', 'tls_validate', 'tls_pem_passphrase', 'is_tls_match_hostname_enabled',
            'tls_ciphers')

        output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_MONGODB
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outconn'] = True
        initial_input_dict['sec_use_rbac'] = False
        initial_input_dict['pool_size'] = 1 # We use pool_size_max from opaque attributes

    def on_after_set_input(self):
        # Convert to integers, as expected by MongoDB driver
        for name in 'hb_frequency', 'max_idle_time', 'write_to_replica', 'read_pref_max_stale', 'zlib_level':
            value = self.input.get(name, None)
            if value is not None:
                self.input[name] = int(value)

    def success_message(self, item):
        return 'Successfully {} outgoing MongoDB connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'out-mongodb-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'out-mongodb-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'out-mongodb-delete'
    error_message = 'Could not delete outgoing MongoDB connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.generic.connection.change-password')

# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id):
    return ping_connection(req, 'zato.generic.connection.ping', id, 'MongoDB connection')

# ################################################################################################################################
