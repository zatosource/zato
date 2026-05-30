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
    from zato.common.typing_ import any_, anydict, strstrdict

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

    publisher_password = 'test.pub.' + os.urandom(8).hex()
    puller_a_password  = 'test.pull.a.' + os.urandom(8).hex()
    pusher_a_password  = 'test.push.a.' + os.urandom(8).hex()

    placeholders:'strstrdict' = {
        'publisher_password': publisher_password,
        'puller_a_password': puller_a_password,
        'pusher_a_password': pusher_a_password,
    }

    def _populate(
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
    ) -> 'None':
        from zato.common.test.config_pubsub_clear_queue_combined import TestConfig

        TestConfig.base_url           = f'http://{host}:{server_port}'
        TestConfig.invoke_password    = invoke_password
        TestConfig.publisher_username = 'test.pubsub.publisher'
        TestConfig.publisher_password = publisher_password
        TestConfig.puller_a_username  = 'test.pubsub.puller.a'
        TestConfig.puller_a_password  = puller_a_password
        TestConfig.pusher_a_username  = 'test.pubsub.pusher.a'
        TestConfig.pusher_a_password  = pusher_a_password
        TestConfig.server_directory   = server_directory

    out:'anydict' = {
        'placeholders': placeholders,
        'populate_callback': _populate,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

zato_server = create_zato_server_fixture(
    logger_name='zato.test.pubsub_clear_queue_combined.conftest',
    server_log_copy_name='server-logs-clear-queue-combined.txt',
    template_path=_template_path,
    quickstart_prefix='zato_clear_queue_combined_qs_',
    extra_server_env={'Zato_Stream_Max_Len': '3'},
    patch_server_conf_bind=False,
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################
