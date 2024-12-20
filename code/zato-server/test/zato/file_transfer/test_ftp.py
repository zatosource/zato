# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

"""
# stdlib
import logging
import os
from unittest import main, TestCase
from uuid import uuid4

# pyfilesystem
from fs.ftpfs import FTPFS

# pyftpdlib
from pyftpdlib.log import config_logging as pyftpdlib_config_logging

# Zato
from zato.common.util.api import wait_until_port_taken
from zato.common.test.ftp import config as ftp_config, FTPServer
from zato.server.connection.file_client.api import FTPFileClient

# ################################################################################################################################
# ################################################################################################################################

pyftpdlib_config_logging(level=logging.WARN)

# ################################################################################################################################
# ################################################################################################################################


class FTPFileTransferTestCase(TestCase):
    def test_ftp(self):

        base_test_dir = 'base_test_dir.{}'.format(uuid4().hex)
        base_test_path = '/{}'.format(base_test_dir)

        test_file = 'zxc.txt'
        test_data = 'test_data.{}'.format(uuid4()).encode()
        test_file_path = os.path.join(base_test_path, test_file)

        def check_directory(client, should_exist):
            # type: (FTPFileClient, bool)

            result = client.list('/')
            directory_list = result['directory_list']
            for item in directory_list:
                if item['name'] == base_test_dir:
                    if not should_exist:
                        raise ValueError('Directory `{}` should not exist'.format(
                            os.path.normpath(os.path.join(ftp_config.directory, base_test_dir))))
                    else:
                        self.assertTrue(item['is_dir'])
                        break
            else:
                if should_exist:
                    raise ValueError('Expected for directory `{}` to exist'.format(
                        os.path.normpath(os.path.join(ftp_config.directory, base_test_dir))))

        # Create an embedded FTP server ..
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

        # .. confirm we are connected ..
        ping_response = client.ping()
        self.assertTrue(ping_response)

        # .. create a new directory ..
        client.create_directory(base_test_dir)

        # .. make sure the directory was created ..
        check_directory(client, True)

        # .. store a new file ..
        client.store(test_file_path, test_data)

        # .. download the uploaded file ..
        received_data = client.get(test_file_path)

        # .. compare the downloaded and uploaded data ..
        self.assertEqual(received_data, test_data)

        # .. delete the test directory ..
        client.delete_directory(base_test_dir)

        # .. make sure the directory was deleted ..
        check_directory(client, False)

        # .. stop the client ..
        client.close()

        # .. finally, stop the embedded server.
        server.stop()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
"""
