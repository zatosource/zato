# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Core publish/subscribe features

# Monkey patch first
from gevent.monkey import patch_all
patch_all()

# stdlib
from datetime import datetime
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
from zato.common import ZATO_NONE
from zato.common.util import datetime_to_seconds, make_repr, new_cid

# ################################################################################################################################

class Topic(object):
    def __init__(self, name, is_fifo=True, max_depth=500):
        self.name = name
        self.is_fifo = is_fifo
        self.max_depth = 500

# ################################################################################################################################

class Message(object):
    """ A published or received message.
    """
    def __init__(self, payload='', msg_id=None, mime_type='text/plain', priority=5, expiration=60, expire_at=None, topic=None):
        self.payload = payload
        self.msg_id = msg_id or new_cid()
        self.mime_type = mime_type
        self.priority = priority # In 1-9 range where 9 is top priority
        self.topic = topic

        # expiration -> how many seconds a message should live
        # expire_at -> a datetime, in UTC, when it should expire
        # Either of these is required.

        self.expiration = expiration
        self.expire_at = expire_at

    def __repr__(self):
        return make_repr(self)

    def to_json(self):
        return dumps({
            'msg_id': self.msg_id,
            'payload': self.payload,
            'mime_type': self.mime_type,
            'priority': self.priority,
            'topic': self.topic
        })

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
    def __init__(self, client_id=None, topics=[]):
        self.client_id = None
        self.topics = topics

# ################################################################################################################################

class GetCtx(object):
    """ A set of data describing where to fetch messages from.
    """
    def __init__(self, sub_key=None, max_batch_size=100, is_fifo=True):
        self.sub_key = sub_key
        self.max_batch_size = max_batch_size
        self.is_fifo = is_fifo # Fetch in FIFO or LIFO order

# ################################################################################################################################

class AckCtx(object):
    """ A set of data describing an acknowledge of a message fetched.
    """
    def __init__(self, msg_id=None):
        self.msg_id = msg_id

# ################################################################################################################################

class RejectCtx(object):
    """ A set of data describing a rejection of one or more messages.
    """
    def __init__(self, sub_key=None, msg_ids=[]):
        self.sub_key = sub_key
        self.msg_ids = msg_ids

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

    def add_topic(self, topic):
        with self.update_lock:
            self.topics[topic.name] = topic

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

    def _not_implemented(self, *ignored_args, **ignored_kwargs):
        raise NotImplementedError('Must be overridden in subclasses')

    publish = subscribe = get = acknowledge = reject = create = _not_implemented

# ################################################################################################################################

class RedisPubSub(PubSub):
    """ Publish/subscribe based on Redis.
    """
    MSG_IDS_PREFIX = 'zato:pubsub:msg-ids:{}'
    BACKLOG_FULL_KEY = 'zato:pubsub:backlog-full'
    CONSUMER_MSG_IDS_PREFIX = 'zato:pubsub:consumer:msg-ids:{}'
    CONSUMER_IN_FLIGHT_PREFIX = 'zato:pubsub:consumer:in-flight:{}'
    MSG_VALUES_KEY = 'zato:pubsub:msg-values'

    LUA_MOVE_TO_TARGET_QUEUES = 'move-to-target-queues'
    LUA_GET_FROM_CONSUMER_QUEUE = 'get-from-consumer-queue'
    LUA_REJECT = 'reject'

    # ############################################################################################################################

    def __init__(self, kvdb):
        super(RedisPubSub, self).__init__()
        self.kvdb = kvdb
        self.lua_programs = {}

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

    def publish(self, ctx):
        """ Publishes a message on a selected topic. If topic is a pattern instead of an exact name
        all topics matching the pattern are published to provided security checks allow for it.
        """
        with self.update_lock:
            if not ctx.topic in self.topics:

                # Note that in the exception we don't make it know which client_id it was
                self.logger.warn('Producer `%s` cannot publish to `%s`', ctx.client_id, ctx.topic)
                raise ValueError("Can't publish to `{}`".format(ctx.topic))

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

        # Below, hset on ID_TO_TOPIC_KEY will have to be set for each topic resolved from a pattern, eventually,
        # when we have patterns on publish.

        with self.kvdb.pipeline() as p:

            p.zadd(id_key, score, ctx.msg.msg_id)
            p.hset(self.MSG_VALUES_KEY, ctx.msg.msg_id, ctx.msg.to_json())

            try:
                p.execute()
            except Exception, e:
                self.logger.error('Pub error `%s`', format_exc(e))
                raise
            else:
                self.logger.debug('Published: `%s` to `%s', ctx.msg.msg_id, ctx.topic)

    # ############################################################################################################################

    def subscribe(self, ctx):
        """ Subscribes the client to one or more topics, or topic patterns. Returns subscription key
        to use in subsequent calls to fetch messages by.
        """
        sub_key = new_cid()
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
                cons_in_flight = self.CONSUMER_IN_FLIGHT_PREFIX.format(ctx.sub_key)
    
                # TODO: Make it run using 'with self.lock(cons_queue)'
    
                messages = self.run_lua(
                    self.LUA_GET_FROM_CONSUMER_QUEUE,
                    [cons_queue, cons_in_flight, self.MSG_VALUES_KEY],
                    [ctx.max_batch_size, datetime.utcnow().isoformat()])

                for msg in messages:
                    yield Message(**loads(msg))

    # ############################################################################################################################

    def acknowledge(self, ctx):
        topic = self.kvdb.hget(self.ID_TO_TOPIC_KEY, ctx.msg_id)
        self.logger.info('Ack msg_id:`%s`, topic:`%s`', ctx.msg_id, topic)

        with self.kvdb.pipeline() as p:

            p.zrem(self.MSG_IDS_PREFIX.format(topic), ctx.msg_id)
            p.hdel(self.ID_TO_TOPIC_KEY, ctx.msg_id)
            p.delete(self.ID_EXP_PREFIX.format(topic, ctx.msg_id))

            p.execute()

    def reject(self, ctx):
        """ Rejects a set of messages for a given consumer.
        """
        # TODO: This should be called with this consumer's in-flight key used by self.lock
        # so it's an atomic operation. If the lock is already held an exception should be
        # raised and a Server Busy kind of message returned.

        # We only validate that this subscription key is valid. Each consumer has its own
        # hashmap of on-flight messages so if they know the sub key, meaning they know the username/password,
        # if any, the worst they can do is to attempt to reject IDs that don't exist.
        # But as long as they don't know each other's subscription keys they can't reject each other's messages.
        self.validate_sub_key(ctx.sub_key)

        cons_queue = self.CONSUMER_MSG_IDS_PREFIX.format(ctx.sub_key)
        cons_in_flight = self.CONSUMER_IN_FLIGHT_PREFIX.format(ctx.sub_key)

        result = self.run_lua(self.LUA_REJECT, keys=[cons_queue, cons_in_flight], args=ctx.msg_ids)

        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(
                'Reject result `%s` for `%s` with `%s`', result, ctx.sub_key, ', '.join(ctx.msg_ids))

    # ############################################################################################################################

    def move_to_target_queues(self):
        """ Invoked periodically in order to fetch data sent to a topic and move it to each consumer's queue.
        """
        # TODO: This will have to be run with a service's self.lock held once this is run from gevent so there is only
        # one such task executed throughout the whole cluster.

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

                # Lua program's args
                args = []
                args.append(int(topic_info.is_fifo)) # So it's easy to cast it to bool in Lua
                args.append(topic_info.max_depth)
                args.append(maxint)

                consumers = self.topic_to_cons[topic]
                for consumer in consumers:
                    sub_key = self.cons_to_sub[consumer]
                    self.logger.debug('Sub `%s` for topic `%s` to consumer `%s`', sub_key, topic, consumer)

                    keys.append(self.CONSUMER_MSG_IDS_PREFIX.format(sub_key))

                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug('keys `%s`', ', '.join(keys))

                move_result = self.run_lua(self.LUA_MOVE_TO_TARGET_QUEUES, keys, args)
                self.logger.debug('move_result `%s` `%s`', move_result, type(move_result))

# ################################################################################################################################

if __name__ == '__main__':

    import logging

    log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)

    from redis import StrictRedis
    kvdb = StrictRedis()

    client_id = 1

    topic1 = Topic('/state/vic/alerts')
    topic2 = Topic('/state/vic/news')

    lua_move_to_target_queues = """

        -- A function to copy Redis keys we operate over to a table which skips the first one, the source queue.
        local function get_target_queues(keys)
            local target_queues = {}
            if #keys == 2 then
              target_queues = {keys[2]}
            else
                for idx = 1, #KEYS do
                    -- Note - the whole point is that we're skipping the first few items which are not target queues
                    target_queues[idx] = KEYS[idx+2]
                end
            end
            return target_queues
        end

        local source_queue = KEYS[1]
        local is_fifo = tonumber(ARGV[1])
        local max_depth = tonumber(ARGV[2])
        local zset_command

        if is_fifo then
            zset_command = 'zrevrange'
        else
            zset_command = 'zrange'
        end

        local target_queues = get_target_queues(KEYS)
        local ids = redis.pcall(zset_command, source_queue, 0, max_depth)

        for queue_idx, target_queue in ipairs(target_queues) do
            for id_idx, id in ipairs(ids) do
                redis.call('lpush', target_queue, id)
            end
        end

        for id_idx, id in ipairs(ids) do
            redis.pcall('zrem', source_queue, id)
        end
        """

    lua_get_from_cons_queue = """

       local cons_queue = KEYS[1]
       local cons_in_flight = KEYS[2]
       local msg_key = KEYS[3]

       local max_batch_size = tonumber(ARGV[1])
       local now = ARGV[2]
        
       local ids = redis.pcall('lrange', cons_queue, 0, max_batch_size)
       local values = redis.pcall('hmget', msg_key, unpack(ids))

        for id_idx, id in ipairs(ids) do
            redis.pcall('hset', cons_in_flight, id, now)
            redis.pcall('lrem', cons_queue, 0, id)
        end

       return values
    """

    lua_reject = """

       local cons_queue = KEYS[1]
       local cons_in_flight = KEYS[2]
       local ids = ARGV

       redis.pcall('hdel', cons_in_flight, unpack(ids))

        for id_idx, id in ipairs(ids) do
            redis.call('lpush', cons_queue, id)
        end
    """

    ps = RedisPubSub(kvdb)

    ps.add_lua_program(ps.LUA_MOVE_TO_TARGET_QUEUES, lua_move_to_target_queues)
    ps.add_lua_program(ps.LUA_GET_FROM_CONSUMER_QUEUE, lua_get_from_cons_queue)
    ps.add_lua_program(ps.LUA_REJECT, lua_reject)

    ps.add_topic(topic1)
    ps.add_topic(topic2)

    # TODO: This will done from GUI
    ps.prod_to_topic[client_id] = set()
    ps.prod_to_topic[client_id].add(topic1.name)

    ps.topic_to_prod[topic1.name] = set()
    ps.topic_to_prod[topic1.name].add(client_id)

    # Subscribe
    sub_ctx1 = SubCtx()
    sub_ctx1.client_id = 1
    sub_ctx1.topics = [topic1.name, topic2.name]

    sub_ctx2 = SubCtx()
    sub_ctx2.client_id = 2
    sub_ctx2.topics = [topic1.name]

    sub_key1 = ps.subscribe(sub_ctx1)
    sub_key2 = ps.subscribe(sub_ctx2)

    # Publish
    pub_ctx = PubCtx()
    pub_ctx.client_id = client_id

    for topic in(topic1, topic2):
        for x in range(2):
            pub_ctx.topic = topic.name
            pub_ctx.msg = Message(new_cid())
    
            ps.publish(pub_ctx)

    # Move messages to target queues
    # TODO: This will be done in background
    ps.move_to_target_queues()

    # Get
    get_ctx1 = GetCtx()
    get_ctx1.sub_key = sub_key1

    to_be_rejected = []

    for msg in ps.get(get_ctx1):
        to_be_rejected.append(msg.msg_id)

    get_ctx2 = GetCtx()
    get_ctx2.sub_key = sub_key2

    for msg in ps.get(get_ctx2):
        pass

    # Reject one of the messages
    reject_ctx = RejectCtx()
    reject_ctx.sub_key = sub_key1
    reject_ctx.msg_ids.extend(to_be_rejected)

    ps.reject(reject_ctx)