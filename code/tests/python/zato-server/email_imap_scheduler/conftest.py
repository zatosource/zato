# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# pytest
import pytest

# Zato
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture

# Local test helpers
from _config import TestConfig
from _imap_test_server import IMAPTestServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import logging
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

def _build_config(
    state:'SessionState',
    logger:'logging.Logger',
    zato_bin:'str',
    server_port:'int',
    invoke_password:'str',
) -> 'anydict':

    def _populate(
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
    ) -> 'None':
        TestConfig.host = host
        TestConfig.server_port = server_port
        TestConfig.invoke_password = invoke_password
        TestConfig.server_directory = server_directory

    out:'anydict' = {
        'placeholders': {},
        'populate_callback': _populate,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

zato_server = create_zato_server_fixture(
    logger_name='zato.test.email_imap_scheduler.conftest',
    server_log_copy_name='server-logs-email-imap-scheduler.txt',
    template_path='',
    quickstart_prefix='zato_imap_scheduler_qs_',
    extra_server_env={},
    patch_server_conf_bind=True,
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def imap_test_server() -> 'any_':
    server = IMAPTestServer()
    server.start()
    yield server
    server.stop()

# ################################################################################################################################
# ################################################################################################################################
