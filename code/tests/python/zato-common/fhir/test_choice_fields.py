from __future__ import annotations

import json


from zato.fhir.r4_0_1.resources import (
    Observation,
    Condition,
    MedicationRequest,
)
from zato.fhir.validation import validate


class TestChoiceFieldDictAssignment:

    def test_dict_assigns_and_roundtrips(self):
        o = Observation()
        o.status = 'final'
        o.code = {'text': 'Body Weight'}
        o.valueQuantity = {'value': 72, 'unit': 'kg'}
        d = o.to_dict()
        assert d['valueQuantity'] == {'value': 72, 'unit': 'kg'}

    def test_dict_assignment_creates_typed_object(self):
        o = Observation()
        o.valueQuantity = {'value': 72, 'unit': 'kg'}
        assert type(o.valueQuantity).__name__ == 'Quantity'

    def test_primitive_choice_stays_primitive(self):
        o = Observation()
        o.valueString = 'normal'
        assert isinstance(o.valueString, str)
        assert o.valueString == 'normal'

    def test_primitive_choice_roundtrip(self):
        o = Observation()
        o.status = 'final'
        o.code = {'text': 'test'}
        o.valueBoolean = True
        d = o.to_dict()
        assert d['valueBoolean'] is True

    def test_datetime_choice_stays_string(self):
        o = Observation()
        o.effectiveDateTime = '2024-06-15T10:30:00Z'
        assert isinstance(o.effectiveDateTime, str)

    def test_condition_onset_dict(self):
        c = Condition()
        c.subject = {'reference': 'Patient/1'}
        c.onsetAge = {'value': 40, 'unit': 'a'}
        d = c.to_dict()
        assert d['onsetAge'] == {'value': 40, 'unit': 'a'}

    def test_medication_request_dict(self):
        m = MedicationRequest()
        m.status = 'active'
        m.intent = 'order'
        m.subject = {'reference': 'Patient/1'}
        m.medicationCodeableConcept = {
            'coding': [{'system': 'http://example.org', 'code': 'vit-c', 'display': 'Vitamin C'}]
        }
        d = m.to_dict()
        assert 'medicationCodeableConcept' in d
        assert d['medicationCodeableConcept']['coding'][0]['display'] == 'Vitamin C'


class TestChoiceFieldTypedAccess:

    def test_quantity_value_access(self):
        o = Observation()
        o.valueQuantity = {'value': 72, 'unit': 'kg'}
        assert o.valueQuantity.value == 72
        assert o.valueQuantity.unit == 'kg'

    def test_period_access(self):
        o = Observation()
        o.effectivePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        assert o.effectivePeriod.start == '2024-01-01'
        assert o.effectivePeriod.end == '2024-12-31'

    def test_codeable_concept_access(self):
        o = Observation()
        o.valueCodeableConcept = {
            'coding': [{'system': 'http://example.org', 'code': 'A', 'display': 'All good'}],
            'text': 'All good'
        }
        assert o.valueCodeableConcept.text == 'All good'

    def test_condition_onset_age_access(self):
        c = Condition()
        c.onsetAge = {'value': 40, 'unit': 'a', 'system': 'http://unitsofmeasure.org'}
        assert c.onsetAge.value == 40
        assert c.onsetAge.unit == 'a'

    def test_range_access(self):
        o = Observation()
        o.valueRange = {'low': {'value': 60, 'unit': 'kg'}, 'high': {'value': 80, 'unit': 'kg'}}
        assert o.valueRange.low.value == 60
        assert o.valueRange.low.unit == 'kg'
        assert o.valueRange.high.value == 80
        assert o.valueRange.high.unit == 'kg'

    def test_ratio_access(self):
        o = Observation()
        o.valueRatio = {
            'numerator': {'value': 1, 'unit': 'mg'},
            'denominator': {'value': 1, 'unit': 'mL'},
        }
        assert o.valueRatio.numerator.value == 1
        assert o.valueRatio.numerator.unit == 'mg'
        assert o.valueRatio.denominator.value == 1
        assert o.valueRatio.denominator.unit == 'mL'


class TestChoiceFieldFromDict:

    def test_from_dict_quantity(self):
        data = {
            'resourceType': 'Observation',
            'status': 'final',
            'code': {'text': 'Weight'},
            'valueQuantity': {'value': 72, 'unit': 'kg'},
        }
        o = Observation.from_dict(data)
        assert type(o.valueQuantity).__name__ == 'Quantity'
        assert o.valueQuantity.value == 72
        assert o.valueQuantity.unit == 'kg'

    def test_from_dict_primitive(self):
        data = {
            'resourceType': 'Observation',
            'status': 'final',
            'code': {'text': 'Note'},
            'valueString': 'all clear',
        }
        o = Observation.from_dict(data)
        assert o.valueString == 'all clear'
        assert o.valueQuantity is None

    def test_from_dict_period(self):
        data = {
            'resourceType': 'Observation',
            'status': 'final',
            'code': {'text': 'Visit'},
            'effectivePeriod': {'start': '2024-01-01', 'end': '2024-06-30'},
        }
        o = Observation.from_dict(data)
        assert type(o.effectivePeriod).__name__ == 'Period'
        assert o.effectivePeriod.start == '2024-01-01'

    def test_from_dict_roundtrip(self):
        data = {
            'resourceType': 'Observation',
            'status': 'final',
            'code': {'text': 'Weight'},
            'valueQuantity': {'value': 72, 'unit': 'kg'},
        }
        o = Observation.from_dict(data)
        d = o.to_dict()
        assert d['valueQuantity'] == {'value': 72, 'unit': 'kg'}


class TestChoiceFieldFromJson:

    def test_from_json_quantity(self):
        raw = json.dumps({
            'resourceType': 'Observation',
            'status': 'final',
            'code': {'text': 'BMI'},
            'valueQuantity': {'value': 22.5, 'unit': 'kg/m2'},
        })
        o = Observation.from_json(raw)
        assert type(o.valueQuantity).__name__ == 'Quantity'
        assert o.valueQuantity.value == 22.5

    def test_from_json_roundtrip(self):
        raw = json.dumps({
            'resourceType': 'Observation',
            'status': 'final',
            'code': {'text': 'Temp'},
            'valueQuantity': {'value': 36.6, 'unit': 'Cel'},
        })
        o = Observation.from_json(raw)
        j = o.to_json()
        parsed = json.loads(j)
        assert parsed['valueQuantity']['value'] == 36.6
        assert parsed['valueQuantity']['unit'] == 'Cel'


class TestChoiceFieldExclusivity:

    def test_two_choice_fields_validation_error(self):
        o = Observation()
        o.status = 'final'
        o.code = {'text': 'test'}
        o.valueQuantity = {'value': 72, 'unit': 'kg'}
        o.valueString = 'also set'
        result = validate(o)
        choice_errors = [e for e in result.errors if e.code == 'choice']
        assert len(choice_errors) == 1
        assert 'value[x]' in choice_errors[0].path

    def test_one_choice_field_no_error(self):
        o = Observation()
        o.status = 'final'
        o.code = {'text': 'test'}
        o.valueQuantity = {'value': 72, 'unit': 'kg'}
        result = validate(o)
        choice_errors = [e for e in result.errors if e.code == 'choice']
        assert len(choice_errors) == 0

    def test_no_choice_field_no_error(self):
        o = Observation()
        o.status = 'final'
        o.code = {'text': 'test'}
        result = validate(o)
        choice_errors = [e for e in result.errors if e.code == 'choice']
        assert len(choice_errors) == 0

    def test_two_effective_fields_validation_error(self):
        o = Observation()
        o.status = 'final'
        o.code = {'text': 'test'}
        o.effectiveDateTime = '2024-01-01'
        o.effectivePeriod = {'start': '2024-01-01', 'end': '2024-12-31'}
        result = validate(o)
        choice_errors = [e for e in result.errors if e.code == 'choice']
        assert len(choice_errors) == 1
        assert 'effective[x]' in choice_errors[0].path


class TestChoiceFieldNone:

    def test_unset_choice_is_none(self):
        o = Observation()
        assert o.valueQuantity is None
        assert o.valueString is None
        assert o.effectiveDateTime is None

    def test_set_then_reset_to_none(self):
        o = Observation()
        o.valueQuantity = {'value': 72, 'unit': 'kg'}
        assert o.valueQuantity is not None
        o.valueQuantity = None
        assert o.valueQuantity is None

    def test_none_not_in_to_dict(self):
        o = Observation()
        o.status = 'final'
        o.code = {'text': 'test'}
        d = o.to_dict()
        assert 'valueQuantity' not in d
        assert 'valueString' not in d
        assert 'effectiveDateTime' not in d
