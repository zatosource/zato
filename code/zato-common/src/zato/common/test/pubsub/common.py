# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import sleep
from json import loads
from logging import getLogger

# Zato
from zato.common import PUBSUB
from zato.common.pubsub import MSG_PREFIX, skip_to_external
from zato.common.test import rand_date_utc
from zato.common.test.config import TestConfig
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from unittest import TestCase
    TestCase = TestCase

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestingClass:

    def _subscribe(self, *args, **kwargs): # type: ignore
        raise NotImplementedError()

    def _unsubscribe(self, *args, **kwargs): # type: ignore
        raise NotImplementedError()

    def _publish(self, *args, **kwargs): # type: ignore
        raise NotImplementedError()

    def _receive(self, *args, **kwargs): # type: ignore
        raise NotImplementedError()

# ################################################################################################################################
# ################################################################################################################################

topic_name_shared = TestConfig.pubsub_topic_shared
topic_name_unique = TestConfig.pubsub_topic_name_unique

# ################################################################################################################################
# ################################################################################################################################

class FullPathTester:

    def __init__(self, test:'PubSubTestingClass', sub_before_publish:'bool', topic_name:'str'='') -> 'None':
        self.test = test
        self.sub_before_publish = sub_before_publish
        self.sub_after_publish = not self.sub_before_publish
        self.topic_name = topic_name
        self.sub_key = '<no-sk>'

        #
        # If we subscribe to a topic before we publish, we can use the shared topic,
        # because we are sure that our subscription is going to receive a message.
        #
        # However, if we subscribe after a publication, we need to use an exclusive topic.
        # If we were to use a shared one then, before we managed to subscribe, another subscriber
        # could have already received our own message that we have just published.
        #
        if self.sub_before_publish:
            self.topic_name = topic_name_shared
            self.needs_unique = False
            self.runner_name = 'Shared{}'.format(self.__class__.__name__)
        else:
            self.topic_name = topic_name or topic_name_unique
            self.needs_unique = True
            self.runner_name = 'Unique{}'.format(self.__class__.__name__)

# ################################################################################################################################

    def _run(self):

        # For type hints
        test = cast_('TestCase', self.test)

        # Always make sure that we are unsubscribed before the test runs
        self._unsubscribe('before')

        # We may potentially need to subscribe before the publication,
        # in which case we can subscribe to a shared
        if self.sub_before_publish:
            logger.info('Subscribing %s (1) (%s)', self.runner_name, self.sub_key)
            self.sub_key = self.test._subscribe(self.topic_name)

        # Publish the message
        data = cast_(str, rand_date_utc(True))
        logger.info('Publishing from %s (%s)', self.runner_name, self.sub_key)
        response_publish = self.test._publish(self.topic_name, data)

        # We expect to have a correct message ID on output
        msg_id = response_publish['msg_id'] # type: str
        test.assertTrue(msg_id.startswith(MSG_PREFIX.MSG_ID))

        # We may potentially need to subscribe after the publication
        if self.sub_after_publish:
            logger.info('Subscribing %s (2) (%s)', self.runner_name, self.sub_key)
            self.sub_key = self.test._subscribe(self.topic_name)
            logger.info('Received sub_key %s for %s (2) (after)', self.sub_key, self.runner_name)

        # Synchronization tasks run once in 0.5 second, which is why we wait a bit longer
        # to give them enough time to push the message to a delivery task.
        sleep_time = 3.6
        logger.info('%s sleeping for %ss (%s)', self.runner_name, sleep_time, self.sub_key)
        sleep(sleep_time)

        # Now, read the message back from our own queue - we can do it because
        # we know that we are subscribed already.
        logger.info('Receiving by %s (%s)', self.runner_name, self.sub_key)
        response_received = self.test._receive(self.topic_name)

        # Right now, this is a string because handle_PATCH in pubapi.py:TopicService serializes data to JSON,
        # which is why we need to load it here.
        if isinstance(response_received, str):
            response_received = loads(response_received)

        # We do not know how many messages we receive because it is possible
        # that there may be some left over from previous tests. However, we still
        # expect that the message that we have just published will be the first one
        # because messages are returned in the Last-In-First-Out order (LIFO).
        msg_received = response_received[0]

        test.assertEqual(msg_received['data'], data)
        test.assertEqual(msg_received['size'], len(data))
        test.assertEqual(msg_received['sub_key'], self.sub_key)
        test.assertEqual(msg_received['delivery_count'], 1)
        test.assertEqual(msg_received['priority'],   PUBSUB.PRIORITY.DEFAULT)
        test.assertEqual(msg_received['mime_type'],  PUBSUB.DEFAULT.MIME_TYPE)
        test.assertEqual(msg_received['expiration'], PUBSUB.DEFAULT.LimitMessageExpiry)
        test.assertEqual(msg_received['topic_name'], self.topic_name)

        # Dates will start with 2nnn, e.g. 2022, or 2107, depending on a particular field
        date_start = '2'

        test.assertTrue(msg_received['pub_time_iso'].startswith(date_start))
        test.assertTrue(msg_received['expiration_time_iso'].startswith(date_start))
        test.assertTrue(msg_received['recv_time_iso'].startswith(date_start))

        # Make sure that keys that are not supposed to be returned to external callers
        # are not returned in the message.
        for name in skip_to_external:
            if name in msg_received:
                test.fail(f'Key `{name}` should not be in message {msg_received}')

# ################################################################################################################################

    def _unsubscribe(self, action:'str') -> 'None':

        logger.info('Unsubscribing %s (%s) (%s)', self.runner_name, action, self.sub_key)

        self.test._unsubscribe(self.topic_name)

        # If this is a topic with a single subscriber that needs exclusive access,
        # we need to wait to make sure that we are truly unsubscribed
        if self.needs_unique:
            sleep_time = 1
            logger.info('%s sleeping for %ss (%s) (%s)', self.runner_name, sleep_time, action, self.sub_key)
            sleep(sleep_time)

# ################################################################################################################################

    def run(self):
        try:
            self._run()
        finally:
            # Always clean up after our tests
            self._unsubscribe('after')

# ################################################################################################################################
# ################################################################################################################################
