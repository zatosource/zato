# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Core publish/subscribe features

# stdlib
from datetime import datetime, timedelta
from json import dumps, loads
from logging import getLogger
from sys import maxint
from traceback import format_exc
from uuid import uuid4
import logging

# Bunch
from bunch import Bunch

# gevent
from gevent.lock import RLock

# Zato
from zato.common import PUB_SUB, ZATO_NONE
from zato.common.pubsub.lua import lua_move_to_target_queues, lua_get_from_cons_queue, lua_publish, lua_reject, lua_ack, \
     lua_delete_expired
from zato.common.util import datetime_to_seconds, make_repr, new_cid

# ################################################################################################################################

class Topic(object):
    def __init__(self, name, is_active=True, is_fifo=True, max_depth=500):
        self.name = name
        self.is_active = is_active
        self.is_fifo = is_fifo
        self.max_depth = 500

# ################################################################################################################################

class Message(object):
    """ A published or received message.
    """
    def __init__(self, payload='', topic=None, mime_type=PUB_SUB.DEFAULT_MIME_TYPE, priority=PUB_SUB.DEFAULT_PRIORITY, \
                     expiration=PUB_SUB.DEFAULT_EXPIRATION, msg_id=None, **kwargs):
        self.payload = payload
        self.topic = topic
        self.mime_type = mime_type
        self.priority = priority # In 1-9 range where 9 is top priority

        self.msg_id = msg_id or new_cid()

        self.expiration = expiration
        self.creation_time_utc = datetime.utcnow()
        self.expire_at_utc = self.creation_time_utc + timedelta(seconds=self.expiration)

    def __repr__(self):
        return make_repr(self)

    def to_dict(self):
        return {
            'payload': self.payload,
            'topic': self.topic,
            'mime_type': self.mime_type,
            'priority': self.priority,
            'msg_id': self.msg_id,
            'creation_time_utc': self.creation_time_utc.isoformat(),
            'expire_at_utc': self.expire_at_utc.isoformat(),
            'expiration': self.expiration
        }

    def to_json(self):
        return dumps(self.to_dict())

# ################################################################################################################################

class PubCtx(object):
    """ A set of data describing what to publish.
    """
    def __init__(self, client_id=None, topic=None, msg=None):
        self.client_id = client_id
        self.topic = topic
        self.msg = msg

# ################################################################################################################################

class SubCtx(object):
    """ Subscription context - what to subscribe to.
    """
    def __init__(self, client_id=None, topics=None):
        self.client_id = None
        self.topics = topics or []

# ################################################################################################################################

class GetCtx(object):
    """ A set of data describing where to fetch messages from.
    """
    def __init__(self, sub_key=None, max_batch_size=PUB_SUB.DEFAULT_GET_MAX_BATCH_SIZE, is_fifo=PUB_SUB.DEFAULT_IS_FIFO):
        self.sub_key = sub_key
        self.max_batch_size = max_batch_size
        self.is_fifo = is_fifo # Fetch in FIFO or LIFO order

# ################################################################################################################################

class AckCtx(object):
    """ A set of data describing an acknowledge of a message fetched.
    """
    def __init__(self, sub_key=None, msg_ids=None):
        self.sub_key = sub_key
        self.msg_ids = msg_ids or []

    def append(self, msg_id):
        self.msg_ids.append(msg_id)

# ################################################################################################################################

class RejectCtx(object):
    """ A set of data describing a rejection of one or more messages.
    """
    def __init__(self, sub_key=None, msg_ids=None):
        self.sub_key = sub_key
        self.msg_ids = msg_ids or []

    def append(self, msg_id):
        self.msg_ids.append(msg_id)

# ################################################################################################################################

class PubSub(object):
    """ An entry point to the pub/sub mechanism. Must be partly subclassed by concrete implementation classes.
    """

    def __init__(self, *ignored_args, **ignored_kwargs):
        self.logger = getLogger(self.__class__.__name__)

        # Held when modifying sets of currently known consumers and producers
        self.update_lock = RLock()

        # Held when in-flight messages are manipulated
        self.in_flight_lock = RLock()

        # All existing topics, key = topic name, value = topic object
        self.topics = {}

        self.sub_to_cons = {}   # String to string, key = sub_id, value = client_id using it
        self.cons_to_sub = {}   # String to string, key = client_id, value = sub_id it has

        # Consumers and topics
        self.cons_to_topic = {} # String to set, key = client_id, value = topics it's subscribed to
        self.topic_to_cons = {} # String to set, key = topic, value = clients subscribed to it

        # Producers and topics
        self.prod_to_topic = {} # String to set, key = client_id, value = topics it can publish to
        self.topic_to_prod = {} # String to set, key = topic, value = clients allowed to publish to it

        # Used by internal services
        self.default_consumer_id = None
        self.default_publisher_id = None

    def add_topic(self, topic):
        with self.update_lock:
            self.topics[topic.name] = topic

    update_topic = add_topic

    def add_subscription(self, sub_key, client_id, topic):
        """ Adds subscription for a given sub_id, client and topic. Must be called with self.update_lock held.
        """
        # Mapping between sub key and client and the other way around.
        self.sub_to_cons[sub_key] = client_id
        self.cons_to_sub[client_id] = sub_key

        # This consumers's topics
        topics = self.cons_to_topic.setdefault(client_id, set())
        topics.add(topic)

        # This topic's consumers
        clients = self.topic_to_cons.setdefault(topic, set())
        clients.add(client_id)

        self.logger.debug('Added subscription: `%s`, `%s`, `%s`', sub_key, client_id, topic)

    def add_producer(self, client_id, topic):
        """ Adds information that this client can publish to the topic. 
        """
        with self.update_lock:
            topics = self.prod_to_topic.setdefault(client_id, set())
            topics.add(topic.name)

            producers = self.topic_to_prod.setdefault(topic.name, set())
            producers.add(client_id)

    def _not_implemented(self, *ignored_args, **ignored_kwargs):
        raise NotImplementedError('Must be overridden in subclasses')

    publish = subscribe = get = acknowledge = reject = create = _not_implemented

# ################################################################################################################################

class RedisPubSub(PubSub):
    """ Publish/subscribe based on Redis.
    """
    LUA_PUBLISH = 'lua-publish'
    LUA_GET_FROM_CONSUMER_QUEUE = 'lua-get-from-consumer-queue'
    LUA_REJECT = 'lua-reject'
    LUA_ACK = 'lua-ack'

    # Background tasks
    LUA_DELETE_EXPIRED = 'lua-delete-expired'
    LUA_MOVE_TO_TARGET_QUEUES = 'lua-move-to-target-queues'

    # ############################################################################################################################

    def __init__(self, kvdb, key_prefix='zato:pubsub:'):
        super(RedisPubSub, self).__init__()
        self.kvdb = kvdb
        self.lua_programs = {}

        self.MSG_IDS_PREFIX = '{}{}'.format(key_prefix, 'zset:msg-ids:{}')
        self.BACKLOG_FULL_KEY = '{}{}'.format(key_prefix, 'backlog-full')
        self.CONSUMER_MSG_IDS_PREFIX = '{}{}'.format(key_prefix, 'list:consumer:msg-ids:{}')
        self.CONSUMER_IN_FLIGHT_IDS_PREFIX = '{}{}'.format(key_prefix, 'set:consumer:in-flight:ids:{}')
        self.CONSUMER_IN_FLIGHT_DATA_PREFIX = '{}{}'.format(key_prefix, 'hash:consumer:in-flight:data:{}')
        self.MSG_VALUES_KEY = '{}{}'.format(key_prefix, 'hash:msg-values')
        self.MSG_EXPIRE_AT_KEY = '{}{}'.format(key_prefix, 'hash:msg-expire-at') # In UTC
        self.UNACK_COUNTER_KEY = '{}{}'.format(key_prefix, 'hash:unack-counter')
        self.LAST_PUB_TIME_KEY = '{}{}'.format(key_prefix, 'hash:last-pub-time') # In UTC

        self.add_lua_program(self.LUA_PUBLISH, lua_publish)
        self.add_lua_program(self.LUA_MOVE_TO_TARGET_QUEUES, lua_move_to_target_queues)
        self.add_lua_program(self.LUA_GET_FROM_CONSUMER_QUEUE, lua_get_from_cons_queue)
        self.add_lua_program(self.LUA_REJECT, lua_reject)
        self.add_lua_program(self.LUA_ACK, lua_ack)
        self.add_lua_program(self.LUA_DELETE_EXPIRED, lua_delete_expired)

    # ############################################################################################################################

    def ping(self):
        """ Pings the pub/sub backend.
        """
        self.kvdb.ping()

    # ############################################################################################################################

    def validate_sub_key(self, sub_key):
        """ Returns a client_id by its matching subscription key or raises ValueError if sub_key could not be found.
        Must be called with self.update_lock held.
        """
        # Grab the client's ID, if it's a valid subscription key.
        if not self.sub_to_cons.get(sub_key):
            msg = 'Invalid sub_key `{}`'.format(sub_key)
            self.logger.warn(msg)
            raise ValueError(msg)

        return True

    # ############################################################################################################################

    def add_lua_program(self, name, program):
        self.lua_programs[name] = self.kvdb.register_script(program)

    def run_lua(self, name, keys=[], args=[]):
        return self.lua_programs[name](keys, args)

    # ############################################################################################################################

    def create(self, ctx):
        """ Creates a new topic to publish messages to.
        """
        self.logger.info('Creating topic `%s`', ctx.topic)

    # ############################################################################################################################

    def _raise_cant_publish_error(self, ctx):
        raise ValueError("Permision denied. Can't publish to `{}`".format(ctx.topic))

    def publish(self, ctx):
        """ Publishes a message on a selected topic.
        """
        # Note that the client always receives the same response but logs contain details
        with self.update_lock:
            if not ctx.topic in self.topics:
                self.logger.warn('Permision denied. No such topic `%s`, publisher `%s`', ctx.topic, ctx.client_id)
                self._raise_cant_publish_error(ctx)

            if not ctx.client_id in self.topic_to_prod.get(ctx.topic, []):
                self.logger.warn('Permision denied. Producer `%s` cannot publish to `%s`', ctx.client_id, ctx.topic)
                self._raise_cant_publish_error(ctx)

            if not self.topics[ctx.topic].is_active:
                self.logger.warn('Topic `%s` is not active. Producer `%s`.', ctx.topic, ctx.client_id)
                self._raise_cant_publish_error(ctx)

        id_key = self.MSG_IDS_PREFIX.format(ctx.topic)

        # Each message will carry information what topic it's intended for
        ctx.msg.topic = ctx.topic

        # The score is built by prefixing the number of milliseconds since UNIX epoch with message's priority. Hence higher
        # priority messages will get higher score whereas messages of equal priority will be still scored according
        # to their time of being published. But in the latter case this is still approximate with a high rate of publications
        # so if guarantees regarding the order of messages are required the messages should be arranged
        # in sequences on client side.

        now_seconds = datetime_to_seconds(datetime.utcnow())
        score = '{}{}'.format(ctx.msg.priority, now_seconds)

        try:
            self.run_lua(
                self.LUA_PUBLISH, [id_key, self.MSG_VALUES_KEY, self.MSG_EXPIRE_AT_KEY, self.LAST_PUB_TIME_KEY],
                    [score, ctx.msg.msg_id, ctx.msg.expire_at_utc.isoformat(), ctx.msg.to_json(),
                       ctx.topic, datetime.utcnow().isoformat()])
        except Exception, e:
            self.logger.error('Pub error `%s`', format_exc(e))
            raise
        else:
            self.logger.debug('Published: `%s` to `%s, exp:`%s`', ctx.msg.msg_id, ctx.topic, ctx.msg.expire_at_utc.isoformat())
            return ctx.msg.msg_id

    # ############################################################################################################################

    def subscribe(self, ctx, sub_key=None):
        """ Subscribes the client to one or more topics, or topic patterns. Returns subscription key
        to use in subsequent calls to fetch messages by.
        """
        sub_key = sub_key or new_cid()
        with self.update_lock:
            for topic in ctx.topics:
                # TODO: Resolve topic here - it can be a pattern instead of a concrete name
                self.add_subscription(sub_key, ctx.client_id, topic)

        self.logger.debug('Client `%s` sub to topics `%s`', ctx.client_id, ', '.join(ctx.topics))
        return sub_key

    # ############################################################################################################################

    def get(self, ctx):
        self.logger.debug('Get by sub_key `%s`', ctx.sub_key)

        with self.in_flight_lock:
            with self.update_lock:

                # Ignoring the result, we just check if this sub_key is valid
                self.validate_sub_key(ctx.sub_key)

                # Now that the client is known to be a valid one we can get all their messages
                cons_queue = self.CONSUMER_MSG_IDS_PREFIX.format(ctx.sub_key)
                cons_in_flight_ids = self.CONSUMER_IN_FLIGHT_IDS_PREFIX.format(ctx.sub_key)
                cons_in_flight_data = self.CONSUMER_IN_FLIGHT_DATA_PREFIX.format(ctx.sub_key)

                messages = self.run_lua(
                    self.LUA_GET_FROM_CONSUMER_QUEUE,
                    [cons_queue, cons_in_flight_ids, cons_in_flight_data, self.MSG_VALUES_KEY],
                    [ctx.max_batch_size, datetime.utcnow().isoformat()])

                for msg in messages:
                    yield Message(**loads(msg))

    # ############################################################################################################################

    def acknowledge(self, ctx):
        """ Consumer confirms and accepts one or more message.
        """
        # Check comment in self.reject on why validating sub_key alone suffices.
        self.validate_sub_key(ctx.sub_key)

        cons_in_flight_ids = self.CONSUMER_IN_FLIGHT_IDS_PREFIX.format(ctx.sub_key)
        cons_in_flight_data = self.CONSUMER_IN_FLIGHT_DATA_PREFIX.format(ctx.sub_key)

        result = self.run_lua(
            self.LUA_ACK,
            keys=[cons_in_flight_ids, cons_in_flight_data, self.UNACK_COUNTER_KEY, self.MSG_VALUES_KEY, self.MSG_EXPIRE_AT_KEY],
            args=ctx.msg_ids) 

        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(
                'Acknowledge result `%s` for `%s` with `%s`', result, ctx.sub_key, ', '.join(ctx.msg_ids))

    def reject(self, ctx):
        """ Rejects a set of messages for a given consumer. The messages will be placed back onto consumer's queue
        and delivered again at a later time.
        """
        # We only validate that this subscription key is valid. Each consumer has its own
        # hashmap of on-flight messages so if they know the sub key, meaning they know the username/password,
        # if any, the worst they can do is to attempt to reject IDs that don't exist.
        # But as long as they don't know each other's subscription keys they can't reject each other's messages.
        self.validate_sub_key(ctx.sub_key)

        cons_queue = self.CONSUMER_MSG_IDS_PREFIX.format(ctx.sub_key)
        cons_in_flight_ids = self.CONSUMER_IN_FLIGHT_IDS_PREFIX.format(ctx.sub_key)
        cons_in_flight_data = self.CONSUMER_IN_FLIGHT_DATA_PREFIX.format(ctx.sub_key)

        result = self.run_lua(self.LUA_REJECT, keys=[cons_queue, cons_in_flight_ids, cons_in_flight_data], args=ctx.msg_ids) 

        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(
                'Reject result `%s` for `%s` with `%s`', result, ctx.sub_key, ', '.join(ctx.msg_ids))

    # ############################################################################################################################

    def delete_expired(self):
        """ Deletes expired messages. For each topic and its subscribers a Lua program is called to find expired
        messages and delete all traces of them.
        """

        for consumer in self.cons_to_topic:
            sub_key = self.cons_to_sub[consumer]
            consumer_msg_ids = self.CONSUMER_MSG_IDS_PREFIX.format(sub_key)
            consumer_in_flight_ids = self.CONSUMER_IN_FLIGHT_IDS_PREFIX.format(sub_key)

            keys = [consumer_msg_ids, consumer_in_flight_ids, self.MSG_VALUES_KEY, self.MSG_EXPIRE_AT_KEY, 
                    self.UNACK_COUNTER_KEY]
            expired = self.run_lua(self.LUA_DELETE_EXPIRED, keys=keys, args=[datetime.utcnow().isoformat()]) 

            self.logger.info('Delete expired `%r` for keys `%s`', expired, keys)

            return expired

# ############################################################################################################################

    def move_to_target_queues(self):
        """ Invoked periodically in order to fetch data sent to a topic and move it to each consumer's queue.
        """
        # TODO: We currently deliver messages to each consumer. However, we also need to support 
        # the delivery to only one consumer chosen randomly from each of the subscribed ones.

        with self.update_lock:
            for topic in self.topic_to_prod:

                source_queue = self.MSG_IDS_PREFIX.format(topic)
                topic_info = self.topics[topic]

                # Keys the Lua program will operate on
                keys = []
                keys.append(source_queue)
                keys.append(self.BACKLOG_FULL_KEY)
                keys.append(self.UNACK_COUNTER_KEY)

                # Lua program's args
                args = []
                args.append(int(topic_info.is_fifo)) # So it's easy to cast it to bool in Lua
                args.append(topic_info.max_depth)
                args.append(maxint)

                consumers = self.topic_to_cons.get(topic, [])
                if consumers:
                    for consumer in consumers:
                        sub_key = self.cons_to_sub[consumer]
                        self.logger.debug('Sub `%s` for topic `%s` to consumer `%s`', sub_key, topic, consumer)

                        keys.append(self.CONSUMER_MSG_IDS_PREFIX.format(sub_key))

                    if self.logger.isEnabledFor(logging.DEBUG):
                        self.logger.debug('keys `%s`', ', '.join(keys))

                    move_result = self.run_lua(self.LUA_MOVE_TO_TARGET_QUEUES, keys, args)
                    self.logger.debug('move_result `%s` `%s`', move_result, type(move_result))

# ################################################################################################################################

    def get_topic_depth(self, topic):
        """ Returns current depth of a topic. Doesn't held onto any locks so by the time the data is returned to the caller
        the depth may have already changed.
        """
        return self.kvdb.zcard(self.MSG_IDS_PREFIX.format(topic))

    def get_consumers_count(self, topic):
        """ Returns the number of consumers allowed to get messages from a given topic.
        """
        return len(self.topic_to_cons.get(topic, []))

    def get_producers_count(self, topic):
        """ Returns the number of producers allowed to publish messages to a topic.
        """
        return len(self.topic_to_prod.get(topic, []))

    def get_last_pub_time(self, topic):
        """ Returns timestamp of the last publication to a topic, if any.
        """
        return self.kvdb.hget(self.LAST_PUB_TIME_KEY, topic)

# ################################################################################################################################

class PubSubAPI(object):
    """ Provides an API for pub/sub users to publish or subscribe to messages through.
    """
    def __init__(self, impl):
        self.impl = impl

    def publish(self, client_id, payload, topic, mime_type=PUB_SUB.DEFAULT_MIME_TYPE, priority=PUB_SUB.DEFAULT_PRIORITY,
            expiration=PUB_SUB.DEFAULT_EXPIRATION, msg_id=None, expire_at=None):
        """ Publishes a message by a given to a given topic using a set of parameters provided.
        """
        pub_ctx = PubCtx()
        pub_ctx.client_id = client_id
        pub_ctx.topic = topic
        pub_ctx.msg = Message(payload, topic, mime_type, priority, expiration, msg_id)

        self.impl.publish(pub_ctx)

    def subscribe(self, client_id, topics, sub_key=None):
        """ Subscribes a client to one or more topic. Returns a subscription key assigned.
        """
        if isinstance(topics, basestring):
            topics = [topics]

        # Sanity check - at this point 'topics' must be something we can iterate over
        # instead of, say, an integer.
        iter(topics)

        sub_ctx = SubCtx()
        sub_ctx.client_id = client_id
        sub_ctx.topics = topics

        return self.impl.subscribe(sub_ctx, sub_key)

    def get(self, sub_key, max_batch_size=PUB_SUB.DEFAULT_GET_MAX_BATCH_SIZE, is_fifo=PUB_SUB.DEFAULT_IS_FIFO):
        """ Gets one or more message, if any are available, for the given subscription key.
        """
        return self.impl.get(GetCtx(sub_key, max_batch_size, is_fifo))

# ################################################################################################################################

    # Admin calls below

    def add_topic(self, topic):
        return self.impl.add_topic(topic)

    def update_topic(self, topic):
        return self.impl.update_topic(topic)

    # ############################################################################################################################

    def get_topic_depth(self, topic):
        return self.impl.get_topic_depth(topic)

    def get_consumers_count(self, topic):
        return self.impl.get_consumers_count(topic)

    def get_producers_count(self, topic):
        return self.impl.get_producers_count(topic)

    def get_last_pub_time(self, topic):
        return self.impl.get_last_pub_time(topic)

    # ############################################################################################################################

    def get_default_consumer_id(self):
        return self.impl.default_consumer_id

    def get_default_producer_id(self):
        return self.impl.default_producer_id

    def set_default_consumer_id(self, client_id):
        self.impl.default_consumer_id = client_id

    def set_default_publisher_id(self, client_id):
        self.impl.default_publisher_id = client_id

# ################################################################################################################################
