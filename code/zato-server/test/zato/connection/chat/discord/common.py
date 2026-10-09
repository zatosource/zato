# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The shared fixtures of the Discord client tests - the simulator each test case starts, the client built
# against it and the shortened handshake pause.

# stdlib
from time import monotonic
from unittest import TestCase

# gevent
from gevent import sleep

# Zato
from zato.server.connection.chat.discord import DiscordClient

# Live Discord
from live_discord.simulator import DiscordSimulator

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The bot token the simulator accepts
Token = 'MTAwMDAwMDAwMDAwMDAwMDAwMQ.GaBcDe.ThisIsATestTokenForTheDiscordSimulator01'

# The default channel of every client
Default_Channel = '200000000000000001'

# The channel each test sends to when it names one
Other_Channel = '200000000000000002'

# The recipient of direct messages
User_ID = '300000000000000001'

# How long a client waits for READY, in seconds, shorter than the default so that timeouts are quick to observe
Timeout = 2

# The pause between handshake attempts, in seconds, shorter than the default so that retries are quick to observe
Handshake_Pause = 0.3

# How long a test waits for the simulator to record an event
Wait_Timeout = 5.0

# ################################################################################################################################
# ################################################################################################################################

def wait_until(condition:'callable_', what:'str', timeout:'float'=Wait_Timeout) -> 'None':
    """ Waits until the condition holds, yielding to the handshake greenlet in the meantime.
    """
    deadline = monotonic() + timeout

    while not condition():
        if monotonic() > deadline:
            raise AssertionError(f'Timed out after {timeout}s waiting until {what}')
        sleep(0.01)

# ################################################################################################################################
# ################################################################################################################################

class DiscordTestCase(TestCase):
    """ A simulator started before each test and stopped after it, with a shortened handshake pause.
    """
    simulator:'DiscordSimulator'
    clients:'list[DiscordClient]'

    def setUp(self) -> 'None':
        self.simulator = DiscordSimulator(Token)
        self.simulator.start()
        self.clients = []

    def tearDown(self) -> 'None':
        for client in self.clients:
            client.stop('test ended')
        self.simulator.stop()

# ################################################################################################################################

    def new_client(self, **overrides:'any_') -> 'DiscordClient':
        """ A client pointed at the simulator, with the handshake not yet started.
        """
        config:'stranydict' = {
            'name': 'test.discord',
            'address': self.simulator.address,
            'timeout': Timeout,
            'default_channel_id': Default_Channel,
            'token': Token,
        }
        config.update(overrides)

        out = DiscordClient(config)
        out.handshake_pause = Handshake_Pause

        self.clients.append(out)
        return out

# ################################################################################################################################

    def new_ready_client(self, **overrides:'any_') -> 'DiscordClient':
        """ A client whose handshake has completed.
        """
        out = self.new_client(**overrides)
        out.start_handshake()
        out._wait_until_ready()
        return out

# ################################################################################################################################
# ################################################################################################################################
