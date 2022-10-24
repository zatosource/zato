# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from unittest import main, TestCase

# Zato
from zato.common.api import EMAIL
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

    def get_conn(self) -> 'Microsoft365IMAPConnection | None':

        # Try to get the main environment variable ..
        tenant_id = os.environ.get(ModuleCtx.Env_Key_Tenant_ID)

        # .. and if it does not exist, do not run the test
        if not tenant_id:
            return
        else:
            client_id = os.environ.get(ModuleCtx.Env_Key_Client_ID)
            secret = os.environ.get(ModuleCtx.Env_Key_Secret)
            resource = os.environ.get(ModuleCtx.Env_Key_Resource)

        config = {
            'cluster_id': 1,
            'id': 2,
            'is_active':True,
            'opaque1':None,
            'name': 'My Name',
            'tenant_id': tenant_id,
            'client_id': client_id,
            'password': secret,
            'username': resource,
            'filter_criteria': EMAIL.DEFAULT.FILTER_CRITERIA,
            'server_type': EMAIL.IMAP.ServerType.Microsoft365,
        }

        conn = Microsoft365IMAPConnection(config, config)
        return conn

# ################################################################################################################################

    def xtest_ping(self):

        conn = self.get_conn()
        if not conn:
            return

        # Assume we will not find the Inbox folder
        found_inbox = False

        # Run the function under test
        result = conn.ping()

        for item in result:
            if item.name == 'Inbox':
                found_inbox = True
                break

        if not found_inbox:
            self.fail(f'Expected for folder Inbox to exist among {result}')

# ################################################################################################################################

    def test_get(self):

        conn = self.get_conn()
        if not conn:
            return

        # Run the function under test
        result = conn.get()

        print(111, result)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
