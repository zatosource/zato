from __future__ import annotations

from typing import Any

from zato.fhir.r4_0_1 import resources as base
from zato.fhir.extensions import get_extension, get_extension_text, set_extension, set_extension_text
from zato.fhir.r4_0_1.us_core.v8_0_0.extensions import (
    JURISDICTION_URL,
    DIRECT_URL,
    AUTHENTICATION_TIME_URL,
    USCDI_REQUIREMENT_URL,
    INTERPRETER_NEEDED_URL,
    ETHNICITY_URL,
    RACE_URL,
    TRIBAL_AFFILIATION_URL,
    MEDICATION_ADHERENCE_URL,
    SEX_URL,
    BIRTHSEX_URL,
    GENDER_IDENTITY_URL,
    QUESTIONNAIRE_URI_URL,
)

class BiologicallyDerivedProduct(base.BiologicallyDerivedProduct):

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

class BodyStructure(base.BodyStructure):

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

class Claim(base.Claim):

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

class Consent(base.Consent):

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

class ContactPoint(base.ContactPoint):

    @property
    def direct(self) -> Any:
        return get_extension(self, DIRECT_URL)

    @direct.setter
    def direct(self, value: Any) -> None:
        set_extension(self, DIRECT_URL, value)

class Contract(base.Contract):

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

class Coverage(base.Coverage):

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

class Device(base.Device):

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

class DeviceMetric(base.DeviceMetric):

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

class DocumentReference(base.DocumentReference):

    @property
    def authentication_time(self) -> Any:
        return get_extension(self, AUTHENTICATION_TIME_URL)

    @authentication_time.setter
    def authentication_time(self, value: Any) -> None:
        set_extension(self, AUTHENTICATION_TIME_URL, value)

class ElementDefinition(base.ElementDefinition):

    @property
    def uscdi_requirement(self) -> Any:
        return get_extension(self, USCDI_REQUIREMENT_URL)

    @uscdi_requirement.setter
    def uscdi_requirement(self, value: Any) -> None:
        set_extension(self, USCDI_REQUIREMENT_URL, value)

class Encounter(base.Encounter):

    @property
    def interpreter_needed(self) -> Any:
        return get_extension(self, INTERPRETER_NEEDED_URL)

    @interpreter_needed.setter
    def interpreter_needed(self, value: Any) -> None:
        set_extension(self, INTERPRETER_NEEDED_URL, value)

class Endpoint(base.Endpoint):

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

class ExplanationOfBenefit(base.ExplanationOfBenefit):

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

class FamilyMemberHistory(base.FamilyMemberHistory):

    @property
    def ethnicity(self) -> Any:
        return get_extension_text(self, ETHNICITY_URL)

    @ethnicity.setter
    def ethnicity(self, value: Any) -> None:
        set_extension_text(self, ETHNICITY_URL, value)

    @property
    def race(self) -> Any:
        return get_extension_text(self, RACE_URL)

    @race.setter
    def race(self, value: Any) -> None:
        set_extension_text(self, RACE_URL, value)

    @property
    def tribal_affiliation(self) -> Any:
        return get_extension(self, TRIBAL_AFFILIATION_URL)

    @tribal_affiliation.setter
    def tribal_affiliation(self, value: Any) -> None:
        set_extension(self, TRIBAL_AFFILIATION_URL, value)

class Group(base.Group):

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

class HealthcareService(base.HealthcareService):

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

class InsurancePlan(base.InsurancePlan):

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

class Invoice(base.Invoice):

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

class Location(base.Location):

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

class MedicationRequest(base.MedicationRequest):

    @property
    def medication_adherence(self) -> Any:
        return get_extension(self, MEDICATION_ADHERENCE_URL)

    @medication_adherence.setter
    def medication_adherence(self, value: Any) -> None:
        set_extension(self, MEDICATION_ADHERENCE_URL, value)

class Organization(base.Organization):

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

class OrganizationAffiliation(base.OrganizationAffiliation):

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

class Patient(base.Patient):

    @property
    def ethnicity(self) -> Any:
        return get_extension_text(self, ETHNICITY_URL)

    @ethnicity.setter
    def ethnicity(self, value: Any) -> None:
        set_extension_text(self, ETHNICITY_URL, value)

    @property
    def sex(self) -> Any:
        return get_extension(self, SEX_URL)

    @sex.setter
    def sex(self, value: Any) -> None:
        set_extension(self, SEX_URL, value)

    @property
    def race(self) -> Any:
        return get_extension_text(self, RACE_URL)

    @race.setter
    def race(self, value: Any) -> None:
        set_extension_text(self, RACE_URL, value)

    @property
    def birthsex(self) -> Any:
        return get_extension(self, BIRTHSEX_URL)

    @birthsex.setter
    def birthsex(self, value: Any) -> None:
        set_extension(self, BIRTHSEX_URL, value)

    @property
    def gender_identity(self) -> Any:
        return get_extension(self, GENDER_IDENTITY_URL)

    @gender_identity.setter
    def gender_identity(self, value: Any) -> None:
        set_extension(self, GENDER_IDENTITY_URL, value)

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

    @property
    def tribal_affiliation(self) -> Any:
        return get_extension(self, TRIBAL_AFFILIATION_URL)

    @tribal_affiliation.setter
    def tribal_affiliation(self, value: Any) -> None:
        set_extension(self, TRIBAL_AFFILIATION_URL, value)

    @property
    def interpreter_needed(self) -> Any:
        return get_extension(self, INTERPRETER_NEEDED_URL)

    @interpreter_needed.setter
    def interpreter_needed(self, value: Any) -> None:
        set_extension(self, INTERPRETER_NEEDED_URL, value)

class Person(base.Person):

    @property
    def ethnicity(self) -> Any:
        return get_extension_text(self, ETHNICITY_URL)

    @ethnicity.setter
    def ethnicity(self, value: Any) -> None:
        set_extension_text(self, ETHNICITY_URL, value)

    @property
    def race(self) -> Any:
        return get_extension_text(self, RACE_URL)

    @race.setter
    def race(self, value: Any) -> None:
        set_extension_text(self, RACE_URL, value)

    @property
    def gender_identity(self) -> Any:
        return get_extension(self, GENDER_IDENTITY_URL)

    @gender_identity.setter
    def gender_identity(self, value: Any) -> None:
        set_extension(self, GENDER_IDENTITY_URL, value)

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

    @property
    def tribal_affiliation(self) -> Any:
        return get_extension(self, TRIBAL_AFFILIATION_URL)

    @tribal_affiliation.setter
    def tribal_affiliation(self, value: Any) -> None:
        set_extension(self, TRIBAL_AFFILIATION_URL, value)

class Practitioner(base.Practitioner):

    @property
    def ethnicity(self) -> Any:
        return get_extension_text(self, ETHNICITY_URL)

    @ethnicity.setter
    def ethnicity(self, value: Any) -> None:
        set_extension_text(self, ETHNICITY_URL, value)

    @property
    def race(self) -> Any:
        return get_extension_text(self, RACE_URL)

    @race.setter
    def race(self, value: Any) -> None:
        set_extension_text(self, RACE_URL, value)

    @property
    def gender_identity(self) -> Any:
        return get_extension(self, GENDER_IDENTITY_URL)

    @gender_identity.setter
    def gender_identity(self, value: Any) -> None:
        set_extension(self, GENDER_IDENTITY_URL, value)

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

    @property
    def tribal_affiliation(self) -> Any:
        return get_extension(self, TRIBAL_AFFILIATION_URL)

    @tribal_affiliation.setter
    def tribal_affiliation(self, value: Any) -> None:
        set_extension(self, TRIBAL_AFFILIATION_URL, value)

    @property
    def interpreter_needed(self) -> Any:
        return get_extension(self, INTERPRETER_NEEDED_URL)

    @interpreter_needed.setter
    def interpreter_needed(self, value: Any) -> None:
        set_extension(self, INTERPRETER_NEEDED_URL, value)

class PractitionerRole(base.PractitionerRole):

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

class QuestionnaireResponse(base.QuestionnaireResponse):

    @property
    def questionnaire_uri(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_URI_URL)

    @questionnaire_uri.setter
    def questionnaire_uri(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_URI_URL, value)

class RelatedPerson(base.RelatedPerson):

    @property
    def ethnicity(self) -> Any:
        return get_extension_text(self, ETHNICITY_URL)

    @ethnicity.setter
    def ethnicity(self, value: Any) -> None:
        set_extension_text(self, ETHNICITY_URL, value)

    @property
    def race(self) -> Any:
        return get_extension_text(self, RACE_URL)

    @race.setter
    def race(self, value: Any) -> None:
        set_extension_text(self, RACE_URL, value)

    @property
    def gender_identity(self) -> Any:
        return get_extension(self, GENDER_IDENTITY_URL)

    @gender_identity.setter
    def gender_identity(self, value: Any) -> None:
        set_extension(self, GENDER_IDENTITY_URL, value)

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

    @property
    def tribal_affiliation(self) -> Any:
        return get_extension(self, TRIBAL_AFFILIATION_URL)

    @tribal_affiliation.setter
    def tribal_affiliation(self, value: Any) -> None:
        set_extension(self, TRIBAL_AFFILIATION_URL, value)

    @property
    def interpreter_needed(self) -> Any:
        return get_extension(self, INTERPRETER_NEEDED_URL)

    @interpreter_needed.setter
    def interpreter_needed(self, value: Any) -> None:
        set_extension(self, INTERPRETER_NEEDED_URL, value)

class Specimen(base.Specimen):

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)

class Substance(base.Substance):

    @property
    def jurisdiction(self) -> Any:
        return get_extension(self, JURISDICTION_URL)

    @jurisdiction.setter
    def jurisdiction(self, value: Any) -> None:
        set_extension(self, JURISDICTION_URL, value)
