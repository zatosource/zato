from __future__ import annotations

from typing import Any

from zato.fhir.r4_0_1 import resources as base
from zato.fhir.extensions import get_extension, set_extension
from zato.fhir.r4_0_1.kbv.v1_5_0.extensions import (
    ALLERGY_INTOLERANCE_ABATEMENT_URL,
    STAGE_LIFE_URL,
    ADDITIONAL_COMMENT_URL,
    RESPONSIBLE_PERSON_ORGANIZATION_URL,
    TREATMENT_GOAL_END_URL,
    MEDICATION_TYPE_URL,
    GOAL_MEDICATION_TARGET_REFERENCE_URL,
)

class AllergyIntolerance(base.AllergyIntolerance):

    @property
    def allergy_intolerance_abatement(self) -> Any:
        return get_extension(self, ALLERGY_INTOLERANCE_ABATEMENT_URL)

    @allergy_intolerance_abatement.setter
    def allergy_intolerance_abatement(self, value: Any) -> None:
        set_extension(self, ALLERGY_INTOLERANCE_ABATEMENT_URL, value)

    @property
    def stage_life(self) -> Any:
        return get_extension(self, STAGE_LIFE_URL)

    @stage_life.setter
    def stage_life(self, value: Any) -> None:
        set_extension(self, STAGE_LIFE_URL, value)

class Composition(base.Composition):

    @property
    def additional_comment(self) -> Any:
        return get_extension(self, ADDITIONAL_COMMENT_URL)

    @additional_comment.setter
    def additional_comment(self, value: Any) -> None:
        set_extension(self, ADDITIONAL_COMMENT_URL, value)

class Condition(base.Condition):

    @property
    def additional_comment(self) -> Any:
        return get_extension(self, ADDITIONAL_COMMENT_URL)

    @additional_comment.setter
    def additional_comment(self, value: Any) -> None:
        set_extension(self, ADDITIONAL_COMMENT_URL, value)

class DateTime(base.DateTime):

    @property
    def stage_life(self) -> Any:
        return get_extension(self, STAGE_LIFE_URL)

    @stage_life.setter
    def stage_life(self, value: Any) -> None:
        set_extension(self, STAGE_LIFE_URL, value)

class Device(base.Device):

    @property
    def responsible_person_organization(self) -> Any:
        return get_extension(self, RESPONSIBLE_PERSON_ORGANIZATION_URL)

    @responsible_person_organization.setter
    def responsible_person_organization(self, value: Any) -> None:
        set_extension(self, RESPONSIBLE_PERSON_ORGANIZATION_URL, value)

class DiagnosticReport(base.DiagnosticReport):

    @property
    def additional_comment(self) -> Any:
        return get_extension(self, ADDITIONAL_COMMENT_URL)

    @additional_comment.setter
    def additional_comment(self, value: Any) -> None:
        set_extension(self, ADDITIONAL_COMMENT_URL, value)

class Element(base.Element):

    @property
    def additional_comment(self) -> Any:
        return get_extension(self, ADDITIONAL_COMMENT_URL)

    @additional_comment.setter
    def additional_comment(self, value: Any) -> None:
        set_extension(self, ADDITIONAL_COMMENT_URL, value)

class Encounter(base.Encounter):

    @property
    def additional_comment(self) -> Any:
        return get_extension(self, ADDITIONAL_COMMENT_URL)

    @additional_comment.setter
    def additional_comment(self, value: Any) -> None:
        set_extension(self, ADDITIONAL_COMMENT_URL, value)

class Goal(base.Goal):

    @property
    def treatment_goal_end(self) -> Any:
        return get_extension(self, TREATMENT_GOAL_END_URL)

    @treatment_goal_end.setter
    def treatment_goal_end(self, value: Any) -> None:
        set_extension(self, TREATMENT_GOAL_END_URL, value)

class Medication(base.Medication):

    @property
    def medication_type(self) -> Any:
        return get_extension(self, MEDICATION_TYPE_URL)

    @medication_type.setter
    def medication_type(self, value: Any) -> None:
        set_extension(self, MEDICATION_TYPE_URL, value)

class MedicationStatement(base.MedicationStatement):

    @property
    def additional_comment(self) -> Any:
        return get_extension(self, ADDITIONAL_COMMENT_URL)

    @additional_comment.setter
    def additional_comment(self, value: Any) -> None:
        set_extension(self, ADDITIONAL_COMMENT_URL, value)

    @property
    def goal_medication_target_reference(self) -> Any:
        return get_extension(self, GOAL_MEDICATION_TARGET_REFERENCE_URL)

    @goal_medication_target_reference.setter
    def goal_medication_target_reference(self, value: Any) -> None:
        set_extension(self, GOAL_MEDICATION_TARGET_REFERENCE_URL, value)

class Observation(base.Observation):

    @property
    def additional_comment(self) -> Any:
        return get_extension(self, ADDITIONAL_COMMENT_URL)

    @additional_comment.setter
    def additional_comment(self, value: Any) -> None:
        set_extension(self, ADDITIONAL_COMMENT_URL, value)

class Organization(base.Organization):

    @property
    def additional_comment(self) -> Any:
        return get_extension(self, ADDITIONAL_COMMENT_URL)

    @additional_comment.setter
    def additional_comment(self, value: Any) -> None:
        set_extension(self, ADDITIONAL_COMMENT_URL, value)

class Patient(base.Patient):

    @property
    def additional_comment(self) -> Any:
        return get_extension(self, ADDITIONAL_COMMENT_URL)

    @additional_comment.setter
    def additional_comment(self, value: Any) -> None:
        set_extension(self, ADDITIONAL_COMMENT_URL, value)

class Person(base.Person):

    @property
    def additional_comment(self) -> Any:
        return get_extension(self, ADDITIONAL_COMMENT_URL)

    @additional_comment.setter
    def additional_comment(self, value: Any) -> None:
        set_extension(self, ADDITIONAL_COMMENT_URL, value)

class Practitioner(base.Practitioner):

    @property
    def additional_comment(self) -> Any:
        return get_extension(self, ADDITIONAL_COMMENT_URL)

    @additional_comment.setter
    def additional_comment(self, value: Any) -> None:
        set_extension(self, ADDITIONAL_COMMENT_URL, value)

class RelatedPerson(base.RelatedPerson):

    @property
    def additional_comment(self) -> Any:
        return get_extension(self, ADDITIONAL_COMMENT_URL)

    @additional_comment.setter
    def additional_comment(self, value: Any) -> None:
        set_extension(self, ADDITIONAL_COMMENT_URL, value)
