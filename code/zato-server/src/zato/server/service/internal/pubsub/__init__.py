# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# SQLAlchemy
from sqlalchemy.sql import func

# Zato
from zato.common.odb.model import ChannelWebSocket, PubSubEndpointEnqueuedMessage, PubSubMessage, PubSubSubscription, \
     WebSocketClient, WebSocketClientPubSubKeys
from zato.common.time_util import datetime_from_ms
from zato.server.service import Opaque
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

class NotifyMessagePublished(AdminService):
    """ Notifies an individual WebSocket client that messages related to a specific sub_key became available.
    """
    def handle(self):
        web_socket = self.request.raw_request['web_socket'] # type: WebSocket
        sub_key = self.request.raw_request['request']['sub_key']

        # Find all WSX clients currently connected to our server process and try to deliver new messages to them.

        self.logger.info('Got sub_key %s for %s', sub_key, web_socket.pub_client_id)

        print(web_socket.pub_client_id)

        # Note that in the query below we join by pub_client_id only to be on the safe
        # side. In theory and practice, looking up messages by sub_key would suffice but we want
        # to double-check that our WSX connection is truly allowed to get these messages so this is
        # why we check by both sub_key and pub_client_id - to rule out situations where other WSX
        # connections erroneously subscribe to our own sub_key or that we subscribe messages
        # destined to other WSX connections.

        with closing(self.odb.session()) as session:
            messages = session.query(PubSubMessage).\
                filter(PubSubEndpointEnqueuedMessage.pub_msg_id==PubSubMessage.pub_msg_id).\
                filter(PubSubEndpointEnqueuedMessage.subscription_id==PubSubSubscription.id).\
                filter(PubSubSubscription.sub_key==WebSocketClientPubSubKeys.sub_key).\
                filter(WebSocketClientPubSubKeys.client_id==WebSocketClient.id).\
                filter(WebSocketClient.pub_client_id==web_socket.pub_client_id).\
                filter(PubSubSubscription.sub_key==sub_key).\
                order_by(PubSubMessage.priority.desc()).\
                order_by(func.coalesce(PubSubMessage.ext_pub_time, PubSubMessage.pub_time)).\
                order_by(PubSubMessage.group_id).\
                order_by(PubSubMessage.position_in_group).\
                all()

            for idx, msg in enumerate(messages, 1):
                ext_pub_time = datetime_from_ms(msg.ext_pub_time)
                pub_time = datetime_from_ms(msg.pub_time)

                print(idx, msg.priority, ext_pub_time, pub_time, msg.group_id, msg.position_in_group)

# ################################################################################################################################

class AfterPublish(AdminService):
    class SimpleIO(AdminSIO):
        input_required = ('topic_name',)
        input_optional = (Opaque('subscriptions'), Opaque('non_gd_messages'))

    def handle(self):
        # Notify all background tasks that new messages are available for their recipients.
        # However, this needs to take into account the fact that there may be many notifications
        # pointing to a single server so instead of sending notifications one by one,
        # we first find all servers and then notify each server once giving it a list of subscriptions
        # on input.

        # We also need to remember that recipients may be currently offline, in which case we do nothing
        # for GD messages but for non-GD ones, we keep them in our server's RAM.

        # TODO: server_messages = {} # Server name/PID/channel_name -> sub keys
        sub_keys = [sub.config.sub_key for sub in self.request.input.subscriptions]

        with closing(self.odb.session()) as session:
            current_ws_clients = session.query(
                WebSocketClientPubSubKeys.sub_key,
                WebSocketClient.pub_client_id,
                WebSocketClient.server_id,
                WebSocketClient.server_name,
                WebSocketClient.server_proc_pid,
                ChannelWebSocket.name.label('channel_name'),
                ).\
                filter(WebSocketClientPubSubKeys.client_id==WebSocketClient.id).\
                filter(ChannelWebSocket.id==WebSocketClient.channel_id).\
                filter(WebSocketClientPubSubKeys.cluster_id==self.server.cluster_id).\
                filter(WebSocketClientPubSubKeys.sub_key.in_(sub_keys)).\
                all()

        for elem in current_ws_clients:
            self.server.servers[elem.server_name].invoke('zato.channel.web-socket.client.notify-pub-sub-message', {
                'pub_client_id': elem.pub_client_id,
                'channel_name': elem.channel_name,
                'request': {
                    'has_gd': True,
                    'sub_key': elem.sub_key,
                },
            }, pid=elem.server_proc_pid)

# ################################################################################################################################
