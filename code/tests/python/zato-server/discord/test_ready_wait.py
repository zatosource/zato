# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Test support
from conftest import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import DiscordSuite

# ################################################################################################################################
# ################################################################################################################################

Conn_Name = 'test.discord.ready-wait'

# ################################################################################################################################
# ################################################################################################################################

class TestReadyWait:

    def test_a_call_waits_for_ready_and_times_out_without_it(self, discord:'DiscordSuite') -> 'None':
        """ A connection whose gateway never sends READY is not usable - a call blocks for the timeout and reports it.
        """
        discord.simulator.never_send_ready = True

        _ = discord.create_connection(Conn_Name)
        _ = discord.wait_for_identifies(1)

        connection = discord.get_connection(Conn_Name)
        assert connection['is_ready'] is False, connection

        start = time.monotonic()
        response = discord.send('too early', conn_name=Conn_Name)
        elapsed = time.monotonic() - start

        assert response['is_ok'] is False, response
        assert f'not ready after {ModuleCtx.Timeout}s' in response['error'], response
        assert elapsed >= ModuleCtx.Timeout
        assert discord.simulator.messages == []

# ################################################################################################################################

    def test_the_handshake_is_repeated_until_ready_arrives(self, discord:'DiscordSuite') -> 'None':
        """ The loop keeps trying while the gateway closes each session and completes once the gateway lets it,
        after which calls go through.
        """
        discord.simulator.identify_close_codes.extend([4004, 4014])

        _ = discord.create_connection(Conn_Name)

        # The first two attempts fail ..
        identifies = discord.wait_for_identifies(2)
        assert identifies[0].close_code == 4004
        assert identifies[1].close_code == 4014

        # .. the third one succeeds ..
        _ = discord.wait_until_ready(Conn_Name)

        identifies = discord.wait_for_identifies(3)
        assert identifies[2].close_code == 0
        assert identifies[2].is_ready_sent is True

        # .. and the connection is usable.
        response = discord.send('after the retries', conn_name=Conn_Name)
        assert response['is_ok'] is True, response

# ################################################################################################################################

    def test_a_call_made_during_the_handshake_proceeds_once_ready_arrives(self, discord:'DiscordSuite') -> 'None':
        """ A call made while READY is delayed does not fail - it waits and then proceeds.
        """
        discord.simulator.ready_delay = 1.0

        _ = discord.create_connection(Conn_Name)

        start = time.monotonic()
        response = discord.send('while READY is on its way', conn_name=Conn_Name)
        elapsed = time.monotonic() - start

        assert response['is_ok'] is True, response
        assert elapsed >= 1.0

        message = discord.wait_for_messages(1)[0]
        assert message.content == 'while READY is on its way'

# ################################################################################################################################
# ################################################################################################################################
