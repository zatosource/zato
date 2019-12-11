# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.admin.web.forms.channel.file_transfer import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common import GENERIC
from zato.common.model import FileTransferChannel

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-file-transfer'
    template = 'zato/channel/file-transfer.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = FileTransferChannel
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id', 'type_'
        output_required = 'id', 'name', 'is_active', 'address', 'idle_timeout', 'keep_alive_timeout'
        output_optional = 'service_name', 'topic_name', 'host_key'
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
        input_required = 'name', 'is_active', 'address', 'idle_timeout', 'keep_alive_timeout'
        input_optional = 'service_name', 'topic_name', 'host_key'
        output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.CHANNEL_FILE_TRANSFER
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = True
        initial_input_dict['is_outconn'] = False
        initial_input_dict['sec_use_rbac'] = False
        initial_input_dict['pool_size'] = 1

    def success_message(self, item):
        return 'Successfully {} file transfer channel `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'channel-file-transfer-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'channel-file-transfer-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'channel-file-transfer-delete'
    error_message = 'Could not delete file transfer channel'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################
