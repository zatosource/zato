# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from unittest import main, TestCase

# Zato
from zato.common.odb.api import PoolStore, SessionWrapper

# ################################################################################################################################
# ################################################################################################################################

class SQLPublishWithRetryTestCase(TestCase):

    def setUp(self) -> 'None':

        # This test case requires for MySQL connection details to be available through environment variables.
        # If they are not specified, the test is skipped.
        database = os.environ.get('ZATO_ODB_DATABASE')

        if not database:
            self.should_run = False
            return

        # If we are here, it means that the test run and we need to set up everything.
        else:
            self.should_run = True

            # Prepare the SQL configuration
            name = 'Test.Connection'

            config = {
                'name': name,
                'is_active': True,
                'engine': 'mysql+pymysql',
                'fs_sql_config': {},
                'ping_query': 'select 1+1',
                'host': os.environ['ZATO_ODB_HOST'],
                'port': os.environ['ZATO_ODB_PORT'],
                'username': os.environ['ZATO_ODB_USERNAME'],
                'password': os.environ['ZATO_ODB_PASSWORD'],
                database: database,
            }

            self.store = PoolStore()
            self.store[name] = config

            self.odb = SessionWrapper()
            self.odb.init_session(name, config, self.store[name].pool)
            self.odb.pool.ping({})

# ################################################################################################################################

    def test_sql_publish_with_retry(self):

        # Skip the test if we are not to run.
        if not self.should_run:
            return

        # If we are here, it means that we can proceed.
        pass

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
