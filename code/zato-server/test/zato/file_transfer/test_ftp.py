# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# pyfilesystem
from fs.ftpfs import FTPFS

# Zato
from zato.common.util.api import wait_until_port_taken
from zato.common.test.ftp import config as ftp_config, FTPServer
from zato.server.connection.file_client.api import FTPFileClient

# ################################################################################################################################
# ################################################################################################################################


class FTPFileTransferTestCase(TestCase):
    def test_ftp(self):

        # Create an embedded server ..
        server = FTPServer()

        # .. start it in a new thread ..
        server.start()

        # .. wait a moment to make sure it is started ..
        wait_until_port_taken(ftp_config.port)

        # .. create an underlying FTP connection object ..
        conn = FTPFS('localhost', ftp_config.username, ftp_config.password, port=ftp_config.port)

        # .. create a higher-level FTP client ..
        client = FTPFileClient(conn, {
            'encoding': 'utf8'
        })

        print(222, client.ping())

        # .. stop the client ..
        client.st

        # .. finally, stop the embedded server.
        server.stop()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
