from __future__ import annotations

from typing import Any

from zato.fhir.r4_0_1 import resources as base
from zato.fhir.extensions import get_extension, set_extension
from zato.fhir.r4_0_1.nictiz.v0_12_0_beta_1.extensions import (
    ADDRESS_INFORMATION_ADDRESS_TYPE_URL,
    NURSING_INTERVENTION_CONTRIBUTOR_IS_REQUESTER_URL,
    CARE_PLAN_MATERIAL_USED_URL,
    ANATOMICAL_LOCATION_LATERALITY_URL,
    CODE_SPECIFICATION_URL,
    PROBLEM_FURTHER_SPECIFICATION_PROBLEM_NAME_URL,
    TREATMENT_DIRECTIVE2_SPECIFICATION_OTHER_URL,
    TREATMENT_DIRECTIVE2_REASON_FOR_ENDING_URL,
    TREATMENT_DIRECTIVE2_ADVANCE_DIRECTIVE_URL,
    ADVANCE_DIRECTIVE_DISORDER_URL,
    PAYER_BANK_INFORMATION_URL,
    MEDICAL_DEVICE_HEALTH_PROFESSIONAL_URL,
    MEDICAL_DEVICE_LOCATION_URL,
    COMMENT_URL,
    EPISODE_OF_CARE_EPISODE_OF_CARE_NAME_URL,
    MEDICATION_CONTRA_INDICATION_REASON_CLOSURE_URL,
    PHARMACEUTICAL_PRODUCT_DESCRIPTION_URL,
    TIME_INTERVAL_PERIOD_URL,
    FEEDING_PATTERN_INFANT_FEEDING_METHOD_URL,
    SOAPREPORT_SOAPLINE_CODE_URL,
    LANGUAGE_PROFICIENCY_COMMUNICATION_DETAILS_URL,
    TIME_INTERVAL_DURATION_URL,
    FREEDOM_RESTRICTING_INTERVENTION_LEGALLY_CAPABLE_URL,
    FREEDOM_RESTRICTING_INTERVENTION_ASSENT_URL,
    PROCEDURE_PROCEDURE_METHOD_URL,
    STOMA_REFERENCE_URL,
    NURSING_INTERVENTION_REFERENCE_URL,
    LABORATORY_TEST_RESULT_SPECIMEN_MORPHOLOGY_URL,
)

class Address(base.Address):

    @property
    def address_information_address_type(self) -> Any:
        return get_extension(self, ADDRESS_INFORMATION_ADDRESS_TYPE_URL)

    @address_information_address_type.setter
    def address_information_address_type(self, value: Any) -> None:
        set_extension(self, ADDRESS_INFORMATION_ADDRESS_TYPE_URL, value)

class CarePlan(base.CarePlan):

    @property
    def nursing_intervention_contributor_is_requester(self) -> Any:
        return get_extension(self, NURSING_INTERVENTION_CONTRIBUTOR_IS_REQUESTER_URL)

    @nursing_intervention_contributor_is_requester.setter
    def nursing_intervention_contributor_is_requester(self, value: Any) -> None:
        set_extension(self, NURSING_INTERVENTION_CONTRIBUTOR_IS_REQUESTER_URL, value)

    @property
    def care_plan_material_used(self) -> Any:
        return get_extension(self, CARE_PLAN_MATERIAL_USED_URL)

    @care_plan_material_used.setter
    def care_plan_material_used(self, value: Any) -> None:
        set_extension(self, CARE_PLAN_MATERIAL_USED_URL, value)

class CodeableConcept(base.CodeableConcept):

    @property
    def anatomical_location_laterality(self) -> Any:
        return get_extension(self, ANATOMICAL_LOCATION_LATERALITY_URL)

    @anatomical_location_laterality.setter
    def anatomical_location_laterality(self, value: Any) -> None:
        set_extension(self, ANATOMICAL_LOCATION_LATERALITY_URL, value)

class Coding(base.Coding):

    @property
    def code_specification(self) -> Any:
        return get_extension(self, CODE_SPECIFICATION_URL)

    @code_specification.setter
    def code_specification(self, value: Any) -> None:
        set_extension(self, CODE_SPECIFICATION_URL, value)

class Condition(base.Condition):

    @property
    def problem_further_specification_problem_name(self) -> Any:
        return get_extension(self, PROBLEM_FURTHER_SPECIFICATION_PROBLEM_NAME_URL)

    @problem_further_specification_problem_name.setter
    def problem_further_specification_problem_name(self, value: Any) -> None:
        set_extension(self, PROBLEM_FURTHER_SPECIFICATION_PROBLEM_NAME_URL, value)

class Consent(base.Consent):

    @property
    def treatment_directive2_specification_other(self) -> Any:
        return get_extension(self, TREATMENT_DIRECTIVE2_SPECIFICATION_OTHER_URL)

    @treatment_directive2_specification_other.setter
    def treatment_directive2_specification_other(self, value: Any) -> None:
        set_extension(self, TREATMENT_DIRECTIVE2_SPECIFICATION_OTHER_URL, value)

    @property
    def treatment_directive2_reason_for_ending(self) -> Any:
        return get_extension(self, TREATMENT_DIRECTIVE2_REASON_FOR_ENDING_URL)

    @treatment_directive2_reason_for_ending.setter
    def treatment_directive2_reason_for_ending(self, value: Any) -> None:
        set_extension(self, TREATMENT_DIRECTIVE2_REASON_FOR_ENDING_URL, value)

    @property
    def treatment_directive2_advance_directive(self) -> Any:
        return get_extension(self, TREATMENT_DIRECTIVE2_ADVANCE_DIRECTIVE_URL)

    @treatment_directive2_advance_directive.setter
    def treatment_directive2_advance_directive(self, value: Any) -> None:
        set_extension(self, TREATMENT_DIRECTIVE2_ADVANCE_DIRECTIVE_URL, value)

    @property
    def advance_directive_disorder(self) -> Any:
        return get_extension(self, ADVANCE_DIRECTIVE_DISORDER_URL)

    @advance_directive_disorder.setter
    def advance_directive_disorder(self, value: Any) -> None:
        set_extension(self, ADVANCE_DIRECTIVE_DISORDER_URL, value)

class Coverage(base.Coverage):

    @property
    def payer_bank_information(self) -> Any:
        return get_extension(self, PAYER_BANK_INFORMATION_URL)

    @payer_bank_information.setter
    def payer_bank_information(self, value: Any) -> None:
        set_extension(self, PAYER_BANK_INFORMATION_URL, value)

class DeviceUseStatement(base.DeviceUseStatement):

    @property
    def medical_device_health_professional(self) -> Any:
        return get_extension(self, MEDICAL_DEVICE_HEALTH_PROFESSIONAL_URL)

    @medical_device_health_professional.setter
    def medical_device_health_professional(self, value: Any) -> None:
        set_extension(self, MEDICAL_DEVICE_HEALTH_PROFESSIONAL_URL, value)

    @property
    def medical_device_location(self) -> Any:
        return get_extension(self, MEDICAL_DEVICE_LOCATION_URL)

    @medical_device_location.setter
    def medical_device_location(self, value: Any) -> None:
        set_extension(self, MEDICAL_DEVICE_LOCATION_URL, value)

class Element(base.Element):

    @property
    def comment(self) -> Any:
        return get_extension(self, COMMENT_URL)

    @comment.setter
    def comment(self, value: Any) -> None:
        set_extension(self, COMMENT_URL, value)

class EpisodeOfCare(base.EpisodeOfCare):

    @property
    def episode_of_care_episode_of_care_name(self) -> Any:
        return get_extension(self, EPISODE_OF_CARE_EPISODE_OF_CARE_NAME_URL)

    @episode_of_care_episode_of_care_name.setter
    def episode_of_care_episode_of_care_name(self, value: Any) -> None:
        set_extension(self, EPISODE_OF_CARE_EPISODE_OF_CARE_NAME_URL, value)

class Flag(base.Flag):

    @property
    def medication_contra_indication_reason_closure(self) -> Any:
        return get_extension(self, MEDICATION_CONTRA_INDICATION_REASON_CLOSURE_URL)

    @medication_contra_indication_reason_closure.setter
    def medication_contra_indication_reason_closure(self, value: Any) -> None:
        set_extension(self, MEDICATION_CONTRA_INDICATION_REASON_CLOSURE_URL, value)

class Medication(base.Medication):

    @property
    def pharmaceutical_product_description(self) -> Any:
        return get_extension(self, PHARMACEUTICAL_PRODUCT_DESCRIPTION_URL)

    @pharmaceutical_product_description.setter
    def pharmaceutical_product_description(self, value: Any) -> None:
        set_extension(self, PHARMACEUTICAL_PRODUCT_DESCRIPTION_URL, value)

class MedicationDispense(base.MedicationDispense):

    @property
    def time_interval_period(self) -> Any:
        return get_extension(self, TIME_INTERVAL_PERIOD_URL)

    @time_interval_period.setter
    def time_interval_period(self, value: Any) -> None:
        set_extension(self, TIME_INTERVAL_PERIOD_URL, value)

class MedicationRequest(base.MedicationRequest):

    @property
    def time_interval_period(self) -> Any:
        return get_extension(self, TIME_INTERVAL_PERIOD_URL)

    @time_interval_period.setter
    def time_interval_period(self, value: Any) -> None:
        set_extension(self, TIME_INTERVAL_PERIOD_URL, value)

class Observation(base.Observation):

    @property
    def feeding_pattern_infant_feeding_method(self) -> Any:
        return get_extension(self, FEEDING_PATTERN_INFANT_FEEDING_METHOD_URL)

    @feeding_pattern_infant_feeding_method.setter
    def feeding_pattern_infant_feeding_method(self, value: Any) -> None:
        set_extension(self, FEEDING_PATTERN_INFANT_FEEDING_METHOD_URL, value)

    @property
    def soapreport_soapline_code(self) -> Any:
        return get_extension(self, SOAPREPORT_SOAPLINE_CODE_URL)

    @soapreport_soapline_code.setter
    def soapreport_soapline_code(self, value: Any) -> None:
        set_extension(self, SOAPREPORT_SOAPLINE_CODE_URL, value)

class Patient(base.Patient):

    @property
    def language_proficiency_communication_details(self) -> Any:
        return get_extension(self, LANGUAGE_PROFICIENCY_COMMUNICATION_DETAILS_URL)

    @language_proficiency_communication_details.setter
    def language_proficiency_communication_details(self, value: Any) -> None:
        set_extension(self, LANGUAGE_PROFICIENCY_COMMUNICATION_DETAILS_URL, value)

class Period(base.Period):

    @property
    def time_interval_duration(self) -> Any:
        return get_extension(self, TIME_INTERVAL_DURATION_URL)

    @time_interval_duration.setter
    def time_interval_duration(self, value: Any) -> None:
        set_extension(self, TIME_INTERVAL_DURATION_URL, value)

class Procedure(base.Procedure):

    @property
    def freedom_restricting_intervention_legally_capable(self) -> Any:
        return get_extension(self, FREEDOM_RESTRICTING_INTERVENTION_LEGALLY_CAPABLE_URL)

    @freedom_restricting_intervention_legally_capable.setter
    def freedom_restricting_intervention_legally_capable(self, value: Any) -> None:
        set_extension(self, FREEDOM_RESTRICTING_INTERVENTION_LEGALLY_CAPABLE_URL, value)

    @property
    def freedom_restricting_intervention_assent(self) -> Any:
        return get_extension(self, FREEDOM_RESTRICTING_INTERVENTION_ASSENT_URL)

    @freedom_restricting_intervention_assent.setter
    def freedom_restricting_intervention_assent(self, value: Any) -> None:
        set_extension(self, FREEDOM_RESTRICTING_INTERVENTION_ASSENT_URL, value)

    @property
    def procedure_procedure_method(self) -> Any:
        return get_extension(self, PROCEDURE_PROCEDURE_METHOD_URL)

    @procedure_procedure_method.setter
    def procedure_procedure_method(self, value: Any) -> None:
        set_extension(self, PROCEDURE_PROCEDURE_METHOD_URL, value)

class Resource(base.Resource):

    @property
    def stoma_reference(self) -> Any:
        return get_extension(self, STOMA_REFERENCE_URL)

    @stoma_reference.setter
    def stoma_reference(self, value: Any) -> None:
        set_extension(self, STOMA_REFERENCE_URL, value)

    @property
    def nursing_intervention_reference(self) -> Any:
        return get_extension(self, NURSING_INTERVENTION_REFERENCE_URL)

    @nursing_intervention_reference.setter
    def nursing_intervention_reference(self, value: Any) -> None:
        set_extension(self, NURSING_INTERVENTION_REFERENCE_URL, value)

class Specimen(base.Specimen):

    @property
    def laboratory_test_result_specimen_morphology(self) -> Any:
        return get_extension(self, LABORATORY_TEST_RESULT_SPECIMEN_MORPHOLOGY_URL)

    @laboratory_test_result_specimen_morphology.setter
    def laboratory_test_result_specimen_morphology(self, value: Any) -> None:
        set_extension(self, LABORATORY_TEST_RESULT_SPECIMEN_MORPHOLOGY_URL, value)
