from __future__ import annotations

import json


from zato.fhir.r4_0_1.resources import (
    Observation, Patient,
)
from zato.fhir.r4_0_1.datatypes import (
    Address, CodeableConcept, Coding, ContactPoint, HumanName,
    Identifier, Meta, Period, Quantity, Reference,
)


class TestSingleComplexField:

    def test_meta_is_typed(self):
        p = Patient.from_dict({'resourceType': 'Patient', 'meta': {'versionId': '1'}})
        assert type(p.meta) is Meta
        assert p.meta.versionId == '1'

    def test_code_is_typed(self):
        o = Observation.from_dict({
            'resourceType': 'Observation', 'status': 'final',
            'code': {'text': 'BP'},
        })
        assert type(o.code) is CodeableConcept
        assert o.code.text == 'BP'

    def test_subject_reference_is_typed(self):
        o = Observation.from_dict({
            'resourceType': 'Observation', 'status': 'final',
            'code': {'text': 'x'},
            'subject': {'reference': 'Patient/1'},
        })
        assert type(o.subject) is Reference
        assert o.subject.reference == 'Patient/1'

    def test_marital_status_is_typed(self):
        p = Patient.from_dict({
            'resourceType': 'Patient',
            'maritalStatus': {
                'coding': [{'system': 'http://hl7.org/fhir/v3/MaritalStatus', 'code': 'M'}],
            },
        })
        assert type(p.maritalStatus) is CodeableConcept


class TestListComplexField:

    def test_name_list_typed(self):
        p = Patient.from_dict({
            'resourceType': 'Patient',
            'name': [{'family': 'Bright', 'given': ['Ada']}],
        })
        assert type(p.name[0]) is HumanName
        assert p.name[0].family == 'Bright'
        assert list(p.name[0].given) == ['Ada']

    def test_identifier_list_typed(self):
        p = Patient.from_dict({
            'resourceType': 'Patient',
            'identifier': [
                {'system': 'http://example.org', 'value': 'MRN-1'},
                {'system': 'http://example.org', 'value': 'MRN-2'},
            ],
        })
        assert len(p.identifier) == 2
        assert all(type(i) is Identifier for i in p.identifier)
        assert p.identifier[1].value == 'MRN-2'

    def test_telecom_list_typed(self):
        p = Patient.from_dict({
            'resourceType': 'Patient',
            'telecom': [{'system': 'phone', 'value': '555-0100'}],
        })
        assert type(p.telecom[0]) is ContactPoint
        assert p.telecom[0].value == '555-0100'

    def test_address_list_typed(self):
        p = Patient.from_dict({
            'resourceType': 'Patient',
            'address': [{'city': 'Tokyo', 'country': 'JP'}],
        })
        assert type(p.address[0]) is Address
        assert p.address[0].city == 'Tokyo'


class TestDeepNesting:

    def test_coding_inside_codeable_concept(self):
        o = Observation.from_dict({
            'resourceType': 'Observation', 'status': 'final',
            'code': {
                'coding': [{'system': 'http://loinc.org', 'code': '8867-4', 'display': 'HR'}],
            },
        })
        assert type(o.code.coding[0]) is Coding
        assert o.code.coding[0].code == '8867-4'

    def test_quantity_inside_backbone_element(self):
        o = Observation.from_dict({
            'resourceType': 'Observation', 'status': 'final',
            'code': {'text': 'x'},
            'referenceRange': [{'low': {'value': 60, 'unit': 'bpm'}}],
        })
        rr = o.referenceRange[0]
        assert type(rr.low) is Quantity
        assert rr.low.value == 60
        assert rr.low.unit == 'bpm'

    def test_period_inside_encounter(self):
        from zato.fhir.r4_0_1.resources import Encounter
        e = Encounter.from_dict({
            'resourceType': 'Encounter', 'status': 'finished',
            'class': {'code': 'AMB'},
            'period': {'start': '2024-01-01', 'end': '2024-01-02'},
        })
        assert type(e.period) is Period
        assert e.period.start == '2024-01-01'
        assert e.period.end == '2024-01-02'

    def test_three_levels_deep(self):
        p = Patient.from_dict({
            'resourceType': 'Patient',
            'identifier': [{
                'type': {
                    'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/v2-0203', 'code': 'MR'}],
                },
                'value': 'X-123',
            }],
        })
        assert type(p.identifier[0]) is Identifier
        assert type(p.identifier[0].type_) is CodeableConcept
        assert type(p.identifier[0].type_.coding[0]) is Coding
        assert p.identifier[0].type_.coding[0].code == 'MR'


class TestChoiceFieldTyping:

    def test_value_quantity_is_typed(self):
        o = Observation.from_dict({
            'resourceType': 'Observation', 'status': 'final',
            'code': {'text': 'x'},
            'valueQuantity': {'value': 72, 'unit': 'bpm'},
        })
        assert type(o.valueQuantity) is Quantity
        assert o.valueQuantity.value == 72

    def test_value_codeable_concept_is_typed(self):
        o = Observation.from_dict({
            'resourceType': 'Observation', 'status': 'final',
            'code': {'text': 'x'},
            'valueCodeableConcept': {'text': 'Positive'},
        })
        assert type(o.valueCodeableConcept) is CodeableConcept
        assert o.valueCodeableConcept.text == 'Positive'


class TestRoundTrip:

    def test_typed_objects_serialize_correctly(self):
        data = {
            'resourceType': 'Patient',
            'id': 'rt-1',
            'meta': {'versionId': '2'},
            'name': [{'family': 'Papadopoulos', 'given': ['Νίκος']}],
            'identifier': [{'system': 'http://example.org', 'value': 'ID-1'}],
            'address': [{'city': 'Athens', 'line': ['1 Ermou St']}],
        }
        p = Patient.from_dict(data)
        d = p.to_dict()

        assert d['meta']['versionId'] == '2'
        assert d['name'][0]['family'] == 'Papadopoulos'
        assert d['name'][0]['given'] == ['Νίκος']
        assert d['identifier'][0]['value'] == 'ID-1'
        assert d['address'][0]['city'] == 'Athens'

    def test_deep_nesting_round_trip(self):
        data = {
            'resourceType': 'Observation', 'status': 'final',
            'code': {
                'coding': [{'system': 'http://loinc.org', 'code': '8867-4'}],
                'text': 'Heart rate',
            },
            'valueQuantity': {'value': 72, 'unit': 'bpm'},
            'referenceRange': [{'low': {'value': 60}, 'high': {'value': 100}}],
        }
        o = Observation.from_dict(data)
        d = o.to_dict()

        assert d['code']['coding'][0]['code'] == '8867-4'
        assert d['valueQuantity']['value'] == 72
        assert d['referenceRange'][0]['low']['value'] == 60

    def test_from_json_round_trip_typed(self):
        raw = json.dumps({
            'resourceType': 'Patient',
            'name': [{'family': 'Tanaka', 'given': ['太郎']}],
        })
        p = Patient.from_json(raw)
        assert type(p.name[0]) is HumanName
        assert p.name[0].family == 'Tanaka'
        d = p.to_dict()
        assert d['name'][0]['family'] == 'Tanaka'


class TestPrimitivesStayPrimitive:

    def test_string_fields_not_wrapped(self):
        p = Patient.from_dict({'resourceType': 'Patient', 'id': 'p1', 'gender': 'male'})
        assert type(p.id) is str
        assert type(p.gender) is str

    def test_boolean_fields_not_wrapped(self):
        p = Patient.from_dict({'resourceType': 'Patient', 'active': True})
        assert type(p.active) is bool

    def test_list_of_primitives_not_wrapped(self):
        p = Patient.from_dict({
            'resourceType': 'Patient',
            'name': [{'family': 'X', 'given': ['A', 'B']}],
        })
        assert all(type(g) is str for g in p.name[0].given)
