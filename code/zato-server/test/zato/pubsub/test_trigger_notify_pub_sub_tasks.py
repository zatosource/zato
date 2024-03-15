# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Run gevent patches first
from gevent.monkey import patch_all
patch_all()

# stdlib
from unittest import TestCase

# Zato
from zato.common.api import PUBSUB
from zato.common.test import TestServer
from zato.server.pubsub import PubSub

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

class TriggerNotifyPubSubTasksTestCase(TestCase):

    def _run_sync(
        self,
        needs_gd:'bool',
        needs_non_gd:'bool',
        gd_pub_time_max:'float',
        non_gd_pub_time:'float',
    ) -> 'stranydict':

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

        # This is used by the one-element non-GD messages
        non_gd_pub_msg_id = 'aaa.bbb.111'
        non_gd_expiration_time = 123456789123456789

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

        # Optionally, set a flag to signal that a GD message is available
        if needs_gd:
            ps.set_sync_has_msg(
                topic_id = topic_id,
                is_gd = True,
                value = True,
                source = 'test_max_pub_time_both_gd_and_non_gd',
                gd_pub_time_max = gd_pub_time_max
            )

        # Optionally, store a minimal list of non-GD messages
        if needs_non_gd:
            sub_keys = [sub_key]
            non_gd_msg_list = [{
                'pub_msg_id': non_gd_pub_msg_id,
                'pub_time': non_gd_pub_time,
                'expiration_time': non_gd_expiration_time
            }]
            ps.store_in_ram(cid, topic_id, topic_name, sub_keys, non_gd_msg_list)

        # Trigger a sync call ..
        ps.trigger_notify_pubsub_tasks()

        # .. and return the dictionary with context data to our caller.
        return server.ctx

# ################################################################################################################################

    def test_pub_max_time_gd_only(self):

        # Only GD max. pub time is given on input and we do not have
        # any non-GD messages so we expect for the GD max. pub time
        # to be returned in the ctx information.

        needs_gd     = True
        needs_non_gd = False

        gd_pub_time_max = 2.0
        non_gd_pub_time = 1.0

        ctx = self._run_sync(needs_gd, needs_non_gd, gd_pub_time_max, non_gd_pub_time)

        pub_time_max = ctx['request']['pub_time_max']
        self.assertEqual(pub_time_max, gd_pub_time_max)

# ################################################################################################################################

    def test_pub_max_time_non_gd_only(self):

        # Only non-GD pub time is given on input and we do not have
        # any GD messages so we expect for the non-GD pub time
        # to be returned in the ctx information.

        needs_gd     = False
        needs_non_gd = True

        gd_pub_time_max = 2.0
        non_gd_pub_time = 1.0

        ctx = self._run_sync(needs_gd, needs_non_gd, gd_pub_time_max, non_gd_pub_time)

        pub_time_max = ctx['request']['pub_time_max']
        self.assertEqual(pub_time_max, non_gd_pub_time)

# ################################################################################################################################

    def test_pub_max_time_gd_is_greater(self):

        # Both GD and non-GD are provided and the former is greater
        # which is why we expect for it to form pub_time_max.

        needs_gd     = True
        needs_non_gd = True

        gd_pub_time_max = 2.0
        non_gd_pub_time = 1.0

        ctx = self._run_sync(needs_gd, needs_non_gd, gd_pub_time_max, non_gd_pub_time)

        pub_time_max = ctx['request']['pub_time_max']
        self.assertEqual(pub_time_max, gd_pub_time_max)

# ################################################################################################################################

    def test_pub_max_time_non_gd_is_greater(self):

        # Both GD and non-GD are provided and the latter is greater
        # which is why we expect for it to form pub_time_max.

        needs_gd     = True
        needs_non_gd = True

        gd_pub_time_max = 2.0
        non_gd_pub_time = 3.0

        ctx = self._run_sync(needs_gd, needs_non_gd, gd_pub_time_max, non_gd_pub_time)

        pub_time_max = ctx['request']['pub_time_max']
        self.assertEqual(pub_time_max, non_gd_pub_time)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    from unittest import main
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
