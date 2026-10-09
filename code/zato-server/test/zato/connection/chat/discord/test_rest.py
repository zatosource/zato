# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The REST calls of a client whose handshake has completed - messages as JSON and as multipart, the default
# allowed mentions, direct messages with the channel cache, rate limits, errors and the ping.

# stdlib
from unittest import main

# Zato
from zato.common.api import Discord

# Live Discord
from live_discord.simulator import Bot_Username, DM_Channel_Prefix, Error_Code_Unknown_Channel

# Test support
from test.zato.connection.chat.discord.common import Default_Channel, DiscordTestCase, Other_Channel, Token, User_ID

# ################################################################################################################################
# ################################################################################################################################

class SendTestCase(DiscordTestCase):

    def test_a_message_goes_to_the_default_channel_as_json(self) -> 'None':

        client = self.new_ready_client()
        response = client.send('Build 1234 finished')

        self.assertEqual(len(self.simulator.messages), 1)
        message = self.simulator.messages[0]

        self.assertEqual(message.channel_id, Default_Channel)
        self.assertEqual(message.content, 'Build 1234 finished')
        self.assertFalse(message.is_multipart)
        self.assertEqual(message.files, [])
        self.assertEqual(message.embeds, [])

        self.assertEqual(message.headers['Authorization'], f'Bot {Token}')
        self.assertEqual(message.headers['User-Agent'], Discord.Default.User_Agent)

        self.assertEqual(response['id'], message.id)
        self.assertEqual(response['channel_id'], Default_Channel)

# ################################################################################################################################

    def test_an_explicit_channel_replaces_the_default(self) -> 'None':

        client = self.new_ready_client()
        _ = client.send('elsewhere', Other_Channel)

        self.assertEqual(self.simulator.messages[0].channel_id, Other_Channel)

# ################################################################################################################################

    def test_mentions_notify_no_one_unless_allowed(self) -> 'None':

        client = self.new_ready_client()
        _ = client.send('@everyone look')

        self.assertEqual(self.simulator.messages[0].allowed_mentions, {'parse': []})

        _ = client.send('@everyone look', allowed_mentions={'parse': ['everyone']})

        self.assertEqual(self.simulator.messages[1].allowed_mentions, {'parse': ['everyone']})

# ################################################################################################################################

    def test_embeds_travel_with_the_content(self) -> 'None':

        embeds = [{'title': 'Deployment', 'description': 'Version 4.1 is live', 'color': 5763719}]

        client = self.new_ready_client()
        _ = client.send('Deployed', embeds=embeds)

        self.assertEqual(self.simulator.messages[0].embeds, embeds)

# ################################################################################################################################

    def test_files_are_sent_as_multipart_with_the_payload_in_its_own_part(self) -> 'None':

        files = [('report.txt', b'line 1\nline 2\n'), ('data.bin', b'\x00\x01\x02')]

        client = self.new_ready_client()
        _ = client.send('With attachments', files=files)

        message = self.simulator.messages[0]

        self.assertTrue(message.is_multipart)
        self.assertEqual(message.content, 'With attachments')
        self.assertEqual(message.allowed_mentions, {'parse': []})

        self.assertEqual(len(message.files), 2)
        self.assertEqual(message.files[0].field_name, 'files[0]')
        self.assertEqual(message.files[0].file_name, 'report.txt')
        self.assertEqual(message.files[0].data, b'line 1\nline 2\n')
        self.assertEqual(message.files[1].field_name, 'files[1]')
        self.assertEqual(message.files[1].file_name, 'data.bin')
        self.assertEqual(message.files[1].data, b'\x00\x01\x02')

# ################################################################################################################################

    def test_a_message_without_a_channel_and_without_a_default_is_refused(self) -> 'None':

        client = self.new_ready_client(default_channel_id='')

        with self.assertRaises(Exception) as ctx:
            _ = client.send('nowhere to go')

        self.assertIn('no channel ID given', str(ctx.exception))
        self.assertEqual(self.simulator.messages, [])

# ################################################################################################################################

    def test_an_unknown_channel_is_reported_with_the_discord_error_code(self) -> 'None':

        self.simulator.unknown_channels = [Other_Channel]

        client = self.new_ready_client()

        with self.assertRaises(Exception) as ctx:
            _ = client.send('to an unknown channel', Other_Channel)

        error = str(ctx.exception)
        self.assertIn('404', error)
        self.assertIn(str(Error_Code_Unknown_Channel), error)
        self.assertIn('Unknown Channel', error)

# ################################################################################################################################

    def test_a_rate_limited_call_is_retried_after_the_given_time(self) -> 'None':

        client = self.new_ready_client()

        self.simulator.rate_limited_calls_left = 2
        self.simulator.rate_limit_retry_after = 0.1

        response = client.send('after the rate limit')

        self.assertEqual(response['content'], 'after the rate limit')
        self.assertEqual(len(self.simulator.rejections), 2)
        self.assertEqual(len(self.simulator.messages), 1)

# ################################################################################################################################

    def test_rate_limit_retries_are_not_endless(self) -> 'None':

        client = self.new_ready_client()

        self.simulator.rate_limited_calls_left = Discord.Default.Max_Rate_Limit_Retries + 10
        self.simulator.rate_limit_retry_after = 0.01

        with self.assertRaises(Exception) as ctx:
            _ = client.send('never accepted')

        self.assertIn('rate limit retries exhausted', str(ctx.exception))
        self.assertEqual(len(self.simulator.rejections), Discord.Default.Max_Rate_Limit_Retries + 1)

# ################################################################################################################################
# ################################################################################################################################

class SendDirectTestCase(DiscordTestCase):

    def test_a_direct_message_opens_the_channel_once(self) -> 'None':

        client = self.new_ready_client()

        _ = client.send_direct(User_ID, 'first')
        _ = client.send_direct(User_ID, 'second')

        self.assertEqual(self.simulator.dm_channel_calls, 1)
        self.assertEqual(client.direct_channels, {User_ID: DM_Channel_Prefix + User_ID})

        messages = self.simulator.messages
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].channel_id, DM_Channel_Prefix + User_ID)
        self.assertEqual(messages[0].content, 'first')
        self.assertEqual(messages[1].channel_id, DM_Channel_Prefix + User_ID)
        self.assertEqual(messages[1].content, 'second')

# ################################################################################################################################

    def test_a_direct_message_takes_embeds_and_files(self) -> 'None':

        client = self.new_ready_client()
        _ = client.send_direct(User_ID, 'see attached', embeds=[{'title': 'Report'}], files=[('a.txt', b'a')])

        message = self.simulator.messages[0]
        self.assertTrue(message.is_multipart)
        self.assertEqual(message.embeds, [{'title': 'Report'}])
        self.assertEqual(message.files[0].file_name, 'a.txt')

# ################################################################################################################################
# ################################################################################################################################

class InvokeAndPingTestCase(DiscordTestCase):

    def test_invoke_reaches_any_endpoint(self) -> 'None':

        client = self.new_ready_client()
        response = client.invoke('GET', 'users/@me')

        self.assertEqual(response['username'], Bot_Username)

# ################################################################################################################################

    def test_ping_succeeds_once_ready(self) -> 'None':

        client = self.new_ready_client()
        client.ping()

        self.assertEqual(self.simulator.rejections, [])

# ################################################################################################################################

    def test_ping_waits_for_ready_like_every_call(self) -> 'None':

        self.simulator.never_send_ready = True

        client = self.new_client()
        client.start_handshake()

        with self.assertRaises(Exception) as ctx:
            client.ping()

        self.assertIn('not ready after', str(ctx.exception))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
