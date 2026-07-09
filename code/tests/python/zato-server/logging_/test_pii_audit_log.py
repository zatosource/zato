# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# pytest
import pytest

# Zato - test utilities
from zato.common.test.client import AdminClient

# Zato - conftest
import conftest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The operation name the fixture service writes to the PII audit log
_pii_operation = 'logging-tests.customer-lookup'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def client(zato_server:'anydict') -> 'AdminClient':
    base_url = f'http://{zato_server["host"]}:{zato_server["server_port"]}'
    out = AdminClient(base_url, zato_server['password'])
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestPIIAuditLog:
    """ Entries written through self.audit_pii must land in audit-pii.log as JSON lines.
    """

    def test_pii_entry_lands_in_audit_pii_log(self, zato_server:'anydict', client:'AdminClient') -> 'None':

        # Invoke the fixture service that writes to the PII audit log ..
        response = client.invoke('logging-tests.pii-writer')
        assert response['result'] == 'ok'

        # .. wait for the entry to land in audit-pii.log ..
        contents = conftest.wait_for_log_content(zato_server['server_dir'], 'audit-pii.log', _pii_operation)

        # .. find the line and parse the JSON document it carries.
        for line in contents.splitlines():
            if _pii_operation in line:
                json_start = line.index('{')
                entry = json.loads(line[json_start:])
                break
        else:
            pytest.fail(f'No line with `{_pii_operation}` found in audit-pii.log')

        assert entry['cid']
        assert entry['op'] == _pii_operation
        assert entry['current_user'] == 'api.user'
        assert entry['extra']['customer_id'] == 'CU-48291'
        assert entry['extra']['remote_addr'] == '127.0.0.1'

# ################################################################################################################################
# ################################################################################################################################
