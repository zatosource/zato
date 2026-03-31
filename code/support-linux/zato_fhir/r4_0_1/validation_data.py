# Generated - do not edit
from __future__ import annotations

REQUIRED_FIELDS: dict[str, list[dict]] = {
    "Account": [
        {"field": "status", "min": 1, "max": "1"},
    ],
    "ActivityDefinition": [
        {"field": "status", "min": 1, "max": "1"},
    ],
    "AdverseEvent": [
        {"field": "actuality", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "AllergyIntolerance": [
        {"field": "patient", "min": 1, "max": "1"},
    ],
    "Appointment": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "participant", "min": 1, "max": "*"},
    ],
    "AppointmentResponse": [
        {"field": "appointment", "min": 1, "max": "1"},
        {"field": "participantStatus", "min": 1, "max": "1"},
    ],
    "AuditEvent": [
        {"field": "type", "min": 1, "max": "1"},
        {"field": "recorded", "min": 1, "max": "1"},
        {"field": "agent", "min": 1, "max": "*"},
        {"field": "source", "min": 1, "max": "1"},
    ],
    "Basic": [
        {"field": "code", "min": 1, "max": "1"},
    ],
    "Binary": [
        {"field": "contentType", "min": 1, "max": "1"},
    ],
    "BodyStructure": [
        {"field": "patient", "min": 1, "max": "1"},
    ],
    "CapabilityStatement": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "date", "min": 1, "max": "1"},
        {"field": "kind", "min": 1, "max": "1"},
        {"field": "fhirVersion", "min": 1, "max": "1"},
        {"field": "format", "min": 1, "max": "*"},
    ],
    "CarePlan": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "intent", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "CatalogEntry": [
        {"field": "orderable", "min": 1, "max": "1"},
        {"field": "referencedItem", "min": 1, "max": "1"},
    ],
    "ChargeItem": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "ChargeItemDefinition": [
        {"field": "url", "min": 1, "max": "1"},
        {"field": "status", "min": 1, "max": "1"},
    ],
    "Claim": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "type", "min": 1, "max": "1"},
        {"field": "use", "min": 1, "max": "1"},
        {"field": "patient", "min": 1, "max": "1"},
        {"field": "created", "min": 1, "max": "1"},
        {"field": "provider", "min": 1, "max": "1"},
        {"field": "priority", "min": 1, "max": "1"},
        {"field": "insurance", "min": 1, "max": "*"},
    ],
    "ClaimResponse": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "type", "min": 1, "max": "1"},
        {"field": "use", "min": 1, "max": "1"},
        {"field": "patient", "min": 1, "max": "1"},
        {"field": "created", "min": 1, "max": "1"},
        {"field": "insurer", "min": 1, "max": "1"},
        {"field": "outcome", "min": 1, "max": "1"},
    ],
    "ClinicalImpression": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "CodeSystem": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "content", "min": 1, "max": "1"},
    ],
    "Communication": [
        {"field": "status", "min": 1, "max": "1"},
    ],
    "CommunicationRequest": [
        {"field": "status", "min": 1, "max": "1"},
    ],
    "CompartmentDefinition": [
        {"field": "url", "min": 1, "max": "1"},
        {"field": "name", "min": 1, "max": "1"},
        {"field": "status", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "search", "min": 1, "max": "1"},
    ],
    "Composition": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "type", "min": 1, "max": "1"},
        {"field": "date", "min": 1, "max": "1"},
        {"field": "author", "min": 1, "max": "*"},
        {"field": "title", "min": 1, "max": "1"},
    ],
    "ConceptMap": [
        {"field": "status", "min": 1, "max": "1"},
    ],
    "Condition": [
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "Consent": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "scope", "min": 1, "max": "1"},
        {"field": "category", "min": 1, "max": "*"},
    ],
    "Coverage": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "beneficiary", "min": 1, "max": "1"},
        {"field": "payor", "min": 1, "max": "*"},
    ],
    "CoverageEligibilityRequest": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "purpose", "min": 1, "max": "*"},
        {"field": "patient", "min": 1, "max": "1"},
        {"field": "created", "min": 1, "max": "1"},
        {"field": "insurer", "min": 1, "max": "1"},
    ],
    "CoverageEligibilityResponse": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "purpose", "min": 1, "max": "*"},
        {"field": "patient", "min": 1, "max": "1"},
        {"field": "created", "min": 1, "max": "1"},
        {"field": "request", "min": 1, "max": "1"},
        {"field": "outcome", "min": 1, "max": "1"},
        {"field": "insurer", "min": 1, "max": "1"},
    ],
    "DetectedIssue": [
        {"field": "status", "min": 1, "max": "1"},
    ],
    "DeviceMetric": [
        {"field": "type", "min": 1, "max": "1"},
        {"field": "category", "min": 1, "max": "1"},
    ],
    "DeviceRequest": [
        {"field": "intent", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "DeviceUseStatement": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
        {"field": "device", "min": 1, "max": "1"},
    ],
    "DiagnosticReport": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
    ],
    "DocumentManifest": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "content", "min": 1, "max": "*"},
    ],
    "DocumentReference": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "content", "min": 1, "max": "*"},
    ],
    "EffectEvidenceSynthesis": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "population", "min": 1, "max": "1"},
        {"field": "exposure", "min": 1, "max": "1"},
        {"field": "exposureAlternative", "min": 1, "max": "1"},
        {"field": "outcome", "min": 1, "max": "1"},
    ],
    "Encounter": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "class", "min": 1, "max": "1"},
    ],
    "Endpoint": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "connectionType", "min": 1, "max": "1"},
        {"field": "payloadType", "min": 1, "max": "*"},
        {"field": "address", "min": 1, "max": "1"},
    ],
    "EpisodeOfCare": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "patient", "min": 1, "max": "1"},
    ],
    "EventDefinition": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "trigger", "min": 1, "max": "*"},
    ],
    "Evidence": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "exposureBackground", "min": 1, "max": "1"},
    ],
    "EvidenceVariable": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "characteristic", "min": 1, "max": "*"},
    ],
    "ExampleScenario": [
        {"field": "status", "min": 1, "max": "1"},
    ],
    "ExplanationOfBenefit": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "type", "min": 1, "max": "1"},
        {"field": "use", "min": 1, "max": "1"},
        {"field": "patient", "min": 1, "max": "1"},
        {"field": "created", "min": 1, "max": "1"},
        {"field": "insurer", "min": 1, "max": "1"},
        {"field": "provider", "min": 1, "max": "1"},
        {"field": "outcome", "min": 1, "max": "1"},
        {"field": "insurance", "min": 1, "max": "*"},
    ],
    "FamilyMemberHistory": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "patient", "min": 1, "max": "1"},
        {"field": "relationship", "min": 1, "max": "1"},
    ],
    "Flag": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "Goal": [
        {"field": "lifecycleStatus", "min": 1, "max": "1"},
        {"field": "description", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "GraphDefinition": [
        {"field": "name", "min": 1, "max": "1"},
        {"field": "status", "min": 1, "max": "1"},
        {"field": "start", "min": 1, "max": "1"},
    ],
    "Group": [
        {"field": "type", "min": 1, "max": "1"},
        {"field": "actual", "min": 1, "max": "1"},
    ],
    "GuidanceResponse": [
        {"field": "status", "min": 1, "max": "1"},
    ],
    "ImagingStudy": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "Immunization": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "vaccineCode", "min": 1, "max": "1"},
        {"field": "patient", "min": 1, "max": "1"},
    ],
    "ImmunizationEvaluation": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "patient", "min": 1, "max": "1"},
        {"field": "targetDisease", "min": 1, "max": "1"},
        {"field": "immunizationEvent", "min": 1, "max": "1"},
        {"field": "doseStatus", "min": 1, "max": "1"},
    ],
    "ImmunizationRecommendation": [
        {"field": "patient", "min": 1, "max": "1"},
        {"field": "date", "min": 1, "max": "1"},
        {"field": "recommendation", "min": 1, "max": "*"},
    ],
    "ImplementationGuide": [
        {"field": "url", "min": 1, "max": "1"},
        {"field": "name", "min": 1, "max": "1"},
        {"field": "status", "min": 1, "max": "1"},
        {"field": "packageId", "min": 1, "max": "1"},
        {"field": "fhirVersion", "min": 1, "max": "*"},
    ],
    "Invoice": [
        {"field": "status", "min": 1, "max": "1"},
    ],
    "Library": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "type", "min": 1, "max": "1"},
    ],
    "Linkage": [
        {"field": "item", "min": 1, "max": "*"},
    ],
    "List": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "mode", "min": 1, "max": "1"},
    ],
    "Measure": [
        {"field": "status", "min": 1, "max": "1"},
    ],
    "MeasureReport": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "type", "min": 1, "max": "1"},
        {"field": "measure", "min": 1, "max": "1"},
        {"field": "period", "min": 1, "max": "1"},
    ],
    "Media": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "content", "min": 1, "max": "1"},
    ],
    "MedicationAdministration": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "MedicationDispense": [
        {"field": "status", "min": 1, "max": "1"},
    ],
    "MedicationRequest": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "intent", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "MedicationStatement": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "MedicinalProduct": [
        {"field": "name", "min": 1, "max": "*"},
    ],
    "MedicinalProductIngredient": [
        {"field": "role", "min": 1, "max": "1"},
    ],
    "MedicinalProductManufactured": [
        {"field": "manufacturedDoseForm", "min": 1, "max": "1"},
        {"field": "quantity", "min": 1, "max": "1"},
    ],
    "MedicinalProductPackaged": [
        {"field": "packageItem", "min": 1, "max": "*"},
    ],
    "MedicinalProductPharmaceutical": [
        {"field": "administrableDoseForm", "min": 1, "max": "1"},
        {"field": "routeOfAdministration", "min": 1, "max": "*"},
    ],
    "MessageDefinition": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "date", "min": 1, "max": "1"},
    ],
    "MessageHeader": [
        {"field": "source", "min": 1, "max": "1"},
    ],
    "MolecularSequence": [
        {"field": "coordinateSystem", "min": 1, "max": "1"},
    ],
    "NamingSystem": [
        {"field": "name", "min": 1, "max": "1"},
        {"field": "status", "min": 1, "max": "1"},
        {"field": "kind", "min": 1, "max": "1"},
        {"field": "date", "min": 1, "max": "1"},
        {"field": "uniqueId", "min": 1, "max": "*"},
    ],
    "NutritionOrder": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "intent", "min": 1, "max": "1"},
        {"field": "patient", "min": 1, "max": "1"},
        {"field": "dateTime", "min": 1, "max": "1"},
    ],
    "Observation": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
    ],
    "ObservationDefinition": [
        {"field": "code", "min": 1, "max": "1"},
    ],
    "OperationDefinition": [
        {"field": "name", "min": 1, "max": "1"},
        {"field": "status", "min": 1, "max": "1"},
        {"field": "kind", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "system", "min": 1, "max": "1"},
        {"field": "type", "min": 1, "max": "1"},
        {"field": "instance", "min": 1, "max": "1"},
    ],
    "OperationOutcome": [
        {"field": "issue", "min": 1, "max": "*"},
    ],
    "PaymentNotice": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "created", "min": 1, "max": "1"},
        {"field": "payment", "min": 1, "max": "1"},
        {"field": "recipient", "min": 1, "max": "1"},
        {"field": "amount", "min": 1, "max": "1"},
    ],
    "PaymentReconciliation": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "created", "min": 1, "max": "1"},
        {"field": "paymentDate", "min": 1, "max": "1"},
        {"field": "paymentAmount", "min": 1, "max": "1"},
    ],
    "PlanDefinition": [
        {"field": "status", "min": 1, "max": "1"},
    ],
    "Procedure": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "Provenance": [
        {"field": "target", "min": 1, "max": "*"},
        {"field": "recorded", "min": 1, "max": "1"},
        {"field": "agent", "min": 1, "max": "*"},
    ],
    "Questionnaire": [
        {"field": "status", "min": 1, "max": "1"},
    ],
    "QuestionnaireResponse": [
        {"field": "status", "min": 1, "max": "1"},
    ],
    "RelatedPerson": [
        {"field": "patient", "min": 1, "max": "1"},
    ],
    "RequestGroup": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "intent", "min": 1, "max": "1"},
    ],
    "ResearchDefinition": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "population", "min": 1, "max": "1"},
    ],
    "ResearchElementDefinition": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "type", "min": 1, "max": "1"},
        {"field": "characteristic", "min": 1, "max": "*"},
    ],
    "ResearchStudy": [
        {"field": "status", "min": 1, "max": "1"},
    ],
    "ResearchSubject": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "study", "min": 1, "max": "1"},
        {"field": "individual", "min": 1, "max": "1"},
    ],
    "RiskAssessment": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "RiskEvidenceSynthesis": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "population", "min": 1, "max": "1"},
        {"field": "outcome", "min": 1, "max": "1"},
    ],
    "Schedule": [
        {"field": "actor", "min": 1, "max": "*"},
    ],
    "SearchParameter": [
        {"field": "url", "min": 1, "max": "1"},
        {"field": "name", "min": 1, "max": "1"},
        {"field": "status", "min": 1, "max": "1"},
        {"field": "description", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "base", "min": 1, "max": "*"},
        {"field": "type", "min": 1, "max": "1"},
    ],
    "ServiceRequest": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "intent", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "Slot": [
        {"field": "schedule", "min": 1, "max": "1"},
        {"field": "status", "min": 1, "max": "1"},
        {"field": "start", "min": 1, "max": "1"},
        {"field": "end", "min": 1, "max": "1"},
    ],
    "StructureDefinition": [
        {"field": "url", "min": 1, "max": "1"},
        {"field": "name", "min": 1, "max": "1"},
        {"field": "status", "min": 1, "max": "1"},
        {"field": "kind", "min": 1, "max": "1"},
        {"field": "abstract", "min": 1, "max": "1"},
        {"field": "type", "min": 1, "max": "1"},
    ],
    "StructureMap": [
        {"field": "url", "min": 1, "max": "1"},
        {"field": "name", "min": 1, "max": "1"},
        {"field": "status", "min": 1, "max": "1"},
        {"field": "group", "min": 1, "max": "*"},
    ],
    "Subscription": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "reason", "min": 1, "max": "1"},
        {"field": "criteria", "min": 1, "max": "1"},
        {"field": "channel", "min": 1, "max": "1"},
    ],
    "Substance": [
        {"field": "code", "min": 1, "max": "1"},
    ],
    "SupplyRequest": [
        {"field": "quantity", "min": 1, "max": "1"},
    ],
    "Task": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "intent", "min": 1, "max": "1"},
    ],
    "TerminologyCapabilities": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "date", "min": 1, "max": "1"},
        {"field": "kind", "min": 1, "max": "1"},
    ],
    "TestReport": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "testScript", "min": 1, "max": "1"},
        {"field": "result", "min": 1, "max": "1"},
    ],
    "TestScript": [
        {"field": "url", "min": 1, "max": "1"},
        {"field": "name", "min": 1, "max": "1"},
        {"field": "status", "min": 1, "max": "1"},
    ],
    "ValueSet": [
        {"field": "status", "min": 1, "max": "1"},
    ],
    "VerificationResult": [
        {"field": "status", "min": 1, "max": "1"},
    ],
    "VisionPrescription": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "created", "min": 1, "max": "1"},
        {"field": "patient", "min": 1, "max": "1"},
        {"field": "dateWritten", "min": 1, "max": "1"},
        {"field": "prescriber", "min": 1, "max": "1"},
        {"field": "lensSpecification", "min": 1, "max": "*"},
    ],
    "actualgroup": [
        {"field": "type", "min": 1, "max": "1"},
        {"field": "actual", "min": 1, "max": "1"},
    ],
    "bmi": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "category", "min": 1, "max": "*"},
        {"field": "category", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "bodyheight": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "category", "min": 1, "max": "*"},
        {"field": "category", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "bodytemp": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "category", "min": 1, "max": "*"},
        {"field": "category", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "bodyweight": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "category", "min": 1, "max": "*"},
        {"field": "category", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "bp": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "category", "min": 1, "max": "*"},
        {"field": "category", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
        {"field": "component", "min": 2, "max": "*"},
        {"field": "component", "min": 1, "max": "1"},
        {"field": "component", "min": 1, "max": "1"},
    ],
    "catalog": [
        {"field": "extension", "min": 1, "max": "1"},
        {"field": "status", "min": 1, "max": "1"},
        {"field": "type", "min": 1, "max": "1"},
        {"field": "category", "min": 1, "max": "1"},
        {"field": "date", "min": 1, "max": "1"},
        {"field": "author", "min": 1, "max": "*"},
        {"field": "title", "min": 1, "max": "1"},
    ],
    "cdshooksguidanceresponse": [
        {"field": "extension", "min": 1, "max": "1"},
        {"field": "requestIdentifier", "min": 1, "max": "1"},
        {"field": "identifier", "min": 1, "max": "1"},
        {"field": "status", "min": 1, "max": "1"},
    ],
    "cdshooksrequestgroup": [
        {"field": "identifier", "min": 1, "max": "1"},
        {"field": "instantiatesUri", "min": 1, "max": "1"},
        {"field": "status", "min": 1, "max": "1"},
        {"field": "intent", "min": 1, "max": "1"},
    ],
    "cdshooksserviceplandefinition": [
        {"field": "extension", "min": 1, "max": "1"},
        {"field": "status", "min": 1, "max": "1"},
    ],
    "cholesterol": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "referenceRange", "min": 1, "max": "1"},
    ],
    "clinicaldocument": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "type", "min": 1, "max": "1"},
        {"field": "date", "min": 1, "max": "1"},
        {"field": "author", "min": 1, "max": "*"},
        {"field": "title", "min": 1, "max": "1"},
    ],
    "computableplandefinition": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "library", "min": 1, "max": "1"},
    ],
    "cqllibrary": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "type", "min": 1, "max": "1"},
    ],
    "devicemetricobservation": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
        {"field": "device", "min": 1, "max": "1"},
    ],
    "groupdefinition": [
        {"field": "type", "min": 1, "max": "1"},
        {"field": "actual", "min": 1, "max": "1"},
    ],
    "hdlcholesterol": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "referenceRange", "min": 1, "max": "1"},
    ],
    "headcircum": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "category", "min": 1, "max": "*"},
        {"field": "category", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "heartrate": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "category", "min": 1, "max": "*"},
        {"field": "category", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "hlaresult": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
    ],
    "ldlcholesterol": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "referenceRange", "min": 1, "max": "1"},
    ],
    "lipidprofile": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "result", "min": 3, "max": "4"},
        {"field": "result", "min": 1, "max": "1"},
        {"field": "result", "min": 1, "max": "1"},
        {"field": "result", "min": 1, "max": "1"},
    ],
    "oxygensat": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "category", "min": 1, "max": "*"},
        {"field": "category", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "picoelement": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "characteristic", "min": 1, "max": "*"},
    ],
    "resprate": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "category", "min": 1, "max": "*"},
        {"field": "category", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "shareableactivitydefinition": [
        {"field": "url", "min": 1, "max": "1"},
        {"field": "version", "min": 1, "max": "1"},
        {"field": "name", "min": 1, "max": "1"},
        {"field": "status", "min": 1, "max": "1"},
        {"field": "experimental", "min": 1, "max": "1"},
        {"field": "publisher", "min": 1, "max": "1"},
        {"field": "description", "min": 1, "max": "1"},
    ],
    "shareablecodesystem": [
        {"field": "url", "min": 1, "max": "1"},
        {"field": "version", "min": 1, "max": "1"},
        {"field": "name", "min": 1, "max": "1"},
        {"field": "status", "min": 1, "max": "1"},
        {"field": "experimental", "min": 1, "max": "1"},
        {"field": "publisher", "min": 1, "max": "1"},
        {"field": "description", "min": 1, "max": "1"},
        {"field": "content", "min": 1, "max": "1"},
        {"field": "concept", "min": 1, "max": "*"},
    ],
    "shareablelibrary": [
        {"field": "url", "min": 1, "max": "1"},
        {"field": "version", "min": 1, "max": "1"},
        {"field": "name", "min": 1, "max": "1"},
        {"field": "status", "min": 1, "max": "1"},
        {"field": "experimental", "min": 1, "max": "1"},
        {"field": "type", "min": 1, "max": "1"},
        {"field": "publisher", "min": 1, "max": "1"},
        {"field": "description", "min": 1, "max": "1"},
    ],
    "shareablemeasure": [
        {"field": "url", "min": 1, "max": "1"},
        {"field": "version", "min": 1, "max": "1"},
        {"field": "name", "min": 1, "max": "1"},
        {"field": "status", "min": 1, "max": "1"},
        {"field": "experimental", "min": 1, "max": "1"},
        {"field": "publisher", "min": 1, "max": "1"},
        {"field": "description", "min": 1, "max": "1"},
    ],
    "shareableplandefinition": [
        {"field": "url", "min": 1, "max": "1"},
        {"field": "version", "min": 1, "max": "1"},
        {"field": "name", "min": 1, "max": "1"},
        {"field": "status", "min": 1, "max": "1"},
        {"field": "experimental", "min": 1, "max": "1"},
        {"field": "publisher", "min": 1, "max": "1"},
        {"field": "description", "min": 1, "max": "1"},
    ],
    "shareablevalueset": [
        {"field": "url", "min": 1, "max": "1"},
        {"field": "version", "min": 1, "max": "1"},
        {"field": "name", "min": 1, "max": "1"},
        {"field": "status", "min": 1, "max": "1"},
        {"field": "experimental", "min": 1, "max": "1"},
        {"field": "publisher", "min": 1, "max": "1"},
        {"field": "description", "min": 1, "max": "1"},
    ],
    "synthesis": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "exposureBackground", "min": 1, "max": "1"},
        {"field": "exposureVariant", "min": 1, "max": "2"},
        {"field": "outcome", "min": 1, "max": "*"},
    ],
    "triglyceride": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "referenceRange", "min": 1, "max": "1"},
    ],
    "vitalsigns": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "category", "min": 1, "max": "*"},
        {"field": "category", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
    ],
    "vitalspanel": [
        {"field": "status", "min": 1, "max": "1"},
        {"field": "category", "min": 1, "max": "*"},
        {"field": "category", "min": 1, "max": "1"},
        {"field": "code", "min": 1, "max": "1"},
        {"field": "subject", "min": 1, "max": "1"},
        {"field": "hasMember", "min": 1, "max": "*"},
    ],
}
