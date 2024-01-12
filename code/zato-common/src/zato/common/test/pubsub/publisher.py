# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""
# Zato
from zato.common.test import TestServer
from zato.common.typing_ import cast_
from zato.server.pubsub import PubSub, Topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
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

class PublisherTestData:

    cid = '123'
    cluster_id = cluster_id
    server = test_server
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
