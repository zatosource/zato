# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

from dataclasses import dataclass

if 0:
    from zato.fhir.r4_0_1.resources import Account, ActivityDefinition, AllergyIntolerance, \
        Appointment, AppointmentResponse, AuditEvent, Basic, Binary, BiologicallyDerivedProduct, \
        BodyStructure, Bundle, CapabilityStatement, CarePlan, CareTeam, CatalogEntry, ChargeItem, \
        ChargeItemDefinition, Claim, ClaimResponse, ClinicalImpression, CodeSystem, Communication, \
        CommunicationRequest, CompartmentDefinition, Composition, ConceptMap, Condition, Consent, \
        Contract, Coverage, CoverageEligibilityRequest, CoverageEligibilityResponse, DetectedIssue, \
        Device, DeviceDefinition, DeviceMetric, DeviceRequest, DeviceUseStatement, DiagnosticReport, \
        DocumentManifest, DocumentReference, EffectEvidenceSynthesis, Encounter, Endpoint, \
        EnrollmentRequest, EnrollmentResponse, EpisodeOfCare, Evidence, \
        EvidenceVariable, ExampleScenario, ExplanationOfBenefit, FamilyMemberHistory, Flag, Goal, \
        GraphDefinition, Group, GuidanceResponse, HealthcareService, Immunization, \
        ImmunizationEvaluation, ImmunizationRecommendation, ImplementationGuide, InsurancePlan, \
        Invoice, Library, Linkage, List, Location, Measure, MeasureReport, Media, Medication, \
        MedicationAdministration, MedicationDispense, MedicationKnowledge, MedicationRequest, \
        MedicationStatement, MedicinalProduct, MedicinalProductAuthorization, \
        MedicinalProductContraindication, MedicinalProductIndication, MedicinalProductIngredient, \
        MedicinalProductInteraction, MedicinalProductManufactured, MedicinalProductPackaged, \
        MedicinalProductPharmaceutical, MedicinalProductUndesirableEffect, MessageDefinition, \
        MessageHeader, MolecularSequence, NamingSystem, NutritionOrder, Observation, \
        ObservationDefinition, OperationDefinition, OperationOutcome, Organization, \
        OrganizationAffiliation, Parameters, Patient, PaymentNotice, PaymentReconciliation, \
        Person, PlanDefinition, Practitioner, PractitionerRole, Procedure, Provenance, \
        Questionnaire, QuestionnaireResponse, RelatedPerson, RequestGroup, ResearchDefinition, \
        ResearchElementDefinition, ResearchStudy, ResearchSubject, RiskAssessment, \
        RiskEvidenceSynthesis, Schedule, SearchParameter, ServiceRequest, Slot, Specimen, \
        SpecimenDefinition, StructureDefinition, StructureMap, Subscription, Substance, \
        SubstanceNucleicAcid, SubstancePolymer, SubstanceProtein, SubstanceReferenceInformation, \
        SubstanceSourceMaterial, SubstanceSpecification, SupplyDelivery, SupplyRequest, Task, \
        TerminologyCapabilities, TestReport, TestScript, ValueSet, VerificationResult, \
        VisionPrescription

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class WellnessVisitScenario:
    patient:           'Patient'
    practitioner:      'Practitioner'
    practitioner_role: 'PractitionerRole'
    organization:      'Organization'
    location:          'Location'
    encounters:        'list[Encounter]'
    observations:      'list[Observation]'
    diagnostic_report: 'DiagnosticReport'
    specimen:          'Specimen'
    procedure:         'Procedure'
    service_request:   'ServiceRequest'
    episode_of_care:   'EpisodeOfCare'
    composition:       'Composition'
    document_ref:      'DocumentReference'
    list_resource:     'List'
    provenance:        'Provenance'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ImmunizationVisitScenario:
    patient:              'Patient'
    practitioner:         'Practitioner'
    organization:         'Organization'
    encounters:           'list[Encounter]'
    immunization:         'Immunization'
    immunization_eval:    'ImmunizationEvaluation'
    immunization_rec:     'ImmunizationRecommendation'
    medication:           'Medication'
    medication_admin:     'MedicationAdministration'
    provenance:           'Provenance'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MedicationRefillScenario:
    patient:              'Patient'
    practitioner:         'Practitioner'
    organization:         'Organization'
    encounters:           'list[Encounter]'
    medication_request:   'MedicationRequest'
    medication_dispense:  'MedicationDispense'
    medication_statement: 'MedicationStatement'
    medication_knowledge: 'MedicationKnowledge'
    substance:            'Substance'
    detected_issue:       'DetectedIssue'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class InsuranceEnrollmentScenario:
    patient:                       'Patient'
    organization:                  'Organization'
    encounters:                    'list[Encounter]'
    coverage:                      'Coverage'
    insurance_plan:                'InsurancePlan'
    enrollment_request:            'EnrollmentRequest'
    enrollment_response:           'EnrollmentResponse'
    eligibility_request:           'CoverageEligibilityRequest'
    eligibility_response:          'CoverageEligibilityResponse'
    claim:                         'Claim'
    claim_response:                'ClaimResponse'
    explanation_of_benefit:        'ExplanationOfBenefit'
    payment_notice:                'PaymentNotice'
    payment_reconciliation:        'PaymentReconciliation'
    invoice:                       'Invoice'
    charge_item:                   'ChargeItem'
    charge_item_definition:        'ChargeItemDefinition'
    account:                       'Account'
    contract:                      'Contract'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class AppointmentBookingScenario:
    patient:              'Patient'
    practitioner:         'Practitioner'
    organization:         'Organization'
    encounters:           'list[Encounter]'
    appointment:          'Appointment'
    appointment_response: 'AppointmentResponse'
    schedule:             'Schedule'
    slot:                 'Slot'
    healthcare_service:   'HealthcareService'
    endpoint:             'Endpoint'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ReferralLetterScenario:
    patient:              'Patient'
    practitioner:         'Practitioner'
    organization:         'Organization'
    encounters:           'list[Encounter]'
    communication:        'Communication'
    communication_request:'CommunicationRequest'
    document_manifest:    'DocumentManifest'
    task:                 'Task'
    flag:                 'Flag'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class FamilyContextScenario:
    patient:               'Patient'
    encounters:            'list[Encounter]'
    related_person:        'RelatedPerson'
    family_member_history: 'FamilyMemberHistory'
    person:                'Person'
    group:                 'Group'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CarePlanScenario:
    patient:             'Patient'
    practitioner:        'Practitioner'
    organization:        'Organization'
    encounters:          'list[Encounter]'
    care_plan:           'CarePlan'
    care_team:           'CareTeam'
    goal:                'Goal'
    request_group:       'RequestGroup'
    plan_definition:     'PlanDefinition'
    activity_definition: 'ActivityDefinition'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class AllergyRecordScenario:
    patient:              'Patient'
    practitioner:         'Practitioner'
    organization:         'Organization'
    encounters:           'list[Encounter]'
    allergy_intolerance:  'AllergyIntolerance'
    clinical_impression:  'ClinicalImpression'
    risk_assessment:      'RiskAssessment'
    condition:            'Condition'
    consent:              'Consent'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class LabPanelScenario:
    patient:                'Patient'
    practitioner:           'Practitioner'
    organization:           'Organization'
    encounters:             'list[Encounter]'
    observations:           'list[Observation]'
    observation_definition: 'ObservationDefinition'
    media:                  'Media'
    specimen:               'Specimen'
    specimen_definition:    'SpecimenDefinition'
    nutrition_order:        'NutritionOrder'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class VisionCheckupScenario:
    patient:            'Patient'
    practitioner:       'Practitioner'
    organization:       'Organization'
    encounters:         'list[Encounter]'
    vision_prescription:'VisionPrescription'
    device:             'Device'
    device_definition:  'DeviceDefinition'
    device_metric:      'DeviceMetric'
    device_request:     'DeviceRequest'
    device_use:         'DeviceUseStatement'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PhysicalTherapyScenario:
    patient:                  'Patient'
    practitioner:             'Practitioner'
    organization:             'Organization'
    encounters:               'list[Encounter]'
    procedure:                'Procedure'
    care_plan:                'CarePlan'
    goal:                     'Goal'
    questionnaire:            'Questionnaire'
    questionnaire_response:   'QuestionnaireResponse'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SupplyOrderScenario:
    patient:                    'Patient'
    organization:               'Organization'
    encounters:                 'list[Encounter]'
    supply_request:             'SupplyRequest'
    supply_delivery:            'SupplyDelivery'
    receiving_organization:     'Organization'
    organization_affiliation:   'OrganizationAffiliation'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ResearchStudyScenario:
    patient:                     'Patient'
    organization:                'Organization'
    encounters:                  'list[Encounter]'
    research_study:              'ResearchStudy'
    research_subject:            'ResearchSubject'
    research_definition:         'ResearchDefinition'
    research_element_definition: 'ResearchElementDefinition'
    evidence:                    'Evidence'
    evidence_variable:           'EvidenceVariable'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class AuditTrailScenario:
    patient:           'Patient'
    audit_event:       'AuditEvent'
    provenance:        'Provenance'
    linkage:           'Linkage'
    basic:             'Basic'
    binary:            'Binary'
    parameters:        'Parameters'
    operation_outcome: 'OperationOutcome'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class TerminologySetupScenario:
    code_system:                'CodeSystem'
    value_set:                  'ValueSet'
    concept_map:                'ConceptMap'
    naming_system:              'NamingSystem'
    terminology_capabilities:   'TerminologyCapabilities'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MessagingScenario:
    patient:            'Patient'
    message_definition: 'MessageDefinition'
    message_header:     'MessageHeader'
    bundle:             'Bundle'
    subscription:       'Subscription'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ConformanceScenario:
    capability_statement:  'CapabilityStatement'
    operation_definition:  'OperationDefinition'
    search_parameter:      'SearchParameter'
    compartment_definition:'CompartmentDefinition'
    structure_definition:  'StructureDefinition'
    structure_map:         'StructureMap'
    implementation_guide:  'ImplementationGuide'
    graph_definition:      'GraphDefinition'
    example_scenario:      'ExampleScenario'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class QualityMeasureScenario:
    measure:        'Measure'
    measure_report: 'MeasureReport'
    library:        'Library'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class TestExecutionScenario:
    test_report:         'TestReport'
    test_script:         'TestScript'
    verification_result: 'VerificationResult'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class VitalsProfilesScenario:
    patient:      'Patient'
    practitioner: 'Practitioner'
    encounters:   'list[Encounter]'
    observations: 'list[Observation]'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class LipidProfilesScenario:
    patient:      'Patient'
    practitioner: 'Practitioner'
    encounters:   'list[Encounter]'
    observations: 'list[Observation]'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ShareableDefinitionsScenario:
    activity_definition: 'ActivityDefinition'
    code_system:         'CodeSystem'
    library:             'Library'
    measure:             'Measure'
    plan_definition:     'PlanDefinition'
    value_set:           'ValueSet'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ClinicalDocumentScenario:
    patient:     'Patient'
    encounters:  'list[Encounter]'
    composition: 'Composition'
    catalog:     'CatalogEntry'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CdsHooksScenario:
    patient:           'Patient'
    guidance_response: 'GuidanceResponse'
    request_group:     'RequestGroup'
    plan_definition:   'PlanDefinition'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DeviceObservationScenario:
    patient:      'Patient'
    device:       'Device'
    observations: 'list[Observation]'
    group:        'Group'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class GenomicsScenario:
    patient:                          'Patient'
    molecular_sequence:               'MolecularSequence'
    biologically_derived_product:     'BiologicallyDerivedProduct'
    body_structure:                   'BodyStructure'
    substance_nucleic_acid:           'SubstanceNucleicAcid'
    substance_polymer:                'SubstancePolymer'
    substance_protein:                'SubstanceProtein'
    substance_reference_information:  'SubstanceReferenceInformation'
    substance_source_material:        'SubstanceSourceMaterial'
    substance_specification:          'SubstanceSpecification'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ProductRegistrationScenario:
    medicinal_product:                 'MedicinalProduct'
    medicinal_product_authorization:   'MedicinalProductAuthorization'
    medicinal_product_ingredient:      'MedicinalProductIngredient'
    medicinal_product_manufactured:    'MedicinalProductManufactured'
    medicinal_product_packaged:        'MedicinalProductPackaged'
    medicinal_product_pharmaceutical:  'MedicinalProductPharmaceutical'
    medicinal_product_contraindication:'MedicinalProductContraindication'
    medicinal_product_indication:      'MedicinalProductIndication'
    medicinal_product_interaction:     'MedicinalProductInteraction'
    medicinal_product_undesirable:     'MedicinalProductUndesirableEffect'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class EffectEvidenceScenario:
    effect_evidence_synthesis: 'EffectEvidenceSynthesis'
    risk_evidence_synthesis:   'RiskEvidenceSynthesis'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PaymentScenario:
    patient:                'Patient'
    organization:           'Organization'
    payment_notice:         'PaymentNotice'
    payment_reconciliation: 'PaymentReconciliation'
    invoice:                'Invoice'
    account:                'Account'

# ################################################################################################################################
# ################################################################################################################################

Scenario_Names = [
    'wellness_visit',
    'immunization_visit',
    'medication_refill',
    'insurance_enrollment',
    'appointment_booking',
    'referral_letter',
    'family_context',
    'care_plan',
    'allergy_record',
    'lab_panel',
    'vision_checkup',
    'physical_therapy',
    'supply_order',
    'research_study',
    'audit_trail',
    'terminology_setup',
    'messaging',
    'conformance',
    'quality_measure',
    'test_execution',
    'vitals_profiles',
    'lipid_profiles',
    'shareable_definitions',
    'clinical_document',
    'cds_hooks',
    'device_observation',
    'genomics',
    'product_registration',
    'effect_evidence',
    'payment',
]

Scenario_Classes = {
    'wellness_visit':          WellnessVisitScenario,
    'immunization_visit':      ImmunizationVisitScenario,
    'medication_refill':       MedicationRefillScenario,
    'insurance_enrollment':    InsuranceEnrollmentScenario,
    'appointment_booking':     AppointmentBookingScenario,
    'referral_letter':         ReferralLetterScenario,
    'family_context':          FamilyContextScenario,
    'care_plan':               CarePlanScenario,
    'allergy_record':          AllergyRecordScenario,
    'lab_panel':               LabPanelScenario,
    'vision_checkup':          VisionCheckupScenario,
    'physical_therapy':        PhysicalTherapyScenario,
    'supply_order':            SupplyOrderScenario,
    'research_study':          ResearchStudyScenario,
    'audit_trail':             AuditTrailScenario,
    'terminology_setup':       TerminologySetupScenario,
    'messaging':               MessagingScenario,
    'conformance':             ConformanceScenario,
    'quality_measure':         QualityMeasureScenario,
    'test_execution':          TestExecutionScenario,
    'vitals_profiles':         VitalsProfilesScenario,
    'lipid_profiles':          LipidProfilesScenario,
    'shareable_definitions':   ShareableDefinitionsScenario,
    'clinical_document':       ClinicalDocumentScenario,
    'cds_hooks':               CdsHooksScenario,
    'device_observation':      DeviceObservationScenario,
    'genomics':                GenomicsScenario,
    'product_registration':    ProductRegistrationScenario,
    'effect_evidence':         EffectEvidenceScenario,
    'payment':                 PaymentScenario,
}
