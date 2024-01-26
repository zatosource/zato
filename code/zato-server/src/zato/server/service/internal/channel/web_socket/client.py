# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from random import randint
from traceback import format_exc

# ciso8601
try:
    from zato.common.util.api import parse_datetime
except ImportError:
    from dateutil.parser import parse as parse_datetime

# Zato
from zato.common.broker_message import PUBSUB as BROKER_MSG_PUBSUB
from zato.common.odb.model import ChannelWebSocket, Cluster, WebSocketClient
from zato.common.odb.query import web_socket_client_by_pub_id, web_socket_clients_by_server_id
from zato.common.util.sql import set_instance_opaque_attrs
from zato.server.service import AsIs, List, Opaque
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

_wsx_client_table = WebSocketClient.__table__

# ################################################################################################################################

class Create(AdminService):
    """ Stores in ODB information about an established connection of an authenticated WebSocket client.
    """
    class SimpleIO(AdminSIO):
        input_required = (AsIs('pub_client_id'), AsIs('ext_client_id'), 'is_internal', 'local_address', 'peer_address',
            'peer_fqdn', 'connection_time', 'last_seen', 'channel_name')
        input_optional = 'ext_client_name', 'peer_forwarded_for', 'peer_forwarded_for_fqdn'
        output_optional = 'ws_client_id'
        response_elem = None

    def handle(self):
        req = self.request.input

        with closing(self.odb.session()) as session:

            # Create the client itself
            client = self._new_zato_instance_with_cluster(WebSocketClient, self.server.cluster_id)
            channel = session.query(ChannelWebSocket).\
                filter(Cluster.id==self.server.cluster_id).\
                filter(ChannelWebSocket.name==req.channel_name).\
                one()

            client.id = randint(100_000, 2_000_000_000)
            client.is_internal = req.is_internal
            client.pub_client_id = req.pub_client_id
            client.ext_client_id = req.ext_client_id
            client.ext_client_name = req.get('ext_client_name', '')
            client.local_address = req.local_address
            client.peer_address = req.peer_address
            client.peer_fqdn = req.peer_fqdn
            client.connection_time = parse_datetime(req.connection_time)
            client.last_seen = parse_datetime(req.last_seen)
            client.server_proc_pid = self.server.pid
            client.channel_id = channel.id
            client.server_id = self.server.id
            client.server_name = self.server.name

            # Opaque attributes
            set_instance_opaque_attrs(client, req, ['channel_name'])

            session.add(client)
            session.commit()

            self.response.payload.ws_client_id = client.id

# ################################################################################################################################

class DeleteByPubId(AdminService):
    """ Deletes information about a previously established WebSocket connection. Called when a client disconnects.
    """
    class SimpleIO(AdminSIO):
        input_required = (AsIs('pub_client_id'),)

    def handle(self):
        with closing(self.odb.session()) as session:
            client = web_socket_client_by_pub_id(session, self.request.input.pub_client_id)
            if client:
                session.execute(_wsx_client_table.delete().where(_wsx_client_table.c.id==client.id))
                session.commit()

# ################################################################################################################################

class UnregisterWSSubKey(AdminService):
    """ Notifies all workers about sub keys that will not longer be accessible because current WSX client disconnects.
    """
    class SimpleIO(AdminSIO):
        input_required = List('sub_key_list')
        input_optional = 'needs_wsx_close'

    def handle(self):

        # If configured to, delete the WebSocket's persistent subscription
        for sub_key in self.request.input.sub_key_list:
            sub = self.pubsub.get_subscription_by_sub_key(sub_key)
            if sub:
                if self.request.input.needs_wsx_close or (sub and sub.unsub_on_wsx_close):
                    self.invoke('zato.pubsub.pubapi.unsubscribe', {
                        'sub_key': sub.sub_key,
                        'topic_name': sub.topic_name,
                    })

        # Update in-RAM state of workers
        self.broker_client.publish({
            'action': BROKER_MSG_PUBSUB.WSX_CLIENT_SUB_KEY_SERVER_REMOVE.value,
            'sub_key_list': self.request.input.sub_key_list,
        })

# ################################################################################################################################

class DeleteByServer(AdminService):
    """ Deletes information about a previously established WebSocket connection. Called when a server shuts down.
    """
    class SimpleIO(AdminSIO):
        input_required = 'needs_pid',

    def handle(self):
        with closing(self.odb.session()) as session:
            server_pid = self.server.pid if self.request.input.get('needs_pid') else None
            clients = web_socket_clients_by_server_id(session, self.server.id, server_pid)
            clients.delete()
            session.commit()

# ################################################################################################################################

class NotifyPubSubMessage(AdminService):
    """ Notifies a WebSocket client of new messages available.
    """
    class SimpleIO(AdminSIO):
        input_required = (AsIs('pub_client_id'), 'channel_name', AsIs('request'))
        output_optional = (AsIs('r'),)
        response_elem = 'r'

    def handle(self):
        req = self.request.input
        try:
            self.response.payload.r = self.server.worker_store.web_socket_api.notify_pubsub_message(
                req.channel_name, self.cid, req.pub_client_id, req.request)
        except Exception:
            self.logger.warning(format_exc())
            raise

# ################################################################################################################################

class SetLastSeen(AdminService):
    """ Sets last_seen for input WSX client.
    """
    class SimpleIO(AdminSIO):
        input_required = 'id', Opaque('last_seen')

    def handle(self):

        with closing(self.odb.session()) as session:
            session.execute(
                _wsx_client_table.update().\
                values(last_seen=self.request.input.last_seen).\
                where(_wsx_client_table.c.id==self.request.input.id))

            session.commit()

# ################################################################################################################################
