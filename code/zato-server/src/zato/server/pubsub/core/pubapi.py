# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from inspect import isclass

# Zato
from zato.common.api import PUBSUB
from zato.common.exception import Forbidden
from zato.common.pubsub import skip_to_external
from zato.common.typing_ import cast_
from zato.common.util.file_system import fs_safe_name
from zato.common.util.wsx import find_wsx_environ

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.model.wsx import WSXConnectorConfig
    from zato.common.typing_ import any_, anydict, anylist, anytuple, callable_, commondict, intnone, stranydict, \
        strnone, strtuple
    from zato.server.connection.web_socket import WebSocket
    from zato.server.pubsub import PubSub
    from zato.server.pubsub.core.endpoint import EndpointAPI
    from zato.server.pubsub.core.topic import TopicAPI
    from zato.server.service import Service
    from zato.server.service.store import ServiceStore

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato_pubsub.ps')
logger_zato = logging.getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

_service_read_messages_gd = 'zato.pubsub.endpoint.get-endpoint-queue-messages-gd'
_service_read_messages_non_gd = 'zato.pubsub.endpoint.get-endpoint-queue-messages-non-gd'

_service_read_message_gd = 'zato.pubsub.message.get-from-queue-gd'
_service_read_message_non_gd = 'zato.pubsub.message.get-from-queue-non-gd'

_service_delete_message_gd = 'zato.pubsub.message.queue-delete-gd'
_service_delete_message_non_gd = 'zato.pubsub.message.queue-delete-non-gd'

_ps_default = PUBSUB.DEFAULT

# ################################################################################################################################
# ################################################################################################################################

class MsgConst:
    wsx_sub_resumed = 'WSX subscription resumed, sk:`%s`, peer:`%s`'

# ################################################################################################################################
# ################################################################################################################################

class PubAPI:

    def __init__(
        self,
        *,

        # This is PubSub but we cannot use it because of spurious "cycle detected" warnings from pylance
        pubsub,        # type: PubSub

        cluster_id,    # type: int
        service_store, # type: ServiceStore
        topic_api,     # type: TopicAPI
        endpoint_api,  # type: EndpointAPI
    ) -> 'None':

        self.pubsub = pubsub

        self.cluster_id = cluster_id
        self.service_store = service_store

        self.topic_api = topic_api
        self.endpoint_api = endpoint_api

# ################################################################################################################################
# ################################################################################################################################

    def _find_wsx_environ(self, service:'Service') -> 'stranydict':
        wsx_environ = service.wsgi_environ.get('zato.request_ctx.async_msg', {}).get('environ')
        if not wsx_environ:
            raise Exception('Could not find `[\'zato.request_ctx.async_msg\'][\'environ\']` in WSGI environ `{}`'.format(
                service.wsgi_environ))
        else:
            return wsx_environ

# ################################################################################################################################
# ################################################################################################################################

    def publish(self, name:'any_', *args:'any_', **kwargs:'any_') -> 'any_':
        """ Publishes a new message to input name, which may point either to a topic or service.
        POST /zato/pubsub/topic/{topic_name}
        """
        # We need to import it here to avoid circular imports
        from zato.server.service import Service

        # Initialize here for type checking
        ws_channel_id = None

        # For later use
        from_service = cast_('Service', kwargs.get('service'))
        ext_client_id = from_service.name if from_service else kwargs.get('ext_client_id')

        # The first one is used if name is a service, the other one if it is a regular topic
        correl_id = kwargs.get('cid') or kwargs.get('correl_id')

        has_gd = kwargs.get('has_gd')
        has_gd = cast_('bool', has_gd)

        # By default, assume that cannot find any endpoint on input
        endpoint_id = None

        # If this is a WebSocket, we need to find its ws_channel_id ..
        if from_service:
            wsx_environ = find_wsx_environ(from_service, raise_if_not_found=False)
            if wsx_environ:
                wsx_config = wsx_environ['ws_channel_config'] # type: WSXConnectorConfig
                ws_channel_id = wsx_config.id
                endpoint = self.endpoint_api.get_by_ws_channel_id(ws_channel_id)
                endpoint_id = endpoint.id

        # Otherwise, use various default data.
        if not endpoint_id:
            endpoint_id = kwargs.get('endpoint_id') or self.pubsub.get_default_internal_pubsub_endpoint_id()
            endpoint_id = cast_('int', endpoint_id)

        # If input name is a topic, let us just use it
        if self.topic_api.has_topic_by_name(name):
            topic_name = name

            # There is no particular Zato context if the topic name is not really a service name
            zato_ctx = None

        # Otherwise, if there is no topic by input name, it may be actually a service name ..
        else:

            # .. it may be a Python class representing the service ..
            if isclass(name) and issubclass(name, Service):
                name = name.get_name()
            else:
                name = cast_('str', name)

            # .. but if there is no such service at all, we give up.
            if not self.service_store.has_service(name):
                msg = f'No such topic or service `{name}` (cid:{correl_id})'
                logger.info(msg)
                raise Forbidden(correl_id, 'You are not allowed to access this resource')

            # At this point we know this is a service so we may build the topic's full name,
            # taking into account the fact that a service's name is an arbitrary string
            # so we need to make it filesystem-safe.
            topic_name = PUBSUB.TOPIC_PATTERN.TO_SERVICE.format(fs_safe_name(name))

            # We continue only if the publisher is allowed to publish messages to that service.
            if not self.pubsub.is_allowed_pub_topic_by_endpoint_id(topic_name, endpoint_id):
                endpoint = self.pubsub.get_endpoint_by_id(endpoint_id)
                msg = f'No pub pattern matched service `{name}` and endpoint `{endpoint.name}` (#1) (cid:{correl_id})'
                logger.info(msg)
                raise Forbidden(correl_id, 'You are not allowed to access this resource')

            # We create a topic for that service to receive messages from unless it already exists
            if not self.topic_api.has_topic_by_name(topic_name):
                self.pubsub.create_topic_for_service(name, topic_name)
                _ = self.pubsub.wait_for_topic(topic_name)

            # Messages published to services always use GD
            has_gd = True

            # Subscribe the default service delivery endpoint to messages from this topic

            endpoint = self.endpoint_api.get_by_name(PUBSUB.SERVICE_SUBSCRIBER.NAME)
            if not self.pubsub.is_subscribed_to(endpoint.id, topic_name):

                # Subscribe the service to this topic ..
                sub_key = self.subscribe(topic_name, endpoint_name=endpoint.name, is_internal=True, delivery_batch_size=1)

                # .. and configure pub/sub metadata for the newly created subscription.
                self.pubsub.set_config_for_service_subscription(sub_key)

            # We need a Zato context to relay information about the service pointed to by the published message
            zato_ctx = {
                'target_service_name': name
            }

        # Data may be either in keyword arguments ..
        if 'data' in kwargs:
            data = kwargs['data'] or ''

        # .. or it may be provided inline among positional arguments ..
        elif args:
            data = args[0] or ''

        # .. otherwise, we assume that the data should be an empty string.
        else:
            data = ''

        data_list = kwargs.get('data_list') or []
        msg_id = kwargs.get('msg_id') or ''
        priority = kwargs.get('priority')
        expiration = kwargs.get('expiration')
        mime_type = kwargs.get('mime_type')
        in_reply_to = kwargs.get('in_reply_to')
        ext_pub_time = kwargs.get('ext_pub_time')
        reply_to_sk = kwargs.get('reply_to_sk')
        deliver_to_sk = kwargs.get('deliver_to_sk')
        user_ctx = kwargs.get('user_ctx')
        zato_ctx = zato_ctx or kwargs.get('zato_ctx')

        request = {
            'topic_name': topic_name,
            'data': data,
            'data_list': data_list,
            'msg_id': msg_id,
            'has_gd': has_gd,
            'priority': priority,
            'expiration': expiration,
            'mime_type': mime_type,
            'correl_id': correl_id,
            'in_reply_to': in_reply_to,
            'ext_client_id': ext_client_id,
            'ext_pub_time': ext_pub_time,
            'endpoint_id': endpoint_id,
            'ws_channel_id': ws_channel_id,
            'reply_to_sk': reply_to_sk,
            'deliver_to_sk': deliver_to_sk,
            'user_ctx': user_ctx,
            'zato_ctx': zato_ctx,
        } # type: anydict

        response = self.pubsub.invoke_service('zato.pubsub.publish.publish', request, serialize=False)

        if isinstance(response, dict):
            if 'response' in response:
                response = response['response']
            has_data = bool(response)
        else:
            has_data = response.has_data()

        if has_data:
            return response.get('msg_id') or response.get('msg_id_list')

# ################################################################################################################################
# ################################################################################################################################

    def get_messages(self,
        topic_name,            # type: str
        sub_key,               # type: str
        /,
        needs_details=False,   # type: bool
        needs_msg_id=False,    # type: bool
        _skip=skip_to_external # type: strtuple
        ) -> 'anylist':
        """ Returns messages from a subscriber's queue, deleting them from the queue in progress.
        POST /zato/pubsub/topic/{topic_name}?sub_key=...
        """
        response = self.pubsub.invoke_service('zato.pubsub.endpoint.get-delivery-messages', {
            'cluster_id': self.cluster_id,
            'sub_key': sub_key,
        }, serialize=False)
        response = response['response']

        # Already includes all the details ..
        if needs_details:
            return response

        # .. otherwise, we need to make sure they are not returned
        out = [] # type: anylist
        for item in response:
            for name in _skip:
                value = item.pop(name, None)
                if needs_msg_id and name == 'pub_msg_id':
                    item['msg_id'] = value
            out.append(item)
        return out

# ################################################################################################################################
# ################################################################################################################################

    def read_messages(self,
        topic_name, # type: str
        sub_key,    # type: str
        has_gd,     # type: bool
        *args,      # type: any_
        **kwargs    # type: any_
    ) -> 'any_':
        """ Looks up messages in subscriber's queue by input criteria without deleting them from the queue.
        """
        service_name = _service_read_messages_gd if has_gd else _service_read_messages_non_gd

        paginate = kwargs.get('paginate') or True
        query = kwargs.get('query') or ''
        cur_page = kwargs.get('cur_page') or 1

        return self.pubsub.invoke_service(service_name, {
            'cluster_id': self.cluster_id,
            'sub_key': sub_key,
            'paginate': paginate,
            'query': query,
            'cur_page': cur_page,
        }, serialize=False).response

# ################################################################################################################################
# ################################################################################################################################

    def read_message(self,
        topic_name, # type: str
        msg_id,     # type: str
        has_gd,     # type: bool
        *args,      # type: any_
        **kwargs    # type: any_
    ) -> 'any_':
        """ Returns details of a particular message without deleting it from the subscriber's queue.
        """
        # Forward reference
        service_data = {} # type: commondict

        if has_gd:
            service_name = _service_read_message_gd
            service_data = {
                'cluster_id': self.cluster_id,
                'msg_id': msg_id
            }
        else:
            sub_key = kwargs.get('sub_key')
            server_name = kwargs.get('server_name')
            server_pid = kwargs.get('server_pid')

            if not(sub_key and server_name and server_pid):
                raise Exception('All of sub_key, server_name and server_pid are required for non-GD messages')

            service_name = _service_read_message_non_gd
            service_data = {
                'cluster_id': self.cluster_id,
                'msg_id': msg_id,
                'sub_key': sub_key,
                'server_name': server_name,
                'server_pid': server_pid,
            }

        return self.pubsub.invoke_service(service_name, service_data, serialize=False).response

# ################################################################################################################################
# ################################################################################################################################

    def delete_message(self, sub_key:'str', msg_id:'str', has_gd:'bool', *args:'anytuple', **kwargs:'any_') -> 'any_':
        """ Deletes a message from a subscriber's queue.
        DELETE /zato/pubsub/msg/{msg_id}
        """
        service_data = {
            'sub_key': sub_key,
            'msg_id': msg_id,
        } # type: stranydict

        if has_gd:
            service_name = _service_delete_message_gd
            service_data['cluster_id'] = self.cluster_id
        else:
            server_name = cast_('str', kwargs.get('server_name', ''))
            server_pid  = cast_('int', kwargs.get('server_pid', 0))

            if not(sub_key and server_name and server_pid):
                raise Exception('All of sub_key, server_name and server_pid are required for non-GD messages')

            service_name = _service_delete_message_non_gd
            service_data['server_name'] = server_name
            service_data['server_pid'] = server_pid

        # There is no response currently but one may be added at a later time
        return self.pubsub.invoke_service(service_name, service_data, serialize=False)

# ################################################################################################################################
# ################################################################################################################################

    def subscribe(self,
        topic_name, # type: str
        _find_wsx_environ=find_wsx_environ, # type: callable_
        **kwargs # type: any_
    ) -> 'str':

        # Forward reference
        wsgi_environ = {} # type: stranydict

        # Are we going to subscribe a WSX client?
        use_current_wsx = kwargs.get('use_current_wsx')

        # This is always needed to invoke the subscription service
        request = {
            'topic_name': topic_name,
            'is_internal': kwargs.get('is_internal') or False,
            'wrap_one_msg_in_list': kwargs.get('wrap_one_msg_in_list', True),
            'delivery_batch_size': kwargs.get('delivery_batch_size', PUBSUB.DEFAULT.DELIVERY_BATCH_SIZE),
        } # type: stranydict

        # This is a subscription for a WebSocket client ..
        if use_current_wsx:
            service = cast_('Service', kwargs.get('service'))

            if use_current_wsx and (not service):
                raise Exception('Parameter `service` is required if `use_current_wsx` is True')

            # If the caller wants to subscribe a WebSocket, make sure the WebSocket's metadata
            # is given to us on input - the call below will raise an exception if it was not,
            # otherwise it will return WSX metadata out which we can extract our WebSocket object.
            wsx_environ = _find_wsx_environ(service)
            wsx = wsx_environ['web_socket']

            # All set, we can carry on with other steps now
            sub_service_name = PUBSUB.SUBSCRIBE_CLASS.get(PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id)
            wsgi_environ = service.wsgi_environ
            kwargs_wsgi_environ = kwargs.get('wsgi_environ') or {}
            wsgi_environ = wsgi_environ or kwargs_wsgi_environ
            wsgi_environ['zato.request_ctx.pubsub.unsub_on_wsx_close'] = kwargs.get('unsub_on_wsx_close')

        # .. this is a subscription for any client that is not WebSockets-based
        else:

            # We do not use WebSockets here
            wsx = None

            # Non-WSX endpoints always need to be identified by their names
            endpoint_name = cast_('str', kwargs.get('endpoint_name'))
            if not endpoint_name:
                raise Exception('Parameter `endpoint_name` is required for non-WebSockets subscriptions')
            else:
                endpoint = self.endpoint_api.get_by_name(endpoint_name)

            # Required to subscribe non-WSX endpoints
            request['endpoint_id'] = endpoint.id

            sub_service_name = PUBSUB.SUBSCRIBE_CLASS.get(endpoint.endpoint_type)
            wsgi_environ = {} # # type: ignore[no-redef]

        # Actually subscribe the caller
        response = self.pubsub.invoke_service(
            sub_service_name,
            request,
            wsgi_environ=wsgi_environ,
            serialize=False
        )

        if isinstance(response, dict) and 'response' in response:
            response = response['response']

        # If this was a WebSocket caller, we can now update its pub/sub metadata
        if use_current_wsx:
            if wsx:
                wsx.set_last_interaction_data('pubsub.subscribe')

        return response['sub_key']

# ################################################################################################################################
# ################################################################################################################################

    def resume_wsx_subscription(
        self,
        sub_key, # type: str
        service, # type: Service
        _find_wsx_environ=find_wsx_environ # type: callable_
    ) -> 'None':
        """ Invoked by WSX clients that want to resume deliveries of their messages after they reconnect.
        """
        # Get metadata and the WebSocket itself
        wsx_environ = _find_wsx_environ(service)
        wsx = wsx_environ['web_socket'] # type: WebSocket

        # Actual resume subscription
        _ = self.pubsub.invoke_service('zato.pubsub.resume-wsx-subscription', {
            'sql_ws_client_id': wsx_environ['sql_ws_client_id'],
            'channel_name': wsx_environ['ws_channel_config'].name,
            'pub_client_id': wsx_environ['pub_client_id'],
            'web_socket': wsx,
            'sub_key': sub_key
        }, wsgi_environ=service.wsgi_environ)

        # If we get here, it means the service succeeded so we can update that WebSocket's pub/sub metadata
        wsx.set_last_interaction_data('wsx.resume_wsx_subscription')

        # All done, we can store a new entry in logs now
        peer_info = wsx.get_peer_info_pretty()

        logger.info(MsgConst.wsx_sub_resumed, sub_key, peer_info)
        logger_zato.info(MsgConst.wsx_sub_resumed, sub_key, peer_info)

# ################################################################################################################################
# ################################################################################################################################

    def create_topic(
        self,
        *,
        name,                     # type: str
        has_gd=False,             # type: bool
        accept_on_no_sub=True,    # type: bool
        is_active=True,           # type: bool
        is_internal=False,        # type: bool
        is_api_sub_allowed=True,  # type: bool
        hook_service_id=None,     # type: intnone
        target_service_name=None, # type: strnone
        task_sync_interval=_ps_default.TASK_SYNC_INTERVAL,         # type: int
        task_delivery_interval=_ps_default.TASK_DELIVERY_INTERVAL, # type: int
        depth_check_freq=_ps_default.DEPTH_CHECK_FREQ,             # type: int
        max_depth_gd=_ps_default.TOPIC_MAX_DEPTH_GD,               # type: int
        max_depth_non_gd=_ps_default.TOPIC_MAX_DEPTH_NON_GD,       # type: int
        pub_buffer_size_gd=_ps_default.PUB_BUFFER_SIZE_GD,         # type: int
    ) -> 'None':

        _ = self.pubsub.invoke_service('zato.pubsub.topic.create', {
            'cluster_id': self.cluster_id,
            'name': name,
            'is_active': is_active,
            'is_internal': is_internal,
            'is_api_sub_allowed': is_api_sub_allowed,
            'has_gd': has_gd,
            'hook_service_id': hook_service_id,
            'target_service_name': target_service_name,
            'on_no_subs_pub': PUBSUB.ON_NO_SUBS_PUB.ACCEPT.id if accept_on_no_sub else PUBSUB.ON_NO_SUBS_PUB.DROP.id,
            'task_sync_interval': task_sync_interval,
            'task_delivery_interval': task_delivery_interval,
            'depth_check_freq': depth_check_freq,
            'max_depth_gd': max_depth_gd,
            'max_depth_non_gd': max_depth_non_gd,
            'pub_buffer_size_gd': pub_buffer_size_gd,
        })

# ################################################################################################################################
# ################################################################################################################################
