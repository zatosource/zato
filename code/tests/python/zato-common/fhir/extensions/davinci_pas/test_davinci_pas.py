from __future__ import annotations

from zato.fhir.r4_0_1.davinci_pas.v2_1_0.extensions import (
    REQUESTED_SERVICE_URL,
    SERVICE_ITEM_REQUEST_TYPE_URL,
    PATIENT_STATUS_URL,
    COMMUNICATED_DIAGNOSIS_URL,
    ITEM_CERTIFICATION_ISSUE_DATE_URL,
    CARE_TEAM_CLAIM_SCOPE_URL,
    PRODUCT_OR_SERVICE_CODE_END_URL,
    CONDITION_CODE_URL,
    CERTIFICATION_TYPE_URL,
    ITEM_PRE_AUTH_ISSUE_DATE_URL,
    SERVICE_LINE_NUMBER_URL,
    DIAGNOSIS_RECORDED_DATE_URL,
    ITEM_AUTHORIZED_DETAIL_URL,
    ITEM_AUTHORIZED_PROVIDER_URL,
    PA_LINE_NUMBER_URL,
    ERROR_FOLLOWUP_ACTION_URL,
    MILITARY_STATUS_URL,
    AUTHORIZATION_NUMBER_URL,
    ITEM_REQUESTED_SERVICE_DATE_URL,
    REVIEW_ACTION_URL,
    INFO_CHANGED_URL,
    ITEM_CERTIFICATION_EXPIRATION_DATE_URL,
    ADMINISTRATION_REFERENCE_NUMBER_URL,
    REVENUE_UNIT_RATE_LIMIT_URL,
    ITEM_CERTIFICATION_EFFECTIVE_DATE_URL,
    ERROR_PATH_URL,
    ERROR_ELEMENT_URL,
    ITEM_PRE_AUTH_PERIOD_URL,
    REVIEW_ACTION_CODE_URL,
    CONTENT_MODIFIER_URL,
    LEVEL_OF_SERVICE_CODE_URL,
    TIMINGDELIVERYPATTERN_URL,
    AUTHORIZED_PROVIDER_TYPE_URL,
    IDENTIFIER_SUB_DEPARTMENT_URL,
    IDENTIFIER_JURISDICTION_URL,
    NURSING_HOME_LEVEL_OF_CARE_URL,
    TIMINGCALENDARPATTERN_URL,
    REVENUE_CODE_URL,
    MODIFIEREXTENSION_INFO_CANCELLED_URL,
    NURSING_HOME_RESIDENTIAL_STATUS_URL,
    EPSDT_INDICATOR_URL,
    ITEM_TRACE_NUMBER_URL,
    HOME_HEALTH_CARE_INFORMATION_URL,
)

from zato.fhir.r4_0_1.davinci_pas.v2_1_0.resources import (
    Claim,
    ClaimResponse,
    CommunicationRequest,
    Dosage,
    Encounter,
    Examples,
    ExplanationOfBenefit,
    Identifier,
    Patient,
    Request,
    Task,
)


class TestImports:

    def test_claim_is_importable(self):
        assert Claim is not None

    def test_claimresponse_is_importable(self):
        assert ClaimResponse is not None

    def test_communicationrequest_is_importable(self):
        assert CommunicationRequest is not None

    def test_dosage_is_importable(self):
        assert Dosage is not None

    def test_encounter_is_importable(self):
        assert Encounter is not None

    def test_examples_is_importable(self):
        assert Examples is not None

    def test_explanationofbenefit_is_importable(self):
        assert ExplanationOfBenefit is not None

    def test_identifier_is_importable(self):
        assert Identifier is not None

    def test_patient_is_importable(self):
        assert Patient is not None

    def test_request_is_importable(self):
        assert Request is not None

    def test_task_is_importable(self):
        assert Task is not None


class TestURLConstants:

    def test_requested_service_url(self):
        assert REQUESTED_SERVICE_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-requestedService'

    def test_service_item_request_type_url(self):
        assert SERVICE_ITEM_REQUEST_TYPE_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-serviceItemRequestType'

    def test_patient_status_url(self):
        assert PATIENT_STATUS_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-patientStatus'

    def test_communicated_diagnosis_url(self):
        assert COMMUNICATED_DIAGNOSIS_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-communicatedDiagnosis'

    def test_item_certification_issue_date_url(self):
        assert ITEM_CERTIFICATION_ISSUE_DATE_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-itemCertificationIssueDate'

    def test_care_team_claim_scope_url(self):
        assert CARE_TEAM_CLAIM_SCOPE_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-careTeamClaimScope'

    def test_product_or_service_code_end_url(self):
        assert PRODUCT_OR_SERVICE_CODE_END_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-productOrServiceCodeEnd'

    def test_condition_code_url(self):
        assert CONDITION_CODE_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-conditionCode'

    def test_certification_type_url(self):
        assert CERTIFICATION_TYPE_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-certificationType'

    def test_item_pre_auth_issue_date_url(self):
        assert ITEM_PRE_AUTH_ISSUE_DATE_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-itemPreAuthIssueDate'

    def test_service_line_number_url(self):
        assert SERVICE_LINE_NUMBER_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-serviceLineNumber'

    def test_diagnosis_recorded_date_url(self):
        assert DIAGNOSIS_RECORDED_DATE_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-diagnosisRecordedDate'

    def test_item_authorized_detail_url(self):
        assert ITEM_AUTHORIZED_DETAIL_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-itemAuthorizedDetail'

    def test_item_authorized_provider_url(self):
        assert ITEM_AUTHORIZED_PROVIDER_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-itemAuthorizedProvider'

    def test_pa_line_number_url(self):
        assert PA_LINE_NUMBER_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-paLineNumber'

    def test_error_followup_action_url(self):
        assert ERROR_FOLLOWUP_ACTION_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-errorFollowupAction'

    def test_military_status_url(self):
        assert MILITARY_STATUS_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-militaryStatus'

    def test_authorization_number_url(self):
        assert AUTHORIZATION_NUMBER_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-authorizationNumber'

    def test_item_requested_service_date_url(self):
        assert ITEM_REQUESTED_SERVICE_DATE_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-itemRequestedServiceDate'

    def test_review_action_url(self):
        assert REVIEW_ACTION_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-reviewAction'

    def test_info_changed_url(self):
        assert INFO_CHANGED_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-infoChanged'

    def test_item_certification_expiration_date_url(self):
        assert ITEM_CERTIFICATION_EXPIRATION_DATE_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-itemCertificationExpirationDate'

    def test_administration_reference_number_url(self):
        assert ADMINISTRATION_REFERENCE_NUMBER_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-administrationReferenceNumber'

    def test_revenue_unit_rate_limit_url(self):
        assert REVENUE_UNIT_RATE_LIMIT_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-revenueUnitRateLimit'

    def test_item_certification_effective_date_url(self):
        assert ITEM_CERTIFICATION_EFFECTIVE_DATE_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-itemCertificationEffectiveDate'

    def test_error_path_url(self):
        assert ERROR_PATH_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-errorPath'

    def test_error_element_url(self):
        assert ERROR_ELEMENT_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-errorElement'

    def test_item_pre_auth_period_url(self):
        assert ITEM_PRE_AUTH_PERIOD_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-itemPreAuthPeriod'

    def test_review_action_code_url(self):
        assert REVIEW_ACTION_CODE_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-reviewActionCode'

    def test_content_modifier_url(self):
        assert CONTENT_MODIFIER_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-contentModifier'

    def test_level_of_service_code_url(self):
        assert LEVEL_OF_SERVICE_CODE_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-levelOfServiceCode'

    def test_timingdeliverypattern_url(self):
        assert TIMINGDELIVERYPATTERN_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-timingdeliverypattern'

    def test_authorized_provider_type_url(self):
        assert AUTHORIZED_PROVIDER_TYPE_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-authorizedProviderType'

    def test_identifier_sub_department_url(self):
        assert IDENTIFIER_SUB_DEPARTMENT_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-identifierSubDepartment'

    def test_identifier_jurisdiction_url(self):
        assert IDENTIFIER_JURISDICTION_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-identifierJurisdiction'

    def test_nursing_home_level_of_care_url(self):
        assert NURSING_HOME_LEVEL_OF_CARE_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-nursingHomeLevelOfCare'

    def test_timingcalendarpattern_url(self):
        assert TIMINGCALENDARPATTERN_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-timingcalendarpattern'

    def test_revenue_code_url(self):
        assert REVENUE_CODE_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-revenueCode'

    def test_modifierextension_info_cancelled_url(self):
        assert MODIFIEREXTENSION_INFO_CANCELLED_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/modifierextension-infoCancelled'

    def test_nursing_home_residential_status_url(self):
        assert NURSING_HOME_RESIDENTIAL_STATUS_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-nursingHomeResidentialStatus'

    def test_epsdt_indicator_url(self):
        assert EPSDT_INDICATOR_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-epsdtIndicator'

    def test_item_trace_number_url(self):
        assert ITEM_TRACE_NUMBER_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-itemTraceNumber'

    def test_home_health_care_information_url(self):
        assert HOME_HEALTH_CARE_INFORMATION_URL == 'http://hl7.org/fhir/us/davinci-pas/StructureDefinition/extension-homeHealthCareInformation'


class TestPropertyAccess:

    def test_claim_requested_service_roundtrip(self):
        r = Claim()
        r.requested_service = "test-value"
        result = r.requested_service
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_service_item_request_type_roundtrip(self):
        r = Claim()
        r.service_item_request_type = "test-value"
        result = r.service_item_request_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_communicated_diagnosis_roundtrip(self):
        r = Claim()
        r.communicated_diagnosis = "test-value"
        result = r.communicated_diagnosis
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_item_certification_issue_date_roundtrip(self):
        r = Claim()
        r.item_certification_issue_date = "test-value"
        result = r.item_certification_issue_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_care_team_claim_scope_roundtrip(self):
        r = Claim()
        r.care_team_claim_scope = "test-value"
        result = r.care_team_claim_scope
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_product_or_service_code_end_roundtrip(self):
        r = Claim()
        r.product_or_service_code_end = "test-value"
        result = r.product_or_service_code_end
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_condition_code_roundtrip(self):
        r = Claim()
        r.condition_code = "test-value"
        result = r.condition_code
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_certification_type_roundtrip(self):
        r = Claim()
        r.certification_type = "test-value"
        result = r.certification_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_diagnosis_recorded_date_roundtrip(self):
        r = Claim()
        r.diagnosis_recorded_date = "test-value"
        result = r.diagnosis_recorded_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_authorization_number_roundtrip(self):
        r = Claim()
        r.authorization_number = "test-value"
        result = r.authorization_number
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_info_changed_roundtrip(self):
        r = Claim()
        r.info_changed = "test-value"
        result = r.info_changed
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_item_certification_expiration_date_roundtrip(self):
        r = Claim()
        r.item_certification_expiration_date = "test-value"
        result = r.item_certification_expiration_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_administration_reference_number_roundtrip(self):
        r = Claim()
        r.administration_reference_number = "test-value"
        result = r.administration_reference_number
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_revenue_unit_rate_limit_roundtrip(self):
        r = Claim()
        r.revenue_unit_rate_limit = "test-value"
        result = r.revenue_unit_rate_limit
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_item_certification_effective_date_roundtrip(self):
        r = Claim()
        r.item_certification_effective_date = "test-value"
        result = r.item_certification_effective_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_review_action_code_roundtrip(self):
        r = Claim()
        r.review_action_code = "test-value"
        result = r.review_action_code
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_level_of_service_code_roundtrip(self):
        r = Claim()
        r.level_of_service_code = "test-value"
        result = r.level_of_service_code
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_nursing_home_level_of_care_roundtrip(self):
        r = Claim()
        r.nursing_home_level_of_care = "test-value"
        result = r.nursing_home_level_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_modifierextension_info_cancelled_roundtrip(self):
        r = Claim()
        r.modifierextension_info_cancelled = "test-value"
        result = r.modifierextension_info_cancelled
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_nursing_home_residential_status_roundtrip(self):
        r = Claim()
        r.nursing_home_residential_status = "test-value"
        result = r.nursing_home_residential_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_epsdt_indicator_roundtrip(self):
        r = Claim()
        r.epsdt_indicator = "test-value"
        result = r.epsdt_indicator
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_item_trace_number_roundtrip(self):
        r = Claim()
        r.item_trace_number = "test-value"
        result = r.item_trace_number
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_home_health_care_information_roundtrip(self):
        r = Claim()
        r.home_health_care_information = "test-value"
        result = r.home_health_care_information
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claimresponse_requested_service_roundtrip(self):
        r = ClaimResponse()
        r.requested_service = "test-value"
        result = r.requested_service
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claimresponse_product_or_service_code_end_roundtrip(self):
        r = ClaimResponse()
        r.product_or_service_code_end = "test-value"
        result = r.product_or_service_code_end
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claimresponse_item_pre_auth_issue_date_roundtrip(self):
        r = ClaimResponse()
        r.item_pre_auth_issue_date = "test-value"
        result = r.item_pre_auth_issue_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claimresponse_item_authorized_detail_roundtrip(self):
        r = ClaimResponse()
        r.item_authorized_detail = "test-value"
        result = r.item_authorized_detail
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claimresponse_item_authorized_provider_roundtrip(self):
        r = ClaimResponse()
        r.item_authorized_provider = "test-value"
        result = r.item_authorized_provider
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claimresponse_error_followup_action_roundtrip(self):
        r = ClaimResponse()
        r.error_followup_action = "test-value"
        result = r.error_followup_action
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claimresponse_authorization_number_roundtrip(self):
        r = ClaimResponse()
        r.authorization_number = "test-value"
        result = r.authorization_number
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claimresponse_item_requested_service_date_roundtrip(self):
        r = ClaimResponse()
        r.item_requested_service_date = "test-value"
        result = r.item_requested_service_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claimresponse_review_action_roundtrip(self):
        r = ClaimResponse()
        r.review_action = "test-value"
        result = r.review_action
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claimresponse_administration_reference_number_roundtrip(self):
        r = ClaimResponse()
        r.administration_reference_number = "test-value"
        result = r.administration_reference_number
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claimresponse_revenue_unit_rate_limit_roundtrip(self):
        r = ClaimResponse()
        r.revenue_unit_rate_limit = "test-value"
        result = r.revenue_unit_rate_limit
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claimresponse_error_path_roundtrip(self):
        r = ClaimResponse()
        r.error_path = "test-value"
        result = r.error_path
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claimresponse_error_element_roundtrip(self):
        r = ClaimResponse()
        r.error_element = "test-value"
        result = r.error_element
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claimresponse_item_pre_auth_period_roundtrip(self):
        r = ClaimResponse()
        r.item_pre_auth_period = "test-value"
        result = r.item_pre_auth_period
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claimresponse_review_action_code_roundtrip(self):
        r = ClaimResponse()
        r.review_action_code = "test-value"
        result = r.review_action_code
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claimresponse_authorized_provider_type_roundtrip(self):
        r = ClaimResponse()
        r.authorized_provider_type = "test-value"
        result = r.authorized_provider_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claimresponse_nursing_home_level_of_care_roundtrip(self):
        r = ClaimResponse()
        r.nursing_home_level_of_care = "test-value"
        result = r.nursing_home_level_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claimresponse_revenue_code_roundtrip(self):
        r = ClaimResponse()
        r.revenue_code = "test-value"
        result = r.revenue_code
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claimresponse_nursing_home_residential_status_roundtrip(self):
        r = ClaimResponse()
        r.nursing_home_residential_status = "test-value"
        result = r.nursing_home_residential_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claimresponse_epsdt_indicator_roundtrip(self):
        r = ClaimResponse()
        r.epsdt_indicator = "test-value"
        result = r.epsdt_indicator
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claimresponse_item_trace_number_roundtrip(self):
        r = ClaimResponse()
        r.item_trace_number = "test-value"
        result = r.item_trace_number
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_communicationrequest_communicated_diagnosis_roundtrip(self):
        r = CommunicationRequest()
        r.communicated_diagnosis = "test-value"
        result = r.communicated_diagnosis
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_communicationrequest_service_line_number_roundtrip(self):
        r = CommunicationRequest()
        r.service_line_number = "test-value"
        result = r.service_line_number
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_communicationrequest_content_modifier_roundtrip(self):
        r = CommunicationRequest()
        r.content_modifier = "test-value"
        result = r.content_modifier
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_dosage_timingdeliverypattern_roundtrip(self):
        r = Dosage()
        r.timingdeliverypattern = "test-value"
        result = r.timingdeliverypattern
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_dosage_timingcalendarpattern_roundtrip(self):
        r = Dosage()
        r.timingcalendarpattern = "test-value"
        result = r.timingcalendarpattern
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_patient_status_roundtrip(self):
        r = Encounter()
        r.patient_status = "test-value"
        result = r.patient_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_nursing_home_residential_status_roundtrip(self):
        r = Encounter()
        r.nursing_home_residential_status = "test-value"
        result = r.nursing_home_residential_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_examples_patient_status_roundtrip(self):
        r = Examples()
        r.patient_status = "test-value"
        result = r.patient_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_examples_military_status_roundtrip(self):
        r = Examples()
        r.military_status = "test-value"
        result = r.military_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_examples_timingdeliverypattern_roundtrip(self):
        r = Examples()
        r.timingdeliverypattern = "test-value"
        result = r.timingdeliverypattern
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_examples_timingcalendarpattern_roundtrip(self):
        r = Examples()
        r.timingcalendarpattern = "test-value"
        result = r.timingcalendarpattern
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_explanationofbenefit_communicated_diagnosis_roundtrip(self):
        r = ExplanationOfBenefit()
        r.communicated_diagnosis = "test-value"
        result = r.communicated_diagnosis
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_explanationofbenefit_care_team_claim_scope_roundtrip(self):
        r = ExplanationOfBenefit()
        r.care_team_claim_scope = "test-value"
        result = r.care_team_claim_scope
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_explanationofbenefit_certification_type_roundtrip(self):
        r = ExplanationOfBenefit()
        r.certification_type = "test-value"
        result = r.certification_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_explanationofbenefit_item_pre_auth_issue_date_roundtrip(self):
        r = ExplanationOfBenefit()
        r.item_pre_auth_issue_date = "test-value"
        result = r.item_pre_auth_issue_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_explanationofbenefit_service_line_number_roundtrip(self):
        r = ExplanationOfBenefit()
        r.service_line_number = "test-value"
        result = r.service_line_number
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_explanationofbenefit_item_authorized_detail_roundtrip(self):
        r = ExplanationOfBenefit()
        r.item_authorized_detail = "test-value"
        result = r.item_authorized_detail
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_explanationofbenefit_item_authorized_provider_roundtrip(self):
        r = ExplanationOfBenefit()
        r.item_authorized_provider = "test-value"
        result = r.item_authorized_provider
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_explanationofbenefit_authorization_number_roundtrip(self):
        r = ExplanationOfBenefit()
        r.authorization_number = "test-value"
        result = r.authorization_number
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_explanationofbenefit_review_action_roundtrip(self):
        r = ExplanationOfBenefit()
        r.review_action = "test-value"
        result = r.review_action
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_explanationofbenefit_info_changed_roundtrip(self):
        r = ExplanationOfBenefit()
        r.info_changed = "test-value"
        result = r.info_changed
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_explanationofbenefit_administration_reference_number_roundtrip(self):
        r = ExplanationOfBenefit()
        r.administration_reference_number = "test-value"
        result = r.administration_reference_number
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_explanationofbenefit_error_path_roundtrip(self):
        r = ExplanationOfBenefit()
        r.error_path = "test-value"
        result = r.error_path
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_explanationofbenefit_error_element_roundtrip(self):
        r = ExplanationOfBenefit()
        r.error_element = "test-value"
        result = r.error_element
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_explanationofbenefit_item_pre_auth_period_roundtrip(self):
        r = ExplanationOfBenefit()
        r.item_pre_auth_period = "test-value"
        result = r.item_pre_auth_period
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_explanationofbenefit_review_action_code_roundtrip(self):
        r = ExplanationOfBenefit()
        r.review_action_code = "test-value"
        result = r.review_action_code
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_explanationofbenefit_content_modifier_roundtrip(self):
        r = ExplanationOfBenefit()
        r.content_modifier = "test-value"
        result = r.content_modifier
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_explanationofbenefit_modifierextension_info_cancelled_roundtrip(self):
        r = ExplanationOfBenefit()
        r.modifierextension_info_cancelled = "test-value"
        result = r.modifierextension_info_cancelled
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_explanationofbenefit_item_trace_number_roundtrip(self):
        r = ExplanationOfBenefit()
        r.item_trace_number = "test-value"
        result = r.item_trace_number
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_identifier_identifier_sub_department_roundtrip(self):
        r = Identifier()
        r.identifier_sub_department = "test-value"
        result = r.identifier_sub_department
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_identifier_identifier_jurisdiction_roundtrip(self):
        r = Identifier()
        r.identifier_jurisdiction = "test-value"
        result = r.identifier_jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_military_status_roundtrip(self):
        r = Patient()
        r.military_status = "test-value"
        result = r.military_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_request_timingdeliverypattern_roundtrip(self):
        r = Request()
        r.timingdeliverypattern = "test-value"
        result = r.timingdeliverypattern
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_request_timingcalendarpattern_roundtrip(self):
        r = Request()
        r.timingcalendarpattern = "test-value"
        result = r.timingcalendarpattern
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_task_pa_line_number_roundtrip(self):
        r = Task()
        r.pa_line_number = "test-value"
        result = r.pa_line_number
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

