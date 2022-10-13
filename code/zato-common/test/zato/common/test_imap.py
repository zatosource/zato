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

class _BaseTestCase(TestCase):

    def setUp(self) -> 'None':

        self.zato_test_config = {}

        host = os.environ.get('Zato_Test_IMAP_Host')
        if not host:
            return

        password = os.environ.get('Zato_Test_IMAP_Password')
        port = os.environ.get('Zato_Test_IMAP_Port')
        username = os.environ.get('Zato_Test_IMAP_Username')

        self.zato_test_config['host'] = host
        self.zato_test_config['port'] = port
        self.zato_test_config['username'] = username
        self.zato_test_config['password'] = password

# ################################################################################################################################
# ################################################################################################################################

class IMAP_Without_OAuth_TestCase(_BaseTestCase):

    def test_connection(self) -> 'None':

        if not self.zato_test_config:
            return

        imbox = Imbox(
            hostname=self.zato_test_config['host'],
            username=self.zato_test_config['username'],
            password=self.zato_test_config['password'],
            port=self.zato_test_config['port'],
        )

        result = imbox.folders()
        self.assertTrue(len(result) > 0)

        imbox.server.server.sock.close()

# ################################################################################################################################
# ################################################################################################################################

class IMAP_With_OAuth_TestCase(_BaseTestCase):

    def xtest_connection(self) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
