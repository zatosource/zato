# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Bunch
from zato.common.ext.bunch import Bunch

# Zato
from zato.admin.web.forms.outgoing.mongodb import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed, ping_connection, SKIP_VALUE
from zato.common.api import GENERIC

# ################################################################################################################################

_fields_required = ('name', 'server_list')
_fields_optional = ('is_active', 'username', 'auth_source', 'replica_set', 'app_name', 'pool_size_max', 'connect_timeout',
    'server_select_timeout', 'is_tls_enabled', 'tls_ca_certs_file', 'tls_cert_key_file', 'is_tls_validation_enabled')

# Fields that the MongoDB client expects to be integers
_int_fields = ('pool_size_max', 'connect_timeout', 'server_select_timeout')

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-mongodb'
    template = 'zato/outgoing/mongodb.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = ('id',) + _fields_required
    output_optional = _fields_optional
    output_repeated = True

    def handle(self):
        return {
            'show_search_form': True,
            'create_form': CreateForm(req=self.req),
            'edit_form': EditForm(prefix='edit', req=self.req),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = _fields_required
    input_optional = _fields_optional + ('secret',)
    output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_MONGODB
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outconn'] = True
        initial_input_dict['pool_size'] = 1 # We use pool_size_max from opaque attributes

    def on_after_set_input(self):

        # Convert to integers, as expected by the MongoDB client
        for name in _int_fields:
            if value := self.input.get(name):
                self.input[name] = int(value)

    def pre_process_item(self, name, value):
        # An empty password on input means the current one is to be kept,
        # which is why the field cannot be sent to the backend at all.
        if name == 'secret' and not value:
            return SKIP_VALUE
        return value

    def success_message(self, item):
        return 'Successfully {} outgoing MongoDB connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'out-mongodb-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'out-mongodb-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'out-mongodb-delete'
    error_message = 'Could not delete outgoing MongoDB connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id):
    return ping_connection(req, 'zato.generic.connection.ping', id, 'MongoDB connection')

# ################################################################################################################################
