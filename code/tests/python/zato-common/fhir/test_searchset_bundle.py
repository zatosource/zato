"""Tests for 8a - build_searchset."""

from __future__ import annotations

import json


from zato.fhir.bundle import build_searchset
from zato.fhir.r4_0_1.resources import Bundle, BundleEntry, BundleEntrySearch, Patient, Observation


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_patient(pid: str = 'p1', family: str = 'Doe') -> Patient:
    p = Patient()
    p.id = pid
    p.active = True
    return p


def _make_observation(oid: str = 'obs-1') -> Observation:
    o = Observation()
    o.id = oid
    o.status = 'final'
    return o


# ---------------------------------------------------------------------------
# Basic structure
# ---------------------------------------------------------------------------

class TestSearchsetBasic:

    def test_type_is_searchset(self):
        b = build_searchset([_make_patient()])
        assert b.type_ == 'searchset'

    def test_total_defaults_to_len(self):
        resources = [_make_patient('p1'), _make_patient('p2'), _make_patient('p3')]
        b = build_searchset(resources)
        assert b.total == 3

    def test_total_explicit(self):
        b = build_searchset([_make_patient()], total=42)
        assert b.total == 42

    def test_returns_bundle_type(self):
        b = build_searchset([_make_patient()])
        assert isinstance(b, Bundle)

    def test_entry_count(self):
        resources = [_make_patient('a'), _make_patient('b')]
        b = build_searchset(resources)
        assert len(b.entry) == 2


# ---------------------------------------------------------------------------
# Entry structure
# ---------------------------------------------------------------------------

class TestSearchsetEntries:

    def test_entry_has_resource(self):
        p = _make_patient()
        b = build_searchset([p])
        assert b.entry[0].resource is p

    def test_entry_is_bundle_entry(self):
        b = build_searchset([_make_patient()])
        assert isinstance(b.entry[0], BundleEntry)

    def test_search_mode_match(self):
        b = build_searchset([_make_patient()])
        assert b.entry[0].search.mode == 'match'

    def test_search_is_typed(self):
        b = build_searchset([_make_patient()])
        assert isinstance(b.entry[0].search, BundleEntrySearch)

    def test_full_url_derived(self):
        b = build_searchset([_make_patient('abc-123')])
        assert b.entry[0].fullUrl == 'Patient/abc-123'

    def test_full_url_absent_when_no_id(self):
        p = Patient()
        b = build_searchset([p])
        assert 'fullUrl' not in b.entry[0].__dict__


# ---------------------------------------------------------------------------
# Dot-access convenience
# ---------------------------------------------------------------------------

class TestSearchsetDotAccess:

    def test_entry_resource_dot(self):
        p = _make_patient('p1')
        b = build_searchset([p])
        assert b.entry.resource.id == 'p1'

    def test_entry_search_mode_dot(self):
        b = build_searchset([_make_patient()])
        assert b.entry.search.mode == 'match'


# ---------------------------------------------------------------------------
# Empty searchset
# ---------------------------------------------------------------------------

class TestSearchsetEmpty:

    def test_empty_total_zero(self):
        b = build_searchset([])
        assert b.total == 0

    def test_empty_no_entries(self):
        b = build_searchset([])
        assert len(b.entry) == 0

    def test_empty_type(self):
        b = build_searchset([])
        assert b.type_ == 'searchset'


# ---------------------------------------------------------------------------
# Mixed resource types
# ---------------------------------------------------------------------------

class TestSearchsetMixed:

    def test_mixed_resources(self):
        p = _make_patient('p1')
        o = _make_observation('obs-1')
        b = build_searchset([p, o])
        assert len(b.entry) == 2
        assert isinstance(b.entry[0].resource, Patient)
        assert isinstance(b.entry[1].resource, Observation)
        assert b.entry[0].fullUrl == 'Patient/p1'
        assert b.entry[1].fullUrl == 'Observation/obs-1'


# ---------------------------------------------------------------------------
# Serialization round-trip
# ---------------------------------------------------------------------------

class TestSearchsetSerialization:

    def test_to_dict(self):
        b = build_searchset([_make_patient('p1')])
        d = b.to_dict()
        assert d['resourceType'] == 'Bundle'
        assert d['type'] == 'searchset'
        assert d['total'] == 1
        assert len(d['entry']) == 1
        assert d['entry'][0]['search']['mode'] == 'match'

    def test_to_json_roundtrip(self):
        p = _make_patient('p1')
        p.active = True
        b = build_searchset([p])
        j = b.to_json()
        data = json.loads(j)
        assert data['type'] == 'searchset'
        assert data['total'] == 1
        assert data['entry'][0]['search']['mode'] == 'match'
        assert data['entry'][0]['resource']['resourceType'] == 'Patient'

    def test_from_dict_roundtrip(self):
        b1 = build_searchset([_make_patient('p1'), _make_patient('p2')])
        d = b1.to_dict()
        b2 = Bundle.from_dict(d)
        assert b2.type_ == 'searchset'
        assert b2.total == 2
        assert b2.entry[0].search.mode == 'match'

    def test_from_json_roundtrip(self):
        b1 = build_searchset([_make_patient('p1')])
        j = b1.to_json()
        b2 = Bundle.from_json(j)
        assert b2.type_ == 'searchset'
        assert b2.total == 1
        assert b2.entry.search.mode == 'match'
