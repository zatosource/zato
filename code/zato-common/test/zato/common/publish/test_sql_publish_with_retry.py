# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from contextlib import closing
from unittest import main

# Zato
from zato.common.api import PUBSUB
from zato.common.odb.api import PoolStore, SessionWrapper
from zato.common.odb.model import PubSubSubscription
from zato.common.odb.query.pubsub.publish import PublishWithRetryManager, sql_publish_with_retry
from zato.common.test import CommandLineTestCase
from zato.common.test.wsx_ import WSXChannelManager
from zato.common.typing_ import cast_
from zato.common.util.api import fs_safe_now
from zato.common.util.time_ import utcnow_as_ms
from zato.server.pubsub import Subscription

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import Column
    from zato.common.typing_ import anydict, callable_, callnone, dictlist, strlist
    Column = Column

# ################################################################################################################################
# ################################################################################################################################

PubSubSubscriptionTable  = PubSubSubscription.__table__
PubSubSubscriptionDelete = PubSubSubscriptionTable.delete

# ################################################################################################################################
# ################################################################################################################################

class SQLPublishWithRetryTestCase(CommandLineTestCase):

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

    def get_gd_msg_list(
        self,
        topic_name:'str',
        topic_id:'int',
        sub_key:'str',
        pubsub_endpoint_id:'int',
        ext_client_id:'str',
    ) -> 'dictlist':

        return [{
            'cluster_id': 1,
            'data': 'abc',
            'data_prefix': 'abc',
            'data_prefix_short': 'abc',
            'deliver_to_sk': [],
            'delivery_count': 0,
            'delivery_status': '2',
            'expiration': 2,
            'expiration_time': 3.1,
            'expiration_time_iso': '',
            'ext_client_id': ext_client_id,
            'ext_pub_time': '0.9',
            'ext_pub_time_iso': '',
            'group_id': '',
            'has_gd': True,
            'in_reply_to': '',
            'is_in_sub_queue': True,
            'mime_type': 'text/plain',
            'position_in_group': 1,
            'pub_correl_id': '',
            'pub_msg_id': 'zpsm001',
            'pub_pattern_matched': 'pub=/*',
            'pub_time': '1.1',
            'pub_time_iso': '',
            'published_by_id': pubsub_endpoint_id,
            'recv_time': 1.0,
            'recv_time_iso': '',
            'reply_to_sk': [],
            'server_name': '',
            'server_pid': 0,
            'size': 3,
            'sub_key': '',
            'sub_pattern_matched': {sub_key: 'sub=/*'},
            'topic_id': topic_id,
            'topic_name': topic_name,
            'zato_ctx': '{\n\n}'
        }]

# ################################################################################################################################

    def create_sql_sub(
        self,
        new_session_func:'callable_',
        pubsub_endpoint_id:'int',
        sub_key:'str',
        topic_id:'int'
    ) -> 'anydict':

        with closing(new_session_func()) as session:

            sub = PubSubSubscription()

            sub.sub_key = sub_key
            sub.endpoint_id = pubsub_endpoint_id
            sub.topic_id = topic_id
            sub.creation_time = utcnow_as_ms()
            sub.sub_pattern_matched = 'sub=/*'
            sub.is_durable = True
            sub.has_gd = True
            sub.active_status = PUBSUB.QUEUE_ACTIVE_STATUS.FULLY_ENABLED.id
            sub.is_staging_enabled = False
            sub.delivery_method = PUBSUB.DELIVERY_METHOD.NOTIFY.id
            sub.delivery_data_format = 'text/plain'
            sub.wrap_one_msg_in_list = True
            sub.delivery_max_size = 111
            sub.delivery_max_retry = 1
            sub.delivery_err_should_block = False
            sub.wait_sock_err = 1
            sub.wait_non_sock_err = 1

            session.add(sub)
            session.commit()

            dict_info = sub.asdict()

        return dict_info

# ################################################################################################################################

    def _run_test(self, before_queue_insert_func:'callnone', should_collect_ctx:'bool') -> 'PublishWithRetryManager':

        # If we are here, it means that we can proceed.

        now_safe = fs_safe_now()

        topic_name = f'/wsx.pubsub.test.{now_safe}.1'
        topics = [topic_name]

        with WSXChannelManager(self, needs_pubsub=True, run_cli=True, topics=topics) as ctx:

            now = 1.0
            cid = 'cid.zxc'
            sub_key = f'zpsk.{now_safe}'
            cluster_id = 1
            pub_counter = 1
            ext_client_id = 'ext.client.id.1'

            new_session_func = self.odb.session

            topic_id = ctx.topic_name_to_id[topic_name]
            gd_msg_list = self.get_gd_msg_list(topic_name, topic_id, sub_key, ctx.pubsub_endpoint_id, ext_client_id)
            subscriptions_by_topic = []

            with closing(self.odb.session()) as session:

                sub_info = self.create_sql_sub(
                    new_session_func,
                    ctx.pubsub_endpoint_id,
                    sub_key,
                    topic_id
                )

                sub_info['topic_name'] = topic_name
                sub_info['task_delivery_interval'] = 1
                sub_info['ext_client_id'] = ext_client_id

                sub = Subscription(sub_info)
                subscriptions_by_topic.append(sub)

                publish_with_retry_manager = sql_publish_with_retry(
                    now = now,
                    cid = cid,
                    topic_id = topic_id,
                    topic_name = topic_name,
                    cluster_id = cluster_id,
                    pub_counter = pub_counter,
                    session = session,
                    new_session_func = new_session_func,
                    before_queue_insert_func = before_queue_insert_func,
                    gd_msg_list = gd_msg_list,
                    subscriptions_by_topic = subscriptions_by_topic,
                    should_collect_ctx = should_collect_ctx,
                )

        return publish_with_retry_manager

# ################################################################################################################################

    def test_sql_publish_with_retry_no_updates_no_context(self):

        # Skip the test if we are not to run.
        if not self.should_run:
            return

        # In this test, we do not update the subscription list at all,
        # assuming rather that everything should be published as it is given on input.
        before_queue_insert_func = None
        should_collect_ctx = False

        # Run the test ..
        publish_with_retry_manager = self._run_test(before_queue_insert_func, should_collect_ctx)

        # .. and confirm the result.
        self.assertListEqual(publish_with_retry_manager.ctx_history, [])

# ################################################################################################################################

    def test_sql_publish_with_retry_no_updates_collect_ctx(self):

        # Skip the test if we are not to run.
        if not self.should_run:
            return

        # In this test, we do not update the subscription list at all, but we collect context information.
        before_queue_insert_func = None
        should_collect_ctx = True

        # Run the test ..
        publish_with_retry_manager = self._run_test(before_queue_insert_func, should_collect_ctx)

        # .. and confirm the result.
        self.assertListEqual(publish_with_retry_manager.ctx_history, ['Counter -> 1:1', 'Result -> True'])

# ################################################################################################################################

    def test_sql_publish_with_retry_one_sub_delete_sub(self):

        # Skip the test if we are not to run.
        if not self.should_run:
            return

        def _before_queue_insert_func(
            publish_with_retry_manager:'PublishWithRetryManager',
            sub_keys_by_topic:'strlist'
        ) -> 'None':

            session = publish_with_retry_manager.new_session_func()
            session.execute(
                PubSubSubscriptionDelete().\
                where(cast_('Column', PubSubSubscription.sub_key).in_(sub_keys_by_topic))
            )
            session.commit()

        # In this test, we update the subscription list and we collect context information.
        before_queue_insert_func = _before_queue_insert_func
        should_collect_ctx = True

        # Run the test ..
        publish_with_retry_manager = self._run_test(before_queue_insert_func, should_collect_ctx)

        # .. and confirm the result.
        self.assertListEqual(publish_with_retry_manager.ctx_history,
            ['Counter -> 1:1', 'Result -> False', 'Queue insert OK -> False', 'Sub by topic -> []',
             'Counter -> 1:2', 'Result -> True'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    log_level = logging.INFO
    log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=log_level, format=log_format)

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
