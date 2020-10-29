# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from logging import getLogger
from traceback import format_exc

# Python 2/3 compatibility
from six import add_metaclass

# Zato
from zato.common.api import DATA_FORMAT
from zato.common.broker_message import CHANNEL
from zato.common.odb.model import ChannelWebSocket, PubSubSubscription, PubSubTopic, Service as ServiceModel, WebSocketClient
from zato.common.odb.query import channel_web_socket_list, channel_web_socket, service, web_socket_client, \
     web_socket_client_by_pub_id, web_socket_client_list, web_socket_sub_key_data_list
from zato.common.util.api import is_port_taken
from zato.common.util.sql import elems_with_opaque
from zato.common.util.time_ import datetime_from_ms
from zato.server.service import AsIs, DateTime, Int, Service
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

# Type checking
if 0:

    # Zato
    from zato.server.connection.web_socket import ChannelWebSocket as ChannelWebSocketImpl

    # For pyflakes
    ChannelWebSocketImpl = ChannelWebSocketImpl

# ################################################################################################################################

elem = 'channel_web_socket'
model = ChannelWebSocket
label = 'a WebSocket channel'
get_list_docs = 'WebSocket channels'
broker_message = CHANNEL
broker_message_prefix = 'WEB_SOCKET_'
list_func = channel_web_socket_list
skip_input_params = ['service_id', 'is_out']
create_edit_input_required_extra = ['service_name']
output_optional_extra = ['sec_type']

# ################################################################################################################################

SubscriptionTable = PubSubSubscription.__table__
SubscriptionDelete = SubscriptionTable.delete

WSXChannelTable = ChannelWebSocket.__table__

WSXClientTable = WebSocketClient.__table__
WSXClientDelete = WSXClientTable.delete

# ################################################################################################################################

logger_pubsub = getLogger('zato_pubsub.srv')

# ################################################################################################################################

def _get_hook_service(self):
    return self.server.fs_server_config.get('wsx', {}).get('hook_service', '')

# ################################################################################################################################

def broker_message_hook(self, input, instance, attrs, service_type):
    input.source_server = self.server.get_full_name()
    input.config_cid = 'channel.web_socket.{}.{}.{}'.format(service_type, input.source_server, self.cid)

    if service_type == 'create_edit':

        with closing(self.odb.session()) as session:
            full_data = channel_web_socket(session, input.cluster_id, instance.id)

        input.sec_type = full_data.sec_type
        input.sec_name = full_data.sec_name
        input.vault_conn_default_auth_method = full_data.vault_conn_default_auth_method
        input.hook_service = _get_hook_service(self)

# ################################################################################################################################

def instance_hook(self, input, instance, attrs):

    if attrs.is_create_edit:
        instance.hook_service = _get_hook_service(self)
        instance.is_out = False
        instance.service = attrs._meta_session.query(ServiceModel).\
            filter(ServiceModel.name==input.service_name).\
            filter(ServiceModel.cluster_id==input.cluster_id).\
            one()

# ################################################################################################################################

def response_hook(self, input, _ignored_instance, attrs, service_type):
    if service_type == 'get_list' and self.name == 'zato.channel.web-socket.get-list':
        with closing(self.odb.session()) as session:
            for item in self.response.payload:
                item.service_name = service(session, self.server.cluster_id, item.service_id).name

# ################################################################################################################################

@add_metaclass(GetListMeta)
class GetList(AdminService):
    _filter_by = ChannelWebSocket.name,

# ################################################################################################################################

@add_metaclass(CreateEditMeta)
class Create(AdminService):
    pass

# ################################################################################################################################

@add_metaclass(CreateEditMeta)
class Edit(AdminService):
    pass

# ################################################################################################################################

@add_metaclass(DeleteMeta)
class Delete(AdminService):
    pass

# ################################################################################################################################

class Start(Service):
    """ Starts a WebSocket channel.
    """
    class SimpleIO(object):
        input_required = 'id', 'config_cid'
        input_optional = Int('bind_port'), 'name', 'service_name', 'sec_name', 'sec_type', 'vault_conn_default_auth_method', \
            'is_active', 'address', 'hook_service', 'data_format', Int('new_token_wait_time'), Int('token_ttl')
        request_elem = 'zato_channel_web_socket_start_request'
        response_elem = 'zato_channel_web_socket_start_response'

    def handle(self):
        input = self.request.input
        if input.bind_port and is_port_taken(input.bind_port):
            self.logger.warn('Cannot bind WebSocket channel `%s` to TCP port %s (already taken)', input.name, input.bind_port)
        else:
            self.server.worker_store.web_socket_channel_create(self.request.input)

# ################################################################################################################################

class GetConnectionList(AdminService):
    """ Returns a list of WSX connections for a particular channel.
    """
    _filter_by = WebSocketClient.ext_client_id,

    class SimpleIO(GetListAdminSIO):
        input_required = 'id', 'cluster_id'
        output_required = ('local_address', 'peer_address', 'peer_fqdn', AsIs('pub_client_id'), AsIs('ext_client_id'),
            DateTime('connection_time'), 'server_name', 'server_proc_pid')
        output_optional = 'ext_client_name', 'sub_count', 'peer_forwarded_for', 'peer_forwarded_for_fqdn'
        output_repeated = True

    def get_data(self, session):
        result = self._search(web_socket_client_list, session, self.request.input.cluster_id, self.request.input.id, False)
        return elems_with_opaque(result)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################

class _BaseCommand(AdminService):
    server_service = None

    class SimpleIO(AdminSIO):
        input_required = 'cluster_id', 'id', AsIs('pub_client_id')
        input_optional = 'request_data', Int('timeout')
        output_optional = 'response_data'
        response_elem = None

# ################################################################################################################################

    def _get_wsx_client(self, session):
        # type: (object) -> WebSocketClient
        client = web_socket_client(session, self.request.input.cluster_id, self.request.input.id,
            self.request.input.pub_client_id)
        if not client:
            raise Exception('No such WebSocket connection `{}`'.format(self.request.input.toDict()))
        else:
            return client

# ################################################################################################################################

class _BaseAPICommand(_BaseCommand):

    def handle(self):
        with closing(self.odb.session()) as session:
            client = self._get_wsx_client(session)
            server_name = client.server_name
            server_proc_pid = client.server_proc_pid

        self.logger.info(
            'WSX API request: `%s` `%s` `%s` `%s` (%s %s:%s)', self.server_service, self.request.input,
            client.pub_client_id, client.ext_client_id, self.cid, server_name, server_proc_pid)

        server_response = self.servers[server_name].invoke(
            self.server_service, self.request.input, pid=server_proc_pid, data_format=DATA_FORMAT.JSON)

        self.logger.info('WSX API response: `%s` (%s)', server_response, self.cid)

        if server_response:
            response_data = server_response.get('response_data') or {}
            self.response.payload.response_data = response_data
        else:
            self.logger.warn('No server response from %s:%s received to command `%s` (sr:%s)',
                server_name, server_proc_pid, self.request.input, server_response)

# ################################################################################################################################

class _BaseServerCommand(_BaseCommand):
    func_name = None

    def _get_server_response(self, func, pub_client_id):
        raise NotImplementedError('Must be implemented in subclasses')

    def handle(self):
        pub_client_id = self.request.input.pub_client_id

        try:
            with closing(self.odb.session()) as session:
                client = web_socket_client_by_pub_id(session, pub_client_id)
                wsx_channel_name = client.channel_name

            connector = self.server.worker_store.web_socket_api.connectors[wsx_channel_name]
            func = getattr(connector, self.func_name)
            response_data = self._get_server_response(func, pub_client_id)

        except Exception:
            self.response.payload.response_data = format_exc()
        else:
            self.response.payload.response_data = response_data

# ################################################################################################################################

class DisconnectConnection(_BaseAPICommand):
    """ Deletes an existing WSX connection.
    """
    server_service = 'zato.channel.web-socket.disconnect-connection-server'

# ################################################################################################################################

class DisconnectConnectionServer(_BaseServerCommand):
    """ Low-level implementation of WSX connection deletion - must be invoked on the server where the connection exists.
    """
    func_name = 'disconnect_client'

    def _get_server_response(self, func, pub_client_id):
        func(self.cid, pub_client_id)

# ################################################################################################################################

class SubscribeWSX(_BaseAPICommand):
    """ Subscribes a WebSocket, identified by pub_client_id, to a topic by its name
    """
    server_service = 'zato.channel.web-socket.server-subscribe-wsx'

# ################################################################################################################################

class ServerSubscribeWSX(_BaseServerCommand):
    """ Low-level implementation of SubscribeWSX that is invoked on the same server a WSX is on.
    """
    func_name = 'subscribe_to_topic'

    def _get_server_response(self, func, pub_client_id):
        return func(self.cid, pub_client_id, self.request.input.request_data)

# ################################################################################################################################

class InvokeWSX(_BaseAPICommand):
    """ Invokes an existing WSX connection.
    """
    server_service = 'zato.channel.web-socket.server-invoke-wsx'

# ################################################################################################################################

class ServerInvokeWSX(_BaseServerCommand):
    """ Low-level implementation of WSX connection inovcations - must be invoked on the server where the connection exists.
    """
    func_name = 'invoke'

    def _get_server_response(self, func, pub_client_id):
        return func(self.cid, pub_client_id, self.request.input.request_data, self.request.input.timeout)

# ################################################################################################################################

class GetSubKeyDataList(AdminService):
    """ Returns a list of pub/sub sub_key data for a particular WSX connection.
    """
    _filter_by = PubSubTopic.name,

    class SimpleIO(GetListAdminSIO):
        input_required = 'cluster_id', AsIs('pub_client_id')
        output_required = ('sub_id', 'sub_key', DateTime('creation_time'), 'topic_id', 'topic_name', 'sub_pattern_matched',
            AsIs('ext_client_id'), 'endpoint_id', 'endpoint_name')
        output_repeated = True

    def get_data(self, session):
        return self._search(web_socket_sub_key_data_list,
            session, self.request.input.cluster_id, self.request.input.pub_client_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            data = self.get_data(session)
            for item in data:
                item.creation_time = datetime_from_ms(item.creation_time * 1000)
            self.response.payload[:] = data

# ################################################################################################################################

class Broadcast(AdminService):
    """ Broacasts the input message to all WebSocket connections attached to a channel by its name.
    """
    def handle(self):
        channel_name = self.request.raw_request['channel_name']
        data = self.request.raw_request['data']
        connector = self.server.worker_store.web_socket_api.connectors[channel_name] # type: ChannelWebSocketImpl
        connector.broadcast(self.cid, data)

# ################################################################################################################################
