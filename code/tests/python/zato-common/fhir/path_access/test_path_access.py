from __future__ import annotations

from zato.fhir.path_access import _parse_path, get_path, set_path
from zato.fhir.r4_0_1 import HumanName, Identifier, Patient


def _wellness_patient() -> Patient:
    patient = Patient()
    patient.id = 'routine-checkup-sunny-01'
    primary = HumanName()
    primary.family = 'Brightwell'
    primary.given = ['Jordan']
    patient.name = [primary]
    member_id = Identifier()
    member_id.system = 'urn:wellness-clinic:members'
    member_id.value = 'vitamins-wellness-plan-42'
    patient.identifier = [member_id]
    return patient


class TestGetPath:

    def test_simple_field(self):
        patient = _wellness_patient()
        assert get_path(patient, 'id') == 'routine-checkup-sunny-01'

    def test_nested_field(self):
        patient = _wellness_patient()
        assert get_path(patient, 'name[0].family') == 'Brightwell'

    def test_array_index(self):
        patient = _wellness_patient()
        assert get_path(patient, 'identifier[0].value') == 'vitamins-wellness-plan-42'

    def test_nonexistent_path_returns_none(self):
        patient = _wellness_patient()
        assert get_path(patient, 'telecom[0].value') is None

    def test_resource_prefix(self):
        patient = _wellness_patient()
        assert get_path(patient, 'Patient.id') == 'routine-checkup-sunny-01'


class TestSetPath:

    def test_simple_field(self):
        patient = _wellness_patient()
        assert set_path(patient, 'id', 'annual-wellness-updated') is True
        assert patient.id == 'annual-wellness-updated'

    def test_nested_field(self):
        patient = _wellness_patient()
        assert set_path(patient, 'name[0].family', 'Sunnybrook') is True
        assert get_path(patient, 'name[0].family') == 'Sunnybrook'

    def test_array_index(self):
        patient = _wellness_patient()
        assert set_path(patient, 'identifier[0].value', 'daily-multivitamin-ref-9') is True
        assert get_path(patient, 'identifier[0].value') == 'daily-multivitamin-ref-9'

    def test_resource_prefix(self):
        patient = _wellness_patient()
        assert set_path(patient, 'Patient.id', 'wellness-chart-refresh') is True
        assert patient.id == 'wellness-chart-refresh'

    def test_meta_object(self):
        patient = _wellness_patient()
        assert set_path(patient, 'meta', {'versionId': '1', 'lastUpdated': '2026-04-06T12:00:00Z'}) is True
        meta = get_path(patient, 'meta')
        assert meta.versionId == '1'


class TestParsePath:

    def test_simple_path(self):
        assert list(_parse_path('id')) == [{'type': 'field', 'name': 'id'}]

    def test_dotted_path(self):
        assert list(_parse_path('meta.versionId')) == [
            {'type': 'field', 'name': 'meta'},
            {'type': 'field', 'name': 'versionId'},
        ]

    def test_array_bracket_notation(self):
        assert list(_parse_path('name[0].family')) == [
            {'type': 'field', 'name': 'name'},
            {'type': 'index', 'index': 0},
            {'type': 'field', 'name': 'family'},
        ]

    def test_resource_prefix(self):
        assert list(_parse_path('Patient.identifier[0].value')) == [
            {'type': 'field', 'name': 'identifier'},
            {'type': 'index', 'index': 0},
            {'type': 'field', 'name': 'value'},
        ]
