from __future__ import annotations

from zato.fhir.r4_0_1.ukcore.v2_0_2.extensions import (
    UKCORE_CONDITION_EPISODE_URL,
    UKCORE_LEGAL_STATUS_URL,
    UKCORE_ETHNIC_CATEGORY_URL,
    UKCORE_ALLERGY_INTOLERANCE_END_URL,
    UKCORE_CARE_SETTING_TYPE_URL,
    UKCORE_NHSNUMBER_UNAVAILABLE_REASON_URL,
    DIAGNOSTIC_REPORT_SUPPORTING_INFO_URL,
    UKCORE_CONTACT_RANK_URL,
    UKCORE_OTHER_CONTACT_SYSTEM_URL,
    DIAGNOSTIC_REPORT_NOTE_URL,
    UKCORE_DISCHARGE_METHOD_URL,
    UKCORE_COPY_CORRESPONDENCE_INDICATOR_URL,
    UKCORE_BOOKING_ORGANIZATION_URL,
    UKCORE_SOURCE_OF_SERVICE_REQUEST_URL,
    UKCORE_RESIDENTIAL_STATUS_URL,
    UKCORE_OUTCOME_OF_ATTENDANCE_URL,
    UKCORE_ADDRESS_KEY_URL,
    SPECIMEN_COLLECTION_COLLECTOR_URL,
    DIAGNOSTIC_REPORT_COMPOSITION_URL,
    UKCORE_PRIORITY_REASON_URL,
    OBSERVATION_BODY_STRUCTURE_URL,
    UKCORE_CODING_SCTDESC_DISPLAY_URL,
    UKCORE_MEDICATION_PRESCRIBING_ORGANIZATION_TYPE_URL,
    UKCORE_DEATH_NOTIFICATION_STATUS_URL,
    UKCORE_EMERGENCY_CARE_DISCHARGE_STATUS_URL,
    UKCORE_DELIVERY_CHANNEL_URL,
    UKCORE_LIST_WARNING_CODE_URL,
    UKCORE_BIRTH_SEX_URL,
    OBSERVATION_TRIGGERED_BY_URL,
    FAMILY_MEMBER_HISTORY_PARTICIPANT_URL,
    UKCORE_CONTACT_PREFERENCE_URL,
    UKCORE_PHARMACIST_VERIFIED_INDICATOR_URL,
    UKCORE_ASSOCIATED_ENCOUNTER_URL,
    UKCORE_SAMPLE_CATEGORY_URL,
    UKCORE_COVERAGE_URL,
    UKCORE_DEVICE_REFERENCE_URL,
    UKCORE_BODY_SITE_REFERENCE_URL,
    UKCORE_MEDICATION_REPEAT_INFORMATION_URL,
    UKCORE_MEDICATION_STATEMENT_LAST_ISSUE_DATE_URL,
    UKCORE_NHSNUMBER_VERIFICATION_STATUS_URL,
    UKCORE_VACCINATION_PROCEDURE_URL,
    UKCORE_ADMISSION_METHOD_URL,
    UKCORE_MAIN_LOCATION_URL,
    UKCORE_ADDITIONAL_CONTACT_URL,
    UKCORE_MEDICATION_TRADE_FAMILY_URL,
    UKCORE_EVIDENCE_URL,
    UKCORE_PARENT_PRESENT_URL,
)

from zato.fhir.r4_0_1.ukcore.v2_0_2.resources import (
    Address,
    AllergyIntolerance,
    Appointment,
    Coding,
    Composition,
    Condition,
    ContactPoint,
    DiagnosticReport,
    Encounter,
    FamilyMemberHistory,
    Immunization,
    List,
    Medication,
    MedicationRequest,
    MedicationStatement,
    Observation,
    Organization,
    Patient,
    RelatedPerson,
    ServiceRequest,
    Slot,
    Specimen,
)


class TestImports:

    def test_address_is_importable(self):
        assert Address is not None

    def test_allergyintolerance_is_importable(self):
        assert AllergyIntolerance is not None

    def test_appointment_is_importable(self):
        assert Appointment is not None

    def test_coding_is_importable(self):
        assert Coding is not None

    def test_composition_is_importable(self):
        assert Composition is not None

    def test_condition_is_importable(self):
        assert Condition is not None

    def test_contactpoint_is_importable(self):
        assert ContactPoint is not None

    def test_diagnosticreport_is_importable(self):
        assert DiagnosticReport is not None

    def test_encounter_is_importable(self):
        assert Encounter is not None

    def test_familymemberhistory_is_importable(self):
        assert FamilyMemberHistory is not None

    def test_immunization_is_importable(self):
        assert Immunization is not None

    def test_list_is_importable(self):
        assert List is not None

    def test_medication_is_importable(self):
        assert Medication is not None

    def test_medicationrequest_is_importable(self):
        assert MedicationRequest is not None

    def test_medicationstatement_is_importable(self):
        assert MedicationStatement is not None

    def test_observation_is_importable(self):
        assert Observation is not None

    def test_organization_is_importable(self):
        assert Organization is not None

    def test_patient_is_importable(self):
        assert Patient is not None

    def test_relatedperson_is_importable(self):
        assert RelatedPerson is not None

    def test_servicerequest_is_importable(self):
        assert ServiceRequest is not None

    def test_slot_is_importable(self):
        assert Slot is not None

    def test_specimen_is_importable(self):
        assert Specimen is not None


class TestURLConstants:

    def test_ukcore_condition_episode_url(self):
        assert UKCORE_CONDITION_EPISODE_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-ConditionEpisode'

    def test_ukcore_legal_status_url(self):
        assert UKCORE_LEGAL_STATUS_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-LegalStatus'

    def test_ukcore_ethnic_category_url(self):
        assert UKCORE_ETHNIC_CATEGORY_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-EthnicCategory'

    def test_ukcore_allergy_intolerance_end_url(self):
        assert UKCORE_ALLERGY_INTOLERANCE_END_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-AllergyIntoleranceEnd'

    def test_ukcore_care_setting_type_url(self):
        assert UKCORE_CARE_SETTING_TYPE_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-CareSettingType'

    def test_ukcore_nhsnumber_unavailable_reason_url(self):
        assert UKCORE_NHSNUMBER_UNAVAILABLE_REASON_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSNumberUnavailableReason'

    def test_diagnostic_report_supporting_info_url(self):
        assert DIAGNOSTIC_REPORT_SUPPORTING_INFO_URL == 'http://hl7.org/fhir/5.0/StructureDefinition/extension-DiagnosticReport.supportingInfo'

    def test_ukcore_contact_rank_url(self):
        assert UKCORE_CONTACT_RANK_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-ContactRank'

    def test_ukcore_other_contact_system_url(self):
        assert UKCORE_OTHER_CONTACT_SYSTEM_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-OtherContactSystem'

    def test_diagnostic_report_note_url(self):
        assert DIAGNOSTIC_REPORT_NOTE_URL == 'http://hl7.org/fhir/5.0/StructureDefinition/extension-DiagnosticReport.note'

    def test_ukcore_discharge_method_url(self):
        assert UKCORE_DISCHARGE_METHOD_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-DischargeMethod'

    def test_ukcore_copy_correspondence_indicator_url(self):
        assert UKCORE_COPY_CORRESPONDENCE_INDICATOR_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-CopyCorrespondenceIndicator'

    def test_ukcore_booking_organization_url(self):
        assert UKCORE_BOOKING_ORGANIZATION_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-BookingOrganization'

    def test_ukcore_source_of_service_request_url(self):
        assert UKCORE_SOURCE_OF_SERVICE_REQUEST_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-SourceOfServiceRequest'

    def test_ukcore_residential_status_url(self):
        assert UKCORE_RESIDENTIAL_STATUS_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-ResidentialStatus'

    def test_ukcore_outcome_of_attendance_url(self):
        assert UKCORE_OUTCOME_OF_ATTENDANCE_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-OutcomeOfAttendance'

    def test_ukcore_address_key_url(self):
        assert UKCORE_ADDRESS_KEY_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-AddressKey'

    def test_specimen_collection_collector_url(self):
        assert SPECIMEN_COLLECTION_COLLECTOR_URL == 'http://hl7.org/fhir/5.0/StructureDefinition/extension-Specimen.collection.collector'

    def test_diagnostic_report_composition_url(self):
        assert DIAGNOSTIC_REPORT_COMPOSITION_URL == 'http://hl7.org/fhir/5.0/StructureDefinition/extension-DiagnosticReport.composition'

    def test_ukcore_priority_reason_url(self):
        assert UKCORE_PRIORITY_REASON_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-PriorityReason'

    def test_observation_body_structure_url(self):
        assert OBSERVATION_BODY_STRUCTURE_URL == 'http://hl7.org/fhir/5.0/StructureDefinition/extension-Observation.bodyStructure'

    def test_ukcore_coding_sctdesc_display_url(self):
        assert UKCORE_CODING_SCTDESC_DISPLAY_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-CodingSCTDescDisplay'

    def test_ukcore_medication_prescribing_organization_type_url(self):
        assert UKCORE_MEDICATION_PRESCRIBING_ORGANIZATION_TYPE_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-MedicationPrescribingOrganizationType'

    def test_ukcore_death_notification_status_url(self):
        assert UKCORE_DEATH_NOTIFICATION_STATUS_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-DeathNotificationStatus'

    def test_ukcore_emergency_care_discharge_status_url(self):
        assert UKCORE_EMERGENCY_CARE_DISCHARGE_STATUS_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-EmergencyCareDischargeStatus'

    def test_ukcore_delivery_channel_url(self):
        assert UKCORE_DELIVERY_CHANNEL_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-DeliveryChannel'

    def test_ukcore_list_warning_code_url(self):
        assert UKCORE_LIST_WARNING_CODE_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-ListWarningCode'

    def test_ukcore_birth_sex_url(self):
        assert UKCORE_BIRTH_SEX_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-BirthSex'

    def test_observation_triggered_by_url(self):
        assert OBSERVATION_TRIGGERED_BY_URL == 'http://hl7.org/fhir/5.0/StructureDefinition/extension-Observation.triggeredBy'

    def test_family_member_history_participant_url(self):
        assert FAMILY_MEMBER_HISTORY_PARTICIPANT_URL == 'http://hl7.org/fhir/5.0/StructureDefinition/extension-FamilyMemberHistory.participant'

    def test_ukcore_contact_preference_url(self):
        assert UKCORE_CONTACT_PREFERENCE_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-ContactPreference'

    def test_ukcore_pharmacist_verified_indicator_url(self):
        assert UKCORE_PHARMACIST_VERIFIED_INDICATOR_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-PharmacistVerifiedIndicator'

    def test_ukcore_associated_encounter_url(self):
        assert UKCORE_ASSOCIATED_ENCOUNTER_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-AssociatedEncounter'

    def test_ukcore_sample_category_url(self):
        assert UKCORE_SAMPLE_CATEGORY_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-SampleCategory'

    def test_ukcore_coverage_url(self):
        assert UKCORE_COVERAGE_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-Coverage'

    def test_ukcore_device_reference_url(self):
        assert UKCORE_DEVICE_REFERENCE_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-DeviceReference'

    def test_ukcore_body_site_reference_url(self):
        assert UKCORE_BODY_SITE_REFERENCE_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-BodySiteReference'

    def test_ukcore_medication_repeat_information_url(self):
        assert UKCORE_MEDICATION_REPEAT_INFORMATION_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-MedicationRepeatInformation'

    def test_ukcore_medication_statement_last_issue_date_url(self):
        assert UKCORE_MEDICATION_STATEMENT_LAST_ISSUE_DATE_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-MedicationStatementLastIssueDate'

    def test_ukcore_nhsnumber_verification_status_url(self):
        assert UKCORE_NHSNUMBER_VERIFICATION_STATUS_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSNumberVerificationStatus'

    def test_ukcore_vaccination_procedure_url(self):
        assert UKCORE_VACCINATION_PROCEDURE_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure'

    def test_ukcore_admission_method_url(self):
        assert UKCORE_ADMISSION_METHOD_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-AdmissionMethod'

    def test_ukcore_main_location_url(self):
        assert UKCORE_MAIN_LOCATION_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-MainLocation'

    def test_ukcore_additional_contact_url(self):
        assert UKCORE_ADDITIONAL_CONTACT_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-AdditionalContact'

    def test_ukcore_medication_trade_family_url(self):
        assert UKCORE_MEDICATION_TRADE_FAMILY_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-MedicationTradeFamily'

    def test_ukcore_evidence_url(self):
        assert UKCORE_EVIDENCE_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-Evidence'

    def test_ukcore_parent_present_url(self):
        assert UKCORE_PARENT_PRESENT_URL == 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-ParentPresent'


class TestPropertyAccess:

    def test_address_ukcore_address_key_roundtrip(self):
        r = Address()
        r.ukcore_address_key = "test-value"
        result = r.ukcore_address_key
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_allergyintolerance_ukcore_allergy_intolerance_end_roundtrip(self):
        r = AllergyIntolerance()
        r.ukcore_allergy_intolerance_end = "test-value"
        result = r.ukcore_allergy_intolerance_end
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_allergyintolerance_ukcore_evidence_roundtrip(self):
        r = AllergyIntolerance()
        r.ukcore_evidence = "test-value"
        result = r.ukcore_evidence
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_appointment_ukcore_booking_organization_roundtrip(self):
        r = Appointment()
        r.ukcore_booking_organization = "test-value"
        result = r.ukcore_booking_organization
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_appointment_ukcore_delivery_channel_roundtrip(self):
        r = Appointment()
        r.ukcore_delivery_channel = "test-value"
        result = r.ukcore_delivery_channel
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_coding_ukcore_coding_sctdesc_display_roundtrip(self):
        r = Coding()
        r.ukcore_coding_sctdesc_display = "test-value"
        result = r.ukcore_coding_sctdesc_display
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_composition_ukcore_care_setting_type_roundtrip(self):
        r = Composition()
        r.ukcore_care_setting_type = "test-value"
        result = r.ukcore_care_setting_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_condition_ukcore_condition_episode_roundtrip(self):
        r = Condition()
        r.ukcore_condition_episode = "test-value"
        result = r.ukcore_condition_episode
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contactpoint_ukcore_other_contact_system_roundtrip(self):
        r = ContactPoint()
        r.ukcore_other_contact_system = "test-value"
        result = r.ukcore_other_contact_system
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_diagnostic_report_supporting_info_roundtrip(self):
        r = DiagnosticReport()
        r.diagnostic_report_supporting_info = "test-value"
        result = r.diagnostic_report_supporting_info
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_diagnostic_report_note_roundtrip(self):
        r = DiagnosticReport()
        r.diagnostic_report_note = "test-value"
        result = r.diagnostic_report_note
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_diagnostic_report_composition_roundtrip(self):
        r = DiagnosticReport()
        r.diagnostic_report_composition = "test-value"
        result = r.diagnostic_report_composition
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_ukcore_device_reference_roundtrip(self):
        r = DiagnosticReport()
        r.ukcore_device_reference = "test-value"
        result = r.ukcore_device_reference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_ukcore_legal_status_roundtrip(self):
        r = Encounter()
        r.ukcore_legal_status = "test-value"
        result = r.ukcore_legal_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_ukcore_discharge_method_roundtrip(self):
        r = Encounter()
        r.ukcore_discharge_method = "test-value"
        result = r.ukcore_discharge_method
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_ukcore_outcome_of_attendance_roundtrip(self):
        r = Encounter()
        r.ukcore_outcome_of_attendance = "test-value"
        result = r.ukcore_outcome_of_attendance
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_ukcore_emergency_care_discharge_status_roundtrip(self):
        r = Encounter()
        r.ukcore_emergency_care_discharge_status = "test-value"
        result = r.ukcore_emergency_care_discharge_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_ukcore_admission_method_roundtrip(self):
        r = Encounter()
        r.ukcore_admission_method = "test-value"
        result = r.ukcore_admission_method
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_familymemberhistory_family_member_history_participant_roundtrip(self):
        r = FamilyMemberHistory()
        r.family_member_history_participant = "test-value"
        result = r.family_member_history_participant
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_familymemberhistory_ukcore_associated_encounter_roundtrip(self):
        r = FamilyMemberHistory()
        r.ukcore_associated_encounter = "test-value"
        result = r.ukcore_associated_encounter
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_immunization_ukcore_vaccination_procedure_roundtrip(self):
        r = Immunization()
        r.ukcore_vaccination_procedure = "test-value"
        result = r.ukcore_vaccination_procedure
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_immunization_ukcore_parent_present_roundtrip(self):
        r = Immunization()
        r.ukcore_parent_present = "test-value"
        result = r.ukcore_parent_present
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_list_ukcore_care_setting_type_roundtrip(self):
        r = List()
        r.ukcore_care_setting_type = "test-value"
        result = r.ukcore_care_setting_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_list_ukcore_list_warning_code_roundtrip(self):
        r = List()
        r.ukcore_list_warning_code = "test-value"
        result = r.ukcore_list_warning_code
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medication_ukcore_medication_trade_family_roundtrip(self):
        r = Medication()
        r.ukcore_medication_trade_family = "test-value"
        result = r.ukcore_medication_trade_family
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationrequest_ukcore_medication_repeat_information_roundtrip(self):
        r = MedicationRequest()
        r.ukcore_medication_repeat_information = "test-value"
        result = r.ukcore_medication_repeat_information
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationstatement_ukcore_medication_prescribing_organization_type_roundtrip(self):
        r = MedicationStatement()
        r.ukcore_medication_prescribing_organization_type = "test-value"
        result = r.ukcore_medication_prescribing_organization_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationstatement_ukcore_pharmacist_verified_indicator_roundtrip(self):
        r = MedicationStatement()
        r.ukcore_pharmacist_verified_indicator = "test-value"
        result = r.ukcore_pharmacist_verified_indicator
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationstatement_ukcore_medication_statement_last_issue_date_roundtrip(self):
        r = MedicationStatement()
        r.ukcore_medication_statement_last_issue_date = "test-value"
        result = r.ukcore_medication_statement_last_issue_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_observation_body_structure_roundtrip(self):
        r = Observation()
        r.observation_body_structure = "test-value"
        result = r.observation_body_structure
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_observation_triggered_by_roundtrip(self):
        r = Observation()
        r.observation_triggered_by = "test-value"
        result = r.observation_triggered_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_ukcore_main_location_roundtrip(self):
        r = Organization()
        r.ukcore_main_location = "test-value"
        result = r.ukcore_main_location
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_ukcore_ethnic_category_roundtrip(self):
        r = Patient()
        r.ukcore_ethnic_category = "test-value"
        result = r.ukcore_ethnic_category
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_ukcore_nhsnumber_unavailable_reason_roundtrip(self):
        r = Patient()
        r.ukcore_nhsnumber_unavailable_reason = "test-value"
        result = r.ukcore_nhsnumber_unavailable_reason
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_ukcore_contact_rank_roundtrip(self):
        r = Patient()
        r.ukcore_contact_rank = "test-value"
        result = r.ukcore_contact_rank
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_ukcore_copy_correspondence_indicator_roundtrip(self):
        r = Patient()
        r.ukcore_copy_correspondence_indicator = "test-value"
        result = r.ukcore_copy_correspondence_indicator
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_ukcore_residential_status_roundtrip(self):
        r = Patient()
        r.ukcore_residential_status = "test-value"
        result = r.ukcore_residential_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_ukcore_death_notification_status_roundtrip(self):
        r = Patient()
        r.ukcore_death_notification_status = "test-value"
        result = r.ukcore_death_notification_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_ukcore_birth_sex_roundtrip(self):
        r = Patient()
        r.ukcore_birth_sex = "test-value"
        result = r.ukcore_birth_sex
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_ukcore_contact_preference_roundtrip(self):
        r = Patient()
        r.ukcore_contact_preference = "test-value"
        result = r.ukcore_contact_preference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_ukcore_nhsnumber_verification_status_roundtrip(self):
        r = Patient()
        r.ukcore_nhsnumber_verification_status = "test-value"
        result = r.ukcore_nhsnumber_verification_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_relatedperson_ukcore_copy_correspondence_indicator_roundtrip(self):
        r = RelatedPerson()
        r.ukcore_copy_correspondence_indicator = "test-value"
        result = r.ukcore_copy_correspondence_indicator
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_relatedperson_ukcore_contact_preference_roundtrip(self):
        r = RelatedPerson()
        r.ukcore_contact_preference = "test-value"
        result = r.ukcore_contact_preference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_servicerequest_ukcore_source_of_service_request_roundtrip(self):
        r = ServiceRequest()
        r.ukcore_source_of_service_request = "test-value"
        result = r.ukcore_source_of_service_request
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_servicerequest_ukcore_priority_reason_roundtrip(self):
        r = ServiceRequest()
        r.ukcore_priority_reason = "test-value"
        result = r.ukcore_priority_reason
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_servicerequest_ukcore_coverage_roundtrip(self):
        r = ServiceRequest()
        r.ukcore_coverage = "test-value"
        result = r.ukcore_coverage
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_servicerequest_ukcore_additional_contact_roundtrip(self):
        r = ServiceRequest()
        r.ukcore_additional_contact = "test-value"
        result = r.ukcore_additional_contact
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_slot_ukcore_delivery_channel_roundtrip(self):
        r = Slot()
        r.ukcore_delivery_channel = "test-value"
        result = r.ukcore_delivery_channel
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_specimen_specimen_collection_collector_roundtrip(self):
        r = Specimen()
        r.specimen_collection_collector = "test-value"
        result = r.specimen_collection_collector
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_specimen_ukcore_sample_category_roundtrip(self):
        r = Specimen()
        r.ukcore_sample_category = "test-value"
        result = r.ukcore_sample_category
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_specimen_ukcore_body_site_reference_roundtrip(self):
        r = Specimen()
        r.ukcore_body_site_reference = "test-value"
        result = r.ukcore_body_site_reference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

