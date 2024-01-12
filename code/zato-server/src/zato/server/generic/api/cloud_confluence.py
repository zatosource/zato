# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.typing_ import cast_
from zato.server.connection.confluence_ import ConfluenceClient
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class _ConfluenceClient(ConfluenceClient):
    def __init__(self, config:'stranydict') -> 'None':
        super().__init__(
            zato_api_version = config['api_version'],
            zato_address = config['address'],
            zato_username = config['username'],
            zato_token = config['secret'],
            zato_is_cloud = config['is_cloud'],
        )

    def ping(self):
        return self.request()

# ################################################################################################################################
# ################################################################################################################################

class CloudConfluenceWrapper(Wrapper):
    """ Wraps a queue of connections to Confluence.
    """
    def __init__(self, config:'stranydict', server) -> 'None':
        config['auth_url'] = config['address']
        super(CloudConfluenceWrapper, self).__init__(config, 'Confluence', server)

# ################################################################################################################################

    def add_client(self):

        try:
            conn = _ConfluenceClient(self.config)
            self.client.put_client(conn)
        except Exception:
            logger.warning('Caught an exception while adding a Confluence client (%s); e:`%s`',
                self.config['name'], format_exc())

# ################################################################################################################################

    def ping(self):
        with self.client() as client:
            client = cast_('_ConfluenceClient', client)
            client.ping()

# ################################################################################################################################

    def delete(self, ignored_reason=None):
        pass

# ################################################################################################################################
# ################################################################################################################################
