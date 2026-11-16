# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture
from zato.common.test.exactly_once.config import TestConfig
from zato.common.test.exactly_once.control import create_control_dir, Env_Dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import logging
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.typing_ import anydict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

_current_dir = os.path.dirname(__file__)

_template_path   = os.path.join(_current_dir, '_enmasse_template.yaml')
_services_source = os.path.join(_current_dir, '_services.py')

_publisher_username = 'test.exactly-once.publisher'
_reader_username    = 'test.exactly-once.reader'
_orders_username    = 'test.exactly-once.orders'
_verifier_username  = 'test.exactly-once.verifier'

# The lease of a pulled message, in seconds
_extra_server_env:'strstrdict' = {
    'Zato_PubSub_Pull_Lease_Seconds': '2',
}

# ################################################################################################################################
# ################################################################################################################################

def _build_config(
    state:'SessionState',
    logger:'logging.Logger',
    zato_bin:'str',
    server_port:'int',
    invoke_password:'str',
    ) -> 'anydict':

    # The control files of the relay are shared by the server and the test process ..
    control_dir = tempfile.mkdtemp(prefix='zato_pubsub_exactly_once_control_')
    create_control_dir(control_dir)
    os.environ[Env_Dir] = control_dir
    state.test_data_directory = control_dir

    # .. and the test process reads the lease that the server uses.
    os.environ.update(_extra_server_env)

    placeholders:'strstrdict' = {
        'publisher_password':    'test.publisher.' + CryptoManager.generate_hex_string(),
        'reader_password':       'test.reader.'    + CryptoManager.generate_hex_string(),
        'orders_password':       'test.orders.'    + CryptoManager.generate_hex_string(),
        'verifier_password':     'test.verifier.'  + CryptoManager.generate_hex_string(),
        'relay_delivery_active': 'true',
    }

    def _populate(
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
        ) -> 'None':

        TestConfig.base_url         = f'http://{host}:{server_port}'
        TestConfig.password         = invoke_password
        TestConfig.server_directory = server_directory
        TestConfig.server_port      = server_port
        TestConfig.zato_bin         = zato_bin

        TestConfig.template_path    = _template_path
        TestConfig.placeholders     = placeholders
        TestConfig.extra_server_env = _extra_server_env

        TestConfig.session_state = state
        TestConfig.logger        = logger

        TestConfig.publisher_username = _publisher_username
        TestConfig.publisher_password = placeholders['publisher_password']

        TestConfig.reader_username = _reader_username
        TestConfig.reader_password = placeholders['reader_password']

        TestConfig.orders_username = _orders_username
        TestConfig.orders_password = placeholders['orders_password']

        TestConfig.verifier_username = _verifier_username
        TestConfig.verifier_password = placeholders['verifier_password']

    out:'anydict' = {
        'placeholders': placeholders,
        'populate_callback': _populate,
        'hot_deploy_sources': [_services_source],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

zato_server = create_zato_server_fixture(
    logger_name='zato.test.pubsub_exactly_once.conftest',
    server_log_copy_name='server-logs-pubsub-exactly-once.txt',
    template_path=_template_path,
    quickstart_prefix='zato_pubsub_exactly_once_qs_',
    extra_server_env=_extra_server_env,
    patch_server_conf_bind=True,
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################
