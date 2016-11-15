# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.channel.web_socket import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common import ZATO_NONE
from zato.common.odb.model import ChannelWebSocket

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-web-socket'
    template = 'zato/channel/web-socket.html'
    service_name = 'zato.channel.web-socket.get-list'
    output_class = ChannelWebSocket
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'address', 'service_name', 'token_format', 'data_format',
            'security_id', 'sec_type', 'new_token_wait_time', 'token_ttl')
        output_repeated = True

    def on_before_append_item(self, item):
        if item.security_id:
            item.security_id = '{}/{}'.format(item.sec_type, item.security_id)
        return item

    def handle(self):
        if self.req.zato.cluster_id:
            sec_list = self.get_sec_def_list('basic_auth').def_items
            sec_list.extend(self.get_sec_def_list('jwt'))
            sec_list.extend(self.get_sec_def_list('vault_conn_sec'))
        else:
            sec_list = []

        return {
            'create_form': CreateForm(sec_list, req=self.req),
            'edit_form': EditForm(sec_list, prefix='edit', req=self.req),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'address', 'service_name', 'token_format', 'data_format', 'is_internal', 
            'security_id', 'new_token_wait_time', 'token_ttl')
        output_required = ('id', 'name')

    def on_after_set_input(self):
        if self.input.security_id != ZATO_NONE:
            self.input.security_id = int(self.input.security_id.split('/')[1])
        else:
            self.input.security_id = None

    def success_message(self, item):
        return 'WebSocket channel `{}` successfully {}'.format(item.name, self.verb)

class Create(_CreateEdit):
    url_name = 'channel-web-socket-create'
    service_name = 'zato.channel.web-socket.create'

class Edit(_CreateEdit):
    url_name = 'channel-web-socket-edit'
    form_prefix = 'edit-'
    service_name = 'zato.channel.web-socket.edit'

class Delete(_Delete):
    url_name = 'channel-web-socket-delete'
    error_message = 'Could not delete the WebSocket channel'
    service_name = 'zato.channel.web-socket.delete'
