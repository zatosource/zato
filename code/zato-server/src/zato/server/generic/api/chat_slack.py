# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.typing_ import cast_
from zato.server.connection.chat.slack import SlackClient
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ChatSlackWrapper(Wrapper):
    """ Wraps a queue of connections to Slack.
    """
    def __init__(self, config:'any_', server:'any_') -> 'None':
        config['auth_url'] = config['address']
        super(ChatSlackWrapper, self).__init__(config, 'Slack', server)

        # A single client shared by all the services that access this connection directly,
        # e.g. through self.slack. This is safe because requests sessions maintain
        # their own HTTP connection pools.
        self.shared_client = SlackClient(config)

# ################################################################################################################################

    def add_client(self):

        try:
            conn = SlackClient(self.config)
            _ = self.client.put_client(conn)
        except Exception:
            logger.warning('Caught an exception while adding a Slack client (%s); e:`%s`',
                self.config['name'], format_exc())

# ################################################################################################################################

    def ping(self):
        with self.client() as client:
            client = cast_('SlackClient', client)
            client.ping()

# ################################################################################################################################
# ################################################################################################################################
