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
from zato.common import PUBSUB
from zato.common.util import is_class_pubsub_hook
from zato.common.odb.model import PubSubSubscription, PubSubTopic
from zato.common.odb.query import pubsub_hook_service
from zato.server.service import AsIs, List, ListOfDicts, Opaque, PubSubHook
from zato.server.service.internal import AdminService, AdminSIO

endpoint_type_service = {
    PUBSUB.ENDPOINT_TYPE.AMQP.id:        'zato.pubsub.delivery.notify-pub-sub-message',
    PUBSUB.ENDPOINT_TYPE.FILES.id:       'zato.pubsub.delivery.notify-pub-sub-message',
    PUBSUB.ENDPOINT_TYPE.FTP.id:         'zato.pubsub.delivery.notify-pub-sub-message',
    PUBSUB.ENDPOINT_TYPE.REST.id:        'zato.pubsub.delivery.notify-pub-sub-message',
    PUBSUB.ENDPOINT_TYPE.REST.id:        'zato.pubsub.delivery.notify-pub-sub-message',
    PUBSUB.ENDPOINT_TYPE.SERVICE.id:     'zato.pubsub.delivery.notify-pub-sub-message',
    PUBSUB.ENDPOINT_TYPE.SMS_TWILIO.id:  'zato.pubsub.delivery.notify-pub-sub-message',
    PUBSUB.ENDPOINT_TYPE.SMTP.id:        'zato.pubsub.delivery.notify-pub-sub-message',
    PUBSUB.ENDPOINT_TYPE.SOAP.id:        'zato.pubsub.delivery.notify-pub-sub-message',
    PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id: 'zato.channel.web-socket.client.notify-pub-sub-message',
}

hook_type_model = {
    PUBSUB.HOOK_TYPE.PUB: PubSubTopic,
    PUBSUB.HOOK_TYPE.SUB: PubSubSubscription,
}

# ################################################################################################################################

class AfterPublish(AdminService):
    class SimpleIO(AdminSIO):
        input_required = ('cid', AsIs('topic_id'), 'topic_name')
        input_optional = (Opaque('subscriptions'), Opaque('non_gd_msg_list'), 'has_gd_msg_list')

    def handle(self):
        # Notify all background tasks that new messages are available for their recipients.
        # However, this needs to take into account the fact that there may be many notifications
        # pointing to a single server so instead of sending notifications one by one,
        # we first find all servers and then notify each server once giving it a list of subscriptions on input.
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
            current_servers, not_found = self.pubsub.get_task_servers_by_sub_keys(sub_keys)

            # Local aliases
            cid = self.request.input.cid
            topic_id = self.request.input.topic_id
            topic_name = self.request.input.topic_name
            non_gd_msg_list = self.request.input.non_gd_msg_list
            has_gd_msg_list = self.request.input.has_gd_msg_list

            # We already know we can store them in RAM
            if not_found:
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

    def _notify_pub_sub(self, current_servers, non_gd_msg_list, has_gd_msg_list, endpoint_type_service=endpoint_type_service):
        """ Notifies all relevant remote servers about new messages available for delivery.
        For GD messages     - a flag is sent to indicate that there is at least one message waiting in SQL DB.
        For non-GD messages - their actual contents is sent.
        """
        notif_error_sub_keys = []

        for server_info, sub_key_list in current_servers.items():
            server_name, server_pid, pub_client_id, channel_name, endpoint_type = server_info
            service_name = endpoint_type_service[endpoint_type]

            try:
                self.server.servers[server_name].invoke(service_name, {
                    'pub_client_id': pub_client_id,
                    'channel_name': channel_name,
                    'request': {
                        'endpoint_type': endpoint_type,
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
    """ Invoked by WSX clients after they reconnect with a list of their sub_keys on input. Collects all messages
    waiting on other servers for that WebSocket and lets the caller know how many of them are available. At the same time,
    the collection process trigger's that WebSocket's delivery task (via pubsub_tool) to start deliveries.
    """
    class SimpleIO(AdminSIO):
        input_required = ('sql_ws_client_id', 'channel_name', AsIs('pub_client_id'), Opaque('web_socket'))
        input_optional = (List('sub_key_list'),)
        output_optional = (ListOfDicts('queue_depth'),)

    def handle(self):

        # Local aliases
        sub_key_list = self.request.input.sub_key_list
        pubsub_tool = self.request.input.web_socket.pubsub_tool

        # Response to produce - a list of dictionaries, each keyed by sub_key,
        # values are a dictionary of gd, non_gd for Guaranteed Delivery and non-GD messages for that sub_key
        response = []

        with closing(self.odb.session()) as session:

            # Everything is performed using that WebSocket's pub/sub lock to ensure that both
            # in-RAM and SQL (non-GD and GD) messages are made available to the WebSocket as a single unit.
            with pubsub_tool.lock:

                # Response to produce
                response = {}

                get_in_ram_service = 'zato.pubsub.topic.get-in-ram-message-list'
                non_gd_messages = self.servers.invoke_all(get_in_ram_service, {'sub_key_list':sub_key_list}, timeout=120)

                # Parse non-GD messages on output from all servers, if any at all, into per-sub_key lists ..
                if non_gd_messages:
                    non_gd_messages = self._parse_non_gd_messages(sub_key_list, non_gd_messages)

                    # If there are any non-GD messages, add them to this WebSocket's pubsub tool.
                    if non_gd_messages:
                        for sub_key, messages in non_gd_messages.items():
                            pubsub_tool.add_sub_key_no_lock(sub_key)
                            pubsub_tool.add_non_gd_messages_by_sub_key(sub_key, messages)

                # For each sub_key from input ..
                for sub_key in sub_key_list:

                    # .. add relevant SQL objects ..
                    self.pubsub.add_ws_client_pubsub_keys(
                        session, self.request.input.sql_ws_client_id, sub_key,
                        self.request.input.channel_name, self.request.input.pub_client_id)

                    # .. update state of that WebSocket's pubsub tool that keeps track of message delivery
                    pubsub_tool.add_sub_key_no_lock(sub_key)

                    # .. add any GD messages waiting for this sub_key - note that we providing our
                    # own session on input so as to control when the SQL commit happens,
                    # which we want to have after all sub_keys have been processed.
                    pubsub_tool.fetch_gd_messages_by_sub_key(sub_key, session)

                    # Will hold depths of queues
                    response[sub_key] = {
                        'queue_depth_gd': None,
                        'queue_depth_non_gd': None,
                    }

                    # .. set current depth for GD messages ..
                    response[sub_key]['queue_depth_gd'] = self.invoke('zato.pubsub.queue.get-queue-depth-by-sub-key', {
                        'sub_key': sub_key
                    })['response']['queue_depth'][sub_key]

                    # .. get depths for a given sub_key, but ignore the GD one
                    # because it only indicates how many GD messages are in the delivery task,
                    # not a total of GD messages which we have already obtained above.
                    _, queue_depth_non_gd = pubsub_tool.get_queue_depth(sub_key)

                    # .. set current depth for GD messages ..
                    response[sub_key]['queue_depth_non_gd'] = queue_depth_non_gd

                session.commit()

            self.response.payload.queue_depth = response

# ################################################################################################################################

    def _parse_non_gd_messages(self, sub_key_list, server_response):
        out = dict.fromkeys(sub_key_list, [])

        for server_name, server_data_dict in server_response.items():
            if server_data_dict['is_ok']:
                server_data = server_data_dict['server_data']

                for server_pid, pid_data_dict in server_data.items():
                    if not pid_data_dict['is_ok']:
                        self.logger.warn('Could not retrieve non-GD in-RAM messages from PID %s of %s (%s), details:`%s`',
                            server_pid, server_name, server_data_dict['meta']['address'], pid_data_dict['error_info'])
                    else:
                        messages = pid_data_dict['pid_data']['response']['messages']
                        for sub_key, sub_key_data in messages.items():
                            for msg in sub_key_data.values():
                                out[sub_key].append(msg)
            else:
                self.logger.warn('Could not retrieve non-GD in-RAM messages from %s (%s), details:`%s`',
                    server_name, server_data_dict['meta']['address'], server_data_dict['error_info'])

        # Do not return empty lists unnecessarily - note that it may happen that all sub_keys
        # will be deleted in which cases only an empty dictionary remains.
        for sub_key in sub_key_list:
            if not out[sub_key]:
                del out[sub_key]

        return out

# ################################################################################################################################
