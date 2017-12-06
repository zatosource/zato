# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Bunch
from bunch import Bunch

# Zato
from zato.common import PUBSUB
from zato.common.broker_message import PUBSUB as BROKER_MSG_PUBSUB
from zato.common.exception import BadRequest, NotFound, Forbidden, PubSubSubscriptionExists
from zato.common.odb.model import PubSubSubscription
from zato.common.odb.query_ps_subscribe import add_subscription, add_wsx_subscription, has_subscription, \
     move_messages_to_sub_queue
from zato.common.odb.query_ps_subscription import pubsub_subscription_list_by_endpoint_id
from zato.common.pubsub import new_sub_key
from zato.common.time_util import utcnow_as_ms
from zato.common.util import get_sa_model_columns
from zato.server.connection.web_socket import WebSocket
from zato.server.pubsub import PubSub, Topic
from zato.server.service import AsIs, Bool, Int, Opaque
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

# For pyflakes and code completion
PubSub = PubSub
Topic = Topic
WebSocket = WebSocket

# ################################################################################################################################

sub_broker_attrs = get_sa_model_columns(PubSubSubscription)

# ################################################################################################################################

class SubCtx(object):
    """ A container for information pertaining to a given subscription request.
    """
    def __init__(self, cluster_id, pubsub):
        self.pubsub = pubsub # type: PubSub
        self.cluster_id = cluster_id
        self.server_id = None
        self.has_gd = None
        self.pattern_matched = None
        self.topic = None # type: Topic
        self.is_internal = None
        self.active_status = None
        self.endpoint_type = None
        self.endpoint_id = None
        self.delivery_method = None
        self.delivery_data_format = None
        self.delivery_batch_size = None
        self.wrap_one_msg_in_list = None
        self.delivery_max_retry = None
        self.delivery_err_should_block = None
        self.wait_sock_err = None
        self.wait_non_sock_err = None
        self.ext_client_id = None
        self.delivery_endpoint = None
        self.out_http_soap_id = None
        self.creation_time = None
        self.sub_key = None

    def set_endpoint_id(self):
        if self.endpoint_id:
            return
        elif self.security_id:
            self.endpoint_id = self.pubsub.get_endpoint_id_by_sec_id(self.security_id)
        elif self.ws_channel_id:
            self.endpoint_id = self.pubsub.get_endpoint_id_by_ws_channel_id(self.ws_channel_id)
        else:
            raise ValueError('Could not obtain endpoint_id')

    def after_properties_set(self):
        """ A hook that lets subclasses customize this object after it is known that all common properties have been set.
        """
        self.wait_sock_err = PUBSUB.DEFAULT.WAIT_TIME_SOCKET_ERROR
        self.wait_non_sock_err = PUBSUB.DEFAULT.WAIT_TIME_NON_SOCKET_ERROR

# ################################################################################################################################

class SubCtxAMQP(SubCtx):
    """ Pub/sub context config for AMQP endpoints.
    """
    def __init__(self, *args, **kwargs):
        super(SubCtxAMQP, self).__init__(*args, **kwargs)
        self.amqp_exchange = None
        self.amqp_routing_key = None

# ################################################################################################################################

class SubCtxFiles(SubCtx):
    """ Pub/sub context config for local files-based endpoints.
    """
    def __init__(self, *args, **kwargs):
        super(SubCtxFiles, self).__init__(*args, **kwargs)
        self.files_directory_list = None

# ################################################################################################################################

class SubCtxFTP(SubCtx):
    """ Pub/sub context config for FTP endpoints.
    """
    def __init__(self, *args, **kwargs):
        super(SubCtxFTP, self).__init__(*args, **kwargs)
        self.ftp_directory_list = None

# ################################################################################################################################

class SubCtxSecBased(SubCtx):
    """ Pub/sub context config for endpoints based around security definitions (e.g. REST and SOAP).
    """
    def __init__(self, *args, **kwargs):
        super(SubCtxSecBased, self).__init__(*args, **kwargs)
        self.security_id = None

# ################################################################################################################################

class SubCtxREST(SubCtxSecBased):
    """ Pub/sub context config for REST endpoints.
    """
    def __init__(self, *args, **kwargs):
        super(SubCtxREST, self).__init__(*args, **kwargs)
        self.out_rest_http_soap_id = None
        self.rest_delivery_endpoint = None

    def after_properties_set(self):
        super(SubCtxREST, self).after_properties_set()
        self.out_http_soap_id = self.out_rest_http_soap_id
        self.delivery_endpoint = self.rest_delivery_endpoint

# ################################################################################################################################

class SubCtxService(SubCtx):
    """ Pub/sub context config for Zato service endpoints.
    """
    def __init__(self, *args, **kwargs):
        super(SubCtxService, self).__init__(*args, **kwargs)
        self.service_id = None

# ################################################################################################################################

class SubCtxSMSTwilio(SubCtx):
    """ Pub/sub context config for SMS Twilio endpoints.
    """
    def __init__(self, *args, **kwargs):
        super(SubCtxSMSTwilio, self).__init__(*args, **kwargs)
        self.sms_twilio_from = None
        self.sms_twilio_to_list = None

# ################################################################################################################################

class SubCtxSMTP(SubCtx):
    """ Pub/sub context config for SMTP endpoints.
    """
    def __init__(self, *args, **kwargs):
        super(SubCtxSMTP, self).__init__(*args, **kwargs)
        self.smtp_is_html = None
        self.smtp_subject = None
        self.smtp_from = None
        self.smtp_to_list = None
        self.smtp_body = None

# ################################################################################################################################

class SubCtxSOAP(SubCtxSecBased):
    """ Pub/sub context config for SOAP endpoints.
    """
    def __init__(self, *args, **kwargs):
        super(SubCtxSOAP, self).__init__(*args, **kwargs)
        self.out_soap_http_soap_id = None
        self.soap_delivery_endpoint = None

    def after_properties_set(self):
        super(SubCtxSOAP, self).after_properties_set()
        self.out_http_soap_id = self.out_rest_http_soap_id
        self.delivery_endpoint = self.rest_delivery_endpoint

# ################################################################################################################################

class SubCtxWebSockets(SubCtx):
    """ Pub/sub context config for WebSockets endpoints.
    """
    def __init__(self, *args, **kwargs):
        super(SubCtxWebSockets, self).__init__(*args, **kwargs)
        self.ws_channel_id = None
        self.ws_channel_name = None
        self.ws_pub_client_id = None
        self.sql_ws_client_id = None
        self.web_socket = None # type: WebSocket

# ################################################################################################################################

ctx_class = {
    PUBSUB.ENDPOINT_TYPE.AMQP.id: SubCtxAMQP,
    PUBSUB.ENDPOINT_TYPE.FILES.id: SubCtxFiles,
    PUBSUB.ENDPOINT_TYPE.FTP.id: SubCtxFTP,
    PUBSUB.ENDPOINT_TYPE.REST.id: SubCtxREST,
    PUBSUB.ENDPOINT_TYPE.SERVICE.id: SubCtxService,
    PUBSUB.ENDPOINT_TYPE.SMS_TWILIO.id: SubCtxSMSTwilio,
    PUBSUB.ENDPOINT_TYPE.SMTP.id: SubCtxSMTP,
    PUBSUB.ENDPOINT_TYPE.SOAP.id: SubCtxSOAP,
    PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id: SubCtxWebSockets,
}

# ################################################################################################################################

class _Input:
    common = ('is_internal', 'topic_name', 'active_status', 'endpoint_type', 'endpoint_id', 'delivery_method',
        'delivery_data_format', 'delivery_batch_size', Bool('wrap_one_msg_in_list'), 'delivery_max_retry',
        Bool('delivery_err_should_block'), 'wait_sock_err', 'wait_non_sock_err', 'server_id')
    amqp = ('amqp_exchange', 'amqp_routing_key')
    files = ('files_directory_list',)
    ftp = ('ftp_directory_list',)
    pubapi = ('security_id',)
    rest = ('out_rest_http_soap_id', 'rest_delivery_endpoint')
    service = ('service_id',)
    sms_twilio = ('sms_twilio_from', 'sms_twilio_to_list')
    smtp = (Bool('smtp_is_html'), 'smtp_subject', 'smtp_from', 'smtp_to_list', 'smtp_body')
    soap = ('out_soap_http_soap_id', 'soap_delivery_endpoint')
    websockets = ('ws_channel_id', 'ws_channel_name', AsIs('ws_pub_client_id'), 'sql_ws_client_id', AsIs('ext_client_id'),
        Opaque('web_socket'))

_create_edit_input_optional = _Input.common + _Input.amqp + _Input.files + _Input.ftp + _Input.rest + _Input.service + \
    _Input.sms_twilio + _Input.smtp + _Input.soap + _Input.websockets + _Input.pubapi

# ################################################################################################################################

class _Subscribe(AdminService):
    """ Base class for services implementing pub/sub subscriptions.
    """
    def _get_pattern_matched(self, topic_name, ws_channel_id, sql_ws_client_id, security_id, endpoint_id):
        pubsub = self.server.worker_store.pubsub

        if ws_channel_id and (not sql_ws_client_id):
            raise BadRequest(self.cid, 'sql_ws_client_id must not be empty if ws_channel_id is given on input')

        # Confirm if this client may subscribe at all to the topic it chose
        if endpoint_id:
            pattern_matched = pubsub.is_allowed_sub_topic_by_endpoint_id(topic_name, endpoint_id)
        else:
            kwargs = {'security_id':security_id} if security_id else {'ws_channel_id':ws_channel_id}
            pattern_matched = pubsub.is_allowed_sub_topic(topic_name, **kwargs)

        # Not allowed - raise an exception then
        if not pattern_matched:
            raise Forbidden(self.cid)

        # Alright, we can proceed
        else:
            return pattern_matched

    # Check if subscription is allowed and getting a pattern that would have matched is the same thing.
    _is_subscription_allowed = _get_pattern_matched

# ################################################################################################################################

class SubscribeServiceImpl(_Subscribe):
    """ Lower-level service that actually handles pub/sub subscriptions. Each endpoint_type has its own subclass.
    """
    endpoint_type = None

    class SimpleIO(AdminSIO):
        input_required = ('topic_name', 'is_internal')
        input_optional = _create_edit_input_optional
        output_optional = ('sub_key', Int('queue_depth'))
        default_value = None

# ################################################################################################################################

    def _get_sub_ctx(self):
        """ Returns a new pub/sub config context specific to self.endpoint_type.
        """
        # Create output object
        ctx = ctx_class[self.endpoint_type](self.server.cluster_id, self.server.worker_store.pubsub)

        # Set all attributes that we were given on input
        for k, v in self.request.input.items():
            setattr(ctx, k, v)

        # Now we can compute endpoint ID
        ctx.set_endpoint_id()

        # Call hooks
        ctx.after_properties_set()

        # Return data
        return ctx

    def _handle_subscription(self, ctx):
        raise NotImplementedError('Must be implement by subclasses')

# ################################################################################################################################

    def handle(self):
        # Get basic pub/sub subscription context
        ctx = self._get_sub_ctx()

        # Confirm correctness of input data, including whether the caller can subscribe
        # to this topic and if the topic exists at all.
        ctx.pattern_matched = self._get_pattern_matched(
            ctx.topic_name, ctx.ws_channel_id, ctx.sql_ws_client_id, ctx.security_id, ctx.endpoint_id)

        try:
            topic = ctx.pubsub.get_topic_by_name(ctx.topic_name)
        except KeyError:
            raise NotFound(self.cid, 'No such topic `{}`'.format(ctx.topic_name))
        else:
            ctx.topic = topic

        # Inherit GD from topic if it is not set explicitly
        ctx.has_gd = ctx.has_gd if isinstance(ctx.has_gd, bool) else topic.has_gd

        # Ok, we can actually subscribe the caller now
        self._handle_subscription(ctx)

    def _subscribe_impl(self, ctx):
        """ Invoked by subclasses to subscribe callers using input pub/sub config context.
        """
        with self.lock('zato.pubsub.subscribe.%s.%s' % (ctx.topic_name, ctx.endpoint_id)):

            with closing(self.odb.session()) as session:

                # Non-WebSocket clients cannot subscribe to the same topic multiple times
                if not ctx.ws_channel_id:
                    if has_subscription(session, ctx.cluster_id, ctx.topic.id, ctx.endpoint_id):
                        raise PubSubSubscriptionExists(self.cid, 'Subscription to topic `{}` already exists'.format(
                            ctx.topic.name))

                ctx.creation_time = now = utcnow_as_ms()
                ctx.sub_key = new_sub_key()

                # If we subscribe a WSX client, we need to create its accompanying SQL models
                if ctx.ws_channel_id:

                    # This object persists across multiple WSX connections
                    add_wsx_subscription(
                        session, ctx.cluster_id, ctx.is_internal, ctx.sub_key, ctx.ext_client_id, ctx.ws_channel_id)

                    # This object will be transient - dropped each time a WSX disconnects
                    self.pubsub.add_ws_client_pubsub_keys(session, ctx.sql_ws_client_id, ctx.sub_key, ctx.ws_channel_name,
                        ctx.ws_pub_client_id)

                    # Let the WebSocket connection object know that it should handle this particular sub_key
                    ctx.web_socket.pubsub_tool.add_sub_key(ctx.sub_key)

                # Create a new subscription object
                ps_sub = add_subscription(session, ctx.cluster_id, ctx)

                # Flush the session because we need the subscription's ID below in INSERT from SELECT
                session.flush()

                # Move all available messages to that subscriber's queue
                total_moved = move_messages_to_sub_queue(session, ctx.cluster_id, ctx.topic.id, ctx.endpoint_id, ps_sub.id, now)

                # Commit all changes
                session.commit()

                # Produce response
                self.response.payload.sub_key = ctx.sub_key
                self.response.payload.queue_depth = total_moved

                # Notify workers of a new subscription
                broker_input = Bunch()
                broker_input.topic_name = ctx.topic.name
                broker_input.endpoint_type = self.endpoint_type

                for name in sub_broker_attrs:
                    broker_input[name] = getattr(ps_sub, name, None)

                broker_input.action = BROKER_MSG_PUBSUB.SUBSCRIPTION_CREATE.value
                self.broker_client.publish(broker_input)

# ################################################################################################################################

class SubscribeWebSockets(SubscribeServiceImpl):
    """ Handles pub/sub subscriptions for WebSockets.
    """
    name = 'zato.pubsub.subscription.subscribe-websockets'
    endpoint_type = PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id

    def _handle_subscription(self, ctx):
        ctx.delivery_method = PUBSUB.DELIVERY_METHOD.WEB_SOCKET.id # This is a WebSocket so delivery_method is always fixed
        self._subscribe_impl(ctx)

# ################################################################################################################################

class SubscribeREST(SubscribeServiceImpl):
    """ Handles pub/sub subscriptions for REST clients.
    """
    endpoint_type = PUBSUB.ENDPOINT_TYPE.REST.id

    def _handle_subscription(self, ctx):
        self._subscribe_impl(ctx)

# ################################################################################################################################

class SubscribeSOAP(SubscribeServiceImpl):
    """ Handles pub/sub subscriptions for SOAP clients.
    """
    endpoint_type = PUBSUB.ENDPOINT_TYPE.SOAP.id

    def _handle_subscription(self, ctx):
        self._subscribe_impl(ctx)

# ################################################################################################################################

class Create(_Subscribe):
    """ Creates a new pub/sub subscription by invoking a subscription service specific to input endpoint_type.
    """
    def handle(self):
        topic_list_text = [elem.strip() for elem in (self.request.raw_request.pop('topic_list_text', '') or '').splitlines()]
        topic_list_json = self.request.raw_request.pop('topic_list_json', [])
        topic_name = self.request.raw_request.pop('topic_name', '').strip()

        if topic_name:
            topic_name = [topic_name]

        if not(topic_list_text or topic_list_json or topic_name):
            raise BadRequest(self.cid, 'No topics to subscribe to given on input')
        else:
            if topic_list_text:
                topic_list = topic_list_text
            elif topic_list_json:
                topic_list = topic_list_json
            else:
                topic_list = topic_name

            # For all topics given on input, check it upfront if caller may subscribe to all of them
            check_input = [
                int(self.request.raw_request.get('ws_channel_id') or 0),
                int(self.request.raw_request.get('sql_ws_client_id') or 0),
                int(self.request.raw_request.get('security_id') or 0),
                int(self.request.raw_request.get('endpoint_id') or 0),
            ]
            for topic_name in topic_list:
                try:
                    self._is_subscription_allowed(topic_name, *check_input)
                except Forbidden:
                    self.logger.warn('Could not subscribe to `%r` using `%r`', topic_name, check_input)
                    raise

            sub_service = 'zato.pubsub.subscription.subscribe-{}'.format(self.request.raw_request['endpoint_type'])
            sub_request = self.request.raw_request

            # Invoke subscription for each topic given on input. At this point we know we can subscribe to all of them.
            for topic_name in topic_list:
                sub_request['topic_name'] = topic_name
                self.response.payload = self.invoke(sub_service, sub_request)

# ################################################################################################################################

class DeleteAll(AdminService):
    """ Deletes all pub/sub subscriptions of a given endpoint.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'endpoint_id')

    def handle(self):
        with closing(self.odb.session()) as session:

            # Get all subscriptions for that endpoint ..
            items = pubsub_subscription_list_by_endpoint_id(
                session, self.request.input.cluster_id, self.request.input.endpoint_id)

            # Build a list of sub_keys that this endpoint was using and delete them all in one go.
            sub_key_list = [item.sub_key for item in items]
            if sub_key_list:
                self.invoke('zato.pubsub.endpoint.delete-endpoint-queue', {
                    'cluster_id': self.request.input.cluster_id,
                    'sub_key_list': sub_key_list,
                })

# ################################################################################################################################
