# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from unittest import TestCase

# Nose
from nose.tools import eq_

# Redis
from redis import ConnectionError, Redis

# Zato
from zato.common.pubsub import AckCtx, GetCtx, Message, PubCtx, RedisPubSub, RejectCtx, SubCtx, Topic

logger = getLogger(__name__)

class RedisPubSubTestCase(TestCase):

    def setUp(self):
        self.kvdb = Redis()

        try:
            self.kvdb.ping()
        except ConnectionError:
            self.has_redis = False
        else:
            self.has_redis = True

            # Clean up in setUp instead of tearDown so we can be sure there are no stale keys
            # even before the first run.
            for key in self.kvdb.keys('zato:pubsub:*'):
                self.kvdb.delete(key)

    def test_full_path(self):
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

          - CRM publishes Msg-CRM1 to /cust/new
          - CRM publishes Msg-CRM2 to /cust/new

          - Billing publishes Msg-Billing1 to /adsl/new
          - Billing publishes Msg-Billing2 to /adsl/update

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
        """

        ps = RedisPubSub(self.kvdb)

        # Check all the Lua programs are loaded

        eq_(len(ps.lua_programs), 4)

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

        client_id_crm = 'CRM'
        client_id_billing = 'Billing'
        client_id_erp = 'ERP'

        ps.add_producer(client_id_crm, topic_cust_new)
        ps.add_producer(client_id_crm, topic_cust_update)

        ps.add_producer(client_id_billing, topic_adsl_new)
        ps.add_producer(client_id_billing, topic_adsl_update)

        # Check producers have been registered for topics

        eq_(len(ps.prod_to_topic), 2)

        self.assertTrue(client_id_crm in ps.prod_to_topic)
        self.assertTrue(client_id_billing in ps.prod_to_topic)
        self.assertTrue(client_id_erp not in ps.prod_to_topic)

        self.assertTrue(isinstance(ps.prod_to_topic[client_id_crm], set))
        eq_(sorted(ps.prod_to_topic[client_id_crm]), ['/cust/new', '/cust/update'])

        self.assertTrue(isinstance(ps.prod_to_topic[client_id_billing], set))
        eq_(sorted(ps.prod_to_topic[client_id_billing]), ['/adsl/new', '/adsl/update'])

        # Subscribe all the systems

        sub_ctx_crm = SubCtx()
        sub_ctx_crm.client_id = client_id_crm
        sub_ctx_crm.topics = [topic_adsl_new.name, topic_adsl_update.name]

        sub_ctx_billing = SubCtx()
        sub_ctx_billing.client_id = client_id_billing
        sub_ctx_billing.topics = [topic_cust_new.name, topic_cust_update.name]

        sub_ctx_erp = SubCtx()
        sub_ctx_erp.client_id = client_id_erp
        sub_ctx_erp.topics = [topic_adsl_new.name, topic_adsl_update.name]

        sub_key_crm = ps.subscribe(sub_ctx_crm)
        sub_key_billing = ps.subscribe(sub_ctx_billing)
        sub_key_erp = ps.subscribe(sub_ctx_erp)