# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import loads
from unittest import main, TestCase

# Zato
from zato.common.util.open_ import open_r
from zato.server.connection.google import GoogleClient

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_Key_Service_File_Path = 'Zato_Test_Google_Service_File_Path'
    Env_Key_User = 'Zato_Test_Google_User'

# ################################################################################################################################
# ################################################################################################################################

class GoogleClientTestCase(TestCase):

    def test_connect(self):

        # Try to get the main environment variable ..
        service_file_path = os.environ.get(ModuleCtx.Env_Key_Service_File_Path)

        # .. and if it does not exist, do not run the test
        if not service_file_path:
            return
        else:
            with open_r(service_file_path) as f:
                service_file_path = f.read()
                service_file_path = loads(service_file_path)

        # Get the rest of the configuration
        user = os.environ.get(ModuleCtx.Env_Key_User) or 'Missing_Env_Key_User'

        # These are constant
        api_name = 'drive'
        api_version = 'v3'
        scopes = ['https://www.googleapis.com/auth/drive']

        client = GoogleClient(api_name, api_version, user, scopes, service_file_path)
        client.connect()

        # Use the Google Drive API ..
        files_api = client.conn.files()

        # .. and list all of the remote files available ..
        listing = files_api.list().execute()

        # .. if we are here, it means that the credentials were valid,
        # .. and even if we do not know what exactly is returned,
        # .. we still do know that it is a dict object.
        self.assertIsInstance(listing, dict)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
