# Generated - do not edit
from __future__ import annotations

import json

from zato.fhir.r4_0_1 import Patient, Observation, Encounter, Practitioner, Organization
from zato.fhir.r4_0_1.datatypes import Identifier, CodeableConcept, Coding


class TestSerializationRoundtrip:

    def test_roundtrip_patient(self):
        p = Patient()
        p.id = 'test-patient-001'
        p.name.family = 'Smith'
        p.name.given = 'John'
        p.gender = 'male'
        p.birthDate = '1980-01-15'

        json_str = p.to_json()
        p2 = Patient.from_json(json_str)

        assert p2.id == 'test-patient-001'
        assert p2.gender == 'male'
        assert p2.birthDate == '1980-01-15'

    def test_roundtrip_observation(self):
        o = Observation()
        o.id = 'test-obs-001'
        o.status = 'final'

        json_str = o.to_json()
        o2 = Observation.from_json(json_str)

        assert o2.id == 'test-obs-001'
        assert o2.status == 'final'

    def test_roundtrip_encounter(self):
        e = Encounter()
        e.id = 'test-enc-001'
        e.status = 'finished'

        json_str = e.to_json()
        e2 = Encounter.from_json(json_str)

        assert e2.id == 'test-enc-001'
        assert e2.status == 'finished'

    def test_roundtrip_practitioner(self):
        pr = Practitioner()
        pr.id = 'test-pract-001'
        pr.name.family = 'Jones'
        pr.name.given = 'Mary'

        json_str = pr.to_json()
        pr2 = Practitioner.from_json(json_str)

        assert pr2.id == 'test-pract-001'

    def test_roundtrip_organization(self):
        org = Organization()
        org.id = 'test-org-001'
        org.name = 'Test Hospital'

        json_str = org.to_json()
        org2 = Organization.from_json(json_str)

        assert org2.id == 'test-org-001'
        assert org2.name == 'Test Hospital'


class TestSerializationPreservesData:

    def test_preserves_nested_objects(self):
        p = Patient()
        p.id = 'nested-test'
        p.name.family = 'Doe'
        p.name.given = 'Jane'
        p.name.prefix = 'Dr'

        d = p.to_dict()
        assert d['name'][0]['family'] == 'Doe'
        assert d['name'][0]['given'] == ['Jane']
        assert d['name'][0]['prefix'] == ['Dr']

    def test_preserves_lists(self):
        p = Patient()
        p.id = 'list-test'

        id1 = Identifier()
        id1.system = 'http://hospital.org/mrn'
        id1.value = 'MRN001'

        id2 = Identifier()
        id2.system = 'http://hospital.org/ssn'
        id2.value = 'SSN001'

        p.identifier = [id1, id2]

        d = p.to_dict()
        assert len(d['identifier']) == 2
        assert d['identifier'][0]['value'] == 'MRN001'
        assert d['identifier'][1]['value'] == 'SSN001'

    def test_preserves_codeable_concept(self):
        o = Observation()
        o.id = 'code-test'
        o.status = 'final'

        code = CodeableConcept()
        coding = Coding()
        coding.system = 'http://loinc.org'
        coding.code = '12345-6'
        coding.display = 'Test Code'
        code.coding = [coding]
        code.text = 'Test Code Text'

        o.code = code

        d = o.to_dict()
        assert d['code']['coding'][0]['system'] == 'http://loinc.org'
        assert d['code']['coding'][0]['code'] == '12345-6'
        assert d['code']['text'] == 'Test Code Text'


class TestSerializationJson:

    def test_to_json_valid_json(self):
        p = Patient()
        p.id = 'json-test'
        p.name.family = 'Test'

        json_str = p.to_json()
        parsed = json.loads(json_str)

        assert parsed['resourceType'] == 'Patient'
        assert parsed['id'] == 'json-test'

    def test_to_json_indent(self):
        p = Patient()
        p.id = 'indent-test'

        json_str = p.to_json(indent=2)
        assert '\n' in json_str
        assert '  ' in json_str

    def test_to_json_no_indent(self):
        p = Patient()
        p.id = 'no-indent-test'

        json_str = p.to_json()
        assert '\n' not in json_str


class TestFromJson:

    def test_from_json_simple(self):
        json_str = '{"resourceType": "Patient", "id": "from-json-1", "gender": "female"}'
        p = Patient.from_json(json_str)

        assert p.id == 'from-json-1'
        assert p.gender == 'female'

    def test_from_dict_simple(self):
        data = {'resourceType': 'Patient', 'id': 'from-dict-1', 'birthDate': '1990-05-20'}
        p = Patient.from_dict(data)

        assert p.id == 'from-dict-1'
        assert p.birthDate == '1990-05-20'

    def test_from_json_with_nested(self):
        json_str = '''
        {
            "resourceType": "Patient",
            "id": "nested-json-1",
            "name": [{"family": "Johnson", "given": ["Bob"]}]
        }
        '''
        p = Patient.from_json(json_str)

        assert p.id == 'nested-json-1'
        assert p.name[0].family == 'Johnson'


class TestDecimalPrecision:

    def test_value_quantity_decimal_preserved(self):
        o = Observation()
        o.id = 'wellness-temp-1'
        o.status = 'final'
        o.code = {'coding': [{'code': 'wellness-check'}]}
        o.valueQuantity = {
            'value': 37.2,
            'unit': 'C',
            'system': 'http://unitsofmeasure.org',
            'code': 'Cel',
        }
        d = o.to_dict()
        assert d['valueQuantity']['value'] == 37.2


class TestUnicodeHandling:

    def test_name_roundtrip_preserves_unicode(self):
        p = Patient()
        p.id = 'unicode-wellness-1'
        p.name = [{
            'family': 'Müller',
            'given': ['ゆき', 'Σωκράτης'],
        }]
        json_str = p.to_json()
        p2 = Patient.from_json(json_str)
        assert p2.name[0].family == 'Müller'
        assert list(p2.name[0].given) == ['ゆき', 'Σωκράτης']


class TestNullVsAbsent:

    def test_unset_fields_omitted_from_dict(self):
        p = Patient()
        p.id = 'minimal-wellness-1'
        d = p.to_dict()
        assert 'gender' not in d
        assert 'name' not in d
        assert 'birthDate' not in d


class TestEmptyArrays:

    def test_empty_identifier_omitted_from_dict(self):
        p = Patient()
        p.id = 'empty-id-list-1'
        p.identifier = []
        d = p.to_dict()
        assert 'identifier' not in d


class TestContainedResourceSerialization:

    def test_contained_in_dict(self):
        p = Patient()
        p.id = 'bundle-style-wellness-1'
        p.contained = [{
            'resourceType': 'Observation',
            'id': 'contained-vitamins',
            'status': 'final',
            'code': {'coding': [{'code': 'wellness-check'}]},
        }]
        d = p.to_dict()
        assert 'contained' in d
        assert len(d['contained']) == 1
        assert d['contained'][0]['id'] == 'contained-vitamins'


class TestFromJsonEdgeCases:

    def test_extra_unknown_fields_parse(self):
        json_str = '{"resourceType": "Patient", "id": "extra-fields-1", "favoriteVitamin": "C"}'
        p = Patient.from_json(json_str)
        assert p.id == 'extra-fields-1'

    def test_missing_resourceType_parses(self):
        p = Patient.from_json('{"id": "no-type-1"}')
        assert p.id == 'no-type-1'
