# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.common.test import TestServer
from zato.common.typing_ import cast_
from zato.server.pubsub import PubSub, Topic
from zato.server.pubsub.publisher import PubCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylistnone
    from zato.server.base.parallel import ParallelServer
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

cluster_id = 1
test_server = TestServer()

topic_config = {}
topic_config['server_name'] = test_server.name
topic_config['server_pid'] = test_server.pid
topic_config['id'] = 1
topic_config['name'] = 'My Topic'
topic_config['is_active'] = True
topic_config['is_internal'] = True
topic_config['max_depth_gd'] = 111
topic_config['max_depth_non_gd'] = 222
topic_config['has_gd'] = True
topic_config['depth_check_freq'] = 333
topic_config['pub_buffer_size_gd'] = 444
topic_config['task_delivery_interval'] = 555
topic_config['meta_store_frequency'] = 666
topic_config['task_sync_interval'] = 777

topic = Topic(topic_config, test_server.name, test_server.pid)

# ################################################################################################################################
# ################################################################################################################################

def my_service_invoke_func():
    pass

def my_new_session_func():
    pass

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    cid = '123'
    cluster_id = cluster_id
    pubsub = PubSub(cluster_id, cast_('ParallelServer', test_server))
    topic = topic
    endpoint_id = 1
    endpoint_name = 'My Endpoint'
    subscriptions_by_topic = []
    msg_id_list = []
    pub_pattern_matched = '/*'
    ext_client_id = 'abc'
    is_first_run = False
    now = 1.0
    is_wsx = True
    service_invoke_func = my_service_invoke_func
    new_session_func = my_new_session_func

# ################################################################################################################################
# ################################################################################################################################

class PublisherCtxTestCase(TestCase):

    def _get_test_ctx(self, gd_msg_list:'anylistnone', non_gd_msg_list:'anylistnone') -> 'PubCtx':

        ctx = PubCtx(
            cid = ModuleCtx.cid,
            cluster_id = ModuleCtx.cluster_id,
            pubsub = ModuleCtx.pubsub,
            topic = ModuleCtx.topic,
            endpoint_id = ModuleCtx.endpoint_id,
            endpoint_name = ModuleCtx.endpoint_name,
            subscriptions_by_topic = ModuleCtx.subscriptions_by_topic,
            msg_id_list = ModuleCtx.msg_id_list,
            pub_pattern_matched = ModuleCtx.pub_pattern_matched,
            ext_client_id = ModuleCtx.ext_client_id,
            is_first_run = ModuleCtx.is_first_run,
            now = ModuleCtx.now,
            is_wsx = ModuleCtx.is_wsx,
            service_invoke_func = ModuleCtx.service_invoke_func,
            new_session_func = ModuleCtx.new_session_func,

            gd_msg_list = cast_('list', gd_msg_list),
            non_gd_msg_list = cast_('list', non_gd_msg_list),
        )

        return ctx

# ################################################################################################################################

    def test_msg_id_lists_are_none(self):

        # We do not provide any list on input
        gd_msg_list = None
        non_gd_msg_list = None

        with self.assertRaises(ValueError) as cm:
            self._get_test_ctx(gd_msg_list, non_gd_msg_list)

        # Extract the exception ..
        exception = cm.exception

        # .. and run the assertions now.

        self.assertIs(type(exception), ValueError)
        self.assertEqual(str(exception), 'At least one of gd_msg_list or non_gd_msg_list must be provided')

# ################################################################################################################################

    def test_msg_id_gd_msg_list_is_none(self):

        # One of the elements is a list, but an empty one
        gd_msg_list = []
        non_gd_msg_list = None

        with self.assertRaises(ValueError) as cm:
            self._get_test_ctx(gd_msg_list, non_gd_msg_list)

        # Extract the exception ..
        exception = cm.exception

        # .. and run the assertions now.

        self.assertIs(type(exception), ValueError)
        self.assertEqual(str(exception), 'At least one of gd_msg_list or non_gd_msg_list must be provided')

# ################################################################################################################################

    def test_msg_id_non_gd_msg_list_is_none(self):

        # Another of the elements is a list, but an empty one
        gd_msg_list = None
        non_gd_msg_list = []

        with self.assertRaises(ValueError) as cm:
            self._get_test_ctx(gd_msg_list, non_gd_msg_list)

        # Extract the exception ..
        exception = cm.exception

        # .. and run the assertions now.

        self.assertIs(type(exception), ValueError)
        self.assertEqual(str(exception), 'At least one of gd_msg_list or non_gd_msg_list must be provided')

# ################################################################################################################################

    def test_msg_id_both_lists_are_empty(self):

        # Both elements are lists but both are empty
        gd_msg_list = []
        non_gd_msg_list = []

        with self.assertRaises(ValueError) as cm:
            self._get_test_ctx(gd_msg_list, non_gd_msg_list)

        # Extract the exception ..
        exception = cm.exception

        # .. and run the assertions now.

        self.assertIs(type(exception), ValueError)
        self.assertEqual(str(exception), 'At least one of gd_msg_list or non_gd_msg_list must be provided')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    from unittest import main
    main()

# ################################################################################################################################
# ################################################################################################################################
