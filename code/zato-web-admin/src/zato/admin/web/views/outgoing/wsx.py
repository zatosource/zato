# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.outgoing.wsx import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import GenericConn

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-wsx'
    template = 'zato/outgoing/wsx.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = GenericConn
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id', 'type_')
        output_required = ('id', 'name', 'address', 'address_masked')
        output_optional = ('is_active', 'is_zato',
            'on_connect_service_id', 'on_connect_service_name', 'on_message_service_id', 'on_message_service_name',
            'on_close_service_id', 'on_close_service_name', 'subscription_list', 'security_def', 'has_auto_reconnect',
            'data_format', 'ping_interval', 'pings_missed_threshold', 'socket_read_timeout', 'socket_write_timeout')
        output_repeated = True

    def handle(self):
        if self.req.zato.get('client'):
            security_list = self.get_sec_def_list('basic_auth').def_items
        else:
            security_list = []

        return {
            'create_form': CreateForm(security_list, req=self.req),
            'edit_form': EditForm(security_list, prefix='edit', req=self.req),
            'change_password_form': ChangePasswordForm()
        }

# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'is_zato', 'address', 'on_connect_service_name', 'on_message_service_name',
            'on_close_service_name', 'subscription_list', 'security_def', 'has_auto_reconnect', 'data_format',
            'ping_interval', 'pings_missed_threshold', 'socket_read_timeout', 'socket_write_timeout')
        output_required = ('id', 'name')

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_WSX
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outconn'] = True
        initial_input_dict['pool_size'] = 1
        initial_input_dict['sec_use_rbac'] = False

    def post_process_return_data(self, return_data):

        for name in ('connect', 'message', 'close'):
            field_name = 'on_{}_service_name'.format(name)
            return_data[field_name] = self.input_dict.get(field_name)

        return return_data

    def success_message(self, item):
        return 'Successfully {} outgoing WebSocket connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'out-wsx-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'out-wsx-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'out-wsx-delete'
    error_message = 'Could not delete outgoing WebSocket connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
