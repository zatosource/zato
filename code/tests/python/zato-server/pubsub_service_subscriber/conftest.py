# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.crypto.api import CryptoManager
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
_services_source = os.path.join(os.path.dirname(__file__), '_services.py')

_publisher_username = 'test.pubsub.service-subscriber.publisher'

# ################################################################################################################################
# ################################################################################################################################

def _build_config(
    state:'SessionState',
    logger:'logging.Logger',
    zato_bin:'str',
    server_port:'int',
    invoke_password:'str',
) -> 'anydict':

    publisher_password = 'test.pub.' + CryptoManager.generate_hex_string()

    placeholders:'strstrdict' = {
        'publisher_password': publisher_password,
    }

    def _populate(
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
    ) -> 'None':
        from zato.common.test.config_pubsub_service_subscriber import TestConfig

        TestConfig.base_url           = f'http://{host}:{server_port}'
        TestConfig.password           = invoke_password
        TestConfig.server_directory   = server_directory
        TestConfig.zato_bin           = zato_bin
        TestConfig.publisher_username = _publisher_username
        TestConfig.publisher_password = publisher_password

    out:'anydict' = {
        'placeholders': placeholders,
        'populate_callback': _populate,
        'hot_deploy_sources': [_services_source],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

zato_server = create_zato_server_fixture(
    logger_name='zato.test.pubsub_service_subscriber.conftest',
    server_log_copy_name='server-logs-pubsub-service-subscriber.txt',
    template_path=_template_path,
    quickstart_prefix='zato_pubsub_service_subscriber_qs_',
    extra_server_env={},
    patch_server_conf_bind=True,
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################
