# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# PyPI
import pytest # type: ignore[reportMissingImports]

# local
from base import BasePushTestCase
from config import is_endpoint_active

# ################################################################################################################################
# ################################################################################################################################

_skip_user_created = pytest.mark.skipif( # type: ignore[reportUntypedFunctionDecorator]
    not is_endpoint_active('iam.user.created'),
    reason='iam.user.created not in active endpoint set',
)

_skip_user_deleted = pytest.mark.skipif( # type: ignore[reportUntypedFunctionDecorator]
    not is_endpoint_active('iam.user.deleted'),
    reason='iam.user.deleted not in active endpoint set',
)

_skip_role_assigned = pytest.mark.skipif( # type: ignore[reportUntypedFunctionDecorator]
    not is_endpoint_active('iam.role.assigned'),
    reason='iam.role.assigned not in active endpoint set',
)

_skip_password_changed = pytest.mark.skipif( # type: ignore[reportUntypedFunctionDecorator]
    not is_endpoint_active('iam.password.changed'),
    reason='iam.password.changed not in active endpoint set',
)

_skip_login_failed = pytest.mark.skipif( # type: ignore[reportUntypedFunctionDecorator]
    not is_endpoint_active('iam.login.failed'),
    reason='iam.login.failed not in active endpoint set',
)

# ################################################################################################################################
# ################################################################################################################################

class TestIAMPushDelivery(BasePushTestCase):
    """ Push delivery tests for IAM domain events.
    """

    @_skip_user_created # type: ignore[reportUntypedFunctionDecorator]
    def test_user_created_pushed(self) -> 'None':
        """ A message published to iam.user.created must be pushed to its HTTP receiver.
        """
        topic_name = 'iam.user.created'
        data = {'user_id': 'usr-001', 'username': 'john.doe', 'event': 'created'}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        messages = self.poll_for_messages(topic_name, expected_count=1)

        message_count = len(messages)
        self.assertEqual(message_count, 1)

        received_data = self.extract_push_data(messages[0])
        self.assertEqual(received_data['user_id'], 'usr-001')

# ################################################################################################################################

    @_skip_user_deleted # type: ignore[reportUntypedFunctionDecorator]
    def test_user_deleted_pushed(self) -> 'None':
        """ A message published to iam.user.deleted must be pushed to its HTTP receiver.
        """
        topic_name = 'iam.user.deleted'
        data = {'user_id': 'usr-002', 'reason': 'account_closed'}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        messages = self.poll_for_messages(topic_name, expected_count=1)

        message_count = len(messages)
        self.assertEqual(message_count, 1)

        received_data = self.extract_push_data(messages[0])
        self.assertEqual(received_data['user_id'], 'usr-002')

# ################################################################################################################################

    @_skip_role_assigned # type: ignore[reportUntypedFunctionDecorator]
    def test_role_assigned_pushed(self) -> 'None':
        """ A message published to iam.role.assigned must be pushed to its HTTP receiver.
        """
        topic_name = 'iam.role.assigned'
        data = {'user_id': 'usr-003', 'role': 'admin', 'assigned_by': 'system'}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        messages = self.poll_for_messages(topic_name, expected_count=1)

        message_count = len(messages)
        self.assertEqual(message_count, 1)

        received_data = self.extract_push_data(messages[0])
        self.assertEqual(received_data['user_id'], 'usr-003')

# ################################################################################################################################

    @_skip_password_changed # type: ignore[reportUntypedFunctionDecorator]
    def test_password_changed_pushed(self) -> 'None':
        """ A message published to iam.password.changed must be pushed to its HTTP receiver.
        """
        topic_name = 'iam.password.changed'
        data = {'user_id': 'usr-004', 'changed_by': 'self'}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        messages = self.poll_for_messages(topic_name, expected_count=1)

        message_count = len(messages)
        self.assertEqual(message_count, 1)

        received_data = self.extract_push_data(messages[0])
        self.assertEqual(received_data['user_id'], 'usr-004')

# ################################################################################################################################

    @_skip_login_failed # type: ignore[reportUntypedFunctionDecorator]
    def test_login_failed_pushed(self) -> 'None':
        """ A message published to iam.login.failed must be pushed to its HTTP receiver.
        """
        topic_name = 'iam.login.failed'
        data = {'user_id': 'usr-005', 'ip_address': '192.168.1.100', 'attempt': 3}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        messages = self.poll_for_messages(topic_name, expected_count=1)

        message_count = len(messages)
        self.assertEqual(message_count, 1)

        received_data = self.extract_push_data(messages[0])
        self.assertEqual(received_data['user_id'], 'usr-005')

# ################################################################################################################################

    @_skip_user_created # type: ignore[reportUntypedFunctionDecorator]
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
            self.assertEqual(message_count, 1)

# ################################################################################################################################

    @_skip_user_created # type: ignore[reportUntypedFunctionDecorator]
    def test_iam_pushed_metadata_present(self) -> 'None':
        """ A pushed message must contain pub/sub metadata fields from the
        raw Redis stream entry.
        """
        topic_name = 'iam.user.created'
        data = {'user_id': 'usr-meta-001', 'event': 'metadata_check'}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        messages = self.poll_for_messages(topic_name, expected_count=1)

        message_count = len(messages)
        self.assertEqual(message_count, 1)

        # The pushed message is a raw Redis stream entry and must contain
        # the standard metadata fields alongside the data payload ..
        first_message = messages[0]

        self.assertIn('data', first_message)
        self.assertIn('msg_id', first_message)
        self.assertIn('pub_time_iso', first_message)
        self.assertIn('topic_name', first_message)

        # .. the topic_name field must match what we published to ..
        self.assertEqual(first_message['topic_name'], 'iam.user.created')

        # .. and the data field must contain our original payload.
        received_data = self.extract_push_data(first_message)
        self.assertEqual(received_data['user_id'], 'usr-meta-001')

# ################################################################################################################################

    @_skip_user_created # type: ignore[reportUntypedFunctionDecorator]
    def test_publish_response_fields(self) -> 'None':
        """ The publish response must contain msg_id and status fields
        as documented in the REST API specification.
        """
        topic_name = 'iam.user.created'
        data = {'user_id': 'usr-resp-001', 'event': 'response_check'}

        result = self.publish(topic_name, data)

        # The response must contain all documented fields ..
        self.assertIn('is_ok', result)
        self.assertTrue(result['is_ok'])

        self.assertIn('msg_id', result)
        msg_id = result['msg_id']
        msg_id_length = len(msg_id)
        self.assertGreater(msg_id_length, 0)

        self.assertIn('status', result)

# ################################################################################################################################
# ################################################################################################################################
