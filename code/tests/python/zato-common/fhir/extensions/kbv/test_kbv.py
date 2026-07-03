from __future__ import annotations

from zato.fhir.r4_0_1.kbv.v1_5_0.extensions import (
    ALLERGY_INTOLERANCE_ABATEMENT_URL,
    ADDITIONAL_COMMENT_URL,
    RESPONSIBLE_PERSON_ORGANIZATION_URL,
    STAGE_LIFE_URL,
    GOAL_MEDICATION_TARGET_REFERENCE_URL,
    TREATMENT_GOAL_END_URL,
    MEDICATION_TYPE_URL,
)

from zato.fhir.r4_0_1.kbv.v1_5_0.resources import (
    AllergyIntolerance,
    Composition,
    Condition,
    DateTime,
    Device,
    DiagnosticReport,
    Element,
    Encounter,
    Goal,
    Medication,
    MedicationStatement,
    Observation,
    Organization,
    Patient,
    Person,
    Practitioner,
    RelatedPerson,
)


class TestImports:

    def test_allergyintolerance_is_importable(self):
        assert AllergyIntolerance is not None

    def test_composition_is_importable(self):
        assert Composition is not None

    def test_condition_is_importable(self):
        assert Condition is not None

    def test_datetime_is_importable(self):
        assert DateTime is not None

    def test_device_is_importable(self):
        assert Device is not None

    def test_diagnosticreport_is_importable(self):
        assert DiagnosticReport is not None

    def test_element_is_importable(self):
        assert Element is not None

    def test_encounter_is_importable(self):
        assert Encounter is not None

    def test_goal_is_importable(self):
        assert Goal is not None

    def test_medication_is_importable(self):
        assert Medication is not None

    def test_medicationstatement_is_importable(self):
        assert MedicationStatement is not None

    def test_observation_is_importable(self):
        assert Observation is not None

    def test_organization_is_importable(self):
        assert Organization is not None

    def test_patient_is_importable(self):
        assert Patient is not None

    def test_person_is_importable(self):
        assert Person is not None

    def test_practitioner_is_importable(self):
        assert Practitioner is not None

    def test_relatedperson_is_importable(self):
        assert RelatedPerson is not None


class TestURLConstants:

    def test_allergy_intolerance_abatement_url(self):
        assert ALLERGY_INTOLERANCE_ABATEMENT_URL == 'https://fhir.kbv.de/StructureDefinition/KBV_EX_Base_AllergyIntolerance_Abatement'

    def test_additional_comment_url(self):
        assert ADDITIONAL_COMMENT_URL == 'https://fhir.kbv.de/StructureDefinition/KBV_EX_Base_Additional_Comment'

    def test_responsible_person_organization_url(self):
        assert RESPONSIBLE_PERSON_ORGANIZATION_URL == 'https://fhir.kbv.de/StructureDefinition/KBV_EX_Base_Responsible_Person_Organization'

    def test_stage_life_url(self):
        assert STAGE_LIFE_URL == 'https://fhir.kbv.de/StructureDefinition/KBV_EX_Base_Stage_Life'

    def test_goal_medication_target_reference_url(self):
        assert GOAL_MEDICATION_TARGET_REFERENCE_URL == 'https://fhir.kbv.de/StructureDefinition/KBV_EX_Base_Goal_Medication_Target_Reference'

    def test_treatment_goal_end_url(self):
        assert TREATMENT_GOAL_END_URL == 'https://fhir.kbv.de/StructureDefinition/KBV_EX_Base_Treatment_Goal_End'

    def test_medication_type_url(self):
        assert MEDICATION_TYPE_URL == 'https://fhir.kbv.de/StructureDefinition/KBV_EX_Base_Medication_Type'


class TestPropertyAccess:

    def test_allergyintolerance_allergy_intolerance_abatement_roundtrip(self):
        r = AllergyIntolerance()
        r.allergy_intolerance_abatement = "test-value"
        result = r.allergy_intolerance_abatement
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_allergyintolerance_stage_life_roundtrip(self):
        r = AllergyIntolerance()
        r.stage_life = "test-value"
        result = r.stage_life
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_composition_additional_comment_roundtrip(self):
        r = Composition()
        r.additional_comment = "test-value"
        result = r.additional_comment
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_condition_additional_comment_roundtrip(self):
        r = Condition()
        r.additional_comment = "test-value"
        result = r.additional_comment
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_datetime_stage_life_roundtrip(self):
        r = DateTime()
        r.stage_life = "test-value"
        result = r.stage_life
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_device_responsible_person_organization_roundtrip(self):
        r = Device()
        r.responsible_person_organization = "test-value"
        result = r.responsible_person_organization
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_additional_comment_roundtrip(self):
        r = DiagnosticReport()
        r.additional_comment = "test-value"
        result = r.additional_comment
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_additional_comment_roundtrip(self):
        r = Element()
        r.additional_comment = "test-value"
        result = r.additional_comment
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_additional_comment_roundtrip(self):
        r = Encounter()
        r.additional_comment = "test-value"
        result = r.additional_comment
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_goal_treatment_goal_end_roundtrip(self):
        r = Goal()
        r.treatment_goal_end = "test-value"
        result = r.treatment_goal_end
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medication_medication_type_roundtrip(self):
        r = Medication()
        r.medication_type = "test-value"
        result = r.medication_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationstatement_additional_comment_roundtrip(self):
        r = MedicationStatement()
        r.additional_comment = "test-value"
        result = r.additional_comment
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationstatement_goal_medication_target_reference_roundtrip(self):
        r = MedicationStatement()
        r.goal_medication_target_reference = "test-value"
        result = r.goal_medication_target_reference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_additional_comment_roundtrip(self):
        r = Observation()
        r.additional_comment = "test-value"
        result = r.additional_comment
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_additional_comment_roundtrip(self):
        r = Organization()
        r.additional_comment = "test-value"
        result = r.additional_comment
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_additional_comment_roundtrip(self):
        r = Patient()
        r.additional_comment = "test-value"
        result = r.additional_comment
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_person_additional_comment_roundtrip(self):
        r = Person()
        r.additional_comment = "test-value"
        result = r.additional_comment
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitioner_additional_comment_roundtrip(self):
        r = Practitioner()
        r.additional_comment = "test-value"
        result = r.additional_comment
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_relatedperson_additional_comment_roundtrip(self):
        r = RelatedPerson()
        r.additional_comment = "test-value"
        result = r.additional_comment
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

