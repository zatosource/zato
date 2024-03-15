# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.common.api import GENERIC, LDAP
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.outgoing.ldap import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, \
     method_allowed, ping_connection
from zato.common.odb.model import GenericConn

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-ldap'
    template = 'zato/outgoing/ldap.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = GenericConn
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id', 'type_')
        output_required = ('id', 'name', 'is_active', 'get_info', 'ip_mode', 'connect_timeout', 'auto_bind', 'server_list',
            'pool_size', 'pool_exhaust_timeout', 'pool_keep_alive', 'pool_max_cycles', 'pool_lifetime', 'pool_ha_strategy',
            'username', 'auth_type')
        output_optional = ('is_active', 'use_tls', 'pool_name', 'use_sasl_external', 'is_read_only', 'is_stats_enabled',
            'should_check_names', 'use_auto_range', 'should_return_empty_attrs', 'is_tls_enabled', 'tls_private_key_file',
            'tls_cert_file', 'tls_ca_certs_file', 'tls_version', 'tls_ciphers', 'tls_validate', 'sasl_mechanism')
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
        input_required = ('name', 'get_info', 'ip_mode', 'connect_timeout', 'auto_bind', 'server_list', 'pool_size',
            'pool_exhaust_timeout', 'pool_keep_alive', 'pool_max_cycles', 'pool_lifetime', 'pool_ha_strategy', 'username',
            'auth_type')
        input_optional = ('is_active', 'use_tls', 'pool_name', 'use_sasl_external', 'is_read_only', 'is_stats_enabled',
            'should_check_names', 'use_auto_range', 'should_return_empty_attrs', 'is_tls_enabled', 'tls_private_key_file',
            'tls_cert_file', 'tls_ca_certs_file', 'tls_version', 'tls_ciphers', 'tls_validate', 'sasl_mechanism')
        output_required = ('id', 'name')

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_LDAP
        initial_input_dict['ip_mode'] = LDAP.IP_MODE.IP_SYSTEM_DEFAULT.id
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outconn'] = True
        initial_input_dict['sec_use_rbac'] = False

    def success_message(self, item):
        return 'Successfully {} outgoing LDAP connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'out-ldap-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'out-ldap-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'out-ldap-delete'
    error_message = 'Could not delete outgoing LDAP connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.generic.connection.change-password')

# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id):
    return ping_connection(req, 'zato.generic.connection.ping', id, 'LDAP connection')

# ################################################################################################################################
