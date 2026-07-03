from __future__ import annotations

from zato.fhir.r4_0_1.fr_core.v2_1_0.extensions import (
    ORGANIZATION_PRESTATION_DISCIPLINE_URL,
    COMMENT_URL,
    PATIENT_CONTACT_IDENTIFIER_URL,
    PATIENT_NATIONALITY_URL,
    SERVICE_TYPE_DURATION_URL,
    SLOT_DATE_URL,
    ORGANIZATION_DESCRIPTION_URL,
    ORGANIZATION_EXTERNAL_URL,
    ESTIMATED_DISCHARGE_DATE_URL,
    PRACTITIONER_PROFESSION_URL,
    ORGANIZATION_ACTIVITY_TYPE_URL,
    IDENTITY_RELIABILITY_URL,
    USE_PERIOD_URL,
    PATIENT_BIRTH_LIST_GIVEN_NAME_URL,
    SCHEDULE_AVAILABILITY_TIME_URL,
    ORGANIZATION_APPLICANT_ACT_URL,
    HUMAN_NAME_ASSEMBLY_ORDER_URL,
    PATIENT_DEATH_PLACE_URL,
    OBSERVATION_HEIGHT_BODY_POSITION_URL,
    ORGANIZATION_FIELD_URL,
    PRACTITIONER_SPECIALTY_URL,
    LOCATION_POSITION_ROOM_URL,
    ORGANIZATION_ACTIVITY_FIELD_URL,
    OBSERVATION_BODY_POSITION_EXT_URL,
    ADDRESS_INSEE_CODE_URL,
    ORGANIZATION_NUMBER_OF_THEORICAL_ACCOMADATION_SPACE_URL,
    ORGANIZATION_ANALYSIS_SECTION_URL,
    CONTACT_POINT_EMAIL_TYPE_URL,
    ORGANIZATION_EXECUTANT_URL,
    LUNAR_DATE_URL,
    ORGANIZATION_SHORT_NAME_URL,
    PATIENT_BIRTHDATE_UPDATE_INDICATOR_URL,
    OBSERVATION_LEVEL_OF_EXERTION_URL,
    APPOINTMENT_OPERATOR_URL,
    ORGANIZATION_BUDGET_LETTER_URL,
)

from zato.fhir.r4_0_1.fr_core.v2_1_0.resources import (
    Address,
    Appointment,
    ContactPoint,
    Encounter,
    HealthcareService,
    HumanName,
    Location,
    Observation,
    Organization,
    Patient,
    Practitioner,
    PractitionerRole,
    Schedule,
    Slot,
)


class TestImports:

    def test_address_is_importable(self):
        assert Address is not None

    def test_appointment_is_importable(self):
        assert Appointment is not None

    def test_contactpoint_is_importable(self):
        assert ContactPoint is not None

    def test_encounter_is_importable(self):
        assert Encounter is not None

    def test_healthcareservice_is_importable(self):
        assert HealthcareService is not None

    def test_humanname_is_importable(self):
        assert HumanName is not None

    def test_location_is_importable(self):
        assert Location is not None

    def test_observation_is_importable(self):
        assert Observation is not None

    def test_organization_is_importable(self):
        assert Organization is not None

    def test_patient_is_importable(self):
        assert Patient is not None

    def test_practitioner_is_importable(self):
        assert Practitioner is not None

    def test_practitionerrole_is_importable(self):
        assert PractitionerRole is not None

    def test_schedule_is_importable(self):
        assert Schedule is not None

    def test_slot_is_importable(self):
        assert Slot is not None


class TestURLConstants:

    def test_organization_prestation_discipline_url(self):
        assert ORGANIZATION_PRESTATION_DISCIPLINE_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-organization-prestation-discipline'

    def test_comment_url(self):
        assert COMMENT_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-comment'

    def test_patient_contact_identifier_url(self):
        assert PATIENT_CONTACT_IDENTIFIER_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-patient-contact-identifier'

    def test_patient_nationality_url(self):
        assert PATIENT_NATIONALITY_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-patient-nationality'

    def test_service_type_duration_url(self):
        assert SERVICE_TYPE_DURATION_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-service-type-duration'

    def test_slot_date_url(self):
        assert SLOT_DATE_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-slot-date'

    def test_organization_description_url(self):
        assert ORGANIZATION_DESCRIPTION_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-organization-description'

    def test_organization_external_url(self):
        assert ORGANIZATION_EXTERNAL_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-organization-external'

    def test_estimated_discharge_date_url(self):
        assert ESTIMATED_DISCHARGE_DATE_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-estimated-discharge-date'

    def test_practitioner_profession_url(self):
        assert PRACTITIONER_PROFESSION_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-practitioner-profession'

    def test_organization_activity_type_url(self):
        assert ORGANIZATION_ACTIVITY_TYPE_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-organization-activity-type'

    def test_identity_reliability_url(self):
        assert IDENTITY_RELIABILITY_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-identity-reliability'

    def test_use_period_url(self):
        assert USE_PERIOD_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-use-period'

    def test_patient_birth_list_given_name_url(self):
        assert PATIENT_BIRTH_LIST_GIVEN_NAME_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-patient-birth-list-given-name'

    def test_schedule_availability_time_url(self):
        assert SCHEDULE_AVAILABILITY_TIME_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-schedule-availability-time'

    def test_organization_applicant_act_url(self):
        assert ORGANIZATION_APPLICANT_ACT_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-organization-applicant-act'

    def test_human_name_assembly_order_url(self):
        assert HUMAN_NAME_ASSEMBLY_ORDER_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-human-name-assembly-order'

    def test_patient_death_place_url(self):
        assert PATIENT_DEATH_PLACE_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-patient-death-place'

    def test_observation_height_body_position_url(self):
        assert OBSERVATION_HEIGHT_BODY_POSITION_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-observation-height-body-position'

    def test_organization_field_url(self):
        assert ORGANIZATION_FIELD_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-organization-field'

    def test_practitioner_specialty_url(self):
        assert PRACTITIONER_SPECIALTY_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-practitioner-specialty'

    def test_location_position_room_url(self):
        assert LOCATION_POSITION_ROOM_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-location-position-room'

    def test_organization_activity_field_url(self):
        assert ORGANIZATION_ACTIVITY_FIELD_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-organization-activity-field'

    def test_observation_body_position_ext_url(self):
        assert OBSERVATION_BODY_POSITION_EXT_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-observation-body-position-ext'

    def test_address_insee_code_url(self):
        assert ADDRESS_INSEE_CODE_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-address-insee-code'

    def test_organization_number_of_theorical_accomadation_space_url(self):
        assert ORGANIZATION_NUMBER_OF_THEORICAL_ACCOMADATION_SPACE_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-organization-number-of-theorical-accomadation-space'

    def test_organization_analysis_section_url(self):
        assert ORGANIZATION_ANALYSIS_SECTION_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-organization-analysis-section'

    def test_contact_point_email_type_url(self):
        assert CONTACT_POINT_EMAIL_TYPE_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-contact-point-email-type'

    def test_organization_executant_url(self):
        assert ORGANIZATION_EXECUTANT_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-organization-executant'

    def test_lunar_date_url(self):
        assert LUNAR_DATE_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-lunar-date'

    def test_organization_short_name_url(self):
        assert ORGANIZATION_SHORT_NAME_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-organization-short-name'

    def test_patient_birthdate_update_indicator_url(self):
        assert PATIENT_BIRTHDATE_UPDATE_INDICATOR_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-patient-birthdate-update-indicator'

    def test_observation_level_of_exertion_url(self):
        assert OBSERVATION_LEVEL_OF_EXERTION_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-observation-level-of-exertion'

    def test_appointment_operator_url(self):
        assert APPOINTMENT_OPERATOR_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-appointment-operator'

    def test_organization_budget_letter_url(self):
        assert ORGANIZATION_BUDGET_LETTER_URL == 'https://hl7.fr/ig/fhir/core/StructureDefinition/fr-core-organization-budget-letter'


class TestPropertyAccess:

    def test_address_address_insee_code_roundtrip(self):
        r = Address()
        r.address_insee_code = "test-value"
        result = r.address_insee_code
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_appointment_appointment_operator_roundtrip(self):
        r = Appointment()
        r.appointment_operator = "test-value"
        result = r.appointment_operator
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contactpoint_contact_point_email_type_roundtrip(self):
        r = ContactPoint()
        r.contact_point_email_type = "test-value"
        result = r.contact_point_email_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_estimated_discharge_date_roundtrip(self):
        r = Encounter()
        r.estimated_discharge_date = "test-value"
        result = r.estimated_discharge_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_healthcareservice_service_type_duration_roundtrip(self):
        r = HealthcareService()
        r.service_type_duration = "test-value"
        result = r.service_type_duration
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_humanname_human_name_assembly_order_roundtrip(self):
        r = HumanName()
        r.human_name_assembly_order = "test-value"
        result = r.human_name_assembly_order
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_location_use_period_roundtrip(self):
        r = Location()
        r.use_period = "test-value"
        result = r.use_period
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_observation_height_body_position_roundtrip(self):
        r = Observation()
        r.observation_height_body_position = "test-value"
        result = r.observation_height_body_position
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_observation_body_position_ext_roundtrip(self):
        r = Observation()
        r.observation_body_position_ext = "test-value"
        result = r.observation_body_position_ext
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_observation_level_of_exertion_roundtrip(self):
        r = Observation()
        r.observation_level_of_exertion = "test-value"
        result = r.observation_level_of_exertion
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_organization_prestation_discipline_roundtrip(self):
        r = Organization()
        r.organization_prestation_discipline = "test-value"
        result = r.organization_prestation_discipline
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_organization_description_roundtrip(self):
        r = Organization()
        r.organization_description = "test-value"
        result = r.organization_description
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_organization_external_roundtrip(self):
        r = Organization()
        r.organization_external = "test-value"
        result = r.organization_external
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_organization_activity_type_roundtrip(self):
        r = Organization()
        r.organization_activity_type = "test-value"
        result = r.organization_activity_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_organization_applicant_act_roundtrip(self):
        r = Organization()
        r.organization_applicant_act = "test-value"
        result = r.organization_applicant_act
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_organization_field_roundtrip(self):
        r = Organization()
        r.organization_field = "test-value"
        result = r.organization_field
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_organization_activity_field_roundtrip(self):
        r = Organization()
        r.organization_activity_field = "test-value"
        result = r.organization_activity_field
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_organization_number_of_theorical_accomadation_space_roundtrip(self):
        r = Organization()
        r.organization_number_of_theorical_accomadation_space = "test-value"
        result = r.organization_number_of_theorical_accomadation_space
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_organization_analysis_section_roundtrip(self):
        r = Organization()
        r.organization_analysis_section = "test-value"
        result = r.organization_analysis_section
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_organization_executant_roundtrip(self):
        r = Organization()
        r.organization_executant = "test-value"
        result = r.organization_executant
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_organization_short_name_roundtrip(self):
        r = Organization()
        r.organization_short_name = "test-value"
        result = r.organization_short_name
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_organization_budget_letter_roundtrip(self):
        r = Organization()
        r.organization_budget_letter = "test-value"
        result = r.organization_budget_letter
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_nationality_roundtrip(self):
        r = Patient()
        r.patient_nationality = "test-value"
        result = r.patient_nationality
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_identity_reliability_roundtrip(self):
        r = Patient()
        r.identity_reliability = "test-value"
        result = r.identity_reliability
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_death_place_roundtrip(self):
        r = Patient()
        r.patient_death_place = "test-value"
        result = r.patient_death_place
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_lunar_date_roundtrip(self):
        r = Patient()
        r.lunar_date = "test-value"
        result = r.lunar_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_birthdate_update_indicator_roundtrip(self):
        r = Patient()
        r.patient_birthdate_update_indicator = "test-value"
        result = r.patient_birthdate_update_indicator
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitioner_practitioner_profession_roundtrip(self):
        r = Practitioner()
        r.practitioner_profession = "test-value"
        result = r.practitioner_profession
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitioner_practitioner_specialty_roundtrip(self):
        r = Practitioner()
        r.practitioner_specialty = "test-value"
        result = r.practitioner_specialty
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitionerrole_service_type_duration_roundtrip(self):
        r = PractitionerRole()
        r.service_type_duration = "test-value"
        result = r.service_type_duration
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_schedule_service_type_duration_roundtrip(self):
        r = Schedule()
        r.service_type_duration = "test-value"
        result = r.service_type_duration
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_schedule_schedule_availability_time_roundtrip(self):
        r = Schedule()
        r.schedule_availability_time = "test-value"
        result = r.schedule_availability_time
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_slot_slot_date_roundtrip(self):
        r = Slot()
        r.slot_date = "test-value"
        result = r.slot_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

