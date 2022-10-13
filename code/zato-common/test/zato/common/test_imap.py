# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
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

class IMAP_Without_OAuth_TestCase(TestCase):

    def test_connection(self) -> 'None':

        host = os.environ.get('Zato_Test_IMAP_Host')
        if not host:
            return

        port = os.environ.get('Zato_Test_IMAP_Port')
        username = os.environ.get('Zato_Test_IMAP_Username')
        password = os.environ.get('Zato_Test_IMAP_Password')

        config = Bunch()

        config.host = host
        config.port = port

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

class IMAP_With_OAuth_TestCase(TestCase):

    def xtest_connection(self) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
