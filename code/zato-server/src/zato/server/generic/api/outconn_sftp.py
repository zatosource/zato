# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from traceback import format_exc


# Zato
from zato.server.connection.queue import Wrapper

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class SFTPClient(object):
    """ Represents a connection to an SFTP connector.
    """
    def __init__(self, config):
        self.config = config

    def delete(self):
        # Needed for API completeness
        pass

# ################################################################################################################################
# ################################################################################################################################

class OutconnSFTPWrapper(Wrapper):
    """ Wraps a queue of connections to an SFTP server.
    """
    def __init__(self, config, server):
        config.parent = self
        super(OutconnSFTPWrapper, self).__init__(config, 'outgoing SFTP', server)

# ################################################################################################################################

    def ping(self):
        print()
        print()

        with self.client() as conn:
            print(222, `conn`)

        print()
        print()

# ################################################################################################################################

    def add_client(self):
        try:
            conn = SFTPClient(self.config)
        except Exception:
            logger.warn('SFTP client could not be built `%s`', format_exc())
        else:
            self.client.put_client(conn)

# ################################################################################################################################
# ################################################################################################################################
