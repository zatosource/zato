# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.common import GENERIC
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.outgoing.sftp import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, \
    method_allowed, ping_connection
from zato.common.odb.model import GenericConn

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

_sio_required = 'name', 'log_level'
_sio_optional = 'is_active', 'host', 'port', 'username', 'password', 'identity_file', \
    'ssh_config_file', 'buffer_size', 'is_compression_enabled', 'bandwidth_limit', 'force_ip_type', 'should_flush', \
    'should_preserve_meta', 'ssh_options'

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-sftp'
    template = 'zato/outgoing/sftp.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = GenericConn
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id', 'type_')
        output_required = ('id',) + _sio_required
        output_optional = _sio_optional
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
        input_required = _sio_required + _sio_optional
        output_required = ('id', 'name')

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_SFTP
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outconn'] = True
        initial_input_dict['pool_size'] = 100
        initial_input_dict['sec_use_rbac'] = False

    def success_message(self, item):
        return 'Successfully {} outgoing SFTP connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'out-sftp-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'out-sftp-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'out-sftp-delete'
    error_message = 'Could not delete outgoing SFTP connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id):
    return ping_connection(req, 'zato.generic.connection.ping', id, 'SFTP connection')

# ################################################################################################################################

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.generic.connection.change-password')

# ################################################################################################################################
