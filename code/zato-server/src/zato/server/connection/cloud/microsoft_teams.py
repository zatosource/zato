# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.server.connection.cloud.microsoft_365 import Microsoft365Client

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftTeamsClient:
    """ Sends messages to Microsoft Teams channels, people and groups through the Graph API.
    """
    def __init__(self, config:'stranydict') -> 'None':

        self.config = config
        self.name = config['name']

        # All the Graph API plumbing - tokens, sessions and URLs - comes from the underlying Microsoft 365 client.
        self.impl = Microsoft365Client(config)

# ################################################################################################################################

    def _get_one_id(self, url:'str', display_name:'str', object_kind:'str') -> 'str':
        """ Returns the ID of the one Graph object under the URL whose display name matches the input.
        """

        # Ask the Graph API for objects matching the display name ..
        params = {'$filter': f"displayName eq '{display_name}'"}
        response = self.impl.con.get(url, params=params)

        # .. the matches are in the value list ..
        data = response.json()
        items = data['value']

        # .. no matches means the name does not exist in the tenant ..
        if not items:
            raise Exception(f'Microsoft Teams {object_kind} not found ({self.name}) -> `{display_name}`')

        # .. and the first match is the one we need.
        item = items[0]

        out = item['id']
        return out

# ################################################################################################################################

    def _post_message(self, url:'str', text:'str') -> 'stranydict':
        """ Posts a message under the URL given on input. The text is HTML, which is how rich content is sent.
        """
        data = {
            'body': {
                'contentType': 'html',
                'content': text,
            }
        }

        response = self.impl.con.post(url, data=data)

        out = response.json()
        return out

# ################################################################################################################################

    def _send_to_channel(self, to:'str', text:'str') -> 'stranydict':
        """ Sends a message to a channel, with the target given as 'Team name/Channel name'.
        """
        service_url = self.impl.protocol.service_url

        # A slash separates the team's name from the channel's name ..
        team_name, channel_name = to.split('/', 1)

        # .. resolve both names to their Graph IDs ..
        team_id = self._get_one_id(f'{service_url}teams', team_name, 'team')
        channel_id = self._get_one_id(f'{service_url}teams/{team_id}/channels', channel_name, 'channel')

        # .. and post the message to the channel.
        url = f'{service_url}teams/{team_id}/channels/{channel_id}/messages'

        out = self._post_message(url, text)
        return out

# ################################################################################################################################

    def _send_to_chat(self, to:'str', text:'str') -> 'stranydict':
        """ Sends a message to a chat with a person or a group, with the target given as a chat ID.
        """
        service_url = self.impl.protocol.service_url
        url = f'{service_url}chats/{to}/messages'

        out = self._post_message(url, text)
        return out

# ################################################################################################################################

    def send(self, to:'str', text:'str') -> 'stranydict':
        """ Sends a message to Microsoft Teams. The target is either 'Team name/Channel name' for channels
        or a chat ID for chats with people and groups. The text is HTML, which is how rich content is sent.
        """

        # A slash means the target is a channel within a team, anything else is a chat with a person or a group.
        if '/' in to:
            out = self._send_to_channel(to, text)
        else:
            out = self._send_to_chat(to, text)

        return out

# ################################################################################################################################

    def zato_delete_impl(self, reason:'str'='') -> 'None':
        self.impl.zato_delete_impl(reason)

# ################################################################################################################################

    def ping(self) -> 'None':
        self.impl.ping()

# ################################################################################################################################
# ################################################################################################################################
