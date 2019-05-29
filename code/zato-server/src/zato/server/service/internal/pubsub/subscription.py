# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from logging import getLogger

# Bunch
from bunch import Bunch

# SQLAlchemy
from sqlalchemy import update

# Zato
from zato.common import PUBSUB
from zato.common.broker_message import PUBSUB as BROKER_MSG_PUBSUB
from zato.common.exception import BadRequest, NotFound, Forbidden, PubSubSubscriptionExists
from zato.common.odb.model import PubSubSubscription
from zato.common.odb.query.pubsub.queue import get_queue_depth_by_sub_key
from zato.common.odb.query.pubsub.subscribe import add_subscription, add_wsx_subscription, has_subscription, \
     move_messages_to_sub_queue
from zato.common.odb.query.pubsub.subscription import pubsub_subscription_list_by_endpoint_id_no_search
from zato.common.pubsub import new_sub_key
from zato.common.util import get_sa_model_columns, make_repr
from zato.common.util.time_ import datetime_to_ms, utcnow_as_ms
from zato.server.connection.web_socket import WebSocket
from zato.server.pubsub import PubSub, Topic
from zato.server.service import Bool, Int, List, Opaque
from zato.server.service.internal import AdminService, AdminSIO
from zato.server.service.internal.pubsub import common_sub_data

# ################################################################################################################################

# For pyflakes and code completion
PubSub = PubSub
Topic = Topic
WebSocket = WebSocket

# ################################################################################################################################

logger_pubsub = getLogger('zato_pubsub.srv')

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
        self.sub_pattern_matched = None
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
        self.out_http_method = None
        self.out_amqp_id = None
        self.creation_time = None
        self.sub_key = None
        self.ws_sub = None

    def __repr__(self):
        return make_repr(self)

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

# ################################################################################################################################

class SubCtxAMQP(SubCtx):
    """ Pub/sub context config for AMQP endpoints.
    """
    def __init__(self, *args, **kwargs):
        super(SubCtxAMQP, self).__init__(*args, **kwargs)
        self.amqp_exchange = None
        self.amqp_routing_key = None
        self.out_amqp_id = None

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
        self.out_http_soap_id = self.out_soap_http_soap_id
        self.delivery_endpoint = self.soap_delivery_endpoint

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
        self.unsub_on_wsx_close = None
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

class _Subscribe(AdminService):
    """ Base class for services implementing pub/sub subscriptions.
    """
    def _get_sub_pattern_matched(self, topic_name, ws_channel_id, sql_ws_client_id, security_id, endpoint_id):
        pubsub = self.server.worker_store.pubsub

        if ws_channel_id and (not sql_ws_client_id):
            raise BadRequest(self.cid, 'sql_ws_client_id must not be empty if ws_channel_id is given on input')

        # Confirm if this client may subscribe at all to the topic it chose
        if endpoint_id:
            sub_pattern_matched = pubsub.is_allowed_sub_topic_by_endpoint_id(topic_name, endpoint_id)
        else:
            kwargs = {'security_id':security_id} if security_id else {'ws_channel_id':ws_channel_id}
            sub_pattern_matched = pubsub.is_allowed_sub_topic(topic_name, **kwargs)

        # Not allowed - raise an exception then
        if not sub_pattern_matched:
            raise Forbidden(self.cid)

        # Alright, we can proceed
        else:
            return sub_pattern_matched

    # Check if subscription is allowed and getting a pattern that would have matched is the same thing.
    _is_subscription_allowed = _get_sub_pattern_matched

# ################################################################################################################################

class SubscribeServiceImpl(_Subscribe):
    """ Lower-level service that actually handles pub/sub subscriptions. Each endpoint_type has its own subclass.
    """
    endpoint_type = None

    class SimpleIO(AdminSIO):
        input_required = ('topic_name', 'is_internal')
        input_optional = common_sub_data
        output_optional = ('sub_key', 'queue_depth')
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
        ctx.sub_pattern_matched = self._get_sub_pattern_matched(
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

# ################################################################################################################################

    def _subscribe_impl(self, ctx):
        """ Invoked by subclasses to subscribe callers using input pub/sub config context.
        """
        with self.lock('zato.pubsub.subscribe.%s' % (ctx.topic_name)):

            # Emit events about an upcoming subscription
            self.pubsub.emit_about_to_subscribe({
                'stage':'sub.sk.1',
                'sub_key':ctx.sub_key
            })

            self.pubsub.emit_about_to_subscribe({
                'stage':'init.ctx',
                'data':ctx
            })

            self.pubsub.emit_about_to_subscribe({
                'stage':'sub.sk.2',
                'sub_key':ctx.sub_key
            })

            # Endpoint on whose behalf the subscription will be made
            endpoint = self.pubsub.get_endpoint_by_id(ctx.endpoint_id)

            # Event log
            self.pubsub.emit_in_subscribe_impl({
                'stage':'endpoint',
                'data':endpoint,
            })

            self.pubsub.emit_about_to_subscribe({
                'stage':'sub.sk.3',
                'sub_key':ctx.sub_key
            })

            with closing(self.odb.session()) as session:

                with session.no_autoflush:

                    # Non-WebSocket clients cannot subscribe to the same topic multiple times
                    if not ctx.ws_channel_id:

                        # Event log
                        self.pubsub.emit_in_subscribe_impl({
                            'stage':'no_ctx_ws_channel_id',
                            'data':ctx.ws_channel_id
                        })

                        self.pubsub.emit_about_to_subscribe({
                            'stage':'sub.sk.4',
                            'sub_key':ctx.sub_key
                        })

                        if has_subscription(session, ctx.cluster_id, ctx.topic.id, ctx.endpoint_id):

                            # Event log
                            self.pubsub.emit_in_subscribe_impl({'stage':'has_subscription', 'data':{
                                'ctx.cluster_id': ctx.cluster_id,
                                'ctx.topic_id': ctx.topic.id,
                                'ctx.topic_id': ctx.endpoint_id,
                            }})

                            raise PubSubSubscriptionExists(self.cid, 'Endpoint `{}` is already subscribed to topic `{}`'.format(
                                endpoint.name, ctx.topic.name))

                    # Is it a WebSockets client?
                    is_wsx = bool(ctx.ws_channel_id)

                    self.pubsub.emit_about_to_subscribe({
                        'stage':'sub.sk.5',
                        'sub_key':ctx.sub_key
                    })

                    ctx.creation_time = now = utcnow_as_ms()
                    sub_key = new_sub_key(self.endpoint_type, ctx.ext_client_id)

                    self.pubsub.emit_in_subscribe_impl({'stage':'new_sk_generated', 'data':{
                        'sub_key': sub_key,
                    }})

                    # Event log
                    self.pubsub.emit_in_subscribe_impl({'stage':'before_add_subscription', 'data':{
                        'is_wsx': is_wsx,
                        'ctx.creation_time': ctx.creation_time,
                        'sub_key': sub_key,
                        'sub_sk': sorted(self.pubsub.subscriptions_by_sub_key),
                    }})

                    # Create a new subscription object and flush the session because the subscription's ID
                    # may be needed for the WSX subscription
                    ps_sub = add_subscription(session, ctx.cluster_id, sub_key, ctx)
                    session.flush()

                    # Event log
                    self.pubsub.emit_in_subscribe_impl({'stage':'after_add_subscription', 'data':{
                        'ctx.cluster_id': ctx.cluster_id,
                        'ps_sub': ps_sub.asdict(),
                        'sub_sk': sorted(self.pubsub.subscriptions_by_sub_key),
                    }})

                    # Common configuration for WSX and broker messages
                    sub_config = Bunch()
                    sub_config.topic_name = ctx.topic.name
                    sub_config.task_delivery_interval = ctx.topic.task_delivery_interval
                    sub_config.endpoint_name = endpoint.name
                    sub_config.endpoint_type = self.endpoint_type
                    sub_config.unsub_on_wsx_close = ctx.unsub_on_wsx_close
                    sub_config.ext_client_id = ctx.ext_client_id

                    for name in sub_broker_attrs:
                        sub_config[name] = getattr(ps_sub, name, None)

                    #
                    # At this point there may be several cases depending on whether there are already other subscriptions
                    # or messages in the topic.
                    #
                    # * If there are subscribers, then this method will not move any messages because the messages
                    #   will have been already moved to queues of other subscribers before we are called
                    #
                    # * If there are no subscribers but there are messages in the topic then this subscriber will become
                    #   the sole recipient of the messages (we don't have any intrinsic foreknowledge of when, if at all,
                    #   other subscribers can appear)
                    #
                    # * If there are no subscribers and no messages in the topic then this is a no-op
                    #

                    move_messages_to_sub_queue(session, ctx.cluster_id, ctx.topic.id, ctx.endpoint_id,
                        ctx.sub_pattern_matched, sub_key, now)

                    # Subscription's ID is available only now, after the session was flushed
                    sub_config.id = ps_sub.id

                    # Update current server's pub/sub config
                    self.pubsub.add_subscription(sub_config)

                    if is_wsx:

                        # Event log
                        self.pubsub.emit_in_subscribe_impl({'stage':'before_wsx_sub', 'data':{
                            'is_wsx': is_wsx,
                            'sub_sk': sorted(self.pubsub.subscriptions_by_sub_key),
                        }})

                        # This object persists across multiple WSX connections
                        wsx_sub = add_wsx_subscription(session, ctx.cluster_id, ctx.is_internal, sub_key,
                            ctx.ext_client_id, ctx.ws_channel_id, ps_sub.id)

                        # Event log
                        self.pubsub.emit_in_subscribe_impl({'stage':'after_wsx_sub', 'data':{
                            'wsx_sub': wsx_sub.asdict(),
                            'sub_sk': sorted(self.pubsub.subscriptions_by_sub_key),
                        }})

                        # This object will be transient - dropped each time a WSX client disconnects
                        self.pubsub.add_wsx_client_pubsub_keys(session, ctx.sql_ws_client_id, sub_key, ctx.ws_channel_name,
                            ctx.ws_pub_client_id, ctx.web_socket.get_peer_info_dict())

                        # Let the WebSocket connection object know that it should handle this particular sub_key
                        ctx.web_socket.pubsub_tool.add_sub_key(sub_key)

                    # Commit all changes
                    session.commit()

                    # Produce response
                    self.response.payload.sub_key = sub_key

                    if is_wsx:

                        # Let the pub/sub task know it can fetch any messages possibly enqueued for that subscriber,
                        # note that since this is a new subscription, it is certain that only GD messages may be available,
                        # never non-GD ones.
                        ctx.web_socket.pubsub_tool.enqueue_gd_messages_by_sub_key(sub_key)

                        gd_depth, non_gd_depth = ctx.web_socket.pubsub_tool.get_queue_depth(sub_key)
                        self.response.payload.queue_depth = gd_depth + non_gd_depth
                    else:

                        # TODO:
                        # This should be read from that client's delivery task instead of SQL so as to include
                        # non-GD messages too.

                        self.response.payload.queue_depth = get_queue_depth_by_sub_key(session, ctx.cluster_id, sub_key, now)

                # Notify workers of a new subscription
                sub_config.action = BROKER_MSG_PUBSUB.SUBSCRIPTION_CREATE.value

                # Append information about current server which will let all workers
                # know if they should create a subscription object (if they are different) or not.
                sub_config.server_receiving_subscription_id = self.server.id
                sub_config.server_receiving_subscription_pid = self.server.pid
                sub_config.is_api_call = True

                logger_pubsub.info('Subscription created `%s`', sub_config)

                self.broker_client.publish(sub_config)

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

class SubscribeAMQP(SubscribeServiceImpl):
    """ Handles pub/sub subscriptions for AMQP endpoints.
    """
    endpoint_type = PUBSUB.ENDPOINT_TYPE.AMQP.id

    def _handle_subscription(self, ctx):
        self._subscribe_impl(ctx)

# ################################################################################################################################

class Create(_Subscribe):
    """ Creates a new pub/sub subscription by invoking a subscription service specific to input endpoint_type.
    """
    def handle(self):

        # This is a multi-line string of topic names
        topic_list_text = [elem.strip() for elem in (self.request.raw_request.pop('topic_list_text', '') or '').splitlines()]

        # This is a JSON list of topic names
        topic_list_json = self.request.raw_request.pop('topic_list_json', [])

        # This is a single topic
        topic_name = self.request.raw_request.pop('topic_name', '').strip()

        if topic_name:
            topic_name = [topic_name]

        if not(topic_list_text or topic_list_json or topic_name):
            raise BadRequest(self.cid, 'No topics to subscribe to were given on input')
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
                    # Assignment to sub_pattern_matched will need to be changed once
                    # we support subscriptions to multiple topics at a time,
                    # but for the time being, this is fine.
                    self.request.raw_request['sub_pattern_matched'] = self._is_subscription_allowed(topic_name, *check_input)
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
            items = pubsub_subscription_list_by_endpoint_id_no_search(
                session, self.request.input.cluster_id, self.request.input.endpoint_id)

            # Build a list of sub_keys that this endpoint was using and delete them all in one go.
            sub_key_list = [item.sub_key for item in items]
            if sub_key_list:
                self.invoke('zato.pubsub.endpoint.delete-endpoint-queue', {
                    'cluster_id': self.request.input.cluster_id,
                    'sub_key_list': sub_key_list,
                })

# ################################################################################################################################

class CreateWSXSubscription(AdminService):
    """ Creates a new pub/sub subscription for current WebSocket connection.
    """
    class SimpleIO:
        input_optional = 'topic_name', List('topic_name_list'), Bool('wrap_one_msg_in_list'), Int('delivery_batch_size')
        output_optional = 'sub_key', 'current_depth', 'sub_data'
        response_elem = None
        skip_empty_keys = True

    def handle(self):

        # Local aliases
        topic_name = self.request.input.topic_name
        topic_name_list = set(self.request.input.topic_name_list)
        async_msg = self.wsgi_environ['zato.request_ctx.async_msg']

        unsub_on_wsx_close = async_msg['wsgi_environ'].get('zato.request_ctx.pubsub.unsub_on_wsx_close')

        # This will exist if we are being invoked directly ..
        environ = async_msg.get('environ')

        # .. however, if there is a service on whose behalf we are invoked, the 'environ' key will be further nested.
        if not environ:
            _wsgi_environ = async_msg['wsgi_environ']
            _async_msg = _wsgi_environ['zato.request_ctx.async_msg']
            environ = _async_msg['environ']

        ws_channel_id = environ['ws_channel_config'].id

        # Make sure the WSX channel actually points to an endpoint. If it does not,
        # we cannot proceed, i.e. there is no such API client.

        try:
            self.pubsub.get_endpoint_id_by_ws_channel_id(ws_channel_id)
        except KeyError:
            self.logger.warn('There is no endpoint for WSX channel ID `%s`', ws_channel_id)
            raise Forbidden(self.cid)

        # Either an exact topic name or a list thereof is needed ..
        if not (topic_name or topic_name_list):
            raise BadRequest(self.cid, 'Either or topic_name or topic_name_list is required')

        # .. but we cannot accept both of them.
        elif topic_name and topic_name_list:
            raise BadRequest(self.cid, 'Cannot provide both topic_name and topic_name_list on input')

        subscribe_to = [topic_name] if topic_name else topic_name_list
        responses = {}

        for item in subscribe_to:

            request = {
                'topic_name': item,
                'ws_channel_id': ws_channel_id,
                'ext_client_id': environ['ext_client_id'],
                'ws_pub_client_id': environ['pub_client_id'],
                'ws_channel_name': environ['ws_channel_config']['name'],
                'sql_ws_client_id': environ['sql_ws_client_id'],
                'unsub_on_wsx_close': unsub_on_wsx_close,
                'web_socket': environ['web_socket'],
            }

            for name in 'wrap_one_msg_in_list', 'delivery_batch_size':
                request[name] = self.request.input.get(name)

            response = self.invoke('zato.pubsub.subscription.subscribe-websockets', request)['response']
            responses[item] = response

        # There was only one topic on input ..
        if topic_name:
            self.response.payload = responses[topic_name]

        # .. or a list of topics on was given on input.
        else:
            out = []
            for key, value in responses.items():
                out.append({
                    'topic_name': key,
                    'sub_key': value['sub_key'],
                    'current_depth': value['queue_depth'],
                })

            self.response.payload.sub_data = out

# ################################################################################################################################

class UpdateInteractionMetadata(AdminService):
    """ Updates last interaction metadata for input sub keys.
    """
    class SimpleIO:
        input_required = List('sub_key'), Opaque('last_interaction_time'), 'last_interaction_type', 'last_interaction_details'

    def handle(self):

        # Local aliases
        req = self.request.input

        # Convert from string to milliseconds as expected by the database
        last_interaction_time = datetime_to_ms(req.last_interaction_time) / 1000.0

        with closing(self.odb.session()) as session:

            # Run the query
            session.execute(
                update(PubSubSubscription).\
                values({
                    'last_interaction_time': last_interaction_time,
                    'last_interaction_type': req.last_interaction_type,
                    'last_interaction_details': req.last_interaction_details.encode('utf8'),
                    }).\
                where(PubSubSubscription.sub_key.in_(req.sub_key))
            )

            # And commit it to the database
            session.commit()

# ################################################################################################################################
