# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# This comes first
from gevent.monkey import patch_all
patch_all()

# stdlib
import os
from unittest import main, TestCase

# Bunch
from bunch import Bunch

# Zato
from zato.common.api import EMAIL
from zato.server.connection.email import Imbox

# ################################################################################################################################
# ################################################################################################################################

class _Base_Test_Case(TestCase):

    def _run_test(self, key_config):

        host_key = key_config.get('host')
        port_key = key_config.get('port')
        username_key = key_config.get('username')
        password_key = key_config.get('password')

        host = os.environ.get(host_key)
        if not host:
            return

        port = os.environ.get(port_key)
        username = os.environ.get(username_key)
        password = os.environ.get(password_key)

        config = Bunch()

        config.host = host
        config.port = int(port) # type: ignore

        config.username = username
        config.password = password

        config.mode = EMAIL.IMAP.MODE.SSL
        config.debug_level = 0

        imbox = Imbox(config, config)

        result = imbox.folders()
        self.assertTrue(len(result) > 0)

        imbox.server.server.sock.close()

# ################################################################################################################################
# ################################################################################################################################

class IMAP_Without_OAuth_TestCase(_Base_Test_Case):

    def test_connection(self) -> 'None':

        config = {
            'host': 'Zato_Test_IMAP_Host',
            'port': 'Zato_Test_IMAP_Port',
            'username': 'Zato_Test_IMAP_Username',
            'password': 'Zato_Test_IMAP_Password',
        }

        self._run_test(config)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
