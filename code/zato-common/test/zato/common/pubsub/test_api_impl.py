# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import BaseHTTPServer

# Zato
from zato.common import PUB_SUB
from zato.common.log_message import CID_LENGTH
from zato.common.pubsub import Client, Message, PubSubAPI, RedisPubSub, Topic
from zato.common.test import rand_bool, rand_int, rand_string
from .common import RedisPubSubCommonTestCase


class RedisPubSubAPITestCase(RedisPubSubCommonTestCase):

    def setUp(self):
        super(RedisPubSubAPITestCase, self).setUp()
        self.api = PubSubAPI(RedisPubSub(self.kvdb, self.key_prefix))

    def test_default_clients(self):
        # Initially, default clients are dummy ones.
        default_consumer = self.api.get_default_consumer()
        default_producer = self.api.get_default_producer()

        self.assertEquals(default_consumer.id, None)
        self.assertEquals(default_consumer.name, None)
        self.assertEquals(default_consumer.is_active, True)

        self.assertEquals(default_producer.id, None)
        self.assertEquals(default_producer.name, None)
        self.assertEquals(default_producer.is_active, True)

        cons_id = rand_int()
        cons_name = rand_string()
        cons_is_active = rand_bool()

        prod_name = rand_string()
        prod_id = rand_int()
        prod_is_active = rand_bool()

        cons = Client(cons_id, cons_name, cons_is_active)
        prod = Client(prod_id, prod_name, prod_is_active)

        self.api.set_default_consumer(cons)
        self.api.set_default_producer(prod)

        default_consumer = self.api.get_default_consumer()
        default_producer = self.api.get_default_producer()

        self.assertEquals(default_consumer.id, cons_id)
        self.assertEquals(default_consumer.name, cons_name)
        self.assertEquals(default_consumer.is_active, cons_is_active)

        self.assertEquals(default_producer.id, prod_id)
        self.assertEquals(default_producer.name, prod_name)
        self.assertEquals(default_producer.is_active, prod_is_active)

    def test_topic_add(self):
        name = rand_string()
        is_active = rand_bool()
        is_fifo = rand_bool()
        max_depth = rand_int()

        topic = Topic(name, is_active, is_fifo, max_depth)

        self.api.add_topic(topic)

        self.assertIn(name, self.api.impl.topics)
        self.assertEquals(len(self.api.impl.topics), 1)

        given = self.api.impl.topics[name]
        self.assertEquals(given.name, name)
        self.assertEquals(given.is_active, is_active)
        self.assertEquals(given.is_fifo, is_fifo)
        self.assertEquals(given.max_depth, max_depth)

        # Adding topic of the same name should not create a new topic because impl.topics is a dictionary
        self.api.add_topic(topic)
        self.assertEquals(len(self.api.impl.topics), 1)

    def test_topic_update(self):
        self.test_topic_add() # updating a topic works the same like creating it

    def _get_message(self):
        return Message()

    def test_message_defaults(self):
        msg = self._get_message()
        self.assertEquals(msg.payload, '')
        self.assertEquals(msg.topic, None)
        self.assertEquals(msg.mime_type, PUB_SUB.DEFAULT_MIME_TYPE)
        self.assertEquals(msg.priority, PUB_SUB.DEFAULT_PRIORITY)
        self.assertEquals(msg.expiration, PUB_SUB.DEFAULT_EXPIRATION)
        self.assertEquals(len(msg.msg_id), CID_LENGTH+1) # +1 because CID_LENGTH doesn't take 'K' into account
        self.assertEquals(msg.producer, None)
        self.assertEquals(msg.expiration, PUB_SUB.DEFAULT_EXPIRATION)

        #

        #self.assertEquals(msg.creation_time_utc, 1)
        #self.assertEquals(msg.expire_at_utc, 2)
