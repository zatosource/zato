# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from unittest import TestCase
from unittest.mock import patch

# Zato
from zato.common.hl7.mllp.settings import (
    Default_Idle_Timeout,
    Default_Max_Message_Size,
    describe_bounds_violations,
    listener_config_from_bounds,
    ListenerConfig,
)
from zato.server.generic.api.channel_hl7_mllp import get_listener_bounds

# ################################################################################################################################
# ################################################################################################################################

# The bounds of a server whose environment narrows the listener below the defaults
_server_max_message_size = 1024 * 1024
_server_idle_timeout = 60.0

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

class TestTheBoundsAreTheServers(TestCase):
    """ The listener is built from the server's environment, so the bounds a channel is judged against
    are the ones the server reports, whatever the environment of the process that saves the channel.
    """

    def test_the_server_reports_the_bounds_of_its_own_environment(self) -> 'None':
        """ What the server reports is what from_env reads in its process - a lower size and a shorter
        idle timeout than the defaults when the environment says so.
        """
        environ = {'Zato_HL7_MLLP_Max_Msg_Size': str(_server_max_message_size), 'Zato_HL7_MLLP_Idle_Timeout': str(_server_idle_timeout)}

        with patch.dict(os.environ, environ, clear=False):
            bounds = get_listener_bounds()

        self.assertEqual(bounds['max_message_size'], _server_max_message_size)
        self.assertEqual(bounds['idle_timeout'], _server_idle_timeout)

# ################################################################################################################################

    def test_a_channel_the_server_would_cap_is_refused_where_it_is_saved(self) -> 'None':
        """ A channel within the defaults of the saving process, yet above what the server reports,
        is refused with the server's bounds named, and never silently narrowed at runtime instead.
        """
        listener_config = listener_config_from_bounds({
            'max_message_size': _server_max_message_size,
            'idle_timeout': _server_idle_timeout,
        })

        violations = describe_bounds_violations(_server_max_message_size * 2, _server_idle_timeout * 2, listener_config)

        self.assertEqual(violations, [
            f'Maximum message size {_server_max_message_size * 2} is above the {_server_max_message_size} bytes the listener allows',
            f'Idle timeout {_server_idle_timeout * 2} is above the {_server_idle_timeout} seconds the listener allows',
        ])

# ################################################################################################################################
# ################################################################################################################################
