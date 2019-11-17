# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.channel.ftp import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common import GENERIC
from zato.common.model import FTPChannel

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-ftp'
    template = 'zato/channel/ftp/index.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = FTPChannel
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id', 'type_'
        output_required = 'id', 'name', 'is_active', 'address', 'max_connections', 'max_conn_per_ip', 'command_timeout', \
           'banner', 'log_prefix', 'base_directory', 'read_throttle', 'write_throttle', \
           'passive_ports', 'log_level'
        output_optional = 'service_name', 'topic_name'
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(req=self.req),
            'edit_form': EditForm(prefix='edit', req=self.req),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'name', 'is_active', 'address', 'max_connections', 'max_conn_per_ip', 'command_timeout', \
           'banner', 'log_prefix', 'base_directory', 'read_throttle', 'write_throttle', \
           'passive_ports', 'log_level'
        input_optional = 'service_name', 'topic_name'
        output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.CHANNEL_FTP
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = True
        initial_input_dict['is_outconn'] = False
        initial_input_dict['sec_use_rbac'] = False
        initial_input_dict['pool_size'] = 1

    def success_message(self, item):
        return 'Successfully {} FTP channel `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'channel-ftp-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'channel-ftp-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'channel-ftp-delete'
    error_message = 'Could not delete FTP channel'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################
