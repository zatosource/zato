# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime, timedelta

# Bunch
from bunch import Bunch

# gevent
from gevent import spawn

# rapidjson
from rapidjson import dumps, loads

# SQLAlchemy
from sqlalchemy import and_, exists, insert, select, update
from sqlalchemy.sql import expression as expr, func
from sqlalchemy.sql.functions import coalesce

# Zato
from zato.common import CONTENT_TYPE, DATA_FORMAT, PUBSUB
from zato.common.broker_message import PUBSUB as BROKER_MSG_PUBSUB
from zato.common.exception import BadRequest, NotFound, Forbidden, PubSubSubscriptionExists, ServiceUnavailable, TooManyRequests
from zato.common.odb.model import ChannelWebSocket, PubSubTopic, PubSubEndpoint, PubSubEndpointEnqueuedMessage, \
     PubSubEndpointTopic, PubSubMessage, PubSubSubscription, SecurityBase, Service as ODBService, ChannelWebSocket, \
     WebSocketClient, WebSocketSubscription, WebSocketClientPubSubKeys
from zato.common.odb.query import pubsub_message, pubsub_messages_for_queue, pubsub_queue_message, query_wrapper
from zato.common.pubsub import new_msg_id, new_sub_key
from zato.common.time_util import datetime_from_ms, datetime_to_ms, utcnow_as_ms
from zato.common.util import new_cid
from zato.server.connection.web_socket import WebSocket
from zato.server.pubsub import get_expiration, get_priority
from zato.server.service import AsIs, Bool, Int, ListOfDicts, Opaque, Service
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

sub_broker_attrs = ('active_status', 'active_status', 'cluster_id', 'creation_time', 'endpoint_id', 'has_gd', 'id',
    'is_durable', 'is_internal', 'name', 'out_amqp_id', 'out_http_soap_id', 'sub_key', 'topic_id', 'ws_channel_id',
    'ws_sub_id', 'delivery_group_size')

# For pyflakes
WebSocket = WebSocket

# ################################################################################################################################

def parse_basic_auth(auth, prefix = 'Basic '):
    if not auth.startswith(prefix):
        raise ValueError('Missing Basic Auth prefix')

    _, auth = auth.split(prefix)
    auth = auth.strip().decode('base64')

    return auth.split(':', 1)

# ################################################################################################################################

class PubSubService(Service):
    class SimpleIO:
        input_required = ('topic_name',)
        input_optional = (Bool('gd'),)
        response_elem = None

    def _pubsub_check_credentials(self):
        auth = self.wsgi_environ.get('HTTP_AUTHORIZATION')
        if not auth:
            raise Forbidden(self.cid)

        try:
            username, password = parse_basic_auth(auth)
        except ValueError:
            raise Forbidden(self.cid)

        basic_auth = self.server.worker_store.request_dispatcher.url_data.basic_auth_config.itervalues()

        for item in basic_auth:
            config = item['config']
            if config['is_active']:
                if config['username'] == username and config['password'] == password:
                    auth_ok = True
                    security_id = config['id']
                    break
                else:
                    auth_ok = False

        if not auth_ok:
            raise Forbidden(self.cid)

        return security_id

# ################################################################################################################################

class TopicService(PubSubService):
    """ Main service responsible for publications to a given topic. Handles security and distribution
    of messages to target queues.
    """
    class SimpleIO(PubSubService.SimpleIO):
        input_optional = PubSubService.SimpleIO.input_optional + (
            Int('priority'), Int('expiration'), 'mime_type', AsIs('correl_id'), 'in_reply_to', AsIs('ext_client_id'))
        output_optional = (AsIs('msg_id'),)

# ################################################################################################################################

    def handle_POST(self):

        # Check credentials first
        security_id = self._pubsub_check_credentials()

        # Regardless of mime-type, we always accept it in JSON payload
        try:
            data_parsed = loads(self.request.raw_request)
        except ValueError:
            raise BadRequest(self.cid, 'JSON input could not be parsed')
        else:
            data = self.request.raw_request

        # Ignore the header set by curl and similar tools
        mime_type = self.wsgi_environ.get('CONTENT_TYPE')
        mime_type = mime_type if mime_type != 'application/x-www-form-urlencoded' else CONTENT_TYPE.JSON

        input = self.request.input

        self.response.payload.msg_id = self.invoke('zato.pubsub.message.publish', {
            'topic_name': input.topic_name,
            'mime_type': mime_type,
            'security_id': security_id,
            'data': data,
            'data_parsed': data_parsed,
            'priority': input.priority,
            'expiration': input.expiration,
            'correl_id': input.correl_id,
            'in_reply_to': input.in_reply_to,
            'ext_client_id': input.ext_client_id,
            'has_gd': input.gd,
        })['response']['msg_id']

# ################################################################################################################################

class SubscribeServiceImpl(AdminService):
    name = 'pubapi1.subscribe-service-impl'

    class SimpleIO(AdminSIO):
        input_required = ('topic_name',)
        input_optional = (Bool('gd'), 'deliver_to', 'delivery_format', 'security_id', 'ws_channel_id',
            'sql_ws_client_id', 'deliver_by', 'is_internal', AsIs('ext_client_id'), 'delivery_group_size')
        output_optional = ('sub_key', Int('queue_depth'))

# ################################################################################################################################

    def handle(self):

        input = self.request.input
        topic_name = self.request.input.topic_name
        pubsub = self.server.worker_store.pubsub

        security_id = input.security_id or None
        ws_channel_id = input.ws_channel_id or None
        sql_ws_client_id = input.sql_ws_client_id or None

        if ws_channel_id and (not sql_ws_client_id):
            raise BadRequest(self.cid, 'sql_ws_client_id must not be empty if ws_channel_id is given on input')

        if security_id:
            endpoint_id = pubsub.get_endpoint_id_by_sec_id(security_id)
        elif ws_channel_id:
            endpoint_id = pubsub.get_endpoint_id_by_ws_channel_id(ws_channel_id)
        else:
            raise NotImplementedError('To be implemented')

        # Confirm if this client may subscribe at all to the topic it chose
        kwargs = {'security_id':security_id} if security_id else {'ws_channel_id':ws_channel_id}
        pattern_matched = pubsub.is_allowed_sub_topic(topic_name, **kwargs)
        if not pattern_matched:
            raise Forbidden(self.cid)

        try:
            topic = pubsub.get_topic_by_name(topic_name)
        except KeyError:
            raise NotFound(self.cid, 'No such topic `{}`'.format(topic_name))

        has_gd = input.gd if isinstance(input.gd, bool) else topic.has_gd
        is_internal = input.is_internal or False

        delivery_data_format = input.delivery_format or None
        deliver_to = input.deliver_to or None
        deliver_by = input.deliver_by or 'priority,ext_pub_time,pub_time'
        delivery_group_size = input.delivery_group_size or 1

        if input.ws_channel_id:
            delivery_method = PUBSUB.DELIVERY_METHOD.WEB_SOCKET
        else:
            delivery_method = PUBSUB.DELIVERY_METHOD.NOTIFY if deliver_to else PUBSUB.DELIVERY_METHOD.PULL

        with self.lock('zato.pubsub.subscribe.%s.%s' % (topic_name, endpoint_id)):

            with closing(self.odb.session()) as session:

                # Non-WebSocket clients cannot subscribe to the same topic multiple times
                if not ws_channel_id:
                    sub_exists = session.query(exists().where(and_(
                        PubSubSubscription.endpoint_id==endpoint_id,
                            PubSubSubscription.topic_id==topic.id,
                            PubSubSubscription.cluster_id==self.server.cluster_id,
                            ))).\
                        scalar()

                    if sub_exists:
                        raise PubSubSubscriptionExists(self.cid, 'Subscription to topic `{}` already exists'.format(topic.name))

                now = utcnow_as_ms()
                sub_key = new_sub_key()

                # If we subscribe a WSX client, we need to create its accompanying SQL models
                if ws_channel_id:

                    # This object persists across multiple WSX connections
                    ws_sub = WebSocketSubscription()
                    ws_sub.is_internal = is_internal
                    ws_sub.sub_key = sub_key
                    ws_sub.ext_client_id = input.ext_client_id
                    ws_sub.channel_id = ws_channel_id
                    ws_sub.cluster_id = self.server.cluster_id
                    session.add(ws_sub)

                    # This object is transient - it will be dropped each time a WSX client disconnects
                    ws_sub_key = WebSocketClientPubSubKeys()
                    ws_sub_key.client_id = sql_ws_client_id
                    ws_sub_key.sub_key = sub_key
                    ws_sub_key.cluster_id = self.server.cluster_id
                    session.add(ws_sub_key)

                else:
                    ws_sub = None

                # Create a new subscription object
                ps_sub = PubSubSubscription()
                ps_sub.active_status = PUBSUB.QUEUE_ACTIVE_STATUS.FULLY_ENABLED.id
                ps_sub.is_internal = False
                ps_sub.creation_time = now
                ps_sub.pattern_matched = pattern_matched
                ps_sub.sub_key = sub_key
                ps_sub.has_gd = has_gd
                ps_sub.topic_id = topic.id
                ps_sub.endpoint_id = endpoint_id
                ps_sub.delivery_method = delivery_method
                ps_sub.delivery_data_format = delivery_data_format
                ps_sub.delivery_endpoint = deliver_to
                ps_sub.deliver_by = deliver_by
                ps_sub.delivery_group_size = delivery_group_size
                ps_sub.ws_channel_id = ws_channel_id
                ps_sub.ws_sub = ws_sub
                ps_sub.cluster_id = self.server.cluster_id

                session.add(ps_sub)
                session.flush() # Flush the session because we need the subscription's ID below in INSERT from SELECT

                # SELECT statement used by the INSERT below finds all messages for that topic
                # that haven't expired yet.
                select_messages = session.query(
                    PubSubMessage.pub_msg_id, PubSubMessage.topic_id,
                    expr.bindparam('creation_time', now),
                    expr.bindparam('delivery_count', 0),
                    expr.bindparam('endpoint_id', endpoint_id),
                    expr.bindparam('subscription_id', ps_sub.id),
                    expr.bindparam('has_gd', False),
                    expr.bindparam('is_in_staging', False),
                    expr.bindparam('cluster_id', self.server.cluster_id),
                    ).\
                    filter(PubSubMessage.topic_id==topic.id).\
                    filter(PubSubMessage.cluster_id==self.server.cluster_id).\
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
                    filter(PubSubEndpointEnqueuedMessage.subscription_id==ps_sub.id).\
                    filter(PubSubEndpointEnqueuedMessage.cluster_id==self.server.cluster_id)

                total_moved_q = moved_q.statement.with_only_columns([func.count()]).order_by(None)
                total_moved = moved_q.session.execute(total_moved_q).scalar()

                session.commit()

                # Produce response
                self.response.payload.sub_key = sub_key
                self.response.payload.queue_depth = total_moved

                # Notify workers of a new subscription
                broker_input = Bunch()
                broker_input.topic_name = topic.name

                for name in sub_broker_attrs:
                    broker_input[name] = getattr(ps_sub, name, None)

                broker_input.action = BROKER_MSG_PUBSUB.SUBSCRIPTION_CREATE.value
                self.broker_client.publish(broker_input)

# ################################################################################################################################

class SubscribeService(PubSubService):
    """ Service through which HTTP Basic Auth-using clients subscribe to topics.
    """
    class SimpleIO(PubSubService.SimpleIO):
        input_optional = PubSubService.SimpleIO.input_optional + ('deliver_to', 'delivery_format')
        output_optional = ('sub_key', Int('queue_depth'))

    def handle_POST(self, _new_cid=new_cid, _utcnow=datetime.utcnow):

        # Check credentials first
        security_id = self._pubsub_check_credentials()

        response = self.invoke('pubapi1.subscribe-service-impl', {
            'topic_name': self.request.input.topic_name,
            'security_id': security_id,
            'has_gd': self.request.input.gd,
            'deliver_to': self.request.input.deliver_to,
            'delivery_format': self.request.input.delivery_format,
        })['response']

        self.response.payload.sub_key = response['sub_key']
        self.response.payload.queue_depth = response['queue_depth']

# ################################################################################################################################

    def handle_GET(self):
        pass

# ################################################################################################################################

class Hook1(AdminService):
    pass

# ################################################################################################################################

class Hook2(AdminService):
    pass

# ################################################################################################################################

class PubSubNotifyMessagePublished(AdminService):
    """ Notifies an individual WebSocket client that messages related to a specific sub_key became available.
    """
    def handle(self):
        web_socket = self.request.raw_request['web_socket'] # type: WebSocket
        has_gd = self.request.raw_request['request']['has_gd']
        sub_key = self.request.raw_request['request']['sub_key']

        # Find all WSX clients currently connected to our server process and try to deliver new messages to them.

        self.logger.info('Got sub_key %s for %s', sub_key, web_socket.pub_client_id)

        with closing(self.odb.session()) as session:
            messages = session.query(PubSubMessage).\
                filter(PubSubEndpointEnqueuedMessage.pub_msg_id==PubSubMessage.pub_msg_id).\
                filter(PubSubEndpointEnqueuedMessage.subscription_id==PubSubSubscription.id).\
                filter(PubSubSubscription.sub_key==sub_key).\
                order_by(PubSubMessage.priority.desc()).\
                order_by(func.coalesce(PubSubMessage.ext_pub_time, PubSubMessage.pub_time)).\
                order_by(PubSubMessage.group_id).\
                order_by(PubSubMessage.position_in_group).\
                all()

            for msg in messages:
                ext_pub_time = datetime_from_ms(msg.ext_pub_time)
                pub_time = datetime_from_ms(msg.pub_time)

                print(msg.priority, ext_pub_time, pub_time, msg.group_id, msg.position_in_group)

# ################################################################################################################################

class PubSubAfterPublish(AdminService):
    class SimpleIO(AdminSIO):
        input_required = ('topic_name',)
        input_optional = (Opaque('subscriptions'), Opaque('non_gd_messages'))

    def handle(self):
        topic_name = self.request.input.topic_name

        # Notify all background tasks that new messages are available for their recipients.
        # However, this needs to take into account the fact that there may be many notifications
        # pointing to a single server so instead of sending notifications one by one,
        # we first find all servers and then notify each server once giving it a list of subscriptions
        # on input.

        # We also need to remember that recipients may be currently offline, in which case we do nothing
        # for GD messages but for non-GD ones, we keep them in our server's RAM.

        server_messages = {} # Server name/PID/channel_name -> sub keys
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
