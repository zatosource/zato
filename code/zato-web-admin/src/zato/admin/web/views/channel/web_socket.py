# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.forms.channel.web_socket import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common import ZATO_NONE
from zato.common.odb.model import ChannelWebSocket

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class WSXConnection(object):
    def __init__(self):
        self.id = None
        self.local_address = None
        self.peer_address = None
        self.peer_fqdn = None
        self.pub_client_id = None
        self.ext_client_id = None
        self.connection_time = None
        self.connection_time_utc = None
        self.server_name = None
        self.server_proc_pid = None
        self.ext_client_name = None
        self.sub_count = 0

# ################################################################################################################################

class WSXSubKeyData(object):
    def __init__(self):
        self.sub_key = None
        self.creation_time = None
        self.topic_id = None
        self.topic_name = None

# ################################################################################################################################

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

# ################################################################################################################################

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

# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'channel-web-socket-create'
    service_name = 'zato.channel.web-socket.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'channel-web-socket-edit'
    form_prefix = 'edit-'
    service_name = 'zato.channel.web-socket.edit'

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'channel-web-socket-delete'
    error_message = 'Could not delete WebSocket channel'
    service_name = 'zato.channel.web-socket.delete'

# ################################################################################################################################

class ConnectionList(_Index):
    method_allowed = 'GET'
    url_name = 'channel-web-socket-connection-list'
    template = 'zato/channel/web-socket-connection-list.html'
    service_name = 'zato.channel.web-socket.get-connection-list'
    output_class = WSXConnection
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id', 'id')
        output_required = ('local_address', 'peer_address', 'peer_fqdn', 'pub_client_id', 'ext_client_id', 'connection_time',
            'server_name', 'server_proc_pid')
        output_optional = 'ext_client_name', 'sub_count'
        output_repeated = True

    def handle(self):
        return {}

    def on_before_append_item(self, item):
        item.id = item.pub_client_id.replace('.', '-')
        item.connection_time_utc = item.connection_time
        item.connection_time = from_utc_to_user(item.connection_time_utc + '+00:00', self.req.zato.user_profile)
        return item

# ################################################################################################################################

class DisconnectionConnection(_Delete):
    url_name = 'channel-web-socket-connection-disconnect'
    error_message = 'Could not disconnect WebSocket connection'
    service_name = 'zato.channel.web-socket.disconnect-connection'

    def get_input_dict(self):
        out = super(DisconnectionConnection, self).get_input_dict()
        out['pub_client_id'] = self.req.zato.args.pub_client_id.replace('-', '.')
        return out

# ################################################################################################################################

class SubKeyDataList(_Index):
    method_allowed = 'GET'
    url_name = 'channel-web-socket-connection-sub-key-data-list'
    template = 'zato/channel/web-socket-connection-sub-key-data-list.html'
    service_name = 'channel.web-socket.get-sub-key-data-list'
    output_class = WSXSubKeyData
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id', 'pub_client_id')
        output_required = 'sub_key', 'creation_time', 'topic_id', 'topic_name'
        output_repeated = True

    def on_after_set_input(self):
        self.input['pub_client_id'] = self.input['pub_client_id'].replace('-', '.')

    def handle(self):
        return {}

    def on_before_append_item(self, item):
        item.id = item.sub_key
        item.creation_time_utc = item.creation_time
        item.creation_time = from_utc_to_user(item.creation_time_utc + '+00:00', self.req.zato.user_profile)
        return item

# ################################################################################################################################

'''
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import date, datetime

# Zato
from zato.common.util.time_ import datetime_from_ms
from zato.common.odb.query import web_socket_sub_key_data_list
from zato.server.service import AsIs, DateTime, Service
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################

class SubKeyDataList(AdminService):
    """ Returns a list of pub/sub sub_key data for a particular WSX connection.
    """
    name = 'channel.web-socket.get-sub-key-data-list'
    _filter_by = WebSocketClientPubSubKeys.sub_key,

    class SimpleIO(GetListAdminSIO):
        input_required = 'cluster_id', AsIs('pub_client_id')
        output_required = 'sub_key', DateTime('creation_time'), 'topic_id', 'topic_name'
        output_repeated = True

    def get_data(self, session):
        return self._search(web_socket_sub_key_data_list,
            session, self.request.input.cluster_id, self.request.input.pub_client_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            data = self.get_data(session)
            for item in data:
                item.creation_time = datetime_from_ms(item.creation_time)
            self.response.payload[:] = data

# ################################################################################################################################
'''
