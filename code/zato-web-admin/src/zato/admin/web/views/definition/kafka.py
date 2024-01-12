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
from zato.admin.web.forms.definition.kafka import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, \
     method_allowed, ping_connection
from zato.common.odb.model import GenericConn

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'definition-kafka'
    template = 'zato/definition/kafka.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = GenericConn
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id', 'type_')
        output_required = ('id', 'name', 'server_list', 'socket_timeout', 'offset_timeout', 'broker_version', 'server_list')
        output_optional = ('is_active',  'should_use_zookeeper', 'should_exclude_internal_topics', 'source_address',
            'is_tls_enabled', 'tls_private_key_file', 'tls_cert_file', 'tls_ca_certs_file', 'tls_pem_passphrase')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(req=self.req),
            'edit_form': EditForm(prefix='edit', req=self.req),
            'change_password_form': ChangePasswordForm()
        }

# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'server_list', 'socket_timeout', 'offset_timeout', 'broker_version', 'server_list')
        input_optional = ('is_active',  'should_use_zookeeper', 'should_exclude_internal_topics', 'source_address',
            'is_tls_enabled', 'tls_private_key_file', 'tls_cert_file', 'tls_ca_certs_file', 'tls_pem_passphrase')

        output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.DEF_KAFKA
        initial_input_dict['is_internal'] = False

        # This definition can be used to create connections in both directions
        initial_input_dict['is_channel'] = True
        initial_input_dict['is_outconn'] = True

        initial_input_dict['sec_use_rbac'] = False
        initial_input_dict['pool_size'] = 1 # Not used but required on input

    def on_after_set_input(self):
        pass

    def success_message(self, item):
        return 'Successfully {} Kafka definition `{}`'.format(self.verb, item.name)

# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'definition-kafka-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'definition-kafka-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'definition-kafka-delete'
    error_message = 'Could not delete outgoing Kafka definition'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.generic.connection.change-password')

# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id):
    return ping_connection(req, 'zato.generic.connection.ping', id, 'Kafka definition')

# ################################################################################################################################
