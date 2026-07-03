from __future__ import annotations

from typing import Any

from zato.fhir.r4_0_1 import resources as base
from zato.fhir.extensions import get_extension, set_extension
from zato.fhir.r4_0_1.davinci_pas.v2_1_0.extensions import (
    REQUESTED_SERVICE_URL,
    SERVICE_ITEM_REQUEST_TYPE_URL,
    COMMUNICATED_DIAGNOSIS_URL,
    ITEM_CERTIFICATION_ISSUE_DATE_URL,
    CARE_TEAM_CLAIM_SCOPE_URL,
    PRODUCT_OR_SERVICE_CODE_END_URL,
    CONDITION_CODE_URL,
    CERTIFICATION_TYPE_URL,
    DIAGNOSIS_RECORDED_DATE_URL,
    AUTHORIZATION_NUMBER_URL,
    INFO_CHANGED_URL,
    ITEM_CERTIFICATION_EXPIRATION_DATE_URL,
    ADMINISTRATION_REFERENCE_NUMBER_URL,
    REVENUE_UNIT_RATE_LIMIT_URL,
    ITEM_CERTIFICATION_EFFECTIVE_DATE_URL,
    REVIEW_ACTION_CODE_URL,
    LEVEL_OF_SERVICE_CODE_URL,
    NURSING_HOME_LEVEL_OF_CARE_URL,
    MODIFIEREXTENSION_INFO_CANCELLED_URL,
    NURSING_HOME_RESIDENTIAL_STATUS_URL,
    EPSDT_INDICATOR_URL,
    ITEM_TRACE_NUMBER_URL,
    HOME_HEALTH_CARE_INFORMATION_URL,
    ITEM_PRE_AUTH_ISSUE_DATE_URL,
    ITEM_AUTHORIZED_DETAIL_URL,
    ITEM_AUTHORIZED_PROVIDER_URL,
    ERROR_FOLLOWUP_ACTION_URL,
    ITEM_REQUESTED_SERVICE_DATE_URL,
    REVIEW_ACTION_URL,
    ERROR_PATH_URL,
    ERROR_ELEMENT_URL,
    ITEM_PRE_AUTH_PERIOD_URL,
    AUTHORIZED_PROVIDER_TYPE_URL,
    REVENUE_CODE_URL,
    SERVICE_LINE_NUMBER_URL,
    CONTENT_MODIFIER_URL,
    TIMINGDELIVERYPATTERN_URL,
    TIMINGCALENDARPATTERN_URL,
    PATIENT_STATUS_URL,
    MILITARY_STATUS_URL,
    IDENTIFIER_SUB_DEPARTMENT_URL,
    IDENTIFIER_JURISDICTION_URL,
    PA_LINE_NUMBER_URL,
)

class Claim(base.Claim):

    @property
    def requested_service(self) -> Any:
        return get_extension(self, REQUESTED_SERVICE_URL)

    @requested_service.setter
    def requested_service(self, value: Any) -> None:
        set_extension(self, REQUESTED_SERVICE_URL, value)

    @property
    def service_item_request_type(self) -> Any:
        return get_extension(self, SERVICE_ITEM_REQUEST_TYPE_URL)

    @service_item_request_type.setter
    def service_item_request_type(self, value: Any) -> None:
        set_extension(self, SERVICE_ITEM_REQUEST_TYPE_URL, value)

    @property
    def communicated_diagnosis(self) -> Any:
        return get_extension(self, COMMUNICATED_DIAGNOSIS_URL)

    @communicated_diagnosis.setter
    def communicated_diagnosis(self, value: Any) -> None:
        set_extension(self, COMMUNICATED_DIAGNOSIS_URL, value)

    @property
    def item_certification_issue_date(self) -> Any:
        return get_extension(self, ITEM_CERTIFICATION_ISSUE_DATE_URL)

    @item_certification_issue_date.setter
    def item_certification_issue_date(self, value: Any) -> None:
        set_extension(self, ITEM_CERTIFICATION_ISSUE_DATE_URL, value)

    @property
    def care_team_claim_scope(self) -> Any:
        return get_extension(self, CARE_TEAM_CLAIM_SCOPE_URL)

    @care_team_claim_scope.setter
    def care_team_claim_scope(self, value: Any) -> None:
        set_extension(self, CARE_TEAM_CLAIM_SCOPE_URL, value)

    @property
    def product_or_service_code_end(self) -> Any:
        return get_extension(self, PRODUCT_OR_SERVICE_CODE_END_URL)

    @product_or_service_code_end.setter
    def product_or_service_code_end(self, value: Any) -> None:
        set_extension(self, PRODUCT_OR_SERVICE_CODE_END_URL, value)

    @property
    def condition_code(self) -> Any:
        return get_extension(self, CONDITION_CODE_URL)

    @condition_code.setter
    def condition_code(self, value: Any) -> None:
        set_extension(self, CONDITION_CODE_URL, value)

    @property
    def certification_type(self) -> Any:
        return get_extension(self, CERTIFICATION_TYPE_URL)

    @certification_type.setter
    def certification_type(self, value: Any) -> None:
        set_extension(self, CERTIFICATION_TYPE_URL, value)

    @property
    def diagnosis_recorded_date(self) -> Any:
        return get_extension(self, DIAGNOSIS_RECORDED_DATE_URL)

    @diagnosis_recorded_date.setter
    def diagnosis_recorded_date(self, value: Any) -> None:
        set_extension(self, DIAGNOSIS_RECORDED_DATE_URL, value)

    @property
    def authorization_number(self) -> Any:
        return get_extension(self, AUTHORIZATION_NUMBER_URL)

    @authorization_number.setter
    def authorization_number(self, value: Any) -> None:
        set_extension(self, AUTHORIZATION_NUMBER_URL, value)

    @property
    def info_changed(self) -> Any:
        return get_extension(self, INFO_CHANGED_URL)

    @info_changed.setter
    def info_changed(self, value: Any) -> None:
        set_extension(self, INFO_CHANGED_URL, value)

    @property
    def item_certification_expiration_date(self) -> Any:
        return get_extension(self, ITEM_CERTIFICATION_EXPIRATION_DATE_URL)

    @item_certification_expiration_date.setter
    def item_certification_expiration_date(self, value: Any) -> None:
        set_extension(self, ITEM_CERTIFICATION_EXPIRATION_DATE_URL, value)

    @property
    def administration_reference_number(self) -> Any:
        return get_extension(self, ADMINISTRATION_REFERENCE_NUMBER_URL)

    @administration_reference_number.setter
    def administration_reference_number(self, value: Any) -> None:
        set_extension(self, ADMINISTRATION_REFERENCE_NUMBER_URL, value)

    @property
    def revenue_unit_rate_limit(self) -> Any:
        return get_extension(self, REVENUE_UNIT_RATE_LIMIT_URL)

    @revenue_unit_rate_limit.setter
    def revenue_unit_rate_limit(self, value: Any) -> None:
        set_extension(self, REVENUE_UNIT_RATE_LIMIT_URL, value)

    @property
    def item_certification_effective_date(self) -> Any:
        return get_extension(self, ITEM_CERTIFICATION_EFFECTIVE_DATE_URL)

    @item_certification_effective_date.setter
    def item_certification_effective_date(self, value: Any) -> None:
        set_extension(self, ITEM_CERTIFICATION_EFFECTIVE_DATE_URL, value)

    @property
    def review_action_code(self) -> Any:
        return get_extension(self, REVIEW_ACTION_CODE_URL)

    @review_action_code.setter
    def review_action_code(self, value: Any) -> None:
        set_extension(self, REVIEW_ACTION_CODE_URL, value)

    @property
    def level_of_service_code(self) -> Any:
        return get_extension(self, LEVEL_OF_SERVICE_CODE_URL)

    @level_of_service_code.setter
    def level_of_service_code(self, value: Any) -> None:
        set_extension(self, LEVEL_OF_SERVICE_CODE_URL, value)

    @property
    def nursing_home_level_of_care(self) -> Any:
        return get_extension(self, NURSING_HOME_LEVEL_OF_CARE_URL)

    @nursing_home_level_of_care.setter
    def nursing_home_level_of_care(self, value: Any) -> None:
        set_extension(self, NURSING_HOME_LEVEL_OF_CARE_URL, value)

    @property
    def modifierextension_info_cancelled(self) -> Any:
        return get_extension(self, MODIFIEREXTENSION_INFO_CANCELLED_URL)

    @modifierextension_info_cancelled.setter
    def modifierextension_info_cancelled(self, value: Any) -> None:
        set_extension(self, MODIFIEREXTENSION_INFO_CANCELLED_URL, value)

    @property
    def nursing_home_residential_status(self) -> Any:
        return get_extension(self, NURSING_HOME_RESIDENTIAL_STATUS_URL)

    @nursing_home_residential_status.setter
    def nursing_home_residential_status(self, value: Any) -> None:
        set_extension(self, NURSING_HOME_RESIDENTIAL_STATUS_URL, value)

    @property
    def epsdt_indicator(self) -> Any:
        return get_extension(self, EPSDT_INDICATOR_URL)

    @epsdt_indicator.setter
    def epsdt_indicator(self, value: Any) -> None:
        set_extension(self, EPSDT_INDICATOR_URL, value)

    @property
    def item_trace_number(self) -> Any:
        return get_extension(self, ITEM_TRACE_NUMBER_URL)

    @item_trace_number.setter
    def item_trace_number(self, value: Any) -> None:
        set_extension(self, ITEM_TRACE_NUMBER_URL, value)

    @property
    def home_health_care_information(self) -> Any:
        return get_extension(self, HOME_HEALTH_CARE_INFORMATION_URL)

    @home_health_care_information.setter
    def home_health_care_information(self, value: Any) -> None:
        set_extension(self, HOME_HEALTH_CARE_INFORMATION_URL, value)

class ClaimResponse(base.ClaimResponse):

    @property
    def requested_service(self) -> Any:
        return get_extension(self, REQUESTED_SERVICE_URL)

    @requested_service.setter
    def requested_service(self, value: Any) -> None:
        set_extension(self, REQUESTED_SERVICE_URL, value)

    @property
    def product_or_service_code_end(self) -> Any:
        return get_extension(self, PRODUCT_OR_SERVICE_CODE_END_URL)

    @product_or_service_code_end.setter
    def product_or_service_code_end(self, value: Any) -> None:
        set_extension(self, PRODUCT_OR_SERVICE_CODE_END_URL, value)

    @property
    def item_pre_auth_issue_date(self) -> Any:
        return get_extension(self, ITEM_PRE_AUTH_ISSUE_DATE_URL)

    @item_pre_auth_issue_date.setter
    def item_pre_auth_issue_date(self, value: Any) -> None:
        set_extension(self, ITEM_PRE_AUTH_ISSUE_DATE_URL, value)

    @property
    def item_authorized_detail(self) -> Any:
        return get_extension(self, ITEM_AUTHORIZED_DETAIL_URL)

    @item_authorized_detail.setter
    def item_authorized_detail(self, value: Any) -> None:
        set_extension(self, ITEM_AUTHORIZED_DETAIL_URL, value)

    @property
    def item_authorized_provider(self) -> Any:
        return get_extension(self, ITEM_AUTHORIZED_PROVIDER_URL)

    @item_authorized_provider.setter
    def item_authorized_provider(self, value: Any) -> None:
        set_extension(self, ITEM_AUTHORIZED_PROVIDER_URL, value)

    @property
    def error_followup_action(self) -> Any:
        return get_extension(self, ERROR_FOLLOWUP_ACTION_URL)

    @error_followup_action.setter
    def error_followup_action(self, value: Any) -> None:
        set_extension(self, ERROR_FOLLOWUP_ACTION_URL, value)

    @property
    def authorization_number(self) -> Any:
        return get_extension(self, AUTHORIZATION_NUMBER_URL)

    @authorization_number.setter
    def authorization_number(self, value: Any) -> None:
        set_extension(self, AUTHORIZATION_NUMBER_URL, value)

    @property
    def item_requested_service_date(self) -> Any:
        return get_extension(self, ITEM_REQUESTED_SERVICE_DATE_URL)

    @item_requested_service_date.setter
    def item_requested_service_date(self, value: Any) -> None:
        set_extension(self, ITEM_REQUESTED_SERVICE_DATE_URL, value)

    @property
    def review_action(self) -> Any:
        return get_extension(self, REVIEW_ACTION_URL)

    @review_action.setter
    def review_action(self, value: Any) -> None:
        set_extension(self, REVIEW_ACTION_URL, value)

    @property
    def administration_reference_number(self) -> Any:
        return get_extension(self, ADMINISTRATION_REFERENCE_NUMBER_URL)

    @administration_reference_number.setter
    def administration_reference_number(self, value: Any) -> None:
        set_extension(self, ADMINISTRATION_REFERENCE_NUMBER_URL, value)

    @property
    def revenue_unit_rate_limit(self) -> Any:
        return get_extension(self, REVENUE_UNIT_RATE_LIMIT_URL)

    @revenue_unit_rate_limit.setter
    def revenue_unit_rate_limit(self, value: Any) -> None:
        set_extension(self, REVENUE_UNIT_RATE_LIMIT_URL, value)

    @property
    def error_path(self) -> Any:
        return get_extension(self, ERROR_PATH_URL)

    @error_path.setter
    def error_path(self, value: Any) -> None:
        set_extension(self, ERROR_PATH_URL, value)

    @property
    def error_element(self) -> Any:
        return get_extension(self, ERROR_ELEMENT_URL)

    @error_element.setter
    def error_element(self, value: Any) -> None:
        set_extension(self, ERROR_ELEMENT_URL, value)

    @property
    def item_pre_auth_period(self) -> Any:
        return get_extension(self, ITEM_PRE_AUTH_PERIOD_URL)

    @item_pre_auth_period.setter
    def item_pre_auth_period(self, value: Any) -> None:
        set_extension(self, ITEM_PRE_AUTH_PERIOD_URL, value)

    @property
    def review_action_code(self) -> Any:
        return get_extension(self, REVIEW_ACTION_CODE_URL)

    @review_action_code.setter
    def review_action_code(self, value: Any) -> None:
        set_extension(self, REVIEW_ACTION_CODE_URL, value)

    @property
    def authorized_provider_type(self) -> Any:
        return get_extension(self, AUTHORIZED_PROVIDER_TYPE_URL)

    @authorized_provider_type.setter
    def authorized_provider_type(self, value: Any) -> None:
        set_extension(self, AUTHORIZED_PROVIDER_TYPE_URL, value)

    @property
    def nursing_home_level_of_care(self) -> Any:
        return get_extension(self, NURSING_HOME_LEVEL_OF_CARE_URL)

    @nursing_home_level_of_care.setter
    def nursing_home_level_of_care(self, value: Any) -> None:
        set_extension(self, NURSING_HOME_LEVEL_OF_CARE_URL, value)

    @property
    def revenue_code(self) -> Any:
        return get_extension(self, REVENUE_CODE_URL)

    @revenue_code.setter
    def revenue_code(self, value: Any) -> None:
        set_extension(self, REVENUE_CODE_URL, value)

    @property
    def nursing_home_residential_status(self) -> Any:
        return get_extension(self, NURSING_HOME_RESIDENTIAL_STATUS_URL)

    @nursing_home_residential_status.setter
    def nursing_home_residential_status(self, value: Any) -> None:
        set_extension(self, NURSING_HOME_RESIDENTIAL_STATUS_URL, value)

    @property
    def epsdt_indicator(self) -> Any:
        return get_extension(self, EPSDT_INDICATOR_URL)

    @epsdt_indicator.setter
    def epsdt_indicator(self, value: Any) -> None:
        set_extension(self, EPSDT_INDICATOR_URL, value)

    @property
    def item_trace_number(self) -> Any:
        return get_extension(self, ITEM_TRACE_NUMBER_URL)

    @item_trace_number.setter
    def item_trace_number(self, value: Any) -> None:
        set_extension(self, ITEM_TRACE_NUMBER_URL, value)

class CommunicationRequest(base.CommunicationRequest):

    @property
    def communicated_diagnosis(self) -> Any:
        return get_extension(self, COMMUNICATED_DIAGNOSIS_URL)

    @communicated_diagnosis.setter
    def communicated_diagnosis(self, value: Any) -> None:
        set_extension(self, COMMUNICATED_DIAGNOSIS_URL, value)

    @property
    def service_line_number(self) -> Any:
        return get_extension(self, SERVICE_LINE_NUMBER_URL)

    @service_line_number.setter
    def service_line_number(self, value: Any) -> None:
        set_extension(self, SERVICE_LINE_NUMBER_URL, value)

    @property
    def content_modifier(self) -> Any:
        return get_extension(self, CONTENT_MODIFIER_URL)

    @content_modifier.setter
    def content_modifier(self, value: Any) -> None:
        set_extension(self, CONTENT_MODIFIER_URL, value)

class Dosage(base.Dosage):

    @property
    def timingdeliverypattern(self) -> Any:
        return get_extension(self, TIMINGDELIVERYPATTERN_URL)

    @timingdeliverypattern.setter
    def timingdeliverypattern(self, value: Any) -> None:
        set_extension(self, TIMINGDELIVERYPATTERN_URL, value)

    @property
    def timingcalendarpattern(self) -> Any:
        return get_extension(self, TIMINGCALENDARPATTERN_URL)

    @timingcalendarpattern.setter
    def timingcalendarpattern(self, value: Any) -> None:
        set_extension(self, TIMINGCALENDARPATTERN_URL, value)

class Encounter(base.Encounter):

    @property
    def patient_status(self) -> Any:
        return get_extension(self, PATIENT_STATUS_URL)

    @patient_status.setter
    def patient_status(self, value: Any) -> None:
        set_extension(self, PATIENT_STATUS_URL, value)

    @property
    def nursing_home_residential_status(self) -> Any:
        return get_extension(self, NURSING_HOME_RESIDENTIAL_STATUS_URL)

    @nursing_home_residential_status.setter
    def nursing_home_residential_status(self, value: Any) -> None:
        set_extension(self, NURSING_HOME_RESIDENTIAL_STATUS_URL, value)

class Examples(base.Examples):

    @property
    def patient_status(self) -> Any:
        return get_extension(self, PATIENT_STATUS_URL)

    @patient_status.setter
    def patient_status(self, value: Any) -> None:
        set_extension(self, PATIENT_STATUS_URL, value)

    @property
    def military_status(self) -> Any:
        return get_extension(self, MILITARY_STATUS_URL)

    @military_status.setter
    def military_status(self, value: Any) -> None:
        set_extension(self, MILITARY_STATUS_URL, value)

    @property
    def timingdeliverypattern(self) -> Any:
        return get_extension(self, TIMINGDELIVERYPATTERN_URL)

    @timingdeliverypattern.setter
    def timingdeliverypattern(self, value: Any) -> None:
        set_extension(self, TIMINGDELIVERYPATTERN_URL, value)

    @property
    def timingcalendarpattern(self) -> Any:
        return get_extension(self, TIMINGCALENDARPATTERN_URL)

    @timingcalendarpattern.setter
    def timingcalendarpattern(self, value: Any) -> None:
        set_extension(self, TIMINGCALENDARPATTERN_URL, value)

class ExplanationOfBenefit(base.ExplanationOfBenefit):

    @property
    def communicated_diagnosis(self) -> Any:
        return get_extension(self, COMMUNICATED_DIAGNOSIS_URL)

    @communicated_diagnosis.setter
    def communicated_diagnosis(self, value: Any) -> None:
        set_extension(self, COMMUNICATED_DIAGNOSIS_URL, value)

    @property
    def care_team_claim_scope(self) -> Any:
        return get_extension(self, CARE_TEAM_CLAIM_SCOPE_URL)

    @care_team_claim_scope.setter
    def care_team_claim_scope(self, value: Any) -> None:
        set_extension(self, CARE_TEAM_CLAIM_SCOPE_URL, value)

    @property
    def certification_type(self) -> Any:
        return get_extension(self, CERTIFICATION_TYPE_URL)

    @certification_type.setter
    def certification_type(self, value: Any) -> None:
        set_extension(self, CERTIFICATION_TYPE_URL, value)

    @property
    def item_pre_auth_issue_date(self) -> Any:
        return get_extension(self, ITEM_PRE_AUTH_ISSUE_DATE_URL)

    @item_pre_auth_issue_date.setter
    def item_pre_auth_issue_date(self, value: Any) -> None:
        set_extension(self, ITEM_PRE_AUTH_ISSUE_DATE_URL, value)

    @property
    def service_line_number(self) -> Any:
        return get_extension(self, SERVICE_LINE_NUMBER_URL)

    @service_line_number.setter
    def service_line_number(self, value: Any) -> None:
        set_extension(self, SERVICE_LINE_NUMBER_URL, value)

    @property
    def item_authorized_detail(self) -> Any:
        return get_extension(self, ITEM_AUTHORIZED_DETAIL_URL)

    @item_authorized_detail.setter
    def item_authorized_detail(self, value: Any) -> None:
        set_extension(self, ITEM_AUTHORIZED_DETAIL_URL, value)

    @property
    def item_authorized_provider(self) -> Any:
        return get_extension(self, ITEM_AUTHORIZED_PROVIDER_URL)

    @item_authorized_provider.setter
    def item_authorized_provider(self, value: Any) -> None:
        set_extension(self, ITEM_AUTHORIZED_PROVIDER_URL, value)

    @property
    def authorization_number(self) -> Any:
        return get_extension(self, AUTHORIZATION_NUMBER_URL)

    @authorization_number.setter
    def authorization_number(self, value: Any) -> None:
        set_extension(self, AUTHORIZATION_NUMBER_URL, value)

    @property
    def review_action(self) -> Any:
        return get_extension(self, REVIEW_ACTION_URL)

    @review_action.setter
    def review_action(self, value: Any) -> None:
        set_extension(self, REVIEW_ACTION_URL, value)

    @property
    def info_changed(self) -> Any:
        return get_extension(self, INFO_CHANGED_URL)

    @info_changed.setter
    def info_changed(self, value: Any) -> None:
        set_extension(self, INFO_CHANGED_URL, value)

    @property
    def administration_reference_number(self) -> Any:
        return get_extension(self, ADMINISTRATION_REFERENCE_NUMBER_URL)

    @administration_reference_number.setter
    def administration_reference_number(self, value: Any) -> None:
        set_extension(self, ADMINISTRATION_REFERENCE_NUMBER_URL, value)

    @property
    def error_path(self) -> Any:
        return get_extension(self, ERROR_PATH_URL)

    @error_path.setter
    def error_path(self, value: Any) -> None:
        set_extension(self, ERROR_PATH_URL, value)

    @property
    def error_element(self) -> Any:
        return get_extension(self, ERROR_ELEMENT_URL)

    @error_element.setter
    def error_element(self, value: Any) -> None:
        set_extension(self, ERROR_ELEMENT_URL, value)

    @property
    def item_pre_auth_period(self) -> Any:
        return get_extension(self, ITEM_PRE_AUTH_PERIOD_URL)

    @item_pre_auth_period.setter
    def item_pre_auth_period(self, value: Any) -> None:
        set_extension(self, ITEM_PRE_AUTH_PERIOD_URL, value)

    @property
    def review_action_code(self) -> Any:
        return get_extension(self, REVIEW_ACTION_CODE_URL)

    @review_action_code.setter
    def review_action_code(self, value: Any) -> None:
        set_extension(self, REVIEW_ACTION_CODE_URL, value)

    @property
    def content_modifier(self) -> Any:
        return get_extension(self, CONTENT_MODIFIER_URL)

    @content_modifier.setter
    def content_modifier(self, value: Any) -> None:
        set_extension(self, CONTENT_MODIFIER_URL, value)

    @property
    def modifierextension_info_cancelled(self) -> Any:
        return get_extension(self, MODIFIEREXTENSION_INFO_CANCELLED_URL)

    @modifierextension_info_cancelled.setter
    def modifierextension_info_cancelled(self, value: Any) -> None:
        set_extension(self, MODIFIEREXTENSION_INFO_CANCELLED_URL, value)

    @property
    def item_trace_number(self) -> Any:
        return get_extension(self, ITEM_TRACE_NUMBER_URL)

    @item_trace_number.setter
    def item_trace_number(self, value: Any) -> None:
        set_extension(self, ITEM_TRACE_NUMBER_URL, value)

class Identifier(base.Identifier):

    @property
    def identifier_sub_department(self) -> Any:
        return get_extension(self, IDENTIFIER_SUB_DEPARTMENT_URL)

    @identifier_sub_department.setter
    def identifier_sub_department(self, value: Any) -> None:
        set_extension(self, IDENTIFIER_SUB_DEPARTMENT_URL, value)

    @property
    def identifier_jurisdiction(self) -> Any:
        return get_extension(self, IDENTIFIER_JURISDICTION_URL)

    @identifier_jurisdiction.setter
    def identifier_jurisdiction(self, value: Any) -> None:
        set_extension(self, IDENTIFIER_JURISDICTION_URL, value)

class Patient(base.Patient):

    @property
    def military_status(self) -> Any:
        return get_extension(self, MILITARY_STATUS_URL)

    @military_status.setter
    def military_status(self, value: Any) -> None:
        set_extension(self, MILITARY_STATUS_URL, value)

class Request(base.Request):

    @property
    def timingdeliverypattern(self) -> Any:
        return get_extension(self, TIMINGDELIVERYPATTERN_URL)

    @timingdeliverypattern.setter
    def timingdeliverypattern(self, value: Any) -> None:
        set_extension(self, TIMINGDELIVERYPATTERN_URL, value)

    @property
    def timingcalendarpattern(self) -> Any:
        return get_extension(self, TIMINGCALENDARPATTERN_URL)

    @timingcalendarpattern.setter
    def timingcalendarpattern(self, value: Any) -> None:
        set_extension(self, TIMINGCALENDARPATTERN_URL, value)

class Task(base.Task):

    @property
    def pa_line_number(self) -> Any:
        return get_extension(self, PA_LINE_NUMBER_URL)

    @pa_line_number.setter
    def pa_line_number(self, value: Any) -> None:
        set_extension(self, PA_LINE_NUMBER_URL, value)
