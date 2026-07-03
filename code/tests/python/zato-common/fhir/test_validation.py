# Generated - do not edit
from __future__ import annotations

import pytest

from zato.fhir.r4_0_1 import (
    Patient, Observation, Encounter, Account, Appointment, Binary,
)
from zato.fhir.r4_0_1.validation_data import REQUIRED_FIELDS
from zato.fhir.validation import validate, ValidationResult


class TestValidationRequiredFields:

    def test_patient_no_required_fields(self):
        p = Patient()
        p.id = 'test-1'
        result = validate(p)
        assert result.is_valid is True

    def test_observation_missing_status(self):
        o = Observation()
        o.id = 'test-1'
        result = validate(o)
        assert result.is_valid is False
        assert any('status' in str(e) for e in result.errors)

    def test_observation_with_required_fields(self):
        o = Observation()
        o.id = 'test-1'
        o.status = 'final'
        o.code = {'coding': [{'code': '12345'}]}
        result = validate(o)
        assert result.is_valid is True

    def test_encounter_missing_status(self):
        e = Encounter()
        e.id = 'test-1'
        result = validate(e)
        assert result.is_valid is False
        assert any('status' in str(err) for err in result.errors)

    def test_encounter_with_required_fields(self):
        e = Encounter()
        e.id = 'test-1'
        e.status = 'finished'
        e.class_ = {'code': 'AMB'}
        result = validate(e)
        assert result.is_valid is True

    def test_account_missing_status(self):
        a = Account()
        a.id = 'test-1'
        result = validate(a)
        assert result.is_valid is False

    def test_account_with_status(self):
        a = Account()
        a.id = 'test-1'
        a.status = 'active'
        result = validate(a)
        assert result.is_valid is True

    def test_appointment_missing_required(self):
        a = Appointment()
        a.id = 'test-1'
        result = validate(a)
        assert result.is_valid is False

    def test_binary_missing_content_type(self):
        b = Binary()
        b.id = 'test-1'
        result = validate(b)
        assert result.is_valid is False

    def test_binary_with_content_type(self):
        b = Binary()
        b.id = 'test-1'
        b.contentType = 'application/pdf'
        result = validate(b)
        assert result.is_valid is True


class TestValidationDataIntegrity:

    def test_required_fields_data_exists(self):
        assert REQUIRED_FIELDS is not None
        assert len(REQUIRED_FIELDS) > 0

    def test_observation_in_required_fields(self):
        assert 'Observation' in REQUIRED_FIELDS
        obs_fields = REQUIRED_FIELDS['Observation']
        field_names = [f['field'] for f in obs_fields]
        assert 'status' in field_names
        assert 'code' in field_names

    def test_encounter_in_required_fields(self):
        assert 'Encounter' in REQUIRED_FIELDS
        enc_fields = REQUIRED_FIELDS['Encounter']
        field_names = [f['field'] for f in enc_fields]
        assert 'status' in field_names

    def test_patient_not_in_required_fields(self):
        assert 'Patient' not in REQUIRED_FIELDS


class TestValidationAllResources:

    @pytest.mark.parametrize('resource_name', list(REQUIRED_FIELDS.keys())[:20])
    def test_resource_validation_runs(self, resource_name):
        import zato.fhir.r4_0_1 as r4
        cls = getattr(r4, resource_name, None)
        if cls:
            obj = cls()
            result = validate(obj)
            assert isinstance(result, ValidationResult)


class TestCardinalityValidation:

    def test_cardinality_single_value_ok(self):
        from zato.fhir.r4_0_1 import Patient
        p = Patient()
        p.id = 'test-1'
        p.gender = 'male'
        result = validate(p)
        assert not any(e.code == 'cardinality' for e in result.errors)

    def test_cardinality_list_exceeds_max(self):
        from zato.fhir.r4_0_1 import Patient
        p = Patient()
        p.id = 'test-1'
        p.gender = ['male', 'female']
        result = validate(p)
        assert any(e.code == 'cardinality' and 'gender' in e.path for e in result.errors)


class TestTypeValidation:

    def test_type_string_ok(self):
        from zato.fhir.r4_0_1 import Patient
        p = Patient()
        p.id = 'test-1'
        p.gender = 'male'
        result = validate(p)
        assert not any(e.code == 'type' for e in result.errors)

    def test_type_boolean_ok(self):
        from zato.fhir.r4_0_1 import Patient
        p = Patient()
        p.id = 'test-1'
        p.active = True
        result = validate(p)
        assert not any(e.code == 'type' for e in result.errors)


class TestReferenceValidation:

    def test_reference_valid_target(self):
        from zato.fhir.r4_0_1 import Observation
        o = Observation()
        o.id = 'test-1'
        o.status = 'final'
        o.code = {'coding': [{'code': '12345'}]}
        o.subject = {'reference': 'Patient/123'}
        result = validate(o)
        assert not any(e.code == 'reference_target' for e in result.errors)

    def test_reference_invalid_target(self):
        from zato.fhir.r4_0_1 import Observation
        o = Observation()
        o.id = 'test-1'
        o.status = 'final'
        o.code = {'coding': [{'code': '12345'}]}
        o.subject = {'reference': 'Medication/123'}
        result = validate(o)
        assert any(e.code == 'reference_target' and 'subject' in e.path for e in result.errors)

    def test_reference_no_reference_field(self):
        from zato.fhir.r4_0_1 import Observation
        o = Observation()
        o.id = 'test-1'
        o.status = 'final'
        o.code = {'coding': [{'code': '12345'}]}
        o.subject = {'display': 'John Doe'}
        result = validate(o)
        assert not any(e.code == 'reference_target' for e in result.errors)


class TestValueSetBindingValidation:

    def test_valueset_valid_code(self):
        from zato.fhir.r4_0_1 import Patient
        from zato.fhir.validation import validate_valueset_binding
        p = Patient()
        p.id = 'test-1'
        p.gender = 'male'
        result = validate_valueset_binding(p)
        assert not any(e.code == 'valueset_binding' and 'gender' in e.path for e in result.errors)

    def test_valueset_invalid_code(self):
        from zato.fhir.r4_0_1 import Patient
        from zato.fhir.validation import validate_valueset_binding
        p = Patient()
        p.id = 'test-1'
        p.gender = 'invalid-gender'
        result = validate_valueset_binding(p)
        assert any(e.code == 'valueset_binding' and 'gender' in e.path for e in result.errors)

    def test_valueset_observation_status_valid(self):
        from zato.fhir.r4_0_1 import Observation
        from zato.fhir.validation import validate_valueset_binding
        o = Observation()
        o.id = 'test-1'
        o.status = 'final'
        result = validate_valueset_binding(o)
        assert not any(e.code == 'valueset_binding' and 'status' in e.path for e in result.errors)

    def test_valueset_observation_status_invalid(self):
        from zato.fhir.r4_0_1 import Observation
        from zato.fhir.validation import validate_valueset_binding
        o = Observation()
        o.id = 'test-1'
        o.status = 'not-a-valid-status'
        result = validate_valueset_binding(o)
        assert any(e.code == 'valueset_binding' and 'status' in e.path for e in result.errors)

    def test_valueset_encounter_status_valid(self):
        from zato.fhir.r4_0_1 import Encounter
        from zato.fhir.validation import validate_valueset_binding
        e = Encounter()
        e.id = 'test-1'
        e.status = 'finished'
        result = validate_valueset_binding(e)
        assert not any(err.code == 'valueset_binding' and 'status' in err.path for err in result.errors)

    def test_valueset_codeable_concept(self):
        from zato.fhir.r4_0_1 import AllergyIntolerance
        from zato.fhir.validation import validate_valueset_binding
        a = AllergyIntolerance()
        a.id = 'test-1'
        a.type = 'allergy'
        result = validate_valueset_binding(a)
        assert not any(e.code == 'valueset_binding' and 'type' in e.path for e in result.errors)

    def test_valueset_skip_extensible(self):
        from zato.fhir.r4_0_1 import Patient
        from zato.fhir.validation import validate_valueset_binding
        p = Patient()
        p.id = 'test-1'
        result = validate_valueset_binding(p, include_extensible=False)
        assert result.is_valid


class TestContainedResourceValidation:

    def test_parent_validation_runs_with_contained(self):
        p = Patient()
        p.id = 'wellness-visit-1'
        p.contained = [{
            'resourceType': 'Observation',
            'id': 'vitamin-d-panel',
            'status': 'final',
            'code': {'coding': [{'code': 'wellness-check'}]},
        }]
        result = validate(p)
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True


class TestChoiceTypeValidation:

    def test_value_quantity(self):
        o = Observation()
        o.id = 'routine-checkup-1'
        o.status = 'final'
        o.code = {'coding': [{'code': 'wellness-check'}]}
        o.valueQuantity = {
            'value': 37.2,
            'unit': 'C',
            'system': 'http://unitsofmeasure.org',
            'code': 'Cel',
        }
        result = validate(o)
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True

    def test_value_string(self):
        o = Observation()
        o.id = 'routine-checkup-2'
        o.status = 'final'
        o.code = {'coding': [{'code': 'wellness-check'}]}
        o.valueString = 'Feeling great after the wellness visit.'
        result = validate(o)
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True


class TestMaxCardinalityEdgeCases:

    def test_single_cardinality_list_errors(self):
        p = Patient()
        p.id = 'vitamins-member-1'
        p.gender = ['male', 'female']
        result = validate(p)
        assert any(e.code == 'cardinality' and 'gender' in e.path for e in result.errors)

    def test_list_cardinality_list_ok(self):
        p = Patient()
        p.id = 'vitamins-member-2'
        p.name = [{'family': 'Sunnyvale', 'given': ['Jordan']}]
        result = validate(p)
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True


class TestRequiredFieldsParametrized:

    @pytest.mark.parametrize('resource_name', list(REQUIRED_FIELDS.keys()))
    def test_validation_returns_validation_result(self, resource_name):
        import zato.fhir.r4_0_1 as r4
        cls = getattr(r4, resource_name)
        obj = cls()
        result = validate(obj)
        assert isinstance(result, ValidationResult)
