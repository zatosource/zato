# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK
from logging import getLogger

# Requests
import requests

# Zato
from zato.common.api import Slack
from zato.common.const import SECRETS

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydictnone, anylistnone, stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_default = Slack.Default

# ################################################################################################################################
# ################################################################################################################################

class SlackClient:
    """ Client for the Slack Web API, used to send messages to channels, people and groups.
    """
    def __init__(self, config:'stranydict') -> 'None':

        self.config = config
        self.name = config['name']

        # The bot token lives in the secret column, except when the connection
        # was imported with the token given directly in its definition.
        token = config.get('secret')
        if (not token) or token.startswith(SECRETS.Auto_Generated_Prefix):
            token = config['token']
        self.token = token

        # The base address of the Slack Web API - it is the public cloud unless configured otherwise, e.g. in tests.
        if address := config.get('address'):
            self.address = address.rstrip('/')
        else:
            self.address = _default.Address

        # A single session shared by all the requests this client makes.
        self.session = requests.Session()

# ################################################################################################################################

    def invoke(self, method_name:'str', data:'anydictnone'=None) -> 'stranydict':
        """ Invokes any Slack Web API method, returning the parsed JSON response.
        """

        # Build the full address of the method to invoke ..
        url = f'{self.address}/{method_name}'

        # .. each request carries the bot token ..
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json; charset=utf-8',
        }

        # .. invoke the method ..
        response = self.session.post(url, headers=headers, json=data)

        # .. anything other than 200 OK means the request never reached the API proper ..
        if response.status_code != OK:
            raise Exception(f'Slack error ({self.name}) -> {method_name}: {response.status_code} -> {repr(response.text)}')

        out = response.json()

        # .. Slack reports errors in the payload rather than through status codes ..
        if not out['ok']:
            error = out['error']
            raise Exception(f'Slack error ({self.name}) -> {method_name}: {error}')

        # .. and hand back the parsed response.
        return out

# ################################################################################################################################

    def send(self, channel:'str', text:'str', blocks:'anylistnone'=None) -> 'stranydict':
        """ Sends a message to a channel, person or group. The text may use Slack's rich formatting (mrkdwn)
        and blocks, if given, carry Block Kit content.
        """
        data = {
            'channel': channel,
            'text': text,
        }

        # Block Kit content is optional - the text above is used when it is not given.
        if blocks:
            data['blocks'] = blocks

        out = self.invoke('chat.postMessage', data)
        return out

# ################################################################################################################################

    def ping(self) -> 'None':
        """ Confirms that the connection's token is valid.
        """
        response = self.invoke('auth.test')

        logger.info('Slack ping OK (%s) -> %s', self.name, response['team'])

# ################################################################################################################################
# ################################################################################################################################
