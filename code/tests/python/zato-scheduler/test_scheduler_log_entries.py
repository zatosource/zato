# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import time
from datetime import datetime, timezone
from textwrap import dedent

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager

# Zato - test utilities
from zato.common.test.client import AdminClient

# Zato - conftest
import conftest

# ################################################################################################################################
# ################################################################################################################################

_job_service_prefix = 'zato.scheduler.job'

_suffix = CryptoManager.generate_hex_string(32)
_job_name = f'test-scheduler.log-entries-{_suffix}'

# The line the fixture service logs on each run - the scheduler must capture it per run
_log_marker = 'Nightly reconciliation completed, records: 42'

# How long to wait for the job to fire at least once
_execution_wait_seconds = 10

# ################################################################################################################################
# Register services to be deployed before server starts
# ################################################################################################################################

conftest._pre_start_service_files.extend([

    ('test_scheduler_log_capture_service.py', dedent('''\
        from zato.server.service import Service

        class TestSchedulerLogCapture(Service):
            name = 'test-scheduler.log-capture'
            def handle(self):
                self.logger.info('Nightly reconciliation completed, records: 42')
    ''')),
])

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def client(zato_server):
    base_url = f'http://{zato_server["host"]}:{zato_server["port"]}'
    out = AdminClient(base_url, zato_server['password'])
    return out

# ################################################################################################################################
# ################################################################################################################################

def _parse(response):
    if isinstance(response, str):
        return json.loads(response)
    return response

# ################################################################################################################################
# ################################################################################################################################

class TestSchedulerLogEntries:
    """ Log lines a service emits during a scheduler-initiated run must be captured
    per run and returned by zato.scheduler.job.get-log-entries, along with system entries.
    """

    job_id = 0

# ##############################################################################################################################

    def test_01_create_job(self, client):

        start_date = datetime.now(timezone.utc).isoformat()

        response = _parse(client.create(f'{_job_service_prefix}.create',
            cluster_id=1,
            name=_job_name,
            is_active=True,
            job_type='interval_based',
            service='test-scheduler.log-capture',
            start_date=start_date,
            seconds=2,
        ))

        assert 'id' in response
        self.__class__.job_id = response['id']

# ##############################################################################################################################

    def test_02_wait_for_executions(self):
        time.sleep(_execution_wait_seconds)

# ##############################################################################################################################

    def test_03_log_entries_are_captured(self, client):

        job_id = self.__class__.job_id

        # The job must have run at least once by now ..
        history = client.invoke(f'{_job_service_prefix}.get-history', {'id': job_id})
        records = history['rows']
        assert records, 'Expected at least one execution record'

        # .. collect the log entries of every run so far ..
        entries = []

        for record in records:
            response = client.invoke(f'{_job_service_prefix}.get-log-entries', {
                'job_id': job_id,
                'current_run': record['current_run'],
                'since_idx': 0,
            })
            entries.extend(response['entries'])

        assert entries, 'Expected at least one log entry across all runs'

        # .. the line the service logged must have been captured ..
        captured = []
        for entry in entries:
            if _log_marker in entry['message']:
                captured.append(entry)

        assert captured, f'No entry with `{_log_marker}` among: {entries}'

        # .. captured entries carry the level of the original log record ..
        first_captured = captured[0]
        assert first_captured['level'] == 'INFO'
        assert first_captured['timestamp_iso']

        # .. and the scheduler adds its own system entries too.
        system_entries = []
        for entry in entries:
            if entry['level'] == 'SYSTEM':
                system_entries.append(entry)

        assert system_entries, f'No SYSTEM entries among: {entries}'

# ##############################################################################################################################

    def test_99_cleanup(self, client):
        client.delete(f'{_job_service_prefix}.delete', id=self.__class__.job_id)

# ################################################################################################################################
# ################################################################################################################################
