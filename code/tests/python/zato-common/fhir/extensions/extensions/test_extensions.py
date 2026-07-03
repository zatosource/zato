from __future__ import annotations

from zato.fhir.r4_0_1.extensions.v5_1_0.extensions import (
    CONTACTPOINT_AREA_URL,
    STRUCTUREDEFINITION_EXTENSION_MEANING_URL,
    ELEMENTDEFINITION_BESTPRACTICE_EXPLANATION_URL,
    ISO21090_ADXP_POST_BOX_URL,
    ARTIFACT_EDITOR_URL,
    ARTIFACT_CITE_AS_URL,
    OPERATIONOUTCOME_FILE_URL,
    RESEARCH_STUDY_STUDY_REGISTRATION_URL,
    MEASUREREPORT_POPULATION_DESCRIPTION_URL,
    CQF_CRITERIA_REFERENCE_URL,
    CQF_CALCULATED_VALUE_URL,
    AUDITEVENT_PARTICIPANT_OBJECT_CONTAINS_STUDY_URL,
    STRUCTUREDEFINITION_DISPLAY_HINT_URL,
    PARAMETERS_FULL_URL_URL,
    HUMANNAME_MOTHERS_FAMILY_URL,
    ELEMENTDEFINITION_PATTERN_URL,
    CQF_EXPRESSION_URL,
    WORKFLOW_TRIGGERED_BY_URL,
    ISO21090_UNCERTAINTY_TYPE_URL,
    TARGET_PATH_URL,
    CONSENT_TRANSCRIBER_URL,
    EXTENDED_CONTACT_AVAILABILITY_URL,
    DEVICEREQUEST_PATIENT_INSTRUCTION_URL,
    ISO21090_ADXP_STREET_NAME_URL,
    NARRATIVE_LINK_URL,
    UNCERTAIN_PERIOD_URL,
    ARTIFACT_PERIOD_DURATION_URL,
    ALTERNATE_CODES_URL,
    EVENT_PERFORMER_FUNCTION_URL,
    VALUESET_UNCLOSED_URL,
    ALLERGYINTOLERANCE_DURATION_URL,
    ELEMENTDEFINITION_TYPE_MUST_SUPPORT_URL,
    CQF_ARTIFACT_COMMENT_URL,
    ISO21090_ADXP_UNIT_ID_URL,
    CQF_LIBRARY_URL,
    ELEMENTDEFINITION_TRANSLATABLE_URL,
    CQF_IS_PRIMARY_CITATION_URL,
    RENDERING_STYLE_URL,
    RESOLVE_AS_VERSION_SPECIFIC_URL,
    REQUIREMENTS_PARENT_URL,
    CQF_KNOWLEDGE_CAPABILITY_URL,
    MIN_LENGTH_URL,
    CODESYSTEM_WARNING_URL,
    STRUCTUREDEFINITION_TYPE_CHARACTERISTICS_URL,
    REFERENCES_CONTAINED_URL,
    CONDITION_RULED_OUT_URL,
    OBSERVATION_BODY_POSITION_URL,
    QUESTIONNAIRE_FHIR_TYPE_URL,
    MEASUREREPORT_CATEGORY_URL,
    PROCEDURE_PROGRESS_STATUS_URL,
    PATIENT_PROFICIENCY_URL,
    DIAGNOSTIC_REPORT_FOCUS_URL,
    LIST_CHANGE_BASE_URL,
    MEDICATIONDISPENSE_REFILLS_REMAINING_URL,
    RELATIVE_DATE_URL,
    ADDRESS_OFFICIAL_URL,
    CQF_TEST_ARTIFACT_URL,
    PATIENT_SEX_PARAMETER_FOR_CLINICAL_USE_URL,
    RESOURCE_APPROVAL_DATE_URL,
    ELEMENTDEFINITION_CONCEPTMAP_URL,
    STRUCTUREDEFINITION_COMPLIES_WITH_PROFILE_URL,
    CQF_CONTRIBUTION_TIME_URL,
    CONDITION_RELATED_URL,
    CQF_IS_SELECTIVE_URL,
    DEVICE_MAINTENANCERESPONSIBILITY_URL,
    CONDITION_DISEASE_COURSE_URL,
    CQF_CITATION_URL,
    ARTIFACT_RELEASE_DESCRIPTION_URL,
    ISO21090_ADXP_STREET_NAME_BASE_URL,
    ISO21090_ADXP_UNIT_TYPE_URL,
    STRUCTUREDEFINITION_CATEGORY_URL,
    ARTIFACT_IS_OWNED_URL,
    STRUCTUREDEFINITION_FMM_URL,
    EXT_11179_OBJECT_CLASS_URL,
    HUMANNAME_OWN_PREFIX_URL,
    ISO21090_ADXP_STREET_NAME_TYPE_URL,
    ELEMENTDEFINITION_EQUIVALENCE_URL,
    ENCOUNTER_MODE_OF_ARRIVAL_URL,
    PROCEDURE_DIRECTED_BY_URL,
    CQF_CQL_ACCESS_MODIFIER_URL,
    ARTIFACT_EXPERIMENTAL_URL,
    CQF_MODEL_INFO_SETTINGS_URL,
    FAMILY_MEMBER_HISTORY_GENETICS_PARENT_URL,
    QUESTIONNAIRE_CONSTRAINT_URL,
    VALUESET_COMPOSE_CREATED_BY_URL,
    CQF_TARGET_INVARIANT_URL,
    STRUCTUREDEFINITION_FHIR_TYPE_URL,
    VERSION_SPECIFIC_USE_URL,
    ELEMENTDEFINITION_PROFILE_ELEMENT_URL,
    CODESYSTEM_ALTERNATE_URL,
    AUDITEVENT_MPPS_URL,
    CQF_MODEL_INFO_PRIMARY_CODE_PATH_URL,
    PATIENT_MULTIPLE_BIRTH_TOTAL_URL,
    RENDERING_MARKDOWN_URL,
    CQF_PUBLICATION_STATUS_URL,
    QUESTIONNAIRERESPONSE_REASON_URL,
    OBSERVATION_SPECIMEN_CODE_URL,
    CONFIDENTIAL_URL,
    QUESTIONNAIRE_REFERENCE_FILTER_URL,
    OPEN_EHR_EXPOSURE_DESCRIPTION_URL,
    ARTIFACTASSESSMENT_DISPOSITION_URL,
    OPEN_EHR_CAREPLAN_URL,
    AUDITEVENT_LIFECYCLE_URL,
    FAMILYMEMBERHISTORY_PATIENT_RECORD_URL,
    AUDITEVENT_ANONYMIZED_URL,
    OBSERVATION_NATURE_OF_ABNORMAL_TEST_URL,
    ELEMENTDEFINITION_SELECTOR_URL,
    SATISFIES_REQUIREMENT_URL,
    PROCEDURE_CAUSED_BY_URL,
    PATIENT_IMPORTANCE_URL,
    MAX_VALUE_URL,
    TIMING_DAY_OF_MONTH_URL,
    ALTERNATE_CANONICAL_URL,
    CONTACTPOINT_LOCAL_URL,
    RESOURCE_PERTAINS_TO_GOAL_URL,
    STRUCTUREDEFINITION_SECURITY_CATEGORY_URL,
    PATIENT_CONGREGATION_URL,
    CODESYSTEM_HISTORY_URL,
    QUESTIONNAIRE_SIGNATURE_REQUIRED_URL,
    ARTIFACT_URI_REFERENCE_URL,
    ISO21090_ADXP_ADDITIONAL_LOCATOR_URL,
    PATIENT_DISABILITY_URL,
    LAST_SOURCE_SYNC_URL,
    STRUCTUREDEFINITION_ANCESTOR_URL,
    OBSERVATION_ANALYSIS_DATE_TIME_URL,
    ARTIFACT_CONTACT_DETAIL_REFERENCE_URL,
    ELEMENTDEFINITION_MAX_VALUE_SET_URL,
    ISO21090_EN_REPRESENTATION_URL,
    CITATION_SOCIETY_AFFILIATION_URL,
    SPECIMEN_SEQUENCE_NUMBER_URL,
    OBSERVATION_REAGENT_URL,
    DEVICE_LASTMAINTENANCETIME_URL,
    QUESTIONNAIRE_DERIVATION_TYPE_URL,
    LANGUAGE_URL,
    STRUCTUREDEFINITION_STANDARDS_STATUS_REASON_URL,
    MEASUREREPORT_COUNT_QUANTITY_URL,
    MAX_DECIMAL_PLACES_URL,
    TIMING_DAYS_OF_CYCLE_URL,
    ADDITIONAL_IDENTIFIER_URL,
    DEVICE_IMPLANT_STATUS_URL,
    ARTIFACT_DESCRIPTION_URL,
    TERMINOLOGY_RESOURCE_IDENTIFIER_METADATA_URL,
    CQF_SCOPE_URL,
    OPEN_EHR_LOCATION_URL,
    CODESYSTEM_PROPERTIES_MODE_URL,
    WORKFLOW_RESEARCH_STUDY_URL,
    CQF_IS_EMPTY_LIST_URL,
    ALLERGYINTOLERANCE_SUBSTANCE_EXPOSURE_RISK_URL,
    GEOLOCATION_URL,
    OPERATIONOUTCOME_ISSUE_SOURCE_URL,
    WORKFLOW_GENERATED_FROM_URL,
    ISO21090_TEL_ADDRESS_URL,
    CQF_CDS_HOOKS_ENDPOINT_URL,
    ALTERNATE_REFERENCE_URL,
    QUESTIONNAIRE_UNIT_URL,
    CONDITION_DUE_TO_URL,
    RENDERED_VALUE_URL,
    GOAL_ACCEPTANCE_URL,
    REQUEST_INSURANCE_URL,
    COMPOSITION_SECTION_SUBJECT_URL,
    IDENTIFIER_CHECK_DIGIT_URL,
    PATIENT_MOTHERS_MAIDEN_NAME_URL,
    ARTIFACT_TITLE_URL,
    CQF_MEASURE_INFO_URL,
    TZ_OFFSET_URL,
    QUESTIONNAIRE_MIN_OCCURS_URL,
    HUMANNAME_ASSEMBLY_ORDER_URL,
    CODESYSTEM_TRUSTED_EXPANSION_URL,
    STRUCTUREDEFINITION_INHERITANCE_CONTROL_URL,
    PATIENT_CONTACT_PRIORITY_URL,
    HUMANNAME_PARTNER_PREFIX_URL,
    CQF_CONTACT_REFERENCE_URL,
    CONTACTPOINT_PURPOSE_URL,
    CQF_INITIAL_VALUE_URL,
    ORGANIZATION_PREFERRED_CONTACT_URL,
    PATIENT_BIRTH_PLACE_URL,
    ISO21090_ADXP_HOUSE_NUMBER_URL,
    CQF_RESOURCE_TYPE_URL,
    DERIVATION_REFERENCE_URL,
    FLAG_DETAIL_URL,
    QUESTIONNAIRE_HIDDEN_URL,
    NO_FIXED_ADDRESS_URL,
    ELEMENTDEFINITION_IS_COMMON_BINDING_URL,
    SERVICEREQUEST_PRECONDITION_URL,
    ALLERGYINTOLERANCE_ABATEMENT_URL,
    TARGET_CONSTRAINT_URL,
    CQF_SHOULD_TRACE_DEPENDENCY_URL,
    ARTIFACT_CONTACT_URL,
    ALLERGYINTOLERANCE_REASON_REFUTED_URL,
    QUESTIONNAIRERESPONSE_REVIEWER_URL,
    CQF_FHIR_QUERY_PATTERN_URL,
    ELEMENTDEFINITION_DEFAULTTYPE_URL,
    MEDICATIONDISPENSE_QUANTITY_REMAINING_URL,
    CONTACTPOINT_EXTENSION_URL,
    DEVICE_COMMERCIAL_BRAND_URL,
    REQUEST_DO_NOT_PERFORM_URL,
    REQUEST_REPLACES_URL,
    CQF_INITIATING_ORGANIZATION_URL,
    AUDITEVENT_INSTANCE_URL,
    AUDITEVENT_ACCESSION_URL,
    PATIENT_PREFERENCE_TYPE_URL,
    OBSERVATION_REPLACES_URL,
    ARTIFACT_LAST_REVIEW_DATE_URL,
    CODESYSTEM_OTHER_NAME_URL,
    QUESTIONNAIRE_UNIT_OPTION_URL,
    DOCUMENTREFERENCE_SOURCEPATIENT_URL,
    CQF_INITIATING_PERSON_URL,
    CAPABILITYSTATEMENT_SEARCH_MODE_URL,
    ORGANIZATION_BRAND_URL,
    OBSERVATION_V2_SUBID_URL,
    VALUESET_CONCEPT_ORDER_URL,
    ARTIFACT_AUTHOR_URL,
    RESEARCH_STUDY_SITE_RECRUITMENT_URL,
    CQF_PARAMETER_DEFINITION_URL,
    VALUESET_LABEL_URL,
    FAMILY_MEMBER_HISTORY_GENETICS_SIBLING_URL,
    HTTP_RESPONSE_HEADER_URL,
    ARTIFACT_COPYRIGHT_LABEL_URL,
    CARETEAM_ALIAS_URL,
    IDENTIFIER_VALID_DATE_URL,
    COMPOSITION_CLINICALDOCUMENT_VERSION_NUMBER_URL,
    GOAL_REASON_REJECTED_URL,
    EXT_11179_PERMITTED_VALUE_VALUESET_URL,
    ARTIFACT_IDENTIFIER_URL,
    RESOURCE_LAST_REVIEW_DATE_URL,
    ARTIFACTASSESSMENT_WORKFLOW_STATUS_URL,
    OBSERVATION_DEVICE_CODE_URL,
    VALUESET_TOOCOSTLY_URL,
    PATIENT_RELIGION_URL,
    ARTIFACT_EFFECTIVE_PERIOD_URL,
    STATISTIC_MODEL_INCLUDE_IF_URL,
    DIAGNOSTIC_REPORT_RISK_URL,
    ELEMENTDEFINITION_ALLOWED_UNITS_URL,
    ARTIFACT_COPYRIGHT_URL,
    CQF_EXPANSION_PARAMETERS_URL,
    CODESYSTEM_AUTHORITATIVE_SOURCE_URL,
    OPEN_EHR_EXPOSURE_DURATION_URL,
    _DATATYPE_URL,
    ISO21090_ADXP_DELIVERY_MODE_IDENTIFIER_URL,
    CQF_PUBLICATION_DATE_URL,
    VALUESET_MAP_URL,
    QUESTIONNAIRERESPONSE_AUTHOR_URL,
    ISO21090_EN_QUALIFIER_URL,
    VALUESET_SYSTEM_REF_URL,
    OPERATIONOUTCOME_DETECTED_ISSUE_URL,
    BIOLOGICALLYDERIVEDPRODUCT_COLLECTION_PROCEDURE_URL,
    CQF_CERTAINTY_URL,
    DIAGNOSTIC_REPORT_EXTENDS_URL,
    CQF_VALUE_FILTER_URL,
    SUBSCRIPTION_BEST_EFFORT_URL,
    QUESTIONNAIRE_UNIT_VALUE_SET_URL,
    RENDERING_XHTML_URL,
    CONDITION_OCCURRED_FOLLOWING_URL,
    CQF_SYSTEM_USER_LANGUAGE_URL,
    OBSERVATION_SEQUEL_TO_URL,
    PATIENT_RELATED_PERSON_URL,
    HUMANNAME_OWN_NAME_URL,
    DIAGNOSTIC_REPORT_SUMMARY_OF_URL,
    VALUESET_SPECIAL_STATUS_URL,
    OPERATIONOUTCOME_ISSUE_COL_URL,
    AUDITEVENT_ON_BEHALF_OF_URL,
    INDIVIDUAL_PRONOUNS_URL,
    STRUCTUREDEFINITION_FMM_NO_WARNINGS_URL,
    CAPABILITYSTATEMENT_SEARCH_PARAMETER_USE_URL,
    TRANSLATION_URL,
    WORKFLOW_PROTECTIVE_FACTOR_URL,
    VALUESET_COMPOSE_CREATION_DATE_URL,
    LOCATION_COMMUNICATION_URL,
    PATIENT_KNOWN_NON_DUPLICATE_URL,
    ELEMENTDEFINITION_SUPPRESS_URL,
    OAUTH_URIS_URL,
    LARGE_VALUE_URL,
    QUESTIONNAIRERESPONSE_COMPLETION_MODE_URL,
    CAPABILITYSTATEMENT_EXPECTATION_URL,
    ARTIFACT_PURPOSE_URL,
    FAMILYMEMBERHISTORY_TYPE_URL,
    STRUCTUREDEFINITION_STANDARDS_STATUS_URL,
    LOCATION_DISTANCE_URL,
    DIAGNOSTIC_REPORT_WORKFLOW_STATUS_URL,
    CAPABILITYSTATEMENT_DECLARED_PROFILE_URL,
    AUDITEVENT_SOPCLASS_URL,
    CQF_RECIPIENT_TYPE_URL,
    QUESTIONNAIRE_OPTION_EXCLUSIVE_URL,
    SPECIMEN_IS_DRY_WEIGHT_URL,
    ARTIFACT_RELATED_ARTIFACT_URL,
    TASK_REPLACES_URL,
    ARTIFACT_REFERENCE_URL,
    CQF_DIRECT_REFERENCE_CODE_URL,
    IMMUNIZATION_PROCEDURE_URL,
    VALUESET_CONCEPT_DEFINITION_URL,
    ANNOTATION_TYPE_URL,
    ENCOUNTER_REASON_CANCELLED_URL,
    STRUCTUREDEFINITION_EXPLICIT_TYPE_NAME_URL,
    EVENT_PART_OF_URL,
    RESOURCE_EFFECTIVE_PERIOD_URL,
    AUDITEVENT_ALTERNATIVE_USER_ID_URL,
    ISO21090_ADXP_DELIVERY_INSTALLATION_AREA_URL,
    WORKFLOW_RELATED_ARTIFACT_URL,
    VALUESET_CONCEPT_COMMENTS_URL,
    OBSERVATION_PRECONDITION_URL,
    SERVICEREQUEST_QUESTIONNAIRE_REQUEST_URL,
    CONCEPT_BIDIRECTIONAL_URL,
    NUTRITIONORDER_ADAPTIVE_FEEDING_DEVICE_URL,
    ISO21090_CODED_STRING_URL,
    ELEMENTDEFINITION_IDENTIFIER_URL,
    ISO21090_ADXP_DELIVERY_ADDRESS_LINE_URL,
    COMMUNICATION_MEDIA_URL,
    STRUCTUREDEFINITION_HIERARCHY_URL,
    SPECIMEN_ADDITIVE_URL,
    PATIENT_BIRTH_TIME_URL,
    PRACTITIONERROLE_EMPLOYMENT_STATUS_URL,
    VALUESET_SOURCE_REFERENCE_URL,
    WORKFLOW_FOLLOW_ON_OF_URL,
    QUANTITY_PRECISION_URL,
    CONDITION_OUTCOME_URL,
    DISPLAY_URL,
    CONTACTPOINT_COMMENT_URL,
    VALUESET_COMPOSE_INCLUDE_VALUE_SET_TITLE_URL,
    VALUESET_REFERENCE_URL,
    ARTIFACT_USAGE_URL,
    ISO21090_ADXP_DELIVERY_INSTALLATION_QUALIFIER_URL,
    ALLERGYINTOLERANCE_RESOLUTION_AGE_URL,
    ARTIFACT_ENDORSER_URL,
    OPEN_EHR_MANAGEMENT_URL,
    QUESTIONNAIRE_OPTION_RESTRICTION_URL,
    NOTE_URL,
    FAMILYMEMBERHISTORY_SEVERITY_URL,
    VERSION_SPECIFIC_VALUE_URL,
    ORGANIZATION_PERIOD_URL,
    CQF_SUPPORTED_CQL_VERSION_URL,
    VALUESET_SYSTEM_NAME_URL,
    ISO21090_ADXP_STREET_ADDRESS_LINE_URL,
    FAMILYMEMBERHISTORY_ABATEMENT_URL,
    ARTIFACT_NAME_URL,
    INDIVIDUAL_GENDER_IDENTITY_URL,
    QUESTIONNAIRE_MAX_OCCURS_URL,
    STRUCTUREDEFINITION_TEMPLATE_STATUS_URL,
    LIST_FOR_URL,
    ARTIFACT_JURISDICTION_URL,
    CODESYSTEM_LABEL_URL,
    CQF_KNOWLEDGE_REPRESENTATION_LEVEL_URL,
    PROCEDURE_METHOD_URL,
    ISO21090_EN_USE_URL,
    EVENT_BASED_ON_URL,
    USAGECONTEXT_GROUP_URL,
    STRUCTUREDEFINITION_SUMMARY_URL,
    DIAGNOSTIC_REPORT_ADDENDUM_OF_URL,
    WORKFLOW_RELEASE_DATE_URL,
    EXT_11179_PERMITTED_VALUE_CONCEPTMAP_URL,
    STRUCTUREDEFINITION_NORMATIVE_VERSION_URL,
    ARTIFACT_CANONICAL_REFERENCE_URL,
    OPERATIONOUTCOME_ISSUE_SLICETEXT_URL,
    CAPABILITYSTATEMENT_PROHIBITED_URL,
    OBLIGATION_URL,
    ISO21090_ADXP_CARE_OF_URL,
    CQM_VALIDITY_PERIOD_URL,
    OBSERVATION_DELTA_URL,
    ORIGINAL_TEXT_URL,
    REQUEST_RELEVANT_HISTORY_URL,
    STRUCTUREDEFINITION_CONFORMANCE_DERIVED_FROM_URL,
    VALUESET_PARAMETER_SOURCE_URL,
    WORKFLOW_SUPPORTING_INFO_URL,
    CONSENT_NOTIFICATION_ENDPOINT_URL,
    EXT_11179_OBJECT_CLASS_PROPERTY_URL,
    MATCH_GRADE_URL,
    ISO21090_ADXP_DELIVERY_MODE_URL,
    VALUESET_EXPANSION_SOURCE_URL,
    QUESTIONNAIRE_DEFINITION_BASED_URL,
    DIAGNOSTIC_REPORT_REPLACES_URL,
    MEDICATION_MANUFACTURING_BATCH_URL,
    CQF_ENCOUNTER_CLASS_URL,
    OPEN_EHR_EXPOSURE_DATE_URL,
    CONDITION_ASSERTED_DATE_URL,
    PRACTITIONER_JOB_TITLE_URL,
    CQF_CONTACT_ADDRESS_URL,
    CODESYSTEM_CONCEPT_ORDER_URL,
    CQF_ALTERNATIVE_EXPRESSION_URL,
    ARTIFACT_REVIEWER_URL,
    HUMANNAME_FATHERS_FAMILY_URL,
    CQF_RELATIVE_DATE_TIME_URL,
    CQF_RECIPIENT_LANGUAGE_URL,
    DOSAGE_MINIMUM_GAP_BETWEEN_DOSE_URL,
    DOCUMENTREFERENCE_THUMBNAIL_URL,
    QUESTIONNAIRE_ITEM_CONTROL_URL,
    VALUESET_SYSTEM_URL,
    QUESTIONNAIRE_SUPPORT_LINK_URL,
    FAMILY_MEMBER_HISTORY_GENETICS_OBSERVATION_URL,
    CQF_CQL_TYPE_URL,
    SPECIMEN_SPECIAL_HANDLING_URL,
    TIMEZONE_URL,
    CQF_MODEL_INFO_IS_RETRIEVABLE_URL,
    STRUCTUREDEFINITION_IMPOSE_PROFILE_URL,
    PATIENT_NATIONALITY_URL,
    WORKFLOW_EPISODE_OF_CARE_URL,
    CANONICALRESOURCE_SHORT_DESCRIPTION_URL,
    NAMINGSYSTEM_CHECK_DIGIT_URL,
    REQUEST_PERFORMER_ORDER_URL,
    MIN_VALUE_URL,
    LOCATION_BOUNDARY_GEOJSON_URL,
    CQF_IS_PREFETCH_TOKEN_URL,
    CQF_DEFINITION_TERM_URL,
    VALUESET_WARNING_URL,
    ISO21090_ADXP_HOUSE_NUMBER_NUMERIC_URL,
    REPLACES_URL,
    LIST_CATEGORY_URL,
    CONSENT_LOCATION_URL,
    CQF_CQL_OPTIONS_URL,
    BIOLOGICALLYDERIVEDPRODUCT_PROCESSING_URL,
    PATIENT_BORN_STATUS_URL,
    VALUESET_CASE_SENSITIVE_URL,
    MIME_TYPE_URL,
    EVENT_STATUS_REASON_URL,
    CODESYSTEM_KEY_WORD_URL,
    DESIGN_NOTE_URL,
    ISO21090_ADXP_DELIMITER_URL,
    HUMANNAME_PARTNER_NAME_URL,
    ELEMENTDEFINITION_INHERITED_EXTENSIBLE_VALUE_SET_URL,
    ARTIFACT_USE_CONTEXT_URL,
    ALLERGYINTOLERANCE_CERTAINTY_URL,
    SPECIMEN_COLLECTION_PRIORITY_URL,
    VARIABLE_URL,
    OPERATIONOUTCOME_MESSAGE_ID_URL,
    COMMUNICATIONREQUEST_INITIATING_LOCATION_URL,
    CODESYSTEM_SOURCE_REFERENCE_URL,
    VALUESET_TRUSTED_EXPANSION_URL,
    VALUESET_EXPRESSION_URL,
    PATIENT_ADOPTION_INFO_URL,
    QUESTIONNAIRE_DISPLAY_CATEGORY_URL,
    ARTIFACT_RELEASE_LABEL_URL,
    ARTIFACTASSESSMENT_CONTENT_URL,
    SPECIMEN_REJECT_REASON_URL,
    CONDITION_REVIEWED_URL,
    CQF_LOGIC_DEFINITION_URL,
    OPERATIONOUTCOME_ISSUE_SERVER_URL,
    PATIENT_UNKNOWN_IDENTITY_URL,
    CAREPLAN_ACTIVITY_TITLE_URL,
    ARTIFACT_VERSION_URL,
    VALUESET_SUPPLEMENT_URL,
    ARTIFACT_URL_URL,
    ELEMENTDEFINITION_QUESTION_URL,
    SERVICEREQUEST_ORDER_CALLBACK_PHONE_NUMBER_URL,
    CQF_RECEIVING_ORGANIZATION_URL,
    RESOURCE_INSTANCE_DESCRIPTION_URL,
    ARTIFACT_VERSION_ALGORITHM_URL,
    ELEMENTDEFINITION_BESTPRACTICE_URL,
    PRACTITIONER_ANIMAL_SPECIES_URL,
    WORKFLOW_BARRIER_URL,
    OBSERVATION_FOCUS_CODE_URL,
    OBSERVATION_SECONDARY_FINDING_URL,
    ISO21090_ADXP_DELIVERY_INSTALLATION_TYPE_URL,
    CODESYSTEM_WORKFLOW_STATUS_URL,
    TIMING_EXACT_URL,
    TIMING_UNCERTAIN_DATE_URL,
    STRUCTUREDEFINITION_WG_URL,
    ISO21090_ADXP_BUILDING_NUMBER_SUFFIX_URL,
    CQF_NOT_DONE_VALUE_SET_URL,
    CQF_INPUT_PARAMETERS_URL,
    CQF_DEFAULT_VALUE_URL,
    CQF_IMPROVEMENT_NOTATION_GUIDANCE_URL,
    DATA_ABSENT_REASON_URL,
    RENDERING_STYLE_SENSITIVE_URL,
    QUESTIONNAIRE_BASE_TYPE_URL,
    OBSERVATION_GATEWAY_DEVICE_URL,
    CQF_STRENGTH_OF_RECOMMENDATION_URL,
    CQF_RECEIVING_PERSON_URL,
    ARTIFACT_PUBLISHER_URL,
    STRUCTUREDEFINITION_INTERFACE_URL,
    ISO21090_NULL_FLAVOR_URL,
    QUESTIONNAIRE_REFERENCE_RESOURCE_URL,
    ITEM_WEIGHT_URL,
    ISO21090_UNCERTAINTY_URL,
    CODESYSTEM_REPLACEDBY_URL,
    VALUESET_AUTHORITATIVE_SOURCE_URL,
    ELEMENTDEFINITION_BINDING_NAME_URL,
    PRACTITIONERROLE_PRIMARY_IND_URL,
    ENDPOINT_FHIR_VERSION_URL,
    CQF_SYSTEM_USER_TYPE_URL,
    ISO21090_PREFERRED_URL,
    CQF_ENCOUNTER_TYPE_URL,
    CODING_CONFORMANCE_URL,
    VALUESET_USAGE_URL,
    VALUESET_OTHER_TITLE_URL,
    CONSENT_WITNESS_URL,
    IMPLEMENTATIONGUIDE_SOURCE_FILE_URL,
    ISO21090_AD_USE_URL,
    DOSAGE_CONDITIONS_URL,
    ISO21090_ADXP_PRECINCT_URL,
    PATIENT_CADAVERIC_DONOR_URL,
    CHARACTERISTIC_EXPRESSION_URL,
    WORKFLOW_REASON_URL,
    ARTIFACT_APPROVAL_DATE_URL,
    CODESYSTEM_USAGE_URL,
    ELEMENTDEFINITION_GRAPH_CONSTRAINT_URL,
    ORGANIZATION_PORTAL_URL,
    OBSERVATION_TIME_OFFSET_URL,
    ARTIFACT_TOPIC_URL,
    OPERATIONOUTCOME_ISSUE_LINE_URL,
    WORKFLOW_ADHERES_TO_URL,
    PATIENT_ANIMAL_URL,
    PARAMETERS_DEFINITION_URL,
    ENCOUNTER_ASSOCIATED_ENCOUNTER_URL,
    CAPABILITYSTATEMENT_SEARCH_PARAMETER_COMBINATION_URL,
    SPECIMEN_PROCESSING_TIME_URL,
    CONTACTPOINT_COUNTRY_URL,
    CAPABILITYSTATEMENT_SUPPORTED_SYSTEM_URL,
    ELEMENTDEFINITION_MIN_VALUE_SET_URL,
    FIRST_CREATED_URL,
    CQF_SYSTEM_USER_TASK_CONTEXT_URL,
    BODY_SITE_URL,
    EVENT_EVENT_HISTORY_URL,
    QUESTIONNAIRE_CHOICE_ORIENTATION_URL,
    QUANTITY_TRANSLATION_URL,
    ALLERGYINTOLERANCE_ASSERTED_DATE_URL,
    VALUESET_DEPRECATED_URL,
    CQF_QUALITY_OF_EVIDENCE_URL,
    ISO21090_ADXP_DIRECTION_URL,
    QUESTIONNAIRERESPONSE_SIGNATURE_URL,
    VALUESET_KEY_WORD_URL,
    FLAG_PRIORITY_URL,
    CQF_MODEL_INFO_LABEL_URL,
    TARGET_ELEMENT_URL,
    PROCEDURE_APPROACH_BODY_STRUCTURE_URL,
    ISO21090_ADXP_CENSUS_TRACT_URL,
    CQF_MODEL_INFO_IS_INCLUDED_URL,
    DIAGNOSTIC_REPORT_LOCATION_PERFORMED_URL,
    CQF_MESSAGES_URL,
    STRUCTUREDEFINITION_CODEGEN_SUPER_URL,
    OPERATIONOUTCOME_AUTHORITY_URL,
    PATIENT_CITIZENSHIP_URL,
    VALUESET_WORKFLOW_STATUS_DESCRIPTION_URL,
    CODESYSTEM_USE_MARKDOWN_URL,
    VALUESET_SYSTEM_TITLE_URL,
    QUESTIONNAIRE_USAGE_MODE_URL,
    OPEN_EHR_ADMINISTRATION_URL,
    AUDITEVENT_ENCRYPTED_URL,
    WORKFLOW_COMPLIES_WITH_URL,
    STRUCTUREDEFINITION_TABLE_NAME_URL,
    ARTIFACT_DATE_URL,
    CAPABILITIES_URL,
    REQUEST_STATUS_REASON_URL,
    ARTIFACT_STATUS_URL,
    VALUESET_EXTENSIBLE_URL,
    PROCEDURE_TARGET_BODY_STRUCTURE_URL,
    CAPABILITYSTATEMENT_WEBSOCKET_URL,
    METADATARESOURCE_PUBLISH_DATE_URL,
    CODESYSTEM_CONCEPT_COMMENTS_URL,
    QUESTIONNAIRE_REFERENCE_PROFILE_URL,
    QUESTIONNAIRERESPONSE_ATTESTER_URL,
    CODING_SCTDESCID_URL,
    ENTRY_FORMAT_URL,
    QUESTIONNAIRE_OPTION_PREFIX_URL,
    BIOLOGICALLYDERIVEDPRODUCT_MANIPULATION_URL,
    VALUESET_OTHER_NAME_URL,
    MESSAGEHEADER_RESPONSE_REQUEST_URL,
    ORGANIZATIONAFFILIATION_PRIMARY_IND_URL,
    RESOURCE_INSTANCE_NAME_URL,
    AUDITEVENT_NUMBER_OF_INSTANCES_URL,
    PROCEDURE_INCISION_DATE_TIME_URL,
    ARTIFACT_VERSION_POLICY_URL,
    CODING_PURPOSE_URL,
    PATIENT_INTERPRETER_REQUIRED_URL,
    CONSENT_RESEARCH_STUDY_CONTEXT_URL,
    WORKFLOW_SHALL_COMPLY_WITH_URL,
    STRUCTUREDEFINITION_FMM_SUPPORT_URL,
    MAX_SIZE_URL,
    INDIVIDUAL_RECORDED_SEX_OR_GENDER_URL,
    GOAL_RELATIONSHIP_URL,
    VALUESET_RULES_TEXT_URL,
    EVENT_LOCATION_URL,
    STRUCTUREDEFINITION_APPLICABLE_VERSION_URL,
    CODESYSTEM_MAP_URL,
    QUESTIONNAIRE_SLIDER_STEP_VALUE_URL,
    CQF_PART_OF_URL,
    OPERATIONDEFINITION_PROFILE_URL,
)

from zato.fhir.r4_0_1.extensions.v5_1_0.resources import (
    Account,
    ActivityDefinition,
    ActorDefinition,
    Address,
    AdverseEvent,
    Age,
    AllergyIntolerance,
    Annotation,
    Appointment,
    ArtifactAssessment,
    Attachment,
    AuditEvent,
    Base,
    Basic,
    BiologicallyDerivedProduct,
    Bundle,
    CanonicalResource,
    CapabilityStatement,
    CarePlan,
    CareTeam,
    ChargeItem,
    ChargeItemDefinition,
    Citation,
    ClinicalImpression,
    CodeSystem,
    CodeableConcept,
    Coding,
    Communication,
    CommunicationRequest,
    CompartmentDefinition,
    Composition,
    ConceptMap,
    Condition,
    ConditionDefinition,
    Consent,
    ContactDetail,
    ContactPoint,
    Contract,
    Count,
    Coverage,
    DataRequirement,
    DetectedIssue,
    Device,
    DeviceDefinition,
    DeviceDispense,
    DeviceRequest,
    DeviceUsage,
    DiagnosticReport,
    Distance,
    DocumentReference,
    DomainResource,
    Dosage,
    Duration,
    Element,
    ElementDefinition,
    Encounter,
    Endpoint,
    EnrollmentRequest,
    EnrollmentResponse,
    EpisodeOfCare,
    EventDefinition,
    Evidence,
    EvidenceReport,
    EvidenceVariable,
    ExampleScenario,
    ExplanationOfBenefit,
    Expression,
    ExtendedContactDetail,
    Extension,
    FamilyMemberHistory,
    Flag,
    Goal,
    GraphDefinition,
    Group,
    GuidanceResponse,
    HumanName,
    Identifier,
    ImagingStudy,
    Immunization,
    ImmunizationEvaluation,
    ImmunizationRecommendation,
    ImplementationGuide,
    InventoryReport,
    Invoice,
    Library,
    List,
    Location,
    Measure,
    MeasureReport,
    Medication,
    MedicationAdministration,
    MedicationDispense,
    MedicationRequest,
    MedicationStatement,
    MessageDefinition,
    MessageHeader,
    Meta,
    MetadataResource,
    MolecularSequence,
    Money,
    NamingSystem,
    NutritionIntake,
    NutritionOrder,
    Observation,
    ObservationDefinition,
    OperationDefinition,
    OperationOutcome,
    Organization,
    OrganizationAffiliation,
    ParameterDefinition,
    Parameters,
    Patient,
    PaymentNotice,
    PaymentReconciliation,
    Period,
    Person,
    PlanDefinition,
    Practitioner,
    PractitionerRole,
    Procedure,
    Quantity,
    Questionnaire,
    QuestionnaireResponse,
    Range,
    Ratio,
    Reference,
    RelatedArtifact,
    RelatedPerson,
    RequestOrchestration,
    Requirements,
    ResearchStudy,
    ResearchSubject,
    Resource,
    RiskAssessment,
    SampledData,
    SearchParameter,
    ServiceRequest,
    Signature,
    Specimen,
    SpecimenDefinition,
    StructureDefinition,
    StructureMap,
    Subscription,
    SubscriptionTopic,
    Substance,
    SupplyDelivery,
    SupplyRequest,
    Task,
    TerminologyCapabilities,
    TestScript,
    Timing,
    TriggerDefinition,
    UsageContext,
    ValueSet,
    VisionPrescription,
)


class TestImports:

    def test_account_is_importable(self):
        assert Account is not None

    def test_activitydefinition_is_importable(self):
        assert ActivityDefinition is not None

    def test_actordefinition_is_importable(self):
        assert ActorDefinition is not None

    def test_address_is_importable(self):
        assert Address is not None

    def test_adverseevent_is_importable(self):
        assert AdverseEvent is not None

    def test_age_is_importable(self):
        assert Age is not None

    def test_allergyintolerance_is_importable(self):
        assert AllergyIntolerance is not None

    def test_annotation_is_importable(self):
        assert Annotation is not None

    def test_appointment_is_importable(self):
        assert Appointment is not None

    def test_artifactassessment_is_importable(self):
        assert ArtifactAssessment is not None

    def test_attachment_is_importable(self):
        assert Attachment is not None

    def test_auditevent_is_importable(self):
        assert AuditEvent is not None

    def test_base_is_importable(self):
        assert Base is not None

    def test_basic_is_importable(self):
        assert Basic is not None

    def test_biologicallyderivedproduct_is_importable(self):
        assert BiologicallyDerivedProduct is not None

    def test_bundle_is_importable(self):
        assert Bundle is not None

    def test_canonicalresource_is_importable(self):
        assert CanonicalResource is not None

    def test_capabilitystatement_is_importable(self):
        assert CapabilityStatement is not None

    def test_careplan_is_importable(self):
        assert CarePlan is not None

    def test_careteam_is_importable(self):
        assert CareTeam is not None

    def test_chargeitem_is_importable(self):
        assert ChargeItem is not None

    def test_chargeitemdefinition_is_importable(self):
        assert ChargeItemDefinition is not None

    def test_citation_is_importable(self):
        assert Citation is not None

    def test_clinicalimpression_is_importable(self):
        assert ClinicalImpression is not None

    def test_codesystem_is_importable(self):
        assert CodeSystem is not None

    def test_codeableconcept_is_importable(self):
        assert CodeableConcept is not None

    def test_coding_is_importable(self):
        assert Coding is not None

    def test_communication_is_importable(self):
        assert Communication is not None

    def test_communicationrequest_is_importable(self):
        assert CommunicationRequest is not None

    def test_compartmentdefinition_is_importable(self):
        assert CompartmentDefinition is not None

    def test_composition_is_importable(self):
        assert Composition is not None

    def test_conceptmap_is_importable(self):
        assert ConceptMap is not None

    def test_condition_is_importable(self):
        assert Condition is not None

    def test_conditiondefinition_is_importable(self):
        assert ConditionDefinition is not None

    def test_consent_is_importable(self):
        assert Consent is not None

    def test_contactdetail_is_importable(self):
        assert ContactDetail is not None

    def test_contactpoint_is_importable(self):
        assert ContactPoint is not None

    def test_contract_is_importable(self):
        assert Contract is not None

    def test_count_is_importable(self):
        assert Count is not None

    def test_coverage_is_importable(self):
        assert Coverage is not None

    def test_datarequirement_is_importable(self):
        assert DataRequirement is not None

    def test_detectedissue_is_importable(self):
        assert DetectedIssue is not None

    def test_device_is_importable(self):
        assert Device is not None

    def test_devicedefinition_is_importable(self):
        assert DeviceDefinition is not None

    def test_devicedispense_is_importable(self):
        assert DeviceDispense is not None

    def test_devicerequest_is_importable(self):
        assert DeviceRequest is not None

    def test_deviceusage_is_importable(self):
        assert DeviceUsage is not None

    def test_diagnosticreport_is_importable(self):
        assert DiagnosticReport is not None

    def test_distance_is_importable(self):
        assert Distance is not None

    def test_documentreference_is_importable(self):
        assert DocumentReference is not None

    def test_domainresource_is_importable(self):
        assert DomainResource is not None

    def test_dosage_is_importable(self):
        assert Dosage is not None

    def test_duration_is_importable(self):
        assert Duration is not None

    def test_element_is_importable(self):
        assert Element is not None

    def test_elementdefinition_is_importable(self):
        assert ElementDefinition is not None

    def test_encounter_is_importable(self):
        assert Encounter is not None

    def test_endpoint_is_importable(self):
        assert Endpoint is not None

    def test_enrollmentrequest_is_importable(self):
        assert EnrollmentRequest is not None

    def test_enrollmentresponse_is_importable(self):
        assert EnrollmentResponse is not None

    def test_episodeofcare_is_importable(self):
        assert EpisodeOfCare is not None

    def test_eventdefinition_is_importable(self):
        assert EventDefinition is not None

    def test_evidence_is_importable(self):
        assert Evidence is not None

    def test_evidencereport_is_importable(self):
        assert EvidenceReport is not None

    def test_evidencevariable_is_importable(self):
        assert EvidenceVariable is not None

    def test_examplescenario_is_importable(self):
        assert ExampleScenario is not None

    def test_explanationofbenefit_is_importable(self):
        assert ExplanationOfBenefit is not None

    def test_expression_is_importable(self):
        assert Expression is not None

    def test_extendedcontactdetail_is_importable(self):
        assert ExtendedContactDetail is not None

    def test_extension_is_importable(self):
        assert Extension is not None

    def test_familymemberhistory_is_importable(self):
        assert FamilyMemberHistory is not None

    def test_flag_is_importable(self):
        assert Flag is not None

    def test_goal_is_importable(self):
        assert Goal is not None

    def test_graphdefinition_is_importable(self):
        assert GraphDefinition is not None

    def test_group_is_importable(self):
        assert Group is not None

    def test_guidanceresponse_is_importable(self):
        assert GuidanceResponse is not None

    def test_humanname_is_importable(self):
        assert HumanName is not None

    def test_identifier_is_importable(self):
        assert Identifier is not None

    def test_imagingstudy_is_importable(self):
        assert ImagingStudy is not None

    def test_immunization_is_importable(self):
        assert Immunization is not None

    def test_immunizationevaluation_is_importable(self):
        assert ImmunizationEvaluation is not None

    def test_immunizationrecommendation_is_importable(self):
        assert ImmunizationRecommendation is not None

    def test_implementationguide_is_importable(self):
        assert ImplementationGuide is not None

    def test_inventoryreport_is_importable(self):
        assert InventoryReport is not None

    def test_invoice_is_importable(self):
        assert Invoice is not None

    def test_library_is_importable(self):
        assert Library is not None

    def test_list_is_importable(self):
        assert List is not None

    def test_location_is_importable(self):
        assert Location is not None

    def test_measure_is_importable(self):
        assert Measure is not None

    def test_measurereport_is_importable(self):
        assert MeasureReport is not None

    def test_medication_is_importable(self):
        assert Medication is not None

    def test_medicationadministration_is_importable(self):
        assert MedicationAdministration is not None

    def test_medicationdispense_is_importable(self):
        assert MedicationDispense is not None

    def test_medicationrequest_is_importable(self):
        assert MedicationRequest is not None

    def test_medicationstatement_is_importable(self):
        assert MedicationStatement is not None

    def test_messagedefinition_is_importable(self):
        assert MessageDefinition is not None

    def test_messageheader_is_importable(self):
        assert MessageHeader is not None

    def test_meta_is_importable(self):
        assert Meta is not None

    def test_metadataresource_is_importable(self):
        assert MetadataResource is not None

    def test_molecularsequence_is_importable(self):
        assert MolecularSequence is not None

    def test_money_is_importable(self):
        assert Money is not None

    def test_namingsystem_is_importable(self):
        assert NamingSystem is not None

    def test_nutritionintake_is_importable(self):
        assert NutritionIntake is not None

    def test_nutritionorder_is_importable(self):
        assert NutritionOrder is not None

    def test_observation_is_importable(self):
        assert Observation is not None

    def test_observationdefinition_is_importable(self):
        assert ObservationDefinition is not None

    def test_operationdefinition_is_importable(self):
        assert OperationDefinition is not None

    def test_operationoutcome_is_importable(self):
        assert OperationOutcome is not None

    def test_organization_is_importable(self):
        assert Organization is not None

    def test_organizationaffiliation_is_importable(self):
        assert OrganizationAffiliation is not None

    def test_parameterdefinition_is_importable(self):
        assert ParameterDefinition is not None

    def test_parameters_is_importable(self):
        assert Parameters is not None

    def test_patient_is_importable(self):
        assert Patient is not None

    def test_paymentnotice_is_importable(self):
        assert PaymentNotice is not None

    def test_paymentreconciliation_is_importable(self):
        assert PaymentReconciliation is not None

    def test_period_is_importable(self):
        assert Period is not None

    def test_person_is_importable(self):
        assert Person is not None

    def test_plandefinition_is_importable(self):
        assert PlanDefinition is not None

    def test_practitioner_is_importable(self):
        assert Practitioner is not None

    def test_practitionerrole_is_importable(self):
        assert PractitionerRole is not None

    def test_procedure_is_importable(self):
        assert Procedure is not None

    def test_quantity_is_importable(self):
        assert Quantity is not None

    def test_questionnaire_is_importable(self):
        assert Questionnaire is not None

    def test_questionnaireresponse_is_importable(self):
        assert QuestionnaireResponse is not None

    def test_range_is_importable(self):
        assert Range is not None

    def test_ratio_is_importable(self):
        assert Ratio is not None

    def test_reference_is_importable(self):
        assert Reference is not None

    def test_relatedartifact_is_importable(self):
        assert RelatedArtifact is not None

    def test_relatedperson_is_importable(self):
        assert RelatedPerson is not None

    def test_requestorchestration_is_importable(self):
        assert RequestOrchestration is not None

    def test_requirements_is_importable(self):
        assert Requirements is not None

    def test_researchstudy_is_importable(self):
        assert ResearchStudy is not None

    def test_researchsubject_is_importable(self):
        assert ResearchSubject is not None

    def test_resource_is_importable(self):
        assert Resource is not None

    def test_riskassessment_is_importable(self):
        assert RiskAssessment is not None

    def test_sampleddata_is_importable(self):
        assert SampledData is not None

    def test_searchparameter_is_importable(self):
        assert SearchParameter is not None

    def test_servicerequest_is_importable(self):
        assert ServiceRequest is not None

    def test_signature_is_importable(self):
        assert Signature is not None

    def test_specimen_is_importable(self):
        assert Specimen is not None

    def test_specimendefinition_is_importable(self):
        assert SpecimenDefinition is not None

    def test_structuredefinition_is_importable(self):
        assert StructureDefinition is not None

    def test_structuremap_is_importable(self):
        assert StructureMap is not None

    def test_subscription_is_importable(self):
        assert Subscription is not None

    def test_subscriptiontopic_is_importable(self):
        assert SubscriptionTopic is not None

    def test_substance_is_importable(self):
        assert Substance is not None

    def test_supplydelivery_is_importable(self):
        assert SupplyDelivery is not None

    def test_supplyrequest_is_importable(self):
        assert SupplyRequest is not None

    def test_task_is_importable(self):
        assert Task is not None

    def test_terminologycapabilities_is_importable(self):
        assert TerminologyCapabilities is not None

    def test_testscript_is_importable(self):
        assert TestScript is not None

    def test_timing_is_importable(self):
        assert Timing is not None

    def test_triggerdefinition_is_importable(self):
        assert TriggerDefinition is not None

    def test_usagecontext_is_importable(self):
        assert UsageContext is not None

    def test_valueset_is_importable(self):
        assert ValueSet is not None

    def test_visionprescription_is_importable(self):
        assert VisionPrescription is not None


class TestURLConstants:

    def test_contactpoint_area_url(self):
        assert CONTACTPOINT_AREA_URL == 'http://hl7.org/fhir/StructureDefinition/contactpoint-area'

    def test_structuredefinition_extension_meaning_url(self):
        assert STRUCTUREDEFINITION_EXTENSION_MEANING_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-extension-meaning'

    def test_elementdefinition_bestpractice_explanation_url(self):
        assert ELEMENTDEFINITION_BESTPRACTICE_EXPLANATION_URL == 'http://hl7.org/fhir/StructureDefinition/elementdefinition-bestpractice-explanation'

    def test_iso21090_adxp_post_box_url(self):
        assert ISO21090_ADXP_POST_BOX_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-postBox'

    def test_artifact_editor_url(self):
        assert ARTIFACT_EDITOR_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-editor'

    def test_artifact_cite_as_url(self):
        assert ARTIFACT_CITE_AS_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-citeAs'

    def test_operationoutcome_file_url(self):
        assert OPERATIONOUTCOME_FILE_URL == 'http://hl7.org/fhir/StructureDefinition/operationoutcome-file'

    def test_research_study_study_registration_url(self):
        assert RESEARCH_STUDY_STUDY_REGISTRATION_URL == 'http://hl7.org/fhir/StructureDefinition/researchStudy-studyRegistration'

    def test_measurereport_population_description_url(self):
        assert MEASUREREPORT_POPULATION_DESCRIPTION_URL == 'http://hl7.org/fhir/StructureDefinition/measurereport-populationDescription'

    def test_cqf_criteria_reference_url(self):
        assert CQF_CRITERIA_REFERENCE_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-criteriaReference'

    def test_cqf_calculated_value_url(self):
        assert CQF_CALCULATED_VALUE_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-calculatedValue'

    def test_auditevent_participant_object_contains_study_url(self):
        assert AUDITEVENT_PARTICIPANT_OBJECT_CONTAINS_STUDY_URL == 'http://hl7.org/fhir/StructureDefinition/auditevent-ParticipantObjectContainsStudy'

    def test_structuredefinition_display_hint_url(self):
        assert STRUCTUREDEFINITION_DISPLAY_HINT_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-display-hint'

    def test_parameters_full_url_url(self):
        assert PARAMETERS_FULL_URL_URL == 'http://hl7.org/fhir/StructureDefinition/parameters-fullUrl'

    def test_humanname_mothers_family_url(self):
        assert HUMANNAME_MOTHERS_FAMILY_URL == 'http://hl7.org/fhir/StructureDefinition/humanname-mothers-family'

    def test_elementdefinition_pattern_url(self):
        assert ELEMENTDEFINITION_PATTERN_URL == 'http://hl7.org/fhir/StructureDefinition/elementdefinition-pattern'

    def test_cqf_expression_url(self):
        assert CQF_EXPRESSION_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-expression'

    def test_workflow_triggered_by_url(self):
        assert WORKFLOW_TRIGGERED_BY_URL == 'http://hl7.org/fhir/StructureDefinition/workflow-triggeredBy'

    def test_iso21090_uncertainty_type_url(self):
        assert ISO21090_UNCERTAINTY_TYPE_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-uncertaintyType'

    def test_target_path_url(self):
        assert TARGET_PATH_URL == 'http://hl7.org/fhir/StructureDefinition/targetPath'

    def test_consent_transcriber_url(self):
        assert CONSENT_TRANSCRIBER_URL == 'http://hl7.org/fhir/StructureDefinition/consent-Transcriber'

    def test_extended_contact_availability_url(self):
        assert EXTENDED_CONTACT_AVAILABILITY_URL == 'http://hl7.org/fhir/StructureDefinition/extended-contact-availability'

    def test_devicerequest_patient_instruction_url(self):
        assert DEVICEREQUEST_PATIENT_INSTRUCTION_URL == 'http://hl7.org/fhir/StructureDefinition/devicerequest-patientInstruction'

    def test_iso21090_adxp_street_name_url(self):
        assert ISO21090_ADXP_STREET_NAME_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-streetName'

    def test_narrative_link_url(self):
        assert NARRATIVE_LINK_URL == 'http://hl7.org/fhir/StructureDefinition/narrativeLink'

    def test_uncertain_period_url(self):
        assert UNCERTAIN_PERIOD_URL == 'http://hl7.org/fhir/StructureDefinition/uncertainPeriod'

    def test_artifact_period_duration_url(self):
        assert ARTIFACT_PERIOD_DURATION_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-periodDuration'

    def test_alternate_codes_url(self):
        assert ALTERNATE_CODES_URL == 'http://hl7.org/fhir/StructureDefinition/alternate-codes'

    def test_event_performer_function_url(self):
        assert EVENT_PERFORMER_FUNCTION_URL == 'http://hl7.org/fhir/StructureDefinition/event-performerFunction'

    def test_valueset_unclosed_url(self):
        assert VALUESET_UNCLOSED_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-unclosed'

    def test_allergyintolerance_duration_url(self):
        assert ALLERGYINTOLERANCE_DURATION_URL == 'http://hl7.org/fhir/StructureDefinition/allergyintolerance-duration'

    def test_elementdefinition_type_must_support_url(self):
        assert ELEMENTDEFINITION_TYPE_MUST_SUPPORT_URL == 'http://hl7.org/fhir/StructureDefinition/elementdefinition-type-must-support'

    def test_cqf_artifact_comment_url(self):
        assert CQF_ARTIFACT_COMMENT_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-artifactComment'

    def test_iso21090_adxp_unit_id_url(self):
        assert ISO21090_ADXP_UNIT_ID_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-unitID'

    def test_cqf_library_url(self):
        assert CQF_LIBRARY_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-library'

    def test_elementdefinition_translatable_url(self):
        assert ELEMENTDEFINITION_TRANSLATABLE_URL == 'http://hl7.org/fhir/StructureDefinition/elementdefinition-translatable'

    def test_cqf_is_primary_citation_url(self):
        assert CQF_IS_PRIMARY_CITATION_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-isPrimaryCitation'

    def test_rendering_style_url(self):
        assert RENDERING_STYLE_URL == 'http://hl7.org/fhir/StructureDefinition/rendering-style'

    def test_resolve_as_version_specific_url(self):
        assert RESOLVE_AS_VERSION_SPECIFIC_URL == 'http://hl7.org/fhir/StructureDefinition/resolve-as-version-specific'

    def test_requirements_parent_url(self):
        assert REQUIREMENTS_PARENT_URL == 'http://hl7.org/fhir/StructureDefinition/requirements-parent'

    def test_cqf_knowledge_capability_url(self):
        assert CQF_KNOWLEDGE_CAPABILITY_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-knowledgeCapability'

    def test_min_length_url(self):
        assert MIN_LENGTH_URL == 'http://hl7.org/fhir/StructureDefinition/minLength'

    def test_codesystem_warning_url(self):
        assert CODESYSTEM_WARNING_URL == 'http://hl7.org/fhir/StructureDefinition/codesystem-warning'

    def test_structuredefinition_type_characteristics_url(self):
        assert STRUCTUREDEFINITION_TYPE_CHARACTERISTICS_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-type-characteristics'

    def test_references_contained_url(self):
        assert REFERENCES_CONTAINED_URL == 'http://hl7.org/fhir/StructureDefinition/referencesContained'

    def test_condition_ruled_out_url(self):
        assert CONDITION_RULED_OUT_URL == 'http://hl7.org/fhir/StructureDefinition/condition-ruledOut'

    def test_observation_body_position_url(self):
        assert OBSERVATION_BODY_POSITION_URL == 'http://hl7.org/fhir/StructureDefinition/observation-bodyPosition'

    def test_questionnaire_fhir_type_url(self):
        assert QUESTIONNAIRE_FHIR_TYPE_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-fhirType'

    def test_measurereport_category_url(self):
        assert MEASUREREPORT_CATEGORY_URL == 'http://hl7.org/fhir/StructureDefinition/measurereport-category'

    def test_procedure_progress_status_url(self):
        assert PROCEDURE_PROGRESS_STATUS_URL == 'http://hl7.org/fhir/StructureDefinition/procedure-progressStatus'

    def test_patient_proficiency_url(self):
        assert PATIENT_PROFICIENCY_URL == 'http://hl7.org/fhir/StructureDefinition/patient-proficiency'

    def test_diagnostic_report_focus_url(self):
        assert DIAGNOSTIC_REPORT_FOCUS_URL == 'http://hl7.org/fhir/StructureDefinition/diagnosticReport-focus'

    def test_list_change_base_url(self):
        assert LIST_CHANGE_BASE_URL == 'http://hl7.org/fhir/StructureDefinition/list-changeBase'

    def test_medicationdispense_refills_remaining_url(self):
        assert MEDICATIONDISPENSE_REFILLS_REMAINING_URL == 'http://hl7.org/fhir/StructureDefinition/medicationdispense-refillsRemaining'

    def test_relative_date_url(self):
        assert RELATIVE_DATE_URL == 'http://hl7.org/fhir/StructureDefinition/relative-date'

    def test_address_official_url(self):
        assert ADDRESS_OFFICIAL_URL == 'http://hl7.org/fhir/StructureDefinition/address-official'

    def test_cqf_test_artifact_url(self):
        assert CQF_TEST_ARTIFACT_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-testArtifact'

    def test_patient_sex_parameter_for_clinical_use_url(self):
        assert PATIENT_SEX_PARAMETER_FOR_CLINICAL_USE_URL == 'http://hl7.org/fhir/StructureDefinition/patient-sexParameterForClinicalUse'

    def test_resource_approval_date_url(self):
        assert RESOURCE_APPROVAL_DATE_URL == 'http://hl7.org/fhir/StructureDefinition/resource-approvalDate'

    def test_elementdefinition_conceptmap_url(self):
        assert ELEMENTDEFINITION_CONCEPTMAP_URL == 'http://hl7.org/fhir/StructureDefinition/elementdefinition-conceptmap'

    def test_structuredefinition_complies_with_profile_url(self):
        assert STRUCTUREDEFINITION_COMPLIES_WITH_PROFILE_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-compliesWithProfile'

    def test_cqf_contribution_time_url(self):
        assert CQF_CONTRIBUTION_TIME_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-contributionTime'

    def test_condition_related_url(self):
        assert CONDITION_RELATED_URL == 'http://hl7.org/fhir/StructureDefinition/condition-related'

    def test_cqf_is_selective_url(self):
        assert CQF_IS_SELECTIVE_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-isSelective'

    def test_device_maintenanceresponsibility_url(self):
        assert DEVICE_MAINTENANCERESPONSIBILITY_URL == 'http://hl7.org/fhir/StructureDefinition/device-maintenanceresponsibility'

    def test_condition_disease_course_url(self):
        assert CONDITION_DISEASE_COURSE_URL == 'http://hl7.org/fhir/StructureDefinition/condition-diseaseCourse'

    def test_cqf_citation_url(self):
        assert CQF_CITATION_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-citation'

    def test_artifact_release_description_url(self):
        assert ARTIFACT_RELEASE_DESCRIPTION_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-releaseDescription'

    def test_iso21090_adxp_street_name_base_url(self):
        assert ISO21090_ADXP_STREET_NAME_BASE_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-streetNameBase'

    def test_iso21090_adxp_unit_type_url(self):
        assert ISO21090_ADXP_UNIT_TYPE_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-unitType'

    def test_structuredefinition_category_url(self):
        assert STRUCTUREDEFINITION_CATEGORY_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-category'

    def test_artifact_is_owned_url(self):
        assert ARTIFACT_IS_OWNED_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-isOwned'

    def test_structuredefinition_fmm_url(self):
        assert STRUCTUREDEFINITION_FMM_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-fmm'

    def test_ext_11179_object_class_url(self):
        assert EXT_11179_OBJECT_CLASS_URL == 'http://hl7.org/fhir/StructureDefinition/11179-objectClass'

    def test_humanname_own_prefix_url(self):
        assert HUMANNAME_OWN_PREFIX_URL == 'http://hl7.org/fhir/StructureDefinition/humanname-own-prefix'

    def test_iso21090_adxp_street_name_type_url(self):
        assert ISO21090_ADXP_STREET_NAME_TYPE_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-streetNameType'

    def test_elementdefinition_equivalence_url(self):
        assert ELEMENTDEFINITION_EQUIVALENCE_URL == 'http://hl7.org/fhir/StructureDefinition/elementdefinition-equivalence'

    def test_encounter_mode_of_arrival_url(self):
        assert ENCOUNTER_MODE_OF_ARRIVAL_URL == 'http://hl7.org/fhir/StructureDefinition/encounter-modeOfArrival'

    def test_procedure_directed_by_url(self):
        assert PROCEDURE_DIRECTED_BY_URL == 'http://hl7.org/fhir/StructureDefinition/procedure-directedBy'

    def test_cqf_cql_access_modifier_url(self):
        assert CQF_CQL_ACCESS_MODIFIER_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-cqlAccessModifier'

    def test_artifact_experimental_url(self):
        assert ARTIFACT_EXPERIMENTAL_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-experimental'

    def test_cqf_model_info_settings_url(self):
        assert CQF_MODEL_INFO_SETTINGS_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-modelInfoSettings'

    def test_family_member_history_genetics_parent_url(self):
        assert FAMILY_MEMBER_HISTORY_GENETICS_PARENT_URL == 'http://hl7.org/fhir/StructureDefinition/family-member-history-genetics-parent'

    def test_questionnaire_constraint_url(self):
        assert QUESTIONNAIRE_CONSTRAINT_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-constraint'

    def test_valueset_compose_created_by_url(self):
        assert VALUESET_COMPOSE_CREATED_BY_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-compose-createdBy'

    def test_cqf_target_invariant_url(self):
        assert CQF_TARGET_INVARIANT_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-targetInvariant'

    def test_structuredefinition_fhir_type_url(self):
        assert STRUCTUREDEFINITION_FHIR_TYPE_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-fhir-type'

    def test_version_specific_use_url(self):
        assert VERSION_SPECIFIC_USE_URL == 'http://hl7.org/fhir/StructureDefinition/version-specific-use'

    def test_elementdefinition_profile_element_url(self):
        assert ELEMENTDEFINITION_PROFILE_ELEMENT_URL == 'http://hl7.org/fhir/StructureDefinition/elementdefinition-profile-element'

    def test_codesystem_alternate_url(self):
        assert CODESYSTEM_ALTERNATE_URL == 'http://hl7.org/fhir/StructureDefinition/codesystem-alternate'

    def test_auditevent_mpps_url(self):
        assert AUDITEVENT_MPPS_URL == 'http://hl7.org/fhir/StructureDefinition/auditevent-MPPS'

    def test_cqf_model_info_primary_code_path_url(self):
        assert CQF_MODEL_INFO_PRIMARY_CODE_PATH_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-modelInfo-primaryCodePath'

    def test_patient_multiple_birth_total_url(self):
        assert PATIENT_MULTIPLE_BIRTH_TOTAL_URL == 'http://hl7.org/fhir/StructureDefinition/patient-multipleBirthTotal'

    def test_rendering_markdown_url(self):
        assert RENDERING_MARKDOWN_URL == 'http://hl7.org/fhir/StructureDefinition/rendering-markdown'

    def test_cqf_publication_status_url(self):
        assert CQF_PUBLICATION_STATUS_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-publicationStatus'

    def test_questionnaireresponse_reason_url(self):
        assert QUESTIONNAIRERESPONSE_REASON_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaireresponse-reason'

    def test_observation_specimen_code_url(self):
        assert OBSERVATION_SPECIMEN_CODE_URL == 'http://hl7.org/fhir/StructureDefinition/observation-specimenCode'

    def test_confidential_url(self):
        assert CONFIDENTIAL_URL == 'http://hl7.org/fhir/StructureDefinition/confidential'

    def test_questionnaire_reference_filter_url(self):
        assert QUESTIONNAIRE_REFERENCE_FILTER_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-referenceFilter'

    def test_open_ehr_exposure_description_url(self):
        assert OPEN_EHR_EXPOSURE_DESCRIPTION_URL == 'http://hl7.org/fhir/StructureDefinition/openEHR-exposureDescription'

    def test_artifactassessment_disposition_url(self):
        assert ARTIFACTASSESSMENT_DISPOSITION_URL == 'http://hl7.org/fhir/StructureDefinition/artifactassessment-disposition'

    def test_open_ehr_careplan_url(self):
        assert OPEN_EHR_CAREPLAN_URL == 'http://hl7.org/fhir/StructureDefinition/openEHR-careplan'

    def test_auditevent_lifecycle_url(self):
        assert AUDITEVENT_LIFECYCLE_URL == 'http://hl7.org/fhir/StructureDefinition/auditevent-Lifecycle'

    def test_familymemberhistory_patient_record_url(self):
        assert FAMILYMEMBERHISTORY_PATIENT_RECORD_URL == 'http://hl7.org/fhir/StructureDefinition/familymemberhistory-patient-record'

    def test_auditevent_anonymized_url(self):
        assert AUDITEVENT_ANONYMIZED_URL == 'http://hl7.org/fhir/StructureDefinition/auditevent-Anonymized'

    def test_observation_nature_of_abnormal_test_url(self):
        assert OBSERVATION_NATURE_OF_ABNORMAL_TEST_URL == 'http://hl7.org/fhir/StructureDefinition/observation-nature-of-abnormal-test'

    def test_elementdefinition_selector_url(self):
        assert ELEMENTDEFINITION_SELECTOR_URL == 'http://hl7.org/fhir/StructureDefinition/elementdefinition-selector'

    def test_satisfies_requirement_url(self):
        assert SATISFIES_REQUIREMENT_URL == 'http://hl7.org/fhir/StructureDefinition/satisfies-requirement'

    def test_procedure_caused_by_url(self):
        assert PROCEDURE_CAUSED_BY_URL == 'http://hl7.org/fhir/StructureDefinition/procedure-causedBy'

    def test_patient_importance_url(self):
        assert PATIENT_IMPORTANCE_URL == 'http://hl7.org/fhir/StructureDefinition/patient-importance'

    def test_max_value_url(self):
        assert MAX_VALUE_URL == 'http://hl7.org/fhir/StructureDefinition/maxValue'

    def test_timing_day_of_month_url(self):
        assert TIMING_DAY_OF_MONTH_URL == 'http://hl7.org/fhir/StructureDefinition/timing-dayOfMonth'

    def test_alternate_canonical_url(self):
        assert ALTERNATE_CANONICAL_URL == 'http://hl7.org/fhir/StructureDefinition/alternate-canonical'

    def test_contactpoint_local_url(self):
        assert CONTACTPOINT_LOCAL_URL == 'http://hl7.org/fhir/StructureDefinition/contactpoint-local'

    def test_resource_pertains_to_goal_url(self):
        assert RESOURCE_PERTAINS_TO_GOAL_URL == 'http://hl7.org/fhir/StructureDefinition/resource-pertainsToGoal'

    def test_structuredefinition_security_category_url(self):
        assert STRUCTUREDEFINITION_SECURITY_CATEGORY_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-security-category'

    def test_patient_congregation_url(self):
        assert PATIENT_CONGREGATION_URL == 'http://hl7.org/fhir/StructureDefinition/patient-congregation'

    def test_codesystem_history_url(self):
        assert CODESYSTEM_HISTORY_URL == 'http://hl7.org/fhir/StructureDefinition/codesystem-history'

    def test_questionnaire_signature_required_url(self):
        assert QUESTIONNAIRE_SIGNATURE_REQUIRED_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-signatureRequired'

    def test_artifact_uri_reference_url(self):
        assert ARTIFACT_URI_REFERENCE_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-uriReference'

    def test_iso21090_adxp_additional_locator_url(self):
        assert ISO21090_ADXP_ADDITIONAL_LOCATOR_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-additionalLocator'

    def test_patient_disability_url(self):
        assert PATIENT_DISABILITY_URL == 'http://hl7.org/fhir/StructureDefinition/patient-disability'

    def test_last_source_sync_url(self):
        assert LAST_SOURCE_SYNC_URL == 'http://hl7.org/fhir/StructureDefinition/lastSourceSync'

    def test_structuredefinition_ancestor_url(self):
        assert STRUCTUREDEFINITION_ANCESTOR_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-ancestor'

    def test_observation_analysis_date_time_url(self):
        assert OBSERVATION_ANALYSIS_DATE_TIME_URL == 'http://hl7.org/fhir/StructureDefinition/observation-analysis-date-time'

    def test_artifact_contact_detail_reference_url(self):
        assert ARTIFACT_CONTACT_DETAIL_REFERENCE_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-contactDetailReference'

    def test_elementdefinition_max_value_set_url(self):
        assert ELEMENTDEFINITION_MAX_VALUE_SET_URL == 'http://hl7.org/fhir/StructureDefinition/elementdefinition-maxValueSet'

    def test_iso21090_en_representation_url(self):
        assert ISO21090_EN_REPRESENTATION_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-EN-representation'

    def test_citation_society_affiliation_url(self):
        assert CITATION_SOCIETY_AFFILIATION_URL == 'http://hl7.org/fhir/StructureDefinition/citation-societyAffiliation'

    def test_specimen_sequence_number_url(self):
        assert SPECIMEN_SEQUENCE_NUMBER_URL == 'http://hl7.org/fhir/StructureDefinition/specimen-sequenceNumber'

    def test_observation_reagent_url(self):
        assert OBSERVATION_REAGENT_URL == 'http://hl7.org/fhir/StructureDefinition/observation-reagent'

    def test_device_lastmaintenancetime_url(self):
        assert DEVICE_LASTMAINTENANCETIME_URL == 'http://hl7.org/fhir/StructureDefinition/device-lastmaintenancetime'

    def test_questionnaire_derivation_type_url(self):
        assert QUESTIONNAIRE_DERIVATION_TYPE_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-derivationType'

    def test_language_url(self):
        assert LANGUAGE_URL == 'http://hl7.org/fhir/StructureDefinition/language'

    def test_structuredefinition_standards_status_reason_url(self):
        assert STRUCTUREDEFINITION_STANDARDS_STATUS_REASON_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-standards-status-reason'

    def test_measurereport_count_quantity_url(self):
        assert MEASUREREPORT_COUNT_QUANTITY_URL == 'http://hl7.org/fhir/StructureDefinition/measurereport-countQuantity'

    def test_max_decimal_places_url(self):
        assert MAX_DECIMAL_PLACES_URL == 'http://hl7.org/fhir/StructureDefinition/maxDecimalPlaces'

    def test_timing_days_of_cycle_url(self):
        assert TIMING_DAYS_OF_CYCLE_URL == 'http://hl7.org/fhir/StructureDefinition/timing-daysOfCycle'

    def test_additional_identifier_url(self):
        assert ADDITIONAL_IDENTIFIER_URL == 'http://hl7.org/fhir/StructureDefinition/additionalIdentifier'

    def test_device_implant_status_url(self):
        assert DEVICE_IMPLANT_STATUS_URL == 'http://hl7.org/fhir/StructureDefinition/device-implantStatus'

    def test_artifact_description_url(self):
        assert ARTIFACT_DESCRIPTION_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-description'

    def test_terminology_resource_identifier_metadata_url(self):
        assert TERMINOLOGY_RESOURCE_IDENTIFIER_METADATA_URL == 'http://hl7.org/fhir/StructureDefinition/terminology-resource-identifier-metadata'

    def test_cqf_scope_url(self):
        assert CQF_SCOPE_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-scope'

    def test_open_ehr_location_url(self):
        assert OPEN_EHR_LOCATION_URL == 'http://hl7.org/fhir/StructureDefinition/openEHR-location'

    def test_codesystem_properties_mode_url(self):
        assert CODESYSTEM_PROPERTIES_MODE_URL == 'http://hl7.org/fhir/StructureDefinition/codesystem-properties-mode'

    def test_workflow_research_study_url(self):
        assert WORKFLOW_RESEARCH_STUDY_URL == 'http://hl7.org/fhir/StructureDefinition/workflow-researchStudy'

    def test_cqf_is_empty_list_url(self):
        assert CQF_IS_EMPTY_LIST_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-isEmptyList'

    def test_allergyintolerance_substance_exposure_risk_url(self):
        assert ALLERGYINTOLERANCE_SUBSTANCE_EXPOSURE_RISK_URL == 'http://hl7.org/fhir/StructureDefinition/allergyintolerance-substanceExposureRisk'

    def test_geolocation_url(self):
        assert GEOLOCATION_URL == 'http://hl7.org/fhir/StructureDefinition/geolocation'

    def test_operationoutcome_issue_source_url(self):
        assert OPERATIONOUTCOME_ISSUE_SOURCE_URL == 'http://hl7.org/fhir/StructureDefinition/operationoutcome-issue-source'

    def test_workflow_generated_from_url(self):
        assert WORKFLOW_GENERATED_FROM_URL == 'http://hl7.org/fhir/StructureDefinition/workflow-generatedFrom'

    def test_iso21090_tel_address_url(self):
        assert ISO21090_TEL_ADDRESS_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-TEL-address'

    def test_cqf_cds_hooks_endpoint_url(self):
        assert CQF_CDS_HOOKS_ENDPOINT_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-cdsHooksEndpoint'

    def test_alternate_reference_url(self):
        assert ALTERNATE_REFERENCE_URL == 'http://hl7.org/fhir/StructureDefinition/alternate-reference'

    def test_questionnaire_unit_url(self):
        assert QUESTIONNAIRE_UNIT_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-unit'

    def test_condition_due_to_url(self):
        assert CONDITION_DUE_TO_URL == 'http://hl7.org/fhir/StructureDefinition/condition-dueTo'

    def test_rendered_value_url(self):
        assert RENDERED_VALUE_URL == 'http://hl7.org/fhir/StructureDefinition/rendered-value'

    def test_goal_acceptance_url(self):
        assert GOAL_ACCEPTANCE_URL == 'http://hl7.org/fhir/StructureDefinition/goal-acceptance'

    def test_request_insurance_url(self):
        assert REQUEST_INSURANCE_URL == 'http://hl7.org/fhir/StructureDefinition/request-insurance'

    def test_composition_section_subject_url(self):
        assert COMPOSITION_SECTION_SUBJECT_URL == 'http://hl7.org/fhir/StructureDefinition/composition-section-subject'

    def test_identifier_check_digit_url(self):
        assert IDENTIFIER_CHECK_DIGIT_URL == 'http://hl7.org/fhir/StructureDefinition/identifier-checkDigit'

    def test_patient_mothers_maiden_name_url(self):
        assert PATIENT_MOTHERS_MAIDEN_NAME_URL == 'http://hl7.org/fhir/StructureDefinition/patient-mothersMaidenName'

    def test_artifact_title_url(self):
        assert ARTIFACT_TITLE_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-title'

    def test_cqf_measure_info_url(self):
        assert CQF_MEASURE_INFO_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-measureInfo'

    def test_tz_offset_url(self):
        assert TZ_OFFSET_URL == 'http://hl7.org/fhir/StructureDefinition/tz-offset'

    def test_questionnaire_min_occurs_url(self):
        assert QUESTIONNAIRE_MIN_OCCURS_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-minOccurs'

    def test_humanname_assembly_order_url(self):
        assert HUMANNAME_ASSEMBLY_ORDER_URL == 'http://hl7.org/fhir/StructureDefinition/humanname-assembly-order'

    def test_codesystem_trusted_expansion_url(self):
        assert CODESYSTEM_TRUSTED_EXPANSION_URL == 'http://hl7.org/fhir/StructureDefinition/codesystem-trusted-expansion'

    def test_structuredefinition_inheritance_control_url(self):
        assert STRUCTUREDEFINITION_INHERITANCE_CONTROL_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-inheritance-control'

    def test_patient_contact_priority_url(self):
        assert PATIENT_CONTACT_PRIORITY_URL == 'http://hl7.org/fhir/StructureDefinition/patient-contactPriority'

    def test_humanname_partner_prefix_url(self):
        assert HUMANNAME_PARTNER_PREFIX_URL == 'http://hl7.org/fhir/StructureDefinition/humanname-partner-prefix'

    def test_cqf_contact_reference_url(self):
        assert CQF_CONTACT_REFERENCE_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-contactReference'

    def test_contactpoint_purpose_url(self):
        assert CONTACTPOINT_PURPOSE_URL == 'http://hl7.org/fhir/StructureDefinition/contactpoint-purpose'

    def test_cqf_initial_value_url(self):
        assert CQF_INITIAL_VALUE_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-initialValue'

    def test_organization_preferred_contact_url(self):
        assert ORGANIZATION_PREFERRED_CONTACT_URL == 'http://hl7.org/fhir/StructureDefinition/organization-preferredContact'

    def test_patient_birth_place_url(self):
        assert PATIENT_BIRTH_PLACE_URL == 'http://hl7.org/fhir/StructureDefinition/patient-birthPlace'

    def test_iso21090_adxp_house_number_url(self):
        assert ISO21090_ADXP_HOUSE_NUMBER_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-houseNumber'

    def test_cqf_resource_type_url(self):
        assert CQF_RESOURCE_TYPE_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-resourceType'

    def test_derivation_reference_url(self):
        assert DERIVATION_REFERENCE_URL == 'http://hl7.org/fhir/StructureDefinition/derivation-reference'

    def test_flag_detail_url(self):
        assert FLAG_DETAIL_URL == 'http://hl7.org/fhir/StructureDefinition/flag-detail'

    def test_questionnaire_hidden_url(self):
        assert QUESTIONNAIRE_HIDDEN_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-hidden'

    def test_no_fixed_address_url(self):
        assert NO_FIXED_ADDRESS_URL == 'http://hl7.org/fhir/StructureDefinition/no-fixed-address'

    def test_elementdefinition_is_common_binding_url(self):
        assert ELEMENTDEFINITION_IS_COMMON_BINDING_URL == 'http://hl7.org/fhir/StructureDefinition/elementdefinition-isCommonBinding'

    def test_servicerequest_precondition_url(self):
        assert SERVICEREQUEST_PRECONDITION_URL == 'http://hl7.org/fhir/StructureDefinition/servicerequest-precondition'

    def test_allergyintolerance_abatement_url(self):
        assert ALLERGYINTOLERANCE_ABATEMENT_URL == 'http://hl7.org/fhir/StructureDefinition/allergyintolerance-abatement'

    def test_target_constraint_url(self):
        assert TARGET_CONSTRAINT_URL == 'http://hl7.org/fhir/StructureDefinition/targetConstraint'

    def test_cqf_should_trace_dependency_url(self):
        assert CQF_SHOULD_TRACE_DEPENDENCY_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-shouldTraceDependency'

    def test_artifact_contact_url(self):
        assert ARTIFACT_CONTACT_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-contact'

    def test_allergyintolerance_reason_refuted_url(self):
        assert ALLERGYINTOLERANCE_REASON_REFUTED_URL == 'http://hl7.org/fhir/StructureDefinition/allergyintolerance-reasonRefuted'

    def test_questionnaireresponse_reviewer_url(self):
        assert QUESTIONNAIRERESPONSE_REVIEWER_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaireresponse-reviewer'

    def test_cqf_fhir_query_pattern_url(self):
        assert CQF_FHIR_QUERY_PATTERN_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-fhirQueryPattern'

    def test_elementdefinition_defaulttype_url(self):
        assert ELEMENTDEFINITION_DEFAULTTYPE_URL == 'http://hl7.org/fhir/StructureDefinition/elementdefinition-defaulttype'

    def test_medicationdispense_quantity_remaining_url(self):
        assert MEDICATIONDISPENSE_QUANTITY_REMAINING_URL == 'http://hl7.org/fhir/StructureDefinition/medicationdispense-quantityRemaining'

    def test_contactpoint_extension_url(self):
        assert CONTACTPOINT_EXTENSION_URL == 'http://hl7.org/fhir/StructureDefinition/contactpoint-extension'

    def test_device_commercial_brand_url(self):
        assert DEVICE_COMMERCIAL_BRAND_URL == 'http://hl7.org/fhir/StructureDefinition/device-commercialBrand'

    def test_request_do_not_perform_url(self):
        assert REQUEST_DO_NOT_PERFORM_URL == 'http://hl7.org/fhir/StructureDefinition/request-doNotPerform'

    def test_request_replaces_url(self):
        assert REQUEST_REPLACES_URL == 'http://hl7.org/fhir/StructureDefinition/request-replaces'

    def test_cqf_initiating_organization_url(self):
        assert CQF_INITIATING_ORGANIZATION_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-initiatingOrganization'

    def test_auditevent_instance_url(self):
        assert AUDITEVENT_INSTANCE_URL == 'http://hl7.org/fhir/StructureDefinition/auditevent-Instance'

    def test_auditevent_accession_url(self):
        assert AUDITEVENT_ACCESSION_URL == 'http://hl7.org/fhir/StructureDefinition/auditevent-Accession'

    def test_patient_preference_type_url(self):
        assert PATIENT_PREFERENCE_TYPE_URL == 'http://hl7.org/fhir/StructureDefinition/patient-preferenceType'

    def test_observation_replaces_url(self):
        assert OBSERVATION_REPLACES_URL == 'http://hl7.org/fhir/StructureDefinition/observation-replaces'

    def test_artifact_last_review_date_url(self):
        assert ARTIFACT_LAST_REVIEW_DATE_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-lastReviewDate'

    def test_codesystem_other_name_url(self):
        assert CODESYSTEM_OTHER_NAME_URL == 'http://hl7.org/fhir/StructureDefinition/codesystem-otherName'

    def test_questionnaire_unit_option_url(self):
        assert QUESTIONNAIRE_UNIT_OPTION_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-unitOption'

    def test_documentreference_sourcepatient_url(self):
        assert DOCUMENTREFERENCE_SOURCEPATIENT_URL == 'http://hl7.org/fhir/StructureDefinition/documentreference-sourcepatient'

    def test_cqf_initiating_person_url(self):
        assert CQF_INITIATING_PERSON_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-initiatingPerson'

    def test_capabilitystatement_search_mode_url(self):
        assert CAPABILITYSTATEMENT_SEARCH_MODE_URL == 'http://hl7.org/fhir/StructureDefinition/capabilitystatement-search-mode'

    def test_organization_brand_url(self):
        assert ORGANIZATION_BRAND_URL == 'http://hl7.org/fhir/StructureDefinition/organization-brand'

    def test_observation_v2_subid_url(self):
        assert OBSERVATION_V2_SUBID_URL == 'http://hl7.org/fhir/StructureDefinition/observation-v2-subid'

    def test_valueset_concept_order_url(self):
        assert VALUESET_CONCEPT_ORDER_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-conceptOrder'

    def test_artifact_author_url(self):
        assert ARTIFACT_AUTHOR_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-author'

    def test_research_study_site_recruitment_url(self):
        assert RESEARCH_STUDY_SITE_RECRUITMENT_URL == 'http://hl7.org/fhir/StructureDefinition/researchStudy-siteRecruitment'

    def test_cqf_parameter_definition_url(self):
        assert CQF_PARAMETER_DEFINITION_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-parameterDefinition'

    def test_valueset_label_url(self):
        assert VALUESET_LABEL_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-label'

    def test_family_member_history_genetics_sibling_url(self):
        assert FAMILY_MEMBER_HISTORY_GENETICS_SIBLING_URL == 'http://hl7.org/fhir/StructureDefinition/family-member-history-genetics-sibling'

    def test_http_response_header_url(self):
        assert HTTP_RESPONSE_HEADER_URL == 'http://hl7.org/fhir/StructureDefinition/http-response-header'

    def test_artifact_copyright_label_url(self):
        assert ARTIFACT_COPYRIGHT_LABEL_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-copyrightLabel'

    def test_careteam_alias_url(self):
        assert CARETEAM_ALIAS_URL == 'http://hl7.org/fhir/StructureDefinition/careteam-alias'

    def test_identifier_valid_date_url(self):
        assert IDENTIFIER_VALID_DATE_URL == 'http://hl7.org/fhir/StructureDefinition/identifier-validDate'

    def test_composition_clinicaldocument_version_number_url(self):
        assert COMPOSITION_CLINICALDOCUMENT_VERSION_NUMBER_URL == 'http://hl7.org/fhir/StructureDefinition/composition-clinicaldocument-versionNumber'

    def test_goal_reason_rejected_url(self):
        assert GOAL_REASON_REJECTED_URL == 'http://hl7.org/fhir/StructureDefinition/goal-reasonRejected'

    def test_ext_11179_permitted_value_valueset_url(self):
        assert EXT_11179_PERMITTED_VALUE_VALUESET_URL == 'http://hl7.org/fhir/StructureDefinition/11179-permitted-value-valueset'

    def test_artifact_identifier_url(self):
        assert ARTIFACT_IDENTIFIER_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-identifier'

    def test_resource_last_review_date_url(self):
        assert RESOURCE_LAST_REVIEW_DATE_URL == 'http://hl7.org/fhir/StructureDefinition/resource-lastReviewDate'

    def test_artifactassessment_workflow_status_url(self):
        assert ARTIFACTASSESSMENT_WORKFLOW_STATUS_URL == 'http://hl7.org/fhir/StructureDefinition/artifactassessment-workflowStatus'

    def test_observation_device_code_url(self):
        assert OBSERVATION_DEVICE_CODE_URL == 'http://hl7.org/fhir/StructureDefinition/observation-deviceCode'

    def test_valueset_toocostly_url(self):
        assert VALUESET_TOOCOSTLY_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-toocostly'

    def test_patient_religion_url(self):
        assert PATIENT_RELIGION_URL == 'http://hl7.org/fhir/StructureDefinition/patient-religion'

    def test_artifact_effective_period_url(self):
        assert ARTIFACT_EFFECTIVE_PERIOD_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-effectivePeriod'

    def test_statistic_model_include_if_url(self):
        assert STATISTIC_MODEL_INCLUDE_IF_URL == 'http://hl7.org/fhir/StructureDefinition/statistic-model-include-if'

    def test_diagnostic_report_risk_url(self):
        assert DIAGNOSTIC_REPORT_RISK_URL == 'http://hl7.org/fhir/StructureDefinition/diagnosticReport-risk'

    def test_elementdefinition_allowed_units_url(self):
        assert ELEMENTDEFINITION_ALLOWED_UNITS_URL == 'http://hl7.org/fhir/StructureDefinition/elementdefinition-allowedUnits'

    def test_artifact_copyright_url(self):
        assert ARTIFACT_COPYRIGHT_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-copyright'

    def test_cqf_expansion_parameters_url(self):
        assert CQF_EXPANSION_PARAMETERS_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-expansionParameters'

    def test_codesystem_authoritative_source_url(self):
        assert CODESYSTEM_AUTHORITATIVE_SOURCE_URL == 'http://hl7.org/fhir/StructureDefinition/codesystem-authoritativeSource'

    def test_open_ehr_exposure_duration_url(self):
        assert OPEN_EHR_EXPOSURE_DURATION_URL == 'http://hl7.org/fhir/StructureDefinition/openEHR-exposureDuration'

    def test__datatype_url(self):
        assert _DATATYPE_URL == 'http://hl7.org/fhir/StructureDefinition/_datatype'

    def test_iso21090_adxp_delivery_mode_identifier_url(self):
        assert ISO21090_ADXP_DELIVERY_MODE_IDENTIFIER_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-deliveryModeIdentifier'

    def test_cqf_publication_date_url(self):
        assert CQF_PUBLICATION_DATE_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-publicationDate'

    def test_valueset_map_url(self):
        assert VALUESET_MAP_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-map'

    def test_questionnaireresponse_author_url(self):
        assert QUESTIONNAIRERESPONSE_AUTHOR_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaireresponse-author'

    def test_iso21090_en_qualifier_url(self):
        assert ISO21090_EN_QUALIFIER_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-EN-qualifier'

    def test_valueset_system_ref_url(self):
        assert VALUESET_SYSTEM_REF_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-systemRef'

    def test_operationoutcome_detected_issue_url(self):
        assert OPERATIONOUTCOME_DETECTED_ISSUE_URL == 'http://hl7.org/fhir/StructureDefinition/operationoutcome-detectedIssue'

    def test_biologicallyderivedproduct_collection_procedure_url(self):
        assert BIOLOGICALLYDERIVEDPRODUCT_COLLECTION_PROCEDURE_URL == 'http://hl7.org/fhir/StructureDefinition/biologicallyderivedproduct-collection-procedure'

    def test_cqf_certainty_url(self):
        assert CQF_CERTAINTY_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-certainty'

    def test_diagnostic_report_extends_url(self):
        assert DIAGNOSTIC_REPORT_EXTENDS_URL == 'http://hl7.org/fhir/StructureDefinition/diagnosticReport-extends'

    def test_cqf_value_filter_url(self):
        assert CQF_VALUE_FILTER_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-valueFilter'

    def test_subscription_best_effort_url(self):
        assert SUBSCRIPTION_BEST_EFFORT_URL == 'http://hl7.org/fhir/StructureDefinition/subscription-best-effort'

    def test_questionnaire_unit_value_set_url(self):
        assert QUESTIONNAIRE_UNIT_VALUE_SET_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-unitValueSet'

    def test_rendering_xhtml_url(self):
        assert RENDERING_XHTML_URL == 'http://hl7.org/fhir/StructureDefinition/rendering-xhtml'

    def test_condition_occurred_following_url(self):
        assert CONDITION_OCCURRED_FOLLOWING_URL == 'http://hl7.org/fhir/StructureDefinition/condition-occurredFollowing'

    def test_cqf_system_user_language_url(self):
        assert CQF_SYSTEM_USER_LANGUAGE_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-systemUserLanguage'

    def test_observation_sequel_to_url(self):
        assert OBSERVATION_SEQUEL_TO_URL == 'http://hl7.org/fhir/StructureDefinition/observation-sequelTo'

    def test_patient_related_person_url(self):
        assert PATIENT_RELATED_PERSON_URL == 'http://hl7.org/fhir/StructureDefinition/patient-relatedPerson'

    def test_humanname_own_name_url(self):
        assert HUMANNAME_OWN_NAME_URL == 'http://hl7.org/fhir/StructureDefinition/humanname-own-name'

    def test_diagnostic_report_summary_of_url(self):
        assert DIAGNOSTIC_REPORT_SUMMARY_OF_URL == 'http://hl7.org/fhir/StructureDefinition/diagnosticReport-summaryOf'

    def test_valueset_special_status_url(self):
        assert VALUESET_SPECIAL_STATUS_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-special-status'

    def test_operationoutcome_issue_col_url(self):
        assert OPERATIONOUTCOME_ISSUE_COL_URL == 'http://hl7.org/fhir/StructureDefinition/operationoutcome-issue-col'

    def test_auditevent_on_behalf_of_url(self):
        assert AUDITEVENT_ON_BEHALF_OF_URL == 'http://hl7.org/fhir/StructureDefinition/auditevent-OnBehalfOf'

    def test_individual_pronouns_url(self):
        assert INDIVIDUAL_PRONOUNS_URL == 'http://hl7.org/fhir/StructureDefinition/individual-pronouns'

    def test_structuredefinition_fmm_no_warnings_url(self):
        assert STRUCTUREDEFINITION_FMM_NO_WARNINGS_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-fmm-no-warnings'

    def test_capabilitystatement_search_parameter_use_url(self):
        assert CAPABILITYSTATEMENT_SEARCH_PARAMETER_USE_URL == 'http://hl7.org/fhir/StructureDefinition/capabilitystatement-search-parameter-use'

    def test_translation_url(self):
        assert TRANSLATION_URL == 'http://hl7.org/fhir/StructureDefinition/translation'

    def test_workflow_protective_factor_url(self):
        assert WORKFLOW_PROTECTIVE_FACTOR_URL == 'http://hl7.org/fhir/StructureDefinition/workflow-protectiveFactor'

    def test_valueset_compose_creation_date_url(self):
        assert VALUESET_COMPOSE_CREATION_DATE_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-compose-creationDate'

    def test_location_communication_url(self):
        assert LOCATION_COMMUNICATION_URL == 'http://hl7.org/fhir/StructureDefinition/location-communication'

    def test_patient_known_non_duplicate_url(self):
        assert PATIENT_KNOWN_NON_DUPLICATE_URL == 'http://hl7.org/fhir/StructureDefinition/patient-knownNonDuplicate'

    def test_elementdefinition_suppress_url(self):
        assert ELEMENTDEFINITION_SUPPRESS_URL == 'http://hl7.org/fhir/StructureDefinition/elementdefinition-suppress'

    def test_oauth_uris_url(self):
        assert OAUTH_URIS_URL == 'http://fhir-registry.smarthealthit.org/StructureDefinition/oauth-uris'

    def test_large_value_url(self):
        assert LARGE_VALUE_URL == 'http://hl7.org/fhir/StructureDefinition/largeValue'

    def test_questionnaireresponse_completion_mode_url(self):
        assert QUESTIONNAIRERESPONSE_COMPLETION_MODE_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaireresponse-completionMode'

    def test_capabilitystatement_expectation_url(self):
        assert CAPABILITYSTATEMENT_EXPECTATION_URL == 'http://hl7.org/fhir/StructureDefinition/capabilitystatement-expectation'

    def test_artifact_purpose_url(self):
        assert ARTIFACT_PURPOSE_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-purpose'

    def test_familymemberhistory_type_url(self):
        assert FAMILYMEMBERHISTORY_TYPE_URL == 'http://hl7.org/fhir/StructureDefinition/familymemberhistory-type'

    def test_structuredefinition_standards_status_url(self):
        assert STRUCTUREDEFINITION_STANDARDS_STATUS_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-standards-status'

    def test_location_distance_url(self):
        assert LOCATION_DISTANCE_URL == 'http://hl7.org/fhir/StructureDefinition/location-distance'

    def test_diagnostic_report_workflow_status_url(self):
        assert DIAGNOSTIC_REPORT_WORKFLOW_STATUS_URL == 'http://hl7.org/fhir/StructureDefinition/diagnosticReport-workflowStatus'

    def test_capabilitystatement_declared_profile_url(self):
        assert CAPABILITYSTATEMENT_DECLARED_PROFILE_URL == 'http://hl7.org/fhir/StructureDefinition/capabilitystatement-declared-profile'

    def test_auditevent_sopclass_url(self):
        assert AUDITEVENT_SOPCLASS_URL == 'http://hl7.org/fhir/StructureDefinition/auditevent-SOPClass'

    def test_cqf_recipient_type_url(self):
        assert CQF_RECIPIENT_TYPE_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-recipientType'

    def test_questionnaire_option_exclusive_url(self):
        assert QUESTIONNAIRE_OPTION_EXCLUSIVE_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-optionExclusive'

    def test_specimen_is_dry_weight_url(self):
        assert SPECIMEN_IS_DRY_WEIGHT_URL == 'http://hl7.org/fhir/StructureDefinition/specimen-isDryWeight'

    def test_artifact_related_artifact_url(self):
        assert ARTIFACT_RELATED_ARTIFACT_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-relatedArtifact'

    def test_task_replaces_url(self):
        assert TASK_REPLACES_URL == 'http://hl7.org/fhir/StructureDefinition/task-replaces'

    def test_artifact_reference_url(self):
        assert ARTIFACT_REFERENCE_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-reference'

    def test_cqf_direct_reference_code_url(self):
        assert CQF_DIRECT_REFERENCE_CODE_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-directReferenceCode'

    def test_immunization_procedure_url(self):
        assert IMMUNIZATION_PROCEDURE_URL == 'http://hl7.org/fhir/StructureDefinition/immunization-procedure'

    def test_valueset_concept_definition_url(self):
        assert VALUESET_CONCEPT_DEFINITION_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-concept-definition'

    def test_annotation_type_url(self):
        assert ANNOTATION_TYPE_URL == 'http://hl7.org/fhir/StructureDefinition/annotationType'

    def test_encounter_reason_cancelled_url(self):
        assert ENCOUNTER_REASON_CANCELLED_URL == 'http://hl7.org/fhir/StructureDefinition/encounter-reasonCancelled'

    def test_structuredefinition_explicit_type_name_url(self):
        assert STRUCTUREDEFINITION_EXPLICIT_TYPE_NAME_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-explicit-type-name'

    def test_event_part_of_url(self):
        assert EVENT_PART_OF_URL == 'http://hl7.org/fhir/StructureDefinition/event-partOf'

    def test_resource_effective_period_url(self):
        assert RESOURCE_EFFECTIVE_PERIOD_URL == 'http://hl7.org/fhir/StructureDefinition/resource-effectivePeriod'

    def test_auditevent_alternative_user_id_url(self):
        assert AUDITEVENT_ALTERNATIVE_USER_ID_URL == 'http://hl7.org/fhir/StructureDefinition/auditevent-AlternativeUserID'

    def test_iso21090_adxp_delivery_installation_area_url(self):
        assert ISO21090_ADXP_DELIVERY_INSTALLATION_AREA_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-deliveryInstallationArea'

    def test_workflow_related_artifact_url(self):
        assert WORKFLOW_RELATED_ARTIFACT_URL == 'http://hl7.org/fhir/StructureDefinition/workflow-relatedArtifact'

    def test_valueset_concept_comments_url(self):
        assert VALUESET_CONCEPT_COMMENTS_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-concept-comments'

    def test_observation_precondition_url(self):
        assert OBSERVATION_PRECONDITION_URL == 'http://hl7.org/fhir/StructureDefinition/observation-precondition'

    def test_servicerequest_questionnaire_request_url(self):
        assert SERVICEREQUEST_QUESTIONNAIRE_REQUEST_URL == 'http://hl7.org/fhir/StructureDefinition/servicerequest-questionnaireRequest'

    def test_concept_bidirectional_url(self):
        assert CONCEPT_BIDIRECTIONAL_URL == 'http://hl7.org/fhir/StructureDefinition/concept-bidirectional'

    def test_nutritionorder_adaptive_feeding_device_url(self):
        assert NUTRITIONORDER_ADAPTIVE_FEEDING_DEVICE_URL == 'http://hl7.org/fhir/StructureDefinition/nutritionorder-adaptiveFeedingDevice'

    def test_iso21090_coded_string_url(self):
        assert ISO21090_CODED_STRING_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-codedString'

    def test_elementdefinition_identifier_url(self):
        assert ELEMENTDEFINITION_IDENTIFIER_URL == 'http://hl7.org/fhir/StructureDefinition/elementdefinition-identifier'

    def test_iso21090_adxp_delivery_address_line_url(self):
        assert ISO21090_ADXP_DELIVERY_ADDRESS_LINE_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-deliveryAddressLine'

    def test_communication_media_url(self):
        assert COMMUNICATION_MEDIA_URL == 'http://hl7.org/fhir/StructureDefinition/communication-media'

    def test_structuredefinition_hierarchy_url(self):
        assert STRUCTUREDEFINITION_HIERARCHY_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-hierarchy'

    def test_specimen_additive_url(self):
        assert SPECIMEN_ADDITIVE_URL == 'http://hl7.org/fhir/StructureDefinition/specimen-additive'

    def test_patient_birth_time_url(self):
        assert PATIENT_BIRTH_TIME_URL == 'http://hl7.org/fhir/StructureDefinition/patient-birthTime'

    def test_practitionerrole_employment_status_url(self):
        assert PRACTITIONERROLE_EMPLOYMENT_STATUS_URL == 'http://hl7.org/fhir/StructureDefinition/practitionerrole-employmentStatus'

    def test_valueset_source_reference_url(self):
        assert VALUESET_SOURCE_REFERENCE_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-sourceReference'

    def test_workflow_follow_on_of_url(self):
        assert WORKFLOW_FOLLOW_ON_OF_URL == 'http://hl7.org/fhir/StructureDefinition/workflow-followOnOf'

    def test_quantity_precision_url(self):
        assert QUANTITY_PRECISION_URL == 'http://hl7.org/fhir/StructureDefinition/quantity-precision'

    def test_condition_outcome_url(self):
        assert CONDITION_OUTCOME_URL == 'http://hl7.org/fhir/StructureDefinition/condition-outcome'

    def test_display_url(self):
        assert DISPLAY_URL == 'http://hl7.org/fhir/StructureDefinition/display'

    def test_contactpoint_comment_url(self):
        assert CONTACTPOINT_COMMENT_URL == 'http://hl7.org/fhir/StructureDefinition/contactpoint-comment'

    def test_valueset_compose_include_value_set_title_url(self):
        assert VALUESET_COMPOSE_INCLUDE_VALUE_SET_TITLE_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-compose-include-valueSetTitle'

    def test_valueset_reference_url(self):
        assert VALUESET_REFERENCE_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-reference'

    def test_artifact_usage_url(self):
        assert ARTIFACT_USAGE_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-usage'

    def test_iso21090_adxp_delivery_installation_qualifier_url(self):
        assert ISO21090_ADXP_DELIVERY_INSTALLATION_QUALIFIER_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-deliveryInstallationQualifier'

    def test_allergyintolerance_resolution_age_url(self):
        assert ALLERGYINTOLERANCE_RESOLUTION_AGE_URL == 'http://hl7.org/fhir/StructureDefinition/allergyintolerance-resolutionAge'

    def test_artifact_endorser_url(self):
        assert ARTIFACT_ENDORSER_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-endorser'

    def test_open_ehr_management_url(self):
        assert OPEN_EHR_MANAGEMENT_URL == 'http://hl7.org/fhir/StructureDefinition/openEHR-management'

    def test_questionnaire_option_restriction_url(self):
        assert QUESTIONNAIRE_OPTION_RESTRICTION_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-optionRestriction'

    def test_note_url(self):
        assert NOTE_URL == 'http://hl7.org/fhir/StructureDefinition/note'

    def test_familymemberhistory_severity_url(self):
        assert FAMILYMEMBERHISTORY_SEVERITY_URL == 'http://hl7.org/fhir/StructureDefinition/familymemberhistory-severity'

    def test_version_specific_value_url(self):
        assert VERSION_SPECIFIC_VALUE_URL == 'http://hl7.org/fhir/StructureDefinition/version-specific-value'

    def test_organization_period_url(self):
        assert ORGANIZATION_PERIOD_URL == 'http://hl7.org/fhir/StructureDefinition/organization-period'

    def test_cqf_supported_cql_version_url(self):
        assert CQF_SUPPORTED_CQL_VERSION_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-supportedCqlVersion'

    def test_valueset_system_name_url(self):
        assert VALUESET_SYSTEM_NAME_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-systemName'

    def test_iso21090_adxp_street_address_line_url(self):
        assert ISO21090_ADXP_STREET_ADDRESS_LINE_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-streetAddressLine'

    def test_familymemberhistory_abatement_url(self):
        assert FAMILYMEMBERHISTORY_ABATEMENT_URL == 'http://hl7.org/fhir/StructureDefinition/familymemberhistory-abatement'

    def test_artifact_name_url(self):
        assert ARTIFACT_NAME_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-name'

    def test_individual_gender_identity_url(self):
        assert INDIVIDUAL_GENDER_IDENTITY_URL == 'http://hl7.org/fhir/StructureDefinition/individual-genderIdentity'

    def test_questionnaire_max_occurs_url(self):
        assert QUESTIONNAIRE_MAX_OCCURS_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-maxOccurs'

    def test_structuredefinition_template_status_url(self):
        assert STRUCTUREDEFINITION_TEMPLATE_STATUS_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-template-status'

    def test_list_for_url(self):
        assert LIST_FOR_URL == 'http://hl7.org/fhir/StructureDefinition/list-for'

    def test_artifact_jurisdiction_url(self):
        assert ARTIFACT_JURISDICTION_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-jurisdiction'

    def test_codesystem_label_url(self):
        assert CODESYSTEM_LABEL_URL == 'http://hl7.org/fhir/StructureDefinition/codesystem-label'

    def test_cqf_knowledge_representation_level_url(self):
        assert CQF_KNOWLEDGE_REPRESENTATION_LEVEL_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-knowledgeRepresentationLevel'

    def test_procedure_method_url(self):
        assert PROCEDURE_METHOD_URL == 'http://hl7.org/fhir/StructureDefinition/procedure-method'

    def test_iso21090_en_use_url(self):
        assert ISO21090_EN_USE_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-EN-use'

    def test_event_based_on_url(self):
        assert EVENT_BASED_ON_URL == 'http://hl7.org/fhir/StructureDefinition/event-basedOn'

    def test_usagecontext_group_url(self):
        assert USAGECONTEXT_GROUP_URL == 'http://hl7.org/fhir/StructureDefinition/usagecontext-group'

    def test_structuredefinition_summary_url(self):
        assert STRUCTUREDEFINITION_SUMMARY_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-summary'

    def test_diagnostic_report_addendum_of_url(self):
        assert DIAGNOSTIC_REPORT_ADDENDUM_OF_URL == 'http://hl7.org/fhir/StructureDefinition/diagnosticReport-addendumOf'

    def test_workflow_release_date_url(self):
        assert WORKFLOW_RELEASE_DATE_URL == 'http://hl7.org/fhir/StructureDefinition/workflow-releaseDate'

    def test_ext_11179_permitted_value_conceptmap_url(self):
        assert EXT_11179_PERMITTED_VALUE_CONCEPTMAP_URL == 'http://hl7.org/fhir/StructureDefinition/11179-permitted-value-conceptmap'

    def test_structuredefinition_normative_version_url(self):
        assert STRUCTUREDEFINITION_NORMATIVE_VERSION_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-normative-version'

    def test_artifact_canonical_reference_url(self):
        assert ARTIFACT_CANONICAL_REFERENCE_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-canonicalReference'

    def test_operationoutcome_issue_slicetext_url(self):
        assert OPERATIONOUTCOME_ISSUE_SLICETEXT_URL == 'http://hl7.org/fhir/StructureDefinition/operationoutcome-issue-slicetext'

    def test_capabilitystatement_prohibited_url(self):
        assert CAPABILITYSTATEMENT_PROHIBITED_URL == 'http://hl7.org/fhir/StructureDefinition/capabilitystatement-prohibited'

    def test_obligation_url(self):
        assert OBLIGATION_URL == 'http://hl7.org/fhir/StructureDefinition/obligation'

    def test_iso21090_adxp_care_of_url(self):
        assert ISO21090_ADXP_CARE_OF_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-careOf'

    def test_cqm_validity_period_url(self):
        assert CQM_VALIDITY_PERIOD_URL == 'http://hl7.org/fhir/StructureDefinition/cqm-ValidityPeriod'

    def test_observation_delta_url(self):
        assert OBSERVATION_DELTA_URL == 'http://hl7.org/fhir/StructureDefinition/observation-delta'

    def test_original_text_url(self):
        assert ORIGINAL_TEXT_URL == 'http://hl7.org/fhir/StructureDefinition/originalText'

    def test_request_relevant_history_url(self):
        assert REQUEST_RELEVANT_HISTORY_URL == 'http://hl7.org/fhir/StructureDefinition/request-relevantHistory'

    def test_structuredefinition_conformance_derived_from_url(self):
        assert STRUCTUREDEFINITION_CONFORMANCE_DERIVED_FROM_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-conformance-derivedFrom'

    def test_valueset_parameter_source_url(self):
        assert VALUESET_PARAMETER_SOURCE_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-parameterSource'

    def test_workflow_supporting_info_url(self):
        assert WORKFLOW_SUPPORTING_INFO_URL == 'http://hl7.org/fhir/StructureDefinition/workflow-supportingInfo'

    def test_consent_notification_endpoint_url(self):
        assert CONSENT_NOTIFICATION_ENDPOINT_URL == 'http://hl7.org/fhir/StructureDefinition/consent-NotificationEndpoint'

    def test_ext_11179_object_class_property_url(self):
        assert EXT_11179_OBJECT_CLASS_PROPERTY_URL == 'http://hl7.org/fhir/StructureDefinition/11179-objectClassProperty'

    def test_match_grade_url(self):
        assert MATCH_GRADE_URL == 'http://hl7.org/fhir/StructureDefinition/match-grade'

    def test_iso21090_adxp_delivery_mode_url(self):
        assert ISO21090_ADXP_DELIVERY_MODE_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-deliveryMode'

    def test_valueset_expansion_source_url(self):
        assert VALUESET_EXPANSION_SOURCE_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-expansionSource'

    def test_questionnaire_definition_based_url(self):
        assert QUESTIONNAIRE_DEFINITION_BASED_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-definitionBased'

    def test_diagnostic_report_replaces_url(self):
        assert DIAGNOSTIC_REPORT_REPLACES_URL == 'http://hl7.org/fhir/StructureDefinition/diagnosticReport-replaces'

    def test_medication_manufacturing_batch_url(self):
        assert MEDICATION_MANUFACTURING_BATCH_URL == 'http://hl7.org/fhir/StructureDefinition/medication-manufacturingBatch'

    def test_cqf_encounter_class_url(self):
        assert CQF_ENCOUNTER_CLASS_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-encounterClass'

    def test_open_ehr_exposure_date_url(self):
        assert OPEN_EHR_EXPOSURE_DATE_URL == 'http://hl7.org/fhir/StructureDefinition/openEHR-exposureDate'

    def test_condition_asserted_date_url(self):
        assert CONDITION_ASSERTED_DATE_URL == 'http://hl7.org/fhir/StructureDefinition/condition-assertedDate'

    def test_practitioner_job_title_url(self):
        assert PRACTITIONER_JOB_TITLE_URL == 'http://hl7.org/fhir/StructureDefinition/practitioner-job-title'

    def test_cqf_contact_address_url(self):
        assert CQF_CONTACT_ADDRESS_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-contactAddress'

    def test_codesystem_concept_order_url(self):
        assert CODESYSTEM_CONCEPT_ORDER_URL == 'http://hl7.org/fhir/StructureDefinition/codesystem-conceptOrder'

    def test_cqf_alternative_expression_url(self):
        assert CQF_ALTERNATIVE_EXPRESSION_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-alternativeExpression'

    def test_artifact_reviewer_url(self):
        assert ARTIFACT_REVIEWER_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-reviewer'

    def test_humanname_fathers_family_url(self):
        assert HUMANNAME_FATHERS_FAMILY_URL == 'http://hl7.org/fhir/StructureDefinition/humanname-fathers-family'

    def test_cqf_relative_date_time_url(self):
        assert CQF_RELATIVE_DATE_TIME_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-relativeDateTime'

    def test_cqf_recipient_language_url(self):
        assert CQF_RECIPIENT_LANGUAGE_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-recipientLanguage'

    def test_dosage_minimum_gap_between_dose_url(self):
        assert DOSAGE_MINIMUM_GAP_BETWEEN_DOSE_URL == 'http://hl7.org/fhir/StructureDefinition/dosage-minimumGapBetweenDose'

    def test_documentreference_thumbnail_url(self):
        assert DOCUMENTREFERENCE_THUMBNAIL_URL == 'http://hl7.org/fhir/StructureDefinition/documentreference-thumbnail'

    def test_questionnaire_item_control_url(self):
        assert QUESTIONNAIRE_ITEM_CONTROL_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-itemControl'

    def test_valueset_system_url(self):
        assert VALUESET_SYSTEM_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-system'

    def test_questionnaire_support_link_url(self):
        assert QUESTIONNAIRE_SUPPORT_LINK_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-supportLink'

    def test_family_member_history_genetics_observation_url(self):
        assert FAMILY_MEMBER_HISTORY_GENETICS_OBSERVATION_URL == 'http://hl7.org/fhir/StructureDefinition/family-member-history-genetics-observation'

    def test_cqf_cql_type_url(self):
        assert CQF_CQL_TYPE_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-cqlType'

    def test_specimen_special_handling_url(self):
        assert SPECIMEN_SPECIAL_HANDLING_URL == 'http://hl7.org/fhir/StructureDefinition/specimen-specialHandling'

    def test_timezone_url(self):
        assert TIMEZONE_URL == 'http://hl7.org/fhir/StructureDefinition/timezone'

    def test_cqf_model_info_is_retrievable_url(self):
        assert CQF_MODEL_INFO_IS_RETRIEVABLE_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-modelInfo-isRetrievable'

    def test_structuredefinition_impose_profile_url(self):
        assert STRUCTUREDEFINITION_IMPOSE_PROFILE_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-imposeProfile'

    def test_patient_nationality_url(self):
        assert PATIENT_NATIONALITY_URL == 'http://hl7.org/fhir/StructureDefinition/patient-nationality'

    def test_workflow_episode_of_care_url(self):
        assert WORKFLOW_EPISODE_OF_CARE_URL == 'http://hl7.org/fhir/StructureDefinition/workflow-episodeOfCare'

    def test_canonicalresource_short_description_url(self):
        assert CANONICALRESOURCE_SHORT_DESCRIPTION_URL == 'http://hl7.org/fhir/StructureDefinition/canonicalresource-short-description'

    def test_namingsystem_check_digit_url(self):
        assert NAMINGSYSTEM_CHECK_DIGIT_URL == 'http://hl7.org/fhir/StructureDefinition/namingsystem-checkDigit'

    def test_request_performer_order_url(self):
        assert REQUEST_PERFORMER_ORDER_URL == 'http://hl7.org/fhir/StructureDefinition/request-performerOrder'

    def test_min_value_url(self):
        assert MIN_VALUE_URL == 'http://hl7.org/fhir/StructureDefinition/minValue'

    def test_location_boundary_geojson_url(self):
        assert LOCATION_BOUNDARY_GEOJSON_URL == 'http://hl7.org/fhir/StructureDefinition/location-boundary-geojson'

    def test_cqf_is_prefetch_token_url(self):
        assert CQF_IS_PREFETCH_TOKEN_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-isPrefetchToken'

    def test_cqf_definition_term_url(self):
        assert CQF_DEFINITION_TERM_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-definitionTerm'

    def test_valueset_warning_url(self):
        assert VALUESET_WARNING_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-warning'

    def test_iso21090_adxp_house_number_numeric_url(self):
        assert ISO21090_ADXP_HOUSE_NUMBER_NUMERIC_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-houseNumberNumeric'

    def test_replaces_url(self):
        assert REPLACES_URL == 'http://hl7.org/fhir/StructureDefinition/replaces'

    def test_list_category_url(self):
        assert LIST_CATEGORY_URL == 'http://hl7.org/fhir/StructureDefinition/list-category'

    def test_consent_location_url(self):
        assert CONSENT_LOCATION_URL == 'http://hl7.org/fhir/StructureDefinition/consent-location'

    def test_cqf_cql_options_url(self):
        assert CQF_CQL_OPTIONS_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-cqlOptions'

    def test_biologicallyderivedproduct_processing_url(self):
        assert BIOLOGICALLYDERIVEDPRODUCT_PROCESSING_URL == 'http://hl7.org/fhir/StructureDefinition/biologicallyderivedproduct-processing'

    def test_patient_born_status_url(self):
        assert PATIENT_BORN_STATUS_URL == 'http://hl7.org/fhir/StructureDefinition/patient-bornStatus'

    def test_valueset_case_sensitive_url(self):
        assert VALUESET_CASE_SENSITIVE_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-caseSensitive'

    def test_mime_type_url(self):
        assert MIME_TYPE_URL == 'http://hl7.org/fhir/StructureDefinition/mimeType'

    def test_event_status_reason_url(self):
        assert EVENT_STATUS_REASON_URL == 'http://hl7.org/fhir/StructureDefinition/event-statusReason'

    def test_codesystem_key_word_url(self):
        assert CODESYSTEM_KEY_WORD_URL == 'http://hl7.org/fhir/StructureDefinition/codesystem-keyWord'

    def test_design_note_url(self):
        assert DESIGN_NOTE_URL == 'http://hl7.org/fhir/StructureDefinition/designNote'

    def test_iso21090_adxp_delimiter_url(self):
        assert ISO21090_ADXP_DELIMITER_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-delimiter'

    def test_humanname_partner_name_url(self):
        assert HUMANNAME_PARTNER_NAME_URL == 'http://hl7.org/fhir/StructureDefinition/humanname-partner-name'

    def test_elementdefinition_inherited_extensible_value_set_url(self):
        assert ELEMENTDEFINITION_INHERITED_EXTENSIBLE_VALUE_SET_URL == 'http://hl7.org/fhir/StructureDefinition/elementdefinition-inheritedExtensibleValueSet'

    def test_artifact_use_context_url(self):
        assert ARTIFACT_USE_CONTEXT_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-useContext'

    def test_allergyintolerance_certainty_url(self):
        assert ALLERGYINTOLERANCE_CERTAINTY_URL == 'http://hl7.org/fhir/StructureDefinition/allergyintolerance-certainty'

    def test_specimen_collection_priority_url(self):
        assert SPECIMEN_COLLECTION_PRIORITY_URL == 'http://hl7.org/fhir/StructureDefinition/specimen-collectionPriority'

    def test_variable_url(self):
        assert VARIABLE_URL == 'http://hl7.org/fhir/StructureDefinition/variable'

    def test_operationoutcome_message_id_url(self):
        assert OPERATIONOUTCOME_MESSAGE_ID_URL == 'http://hl7.org/fhir/StructureDefinition/operationoutcome-message-id'

    def test_communicationrequest_initiating_location_url(self):
        assert COMMUNICATIONREQUEST_INITIATING_LOCATION_URL == 'http://hl7.org/fhir/StructureDefinition/communicationrequest-initiatingLocation'

    def test_codesystem_source_reference_url(self):
        assert CODESYSTEM_SOURCE_REFERENCE_URL == 'http://hl7.org/fhir/StructureDefinition/codesystem-sourceReference'

    def test_valueset_trusted_expansion_url(self):
        assert VALUESET_TRUSTED_EXPANSION_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-trusted-expansion'

    def test_valueset_expression_url(self):
        assert VALUESET_EXPRESSION_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-expression'

    def test_patient_adoption_info_url(self):
        assert PATIENT_ADOPTION_INFO_URL == 'http://hl7.org/fhir/StructureDefinition/patient-adoptionInfo'

    def test_questionnaire_display_category_url(self):
        assert QUESTIONNAIRE_DISPLAY_CATEGORY_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-displayCategory'

    def test_artifact_release_label_url(self):
        assert ARTIFACT_RELEASE_LABEL_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-releaseLabel'

    def test_artifactassessment_content_url(self):
        assert ARTIFACTASSESSMENT_CONTENT_URL == 'http://hl7.org/fhir/StructureDefinition/artifactassessment-content'

    def test_specimen_reject_reason_url(self):
        assert SPECIMEN_REJECT_REASON_URL == 'http://hl7.org/fhir/StructureDefinition/specimen-reject-reason'

    def test_condition_reviewed_url(self):
        assert CONDITION_REVIEWED_URL == 'http://hl7.org/fhir/StructureDefinition/condition-reviewed'

    def test_cqf_logic_definition_url(self):
        assert CQF_LOGIC_DEFINITION_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-logicDefinition'

    def test_operationoutcome_issue_server_url(self):
        assert OPERATIONOUTCOME_ISSUE_SERVER_URL == 'http://hl7.org/fhir/StructureDefinition/operationoutcome-issue-server'

    def test_patient_unknown_identity_url(self):
        assert PATIENT_UNKNOWN_IDENTITY_URL == 'http://hl7.org/fhir/StructureDefinition/patient-unknownIdentity'

    def test_careplan_activity_title_url(self):
        assert CAREPLAN_ACTIVITY_TITLE_URL == 'http://hl7.org/fhir/StructureDefinition/careplan-activity-title'

    def test_artifact_version_url(self):
        assert ARTIFACT_VERSION_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-version'

    def test_valueset_supplement_url(self):
        assert VALUESET_SUPPLEMENT_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-supplement'

    def test_artifact_url_url(self):
        assert ARTIFACT_URL_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-url'

    def test_elementdefinition_question_url(self):
        assert ELEMENTDEFINITION_QUESTION_URL == 'http://hl7.org/fhir/StructureDefinition/elementdefinition-question'

    def test_servicerequest_order_callback_phone_number_url(self):
        assert SERVICEREQUEST_ORDER_CALLBACK_PHONE_NUMBER_URL == 'http://hl7.org/fhir/StructureDefinition/servicerequest-order-callback-phone-number'

    def test_cqf_receiving_organization_url(self):
        assert CQF_RECEIVING_ORGANIZATION_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-receivingOrganization'

    def test_resource_instance_description_url(self):
        assert RESOURCE_INSTANCE_DESCRIPTION_URL == 'http://hl7.org/fhir/StructureDefinition/resource-instance-description'

    def test_artifact_version_algorithm_url(self):
        assert ARTIFACT_VERSION_ALGORITHM_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-versionAlgorithm'

    def test_elementdefinition_bestpractice_url(self):
        assert ELEMENTDEFINITION_BESTPRACTICE_URL == 'http://hl7.org/fhir/StructureDefinition/elementdefinition-bestpractice'

    def test_practitioner_animal_species_url(self):
        assert PRACTITIONER_ANIMAL_SPECIES_URL == 'http://hl7.org/fhir/StructureDefinition/practitioner-animalSpecies'

    def test_workflow_barrier_url(self):
        assert WORKFLOW_BARRIER_URL == 'http://hl7.org/fhir/StructureDefinition/workflow-barrier'

    def test_observation_focus_code_url(self):
        assert OBSERVATION_FOCUS_CODE_URL == 'http://hl7.org/fhir/StructureDefinition/observation-focusCode'

    def test_observation_secondary_finding_url(self):
        assert OBSERVATION_SECONDARY_FINDING_URL == 'http://hl7.org/fhir/StructureDefinition/observation-secondaryFinding'

    def test_iso21090_adxp_delivery_installation_type_url(self):
        assert ISO21090_ADXP_DELIVERY_INSTALLATION_TYPE_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-deliveryInstallationType'

    def test_codesystem_workflow_status_url(self):
        assert CODESYSTEM_WORKFLOW_STATUS_URL == 'http://hl7.org/fhir/StructureDefinition/codesystem-workflowStatus'

    def test_timing_exact_url(self):
        assert TIMING_EXACT_URL == 'http://hl7.org/fhir/StructureDefinition/timing-exact'

    def test_timing_uncertain_date_url(self):
        assert TIMING_UNCERTAIN_DATE_URL == 'http://hl7.org/fhir/StructureDefinition/timing-uncertainDate'

    def test_structuredefinition_wg_url(self):
        assert STRUCTUREDEFINITION_WG_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-wg'

    def test_iso21090_adxp_building_number_suffix_url(self):
        assert ISO21090_ADXP_BUILDING_NUMBER_SUFFIX_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-buildingNumberSuffix'

    def test_cqf_not_done_value_set_url(self):
        assert CQF_NOT_DONE_VALUE_SET_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-notDoneValueSet'

    def test_cqf_input_parameters_url(self):
        assert CQF_INPUT_PARAMETERS_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-inputParameters'

    def test_cqf_default_value_url(self):
        assert CQF_DEFAULT_VALUE_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-defaultValue'

    def test_cqf_improvement_notation_guidance_url(self):
        assert CQF_IMPROVEMENT_NOTATION_GUIDANCE_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-improvementNotationGuidance'

    def test_data_absent_reason_url(self):
        assert DATA_ABSENT_REASON_URL == 'http://hl7.org/fhir/StructureDefinition/data-absent-reason'

    def test_rendering_style_sensitive_url(self):
        assert RENDERING_STYLE_SENSITIVE_URL == 'http://hl7.org/fhir/StructureDefinition/rendering-styleSensitive'

    def test_questionnaire_base_type_url(self):
        assert QUESTIONNAIRE_BASE_TYPE_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-baseType'

    def test_observation_gateway_device_url(self):
        assert OBSERVATION_GATEWAY_DEVICE_URL == 'http://hl7.org/fhir/StructureDefinition/observation-gatewayDevice'

    def test_cqf_strength_of_recommendation_url(self):
        assert CQF_STRENGTH_OF_RECOMMENDATION_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-strengthOfRecommendation'

    def test_cqf_receiving_person_url(self):
        assert CQF_RECEIVING_PERSON_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-receivingPerson'

    def test_artifact_publisher_url(self):
        assert ARTIFACT_PUBLISHER_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-publisher'

    def test_structuredefinition_interface_url(self):
        assert STRUCTUREDEFINITION_INTERFACE_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-interface'

    def test_iso21090_null_flavor_url(self):
        assert ISO21090_NULL_FLAVOR_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-nullFlavor'

    def test_questionnaire_reference_resource_url(self):
        assert QUESTIONNAIRE_REFERENCE_RESOURCE_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-referenceResource'

    def test_item_weight_url(self):
        assert ITEM_WEIGHT_URL == 'http://hl7.org/fhir/StructureDefinition/itemWeight'

    def test_iso21090_uncertainty_url(self):
        assert ISO21090_UNCERTAINTY_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-uncertainty'

    def test_codesystem_replacedby_url(self):
        assert CODESYSTEM_REPLACEDBY_URL == 'http://hl7.org/fhir/StructureDefinition/codesystem-replacedby'

    def test_valueset_authoritative_source_url(self):
        assert VALUESET_AUTHORITATIVE_SOURCE_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-authoritativeSource'

    def test_elementdefinition_binding_name_url(self):
        assert ELEMENTDEFINITION_BINDING_NAME_URL == 'http://hl7.org/fhir/StructureDefinition/elementdefinition-bindingName'

    def test_practitionerrole_primary_ind_url(self):
        assert PRACTITIONERROLE_PRIMARY_IND_URL == 'http://hl7.org/fhir/StructureDefinition/practitionerrole-primaryInd'

    def test_endpoint_fhir_version_url(self):
        assert ENDPOINT_FHIR_VERSION_URL == 'http://hl7.org/fhir/StructureDefinition/endpoint-fhir-version'

    def test_cqf_system_user_type_url(self):
        assert CQF_SYSTEM_USER_TYPE_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-systemUserType'

    def test_iso21090_preferred_url(self):
        assert ISO21090_PREFERRED_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-preferred'

    def test_cqf_encounter_type_url(self):
        assert CQF_ENCOUNTER_TYPE_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-encounterType'

    def test_coding_conformance_url(self):
        assert CODING_CONFORMANCE_URL == 'http://hl7.org/fhir/StructureDefinition/coding-conformance'

    def test_valueset_usage_url(self):
        assert VALUESET_USAGE_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-usage'

    def test_valueset_other_title_url(self):
        assert VALUESET_OTHER_TITLE_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-otherTitle'

    def test_consent_witness_url(self):
        assert CONSENT_WITNESS_URL == 'http://hl7.org/fhir/StructureDefinition/consent-Witness'

    def test_implementationguide_source_file_url(self):
        assert IMPLEMENTATIONGUIDE_SOURCE_FILE_URL == 'http://hl7.org/fhir/StructureDefinition/implementationguide-sourceFile'

    def test_iso21090_ad_use_url(self):
        assert ISO21090_AD_USE_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-AD-use'

    def test_dosage_conditions_url(self):
        assert DOSAGE_CONDITIONS_URL == 'http://hl7.org/fhir/StructureDefinition/dosage-conditions'

    def test_iso21090_adxp_precinct_url(self):
        assert ISO21090_ADXP_PRECINCT_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-precinct'

    def test_patient_cadaveric_donor_url(self):
        assert PATIENT_CADAVERIC_DONOR_URL == 'http://hl7.org/fhir/StructureDefinition/patient-cadavericDonor'

    def test_characteristic_expression_url(self):
        assert CHARACTERISTIC_EXPRESSION_URL == 'http://hl7.org/fhir/StructureDefinition/characteristicExpression'

    def test_workflow_reason_url(self):
        assert WORKFLOW_REASON_URL == 'http://hl7.org/fhir/StructureDefinition/workflow-reason'

    def test_artifact_approval_date_url(self):
        assert ARTIFACT_APPROVAL_DATE_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-approvalDate'

    def test_codesystem_usage_url(self):
        assert CODESYSTEM_USAGE_URL == 'http://hl7.org/fhir/StructureDefinition/codesystem-usage'

    def test_elementdefinition_graph_constraint_url(self):
        assert ELEMENTDEFINITION_GRAPH_CONSTRAINT_URL == 'http://hl7.org/fhir/StructureDefinition/elementdefinition-graphConstraint'

    def test_organization_portal_url(self):
        assert ORGANIZATION_PORTAL_URL == 'http://hl7.org/fhir/StructureDefinition/organization-portal'

    def test_observation_time_offset_url(self):
        assert OBSERVATION_TIME_OFFSET_URL == 'http://hl7.org/fhir/StructureDefinition/observation-timeOffset'

    def test_artifact_topic_url(self):
        assert ARTIFACT_TOPIC_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-topic'

    def test_operationoutcome_issue_line_url(self):
        assert OPERATIONOUTCOME_ISSUE_LINE_URL == 'http://hl7.org/fhir/StructureDefinition/operationoutcome-issue-line'

    def test_workflow_adheres_to_url(self):
        assert WORKFLOW_ADHERES_TO_URL == 'http://hl7.org/fhir/StructureDefinition/workflow-adheresTo'

    def test_patient_animal_url(self):
        assert PATIENT_ANIMAL_URL == 'http://hl7.org/fhir/StructureDefinition/patient-animal'

    def test_parameters_definition_url(self):
        assert PARAMETERS_DEFINITION_URL == 'http://hl7.org/fhir/StructureDefinition/parameters-definition'

    def test_encounter_associated_encounter_url(self):
        assert ENCOUNTER_ASSOCIATED_ENCOUNTER_URL == 'http://hl7.org/fhir/StructureDefinition/encounter-associatedEncounter'

    def test_capabilitystatement_search_parameter_combination_url(self):
        assert CAPABILITYSTATEMENT_SEARCH_PARAMETER_COMBINATION_URL == 'http://hl7.org/fhir/StructureDefinition/capabilitystatement-search-parameter-combination'

    def test_specimen_processing_time_url(self):
        assert SPECIMEN_PROCESSING_TIME_URL == 'http://hl7.org/fhir/StructureDefinition/specimen-processingTime'

    def test_contactpoint_country_url(self):
        assert CONTACTPOINT_COUNTRY_URL == 'http://hl7.org/fhir/StructureDefinition/contactpoint-country'

    def test_capabilitystatement_supported_system_url(self):
        assert CAPABILITYSTATEMENT_SUPPORTED_SYSTEM_URL == 'http://hl7.org/fhir/StructureDefinition/capabilitystatement-supported-system'

    def test_elementdefinition_min_value_set_url(self):
        assert ELEMENTDEFINITION_MIN_VALUE_SET_URL == 'http://hl7.org/fhir/StructureDefinition/elementdefinition-minValueSet'

    def test_first_created_url(self):
        assert FIRST_CREATED_URL == 'http://hl7.org/fhir/StructureDefinition/firstCreated'

    def test_cqf_system_user_task_context_url(self):
        assert CQF_SYSTEM_USER_TASK_CONTEXT_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-systemUserTaskContext'

    def test_body_site_url(self):
        assert BODY_SITE_URL == 'http://hl7.org/fhir/StructureDefinition/bodySite'

    def test_event_event_history_url(self):
        assert EVENT_EVENT_HISTORY_URL == 'http://hl7.org/fhir/StructureDefinition/event-eventHistory'

    def test_questionnaire_choice_orientation_url(self):
        assert QUESTIONNAIRE_CHOICE_ORIENTATION_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-choiceOrientation'

    def test_quantity_translation_url(self):
        assert QUANTITY_TRANSLATION_URL == 'http://hl7.org/fhir/StructureDefinition/extension-quantity-translation'

    def test_allergyintolerance_asserted_date_url(self):
        assert ALLERGYINTOLERANCE_ASSERTED_DATE_URL == 'http://hl7.org/fhir/StructureDefinition/allergyintolerance-assertedDate'

    def test_valueset_deprecated_url(self):
        assert VALUESET_DEPRECATED_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-deprecated'

    def test_cqf_quality_of_evidence_url(self):
        assert CQF_QUALITY_OF_EVIDENCE_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-qualityOfEvidence'

    def test_iso21090_adxp_direction_url(self):
        assert ISO21090_ADXP_DIRECTION_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-direction'

    def test_questionnaireresponse_signature_url(self):
        assert QUESTIONNAIRERESPONSE_SIGNATURE_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaireresponse-signature'

    def test_valueset_key_word_url(self):
        assert VALUESET_KEY_WORD_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-keyWord'

    def test_flag_priority_url(self):
        assert FLAG_PRIORITY_URL == 'http://hl7.org/fhir/StructureDefinition/flag-priority'

    def test_cqf_model_info_label_url(self):
        assert CQF_MODEL_INFO_LABEL_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-modelInfo-label'

    def test_target_element_url(self):
        assert TARGET_ELEMENT_URL == 'http://hl7.org/fhir/StructureDefinition/targetElement'

    def test_procedure_approach_body_structure_url(self):
        assert PROCEDURE_APPROACH_BODY_STRUCTURE_URL == 'http://hl7.org/fhir/StructureDefinition/procedure-approachBodyStructure'

    def test_iso21090_adxp_census_tract_url(self):
        assert ISO21090_ADXP_CENSUS_TRACT_URL == 'http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-censusTract'

    def test_cqf_model_info_is_included_url(self):
        assert CQF_MODEL_INFO_IS_INCLUDED_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-modelInfo-isIncluded'

    def test_diagnostic_report_location_performed_url(self):
        assert DIAGNOSTIC_REPORT_LOCATION_PERFORMED_URL == 'http://hl7.org/fhir/StructureDefinition/diagnosticReport-locationPerformed'

    def test_cqf_messages_url(self):
        assert CQF_MESSAGES_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-messages'

    def test_structuredefinition_codegen_super_url(self):
        assert STRUCTUREDEFINITION_CODEGEN_SUPER_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-codegen-super'

    def test_operationoutcome_authority_url(self):
        assert OPERATIONOUTCOME_AUTHORITY_URL == 'http://hl7.org/fhir/StructureDefinition/operationoutcome-authority'

    def test_patient_citizenship_url(self):
        assert PATIENT_CITIZENSHIP_URL == 'http://hl7.org/fhir/StructureDefinition/patient-citizenship'

    def test_valueset_workflow_status_description_url(self):
        assert VALUESET_WORKFLOW_STATUS_DESCRIPTION_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-workflowStatusDescription'

    def test_codesystem_use_markdown_url(self):
        assert CODESYSTEM_USE_MARKDOWN_URL == 'http://hl7.org/fhir/StructureDefinition/codesystem-use-markdown'

    def test_valueset_system_title_url(self):
        assert VALUESET_SYSTEM_TITLE_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-systemTitle'

    def test_questionnaire_usage_mode_url(self):
        assert QUESTIONNAIRE_USAGE_MODE_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-usageMode'

    def test_open_ehr_administration_url(self):
        assert OPEN_EHR_ADMINISTRATION_URL == 'http://hl7.org/fhir/StructureDefinition/openEHR-administration'

    def test_auditevent_encrypted_url(self):
        assert AUDITEVENT_ENCRYPTED_URL == 'http://hl7.org/fhir/StructureDefinition/auditevent-Encrypted'

    def test_workflow_complies_with_url(self):
        assert WORKFLOW_COMPLIES_WITH_URL == 'http://hl7.org/fhir/StructureDefinition/workflow-compliesWith'

    def test_structuredefinition_table_name_url(self):
        assert STRUCTUREDEFINITION_TABLE_NAME_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-table-name'

    def test_artifact_date_url(self):
        assert ARTIFACT_DATE_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-date'

    def test_capabilities_url(self):
        assert CAPABILITIES_URL == 'http://fhir-registry.smarthealthit.org/StructureDefinition/capabilities'

    def test_request_status_reason_url(self):
        assert REQUEST_STATUS_REASON_URL == 'http://hl7.org/fhir/StructureDefinition/request-statusReason'

    def test_artifact_status_url(self):
        assert ARTIFACT_STATUS_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-status'

    def test_valueset_extensible_url(self):
        assert VALUESET_EXTENSIBLE_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-extensible'

    def test_procedure_target_body_structure_url(self):
        assert PROCEDURE_TARGET_BODY_STRUCTURE_URL == 'http://hl7.org/fhir/StructureDefinition/procedure-targetBodyStructure'

    def test_capabilitystatement_websocket_url(self):
        assert CAPABILITYSTATEMENT_WEBSOCKET_URL == 'http://hl7.org/fhir/StructureDefinition/capabilitystatement-websocket'

    def test_metadataresource_publish_date_url(self):
        assert METADATARESOURCE_PUBLISH_DATE_URL == 'http://hl7.org/fhir/StructureDefinition/metadataresource-publish-date'

    def test_codesystem_concept_comments_url(self):
        assert CODESYSTEM_CONCEPT_COMMENTS_URL == 'http://hl7.org/fhir/StructureDefinition/codesystem-concept-comments'

    def test_questionnaire_reference_profile_url(self):
        assert QUESTIONNAIRE_REFERENCE_PROFILE_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-referenceProfile'

    def test_questionnaireresponse_attester_url(self):
        assert QUESTIONNAIRERESPONSE_ATTESTER_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaireresponse-attester'

    def test_coding_sctdescid_url(self):
        assert CODING_SCTDESCID_URL == 'http://hl7.org/fhir/StructureDefinition/coding-sctdescid'

    def test_entry_format_url(self):
        assert ENTRY_FORMAT_URL == 'http://hl7.org/fhir/StructureDefinition/entryFormat'

    def test_questionnaire_option_prefix_url(self):
        assert QUESTIONNAIRE_OPTION_PREFIX_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-optionPrefix'

    def test_biologicallyderivedproduct_manipulation_url(self):
        assert BIOLOGICALLYDERIVEDPRODUCT_MANIPULATION_URL == 'http://hl7.org/fhir/StructureDefinition/biologicallyderivedproduct-manipulation'

    def test_valueset_other_name_url(self):
        assert VALUESET_OTHER_NAME_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-otherName'

    def test_messageheader_response_request_url(self):
        assert MESSAGEHEADER_RESPONSE_REQUEST_URL == 'http://hl7.org/fhir/StructureDefinition/messageheader-response-request'

    def test_organizationaffiliation_primary_ind_url(self):
        assert ORGANIZATIONAFFILIATION_PRIMARY_IND_URL == 'http://hl7.org/fhir/StructureDefinition/organizationaffiliation-primaryInd'

    def test_resource_instance_name_url(self):
        assert RESOURCE_INSTANCE_NAME_URL == 'http://hl7.org/fhir/StructureDefinition/resource-instance-name'

    def test_auditevent_number_of_instances_url(self):
        assert AUDITEVENT_NUMBER_OF_INSTANCES_URL == 'http://hl7.org/fhir/StructureDefinition/auditevent-NumberOfInstances'

    def test_procedure_incision_date_time_url(self):
        assert PROCEDURE_INCISION_DATE_TIME_URL == 'http://hl7.org/fhir/StructureDefinition/procedure-incisionDateTime'

    def test_artifact_version_policy_url(self):
        assert ARTIFACT_VERSION_POLICY_URL == 'http://hl7.org/fhir/StructureDefinition/artifact-versionPolicy'

    def test_coding_purpose_url(self):
        assert CODING_PURPOSE_URL == 'http://hl7.org/fhir/StructureDefinition/coding-purpose'

    def test_patient_interpreter_required_url(self):
        assert PATIENT_INTERPRETER_REQUIRED_URL == 'http://hl7.org/fhir/StructureDefinition/patient-interpreterRequired'

    def test_consent_research_study_context_url(self):
        assert CONSENT_RESEARCH_STUDY_CONTEXT_URL == 'http://hl7.org/fhir/StructureDefinition/consent-ResearchStudyContext'

    def test_workflow_shall_comply_with_url(self):
        assert WORKFLOW_SHALL_COMPLY_WITH_URL == 'http://hl7.org/fhir/StructureDefinition/workflow-shallComplyWith'

    def test_structuredefinition_fmm_support_url(self):
        assert STRUCTUREDEFINITION_FMM_SUPPORT_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-fmm-support'

    def test_max_size_url(self):
        assert MAX_SIZE_URL == 'http://hl7.org/fhir/StructureDefinition/maxSize'

    def test_individual_recorded_sex_or_gender_url(self):
        assert INDIVIDUAL_RECORDED_SEX_OR_GENDER_URL == 'http://hl7.org/fhir/StructureDefinition/individual-recordedSexOrGender'

    def test_goal_relationship_url(self):
        assert GOAL_RELATIONSHIP_URL == 'http://hl7.org/fhir/StructureDefinition/goal-relationship'

    def test_valueset_rules_text_url(self):
        assert VALUESET_RULES_TEXT_URL == 'http://hl7.org/fhir/StructureDefinition/valueset-rules-text'

    def test_event_location_url(self):
        assert EVENT_LOCATION_URL == 'http://hl7.org/fhir/StructureDefinition/event-location'

    def test_structuredefinition_applicable_version_url(self):
        assert STRUCTUREDEFINITION_APPLICABLE_VERSION_URL == 'http://hl7.org/fhir/StructureDefinition/structuredefinition-applicable-version'

    def test_codesystem_map_url(self):
        assert CODESYSTEM_MAP_URL == 'http://hl7.org/fhir/StructureDefinition/codesystem-map'

    def test_questionnaire_slider_step_value_url(self):
        assert QUESTIONNAIRE_SLIDER_STEP_VALUE_URL == 'http://hl7.org/fhir/StructureDefinition/questionnaire-sliderStepValue'

    def test_cqf_part_of_url(self):
        assert CQF_PART_OF_URL == 'http://hl7.org/fhir/StructureDefinition/cqf-partOf'

    def test_operationdefinition_profile_url(self):
        assert OPERATIONDEFINITION_PROFILE_URL == 'http://hl7.org/fhir/StructureDefinition/operationdefinition-profile'


class TestPropertyAccess:

    def test_account_workflow_release_date_roundtrip(self):
        r = Account()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_activitydefinition_artifact_is_owned_roundtrip(self):
        r = ActivityDefinition()
        r.artifact_is_owned = "test-value"
        result = r.artifact_is_owned
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_activitydefinition_cqf_target_invariant_roundtrip(self):
        r = ActivityDefinition()
        r.cqf_target_invariant = "test-value"
        result = r.cqf_target_invariant
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_activitydefinition_target_constraint_roundtrip(self):
        r = ActivityDefinition()
        r.target_constraint = "test-value"
        result = r.target_constraint
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_activitydefinition_replaces_roundtrip(self):
        r = ActivityDefinition()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_activitydefinition_variable_roundtrip(self):
        r = ActivityDefinition()
        r.variable = "test-value"
        result = r.variable
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_activitydefinition_workflow_shall_comply_with_roundtrip(self):
        r = ActivityDefinition()
        r.workflow_shall_comply_with = "test-value"
        result = r.workflow_shall_comply_with
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_actordefinition_replaces_roundtrip(self):
        r = ActorDefinition()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_post_box_roundtrip(self):
        r = Address()
        r.iso21090_adxp_post_box = "test-value"
        result = r.iso21090_adxp_post_box
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_extended_contact_availability_roundtrip(self):
        r = Address()
        r.extended_contact_availability = "test-value"
        result = r.extended_contact_availability
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_street_name_roundtrip(self):
        r = Address()
        r.iso21090_adxp_street_name = "test-value"
        result = r.iso21090_adxp_street_name
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_unit_id_roundtrip(self):
        r = Address()
        r.iso21090_adxp_unit_id = "test-value"
        result = r.iso21090_adxp_unit_id
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_address_official_roundtrip(self):
        r = Address()
        r.address_official = "test-value"
        result = r.address_official
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_street_name_base_roundtrip(self):
        r = Address()
        r.iso21090_adxp_street_name_base = "test-value"
        result = r.iso21090_adxp_street_name_base
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_unit_type_roundtrip(self):
        r = Address()
        r.iso21090_adxp_unit_type = "test-value"
        result = r.iso21090_adxp_unit_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_street_name_type_roundtrip(self):
        r = Address()
        r.iso21090_adxp_street_name_type = "test-value"
        result = r.iso21090_adxp_street_name_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_confidential_roundtrip(self):
        r = Address()
        r.confidential = "test-value"
        result = r.confidential
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_additional_locator_roundtrip(self):
        r = Address()
        r.iso21090_adxp_additional_locator = "test-value"
        result = r.iso21090_adxp_additional_locator
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_language_roundtrip(self):
        r = Address()
        r.language = "test-value"
        result = r.language
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_cqf_is_empty_list_roundtrip(self):
        r = Address()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_geolocation_roundtrip(self):
        r = Address()
        r.geolocation = "test-value"
        result = r.geolocation
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_house_number_roundtrip(self):
        r = Address()
        r.iso21090_adxp_house_number = "test-value"
        result = r.iso21090_adxp_house_number
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_no_fixed_address_roundtrip(self):
        r = Address()
        r.no_fixed_address = "test-value"
        result = r.no_fixed_address
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_delivery_mode_identifier_roundtrip(self):
        r = Address()
        r.iso21090_adxp_delivery_mode_identifier = "test-value"
        result = r.iso21090_adxp_delivery_mode_identifier
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_delivery_installation_area_roundtrip(self):
        r = Address()
        r.iso21090_adxp_delivery_installation_area = "test-value"
        result = r.iso21090_adxp_delivery_installation_area
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_delivery_address_line_roundtrip(self):
        r = Address()
        r.iso21090_adxp_delivery_address_line = "test-value"
        result = r.iso21090_adxp_delivery_address_line
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_delivery_installation_qualifier_roundtrip(self):
        r = Address()
        r.iso21090_adxp_delivery_installation_qualifier = "test-value"
        result = r.iso21090_adxp_delivery_installation_qualifier
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_street_address_line_roundtrip(self):
        r = Address()
        r.iso21090_adxp_street_address_line = "test-value"
        result = r.iso21090_adxp_street_address_line
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_care_of_roundtrip(self):
        r = Address()
        r.iso21090_adxp_care_of = "test-value"
        result = r.iso21090_adxp_care_of
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_delivery_mode_roundtrip(self):
        r = Address()
        r.iso21090_adxp_delivery_mode = "test-value"
        result = r.iso21090_adxp_delivery_mode
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_house_number_numeric_roundtrip(self):
        r = Address()
        r.iso21090_adxp_house_number_numeric = "test-value"
        result = r.iso21090_adxp_house_number_numeric
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_delimiter_roundtrip(self):
        r = Address()
        r.iso21090_adxp_delimiter = "test-value"
        result = r.iso21090_adxp_delimiter
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_delivery_installation_type_roundtrip(self):
        r = Address()
        r.iso21090_adxp_delivery_installation_type = "test-value"
        result = r.iso21090_adxp_delivery_installation_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_building_number_suffix_roundtrip(self):
        r = Address()
        r.iso21090_adxp_building_number_suffix = "test-value"
        result = r.iso21090_adxp_building_number_suffix
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_preferred_roundtrip(self):
        r = Address()
        r.iso21090_preferred = "test-value"
        result = r.iso21090_preferred
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_ad_use_roundtrip(self):
        r = Address()
        r.iso21090_ad_use = "test-value"
        result = r.iso21090_ad_use
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_precinct_roundtrip(self):
        r = Address()
        r.iso21090_adxp_precinct = "test-value"
        result = r.iso21090_adxp_precinct
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_direction_roundtrip(self):
        r = Address()
        r.iso21090_adxp_direction = "test-value"
        result = r.iso21090_adxp_direction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_iso21090_adxp_census_tract_roundtrip(self):
        r = Address()
        r.iso21090_adxp_census_tract = "test-value"
        result = r.iso21090_adxp_census_tract
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_adverseevent_workflow_episode_of_care_roundtrip(self):
        r = AdverseEvent()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_age_cqf_is_empty_list_roundtrip(self):
        r = Age()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_allergyintolerance_allergyintolerance_duration_roundtrip(self):
        r = AllergyIntolerance()
        r.allergyintolerance_duration = "test-value"
        result = r.allergyintolerance_duration
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_allergyintolerance_open_ehr_exposure_description_roundtrip(self):
        r = AllergyIntolerance()
        r.open_ehr_exposure_description = "test-value"
        result = r.open_ehr_exposure_description
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_allergyintolerance_open_ehr_careplan_roundtrip(self):
        r = AllergyIntolerance()
        r.open_ehr_careplan = "test-value"
        result = r.open_ehr_careplan
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_allergyintolerance_open_ehr_location_roundtrip(self):
        r = AllergyIntolerance()
        r.open_ehr_location = "test-value"
        result = r.open_ehr_location
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_allergyintolerance_allergyintolerance_substance_exposure_risk_roundtrip(self):
        r = AllergyIntolerance()
        r.allergyintolerance_substance_exposure_risk = "test-value"
        result = r.allergyintolerance_substance_exposure_risk
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_allergyintolerance_allergyintolerance_abatement_roundtrip(self):
        r = AllergyIntolerance()
        r.allergyintolerance_abatement = "test-value"
        result = r.allergyintolerance_abatement
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_allergyintolerance_allergyintolerance_reason_refuted_roundtrip(self):
        r = AllergyIntolerance()
        r.allergyintolerance_reason_refuted = "test-value"
        result = r.allergyintolerance_reason_refuted
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_allergyintolerance_open_ehr_exposure_duration_roundtrip(self):
        r = AllergyIntolerance()
        r.open_ehr_exposure_duration = "test-value"
        result = r.open_ehr_exposure_duration
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_allergyintolerance_allergyintolerance_resolution_age_roundtrip(self):
        r = AllergyIntolerance()
        r.allergyintolerance_resolution_age = "test-value"
        result = r.allergyintolerance_resolution_age
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_allergyintolerance_open_ehr_management_roundtrip(self):
        r = AllergyIntolerance()
        r.open_ehr_management = "test-value"
        result = r.open_ehr_management
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_allergyintolerance_open_ehr_exposure_date_roundtrip(self):
        r = AllergyIntolerance()
        r.open_ehr_exposure_date = "test-value"
        result = r.open_ehr_exposure_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_allergyintolerance_condition_asserted_date_roundtrip(self):
        r = AllergyIntolerance()
        r.condition_asserted_date = "test-value"
        result = r.condition_asserted_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_allergyintolerance_allergyintolerance_certainty_roundtrip(self):
        r = AllergyIntolerance()
        r.allergyintolerance_certainty = "test-value"
        result = r.allergyintolerance_certainty
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_allergyintolerance_allergyintolerance_asserted_date_roundtrip(self):
        r = AllergyIntolerance()
        r.allergyintolerance_asserted_date = "test-value"
        result = r.allergyintolerance_asserted_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_allergyintolerance_open_ehr_administration_roundtrip(self):
        r = AllergyIntolerance()
        r.open_ehr_administration = "test-value"
        result = r.open_ehr_administration
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_annotation_language_roundtrip(self):
        r = Annotation()
        r.language = "test-value"
        result = r.language
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_annotation_cqf_is_empty_list_roundtrip(self):
        r = Annotation()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_annotation_annotation_type_roundtrip(self):
        r = Annotation()
        r.annotation_type = "test-value"
        result = r.annotation_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_appointment_workflow_release_date_roundtrip(self):
        r = Appointment()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_appointment_workflow_episode_of_care_roundtrip(self):
        r = Appointment()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_artifactassessment_workflow_release_date_roundtrip(self):
        r = ArtifactAssessment()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_attachment_cqf_is_empty_list_roundtrip(self):
        r = Attachment()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_auditevent_auditevent_participant_object_contains_study_roundtrip(self):
        r = AuditEvent()
        r.auditevent_participant_object_contains_study = "test-value"
        result = r.auditevent_participant_object_contains_study
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_auditevent_auditevent_mpps_roundtrip(self):
        r = AuditEvent()
        r.auditevent_mpps = "test-value"
        result = r.auditevent_mpps
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_auditevent_auditevent_lifecycle_roundtrip(self):
        r = AuditEvent()
        r.auditevent_lifecycle = "test-value"
        result = r.auditevent_lifecycle
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_auditevent_auditevent_anonymized_roundtrip(self):
        r = AuditEvent()
        r.auditevent_anonymized = "test-value"
        result = r.auditevent_anonymized
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_auditevent_auditevent_instance_roundtrip(self):
        r = AuditEvent()
        r.auditevent_instance = "test-value"
        result = r.auditevent_instance
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_auditevent_auditevent_accession_roundtrip(self):
        r = AuditEvent()
        r.auditevent_accession = "test-value"
        result = r.auditevent_accession
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_auditevent_auditevent_on_behalf_of_roundtrip(self):
        r = AuditEvent()
        r.auditevent_on_behalf_of = "test-value"
        result = r.auditevent_on_behalf_of
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_auditevent_auditevent_sopclass_roundtrip(self):
        r = AuditEvent()
        r.auditevent_sopclass = "test-value"
        result = r.auditevent_sopclass
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_auditevent_auditevent_alternative_user_id_roundtrip(self):
        r = AuditEvent()
        r.auditevent_alternative_user_id = "test-value"
        result = r.auditevent_alternative_user_id
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_auditevent_auditevent_encrypted_roundtrip(self):
        r = AuditEvent()
        r.auditevent_encrypted = "test-value"
        result = r.auditevent_encrypted
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_auditevent_auditevent_number_of_instances_roundtrip(self):
        r = AuditEvent()
        r.auditevent_number_of_instances = "test-value"
        result = r.auditevent_number_of_instances
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_base__datatype_roundtrip(self):
        r = Base()
        r._datatype = "test-value"
        result = r._datatype
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_cqf_initiating_organization_roundtrip(self):
        r = Basic()
        r.cqf_initiating_organization = "test-value"
        result = r.cqf_initiating_organization
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_cqf_initiating_person_roundtrip(self):
        r = Basic()
        r.cqf_initiating_person = "test-value"
        result = r.cqf_initiating_person
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_cqf_system_user_language_roundtrip(self):
        r = Basic()
        r.cqf_system_user_language = "test-value"
        result = r.cqf_system_user_language
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_cqf_recipient_type_roundtrip(self):
        r = Basic()
        r.cqf_recipient_type = "test-value"
        result = r.cqf_recipient_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_cqf_encounter_class_roundtrip(self):
        r = Basic()
        r.cqf_encounter_class = "test-value"
        result = r.cqf_encounter_class
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_cqf_recipient_language_roundtrip(self):
        r = Basic()
        r.cqf_recipient_language = "test-value"
        result = r.cqf_recipient_language
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_workflow_episode_of_care_roundtrip(self):
        r = Basic()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_artifactassessment_content_roundtrip(self):
        r = Basic()
        r.artifactassessment_content = "test-value"
        result = r.artifactassessment_content
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_cqf_receiving_organization_roundtrip(self):
        r = Basic()
        r.cqf_receiving_organization = "test-value"
        result = r.cqf_receiving_organization
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_cqf_receiving_person_roundtrip(self):
        r = Basic()
        r.cqf_receiving_person = "test-value"
        result = r.cqf_receiving_person
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_cqf_system_user_type_roundtrip(self):
        r = Basic()
        r.cqf_system_user_type = "test-value"
        result = r.cqf_system_user_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_cqf_encounter_type_roundtrip(self):
        r = Basic()
        r.cqf_encounter_type = "test-value"
        result = r.cqf_encounter_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_cqf_system_user_task_context_roundtrip(self):
        r = Basic()
        r.cqf_system_user_task_context = "test-value"
        result = r.cqf_system_user_task_context
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_biologicallyderivedproduct_biologicallyderivedproduct_collection_procedure_roundtrip(self):
        r = BiologicallyDerivedProduct()
        r.biologicallyderivedproduct_collection_procedure = "test-value"
        result = r.biologicallyderivedproduct_collection_procedure
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_biologicallyderivedproduct_biologicallyderivedproduct_processing_roundtrip(self):
        r = BiologicallyDerivedProduct()
        r.biologicallyderivedproduct_processing = "test-value"
        result = r.biologicallyderivedproduct_processing
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_biologicallyderivedproduct_biologicallyderivedproduct_manipulation_roundtrip(self):
        r = BiologicallyDerivedProduct()
        r.biologicallyderivedproduct_manipulation = "test-value"
        result = r.biologicallyderivedproduct_manipulation
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_bundle_http_response_header_roundtrip(self):
        r = Bundle()
        r.http_response_header = "test-value"
        result = r.http_response_header
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_bundle_location_distance_roundtrip(self):
        r = Bundle()
        r.location_distance = "test-value"
        result = r.location_distance
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_bundle_match_grade_roundtrip(self):
        r = Bundle()
        r.match_grade = "test-value"
        result = r.match_grade
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_canonicalresource_structuredefinition_standards_status_roundtrip(self):
        r = CanonicalResource()
        r.structuredefinition_standards_status = "test-value"
        result = r.structuredefinition_standards_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_canonicalresource_structuredefinition_normative_version_roundtrip(self):
        r = CanonicalResource()
        r.structuredefinition_normative_version = "test-value"
        result = r.structuredefinition_normative_version
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_canonicalresource_canonicalresource_short_description_roundtrip(self):
        r = CanonicalResource()
        r.canonicalresource_short_description = "test-value"
        result = r.canonicalresource_short_description
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_capabilitystatement_resource_approval_date_roundtrip(self):
        r = CapabilityStatement()
        r.resource_approval_date = "test-value"
        result = r.resource_approval_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_capabilitystatement_capabilitystatement_search_mode_roundtrip(self):
        r = CapabilityStatement()
        r.capabilitystatement_search_mode = "test-value"
        result = r.capabilitystatement_search_mode
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_capabilitystatement_resource_last_review_date_roundtrip(self):
        r = CapabilityStatement()
        r.resource_last_review_date = "test-value"
        result = r.resource_last_review_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_capabilitystatement_capabilitystatement_search_parameter_use_roundtrip(self):
        r = CapabilityStatement()
        r.capabilitystatement_search_parameter_use = "test-value"
        result = r.capabilitystatement_search_parameter_use
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_capabilitystatement_oauth_uris_roundtrip(self):
        r = CapabilityStatement()
        r.oauth_uris = "test-value"
        result = r.oauth_uris
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_capabilitystatement_capabilitystatement_expectation_roundtrip(self):
        r = CapabilityStatement()
        r.capabilitystatement_expectation = "test-value"
        result = r.capabilitystatement_expectation
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_capabilitystatement_capabilitystatement_declared_profile_roundtrip(self):
        r = CapabilityStatement()
        r.capabilitystatement_declared_profile = "test-value"
        result = r.capabilitystatement_declared_profile
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_capabilitystatement_resource_effective_period_roundtrip(self):
        r = CapabilityStatement()
        r.resource_effective_period = "test-value"
        result = r.resource_effective_period
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_capabilitystatement_cqf_supported_cql_version_roundtrip(self):
        r = CapabilityStatement()
        r.cqf_supported_cql_version = "test-value"
        result = r.cqf_supported_cql_version
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_capabilitystatement_capabilitystatement_prohibited_roundtrip(self):
        r = CapabilityStatement()
        r.capabilitystatement_prohibited = "test-value"
        result = r.capabilitystatement_prohibited
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_capabilitystatement_replaces_roundtrip(self):
        r = CapabilityStatement()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_capabilitystatement_capabilitystatement_search_parameter_combination_roundtrip(self):
        r = CapabilityStatement()
        r.capabilitystatement_search_parameter_combination = "test-value"
        result = r.capabilitystatement_search_parameter_combination
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_capabilitystatement_capabilitystatement_supported_system_roundtrip(self):
        r = CapabilityStatement()
        r.capabilitystatement_supported_system = "test-value"
        result = r.capabilitystatement_supported_system
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_capabilitystatement_capabilities_roundtrip(self):
        r = CapabilityStatement()
        r.capabilities = "test-value"
        result = r.capabilities
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_capabilitystatement_capabilitystatement_websocket_roundtrip(self):
        r = CapabilityStatement()
        r.capabilitystatement_websocket = "test-value"
        result = r.capabilitystatement_websocket
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_careplan_workflow_triggered_by_roundtrip(self):
        r = CarePlan()
        r.workflow_triggered_by = "test-value"
        result = r.workflow_triggered_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_careplan_workflow_generated_from_roundtrip(self):
        r = CarePlan()
        r.workflow_generated_from = "test-value"
        result = r.workflow_generated_from
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_careplan_workflow_protective_factor_roundtrip(self):
        r = CarePlan()
        r.workflow_protective_factor = "test-value"
        result = r.workflow_protective_factor
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_careplan_workflow_release_date_roundtrip(self):
        r = CarePlan()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_careplan_request_relevant_history_roundtrip(self):
        r = CarePlan()
        r.request_relevant_history = "test-value"
        result = r.request_relevant_history
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_careplan_workflow_episode_of_care_roundtrip(self):
        r = CarePlan()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_careplan_careplan_activity_title_roundtrip(self):
        r = CarePlan()
        r.careplan_activity_title = "test-value"
        result = r.careplan_activity_title
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_careplan_workflow_barrier_roundtrip(self):
        r = CarePlan()
        r.workflow_barrier = "test-value"
        result = r.workflow_barrier
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_careplan_workflow_complies_with_roundtrip(self):
        r = CarePlan()
        r.workflow_complies_with = "test-value"
        result = r.workflow_complies_with
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_careteam_careteam_alias_roundtrip(self):
        r = CareTeam()
        r.careteam_alias = "test-value"
        result = r.careteam_alias
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_chargeitem_event_based_on_roundtrip(self):
        r = ChargeItem()
        r.event_based_on = "test-value"
        result = r.event_based_on
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_chargeitem_workflow_episode_of_care_roundtrip(self):
        r = ChargeItem()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_chargeitemdefinition_replaces_roundtrip(self):
        r = ChargeItemDefinition()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_citation_citation_society_affiliation_roundtrip(self):
        r = Citation()
        r.citation_society_affiliation = "test-value"
        result = r.citation_society_affiliation
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_citation_replaces_roundtrip(self):
        r = Citation()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_clinicalimpression_event_based_on_roundtrip(self):
        r = ClinicalImpression()
        r.event_based_on = "test-value"
        result = r.event_based_on
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_clinicalimpression_workflow_release_date_roundtrip(self):
        r = ClinicalImpression()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_clinicalimpression_workflow_episode_of_care_roundtrip(self):
        r = ClinicalImpression()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_codesystem_warning_roundtrip(self):
        r = CodeSystem()
        r.codesystem_warning = "test-value"
        result = r.codesystem_warning
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_resource_approval_date_roundtrip(self):
        r = CodeSystem()
        r.resource_approval_date = "test-value"
        result = r.resource_approval_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_codesystem_alternate_roundtrip(self):
        r = CodeSystem()
        r.codesystem_alternate = "test-value"
        result = r.codesystem_alternate
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_codesystem_history_roundtrip(self):
        r = CodeSystem()
        r.codesystem_history = "test-value"
        result = r.codesystem_history
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_terminology_resource_identifier_metadata_roundtrip(self):
        r = CodeSystem()
        r.terminology_resource_identifier_metadata = "test-value"
        result = r.terminology_resource_identifier_metadata
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_codesystem_properties_mode_roundtrip(self):
        r = CodeSystem()
        r.codesystem_properties_mode = "test-value"
        result = r.codesystem_properties_mode
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_codesystem_trusted_expansion_roundtrip(self):
        r = CodeSystem()
        r.codesystem_trusted_expansion = "test-value"
        result = r.codesystem_trusted_expansion
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_codesystem_other_name_roundtrip(self):
        r = CodeSystem()
        r.codesystem_other_name = "test-value"
        result = r.codesystem_other_name
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_resource_last_review_date_roundtrip(self):
        r = CodeSystem()
        r.resource_last_review_date = "test-value"
        result = r.resource_last_review_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_codesystem_authoritative_source_roundtrip(self):
        r = CodeSystem()
        r.codesystem_authoritative_source = "test-value"
        result = r.codesystem_authoritative_source
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_valueset_special_status_roundtrip(self):
        r = CodeSystem()
        r.valueset_special_status = "test-value"
        result = r.valueset_special_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_structuredefinition_standards_status_roundtrip(self):
        r = CodeSystem()
        r.structuredefinition_standards_status = "test-value"
        result = r.structuredefinition_standards_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_resource_effective_period_roundtrip(self):
        r = CodeSystem()
        r.resource_effective_period = "test-value"
        result = r.resource_effective_period
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_codesystem_label_roundtrip(self):
        r = CodeSystem()
        r.codesystem_label = "test-value"
        result = r.codesystem_label
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_codesystem_concept_order_roundtrip(self):
        r = CodeSystem()
        r.codesystem_concept_order = "test-value"
        result = r.codesystem_concept_order
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_replaces_roundtrip(self):
        r = CodeSystem()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_codesystem_key_word_roundtrip(self):
        r = CodeSystem()
        r.codesystem_key_word = "test-value"
        result = r.codesystem_key_word
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_codesystem_source_reference_roundtrip(self):
        r = CodeSystem()
        r.codesystem_source_reference = "test-value"
        result = r.codesystem_source_reference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_codesystem_workflow_status_roundtrip(self):
        r = CodeSystem()
        r.codesystem_workflow_status = "test-value"
        result = r.codesystem_workflow_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_codesystem_replacedby_roundtrip(self):
        r = CodeSystem()
        r.codesystem_replacedby = "test-value"
        result = r.codesystem_replacedby
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_codesystem_usage_roundtrip(self):
        r = CodeSystem()
        r.codesystem_usage = "test-value"
        result = r.codesystem_usage
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_codesystem_use_markdown_roundtrip(self):
        r = CodeSystem()
        r.codesystem_use_markdown = "test-value"
        result = r.codesystem_use_markdown
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_codesystem_concept_comments_roundtrip(self):
        r = CodeSystem()
        r.codesystem_concept_comments = "test-value"
        result = r.codesystem_concept_comments
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_coding_sctdescid_roundtrip(self):
        r = CodeSystem()
        r.coding_sctdescid = "test-value"
        result = r.coding_sctdescid
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codesystem_codesystem_map_roundtrip(self):
        r = CodeSystem()
        r.codesystem_map = "test-value"
        result = r.codesystem_map
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codeableconcept_cqf_is_empty_list_roundtrip(self):
        r = CodeableConcept()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_codeableconcept_cqf_not_done_value_set_roundtrip(self):
        r = CodeableConcept()
        r.cqf_not_done_value_set = "test-value"
        result = r.cqf_not_done_value_set
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_coding_cqf_is_empty_list_roundtrip(self):
        r = Coding()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_coding_valueset_reference_roundtrip(self):
        r = Coding()
        r.valueset_reference = "test-value"
        result = r.valueset_reference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_coding_item_weight_roundtrip(self):
        r = Coding()
        r.item_weight = "test-value"
        result = r.item_weight
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_coding_coding_conformance_roundtrip(self):
        r = Coding()
        r.coding_conformance = "test-value"
        result = r.coding_conformance
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_coding_coding_sctdescid_roundtrip(self):
        r = Coding()
        r.coding_sctdescid = "test-value"
        result = r.coding_sctdescid
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_coding_coding_purpose_roundtrip(self):
        r = Coding()
        r.coding_purpose = "test-value"
        result = r.coding_purpose
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_communication_workflow_triggered_by_roundtrip(self):
        r = Communication()
        r.workflow_triggered_by = "test-value"
        result = r.workflow_triggered_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_communication_communication_media_roundtrip(self):
        r = Communication()
        r.communication_media = "test-value"
        result = r.communication_media
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_communication_workflow_release_date_roundtrip(self):
        r = Communication()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_communication_workflow_episode_of_care_roundtrip(self):
        r = Communication()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_communication_workflow_adheres_to_roundtrip(self):
        r = Communication()
        r.workflow_adheres_to = "test-value"
        result = r.workflow_adheres_to
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_communicationrequest_workflow_triggered_by_roundtrip(self):
        r = CommunicationRequest()
        r.workflow_triggered_by = "test-value"
        result = r.workflow_triggered_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_communicationrequest_workflow_generated_from_roundtrip(self):
        r = CommunicationRequest()
        r.workflow_generated_from = "test-value"
        result = r.workflow_generated_from
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_communicationrequest_workflow_protective_factor_roundtrip(self):
        r = CommunicationRequest()
        r.workflow_protective_factor = "test-value"
        result = r.workflow_protective_factor
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_communicationrequest_workflow_release_date_roundtrip(self):
        r = CommunicationRequest()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_communicationrequest_request_relevant_history_roundtrip(self):
        r = CommunicationRequest()
        r.request_relevant_history = "test-value"
        result = r.request_relevant_history
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_communicationrequest_workflow_supporting_info_roundtrip(self):
        r = CommunicationRequest()
        r.workflow_supporting_info = "test-value"
        result = r.workflow_supporting_info
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_communicationrequest_workflow_episode_of_care_roundtrip(self):
        r = CommunicationRequest()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_communicationrequest_communicationrequest_initiating_location_roundtrip(self):
        r = CommunicationRequest()
        r.communicationrequest_initiating_location = "test-value"
        result = r.communicationrequest_initiating_location
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_communicationrequest_workflow_barrier_roundtrip(self):
        r = CommunicationRequest()
        r.workflow_barrier = "test-value"
        result = r.workflow_barrier
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_communicationrequest_workflow_complies_with_roundtrip(self):
        r = CommunicationRequest()
        r.workflow_complies_with = "test-value"
        result = r.workflow_complies_with
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_communicationrequest_workflow_shall_comply_with_roundtrip(self):
        r = CommunicationRequest()
        r.workflow_shall_comply_with = "test-value"
        result = r.workflow_shall_comply_with
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_compartmentdefinition_resource_approval_date_roundtrip(self):
        r = CompartmentDefinition()
        r.resource_approval_date = "test-value"
        result = r.resource_approval_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_compartmentdefinition_resource_last_review_date_roundtrip(self):
        r = CompartmentDefinition()
        r.resource_last_review_date = "test-value"
        result = r.resource_last_review_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_compartmentdefinition_resource_effective_period_roundtrip(self):
        r = CompartmentDefinition()
        r.resource_effective_period = "test-value"
        result = r.resource_effective_period
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_compartmentdefinition_replaces_roundtrip(self):
        r = CompartmentDefinition()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_composition_workflow_research_study_roundtrip(self):
        r = Composition()
        r.workflow_research_study = "test-value"
        result = r.workflow_research_study
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_composition_composition_section_subject_roundtrip(self):
        r = Composition()
        r.composition_section_subject = "test-value"
        result = r.composition_section_subject
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_composition_composition_clinicaldocument_version_number_roundtrip(self):
        r = Composition()
        r.composition_clinicaldocument_version_number = "test-value"
        result = r.composition_clinicaldocument_version_number
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_composition_note_roundtrip(self):
        r = Composition()
        r.note = "test-value"
        result = r.note
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_composition_event_based_on_roundtrip(self):
        r = Composition()
        r.event_based_on = "test-value"
        result = r.event_based_on
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_composition_cqm_validity_period_roundtrip(self):
        r = Composition()
        r.cqm_validity_period = "test-value"
        result = r.cqm_validity_period
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_composition_workflow_episode_of_care_roundtrip(self):
        r = Composition()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_conceptmap_resource_approval_date_roundtrip(self):
        r = ConceptMap()
        r.resource_approval_date = "test-value"
        result = r.resource_approval_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_conceptmap_terminology_resource_identifier_metadata_roundtrip(self):
        r = ConceptMap()
        r.terminology_resource_identifier_metadata = "test-value"
        result = r.terminology_resource_identifier_metadata
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_conceptmap_resource_last_review_date_roundtrip(self):
        r = ConceptMap()
        r.resource_last_review_date = "test-value"
        result = r.resource_last_review_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_conceptmap_resource_effective_period_roundtrip(self):
        r = ConceptMap()
        r.resource_effective_period = "test-value"
        result = r.resource_effective_period
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_conceptmap_workflow_related_artifact_roundtrip(self):
        r = ConceptMap()
        r.workflow_related_artifact = "test-value"
        result = r.workflow_related_artifact
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_conceptmap_concept_bidirectional_roundtrip(self):
        r = ConceptMap()
        r.concept_bidirectional = "test-value"
        result = r.concept_bidirectional
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_conceptmap_replaces_roundtrip(self):
        r = ConceptMap()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_condition_workflow_triggered_by_roundtrip(self):
        r = Condition()
        r.workflow_triggered_by = "test-value"
        result = r.workflow_triggered_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_condition_condition_ruled_out_roundtrip(self):
        r = Condition()
        r.condition_ruled_out = "test-value"
        result = r.condition_ruled_out
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_condition_condition_related_roundtrip(self):
        r = Condition()
        r.condition_related = "test-value"
        result = r.condition_related
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_condition_condition_disease_course_roundtrip(self):
        r = Condition()
        r.condition_disease_course = "test-value"
        result = r.condition_disease_course
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_condition_condition_due_to_roundtrip(self):
        r = Condition()
        r.condition_due_to = "test-value"
        result = r.condition_due_to
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_condition_condition_occurred_following_roundtrip(self):
        r = Condition()
        r.condition_occurred_following = "test-value"
        result = r.condition_occurred_following
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_condition_event_part_of_roundtrip(self):
        r = Condition()
        r.event_part_of = "test-value"
        result = r.event_part_of
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_condition_condition_outcome_roundtrip(self):
        r = Condition()
        r.condition_outcome = "test-value"
        result = r.condition_outcome
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_condition_event_based_on_roundtrip(self):
        r = Condition()
        r.event_based_on = "test-value"
        result = r.event_based_on
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_condition_condition_asserted_date_roundtrip(self):
        r = Condition()
        r.condition_asserted_date = "test-value"
        result = r.condition_asserted_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_condition_workflow_episode_of_care_roundtrip(self):
        r = Condition()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_condition_condition_reviewed_roundtrip(self):
        r = Condition()
        r.condition_reviewed = "test-value"
        result = r.condition_reviewed
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_condition_workflow_adheres_to_roundtrip(self):
        r = Condition()
        r.workflow_adheres_to = "test-value"
        result = r.workflow_adheres_to
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_condition_workflow_shall_comply_with_roundtrip(self):
        r = Condition()
        r.workflow_shall_comply_with = "test-value"
        result = r.workflow_shall_comply_with
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_conditiondefinition_replaces_roundtrip(self):
        r = ConditionDefinition()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_consent_consent_transcriber_roundtrip(self):
        r = Consent()
        r.consent_transcriber = "test-value"
        result = r.consent_transcriber
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_consent_event_performer_function_roundtrip(self):
        r = Consent()
        r.event_performer_function = "test-value"
        result = r.event_performer_function
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_consent_workflow_research_study_roundtrip(self):
        r = Consent()
        r.workflow_research_study = "test-value"
        result = r.workflow_research_study
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_consent_event_based_on_roundtrip(self):
        r = Consent()
        r.event_based_on = "test-value"
        result = r.event_based_on
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_consent_consent_notification_endpoint_roundtrip(self):
        r = Consent()
        r.consent_notification_endpoint = "test-value"
        result = r.consent_notification_endpoint
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_consent_workflow_episode_of_care_roundtrip(self):
        r = Consent()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_consent_consent_location_roundtrip(self):
        r = Consent()
        r.consent_location = "test-value"
        result = r.consent_location
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_consent_consent_witness_roundtrip(self):
        r = Consent()
        r.consent_witness = "test-value"
        result = r.consent_witness
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_consent_consent_research_study_context_roundtrip(self):
        r = Consent()
        r.consent_research_study_context = "test-value"
        result = r.consent_research_study_context
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contactdetail_extended_contact_availability_roundtrip(self):
        r = ContactDetail()
        r.extended_contact_availability = "test-value"
        result = r.extended_contact_availability
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contactdetail_cqf_contribution_time_roundtrip(self):
        r = ContactDetail()
        r.cqf_contribution_time = "test-value"
        result = r.cqf_contribution_time
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contactdetail_artifact_contact_detail_reference_roundtrip(self):
        r = ContactDetail()
        r.artifact_contact_detail_reference = "test-value"
        result = r.artifact_contact_detail_reference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contactdetail_cqf_is_empty_list_roundtrip(self):
        r = ContactDetail()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contactdetail_cqf_contact_reference_roundtrip(self):
        r = ContactDetail()
        r.cqf_contact_reference = "test-value"
        result = r.cqf_contact_reference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contactdetail_cqf_contact_address_roundtrip(self):
        r = ContactDetail()
        r.cqf_contact_address = "test-value"
        result = r.cqf_contact_address
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contactpoint_contactpoint_area_roundtrip(self):
        r = ContactPoint()
        r.contactpoint_area = "test-value"
        result = r.contactpoint_area
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contactpoint_confidential_roundtrip(self):
        r = ContactPoint()
        r.confidential = "test-value"
        result = r.confidential
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contactpoint_contactpoint_local_roundtrip(self):
        r = ContactPoint()
        r.contactpoint_local = "test-value"
        result = r.contactpoint_local
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contactpoint_cqf_is_empty_list_roundtrip(self):
        r = ContactPoint()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contactpoint_iso21090_tel_address_roundtrip(self):
        r = ContactPoint()
        r.iso21090_tel_address = "test-value"
        result = r.iso21090_tel_address
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contactpoint_contactpoint_purpose_roundtrip(self):
        r = ContactPoint()
        r.contactpoint_purpose = "test-value"
        result = r.contactpoint_purpose
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contactpoint_contactpoint_extension_roundtrip(self):
        r = ContactPoint()
        r.contactpoint_extension = "test-value"
        result = r.contactpoint_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contactpoint_contactpoint_comment_roundtrip(self):
        r = ContactPoint()
        r.contactpoint_comment = "test-value"
        result = r.contactpoint_comment
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contactpoint_iso21090_preferred_roundtrip(self):
        r = ContactPoint()
        r.iso21090_preferred = "test-value"
        result = r.iso21090_preferred
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contactpoint_contactpoint_country_roundtrip(self):
        r = ContactPoint()
        r.contactpoint_country = "test-value"
        result = r.contactpoint_country
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contract_workflow_release_date_roundtrip(self):
        r = Contract()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_count_cqf_is_empty_list_roundtrip(self):
        r = Count()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_coverage_event_based_on_roundtrip(self):
        r = Coverage()
        r.event_based_on = "test-value"
        result = r.event_based_on
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_datarequirement_cqf_is_selective_roundtrip(self):
        r = DataRequirement()
        r.cqf_is_selective = "test-value"
        result = r.cqf_is_selective
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_datarequirement_cqf_is_empty_list_roundtrip(self):
        r = DataRequirement()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_datarequirement_cqf_fhir_query_pattern_roundtrip(self):
        r = DataRequirement()
        r.cqf_fhir_query_pattern = "test-value"
        result = r.cqf_fhir_query_pattern
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_datarequirement_cqf_value_filter_roundtrip(self):
        r = DataRequirement()
        r.cqf_value_filter = "test-value"
        result = r.cqf_value_filter
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_detectedissue_event_based_on_roundtrip(self):
        r = DetectedIssue()
        r.event_based_on = "test-value"
        result = r.event_based_on
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_detectedissue_workflow_episode_of_care_roundtrip(self):
        r = DetectedIssue()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_device_device_maintenanceresponsibility_roundtrip(self):
        r = Device()
        r.device_maintenanceresponsibility = "test-value"
        result = r.device_maintenanceresponsibility
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_device_device_lastmaintenancetime_roundtrip(self):
        r = Device()
        r.device_lastmaintenancetime = "test-value"
        result = r.device_lastmaintenancetime
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_device_device_implant_status_roundtrip(self):
        r = Device()
        r.device_implant_status = "test-value"
        result = r.device_implant_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_device_device_commercial_brand_roundtrip(self):
        r = Device()
        r.device_commercial_brand = "test-value"
        result = r.device_commercial_brand
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_devicedefinition_device_commercial_brand_roundtrip(self):
        r = DeviceDefinition()
        r.device_commercial_brand = "test-value"
        result = r.device_commercial_brand
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_devicedispense_workflow_release_date_roundtrip(self):
        r = DeviceDispense()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_devicerequest_workflow_triggered_by_roundtrip(self):
        r = DeviceRequest()
        r.workflow_triggered_by = "test-value"
        result = r.workflow_triggered_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_devicerequest_devicerequest_patient_instruction_roundtrip(self):
        r = DeviceRequest()
        r.devicerequest_patient_instruction = "test-value"
        result = r.devicerequest_patient_instruction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_devicerequest_workflow_generated_from_roundtrip(self):
        r = DeviceRequest()
        r.workflow_generated_from = "test-value"
        result = r.workflow_generated_from
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_devicerequest_workflow_follow_on_of_roundtrip(self):
        r = DeviceRequest()
        r.workflow_follow_on_of = "test-value"
        result = r.workflow_follow_on_of
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_devicerequest_workflow_release_date_roundtrip(self):
        r = DeviceRequest()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_devicerequest_workflow_episode_of_care_roundtrip(self):
        r = DeviceRequest()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_devicerequest_procedure_approach_body_structure_roundtrip(self):
        r = DeviceRequest()
        r.procedure_approach_body_structure = "test-value"
        result = r.procedure_approach_body_structure
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_devicerequest_workflow_complies_with_roundtrip(self):
        r = DeviceRequest()
        r.workflow_complies_with = "test-value"
        result = r.workflow_complies_with
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_devicerequest_request_status_reason_roundtrip(self):
        r = DeviceRequest()
        r.request_status_reason = "test-value"
        result = r.request_status_reason
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_deviceusage_workflow_research_study_roundtrip(self):
        r = DeviceUsage()
        r.workflow_research_study = "test-value"
        result = r.workflow_research_study
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_deviceusage_workflow_release_date_roundtrip(self):
        r = DeviceUsage()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_deviceusage_workflow_episode_of_care_roundtrip(self):
        r = DeviceUsage()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_deviceusage_event_status_reason_roundtrip(self):
        r = DeviceUsage()
        r.event_status_reason = "test-value"
        result = r.event_status_reason
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_deviceusage_event_event_history_roundtrip(self):
        r = DeviceUsage()
        r.event_event_history = "test-value"
        result = r.event_event_history
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_deviceusage_procedure_approach_body_structure_roundtrip(self):
        r = DeviceUsage()
        r.procedure_approach_body_structure = "test-value"
        result = r.procedure_approach_body_structure
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_workflow_triggered_by_roundtrip(self):
        r = DiagnosticReport()
        r.workflow_triggered_by = "test-value"
        result = r.workflow_triggered_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_event_performer_function_roundtrip(self):
        r = DiagnosticReport()
        r.event_performer_function = "test-value"
        result = r.event_performer_function
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_diagnostic_report_focus_roundtrip(self):
        r = DiagnosticReport()
        r.diagnostic_report_focus = "test-value"
        result = r.diagnostic_report_focus
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_workflow_research_study_roundtrip(self):
        r = DiagnosticReport()
        r.workflow_research_study = "test-value"
        result = r.workflow_research_study
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_diagnostic_report_risk_roundtrip(self):
        r = DiagnosticReport()
        r.diagnostic_report_risk = "test-value"
        result = r.diagnostic_report_risk
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_diagnostic_report_extends_roundtrip(self):
        r = DiagnosticReport()
        r.diagnostic_report_extends = "test-value"
        result = r.diagnostic_report_extends
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_diagnostic_report_summary_of_roundtrip(self):
        r = DiagnosticReport()
        r.diagnostic_report_summary_of = "test-value"
        result = r.diagnostic_report_summary_of
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_diagnostic_report_workflow_status_roundtrip(self):
        r = DiagnosticReport()
        r.diagnostic_report_workflow_status = "test-value"
        result = r.diagnostic_report_workflow_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_event_part_of_roundtrip(self):
        r = DiagnosticReport()
        r.event_part_of = "test-value"
        result = r.event_part_of
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_workflow_related_artifact_roundtrip(self):
        r = DiagnosticReport()
        r.workflow_related_artifact = "test-value"
        result = r.workflow_related_artifact
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_diagnostic_report_addendum_of_roundtrip(self):
        r = DiagnosticReport()
        r.diagnostic_report_addendum_of = "test-value"
        result = r.diagnostic_report_addendum_of
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_workflow_supporting_info_roundtrip(self):
        r = DiagnosticReport()
        r.workflow_supporting_info = "test-value"
        result = r.workflow_supporting_info
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_diagnostic_report_replaces_roundtrip(self):
        r = DiagnosticReport()
        r.diagnostic_report_replaces = "test-value"
        result = r.diagnostic_report_replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_workflow_episode_of_care_roundtrip(self):
        r = DiagnosticReport()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_event_status_reason_roundtrip(self):
        r = DiagnosticReport()
        r.event_status_reason = "test-value"
        result = r.event_status_reason
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_workflow_reason_roundtrip(self):
        r = DiagnosticReport()
        r.workflow_reason = "test-value"
        result = r.workflow_reason
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_workflow_adheres_to_roundtrip(self):
        r = DiagnosticReport()
        r.workflow_adheres_to = "test-value"
        result = r.workflow_adheres_to
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_event_event_history_roundtrip(self):
        r = DiagnosticReport()
        r.event_event_history = "test-value"
        result = r.event_event_history
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_diagnostic_report_location_performed_roundtrip(self):
        r = DiagnosticReport()
        r.diagnostic_report_location_performed = "test-value"
        result = r.diagnostic_report_location_performed
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_workflow_shall_comply_with_roundtrip(self):
        r = DiagnosticReport()
        r.workflow_shall_comply_with = "test-value"
        result = r.workflow_shall_comply_with
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_diagnosticreport_event_location_roundtrip(self):
        r = DiagnosticReport()
        r.event_location = "test-value"
        result = r.event_location
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_distance_cqf_is_empty_list_roundtrip(self):
        r = Distance()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_documentreference_workflow_triggered_by_roundtrip(self):
        r = DocumentReference()
        r.workflow_triggered_by = "test-value"
        result = r.workflow_triggered_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_documentreference_event_performer_function_roundtrip(self):
        r = DocumentReference()
        r.event_performer_function = "test-value"
        result = r.event_performer_function
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_documentreference_workflow_research_study_roundtrip(self):
        r = DocumentReference()
        r.workflow_research_study = "test-value"
        result = r.workflow_research_study
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_documentreference_documentreference_sourcepatient_roundtrip(self):
        r = DocumentReference()
        r.documentreference_sourcepatient = "test-value"
        result = r.documentreference_sourcepatient
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_documentreference_workflow_supporting_info_roundtrip(self):
        r = DocumentReference()
        r.workflow_supporting_info = "test-value"
        result = r.workflow_supporting_info
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_documentreference_documentreference_thumbnail_roundtrip(self):
        r = DocumentReference()
        r.documentreference_thumbnail = "test-value"
        result = r.documentreference_thumbnail
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_documentreference_workflow_episode_of_care_roundtrip(self):
        r = DocumentReference()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_documentreference_event_status_reason_roundtrip(self):
        r = DocumentReference()
        r.event_status_reason = "test-value"
        result = r.event_status_reason
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_documentreference_workflow_reason_roundtrip(self):
        r = DocumentReference()
        r.workflow_reason = "test-value"
        result = r.workflow_reason
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_documentreference_workflow_adheres_to_roundtrip(self):
        r = DocumentReference()
        r.workflow_adheres_to = "test-value"
        result = r.workflow_adheres_to
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_documentreference_workflow_shall_comply_with_roundtrip(self):
        r = DocumentReference()
        r.workflow_shall_comply_with = "test-value"
        result = r.workflow_shall_comply_with
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_documentreference_event_location_roundtrip(self):
        r = DocumentReference()
        r.event_location = "test-value"
        result = r.event_location
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_domainresource_cqf_library_roundtrip(self):
        r = DomainResource()
        r.cqf_library = "test-value"
        result = r.cqf_library
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_domainresource_cqf_knowledge_capability_roundtrip(self):
        r = DomainResource()
        r.cqf_knowledge_capability = "test-value"
        result = r.cqf_knowledge_capability
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_domainresource_artifact_is_owned_roundtrip(self):
        r = DomainResource()
        r.artifact_is_owned = "test-value"
        result = r.artifact_is_owned
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_domainresource_structuredefinition_fmm_roundtrip(self):
        r = DomainResource()
        r.structuredefinition_fmm = "test-value"
        result = r.structuredefinition_fmm
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_domainresource_structuredefinition_standards_status_reason_roundtrip(self):
        r = DomainResource()
        r.structuredefinition_standards_status_reason = "test-value"
        result = r.structuredefinition_standards_status_reason
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_domainresource_cqf_knowledge_representation_level_roundtrip(self):
        r = DomainResource()
        r.cqf_knowledge_representation_level = "test-value"
        result = r.cqf_knowledge_representation_level
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_domainresource_cqf_logic_definition_roundtrip(self):
        r = DomainResource()
        r.cqf_logic_definition = "test-value"
        result = r.cqf_logic_definition
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_domainresource_structuredefinition_wg_roundtrip(self):
        r = DomainResource()
        r.structuredefinition_wg = "test-value"
        result = r.structuredefinition_wg
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_domainresource_structuredefinition_fmm_support_roundtrip(self):
        r = DomainResource()
        r.structuredefinition_fmm_support = "test-value"
        result = r.structuredefinition_fmm_support
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_dosage_cqf_is_empty_list_roundtrip(self):
        r = Dosage()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_dosage_dosage_minimum_gap_between_dose_roundtrip(self):
        r = Dosage()
        r.dosage_minimum_gap_between_dose = "test-value"
        result = r.dosage_minimum_gap_between_dose
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_dosage_dosage_conditions_roundtrip(self):
        r = Dosage()
        r.dosage_conditions = "test-value"
        result = r.dosage_conditions
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_duration_cqf_is_empty_list_roundtrip(self):
        r = Duration()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_artifact_editor_roundtrip(self):
        r = Element()
        r.artifact_editor = "test-value"
        result = r.artifact_editor
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_cqf_calculated_value_roundtrip(self):
        r = Element()
        r.cqf_calculated_value = "test-value"
        result = r.cqf_calculated_value
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_cqf_expression_roundtrip(self):
        r = Element()
        r.cqf_expression = "test-value"
        result = r.cqf_expression
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_narrative_link_roundtrip(self):
        r = Element()
        r.narrative_link = "test-value"
        result = r.narrative_link
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_rendering_style_roundtrip(self):
        r = Element()
        r.rendering_style = "test-value"
        result = r.rendering_style
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_cqf_citation_roundtrip(self):
        r = Element()
        r.cqf_citation = "test-value"
        result = r.cqf_citation
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_version_specific_use_roundtrip(self):
        r = Element()
        r.version_specific_use = "test-value"
        result = r.version_specific_use
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_satisfies_requirement_roundtrip(self):
        r = Element()
        r.satisfies_requirement = "test-value"
        result = r.satisfies_requirement
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_cqf_initial_value_roundtrip(self):
        r = Element()
        r.cqf_initial_value = "test-value"
        result = r.cqf_initial_value
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_derivation_reference_roundtrip(self):
        r = Element()
        r.derivation_reference = "test-value"
        result = r.derivation_reference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_cqf_certainty_roundtrip(self):
        r = Element()
        r.cqf_certainty = "test-value"
        result = r.cqf_certainty
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_artifact_reference_roundtrip(self):
        r = Element()
        r.artifact_reference = "test-value"
        result = r.artifact_reference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_artifact_endorser_roundtrip(self):
        r = Element()
        r.artifact_endorser = "test-value"
        result = r.artifact_endorser
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_version_specific_value_roundtrip(self):
        r = Element()
        r.version_specific_value = "test-value"
        result = r.version_specific_value
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_artifact_canonical_reference_roundtrip(self):
        r = Element()
        r.artifact_canonical_reference = "test-value"
        result = r.artifact_canonical_reference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_original_text_roundtrip(self):
        r = Element()
        r.original_text = "test-value"
        result = r.original_text
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_artifact_reviewer_roundtrip(self):
        r = Element()
        r.artifact_reviewer = "test-value"
        result = r.artifact_reviewer
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_cqf_relative_date_time_roundtrip(self):
        r = Element()
        r.cqf_relative_date_time = "test-value"
        result = r.cqf_relative_date_time
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_data_absent_reason_roundtrip(self):
        r = Element()
        r.data_absent_reason = "test-value"
        result = r.data_absent_reason
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_rendering_style_sensitive_roundtrip(self):
        r = Element()
        r.rendering_style_sensitive = "test-value"
        result = r.rendering_style_sensitive
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_iso21090_null_flavor_roundtrip(self):
        r = Element()
        r.iso21090_null_flavor = "test-value"
        result = r.iso21090_null_flavor
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_body_site_roundtrip(self):
        r = Element()
        r.body_site = "test-value"
        result = r.body_site
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_elementdefinition_bestpractice_explanation_roundtrip(self):
        r = ElementDefinition()
        r.elementdefinition_bestpractice_explanation = "test-value"
        result = r.elementdefinition_bestpractice_explanation
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_structuredefinition_display_hint_roundtrip(self):
        r = ElementDefinition()
        r.structuredefinition_display_hint = "test-value"
        result = r.structuredefinition_display_hint
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_elementdefinition_pattern_roundtrip(self):
        r = ElementDefinition()
        r.elementdefinition_pattern = "test-value"
        result = r.elementdefinition_pattern
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_elementdefinition_type_must_support_roundtrip(self):
        r = ElementDefinition()
        r.elementdefinition_type_must_support = "test-value"
        result = r.elementdefinition_type_must_support
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_elementdefinition_translatable_roundtrip(self):
        r = ElementDefinition()
        r.elementdefinition_translatable = "test-value"
        result = r.elementdefinition_translatable
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_min_length_roundtrip(self):
        r = ElementDefinition()
        r.min_length = "test-value"
        result = r.min_length
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_ext_11179_object_class_roundtrip(self):
        r = ElementDefinition()
        r.ext_11179_object_class = "test-value"
        result = r.ext_11179_object_class
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_elementdefinition_equivalence_roundtrip(self):
        r = ElementDefinition()
        r.elementdefinition_equivalence = "test-value"
        result = r.elementdefinition_equivalence
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_questionnaire_constraint_roundtrip(self):
        r = ElementDefinition()
        r.questionnaire_constraint = "test-value"
        result = r.questionnaire_constraint
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_structuredefinition_fhir_type_roundtrip(self):
        r = ElementDefinition()
        r.structuredefinition_fhir_type = "test-value"
        result = r.structuredefinition_fhir_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_elementdefinition_profile_element_roundtrip(self):
        r = ElementDefinition()
        r.elementdefinition_profile_element = "test-value"
        result = r.elementdefinition_profile_element
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_elementdefinition_selector_roundtrip(self):
        r = ElementDefinition()
        r.elementdefinition_selector = "test-value"
        result = r.elementdefinition_selector
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_questionnaire_signature_required_roundtrip(self):
        r = ElementDefinition()
        r.questionnaire_signature_required = "test-value"
        result = r.questionnaire_signature_required
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_elementdefinition_max_value_set_roundtrip(self):
        r = ElementDefinition()
        r.elementdefinition_max_value_set = "test-value"
        result = r.elementdefinition_max_value_set
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_max_decimal_places_roundtrip(self):
        r = ElementDefinition()
        r.max_decimal_places = "test-value"
        result = r.max_decimal_places
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_questionnaire_hidden_roundtrip(self):
        r = ElementDefinition()
        r.questionnaire_hidden = "test-value"
        result = r.questionnaire_hidden
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_elementdefinition_is_common_binding_roundtrip(self):
        r = ElementDefinition()
        r.elementdefinition_is_common_binding = "test-value"
        result = r.elementdefinition_is_common_binding
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_cqf_should_trace_dependency_roundtrip(self):
        r = ElementDefinition()
        r.cqf_should_trace_dependency = "test-value"
        result = r.cqf_should_trace_dependency
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_elementdefinition_defaulttype_roundtrip(self):
        r = ElementDefinition()
        r.elementdefinition_defaulttype = "test-value"
        result = r.elementdefinition_defaulttype
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_elementdefinition_allowed_units_roundtrip(self):
        r = ElementDefinition()
        r.elementdefinition_allowed_units = "test-value"
        result = r.elementdefinition_allowed_units
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_elementdefinition_suppress_roundtrip(self):
        r = ElementDefinition()
        r.elementdefinition_suppress = "test-value"
        result = r.elementdefinition_suppress
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_structuredefinition_standards_status_roundtrip(self):
        r = ElementDefinition()
        r.structuredefinition_standards_status = "test-value"
        result = r.structuredefinition_standards_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_structuredefinition_explicit_type_name_roundtrip(self):
        r = ElementDefinition()
        r.structuredefinition_explicit_type_name = "test-value"
        result = r.structuredefinition_explicit_type_name
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_elementdefinition_identifier_roundtrip(self):
        r = ElementDefinition()
        r.elementdefinition_identifier = "test-value"
        result = r.elementdefinition_identifier
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_structuredefinition_hierarchy_roundtrip(self):
        r = ElementDefinition()
        r.structuredefinition_hierarchy = "test-value"
        result = r.structuredefinition_hierarchy
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_structuredefinition_normative_version_roundtrip(self):
        r = ElementDefinition()
        r.structuredefinition_normative_version = "test-value"
        result = r.structuredefinition_normative_version
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_obligation_roundtrip(self):
        r = ElementDefinition()
        r.obligation = "test-value"
        result = r.obligation
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_ext_11179_object_class_property_roundtrip(self):
        r = ElementDefinition()
        r.ext_11179_object_class_property = "test-value"
        result = r.ext_11179_object_class_property
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_questionnaire_item_control_roundtrip(self):
        r = ElementDefinition()
        r.questionnaire_item_control = "test-value"
        result = r.questionnaire_item_control
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_questionnaire_support_link_roundtrip(self):
        r = ElementDefinition()
        r.questionnaire_support_link = "test-value"
        result = r.questionnaire_support_link
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_mime_type_roundtrip(self):
        r = ElementDefinition()
        r.mime_type = "test-value"
        result = r.mime_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_design_note_roundtrip(self):
        r = ElementDefinition()
        r.design_note = "test-value"
        result = r.design_note
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_elementdefinition_inherited_extensible_value_set_roundtrip(self):
        r = ElementDefinition()
        r.elementdefinition_inherited_extensible_value_set = "test-value"
        result = r.elementdefinition_inherited_extensible_value_set
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_elementdefinition_question_roundtrip(self):
        r = ElementDefinition()
        r.elementdefinition_question = "test-value"
        result = r.elementdefinition_question
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_elementdefinition_bestpractice_roundtrip(self):
        r = ElementDefinition()
        r.elementdefinition_bestpractice = "test-value"
        result = r.elementdefinition_bestpractice
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_questionnaire_base_type_roundtrip(self):
        r = ElementDefinition()
        r.questionnaire_base_type = "test-value"
        result = r.questionnaire_base_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_elementdefinition_binding_name_roundtrip(self):
        r = ElementDefinition()
        r.elementdefinition_binding_name = "test-value"
        result = r.elementdefinition_binding_name
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_elementdefinition_graph_constraint_roundtrip(self):
        r = ElementDefinition()
        r.elementdefinition_graph_constraint = "test-value"
        result = r.elementdefinition_graph_constraint
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_elementdefinition_min_value_set_roundtrip(self):
        r = ElementDefinition()
        r.elementdefinition_min_value_set = "test-value"
        result = r.elementdefinition_min_value_set
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_questionnaire_usage_mode_roundtrip(self):
        r = ElementDefinition()
        r.questionnaire_usage_mode = "test-value"
        result = r.questionnaire_usage_mode
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_entry_format_roundtrip(self):
        r = ElementDefinition()
        r.entry_format = "test-value"
        result = r.entry_format
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_max_size_roundtrip(self):
        r = ElementDefinition()
        r.max_size = "test-value"
        result = r.max_size
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_workflow_triggered_by_roundtrip(self):
        r = Encounter()
        r.workflow_triggered_by = "test-value"
        result = r.workflow_triggered_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_encounter_mode_of_arrival_roundtrip(self):
        r = Encounter()
        r.encounter_mode_of_arrival = "test-value"
        result = r.encounter_mode_of_arrival
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_workflow_research_study_roundtrip(self):
        r = Encounter()
        r.workflow_research_study = "test-value"
        result = r.workflow_research_study
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_encounter_reason_cancelled_roundtrip(self):
        r = Encounter()
        r.encounter_reason_cancelled = "test-value"
        result = r.encounter_reason_cancelled
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_workflow_follow_on_of_roundtrip(self):
        r = Encounter()
        r.workflow_follow_on_of = "test-value"
        result = r.workflow_follow_on_of
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_workflow_release_date_roundtrip(self):
        r = Encounter()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_workflow_supporting_info_roundtrip(self):
        r = Encounter()
        r.workflow_supporting_info = "test-value"
        result = r.workflow_supporting_info
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_workflow_adheres_to_roundtrip(self):
        r = Encounter()
        r.workflow_adheres_to = "test-value"
        result = r.workflow_adheres_to
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_encounter_associated_encounter_roundtrip(self):
        r = Encounter()
        r.encounter_associated_encounter = "test-value"
        result = r.encounter_associated_encounter
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_endpoint_workflow_release_date_roundtrip(self):
        r = Endpoint()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_endpoint_endpoint_fhir_version_roundtrip(self):
        r = Endpoint()
        r.endpoint_fhir_version = "test-value"
        result = r.endpoint_fhir_version
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_enrollmentrequest_workflow_episode_of_care_roundtrip(self):
        r = EnrollmentRequest()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_enrollmentresponse_workflow_episode_of_care_roundtrip(self):
        r = EnrollmentResponse()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_episodeofcare_event_based_on_roundtrip(self):
        r = EpisodeOfCare()
        r.event_based_on = "test-value"
        result = r.event_based_on
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_episodeofcare_workflow_release_date_roundtrip(self):
        r = EpisodeOfCare()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_eventdefinition_replaces_roundtrip(self):
        r = EventDefinition()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_evidence_statistic_model_include_if_roundtrip(self):
        r = Evidence()
        r.statistic_model_include_if = "test-value"
        result = r.statistic_model_include_if
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_evidence_replaces_roundtrip(self):
        r = Evidence()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_evidencereport_replaces_roundtrip(self):
        r = EvidenceReport()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_evidencevariable_replaces_roundtrip(self):
        r = EvidenceVariable()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_examplescenario_replaces_roundtrip(self):
        r = ExampleScenario()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_explanationofbenefit_event_based_on_roundtrip(self):
        r = ExplanationOfBenefit()
        r.event_based_on = "test-value"
        result = r.event_based_on
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_expression_references_contained_roundtrip(self):
        r = Expression()
        r.references_contained = "test-value"
        result = r.references_contained
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_expression_cqf_is_empty_list_roundtrip(self):
        r = Expression()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_expression_cqf_alternative_expression_roundtrip(self):
        r = Expression()
        r.cqf_alternative_expression = "test-value"
        result = r.cqf_alternative_expression
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_extendedcontactdetail_extended_contact_availability_roundtrip(self):
        r = ExtendedContactDetail()
        r.extended_contact_availability = "test-value"
        result = r.extended_contact_availability
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_extendedcontactdetail_contactpoint_comment_roundtrip(self):
        r = ExtendedContactDetail()
        r.contactpoint_comment = "test-value"
        result = r.contactpoint_comment
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_extendedcontactdetail_iso21090_preferred_roundtrip(self):
        r = ExtendedContactDetail()
        r.iso21090_preferred = "test-value"
        result = r.iso21090_preferred
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_extension_structuredefinition_extension_meaning_roundtrip(self):
        r = Extension()
        r.structuredefinition_extension_meaning = "test-value"
        result = r.structuredefinition_extension_meaning
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_familymemberhistory_workflow_triggered_by_roundtrip(self):
        r = FamilyMemberHistory()
        r.workflow_triggered_by = "test-value"
        result = r.workflow_triggered_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_familymemberhistory_family_member_history_genetics_parent_roundtrip(self):
        r = FamilyMemberHistory()
        r.family_member_history_genetics_parent = "test-value"
        result = r.family_member_history_genetics_parent
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_familymemberhistory_familymemberhistory_patient_record_roundtrip(self):
        r = FamilyMemberHistory()
        r.familymemberhistory_patient_record = "test-value"
        result = r.familymemberhistory_patient_record
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_familymemberhistory_workflow_research_study_roundtrip(self):
        r = FamilyMemberHistory()
        r.workflow_research_study = "test-value"
        result = r.workflow_research_study
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_familymemberhistory_family_member_history_genetics_sibling_roundtrip(self):
        r = FamilyMemberHistory()
        r.family_member_history_genetics_sibling = "test-value"
        result = r.family_member_history_genetics_sibling
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_familymemberhistory_familymemberhistory_type_roundtrip(self):
        r = FamilyMemberHistory()
        r.familymemberhistory_type = "test-value"
        result = r.familymemberhistory_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_familymemberhistory_familymemberhistory_severity_roundtrip(self):
        r = FamilyMemberHistory()
        r.familymemberhistory_severity = "test-value"
        result = r.familymemberhistory_severity
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_familymemberhistory_familymemberhistory_abatement_roundtrip(self):
        r = FamilyMemberHistory()
        r.familymemberhistory_abatement = "test-value"
        result = r.familymemberhistory_abatement
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_familymemberhistory_event_based_on_roundtrip(self):
        r = FamilyMemberHistory()
        r.event_based_on = "test-value"
        result = r.event_based_on
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_familymemberhistory_family_member_history_genetics_observation_roundtrip(self):
        r = FamilyMemberHistory()
        r.family_member_history_genetics_observation = "test-value"
        result = r.family_member_history_genetics_observation
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_familymemberhistory_workflow_episode_of_care_roundtrip(self):
        r = FamilyMemberHistory()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_familymemberhistory_workflow_adheres_to_roundtrip(self):
        r = FamilyMemberHistory()
        r.workflow_adheres_to = "test-value"
        result = r.workflow_adheres_to
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_flag_flag_detail_roundtrip(self):
        r = Flag()
        r.flag_detail = "test-value"
        result = r.flag_detail
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_flag_workflow_episode_of_care_roundtrip(self):
        r = Flag()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_flag_flag_priority_roundtrip(self):
        r = Flag()
        r.flag_priority = "test-value"
        result = r.flag_priority
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_goal_goal_acceptance_roundtrip(self):
        r = Goal()
        r.goal_acceptance = "test-value"
        result = r.goal_acceptance
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_goal_goal_reason_rejected_roundtrip(self):
        r = Goal()
        r.goal_reason_rejected = "test-value"
        result = r.goal_reason_rejected
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_goal_workflow_protective_factor_roundtrip(self):
        r = Goal()
        r.workflow_protective_factor = "test-value"
        result = r.workflow_protective_factor
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_goal_workflow_release_date_roundtrip(self):
        r = Goal()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_goal_workflow_episode_of_care_roundtrip(self):
        r = Goal()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_goal_workflow_barrier_roundtrip(self):
        r = Goal()
        r.workflow_barrier = "test-value"
        result = r.workflow_barrier
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_goal_goal_relationship_roundtrip(self):
        r = Goal()
        r.goal_relationship = "test-value"
        result = r.goal_relationship
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_graphdefinition_replaces_roundtrip(self):
        r = GraphDefinition()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_group_artifact_editor_roundtrip(self):
        r = Group()
        r.artifact_editor = "test-value"
        result = r.artifact_editor
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_group_cqf_test_artifact_roundtrip(self):
        r = Group()
        r.cqf_test_artifact = "test-value"
        result = r.cqf_test_artifact
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_group_resource_approval_date_roundtrip(self):
        r = Group()
        r.resource_approval_date = "test-value"
        result = r.resource_approval_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_group_resource_last_review_date_roundtrip(self):
        r = Group()
        r.resource_last_review_date = "test-value"
        result = r.resource_last_review_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_group_resource_effective_period_roundtrip(self):
        r = Group()
        r.resource_effective_period = "test-value"
        result = r.resource_effective_period
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_group_artifact_endorser_roundtrip(self):
        r = Group()
        r.artifact_endorser = "test-value"
        result = r.artifact_endorser
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_group_artifact_reviewer_roundtrip(self):
        r = Group()
        r.artifact_reviewer = "test-value"
        result = r.artifact_reviewer
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_group_cqf_input_parameters_roundtrip(self):
        r = Group()
        r.cqf_input_parameters = "test-value"
        result = r.cqf_input_parameters
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_group_characteristic_expression_roundtrip(self):
        r = Group()
        r.characteristic_expression = "test-value"
        result = r.characteristic_expression
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_guidanceresponse_cqf_input_parameters_roundtrip(self):
        r = GuidanceResponse()
        r.cqf_input_parameters = "test-value"
        result = r.cqf_input_parameters
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_humanname_humanname_mothers_family_roundtrip(self):
        r = HumanName()
        r.humanname_mothers_family = "test-value"
        result = r.humanname_mothers_family
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_humanname_humanname_own_prefix_roundtrip(self):
        r = HumanName()
        r.humanname_own_prefix = "test-value"
        result = r.humanname_own_prefix
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_humanname_iso21090_en_representation_roundtrip(self):
        r = HumanName()
        r.iso21090_en_representation = "test-value"
        result = r.iso21090_en_representation
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_humanname_language_roundtrip(self):
        r = HumanName()
        r.language = "test-value"
        result = r.language
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_humanname_cqf_is_empty_list_roundtrip(self):
        r = HumanName()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_humanname_humanname_assembly_order_roundtrip(self):
        r = HumanName()
        r.humanname_assembly_order = "test-value"
        result = r.humanname_assembly_order
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_humanname_humanname_partner_prefix_roundtrip(self):
        r = HumanName()
        r.humanname_partner_prefix = "test-value"
        result = r.humanname_partner_prefix
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_humanname_iso21090_en_qualifier_roundtrip(self):
        r = HumanName()
        r.iso21090_en_qualifier = "test-value"
        result = r.iso21090_en_qualifier
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_humanname_humanname_own_name_roundtrip(self):
        r = HumanName()
        r.humanname_own_name = "test-value"
        result = r.humanname_own_name
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_humanname_iso21090_en_use_roundtrip(self):
        r = HumanName()
        r.iso21090_en_use = "test-value"
        result = r.iso21090_en_use
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_humanname_humanname_fathers_family_roundtrip(self):
        r = HumanName()
        r.humanname_fathers_family = "test-value"
        result = r.humanname_fathers_family
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_humanname_humanname_partner_name_roundtrip(self):
        r = HumanName()
        r.humanname_partner_name = "test-value"
        result = r.humanname_partner_name
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_identifier_cqf_is_empty_list_roundtrip(self):
        r = Identifier()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_identifier_rendered_value_roundtrip(self):
        r = Identifier()
        r.rendered_value = "test-value"
        result = r.rendered_value
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_identifier_identifier_check_digit_roundtrip(self):
        r = Identifier()
        r.identifier_check_digit = "test-value"
        result = r.identifier_check_digit
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_identifier_identifier_valid_date_roundtrip(self):
        r = Identifier()
        r.identifier_valid_date = "test-value"
        result = r.identifier_valid_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_imagingstudy_workflow_episode_of_care_roundtrip(self):
        r = ImagingStudy()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_immunization_workflow_triggered_by_roundtrip(self):
        r = Immunization()
        r.workflow_triggered_by = "test-value"
        result = r.workflow_triggered_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_immunization_workflow_research_study_roundtrip(self):
        r = Immunization()
        r.workflow_research_study = "test-value"
        result = r.workflow_research_study
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_immunization_immunization_procedure_roundtrip(self):
        r = Immunization()
        r.immunization_procedure = "test-value"
        result = r.immunization_procedure
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_immunization_workflow_episode_of_care_roundtrip(self):
        r = Immunization()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_immunization_workflow_adheres_to_roundtrip(self):
        r = Immunization()
        r.workflow_adheres_to = "test-value"
        result = r.workflow_adheres_to
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_immunizationevaluation_workflow_generated_from_roundtrip(self):
        r = ImmunizationEvaluation()
        r.workflow_generated_from = "test-value"
        result = r.workflow_generated_from
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_immunizationevaluation_event_based_on_roundtrip(self):
        r = ImmunizationEvaluation()
        r.event_based_on = "test-value"
        result = r.event_based_on
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_immunizationevaluation_workflow_episode_of_care_roundtrip(self):
        r = ImmunizationEvaluation()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_immunizationevaluation_workflow_adheres_to_roundtrip(self):
        r = ImmunizationEvaluation()
        r.workflow_adheres_to = "test-value"
        result = r.workflow_adheres_to
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_immunizationrecommendation_workflow_triggered_by_roundtrip(self):
        r = ImmunizationRecommendation()
        r.workflow_triggered_by = "test-value"
        result = r.workflow_triggered_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_immunizationrecommendation_workflow_generated_from_roundtrip(self):
        r = ImmunizationRecommendation()
        r.workflow_generated_from = "test-value"
        result = r.workflow_generated_from
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_immunizationrecommendation_workflow_episode_of_care_roundtrip(self):
        r = ImmunizationRecommendation()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_immunizationrecommendation_workflow_complies_with_roundtrip(self):
        r = ImmunizationRecommendation()
        r.workflow_complies_with = "test-value"
        result = r.workflow_complies_with
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_implementationguide_resource_approval_date_roundtrip(self):
        r = ImplementationGuide()
        r.resource_approval_date = "test-value"
        result = r.resource_approval_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_implementationguide_cqf_model_info_settings_roundtrip(self):
        r = ImplementationGuide()
        r.cqf_model_info_settings = "test-value"
        result = r.cqf_model_info_settings
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_implementationguide_resource_last_review_date_roundtrip(self):
        r = ImplementationGuide()
        r.resource_last_review_date = "test-value"
        result = r.resource_last_review_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_implementationguide_cqf_expansion_parameters_roundtrip(self):
        r = ImplementationGuide()
        r.cqf_expansion_parameters = "test-value"
        result = r.cqf_expansion_parameters
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_implementationguide_structuredefinition_standards_status_roundtrip(self):
        r = ImplementationGuide()
        r.structuredefinition_standards_status = "test-value"
        result = r.structuredefinition_standards_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_implementationguide_resource_effective_period_roundtrip(self):
        r = ImplementationGuide()
        r.resource_effective_period = "test-value"
        result = r.resource_effective_period
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_implementationguide_replaces_roundtrip(self):
        r = ImplementationGuide()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_implementationguide_implementationguide_source_file_roundtrip(self):
        r = ImplementationGuide()
        r.implementationguide_source_file = "test-value"
        result = r.implementationguide_source_file
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_inventoryreport_event_based_on_roundtrip(self):
        r = InventoryReport()
        r.event_based_on = "test-value"
        result = r.event_based_on
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_invoice_workflow_episode_of_care_roundtrip(self):
        r = Invoice()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_library_cqf_test_artifact_roundtrip(self):
        r = Library()
        r.cqf_test_artifact = "test-value"
        result = r.cqf_test_artifact
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_library_cqf_model_info_settings_roundtrip(self):
        r = Library()
        r.cqf_model_info_settings = "test-value"
        result = r.cqf_model_info_settings
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_library_cqf_expansion_parameters_roundtrip(self):
        r = Library()
        r.cqf_expansion_parameters = "test-value"
        result = r.cqf_expansion_parameters
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_library_replaces_roundtrip(self):
        r = Library()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_library_cqf_cql_options_roundtrip(self):
        r = Library()
        r.cqf_cql_options = "test-value"
        result = r.cqf_cql_options
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_library_cqf_input_parameters_roundtrip(self):
        r = Library()
        r.cqf_input_parameters = "test-value"
        result = r.cqf_input_parameters
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_library_cqf_part_of_roundtrip(self):
        r = Library()
        r.cqf_part_of = "test-value"
        result = r.cqf_part_of
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_list_list_change_base_roundtrip(self):
        r = List()
        r.list_change_base = "test-value"
        result = r.list_change_base
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_list_list_for_roundtrip(self):
        r = List()
        r.list_for = "test-value"
        result = r.list_for
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_list_workflow_episode_of_care_roundtrip(self):
        r = List()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_list_list_category_roundtrip(self):
        r = List()
        r.list_category = "test-value"
        result = r.list_category
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_location_location_communication_roundtrip(self):
        r = Location()
        r.location_communication = "test-value"
        result = r.location_communication
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_location_location_boundary_geojson_roundtrip(self):
        r = Location()
        r.location_boundary_geojson = "test-value"
        result = r.location_boundary_geojson
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_measure_cqf_criteria_reference_roundtrip(self):
        r = Measure()
        r.cqf_criteria_reference = "test-value"
        result = r.cqf_criteria_reference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_measure_artifact_is_owned_roundtrip(self):
        r = Measure()
        r.artifact_is_owned = "test-value"
        result = r.artifact_is_owned
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_measure_cqf_target_invariant_roundtrip(self):
        r = Measure()
        r.cqf_target_invariant = "test-value"
        result = r.cqf_target_invariant
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_measure_target_constraint_roundtrip(self):
        r = Measure()
        r.target_constraint = "test-value"
        result = r.target_constraint
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_measure_replaces_roundtrip(self):
        r = Measure()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_measure_variable_roundtrip(self):
        r = Measure()
        r.variable = "test-value"
        result = r.variable
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_measure_cqf_improvement_notation_guidance_roundtrip(self):
        r = Measure()
        r.cqf_improvement_notation_guidance = "test-value"
        result = r.cqf_improvement_notation_guidance
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_measure_workflow_shall_comply_with_roundtrip(self):
        r = Measure()
        r.workflow_shall_comply_with = "test-value"
        result = r.workflow_shall_comply_with
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_measurereport_measurereport_population_description_roundtrip(self):
        r = MeasureReport()
        r.measurereport_population_description = "test-value"
        result = r.measurereport_population_description
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_measurereport_cqf_criteria_reference_roundtrip(self):
        r = MeasureReport()
        r.cqf_criteria_reference = "test-value"
        result = r.cqf_criteria_reference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_measurereport_measurereport_category_roundtrip(self):
        r = MeasureReport()
        r.measurereport_category = "test-value"
        result = r.measurereport_category
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_measurereport_measurereport_count_quantity_roundtrip(self):
        r = MeasureReport()
        r.measurereport_count_quantity = "test-value"
        result = r.measurereport_count_quantity
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_measurereport_workflow_episode_of_care_roundtrip(self):
        r = MeasureReport()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_measurereport_cqf_input_parameters_roundtrip(self):
        r = MeasureReport()
        r.cqf_input_parameters = "test-value"
        result = r.cqf_input_parameters
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_measurereport_cqf_improvement_notation_guidance_roundtrip(self):
        r = MeasureReport()
        r.cqf_improvement_notation_guidance = "test-value"
        result = r.cqf_improvement_notation_guidance
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medication_medication_manufacturing_batch_roundtrip(self):
        r = Medication()
        r.medication_manufacturing_batch = "test-value"
        result = r.medication_manufacturing_batch
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationadministration_workflow_research_study_roundtrip(self):
        r = MedicationAdministration()
        r.workflow_research_study = "test-value"
        result = r.workflow_research_study
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationadministration_workflow_release_date_roundtrip(self):
        r = MedicationAdministration()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationadministration_workflow_episode_of_care_roundtrip(self):
        r = MedicationAdministration()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationdispense_medicationdispense_refills_remaining_roundtrip(self):
        r = MedicationDispense()
        r.medicationdispense_refills_remaining = "test-value"
        result = r.medicationdispense_refills_remaining
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationdispense_workflow_research_study_roundtrip(self):
        r = MedicationDispense()
        r.workflow_research_study = "test-value"
        result = r.workflow_research_study
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationdispense_medicationdispense_quantity_remaining_roundtrip(self):
        r = MedicationDispense()
        r.medicationdispense_quantity_remaining = "test-value"
        result = r.medicationdispense_quantity_remaining
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationdispense_workflow_release_date_roundtrip(self):
        r = MedicationDispense()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationdispense_workflow_episode_of_care_roundtrip(self):
        r = MedicationDispense()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationrequest_workflow_release_date_roundtrip(self):
        r = MedicationRequest()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationrequest_workflow_episode_of_care_roundtrip(self):
        r = MedicationRequest()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationstatement_workflow_research_study_roundtrip(self):
        r = MedicationStatement()
        r.workflow_research_study = "test-value"
        result = r.workflow_research_study
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationstatement_event_based_on_roundtrip(self):
        r = MedicationStatement()
        r.event_based_on = "test-value"
        result = r.event_based_on
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationstatement_workflow_episode_of_care_roundtrip(self):
        r = MedicationStatement()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_messagedefinition_replaces_roundtrip(self):
        r = MessageDefinition()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_messageheader_messageheader_response_request_roundtrip(self):
        r = MessageHeader()
        r.messageheader_response_request = "test-value"
        result = r.messageheader_response_request
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_meta_last_source_sync_roundtrip(self):
        r = Meta()
        r.last_source_sync = "test-value"
        result = r.last_source_sync
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_meta_cqf_is_empty_list_roundtrip(self):
        r = Meta()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_meta_timezone_roundtrip(self):
        r = Meta()
        r.timezone = "test-value"
        result = r.timezone
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_meta_first_created_roundtrip(self):
        r = Meta()
        r.first_created = "test-value"
        result = r.first_created
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_metadataresource_metadataresource_publish_date_roundtrip(self):
        r = MetadataResource()
        r.metadataresource_publish_date = "test-value"
        result = r.metadataresource_publish_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_molecularsequence_workflow_episode_of_care_roundtrip(self):
        r = MolecularSequence()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_money_cqf_is_empty_list_roundtrip(self):
        r = Money()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_namingsystem_resource_approval_date_roundtrip(self):
        r = NamingSystem()
        r.resource_approval_date = "test-value"
        result = r.resource_approval_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_namingsystem_resource_last_review_date_roundtrip(self):
        r = NamingSystem()
        r.resource_last_review_date = "test-value"
        result = r.resource_last_review_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_namingsystem_resource_effective_period_roundtrip(self):
        r = NamingSystem()
        r.resource_effective_period = "test-value"
        result = r.resource_effective_period
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_namingsystem_namingsystem_check_digit_roundtrip(self):
        r = NamingSystem()
        r.namingsystem_check_digit = "test-value"
        result = r.namingsystem_check_digit
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_namingsystem_replaces_roundtrip(self):
        r = NamingSystem()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_nutritionintake_workflow_release_date_roundtrip(self):
        r = NutritionIntake()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_nutritionintake_workflow_episode_of_care_roundtrip(self):
        r = NutritionIntake()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_nutritionorder_workflow_triggered_by_roundtrip(self):
        r = NutritionOrder()
        r.workflow_triggered_by = "test-value"
        result = r.workflow_triggered_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_nutritionorder_workflow_generated_from_roundtrip(self):
        r = NutritionOrder()
        r.workflow_generated_from = "test-value"
        result = r.workflow_generated_from
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_nutritionorder_request_insurance_roundtrip(self):
        r = NutritionOrder()
        r.request_insurance = "test-value"
        result = r.request_insurance
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_nutritionorder_request_do_not_perform_roundtrip(self):
        r = NutritionOrder()
        r.request_do_not_perform = "test-value"
        result = r.request_do_not_perform
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_nutritionorder_request_replaces_roundtrip(self):
        r = NutritionOrder()
        r.request_replaces = "test-value"
        result = r.request_replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_nutritionorder_nutritionorder_adaptive_feeding_device_roundtrip(self):
        r = NutritionOrder()
        r.nutritionorder_adaptive_feeding_device = "test-value"
        result = r.nutritionorder_adaptive_feeding_device
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_nutritionorder_workflow_release_date_roundtrip(self):
        r = NutritionOrder()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_nutritionorder_request_relevant_history_roundtrip(self):
        r = NutritionOrder()
        r.request_relevant_history = "test-value"
        result = r.request_relevant_history
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_nutritionorder_workflow_episode_of_care_roundtrip(self):
        r = NutritionOrder()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_nutritionorder_workflow_reason_roundtrip(self):
        r = NutritionOrder()
        r.workflow_reason = "test-value"
        result = r.workflow_reason
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_nutritionorder_workflow_complies_with_roundtrip(self):
        r = NutritionOrder()
        r.workflow_complies_with = "test-value"
        result = r.workflow_complies_with
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_nutritionorder_request_status_reason_roundtrip(self):
        r = NutritionOrder()
        r.request_status_reason = "test-value"
        result = r.request_status_reason
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_workflow_triggered_by_roundtrip(self):
        r = Observation()
        r.workflow_triggered_by = "test-value"
        result = r.workflow_triggered_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_event_performer_function_roundtrip(self):
        r = Observation()
        r.event_performer_function = "test-value"
        result = r.event_performer_function
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_observation_body_position_roundtrip(self):
        r = Observation()
        r.observation_body_position = "test-value"
        result = r.observation_body_position
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_observation_specimen_code_roundtrip(self):
        r = Observation()
        r.observation_specimen_code = "test-value"
        result = r.observation_specimen_code
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_observation_nature_of_abnormal_test_roundtrip(self):
        r = Observation()
        r.observation_nature_of_abnormal_test = "test-value"
        result = r.observation_nature_of_abnormal_test
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_observation_analysis_date_time_roundtrip(self):
        r = Observation()
        r.observation_analysis_date_time = "test-value"
        result = r.observation_analysis_date_time
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_observation_reagent_roundtrip(self):
        r = Observation()
        r.observation_reagent = "test-value"
        result = r.observation_reagent
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_workflow_research_study_roundtrip(self):
        r = Observation()
        r.workflow_research_study = "test-value"
        result = r.workflow_research_study
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_observation_replaces_roundtrip(self):
        r = Observation()
        r.observation_replaces = "test-value"
        result = r.observation_replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_observation_v2_subid_roundtrip(self):
        r = Observation()
        r.observation_v2_subid = "test-value"
        result = r.observation_v2_subid
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_observation_device_code_roundtrip(self):
        r = Observation()
        r.observation_device_code = "test-value"
        result = r.observation_device_code
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_diagnostic_report_risk_roundtrip(self):
        r = Observation()
        r.diagnostic_report_risk = "test-value"
        result = r.diagnostic_report_risk
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_observation_sequel_to_roundtrip(self):
        r = Observation()
        r.observation_sequel_to = "test-value"
        result = r.observation_sequel_to
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_workflow_related_artifact_roundtrip(self):
        r = Observation()
        r.workflow_related_artifact = "test-value"
        result = r.workflow_related_artifact
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_observation_precondition_roundtrip(self):
        r = Observation()
        r.observation_precondition = "test-value"
        result = r.observation_precondition
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_observation_delta_roundtrip(self):
        r = Observation()
        r.observation_delta = "test-value"
        result = r.observation_delta
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_workflow_supporting_info_roundtrip(self):
        r = Observation()
        r.workflow_supporting_info = "test-value"
        result = r.workflow_supporting_info
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_workflow_episode_of_care_roundtrip(self):
        r = Observation()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_event_status_reason_roundtrip(self):
        r = Observation()
        r.event_status_reason = "test-value"
        result = r.event_status_reason
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_observation_focus_code_roundtrip(self):
        r = Observation()
        r.observation_focus_code = "test-value"
        result = r.observation_focus_code
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_observation_secondary_finding_roundtrip(self):
        r = Observation()
        r.observation_secondary_finding = "test-value"
        result = r.observation_secondary_finding
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_observation_gateway_device_roundtrip(self):
        r = Observation()
        r.observation_gateway_device = "test-value"
        result = r.observation_gateway_device
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_workflow_reason_roundtrip(self):
        r = Observation()
        r.workflow_reason = "test-value"
        result = r.workflow_reason
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_observation_time_offset_roundtrip(self):
        r = Observation()
        r.observation_time_offset = "test-value"
        result = r.observation_time_offset
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_workflow_adheres_to_roundtrip(self):
        r = Observation()
        r.workflow_adheres_to = "test-value"
        result = r.workflow_adheres_to
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_event_event_history_roundtrip(self):
        r = Observation()
        r.event_event_history = "test-value"
        result = r.event_event_history
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_workflow_shall_comply_with_roundtrip(self):
        r = Observation()
        r.workflow_shall_comply_with = "test-value"
        result = r.workflow_shall_comply_with
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observation_event_location_roundtrip(self):
        r = Observation()
        r.event_location = "test-value"
        result = r.event_location
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_observationdefinition_replaces_roundtrip(self):
        r = ObservationDefinition()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_operationdefinition_resource_approval_date_roundtrip(self):
        r = OperationDefinition()
        r.resource_approval_date = "test-value"
        result = r.resource_approval_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_operationdefinition_resource_last_review_date_roundtrip(self):
        r = OperationDefinition()
        r.resource_last_review_date = "test-value"
        result = r.resource_last_review_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_operationdefinition_structuredefinition_standards_status_roundtrip(self):
        r = OperationDefinition()
        r.structuredefinition_standards_status = "test-value"
        result = r.structuredefinition_standards_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_operationdefinition_resource_effective_period_roundtrip(self):
        r = OperationDefinition()
        r.resource_effective_period = "test-value"
        result = r.resource_effective_period
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_operationdefinition_replaces_roundtrip(self):
        r = OperationDefinition()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_operationdefinition_elementdefinition_binding_name_roundtrip(self):
        r = OperationDefinition()
        r.elementdefinition_binding_name = "test-value"
        result = r.elementdefinition_binding_name
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_operationdefinition_workflow_shall_comply_with_roundtrip(self):
        r = OperationDefinition()
        r.workflow_shall_comply_with = "test-value"
        result = r.workflow_shall_comply_with
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_operationdefinition_operationdefinition_profile_roundtrip(self):
        r = OperationDefinition()
        r.operationdefinition_profile = "test-value"
        result = r.operationdefinition_profile
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_operationoutcome_operationoutcome_file_roundtrip(self):
        r = OperationOutcome()
        r.operationoutcome_file = "test-value"
        result = r.operationoutcome_file
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_operationoutcome_operationoutcome_issue_source_roundtrip(self):
        r = OperationOutcome()
        r.operationoutcome_issue_source = "test-value"
        result = r.operationoutcome_issue_source
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_operationoutcome_operationoutcome_detected_issue_roundtrip(self):
        r = OperationOutcome()
        r.operationoutcome_detected_issue = "test-value"
        result = r.operationoutcome_detected_issue
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_operationoutcome_operationoutcome_issue_col_roundtrip(self):
        r = OperationOutcome()
        r.operationoutcome_issue_col = "test-value"
        result = r.operationoutcome_issue_col
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_operationoutcome_operationoutcome_issue_slicetext_roundtrip(self):
        r = OperationOutcome()
        r.operationoutcome_issue_slicetext = "test-value"
        result = r.operationoutcome_issue_slicetext
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_operationoutcome_operationoutcome_message_id_roundtrip(self):
        r = OperationOutcome()
        r.operationoutcome_message_id = "test-value"
        result = r.operationoutcome_message_id
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_operationoutcome_operationoutcome_issue_server_roundtrip(self):
        r = OperationOutcome()
        r.operationoutcome_issue_server = "test-value"
        result = r.operationoutcome_issue_server
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_operationoutcome_operationoutcome_issue_line_roundtrip(self):
        r = OperationOutcome()
        r.operationoutcome_issue_line = "test-value"
        result = r.operationoutcome_issue_line
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_operationoutcome_operationoutcome_authority_roundtrip(self):
        r = OperationOutcome()
        r.operationoutcome_authority = "test-value"
        result = r.operationoutcome_authority
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_organization_preferred_contact_roundtrip(self):
        r = Organization()
        r.organization_preferred_contact = "test-value"
        result = r.organization_preferred_contact
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_organization_brand_roundtrip(self):
        r = Organization()
        r.organization_brand = "test-value"
        result = r.organization_brand
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_organization_period_roundtrip(self):
        r = Organization()
        r.organization_period = "test-value"
        result = r.organization_period
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_organization_portal_roundtrip(self):
        r = Organization()
        r.organization_portal = "test-value"
        result = r.organization_portal
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organizationaffiliation_organizationaffiliation_primary_ind_roundtrip(self):
        r = OrganizationAffiliation()
        r.organizationaffiliation_primary_ind = "test-value"
        result = r.organizationaffiliation_primary_ind
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_parameterdefinition_cqf_cql_access_modifier_roundtrip(self):
        r = ParameterDefinition()
        r.cqf_cql_access_modifier = "test-value"
        result = r.cqf_cql_access_modifier
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_parameterdefinition_cqf_is_empty_list_roundtrip(self):
        r = ParameterDefinition()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_parameterdefinition_cqf_cql_type_roundtrip(self):
        r = ParameterDefinition()
        r.cqf_cql_type = "test-value"
        result = r.cqf_cql_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_parameterdefinition_cqf_is_prefetch_token_roundtrip(self):
        r = ParameterDefinition()
        r.cqf_is_prefetch_token = "test-value"
        result = r.cqf_is_prefetch_token
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_parameterdefinition_cqf_default_value_roundtrip(self):
        r = ParameterDefinition()
        r.cqf_default_value = "test-value"
        result = r.cqf_default_value
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_parameters_parameters_full_url_roundtrip(self):
        r = Parameters()
        r.parameters_full_url = "test-value"
        result = r.parameters_full_url
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_parameters_cqf_cql_type_roundtrip(self):
        r = Parameters()
        r.cqf_cql_type = "test-value"
        result = r.cqf_cql_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_parameters_parameters_definition_roundtrip(self):
        r = Parameters()
        r.parameters_definition = "test-value"
        result = r.parameters_definition
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_proficiency_roundtrip(self):
        r = Patient()
        r.patient_proficiency = "test-value"
        result = r.patient_proficiency
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_multiple_birth_total_roundtrip(self):
        r = Patient()
        r.patient_multiple_birth_total = "test-value"
        result = r.patient_multiple_birth_total
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_importance_roundtrip(self):
        r = Patient()
        r.patient_importance = "test-value"
        result = r.patient_importance
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_congregation_roundtrip(self):
        r = Patient()
        r.patient_congregation = "test-value"
        result = r.patient_congregation
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_disability_roundtrip(self):
        r = Patient()
        r.patient_disability = "test-value"
        result = r.patient_disability
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_mothers_maiden_name_roundtrip(self):
        r = Patient()
        r.patient_mothers_maiden_name = "test-value"
        result = r.patient_mothers_maiden_name
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_contact_priority_roundtrip(self):
        r = Patient()
        r.patient_contact_priority = "test-value"
        result = r.patient_contact_priority
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_birth_place_roundtrip(self):
        r = Patient()
        r.patient_birth_place = "test-value"
        result = r.patient_birth_place
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_preference_type_roundtrip(self):
        r = Patient()
        r.patient_preference_type = "test-value"
        result = r.patient_preference_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_religion_roundtrip(self):
        r = Patient()
        r.patient_religion = "test-value"
        result = r.patient_religion
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_related_person_roundtrip(self):
        r = Patient()
        r.patient_related_person = "test-value"
        result = r.patient_related_person
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_individual_pronouns_roundtrip(self):
        r = Patient()
        r.individual_pronouns = "test-value"
        result = r.individual_pronouns
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_known_non_duplicate_roundtrip(self):
        r = Patient()
        r.patient_known_non_duplicate = "test-value"
        result = r.patient_known_non_duplicate
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_birth_time_roundtrip(self):
        r = Patient()
        r.patient_birth_time = "test-value"
        result = r.patient_birth_time
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_individual_gender_identity_roundtrip(self):
        r = Patient()
        r.individual_gender_identity = "test-value"
        result = r.individual_gender_identity
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

    def test_patient_patient_born_status_roundtrip(self):
        r = Patient()
        r.patient_born_status = "test-value"
        result = r.patient_born_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_adoption_info_roundtrip(self):
        r = Patient()
        r.patient_adoption_info = "test-value"
        result = r.patient_adoption_info
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_unknown_identity_roundtrip(self):
        r = Patient()
        r.patient_unknown_identity = "test-value"
        result = r.patient_unknown_identity
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_cadaveric_donor_roundtrip(self):
        r = Patient()
        r.patient_cadaveric_donor = "test-value"
        result = r.patient_cadaveric_donor
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_animal_roundtrip(self):
        r = Patient()
        r.patient_animal = "test-value"
        result = r.patient_animal
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_citizenship_roundtrip(self):
        r = Patient()
        r.patient_citizenship = "test-value"
        result = r.patient_citizenship
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_patient_interpreter_required_roundtrip(self):
        r = Patient()
        r.patient_interpreter_required = "test-value"
        result = r.patient_interpreter_required
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_individual_recorded_sex_or_gender_roundtrip(self):
        r = Patient()
        r.individual_recorded_sex_or_gender = "test-value"
        result = r.individual_recorded_sex_or_gender
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_paymentnotice_event_based_on_roundtrip(self):
        r = PaymentNotice()
        r.event_based_on = "test-value"
        result = r.event_based_on
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_paymentreconciliation_event_based_on_roundtrip(self):
        r = PaymentReconciliation()
        r.event_based_on = "test-value"
        result = r.event_based_on
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_period_artifact_period_duration_roundtrip(self):
        r = Period()
        r.artifact_period_duration = "test-value"
        result = r.artifact_period_duration
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_period_cqf_is_empty_list_roundtrip(self):
        r = Period()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_person_patient_proficiency_roundtrip(self):
        r = Person()
        r.patient_proficiency = "test-value"
        result = r.patient_proficiency
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_person_individual_pronouns_roundtrip(self):
        r = Person()
        r.individual_pronouns = "test-value"
        result = r.individual_pronouns
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_person_individual_gender_identity_roundtrip(self):
        r = Person()
        r.individual_gender_identity = "test-value"
        result = r.individual_gender_identity
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_person_individual_recorded_sex_or_gender_roundtrip(self):
        r = Person()
        r.individual_recorded_sex_or_gender = "test-value"
        result = r.individual_recorded_sex_or_gender
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_plandefinition_artifact_is_owned_roundtrip(self):
        r = PlanDefinition()
        r.artifact_is_owned = "test-value"
        result = r.artifact_is_owned
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_plandefinition_cqf_target_invariant_roundtrip(self):
        r = PlanDefinition()
        r.cqf_target_invariant = "test-value"
        result = r.cqf_target_invariant
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_plandefinition_timing_days_of_cycle_roundtrip(self):
        r = PlanDefinition()
        r.timing_days_of_cycle = "test-value"
        result = r.timing_days_of_cycle
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_plandefinition_cqf_cds_hooks_endpoint_roundtrip(self):
        r = PlanDefinition()
        r.cqf_cds_hooks_endpoint = "test-value"
        result = r.cqf_cds_hooks_endpoint
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_plandefinition_target_constraint_roundtrip(self):
        r = PlanDefinition()
        r.target_constraint = "test-value"
        result = r.target_constraint
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_plandefinition_replaces_roundtrip(self):
        r = PlanDefinition()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_plandefinition_variable_roundtrip(self):
        r = PlanDefinition()
        r.variable = "test-value"
        result = r.variable
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_plandefinition_cqf_strength_of_recommendation_roundtrip(self):
        r = PlanDefinition()
        r.cqf_strength_of_recommendation = "test-value"
        result = r.cqf_strength_of_recommendation
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_plandefinition_cqf_quality_of_evidence_roundtrip(self):
        r = PlanDefinition()
        r.cqf_quality_of_evidence = "test-value"
        result = r.cqf_quality_of_evidence
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_plandefinition_workflow_shall_comply_with_roundtrip(self):
        r = PlanDefinition()
        r.workflow_shall_comply_with = "test-value"
        result = r.workflow_shall_comply_with
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_plandefinition_goal_relationship_roundtrip(self):
        r = PlanDefinition()
        r.goal_relationship = "test-value"
        result = r.goal_relationship
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitioner_patient_proficiency_roundtrip(self):
        r = Practitioner()
        r.patient_proficiency = "test-value"
        result = r.patient_proficiency
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitioner_individual_pronouns_roundtrip(self):
        r = Practitioner()
        r.individual_pronouns = "test-value"
        result = r.individual_pronouns
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitioner_individual_gender_identity_roundtrip(self):
        r = Practitioner()
        r.individual_gender_identity = "test-value"
        result = r.individual_gender_identity
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitioner_practitioner_job_title_roundtrip(self):
        r = Practitioner()
        r.practitioner_job_title = "test-value"
        result = r.practitioner_job_title
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitioner_practitioner_animal_species_roundtrip(self):
        r = Practitioner()
        r.practitioner_animal_species = "test-value"
        result = r.practitioner_animal_species
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitioner_individual_recorded_sex_or_gender_roundtrip(self):
        r = Practitioner()
        r.individual_recorded_sex_or_gender = "test-value"
        result = r.individual_recorded_sex_or_gender
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitionerrole_practitionerrole_employment_status_roundtrip(self):
        r = PractitionerRole()
        r.practitionerrole_employment_status = "test-value"
        result = r.practitionerrole_employment_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitionerrole_individual_gender_identity_roundtrip(self):
        r = PractitionerRole()
        r.individual_gender_identity = "test-value"
        result = r.individual_gender_identity
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitionerrole_practitioner_job_title_roundtrip(self):
        r = PractitionerRole()
        r.practitioner_job_title = "test-value"
        result = r.practitioner_job_title
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitionerrole_practitionerrole_primary_ind_roundtrip(self):
        r = PractitionerRole()
        r.practitionerrole_primary_ind = "test-value"
        result = r.practitionerrole_primary_ind
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_procedure_procedure_progress_status_roundtrip(self):
        r = Procedure()
        r.procedure_progress_status = "test-value"
        result = r.procedure_progress_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_procedure_procedure_directed_by_roundtrip(self):
        r = Procedure()
        r.procedure_directed_by = "test-value"
        result = r.procedure_directed_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_procedure_procedure_caused_by_roundtrip(self):
        r = Procedure()
        r.procedure_caused_by = "test-value"
        result = r.procedure_caused_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_procedure_workflow_research_study_roundtrip(self):
        r = Procedure()
        r.workflow_research_study = "test-value"
        result = r.workflow_research_study
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_procedure_workflow_follow_on_of_roundtrip(self):
        r = Procedure()
        r.workflow_follow_on_of = "test-value"
        result = r.workflow_follow_on_of
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_procedure_procedure_method_roundtrip(self):
        r = Procedure()
        r.procedure_method = "test-value"
        result = r.procedure_method
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_procedure_workflow_release_date_roundtrip(self):
        r = Procedure()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_procedure_workflow_episode_of_care_roundtrip(self):
        r = Procedure()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_procedure_procedure_approach_body_structure_roundtrip(self):
        r = Procedure()
        r.procedure_approach_body_structure = "test-value"
        result = r.procedure_approach_body_structure
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_procedure_procedure_target_body_structure_roundtrip(self):
        r = Procedure()
        r.procedure_target_body_structure = "test-value"
        result = r.procedure_target_body_structure
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_procedure_procedure_incision_date_time_roundtrip(self):
        r = Procedure()
        r.procedure_incision_date_time = "test-value"
        result = r.procedure_incision_date_time
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_quantity_iso21090_uncertainty_type_roundtrip(self):
        r = Quantity()
        r.iso21090_uncertainty_type = "test-value"
        result = r.iso21090_uncertainty_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_quantity_cqf_is_empty_list_roundtrip(self):
        r = Quantity()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_quantity_iso21090_uncertainty_roundtrip(self):
        r = Quantity()
        r.iso21090_uncertainty = "test-value"
        result = r.iso21090_uncertainty
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_quantity_quantity_translation_roundtrip(self):
        r = Quantity()
        r.quantity_translation = "test-value"
        result = r.quantity_translation
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_min_length_roundtrip(self):
        r = Questionnaire()
        r.min_length = "test-value"
        result = r.min_length
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_fhir_type_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_fhir_type = "test-value"
        result = r.questionnaire_fhir_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_elementdefinition_conceptmap_roundtrip(self):
        r = Questionnaire()
        r.elementdefinition_conceptmap = "test-value"
        result = r.elementdefinition_conceptmap
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_constraint_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_constraint = "test-value"
        result = r.questionnaire_constraint
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_cqf_target_invariant_roundtrip(self):
        r = Questionnaire()
        r.cqf_target_invariant = "test-value"
        result = r.cqf_target_invariant
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_reference_filter_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_reference_filter = "test-value"
        result = r.questionnaire_reference_filter
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_max_value_roundtrip(self):
        r = Questionnaire()
        r.max_value = "test-value"
        result = r.max_value
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_signature_required_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_signature_required = "test-value"
        result = r.questionnaire_signature_required
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_derivation_type_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_derivation_type = "test-value"
        result = r.questionnaire_derivation_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_max_decimal_places_roundtrip(self):
        r = Questionnaire()
        r.max_decimal_places = "test-value"
        result = r.max_decimal_places
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_unit_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_unit = "test-value"
        result = r.questionnaire_unit
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_min_occurs_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_min_occurs = "test-value"
        result = r.questionnaire_min_occurs
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_hidden_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_hidden = "test-value"
        result = r.questionnaire_hidden
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_target_constraint_roundtrip(self):
        r = Questionnaire()
        r.target_constraint = "test-value"
        result = r.target_constraint
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_unit_option_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_unit_option = "test-value"
        result = r.questionnaire_unit_option
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_ext_11179_permitted_value_valueset_roundtrip(self):
        r = Questionnaire()
        r.ext_11179_permitted_value_valueset = "test-value"
        result = r.ext_11179_permitted_value_valueset
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_unit_value_set_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_unit_value_set = "test-value"
        result = r.questionnaire_unit_value_set
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_option_exclusive_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_option_exclusive = "test-value"
        result = r.questionnaire_option_exclusive
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_option_restriction_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_option_restriction = "test-value"
        result = r.questionnaire_option_restriction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_max_occurs_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_max_occurs = "test-value"
        result = r.questionnaire_max_occurs
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_ext_11179_permitted_value_conceptmap_roundtrip(self):
        r = Questionnaire()
        r.ext_11179_permitted_value_conceptmap = "test-value"
        result = r.ext_11179_permitted_value_conceptmap
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_definition_based_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_definition_based = "test-value"
        result = r.questionnaire_definition_based
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_item_control_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_item_control = "test-value"
        result = r.questionnaire_item_control
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_support_link_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_support_link = "test-value"
        result = r.questionnaire_support_link
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_min_value_roundtrip(self):
        r = Questionnaire()
        r.min_value = "test-value"
        result = r.min_value
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_replaces_roundtrip(self):
        r = Questionnaire()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_mime_type_roundtrip(self):
        r = Questionnaire()
        r.mime_type = "test-value"
        result = r.mime_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_design_note_roundtrip(self):
        r = Questionnaire()
        r.design_note = "test-value"
        result = r.design_note
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_variable_roundtrip(self):
        r = Questionnaire()
        r.variable = "test-value"
        result = r.variable
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_display_category_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_display_category = "test-value"
        result = r.questionnaire_display_category
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_base_type_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_base_type = "test-value"
        result = r.questionnaire_base_type
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_reference_resource_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_reference_resource = "test-value"
        result = r.questionnaire_reference_resource
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_item_weight_roundtrip(self):
        r = Questionnaire()
        r.item_weight = "test-value"
        result = r.item_weight
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_choice_orientation_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_choice_orientation = "test-value"
        result = r.questionnaire_choice_orientation
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_usage_mode_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_usage_mode = "test-value"
        result = r.questionnaire_usage_mode
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_reference_profile_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_reference_profile = "test-value"
        result = r.questionnaire_reference_profile
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_entry_format_roundtrip(self):
        r = Questionnaire()
        r.entry_format = "test-value"
        result = r.entry_format
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_option_prefix_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_option_prefix = "test-value"
        result = r.questionnaire_option_prefix
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_max_size_roundtrip(self):
        r = Questionnaire()
        r.max_size = "test-value"
        result = r.max_size
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaire_questionnaire_slider_step_value_roundtrip(self):
        r = Questionnaire()
        r.questionnaire_slider_step_value = "test-value"
        result = r.questionnaire_slider_step_value
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaireresponse_workflow_triggered_by_roundtrip(self):
        r = QuestionnaireResponse()
        r.workflow_triggered_by = "test-value"
        result = r.workflow_triggered_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaireresponse_questionnaireresponse_reason_roundtrip(self):
        r = QuestionnaireResponse()
        r.questionnaireresponse_reason = "test-value"
        result = r.questionnaireresponse_reason
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaireresponse_workflow_research_study_roundtrip(self):
        r = QuestionnaireResponse()
        r.workflow_research_study = "test-value"
        result = r.workflow_research_study
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaireresponse_questionnaireresponse_reviewer_roundtrip(self):
        r = QuestionnaireResponse()
        r.questionnaireresponse_reviewer = "test-value"
        result = r.questionnaireresponse_reviewer
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaireresponse_questionnaireresponse_author_roundtrip(self):
        r = QuestionnaireResponse()
        r.questionnaireresponse_author = "test-value"
        result = r.questionnaireresponse_author
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaireresponse_questionnaireresponse_completion_mode_roundtrip(self):
        r = QuestionnaireResponse()
        r.questionnaireresponse_completion_mode = "test-value"
        result = r.questionnaireresponse_completion_mode
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaireresponse_workflow_episode_of_care_roundtrip(self):
        r = QuestionnaireResponse()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaireresponse_workflow_adheres_to_roundtrip(self):
        r = QuestionnaireResponse()
        r.workflow_adheres_to = "test-value"
        result = r.workflow_adheres_to
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaireresponse_questionnaireresponse_signature_roundtrip(self):
        r = QuestionnaireResponse()
        r.questionnaireresponse_signature = "test-value"
        result = r.questionnaireresponse_signature
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaireresponse_questionnaireresponse_attester_roundtrip(self):
        r = QuestionnaireResponse()
        r.questionnaireresponse_attester = "test-value"
        result = r.questionnaireresponse_attester
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_range_cqf_is_empty_list_roundtrip(self):
        r = Range()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_ratio_cqf_is_empty_list_roundtrip(self):
        r = Ratio()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_reference_target_path_roundtrip(self):
        r = Reference()
        r.target_path = "test-value"
        result = r.target_path
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_reference_resolve_as_version_specific_roundtrip(self):
        r = Reference()
        r.resolve_as_version_specific = "test-value"
        result = r.resolve_as_version_specific
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_reference_artifact_uri_reference_roundtrip(self):
        r = Reference()
        r.artifact_uri_reference = "test-value"
        result = r.artifact_uri_reference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_reference_additional_identifier_roundtrip(self):
        r = Reference()
        r.additional_identifier = "test-value"
        result = r.additional_identifier
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_reference_cqf_is_empty_list_roundtrip(self):
        r = Reference()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_reference_alternate_reference_roundtrip(self):
        r = Reference()
        r.alternate_reference = "test-value"
        result = r.alternate_reference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_reference_cqf_measure_info_roundtrip(self):
        r = Reference()
        r.cqf_measure_info = "test-value"
        result = r.cqf_measure_info
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_reference_target_element_roundtrip(self):
        r = Reference()
        r.target_element = "test-value"
        result = r.target_element
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_relatedartifact_cqf_is_primary_citation_roundtrip(self):
        r = RelatedArtifact()
        r.cqf_is_primary_citation = "test-value"
        result = r.cqf_is_primary_citation
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_relatedartifact_artifact_is_owned_roundtrip(self):
        r = RelatedArtifact()
        r.artifact_is_owned = "test-value"
        result = r.artifact_is_owned
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_relatedartifact_cqf_model_info_settings_roundtrip(self):
        r = RelatedArtifact()
        r.cqf_model_info_settings = "test-value"
        result = r.cqf_model_info_settings
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_relatedartifact_cqf_publication_status_roundtrip(self):
        r = RelatedArtifact()
        r.cqf_publication_status = "test-value"
        result = r.cqf_publication_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_relatedartifact_cqf_is_empty_list_roundtrip(self):
        r = RelatedArtifact()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_relatedartifact_cqf_expansion_parameters_roundtrip(self):
        r = RelatedArtifact()
        r.cqf_expansion_parameters = "test-value"
        result = r.cqf_expansion_parameters
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_relatedartifact_cqf_publication_date_roundtrip(self):
        r = RelatedArtifact()
        r.cqf_publication_date = "test-value"
        result = r.cqf_publication_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_relatedperson_patient_proficiency_roundtrip(self):
        r = RelatedPerson()
        r.patient_proficiency = "test-value"
        result = r.patient_proficiency
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_relatedperson_individual_pronouns_roundtrip(self):
        r = RelatedPerson()
        r.individual_pronouns = "test-value"
        result = r.individual_pronouns
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_relatedperson_individual_gender_identity_roundtrip(self):
        r = RelatedPerson()
        r.individual_gender_identity = "test-value"
        result = r.individual_gender_identity
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_relatedperson_practitioner_animal_species_roundtrip(self):
        r = RelatedPerson()
        r.practitioner_animal_species = "test-value"
        result = r.practitioner_animal_species
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_relatedperson_individual_recorded_sex_or_gender_roundtrip(self):
        r = RelatedPerson()
        r.individual_recorded_sex_or_gender = "test-value"
        result = r.individual_recorded_sex_or_gender
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_requestorchestration_workflow_triggered_by_roundtrip(self):
        r = RequestOrchestration()
        r.workflow_triggered_by = "test-value"
        result = r.workflow_triggered_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_requestorchestration_timing_days_of_cycle_roundtrip(self):
        r = RequestOrchestration()
        r.timing_days_of_cycle = "test-value"
        result = r.timing_days_of_cycle
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_requestorchestration_workflow_generated_from_roundtrip(self):
        r = RequestOrchestration()
        r.workflow_generated_from = "test-value"
        result = r.workflow_generated_from
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_requestorchestration_workflow_release_date_roundtrip(self):
        r = RequestOrchestration()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_requestorchestration_workflow_episode_of_care_roundtrip(self):
        r = RequestOrchestration()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_requestorchestration_variable_roundtrip(self):
        r = RequestOrchestration()
        r.variable = "test-value"
        result = r.variable
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_requestorchestration_cqf_input_parameters_roundtrip(self):
        r = RequestOrchestration()
        r.cqf_input_parameters = "test-value"
        result = r.cqf_input_parameters
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_requestorchestration_workflow_complies_with_roundtrip(self):
        r = RequestOrchestration()
        r.workflow_complies_with = "test-value"
        result = r.workflow_complies_with
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_requirements_requirements_parent_roundtrip(self):
        r = Requirements()
        r.requirements_parent = "test-value"
        result = r.requirements_parent
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_requirements_replaces_roundtrip(self):
        r = Requirements()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_researchstudy_research_study_study_registration_roundtrip(self):
        r = ResearchStudy()
        r.research_study_study_registration = "test-value"
        result = r.research_study_study_registration
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_researchstudy_research_study_site_recruitment_roundtrip(self):
        r = ResearchStudy()
        r.research_study_site_recruitment = "test-value"
        result = r.research_study_site_recruitment
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_researchsubject_workflow_episode_of_care_roundtrip(self):
        r = ResearchSubject()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_cite_as_roundtrip(self):
        r = Resource()
        r.artifact_cite_as = "test-value"
        result = r.artifact_cite_as
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_cqf_artifact_comment_roundtrip(self):
        r = Resource()
        r.cqf_artifact_comment = "test-value"
        result = r.cqf_artifact_comment
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_patient_sex_parameter_for_clinical_use_roundtrip(self):
        r = Resource()
        r.patient_sex_parameter_for_clinical_use = "test-value"
        result = r.patient_sex_parameter_for_clinical_use
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_release_description_roundtrip(self):
        r = Resource()
        r.artifact_release_description = "test-value"
        result = r.artifact_release_description
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_structuredefinition_fmm_roundtrip(self):
        r = Resource()
        r.structuredefinition_fmm = "test-value"
        result = r.structuredefinition_fmm
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_experimental_roundtrip(self):
        r = Resource()
        r.artifact_experimental = "test-value"
        result = r.artifact_experimental
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_version_specific_use_roundtrip(self):
        r = Resource()
        r.version_specific_use = "test-value"
        result = r.version_specific_use
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifactassessment_disposition_roundtrip(self):
        r = Resource()
        r.artifactassessment_disposition = "test-value"
        result = r.artifactassessment_disposition
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_satisfies_requirement_roundtrip(self):
        r = Resource()
        r.satisfies_requirement = "test-value"
        result = r.satisfies_requirement
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_resource_pertains_to_goal_roundtrip(self):
        r = Resource()
        r.resource_pertains_to_goal = "test-value"
        result = r.resource_pertains_to_goal
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_description_roundtrip(self):
        r = Resource()
        r.artifact_description = "test-value"
        result = r.artifact_description
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_cqf_scope_roundtrip(self):
        r = Resource()
        r.cqf_scope = "test-value"
        result = r.cqf_scope
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_title_roundtrip(self):
        r = Resource()
        r.artifact_title = "test-value"
        result = r.artifact_title
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_cqf_measure_info_roundtrip(self):
        r = Resource()
        r.cqf_measure_info = "test-value"
        result = r.cqf_measure_info
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_derivation_reference_roundtrip(self):
        r = Resource()
        r.derivation_reference = "test-value"
        result = r.derivation_reference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_contact_roundtrip(self):
        r = Resource()
        r.artifact_contact = "test-value"
        result = r.artifact_contact
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_last_review_date_roundtrip(self):
        r = Resource()
        r.artifact_last_review_date = "test-value"
        result = r.artifact_last_review_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_author_roundtrip(self):
        r = Resource()
        r.artifact_author = "test-value"
        result = r.artifact_author
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_copyright_label_roundtrip(self):
        r = Resource()
        r.artifact_copyright_label = "test-value"
        result = r.artifact_copyright_label
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_identifier_roundtrip(self):
        r = Resource()
        r.artifact_identifier = "test-value"
        result = r.artifact_identifier
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifactassessment_workflow_status_roundtrip(self):
        r = Resource()
        r.artifactassessment_workflow_status = "test-value"
        result = r.artifactassessment_workflow_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_effective_period_roundtrip(self):
        r = Resource()
        r.artifact_effective_period = "test-value"
        result = r.artifact_effective_period
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_copyright_roundtrip(self):
        r = Resource()
        r.artifact_copyright = "test-value"
        result = r.artifact_copyright
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_purpose_roundtrip(self):
        r = Resource()
        r.artifact_purpose = "test-value"
        result = r.artifact_purpose
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_related_artifact_roundtrip(self):
        r = Resource()
        r.artifact_related_artifact = "test-value"
        result = r.artifact_related_artifact
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_cqf_direct_reference_code_roundtrip(self):
        r = Resource()
        r.cqf_direct_reference_code = "test-value"
        result = r.cqf_direct_reference_code
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_usage_roundtrip(self):
        r = Resource()
        r.artifact_usage = "test-value"
        result = r.artifact_usage
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_note_roundtrip(self):
        r = Resource()
        r.note = "test-value"
        result = r.note
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_version_specific_value_roundtrip(self):
        r = Resource()
        r.version_specific_value = "test-value"
        result = r.version_specific_value
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_name_roundtrip(self):
        r = Resource()
        r.artifact_name = "test-value"
        result = r.artifact_name
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_jurisdiction_roundtrip(self):
        r = Resource()
        r.artifact_jurisdiction = "test-value"
        result = r.artifact_jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_cqf_definition_term_roundtrip(self):
        r = Resource()
        r.cqf_definition_term = "test-value"
        result = r.cqf_definition_term
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_use_context_roundtrip(self):
        r = Resource()
        r.artifact_use_context = "test-value"
        result = r.artifact_use_context
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_release_label_roundtrip(self):
        r = Resource()
        r.artifact_release_label = "test-value"
        result = r.artifact_release_label
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_version_roundtrip(self):
        r = Resource()
        r.artifact_version = "test-value"
        result = r.artifact_version
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_url_roundtrip(self):
        r = Resource()
        r.artifact_url = "test-value"
        result = r.artifact_url
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_resource_instance_description_roundtrip(self):
        r = Resource()
        r.resource_instance_description = "test-value"
        result = r.resource_instance_description
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_version_algorithm_roundtrip(self):
        r = Resource()
        r.artifact_version_algorithm = "test-value"
        result = r.artifact_version_algorithm
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_publisher_roundtrip(self):
        r = Resource()
        r.artifact_publisher = "test-value"
        result = r.artifact_publisher
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_approval_date_roundtrip(self):
        r = Resource()
        r.artifact_approval_date = "test-value"
        result = r.artifact_approval_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_topic_roundtrip(self):
        r = Resource()
        r.artifact_topic = "test-value"
        result = r.artifact_topic
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_cqf_messages_roundtrip(self):
        r = Resource()
        r.cqf_messages = "test-value"
        result = r.cqf_messages
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_date_roundtrip(self):
        r = Resource()
        r.artifact_date = "test-value"
        result = r.artifact_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_status_roundtrip(self):
        r = Resource()
        r.artifact_status = "test-value"
        result = r.artifact_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_resource_instance_name_roundtrip(self):
        r = Resource()
        r.resource_instance_name = "test-value"
        result = r.resource_instance_name
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_resource_artifact_version_policy_roundtrip(self):
        r = Resource()
        r.artifact_version_policy = "test-value"
        result = r.artifact_version_policy
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_riskassessment_workflow_research_study_roundtrip(self):
        r = RiskAssessment()
        r.workflow_research_study = "test-value"
        result = r.workflow_research_study
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_riskassessment_workflow_episode_of_care_roundtrip(self):
        r = RiskAssessment()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_sampleddata_cqf_is_empty_list_roundtrip(self):
        r = SampledData()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_searchparameter_resource_approval_date_roundtrip(self):
        r = SearchParameter()
        r.resource_approval_date = "test-value"
        result = r.resource_approval_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_searchparameter_resource_last_review_date_roundtrip(self):
        r = SearchParameter()
        r.resource_last_review_date = "test-value"
        result = r.resource_last_review_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_searchparameter_structuredefinition_standards_status_roundtrip(self):
        r = SearchParameter()
        r.structuredefinition_standards_status = "test-value"
        result = r.structuredefinition_standards_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_searchparameter_resource_effective_period_roundtrip(self):
        r = SearchParameter()
        r.resource_effective_period = "test-value"
        result = r.resource_effective_period
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_searchparameter_replaces_roundtrip(self):
        r = SearchParameter()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_servicerequest_workflow_triggered_by_roundtrip(self):
        r = ServiceRequest()
        r.workflow_triggered_by = "test-value"
        result = r.workflow_triggered_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_servicerequest_procedure_directed_by_roundtrip(self):
        r = ServiceRequest()
        r.procedure_directed_by = "test-value"
        result = r.procedure_directed_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_servicerequest_workflow_research_study_roundtrip(self):
        r = ServiceRequest()
        r.workflow_research_study = "test-value"
        result = r.workflow_research_study
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_servicerequest_workflow_generated_from_roundtrip(self):
        r = ServiceRequest()
        r.workflow_generated_from = "test-value"
        result = r.workflow_generated_from
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_servicerequest_servicerequest_precondition_roundtrip(self):
        r = ServiceRequest()
        r.servicerequest_precondition = "test-value"
        result = r.servicerequest_precondition
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_servicerequest_servicerequest_questionnaire_request_roundtrip(self):
        r = ServiceRequest()
        r.servicerequest_questionnaire_request = "test-value"
        result = r.servicerequest_questionnaire_request
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_servicerequest_workflow_follow_on_of_roundtrip(self):
        r = ServiceRequest()
        r.workflow_follow_on_of = "test-value"
        result = r.workflow_follow_on_of
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_servicerequest_workflow_release_date_roundtrip(self):
        r = ServiceRequest()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_servicerequest_workflow_episode_of_care_roundtrip(self):
        r = ServiceRequest()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_servicerequest_request_performer_order_roundtrip(self):
        r = ServiceRequest()
        r.request_performer_order = "test-value"
        result = r.request_performer_order
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_servicerequest_servicerequest_order_callback_phone_number_roundtrip(self):
        r = ServiceRequest()
        r.servicerequest_order_callback_phone_number = "test-value"
        result = r.servicerequest_order_callback_phone_number
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_servicerequest_procedure_approach_body_structure_roundtrip(self):
        r = ServiceRequest()
        r.procedure_approach_body_structure = "test-value"
        result = r.procedure_approach_body_structure
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_servicerequest_workflow_complies_with_roundtrip(self):
        r = ServiceRequest()
        r.workflow_complies_with = "test-value"
        result = r.workflow_complies_with
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_servicerequest_request_status_reason_roundtrip(self):
        r = ServiceRequest()
        r.request_status_reason = "test-value"
        result = r.request_status_reason
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_servicerequest_procedure_target_body_structure_roundtrip(self):
        r = ServiceRequest()
        r.procedure_target_body_structure = "test-value"
        result = r.procedure_target_body_structure
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_signature_cqf_is_empty_list_roundtrip(self):
        r = Signature()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_specimen_observation_body_position_roundtrip(self):
        r = Specimen()
        r.observation_body_position = "test-value"
        result = r.observation_body_position
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_specimen_specimen_sequence_number_roundtrip(self):
        r = Specimen()
        r.specimen_sequence_number = "test-value"
        result = r.specimen_sequence_number
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_specimen_specimen_is_dry_weight_roundtrip(self):
        r = Specimen()
        r.specimen_is_dry_weight = "test-value"
        result = r.specimen_is_dry_weight
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_specimen_specimen_additive_roundtrip(self):
        r = Specimen()
        r.specimen_additive = "test-value"
        result = r.specimen_additive
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_specimen_specimen_special_handling_roundtrip(self):
        r = Specimen()
        r.specimen_special_handling = "test-value"
        result = r.specimen_special_handling
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_specimen_specimen_collection_priority_roundtrip(self):
        r = Specimen()
        r.specimen_collection_priority = "test-value"
        result = r.specimen_collection_priority
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_specimen_specimen_reject_reason_roundtrip(self):
        r = Specimen()
        r.specimen_reject_reason = "test-value"
        result = r.specimen_reject_reason
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_specimen_specimen_processing_time_roundtrip(self):
        r = Specimen()
        r.specimen_processing_time = "test-value"
        result = r.specimen_processing_time
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_specimen_procedure_approach_body_structure_roundtrip(self):
        r = Specimen()
        r.procedure_approach_body_structure = "test-value"
        result = r.procedure_approach_body_structure
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_specimendefinition_replaces_roundtrip(self):
        r = SpecimenDefinition()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_structuredefinition_type_characteristics_roundtrip(self):
        r = StructureDefinition()
        r.structuredefinition_type_characteristics = "test-value"
        result = r.structuredefinition_type_characteristics
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_resource_approval_date_roundtrip(self):
        r = StructureDefinition()
        r.resource_approval_date = "test-value"
        result = r.resource_approval_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_elementdefinition_conceptmap_roundtrip(self):
        r = StructureDefinition()
        r.elementdefinition_conceptmap = "test-value"
        result = r.elementdefinition_conceptmap
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_structuredefinition_complies_with_profile_roundtrip(self):
        r = StructureDefinition()
        r.structuredefinition_complies_with_profile = "test-value"
        result = r.structuredefinition_complies_with_profile
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_structuredefinition_category_roundtrip(self):
        r = StructureDefinition()
        r.structuredefinition_category = "test-value"
        result = r.structuredefinition_category
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_cqf_model_info_primary_code_path_roundtrip(self):
        r = StructureDefinition()
        r.cqf_model_info_primary_code_path = "test-value"
        result = r.cqf_model_info_primary_code_path
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_structuredefinition_security_category_roundtrip(self):
        r = StructureDefinition()
        r.structuredefinition_security_category = "test-value"
        result = r.structuredefinition_security_category
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_structuredefinition_ancestor_roundtrip(self):
        r = StructureDefinition()
        r.structuredefinition_ancestor = "test-value"
        result = r.structuredefinition_ancestor
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_structuredefinition_inheritance_control_roundtrip(self):
        r = StructureDefinition()
        r.structuredefinition_inheritance_control = "test-value"
        result = r.structuredefinition_inheritance_control
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_cqf_should_trace_dependency_roundtrip(self):
        r = StructureDefinition()
        r.cqf_should_trace_dependency = "test-value"
        result = r.cqf_should_trace_dependency
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_ext_11179_permitted_value_valueset_roundtrip(self):
        r = StructureDefinition()
        r.ext_11179_permitted_value_valueset = "test-value"
        result = r.ext_11179_permitted_value_valueset
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_resource_last_review_date_roundtrip(self):
        r = StructureDefinition()
        r.resource_last_review_date = "test-value"
        result = r.resource_last_review_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_structuredefinition_fmm_no_warnings_roundtrip(self):
        r = StructureDefinition()
        r.structuredefinition_fmm_no_warnings = "test-value"
        result = r.structuredefinition_fmm_no_warnings
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_structuredefinition_standards_status_roundtrip(self):
        r = StructureDefinition()
        r.structuredefinition_standards_status = "test-value"
        result = r.structuredefinition_standards_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_resource_effective_period_roundtrip(self):
        r = StructureDefinition()
        r.resource_effective_period = "test-value"
        result = r.resource_effective_period
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_structuredefinition_template_status_roundtrip(self):
        r = StructureDefinition()
        r.structuredefinition_template_status = "test-value"
        result = r.structuredefinition_template_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_structuredefinition_summary_roundtrip(self):
        r = StructureDefinition()
        r.structuredefinition_summary = "test-value"
        result = r.structuredefinition_summary
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_ext_11179_permitted_value_conceptmap_roundtrip(self):
        r = StructureDefinition()
        r.ext_11179_permitted_value_conceptmap = "test-value"
        result = r.ext_11179_permitted_value_conceptmap
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_obligation_roundtrip(self):
        r = StructureDefinition()
        r.obligation = "test-value"
        result = r.obligation
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_cqf_model_info_is_retrievable_roundtrip(self):
        r = StructureDefinition()
        r.cqf_model_info_is_retrievable = "test-value"
        result = r.cqf_model_info_is_retrievable
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_structuredefinition_impose_profile_roundtrip(self):
        r = StructureDefinition()
        r.structuredefinition_impose_profile = "test-value"
        result = r.structuredefinition_impose_profile
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_replaces_roundtrip(self):
        r = StructureDefinition()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_structuredefinition_interface_roundtrip(self):
        r = StructureDefinition()
        r.structuredefinition_interface = "test-value"
        result = r.structuredefinition_interface
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_cqf_model_info_label_roundtrip(self):
        r = StructureDefinition()
        r.cqf_model_info_label = "test-value"
        result = r.cqf_model_info_label
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_cqf_model_info_is_included_roundtrip(self):
        r = StructureDefinition()
        r.cqf_model_info_is_included = "test-value"
        result = r.cqf_model_info_is_included
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_structuredefinition_codegen_super_roundtrip(self):
        r = StructureDefinition()
        r.structuredefinition_codegen_super = "test-value"
        result = r.structuredefinition_codegen_super
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_structuredefinition_table_name_roundtrip(self):
        r = StructureDefinition()
        r.structuredefinition_table_name = "test-value"
        result = r.structuredefinition_table_name
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuredefinition_structuredefinition_applicable_version_roundtrip(self):
        r = StructureDefinition()
        r.structuredefinition_applicable_version = "test-value"
        result = r.structuredefinition_applicable_version
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuremap_resource_approval_date_roundtrip(self):
        r = StructureMap()
        r.resource_approval_date = "test-value"
        result = r.resource_approval_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuremap_resource_last_review_date_roundtrip(self):
        r = StructureMap()
        r.resource_last_review_date = "test-value"
        result = r.resource_last_review_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuremap_resource_effective_period_roundtrip(self):
        r = StructureMap()
        r.resource_effective_period = "test-value"
        result = r.resource_effective_period
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_structuremap_replaces_roundtrip(self):
        r = StructureMap()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_subscription_subscription_best_effort_roundtrip(self):
        r = Subscription()
        r.subscription_best_effort = "test-value"
        result = r.subscription_best_effort
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_subscriptiontopic_replaces_roundtrip(self):
        r = SubscriptionTopic()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_substance_medication_manufacturing_batch_roundtrip(self):
        r = Substance()
        r.medication_manufacturing_batch = "test-value"
        result = r.medication_manufacturing_batch
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_supplydelivery_workflow_triggered_by_roundtrip(self):
        r = SupplyDelivery()
        r.workflow_triggered_by = "test-value"
        result = r.workflow_triggered_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_supplydelivery_workflow_research_study_roundtrip(self):
        r = SupplyDelivery()
        r.workflow_research_study = "test-value"
        result = r.workflow_research_study
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_supplydelivery_workflow_episode_of_care_roundtrip(self):
        r = SupplyDelivery()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_supplydelivery_event_status_reason_roundtrip(self):
        r = SupplyDelivery()
        r.event_status_reason = "test-value"
        result = r.event_status_reason
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_supplydelivery_workflow_adheres_to_roundtrip(self):
        r = SupplyDelivery()
        r.workflow_adheres_to = "test-value"
        result = r.workflow_adheres_to
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_supplydelivery_event_event_history_roundtrip(self):
        r = SupplyDelivery()
        r.event_event_history = "test-value"
        result = r.event_event_history
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_supplydelivery_workflow_shall_comply_with_roundtrip(self):
        r = SupplyDelivery()
        r.workflow_shall_comply_with = "test-value"
        result = r.workflow_shall_comply_with
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_supplydelivery_event_location_roundtrip(self):
        r = SupplyDelivery()
        r.event_location = "test-value"
        result = r.event_location
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_supplyrequest_workflow_triggered_by_roundtrip(self):
        r = SupplyRequest()
        r.workflow_triggered_by = "test-value"
        result = r.workflow_triggered_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_supplyrequest_workflow_generated_from_roundtrip(self):
        r = SupplyRequest()
        r.workflow_generated_from = "test-value"
        result = r.workflow_generated_from
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_supplyrequest_request_replaces_roundtrip(self):
        r = SupplyRequest()
        r.request_replaces = "test-value"
        result = r.request_replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_supplyrequest_workflow_release_date_roundtrip(self):
        r = SupplyRequest()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_supplyrequest_workflow_episode_of_care_roundtrip(self):
        r = SupplyRequest()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_supplyrequest_workflow_complies_with_roundtrip(self):
        r = SupplyRequest()
        r.workflow_complies_with = "test-value"
        result = r.workflow_complies_with
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_supplyrequest_request_status_reason_roundtrip(self):
        r = SupplyRequest()
        r.request_status_reason = "test-value"
        result = r.request_status_reason
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_supplyrequest_workflow_shall_comply_with_roundtrip(self):
        r = SupplyRequest()
        r.workflow_shall_comply_with = "test-value"
        result = r.workflow_shall_comply_with
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_task_workflow_triggered_by_roundtrip(self):
        r = Task()
        r.workflow_triggered_by = "test-value"
        result = r.workflow_triggered_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_task_workflow_research_study_roundtrip(self):
        r = Task()
        r.workflow_research_study = "test-value"
        result = r.workflow_research_study
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_task_workflow_generated_from_roundtrip(self):
        r = Task()
        r.workflow_generated_from = "test-value"
        result = r.workflow_generated_from
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_task_request_do_not_perform_roundtrip(self):
        r = Task()
        r.request_do_not_perform = "test-value"
        result = r.request_do_not_perform
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_task_request_replaces_roundtrip(self):
        r = Task()
        r.request_replaces = "test-value"
        result = r.request_replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_task_task_replaces_roundtrip(self):
        r = Task()
        r.task_replaces = "test-value"
        result = r.task_replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_task_workflow_follow_on_of_roundtrip(self):
        r = Task()
        r.workflow_follow_on_of = "test-value"
        result = r.workflow_follow_on_of
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_task_workflow_release_date_roundtrip(self):
        r = Task()
        r.workflow_release_date = "test-value"
        result = r.workflow_release_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_task_request_performer_order_roundtrip(self):
        r = Task()
        r.request_performer_order = "test-value"
        result = r.request_performer_order
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_task_event_event_history_roundtrip(self):
        r = Task()
        r.event_event_history = "test-value"
        result = r.event_event_history
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_task_workflow_complies_with_roundtrip(self):
        r = Task()
        r.workflow_complies_with = "test-value"
        result = r.workflow_complies_with
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_terminologycapabilities_replaces_roundtrip(self):
        r = TerminologyCapabilities()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_testscript_replaces_roundtrip(self):
        r = TestScript()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_timing_timing_day_of_month_roundtrip(self):
        r = Timing()
        r.timing_day_of_month = "test-value"
        result = r.timing_day_of_month
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_timing_cqf_is_empty_list_roundtrip(self):
        r = Timing()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_timing_timing_exact_roundtrip(self):
        r = Timing()
        r.timing_exact = "test-value"
        result = r.timing_exact
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_triggerdefinition_cqf_is_empty_list_roundtrip(self):
        r = TriggerDefinition()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_triggerdefinition_cqf_parameter_definition_roundtrip(self):
        r = TriggerDefinition()
        r.cqf_parameter_definition = "test-value"
        result = r.cqf_parameter_definition
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_usagecontext_cqf_is_empty_list_roundtrip(self):
        r = UsageContext()
        r.cqf_is_empty_list = "test-value"
        result = r.cqf_is_empty_list
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_usagecontext_usagecontext_group_roundtrip(self):
        r = UsageContext()
        r.usagecontext_group = "test-value"
        result = r.usagecontext_group
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_unclosed_roundtrip(self):
        r = ValueSet()
        r.valueset_unclosed = "test-value"
        result = r.valueset_unclosed
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_resource_approval_date_roundtrip(self):
        r = ValueSet()
        r.resource_approval_date = "test-value"
        result = r.resource_approval_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_compose_created_by_roundtrip(self):
        r = ValueSet()
        r.valueset_compose_created_by = "test-value"
        result = r.valueset_compose_created_by
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_terminology_resource_identifier_metadata_roundtrip(self):
        r = ValueSet()
        r.terminology_resource_identifier_metadata = "test-value"
        result = r.terminology_resource_identifier_metadata
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_concept_order_roundtrip(self):
        r = ValueSet()
        r.valueset_concept_order = "test-value"
        result = r.valueset_concept_order
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_label_roundtrip(self):
        r = ValueSet()
        r.valueset_label = "test-value"
        result = r.valueset_label
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_resource_last_review_date_roundtrip(self):
        r = ValueSet()
        r.resource_last_review_date = "test-value"
        result = r.resource_last_review_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_toocostly_roundtrip(self):
        r = ValueSet()
        r.valueset_toocostly = "test-value"
        result = r.valueset_toocostly
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_map_roundtrip(self):
        r = ValueSet()
        r.valueset_map = "test-value"
        result = r.valueset_map
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_system_ref_roundtrip(self):
        r = ValueSet()
        r.valueset_system_ref = "test-value"
        result = r.valueset_system_ref
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_special_status_roundtrip(self):
        r = ValueSet()
        r.valueset_special_status = "test-value"
        result = r.valueset_special_status
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_compose_creation_date_roundtrip(self):
        r = ValueSet()
        r.valueset_compose_creation_date = "test-value"
        result = r.valueset_compose_creation_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_concept_definition_roundtrip(self):
        r = ValueSet()
        r.valueset_concept_definition = "test-value"
        result = r.valueset_concept_definition
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_resource_effective_period_roundtrip(self):
        r = ValueSet()
        r.resource_effective_period = "test-value"
        result = r.resource_effective_period
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_concept_comments_roundtrip(self):
        r = ValueSet()
        r.valueset_concept_comments = "test-value"
        result = r.valueset_concept_comments
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_source_reference_roundtrip(self):
        r = ValueSet()
        r.valueset_source_reference = "test-value"
        result = r.valueset_source_reference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_compose_include_value_set_title_roundtrip(self):
        r = ValueSet()
        r.valueset_compose_include_value_set_title = "test-value"
        result = r.valueset_compose_include_value_set_title
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_system_name_roundtrip(self):
        r = ValueSet()
        r.valueset_system_name = "test-value"
        result = r.valueset_system_name
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_parameter_source_roundtrip(self):
        r = ValueSet()
        r.valueset_parameter_source = "test-value"
        result = r.valueset_parameter_source
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_expansion_source_roundtrip(self):
        r = ValueSet()
        r.valueset_expansion_source = "test-value"
        result = r.valueset_expansion_source
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_system_roundtrip(self):
        r = ValueSet()
        r.valueset_system = "test-value"
        result = r.valueset_system
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_warning_roundtrip(self):
        r = ValueSet()
        r.valueset_warning = "test-value"
        result = r.valueset_warning
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_replaces_roundtrip(self):
        r = ValueSet()
        r.replaces = "test-value"
        result = r.replaces
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_case_sensitive_roundtrip(self):
        r = ValueSet()
        r.valueset_case_sensitive = "test-value"
        result = r.valueset_case_sensitive
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_trusted_expansion_roundtrip(self):
        r = ValueSet()
        r.valueset_trusted_expansion = "test-value"
        result = r.valueset_trusted_expansion
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_expression_roundtrip(self):
        r = ValueSet()
        r.valueset_expression = "test-value"
        result = r.valueset_expression
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_supplement_roundtrip(self):
        r = ValueSet()
        r.valueset_supplement = "test-value"
        result = r.valueset_supplement
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_authoritative_source_roundtrip(self):
        r = ValueSet()
        r.valueset_authoritative_source = "test-value"
        result = r.valueset_authoritative_source
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_usage_roundtrip(self):
        r = ValueSet()
        r.valueset_usage = "test-value"
        result = r.valueset_usage
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_other_title_roundtrip(self):
        r = ValueSet()
        r.valueset_other_title = "test-value"
        result = r.valueset_other_title
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_deprecated_roundtrip(self):
        r = ValueSet()
        r.valueset_deprecated = "test-value"
        result = r.valueset_deprecated
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_key_word_roundtrip(self):
        r = ValueSet()
        r.valueset_key_word = "test-value"
        result = r.valueset_key_word
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_workflow_status_description_roundtrip(self):
        r = ValueSet()
        r.valueset_workflow_status_description = "test-value"
        result = r.valueset_workflow_status_description
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_system_title_roundtrip(self):
        r = ValueSet()
        r.valueset_system_title = "test-value"
        result = r.valueset_system_title
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_extensible_roundtrip(self):
        r = ValueSet()
        r.valueset_extensible = "test-value"
        result = r.valueset_extensible
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_coding_sctdescid_roundtrip(self):
        r = ValueSet()
        r.coding_sctdescid = "test-value"
        result = r.coding_sctdescid
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_other_name_roundtrip(self):
        r = ValueSet()
        r.valueset_other_name = "test-value"
        result = r.valueset_other_name
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_valueset_valueset_rules_text_roundtrip(self):
        r = ValueSet()
        r.valueset_rules_text = "test-value"
        result = r.valueset_rules_text
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_visionprescription_workflow_episode_of_care_roundtrip(self):
        r = VisionPrescription()
        r.workflow_episode_of_care = "test-value"
        result = r.workflow_episode_of_care
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

