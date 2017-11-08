# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from datetime import datetime

# datetutil
from dateparser import parse as dt_parse

# gevent
from gevent import spawn

# SQLAlchemy
from sqlalchemy import and_, exists, select, update
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common import DATA_FORMAT
from zato.common.exception import BadRequest, Forbidden, NotFound, ServiceUnavailable
from zato.common.odb.model import PubSubTopic, PubSubEndpoint, PubSubEndpointEnqueuedMessage, PubSubEndpointTopic, PubSubMessage
from zato.common.odb.query import pubsub_message, pubsub_queue_message
from zato.common.pubsub import new_msg_id
from zato.common.time_util import datetime_to_ms, datetime_from_ms, utcnow_as_ms
from zato.server.pubsub import get_expiration, get_priority
from zato.server.service import AsIs, Bool, Int, List
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

_JSON = DATA_FORMAT.JSON

MsgInsert = PubSubMessage.__table__.insert
EndpointTopicInsert = PubSubEndpointTopic.__table__.insert
EnqueuedMsgInsert = PubSubEndpointEnqueuedMessage.__table__.insert

Topic = PubSubTopic.__table__
Endpoint = PubSubEndpoint.__table__
EndpointTopic = PubSubEndpointTopic.__table__

# ################################################################################################################################

class GetFromTopic(AdminService):
    """ Returns a pub/sub topic message by its ID.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', AsIs('msg_id'))
        output_optional = ('topic_id', 'topic_name', AsIs('msg_id'), AsIs('correl_id'), 'in_reply_to', 'pub_time', \
            'ext_pub_time', 'pattern_matched', 'priority', 'data_format', 'mime_type', 'size', 'data',
            'expiration', 'expiration_time', 'endpoint_id', 'endpoint_name', Bool('has_gd'),
            'pub_hook_service_id', 'pub_hook_service_name', AsIs('ext_client_id'))

    def handle(self):
        with closing(self.odb.session()) as session:

            item = pubsub_message(session, self.request.input.cluster_id, self.request.input.msg_id).\
                first()

            if item:
                item.pub_time = datetime_from_ms(item.pub_time)
                item.ext_pub_time = datetime_from_ms(item.ext_pub_time) if item.ext_pub_time else ''
                item.expiration_time = datetime_from_ms(item.expiration_time) if item.expiration_time else ''
                self.response.payload = item
            else:
                raise NotFound(self.cid, 'No such message `{}`'.format(self.request.input.msg_id))

# ################################################################################################################################

class Has(AdminService):
    """ Returns a boolean flag to indicate whether a given message by ID exists in pub/sub.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', AsIs('msg_id'))
        output_required = (Bool('found'),)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload.found = session.query(
                exists().where(and_(
                    PubSubMessage.pub_msg_id==self.request.input.msg_id,
                    PubSubMessage.cluster_id==self.server.cluster_id,
                    ))).\
                scalar()

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a message by its ID. Cascades to all related SQL objects, e.g. subscriber queues.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', AsIs('msg_id'))

    def handle(self):
        with closing(self.odb.session()) as session:
            ps_msg = session.query(PubSubMessage).\
                filter(PubSubMessage.cluster_id==self.request.input.cluster_id).\
                filter(PubSubMessage.pub_msg_id==self.request.input.msg_id).\
                first()

            if not ps_msg:
                raise NotFound(self.cid, 'Message not found `{}`'.format(self.request.input.msg_id))

            ps_topic = session.query(PubSubTopic).\
                filter(PubSubTopic.cluster_id==self.request.input.cluster_id).\
                filter(PubSubTopic.id==ps_msg.topic_id).\
                one()

            # Delete the message and decrement its topic's current depth ..
            session.delete(ps_msg)
            ps_topic.current_depth = ps_topic.current_depth - 1

            # .. but do it under a global lock because other transactions may want to update the topic in parallel.
            with self.lock('zato.pubsub.publish.%s' % ps_topic.name):
                session.commit()

# ################################################################################################################################

class Update(AdminService):
    """ Updates details of an individual message.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', AsIs('msg_id'), 'mime_type')
        input_optional = ('data', Int('expiration'), AsIs('correl_id'), AsIs('in_reply_to'), Int('priority'))
        output_required = (Bool('found'),)
        output_optional = ('expiration_time', Int('size'))

    def handle(self, _utcnow=datetime.utcnow):
        input = self.request.input

        with closing(self.odb.session()) as session:
            item = session.query(PubSubMessage).\
                filter(PubSubMessage.cluster_id==input.cluster_id).\
                filter(PubSubMessage.pub_msg_id==input.msg_id).\
                first()

            if not item:
                self.response.payload.found = False
                return

            item.data = input.data.encode('utf8')
            item.data_prefix = input.data[:2048].encode('utf8')
            item.data_prefix_short = input.data[:64].encode('utf8')
            item.size = len(input.data)
            item.expiration = get_expiration(self.cid, input)
            item.priority = get_priority(self.cid, input)

            item.pub_correl_id = input.correl_id
            item.in_reply_to = input.in_reply_to
            item.mime_type = input.mime_type

            if item.expiration:
                item.expiration_time = item.pub_time + (item.expiration * 1000)
            else:
                item.expiration_time = None

            session.add(item)
            session.commit()

            self.response.payload.found = True
            self.response.payload.size = item.size
            self.response.payload.expiration_time = datetime_from_ms(item.expiration_time) if item.expiration_time else None

# ################################################################################################################################

class GetFromQueue(AdminService):
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', AsIs('msg_id'))
        output_optional = (AsIs('msg_id'), 'recv_time', 'data', Int('delivery_count'), 'last_delivery_time',
            'is_in_staging', 'has_gd', 'queue_name', 'endpoint_id', 'endpoint_name', 'size', 'priority', 'mime_type',
            'sub_pattern_matched', AsIs('correl_id'), 'in_reply_to', 'expiration', 'expiration_time',
            AsIs('sub_hook_service_id'), 'sub_hook_service_name', AsIs('ext_client_id'))

    def handle(self):

        with closing(self.odb.session()) as session:

            item = pubsub_queue_message(session, self.request.input.cluster_id, self.request.input.msg_id).\
                first()

            if item:
                item.expiration = item.expiration or None
                for name in('expiration_time', 'recv_time', 'ext_pub_time', 'last_delivery_time'):
                    value = getattr(item, name, None)
                    if value:
                        setattr(item, name, datetime_from_ms(value))

                self.response.payload = item
            else:
                raise NotFound(self.cid, 'No such message `{}`'.format(self.request.input.msg_id))

# ################################################################################################################################

class Publish(AdminService):
    """ Actual implementation of message publishing exposed through other services to the outside world.
    """
    class SimpleIO:
        input_required = ('topic_name',)
        input_optional = ('data', List('data_list'), AsIs('msg_id'), 'has_gd', Int('priority'), Int('expiration'), 'mime_type',
            AsIs('correl_id'), 'in_reply_to', AsIs('ext_client_id'), 'ext_pub_time', 'pattern_matched', 'security_id',
            'ws_channel_id', 'service_id', 'data_parsed', 'meta', AsIs('group_id'),
            Int('position_in_group'), 'endpoint_id')
        output_optional = (AsIs('msg_id'), List('msg_id_list'))

# ################################################################################################################################

    def _get_message(self, topic, input, now, pattern_matched, endpoint_id):

        priority = get_priority(self.cid, input)
        expiration = get_expiration(self.cid, input)
        expiration_time = now + (expiration * 1000)

        pub_msg_id = input.get('msg_id', '').encode('utf8') or new_msg_id()
        has_gd = input['has_gd'] if isinstance(input.get('has_gd'), bool) else topic.has_gd

        pub_correl_id = input.get('correl_id')
        in_reply_to = input.get('in_reply_to')
        ext_client_id = input.get('ext_client_id')

        ext_pub_time = input.get('ext_pub_time')
        if ext_pub_time:
            ext_pub_time = dt_parse(ext_pub_time)
            ext_pub_time = datetime_to_ms(ext_pub_time)

        pub_correl_id = pub_correl_id.encode('utf8') if pub_correl_id else None
        in_reply_to = in_reply_to.encode('utf8') if in_reply_to else None
        ext_client_id = ext_client_id.encode('utf8') if ext_client_id else None

        ps_msg = {
            'pub_msg_id': pub_msg_id,
            'pub_correl_id': pub_correl_id,
            'in_reply_to': in_reply_to,
            'pub_time': now,
            'pattern_matched': pattern_matched,
            'data': input['data'].encode('utf8'),
            'data_prefix': input['data'][:2048].encode('utf8'),
            'data_prefix_short': input['data'][:64].encode('utf8'),
            'mime_type': input.get('mime_type', 'text/plain'),
            'size': len(input['data']),
            'priority': priority,
            'expiration': expiration,
            'expiration_time': expiration_time,
            'published_by_id': endpoint_id,
            'topic_id': topic.id,
            'cluster_id': self.server.cluster_id,
            'has_gd': has_gd,
            'ext_client_id': ext_client_id,
            'ext_pub_time': ext_pub_time,
            'group_id': input.get('group_id') or None,
            'position_in_group': input.get('position_in_group') or None,
        }

        return ps_msg

# ################################################################################################################################

    def _get_messages_from_data(self, topic, data_list, input, now, pattern_matched, endpoint_id):

        ps_msg_list = []

        if data_list and isinstance(data_list, (list, tuple)):
            for elem in data_list:
                ps_msg_list.append(self._get_message(topic, elem, now, pattern_matched, endpoint_id))
        else:
            ps_msg_list.append(self._get_message(topic, input, now, pattern_matched, endpoint_id))

        return ps_msg_list

# ################################################################################################################################

    def _notify_pubsub_task_runners(self, topic_name, subscriptions):
        spawn(self.invoke, 'pubapi1.pub-sub-after-publish', {'topic_name':topic_name, 'subscriptions': subscriptions})

# ################################################################################################################################

    def handle(self):

        input = self.request.input
        pubsub = self.server.worker_store.pubsub
        endpoint_id = input.endpoint_id
        security_id = input.security_id or None
        ws_channel_id = input.ws_channel_id or None

        if not endpoint_id:

            if security_id:
                endpoint_id = pubsub.get_endpoint_id_by_sec_id(security_id)
            elif ws_channel_id:
                endpoint_id = pubsub.get_endpoint_id_by_ws_channel_id(ws_channel_id)
            else:
                raise NotImplementedError('To be implemented')

        #if input.get('skip_pattern_matching'):
        #    pattern_matched = PUBSUB.SKIPPED_PATTERN_MATCHING
        #else:
        # Confirm if this client may publish at all to the topic it chose
        kwargs = {'security_id':security_id} if security_id else {'ws_channel_id':ws_channel_id}
        pattern_matched = pubsub.is_allowed_sub_topic(input.topic_name, **kwargs)
        if not pattern_matched:
            raise Forbidden(self.cid)

        try:
            topic = pubsub.get_topic_by_name(input.topic_name)
        except KeyError:
            raise NotFound(self.cid, 'No such topic `{}`'.format(input.topic_name))

        now = utcnow_as_ms()

        # If input.data is a list, it means that it is a list of messages, each of which has its own
        # metadata. Otherwise, it's a string to publish and other input parameters describe it.
        data_list = input.data_list if input.data_list else None
        ps_msg_list = self._get_messages_from_data(topic, data_list, input, now, pattern_matched, endpoint_id)

        # Get all subscribers for that topic from local worker store
        subscriptions_by_topic = pubsub.get_subscriptions_by_topic(input.topic_name)

        # Operate under a global lock for that topic to rule out any interference
        with self.lock('zato.pubsub.publish.%s' % input.topic_name):

            with closing(self.odb.session()) as session:

                # Get current depth of this topic
                current_depth = session.execute(
                    select([Topic.c.current_depth]).\
                    where(Topic.c.id==topic.id).\
                    where(Topic.c.cluster_id==self.server.cluster_id)
                    ).\
                    fetchone()[0]

                # Abort if max depth is already reached ..
                if current_depth >= topic.max_depth:
                    raise ServiceUnavailable(self.cid, 'Max depth already reached for `{}`'.format(topic.name))

                # .. otherwise, update current depth and timestamp of last publication to the topic.
                else:
                    session.execute(
                        update(Topic).\
                        values({
                            'current_depth': Topic.c.current_depth + len(ps_msg_list),
                            'last_pub_time': now
                            }).\
                        where(Topic.c.id==topic.id).\
                        where(Topic.c.cluster_id==self.server.cluster_id)
                    )

                # Insert the message and get its ID back
                try:
                    msg_insert_result = session.execute(MsgInsert().values(ps_msg_list))
                except IntegrityError, e:
                    if 'pubsb_msg_pubmsg_id_idx' in e.message:
                        raise BadRequest(self.cid, 'Duplicate msg_id:`{}`'.format(pub_msg_id))
                    else:
                        raise

                if subscriptions_by_topic:
                    queue_msgs = []
                    for sub in subscriptions_by_topic:
                        for ps_msg in ps_msg_list:
                            queue_msgs.append({
                                'creation_time': now,
                                'delivery_count': 0,
                                'pub_msg_id': ps_msg['pub_msg_id'],
                                'endpoint_id': sub.endpoint_id,
                                'topic_id': topic.id,
                                'subscription_id': sub.id,
                                'cluster_id': self.server.cluster_id,
                                'has_gd': False,
                                'is_in_staging': False,
                            })

                    # Move the message to endpoint queues
                    session.execute(EnqueuedMsgInsert().values(queue_msgs))

                session.commit()

        # Update metadata in background
        last_pub_msg_id = ps_msg_list[-1]['pub_msg_id']
        last_pub_correl_id = ps_msg_list[-1]['pub_correl_id']
        last_in_reply_to = ps_msg_list[-1]['in_reply_to']
        last_ext_client_id = ps_msg_list[-1]['ext_client_id']

        spawn(self._update_pub_metadata, topic.id, endpoint_id, self.server.cluster_id, now, last_pub_msg_id,
            last_pub_correl_id, last_pub_correl_id, pattern_matched, last_ext_client_id)

        # Also in background, notify pub/sub task runners that there are new messages for them
        if subscriptions_by_topic:
            self._notify_pubsub_task_runners(topic.name, subscriptions_by_topic)

        if len(ps_msg_list) == 1:
            self.response.payload.msg_id = last_pub_msg_id
        else:
            self.response.payload.msg_id_list = [elem['pub_msg_id'] for elem in ps_msg_list]

# ################################################################################################################################

    def _update_pub_metadata(self, topic_id, endpoint_id, cluster_id, now, pub_msg_id, pub_correl_id, in_reply_to,
        pattern_matched, ext_client_id):
        """ Updates in background metadata about a topic and publisher after each publication.
        """
        with closing(self.odb.session()) as session:

            # Update information when this endpoint last published to the topic
            endpoint_topic = session.execute(
                select([EndpointTopic.c.id]).\
                where(EndpointTopic.c.topic_id==topic_id).\
                where(EndpointTopic.c.endpoint_id==endpoint_id).\
                where(EndpointTopic.c.cluster_id==cluster_id)
                ).\
                fetchone()

            # Never published before - add a new row then
            if not endpoint_topic:

                session.execute(
                    EndpointTopicInsert(), [{
                        'endpoint_id': endpoint_id,
                    'topic_id': topic_id,
                    'cluster_id': cluster_id,

                    'last_pub_time': now,
                    'pub_msg_id': pub_msg_id,
                    'pub_correl_id': pub_correl_id,
                    'in_reply_to': in_reply_to,
                    'pattern_matched': pattern_matched,
                    'ext_client_id': ext_client_id,
                    }])

            # Already published before - update its metadata in that case.
            else:
                session.execute(
                    update(EndpointTopic).\
                    values({
                        'last_pub_time': now,
                        'pub_msg_id': pub_msg_id,
                        'pub_correl_id': pub_correl_id,
                        'in_reply_to': in_reply_to,
                        'pattern_matched': pattern_matched,
                        'ext_client_id': ext_client_id,
                        }).\
                    where(EndpointTopic.c.topic_id==topic_id).\
                    where(EndpointTopic.c.endpoint_id==endpoint_id).\
                    where(EndpointTopic.c.cluster_id==cluster_id)
                )

            # Update metatadata for endpoint
            session.execute(
                update(Endpoint).\
                values({
                    'last_seen': now,
                    'last_pub_time': now,
                    }).\
                where(Endpoint.c.id==endpoint_id).\
                where(Endpoint.c.cluster_id==cluster_id)
            )

            session.commit()

# ################################################################################################################################
