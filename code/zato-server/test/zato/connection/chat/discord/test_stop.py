# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Stopping a client while its handshake is in progress - at each point the handshake loop blocks in, the stop ends
# the loop at once and every caller waiting for READY is released with the stop reason.

# stdlib
from unittest import main

# gevent
from gevent import sleep, spawn

# Live Discord
from live_discord.simulator import Close_Code_Invalid_Token

# Test support
from test.zato.connection.chat.discord.common import DiscordTestCase, Handshake_Pause, wait_until

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.connection.chat.discord import DiscordClient

# ################################################################################################################################
# ################################################################################################################################

# The reason the wrapper gives when a connection is edited or deleted
Stop_Reason = 'was edited or deleted'

# How long a test observes the simulator after a stop, longer than the pause between attempts
Observation_Period = Handshake_Pause * 3

# ################################################################################################################################
# ################################################################################################################################

class StopTestCase(DiscordTestCase):

    def _assert_stopped(self, client:'DiscordClient') -> 'None':
        """ The client holds neither a greenlet nor a websocket and reports the stop reason to callers.
        """
        self.assertIsNone(client.handshake_greenlet)
        self.assertIsNone(client.gateway_socket)

        with self.assertRaises(Exception) as ctx:
            _ = client.send('after the stop')

        self.assertIn(Stop_Reason, str(ctx.exception))

# ################################################################################################################################

    def test_a_stop_while_waiting_for_ready_ends_the_handshake(self) -> 'None':

        self.simulator.never_send_ready = True

        client = self.new_client()
        client.start_handshake()

        wait_until(lambda: len(self.simulator.identifies) == 1, 'IDENTIFY arrives')
        self.assertIsNotNone(client.gateway_socket)

        client.stop(Stop_Reason)
        self._assert_stopped(client)

        # No new attempt follows the stop
        sleep(Observation_Period)
        self.assertEqual(len(self.simulator.identifies), 1)
        self.assertEqual(self.simulator.gateway_info_calls, 1)

# ################################################################################################################################

    def test_a_stop_during_the_pause_between_attempts_ends_the_loop(self) -> 'None':

        self.simulator.identify_close_codes = [Close_Code_Invalid_Token]

        client = self.new_client()
        client.start_handshake()

        # The first attempt fails and the loop sleeps before the next one ..
        wait_until(lambda: client.last_error != '', 'the first attempt fails')

        # .. and the stop lands in that sleep.
        client.stop(Stop_Reason)
        self._assert_stopped(client)

        sleep(Observation_Period)
        self.assertEqual(len(self.simulator.identifies), 1)

# ################################################################################################################################

    def test_a_stop_while_waiting_out_a_rate_limit_ends_the_loop(self) -> 'None':

        # Every gateway/bot call is rate-limited for longer than the test observes
        self.simulator.rate_limited_calls_left = 1000
        self.simulator.rate_limit_retry_after = Observation_Period

        client = self.new_client()
        client.start_handshake()

        wait_until(lambda: len(self.simulator.rejections) > 0, 'the first call is rate-limited')

        client.stop(Stop_Reason)
        self._assert_stopped(client)

        rejections_at_stop = len(self.simulator.rejections)

        sleep(Observation_Period * 2)
        self.assertEqual(len(self.simulator.rejections), rejections_at_stop)
        self.assertEqual(self.simulator.identifies, [])

# ################################################################################################################################

    def test_a_stop_while_waiting_for_the_identify_limit_ends_the_loop(self) -> 'None':

        self.simulator.session_start_remaining = 0
        self.simulator.session_start_reset_after_ms = int(Observation_Period * 1000)

        client = self.new_client()
        client.start_handshake()

        wait_until(lambda: self.simulator.gateway_info_calls == 1, 'the gateway address is read')

        client.stop(Stop_Reason)
        self._assert_stopped(client)

        sleep(Observation_Period * 2)
        self.assertEqual(self.simulator.identifies, [])

# ################################################################################################################################

    def test_a_stop_before_the_first_attempt_ends_the_loop(self) -> 'None':

        client = self.new_client()
        client.start_handshake()
        client.stop(Stop_Reason)

        self._assert_stopped(client)

        sleep(Observation_Period)
        self.assertEqual(self.simulator.identifies, [])

# ################################################################################################################################

    def test_callers_waiting_for_ready_are_released_with_the_stop_reason(self) -> 'None':

        self.simulator.never_send_ready = True

        client = self.new_client()
        client.start_handshake()

        # Two callers block in the readiness gate ..
        errors:'list[str]' = []

        def call() -> 'None':
            try:
                _ = client.send('while waiting')
            except Exception as e:
                errors.append(str(e))

        waiters = [spawn(call), spawn(call)]
        sleep(0.2)
        self.assertEqual(errors, [])

        # .. and the stop releases both at once, long before the timeout.
        client.stop(Stop_Reason)

        for waiter in waiters:
            waiter.join(1.0)

        self.assertEqual(len(errors), 2)
        for error in errors:
            self.assertIn(Stop_Reason, error)

        self.assertEqual(self.simulator.messages, [])

# ################################################################################################################################

    def test_a_stop_after_ready_refuses_further_calls(self) -> 'None':

        client = self.new_ready_client()
        _ = client.send('before the stop')

        client.stop(Stop_Reason)
        self._assert_stopped(client)

        self.assertEqual(len(self.simulator.messages), 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
