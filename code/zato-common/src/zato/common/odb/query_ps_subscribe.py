# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# SQLAlchemy
from sqlalchemy import and_, exists, insert
from sqlalchemy.sql import expression as expr, func

# Zato
from zato.common.odb.model import PubSubEndpointEnqueuedMessage, PubSubMessage, PubSubSubscription, WebSocketSubscription

# ################################################################################################################################

def has_subscription(session, cluster_id, topic_id, endpoint_id):
    """ Returns a boolean flag indicating whether input endpoint has subscription to a given topic.
    """
    return session.query(exists().where(and_(
        PubSubSubscription.endpoint_id==endpoint_id,
            PubSubSubscription.topic_id==topic_id,
            PubSubSubscription.cluster_id==cluster_id,
            ))).\
        scalar()

# ################################################################################################################################

def add_wsx_subscription(session, cluster_id, is_internal, sub_key, ext_client_id, ws_channel_id):
    """ Adds an object representing a subscription of a WebSockets client.
    """
    ws_sub = WebSocketSubscription()
    ws_sub.is_internal = is_internal
    ws_sub.sub_key = sub_key
    ws_sub.ext_client_id = ext_client_id
    ws_sub.channel_id = ws_channel_id
    ws_sub.cluster_id = cluster_id
    session.add(ws_sub)

    return ws_sub

# ################################################################################################################################

def add_subscription(session, cluster_id, ctx):
    """ Adds an object representing a subscription regardless of the underlying protocol.
    """
    # Common
    ps_sub = PubSubSubscription()

    ps_sub.cluster_id = ctx.cluster_id
    ps_sub.topic_id = ctx.topic.id
    ps_sub.is_internal = ctx.is_internal
    ps_sub.creation_time = ctx.creation_time
    ps_sub.sub_key = ctx.sub_key
    ps_sub.pattern_matched = ctx.pattern_matched
    ps_sub.has_gd = ctx.has_gd
    ps_sub.active_status = ctx.active_status
    ps_sub.endpoint_type = ctx.endpoint_type
    ps_sub.endpoint_id = ctx.endpoint_id
    ps_sub.delivery_method = ctx.delivery_method
    ps_sub.delivery_data_format = ctx.delivery_data_format
    ps_sub.delivery_batch_size = ctx.delivery_batch_size
    ps_sub.wrap_one_msg_in_list = ctx.wrap_one_msg_in_list
    ps_sub.delivery_max_retry = ctx.delivery_max_retry
    ps_sub.delivery_err_should_block = ctx.delivery_err_should_block
    ps_sub.wait_sock_err = ctx.wait_sock_err
    ps_sub.wait_non_sock_err = ctx.wait_non_sock_err
    ps_sub.ext_client_id = ctx.ext_client_id

    # AMQP
    ps_sub.amqp_exchange = ctx.amqp_exchange
    ps_sub.amqp_routing_key = ctx.amqp_routing_key

    # Local files
    ps_sub.files_directory_list = ctx.files_directory_list

    # FTP
    ps_sub.ftp_directory_list = ctx.ftp_directory_list

    # REST/SOAP
    ps_sub.security_id = ctx.security_id

    # Services
    ps_sub.service_id = ctx.service_id

    # SMS - Twilio
    ps_sub.sms_twilio_from = ctx.sms_twilio_from
    ps_sub.sms_twilio_to_list = ctx.sms_twilio_to_list
    ps_sub.smtp_is_html = ctx.smtp_is_html
    ps_sub.smtp_subject = ctx.smtp_subject
    ps_sub.smtp_from = ctx.smtp_from
    ps_sub.smtp_to_list = ctx.smtp_to_list
    ps_sub.smtp_body = ctx.smtp_body

    # WebSockets
    ps_sub.ws_channel_id = ctx.ws_channel_id
    ps_sub.ws_channel_name = ctx.ws_channel_name
    ps_sub.ws_pub_client_id = ctx.ws_pub_client_id
    ps_sub.sql_ws_client_id = ctx.sql_ws_client_id

    session.add(ps_sub)

    return ps_sub

# ################################################################################################################################

def move_messages_to_sub_queue(session, cluster_id, topic_id, endpoint_id, ps_sub_id, now):
    """ Move all unexpired messages from topic to a given subscriber's queue and returns the number of messages moved.
    """

    # SELECT statement used by the INSERT below finds all messages for that topic
    # that haven't expired yet.
    select_messages = session.query(
        PubSubMessage.pub_msg_id, PubSubMessage.topic_id,
        expr.bindparam('creation_time', now),
        expr.bindparam('delivery_count', 0),
        expr.bindparam('endpoint_id', endpoint_id),
        expr.bindparam('subscription_id', ps_sub_id),
        expr.bindparam('has_gd', False),
        expr.bindparam('is_in_staging', False),
        expr.bindparam('cluster_id', cluster_id),
        ).\
        filter(PubSubMessage.topic_id==topic_id).\
        filter(PubSubMessage.cluster_id==cluster_id).\
        filter(PubSubMessage.expiration_time > now)

    # INSERT references to topic's messages in the subscriber's queue.
    insert_messages = insert(PubSubEndpointEnqueuedMessage).\
        from_select((
            PubSubEndpointEnqueuedMessage.pub_msg_id,
            PubSubEndpointEnqueuedMessage.topic_id,
            expr.column('creation_time'),
            expr.column('delivery_count'),
            expr.column('endpoint_id'),
            expr.column('subscription_id'),
            expr.column('has_gd'),
            expr.column('is_in_staging'),
            expr.column('cluster_id'),
            ), select_messages)

    # Commit changes to subscriber's queue
    session.execute(insert_messages)

    # Get the number of messages moved to let the subscriber know
    # how many there are available initially.
    moved_q = session.query(PubSubEndpointEnqueuedMessage.id).\
        filter(PubSubEndpointEnqueuedMessage.subscription_id==ps_sub_id).\
        filter(PubSubEndpointEnqueuedMessage.cluster_id==cluster_id)

    total_moved_q = moved_q.statement.with_only_columns([func.count()]).order_by(None)
    total_moved = moved_q.session.execute(total_moved_q).scalar()

    return total_moved

# ################################################################################################################################

'''
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
from zato.common.odb.model import PubSubEndpoint, PubSubSubscription
from zato.common.odb.query_ps_subscribe import add_subscription, add_wsx_subscription, has_subscription, \
     move_messages_to_sub_queue
from zato.common.odb.query_ps_subscription import pubsub_endpoint_summary_list
from zato.common.pubsub import new_sub_key
from zato.common.time_util import datetime_from_ms, utcnow_as_ms
from zato.common.util import make_repr
from zato.server.connection.web_socket import WebSocket
from zato.server.pubsub import PubSub, Topic
from zato.server.service import AsIs, Bool, Int, Opaque
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################

# For pyflakes and code completion
PubSub = PubSub
Topic = Topic
WebSocket = WebSocket

# ################################################################################################################################

sub_broker_attrs = ('active_status', 'active_status', 'cluster_id', 'creation_time', 'endpoint_id', 'has_gd', 'id', 'is_durable',
    'is_internal', 'name', 'out_amqp_id', 'out_http_soap_id', 'sub_key', 'topic_id', 'ws_channel_id','ws_sub_id',
    'delivery_batch_size')

# ################################################################################################################################

class SubCtx(object):
    """ A container for information pertaining to a given subscription request.
    """
    def __init__(self, cluster_id, pubsub):
        self.pubsub = pubsub # type: PubSub
        self.cluster_id = cluster_id
        self.has_gd = None
        self.pattern_matched = None
        self.topic = None # type: Topic
        self.topic_name = None
        self.is_internal = None
        self.topic_list_text = None
        self.topic_list_json = None
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
    common = ('is_internal', 'topic_list_text', 'topic_list_json', 'active_status', 'endpoint_type', 'endpoint_id',
              'delivery_method', 'delivery_data_format', 'delivery_batch_size', 'wrap_one_msg_in_list', 'delivery_max_retry',
        'delivery_err_should_block', 'wait_sock_err', 'wait_non_sock_err')
    amqp = ('amqp_exchange', 'amqp_routing_key')
    files = ('files_directory_list',)
    ftp = ('ftp_directory_list',)
    pubapi = ('security_id',)
    rest = ('out_rest_http_soap_id', 'rest_delivery_endpoint')
    service = ('service_id',)
    sms_twilio = ('sms_twilio_from', 'sms_twilio_to_list')
    smtp = ('smtp_is_html', 'smtp_subject', 'smtp_from', 'smtp_to_list', 'smtp_body')
    soap = ('out_soap_http_soap_id', 'soap_delivery_endpoint')
    websockets = ('ws_channel_id', 'ws_channel_name', AsIs('ws_pub_client_id'), 'sql_ws_client_id', AsIs('ext_client_id'),
                  Opaque('web_socket'))

_create_edit_input_optional = _Input.common + _Input.amqp + _Input.files + _Input.ftp + _Input.rest + _Input.service + \
    _Input.sms_twilio + _Input.smtp + _Input.soap + _Input.websockets + _Input.pubapi

# ################################################################################################################################

class GetEndpointSummaryList(AdminService):
    """ Returns summarized information about endpoints subscribed to topics.
    """
    _filter_by = PubSubEndpoint.name,

    class SimpleIO(GetListAdminSIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'endpoint_name', 'endpoint_type', 'subscription_count', 'is_active', 'is_internal')
        output_optional = ('security_id', 'sec_type', 'sec_name', 'ws_channel_id', 'ws_channel_name',
                           'service_id', 'service_name', 'last_seen', 'last_deliv_time', 'role')
        request_elem = 'zato_pubsub_subscription_get_endpoint_summary_list_request'
        response_elem = 'zato_pubsub_subscription_get_endpoint_summary_list_response'

    def get_data(self, session):
        result = self._search(pubsub_endpoint_summary_list, session, self.request.input.cluster_id, False)
        for item in result:

            if item.last_seen:
                item.last_seen = datetime_from_ms(item.last_seen)

            if item.last_deliv_time:
                item.last_deliv_time = datetime_from_ms(item.last_deliv_time)

        return result

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################

class SubscribeServiceImpl(AdminService):
    """ Lower-level service that actually handles pub/sub subscriptions. Each endpoint_type has its own subclass.
    """
    endpoint_type = None

    class SimpleIO(AdminSIO):
        input_required = ('topic_name', 'is_internal')
        input_optional = _create_edit_input_optional
        output_optional = ('sub_key', Int('queue_depth'))
        default_value = None

# ################################################################################################################################

    def get_pattern_matched(self, topic_name, ws_channel_id, sql_ws_client_id, security_id, endpoint_id):
        pubsub = self.server.worker_store.pubsub

        if ws_channel_id and (not sql_ws_client_id):
            raise BadRequest(self.cid, 'sql_ws_client_id must not be empty if ws_channel_id is given on input')

        # Confirm if this client may subscribe at all to the topic it chose
        kwargs = {'security_id':security_id} if security_id else {'ws_channel_id':ws_channel_id}
        pattern_matched = pubsub.is_allowed_sub_topic(topic_name, **kwargs)

        # Not allowed - raise an exception then
        if not pattern_matched:
            raise Forbidden(self.cid)

        # Alright, we can proceed
        else:
            return pattern_matched

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

    def _subscribe_impl(self, ctx):
        raise NotImplementedError('Must be implement by subclasses')

# ################################################################################################################################

    def handle(self):
        # Get basic pub/sub subscription context
        ctx = self._get_sub_ctx()

        # Confirm correctness of input data, including whether the caller can subscribe
        # to this topic and if the topic exists at all.
        ctx.pattern_matched = self.get_pattern_matched(
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
        self._subscribe_impl(ctx)

# ################################################################################################################################

class SubscribeWebSockets(SubscribeServiceImpl):
    """ Handles pub/sub subscriptions for WebSockets.
    """
    endpoint_type = PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id

    name = 'subscribe-websockets'

    def _subscribe_impl(self, ctx):
        # type: (SubCtxWebSockets)

        # This is a WebSocket so delivery_method is always fixed
        ctx.delivery_method = PUBSUB.DELIVERY_METHOD.WEB_SOCKET.id

        with self.lock('zato.pubsub.subscribe.%s.%s' % (ctx.topic_name, ctx.endpoint_id)):

            with closing(self.odb.session()) as session:

                # Non-WebSocket clients cannot subscribe to the same topic multiple times
                if not ctx.ws_channel_id:
                    if has_subscription(session, ctx.cluster_id, ctx.topic.id, ctx.endpoint_id):
                        raise PubSubSubscriptionExists(self.cid, 'Subscription to topic `{}` already exists'.format(topic.name))

                ctx.creation_time = now = utcnow_as_ms()
                ctx.sub_key = new_sub_key()

                # If we subscribe a WSX client, we need to create its accompanying SQL models
                if ctx.ws_channel_id:

                    # This object persists across multiple WSX connections
                    ws_sub = add_wsx_subscription(
                        session, ctx.cluster_id, ctx.is_internal, ctx.sub_key, ctx.ext_client_id, ctx.ws_channel_id)

                    # This object will be transient - dropped each time a WSX disconnects
                    self.pubsub.add_ws_client_pubsub_keys(session, ctx.sql_ws_client_id, ctx.sub_key, ctx.ws_channel_name,
                        ctx.ws_pub_client_id)

                    # Let the WebSocket connection object know that it should handle this particular sub_key
                    ctx.web_socket.pubsub_tool.add_sub_key(ctx.sub_key)

                else:
                    ws_sub = None

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

                for name in sub_broker_attrs:
                    broker_input[name] = getattr(ps_sub, name, None)

                broker_input.action = BROKER_MSG_PUBSUB.SUBSCRIPTION_CREATE.value
                self.broker_client.publish(broker_input)

# ################################################################################################################################
'''
