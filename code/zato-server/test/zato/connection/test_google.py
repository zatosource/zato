# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from unittest import main, TestCase

# Zato
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

        # Get the rest of the configuration
        user = os.environ.get(ModuleCtx.Env_Key_User) or 'Missing_Env_Key_User'

        # These are constant
        api_name = 'drive'
        api_version = 'v3'
        scopes = ['https://www.googleapis.com/auth/drive']

        client = GoogleClient(api_name, api_version, user, scopes, service_file_path)
        client.connect()

        # List all of the remote files available ..
        listing = client.files.list().execute()

        # .. if we are here, it means that the credentials were valid,
        # .. and even if we do not know what exactly is returned,
        # .. we still do know that it is a dict object.
        self.assertIsInstance(listing, dict)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
