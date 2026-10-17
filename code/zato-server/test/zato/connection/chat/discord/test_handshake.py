# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The gateway handshake - its completion, the readiness gate in front of every call and the loop that repeats
# the handshake until READY arrives.

# stdlib
from time import monotonic
from unittest import main

# Zato
from zato.common.api import Discord

# Live Discord
from live_discord.simulator import Close_Code_Invalid_Token

# Test support
from test.zato.connection.chat.discord.common import DiscordTestCase, Handshake_Pause, Timeout, Token, wait_until

# ################################################################################################################################
# ################################################################################################################################

class HandshakeTestCase(DiscordTestCase):

    def test_the_handshake_identifies_the_bot_and_receives_ready(self) -> 'None':

        client = self.new_client()
        client.start_handshake()

        client._wait_until_ready()

        identify = self.simulator.identifies[0]
        self.assertEqual(identify.token, Token)
        self.assertEqual(identify.intents, Discord.Default.Intents)
        self.assertEqual(identify.properties['os'], 'zato')
        self.assertTrue(identify.is_ready_sent)

        self.assertEqual(self.simulator.gateway_info_calls, 1)
        self.assertTrue(client.ready.is_set())
        self.assertIsNone(client.gateway_socket)

# ################################################################################################################################

    def test_a_call_waits_until_ready_arrives(self) -> 'None':

        self.simulator.ready_delay = 1.0

        client = self.new_client()
        client.start_handshake()

        start = monotonic()
        response = client.send('after READY')
        elapsed = monotonic() - start

        self.assertGreaterEqual(elapsed, 1.0)
        self.assertEqual(response['content'], 'after READY')
        self.assertEqual(len(self.simulator.messages), 1)

# ################################################################################################################################

    def test_a_call_times_out_when_ready_does_not_arrive(self) -> 'None':

        self.simulator.never_send_ready = True

        client = self.new_client()
        client.start_handshake()

        start = monotonic()
        with self.assertRaises(Exception) as ctx:
            _ = client.send('never sent')
        elapsed = monotonic() - start

        self.assertGreaterEqual(elapsed, Timeout)
        self.assertIn(f'not ready after {Timeout}s', str(ctx.exception))
        self.assertEqual(self.simulator.messages, [])

# ################################################################################################################################

    def test_the_loop_continues_through_close_codes_until_ready(self) -> 'None':

        self.simulator.identify_close_codes = [Close_Code_Invalid_Token, 4014]

        client = self.new_client()
        client.start_handshake()

        response = client.send('after retries')
        self.assertEqual(response['content'], 'after retries')

        identifies = self.simulator.identifies
        self.assertEqual(len(identifies), 3)
        self.assertEqual(identifies[0].close_code, Close_Code_Invalid_Token)
        self.assertEqual(identifies[1].close_code, 4014)
        self.assertEqual(identifies[2].close_code, 0)
        self.assertTrue(identifies[2].is_ready_sent)

        # Each failed attempt asked the REST API for the gateway anew
        self.assertEqual(self.simulator.gateway_info_calls, 3)

# ################################################################################################################################

    def test_the_loop_continues_through_rest_failures_until_ready(self) -> 'None':

        # The simulator refuses the token until it is changed back
        self.simulator.token = 'another-token'

        client = self.new_client()
        client.start_handshake()

        wait_until(lambda: '401' in client.last_error, 'the REST API refuses the token')

        self.assertEqual(self.simulator.identifies, [])

        self.simulator.token = Token

        response = client.send('after the token is accepted')
        self.assertEqual(response['content'], 'after the token is accepted')
        self.assertEqual(len(self.simulator.identifies), 1)

# ################################################################################################################################

    def test_the_handshake_waits_for_the_identify_limit_to_reset(self) -> 'None':

        self.simulator.session_start_remaining = 0
        self.simulator.session_start_reset_after_ms = 700

        client = self.new_client()
        client.start_handshake()

        start = monotonic()
        client._wait_until_ready()
        elapsed = monotonic() - start

        self.assertGreaterEqual(elapsed, 0.7)
        self.assertEqual(len(self.simulator.identifies), 1)

# ################################################################################################################################

    def test_attempts_are_paused_between_failures(self) -> 'None':

        self.simulator.identify_close_codes = [Close_Code_Invalid_Token]

        client = self.new_client()
        client.start_handshake()

        identifies = self.simulator.identifies
        wait_until(lambda: len(identifies) >= 2, 'the second IDENTIFY arrives')
        pause = identifies[1].received_at - identifies[0].received_at

        self.assertGreaterEqual(pause, Handshake_Pause)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
