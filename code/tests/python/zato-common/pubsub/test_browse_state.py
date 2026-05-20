# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import unittest

# Zato
from zato.common.pubsub.redis_backend import ModuleCtx

# This module
from test_fetch import BaseFetchTestCase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist # noqa: F401

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class TestBrowsePending(BaseFetchTestCase):
    """ Tests for browse_messages with state='pending'.
    """

    def test_pending_shows_only_undelivered(self) -> 'None':

        # Subscribe ..
        sub_key = f'sub.browse.pending.undelivered.{self._run_id}'
        self.subscribe(sub_key)

        # .. publish 3 messages ..
        for idx in range(3):
            _ = self.backend.publish(self.topic_name, f'msg-{idx}')
            _ = self.get_data_ref_from_stream()

        # .. fetch all (puts them in PEL) ..
        messages = self.backend.fetch_messages(sub_key)
        logger.info('fetch_messages -> %d messages fetched', len(messages))
        self.assertEqual(len(messages), 3)

        # .. ack one message (removes from PEL) ..
        stream_key = f'{ModuleCtx.Stream_Prefix}{self.topic_name}'
        first_message = messages[0]
        self.backend.ack_message(stream_key, sub_key, first_message['_redis_message_id'], first_message['_data_ref'])
        logger.info('ack_message -> redis_id:%s', first_message['_redis_message_id'])

        # .. browse pending should return only the 2 unacked messages.
        result, next_cursor = self.backend.browse_messages(self.topic_name, sub_key=sub_key, state='pending')
        logger.info('browse_messages(pending) -> %d entries, next_cursor:%s', len(result), next_cursor)
        self.assertEqual(len(result), 2)

# ################################################################################################################################

    def test_pending_empty_after_all_acked(self) -> 'None':

        # Subscribe ..
        sub_key = f'sub.browse.pending.all_acked.{self._run_id}'
        self.subscribe(sub_key)

        # .. publish 2 messages ..
        for idx in range(2):
            _ = self.backend.publish(self.topic_name, f'msg-{idx}')
            _ = self.get_data_ref_from_stream()

        # .. fetch all (puts them in PEL) ..
        messages = self.backend.fetch_messages(sub_key)
        logger.info('fetch_messages -> %d messages fetched', len(messages))
        self.assertEqual(len(messages), 2)

        # .. ack all messages ..
        stream_key = f'{ModuleCtx.Stream_Prefix}{self.topic_name}'
        for message in messages:
            self.backend.ack_message(stream_key, sub_key, message['_redis_message_id'], message['_data_ref'])
            logger.info('ack_message -> redis_id:%s', message['_redis_message_id'])

        # .. browse pending should return 0.
        result, next_cursor = self.backend.browse_messages(self.topic_name, sub_key=sub_key, state='pending')
        logger.info('browse_messages(pending) -> %d entries, next_cursor:%s', len(result), next_cursor)
        self.assertEqual(len(result), 0)

# ################################################################################################################################

    def test_pending_pagination(self) -> 'None':

        # Subscribe ..
        sub_key = f'sub.browse.pending.pagination.{self._run_id}'
        self.subscribe(sub_key)

        # .. publish 5 messages ..
        for idx in range(5):
            _ = self.backend.publish(self.topic_name, f'msg-{idx}')
            _ = self.get_data_ref_from_stream()

        # .. fetch all (puts them in PEL) ..
        messages = self.backend.fetch_messages(sub_key)
        logger.info('fetch_messages -> %d messages fetched', len(messages))
        self.assertEqual(len(messages), 5)

        # .. browse first page with page_size=2 ..
        result, next_cursor = self.backend.browse_messages(
            self.topic_name, sub_key=sub_key, state='pending', page_size=2)
        logger.info('browse_messages(pending, page_size=2) -> %d entries, next_cursor:%s', len(result), next_cursor)
        self.assertEqual(len(result), 2)
        self.assertTrue(next_cursor)

        # .. browse from next_cursor should return the next 2.
        result2, next_cursor2 = self.backend.browse_messages(
            self.topic_name, sub_key=sub_key, state='pending', cursor=next_cursor, page_size=2)
        logger.info('browse_messages(pending, cursor=%s, page_size=2) -> %d entries, next_cursor:%s',
            next_cursor, len(result2), next_cursor2)
        self.assertEqual(len(result2), 2)
        self.assertTrue(next_cursor2)

        # .. browse from next_cursor2 should return the last entry.
        result3, next_cursor3 = self.backend.browse_messages(
            self.topic_name, sub_key=sub_key, state='pending', cursor=next_cursor2, page_size=2)
        logger.info('browse_messages(pending, cursor=%s, page_size=2) -> %d entries, next_cursor:%s',
            next_cursor2, len(result3), next_cursor3)
        self.assertEqual(len(result3), 1)
        self.assertEqual(next_cursor3, '')

# ################################################################################################################################
# ################################################################################################################################

class TestBrowseAll(BaseFetchTestCase):
    """ Tests for browse_messages with state='all'.
    """

    def test_all_shows_everything(self) -> 'None':

        # Subscribe ..
        sub_key = f'sub.browse.all.everything.{self._run_id}'
        self.subscribe(sub_key)

        # .. publish 3 messages ..
        for idx in range(3):
            _ = self.backend.publish(self.topic_name, f'msg-{idx}')
            _ = self.get_data_ref_from_stream()

        # .. fetch all and ack one ..
        messages = self.backend.fetch_messages(sub_key)
        logger.info('fetch_messages -> %d messages fetched', len(messages))
        self.assertEqual(len(messages), 3)

        stream_key = f'{ModuleCtx.Stream_Prefix}{self.topic_name}'
        first_message = messages[0]
        self.backend.ack_message(stream_key, sub_key, first_message['_redis_message_id'], first_message['_data_ref'])
        logger.info('ack_message -> redis_id:%s', first_message['_redis_message_id'])

        # .. browse with state='all' should return all 3 regardless of ack status.
        result, next_cursor = self.backend.browse_messages(self.topic_name, sub_key=sub_key, state='all')
        logger.info('browse_messages(all) -> %d entries, next_cursor:%s', len(result), next_cursor)
        self.assertEqual(len(result), 3)

# ################################################################################################################################

    def test_all_pagination(self) -> 'None':

        # Subscribe ..
        sub_key = f'sub.browse.all.pagination.{self._run_id}'
        self.subscribe(sub_key)

        # .. publish 5 messages ..
        for idx in range(5):
            _ = self.backend.publish(self.topic_name, f'msg-{idx}')
            _ = self.get_data_ref_from_stream()

        # .. browse first page with page_size=3 ..
        result, next_cursor = self.backend.browse_messages(
            self.topic_name, sub_key=sub_key, state='all', page_size=3)
        logger.info('browse_messages(all, page_size=3) -> %d entries, next_cursor:%s', len(result), next_cursor)
        self.assertEqual(len(result), 3)
        self.assertTrue(next_cursor)

        # .. browse from next_cursor should return the remaining 2.
        result2, next_cursor2 = self.backend.browse_messages(
            self.topic_name, sub_key=sub_key, state='all', cursor=next_cursor, page_size=3)
        logger.info('browse_messages(all, cursor=%s, page_size=3) -> %d entries, next_cursor:%s',
            next_cursor, len(result2), next_cursor2)
        self.assertEqual(len(result2), 2)
        self.assertEqual(next_cursor2, '')

# ################################################################################################################################
# ################################################################################################################################

class TestBrowseDelivered(BaseFetchTestCase):
    """ Tests for browse_messages with state='delivered'.
    """

    def test_delivered_shows_only_acked(self) -> 'None':

        # Subscribe ..
        sub_key = f'sub.browse.delivered.acked.{self._run_id}'
        self.subscribe(sub_key)

        # .. publish 3 messages ..
        for idx in range(3):
            _ = self.backend.publish(self.topic_name, f'msg-{idx}')
            _ = self.get_data_ref_from_stream()

        # .. fetch all and ack one ..
        messages = self.backend.fetch_messages(sub_key)
        logger.info('fetch_messages -> %d messages fetched', len(messages))
        self.assertEqual(len(messages), 3)

        stream_key = f'{ModuleCtx.Stream_Prefix}{self.topic_name}'
        first_message = messages[0]
        self.backend.ack_message(stream_key, sub_key, first_message['_redis_message_id'], first_message['_data_ref'])
        logger.info('ack_message -> redis_id:%s', first_message['_redis_message_id'])

        # .. browse with state='delivered' should return only the acked entry.
        result, next_cursor = self.backend.browse_messages(self.topic_name, sub_key=sub_key, state='delivered')
        logger.info('browse_messages(delivered) -> %d entries, next_cursor:%s', len(result), next_cursor)
        self.assertEqual(len(result), 1)

# ################################################################################################################################

    def test_delivered_empty_when_nothing_acked(self) -> 'None':

        # Subscribe ..
        sub_key = f'sub.browse.delivered.none_acked.{self._run_id}'
        self.subscribe(sub_key)

        # .. publish 3 messages ..
        for idx in range(3):
            _ = self.backend.publish(self.topic_name, f'msg-{idx}')
            _ = self.get_data_ref_from_stream()

        # .. fetch all (puts in PEL) but do not ack ..
        messages = self.backend.fetch_messages(sub_key)
        logger.info('fetch_messages -> %d messages fetched', len(messages))
        self.assertEqual(len(messages), 3)

        # .. browse with state='delivered' should return 0 (nothing acked).
        result, next_cursor = self.backend.browse_messages(self.topic_name, sub_key=sub_key, state='delivered')
        logger.info('browse_messages(delivered) -> %d entries, next_cursor:%s', len(result), next_cursor)
        self.assertEqual(len(result), 0)

# ################################################################################################################################
# ################################################################################################################################

class TestBrowseStateDispatch(BaseFetchTestCase):
    """ Tests for the state dispatch mechanism.
    """

    def test_unknown_state_raises(self) -> 'None':

        # Subscribe ..
        sub_key = f'sub.browse.dispatch.unknown.{self._run_id}'
        self.subscribe(sub_key)

        # .. browsing with an unknown state should raise KeyError.
        with self.assertRaises(KeyError):
            _ = self.backend.browse_messages(self.topic_name, sub_key=sub_key, state='nonexistent')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
