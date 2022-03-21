# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Run gevent patches first
from gevent.monkey import patch_all
patch_all()

# stdlib
from unittest import TestCase

# Bunch
from bunch import Bunch

# Zato
from zato.common.api import PUBSUB
from zato.common.util.time_ import utcnow_as_ms
from zato.server.pubsub import PubSub

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

class TestServer:
    def __init__(self) -> 'None':

        self.name = 'TestServerObject'
        self.pid = 9988

        self.fs_server_config = Bunch()
        self.fs_server_config.pubsub = Bunch()
        self.fs_server_config.pubsub_meta_topic = Bunch()
        self.fs_server_config.pubsub_meta_endpoint_pub = Bunch()

        self.fs_server_config.pubsub.data_prefix_len = 9999
        self.fs_server_config.pubsub.data_prefix_short_len = 123
        self.fs_server_config.pubsub.log_if_deliv_server_not_found = True
        self.fs_server_config.pubsub.log_if_wsx_deliv_server_not_found = False

        self.fs_server_config.pubsub_meta_topic.enabled = True
        self.fs_server_config.pubsub_meta_topic.store_frequency = 1

        self.fs_server_config.pubsub_meta_endpoint_pub.enabled = True
        self.fs_server_config.pubsub_meta_endpoint_pub.store_frequency = 1
        self.fs_server_config.pubsub_meta_endpoint_pub.data_len = 1234
        self.fs_server_config.pubsub_meta_endpoint_pub.max_history = 111

        self.ctx = []

# ################################################################################################################################

    def invoke(self, service:'any_', request:'any_') -> 'None':
        self.ctx.append({
            'service': service,
            'request': request,
        })

# ################################################################################################################################
# ################################################################################################################################

class TriggerNotifyPubSubTasksTestCase(TestCase):

    def test_max_pub_time_both_gd_and_non_gd(self):

        cid = '987'
        cluster_id = 123
        server = TestServer()
        broker_client = None

        sub_key = 'sk.123'
        topic_id = 222
        topic_name = '/my.topic'
        endpoint_id = 1
        ws_channel_id = 2
        cluster_id = 12345
        endpoint_type = PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id

        topic_config = {
            'id': topic_id,
            'name': topic_name,
            'is_active': True,
            'is_internal': False,
            'max_depth_gd': 111,
            'max_depth_non_gd': 222,
            'has_gd': True,
            'depth': 0,
            'depth_check_freq': 1,
            'pub_buffer_size_gd': 1,
            'task_delivery_interval': 1,
            'task_sync_interval': 1,
        }

        sub_config = {
            'id': 555,
            'sub_key': sub_key,
            'topic_id': topic_id,
            'topic_name': topic_name,
            'ws_channel_id': ws_channel_id,
            'ext_client_id': 'my.ext.1',
            'endpoint_id': endpoint_id,
            'sub_pattern_matched': '/*',
            'task_delivery_interval': 0.1,
            'unsub_on_wsx_close': True,
            'creation_time': 123456,
        }

        sk_server_config = {
            'cluster_id': cluster_id,
            'server_name': server.name,
            'server_pid': server.pid,
            'sub_key': sub_key,
            'endpoint_id': endpoint_id,
            'endpoint_type': endpoint_type,
        }

        endpoint_config = {
            'id': endpoint_id,
            'ws_channel_id': ws_channel_id,
            'name': 'my.endpoint',
            'endpoint_type': endpoint_type,
            'role': PUBSUB.ROLE.PUBLISHER_SUBSCRIBER.id,
            'is_active': True,
            'is_internal': True,
            'security_id': None,
        }

        sync_max_iters = 1
        spawn_trigger_notify = False
        now = utcnow_as_ms()

        ps = PubSub(
            cluster_id,
            server, # type: ignore
            broker_client,
            sync_max_iters=sync_max_iters,
            spawn_trigger_notify=spawn_trigger_notify)

        ps.create_topic_object(topic_config)
        ps.create_endpoint(endpoint_config)
        ps.add_subscription(sub_config)
        ps.set_sub_key_server(sk_server_config)

        # Set a flag to signal that a GD message is available
        ps.set_sync_has_msg(
            topic_id = topic_id,
            is_gd = True,
            value = True,
            source = 'test_max_pub_time_both_gd_and_non_gd',
            gd_pub_time_max = now
        )

        # Store a minimal list of non-GD messages
        sub_keys = [sub_key]
        non_gd_msg_list = [333]
        ps.store_in_ram(cid, topic_id, topic_name, sub_keys, non_gd_msg_list)

        ps.trigger_notify_pubsub_tasks()

        print(111, server.ctx)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    from unittest import main
    main()

# ################################################################################################################################
# ################################################################################################################################
