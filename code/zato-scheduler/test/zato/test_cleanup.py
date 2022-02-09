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
from zato.common.test import CommandLineTestCase, PubSubConfig
from zato.common.test.unittest_ import BasePubSubRestTestCase, PubSubAPIRestImpl
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

test_topic_prefix = PubSubConfig.TestTopicPrefix
delta_environ_key = 'ZATO_SCHED_DELTA'

# ################################################################################################################################
# ################################################################################################################################

class PubSubCleanupTestCase(CommandLineTestCase, BasePubSubRestTestCase):

    should_init_rest_client = False

    def setUp(self) -> 'None':

        # Set up a test client before each test ..
        self.rest_client.init(username=username, sec_name=sec_name)
        self.api_impl = PubSubAPIRestImpl(self, self.rest_client)

        # .. clean up any left over topics as well ..
        cli_params = ['pubsub', 'delete-topics', '--pattern', test_topic_prefix]
        _ = self.run_zato_cli_json_command(cli_params)

        # .. and call our parent
        super().setUp()

# ################################################################################################################################

    def _run_cleanup_old_pubsub_one_sub_key(
        self,
        topic_name:'str',
        *,
        env_delta:'intnone',
        limit_retention:'intnone',
        limit_sub_inactivity:'intnone',
        clean_up_subscriptions: 'bool' = True,
        clean_up_topics_without_subscribers: 'bool' = True,
        clean_up_topics_with_max_retention_reached: 'bool' = True,
        ) -> 'None':

        # Filter our warnings coming from requests
        import warnings
        warnings.filterwarnings(action='ignore', message='unclosed', category=ResourceWarning)

        # Assume we are not going to sleep after publishing
        after_publish_sleep_base = 0

        # All the messages published during this test
        messages_published = []

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
            msg = self._publish(topic_name, data)
            messages_published.append(msg['msg_id'])

        # Sort all the message IDs published for later use
        messages_published.sort()

        # Because each publication is synchronous, we now know that all of them are in the subscriber's queue
        # which means that we can delete them already.

        # Use the delta value from the environment to override any per-topic cleanup time configuration.
        # Such a delta indicates after a passage of how many seconds we will consider a subscribers as gone,
        # that is, after how many seconds since its last interaction time it will be deleted.
        if env_delta:

            # Export a variable with delta as required by the underlying cleanup implementation
            os.environ[delta_environ_key] = str(env_delta)

            # Our sleep time is based on the delta environment variable
            after_publish_sleep_base = env_delta

        elif limit_retention:
            # We are going to sleep based on the topic's max. retention time
            after_publish_sleep_base = limit_retention

        elif limit_sub_inactivity:
            # We need to sleep based on the topic's subscription inactivity limit.
            after_publish_sleep_base = limit_sub_inactivity

        # If requested to, sleep a little bit longer to make sure that we actually exceed the delta or retention time
        if after_publish_sleep_base:
            sleep_extra = after_publish_sleep_base * 0.1
            sleep(after_publish_sleep_base + sleep_extra)

        # Run the cleanup procedure now
        cleanup_result = run_cleanup(
            clean_up_subscriptions,
            clean_up_topics_without_subscribers,
            clean_up_topics_with_max_retention_reached,
        )

        # We enter and check the assertions here only if we were to clean up subscriptions
        # as otherwise the subscription will be still around.
        if clean_up_subscriptions:

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

            # This topic was cleaned up based on the fact that it had no subscribers,
            # which left no messages in the topic at all. That means that there must have been
            # no messages with a max. retention time left which in turn means that we do not
            # expect this topic to be among ones that still contained such messages
            # when the cleanup procedure went on to clean up topics based on max. retention time.
            for item in cleanup_result.topics_with_max_retention_reached:
                if item.name == topic_name:
                    self.fail('Topic `{}` should not be among `{}` (topics_cleaned_up)'.format(
                        topic_name, cleanup_result.topics_with_max_retention_reached))

        elif clean_up_topics_with_max_retention_reached:

            # Confirm that the environment variable was not used
            self.assertFalse(cleanup_result.has_env_delta)

            # We expect for no subscriptions to have been cleaned up in this if branch
            self.assertListEqual(cleanup_result.topics_without_subscribers, [])

            # Because its name is unique, there should be only one topic that was cleaned up
            self.assertEqual(len(cleanup_result.topics_cleaned_up), 1)
            self.assertEqual(len(cleanup_result.topics_with_max_retention_reached), 1)

            # This is our topic that was cleaned up
            topic_from_cleaned_up_list = cleanup_result.topics_cleaned_up[0]
            topic_based_on_max_retention_reached = cleanup_result.topics_with_max_retention_reached[0]

            # These two objects should be the same
            self.assertIs(topic_from_cleaned_up_list, topic_based_on_max_retention_reached)

            # Let's use a shorter name
            topic_ctx = cleanup_result.topics_cleaned_up[0]

            # These must be equal
            self.assertTrue(topic_ctx.name, topic_name)
            self.assertEqual(topic_ctx.limit_retention, limit_retention)
            self.assertEqual(topic_ctx.len_messages, len(messages_published))

            # Messages received are going to be a list of Bunch objects in an unspecified order.
            # We need to convert them to a simple list of sorted message IDs.
            cleaned_up_msg_id_list = [elem['pub_msg_id'] for elem in topic_ctx.messages]
            cleaned_up_msg_id_list.sort()

            self.assertListEqual(messages_published, cleaned_up_msg_id_list)

# ################################################################################################################################

    def test_cleanup_old_subscriptions_no_sub_keys(self) -> 'None':

        # Indicate after a passage of how many seconds we will consider a subscribers as gone,
        # that is, after how many seconds since its last interaction time it will be deleted.
        env_delta = 1

        # Create a new topic for this test with a unique prefix,
        # which will ensure that there are no other subscriptions for it.
        now = datetime.utcnow().isoformat()
        prefix = f'{test_topic_prefix}{now}/'
        out = self.create_pubsub_topic(topic_prefix=prefix)
        topic_name = out['name']

        # Export a variable with delta as required by the underlying cleanup implementation
        os.environ[delta_environ_key] = str(env_delta)

        # Sleep for that many seconds to make sure that we are the only pub/sub participant
        # currently using the system. This will allow us to reliably check below
        # that there were no sub_keys used during the delta time since we created the topic
        # and when the cleanup procedure ran.
        sleep_extra = env_delta * 0.1
        sleep(env_delta + sleep_extra)

        # Run the cleanup procedure now
        cleanup_result = run_cleanup(
            clean_up_subscriptions = True,
            clean_up_topics_without_subscribers = True,
            clean_up_topics_with_max_retention_reached = True,
        )

        # We expect for the environment variable to have been taken into account
        self.assertEqual(cleanup_result.max_limit_sub_inactivity, env_delta)

        # We do not know how topics will have been cleaned up
        # because this test may be part of a bigger test suite
        # with other topics, subscribers and message publications.
        # However, because we do not have any subscription to that very topic,
        # it means that we do not expect to find it in the list of topics cleaned up
        # and this is what we are testing below, i.e. that it was not cleaned up.

        for item in cleanup_result.topics_cleaned_up:
            if item.name == topic_name:
                self.fail('Topic `{}` should not be among `{}` (topics_cleaned_up)'.format(
                    topic_name, cleanup_result.topics_cleaned_up))

        for item in cleanup_result.topics_without_subscribers:
            if item.name == topic_name:
                self.fail('Topic `{}` should not be among `{}` (topics_cleaned_up)'.format(
                    topic_name, cleanup_result.topics_without_subscribers))

        # We are sure that have been the only potential user of the pub/sub system
        # while the test was running and, because we did not publish anything,
        # nor did we subscribe to anything, we can be sure that there have been
        # no subscriptions found when the cleanup procedure ran.
        self.assertEqual(len(cleanup_result.found_sk_list), 0)
        self.assertListEqual(cleanup_result.found_sk_list, [])

# ################################################################################################################################

    def test_cleanup_old_subscriptions_one_sub_key_with_env_delta_default_topic(self):

        # In this test, we explicitly specify a seconds delta to clean up messages by.
        env_delta = 1

        # Create a new topic for this test
        out = self.create_pubsub_topic()
        topic_name = out['name']

        # Run the actual test
        self._run_cleanup_old_pubsub_one_sub_key(
            topic_name,
            env_delta=env_delta,
            limit_retention=None,
            limit_sub_inactivity=None,
        )

# ################################################################################################################################

    def test_cleanup_old_subscriptions_one_sub_key_with_env_delta_new_topic(self):

        # In this test, we explicitly specify a seconds delta to clean up messages by.
        # I.e. even if we use a new test topic below, the delta is given on input too.
        env_delta = 1

        # Create a new topic for this test
        out = self.create_pubsub_topic()
        topic_name = out['name']

        # Run the actual test
        self._run_cleanup_old_pubsub_one_sub_key(
            topic_name,
            env_delta=env_delta,
            limit_retention=None,
            limit_sub_inactivity=None,
        )

# ################################################################################################################################

    def test_cleanup_old_subscriptions_one_sub_key_no_env_delta(self):

        # We explcitly request that inactive subscriptions should be deleted after that many seconds
        limit_sub_inactivity = 1

        # Create a new topic for this test
        out = self.create_pubsub_topic()
        topic_name = out['name']

        # Run the actual test
        self._run_cleanup_old_pubsub_one_sub_key(
            topic_name,
            env_delta=None,
            limit_retention=None,
            limit_sub_inactivity=limit_sub_inactivity,
        )

# ################################################################################################################################

    def test_cleanup_old_subscriptions_one_sub_key_env_delta_overrides_topic_delta(self):

        # In this test, we specify a short delta in the environment and we expect
        # that it will override the explicit inactivity limit configured for a new topic.
        # In other words, the environment variable has priority over what the topic has configured
        env_delta = 1

        # We explcitly request that inactive subscriptions should be deleted after that many seconds
        limit_sub_inactivity = 123456789

        # Create a new topic for this test
        out = self.create_pubsub_topic()
        topic_name = out['name']

        # Run the actual test
        self._run_cleanup_old_pubsub_one_sub_key(
            topic_name,
            env_delta=env_delta,
            limit_retention=None,
            limit_sub_inactivity=limit_sub_inactivity,
        )

# ################################################################################################################################

    def test_cleanup_max_topic_retention_exceeded(self) -> 'None':

        # Messages without subscribers will be eligible for deletion from topics after that many seconds
        limit_retention = 1

        # Create a new topic for this test with a unique prefix,
        # which will ensure that there are no other subscriptions for it.
        now = datetime.utcnow().isoformat()
        prefix = f'{test_topic_prefix}retention/{now}/'
        out = self.create_pubsub_topic(topic_prefix=prefix, limit_retention=limit_retention)
        topic_name = out['name']

        # Run the actual test
        self._run_cleanup_old_pubsub_one_sub_key(
            topic_name,
            env_delta=None,
            limit_retention=limit_retention,
            limit_sub_inactivity=None,
            clean_up_subscriptions = False,
            clean_up_topics_without_subscribers = False,
            clean_up_topics_with_max_retention_reached = True,
        )

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
