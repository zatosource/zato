# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
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

topic_name = TestConfig.pubsub_topic_name_name

# ################################################################################################################################
# ################################################################################################################################

class FullPathTester:

    def __init__(self, test:'PubSubTestingClass', sub_before_publish:'bool') -> 'None':
        self.test = test
        self.sub_before_publish = sub_before_publish
        self.sub_after_publish = not self.sub_before_publish

# ################################################################################################################################

    def run(self):

        # For type checking
        sub_key = None

        # Always make sure that we are unsubscribed before the test runs
        logger.info('Unsubscribing FullPathTester')
        self.test._unsubscribe()

        # We may potentially need to subscribe before the publication
        if self.sub_before_publish:
            logger.info('Subscribing FullPathTester (1)')
            sub_key = self.test._subscribe()

        # Publish the message
        data = cast_(str, rand_date_utc(True))
        logger.info('Publishing from FullPathTester')
        response_publish = self.test._publish(data)

        # We expect to have a correct message ID on output
        msg_id = response_publish['msg_id'] # type: str
        self.test.assertTrue(msg_id.startswith(MSG_PREFIX.MSG_ID))

        # We may potentially need to subscribe after the publication
        if self.sub_after_publish:
            logger.info('Subscribing FullPathTester (2)')
            sub_key = self.test._subscribe()

        # Now, read the message back from our own queue - we can do it because
        # we know that we are subscribed already.
        logger.info('Receiving by FullPathTester')
        response_received = self.test._receive()

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
        self.test.assertEqual(msg_received['topic_name'], topic_name)

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
# ################################################################################################################################
