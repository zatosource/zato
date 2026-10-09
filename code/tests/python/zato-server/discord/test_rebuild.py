# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An edit rebuilds the connection - the old client is stopped, a new one performs the handshake anew and calls
# go through the new one with the edited configuration.

# Test support
from conftest import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import DiscordSuite

# ################################################################################################################################
# ################################################################################################################################

Conn_Name = 'test.discord.rebuild'
New_Default_Channel = '200000000000000009'

# ################################################################################################################################
# ################################################################################################################################

class TestRebuild:

    def test_an_edit_performs_the_handshake_anew(self, discord:'DiscordSuite') -> 'None':

        _ = discord.create_connection(Conn_Name)
        _ = discord.wait_until_ready(Conn_Name)
        assert len(discord.wait_for_identifies(1)) == 1

        _ = discord.edit_connection({'default_channel_id': New_Default_Channel}, conn_name=Conn_Name)

        # The new client identifies itself anew ..
        identifies = discord.wait_for_identifies(2)
        assert identifies[1].is_ready_sent is True

        connection = discord.wait_until_ready(Conn_Name)
        assert connection['default_channel_id'] == New_Default_Channel

        # .. and the edited configuration is what calls use.
        response = discord.send('after the edit', conn_name=Conn_Name)
        assert response['is_ok'] is True, response

        message = discord.wait_for_messages(1)[0]
        assert message.channel_id == New_Default_Channel

# ################################################################################################################################

    def test_an_edit_keeps_the_token(self, discord:'DiscordSuite') -> 'None':
        """ The Dashboard's edit form does not send the token back and the rebuilt client uses the stored one.
        """
        _ = discord.create_connection(Conn_Name)
        _ = discord.wait_until_ready(Conn_Name)

        _ = discord.edit_connection({'timeout': ModuleCtx.Timeout + 1}, conn_name=Conn_Name)

        identifies = discord.wait_for_identifies(2)
        assert identifies[1].token == ModuleCtx.Token

        connection = discord.wait_until_ready(Conn_Name)
        assert connection['timeout'] == ModuleCtx.Timeout + 1

        response = discord.ping(Conn_Name)
        assert response['is_ok'] is True, response

# ################################################################################################################################

    def test_a_rename_keeps_the_connection_usable_under_the_new_name(self, discord:'DiscordSuite') -> 'None':

        new_name = Conn_Name + '.renamed'

        _ = discord.create_connection(Conn_Name)
        _ = discord.wait_until_ready(Conn_Name)

        _ = discord.edit_connection({'name': new_name}, conn_name=Conn_Name)
        _ = discord.wait_until_ready(new_name)

        assert discord.get_connection(Conn_Name)['is_found'] is False

        response = discord.send('under the new name', conn_name=new_name)
        assert response['is_ok'] is True, response

# ################################################################################################################################
# ################################################################################################################################
