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
from zato.common.util.time_ import utcnow_as_ms
from zato.server.pubsub import PubSub

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

class TestServer:
    def __init__(self):
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

# ################################################################################################################################
# ################################################################################################################################

class TriggerNotifyPubSubTasksTestCase(TestCase):

    def test_max_pub_time_both_gd_and_non_gd(self):

        cluster_id = 123
        server = TestServer()
        broker_client = None

        sync_max_iters = 1
        spawn_trigger_notify = False

        topic_id = 222
        now = utcnow_as_ms()

        ps = PubSub(
            cluster_id,
            server, # type: ignore
            broker_client,
            sync_max_iters=sync_max_iters,
            spawn_trigger_notify=spawn_trigger_notify)

        # Set a flag to signal that a GD message is available
        ps.set_sync_has_msg(
            topic_id = topic_id,
            is_gd = True,
            value = True,
            source = 'test_max_pub_time_both_gd_and_non_gd',
            gd_pub_time_max = now
        )

        ps.trigger_notify_pubsub_tasks()

        ps

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    from unittest import main
    main()

# ################################################################################################################################
# ################################################################################################################################
