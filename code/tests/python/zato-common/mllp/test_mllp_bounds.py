# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.common.hl7.mllp.settings import (
    Default_Idle_Timeout,
    Default_Max_Message_Size,
    describe_bounds_violations,
    ListenerConfig,
)

# ################################################################################################################################
# ################################################################################################################################

class TestBoundsAreRefusedWhereTheyAreEntered(TestCase):
    """ A channel's values tune what the listener already allows, so one the listener will not
    honour is refused where it is saved rather than quietly capped once a message is on the wire.
    """

    def setUp(self) -> 'None':
        self.listener_config = ListenerConfig(
            max_message_size=Default_Max_Message_Size,
            idle_timeout=Default_Idle_Timeout,
        )

# ################################################################################################################################

    def test_a_channel_within_the_bounds_is_accepted(self) -> 'None':
        """ Nothing is said about a channel asking for less than the listener has.
        """
        violations = describe_bounds_violations(
            Default_Max_Message_Size // 2,
            Default_Idle_Timeout / 2,
            self.listener_config,
        )

        self.assertEqual(violations, [])

# ################################################################################################################################

    def test_a_channel_at_the_bounds_is_accepted(self) -> 'None':
        """ Asking for exactly what the listener has is asking for nothing extra.
        """
        violations = describe_bounds_violations(
            Default_Max_Message_Size,
            Default_Idle_Timeout,
            self.listener_config,
        )

        self.assertEqual(violations, [])

# ################################################################################################################################

    def test_a_larger_message_size_is_refused(self) -> 'None':
        """ A channel cannot give itself more room than the listener has.
        """
        violations = describe_bounds_violations(
            Default_Max_Message_Size + 1,
            Default_Idle_Timeout,
            self.listener_config,
        )

        self.assertEqual(len(violations), 1)
        self.assertIn('Maximum message size', violations[0])

# ################################################################################################################################

    def test_a_longer_idle_timeout_is_refused(self) -> 'None':
        """ Nor can it hold a connection open longer than the listener would.
        """
        violations = describe_bounds_violations(
            Default_Max_Message_Size,
            Default_Idle_Timeout + 1,
            self.listener_config,
        )

        self.assertEqual(len(violations), 1)
        self.assertIn('Idle timeout', violations[0])

# ################################################################################################################################

    def test_every_violation_is_reported_at_once(self) -> 'None':
        """ Both are named together, so a correction does not have to be made one at a time.
        """
        violations = describe_bounds_violations(
            Default_Max_Message_Size + 1,
            Default_Idle_Timeout + 1,
            self.listener_config,
        )

        self.assertEqual(len(violations), 2)

# ################################################################################################################################
# ################################################################################################################################
