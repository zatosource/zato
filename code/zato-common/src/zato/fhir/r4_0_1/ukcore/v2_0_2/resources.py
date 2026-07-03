from __future__ import annotations

from typing import Any

from zato.fhir.r4_0_1 import resources as base
from zato.fhir.extensions import get_extension, set_extension
from zato.fhir.r4_0_1.ukcore.v2_0_2.extensions import (
    UKCORE_ADDRESS_KEY_URL,
    UKCORE_ALLERGY_INTOLERANCE_END_URL,
    UKCORE_EVIDENCE_URL,
    UKCORE_BOOKING_ORGANIZATION_URL,
    UKCORE_DELIVERY_CHANNEL_URL,
    UKCORE_CODING_SCTDESC_DISPLAY_URL,
    UKCORE_CARE_SETTING_TYPE_URL,
    UKCORE_CONDITION_EPISODE_URL,
    UKCORE_OTHER_CONTACT_SYSTEM_URL,
    DIAGNOSTIC_REPORT_SUPPORTING_INFO_URL,
    DIAGNOSTIC_REPORT_NOTE_URL,
    DIAGNOSTIC_REPORT_COMPOSITION_URL,
    UKCORE_DEVICE_REFERENCE_URL,
    UKCORE_LEGAL_STATUS_URL,
    UKCORE_DISCHARGE_METHOD_URL,
    UKCORE_OUTCOME_OF_ATTENDANCE_URL,
    UKCORE_EMERGENCY_CARE_DISCHARGE_STATUS_URL,
    UKCORE_ADMISSION_METHOD_URL,
    FAMILY_MEMBER_HISTORY_PARTICIPANT_URL,
    UKCORE_ASSOCIATED_ENCOUNTER_URL,
    UKCORE_VACCINATION_PROCEDURE_URL,
    UKCORE_PARENT_PRESENT_URL,
    UKCORE_LIST_WARNING_CODE_URL,
    UKCORE_MEDICATION_TRADE_FAMILY_URL,
    UKCORE_MEDICATION_REPEAT_INFORMATION_URL,
    UKCORE_MEDICATION_PRESCRIBING_ORGANIZATION_TYPE_URL,
    UKCORE_PHARMACIST_VERIFIED_INDICATOR_URL,
    UKCORE_MEDICATION_STATEMENT_LAST_ISSUE_DATE_URL,
    OBSERVATION_BODY_STRUCTURE_URL,
    OBSERVATION_TRIGGERED_BY_URL,
    UKCORE_MAIN_LOCATION_URL,
    UKCORE_ETHNIC_CATEGORY_URL,
    UKCORE_NHSNUMBER_UNAVAILABLE_REASON_URL,
    UKCORE_CONTACT_RANK_URL,
    UKCORE_COPY_CORRESPONDENCE_INDICATOR_URL,
    UKCORE_RESIDENTIAL_STATUS_URL,
    UKCORE_DEATH_NOTIFICATION_STATUS_URL,
    UKCORE_BIRTH_SEX_URL,
    UKCORE_CONTACT_PREFERENCE_URL,
    UKCORE_NHSNUMBER_VERIFICATION_STATUS_URL,
    UKCORE_SOURCE_OF_SERVICE_REQUEST_URL,
    UKCORE_PRIORITY_REASON_URL,
    UKCORE_COVERAGE_URL,
    UKCORE_ADDITIONAL_CONTACT_URL,
    SPECIMEN_COLLECTION_COLLECTOR_URL,
    UKCORE_SAMPLE_CATEGORY_URL,
    UKCORE_BODY_SITE_REFERENCE_URL,
)

class Address(base.Address):

    @property
    def ukcore_address_key(self) -> Any:
        return get_extension(self, UKCORE_ADDRESS_KEY_URL)

    @ukcore_address_key.setter
    def ukcore_address_key(self, value: Any) -> None:
        set_extension(self, UKCORE_ADDRESS_KEY_URL, value)

class AllergyIntolerance(base.AllergyIntolerance):

    @property
    def ukcore_allergy_intolerance_end(self) -> Any:
        return get_extension(self, UKCORE_ALLERGY_INTOLERANCE_END_URL)

    @ukcore_allergy_intolerance_end.setter
    def ukcore_allergy_intolerance_end(self, value: Any) -> None:
        set_extension(self, UKCORE_ALLERGY_INTOLERANCE_END_URL, value)

    @property
    def ukcore_evidence(self) -> Any:
        return get_extension(self, UKCORE_EVIDENCE_URL)

    @ukcore_evidence.setter
    def ukcore_evidence(self, value: Any) -> None:
        set_extension(self, UKCORE_EVIDENCE_URL, value)

class Appointment(base.Appointment):

    @property
    def ukcore_booking_organization(self) -> Any:
        return get_extension(self, UKCORE_BOOKING_ORGANIZATION_URL)

    @ukcore_booking_organization.setter
    def ukcore_booking_organization(self, value: Any) -> None:
        set_extension(self, UKCORE_BOOKING_ORGANIZATION_URL, value)

    @property
    def ukcore_delivery_channel(self) -> Any:
        return get_extension(self, UKCORE_DELIVERY_CHANNEL_URL)

    @ukcore_delivery_channel.setter
    def ukcore_delivery_channel(self, value: Any) -> None:
        set_extension(self, UKCORE_DELIVERY_CHANNEL_URL, value)

class Coding(base.Coding):

    @property
    def ukcore_coding_sctdesc_display(self) -> Any:
        return get_extension(self, UKCORE_CODING_SCTDESC_DISPLAY_URL)

    @ukcore_coding_sctdesc_display.setter
    def ukcore_coding_sctdesc_display(self, value: Any) -> None:
        set_extension(self, UKCORE_CODING_SCTDESC_DISPLAY_URL, value)

class Composition(base.Composition):

    @property
    def ukcore_care_setting_type(self) -> Any:
        return get_extension(self, UKCORE_CARE_SETTING_TYPE_URL)

    @ukcore_care_setting_type.setter
    def ukcore_care_setting_type(self, value: Any) -> None:
        set_extension(self, UKCORE_CARE_SETTING_TYPE_URL, value)

class Condition(base.Condition):

    @property
    def ukcore_condition_episode(self) -> Any:
        return get_extension(self, UKCORE_CONDITION_EPISODE_URL)

    @ukcore_condition_episode.setter
    def ukcore_condition_episode(self, value: Any) -> None:
        set_extension(self, UKCORE_CONDITION_EPISODE_URL, value)

class ContactPoint(base.ContactPoint):

    @property
    def ukcore_other_contact_system(self) -> Any:
        return get_extension(self, UKCORE_OTHER_CONTACT_SYSTEM_URL)

    @ukcore_other_contact_system.setter
    def ukcore_other_contact_system(self, value: Any) -> None:
        set_extension(self, UKCORE_OTHER_CONTACT_SYSTEM_URL, value)

class DiagnosticReport(base.DiagnosticReport):

    @property
    def diagnostic_report_supporting_info(self) -> Any:
        return get_extension(self, DIAGNOSTIC_REPORT_SUPPORTING_INFO_URL)

    @diagnostic_report_supporting_info.setter
    def diagnostic_report_supporting_info(self, value: Any) -> None:
        set_extension(self, DIAGNOSTIC_REPORT_SUPPORTING_INFO_URL, value)

    @property
    def diagnostic_report_note(self) -> Any:
        return get_extension(self, DIAGNOSTIC_REPORT_NOTE_URL)

    @diagnostic_report_note.setter
    def diagnostic_report_note(self, value: Any) -> None:
        set_extension(self, DIAGNOSTIC_REPORT_NOTE_URL, value)

    @property
    def diagnostic_report_composition(self) -> Any:
        return get_extension(self, DIAGNOSTIC_REPORT_COMPOSITION_URL)

    @diagnostic_report_composition.setter
    def diagnostic_report_composition(self, value: Any) -> None:
        set_extension(self, DIAGNOSTIC_REPORT_COMPOSITION_URL, value)

    @property
    def ukcore_device_reference(self) -> Any:
        return get_extension(self, UKCORE_DEVICE_REFERENCE_URL)

    @ukcore_device_reference.setter
    def ukcore_device_reference(self, value: Any) -> None:
        set_extension(self, UKCORE_DEVICE_REFERENCE_URL, value)

class Encounter(base.Encounter):

    @property
    def ukcore_legal_status(self) -> Any:
        return get_extension(self, UKCORE_LEGAL_STATUS_URL)

    @ukcore_legal_status.setter
    def ukcore_legal_status(self, value: Any) -> None:
        set_extension(self, UKCORE_LEGAL_STATUS_URL, value)

    @property
    def ukcore_discharge_method(self) -> Any:
        return get_extension(self, UKCORE_DISCHARGE_METHOD_URL)

    @ukcore_discharge_method.setter
    def ukcore_discharge_method(self, value: Any) -> None:
        set_extension(self, UKCORE_DISCHARGE_METHOD_URL, value)

    @property
    def ukcore_outcome_of_attendance(self) -> Any:
        return get_extension(self, UKCORE_OUTCOME_OF_ATTENDANCE_URL)

    @ukcore_outcome_of_attendance.setter
    def ukcore_outcome_of_attendance(self, value: Any) -> None:
        set_extension(self, UKCORE_OUTCOME_OF_ATTENDANCE_URL, value)

    @property
    def ukcore_emergency_care_discharge_status(self) -> Any:
        return get_extension(self, UKCORE_EMERGENCY_CARE_DISCHARGE_STATUS_URL)

    @ukcore_emergency_care_discharge_status.setter
    def ukcore_emergency_care_discharge_status(self, value: Any) -> None:
        set_extension(self, UKCORE_EMERGENCY_CARE_DISCHARGE_STATUS_URL, value)

    @property
    def ukcore_admission_method(self) -> Any:
        return get_extension(self, UKCORE_ADMISSION_METHOD_URL)

    @ukcore_admission_method.setter
    def ukcore_admission_method(self, value: Any) -> None:
        set_extension(self, UKCORE_ADMISSION_METHOD_URL, value)

class FamilyMemberHistory(base.FamilyMemberHistory):

    @property
    def family_member_history_participant(self) -> Any:
        return get_extension(self, FAMILY_MEMBER_HISTORY_PARTICIPANT_URL)

    @family_member_history_participant.setter
    def family_member_history_participant(self, value: Any) -> None:
        set_extension(self, FAMILY_MEMBER_HISTORY_PARTICIPANT_URL, value)

    @property
    def ukcore_associated_encounter(self) -> Any:
        return get_extension(self, UKCORE_ASSOCIATED_ENCOUNTER_URL)

    @ukcore_associated_encounter.setter
    def ukcore_associated_encounter(self, value: Any) -> None:
        set_extension(self, UKCORE_ASSOCIATED_ENCOUNTER_URL, value)

class Immunization(base.Immunization):

    @property
    def ukcore_vaccination_procedure(self) -> Any:
        return get_extension(self, UKCORE_VACCINATION_PROCEDURE_URL)

    @ukcore_vaccination_procedure.setter
    def ukcore_vaccination_procedure(self, value: Any) -> None:
        set_extension(self, UKCORE_VACCINATION_PROCEDURE_URL, value)

    @property
    def ukcore_parent_present(self) -> Any:
        return get_extension(self, UKCORE_PARENT_PRESENT_URL)

    @ukcore_parent_present.setter
    def ukcore_parent_present(self, value: Any) -> None:
        set_extension(self, UKCORE_PARENT_PRESENT_URL, value)

class List(base.List):

    @property
    def ukcore_care_setting_type(self) -> Any:
        return get_extension(self, UKCORE_CARE_SETTING_TYPE_URL)

    @ukcore_care_setting_type.setter
    def ukcore_care_setting_type(self, value: Any) -> None:
        set_extension(self, UKCORE_CARE_SETTING_TYPE_URL, value)

    @property
    def ukcore_list_warning_code(self) -> Any:
        return get_extension(self, UKCORE_LIST_WARNING_CODE_URL)

    @ukcore_list_warning_code.setter
    def ukcore_list_warning_code(self, value: Any) -> None:
        set_extension(self, UKCORE_LIST_WARNING_CODE_URL, value)

class Medication(base.Medication):

    @property
    def ukcore_medication_trade_family(self) -> Any:
        return get_extension(self, UKCORE_MEDICATION_TRADE_FAMILY_URL)

    @ukcore_medication_trade_family.setter
    def ukcore_medication_trade_family(self, value: Any) -> None:
        set_extension(self, UKCORE_MEDICATION_TRADE_FAMILY_URL, value)

class MedicationRequest(base.MedicationRequest):

    @property
    def ukcore_medication_repeat_information(self) -> Any:
        return get_extension(self, UKCORE_MEDICATION_REPEAT_INFORMATION_URL)

    @ukcore_medication_repeat_information.setter
    def ukcore_medication_repeat_information(self, value: Any) -> None:
        set_extension(self, UKCORE_MEDICATION_REPEAT_INFORMATION_URL, value)

class MedicationStatement(base.MedicationStatement):

    @property
    def ukcore_medication_prescribing_organization_type(self) -> Any:
        return get_extension(self, UKCORE_MEDICATION_PRESCRIBING_ORGANIZATION_TYPE_URL)

    @ukcore_medication_prescribing_organization_type.setter
    def ukcore_medication_prescribing_organization_type(self, value: Any) -> None:
        set_extension(self, UKCORE_MEDICATION_PRESCRIBING_ORGANIZATION_TYPE_URL, value)

    @property
    def ukcore_pharmacist_verified_indicator(self) -> Any:
        return get_extension(self, UKCORE_PHARMACIST_VERIFIED_INDICATOR_URL)

    @ukcore_pharmacist_verified_indicator.setter
    def ukcore_pharmacist_verified_indicator(self, value: Any) -> None:
        set_extension(self, UKCORE_PHARMACIST_VERIFIED_INDICATOR_URL, value)

    @property
    def ukcore_medication_statement_last_issue_date(self) -> Any:
        return get_extension(self, UKCORE_MEDICATION_STATEMENT_LAST_ISSUE_DATE_URL)

    @ukcore_medication_statement_last_issue_date.setter
    def ukcore_medication_statement_last_issue_date(self, value: Any) -> None:
        set_extension(self, UKCORE_MEDICATION_STATEMENT_LAST_ISSUE_DATE_URL, value)

class Observation(base.Observation):

    @property
    def observation_body_structure(self) -> Any:
        return get_extension(self, OBSERVATION_BODY_STRUCTURE_URL)

    @observation_body_structure.setter
    def observation_body_structure(self, value: Any) -> None:
        set_extension(self, OBSERVATION_BODY_STRUCTURE_URL, value)

    @property
    def observation_triggered_by(self) -> Any:
        return get_extension(self, OBSERVATION_TRIGGERED_BY_URL)

    @observation_triggered_by.setter
    def observation_triggered_by(self, value: Any) -> None:
        set_extension(self, OBSERVATION_TRIGGERED_BY_URL, value)

class Organization(base.Organization):

    @property
    def ukcore_main_location(self) -> Any:
        return get_extension(self, UKCORE_MAIN_LOCATION_URL)

    @ukcore_main_location.setter
    def ukcore_main_location(self, value: Any) -> None:
        set_extension(self, UKCORE_MAIN_LOCATION_URL, value)

class Patient(base.Patient):

    @property
    def ukcore_ethnic_category(self) -> Any:
        return get_extension(self, UKCORE_ETHNIC_CATEGORY_URL)

    @ukcore_ethnic_category.setter
    def ukcore_ethnic_category(self, value: Any) -> None:
        set_extension(self, UKCORE_ETHNIC_CATEGORY_URL, value)

    @property
    def ukcore_nhsnumber_unavailable_reason(self) -> Any:
        return get_extension(self, UKCORE_NHSNUMBER_UNAVAILABLE_REASON_URL)

    @ukcore_nhsnumber_unavailable_reason.setter
    def ukcore_nhsnumber_unavailable_reason(self, value: Any) -> None:
        set_extension(self, UKCORE_NHSNUMBER_UNAVAILABLE_REASON_URL, value)

    @property
    def ukcore_contact_rank(self) -> Any:
        return get_extension(self, UKCORE_CONTACT_RANK_URL)

    @ukcore_contact_rank.setter
    def ukcore_contact_rank(self, value: Any) -> None:
        set_extension(self, UKCORE_CONTACT_RANK_URL, value)

    @property
    def ukcore_copy_correspondence_indicator(self) -> Any:
        return get_extension(self, UKCORE_COPY_CORRESPONDENCE_INDICATOR_URL)

    @ukcore_copy_correspondence_indicator.setter
    def ukcore_copy_correspondence_indicator(self, value: Any) -> None:
        set_extension(self, UKCORE_COPY_CORRESPONDENCE_INDICATOR_URL, value)

    @property
    def ukcore_residential_status(self) -> Any:
        return get_extension(self, UKCORE_RESIDENTIAL_STATUS_URL)

    @ukcore_residential_status.setter
    def ukcore_residential_status(self, value: Any) -> None:
        set_extension(self, UKCORE_RESIDENTIAL_STATUS_URL, value)

    @property
    def ukcore_death_notification_status(self) -> Any:
        return get_extension(self, UKCORE_DEATH_NOTIFICATION_STATUS_URL)

    @ukcore_death_notification_status.setter
    def ukcore_death_notification_status(self, value: Any) -> None:
        set_extension(self, UKCORE_DEATH_NOTIFICATION_STATUS_URL, value)

    @property
    def ukcore_birth_sex(self) -> Any:
        return get_extension(self, UKCORE_BIRTH_SEX_URL)

    @ukcore_birth_sex.setter
    def ukcore_birth_sex(self, value: Any) -> None:
        set_extension(self, UKCORE_BIRTH_SEX_URL, value)

    @property
    def ukcore_contact_preference(self) -> Any:
        return get_extension(self, UKCORE_CONTACT_PREFERENCE_URL)

    @ukcore_contact_preference.setter
    def ukcore_contact_preference(self, value: Any) -> None:
        set_extension(self, UKCORE_CONTACT_PREFERENCE_URL, value)

    @property
    def ukcore_nhsnumber_verification_status(self) -> Any:
        return get_extension(self, UKCORE_NHSNUMBER_VERIFICATION_STATUS_URL)

    @ukcore_nhsnumber_verification_status.setter
    def ukcore_nhsnumber_verification_status(self, value: Any) -> None:
        set_extension(self, UKCORE_NHSNUMBER_VERIFICATION_STATUS_URL, value)

class RelatedPerson(base.RelatedPerson):

    @property
    def ukcore_copy_correspondence_indicator(self) -> Any:
        return get_extension(self, UKCORE_COPY_CORRESPONDENCE_INDICATOR_URL)

    @ukcore_copy_correspondence_indicator.setter
    def ukcore_copy_correspondence_indicator(self, value: Any) -> None:
        set_extension(self, UKCORE_COPY_CORRESPONDENCE_INDICATOR_URL, value)

    @property
    def ukcore_contact_preference(self) -> Any:
        return get_extension(self, UKCORE_CONTACT_PREFERENCE_URL)

    @ukcore_contact_preference.setter
    def ukcore_contact_preference(self, value: Any) -> None:
        set_extension(self, UKCORE_CONTACT_PREFERENCE_URL, value)

class ServiceRequest(base.ServiceRequest):

    @property
    def ukcore_source_of_service_request(self) -> Any:
        return get_extension(self, UKCORE_SOURCE_OF_SERVICE_REQUEST_URL)

    @ukcore_source_of_service_request.setter
    def ukcore_source_of_service_request(self, value: Any) -> None:
        set_extension(self, UKCORE_SOURCE_OF_SERVICE_REQUEST_URL, value)

    @property
    def ukcore_priority_reason(self) -> Any:
        return get_extension(self, UKCORE_PRIORITY_REASON_URL)

    @ukcore_priority_reason.setter
    def ukcore_priority_reason(self, value: Any) -> None:
        set_extension(self, UKCORE_PRIORITY_REASON_URL, value)

    @property
    def ukcore_coverage(self) -> Any:
        return get_extension(self, UKCORE_COVERAGE_URL)

    @ukcore_coverage.setter
    def ukcore_coverage(self, value: Any) -> None:
        set_extension(self, UKCORE_COVERAGE_URL, value)

    @property
    def ukcore_additional_contact(self) -> Any:
        return get_extension(self, UKCORE_ADDITIONAL_CONTACT_URL)

    @ukcore_additional_contact.setter
    def ukcore_additional_contact(self, value: Any) -> None:
        set_extension(self, UKCORE_ADDITIONAL_CONTACT_URL, value)

class Slot(base.Slot):

    @property
    def ukcore_delivery_channel(self) -> Any:
        return get_extension(self, UKCORE_DELIVERY_CHANNEL_URL)

    @ukcore_delivery_channel.setter
    def ukcore_delivery_channel(self, value: Any) -> None:
        set_extension(self, UKCORE_DELIVERY_CHANNEL_URL, value)

class Specimen(base.Specimen):

    @property
    def specimen_collection_collector(self) -> Any:
        return get_extension(self, SPECIMEN_COLLECTION_COLLECTOR_URL)

    @specimen_collection_collector.setter
    def specimen_collection_collector(self, value: Any) -> None:
        set_extension(self, SPECIMEN_COLLECTION_COLLECTOR_URL, value)

    @property
    def ukcore_sample_category(self) -> Any:
        return get_extension(self, UKCORE_SAMPLE_CATEGORY_URL)

    @ukcore_sample_category.setter
    def ukcore_sample_category(self, value: Any) -> None:
        set_extension(self, UKCORE_SAMPLE_CATEGORY_URL, value)

    @property
    def ukcore_body_site_reference(self) -> Any:
        return get_extension(self, UKCORE_BODY_SITE_REFERENCE_URL)

    @ukcore_body_site_reference.setter
    def ukcore_body_site_reference(self, value: Any) -> None:
        set_extension(self, UKCORE_BODY_SITE_REFERENCE_URL, value)
