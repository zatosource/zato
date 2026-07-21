# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from unittest.mock import MagicMock

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class TestServicePublishKwargs(unittest.TestCase):
    """ Tests the Service.publish layer that separates payload kwargs from metadata kwargs
    before delegating to self.pubsub.publish.
    """

    def setUp(self) -> 'None':

        # Build a minimally wired Service instance ..
        self.service = Service.__new__(Service)
        self.service.cid = 'test-cid-1'

        # .. mock pubsub.publish to capture what it receives, keeping a direct
        # .. reference to the mock so assertions are made through a mock-typed object.
        self.pubsub_mock = MagicMock()
        self.service.pubsub = self.pubsub_mock

# ################################################################################################################################

    def test_inline_kwargs_become_payload(self) -> 'None':
        """ When inline kwargs are used as payload via Service.publish,
        they are collected into a dict payload.
        """
        _ = self.service.publish('test.topic', order_id=123, status='pending')

        call_args = self.pubsub_mock.publish.call_args
        received_data = call_args[0][1]

        self.assertEqual(received_data, {'order_id': 123, 'status': 'pending'})

# ################################################################################################################################

    def test_inline_kwargs_with_metadata(self) -> 'None':
        """ When metadata kwargs (like priority) are passed alongside
        payload kwargs, only the payload keys reach the subscriber.
        """

        # Call publish with a mix of payload and metadata kwargs ..
        _ = self.service.publish('test.topic', order_id=123, priority=5)

        # .. verify pubsub.publish received the payload dict
        # .. with only the non-meta keys ..
        call_args = self.pubsub_mock.publish.call_args
        received_data = call_args[0][1]

        self.assertEqual(received_data, {'order_id': 123})

        # .. and priority was passed as a kwarg to pubsub.publish,
        # .. not included in the payload.
        received_kwargs = call_args[1]
        self.assertEqual(received_kwargs['priority'], 5)

        # .. the service's own CID was forwarded too.
        self.assertEqual(received_kwargs['cid'], 'test-cid-1')

# ################################################################################################################################

    def test_explicit_cid_is_kept(self) -> 'None':
        """ A CID given by the caller is not overwritten with the service's own CID.
        """
        _ = self.service.publish('test.topic', 'data', cid='caller-cid-1')

        received_kwargs = self.pubsub_mock.publish.call_args[1]

        self.assertEqual(received_kwargs['cid'], 'caller-cid-1')

# ################################################################################################################################

    def test_explicit_data_leaves_kwargs_intact(self) -> 'None':
        """ When explicit data is given, metadata kwargs are forwarded unchanged
        and nothing is folded into the payload.
        """
        _ = self.service.publish('test.topic', 'explicit data', priority=7, expiration=3600)

        call_args = self.pubsub_mock.publish.call_args

        self.assertEqual(call_args[0][0], 'test.topic')
        self.assertEqual(call_args[0][1], 'explicit data')

        received_kwargs = call_args[1]

        self.assertEqual(received_kwargs['priority'], 7)
        self.assertEqual(received_kwargs['expiration'], 3600)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
