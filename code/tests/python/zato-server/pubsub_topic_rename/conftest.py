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
    from zato.common.typing_ import anydict, strstrdict

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

    publisher_password  = 'test.pub.' + os.urandom(8).hex()
    subscriber_password = 'test.sub.' + os.urandom(8).hex()

    placeholders:'strstrdict' = {
        'publisher_password': publisher_password,
        'subscriber_password': subscriber_password,
    }

    def _populate(
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
    ) -> 'None':
        from zato.common.test.config_pubsub_topic_rename import TestConfig

        TestConfig.base_url            = f'http://{host}:{server_port}'
        TestConfig.invoke_password     = invoke_password
        TestConfig.publisher_username  = 'test.rename.publisher'
        TestConfig.publisher_password  = publisher_password
        TestConfig.subscriber_username = 'test.rename.subscriber'
        TestConfig.subscriber_password = subscriber_password
        TestConfig.server_directory    = server_directory
        TestConfig.zato_bin            = zato_bin

    out:'anydict' = {
        'placeholders': placeholders,
        'populate_callback': _populate,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

zato_server = create_zato_server_fixture(
    logger_name='zato.test.pubsub_topic_rename.conftest',
    server_log_copy_name='server-logs-pubsub-topic-rename.txt',
    template_path=_template_path,
    quickstart_prefix='zato_pubsub_topic_rename_qs_',
    extra_server_env={},
    patch_server_conf_bind=True,
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################
