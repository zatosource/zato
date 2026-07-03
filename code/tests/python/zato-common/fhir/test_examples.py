# Generated - do not edit
from __future__ import annotations

import json
from pathlib import Path


from zato.fhir.r4_0_1 import Patient, Observation, Encounter, Practitioner, Organization

EXAMPLES_DIR = Path(__file__).parent / 'examples'


class TestPatientExample:

    def test_parse_patient_example(self):
        with open(EXAMPLES_DIR / 'patient-example.json') as f:
            data = json.load(f)

        p = Patient.from_dict(data)

        assert p.id == 'example'
        assert p.gender == 'male'
        assert p.birthDate == '1974-12-25'
        assert p.active is True

    def test_patient_example_has_name(self):
        with open(EXAMPLES_DIR / 'patient-example.json') as f:
            data = json.load(f)

        p = Patient.from_dict(data)

        assert p.name is not None
        assert len(p.name) == 2
        assert p.name[0].family == 'Smith'
        assert list(p.name[0].given) == ['John', 'Jacob']

    def test_patient_example_has_identifier(self):
        with open(EXAMPLES_DIR / 'patient-example.json') as f:
            data = json.load(f)

        p = Patient.from_dict(data)

        assert p.identifier is not None
        assert len(p.identifier) == 1
        assert p.identifier[0].value == '12345'

    def test_patient_example_has_telecom(self):
        with open(EXAMPLES_DIR / 'patient-example.json') as f:
            data = json.load(f)

        p = Patient.from_dict(data)

        assert p.telecom is not None
        assert len(p.telecom) == 2

    def test_patient_example_has_address(self):
        with open(EXAMPLES_DIR / 'patient-example.json') as f:
            data = json.load(f)

        p = Patient.from_dict(data)

        assert p.address is not None
        assert len(p.address) == 1
        assert p.address[0].city == 'PleasantVille'

    def test_patient_example_roundtrip(self):
        with open(EXAMPLES_DIR / 'patient-example.json') as f:
            original = json.load(f)

        p = Patient.from_dict(original)
        serialized = p.to_dict()

        assert serialized['resourceType'] == 'Patient'
        assert serialized['id'] == 'example'
        assert serialized['gender'] == 'male'


class TestObservationExample:

    def test_parse_observation_example(self):
        with open(EXAMPLES_DIR / 'observation-example.json') as f:
            data = json.load(f)

        o = Observation.from_dict(data)

        assert o.id == 'example'
        assert o.status == 'final'

    def test_observation_example_has_code(self):
        with open(EXAMPLES_DIR / 'observation-example.json') as f:
            data = json.load(f)

        o = Observation.from_dict(data)

        assert o.code is not None
        assert o.code.coding[0].code == '15074-8'

    def test_observation_example_has_value(self):
        with open(EXAMPLES_DIR / 'observation-example.json') as f:
            data = json.load(f)

        o = Observation.from_dict(data)
        d = o.to_dict()

        assert 'valueQuantity' in d
        assert d['valueQuantity']['value'] == 6.3

    def test_observation_example_has_subject(self):
        with open(EXAMPLES_DIR / 'observation-example.json') as f:
            data = json.load(f)

        o = Observation.from_dict(data)

        assert o.subject is not None
        assert o.subject.reference == 'Patient/example'

    def test_observation_example_roundtrip(self):
        with open(EXAMPLES_DIR / 'observation-example.json') as f:
            original = json.load(f)

        o = Observation.from_dict(original)
        serialized = o.to_dict()

        assert serialized['resourceType'] == 'Observation'
        assert serialized['id'] == 'example'
        assert serialized['status'] == 'final'


class TestEncounterExample:

    def test_parse_encounter_example(self):
        with open(EXAMPLES_DIR / 'encounter-example.json') as f:
            data = json.load(f)

        e = Encounter.from_dict(data)

        assert e.id == 'example'
        assert e.status == 'finished'

    def test_encounter_example_has_class(self):
        with open(EXAMPLES_DIR / 'encounter-example.json') as f:
            data = json.load(f)

        e = Encounter.from_dict(data)

        assert e.class_ is not None

    def test_encounter_example_has_subject(self):
        with open(EXAMPLES_DIR / 'encounter-example.json') as f:
            data = json.load(f)

        e = Encounter.from_dict(data)

        assert e.subject is not None
        assert e.subject.reference == 'Patient/example'

    def test_encounter_example_has_period(self):
        with open(EXAMPLES_DIR / 'encounter-example.json') as f:
            data = json.load(f)

        e = Encounter.from_dict(data)

        assert e.period is not None
        assert e.period.start is not None

    def test_encounter_example_roundtrip(self):
        with open(EXAMPLES_DIR / 'encounter-example.json') as f:
            original = json.load(f)

        e = Encounter.from_dict(original)
        serialized = e.to_dict()

        assert serialized['resourceType'] == 'Encounter'
        assert serialized['id'] == 'example'


class TestPractitionerExample:

    def test_parse_practitioner_example(self):
        with open(EXAMPLES_DIR / 'practitioner-example.json') as f:
            data = json.load(f)

        pr = Practitioner.from_dict(data)

        assert pr.id == 'example'
        assert pr.active is True
        assert pr.gender == 'female'

    def test_practitioner_example_has_name(self):
        with open(EXAMPLES_DIR / 'practitioner-example.json') as f:
            data = json.load(f)

        pr = Practitioner.from_dict(data)

        assert pr.name is not None
        assert pr.name[0].family == 'Jones'

    def test_practitioner_example_has_qualification(self):
        with open(EXAMPLES_DIR / 'practitioner-example.json') as f:
            data = json.load(f)

        pr = Practitioner.from_dict(data)
        d = pr.to_dict()

        assert 'qualification' in d
        assert len(d['qualification']) == 1

    def test_practitioner_example_roundtrip(self):
        with open(EXAMPLES_DIR / 'practitioner-example.json') as f:
            original = json.load(f)

        pr = Practitioner.from_dict(original)
        serialized = pr.to_dict()

        assert serialized['resourceType'] == 'Practitioner'
        assert serialized['id'] == 'example'


class TestOrganizationExample:

    def test_parse_organization_example(self):
        with open(EXAMPLES_DIR / 'organization-example.json') as f:
            data = json.load(f)

        org = Organization.from_dict(data)

        assert org.id == 'example'
        assert org.name == 'Acme Healthcare'
        assert org.active is True

    def test_organization_example_has_identifier(self):
        with open(EXAMPLES_DIR / 'organization-example.json') as f:
            data = json.load(f)

        org = Organization.from_dict(data)

        assert org.identifier is not None
        assert len(org.identifier) == 2

    def test_organization_example_has_telecom(self):
        with open(EXAMPLES_DIR / 'organization-example.json') as f:
            data = json.load(f)

        org = Organization.from_dict(data)

        assert org.telecom is not None
        assert len(org.telecom) == 3

    def test_organization_example_has_address(self):
        with open(EXAMPLES_DIR / 'organization-example.json') as f:
            data = json.load(f)

        org = Organization.from_dict(data)

        assert org.address is not None
        assert org.address[0].city == 'PleasantVille'

    def test_organization_example_roundtrip(self):
        with open(EXAMPLES_DIR / 'organization-example.json') as f:
            original = json.load(f)

        org = Organization.from_dict(original)
        serialized = org.to_dict()

        assert serialized['resourceType'] == 'Organization'
        assert serialized['id'] == 'example'
        assert serialized['name'] == 'Acme Healthcare'


class TestBundleExample:

    def test_parse_bundle_example(self):
        with open(EXAMPLES_DIR / 'bundle-example.json') as f:
            data = json.load(f)

        assert data['resourceType'] == 'Bundle'
        assert data['type'] == 'collection'
        assert len(data['entry']) == 2

    def test_bundle_contains_patient(self):
        with open(EXAMPLES_DIR / 'bundle-example.json') as f:
            data = json.load(f)

        patient_entry = data['entry'][0]
        p = Patient.from_dict(patient_entry['resource'])

        assert p.id == 'example'
        assert p.gender == 'male'

    def test_bundle_contains_observation(self):
        with open(EXAMPLES_DIR / 'bundle-example.json') as f:
            data = json.load(f)

        obs_entry = data['entry'][1]
        o = Observation.from_dict(obs_entry['resource'])

        assert o.id == 'example'
        assert o.status == 'final'
