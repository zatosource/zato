from __future__ import annotations

from typing import Any

from zato.fhir.r4_0_1 import resources as base
from zato.fhir.extensions import get_extension, set_extension
from zato.fhir.r4_0_1.davinci_plan_net.v1_2_0.extensions import (
    VIA_INTERMEDIARY_URL,
    CONTACTPOINT_AVAILABLETIME_URL,
    ENDPOINT_USECASE_URL,
    DELIVERY_METHOD_URL,
    NEWPATIENTS_URL,
    ACCESSIBILITY_URL,
    ORG_DESCRIPTION_URL,
    QUALIFICATION_URL,
    LOCATION_REFERENCE_URL,
    COMMUNICATION_PROFICIENCY_URL,
    PRACTITIONER_PERIOD_URL,
    PRACTITIONER_QUALIFICATION_URL,
    NETWORK_REFERENCE_URL,
)

class ContactPoint(base.ContactPoint):

    @property
    def via_intermediary(self) -> Any:
        return get_extension(self, VIA_INTERMEDIARY_URL)

    @via_intermediary.setter
    def via_intermediary(self, value: Any) -> None:
        set_extension(self, VIA_INTERMEDIARY_URL, value)

    @property
    def contactpoint_availabletime(self) -> Any:
        return get_extension(self, CONTACTPOINT_AVAILABLETIME_URL)

    @contactpoint_availabletime.setter
    def contactpoint_availabletime(self, value: Any) -> None:
        set_extension(self, CONTACTPOINT_AVAILABLETIME_URL, value)

class Endpoint(base.Endpoint):

    @property
    def endpoint_usecase(self) -> Any:
        return get_extension(self, ENDPOINT_USECASE_URL)

    @endpoint_usecase.setter
    def endpoint_usecase(self, value: Any) -> None:
        set_extension(self, ENDPOINT_USECASE_URL, value)

class HealthcareService(base.HealthcareService):

    @property
    def delivery_method(self) -> Any:
        return get_extension(self, DELIVERY_METHOD_URL)

    @delivery_method.setter
    def delivery_method(self, value: Any) -> None:
        set_extension(self, DELIVERY_METHOD_URL, value)

    @property
    def newpatients(self) -> Any:
        return get_extension(self, NEWPATIENTS_URL)

    @newpatients.setter
    def newpatients(self, value: Any) -> None:
        set_extension(self, NEWPATIENTS_URL, value)

class Location(base.Location):

    @property
    def accessibility(self) -> Any:
        return get_extension(self, ACCESSIBILITY_URL)

    @accessibility.setter
    def accessibility(self, value: Any) -> None:
        set_extension(self, ACCESSIBILITY_URL, value)

    @property
    def newpatients(self) -> Any:
        return get_extension(self, NEWPATIENTS_URL)

    @newpatients.setter
    def newpatients(self, value: Any) -> None:
        set_extension(self, NEWPATIENTS_URL, value)

class Organization(base.Organization):

    @property
    def org_description(self) -> Any:
        return get_extension(self, ORG_DESCRIPTION_URL)

    @org_description.setter
    def org_description(self, value: Any) -> None:
        set_extension(self, ORG_DESCRIPTION_URL, value)

    @property
    def qualification(self) -> Any:
        return get_extension(self, QUALIFICATION_URL)

    @qualification.setter
    def qualification(self, value: Any) -> None:
        set_extension(self, QUALIFICATION_URL, value)

    @property
    def location_reference(self) -> Any:
        return get_extension(self, LOCATION_REFERENCE_URL)

    @location_reference.setter
    def location_reference(self, value: Any) -> None:
        set_extension(self, LOCATION_REFERENCE_URL, value)

class OrganizationAffiliation(base.OrganizationAffiliation):

    @property
    def qualification(self) -> Any:
        return get_extension(self, QUALIFICATION_URL)

    @qualification.setter
    def qualification(self, value: Any) -> None:
        set_extension(self, QUALIFICATION_URL, value)

class Practitioner(base.Practitioner):

    @property
    def communication_proficiency(self) -> Any:
        return get_extension(self, COMMUNICATION_PROFICIENCY_URL)

    @communication_proficiency.setter
    def communication_proficiency(self, value: Any) -> None:
        set_extension(self, COMMUNICATION_PROFICIENCY_URL, value)

    @property
    def practitioner_period(self) -> Any:
        return get_extension(self, PRACTITIONER_PERIOD_URL)

    @practitioner_period.setter
    def practitioner_period(self, value: Any) -> None:
        set_extension(self, PRACTITIONER_PERIOD_URL, value)

    @property
    def practitioner_qualification(self) -> Any:
        return get_extension(self, PRACTITIONER_QUALIFICATION_URL)

    @practitioner_qualification.setter
    def practitioner_qualification(self, value: Any) -> None:
        set_extension(self, PRACTITIONER_QUALIFICATION_URL, value)

class PractitionerRole(base.PractitionerRole):

    @property
    def network_reference(self) -> Any:
        return get_extension(self, NETWORK_REFERENCE_URL)

    @network_reference.setter
    def network_reference(self, value: Any) -> None:
        set_extension(self, NETWORK_REFERENCE_URL, value)

    @property
    def qualification(self) -> Any:
        return get_extension(self, QUALIFICATION_URL)

    @qualification.setter
    def qualification(self, value: Any) -> None:
        set_extension(self, QUALIFICATION_URL, value)

    @property
    def newpatients(self) -> Any:
        return get_extension(self, NEWPATIENTS_URL)

    @newpatients.setter
    def newpatients(self, value: Any) -> None:
        set_extension(self, NEWPATIENTS_URL, value)
