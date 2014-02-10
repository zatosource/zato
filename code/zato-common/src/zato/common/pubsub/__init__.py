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
from json import dumps
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
    def __init__(self, payload='', msg_id=None, mime_type='text/plain', priority=5, expiration=60, expire_at=None):
        self.payload = payload
        self.msg_id = msg_id or new_cid()
        self.mime_type = mime_type
        self.priority = priority # In 1-9 range where 9 is top priority

        # expiration -> how many seconds a message should live
        # expire_at -> a datetime, in UTC, when it should expire
        # Either of these is required.

        self.expiration = expiration
        self.expire_at = expire_at

    def dumps(self):
        return dumps({
            'msg_id': self.msg_id,
            'payload': self.payload,
            'mime_type': self.mime_type,
            'priority': self.priority,
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
    def __init__(self, sub_key=None, batch_max_size=100, is_fifo=True):
        self.sub_key = sub_key
        self.batch_max_size = batch_max_size
        self.is_fifo = is_fifo # Fetch in FIFO or LIFO order

# ################################################################################################################################

class AckCtx(object):
    """ A set of data describing an acknowledge of a message fetched.
    """
    def __init__(self, msg_id=None):
        self.msg_id = msg_id

# ################################################################################################################################

class PubSub(object):
    """ An entry point to the pub/sub mechanism. Must be partly subclassed by concrete implementation classes.
    """
    LUA_MOVE_TO_TARGET_QUEUES = 'move-to-target-queues'

    def __init__(self, *ignored_args, **ignored_kwargs):
        self.logger = getLogger(self.__class__.__name__)

        self.lua_programs = {}
        self.update_lock = RLock() # Held when modifying sets of currently known consumers and producers

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

    def add_lua_program(self, name, program):
        self.lua_programs[name] = self.kvdb.register_script(program)

    def run_lua(self, name, keys, args):
        return self.lua_programs[name](keys, args)

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
    ID_PREFIX = 'zato:pubsub:id:{}'
    ID_TO_TOPIC_KEY = 'zato:pubsub:id-to-topic'
    ID_EXP_PREFIX = 'zato:pubsub:id-exp:{}:{}'
    BACKUP_PREFIX = 'zato:pubsub:backup:{}'
    BACKLOG_FULL_KEY = 'zato:pubsub:backlog-full'
    CONS_ID_PREFIX = 'zato:pubsub:cons:id:{}'
    MSG_PREFIX = 'zato:pubsub:msg:{}'
    IN_FLIGHT_PREFIX = 'zato:pubsub:in-flight:{}'
    IN_FLIGHT_EXP_PREFIX = 'zato:pubsub:in-flight-exp:{}:{}'

    # ############################################################################################################################

    def __init__(self, kvdb):
        super(RedisPubSub, self).__init__()
        self.kvdb = kvdb

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

        id_key = self.ID_PREFIX.format(ctx.topic)
        id_exp_key = self.ID_EXP_PREFIX.format(ctx.topic, ctx.msg.msg_id)
        msg_key = self.MSG_PREFIX.format(ctx.topic)

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
            p.hset(msg_key, ctx.msg.msg_id, ctx.msg.dumps())
            #p.hset(self.ID_TO_TOPIC_KEY, ctx.msg.msg_id, ctx.topic)
            #p.setex(id_exp_key, ctx.msg.expiration, '')

            try:
                p.execute()
            except Exception, e:
                self.logger.error('Pub error `%s`', format_exc(e))
                raise
            else:
                self.logger.info('Published: `%s` to `%s', ctx.msg.msg_id, ctx.topic)

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

        self.logger.info('Client `%s` sub to topics `%s`', ctx.client_id, ', '.join(ctx.topics))
        return sub_key

    # ############################################################################################################################

    def get(self, ctx):
        self.logger.info('Fetching for sub_key `%s`', ctx.sub_key)
        with self.update_lock:

            client_id = self.sub_to_cons.get(ctx.sub_key)

            if not client_id:
                msg = 'Invalid sub_key `{}`'.format(ctx.sub_key)
                self.logger.warn(msg)
                raise ValueError(msg)

    # ############################################################################################################################

    def acknowledge(self, ctx):
        topic = self.kvdb.hget(self.ID_TO_TOPIC_KEY, ctx.msg_id)
        self.logger.info('Ack msg_id:`%s`, topic:`%s`', ctx.msg_id, topic)

        with self.kvdb.pipeline() as p:

            p.zrem(self.ID_PREFIX.format(topic), ctx.msg_id)
            p.hdel(self.ID_TO_TOPIC_KEY, ctx.msg_id)
            p.delete(self.ID_EXP_PREFIX.format(topic, ctx.msg_id))
            p.hdel(self.MSG_PREFIX.format(topic), ctx.msg_id)

            p.execute()

    def reject(self, msg_id):
        pass

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

                source_queue = self.ID_PREFIX.format(topic)
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
                    self.logger.info('Sub `%s` for topic `%s` from consumer `%s`', sub_key, topic, consumer)

                    keys.append(self.CONS_ID_PREFIX.format(sub_key))

                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug('keys `%s`', ', '.join(keys))

                move_result = self.run_lua(self.LUA_MOVE_TO_TARGET_QUEUES, keys, args)
                self.logger.info('move_result `%s` `%s`', move_result, type(move_result))

# ################################################################################################################################

if __name__ == '__main__':

    import logging

    log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format)

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
        local ids = unpack(redis.pcall(zset_command, source_queue, 0, max_depth))

        for idx, target_queue in ipairs(target_queues) do
            redis.pcall('sadd', target_queue, ids)
        end

        redis.pcall('zrem', source_queue, ids)
    """

    ps = RedisPubSub(kvdb)
    ps.add_lua_program(ps.LUA_MOVE_TO_TARGET_QUEUES, lua_move_to_target_queues)

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
    pub_ctx.topic = topic1.name
    pub_ctx.msg = Message('aaa')

    ps.publish(pub_ctx)

    # Move messages to target queues
    # TODO: This will be done in background
    ps.move_to_target_queues()

    # Get
    get_ctx1 = GetCtx()
    get_ctx1.sub_key = sub_key1
    ps.get(get_ctx1)

    get_ctx2 = GetCtx()
    get_ctx2.sub_key = sub_key2
    ps.get(get_ctx2)