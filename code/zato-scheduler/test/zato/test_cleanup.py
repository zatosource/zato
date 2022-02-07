# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# This needs to be done as soon as possible
from gevent.monkey import patch_all
patch_all()

# stdlib
import os
from datetime import datetime
from unittest import main

# gevent
from gevent import sleep

# Zato
from zato.common import PUBSUB
from zato.common.test import CommandLineTestCase
from zato.common.test.config import TestConfig
from zato.common.test.unittest_ import BasePubSubRestTestCase, PubSubConfig, PubSubAPIRestImpl
from zato.common.typing_ import cast_
from zato.scheduler.cleanup.core import run_cleanup

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, intnone
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

_default = PUBSUB.DEFAULT

sec_name = _default.TEST_SECDEF_NAME
username = _default.TEST_USERNAME


delta_environ_key = 'ZATO_SCHED_DELTA'

# ################################################################################################################################
# ################################################################################################################################

class PubSubCleanupTestCase(CommandLineTestCase, BasePubSubRestTestCase):

    should_init_rest_client = False

    def setUp(self) -> 'None':
        self.rest_client.init(username=username, sec_name=sec_name)
        self.api_impl = PubSubAPIRestImpl(self, self.rest_client)
        super().setUp()

# ################################################################################################################################

    def _run_cleanup_old_subscriptions_one_sub_key(
        self,
        topic_name:'str',
        env_delta:'int',
        limit_sub_inactivity:'intnone' = None
        ) -> 'None':

        # Filter our warnings coming from requests
        import warnings
        warnings.filterwarnings(action='ignore', message='unclosed', category=ResourceWarning)

        # Before subscribing, make sure we are not currently subscribed
        self._unsubscribe(topic_name)

        # Subscribe to the topic
        response_initial = self.rest_client.post(PubSubConfig.PathSubscribe + topic_name)

        # Wait a moment to make sure the subscription data is created
        sleep(2)

        sub_key = response_initial['sub_key']
        sub_key

        data = 'abc'
        len_messages = 2

        for _ in range(len_messages):
            self._publish(topic_name, data)

        # Because each publication is synchronous, we now know that all of them are in the subscriber's queue
        # which means that we can delete them already.

        # Use the delta value from the environment to override any per-topic cleanup time configuration.
        # Such a delta indicates after a passage of how many seconds we will consider a subscribers as gone,
        # that is, after how many seconds since its last interaction time it will be deleted.
        if env_delta:

            # Export a variable with delta as required by the underlying cleanup implementation
            os.environ[delta_environ_key] = str(env_delta)

            # Sleep a little bit longer to make sure that we actually exceed the delta
            sleep_extra = env_delta * 0.1
            sleep(env_delta + sleep_extra)

        # We get here if there was no delta, in which case we still need to sleep
        # based on the topic's subscription inactivity limit.
        elif limit_sub_inactivity:
            sleep_extra = limit_sub_inactivity * 0.1
            sleep(limit_sub_inactivity + sleep_extra)

        # Run the cleanup procedure now
        cleanup_result = run_cleanup()

        self.assertEqual(cleanup_result.found_total_queue_messages, len_messages)
        self.assertListEqual(cleanup_result.found_sk_list, [sub_key])

        # The cleanup procedure invoked the server which in turn deleted our subscription,
        # which means that we can sleep for a moment now to make sure that it is actually
        # deleted and then we can try to get message for the now-already-deleted sub_key.
        # We expect that it will result in a permissioned denied, as though this sub_key never existed.

        # Wait a moment ..
        sleep(0.1)

        receive_result = cast_('anydict', self._receive(topic_name, expect_ok=False))

        cid = receive_result['cid']

        self.assertIsInstance(cid, str)
        self.assertTrue(len(cid) >= 20)

        self.assertEqual(receive_result['result'], 'Error')
        self.assertEqual(receive_result['details'], f'You are not subscribed to topic `{topic_name}`')

# ################################################################################################################################

    def test_cleanup_old_subscriptions_no_sub_keys(self) -> 'None':

        # In this test, we check subscriptions to shared topics
        topic_name = TestConfig.pubsub_topic_test

        # Make sure we are not subscribed to anything
        self._unsubscribe(topic_name)

        # Indicate after a passage of how many seconds we will consider a subscribers as gone,
        # that is, after how many seconds since its last interaction time it will be deleted.
        delta = 1

        # Export a variable with delta as required by the underlying cleanup implementation
        os.environ[delta_environ_key] = str(delta)

        # Run the cleanup procedure now
        cleanup_result = run_cleanup()

        self.assertEqual(cleanup_result.found_all_topics, 0)
        self.assertEqual(cleanup_result.found_total_queue_messages, 0)
        self.assertEqual(cleanup_result.max_limit_sub_inactivity, delta)
        self.assertListEqual(cleanup_result.found_sk_list, [])
        self.assertListEqual(cleanup_result.topics_cleaned_up, [])

# ################################################################################################################################

    def test_cleanup_old_subscriptions_one_sub_key_with_env_delta_default_topic(self):

        # In this test, we explicitly specify a seconds delta to clean up messages by.
        env_delta = 1

        # Use the default topic here
        topic_name = TestConfig.pubsub_topic_test

        # Run the actual test
        self._run_cleanup_old_subscriptions_one_sub_key(topic_name, env_delta)

# ################################################################################################################################

    def test_cleanup_old_subscriptions_one_sub_key_with_env_delta_new_topic(self):

        # In this test, we explicitly specify a seconds delta to clean up messages by.
        # I.e. even if we use a new test topic below, the delta is given on input too.
        env_delta = 1

        # Create a new topic for this test
        prefix = '/zato/test/'
        topic_name = prefix + datetime.utcnow().isoformat()

        # Command to invoke ..
        cli_params = ['pubsub', 'create-topic', '--name', topic_name]

        # Create the test topic here ..
        _ = self.run_zato_cli_json_command(cli_params) # type: anydict

        # Run the actual test
        self._run_cleanup_old_subscriptions_one_sub_key(topic_name, env_delta)

# ################################################################################################################################

    def test_cleanup_old_subscriptions_one_sub_key_no_env_delta(self):

        # In this test, we do not specify a seconds delta to clean up messages by
        # which means that its value will be taken from each topic separately.
        env_delta = 0

        # We explcitly request that inactive subscriptions should be deleted after that many seconds
        limit_sub_inactivity = 1

        # Create a new topic for this test
        prefix = '/zato/test/'
        topic_name = prefix + datetime.utcnow().isoformat()

        # Command to invoke ..
        cli_params = ['pubsub', 'create-topic', '--name', topic_name, '--limit-sub-inactivity', limit_sub_inactivity]

        # Create the test topic here ..
        _ = self.run_zato_cli_json_command(cli_params) # type: anydict

        # Run the actual test
        self._run_cleanup_old_subscriptions_one_sub_key(topic_name, env_delta, limit_sub_inactivity)

# ################################################################################################################################

    def test_cleanup_old_subscriptions_one_sub_key_env_delta_overrides_topic_delta(self):

        # In this test, we specify a short delta in the environment and we expect
        # that it will override the explicit inactivity limit configured for a new topic.
        # In other words, the environment variable has priority over what the topic has configured
        env_delta = 1

        # We explcitly request that inactive subscriptions should be deleted after that many seconds
        limit_sub_inactivity = 123456789

        # Create a new topic for this test
        prefix = '/zato/test/'
        topic_name = prefix + datetime.utcnow().isoformat()

        # Command to invoke ..
        cli_params = ['pubsub', 'create-topic', '--name', topic_name, '--limit-sub-inactivity', limit_sub_inactivity]

        # Create the test topic here ..
        _ = self.run_zato_cli_json_command(cli_params) # type: anydict

        # Run the actual test
        self._run_cleanup_old_subscriptions_one_sub_key(topic_name, env_delta, limit_sub_inactivity)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
