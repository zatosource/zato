# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.server.service import AsIs, Int, List, Opaque
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

class AfterPublish(AdminService):
    class SimpleIO(AdminSIO):
        input_required = ('cid', AsIs('topic_id'), 'topic_name')
        input_optional = (Opaque('subscriptions'), Opaque('non_gd_msg_list'), 'has_gd_msg_list')

    def handle(self):
        # Notify all background tasks that new messages are available for their recipients.
        # However, this needs to take into account the fact that there may be many notifications
        # pointing to a single server so instead of sending notifications one by one,
        # we first find all servers and then notify each server once giving it a list of subscriptions
        # on input.
        #
        # We also need to remember that recipients may be currently offline, or in any other way inaccessible,
        # in which case we keep non-GD messages in our server's RAM.

        # Extract sub_keys from live Python subscription objects
        sub_keys = [sub.config.sub_key for sub in self.request.input.subscriptions]

        #
        # There are two elements returned.
        #
        # current_servers - a list of servers that we know have currently subscribers
        #                   for messsages on whose behalf we are being called
        #
        # not_found ------- a list of sub_keys for which we don't have any servers
        #                   with delivery tasks right now
        #
        # All servers from current_servers will be invoked and notified about messages published (GD and non-GD).
        # For all sub_keys from not_found, information about non-GD messages for each of them will be kept in RAM.
        #
        # Additionally, for all servers from current_servers that can not be invoked for any reasons,
        # we will also store non-GD messages in our RAM store.
        #
        # Note that GD messages are not passed here directly at all - this is because at this point
        # they have been already stored in SQL by publish service before this service runs.
        #

        try:
            current_servers, not_found = self.pubsub.get_ws_clients_by_sub_keys(sub_keys)

            # Local aliases
            cid = self.request.input.cid
            topic_id = self.request.input.topic_id
            topic_name = self.request.input.topic_name
            non_gd_msg_list = self.request.input.non_gd_msg_list

            # We already know we can store them in RAM
            self._store_in_ram(cid, topic_id, topic_name, not_found, non_gd_msg_list, False)

            # Attempt to notify pub/sub tasks about non-GD messages ..
            notif_error_sub_keys = self._notify_pub_sub(current_servers, non_gd_msg_list, self.request.input.has_gd_msg_list)

            # .. but if there are any errors, store them in RAM as though they were from not_found in the first place.
            if notif_error_sub_keys:
                self._store_in_ram(cid, topic_id, topic_name, notif_error_sub_keys, non_gd_msg_list, True)

        except Exception, e:
            self.logger.warn('Error in after_publish callback, e:`%s`', format_exc(e))

# ################################################################################################################################

    def _store_in_ram(self, cid, topic_id, topic_name, sub_keys, non_gd_msg_list, from_notif_error):
        """ Stores in RAM all input messages for all sub_keys.
        """
        self.pubsub.store_in_ram(cid, topic_id, topic_name, sub_keys, non_gd_msg_list, from_notif_error)

# ################################################################################################################################

    def _notify_pub_sub(self, current_servers, non_gd_msg_list, has_gd_msg_list):
        """ Notifies all relevant remote servers about new messages available for delivery.
        For GD messages     - a flag is sent to indicate that there is at least one message in SQL waiting.
        For non-GD messages - their actual contents is sent.
        """
        notif_error_sub_keys = []

        for server_info, sub_key_list in current_servers.items():
            server_name, server_pid, pub_client_id, channel_name = server_info

            try:
                self.server.servers[server_name].invoke('zato.channel.web-socket.client.notify-pub-sub-message', {
                    'pub_client_id': pub_client_id,
                    'channel_name': channel_name,
                    'request': {
                        'has_gd': has_gd_msg_list,
                        'sub_key_list': sub_key_list,
                        'non_gd_msg_list': non_gd_msg_list
                    },
                }, pid=server_pid)
            except Exception, e:
                self.logger.warn('Error in pub/sub notification %r', format_exc(e))
                notif_error_sub_keys.extend(sub_key_list)

        return notif_error_sub_keys

# ################################################################################################################################

class AfterWSXReconnect(AdminService):
    """ Invoked by WSX clients after they reconnect with a list of their sub_keys on input.
    """
    class SimpleIO(AdminSIO):
        input_required = ('sql_ws_client_id', 'channel_name', AsIs('pub_client_id'), Opaque('web_socket'))
        input_optional = (List('sub_key_list'),)
        output_optional = (Int('queue_depth_gd'), Int('queue_depth_non_gd'), Int('queue_depth_total'))

    def handle(self):

        with closing(self.odb.session()) as session:

            # Everything is performed using that WebSocket's pub/sub lock to ensure that both
            # in-RAM and SQL (non-GD and GD) messages are made available to the WebSocket as a single unit.
            with self.request.input.web_socket.pubsub_tool.lock:

                # Response to produce
                response = {}

                get_in_ram_service = 'zato.pubsub.topic.get-in-ram-message-list'
                non_gd = self.servers.invoke_all(
                    get_in_ram_service, {'sub_key_list':self.request.input.sub_key_list}, timeout=120)

                self.logger.warn('zzzzzzzzzz')

                self.logger.warn('333 %s', non_gd)

                # For each sub_key from input ..
                for sub_key in self.request.input.sub_key_list:

                    # .. add relevant SQL objects ..
                    self.pubsub.add_ws_client_pubsub_keys(
                        session, self.request.input.sql_ws_client_id, sub_key,
                        self.request.input.channel_name, self.request.input.pub_client_id)

                    # .. update state of that WebSocket's pubsub tool that keeps track of message delivery
                    self.request.input.web_socket.pubsub_tool.add_sub_key_no_lock(sub_key)

                    # .. return current depth
                    response[sub_key] = self.invoke('zato.pubsub.queue.get-queue-depth-by-sub-key', {
                        'sub_key': sub_key
                    })['response']['queue_depth'][sub_key]

                session.commit()

            self.response.payload.queue_depth = response

# ################################################################################################################################

    def _get_non_gd_messages(self, server_response):
        return 'zzz'

# ################################################################################################################################
