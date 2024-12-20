# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.api import PUBSUB
from zato.common.exception import Forbidden
from zato.common.odb.model import PubSubSubscription, PubSubTopic
from zato.common.typing_ import cast_
from zato.server.service import AsIs, Bool, DateTime, Int, Opaque
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, anytuple, stranydict, strlist
    from zato.server.pubsub.delivery.tool import PubSubTool
    anytuple = anytuple
    stranydict = stranydict
    PubSubTool = PubSubTool

# ################################################################################################################################

logger_pubsub = getLogger('zato_pubsub.srv')

# ################################################################################################################################

# Jitter to add to sleep_time so as no to have all worker processes issue the same queries at the same time,
# in the range of 0.10 to 0.29, step 0.1.
cleanup_sleep_jitter = [elem / 10.0 for elem in range(1, 4, 1)]

# ################################################################################################################################

endpoint_type_service = {
    PUBSUB.ENDPOINT_TYPE.INTERNAL.id:    'zato.pubsub.delivery.notify-pub-sub-message',
    PUBSUB.ENDPOINT_TYPE.REST.id:        'zato.pubsub.delivery.notify-pub-sub-message',
    PUBSUB.ENDPOINT_TYPE.SERVICE.id:     'zato.pubsub.delivery.notify-pub-sub-message',
    PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id: 'zato.channel.web-socket.client.notify-pub-sub-message',
}

# ################################################################################################################################

hook_type_model = {
    PUBSUB.HOOK_TYPE.BEFORE_PUBLISH: PubSubTopic,
    PUBSUB.HOOK_TYPE.BEFORE_DELIVERY: PubSubSubscription,
}

_no_sk='no-sk'
_notify_error='notify-error'
_wsx_expected_endpoint_type=PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id

# ################################################################################################################################
# ################################################################################################################################

class CommonSubData:
    common = ('subscription_id', 'is_internal', 'topic_name', 'active_status', 'endpoint_type', 'endpoint_id',
        'endpoint_name', 'delivery_method', 'delivery_data_format', 'delivery_batch_size', Bool('wrap_one_msg_in_list'),
        'delivery_max_retry', Bool('delivery_err_should_block'), 'wait_sock_err', 'wait_non_sock_err', 'server_id',
        'server_name', 'out_http_method', 'out_http_method', DateTime('creation_time'), DateTime('last_interaction_time'),
        'last_interaction_type', 'last_interaction_details', Int('total_depth'), Int('current_depth_gd'),
        Int('current_depth_non_gd'), 'sub_key', 'has_gd', 'is_staging_enabled', 'sub_id', 'name', AsIs('ws_ext_client_id'),
        AsIs('ext_client_id'), 'topic_id', 'should_ignore_if_sub_exists', 'should_delete_all') # type: anytuple
    amqp = ('out_amqp_id', 'amqp_exchange', 'amqp_routing_key')
    files = ('files_directory_list',)
    ftp = ('ftp_directory_list',)
    pubapi = ('security_id',)
    rest = ('out_http_soap_id', 'out_rest_http_soap_id', 'rest_connection', 'rest_delivery_endpoint')
    service = ('service_id',)
    sms_twilio = ('sms_twilio_from', 'sms_twilio_to_list')
    smtp = (Bool('smtp_is_html'), 'smtp_subject', 'smtp_from', 'smtp_to_list', 'smtp_body') # type: anytuple
    soap = ('out_soap_http_soap_id', 'soap_delivery_endpoint')
    wsx = ('ws_channel_id', 'ws_channel_name', AsIs('ws_pub_client_id'), 'sql_ws_client_id', Bool('unsub_on_wsx_close'),
        Opaque('web_socket')) # type: anytuple

# ################################################################################################################################

common_sub_data = CommonSubData.common + CommonSubData.amqp + CommonSubData.files + \
    CommonSubData.ftp + CommonSubData.rest + CommonSubData.service + \
    CommonSubData.sms_twilio + CommonSubData.smtp + CommonSubData.soap + CommonSubData.wsx + CommonSubData.pubapi

# ################################################################################################################################
# ################################################################################################################################

class AfterPublish(AdminService):
    """ A hook service invoked after each publication, sends messages from current server to delivery tasks.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cid', AsIs('topic_id'), 'topic_name', 'is_bg_call', Opaque('pub_time_max')) # type: anytuple
        input_optional = (Opaque('subscriptions'), Opaque('non_gd_msg_list'), 'has_gd_msg_list') # type: anytuple

    def handle(self) -> 'None':

        try:

            # Notify all background tasks that new messages are available for their recipients.
            # However, this needs to take into account the fact that there may be many notifications
            # pointing to a single server so instead of sending notifications one by one,
            # we first find all servers and then notify each server once giving it a list of subscriptions on input.
            #
            # We also need to remember that recipients may be currently offline, or in any other way inaccessible,
            # in which case we keep non-GD messages in our server's RAM.

            # Extract sub_keys from live Python subscription objects
            sub_key_data = [{'sub_key':sub.config.sub_key, 'is_wsx':bool(sub.config.ws_channel_id)} \
                for sub in self.request.input.subscriptions]

            #
            # There are two elements returned.
            #
            # current_servers - a list of servers that we know have currently subscribers
            #                   for messsages on whose behalf we are being called
            #
            # not_found ------- a list of sub_keys for which right now we don't have any servers
            #                   with delivery tasks
            #
            # All servers from current_servers will be invoked and notified about messages published (GD and non-GD).
            # For all sub_keys from not_found, information about non-GD messages for each of them will be kept in RAM.
            #
            # Additionally, for all servers from current_servers that can not be invoked for any reasons,
            # we will also store non-GD messages in our RAM store.
            #
            # Note that GD messages are not passed here directly at all - this is because at this point
            # they have been already stored in SQL by publish service before the current one has run.
            #

            current_servers, not_found = self.pubsub.get_task_servers_by_sub_keys(sub_key_data)

            # Local aliases
            cid = self.request.input.cid
            topic_id = self.request.input.topic_id
            topic_name = self.request.input.topic_name
            non_gd_msg_list = self.request.input.non_gd_msg_list
            has_gd_msg_list = self.request.input.has_gd_msg_list
            is_bg_call = self.request.input.is_bg_call
            pub_time_max = self.request.input.pub_time_max

            # We already know that we can store some of the messages in RAM,
            # but only if there are any non-GD ones to keep in RAM.
            if not_found and non_gd_msg_list:
                self._store_in_ram(cid, topic_id, topic_name, not_found, non_gd_msg_list, _no_sk)

            # .. but if some servers are up, attempt to notify pub/sub tasks about the messages ..
            if current_servers:
                notif_error_sub_keys = self._notify_pub_sub(current_servers, non_gd_msg_list,
                    has_gd_msg_list, is_bg_call, pub_time_max)

                # .. but if there are any errors, store them in RAM as though they were from not_found in the first place.
                # Note that only non-GD messages go to RAM because the GD ones are still in the SQL database.
                if notif_error_sub_keys:

                    # This will signal that non-GD messages should be retried
                    if non_gd_msg_list:
                        self._store_in_ram(cid, topic_id, topic_name, notif_error_sub_keys, non_gd_msg_list, _notify_error)

                    # This will signal that GD messages should be retried
                    if has_gd_msg_list:
                        self.pubsub.after_gd_sync_error(topic_id, 'AfterPublish.gd_notif_error_sub_keys', pub_time_max)

        except Exception:
            self.logger.warning('Error in after_publish callback, e:`%s`', format_exc())

# ################################################################################################################################

    def _store_in_ram(
        self,
        cid:'str',
        topic_id:'int',
        topic_name:'str',
        sub_keys:'strlist',
        non_gd_msg_list:'anylist',
        error_source:'str'=''
    ) -> 'None':
        """ Stores in RAM all input messages for all sub_keys.
        """
        self.pubsub.store_in_ram(cid, topic_id, topic_name, sub_keys, non_gd_msg_list, error_source)

# ################################################################################################################################

    def _notify_pub_sub(
        self,
        current_servers: 'anydict',
        non_gd_msg_list: 'anylist',
        has_gd_msg_list: 'bool',
        is_bg_call: 'bool',
        pub_time_max: 'float'
    ) -> 'anylist':
        """ Notifies all relevant remote servers about new messages available for delivery.
        For GD messages     - a flag is sent to indicate that there is at least one message waiting in SQL DB.
        For non-GD messages - their actual contents is sent.
        """
        notif_error_sub_keys = [] # type: strlist

        for server_info, sub_key_list in current_servers.items():
            server_name, server_pid, pub_client_id, channel_name, endpoint_type = server_info
            service_name = endpoint_type_service[endpoint_type]

            full_request = {
                'pub_client_id': pub_client_id,
                'channel_name': channel_name,
                'request': {
                    'endpoint_type': endpoint_type,
                    'has_gd': has_gd_msg_list,
                    'sub_key_list': sub_key_list,
                    'non_gd_msg_list': non_gd_msg_list,
                    'is_bg_call': is_bg_call,
                    'pub_time_max': pub_time_max,
                },
            }

            try:
                invoker = self.server.rpc.get_invoker_by_server_name(server_name)
                invoker.invoke(service_name, full_request, pid=server_pid)
            except Exception:

                for logger in (self.logger, logger_pubsub):
                    logger.warning('Error in pub/sub notification, service:`%s` req:`%s` pid:`%s` e:`%s`',
                        service_name, full_request, server_pid, format_exc())

                notif_error_sub_keys.extend(sub_key_list)

        return notif_error_sub_keys

# ################################################################################################################################
# ################################################################################################################################

class ResumeWSXSubscription(AdminService):
    """ Invoked by WSX clients after they reconnect with a list of their sub_keys on input.
    Collects all messages waiting on other servers for that WebSocket and enqueues any available for a task that is started
    on behalf of that WebSocket.
    """
    class SimpleIO(AdminSIO):
        input_required = ('sub_key',)

    def handle(self) -> 'None':

        # Local aliases
        sub_key_list = [self.request.input.sub_key]
        async_msg = self.wsgi_environ['zato.request_ctx.async_msg']

        # This will exist if are being invoked directly ..
        environ = async_msg.get('environ')

        # .. however, if there is a service on whose behalf we are invoked, the 'environ' key will be further nested.
        if not environ:
            _wsgi_environ = async_msg['wsgi_environ']
            _async_msg = _wsgi_environ['zato.request_ctx.async_msg']
            environ = _async_msg['environ']

        # We now have environ in one way or another
        wsx = environ['web_socket']
        pubsub_tool = wsx.pubsub_tool # type: PubSubTool

        # Need to confirm that our WebSocket previously created all the input sub_keys
        wsx_channel_id = environ['ws_channel_config'].id
        wsx_endpoint = self.pubsub.get_endpoint_by_ws_channel_id(wsx_channel_id)

        # First off, make sure that input sub_key(s) were previously created by current WebSocket
        for sub_key in sub_key_list:
            sub = self.pubsub.get_subscription_by_sub_key(sub_key)

            if not sub:
                self.logger.info('No such sub_key `%s` (ResumeWSXSubscription)', sub_key)
                continue

            if sub.config['endpoint_type'] != _wsx_expected_endpoint_type:
                self.logger.warning('Subscription `%s` endpoint_type:`%s` did not match `%s`',
                    sub_key, sub.config['endpoint_type'], _wsx_expected_endpoint_type)
                raise Forbidden(self.cid)

            if wsx_endpoint.name != sub.config['endpoint_name']:
                expected_endpoint = self.pubsub.get_endpoint_by_id(sub.config['endpoint_id'])
                self.logger.warning('Current WSX endpoint did not match sub_key `%s` endpoint, current:%s (%s) vs. expected:%s (%s)',
                    sub_key, wsx_endpoint.name, wsx_endpoint.id, expected_endpoint.name, expected_endpoint.id)

                raise Forbidden(self.cid)

        try:
            with closing(self.odb.session()) as session:

                # Everything is performed using that WebSocket's pub/sub lock to ensure that both
                # in-RAM and SQL (non-GD and GD) messages are made available to the WebSocket as a single unit.
                with pubsub_tool.lock:

                    get_in_ram_service = 'zato.pubsub.topic.get-in-ram-message-list'
                    reply = self.server.rpc.invoke_all(get_in_ram_service, {
                        'sub_key_list':sub_key_list
                    }, timeout=120)

                    # Parse non-GD messages on output from all servers, if any at all, into per-sub_key lists ..
                    reply_data = cast_('anylist', reply.data) # type: ignore
                    if reply_data:
                        non_gd_messages = self._parse_non_gd_messages(sub_key_list, reply_data)

                        # If there are any non-GD messages, add them to this WebSocket's pubsub tool.
                        if non_gd_messages:
                            for sub_key, messages in non_gd_messages.items():
                                pubsub_tool.add_sub_key_no_lock(sub_key)
                                pubsub_tool.add_non_gd_messages_by_sub_key(sub_key, messages)

                    # For each sub_key from input ..
                    for sub_key in sub_key_list:

                        # .. add relevant SQL objects ..
                        self.pubsub.add_wsx_client_pubsub_keys(session, environ['sql_ws_client_id'], sub_key,
                            environ['ws_channel_config'].name, environ['pub_client_id'],
                                environ['web_socket'].get_peer_info_dict())

                        # .. update state of that WebSocket's pubsub tool that keeps track of message delivery
                        pubsub_tool.add_sub_key_no_lock(sub_key)

                    # Everything is ready - note that pubsub_tool itself will enqueue any initial messages
                    # using its enqueue_initial_messages method which does it in batches.
                    session.commit() # type: ignore

        except Exception:
            self.logger.warning('Error while resuming WSX pub/sub for keys `%s`, e:`%s`', sub_key_list, format_exc())
            raise
        else:
            # No exception = all good and we can register this pubsub_tool with self.pubsub now
            for sub_key in sub_key_list:
                self.pubsub.set_pubsub_tool_for_sub_key(sub_key, pubsub_tool)

            # No exceptions here = we have resumed the subscription(s) successfully and we can report it
            _log_info = {}
            for _sub_key in sub_key_list:
                _log_info[_sub_key] = self.pubsub.get_topic_by_sub_key(_sub_key).name

            self.logger.info('Subscription%sresumed: `%s', ' ' if len(sub_key_list) == 1 else 's ', _log_info)

# ################################################################################################################################

    def _parse_non_gd_messages(
        self,
        sub_key_list: 'strlist',
        messages_list: 'anylist'
    ) -> 'anydict':

        out = dict.fromkeys(sub_key_list, []) # type: stranydict

        for messages in messages_list:
            messages = messages['response']
            for sub_key, sub_key_data in messages.items():
                for msg in sub_key_data:
                    out[sub_key].append(msg)

        # Do not return empty lists unnecessarily - note that it may happen that all sub_keys
        # will be deleted in which cases only an empty dictionary remains.
        for sub_key in sub_key_list:
            if not out[sub_key]:
                del out[sub_key]

        return out

# ################################################################################################################################
# ################################################################################################################################

#
# Since v3.2, these services are no longer in use.
# They were replaced by zato pubsub cleanup.
#

class _BaseCleanup(AdminService):
    def handle(self):
        pass

class DeleteMsgDelivered(_BaseCleanup):
    pass

class DeleteMsgExpired(_BaseCleanup):
    pass

class DeleteEnqDelivered(_BaseCleanup):
    pass

class DeleteEnqMarkedDeleted(_BaseCleanup):
    pass

class CleanupService(AdminService):
    pass

# ################################################################################################################################
# ################################################################################################################################
