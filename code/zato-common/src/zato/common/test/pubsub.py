# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
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

    def __init__(self, test:'PubSubTestingClass', sub_before_publish:'bool') -> 'None':
        self.test = test
        self.sub_before_publish = sub_before_publish
        self.sub_after_publish = not self.sub_before_publish

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
        else:
            self.topic_name = topic_name_unique

# ################################################################################################################################

    def _run(self):

        # For type checking
        sub_key = None

        # Always make sure that we are unsubscribed before the test runs
        self._unsubscribe('before')

        # We may potentially need to subscribe before the publication,
        # in which case we can subscribe to a shared
        if self.sub_before_publish:
            logger.info('Subscribing FullPathTester (1)')
            sub_key = self.test._subscribe(self.topic_name)

        # Publish the message
        data = cast_(str, rand_date_utc(True))
        logger.info('Publishing from FullPathTester')
        response_publish = self.test._publish(self.topic_name, data)

        # We expect to have a correct message ID on output
        msg_id = response_publish['msg_id'] # type: str
        self.test.assertTrue(msg_id.startswith(MSG_PREFIX.MSG_ID))

        # We may potentially need to subscribe after the publication
        if self.sub_after_publish:
            logger.info('Subscribing FullPathTester (2)')
            sub_key = self.test._subscribe(self.topic_name)

        # Synchronization tasks run once in 0.5 second, which is why we wait a bit longer
        # to give them enough time to push the message to a delivery task.
        time.sleep(0.6)

        # Now, read the message back from our own queue - we can do it because
        # we know that we are subscribed already.
        logger.info('Receiving by FullPathTester')
        response_received = self.test._receive(self.topic_name)

        # Right now, this is a string because handle_PATCH in pubapi.py:TopicService serializes data to JSON,
        # which is why we need to load it here.
        if isinstance(response_received, str):
            response_received = loads(response_received)

        return

        # We do not know how many messages we receive because it is possible
        # that there may be some left over from previous tests. However, we still
        # expect that the message that we have just published will be the first one
        # because messages are returned in the Last-In-First-Out order (LIFO).
        msg_received = response_received[0]

        self.test.assertEqual(msg_received['data'], data)
        self.test.assertEqual(msg_received['size'], len(data))
        self.test.assertEqual(msg_received['sub_key'], sub_key)
        self.test.assertEqual(msg_received['delivery_count'], 1)
        self.test.assertEqual(msg_received['priority'],   PUBSUB.PRIORITY.DEFAULT)
        self.test.assertEqual(msg_received['mime_type'],  PUBSUB.DEFAULT.MIME_TYPE)
        self.test.assertEqual(msg_received['expiration'], PUBSUB.DEFAULT.EXPIRATION)
        self.test.assertEqual(msg_received['topic_name'], self.topic_name)

        # Dates will start with 2nnn, e.g. 2022, or 2107, depending on a particular field
        date_start = '2'

        self.test.assertTrue(msg_received['pub_time_iso'].startswith(date_start))
        self.test.assertTrue(msg_received['expiration_time_iso'].startswith(date_start))
        self.test.assertTrue(msg_received['recv_time_iso'].startswith(date_start))

        # Make sure that keys that are not supposed to be returned to external callers
        # are not returned in the message.
        for name in skip_to_external:
            if name in msg_received:
                self.test.fail(f'Key `{name}` should not be in message {msg_received}')

# ################################################################################################################################

    def _unsubscribe(self, action:'str') -> 'None':
        logger.info('Unsubscribing FullPathTester (%s)', action)
        self.test._unsubscribe(self.topic_name)

# ################################################################################################################################

    def run(self):
        try:
            self._run()
        finally:
            # Always clean up after our tests
            self._unsubscribe('after')

# ################################################################################################################################
# ################################################################################################################################
