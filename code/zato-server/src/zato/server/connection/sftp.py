# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import typing

# ################################################################################################################################

if typing.TYPE_CHECKING:
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

class SFTPIPCFacade(object):
    """ Provides servers and services with access to SFTP resources.
    """
    def __init__(self, server, config):
        # type: (ParallelServer, dict) -> None
        self.server = server
        self.config = config

# ################################################################################################################################

    def ping(self, msg):
        # type: (dict) -> None

        print()
        print()

        print('111 SFTPIPCFacade', msg)

        print()
        print()

# ################################################################################################################################
# ################################################################################################################################
