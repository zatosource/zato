from __future__ import annotations

from typing import Any

from zato.fhir.r4_0_1 import resources as base
from zato.fhir.extensions import get_extension, set_extension
from zato.fhir.r4_0_1.davinci_formulary.v2_1_0.extensions import (
    AVAILABILITY_STATUS_EXTENSION_URL,
    QUANTITY_LIMIT_EXTENSION_URL,
    PHARMACY_BENEFIT_TYPE_EXTENSION_URL,
    PRIOR_AUTHORIZATION_EXTENSION_URL,
    QUANTITY_LIMIT_DETAIL_EXTENSION_URL,
    PRIOR_AUTHORIZATION_NEW_STARTS_ONLY_EXTENSION_URL,
    FORMULARY_REFERENCE_EXTENSION_URL,
    DRUG_TIER_ID_EXTENSION_URL,
    ADDITIONAL_COVERAGE_INFORMATION_EXTENSION_URL,
    STEP_THERAPY_LIMIT_NEW_STARTS_ONLY_EXTENSION_URL,
    STEP_THERAPY_LIMIT_EXTENSION_URL,
    AVAILABILITY_PERIOD_EXTENSION_URL,
)

class Basic(base.Basic):

    @property
    def availability_status_extension(self) -> Any:
        return get_extension(self, AVAILABILITY_STATUS_EXTENSION_URL)

    @availability_status_extension.setter
    def availability_status_extension(self, value: Any) -> None:
        set_extension(self, AVAILABILITY_STATUS_EXTENSION_URL, value)

    @property
    def quantity_limit_extension(self) -> Any:
        return get_extension(self, QUANTITY_LIMIT_EXTENSION_URL)

    @quantity_limit_extension.setter
    def quantity_limit_extension(self, value: Any) -> None:
        set_extension(self, QUANTITY_LIMIT_EXTENSION_URL, value)

    @property
    def pharmacy_benefit_type_extension(self) -> Any:
        return get_extension(self, PHARMACY_BENEFIT_TYPE_EXTENSION_URL)

    @pharmacy_benefit_type_extension.setter
    def pharmacy_benefit_type_extension(self, value: Any) -> None:
        set_extension(self, PHARMACY_BENEFIT_TYPE_EXTENSION_URL, value)

    @property
    def prior_authorization_extension(self) -> Any:
        return get_extension(self, PRIOR_AUTHORIZATION_EXTENSION_URL)

    @prior_authorization_extension.setter
    def prior_authorization_extension(self, value: Any) -> None:
        set_extension(self, PRIOR_AUTHORIZATION_EXTENSION_URL, value)

    @property
    def quantity_limit_detail_extension(self) -> Any:
        return get_extension(self, QUANTITY_LIMIT_DETAIL_EXTENSION_URL)

    @quantity_limit_detail_extension.setter
    def quantity_limit_detail_extension(self, value: Any) -> None:
        set_extension(self, QUANTITY_LIMIT_DETAIL_EXTENSION_URL, value)

    @property
    def prior_authorization_new_starts_only_extension(self) -> Any:
        return get_extension(self, PRIOR_AUTHORIZATION_NEW_STARTS_ONLY_EXTENSION_URL)

    @prior_authorization_new_starts_only_extension.setter
    def prior_authorization_new_starts_only_extension(self, value: Any) -> None:
        set_extension(self, PRIOR_AUTHORIZATION_NEW_STARTS_ONLY_EXTENSION_URL, value)

    @property
    def formulary_reference_extension(self) -> Any:
        return get_extension(self, FORMULARY_REFERENCE_EXTENSION_URL)

    @formulary_reference_extension.setter
    def formulary_reference_extension(self, value: Any) -> None:
        set_extension(self, FORMULARY_REFERENCE_EXTENSION_URL, value)

    @property
    def drug_tier_id_extension(self) -> Any:
        return get_extension(self, DRUG_TIER_ID_EXTENSION_URL)

    @drug_tier_id_extension.setter
    def drug_tier_id_extension(self, value: Any) -> None:
        set_extension(self, DRUG_TIER_ID_EXTENSION_URL, value)

    @property
    def additional_coverage_information_extension(self) -> Any:
        return get_extension(self, ADDITIONAL_COVERAGE_INFORMATION_EXTENSION_URL)

    @additional_coverage_information_extension.setter
    def additional_coverage_information_extension(self, value: Any) -> None:
        set_extension(self, ADDITIONAL_COVERAGE_INFORMATION_EXTENSION_URL, value)

    @property
    def step_therapy_limit_new_starts_only_extension(self) -> Any:
        return get_extension(self, STEP_THERAPY_LIMIT_NEW_STARTS_ONLY_EXTENSION_URL)

    @step_therapy_limit_new_starts_only_extension.setter
    def step_therapy_limit_new_starts_only_extension(self, value: Any) -> None:
        set_extension(self, STEP_THERAPY_LIMIT_NEW_STARTS_ONLY_EXTENSION_URL, value)

    @property
    def step_therapy_limit_extension(self) -> Any:
        return get_extension(self, STEP_THERAPY_LIMIT_EXTENSION_URL)

    @step_therapy_limit_extension.setter
    def step_therapy_limit_extension(self, value: Any) -> None:
        set_extension(self, STEP_THERAPY_LIMIT_EXTENSION_URL, value)

    @property
    def availability_period_extension(self) -> Any:
        return get_extension(self, AVAILABILITY_PERIOD_EXTENSION_URL)

    @availability_period_extension.setter
    def availability_period_extension(self, value: Any) -> None:
        set_extension(self, AVAILABILITY_PERIOD_EXTENSION_URL, value)

class InsurancePlan(base.InsurancePlan):

    @property
    def formulary_reference_extension(self) -> Any:
        return get_extension(self, FORMULARY_REFERENCE_EXTENSION_URL)

    @formulary_reference_extension.setter
    def formulary_reference_extension(self, value: Any) -> None:
        set_extension(self, FORMULARY_REFERENCE_EXTENSION_URL, value)
