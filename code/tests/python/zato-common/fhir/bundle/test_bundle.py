from __future__ import annotations

import copy
import json

import pytest

from zato.fhir.base import FHIRResource
from zato.fhir.bundle import FHIRBundle, create_bundle, parse_bundle
from zato.fhir.r4_0_1 import Observation, Patient


def _wellness_patient() -> Patient:
    p = Patient()
    p.id = 'annual-wellness-patient-01'
    p.active = True
    p.gender = 'female'
    p.birthDate = '1990-05-15'
    return p


def _vitamin_observation() -> Observation:
    o = Observation()
    o.id = 'vitamin-d-wellness-01'
    o.status = 'final'
    return o


class TestFHIRBundleInit:

    def test_init_none(self):
        b = FHIRBundle(None)
        assert b._data == {}
        assert len(b) == 0

    def test_init_with_data(self):
        data = {
            'resourceType': 'Bundle',
            'type': 'collection',
            'id': 'bundle-01',
            'entry': [{'resource': {'resourceType': 'Patient', 'id': 'p1', 'active': True}}],
        }
        b = FHIRBundle(data)
        assert b._data is data
        assert len(b) == 1


class TestFHIRBundleProperties:

    def test_id(self):
        b = FHIRBundle({'id': 'wellness-bundle-id', 'entry': []})
        assert b.id == 'wellness-bundle-id'

    def test_type(self):
        b = FHIRBundle({'type': 'collection', 'entry': []})
        assert b.type == 'collection'

    def test_total(self):
        b = FHIRBundle({'total': 2, 'entry': []})
        assert b.total == 2

    def test_timestamp(self):
        b = FHIRBundle({'timestamp': '2026-04-06T12:00:00Z', 'entry': []})
        assert b.timestamp == '2026-04-06T12:00:00Z'


class TestFHIRBundleSequence:

    def test_len(self):
        p = _wellness_patient()
        b = create_bundle([p])
        assert len(b) == 1

    def test_iter(self):
        p = _wellness_patient()
        o = _vitamin_observation()
        b = create_bundle([p, o])
        entries = list(b)
        assert len(entries) == 2
        assert entries[0]['resource']['resourceType'] == 'Patient'
        assert entries[1]['resource']['resourceType'] == 'Observation'

    def test_getitem_valid(self):
        p = _wellness_patient()
        b = create_bundle([p])
        assert b[0]['resource']['id'] == 'annual-wellness-patient-01'

    def test_getitem_out_of_range_raises(self):
        b = FHIRBundle({'resourceType': 'Bundle', 'type': 'collection', 'entry': []})
        with pytest.raises(IndexError):
            _ = b[0]


class TestFHIRBundleGetResource:

    def test_get_resource_returns_fhir_resource(self):
        p = _wellness_patient()
        b = create_bundle([p])
        r = b.get_resource(0)
        assert r is not None
        assert isinstance(r, FHIRResource)
        assert isinstance(r, Patient)
        assert r.id == 'annual-wellness-patient-01'

    def test_get_resource_out_of_range_none(self):
        b = create_bundle([_wellness_patient()])
        assert b.get_resource(99) is None


class TestFHIRBundleGetResources:

    def test_get_resources_all_entries(self):
        p = _wellness_patient()
        o = _vitamin_observation()
        b = create_bundle([p, o])
        resources = b.get_resources()
        assert len(resources) == 2
        assert isinstance(resources[0], Patient)
        assert isinstance(resources[1], Observation)


class TestFHIRBundleSerialization:

    def test_to_dict_roundtrip(self):
        p = _wellness_patient()
        b = create_bundle([p], id_='roundtrip-bundle')
        payload = copy.deepcopy(b.to_dict())
        b2 = FHIRBundle.from_dict(payload)
        assert b2.id == 'roundtrip-bundle'
        assert len(b2) == 1
        assert b2[0]['resource']['id'] == 'annual-wellness-patient-01'

    def test_to_json_roundtrip(self):
        p = _wellness_patient()
        b = create_bundle([p])
        raw = b.to_json(indent=2)
        parsed = json.loads(raw)
        assert parsed['resourceType'] == 'Bundle'
        assert parsed['type'] == 'collection'
        assert parsed['entry'][0]['resource']['resourceType'] == 'Patient'

    def test_from_dict(self):
        data = {
            'resourceType': 'Bundle',
            'type': 'collection',
            'entry': [{'resource': {'resourceType': 'Patient', 'id': 'from-dict-patient', 'active': True}}],
        }
        b = FHIRBundle.from_dict(data)
        assert b.type == 'collection'
        assert len(b) == 1

    def test_from_json(self):
        data = {
            'resourceType': 'Bundle',
            'type': 'collection',
            'entry': [],
        }
        b = FHIRBundle.from_json(json.dumps(data))
        assert b.type == 'collection'
        assert len(b) == 0


class TestParseBundle:

    def test_parse_bundle_valid_json(self):
        raw = json.dumps({
            'resourceType': 'Bundle',
            'type': 'collection',
            'id': 'parsed-wellness-bundle',
            'entry': [],
        })
        b = parse_bundle(raw)
        assert isinstance(b, FHIRBundle)
        assert b.id == 'parsed-wellness-bundle'

    def test_parse_bundle_invalid_json_raises(self):
        with pytest.raises(json.JSONDecodeError):
            parse_bundle('not valid json {{{')


class TestCreateBundle:

    def test_create_bundle_searchset_with_resources(self):
        p = _wellness_patient()
        o = _vitamin_observation()
        b = create_bundle([p, o], bundle_type='searchset', id_='wellness-search-bundle')
        assert b.type == 'searchset'
        assert b.id == 'wellness-search-bundle'
        assert len(b) == 2
        assert b[0]['fullUrl'] == 'urn:uuid:annual-wellness-patient-01'
        assert b[1]['fullUrl'] == 'urn:uuid:vitamin-d-wellness-01'

    def test_create_bundle_collection_default(self):
        p = _wellness_patient()
        b = create_bundle([p])
        assert b.type == 'collection'


class TestFHIRBundleNestedContained:

    def test_bundle_preserves_contained_resources(self):
        inner = Observation()
        inner.id = 'routine-panel-vitamin-b12'
        inner.status = 'final'

        outer = Patient()
        outer.id = 'annual-checkup-patient-02'
        outer.active = True
        outer.contained = inner

        b = create_bundle([outer])
        loaded = b.get_resource(0)
        assert isinstance(loaded, Patient)
        assert loaded.contained is not None
        d = loaded.to_dict()
        assert 'contained' in d
        assert d['contained'][0]['resourceType'] == 'Observation'
        assert d['contained'][0]['id'] == 'routine-panel-vitamin-b12'


class TestFHIRBundleEmpty:

    def test_empty_bundle_no_entries(self):
        b = FHIRBundle({
            'resourceType': 'Bundle',
            'type': 'collection',
            'entry': [],
        })
        assert len(b) == 0
        assert list(b) == []
        assert b.get_resources() == []
