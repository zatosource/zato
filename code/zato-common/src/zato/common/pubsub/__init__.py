# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Core publish/subscribe features

# stdlib
from contextlib import closing
from datetime import datetime, timedelta
from json import dumps, loads
from logging import getLogger
from sys import maxint
from traceback import format_exc
import logging

# gevent
from gevent.lock import RLock

# Zato
from zato.common import PUB_SUB, ZATO_NONE, ZATO_NOT_GIVEN
from zato.common.kvdb import LuaContainer
from zato.common.pubsub import lua
from zato.common.odb.model import PubSubSubscription
from zato.common.util import datetime_to_seconds, make_repr, new_cid

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class HasAutoRepr(object):
    def __repr__(self):
        return make_repr(self)

# ################################################################################################################################

class PubSubException(Exception):
    """ A base class for pub/sub exception.
    """

class PermissionDenied(PubSubException):
    """ Raised when an attempt is made to make use of a topic a client is not allowed to access.
    """

class ItemFull(Exception):
    """ Raised when either a topic or a consumer's queue is full.
    """
    def __init__(self, msg, item, max_depth):
        self.msg = msg
        self.item = item
        self.max_depth = max_depth

# ################################################################################################################################

class Topic(HasAutoRepr):
    def __init__(self, name, is_active=True, is_fifo=PUB_SUB.DEFAULT_IS_FIFO, max_depth=PUB_SUB.DEFAULT_MAX_DEPTH):
        self.name = name
        self.is_active = is_active
        self.is_fifo = is_fifo
        self.max_depth = max_depth

# ################################################################################################################################

class Message(object):
    """ A published or received message.
    """
    def __init__(self, payload='', topic=None, mime_type=PUB_SUB.DEFAULT_MIME_TYPE, priority=PUB_SUB.DEFAULT_PRIORITY,
             expiration=PUB_SUB.DEFAULT_EXPIRATION, msg_id=None, producer=None, creation_time_utc=None,
             expire_at_utc=None):
        self.payload = payload
        self.topic = topic
        self.mime_type = mime_type
        self.priority = priority # In 1-9 range where 9 is top priority
        self.msg_id = msg_id or new_cid()
        self.producer = producer
        self.expiration = expiration
        self.creation_time_utc = creation_time_utc or datetime.utcnow()
        self.expire_at_utc = expire_at_utc or (self.creation_time_utc + timedelta(seconds=self.expiration))

        # These two, in local timezone, are used by web-admin.
        self.creation_time = None
        self.expire_at = None

        self.id = None # Used by frontend only
        self.payload_html = None # Used by frontend only

    def __repr__(self):
        return make_repr(self)

    def to_dict(self):
        if isinstance(self.creation_time_utc, basestring):
            creation_time_utc = self.creation_time_utc
        else:
            creation_time_utc = self.creation_time_utc.isoformat()

        if isinstance(self.expire_at_utc, basestring):
            expire_at_utc = self.expire_at_utc
        else:
            expire_at_utc = self.expire_at_utc.isoformat()

        return {
            'topic': self.topic,
            'mime_type': self.mime_type,
            'priority': self.priority,
            'msg_id': self.msg_id,
            'creation_time_utc': creation_time_utc,
            'expire_at_utc': expire_at_utc,
            'expiration': self.expiration,
            'producer': self.producer
        }

    def to_json(self):
        return dumps(self.to_dict())

# ################################################################################################################################

class PubCtx(HasAutoRepr):
    """ A set of data describing what to publish.
    """
    def __init__(self, client_id=None, topic=None, msg=None):
        self.client_id = client_id
        self.topic = topic
        self.msg = msg

# ################################################################################################################################

class SubCtx(HasAutoRepr):
    """ Subscription context - what to subscribe to.
    """
    def __init__(self, client_id=None, topics=None):
        self.client_id = client_id
        self.topics = topics or []

# ################################################################################################################################

class GetCtx(HasAutoRepr):
    """ A set of data describing where to fetch messages from.
    """
    def __init__(self, sub_key=None, max_batch_size=PUB_SUB.DEFAULT_GET_MAX_BATCH_SIZE, is_fifo=PUB_SUB.DEFAULT_IS_FIFO,
                   get_format=PUB_SUB.GET_FORMAT.OBJECT.id):
        self.sub_key = sub_key
        self.max_batch_size = max_batch_size
        self.is_fifo = is_fifo # Fetch in FIFO or LIFO order
        self.get_format = get_format

# ################################################################################################################################

class AckCtx(HasAutoRepr):
    """ A set of data describing an acknowledge_delete of a message fetched.
    """
    def __init__(self, sub_key=None, msg_ids=None):
        self.sub_key = sub_key
        self.msg_ids = msg_ids or []

    def append(self, msg_id):
        self.msg_ids.append(msg_id)

    def __repr__(self):
        return make_repr(self)

# ################################################################################################################################

class RejectCtx(HasAutoRepr):
    """ A set of data describing a rejection of one or more messages.
    """
    def __init__(self, sub_key=None, msg_ids=None):
        self.sub_key = sub_key
        self.msg_ids = msg_ids or []

    def append(self, msg_id):
        self.msg_ids.append(msg_id)

# ################################################################################################################################

class Client(HasAutoRepr):
    """ Either a subscriber or publisher.
    """
    def __init__(self, id, name, is_active=True):
        self.id = id
        self.name = name
        self.is_active = is_active

class Consumer(Client):
    """ Pub/sub consumer.
    """
    def __init__(self, id, name, is_active=True, sub_key=None, max_depth=PUB_SUB.DEFAULT_MAX_BACKLOG,
            delivery_mode=PUB_SUB.DELIVERY_MODE.PULL.id, callback_id='', callback_name=None, callback_type=ZATO_NOT_GIVEN):
        super(Consumer, self).__init__(id, name, is_active)
        self.sub_key = sub_key
        self.max_depth = max_depth
        self.delivery_mode = delivery_mode
        self.callback_id = callback_id
        self.callback_name = callback_name
        self.callback_type = callback_type

# ################################################################################################################################

class PubSub(object):
    """ An entry point to the pub/sub mechanism. Must be partly subclassed by concrete implementation classes.
    """
    def __init__(self, *ignored_args, **ignored_kwargs):
        self.logger = getLogger('zato_pubsub')

        # Held when modifying sets of currently known consumers and producers
        self.update_lock = RLock()

        # Held when in-flight messages are manipulated
        self.in_flight_lock = RLock()

        # All existing topics, key = topic name, value = topic object
        self.topics = {}

        # All existing consumers, key = client_id, value = client object
        self.consumers = {}

        # All existing producers, key = client_id, value = client object
        self.producers = {}

        self.sub_to_cons = {}   # String to string, key = sub_id, value = client_id using it
        self.cons_to_sub = {}   # String to string, key = client_id, value = sub_id it has

        # Consumers and topics
        self.cons_to_topic = {} # String to set, key = client_id, value = topics it's subscribed to
        self.topic_to_cons = {} # String to set, key = topic, value = client_ids subscribed to it

        # Producers and topics
        self.prod_to_topic = {} # String to set, key = client_id, value = topics it can publish to
        self.topic_to_prod = {} # String to set, key = topic, value = client_ids allowed to publish to it

        # Used by internal services
        self.default_consumer = Client(None, None)
        self.default_producer = Client(None, None)

# ################################################################################################################################

    def add_topic(self, topic):
        """ Adds a topic, with no clients attached.
        """
        with self.update_lock:
            self.topics[topic.name] = topic
            self.logger.info('Added topic `%s`', topic)

    update_topic = add_topic

# ################################################################################################################################

    def delete_topic(self, topic):
        """ Deletes a topic and any consumers or producers assigned to it.
        """
        with self.update_lock:
            deleted = self.topics[topic.name]

            consumers = self.topic_to_cons.get(topic.name, [])
            producers = self.topic_to_prod.get(topic.name, [])

            for consumer_id in list(consumers):
                self.delete_consumer(self.consumers[consumer_id], topic)

            for producer_id in list(producers):
                self.delete_producer(self.producers[producer_id], topic)

            # Implemented by subclasses
            self.delete_topic_metadata(topic)

            self.logger.info('Deleted topic `%s`', deleted)

# ################################################################################################################################

    def delete_topic_metadata(self, topic):
        """ Deletes topic's metadata. Needs to be subclasses by concrete implementations.
        """
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def add_subscription(self, sub_key, client_id, topic):
        """ Adds subscription for a given sub_id, client and topic. Must be called with self.update_lock held.
        """
        # Mapping between sub key and client and the other way around.
        self.sub_to_cons[sub_key] = client_id
        self.cons_to_sub[client_id] = sub_key

        # This consumer's topics
        topics = self.cons_to_topic.setdefault(client_id, set())
        topics.add(topic)

        # This topic's consumers
        clients = self.topic_to_cons.setdefault(topic, set())
        clients.add(client_id)

        self.logger.info('Added subscription: `%s`, `%s`, `%s`', sub_key, client_id, topic)

# ################################################################################################################################

    def add_producer(self, client, topic):
        """ Adds information that this client can publish to the topic.
        """
        with self.update_lock:

            # Topics for this producer
            topics = self.prod_to_topic.setdefault(client.id, set())
            topics.add(topic.name)

            # Producers for this topic
            producers = self.topic_to_prod.setdefault(topic.name, set())
            producers.add(client.id)

            self.producers[client.id] = client

            self.logger.info('Added producer `%s` for topic:`%s`', client, topic)

    def update_producer(self, client, topic):
        """ Updates a producer.
        """
        # Currently we can only switch is_active flag on/off
        with self.update_lock:
            self.producers[client.id].is_active = client.is_active
            self.logger.info('Updated producer `%s` for topic:`%s`', client, topic)

    def delete_producer(self, client, topic):
        """ Deletes an association between a producer and a topic.
        """
        with self.update_lock:

            # Topics for this producer
            topics = self.prod_to_topic.pop(client.id, set())
            topics.remove(topic.name)

            # Producers for this topic
            producers = self.topic_to_prod.get(topic.name, set())
            producers.remove(client.id)

            # That was the last producer for this topic so let's delete the topic from this dict
            # so other parts of the code can assume that if a topic doesn't exist in it, it means there is no producer
            # for the given topic name.
            if not self.topic_to_prod[topic.name]:
                del self.topic_to_prod[topic.name]

            del self.producers[client.id]
            self.delete_producer_metadata(client)

            self.logger.info('Deleted producer `%s` for topic:`%s`', client, topic)

    def delete_producer_metadata(self, client):
        """ Deletes producer's metadata. Needs to be subclasses by concrete implementations.
        """
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def add_consumer(self, client, topic):
        """ Adds information that this client can publish to the topic.
        """
        with self.update_lock:
            topics = self.cons_to_topic.setdefault(client.id, set())
            topics.add(topic.name)

            consumers = self.topic_to_cons.setdefault(topic.name, set())
            consumers.add(client.id)

            self.consumers[client.id] = client

            self.sub_to_cons[client.sub_key] = client.id
            self.cons_to_sub[client.id] = client.sub_key

            self.logger.info('Added consumer `%s` for topic:`%s`', client, topic)

    def update_consumer(self, client, topic):
        """ Updates a consumer.
        """
        with self.update_lock:
            self.consumers[client.id].is_active = client.is_active
            self.consumers[client.id].max_depth = client.max_depth
            self.consumers[client.id].delivery_mode = client.delivery_mode
            self.consumers[client.id].callback_id = client.callback_id

            self.logger.info('Updated consumer `%s` for topic:`%s`', client, topic)

    def delete_consumer(self, client, topic):
        """ Deletes an association between a consumer and a topic.
        """
        with self.update_lock:
            topics = self.cons_to_topic.pop(client.id, set())
            topics.remove(topic.name)

            consumers = self.topic_to_cons.get(topic.name, set())
            consumers.remove(client.id)

            # That was the last consumer for this topic so let's delete the topic from this dict
            # so other parts of the code can assume that if a topic doesn't exist in it, it means there is no consumer
            # for the given topic name.
            if not self.topic_to_cons[topic.name]:
                del self.topic_to_cons[topic.name]

            del self.consumers[client.id]
            del self.sub_to_cons[client.sub_key]
            del self.cons_to_sub[client.id]

            self.delete_consumer_metadata(client)

            self.logger.info('Deleted consumer `%s` for topic:`%s`', client, topic)

    def delete_consumer_metadata(self, client):
        """ Deletes consumer's metadata. Needs to be subclasses by concrete implementations.
        """
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def _not_implemented(self, *ignored_args, **ignored_kwargs):
        raise NotImplementedError('Must be overridden in subclasses')

    publish = subscribe = get = acknowledge_delete = reject = create = _not_implemented

# ################################################################################################################################

class SQLPubSub(PubSub):
    def __init__(self, conn, invoke_outconn_http):
        self.conn = conn
        self.invoke_outconn_http = invoke_outconn_http

    def publish(self, ctx):
        logger.warn('zzz %s', ctx)

        with closing(self.conn.session()) as session:
            logger.warn('aaa %s', session)

# ################################################################################################################################

class PubSubAPI(object):
    """ Provides an API for pub/sub users to publish or subscribe to messages through.
    """
    def __init__(self, impl):
        self.impl = impl

    def publish(self, payload, topic, mime_type=None, priority=None, expiration=None, msg_id=None, expire_at=None,
        client_id=None):
        """ Publishes a message to a given topic using a set of parameters provided.
        """
        client_id = client_id or self.get_default_producer().id
        ctx = PubCtx()
        ctx.client_id = client_id
        ctx.topic = topic
        ctx.msg = Message(
            payload, topic, mime_type or PUB_SUB.DEFAULT_MIME_TYPE, priority or PUB_SUB.DEFAULT_PRIORITY,
            expiration or PUB_SUB.DEFAULT_EXPIRATION, msg_id, 'dummy-producer')#self.impl.producers[client_id].name)

        return self.impl.publish(ctx)

    def subscribe(self, client_id, topics, sub_key=None):
        """ Subscribes a client to one or more topic. Returns a subscription key assigned.
        """
        if isinstance(topics, basestring):
            topics = [topics]

        # Sanity check - at this point 'topics' must be something we can iterate over
        # instead of, say, an integer.
        iter(topics)

        ctx = SubCtx()
        ctx.client_id = client_id
        ctx.topics = topics

        return self.impl.subscribe(ctx, sub_key)

    def get(self, sub_key, max_batch_size=PUB_SUB.DEFAULT_GET_MAX_BATCH_SIZE, is_fifo=PUB_SUB.DEFAULT_IS_FIFO,
            get_format=PUB_SUB.GET_FORMAT.DEFAULT.id):
        """ Gets one or more message, if any are available, for the given subscription key.
        """
        return self.impl.get(GetCtx(sub_key, max_batch_size, is_fifo, get_format))

    def acknowledge(self, sub_key, msg_ids):
        """ Acknowledges one or more message IDs for a given subscription key.
        """
        ctx = AckCtx()
        ctx.sub_key = sub_key
        ctx.msg_ids = [msg_ids] if not isinstance(msg_ids, (list, tuple, set, dict)) else msg_ids

        return self.impl.acknowledge_delete(ctx)

    def reject(self, sub_key, msg_ids):
        """ Rejects one or more message IDs for a given subscription key.
        """
        ctx = RejectCtx()
        ctx.sub_key = sub_key
        ctx.msg_ids = [msg_ids] if not isinstance(msg_ids, (list, tuple, set, dict)) else msg_ids

        return self.impl.reject(ctx)

# ################################################################################################################################

    # Admin calls below

    def add_topic(self, topic):
        return self.impl.add_topic(topic)

    def update_topic(self, topic):
        return self.impl.update_topic(topic)

    def delete_topic(self, topic):
        return self.impl.delete_topic(topic)

    def delete_consumer(self, consumer, topic):
        return self.impl.delete_consumer(consumer, topic)

    def add_producer(self, producer, topic):
        return self.impl.add_producer(producer, topic)

    def update_producer(self, producer, topic):
        return self.impl.update_producer(producer, topic)

    def delete_producer(self, producer, topic):
        return self.impl.delete_producer(producer, topic)

    def add_consumer(self, consumer, topic):
        return self.impl.add_consumer(consumer, topic)

    def update_consumer(self, consumer, topic):
        return self.impl.update_consumer(consumer, topic)

# ############################################################################################################################

    def get_topic_depth(self, topic):
        return self.impl.get_topic_depth(topic)

    def get_consumer_queue_current_depth(self, sub_key):
        return self.impl.get_consumer_queue_current_depth(sub_key)

    def get_consumer_queue_in_flight_depth(self, sub_key):
        return self.impl.get_consumer_queue_in_flight_depth(sub_key)

    def get_consumer_by_sub_key(self, sub_key):
        return self.impl.get_consumer_by_sub_key(sub_key)

    def get_consumer_by_client_id(self, client_id):
        return self.impl.get_consumer_by_client_id(client_id)

    def get_consumers_count(self, topic):
        return self.impl.get_consumers_count(topic)

    def get_producers_count(self, topic):
        return self.impl.get_producers_count(topic)

    def get_last_pub_time(self, topic):
        return self.impl.get_last_pub_time(topic)

    def get_producer_last_seen(self, client_id):
        return self.impl.get_producer_last_seen(client_id)

    def get_consumer_last_seen(self, client_id):
        return self.impl.get_consumer_last_seen(client_id)

    def get_producer_by_sub_key(self, sub_key):
        return self.producers.get(self.sub_to_cons.get(sub_key, ZATO_NONE))

# ################################################################################################################################

    def get_default_consumer(self):
        return self.impl.default_consumer

    def get_default_producer(self):
        return self.impl.default_producer

    def set_default_consumer(self, client):
        self.impl.default_consumer = client

    def set_default_producer(self, client):
        self.impl.default_producer = client

# ################################################################################################################################

    def get_consumer_queue_message_list(self, sub_key):
        return self.impl.get_consumer_queue_message_list(sub_key)

    def get_consumer_in_flight_message_list(self, sub_key):
        return self.impl.get_consumer_in_flight_message_list(sub_key)

    def get_topic_message_list(self, source_name):
        return self.impl.get_topic_message_list(source_name)

# ################################################################################################################################

    def delete_from_topic(self, topic_name, msg_id, *ignored):
        return self.impl.delete_from_topic(topic_name, msg_id)

    def delete_from_consumer_queue(self, sub_key, msg_ids):
        if isinstance(msg_ids, basestring):
            msg_ids = [msg_ids]
        return self.impl.delete_from_consumer_queue(sub_key, msg_ids if isinstance(msg_ids, list) else list(msg_ids))

# ################################################################################################################################

    def get_message(self, msg_id):
        return self.impl.get_message(msg_id)

# ################################################################################################################################

    def can_access_topic(self, client_id, topic, is_consumer):
        return topic in self.impl.cons_to_topic.get(client_id, []) if is_consumer else self.impl.prod_to_topic.get(client_id, [])

# ################################################################################################################################
