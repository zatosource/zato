# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A bulk export run through a live server against the fake FHIR server - the run service starts the export of a
# connection deployed through enmasse, the files reach the service destination of the tab, the job's state says it
# finished and the server's copy is gone, an export started from a service through client.export() runs with what
# the call gave it, and the connection exports back with its bulk_export mapping.

# stdlib
import os
import time
from http.client import OK
from json import dumps, loads

# Requests
import requests

# PyYAML
import yaml

# Zato
from zato.common.api import HL7
from zato.common.hl7.fhir.bulk_export.spec import JobState

from conftest import run_enmasse_export, FHIR_Outconn_Name, Observation_ID, Patient_ID_1, Patient_ID_2, \
    Receiver_Service_Name, Resources, Start_Service_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

_bulk = HL7.BulkExport

# Timeout for HTTP requests to the server under test, in seconds
_http_timeout = 30

# How long a job may take from start to its final state, in seconds, and how often it is looked at
_job_timeout = 60
_job_poll_interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

def _invoke(zato_server:'stranydict', service:'str', request:'stranydict') -> 'any_':
    """ Invokes a service through the server's admin invoke endpoint and returns the decoded response.
    """
    url = f'{zato_server["base_url"]}/zato/api/invoke/{service}'
    auth = ('admin.invoke', zato_server['invoke_password'])
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, data=dumps(request), headers=headers, auth=auth, timeout=_http_timeout)

    assert response.status_code == OK, f'{service} returned {response.status_code} -> {response.text}'

    out = response.json()
    return out

# ################################################################################################################################

def _wait_for_job(zato_server:'stranydict', job_id:'str') -> 'JobState':
    """ Waits until the job's state on disk says it finished and returns that state.
    """
    job_dir = os.path.join(zato_server['download_dir'], job_id)
    deadline = time.monotonic() + _job_timeout

    while time.monotonic() < deadline:

        state_path = os.path.join(job_dir, _bulk.State_File_Name)

        if os.path.exists(state_path):
            state = JobState.load(job_dir)
            if state.is_finished:
                return state

        time.sleep(_job_poll_interval)

    raise RuntimeError(f'Job {job_id} did not finish within {_job_timeout}s')

# ################################################################################################################################

def _received(zato_server:'stranydict', job_id:'str') -> 'anylist':
    """ What the receiver service was handed for one job, in the order it arrived.
    """
    out = []

    path = zato_server['receiver_path']
    if not os.path.exists(path):
        return out

    with open(path) as receiver_file:
        for line in receiver_file:
            record = loads(line)
            if record['job_id'] == job_id:
                out.append(record)

    return out

# ################################################################################################################################

def _by_type(items:'anylist', key:'str') -> 'stranydict':
    out = {}
    for item in items:
        out[item[key]] = item
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_the_run_service_exports_the_connection(zato_server:'stranydict') -> 'None':
    """ The run service starts the export the tab describes - the whole server, delivered to the receiver service.
    """
    response = _invoke(zato_server, _bulk.Dispatch_Service, {'conn_name': FHIR_Outconn_Name})
    job_id = response['job_id']
    assert job_id

    state = _wait_for_job(zato_server, job_id)

    assert state.status == _bulk.Status.Done, state.failures
    assert state.conn_name == FHIR_Outconn_Name
    assert state.failures == []

    # One file per resource type, every one of them delivered
    files = _by_type(state.files, 'resource_type')
    assert sorted(files) == ['Observation', 'Patient']
    assert files['Patient'].count == 2
    assert files['Observation'].count == 1

    for file_state in state.files:
        assert file_state.is_delivered is True

    # The receiver was handed each file and could read its resources
    received = _by_type(_received(zato_server, job_id), 'resource_type')
    assert sorted(received) == ['Observation', 'Patient']

    assert received['Patient']['connection_name'] == FHIR_Outconn_Name
    assert sorted(received['Patient']['ids']) == sorted([Patient_ID_1, Patient_ID_2])
    assert received['Observation']['ids'] == [Observation_ID]

    for record in received.values():
        assert record['is_error_file'] is False
        assert record['file_name'].endswith('.ndjson')

    # The server's copy of the export is gone and the kick-off went out with a token
    fhir_server = zato_server['fhir_server']

    export = fhir_server.bulk.exports[list(fhir_server.bulk.exports)[-1]]
    assert export.level == _bulk.Level.System
    assert export.is_deleted is True

    headers = fhir_server.bulk.kickoff_headers[-1]
    assert headers['Authorization'].startswith('Bearer ')

# ################################################################################################################################

def test_an_export_started_from_a_service_runs_with_what_the_call_gave_it(zato_server:'stranydict') -> 'None':
    """ client.export() starts an export of one patient's resources, the tab's level and types set aside.
    """
    request = {
        'conn_name': FHIR_Outconn_Name,
        'level': _bulk.Level.Patient,
        'patient_ids': [Patient_ID_1],
        'types': ['Patient'],
    }

    response = _invoke(zato_server, Start_Service_Name, request)
    job_id = response['job_id']
    assert job_id

    state = _wait_for_job(zato_server, job_id)
    assert state.status == _bulk.Status.Done, state.failures

    # Only the one patient, and only patients
    assert len(state.files) == 1
    assert state.files[0].resource_type == 'Patient'
    assert state.files[0].count == 1

    received = _received(zato_server, job_id)
    assert len(received) == 1
    assert received[0]['ids'] == [Patient_ID_1]

    fhir_server = zato_server['fhir_server']
    export = fhir_server.bulk.exports[list(fhir_server.bulk.exports)[-1]]

    assert export.level == _bulk.Level.Patient
    assert export.parameters['patient'] == Patient_ID_1
    assert export.parameters['_type'] == 'Patient'

# ################################################################################################################################

def test_every_resource_reaches_the_receiver(zato_server:'stranydict') -> 'None':
    """ Across the whole-server export, the receiver saw each resource the fake server holds exactly once.
    """
    response = _invoke(zato_server, _bulk.Dispatch_Service, {'conn_name': FHIR_Outconn_Name})
    job_id = response['job_id']

    _ = _wait_for_job(zato_server, job_id)

    ids = []
    for record in _received(zato_server, job_id):
        ids.extend(record['ids'])

    expected = []
    for resource in Resources:
        expected.append(resource['id'])

    assert sorted(ids) == sorted(expected)

# ################################################################################################################################

def test_the_connection_exports_with_its_bulk_export_mapping(zato_server:'stranydict') -> 'None':
    """ What enmasse imported comes back out under the bulk_export key, without the job's id.
    """
    exported = yaml.safe_load(run_enmasse_export(zato_server['server_directory']))

    connection = None
    for item in exported['outgoing_fhir']:
        if item['name'] == FHIR_Outconn_Name:
            connection = item

    assert connection is not None, 'The connection should be exported'

    bulk_export = connection[_bulk.Enmasse_Key]

    assert bulk_export['is_active'] is True
    assert bulk_export['level'] == _bulk.Level.System
    assert bulk_export['run_every'] == 1
    assert bulk_export['run_unit'] == 'days'
    assert bulk_export['delete_files'] is False
    assert 'job_id' not in bulk_export

    assert bulk_export['destinations'] == [
        {'name': Receiver_Service_Name, 'type': 'service', 'connection': Receiver_Service_Name, 'is_active': True},
    ]

    for key in connection:
        assert not key.startswith(_bulk.Field_Prefix)

# ################################################################################################################################
# ################################################################################################################################
