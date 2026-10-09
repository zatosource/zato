# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import Discord

# Live Discord
from live_discord.simulator import Error_Code_Unknown_Channel

# Test support
from conftest import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import DiscordSuite

# ################################################################################################################################
# ################################################################################################################################

Other_Channel = '200000000000000002'

# ################################################################################################################################
# ################################################################################################################################

class TestSend:

    def test_a_message_goes_to_the_default_channel(self, discord:'DiscordSuite') -> 'None':
        """ The connection sends the message to its default channel as JSON, with the bot token and the user agent
        Discord requires, and the service receives what Discord answered.
        """
        response = discord.send('Build 1234 finished')
        assert response['is_ok'] is True, response

        messages = discord.wait_for_messages(1)
        message = messages[0]

        assert message.channel_id == ModuleCtx.Default_Channel
        assert message.content == 'Build 1234 finished'
        assert message.is_multipart is False
        assert message.allowed_mentions == {'parse': []}
        assert message.headers['Authorization'] == f'Bot {ModuleCtx.Token}'
        assert message.headers['User-Agent'] == Discord.Default.User_Agent

        assert response['response']['id'] == message.id
        assert response['response']['channel_id'] == ModuleCtx.Default_Channel

# ################################################################################################################################

    def test_an_explicit_channel_replaces_the_default(self, discord:'DiscordSuite') -> 'None':

        response = discord.send('elsewhere', channel_id=Other_Channel)
        assert response['is_ok'] is True, response

        messages = discord.wait_for_messages(1)
        assert messages[0].channel_id == Other_Channel

# ################################################################################################################################

    def test_embeds_and_allowed_mentions_travel_with_the_content(self, discord:'DiscordSuite') -> 'None':

        embeds = [{'title': 'Deployment', 'description': 'Version 4.1 is live', 'color': 5763719}]
        allowed_mentions = {'parse': ['users']}

        response = discord.send('Deployed', embeds=embeds, allowed_mentions=allowed_mentions)
        assert response['is_ok'] is True, response

        message = discord.wait_for_messages(1)[0]
        assert message.embeds == embeds
        assert message.allowed_mentions == allowed_mentions

# ################################################################################################################################

    def test_files_are_sent_as_multipart(self, discord:'DiscordSuite') -> 'None':

        files = [('report.txt', b'line 1\nline 2\n'), ('data.bin', b'\x00\x01\x02')]

        response = discord.send('With attachments', files=files)
        assert response['is_ok'] is True, response

        message = discord.wait_for_messages(1)[0]

        assert message.is_multipart is True
        assert message.content == 'With attachments'
        assert len(message.files) == 2
        assert message.files[0].file_name == 'report.txt'
        assert message.files[0].data == b'line 1\nline 2\n'
        assert message.files[1].file_name == 'data.bin'
        assert message.files[1].data == b'\x00\x01\x02'

# ################################################################################################################################

    def test_an_unknown_channel_is_reported_with_the_discord_error(self, discord:'DiscordSuite') -> 'None':

        discord.simulator.unknown_channels.append(Other_Channel)

        response = discord.send('to nowhere', channel_id=Other_Channel)

        assert response['is_ok'] is False, response
        assert str(Error_Code_Unknown_Channel) in response['error'], response
        assert 'Unknown Channel' in response['error'], response
        assert discord.simulator.messages == []

# ################################################################################################################################

    def test_a_rate_limited_message_is_retried(self, discord:'DiscordSuite') -> 'None':

        discord.simulator.rate_limited_calls_left = 2
        discord.simulator.rate_limit_retry_after = 0.2

        response = discord.send('after the rate limit')
        assert response['is_ok'] is True, response

        assert len(discord.simulator.rejections) == 2
        assert len(discord.simulator.messages) == 1

# ################################################################################################################################

    def test_the_dashboard_invoker_sends_through_the_same_client(self, discord:'DiscordSuite') -> 'None':
        """ The Dashboard's send-message dialog goes through the internal invoke service, with the channel as the target.
        """
        response = discord.dashboard_send('from the Dashboard', target=Other_Channel)
        assert 'response_data' in response, response

        message = discord.wait_for_messages(1)[0]
        assert message.channel_id == Other_Channel
        assert message.content == 'from the Dashboard'

        # Without a target the message goes to the default channel
        _ = discord.dashboard_send('to the default channel')

        message = discord.wait_for_messages(2)[1]
        assert message.channel_id == ModuleCtx.Default_Channel

# ################################################################################################################################

    def test_any_endpoint_can_be_invoked(self, discord:'DiscordSuite') -> 'None':

        response = discord.invoke_api('GET', 'users/@me')

        assert response['is_ok'] is True, response
        assert response['response']['bot'] is True

# ################################################################################################################################
# ################################################################################################################################
