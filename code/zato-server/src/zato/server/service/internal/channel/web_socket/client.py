# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# dateutil
from dateutil.parser import parse

# Zato
from zato.common.odb.model import ChannelWebSocket, Cluster, WebSocketClient
from zato.common.odb.query import web_socket_client_by_pub_id, web_socket_clients_by_server_id
from zato.server.service import AsIs
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

class Create(AdminService):
    """ Stores in ODB information about an established connection of an authenciated WebSocket client.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_channel_web_socket_client_create_request'
        response_elem = 'zato_channel_web_socket_client_create_response'
        input_required = (AsIs('pub_client_id'), AsIs('ext_client_id'), 'is_internal', 'local_address', 'peer_address',
            'peer_fqdn', 'connection_time', 'last_seen', 'channel_name')
        input_optional = ('ext_client_name',)

    def handle(self):
        req = self.request.input

        with closing(self.odb.session()) as session:

            # Create the client itself
            client = WebSocketClient()
            channel = session.query(ChannelWebSocket).\
                filter(Cluster.id==self.server.cluster_id).\
                filter(ChannelWebSocket.name==req.channel_name).\
                one()

            client.is_internal = req.is_internal
            client.pub_client_id = req.pub_client_id
            client.ext_client_id = req.ext_client_id
            client.ext_client_name = req.get('ext_client_name')
            client.local_address = req.local_address
            client.peer_address = req.peer_address
            client.peer_fqdn = req.peer_fqdn
            client.connection_time = parse(req.connection_time)
            client.last_seen = parse(req.last_seen)
            client.server_proc_pid = self.server.pid
            client.channel_id = channel.id
            client.server_id = self.server.id
            client.server_name = self.server.name

            session.add(client)
            session.commit()

            # Create default subscriptions for the client
            self.invoke('zato.channel.web-socket.subscription.create-default', {
                'ext_client_id': req.ext_client_id,
                'client_id': client.id,
                'channel_id': channel.id,
                'channel_name': channel.name,
            })


# ################################################################################################################################

class DeleteByPubId(AdminService):
    """ Deletes information about a previously established WebSocket connection. Called when a client disconnects.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_channel_web_socket_client_delete_by_pub_id_request'
        response_elem = 'zato_channel_web_socket_client_delete_by_pub_id_response'
        input_required = (AsIs('pub_client_id'),)

    def handle(self):
        with closing(self.odb.session()) as session:
            session.delete(web_socket_client_by_pub_id(session, self.request.input.pub_client_id))
            session.commit()

# ################################################################################################################################

class DeleteByServer(AdminService):
    """ Deletes information about a previously established WebSocket connection. Called when a server shuts down.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_channel_web_socket_client_delete_by_server_request'
        response_elem = 'zato_channel_web_socket_client_delete_by_server_response'

    def handle(self):

        with closing(self.odb.session()) as session:
            clients = web_socket_clients_by_server_id(session, self.server.id)
            clients.delete()
            session.commit()

# ################################################################################################################################

class DeliverRequest(AdminService):
    """ Delivers request to a selected WebSocket client.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_channel_web_socket_client_deliver_request_request'
        response_elem = 'zato_channel_web_socket_client_deliver_request_response'
        input_required = (AsIs('pub_client_id'), 'channel_name', AsIs('request'))
        output_required = (AsIs('response'),)

    def handle(self):
        req = self.request.input
        self.response.payload.response = self.server.worker_store.web_socket_api.invoke(
            req.channel_name, self.cid, req.pub_client_id, req.request)

# ################################################################################################################################
