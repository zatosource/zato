# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An edit or a delete of a connection whose handshake is in progress ends the handshake at once - the loop makes
# no further attempt, the websocket is closed and callers waiting for READY are released.

# stdlib
import time
from threading import Thread

# Zato
from zato.common.api import Discord

# Test support
from conftest import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import DiscordSuite
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

Conn_Name = 'test.discord.build-stop'

# How long a test observes the simulator after a stop, longer than the pause between handshake attempts
Observation_Period = Discord.Default.Handshake_Pause + 2

# ################################################################################################################################
# ################################################################################################################################

class TestBuildStop:

    def test_a_delete_during_the_handshake_ends_it(self, discord:'DiscordSuite') -> 'None':

        discord.simulator.never_send_ready = True

        _ = discord.create_connection(Conn_Name)
        _ = discord.wait_for_identifies(1)

        connection = discord.get_connection(Conn_Name)
        assert connection['is_ready'] is False, connection
        assert connection['has_handshake_greenlet'] is True, connection

        _ = discord.delete_connection(Conn_Name)

        # No further attempt follows the delete
        time.sleep(Observation_Period)
        assert len(discord.simulator.identifies) == 1
        assert discord.simulator.gateway_info_calls == 1

# ################################################################################################################################

    def test_an_edit_during_the_handshake_ends_it_and_starts_a_new_one(self, discord:'DiscordSuite') -> 'None':

        discord.simulator.never_send_ready = True

        _ = discord.create_connection(Conn_Name)
        _ = discord.wait_for_identifies(1)

        # The gateway lets the next handshake complete ..
        discord.simulator.never_send_ready = False

        _ = discord.edit_connection({'timeout': ModuleCtx.Timeout + 1}, conn_name=Conn_Name)

        # .. the new client identifies itself at once, without waiting for the old loop's pause ..
        identifies = discord.wait_for_identifies(2, timeout=ModuleCtx.Timeout)
        assert identifies[1].is_ready_sent is True

        _ = discord.wait_until_ready(Conn_Name)

        # .. and the old loop makes no further attempt.
        time.sleep(Observation_Period)
        assert len(discord.simulator.identifies) == 2

# ################################################################################################################################

    def test_a_delete_during_the_pause_between_attempts_ends_the_loop(self, discord:'DiscordSuite') -> 'None':

        # Every attempt fails until the connection is deleted
        discord.simulator.identify_close_codes.extend([4004] * 100)

        _ = discord.create_connection(Conn_Name)
        _ = discord.wait_for_identifies(1)

        _ = discord.delete_connection(Conn_Name)
        count_at_delete = len(discord.simulator.identifies)

        time.sleep(Observation_Period)
        assert len(discord.simulator.identifies) == count_at_delete

# ################################################################################################################################

    def test_a_delete_releases_callers_waiting_for_ready(self, discord:'DiscordSuite') -> 'None':

        discord.simulator.never_send_ready = True

        _ = discord.create_connection(Conn_Name)
        _ = discord.wait_for_identifies(1)

        # A caller blocks in the readiness gate ..
        responses:'anylist' = []

        def call() -> 'None':
            responses.append(discord.send('while waiting', conn_name=Conn_Name))

        caller = Thread(target=call, daemon=True)
        caller.start()
        time.sleep(0.5)
        assert responses == []

        # .. and the delete releases it long before the timeout.
        start = time.monotonic()
        _ = discord.delete_connection(Conn_Name)
        caller.join(ModuleCtx.Timeout)
        elapsed = time.monotonic() - start

        assert len(responses) == 1, responses
        assert responses[0]['is_ok'] is False, responses
        assert 'was edited or deleted' in responses[0]['error'], responses
        assert elapsed < ModuleCtx.Timeout

# ################################################################################################################################
# ################################################################################################################################
