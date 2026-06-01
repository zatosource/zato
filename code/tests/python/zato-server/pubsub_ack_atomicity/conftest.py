# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import logging
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.typing_ import anydict, anylist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

_template_path = os.path.join(os.path.dirname(__file__), '_enmasse_template.yaml')

# ################################################################################################################################
# ################################################################################################################################

def _build_config(
    state:'SessionState',
    logger:'logging.Logger',
    zato_bin:'str',
    server_port:'int',
    invoke_password:'str',
) -> 'anydict':

    from redis import Redis
    from zato.common.api import PubSub

    # .. flush the test Redis DB to remove stale data from previous runs ..
    redis_conn = Redis(host='localhost', port=6379, db=PubSub.Test_Redis_DB, decode_responses=True)
    _ = redis_conn.flushdb()
    redis_conn.close()

    publisher_password = 'test.pub.' + os.urandom(8).hex()
    puller_a_password  = 'test.pull.a.' + os.urandom(8).hex()
    puller_b_password  = 'test.pull.b.' + os.urandom(8).hex()

    placeholders:'strstrdict' = {
        'publisher_password': publisher_password,
        'puller_a_password': puller_a_password,
        'puller_b_password': puller_b_password,
    }

    def _populate(
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
    ) -> 'None':
        from zato.common.test.client import AdminClient
        from zato.common.test.config_pubsub_ack_atomicity import TestConfig

        TestConfig.base_url           = f'http://{host}:{server_port}'
        TestConfig.invoke_password    = invoke_password
        TestConfig.publisher_username = 'test.pubsub.ack.publisher'
        TestConfig.publisher_password = publisher_password
        TestConfig.puller_a_username  = 'test.pubsub.ack.puller.a'
        TestConfig.puller_a_password  = puller_a_password
        TestConfig.puller_b_username  = 'test.pubsub.ack.puller.b'
        TestConfig.puller_b_password  = puller_b_password
        TestConfig.server_directory   = server_directory

        # .. look up the puller_a sec_base_id for subscription re-creation ..
        admin = AdminClient(TestConfig.base_url, invoke_password)
        sec_list = admin.invoke('zato.security.get-list', {'cluster_id': 1})

        if isinstance(sec_list, list):
            sec_items:'anylist' = sec_list
        else:
            sec_items = sec_list['zato_security_get_list_response']

        for sec_item in sec_items:
            if sec_item['name'] == TestConfig.puller_a_username:
                TestConfig.puller_a_sec_base_id = sec_item['id']
                break

    out:'anydict' = {
        'placeholders': placeholders,
        'populate_callback': _populate,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

zato_server = create_zato_server_fixture(
    logger_name='zato.test.pubsub_ack_atomicity.conftest',
    server_log_copy_name='server-logs-ack-atomicity.txt',
    template_path=_template_path,
    quickstart_prefix='zato_ack_atomicity_qs_',
    extra_server_env={},
    patch_server_conf_bind=False,
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################
