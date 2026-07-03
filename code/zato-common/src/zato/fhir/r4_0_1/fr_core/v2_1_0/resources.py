from __future__ import annotations

from typing import Any

from zato.fhir.r4_0_1 import resources as base
from zato.fhir.extensions import get_extension, set_extension
from zato.fhir.r4_0_1.fr_core.v2_1_0.extensions import (
    ADDRESS_INSEE_CODE_URL,
    APPOINTMENT_OPERATOR_URL,
    CONTACT_POINT_EMAIL_TYPE_URL,
    ESTIMATED_DISCHARGE_DATE_URL,
    SERVICE_TYPE_DURATION_URL,
    HUMAN_NAME_ASSEMBLY_ORDER_URL,
    USE_PERIOD_URL,
    OBSERVATION_HEIGHT_BODY_POSITION_URL,
    OBSERVATION_BODY_POSITION_EXT_URL,
    OBSERVATION_LEVEL_OF_EXERTION_URL,
    ORGANIZATION_PRESTATION_DISCIPLINE_URL,
    ORGANIZATION_DESCRIPTION_URL,
    ORGANIZATION_EXTERNAL_URL,
    ORGANIZATION_ACTIVITY_TYPE_URL,
    ORGANIZATION_APPLICANT_ACT_URL,
    ORGANIZATION_FIELD_URL,
    ORGANIZATION_ACTIVITY_FIELD_URL,
    ORGANIZATION_NUMBER_OF_THEORICAL_ACCOMADATION_SPACE_URL,
    ORGANIZATION_ANALYSIS_SECTION_URL,
    ORGANIZATION_EXECUTANT_URL,
    ORGANIZATION_SHORT_NAME_URL,
    ORGANIZATION_BUDGET_LETTER_URL,
    PATIENT_NATIONALITY_URL,
    IDENTITY_RELIABILITY_URL,
    PATIENT_DEATH_PLACE_URL,
    LUNAR_DATE_URL,
    PATIENT_BIRTHDATE_UPDATE_INDICATOR_URL,
    PRACTITIONER_PROFESSION_URL,
    PRACTITIONER_SPECIALTY_URL,
    SCHEDULE_AVAILABILITY_TIME_URL,
    SLOT_DATE_URL,
)

class Address(base.Address):

    @property
    def address_insee_code(self) -> Any:
        return get_extension(self, ADDRESS_INSEE_CODE_URL)

    @address_insee_code.setter
    def address_insee_code(self, value: Any) -> None:
        set_extension(self, ADDRESS_INSEE_CODE_URL, value)

class Appointment(base.Appointment):

    @property
    def appointment_operator(self) -> Any:
        return get_extension(self, APPOINTMENT_OPERATOR_URL)

    @appointment_operator.setter
    def appointment_operator(self, value: Any) -> None:
        set_extension(self, APPOINTMENT_OPERATOR_URL, value)

class ContactPoint(base.ContactPoint):

    @property
    def contact_point_email_type(self) -> Any:
        return get_extension(self, CONTACT_POINT_EMAIL_TYPE_URL)

    @contact_point_email_type.setter
    def contact_point_email_type(self, value: Any) -> None:
        set_extension(self, CONTACT_POINT_EMAIL_TYPE_URL, value)

class Encounter(base.Encounter):

    @property
    def estimated_discharge_date(self) -> Any:
        return get_extension(self, ESTIMATED_DISCHARGE_DATE_URL)

    @estimated_discharge_date.setter
    def estimated_discharge_date(self, value: Any) -> None:
        set_extension(self, ESTIMATED_DISCHARGE_DATE_URL, value)

class HealthcareService(base.HealthcareService):

    @property
    def service_type_duration(self) -> Any:
        return get_extension(self, SERVICE_TYPE_DURATION_URL)

    @service_type_duration.setter
    def service_type_duration(self, value: Any) -> None:
        set_extension(self, SERVICE_TYPE_DURATION_URL, value)

class HumanName(base.HumanName):

    @property
    def human_name_assembly_order(self) -> Any:
        return get_extension(self, HUMAN_NAME_ASSEMBLY_ORDER_URL)

    @human_name_assembly_order.setter
    def human_name_assembly_order(self, value: Any) -> None:
        set_extension(self, HUMAN_NAME_ASSEMBLY_ORDER_URL, value)

class Location(base.Location):

    @property
    def use_period(self) -> Any:
        return get_extension(self, USE_PERIOD_URL)

    @use_period.setter
    def use_period(self, value: Any) -> None:
        set_extension(self, USE_PERIOD_URL, value)

class Observation(base.Observation):

    @property
    def observation_height_body_position(self) -> Any:
        return get_extension(self, OBSERVATION_HEIGHT_BODY_POSITION_URL)

    @observation_height_body_position.setter
    def observation_height_body_position(self, value: Any) -> None:
        set_extension(self, OBSERVATION_HEIGHT_BODY_POSITION_URL, value)

    @property
    def observation_body_position_ext(self) -> Any:
        return get_extension(self, OBSERVATION_BODY_POSITION_EXT_URL)

    @observation_body_position_ext.setter
    def observation_body_position_ext(self, value: Any) -> None:
        set_extension(self, OBSERVATION_BODY_POSITION_EXT_URL, value)

    @property
    def observation_level_of_exertion(self) -> Any:
        return get_extension(self, OBSERVATION_LEVEL_OF_EXERTION_URL)

    @observation_level_of_exertion.setter
    def observation_level_of_exertion(self, value: Any) -> None:
        set_extension(self, OBSERVATION_LEVEL_OF_EXERTION_URL, value)

class Organization(base.Organization):

    @property
    def organization_prestation_discipline(self) -> Any:
        return get_extension(self, ORGANIZATION_PRESTATION_DISCIPLINE_URL)

    @organization_prestation_discipline.setter
    def organization_prestation_discipline(self, value: Any) -> None:
        set_extension(self, ORGANIZATION_PRESTATION_DISCIPLINE_URL, value)

    @property
    def organization_description(self) -> Any:
        return get_extension(self, ORGANIZATION_DESCRIPTION_URL)

    @organization_description.setter
    def organization_description(self, value: Any) -> None:
        set_extension(self, ORGANIZATION_DESCRIPTION_URL, value)

    @property
    def organization_external(self) -> Any:
        return get_extension(self, ORGANIZATION_EXTERNAL_URL)

    @organization_external.setter
    def organization_external(self, value: Any) -> None:
        set_extension(self, ORGANIZATION_EXTERNAL_URL, value)

    @property
    def organization_activity_type(self) -> Any:
        return get_extension(self, ORGANIZATION_ACTIVITY_TYPE_URL)

    @organization_activity_type.setter
    def organization_activity_type(self, value: Any) -> None:
        set_extension(self, ORGANIZATION_ACTIVITY_TYPE_URL, value)

    @property
    def organization_applicant_act(self) -> Any:
        return get_extension(self, ORGANIZATION_APPLICANT_ACT_URL)

    @organization_applicant_act.setter
    def organization_applicant_act(self, value: Any) -> None:
        set_extension(self, ORGANIZATION_APPLICANT_ACT_URL, value)

    @property
    def organization_field(self) -> Any:
        return get_extension(self, ORGANIZATION_FIELD_URL)

    @organization_field.setter
    def organization_field(self, value: Any) -> None:
        set_extension(self, ORGANIZATION_FIELD_URL, value)

    @property
    def organization_activity_field(self) -> Any:
        return get_extension(self, ORGANIZATION_ACTIVITY_FIELD_URL)

    @organization_activity_field.setter
    def organization_activity_field(self, value: Any) -> None:
        set_extension(self, ORGANIZATION_ACTIVITY_FIELD_URL, value)

    @property
    def organization_number_of_theorical_accomadation_space(self) -> Any:
        return get_extension(self, ORGANIZATION_NUMBER_OF_THEORICAL_ACCOMADATION_SPACE_URL)

    @organization_number_of_theorical_accomadation_space.setter
    def organization_number_of_theorical_accomadation_space(self, value: Any) -> None:
        set_extension(self, ORGANIZATION_NUMBER_OF_THEORICAL_ACCOMADATION_SPACE_URL, value)

    @property
    def organization_analysis_section(self) -> Any:
        return get_extension(self, ORGANIZATION_ANALYSIS_SECTION_URL)

    @organization_analysis_section.setter
    def organization_analysis_section(self, value: Any) -> None:
        set_extension(self, ORGANIZATION_ANALYSIS_SECTION_URL, value)

    @property
    def organization_executant(self) -> Any:
        return get_extension(self, ORGANIZATION_EXECUTANT_URL)

    @organization_executant.setter
    def organization_executant(self, value: Any) -> None:
        set_extension(self, ORGANIZATION_EXECUTANT_URL, value)

    @property
    def organization_short_name(self) -> Any:
        return get_extension(self, ORGANIZATION_SHORT_NAME_URL)

    @organization_short_name.setter
    def organization_short_name(self, value: Any) -> None:
        set_extension(self, ORGANIZATION_SHORT_NAME_URL, value)

    @property
    def organization_budget_letter(self) -> Any:
        return get_extension(self, ORGANIZATION_BUDGET_LETTER_URL)

    @organization_budget_letter.setter
    def organization_budget_letter(self, value: Any) -> None:
        set_extension(self, ORGANIZATION_BUDGET_LETTER_URL, value)

class Patient(base.Patient):

    @property
    def patient_nationality(self) -> Any:
        return get_extension(self, PATIENT_NATIONALITY_URL)

    @patient_nationality.setter
    def patient_nationality(self, value: Any) -> None:
        set_extension(self, PATIENT_NATIONALITY_URL, value)

    @property
    def identity_reliability(self) -> Any:
        return get_extension(self, IDENTITY_RELIABILITY_URL)

    @identity_reliability.setter
    def identity_reliability(self, value: Any) -> None:
        set_extension(self, IDENTITY_RELIABILITY_URL, value)

    @property
    def patient_death_place(self) -> Any:
        return get_extension(self, PATIENT_DEATH_PLACE_URL)

    @patient_death_place.setter
    def patient_death_place(self, value: Any) -> None:
        set_extension(self, PATIENT_DEATH_PLACE_URL, value)

    @property
    def lunar_date(self) -> Any:
        return get_extension(self, LUNAR_DATE_URL)

    @lunar_date.setter
    def lunar_date(self, value: Any) -> None:
        set_extension(self, LUNAR_DATE_URL, value)

    @property
    def patient_birthdate_update_indicator(self) -> Any:
        return get_extension(self, PATIENT_BIRTHDATE_UPDATE_INDICATOR_URL)

    @patient_birthdate_update_indicator.setter
    def patient_birthdate_update_indicator(self, value: Any) -> None:
        set_extension(self, PATIENT_BIRTHDATE_UPDATE_INDICATOR_URL, value)

class Practitioner(base.Practitioner):

    @property
    def practitioner_profession(self) -> Any:
        return get_extension(self, PRACTITIONER_PROFESSION_URL)

    @practitioner_profession.setter
    def practitioner_profession(self, value: Any) -> None:
        set_extension(self, PRACTITIONER_PROFESSION_URL, value)

    @property
    def practitioner_specialty(self) -> Any:
        return get_extension(self, PRACTITIONER_SPECIALTY_URL)

    @practitioner_specialty.setter
    def practitioner_specialty(self, value: Any) -> None:
        set_extension(self, PRACTITIONER_SPECIALTY_URL, value)

class PractitionerRole(base.PractitionerRole):

    @property
    def service_type_duration(self) -> Any:
        return get_extension(self, SERVICE_TYPE_DURATION_URL)

    @service_type_duration.setter
    def service_type_duration(self, value: Any) -> None:
        set_extension(self, SERVICE_TYPE_DURATION_URL, value)

class Schedule(base.Schedule):

    @property
    def service_type_duration(self) -> Any:
        return get_extension(self, SERVICE_TYPE_DURATION_URL)

    @service_type_duration.setter
    def service_type_duration(self, value: Any) -> None:
        set_extension(self, SERVICE_TYPE_DURATION_URL, value)

    @property
    def schedule_availability_time(self) -> Any:
        return get_extension(self, SCHEDULE_AVAILABILITY_TIME_URL)

    @schedule_availability_time.setter
    def schedule_availability_time(self, value: Any) -> None:
        set_extension(self, SCHEDULE_AVAILABILITY_TIME_URL, value)

class Slot(base.Slot):

    @property
    def slot_date(self) -> Any:
        return get_extension(self, SLOT_DATE_URL)

    @slot_date.setter
    def slot_date(self, value: Any) -> None:
        set_extension(self, SLOT_DATE_URL, value)
