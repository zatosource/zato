from __future__ import annotations

from uuid import uuid4

from zato.fhir.r4_0_1 import (
    Account,
    ActivityDefinition,
    AdverseEvent,
    AllergyIntolerance,
    Appointment,
    AppointmentResponse,
    AuditEvent,
    Basic,
    Binary,
    BiologicallyDerivedProduct,
    BodyStructure,
    Bundle,
    CapabilityStatement,
    CarePlan,
    CareTeam,
    CatalogEntry,
    ChargeItem,
    ChargeItemDefinition,
    Claim,
    ClaimResponse,
    ClinicalImpression,
    CodeSystem,
    Communication,
    CommunicationRequest,
    CompartmentDefinition,
    Composition,
    ConceptMap,
    Condition,
    Consent,
    Contract,
    Coverage,
    CoverageEligibilityRequest,
    CoverageEligibilityResponse,
    DetectedIssue,
    Device,
    DeviceDefinition,
    DeviceMetric,
    DeviceRequest,
    DeviceUseStatement,
    DiagnosticReport,
    DocumentManifest,
    DocumentReference,
    EffectEvidenceSynthesis,
    Encounter,
    Endpoint,
    EnrollmentRequest,
    EnrollmentResponse,
    EpisodeOfCare,
    EventDefinition,
    Evidence,
    EvidenceVariable,
    ExampleScenario,
    ExplanationOfBenefit,
    FamilyMemberHistory,
    Flag,
    Goal,
    GraphDefinition,
    Group,
    GuidanceResponse,
    HealthcareService,
    ImagingStudy,
    Immunization,
    ImmunizationEvaluation,
    ImmunizationRecommendation,
    ImplementationGuide,
    InsurancePlan,
    Invoice,
    Library,
    Linkage,
    List,
    Location,
    Measure,
    MeasureReport,
    Media,
    Medication,
    MedicationAdministration,
    MedicationDispense,
    MedicationKnowledge,
    MedicationRequest,
    MedicationStatement,
    MedicinalProduct,
    MedicinalProductAuthorization,
    MedicinalProductContraindication,
    MedicinalProductIndication,
    MedicinalProductIngredient,
    MedicinalProductInteraction,
    MedicinalProductManufactured,
    MedicinalProductPackaged,
    MedicinalProductPharmaceutical,
    MedicinalProductUndesirableEffect,
    MessageDefinition,
    MessageHeader,
    MolecularSequence,
    NamingSystem,
    NutritionOrder,
    Observation,
    ObservationDefinition,
    OperationDefinition,
    OperationOutcome,
    Organization,
    OrganizationAffiliation,
    Parameters,
    Patient,
    PaymentNotice,
    PaymentReconciliation,
    Person,
    PlanDefinition,
    Practitioner,
    PractitionerRole,
    Procedure,
    Provenance,
    Questionnaire,
    QuestionnaireResponse,
    RelatedPerson,
    RequestGroup,
    ResearchDefinition,
    ResearchElementDefinition,
    ResearchStudy,
    ResearchSubject,
    RiskAssessment,
    RiskEvidenceSynthesis,
    Schedule,
    SearchParameter,
    ServiceRequest,
    Slot,
    Specimen,
    SpecimenDefinition,
    StructureDefinition,
    StructureMap,
    Subscription,
    Substance,
    SubstanceNucleicAcid,
    SubstancePolymer,
    SubstanceProtein,
    SubstanceReferenceInformation,
    SubstanceSourceMaterial,
    SubstanceSpecification,
    SupplyDelivery,
    SupplyRequest,
    Task,
    TerminologyCapabilities,
    TestReport,
    TestScript,
    ValueSet,
    VerificationResult,
    VisionPrescription,
    actualgroup,
    bmi,
    bodyheight,
    bodytemp,
    bodyweight,
    bp,
    catalog,
    cdshooksguidanceresponse,
    cdshooksrequestgroup,
    cdshooksserviceplandefinition,
    cholesterol,
    clinicaldocument,
    computableplandefinition,
    cqllibrary,
    devicemetricobservation,
    groupdefinition,
    hdlcholesterol,
    headcircum,
    heartrate,
    hlaresult,
    ldlcholesterol,
    lipidprofile,
    oxygensat,
    picoelement,
    resprate,
    shareableactivitydefinition,
    shareablecodesystem,
    shareablelibrary,
    shareablemeasure,
    shareableplandefinition,
    shareablevalueset,
    synthesis,
    triglyceride,
    vitalsigns,
    vitalspanel,
)


def fake_account(
    id_: str | None = None,
) -> Account:
    obj = Account()
    obj.id = id_ or f"fake-account-{uuid4().hex[:8]}"
    return obj


def fake_activity_definition(
    id_: str | None = None,
) -> ActivityDefinition:
    obj = ActivityDefinition()
    obj.id = id_ or f"fake-activity_definition-{uuid4().hex[:8]}"
    return obj


def fake_adverse_event(
    id_: str | None = None,
) -> AdverseEvent:
    obj = AdverseEvent()
    obj.id = id_ or f"fake-adverse_event-{uuid4().hex[:8]}"
    return obj


def fake_allergy_intolerance(
    id_: str | None = None,
) -> AllergyIntolerance:
    obj = AllergyIntolerance()
    obj.id = id_ or f"fake-allergy_intolerance-{uuid4().hex[:8]}"
    return obj


def fake_appointment(
    id_: str | None = None,
) -> Appointment:
    obj = Appointment()
    obj.id = id_ or f"fake-appointment-{uuid4().hex[:8]}"
    return obj


def fake_appointment_response(
    id_: str | None = None,
) -> AppointmentResponse:
    obj = AppointmentResponse()
    obj.id = id_ or f"fake-appointment_response-{uuid4().hex[:8]}"
    return obj


def fake_audit_event(
    id_: str | None = None,
) -> AuditEvent:
    obj = AuditEvent()
    obj.id = id_ or f"fake-audit_event-{uuid4().hex[:8]}"
    return obj


def fake_basic(
    id_: str | None = None,
) -> Basic:
    obj = Basic()
    obj.id = id_ or f"fake-basic-{uuid4().hex[:8]}"
    return obj


def fake_binary(
    id_: str | None = None,
) -> Binary:
    obj = Binary()
    obj.id = id_ or f"fake-binary-{uuid4().hex[:8]}"
    return obj


def fake_biologically_derived_product(
    id_: str | None = None,
) -> BiologicallyDerivedProduct:
    obj = BiologicallyDerivedProduct()
    obj.id = id_ or f"fake-biologically_derived_product-{uuid4().hex[:8]}"
    return obj


def fake_body_structure(
    id_: str | None = None,
) -> BodyStructure:
    obj = BodyStructure()
    obj.id = id_ or f"fake-body_structure-{uuid4().hex[:8]}"
    return obj


def fake_bundle(
    id_: str | None = None,
) -> Bundle:
    obj = Bundle()
    obj.id = id_ or f"fake-bundle-{uuid4().hex[:8]}"
    return obj


def fake_capability_statement(
    id_: str | None = None,
) -> CapabilityStatement:
    obj = CapabilityStatement()
    obj.id = id_ or f"fake-capability_statement-{uuid4().hex[:8]}"
    return obj


def fake_care_plan(
    id_: str | None = None,
) -> CarePlan:
    obj = CarePlan()
    obj.id = id_ or f"fake-care_plan-{uuid4().hex[:8]}"
    return obj


def fake_care_team(
    id_: str | None = None,
) -> CareTeam:
    obj = CareTeam()
    obj.id = id_ or f"fake-care_team-{uuid4().hex[:8]}"
    return obj


def fake_catalog_entry(
    id_: str | None = None,
) -> CatalogEntry:
    obj = CatalogEntry()
    obj.id = id_ or f"fake-catalog_entry-{uuid4().hex[:8]}"
    return obj


def fake_charge_item(
    id_: str | None = None,
) -> ChargeItem:
    obj = ChargeItem()
    obj.id = id_ or f"fake-charge_item-{uuid4().hex[:8]}"
    return obj


def fake_charge_item_definition(
    id_: str | None = None,
) -> ChargeItemDefinition:
    obj = ChargeItemDefinition()
    obj.id = id_ or f"fake-charge_item_definition-{uuid4().hex[:8]}"
    return obj


def fake_claim(
    id_: str | None = None,
) -> Claim:
    obj = Claim()
    obj.id = id_ or f"fake-claim-{uuid4().hex[:8]}"
    return obj


def fake_claim_response(
    id_: str | None = None,
) -> ClaimResponse:
    obj = ClaimResponse()
    obj.id = id_ or f"fake-claim_response-{uuid4().hex[:8]}"
    return obj


def fake_clinical_impression(
    id_: str | None = None,
) -> ClinicalImpression:
    obj = ClinicalImpression()
    obj.id = id_ or f"fake-clinical_impression-{uuid4().hex[:8]}"
    return obj


def fake_code_system(
    id_: str | None = None,
) -> CodeSystem:
    obj = CodeSystem()
    obj.id = id_ or f"fake-code_system-{uuid4().hex[:8]}"
    return obj


def fake_communication(
    id_: str | None = None,
) -> Communication:
    obj = Communication()
    obj.id = id_ or f"fake-communication-{uuid4().hex[:8]}"
    return obj


def fake_communication_request(
    id_: str | None = None,
) -> CommunicationRequest:
    obj = CommunicationRequest()
    obj.id = id_ or f"fake-communication_request-{uuid4().hex[:8]}"
    return obj


def fake_compartment_definition(
    id_: str | None = None,
) -> CompartmentDefinition:
    obj = CompartmentDefinition()
    obj.id = id_ or f"fake-compartment_definition-{uuid4().hex[:8]}"
    return obj


def fake_composition(
    id_: str | None = None,
) -> Composition:
    obj = Composition()
    obj.id = id_ or f"fake-composition-{uuid4().hex[:8]}"
    return obj


def fake_concept_map(
    id_: str | None = None,
) -> ConceptMap:
    obj = ConceptMap()
    obj.id = id_ or f"fake-concept_map-{uuid4().hex[:8]}"
    return obj


def fake_condition(
    id_: str | None = None,
) -> Condition:
    obj = Condition()
    obj.id = id_ or f"fake-condition-{uuid4().hex[:8]}"
    return obj


def fake_consent(
    id_: str | None = None,
) -> Consent:
    obj = Consent()
    obj.id = id_ or f"fake-consent-{uuid4().hex[:8]}"
    return obj


def fake_contract(
    id_: str | None = None,
) -> Contract:
    obj = Contract()
    obj.id = id_ or f"fake-contract-{uuid4().hex[:8]}"
    return obj


def fake_coverage(
    id_: str | None = None,
) -> Coverage:
    obj = Coverage()
    obj.id = id_ or f"fake-coverage-{uuid4().hex[:8]}"
    return obj


def fake_coverage_eligibility_request(
    id_: str | None = None,
) -> CoverageEligibilityRequest:
    obj = CoverageEligibilityRequest()
    obj.id = id_ or f"fake-coverage_eligibility_request-{uuid4().hex[:8]}"
    return obj


def fake_coverage_eligibility_response(
    id_: str | None = None,
) -> CoverageEligibilityResponse:
    obj = CoverageEligibilityResponse()
    obj.id = id_ or f"fake-coverage_eligibility_response-{uuid4().hex[:8]}"
    return obj


def fake_detected_issue(
    id_: str | None = None,
) -> DetectedIssue:
    obj = DetectedIssue()
    obj.id = id_ or f"fake-detected_issue-{uuid4().hex[:8]}"
    return obj


def fake_device(
    id_: str | None = None,
) -> Device:
    obj = Device()
    obj.id = id_ or f"fake-device-{uuid4().hex[:8]}"
    return obj


def fake_device_definition(
    id_: str | None = None,
) -> DeviceDefinition:
    obj = DeviceDefinition()
    obj.id = id_ or f"fake-device_definition-{uuid4().hex[:8]}"
    return obj


def fake_device_metric(
    id_: str | None = None,
) -> DeviceMetric:
    obj = DeviceMetric()
    obj.id = id_ or f"fake-device_metric-{uuid4().hex[:8]}"
    return obj


def fake_device_request(
    id_: str | None = None,
) -> DeviceRequest:
    obj = DeviceRequest()
    obj.id = id_ or f"fake-device_request-{uuid4().hex[:8]}"
    return obj


def fake_device_use_statement(
    id_: str | None = None,
) -> DeviceUseStatement:
    obj = DeviceUseStatement()
    obj.id = id_ or f"fake-device_use_statement-{uuid4().hex[:8]}"
    return obj


def fake_diagnostic_report(
    id_: str | None = None,
) -> DiagnosticReport:
    obj = DiagnosticReport()
    obj.id = id_ or f"fake-diagnostic_report-{uuid4().hex[:8]}"
    return obj


def fake_document_manifest(
    id_: str | None = None,
) -> DocumentManifest:
    obj = DocumentManifest()
    obj.id = id_ or f"fake-document_manifest-{uuid4().hex[:8]}"
    return obj


def fake_document_reference(
    id_: str | None = None,
) -> DocumentReference:
    obj = DocumentReference()
    obj.id = id_ or f"fake-document_reference-{uuid4().hex[:8]}"
    return obj


def fake_effect_evidence_synthesis(
    id_: str | None = None,
) -> EffectEvidenceSynthesis:
    obj = EffectEvidenceSynthesis()
    obj.id = id_ or f"fake-effect_evidence_synthesis-{uuid4().hex[:8]}"
    return obj


def fake_encounter(
    id_: str | None = None,
) -> Encounter:
    obj = Encounter()
    obj.id = id_ or f"fake-encounter-{uuid4().hex[:8]}"
    return obj


def fake_endpoint(
    id_: str | None = None,
) -> Endpoint:
    obj = Endpoint()
    obj.id = id_ or f"fake-endpoint-{uuid4().hex[:8]}"
    return obj


def fake_enrollment_request(
    id_: str | None = None,
) -> EnrollmentRequest:
    obj = EnrollmentRequest()
    obj.id = id_ or f"fake-enrollment_request-{uuid4().hex[:8]}"
    return obj


def fake_enrollment_response(
    id_: str | None = None,
) -> EnrollmentResponse:
    obj = EnrollmentResponse()
    obj.id = id_ or f"fake-enrollment_response-{uuid4().hex[:8]}"
    return obj


def fake_episode_of_care(
    id_: str | None = None,
) -> EpisodeOfCare:
    obj = EpisodeOfCare()
    obj.id = id_ or f"fake-episode_of_care-{uuid4().hex[:8]}"
    return obj


def fake_event_definition(
    id_: str | None = None,
) -> EventDefinition:
    obj = EventDefinition()
    obj.id = id_ or f"fake-event_definition-{uuid4().hex[:8]}"
    return obj


def fake_evidence(
    id_: str | None = None,
) -> Evidence:
    obj = Evidence()
    obj.id = id_ or f"fake-evidence-{uuid4().hex[:8]}"
    return obj


def fake_evidence_variable(
    id_: str | None = None,
) -> EvidenceVariable:
    obj = EvidenceVariable()
    obj.id = id_ or f"fake-evidence_variable-{uuid4().hex[:8]}"
    return obj


def fake_example_scenario(
    id_: str | None = None,
) -> ExampleScenario:
    obj = ExampleScenario()
    obj.id = id_ or f"fake-example_scenario-{uuid4().hex[:8]}"
    return obj


def fake_explanation_of_benefit(
    id_: str | None = None,
) -> ExplanationOfBenefit:
    obj = ExplanationOfBenefit()
    obj.id = id_ or f"fake-explanation_of_benefit-{uuid4().hex[:8]}"
    return obj


def fake_family_member_history(
    id_: str | None = None,
) -> FamilyMemberHistory:
    obj = FamilyMemberHistory()
    obj.id = id_ or f"fake-family_member_history-{uuid4().hex[:8]}"
    return obj


def fake_flag(
    id_: str | None = None,
) -> Flag:
    obj = Flag()
    obj.id = id_ or f"fake-flag-{uuid4().hex[:8]}"
    return obj


def fake_goal(
    id_: str | None = None,
) -> Goal:
    obj = Goal()
    obj.id = id_ or f"fake-goal-{uuid4().hex[:8]}"
    return obj


def fake_graph_definition(
    id_: str | None = None,
) -> GraphDefinition:
    obj = GraphDefinition()
    obj.id = id_ or f"fake-graph_definition-{uuid4().hex[:8]}"
    return obj


def fake_group(
    id_: str | None = None,
) -> Group:
    obj = Group()
    obj.id = id_ or f"fake-group-{uuid4().hex[:8]}"
    return obj


def fake_guidance_response(
    id_: str | None = None,
) -> GuidanceResponse:
    obj = GuidanceResponse()
    obj.id = id_ or f"fake-guidance_response-{uuid4().hex[:8]}"
    return obj


def fake_healthcare_service(
    id_: str | None = None,
) -> HealthcareService:
    obj = HealthcareService()
    obj.id = id_ or f"fake-healthcare_service-{uuid4().hex[:8]}"
    return obj


def fake_imaging_study(
    id_: str | None = None,
) -> ImagingStudy:
    obj = ImagingStudy()
    obj.id = id_ or f"fake-imaging_study-{uuid4().hex[:8]}"
    return obj


def fake_immunization(
    id_: str | None = None,
) -> Immunization:
    obj = Immunization()
    obj.id = id_ or f"fake-immunization-{uuid4().hex[:8]}"
    return obj


def fake_immunization_evaluation(
    id_: str | None = None,
) -> ImmunizationEvaluation:
    obj = ImmunizationEvaluation()
    obj.id = id_ or f"fake-immunization_evaluation-{uuid4().hex[:8]}"
    return obj


def fake_immunization_recommendation(
    id_: str | None = None,
) -> ImmunizationRecommendation:
    obj = ImmunizationRecommendation()
    obj.id = id_ or f"fake-immunization_recommendation-{uuid4().hex[:8]}"
    return obj


def fake_implementation_guide(
    id_: str | None = None,
) -> ImplementationGuide:
    obj = ImplementationGuide()
    obj.id = id_ or f"fake-implementation_guide-{uuid4().hex[:8]}"
    return obj


def fake_insurance_plan(
    id_: str | None = None,
) -> InsurancePlan:
    obj = InsurancePlan()
    obj.id = id_ or f"fake-insurance_plan-{uuid4().hex[:8]}"
    return obj


def fake_invoice(
    id_: str | None = None,
) -> Invoice:
    obj = Invoice()
    obj.id = id_ or f"fake-invoice-{uuid4().hex[:8]}"
    return obj


def fake_library(
    id_: str | None = None,
) -> Library:
    obj = Library()
    obj.id = id_ or f"fake-library-{uuid4().hex[:8]}"
    return obj


def fake_linkage(
    id_: str | None = None,
) -> Linkage:
    obj = Linkage()
    obj.id = id_ or f"fake-linkage-{uuid4().hex[:8]}"
    return obj


def fake_list(
    id_: str | None = None,
) -> List:
    obj = List()
    obj.id = id_ or f"fake-list-{uuid4().hex[:8]}"
    return obj


def fake_location(
    id_: str | None = None,
) -> Location:
    obj = Location()
    obj.id = id_ or f"fake-location-{uuid4().hex[:8]}"
    return obj


def fake_measure(
    id_: str | None = None,
) -> Measure:
    obj = Measure()
    obj.id = id_ or f"fake-measure-{uuid4().hex[:8]}"
    return obj


def fake_measure_report(
    id_: str | None = None,
) -> MeasureReport:
    obj = MeasureReport()
    obj.id = id_ or f"fake-measure_report-{uuid4().hex[:8]}"
    return obj


def fake_media(
    id_: str | None = None,
) -> Media:
    obj = Media()
    obj.id = id_ or f"fake-media-{uuid4().hex[:8]}"
    return obj


def fake_medication(
    id_: str | None = None,
) -> Medication:
    obj = Medication()
    obj.id = id_ or f"fake-medication-{uuid4().hex[:8]}"
    return obj


def fake_medication_administration(
    id_: str | None = None,
) -> MedicationAdministration:
    obj = MedicationAdministration()
    obj.id = id_ or f"fake-medication_administration-{uuid4().hex[:8]}"
    return obj


def fake_medication_dispense(
    id_: str | None = None,
) -> MedicationDispense:
    obj = MedicationDispense()
    obj.id = id_ or f"fake-medication_dispense-{uuid4().hex[:8]}"
    return obj


def fake_medication_knowledge(
    id_: str | None = None,
) -> MedicationKnowledge:
    obj = MedicationKnowledge()
    obj.id = id_ or f"fake-medication_knowledge-{uuid4().hex[:8]}"
    return obj


def fake_medication_request(
    id_: str | None = None,
) -> MedicationRequest:
    obj = MedicationRequest()
    obj.id = id_ or f"fake-medication_request-{uuid4().hex[:8]}"
    return obj


def fake_medication_statement(
    id_: str | None = None,
) -> MedicationStatement:
    obj = MedicationStatement()
    obj.id = id_ or f"fake-medication_statement-{uuid4().hex[:8]}"
    return obj


def fake_medicinal_product(
    id_: str | None = None,
) -> MedicinalProduct:
    obj = MedicinalProduct()
    obj.id = id_ or f"fake-medicinal_product-{uuid4().hex[:8]}"
    return obj


def fake_medicinal_product_authorization(
    id_: str | None = None,
) -> MedicinalProductAuthorization:
    obj = MedicinalProductAuthorization()
    obj.id = id_ or f"fake-medicinal_product_authorization-{uuid4().hex[:8]}"
    return obj


def fake_medicinal_product_contraindication(
    id_: str | None = None,
) -> MedicinalProductContraindication:
    obj = MedicinalProductContraindication()
    obj.id = id_ or f"fake-medicinal_product_contraindication-{uuid4().hex[:8]}"
    return obj


def fake_medicinal_product_indication(
    id_: str | None = None,
) -> MedicinalProductIndication:
    obj = MedicinalProductIndication()
    obj.id = id_ or f"fake-medicinal_product_indication-{uuid4().hex[:8]}"
    return obj


def fake_medicinal_product_ingredient(
    id_: str | None = None,
) -> MedicinalProductIngredient:
    obj = MedicinalProductIngredient()
    obj.id = id_ or f"fake-medicinal_product_ingredient-{uuid4().hex[:8]}"
    return obj


def fake_medicinal_product_interaction(
    id_: str | None = None,
) -> MedicinalProductInteraction:
    obj = MedicinalProductInteraction()
    obj.id = id_ or f"fake-medicinal_product_interaction-{uuid4().hex[:8]}"
    return obj


def fake_medicinal_product_manufactured(
    id_: str | None = None,
) -> MedicinalProductManufactured:
    obj = MedicinalProductManufactured()
    obj.id = id_ or f"fake-medicinal_product_manufactured-{uuid4().hex[:8]}"
    return obj


def fake_medicinal_product_packaged(
    id_: str | None = None,
) -> MedicinalProductPackaged:
    obj = MedicinalProductPackaged()
    obj.id = id_ or f"fake-medicinal_product_packaged-{uuid4().hex[:8]}"
    return obj


def fake_medicinal_product_pharmaceutical(
    id_: str | None = None,
) -> MedicinalProductPharmaceutical:
    obj = MedicinalProductPharmaceutical()
    obj.id = id_ or f"fake-medicinal_product_pharmaceutical-{uuid4().hex[:8]}"
    return obj


def fake_medicinal_product_undesirable_effect(
    id_: str | None = None,
) -> MedicinalProductUndesirableEffect:
    obj = MedicinalProductUndesirableEffect()
    obj.id = id_ or f"fake-medicinal_product_undesirable_effect-{uuid4().hex[:8]}"
    return obj


def fake_message_definition(
    id_: str | None = None,
) -> MessageDefinition:
    obj = MessageDefinition()
    obj.id = id_ or f"fake-message_definition-{uuid4().hex[:8]}"
    return obj


def fake_message_header(
    id_: str | None = None,
) -> MessageHeader:
    obj = MessageHeader()
    obj.id = id_ or f"fake-message_header-{uuid4().hex[:8]}"
    return obj


def fake_molecular_sequence(
    id_: str | None = None,
) -> MolecularSequence:
    obj = MolecularSequence()
    obj.id = id_ or f"fake-molecular_sequence-{uuid4().hex[:8]}"
    return obj


def fake_naming_system(
    id_: str | None = None,
) -> NamingSystem:
    obj = NamingSystem()
    obj.id = id_ or f"fake-naming_system-{uuid4().hex[:8]}"
    return obj


def fake_nutrition_order(
    id_: str | None = None,
) -> NutritionOrder:
    obj = NutritionOrder()
    obj.id = id_ or f"fake-nutrition_order-{uuid4().hex[:8]}"
    return obj


def fake_observation(
    id_: str | None = None,
) -> Observation:
    obj = Observation()
    obj.id = id_ or f"fake-observation-{uuid4().hex[:8]}"
    return obj


def fake_observation_definition(
    id_: str | None = None,
) -> ObservationDefinition:
    obj = ObservationDefinition()
    obj.id = id_ or f"fake-observation_definition-{uuid4().hex[:8]}"
    return obj


def fake_operation_definition(
    id_: str | None = None,
) -> OperationDefinition:
    obj = OperationDefinition()
    obj.id = id_ or f"fake-operation_definition-{uuid4().hex[:8]}"
    return obj


def fake_operation_outcome(
    id_: str | None = None,
) -> OperationOutcome:
    obj = OperationOutcome()
    obj.id = id_ or f"fake-operation_outcome-{uuid4().hex[:8]}"
    return obj


def fake_organization(
    id_: str | None = None,
) -> Organization:
    obj = Organization()
    obj.id = id_ or f"fake-organization-{uuid4().hex[:8]}"
    return obj


def fake_organization_affiliation(
    id_: str | None = None,
) -> OrganizationAffiliation:
    obj = OrganizationAffiliation()
    obj.id = id_ or f"fake-organization_affiliation-{uuid4().hex[:8]}"
    return obj


def fake_parameters(
    id_: str | None = None,
) -> Parameters:
    obj = Parameters()
    obj.id = id_ or f"fake-parameters-{uuid4().hex[:8]}"
    return obj


def fake_patient(
    id_: str | None = None,
) -> Patient:
    obj = Patient()
    obj.id = id_ or f"fake-patient-{uuid4().hex[:8]}"
    return obj


def fake_payment_notice(
    id_: str | None = None,
) -> PaymentNotice:
    obj = PaymentNotice()
    obj.id = id_ or f"fake-payment_notice-{uuid4().hex[:8]}"
    return obj


def fake_payment_reconciliation(
    id_: str | None = None,
) -> PaymentReconciliation:
    obj = PaymentReconciliation()
    obj.id = id_ or f"fake-payment_reconciliation-{uuid4().hex[:8]}"
    return obj


def fake_person(
    id_: str | None = None,
) -> Person:
    obj = Person()
    obj.id = id_ or f"fake-person-{uuid4().hex[:8]}"
    return obj


def fake_plan_definition(
    id_: str | None = None,
) -> PlanDefinition:
    obj = PlanDefinition()
    obj.id = id_ or f"fake-plan_definition-{uuid4().hex[:8]}"
    return obj


def fake_practitioner(
    id_: str | None = None,
) -> Practitioner:
    obj = Practitioner()
    obj.id = id_ or f"fake-practitioner-{uuid4().hex[:8]}"
    return obj


def fake_practitioner_role(
    id_: str | None = None,
) -> PractitionerRole:
    obj = PractitionerRole()
    obj.id = id_ or f"fake-practitioner_role-{uuid4().hex[:8]}"
    return obj


def fake_procedure(
    id_: str | None = None,
) -> Procedure:
    obj = Procedure()
    obj.id = id_ or f"fake-procedure-{uuid4().hex[:8]}"
    return obj


def fake_provenance(
    id_: str | None = None,
) -> Provenance:
    obj = Provenance()
    obj.id = id_ or f"fake-provenance-{uuid4().hex[:8]}"
    return obj


def fake_questionnaire(
    id_: str | None = None,
) -> Questionnaire:
    obj = Questionnaire()
    obj.id = id_ or f"fake-questionnaire-{uuid4().hex[:8]}"
    return obj


def fake_questionnaire_response(
    id_: str | None = None,
) -> QuestionnaireResponse:
    obj = QuestionnaireResponse()
    obj.id = id_ or f"fake-questionnaire_response-{uuid4().hex[:8]}"
    return obj


def fake_related_person(
    id_: str | None = None,
) -> RelatedPerson:
    obj = RelatedPerson()
    obj.id = id_ or f"fake-related_person-{uuid4().hex[:8]}"
    return obj


def fake_request_group(
    id_: str | None = None,
) -> RequestGroup:
    obj = RequestGroup()
    obj.id = id_ or f"fake-request_group-{uuid4().hex[:8]}"
    return obj


def fake_research_definition(
    id_: str | None = None,
) -> ResearchDefinition:
    obj = ResearchDefinition()
    obj.id = id_ or f"fake-research_definition-{uuid4().hex[:8]}"
    return obj


def fake_research_element_definition(
    id_: str | None = None,
) -> ResearchElementDefinition:
    obj = ResearchElementDefinition()
    obj.id = id_ or f"fake-research_element_definition-{uuid4().hex[:8]}"
    return obj


def fake_research_study(
    id_: str | None = None,
) -> ResearchStudy:
    obj = ResearchStudy()
    obj.id = id_ or f"fake-research_study-{uuid4().hex[:8]}"
    return obj


def fake_research_subject(
    id_: str | None = None,
) -> ResearchSubject:
    obj = ResearchSubject()
    obj.id = id_ or f"fake-research_subject-{uuid4().hex[:8]}"
    return obj


def fake_risk_assessment(
    id_: str | None = None,
) -> RiskAssessment:
    obj = RiskAssessment()
    obj.id = id_ or f"fake-risk_assessment-{uuid4().hex[:8]}"
    return obj


def fake_risk_evidence_synthesis(
    id_: str | None = None,
) -> RiskEvidenceSynthesis:
    obj = RiskEvidenceSynthesis()
    obj.id = id_ or f"fake-risk_evidence_synthesis-{uuid4().hex[:8]}"
    return obj


def fake_schedule(
    id_: str | None = None,
) -> Schedule:
    obj = Schedule()
    obj.id = id_ or f"fake-schedule-{uuid4().hex[:8]}"
    return obj


def fake_search_parameter(
    id_: str | None = None,
) -> SearchParameter:
    obj = SearchParameter()
    obj.id = id_ or f"fake-search_parameter-{uuid4().hex[:8]}"
    return obj


def fake_service_request(
    id_: str | None = None,
) -> ServiceRequest:
    obj = ServiceRequest()
    obj.id = id_ or f"fake-service_request-{uuid4().hex[:8]}"
    return obj


def fake_slot(
    id_: str | None = None,
) -> Slot:
    obj = Slot()
    obj.id = id_ or f"fake-slot-{uuid4().hex[:8]}"
    return obj


def fake_specimen(
    id_: str | None = None,
) -> Specimen:
    obj = Specimen()
    obj.id = id_ or f"fake-specimen-{uuid4().hex[:8]}"
    return obj


def fake_specimen_definition(
    id_: str | None = None,
) -> SpecimenDefinition:
    obj = SpecimenDefinition()
    obj.id = id_ or f"fake-specimen_definition-{uuid4().hex[:8]}"
    return obj


def fake_structure_definition(
    id_: str | None = None,
) -> StructureDefinition:
    obj = StructureDefinition()
    obj.id = id_ or f"fake-structure_definition-{uuid4().hex[:8]}"
    return obj


def fake_structure_map(
    id_: str | None = None,
) -> StructureMap:
    obj = StructureMap()
    obj.id = id_ or f"fake-structure_map-{uuid4().hex[:8]}"
    return obj


def fake_subscription(
    id_: str | None = None,
) -> Subscription:
    obj = Subscription()
    obj.id = id_ or f"fake-subscription-{uuid4().hex[:8]}"
    return obj


def fake_substance(
    id_: str | None = None,
) -> Substance:
    obj = Substance()
    obj.id = id_ or f"fake-substance-{uuid4().hex[:8]}"
    return obj


def fake_substance_nucleic_acid(
    id_: str | None = None,
) -> SubstanceNucleicAcid:
    obj = SubstanceNucleicAcid()
    obj.id = id_ or f"fake-substance_nucleic_acid-{uuid4().hex[:8]}"
    return obj


def fake_substance_polymer(
    id_: str | None = None,
) -> SubstancePolymer:
    obj = SubstancePolymer()
    obj.id = id_ or f"fake-substance_polymer-{uuid4().hex[:8]}"
    return obj


def fake_substance_protein(
    id_: str | None = None,
) -> SubstanceProtein:
    obj = SubstanceProtein()
    obj.id = id_ or f"fake-substance_protein-{uuid4().hex[:8]}"
    return obj


def fake_substance_reference_information(
    id_: str | None = None,
) -> SubstanceReferenceInformation:
    obj = SubstanceReferenceInformation()
    obj.id = id_ or f"fake-substance_reference_information-{uuid4().hex[:8]}"
    return obj


def fake_substance_source_material(
    id_: str | None = None,
) -> SubstanceSourceMaterial:
    obj = SubstanceSourceMaterial()
    obj.id = id_ or f"fake-substance_source_material-{uuid4().hex[:8]}"
    return obj


def fake_substance_specification(
    id_: str | None = None,
) -> SubstanceSpecification:
    obj = SubstanceSpecification()
    obj.id = id_ or f"fake-substance_specification-{uuid4().hex[:8]}"
    return obj


def fake_supply_delivery(
    id_: str | None = None,
) -> SupplyDelivery:
    obj = SupplyDelivery()
    obj.id = id_ or f"fake-supply_delivery-{uuid4().hex[:8]}"
    return obj


def fake_supply_request(
    id_: str | None = None,
) -> SupplyRequest:
    obj = SupplyRequest()
    obj.id = id_ or f"fake-supply_request-{uuid4().hex[:8]}"
    return obj


def fake_task(
    id_: str | None = None,
) -> Task:
    obj = Task()
    obj.id = id_ or f"fake-task-{uuid4().hex[:8]}"
    return obj


def fake_terminology_capabilities(
    id_: str | None = None,
) -> TerminologyCapabilities:
    obj = TerminologyCapabilities()
    obj.id = id_ or f"fake-terminology_capabilities-{uuid4().hex[:8]}"
    return obj


def fake_test_report(
    id_: str | None = None,
) -> TestReport:
    obj = TestReport()
    obj.id = id_ or f"fake-test_report-{uuid4().hex[:8]}"
    return obj


def fake_test_script(
    id_: str | None = None,
) -> TestScript:
    obj = TestScript()
    obj.id = id_ or f"fake-test_script-{uuid4().hex[:8]}"
    return obj


def fake_value_set(
    id_: str | None = None,
) -> ValueSet:
    obj = ValueSet()
    obj.id = id_ or f"fake-value_set-{uuid4().hex[:8]}"
    return obj


def fake_verification_result(
    id_: str | None = None,
) -> VerificationResult:
    obj = VerificationResult()
    obj.id = id_ or f"fake-verification_result-{uuid4().hex[:8]}"
    return obj


def fake_vision_prescription(
    id_: str | None = None,
) -> VisionPrescription:
    obj = VisionPrescription()
    obj.id = id_ or f"fake-vision_prescription-{uuid4().hex[:8]}"
    return obj


def fake_actualgroup(
    id_: str | None = None,
) -> actualgroup:
    obj = actualgroup()
    obj.id = id_ or f"fake-actualgroup-{uuid4().hex[:8]}"
    return obj


def fake_bmi(
    id_: str | None = None,
) -> bmi:
    obj = bmi()
    obj.id = id_ or f"fake-bmi-{uuid4().hex[:8]}"
    return obj


def fake_bodyheight(
    id_: str | None = None,
) -> bodyheight:
    obj = bodyheight()
    obj.id = id_ or f"fake-bodyheight-{uuid4().hex[:8]}"
    return obj


def fake_bodytemp(
    id_: str | None = None,
) -> bodytemp:
    obj = bodytemp()
    obj.id = id_ or f"fake-bodytemp-{uuid4().hex[:8]}"
    return obj


def fake_bodyweight(
    id_: str | None = None,
) -> bodyweight:
    obj = bodyweight()
    obj.id = id_ or f"fake-bodyweight-{uuid4().hex[:8]}"
    return obj


def fake_bp(
    id_: str | None = None,
) -> bp:
    obj = bp()
    obj.id = id_ or f"fake-bp-{uuid4().hex[:8]}"
    return obj


def fake_catalog(
    id_: str | None = None,
) -> catalog:
    obj = catalog()
    obj.id = id_ or f"fake-catalog-{uuid4().hex[:8]}"
    return obj


def fake_cdshooksguidanceresponse(
    id_: str | None = None,
) -> cdshooksguidanceresponse:
    obj = cdshooksguidanceresponse()
    obj.id = id_ or f"fake-cdshooksguidanceresponse-{uuid4().hex[:8]}"
    return obj


def fake_cdshooksrequestgroup(
    id_: str | None = None,
) -> cdshooksrequestgroup:
    obj = cdshooksrequestgroup()
    obj.id = id_ or f"fake-cdshooksrequestgroup-{uuid4().hex[:8]}"
    return obj


def fake_cdshooksserviceplandefinition(
    id_: str | None = None,
) -> cdshooksserviceplandefinition:
    obj = cdshooksserviceplandefinition()
    obj.id = id_ or f"fake-cdshooksserviceplandefinition-{uuid4().hex[:8]}"
    return obj


def fake_cholesterol(
    id_: str | None = None,
) -> cholesterol:
    obj = cholesterol()
    obj.id = id_ or f"fake-cholesterol-{uuid4().hex[:8]}"
    return obj


def fake_clinicaldocument(
    id_: str | None = None,
) -> clinicaldocument:
    obj = clinicaldocument()
    obj.id = id_ or f"fake-clinicaldocument-{uuid4().hex[:8]}"
    return obj


def fake_computableplandefinition(
    id_: str | None = None,
) -> computableplandefinition:
    obj = computableplandefinition()
    obj.id = id_ or f"fake-computableplandefinition-{uuid4().hex[:8]}"
    return obj


def fake_cqllibrary(
    id_: str | None = None,
) -> cqllibrary:
    obj = cqllibrary()
    obj.id = id_ or f"fake-cqllibrary-{uuid4().hex[:8]}"
    return obj


def fake_devicemetricobservation(
    id_: str | None = None,
) -> devicemetricobservation:
    obj = devicemetricobservation()
    obj.id = id_ or f"fake-devicemetricobservation-{uuid4().hex[:8]}"
    return obj


def fake_groupdefinition(
    id_: str | None = None,
) -> groupdefinition:
    obj = groupdefinition()
    obj.id = id_ or f"fake-groupdefinition-{uuid4().hex[:8]}"
    return obj


def fake_hdlcholesterol(
    id_: str | None = None,
) -> hdlcholesterol:
    obj = hdlcholesterol()
    obj.id = id_ or f"fake-hdlcholesterol-{uuid4().hex[:8]}"
    return obj


def fake_headcircum(
    id_: str | None = None,
) -> headcircum:
    obj = headcircum()
    obj.id = id_ or f"fake-headcircum-{uuid4().hex[:8]}"
    return obj


def fake_heartrate(
    id_: str | None = None,
) -> heartrate:
    obj = heartrate()
    obj.id = id_ or f"fake-heartrate-{uuid4().hex[:8]}"
    return obj


def fake_hlaresult(
    id_: str | None = None,
) -> hlaresult:
    obj = hlaresult()
    obj.id = id_ or f"fake-hlaresult-{uuid4().hex[:8]}"
    return obj


def fake_ldlcholesterol(
    id_: str | None = None,
) -> ldlcholesterol:
    obj = ldlcholesterol()
    obj.id = id_ or f"fake-ldlcholesterol-{uuid4().hex[:8]}"
    return obj


def fake_lipidprofile(
    id_: str | None = None,
) -> lipidprofile:
    obj = lipidprofile()
    obj.id = id_ or f"fake-lipidprofile-{uuid4().hex[:8]}"
    return obj


def fake_oxygensat(
    id_: str | None = None,
) -> oxygensat:
    obj = oxygensat()
    obj.id = id_ or f"fake-oxygensat-{uuid4().hex[:8]}"
    return obj


def fake_picoelement(
    id_: str | None = None,
) -> picoelement:
    obj = picoelement()
    obj.id = id_ or f"fake-picoelement-{uuid4().hex[:8]}"
    return obj


def fake_resprate(
    id_: str | None = None,
) -> resprate:
    obj = resprate()
    obj.id = id_ or f"fake-resprate-{uuid4().hex[:8]}"
    return obj


def fake_shareableactivitydefinition(
    id_: str | None = None,
) -> shareableactivitydefinition:
    obj = shareableactivitydefinition()
    obj.id = id_ or f"fake-shareableactivitydefinition-{uuid4().hex[:8]}"
    return obj


def fake_shareablecodesystem(
    id_: str | None = None,
) -> shareablecodesystem:
    obj = shareablecodesystem()
    obj.id = id_ or f"fake-shareablecodesystem-{uuid4().hex[:8]}"
    return obj


def fake_shareablelibrary(
    id_: str | None = None,
) -> shareablelibrary:
    obj = shareablelibrary()
    obj.id = id_ or f"fake-shareablelibrary-{uuid4().hex[:8]}"
    return obj


def fake_shareablemeasure(
    id_: str | None = None,
) -> shareablemeasure:
    obj = shareablemeasure()
    obj.id = id_ or f"fake-shareablemeasure-{uuid4().hex[:8]}"
    return obj


def fake_shareableplandefinition(
    id_: str | None = None,
) -> shareableplandefinition:
    obj = shareableplandefinition()
    obj.id = id_ or f"fake-shareableplandefinition-{uuid4().hex[:8]}"
    return obj


def fake_shareablevalueset(
    id_: str | None = None,
) -> shareablevalueset:
    obj = shareablevalueset()
    obj.id = id_ or f"fake-shareablevalueset-{uuid4().hex[:8]}"
    return obj


def fake_synthesis(
    id_: str | None = None,
) -> synthesis:
    obj = synthesis()
    obj.id = id_ or f"fake-synthesis-{uuid4().hex[:8]}"
    return obj


def fake_triglyceride(
    id_: str | None = None,
) -> triglyceride:
    obj = triglyceride()
    obj.id = id_ or f"fake-triglyceride-{uuid4().hex[:8]}"
    return obj


def fake_vitalsigns(
    id_: str | None = None,
) -> vitalsigns:
    obj = vitalsigns()
    obj.id = id_ or f"fake-vitalsigns-{uuid4().hex[:8]}"
    return obj


def fake_vitalspanel(
    id_: str | None = None,
) -> vitalspanel:
    obj = vitalspanel()
    obj.id = id_ or f"fake-vitalspanel-{uuid4().hex[:8]}"
    return obj
