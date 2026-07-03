"""Tests that extension value[x] keys use correct FHIR casing.

FHIR requires that value keys preserve the original type casing:
  dateTime  -> valueDateTime   (NOT valueDatetime)
  base64Binary -> valueBase64Binary (NOT valueBase64binary)
  CodeableConcept -> valueCodeableConcept

This verifies add_extension produces the right key for every
Extension value[x] type defined in FHIR R4 4.0.1.
"""
from __future__ import annotations

import pytest

from zato.fhir.extensions import add_extension, get_extension
from zato.fhir.r4_0_1 import Patient
from zato.fhir.r4_0_1.datatypes import Extension


PRIMITIVE_VALUE_TYPES = [
    ('base64Binary', 'dGVzdA==', 'valueBase64Binary'),
    ('boolean', True, 'valueBoolean'),
    ('canonical', 'http://example.org/StructureDefinition/x', 'valueCanonical'),
    ('code', 'active', 'valueCode'),
    ('date', '2024-01-15', 'valueDate'),
    ('dateTime', '2024-01-15T10:30:00Z', 'valueDateTime'),
    ('decimal', '3.14', 'valueDecimal'),
    ('id', 'abc-123', 'valueId'),
    ('instant', '2024-01-15T10:30:00.000Z', 'valueInstant'),
    ('integer', 42, 'valueInteger'),
    ('markdown', '**bold**', 'valueMarkdown'),
    ('oid', 'urn:oid:2.16.840.1.113883', 'valueOid'),
    ('positiveInt', 1, 'valuePositiveInt'),
    ('string', 'hello', 'valueString'),
    ('time', '14:30:00', 'valueTime'),
    ('unsignedInt', 0, 'valueUnsignedInt'),
    ('uri', 'urn:uuid:abc', 'valueUri'),
    ('url', 'https://example.org', 'valueUrl'),
    ('uuid', 'urn:uuid:c757873d-ec9a-4326-a141-556f43239520', 'valueUuid'),
]

COMPLEX_VALUE_TYPES = [
    ('Address', {'city': 'Boston'}, 'valueAddress'),
    ('Age', {'value': 30, 'unit': 'years'}, 'valueAge'),
    ('Annotation', {'text': 'Note'}, 'valueAnnotation'),
    ('Attachment', {'contentType': 'text/plain'}, 'valueAttachment'),
    ('CodeableConcept', {'text': 'Test'}, 'valueCodeableConcept'),
    ('Coding', {'system': 'http://loinc.org', 'code': '1234'}, 'valueCoding'),
    ('ContactPoint', {'system': 'phone', 'value': '555-0100'}, 'valueContactPoint'),
    ('Count', {'value': 5}, 'valueCount'),
    ('Distance', {'value': 10, 'unit': 'km'}, 'valueDistance'),
    ('Duration', {'value': 60, 'unit': 'min'}, 'valueDuration'),
    ('HumanName', {'family': 'Smith'}, 'valueHumanName'),
    ('Identifier', {'system': 'http://example.org', 'value': 'ID-1'}, 'valueIdentifier'),
    ('Money', {'value': 100, 'currency': 'USD'}, 'valueMoney'),
    ('Period', {'start': '2024-01-01'}, 'valuePeriod'),
    ('Quantity', {'value': 120, 'unit': 'mmHg'}, 'valueQuantity'),
    ('Range', {'low': {'value': 1}, 'high': {'value': 10}}, 'valueRange'),
    ('Ratio', {'numerator': {'value': 1}}, 'valueRatio'),
    ('Reference', {'reference': 'Patient/1'}, 'valueReference'),
    ('SampledData', {'origin': {'value': 0}}, 'valueSampledData'),
    ('Signature', {'when': '2024-01-15T10:30:00Z'}, 'valueSignature'),
    ('Timing', {'event': ['2024-01-15']}, 'valueTiming'),
    ('ContactDetail', {'name': 'Dr. Smith'}, 'valueContactDetail'),
    ('Contributor', {'type': 'author', 'name': 'J Doe'}, 'valueContributor'),
    ('DataRequirement', {'type': 'Patient'}, 'valueDataRequirement'),
    ('Expression', {'language': 'text/fhirpath'}, 'valueExpression'),
    ('ParameterDefinition', {'use': 'in', 'type': 'string'}, 'valueParameterDefinition'),
    ('RelatedArtifact', {'type': 'documentation'}, 'valueRelatedArtifact'),
    ('TriggerDefinition', {'type': 'named-event'}, 'valueTriggerDefinition'),
    ('UsageContext', {'code': {'code': 'focus'}}, 'valueUsageContext'),
    ('Dosage', {'text': 'Take 1 tab daily'}, 'valueDosage'),
    ('Meta', {'versionId': '1'}, 'valueMeta'),
]


@pytest.mark.parametrize(
    'value_type, value, expected_key',
    PRIMITIVE_VALUE_TYPES,
    ids=[t[0] for t in PRIMITIVE_VALUE_TYPES],
)
class TestPrimitiveValueKeyCasing:

    def test_add_extension_produces_correct_key_on_dict(self, value_type, value, expected_key):
        resource = {'resourceType': 'Patient'}
        add_extension(resource, 'http://example.org/ext', value, value_type)
        ext = resource['extension'][0]
        assert expected_key in ext, f'Expected key {expected_key}, got keys {list(ext.keys())}'
        assert ext[expected_key] == value

    def test_add_extension_produces_correct_key_on_patient(self, value_type, value, expected_key):
        p = Patient()
        add_extension(p, 'http://example.org/ext', value, value_type)
        result = get_extension(p, 'http://example.org/ext')
        assert result == value


@pytest.mark.parametrize(
    'value_type, value, expected_key',
    COMPLEX_VALUE_TYPES,
    ids=[t[0] for t in COMPLEX_VALUE_TYPES],
)
class TestComplexValueKeyCasing:

    def test_add_extension_produces_correct_key_on_dict(self, value_type, value, expected_key):
        resource = {'resourceType': 'Patient'}
        add_extension(resource, 'http://example.org/ext', value, value_type)
        ext = resource['extension'][0]
        assert expected_key in ext, f'Expected key {expected_key}, got keys {list(ext.keys())}'

    def test_get_extension_returns_complex_value(self, value_type, value, expected_key):
        resource = {'resourceType': 'Patient'}
        add_extension(resource, 'http://example.org/ext', value, value_type)
        result = get_extension(resource, 'http://example.org/ext')
        assert result is not None


class TestExtensionChoiceFieldsOnClass:

    def test_extension_has_choice_fields(self):
        assert hasattr(Extension, '_choice_fields')
        assert 'value' in Extension._choice_fields

    def test_extension_choice_fields_include_all_primitive_types(self):
        choice_names = Extension._choice_fields['value']
        for _, _, expected_key in PRIMITIVE_VALUE_TYPES:
            assert expected_key in choice_names, f'{expected_key} not in Extension._choice_fields'

    def test_extension_choice_fields_include_all_complex_types(self):
        choice_names = Extension._choice_fields['value']
        for _, _, expected_key in COMPLEX_VALUE_TYPES:
            assert expected_key in choice_names, f'{expected_key} not in Extension._choice_fields'

    def test_extension_value_fields_have_annotations(self):
        for _, _, expected_key in PRIMITIVE_VALUE_TYPES:
            assert expected_key in Extension.__annotations__, (
                f'{expected_key} not in Extension.__annotations__'
            )


class TestExtensionRoundTripCasing:

    def test_from_dict_preserves_value_key(self):
        data = {
            'resourceType': 'Patient',
            'extension': [
                {'url': 'http://example.org/dt', 'valueDateTime': '2024-01-15T10:30:00Z'},
                {'url': 'http://example.org/b64', 'valueBase64Binary': 'dGVzdA=='},
                {'url': 'http://example.org/cc', 'valueCodeableConcept': {'text': 'Test'}},
            ]
        }
        p = Patient.from_dict(data)
        d = p.to_dict()
        exts = d.get('extension', [])
        assert len(exts) == 3
        assert 'valueDateTime' in exts[0]
        assert 'valueBase64Binary' in exts[1]
        assert 'valueCodeableConcept' in exts[2]


class TestNoSpuriousEmptyExtensions:

    def test_add_extension_does_not_create_empty_extension_objects(self):
        p = Patient()
        add_extension(p, 'http://example.org/ext', 'test', 'string')
        ext_list = object.__getattribute__(p, '__dict__').get('extension')
        assert len(ext_list) == 1
        item = ext_list[0]
        assert isinstance(item, dict)
        assert item['url'] == 'http://example.org/ext'
        assert item['valueString'] == 'test'

    def test_multiple_add_extension_no_empty_objects(self):
        p = Patient()
        add_extension(p, 'http://example.org/ext1', 'a', 'string')
        add_extension(p, 'http://example.org/ext2', 'b', 'string')
        ext_list = object.__getattribute__(p, '__dict__').get('extension')
        assert len(ext_list) == 2
        for item in ext_list:
            assert isinstance(item, dict)
