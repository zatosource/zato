from __future__ import annotations

import json


from zato.fhir.r4_0_1.resources import (
    Bundle, BundleEntry, Observation, Patient,
)
from zato.fhir.r4_0_1.datatypes import HumanName
from zato.fhir.bundle import BatchBuilder, TransactionBuilder


def _make_patient(id_: str = 'p1', family: str = 'Smith') -> Patient:
    p = Patient()
    p.id = id_
    n = HumanName()
    n.family = family
    p.name = n
    return p


def _make_observation(id_: str = 'obs1') -> Observation:
    o = Observation()
    o.id = id_
    o.status = 'final'
    o.code = {'text': 'BP'}
    return o


class TestTransactionBuilderCreate:

    def test_single_create(self):
        b = TransactionBuilder().create(_make_patient()).build()
        assert b.type_ == 'transaction'
        assert len(b.entry) == 1
        assert b.entry[0].request.method == 'POST'
        assert b.entry[0].request.url == 'Patient'

    def test_create_has_resource(self):
        b = TransactionBuilder().create(_make_patient()).build()
        r = b.entry[0].resource
        assert r.id == 'p1'
        assert r.name.family == 'Smith'

    def test_create_with_full_url(self):
        b = TransactionBuilder().create(
            _make_patient(), full_url='urn:uuid:abc-123'
        ).build()
        assert b.entry[0].fullUrl == 'urn:uuid:abc-123'

    def test_create_with_if_none_exist(self):
        b = TransactionBuilder().create(
            _make_patient(), if_none_exist='identifier=MRN-1'
        ).build()
        assert b.entry[0].request.ifNoneExist == 'identifier=MRN-1'


class TestTransactionBuilderUpdate:

    def test_update_sets_put_method(self):
        b = TransactionBuilder().update(_make_observation()).build()
        assert b.entry[0].request.method == 'PUT'
        assert b.entry[0].request.url == 'Observation/obs1'

    def test_update_with_if_match(self):
        b = TransactionBuilder().update(
            _make_observation(), if_match='W/"1"'
        ).build()
        assert b.entry[0].request.ifMatch == 'W/"1"'

    def test_update_has_resource(self):
        b = TransactionBuilder().update(_make_observation()).build()
        assert b.entry[0].resource.status == 'final'


class TestTransactionBuilderDelete:

    def test_delete_sets_method_and_url(self):
        b = TransactionBuilder().delete('Patient', 'old-1').build()
        assert b.entry[0].request.method == 'DELETE'
        assert b.entry[0].request.url == 'Patient/old-1'

    def test_delete_has_no_resource(self):
        b = TransactionBuilder().delete('Patient', 'old-1').build()
        assert 'resource' not in b.entry[0].__dict__


class TestTransactionBuilderRead:

    def test_read_sets_get_method(self):
        b = TransactionBuilder().read('Patient', 'p1').build()
        assert b.entry[0].request.method == 'GET'
        assert b.entry[0].request.url == 'Patient/p1'


class TestTransactionBuilderMultiple:

    def test_three_mixed_entries(self):
        b = (
            TransactionBuilder()
            .create(_make_patient())
            .update(_make_observation(), if_match='W/"2"')
            .delete('Patient', 'old-1')
            .build()
        )
        assert len(b.entry) == 3
        assert b.entry[0].request.method == 'POST'
        assert b.entry[1].request.method == 'PUT'
        assert b.entry[2].request.method == 'DELETE'

    def test_chaining_returns_self(self):
        builder = TransactionBuilder()
        result = builder.create(_make_patient())
        assert result is builder


class TestTransactionBuilderEmpty:

    def test_empty_transaction(self):
        b = TransactionBuilder().build()
        assert b.type_ == 'transaction'
        assert len(b.entry) == 0


class TestBatchBuilder:

    def test_batch_type(self):
        b = BatchBuilder().create(_make_patient()).build()
        assert b.type_ == 'batch'

    def test_batch_multiple(self):
        b = (
            BatchBuilder()
            .create(_make_patient('p1'))
            .create(_make_patient('p2', 'Jones'))
            .read('Patient', 'p3')
            .build()
        )
        assert len(b.entry) == 3
        assert all(isinstance(e, BundleEntry) for e in b.entry)


class TestTransactionBundleSerialization:

    def test_to_dict_has_correct_structure(self):
        b = (
            TransactionBuilder()
            .create(_make_patient())
            .delete('Patient', 'old-1')
            .build()
        )
        d = b.to_dict()
        assert d['resourceType'] == 'Bundle'
        assert d['type'] == 'transaction'
        assert len(d['entry']) == 2
        assert d['entry'][0]['request']['method'] == 'POST'
        assert d['entry'][0]['request']['url'] == 'Patient'
        assert d['entry'][0]['resource']['resourceType'] == 'Patient'
        assert d['entry'][1]['request']['method'] == 'DELETE'
        assert d['entry'][1]['request']['url'] == 'Patient/old-1'

    def test_to_json_is_valid_json(self):
        b = TransactionBuilder().create(_make_patient()).build()
        raw = b.to_json()
        d = json.loads(raw)
        assert d['type'] == 'transaction'
        assert d['entry'][0]['request']['method'] == 'POST'

    def test_round_trip_json(self):
        b = (
            TransactionBuilder()
            .create(_make_patient(), if_none_exist='identifier=MRN-1')
            .update(_make_observation(), if_match='W/"1"')
            .build()
        )
        raw = b.to_json()
        b2 = Bundle.from_json(raw)
        assert b2.type_ == 'transaction'
        assert len(b2.entry) == 2
        assert b2.entry[0].request.method == 'POST'
        assert b2.entry[0].request.ifNoneExist == 'identifier=MRN-1'
        assert b2.entry[1].request.method == 'PUT'
        assert b2.entry[1].request.ifMatch == 'W/"1"'

    def test_conditional_fields_absent_when_not_set(self):
        b = TransactionBuilder().create(_make_patient()).build()
        d = b.to_dict()
        req = d['entry'][0]['request']
        assert 'ifNoneExist' not in req
        assert 'ifMatch' not in req
        assert 'ifNoneMatch' not in req


class TestResponseBundleReading:

    def _response_json(self) -> str:
        return json.dumps({
            'resourceType': 'Bundle',
            'type': 'transaction-response',
            'entry': [
                {
                    'response': {
                        'status': '201 Created',
                        'location': 'Patient/p1/_history/1',
                        'etag': 'W/"1"',
                        'lastModified': '2024-01-15T10:30:00Z',
                    }
                },
                {
                    'response': {
                        'status': '200 OK',
                        'location': 'Observation/obs1/_history/2',
                    }
                },
            ]
        })

    def test_parse_response_type(self):
        resp = Bundle.from_json(self._response_json())
        assert resp.type_ == 'transaction-response'

    def test_parse_response_entry_status(self):
        resp = Bundle.from_json(self._response_json())
        assert resp.entry[0].response.status == '201 Created'
        assert resp.entry[1].response.status == '200 OK'

    def test_parse_response_entry_location(self):
        resp = Bundle.from_json(self._response_json())
        assert resp.entry[0].response.location == 'Patient/p1/_history/1'

    def test_parse_response_entry_etag(self):
        resp = Bundle.from_json(self._response_json())
        assert resp.entry[0].response.etag == 'W/"1"'

    def test_parse_response_entry_last_modified(self):
        resp = Bundle.from_json(self._response_json())
        assert resp.entry[0].response.lastModified == '2024-01-15T10:30:00Z'

    def test_response_round_trip(self):
        resp = Bundle.from_json(self._response_json())
        d = resp.to_dict()
        assert d['entry'][0]['response']['status'] == '201 Created'
        assert d['entry'][0]['response']['etag'] == 'W/"1"'


class TestTypedObjects:

    def test_bundle_is_typed(self):
        b = TransactionBuilder().create(_make_patient()).build()
        assert type(b).__name__ == 'Bundle'

    def test_entry_is_typed(self):
        b = TransactionBuilder().create(_make_patient()).build()
        assert type(b.entry[0]).__name__ == 'BundleEntry'

    def test_request_is_typed(self):
        b = TransactionBuilder().create(_make_patient()).build()
        assert type(b.entry[0].request).__name__ == 'BundleEntryRequest'

    def test_response_is_typed(self):
        resp = Bundle.from_json(json.dumps({
            'resourceType': 'Bundle',
            'type': 'transaction-response',
            'entry': [{'response': {'status': '200 OK'}}],
        }))
        assert type(resp.entry[0].response).__name__ == 'BundleEntryResponse'
