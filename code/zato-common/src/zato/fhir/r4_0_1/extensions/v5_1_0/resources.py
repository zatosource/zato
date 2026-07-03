from __future__ import annotations

from typing import Any

from zato.fhir.r4_0_1 import resources as base
from zato.fhir.extensions import get_extension, get_extension_text, set_extension, set_extension_text
from zato.fhir.r4_0_1.extensions.v5_1_0.extensions import (
    WORKFLOW_RELEASE_DATE_URL,
    ARTIFACT_IS_OWNED_URL,
    CQF_TARGET_INVARIANT_URL,
    TARGET_CONSTRAINT_URL,
    REPLACES_URL,
    VARIABLE_URL,
    WORKFLOW_SHALL_COMPLY_WITH_URL,
    ISO21090_ADXP_POST_BOX_URL,
    EXTENDED_CONTACT_AVAILABILITY_URL,
    ISO21090_ADXP_STREET_NAME_URL,
    ISO21090_ADXP_UNIT_ID_URL,
    ADDRESS_OFFICIAL_URL,
    ISO21090_ADXP_STREET_NAME_BASE_URL,
    ISO21090_ADXP_UNIT_TYPE_URL,
    ISO21090_ADXP_STREET_NAME_TYPE_URL,
    CONFIDENTIAL_URL,
    ISO21090_ADXP_ADDITIONAL_LOCATOR_URL,
    LANGUAGE_URL,
    CQF_IS_EMPTY_LIST_URL,
    GEOLOCATION_URL,
    ISO21090_ADXP_HOUSE_NUMBER_URL,
    NO_FIXED_ADDRESS_URL,
    ISO21090_ADXP_DELIVERY_MODE_IDENTIFIER_URL,
    ISO21090_ADXP_DELIVERY_INSTALLATION_AREA_URL,
    ISO21090_ADXP_DELIVERY_ADDRESS_LINE_URL,
    ISO21090_ADXP_DELIVERY_INSTALLATION_QUALIFIER_URL,
    ISO21090_ADXP_STREET_ADDRESS_LINE_URL,
    ISO21090_ADXP_CARE_OF_URL,
    ISO21090_ADXP_DELIVERY_MODE_URL,
    ISO21090_ADXP_HOUSE_NUMBER_NUMERIC_URL,
    ISO21090_ADXP_DELIMITER_URL,
    ISO21090_ADXP_DELIVERY_INSTALLATION_TYPE_URL,
    ISO21090_ADXP_BUILDING_NUMBER_SUFFIX_URL,
    ISO21090_PREFERRED_URL,
    ISO21090_AD_USE_URL,
    ISO21090_ADXP_PRECINCT_URL,
    ISO21090_ADXP_DIRECTION_URL,
    ISO21090_ADXP_CENSUS_TRACT_URL,
    WORKFLOW_EPISODE_OF_CARE_URL,
    ALLERGYINTOLERANCE_DURATION_URL,
    OPEN_EHR_EXPOSURE_DESCRIPTION_URL,
    OPEN_EHR_CAREPLAN_URL,
    OPEN_EHR_LOCATION_URL,
    ALLERGYINTOLERANCE_SUBSTANCE_EXPOSURE_RISK_URL,
    ALLERGYINTOLERANCE_ABATEMENT_URL,
    ALLERGYINTOLERANCE_REASON_REFUTED_URL,
    OPEN_EHR_EXPOSURE_DURATION_URL,
    ALLERGYINTOLERANCE_RESOLUTION_AGE_URL,
    OPEN_EHR_MANAGEMENT_URL,
    OPEN_EHR_EXPOSURE_DATE_URL,
    CONDITION_ASSERTED_DATE_URL,
    ALLERGYINTOLERANCE_CERTAINTY_URL,
    ALLERGYINTOLERANCE_ASSERTED_DATE_URL,
    OPEN_EHR_ADMINISTRATION_URL,
    ANNOTATION_TYPE_URL,
    AUDITEVENT_PARTICIPANT_OBJECT_CONTAINS_STUDY_URL,
    AUDITEVENT_MPPS_URL,
    AUDITEVENT_LIFECYCLE_URL,
    AUDITEVENT_ANONYMIZED_URL,
    AUDITEVENT_INSTANCE_URL,
    AUDITEVENT_ACCESSION_URL,
    AUDITEVENT_ON_BEHALF_OF_URL,
    AUDITEVENT_SOPCLASS_URL,
    AUDITEVENT_ALTERNATIVE_USER_ID_URL,
    AUDITEVENT_ENCRYPTED_URL,
    AUDITEVENT_NUMBER_OF_INSTANCES_URL,
    _DATATYPE_URL,
    CQF_INITIATING_ORGANIZATION_URL,
    CQF_INITIATING_PERSON_URL,
    CQF_SYSTEM_USER_LANGUAGE_URL,
    CQF_RECIPIENT_TYPE_URL,
    CQF_ENCOUNTER_CLASS_URL,
    CQF_RECIPIENT_LANGUAGE_URL,
    ARTIFACTASSESSMENT_CONTENT_URL,
    CQF_RECEIVING_ORGANIZATION_URL,
    CQF_RECEIVING_PERSON_URL,
    CQF_SYSTEM_USER_TYPE_URL,
    CQF_ENCOUNTER_TYPE_URL,
    CQF_SYSTEM_USER_TASK_CONTEXT_URL,
    BIOLOGICALLYDERIVEDPRODUCT_COLLECTION_PROCEDURE_URL,
    BIOLOGICALLYDERIVEDPRODUCT_PROCESSING_URL,
    BIOLOGICALLYDERIVEDPRODUCT_MANIPULATION_URL,
    HTTP_RESPONSE_HEADER_URL,
    LOCATION_DISTANCE_URL,
    MATCH_GRADE_URL,
    STRUCTUREDEFINITION_STANDARDS_STATUS_URL,
    STRUCTUREDEFINITION_NORMATIVE_VERSION_URL,
    CANONICALRESOURCE_SHORT_DESCRIPTION_URL,
    RESOURCE_APPROVAL_DATE_URL,
    CAPABILITYSTATEMENT_SEARCH_MODE_URL,
    RESOURCE_LAST_REVIEW_DATE_URL,
    CAPABILITYSTATEMENT_SEARCH_PARAMETER_USE_URL,
    OAUTH_URIS_URL,
    CAPABILITYSTATEMENT_EXPECTATION_URL,
    CAPABILITYSTATEMENT_DECLARED_PROFILE_URL,
    RESOURCE_EFFECTIVE_PERIOD_URL,
    CQF_SUPPORTED_CQL_VERSION_URL,
    CAPABILITYSTATEMENT_PROHIBITED_URL,
    CAPABILITYSTATEMENT_SEARCH_PARAMETER_COMBINATION_URL,
    CAPABILITYSTATEMENT_SUPPORTED_SYSTEM_URL,
    CAPABILITIES_URL,
    CAPABILITYSTATEMENT_WEBSOCKET_URL,
    WORKFLOW_TRIGGERED_BY_URL,
    WORKFLOW_GENERATED_FROM_URL,
    WORKFLOW_PROTECTIVE_FACTOR_URL,
    REQUEST_RELEVANT_HISTORY_URL,
    CAREPLAN_ACTIVITY_TITLE_URL,
    WORKFLOW_BARRIER_URL,
    WORKFLOW_COMPLIES_WITH_URL,
    CARETEAM_ALIAS_URL,
    EVENT_BASED_ON_URL,
    CITATION_SOCIETY_AFFILIATION_URL,
    CODESYSTEM_WARNING_URL,
    CODESYSTEM_ALTERNATE_URL,
    CODESYSTEM_HISTORY_URL,
    TERMINOLOGY_RESOURCE_IDENTIFIER_METADATA_URL,
    CODESYSTEM_PROPERTIES_MODE_URL,
    CODESYSTEM_TRUSTED_EXPANSION_URL,
    CODESYSTEM_OTHER_NAME_URL,
    CODESYSTEM_AUTHORITATIVE_SOURCE_URL,
    VALUESET_SPECIAL_STATUS_URL,
    CODESYSTEM_LABEL_URL,
    CODESYSTEM_CONCEPT_ORDER_URL,
    CODESYSTEM_KEY_WORD_URL,
    CODESYSTEM_SOURCE_REFERENCE_URL,
    CODESYSTEM_WORKFLOW_STATUS_URL,
    CODESYSTEM_REPLACEDBY_URL,
    CODESYSTEM_USAGE_URL,
    CODESYSTEM_USE_MARKDOWN_URL,
    CODESYSTEM_CONCEPT_COMMENTS_URL,
    CODING_SCTDESCID_URL,
    CODESYSTEM_MAP_URL,
    CQF_NOT_DONE_VALUE_SET_URL,
    VALUESET_REFERENCE_URL,
    ITEM_WEIGHT_URL,
    CODING_CONFORMANCE_URL,
    CODING_PURPOSE_URL,
    COMMUNICATION_MEDIA_URL,
    WORKFLOW_ADHERES_TO_URL,
    WORKFLOW_SUPPORTING_INFO_URL,
    COMMUNICATIONREQUEST_INITIATING_LOCATION_URL,
    WORKFLOW_RESEARCH_STUDY_URL,
    COMPOSITION_SECTION_SUBJECT_URL,
    COMPOSITION_CLINICALDOCUMENT_VERSION_NUMBER_URL,
    NOTE_URL,
    CQM_VALIDITY_PERIOD_URL,
    WORKFLOW_RELATED_ARTIFACT_URL,
    CONCEPT_BIDIRECTIONAL_URL,
    CONDITION_RULED_OUT_URL,
    CONDITION_RELATED_URL,
    CONDITION_DISEASE_COURSE_URL,
    CONDITION_DUE_TO_URL,
    CONDITION_OCCURRED_FOLLOWING_URL,
    EVENT_PART_OF_URL,
    CONDITION_OUTCOME_URL,
    CONDITION_REVIEWED_URL,
    CONSENT_TRANSCRIBER_URL,
    EVENT_PERFORMER_FUNCTION_URL,
    CONSENT_NOTIFICATION_ENDPOINT_URL,
    CONSENT_LOCATION_URL,
    CONSENT_WITNESS_URL,
    CONSENT_RESEARCH_STUDY_CONTEXT_URL,
    CQF_CONTRIBUTION_TIME_URL,
    ARTIFACT_CONTACT_DETAIL_REFERENCE_URL,
    CQF_CONTACT_REFERENCE_URL,
    CQF_CONTACT_ADDRESS_URL,
    CONTACTPOINT_AREA_URL,
    CONTACTPOINT_LOCAL_URL,
    ISO21090_TEL_ADDRESS_URL,
    CONTACTPOINT_PURPOSE_URL,
    CONTACTPOINT_EXTENSION_URL,
    CONTACTPOINT_COMMENT_URL,
    CONTACTPOINT_COUNTRY_URL,
    CQF_IS_SELECTIVE_URL,
    CQF_FHIR_QUERY_PATTERN_URL,
    CQF_VALUE_FILTER_URL,
    DEVICE_MAINTENANCERESPONSIBILITY_URL,
    DEVICE_LASTMAINTENANCETIME_URL,
    DEVICE_IMPLANT_STATUS_URL,
    DEVICE_COMMERCIAL_BRAND_URL,
    DEVICEREQUEST_PATIENT_INSTRUCTION_URL,
    WORKFLOW_FOLLOW_ON_OF_URL,
    PROCEDURE_APPROACH_BODY_STRUCTURE_URL,
    REQUEST_STATUS_REASON_URL,
    EVENT_STATUS_REASON_URL,
    EVENT_EVENT_HISTORY_URL,
    DIAGNOSTIC_REPORT_FOCUS_URL,
    DIAGNOSTIC_REPORT_RISK_URL,
    DIAGNOSTIC_REPORT_EXTENDS_URL,
    DIAGNOSTIC_REPORT_SUMMARY_OF_URL,
    DIAGNOSTIC_REPORT_WORKFLOW_STATUS_URL,
    DIAGNOSTIC_REPORT_ADDENDUM_OF_URL,
    DIAGNOSTIC_REPORT_REPLACES_URL,
    WORKFLOW_REASON_URL,
    DIAGNOSTIC_REPORT_LOCATION_PERFORMED_URL,
    EVENT_LOCATION_URL,
    DOCUMENTREFERENCE_SOURCEPATIENT_URL,
    DOCUMENTREFERENCE_THUMBNAIL_URL,
    CQF_LIBRARY_URL,
    CQF_KNOWLEDGE_CAPABILITY_URL,
    STRUCTUREDEFINITION_FMM_URL,
    STRUCTUREDEFINITION_STANDARDS_STATUS_REASON_URL,
    CQF_KNOWLEDGE_REPRESENTATION_LEVEL_URL,
    CQF_LOGIC_DEFINITION_URL,
    STRUCTUREDEFINITION_WG_URL,
    STRUCTUREDEFINITION_FMM_SUPPORT_URL,
    DOSAGE_MINIMUM_GAP_BETWEEN_DOSE_URL,
    DOSAGE_CONDITIONS_URL,
    ARTIFACT_EDITOR_URL,
    CQF_CALCULATED_VALUE_URL,
    CQF_EXPRESSION_URL,
    NARRATIVE_LINK_URL,
    RENDERING_STYLE_URL,
    CQF_CITATION_URL,
    VERSION_SPECIFIC_USE_URL,
    SATISFIES_REQUIREMENT_URL,
    CQF_INITIAL_VALUE_URL,
    DERIVATION_REFERENCE_URL,
    CQF_CERTAINTY_URL,
    ARTIFACT_REFERENCE_URL,
    ARTIFACT_ENDORSER_URL,
    VERSION_SPECIFIC_VALUE_URL,
    ARTIFACT_CANONICAL_REFERENCE_URL,
    ORIGINAL_TEXT_URL,
    ARTIFACT_REVIEWER_URL,
    CQF_RELATIVE_DATE_TIME_URL,
    DATA_ABSENT_REASON_URL,
    RENDERING_STYLE_SENSITIVE_URL,
    ISO21090_NULL_FLAVOR_URL,
    BODY_SITE_URL,
    ELEMENTDEFINITION_BESTPRACTICE_EXPLANATION_URL,
    STRUCTUREDEFINITION_DISPLAY_HINT_URL,
    ELEMENTDEFINITION_PATTERN_URL,
    ELEMENTDEFINITION_TYPE_MUST_SUPPORT_URL,
    ELEMENTDEFINITION_TRANSLATABLE_URL,
    MIN_LENGTH_URL,
    EXT_11179_OBJECT_CLASS_URL,
    ELEMENTDEFINITION_EQUIVALENCE_URL,
    QUESTIONNAIRE_CONSTRAINT_URL,
    STRUCTUREDEFINITION_FHIR_TYPE_URL,
    ELEMENTDEFINITION_PROFILE_ELEMENT_URL,
    ELEMENTDEFINITION_SELECTOR_URL,
    QUESTIONNAIRE_SIGNATURE_REQUIRED_URL,
    ELEMENTDEFINITION_MAX_VALUE_SET_URL,
    MAX_DECIMAL_PLACES_URL,
    QUESTIONNAIRE_HIDDEN_URL,
    ELEMENTDEFINITION_IS_COMMON_BINDING_URL,
    CQF_SHOULD_TRACE_DEPENDENCY_URL,
    ELEMENTDEFINITION_DEFAULTTYPE_URL,
    ELEMENTDEFINITION_ALLOWED_UNITS_URL,
    ELEMENTDEFINITION_SUPPRESS_URL,
    STRUCTUREDEFINITION_EXPLICIT_TYPE_NAME_URL,
    ELEMENTDEFINITION_IDENTIFIER_URL,
    STRUCTUREDEFINITION_HIERARCHY_URL,
    OBLIGATION_URL,
    EXT_11179_OBJECT_CLASS_PROPERTY_URL,
    QUESTIONNAIRE_ITEM_CONTROL_URL,
    QUESTIONNAIRE_SUPPORT_LINK_URL,
    MIME_TYPE_URL,
    DESIGN_NOTE_URL,
    ELEMENTDEFINITION_INHERITED_EXTENSIBLE_VALUE_SET_URL,
    ELEMENTDEFINITION_QUESTION_URL,
    ELEMENTDEFINITION_BESTPRACTICE_URL,
    QUESTIONNAIRE_BASE_TYPE_URL,
    ELEMENTDEFINITION_BINDING_NAME_URL,
    ELEMENTDEFINITION_GRAPH_CONSTRAINT_URL,
    ELEMENTDEFINITION_MIN_VALUE_SET_URL,
    QUESTIONNAIRE_USAGE_MODE_URL,
    ENTRY_FORMAT_URL,
    MAX_SIZE_URL,
    ENCOUNTER_MODE_OF_ARRIVAL_URL,
    ENCOUNTER_REASON_CANCELLED_URL,
    ENCOUNTER_ASSOCIATED_ENCOUNTER_URL,
    ENDPOINT_FHIR_VERSION_URL,
    STATISTIC_MODEL_INCLUDE_IF_URL,
    REFERENCES_CONTAINED_URL,
    CQF_ALTERNATIVE_EXPRESSION_URL,
    STRUCTUREDEFINITION_EXTENSION_MEANING_URL,
    FAMILY_MEMBER_HISTORY_GENETICS_PARENT_URL,
    FAMILYMEMBERHISTORY_PATIENT_RECORD_URL,
    FAMILY_MEMBER_HISTORY_GENETICS_SIBLING_URL,
    FAMILYMEMBERHISTORY_TYPE_URL,
    FAMILYMEMBERHISTORY_SEVERITY_URL,
    FAMILYMEMBERHISTORY_ABATEMENT_URL,
    FAMILY_MEMBER_HISTORY_GENETICS_OBSERVATION_URL,
    FLAG_DETAIL_URL,
    FLAG_PRIORITY_URL,
    GOAL_ACCEPTANCE_URL,
    GOAL_REASON_REJECTED_URL,
    GOAL_RELATIONSHIP_URL,
    CQF_TEST_ARTIFACT_URL,
    CQF_INPUT_PARAMETERS_URL,
    CHARACTERISTIC_EXPRESSION_URL,
    HUMANNAME_MOTHERS_FAMILY_URL,
    HUMANNAME_OWN_PREFIX_URL,
    ISO21090_EN_REPRESENTATION_URL,
    HUMANNAME_ASSEMBLY_ORDER_URL,
    HUMANNAME_PARTNER_PREFIX_URL,
    ISO21090_EN_QUALIFIER_URL,
    HUMANNAME_OWN_NAME_URL,
    ISO21090_EN_USE_URL,
    HUMANNAME_FATHERS_FAMILY_URL,
    HUMANNAME_PARTNER_NAME_URL,
    RENDERED_VALUE_URL,
    IDENTIFIER_CHECK_DIGIT_URL,
    IDENTIFIER_VALID_DATE_URL,
    IMMUNIZATION_PROCEDURE_URL,
    CQF_MODEL_INFO_SETTINGS_URL,
    CQF_EXPANSION_PARAMETERS_URL,
    IMPLEMENTATIONGUIDE_SOURCE_FILE_URL,
    CQF_CQL_OPTIONS_URL,
    CQF_PART_OF_URL,
    LIST_CHANGE_BASE_URL,
    LIST_FOR_URL,
    LIST_CATEGORY_URL,
    LOCATION_COMMUNICATION_URL,
    LOCATION_BOUNDARY_GEOJSON_URL,
    CQF_CRITERIA_REFERENCE_URL,
    CQF_IMPROVEMENT_NOTATION_GUIDANCE_URL,
    MEASUREREPORT_POPULATION_DESCRIPTION_URL,
    MEASUREREPORT_CATEGORY_URL,
    MEASUREREPORT_COUNT_QUANTITY_URL,
    MEDICATION_MANUFACTURING_BATCH_URL,
    MEDICATIONDISPENSE_REFILLS_REMAINING_URL,
    MEDICATIONDISPENSE_QUANTITY_REMAINING_URL,
    MESSAGEHEADER_RESPONSE_REQUEST_URL,
    LAST_SOURCE_SYNC_URL,
    TIMEZONE_URL,
    FIRST_CREATED_URL,
    METADATARESOURCE_PUBLISH_DATE_URL,
    NAMINGSYSTEM_CHECK_DIGIT_URL,
    REQUEST_INSURANCE_URL,
    REQUEST_DO_NOT_PERFORM_URL,
    REQUEST_REPLACES_URL,
    NUTRITIONORDER_ADAPTIVE_FEEDING_DEVICE_URL,
    OBSERVATION_BODY_POSITION_URL,
    OBSERVATION_SPECIMEN_CODE_URL,
    OBSERVATION_NATURE_OF_ABNORMAL_TEST_URL,
    OBSERVATION_ANALYSIS_DATE_TIME_URL,
    OBSERVATION_REAGENT_URL,
    OBSERVATION_REPLACES_URL,
    OBSERVATION_V2_SUBID_URL,
    OBSERVATION_DEVICE_CODE_URL,
    OBSERVATION_SEQUEL_TO_URL,
    OBSERVATION_PRECONDITION_URL,
    OBSERVATION_DELTA_URL,
    OBSERVATION_FOCUS_CODE_URL,
    OBSERVATION_SECONDARY_FINDING_URL,
    OBSERVATION_GATEWAY_DEVICE_URL,
    OBSERVATION_TIME_OFFSET_URL,
    OPERATIONDEFINITION_PROFILE_URL,
    OPERATIONOUTCOME_FILE_URL,
    OPERATIONOUTCOME_ISSUE_SOURCE_URL,
    OPERATIONOUTCOME_DETECTED_ISSUE_URL,
    OPERATIONOUTCOME_ISSUE_COL_URL,
    OPERATIONOUTCOME_ISSUE_SLICETEXT_URL,
    OPERATIONOUTCOME_MESSAGE_ID_URL,
    OPERATIONOUTCOME_ISSUE_SERVER_URL,
    OPERATIONOUTCOME_ISSUE_LINE_URL,
    OPERATIONOUTCOME_AUTHORITY_URL,
    ORGANIZATION_PREFERRED_CONTACT_URL,
    ORGANIZATION_BRAND_URL,
    ORGANIZATION_PERIOD_URL,
    ORGANIZATION_PORTAL_URL,
    ORGANIZATIONAFFILIATION_PRIMARY_IND_URL,
    CQF_CQL_ACCESS_MODIFIER_URL,
    CQF_CQL_TYPE_URL,
    CQF_IS_PREFETCH_TOKEN_URL,
    CQF_DEFAULT_VALUE_URL,
    PARAMETERS_FULL_URL_URL,
    PARAMETERS_DEFINITION_URL,
    PATIENT_PROFICIENCY_URL,
    PATIENT_MULTIPLE_BIRTH_TOTAL_URL,
    PATIENT_IMPORTANCE_URL,
    PATIENT_CONGREGATION_URL,
    PATIENT_DISABILITY_URL,
    PATIENT_MOTHERS_MAIDEN_NAME_URL,
    PATIENT_CONTACT_PRIORITY_URL,
    PATIENT_BIRTH_PLACE_URL,
    PATIENT_PREFERENCE_TYPE_URL,
    PATIENT_RELIGION_URL,
    PATIENT_RELATED_PERSON_URL,
    INDIVIDUAL_PRONOUNS_URL,
    PATIENT_KNOWN_NON_DUPLICATE_URL,
    PATIENT_BIRTH_TIME_URL,
    INDIVIDUAL_GENDER_IDENTITY_URL,
    PATIENT_NATIONALITY_URL,
    PATIENT_BORN_STATUS_URL,
    PATIENT_ADOPTION_INFO_URL,
    PATIENT_UNKNOWN_IDENTITY_URL,
    PATIENT_CADAVERIC_DONOR_URL,
    PATIENT_ANIMAL_URL,
    PATIENT_CITIZENSHIP_URL,
    PATIENT_INTERPRETER_REQUIRED_URL,
    INDIVIDUAL_RECORDED_SEX_OR_GENDER_URL,
    ARTIFACT_PERIOD_DURATION_URL,
    TIMING_DAYS_OF_CYCLE_URL,
    CQF_CDS_HOOKS_ENDPOINT_URL,
    CQF_STRENGTH_OF_RECOMMENDATION_URL,
    CQF_QUALITY_OF_EVIDENCE_URL,
    PRACTITIONER_JOB_TITLE_URL,
    PRACTITIONER_ANIMAL_SPECIES_URL,
    PRACTITIONERROLE_EMPLOYMENT_STATUS_URL,
    PRACTITIONERROLE_PRIMARY_IND_URL,
    PROCEDURE_PROGRESS_STATUS_URL,
    PROCEDURE_DIRECTED_BY_URL,
    PROCEDURE_CAUSED_BY_URL,
    PROCEDURE_METHOD_URL,
    PROCEDURE_TARGET_BODY_STRUCTURE_URL,
    PROCEDURE_INCISION_DATE_TIME_URL,
    ISO21090_UNCERTAINTY_TYPE_URL,
    ISO21090_UNCERTAINTY_URL,
    QUANTITY_TRANSLATION_URL,
    QUESTIONNAIRE_FHIR_TYPE_URL,
    ELEMENTDEFINITION_CONCEPTMAP_URL,
    QUESTIONNAIRE_REFERENCE_FILTER_URL,
    MAX_VALUE_URL,
    QUESTIONNAIRE_DERIVATION_TYPE_URL,
    QUESTIONNAIRE_UNIT_URL,
    QUESTIONNAIRE_MIN_OCCURS_URL,
    QUESTIONNAIRE_UNIT_OPTION_URL,
    EXT_11179_PERMITTED_VALUE_VALUESET_URL,
    QUESTIONNAIRE_UNIT_VALUE_SET_URL,
    QUESTIONNAIRE_OPTION_EXCLUSIVE_URL,
    QUESTIONNAIRE_OPTION_RESTRICTION_URL,
    QUESTIONNAIRE_MAX_OCCURS_URL,
    EXT_11179_PERMITTED_VALUE_CONCEPTMAP_URL,
    QUESTIONNAIRE_DEFINITION_BASED_URL,
    MIN_VALUE_URL,
    QUESTIONNAIRE_DISPLAY_CATEGORY_URL,
    QUESTIONNAIRE_REFERENCE_RESOURCE_URL,
    QUESTIONNAIRE_CHOICE_ORIENTATION_URL,
    QUESTIONNAIRE_REFERENCE_PROFILE_URL,
    QUESTIONNAIRE_OPTION_PREFIX_URL,
    QUESTIONNAIRE_SLIDER_STEP_VALUE_URL,
    QUESTIONNAIRERESPONSE_REASON_URL,
    QUESTIONNAIRERESPONSE_REVIEWER_URL,
    QUESTIONNAIRERESPONSE_AUTHOR_URL,
    QUESTIONNAIRERESPONSE_COMPLETION_MODE_URL,
    QUESTIONNAIRERESPONSE_SIGNATURE_URL,
    QUESTIONNAIRERESPONSE_ATTESTER_URL,
    TARGET_PATH_URL,
    RESOLVE_AS_VERSION_SPECIFIC_URL,
    ARTIFACT_URI_REFERENCE_URL,
    ADDITIONAL_IDENTIFIER_URL,
    ALTERNATE_REFERENCE_URL,
    CQF_MEASURE_INFO_URL,
    TARGET_ELEMENT_URL,
    CQF_IS_PRIMARY_CITATION_URL,
    CQF_PUBLICATION_STATUS_URL,
    CQF_PUBLICATION_DATE_URL,
    REQUIREMENTS_PARENT_URL,
    RESEARCH_STUDY_STUDY_REGISTRATION_URL,
    RESEARCH_STUDY_SITE_RECRUITMENT_URL,
    ARTIFACT_CITE_AS_URL,
    CQF_ARTIFACT_COMMENT_URL,
    PATIENT_SEX_PARAMETER_FOR_CLINICAL_USE_URL,
    ARTIFACT_RELEASE_DESCRIPTION_URL,
    ARTIFACT_EXPERIMENTAL_URL,
    ARTIFACTASSESSMENT_DISPOSITION_URL,
    RESOURCE_PERTAINS_TO_GOAL_URL,
    ARTIFACT_DESCRIPTION_URL,
    CQF_SCOPE_URL,
    ARTIFACT_TITLE_URL,
    ARTIFACT_CONTACT_URL,
    ARTIFACT_LAST_REVIEW_DATE_URL,
    ARTIFACT_AUTHOR_URL,
    ARTIFACT_COPYRIGHT_LABEL_URL,
    ARTIFACT_IDENTIFIER_URL,
    ARTIFACTASSESSMENT_WORKFLOW_STATUS_URL,
    ARTIFACT_EFFECTIVE_PERIOD_URL,
    ARTIFACT_COPYRIGHT_URL,
    ARTIFACT_PURPOSE_URL,
    ARTIFACT_RELATED_ARTIFACT_URL,
    CQF_DIRECT_REFERENCE_CODE_URL,
    ARTIFACT_USAGE_URL,
    ARTIFACT_NAME_URL,
    ARTIFACT_JURISDICTION_URL,
    CQF_DEFINITION_TERM_URL,
    ARTIFACT_USE_CONTEXT_URL,
    ARTIFACT_RELEASE_LABEL_URL,
    ARTIFACT_VERSION_URL,
    ARTIFACT_URL_URL,
    RESOURCE_INSTANCE_DESCRIPTION_URL,
    ARTIFACT_VERSION_ALGORITHM_URL,
    ARTIFACT_PUBLISHER_URL,
    ARTIFACT_APPROVAL_DATE_URL,
    ARTIFACT_TOPIC_URL,
    CQF_MESSAGES_URL,
    ARTIFACT_DATE_URL,
    ARTIFACT_STATUS_URL,
    RESOURCE_INSTANCE_NAME_URL,
    ARTIFACT_VERSION_POLICY_URL,
    SERVICEREQUEST_PRECONDITION_URL,
    SERVICEREQUEST_QUESTIONNAIRE_REQUEST_URL,
    REQUEST_PERFORMER_ORDER_URL,
    SERVICEREQUEST_ORDER_CALLBACK_PHONE_NUMBER_URL,
    SPECIMEN_SEQUENCE_NUMBER_URL,
    SPECIMEN_IS_DRY_WEIGHT_URL,
    SPECIMEN_ADDITIVE_URL,
    SPECIMEN_SPECIAL_HANDLING_URL,
    SPECIMEN_COLLECTION_PRIORITY_URL,
    SPECIMEN_REJECT_REASON_URL,
    SPECIMEN_PROCESSING_TIME_URL,
    STRUCTUREDEFINITION_TYPE_CHARACTERISTICS_URL,
    STRUCTUREDEFINITION_COMPLIES_WITH_PROFILE_URL,
    STRUCTUREDEFINITION_CATEGORY_URL,
    CQF_MODEL_INFO_PRIMARY_CODE_PATH_URL,
    STRUCTUREDEFINITION_SECURITY_CATEGORY_URL,
    STRUCTUREDEFINITION_ANCESTOR_URL,
    STRUCTUREDEFINITION_INHERITANCE_CONTROL_URL,
    STRUCTUREDEFINITION_FMM_NO_WARNINGS_URL,
    STRUCTUREDEFINITION_TEMPLATE_STATUS_URL,
    STRUCTUREDEFINITION_SUMMARY_URL,
    CQF_MODEL_INFO_IS_RETRIEVABLE_URL,
    STRUCTUREDEFINITION_IMPOSE_PROFILE_URL,
    STRUCTUREDEFINITION_INTERFACE_URL,
    CQF_MODEL_INFO_LABEL_URL,
    CQF_MODEL_INFO_IS_INCLUDED_URL,
    STRUCTUREDEFINITION_CODEGEN_SUPER_URL,
    STRUCTUREDEFINITION_TABLE_NAME_URL,
    STRUCTUREDEFINITION_APPLICABLE_VERSION_URL,
    SUBSCRIPTION_BEST_EFFORT_URL,
    TASK_REPLACES_URL,
    TIMING_DAY_OF_MONTH_URL,
    TIMING_EXACT_URL,
    CQF_PARAMETER_DEFINITION_URL,
    USAGECONTEXT_GROUP_URL,
    VALUESET_UNCLOSED_URL,
    VALUESET_COMPOSE_CREATED_BY_URL,
    VALUESET_CONCEPT_ORDER_URL,
    VALUESET_LABEL_URL,
    VALUESET_TOOCOSTLY_URL,
    VALUESET_MAP_URL,
    VALUESET_SYSTEM_REF_URL,
    VALUESET_COMPOSE_CREATION_DATE_URL,
    VALUESET_CONCEPT_DEFINITION_URL,
    VALUESET_CONCEPT_COMMENTS_URL,
    VALUESET_SOURCE_REFERENCE_URL,
    VALUESET_COMPOSE_INCLUDE_VALUE_SET_TITLE_URL,
    VALUESET_SYSTEM_NAME_URL,
    VALUESET_PARAMETER_SOURCE_URL,
    VALUESET_EXPANSION_SOURCE_URL,
    VALUESET_SYSTEM_URL,
    VALUESET_WARNING_URL,
    VALUESET_CASE_SENSITIVE_URL,
    VALUESET_TRUSTED_EXPANSION_URL,
    VALUESET_EXPRESSION_URL,
    VALUESET_SUPPLEMENT_URL,
    VALUESET_AUTHORITATIVE_SOURCE_URL,
    VALUESET_USAGE_URL,
    VALUESET_OTHER_TITLE_URL,
    VALUESET_DEPRECATED_URL,
    VALUESET_KEY_WORD_URL,
    VALUESET_WORKFLOW_STATUS_DESCRIPTION_URL,
    VALUESET_SYSTEM_TITLE_URL,
    VALUESET_EXTENSIBLE_URL,
    VALUESET_OTHER_NAME_URL,
    VALUESET_RULES_TEXT_URL,
)

class Account(base.Account):

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

class ActivityDefinition(base.ActivityDefinition):

    @property
    def artifact_is_owned(self) -> Any:
        return get_extension(self, ARTIFACT_IS_OWNED_URL)

    @artifact_is_owned.setter
    def artifact_is_owned(self, value: Any) -> None:
        set_extension(self, ARTIFACT_IS_OWNED_URL, value)

    @property
    def cqf_target_invariant(self) -> Any:
        return get_extension(self, CQF_TARGET_INVARIANT_URL)

    @cqf_target_invariant.setter
    def cqf_target_invariant(self, value: Any) -> None:
        set_extension(self, CQF_TARGET_INVARIANT_URL, value)

    @property
    def target_constraint(self) -> Any:
        return get_extension(self, TARGET_CONSTRAINT_URL)

    @target_constraint.setter
    def target_constraint(self, value: Any) -> None:
        set_extension(self, TARGET_CONSTRAINT_URL, value)

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

    @property
    def variable(self) -> Any:
        return get_extension(self, VARIABLE_URL)

    @variable.setter
    def variable(self, value: Any) -> None:
        set_extension(self, VARIABLE_URL, value)

    @property
    def workflow_shall_comply_with(self) -> Any:
        return get_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL)

    @workflow_shall_comply_with.setter
    def workflow_shall_comply_with(self, value: Any) -> None:
        set_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL, value)

class ActorDefinition(base.ActorDefinition):

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class Address(base.Address):

    @property
    def iso21090_adxp_post_box(self) -> Any:
        return get_extension(self, ISO21090_ADXP_POST_BOX_URL)

    @iso21090_adxp_post_box.setter
    def iso21090_adxp_post_box(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_POST_BOX_URL, value)

    @property
    def extended_contact_availability(self) -> Any:
        return get_extension(self, EXTENDED_CONTACT_AVAILABILITY_URL)

    @extended_contact_availability.setter
    def extended_contact_availability(self, value: Any) -> None:
        set_extension(self, EXTENDED_CONTACT_AVAILABILITY_URL, value)

    @property
    def iso21090_adxp_street_name(self) -> Any:
        return get_extension(self, ISO21090_ADXP_STREET_NAME_URL)

    @iso21090_adxp_street_name.setter
    def iso21090_adxp_street_name(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_STREET_NAME_URL, value)

    @property
    def iso21090_adxp_unit_id(self) -> Any:
        return get_extension(self, ISO21090_ADXP_UNIT_ID_URL)

    @iso21090_adxp_unit_id.setter
    def iso21090_adxp_unit_id(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_UNIT_ID_URL, value)

    @property
    def address_official(self) -> Any:
        return get_extension(self, ADDRESS_OFFICIAL_URL)

    @address_official.setter
    def address_official(self, value: Any) -> None:
        set_extension(self, ADDRESS_OFFICIAL_URL, value)

    @property
    def iso21090_adxp_street_name_base(self) -> Any:
        return get_extension(self, ISO21090_ADXP_STREET_NAME_BASE_URL)

    @iso21090_adxp_street_name_base.setter
    def iso21090_adxp_street_name_base(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_STREET_NAME_BASE_URL, value)

    @property
    def iso21090_adxp_unit_type(self) -> Any:
        return get_extension(self, ISO21090_ADXP_UNIT_TYPE_URL)

    @iso21090_adxp_unit_type.setter
    def iso21090_adxp_unit_type(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_UNIT_TYPE_URL, value)

    @property
    def iso21090_adxp_street_name_type(self) -> Any:
        return get_extension(self, ISO21090_ADXP_STREET_NAME_TYPE_URL)

    @iso21090_adxp_street_name_type.setter
    def iso21090_adxp_street_name_type(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_STREET_NAME_TYPE_URL, value)

    @property
    def confidential(self) -> Any:
        return get_extension(self, CONFIDENTIAL_URL)

    @confidential.setter
    def confidential(self, value: Any) -> None:
        set_extension(self, CONFIDENTIAL_URL, value)

    @property
    def iso21090_adxp_additional_locator(self) -> Any:
        return get_extension(self, ISO21090_ADXP_ADDITIONAL_LOCATOR_URL)

    @iso21090_adxp_additional_locator.setter
    def iso21090_adxp_additional_locator(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_ADDITIONAL_LOCATOR_URL, value)

    @property
    def language(self) -> Any:
        return get_extension(self, LANGUAGE_URL)

    @language.setter
    def language(self, value: Any) -> None:
        set_extension(self, LANGUAGE_URL, value)

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

    @property
    def geolocation(self) -> Any:
        return get_extension(self, GEOLOCATION_URL)

    @geolocation.setter
    def geolocation(self, value: Any) -> None:
        set_extension(self, GEOLOCATION_URL, value)

    @property
    def iso21090_adxp_house_number(self) -> Any:
        return get_extension(self, ISO21090_ADXP_HOUSE_NUMBER_URL)

    @iso21090_adxp_house_number.setter
    def iso21090_adxp_house_number(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_HOUSE_NUMBER_URL, value)

    @property
    def no_fixed_address(self) -> Any:
        return get_extension(self, NO_FIXED_ADDRESS_URL)

    @no_fixed_address.setter
    def no_fixed_address(self, value: Any) -> None:
        set_extension(self, NO_FIXED_ADDRESS_URL, value)

    @property
    def iso21090_adxp_delivery_mode_identifier(self) -> Any:
        return get_extension(self, ISO21090_ADXP_DELIVERY_MODE_IDENTIFIER_URL)

    @iso21090_adxp_delivery_mode_identifier.setter
    def iso21090_adxp_delivery_mode_identifier(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_DELIVERY_MODE_IDENTIFIER_URL, value)

    @property
    def iso21090_adxp_delivery_installation_area(self) -> Any:
        return get_extension(self, ISO21090_ADXP_DELIVERY_INSTALLATION_AREA_URL)

    @iso21090_adxp_delivery_installation_area.setter
    def iso21090_adxp_delivery_installation_area(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_DELIVERY_INSTALLATION_AREA_URL, value)

    @property
    def iso21090_adxp_delivery_address_line(self) -> Any:
        return get_extension(self, ISO21090_ADXP_DELIVERY_ADDRESS_LINE_URL)

    @iso21090_adxp_delivery_address_line.setter
    def iso21090_adxp_delivery_address_line(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_DELIVERY_ADDRESS_LINE_URL, value)

    @property
    def iso21090_adxp_delivery_installation_qualifier(self) -> Any:
        return get_extension(self, ISO21090_ADXP_DELIVERY_INSTALLATION_QUALIFIER_URL)

    @iso21090_adxp_delivery_installation_qualifier.setter
    def iso21090_adxp_delivery_installation_qualifier(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_DELIVERY_INSTALLATION_QUALIFIER_URL, value)

    @property
    def iso21090_adxp_street_address_line(self) -> Any:
        return get_extension(self, ISO21090_ADXP_STREET_ADDRESS_LINE_URL)

    @iso21090_adxp_street_address_line.setter
    def iso21090_adxp_street_address_line(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_STREET_ADDRESS_LINE_URL, value)

    @property
    def iso21090_adxp_care_of(self) -> Any:
        return get_extension(self, ISO21090_ADXP_CARE_OF_URL)

    @iso21090_adxp_care_of.setter
    def iso21090_adxp_care_of(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_CARE_OF_URL, value)

    @property
    def iso21090_adxp_delivery_mode(self) -> Any:
        return get_extension(self, ISO21090_ADXP_DELIVERY_MODE_URL)

    @iso21090_adxp_delivery_mode.setter
    def iso21090_adxp_delivery_mode(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_DELIVERY_MODE_URL, value)

    @property
    def iso21090_adxp_house_number_numeric(self) -> Any:
        return get_extension(self, ISO21090_ADXP_HOUSE_NUMBER_NUMERIC_URL)

    @iso21090_adxp_house_number_numeric.setter
    def iso21090_adxp_house_number_numeric(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_HOUSE_NUMBER_NUMERIC_URL, value)

    @property
    def iso21090_adxp_delimiter(self) -> Any:
        return get_extension(self, ISO21090_ADXP_DELIMITER_URL)

    @iso21090_adxp_delimiter.setter
    def iso21090_adxp_delimiter(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_DELIMITER_URL, value)

    @property
    def iso21090_adxp_delivery_installation_type(self) -> Any:
        return get_extension(self, ISO21090_ADXP_DELIVERY_INSTALLATION_TYPE_URL)

    @iso21090_adxp_delivery_installation_type.setter
    def iso21090_adxp_delivery_installation_type(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_DELIVERY_INSTALLATION_TYPE_URL, value)

    @property
    def iso21090_adxp_building_number_suffix(self) -> Any:
        return get_extension(self, ISO21090_ADXP_BUILDING_NUMBER_SUFFIX_URL)

    @iso21090_adxp_building_number_suffix.setter
    def iso21090_adxp_building_number_suffix(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_BUILDING_NUMBER_SUFFIX_URL, value)

    @property
    def iso21090_preferred(self) -> Any:
        return get_extension(self, ISO21090_PREFERRED_URL)

    @iso21090_preferred.setter
    def iso21090_preferred(self, value: Any) -> None:
        set_extension(self, ISO21090_PREFERRED_URL, value)

    @property
    def iso21090_ad_use(self) -> Any:
        return get_extension(self, ISO21090_AD_USE_URL)

    @iso21090_ad_use.setter
    def iso21090_ad_use(self, value: Any) -> None:
        set_extension(self, ISO21090_AD_USE_URL, value)

    @property
    def iso21090_adxp_precinct(self) -> Any:
        return get_extension(self, ISO21090_ADXP_PRECINCT_URL)

    @iso21090_adxp_precinct.setter
    def iso21090_adxp_precinct(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_PRECINCT_URL, value)

    @property
    def iso21090_adxp_direction(self) -> Any:
        return get_extension(self, ISO21090_ADXP_DIRECTION_URL)

    @iso21090_adxp_direction.setter
    def iso21090_adxp_direction(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_DIRECTION_URL, value)

    @property
    def iso21090_adxp_census_tract(self) -> Any:
        return get_extension(self, ISO21090_ADXP_CENSUS_TRACT_URL)

    @iso21090_adxp_census_tract.setter
    def iso21090_adxp_census_tract(self, value: Any) -> None:
        set_extension(self, ISO21090_ADXP_CENSUS_TRACT_URL, value)

class AdverseEvent(base.AdverseEvent):

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

class Age(base.Age):

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

class AllergyIntolerance(base.AllergyIntolerance):

    @property
    def allergyintolerance_duration(self) -> Any:
        return get_extension(self, ALLERGYINTOLERANCE_DURATION_URL)

    @allergyintolerance_duration.setter
    def allergyintolerance_duration(self, value: Any) -> None:
        set_extension(self, ALLERGYINTOLERANCE_DURATION_URL, value)

    @property
    def open_ehr_exposure_description(self) -> Any:
        return get_extension(self, OPEN_EHR_EXPOSURE_DESCRIPTION_URL)

    @open_ehr_exposure_description.setter
    def open_ehr_exposure_description(self, value: Any) -> None:
        set_extension(self, OPEN_EHR_EXPOSURE_DESCRIPTION_URL, value)

    @property
    def open_ehr_careplan(self) -> Any:
        return get_extension(self, OPEN_EHR_CAREPLAN_URL)

    @open_ehr_careplan.setter
    def open_ehr_careplan(self, value: Any) -> None:
        set_extension(self, OPEN_EHR_CAREPLAN_URL, value)

    @property
    def open_ehr_location(self) -> Any:
        return get_extension(self, OPEN_EHR_LOCATION_URL)

    @open_ehr_location.setter
    def open_ehr_location(self, value: Any) -> None:
        set_extension(self, OPEN_EHR_LOCATION_URL, value)

    @property
    def allergyintolerance_substance_exposure_risk(self) -> Any:
        return get_extension(self, ALLERGYINTOLERANCE_SUBSTANCE_EXPOSURE_RISK_URL)

    @allergyintolerance_substance_exposure_risk.setter
    def allergyintolerance_substance_exposure_risk(self, value: Any) -> None:
        set_extension(self, ALLERGYINTOLERANCE_SUBSTANCE_EXPOSURE_RISK_URL, value)

    @property
    def allergyintolerance_abatement(self) -> Any:
        return get_extension(self, ALLERGYINTOLERANCE_ABATEMENT_URL)

    @allergyintolerance_abatement.setter
    def allergyintolerance_abatement(self, value: Any) -> None:
        set_extension(self, ALLERGYINTOLERANCE_ABATEMENT_URL, value)

    @property
    def allergyintolerance_reason_refuted(self) -> Any:
        return get_extension(self, ALLERGYINTOLERANCE_REASON_REFUTED_URL)

    @allergyintolerance_reason_refuted.setter
    def allergyintolerance_reason_refuted(self, value: Any) -> None:
        set_extension(self, ALLERGYINTOLERANCE_REASON_REFUTED_URL, value)

    @property
    def open_ehr_exposure_duration(self) -> Any:
        return get_extension(self, OPEN_EHR_EXPOSURE_DURATION_URL)

    @open_ehr_exposure_duration.setter
    def open_ehr_exposure_duration(self, value: Any) -> None:
        set_extension(self, OPEN_EHR_EXPOSURE_DURATION_URL, value)

    @property
    def allergyintolerance_resolution_age(self) -> Any:
        return get_extension(self, ALLERGYINTOLERANCE_RESOLUTION_AGE_URL)

    @allergyintolerance_resolution_age.setter
    def allergyintolerance_resolution_age(self, value: Any) -> None:
        set_extension(self, ALLERGYINTOLERANCE_RESOLUTION_AGE_URL, value)

    @property
    def open_ehr_management(self) -> Any:
        return get_extension(self, OPEN_EHR_MANAGEMENT_URL)

    @open_ehr_management.setter
    def open_ehr_management(self, value: Any) -> None:
        set_extension(self, OPEN_EHR_MANAGEMENT_URL, value)

    @property
    def open_ehr_exposure_date(self) -> Any:
        return get_extension(self, OPEN_EHR_EXPOSURE_DATE_URL)

    @open_ehr_exposure_date.setter
    def open_ehr_exposure_date(self, value: Any) -> None:
        set_extension(self, OPEN_EHR_EXPOSURE_DATE_URL, value)

    @property
    def condition_asserted_date(self) -> Any:
        return get_extension(self, CONDITION_ASSERTED_DATE_URL)

    @condition_asserted_date.setter
    def condition_asserted_date(self, value: Any) -> None:
        set_extension(self, CONDITION_ASSERTED_DATE_URL, value)

    @property
    def allergyintolerance_certainty(self) -> Any:
        return get_extension(self, ALLERGYINTOLERANCE_CERTAINTY_URL)

    @allergyintolerance_certainty.setter
    def allergyintolerance_certainty(self, value: Any) -> None:
        set_extension(self, ALLERGYINTOLERANCE_CERTAINTY_URL, value)

    @property
    def allergyintolerance_asserted_date(self) -> Any:
        return get_extension(self, ALLERGYINTOLERANCE_ASSERTED_DATE_URL)

    @allergyintolerance_asserted_date.setter
    def allergyintolerance_asserted_date(self, value: Any) -> None:
        set_extension(self, ALLERGYINTOLERANCE_ASSERTED_DATE_URL, value)

    @property
    def open_ehr_administration(self) -> Any:
        return get_extension(self, OPEN_EHR_ADMINISTRATION_URL)

    @open_ehr_administration.setter
    def open_ehr_administration(self, value: Any) -> None:
        set_extension(self, OPEN_EHR_ADMINISTRATION_URL, value)

class Annotation(base.Annotation):

    @property
    def language(self) -> Any:
        return get_extension(self, LANGUAGE_URL)

    @language.setter
    def language(self, value: Any) -> None:
        set_extension(self, LANGUAGE_URL, value)

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

    @property
    def annotation_type(self) -> Any:
        return get_extension(self, ANNOTATION_TYPE_URL)

    @annotation_type.setter
    def annotation_type(self, value: Any) -> None:
        set_extension(self, ANNOTATION_TYPE_URL, value)

class Appointment(base.Appointment):

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

class ArtifactAssessment(base.ArtifactAssessment):

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

class Attachment(base.Attachment):

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

class AuditEvent(base.AuditEvent):

    @property
    def auditevent_participant_object_contains_study(self) -> Any:
        return get_extension(self, AUDITEVENT_PARTICIPANT_OBJECT_CONTAINS_STUDY_URL)

    @auditevent_participant_object_contains_study.setter
    def auditevent_participant_object_contains_study(self, value: Any) -> None:
        set_extension(self, AUDITEVENT_PARTICIPANT_OBJECT_CONTAINS_STUDY_URL, value)

    @property
    def auditevent_mpps(self) -> Any:
        return get_extension(self, AUDITEVENT_MPPS_URL)

    @auditevent_mpps.setter
    def auditevent_mpps(self, value: Any) -> None:
        set_extension(self, AUDITEVENT_MPPS_URL, value)

    @property
    def auditevent_lifecycle(self) -> Any:
        return get_extension(self, AUDITEVENT_LIFECYCLE_URL)

    @auditevent_lifecycle.setter
    def auditevent_lifecycle(self, value: Any) -> None:
        set_extension(self, AUDITEVENT_LIFECYCLE_URL, value)

    @property
    def auditevent_anonymized(self) -> Any:
        return get_extension(self, AUDITEVENT_ANONYMIZED_URL)

    @auditevent_anonymized.setter
    def auditevent_anonymized(self, value: Any) -> None:
        set_extension(self, AUDITEVENT_ANONYMIZED_URL, value)

    @property
    def auditevent_instance(self) -> Any:
        return get_extension(self, AUDITEVENT_INSTANCE_URL)

    @auditevent_instance.setter
    def auditevent_instance(self, value: Any) -> None:
        set_extension(self, AUDITEVENT_INSTANCE_URL, value)

    @property
    def auditevent_accession(self) -> Any:
        return get_extension(self, AUDITEVENT_ACCESSION_URL)

    @auditevent_accession.setter
    def auditevent_accession(self, value: Any) -> None:
        set_extension(self, AUDITEVENT_ACCESSION_URL, value)

    @property
    def auditevent_on_behalf_of(self) -> Any:
        return get_extension(self, AUDITEVENT_ON_BEHALF_OF_URL)

    @auditevent_on_behalf_of.setter
    def auditevent_on_behalf_of(self, value: Any) -> None:
        set_extension(self, AUDITEVENT_ON_BEHALF_OF_URL, value)

    @property
    def auditevent_sopclass(self) -> Any:
        return get_extension(self, AUDITEVENT_SOPCLASS_URL)

    @auditevent_sopclass.setter
    def auditevent_sopclass(self, value: Any) -> None:
        set_extension(self, AUDITEVENT_SOPCLASS_URL, value)

    @property
    def auditevent_alternative_user_id(self) -> Any:
        return get_extension(self, AUDITEVENT_ALTERNATIVE_USER_ID_URL)

    @auditevent_alternative_user_id.setter
    def auditevent_alternative_user_id(self, value: Any) -> None:
        set_extension(self, AUDITEVENT_ALTERNATIVE_USER_ID_URL, value)

    @property
    def auditevent_encrypted(self) -> Any:
        return get_extension(self, AUDITEVENT_ENCRYPTED_URL)

    @auditevent_encrypted.setter
    def auditevent_encrypted(self, value: Any) -> None:
        set_extension(self, AUDITEVENT_ENCRYPTED_URL, value)

    @property
    def auditevent_number_of_instances(self) -> Any:
        return get_extension(self, AUDITEVENT_NUMBER_OF_INSTANCES_URL)

    @auditevent_number_of_instances.setter
    def auditevent_number_of_instances(self, value: Any) -> None:
        set_extension(self, AUDITEVENT_NUMBER_OF_INSTANCES_URL, value)

class Base(base.Base):

    @property
    def _datatype(self) -> Any:
        return get_extension(self, _DATATYPE_URL)

    @_datatype.setter
    def _datatype(self, value: Any) -> None:
        set_extension(self, _DATATYPE_URL, value)

class Basic(base.Basic):

    @property
    def cqf_initiating_organization(self) -> Any:
        return get_extension(self, CQF_INITIATING_ORGANIZATION_URL)

    @cqf_initiating_organization.setter
    def cqf_initiating_organization(self, value: Any) -> None:
        set_extension(self, CQF_INITIATING_ORGANIZATION_URL, value)

    @property
    def cqf_initiating_person(self) -> Any:
        return get_extension(self, CQF_INITIATING_PERSON_URL)

    @cqf_initiating_person.setter
    def cqf_initiating_person(self, value: Any) -> None:
        set_extension(self, CQF_INITIATING_PERSON_URL, value)

    @property
    def cqf_system_user_language(self) -> Any:
        return get_extension(self, CQF_SYSTEM_USER_LANGUAGE_URL)

    @cqf_system_user_language.setter
    def cqf_system_user_language(self, value: Any) -> None:
        set_extension(self, CQF_SYSTEM_USER_LANGUAGE_URL, value)

    @property
    def cqf_recipient_type(self) -> Any:
        return get_extension(self, CQF_RECIPIENT_TYPE_URL)

    @cqf_recipient_type.setter
    def cqf_recipient_type(self, value: Any) -> None:
        set_extension(self, CQF_RECIPIENT_TYPE_URL, value)

    @property
    def cqf_encounter_class(self) -> Any:
        return get_extension(self, CQF_ENCOUNTER_CLASS_URL)

    @cqf_encounter_class.setter
    def cqf_encounter_class(self, value: Any) -> None:
        set_extension(self, CQF_ENCOUNTER_CLASS_URL, value)

    @property
    def cqf_recipient_language(self) -> Any:
        return get_extension(self, CQF_RECIPIENT_LANGUAGE_URL)

    @cqf_recipient_language.setter
    def cqf_recipient_language(self, value: Any) -> None:
        set_extension(self, CQF_RECIPIENT_LANGUAGE_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def artifactassessment_content(self) -> Any:
        return get_extension(self, ARTIFACTASSESSMENT_CONTENT_URL)

    @artifactassessment_content.setter
    def artifactassessment_content(self, value: Any) -> None:
        set_extension(self, ARTIFACTASSESSMENT_CONTENT_URL, value)

    @property
    def cqf_receiving_organization(self) -> Any:
        return get_extension(self, CQF_RECEIVING_ORGANIZATION_URL)

    @cqf_receiving_organization.setter
    def cqf_receiving_organization(self, value: Any) -> None:
        set_extension(self, CQF_RECEIVING_ORGANIZATION_URL, value)

    @property
    def cqf_receiving_person(self) -> Any:
        return get_extension(self, CQF_RECEIVING_PERSON_URL)

    @cqf_receiving_person.setter
    def cqf_receiving_person(self, value: Any) -> None:
        set_extension(self, CQF_RECEIVING_PERSON_URL, value)

    @property
    def cqf_system_user_type(self) -> Any:
        return get_extension(self, CQF_SYSTEM_USER_TYPE_URL)

    @cqf_system_user_type.setter
    def cqf_system_user_type(self, value: Any) -> None:
        set_extension(self, CQF_SYSTEM_USER_TYPE_URL, value)

    @property
    def cqf_encounter_type(self) -> Any:
        return get_extension(self, CQF_ENCOUNTER_TYPE_URL)

    @cqf_encounter_type.setter
    def cqf_encounter_type(self, value: Any) -> None:
        set_extension(self, CQF_ENCOUNTER_TYPE_URL, value)

    @property
    def cqf_system_user_task_context(self) -> Any:
        return get_extension(self, CQF_SYSTEM_USER_TASK_CONTEXT_URL)

    @cqf_system_user_task_context.setter
    def cqf_system_user_task_context(self, value: Any) -> None:
        set_extension(self, CQF_SYSTEM_USER_TASK_CONTEXT_URL, value)

class BiologicallyDerivedProduct(base.BiologicallyDerivedProduct):

    @property
    def biologicallyderivedproduct_collection_procedure(self) -> Any:
        return get_extension(self, BIOLOGICALLYDERIVEDPRODUCT_COLLECTION_PROCEDURE_URL)

    @biologicallyderivedproduct_collection_procedure.setter
    def biologicallyderivedproduct_collection_procedure(self, value: Any) -> None:
        set_extension(self, BIOLOGICALLYDERIVEDPRODUCT_COLLECTION_PROCEDURE_URL, value)

    @property
    def biologicallyderivedproduct_processing(self) -> Any:
        return get_extension(self, BIOLOGICALLYDERIVEDPRODUCT_PROCESSING_URL)

    @biologicallyderivedproduct_processing.setter
    def biologicallyderivedproduct_processing(self, value: Any) -> None:
        set_extension(self, BIOLOGICALLYDERIVEDPRODUCT_PROCESSING_URL, value)

    @property
    def biologicallyderivedproduct_manipulation(self) -> Any:
        return get_extension(self, BIOLOGICALLYDERIVEDPRODUCT_MANIPULATION_URL)

    @biologicallyderivedproduct_manipulation.setter
    def biologicallyderivedproduct_manipulation(self, value: Any) -> None:
        set_extension(self, BIOLOGICALLYDERIVEDPRODUCT_MANIPULATION_URL, value)

class Bundle(base.Bundle):

    @property
    def http_response_header(self) -> Any:
        return get_extension(self, HTTP_RESPONSE_HEADER_URL)

    @http_response_header.setter
    def http_response_header(self, value: Any) -> None:
        set_extension(self, HTTP_RESPONSE_HEADER_URL, value)

    @property
    def location_distance(self) -> Any:
        return get_extension(self, LOCATION_DISTANCE_URL)

    @location_distance.setter
    def location_distance(self, value: Any) -> None:
        set_extension(self, LOCATION_DISTANCE_URL, value)

    @property
    def match_grade(self) -> Any:
        return get_extension(self, MATCH_GRADE_URL)

    @match_grade.setter
    def match_grade(self, value: Any) -> None:
        set_extension(self, MATCH_GRADE_URL, value)

class CanonicalResource(base.CanonicalResource):

    @property
    def structuredefinition_standards_status(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_STANDARDS_STATUS_URL)

    @structuredefinition_standards_status.setter
    def structuredefinition_standards_status(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_STANDARDS_STATUS_URL, value)

    @property
    def structuredefinition_normative_version(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_NORMATIVE_VERSION_URL)

    @structuredefinition_normative_version.setter
    def structuredefinition_normative_version(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_NORMATIVE_VERSION_URL, value)

    @property
    def canonicalresource_short_description(self) -> Any:
        return get_extension(self, CANONICALRESOURCE_SHORT_DESCRIPTION_URL)

    @canonicalresource_short_description.setter
    def canonicalresource_short_description(self, value: Any) -> None:
        set_extension(self, CANONICALRESOURCE_SHORT_DESCRIPTION_URL, value)

class CapabilityStatement(base.CapabilityStatement):

    @property
    def resource_approval_date(self) -> Any:
        return get_extension(self, RESOURCE_APPROVAL_DATE_URL)

    @resource_approval_date.setter
    def resource_approval_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_APPROVAL_DATE_URL, value)

    @property
    def capabilitystatement_search_mode(self) -> Any:
        return get_extension(self, CAPABILITYSTATEMENT_SEARCH_MODE_URL)

    @capabilitystatement_search_mode.setter
    def capabilitystatement_search_mode(self, value: Any) -> None:
        set_extension(self, CAPABILITYSTATEMENT_SEARCH_MODE_URL, value)

    @property
    def resource_last_review_date(self) -> Any:
        return get_extension(self, RESOURCE_LAST_REVIEW_DATE_URL)

    @resource_last_review_date.setter
    def resource_last_review_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_LAST_REVIEW_DATE_URL, value)

    @property
    def capabilitystatement_search_parameter_use(self) -> Any:
        return get_extension(self, CAPABILITYSTATEMENT_SEARCH_PARAMETER_USE_URL)

    @capabilitystatement_search_parameter_use.setter
    def capabilitystatement_search_parameter_use(self, value: Any) -> None:
        set_extension(self, CAPABILITYSTATEMENT_SEARCH_PARAMETER_USE_URL, value)

    @property
    def oauth_uris(self) -> Any:
        return get_extension(self, OAUTH_URIS_URL)

    @oauth_uris.setter
    def oauth_uris(self, value: Any) -> None:
        set_extension(self, OAUTH_URIS_URL, value)

    @property
    def capabilitystatement_expectation(self) -> Any:
        return get_extension(self, CAPABILITYSTATEMENT_EXPECTATION_URL)

    @capabilitystatement_expectation.setter
    def capabilitystatement_expectation(self, value: Any) -> None:
        set_extension(self, CAPABILITYSTATEMENT_EXPECTATION_URL, value)

    @property
    def capabilitystatement_declared_profile(self) -> Any:
        return get_extension(self, CAPABILITYSTATEMENT_DECLARED_PROFILE_URL)

    @capabilitystatement_declared_profile.setter
    def capabilitystatement_declared_profile(self, value: Any) -> None:
        set_extension(self, CAPABILITYSTATEMENT_DECLARED_PROFILE_URL, value)

    @property
    def resource_effective_period(self) -> Any:
        return get_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL)

    @resource_effective_period.setter
    def resource_effective_period(self, value: Any) -> None:
        set_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL, value)

    @property
    def cqf_supported_cql_version(self) -> Any:
        return get_extension(self, CQF_SUPPORTED_CQL_VERSION_URL)

    @cqf_supported_cql_version.setter
    def cqf_supported_cql_version(self, value: Any) -> None:
        set_extension(self, CQF_SUPPORTED_CQL_VERSION_URL, value)

    @property
    def capabilitystatement_prohibited(self) -> Any:
        return get_extension(self, CAPABILITYSTATEMENT_PROHIBITED_URL)

    @capabilitystatement_prohibited.setter
    def capabilitystatement_prohibited(self, value: Any) -> None:
        set_extension(self, CAPABILITYSTATEMENT_PROHIBITED_URL, value)

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

    @property
    def capabilitystatement_search_parameter_combination(self) -> Any:
        return get_extension(self, CAPABILITYSTATEMENT_SEARCH_PARAMETER_COMBINATION_URL)

    @capabilitystatement_search_parameter_combination.setter
    def capabilitystatement_search_parameter_combination(self, value: Any) -> None:
        set_extension(self, CAPABILITYSTATEMENT_SEARCH_PARAMETER_COMBINATION_URL, value)

    @property
    def capabilitystatement_supported_system(self) -> Any:
        return get_extension(self, CAPABILITYSTATEMENT_SUPPORTED_SYSTEM_URL)

    @capabilitystatement_supported_system.setter
    def capabilitystatement_supported_system(self, value: Any) -> None:
        set_extension(self, CAPABILITYSTATEMENT_SUPPORTED_SYSTEM_URL, value)

    @property
    def capabilities(self) -> Any:
        return get_extension(self, CAPABILITIES_URL)

    @capabilities.setter
    def capabilities(self, value: Any) -> None:
        set_extension(self, CAPABILITIES_URL, value)

    @property
    def capabilitystatement_websocket(self) -> Any:
        return get_extension(self, CAPABILITYSTATEMENT_WEBSOCKET_URL)

    @capabilitystatement_websocket.setter
    def capabilitystatement_websocket(self, value: Any) -> None:
        set_extension(self, CAPABILITYSTATEMENT_WEBSOCKET_URL, value)

class CarePlan(base.CarePlan):

    @property
    def workflow_triggered_by(self) -> Any:
        return get_extension(self, WORKFLOW_TRIGGERED_BY_URL)

    @workflow_triggered_by.setter
    def workflow_triggered_by(self, value: Any) -> None:
        set_extension(self, WORKFLOW_TRIGGERED_BY_URL, value)

    @property
    def workflow_generated_from(self) -> Any:
        return get_extension(self, WORKFLOW_GENERATED_FROM_URL)

    @workflow_generated_from.setter
    def workflow_generated_from(self, value: Any) -> None:
        set_extension(self, WORKFLOW_GENERATED_FROM_URL, value)

    @property
    def workflow_protective_factor(self) -> Any:
        return get_extension(self, WORKFLOW_PROTECTIVE_FACTOR_URL)

    @workflow_protective_factor.setter
    def workflow_protective_factor(self, value: Any) -> None:
        set_extension(self, WORKFLOW_PROTECTIVE_FACTOR_URL, value)

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

    @property
    def request_relevant_history(self) -> Any:
        return get_extension(self, REQUEST_RELEVANT_HISTORY_URL)

    @request_relevant_history.setter
    def request_relevant_history(self, value: Any) -> None:
        set_extension(self, REQUEST_RELEVANT_HISTORY_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def careplan_activity_title(self) -> Any:
        return get_extension(self, CAREPLAN_ACTIVITY_TITLE_URL)

    @careplan_activity_title.setter
    def careplan_activity_title(self, value: Any) -> None:
        set_extension(self, CAREPLAN_ACTIVITY_TITLE_URL, value)

    @property
    def workflow_barrier(self) -> Any:
        return get_extension(self, WORKFLOW_BARRIER_URL)

    @workflow_barrier.setter
    def workflow_barrier(self, value: Any) -> None:
        set_extension(self, WORKFLOW_BARRIER_URL, value)

    @property
    def workflow_complies_with(self) -> Any:
        return get_extension(self, WORKFLOW_COMPLIES_WITH_URL)

    @workflow_complies_with.setter
    def workflow_complies_with(self, value: Any) -> None:
        set_extension(self, WORKFLOW_COMPLIES_WITH_URL, value)

class CareTeam(base.CareTeam):

    @property
    def careteam_alias(self) -> Any:
        return get_extension(self, CARETEAM_ALIAS_URL)

    @careteam_alias.setter
    def careteam_alias(self, value: Any) -> None:
        set_extension(self, CARETEAM_ALIAS_URL, value)

class ChargeItem(base.ChargeItem):

    @property
    def event_based_on(self) -> Any:
        return get_extension(self, EVENT_BASED_ON_URL)

    @event_based_on.setter
    def event_based_on(self, value: Any) -> None:
        set_extension(self, EVENT_BASED_ON_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

class ChargeItemDefinition(base.ChargeItemDefinition):

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class Citation(base.Citation):

    @property
    def citation_society_affiliation(self) -> Any:
        return get_extension(self, CITATION_SOCIETY_AFFILIATION_URL)

    @citation_society_affiliation.setter
    def citation_society_affiliation(self, value: Any) -> None:
        set_extension(self, CITATION_SOCIETY_AFFILIATION_URL, value)

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class ClinicalImpression(base.ClinicalImpression):

    @property
    def event_based_on(self) -> Any:
        return get_extension(self, EVENT_BASED_ON_URL)

    @event_based_on.setter
    def event_based_on(self, value: Any) -> None:
        set_extension(self, EVENT_BASED_ON_URL, value)

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

class CodeSystem(base.CodeSystem):

    @property
    def codesystem_warning(self) -> Any:
        return get_extension(self, CODESYSTEM_WARNING_URL)

    @codesystem_warning.setter
    def codesystem_warning(self, value: Any) -> None:
        set_extension(self, CODESYSTEM_WARNING_URL, value)

    @property
    def resource_approval_date(self) -> Any:
        return get_extension(self, RESOURCE_APPROVAL_DATE_URL)

    @resource_approval_date.setter
    def resource_approval_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_APPROVAL_DATE_URL, value)

    @property
    def codesystem_alternate(self) -> Any:
        return get_extension(self, CODESYSTEM_ALTERNATE_URL)

    @codesystem_alternate.setter
    def codesystem_alternate(self, value: Any) -> None:
        set_extension(self, CODESYSTEM_ALTERNATE_URL, value)

    @property
    def codesystem_history(self) -> Any:
        return get_extension(self, CODESYSTEM_HISTORY_URL)

    @codesystem_history.setter
    def codesystem_history(self, value: Any) -> None:
        set_extension(self, CODESYSTEM_HISTORY_URL, value)

    @property
    def terminology_resource_identifier_metadata(self) -> Any:
        return get_extension(self, TERMINOLOGY_RESOURCE_IDENTIFIER_METADATA_URL)

    @terminology_resource_identifier_metadata.setter
    def terminology_resource_identifier_metadata(self, value: Any) -> None:
        set_extension(self, TERMINOLOGY_RESOURCE_IDENTIFIER_METADATA_URL, value)

    @property
    def codesystem_properties_mode(self) -> Any:
        return get_extension(self, CODESYSTEM_PROPERTIES_MODE_URL)

    @codesystem_properties_mode.setter
    def codesystem_properties_mode(self, value: Any) -> None:
        set_extension(self, CODESYSTEM_PROPERTIES_MODE_URL, value)

    @property
    def codesystem_trusted_expansion(self) -> Any:
        return get_extension(self, CODESYSTEM_TRUSTED_EXPANSION_URL)

    @codesystem_trusted_expansion.setter
    def codesystem_trusted_expansion(self, value: Any) -> None:
        set_extension(self, CODESYSTEM_TRUSTED_EXPANSION_URL, value)

    @property
    def codesystem_other_name(self) -> Any:
        return get_extension(self, CODESYSTEM_OTHER_NAME_URL)

    @codesystem_other_name.setter
    def codesystem_other_name(self, value: Any) -> None:
        set_extension(self, CODESYSTEM_OTHER_NAME_URL, value)

    @property
    def resource_last_review_date(self) -> Any:
        return get_extension(self, RESOURCE_LAST_REVIEW_DATE_URL)

    @resource_last_review_date.setter
    def resource_last_review_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_LAST_REVIEW_DATE_URL, value)

    @property
    def codesystem_authoritative_source(self) -> Any:
        return get_extension(self, CODESYSTEM_AUTHORITATIVE_SOURCE_URL)

    @codesystem_authoritative_source.setter
    def codesystem_authoritative_source(self, value: Any) -> None:
        set_extension(self, CODESYSTEM_AUTHORITATIVE_SOURCE_URL, value)

    @property
    def valueset_special_status(self) -> Any:
        return get_extension(self, VALUESET_SPECIAL_STATUS_URL)

    @valueset_special_status.setter
    def valueset_special_status(self, value: Any) -> None:
        set_extension(self, VALUESET_SPECIAL_STATUS_URL, value)

    @property
    def structuredefinition_standards_status(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_STANDARDS_STATUS_URL)

    @structuredefinition_standards_status.setter
    def structuredefinition_standards_status(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_STANDARDS_STATUS_URL, value)

    @property
    def resource_effective_period(self) -> Any:
        return get_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL)

    @resource_effective_period.setter
    def resource_effective_period(self, value: Any) -> None:
        set_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL, value)

    @property
    def codesystem_label(self) -> Any:
        return get_extension(self, CODESYSTEM_LABEL_URL)

    @codesystem_label.setter
    def codesystem_label(self, value: Any) -> None:
        set_extension(self, CODESYSTEM_LABEL_URL, value)

    @property
    def codesystem_concept_order(self) -> Any:
        return get_extension(self, CODESYSTEM_CONCEPT_ORDER_URL)

    @codesystem_concept_order.setter
    def codesystem_concept_order(self, value: Any) -> None:
        set_extension(self, CODESYSTEM_CONCEPT_ORDER_URL, value)

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

    @property
    def codesystem_key_word(self) -> Any:
        return get_extension(self, CODESYSTEM_KEY_WORD_URL)

    @codesystem_key_word.setter
    def codesystem_key_word(self, value: Any) -> None:
        set_extension(self, CODESYSTEM_KEY_WORD_URL, value)

    @property
    def codesystem_source_reference(self) -> Any:
        return get_extension(self, CODESYSTEM_SOURCE_REFERENCE_URL)

    @codesystem_source_reference.setter
    def codesystem_source_reference(self, value: Any) -> None:
        set_extension(self, CODESYSTEM_SOURCE_REFERENCE_URL, value)

    @property
    def codesystem_workflow_status(self) -> Any:
        return get_extension(self, CODESYSTEM_WORKFLOW_STATUS_URL)

    @codesystem_workflow_status.setter
    def codesystem_workflow_status(self, value: Any) -> None:
        set_extension(self, CODESYSTEM_WORKFLOW_STATUS_URL, value)

    @property
    def codesystem_replacedby(self) -> Any:
        return get_extension(self, CODESYSTEM_REPLACEDBY_URL)

    @codesystem_replacedby.setter
    def codesystem_replacedby(self, value: Any) -> None:
        set_extension(self, CODESYSTEM_REPLACEDBY_URL, value)

    @property
    def codesystem_usage(self) -> Any:
        return get_extension(self, CODESYSTEM_USAGE_URL)

    @codesystem_usage.setter
    def codesystem_usage(self, value: Any) -> None:
        set_extension(self, CODESYSTEM_USAGE_URL, value)

    @property
    def codesystem_use_markdown(self) -> Any:
        return get_extension(self, CODESYSTEM_USE_MARKDOWN_URL)

    @codesystem_use_markdown.setter
    def codesystem_use_markdown(self, value: Any) -> None:
        set_extension(self, CODESYSTEM_USE_MARKDOWN_URL, value)

    @property
    def codesystem_concept_comments(self) -> Any:
        return get_extension(self, CODESYSTEM_CONCEPT_COMMENTS_URL)

    @codesystem_concept_comments.setter
    def codesystem_concept_comments(self, value: Any) -> None:
        set_extension(self, CODESYSTEM_CONCEPT_COMMENTS_URL, value)

    @property
    def coding_sctdescid(self) -> Any:
        return get_extension(self, CODING_SCTDESCID_URL)

    @coding_sctdescid.setter
    def coding_sctdescid(self, value: Any) -> None:
        set_extension(self, CODING_SCTDESCID_URL, value)

    @property
    def codesystem_map(self) -> Any:
        return get_extension(self, CODESYSTEM_MAP_URL)

    @codesystem_map.setter
    def codesystem_map(self, value: Any) -> None:
        set_extension(self, CODESYSTEM_MAP_URL, value)

class CodeableConcept(base.CodeableConcept):

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

    @property
    def cqf_not_done_value_set(self) -> Any:
        return get_extension(self, CQF_NOT_DONE_VALUE_SET_URL)

    @cqf_not_done_value_set.setter
    def cqf_not_done_value_set(self, value: Any) -> None:
        set_extension(self, CQF_NOT_DONE_VALUE_SET_URL, value)

class Coding(base.Coding):

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

    @property
    def valueset_reference(self) -> Any:
        return get_extension(self, VALUESET_REFERENCE_URL)

    @valueset_reference.setter
    def valueset_reference(self, value: Any) -> None:
        set_extension(self, VALUESET_REFERENCE_URL, value)

    @property
    def item_weight(self) -> Any:
        return get_extension(self, ITEM_WEIGHT_URL)

    @item_weight.setter
    def item_weight(self, value: Any) -> None:
        set_extension(self, ITEM_WEIGHT_URL, value)

    @property
    def coding_conformance(self) -> Any:
        return get_extension(self, CODING_CONFORMANCE_URL)

    @coding_conformance.setter
    def coding_conformance(self, value: Any) -> None:
        set_extension(self, CODING_CONFORMANCE_URL, value)

    @property
    def coding_sctdescid(self) -> Any:
        return get_extension(self, CODING_SCTDESCID_URL)

    @coding_sctdescid.setter
    def coding_sctdescid(self, value: Any) -> None:
        set_extension(self, CODING_SCTDESCID_URL, value)

    @property
    def coding_purpose(self) -> Any:
        return get_extension(self, CODING_PURPOSE_URL)

    @coding_purpose.setter
    def coding_purpose(self, value: Any) -> None:
        set_extension(self, CODING_PURPOSE_URL, value)

class Communication(base.Communication):

    @property
    def workflow_triggered_by(self) -> Any:
        return get_extension(self, WORKFLOW_TRIGGERED_BY_URL)

    @workflow_triggered_by.setter
    def workflow_triggered_by(self, value: Any) -> None:
        set_extension(self, WORKFLOW_TRIGGERED_BY_URL, value)

    @property
    def communication_media(self) -> Any:
        return get_extension(self, COMMUNICATION_MEDIA_URL)

    @communication_media.setter
    def communication_media(self, value: Any) -> None:
        set_extension(self, COMMUNICATION_MEDIA_URL, value)

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def workflow_adheres_to(self) -> Any:
        return get_extension(self, WORKFLOW_ADHERES_TO_URL)

    @workflow_adheres_to.setter
    def workflow_adheres_to(self, value: Any) -> None:
        set_extension(self, WORKFLOW_ADHERES_TO_URL, value)

class CommunicationRequest(base.CommunicationRequest):

    @property
    def workflow_triggered_by(self) -> Any:
        return get_extension(self, WORKFLOW_TRIGGERED_BY_URL)

    @workflow_triggered_by.setter
    def workflow_triggered_by(self, value: Any) -> None:
        set_extension(self, WORKFLOW_TRIGGERED_BY_URL, value)

    @property
    def workflow_generated_from(self) -> Any:
        return get_extension(self, WORKFLOW_GENERATED_FROM_URL)

    @workflow_generated_from.setter
    def workflow_generated_from(self, value: Any) -> None:
        set_extension(self, WORKFLOW_GENERATED_FROM_URL, value)

    @property
    def workflow_protective_factor(self) -> Any:
        return get_extension(self, WORKFLOW_PROTECTIVE_FACTOR_URL)

    @workflow_protective_factor.setter
    def workflow_protective_factor(self, value: Any) -> None:
        set_extension(self, WORKFLOW_PROTECTIVE_FACTOR_URL, value)

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

    @property
    def request_relevant_history(self) -> Any:
        return get_extension(self, REQUEST_RELEVANT_HISTORY_URL)

    @request_relevant_history.setter
    def request_relevant_history(self, value: Any) -> None:
        set_extension(self, REQUEST_RELEVANT_HISTORY_URL, value)

    @property
    def workflow_supporting_info(self) -> Any:
        return get_extension(self, WORKFLOW_SUPPORTING_INFO_URL)

    @workflow_supporting_info.setter
    def workflow_supporting_info(self, value: Any) -> None:
        set_extension(self, WORKFLOW_SUPPORTING_INFO_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def communicationrequest_initiating_location(self) -> Any:
        return get_extension(self, COMMUNICATIONREQUEST_INITIATING_LOCATION_URL)

    @communicationrequest_initiating_location.setter
    def communicationrequest_initiating_location(self, value: Any) -> None:
        set_extension(self, COMMUNICATIONREQUEST_INITIATING_LOCATION_URL, value)

    @property
    def workflow_barrier(self) -> Any:
        return get_extension(self, WORKFLOW_BARRIER_URL)

    @workflow_barrier.setter
    def workflow_barrier(self, value: Any) -> None:
        set_extension(self, WORKFLOW_BARRIER_URL, value)

    @property
    def workflow_complies_with(self) -> Any:
        return get_extension(self, WORKFLOW_COMPLIES_WITH_URL)

    @workflow_complies_with.setter
    def workflow_complies_with(self, value: Any) -> None:
        set_extension(self, WORKFLOW_COMPLIES_WITH_URL, value)

    @property
    def workflow_shall_comply_with(self) -> Any:
        return get_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL)

    @workflow_shall_comply_with.setter
    def workflow_shall_comply_with(self, value: Any) -> None:
        set_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL, value)

class CompartmentDefinition(base.CompartmentDefinition):

    @property
    def resource_approval_date(self) -> Any:
        return get_extension(self, RESOURCE_APPROVAL_DATE_URL)

    @resource_approval_date.setter
    def resource_approval_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_APPROVAL_DATE_URL, value)

    @property
    def resource_last_review_date(self) -> Any:
        return get_extension(self, RESOURCE_LAST_REVIEW_DATE_URL)

    @resource_last_review_date.setter
    def resource_last_review_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_LAST_REVIEW_DATE_URL, value)

    @property
    def resource_effective_period(self) -> Any:
        return get_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL)

    @resource_effective_period.setter
    def resource_effective_period(self, value: Any) -> None:
        set_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL, value)

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class Composition(base.Composition):

    @property
    def workflow_research_study(self) -> Any:
        return get_extension(self, WORKFLOW_RESEARCH_STUDY_URL)

    @workflow_research_study.setter
    def workflow_research_study(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RESEARCH_STUDY_URL, value)

    @property
    def composition_section_subject(self) -> Any:
        return get_extension(self, COMPOSITION_SECTION_SUBJECT_URL)

    @composition_section_subject.setter
    def composition_section_subject(self, value: Any) -> None:
        set_extension(self, COMPOSITION_SECTION_SUBJECT_URL, value)

    @property
    def composition_clinicaldocument_version_number(self) -> Any:
        return get_extension(self, COMPOSITION_CLINICALDOCUMENT_VERSION_NUMBER_URL)

    @composition_clinicaldocument_version_number.setter
    def composition_clinicaldocument_version_number(self, value: Any) -> None:
        set_extension(self, COMPOSITION_CLINICALDOCUMENT_VERSION_NUMBER_URL, value)

    @property
    def note(self) -> Any:
        return get_extension(self, NOTE_URL)

    @note.setter
    def note(self, value: Any) -> None:
        set_extension(self, NOTE_URL, value)

    @property
    def event_based_on(self) -> Any:
        return get_extension(self, EVENT_BASED_ON_URL)

    @event_based_on.setter
    def event_based_on(self, value: Any) -> None:
        set_extension(self, EVENT_BASED_ON_URL, value)

    @property
    def cqm_validity_period(self) -> Any:
        return get_extension(self, CQM_VALIDITY_PERIOD_URL)

    @cqm_validity_period.setter
    def cqm_validity_period(self, value: Any) -> None:
        set_extension(self, CQM_VALIDITY_PERIOD_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

class ConceptMap(base.ConceptMap):

    @property
    def resource_approval_date(self) -> Any:
        return get_extension(self, RESOURCE_APPROVAL_DATE_URL)

    @resource_approval_date.setter
    def resource_approval_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_APPROVAL_DATE_URL, value)

    @property
    def terminology_resource_identifier_metadata(self) -> Any:
        return get_extension(self, TERMINOLOGY_RESOURCE_IDENTIFIER_METADATA_URL)

    @terminology_resource_identifier_metadata.setter
    def terminology_resource_identifier_metadata(self, value: Any) -> None:
        set_extension(self, TERMINOLOGY_RESOURCE_IDENTIFIER_METADATA_URL, value)

    @property
    def resource_last_review_date(self) -> Any:
        return get_extension(self, RESOURCE_LAST_REVIEW_DATE_URL)

    @resource_last_review_date.setter
    def resource_last_review_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_LAST_REVIEW_DATE_URL, value)

    @property
    def resource_effective_period(self) -> Any:
        return get_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL)

    @resource_effective_period.setter
    def resource_effective_period(self, value: Any) -> None:
        set_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL, value)

    @property
    def workflow_related_artifact(self) -> Any:
        return get_extension(self, WORKFLOW_RELATED_ARTIFACT_URL)

    @workflow_related_artifact.setter
    def workflow_related_artifact(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELATED_ARTIFACT_URL, value)

    @property
    def concept_bidirectional(self) -> Any:
        return get_extension(self, CONCEPT_BIDIRECTIONAL_URL)

    @concept_bidirectional.setter
    def concept_bidirectional(self, value: Any) -> None:
        set_extension(self, CONCEPT_BIDIRECTIONAL_URL, value)

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class Condition(base.Condition):

    @property
    def workflow_triggered_by(self) -> Any:
        return get_extension(self, WORKFLOW_TRIGGERED_BY_URL)

    @workflow_triggered_by.setter
    def workflow_triggered_by(self, value: Any) -> None:
        set_extension(self, WORKFLOW_TRIGGERED_BY_URL, value)

    @property
    def condition_ruled_out(self) -> Any:
        return get_extension(self, CONDITION_RULED_OUT_URL)

    @condition_ruled_out.setter
    def condition_ruled_out(self, value: Any) -> None:
        set_extension(self, CONDITION_RULED_OUT_URL, value)

    @property
    def condition_related(self) -> Any:
        return get_extension(self, CONDITION_RELATED_URL)

    @condition_related.setter
    def condition_related(self, value: Any) -> None:
        set_extension(self, CONDITION_RELATED_URL, value)

    @property
    def condition_disease_course(self) -> Any:
        return get_extension(self, CONDITION_DISEASE_COURSE_URL)

    @condition_disease_course.setter
    def condition_disease_course(self, value: Any) -> None:
        set_extension(self, CONDITION_DISEASE_COURSE_URL, value)

    @property
    def condition_due_to(self) -> Any:
        return get_extension(self, CONDITION_DUE_TO_URL)

    @condition_due_to.setter
    def condition_due_to(self, value: Any) -> None:
        set_extension(self, CONDITION_DUE_TO_URL, value)

    @property
    def condition_occurred_following(self) -> Any:
        return get_extension(self, CONDITION_OCCURRED_FOLLOWING_URL)

    @condition_occurred_following.setter
    def condition_occurred_following(self, value: Any) -> None:
        set_extension(self, CONDITION_OCCURRED_FOLLOWING_URL, value)

    @property
    def event_part_of(self) -> Any:
        return get_extension(self, EVENT_PART_OF_URL)

    @event_part_of.setter
    def event_part_of(self, value: Any) -> None:
        set_extension(self, EVENT_PART_OF_URL, value)

    @property
    def condition_outcome(self) -> Any:
        return get_extension(self, CONDITION_OUTCOME_URL)

    @condition_outcome.setter
    def condition_outcome(self, value: Any) -> None:
        set_extension(self, CONDITION_OUTCOME_URL, value)

    @property
    def event_based_on(self) -> Any:
        return get_extension(self, EVENT_BASED_ON_URL)

    @event_based_on.setter
    def event_based_on(self, value: Any) -> None:
        set_extension(self, EVENT_BASED_ON_URL, value)

    @property
    def condition_asserted_date(self) -> Any:
        return get_extension(self, CONDITION_ASSERTED_DATE_URL)

    @condition_asserted_date.setter
    def condition_asserted_date(self, value: Any) -> None:
        set_extension(self, CONDITION_ASSERTED_DATE_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def condition_reviewed(self) -> Any:
        return get_extension(self, CONDITION_REVIEWED_URL)

    @condition_reviewed.setter
    def condition_reviewed(self, value: Any) -> None:
        set_extension(self, CONDITION_REVIEWED_URL, value)

    @property
    def workflow_adheres_to(self) -> Any:
        return get_extension(self, WORKFLOW_ADHERES_TO_URL)

    @workflow_adheres_to.setter
    def workflow_adheres_to(self, value: Any) -> None:
        set_extension(self, WORKFLOW_ADHERES_TO_URL, value)

    @property
    def workflow_shall_comply_with(self) -> Any:
        return get_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL)

    @workflow_shall_comply_with.setter
    def workflow_shall_comply_with(self, value: Any) -> None:
        set_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL, value)

class ConditionDefinition(base.ConditionDefinition):

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class Consent(base.Consent):

    @property
    def consent_transcriber(self) -> Any:
        return get_extension(self, CONSENT_TRANSCRIBER_URL)

    @consent_transcriber.setter
    def consent_transcriber(self, value: Any) -> None:
        set_extension(self, CONSENT_TRANSCRIBER_URL, value)

    @property
    def event_performer_function(self) -> Any:
        return get_extension(self, EVENT_PERFORMER_FUNCTION_URL)

    @event_performer_function.setter
    def event_performer_function(self, value: Any) -> None:
        set_extension(self, EVENT_PERFORMER_FUNCTION_URL, value)

    @property
    def workflow_research_study(self) -> Any:
        return get_extension(self, WORKFLOW_RESEARCH_STUDY_URL)

    @workflow_research_study.setter
    def workflow_research_study(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RESEARCH_STUDY_URL, value)

    @property
    def event_based_on(self) -> Any:
        return get_extension(self, EVENT_BASED_ON_URL)

    @event_based_on.setter
    def event_based_on(self, value: Any) -> None:
        set_extension(self, EVENT_BASED_ON_URL, value)

    @property
    def consent_notification_endpoint(self) -> Any:
        return get_extension(self, CONSENT_NOTIFICATION_ENDPOINT_URL)

    @consent_notification_endpoint.setter
    def consent_notification_endpoint(self, value: Any) -> None:
        set_extension(self, CONSENT_NOTIFICATION_ENDPOINT_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def consent_location(self) -> Any:
        return get_extension(self, CONSENT_LOCATION_URL)

    @consent_location.setter
    def consent_location(self, value: Any) -> None:
        set_extension(self, CONSENT_LOCATION_URL, value)

    @property
    def consent_witness(self) -> Any:
        return get_extension(self, CONSENT_WITNESS_URL)

    @consent_witness.setter
    def consent_witness(self, value: Any) -> None:
        set_extension(self, CONSENT_WITNESS_URL, value)

    @property
    def consent_research_study_context(self) -> Any:
        return get_extension(self, CONSENT_RESEARCH_STUDY_CONTEXT_URL)

    @consent_research_study_context.setter
    def consent_research_study_context(self, value: Any) -> None:
        set_extension(self, CONSENT_RESEARCH_STUDY_CONTEXT_URL, value)

class ContactDetail(base.ContactDetail):

    @property
    def extended_contact_availability(self) -> Any:
        return get_extension(self, EXTENDED_CONTACT_AVAILABILITY_URL)

    @extended_contact_availability.setter
    def extended_contact_availability(self, value: Any) -> None:
        set_extension(self, EXTENDED_CONTACT_AVAILABILITY_URL, value)

    @property
    def cqf_contribution_time(self) -> Any:
        return get_extension(self, CQF_CONTRIBUTION_TIME_URL)

    @cqf_contribution_time.setter
    def cqf_contribution_time(self, value: Any) -> None:
        set_extension(self, CQF_CONTRIBUTION_TIME_URL, value)

    @property
    def artifact_contact_detail_reference(self) -> Any:
        return get_extension(self, ARTIFACT_CONTACT_DETAIL_REFERENCE_URL)

    @artifact_contact_detail_reference.setter
    def artifact_contact_detail_reference(self, value: Any) -> None:
        set_extension(self, ARTIFACT_CONTACT_DETAIL_REFERENCE_URL, value)

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

    @property
    def cqf_contact_reference(self) -> Any:
        return get_extension(self, CQF_CONTACT_REFERENCE_URL)

    @cqf_contact_reference.setter
    def cqf_contact_reference(self, value: Any) -> None:
        set_extension(self, CQF_CONTACT_REFERENCE_URL, value)

    @property
    def cqf_contact_address(self) -> Any:
        return get_extension(self, CQF_CONTACT_ADDRESS_URL)

    @cqf_contact_address.setter
    def cqf_contact_address(self, value: Any) -> None:
        set_extension(self, CQF_CONTACT_ADDRESS_URL, value)

class ContactPoint(base.ContactPoint):

    @property
    def contactpoint_area(self) -> Any:
        return get_extension(self, CONTACTPOINT_AREA_URL)

    @contactpoint_area.setter
    def contactpoint_area(self, value: Any) -> None:
        set_extension(self, CONTACTPOINT_AREA_URL, value)

    @property
    def confidential(self) -> Any:
        return get_extension(self, CONFIDENTIAL_URL)

    @confidential.setter
    def confidential(self, value: Any) -> None:
        set_extension(self, CONFIDENTIAL_URL, value)

    @property
    def contactpoint_local(self) -> Any:
        return get_extension(self, CONTACTPOINT_LOCAL_URL)

    @contactpoint_local.setter
    def contactpoint_local(self, value: Any) -> None:
        set_extension(self, CONTACTPOINT_LOCAL_URL, value)

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

    @property
    def iso21090_tel_address(self) -> Any:
        return get_extension(self, ISO21090_TEL_ADDRESS_URL)

    @iso21090_tel_address.setter
    def iso21090_tel_address(self, value: Any) -> None:
        set_extension(self, ISO21090_TEL_ADDRESS_URL, value)

    @property
    def contactpoint_purpose(self) -> Any:
        return get_extension(self, CONTACTPOINT_PURPOSE_URL)

    @contactpoint_purpose.setter
    def contactpoint_purpose(self, value: Any) -> None:
        set_extension(self, CONTACTPOINT_PURPOSE_URL, value)

    @property
    def contactpoint_extension(self) -> Any:
        return get_extension(self, CONTACTPOINT_EXTENSION_URL)

    @contactpoint_extension.setter
    def contactpoint_extension(self, value: Any) -> None:
        set_extension(self, CONTACTPOINT_EXTENSION_URL, value)

    @property
    def contactpoint_comment(self) -> Any:
        return get_extension(self, CONTACTPOINT_COMMENT_URL)

    @contactpoint_comment.setter
    def contactpoint_comment(self, value: Any) -> None:
        set_extension(self, CONTACTPOINT_COMMENT_URL, value)

    @property
    def iso21090_preferred(self) -> Any:
        return get_extension(self, ISO21090_PREFERRED_URL)

    @iso21090_preferred.setter
    def iso21090_preferred(self, value: Any) -> None:
        set_extension(self, ISO21090_PREFERRED_URL, value)

    @property
    def contactpoint_country(self) -> Any:
        return get_extension(self, CONTACTPOINT_COUNTRY_URL)

    @contactpoint_country.setter
    def contactpoint_country(self, value: Any) -> None:
        set_extension(self, CONTACTPOINT_COUNTRY_URL, value)

class Contract(base.Contract):

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

class Count(base.Count):

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

class Coverage(base.Coverage):

    @property
    def event_based_on(self) -> Any:
        return get_extension(self, EVENT_BASED_ON_URL)

    @event_based_on.setter
    def event_based_on(self, value: Any) -> None:
        set_extension(self, EVENT_BASED_ON_URL, value)

class DataRequirement(base.DataRequirement):

    @property
    def cqf_is_selective(self) -> Any:
        return get_extension(self, CQF_IS_SELECTIVE_URL)

    @cqf_is_selective.setter
    def cqf_is_selective(self, value: Any) -> None:
        set_extension(self, CQF_IS_SELECTIVE_URL, value)

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

    @property
    def cqf_fhir_query_pattern(self) -> Any:
        return get_extension(self, CQF_FHIR_QUERY_PATTERN_URL)

    @cqf_fhir_query_pattern.setter
    def cqf_fhir_query_pattern(self, value: Any) -> None:
        set_extension(self, CQF_FHIR_QUERY_PATTERN_URL, value)

    @property
    def cqf_value_filter(self) -> Any:
        return get_extension(self, CQF_VALUE_FILTER_URL)

    @cqf_value_filter.setter
    def cqf_value_filter(self, value: Any) -> None:
        set_extension(self, CQF_VALUE_FILTER_URL, value)

class DetectedIssue(base.DetectedIssue):

    @property
    def event_based_on(self) -> Any:
        return get_extension(self, EVENT_BASED_ON_URL)

    @event_based_on.setter
    def event_based_on(self, value: Any) -> None:
        set_extension(self, EVENT_BASED_ON_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

class Device(base.Device):

    @property
    def device_maintenanceresponsibility(self) -> Any:
        return get_extension(self, DEVICE_MAINTENANCERESPONSIBILITY_URL)

    @device_maintenanceresponsibility.setter
    def device_maintenanceresponsibility(self, value: Any) -> None:
        set_extension(self, DEVICE_MAINTENANCERESPONSIBILITY_URL, value)

    @property
    def device_lastmaintenancetime(self) -> Any:
        return get_extension(self, DEVICE_LASTMAINTENANCETIME_URL)

    @device_lastmaintenancetime.setter
    def device_lastmaintenancetime(self, value: Any) -> None:
        set_extension(self, DEVICE_LASTMAINTENANCETIME_URL, value)

    @property
    def device_implant_status(self) -> Any:
        return get_extension(self, DEVICE_IMPLANT_STATUS_URL)

    @device_implant_status.setter
    def device_implant_status(self, value: Any) -> None:
        set_extension(self, DEVICE_IMPLANT_STATUS_URL, value)

    @property
    def device_commercial_brand(self) -> Any:
        return get_extension(self, DEVICE_COMMERCIAL_BRAND_URL)

    @device_commercial_brand.setter
    def device_commercial_brand(self, value: Any) -> None:
        set_extension(self, DEVICE_COMMERCIAL_BRAND_URL, value)

class DeviceDefinition(base.DeviceDefinition):

    @property
    def device_commercial_brand(self) -> Any:
        return get_extension(self, DEVICE_COMMERCIAL_BRAND_URL)

    @device_commercial_brand.setter
    def device_commercial_brand(self, value: Any) -> None:
        set_extension(self, DEVICE_COMMERCIAL_BRAND_URL, value)

class DeviceDispense(base.DeviceDispense):

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

class DeviceRequest(base.DeviceRequest):

    @property
    def workflow_triggered_by(self) -> Any:
        return get_extension(self, WORKFLOW_TRIGGERED_BY_URL)

    @workflow_triggered_by.setter
    def workflow_triggered_by(self, value: Any) -> None:
        set_extension(self, WORKFLOW_TRIGGERED_BY_URL, value)

    @property
    def devicerequest_patient_instruction(self) -> Any:
        return get_extension(self, DEVICEREQUEST_PATIENT_INSTRUCTION_URL)

    @devicerequest_patient_instruction.setter
    def devicerequest_patient_instruction(self, value: Any) -> None:
        set_extension(self, DEVICEREQUEST_PATIENT_INSTRUCTION_URL, value)

    @property
    def workflow_generated_from(self) -> Any:
        return get_extension(self, WORKFLOW_GENERATED_FROM_URL)

    @workflow_generated_from.setter
    def workflow_generated_from(self, value: Any) -> None:
        set_extension(self, WORKFLOW_GENERATED_FROM_URL, value)

    @property
    def workflow_follow_on_of(self) -> Any:
        return get_extension(self, WORKFLOW_FOLLOW_ON_OF_URL)

    @workflow_follow_on_of.setter
    def workflow_follow_on_of(self, value: Any) -> None:
        set_extension(self, WORKFLOW_FOLLOW_ON_OF_URL, value)

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def procedure_approach_body_structure(self) -> Any:
        return get_extension(self, PROCEDURE_APPROACH_BODY_STRUCTURE_URL)

    @procedure_approach_body_structure.setter
    def procedure_approach_body_structure(self, value: Any) -> None:
        set_extension(self, PROCEDURE_APPROACH_BODY_STRUCTURE_URL, value)

    @property
    def workflow_complies_with(self) -> Any:
        return get_extension(self, WORKFLOW_COMPLIES_WITH_URL)

    @workflow_complies_with.setter
    def workflow_complies_with(self, value: Any) -> None:
        set_extension(self, WORKFLOW_COMPLIES_WITH_URL, value)

    @property
    def request_status_reason(self) -> Any:
        return get_extension(self, REQUEST_STATUS_REASON_URL)

    @request_status_reason.setter
    def request_status_reason(self, value: Any) -> None:
        set_extension(self, REQUEST_STATUS_REASON_URL, value)

class DeviceUsage(base.DeviceUsage):

    @property
    def workflow_research_study(self) -> Any:
        return get_extension(self, WORKFLOW_RESEARCH_STUDY_URL)

    @workflow_research_study.setter
    def workflow_research_study(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RESEARCH_STUDY_URL, value)

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def event_status_reason(self) -> Any:
        return get_extension(self, EVENT_STATUS_REASON_URL)

    @event_status_reason.setter
    def event_status_reason(self, value: Any) -> None:
        set_extension(self, EVENT_STATUS_REASON_URL, value)

    @property
    def event_event_history(self) -> Any:
        return get_extension(self, EVENT_EVENT_HISTORY_URL)

    @event_event_history.setter
    def event_event_history(self, value: Any) -> None:
        set_extension(self, EVENT_EVENT_HISTORY_URL, value)

    @property
    def procedure_approach_body_structure(self) -> Any:
        return get_extension(self, PROCEDURE_APPROACH_BODY_STRUCTURE_URL)

    @procedure_approach_body_structure.setter
    def procedure_approach_body_structure(self, value: Any) -> None:
        set_extension(self, PROCEDURE_APPROACH_BODY_STRUCTURE_URL, value)

class DiagnosticReport(base.DiagnosticReport):

    @property
    def workflow_triggered_by(self) -> Any:
        return get_extension(self, WORKFLOW_TRIGGERED_BY_URL)

    @workflow_triggered_by.setter
    def workflow_triggered_by(self, value: Any) -> None:
        set_extension(self, WORKFLOW_TRIGGERED_BY_URL, value)

    @property
    def event_performer_function(self) -> Any:
        return get_extension(self, EVENT_PERFORMER_FUNCTION_URL)

    @event_performer_function.setter
    def event_performer_function(self, value: Any) -> None:
        set_extension(self, EVENT_PERFORMER_FUNCTION_URL, value)

    @property
    def diagnostic_report_focus(self) -> Any:
        return get_extension(self, DIAGNOSTIC_REPORT_FOCUS_URL)

    @diagnostic_report_focus.setter
    def diagnostic_report_focus(self, value: Any) -> None:
        set_extension(self, DIAGNOSTIC_REPORT_FOCUS_URL, value)

    @property
    def workflow_research_study(self) -> Any:
        return get_extension(self, WORKFLOW_RESEARCH_STUDY_URL)

    @workflow_research_study.setter
    def workflow_research_study(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RESEARCH_STUDY_URL, value)

    @property
    def diagnostic_report_risk(self) -> Any:
        return get_extension(self, DIAGNOSTIC_REPORT_RISK_URL)

    @diagnostic_report_risk.setter
    def diagnostic_report_risk(self, value: Any) -> None:
        set_extension(self, DIAGNOSTIC_REPORT_RISK_URL, value)

    @property
    def diagnostic_report_extends(self) -> Any:
        return get_extension(self, DIAGNOSTIC_REPORT_EXTENDS_URL)

    @diagnostic_report_extends.setter
    def diagnostic_report_extends(self, value: Any) -> None:
        set_extension(self, DIAGNOSTIC_REPORT_EXTENDS_URL, value)

    @property
    def diagnostic_report_summary_of(self) -> Any:
        return get_extension(self, DIAGNOSTIC_REPORT_SUMMARY_OF_URL)

    @diagnostic_report_summary_of.setter
    def diagnostic_report_summary_of(self, value: Any) -> None:
        set_extension(self, DIAGNOSTIC_REPORT_SUMMARY_OF_URL, value)

    @property
    def diagnostic_report_workflow_status(self) -> Any:
        return get_extension(self, DIAGNOSTIC_REPORT_WORKFLOW_STATUS_URL)

    @diagnostic_report_workflow_status.setter
    def diagnostic_report_workflow_status(self, value: Any) -> None:
        set_extension(self, DIAGNOSTIC_REPORT_WORKFLOW_STATUS_URL, value)

    @property
    def event_part_of(self) -> Any:
        return get_extension(self, EVENT_PART_OF_URL)

    @event_part_of.setter
    def event_part_of(self, value: Any) -> None:
        set_extension(self, EVENT_PART_OF_URL, value)

    @property
    def workflow_related_artifact(self) -> Any:
        return get_extension(self, WORKFLOW_RELATED_ARTIFACT_URL)

    @workflow_related_artifact.setter
    def workflow_related_artifact(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELATED_ARTIFACT_URL, value)

    @property
    def diagnostic_report_addendum_of(self) -> Any:
        return get_extension(self, DIAGNOSTIC_REPORT_ADDENDUM_OF_URL)

    @diagnostic_report_addendum_of.setter
    def diagnostic_report_addendum_of(self, value: Any) -> None:
        set_extension(self, DIAGNOSTIC_REPORT_ADDENDUM_OF_URL, value)

    @property
    def workflow_supporting_info(self) -> Any:
        return get_extension(self, WORKFLOW_SUPPORTING_INFO_URL)

    @workflow_supporting_info.setter
    def workflow_supporting_info(self, value: Any) -> None:
        set_extension(self, WORKFLOW_SUPPORTING_INFO_URL, value)

    @property
    def diagnostic_report_replaces(self) -> Any:
        return get_extension(self, DIAGNOSTIC_REPORT_REPLACES_URL)

    @diagnostic_report_replaces.setter
    def diagnostic_report_replaces(self, value: Any) -> None:
        set_extension(self, DIAGNOSTIC_REPORT_REPLACES_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def event_status_reason(self) -> Any:
        return get_extension(self, EVENT_STATUS_REASON_URL)

    @event_status_reason.setter
    def event_status_reason(self, value: Any) -> None:
        set_extension(self, EVENT_STATUS_REASON_URL, value)

    @property
    def workflow_reason(self) -> Any:
        return get_extension(self, WORKFLOW_REASON_URL)

    @workflow_reason.setter
    def workflow_reason(self, value: Any) -> None:
        set_extension(self, WORKFLOW_REASON_URL, value)

    @property
    def workflow_adheres_to(self) -> Any:
        return get_extension(self, WORKFLOW_ADHERES_TO_URL)

    @workflow_adheres_to.setter
    def workflow_adheres_to(self, value: Any) -> None:
        set_extension(self, WORKFLOW_ADHERES_TO_URL, value)

    @property
    def event_event_history(self) -> Any:
        return get_extension(self, EVENT_EVENT_HISTORY_URL)

    @event_event_history.setter
    def event_event_history(self, value: Any) -> None:
        set_extension(self, EVENT_EVENT_HISTORY_URL, value)

    @property
    def diagnostic_report_location_performed(self) -> Any:
        return get_extension(self, DIAGNOSTIC_REPORT_LOCATION_PERFORMED_URL)

    @diagnostic_report_location_performed.setter
    def diagnostic_report_location_performed(self, value: Any) -> None:
        set_extension(self, DIAGNOSTIC_REPORT_LOCATION_PERFORMED_URL, value)

    @property
    def workflow_shall_comply_with(self) -> Any:
        return get_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL)

    @workflow_shall_comply_with.setter
    def workflow_shall_comply_with(self, value: Any) -> None:
        set_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL, value)

    @property
    def event_location(self) -> Any:
        return get_extension(self, EVENT_LOCATION_URL)

    @event_location.setter
    def event_location(self, value: Any) -> None:
        set_extension(self, EVENT_LOCATION_URL, value)

class Distance(base.Distance):

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

class DocumentReference(base.DocumentReference):

    @property
    def workflow_triggered_by(self) -> Any:
        return get_extension(self, WORKFLOW_TRIGGERED_BY_URL)

    @workflow_triggered_by.setter
    def workflow_triggered_by(self, value: Any) -> None:
        set_extension(self, WORKFLOW_TRIGGERED_BY_URL, value)

    @property
    def event_performer_function(self) -> Any:
        return get_extension(self, EVENT_PERFORMER_FUNCTION_URL)

    @event_performer_function.setter
    def event_performer_function(self, value: Any) -> None:
        set_extension(self, EVENT_PERFORMER_FUNCTION_URL, value)

    @property
    def workflow_research_study(self) -> Any:
        return get_extension(self, WORKFLOW_RESEARCH_STUDY_URL)

    @workflow_research_study.setter
    def workflow_research_study(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RESEARCH_STUDY_URL, value)

    @property
    def documentreference_sourcepatient(self) -> Any:
        return get_extension(self, DOCUMENTREFERENCE_SOURCEPATIENT_URL)

    @documentreference_sourcepatient.setter
    def documentreference_sourcepatient(self, value: Any) -> None:
        set_extension(self, DOCUMENTREFERENCE_SOURCEPATIENT_URL, value)

    @property
    def workflow_supporting_info(self) -> Any:
        return get_extension(self, WORKFLOW_SUPPORTING_INFO_URL)

    @workflow_supporting_info.setter
    def workflow_supporting_info(self, value: Any) -> None:
        set_extension(self, WORKFLOW_SUPPORTING_INFO_URL, value)

    @property
    def documentreference_thumbnail(self) -> Any:
        return get_extension(self, DOCUMENTREFERENCE_THUMBNAIL_URL)

    @documentreference_thumbnail.setter
    def documentreference_thumbnail(self, value: Any) -> None:
        set_extension(self, DOCUMENTREFERENCE_THUMBNAIL_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def event_status_reason(self) -> Any:
        return get_extension(self, EVENT_STATUS_REASON_URL)

    @event_status_reason.setter
    def event_status_reason(self, value: Any) -> None:
        set_extension(self, EVENT_STATUS_REASON_URL, value)

    @property
    def workflow_reason(self) -> Any:
        return get_extension(self, WORKFLOW_REASON_URL)

    @workflow_reason.setter
    def workflow_reason(self, value: Any) -> None:
        set_extension(self, WORKFLOW_REASON_URL, value)

    @property
    def workflow_adheres_to(self) -> Any:
        return get_extension(self, WORKFLOW_ADHERES_TO_URL)

    @workflow_adheres_to.setter
    def workflow_adheres_to(self, value: Any) -> None:
        set_extension(self, WORKFLOW_ADHERES_TO_URL, value)

    @property
    def workflow_shall_comply_with(self) -> Any:
        return get_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL)

    @workflow_shall_comply_with.setter
    def workflow_shall_comply_with(self, value: Any) -> None:
        set_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL, value)

    @property
    def event_location(self) -> Any:
        return get_extension(self, EVENT_LOCATION_URL)

    @event_location.setter
    def event_location(self, value: Any) -> None:
        set_extension(self, EVENT_LOCATION_URL, value)

class DomainResource(base.DomainResource):

    @property
    def cqf_library(self) -> Any:
        return get_extension(self, CQF_LIBRARY_URL)

    @cqf_library.setter
    def cqf_library(self, value: Any) -> None:
        set_extension(self, CQF_LIBRARY_URL, value)

    @property
    def cqf_knowledge_capability(self) -> Any:
        return get_extension(self, CQF_KNOWLEDGE_CAPABILITY_URL)

    @cqf_knowledge_capability.setter
    def cqf_knowledge_capability(self, value: Any) -> None:
        set_extension(self, CQF_KNOWLEDGE_CAPABILITY_URL, value)

    @property
    def artifact_is_owned(self) -> Any:
        return get_extension(self, ARTIFACT_IS_OWNED_URL)

    @artifact_is_owned.setter
    def artifact_is_owned(self, value: Any) -> None:
        set_extension(self, ARTIFACT_IS_OWNED_URL, value)

    @property
    def structuredefinition_fmm(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_FMM_URL)

    @structuredefinition_fmm.setter
    def structuredefinition_fmm(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_FMM_URL, value)

    @property
    def structuredefinition_standards_status_reason(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_STANDARDS_STATUS_REASON_URL)

    @structuredefinition_standards_status_reason.setter
    def structuredefinition_standards_status_reason(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_STANDARDS_STATUS_REASON_URL, value)

    @property
    def cqf_knowledge_representation_level(self) -> Any:
        return get_extension(self, CQF_KNOWLEDGE_REPRESENTATION_LEVEL_URL)

    @cqf_knowledge_representation_level.setter
    def cqf_knowledge_representation_level(self, value: Any) -> None:
        set_extension(self, CQF_KNOWLEDGE_REPRESENTATION_LEVEL_URL, value)

    @property
    def cqf_logic_definition(self) -> Any:
        return get_extension(self, CQF_LOGIC_DEFINITION_URL)

    @cqf_logic_definition.setter
    def cqf_logic_definition(self, value: Any) -> None:
        set_extension(self, CQF_LOGIC_DEFINITION_URL, value)

    @property
    def structuredefinition_wg(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_WG_URL)

    @structuredefinition_wg.setter
    def structuredefinition_wg(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_WG_URL, value)

    @property
    def structuredefinition_fmm_support(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_FMM_SUPPORT_URL)

    @structuredefinition_fmm_support.setter
    def structuredefinition_fmm_support(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_FMM_SUPPORT_URL, value)

class Dosage(base.Dosage):

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

    @property
    def dosage_minimum_gap_between_dose(self) -> Any:
        return get_extension(self, DOSAGE_MINIMUM_GAP_BETWEEN_DOSE_URL)

    @dosage_minimum_gap_between_dose.setter
    def dosage_minimum_gap_between_dose(self, value: Any) -> None:
        set_extension(self, DOSAGE_MINIMUM_GAP_BETWEEN_DOSE_URL, value)

    @property
    def dosage_conditions(self) -> Any:
        return get_extension(self, DOSAGE_CONDITIONS_URL)

    @dosage_conditions.setter
    def dosage_conditions(self, value: Any) -> None:
        set_extension(self, DOSAGE_CONDITIONS_URL, value)

class Duration(base.Duration):

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

class Element(base.Element):

    @property
    def artifact_editor(self) -> Any:
        return get_extension(self, ARTIFACT_EDITOR_URL)

    @artifact_editor.setter
    def artifact_editor(self, value: Any) -> None:
        set_extension(self, ARTIFACT_EDITOR_URL, value)

    @property
    def cqf_calculated_value(self) -> Any:
        return get_extension(self, CQF_CALCULATED_VALUE_URL)

    @cqf_calculated_value.setter
    def cqf_calculated_value(self, value: Any) -> None:
        set_extension(self, CQF_CALCULATED_VALUE_URL, value)

    @property
    def cqf_expression(self) -> Any:
        return get_extension(self, CQF_EXPRESSION_URL)

    @cqf_expression.setter
    def cqf_expression(self, value: Any) -> None:
        set_extension(self, CQF_EXPRESSION_URL, value)

    @property
    def narrative_link(self) -> Any:
        return get_extension(self, NARRATIVE_LINK_URL)

    @narrative_link.setter
    def narrative_link(self, value: Any) -> None:
        set_extension(self, NARRATIVE_LINK_URL, value)

    @property
    def rendering_style(self) -> Any:
        return get_extension(self, RENDERING_STYLE_URL)

    @rendering_style.setter
    def rendering_style(self, value: Any) -> None:
        set_extension(self, RENDERING_STYLE_URL, value)

    @property
    def cqf_citation(self) -> Any:
        return get_extension(self, CQF_CITATION_URL)

    @cqf_citation.setter
    def cqf_citation(self, value: Any) -> None:
        set_extension(self, CQF_CITATION_URL, value)

    @property
    def version_specific_use(self) -> Any:
        return get_extension(self, VERSION_SPECIFIC_USE_URL)

    @version_specific_use.setter
    def version_specific_use(self, value: Any) -> None:
        set_extension(self, VERSION_SPECIFIC_USE_URL, value)

    @property
    def satisfies_requirement(self) -> Any:
        return get_extension(self, SATISFIES_REQUIREMENT_URL)

    @satisfies_requirement.setter
    def satisfies_requirement(self, value: Any) -> None:
        set_extension(self, SATISFIES_REQUIREMENT_URL, value)

    @property
    def cqf_initial_value(self) -> Any:
        return get_extension(self, CQF_INITIAL_VALUE_URL)

    @cqf_initial_value.setter
    def cqf_initial_value(self, value: Any) -> None:
        set_extension(self, CQF_INITIAL_VALUE_URL, value)

    @property
    def derivation_reference(self) -> Any:
        return get_extension(self, DERIVATION_REFERENCE_URL)

    @derivation_reference.setter
    def derivation_reference(self, value: Any) -> None:
        set_extension(self, DERIVATION_REFERENCE_URL, value)

    @property
    def cqf_certainty(self) -> Any:
        return get_extension(self, CQF_CERTAINTY_URL)

    @cqf_certainty.setter
    def cqf_certainty(self, value: Any) -> None:
        set_extension(self, CQF_CERTAINTY_URL, value)

    @property
    def artifact_reference(self) -> Any:
        return get_extension(self, ARTIFACT_REFERENCE_URL)

    @artifact_reference.setter
    def artifact_reference(self, value: Any) -> None:
        set_extension(self, ARTIFACT_REFERENCE_URL, value)

    @property
    def artifact_endorser(self) -> Any:
        return get_extension(self, ARTIFACT_ENDORSER_URL)

    @artifact_endorser.setter
    def artifact_endorser(self, value: Any) -> None:
        set_extension(self, ARTIFACT_ENDORSER_URL, value)

    @property
    def version_specific_value(self) -> Any:
        return get_extension(self, VERSION_SPECIFIC_VALUE_URL)

    @version_specific_value.setter
    def version_specific_value(self, value: Any) -> None:
        set_extension(self, VERSION_SPECIFIC_VALUE_URL, value)

    @property
    def artifact_canonical_reference(self) -> Any:
        return get_extension(self, ARTIFACT_CANONICAL_REFERENCE_URL)

    @artifact_canonical_reference.setter
    def artifact_canonical_reference(self, value: Any) -> None:
        set_extension(self, ARTIFACT_CANONICAL_REFERENCE_URL, value)

    @property
    def original_text(self) -> Any:
        return get_extension(self, ORIGINAL_TEXT_URL)

    @original_text.setter
    def original_text(self, value: Any) -> None:
        set_extension(self, ORIGINAL_TEXT_URL, value)

    @property
    def artifact_reviewer(self) -> Any:
        return get_extension(self, ARTIFACT_REVIEWER_URL)

    @artifact_reviewer.setter
    def artifact_reviewer(self, value: Any) -> None:
        set_extension(self, ARTIFACT_REVIEWER_URL, value)

    @property
    def cqf_relative_date_time(self) -> Any:
        return get_extension(self, CQF_RELATIVE_DATE_TIME_URL)

    @cqf_relative_date_time.setter
    def cqf_relative_date_time(self, value: Any) -> None:
        set_extension(self, CQF_RELATIVE_DATE_TIME_URL, value)

    @property
    def data_absent_reason(self) -> Any:
        return get_extension(self, DATA_ABSENT_REASON_URL)

    @data_absent_reason.setter
    def data_absent_reason(self, value: Any) -> None:
        set_extension(self, DATA_ABSENT_REASON_URL, value)

    @property
    def rendering_style_sensitive(self) -> Any:
        return get_extension(self, RENDERING_STYLE_SENSITIVE_URL)

    @rendering_style_sensitive.setter
    def rendering_style_sensitive(self, value: Any) -> None:
        set_extension(self, RENDERING_STYLE_SENSITIVE_URL, value)

    @property
    def iso21090_null_flavor(self) -> Any:
        return get_extension(self, ISO21090_NULL_FLAVOR_URL)

    @iso21090_null_flavor.setter
    def iso21090_null_flavor(self, value: Any) -> None:
        set_extension(self, ISO21090_NULL_FLAVOR_URL, value)

    @property
    def body_site(self) -> Any:
        return get_extension(self, BODY_SITE_URL)

    @body_site.setter
    def body_site(self, value: Any) -> None:
        set_extension(self, BODY_SITE_URL, value)

class ElementDefinition(base.ElementDefinition):

    @property
    def elementdefinition_bestpractice_explanation(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_BESTPRACTICE_EXPLANATION_URL)

    @elementdefinition_bestpractice_explanation.setter
    def elementdefinition_bestpractice_explanation(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_BESTPRACTICE_EXPLANATION_URL, value)

    @property
    def structuredefinition_display_hint(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_DISPLAY_HINT_URL)

    @structuredefinition_display_hint.setter
    def structuredefinition_display_hint(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_DISPLAY_HINT_URL, value)

    @property
    def elementdefinition_pattern(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_PATTERN_URL)

    @elementdefinition_pattern.setter
    def elementdefinition_pattern(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_PATTERN_URL, value)

    @property
    def elementdefinition_type_must_support(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_TYPE_MUST_SUPPORT_URL)

    @elementdefinition_type_must_support.setter
    def elementdefinition_type_must_support(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_TYPE_MUST_SUPPORT_URL, value)

    @property
    def elementdefinition_translatable(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_TRANSLATABLE_URL)

    @elementdefinition_translatable.setter
    def elementdefinition_translatable(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_TRANSLATABLE_URL, value)

    @property
    def min_length(self) -> Any:
        return get_extension(self, MIN_LENGTH_URL)

    @min_length.setter
    def min_length(self, value: Any) -> None:
        set_extension(self, MIN_LENGTH_URL, value)

    @property
    def ext_11179_object_class(self) -> Any:
        return get_extension(self, EXT_11179_OBJECT_CLASS_URL)

    @ext_11179_object_class.setter
    def ext_11179_object_class(self, value: Any) -> None:
        set_extension(self, EXT_11179_OBJECT_CLASS_URL, value)

    @property
    def elementdefinition_equivalence(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_EQUIVALENCE_URL)

    @elementdefinition_equivalence.setter
    def elementdefinition_equivalence(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_EQUIVALENCE_URL, value)

    @property
    def questionnaire_constraint(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_CONSTRAINT_URL)

    @questionnaire_constraint.setter
    def questionnaire_constraint(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_CONSTRAINT_URL, value)

    @property
    def structuredefinition_fhir_type(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_FHIR_TYPE_URL)

    @structuredefinition_fhir_type.setter
    def structuredefinition_fhir_type(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_FHIR_TYPE_URL, value)

    @property
    def elementdefinition_profile_element(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_PROFILE_ELEMENT_URL)

    @elementdefinition_profile_element.setter
    def elementdefinition_profile_element(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_PROFILE_ELEMENT_URL, value)

    @property
    def elementdefinition_selector(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_SELECTOR_URL)

    @elementdefinition_selector.setter
    def elementdefinition_selector(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_SELECTOR_URL, value)

    @property
    def questionnaire_signature_required(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_SIGNATURE_REQUIRED_URL)

    @questionnaire_signature_required.setter
    def questionnaire_signature_required(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_SIGNATURE_REQUIRED_URL, value)

    @property
    def elementdefinition_max_value_set(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_MAX_VALUE_SET_URL)

    @elementdefinition_max_value_set.setter
    def elementdefinition_max_value_set(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_MAX_VALUE_SET_URL, value)

    @property
    def max_decimal_places(self) -> Any:
        return get_extension(self, MAX_DECIMAL_PLACES_URL)

    @max_decimal_places.setter
    def max_decimal_places(self, value: Any) -> None:
        set_extension(self, MAX_DECIMAL_PLACES_URL, value)

    @property
    def questionnaire_hidden(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_HIDDEN_URL)

    @questionnaire_hidden.setter
    def questionnaire_hidden(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_HIDDEN_URL, value)

    @property
    def elementdefinition_is_common_binding(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_IS_COMMON_BINDING_URL)

    @elementdefinition_is_common_binding.setter
    def elementdefinition_is_common_binding(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_IS_COMMON_BINDING_URL, value)

    @property
    def cqf_should_trace_dependency(self) -> Any:
        return get_extension(self, CQF_SHOULD_TRACE_DEPENDENCY_URL)

    @cqf_should_trace_dependency.setter
    def cqf_should_trace_dependency(self, value: Any) -> None:
        set_extension(self, CQF_SHOULD_TRACE_DEPENDENCY_URL, value)

    @property
    def elementdefinition_defaulttype(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_DEFAULTTYPE_URL)

    @elementdefinition_defaulttype.setter
    def elementdefinition_defaulttype(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_DEFAULTTYPE_URL, value)

    @property
    def elementdefinition_allowed_units(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_ALLOWED_UNITS_URL)

    @elementdefinition_allowed_units.setter
    def elementdefinition_allowed_units(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_ALLOWED_UNITS_URL, value)

    @property
    def elementdefinition_suppress(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_SUPPRESS_URL)

    @elementdefinition_suppress.setter
    def elementdefinition_suppress(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_SUPPRESS_URL, value)

    @property
    def structuredefinition_standards_status(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_STANDARDS_STATUS_URL)

    @structuredefinition_standards_status.setter
    def structuredefinition_standards_status(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_STANDARDS_STATUS_URL, value)

    @property
    def structuredefinition_explicit_type_name(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_EXPLICIT_TYPE_NAME_URL)

    @structuredefinition_explicit_type_name.setter
    def structuredefinition_explicit_type_name(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_EXPLICIT_TYPE_NAME_URL, value)

    @property
    def elementdefinition_identifier(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_IDENTIFIER_URL)

    @elementdefinition_identifier.setter
    def elementdefinition_identifier(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_IDENTIFIER_URL, value)

    @property
    def structuredefinition_hierarchy(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_HIERARCHY_URL)

    @structuredefinition_hierarchy.setter
    def structuredefinition_hierarchy(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_HIERARCHY_URL, value)

    @property
    def structuredefinition_normative_version(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_NORMATIVE_VERSION_URL)

    @structuredefinition_normative_version.setter
    def structuredefinition_normative_version(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_NORMATIVE_VERSION_URL, value)

    @property
    def obligation(self) -> Any:
        return get_extension(self, OBLIGATION_URL)

    @obligation.setter
    def obligation(self, value: Any) -> None:
        set_extension(self, OBLIGATION_URL, value)

    @property
    def ext_11179_object_class_property(self) -> Any:
        return get_extension(self, EXT_11179_OBJECT_CLASS_PROPERTY_URL)

    @ext_11179_object_class_property.setter
    def ext_11179_object_class_property(self, value: Any) -> None:
        set_extension(self, EXT_11179_OBJECT_CLASS_PROPERTY_URL, value)

    @property
    def questionnaire_item_control(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_ITEM_CONTROL_URL)

    @questionnaire_item_control.setter
    def questionnaire_item_control(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_ITEM_CONTROL_URL, value)

    @property
    def questionnaire_support_link(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_SUPPORT_LINK_URL)

    @questionnaire_support_link.setter
    def questionnaire_support_link(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_SUPPORT_LINK_URL, value)

    @property
    def mime_type(self) -> Any:
        return get_extension(self, MIME_TYPE_URL)

    @mime_type.setter
    def mime_type(self, value: Any) -> None:
        set_extension(self, MIME_TYPE_URL, value)

    @property
    def design_note(self) -> Any:
        return get_extension(self, DESIGN_NOTE_URL)

    @design_note.setter
    def design_note(self, value: Any) -> None:
        set_extension(self, DESIGN_NOTE_URL, value)

    @property
    def elementdefinition_inherited_extensible_value_set(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_INHERITED_EXTENSIBLE_VALUE_SET_URL)

    @elementdefinition_inherited_extensible_value_set.setter
    def elementdefinition_inherited_extensible_value_set(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_INHERITED_EXTENSIBLE_VALUE_SET_URL, value)

    @property
    def elementdefinition_question(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_QUESTION_URL)

    @elementdefinition_question.setter
    def elementdefinition_question(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_QUESTION_URL, value)

    @property
    def elementdefinition_bestpractice(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_BESTPRACTICE_URL)

    @elementdefinition_bestpractice.setter
    def elementdefinition_bestpractice(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_BESTPRACTICE_URL, value)

    @property
    def questionnaire_base_type(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_BASE_TYPE_URL)

    @questionnaire_base_type.setter
    def questionnaire_base_type(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_BASE_TYPE_URL, value)

    @property
    def elementdefinition_binding_name(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_BINDING_NAME_URL)

    @elementdefinition_binding_name.setter
    def elementdefinition_binding_name(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_BINDING_NAME_URL, value)

    @property
    def elementdefinition_graph_constraint(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_GRAPH_CONSTRAINT_URL)

    @elementdefinition_graph_constraint.setter
    def elementdefinition_graph_constraint(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_GRAPH_CONSTRAINT_URL, value)

    @property
    def elementdefinition_min_value_set(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_MIN_VALUE_SET_URL)

    @elementdefinition_min_value_set.setter
    def elementdefinition_min_value_set(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_MIN_VALUE_SET_URL, value)

    @property
    def questionnaire_usage_mode(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_USAGE_MODE_URL)

    @questionnaire_usage_mode.setter
    def questionnaire_usage_mode(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_USAGE_MODE_URL, value)

    @property
    def entry_format(self) -> Any:
        return get_extension(self, ENTRY_FORMAT_URL)

    @entry_format.setter
    def entry_format(self, value: Any) -> None:
        set_extension(self, ENTRY_FORMAT_URL, value)

    @property
    def max_size(self) -> Any:
        return get_extension(self, MAX_SIZE_URL)

    @max_size.setter
    def max_size(self, value: Any) -> None:
        set_extension(self, MAX_SIZE_URL, value)

class Encounter(base.Encounter):

    @property
    def workflow_triggered_by(self) -> Any:
        return get_extension(self, WORKFLOW_TRIGGERED_BY_URL)

    @workflow_triggered_by.setter
    def workflow_triggered_by(self, value: Any) -> None:
        set_extension(self, WORKFLOW_TRIGGERED_BY_URL, value)

    @property
    def encounter_mode_of_arrival(self) -> Any:
        return get_extension(self, ENCOUNTER_MODE_OF_ARRIVAL_URL)

    @encounter_mode_of_arrival.setter
    def encounter_mode_of_arrival(self, value: Any) -> None:
        set_extension(self, ENCOUNTER_MODE_OF_ARRIVAL_URL, value)

    @property
    def workflow_research_study(self) -> Any:
        return get_extension(self, WORKFLOW_RESEARCH_STUDY_URL)

    @workflow_research_study.setter
    def workflow_research_study(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RESEARCH_STUDY_URL, value)

    @property
    def encounter_reason_cancelled(self) -> Any:
        return get_extension(self, ENCOUNTER_REASON_CANCELLED_URL)

    @encounter_reason_cancelled.setter
    def encounter_reason_cancelled(self, value: Any) -> None:
        set_extension(self, ENCOUNTER_REASON_CANCELLED_URL, value)

    @property
    def workflow_follow_on_of(self) -> Any:
        return get_extension(self, WORKFLOW_FOLLOW_ON_OF_URL)

    @workflow_follow_on_of.setter
    def workflow_follow_on_of(self, value: Any) -> None:
        set_extension(self, WORKFLOW_FOLLOW_ON_OF_URL, value)

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

    @property
    def workflow_supporting_info(self) -> Any:
        return get_extension(self, WORKFLOW_SUPPORTING_INFO_URL)

    @workflow_supporting_info.setter
    def workflow_supporting_info(self, value: Any) -> None:
        set_extension(self, WORKFLOW_SUPPORTING_INFO_URL, value)

    @property
    def workflow_adheres_to(self) -> Any:
        return get_extension(self, WORKFLOW_ADHERES_TO_URL)

    @workflow_adheres_to.setter
    def workflow_adheres_to(self, value: Any) -> None:
        set_extension(self, WORKFLOW_ADHERES_TO_URL, value)

    @property
    def encounter_associated_encounter(self) -> Any:
        return get_extension(self, ENCOUNTER_ASSOCIATED_ENCOUNTER_URL)

    @encounter_associated_encounter.setter
    def encounter_associated_encounter(self, value: Any) -> None:
        set_extension(self, ENCOUNTER_ASSOCIATED_ENCOUNTER_URL, value)

class Endpoint(base.Endpoint):

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

    @property
    def endpoint_fhir_version(self) -> Any:
        return get_extension(self, ENDPOINT_FHIR_VERSION_URL)

    @endpoint_fhir_version.setter
    def endpoint_fhir_version(self, value: Any) -> None:
        set_extension(self, ENDPOINT_FHIR_VERSION_URL, value)

class EnrollmentRequest(base.EnrollmentRequest):

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

class EnrollmentResponse(base.EnrollmentResponse):

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

class EpisodeOfCare(base.EpisodeOfCare):

    @property
    def event_based_on(self) -> Any:
        return get_extension(self, EVENT_BASED_ON_URL)

    @event_based_on.setter
    def event_based_on(self, value: Any) -> None:
        set_extension(self, EVENT_BASED_ON_URL, value)

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

class EventDefinition(base.EventDefinition):

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class Evidence(base.Evidence):

    @property
    def statistic_model_include_if(self) -> Any:
        return get_extension(self, STATISTIC_MODEL_INCLUDE_IF_URL)

    @statistic_model_include_if.setter
    def statistic_model_include_if(self, value: Any) -> None:
        set_extension(self, STATISTIC_MODEL_INCLUDE_IF_URL, value)

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class EvidenceReport(base.EvidenceReport):

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class EvidenceVariable(base.EvidenceVariable):

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class ExampleScenario(base.ExampleScenario):

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class ExplanationOfBenefit(base.ExplanationOfBenefit):

    @property
    def event_based_on(self) -> Any:
        return get_extension(self, EVENT_BASED_ON_URL)

    @event_based_on.setter
    def event_based_on(self, value: Any) -> None:
        set_extension(self, EVENT_BASED_ON_URL, value)

class Expression(base.Expression):

    @property
    def references_contained(self) -> Any:
        return get_extension(self, REFERENCES_CONTAINED_URL)

    @references_contained.setter
    def references_contained(self, value: Any) -> None:
        set_extension(self, REFERENCES_CONTAINED_URL, value)

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

    @property
    def cqf_alternative_expression(self) -> Any:
        return get_extension(self, CQF_ALTERNATIVE_EXPRESSION_URL)

    @cqf_alternative_expression.setter
    def cqf_alternative_expression(self, value: Any) -> None:
        set_extension(self, CQF_ALTERNATIVE_EXPRESSION_URL, value)

class ExtendedContactDetail(base.ExtendedContactDetail):

    @property
    def extended_contact_availability(self) -> Any:
        return get_extension(self, EXTENDED_CONTACT_AVAILABILITY_URL)

    @extended_contact_availability.setter
    def extended_contact_availability(self, value: Any) -> None:
        set_extension(self, EXTENDED_CONTACT_AVAILABILITY_URL, value)

    @property
    def contactpoint_comment(self) -> Any:
        return get_extension(self, CONTACTPOINT_COMMENT_URL)

    @contactpoint_comment.setter
    def contactpoint_comment(self, value: Any) -> None:
        set_extension(self, CONTACTPOINT_COMMENT_URL, value)

    @property
    def iso21090_preferred(self) -> Any:
        return get_extension(self, ISO21090_PREFERRED_URL)

    @iso21090_preferred.setter
    def iso21090_preferred(self, value: Any) -> None:
        set_extension(self, ISO21090_PREFERRED_URL, value)

class Extension(base.Extension):

    @property
    def structuredefinition_extension_meaning(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_EXTENSION_MEANING_URL)

    @structuredefinition_extension_meaning.setter
    def structuredefinition_extension_meaning(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_EXTENSION_MEANING_URL, value)

class FamilyMemberHistory(base.FamilyMemberHistory):

    @property
    def workflow_triggered_by(self) -> Any:
        return get_extension(self, WORKFLOW_TRIGGERED_BY_URL)

    @workflow_triggered_by.setter
    def workflow_triggered_by(self, value: Any) -> None:
        set_extension(self, WORKFLOW_TRIGGERED_BY_URL, value)

    @property
    def family_member_history_genetics_parent(self) -> Any:
        return get_extension(self, FAMILY_MEMBER_HISTORY_GENETICS_PARENT_URL)

    @family_member_history_genetics_parent.setter
    def family_member_history_genetics_parent(self, value: Any) -> None:
        set_extension(self, FAMILY_MEMBER_HISTORY_GENETICS_PARENT_URL, value)

    @property
    def familymemberhistory_patient_record(self) -> Any:
        return get_extension(self, FAMILYMEMBERHISTORY_PATIENT_RECORD_URL)

    @familymemberhistory_patient_record.setter
    def familymemberhistory_patient_record(self, value: Any) -> None:
        set_extension(self, FAMILYMEMBERHISTORY_PATIENT_RECORD_URL, value)

    @property
    def workflow_research_study(self) -> Any:
        return get_extension(self, WORKFLOW_RESEARCH_STUDY_URL)

    @workflow_research_study.setter
    def workflow_research_study(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RESEARCH_STUDY_URL, value)

    @property
    def family_member_history_genetics_sibling(self) -> Any:
        return get_extension(self, FAMILY_MEMBER_HISTORY_GENETICS_SIBLING_URL)

    @family_member_history_genetics_sibling.setter
    def family_member_history_genetics_sibling(self, value: Any) -> None:
        set_extension(self, FAMILY_MEMBER_HISTORY_GENETICS_SIBLING_URL, value)

    @property
    def familymemberhistory_type(self) -> Any:
        return get_extension(self, FAMILYMEMBERHISTORY_TYPE_URL)

    @familymemberhistory_type.setter
    def familymemberhistory_type(self, value: Any) -> None:
        set_extension(self, FAMILYMEMBERHISTORY_TYPE_URL, value)

    @property
    def familymemberhistory_severity(self) -> Any:
        return get_extension(self, FAMILYMEMBERHISTORY_SEVERITY_URL)

    @familymemberhistory_severity.setter
    def familymemberhistory_severity(self, value: Any) -> None:
        set_extension(self, FAMILYMEMBERHISTORY_SEVERITY_URL, value)

    @property
    def familymemberhistory_abatement(self) -> Any:
        return get_extension(self, FAMILYMEMBERHISTORY_ABATEMENT_URL)

    @familymemberhistory_abatement.setter
    def familymemberhistory_abatement(self, value: Any) -> None:
        set_extension(self, FAMILYMEMBERHISTORY_ABATEMENT_URL, value)

    @property
    def event_based_on(self) -> Any:
        return get_extension(self, EVENT_BASED_ON_URL)

    @event_based_on.setter
    def event_based_on(self, value: Any) -> None:
        set_extension(self, EVENT_BASED_ON_URL, value)

    @property
    def family_member_history_genetics_observation(self) -> Any:
        return get_extension(self, FAMILY_MEMBER_HISTORY_GENETICS_OBSERVATION_URL)

    @family_member_history_genetics_observation.setter
    def family_member_history_genetics_observation(self, value: Any) -> None:
        set_extension(self, FAMILY_MEMBER_HISTORY_GENETICS_OBSERVATION_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def workflow_adheres_to(self) -> Any:
        return get_extension(self, WORKFLOW_ADHERES_TO_URL)

    @workflow_adheres_to.setter
    def workflow_adheres_to(self, value: Any) -> None:
        set_extension(self, WORKFLOW_ADHERES_TO_URL, value)

class Flag(base.Flag):

    @property
    def flag_detail(self) -> Any:
        return get_extension(self, FLAG_DETAIL_URL)

    @flag_detail.setter
    def flag_detail(self, value: Any) -> None:
        set_extension(self, FLAG_DETAIL_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def flag_priority(self) -> Any:
        return get_extension(self, FLAG_PRIORITY_URL)

    @flag_priority.setter
    def flag_priority(self, value: Any) -> None:
        set_extension(self, FLAG_PRIORITY_URL, value)

class Goal(base.Goal):

    @property
    def goal_acceptance(self) -> Any:
        return get_extension(self, GOAL_ACCEPTANCE_URL)

    @goal_acceptance.setter
    def goal_acceptance(self, value: Any) -> None:
        set_extension(self, GOAL_ACCEPTANCE_URL, value)

    @property
    def goal_reason_rejected(self) -> Any:
        return get_extension(self, GOAL_REASON_REJECTED_URL)

    @goal_reason_rejected.setter
    def goal_reason_rejected(self, value: Any) -> None:
        set_extension(self, GOAL_REASON_REJECTED_URL, value)

    @property
    def workflow_protective_factor(self) -> Any:
        return get_extension(self, WORKFLOW_PROTECTIVE_FACTOR_URL)

    @workflow_protective_factor.setter
    def workflow_protective_factor(self, value: Any) -> None:
        set_extension(self, WORKFLOW_PROTECTIVE_FACTOR_URL, value)

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def workflow_barrier(self) -> Any:
        return get_extension(self, WORKFLOW_BARRIER_URL)

    @workflow_barrier.setter
    def workflow_barrier(self, value: Any) -> None:
        set_extension(self, WORKFLOW_BARRIER_URL, value)

    @property
    def goal_relationship(self) -> Any:
        return get_extension(self, GOAL_RELATIONSHIP_URL)

    @goal_relationship.setter
    def goal_relationship(self, value: Any) -> None:
        set_extension(self, GOAL_RELATIONSHIP_URL, value)

class GraphDefinition(base.GraphDefinition):

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class Group(base.Group):

    @property
    def artifact_editor(self) -> Any:
        return get_extension(self, ARTIFACT_EDITOR_URL)

    @artifact_editor.setter
    def artifact_editor(self, value: Any) -> None:
        set_extension(self, ARTIFACT_EDITOR_URL, value)

    @property
    def cqf_test_artifact(self) -> Any:
        return get_extension(self, CQF_TEST_ARTIFACT_URL)

    @cqf_test_artifact.setter
    def cqf_test_artifact(self, value: Any) -> None:
        set_extension(self, CQF_TEST_ARTIFACT_URL, value)

    @property
    def resource_approval_date(self) -> Any:
        return get_extension(self, RESOURCE_APPROVAL_DATE_URL)

    @resource_approval_date.setter
    def resource_approval_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_APPROVAL_DATE_URL, value)

    @property
    def resource_last_review_date(self) -> Any:
        return get_extension(self, RESOURCE_LAST_REVIEW_DATE_URL)

    @resource_last_review_date.setter
    def resource_last_review_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_LAST_REVIEW_DATE_URL, value)

    @property
    def resource_effective_period(self) -> Any:
        return get_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL)

    @resource_effective_period.setter
    def resource_effective_period(self, value: Any) -> None:
        set_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL, value)

    @property
    def artifact_endorser(self) -> Any:
        return get_extension(self, ARTIFACT_ENDORSER_URL)

    @artifact_endorser.setter
    def artifact_endorser(self, value: Any) -> None:
        set_extension(self, ARTIFACT_ENDORSER_URL, value)

    @property
    def artifact_reviewer(self) -> Any:
        return get_extension(self, ARTIFACT_REVIEWER_URL)

    @artifact_reviewer.setter
    def artifact_reviewer(self, value: Any) -> None:
        set_extension(self, ARTIFACT_REVIEWER_URL, value)

    @property
    def cqf_input_parameters(self) -> Any:
        return get_extension(self, CQF_INPUT_PARAMETERS_URL)

    @cqf_input_parameters.setter
    def cqf_input_parameters(self, value: Any) -> None:
        set_extension(self, CQF_INPUT_PARAMETERS_URL, value)

    @property
    def characteristic_expression(self) -> Any:
        return get_extension(self, CHARACTERISTIC_EXPRESSION_URL)

    @characteristic_expression.setter
    def characteristic_expression(self, value: Any) -> None:
        set_extension(self, CHARACTERISTIC_EXPRESSION_URL, value)

class GuidanceResponse(base.GuidanceResponse):

    @property
    def cqf_input_parameters(self) -> Any:
        return get_extension(self, CQF_INPUT_PARAMETERS_URL)

    @cqf_input_parameters.setter
    def cqf_input_parameters(self, value: Any) -> None:
        set_extension(self, CQF_INPUT_PARAMETERS_URL, value)

class HumanName(base.HumanName):

    @property
    def humanname_mothers_family(self) -> Any:
        return get_extension(self, HUMANNAME_MOTHERS_FAMILY_URL)

    @humanname_mothers_family.setter
    def humanname_mothers_family(self, value: Any) -> None:
        set_extension(self, HUMANNAME_MOTHERS_FAMILY_URL, value)

    @property
    def humanname_own_prefix(self) -> Any:
        return get_extension(self, HUMANNAME_OWN_PREFIX_URL)

    @humanname_own_prefix.setter
    def humanname_own_prefix(self, value: Any) -> None:
        set_extension(self, HUMANNAME_OWN_PREFIX_URL, value)

    @property
    def iso21090_en_representation(self) -> Any:
        return get_extension(self, ISO21090_EN_REPRESENTATION_URL)

    @iso21090_en_representation.setter
    def iso21090_en_representation(self, value: Any) -> None:
        set_extension(self, ISO21090_EN_REPRESENTATION_URL, value)

    @property
    def language(self) -> Any:
        return get_extension(self, LANGUAGE_URL)

    @language.setter
    def language(self, value: Any) -> None:
        set_extension(self, LANGUAGE_URL, value)

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

    @property
    def humanname_assembly_order(self) -> Any:
        return get_extension(self, HUMANNAME_ASSEMBLY_ORDER_URL)

    @humanname_assembly_order.setter
    def humanname_assembly_order(self, value: Any) -> None:
        set_extension(self, HUMANNAME_ASSEMBLY_ORDER_URL, value)

    @property
    def humanname_partner_prefix(self) -> Any:
        return get_extension(self, HUMANNAME_PARTNER_PREFIX_URL)

    @humanname_partner_prefix.setter
    def humanname_partner_prefix(self, value: Any) -> None:
        set_extension(self, HUMANNAME_PARTNER_PREFIX_URL, value)

    @property
    def iso21090_en_qualifier(self) -> Any:
        return get_extension(self, ISO21090_EN_QUALIFIER_URL)

    @iso21090_en_qualifier.setter
    def iso21090_en_qualifier(self, value: Any) -> None:
        set_extension(self, ISO21090_EN_QUALIFIER_URL, value)

    @property
    def humanname_own_name(self) -> Any:
        return get_extension(self, HUMANNAME_OWN_NAME_URL)

    @humanname_own_name.setter
    def humanname_own_name(self, value: Any) -> None:
        set_extension(self, HUMANNAME_OWN_NAME_URL, value)

    @property
    def iso21090_en_use(self) -> Any:
        return get_extension(self, ISO21090_EN_USE_URL)

    @iso21090_en_use.setter
    def iso21090_en_use(self, value: Any) -> None:
        set_extension(self, ISO21090_EN_USE_URL, value)

    @property
    def humanname_fathers_family(self) -> Any:
        return get_extension(self, HUMANNAME_FATHERS_FAMILY_URL)

    @humanname_fathers_family.setter
    def humanname_fathers_family(self, value: Any) -> None:
        set_extension(self, HUMANNAME_FATHERS_FAMILY_URL, value)

    @property
    def humanname_partner_name(self) -> Any:
        return get_extension(self, HUMANNAME_PARTNER_NAME_URL)

    @humanname_partner_name.setter
    def humanname_partner_name(self, value: Any) -> None:
        set_extension(self, HUMANNAME_PARTNER_NAME_URL, value)

class Identifier(base.Identifier):

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

    @property
    def rendered_value(self) -> Any:
        return get_extension(self, RENDERED_VALUE_URL)

    @rendered_value.setter
    def rendered_value(self, value: Any) -> None:
        set_extension(self, RENDERED_VALUE_URL, value)

    @property
    def identifier_check_digit(self) -> Any:
        return get_extension(self, IDENTIFIER_CHECK_DIGIT_URL)

    @identifier_check_digit.setter
    def identifier_check_digit(self, value: Any) -> None:
        set_extension(self, IDENTIFIER_CHECK_DIGIT_URL, value)

    @property
    def identifier_valid_date(self) -> Any:
        return get_extension(self, IDENTIFIER_VALID_DATE_URL)

    @identifier_valid_date.setter
    def identifier_valid_date(self, value: Any) -> None:
        set_extension(self, IDENTIFIER_VALID_DATE_URL, value)

class ImagingStudy(base.ImagingStudy):

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

class Immunization(base.Immunization):

    @property
    def workflow_triggered_by(self) -> Any:
        return get_extension(self, WORKFLOW_TRIGGERED_BY_URL)

    @workflow_triggered_by.setter
    def workflow_triggered_by(self, value: Any) -> None:
        set_extension(self, WORKFLOW_TRIGGERED_BY_URL, value)

    @property
    def workflow_research_study(self) -> Any:
        return get_extension(self, WORKFLOW_RESEARCH_STUDY_URL)

    @workflow_research_study.setter
    def workflow_research_study(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RESEARCH_STUDY_URL, value)

    @property
    def immunization_procedure(self) -> Any:
        return get_extension(self, IMMUNIZATION_PROCEDURE_URL)

    @immunization_procedure.setter
    def immunization_procedure(self, value: Any) -> None:
        set_extension(self, IMMUNIZATION_PROCEDURE_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def workflow_adheres_to(self) -> Any:
        return get_extension(self, WORKFLOW_ADHERES_TO_URL)

    @workflow_adheres_to.setter
    def workflow_adheres_to(self, value: Any) -> None:
        set_extension(self, WORKFLOW_ADHERES_TO_URL, value)

class ImmunizationEvaluation(base.ImmunizationEvaluation):

    @property
    def workflow_generated_from(self) -> Any:
        return get_extension(self, WORKFLOW_GENERATED_FROM_URL)

    @workflow_generated_from.setter
    def workflow_generated_from(self, value: Any) -> None:
        set_extension(self, WORKFLOW_GENERATED_FROM_URL, value)

    @property
    def event_based_on(self) -> Any:
        return get_extension(self, EVENT_BASED_ON_URL)

    @event_based_on.setter
    def event_based_on(self, value: Any) -> None:
        set_extension(self, EVENT_BASED_ON_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def workflow_adheres_to(self) -> Any:
        return get_extension(self, WORKFLOW_ADHERES_TO_URL)

    @workflow_adheres_to.setter
    def workflow_adheres_to(self, value: Any) -> None:
        set_extension(self, WORKFLOW_ADHERES_TO_URL, value)

class ImmunizationRecommendation(base.ImmunizationRecommendation):

    @property
    def workflow_triggered_by(self) -> Any:
        return get_extension(self, WORKFLOW_TRIGGERED_BY_URL)

    @workflow_triggered_by.setter
    def workflow_triggered_by(self, value: Any) -> None:
        set_extension(self, WORKFLOW_TRIGGERED_BY_URL, value)

    @property
    def workflow_generated_from(self) -> Any:
        return get_extension(self, WORKFLOW_GENERATED_FROM_URL)

    @workflow_generated_from.setter
    def workflow_generated_from(self, value: Any) -> None:
        set_extension(self, WORKFLOW_GENERATED_FROM_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def workflow_complies_with(self) -> Any:
        return get_extension(self, WORKFLOW_COMPLIES_WITH_URL)

    @workflow_complies_with.setter
    def workflow_complies_with(self, value: Any) -> None:
        set_extension(self, WORKFLOW_COMPLIES_WITH_URL, value)

class ImplementationGuide(base.ImplementationGuide):

    @property
    def resource_approval_date(self) -> Any:
        return get_extension(self, RESOURCE_APPROVAL_DATE_URL)

    @resource_approval_date.setter
    def resource_approval_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_APPROVAL_DATE_URL, value)

    @property
    def cqf_model_info_settings(self) -> Any:
        return get_extension(self, CQF_MODEL_INFO_SETTINGS_URL)

    @cqf_model_info_settings.setter
    def cqf_model_info_settings(self, value: Any) -> None:
        set_extension(self, CQF_MODEL_INFO_SETTINGS_URL, value)

    @property
    def resource_last_review_date(self) -> Any:
        return get_extension(self, RESOURCE_LAST_REVIEW_DATE_URL)

    @resource_last_review_date.setter
    def resource_last_review_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_LAST_REVIEW_DATE_URL, value)

    @property
    def cqf_expansion_parameters(self) -> Any:
        return get_extension(self, CQF_EXPANSION_PARAMETERS_URL)

    @cqf_expansion_parameters.setter
    def cqf_expansion_parameters(self, value: Any) -> None:
        set_extension(self, CQF_EXPANSION_PARAMETERS_URL, value)

    @property
    def structuredefinition_standards_status(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_STANDARDS_STATUS_URL)

    @structuredefinition_standards_status.setter
    def structuredefinition_standards_status(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_STANDARDS_STATUS_URL, value)

    @property
    def resource_effective_period(self) -> Any:
        return get_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL)

    @resource_effective_period.setter
    def resource_effective_period(self, value: Any) -> None:
        set_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL, value)

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

    @property
    def implementationguide_source_file(self) -> Any:
        return get_extension(self, IMPLEMENTATIONGUIDE_SOURCE_FILE_URL)

    @implementationguide_source_file.setter
    def implementationguide_source_file(self, value: Any) -> None:
        set_extension(self, IMPLEMENTATIONGUIDE_SOURCE_FILE_URL, value)

class InventoryReport(base.InventoryReport):

    @property
    def event_based_on(self) -> Any:
        return get_extension(self, EVENT_BASED_ON_URL)

    @event_based_on.setter
    def event_based_on(self, value: Any) -> None:
        set_extension(self, EVENT_BASED_ON_URL, value)

class Invoice(base.Invoice):

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

class Library(base.Library):

    @property
    def cqf_test_artifact(self) -> Any:
        return get_extension(self, CQF_TEST_ARTIFACT_URL)

    @cqf_test_artifact.setter
    def cqf_test_artifact(self, value: Any) -> None:
        set_extension(self, CQF_TEST_ARTIFACT_URL, value)

    @property
    def cqf_model_info_settings(self) -> Any:
        return get_extension(self, CQF_MODEL_INFO_SETTINGS_URL)

    @cqf_model_info_settings.setter
    def cqf_model_info_settings(self, value: Any) -> None:
        set_extension(self, CQF_MODEL_INFO_SETTINGS_URL, value)

    @property
    def cqf_expansion_parameters(self) -> Any:
        return get_extension(self, CQF_EXPANSION_PARAMETERS_URL)

    @cqf_expansion_parameters.setter
    def cqf_expansion_parameters(self, value: Any) -> None:
        set_extension(self, CQF_EXPANSION_PARAMETERS_URL, value)

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

    @property
    def cqf_cql_options(self) -> Any:
        return get_extension(self, CQF_CQL_OPTIONS_URL)

    @cqf_cql_options.setter
    def cqf_cql_options(self, value: Any) -> None:
        set_extension(self, CQF_CQL_OPTIONS_URL, value)

    @property
    def cqf_input_parameters(self) -> Any:
        return get_extension(self, CQF_INPUT_PARAMETERS_URL)

    @cqf_input_parameters.setter
    def cqf_input_parameters(self, value: Any) -> None:
        set_extension(self, CQF_INPUT_PARAMETERS_URL, value)

    @property
    def cqf_part_of(self) -> Any:
        return get_extension(self, CQF_PART_OF_URL)

    @cqf_part_of.setter
    def cqf_part_of(self, value: Any) -> None:
        set_extension(self, CQF_PART_OF_URL, value)

class List(base.List):

    @property
    def list_change_base(self) -> Any:
        return get_extension(self, LIST_CHANGE_BASE_URL)

    @list_change_base.setter
    def list_change_base(self, value: Any) -> None:
        set_extension(self, LIST_CHANGE_BASE_URL, value)

    @property
    def list_for(self) -> Any:
        return get_extension(self, LIST_FOR_URL)

    @list_for.setter
    def list_for(self, value: Any) -> None:
        set_extension(self, LIST_FOR_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def list_category(self) -> Any:
        return get_extension(self, LIST_CATEGORY_URL)

    @list_category.setter
    def list_category(self, value: Any) -> None:
        set_extension(self, LIST_CATEGORY_URL, value)

class Location(base.Location):

    @property
    def location_communication(self) -> Any:
        return get_extension(self, LOCATION_COMMUNICATION_URL)

    @location_communication.setter
    def location_communication(self, value: Any) -> None:
        set_extension(self, LOCATION_COMMUNICATION_URL, value)

    @property
    def location_boundary_geojson(self) -> Any:
        return get_extension(self, LOCATION_BOUNDARY_GEOJSON_URL)

    @location_boundary_geojson.setter
    def location_boundary_geojson(self, value: Any) -> None:
        set_extension(self, LOCATION_BOUNDARY_GEOJSON_URL, value)

class Measure(base.Measure):

    @property
    def cqf_criteria_reference(self) -> Any:
        return get_extension(self, CQF_CRITERIA_REFERENCE_URL)

    @cqf_criteria_reference.setter
    def cqf_criteria_reference(self, value: Any) -> None:
        set_extension(self, CQF_CRITERIA_REFERENCE_URL, value)

    @property
    def artifact_is_owned(self) -> Any:
        return get_extension(self, ARTIFACT_IS_OWNED_URL)

    @artifact_is_owned.setter
    def artifact_is_owned(self, value: Any) -> None:
        set_extension(self, ARTIFACT_IS_OWNED_URL, value)

    @property
    def cqf_target_invariant(self) -> Any:
        return get_extension(self, CQF_TARGET_INVARIANT_URL)

    @cqf_target_invariant.setter
    def cqf_target_invariant(self, value: Any) -> None:
        set_extension(self, CQF_TARGET_INVARIANT_URL, value)

    @property
    def target_constraint(self) -> Any:
        return get_extension(self, TARGET_CONSTRAINT_URL)

    @target_constraint.setter
    def target_constraint(self, value: Any) -> None:
        set_extension(self, TARGET_CONSTRAINT_URL, value)

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

    @property
    def variable(self) -> Any:
        return get_extension(self, VARIABLE_URL)

    @variable.setter
    def variable(self, value: Any) -> None:
        set_extension(self, VARIABLE_URL, value)

    @property
    def cqf_improvement_notation_guidance(self) -> Any:
        return get_extension(self, CQF_IMPROVEMENT_NOTATION_GUIDANCE_URL)

    @cqf_improvement_notation_guidance.setter
    def cqf_improvement_notation_guidance(self, value: Any) -> None:
        set_extension(self, CQF_IMPROVEMENT_NOTATION_GUIDANCE_URL, value)

    @property
    def workflow_shall_comply_with(self) -> Any:
        return get_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL)

    @workflow_shall_comply_with.setter
    def workflow_shall_comply_with(self, value: Any) -> None:
        set_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL, value)

class MeasureReport(base.MeasureReport):

    @property
    def measurereport_population_description(self) -> Any:
        return get_extension(self, MEASUREREPORT_POPULATION_DESCRIPTION_URL)

    @measurereport_population_description.setter
    def measurereport_population_description(self, value: Any) -> None:
        set_extension(self, MEASUREREPORT_POPULATION_DESCRIPTION_URL, value)

    @property
    def cqf_criteria_reference(self) -> Any:
        return get_extension(self, CQF_CRITERIA_REFERENCE_URL)

    @cqf_criteria_reference.setter
    def cqf_criteria_reference(self, value: Any) -> None:
        set_extension(self, CQF_CRITERIA_REFERENCE_URL, value)

    @property
    def measurereport_category(self) -> Any:
        return get_extension(self, MEASUREREPORT_CATEGORY_URL)

    @measurereport_category.setter
    def measurereport_category(self, value: Any) -> None:
        set_extension(self, MEASUREREPORT_CATEGORY_URL, value)

    @property
    def measurereport_count_quantity(self) -> Any:
        return get_extension(self, MEASUREREPORT_COUNT_QUANTITY_URL)

    @measurereport_count_quantity.setter
    def measurereport_count_quantity(self, value: Any) -> None:
        set_extension(self, MEASUREREPORT_COUNT_QUANTITY_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def cqf_input_parameters(self) -> Any:
        return get_extension(self, CQF_INPUT_PARAMETERS_URL)

    @cqf_input_parameters.setter
    def cqf_input_parameters(self, value: Any) -> None:
        set_extension(self, CQF_INPUT_PARAMETERS_URL, value)

    @property
    def cqf_improvement_notation_guidance(self) -> Any:
        return get_extension(self, CQF_IMPROVEMENT_NOTATION_GUIDANCE_URL)

    @cqf_improvement_notation_guidance.setter
    def cqf_improvement_notation_guidance(self, value: Any) -> None:
        set_extension(self, CQF_IMPROVEMENT_NOTATION_GUIDANCE_URL, value)

class Medication(base.Medication):

    @property
    def medication_manufacturing_batch(self) -> Any:
        return get_extension(self, MEDICATION_MANUFACTURING_BATCH_URL)

    @medication_manufacturing_batch.setter
    def medication_manufacturing_batch(self, value: Any) -> None:
        set_extension(self, MEDICATION_MANUFACTURING_BATCH_URL, value)

class MedicationAdministration(base.MedicationAdministration):

    @property
    def workflow_research_study(self) -> Any:
        return get_extension(self, WORKFLOW_RESEARCH_STUDY_URL)

    @workflow_research_study.setter
    def workflow_research_study(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RESEARCH_STUDY_URL, value)

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

class MedicationDispense(base.MedicationDispense):

    @property
    def medicationdispense_refills_remaining(self) -> Any:
        return get_extension(self, MEDICATIONDISPENSE_REFILLS_REMAINING_URL)

    @medicationdispense_refills_remaining.setter
    def medicationdispense_refills_remaining(self, value: Any) -> None:
        set_extension(self, MEDICATIONDISPENSE_REFILLS_REMAINING_URL, value)

    @property
    def workflow_research_study(self) -> Any:
        return get_extension(self, WORKFLOW_RESEARCH_STUDY_URL)

    @workflow_research_study.setter
    def workflow_research_study(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RESEARCH_STUDY_URL, value)

    @property
    def medicationdispense_quantity_remaining(self) -> Any:
        return get_extension(self, MEDICATIONDISPENSE_QUANTITY_REMAINING_URL)

    @medicationdispense_quantity_remaining.setter
    def medicationdispense_quantity_remaining(self, value: Any) -> None:
        set_extension(self, MEDICATIONDISPENSE_QUANTITY_REMAINING_URL, value)

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

class MedicationRequest(base.MedicationRequest):

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

class MedicationStatement(base.MedicationStatement):

    @property
    def workflow_research_study(self) -> Any:
        return get_extension(self, WORKFLOW_RESEARCH_STUDY_URL)

    @workflow_research_study.setter
    def workflow_research_study(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RESEARCH_STUDY_URL, value)

    @property
    def event_based_on(self) -> Any:
        return get_extension(self, EVENT_BASED_ON_URL)

    @event_based_on.setter
    def event_based_on(self, value: Any) -> None:
        set_extension(self, EVENT_BASED_ON_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

class MessageDefinition(base.MessageDefinition):

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class MessageHeader(base.MessageHeader):

    @property
    def messageheader_response_request(self) -> Any:
        return get_extension(self, MESSAGEHEADER_RESPONSE_REQUEST_URL)

    @messageheader_response_request.setter
    def messageheader_response_request(self, value: Any) -> None:
        set_extension(self, MESSAGEHEADER_RESPONSE_REQUEST_URL, value)

class Meta(base.Meta):

    @property
    def last_source_sync(self) -> Any:
        return get_extension(self, LAST_SOURCE_SYNC_URL)

    @last_source_sync.setter
    def last_source_sync(self, value: Any) -> None:
        set_extension(self, LAST_SOURCE_SYNC_URL, value)

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

    @property
    def timezone(self) -> Any:
        return get_extension(self, TIMEZONE_URL)

    @timezone.setter
    def timezone(self, value: Any) -> None:
        set_extension(self, TIMEZONE_URL, value)

    @property
    def first_created(self) -> Any:
        return get_extension(self, FIRST_CREATED_URL)

    @first_created.setter
    def first_created(self, value: Any) -> None:
        set_extension(self, FIRST_CREATED_URL, value)

class MetadataResource(base.MetadataResource):

    @property
    def metadataresource_publish_date(self) -> Any:
        return get_extension(self, METADATARESOURCE_PUBLISH_DATE_URL)

    @metadataresource_publish_date.setter
    def metadataresource_publish_date(self, value: Any) -> None:
        set_extension(self, METADATARESOURCE_PUBLISH_DATE_URL, value)

class MolecularSequence(base.MolecularSequence):

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

class Money(base.Money):

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

class NamingSystem(base.NamingSystem):

    @property
    def resource_approval_date(self) -> Any:
        return get_extension(self, RESOURCE_APPROVAL_DATE_URL)

    @resource_approval_date.setter
    def resource_approval_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_APPROVAL_DATE_URL, value)

    @property
    def resource_last_review_date(self) -> Any:
        return get_extension(self, RESOURCE_LAST_REVIEW_DATE_URL)

    @resource_last_review_date.setter
    def resource_last_review_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_LAST_REVIEW_DATE_URL, value)

    @property
    def resource_effective_period(self) -> Any:
        return get_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL)

    @resource_effective_period.setter
    def resource_effective_period(self, value: Any) -> None:
        set_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL, value)

    @property
    def namingsystem_check_digit(self) -> Any:
        return get_extension(self, NAMINGSYSTEM_CHECK_DIGIT_URL)

    @namingsystem_check_digit.setter
    def namingsystem_check_digit(self, value: Any) -> None:
        set_extension(self, NAMINGSYSTEM_CHECK_DIGIT_URL, value)

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class NutritionIntake(base.NutritionIntake):

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

class NutritionOrder(base.NutritionOrder):

    @property
    def workflow_triggered_by(self) -> Any:
        return get_extension(self, WORKFLOW_TRIGGERED_BY_URL)

    @workflow_triggered_by.setter
    def workflow_triggered_by(self, value: Any) -> None:
        set_extension(self, WORKFLOW_TRIGGERED_BY_URL, value)

    @property
    def workflow_generated_from(self) -> Any:
        return get_extension(self, WORKFLOW_GENERATED_FROM_URL)

    @workflow_generated_from.setter
    def workflow_generated_from(self, value: Any) -> None:
        set_extension(self, WORKFLOW_GENERATED_FROM_URL, value)

    @property
    def request_insurance(self) -> Any:
        return get_extension(self, REQUEST_INSURANCE_URL)

    @request_insurance.setter
    def request_insurance(self, value: Any) -> None:
        set_extension(self, REQUEST_INSURANCE_URL, value)

    @property
    def request_do_not_perform(self) -> Any:
        return get_extension(self, REQUEST_DO_NOT_PERFORM_URL)

    @request_do_not_perform.setter
    def request_do_not_perform(self, value: Any) -> None:
        set_extension(self, REQUEST_DO_NOT_PERFORM_URL, value)

    @property
    def request_replaces(self) -> Any:
        return get_extension(self, REQUEST_REPLACES_URL)

    @request_replaces.setter
    def request_replaces(self, value: Any) -> None:
        set_extension(self, REQUEST_REPLACES_URL, value)

    @property
    def nutritionorder_adaptive_feeding_device(self) -> Any:
        return get_extension(self, NUTRITIONORDER_ADAPTIVE_FEEDING_DEVICE_URL)

    @nutritionorder_adaptive_feeding_device.setter
    def nutritionorder_adaptive_feeding_device(self, value: Any) -> None:
        set_extension(self, NUTRITIONORDER_ADAPTIVE_FEEDING_DEVICE_URL, value)

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

    @property
    def request_relevant_history(self) -> Any:
        return get_extension(self, REQUEST_RELEVANT_HISTORY_URL)

    @request_relevant_history.setter
    def request_relevant_history(self, value: Any) -> None:
        set_extension(self, REQUEST_RELEVANT_HISTORY_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def workflow_reason(self) -> Any:
        return get_extension(self, WORKFLOW_REASON_URL)

    @workflow_reason.setter
    def workflow_reason(self, value: Any) -> None:
        set_extension(self, WORKFLOW_REASON_URL, value)

    @property
    def workflow_complies_with(self) -> Any:
        return get_extension(self, WORKFLOW_COMPLIES_WITH_URL)

    @workflow_complies_with.setter
    def workflow_complies_with(self, value: Any) -> None:
        set_extension(self, WORKFLOW_COMPLIES_WITH_URL, value)

    @property
    def request_status_reason(self) -> Any:
        return get_extension(self, REQUEST_STATUS_REASON_URL)

    @request_status_reason.setter
    def request_status_reason(self, value: Any) -> None:
        set_extension(self, REQUEST_STATUS_REASON_URL, value)

class Observation(base.Observation):

    @property
    def workflow_triggered_by(self) -> Any:
        return get_extension(self, WORKFLOW_TRIGGERED_BY_URL)

    @workflow_triggered_by.setter
    def workflow_triggered_by(self, value: Any) -> None:
        set_extension(self, WORKFLOW_TRIGGERED_BY_URL, value)

    @property
    def event_performer_function(self) -> Any:
        return get_extension(self, EVENT_PERFORMER_FUNCTION_URL)

    @event_performer_function.setter
    def event_performer_function(self, value: Any) -> None:
        set_extension(self, EVENT_PERFORMER_FUNCTION_URL, value)

    @property
    def observation_body_position(self) -> Any:
        return get_extension(self, OBSERVATION_BODY_POSITION_URL)

    @observation_body_position.setter
    def observation_body_position(self, value: Any) -> None:
        set_extension(self, OBSERVATION_BODY_POSITION_URL, value)

    @property
    def observation_specimen_code(self) -> Any:
        return get_extension(self, OBSERVATION_SPECIMEN_CODE_URL)

    @observation_specimen_code.setter
    def observation_specimen_code(self, value: Any) -> None:
        set_extension(self, OBSERVATION_SPECIMEN_CODE_URL, value)

    @property
    def observation_nature_of_abnormal_test(self) -> Any:
        return get_extension(self, OBSERVATION_NATURE_OF_ABNORMAL_TEST_URL)

    @observation_nature_of_abnormal_test.setter
    def observation_nature_of_abnormal_test(self, value: Any) -> None:
        set_extension(self, OBSERVATION_NATURE_OF_ABNORMAL_TEST_URL, value)

    @property
    def observation_analysis_date_time(self) -> Any:
        return get_extension(self, OBSERVATION_ANALYSIS_DATE_TIME_URL)

    @observation_analysis_date_time.setter
    def observation_analysis_date_time(self, value: Any) -> None:
        set_extension(self, OBSERVATION_ANALYSIS_DATE_TIME_URL, value)

    @property
    def observation_reagent(self) -> Any:
        return get_extension(self, OBSERVATION_REAGENT_URL)

    @observation_reagent.setter
    def observation_reagent(self, value: Any) -> None:
        set_extension(self, OBSERVATION_REAGENT_URL, value)

    @property
    def workflow_research_study(self) -> Any:
        return get_extension(self, WORKFLOW_RESEARCH_STUDY_URL)

    @workflow_research_study.setter
    def workflow_research_study(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RESEARCH_STUDY_URL, value)

    @property
    def observation_replaces(self) -> Any:
        return get_extension(self, OBSERVATION_REPLACES_URL)

    @observation_replaces.setter
    def observation_replaces(self, value: Any) -> None:
        set_extension(self, OBSERVATION_REPLACES_URL, value)

    @property
    def observation_v2_subid(self) -> Any:
        return get_extension(self, OBSERVATION_V2_SUBID_URL)

    @observation_v2_subid.setter
    def observation_v2_subid(self, value: Any) -> None:
        set_extension(self, OBSERVATION_V2_SUBID_URL, value)

    @property
    def observation_device_code(self) -> Any:
        return get_extension(self, OBSERVATION_DEVICE_CODE_URL)

    @observation_device_code.setter
    def observation_device_code(self, value: Any) -> None:
        set_extension(self, OBSERVATION_DEVICE_CODE_URL, value)

    @property
    def diagnostic_report_risk(self) -> Any:
        return get_extension(self, DIAGNOSTIC_REPORT_RISK_URL)

    @diagnostic_report_risk.setter
    def diagnostic_report_risk(self, value: Any) -> None:
        set_extension(self, DIAGNOSTIC_REPORT_RISK_URL, value)

    @property
    def observation_sequel_to(self) -> Any:
        return get_extension(self, OBSERVATION_SEQUEL_TO_URL)

    @observation_sequel_to.setter
    def observation_sequel_to(self, value: Any) -> None:
        set_extension(self, OBSERVATION_SEQUEL_TO_URL, value)

    @property
    def workflow_related_artifact(self) -> Any:
        return get_extension(self, WORKFLOW_RELATED_ARTIFACT_URL)

    @workflow_related_artifact.setter
    def workflow_related_artifact(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELATED_ARTIFACT_URL, value)

    @property
    def observation_precondition(self) -> Any:
        return get_extension(self, OBSERVATION_PRECONDITION_URL)

    @observation_precondition.setter
    def observation_precondition(self, value: Any) -> None:
        set_extension(self, OBSERVATION_PRECONDITION_URL, value)

    @property
    def observation_delta(self) -> Any:
        return get_extension(self, OBSERVATION_DELTA_URL)

    @observation_delta.setter
    def observation_delta(self, value: Any) -> None:
        set_extension(self, OBSERVATION_DELTA_URL, value)

    @property
    def workflow_supporting_info(self) -> Any:
        return get_extension(self, WORKFLOW_SUPPORTING_INFO_URL)

    @workflow_supporting_info.setter
    def workflow_supporting_info(self, value: Any) -> None:
        set_extension(self, WORKFLOW_SUPPORTING_INFO_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def event_status_reason(self) -> Any:
        return get_extension(self, EVENT_STATUS_REASON_URL)

    @event_status_reason.setter
    def event_status_reason(self, value: Any) -> None:
        set_extension(self, EVENT_STATUS_REASON_URL, value)

    @property
    def observation_focus_code(self) -> Any:
        return get_extension(self, OBSERVATION_FOCUS_CODE_URL)

    @observation_focus_code.setter
    def observation_focus_code(self, value: Any) -> None:
        set_extension(self, OBSERVATION_FOCUS_CODE_URL, value)

    @property
    def observation_secondary_finding(self) -> Any:
        return get_extension(self, OBSERVATION_SECONDARY_FINDING_URL)

    @observation_secondary_finding.setter
    def observation_secondary_finding(self, value: Any) -> None:
        set_extension(self, OBSERVATION_SECONDARY_FINDING_URL, value)

    @property
    def observation_gateway_device(self) -> Any:
        return get_extension(self, OBSERVATION_GATEWAY_DEVICE_URL)

    @observation_gateway_device.setter
    def observation_gateway_device(self, value: Any) -> None:
        set_extension(self, OBSERVATION_GATEWAY_DEVICE_URL, value)

    @property
    def workflow_reason(self) -> Any:
        return get_extension(self, WORKFLOW_REASON_URL)

    @workflow_reason.setter
    def workflow_reason(self, value: Any) -> None:
        set_extension(self, WORKFLOW_REASON_URL, value)

    @property
    def observation_time_offset(self) -> Any:
        return get_extension(self, OBSERVATION_TIME_OFFSET_URL)

    @observation_time_offset.setter
    def observation_time_offset(self, value: Any) -> None:
        set_extension(self, OBSERVATION_TIME_OFFSET_URL, value)

    @property
    def workflow_adheres_to(self) -> Any:
        return get_extension(self, WORKFLOW_ADHERES_TO_URL)

    @workflow_adheres_to.setter
    def workflow_adheres_to(self, value: Any) -> None:
        set_extension(self, WORKFLOW_ADHERES_TO_URL, value)

    @property
    def event_event_history(self) -> Any:
        return get_extension(self, EVENT_EVENT_HISTORY_URL)

    @event_event_history.setter
    def event_event_history(self, value: Any) -> None:
        set_extension(self, EVENT_EVENT_HISTORY_URL, value)

    @property
    def workflow_shall_comply_with(self) -> Any:
        return get_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL)

    @workflow_shall_comply_with.setter
    def workflow_shall_comply_with(self, value: Any) -> None:
        set_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL, value)

    @property
    def event_location(self) -> Any:
        return get_extension(self, EVENT_LOCATION_URL)

    @event_location.setter
    def event_location(self, value: Any) -> None:
        set_extension(self, EVENT_LOCATION_URL, value)

class ObservationDefinition(base.ObservationDefinition):

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class OperationDefinition(base.OperationDefinition):

    @property
    def resource_approval_date(self) -> Any:
        return get_extension(self, RESOURCE_APPROVAL_DATE_URL)

    @resource_approval_date.setter
    def resource_approval_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_APPROVAL_DATE_URL, value)

    @property
    def resource_last_review_date(self) -> Any:
        return get_extension(self, RESOURCE_LAST_REVIEW_DATE_URL)

    @resource_last_review_date.setter
    def resource_last_review_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_LAST_REVIEW_DATE_URL, value)

    @property
    def structuredefinition_standards_status(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_STANDARDS_STATUS_URL)

    @structuredefinition_standards_status.setter
    def structuredefinition_standards_status(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_STANDARDS_STATUS_URL, value)

    @property
    def resource_effective_period(self) -> Any:
        return get_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL)

    @resource_effective_period.setter
    def resource_effective_period(self, value: Any) -> None:
        set_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL, value)

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

    @property
    def elementdefinition_binding_name(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_BINDING_NAME_URL)

    @elementdefinition_binding_name.setter
    def elementdefinition_binding_name(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_BINDING_NAME_URL, value)

    @property
    def workflow_shall_comply_with(self) -> Any:
        return get_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL)

    @workflow_shall_comply_with.setter
    def workflow_shall_comply_with(self, value: Any) -> None:
        set_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL, value)

    @property
    def operationdefinition_profile(self) -> Any:
        return get_extension(self, OPERATIONDEFINITION_PROFILE_URL)

    @operationdefinition_profile.setter
    def operationdefinition_profile(self, value: Any) -> None:
        set_extension(self, OPERATIONDEFINITION_PROFILE_URL, value)

class OperationOutcome(base.OperationOutcome):

    @property
    def operationoutcome_file(self) -> Any:
        return get_extension(self, OPERATIONOUTCOME_FILE_URL)

    @operationoutcome_file.setter
    def operationoutcome_file(self, value: Any) -> None:
        set_extension(self, OPERATIONOUTCOME_FILE_URL, value)

    @property
    def operationoutcome_issue_source(self) -> Any:
        return get_extension(self, OPERATIONOUTCOME_ISSUE_SOURCE_URL)

    @operationoutcome_issue_source.setter
    def operationoutcome_issue_source(self, value: Any) -> None:
        set_extension(self, OPERATIONOUTCOME_ISSUE_SOURCE_URL, value)

    @property
    def operationoutcome_detected_issue(self) -> Any:
        return get_extension(self, OPERATIONOUTCOME_DETECTED_ISSUE_URL)

    @operationoutcome_detected_issue.setter
    def operationoutcome_detected_issue(self, value: Any) -> None:
        set_extension(self, OPERATIONOUTCOME_DETECTED_ISSUE_URL, value)

    @property
    def operationoutcome_issue_col(self) -> Any:
        return get_extension(self, OPERATIONOUTCOME_ISSUE_COL_URL)

    @operationoutcome_issue_col.setter
    def operationoutcome_issue_col(self, value: Any) -> None:
        set_extension(self, OPERATIONOUTCOME_ISSUE_COL_URL, value)

    @property
    def operationoutcome_issue_slicetext(self) -> Any:
        return get_extension(self, OPERATIONOUTCOME_ISSUE_SLICETEXT_URL)

    @operationoutcome_issue_slicetext.setter
    def operationoutcome_issue_slicetext(self, value: Any) -> None:
        set_extension(self, OPERATIONOUTCOME_ISSUE_SLICETEXT_URL, value)

    @property
    def operationoutcome_message_id(self) -> Any:
        return get_extension(self, OPERATIONOUTCOME_MESSAGE_ID_URL)

    @operationoutcome_message_id.setter
    def operationoutcome_message_id(self, value: Any) -> None:
        set_extension(self, OPERATIONOUTCOME_MESSAGE_ID_URL, value)

    @property
    def operationoutcome_issue_server(self) -> Any:
        return get_extension(self, OPERATIONOUTCOME_ISSUE_SERVER_URL)

    @operationoutcome_issue_server.setter
    def operationoutcome_issue_server(self, value: Any) -> None:
        set_extension(self, OPERATIONOUTCOME_ISSUE_SERVER_URL, value)

    @property
    def operationoutcome_issue_line(self) -> Any:
        return get_extension(self, OPERATIONOUTCOME_ISSUE_LINE_URL)

    @operationoutcome_issue_line.setter
    def operationoutcome_issue_line(self, value: Any) -> None:
        set_extension(self, OPERATIONOUTCOME_ISSUE_LINE_URL, value)

    @property
    def operationoutcome_authority(self) -> Any:
        return get_extension(self, OPERATIONOUTCOME_AUTHORITY_URL)

    @operationoutcome_authority.setter
    def operationoutcome_authority(self, value: Any) -> None:
        set_extension(self, OPERATIONOUTCOME_AUTHORITY_URL, value)

class Organization(base.Organization):

    @property
    def organization_preferred_contact(self) -> Any:
        return get_extension(self, ORGANIZATION_PREFERRED_CONTACT_URL)

    @organization_preferred_contact.setter
    def organization_preferred_contact(self, value: Any) -> None:
        set_extension(self, ORGANIZATION_PREFERRED_CONTACT_URL, value)

    @property
    def organization_brand(self) -> Any:
        return get_extension(self, ORGANIZATION_BRAND_URL)

    @organization_brand.setter
    def organization_brand(self, value: Any) -> None:
        set_extension(self, ORGANIZATION_BRAND_URL, value)

    @property
    def organization_period(self) -> Any:
        return get_extension(self, ORGANIZATION_PERIOD_URL)

    @organization_period.setter
    def organization_period(self, value: Any) -> None:
        set_extension(self, ORGANIZATION_PERIOD_URL, value)

    @property
    def organization_portal(self) -> Any:
        return get_extension(self, ORGANIZATION_PORTAL_URL)

    @organization_portal.setter
    def organization_portal(self, value: Any) -> None:
        set_extension(self, ORGANIZATION_PORTAL_URL, value)

class OrganizationAffiliation(base.OrganizationAffiliation):

    @property
    def organizationaffiliation_primary_ind(self) -> Any:
        return get_extension(self, ORGANIZATIONAFFILIATION_PRIMARY_IND_URL)

    @organizationaffiliation_primary_ind.setter
    def organizationaffiliation_primary_ind(self, value: Any) -> None:
        set_extension(self, ORGANIZATIONAFFILIATION_PRIMARY_IND_URL, value)

class ParameterDefinition(base.ParameterDefinition):

    @property
    def cqf_cql_access_modifier(self) -> Any:
        return get_extension(self, CQF_CQL_ACCESS_MODIFIER_URL)

    @cqf_cql_access_modifier.setter
    def cqf_cql_access_modifier(self, value: Any) -> None:
        set_extension(self, CQF_CQL_ACCESS_MODIFIER_URL, value)

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

    @property
    def cqf_cql_type(self) -> Any:
        return get_extension(self, CQF_CQL_TYPE_URL)

    @cqf_cql_type.setter
    def cqf_cql_type(self, value: Any) -> None:
        set_extension(self, CQF_CQL_TYPE_URL, value)

    @property
    def cqf_is_prefetch_token(self) -> Any:
        return get_extension(self, CQF_IS_PREFETCH_TOKEN_URL)

    @cqf_is_prefetch_token.setter
    def cqf_is_prefetch_token(self, value: Any) -> None:
        set_extension(self, CQF_IS_PREFETCH_TOKEN_URL, value)

    @property
    def cqf_default_value(self) -> Any:
        return get_extension(self, CQF_DEFAULT_VALUE_URL)

    @cqf_default_value.setter
    def cqf_default_value(self, value: Any) -> None:
        set_extension(self, CQF_DEFAULT_VALUE_URL, value)

class Parameters(base.Parameters):

    @property
    def parameters_full_url(self) -> Any:
        return get_extension(self, PARAMETERS_FULL_URL_URL)

    @parameters_full_url.setter
    def parameters_full_url(self, value: Any) -> None:
        set_extension(self, PARAMETERS_FULL_URL_URL, value)

    @property
    def cqf_cql_type(self) -> Any:
        return get_extension(self, CQF_CQL_TYPE_URL)

    @cqf_cql_type.setter
    def cqf_cql_type(self, value: Any) -> None:
        set_extension(self, CQF_CQL_TYPE_URL, value)

    @property
    def parameters_definition(self) -> Any:
        return get_extension(self, PARAMETERS_DEFINITION_URL)

    @parameters_definition.setter
    def parameters_definition(self, value: Any) -> None:
        set_extension(self, PARAMETERS_DEFINITION_URL, value)

class Patient(base.Patient):

    @property
    def patient_proficiency(self) -> Any:
        return get_extension(self, PATIENT_PROFICIENCY_URL)

    @patient_proficiency.setter
    def patient_proficiency(self, value: Any) -> None:
        set_extension(self, PATIENT_PROFICIENCY_URL, value)

    @property
    def patient_multiple_birth_total(self) -> Any:
        return get_extension(self, PATIENT_MULTIPLE_BIRTH_TOTAL_URL)

    @patient_multiple_birth_total.setter
    def patient_multiple_birth_total(self, value: Any) -> None:
        set_extension(self, PATIENT_MULTIPLE_BIRTH_TOTAL_URL, value)

    @property
    def patient_importance(self) -> Any:
        return get_extension(self, PATIENT_IMPORTANCE_URL)

    @patient_importance.setter
    def patient_importance(self, value: Any) -> None:
        set_extension(self, PATIENT_IMPORTANCE_URL, value)

    @property
    def patient_congregation(self) -> Any:
        return get_extension(self, PATIENT_CONGREGATION_URL)

    @patient_congregation.setter
    def patient_congregation(self, value: Any) -> None:
        set_extension(self, PATIENT_CONGREGATION_URL, value)

    @property
    def patient_disability(self) -> Any:
        return get_extension(self, PATIENT_DISABILITY_URL)

    @patient_disability.setter
    def patient_disability(self, value: Any) -> None:
        set_extension(self, PATIENT_DISABILITY_URL, value)

    @property
    def patient_mothers_maiden_name(self) -> Any:
        return get_extension(self, PATIENT_MOTHERS_MAIDEN_NAME_URL)

    @patient_mothers_maiden_name.setter
    def patient_mothers_maiden_name(self, value: Any) -> None:
        set_extension(self, PATIENT_MOTHERS_MAIDEN_NAME_URL, value)

    @property
    def patient_contact_priority(self) -> Any:
        return get_extension(self, PATIENT_CONTACT_PRIORITY_URL)

    @patient_contact_priority.setter
    def patient_contact_priority(self, value: Any) -> None:
        set_extension(self, PATIENT_CONTACT_PRIORITY_URL, value)

    @property
    def patient_birth_place(self) -> Any:
        return get_extension(self, PATIENT_BIRTH_PLACE_URL)

    @patient_birth_place.setter
    def patient_birth_place(self, value: Any) -> None:
        set_extension(self, PATIENT_BIRTH_PLACE_URL, value)

    @property
    def patient_preference_type(self) -> Any:
        return get_extension(self, PATIENT_PREFERENCE_TYPE_URL)

    @patient_preference_type.setter
    def patient_preference_type(self, value: Any) -> None:
        set_extension(self, PATIENT_PREFERENCE_TYPE_URL, value)

    @property
    def patient_religion(self) -> Any:
        return get_extension(self, PATIENT_RELIGION_URL)

    @patient_religion.setter
    def patient_religion(self, value: Any) -> None:
        set_extension(self, PATIENT_RELIGION_URL, value)

    @property
    def patient_related_person(self) -> Any:
        return get_extension(self, PATIENT_RELATED_PERSON_URL)

    @patient_related_person.setter
    def patient_related_person(self, value: Any) -> None:
        set_extension(self, PATIENT_RELATED_PERSON_URL, value)

    @property
    def individual_pronouns(self) -> Any:
        return get_extension(self, INDIVIDUAL_PRONOUNS_URL)

    @individual_pronouns.setter
    def individual_pronouns(self, value: Any) -> None:
        set_extension(self, INDIVIDUAL_PRONOUNS_URL, value)

    @property
    def patient_known_non_duplicate(self) -> Any:
        return get_extension(self, PATIENT_KNOWN_NON_DUPLICATE_URL)

    @patient_known_non_duplicate.setter
    def patient_known_non_duplicate(self, value: Any) -> None:
        set_extension(self, PATIENT_KNOWN_NON_DUPLICATE_URL, value)

    @property
    def patient_birth_time(self) -> Any:
        return get_extension(self, PATIENT_BIRTH_TIME_URL)

    @patient_birth_time.setter
    def patient_birth_time(self, value: Any) -> None:
        set_extension(self, PATIENT_BIRTH_TIME_URL, value)

    @property
    def individual_gender_identity(self) -> Any:
        return get_extension(self, INDIVIDUAL_GENDER_IDENTITY_URL)

    @individual_gender_identity.setter
    def individual_gender_identity(self, value: Any) -> None:
        set_extension(self, INDIVIDUAL_GENDER_IDENTITY_URL, value)

    @property
    def patient_nationality(self) -> Any:
        return get_extension(self, PATIENT_NATIONALITY_URL)

    @patient_nationality.setter
    def patient_nationality(self, value: Any) -> None:
        set_extension(self, PATIENT_NATIONALITY_URL, value)

    @property
    def patient_born_status(self) -> Any:
        return get_extension(self, PATIENT_BORN_STATUS_URL)

    @patient_born_status.setter
    def patient_born_status(self, value: Any) -> None:
        set_extension(self, PATIENT_BORN_STATUS_URL, value)

    @property
    def patient_adoption_info(self) -> Any:
        return get_extension(self, PATIENT_ADOPTION_INFO_URL)

    @patient_adoption_info.setter
    def patient_adoption_info(self, value: Any) -> None:
        set_extension(self, PATIENT_ADOPTION_INFO_URL, value)

    @property
    def patient_unknown_identity(self) -> Any:
        return get_extension(self, PATIENT_UNKNOWN_IDENTITY_URL)

    @patient_unknown_identity.setter
    def patient_unknown_identity(self, value: Any) -> None:
        set_extension(self, PATIENT_UNKNOWN_IDENTITY_URL, value)

    @property
    def patient_cadaveric_donor(self) -> Any:
        return get_extension(self, PATIENT_CADAVERIC_DONOR_URL)

    @patient_cadaveric_donor.setter
    def patient_cadaveric_donor(self, value: Any) -> None:
        set_extension(self, PATIENT_CADAVERIC_DONOR_URL, value)

    @property
    def patient_animal(self) -> Any:
        return get_extension(self, PATIENT_ANIMAL_URL)

    @patient_animal.setter
    def patient_animal(self, value: Any) -> None:
        set_extension(self, PATIENT_ANIMAL_URL, value)

    @property
    def patient_citizenship(self) -> Any:
        return get_extension(self, PATIENT_CITIZENSHIP_URL)

    @patient_citizenship.setter
    def patient_citizenship(self, value: Any) -> None:
        set_extension(self, PATIENT_CITIZENSHIP_URL, value)

    @property
    def patient_interpreter_required(self) -> Any:
        return get_extension(self, PATIENT_INTERPRETER_REQUIRED_URL)

    @patient_interpreter_required.setter
    def patient_interpreter_required(self, value: Any) -> None:
        set_extension(self, PATIENT_INTERPRETER_REQUIRED_URL, value)

    @property
    def individual_recorded_sex_or_gender(self) -> Any:
        return get_extension(self, INDIVIDUAL_RECORDED_SEX_OR_GENDER_URL)

    @individual_recorded_sex_or_gender.setter
    def individual_recorded_sex_or_gender(self, value: Any) -> None:
        set_extension(self, INDIVIDUAL_RECORDED_SEX_OR_GENDER_URL, value)

class PaymentNotice(base.PaymentNotice):

    @property
    def event_based_on(self) -> Any:
        return get_extension(self, EVENT_BASED_ON_URL)

    @event_based_on.setter
    def event_based_on(self, value: Any) -> None:
        set_extension(self, EVENT_BASED_ON_URL, value)

class PaymentReconciliation(base.PaymentReconciliation):

    @property
    def event_based_on(self) -> Any:
        return get_extension(self, EVENT_BASED_ON_URL)

    @event_based_on.setter
    def event_based_on(self, value: Any) -> None:
        set_extension(self, EVENT_BASED_ON_URL, value)

class Period(base.Period):

    @property
    def artifact_period_duration(self) -> Any:
        return get_extension(self, ARTIFACT_PERIOD_DURATION_URL)

    @artifact_period_duration.setter
    def artifact_period_duration(self, value: Any) -> None:
        set_extension(self, ARTIFACT_PERIOD_DURATION_URL, value)

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

class Person(base.Person):

    @property
    def patient_proficiency(self) -> Any:
        return get_extension(self, PATIENT_PROFICIENCY_URL)

    @patient_proficiency.setter
    def patient_proficiency(self, value: Any) -> None:
        set_extension(self, PATIENT_PROFICIENCY_URL, value)

    @property
    def individual_pronouns(self) -> Any:
        return get_extension(self, INDIVIDUAL_PRONOUNS_URL)

    @individual_pronouns.setter
    def individual_pronouns(self, value: Any) -> None:
        set_extension(self, INDIVIDUAL_PRONOUNS_URL, value)

    @property
    def individual_gender_identity(self) -> Any:
        return get_extension(self, INDIVIDUAL_GENDER_IDENTITY_URL)

    @individual_gender_identity.setter
    def individual_gender_identity(self, value: Any) -> None:
        set_extension(self, INDIVIDUAL_GENDER_IDENTITY_URL, value)

    @property
    def individual_recorded_sex_or_gender(self) -> Any:
        return get_extension(self, INDIVIDUAL_RECORDED_SEX_OR_GENDER_URL)

    @individual_recorded_sex_or_gender.setter
    def individual_recorded_sex_or_gender(self, value: Any) -> None:
        set_extension(self, INDIVIDUAL_RECORDED_SEX_OR_GENDER_URL, value)

class PlanDefinition(base.PlanDefinition):

    @property
    def artifact_is_owned(self) -> Any:
        return get_extension(self, ARTIFACT_IS_OWNED_URL)

    @artifact_is_owned.setter
    def artifact_is_owned(self, value: Any) -> None:
        set_extension(self, ARTIFACT_IS_OWNED_URL, value)

    @property
    def cqf_target_invariant(self) -> Any:
        return get_extension(self, CQF_TARGET_INVARIANT_URL)

    @cqf_target_invariant.setter
    def cqf_target_invariant(self, value: Any) -> None:
        set_extension(self, CQF_TARGET_INVARIANT_URL, value)

    @property
    def timing_days_of_cycle(self) -> Any:
        return get_extension(self, TIMING_DAYS_OF_CYCLE_URL)

    @timing_days_of_cycle.setter
    def timing_days_of_cycle(self, value: Any) -> None:
        set_extension(self, TIMING_DAYS_OF_CYCLE_URL, value)

    @property
    def cqf_cds_hooks_endpoint(self) -> Any:
        return get_extension(self, CQF_CDS_HOOKS_ENDPOINT_URL)

    @cqf_cds_hooks_endpoint.setter
    def cqf_cds_hooks_endpoint(self, value: Any) -> None:
        set_extension(self, CQF_CDS_HOOKS_ENDPOINT_URL, value)

    @property
    def target_constraint(self) -> Any:
        return get_extension(self, TARGET_CONSTRAINT_URL)

    @target_constraint.setter
    def target_constraint(self, value: Any) -> None:
        set_extension(self, TARGET_CONSTRAINT_URL, value)

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

    @property
    def variable(self) -> Any:
        return get_extension(self, VARIABLE_URL)

    @variable.setter
    def variable(self, value: Any) -> None:
        set_extension(self, VARIABLE_URL, value)

    @property
    def cqf_strength_of_recommendation(self) -> Any:
        return get_extension(self, CQF_STRENGTH_OF_RECOMMENDATION_URL)

    @cqf_strength_of_recommendation.setter
    def cqf_strength_of_recommendation(self, value: Any) -> None:
        set_extension(self, CQF_STRENGTH_OF_RECOMMENDATION_URL, value)

    @property
    def cqf_quality_of_evidence(self) -> Any:
        return get_extension(self, CQF_QUALITY_OF_EVIDENCE_URL)

    @cqf_quality_of_evidence.setter
    def cqf_quality_of_evidence(self, value: Any) -> None:
        set_extension(self, CQF_QUALITY_OF_EVIDENCE_URL, value)

    @property
    def workflow_shall_comply_with(self) -> Any:
        return get_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL)

    @workflow_shall_comply_with.setter
    def workflow_shall_comply_with(self, value: Any) -> None:
        set_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL, value)

    @property
    def goal_relationship(self) -> Any:
        return get_extension(self, GOAL_RELATIONSHIP_URL)

    @goal_relationship.setter
    def goal_relationship(self, value: Any) -> None:
        set_extension(self, GOAL_RELATIONSHIP_URL, value)

class Practitioner(base.Practitioner):

    @property
    def patient_proficiency(self) -> Any:
        return get_extension(self, PATIENT_PROFICIENCY_URL)

    @patient_proficiency.setter
    def patient_proficiency(self, value: Any) -> None:
        set_extension(self, PATIENT_PROFICIENCY_URL, value)

    @property
    def individual_pronouns(self) -> Any:
        return get_extension(self, INDIVIDUAL_PRONOUNS_URL)

    @individual_pronouns.setter
    def individual_pronouns(self, value: Any) -> None:
        set_extension(self, INDIVIDUAL_PRONOUNS_URL, value)

    @property
    def individual_gender_identity(self) -> Any:
        return get_extension(self, INDIVIDUAL_GENDER_IDENTITY_URL)

    @individual_gender_identity.setter
    def individual_gender_identity(self, value: Any) -> None:
        set_extension(self, INDIVIDUAL_GENDER_IDENTITY_URL, value)

    @property
    def practitioner_job_title(self) -> Any:
        return get_extension(self, PRACTITIONER_JOB_TITLE_URL)

    @practitioner_job_title.setter
    def practitioner_job_title(self, value: Any) -> None:
        set_extension(self, PRACTITIONER_JOB_TITLE_URL, value)

    @property
    def practitioner_animal_species(self) -> Any:
        return get_extension(self, PRACTITIONER_ANIMAL_SPECIES_URL)

    @practitioner_animal_species.setter
    def practitioner_animal_species(self, value: Any) -> None:
        set_extension(self, PRACTITIONER_ANIMAL_SPECIES_URL, value)

    @property
    def individual_recorded_sex_or_gender(self) -> Any:
        return get_extension(self, INDIVIDUAL_RECORDED_SEX_OR_GENDER_URL)

    @individual_recorded_sex_or_gender.setter
    def individual_recorded_sex_or_gender(self, value: Any) -> None:
        set_extension(self, INDIVIDUAL_RECORDED_SEX_OR_GENDER_URL, value)

class PractitionerRole(base.PractitionerRole):

    @property
    def practitionerrole_employment_status(self) -> Any:
        return get_extension(self, PRACTITIONERROLE_EMPLOYMENT_STATUS_URL)

    @practitionerrole_employment_status.setter
    def practitionerrole_employment_status(self, value: Any) -> None:
        set_extension(self, PRACTITIONERROLE_EMPLOYMENT_STATUS_URL, value)

    @property
    def individual_gender_identity(self) -> Any:
        return get_extension(self, INDIVIDUAL_GENDER_IDENTITY_URL)

    @individual_gender_identity.setter
    def individual_gender_identity(self, value: Any) -> None:
        set_extension(self, INDIVIDUAL_GENDER_IDENTITY_URL, value)

    @property
    def practitioner_job_title(self) -> Any:
        return get_extension(self, PRACTITIONER_JOB_TITLE_URL)

    @practitioner_job_title.setter
    def practitioner_job_title(self, value: Any) -> None:
        set_extension(self, PRACTITIONER_JOB_TITLE_URL, value)

    @property
    def practitionerrole_primary_ind(self) -> Any:
        return get_extension(self, PRACTITIONERROLE_PRIMARY_IND_URL)

    @practitionerrole_primary_ind.setter
    def practitionerrole_primary_ind(self, value: Any) -> None:
        set_extension(self, PRACTITIONERROLE_PRIMARY_IND_URL, value)

class Procedure(base.Procedure):

    @property
    def procedure_progress_status(self) -> Any:
        return get_extension(self, PROCEDURE_PROGRESS_STATUS_URL)

    @procedure_progress_status.setter
    def procedure_progress_status(self, value: Any) -> None:
        set_extension(self, PROCEDURE_PROGRESS_STATUS_URL, value)

    @property
    def procedure_directed_by(self) -> Any:
        return get_extension(self, PROCEDURE_DIRECTED_BY_URL)

    @procedure_directed_by.setter
    def procedure_directed_by(self, value: Any) -> None:
        set_extension(self, PROCEDURE_DIRECTED_BY_URL, value)

    @property
    def procedure_caused_by(self) -> Any:
        return get_extension(self, PROCEDURE_CAUSED_BY_URL)

    @procedure_caused_by.setter
    def procedure_caused_by(self, value: Any) -> None:
        set_extension(self, PROCEDURE_CAUSED_BY_URL, value)

    @property
    def workflow_research_study(self) -> Any:
        return get_extension(self, WORKFLOW_RESEARCH_STUDY_URL)

    @workflow_research_study.setter
    def workflow_research_study(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RESEARCH_STUDY_URL, value)

    @property
    def workflow_follow_on_of(self) -> Any:
        return get_extension(self, WORKFLOW_FOLLOW_ON_OF_URL)

    @workflow_follow_on_of.setter
    def workflow_follow_on_of(self, value: Any) -> None:
        set_extension(self, WORKFLOW_FOLLOW_ON_OF_URL, value)

    @property
    def procedure_method(self) -> Any:
        return get_extension(self, PROCEDURE_METHOD_URL)

    @procedure_method.setter
    def procedure_method(self, value: Any) -> None:
        set_extension(self, PROCEDURE_METHOD_URL, value)

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def procedure_approach_body_structure(self) -> Any:
        return get_extension(self, PROCEDURE_APPROACH_BODY_STRUCTURE_URL)

    @procedure_approach_body_structure.setter
    def procedure_approach_body_structure(self, value: Any) -> None:
        set_extension(self, PROCEDURE_APPROACH_BODY_STRUCTURE_URL, value)

    @property
    def procedure_target_body_structure(self) -> Any:
        return get_extension(self, PROCEDURE_TARGET_BODY_STRUCTURE_URL)

    @procedure_target_body_structure.setter
    def procedure_target_body_structure(self, value: Any) -> None:
        set_extension(self, PROCEDURE_TARGET_BODY_STRUCTURE_URL, value)

    @property
    def procedure_incision_date_time(self) -> Any:
        return get_extension(self, PROCEDURE_INCISION_DATE_TIME_URL)

    @procedure_incision_date_time.setter
    def procedure_incision_date_time(self, value: Any) -> None:
        set_extension(self, PROCEDURE_INCISION_DATE_TIME_URL, value)

class Quantity(base.Quantity):

    @property
    def iso21090_uncertainty_type(self) -> Any:
        return get_extension(self, ISO21090_UNCERTAINTY_TYPE_URL)

    @iso21090_uncertainty_type.setter
    def iso21090_uncertainty_type(self, value: Any) -> None:
        set_extension(self, ISO21090_UNCERTAINTY_TYPE_URL, value)

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

    @property
    def iso21090_uncertainty(self) -> Any:
        return get_extension(self, ISO21090_UNCERTAINTY_URL)

    @iso21090_uncertainty.setter
    def iso21090_uncertainty(self, value: Any) -> None:
        set_extension(self, ISO21090_UNCERTAINTY_URL, value)

    @property
    def quantity_translation(self) -> Any:
        return get_extension(self, QUANTITY_TRANSLATION_URL)

    @quantity_translation.setter
    def quantity_translation(self, value: Any) -> None:
        set_extension(self, QUANTITY_TRANSLATION_URL, value)

class Questionnaire(base.Questionnaire):

    @property
    def min_length(self) -> Any:
        return get_extension(self, MIN_LENGTH_URL)

    @min_length.setter
    def min_length(self, value: Any) -> None:
        set_extension(self, MIN_LENGTH_URL, value)

    @property
    def questionnaire_fhir_type(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_FHIR_TYPE_URL)

    @questionnaire_fhir_type.setter
    def questionnaire_fhir_type(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_FHIR_TYPE_URL, value)

    @property
    def elementdefinition_conceptmap(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_CONCEPTMAP_URL)

    @elementdefinition_conceptmap.setter
    def elementdefinition_conceptmap(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_CONCEPTMAP_URL, value)

    @property
    def questionnaire_constraint(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_CONSTRAINT_URL)

    @questionnaire_constraint.setter
    def questionnaire_constraint(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_CONSTRAINT_URL, value)

    @property
    def cqf_target_invariant(self) -> Any:
        return get_extension(self, CQF_TARGET_INVARIANT_URL)

    @cqf_target_invariant.setter
    def cqf_target_invariant(self, value: Any) -> None:
        set_extension(self, CQF_TARGET_INVARIANT_URL, value)

    @property
    def questionnaire_reference_filter(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_REFERENCE_FILTER_URL)

    @questionnaire_reference_filter.setter
    def questionnaire_reference_filter(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_REFERENCE_FILTER_URL, value)

    @property
    def max_value(self) -> Any:
        return get_extension(self, MAX_VALUE_URL)

    @max_value.setter
    def max_value(self, value: Any) -> None:
        set_extension(self, MAX_VALUE_URL, value)

    @property
    def questionnaire_signature_required(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_SIGNATURE_REQUIRED_URL)

    @questionnaire_signature_required.setter
    def questionnaire_signature_required(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_SIGNATURE_REQUIRED_URL, value)

    @property
    def questionnaire_derivation_type(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_DERIVATION_TYPE_URL)

    @questionnaire_derivation_type.setter
    def questionnaire_derivation_type(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_DERIVATION_TYPE_URL, value)

    @property
    def max_decimal_places(self) -> Any:
        return get_extension(self, MAX_DECIMAL_PLACES_URL)

    @max_decimal_places.setter
    def max_decimal_places(self, value: Any) -> None:
        set_extension(self, MAX_DECIMAL_PLACES_URL, value)

    @property
    def questionnaire_unit(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_UNIT_URL)

    @questionnaire_unit.setter
    def questionnaire_unit(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_UNIT_URL, value)

    @property
    def questionnaire_min_occurs(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_MIN_OCCURS_URL)

    @questionnaire_min_occurs.setter
    def questionnaire_min_occurs(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_MIN_OCCURS_URL, value)

    @property
    def questionnaire_hidden(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_HIDDEN_URL)

    @questionnaire_hidden.setter
    def questionnaire_hidden(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_HIDDEN_URL, value)

    @property
    def target_constraint(self) -> Any:
        return get_extension(self, TARGET_CONSTRAINT_URL)

    @target_constraint.setter
    def target_constraint(self, value: Any) -> None:
        set_extension(self, TARGET_CONSTRAINT_URL, value)

    @property
    def questionnaire_unit_option(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_UNIT_OPTION_URL)

    @questionnaire_unit_option.setter
    def questionnaire_unit_option(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_UNIT_OPTION_URL, value)

    @property
    def ext_11179_permitted_value_valueset(self) -> Any:
        return get_extension(self, EXT_11179_PERMITTED_VALUE_VALUESET_URL)

    @ext_11179_permitted_value_valueset.setter
    def ext_11179_permitted_value_valueset(self, value: Any) -> None:
        set_extension(self, EXT_11179_PERMITTED_VALUE_VALUESET_URL, value)

    @property
    def questionnaire_unit_value_set(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_UNIT_VALUE_SET_URL)

    @questionnaire_unit_value_set.setter
    def questionnaire_unit_value_set(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_UNIT_VALUE_SET_URL, value)

    @property
    def questionnaire_option_exclusive(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_OPTION_EXCLUSIVE_URL)

    @questionnaire_option_exclusive.setter
    def questionnaire_option_exclusive(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_OPTION_EXCLUSIVE_URL, value)

    @property
    def questionnaire_option_restriction(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_OPTION_RESTRICTION_URL)

    @questionnaire_option_restriction.setter
    def questionnaire_option_restriction(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_OPTION_RESTRICTION_URL, value)

    @property
    def questionnaire_max_occurs(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_MAX_OCCURS_URL)

    @questionnaire_max_occurs.setter
    def questionnaire_max_occurs(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_MAX_OCCURS_URL, value)

    @property
    def ext_11179_permitted_value_conceptmap(self) -> Any:
        return get_extension(self, EXT_11179_PERMITTED_VALUE_CONCEPTMAP_URL)

    @ext_11179_permitted_value_conceptmap.setter
    def ext_11179_permitted_value_conceptmap(self, value: Any) -> None:
        set_extension(self, EXT_11179_PERMITTED_VALUE_CONCEPTMAP_URL, value)

    @property
    def questionnaire_definition_based(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_DEFINITION_BASED_URL)

    @questionnaire_definition_based.setter
    def questionnaire_definition_based(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_DEFINITION_BASED_URL, value)

    @property
    def questionnaire_item_control(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_ITEM_CONTROL_URL)

    @questionnaire_item_control.setter
    def questionnaire_item_control(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_ITEM_CONTROL_URL, value)

    @property
    def questionnaire_support_link(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_SUPPORT_LINK_URL)

    @questionnaire_support_link.setter
    def questionnaire_support_link(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_SUPPORT_LINK_URL, value)

    @property
    def min_value(self) -> Any:
        return get_extension(self, MIN_VALUE_URL)

    @min_value.setter
    def min_value(self, value: Any) -> None:
        set_extension(self, MIN_VALUE_URL, value)

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

    @property
    def mime_type(self) -> Any:
        return get_extension(self, MIME_TYPE_URL)

    @mime_type.setter
    def mime_type(self, value: Any) -> None:
        set_extension(self, MIME_TYPE_URL, value)

    @property
    def design_note(self) -> Any:
        return get_extension(self, DESIGN_NOTE_URL)

    @design_note.setter
    def design_note(self, value: Any) -> None:
        set_extension(self, DESIGN_NOTE_URL, value)

    @property
    def variable(self) -> Any:
        return get_extension(self, VARIABLE_URL)

    @variable.setter
    def variable(self, value: Any) -> None:
        set_extension(self, VARIABLE_URL, value)

    @property
    def questionnaire_display_category(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_DISPLAY_CATEGORY_URL)

    @questionnaire_display_category.setter
    def questionnaire_display_category(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_DISPLAY_CATEGORY_URL, value)

    @property
    def questionnaire_base_type(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_BASE_TYPE_URL)

    @questionnaire_base_type.setter
    def questionnaire_base_type(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_BASE_TYPE_URL, value)

    @property
    def questionnaire_reference_resource(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_REFERENCE_RESOURCE_URL)

    @questionnaire_reference_resource.setter
    def questionnaire_reference_resource(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_REFERENCE_RESOURCE_URL, value)

    @property
    def item_weight(self) -> Any:
        return get_extension(self, ITEM_WEIGHT_URL)

    @item_weight.setter
    def item_weight(self, value: Any) -> None:
        set_extension(self, ITEM_WEIGHT_URL, value)

    @property
    def questionnaire_choice_orientation(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_CHOICE_ORIENTATION_URL)

    @questionnaire_choice_orientation.setter
    def questionnaire_choice_orientation(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_CHOICE_ORIENTATION_URL, value)

    @property
    def questionnaire_usage_mode(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_USAGE_MODE_URL)

    @questionnaire_usage_mode.setter
    def questionnaire_usage_mode(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_USAGE_MODE_URL, value)

    @property
    def questionnaire_reference_profile(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_REFERENCE_PROFILE_URL)

    @questionnaire_reference_profile.setter
    def questionnaire_reference_profile(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_REFERENCE_PROFILE_URL, value)

    @property
    def entry_format(self) -> Any:
        return get_extension(self, ENTRY_FORMAT_URL)

    @entry_format.setter
    def entry_format(self, value: Any) -> None:
        set_extension(self, ENTRY_FORMAT_URL, value)

    @property
    def questionnaire_option_prefix(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_OPTION_PREFIX_URL)

    @questionnaire_option_prefix.setter
    def questionnaire_option_prefix(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_OPTION_PREFIX_URL, value)

    @property
    def max_size(self) -> Any:
        return get_extension(self, MAX_SIZE_URL)

    @max_size.setter
    def max_size(self, value: Any) -> None:
        set_extension(self, MAX_SIZE_URL, value)

    @property
    def questionnaire_slider_step_value(self) -> Any:
        return get_extension(self, QUESTIONNAIRE_SLIDER_STEP_VALUE_URL)

    @questionnaire_slider_step_value.setter
    def questionnaire_slider_step_value(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRE_SLIDER_STEP_VALUE_URL, value)

class QuestionnaireResponse(base.QuestionnaireResponse):

    @property
    def workflow_triggered_by(self) -> Any:
        return get_extension(self, WORKFLOW_TRIGGERED_BY_URL)

    @workflow_triggered_by.setter
    def workflow_triggered_by(self, value: Any) -> None:
        set_extension(self, WORKFLOW_TRIGGERED_BY_URL, value)

    @property
    def questionnaireresponse_reason(self) -> Any:
        return get_extension(self, QUESTIONNAIRERESPONSE_REASON_URL)

    @questionnaireresponse_reason.setter
    def questionnaireresponse_reason(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRERESPONSE_REASON_URL, value)

    @property
    def workflow_research_study(self) -> Any:
        return get_extension(self, WORKFLOW_RESEARCH_STUDY_URL)

    @workflow_research_study.setter
    def workflow_research_study(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RESEARCH_STUDY_URL, value)

    @property
    def questionnaireresponse_reviewer(self) -> Any:
        return get_extension(self, QUESTIONNAIRERESPONSE_REVIEWER_URL)

    @questionnaireresponse_reviewer.setter
    def questionnaireresponse_reviewer(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRERESPONSE_REVIEWER_URL, value)

    @property
    def questionnaireresponse_author(self) -> Any:
        return get_extension(self, QUESTIONNAIRERESPONSE_AUTHOR_URL)

    @questionnaireresponse_author.setter
    def questionnaireresponse_author(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRERESPONSE_AUTHOR_URL, value)

    @property
    def questionnaireresponse_completion_mode(self) -> Any:
        return get_extension(self, QUESTIONNAIRERESPONSE_COMPLETION_MODE_URL)

    @questionnaireresponse_completion_mode.setter
    def questionnaireresponse_completion_mode(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRERESPONSE_COMPLETION_MODE_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def workflow_adheres_to(self) -> Any:
        return get_extension(self, WORKFLOW_ADHERES_TO_URL)

    @workflow_adheres_to.setter
    def workflow_adheres_to(self, value: Any) -> None:
        set_extension(self, WORKFLOW_ADHERES_TO_URL, value)

    @property
    def questionnaireresponse_signature(self) -> Any:
        return get_extension(self, QUESTIONNAIRERESPONSE_SIGNATURE_URL)

    @questionnaireresponse_signature.setter
    def questionnaireresponse_signature(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRERESPONSE_SIGNATURE_URL, value)

    @property
    def questionnaireresponse_attester(self) -> Any:
        return get_extension(self, QUESTIONNAIRERESPONSE_ATTESTER_URL)

    @questionnaireresponse_attester.setter
    def questionnaireresponse_attester(self, value: Any) -> None:
        set_extension(self, QUESTIONNAIRERESPONSE_ATTESTER_URL, value)

class Range(base.Range):

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

class Ratio(base.Ratio):

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

class Reference(base.Reference):

    @property
    def target_path(self) -> Any:
        return get_extension(self, TARGET_PATH_URL)

    @target_path.setter
    def target_path(self, value: Any) -> None:
        set_extension(self, TARGET_PATH_URL, value)

    @property
    def resolve_as_version_specific(self) -> Any:
        return get_extension(self, RESOLVE_AS_VERSION_SPECIFIC_URL)

    @resolve_as_version_specific.setter
    def resolve_as_version_specific(self, value: Any) -> None:
        set_extension(self, RESOLVE_AS_VERSION_SPECIFIC_URL, value)

    @property
    def artifact_uri_reference(self) -> Any:
        return get_extension(self, ARTIFACT_URI_REFERENCE_URL)

    @artifact_uri_reference.setter
    def artifact_uri_reference(self, value: Any) -> None:
        set_extension(self, ARTIFACT_URI_REFERENCE_URL, value)

    @property
    def additional_identifier(self) -> Any:
        return get_extension(self, ADDITIONAL_IDENTIFIER_URL)

    @additional_identifier.setter
    def additional_identifier(self, value: Any) -> None:
        set_extension(self, ADDITIONAL_IDENTIFIER_URL, value)

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

    @property
    def alternate_reference(self) -> Any:
        return get_extension(self, ALTERNATE_REFERENCE_URL)

    @alternate_reference.setter
    def alternate_reference(self, value: Any) -> None:
        set_extension(self, ALTERNATE_REFERENCE_URL, value)

    @property
    def cqf_measure_info(self) -> Any:
        return get_extension(self, CQF_MEASURE_INFO_URL)

    @cqf_measure_info.setter
    def cqf_measure_info(self, value: Any) -> None:
        set_extension(self, CQF_MEASURE_INFO_URL, value)

    @property
    def target_element(self) -> Any:
        return get_extension(self, TARGET_ELEMENT_URL)

    @target_element.setter
    def target_element(self, value: Any) -> None:
        set_extension(self, TARGET_ELEMENT_URL, value)

class RelatedArtifact(base.RelatedArtifact):

    @property
    def cqf_is_primary_citation(self) -> Any:
        return get_extension(self, CQF_IS_PRIMARY_CITATION_URL)

    @cqf_is_primary_citation.setter
    def cqf_is_primary_citation(self, value: Any) -> None:
        set_extension(self, CQF_IS_PRIMARY_CITATION_URL, value)

    @property
    def artifact_is_owned(self) -> Any:
        return get_extension(self, ARTIFACT_IS_OWNED_URL)

    @artifact_is_owned.setter
    def artifact_is_owned(self, value: Any) -> None:
        set_extension(self, ARTIFACT_IS_OWNED_URL, value)

    @property
    def cqf_model_info_settings(self) -> Any:
        return get_extension(self, CQF_MODEL_INFO_SETTINGS_URL)

    @cqf_model_info_settings.setter
    def cqf_model_info_settings(self, value: Any) -> None:
        set_extension(self, CQF_MODEL_INFO_SETTINGS_URL, value)

    @property
    def cqf_publication_status(self) -> Any:
        return get_extension(self, CQF_PUBLICATION_STATUS_URL)

    @cqf_publication_status.setter
    def cqf_publication_status(self, value: Any) -> None:
        set_extension(self, CQF_PUBLICATION_STATUS_URL, value)

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

    @property
    def cqf_expansion_parameters(self) -> Any:
        return get_extension(self, CQF_EXPANSION_PARAMETERS_URL)

    @cqf_expansion_parameters.setter
    def cqf_expansion_parameters(self, value: Any) -> None:
        set_extension(self, CQF_EXPANSION_PARAMETERS_URL, value)

    @property
    def cqf_publication_date(self) -> Any:
        return get_extension(self, CQF_PUBLICATION_DATE_URL)

    @cqf_publication_date.setter
    def cqf_publication_date(self, value: Any) -> None:
        set_extension(self, CQF_PUBLICATION_DATE_URL, value)

class RelatedPerson(base.RelatedPerson):

    @property
    def patient_proficiency(self) -> Any:
        return get_extension(self, PATIENT_PROFICIENCY_URL)

    @patient_proficiency.setter
    def patient_proficiency(self, value: Any) -> None:
        set_extension(self, PATIENT_PROFICIENCY_URL, value)

    @property
    def individual_pronouns(self) -> Any:
        return get_extension(self, INDIVIDUAL_PRONOUNS_URL)

    @individual_pronouns.setter
    def individual_pronouns(self, value: Any) -> None:
        set_extension(self, INDIVIDUAL_PRONOUNS_URL, value)

    @property
    def individual_gender_identity(self) -> Any:
        return get_extension(self, INDIVIDUAL_GENDER_IDENTITY_URL)

    @individual_gender_identity.setter
    def individual_gender_identity(self, value: Any) -> None:
        set_extension(self, INDIVIDUAL_GENDER_IDENTITY_URL, value)

    @property
    def practitioner_animal_species(self) -> Any:
        return get_extension(self, PRACTITIONER_ANIMAL_SPECIES_URL)

    @practitioner_animal_species.setter
    def practitioner_animal_species(self, value: Any) -> None:
        set_extension(self, PRACTITIONER_ANIMAL_SPECIES_URL, value)

    @property
    def individual_recorded_sex_or_gender(self) -> Any:
        return get_extension(self, INDIVIDUAL_RECORDED_SEX_OR_GENDER_URL)

    @individual_recorded_sex_or_gender.setter
    def individual_recorded_sex_or_gender(self, value: Any) -> None:
        set_extension(self, INDIVIDUAL_RECORDED_SEX_OR_GENDER_URL, value)

class RequestOrchestration(base.RequestOrchestration):

    @property
    def workflow_triggered_by(self) -> Any:
        return get_extension(self, WORKFLOW_TRIGGERED_BY_URL)

    @workflow_triggered_by.setter
    def workflow_triggered_by(self, value: Any) -> None:
        set_extension(self, WORKFLOW_TRIGGERED_BY_URL, value)

    @property
    def timing_days_of_cycle(self) -> Any:
        return get_extension(self, TIMING_DAYS_OF_CYCLE_URL)

    @timing_days_of_cycle.setter
    def timing_days_of_cycle(self, value: Any) -> None:
        set_extension(self, TIMING_DAYS_OF_CYCLE_URL, value)

    @property
    def workflow_generated_from(self) -> Any:
        return get_extension(self, WORKFLOW_GENERATED_FROM_URL)

    @workflow_generated_from.setter
    def workflow_generated_from(self, value: Any) -> None:
        set_extension(self, WORKFLOW_GENERATED_FROM_URL, value)

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def variable(self) -> Any:
        return get_extension(self, VARIABLE_URL)

    @variable.setter
    def variable(self, value: Any) -> None:
        set_extension(self, VARIABLE_URL, value)

    @property
    def cqf_input_parameters(self) -> Any:
        return get_extension(self, CQF_INPUT_PARAMETERS_URL)

    @cqf_input_parameters.setter
    def cqf_input_parameters(self, value: Any) -> None:
        set_extension(self, CQF_INPUT_PARAMETERS_URL, value)

    @property
    def workflow_complies_with(self) -> Any:
        return get_extension(self, WORKFLOW_COMPLIES_WITH_URL)

    @workflow_complies_with.setter
    def workflow_complies_with(self, value: Any) -> None:
        set_extension(self, WORKFLOW_COMPLIES_WITH_URL, value)

class Requirements(base.Requirements):

    @property
    def requirements_parent(self) -> Any:
        return get_extension(self, REQUIREMENTS_PARENT_URL)

    @requirements_parent.setter
    def requirements_parent(self, value: Any) -> None:
        set_extension(self, REQUIREMENTS_PARENT_URL, value)

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class ResearchStudy(base.ResearchStudy):

    @property
    def research_study_study_registration(self) -> Any:
        return get_extension(self, RESEARCH_STUDY_STUDY_REGISTRATION_URL)

    @research_study_study_registration.setter
    def research_study_study_registration(self, value: Any) -> None:
        set_extension(self, RESEARCH_STUDY_STUDY_REGISTRATION_URL, value)

    @property
    def research_study_site_recruitment(self) -> Any:
        return get_extension(self, RESEARCH_STUDY_SITE_RECRUITMENT_URL)

    @research_study_site_recruitment.setter
    def research_study_site_recruitment(self, value: Any) -> None:
        set_extension(self, RESEARCH_STUDY_SITE_RECRUITMENT_URL, value)

class ResearchSubject(base.ResearchSubject):

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

class Resource(base.Resource):

    @property
    def artifact_cite_as(self) -> Any:
        return get_extension(self, ARTIFACT_CITE_AS_URL)

    @artifact_cite_as.setter
    def artifact_cite_as(self, value: Any) -> None:
        set_extension(self, ARTIFACT_CITE_AS_URL, value)

    @property
    def cqf_artifact_comment(self) -> Any:
        return get_extension_text(self, CQF_ARTIFACT_COMMENT_URL)

    @cqf_artifact_comment.setter
    def cqf_artifact_comment(self, value: Any) -> None:
        set_extension_text(self, CQF_ARTIFACT_COMMENT_URL, value)

    @property
    def patient_sex_parameter_for_clinical_use(self) -> Any:
        return get_extension(self, PATIENT_SEX_PARAMETER_FOR_CLINICAL_USE_URL)

    @patient_sex_parameter_for_clinical_use.setter
    def patient_sex_parameter_for_clinical_use(self, value: Any) -> None:
        set_extension(self, PATIENT_SEX_PARAMETER_FOR_CLINICAL_USE_URL, value)

    @property
    def artifact_release_description(self) -> Any:
        return get_extension(self, ARTIFACT_RELEASE_DESCRIPTION_URL)

    @artifact_release_description.setter
    def artifact_release_description(self, value: Any) -> None:
        set_extension(self, ARTIFACT_RELEASE_DESCRIPTION_URL, value)

    @property
    def structuredefinition_fmm(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_FMM_URL)

    @structuredefinition_fmm.setter
    def structuredefinition_fmm(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_FMM_URL, value)

    @property
    def artifact_experimental(self) -> Any:
        return get_extension(self, ARTIFACT_EXPERIMENTAL_URL)

    @artifact_experimental.setter
    def artifact_experimental(self, value: Any) -> None:
        set_extension(self, ARTIFACT_EXPERIMENTAL_URL, value)

    @property
    def version_specific_use(self) -> Any:
        return get_extension(self, VERSION_SPECIFIC_USE_URL)

    @version_specific_use.setter
    def version_specific_use(self, value: Any) -> None:
        set_extension(self, VERSION_SPECIFIC_USE_URL, value)

    @property
    def artifactassessment_disposition(self) -> Any:
        return get_extension(self, ARTIFACTASSESSMENT_DISPOSITION_URL)

    @artifactassessment_disposition.setter
    def artifactassessment_disposition(self, value: Any) -> None:
        set_extension(self, ARTIFACTASSESSMENT_DISPOSITION_URL, value)

    @property
    def satisfies_requirement(self) -> Any:
        return get_extension(self, SATISFIES_REQUIREMENT_URL)

    @satisfies_requirement.setter
    def satisfies_requirement(self, value: Any) -> None:
        set_extension(self, SATISFIES_REQUIREMENT_URL, value)

    @property
    def resource_pertains_to_goal(self) -> Any:
        return get_extension(self, RESOURCE_PERTAINS_TO_GOAL_URL)

    @resource_pertains_to_goal.setter
    def resource_pertains_to_goal(self, value: Any) -> None:
        set_extension(self, RESOURCE_PERTAINS_TO_GOAL_URL, value)

    @property
    def artifact_description(self) -> Any:
        return get_extension(self, ARTIFACT_DESCRIPTION_URL)

    @artifact_description.setter
    def artifact_description(self, value: Any) -> None:
        set_extension(self, ARTIFACT_DESCRIPTION_URL, value)

    @property
    def cqf_scope(self) -> Any:
        return get_extension(self, CQF_SCOPE_URL)

    @cqf_scope.setter
    def cqf_scope(self, value: Any) -> None:
        set_extension(self, CQF_SCOPE_URL, value)

    @property
    def artifact_title(self) -> Any:
        return get_extension(self, ARTIFACT_TITLE_URL)

    @artifact_title.setter
    def artifact_title(self, value: Any) -> None:
        set_extension(self, ARTIFACT_TITLE_URL, value)

    @property
    def cqf_measure_info(self) -> Any:
        return get_extension(self, CQF_MEASURE_INFO_URL)

    @cqf_measure_info.setter
    def cqf_measure_info(self, value: Any) -> None:
        set_extension(self, CQF_MEASURE_INFO_URL, value)

    @property
    def derivation_reference(self) -> Any:
        return get_extension(self, DERIVATION_REFERENCE_URL)

    @derivation_reference.setter
    def derivation_reference(self, value: Any) -> None:
        set_extension(self, DERIVATION_REFERENCE_URL, value)

    @property
    def artifact_contact(self) -> Any:
        return get_extension(self, ARTIFACT_CONTACT_URL)

    @artifact_contact.setter
    def artifact_contact(self, value: Any) -> None:
        set_extension(self, ARTIFACT_CONTACT_URL, value)

    @property
    def artifact_last_review_date(self) -> Any:
        return get_extension(self, ARTIFACT_LAST_REVIEW_DATE_URL)

    @artifact_last_review_date.setter
    def artifact_last_review_date(self, value: Any) -> None:
        set_extension(self, ARTIFACT_LAST_REVIEW_DATE_URL, value)

    @property
    def artifact_author(self) -> Any:
        return get_extension(self, ARTIFACT_AUTHOR_URL)

    @artifact_author.setter
    def artifact_author(self, value: Any) -> None:
        set_extension(self, ARTIFACT_AUTHOR_URL, value)

    @property
    def artifact_copyright_label(self) -> Any:
        return get_extension(self, ARTIFACT_COPYRIGHT_LABEL_URL)

    @artifact_copyright_label.setter
    def artifact_copyright_label(self, value: Any) -> None:
        set_extension(self, ARTIFACT_COPYRIGHT_LABEL_URL, value)

    @property
    def artifact_identifier(self) -> Any:
        return get_extension(self, ARTIFACT_IDENTIFIER_URL)

    @artifact_identifier.setter
    def artifact_identifier(self, value: Any) -> None:
        set_extension(self, ARTIFACT_IDENTIFIER_URL, value)

    @property
    def artifactassessment_workflow_status(self) -> Any:
        return get_extension(self, ARTIFACTASSESSMENT_WORKFLOW_STATUS_URL)

    @artifactassessment_workflow_status.setter
    def artifactassessment_workflow_status(self, value: Any) -> None:
        set_extension(self, ARTIFACTASSESSMENT_WORKFLOW_STATUS_URL, value)

    @property
    def artifact_effective_period(self) -> Any:
        return get_extension(self, ARTIFACT_EFFECTIVE_PERIOD_URL)

    @artifact_effective_period.setter
    def artifact_effective_period(self, value: Any) -> None:
        set_extension(self, ARTIFACT_EFFECTIVE_PERIOD_URL, value)

    @property
    def artifact_copyright(self) -> Any:
        return get_extension(self, ARTIFACT_COPYRIGHT_URL)

    @artifact_copyright.setter
    def artifact_copyright(self, value: Any) -> None:
        set_extension(self, ARTIFACT_COPYRIGHT_URL, value)

    @property
    def artifact_purpose(self) -> Any:
        return get_extension(self, ARTIFACT_PURPOSE_URL)

    @artifact_purpose.setter
    def artifact_purpose(self, value: Any) -> None:
        set_extension(self, ARTIFACT_PURPOSE_URL, value)

    @property
    def artifact_related_artifact(self) -> Any:
        return get_extension(self, ARTIFACT_RELATED_ARTIFACT_URL)

    @artifact_related_artifact.setter
    def artifact_related_artifact(self, value: Any) -> None:
        set_extension(self, ARTIFACT_RELATED_ARTIFACT_URL, value)

    @property
    def cqf_direct_reference_code(self) -> Any:
        return get_extension(self, CQF_DIRECT_REFERENCE_CODE_URL)

    @cqf_direct_reference_code.setter
    def cqf_direct_reference_code(self, value: Any) -> None:
        set_extension(self, CQF_DIRECT_REFERENCE_CODE_URL, value)

    @property
    def artifact_usage(self) -> Any:
        return get_extension(self, ARTIFACT_USAGE_URL)

    @artifact_usage.setter
    def artifact_usage(self, value: Any) -> None:
        set_extension(self, ARTIFACT_USAGE_URL, value)

    @property
    def note(self) -> Any:
        return get_extension(self, NOTE_URL)

    @note.setter
    def note(self, value: Any) -> None:
        set_extension(self, NOTE_URL, value)

    @property
    def version_specific_value(self) -> Any:
        return get_extension(self, VERSION_SPECIFIC_VALUE_URL)

    @version_specific_value.setter
    def version_specific_value(self, value: Any) -> None:
        set_extension(self, VERSION_SPECIFIC_VALUE_URL, value)

    @property
    def artifact_name(self) -> Any:
        return get_extension(self, ARTIFACT_NAME_URL)

    @artifact_name.setter
    def artifact_name(self, value: Any) -> None:
        set_extension(self, ARTIFACT_NAME_URL, value)

    @property
    def artifact_jurisdiction(self) -> Any:
        return get_extension(self, ARTIFACT_JURISDICTION_URL)

    @artifact_jurisdiction.setter
    def artifact_jurisdiction(self, value: Any) -> None:
        set_extension(self, ARTIFACT_JURISDICTION_URL, value)

    @property
    def cqf_definition_term(self) -> Any:
        return get_extension(self, CQF_DEFINITION_TERM_URL)

    @cqf_definition_term.setter
    def cqf_definition_term(self, value: Any) -> None:
        set_extension(self, CQF_DEFINITION_TERM_URL, value)

    @property
    def artifact_use_context(self) -> Any:
        return get_extension(self, ARTIFACT_USE_CONTEXT_URL)

    @artifact_use_context.setter
    def artifact_use_context(self, value: Any) -> None:
        set_extension(self, ARTIFACT_USE_CONTEXT_URL, value)

    @property
    def artifact_release_label(self) -> Any:
        return get_extension(self, ARTIFACT_RELEASE_LABEL_URL)

    @artifact_release_label.setter
    def artifact_release_label(self, value: Any) -> None:
        set_extension(self, ARTIFACT_RELEASE_LABEL_URL, value)

    @property
    def artifact_version(self) -> Any:
        return get_extension(self, ARTIFACT_VERSION_URL)

    @artifact_version.setter
    def artifact_version(self, value: Any) -> None:
        set_extension(self, ARTIFACT_VERSION_URL, value)

    @property
    def artifact_url(self) -> Any:
        return get_extension(self, ARTIFACT_URL_URL)

    @artifact_url.setter
    def artifact_url(self, value: Any) -> None:
        set_extension(self, ARTIFACT_URL_URL, value)

    @property
    def resource_instance_description(self) -> Any:
        return get_extension(self, RESOURCE_INSTANCE_DESCRIPTION_URL)

    @resource_instance_description.setter
    def resource_instance_description(self, value: Any) -> None:
        set_extension(self, RESOURCE_INSTANCE_DESCRIPTION_URL, value)

    @property
    def artifact_version_algorithm(self) -> Any:
        return get_extension(self, ARTIFACT_VERSION_ALGORITHM_URL)

    @artifact_version_algorithm.setter
    def artifact_version_algorithm(self, value: Any) -> None:
        set_extension(self, ARTIFACT_VERSION_ALGORITHM_URL, value)

    @property
    def artifact_publisher(self) -> Any:
        return get_extension(self, ARTIFACT_PUBLISHER_URL)

    @artifact_publisher.setter
    def artifact_publisher(self, value: Any) -> None:
        set_extension(self, ARTIFACT_PUBLISHER_URL, value)

    @property
    def artifact_approval_date(self) -> Any:
        return get_extension(self, ARTIFACT_APPROVAL_DATE_URL)

    @artifact_approval_date.setter
    def artifact_approval_date(self, value: Any) -> None:
        set_extension(self, ARTIFACT_APPROVAL_DATE_URL, value)

    @property
    def artifact_topic(self) -> Any:
        return get_extension(self, ARTIFACT_TOPIC_URL)

    @artifact_topic.setter
    def artifact_topic(self, value: Any) -> None:
        set_extension(self, ARTIFACT_TOPIC_URL, value)

    @property
    def cqf_messages(self) -> Any:
        return get_extension(self, CQF_MESSAGES_URL)

    @cqf_messages.setter
    def cqf_messages(self, value: Any) -> None:
        set_extension(self, CQF_MESSAGES_URL, value)

    @property
    def artifact_date(self) -> Any:
        return get_extension(self, ARTIFACT_DATE_URL)

    @artifact_date.setter
    def artifact_date(self, value: Any) -> None:
        set_extension(self, ARTIFACT_DATE_URL, value)

    @property
    def artifact_status(self) -> Any:
        return get_extension(self, ARTIFACT_STATUS_URL)

    @artifact_status.setter
    def artifact_status(self, value: Any) -> None:
        set_extension(self, ARTIFACT_STATUS_URL, value)

    @property
    def resource_instance_name(self) -> Any:
        return get_extension(self, RESOURCE_INSTANCE_NAME_URL)

    @resource_instance_name.setter
    def resource_instance_name(self, value: Any) -> None:
        set_extension(self, RESOURCE_INSTANCE_NAME_URL, value)

    @property
    def artifact_version_policy(self) -> Any:
        return get_extension(self, ARTIFACT_VERSION_POLICY_URL)

    @artifact_version_policy.setter
    def artifact_version_policy(self, value: Any) -> None:
        set_extension(self, ARTIFACT_VERSION_POLICY_URL, value)

class RiskAssessment(base.RiskAssessment):

    @property
    def workflow_research_study(self) -> Any:
        return get_extension(self, WORKFLOW_RESEARCH_STUDY_URL)

    @workflow_research_study.setter
    def workflow_research_study(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RESEARCH_STUDY_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

class SampledData(base.SampledData):

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

class SearchParameter(base.SearchParameter):

    @property
    def resource_approval_date(self) -> Any:
        return get_extension(self, RESOURCE_APPROVAL_DATE_URL)

    @resource_approval_date.setter
    def resource_approval_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_APPROVAL_DATE_URL, value)

    @property
    def resource_last_review_date(self) -> Any:
        return get_extension(self, RESOURCE_LAST_REVIEW_DATE_URL)

    @resource_last_review_date.setter
    def resource_last_review_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_LAST_REVIEW_DATE_URL, value)

    @property
    def structuredefinition_standards_status(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_STANDARDS_STATUS_URL)

    @structuredefinition_standards_status.setter
    def structuredefinition_standards_status(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_STANDARDS_STATUS_URL, value)

    @property
    def resource_effective_period(self) -> Any:
        return get_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL)

    @resource_effective_period.setter
    def resource_effective_period(self, value: Any) -> None:
        set_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL, value)

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class ServiceRequest(base.ServiceRequest):

    @property
    def workflow_triggered_by(self) -> Any:
        return get_extension(self, WORKFLOW_TRIGGERED_BY_URL)

    @workflow_triggered_by.setter
    def workflow_triggered_by(self, value: Any) -> None:
        set_extension(self, WORKFLOW_TRIGGERED_BY_URL, value)

    @property
    def procedure_directed_by(self) -> Any:
        return get_extension(self, PROCEDURE_DIRECTED_BY_URL)

    @procedure_directed_by.setter
    def procedure_directed_by(self, value: Any) -> None:
        set_extension(self, PROCEDURE_DIRECTED_BY_URL, value)

    @property
    def workflow_research_study(self) -> Any:
        return get_extension(self, WORKFLOW_RESEARCH_STUDY_URL)

    @workflow_research_study.setter
    def workflow_research_study(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RESEARCH_STUDY_URL, value)

    @property
    def workflow_generated_from(self) -> Any:
        return get_extension(self, WORKFLOW_GENERATED_FROM_URL)

    @workflow_generated_from.setter
    def workflow_generated_from(self, value: Any) -> None:
        set_extension(self, WORKFLOW_GENERATED_FROM_URL, value)

    @property
    def servicerequest_precondition(self) -> Any:
        return get_extension(self, SERVICEREQUEST_PRECONDITION_URL)

    @servicerequest_precondition.setter
    def servicerequest_precondition(self, value: Any) -> None:
        set_extension(self, SERVICEREQUEST_PRECONDITION_URL, value)

    @property
    def servicerequest_questionnaire_request(self) -> Any:
        return get_extension(self, SERVICEREQUEST_QUESTIONNAIRE_REQUEST_URL)

    @servicerequest_questionnaire_request.setter
    def servicerequest_questionnaire_request(self, value: Any) -> None:
        set_extension(self, SERVICEREQUEST_QUESTIONNAIRE_REQUEST_URL, value)

    @property
    def workflow_follow_on_of(self) -> Any:
        return get_extension(self, WORKFLOW_FOLLOW_ON_OF_URL)

    @workflow_follow_on_of.setter
    def workflow_follow_on_of(self, value: Any) -> None:
        set_extension(self, WORKFLOW_FOLLOW_ON_OF_URL, value)

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def request_performer_order(self) -> Any:
        return get_extension(self, REQUEST_PERFORMER_ORDER_URL)

    @request_performer_order.setter
    def request_performer_order(self, value: Any) -> None:
        set_extension(self, REQUEST_PERFORMER_ORDER_URL, value)

    @property
    def servicerequest_order_callback_phone_number(self) -> Any:
        return get_extension(self, SERVICEREQUEST_ORDER_CALLBACK_PHONE_NUMBER_URL)

    @servicerequest_order_callback_phone_number.setter
    def servicerequest_order_callback_phone_number(self, value: Any) -> None:
        set_extension(self, SERVICEREQUEST_ORDER_CALLBACK_PHONE_NUMBER_URL, value)

    @property
    def procedure_approach_body_structure(self) -> Any:
        return get_extension(self, PROCEDURE_APPROACH_BODY_STRUCTURE_URL)

    @procedure_approach_body_structure.setter
    def procedure_approach_body_structure(self, value: Any) -> None:
        set_extension(self, PROCEDURE_APPROACH_BODY_STRUCTURE_URL, value)

    @property
    def workflow_complies_with(self) -> Any:
        return get_extension(self, WORKFLOW_COMPLIES_WITH_URL)

    @workflow_complies_with.setter
    def workflow_complies_with(self, value: Any) -> None:
        set_extension(self, WORKFLOW_COMPLIES_WITH_URL, value)

    @property
    def request_status_reason(self) -> Any:
        return get_extension(self, REQUEST_STATUS_REASON_URL)

    @request_status_reason.setter
    def request_status_reason(self, value: Any) -> None:
        set_extension(self, REQUEST_STATUS_REASON_URL, value)

    @property
    def procedure_target_body_structure(self) -> Any:
        return get_extension(self, PROCEDURE_TARGET_BODY_STRUCTURE_URL)

    @procedure_target_body_structure.setter
    def procedure_target_body_structure(self, value: Any) -> None:
        set_extension(self, PROCEDURE_TARGET_BODY_STRUCTURE_URL, value)

class Signature(base.Signature):

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

class Specimen(base.Specimen):

    @property
    def observation_body_position(self) -> Any:
        return get_extension(self, OBSERVATION_BODY_POSITION_URL)

    @observation_body_position.setter
    def observation_body_position(self, value: Any) -> None:
        set_extension(self, OBSERVATION_BODY_POSITION_URL, value)

    @property
    def specimen_sequence_number(self) -> Any:
        return get_extension(self, SPECIMEN_SEQUENCE_NUMBER_URL)

    @specimen_sequence_number.setter
    def specimen_sequence_number(self, value: Any) -> None:
        set_extension(self, SPECIMEN_SEQUENCE_NUMBER_URL, value)

    @property
    def specimen_is_dry_weight(self) -> Any:
        return get_extension(self, SPECIMEN_IS_DRY_WEIGHT_URL)

    @specimen_is_dry_weight.setter
    def specimen_is_dry_weight(self, value: Any) -> None:
        set_extension(self, SPECIMEN_IS_DRY_WEIGHT_URL, value)

    @property
    def specimen_additive(self) -> Any:
        return get_extension(self, SPECIMEN_ADDITIVE_URL)

    @specimen_additive.setter
    def specimen_additive(self, value: Any) -> None:
        set_extension(self, SPECIMEN_ADDITIVE_URL, value)

    @property
    def specimen_special_handling(self) -> Any:
        return get_extension(self, SPECIMEN_SPECIAL_HANDLING_URL)

    @specimen_special_handling.setter
    def specimen_special_handling(self, value: Any) -> None:
        set_extension(self, SPECIMEN_SPECIAL_HANDLING_URL, value)

    @property
    def specimen_collection_priority(self) -> Any:
        return get_extension(self, SPECIMEN_COLLECTION_PRIORITY_URL)

    @specimen_collection_priority.setter
    def specimen_collection_priority(self, value: Any) -> None:
        set_extension(self, SPECIMEN_COLLECTION_PRIORITY_URL, value)

    @property
    def specimen_reject_reason(self) -> Any:
        return get_extension(self, SPECIMEN_REJECT_REASON_URL)

    @specimen_reject_reason.setter
    def specimen_reject_reason(self, value: Any) -> None:
        set_extension(self, SPECIMEN_REJECT_REASON_URL, value)

    @property
    def specimen_processing_time(self) -> Any:
        return get_extension(self, SPECIMEN_PROCESSING_TIME_URL)

    @specimen_processing_time.setter
    def specimen_processing_time(self, value: Any) -> None:
        set_extension(self, SPECIMEN_PROCESSING_TIME_URL, value)

    @property
    def procedure_approach_body_structure(self) -> Any:
        return get_extension(self, PROCEDURE_APPROACH_BODY_STRUCTURE_URL)

    @procedure_approach_body_structure.setter
    def procedure_approach_body_structure(self, value: Any) -> None:
        set_extension(self, PROCEDURE_APPROACH_BODY_STRUCTURE_URL, value)

class SpecimenDefinition(base.SpecimenDefinition):

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class StructureDefinition(base.StructureDefinition):

    @property
    def structuredefinition_type_characteristics(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_TYPE_CHARACTERISTICS_URL)

    @structuredefinition_type_characteristics.setter
    def structuredefinition_type_characteristics(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_TYPE_CHARACTERISTICS_URL, value)

    @property
    def resource_approval_date(self) -> Any:
        return get_extension(self, RESOURCE_APPROVAL_DATE_URL)

    @resource_approval_date.setter
    def resource_approval_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_APPROVAL_DATE_URL, value)

    @property
    def elementdefinition_conceptmap(self) -> Any:
        return get_extension(self, ELEMENTDEFINITION_CONCEPTMAP_URL)

    @elementdefinition_conceptmap.setter
    def elementdefinition_conceptmap(self, value: Any) -> None:
        set_extension(self, ELEMENTDEFINITION_CONCEPTMAP_URL, value)

    @property
    def structuredefinition_complies_with_profile(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_COMPLIES_WITH_PROFILE_URL)

    @structuredefinition_complies_with_profile.setter
    def structuredefinition_complies_with_profile(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_COMPLIES_WITH_PROFILE_URL, value)

    @property
    def structuredefinition_category(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_CATEGORY_URL)

    @structuredefinition_category.setter
    def structuredefinition_category(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_CATEGORY_URL, value)

    @property
    def cqf_model_info_primary_code_path(self) -> Any:
        return get_extension(self, CQF_MODEL_INFO_PRIMARY_CODE_PATH_URL)

    @cqf_model_info_primary_code_path.setter
    def cqf_model_info_primary_code_path(self, value: Any) -> None:
        set_extension(self, CQF_MODEL_INFO_PRIMARY_CODE_PATH_URL, value)

    @property
    def structuredefinition_security_category(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_SECURITY_CATEGORY_URL)

    @structuredefinition_security_category.setter
    def structuredefinition_security_category(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_SECURITY_CATEGORY_URL, value)

    @property
    def structuredefinition_ancestor(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_ANCESTOR_URL)

    @structuredefinition_ancestor.setter
    def structuredefinition_ancestor(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_ANCESTOR_URL, value)

    @property
    def structuredefinition_inheritance_control(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_INHERITANCE_CONTROL_URL)

    @structuredefinition_inheritance_control.setter
    def structuredefinition_inheritance_control(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_INHERITANCE_CONTROL_URL, value)

    @property
    def cqf_should_trace_dependency(self) -> Any:
        return get_extension(self, CQF_SHOULD_TRACE_DEPENDENCY_URL)

    @cqf_should_trace_dependency.setter
    def cqf_should_trace_dependency(self, value: Any) -> None:
        set_extension(self, CQF_SHOULD_TRACE_DEPENDENCY_URL, value)

    @property
    def ext_11179_permitted_value_valueset(self) -> Any:
        return get_extension(self, EXT_11179_PERMITTED_VALUE_VALUESET_URL)

    @ext_11179_permitted_value_valueset.setter
    def ext_11179_permitted_value_valueset(self, value: Any) -> None:
        set_extension(self, EXT_11179_PERMITTED_VALUE_VALUESET_URL, value)

    @property
    def resource_last_review_date(self) -> Any:
        return get_extension(self, RESOURCE_LAST_REVIEW_DATE_URL)

    @resource_last_review_date.setter
    def resource_last_review_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_LAST_REVIEW_DATE_URL, value)

    @property
    def structuredefinition_fmm_no_warnings(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_FMM_NO_WARNINGS_URL)

    @structuredefinition_fmm_no_warnings.setter
    def structuredefinition_fmm_no_warnings(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_FMM_NO_WARNINGS_URL, value)

    @property
    def structuredefinition_standards_status(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_STANDARDS_STATUS_URL)

    @structuredefinition_standards_status.setter
    def structuredefinition_standards_status(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_STANDARDS_STATUS_URL, value)

    @property
    def resource_effective_period(self) -> Any:
        return get_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL)

    @resource_effective_period.setter
    def resource_effective_period(self, value: Any) -> None:
        set_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL, value)

    @property
    def structuredefinition_template_status(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_TEMPLATE_STATUS_URL)

    @structuredefinition_template_status.setter
    def structuredefinition_template_status(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_TEMPLATE_STATUS_URL, value)

    @property
    def structuredefinition_summary(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_SUMMARY_URL)

    @structuredefinition_summary.setter
    def structuredefinition_summary(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_SUMMARY_URL, value)

    @property
    def ext_11179_permitted_value_conceptmap(self) -> Any:
        return get_extension(self, EXT_11179_PERMITTED_VALUE_CONCEPTMAP_URL)

    @ext_11179_permitted_value_conceptmap.setter
    def ext_11179_permitted_value_conceptmap(self, value: Any) -> None:
        set_extension(self, EXT_11179_PERMITTED_VALUE_CONCEPTMAP_URL, value)

    @property
    def obligation(self) -> Any:
        return get_extension(self, OBLIGATION_URL)

    @obligation.setter
    def obligation(self, value: Any) -> None:
        set_extension(self, OBLIGATION_URL, value)

    @property
    def cqf_model_info_is_retrievable(self) -> Any:
        return get_extension(self, CQF_MODEL_INFO_IS_RETRIEVABLE_URL)

    @cqf_model_info_is_retrievable.setter
    def cqf_model_info_is_retrievable(self, value: Any) -> None:
        set_extension(self, CQF_MODEL_INFO_IS_RETRIEVABLE_URL, value)

    @property
    def structuredefinition_impose_profile(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_IMPOSE_PROFILE_URL)

    @structuredefinition_impose_profile.setter
    def structuredefinition_impose_profile(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_IMPOSE_PROFILE_URL, value)

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

    @property
    def structuredefinition_interface(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_INTERFACE_URL)

    @structuredefinition_interface.setter
    def structuredefinition_interface(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_INTERFACE_URL, value)

    @property
    def cqf_model_info_label(self) -> Any:
        return get_extension(self, CQF_MODEL_INFO_LABEL_URL)

    @cqf_model_info_label.setter
    def cqf_model_info_label(self, value: Any) -> None:
        set_extension(self, CQF_MODEL_INFO_LABEL_URL, value)

    @property
    def cqf_model_info_is_included(self) -> Any:
        return get_extension(self, CQF_MODEL_INFO_IS_INCLUDED_URL)

    @cqf_model_info_is_included.setter
    def cqf_model_info_is_included(self, value: Any) -> None:
        set_extension(self, CQF_MODEL_INFO_IS_INCLUDED_URL, value)

    @property
    def structuredefinition_codegen_super(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_CODEGEN_SUPER_URL)

    @structuredefinition_codegen_super.setter
    def structuredefinition_codegen_super(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_CODEGEN_SUPER_URL, value)

    @property
    def structuredefinition_table_name(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_TABLE_NAME_URL)

    @structuredefinition_table_name.setter
    def structuredefinition_table_name(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_TABLE_NAME_URL, value)

    @property
    def structuredefinition_applicable_version(self) -> Any:
        return get_extension(self, STRUCTUREDEFINITION_APPLICABLE_VERSION_URL)

    @structuredefinition_applicable_version.setter
    def structuredefinition_applicable_version(self, value: Any) -> None:
        set_extension(self, STRUCTUREDEFINITION_APPLICABLE_VERSION_URL, value)

class StructureMap(base.StructureMap):

    @property
    def resource_approval_date(self) -> Any:
        return get_extension(self, RESOURCE_APPROVAL_DATE_URL)

    @resource_approval_date.setter
    def resource_approval_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_APPROVAL_DATE_URL, value)

    @property
    def resource_last_review_date(self) -> Any:
        return get_extension(self, RESOURCE_LAST_REVIEW_DATE_URL)

    @resource_last_review_date.setter
    def resource_last_review_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_LAST_REVIEW_DATE_URL, value)

    @property
    def resource_effective_period(self) -> Any:
        return get_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL)

    @resource_effective_period.setter
    def resource_effective_period(self, value: Any) -> None:
        set_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL, value)

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class Subscription(base.Subscription):

    @property
    def subscription_best_effort(self) -> Any:
        return get_extension(self, SUBSCRIPTION_BEST_EFFORT_URL)

    @subscription_best_effort.setter
    def subscription_best_effort(self, value: Any) -> None:
        set_extension(self, SUBSCRIPTION_BEST_EFFORT_URL, value)

class SubscriptionTopic(base.SubscriptionTopic):

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class Substance(base.Substance):

    @property
    def medication_manufacturing_batch(self) -> Any:
        return get_extension(self, MEDICATION_MANUFACTURING_BATCH_URL)

    @medication_manufacturing_batch.setter
    def medication_manufacturing_batch(self, value: Any) -> None:
        set_extension(self, MEDICATION_MANUFACTURING_BATCH_URL, value)

class SupplyDelivery(base.SupplyDelivery):

    @property
    def workflow_triggered_by(self) -> Any:
        return get_extension(self, WORKFLOW_TRIGGERED_BY_URL)

    @workflow_triggered_by.setter
    def workflow_triggered_by(self, value: Any) -> None:
        set_extension(self, WORKFLOW_TRIGGERED_BY_URL, value)

    @property
    def workflow_research_study(self) -> Any:
        return get_extension(self, WORKFLOW_RESEARCH_STUDY_URL)

    @workflow_research_study.setter
    def workflow_research_study(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RESEARCH_STUDY_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def event_status_reason(self) -> Any:
        return get_extension(self, EVENT_STATUS_REASON_URL)

    @event_status_reason.setter
    def event_status_reason(self, value: Any) -> None:
        set_extension(self, EVENT_STATUS_REASON_URL, value)

    @property
    def workflow_adheres_to(self) -> Any:
        return get_extension(self, WORKFLOW_ADHERES_TO_URL)

    @workflow_adheres_to.setter
    def workflow_adheres_to(self, value: Any) -> None:
        set_extension(self, WORKFLOW_ADHERES_TO_URL, value)

    @property
    def event_event_history(self) -> Any:
        return get_extension(self, EVENT_EVENT_HISTORY_URL)

    @event_event_history.setter
    def event_event_history(self, value: Any) -> None:
        set_extension(self, EVENT_EVENT_HISTORY_URL, value)

    @property
    def workflow_shall_comply_with(self) -> Any:
        return get_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL)

    @workflow_shall_comply_with.setter
    def workflow_shall_comply_with(self, value: Any) -> None:
        set_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL, value)

    @property
    def event_location(self) -> Any:
        return get_extension(self, EVENT_LOCATION_URL)

    @event_location.setter
    def event_location(self, value: Any) -> None:
        set_extension(self, EVENT_LOCATION_URL, value)

class SupplyRequest(base.SupplyRequest):

    @property
    def workflow_triggered_by(self) -> Any:
        return get_extension(self, WORKFLOW_TRIGGERED_BY_URL)

    @workflow_triggered_by.setter
    def workflow_triggered_by(self, value: Any) -> None:
        set_extension(self, WORKFLOW_TRIGGERED_BY_URL, value)

    @property
    def workflow_generated_from(self) -> Any:
        return get_extension(self, WORKFLOW_GENERATED_FROM_URL)

    @workflow_generated_from.setter
    def workflow_generated_from(self, value: Any) -> None:
        set_extension(self, WORKFLOW_GENERATED_FROM_URL, value)

    @property
    def request_replaces(self) -> Any:
        return get_extension(self, REQUEST_REPLACES_URL)

    @request_replaces.setter
    def request_replaces(self, value: Any) -> None:
        set_extension(self, REQUEST_REPLACES_URL, value)

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)

    @property
    def workflow_complies_with(self) -> Any:
        return get_extension(self, WORKFLOW_COMPLIES_WITH_URL)

    @workflow_complies_with.setter
    def workflow_complies_with(self, value: Any) -> None:
        set_extension(self, WORKFLOW_COMPLIES_WITH_URL, value)

    @property
    def request_status_reason(self) -> Any:
        return get_extension(self, REQUEST_STATUS_REASON_URL)

    @request_status_reason.setter
    def request_status_reason(self, value: Any) -> None:
        set_extension(self, REQUEST_STATUS_REASON_URL, value)

    @property
    def workflow_shall_comply_with(self) -> Any:
        return get_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL)

    @workflow_shall_comply_with.setter
    def workflow_shall_comply_with(self, value: Any) -> None:
        set_extension(self, WORKFLOW_SHALL_COMPLY_WITH_URL, value)

class Task(base.Task):

    @property
    def workflow_triggered_by(self) -> Any:
        return get_extension(self, WORKFLOW_TRIGGERED_BY_URL)

    @workflow_triggered_by.setter
    def workflow_triggered_by(self, value: Any) -> None:
        set_extension(self, WORKFLOW_TRIGGERED_BY_URL, value)

    @property
    def workflow_research_study(self) -> Any:
        return get_extension(self, WORKFLOW_RESEARCH_STUDY_URL)

    @workflow_research_study.setter
    def workflow_research_study(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RESEARCH_STUDY_URL, value)

    @property
    def workflow_generated_from(self) -> Any:
        return get_extension(self, WORKFLOW_GENERATED_FROM_URL)

    @workflow_generated_from.setter
    def workflow_generated_from(self, value: Any) -> None:
        set_extension(self, WORKFLOW_GENERATED_FROM_URL, value)

    @property
    def request_do_not_perform(self) -> Any:
        return get_extension(self, REQUEST_DO_NOT_PERFORM_URL)

    @request_do_not_perform.setter
    def request_do_not_perform(self, value: Any) -> None:
        set_extension(self, REQUEST_DO_NOT_PERFORM_URL, value)

    @property
    def request_replaces(self) -> Any:
        return get_extension(self, REQUEST_REPLACES_URL)

    @request_replaces.setter
    def request_replaces(self, value: Any) -> None:
        set_extension(self, REQUEST_REPLACES_URL, value)

    @property
    def task_replaces(self) -> Any:
        return get_extension(self, TASK_REPLACES_URL)

    @task_replaces.setter
    def task_replaces(self, value: Any) -> None:
        set_extension(self, TASK_REPLACES_URL, value)

    @property
    def workflow_follow_on_of(self) -> Any:
        return get_extension(self, WORKFLOW_FOLLOW_ON_OF_URL)

    @workflow_follow_on_of.setter
    def workflow_follow_on_of(self, value: Any) -> None:
        set_extension(self, WORKFLOW_FOLLOW_ON_OF_URL, value)

    @property
    def workflow_release_date(self) -> Any:
        return get_extension(self, WORKFLOW_RELEASE_DATE_URL)

    @workflow_release_date.setter
    def workflow_release_date(self, value: Any) -> None:
        set_extension(self, WORKFLOW_RELEASE_DATE_URL, value)

    @property
    def request_performer_order(self) -> Any:
        return get_extension(self, REQUEST_PERFORMER_ORDER_URL)

    @request_performer_order.setter
    def request_performer_order(self, value: Any) -> None:
        set_extension(self, REQUEST_PERFORMER_ORDER_URL, value)

    @property
    def event_event_history(self) -> Any:
        return get_extension(self, EVENT_EVENT_HISTORY_URL)

    @event_event_history.setter
    def event_event_history(self, value: Any) -> None:
        set_extension(self, EVENT_EVENT_HISTORY_URL, value)

    @property
    def workflow_complies_with(self) -> Any:
        return get_extension(self, WORKFLOW_COMPLIES_WITH_URL)

    @workflow_complies_with.setter
    def workflow_complies_with(self, value: Any) -> None:
        set_extension(self, WORKFLOW_COMPLIES_WITH_URL, value)

class TerminologyCapabilities(base.TerminologyCapabilities):

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class TestScript(base.TestScript):

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

class Timing(base.Timing):

    @property
    def timing_day_of_month(self) -> Any:
        return get_extension(self, TIMING_DAY_OF_MONTH_URL)

    @timing_day_of_month.setter
    def timing_day_of_month(self, value: Any) -> None:
        set_extension(self, TIMING_DAY_OF_MONTH_URL, value)

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

    @property
    def timing_exact(self) -> Any:
        return get_extension(self, TIMING_EXACT_URL)

    @timing_exact.setter
    def timing_exact(self, value: Any) -> None:
        set_extension(self, TIMING_EXACT_URL, value)

class TriggerDefinition(base.TriggerDefinition):

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

    @property
    def cqf_parameter_definition(self) -> Any:
        return get_extension(self, CQF_PARAMETER_DEFINITION_URL)

    @cqf_parameter_definition.setter
    def cqf_parameter_definition(self, value: Any) -> None:
        set_extension(self, CQF_PARAMETER_DEFINITION_URL, value)

class UsageContext(base.UsageContext):

    @property
    def cqf_is_empty_list(self) -> Any:
        return get_extension(self, CQF_IS_EMPTY_LIST_URL)

    @cqf_is_empty_list.setter
    def cqf_is_empty_list(self, value: Any) -> None:
        set_extension(self, CQF_IS_EMPTY_LIST_URL, value)

    @property
    def usagecontext_group(self) -> Any:
        return get_extension(self, USAGECONTEXT_GROUP_URL)

    @usagecontext_group.setter
    def usagecontext_group(self, value: Any) -> None:
        set_extension(self, USAGECONTEXT_GROUP_URL, value)

class ValueSet(base.ValueSet):

    @property
    def valueset_unclosed(self) -> Any:
        return get_extension(self, VALUESET_UNCLOSED_URL)

    @valueset_unclosed.setter
    def valueset_unclosed(self, value: Any) -> None:
        set_extension(self, VALUESET_UNCLOSED_URL, value)

    @property
    def resource_approval_date(self) -> Any:
        return get_extension(self, RESOURCE_APPROVAL_DATE_URL)

    @resource_approval_date.setter
    def resource_approval_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_APPROVAL_DATE_URL, value)

    @property
    def valueset_compose_created_by(self) -> Any:
        return get_extension(self, VALUESET_COMPOSE_CREATED_BY_URL)

    @valueset_compose_created_by.setter
    def valueset_compose_created_by(self, value: Any) -> None:
        set_extension(self, VALUESET_COMPOSE_CREATED_BY_URL, value)

    @property
    def terminology_resource_identifier_metadata(self) -> Any:
        return get_extension(self, TERMINOLOGY_RESOURCE_IDENTIFIER_METADATA_URL)

    @terminology_resource_identifier_metadata.setter
    def terminology_resource_identifier_metadata(self, value: Any) -> None:
        set_extension(self, TERMINOLOGY_RESOURCE_IDENTIFIER_METADATA_URL, value)

    @property
    def valueset_concept_order(self) -> Any:
        return get_extension(self, VALUESET_CONCEPT_ORDER_URL)

    @valueset_concept_order.setter
    def valueset_concept_order(self, value: Any) -> None:
        set_extension(self, VALUESET_CONCEPT_ORDER_URL, value)

    @property
    def valueset_label(self) -> Any:
        return get_extension(self, VALUESET_LABEL_URL)

    @valueset_label.setter
    def valueset_label(self, value: Any) -> None:
        set_extension(self, VALUESET_LABEL_URL, value)

    @property
    def resource_last_review_date(self) -> Any:
        return get_extension(self, RESOURCE_LAST_REVIEW_DATE_URL)

    @resource_last_review_date.setter
    def resource_last_review_date(self, value: Any) -> None:
        set_extension(self, RESOURCE_LAST_REVIEW_DATE_URL, value)

    @property
    def valueset_toocostly(self) -> Any:
        return get_extension(self, VALUESET_TOOCOSTLY_URL)

    @valueset_toocostly.setter
    def valueset_toocostly(self, value: Any) -> None:
        set_extension(self, VALUESET_TOOCOSTLY_URL, value)

    @property
    def valueset_map(self) -> Any:
        return get_extension(self, VALUESET_MAP_URL)

    @valueset_map.setter
    def valueset_map(self, value: Any) -> None:
        set_extension(self, VALUESET_MAP_URL, value)

    @property
    def valueset_system_ref(self) -> Any:
        return get_extension(self, VALUESET_SYSTEM_REF_URL)

    @valueset_system_ref.setter
    def valueset_system_ref(self, value: Any) -> None:
        set_extension(self, VALUESET_SYSTEM_REF_URL, value)

    @property
    def valueset_special_status(self) -> Any:
        return get_extension(self, VALUESET_SPECIAL_STATUS_URL)

    @valueset_special_status.setter
    def valueset_special_status(self, value: Any) -> None:
        set_extension(self, VALUESET_SPECIAL_STATUS_URL, value)

    @property
    def valueset_compose_creation_date(self) -> Any:
        return get_extension(self, VALUESET_COMPOSE_CREATION_DATE_URL)

    @valueset_compose_creation_date.setter
    def valueset_compose_creation_date(self, value: Any) -> None:
        set_extension(self, VALUESET_COMPOSE_CREATION_DATE_URL, value)

    @property
    def valueset_concept_definition(self) -> Any:
        return get_extension(self, VALUESET_CONCEPT_DEFINITION_URL)

    @valueset_concept_definition.setter
    def valueset_concept_definition(self, value: Any) -> None:
        set_extension(self, VALUESET_CONCEPT_DEFINITION_URL, value)

    @property
    def resource_effective_period(self) -> Any:
        return get_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL)

    @resource_effective_period.setter
    def resource_effective_period(self, value: Any) -> None:
        set_extension(self, RESOURCE_EFFECTIVE_PERIOD_URL, value)

    @property
    def valueset_concept_comments(self) -> Any:
        return get_extension(self, VALUESET_CONCEPT_COMMENTS_URL)

    @valueset_concept_comments.setter
    def valueset_concept_comments(self, value: Any) -> None:
        set_extension(self, VALUESET_CONCEPT_COMMENTS_URL, value)

    @property
    def valueset_source_reference(self) -> Any:
        return get_extension(self, VALUESET_SOURCE_REFERENCE_URL)

    @valueset_source_reference.setter
    def valueset_source_reference(self, value: Any) -> None:
        set_extension(self, VALUESET_SOURCE_REFERENCE_URL, value)

    @property
    def valueset_compose_include_value_set_title(self) -> Any:
        return get_extension(self, VALUESET_COMPOSE_INCLUDE_VALUE_SET_TITLE_URL)

    @valueset_compose_include_value_set_title.setter
    def valueset_compose_include_value_set_title(self, value: Any) -> None:
        set_extension(self, VALUESET_COMPOSE_INCLUDE_VALUE_SET_TITLE_URL, value)

    @property
    def valueset_system_name(self) -> Any:
        return get_extension(self, VALUESET_SYSTEM_NAME_URL)

    @valueset_system_name.setter
    def valueset_system_name(self, value: Any) -> None:
        set_extension(self, VALUESET_SYSTEM_NAME_URL, value)

    @property
    def valueset_parameter_source(self) -> Any:
        return get_extension(self, VALUESET_PARAMETER_SOURCE_URL)

    @valueset_parameter_source.setter
    def valueset_parameter_source(self, value: Any) -> None:
        set_extension(self, VALUESET_PARAMETER_SOURCE_URL, value)

    @property
    def valueset_expansion_source(self) -> Any:
        return get_extension(self, VALUESET_EXPANSION_SOURCE_URL)

    @valueset_expansion_source.setter
    def valueset_expansion_source(self, value: Any) -> None:
        set_extension(self, VALUESET_EXPANSION_SOURCE_URL, value)

    @property
    def valueset_system(self) -> Any:
        return get_extension(self, VALUESET_SYSTEM_URL)

    @valueset_system.setter
    def valueset_system(self, value: Any) -> None:
        set_extension(self, VALUESET_SYSTEM_URL, value)

    @property
    def valueset_warning(self) -> Any:
        return get_extension(self, VALUESET_WARNING_URL)

    @valueset_warning.setter
    def valueset_warning(self, value: Any) -> None:
        set_extension(self, VALUESET_WARNING_URL, value)

    @property
    def replaces(self) -> Any:
        return get_extension(self, REPLACES_URL)

    @replaces.setter
    def replaces(self, value: Any) -> None:
        set_extension(self, REPLACES_URL, value)

    @property
    def valueset_case_sensitive(self) -> Any:
        return get_extension(self, VALUESET_CASE_SENSITIVE_URL)

    @valueset_case_sensitive.setter
    def valueset_case_sensitive(self, value: Any) -> None:
        set_extension(self, VALUESET_CASE_SENSITIVE_URL, value)

    @property
    def valueset_trusted_expansion(self) -> Any:
        return get_extension(self, VALUESET_TRUSTED_EXPANSION_URL)

    @valueset_trusted_expansion.setter
    def valueset_trusted_expansion(self, value: Any) -> None:
        set_extension(self, VALUESET_TRUSTED_EXPANSION_URL, value)

    @property
    def valueset_expression(self) -> Any:
        return get_extension(self, VALUESET_EXPRESSION_URL)

    @valueset_expression.setter
    def valueset_expression(self, value: Any) -> None:
        set_extension(self, VALUESET_EXPRESSION_URL, value)

    @property
    def valueset_supplement(self) -> Any:
        return get_extension(self, VALUESET_SUPPLEMENT_URL)

    @valueset_supplement.setter
    def valueset_supplement(self, value: Any) -> None:
        set_extension(self, VALUESET_SUPPLEMENT_URL, value)

    @property
    def valueset_authoritative_source(self) -> Any:
        return get_extension(self, VALUESET_AUTHORITATIVE_SOURCE_URL)

    @valueset_authoritative_source.setter
    def valueset_authoritative_source(self, value: Any) -> None:
        set_extension(self, VALUESET_AUTHORITATIVE_SOURCE_URL, value)

    @property
    def valueset_usage(self) -> Any:
        return get_extension(self, VALUESET_USAGE_URL)

    @valueset_usage.setter
    def valueset_usage(self, value: Any) -> None:
        set_extension(self, VALUESET_USAGE_URL, value)

    @property
    def valueset_other_title(self) -> Any:
        return get_extension(self, VALUESET_OTHER_TITLE_URL)

    @valueset_other_title.setter
    def valueset_other_title(self, value: Any) -> None:
        set_extension(self, VALUESET_OTHER_TITLE_URL, value)

    @property
    def valueset_deprecated(self) -> Any:
        return get_extension(self, VALUESET_DEPRECATED_URL)

    @valueset_deprecated.setter
    def valueset_deprecated(self, value: Any) -> None:
        set_extension(self, VALUESET_DEPRECATED_URL, value)

    @property
    def valueset_key_word(self) -> Any:
        return get_extension(self, VALUESET_KEY_WORD_URL)

    @valueset_key_word.setter
    def valueset_key_word(self, value: Any) -> None:
        set_extension(self, VALUESET_KEY_WORD_URL, value)

    @property
    def valueset_workflow_status_description(self) -> Any:
        return get_extension(self, VALUESET_WORKFLOW_STATUS_DESCRIPTION_URL)

    @valueset_workflow_status_description.setter
    def valueset_workflow_status_description(self, value: Any) -> None:
        set_extension(self, VALUESET_WORKFLOW_STATUS_DESCRIPTION_URL, value)

    @property
    def valueset_system_title(self) -> Any:
        return get_extension(self, VALUESET_SYSTEM_TITLE_URL)

    @valueset_system_title.setter
    def valueset_system_title(self, value: Any) -> None:
        set_extension(self, VALUESET_SYSTEM_TITLE_URL, value)

    @property
    def valueset_extensible(self) -> Any:
        return get_extension(self, VALUESET_EXTENSIBLE_URL)

    @valueset_extensible.setter
    def valueset_extensible(self, value: Any) -> None:
        set_extension(self, VALUESET_EXTENSIBLE_URL, value)

    @property
    def coding_sctdescid(self) -> Any:
        return get_extension(self, CODING_SCTDESCID_URL)

    @coding_sctdescid.setter
    def coding_sctdescid(self, value: Any) -> None:
        set_extension(self, CODING_SCTDESCID_URL, value)

    @property
    def valueset_other_name(self) -> Any:
        return get_extension(self, VALUESET_OTHER_NAME_URL)

    @valueset_other_name.setter
    def valueset_other_name(self, value: Any) -> None:
        set_extension(self, VALUESET_OTHER_NAME_URL, value)

    @property
    def valueset_rules_text(self) -> Any:
        return get_extension(self, VALUESET_RULES_TEXT_URL)

    @valueset_rules_text.setter
    def valueset_rules_text(self, value: Any) -> None:
        set_extension(self, VALUESET_RULES_TEXT_URL, value)

class VisionPrescription(base.VisionPrescription):

    @property
    def workflow_episode_of_care(self) -> Any:
        return get_extension(self, WORKFLOW_EPISODE_OF_CARE_URL)

    @workflow_episode_of_care.setter
    def workflow_episode_of_care(self, value: Any) -> None:
        set_extension(self, WORKFLOW_EPISODE_OF_CARE_URL, value)
