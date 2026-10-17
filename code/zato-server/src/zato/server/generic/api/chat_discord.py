# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.common.api import Discord
from zato.server.connection.chat.discord import DiscordClient
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_default = Discord.Default

# Default values applied when a configuration key is missing or None
discord_config_defaults:'stranydict' = {
    'address': _default.Address,
    'timeout': _default.Timeout,
    'default_channel_id': '',
}

# Config keys that must be integers but may arrive as strings from opaque storage
discord_int_config_keys = ('timeout',)

# What callers waiting for the gateway handshake are told when the connection goes away under them
_stop_reason = 'was edited or deleted'

# ################################################################################################################################
# ################################################################################################################################

class ChatDiscordWrapper(Wrapper):
    """ Wraps a connection to Discord. A single client is shared by all the services that access the connection,
    because the gateway handshake is performed once per connection rather than once per client.
    """
    def __init__(self, config:'any_', server:'any_') -> 'None':
        config['auth_url'] = config['address']
        super(ChatDiscordWrapper, self).__init__(config, 'Discord', server)

        self.shared_client = DiscordClient(config)

# ################################################################################################################################

    def add_client(self) -> 'None':
        _ = self.client.put_client(self.shared_client)

# ################################################################################################################################

    def build_wrapper(self) -> 'None':

        # The handshake runs in the background - this call returns before it completes ..
        if self.config['is_active']:
            self.shared_client.start_handshake()

        # .. and the queue is filled with references to the shared client.
        self.build_queue()

# ################################################################################################################################

    def delete(self, reason:'strnone'=None) -> 'None':

        # Stop the handshake before the queue is taken apart, so that no attempt outlives the connection.
        self.shared_client.stop(_stop_reason)
        super(ChatDiscordWrapper, self).delete(reason)

# ################################################################################################################################

    def ping(self) -> 'None':
        self.shared_client.ping()

# ################################################################################################################################
# ################################################################################################################################
