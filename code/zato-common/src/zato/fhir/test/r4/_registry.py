# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

# ################################################################################################################################
# ################################################################################################################################

#  Maps every R4 resource type to the scenario(s) that produce it.
#  The coverage test asserts this dict covers all 181 types in r4_resource_names.json.

Resource_To_Scenario: 'dict[str, list[str]]' = {

    #  wellness_visit
    'Patient':              ['wellness_visit', 'immunization_visit', 'medication_refill', 'insurance_enrollment',
                             'appointment_booking', 'referral_letter', 'family_context', 'care_plan',
                             'allergy_record', 'lab_panel', 'vision_checkup', 'physical_therapy',
                             'supply_order', 'research_study', 'audit_trail', 'messaging',
                             'vitals_profiles', 'lipid_profiles', 'clinical_document', 'cds_hooks',
                             'device_observation', 'genomics', 'payment'],
    'Practitioner':         ['wellness_visit', 'immunization_visit', 'medication_refill',
                             'appointment_booking', 'referral_letter', 'care_plan', 'allergy_record',
                             'lab_panel', 'vision_checkup', 'physical_therapy', 'vitals_profiles',
                             'lipid_profiles'],
    'PractitionerRole':     ['wellness_visit'],
    'Organization':         ['wellness_visit', 'immunization_visit', 'medication_refill',
                             'insurance_enrollment', 'appointment_booking', 'referral_letter',
                             'care_plan', 'allergy_record', 'lab_panel', 'vision_checkup',
                             'physical_therapy', 'supply_order', 'research_study', 'payment'],
    'Location':             ['wellness_visit'],
    'Encounter':            ['wellness_visit', 'immunization_visit', 'medication_refill',
                             'insurance_enrollment', 'appointment_booking', 'referral_letter',
                             'family_context', 'care_plan', 'allergy_record', 'lab_panel',
                             'vision_checkup', 'physical_therapy', 'supply_order', 'research_study',
                             'vitals_profiles', 'lipid_profiles', 'clinical_document'],
    'Observation':          ['wellness_visit', 'lab_panel', 'vitals_profiles', 'lipid_profiles',
                             'device_observation'],
    'DiagnosticReport':     ['wellness_visit'],
    'Specimen':             ['wellness_visit', 'lab_panel'],
    'Procedure':            ['wellness_visit', 'physical_therapy'],
    'ServiceRequest':       ['wellness_visit'],
    'EpisodeOfCare':        ['wellness_visit'],
    'Composition':          ['wellness_visit', 'clinical_document'],
    'DocumentReference':    ['wellness_visit'],
    'List':                 ['wellness_visit'],
    'Provenance':           ['wellness_visit', 'immunization_visit', 'audit_trail'],

    #  immunization_visit
    'Immunization':                   ['immunization_visit'],
    'ImmunizationEvaluation':         ['immunization_visit'],
    'ImmunizationRecommendation':     ['immunization_visit'],
    'Medication':                     ['immunization_visit', 'medication_refill'],
    'MedicationAdministration':       ['immunization_visit'],

    #  medication_refill
    'MedicationRequest':    ['medication_refill'],
    'MedicationDispense':   ['medication_refill'],
    'MedicationStatement':  ['medication_refill'],
    'MedicationKnowledge':  ['medication_refill'],
    'Substance':            ['medication_refill'],
    'DetectedIssue':        ['medication_refill'],

    #  insurance_enrollment
    'Coverage':                      ['insurance_enrollment'],
    'InsurancePlan':                 ['insurance_enrollment'],
    'EnrollmentRequest':             ['insurance_enrollment'],
    'EnrollmentResponse':            ['insurance_enrollment'],
    'CoverageEligibilityRequest':    ['insurance_enrollment'],
    'CoverageEligibilityResponse':   ['insurance_enrollment'],
    'Claim':                         ['insurance_enrollment'],
    'ClaimResponse':                 ['insurance_enrollment'],
    'ExplanationOfBenefit':          ['insurance_enrollment'],
    'PaymentNotice':                 ['insurance_enrollment', 'payment'],
    'PaymentReconciliation':         ['insurance_enrollment', 'payment'],
    'Invoice':                       ['insurance_enrollment', 'payment'],
    'ChargeItem':                    ['insurance_enrollment'],
    'ChargeItemDefinition':          ['insurance_enrollment'],
    'Account':                       ['insurance_enrollment', 'payment'],
    'Contract':                      ['insurance_enrollment'],

    #  appointment_booking
    'Appointment':          ['appointment_booking'],
    'AppointmentResponse':  ['appointment_booking'],
    'Schedule':             ['appointment_booking'],
    'Slot':                 ['appointment_booking'],
    'HealthcareService':    ['appointment_booking'],
    'Endpoint':             ['appointment_booking'],

    #  referral_letter
    'Communication':        ['referral_letter'],
    'CommunicationRequest': ['referral_letter'],
    'DocumentManifest':     ['referral_letter'],
    'Task':                 ['referral_letter'],
    'Flag':                 ['referral_letter'],

    #  family_context
    'RelatedPerson':        ['family_context'],
    'FamilyMemberHistory':  ['family_context'],
    'Person':               ['family_context'],
    'Group':                ['family_context', 'device_observation'],

    #  care_plan
    'CarePlan':             ['care_plan', 'physical_therapy'],
    'CareTeam':             ['care_plan'],
    'Goal':                 ['care_plan', 'physical_therapy'],
    'RequestGroup':         ['care_plan', 'cds_hooks'],
    'PlanDefinition':       ['care_plan', 'cds_hooks', 'shareable_definitions'],
    'ActivityDefinition':   ['care_plan', 'shareable_definitions'],

    #  allergy_record
    'AllergyIntolerance':   ['allergy_record'],
    'ClinicalImpression':   ['allergy_record'],
    'RiskAssessment':       ['allergy_record'],
    'Condition':            ['allergy_record'],
    'Consent':              ['allergy_record'],

    #  lab_panel
    'ObservationDefinition': ['lab_panel'],
    'Media':                 ['lab_panel'],
    'SpecimenDefinition':    ['lab_panel'],
    'NutritionOrder':        ['lab_panel'],

    #  vision_checkup
    'VisionPrescription':   ['vision_checkup'],
    'Device':               ['vision_checkup', 'device_observation'],
    'DeviceDefinition':     ['vision_checkup'],
    'DeviceMetric':         ['vision_checkup'],
    'DeviceRequest':        ['vision_checkup'],
    'DeviceUseStatement':   ['vision_checkup'],

    #  physical_therapy
    'Questionnaire':         ['physical_therapy'],
    'QuestionnaireResponse': ['physical_therapy'],

    #  supply_order
    'SupplyRequest':             ['supply_order'],
    'SupplyDelivery':            ['supply_order'],
    'OrganizationAffiliation':   ['supply_order'],

    #  research_study
    'ResearchStudy':              ['research_study'],
    'ResearchSubject':            ['research_study'],
    'ResearchDefinition':         ['research_study'],
    'ResearchElementDefinition':  ['research_study'],
    'Evidence':                   ['research_study'],
    'EvidenceVariable':           ['research_study'],

    #  audit_trail
    'AuditEvent':        ['audit_trail'],
    'Linkage':           ['audit_trail'],
    'Basic':             ['audit_trail'],
    'Binary':            ['audit_trail'],
    'Parameters':        ['audit_trail'],
    'OperationOutcome':  ['audit_trail'],

    #  terminology_setup
    'CodeSystem':               ['terminology_setup', 'shareable_definitions'],
    'ValueSet':                 ['terminology_setup', 'shareable_definitions'],
    'ConceptMap':               ['terminology_setup'],
    'NamingSystem':             ['terminology_setup'],
    'TerminologyCapabilities':  ['terminology_setup'],

    #  messaging
    'MessageDefinition': ['messaging'],
    'MessageHeader':     ['messaging'],
    'Bundle':            ['messaging'],
    'Subscription':      ['messaging'],

    #  conformance
    'CapabilityStatement':    ['conformance'],
    'OperationDefinition':    ['conformance'],
    'SearchParameter':        ['conformance'],
    'CompartmentDefinition':  ['conformance'],
    'StructureDefinition':    ['conformance'],
    'StructureMap':           ['conformance'],
    'ImplementationGuide':    ['conformance'],
    'GraphDefinition':        ['conformance'],
    'ExampleScenario':        ['conformance'],

    #  quality_measure
    'Measure':       ['quality_measure', 'shareable_definitions'],
    'MeasureReport': ['quality_measure'],
    'Library':       ['quality_measure', 'shareable_definitions'],

    #  test_execution
    'TestReport':          ['test_execution'],
    'TestScript':          ['test_execution'],
    'VerificationResult':  ['test_execution'],

    #  vitals_profiles
    'vitalsigns':   ['vitals_profiles'],
    'vitalspanel':  ['vitals_profiles'],
    'bp':           ['vitals_profiles'],
    'bodyheight':   ['vitals_profiles'],
    'bodyweight':   ['vitals_profiles'],
    'bodytemp':     ['vitals_profiles'],
    'bmi':          ['vitals_profiles'],
    'headcircum':   ['vitals_profiles'],
    'heartrate':    ['vitals_profiles'],
    'oxygensat':    ['vitals_profiles'],
    'resprate':     ['vitals_profiles'],

    #  lipid_profiles
    'lipidprofile':    ['lipid_profiles'],
    'cholesterol':     ['lipid_profiles'],
    'hdlcholesterol':  ['lipid_profiles'],
    'ldlcholesterol':  ['lipid_profiles'],
    'triglyceride':    ['lipid_profiles'],

    #  shareable_definitions
    'shareableactivitydefinition': ['shareable_definitions'],
    'shareablecodesystem':         ['shareable_definitions'],
    'shareablelibrary':            ['shareable_definitions'],
    'shareablemeasure':            ['shareable_definitions'],
    'shareableplandefinition':     ['shareable_definitions'],
    'shareablevalueset':           ['shareable_definitions'],

    #  clinical_document
    'clinicaldocument': ['clinical_document'],
    'catalog':          ['clinical_document'],
    'CatalogEntry':     ['clinical_document'],

    #  cds_hooks
    'cdshooksguidanceresponse':       ['cds_hooks'],
    'cdshooksrequestgroup':           ['cds_hooks'],
    'cdshooksserviceplandefinition':   ['cds_hooks'],
    'computableplandefinition':       ['cds_hooks'],
    'GuidanceResponse':               ['cds_hooks'],

    #  device_observation
    'devicemetricobservation': ['device_observation'],
    'actualgroup':             ['device_observation'],
    'groupdefinition':         ['device_observation'],

    #  genomics
    'MolecularSequence':               ['genomics'],
    'hlaresult':                       ['genomics'],
    'BiologicallyDerivedProduct':      ['genomics'],
    'BodyStructure':                   ['genomics'],
    'SubstanceNucleicAcid':            ['genomics'],
    'SubstancePolymer':                ['genomics'],
    'SubstanceProtein':                ['genomics'],
    'SubstanceReferenceInformation':   ['genomics'],
    'SubstanceSourceMaterial':         ['genomics'],
    'SubstanceSpecification':          ['genomics'],

    #  product_registration
    'MedicinalProduct':                     ['product_registration'],
    'MedicinalProductAuthorization':        ['product_registration'],
    'MedicinalProductIngredient':           ['product_registration'],
    'MedicinalProductManufactured':         ['product_registration'],
    'MedicinalProductPackaged':             ['product_registration'],
    'MedicinalProductPharmaceutical':       ['product_registration'],
    'MedicinalProductContraindication':     ['product_registration'],
    'MedicinalProductIndication':           ['product_registration'],
    'MedicinalProductInteraction':          ['product_registration'],
    'MedicinalProductUndesirableEffect':    ['product_registration'],

    #  effect_evidence
    'EffectEvidenceSynthesis': ['effect_evidence'],
    'RiskEvidenceSynthesis':   ['effect_evidence'],
    'picoelement':             ['effect_evidence'],
    'cqllibrary':              ['effect_evidence'],
    'synthesis':               ['effect_evidence'],

    #  remaining profile types not covered above
    'AdverseEvent':     ['allergy_record'],
    'EventDefinition':  ['conformance'],
    'ImagingStudy':     ['vision_checkup'],
}
