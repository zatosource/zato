# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from http.client import OK
from urllib.request import Request, urlopen

# pytest
import pytest

# Zato
from zato.common.test.fhir_ import FHIRTestServer

# Local
from conftest import convert

# ################################################################################################################################
# ################################################################################################################################

MSH = 'MSH|^~\\&|SENDAPP|SENDFAC|RECVAPP|RECVFAC|20240517143055||ADT^A01|MSG00001|P|2.5'
PID = 'PID|1||12345^^^MYHOSP^MR||Smith^John^Q|||M'
PV1 = 'PV1|1|I|WARD1^101^A^GENHOSP|||||||MED|||||||||VN123^^^MYHOSP'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def fhir_server():
    """ A live FHIR test server shared by all the tests of this module.
    """
    server = FHIRTestServer()
    server.start()

    yield server

    server.stop()

# ################################################################################################################################

def _post_bundle(server:'FHIRTestServer', bundle_dict:'dict') -> 'dict':
    """ Posts a bundle to the server's base URL and returns the response bundle.
    """
    body = json.dumps(bundle_dict)
    body_bytes = body.encode('utf8')

    request = Request(server.address, data=body_bytes, headers={'Content-Type': 'application/fhir+json'})

    with urlopen(request) as response:
        assert response.status == OK
        out = json.loads(response.read())

    return out

# ################################################################################################################################

def _read_resource(server:'FHIRTestServer', location:'str') -> 'dict':
    """ Reads one resource back from the server by its Type/id location.
    """
    with urlopen(f'{server.address}/{location}') as response:
        assert response.status == OK
        out = json.loads(response.read())

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestTransactionBundle:

    def test_transaction_applies_all_entries(self, fhir_server):
        bundle = convert(MSH, PID, PV1)
        bundle_dict = bundle.to_dict()

        response = _post_bundle(fhir_server, bundle_dict)

        assert response['resourceType'] == 'Bundle'
        assert response['type'] == 'transaction-response'

        # Every entry was created and got its own location
        entries = response['entry']
        assert len(entries) == len(bundle_dict['entry'])

        for entry in entries:
            entry_response = entry['response']

            assert entry_response['status'] == '201 Created'
            assert 'location' in entry_response

    def test_urn_references_resolve_to_server_ids(self, fhir_server):
        bundle = convert(MSH, PID, PV1)
        bundle_dict = bundle.to_dict()

        response = _post_bundle(fhir_server, bundle_dict)

        # Find where the Patient and the Encounter now live
        patient_location = None
        encounter_location = None

        request_entries = bundle_dict['entry']
        response_entries = response['entry']

        for request_entry, response_entry in zip(request_entries, response_entries):
            resource = request_entry['resource']
            entry_response = response_entry['response']

            location = entry_response['location']
            location = location.split('/_history')[0]

            if resource['resourceType'] == 'Patient':
                patient_location = location

            if resource['resourceType'] == 'Encounter':
                encounter_location = location

        # The stored Encounter points at the ID the server assigned to the Patient
        encounter = _read_resource(fhir_server, encounter_location)
        subject = encounter['subject']

        assert subject['reference'] == patient_location

        # And the Patient itself reads back with the demographics from the message
        patient = _read_resource(fhir_server, patient_location)
        names = patient['name']
        name = names[0]

        assert name['family'] == 'Smith'

    def test_batch_bundle(self, fhir_server):
        bundle = convert(MSH, PID, config=None)
        bundle_dict = bundle.to_dict()

        # The same content posted as a batch gets a batch-response back
        bundle_dict['type'] = 'batch'

        response = _post_bundle(fhir_server, bundle_dict)
        assert response['type'] == 'batch-response'

    def test_non_bundle_is_rejected(self, fhir_server):
        body = json.dumps({'resourceType': 'Patient'})
        body_bytes = body.encode('utf8')

        request = Request(fhir_server.address, data=body_bytes, headers={'Content-Type': 'application/fhir+json'})

        from urllib.error import HTTPError

        with pytest.raises(HTTPError) as wrapper:
            _ = urlopen(request)

        assert wrapper.value.code == 400

    def test_wrong_bundle_type_is_rejected(self, fhir_server):
        body = json.dumps({'resourceType': 'Bundle', 'type': 'collection'})
        body_bytes = body.encode('utf8')

        request = Request(fhir_server.address, data=body_bytes, headers={'Content-Type': 'application/fhir+json'})

        from urllib.error import HTTPError

        with pytest.raises(HTTPError) as wrapper:
            _ = urlopen(request)

        assert wrapper.value.code == 400

# ################################################################################################################################
# ################################################################################################################################
