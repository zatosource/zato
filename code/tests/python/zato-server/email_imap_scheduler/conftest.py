# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile

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

# Source code of the services that the tests point IMAP connections to. The first one records each message
# it receives in the evidence file and marks it as seen, the second one always raises so that tests can confirm
# that messages are not marked as seen when the target service fails.
_test_services_template = '''# -*- coding: utf-8 -*-

# stdlib
from json import dumps

# Zato
from zato.server.service import Service

_evidence_file = '{evidence_file}'

class StoreIMAPMessage(Service):
    """ Records each IMAP message received on input and marks it as seen.
    """
    name = '{service_store_message}'

    def handle(self):

        # The dispatch service hands us the message object itself
        message = self.request.raw_request

        uid = message.uid.decode('utf-8')
        sent_from = message.data.sent_from[0]['email']
        body = message.data.body['plain'][0]

        line = dumps({{
            'uid': uid,
            'subject': message.data.subject,
            'sent_from': sent_from,
            'body': body,
        }})

        # Record the message first ..
        with open(_evidence_file, 'a') as evidence:
            _ = evidence.write(line + '\\n')

        # .. and mark it as seen only afterwards, so a failed write leaves it available for a retry.
        message.mark_seen()

class AlwaysRaiseIMAPMessage(Service):
    """ Fails on purpose, without marking the input message as seen.
    """
    name = '{service_always_raise}'

    def handle(self):
        raise Exception('This service always raises an error for IMAP message tests')
'''

# ################################################################################################################################
# ################################################################################################################################

def _build_config(
    state:'SessionState',
    logger:'logging.Logger',
    zato_bin:'str',
    server_port:'int',
    invoke_password:'str',
) -> 'anydict':

    # A directory for the evidence file and the generated source code of the test services
    work_directory = tempfile.mkdtemp(prefix='zato_imap_scheduler_work_')

    evidence_file = os.path.join(work_directory, 'imap-messages.jsonl')
    TestConfig.evidence_file = evidence_file

    # Render the test services with the evidence file path embedded ..
    source = _test_services_template.format(
        evidence_file=evidence_file,
        service_store_message=TestConfig.service_store_message,
        service_always_raise=TestConfig.service_always_raise,
    )

    # .. and write them out for the fixture to copy into the server's pickup directory.
    source_path = os.path.join(work_directory, 'imap_scheduler_test_services.py')

    with open(source_path, 'w') as source_file:
        _ = source_file.write(source)

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
        'hot_deploy_sources': [source_path],
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
