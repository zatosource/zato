from __future__ import annotations

from typing import Any

from zato.fhir.r4_0_1 import resources as base
from zato.fhir.extensions import get_extension, set_extension
from zato.fhir.r4_0_1.dk_core.v3_5_0.extensions import (
    DK_CORE_MUNICIPALITY_CODES_URL,
    DK_CORE_REGIONAL_SUB_DIVISION_CODES_URL,
    CONDITION_LAST_ASSERTED_DATE_URL,
    NOT_FOLLOWED_ANYMORE_URL,
    DK_CORE_DOCUMENTREFERENCE_VERSION_ID_EXTENSION_URL,
    DK_CORE_PLANNED_END_DATE_URL,
    DK_CORE_PLANNED_START_DATE_URL,
    DK_CORE_CARE_PROVIDER_URL,
)

class Address(base.Address):

    @property
    def dk_core_municipality_codes(self) -> Any:
        return get_extension(self, DK_CORE_MUNICIPALITY_CODES_URL)

    @dk_core_municipality_codes.setter
    def dk_core_municipality_codes(self, value: Any) -> None:
        set_extension(self, DK_CORE_MUNICIPALITY_CODES_URL, value)

    @property
    def dk_core_regional_sub_division_codes(self) -> Any:
        return get_extension(self, DK_CORE_REGIONAL_SUB_DIVISION_CODES_URL)

    @dk_core_regional_sub_division_codes.setter
    def dk_core_regional_sub_division_codes(self, value: Any) -> None:
        set_extension(self, DK_CORE_REGIONAL_SUB_DIVISION_CODES_URL, value)

class Condition(base.Condition):

    @property
    def condition_last_asserted_date(self) -> Any:
        return get_extension(self, CONDITION_LAST_ASSERTED_DATE_URL)

    @condition_last_asserted_date.setter
    def condition_last_asserted_date(self, value: Any) -> None:
        set_extension(self, CONDITION_LAST_ASSERTED_DATE_URL, value)

    @property
    def not_followed_anymore(self) -> Any:
        return get_extension(self, NOT_FOLLOWED_ANYMORE_URL)

    @not_followed_anymore.setter
    def not_followed_anymore(self, value: Any) -> None:
        set_extension(self, NOT_FOLLOWED_ANYMORE_URL, value)

class Element(base.Element):

    @property
    def dk_core_documentreference_version_id_extension(self) -> Any:
        return get_extension(self, DK_CORE_DOCUMENTREFERENCE_VERSION_ID_EXTENSION_URL)

    @dk_core_documentreference_version_id_extension.setter
    def dk_core_documentreference_version_id_extension(self, value: Any) -> None:
        set_extension(self, DK_CORE_DOCUMENTREFERENCE_VERSION_ID_EXTENSION_URL, value)

class Encounter(base.Encounter):

    @property
    def dk_core_planned_end_date(self) -> Any:
        return get_extension(self, DK_CORE_PLANNED_END_DATE_URL)

    @dk_core_planned_end_date.setter
    def dk_core_planned_end_date(self, value: Any) -> None:
        set_extension(self, DK_CORE_PLANNED_END_DATE_URL, value)

    @property
    def dk_core_planned_start_date(self) -> Any:
        return get_extension(self, DK_CORE_PLANNED_START_DATE_URL)

    @dk_core_planned_start_date.setter
    def dk_core_planned_start_date(self, value: Any) -> None:
        set_extension(self, DK_CORE_PLANNED_START_DATE_URL, value)

    @property
    def dk_core_care_provider(self) -> Any:
        return get_extension(self, DK_CORE_CARE_PROVIDER_URL)

    @dk_core_care_provider.setter
    def dk_core_care_provider(self, value: Any) -> None:
        set_extension(self, DK_CORE_CARE_PROVIDER_URL, value)

class Patient(base.Patient):

    @property
    def dk_core_municipality_codes(self) -> Any:
        return get_extension(self, DK_CORE_MUNICIPALITY_CODES_URL)

    @dk_core_municipality_codes.setter
    def dk_core_municipality_codes(self, value: Any) -> None:
        set_extension(self, DK_CORE_MUNICIPALITY_CODES_URL, value)

    @property
    def dk_core_regional_sub_division_codes(self) -> Any:
        return get_extension(self, DK_CORE_REGIONAL_SUB_DIVISION_CODES_URL)

    @dk_core_regional_sub_division_codes.setter
    def dk_core_regional_sub_division_codes(self, value: Any) -> None:
        set_extension(self, DK_CORE_REGIONAL_SUB_DIVISION_CODES_URL, value)
