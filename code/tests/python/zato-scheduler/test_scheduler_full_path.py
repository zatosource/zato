# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import tempfile
import time
from datetime import datetime, timezone
from textwrap import dedent

# Zato
from zato.common.crypto.api import CryptoManager

# PyPI
import pytest

# Zato - test utilities
from zato.common.test.client import AdminClient as ZatoClient

# Zato - conftest
import conftest

JOB_SERVICE = 'zato.scheduler.job'

_suffix = CryptoManager.generate_hex_string(32)

_FAST_OK_NAME = f'test-scheduler.fast-ok-{_suffix}'
_SLOW_TIMEOUT_NAME = f'test-scheduler.slow-timeout-{_suffix}'
_ERROR_NAME = f'test-scheduler.error-{_suffix}'

_evidence_file = tempfile.NamedTemporaryFile(prefix='zato_sched_evidence_', suffix='.csv', delete=False)
_evidence_path = _evidence_file.name
_evidence_file.close()

# ################################################################################################################################
# Register services to be deployed before server starts
# ################################################################################################################################

conftest._pre_start_service_files.extend([

    ('test_scheduler_file_appender.py', dedent('''\
        from zato.server.service import Service
        import json
        from datetime import datetime, timezone

        class TestSchedulerFileAppender(Service):
            name = 'test-scheduler.file-appender'
            def handle(self):
                extra = json.loads(self.request.raw_request)
                with open(extra['path'], 'a') as f:
                    f.write(f'{extra["tag"]},{datetime.now(timezone.utc).isoformat()}\\n')
    ''')),

    ('test_scheduler_raise_error.py', dedent('''\
        from zato.server.service import Service

        class TestSchedulerRaiseError(Service):
            name = 'test-scheduler.raise-error'
            def handle(self):
                raise Exception('deliberate test error')
    ''')),
])

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def client(zato_server):
    out = ZatoClient(zato_server['base_url'], zato_server['password'])
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSchedulerFullPath:

    created_ids = []

    def _start_date(self):
        return datetime.now(timezone.utc).isoformat()

    # ##############################################################################################################################

    def _parse(self, resp):
        if isinstance(resp, str):
            return json.loads(resp)
        return resp

    def test_01_create_jobs(self, client):

        resp = self._parse(client.create(f'{JOB_SERVICE}.create',
            cluster_id=1,
            name=_FAST_OK_NAME,
            is_active=True,
            job_type='interval_based',
            service='test-scheduler.file-appender',
            start_date=self._start_date(),
            seconds=2,
            extra=json.dumps({'path': _evidence_path, 'tag': 'fast-ok'}),
        ))
        assert 'id' in resp
        self.__class__.created_ids.append(resp['id'])

        resp = self._parse(client.create(f'{JOB_SERVICE}.create',
            cluster_id=1,
            name=_SLOW_TIMEOUT_NAME,
            is_active=True,
            job_type='interval_based',
            service='demo.sleep',
            start_date=self._start_date(),
            seconds=2,
            max_execution_time_ms=3000,
            extra=json.dumps({'seconds': 10}),
        ))
        assert 'id' in resp
        self.__class__.created_ids.append(resp['id'])

        resp = self._parse(client.create(f'{JOB_SERVICE}.create',
            cluster_id=1,
            name=_ERROR_NAME,
            is_active=True,
            job_type='interval_based',
            service='test-scheduler.raise-error',
            start_date=self._start_date(),
            seconds=3,
        ))
        assert 'id' in resp
        self.__class__.created_ids.append(resp['id'])

    # ##############################################################################################################################

    def test_02_wait_for_executions(self):
        time.sleep(12)

    # ##############################################################################################################################

    def test_03_file_proves_execution(self):
        with open(_evidence_path) as f:
            lines = [line.strip() for line in f if line.strip()]

        assert len(lines) >= 3, f'Expected >= 3 lines in evidence file, got {len(lines)}: {lines}'

        for line in lines:
            tag, iso_ts = line.split(',', 1)
            assert tag == 'fast-ok'
            datetime.fromisoformat(iso_ts)

    # ##############################################################################################################################

    def test_04_fast_ok_history(self, client):
        job_id = self.__class__.created_ids[0]
        response = client.invoke(f'{JOB_SERVICE}.get-history', {'id': job_id})
        rows = response['rows']
        ok_records = []

        for record in rows:
            if record['outcome'] == 'ok':
                ok_records.append(record)

        assert len(ok_records) >= 3, f'Expected >= 3 ok records, got {len(ok_records)}'

    # ##############################################################################################################################

    def test_05_fast_ok_ran_multiple_times(self, client):
        job_id = self.__class__.created_ids[0]
        response = client.invoke(f'{JOB_SERVICE}.get-history', {'id': job_id})
        total = response['total']
        assert total >= 3, f'Expected total >= 3, got {total}'

    # ##############################################################################################################################

    def test_06_timeout_detected(self, client):
        job_id = self.__class__.created_ids[1]
        response = client.invoke(f'{JOB_SERVICE}.get-history', {'id': job_id})
        rows = response['rows']
        timeouts = []
        outcomes = []

        for record in rows:
            outcomes.append(record['outcome'])
            if record['outcome'] == 'timeout':
                timeouts.append(record)

        assert len(timeouts) >= 1, f'Expected >= 1 timeout records, got {len(timeouts)}: {outcomes}'

    # ##############################################################################################################################

    def test_07_error_recorded(self, client):
        job_id = self.__class__.created_ids[2]
        response = client.invoke(f'{JOB_SERVICE}.get-history', {'id': job_id})
        rows = response['rows']
        errors = []
        outcomes = []

        for record in rows:
            outcomes.append(record['outcome'])
            if record['outcome'] == 'error':
                errors.append(record)

        assert len(errors) >= 1, f'Expected >= 1 error records, got {len(errors)}: {outcomes}'

    # ##############################################################################################################################

    def test_99_cleanup(self, client):
        for job_id in self.__class__.created_ids[:]:
            client.delete(f'{JOB_SERVICE}.delete', id=job_id)
            self.__class__.created_ids.remove(job_id)

        if os.path.exists(_evidence_path):
            os.unlink(_evidence_path)

# ################################################################################################################################
# ################################################################################################################################
