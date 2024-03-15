# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# ################################################################################################################################
# ################################################################################################################################

class TestConfig:

    # This is a shared topic with multiple subscribers
    pubsub_topic_shared = '/zato/demo/sample'

    # This is a different shared topic
    pubsub_topic_test = '/zato/test/sample'

    # This topic has only one subscriber
    pubsub_topic_name_unique = '/zato/demo/unique'

    # Tests will create topics with this pattern - note the trailing dot.
    pubsub_topic_name_unique_auto_create = '/zato/demo/unique.'

    # Tests will also create topics with alsothis pattern - note the trailing dot.
    pubsub_topic_name_perf_auto_create = '/test-perf.'

    default_stdout = b'(None)\n'

    current_app = 'CRM'
    super_user_name = 'zato.unit-test.admin1'
    super_user_password = 'hQ9nl93UDqGus'
    super_user_totp_key = 'KMCLCWN4YPMD2WO3'

    username_prefix = 'test.{}+{}'
    random_prefix = 'rand.{}+{}'

    server_address  = 'http://localhost:17010{}'
    server_location = os.path.expanduser('~/env/qs-1/server1')

    scheduler_host = 'localhost'
    scheduler_port = 31530

    scheduler_address  = 'http://{}:{}{{}}'.format(scheduler_host, scheduler_port)
    scheduler_location = os.path.expanduser('~/env/qs-1/scheduler')

    invalid_base_address = '<invalid-base-address>'

# ################################################################################################################################
# ################################################################################################################################
