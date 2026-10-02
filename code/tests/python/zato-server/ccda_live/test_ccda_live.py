# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# C-CDA documents through a live server - a channel created by enmasse with the C-CDA data format converts each document
# before its service runs, as XML or as base64, and refuses what is not a CDA document with a 400, a service behind a plain
# REST channel converts with self.ccda.to_fhir() to the same result, each conversion is in the audit log under the service's
# name, and the channel exports back with its data format.

# stdlib
import sqlite3
import time
from base64 import b64encode
from http.client import BAD_REQUEST, INTERNAL_SERVER_ERROR, OK

# Requests
import requests

# PyYAML
import yaml

# Zato
from zato.common.api import HL7
from zato.common.audit_log.common import AuditOutcome, AuditSource

from conftest import CCDA_Channel_Name, CCDA_Channel_Path, Convert_Service_Name, Plain_Channel_Name, Plain_Channel_Path, \
    read_sample, Receive_Service_Name, run_enmasse, run_enmasse_export

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

_ccda = HL7.CCDA

# Timeout for HTTP requests to the server under test, in seconds
_http_timeout = 60

# How long an audit event is given to reach the database, in seconds, and how often it is looked for
_audit_timeout = 30
_audit_poll_interval = 0.5

# What the CCD sample is about
_ccd_patient_family = 'Jones'

# ################################################################################################################################
# ################################################################################################################################

def _post(zato_server:'stranydict', path:'str', data:'bytes', content_type:'str') -> 'requests.Response':
    url = zato_server['base_url'] + path
    headers = {'Content-Type': content_type}

    out = requests.post(url, data=data, headers=headers, timeout=_http_timeout)
    return out

# ################################################################################################################################

def _audit_events(zato_server:'stranydict', object_name:'str', outcome:'str') -> 'anylist':
    """ The C-CDA audit events of one object with one outcome, each with its attributes, oldest first.
    """
    out = []

    connection = sqlite3.connect(zato_server['audit_db_path'])
    connection.row_factory = sqlite3.Row

    try:
        events = connection.execute(
            'select id, cid, duration_ms, data from event where source = ? and object_name = ? and outcome = ? order by id',
            (AuditSource.CCDA, object_name, outcome)).fetchall()

        for event in events:
            attrs = {}
            for row in connection.execute('select name, value from event_attr where event_id = ?', (event['id'],)):
                attrs[row['name']] = row['value']

            out.append({
                'cid': event['cid'],
                'duration_ms': event['duration_ms'],
                'data': event['data'],
                'attrs': attrs,
            })

    finally:
        connection.close()

    return out

# ################################################################################################################################

def _wait_for_audit_events(zato_server:'stranydict', object_name:'str', outcome:'str', count:'int') -> 'anylist':
    """ Waits until at least the given number of events is in the database and returns them all.
    """
    deadline = time.monotonic() + _audit_timeout

    while time.monotonic() < deadline:
        out = _audit_events(zato_server, object_name, outcome)
        if len(out) >= count:
            return out

        time.sleep(_audit_poll_interval)

    raise RuntimeError(f'Fewer than {count} {outcome} C-CDA audit events for {object_name} within {_audit_timeout}s')

# ################################################################################################################################

def _channels_by_name(exported_yaml:'str') -> 'stranydict':
    exported = yaml.safe_load(exported_yaml)

    out = {}
    for item in exported['channel_rest']:
        out[item['name']] = item

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_ccda_channel_converts_the_document_before_the_service_runs(zato_server:'stranydict') -> 'None':
    document = read_sample('CCD.ccda')

    response = _post(zato_server, CCDA_Channel_Path, document, _ccda.Content_Type)
    assert response.status_code == OK, response.text

    # The service was handed a transaction bundle of the document's resources, with the document itself among them
    summary = response.json()

    assert summary['type'] == _ccda.Bundle_Type
    assert summary['resource_count'] > 20
    assert summary['patient_family'] == _ccd_patient_family
    assert summary['document_size'] == len(document)

    for resource_type in ('Composition', 'Patient', 'DocumentReference', 'AllergyIntolerance', 'Observation'):
        assert resource_type in summary['resource_types']

# ################################################################################################################################

def test_a_ccda_channel_takes_base64_too(zato_server:'stranydict') -> 'None':
    document = read_sample('Patient-1.ccda')

    response = _post(zato_server, CCDA_Channel_Path, b64encode(document), 'text/plain')
    assert response.status_code == OK, response.text

    summary = response.json()
    assert summary['type'] == _ccda.Bundle_Type
    assert summary['document_size'] == len(document)
    assert 'Patient' in summary['resource_types']

# ################################################################################################################################

def test_a_ccda_channel_refuses_what_is_not_a_cda_document(zato_server:'stranydict') -> 'None':

    # Not XML at all ..
    response = _post(zato_server, CCDA_Channel_Path, b'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FACILITY|20260102||ADT^A01|1|P|2.5',
        'text/plain')
    assert response.status_code == BAD_REQUEST, response.text

    # .. XML that is not a CDA document.
    response = _post(zato_server, CCDA_Channel_Path, b'<Patient xmlns="http://hl7.org/fhir"><id value="p1"/></Patient>',
        'application/xml')
    assert response.status_code == BAD_REQUEST, response.text

# ################################################################################################################################

def test_a_service_converts_with_self_ccda_to_the_same_result(zato_server:'stranydict') -> 'None':
    document = read_sample('CCD.ccda')

    from_channel = _post(zato_server, CCDA_Channel_Path, document, _ccda.Content_Type)
    from_service = _post(zato_server, Plain_Channel_Path, document, _ccda.Content_Type)

    assert from_channel.status_code == OK, from_channel.text
    assert from_service.status_code == OK, from_service.text

    assert from_service.json() == from_channel.json()

# ################################################################################################################################

def test_each_kind_of_document_converts_through_the_service(zato_server:'stranydict') -> 'None':
    for name in ('Discharge_Summary.ccda', 'Progress_Note.ccda', 'Referral_Note.ccda'):
        response = _post(zato_server, Plain_Channel_Path, read_sample(name), _ccda.Content_Type)
        assert response.status_code == OK, f'{name} -> {response.text}'

        summary = response.json()
        assert summary['type'] == _ccda.Bundle_Type
        assert 'Composition' in summary['resource_types']

# ################################################################################################################################

def test_a_service_given_what_is_not_a_cda_document_fails(zato_server:'stranydict') -> 'None':
    response = _post(zato_server, Plain_Channel_Path, b'{"resourceType": "Patient"}', 'application/json')
    assert response.status_code == INTERNAL_SERVER_ERROR, response.text

# ################################################################################################################################

def test_each_conversion_is_in_the_audit_log(zato_server:'stranydict') -> 'None':
    document = read_sample('Progress_Note.ccda')

    response = _post(zato_server, Plain_Channel_Path, document, _ccda.Content_Type)
    assert response.status_code == OK, response.text

    summary = response.json()

    # The conversion is filed under the name of the service that asked for it ..
    events = _wait_for_audit_events(zato_server, Convert_Service_Name, AuditOutcome.OK, 1)
    event = events[-1]

    assert event['cid']
    assert event['duration_ms'] > 0

    attrs = event['attrs']
    assert attrs['root_template'] == 'ProgressNote'
    assert attrs['resource_count'] == str(summary['resource_count'])
    assert attrs['document_size'] == str(len(document))

    # .. a channel's conversions under the channel's name ..
    assert len(_wait_for_audit_events(zato_server, CCDA_Channel_Name, AuditOutcome.OK, 1)) >= 1

    # .. and what was refused is there as an error with its reason.
    errors = _wait_for_audit_events(zato_server, CCDA_Channel_Name, AuditOutcome.Error, 1)
    assert errors[-1]['attrs']['reason'] == _ccda.Reason.Not_CDA

# ################################################################################################################################

def test_the_channel_exports_with_its_data_format(zato_server:'stranydict') -> 'None':
    channels = _channels_by_name(run_enmasse_export(zato_server['server_directory']))

    ccda_channel = channels[CCDA_Channel_Name]
    assert ccda_channel['data_format'] == _ccda.Data_Format
    assert ccda_channel['service'] == Receive_Service_Name
    assert ccda_channel['url_path'] == CCDA_Channel_Path

    # A plain channel says nothing about its format
    assert 'data_format' not in channels[Plain_Channel_Name]

    # Importing the export back changes nothing, and the channel still converts
    run_enmasse(zato_server['server_directory'], yaml.safe_dump({'channel_rest': [ccda_channel]}))

    assert _channels_by_name(run_enmasse_export(zato_server['server_directory']))[CCDA_Channel_Name] == ccda_channel

    response = _post(zato_server, CCDA_Channel_Path, read_sample('CCD.ccda'), _ccda.Content_Type)
    assert response.status_code == OK, response.text

# ################################################################################################################################
# ################################################################################################################################
