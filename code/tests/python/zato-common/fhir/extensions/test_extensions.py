from __future__ import annotations


from zato.fhir.extensions import (
    add_extension,
    get_extension,
    get_extensions,
    get_extension_text,
    get_nested_extension,
    has_extension,
    remove_extension,
    set_extension,
    set_extension_text,
)
from zato.fhir.r4_0_1 import Patient

URL_WELLNESS_NOTE = 'http://example.org/fhir/StructureDefinition/wellness-visit-note'
URL_VITAMIN_FOLLOWUP = 'http://example.org/fhir/StructureDefinition/vitamin-d-routine-followup'
URL_ANNUAL_CHECKUP = 'http://example.org/fhir/StructureDefinition/annual-wellness-checkup'
URL_CHECKUP_LOCATION = 'http://example.org/fhir/StructureDefinition/wellness-visit-location'
URL_CHECKUP_ROOM = 'http://example.org/fhir/StructureDefinition/wellness-visit-room'


def _patient_dict_with_extension() -> dict:
    return {
        'resourceType': 'Patient',
        'extension': [
            {
                'url': URL_WELLNESS_NOTE,
                'valueString': 'Annual wellness visit completed; feeling great.',
            },
        ],
    }


class TestGetExtension:

    def test_returns_matching_value_by_url(self):
        resource = _patient_dict_with_extension()
        assert get_extension(resource, URL_WELLNESS_NOTE) == (
            'Annual wellness visit completed; feeling great.'
        )

    def test_returns_none_if_absent(self):
        resource = _patient_dict_with_extension()
        assert get_extension(resource, URL_VITAMIN_FOLLOWUP) is None

    def test_returns_first_value_when_multiple_same_url(self):
        resource = {
            'resourceType': 'Patient',
            'extension': [
                {'url': URL_ANNUAL_CHECKUP, 'valueString': 'First reminder'},
                {'url': URL_ANNUAL_CHECKUP, 'valueString': 'Second reminder'},
            ],
        }
        assert get_extension(resource, URL_ANNUAL_CHECKUP) == 'First reminder'

    def test_returns_whole_extension_dict_when_nested_without_value_field(self):
        complex_ext = {
            'url': URL_WELLNESS_NOTE,
            'extension': [
                {'url': 'text', 'valueString': 'Bring your vitamins list to the next visit.'},
            ],
        }
        resource = {'resourceType': 'Patient', 'extension': [complex_ext]}
        result = get_extension(resource, URL_WELLNESS_NOTE)
        assert result == complex_ext

    def test_complex_value_codeable_concept(self):
        concept = {
            'coding': [
                {
                    'system': 'http://loinc.org',
                    'code': '58410-2',
                    'display': 'CBC panel - Blood by Automated count',
                }
            ],
            'text': 'Routine blood panel for wellness screening',
        }
        resource = {
            'resourceType': 'Patient',
            'extension': [
                {'url': URL_VITAMIN_FOLLOWUP, 'valueCodeableConcept': concept},
            ],
        }
        assert get_extension(resource, URL_VITAMIN_FOLLOWUP) == concept


class TestGetExtensions:

    def test_returns_all_values_matching_url(self):
        resource = {
            'resourceType': 'Patient',
            'extension': [
                {'url': URL_ANNUAL_CHECKUP, 'valueString': 'Schedule A'},
                {'url': URL_VITAMIN_FOLLOWUP, 'valueString': 'Other'},
                {'url': URL_ANNUAL_CHECKUP, 'valueString': 'Schedule B'},
            ],
        }
        assert get_extensions(resource, URL_ANNUAL_CHECKUP) == ['Schedule A', 'Schedule B']

    def test_returns_empty_list_when_none_match(self):
        resource = _patient_dict_with_extension()
        assert get_extensions(resource, URL_ANNUAL_CHECKUP) == []


class TestHasExtension:

    def test_true_when_present(self):
        resource = _patient_dict_with_extension()
        assert has_extension(resource, URL_WELLNESS_NOTE) is True

    def test_false_when_absent(self):
        resource = _patient_dict_with_extension()
        assert has_extension(resource, URL_VITAMIN_FOLLOWUP) is False


class TestGetExtensionText:

    def test_returns_value_string_from_nested_text_sub_extension(self):
        resource = {
            'resourceType': 'Patient',
            'extension': [
                {
                    'url': URL_WELLNESS_NOTE,
                    'extension': [
                        {'url': 'text', 'valueString': 'Hydrate well before your lab draw.'},
                    ],
                },
            ],
        }
        assert (
            get_extension_text(resource, URL_WELLNESS_NOTE)
            == 'Hydrate well before your lab draw.'
        )

    def test_returns_none_when_text_sub_extension_missing(self):
        resource = _patient_dict_with_extension()
        assert get_extension_text(resource, URL_WELLNESS_NOTE) is None


class TestSetExtensionText:

    def test_sets_complex_extension_with_nested_text(self):
        resource: dict = {'resourceType': 'Patient'}
        set_extension_text(resource, URL_WELLNESS_NOTE, 'Remember to bring your supplement list.')
        assert resource['extension'] == [
            {
                'url': URL_WELLNESS_NOTE,
                'extension': [
                    {'url': 'text', 'valueString': 'Remember to bring your supplement list.'},
                ],
            },
        ]
        assert (
            get_extension_text(resource, URL_WELLNESS_NOTE)
            == 'Remember to bring your supplement list.'
        )


class TestSetExtension:

    def test_replaces_existing_extension_value(self):
        resource = _patient_dict_with_extension()
        set_extension(resource, URL_WELLNESS_NOTE, 'Updated: follow-up scheduled for next quarter.')
        exts = resource['extension']
        assert len(exts) == 1
        assert exts[0]['valueString'] == 'Updated: follow-up scheduled for next quarter.'

    def test_dict_value_merges_with_url(self):
        resource: dict = {'resourceType': 'Patient'}
        set_extension(
            resource,
            URL_VITAMIN_FOLLOWUP,
            {'valueBoolean': True},
        )
        assert resource['extension'] == [
            {'url': URL_VITAMIN_FOLLOWUP, 'valueBoolean': True},
        ]


class TestAddExtension:

    def test_appends_without_removing_existing_same_url(self):
        resource: dict = {'resourceType': 'Patient'}
        add_extension(resource, URL_ANNUAL_CHECKUP, 'Morning slot', value_type='string')
        add_extension(resource, URL_ANNUAL_CHECKUP, 'Afternoon slot', value_type='string')
        assert len(resource['extension']) == 2
        assert get_extensions(resource, URL_ANNUAL_CHECKUP) == ['Morning slot', 'Afternoon slot']


class TestRemoveExtension:

    def test_removes_all_matching_url_returns_true(self):
        resource = {
            'resourceType': 'Patient',
            'extension': [
                {'url': URL_ANNUAL_CHECKUP, 'valueString': 'A'},
                {'url': URL_ANNUAL_CHECKUP, 'valueString': 'B'},
            ],
        }
        assert remove_extension(resource, URL_ANNUAL_CHECKUP) is True
        assert resource['extension'] == []

    def test_returns_false_when_nothing_removed(self):
        resource = _patient_dict_with_extension()
        assert remove_extension(resource, URL_ANNUAL_CHECKUP) is False
        assert len(resource['extension']) == 1


class TestGetNestedExtension:

    def test_follows_chain_of_sub_extension_urls(self):
        resource = {
            'resourceType': 'Patient',
            'extension': [
                {
                    'url': URL_ANNUAL_CHECKUP,
                    'extension': [
                        {
                            'url': URL_CHECKUP_LOCATION,
                            'extension': [
                                {
                                    'url': URL_CHECKUP_ROOM,
                                    'valueString': 'Sunshine Suite',
                                },
                            ],
                        },
                    ],
                },
            ],
        }
        assert (
            get_nested_extension(
                resource,
                URL_ANNUAL_CHECKUP,
                URL_CHECKUP_LOCATION,
                URL_CHECKUP_ROOM,
            )
            == 'Sunshine Suite'
        )


class TestExtensionDictResource:

    def test_round_trip_on_plain_dict(self):
        resource: dict = {'resourceType': 'Patient', 'id': 'wellness-1'}
        set_extension(resource, URL_WELLNESS_NOTE, 'Routine visit - all markers look good.')
        assert get_extension(resource, URL_WELLNESS_NOTE) == (
            'Routine visit - all markers look good.'
        )
        assert remove_extension(resource, URL_WELLNESS_NOTE) is True
        assert get_extension(resource, URL_WELLNESS_NOTE) is None


class TestExtensionFHIRResourcePatient:

    def test_get_and_set_on_patient_instance(self):
        patient = Patient()
        patient.id = 'patient-wellness-1'
        set_extension(patient, URL_WELLNESS_NOTE, 'Enjoyed the guided stretching session.')
        assert get_extension(patient, URL_WELLNESS_NOTE) == (
            'Enjoyed the guided stretching session.'
        )
        assert has_extension(patient, URL_WELLNESS_NOTE) is True

    def test_add_extension_patient_accumulates(self):
        patient = Patient()
        add_extension(patient, URL_VITAMIN_FOLLOWUP, 'Level checked - continue current plan.')
        add_extension(patient, URL_VITAMIN_FOLLOWUP, 'Recheck in twelve months.')
        assert get_extensions(patient, URL_VITAMIN_FOLLOWUP) == [
            'Level checked - continue current plan.',
            'Recheck in twelve months.',
        ]

    def test_set_extension_text_on_patient(self):
        patient = Patient()
        set_extension_text(patient, URL_WELLNESS_NOTE, 'Pack a water bottle for your walk-in visit.')
        assert get_extension_text(patient, URL_WELLNESS_NOTE) == (
            'Pack a water bottle for your walk-in visit.'
        )

    def test_get_nested_extension_on_patient(self):
        patient = Patient()
        patient.extension = [
            {
                'url': URL_ANNUAL_CHECKUP,
                'extension': [
                    {
                        'url': URL_CHECKUP_LOCATION,
                        'valueString': 'Community Wellness Center',
                    },
                ],
            },
        ]
        assert (
            get_nested_extension(patient, URL_ANNUAL_CHECKUP, URL_CHECKUP_LOCATION)
            == 'Community Wellness Center'
        )

    def test_codeable_concept_on_patient_via_set_extension(self):
        patient = Patient()
        set_extension(
            patient,
            URL_VITAMIN_FOLLOWUP,
            {
                'valueCodeableConcept': {
                    'coding': [
                        {
                            'system': 'http://snomed.info/sct',
                            'code': '409073007',
                            'display': 'Education about balanced nutrition',
                        }
                    ],
                    'text': 'Healthy eating tips discussed',
                },
            },
        )
        value = get_extension(patient, URL_VITAMIN_FOLLOWUP)
        assert value['coding'][0]['display'] == 'Education about balanced nutrition'
