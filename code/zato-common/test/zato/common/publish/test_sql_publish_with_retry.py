# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from contextlib import closing
from unittest import main, TestCase

# Zato
from zato.common.odb.api import PoolStore, SessionWrapper
from zato.common.odb.query.pubsub.publish import sql_publish_with_retry

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import dictlist

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
                'db_name': database,
            }

            self.store = PoolStore()
            self.store[name] = config

            self.odb = SessionWrapper()
            self.odb.init_session(name, config, self.store[name].pool)
            self.odb.pool.ping({})

# ################################################################################################################################

    def get_gd_msg_list(self) -> 'dictlist':
        out = []
        return out

# ################################################################################################################################

    def test_sql_publish_with_retry(self):

        # Skip the test if we are not to run.
        if not self.should_run:
            return

        # If we are here, it means that we can proceed.

        now = 1.0
        cid = 'abc'

        topic_id = 1234
        topic_name = '/test-sql-publish-with-retry-1'

        cluster_id = 1
        pub_counter = 1

        new_session_func = self.odb.session

        gd_msg_list = self.get_gd_msg_list()
        subscriptions_by_topic = []

        with closing(self.odb.session()) as session:

            publish_with_retry_manager = sql_publish_with_retry(
                now,
                cid,
                topic_id,
                topic_name,
                cluster_id,
                pub_counter,
                session,
                new_session_func,
                gd_msg_list,
                subscriptions_by_topic
            )

            publish_with_retry_manager

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
