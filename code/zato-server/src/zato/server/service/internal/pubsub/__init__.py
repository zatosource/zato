# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Zato
from zato.server.service import AsIs, List, Opaque
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

class NotifyMessagePublished(AdminService):
    """ Notifies an individual WebSocket client that messages related to a specific sub_key became available.
    """
    def handle(self):
        '''
        web_socket = self.request.raw_request['web_socket'] # type: WebSocket
        sub_key = self.request.raw_request['request']['sub_key']

        # Find all WSX clients currently connected to our server process and try to deliver new messages to them.

        self.logger.info('Got sub_key %s for %s', sub_key, web_socket.pub_client_id)

        #server_info = self.pubsub.get_ws_clients_by_sub_keys(

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

                #print(idx, msg.priority, ext_pub_time, pub_time, msg.group_id, msg.position_in_group)
                '''

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

        current_servers, not_found = self.pubsub.get_ws_clients_by_sub_keys(sub_keys)

        for server_info, sub_key_list in current_servers.items():
            server_name, server_pid, pub_client_id, channel_name = server_info

            self.server.servers[server_name].invoke('zato.channel.web-socket.client.notify-pub-sub-message', {
                'pub_client_id': pub_client_id,
                'channel_name': channel_name,
                'request': {
                    'has_gd': True,
                    'sub_key_list': sub_key_list,
                },
            }, pid=server_pid)

# ################################################################################################################################

class AfterWSXReconnect(AdminService):
    """ Invoked by WSX clients after they reconnect with a list of their sub_keys on input.
    """
    class SimpleIO(AdminSIO):
        input_required = ('sql_ws_client_id', 'channel_name', AsIs('pub_client_id'), Opaque('web_socket'))
        input_optional = (List('sub_key_list'),)
        output_optional = (Opaque('queue_depth'),)

    def handle(self):

        with closing(self.odb.session()) as session:

            # Response to produce
            response = {}

            # For each sub_key from input ..
            for sub_key in self.request.input.sub_key_list:

                # .. add relevant SQL objects ..
                self.pubsub.add_ws_client_pubsub_keys(
                    session, self.request.input.sql_ws_client_id, sub_key,
                    self.request.input.channel_name, self.request.input.pub_client_id)

                # .. update state of that WebSocket's pubsub tool that keeps track of message delivery
                self.request.input.web_socket.pubsub_tool.add_sub_key(sub_key)

                # .. return current depth
                response[sub_key] = self.invoke('zato.pubsub.queue.get-queue-depth-by-sub-key', {
                    'sub_key': sub_key
                })['response']['queue_depth'][sub_key]

            session.commit()

        self.response.payload.queue_depth = response

# ################################################################################################################################
