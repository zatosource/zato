# Generated - do not edit
from __future__ import annotations

from typing import Any, Optional

from zato_fhir.base import FHIRResource, FHIRList
from zato_fhir.r4_0_1.primitives import (
    Base64Binary,
    Boolean,
    Canonical,
    Code,
    Date,
    DateTime,
    Decimal,
    Id,
    Instant,
    Integer,
    Markdown,
    Oid,
    PositiveInt,
    String,
    Time,
    UnsignedInt,
    Uri,
    Url,
    Uuid,
    Xhtml,
)
from zato_fhir.r4_0_1.datatypes import *


class Account(FHIRResource):
    _resource_type = "Account"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'subject', 'coverage', 'guarantor'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'subject': 'Reference', 'servicePeriod': 'Period', 'coverage': 'BackboneElement', 'owner': 'Reference', 'guarantor': 'BackboneElement', 'partOf': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    type: Optional[CodeableConcept]
    name: Optional[String] = None
    subject: Reference | FHIRList[Reference]
    servicePeriod: Optional[Period]
    coverage: BackboneElement | FHIRList[BackboneElement]
    owner: Optional[Reference]
    description: Optional[String] = None
    guarantor: BackboneElement | FHIRList[BackboneElement]
    partOf: Optional[Reference]


class ActivityDefinition(FHIRResource):
    _resource_type = "ActivityDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'library', 'participant', 'dosage', 'bodySite', 'specimenRequirement', 'observationRequirement', 'observationResultRequirement', 'dynamicValue'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'code': 'CodeableConcept', 'location': 'Reference', 'participant': 'BackboneElement', 'quantity': 'Quantity', 'dosage': 'Dosage', 'bodySite': 'CodeableConcept', 'specimenRequirement': 'Reference', 'observationRequirement': 'Reference', 'observationResultRequirement': 'Reference', 'dynamicValue': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    topic: CodeableConcept | FHIRList[CodeableConcept]
    author: ContactDetail | FHIRList[ContactDetail]
    editor: ContactDetail | FHIRList[ContactDetail]
    reviewer: ContactDetail | FHIRList[ContactDetail]
    endorser: ContactDetail | FHIRList[ContactDetail]
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact]
    library: Canonical | FHIRList[Canonical] = None
    kind: Optional[Code] = None
    profile: Optional[Canonical] = None
    code: Optional[CodeableConcept]
    intent: Optional[Code] = None
    priority: Optional[Code] = None
    doNotPerform: Optional[Boolean] = None
    location: Optional[Reference]
    participant: BackboneElement | FHIRList[BackboneElement]
    quantity: Optional[Quantity]
    dosage: Dosage | FHIRList[Dosage]
    bodySite: CodeableConcept | FHIRList[CodeableConcept]
    specimenRequirement: Reference | FHIRList[Reference]
    observationRequirement: Reference | FHIRList[Reference]
    observationResultRequirement: Reference | FHIRList[Reference]
    transform: Optional[Canonical] = None
    dynamicValue: BackboneElement | FHIRList[BackboneElement]


class AdverseEvent(FHIRResource):
    _resource_type = "AdverseEvent"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'category', 'resultingCondition', 'contributor', 'suspectEntity', 'subjectMedicalHistory', 'referenceDocument', 'study'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'category': 'CodeableConcept', 'event': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'resultingCondition': 'Reference', 'location': 'Reference', 'seriousness': 'CodeableConcept', 'severity': 'CodeableConcept', 'outcome': 'CodeableConcept', 'recorder': 'Reference', 'contributor': 'Reference', 'suspectEntity': 'BackboneElement', 'subjectMedicalHistory': 'Reference', 'referenceDocument': 'Reference', 'study': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Identifier]
    actuality: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    event: Optional[CodeableConcept]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    date: Optional[DateTime] = None
    detected: Optional[DateTime] = None
    recordedDate: Optional[DateTime] = None
    resultingCondition: Reference | FHIRList[Reference]
    location: Optional[Reference]
    seriousness: Optional[CodeableConcept]
    severity: Optional[CodeableConcept]
    outcome: Optional[CodeableConcept]
    recorder: Optional[Reference]
    contributor: Reference | FHIRList[Reference]
    suspectEntity: BackboneElement | FHIRList[BackboneElement]
    subjectMedicalHistory: Reference | FHIRList[Reference]
    referenceDocument: Reference | FHIRList[Reference]
    study: Reference | FHIRList[Reference]


class AllergyIntolerance(FHIRResource):
    _resource_type = "AllergyIntolerance"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'note', 'reaction'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'clinicalStatus': 'CodeableConcept', 'verificationStatus': 'CodeableConcept', 'code': 'CodeableConcept', 'patient': 'Reference', 'encounter': 'Reference', 'recorder': 'Reference', 'asserter': 'Reference', 'note': 'Annotation', 'reaction': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    clinicalStatus: Optional[CodeableConcept]
    verificationStatus: Optional[CodeableConcept]
    type: Optional[Code] = None
    category: Code | FHIRList[Code] = None
    criticality: Optional[Code] = None
    code: Optional[CodeableConcept]
    patient: Optional[Reference]
    encounter: Optional[Reference]
    recordedDate: Optional[DateTime] = None
    recorder: Optional[Reference]
    asserter: Optional[Reference]
    lastOccurrence: Optional[DateTime] = None
    note: Annotation | FHIRList[Annotation]
    reaction: BackboneElement | FHIRList[BackboneElement]


class Appointment(FHIRResource):
    _resource_type = "Appointment"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'serviceCategory', 'serviceType', 'specialty', 'reasonCode', 'reasonReference', 'supportingInformation', 'slot', 'basedOn', 'participant', 'requestedPeriod'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'cancelationReason': 'CodeableConcept', 'serviceCategory': 'CodeableConcept', 'serviceType': 'CodeableConcept', 'specialty': 'CodeableConcept', 'appointmentType': 'CodeableConcept', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'supportingInformation': 'Reference', 'slot': 'Reference', 'basedOn': 'Reference', 'participant': 'BackboneElement', 'requestedPeriod': 'Period'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    cancelationReason: Optional[CodeableConcept]
    serviceCategory: CodeableConcept | FHIRList[CodeableConcept]
    serviceType: CodeableConcept | FHIRList[CodeableConcept]
    specialty: CodeableConcept | FHIRList[CodeableConcept]
    appointmentType: Optional[CodeableConcept]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    priority: Optional[UnsignedInt] = None
    description: Optional[String] = None
    supportingInformation: Reference | FHIRList[Reference]
    start: Optional[Instant] = None
    end: Optional[Instant] = None
    minutesDuration: Optional[PositiveInt] = None
    slot: Reference | FHIRList[Reference]
    created: Optional[DateTime] = None
    comment: Optional[String] = None
    patientInstruction: Optional[String] = None
    basedOn: Reference | FHIRList[Reference]
    participant: BackboneElement | FHIRList[BackboneElement]
    requestedPeriod: Period | FHIRList[Period]


class AppointmentResponse(FHIRResource):
    _resource_type = "AppointmentResponse"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'participantType'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'appointment': 'Reference', 'participantType': 'CodeableConcept', 'actor': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    appointment: Optional[Reference]
    start: Optional[Instant] = None
    end: Optional[Instant] = None
    participantType: CodeableConcept | FHIRList[CodeableConcept]
    actor: Optional[Reference]
    participantStatus: Optional[Code] = None
    comment: Optional[String] = None


class AuditEvent(FHIRResource):
    _resource_type = "AuditEvent"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'subtype', 'purposeOfEvent', 'agent', 'entity'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'type': 'Coding', 'subtype': 'Coding', 'period': 'Period', 'purposeOfEvent': 'CodeableConcept', 'agent': 'BackboneElement', 'source': 'BackboneElement', 'entity': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type: Optional[Coding]
    subtype: Coding | FHIRList[Coding]
    action: Optional[Code] = None
    period: Optional[Period]
    recorded: Optional[Instant] = None
    outcome: Optional[Code] = None
    outcomeDesc: Optional[String] = None
    purposeOfEvent: CodeableConcept | FHIRList[CodeableConcept]
    agent: BackboneElement | FHIRList[BackboneElement]
    source: Optional[BackboneElement]
    entity: BackboneElement | FHIRList[BackboneElement]


class Basic(FHIRResource):
    _resource_type = "Basic"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'code': 'CodeableConcept', 'subject': 'Reference', 'author': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    created: Optional[Date] = None
    author: Optional[Reference]


class Binary(FHIRResource):
    _resource_type = "Binary"
    _field_types = {'meta': 'Meta', 'securityContext': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    contentType: Optional[Code] = None
    securityContext: Optional[Reference]
    data: Optional[Base64Binary] = None


class BiologicallyDerivedProduct(FHIRResource):
    _resource_type = "BiologicallyDerivedProduct"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'request', 'parent', 'processing', 'storage'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'productCode': 'CodeableConcept', 'request': 'Reference', 'parent': 'Reference', 'collection': 'BackboneElement', 'processing': 'BackboneElement', 'manipulation': 'BackboneElement', 'storage': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    productCategory: Optional[Code] = None
    productCode: Optional[CodeableConcept]
    status: Optional[Code] = None
    request: Reference | FHIRList[Reference]
    quantity: Optional[Integer] = None
    parent: Reference | FHIRList[Reference]
    collection: Optional[BackboneElement]
    processing: BackboneElement | FHIRList[BackboneElement]
    manipulation: Optional[BackboneElement]
    storage: BackboneElement | FHIRList[BackboneElement]


class BodyStructure(FHIRResource):
    _resource_type = "BodyStructure"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'locationQualifier', 'image'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'morphology': 'CodeableConcept', 'location': 'CodeableConcept', 'locationQualifier': 'CodeableConcept', 'image': 'Attachment', 'patient': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    active: Optional[Boolean] = None
    morphology: Optional[CodeableConcept]
    location: Optional[CodeableConcept]
    locationQualifier: CodeableConcept | FHIRList[CodeableConcept]
    description: Optional[String] = None
    image: Attachment | FHIRList[Attachment]
    patient: Optional[Reference]


class CapabilityStatement(FHIRResource):
    _resource_type = "CapabilityStatement"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'instantiates', 'imports', 'format', 'patchFormat', 'implementationGuide', 'rest', 'messaging', 'document'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'software': 'BackboneElement', 'implementation': 'BackboneElement', 'rest': 'BackboneElement', 'messaging': 'BackboneElement', 'document': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    kind: Optional[Code] = None
    instantiates: Canonical | FHIRList[Canonical] = None
    imports: Canonical | FHIRList[Canonical] = None
    software: Optional[BackboneElement]
    implementation: Optional[BackboneElement]
    fhirVersion: Optional[Code] = None
    format: Code | FHIRList[Code] = None
    patchFormat: Code | FHIRList[Code] = None
    implementationGuide: Canonical | FHIRList[Canonical] = None
    rest: BackboneElement | FHIRList[BackboneElement]
    messaging: BackboneElement | FHIRList[BackboneElement]
    document: BackboneElement | FHIRList[BackboneElement]


class CarePlan(FHIRResource):
    _resource_type = "CarePlan"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'instantiatesCanonical', 'instantiatesUri', 'basedOn', 'replaces', 'partOf', 'category', 'contributor', 'careTeam', 'addresses', 'supportingInfo', 'goal', 'activity', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'replaces': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'period': 'Period', 'author': 'Reference', 'contributor': 'Reference', 'careTeam': 'Reference', 'addresses': 'Reference', 'supportingInfo': 'Reference', 'goal': 'Reference', 'activity': 'BackboneElement', 'note': 'Annotation'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    instantiatesCanonical: Canonical | FHIRList[Canonical] = None
    instantiatesUri: Uri | FHIRList[Uri] = None
    basedOn: Reference | FHIRList[Reference]
    replaces: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    intent: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    title: Optional[String] = None
    description: Optional[String] = None
    subject: Optional[Reference]
    encounter: Optional[Reference]
    period: Optional[Period]
    created: Optional[DateTime] = None
    author: Optional[Reference]
    contributor: Reference | FHIRList[Reference]
    careTeam: Reference | FHIRList[Reference]
    addresses: Reference | FHIRList[Reference]
    supportingInfo: Reference | FHIRList[Reference]
    goal: Reference | FHIRList[Reference]
    activity: BackboneElement | FHIRList[BackboneElement]
    note: Annotation | FHIRList[Annotation]


class CareTeam(FHIRResource):
    _resource_type = "CareTeam"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'participant', 'reasonCode', 'reasonReference', 'managingOrganization', 'telecom', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'category': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'period': 'Period', 'participant': 'BackboneElement', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'managingOrganization': 'Reference', 'telecom': 'ContactPoint', 'note': 'Annotation'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    name: Optional[String] = None
    subject: Optional[Reference]
    encounter: Optional[Reference]
    period: Optional[Period]
    participant: BackboneElement | FHIRList[BackboneElement]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    managingOrganization: Reference | FHIRList[Reference]
    telecom: ContactPoint | FHIRList[ContactPoint]
    note: Annotation | FHIRList[Annotation]


class CatalogEntry(FHIRResource):
    _resource_type = "CatalogEntry"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'additionalIdentifier', 'classification', 'additionalCharacteristic', 'additionalClassification', 'relatedEntry'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'referencedItem': 'Reference', 'additionalIdentifier': 'Identifier', 'classification': 'CodeableConcept', 'validityPeriod': 'Period', 'additionalCharacteristic': 'CodeableConcept', 'additionalClassification': 'CodeableConcept', 'relatedEntry': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    type: Optional[CodeableConcept]
    orderable: Optional[Boolean] = None
    referencedItem: Optional[Reference]
    additionalIdentifier: Identifier | FHIRList[Identifier]
    classification: CodeableConcept | FHIRList[CodeableConcept]
    status: Optional[Code] = None
    validityPeriod: Optional[Period]
    validTo: Optional[DateTime] = None
    lastUpdated: Optional[DateTime] = None
    additionalCharacteristic: CodeableConcept | FHIRList[CodeableConcept]
    additionalClassification: CodeableConcept | FHIRList[CodeableConcept]
    relatedEntry: BackboneElement | FHIRList[BackboneElement]


class ChargeItem(FHIRResource):
    _resource_type = "ChargeItem"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'definitionUri', 'definitionCanonical', 'partOf', 'performer', 'bodysite', 'reason', 'service', 'account', 'note', 'supportingInformation'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'partOf': 'Reference', 'code': 'CodeableConcept', 'subject': 'Reference', 'context': 'Reference', 'performer': 'BackboneElement', 'performingOrganization': 'Reference', 'requestingOrganization': 'Reference', 'costCenter': 'Reference', 'quantity': 'Quantity', 'bodysite': 'CodeableConcept', 'priceOverride': 'Money', 'enterer': 'Reference', 'reason': 'CodeableConcept', 'service': 'Reference', 'account': 'Reference', 'note': 'Annotation', 'supportingInformation': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    definitionUri: Uri | FHIRList[Uri] = None
    definitionCanonical: Canonical | FHIRList[Canonical] = None
    status: Optional[Code] = None
    partOf: Reference | FHIRList[Reference]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    context: Optional[Reference]
    performer: BackboneElement | FHIRList[BackboneElement]
    performingOrganization: Optional[Reference]
    requestingOrganization: Optional[Reference]
    costCenter: Optional[Reference]
    quantity: Optional[Quantity]
    bodysite: CodeableConcept | FHIRList[CodeableConcept]
    factorOverride: Optional[Decimal] = None
    priceOverride: Optional[Money]
    overrideReason: Optional[String] = None
    enterer: Optional[Reference]
    enteredDate: Optional[DateTime] = None
    reason: CodeableConcept | FHIRList[CodeableConcept]
    service: Reference | FHIRList[Reference]
    account: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]
    supportingInformation: Reference | FHIRList[Reference]


class ChargeItemDefinition(FHIRResource):
    _resource_type = "ChargeItemDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'derivedFromUri', 'partOf', 'replaces', 'contact', 'useContext', 'jurisdiction', 'instance', 'applicability', 'propertyGroup'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'code': 'CodeableConcept', 'instance': 'Reference', 'applicability': 'BackboneElement', 'propertyGroup': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    title: Optional[String] = None
    derivedFromUri: Uri | FHIRList[Uri] = None
    partOf: Canonical | FHIRList[Canonical] = None
    replaces: Canonical | FHIRList[Canonical] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    code: Optional[CodeableConcept]
    instance: Reference | FHIRList[Reference]
    applicability: BackboneElement | FHIRList[BackboneElement]
    propertyGroup: BackboneElement | FHIRList[BackboneElement]


class Claim(FHIRResource):
    _resource_type = "Claim"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'related', 'careTeam', 'supportingInfo', 'diagnosis', 'procedure', 'insurance', 'item'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'subType': 'CodeableConcept', 'patient': 'Reference', 'billablePeriod': 'Period', 'enterer': 'Reference', 'insurer': 'Reference', 'provider': 'Reference', 'priority': 'CodeableConcept', 'fundsReserve': 'CodeableConcept', 'related': 'BackboneElement', 'prescription': 'Reference', 'originalPrescription': 'Reference', 'payee': 'BackboneElement', 'referral': 'Reference', 'facility': 'Reference', 'careTeam': 'BackboneElement', 'supportingInfo': 'BackboneElement', 'diagnosis': 'BackboneElement', 'procedure': 'BackboneElement', 'insurance': 'BackboneElement', 'accident': 'BackboneElement', 'item': 'BackboneElement', 'total': 'Money'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    type: Optional[CodeableConcept]
    subType: Optional[CodeableConcept]
    use: Optional[Code] = None
    patient: Optional[Reference]
    billablePeriod: Optional[Period]
    created: Optional[DateTime] = None
    enterer: Optional[Reference]
    insurer: Optional[Reference]
    provider: Optional[Reference]
    priority: Optional[CodeableConcept]
    fundsReserve: Optional[CodeableConcept]
    related: BackboneElement | FHIRList[BackboneElement]
    prescription: Optional[Reference]
    originalPrescription: Optional[Reference]
    payee: Optional[BackboneElement]
    referral: Optional[Reference]
    facility: Optional[Reference]
    careTeam: BackboneElement | FHIRList[BackboneElement]
    supportingInfo: BackboneElement | FHIRList[BackboneElement]
    diagnosis: BackboneElement | FHIRList[BackboneElement]
    procedure: BackboneElement | FHIRList[BackboneElement]
    insurance: BackboneElement | FHIRList[BackboneElement]
    accident: Optional[BackboneElement]
    item: BackboneElement | FHIRList[BackboneElement]
    total: Optional[Money]


class ClaimResponse(FHIRResource):
    _resource_type = "ClaimResponse"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'item', 'addItem', 'adjudication', 'total', 'processNote', 'communicationRequest', 'insurance', 'error'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'subType': 'CodeableConcept', 'patient': 'Reference', 'insurer': 'Reference', 'requestor': 'Reference', 'request': 'Reference', 'preAuthPeriod': 'Period', 'payeeType': 'CodeableConcept', 'item': 'BackboneElement', 'addItem': 'BackboneElement', 'total': 'BackboneElement', 'payment': 'BackboneElement', 'fundsReserve': 'CodeableConcept', 'formCode': 'CodeableConcept', 'form': 'Attachment', 'processNote': 'BackboneElement', 'communicationRequest': 'Reference', 'insurance': 'BackboneElement', 'error': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    type: Optional[CodeableConcept]
    subType: Optional[CodeableConcept]
    use: Optional[Code] = None
    patient: Optional[Reference]
    created: Optional[DateTime] = None
    insurer: Optional[Reference]
    requestor: Optional[Reference]
    request: Optional[Reference]
    outcome: Optional[Code] = None
    disposition: Optional[String] = None
    preAuthRef: Optional[String] = None
    preAuthPeriod: Optional[Period]
    payeeType: Optional[CodeableConcept]
    item: BackboneElement | FHIRList[BackboneElement]
    addItem: BackboneElement | FHIRList[BackboneElement]
    adjudication: Any = None
    total: BackboneElement | FHIRList[BackboneElement]
    payment: Optional[BackboneElement]
    fundsReserve: Optional[CodeableConcept]
    formCode: Optional[CodeableConcept]
    form: Optional[Attachment]
    processNote: BackboneElement | FHIRList[BackboneElement]
    communicationRequest: Reference | FHIRList[Reference]
    insurance: BackboneElement | FHIRList[BackboneElement]
    error: BackboneElement | FHIRList[BackboneElement]


class ClinicalImpression(FHIRResource):
    _resource_type = "ClinicalImpression"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'problem', 'investigation', 'protocol', 'finding', 'prognosisCodeableConcept', 'prognosisReference', 'supportingInfo', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'statusReason': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'assessor': 'Reference', 'previous': 'Reference', 'problem': 'Reference', 'investigation': 'BackboneElement', 'finding': 'BackboneElement', 'prognosisCodeableConcept': 'CodeableConcept', 'prognosisReference': 'Reference', 'supportingInfo': 'Reference', 'note': 'Annotation'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    statusReason: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    description: Optional[String] = None
    subject: Optional[Reference]
    encounter: Optional[Reference]
    date: Optional[DateTime] = None
    assessor: Optional[Reference]
    previous: Optional[Reference]
    problem: Reference | FHIRList[Reference]
    investigation: BackboneElement | FHIRList[BackboneElement]
    protocol: Uri | FHIRList[Uri] = None
    summary: Optional[String] = None
    finding: BackboneElement | FHIRList[BackboneElement]
    prognosisCodeableConcept: CodeableConcept | FHIRList[CodeableConcept]
    prognosisReference: Reference | FHIRList[Reference]
    supportingInfo: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]


class CodeSystem(FHIRResource):
    _resource_type = "CodeSystem"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'filter', 'property', 'concept'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'filter': 'BackboneElement', 'property': 'BackboneElement', 'concept': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    caseSensitive: Optional[Boolean] = None
    valueSet: Optional[Canonical] = None
    hierarchyMeaning: Optional[Code] = None
    compositional: Optional[Boolean] = None
    versionNeeded: Optional[Boolean] = None
    content: Optional[Code] = None
    supplements: Optional[Canonical] = None
    count: Optional[UnsignedInt] = None
    filter: BackboneElement | FHIRList[BackboneElement]
    property: BackboneElement | FHIRList[BackboneElement]
    concept: BackboneElement | FHIRList[BackboneElement]


class Communication(FHIRResource):
    _resource_type = "Communication"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'instantiatesCanonical', 'instantiatesUri', 'basedOn', 'partOf', 'inResponseTo', 'category', 'medium', 'about', 'recipient', 'reasonCode', 'reasonReference', 'payload', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'inResponseTo': 'Reference', 'statusReason': 'CodeableConcept', 'category': 'CodeableConcept', 'medium': 'CodeableConcept', 'subject': 'Reference', 'topic': 'CodeableConcept', 'about': 'Reference', 'encounter': 'Reference', 'recipient': 'Reference', 'sender': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'payload': 'BackboneElement', 'note': 'Annotation'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    instantiatesCanonical: Canonical | FHIRList[Canonical] = None
    instantiatesUri: Uri | FHIRList[Uri] = None
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    inResponseTo: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    statusReason: Optional[CodeableConcept]
    category: CodeableConcept | FHIRList[CodeableConcept]
    priority: Optional[Code] = None
    medium: CodeableConcept | FHIRList[CodeableConcept]
    subject: Optional[Reference]
    topic: Optional[CodeableConcept]
    about: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    sent: Optional[DateTime] = None
    received: Optional[DateTime] = None
    recipient: Reference | FHIRList[Reference]
    sender: Optional[Reference]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    payload: BackboneElement | FHIRList[BackboneElement]
    note: Annotation | FHIRList[Annotation]


class CommunicationRequest(FHIRResource):
    _resource_type = "CommunicationRequest"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'replaces', 'category', 'medium', 'about', 'payload', 'recipient', 'reasonCode', 'reasonReference', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'replaces': 'Reference', 'groupIdentifier': 'Identifier', 'statusReason': 'CodeableConcept', 'category': 'CodeableConcept', 'medium': 'CodeableConcept', 'subject': 'Reference', 'about': 'Reference', 'encounter': 'Reference', 'payload': 'BackboneElement', 'requester': 'Reference', 'recipient': 'Reference', 'sender': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'note': 'Annotation'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    replaces: Reference | FHIRList[Reference]
    groupIdentifier: Optional[Identifier]
    status: Optional[Code] = None
    statusReason: Optional[CodeableConcept]
    category: CodeableConcept | FHIRList[CodeableConcept]
    priority: Optional[Code] = None
    doNotPerform: Optional[Boolean] = None
    medium: CodeableConcept | FHIRList[CodeableConcept]
    subject: Optional[Reference]
    about: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    payload: BackboneElement | FHIRList[BackboneElement]
    authoredOn: Optional[DateTime] = None
    requester: Optional[Reference]
    recipient: Reference | FHIRList[Reference]
    sender: Optional[Reference]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]


class CompartmentDefinition(FHIRResource):
    _resource_type = "CompartmentDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'resource'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'resource': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    version: Optional[String] = None
    name: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    purpose: Optional[Markdown] = None
    code: Optional[Code] = None
    search: Optional[Boolean] = None
    resource: BackboneElement | FHIRList[BackboneElement]


class Composition(FHIRResource):
    _resource_type = "Composition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'category', 'author', 'attester', 'relatesTo', 'event', 'section'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'category': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'author': 'Reference', 'attester': 'BackboneElement', 'custodian': 'Reference', 'relatesTo': 'BackboneElement', 'event': 'BackboneElement', 'section': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Identifier]
    status: Optional[Code] = None
    type: Optional[CodeableConcept]
    category: CodeableConcept | FHIRList[CodeableConcept]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    date: Optional[DateTime] = None
    author: Reference | FHIRList[Reference]
    title: Optional[String] = None
    confidentiality: Optional[Code] = None
    attester: BackboneElement | FHIRList[BackboneElement]
    custodian: Optional[Reference]
    relatesTo: BackboneElement | FHIRList[BackboneElement]
    event: BackboneElement | FHIRList[BackboneElement]
    section: BackboneElement | FHIRList[BackboneElement]


class ConceptMap(FHIRResource):
    _resource_type = "ConceptMap"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'group'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'group': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Optional[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    group: BackboneElement | FHIRList[BackboneElement]


class Condition(FHIRResource):
    _resource_type = "Condition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'bodySite', 'stage', 'evidence', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'clinicalStatus': 'CodeableConcept', 'verificationStatus': 'CodeableConcept', 'category': 'CodeableConcept', 'severity': 'CodeableConcept', 'code': 'CodeableConcept', 'bodySite': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'recorder': 'Reference', 'asserter': 'Reference', 'stage': 'BackboneElement', 'evidence': 'BackboneElement', 'note': 'Annotation'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    clinicalStatus: Optional[CodeableConcept]
    verificationStatus: Optional[CodeableConcept]
    category: CodeableConcept | FHIRList[CodeableConcept]
    severity: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    bodySite: CodeableConcept | FHIRList[CodeableConcept]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    recordedDate: Optional[DateTime] = None
    recorder: Optional[Reference]
    asserter: Optional[Reference]
    stage: BackboneElement | FHIRList[BackboneElement]
    evidence: BackboneElement | FHIRList[BackboneElement]
    note: Annotation | FHIRList[Annotation]


class Consent(FHIRResource):
    _resource_type = "Consent"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'performer', 'organization', 'policy', 'verification'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'scope': 'CodeableConcept', 'category': 'CodeableConcept', 'patient': 'Reference', 'performer': 'Reference', 'organization': 'Reference', 'policy': 'BackboneElement', 'policyRule': 'CodeableConcept', 'verification': 'BackboneElement', 'provision': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    scope: Optional[CodeableConcept]
    category: CodeableConcept | FHIRList[CodeableConcept]
    patient: Optional[Reference]
    dateTime: Optional[DateTime] = None
    performer: Reference | FHIRList[Reference]
    organization: Reference | FHIRList[Reference]
    policy: BackboneElement | FHIRList[BackboneElement]
    policyRule: Optional[CodeableConcept]
    verification: BackboneElement | FHIRList[BackboneElement]
    provision: Optional[BackboneElement]


class Contract(FHIRResource):
    _resource_type = "Contract"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'subject', 'authority', 'domain', 'site', 'alias', 'subType', 'term', 'supportingInfo', 'relevantHistory', 'signer', 'friendly', 'legal', 'rule'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'legalState': 'CodeableConcept', 'instantiatesCanonical': 'Reference', 'contentDerivative': 'CodeableConcept', 'applies': 'Period', 'expirationType': 'CodeableConcept', 'subject': 'Reference', 'authority': 'Reference', 'domain': 'Reference', 'site': 'Reference', 'author': 'Reference', 'scope': 'CodeableConcept', 'type': 'CodeableConcept', 'subType': 'CodeableConcept', 'contentDefinition': 'BackboneElement', 'term': 'BackboneElement', 'supportingInfo': 'Reference', 'relevantHistory': 'Reference', 'signer': 'BackboneElement', 'friendly': 'BackboneElement', 'legal': 'BackboneElement', 'rule': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    url: Optional[Uri] = None
    version: Optional[String] = None
    status: Optional[Code] = None
    legalState: Optional[CodeableConcept]
    instantiatesCanonical: Optional[Reference]
    instantiatesUri: Optional[Uri] = None
    contentDerivative: Optional[CodeableConcept]
    issued: Optional[DateTime] = None
    applies: Optional[Period]
    expirationType: Optional[CodeableConcept]
    subject: Reference | FHIRList[Reference]
    authority: Reference | FHIRList[Reference]
    domain: Reference | FHIRList[Reference]
    site: Reference | FHIRList[Reference]
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    alias: String | FHIRList[String] = None
    author: Optional[Reference]
    scope: Optional[CodeableConcept]
    type: Optional[CodeableConcept]
    subType: CodeableConcept | FHIRList[CodeableConcept]
    contentDefinition: Optional[BackboneElement]
    term: BackboneElement | FHIRList[BackboneElement]
    supportingInfo: Reference | FHIRList[Reference]
    relevantHistory: Reference | FHIRList[Reference]
    signer: BackboneElement | FHIRList[BackboneElement]
    friendly: BackboneElement | FHIRList[BackboneElement]
    legal: BackboneElement | FHIRList[BackboneElement]
    rule: BackboneElement | FHIRList[BackboneElement]


class Coverage(FHIRResource):
    _resource_type = "Coverage"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'payor', 'class_', 'costToBeneficiary', 'contract'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'policyHolder': 'Reference', 'subscriber': 'Reference', 'beneficiary': 'Reference', 'relationship': 'CodeableConcept', 'period': 'Period', 'payor': 'Reference', 'class_': 'BackboneElement', 'costToBeneficiary': 'BackboneElement', 'contract': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    type: Optional[CodeableConcept]
    policyHolder: Optional[Reference]
    subscriber: Optional[Reference]
    subscriberId: Optional[String] = None
    beneficiary: Optional[Reference]
    dependent: Optional[String] = None
    relationship: Optional[CodeableConcept]
    period: Optional[Period]
    payor: Reference | FHIRList[Reference]
    class_: BackboneElement | FHIRList[BackboneElement]
    order: Optional[PositiveInt] = None
    network: Optional[String] = None
    costToBeneficiary: BackboneElement | FHIRList[BackboneElement]
    subrogation: Optional[Boolean] = None
    contract: Reference | FHIRList[Reference]


class CoverageEligibilityRequest(FHIRResource):
    _resource_type = "CoverageEligibilityRequest"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'purpose', 'supportingInfo', 'insurance', 'item'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'priority': 'CodeableConcept', 'patient': 'Reference', 'enterer': 'Reference', 'provider': 'Reference', 'insurer': 'Reference', 'facility': 'Reference', 'supportingInfo': 'BackboneElement', 'insurance': 'BackboneElement', 'item': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    priority: Optional[CodeableConcept]
    purpose: Code | FHIRList[Code] = None
    patient: Optional[Reference]
    created: Optional[DateTime] = None
    enterer: Optional[Reference]
    provider: Optional[Reference]
    insurer: Optional[Reference]
    facility: Optional[Reference]
    supportingInfo: BackboneElement | FHIRList[BackboneElement]
    insurance: BackboneElement | FHIRList[BackboneElement]
    item: BackboneElement | FHIRList[BackboneElement]


class CoverageEligibilityResponse(FHIRResource):
    _resource_type = "CoverageEligibilityResponse"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'purpose', 'insurance', 'error'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'patient': 'Reference', 'requestor': 'Reference', 'request': 'Reference', 'insurer': 'Reference', 'insurance': 'BackboneElement', 'form': 'CodeableConcept', 'error': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    purpose: Code | FHIRList[Code] = None
    patient: Optional[Reference]
    created: Optional[DateTime] = None
    requestor: Optional[Reference]
    request: Optional[Reference]
    outcome: Optional[Code] = None
    disposition: Optional[String] = None
    insurer: Optional[Reference]
    insurance: BackboneElement | FHIRList[BackboneElement]
    preAuthRef: Optional[String] = None
    form: Optional[CodeableConcept]
    error: BackboneElement | FHIRList[BackboneElement]


class DetectedIssue(FHIRResource):
    _resource_type = "DetectedIssue"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'implicated', 'evidence', 'mitigation'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'code': 'CodeableConcept', 'patient': 'Reference', 'author': 'Reference', 'implicated': 'Reference', 'evidence': 'BackboneElement', 'mitigation': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    code: Optional[CodeableConcept]
    severity: Optional[Code] = None
    patient: Optional[Reference]
    author: Optional[Reference]
    implicated: Reference | FHIRList[Reference]
    evidence: BackboneElement | FHIRList[BackboneElement]
    detail: Optional[String] = None
    reference: Optional[Uri] = None
    mitigation: BackboneElement | FHIRList[BackboneElement]


class Device(FHIRResource):
    _resource_type = "Device"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'udiCarrier', 'statusReason', 'deviceName', 'specialization', 'version', 'property', 'contact', 'note', 'safety'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'definition': 'Reference', 'udiCarrier': 'BackboneElement', 'statusReason': 'CodeableConcept', 'deviceName': 'BackboneElement', 'type': 'CodeableConcept', 'specialization': 'BackboneElement', 'version': 'BackboneElement', 'property': 'BackboneElement', 'patient': 'Reference', 'owner': 'Reference', 'contact': 'ContactPoint', 'location': 'Reference', 'note': 'Annotation', 'safety': 'CodeableConcept', 'parent': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    definition: Optional[Reference]
    udiCarrier: BackboneElement | FHIRList[BackboneElement]
    status: Optional[Code] = None
    statusReason: CodeableConcept | FHIRList[CodeableConcept]
    distinctIdentifier: Optional[String] = None
    manufacturer: Optional[String] = None
    manufactureDate: Optional[DateTime] = None
    expirationDate: Optional[DateTime] = None
    lotNumber: Optional[String] = None
    serialNumber: Optional[String] = None
    deviceName: BackboneElement | FHIRList[BackboneElement]
    modelNumber: Optional[String] = None
    partNumber: Optional[String] = None
    type: Optional[CodeableConcept]
    specialization: BackboneElement | FHIRList[BackboneElement]
    version: BackboneElement | FHIRList[BackboneElement]
    property: BackboneElement | FHIRList[BackboneElement]
    patient: Optional[Reference]
    owner: Optional[Reference]
    contact: ContactPoint | FHIRList[ContactPoint]
    location: Optional[Reference]
    url: Optional[Uri] = None
    note: Annotation | FHIRList[Annotation]
    safety: CodeableConcept | FHIRList[CodeableConcept]
    parent: Optional[Reference]


class DeviceDefinition(FHIRResource):
    _resource_type = "DeviceDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'udiDeviceIdentifier', 'deviceName', 'specialization', 'version', 'safety', 'shelfLifeStorage', 'languageCode', 'capability', 'property', 'contact', 'note', 'material'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'udiDeviceIdentifier': 'BackboneElement', 'deviceName': 'BackboneElement', 'type': 'CodeableConcept', 'specialization': 'BackboneElement', 'safety': 'CodeableConcept', 'shelfLifeStorage': 'ProductShelfLife', 'physicalCharacteristics': 'ProdCharacteristic', 'languageCode': 'CodeableConcept', 'capability': 'BackboneElement', 'property': 'BackboneElement', 'owner': 'Reference', 'contact': 'ContactPoint', 'note': 'Annotation', 'quantity': 'Quantity', 'parentDevice': 'Reference', 'material': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    udiDeviceIdentifier: BackboneElement | FHIRList[BackboneElement]
    deviceName: BackboneElement | FHIRList[BackboneElement]
    modelNumber: Optional[String] = None
    type: Optional[CodeableConcept]
    specialization: BackboneElement | FHIRList[BackboneElement]
    version: String | FHIRList[String] = None
    safety: CodeableConcept | FHIRList[CodeableConcept]
    shelfLifeStorage: ProductShelfLife | FHIRList[ProductShelfLife]
    physicalCharacteristics: Optional[ProdCharacteristic]
    languageCode: CodeableConcept | FHIRList[CodeableConcept]
    capability: BackboneElement | FHIRList[BackboneElement]
    property: BackboneElement | FHIRList[BackboneElement]
    owner: Optional[Reference]
    contact: ContactPoint | FHIRList[ContactPoint]
    url: Optional[Uri] = None
    onlineInformation: Optional[Uri] = None
    note: Annotation | FHIRList[Annotation]
    quantity: Optional[Quantity]
    parentDevice: Optional[Reference]
    material: BackboneElement | FHIRList[BackboneElement]


class DeviceMetric(FHIRResource):
    _resource_type = "DeviceMetric"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'calibration'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'unit': 'CodeableConcept', 'source': 'Reference', 'parent': 'Reference', 'measurementPeriod': 'Timing', 'calibration': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    type: Optional[CodeableConcept]
    unit: Optional[CodeableConcept]
    source: Optional[Reference]
    parent: Optional[Reference]
    operationalStatus: Optional[Code] = None
    color: Optional[Code] = None
    category: Optional[Code] = None
    measurementPeriod: Optional[Timing]
    calibration: BackboneElement | FHIRList[BackboneElement]


class DeviceRequest(FHIRResource):
    _resource_type = "DeviceRequest"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'instantiatesCanonical', 'instantiatesUri', 'basedOn', 'priorRequest', 'parameter', 'reasonCode', 'reasonReference', 'insurance', 'supportingInfo', 'note', 'relevantHistory'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'priorRequest': 'Reference', 'groupIdentifier': 'Identifier', 'parameter': 'BackboneElement', 'subject': 'Reference', 'encounter': 'Reference', 'requester': 'Reference', 'performerType': 'CodeableConcept', 'performer': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'insurance': 'Reference', 'supportingInfo': 'Reference', 'note': 'Annotation', 'relevantHistory': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    instantiatesCanonical: Canonical | FHIRList[Canonical] = None
    instantiatesUri: Uri | FHIRList[Uri] = None
    basedOn: Reference | FHIRList[Reference]
    priorRequest: Reference | FHIRList[Reference]
    groupIdentifier: Optional[Identifier]
    status: Optional[Code] = None
    intent: Optional[Code] = None
    priority: Optional[Code] = None
    parameter: BackboneElement | FHIRList[BackboneElement]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    authoredOn: Optional[DateTime] = None
    requester: Optional[Reference]
    performerType: Optional[CodeableConcept]
    performer: Optional[Reference]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    insurance: Reference | FHIRList[Reference]
    supportingInfo: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]
    relevantHistory: Reference | FHIRList[Reference]


class DeviceUseStatement(FHIRResource):
    _resource_type = "DeviceUseStatement"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'derivedFrom', 'reasonCode', 'reasonReference', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'subject': 'Reference', 'derivedFrom': 'Reference', 'source': 'Reference', 'device': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'bodySite': 'CodeableConcept', 'note': 'Annotation'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    subject: Optional[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    recordedOn: Optional[DateTime] = None
    source: Optional[Reference]
    device: Optional[Reference]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    bodySite: Optional[CodeableConcept]
    note: Annotation | FHIRList[Annotation]


class DiagnosticReport(FHIRResource):
    _resource_type = "DiagnosticReport"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'category', 'performer', 'resultsInterpreter', 'specimen', 'result', 'imagingStudy', 'media', 'conclusionCode', 'presentedForm'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'resultsInterpreter': 'Reference', 'specimen': 'Reference', 'result': 'Reference', 'imagingStudy': 'Reference', 'media': 'BackboneElement', 'conclusionCode': 'CodeableConcept', 'presentedForm': 'Attachment'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    resultsInterpreter: Reference | FHIRList[Reference]
    specimen: Reference | FHIRList[Reference]
    result: Reference | FHIRList[Reference]
    imagingStudy: Reference | FHIRList[Reference]
    media: BackboneElement | FHIRList[BackboneElement]
    conclusion: Optional[String] = None
    conclusionCode: CodeableConcept | FHIRList[CodeableConcept]
    presentedForm: Attachment | FHIRList[Attachment]


class DocumentManifest(FHIRResource):
    _resource_type = "DocumentManifest"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'author', 'recipient', 'content', 'related'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'masterIdentifier': 'Identifier', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'subject': 'Reference', 'author': 'Reference', 'recipient': 'Reference', 'content': 'Reference', 'related': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    masterIdentifier: Optional[Identifier]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    type: Optional[CodeableConcept]
    subject: Optional[Reference]
    created: Optional[DateTime] = None
    author: Reference | FHIRList[Reference]
    recipient: Reference | FHIRList[Reference]
    source: Optional[Uri] = None
    description: Optional[String] = None
    content: Reference | FHIRList[Reference]
    related: BackboneElement | FHIRList[BackboneElement]


class DocumentReference(FHIRResource):
    _resource_type = "DocumentReference"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'author', 'relatesTo', 'securityLabel', 'content'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'masterIdentifier': 'Identifier', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'category': 'CodeableConcept', 'subject': 'Reference', 'author': 'Reference', 'authenticator': 'Reference', 'custodian': 'Reference', 'relatesTo': 'BackboneElement', 'securityLabel': 'CodeableConcept', 'content': 'BackboneElement', 'context': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    masterIdentifier: Optional[Identifier]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    docStatus: Optional[Code] = None
    type: Optional[CodeableConcept]
    category: CodeableConcept | FHIRList[CodeableConcept]
    subject: Optional[Reference]
    date: Optional[Instant] = None
    author: Reference | FHIRList[Reference]
    authenticator: Optional[Reference]
    custodian: Optional[Reference]
    relatesTo: BackboneElement | FHIRList[BackboneElement]
    description: Optional[String] = None
    securityLabel: CodeableConcept | FHIRList[CodeableConcept]
    content: BackboneElement | FHIRList[BackboneElement]
    context: Optional[BackboneElement]


class EffectEvidenceSynthesis(FHIRResource):
    _resource_type = "EffectEvidenceSynthesis"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'note', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'resultsByExposure', 'effectEstimate', 'certainty'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'note': 'Annotation', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'synthesisType': 'CodeableConcept', 'studyType': 'CodeableConcept', 'population': 'Reference', 'exposure': 'Reference', 'exposureAlternative': 'Reference', 'outcome': 'Reference', 'sampleSize': 'BackboneElement', 'resultsByExposure': 'BackboneElement', 'effectEstimate': 'BackboneElement', 'certainty': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    note: Annotation | FHIRList[Annotation]
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    topic: CodeableConcept | FHIRList[CodeableConcept]
    author: ContactDetail | FHIRList[ContactDetail]
    editor: ContactDetail | FHIRList[ContactDetail]
    reviewer: ContactDetail | FHIRList[ContactDetail]
    endorser: ContactDetail | FHIRList[ContactDetail]
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact]
    synthesisType: Optional[CodeableConcept]
    studyType: Optional[CodeableConcept]
    population: Optional[Reference]
    exposure: Optional[Reference]
    exposureAlternative: Optional[Reference]
    outcome: Optional[Reference]
    sampleSize: Optional[BackboneElement]
    resultsByExposure: BackboneElement | FHIRList[BackboneElement]
    effectEstimate: BackboneElement | FHIRList[BackboneElement]
    certainty: BackboneElement | FHIRList[BackboneElement]


class Encounter(FHIRResource):
    _resource_type = "Encounter"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'statusHistory', 'classHistory', 'type', 'episodeOfCare', 'basedOn', 'participant', 'appointment', 'reasonCode', 'reasonReference', 'diagnosis', 'account', 'location'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'statusHistory': 'BackboneElement', 'class_': 'Coding', 'classHistory': 'BackboneElement', 'type': 'CodeableConcept', 'serviceType': 'CodeableConcept', 'priority': 'CodeableConcept', 'subject': 'Reference', 'episodeOfCare': 'Reference', 'basedOn': 'Reference', 'participant': 'BackboneElement', 'appointment': 'Reference', 'period': 'Period', 'length': 'Duration', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'diagnosis': 'BackboneElement', 'account': 'Reference', 'hospitalization': 'BackboneElement', 'location': 'BackboneElement', 'serviceProvider': 'Reference', 'partOf': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    statusHistory: BackboneElement | FHIRList[BackboneElement]
    class_: Optional[Coding]
    classHistory: BackboneElement | FHIRList[BackboneElement]
    type: CodeableConcept | FHIRList[CodeableConcept]
    serviceType: Optional[CodeableConcept]
    priority: Optional[CodeableConcept]
    subject: Optional[Reference]
    episodeOfCare: Reference | FHIRList[Reference]
    basedOn: Reference | FHIRList[Reference]
    participant: BackboneElement | FHIRList[BackboneElement]
    appointment: Reference | FHIRList[Reference]
    period: Optional[Period]
    length: Optional[Duration]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    diagnosis: BackboneElement | FHIRList[BackboneElement]
    account: Reference | FHIRList[Reference]
    hospitalization: Optional[BackboneElement]
    location: BackboneElement | FHIRList[BackboneElement]
    serviceProvider: Optional[Reference]
    partOf: Optional[Reference]


class Endpoint(FHIRResource):
    _resource_type = "Endpoint"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'payloadType', 'payloadMimeType', 'header'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'connectionType': 'Coding', 'managingOrganization': 'Reference', 'contact': 'ContactPoint', 'period': 'Period', 'payloadType': 'CodeableConcept'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    connectionType: Optional[Coding]
    name: Optional[String] = None
    managingOrganization: Optional[Reference]
    contact: ContactPoint | FHIRList[ContactPoint]
    period: Optional[Period]
    payloadType: CodeableConcept | FHIRList[CodeableConcept]
    payloadMimeType: Code | FHIRList[Code] = None
    address: Optional[Url] = None
    header: String | FHIRList[String] = None


class EnrollmentRequest(FHIRResource):
    _resource_type = "EnrollmentRequest"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'insurer': 'Reference', 'provider': 'Reference', 'candidate': 'Reference', 'coverage': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    created: Optional[DateTime] = None
    insurer: Optional[Reference]
    provider: Optional[Reference]
    candidate: Optional[Reference]
    coverage: Optional[Reference]


class EnrollmentResponse(FHIRResource):
    _resource_type = "EnrollmentResponse"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'request': 'Reference', 'organization': 'Reference', 'requestProvider': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    request: Optional[Reference]
    outcome: Optional[Code] = None
    disposition: Optional[String] = None
    created: Optional[DateTime] = None
    organization: Optional[Reference]
    requestProvider: Optional[Reference]


class EpisodeOfCare(FHIRResource):
    _resource_type = "EpisodeOfCare"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'statusHistory', 'type', 'diagnosis', 'referralRequest', 'team', 'account'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'statusHistory': 'BackboneElement', 'type': 'CodeableConcept', 'diagnosis': 'BackboneElement', 'patient': 'Reference', 'managingOrganization': 'Reference', 'period': 'Period', 'referralRequest': 'Reference', 'careManager': 'Reference', 'team': 'Reference', 'account': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    statusHistory: BackboneElement | FHIRList[BackboneElement]
    type: CodeableConcept | FHIRList[CodeableConcept]
    diagnosis: BackboneElement | FHIRList[BackboneElement]
    patient: Optional[Reference]
    managingOrganization: Optional[Reference]
    period: Optional[Period]
    referralRequest: Reference | FHIRList[Reference]
    careManager: Optional[Reference]
    team: Reference | FHIRList[Reference]
    account: Reference | FHIRList[Reference]


class EventDefinition(FHIRResource):
    _resource_type = "EventDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'trigger'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'trigger': 'TriggerDefinition'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    topic: CodeableConcept | FHIRList[CodeableConcept]
    author: ContactDetail | FHIRList[ContactDetail]
    editor: ContactDetail | FHIRList[ContactDetail]
    reviewer: ContactDetail | FHIRList[ContactDetail]
    endorser: ContactDetail | FHIRList[ContactDetail]
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact]
    trigger: TriggerDefinition | FHIRList[TriggerDefinition]


class Evidence(FHIRResource):
    _resource_type = "Evidence"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'note', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'exposureVariant', 'outcome'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'note': 'Annotation', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'exposureBackground': 'Reference', 'exposureVariant': 'Reference', 'outcome': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    shortTitle: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    note: Annotation | FHIRList[Annotation]
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    topic: CodeableConcept | FHIRList[CodeableConcept]
    author: ContactDetail | FHIRList[ContactDetail]
    editor: ContactDetail | FHIRList[ContactDetail]
    reviewer: ContactDetail | FHIRList[ContactDetail]
    endorser: ContactDetail | FHIRList[ContactDetail]
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact]
    exposureBackground: Optional[Reference]
    exposureVariant: Reference | FHIRList[Reference]
    outcome: Reference | FHIRList[Reference]


class EvidenceVariable(FHIRResource):
    _resource_type = "EvidenceVariable"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'note', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'characteristic'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'note': 'Annotation', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'characteristic': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    shortTitle: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    note: Annotation | FHIRList[Annotation]
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    topic: CodeableConcept | FHIRList[CodeableConcept]
    author: ContactDetail | FHIRList[ContactDetail]
    editor: ContactDetail | FHIRList[ContactDetail]
    reviewer: ContactDetail | FHIRList[ContactDetail]
    endorser: ContactDetail | FHIRList[ContactDetail]
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact]
    type: Optional[Code] = None
    characteristic: BackboneElement | FHIRList[BackboneElement]


class ExampleScenario(FHIRResource):
    _resource_type = "ExampleScenario"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'actor', 'instance', 'process', 'workflow'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'actor': 'BackboneElement', 'instance': 'BackboneElement', 'process': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    copyright: Optional[Markdown] = None
    purpose: Optional[Markdown] = None
    actor: BackboneElement | FHIRList[BackboneElement]
    instance: BackboneElement | FHIRList[BackboneElement]
    process: BackboneElement | FHIRList[BackboneElement]
    workflow: Canonical | FHIRList[Canonical] = None


class ExplanationOfBenefit(FHIRResource):
    _resource_type = "ExplanationOfBenefit"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'related', 'preAuthRef', 'preAuthRefPeriod', 'careTeam', 'supportingInfo', 'diagnosis', 'procedure', 'insurance', 'item', 'addItem', 'adjudication', 'total', 'processNote', 'benefitBalance'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'subType': 'CodeableConcept', 'patient': 'Reference', 'billablePeriod': 'Period', 'enterer': 'Reference', 'insurer': 'Reference', 'provider': 'Reference', 'priority': 'CodeableConcept', 'fundsReserveRequested': 'CodeableConcept', 'fundsReserve': 'CodeableConcept', 'related': 'BackboneElement', 'prescription': 'Reference', 'originalPrescription': 'Reference', 'payee': 'BackboneElement', 'referral': 'Reference', 'facility': 'Reference', 'claim': 'Reference', 'claimResponse': 'Reference', 'preAuthRefPeriod': 'Period', 'careTeam': 'BackboneElement', 'supportingInfo': 'BackboneElement', 'diagnosis': 'BackboneElement', 'procedure': 'BackboneElement', 'insurance': 'BackboneElement', 'accident': 'BackboneElement', 'item': 'BackboneElement', 'addItem': 'BackboneElement', 'total': 'BackboneElement', 'payment': 'BackboneElement', 'formCode': 'CodeableConcept', 'form': 'Attachment', 'processNote': 'BackboneElement', 'benefitPeriod': 'Period', 'benefitBalance': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    type: Optional[CodeableConcept]
    subType: Optional[CodeableConcept]
    use: Optional[Code] = None
    patient: Optional[Reference]
    billablePeriod: Optional[Period]
    created: Optional[DateTime] = None
    enterer: Optional[Reference]
    insurer: Optional[Reference]
    provider: Optional[Reference]
    priority: Optional[CodeableConcept]
    fundsReserveRequested: Optional[CodeableConcept]
    fundsReserve: Optional[CodeableConcept]
    related: BackboneElement | FHIRList[BackboneElement]
    prescription: Optional[Reference]
    originalPrescription: Optional[Reference]
    payee: Optional[BackboneElement]
    referral: Optional[Reference]
    facility: Optional[Reference]
    claim: Optional[Reference]
    claimResponse: Optional[Reference]
    outcome: Optional[Code] = None
    disposition: Optional[String] = None
    preAuthRef: String | FHIRList[String] = None
    preAuthRefPeriod: Period | FHIRList[Period]
    careTeam: BackboneElement | FHIRList[BackboneElement]
    supportingInfo: BackboneElement | FHIRList[BackboneElement]
    diagnosis: BackboneElement | FHIRList[BackboneElement]
    procedure: BackboneElement | FHIRList[BackboneElement]
    precedence: Optional[PositiveInt] = None
    insurance: BackboneElement | FHIRList[BackboneElement]
    accident: Optional[BackboneElement]
    item: BackboneElement | FHIRList[BackboneElement]
    addItem: BackboneElement | FHIRList[BackboneElement]
    adjudication: Any = None
    total: BackboneElement | FHIRList[BackboneElement]
    payment: Optional[BackboneElement]
    formCode: Optional[CodeableConcept]
    form: Optional[Attachment]
    processNote: BackboneElement | FHIRList[BackboneElement]
    benefitPeriod: Optional[Period]
    benefitBalance: BackboneElement | FHIRList[BackboneElement]


class FamilyMemberHistory(FHIRResource):
    _resource_type = "FamilyMemberHistory"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'instantiatesCanonical', 'instantiatesUri', 'reasonCode', 'reasonReference', 'note', 'condition'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'dataAbsentReason': 'CodeableConcept', 'patient': 'Reference', 'relationship': 'CodeableConcept', 'sex': 'CodeableConcept', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'note': 'Annotation', 'condition': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    instantiatesCanonical: Canonical | FHIRList[Canonical] = None
    instantiatesUri: Uri | FHIRList[Uri] = None
    status: Optional[Code] = None
    dataAbsentReason: Optional[CodeableConcept]
    patient: Optional[Reference]
    date: Optional[DateTime] = None
    name: Optional[String] = None
    relationship: Optional[CodeableConcept]
    sex: Optional[CodeableConcept]
    estimatedAge: Optional[Boolean] = None
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]
    condition: BackboneElement | FHIRList[BackboneElement]


class Flag(FHIRResource):
    _resource_type = "Flag"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'period': 'Period', 'encounter': 'Reference', 'author': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    period: Optional[Period]
    encounter: Optional[Reference]
    author: Optional[Reference]


class Goal(FHIRResource):
    _resource_type = "Goal"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'target', 'addresses', 'note', 'outcomeCode', 'outcomeReference'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'achievementStatus': 'CodeableConcept', 'category': 'CodeableConcept', 'priority': 'CodeableConcept', 'description': 'CodeableConcept', 'subject': 'Reference', 'target': 'BackboneElement', 'expressedBy': 'Reference', 'addresses': 'Reference', 'note': 'Annotation', 'outcomeCode': 'CodeableConcept', 'outcomeReference': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    lifecycleStatus: Optional[Code] = None
    achievementStatus: Optional[CodeableConcept]
    category: CodeableConcept | FHIRList[CodeableConcept]
    priority: Optional[CodeableConcept]
    description: Optional[CodeableConcept]
    subject: Optional[Reference]
    target: BackboneElement | FHIRList[BackboneElement]
    statusDate: Optional[Date] = None
    statusReason: Optional[String] = None
    expressedBy: Optional[Reference]
    addresses: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]
    outcomeCode: CodeableConcept | FHIRList[CodeableConcept]
    outcomeReference: Reference | FHIRList[Reference]


class GraphDefinition(FHIRResource):
    _resource_type = "GraphDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'link'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'link': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    version: Optional[String] = None
    name: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    start: Optional[Code] = None
    profile: Optional[Canonical] = None
    link: BackboneElement | FHIRList[BackboneElement]


class Group(FHIRResource):
    _resource_type = "Group"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'characteristic', 'member'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'code': 'CodeableConcept', 'managingEntity': 'Reference', 'characteristic': 'BackboneElement', 'member': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    active: Optional[Boolean] = None
    type: Optional[Code] = None
    actual: Optional[Boolean] = None
    code: Optional[CodeableConcept]
    name: Optional[String] = None
    quantity: Optional[UnsignedInt] = None
    managingEntity: Optional[Reference]
    characteristic: BackboneElement | FHIRList[BackboneElement]
    member: BackboneElement | FHIRList[BackboneElement]


class GuidanceResponse(FHIRResource):
    _resource_type = "GuidanceResponse"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'reasonCode', 'reasonReference', 'note', 'evaluationMessage', 'dataRequirement'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'requestIdentifier': 'Identifier', 'identifier': 'Identifier', 'subject': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'note': 'Annotation', 'evaluationMessage': 'Reference', 'outputParameters': 'Reference', 'result': 'Reference', 'dataRequirement': 'DataRequirement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    requestIdentifier: Optional[Identifier]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    subject: Optional[Reference]
    encounter: Optional[Reference]
    occurrenceDateTime: Optional[DateTime] = None
    performer: Optional[Reference]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]
    evaluationMessage: Reference | FHIRList[Reference]
    outputParameters: Optional[Reference]
    result: Optional[Reference]
    dataRequirement: DataRequirement | FHIRList[DataRequirement]


class HealthcareService(FHIRResource):
    _resource_type = "HealthcareService"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'type', 'specialty', 'location', 'telecom', 'coverageArea', 'serviceProvisionCode', 'eligibility', 'program', 'characteristic', 'communication', 'referralMethod', 'availableTime', 'notAvailable', 'endpoint'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'providedBy': 'Reference', 'category': 'CodeableConcept', 'type': 'CodeableConcept', 'specialty': 'CodeableConcept', 'location': 'Reference', 'photo': 'Attachment', 'telecom': 'ContactPoint', 'coverageArea': 'Reference', 'serviceProvisionCode': 'CodeableConcept', 'eligibility': 'BackboneElement', 'program': 'CodeableConcept', 'characteristic': 'CodeableConcept', 'communication': 'CodeableConcept', 'referralMethod': 'CodeableConcept', 'availableTime': 'BackboneElement', 'notAvailable': 'BackboneElement', 'endpoint': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    active: Optional[Boolean] = None
    providedBy: Optional[Reference]
    category: CodeableConcept | FHIRList[CodeableConcept]
    type: CodeableConcept | FHIRList[CodeableConcept]
    specialty: CodeableConcept | FHIRList[CodeableConcept]
    location: Reference | FHIRList[Reference]
    name: Optional[String] = None
    comment: Optional[String] = None
    extraDetails: Optional[Markdown] = None
    photo: Optional[Attachment]
    telecom: ContactPoint | FHIRList[ContactPoint]
    coverageArea: Reference | FHIRList[Reference]
    serviceProvisionCode: CodeableConcept | FHIRList[CodeableConcept]
    eligibility: BackboneElement | FHIRList[BackboneElement]
    program: CodeableConcept | FHIRList[CodeableConcept]
    characteristic: CodeableConcept | FHIRList[CodeableConcept]
    communication: CodeableConcept | FHIRList[CodeableConcept]
    referralMethod: CodeableConcept | FHIRList[CodeableConcept]
    appointmentRequired: Optional[Boolean] = None
    availableTime: BackboneElement | FHIRList[BackboneElement]
    notAvailable: BackboneElement | FHIRList[BackboneElement]
    availabilityExceptions: Optional[String] = None
    endpoint: Reference | FHIRList[Reference]


class ImagingStudy(FHIRResource):
    _resource_type = "ImagingStudy"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'modality', 'basedOn', 'interpreter', 'endpoint', 'procedureCode', 'reasonCode', 'reasonReference', 'note', 'series'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'modality': 'Coding', 'subject': 'Reference', 'encounter': 'Reference', 'basedOn': 'Reference', 'referrer': 'Reference', 'interpreter': 'Reference', 'endpoint': 'Reference', 'procedureReference': 'Reference', 'procedureCode': 'CodeableConcept', 'location': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'note': 'Annotation', 'series': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    modality: Coding | FHIRList[Coding]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    started: Optional[DateTime] = None
    basedOn: Reference | FHIRList[Reference]
    referrer: Optional[Reference]
    interpreter: Reference | FHIRList[Reference]
    endpoint: Reference | FHIRList[Reference]
    numberOfSeries: Optional[UnsignedInt] = None
    numberOfInstances: Optional[UnsignedInt] = None
    procedureReference: Optional[Reference]
    procedureCode: CodeableConcept | FHIRList[CodeableConcept]
    location: Optional[Reference]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]
    description: Optional[String] = None
    series: BackboneElement | FHIRList[BackboneElement]


class Immunization(FHIRResource):
    _resource_type = "Immunization"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'performer', 'note', 'reasonCode', 'reasonReference', 'subpotentReason', 'education', 'programEligibility', 'reaction', 'protocolApplied'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'statusReason': 'CodeableConcept', 'vaccineCode': 'CodeableConcept', 'patient': 'Reference', 'encounter': 'Reference', 'reportOrigin': 'CodeableConcept', 'location': 'Reference', 'manufacturer': 'Reference', 'site': 'CodeableConcept', 'route': 'CodeableConcept', 'doseQuantity': 'Quantity', 'performer': 'BackboneElement', 'note': 'Annotation', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'subpotentReason': 'CodeableConcept', 'education': 'BackboneElement', 'programEligibility': 'CodeableConcept', 'fundingSource': 'CodeableConcept', 'reaction': 'BackboneElement', 'protocolApplied': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    statusReason: Optional[CodeableConcept]
    vaccineCode: Optional[CodeableConcept]
    patient: Optional[Reference]
    encounter: Optional[Reference]
    recorded: Optional[DateTime] = None
    primarySource: Optional[Boolean] = None
    reportOrigin: Optional[CodeableConcept]
    location: Optional[Reference]
    manufacturer: Optional[Reference]
    lotNumber: Optional[String] = None
    expirationDate: Optional[Date] = None
    site: Optional[CodeableConcept]
    route: Optional[CodeableConcept]
    doseQuantity: Optional[Quantity]
    performer: BackboneElement | FHIRList[BackboneElement]
    note: Annotation | FHIRList[Annotation]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    isSubpotent: Optional[Boolean] = None
    subpotentReason: CodeableConcept | FHIRList[CodeableConcept]
    education: BackboneElement | FHIRList[BackboneElement]
    programEligibility: CodeableConcept | FHIRList[CodeableConcept]
    fundingSource: Optional[CodeableConcept]
    reaction: BackboneElement | FHIRList[BackboneElement]
    protocolApplied: BackboneElement | FHIRList[BackboneElement]


class ImmunizationEvaluation(FHIRResource):
    _resource_type = "ImmunizationEvaluation"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'doseStatusReason'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'patient': 'Reference', 'authority': 'Reference', 'targetDisease': 'CodeableConcept', 'immunizationEvent': 'Reference', 'doseStatus': 'CodeableConcept', 'doseStatusReason': 'CodeableConcept'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    patient: Optional[Reference]
    date: Optional[DateTime] = None
    authority: Optional[Reference]
    targetDisease: Optional[CodeableConcept]
    immunizationEvent: Optional[Reference]
    doseStatus: Optional[CodeableConcept]
    doseStatusReason: CodeableConcept | FHIRList[CodeableConcept]
    description: Optional[String] = None
    series: Optional[String] = None


class ImmunizationRecommendation(FHIRResource):
    _resource_type = "ImmunizationRecommendation"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'recommendation'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'patient': 'Reference', 'authority': 'Reference', 'recommendation': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    patient: Optional[Reference]
    date: Optional[DateTime] = None
    authority: Optional[Reference]
    recommendation: BackboneElement | FHIRList[BackboneElement]


class ImplementationGuide(FHIRResource):
    _resource_type = "ImplementationGuide"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'fhirVersion', 'dependsOn', 'global_'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'dependsOn': 'BackboneElement', 'global_': 'BackboneElement', 'definition': 'BackboneElement', 'manifest': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    copyright: Optional[Markdown] = None
    packageId: Optional[Id] = None
    license: Optional[Code] = None
    fhirVersion: Code | FHIRList[Code] = None
    dependsOn: BackboneElement | FHIRList[BackboneElement]
    global_: BackboneElement | FHIRList[BackboneElement]
    definition: Optional[BackboneElement]
    manifest: Optional[BackboneElement]


class InsurancePlan(FHIRResource):
    _resource_type = "InsurancePlan"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'type', 'alias', 'coverageArea', 'contact', 'endpoint', 'network', 'coverage', 'plan'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'period': 'Period', 'ownedBy': 'Reference', 'administeredBy': 'Reference', 'coverageArea': 'Reference', 'contact': 'BackboneElement', 'endpoint': 'Reference', 'network': 'Reference', 'coverage': 'BackboneElement', 'plan': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    type: CodeableConcept | FHIRList[CodeableConcept]
    name: Optional[String] = None
    alias: String | FHIRList[String] = None
    period: Optional[Period]
    ownedBy: Optional[Reference]
    administeredBy: Optional[Reference]
    coverageArea: Reference | FHIRList[Reference]
    contact: BackboneElement | FHIRList[BackboneElement]
    endpoint: Reference | FHIRList[Reference]
    network: Reference | FHIRList[Reference]
    coverage: BackboneElement | FHIRList[BackboneElement]
    plan: BackboneElement | FHIRList[BackboneElement]


class Invoice(FHIRResource):
    _resource_type = "Invoice"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'participant', 'lineItem', 'totalPriceComponent', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'subject': 'Reference', 'recipient': 'Reference', 'participant': 'BackboneElement', 'issuer': 'Reference', 'account': 'Reference', 'lineItem': 'BackboneElement', 'totalNet': 'Money', 'totalGross': 'Money', 'note': 'Annotation'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    cancelledReason: Optional[String] = None
    type: Optional[CodeableConcept]
    subject: Optional[Reference]
    recipient: Optional[Reference]
    date: Optional[DateTime] = None
    participant: BackboneElement | FHIRList[BackboneElement]
    issuer: Optional[Reference]
    account: Optional[Reference]
    lineItem: BackboneElement | FHIRList[BackboneElement]
    totalPriceComponent: Any = None
    totalNet: Optional[Money]
    totalGross: Optional[Money]
    paymentTerms: Optional[Markdown] = None
    note: Annotation | FHIRList[Annotation]


class Library(FHIRResource):
    _resource_type = "Library"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'parameter', 'dataRequirement', 'content'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'parameter': 'ParameterDefinition', 'dataRequirement': 'DataRequirement', 'content': 'Attachment'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    type: Optional[CodeableConcept]
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    topic: CodeableConcept | FHIRList[CodeableConcept]
    author: ContactDetail | FHIRList[ContactDetail]
    editor: ContactDetail | FHIRList[ContactDetail]
    reviewer: ContactDetail | FHIRList[ContactDetail]
    endorser: ContactDetail | FHIRList[ContactDetail]
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact]
    parameter: ParameterDefinition | FHIRList[ParameterDefinition]
    dataRequirement: DataRequirement | FHIRList[DataRequirement]
    content: Attachment | FHIRList[Attachment]


class Linkage(FHIRResource):
    _resource_type = "Linkage"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'item'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'author': 'Reference', 'item': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    active: Optional[Boolean] = None
    author: Optional[Reference]
    item: BackboneElement | FHIRList[BackboneElement]


class List(FHIRResource):
    _resource_type = "List"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'note', 'entry'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'code': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'source': 'Reference', 'orderedBy': 'CodeableConcept', 'note': 'Annotation', 'entry': 'BackboneElement', 'emptyReason': 'CodeableConcept'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    mode: Optional[Code] = None
    title: Optional[String] = None
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    date: Optional[DateTime] = None
    source: Optional[Reference]
    orderedBy: Optional[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    entry: BackboneElement | FHIRList[BackboneElement]
    emptyReason: Optional[CodeableConcept]


class Location(FHIRResource):
    _resource_type = "Location"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'alias', 'type', 'telecom', 'hoursOfOperation', 'endpoint'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'operationalStatus': 'Coding', 'type': 'CodeableConcept', 'telecom': 'ContactPoint', 'address': 'Address', 'physicalType': 'CodeableConcept', 'position': 'BackboneElement', 'managingOrganization': 'Reference', 'partOf': 'Reference', 'hoursOfOperation': 'BackboneElement', 'endpoint': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    operationalStatus: Optional[Coding]
    name: Optional[String] = None
    alias: String | FHIRList[String] = None
    description: Optional[String] = None
    mode: Optional[Code] = None
    type: CodeableConcept | FHIRList[CodeableConcept]
    telecom: ContactPoint | FHIRList[ContactPoint]
    address: Optional[Address]
    physicalType: Optional[CodeableConcept]
    position: Optional[BackboneElement]
    managingOrganization: Optional[Reference]
    partOf: Optional[Reference]
    hoursOfOperation: BackboneElement | FHIRList[BackboneElement]
    availabilityExceptions: Optional[String] = None
    endpoint: Reference | FHIRList[Reference]


class Measure(FHIRResource):
    _resource_type = "Measure"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'library', 'type', 'definition', 'group', 'supplementalData'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'scoring': 'CodeableConcept', 'compositeScoring': 'CodeableConcept', 'type': 'CodeableConcept', 'improvementNotation': 'CodeableConcept', 'group': 'BackboneElement', 'supplementalData': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    topic: CodeableConcept | FHIRList[CodeableConcept]
    author: ContactDetail | FHIRList[ContactDetail]
    editor: ContactDetail | FHIRList[ContactDetail]
    reviewer: ContactDetail | FHIRList[ContactDetail]
    endorser: ContactDetail | FHIRList[ContactDetail]
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact]
    library: Canonical | FHIRList[Canonical] = None
    disclaimer: Optional[Markdown] = None
    scoring: Optional[CodeableConcept]
    compositeScoring: Optional[CodeableConcept]
    type: CodeableConcept | FHIRList[CodeableConcept]
    riskAdjustment: Optional[String] = None
    rateAggregation: Optional[String] = None
    rationale: Optional[Markdown] = None
    clinicalRecommendationStatement: Optional[Markdown] = None
    improvementNotation: Optional[CodeableConcept]
    definition: Markdown | FHIRList[Markdown] = None
    guidance: Optional[Markdown] = None
    group: BackboneElement | FHIRList[BackboneElement]
    supplementalData: BackboneElement | FHIRList[BackboneElement]


class MeasureReport(FHIRResource):
    _resource_type = "MeasureReport"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'group', 'evaluatedResource'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'subject': 'Reference', 'reporter': 'Reference', 'period': 'Period', 'improvementNotation': 'CodeableConcept', 'group': 'BackboneElement', 'evaluatedResource': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    type: Optional[Code] = None
    measure: Optional[Canonical] = None
    subject: Optional[Reference]
    date: Optional[DateTime] = None
    reporter: Optional[Reference]
    period: Optional[Period]
    improvementNotation: Optional[CodeableConcept]
    group: BackboneElement | FHIRList[BackboneElement]
    evaluatedResource: Reference | FHIRList[Reference]


class Media(FHIRResource):
    _resource_type = "Media"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'reasonCode', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'type': 'CodeableConcept', 'modality': 'CodeableConcept', 'view': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'operator': 'Reference', 'reasonCode': 'CodeableConcept', 'bodySite': 'CodeableConcept', 'device': 'Reference', 'content': 'Attachment', 'note': 'Annotation'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    type: Optional[CodeableConcept]
    modality: Optional[CodeableConcept]
    view: Optional[CodeableConcept]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    issued: Optional[Instant] = None
    operator: Optional[Reference]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    bodySite: Optional[CodeableConcept]
    deviceName: Optional[String] = None
    device: Optional[Reference]
    height: Optional[PositiveInt] = None
    width: Optional[PositiveInt] = None
    frames: Optional[PositiveInt] = None
    duration: Optional[Decimal] = None
    content: Optional[Attachment]
    note: Annotation | FHIRList[Annotation]


class Medication(FHIRResource):
    _resource_type = "Medication"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'ingredient'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'code': 'CodeableConcept', 'manufacturer': 'Reference', 'form': 'CodeableConcept', 'amount': 'Ratio', 'ingredient': 'BackboneElement', 'batch': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    code: Optional[CodeableConcept]
    status: Optional[Code] = None
    manufacturer: Optional[Reference]
    form: Optional[CodeableConcept]
    amount: Optional[Ratio]
    ingredient: BackboneElement | FHIRList[BackboneElement]
    batch: Optional[BackboneElement]


class MedicationAdministration(FHIRResource):
    _resource_type = "MedicationAdministration"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'instantiates', 'partOf', 'statusReason', 'supportingInformation', 'performer', 'reasonCode', 'reasonReference', 'device', 'note', 'eventHistory'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'partOf': 'Reference', 'statusReason': 'CodeableConcept', 'category': 'CodeableConcept', 'subject': 'Reference', 'context': 'Reference', 'supportingInformation': 'Reference', 'performer': 'BackboneElement', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'request': 'Reference', 'device': 'Reference', 'note': 'Annotation', 'dosage': 'BackboneElement', 'eventHistory': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    instantiates: Uri | FHIRList[Uri] = None
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    statusReason: CodeableConcept | FHIRList[CodeableConcept]
    category: Optional[CodeableConcept]
    subject: Optional[Reference]
    context: Optional[Reference]
    supportingInformation: Reference | FHIRList[Reference]
    performer: BackboneElement | FHIRList[BackboneElement]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    request: Optional[Reference]
    device: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]
    dosage: Optional[BackboneElement]
    eventHistory: Reference | FHIRList[Reference]


class MedicationDispense(FHIRResource):
    _resource_type = "MedicationDispense"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'partOf', 'supportingInformation', 'performer', 'authorizingPrescription', 'receiver', 'note', 'dosageInstruction', 'detectedIssue', 'eventHistory'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'partOf': 'Reference', 'category': 'CodeableConcept', 'subject': 'Reference', 'context': 'Reference', 'supportingInformation': 'Reference', 'performer': 'BackboneElement', 'location': 'Reference', 'authorizingPrescription': 'Reference', 'type': 'CodeableConcept', 'quantity': 'Quantity', 'daysSupply': 'Quantity', 'destination': 'Reference', 'receiver': 'Reference', 'note': 'Annotation', 'dosageInstruction': 'Dosage', 'substitution': 'BackboneElement', 'detectedIssue': 'Reference', 'eventHistory': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: Optional[CodeableConcept]
    subject: Optional[Reference]
    context: Optional[Reference]
    supportingInformation: Reference | FHIRList[Reference]
    performer: BackboneElement | FHIRList[BackboneElement]
    location: Optional[Reference]
    authorizingPrescription: Reference | FHIRList[Reference]
    type: Optional[CodeableConcept]
    quantity: Optional[Quantity]
    daysSupply: Optional[Quantity]
    whenPrepared: Optional[DateTime] = None
    whenHandedOver: Optional[DateTime] = None
    destination: Optional[Reference]
    receiver: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]
    dosageInstruction: Dosage | FHIRList[Dosage]
    substitution: Optional[BackboneElement]
    detectedIssue: Reference | FHIRList[Reference]
    eventHistory: Reference | FHIRList[Reference]


class MedicationKnowledge(FHIRResource):
    _resource_type = "MedicationKnowledge"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'synonym', 'relatedMedicationKnowledge', 'associatedMedication', 'productType', 'monograph', 'ingredient', 'intendedRoute', 'cost', 'monitoringProgram', 'administrationGuidelines', 'medicineClassification', 'drugCharacteristic', 'contraindication', 'regulatory', 'kinetics'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'manufacturer': 'Reference', 'doseForm': 'CodeableConcept', 'amount': 'Quantity', 'relatedMedicationKnowledge': 'BackboneElement', 'associatedMedication': 'Reference', 'productType': 'CodeableConcept', 'monograph': 'BackboneElement', 'ingredient': 'BackboneElement', 'intendedRoute': 'CodeableConcept', 'cost': 'BackboneElement', 'monitoringProgram': 'BackboneElement', 'administrationGuidelines': 'BackboneElement', 'medicineClassification': 'BackboneElement', 'packaging': 'BackboneElement', 'drugCharacteristic': 'BackboneElement', 'contraindication': 'Reference', 'regulatory': 'BackboneElement', 'kinetics': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    status: Optional[Code] = None
    manufacturer: Optional[Reference]
    doseForm: Optional[CodeableConcept]
    amount: Optional[Quantity]
    synonym: String | FHIRList[String] = None
    relatedMedicationKnowledge: BackboneElement | FHIRList[BackboneElement]
    associatedMedication: Reference | FHIRList[Reference]
    productType: CodeableConcept | FHIRList[CodeableConcept]
    monograph: BackboneElement | FHIRList[BackboneElement]
    ingredient: BackboneElement | FHIRList[BackboneElement]
    preparationInstruction: Optional[Markdown] = None
    intendedRoute: CodeableConcept | FHIRList[CodeableConcept]
    cost: BackboneElement | FHIRList[BackboneElement]
    monitoringProgram: BackboneElement | FHIRList[BackboneElement]
    administrationGuidelines: BackboneElement | FHIRList[BackboneElement]
    medicineClassification: BackboneElement | FHIRList[BackboneElement]
    packaging: Optional[BackboneElement]
    drugCharacteristic: BackboneElement | FHIRList[BackboneElement]
    contraindication: Reference | FHIRList[Reference]
    regulatory: BackboneElement | FHIRList[BackboneElement]
    kinetics: BackboneElement | FHIRList[BackboneElement]


class MedicationRequest(FHIRResource):
    _resource_type = "MedicationRequest"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'supportingInformation', 'reasonCode', 'reasonReference', 'instantiatesCanonical', 'instantiatesUri', 'basedOn', 'insurance', 'note', 'dosageInstruction', 'detectedIssue', 'eventHistory'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'statusReason': 'CodeableConcept', 'category': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'supportingInformation': 'Reference', 'requester': 'Reference', 'performer': 'Reference', 'performerType': 'CodeableConcept', 'recorder': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'basedOn': 'Reference', 'groupIdentifier': 'Identifier', 'courseOfTherapyType': 'CodeableConcept', 'insurance': 'Reference', 'note': 'Annotation', 'dosageInstruction': 'Dosage', 'dispenseRequest': 'BackboneElement', 'substitution': 'BackboneElement', 'priorPrescription': 'Reference', 'detectedIssue': 'Reference', 'eventHistory': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    statusReason: Optional[CodeableConcept]
    intent: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    priority: Optional[Code] = None
    doNotPerform: Optional[Boolean] = None
    subject: Optional[Reference]
    encounter: Optional[Reference]
    supportingInformation: Reference | FHIRList[Reference]
    authoredOn: Optional[DateTime] = None
    requester: Optional[Reference]
    performer: Optional[Reference]
    performerType: Optional[CodeableConcept]
    recorder: Optional[Reference]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    instantiatesCanonical: Canonical | FHIRList[Canonical] = None
    instantiatesUri: Uri | FHIRList[Uri] = None
    basedOn: Reference | FHIRList[Reference]
    groupIdentifier: Optional[Identifier]
    courseOfTherapyType: Optional[CodeableConcept]
    insurance: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]
    dosageInstruction: Dosage | FHIRList[Dosage]
    dispenseRequest: Optional[BackboneElement]
    substitution: Optional[BackboneElement]
    priorPrescription: Optional[Reference]
    detectedIssue: Reference | FHIRList[Reference]
    eventHistory: Reference | FHIRList[Reference]


class MedicationStatement(FHIRResource):
    _resource_type = "MedicationStatement"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'statusReason', 'derivedFrom', 'reasonCode', 'reasonReference', 'note', 'dosage'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'statusReason': 'CodeableConcept', 'category': 'CodeableConcept', 'subject': 'Reference', 'context': 'Reference', 'informationSource': 'Reference', 'derivedFrom': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'note': 'Annotation', 'dosage': 'Dosage'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    statusReason: CodeableConcept | FHIRList[CodeableConcept]
    category: Optional[CodeableConcept]
    subject: Optional[Reference]
    context: Optional[Reference]
    dateAsserted: Optional[DateTime] = None
    informationSource: Optional[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]
    dosage: Dosage | FHIRList[Dosage]


class MedicinalProduct(FHIRResource):
    _resource_type = "MedicinalProduct"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'specialMeasures', 'productClassification', 'marketingStatus', 'pharmaceuticalProduct', 'packagedMedicinalProduct', 'attachedDocument', 'masterFile', 'contact', 'clinicalTrial', 'name', 'crossReference', 'manufacturingBusinessOperation', 'specialDesignation'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'domain': 'Coding', 'combinedPharmaceuticalDoseForm': 'CodeableConcept', 'legalStatusOfSupply': 'CodeableConcept', 'additionalMonitoringIndicator': 'CodeableConcept', 'paediatricUseIndicator': 'CodeableConcept', 'productClassification': 'CodeableConcept', 'marketingStatus': 'MarketingStatus', 'pharmaceuticalProduct': 'Reference', 'packagedMedicinalProduct': 'Reference', 'attachedDocument': 'Reference', 'masterFile': 'Reference', 'contact': 'Reference', 'clinicalTrial': 'Reference', 'name': 'BackboneElement', 'crossReference': 'Identifier', 'manufacturingBusinessOperation': 'BackboneElement', 'specialDesignation': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    type: Optional[CodeableConcept]
    domain: Optional[Coding]
    combinedPharmaceuticalDoseForm: Optional[CodeableConcept]
    legalStatusOfSupply: Optional[CodeableConcept]
    additionalMonitoringIndicator: Optional[CodeableConcept]
    specialMeasures: String | FHIRList[String] = None
    paediatricUseIndicator: Optional[CodeableConcept]
    productClassification: CodeableConcept | FHIRList[CodeableConcept]
    marketingStatus: MarketingStatus | FHIRList[MarketingStatus]
    pharmaceuticalProduct: Reference | FHIRList[Reference]
    packagedMedicinalProduct: Reference | FHIRList[Reference]
    attachedDocument: Reference | FHIRList[Reference]
    masterFile: Reference | FHIRList[Reference]
    contact: Reference | FHIRList[Reference]
    clinicalTrial: Reference | FHIRList[Reference]
    name: BackboneElement | FHIRList[BackboneElement]
    crossReference: Identifier | FHIRList[Identifier]
    manufacturingBusinessOperation: BackboneElement | FHIRList[BackboneElement]
    specialDesignation: BackboneElement | FHIRList[BackboneElement]


class MedicinalProductAuthorization(FHIRResource):
    _resource_type = "MedicinalProductAuthorization"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'country', 'jurisdiction', 'jurisdictionalAuthorization'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'subject': 'Reference', 'country': 'CodeableConcept', 'jurisdiction': 'CodeableConcept', 'status': 'CodeableConcept', 'validityPeriod': 'Period', 'dataExclusivityPeriod': 'Period', 'legalBasis': 'CodeableConcept', 'jurisdictionalAuthorization': 'BackboneElement', 'holder': 'Reference', 'regulator': 'Reference', 'procedure': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    subject: Optional[Reference]
    country: CodeableConcept | FHIRList[CodeableConcept]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    status: Optional[CodeableConcept]
    statusDate: Optional[DateTime] = None
    restoreDate: Optional[DateTime] = None
    validityPeriod: Optional[Period]
    dataExclusivityPeriod: Optional[Period]
    dateOfFirstAuthorization: Optional[DateTime] = None
    internationalBirthDate: Optional[DateTime] = None
    legalBasis: Optional[CodeableConcept]
    jurisdictionalAuthorization: BackboneElement | FHIRList[BackboneElement]
    holder: Optional[Reference]
    regulator: Optional[Reference]
    procedure: Optional[BackboneElement]


class MedicinalProductContraindication(FHIRResource):
    _resource_type = "MedicinalProductContraindication"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'subject', 'comorbidity', 'therapeuticIndication', 'otherTherapy', 'population'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'subject': 'Reference', 'disease': 'CodeableConcept', 'diseaseStatus': 'CodeableConcept', 'comorbidity': 'CodeableConcept', 'therapeuticIndication': 'Reference', 'otherTherapy': 'BackboneElement', 'population': 'Population'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    subject: Reference | FHIRList[Reference]
    disease: Optional[CodeableConcept]
    diseaseStatus: Optional[CodeableConcept]
    comorbidity: CodeableConcept | FHIRList[CodeableConcept]
    therapeuticIndication: Reference | FHIRList[Reference]
    otherTherapy: BackboneElement | FHIRList[BackboneElement]
    population: Population | FHIRList[Population]


class MedicinalProductIndication(FHIRResource):
    _resource_type = "MedicinalProductIndication"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'subject', 'comorbidity', 'otherTherapy', 'undesirableEffect', 'population'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'subject': 'Reference', 'diseaseSymptomProcedure': 'CodeableConcept', 'diseaseStatus': 'CodeableConcept', 'comorbidity': 'CodeableConcept', 'intendedEffect': 'CodeableConcept', 'duration': 'Quantity', 'otherTherapy': 'BackboneElement', 'undesirableEffect': 'Reference', 'population': 'Population'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    subject: Reference | FHIRList[Reference]
    diseaseSymptomProcedure: Optional[CodeableConcept]
    diseaseStatus: Optional[CodeableConcept]
    comorbidity: CodeableConcept | FHIRList[CodeableConcept]
    intendedEffect: Optional[CodeableConcept]
    duration: Optional[Quantity]
    otherTherapy: BackboneElement | FHIRList[BackboneElement]
    undesirableEffect: Reference | FHIRList[Reference]
    population: Population | FHIRList[Population]


class MedicinalProductIngredient(FHIRResource):
    _resource_type = "MedicinalProductIngredient"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'manufacturer', 'specifiedSubstance'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'role': 'CodeableConcept', 'manufacturer': 'Reference', 'specifiedSubstance': 'BackboneElement', 'substance': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Identifier]
    role: Optional[CodeableConcept]
    allergenicIndicator: Optional[Boolean] = None
    manufacturer: Reference | FHIRList[Reference]
    specifiedSubstance: BackboneElement | FHIRList[BackboneElement]
    substance: Optional[BackboneElement]


class MedicinalProductInteraction(FHIRResource):
    _resource_type = "MedicinalProductInteraction"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'subject', 'interactant'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'subject': 'Reference', 'interactant': 'BackboneElement', 'type': 'CodeableConcept', 'effect': 'CodeableConcept', 'incidence': 'CodeableConcept', 'management': 'CodeableConcept'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    subject: Reference | FHIRList[Reference]
    description: Optional[String] = None
    interactant: BackboneElement | FHIRList[BackboneElement]
    type: Optional[CodeableConcept]
    effect: Optional[CodeableConcept]
    incidence: Optional[CodeableConcept]
    management: Optional[CodeableConcept]


class MedicinalProductManufactured(FHIRResource):
    _resource_type = "MedicinalProductManufactured"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'manufacturer', 'ingredient', 'otherCharacteristics'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'manufacturedDoseForm': 'CodeableConcept', 'unitOfPresentation': 'CodeableConcept', 'quantity': 'Quantity', 'manufacturer': 'Reference', 'ingredient': 'Reference', 'physicalCharacteristics': 'ProdCharacteristic', 'otherCharacteristics': 'CodeableConcept'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    manufacturedDoseForm: Optional[CodeableConcept]
    unitOfPresentation: Optional[CodeableConcept]
    quantity: Optional[Quantity]
    manufacturer: Reference | FHIRList[Reference]
    ingredient: Reference | FHIRList[Reference]
    physicalCharacteristics: Optional[ProdCharacteristic]
    otherCharacteristics: CodeableConcept | FHIRList[CodeableConcept]


class MedicinalProductPackaged(FHIRResource):
    _resource_type = "MedicinalProductPackaged"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'subject', 'marketingStatus', 'manufacturer', 'batchIdentifier', 'packageItem'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'subject': 'Reference', 'legalStatusOfSupply': 'CodeableConcept', 'marketingStatus': 'MarketingStatus', 'marketingAuthorization': 'Reference', 'manufacturer': 'Reference', 'batchIdentifier': 'BackboneElement', 'packageItem': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    subject: Reference | FHIRList[Reference]
    description: Optional[String] = None
    legalStatusOfSupply: Optional[CodeableConcept]
    marketingStatus: MarketingStatus | FHIRList[MarketingStatus]
    marketingAuthorization: Optional[Reference]
    manufacturer: Reference | FHIRList[Reference]
    batchIdentifier: BackboneElement | FHIRList[BackboneElement]
    packageItem: BackboneElement | FHIRList[BackboneElement]


class MedicinalProductPharmaceutical(FHIRResource):
    _resource_type = "MedicinalProductPharmaceutical"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'ingredient', 'device', 'characteristics', 'routeOfAdministration'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'administrableDoseForm': 'CodeableConcept', 'unitOfPresentation': 'CodeableConcept', 'ingredient': 'Reference', 'device': 'Reference', 'characteristics': 'BackboneElement', 'routeOfAdministration': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    administrableDoseForm: Optional[CodeableConcept]
    unitOfPresentation: Optional[CodeableConcept]
    ingredient: Reference | FHIRList[Reference]
    device: Reference | FHIRList[Reference]
    characteristics: BackboneElement | FHIRList[BackboneElement]
    routeOfAdministration: BackboneElement | FHIRList[BackboneElement]


class MedicinalProductUndesirableEffect(FHIRResource):
    _resource_type = "MedicinalProductUndesirableEffect"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'subject', 'population'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'subject': 'Reference', 'symptomConditionEffect': 'CodeableConcept', 'classification': 'CodeableConcept', 'frequencyOfOccurrence': 'CodeableConcept', 'population': 'Population'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    subject: Reference | FHIRList[Reference]
    symptomConditionEffect: Optional[CodeableConcept]
    classification: Optional[CodeableConcept]
    frequencyOfOccurrence: Optional[CodeableConcept]
    population: Population | FHIRList[Population]


class MessageDefinition(FHIRResource):
    _resource_type = "MessageDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'replaces', 'contact', 'useContext', 'jurisdiction', 'parent', 'focus', 'allowedResponse', 'graph'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'focus': 'BackboneElement', 'allowedResponse': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    replaces: Canonical | FHIRList[Canonical] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    base: Optional[Canonical] = None
    parent: Canonical | FHIRList[Canonical] = None
    category: Optional[Code] = None
    focus: BackboneElement | FHIRList[BackboneElement]
    responseRequired: Optional[Code] = None
    allowedResponse: BackboneElement | FHIRList[BackboneElement]
    graph: Canonical | FHIRList[Canonical] = None


class MessageHeader(FHIRResource):
    _resource_type = "MessageHeader"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'destination', 'focus'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'destination': 'BackboneElement', 'sender': 'Reference', 'enterer': 'Reference', 'author': 'Reference', 'source': 'BackboneElement', 'responsible': 'Reference', 'reason': 'CodeableConcept', 'response': 'BackboneElement', 'focus': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    destination: BackboneElement | FHIRList[BackboneElement]
    sender: Optional[Reference]
    enterer: Optional[Reference]
    author: Optional[Reference]
    source: Optional[BackboneElement]
    responsible: Optional[Reference]
    reason: Optional[CodeableConcept]
    response: Optional[BackboneElement]
    focus: Reference | FHIRList[Reference]
    definition: Optional[Canonical] = None


class MolecularSequence(FHIRResource):
    _resource_type = "MolecularSequence"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'variant', 'quality', 'repository', 'pointer', 'structureVariant'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'patient': 'Reference', 'specimen': 'Reference', 'device': 'Reference', 'performer': 'Reference', 'quantity': 'Quantity', 'referenceSeq': 'BackboneElement', 'variant': 'BackboneElement', 'quality': 'BackboneElement', 'repository': 'BackboneElement', 'pointer': 'Reference', 'structureVariant': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    type: Optional[Code] = None
    coordinateSystem: Optional[Integer] = None
    patient: Optional[Reference]
    specimen: Optional[Reference]
    device: Optional[Reference]
    performer: Optional[Reference]
    quantity: Optional[Quantity]
    referenceSeq: Optional[BackboneElement]
    variant: BackboneElement | FHIRList[BackboneElement]
    observedSeq: Optional[String] = None
    quality: BackboneElement | FHIRList[BackboneElement]
    readCoverage: Optional[Integer] = None
    repository: BackboneElement | FHIRList[BackboneElement]
    pointer: Reference | FHIRList[Reference]
    structureVariant: BackboneElement | FHIRList[BackboneElement]


class NamingSystem(FHIRResource):
    _resource_type = "NamingSystem"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'uniqueId'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'contact': 'ContactDetail', 'type': 'CodeableConcept', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'uniqueId': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[String] = None
    status: Optional[Code] = None
    kind: Optional[Code] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    responsible: Optional[String] = None
    type: Optional[CodeableConcept]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    usage: Optional[String] = None
    uniqueId: BackboneElement | FHIRList[BackboneElement]


class NutritionOrder(FHIRResource):
    _resource_type = "NutritionOrder"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'instantiatesCanonical', 'instantiatesUri', 'instantiates', 'allergyIntolerance', 'foodPreferenceModifier', 'excludeFoodModifier', 'supplement', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'patient': 'Reference', 'encounter': 'Reference', 'orderer': 'Reference', 'allergyIntolerance': 'Reference', 'foodPreferenceModifier': 'CodeableConcept', 'excludeFoodModifier': 'CodeableConcept', 'oralDiet': 'BackboneElement', 'supplement': 'BackboneElement', 'enteralFormula': 'BackboneElement', 'note': 'Annotation'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    instantiatesCanonical: Canonical | FHIRList[Canonical] = None
    instantiatesUri: Uri | FHIRList[Uri] = None
    instantiates: Uri | FHIRList[Uri] = None
    status: Optional[Code] = None
    intent: Optional[Code] = None
    patient: Optional[Reference]
    encounter: Optional[Reference]
    dateTime: Optional[DateTime] = None
    orderer: Optional[Reference]
    allergyIntolerance: Reference | FHIRList[Reference]
    foodPreferenceModifier: CodeableConcept | FHIRList[CodeableConcept]
    excludeFoodModifier: CodeableConcept | FHIRList[CodeableConcept]
    oralDiet: Optional[BackboneElement]
    supplement: BackboneElement | FHIRList[BackboneElement]
    enteralFormula: Optional[BackboneElement]
    note: Annotation | FHIRList[Annotation]


class Observation(FHIRResource):
    _resource_type = "Observation"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'BackboneElement', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: BackboneElement | FHIRList[BackboneElement]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: BackboneElement | FHIRList[BackboneElement]


class ObservationDefinition(FHIRResource):
    _resource_type = "ObservationDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'category', 'identifier', 'permittedDataType', 'qualifiedInterval'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'identifier': 'Identifier', 'method': 'CodeableConcept', 'quantitativeDetails': 'BackboneElement', 'qualifiedInterval': 'BackboneElement', 'validCodedValueSet': 'Reference', 'normalCodedValueSet': 'Reference', 'abnormalCodedValueSet': 'Reference', 'criticalCodedValueSet': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    category: CodeableConcept | FHIRList[CodeableConcept]
    code: Optional[CodeableConcept]
    identifier: Identifier | FHIRList[Identifier]
    permittedDataType: Code | FHIRList[Code] = None
    multipleResultsAllowed: Optional[Boolean] = None
    method: Optional[CodeableConcept]
    preferredReportName: Optional[String] = None
    quantitativeDetails: Optional[BackboneElement]
    qualifiedInterval: BackboneElement | FHIRList[BackboneElement]
    validCodedValueSet: Optional[Reference]
    normalCodedValueSet: Optional[Reference]
    abnormalCodedValueSet: Optional[Reference]
    criticalCodedValueSet: Optional[Reference]


class OperationDefinition(FHIRResource):
    _resource_type = "OperationDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'resource', 'parameter', 'overload'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'parameter': 'BackboneElement', 'overload': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    kind: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    affectsState: Optional[Boolean] = None
    code: Optional[Code] = None
    comment: Optional[Markdown] = None
    base: Optional[Canonical] = None
    resource: Code | FHIRList[Code] = None
    system: Optional[Boolean] = None
    type: Optional[Boolean] = None
    instance: Optional[Boolean] = None
    inputProfile: Optional[Canonical] = None
    outputProfile: Optional[Canonical] = None
    parameter: BackboneElement | FHIRList[BackboneElement]
    overload: BackboneElement | FHIRList[BackboneElement]


class OperationOutcome(FHIRResource):
    _resource_type = "OperationOutcome"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'issue'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'issue': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    issue: BackboneElement | FHIRList[BackboneElement]


class Organization(FHIRResource):
    _resource_type = "Organization"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'type', 'alias', 'telecom', 'address', 'contact', 'endpoint'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'telecom': 'ContactPoint', 'address': 'Address', 'partOf': 'Reference', 'contact': 'BackboneElement', 'endpoint': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    active: Optional[Boolean] = None
    type: CodeableConcept | FHIRList[CodeableConcept]
    name: Optional[String] = None
    alias: String | FHIRList[String] = None
    telecom: ContactPoint | FHIRList[ContactPoint]
    address: Address | FHIRList[Address]
    partOf: Optional[Reference]
    contact: BackboneElement | FHIRList[BackboneElement]
    endpoint: Reference | FHIRList[Reference]


class OrganizationAffiliation(FHIRResource):
    _resource_type = "OrganizationAffiliation"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'network', 'code', 'specialty', 'location', 'healthcareService', 'telecom', 'endpoint'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'period': 'Period', 'organization': 'Reference', 'participatingOrganization': 'Reference', 'network': 'Reference', 'code': 'CodeableConcept', 'specialty': 'CodeableConcept', 'location': 'Reference', 'healthcareService': 'Reference', 'telecom': 'ContactPoint', 'endpoint': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    active: Optional[Boolean] = None
    period: Optional[Period]
    organization: Optional[Reference]
    participatingOrganization: Optional[Reference]
    network: Reference | FHIRList[Reference]
    code: CodeableConcept | FHIRList[CodeableConcept]
    specialty: CodeableConcept | FHIRList[CodeableConcept]
    location: Reference | FHIRList[Reference]
    healthcareService: Reference | FHIRList[Reference]
    telecom: ContactPoint | FHIRList[ContactPoint]
    endpoint: Reference | FHIRList[Reference]


class Patient(FHIRResource):
    _resource_type = "Patient"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'name', 'telecom', 'address', 'photo', 'contact', 'communication', 'generalPractitioner', 'link'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'name': 'HumanName', 'telecom': 'ContactPoint', 'address': 'Address', 'maritalStatus': 'CodeableConcept', 'photo': 'Attachment', 'contact': 'BackboneElement', 'communication': 'BackboneElement', 'generalPractitioner': 'Reference', 'managingOrganization': 'Reference', 'link': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    active: Optional[Boolean] = None
    name: HumanName | FHIRList[HumanName]
    telecom: ContactPoint | FHIRList[ContactPoint]
    gender: Optional[Code] = None
    birthDate: Optional[Date] = None
    address: Address | FHIRList[Address]
    maritalStatus: Optional[CodeableConcept]
    photo: Attachment | FHIRList[Attachment]
    contact: BackboneElement | FHIRList[BackboneElement]
    communication: BackboneElement | FHIRList[BackboneElement]
    generalPractitioner: Reference | FHIRList[Reference]
    managingOrganization: Optional[Reference]
    link: BackboneElement | FHIRList[BackboneElement]


class PaymentNotice(FHIRResource):
    _resource_type = "PaymentNotice"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'request': 'Reference', 'response': 'Reference', 'provider': 'Reference', 'payment': 'Reference', 'payee': 'Reference', 'recipient': 'Reference', 'amount': 'Money', 'paymentStatus': 'CodeableConcept'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    request: Optional[Reference]
    response: Optional[Reference]
    created: Optional[DateTime] = None
    provider: Optional[Reference]
    payment: Optional[Reference]
    paymentDate: Optional[Date] = None
    payee: Optional[Reference]
    recipient: Optional[Reference]
    amount: Optional[Money]
    paymentStatus: Optional[CodeableConcept]


class PaymentReconciliation(FHIRResource):
    _resource_type = "PaymentReconciliation"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'detail', 'processNote'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'period': 'Period', 'paymentIssuer': 'Reference', 'request': 'Reference', 'requestor': 'Reference', 'paymentAmount': 'Money', 'paymentIdentifier': 'Identifier', 'detail': 'BackboneElement', 'formCode': 'CodeableConcept', 'processNote': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    period: Optional[Period]
    created: Optional[DateTime] = None
    paymentIssuer: Optional[Reference]
    request: Optional[Reference]
    requestor: Optional[Reference]
    outcome: Optional[Code] = None
    disposition: Optional[String] = None
    paymentDate: Optional[Date] = None
    paymentAmount: Optional[Money]
    paymentIdentifier: Optional[Identifier]
    detail: BackboneElement | FHIRList[BackboneElement]
    formCode: Optional[CodeableConcept]
    processNote: BackboneElement | FHIRList[BackboneElement]


class Person(FHIRResource):
    _resource_type = "Person"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'name', 'telecom', 'address', 'link'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'name': 'HumanName', 'telecom': 'ContactPoint', 'address': 'Address', 'photo': 'Attachment', 'managingOrganization': 'Reference', 'link': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    name: HumanName | FHIRList[HumanName]
    telecom: ContactPoint | FHIRList[ContactPoint]
    gender: Optional[Code] = None
    birthDate: Optional[Date] = None
    address: Address | FHIRList[Address]
    photo: Optional[Attachment]
    managingOrganization: Optional[Reference]
    active: Optional[Boolean] = None
    link: BackboneElement | FHIRList[BackboneElement]


class PlanDefinition(FHIRResource):
    _resource_type = "PlanDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'library', 'goal', 'action'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'goal': 'BackboneElement', 'action': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    type: Optional[CodeableConcept]
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    topic: CodeableConcept | FHIRList[CodeableConcept]
    author: ContactDetail | FHIRList[ContactDetail]
    editor: ContactDetail | FHIRList[ContactDetail]
    reviewer: ContactDetail | FHIRList[ContactDetail]
    endorser: ContactDetail | FHIRList[ContactDetail]
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact]
    library: Canonical | FHIRList[Canonical] = None
    goal: BackboneElement | FHIRList[BackboneElement]
    action: BackboneElement | FHIRList[BackboneElement]


class Practitioner(FHIRResource):
    _resource_type = "Practitioner"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'name', 'telecom', 'address', 'photo', 'qualification', 'communication'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'name': 'HumanName', 'telecom': 'ContactPoint', 'address': 'Address', 'photo': 'Attachment', 'qualification': 'BackboneElement', 'communication': 'CodeableConcept'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    active: Optional[Boolean] = None
    name: HumanName | FHIRList[HumanName]
    telecom: ContactPoint | FHIRList[ContactPoint]
    address: Address | FHIRList[Address]
    gender: Optional[Code] = None
    birthDate: Optional[Date] = None
    photo: Attachment | FHIRList[Attachment]
    qualification: BackboneElement | FHIRList[BackboneElement]
    communication: CodeableConcept | FHIRList[CodeableConcept]


class PractitionerRole(FHIRResource):
    _resource_type = "PractitionerRole"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'code', 'specialty', 'location', 'healthcareService', 'telecom', 'availableTime', 'notAvailable', 'endpoint'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'period': 'Period', 'practitioner': 'Reference', 'organization': 'Reference', 'code': 'CodeableConcept', 'specialty': 'CodeableConcept', 'location': 'Reference', 'healthcareService': 'Reference', 'telecom': 'ContactPoint', 'availableTime': 'BackboneElement', 'notAvailable': 'BackboneElement', 'endpoint': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    active: Optional[Boolean] = None
    period: Optional[Period]
    practitioner: Optional[Reference]
    organization: Optional[Reference]
    code: CodeableConcept | FHIRList[CodeableConcept]
    specialty: CodeableConcept | FHIRList[CodeableConcept]
    location: Reference | FHIRList[Reference]
    healthcareService: Reference | FHIRList[Reference]
    telecom: ContactPoint | FHIRList[ContactPoint]
    availableTime: BackboneElement | FHIRList[BackboneElement]
    notAvailable: BackboneElement | FHIRList[BackboneElement]
    availabilityExceptions: Optional[String] = None
    endpoint: Reference | FHIRList[Reference]


class Procedure(FHIRResource):
    _resource_type = "Procedure"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'instantiatesCanonical', 'instantiatesUri', 'basedOn', 'partOf', 'performer', 'reasonCode', 'reasonReference', 'bodySite', 'report', 'complication', 'complicationDetail', 'followUp', 'note', 'focalDevice', 'usedReference', 'usedCode'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'statusReason': 'CodeableConcept', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'recorder': 'Reference', 'asserter': 'Reference', 'performer': 'BackboneElement', 'location': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'bodySite': 'CodeableConcept', 'outcome': 'CodeableConcept', 'report': 'Reference', 'complication': 'CodeableConcept', 'complicationDetail': 'Reference', 'followUp': 'CodeableConcept', 'note': 'Annotation', 'focalDevice': 'BackboneElement', 'usedReference': 'Reference', 'usedCode': 'CodeableConcept'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    instantiatesCanonical: Canonical | FHIRList[Canonical] = None
    instantiatesUri: Uri | FHIRList[Uri] = None
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    statusReason: Optional[CodeableConcept]
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    recorder: Optional[Reference]
    asserter: Optional[Reference]
    performer: BackboneElement | FHIRList[BackboneElement]
    location: Optional[Reference]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    bodySite: CodeableConcept | FHIRList[CodeableConcept]
    outcome: Optional[CodeableConcept]
    report: Reference | FHIRList[Reference]
    complication: CodeableConcept | FHIRList[CodeableConcept]
    complicationDetail: Reference | FHIRList[Reference]
    followUp: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    focalDevice: BackboneElement | FHIRList[BackboneElement]
    usedReference: Reference | FHIRList[Reference]
    usedCode: CodeableConcept | FHIRList[CodeableConcept]


class Provenance(FHIRResource):
    _resource_type = "Provenance"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'target', 'policy', 'reason', 'agent', 'entity', 'signature'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'target': 'Reference', 'location': 'Reference', 'reason': 'CodeableConcept', 'activity': 'CodeableConcept', 'agent': 'BackboneElement', 'entity': 'BackboneElement', 'signature': 'Signature'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    target: Reference | FHIRList[Reference]
    recorded: Optional[Instant] = None
    policy: Uri | FHIRList[Uri] = None
    location: Optional[Reference]
    reason: CodeableConcept | FHIRList[CodeableConcept]
    activity: Optional[CodeableConcept]
    agent: BackboneElement | FHIRList[BackboneElement]
    entity: BackboneElement | FHIRList[BackboneElement]
    signature: Signature | FHIRList[Signature]


class Questionnaire(FHIRResource):
    _resource_type = "Questionnaire"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'derivedFrom', 'subjectType', 'contact', 'useContext', 'jurisdiction', 'code', 'item'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'code': 'Coding', 'item': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    derivedFrom: Canonical | FHIRList[Canonical] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    subjectType: Code | FHIRList[Code] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    code: Coding | FHIRList[Coding]
    item: BackboneElement | FHIRList[BackboneElement]


class QuestionnaireResponse(FHIRResource):
    _resource_type = "QuestionnaireResponse"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'basedOn', 'partOf', 'item'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'subject': 'Reference', 'encounter': 'Reference', 'author': 'Reference', 'source': 'Reference', 'item': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Identifier]
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    questionnaire: Optional[Canonical] = None
    status: Optional[Code] = None
    subject: Optional[Reference]
    encounter: Optional[Reference]
    authored: Optional[DateTime] = None
    author: Optional[Reference]
    source: Optional[Reference]
    item: BackboneElement | FHIRList[BackboneElement]


class RelatedPerson(FHIRResource):
    _resource_type = "RelatedPerson"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'relationship', 'name', 'telecom', 'address', 'photo', 'communication'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'patient': 'Reference', 'relationship': 'CodeableConcept', 'name': 'HumanName', 'telecom': 'ContactPoint', 'address': 'Address', 'photo': 'Attachment', 'period': 'Period', 'communication': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    active: Optional[Boolean] = None
    patient: Optional[Reference]
    relationship: CodeableConcept | FHIRList[CodeableConcept]
    name: HumanName | FHIRList[HumanName]
    telecom: ContactPoint | FHIRList[ContactPoint]
    gender: Optional[Code] = None
    birthDate: Optional[Date] = None
    address: Address | FHIRList[Address]
    photo: Attachment | FHIRList[Attachment]
    period: Optional[Period]
    communication: BackboneElement | FHIRList[BackboneElement]


class RequestGroup(FHIRResource):
    _resource_type = "RequestGroup"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'instantiatesCanonical', 'instantiatesUri', 'basedOn', 'replaces', 'reasonCode', 'reasonReference', 'note', 'action'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'replaces': 'Reference', 'groupIdentifier': 'Identifier', 'code': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'author': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'note': 'Annotation', 'action': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    instantiatesCanonical: Canonical | FHIRList[Canonical] = None
    instantiatesUri: Uri | FHIRList[Uri] = None
    basedOn: Reference | FHIRList[Reference]
    replaces: Reference | FHIRList[Reference]
    groupIdentifier: Optional[Identifier]
    status: Optional[Code] = None
    intent: Optional[Code] = None
    priority: Optional[Code] = None
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    authoredOn: Optional[DateTime] = None
    author: Optional[Reference]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]
    action: BackboneElement | FHIRList[BackboneElement]


class ResearchDefinition(FHIRResource):
    _resource_type = "ResearchDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'comment', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'library'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'population': 'Reference', 'exposure': 'Reference', 'exposureAlternative': 'Reference', 'outcome': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    shortTitle: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    comment: String | FHIRList[String] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    topic: CodeableConcept | FHIRList[CodeableConcept]
    author: ContactDetail | FHIRList[ContactDetail]
    editor: ContactDetail | FHIRList[ContactDetail]
    reviewer: ContactDetail | FHIRList[ContactDetail]
    endorser: ContactDetail | FHIRList[ContactDetail]
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact]
    library: Canonical | FHIRList[Canonical] = None
    population: Optional[Reference]
    exposure: Optional[Reference]
    exposureAlternative: Optional[Reference]
    outcome: Optional[Reference]


class ResearchElementDefinition(FHIRResource):
    _resource_type = "ResearchElementDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'comment', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'library', 'characteristic'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'characteristic': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    shortTitle: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    comment: String | FHIRList[String] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    topic: CodeableConcept | FHIRList[CodeableConcept]
    author: ContactDetail | FHIRList[ContactDetail]
    editor: ContactDetail | FHIRList[ContactDetail]
    reviewer: ContactDetail | FHIRList[ContactDetail]
    endorser: ContactDetail | FHIRList[ContactDetail]
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact]
    library: Canonical | FHIRList[Canonical] = None
    type: Optional[Code] = None
    variableType: Optional[Code] = None
    characteristic: BackboneElement | FHIRList[BackboneElement]


class ResearchStudy(FHIRResource):
    _resource_type = "ResearchStudy"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'protocol', 'partOf', 'category', 'focus', 'condition', 'contact', 'relatedArtifact', 'keyword', 'location', 'enrollment', 'site', 'note', 'arm', 'objective'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'protocol': 'Reference', 'partOf': 'Reference', 'primaryPurposeType': 'CodeableConcept', 'phase': 'CodeableConcept', 'category': 'CodeableConcept', 'focus': 'CodeableConcept', 'condition': 'CodeableConcept', 'contact': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'keyword': 'CodeableConcept', 'location': 'CodeableConcept', 'enrollment': 'Reference', 'period': 'Period', 'sponsor': 'Reference', 'principalInvestigator': 'Reference', 'site': 'Reference', 'reasonStopped': 'CodeableConcept', 'note': 'Annotation', 'arm': 'BackboneElement', 'objective': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    title: Optional[String] = None
    protocol: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    primaryPurposeType: Optional[CodeableConcept]
    phase: Optional[CodeableConcept]
    category: CodeableConcept | FHIRList[CodeableConcept]
    focus: CodeableConcept | FHIRList[CodeableConcept]
    condition: CodeableConcept | FHIRList[CodeableConcept]
    contact: ContactDetail | FHIRList[ContactDetail]
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact]
    keyword: CodeableConcept | FHIRList[CodeableConcept]
    location: CodeableConcept | FHIRList[CodeableConcept]
    description: Optional[Markdown] = None
    enrollment: Reference | FHIRList[Reference]
    period: Optional[Period]
    sponsor: Optional[Reference]
    principalInvestigator: Optional[Reference]
    site: Reference | FHIRList[Reference]
    reasonStopped: Optional[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    arm: BackboneElement | FHIRList[BackboneElement]
    objective: BackboneElement | FHIRList[BackboneElement]


class ResearchSubject(FHIRResource):
    _resource_type = "ResearchSubject"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'period': 'Period', 'study': 'Reference', 'individual': 'Reference', 'consent': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    period: Optional[Period]
    study: Optional[Reference]
    individual: Optional[Reference]
    assignedArm: Optional[String] = None
    actualArm: Optional[String] = None
    consent: Optional[Reference]


class RiskAssessment(FHIRResource):
    _resource_type = "RiskAssessment"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'reasonCode', 'reasonReference', 'basis', 'prediction', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'parent': 'Reference', 'method': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'condition': 'Reference', 'performer': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'basis': 'Reference', 'prediction': 'BackboneElement', 'note': 'Annotation'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Optional[Reference]
    parent: Optional[Reference]
    status: Optional[Code] = None
    method: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    condition: Optional[Reference]
    performer: Optional[Reference]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    basis: Reference | FHIRList[Reference]
    prediction: BackboneElement | FHIRList[BackboneElement]
    mitigation: Optional[String] = None
    note: Annotation | FHIRList[Annotation]


class RiskEvidenceSynthesis(FHIRResource):
    _resource_type = "RiskEvidenceSynthesis"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'note', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'certainty'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'note': 'Annotation', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'synthesisType': 'CodeableConcept', 'studyType': 'CodeableConcept', 'population': 'Reference', 'exposure': 'Reference', 'outcome': 'Reference', 'sampleSize': 'BackboneElement', 'riskEstimate': 'BackboneElement', 'certainty': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    note: Annotation | FHIRList[Annotation]
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    topic: CodeableConcept | FHIRList[CodeableConcept]
    author: ContactDetail | FHIRList[ContactDetail]
    editor: ContactDetail | FHIRList[ContactDetail]
    reviewer: ContactDetail | FHIRList[ContactDetail]
    endorser: ContactDetail | FHIRList[ContactDetail]
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact]
    synthesisType: Optional[CodeableConcept]
    studyType: Optional[CodeableConcept]
    population: Optional[Reference]
    exposure: Optional[Reference]
    outcome: Optional[Reference]
    sampleSize: Optional[BackboneElement]
    riskEstimate: Optional[BackboneElement]
    certainty: BackboneElement | FHIRList[BackboneElement]


class Schedule(FHIRResource):
    _resource_type = "Schedule"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'serviceCategory', 'serviceType', 'specialty', 'actor'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'serviceCategory': 'CodeableConcept', 'serviceType': 'CodeableConcept', 'specialty': 'CodeableConcept', 'actor': 'Reference', 'planningHorizon': 'Period'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    active: Optional[Boolean] = None
    serviceCategory: CodeableConcept | FHIRList[CodeableConcept]
    serviceType: CodeableConcept | FHIRList[CodeableConcept]
    specialty: CodeableConcept | FHIRList[CodeableConcept]
    actor: Reference | FHIRList[Reference]
    planningHorizon: Optional[Period]
    comment: Optional[String] = None


class SearchParameter(FHIRResource):
    _resource_type = "SearchParameter"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'base', 'target', 'comparator', 'modifier', 'chain', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'component': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    version: Optional[String] = None
    name: Optional[String] = None
    derivedFrom: Optional[Canonical] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    code: Optional[Code] = None
    base: Code | FHIRList[Code] = None
    type: Optional[Code] = None
    expression: Optional[String] = None
    xpath: Optional[String] = None
    xpathUsage: Optional[Code] = None
    target: Code | FHIRList[Code] = None
    multipleOr: Optional[Boolean] = None
    multipleAnd: Optional[Boolean] = None
    comparator: Code | FHIRList[Code] = None
    modifier: Code | FHIRList[Code] = None
    chain: String | FHIRList[String] = None
    component: BackboneElement | FHIRList[BackboneElement]


class ServiceRequest(FHIRResource):
    _resource_type = "ServiceRequest"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'instantiatesCanonical', 'instantiatesUri', 'basedOn', 'replaces', 'category', 'orderDetail', 'performer', 'locationCode', 'locationReference', 'reasonCode', 'reasonReference', 'insurance', 'supportingInfo', 'specimen', 'bodySite', 'note', 'relevantHistory'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'replaces': 'Reference', 'requisition': 'Identifier', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'orderDetail': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'requester': 'Reference', 'performerType': 'CodeableConcept', 'performer': 'Reference', 'locationCode': 'CodeableConcept', 'locationReference': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'insurance': 'Reference', 'supportingInfo': 'Reference', 'specimen': 'Reference', 'bodySite': 'CodeableConcept', 'note': 'Annotation', 'relevantHistory': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    instantiatesCanonical: Canonical | FHIRList[Canonical] = None
    instantiatesUri: Uri | FHIRList[Uri] = None
    basedOn: Reference | FHIRList[Reference]
    replaces: Reference | FHIRList[Reference]
    requisition: Optional[Identifier]
    status: Optional[Code] = None
    intent: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    priority: Optional[Code] = None
    doNotPerform: Optional[Boolean] = None
    code: Optional[CodeableConcept]
    orderDetail: CodeableConcept | FHIRList[CodeableConcept]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    authoredOn: Optional[DateTime] = None
    requester: Optional[Reference]
    performerType: Optional[CodeableConcept]
    performer: Reference | FHIRList[Reference]
    locationCode: CodeableConcept | FHIRList[CodeableConcept]
    locationReference: Reference | FHIRList[Reference]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    insurance: Reference | FHIRList[Reference]
    supportingInfo: Reference | FHIRList[Reference]
    specimen: Reference | FHIRList[Reference]
    bodySite: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    patientInstruction: Optional[String] = None
    relevantHistory: Reference | FHIRList[Reference]


class Slot(FHIRResource):
    _resource_type = "Slot"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'serviceCategory', 'serviceType', 'specialty'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'serviceCategory': 'CodeableConcept', 'serviceType': 'CodeableConcept', 'specialty': 'CodeableConcept', 'appointmentType': 'CodeableConcept', 'schedule': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    serviceCategory: CodeableConcept | FHIRList[CodeableConcept]
    serviceType: CodeableConcept | FHIRList[CodeableConcept]
    specialty: CodeableConcept | FHIRList[CodeableConcept]
    appointmentType: Optional[CodeableConcept]
    schedule: Optional[Reference]
    status: Optional[Code] = None
    start: Optional[Instant] = None
    end: Optional[Instant] = None
    overbooked: Optional[Boolean] = None
    comment: Optional[String] = None


class Specimen(FHIRResource):
    _resource_type = "Specimen"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'parent', 'request', 'processing', 'container', 'condition', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'accessionIdentifier': 'Identifier', 'type': 'CodeableConcept', 'subject': 'Reference', 'parent': 'Reference', 'request': 'Reference', 'collection': 'BackboneElement', 'processing': 'BackboneElement', 'container': 'BackboneElement', 'condition': 'CodeableConcept', 'note': 'Annotation'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    accessionIdentifier: Optional[Identifier]
    status: Optional[Code] = None
    type: Optional[CodeableConcept]
    subject: Optional[Reference]
    receivedTime: Optional[DateTime] = None
    parent: Reference | FHIRList[Reference]
    request: Reference | FHIRList[Reference]
    collection: Optional[BackboneElement]
    processing: BackboneElement | FHIRList[BackboneElement]
    container: BackboneElement | FHIRList[BackboneElement]
    condition: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]


class SpecimenDefinition(FHIRResource):
    _resource_type = "SpecimenDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'patientPreparation', 'collection', 'typeTested'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'typeCollected': 'CodeableConcept', 'patientPreparation': 'CodeableConcept', 'collection': 'CodeableConcept', 'typeTested': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Identifier]
    typeCollected: Optional[CodeableConcept]
    patientPreparation: CodeableConcept | FHIRList[CodeableConcept]
    timeAspect: Optional[String] = None
    collection: CodeableConcept | FHIRList[CodeableConcept]
    typeTested: BackboneElement | FHIRList[BackboneElement]


class StructureDefinition(FHIRResource):
    _resource_type = "StructureDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'keyword', 'mapping', 'context', 'contextInvariant'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'keyword': 'Coding', 'mapping': 'BackboneElement', 'context': 'BackboneElement', 'snapshot': 'BackboneElement', 'differential': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    keyword: Coding | FHIRList[Coding]
    fhirVersion: Optional[Code] = None
    mapping: BackboneElement | FHIRList[BackboneElement]
    kind: Optional[Code] = None
    abstract: Optional[Boolean] = None
    context: BackboneElement | FHIRList[BackboneElement]
    contextInvariant: String | FHIRList[String] = None
    type: Optional[Uri] = None
    baseDefinition: Optional[Canonical] = None
    derivation: Optional[Code] = None
    snapshot: Optional[BackboneElement]
    differential: Optional[BackboneElement]


class StructureMap(FHIRResource):
    _resource_type = "StructureMap"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'structure', 'import_', 'group'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'structure': 'BackboneElement', 'group': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    structure: BackboneElement | FHIRList[BackboneElement]
    import_: Canonical | FHIRList[Canonical] = None
    group: BackboneElement | FHIRList[BackboneElement]


class Subscription(FHIRResource):
    _resource_type = "Subscription"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'contact': 'ContactPoint', 'channel': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    status: Optional[Code] = None
    contact: ContactPoint | FHIRList[ContactPoint]
    end: Optional[Instant] = None
    reason: Optional[String] = None
    criteria: Optional[String] = None
    error: Optional[String] = None
    channel: Optional[BackboneElement]


class Substance(FHIRResource):
    _resource_type = "Substance"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'instance', 'ingredient'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'instance': 'BackboneElement', 'ingredient': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    code: Optional[CodeableConcept]
    description: Optional[String] = None
    instance: BackboneElement | FHIRList[BackboneElement]
    ingredient: BackboneElement | FHIRList[BackboneElement]


class SubstanceNucleicAcid(FHIRResource):
    _resource_type = "SubstanceNucleicAcid"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'subunit'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'sequenceType': 'CodeableConcept', 'oligoNucleotideType': 'CodeableConcept', 'subunit': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequenceType: Optional[CodeableConcept]
    numberOfSubunits: Optional[Integer] = None
    areaOfHybridisation: Optional[String] = None
    oligoNucleotideType: Optional[CodeableConcept]
    subunit: BackboneElement | FHIRList[BackboneElement]


class SubstancePolymer(FHIRResource):
    _resource_type = "SubstancePolymer"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'copolymerConnectivity', 'modification', 'monomerSet', 'repeat'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'class_': 'CodeableConcept', 'geometry': 'CodeableConcept', 'copolymerConnectivity': 'CodeableConcept', 'monomerSet': 'BackboneElement', 'repeat': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    class_: Optional[CodeableConcept]
    geometry: Optional[CodeableConcept]
    copolymerConnectivity: CodeableConcept | FHIRList[CodeableConcept]
    modification: String | FHIRList[String] = None
    monomerSet: BackboneElement | FHIRList[BackboneElement]
    repeat: BackboneElement | FHIRList[BackboneElement]


class SubstanceProtein(FHIRResource):
    _resource_type = "SubstanceProtein"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'disulfideLinkage', 'subunit'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'sequenceType': 'CodeableConcept', 'subunit': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequenceType: Optional[CodeableConcept]
    numberOfSubunits: Optional[Integer] = None
    disulfideLinkage: String | FHIRList[String] = None
    subunit: BackboneElement | FHIRList[BackboneElement]


class SubstanceReferenceInformation(FHIRResource):
    _resource_type = "SubstanceReferenceInformation"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'gene', 'geneElement', 'classification', 'target'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'gene': 'BackboneElement', 'geneElement': 'BackboneElement', 'classification': 'BackboneElement', 'target': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    comment: Optional[String] = None
    gene: BackboneElement | FHIRList[BackboneElement]
    geneElement: BackboneElement | FHIRList[BackboneElement]
    classification: BackboneElement | FHIRList[BackboneElement]
    target: BackboneElement | FHIRList[BackboneElement]


class SubstanceSourceMaterial(FHIRResource):
    _resource_type = "SubstanceSourceMaterial"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'parentSubstanceId', 'parentSubstanceName', 'countryOfOrigin', 'geographicalLocation', 'fractionDescription', 'partDescription'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'sourceMaterialClass': 'CodeableConcept', 'sourceMaterialType': 'CodeableConcept', 'sourceMaterialState': 'CodeableConcept', 'organismId': 'Identifier', 'parentSubstanceId': 'Identifier', 'countryOfOrigin': 'CodeableConcept', 'developmentStage': 'CodeableConcept', 'fractionDescription': 'BackboneElement', 'organism': 'BackboneElement', 'partDescription': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sourceMaterialClass: Optional[CodeableConcept]
    sourceMaterialType: Optional[CodeableConcept]
    sourceMaterialState: Optional[CodeableConcept]
    organismId: Optional[Identifier]
    organismName: Optional[String] = None
    parentSubstanceId: Identifier | FHIRList[Identifier]
    parentSubstanceName: String | FHIRList[String] = None
    countryOfOrigin: CodeableConcept | FHIRList[CodeableConcept]
    geographicalLocation: String | FHIRList[String] = None
    developmentStage: Optional[CodeableConcept]
    fractionDescription: BackboneElement | FHIRList[BackboneElement]
    organism: Optional[BackboneElement]
    partDescription: BackboneElement | FHIRList[BackboneElement]


class SubstanceSpecification(FHIRResource):
    _resource_type = "SubstanceSpecification"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'source', 'moiety', 'property', 'code', 'name', 'molecularWeight', 'relationship'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'status': 'CodeableConcept', 'domain': 'CodeableConcept', 'source': 'Reference', 'moiety': 'BackboneElement', 'property': 'BackboneElement', 'referenceInformation': 'Reference', 'structure': 'BackboneElement', 'code': 'BackboneElement', 'name': 'BackboneElement', 'relationship': 'BackboneElement', 'nucleicAcid': 'Reference', 'polymer': 'Reference', 'protein': 'Reference', 'sourceMaterial': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Identifier]
    type: Optional[CodeableConcept]
    status: Optional[CodeableConcept]
    domain: Optional[CodeableConcept]
    description: Optional[String] = None
    source: Reference | FHIRList[Reference]
    comment: Optional[String] = None
    moiety: BackboneElement | FHIRList[BackboneElement]
    property: BackboneElement | FHIRList[BackboneElement]
    referenceInformation: Optional[Reference]
    structure: Optional[BackboneElement]
    code: BackboneElement | FHIRList[BackboneElement]
    name: BackboneElement | FHIRList[BackboneElement]
    molecularWeight: Any = None
    relationship: BackboneElement | FHIRList[BackboneElement]
    nucleicAcid: Optional[Reference]
    polymer: Optional[Reference]
    protein: Optional[Reference]
    sourceMaterial: Optional[Reference]


class SupplyDelivery(FHIRResource):
    _resource_type = "SupplyDelivery"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'receiver'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'patient': 'Reference', 'type': 'CodeableConcept', 'suppliedItem': 'BackboneElement', 'supplier': 'Reference', 'destination': 'Reference', 'receiver': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    patient: Optional[Reference]
    type: Optional[CodeableConcept]
    suppliedItem: Optional[BackboneElement]
    supplier: Optional[Reference]
    destination: Optional[Reference]
    receiver: Reference | FHIRList[Reference]


class SupplyRequest(FHIRResource):
    _resource_type = "SupplyRequest"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'parameter', 'supplier', 'reasonCode', 'reasonReference'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'category': 'CodeableConcept', 'quantity': 'Quantity', 'parameter': 'BackboneElement', 'requester': 'Reference', 'supplier': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'deliverFrom': 'Reference', 'deliverTo': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    category: Optional[CodeableConcept]
    priority: Optional[Code] = None
    quantity: Optional[Quantity]
    parameter: BackboneElement | FHIRList[BackboneElement]
    authoredOn: Optional[DateTime] = None
    requester: Optional[Reference]
    supplier: Reference | FHIRList[Reference]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    deliverFrom: Optional[Reference]
    deliverTo: Optional[Reference]


class Task(FHIRResource):
    _resource_type = "Task"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'performerType', 'insurance', 'note', 'relevantHistory', 'input', 'output'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'groupIdentifier': 'Identifier', 'partOf': 'Reference', 'statusReason': 'CodeableConcept', 'businessStatus': 'CodeableConcept', 'code': 'CodeableConcept', 'focus': 'Reference', 'for_': 'Reference', 'encounter': 'Reference', 'executionPeriod': 'Period', 'requester': 'Reference', 'performerType': 'CodeableConcept', 'owner': 'Reference', 'location': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'insurance': 'Reference', 'note': 'Annotation', 'relevantHistory': 'Reference', 'restriction': 'BackboneElement', 'input': 'BackboneElement', 'output': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    instantiatesCanonical: Optional[Canonical] = None
    instantiatesUri: Optional[Uri] = None
    basedOn: Reference | FHIRList[Reference]
    groupIdentifier: Optional[Identifier]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    statusReason: Optional[CodeableConcept]
    businessStatus: Optional[CodeableConcept]
    intent: Optional[Code] = None
    priority: Optional[Code] = None
    code: Optional[CodeableConcept]
    description: Optional[String] = None
    focus: Optional[Reference]
    for_: Optional[Reference]
    encounter: Optional[Reference]
    executionPeriod: Optional[Period]
    authoredOn: Optional[DateTime] = None
    lastModified: Optional[DateTime] = None
    requester: Optional[Reference]
    performerType: CodeableConcept | FHIRList[CodeableConcept]
    owner: Optional[Reference]
    location: Optional[Reference]
    reasonCode: Optional[CodeableConcept]
    reasonReference: Optional[Reference]
    insurance: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]
    relevantHistory: Reference | FHIRList[Reference]
    restriction: Optional[BackboneElement]
    input: BackboneElement | FHIRList[BackboneElement]
    output: BackboneElement | FHIRList[BackboneElement]


class TerminologyCapabilities(FHIRResource):
    _resource_type = "TerminologyCapabilities"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'codeSystem'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'software': 'BackboneElement', 'implementation': 'BackboneElement', 'codeSystem': 'BackboneElement', 'expansion': 'BackboneElement', 'validateCode': 'BackboneElement', 'translation': 'BackboneElement', 'closure': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    kind: Optional[Code] = None
    software: Optional[BackboneElement]
    implementation: Optional[BackboneElement]
    lockedDate: Optional[Boolean] = None
    codeSystem: BackboneElement | FHIRList[BackboneElement]
    expansion: Optional[BackboneElement]
    codeSearch: Optional[Code] = None
    validateCode: Optional[BackboneElement]
    translation: Optional[BackboneElement]
    closure: Optional[BackboneElement]


class TestReport(FHIRResource):
    _resource_type = "TestReport"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'participant', 'test'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'testScript': 'Reference', 'participant': 'BackboneElement', 'setup': 'BackboneElement', 'test': 'BackboneElement', 'teardown': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Identifier]
    name: Optional[String] = None
    status: Optional[Code] = None
    testScript: Optional[Reference]
    result: Optional[Code] = None
    score: Optional[Decimal] = None
    tester: Optional[String] = None
    issued: Optional[DateTime] = None
    participant: BackboneElement | FHIRList[BackboneElement]
    setup: Optional[BackboneElement]
    test: BackboneElement | FHIRList[BackboneElement]
    teardown: Optional[BackboneElement]


class TestScript(FHIRResource):
    _resource_type = "TestScript"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'origin', 'destination', 'fixture', 'profile', 'variable', 'test'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'origin': 'BackboneElement', 'destination': 'BackboneElement', 'metadata': 'BackboneElement', 'fixture': 'BackboneElement', 'profile': 'Reference', 'variable': 'BackboneElement', 'setup': 'BackboneElement', 'test': 'BackboneElement', 'teardown': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Optional[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    origin: BackboneElement | FHIRList[BackboneElement]
    destination: BackboneElement | FHIRList[BackboneElement]
    metadata: Optional[BackboneElement]
    fixture: BackboneElement | FHIRList[BackboneElement]
    profile: Reference | FHIRList[Reference]
    variable: BackboneElement | FHIRList[BackboneElement]
    setup: Optional[BackboneElement]
    test: BackboneElement | FHIRList[BackboneElement]
    teardown: Optional[BackboneElement]


class ValueSet(FHIRResource):
    _resource_type = "ValueSet"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'compose': 'BackboneElement', 'expansion': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    immutable: Optional[Boolean] = None
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    compose: Optional[BackboneElement]
    expansion: Optional[BackboneElement]


class VerificationResult(FHIRResource):
    _resource_type = "VerificationResult"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'target', 'targetLocation', 'validationProcess', 'primarySource', 'validator'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'target': 'Reference', 'need': 'CodeableConcept', 'validationType': 'CodeableConcept', 'validationProcess': 'CodeableConcept', 'frequency': 'Timing', 'failureAction': 'CodeableConcept', 'primarySource': 'BackboneElement', 'attestation': 'BackboneElement', 'validator': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    target: Reference | FHIRList[Reference]
    targetLocation: String | FHIRList[String] = None
    need: Optional[CodeableConcept]
    status: Optional[Code] = None
    statusDate: Optional[DateTime] = None
    validationType: Optional[CodeableConcept]
    validationProcess: CodeableConcept | FHIRList[CodeableConcept]
    frequency: Optional[Timing]
    lastPerformed: Optional[DateTime] = None
    nextScheduled: Optional[Date] = None
    failureAction: Optional[CodeableConcept]
    primarySource: BackboneElement | FHIRList[BackboneElement]
    attestation: Optional[BackboneElement]
    validator: BackboneElement | FHIRList[BackboneElement]


class VisionPrescription(FHIRResource):
    _resource_type = "VisionPrescription"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'lensSpecification'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'patient': 'Reference', 'encounter': 'Reference', 'prescriber': 'Reference', 'lensSpecification': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    status: Optional[Code] = None
    created: Optional[DateTime] = None
    patient: Optional[Reference]
    encounter: Optional[Reference]
    dateWritten: Optional[DateTime] = None
    prescriber: Optional[Reference]
    lensSpecification: BackboneElement | FHIRList[BackboneElement]


class actualgroup(FHIRResource):
    _resource_type = "actualgroup"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'member'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'code': 'CodeableConcept', 'managingEntity': 'Reference', 'characteristic': 'BackboneElement', 'member': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    active: Optional[Boolean] = None
    type: Optional[Code] = None
    actual: Optional[Boolean] = None
    code: Optional[CodeableConcept]
    name: Optional[String] = None
    quantity: Optional[UnsignedInt] = None
    managingEntity: Optional[Reference]
    characteristic: Optional[BackboneElement]
    member: BackboneElement | FHIRList[BackboneElement]


class bmi(FHIRResource):
    _resource_type = "bmi"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'BackboneElement', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: BackboneElement | FHIRList[BackboneElement]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: BackboneElement | FHIRList[BackboneElement]


class bodyheight(FHIRResource):
    _resource_type = "bodyheight"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'BackboneElement', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: BackboneElement | FHIRList[BackboneElement]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: BackboneElement | FHIRList[BackboneElement]


class bodytemp(FHIRResource):
    _resource_type = "bodytemp"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'BackboneElement', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: BackboneElement | FHIRList[BackboneElement]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: BackboneElement | FHIRList[BackboneElement]


class bodyweight(FHIRResource):
    _resource_type = "bodyweight"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'BackboneElement', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: BackboneElement | FHIRList[BackboneElement]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: BackboneElement | FHIRList[BackboneElement]


class bp(FHIRResource):
    _resource_type = "bp"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'BackboneElement', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'BackboneElement', 'component': 'BackboneElement', 'component': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: BackboneElement | FHIRList[BackboneElement]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: BackboneElement | FHIRList[BackboneElement]
    component: Optional[BackboneElement]
    component: Optional[BackboneElement]


class catalog(FHIRResource):
    _resource_type = "catalog"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'author', 'attester', 'relatesTo', 'event', 'section'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'category': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'author': 'Reference', 'attester': 'BackboneElement', 'custodian': 'Reference', 'relatesTo': 'BackboneElement', 'event': 'BackboneElement', 'section': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    extension: Optional[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Identifier]
    status: Optional[Code] = None
    type: Optional[CodeableConcept]
    category: Optional[CodeableConcept]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    date: Optional[DateTime] = None
    author: Reference | FHIRList[Reference]
    title: Optional[String] = None
    confidentiality: Optional[Code] = None
    attester: BackboneElement | FHIRList[BackboneElement]
    custodian: Optional[Reference]
    relatesTo: BackboneElement | FHIRList[BackboneElement]
    event: BackboneElement | FHIRList[BackboneElement]
    section: BackboneElement | FHIRList[BackboneElement]


class cdshooksguidanceresponse(FHIRResource):
    _resource_type = "cdshooksguidanceresponse"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'reasonCode', 'reasonReference', 'note', 'evaluationMessage', 'dataRequirement'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'extension': 'Extension', 'modifierExtension': 'Extension', 'requestIdentifier': 'Identifier', 'identifier': 'Identifier', 'subject': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'note': 'Annotation', 'evaluationMessage': 'Reference', 'outputParameters': 'Reference', 'result': 'Reference', 'dataRequirement': 'DataRequirement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    extension: Optional[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    requestIdentifier: Optional[Identifier]
    identifier: Optional[Identifier]
    status: Optional[Code] = None
    subject: Optional[Reference]
    encounter: Optional[Reference]
    occurrenceDateTime: Optional[DateTime] = None
    performer: Optional[Reference]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]
    evaluationMessage: Reference | FHIRList[Reference]
    outputParameters: Optional[Reference]
    result: Optional[Reference]
    dataRequirement: DataRequirement | FHIRList[DataRequirement]


class cdshooksrequestgroup(FHIRResource):
    _resource_type = "cdshooksrequestgroup"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'instantiatesCanonical', 'basedOn', 'replaces', 'reasonCode', 'reasonReference', 'note', 'action'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'replaces': 'Reference', 'groupIdentifier': 'Identifier', 'code': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'author': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'note': 'Annotation', 'action': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Identifier]
    instantiatesCanonical: Canonical | FHIRList[Canonical] = None
    instantiatesUri: Optional[Uri] = None
    basedOn: Reference | FHIRList[Reference]
    replaces: Reference | FHIRList[Reference]
    groupIdentifier: Optional[Identifier]
    status: Optional[Code] = None
    intent: Optional[Code] = None
    priority: Optional[Code] = None
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    authoredOn: Optional[DateTime] = None
    author: Optional[Reference]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]
    action: BackboneElement | FHIRList[BackboneElement]


class cdshooksserviceplandefinition(FHIRResource):
    _resource_type = "cdshooksserviceplandefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'library', 'goal', 'action'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'goal': 'BackboneElement', 'action': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    extension: Optional[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    type: Optional[CodeableConcept]
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    topic: CodeableConcept | FHIRList[CodeableConcept]
    author: ContactDetail | FHIRList[ContactDetail]
    editor: ContactDetail | FHIRList[ContactDetail]
    reviewer: ContactDetail | FHIRList[ContactDetail]
    endorser: ContactDetail | FHIRList[ContactDetail]
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact]
    library: Canonical | FHIRList[Canonical] = None
    goal: BackboneElement | FHIRList[BackboneElement]
    action: BackboneElement | FHIRList[BackboneElement]


class cholesterol(FHIRResource):
    _resource_type = "cholesterol"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'note', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'BackboneElement', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: Optional[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: Optional[BackboneElement]
    hasMember: Optional[Reference]
    derivedFrom: Optional[Reference]
    component: BackboneElement | FHIRList[BackboneElement]


class clinicaldocument(FHIRResource):
    _resource_type = "clinicaldocument"
    _list_fields = {'contained', 'extension', 'extension', 'modifierExtension', 'category', 'author', 'attester', 'relatesTo', 'event', 'section'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'category': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'author': 'Reference', 'attester': 'BackboneElement', 'custodian': 'Reference', 'relatesTo': 'BackboneElement', 'event': 'BackboneElement', 'section': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Identifier]
    status: Optional[Code] = None
    type: Optional[CodeableConcept]
    category: CodeableConcept | FHIRList[CodeableConcept]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    date: Optional[DateTime] = None
    author: Reference | FHIRList[Reference]
    title: Optional[String] = None
    confidentiality: Optional[Code] = None
    attester: BackboneElement | FHIRList[BackboneElement]
    custodian: Optional[Reference]
    relatesTo: BackboneElement | FHIRList[BackboneElement]
    event: BackboneElement | FHIRList[BackboneElement]
    section: BackboneElement | FHIRList[BackboneElement]


class computableplandefinition(FHIRResource):
    _resource_type = "computableplandefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'goal', 'action'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'goal': 'BackboneElement', 'action': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    type: Optional[CodeableConcept]
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    topic: CodeableConcept | FHIRList[CodeableConcept]
    author: ContactDetail | FHIRList[ContactDetail]
    editor: ContactDetail | FHIRList[ContactDetail]
    reviewer: ContactDetail | FHIRList[ContactDetail]
    endorser: ContactDetail | FHIRList[ContactDetail]
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact]
    library: Optional[Canonical] = None
    goal: BackboneElement | FHIRList[BackboneElement]
    action: BackboneElement | FHIRList[BackboneElement]


class cqllibrary(FHIRResource):
    _resource_type = "cqllibrary"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'parameter', 'dataRequirement', 'content'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'parameter': 'ParameterDefinition', 'dataRequirement': 'DataRequirement', 'content': 'Attachment'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    type: Optional[CodeableConcept]
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    topic: CodeableConcept | FHIRList[CodeableConcept]
    author: ContactDetail | FHIRList[ContactDetail]
    editor: ContactDetail | FHIRList[ContactDetail]
    reviewer: ContactDetail | FHIRList[ContactDetail]
    endorser: ContactDetail | FHIRList[ContactDetail]
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact]
    parameter: ParameterDefinition | FHIRList[ParameterDefinition]
    dataRequirement: DataRequirement | FHIRList[DataRequirement]
    content: Attachment | FHIRList[Attachment]


class devicemetricobservation(FHIRResource):
    _resource_type = "devicemetricobservation"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'note', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'BackboneElement', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: Optional[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: Optional[BackboneElement]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: BackboneElement | FHIRList[BackboneElement]


class groupdefinition(FHIRResource):
    _resource_type = "groupdefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'characteristic'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'code': 'CodeableConcept', 'managingEntity': 'Reference', 'characteristic': 'BackboneElement', 'member': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    active: Optional[Boolean] = None
    type: Optional[Code] = None
    actual: Optional[Boolean] = None
    code: Optional[CodeableConcept]
    name: Optional[String] = None
    quantity: Optional[UnsignedInt] = None
    managingEntity: Optional[Reference]
    characteristic: BackboneElement | FHIRList[BackboneElement]
    member: Optional[BackboneElement]


class hdlcholesterol(FHIRResource):
    _resource_type = "hdlcholesterol"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'note', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'BackboneElement', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: Optional[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: Optional[BackboneElement]
    hasMember: Optional[Reference]
    derivedFrom: Optional[Reference]
    component: BackboneElement | FHIRList[BackboneElement]


class headcircum(FHIRResource):
    _resource_type = "headcircum"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'BackboneElement', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: BackboneElement | FHIRList[BackboneElement]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: BackboneElement | FHIRList[BackboneElement]


class heartrate(FHIRResource):
    _resource_type = "heartrate"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'BackboneElement', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: BackboneElement | FHIRList[BackboneElement]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: BackboneElement | FHIRList[BackboneElement]


class hlaresult(FHIRResource):
    _resource_type = "hlaresult"
    _list_fields = {'contained', 'extension', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'category', 'performer', 'resultsInterpreter', 'specimen', 'result', 'imagingStudy', 'media', 'conclusionCode', 'presentedForm'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'extension': 'Extension', 'extension': 'Extension', 'extension': 'Extension', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'resultsInterpreter': 'Reference', 'specimen': 'Reference', 'result': 'Reference', 'imagingStudy': 'Reference', 'media': 'BackboneElement', 'conclusionCode': 'CodeableConcept', 'presentedForm': 'Attachment'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    extension: Optional[Extension]
    extension: Optional[Extension]
    extension: Extension | FHIRList[Extension]
    extension: Optional[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    resultsInterpreter: Reference | FHIRList[Reference]
    specimen: Reference | FHIRList[Reference]
    result: Reference | FHIRList[Reference]
    imagingStudy: Reference | FHIRList[Reference]
    media: BackboneElement | FHIRList[BackboneElement]
    conclusion: Optional[String] = None
    conclusionCode: CodeableConcept | FHIRList[CodeableConcept]
    presentedForm: Attachment | FHIRList[Attachment]


class ldlcholesterol(FHIRResource):
    _resource_type = "ldlcholesterol"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'note', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'BackboneElement', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: Optional[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: Optional[BackboneElement]
    hasMember: Optional[Reference]
    derivedFrom: Optional[Reference]
    component: BackboneElement | FHIRList[BackboneElement]


class lipidprofile(FHIRResource):
    _resource_type = "lipidprofile"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'category', 'performer', 'resultsInterpreter', 'specimen', 'result', 'imagingStudy', 'media', 'presentedForm'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'resultsInterpreter': 'Reference', 'specimen': 'Reference', 'result': 'Reference', 'result': 'Reference', 'result': 'Reference', 'result': 'Reference', 'result': 'Reference', 'imagingStudy': 'Reference', 'media': 'BackboneElement', 'conclusionCode': 'CodeableConcept', 'presentedForm': 'Attachment'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    resultsInterpreter: Reference | FHIRList[Reference]
    specimen: Reference | FHIRList[Reference]
    result: Reference | FHIRList[Reference]
    result: Optional[Reference]
    result: Optional[Reference]
    result: Optional[Reference]
    result: Optional[Reference]
    imagingStudy: Reference | FHIRList[Reference]
    media: BackboneElement | FHIRList[BackboneElement]
    conclusion: Optional[String] = None
    conclusionCode: Optional[CodeableConcept]
    presentedForm: Attachment | FHIRList[Attachment]


class oxygensat(FHIRResource):
    _resource_type = "oxygensat"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'BackboneElement', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: BackboneElement | FHIRList[BackboneElement]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: BackboneElement | FHIRList[BackboneElement]


class picoelement(FHIRResource):
    _resource_type = "picoelement"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'note', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'characteristic'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'note': 'Annotation', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'characteristic': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    shortTitle: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    note: Annotation | FHIRList[Annotation]
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    topic: CodeableConcept | FHIRList[CodeableConcept]
    author: ContactDetail | FHIRList[ContactDetail]
    editor: ContactDetail | FHIRList[ContactDetail]
    reviewer: ContactDetail | FHIRList[ContactDetail]
    endorser: ContactDetail | FHIRList[ContactDetail]
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact]
    type: Optional[Code] = None
    characteristic: BackboneElement | FHIRList[BackboneElement]


class resprate(FHIRResource):
    _resource_type = "resprate"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'BackboneElement', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: BackboneElement | FHIRList[BackboneElement]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: BackboneElement | FHIRList[BackboneElement]


class shareableactivitydefinition(FHIRResource):
    _resource_type = "shareableactivitydefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'library', 'participant', 'dosage', 'bodySite', 'specimenRequirement', 'observationRequirement', 'observationResultRequirement', 'dynamicValue'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'code': 'CodeableConcept', 'location': 'Reference', 'participant': 'BackboneElement', 'quantity': 'Quantity', 'dosage': 'Dosage', 'bodySite': 'CodeableConcept', 'specimenRequirement': 'Reference', 'observationRequirement': 'Reference', 'observationResultRequirement': 'Reference', 'dynamicValue': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    topic: CodeableConcept | FHIRList[CodeableConcept]
    author: ContactDetail | FHIRList[ContactDetail]
    editor: ContactDetail | FHIRList[ContactDetail]
    reviewer: ContactDetail | FHIRList[ContactDetail]
    endorser: ContactDetail | FHIRList[ContactDetail]
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact]
    library: Canonical | FHIRList[Canonical] = None
    kind: Optional[Code] = None
    profile: Optional[Canonical] = None
    code: Optional[CodeableConcept]
    intent: Optional[Code] = None
    priority: Optional[Code] = None
    doNotPerform: Optional[Boolean] = None
    location: Optional[Reference]
    participant: BackboneElement | FHIRList[BackboneElement]
    quantity: Optional[Quantity]
    dosage: Dosage | FHIRList[Dosage]
    bodySite: CodeableConcept | FHIRList[CodeableConcept]
    specimenRequirement: Reference | FHIRList[Reference]
    observationRequirement: Reference | FHIRList[Reference]
    observationResultRequirement: Reference | FHIRList[Reference]
    transform: Optional[Canonical] = None
    dynamicValue: BackboneElement | FHIRList[BackboneElement]


class shareablecodesystem(FHIRResource):
    _resource_type = "shareablecodesystem"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'filter', 'property', 'concept'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'filter': 'BackboneElement', 'property': 'BackboneElement', 'concept': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    caseSensitive: Optional[Boolean] = None
    valueSet: Optional[Canonical] = None
    hierarchyMeaning: Optional[Code] = None
    compositional: Optional[Boolean] = None
    versionNeeded: Optional[Boolean] = None
    content: Optional[Code] = None
    supplements: Optional[Canonical] = None
    count: Optional[UnsignedInt] = None
    filter: BackboneElement | FHIRList[BackboneElement]
    property: BackboneElement | FHIRList[BackboneElement]
    concept: BackboneElement | FHIRList[BackboneElement]


class shareablelibrary(FHIRResource):
    _resource_type = "shareablelibrary"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'parameter', 'dataRequirement', 'content'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'parameter': 'ParameterDefinition', 'dataRequirement': 'DataRequirement', 'content': 'Attachment'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    type: Optional[CodeableConcept]
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    topic: CodeableConcept | FHIRList[CodeableConcept]
    author: ContactDetail | FHIRList[ContactDetail]
    editor: ContactDetail | FHIRList[ContactDetail]
    reviewer: ContactDetail | FHIRList[ContactDetail]
    endorser: ContactDetail | FHIRList[ContactDetail]
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact]
    parameter: ParameterDefinition | FHIRList[ParameterDefinition]
    dataRequirement: DataRequirement | FHIRList[DataRequirement]
    content: Attachment | FHIRList[Attachment]


class shareablemeasure(FHIRResource):
    _resource_type = "shareablemeasure"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'library', 'type', 'definition', 'group', 'supplementalData'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'scoring': 'CodeableConcept', 'compositeScoring': 'CodeableConcept', 'type': 'CodeableConcept', 'improvementNotation': 'CodeableConcept', 'group': 'BackboneElement', 'supplementalData': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    topic: CodeableConcept | FHIRList[CodeableConcept]
    author: ContactDetail | FHIRList[ContactDetail]
    editor: ContactDetail | FHIRList[ContactDetail]
    reviewer: ContactDetail | FHIRList[ContactDetail]
    endorser: ContactDetail | FHIRList[ContactDetail]
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact]
    library: Canonical | FHIRList[Canonical] = None
    disclaimer: Optional[Markdown] = None
    scoring: Optional[CodeableConcept]
    compositeScoring: Optional[CodeableConcept]
    type: CodeableConcept | FHIRList[CodeableConcept]
    riskAdjustment: Optional[String] = None
    rateAggregation: Optional[String] = None
    rationale: Optional[Markdown] = None
    clinicalRecommendationStatement: Optional[Markdown] = None
    improvementNotation: Optional[CodeableConcept]
    definition: Markdown | FHIRList[Markdown] = None
    guidance: Optional[Markdown] = None
    group: BackboneElement | FHIRList[BackboneElement]
    supplementalData: BackboneElement | FHIRList[BackboneElement]


class shareableplandefinition(FHIRResource):
    _resource_type = "shareableplandefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'library', 'goal', 'action'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'goal': 'BackboneElement', 'action': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    type: Optional[CodeableConcept]
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    topic: CodeableConcept | FHIRList[CodeableConcept]
    author: ContactDetail | FHIRList[ContactDetail]
    editor: ContactDetail | FHIRList[ContactDetail]
    reviewer: ContactDetail | FHIRList[ContactDetail]
    endorser: ContactDetail | FHIRList[ContactDetail]
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact]
    library: Canonical | FHIRList[Canonical] = None
    goal: BackboneElement | FHIRList[BackboneElement]
    action: BackboneElement | FHIRList[BackboneElement]


class shareablevalueset(FHIRResource):
    _resource_type = "shareablevalueset"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'compose': 'BackboneElement', 'expansion': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    immutable: Optional[Boolean] = None
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    compose: Optional[BackboneElement]
    expansion: Optional[BackboneElement]


class synthesis(FHIRResource):
    _resource_type = "synthesis"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'note', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'exposureVariant', 'outcome'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'note': 'Annotation', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'exposureBackground': 'Reference', 'exposureVariant': 'Reference', 'outcome': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    shortTitle: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]
    description: Optional[Markdown] = None
    note: Annotation | FHIRList[Annotation]
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Optional[Period]
    topic: CodeableConcept | FHIRList[CodeableConcept]
    author: ContactDetail | FHIRList[ContactDetail]
    editor: ContactDetail | FHIRList[ContactDetail]
    reviewer: ContactDetail | FHIRList[ContactDetail]
    endorser: ContactDetail | FHIRList[ContactDetail]
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact]
    exposureBackground: Optional[Reference]
    exposureVariant: Reference | FHIRList[Reference]
    outcome: Reference | FHIRList[Reference]


class triglyceride(FHIRResource):
    _resource_type = "triglyceride"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'note', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'BackboneElement', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: Optional[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: Optional[BackboneElement]
    hasMember: Optional[Reference]
    derivedFrom: Optional[Reference]
    component: BackboneElement | FHIRList[BackboneElement]


class vitalsigns(FHIRResource):
    _resource_type = "vitalsigns"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'BackboneElement', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: BackboneElement | FHIRList[BackboneElement]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: BackboneElement | FHIRList[BackboneElement]


class vitalspanel(FHIRResource):
    _resource_type = "vitalspanel"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'BackboneElement', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'BackboneElement'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    partOf: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: BackboneElement | FHIRList[BackboneElement]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: BackboneElement | FHIRList[BackboneElement]
