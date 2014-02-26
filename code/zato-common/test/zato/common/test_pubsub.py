# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from json import loads
from logging import getLogger
from operator import attrgetter
from time import sleep
from unittest import TestCase

# Arrow
import arrow

# Nose
from nose.tools import eq_

# Redis
from redis import ConnectionError, Redis

# Zato
from zato.common import PUB_SUB
from zato.common.pubsub import AckCtx, Client, Consumer, GetCtx, Message, PubCtx, RedisPubSub, RejectCtx, SubCtx, Topic
from zato.common.util import new_cid

logger = getLogger(__name__)

class RedisPubSubTestCase(TestCase):

    def setUp(self):
        self.key_prefix = 'zato:pubsub:{}:'.format(new_cid())
        self.kvdb = Redis()

        try:
            self.kvdb.ping()
        except ConnectionError:
            self.has_redis = False
        else:
            self.has_redis = True

    def tearDown(self):
        #for key in self.kvdb.keys('{}*'.format(self.key_prefix)):
        #    self.kvdb.delete(key)
        pass

    def xtest_sub_key_generation(self):
        """ Checks whether a sub_key is generated if none is provided on input during subscribing.
        """
        sub_ctx = SubCtx()
        sub_ctx.client_id = '111'
        sub_ctx.topics = ['aaa']

        ps = RedisPubSub(self.kvdb)
        sub_key = ps.subscribe(sub_ctx)

        # Does it looks like a CID?
        eq_(len(sub_key), 28)
        eq_(sub_key[0], 'K')

    def xtest_full_path(self):
        """ Tests full sub/pub/ack/reject path with 4 topics and 3 clients. Doesn't test background tasks.
        """
        # Give up early if there is no connection to Redis at all
        if not self.has_redis:
            return

        """ What is tested.

        - 3 clients connect to pub/sub: CRM, Billing and ERP.
        - 4 topics are created: /cust/new, /cust/update, /adsl/new and /adsl/update

        - Subscriptions are:

          - CRM subs to /adsl/new
          - CRM subs to /adsl/update

          - Billing subs to /cust/new
          - Billing subs to /cust/update

          - ERP subs to /adsl/new
          - ERP subs to /adsl/update

        - Publications are:

          - CRM publishes Msg-CRM1 to /cust/new -------------- TTL of 0.1s
          - CRM publishes Msg-CRM2 to /cust/update ----------- TTL of 0.2s

          - Billing publishes Msg-Billing1 to /adsl/new ------ TTL of 0.3s
          - Billing publishes Msg-Billing2 to /adsl/update --- TTL of 3600s

          - (ERP doesn't publish anything)

        - Expected deliveries are:

          - Msg-CRM1 goes to Billing
          - Msg-CRM2 goes to Billing

          - Msg-Billing1 goes to CRM
          - Msg-Billing2 goes to CRM

          - Msg-Billing1 goes to ERP
          - Msg-Billing2 goes to ERP

        - Confirmations are:

          - CRM acks Msg-Billing1
          - CRM rejects Msg-Billing2

          - Billing acks Msg-CRM1
          - Billing acks Msg-CRM2

          - ERP rejects Msg-Billing1
          - ERP acks Msg-Billing2

        - Clean up tasks are

          - Msg-CRM1 is deleted because it's confirmed by its only recipient of Billing
          - Msg-CRM2 is deleted because it's confirmed by its only recipient of Billing

          - Msg-Billing1 is deleted because:

            - CRM confirms it
            - ERP rejects it but the message's TTL is 0.3s so it times out
              (In real world ERP would have possibly acknowledged it in say, 2s, but it would've been too late)

          - Msg-Billing2 is not deleted because:

            - ERP confirms it
            - CRM rejects it and the message's TTL is 3600s so it's still around when a clean up task runs

        """

        ps = RedisPubSub(self.kvdb, self.key_prefix)

        msg_billing1_value = '"msg_billing1"'
        msg_billing2_value = '"msg_billing2"'

        msg_crm1_value = '"msg_crm1"'
        msg_crm2_value = '"msg_crm2"'

        # Check all the Lua programs are loaded

        eq_(len(ps.lua_programs), 8)

        for attr in dir(ps):
            if attr.startswith('LUA'):
                value = getattr(ps, attr)
                self.assertTrue(value in ps.lua_programs)

        topic_cust_new = Topic('/cust/new')
        topic_cust_update = Topic('/cust/update')

        topic_adsl_new = Topic('/adsl/new')
        topic_adsl_update = Topic('/adsl/update')

        ps.add_topic(topic_cust_new)
        ps.add_topic(topic_cust_update)

        ps.add_topic(topic_adsl_new)
        ps.add_topic(topic_adsl_update)

        # Check all the topics are cached locally

        eq_(len(ps.topics), 4)

        for topic in(topic_cust_new, topic_cust_update, topic_adsl_new, topic_adsl_update):
            eq_(ps.topics[topic.name], topic)

        client_id_crm = Client('CRM', 'CRM')
        client_id_billing = Client('Billing', 'Billing')
        client_id_erp = Client('ERP', 'ERP')

        ps.add_producer(client_id_crm, topic_cust_new)
        ps.add_producer(client_id_crm, topic_cust_update)

        ps.add_producer(client_id_billing, topic_adsl_new)
        ps.add_producer(client_id_billing, topic_adsl_update)

        # Check producers have been registered for topics

        eq_(len(ps.prod_to_topic), 2)

        self.assertTrue(client_id_crm.id in ps.prod_to_topic)
        self.assertTrue(client_id_billing.id in ps.prod_to_topic)
        self.assertTrue(client_id_erp.id not in ps.prod_to_topic)

        self.assertTrue(isinstance(ps.prod_to_topic[client_id_crm.id], set))
        eq_(sorted(ps.prod_to_topic[client_id_crm.id]), ['/cust/new', '/cust/update'])

        self.assertTrue(isinstance(ps.prod_to_topic[client_id_billing.id], set))
        eq_(sorted(ps.prod_to_topic[client_id_billing.id]), ['/adsl/new', '/adsl/update'])

        # Subscribe all the systems

        sub_ctx_crm = SubCtx()
        sub_ctx_crm.client_id = client_id_crm.id
        sub_ctx_crm.topics = [topic_adsl_new.name, topic_adsl_update.name]

        sub_ctx_billing = SubCtx()
        sub_ctx_billing.client_id = client_id_billing.id
        sub_ctx_billing.topics = [topic_cust_new.name, topic_cust_update.name]

        sub_ctx_erp = SubCtx()
        sub_ctx_erp.client_id = client_id_erp.id
        sub_ctx_erp.topics = [topic_adsl_new.name, topic_adsl_update.name]

        sub_key_crm = 'sub_key_crm'
        sub_key_billing = 'sub_key_billing'
        sub_key_erp = 'sub_key_erp'

        received_sub_key_crm = ps.subscribe(sub_ctx_crm, sub_key_crm)
        received_sub_key_billing = ps.subscribe(sub_ctx_billing, sub_key_billing)
        received_sub_key_erp = ps.subscribe(sub_ctx_erp, sub_key_erp)

        eq_(sub_key_crm, received_sub_key_crm)
        eq_(sub_key_billing, received_sub_key_billing)
        eq_(sub_key_erp, received_sub_key_erp)

        eq_(sorted(ps.sub_to_cons.items()), [('sub_key_billing', 'Billing'), ('sub_key_crm', 'CRM'), ('sub_key_erp', 'ERP')])
        eq_(sorted(ps.cons_to_sub.items()), [('Billing', 'sub_key_billing'), ('CRM', 'sub_key_crm'), ('ERP', 'sub_key_erp')])

        # CRM publishes Msg-CRM1 to /cust/new
        pub_ctx_msg_crm1 = PubCtx()
        pub_ctx_msg_crm1.client_id = client_id_crm.id
        pub_ctx_msg_crm1.topic = topic_cust_new.name
        pub_ctx_msg_crm1.msg = Message(msg_crm1_value, mime_type='text/xml', priority=1, expiration=0.1)

        msg_crm1_id = ps.publish(pub_ctx_msg_crm1)

        # CRM publishes Msg-CRM2 to /cust/new
        pub_ctx_msg_crm2 = PubCtx()
        pub_ctx_msg_crm2.client_id = client_id_crm.id
        pub_ctx_msg_crm2.topic = topic_cust_update.name
        pub_ctx_msg_crm2.msg = Message(msg_crm2_value,  mime_type='application/json', priority=2, expiration=0.2)

        msg_crm2_id = ps.publish(pub_ctx_msg_crm2)

        # Billing publishes Msg-Billing1 to /adsl/new
        pub_ctx_msg_billing1 = PubCtx()
        pub_ctx_msg_billing1.client_id = client_id_billing.id
        pub_ctx_msg_billing1.topic = topic_adsl_new.name
        pub_ctx_msg_billing1.msg = Message(msg_billing1_value,  mime_type='application/soap+xml', priority=3, expiration=0.3)

        msg_billing1_id = ps.publish(pub_ctx_msg_billing1)

        # Billing publishes Msg-Billing2 to /adsl/update
        pub_ctx_msg_billing2 = PubCtx()
        pub_ctx_msg_billing2.client_id = client_id_billing.id
        pub_ctx_msg_billing2.topic = topic_adsl_update.name

        # Nothing except payload and expiration set, defaults should be used
        msg_billing2 = Message(msg_billing2_value, expiration=3600)
        pub_ctx_msg_billing2.msg = msg_billing2

        msg_billing2_id = ps.publish(pub_ctx_msg_billing2)

        keys = self.kvdb.keys('{}*'.format(self.key_prefix))
        eq_(len(keys), 9)

        expected_keys = [ps.MSG_VALUES_KEY, ps.MSG_EXPIRE_AT_KEY, ps.LAST_PUB_TIME_KEY]
        for topic in topic_cust_new, topic_cust_update, topic_adsl_new, topic_adsl_update:
            expected_keys.append(ps.MSG_IDS_PREFIX.format(topic.name))

        for key in expected_keys:
            self.assertIn(key, keys)

        # Check values of messages published
        self._check_msg_values_metadata(ps, msg_crm1_id, msg_crm2_id, msg_billing1_id, msg_billing2_id, True)

        # Now move the messages just published to each of the subscriber's queue.
        # In a real environment this is done by a background job.
        ps.move_to_target_queues()

        # Now all the messages have been moved we can check if everything is in place
        # ready for subscribers to get their messages.

        keys = self.kvdb.keys('{}*'.format(self.key_prefix))
        eq_(len(keys), 9)

        self.assertIn(ps.UNACK_COUNTER_KEY, keys)
        self.assertIn(ps.MSG_VALUES_KEY, keys)

        for sub_key in(sub_key_crm, sub_key_billing, sub_key_erp):
            key = ps.CONSUMER_MSG_IDS_PREFIX.format(sub_key)
            self.assertIn(key, keys)

        self._check_unack_counter(ps, msg_crm1_id, msg_crm2_id, msg_billing1_id, msg_billing2_id, 1, 1, 2, 2)

        # Check values of messages published are still there
        self._check_msg_values_metadata(ps, msg_crm1_id, msg_crm2_id, msg_billing1_id, msg_billing2_id, True)

        # Check that each recipient has expected message IDs in its respective message queue
        keys = self.kvdb.keys(ps.CONSUMER_MSG_IDS_PREFIX.format('*'))
        eq_(len(keys), 3)

        msg_ids_crm = self.kvdb.lrange(ps.CONSUMER_MSG_IDS_PREFIX.format(sub_key_crm), 0, 100)
        msg_ids_billing = self.kvdb.lrange(ps.CONSUMER_MSG_IDS_PREFIX.format(sub_key_billing), 0, 100)
        msg_ids_erp = self.kvdb.lrange(ps.CONSUMER_MSG_IDS_PREFIX.format(sub_key_erp), 0, 100)

        eq_(len(msg_ids_crm), 2)
        eq_(len(msg_ids_billing), 2)
        eq_(len(msg_ids_erp), 2)

        self.assertIn(msg_billing1_id, msg_ids_crm)
        self.assertIn(msg_billing2_id, msg_ids_crm)

        self.assertIn(msg_billing1_id, msg_ids_erp)
        self.assertIn(msg_billing2_id, msg_ids_erp)

        self.assertIn(msg_crm1_id, msg_ids_billing)
        self.assertIn(msg_crm1_id, msg_ids_billing)

        # Now that the messages are in queues, let's fetch them

        get_ctx_crm = GetCtx()
        get_ctx_crm.sub_key = sub_key_crm

        get_ctx_billing = GetCtx()
        get_ctx_billing.sub_key = sub_key_billing

        get_ctx_erp = GetCtx()
        get_ctx_erp.sub_key = sub_key_erp

        msgs_crm = sorted(list(ps.get(get_ctx_crm)), key=attrgetter('payload'))
        msgs_billing = sorted(list(ps.get(get_ctx_billing)), key=attrgetter('payload'))
        msgs_erp = sorted(list(ps.get(get_ctx_erp)), key=attrgetter('payload'))

        eq_(len(msgs_crm), 2)
        eq_(len(msgs_billing), 2)
        eq_(len(msgs_erp), 2)

        self._assert_has_msg_metadata(msgs_crm, msg_billing1_id, 'application/soap+xml', 3, 0.3)
        self._assert_has_msg_metadata(msgs_crm, msg_billing2_id, 'text/plain', 5, 3600)

        self._assert_has_msg_metadata(msgs_billing, msg_crm1_id, 'text/xml', 1, 0.1)
        self._assert_has_msg_metadata(msgs_billing, msg_crm2_id, 'application/json', 2, 0.2)

        self._assert_has_msg_metadata(msgs_erp, msg_billing1_id, 'application/soap+xml', 3, 0.3)
        self._assert_has_msg_metadata(msgs_erp, msg_billing2_id, 'text/plain', 5, 3600)

        # Check in-flight status for each message got
        keys = self.kvdb.keys(ps.CONSUMER_IN_FLIGHT_DATA_PREFIX.format('*'))
        eq_(len(keys), 3)

        now = arrow.utcnow()

        self._check_in_flight(ps, now, sub_key_crm, sub_key_billing, sub_key_erp, msg_crm1_id, msg_crm2_id,
                msg_billing1_id, msg_billing2_id, True, True, True, True, True, True)

        # Messages should still be undelivered hence their unack counters are not touched at this point
        self._check_unack_counter(ps, msg_crm1_id, msg_crm2_id, msg_billing1_id, msg_billing2_id, 1, 1, 2, 2)

        # ########################################################################################################################

        # Messages are fetched, they can be confirmed or rejected now

        # CRM
        ack_ctx_crm = AckCtx()
        ack_ctx_crm.sub_key = sub_key_crm
        ack_ctx_crm.append(msg_billing1_id)

        reject_ctx_crm = RejectCtx()
        reject_ctx_crm.sub_key = sub_key_crm
        reject_ctx_crm.append(msg_billing2_id)

        ps.acknowledge(ack_ctx_crm)
        ps.reject(reject_ctx_crm)

        # One in-flight less
        self._check_in_flight(ps, now, sub_key_crm, sub_key_billing, sub_key_erp, msg_crm1_id, msg_crm2_id,
                msg_billing1_id, msg_billing2_id, False, False, True, True, True, True)

        # Rejections, as with reject_ctx_crm, don't change unack count
        self._check_unack_counter(ps, msg_crm1_id, msg_crm2_id, msg_billing1_id, msg_billing2_id, 1, 1, 1, 2)

        # Billing
        ack_ctx_billing = AckCtx()
        ack_ctx_billing.sub_key = sub_key_billing
        ack_ctx_billing.append(msg_crm1_id)
        ack_ctx_billing.append(msg_crm2_id)

        ps.acknowledge(ack_ctx_billing)

        # Two in-flight less
        self._check_in_flight(ps, now, sub_key_crm, sub_key_billing, sub_key_erp, msg_crm1_id, msg_crm2_id,
                msg_billing1_id, msg_billing2_id, False, False, False, False, True, True)

        # Again, rejections, as with reject_ctx_crm, don't change unack count
        self._check_unack_counter(ps, None, None, msg_billing1_id, msg_billing2_id, 1, 1, 1, 2)

        # ERP
        reject_ctx_erp = RejectCtx()
        reject_ctx_erp.sub_key = sub_key_erp
        reject_ctx_erp.append(msg_billing1_id)

        ack_ctx_erp = AckCtx()
        ack_ctx_erp.sub_key = sub_key_erp
        ack_ctx_erp.append(msg_billing2_id)

        ps.reject(reject_ctx_erp)
        ps.acknowledge(ack_ctx_erp)

        # Another in-flight less
        self._check_in_flight(ps, now, sub_key_crm, sub_key_billing, sub_key_erp, msg_crm1_id, msg_crm2_id,
                msg_billing1_id, msg_billing2_id, False, False, False, False, False, False)

        # And again, rejections, as with reject_ctx_crm, don't change unack count
        self._check_unack_counter(ps, None, None, msg_billing1_id, msg_billing2_id, 1, 1, 1, 1)

        # Values should be still there because no background job run to clean them up
        self._check_msg_values_metadata(ps, msg_crm1_id, msg_crm2_id, msg_billing1_id, msg_billing2_id, False)

        # Sleep for a moment to make sure enough time passes for messages to expire
        sleep(0.4)

        # Deletes everything except for Msg-Billing2 which has a TTL of 3600
        ps.delete_expired()

        keys = self.kvdb.keys('{}*'.format(self.key_prefix))
        eq_(len(keys), 7)

        expected_keys = [ps.MSG_VALUES_KEY, ps.MSG_EXPIRE_AT_KEY, ps.UNACK_COUNTER_KEY, 
                         ps.CONSUMER_MSG_IDS_PREFIX.format(sub_key_crm)]
        for key in expected_keys:
            self.assertTrue(key in keys, 'Key not found `{}` in `{}`'.format(key, keys))

        # Check all the remaining keys - still concerning Msg-Billing2 only
        # because this is the only message that wasn't confirmed nor expired.

        expire_at = self.kvdb.hgetall(ps.MSG_EXPIRE_AT_KEY)
        eq_(len(expire_at), 1)
        eq_(expire_at[msg_billing2_id], msg_billing2.expire_at_utc.isoformat())

        unack_counter = self.kvdb.hgetall(ps.UNACK_COUNTER_KEY)
        eq_(len(unack_counter), 1)
        eq_(unack_counter[msg_billing2_id], '1')

        crm_messages = self.kvdb.lrange(ps.CONSUMER_MSG_IDS_PREFIX.format(sub_key_crm), 0, 100)
        eq_(len(crm_messages), 1)
        eq_(crm_messages[0],msg_billing2_id)

        msg_values = self.kvdb.hgetall(ps.MSG_METADATA_KEY)
        eq_(len(msg_values), 4)
        eq_(sorted(loads(msg_values[msg_billing2_id]).items()), sorted(msg_billing2.to_dict().items()))

    # ############################################################################################################################

    def xtest_delete_from_topic_no_subscribers(self):
        """ Tests deleting of messages from a topic without subscribers.
        """
        ps = RedisPubSub(self.kvdb, self.key_prefix)

        msg_value = '"msg_value"'

        topic = Topic('/test/delete')
        ps.add_topic(topic)

        producer = Client('Producer', 'producer')
        ps.add_producer(producer, topic)

        pub_ctx = PubCtx()
        pub_ctx.client_id = producer.id
        pub_ctx.topic = topic.name
        pub_ctx.msg = Message(msg_value)

        msg_id = ps.publish(pub_ctx)

        # We've got a msg_id now and we know this is a topic with no subsribers. In that case, deleting a messages should
        # also delete all the metadata related to it along with its payload.

        # First, let's confirm the messages is actually there

        result = self.kvdb.zrange(ps.MSG_IDS_PREFIX.format(topic.name), 0, -1)
        eq_(result, [msg_id])

        result = self.kvdb.hgetall(ps.MSG_VALUES_KEY)
        eq_(len(result), 1)
        self.assertTrue(msg_id in result)

        result = self.kvdb.hgetall(ps.MSG_METADATA_KEY)
        eq_(len(result), 1)
        self.assertTrue(msg_id in result)

        result = self.kvdb.hgetall(ps.MSG_EXPIRE_AT_KEY)
        eq_(len(result), 1)
        self.assertTrue(msg_id in result)

        # Ok, now delete the message and confirm it's not in Redis anymore

        ps.delete_from_topic(topic.name, msg_id)

        result = self.kvdb.zrange(ps.MSG_IDS_PREFIX.format(topic.name), 0, -1)
        eq_(result, [])

        result = self.kvdb.hgetall(ps.MSG_VALUES_KEY)
        eq_({}, result)

        result = self.kvdb.hgetall(ps.MSG_METADATA_KEY)
        eq_({}, result)

        result = self.kvdb.hgetall(ps.MSG_EXPIRE_AT_KEY)
        eq_({}, result)

    # ############################################################################################################################

    def xtest_delete_from_topic_has_subscribers(self):
        """ Tests deleting of messages from a topic which has subscribers.
        """
        ps = RedisPubSub(self.kvdb, self.key_prefix)

        msg_value = '"msg_value"'

        topic = Topic('/test/delete')
        ps.add_topic(topic)

        producer = Client('Producer', 'producer')
        ps.add_producer(producer, topic)

        consumer = Consumer('Consumer', 'consumer', new_cid())
        ps.add_consumer(consumer, topic)

        pub_ctx = PubCtx()
        pub_ctx.client_id = producer.id
        pub_ctx.topic = topic.name
        pub_ctx.msg = Message(msg_value)

        msg_id = ps.publish(pub_ctx)

        # We've got a msg_id now and we know this is a topic which has a subscriber so deleting a message from the topic
        # should not delete it from any other place because the consumer may still hold onto it.

        # First, let's confirm the messages is actually there

        result = self.kvdb.zrange(ps.MSG_IDS_PREFIX.format(topic.name), 0, -1)
        eq_(result, [msg_id])

        result = self.kvdb.hgetall(ps.MSG_VALUES_KEY)
        eq_(len(result), 1)
        self.assertTrue(msg_id in result)

        result = self.kvdb.hgetall(ps.MSG_METADATA_KEY)
        eq_(len(result), 1)
        self.assertTrue(msg_id in result)

        result = self.kvdb.hgetall(ps.MSG_EXPIRE_AT_KEY)
        eq_(len(result), 1)
        self.assertTrue(msg_id in result)

        # Ok, now delete the message and confirm it's not in the topic anymore however it's still kept elsewhere.

        ps.delete_from_topic(topic.name, msg_id)

        result = self.kvdb.zrange(ps.MSG_IDS_PREFIX.format(topic.name), 0, -1)
        eq_(result, [])

        result = self.kvdb.hgetall(ps.MSG_VALUES_KEY)
        eq_(len(result), 1)
        self.assertTrue(msg_id in result)

        result = self.kvdb.hgetall(ps.MSG_METADATA_KEY)
        eq_(len(result), 1)
        self.assertTrue(msg_id in result)

        result = self.kvdb.hgetall(ps.MSG_EXPIRE_AT_KEY)
        eq_(len(result), 1)
        self.assertTrue(msg_id in result)

    # ############################################################################################################################

    def test_ack_delete_from(self):
        """ Tests ack and delete on a consumer's queue.
        """
        # Both ack and delete use the same implementation and it's only the user-exposed API that differs.

        ps = RedisPubSub(self.kvdb, self.key_prefix)

        msg_value = '"msg_value"'

        topic = Topic('/test/delete')
        ps.add_topic(topic)

        producer = Client('Producer', 'producer')
        ps.add_producer(producer, topic)

        consumer = Consumer('Consumer', 'consumer', sub_key=new_cid())
        ps.add_consumer(consumer, topic)

        pub_ctx = PubCtx()
        pub_ctx.client_id = producer.id
        pub_ctx.topic = topic.name
        pub_ctx.msg = Message(msg_value)

        msg_id = ps.publish(pub_ctx)
        ps.move_to_target_queues()

        # A message has been published and move to a consumer's queue so let's confirm the fact first.
        result = self.kvdb.lrange(ps.CONSUMER_MSG_IDS_PREFIX.format(consumer.sub_key), 0, -1)
        eq_(result, [msg_id])

        # Ok, now delete the message and confirm it's not in the consumer's queue anymore.

        ps.delete_from_consumer_queue(consumer.sub_key, msg_id)

        result = self.kvdb.lrange(ps.CONSUMER_MSG_IDS_PREFIX.format(consumer.sub_key), 0, -1)
        eq_(result, [])

    # ############################################################################################################################

    def _check_unack_counter(self, ps, msg_crm1_id, msg_crm2_id, msg_billing1_id, msg_billing2_id,
            msg_crm1_id_counter, msg_crm2_id_counter, msg_billing1_id_counter, msg_billing2_id_counter
        ):

        unack_counter = self.kvdb.hgetall(ps.UNACK_COUNTER_KEY)
        expected_counters = {}

        if msg_crm1_id:
            expected_counters[msg_crm1_id] = str(msg_crm1_id_counter)

        if msg_crm2_id:
            expected_counters[msg_crm2_id] = str(msg_crm2_id_counter)

        if msg_billing1_id:
            expected_counters[msg_billing1_id] = str(msg_billing1_id_counter)

        if msg_billing2_id:
            expected_counters[msg_billing2_id] = str(msg_billing2_id_counter)

        eq_(sorted(unack_counter.items()), sorted(expected_counters.items()))

    # ############################################################################################################################

    def _check_in_flight(self, ps, now, sub_key_crm, sub_key_billing, sub_key_erp, msg_crm1_id, msg_crm2_id,
            msg_billing1_id, msg_billing2_id, crm_needs_billing1_id, crm_needs_billing2_id,
            billing_needs_crm1_id, billing_needs_crm2_id, erp_needs_billing1_id, erp_needs_billing2_id):

        # CRM
        in_flight_crm_ids = self.kvdb.smembers(ps.CONSUMER_IN_FLIGHT_IDS_PREFIX.format(sub_key_crm))
        in_flight_crm_data = self.kvdb.hgetall(ps.CONSUMER_IN_FLIGHT_DATA_PREFIX.format(sub_key_crm))

        if crm_needs_billing1_id:
            in_flight_crm_data_msg1 = in_flight_crm_data[msg_billing1_id]
            self.assertLess(arrow.get(in_flight_crm_data_msg1), now)
            eq_(sorted(in_flight_crm_ids), sorted(in_flight_crm_data.keys()))
        else:
            self.assertNotIn(msg_billing1_id, in_flight_crm_data)

        if crm_needs_billing2_id:
            in_flight_crm_data_msg2 = in_flight_crm_data[msg_billing2_id]
            self.assertLess(arrow.get(in_flight_crm_data_msg2), now)
            eq_(sorted(in_flight_crm_ids), sorted(in_flight_crm_data.keys()))
        else:
            self.assertNotIn(msg_billing2_id, in_flight_crm_data)

        # Billing
        in_flight_billing_ids = self.kvdb.smembers(ps.CONSUMER_IN_FLIGHT_IDS_PREFIX.format(sub_key_billing))
        in_flight_billing_data = self.kvdb.hgetall(ps.CONSUMER_IN_FLIGHT_DATA_PREFIX.format(sub_key_billing))

        if billing_needs_crm1_id:
            in_flight_billing_data_msg1 = in_flight_billing_data[msg_crm1_id]
            self.assertLess(arrow.get(in_flight_billing_data_msg1), now)
            eq_(sorted(in_flight_billing_ids), sorted(in_flight_billing_data.keys()))
        else:
            self.assertNotIn(msg_crm1_id, in_flight_billing_data)

        if billing_needs_crm2_id:
            in_flight_billing_data_msg2 = in_flight_billing_data[msg_crm2_id]
            self.assertLess(arrow.get(in_flight_billing_data_msg2), now)
            eq_(sorted(in_flight_billing_ids), sorted(in_flight_billing_data.keys()))
        else:
            self.assertNotIn(msg_crm2_id, in_flight_billing_data)

        # ERP
        in_flight_erp_ids = self.kvdb.smembers(ps.CONSUMER_IN_FLIGHT_IDS_PREFIX.format(sub_key_erp))
        in_flight_erp_data = self.kvdb.hgetall(ps.CONSUMER_IN_FLIGHT_DATA_PREFIX.format(sub_key_erp))

        if erp_needs_billing1_id:
            in_flight_erp_data_msg1 = in_flight_erp_data[msg_billing1_id]
            self.assertLess(arrow.get(in_flight_erp_data_msg1), now)
            eq_(sorted(in_flight_erp_ids), sorted(in_flight_erp_data.keys()))
        else:
            self.assertNotIn(msg_billing1_id, in_flight_erp_data)

        if erp_needs_billing2_id:
            in_flight_erp_data_msg2 = in_flight_erp_data[msg_billing2_id]
            self.assertLess(arrow.get(in_flight_erp_data_msg2), now)
            eq_(sorted(in_flight_erp_ids), sorted(in_flight_erp_data.keys()))
        else:
            self.assertNotIn(msg_billing2_id, in_flight_erp_data)

    # ############################################################################################################################

    def _check_msg_values_metadata(self, ps, msg_crm1_id, msg_crm2_id, msg_billing1_id, msg_billing2_id, before_last_acknowledge):

        # Out of all messages that are expected to be acknowledged, when the last one actually is, there should be
        # less messages in Redis because the last acknowledgment deletes a message's key from msg_values.
        msgs_expected_no = 4 if before_last_acknowledge else 2

        raw_msgs_metadata = self.kvdb.hgetall(ps.MSG_METADATA_KEY)
        eq_(len(raw_msgs_metadata), 4)

        raw_msgs_payload = self.kvdb.hgetall(ps.MSG_VALUES_KEY)
        eq_(len(raw_msgs_payload), msgs_expected_no)

        msgs_metadata = {}
        msgs_payload = {}

        for msg_id, msg_data in raw_msgs_metadata.items():
            msgs_metadata[msg_id] = Message(**loads(msg_data))

        msgs_payload = dict(raw_msgs_payload.items())

        if before_last_acknowledge:
            eq_(msgs_payload[msg_crm1_id], '"msg_crm1"')
            eq_(msgs_payload[msg_crm2_id], '"msg_crm2"')

        eq_(msgs_payload[msg_billing1_id], '"msg_billing1"')
        eq_(msgs_payload[msg_billing2_id], '"msg_billing2"')

        # After acks only billing messages are not acked yet
        expected_msg_ids = (
            msg_crm1_id, msg_crm2_id, msg_billing1_id, msg_billing2_id) if before_last_acknowledge else \
                (msg_billing1_id, msg_billing2_id)

        for msg_id in expected_msg_ids:
            self.assertIn(msg_id, msgs_metadata)

        if before_last_acknowledge:
            msg_crm1 = msgs_metadata[msg_crm1_id]
            msg_crm2 = msgs_metadata[msg_crm2_id]

            eq_(msg_crm1.priority, 1)
            eq_(msg_crm1.mime_type, 'text/xml')
            eq_(msg_crm1.expiration, 0.1)

            eq_(msg_crm2.priority, 2)
            eq_(msg_crm2.mime_type, 'application/json')
            eq_(msg_crm2.expiration, 0.2)

        msg_billing1 = msgs_metadata[msg_billing1_id]
        msg_billing2 = msgs_metadata[msg_billing2_id]

        eq_(msg_billing1.priority, 3)
        eq_(msg_billing1.mime_type, 'application/soap+xml')
        eq_(msg_billing1.expiration, 0.3)

        eq_(msg_billing2.priority, 5)
        eq_(msg_billing2.mime_type, 'text/plain')
        eq_(msg_billing2.expiration, 3600)

    # ############################################################################################################################

    def _assert_has_msg_metadata(self, msgs, msg_id, mime_type, priority, expiration):
        for msg in msgs:
            if msg.msg_id == msg_id:
                eq_(msg.mime_type, mime_type, 'mime_type `{}` `{}`'.format(mime_type, msg))
                eq_(msg.priority, priority, 'priority `{}` `{}`'.format(priority, msg))
                eq_(msg.expiration, expiration, 'expiration `{}` `{}`'.format(expiration, msg))
                break
        else:
            raise Exception('Msg with msg_id `{}` not in `{}`'.format(msg_id, msgs))

    # ############################################################################################################################