# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from unittest import main, TestCase

# Zato
from zato.server.connection.email import Microsoft365IMAPConnection

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_Key_Tenant_ID = 'Zato_Test_IMAP_MS365_Tenant_ID'
    Env_Key_Client_ID = 'Zato_Test_IMAP_MS365_Client_ID'
    Env_Key_Secret = 'Zato_Test_IMAP_MS365_Secret'
    Env_Key_Resource = 'Zato_Test_IMAP_MS365_Resource'

# ################################################################################################################################
# ################################################################################################################################

class Microsoft365IMAPConnectionTestCase(TestCase):

    def test_ping(self):

        # Try to get the main environment variable ..
        tenant_id = os.environ.get(ModuleCtx.Env_Key_Tenant_ID)

        # .. and if it does not exist, do not run the test
        if not tenant_id:
            return
        else:
            client_id = os.environ.get(ModuleCtx.Env_Key_Tenant_ID)
            secret = os.environ.get(ModuleCtx.Env_Key_Secret)
            resource = os.environ.get(ModuleCtx.Env_Key_Resource)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
