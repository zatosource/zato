# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Test support
from conftest import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import DiscordSuite

# ################################################################################################################################
# ################################################################################################################################

class TestPing:

    def test_a_ping_reaches_the_bot_user_endpoint(self, discord:'DiscordSuite') -> 'None':

        response = discord.ping()

        assert response['is_ok'] is True, response
        assert discord.simulator.rejections == []

# ################################################################################################################################

    def test_the_dashboard_ping_succeeds(self, discord:'DiscordSuite') -> 'None':
        """ The Dashboard's ping goes through the internal ping service, which calls the wrapper's ping.
        """
        response = discord.dashboard_ping()

        assert response['is_success'] is True, response
        assert discord.simulator.rejections == []

# ################################################################################################################################

    def test_a_ping_with_a_refused_token_fails(self, discord:'DiscordSuite') -> 'None':
        """ The simulator refuses the token for the duration of the test and the ping reports the 401.
        """
        discord.simulator.token = 'another-token'

        try:
            response = discord.ping()
        finally:
            discord.simulator.token = ModuleCtx.Token

        assert response['is_ok'] is False, response
        assert '401' in response['error'], response

# ################################################################################################################################
# ################################################################################################################################
