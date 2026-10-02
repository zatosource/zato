# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The export program run in-process against the fake FHIR server - a kick-off with a bearer token, polling until
# the manifest is ready, one NDJSON file per resource type downloaded and handed to the deliver service in the
# manifest's order, the server's copy deleted and the job directory removed, with the job's story in the audit log.
# A refused delivery stops the job where it is, and a program started again for the same job carries on from there.
# A kick-off the server refuses fails the job with the server's status, and an error file travels like any other.

# stdlib
import os
from base64 import b64decode
from http.client import FORBIDDEN, NO_CONTENT, NOT_FOUND
from json import loads

# pytest
import pytest

# Zato
from zato.common.api import HL7
from zato.common.audit_log.common import AuditEvent, AuditOutcome, AuditSource
from zato.common.hl7.fhir.bulk_export.program import run_job
from zato.common.hl7.fhir.bulk_export.spec import JobState
from zato.common.test.fhir.common import auth_type_basic

from bulk_stub import bulk_audit_env, get_attrs, get_events, new_fhir_server, new_spec, Connection_Name, \
    DeliverStandIn, File_Count, Invoke_Password, Invoke_Username, Observation_ID, Patient_ID_1, Patient_ID_2, \
    Resources

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.fhir import FHIRTestServer
    from zato.common.typing_ import any_, anylist, strlist

    anylist = anylist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

_bulk = HL7.BulkExport

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def fhir_server() -> 'any_':
    server = new_fhir_server()
    yield server
    server.stop()

# ################################################################################################################################

@pytest.fixture
def basic_fhir_server() -> 'any_':
    server = new_fhir_server(auth_type_basic)
    yield server
    server.stop()

# ################################################################################################################################

@pytest.fixture
def deliver() -> 'any_':
    with DeliverStandIn() as stand_in:
        yield stand_in

# ################################################################################################################################

def _resource_ids(path:'str') -> 'strlist':
    out = []
    with open(path) as file:
        for line in file:
            out.append(loads(line)['id'])
    return out

# ################################################################################################################################

def _events_of(event_type:'str') -> 'anylist':
    out = []
    for event in get_events():
        if event['event_type'] == event_type:
            out.append(event)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestExport:

    def test_an_export_downloads_every_file_and_hands_each_over(
        self,
        tmp_path:'any_',
        fhir_server:'FHIRTestServer',
        deliver:'DeliverStandIn',
    ) -> 'None':

        # The files stay on disk so the test can read them
        spec = new_spec(fhir_server, deliver, str(tmp_path))
        spec.delete_files = False

        with bulk_audit_env(tmp_path):
            state = run_job(spec)

        assert state.status == _bulk.Status.Done
        assert state.phase == _bulk.Phase.Done
        assert state.failures == []

        # One file per resource type, every one of them downloaded and delivered
        assert len(state.files) == File_Count

        by_type = {}
        for file_state in state.files:
            assert file_state.is_downloaded is True
            assert file_state.is_delivered is True
            by_type[file_state.resource_type] = file_state

        assert sorted(by_type) == ['Observation', 'Patient']

        patient_file = by_type['Patient']
        assert patient_file.count == 2
        assert sorted(_resource_ids(patient_file.path)) == sorted([Patient_ID_1, Patient_ID_2])

        observation_file = by_type['Observation']
        assert observation_file.count == 1
        assert _resource_ids(observation_file.path) == [Observation_ID]

        # Each file reached the deliver service, in the manifest's order, under the connection's name
        assert len(deliver.files) == File_Count

        for file_state, delivered, request in zip(state.files, deliver.files, deliver.requests):
            assert delivered['job_id'] == spec.job_id
            assert delivered['connection_name'] == Connection_Name
            assert delivered['resource_type'] == file_state.resource_type
            assert delivered['count'] == file_state.count
            assert delivered['path'] == file_state.path
            assert delivered['is_error_file'] is False

            assert request['conn_name'] == Connection_Name
            assert request['destinations'] == ''

        # The server's copy of the export is gone
        export_id = list(fhir_server.bulk.exports)[0]
        assert fhir_server.bulk.exports[export_id].is_deleted is True

# ################################################################################################################################

    def test_the_job_directory_goes_once_the_files_are_delivered(
        self,
        tmp_path:'any_',
        fhir_server:'FHIRTestServer',
        deliver:'DeliverStandIn',
    ) -> 'None':
        spec = new_spec(fhir_server, deliver, str(tmp_path))

        with bulk_audit_env(tmp_path):
            state = run_job(spec)

        assert state.status == _bulk.Status.Done
        assert not os.path.exists(spec.job_dir)

# ################################################################################################################################

    def test_the_kick_off_carries_the_parameters_and_the_token(
        self,
        tmp_path:'any_',
        fhir_server:'FHIRTestServer',
        deliver:'DeliverStandIn',
    ) -> 'None':
        spec = new_spec(fhir_server, deliver, str(tmp_path))
        spec.level = _bulk.Level.Patient
        spec.patient_ids = [Patient_ID_1]
        spec.types = ['Patient', 'Observation']
        spec.since = '2020-01-01T00:00:00Z'

        with bulk_audit_env(tmp_path):
            state = run_job(spec)

        assert state.status == _bulk.Status.Done

        export = list(fhir_server.bulk.exports.values())[0]
        assert export.level == _bulk.Level.Patient
        assert export.parameters['_type'] == 'Patient,Observation'
        assert export.parameters['_since'] == spec.since
        assert export.parameters['patient'] == Patient_ID_1

        # The kick-off went out with a token the server's own endpoint issued
        headers = fhir_server.bulk.kickoff_headers[0]
        assert headers['Authorization'].startswith('Bearer ')
        assert headers['Prefer'] == 'respond-async'

        # Only the first patient's resources were exported
        by_type = {}
        for file_state in state.files:
            by_type[file_state.resource_type] = file_state.count

        assert by_type == {'Patient': 1, 'Observation': 1}

# ################################################################################################################################

    def test_basic_auth_is_sent_as_it_is(
        self,
        tmp_path:'any_',
        basic_fhir_server:'FHIRTestServer',
        deliver:'DeliverStandIn',
    ) -> 'None':
        spec = new_spec(basic_fhir_server, deliver, str(tmp_path))

        with bulk_audit_env(tmp_path):
            state = run_job(spec)

        assert state.status == _bulk.Status.Done

        headers = basic_fhir_server.bulk.kickoff_headers[0]
        assert headers['Authorization'] == spec.basic_auth_header

# ################################################################################################################################

    def test_the_server_is_polled_until_the_manifest_is_ready(
        self,
        tmp_path:'any_',
        fhir_server:'FHIRTestServer',
        deliver:'DeliverStandIn',
    ) -> 'None':
        fhir_server.bulk.config.polls_until_ready = 3

        spec = new_spec(fhir_server, deliver, str(tmp_path))

        with bulk_audit_env(tmp_path):
            state = run_job(spec)

        assert state.status == _bulk.Status.Done

        export = list(fhir_server.bulk.exports.values())[0]
        assert export.poll_count == 4

# ################################################################################################################################

    def test_files_that_need_no_token_are_downloaded_without_one(
        self,
        tmp_path:'any_',
        fhir_server:'FHIRTestServer',
        deliver:'DeliverStandIn',
    ) -> 'None':
        fhir_server.bulk.config.requires_access_token = False

        spec = new_spec(fhir_server, deliver, str(tmp_path))

        with bulk_audit_env(tmp_path):
            state = run_job(spec)

        assert state.status == _bulk.Status.Done
        assert state.requires_access_token is False

        for headers in fhir_server.bulk.file_headers:
            assert 'Authorization' not in headers

# ################################################################################################################################

    def test_the_servers_copy_stays_when_the_connection_says_so(
        self,
        tmp_path:'any_',
        fhir_server:'FHIRTestServer',
        deliver:'DeliverStandIn',
    ) -> 'None':
        spec = new_spec(fhir_server, deliver, str(tmp_path))
        spec.delete_on_server = False

        with bulk_audit_env(tmp_path):
            state = run_job(spec)

        assert state.status == _bulk.Status.Done

        export = list(fhir_server.bulk.exports.values())[0]
        assert export.is_deleted is False

# ################################################################################################################################

    def test_an_error_file_travels_like_any_other(
        self,
        tmp_path:'any_',
        fhir_server:'FHIRTestServer',
        deliver:'DeliverStandIn',
    ) -> 'None':
        fhir_server.bulk.config.error_outcomes = [
            {'resourceType': 'OperationOutcome', 'issue': [{'severity': 'error', 'code': 'exception'}]},
        ]

        spec = new_spec(fhir_server, deliver, str(tmp_path))

        with bulk_audit_env(tmp_path):
            state = run_job(spec)

        assert state.status == _bulk.Status.Done

        # The error file comes last, after the server's own files
        last = state.files[-1]
        assert last.resource_type == _bulk.Error_Resource_Type
        assert last.count == 1

        delivered = deliver.files[-1]
        assert delivered['is_error_file'] is True
        assert delivered['resource_type'] == _bulk.Error_Resource_Type

# ################################################################################################################################
# ################################################################################################################################

class TestFailures:

    def test_a_refused_kick_off_fails_the_job_with_the_servers_status(
        self,
        tmp_path:'any_',
        fhir_server:'FHIRTestServer',
        deliver:'DeliverStandIn',
    ) -> 'None':
        fhir_server.bulk.config.kickoff_status = FORBIDDEN

        spec = new_spec(fhir_server, deliver, str(tmp_path))

        with bulk_audit_env(tmp_path):
            state = run_job(spec)

            assert state.status == _bulk.Status.Failed
            assert state.phase == _bulk.Phase.Failed
            assert state.status_url == ''
            assert len(state.failures) == 1
            assert str(FORBIDDEN) in state.failures[0]

            # Nothing was handed over and the job's directory stays for the job to be picked up again
            assert deliver.files == []
            assert os.path.exists(spec.job_dir)

            # The audit log says why
            completed = _events_of(AuditEvent.Run_Completed)
            assert len(completed) == 1
            assert completed[0]['outcome'] == AuditOutcome.Error
            assert completed[0]['status'] == str(FORBIDDEN)

# ################################################################################################################################

    def test_a_refused_delivery_stops_the_job_and_a_new_run_carries_on(
        self,
        tmp_path:'any_',
        fhir_server:'FHIRTestServer',
        deliver:'DeliverStandIn',
    ) -> 'None':
        deliver.refuse('sftp.archive -> Permission denied')

        spec = new_spec(fhir_server, deliver, str(tmp_path))

        with bulk_audit_env(tmp_path):
            state = run_job(spec)

            assert state.status == _bulk.Status.Failed
            assert 'Permission denied' in state.failures[0]

            # The first file was downloaded and offered once, nothing past it was touched
            assert state.files[0].is_downloaded is True
            assert state.files[0].is_delivered is False
            assert state.files[1].is_downloaded is False
            assert len(deliver.files) == 1

            # The state on disk is what a program started again reads back
            saved = JobState.load(spec.job_dir)
            assert saved.status == _bulk.Status.Failed
            assert saved.status_url == state.status_url
            assert saved.manifest == state.manifest

            # The destination is reachable again and the same job is run once more ..
            deliver.accept()
            resumed = run_job(spec)

            assert resumed.status == _bulk.Status.Done
            assert resumed.job_id == spec.job_id

            # .. the export was neither kicked off nor polled again ..
            assert len(fhir_server.bulk.exports) == 1
            assert len(fhir_server.bulk.kickoff_headers) == 1

            # .. the first file was offered again and the rest followed.
            assert len(deliver.files) == 1 + File_Count
            assert deliver.files[1]['resource_type'] == state.files[0].resource_type

            for file_state in resumed.files:
                assert file_state.is_delivered is True

            assert not os.path.exists(spec.job_dir)

# ################################################################################################################################

    def test_a_failed_download_fails_the_job(
        self,
        tmp_path:'any_',
        fhir_server:'FHIRTestServer',
        deliver:'DeliverStandIn',
    ) -> 'None':
        fhir_server.bulk.config.download_status = NOT_FOUND

        spec = new_spec(fhir_server, deliver, str(tmp_path))

        with bulk_audit_env(tmp_path):
            state = run_job(spec)

            assert state.status == _bulk.Status.Failed
            assert str(NOT_FOUND) in state.failures[0]
            assert deliver.files == []

            received = _events_of(AuditEvent.Received)
            assert len(received) == 1
            assert received[0]['outcome'] == AuditOutcome.Error
            assert received[0]['status'] == str(NOT_FOUND)

# ################################################################################################################################
# ################################################################################################################################

class TestAuditLog:

    def test_the_job_reads_as_one_story_under_its_id(
        self,
        tmp_path:'any_',
        fhir_server:'FHIRTestServer',
        deliver:'DeliverStandIn',
    ) -> 'None':
        spec = new_spec(fhir_server, deliver, str(tmp_path))

        with bulk_audit_env(tmp_path):
            state = run_job(spec)
            assert state.status == _bulk.Status.Done

            events = get_events()

            # Every event belongs to the job and the connection
            for event in events:
                assert event['source'] == AuditSource.FHIR_Bulk_Export
                assert event['cid'] == spec.job_id
                assert event['object_name'] == Connection_Name

                attrs = get_attrs(event['id'])
                assert attrs['job_id'] == spec.job_id

            # The phases follow one another - kick-off, manifest, one download and one delivery per file, clean-up, done
            phases = []
            for event in events:
                phases.append(get_attrs(event['id'])['phase'])

            expected = [_bulk.Phase.Kickoff, _bulk.Phase.Manifest]
            for _ in range(File_Count):
                expected.append(_bulk.Phase.Download)
                expected.append(_bulk.Phase.Deliver)
            expected.append(_bulk.Phase.Cleanup)
            expected.append(_bulk.Phase.Done)

            assert phases == expected

            # The kick-off names the endpoint, the manifest says how many files, each download how many resources
            kickoff = events[0]
            assert kickoff['event_type'] == AuditEvent.Request_Sent
            assert kickoff['endpoint'] == fhir_server.address + '/$export'
            assert kickoff['outcome'] == AuditOutcome.OK

            manifest = events[1]
            assert manifest['event_type'] == AuditEvent.Response_Received
            assert get_attrs(manifest['id'])['count'] == str(File_Count)
            assert loads(manifest['data'])['output']

            total = 0
            for event in events:
                attrs = get_attrs(event['id'])
                if attrs['phase'] == _bulk.Phase.Download:
                    assert event['event_type'] == AuditEvent.Received
                    assert attrs['resource_type'] in ('Patient', 'Observation')
                    assert attrs['file_name'].endswith('.ndjson')
                    total += int(attrs['count'])

            assert total == len(Resources)

            # The clean-up recorded the server's answer and the last word is the job's total
            cleanup = events[-2]
            assert cleanup['event_type'] == AuditEvent.Note
            assert cleanup['status'] == str(NO_CONTENT)

            done = events[-1]
            assert done['event_type'] == AuditEvent.Run_Completed
            assert done['outcome'] == AuditOutcome.OK
            assert get_attrs(done['id'])['count'] == str(len(Resources))

# ################################################################################################################################

    def test_the_deliver_service_is_called_with_the_servers_credentials(
        self,
        tmp_path:'any_',
        fhir_server:'FHIRTestServer',
        deliver:'DeliverStandIn',
    ) -> 'None':
        spec = new_spec(fhir_server, deliver, str(tmp_path))

        with bulk_audit_env(tmp_path):
            _ = run_job(spec)

        request = deliver.requests[0]
        assert request['path'] == '/zato/api/invoke/' + _bulk.Deliver_Service

        # Basic Auth with the invoke credentials
        expected = f'{Invoke_Username}:{Invoke_Password}'
        assert request['authorization'].startswith('Basic ')

        decoded = b64decode(request['authorization'][len('Basic '):]).decode('ascii')
        assert decoded == expected

# ################################################################################################################################
# ################################################################################################################################
