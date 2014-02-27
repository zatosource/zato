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
from zato.common.pubsub import lua
     
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
                     expiration=PUB_SUB.DEFAULT_EXPIRATION, msg_id=None, producer=None, creation_time_utc=None,
                     expire_at_utc=None, **kwargs):
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

    def __repr__(self):
        return make_repr(self)

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

class Client(object):
    """ Either a subscriber or publisher.
    """
    def __init__(self, id, name, is_active=True):
        self.id = id
        self.name = name
        self.is_active = is_active

class Consumer(Client):
    """ Pub/sub consumer.
    """
    def __init__(self, id, name, is_active=True, sub_key=None, max_backlog=PUB_SUB.DEFAULT_MAX_BACKLOG):
        super(Consumer, self).__init__(id, name, is_active)
        self.sub_key = sub_key
        self.max_backlog = max_backlog

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
        self.topic_to_cons = {} # String to set, key = topic, value = clients subscribed to it

        # Producers and topics
        self.prod_to_topic = {} # String to set, key = client_id, value = topics it can publish to
        self.topic_to_prod = {} # String to set, key = topic, value = clients allowed to publish to it

        # Used by internal services
        self.default_consumer = Client(None, None)
        self.default_producer = Client(None, None)

    # ############################################################################################################################

    def add_topic(self, topic):
        with self.update_lock:
            self.topics[topic.name] = topic

    update_topic = add_topic

    # ############################################################################################################################

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

        self.logger.info('Added subscription: `%s`, `%s`, `%s`', sub_key, client_id, topic)

    # ############################################################################################################################

    def add_producer(self, client, topic):
        """ Adds information that this client can publish to the topic. 
        """
        with self.update_lock:
            topics = self.prod_to_topic.setdefault(client.id, set())
            topics.add(topic.name)

            producers = self.topic_to_prod.setdefault(topic.name, set())
            producers.add(client.id)

            self.producers[client.id] = client

    def update_producer(self, client, topic):
        """ Updates a producer.
        """
        # Currently we can only switch is_active flag on/off
        with self.update_lock:
            self.producers[client.id].is_active = client.is_active

    def delete_producer(self, client, topic):
        """ Deletes an association between a producer and a topic.
        """
        with self.update_lock:
            topics = self.prod_to_topic.setdefault(client.id, set())
            topics.remove(topic.name)

            producers = self.topic_to_prod.setdefault(topic.name, set())
            producers.remove(client.id)

            del self.producers[client.id]

    # ############################################################################################################################

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

    def update_consumer(self, client, topic):
        """ Updates a consumer.
        """
        with self.update_lock:
            self.consumers[client.id].is_active = client.is_active
            self.consumers[client.id].max_backlog = client.max_backlog

    def delete_consumer(self, client, topic):
        """ Deletes an association between a consumer and a topic.
        """
        with self.update_lock:
            topics = self.cons_to_topic.setdefault(client.id, set())
            topics.remove(topic.name)

            consumers = self.topic_to_cons.setdefault(topic.name, set())
            consumers.remove(client.id)

            del self.consumers[client.id]
            del self.sub_to_cons[client.sub_key]
            del self.cons_to_sub[client.id]

    # ############################################################################################################################

    def _not_implemented(self, *ignored_args, **ignored_kwargs):
        raise NotImplementedError('Must be overridden in subclasses')

    publish = subscribe = get = acknowledge = reject = create = _not_implemented

# ################################################################################################################################

class RedisPubSub(PubSub):
    """ Publish/subscribe based on Redis.
    """
    # Main public API
    LUA_PUBLISH = 'lua-publish'
    LUA_GET_FROM_CONSUMER_QUEUE = 'lua-get-from-consumer-queue'
    LUA_REJECT = 'lua-reject'
    LUA_ACK_DELETE = 'lua-ack-delete'

    # Background tasks
    LUA_DELETE_EXPIRED = 'lua-delete-expired'
    LUA_MOVE_TO_TARGET_QUEUES = 'lua-move-to-target-queues'

    # Message browsing
    LUA_GET_CONSUMER_QUEUE_MESSAGE_LIST = 'lua-get-consumer-queue-message-list'
    LUA_GET_MESSAGE_LIST = 'lua-get-message-list'

    # Message deleting
    LUA_DELETE_FROM_TOPIC = 'lua-delete-from-topic'
    LUA_DELETE_FROM_CONSUMER_QUEUE = 'lua-delete-from-consumer-queue'

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
        self.MSG_METADATA_KEY = '{}{}'.format(key_prefix, 'hash:msg-metadata')
        self.MSG_EXPIRE_AT_KEY = '{}{}'.format(key_prefix, 'hash:msg-expire-at') # In UTC
        self.UNACK_COUNTER_KEY = '{}{}'.format(key_prefix, 'hash:unack-counter')
        self.LAST_PUB_TIME_KEY = '{}{}'.format(key_prefix, 'hash:last-pub-time') # In UTC
        self.LAST_SEEN_CONSUMER_KEY = '{}{}'.format(key_prefix, 'hash:last-seen-consumer') # In UTC
        self.LAST_SEEN_PRODUCER_KEY = '{}{}'.format(key_prefix, 'hash:last-seen-producer') # In UTC

        self.add_lua_program(self.LUA_PUBLISH, lua.lua_publish)
        self.add_lua_program(self.LUA_MOVE_TO_TARGET_QUEUES, lua.lua_move_to_target_queues)
        self.add_lua_program(self.LUA_GET_FROM_CONSUMER_QUEUE, lua.lua_get_from_cons_queue)
        self.add_lua_program(self.LUA_REJECT, lua.lua_reject)
        self.add_lua_program(self.LUA_ACK_DELETE, lua.lua_ack_delete)
        self.add_lua_program(self.LUA_DELETE_EXPIRED, lua.lua_delete_expired)
        self.add_lua_program(self.LUA_GET_MESSAGE_LIST, lua.lua_get_message_list)
        self.add_lua_program(self.LUA_DELETE_FROM_TOPIC, lua.lua_delete_from_topic)
        self.add_lua_program(self.LUA_DELETE_FROM_CONSUMER_QUEUE, lua.lua_delete_from_consumer_queue)

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

            if not self.producers[ctx.client_id].is_active:
                self.logger.warn('Producer `%s` is not active. Producer `%s`.', ctx.client_id, ctx.topic)
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
                self.LUA_PUBLISH, [
                    id_key, self.MSG_VALUES_KEY, self.MSG_METADATA_KEY, self.MSG_EXPIRE_AT_KEY, self.LAST_PUB_TIME_KEY,
                      self.LAST_SEEN_PRODUCER_KEY],
                    [score, ctx.msg.msg_id, ctx.msg.expire_at_utc.isoformat(), ctx.msg.payload, ctx.msg.to_json(),
                       ctx.topic, datetime.utcnow().isoformat(), ctx.client_id])
        except Exception, e:
            self.logger.error('Pub error `%s`', format_exc(e))
            raise
        else:
            self.logger.info('Published: `%s` to `%s, exp:`%s`', ctx.msg.msg_id, ctx.topic, ctx.msg.expire_at_utc.isoformat())
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

        self.logger.info('Client `%s` sub to topics `%s`', ctx.client_id, ', '.join(ctx.topics))
        return sub_key

    # ############################################################################################################################

    def get(self, ctx):
        self.logger.info('Get by sub_key `%s`', ctx.sub_key)

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
                    [cons_queue, cons_in_flight_ids, cons_in_flight_data, self.MSG_METADATA_KEY, self.LAST_SEEN_CONSUMER_KEY],
                    [ctx.max_batch_size, datetime.utcnow().isoformat(), self.sub_to_cons[ctx.sub_key]])

                for msg in messages:
                    yield Message(**loads(msg))

    # ############################################################################################################################

    def acknowledge(self, ctx, is_delete=False):
        """ Consumer confirms and accepts one or more message.
        """
        # Check comment in self.reject on why validating sub_key alone suffices.
        self.validate_sub_key(ctx.sub_key)

        cons_in_flight_ids = self.CONSUMER_IN_FLIGHT_IDS_PREFIX.format(ctx.sub_key)
        cons_in_flight_data = self.CONSUMER_IN_FLIGHT_DATA_PREFIX.format(ctx.sub_key)
        cons_queue = self.CONSUMER_MSG_IDS_PREFIX.format(ctx.sub_key)

        result = self.run_lua(
            self.LUA_ACK_DELETE,
            keys=[cons_in_flight_ids, cons_in_flight_data, self.UNACK_COUNTER_KEY, self.MSG_VALUES_KEY, self.MSG_EXPIRE_AT_KEY,
                  cons_queue],
            args=[int(is_delete)] + ctx.msg_ids) 

        self.logger.info(
            'Ack: result `%s` for sub_key `%s` with msgs `%s`', result, ctx.sub_key, ', '.join(ctx.msg_ids))

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
            self.logger.info(
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
                        self.logger.debug('Move: Found sub `%s` for topic `%s` by consumer `%s`', sub_key, topic, consumer)

                        keys.append(self.CONSUMER_MSG_IDS_PREFIX.format(sub_key))

                    move_result = self.run_lua(self.LUA_MOVE_TO_TARGET_QUEUES, keys, args)
                    if move_result:
                        self.logger.info('Move: result `%s`, keys `%s`', move_result, ', '.join(keys))

# ################################################################################################################################

    def get_topic_depth(self, topic):
        """ Returns current depth of a topic. Doesn't held onto any locks so by the time the data is returned to the caller
        the depth may have already changed.
        """
        return self.kvdb.zcard(self.MSG_IDS_PREFIX.format(topic))

    def get_consumer_queue_current_depth(self, sub_key):
        """ Returns current depth of a consumer's queue. Doesn't held onto any locks so by the time the data
        is returned to the caller the depth may have already changed.
        """
        return self.kvdb.llen(self.CONSUMER_MSG_IDS_PREFIX.format(sub_key))

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

    def get_producer_last_seen(self, client_id):
        """ Returns timestamp of the last time a producer published a message, regardless of its topic.
        """
        return self.kvdb.hget(self.LAST_SEEN_PRODUCER_KEY, client_id)

    def get_consumer_last_seen(self, client_id):
        """ Returns timestamp of the last time a consumer got a message, regardless of its topic.
        """
        return self.kvdb.hget(self.LAST_SEEN_CONSUMER_KEY, client_id)

    # ############################################################################################################################

    def get_consumer_queue_message_list(self, sub_key):
        """ Returns all messages from a given consumer queue by its subscriber's key.
        """
        for item in self.run_lua(
            self.LUA_GET_MESSAGE_LIST, [
                self.CONSUMER_MSG_IDS_PREFIX.format(sub_key), self.MSG_METADATA_KEY], [PUB_SUB.MESSAGE_SOURCE.CONSUMER_QUEUE.id]):
            yield Message(**loads(item))

    def get_topic_message_list(self, source_name):
        """ Returns all messages from a given topic.
        """
        for item in self.run_lua(
            self.LUA_GET_MESSAGE_LIST, [
                self.MSG_IDS_PREFIX.format(source_name), self.MSG_METADATA_KEY], [PUB_SUB.MESSAGE_SOURCE.TOPIC.id]):
            yield Message(**loads(item))

    def delete_from_topic(self, source_name, msg_id):
        """ The message is deleted from a topic and if there are no subscriptions to a topic
        it's also removed from Redis keys holding the message's metadada and payload.
        """
        with self.update_lock:
            # Let's find subscriptions to this topic. If there aren't any subscriptions, we call a Lua function
            # that deletes not only the message from topic but also any other piece of information regarding it.
            has_consumers = True if source_name in self.topic_to_cons else False
            result = self.run_lua(
                self.LUA_DELETE_FROM_TOPIC,
                  [self.MSG_IDS_PREFIX.format(source_name), self.MSG_VALUES_KEY, self.MSG_METADATA_KEY, self.MSG_EXPIRE_AT_KEY],
                  [int(has_consumers), msg_id])

            self.logger.info(
                'Del topic: result `%s`, source_name `%s`, msg_id `%s`, has_consumers `%s`',
                  result, source_name, msg_id, has_consumers)

    def delete_from_consumer_queue(self, sub_key, msg_id):
        """ Deleting a message from a consumer's queue works exactly like acknowledging it.
        """
        return self.acknowledge(AckCtx(sub_key, [msg_id]), True)

    def get_message(self, msg_id):
        """ Returns payload of a message along with its metadata.
        """
        out = {'payload': self.kvdb.hget(self.MSG_VALUES_KEY, msg_id)}
        out.update(loads(self.kvdb.hget(self.MSG_METADATA_KEY, msg_id)))

        return out

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
        pub_ctx.msg = Message(
            payload, topic, mime_type, priority, expiration, msg_id, self.impl.producers[client_id].name)

        return self.impl.publish(pub_ctx)

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

    def delete_consumer(self, consumer, topic):
        return self.impl.delete_consumer(consumer, topic)

    # ############################################################################################################################

    def get_topic_depth(self, topic):
        return self.impl.get_topic_depth(topic)

    def get_consumer_queue_current_depth(self, sub_key):
        return self.impl.get_consumer_queue_current_depth(sub_key)

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

    # ############################################################################################################################

    def get_default_consumer(self):
        return self.impl.default_consumer

    def get_default_consumer(self):
        return self.impl.default_consumer

    def get_default_producer(self):
        return self.impl.default_producer

    def set_default_consumer(self, client):
        self.impl.default_consumer = client

    def set_default_producer(self, client):
        self.impl.default_producer = client

# ################################################################################################################################

    def get_consumer_queue_message_list(self, source_name):
        return self.impl.get_consumer_queue_message_list(source_name)

    def get_topic_message_list(self, source_name):
        return self.impl.get_topic_message_list(source_name)

    def delete_from_topic(self, source_name, msg_id):
        return self.impl.delete_from_topic(source_name, msg_id)

    def delete_from_consumer_queue(self, source_name, msg_id):
        return self.impl.delete_from_consumer_queue(source_name)

    def get_message(self, msg_id):
        return self.impl.get_message(msg_id)

# ################################################################################################################################
