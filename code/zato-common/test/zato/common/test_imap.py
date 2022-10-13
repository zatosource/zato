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

# Zato
from zato.common.ext.imbox.imbox import Imbox

# ################################################################################################################################
# ################################################################################################################################

class IMAP_Without_OAuth_TestCase(TestCase):

    def test_connection(self) -> 'None':

        host = os.environ.get('Zato_Test_IMAP_Host')
        if not host:
            return

        password = os.environ.get('Zato_Test_IMAP_Password')
        port = os.environ.get('Zato_Test_IMAP_Port')
        username = os.environ.get('Zato_Test_IMAP_Username')

        imbox = Imbox(
            hostname = host,
            username = username,
            password = password,
            port = port,
        )

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
