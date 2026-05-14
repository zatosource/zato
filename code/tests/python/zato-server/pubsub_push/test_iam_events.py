# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# PyPI
import pytest

# local
from base import BasePubSubPushTestCase
from config import is_endpoint_active

# ################################################################################################################################
# ################################################################################################################################

_skip_user_created = pytest.mark.skipif(
    not is_endpoint_active('iam.user.created'),
    reason='iam.user.created not in active endpoint set',
)

_skip_user_deleted = pytest.mark.skipif(
    not is_endpoint_active('iam.user.deleted'),
    reason='iam.user.deleted not in active endpoint set',
)

_skip_role_assigned = pytest.mark.skipif(
    not is_endpoint_active('iam.role.assigned'),
    reason='iam.role.assigned not in active endpoint set',
)

_skip_password_changed = pytest.mark.skipif(
    not is_endpoint_active('iam.password.changed'),
    reason='iam.password.changed not in active endpoint set',
)

_skip_login_failed = pytest.mark.skipif(
    not is_endpoint_active('iam.login.failed'),
    reason='iam.login.failed not in active endpoint set',
)

# ################################################################################################################################
# ################################################################################################################################

class TestIAMPushDelivery(BasePubSubPushTestCase):
    """ Push delivery tests for IAM domain events.
    """

    @_skip_user_created
    def test_user_created_pushed(self) -> 'None':
        """ A message published to iam.user.created must be pushed to its HTTP receiver.
        """
        topic_name = 'iam.user.created'
        data = {'user_id': 'usr-001', 'username': 'john.doe', 'event': 'created'}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        messages = self.poll_for_messages(topic_name, expected_count=1)

        message_count = len(messages)
        self.assertGreaterEqual(message_count, 1)

        received_data = json.dumps(messages[0])
        self.assertIn('usr-001', received_data)

# ################################################################################################################################

    @_skip_user_deleted
    def test_user_deleted_pushed(self) -> 'None':
        """ A message published to iam.user.deleted must be pushed to its HTTP receiver.
        """
        topic_name = 'iam.user.deleted'
        data = {'user_id': 'usr-002', 'reason': 'account_closed'}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        messages = self.poll_for_messages(topic_name, expected_count=1)

        message_count = len(messages)
        self.assertGreaterEqual(message_count, 1)

        received_data = json.dumps(messages[0])
        self.assertIn('usr-002', received_data)

# ################################################################################################################################

    @_skip_role_assigned
    def test_role_assigned_pushed(self) -> 'None':
        """ A message published to iam.role.assigned must be pushed to its HTTP receiver.
        """
        topic_name = 'iam.role.assigned'
        data = {'user_id': 'usr-003', 'role': 'admin', 'assigned_by': 'system'}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        messages = self.poll_for_messages(topic_name, expected_count=1)

        message_count = len(messages)
        self.assertGreaterEqual(message_count, 1)

        received_data = json.dumps(messages[0])
        self.assertIn('usr-003', received_data)

# ################################################################################################################################

    @_skip_password_changed
    def test_password_changed_pushed(self) -> 'None':
        """ A message published to iam.password.changed must be pushed to its HTTP receiver.
        """
        topic_name = 'iam.password.changed'
        data = {'user_id': 'usr-004', 'changed_by': 'self'}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        messages = self.poll_for_messages(topic_name, expected_count=1)

        message_count = len(messages)
        self.assertGreaterEqual(message_count, 1)

        received_data = json.dumps(messages[0])
        self.assertIn('usr-004', received_data)

# ################################################################################################################################

    @_skip_login_failed
    def test_login_failed_pushed(self) -> 'None':
        """ A message published to iam.login.failed must be pushed to its HTTP receiver.
        """
        topic_name = 'iam.login.failed'
        data = {'user_id': 'usr-005', 'ip_address': '192.168.1.100', 'attempt': 3}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        messages = self.poll_for_messages(topic_name, expected_count=1)

        message_count = len(messages)
        self.assertGreaterEqual(message_count, 1)

        received_data = json.dumps(messages[0])
        self.assertIn('usr-005', received_data)

# ################################################################################################################################

    @_skip_user_created
    def test_multiple_iam_events_pushed(self) -> 'None':
        """ Publishing to multiple active IAM topics must deliver to each respective endpoint.
        """
        iam_topics = [
            'iam.user.created',
            'iam.user.deleted',
            'iam.role.assigned',
            'iam.password.changed',
            'iam.login.failed',
        ]

        active_iam_topics = []

        for topic_name in iam_topics:
            if is_endpoint_active(topic_name):
                active_iam_topics.append(topic_name)

        for topic_name in active_iam_topics:
            data = {'event_type': topic_name, 'batch_test': True}
            result = self.publish(topic_name, data)
            self.assertTrue(result['is_ok'])

        for topic_name in active_iam_topics:
            messages = self.poll_for_messages(topic_name, expected_count=1)

            message_count = len(messages)
            self.assertGreaterEqual(message_count, 1)

# ################################################################################################################################

    @_skip_user_created
    def test_iam_pushed_metadata_present(self) -> 'None':
        """ A pushed message must contain pub/sub metadata fields.
        """
        topic_name = 'iam.user.created'
        data = {'user_id': 'usr-meta-001', 'event': 'metadata_check'}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        messages = self.poll_for_messages(topic_name, expected_count=1)

        message_count = len(messages)
        self.assertGreaterEqual(message_count, 1)

        # The pushed message should contain the raw Redis stream fields
        first_message = messages[0]
        serialized = json.dumps(first_message)

        # The topic name should appear somewhere in the pushed payload
        self.assertIn('iam.user.created', serialized)

# ################################################################################################################################
# ################################################################################################################################
