# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Live Discord
from live_discord.simulator import DM_Channel_Prefix

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import DiscordSuite

# ################################################################################################################################
# ################################################################################################################################

User_ID = '300000000000000001'

# ################################################################################################################################
# ################################################################################################################################

class TestSendDirect:

    def test_a_direct_message_opens_the_channel_once(self, discord:'DiscordSuite') -> 'None':
        """ The first direct message to a person opens the DM channel and the second one reuses it.
        """
        response = discord.send_direct(User_ID, 'first')
        assert response['is_ok'] is True, response

        response = discord.send_direct(User_ID, 'second')
        assert response['is_ok'] is True, response

        messages = discord.wait_for_messages(2)

        assert discord.simulator.dm_channel_calls == 1
        assert messages[0].channel_id == DM_Channel_Prefix + User_ID
        assert messages[0].content == 'first'
        assert messages[1].channel_id == DM_Channel_Prefix + User_ID
        assert messages[1].content == 'second'

# ################################################################################################################################
# ################################################################################################################################
