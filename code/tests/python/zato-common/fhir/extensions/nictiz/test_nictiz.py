from __future__ import annotations

from zato.fhir.r4_0_1.nictiz.v0_12_0_beta_1.extensions import (
    ADDRESS_INFORMATION_ADDRESS_TYPE_URL,
    NURSING_INTERVENTION_CONTRIBUTOR_IS_REQUESTER_URL,
    PAYER_BANK_INFORMATION_URL,
    STOMA_REFERENCE_URL,
    MEDICAL_DEVICE_HEALTH_PROFESSIONAL_URL,
    FREEDOM_RESTRICTING_INTERVENTION_LEGALLY_CAPABLE_URL,
    ANATOMICAL_LOCATION_LATERALITY_URL,
    MEDICATION_CONTRA_INDICATION_REASON_CLOSURE_URL,
    FEEDING_PATTERN_INFANT_FEEDING_METHOD_URL,
    COMMENT_URL,
    TREATMENT_DIRECTIVE2_SPECIFICATION_OTHER_URL,
    TIME_INTERVAL_PERIOD_URL,
    FREEDOM_RESTRICTING_INTERVENTION_ASSENT_URL,
    PROCEDURE_PROCEDURE_METHOD_URL,
    TREATMENT_DIRECTIVE2_REASON_FOR_ENDING_URL,
    TIME_INTERVAL_DURATION_URL,
    PHARMACEUTICAL_PRODUCT_DESCRIPTION_URL,
    CARE_PLAN_MATERIAL_USED_URL,
    MEDICAL_DEVICE_LOCATION_URL,
    CODE_SPECIFICATION_URL,
    TREATMENT_DIRECTIVE2_ADVANCE_DIRECTIVE_URL,
    NURSING_INTERVENTION_REFERENCE_URL,
    EPISODE_OF_CARE_EPISODE_OF_CARE_NAME_URL,
    ADVANCE_DIRECTIVE_DISORDER_URL,
    LANGUAGE_PROFICIENCY_COMMUNICATION_DETAILS_URL,
    SOAPREPORT_SOAPLINE_CODE_URL,
    PROBLEM_FURTHER_SPECIFICATION_PROBLEM_NAME_URL,
    LABORATORY_TEST_RESULT_SPECIMEN_MORPHOLOGY_URL,
)

from zato.fhir.r4_0_1.nictiz.v0_12_0_beta_1.resources import (
    Address,
    CarePlan,
    CodeableConcept,
    Coding,
    Condition,
    Consent,
    Coverage,
    DeviceUseStatement,
    Element,
    EpisodeOfCare,
    Flag,
    Medication,
    MedicationDispense,
    MedicationRequest,
    Observation,
    Patient,
    Period,
    Procedure,
    Resource,
    Specimen,
)


class TestImports:

    def test_address_is_importable(self):
        assert Address is not None

    def test_careplan_is_importable(self):
        assert CarePlan is not None

    def test_codeableconcept_is_importable(self):
        assert CodeableConcept is not None

    def test_coding_is_importable(self):
        assert Coding is not None

    def test_condition_is_importable(self):
        assert Condition is not None

    def test_consent_is_importable(self):
        assert Consent is not None

    def test_coverage_is_importable(self):
        assert Coverage is not None

    def test_deviceusestatement_is_importable(self):
        assert DeviceUseStatement is not None

    def test_element_is_importable(self):
        assert Element is not None

    def test_episodeofcare_is_importable(self):
        assert EpisodeOfCare is not None

    def test_flag_is_importable(self):
        assert Flag is not None

    def test_medication_is_importable(self):
        assert Medication is not None

    def test_medicationdispense_is_importable(self):
        assert MedicationDispense is not None

    def test_medicationrequest_is_importable(self):
        assert MedicationRequest is not None

    def test_observation_is_importable(self):
        assert Observation is not None

    def test_patient_is_importable(self):
        assert Patient is not None

    def test_period_is_importable(self):
        assert Period is not None

    def test_procedure_is_importable(self):
        assert Procedure is not None

    def test_resource_is_importable(self):
        assert Resource is not None

    def test_specimen_is_importable(self):
        assert Specimen is not None


class TestURLConstants:

    def test_address_information_address_type_url(self):
        assert ADDRESS_INFORMATION_ADDRESS_TYPE_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-AddressInformation.AddressType'

    def test_nursing_intervention_contributor_is_requester_url(self):
        assert NURSING_INTERVENTION_CONTRIBUTOR_IS_REQUESTER_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-NursingIntervention-ContributorIsRequester'

    def test_payer_bank_information_url(self):
        assert PAYER_BANK_INFORMATION_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-Payer.BankInformation'

    def test_stoma_reference_url(self):
        assert STOMA_REFERENCE_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-StomaReference'

    def test_medical_device_health_professional_url(self):
        assert MEDICAL_DEVICE_HEALTH_PROFESSIONAL_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-MedicalDevice.HealthProfessional'

    def test_freedom_restricting_intervention_legally_capable_url(self):
        assert FREEDOM_RESTRICTING_INTERVENTION_LEGALLY_CAPABLE_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-FreedomRestrictingIntervention.LegallyCapable'

    def test_anatomical_location_laterality_url(self):
        assert ANATOMICAL_LOCATION_LATERALITY_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-AnatomicalLocation.Laterality'

    def test_medication_contra_indication_reason_closure_url(self):
        assert MEDICATION_CONTRA_INDICATION_REASON_CLOSURE_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-MedicationContraIndication.ReasonClosure'

    def test_feeding_pattern_infant_feeding_method_url(self):
        assert FEEDING_PATTERN_INFANT_FEEDING_METHOD_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-FeedingPatternInfant.FeedingMethod'

    def test_comment_url(self):
        assert COMMENT_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-Comment'

    def test_treatment_directive2_specification_other_url(self):
        assert TREATMENT_DIRECTIVE2_SPECIFICATION_OTHER_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-TreatmentDirective2.SpecificationOther'

    def test_time_interval_period_url(self):
        assert TIME_INTERVAL_PERIOD_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-TimeInterval.Period'

    def test_freedom_restricting_intervention_assent_url(self):
        assert FREEDOM_RESTRICTING_INTERVENTION_ASSENT_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-FreedomRestrictingIntervention.Assent'

    def test_procedure_procedure_method_url(self):
        assert PROCEDURE_PROCEDURE_METHOD_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-Procedure.ProcedureMethod'

    def test_treatment_directive2_reason_for_ending_url(self):
        assert TREATMENT_DIRECTIVE2_REASON_FOR_ENDING_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-TreatmentDirective2.ReasonForEnding'

    def test_time_interval_duration_url(self):
        assert TIME_INTERVAL_DURATION_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-TimeInterval.Duration'

    def test_pharmaceutical_product_description_url(self):
        assert PHARMACEUTICAL_PRODUCT_DESCRIPTION_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-PharmaceuticalProduct.Description'

    def test_care_plan_material_used_url(self):
        assert CARE_PLAN_MATERIAL_USED_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-CarePlan-MaterialUsed'

    def test_medical_device_location_url(self):
        assert MEDICAL_DEVICE_LOCATION_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-MedicalDevice.Location'

    def test_code_specification_url(self):
        assert CODE_SPECIFICATION_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-CodeSpecification'

    def test_treatment_directive2_advance_directive_url(self):
        assert TREATMENT_DIRECTIVE2_ADVANCE_DIRECTIVE_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-TreatmentDirective2.AdvanceDirective'

    def test_nursing_intervention_reference_url(self):
        assert NURSING_INTERVENTION_REFERENCE_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-NursingInterventionReference'

    def test_episode_of_care_episode_of_care_name_url(self):
        assert EPISODE_OF_CARE_EPISODE_OF_CARE_NAME_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-EpisodeOfCare.EpisodeOfCareName'

    def test_advance_directive_disorder_url(self):
        assert ADVANCE_DIRECTIVE_DISORDER_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-AdvanceDirective.Disorder'

    def test_language_proficiency_communication_details_url(self):
        assert LANGUAGE_PROFICIENCY_COMMUNICATION_DETAILS_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-LanguageProficiency.CommunicationDetails'

    def test_soapreport_soapline_code_url(self):
        assert SOAPREPORT_SOAPLINE_CODE_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-SOAPReport.SOAPLineCode'

    def test_problem_further_specification_problem_name_url(self):
        assert PROBLEM_FURTHER_SPECIFICATION_PROBLEM_NAME_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-Problem.FurtherSpecificationProblemName'

    def test_laboratory_test_result_specimen_morphology_url(self):
        assert LABORATORY_TEST_RESULT_SPECIMEN_MORPHOLOGY_URL == 'http://nictiz.nl/fhir/StructureDefinition/ext-LaboratoryTestResult.Specimen.Morphology'


class TestPropertyAccess:

    def test_address_address_information_address_type_roundtrip(self):
        r = Address()
        r.address_information_address_type = "test-value"
        result = r.address_information_address_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_careplan_nursing_intervention_contributor_is_requester_roundtrip(self):
        r = CarePlan()
        r.nursing_intervention_contributor_is_requester = "test-value"
        result = r.nursing_intervention_contributor_is_requester
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_careplan_care_plan_material_used_roundtrip(self):
        r = CarePlan()
        r.care_plan_material_used = "test-value"
        result = r.care_plan_material_used
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codeableconcept_anatomical_location_laterality_roundtrip(self):
        r = CodeableConcept()
        r.anatomical_location_laterality = "test-value"
        result = r.anatomical_location_laterality
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_coding_code_specification_roundtrip(self):
        r = Coding()
        r.code_specification = "test-value"
        result = r.code_specification
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_condition_problem_further_specification_problem_name_roundtrip(self):
        r = Condition()
        r.problem_further_specification_problem_name = "test-value"
        result = r.problem_further_specification_problem_name
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_consent_treatment_directive2_specification_other_roundtrip(self):
        r = Consent()
        r.treatment_directive2_specification_other = "test-value"
        result = r.treatment_directive2_specification_other
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_consent_treatment_directive2_reason_for_ending_roundtrip(self):
        r = Consent()
        r.treatment_directive2_reason_for_ending = "test-value"
        result = r.treatment_directive2_reason_for_ending
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_consent_treatment_directive2_advance_directive_roundtrip(self):
        r = Consent()
        r.treatment_directive2_advance_directive = "test-value"
        result = r.treatment_directive2_advance_directive
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_consent_advance_directive_disorder_roundtrip(self):
        r = Consent()
        r.advance_directive_disorder = "test-value"
        result = r.advance_directive_disorder
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_coverage_payer_bank_information_roundtrip(self):
        r = Coverage()
        r.payer_bank_information = "test-value"
        result = r.payer_bank_information
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_deviceusestatement_medical_device_health_professional_roundtrip(self):
        r = DeviceUseStatement()
        r.medical_device_health_professional = "test-value"
        result = r.medical_device_health_professional
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_deviceusestatement_medical_device_location_roundtrip(self):
        r = DeviceUseStatement()
        r.medical_device_location = "test-value"
        result = r.medical_device_location
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_comment_roundtrip(self):
        r = Element()
        r.comment = "test-value"
        result = r.comment
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_episodeofcare_episode_of_care_episode_of_care_name_roundtrip(self):
        r = EpisodeOfCare()
        r.episode_of_care_episode_of_care_name = "test-value"
        result = r.episode_of_care_episode_of_care_name
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_flag_medication_contra_indication_reason_closure_roundtrip(self):
        r = Flag()
        r.medication_contra_indication_reason_closure = "test-value"
        result = r.medication_contra_indication_reason_closure
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medication_pharmaceutical_product_description_roundtrip(self):
        r = Medication()
        r.pharmaceutical_product_description = "test-value"
        result = r.pharmaceutical_product_description
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationdispense_time_interval_period_roundtrip(self):
        r = MedicationDispense()
        r.time_interval_period = "test-value"
        result = r.time_interval_period
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationrequest_time_interval_period_roundtrip(self):
        r = MedicationRequest()
        r.time_interval_period = "test-value"
        result = r.time_interval_period
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_feeding_pattern_infant_feeding_method_roundtrip(self):
        r = Observation()
        r.feeding_pattern_infant_feeding_method = "test-value"
        result = r.feeding_pattern_infant_feeding_method
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_soapreport_soapline_code_roundtrip(self):
        r = Observation()
        r.soapreport_soapline_code = "test-value"
        result = r.soapreport_soapline_code
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_language_proficiency_communication_details_roundtrip(self):
        r = Patient()
        r.language_proficiency_communication_details = "test-value"
        result = r.language_proficiency_communication_details
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_period_time_interval_duration_roundtrip(self):
        r = Period()
        r.time_interval_duration = "test-value"
        result = r.time_interval_duration
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_procedure_freedom_restricting_intervention_legally_capable_roundtrip(self):
        r = Procedure()
        r.freedom_restricting_intervention_legally_capable = "test-value"
        result = r.freedom_restricting_intervention_legally_capable
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_procedure_freedom_restricting_intervention_assent_roundtrip(self):
        r = Procedure()
        r.freedom_restricting_intervention_assent = "test-value"
        result = r.freedom_restricting_intervention_assent
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_procedure_procedure_procedure_method_roundtrip(self):
        r = Procedure()
        r.procedure_procedure_method = "test-value"
        result = r.procedure_procedure_method
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_stoma_reference_roundtrip(self):
        r = Resource()
        r.stoma_reference = "test-value"
        result = r.stoma_reference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_nursing_intervention_reference_roundtrip(self):
        r = Resource()
        r.nursing_intervention_reference = "test-value"
        result = r.nursing_intervention_reference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_specimen_laboratory_test_result_specimen_morphology_roundtrip(self):
        r = Specimen()
        r.laboratory_test_result_specimen_morphology = "test-value"
        result = r.laboratory_test_result_specimen_morphology
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

