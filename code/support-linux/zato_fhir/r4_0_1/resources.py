# Generated - do not edit
from __future__ import annotations

from typing import Any, Optional

from zato_fhir.base import FHIRResource, FHIRElement, FHIRList
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


class AccountCoverage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'coverage': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    coverage: Optional[Reference]
    priority: Optional[PositiveInt] = None


class AccountGuarantor(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'party': 'Reference', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    party: Optional[Reference]
    onHold: Optional[Boolean] = None
    period: Optional[Period]


class Account(FHIRResource):
    _resource_type = "Account"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'subject', 'coverage', 'guarantor'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'subject': 'Reference', 'servicePeriod': 'Period', 'coverage': 'AccountCoverage', 'owner': 'Reference', 'guarantor': 'AccountGuarantor', 'partOf': 'Reference'}

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
    type_: Optional[CodeableConcept]
    name: Optional[String] = None
    subject: Reference | FHIRList[Reference]
    servicePeriod: Optional[Period]
    coverage: AccountCoverage | FHIRList[AccountCoverage]
    owner: Optional[Reference]
    description: Optional[String] = None
    guarantor: AccountGuarantor | FHIRList[AccountGuarantor]
    partOf: Optional[Reference]


class ActivityDefinitionParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'role': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    role: Optional[CodeableConcept]


class ActivityDefinitionDynamicValue(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    path: Optional[String] = None
    expression: Optional[Expression]


class ActivityDefinition(FHIRResource):
    _resource_type = "ActivityDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'library', 'participant', 'dosage', 'bodySite', 'specimenRequirement', 'observationRequirement', 'observationResultRequirement', 'dynamicValue'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'subjectCodeableConcept': 'CodeableConcept', 'subjectReference': 'Reference', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'code': 'CodeableConcept', 'timingTiming': 'Timing', 'timingAge': 'Age', 'timingPeriod': 'Period', 'timingRange': 'Range', 'timingDuration': 'Duration', 'location': 'Reference', 'participant': 'ActivityDefinitionParticipant', 'productReference': 'Reference', 'productCodeableConcept': 'CodeableConcept', 'quantity': 'Quantity', 'dosage': 'Dosage', 'bodySite': 'CodeableConcept', 'specimenRequirement': 'Reference', 'observationRequirement': 'Reference', 'observationResultRequirement': 'Reference', 'dynamicValue': 'ActivityDefinitionDynamicValue'}
    _choice_fields = {'product': ['productReference', 'productCodeableConcept'], 'subject': ['subjectCodeableConcept', 'subjectReference'], 'timing': ['timingTiming', 'timingDateTime', 'timingAge', 'timingPeriod', 'timingRange', 'timingDuration']}

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
    subjectCodeableConcept: Optional[CodeableConcept]
    subjectReference: Optional[Reference]
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
    timingTiming: Optional[Timing]
    timingDateTime: Optional[DateTime] = None
    timingAge: Optional[Age]
    timingPeriod: Optional[Period]
    timingRange: Optional[Range]
    timingDuration: Optional[Duration]
    location: Optional[Reference]
    participant: ActivityDefinitionParticipant | FHIRList[ActivityDefinitionParticipant]
    productReference: Optional[Reference]
    productCodeableConcept: Optional[CodeableConcept]
    quantity: Optional[Quantity]
    dosage: Dosage | FHIRList[Dosage]
    bodySite: CodeableConcept | FHIRList[CodeableConcept]
    specimenRequirement: Reference | FHIRList[Reference]
    observationRequirement: Reference | FHIRList[Reference]
    observationResultRequirement: Reference | FHIRList[Reference]
    transform: Optional[Canonical] = None
    dynamicValue: ActivityDefinitionDynamicValue | FHIRList[ActivityDefinitionDynamicValue]


class AdverseEventSuspectEntity(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'causality'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'instance': 'Reference', 'causality': 'AdverseEventSuspectEntityCausality'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    instance: Optional[Reference]
    causality: AdverseEventSuspectEntityCausality | FHIRList[AdverseEventSuspectEntityCausality]


class AdverseEventSuspectEntityCausality(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'assessment': 'CodeableConcept', 'author': 'Reference', 'method': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    assessment: Optional[CodeableConcept]
    productRelatedness: Optional[String] = None
    author: Optional[Reference]
    method: Optional[CodeableConcept]


class AdverseEvent(FHIRResource):
    _resource_type = "AdverseEvent"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'category', 'resultingCondition', 'contributor', 'suspectEntity', 'subjectMedicalHistory', 'referenceDocument', 'study'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'category': 'CodeableConcept', 'event': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'resultingCondition': 'Reference', 'location': 'Reference', 'seriousness': 'CodeableConcept', 'severity': 'CodeableConcept', 'outcome': 'CodeableConcept', 'recorder': 'Reference', 'contributor': 'Reference', 'suspectEntity': 'AdverseEventSuspectEntity', 'subjectMedicalHistory': 'Reference', 'referenceDocument': 'Reference', 'study': 'Reference'}

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
    suspectEntity: AdverseEventSuspectEntity | FHIRList[AdverseEventSuspectEntity]
    subjectMedicalHistory: Reference | FHIRList[Reference]
    referenceDocument: Reference | FHIRList[Reference]
    study: Reference | FHIRList[Reference]


class AllergyIntoleranceReaction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'manifestation', 'note'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'substance': 'CodeableConcept', 'manifestation': 'CodeableConcept', 'exposureRoute': 'CodeableConcept', 'note': 'Annotation'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    substance: Optional[CodeableConcept]
    manifestation: CodeableConcept | FHIRList[CodeableConcept]
    description: Optional[String] = None
    onset: Optional[DateTime] = None
    severity: Optional[Code] = None
    exposureRoute: Optional[CodeableConcept]
    note: Annotation | FHIRList[Annotation]


class AllergyIntolerance(FHIRResource):
    _resource_type = "AllergyIntolerance"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'note', 'reaction'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'clinicalStatus': 'CodeableConcept', 'verificationStatus': 'CodeableConcept', 'code': 'CodeableConcept', 'patient': 'Reference', 'encounter': 'Reference', 'onsetAge': 'Age', 'onsetPeriod': 'Period', 'onsetRange': 'Range', 'recorder': 'Reference', 'asserter': 'Reference', 'note': 'Annotation', 'reaction': 'AllergyIntoleranceReaction'}
    _choice_fields = {'onset': ['onsetDateTime', 'onsetAge', 'onsetPeriod', 'onsetRange', 'onsetString']}

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
    type_: Optional[Code] = None
    category: Code | FHIRList[Code] = None
    criticality: Optional[Code] = None
    code: Optional[CodeableConcept]
    patient: Optional[Reference]
    encounter: Optional[Reference]
    onsetDateTime: Optional[DateTime] = None
    onsetAge: Optional[Age]
    onsetPeriod: Optional[Period]
    onsetRange: Optional[Range]
    onsetString: Optional[String] = None
    recordedDate: Optional[DateTime] = None
    recorder: Optional[Reference]
    asserter: Optional[Reference]
    lastOccurrence: Optional[DateTime] = None
    note: Annotation | FHIRList[Annotation]
    reaction: AllergyIntoleranceReaction | FHIRList[AllergyIntoleranceReaction]


class AppointmentParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'type_'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'actor': 'Reference', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: CodeableConcept | FHIRList[CodeableConcept]
    actor: Optional[Reference]
    required: Optional[Code] = None
    status: Optional[Code] = None
    period: Optional[Period]


class Appointment(FHIRResource):
    _resource_type = "Appointment"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'serviceCategory', 'serviceType', 'specialty', 'reasonCode', 'reasonReference', 'supportingInformation', 'slot', 'basedOn', 'participant', 'requestedPeriod'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'cancelationReason': 'CodeableConcept', 'serviceCategory': 'CodeableConcept', 'serviceType': 'CodeableConcept', 'specialty': 'CodeableConcept', 'appointmentType': 'CodeableConcept', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'supportingInformation': 'Reference', 'slot': 'Reference', 'basedOn': 'Reference', 'participant': 'AppointmentParticipant', 'requestedPeriod': 'Period'}

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
    participant: AppointmentParticipant | FHIRList[AppointmentParticipant]
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


class AuditEventAgent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'role', 'policy', 'purposeOfUse'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'role': 'CodeableConcept', 'who': 'Reference', 'location': 'Reference', 'media': 'Coding', 'network': 'AuditEventAgentNetwork', 'purposeOfUse': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    role: CodeableConcept | FHIRList[CodeableConcept]
    who: Optional[Reference]
    altId: Optional[String] = None
    name: Optional[String] = None
    requestor: Optional[Boolean] = None
    location: Optional[Reference]
    policy: Uri | FHIRList[Uri] = None
    media: Optional[Coding]
    network: Optional[AuditEventAgentNetwork]
    purposeOfUse: CodeableConcept | FHIRList[CodeableConcept]


class AuditEventAgentNetwork(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    address: Optional[String] = None
    type_: Optional[Code] = None


class AuditEventSource(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'type_'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'observer': 'Reference', 'type_': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    site: Optional[String] = None
    observer: Optional[Reference]
    type_: Coding | FHIRList[Coding]


class AuditEventEntity(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'securityLabel', 'detail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'what': 'Reference', 'type_': 'Coding', 'role': 'Coding', 'lifecycle': 'Coding', 'securityLabel': 'Coding', 'detail': 'AuditEventEntityDetail'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    what: Optional[Reference]
    type_: Optional[Coding]
    role: Optional[Coding]
    lifecycle: Optional[Coding]
    securityLabel: Coding | FHIRList[Coding]
    name: Optional[String] = None
    description: Optional[String] = None
    query: Optional[Base64Binary] = None
    detail: AuditEventEntityDetail | FHIRList[AuditEventEntityDetail]


class AuditEventEntityDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}
    _choice_fields = {'value': ['valueString', 'valueBase64Binary']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[String] = None
    valueString: Optional[String] = None
    valueBase64Binary: Optional[Base64Binary] = None


class AuditEvent(FHIRResource):
    _resource_type = "AuditEvent"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'subtype', 'purposeOfEvent', 'agent', 'entity'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'Coding', 'subtype': 'Coding', 'period': 'Period', 'purposeOfEvent': 'CodeableConcept', 'agent': 'AuditEventAgent', 'source': 'AuditEventSource', 'entity': 'AuditEventEntity'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Coding]
    subtype: Coding | FHIRList[Coding]
    action: Optional[Code] = None
    period: Optional[Period]
    recorded: Optional[Instant] = None
    outcome: Optional[Code] = None
    outcomeDesc: Optional[String] = None
    purposeOfEvent: CodeableConcept | FHIRList[CodeableConcept]
    agent: AuditEventAgent | FHIRList[AuditEventAgent]
    source: Optional[AuditEventSource]
    entity: AuditEventEntity | FHIRList[AuditEventEntity]


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


class BiologicallyDerivedProductCollection(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'collector': 'Reference', 'source': 'Reference', 'collectedPeriod': 'Period'}
    _choice_fields = {'collected': ['collectedDateTime', 'collectedPeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    collector: Optional[Reference]
    source: Optional[Reference]
    collectedDateTime: Optional[DateTime] = None
    collectedPeriod: Optional[Period]


class BiologicallyDerivedProductProcessing(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'procedure': 'CodeableConcept', 'additive': 'Reference', 'timePeriod': 'Period'}
    _choice_fields = {'time': ['timeDateTime', 'timePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    description: Optional[String] = None
    procedure: Optional[CodeableConcept]
    additive: Optional[Reference]
    timeDateTime: Optional[DateTime] = None
    timePeriod: Optional[Period]


class BiologicallyDerivedProductManipulation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'timePeriod': 'Period'}
    _choice_fields = {'time': ['timeDateTime', 'timePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    description: Optional[String] = None
    timeDateTime: Optional[DateTime] = None
    timePeriod: Optional[Period]


class BiologicallyDerivedProductStorage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'duration': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    description: Optional[String] = None
    temperature: Optional[Decimal] = None
    scale: Optional[Code] = None
    duration: Optional[Period]


class BiologicallyDerivedProduct(FHIRResource):
    _resource_type = "BiologicallyDerivedProduct"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'request', 'parent', 'processing', 'storage'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'productCode': 'CodeableConcept', 'request': 'Reference', 'parent': 'Reference', 'collection': 'BiologicallyDerivedProductCollection', 'processing': 'BiologicallyDerivedProductProcessing', 'manipulation': 'BiologicallyDerivedProductManipulation', 'storage': 'BiologicallyDerivedProductStorage'}

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
    collection: Optional[BiologicallyDerivedProductCollection]
    processing: BiologicallyDerivedProductProcessing | FHIRList[BiologicallyDerivedProductProcessing]
    manipulation: Optional[BiologicallyDerivedProductManipulation]
    storage: BiologicallyDerivedProductStorage | FHIRList[BiologicallyDerivedProductStorage]


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


class BundleLink(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    relation: Optional[String] = None
    url: Optional[Uri] = None


class BundleEntry(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'link'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'resource': 'Resource', 'search': 'BundleEntrySearch', 'request': 'BundleEntryRequest', 'response': 'BundleEntryResponse'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    link: Any = None
    fullUrl: Optional[Uri] = None
    resource: Optional[Resource]
    search: Optional[BundleEntrySearch]
    request: Optional[BundleEntryRequest]
    response: Optional[BundleEntryResponse]


class BundleEntrySearch(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    mode: Optional[Code] = None
    score: Optional[Decimal] = None


class BundleEntryRequest(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    method: Optional[Code] = None
    url: Optional[Uri] = None
    ifNoneMatch: Optional[String] = None
    ifModifiedSince: Optional[Instant] = None
    ifMatch: Optional[String] = None
    ifNoneExist: Optional[String] = None


class BundleEntryResponse(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'outcome': 'Resource'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    status: Optional[String] = None
    location: Optional[Uri] = None
    etag: Optional[String] = None
    lastModified: Optional[Instant] = None
    outcome: Optional[Resource]


class Bundle(FHIRResource):
    _resource_type = "Bundle"
    _list_fields = {'link', 'entry'}
    _field_types = {'meta': 'Meta', 'identifier': 'Identifier', 'link': 'BundleLink', 'entry': 'BundleEntry', 'signature': 'Signature'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    identifier: Optional[Identifier]
    type_: Optional[Code] = None
    timestamp: Optional[Instant] = None
    total: Optional[UnsignedInt] = None
    link: BundleLink | FHIRList[BundleLink]
    entry: BundleEntry | FHIRList[BundleEntry]
    signature: Optional[Signature]


class CapabilityStatementSoftware(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[String] = None
    version: Optional[String] = None
    releaseDate: Optional[DateTime] = None


class CapabilityStatementImplementation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'custodian': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    description: Optional[String] = None
    url: Optional[Url] = None
    custodian: Optional[Reference]


class CapabilityStatementRest(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'resource', 'interaction', 'searchParam', 'operation', 'compartment'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'security': 'CapabilityStatementRestSecurity', 'resource': 'CapabilityStatementRestResource', 'interaction': 'CapabilityStatementRestInteraction'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    mode: Optional[Code] = None
    documentation: Optional[Markdown] = None
    security: Optional[CapabilityStatementRestSecurity]
    resource: CapabilityStatementRestResource | FHIRList[CapabilityStatementRestResource]
    interaction: CapabilityStatementRestInteraction | FHIRList[CapabilityStatementRestInteraction]
    searchParam: Any = None
    operation: Any = None
    compartment: Canonical | FHIRList[Canonical] = None


class CapabilityStatementRestSecurity(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'service'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'service': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    cors: Optional[Boolean] = None
    service: CodeableConcept | FHIRList[CodeableConcept]
    description: Optional[Markdown] = None


class CapabilityStatementRestResource(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'supportedProfile', 'interaction', 'referencePolicy', 'searchInclude', 'searchRevInclude', 'searchParam', 'operation'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'interaction': 'CapabilityStatementRestResourceInteraction', 'searchParam': 'CapabilityStatementRestResourceSearchParam', 'operation': 'CapabilityStatementRestResourceOperation'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    profile: Optional[Canonical] = None
    supportedProfile: Canonical | FHIRList[Canonical] = None
    documentation: Optional[Markdown] = None
    interaction: CapabilityStatementRestResourceInteraction | FHIRList[CapabilityStatementRestResourceInteraction]
    versioning: Optional[Code] = None
    readHistory: Optional[Boolean] = None
    updateCreate: Optional[Boolean] = None
    conditionalCreate: Optional[Boolean] = None
    conditionalRead: Optional[Code] = None
    conditionalUpdate: Optional[Boolean] = None
    conditionalDelete: Optional[Code] = None
    referencePolicy: Code | FHIRList[Code] = None
    searchInclude: String | FHIRList[String] = None
    searchRevInclude: String | FHIRList[String] = None
    searchParam: CapabilityStatementRestResourceSearchParam | FHIRList[CapabilityStatementRestResourceSearchParam]
    operation: CapabilityStatementRestResourceOperation | FHIRList[CapabilityStatementRestResourceOperation]


class CapabilityStatementRestResourceInteraction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    documentation: Optional[Markdown] = None


class CapabilityStatementRestResourceSearchParam(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[String] = None
    definition: Optional[Canonical] = None
    type_: Optional[Code] = None
    documentation: Optional[Markdown] = None


class CapabilityStatementRestResourceOperation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[String] = None
    definition: Optional[Canonical] = None
    documentation: Optional[Markdown] = None


class CapabilityStatementRestInteraction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    documentation: Optional[Markdown] = None


class CapabilityStatementMessaging(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'endpoint', 'supportedMessage'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'endpoint': 'CapabilityStatementMessagingEndpoint', 'supportedMessage': 'CapabilityStatementMessagingSupportedMessage'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    endpoint: CapabilityStatementMessagingEndpoint | FHIRList[CapabilityStatementMessagingEndpoint]
    reliableCache: Optional[UnsignedInt] = None
    documentation: Optional[Markdown] = None
    supportedMessage: CapabilityStatementMessagingSupportedMessage | FHIRList[CapabilityStatementMessagingSupportedMessage]


class CapabilityStatementMessagingEndpoint(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'protocol': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    protocol: Optional[Coding]
    address: Optional[Url] = None


class CapabilityStatementMessagingSupportedMessage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    mode: Optional[Code] = None
    definition: Optional[Canonical] = None


class CapabilityStatementDocument(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    mode: Optional[Code] = None
    documentation: Optional[Markdown] = None
    profile: Optional[Canonical] = None


class CapabilityStatement(FHIRResource):
    _resource_type = "CapabilityStatement"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'instantiates', 'imports', 'format', 'patchFormat', 'implementationGuide', 'rest', 'messaging', 'document'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'software': 'CapabilityStatementSoftware', 'implementation': 'CapabilityStatementImplementation', 'rest': 'CapabilityStatementRest', 'messaging': 'CapabilityStatementMessaging', 'document': 'CapabilityStatementDocument'}

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
    software: Optional[CapabilityStatementSoftware]
    implementation: Optional[CapabilityStatementImplementation]
    fhirVersion: Optional[Code] = None
    format: Code | FHIRList[Code] = None
    patchFormat: Code | FHIRList[Code] = None
    implementationGuide: Canonical | FHIRList[Canonical] = None
    rest: CapabilityStatementRest | FHIRList[CapabilityStatementRest]
    messaging: CapabilityStatementMessaging | FHIRList[CapabilityStatementMessaging]
    document: CapabilityStatementDocument | FHIRList[CapabilityStatementDocument]


class CarePlanActivity(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'outcomeCodeableConcept', 'outcomeReference', 'progress'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'outcomeCodeableConcept': 'CodeableConcept', 'outcomeReference': 'Reference', 'progress': 'Annotation', 'reference': 'Reference', 'detail': 'CarePlanActivityDetail'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    outcomeCodeableConcept: CodeableConcept | FHIRList[CodeableConcept]
    outcomeReference: Reference | FHIRList[Reference]
    progress: Annotation | FHIRList[Annotation]
    reference: Optional[Reference]
    detail: Optional[CarePlanActivityDetail]


class CarePlanActivityDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'instantiatesCanonical', 'instantiatesUri', 'reasonCode', 'reasonReference', 'goal', 'performer'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'goal': 'Reference', 'statusReason': 'CodeableConcept', 'scheduledTiming': 'Timing', 'scheduledPeriod': 'Period', 'location': 'Reference', 'performer': 'Reference', 'productCodeableConcept': 'CodeableConcept', 'productReference': 'Reference', 'dailyAmount': 'Quantity', 'quantity': 'Quantity'}
    _choice_fields = {'product': ['productCodeableConcept', 'productReference'], 'scheduled': ['scheduledTiming', 'scheduledPeriod', 'scheduledString']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    kind: Optional[Code] = None
    instantiatesCanonical: Canonical | FHIRList[Canonical] = None
    instantiatesUri: Uri | FHIRList[Uri] = None
    code: Optional[CodeableConcept]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    goal: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    statusReason: Optional[CodeableConcept]
    doNotPerform: Optional[Boolean] = None
    scheduledTiming: Optional[Timing]
    scheduledPeriod: Optional[Period]
    scheduledString: Optional[String] = None
    location: Optional[Reference]
    performer: Reference | FHIRList[Reference]
    productCodeableConcept: Optional[CodeableConcept]
    productReference: Optional[Reference]
    dailyAmount: Optional[Quantity]
    quantity: Optional[Quantity]
    description: Optional[String] = None


class CarePlan(FHIRResource):
    _resource_type = "CarePlan"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'instantiatesCanonical', 'instantiatesUri', 'basedOn', 'replaces', 'partOf', 'category', 'contributor', 'careTeam', 'addresses', 'supportingInfo', 'goal', 'activity', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'replaces': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'period': 'Period', 'author': 'Reference', 'contributor': 'Reference', 'careTeam': 'Reference', 'addresses': 'Reference', 'supportingInfo': 'Reference', 'goal': 'Reference', 'activity': 'CarePlanActivity', 'note': 'Annotation'}

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
    activity: CarePlanActivity | FHIRList[CarePlanActivity]
    note: Annotation | FHIRList[Annotation]


class CareTeamParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'role'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'role': 'CodeableConcept', 'member': 'Reference', 'onBehalfOf': 'Reference', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    role: CodeableConcept | FHIRList[CodeableConcept]
    member: Optional[Reference]
    onBehalfOf: Optional[Reference]
    period: Optional[Period]


class CareTeam(FHIRResource):
    _resource_type = "CareTeam"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'participant', 'reasonCode', 'reasonReference', 'managingOrganization', 'telecom', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'category': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'period': 'Period', 'participant': 'CareTeamParticipant', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'managingOrganization': 'Reference', 'telecom': 'ContactPoint', 'note': 'Annotation'}

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
    participant: CareTeamParticipant | FHIRList[CareTeamParticipant]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    managingOrganization: Reference | FHIRList[Reference]
    telecom: ContactPoint | FHIRList[ContactPoint]
    note: Annotation | FHIRList[Annotation]


class CatalogEntryRelatedEntry(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'item': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    relationtype: Optional[Code] = None
    item: Optional[Reference]


class CatalogEntry(FHIRResource):
    _resource_type = "CatalogEntry"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'additionalIdentifier', 'classification', 'additionalCharacteristic', 'additionalClassification', 'relatedEntry'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'referencedItem': 'Reference', 'additionalIdentifier': 'Identifier', 'classification': 'CodeableConcept', 'validityPeriod': 'Period', 'additionalCharacteristic': 'CodeableConcept', 'additionalClassification': 'CodeableConcept', 'relatedEntry': 'CatalogEntryRelatedEntry'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    type_: Optional[CodeableConcept]
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
    relatedEntry: CatalogEntryRelatedEntry | FHIRList[CatalogEntryRelatedEntry]


class ChargeItemPerformer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'function': 'CodeableConcept', 'actor': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    function: Optional[CodeableConcept]
    actor: Optional[Reference]


class ChargeItem(FHIRResource):
    _resource_type = "ChargeItem"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'definitionUri', 'definitionCanonical', 'partOf', 'performer', 'bodysite', 'reason', 'service', 'account', 'note', 'supportingInformation'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'partOf': 'Reference', 'code': 'CodeableConcept', 'subject': 'Reference', 'context': 'Reference', 'occurrencePeriod': 'Period', 'occurrenceTiming': 'Timing', 'performer': 'ChargeItemPerformer', 'performingOrganization': 'Reference', 'requestingOrganization': 'Reference', 'costCenter': 'Reference', 'quantity': 'Quantity', 'bodysite': 'CodeableConcept', 'priceOverride': 'Money', 'enterer': 'Reference', 'reason': 'CodeableConcept', 'service': 'Reference', 'productReference': 'Reference', 'productCodeableConcept': 'CodeableConcept', 'account': 'Reference', 'note': 'Annotation', 'supportingInformation': 'Reference'}
    _choice_fields = {'occurrence': ['occurrenceDateTime', 'occurrencePeriod', 'occurrenceTiming'], 'product': ['productReference', 'productCodeableConcept']}

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
    occurrenceDateTime: Optional[DateTime] = None
    occurrencePeriod: Optional[Period]
    occurrenceTiming: Optional[Timing]
    performer: ChargeItemPerformer | FHIRList[ChargeItemPerformer]
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
    productReference: Optional[Reference]
    productCodeableConcept: Optional[CodeableConcept]
    account: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]
    supportingInformation: Reference | FHIRList[Reference]


class ChargeItemDefinitionApplicability(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    description: Optional[String] = None
    language: Optional[String] = None
    expression: Optional[String] = None


class ChargeItemDefinitionPropertyGroup(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'applicability', 'priceComponent'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'priceComponent': 'ChargeItemDefinitionPropertyGroupPriceComponent'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    applicability: Any = None
    priceComponent: ChargeItemDefinitionPropertyGroupPriceComponent | FHIRList[ChargeItemDefinitionPropertyGroupPriceComponent]


class ChargeItemDefinitionPropertyGroupPriceComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'amount': 'Money'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    code: Optional[CodeableConcept]
    factor: Optional[Decimal] = None
    amount: Optional[Money]


class ChargeItemDefinition(FHIRResource):
    _resource_type = "ChargeItemDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'derivedFromUri', 'partOf', 'replaces', 'contact', 'useContext', 'jurisdiction', 'instance', 'applicability', 'propertyGroup'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'code': 'CodeableConcept', 'instance': 'Reference', 'applicability': 'ChargeItemDefinitionApplicability', 'propertyGroup': 'ChargeItemDefinitionPropertyGroup'}

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
    applicability: ChargeItemDefinitionApplicability | FHIRList[ChargeItemDefinitionApplicability]
    propertyGroup: ChargeItemDefinitionPropertyGroup | FHIRList[ChargeItemDefinitionPropertyGroup]


class ClaimRelated(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'claim': 'Reference', 'relationship': 'CodeableConcept', 'reference': 'Identifier'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    claim: Optional[Reference]
    relationship: Optional[CodeableConcept]
    reference: Optional[Identifier]


class ClaimPayee(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'party': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    party: Optional[Reference]


class ClaimCareTeam(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'provider': 'Reference', 'role': 'CodeableConcept', 'qualification': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequence: Optional[PositiveInt] = None
    provider: Optional[Reference]
    responsible: Optional[Boolean] = None
    role: Optional[CodeableConcept]
    qualification: Optional[CodeableConcept]


class ClaimSupportingInfo(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'timingPeriod': 'Period', 'valueQuantity': 'Quantity', 'valueAttachment': 'Attachment', 'valueReference': 'Reference', 'reason': 'CodeableConcept'}
    _choice_fields = {'timing': ['timingDate', 'timingPeriod'], 'value': ['valueBoolean', 'valueString', 'valueQuantity', 'valueAttachment', 'valueReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequence: Optional[PositiveInt] = None
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    timingDate: Optional[Date] = None
    timingPeriod: Optional[Period]
    valueBoolean: Optional[Boolean] = None
    valueString: Optional[String] = None
    valueQuantity: Optional[Quantity]
    valueAttachment: Optional[Attachment]
    valueReference: Optional[Reference]
    reason: Optional[CodeableConcept]


class ClaimDiagnosis(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'type_'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'diagnosisCodeableConcept': 'CodeableConcept', 'diagnosisReference': 'Reference', 'type_': 'CodeableConcept', 'onAdmission': 'CodeableConcept', 'packageCode': 'CodeableConcept'}
    _choice_fields = {'diagnosis': ['diagnosisCodeableConcept', 'diagnosisReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequence: Optional[PositiveInt] = None
    diagnosisCodeableConcept: Optional[CodeableConcept]
    diagnosisReference: Optional[Reference]
    type_: CodeableConcept | FHIRList[CodeableConcept]
    onAdmission: Optional[CodeableConcept]
    packageCode: Optional[CodeableConcept]


class ClaimProcedure(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'type_', 'udi'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'procedureCodeableConcept': 'CodeableConcept', 'procedureReference': 'Reference', 'udi': 'Reference'}
    _choice_fields = {'procedure': ['procedureCodeableConcept', 'procedureReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequence: Optional[PositiveInt] = None
    type_: CodeableConcept | FHIRList[CodeableConcept]
    date: Optional[DateTime] = None
    procedureCodeableConcept: Optional[CodeableConcept]
    procedureReference: Optional[Reference]
    udi: Reference | FHIRList[Reference]


class ClaimInsurance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'preAuthRef'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'coverage': 'Reference', 'claimResponse': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequence: Optional[PositiveInt] = None
    focal: Optional[Boolean] = None
    identifier: Optional[Identifier]
    coverage: Optional[Reference]
    businessArrangement: Optional[String] = None
    preAuthRef: String | FHIRList[String] = None
    claimResponse: Optional[Reference]


class ClaimAccident(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'locationAddress': 'Address', 'locationReference': 'Reference'}
    _choice_fields = {'location': ['locationAddress', 'locationReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    date: Optional[Date] = None
    type_: Optional[CodeableConcept]
    locationAddress: Optional[Address]
    locationReference: Optional[Reference]


class ClaimItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'careTeamSequence', 'diagnosisSequence', 'procedureSequence', 'informationSequence', 'modifier', 'programCode', 'udi', 'subSite', 'encounter', 'detail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'revenue': 'CodeableConcept', 'category': 'CodeableConcept', 'productOrService': 'CodeableConcept', 'modifier': 'CodeableConcept', 'programCode': 'CodeableConcept', 'servicedPeriod': 'Period', 'locationCodeableConcept': 'CodeableConcept', 'locationAddress': 'Address', 'locationReference': 'Reference', 'quantity': 'Quantity', 'unitPrice': 'Money', 'net': 'Money', 'udi': 'Reference', 'bodySite': 'CodeableConcept', 'subSite': 'CodeableConcept', 'encounter': 'Reference', 'detail': 'ClaimItemDetail'}
    _choice_fields = {'location': ['locationCodeableConcept', 'locationAddress', 'locationReference'], 'serviced': ['servicedDate', 'servicedPeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequence: Optional[PositiveInt] = None
    careTeamSequence: PositiveInt | FHIRList[PositiveInt] = None
    diagnosisSequence: PositiveInt | FHIRList[PositiveInt] = None
    procedureSequence: PositiveInt | FHIRList[PositiveInt] = None
    informationSequence: PositiveInt | FHIRList[PositiveInt] = None
    revenue: Optional[CodeableConcept]
    category: Optional[CodeableConcept]
    productOrService: Optional[CodeableConcept]
    modifier: CodeableConcept | FHIRList[CodeableConcept]
    programCode: CodeableConcept | FHIRList[CodeableConcept]
    servicedDate: Optional[Date] = None
    servicedPeriod: Optional[Period]
    locationCodeableConcept: Optional[CodeableConcept]
    locationAddress: Optional[Address]
    locationReference: Optional[Reference]
    quantity: Optional[Quantity]
    unitPrice: Optional[Money]
    factor: Optional[Decimal] = None
    net: Optional[Money]
    udi: Reference | FHIRList[Reference]
    bodySite: Optional[CodeableConcept]
    subSite: CodeableConcept | FHIRList[CodeableConcept]
    encounter: Reference | FHIRList[Reference]
    detail: ClaimItemDetail | FHIRList[ClaimItemDetail]


class ClaimItemDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'modifier', 'programCode', 'udi', 'subDetail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'revenue': 'CodeableConcept', 'category': 'CodeableConcept', 'productOrService': 'CodeableConcept', 'modifier': 'CodeableConcept', 'programCode': 'CodeableConcept', 'quantity': 'Quantity', 'unitPrice': 'Money', 'net': 'Money', 'udi': 'Reference', 'subDetail': 'ClaimItemDetailSubDetail'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequence: Optional[PositiveInt] = None
    revenue: Optional[CodeableConcept]
    category: Optional[CodeableConcept]
    productOrService: Optional[CodeableConcept]
    modifier: CodeableConcept | FHIRList[CodeableConcept]
    programCode: CodeableConcept | FHIRList[CodeableConcept]
    quantity: Optional[Quantity]
    unitPrice: Optional[Money]
    factor: Optional[Decimal] = None
    net: Optional[Money]
    udi: Reference | FHIRList[Reference]
    subDetail: ClaimItemDetailSubDetail | FHIRList[ClaimItemDetailSubDetail]


class ClaimItemDetailSubDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'modifier', 'programCode', 'udi'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'revenue': 'CodeableConcept', 'category': 'CodeableConcept', 'productOrService': 'CodeableConcept', 'modifier': 'CodeableConcept', 'programCode': 'CodeableConcept', 'quantity': 'Quantity', 'unitPrice': 'Money', 'net': 'Money', 'udi': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequence: Optional[PositiveInt] = None
    revenue: Optional[CodeableConcept]
    category: Optional[CodeableConcept]
    productOrService: Optional[CodeableConcept]
    modifier: CodeableConcept | FHIRList[CodeableConcept]
    programCode: CodeableConcept | FHIRList[CodeableConcept]
    quantity: Optional[Quantity]
    unitPrice: Optional[Money]
    factor: Optional[Decimal] = None
    net: Optional[Money]
    udi: Reference | FHIRList[Reference]


class Claim(FHIRResource):
    _resource_type = "Claim"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'related', 'careTeam', 'supportingInfo', 'diagnosis', 'procedure', 'insurance', 'item'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'subType': 'CodeableConcept', 'patient': 'Reference', 'billablePeriod': 'Period', 'enterer': 'Reference', 'insurer': 'Reference', 'provider': 'Reference', 'priority': 'CodeableConcept', 'fundsReserve': 'CodeableConcept', 'related': 'ClaimRelated', 'prescription': 'Reference', 'originalPrescription': 'Reference', 'payee': 'ClaimPayee', 'referral': 'Reference', 'facility': 'Reference', 'careTeam': 'ClaimCareTeam', 'supportingInfo': 'ClaimSupportingInfo', 'diagnosis': 'ClaimDiagnosis', 'procedure': 'ClaimProcedure', 'insurance': 'ClaimInsurance', 'accident': 'ClaimAccident', 'item': 'ClaimItem', 'total': 'Money'}

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
    type_: Optional[CodeableConcept]
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
    related: ClaimRelated | FHIRList[ClaimRelated]
    prescription: Optional[Reference]
    originalPrescription: Optional[Reference]
    payee: Optional[ClaimPayee]
    referral: Optional[Reference]
    facility: Optional[Reference]
    careTeam: ClaimCareTeam | FHIRList[ClaimCareTeam]
    supportingInfo: ClaimSupportingInfo | FHIRList[ClaimSupportingInfo]
    diagnosis: ClaimDiagnosis | FHIRList[ClaimDiagnosis]
    procedure: ClaimProcedure | FHIRList[ClaimProcedure]
    insurance: ClaimInsurance | FHIRList[ClaimInsurance]
    accident: Optional[ClaimAccident]
    item: ClaimItem | FHIRList[ClaimItem]
    total: Optional[Money]


class ClaimResponseItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'noteNumber', 'adjudication', 'detail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'adjudication': 'ClaimResponseItemAdjudication', 'detail': 'ClaimResponseItemDetail'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    itemSequence: Optional[PositiveInt] = None
    noteNumber: PositiveInt | FHIRList[PositiveInt] = None
    adjudication: ClaimResponseItemAdjudication | FHIRList[ClaimResponseItemAdjudication]
    detail: ClaimResponseItemDetail | FHIRList[ClaimResponseItemDetail]


class ClaimResponseItemAdjudication(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'category': 'CodeableConcept', 'reason': 'CodeableConcept', 'amount': 'Money'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    category: Optional[CodeableConcept]
    reason: Optional[CodeableConcept]
    amount: Optional[Money]
    value: Optional[Decimal] = None


class ClaimResponseItemDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'noteNumber', 'adjudication', 'subDetail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'subDetail': 'ClaimResponseItemDetailSubDetail'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    detailSequence: Optional[PositiveInt] = None
    noteNumber: PositiveInt | FHIRList[PositiveInt] = None
    adjudication: Any = None
    subDetail: ClaimResponseItemDetailSubDetail | FHIRList[ClaimResponseItemDetailSubDetail]


class ClaimResponseItemDetailSubDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'noteNumber', 'adjudication'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    subDetailSequence: Optional[PositiveInt] = None
    noteNumber: PositiveInt | FHIRList[PositiveInt] = None
    adjudication: Any = None


class ClaimResponseAddItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'itemSequence', 'detailSequence', 'subdetailSequence', 'provider', 'modifier', 'programCode', 'subSite', 'noteNumber', 'adjudication', 'detail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'provider': 'Reference', 'productOrService': 'CodeableConcept', 'modifier': 'CodeableConcept', 'programCode': 'CodeableConcept', 'servicedPeriod': 'Period', 'locationCodeableConcept': 'CodeableConcept', 'locationAddress': 'Address', 'locationReference': 'Reference', 'quantity': 'Quantity', 'unitPrice': 'Money', 'net': 'Money', 'bodySite': 'CodeableConcept', 'subSite': 'CodeableConcept', 'detail': 'ClaimResponseAddItemDetail'}
    _choice_fields = {'location': ['locationCodeableConcept', 'locationAddress', 'locationReference'], 'serviced': ['servicedDate', 'servicedPeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    itemSequence: PositiveInt | FHIRList[PositiveInt] = None
    detailSequence: PositiveInt | FHIRList[PositiveInt] = None
    subdetailSequence: PositiveInt | FHIRList[PositiveInt] = None
    provider: Reference | FHIRList[Reference]
    productOrService: Optional[CodeableConcept]
    modifier: CodeableConcept | FHIRList[CodeableConcept]
    programCode: CodeableConcept | FHIRList[CodeableConcept]
    servicedDate: Optional[Date] = None
    servicedPeriod: Optional[Period]
    locationCodeableConcept: Optional[CodeableConcept]
    locationAddress: Optional[Address]
    locationReference: Optional[Reference]
    quantity: Optional[Quantity]
    unitPrice: Optional[Money]
    factor: Optional[Decimal] = None
    net: Optional[Money]
    bodySite: Optional[CodeableConcept]
    subSite: CodeableConcept | FHIRList[CodeableConcept]
    noteNumber: PositiveInt | FHIRList[PositiveInt] = None
    adjudication: Any = None
    detail: ClaimResponseAddItemDetail | FHIRList[ClaimResponseAddItemDetail]


class ClaimResponseAddItemDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'modifier', 'noteNumber', 'adjudication', 'subDetail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'productOrService': 'CodeableConcept', 'modifier': 'CodeableConcept', 'quantity': 'Quantity', 'unitPrice': 'Money', 'net': 'Money', 'subDetail': 'ClaimResponseAddItemDetailSubDetail'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    productOrService: Optional[CodeableConcept]
    modifier: CodeableConcept | FHIRList[CodeableConcept]
    quantity: Optional[Quantity]
    unitPrice: Optional[Money]
    factor: Optional[Decimal] = None
    net: Optional[Money]
    noteNumber: PositiveInt | FHIRList[PositiveInt] = None
    adjudication: Any = None
    subDetail: ClaimResponseAddItemDetailSubDetail | FHIRList[ClaimResponseAddItemDetailSubDetail]


class ClaimResponseAddItemDetailSubDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'modifier', 'noteNumber', 'adjudication'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'productOrService': 'CodeableConcept', 'modifier': 'CodeableConcept', 'quantity': 'Quantity', 'unitPrice': 'Money', 'net': 'Money'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    productOrService: Optional[CodeableConcept]
    modifier: CodeableConcept | FHIRList[CodeableConcept]
    quantity: Optional[Quantity]
    unitPrice: Optional[Money]
    factor: Optional[Decimal] = None
    net: Optional[Money]
    noteNumber: PositiveInt | FHIRList[PositiveInt] = None
    adjudication: Any = None


class ClaimResponseTotal(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'category': 'CodeableConcept', 'amount': 'Money'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    category: Optional[CodeableConcept]
    amount: Optional[Money]


class ClaimResponsePayment(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'adjustment': 'Money', 'adjustmentReason': 'CodeableConcept', 'amount': 'Money', 'identifier': 'Identifier'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    adjustment: Optional[Money]
    adjustmentReason: Optional[CodeableConcept]
    date: Optional[Date] = None
    amount: Optional[Money]
    identifier: Optional[Identifier]


class ClaimResponseProcessNote(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'language': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    number: Optional[PositiveInt] = None
    type_: Optional[Code] = None
    text: Optional[String] = None
    language: Optional[CodeableConcept]


class ClaimResponseInsurance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'coverage': 'Reference', 'claimResponse': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequence: Optional[PositiveInt] = None
    focal: Optional[Boolean] = None
    coverage: Optional[Reference]
    businessArrangement: Optional[String] = None
    claimResponse: Optional[Reference]


class ClaimResponseError(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    itemSequence: Optional[PositiveInt] = None
    detailSequence: Optional[PositiveInt] = None
    subDetailSequence: Optional[PositiveInt] = None
    code: Optional[CodeableConcept]


class ClaimResponse(FHIRResource):
    _resource_type = "ClaimResponse"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'item', 'addItem', 'adjudication', 'total', 'processNote', 'communicationRequest', 'insurance', 'error'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'subType': 'CodeableConcept', 'patient': 'Reference', 'insurer': 'Reference', 'requestor': 'Reference', 'request': 'Reference', 'preAuthPeriod': 'Period', 'payeeType': 'CodeableConcept', 'item': 'ClaimResponseItem', 'addItem': 'ClaimResponseAddItem', 'total': 'ClaimResponseTotal', 'payment': 'ClaimResponsePayment', 'fundsReserve': 'CodeableConcept', 'formCode': 'CodeableConcept', 'form': 'Attachment', 'processNote': 'ClaimResponseProcessNote', 'communicationRequest': 'Reference', 'insurance': 'ClaimResponseInsurance', 'error': 'ClaimResponseError'}

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
    type_: Optional[CodeableConcept]
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
    item: ClaimResponseItem | FHIRList[ClaimResponseItem]
    addItem: ClaimResponseAddItem | FHIRList[ClaimResponseAddItem]
    adjudication: Any = None
    total: ClaimResponseTotal | FHIRList[ClaimResponseTotal]
    payment: Optional[ClaimResponsePayment]
    fundsReserve: Optional[CodeableConcept]
    formCode: Optional[CodeableConcept]
    form: Optional[Attachment]
    processNote: ClaimResponseProcessNote | FHIRList[ClaimResponseProcessNote]
    communicationRequest: Reference | FHIRList[Reference]
    insurance: ClaimResponseInsurance | FHIRList[ClaimResponseInsurance]
    error: ClaimResponseError | FHIRList[ClaimResponseError]


class ClinicalImpressionInvestigation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'item'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'item': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    item: Reference | FHIRList[Reference]


class ClinicalImpressionFinding(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'itemCodeableConcept': 'CodeableConcept', 'itemReference': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    itemCodeableConcept: Optional[CodeableConcept]
    itemReference: Optional[Reference]
    basis: Optional[String] = None


class ClinicalImpression(FHIRResource):
    _resource_type = "ClinicalImpression"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'problem', 'investigation', 'protocol', 'finding', 'prognosisCodeableConcept', 'prognosisReference', 'supportingInfo', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'statusReason': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'effectivePeriod': 'Period', 'assessor': 'Reference', 'previous': 'Reference', 'problem': 'Reference', 'investigation': 'ClinicalImpressionInvestigation', 'finding': 'ClinicalImpressionFinding', 'prognosisCodeableConcept': 'CodeableConcept', 'prognosisReference': 'Reference', 'supportingInfo': 'Reference', 'note': 'Annotation'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod']}

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
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    date: Optional[DateTime] = None
    assessor: Optional[Reference]
    previous: Optional[Reference]
    problem: Reference | FHIRList[Reference]
    investigation: ClinicalImpressionInvestigation | FHIRList[ClinicalImpressionInvestigation]
    protocol: Uri | FHIRList[Uri] = None
    summary: Optional[String] = None
    finding: ClinicalImpressionFinding | FHIRList[ClinicalImpressionFinding]
    prognosisCodeableConcept: CodeableConcept | FHIRList[CodeableConcept]
    prognosisReference: Reference | FHIRList[Reference]
    supportingInfo: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]


class CodeSystemFilter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'operator'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    description: Optional[String] = None
    operator: Code | FHIRList[Code] = None
    value: Optional[String] = None


class CodeSystemProperty(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    uri: Optional[Uri] = None
    description: Optional[String] = None
    type_: Optional[Code] = None


class CodeSystemConcept(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'designation', 'property', 'concept'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'designation': 'CodeSystemConceptDesignation', 'property': 'CodeSystemConceptProperty'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    display: Optional[String] = None
    definition: Optional[String] = None
    designation: CodeSystemConceptDesignation | FHIRList[CodeSystemConceptDesignation]
    property: CodeSystemConceptProperty | FHIRList[CodeSystemConceptProperty]
    concept: Any = None


class CodeSystemConceptDesignation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'use': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    language: Optional[Code] = None
    use: Optional[Coding]
    value: Optional[String] = None


class CodeSystemConceptProperty(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'valueCoding': 'Coding'}
    _choice_fields = {'value': ['valueCode', 'valueCoding', 'valueString', 'valueInteger', 'valueBoolean', 'valueDateTime', 'valueDecimal']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    valueCode: Optional[Code] = None
    valueCoding: Optional[Coding]
    valueString: Optional[String] = None
    valueInteger: Optional[Integer] = None
    valueBoolean: Optional[Boolean] = None
    valueDateTime: Optional[DateTime] = None
    valueDecimal: Optional[Decimal] = None


class CodeSystem(FHIRResource):
    _resource_type = "CodeSystem"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'filter', 'property', 'concept'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'filter': 'CodeSystemFilter', 'property': 'CodeSystemProperty', 'concept': 'CodeSystemConcept'}

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
    filter: CodeSystemFilter | FHIRList[CodeSystemFilter]
    property: CodeSystemProperty | FHIRList[CodeSystemProperty]
    concept: CodeSystemConcept | FHIRList[CodeSystemConcept]


class CommunicationPayload(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'contentAttachment': 'Attachment', 'contentReference': 'Reference'}
    _choice_fields = {'content': ['contentString', 'contentAttachment', 'contentReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    contentString: Optional[String] = None
    contentAttachment: Optional[Attachment]
    contentReference: Optional[Reference]


class Communication(FHIRResource):
    _resource_type = "Communication"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'instantiatesCanonical', 'instantiatesUri', 'basedOn', 'partOf', 'inResponseTo', 'category', 'medium', 'about', 'recipient', 'reasonCode', 'reasonReference', 'payload', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'inResponseTo': 'Reference', 'statusReason': 'CodeableConcept', 'category': 'CodeableConcept', 'medium': 'CodeableConcept', 'subject': 'Reference', 'topic': 'CodeableConcept', 'about': 'Reference', 'encounter': 'Reference', 'recipient': 'Reference', 'sender': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'payload': 'CommunicationPayload', 'note': 'Annotation'}

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
    payload: CommunicationPayload | FHIRList[CommunicationPayload]
    note: Annotation | FHIRList[Annotation]


class CommunicationRequestPayload(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'contentAttachment': 'Attachment', 'contentReference': 'Reference'}
    _choice_fields = {'content': ['contentString', 'contentAttachment', 'contentReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    contentString: Optional[String] = None
    contentAttachment: Optional[Attachment]
    contentReference: Optional[Reference]


class CommunicationRequest(FHIRResource):
    _resource_type = "CommunicationRequest"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'replaces', 'category', 'medium', 'about', 'payload', 'recipient', 'reasonCode', 'reasonReference', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'replaces': 'Reference', 'groupIdentifier': 'Identifier', 'statusReason': 'CodeableConcept', 'category': 'CodeableConcept', 'medium': 'CodeableConcept', 'subject': 'Reference', 'about': 'Reference', 'encounter': 'Reference', 'payload': 'CommunicationRequestPayload', 'occurrencePeriod': 'Period', 'requester': 'Reference', 'recipient': 'Reference', 'sender': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'note': 'Annotation'}
    _choice_fields = {'occurrence': ['occurrenceDateTime', 'occurrencePeriod']}

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
    payload: CommunicationRequestPayload | FHIRList[CommunicationRequestPayload]
    occurrenceDateTime: Optional[DateTime] = None
    occurrencePeriod: Optional[Period]
    authoredOn: Optional[DateTime] = None
    requester: Optional[Reference]
    recipient: Reference | FHIRList[Reference]
    sender: Optional[Reference]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]


class CompartmentDefinitionResource(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'param'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    param: String | FHIRList[String] = None
    documentation: Optional[String] = None


class CompartmentDefinition(FHIRResource):
    _resource_type = "CompartmentDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'resource'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'resource': 'CompartmentDefinitionResource'}

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
    resource: CompartmentDefinitionResource | FHIRList[CompartmentDefinitionResource]


class CompositionAttester(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'party': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    mode: Optional[Code] = None
    time: Optional[DateTime] = None
    party: Optional[Reference]


class CompositionRelatesTo(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'targetIdentifier': 'Identifier', 'targetReference': 'Reference'}
    _choice_fields = {'target': ['targetIdentifier', 'targetReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    targetIdentifier: Optional[Identifier]
    targetReference: Optional[Reference]


class CompositionEvent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'detail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'period': 'Period', 'detail': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: CodeableConcept | FHIRList[CodeableConcept]
    period: Optional[Period]
    detail: Reference | FHIRList[Reference]


class CompositionSection(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'author', 'entry', 'section'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'author': 'Reference', 'focus': 'Reference', 'text': 'Narrative', 'orderedBy': 'CodeableConcept', 'entry': 'Reference', 'emptyReason': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    title: Optional[String] = None
    code: Optional[CodeableConcept]
    author: Reference | FHIRList[Reference]
    focus: Optional[Reference]
    text: Optional[Narrative]
    mode: Optional[Code] = None
    orderedBy: Optional[CodeableConcept]
    entry: Reference | FHIRList[Reference]
    emptyReason: Optional[CodeableConcept]
    section: Any = None


class Composition(FHIRResource):
    _resource_type = "Composition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'category', 'author', 'attester', 'relatesTo', 'event', 'section'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'category': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'author': 'Reference', 'attester': 'CompositionAttester', 'custodian': 'Reference', 'relatesTo': 'CompositionRelatesTo', 'event': 'CompositionEvent', 'section': 'CompositionSection'}

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
    type_: Optional[CodeableConcept]
    category: CodeableConcept | FHIRList[CodeableConcept]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    date: Optional[DateTime] = None
    author: Reference | FHIRList[Reference]
    title: Optional[String] = None
    confidentiality: Optional[Code] = None
    attester: CompositionAttester | FHIRList[CompositionAttester]
    custodian: Optional[Reference]
    relatesTo: CompositionRelatesTo | FHIRList[CompositionRelatesTo]
    event: CompositionEvent | FHIRList[CompositionEvent]
    section: CompositionSection | FHIRList[CompositionSection]


class ConceptMapGroup(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'element'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'element': 'ConceptMapGroupElement', 'unmapped': 'ConceptMapGroupUnmapped'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    source: Optional[Uri] = None
    sourceVersion: Optional[String] = None
    target: Optional[Uri] = None
    targetVersion: Optional[String] = None
    element: ConceptMapGroupElement | FHIRList[ConceptMapGroupElement]
    unmapped: Optional[ConceptMapGroupUnmapped]


class ConceptMapGroupElement(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'target'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'target': 'ConceptMapGroupElementTarget'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    display: Optional[String] = None
    target: ConceptMapGroupElementTarget | FHIRList[ConceptMapGroupElementTarget]


class ConceptMapGroupElementTarget(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'dependsOn', 'product'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'dependsOn': 'ConceptMapGroupElementTargetDependsOn'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    display: Optional[String] = None
    equivalence: Optional[Code] = None
    comment: Optional[String] = None
    dependsOn: ConceptMapGroupElementTargetDependsOn | FHIRList[ConceptMapGroupElementTargetDependsOn]
    product: Any = None


class ConceptMapGroupElementTargetDependsOn(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    property: Optional[Uri] = None
    system: Optional[Canonical] = None
    value: Optional[String] = None
    display: Optional[String] = None


class ConceptMapGroupUnmapped(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    mode: Optional[Code] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    url: Optional[Canonical] = None


class ConceptMap(FHIRResource):
    _resource_type = "ConceptMap"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'group'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'group': 'ConceptMapGroup'}
    _choice_fields = {'source': ['sourceUri', 'sourceCanonical'], 'target': ['targetUri', 'targetCanonical']}

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
    sourceUri: Optional[Uri] = None
    sourceCanonical: Optional[Canonical] = None
    targetUri: Optional[Uri] = None
    targetCanonical: Optional[Canonical] = None
    group: ConceptMapGroup | FHIRList[ConceptMapGroup]


class ConditionStage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'assessment'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'summary': 'CodeableConcept', 'assessment': 'Reference', 'type_': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    summary: Optional[CodeableConcept]
    assessment: Reference | FHIRList[Reference]
    type_: Optional[CodeableConcept]


class ConditionEvidence(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'detail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'detail': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: CodeableConcept | FHIRList[CodeableConcept]
    detail: Reference | FHIRList[Reference]


class Condition(FHIRResource):
    _resource_type = "Condition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'bodySite', 'stage', 'evidence', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'clinicalStatus': 'CodeableConcept', 'verificationStatus': 'CodeableConcept', 'category': 'CodeableConcept', 'severity': 'CodeableConcept', 'code': 'CodeableConcept', 'bodySite': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'onsetAge': 'Age', 'onsetPeriod': 'Period', 'onsetRange': 'Range', 'abatementAge': 'Age', 'abatementPeriod': 'Period', 'abatementRange': 'Range', 'recorder': 'Reference', 'asserter': 'Reference', 'stage': 'ConditionStage', 'evidence': 'ConditionEvidence', 'note': 'Annotation'}
    _choice_fields = {'abatement': ['abatementDateTime', 'abatementAge', 'abatementPeriod', 'abatementRange', 'abatementString'], 'onset': ['onsetDateTime', 'onsetAge', 'onsetPeriod', 'onsetRange', 'onsetString']}

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
    onsetDateTime: Optional[DateTime] = None
    onsetAge: Optional[Age]
    onsetPeriod: Optional[Period]
    onsetRange: Optional[Range]
    onsetString: Optional[String] = None
    abatementDateTime: Optional[DateTime] = None
    abatementAge: Optional[Age]
    abatementPeriod: Optional[Period]
    abatementRange: Optional[Range]
    abatementString: Optional[String] = None
    recordedDate: Optional[DateTime] = None
    recorder: Optional[Reference]
    asserter: Optional[Reference]
    stage: ConditionStage | FHIRList[ConditionStage]
    evidence: ConditionEvidence | FHIRList[ConditionEvidence]
    note: Annotation | FHIRList[Annotation]


class ConsentPolicy(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    authority: Optional[Uri] = None
    uri: Optional[Uri] = None


class ConsentVerification(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'verifiedWith': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    verified: Optional[Boolean] = None
    verifiedWith: Optional[Reference]
    verificationDate: Optional[DateTime] = None


class ConsentProvision(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'actor', 'action', 'securityLabel', 'purpose', 'class_', 'code', 'data', 'provision'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'period': 'Period', 'actor': 'ConsentProvisionActor', 'action': 'CodeableConcept', 'securityLabel': 'Coding', 'purpose': 'Coding', 'class_': 'Coding', 'code': 'CodeableConcept', 'dataPeriod': 'Period', 'data': 'ConsentProvisionData'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    period: Optional[Period]
    actor: ConsentProvisionActor | FHIRList[ConsentProvisionActor]
    action: CodeableConcept | FHIRList[CodeableConcept]
    securityLabel: Coding | FHIRList[Coding]
    purpose: Coding | FHIRList[Coding]
    class_: Coding | FHIRList[Coding]
    code: CodeableConcept | FHIRList[CodeableConcept]
    dataPeriod: Optional[Period]
    data: ConsentProvisionData | FHIRList[ConsentProvisionData]
    provision: Any = None


class ConsentProvisionActor(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'role': 'CodeableConcept', 'reference': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    role: Optional[CodeableConcept]
    reference: Optional[Reference]


class ConsentProvisionData(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'reference': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    meaning: Optional[Code] = None
    reference: Optional[Reference]


class Consent(FHIRResource):
    _resource_type = "Consent"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'performer', 'organization', 'policy', 'verification'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'scope': 'CodeableConcept', 'category': 'CodeableConcept', 'patient': 'Reference', 'performer': 'Reference', 'organization': 'Reference', 'sourceAttachment': 'Attachment', 'sourceReference': 'Reference', 'policy': 'ConsentPolicy', 'policyRule': 'CodeableConcept', 'verification': 'ConsentVerification', 'provision': 'ConsentProvision'}
    _choice_fields = {'source': ['sourceAttachment', 'sourceReference']}

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
    sourceAttachment: Optional[Attachment]
    sourceReference: Optional[Reference]
    policy: ConsentPolicy | FHIRList[ConsentPolicy]
    policyRule: Optional[CodeableConcept]
    verification: ConsentVerification | FHIRList[ConsentVerification]
    provision: Optional[ConsentProvision]


class ContractContentDefinition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'subType': 'CodeableConcept', 'publisher': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    subType: Optional[CodeableConcept]
    publisher: Optional[Reference]
    publicationDate: Optional[DateTime] = None
    publicationStatus: Optional[Code] = None
    copyright: Optional[Markdown] = None


class ContractTerm(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'securityLabel', 'asset', 'action', 'group'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'applies': 'Period', 'topicCodeableConcept': 'CodeableConcept', 'topicReference': 'Reference', 'type_': 'CodeableConcept', 'subType': 'CodeableConcept', 'securityLabel': 'ContractTermSecurityLabel', 'offer': 'ContractTermOffer', 'asset': 'ContractTermAsset', 'action': 'ContractTermAction'}
    _choice_fields = {'topic': ['topicCodeableConcept', 'topicReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Identifier]
    issued: Optional[DateTime] = None
    applies: Optional[Period]
    topicCodeableConcept: Optional[CodeableConcept]
    topicReference: Optional[Reference]
    type_: Optional[CodeableConcept]
    subType: Optional[CodeableConcept]
    text: Optional[String] = None
    securityLabel: ContractTermSecurityLabel | FHIRList[ContractTermSecurityLabel]
    offer: Optional[ContractTermOffer]
    asset: ContractTermAsset | FHIRList[ContractTermAsset]
    action: ContractTermAction | FHIRList[ContractTermAction]
    group: Any = None


class ContractTermSecurityLabel(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'number', 'category', 'control'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'classification': 'Coding', 'category': 'Coding', 'control': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    number: UnsignedInt | FHIRList[UnsignedInt] = None
    classification: Optional[Coding]
    category: Coding | FHIRList[Coding]
    control: Coding | FHIRList[Coding]


class ContractTermOffer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'identifier', 'party', 'decisionMode', 'answer', 'linkId', 'securityLabelNumber'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'party': 'ContractTermOfferParty', 'topic': 'Reference', 'type_': 'CodeableConcept', 'decision': 'CodeableConcept', 'decisionMode': 'CodeableConcept', 'answer': 'ContractTermOfferAnswer'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    party: ContractTermOfferParty | FHIRList[ContractTermOfferParty]
    topic: Optional[Reference]
    type_: Optional[CodeableConcept]
    decision: Optional[CodeableConcept]
    decisionMode: CodeableConcept | FHIRList[CodeableConcept]
    answer: ContractTermOfferAnswer | FHIRList[ContractTermOfferAnswer]
    text: Optional[String] = None
    linkId: String | FHIRList[String] = None
    securityLabelNumber: UnsignedInt | FHIRList[UnsignedInt] = None


class ContractTermOfferParty(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'reference'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'reference': 'Reference', 'role': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    reference: Reference | FHIRList[Reference]
    role: Optional[CodeableConcept]


class ContractTermOfferAnswer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'valueAttachment': 'Attachment', 'valueCoding': 'Coding', 'valueQuantity': 'Quantity', 'valueReference': 'Reference'}
    _choice_fields = {'value': ['valueBoolean', 'valueDecimal', 'valueInteger', 'valueDate', 'valueDateTime', 'valueTime', 'valueString', 'valueUri', 'valueAttachment', 'valueCoding', 'valueQuantity', 'valueReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    valueBoolean: Optional[Boolean] = None
    valueDecimal: Optional[Decimal] = None
    valueInteger: Optional[Integer] = None
    valueDate: Optional[Date] = None
    valueDateTime: Optional[DateTime] = None
    valueTime: Optional[Time] = None
    valueString: Optional[String] = None
    valueUri: Optional[Uri] = None
    valueAttachment: Optional[Attachment]
    valueCoding: Optional[Coding]
    valueQuantity: Optional[Quantity]
    valueReference: Optional[Reference]


class ContractTermAsset(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'type_', 'typeReference', 'subtype', 'context', 'periodType', 'period', 'usePeriod', 'linkId', 'answer', 'securityLabelNumber', 'valuedItem'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'scope': 'CodeableConcept', 'type_': 'CodeableConcept', 'typeReference': 'Reference', 'subtype': 'CodeableConcept', 'relationship': 'Coding', 'context': 'ContractTermAssetContext', 'periodType': 'CodeableConcept', 'period': 'Period', 'usePeriod': 'Period', 'valuedItem': 'ContractTermAssetValuedItem'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    scope: Optional[CodeableConcept]
    type_: CodeableConcept | FHIRList[CodeableConcept]
    typeReference: Reference | FHIRList[Reference]
    subtype: CodeableConcept | FHIRList[CodeableConcept]
    relationship: Optional[Coding]
    context: ContractTermAssetContext | FHIRList[ContractTermAssetContext]
    condition: Optional[String] = None
    periodType: CodeableConcept | FHIRList[CodeableConcept]
    period: Period | FHIRList[Period]
    usePeriod: Period | FHIRList[Period]
    text: Optional[String] = None
    linkId: String | FHIRList[String] = None
    answer: Any = None
    securityLabelNumber: UnsignedInt | FHIRList[UnsignedInt] = None
    valuedItem: ContractTermAssetValuedItem | FHIRList[ContractTermAssetValuedItem]


class ContractTermAssetContext(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'reference': 'Reference', 'code': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    reference: Optional[Reference]
    code: CodeableConcept | FHIRList[CodeableConcept]
    text: Optional[String] = None


class ContractTermAssetValuedItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'linkId', 'securityLabelNumber'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'entityCodeableConcept': 'CodeableConcept', 'entityReference': 'Reference', 'identifier': 'Identifier', 'quantity': 'Quantity', 'unitPrice': 'Money', 'net': 'Money', 'responsible': 'Reference', 'recipient': 'Reference'}
    _choice_fields = {'entity': ['entityCodeableConcept', 'entityReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    entityCodeableConcept: Optional[CodeableConcept]
    entityReference: Optional[Reference]
    identifier: Optional[Identifier]
    effectiveTime: Optional[DateTime] = None
    quantity: Optional[Quantity]
    unitPrice: Optional[Money]
    factor: Optional[Decimal] = None
    points: Optional[Decimal] = None
    net: Optional[Money]
    payment: Optional[String] = None
    paymentDate: Optional[DateTime] = None
    responsible: Optional[Reference]
    recipient: Optional[Reference]
    linkId: String | FHIRList[String] = None
    securityLabelNumber: UnsignedInt | FHIRList[UnsignedInt] = None


class ContractTermAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'subject', 'linkId', 'contextLinkId', 'requester', 'requesterLinkId', 'performerType', 'performerLinkId', 'reasonCode', 'reasonReference', 'reason', 'reasonLinkId', 'note', 'securityLabelNumber'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'subject': 'ContractTermActionSubject', 'intent': 'CodeableConcept', 'status': 'CodeableConcept', 'context': 'Reference', 'occurrencePeriod': 'Period', 'occurrenceTiming': 'Timing', 'requester': 'Reference', 'performerType': 'CodeableConcept', 'performerRole': 'CodeableConcept', 'performer': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'note': 'Annotation'}
    _choice_fields = {'occurrence': ['occurrenceDateTime', 'occurrencePeriod', 'occurrenceTiming']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    doNotPerform: Optional[Boolean] = None
    type_: Optional[CodeableConcept]
    subject: ContractTermActionSubject | FHIRList[ContractTermActionSubject]
    intent: Optional[CodeableConcept]
    linkId: String | FHIRList[String] = None
    status: Optional[CodeableConcept]
    context: Optional[Reference]
    contextLinkId: String | FHIRList[String] = None
    occurrenceDateTime: Optional[DateTime] = None
    occurrencePeriod: Optional[Period]
    occurrenceTiming: Optional[Timing]
    requester: Reference | FHIRList[Reference]
    requesterLinkId: String | FHIRList[String] = None
    performerType: CodeableConcept | FHIRList[CodeableConcept]
    performerRole: Optional[CodeableConcept]
    performer: Optional[Reference]
    performerLinkId: String | FHIRList[String] = None
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    reason: String | FHIRList[String] = None
    reasonLinkId: String | FHIRList[String] = None
    note: Annotation | FHIRList[Annotation]
    securityLabelNumber: UnsignedInt | FHIRList[UnsignedInt] = None


class ContractTermActionSubject(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'reference'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'reference': 'Reference', 'role': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    reference: Reference | FHIRList[Reference]
    role: Optional[CodeableConcept]


class ContractSigner(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'signature'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'Coding', 'party': 'Reference', 'signature': 'Signature'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Coding]
    party: Optional[Reference]
    signature: Signature | FHIRList[Signature]


class ContractFriendly(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'contentAttachment': 'Attachment', 'contentReference': 'Reference'}
    _choice_fields = {'content': ['contentAttachment', 'contentReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    contentAttachment: Optional[Attachment]
    contentReference: Optional[Reference]


class ContractLegal(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'contentAttachment': 'Attachment', 'contentReference': 'Reference'}
    _choice_fields = {'content': ['contentAttachment', 'contentReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    contentAttachment: Optional[Attachment]
    contentReference: Optional[Reference]


class ContractRule(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'contentAttachment': 'Attachment', 'contentReference': 'Reference'}
    _choice_fields = {'content': ['contentAttachment', 'contentReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    contentAttachment: Optional[Attachment]
    contentReference: Optional[Reference]


class Contract(FHIRResource):
    _resource_type = "Contract"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'subject', 'authority', 'domain', 'site', 'alias', 'subType', 'term', 'supportingInfo', 'relevantHistory', 'signer', 'friendly', 'legal', 'rule'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'legalState': 'CodeableConcept', 'instantiatesCanonical': 'Reference', 'contentDerivative': 'CodeableConcept', 'applies': 'Period', 'expirationType': 'CodeableConcept', 'subject': 'Reference', 'authority': 'Reference', 'domain': 'Reference', 'site': 'Reference', 'author': 'Reference', 'scope': 'CodeableConcept', 'topicCodeableConcept': 'CodeableConcept', 'topicReference': 'Reference', 'type_': 'CodeableConcept', 'subType': 'CodeableConcept', 'contentDefinition': 'ContractContentDefinition', 'term': 'ContractTerm', 'supportingInfo': 'Reference', 'relevantHistory': 'Reference', 'signer': 'ContractSigner', 'friendly': 'ContractFriendly', 'legal': 'ContractLegal', 'rule': 'ContractRule', 'legallyBindingAttachment': 'Attachment', 'legallyBindingReference': 'Reference'}
    _choice_fields = {'legallyBinding': ['legallyBindingAttachment', 'legallyBindingReference'], 'topic': ['topicCodeableConcept', 'topicReference']}

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
    topicCodeableConcept: Optional[CodeableConcept]
    topicReference: Optional[Reference]
    type_: Optional[CodeableConcept]
    subType: CodeableConcept | FHIRList[CodeableConcept]
    contentDefinition: Optional[ContractContentDefinition]
    term: ContractTerm | FHIRList[ContractTerm]
    supportingInfo: Reference | FHIRList[Reference]
    relevantHistory: Reference | FHIRList[Reference]
    signer: ContractSigner | FHIRList[ContractSigner]
    friendly: ContractFriendly | FHIRList[ContractFriendly]
    legal: ContractLegal | FHIRList[ContractLegal]
    rule: ContractRule | FHIRList[ContractRule]
    legallyBindingAttachment: Optional[Attachment]
    legallyBindingReference: Optional[Reference]


class CoverageClass(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    value: Optional[String] = None
    name: Optional[String] = None


class CoverageCostToBeneficiary(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'exception'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueMoney': 'Money', 'exception': 'CoverageCostToBeneficiaryException'}
    _choice_fields = {'value': ['valueQuantity', 'valueMoney']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    valueQuantity: Optional[Quantity]
    valueMoney: Optional[Money]
    exception: CoverageCostToBeneficiaryException | FHIRList[CoverageCostToBeneficiaryException]


class CoverageCostToBeneficiaryException(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    period: Optional[Period]


class Coverage(FHIRResource):
    _resource_type = "Coverage"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'payor', 'class_', 'costToBeneficiary', 'contract'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'policyHolder': 'Reference', 'subscriber': 'Reference', 'beneficiary': 'Reference', 'relationship': 'CodeableConcept', 'period': 'Period', 'payor': 'Reference', 'class_': 'CoverageClass', 'costToBeneficiary': 'CoverageCostToBeneficiary', 'contract': 'Reference'}

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
    type_: Optional[CodeableConcept]
    policyHolder: Optional[Reference]
    subscriber: Optional[Reference]
    subscriberId: Optional[String] = None
    beneficiary: Optional[Reference]
    dependent: Optional[String] = None
    relationship: Optional[CodeableConcept]
    period: Optional[Period]
    payor: Reference | FHIRList[Reference]
    class_: CoverageClass | FHIRList[CoverageClass]
    order: Optional[PositiveInt] = None
    network: Optional[String] = None
    costToBeneficiary: CoverageCostToBeneficiary | FHIRList[CoverageCostToBeneficiary]
    subrogation: Optional[Boolean] = None
    contract: Reference | FHIRList[Reference]


class CoverageEligibilityRequestSupportingInfo(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'information': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequence: Optional[PositiveInt] = None
    information: Optional[Reference]
    appliesToAll: Optional[Boolean] = None


class CoverageEligibilityRequestInsurance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'coverage': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    focal: Optional[Boolean] = None
    coverage: Optional[Reference]
    businessArrangement: Optional[String] = None


class CoverageEligibilityRequestItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'supportingInfoSequence', 'modifier', 'diagnosis', 'detail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'category': 'CodeableConcept', 'productOrService': 'CodeableConcept', 'modifier': 'CodeableConcept', 'provider': 'Reference', 'quantity': 'Quantity', 'unitPrice': 'Money', 'facility': 'Reference', 'diagnosis': 'CoverageEligibilityRequestItemDiagnosis', 'detail': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    supportingInfoSequence: PositiveInt | FHIRList[PositiveInt] = None
    category: Optional[CodeableConcept]
    productOrService: Optional[CodeableConcept]
    modifier: CodeableConcept | FHIRList[CodeableConcept]
    provider: Optional[Reference]
    quantity: Optional[Quantity]
    unitPrice: Optional[Money]
    facility: Optional[Reference]
    diagnosis: CoverageEligibilityRequestItemDiagnosis | FHIRList[CoverageEligibilityRequestItemDiagnosis]
    detail: Reference | FHIRList[Reference]


class CoverageEligibilityRequestItemDiagnosis(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'diagnosisCodeableConcept': 'CodeableConcept', 'diagnosisReference': 'Reference'}
    _choice_fields = {'diagnosis': ['diagnosisCodeableConcept', 'diagnosisReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    diagnosisCodeableConcept: Optional[CodeableConcept]
    diagnosisReference: Optional[Reference]


class CoverageEligibilityRequest(FHIRResource):
    _resource_type = "CoverageEligibilityRequest"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'purpose', 'supportingInfo', 'insurance', 'item'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'priority': 'CodeableConcept', 'patient': 'Reference', 'servicedPeriod': 'Period', 'enterer': 'Reference', 'provider': 'Reference', 'insurer': 'Reference', 'facility': 'Reference', 'supportingInfo': 'CoverageEligibilityRequestSupportingInfo', 'insurance': 'CoverageEligibilityRequestInsurance', 'item': 'CoverageEligibilityRequestItem'}
    _choice_fields = {'serviced': ['servicedDate', 'servicedPeriod']}

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
    servicedDate: Optional[Date] = None
    servicedPeriod: Optional[Period]
    created: Optional[DateTime] = None
    enterer: Optional[Reference]
    provider: Optional[Reference]
    insurer: Optional[Reference]
    facility: Optional[Reference]
    supportingInfo: CoverageEligibilityRequestSupportingInfo | FHIRList[CoverageEligibilityRequestSupportingInfo]
    insurance: CoverageEligibilityRequestInsurance | FHIRList[CoverageEligibilityRequestInsurance]
    item: CoverageEligibilityRequestItem | FHIRList[CoverageEligibilityRequestItem]


class CoverageEligibilityResponseInsurance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'item'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'coverage': 'Reference', 'benefitPeriod': 'Period', 'item': 'CoverageEligibilityResponseInsuranceItem'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    coverage: Optional[Reference]
    inforce: Optional[Boolean] = None
    benefitPeriod: Optional[Period]
    item: CoverageEligibilityResponseInsuranceItem | FHIRList[CoverageEligibilityResponseInsuranceItem]


class CoverageEligibilityResponseInsuranceItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'modifier', 'benefit', 'authorizationSupporting'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'category': 'CodeableConcept', 'productOrService': 'CodeableConcept', 'modifier': 'CodeableConcept', 'provider': 'Reference', 'network': 'CodeableConcept', 'unit': 'CodeableConcept', 'term': 'CodeableConcept', 'benefit': 'CoverageEligibilityResponseInsuranceItemBenefit', 'authorizationSupporting': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    category: Optional[CodeableConcept]
    productOrService: Optional[CodeableConcept]
    modifier: CodeableConcept | FHIRList[CodeableConcept]
    provider: Optional[Reference]
    excluded: Optional[Boolean] = None
    name: Optional[String] = None
    description: Optional[String] = None
    network: Optional[CodeableConcept]
    unit: Optional[CodeableConcept]
    term: Optional[CodeableConcept]
    benefit: CoverageEligibilityResponseInsuranceItemBenefit | FHIRList[CoverageEligibilityResponseInsuranceItemBenefit]
    authorizationRequired: Optional[Boolean] = None
    authorizationSupporting: CodeableConcept | FHIRList[CodeableConcept]
    authorizationUrl: Optional[Uri] = None


class CoverageEligibilityResponseInsuranceItemBenefit(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'allowedMoney': 'Money', 'usedMoney': 'Money'}
    _choice_fields = {'allowed': ['allowedUnsignedInt', 'allowedString', 'allowedMoney'], 'used': ['usedUnsignedInt', 'usedString', 'usedMoney']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    allowedUnsignedInt: Optional[UnsignedInt] = None
    allowedString: Optional[String] = None
    allowedMoney: Optional[Money]
    usedUnsignedInt: Optional[UnsignedInt] = None
    usedString: Optional[String] = None
    usedMoney: Optional[Money]


class CoverageEligibilityResponseError(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]


class CoverageEligibilityResponse(FHIRResource):
    _resource_type = "CoverageEligibilityResponse"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'purpose', 'insurance', 'error'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'patient': 'Reference', 'servicedPeriod': 'Period', 'requestor': 'Reference', 'request': 'Reference', 'insurer': 'Reference', 'insurance': 'CoverageEligibilityResponseInsurance', 'form': 'CodeableConcept', 'error': 'CoverageEligibilityResponseError'}
    _choice_fields = {'serviced': ['servicedDate', 'servicedPeriod']}

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
    servicedDate: Optional[Date] = None
    servicedPeriod: Optional[Period]
    created: Optional[DateTime] = None
    requestor: Optional[Reference]
    request: Optional[Reference]
    outcome: Optional[Code] = None
    disposition: Optional[String] = None
    insurer: Optional[Reference]
    insurance: CoverageEligibilityResponseInsurance | FHIRList[CoverageEligibilityResponseInsurance]
    preAuthRef: Optional[String] = None
    form: Optional[CodeableConcept]
    error: CoverageEligibilityResponseError | FHIRList[CoverageEligibilityResponseError]


class DetectedIssueEvidence(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'detail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'detail': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: CodeableConcept | FHIRList[CodeableConcept]
    detail: Reference | FHIRList[Reference]


class DetectedIssueMitigation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'action': 'CodeableConcept', 'author': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    action: Optional[CodeableConcept]
    date: Optional[DateTime] = None
    author: Optional[Reference]


class DetectedIssue(FHIRResource):
    _resource_type = "DetectedIssue"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'implicated', 'evidence', 'mitigation'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'code': 'CodeableConcept', 'patient': 'Reference', 'identifiedPeriod': 'Period', 'author': 'Reference', 'implicated': 'Reference', 'evidence': 'DetectedIssueEvidence', 'mitigation': 'DetectedIssueMitigation'}
    _choice_fields = {'identified': ['identifiedDateTime', 'identifiedPeriod']}

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
    identifiedDateTime: Optional[DateTime] = None
    identifiedPeriod: Optional[Period]
    author: Optional[Reference]
    implicated: Reference | FHIRList[Reference]
    evidence: DetectedIssueEvidence | FHIRList[DetectedIssueEvidence]
    detail: Optional[String] = None
    reference: Optional[Uri] = None
    mitigation: DetectedIssueMitigation | FHIRList[DetectedIssueMitigation]


class DeviceUdiCarrier(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    deviceIdentifier: Optional[String] = None
    issuer: Optional[Uri] = None
    jurisdiction: Optional[Uri] = None
    carrierAIDC: Optional[Base64Binary] = None
    carrierHRF: Optional[String] = None
    entryType: Optional[Code] = None


class DeviceDeviceName(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[String] = None
    type_: Optional[Code] = None


class DeviceSpecialization(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'systemType': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    systemType: Optional[CodeableConcept]
    version: Optional[String] = None


class DeviceVersion(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'component': 'Identifier'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    component: Optional[Identifier]
    value: Optional[String] = None


class DeviceProperty(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'valueQuantity', 'valueCode'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueCode': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    valueQuantity: Quantity | FHIRList[Quantity]
    valueCode: CodeableConcept | FHIRList[CodeableConcept]


class Device(FHIRResource):
    _resource_type = "Device"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'udiCarrier', 'statusReason', 'deviceName', 'specialization', 'version', 'property', 'contact', 'note', 'safety'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'definition': 'Reference', 'udiCarrier': 'DeviceUdiCarrier', 'statusReason': 'CodeableConcept', 'deviceName': 'DeviceDeviceName', 'type_': 'CodeableConcept', 'specialization': 'DeviceSpecialization', 'version': 'DeviceVersion', 'property': 'DeviceProperty', 'patient': 'Reference', 'owner': 'Reference', 'contact': 'ContactPoint', 'location': 'Reference', 'note': 'Annotation', 'safety': 'CodeableConcept', 'parent': 'Reference'}

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
    udiCarrier: DeviceUdiCarrier | FHIRList[DeviceUdiCarrier]
    status: Optional[Code] = None
    statusReason: CodeableConcept | FHIRList[CodeableConcept]
    distinctIdentifier: Optional[String] = None
    manufacturer: Optional[String] = None
    manufactureDate: Optional[DateTime] = None
    expirationDate: Optional[DateTime] = None
    lotNumber: Optional[String] = None
    serialNumber: Optional[String] = None
    deviceName: DeviceDeviceName | FHIRList[DeviceDeviceName]
    modelNumber: Optional[String] = None
    partNumber: Optional[String] = None
    type_: Optional[CodeableConcept]
    specialization: DeviceSpecialization | FHIRList[DeviceSpecialization]
    version: DeviceVersion | FHIRList[DeviceVersion]
    property: DeviceProperty | FHIRList[DeviceProperty]
    patient: Optional[Reference]
    owner: Optional[Reference]
    contact: ContactPoint | FHIRList[ContactPoint]
    location: Optional[Reference]
    url: Optional[Uri] = None
    note: Annotation | FHIRList[Annotation]
    safety: CodeableConcept | FHIRList[CodeableConcept]
    parent: Optional[Reference]


class DeviceDefinitionUdiDeviceIdentifier(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    deviceIdentifier: Optional[String] = None
    issuer: Optional[Uri] = None
    jurisdiction: Optional[Uri] = None


class DeviceDefinitionDeviceName(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[String] = None
    type_: Optional[Code] = None


class DeviceDefinitionSpecialization(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    systemType: Optional[String] = None
    version: Optional[String] = None


class DeviceDefinitionCapability(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'description'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'description': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    description: CodeableConcept | FHIRList[CodeableConcept]


class DeviceDefinitionProperty(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'valueQuantity', 'valueCode'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueCode': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    valueQuantity: Quantity | FHIRList[Quantity]
    valueCode: CodeableConcept | FHIRList[CodeableConcept]


class DeviceDefinitionMaterial(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'substance': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    substance: Optional[CodeableConcept]
    alternate: Optional[Boolean] = None
    allergenicIndicator: Optional[Boolean] = None


class DeviceDefinition(FHIRResource):
    _resource_type = "DeviceDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'udiDeviceIdentifier', 'deviceName', 'specialization', 'version', 'safety', 'shelfLifeStorage', 'languageCode', 'capability', 'property', 'contact', 'note', 'material'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'udiDeviceIdentifier': 'DeviceDefinitionUdiDeviceIdentifier', 'manufacturerReference': 'Reference', 'deviceName': 'DeviceDefinitionDeviceName', 'type_': 'CodeableConcept', 'specialization': 'DeviceDefinitionSpecialization', 'safety': 'CodeableConcept', 'shelfLifeStorage': 'ProductShelfLife', 'physicalCharacteristics': 'ProdCharacteristic', 'languageCode': 'CodeableConcept', 'capability': 'DeviceDefinitionCapability', 'property': 'DeviceDefinitionProperty', 'owner': 'Reference', 'contact': 'ContactPoint', 'note': 'Annotation', 'quantity': 'Quantity', 'parentDevice': 'Reference', 'material': 'DeviceDefinitionMaterial'}
    _choice_fields = {'manufacturer': ['manufacturerString', 'manufacturerReference']}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    udiDeviceIdentifier: DeviceDefinitionUdiDeviceIdentifier | FHIRList[DeviceDefinitionUdiDeviceIdentifier]
    manufacturerString: Optional[String] = None
    manufacturerReference: Optional[Reference]
    deviceName: DeviceDefinitionDeviceName | FHIRList[DeviceDefinitionDeviceName]
    modelNumber: Optional[String] = None
    type_: Optional[CodeableConcept]
    specialization: DeviceDefinitionSpecialization | FHIRList[DeviceDefinitionSpecialization]
    version: String | FHIRList[String] = None
    safety: CodeableConcept | FHIRList[CodeableConcept]
    shelfLifeStorage: ProductShelfLife | FHIRList[ProductShelfLife]
    physicalCharacteristics: Optional[ProdCharacteristic]
    languageCode: CodeableConcept | FHIRList[CodeableConcept]
    capability: DeviceDefinitionCapability | FHIRList[DeviceDefinitionCapability]
    property: DeviceDefinitionProperty | FHIRList[DeviceDefinitionProperty]
    owner: Optional[Reference]
    contact: ContactPoint | FHIRList[ContactPoint]
    url: Optional[Uri] = None
    onlineInformation: Optional[Uri] = None
    note: Annotation | FHIRList[Annotation]
    quantity: Optional[Quantity]
    parentDevice: Optional[Reference]
    material: DeviceDefinitionMaterial | FHIRList[DeviceDefinitionMaterial]


class DeviceMetricCalibration(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    state: Optional[Code] = None
    time: Optional[Instant] = None


class DeviceMetric(FHIRResource):
    _resource_type = "DeviceMetric"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'calibration'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'unit': 'CodeableConcept', 'source': 'Reference', 'parent': 'Reference', 'measurementPeriod': 'Timing', 'calibration': 'DeviceMetricCalibration'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    type_: Optional[CodeableConcept]
    unit: Optional[CodeableConcept]
    source: Optional[Reference]
    parent: Optional[Reference]
    operationalStatus: Optional[Code] = None
    color: Optional[Code] = None
    category: Optional[Code] = None
    measurementPeriod: Optional[Timing]
    calibration: DeviceMetricCalibration | FHIRList[DeviceMetricCalibration]


class DeviceRequestParameter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueCodeableConcept': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueRange': 'Range'}
    _choice_fields = {'value': ['valueCodeableConcept', 'valueQuantity', 'valueRange', 'valueBoolean']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueCodeableConcept: Optional[CodeableConcept]
    valueQuantity: Optional[Quantity]
    valueRange: Optional[Range]
    valueBoolean: Optional[Boolean] = None


class DeviceRequest(FHIRResource):
    _resource_type = "DeviceRequest"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'instantiatesCanonical', 'instantiatesUri', 'basedOn', 'priorRequest', 'parameter', 'reasonCode', 'reasonReference', 'insurance', 'supportingInfo', 'note', 'relevantHistory'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'priorRequest': 'Reference', 'groupIdentifier': 'Identifier', 'codeReference': 'Reference', 'codeCodeableConcept': 'CodeableConcept', 'parameter': 'DeviceRequestParameter', 'subject': 'Reference', 'encounter': 'Reference', 'occurrencePeriod': 'Period', 'occurrenceTiming': 'Timing', 'requester': 'Reference', 'performerType': 'CodeableConcept', 'performer': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'insurance': 'Reference', 'supportingInfo': 'Reference', 'note': 'Annotation', 'relevantHistory': 'Reference'}
    _choice_fields = {'code': ['codeReference', 'codeCodeableConcept'], 'occurrence': ['occurrenceDateTime', 'occurrencePeriod', 'occurrenceTiming']}

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
    codeReference: Optional[Reference]
    codeCodeableConcept: Optional[CodeableConcept]
    parameter: DeviceRequestParameter | FHIRList[DeviceRequestParameter]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    occurrenceDateTime: Optional[DateTime] = None
    occurrencePeriod: Optional[Period]
    occurrenceTiming: Optional[Timing]
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
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'subject': 'Reference', 'derivedFrom': 'Reference', 'timingTiming': 'Timing', 'timingPeriod': 'Period', 'source': 'Reference', 'device': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'bodySite': 'CodeableConcept', 'note': 'Annotation'}
    _choice_fields = {'timing': ['timingTiming', 'timingPeriod', 'timingDateTime']}

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
    timingTiming: Optional[Timing]
    timingPeriod: Optional[Period]
    timingDateTime: Optional[DateTime] = None
    recordedOn: Optional[DateTime] = None
    source: Optional[Reference]
    device: Optional[Reference]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    bodySite: Optional[CodeableConcept]
    note: Annotation | FHIRList[Annotation]


class DiagnosticReportMedia(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'link': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    comment: Optional[String] = None
    link: Optional[Reference]


class DiagnosticReport(FHIRResource):
    _resource_type = "DiagnosticReport"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'category', 'performer', 'resultsInterpreter', 'specimen', 'result', 'imagingStudy', 'media', 'conclusionCode', 'presentedForm'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'effectivePeriod': 'Period', 'performer': 'Reference', 'resultsInterpreter': 'Reference', 'specimen': 'Reference', 'result': 'Reference', 'imagingStudy': 'Reference', 'media': 'DiagnosticReportMedia', 'conclusionCode': 'CodeableConcept', 'presentedForm': 'Attachment'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod']}

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
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    resultsInterpreter: Reference | FHIRList[Reference]
    specimen: Reference | FHIRList[Reference]
    result: Reference | FHIRList[Reference]
    imagingStudy: Reference | FHIRList[Reference]
    media: DiagnosticReportMedia | FHIRList[DiagnosticReportMedia]
    conclusion: Optional[String] = None
    conclusionCode: CodeableConcept | FHIRList[CodeableConcept]
    presentedForm: Attachment | FHIRList[Attachment]


class DocumentManifestRelated(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'ref': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Identifier]
    ref: Optional[Reference]


class DocumentManifest(FHIRResource):
    _resource_type = "DocumentManifest"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'author', 'recipient', 'content', 'related'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'masterIdentifier': 'Identifier', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'subject': 'Reference', 'author': 'Reference', 'recipient': 'Reference', 'content': 'Reference', 'related': 'DocumentManifestRelated'}

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
    type_: Optional[CodeableConcept]
    subject: Optional[Reference]
    created: Optional[DateTime] = None
    author: Reference | FHIRList[Reference]
    recipient: Reference | FHIRList[Reference]
    source: Optional[Uri] = None
    description: Optional[String] = None
    content: Reference | FHIRList[Reference]
    related: DocumentManifestRelated | FHIRList[DocumentManifestRelated]


class DocumentReferenceRelatesTo(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'target': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    target: Optional[Reference]


class DocumentReferenceContent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'attachment': 'Attachment', 'format': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    attachment: Optional[Attachment]
    format: Optional[Coding]


class DocumentReferenceContext(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'encounter', 'event', 'related'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'encounter': 'Reference', 'event': 'CodeableConcept', 'period': 'Period', 'facilityType': 'CodeableConcept', 'practiceSetting': 'CodeableConcept', 'sourcePatientInfo': 'Reference', 'related': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    encounter: Reference | FHIRList[Reference]
    event: CodeableConcept | FHIRList[CodeableConcept]
    period: Optional[Period]
    facilityType: Optional[CodeableConcept]
    practiceSetting: Optional[CodeableConcept]
    sourcePatientInfo: Optional[Reference]
    related: Reference | FHIRList[Reference]


class DocumentReference(FHIRResource):
    _resource_type = "DocumentReference"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'author', 'relatesTo', 'securityLabel', 'content'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'masterIdentifier': 'Identifier', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'category': 'CodeableConcept', 'subject': 'Reference', 'author': 'Reference', 'authenticator': 'Reference', 'custodian': 'Reference', 'relatesTo': 'DocumentReferenceRelatesTo', 'securityLabel': 'CodeableConcept', 'content': 'DocumentReferenceContent', 'context': 'DocumentReferenceContext'}

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
    type_: Optional[CodeableConcept]
    category: CodeableConcept | FHIRList[CodeableConcept]
    subject: Optional[Reference]
    date: Optional[Instant] = None
    author: Reference | FHIRList[Reference]
    authenticator: Optional[Reference]
    custodian: Optional[Reference]
    relatesTo: DocumentReferenceRelatesTo | FHIRList[DocumentReferenceRelatesTo]
    description: Optional[String] = None
    securityLabel: CodeableConcept | FHIRList[CodeableConcept]
    content: DocumentReferenceContent | FHIRList[DocumentReferenceContent]
    context: Optional[DocumentReferenceContext]


class EffectEvidenceSynthesisSampleSize(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    description: Optional[String] = None
    numberOfStudies: Optional[Integer] = None
    numberOfParticipants: Optional[Integer] = None


class EffectEvidenceSynthesisResultsByExposure(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'variantState': 'CodeableConcept', 'riskEvidenceSynthesis': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    description: Optional[String] = None
    exposureState: Optional[Code] = None
    variantState: Optional[CodeableConcept]
    riskEvidenceSynthesis: Optional[Reference]


class EffectEvidenceSynthesisEffectEstimate(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'precisionEstimate'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'variantState': 'CodeableConcept', 'unitOfMeasure': 'CodeableConcept', 'precisionEstimate': 'EffectEvidenceSynthesisEffectEstimatePrecisionEstimate'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    description: Optional[String] = None
    type_: Optional[CodeableConcept]
    variantState: Optional[CodeableConcept]
    value: Optional[Decimal] = None
    unitOfMeasure: Optional[CodeableConcept]
    precisionEstimate: EffectEvidenceSynthesisEffectEstimatePrecisionEstimate | FHIRList[EffectEvidenceSynthesisEffectEstimatePrecisionEstimate]


class EffectEvidenceSynthesisEffectEstimatePrecisionEstimate(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    level: Optional[Decimal] = None
    from_: Optional[Decimal] = None
    to: Optional[Decimal] = None


class EffectEvidenceSynthesisCertainty(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'rating', 'note', 'certaintySubcomponent'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'rating': 'CodeableConcept', 'note': 'Annotation', 'certaintySubcomponent': 'EffectEvidenceSynthesisCertaintyCertaintySubcomponent'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    rating: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    certaintySubcomponent: EffectEvidenceSynthesisCertaintyCertaintySubcomponent | FHIRList[EffectEvidenceSynthesisCertaintyCertaintySubcomponent]


class EffectEvidenceSynthesisCertaintyCertaintySubcomponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'rating', 'note'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'rating': 'CodeableConcept', 'note': 'Annotation'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    rating: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]


class EffectEvidenceSynthesis(FHIRResource):
    _resource_type = "EffectEvidenceSynthesis"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'note', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'resultsByExposure', 'effectEstimate', 'certainty'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'note': 'Annotation', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'synthesisType': 'CodeableConcept', 'studyType': 'CodeableConcept', 'population': 'Reference', 'exposure': 'Reference', 'exposureAlternative': 'Reference', 'outcome': 'Reference', 'sampleSize': 'EffectEvidenceSynthesisSampleSize', 'resultsByExposure': 'EffectEvidenceSynthesisResultsByExposure', 'effectEstimate': 'EffectEvidenceSynthesisEffectEstimate', 'certainty': 'EffectEvidenceSynthesisCertainty'}

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
    sampleSize: Optional[EffectEvidenceSynthesisSampleSize]
    resultsByExposure: EffectEvidenceSynthesisResultsByExposure | FHIRList[EffectEvidenceSynthesisResultsByExposure]
    effectEstimate: EffectEvidenceSynthesisEffectEstimate | FHIRList[EffectEvidenceSynthesisEffectEstimate]
    certainty: EffectEvidenceSynthesisCertainty | FHIRList[EffectEvidenceSynthesisCertainty]


class EncounterStatusHistory(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    status: Optional[Code] = None
    period: Optional[Period]


class EncounterClassHistory(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'class_': 'Coding', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    class_: Optional[Coding]
    period: Optional[Period]


class EncounterParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'type_'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'period': 'Period', 'individual': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: CodeableConcept | FHIRList[CodeableConcept]
    period: Optional[Period]
    individual: Optional[Reference]


class EncounterDiagnosis(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'condition': 'Reference', 'use': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    condition: Optional[Reference]
    use: Optional[CodeableConcept]
    rank: Optional[PositiveInt] = None


class EncounterHospitalization(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'dietPreference', 'specialCourtesy', 'specialArrangement'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'preAdmissionIdentifier': 'Identifier', 'origin': 'Reference', 'admitSource': 'CodeableConcept', 'reAdmission': 'CodeableConcept', 'dietPreference': 'CodeableConcept', 'specialCourtesy': 'CodeableConcept', 'specialArrangement': 'CodeableConcept', 'destination': 'Reference', 'dischargeDisposition': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    preAdmissionIdentifier: Optional[Identifier]
    origin: Optional[Reference]
    admitSource: Optional[CodeableConcept]
    reAdmission: Optional[CodeableConcept]
    dietPreference: CodeableConcept | FHIRList[CodeableConcept]
    specialCourtesy: CodeableConcept | FHIRList[CodeableConcept]
    specialArrangement: CodeableConcept | FHIRList[CodeableConcept]
    destination: Optional[Reference]
    dischargeDisposition: Optional[CodeableConcept]


class EncounterLocation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'location': 'Reference', 'physicalType': 'CodeableConcept', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    location: Optional[Reference]
    status: Optional[Code] = None
    physicalType: Optional[CodeableConcept]
    period: Optional[Period]


class Encounter(FHIRResource):
    _resource_type = "Encounter"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'statusHistory', 'classHistory', 'type_', 'episodeOfCare', 'basedOn', 'participant', 'appointment', 'reasonCode', 'reasonReference', 'diagnosis', 'account', 'location'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'statusHistory': 'EncounterStatusHistory', 'class_': 'Coding', 'classHistory': 'EncounterClassHistory', 'type_': 'CodeableConcept', 'serviceType': 'CodeableConcept', 'priority': 'CodeableConcept', 'subject': 'Reference', 'episodeOfCare': 'Reference', 'basedOn': 'Reference', 'participant': 'EncounterParticipant', 'appointment': 'Reference', 'period': 'Period', 'length': 'Duration', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'diagnosis': 'EncounterDiagnosis', 'account': 'Reference', 'hospitalization': 'EncounterHospitalization', 'location': 'EncounterLocation', 'serviceProvider': 'Reference', 'partOf': 'Reference'}

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
    statusHistory: EncounterStatusHistory | FHIRList[EncounterStatusHistory]
    class_: Optional[Coding]
    classHistory: EncounterClassHistory | FHIRList[EncounterClassHistory]
    type_: CodeableConcept | FHIRList[CodeableConcept]
    serviceType: Optional[CodeableConcept]
    priority: Optional[CodeableConcept]
    subject: Optional[Reference]
    episodeOfCare: Reference | FHIRList[Reference]
    basedOn: Reference | FHIRList[Reference]
    participant: EncounterParticipant | FHIRList[EncounterParticipant]
    appointment: Reference | FHIRList[Reference]
    period: Optional[Period]
    length: Optional[Duration]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    diagnosis: EncounterDiagnosis | FHIRList[EncounterDiagnosis]
    account: Reference | FHIRList[Reference]
    hospitalization: Optional[EncounterHospitalization]
    location: EncounterLocation | FHIRList[EncounterLocation]
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


class EpisodeOfCareStatusHistory(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    status: Optional[Code] = None
    period: Optional[Period]


class EpisodeOfCareDiagnosis(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'condition': 'Reference', 'role': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    condition: Optional[Reference]
    role: Optional[CodeableConcept]
    rank: Optional[PositiveInt] = None


class EpisodeOfCare(FHIRResource):
    _resource_type = "EpisodeOfCare"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'statusHistory', 'type_', 'diagnosis', 'referralRequest', 'team', 'account'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'statusHistory': 'EpisodeOfCareStatusHistory', 'type_': 'CodeableConcept', 'diagnosis': 'EpisodeOfCareDiagnosis', 'patient': 'Reference', 'managingOrganization': 'Reference', 'period': 'Period', 'referralRequest': 'Reference', 'careManager': 'Reference', 'team': 'Reference', 'account': 'Reference'}

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
    statusHistory: EpisodeOfCareStatusHistory | FHIRList[EpisodeOfCareStatusHistory]
    type_: CodeableConcept | FHIRList[CodeableConcept]
    diagnosis: EpisodeOfCareDiagnosis | FHIRList[EpisodeOfCareDiagnosis]
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
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'subjectCodeableConcept': 'CodeableConcept', 'subjectReference': 'Reference', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'trigger': 'TriggerDefinition'}
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

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
    subjectCodeableConcept: Optional[CodeableConcept]
    subjectReference: Optional[Reference]
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


class EvidenceVariableCharacteristic(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'usageContext'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'definitionReference': 'Reference', 'definitionCodeableConcept': 'CodeableConcept', 'definitionExpression': 'Expression', 'definitionDataRequirement': 'DataRequirement', 'definitionTriggerDefinition': 'TriggerDefinition', 'usageContext': 'UsageContext', 'participantEffectivePeriod': 'Period', 'participantEffectiveDuration': 'Duration', 'participantEffectiveTiming': 'Timing', 'timeFromStart': 'Duration'}
    _choice_fields = {'definition': ['definitionReference', 'definitionCanonical', 'definitionCodeableConcept', 'definitionExpression', 'definitionDataRequirement', 'definitionTriggerDefinition'], 'participantEffective': ['participantEffectiveDateTime', 'participantEffectivePeriod', 'participantEffectiveDuration', 'participantEffectiveTiming']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    description: Optional[String] = None
    definitionReference: Optional[Reference]
    definitionCanonical: Optional[Canonical] = None
    definitionCodeableConcept: Optional[CodeableConcept]
    definitionExpression: Optional[Expression]
    definitionDataRequirement: Optional[DataRequirement]
    definitionTriggerDefinition: Optional[TriggerDefinition]
    usageContext: UsageContext | FHIRList[UsageContext]
    exclude: Optional[Boolean] = None
    participantEffectiveDateTime: Optional[DateTime] = None
    participantEffectivePeriod: Optional[Period]
    participantEffectiveDuration: Optional[Duration]
    participantEffectiveTiming: Optional[Timing]
    timeFromStart: Optional[Duration]
    groupMeasure: Optional[Code] = None


class EvidenceVariable(FHIRResource):
    _resource_type = "EvidenceVariable"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'note', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'characteristic'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'note': 'Annotation', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'characteristic': 'EvidenceVariableCharacteristic'}

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
    type_: Optional[Code] = None
    characteristic: EvidenceVariableCharacteristic | FHIRList[EvidenceVariableCharacteristic]


class ExampleScenarioActor(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    actorId: Optional[String] = None
    type_: Optional[Code] = None
    name: Optional[String] = None
    description: Optional[Markdown] = None


class ExampleScenarioInstance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'version', 'containedInstance'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'version': 'ExampleScenarioInstanceVersion', 'containedInstance': 'ExampleScenarioInstanceContainedInstance'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    resourceId: Optional[String] = None
    resourceType: Optional[Code] = None
    name: Optional[String] = None
    description: Optional[Markdown] = None
    version: ExampleScenarioInstanceVersion | FHIRList[ExampleScenarioInstanceVersion]
    containedInstance: ExampleScenarioInstanceContainedInstance | FHIRList[ExampleScenarioInstanceContainedInstance]


class ExampleScenarioInstanceVersion(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    versionId: Optional[String] = None
    description: Optional[Markdown] = None


class ExampleScenarioInstanceContainedInstance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    resourceId: Optional[String] = None
    versionId: Optional[String] = None


class ExampleScenarioProcess(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'step'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'step': 'ExampleScenarioProcessStep'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    title: Optional[String] = None
    description: Optional[Markdown] = None
    preConditions: Optional[Markdown] = None
    postConditions: Optional[Markdown] = None
    step: ExampleScenarioProcessStep | FHIRList[ExampleScenarioProcessStep]


class ExampleScenarioProcessStep(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'process', 'alternative'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'operation': 'ExampleScenarioProcessStepOperation', 'alternative': 'ExampleScenarioProcessStepAlternative'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    process: Any = None
    pause: Optional[Boolean] = None
    operation: Optional[ExampleScenarioProcessStepOperation]
    alternative: ExampleScenarioProcessStepAlternative | FHIRList[ExampleScenarioProcessStepAlternative]


class ExampleScenarioProcessStepOperation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    number: Optional[String] = None
    type_: Optional[String] = None
    name: Optional[String] = None
    initiator: Optional[String] = None
    receiver: Optional[String] = None
    description: Optional[Markdown] = None
    initiatorActive: Optional[Boolean] = None
    receiverActive: Optional[Boolean] = None
    request: Any = None
    response: Any = None


class ExampleScenarioProcessStepAlternative(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'step'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    title: Optional[String] = None
    description: Optional[Markdown] = None
    step: Any = None


class ExampleScenario(FHIRResource):
    _resource_type = "ExampleScenario"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'actor', 'instance', 'process', 'workflow'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'actor': 'ExampleScenarioActor', 'instance': 'ExampleScenarioInstance', 'process': 'ExampleScenarioProcess'}

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
    actor: ExampleScenarioActor | FHIRList[ExampleScenarioActor]
    instance: ExampleScenarioInstance | FHIRList[ExampleScenarioInstance]
    process: ExampleScenarioProcess | FHIRList[ExampleScenarioProcess]
    workflow: Canonical | FHIRList[Canonical] = None


class ExplanationOfBenefitRelated(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'claim': 'Reference', 'relationship': 'CodeableConcept', 'reference': 'Identifier'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    claim: Optional[Reference]
    relationship: Optional[CodeableConcept]
    reference: Optional[Identifier]


class ExplanationOfBenefitPayee(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'party': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    party: Optional[Reference]


class ExplanationOfBenefitCareTeam(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'provider': 'Reference', 'role': 'CodeableConcept', 'qualification': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequence: Optional[PositiveInt] = None
    provider: Optional[Reference]
    responsible: Optional[Boolean] = None
    role: Optional[CodeableConcept]
    qualification: Optional[CodeableConcept]


class ExplanationOfBenefitSupportingInfo(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'timingPeriod': 'Period', 'valueQuantity': 'Quantity', 'valueAttachment': 'Attachment', 'valueReference': 'Reference', 'reason': 'Coding'}
    _choice_fields = {'timing': ['timingDate', 'timingPeriod'], 'value': ['valueBoolean', 'valueString', 'valueQuantity', 'valueAttachment', 'valueReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequence: Optional[PositiveInt] = None
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    timingDate: Optional[Date] = None
    timingPeriod: Optional[Period]
    valueBoolean: Optional[Boolean] = None
    valueString: Optional[String] = None
    valueQuantity: Optional[Quantity]
    valueAttachment: Optional[Attachment]
    valueReference: Optional[Reference]
    reason: Optional[Coding]


class ExplanationOfBenefitDiagnosis(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'type_'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'diagnosisCodeableConcept': 'CodeableConcept', 'diagnosisReference': 'Reference', 'type_': 'CodeableConcept', 'onAdmission': 'CodeableConcept', 'packageCode': 'CodeableConcept'}
    _choice_fields = {'diagnosis': ['diagnosisCodeableConcept', 'diagnosisReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequence: Optional[PositiveInt] = None
    diagnosisCodeableConcept: Optional[CodeableConcept]
    diagnosisReference: Optional[Reference]
    type_: CodeableConcept | FHIRList[CodeableConcept]
    onAdmission: Optional[CodeableConcept]
    packageCode: Optional[CodeableConcept]


class ExplanationOfBenefitProcedure(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'type_', 'udi'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'procedureCodeableConcept': 'CodeableConcept', 'procedureReference': 'Reference', 'udi': 'Reference'}
    _choice_fields = {'procedure': ['procedureCodeableConcept', 'procedureReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequence: Optional[PositiveInt] = None
    type_: CodeableConcept | FHIRList[CodeableConcept]
    date: Optional[DateTime] = None
    procedureCodeableConcept: Optional[CodeableConcept]
    procedureReference: Optional[Reference]
    udi: Reference | FHIRList[Reference]


class ExplanationOfBenefitInsurance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'preAuthRef'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'coverage': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    focal: Optional[Boolean] = None
    coverage: Optional[Reference]
    preAuthRef: String | FHIRList[String] = None


class ExplanationOfBenefitAccident(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'locationAddress': 'Address', 'locationReference': 'Reference'}
    _choice_fields = {'location': ['locationAddress', 'locationReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    date: Optional[Date] = None
    type_: Optional[CodeableConcept]
    locationAddress: Optional[Address]
    locationReference: Optional[Reference]


class ExplanationOfBenefitItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'careTeamSequence', 'diagnosisSequence', 'procedureSequence', 'informationSequence', 'modifier', 'programCode', 'udi', 'subSite', 'encounter', 'noteNumber', 'adjudication', 'detail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'revenue': 'CodeableConcept', 'category': 'CodeableConcept', 'productOrService': 'CodeableConcept', 'modifier': 'CodeableConcept', 'programCode': 'CodeableConcept', 'servicedPeriod': 'Period', 'locationCodeableConcept': 'CodeableConcept', 'locationAddress': 'Address', 'locationReference': 'Reference', 'quantity': 'Quantity', 'unitPrice': 'Money', 'net': 'Money', 'udi': 'Reference', 'bodySite': 'CodeableConcept', 'subSite': 'CodeableConcept', 'encounter': 'Reference', 'adjudication': 'ExplanationOfBenefitItemAdjudication', 'detail': 'ExplanationOfBenefitItemDetail'}
    _choice_fields = {'location': ['locationCodeableConcept', 'locationAddress', 'locationReference'], 'serviced': ['servicedDate', 'servicedPeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequence: Optional[PositiveInt] = None
    careTeamSequence: PositiveInt | FHIRList[PositiveInt] = None
    diagnosisSequence: PositiveInt | FHIRList[PositiveInt] = None
    procedureSequence: PositiveInt | FHIRList[PositiveInt] = None
    informationSequence: PositiveInt | FHIRList[PositiveInt] = None
    revenue: Optional[CodeableConcept]
    category: Optional[CodeableConcept]
    productOrService: Optional[CodeableConcept]
    modifier: CodeableConcept | FHIRList[CodeableConcept]
    programCode: CodeableConcept | FHIRList[CodeableConcept]
    servicedDate: Optional[Date] = None
    servicedPeriod: Optional[Period]
    locationCodeableConcept: Optional[CodeableConcept]
    locationAddress: Optional[Address]
    locationReference: Optional[Reference]
    quantity: Optional[Quantity]
    unitPrice: Optional[Money]
    factor: Optional[Decimal] = None
    net: Optional[Money]
    udi: Reference | FHIRList[Reference]
    bodySite: Optional[CodeableConcept]
    subSite: CodeableConcept | FHIRList[CodeableConcept]
    encounter: Reference | FHIRList[Reference]
    noteNumber: PositiveInt | FHIRList[PositiveInt] = None
    adjudication: ExplanationOfBenefitItemAdjudication | FHIRList[ExplanationOfBenefitItemAdjudication]
    detail: ExplanationOfBenefitItemDetail | FHIRList[ExplanationOfBenefitItemDetail]


class ExplanationOfBenefitItemAdjudication(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'category': 'CodeableConcept', 'reason': 'CodeableConcept', 'amount': 'Money'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    category: Optional[CodeableConcept]
    reason: Optional[CodeableConcept]
    amount: Optional[Money]
    value: Optional[Decimal] = None


class ExplanationOfBenefitItemDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'modifier', 'programCode', 'udi', 'noteNumber', 'adjudication', 'subDetail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'revenue': 'CodeableConcept', 'category': 'CodeableConcept', 'productOrService': 'CodeableConcept', 'modifier': 'CodeableConcept', 'programCode': 'CodeableConcept', 'quantity': 'Quantity', 'unitPrice': 'Money', 'net': 'Money', 'udi': 'Reference', 'subDetail': 'ExplanationOfBenefitItemDetailSubDetail'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequence: Optional[PositiveInt] = None
    revenue: Optional[CodeableConcept]
    category: Optional[CodeableConcept]
    productOrService: Optional[CodeableConcept]
    modifier: CodeableConcept | FHIRList[CodeableConcept]
    programCode: CodeableConcept | FHIRList[CodeableConcept]
    quantity: Optional[Quantity]
    unitPrice: Optional[Money]
    factor: Optional[Decimal] = None
    net: Optional[Money]
    udi: Reference | FHIRList[Reference]
    noteNumber: PositiveInt | FHIRList[PositiveInt] = None
    adjudication: Any = None
    subDetail: ExplanationOfBenefitItemDetailSubDetail | FHIRList[ExplanationOfBenefitItemDetailSubDetail]


class ExplanationOfBenefitItemDetailSubDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'modifier', 'programCode', 'udi', 'noteNumber', 'adjudication'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'revenue': 'CodeableConcept', 'category': 'CodeableConcept', 'productOrService': 'CodeableConcept', 'modifier': 'CodeableConcept', 'programCode': 'CodeableConcept', 'quantity': 'Quantity', 'unitPrice': 'Money', 'net': 'Money', 'udi': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequence: Optional[PositiveInt] = None
    revenue: Optional[CodeableConcept]
    category: Optional[CodeableConcept]
    productOrService: Optional[CodeableConcept]
    modifier: CodeableConcept | FHIRList[CodeableConcept]
    programCode: CodeableConcept | FHIRList[CodeableConcept]
    quantity: Optional[Quantity]
    unitPrice: Optional[Money]
    factor: Optional[Decimal] = None
    net: Optional[Money]
    udi: Reference | FHIRList[Reference]
    noteNumber: PositiveInt | FHIRList[PositiveInt] = None
    adjudication: Any = None


class ExplanationOfBenefitAddItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'itemSequence', 'detailSequence', 'subDetailSequence', 'provider', 'modifier', 'programCode', 'subSite', 'noteNumber', 'adjudication', 'detail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'provider': 'Reference', 'productOrService': 'CodeableConcept', 'modifier': 'CodeableConcept', 'programCode': 'CodeableConcept', 'servicedPeriod': 'Period', 'locationCodeableConcept': 'CodeableConcept', 'locationAddress': 'Address', 'locationReference': 'Reference', 'quantity': 'Quantity', 'unitPrice': 'Money', 'net': 'Money', 'bodySite': 'CodeableConcept', 'subSite': 'CodeableConcept', 'detail': 'ExplanationOfBenefitAddItemDetail'}
    _choice_fields = {'location': ['locationCodeableConcept', 'locationAddress', 'locationReference'], 'serviced': ['servicedDate', 'servicedPeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    itemSequence: PositiveInt | FHIRList[PositiveInt] = None
    detailSequence: PositiveInt | FHIRList[PositiveInt] = None
    subDetailSequence: PositiveInt | FHIRList[PositiveInt] = None
    provider: Reference | FHIRList[Reference]
    productOrService: Optional[CodeableConcept]
    modifier: CodeableConcept | FHIRList[CodeableConcept]
    programCode: CodeableConcept | FHIRList[CodeableConcept]
    servicedDate: Optional[Date] = None
    servicedPeriod: Optional[Period]
    locationCodeableConcept: Optional[CodeableConcept]
    locationAddress: Optional[Address]
    locationReference: Optional[Reference]
    quantity: Optional[Quantity]
    unitPrice: Optional[Money]
    factor: Optional[Decimal] = None
    net: Optional[Money]
    bodySite: Optional[CodeableConcept]
    subSite: CodeableConcept | FHIRList[CodeableConcept]
    noteNumber: PositiveInt | FHIRList[PositiveInt] = None
    adjudication: Any = None
    detail: ExplanationOfBenefitAddItemDetail | FHIRList[ExplanationOfBenefitAddItemDetail]


class ExplanationOfBenefitAddItemDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'modifier', 'noteNumber', 'adjudication', 'subDetail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'productOrService': 'CodeableConcept', 'modifier': 'CodeableConcept', 'quantity': 'Quantity', 'unitPrice': 'Money', 'net': 'Money', 'subDetail': 'ExplanationOfBenefitAddItemDetailSubDetail'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    productOrService: Optional[CodeableConcept]
    modifier: CodeableConcept | FHIRList[CodeableConcept]
    quantity: Optional[Quantity]
    unitPrice: Optional[Money]
    factor: Optional[Decimal] = None
    net: Optional[Money]
    noteNumber: PositiveInt | FHIRList[PositiveInt] = None
    adjudication: Any = None
    subDetail: ExplanationOfBenefitAddItemDetailSubDetail | FHIRList[ExplanationOfBenefitAddItemDetailSubDetail]


class ExplanationOfBenefitAddItemDetailSubDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'modifier', 'noteNumber', 'adjudication'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'productOrService': 'CodeableConcept', 'modifier': 'CodeableConcept', 'quantity': 'Quantity', 'unitPrice': 'Money', 'net': 'Money'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    productOrService: Optional[CodeableConcept]
    modifier: CodeableConcept | FHIRList[CodeableConcept]
    quantity: Optional[Quantity]
    unitPrice: Optional[Money]
    factor: Optional[Decimal] = None
    net: Optional[Money]
    noteNumber: PositiveInt | FHIRList[PositiveInt] = None
    adjudication: Any = None


class ExplanationOfBenefitTotal(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'category': 'CodeableConcept', 'amount': 'Money'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    category: Optional[CodeableConcept]
    amount: Optional[Money]


class ExplanationOfBenefitPayment(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'adjustment': 'Money', 'adjustmentReason': 'CodeableConcept', 'amount': 'Money', 'identifier': 'Identifier'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    adjustment: Optional[Money]
    adjustmentReason: Optional[CodeableConcept]
    date: Optional[Date] = None
    amount: Optional[Money]
    identifier: Optional[Identifier]


class ExplanationOfBenefitProcessNote(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'language': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    number: Optional[PositiveInt] = None
    type_: Optional[Code] = None
    text: Optional[String] = None
    language: Optional[CodeableConcept]


class ExplanationOfBenefitBenefitBalance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'financial'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'category': 'CodeableConcept', 'network': 'CodeableConcept', 'unit': 'CodeableConcept', 'term': 'CodeableConcept', 'financial': 'ExplanationOfBenefitBenefitBalanceFinancial'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    category: Optional[CodeableConcept]
    excluded: Optional[Boolean] = None
    name: Optional[String] = None
    description: Optional[String] = None
    network: Optional[CodeableConcept]
    unit: Optional[CodeableConcept]
    term: Optional[CodeableConcept]
    financial: ExplanationOfBenefitBenefitBalanceFinancial | FHIRList[ExplanationOfBenefitBenefitBalanceFinancial]


class ExplanationOfBenefitBenefitBalanceFinancial(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'allowedMoney': 'Money', 'usedMoney': 'Money'}
    _choice_fields = {'allowed': ['allowedUnsignedInt', 'allowedString', 'allowedMoney'], 'used': ['usedUnsignedInt', 'usedMoney']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    allowedUnsignedInt: Optional[UnsignedInt] = None
    allowedString: Optional[String] = None
    allowedMoney: Optional[Money]
    usedUnsignedInt: Optional[UnsignedInt] = None
    usedMoney: Optional[Money]


class ExplanationOfBenefit(FHIRResource):
    _resource_type = "ExplanationOfBenefit"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'related', 'preAuthRef', 'preAuthRefPeriod', 'careTeam', 'supportingInfo', 'diagnosis', 'procedure', 'insurance', 'item', 'addItem', 'adjudication', 'total', 'processNote', 'benefitBalance'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'subType': 'CodeableConcept', 'patient': 'Reference', 'billablePeriod': 'Period', 'enterer': 'Reference', 'insurer': 'Reference', 'provider': 'Reference', 'priority': 'CodeableConcept', 'fundsReserveRequested': 'CodeableConcept', 'fundsReserve': 'CodeableConcept', 'related': 'ExplanationOfBenefitRelated', 'prescription': 'Reference', 'originalPrescription': 'Reference', 'payee': 'ExplanationOfBenefitPayee', 'referral': 'Reference', 'facility': 'Reference', 'claim': 'Reference', 'claimResponse': 'Reference', 'preAuthRefPeriod': 'Period', 'careTeam': 'ExplanationOfBenefitCareTeam', 'supportingInfo': 'ExplanationOfBenefitSupportingInfo', 'diagnosis': 'ExplanationOfBenefitDiagnosis', 'procedure': 'ExplanationOfBenefitProcedure', 'insurance': 'ExplanationOfBenefitInsurance', 'accident': 'ExplanationOfBenefitAccident', 'item': 'ExplanationOfBenefitItem', 'addItem': 'ExplanationOfBenefitAddItem', 'total': 'ExplanationOfBenefitTotal', 'payment': 'ExplanationOfBenefitPayment', 'formCode': 'CodeableConcept', 'form': 'Attachment', 'processNote': 'ExplanationOfBenefitProcessNote', 'benefitPeriod': 'Period', 'benefitBalance': 'ExplanationOfBenefitBenefitBalance'}

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
    type_: Optional[CodeableConcept]
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
    related: ExplanationOfBenefitRelated | FHIRList[ExplanationOfBenefitRelated]
    prescription: Optional[Reference]
    originalPrescription: Optional[Reference]
    payee: Optional[ExplanationOfBenefitPayee]
    referral: Optional[Reference]
    facility: Optional[Reference]
    claim: Optional[Reference]
    claimResponse: Optional[Reference]
    outcome: Optional[Code] = None
    disposition: Optional[String] = None
    preAuthRef: String | FHIRList[String] = None
    preAuthRefPeriod: Period | FHIRList[Period]
    careTeam: ExplanationOfBenefitCareTeam | FHIRList[ExplanationOfBenefitCareTeam]
    supportingInfo: ExplanationOfBenefitSupportingInfo | FHIRList[ExplanationOfBenefitSupportingInfo]
    diagnosis: ExplanationOfBenefitDiagnosis | FHIRList[ExplanationOfBenefitDiagnosis]
    procedure: ExplanationOfBenefitProcedure | FHIRList[ExplanationOfBenefitProcedure]
    precedence: Optional[PositiveInt] = None
    insurance: ExplanationOfBenefitInsurance | FHIRList[ExplanationOfBenefitInsurance]
    accident: Optional[ExplanationOfBenefitAccident]
    item: ExplanationOfBenefitItem | FHIRList[ExplanationOfBenefitItem]
    addItem: ExplanationOfBenefitAddItem | FHIRList[ExplanationOfBenefitAddItem]
    adjudication: Any = None
    total: ExplanationOfBenefitTotal | FHIRList[ExplanationOfBenefitTotal]
    payment: Optional[ExplanationOfBenefitPayment]
    formCode: Optional[CodeableConcept]
    form: Optional[Attachment]
    processNote: ExplanationOfBenefitProcessNote | FHIRList[ExplanationOfBenefitProcessNote]
    benefitPeriod: Optional[Period]
    benefitBalance: ExplanationOfBenefitBenefitBalance | FHIRList[ExplanationOfBenefitBenefitBalance]


class FamilyMemberHistoryCondition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'note'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'outcome': 'CodeableConcept', 'onsetAge': 'Age', 'onsetRange': 'Range', 'onsetPeriod': 'Period', 'note': 'Annotation'}
    _choice_fields = {'onset': ['onsetAge', 'onsetRange', 'onsetPeriod', 'onsetString']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    outcome: Optional[CodeableConcept]
    contributedToDeath: Optional[Boolean] = None
    onsetAge: Optional[Age]
    onsetRange: Optional[Range]
    onsetPeriod: Optional[Period]
    onsetString: Optional[String] = None
    note: Annotation | FHIRList[Annotation]


class FamilyMemberHistory(FHIRResource):
    _resource_type = "FamilyMemberHistory"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'instantiatesCanonical', 'instantiatesUri', 'reasonCode', 'reasonReference', 'note', 'condition'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'dataAbsentReason': 'CodeableConcept', 'patient': 'Reference', 'relationship': 'CodeableConcept', 'sex': 'CodeableConcept', 'bornPeriod': 'Period', 'ageAge': 'Age', 'ageRange': 'Range', 'deceasedAge': 'Age', 'deceasedRange': 'Range', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'note': 'Annotation', 'condition': 'FamilyMemberHistoryCondition'}
    _choice_fields = {'age': ['ageAge', 'ageRange', 'ageString'], 'born': ['bornPeriod', 'bornDate', 'bornString'], 'deceased': ['deceasedBoolean', 'deceasedAge', 'deceasedRange', 'deceasedDate', 'deceasedString']}

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
    bornPeriod: Optional[Period]
    bornDate: Optional[Date] = None
    bornString: Optional[String] = None
    ageAge: Optional[Age]
    ageRange: Optional[Range]
    ageString: Optional[String] = None
    estimatedAge: Optional[Boolean] = None
    deceasedBoolean: Optional[Boolean] = None
    deceasedAge: Optional[Age]
    deceasedRange: Optional[Range]
    deceasedDate: Optional[Date] = None
    deceasedString: Optional[String] = None
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]
    condition: FamilyMemberHistoryCondition | FHIRList[FamilyMemberHistoryCondition]


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


class GoalTarget(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'measure': 'CodeableConcept', 'detailQuantity': 'Quantity', 'detailRange': 'Range', 'detailCodeableConcept': 'CodeableConcept', 'detailRatio': 'Ratio', 'dueDuration': 'Duration'}
    _choice_fields = {'detail': ['detailQuantity', 'detailRange', 'detailCodeableConcept', 'detailString', 'detailBoolean', 'detailInteger', 'detailRatio'], 'due': ['dueDate', 'dueDuration']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    measure: Optional[CodeableConcept]
    detailQuantity: Optional[Quantity]
    detailRange: Optional[Range]
    detailCodeableConcept: Optional[CodeableConcept]
    detailString: Optional[String] = None
    detailBoolean: Optional[Boolean] = None
    detailInteger: Optional[Integer] = None
    detailRatio: Optional[Ratio]
    dueDate: Optional[Date] = None
    dueDuration: Optional[Duration]


class Goal(FHIRResource):
    _resource_type = "Goal"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'target', 'addresses', 'note', 'outcomeCode', 'outcomeReference'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'achievementStatus': 'CodeableConcept', 'category': 'CodeableConcept', 'priority': 'CodeableConcept', 'description': 'CodeableConcept', 'subject': 'Reference', 'startCodeableConcept': 'CodeableConcept', 'target': 'GoalTarget', 'expressedBy': 'Reference', 'addresses': 'Reference', 'note': 'Annotation', 'outcomeCode': 'CodeableConcept', 'outcomeReference': 'Reference'}
    _choice_fields = {'start': ['startDate', 'startCodeableConcept']}

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
    startDate: Optional[Date] = None
    startCodeableConcept: Optional[CodeableConcept]
    target: GoalTarget | FHIRList[GoalTarget]
    statusDate: Optional[Date] = None
    statusReason: Optional[String] = None
    expressedBy: Optional[Reference]
    addresses: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]
    outcomeCode: CodeableConcept | FHIRList[CodeableConcept]
    outcomeReference: Reference | FHIRList[Reference]


class GraphDefinitionLink(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'target'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'target': 'GraphDefinitionLinkTarget'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    path: Optional[String] = None
    sliceName: Optional[String] = None
    min: Optional[Integer] = None
    max: Optional[String] = None
    description: Optional[String] = None
    target: GraphDefinitionLinkTarget | FHIRList[GraphDefinitionLinkTarget]


class GraphDefinitionLinkTarget(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'compartment', 'link'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'compartment': 'GraphDefinitionLinkTargetCompartment'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    params: Optional[String] = None
    profile: Optional[Canonical] = None
    compartment: GraphDefinitionLinkTargetCompartment | FHIRList[GraphDefinitionLinkTargetCompartment]
    link: Any = None


class GraphDefinitionLinkTargetCompartment(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    use: Optional[Code] = None
    code: Optional[Code] = None
    rule: Optional[Code] = None
    expression: Optional[String] = None
    description: Optional[String] = None


class GraphDefinition(FHIRResource):
    _resource_type = "GraphDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'link'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'link': 'GraphDefinitionLink'}

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
    link: GraphDefinitionLink | FHIRList[GraphDefinitionLink]


class GroupCharacteristic(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueCodeableConcept': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueRange': 'Range', 'valueReference': 'Reference', 'period': 'Period'}
    _choice_fields = {'value': ['valueCodeableConcept', 'valueBoolean', 'valueQuantity', 'valueRange', 'valueReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueCodeableConcept: Optional[CodeableConcept]
    valueBoolean: Optional[Boolean] = None
    valueQuantity: Optional[Quantity]
    valueRange: Optional[Range]
    valueReference: Optional[Reference]
    exclude: Optional[Boolean] = None
    period: Optional[Period]


class GroupMember(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'entity': 'Reference', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    entity: Optional[Reference]
    period: Optional[Period]
    inactive: Optional[Boolean] = None


class Group(FHIRResource):
    _resource_type = "Group"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'characteristic', 'member'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'code': 'CodeableConcept', 'managingEntity': 'Reference', 'characteristic': 'GroupCharacteristic', 'member': 'GroupMember'}

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
    type_: Optional[Code] = None
    actual: Optional[Boolean] = None
    code: Optional[CodeableConcept]
    name: Optional[String] = None
    quantity: Optional[UnsignedInt] = None
    managingEntity: Optional[Reference]
    characteristic: GroupCharacteristic | FHIRList[GroupCharacteristic]
    member: GroupMember | FHIRList[GroupMember]


class GuidanceResponse(FHIRResource):
    _resource_type = "GuidanceResponse"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'reasonCode', 'reasonReference', 'note', 'evaluationMessage', 'dataRequirement'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'requestIdentifier': 'Identifier', 'identifier': 'Identifier', 'moduleCodeableConcept': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'note': 'Annotation', 'evaluationMessage': 'Reference', 'outputParameters': 'Reference', 'result': 'Reference', 'dataRequirement': 'DataRequirement'}
    _choice_fields = {'module': ['moduleUri', 'moduleCanonical', 'moduleCodeableConcept']}

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
    moduleUri: Optional[Uri] = None
    moduleCanonical: Optional[Canonical] = None
    moduleCodeableConcept: Optional[CodeableConcept]
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


class HealthcareServiceEligibility(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    comment: Optional[Markdown] = None


class HealthcareServiceAvailableTime(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'daysOfWeek'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    daysOfWeek: Code | FHIRList[Code] = None
    allDay: Optional[Boolean] = None
    availableStartTime: Optional[Time] = None
    availableEndTime: Optional[Time] = None


class HealthcareServiceNotAvailable(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'during': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    description: Optional[String] = None
    during: Optional[Period]


class HealthcareService(FHIRResource):
    _resource_type = "HealthcareService"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'type_', 'specialty', 'location', 'telecom', 'coverageArea', 'serviceProvisionCode', 'eligibility', 'program', 'characteristic', 'communication', 'referralMethod', 'availableTime', 'notAvailable', 'endpoint'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'providedBy': 'Reference', 'category': 'CodeableConcept', 'type_': 'CodeableConcept', 'specialty': 'CodeableConcept', 'location': 'Reference', 'photo': 'Attachment', 'telecom': 'ContactPoint', 'coverageArea': 'Reference', 'serviceProvisionCode': 'CodeableConcept', 'eligibility': 'HealthcareServiceEligibility', 'program': 'CodeableConcept', 'characteristic': 'CodeableConcept', 'communication': 'CodeableConcept', 'referralMethod': 'CodeableConcept', 'availableTime': 'HealthcareServiceAvailableTime', 'notAvailable': 'HealthcareServiceNotAvailable', 'endpoint': 'Reference'}

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
    type_: CodeableConcept | FHIRList[CodeableConcept]
    specialty: CodeableConcept | FHIRList[CodeableConcept]
    location: Reference | FHIRList[Reference]
    name: Optional[String] = None
    comment: Optional[String] = None
    extraDetails: Optional[Markdown] = None
    photo: Optional[Attachment]
    telecom: ContactPoint | FHIRList[ContactPoint]
    coverageArea: Reference | FHIRList[Reference]
    serviceProvisionCode: CodeableConcept | FHIRList[CodeableConcept]
    eligibility: HealthcareServiceEligibility | FHIRList[HealthcareServiceEligibility]
    program: CodeableConcept | FHIRList[CodeableConcept]
    characteristic: CodeableConcept | FHIRList[CodeableConcept]
    communication: CodeableConcept | FHIRList[CodeableConcept]
    referralMethod: CodeableConcept | FHIRList[CodeableConcept]
    appointmentRequired: Optional[Boolean] = None
    availableTime: HealthcareServiceAvailableTime | FHIRList[HealthcareServiceAvailableTime]
    notAvailable: HealthcareServiceNotAvailable | FHIRList[HealthcareServiceNotAvailable]
    availabilityExceptions: Optional[String] = None
    endpoint: Reference | FHIRList[Reference]


class ImagingStudySeries(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'endpoint', 'specimen', 'performer', 'instance'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'modality': 'Coding', 'endpoint': 'Reference', 'bodySite': 'Coding', 'laterality': 'Coding', 'specimen': 'Reference', 'performer': 'ImagingStudySeriesPerformer', 'instance': 'ImagingStudySeriesInstance'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    uid: Optional[Id] = None
    number: Optional[UnsignedInt] = None
    modality: Optional[Coding]
    description: Optional[String] = None
    numberOfInstances: Optional[UnsignedInt] = None
    endpoint: Reference | FHIRList[Reference]
    bodySite: Optional[Coding]
    laterality: Optional[Coding]
    specimen: Reference | FHIRList[Reference]
    started: Optional[DateTime] = None
    performer: ImagingStudySeriesPerformer | FHIRList[ImagingStudySeriesPerformer]
    instance: ImagingStudySeriesInstance | FHIRList[ImagingStudySeriesInstance]


class ImagingStudySeriesPerformer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'function': 'CodeableConcept', 'actor': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    function: Optional[CodeableConcept]
    actor: Optional[Reference]


class ImagingStudySeriesInstance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'sopClass': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    uid: Optional[Id] = None
    sopClass: Optional[Coding]
    number: Optional[UnsignedInt] = None
    title: Optional[String] = None


class ImagingStudy(FHIRResource):
    _resource_type = "ImagingStudy"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'modality', 'basedOn', 'interpreter', 'endpoint', 'procedureCode', 'reasonCode', 'reasonReference', 'note', 'series'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'modality': 'Coding', 'subject': 'Reference', 'encounter': 'Reference', 'basedOn': 'Reference', 'referrer': 'Reference', 'interpreter': 'Reference', 'endpoint': 'Reference', 'procedureReference': 'Reference', 'procedureCode': 'CodeableConcept', 'location': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'note': 'Annotation', 'series': 'ImagingStudySeries'}

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
    series: ImagingStudySeries | FHIRList[ImagingStudySeries]


class ImmunizationPerformer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'function': 'CodeableConcept', 'actor': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    function: Optional[CodeableConcept]
    actor: Optional[Reference]


class ImmunizationEducation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    documentType: Optional[String] = None
    reference: Optional[Uri] = None
    publicationDate: Optional[DateTime] = None
    presentationDate: Optional[DateTime] = None


class ImmunizationReaction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'detail': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    date: Optional[DateTime] = None
    detail: Optional[Reference]
    reported: Optional[Boolean] = None


class ImmunizationProtocolApplied(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'targetDisease'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'authority': 'Reference', 'targetDisease': 'CodeableConcept'}
    _choice_fields = {'doseNumber': ['doseNumberPositiveInt', 'doseNumberString'], 'seriesDoses': ['seriesDosesPositiveInt', 'seriesDosesString']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    series: Optional[String] = None
    authority: Optional[Reference]
    targetDisease: CodeableConcept | FHIRList[CodeableConcept]
    doseNumberPositiveInt: Optional[PositiveInt] = None
    doseNumberString: Optional[String] = None
    seriesDosesPositiveInt: Optional[PositiveInt] = None
    seriesDosesString: Optional[String] = None


class Immunization(FHIRResource):
    _resource_type = "Immunization"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'performer', 'note', 'reasonCode', 'reasonReference', 'subpotentReason', 'education', 'programEligibility', 'reaction', 'protocolApplied'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'statusReason': 'CodeableConcept', 'vaccineCode': 'CodeableConcept', 'patient': 'Reference', 'encounter': 'Reference', 'reportOrigin': 'CodeableConcept', 'location': 'Reference', 'manufacturer': 'Reference', 'site': 'CodeableConcept', 'route': 'CodeableConcept', 'doseQuantity': 'Quantity', 'performer': 'ImmunizationPerformer', 'note': 'Annotation', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'subpotentReason': 'CodeableConcept', 'education': 'ImmunizationEducation', 'programEligibility': 'CodeableConcept', 'fundingSource': 'CodeableConcept', 'reaction': 'ImmunizationReaction', 'protocolApplied': 'ImmunizationProtocolApplied'}
    _choice_fields = {'occurrence': ['occurrenceDateTime', 'occurrenceString']}

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
    occurrenceDateTime: Optional[DateTime] = None
    occurrenceString: Optional[String] = None
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
    performer: ImmunizationPerformer | FHIRList[ImmunizationPerformer]
    note: Annotation | FHIRList[Annotation]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    isSubpotent: Optional[Boolean] = None
    subpotentReason: CodeableConcept | FHIRList[CodeableConcept]
    education: ImmunizationEducation | FHIRList[ImmunizationEducation]
    programEligibility: CodeableConcept | FHIRList[CodeableConcept]
    fundingSource: Optional[CodeableConcept]
    reaction: ImmunizationReaction | FHIRList[ImmunizationReaction]
    protocolApplied: ImmunizationProtocolApplied | FHIRList[ImmunizationProtocolApplied]


class ImmunizationEvaluation(FHIRResource):
    _resource_type = "ImmunizationEvaluation"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'doseStatusReason'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'patient': 'Reference', 'authority': 'Reference', 'targetDisease': 'CodeableConcept', 'immunizationEvent': 'Reference', 'doseStatus': 'CodeableConcept', 'doseStatusReason': 'CodeableConcept'}
    _choice_fields = {'doseNumber': ['doseNumberPositiveInt', 'doseNumberString'], 'seriesDoses': ['seriesDosesPositiveInt', 'seriesDosesString']}

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
    doseNumberPositiveInt: Optional[PositiveInt] = None
    doseNumberString: Optional[String] = None
    seriesDosesPositiveInt: Optional[PositiveInt] = None
    seriesDosesString: Optional[String] = None


class ImmunizationRecommendationRecommendation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'vaccineCode', 'contraindicatedVaccineCode', 'forecastReason', 'dateCriterion', 'supportingImmunization', 'supportingPatientInformation'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'vaccineCode': 'CodeableConcept', 'targetDisease': 'CodeableConcept', 'contraindicatedVaccineCode': 'CodeableConcept', 'forecastStatus': 'CodeableConcept', 'forecastReason': 'CodeableConcept', 'dateCriterion': 'ImmunizationRecommendationRecommendationDateCriterion', 'supportingImmunization': 'Reference', 'supportingPatientInformation': 'Reference'}
    _choice_fields = {'doseNumber': ['doseNumberPositiveInt', 'doseNumberString'], 'seriesDoses': ['seriesDosesPositiveInt', 'seriesDosesString']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    vaccineCode: CodeableConcept | FHIRList[CodeableConcept]
    targetDisease: Optional[CodeableConcept]
    contraindicatedVaccineCode: CodeableConcept | FHIRList[CodeableConcept]
    forecastStatus: Optional[CodeableConcept]
    forecastReason: CodeableConcept | FHIRList[CodeableConcept]
    dateCriterion: ImmunizationRecommendationRecommendationDateCriterion | FHIRList[ImmunizationRecommendationRecommendationDateCriterion]
    description: Optional[String] = None
    series: Optional[String] = None
    doseNumberPositiveInt: Optional[PositiveInt] = None
    doseNumberString: Optional[String] = None
    seriesDosesPositiveInt: Optional[PositiveInt] = None
    seriesDosesString: Optional[String] = None
    supportingImmunization: Reference | FHIRList[Reference]
    supportingPatientInformation: Reference | FHIRList[Reference]


class ImmunizationRecommendationRecommendationDateCriterion(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    value: Optional[DateTime] = None


class ImmunizationRecommendation(FHIRResource):
    _resource_type = "ImmunizationRecommendation"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'recommendation'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'patient': 'Reference', 'authority': 'Reference', 'recommendation': 'ImmunizationRecommendationRecommendation'}

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
    recommendation: ImmunizationRecommendationRecommendation | FHIRList[ImmunizationRecommendationRecommendation]


class ImplementationGuideDependsOn(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    uri: Optional[Canonical] = None
    packageId: Optional[Id] = None
    version: Optional[String] = None


class ImplementationGuideGlobal(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    profile: Optional[Canonical] = None


class ImplementationGuideDefinition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'grouping', 'resource', 'parameter', 'template'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'grouping': 'ImplementationGuideDefinitionGrouping', 'resource': 'ImplementationGuideDefinitionResource', 'page': 'ImplementationGuideDefinitionPage', 'parameter': 'ImplementationGuideDefinitionParameter', 'template': 'ImplementationGuideDefinitionTemplate'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    grouping: ImplementationGuideDefinitionGrouping | FHIRList[ImplementationGuideDefinitionGrouping]
    resource: ImplementationGuideDefinitionResource | FHIRList[ImplementationGuideDefinitionResource]
    page: Optional[ImplementationGuideDefinitionPage]
    parameter: ImplementationGuideDefinitionParameter | FHIRList[ImplementationGuideDefinitionParameter]
    template: ImplementationGuideDefinitionTemplate | FHIRList[ImplementationGuideDefinitionTemplate]


class ImplementationGuideDefinitionGrouping(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[String] = None
    description: Optional[String] = None


class ImplementationGuideDefinitionResource(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'fhirVersion'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'reference': 'Reference'}
    _choice_fields = {'example': ['exampleBoolean', 'exampleCanonical']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    reference: Optional[Reference]
    fhirVersion: Code | FHIRList[Code] = None
    name: Optional[String] = None
    description: Optional[String] = None
    exampleBoolean: Optional[Boolean] = None
    exampleCanonical: Optional[Canonical] = None
    groupingId: Optional[Id] = None


class ImplementationGuideDefinitionPage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'page'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'nameReference': 'Reference'}
    _choice_fields = {'name': ['nameUrl', 'nameReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    nameUrl: Optional[Url] = None
    nameReference: Optional[Reference]
    title: Optional[String] = None
    generation: Optional[Code] = None
    page: Any = None


class ImplementationGuideDefinitionParameter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    value: Optional[String] = None


class ImplementationGuideDefinitionTemplate(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    source: Optional[String] = None
    scope: Optional[String] = None


class ImplementationGuideManifest(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'resource', 'page', 'image', 'other'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'resource': 'ImplementationGuideManifestResource', 'page': 'ImplementationGuideManifestPage'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    rendering: Optional[Url] = None
    resource: ImplementationGuideManifestResource | FHIRList[ImplementationGuideManifestResource]
    page: ImplementationGuideManifestPage | FHIRList[ImplementationGuideManifestPage]
    image: String | FHIRList[String] = None
    other: String | FHIRList[String] = None


class ImplementationGuideManifestResource(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'reference': 'Reference'}
    _choice_fields = {'example': ['exampleBoolean', 'exampleCanonical']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    reference: Optional[Reference]
    exampleBoolean: Optional[Boolean] = None
    exampleCanonical: Optional[Canonical] = None
    relativePath: Optional[Url] = None


class ImplementationGuideManifestPage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'anchor'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[String] = None
    title: Optional[String] = None
    anchor: String | FHIRList[String] = None


class ImplementationGuide(FHIRResource):
    _resource_type = "ImplementationGuide"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'fhirVersion', 'dependsOn', 'global_'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'dependsOn': 'ImplementationGuideDependsOn', 'global_': 'ImplementationGuideGlobal', 'definition': 'ImplementationGuideDefinition', 'manifest': 'ImplementationGuideManifest'}

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
    dependsOn: ImplementationGuideDependsOn | FHIRList[ImplementationGuideDependsOn]
    global_: ImplementationGuideGlobal | FHIRList[ImplementationGuideGlobal]
    definition: Optional[ImplementationGuideDefinition]
    manifest: Optional[ImplementationGuideManifest]


class InsurancePlanContact(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'telecom'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'purpose': 'CodeableConcept', 'name': 'HumanName', 'telecom': 'ContactPoint', 'address': 'Address'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    purpose: Optional[CodeableConcept]
    name: Optional[HumanName]
    telecom: ContactPoint | FHIRList[ContactPoint]
    address: Optional[Address]


class InsurancePlanCoverage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'network', 'benefit'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'network': 'Reference', 'benefit': 'InsurancePlanCoverageBenefit'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    network: Reference | FHIRList[Reference]
    benefit: InsurancePlanCoverageBenefit | FHIRList[InsurancePlanCoverageBenefit]


class InsurancePlanCoverageBenefit(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'limit'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'limit': 'InsurancePlanCoverageBenefitLimit'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    requirement: Optional[String] = None
    limit: InsurancePlanCoverageBenefitLimit | FHIRList[InsurancePlanCoverageBenefitLimit]


class InsurancePlanCoverageBenefitLimit(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'value': 'Quantity', 'code': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    value: Optional[Quantity]
    code: Optional[CodeableConcept]


class InsurancePlanPlan(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'identifier', 'coverageArea', 'network', 'generalCost', 'specificCost'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'coverageArea': 'Reference', 'network': 'Reference', 'generalCost': 'InsurancePlanPlanGeneralCost', 'specificCost': 'InsurancePlanPlanSpecificCost'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    type_: Optional[CodeableConcept]
    coverageArea: Reference | FHIRList[Reference]
    network: Reference | FHIRList[Reference]
    generalCost: InsurancePlanPlanGeneralCost | FHIRList[InsurancePlanPlanGeneralCost]
    specificCost: InsurancePlanPlanSpecificCost | FHIRList[InsurancePlanPlanSpecificCost]


class InsurancePlanPlanGeneralCost(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'cost': 'Money'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    groupSize: Optional[PositiveInt] = None
    cost: Optional[Money]
    comment: Optional[String] = None


class InsurancePlanPlanSpecificCost(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'benefit'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'category': 'CodeableConcept', 'benefit': 'InsurancePlanPlanSpecificCostBenefit'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    category: Optional[CodeableConcept]
    benefit: InsurancePlanPlanSpecificCostBenefit | FHIRList[InsurancePlanPlanSpecificCostBenefit]


class InsurancePlanPlanSpecificCostBenefit(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'cost'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'cost': 'InsurancePlanPlanSpecificCostBenefitCost'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    cost: InsurancePlanPlanSpecificCostBenefitCost | FHIRList[InsurancePlanPlanSpecificCostBenefitCost]


class InsurancePlanPlanSpecificCostBenefitCost(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'qualifiers'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'applicability': 'CodeableConcept', 'qualifiers': 'CodeableConcept', 'value': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    applicability: Optional[CodeableConcept]
    qualifiers: CodeableConcept | FHIRList[CodeableConcept]
    value: Optional[Quantity]


class InsurancePlan(FHIRResource):
    _resource_type = "InsurancePlan"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'type_', 'alias', 'coverageArea', 'contact', 'endpoint', 'network', 'coverage', 'plan'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'period': 'Period', 'ownedBy': 'Reference', 'administeredBy': 'Reference', 'coverageArea': 'Reference', 'contact': 'InsurancePlanContact', 'endpoint': 'Reference', 'network': 'Reference', 'coverage': 'InsurancePlanCoverage', 'plan': 'InsurancePlanPlan'}

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
    type_: CodeableConcept | FHIRList[CodeableConcept]
    name: Optional[String] = None
    alias: String | FHIRList[String] = None
    period: Optional[Period]
    ownedBy: Optional[Reference]
    administeredBy: Optional[Reference]
    coverageArea: Reference | FHIRList[Reference]
    contact: InsurancePlanContact | FHIRList[InsurancePlanContact]
    endpoint: Reference | FHIRList[Reference]
    network: Reference | FHIRList[Reference]
    coverage: InsurancePlanCoverage | FHIRList[InsurancePlanCoverage]
    plan: InsurancePlanPlan | FHIRList[InsurancePlanPlan]


class InvoiceParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'role': 'CodeableConcept', 'actor': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    role: Optional[CodeableConcept]
    actor: Optional[Reference]


class InvoiceLineItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'priceComponent'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'chargeItemReference': 'Reference', 'chargeItemCodeableConcept': 'CodeableConcept', 'priceComponent': 'InvoiceLineItemPriceComponent'}
    _choice_fields = {'chargeItem': ['chargeItemReference', 'chargeItemCodeableConcept']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequence: Optional[PositiveInt] = None
    chargeItemReference: Optional[Reference]
    chargeItemCodeableConcept: Optional[CodeableConcept]
    priceComponent: InvoiceLineItemPriceComponent | FHIRList[InvoiceLineItemPriceComponent]


class InvoiceLineItemPriceComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'amount': 'Money'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    code: Optional[CodeableConcept]
    factor: Optional[Decimal] = None
    amount: Optional[Money]


class Invoice(FHIRResource):
    _resource_type = "Invoice"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'participant', 'lineItem', 'totalPriceComponent', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'subject': 'Reference', 'recipient': 'Reference', 'participant': 'InvoiceParticipant', 'issuer': 'Reference', 'account': 'Reference', 'lineItem': 'InvoiceLineItem', 'totalNet': 'Money', 'totalGross': 'Money', 'note': 'Annotation'}

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
    type_: Optional[CodeableConcept]
    subject: Optional[Reference]
    recipient: Optional[Reference]
    date: Optional[DateTime] = None
    participant: InvoiceParticipant | FHIRList[InvoiceParticipant]
    issuer: Optional[Reference]
    account: Optional[Reference]
    lineItem: InvoiceLineItem | FHIRList[InvoiceLineItem]
    totalPriceComponent: Any = None
    totalNet: Optional[Money]
    totalGross: Optional[Money]
    paymentTerms: Optional[Markdown] = None
    note: Annotation | FHIRList[Annotation]


class Library(FHIRResource):
    _resource_type = "Library"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'parameter', 'dataRequirement', 'content'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'subjectCodeableConcept': 'CodeableConcept', 'subjectReference': 'Reference', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'parameter': 'ParameterDefinition', 'dataRequirement': 'DataRequirement', 'content': 'Attachment'}
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

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
    type_: Optional[CodeableConcept]
    subjectCodeableConcept: Optional[CodeableConcept]
    subjectReference: Optional[Reference]
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


class LinkageItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'resource': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    resource: Optional[Reference]


class Linkage(FHIRResource):
    _resource_type = "Linkage"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'item'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'author': 'Reference', 'item': 'LinkageItem'}

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
    item: LinkageItem | FHIRList[LinkageItem]


class ListEntry(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'flag': 'CodeableConcept', 'item': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    flag: Optional[CodeableConcept]
    deleted: Optional[Boolean] = None
    date: Optional[DateTime] = None
    item: Optional[Reference]


class List(FHIRResource):
    _resource_type = "List"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'note', 'entry'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'code': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'source': 'Reference', 'orderedBy': 'CodeableConcept', 'note': 'Annotation', 'entry': 'ListEntry', 'emptyReason': 'CodeableConcept'}

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
    entry: ListEntry | FHIRList[ListEntry]
    emptyReason: Optional[CodeableConcept]


class LocationPosition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    longitude: Optional[Decimal] = None
    latitude: Optional[Decimal] = None
    altitude: Optional[Decimal] = None


class LocationHoursOfOperation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'daysOfWeek'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    daysOfWeek: Code | FHIRList[Code] = None
    allDay: Optional[Boolean] = None
    openingTime: Optional[Time] = None
    closingTime: Optional[Time] = None


class Location(FHIRResource):
    _resource_type = "Location"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'alias', 'type_', 'telecom', 'hoursOfOperation', 'endpoint'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'operationalStatus': 'Coding', 'type_': 'CodeableConcept', 'telecom': 'ContactPoint', 'address': 'Address', 'physicalType': 'CodeableConcept', 'position': 'LocationPosition', 'managingOrganization': 'Reference', 'partOf': 'Reference', 'hoursOfOperation': 'LocationHoursOfOperation', 'endpoint': 'Reference'}

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
    type_: CodeableConcept | FHIRList[CodeableConcept]
    telecom: ContactPoint | FHIRList[ContactPoint]
    address: Optional[Address]
    physicalType: Optional[CodeableConcept]
    position: Optional[LocationPosition]
    managingOrganization: Optional[Reference]
    partOf: Optional[Reference]
    hoursOfOperation: LocationHoursOfOperation | FHIRList[LocationHoursOfOperation]
    availabilityExceptions: Optional[String] = None
    endpoint: Reference | FHIRList[Reference]


class MeasureGroup(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'population', 'stratifier'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'population': 'MeasureGroupPopulation', 'stratifier': 'MeasureGroupStratifier'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    description: Optional[String] = None
    population: MeasureGroupPopulation | FHIRList[MeasureGroupPopulation]
    stratifier: MeasureGroupStratifier | FHIRList[MeasureGroupStratifier]


class MeasureGroupPopulation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'criteria': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    description: Optional[String] = None
    criteria: Optional[Expression]


class MeasureGroupStratifier(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'component'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'criteria': 'Expression', 'component': 'MeasureGroupStratifierComponent'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    description: Optional[String] = None
    criteria: Optional[Expression]
    component: MeasureGroupStratifierComponent | FHIRList[MeasureGroupStratifierComponent]


class MeasureGroupStratifierComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'criteria': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    description: Optional[String] = None
    criteria: Optional[Expression]


class MeasureSupplementalData(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'usage'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'usage': 'CodeableConcept', 'criteria': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    usage: CodeableConcept | FHIRList[CodeableConcept]
    description: Optional[String] = None
    criteria: Optional[Expression]


class Measure(FHIRResource):
    _resource_type = "Measure"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'library', 'type_', 'definition', 'group', 'supplementalData'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'subjectCodeableConcept': 'CodeableConcept', 'subjectReference': 'Reference', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'scoring': 'CodeableConcept', 'compositeScoring': 'CodeableConcept', 'type_': 'CodeableConcept', 'improvementNotation': 'CodeableConcept', 'group': 'MeasureGroup', 'supplementalData': 'MeasureSupplementalData'}
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

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
    subjectCodeableConcept: Optional[CodeableConcept]
    subjectReference: Optional[Reference]
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
    type_: CodeableConcept | FHIRList[CodeableConcept]
    riskAdjustment: Optional[String] = None
    rateAggregation: Optional[String] = None
    rationale: Optional[Markdown] = None
    clinicalRecommendationStatement: Optional[Markdown] = None
    improvementNotation: Optional[CodeableConcept]
    definition: Markdown | FHIRList[Markdown] = None
    guidance: Optional[Markdown] = None
    group: MeasureGroup | FHIRList[MeasureGroup]
    supplementalData: MeasureSupplementalData | FHIRList[MeasureSupplementalData]


class MeasureReportGroup(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'population', 'stratifier'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'population': 'MeasureReportGroupPopulation', 'measureScore': 'Quantity', 'stratifier': 'MeasureReportGroupStratifier'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    population: MeasureReportGroupPopulation | FHIRList[MeasureReportGroupPopulation]
    measureScore: Optional[Quantity]
    stratifier: MeasureReportGroupStratifier | FHIRList[MeasureReportGroupStratifier]


class MeasureReportGroupPopulation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'subjectResults': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    count: Optional[Integer] = None
    subjectResults: Optional[Reference]


class MeasureReportGroupStratifier(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'stratum'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'stratum': 'MeasureReportGroupStratifierStratum'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: CodeableConcept | FHIRList[CodeableConcept]
    stratum: MeasureReportGroupStratifierStratum | FHIRList[MeasureReportGroupStratifierStratum]


class MeasureReportGroupStratifierStratum(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'component', 'population'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'value': 'CodeableConcept', 'component': 'MeasureReportGroupStratifierStratumComponent', 'population': 'MeasureReportGroupStratifierStratumPopulation', 'measureScore': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    value: Optional[CodeableConcept]
    component: MeasureReportGroupStratifierStratumComponent | FHIRList[MeasureReportGroupStratifierStratumComponent]
    population: MeasureReportGroupStratifierStratumPopulation | FHIRList[MeasureReportGroupStratifierStratumPopulation]
    measureScore: Optional[Quantity]


class MeasureReportGroupStratifierStratumComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'value': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    value: Optional[CodeableConcept]


class MeasureReportGroupStratifierStratumPopulation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'subjectResults': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    count: Optional[Integer] = None
    subjectResults: Optional[Reference]


class MeasureReport(FHIRResource):
    _resource_type = "MeasureReport"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'group', 'evaluatedResource'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'subject': 'Reference', 'reporter': 'Reference', 'period': 'Period', 'improvementNotation': 'CodeableConcept', 'group': 'MeasureReportGroup', 'evaluatedResource': 'Reference'}

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
    type_: Optional[Code] = None
    measure: Optional[Canonical] = None
    subject: Optional[Reference]
    date: Optional[DateTime] = None
    reporter: Optional[Reference]
    period: Optional[Period]
    improvementNotation: Optional[CodeableConcept]
    group: MeasureReportGroup | FHIRList[MeasureReportGroup]
    evaluatedResource: Reference | FHIRList[Reference]


class Media(FHIRResource):
    _resource_type = "Media"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'reasonCode', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'type_': 'CodeableConcept', 'modality': 'CodeableConcept', 'view': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'createdPeriod': 'Period', 'operator': 'Reference', 'reasonCode': 'CodeableConcept', 'bodySite': 'CodeableConcept', 'device': 'Reference', 'content': 'Attachment', 'note': 'Annotation'}
    _choice_fields = {'created': ['createdDateTime', 'createdPeriod']}

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
    type_: Optional[CodeableConcept]
    modality: Optional[CodeableConcept]
    view: Optional[CodeableConcept]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    createdDateTime: Optional[DateTime] = None
    createdPeriod: Optional[Period]
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


class MedicationIngredient(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'itemCodeableConcept': 'CodeableConcept', 'itemReference': 'Reference', 'strength': 'Ratio'}
    _choice_fields = {'item': ['itemCodeableConcept', 'itemReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    itemCodeableConcept: Optional[CodeableConcept]
    itemReference: Optional[Reference]
    isActive: Optional[Boolean] = None
    strength: Optional[Ratio]


class MedicationBatch(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    lotNumber: Optional[String] = None
    expirationDate: Optional[DateTime] = None


class Medication(FHIRResource):
    _resource_type = "Medication"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'ingredient'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'code': 'CodeableConcept', 'manufacturer': 'Reference', 'form': 'CodeableConcept', 'amount': 'Ratio', 'ingredient': 'MedicationIngredient', 'batch': 'MedicationBatch'}

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
    ingredient: MedicationIngredient | FHIRList[MedicationIngredient]
    batch: Optional[MedicationBatch]


class MedicationAdministrationPerformer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'function': 'CodeableConcept', 'actor': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    function: Optional[CodeableConcept]
    actor: Optional[Reference]


class MedicationAdministrationDosage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'site': 'CodeableConcept', 'route': 'CodeableConcept', 'method': 'CodeableConcept', 'dose': 'Quantity', 'rateRatio': 'Ratio', 'rateQuantity': 'Quantity'}
    _choice_fields = {'rate': ['rateRatio', 'rateQuantity']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    text: Optional[String] = None
    site: Optional[CodeableConcept]
    route: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    dose: Optional[Quantity]
    rateRatio: Optional[Ratio]
    rateQuantity: Optional[Quantity]


class MedicationAdministration(FHIRResource):
    _resource_type = "MedicationAdministration"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'instantiates', 'partOf', 'statusReason', 'supportingInformation', 'performer', 'reasonCode', 'reasonReference', 'device', 'note', 'eventHistory'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'partOf': 'Reference', 'statusReason': 'CodeableConcept', 'category': 'CodeableConcept', 'medicationCodeableConcept': 'CodeableConcept', 'medicationReference': 'Reference', 'subject': 'Reference', 'context': 'Reference', 'supportingInformation': 'Reference', 'effectivePeriod': 'Period', 'performer': 'MedicationAdministrationPerformer', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'request': 'Reference', 'device': 'Reference', 'note': 'Annotation', 'dosage': 'MedicationAdministrationDosage', 'eventHistory': 'Reference'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'medication': ['medicationCodeableConcept', 'medicationReference']}

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
    medicationCodeableConcept: Optional[CodeableConcept]
    medicationReference: Optional[Reference]
    subject: Optional[Reference]
    context: Optional[Reference]
    supportingInformation: Reference | FHIRList[Reference]
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    performer: MedicationAdministrationPerformer | FHIRList[MedicationAdministrationPerformer]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    request: Optional[Reference]
    device: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]
    dosage: Optional[MedicationAdministrationDosage]
    eventHistory: Reference | FHIRList[Reference]


class MedicationDispensePerformer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'function': 'CodeableConcept', 'actor': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    function: Optional[CodeableConcept]
    actor: Optional[Reference]


class MedicationDispenseSubstitution(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'reason', 'responsibleParty'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'reason': 'CodeableConcept', 'responsibleParty': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    wasSubstituted: Optional[Boolean] = None
    type_: Optional[CodeableConcept]
    reason: CodeableConcept | FHIRList[CodeableConcept]
    responsibleParty: Reference | FHIRList[Reference]


class MedicationDispense(FHIRResource):
    _resource_type = "MedicationDispense"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'partOf', 'supportingInformation', 'performer', 'authorizingPrescription', 'receiver', 'note', 'dosageInstruction', 'detectedIssue', 'eventHistory'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'partOf': 'Reference', 'statusReasonCodeableConcept': 'CodeableConcept', 'statusReasonReference': 'Reference', 'category': 'CodeableConcept', 'medicationCodeableConcept': 'CodeableConcept', 'medicationReference': 'Reference', 'subject': 'Reference', 'context': 'Reference', 'supportingInformation': 'Reference', 'performer': 'MedicationDispensePerformer', 'location': 'Reference', 'authorizingPrescription': 'Reference', 'type_': 'CodeableConcept', 'quantity': 'Quantity', 'daysSupply': 'Quantity', 'destination': 'Reference', 'receiver': 'Reference', 'note': 'Annotation', 'dosageInstruction': 'Dosage', 'substitution': 'MedicationDispenseSubstitution', 'detectedIssue': 'Reference', 'eventHistory': 'Reference'}
    _choice_fields = {'medication': ['medicationCodeableConcept', 'medicationReference'], 'statusReason': ['statusReasonCodeableConcept', 'statusReasonReference']}

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
    statusReasonCodeableConcept: Optional[CodeableConcept]
    statusReasonReference: Optional[Reference]
    category: Optional[CodeableConcept]
    medicationCodeableConcept: Optional[CodeableConcept]
    medicationReference: Optional[Reference]
    subject: Optional[Reference]
    context: Optional[Reference]
    supportingInformation: Reference | FHIRList[Reference]
    performer: MedicationDispensePerformer | FHIRList[MedicationDispensePerformer]
    location: Optional[Reference]
    authorizingPrescription: Reference | FHIRList[Reference]
    type_: Optional[CodeableConcept]
    quantity: Optional[Quantity]
    daysSupply: Optional[Quantity]
    whenPrepared: Optional[DateTime] = None
    whenHandedOver: Optional[DateTime] = None
    destination: Optional[Reference]
    receiver: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]
    dosageInstruction: Dosage | FHIRList[Dosage]
    substitution: Optional[MedicationDispenseSubstitution]
    detectedIssue: Reference | FHIRList[Reference]
    eventHistory: Reference | FHIRList[Reference]


class MedicationKnowledgeRelatedMedicationKnowledge(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'reference'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'reference': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    reference: Reference | FHIRList[Reference]


class MedicationKnowledgeMonograph(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'source': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    source: Optional[Reference]


class MedicationKnowledgeIngredient(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'itemCodeableConcept': 'CodeableConcept', 'itemReference': 'Reference', 'strength': 'Ratio'}
    _choice_fields = {'item': ['itemCodeableConcept', 'itemReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    itemCodeableConcept: Optional[CodeableConcept]
    itemReference: Optional[Reference]
    isActive: Optional[Boolean] = None
    strength: Optional[Ratio]


class MedicationKnowledgeCost(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'cost': 'Money'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    source: Optional[String] = None
    cost: Optional[Money]


class MedicationKnowledgeMonitoringProgram(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    name: Optional[String] = None


class MedicationKnowledgeAdministrationGuidelines(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'dosage', 'patientCharacteristics'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'dosage': 'MedicationKnowledgeAdministrationGuidelinesDosage', 'indicationCodeableConcept': 'CodeableConcept', 'indicationReference': 'Reference', 'patientCharacteristics': 'MedicationKnowledgeAdministrationGuidelinesPatientCharacteristics'}
    _choice_fields = {'indication': ['indicationCodeableConcept', 'indicationReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    dosage: MedicationKnowledgeAdministrationGuidelinesDosage | FHIRList[MedicationKnowledgeAdministrationGuidelinesDosage]
    indicationCodeableConcept: Optional[CodeableConcept]
    indicationReference: Optional[Reference]
    patientCharacteristics: MedicationKnowledgeAdministrationGuidelinesPatientCharacteristics | FHIRList[MedicationKnowledgeAdministrationGuidelinesPatientCharacteristics]


class MedicationKnowledgeAdministrationGuidelinesDosage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'dosage'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'dosage': 'Dosage'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    dosage: Dosage | FHIRList[Dosage]


class MedicationKnowledgeAdministrationGuidelinesPatientCharacteristics(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'value'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'characteristicCodeableConcept': 'CodeableConcept', 'characteristicQuantity': 'Quantity'}
    _choice_fields = {'characteristic': ['characteristicCodeableConcept', 'characteristicQuantity']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    characteristicCodeableConcept: Optional[CodeableConcept]
    characteristicQuantity: Optional[Quantity]
    value: String | FHIRList[String] = None


class MedicationKnowledgeMedicineClassification(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'classification'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'classification': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    classification: CodeableConcept | FHIRList[CodeableConcept]


class MedicationKnowledgePackaging(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'quantity': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    quantity: Optional[Quantity]


class MedicationKnowledgeDrugCharacteristic(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'valueCodeableConcept': 'CodeableConcept', 'valueQuantity': 'Quantity'}
    _choice_fields = {'value': ['valueCodeableConcept', 'valueString', 'valueQuantity', 'valueBase64Binary']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueQuantity: Optional[Quantity]
    valueBase64Binary: Optional[Base64Binary] = None


class MedicationKnowledgeRegulatory(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'substitution', 'schedule'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'regulatoryAuthority': 'Reference', 'substitution': 'MedicationKnowledgeRegulatorySubstitution', 'schedule': 'MedicationKnowledgeRegulatorySchedule', 'maxDispense': 'MedicationKnowledgeRegulatoryMaxDispense'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    regulatoryAuthority: Optional[Reference]
    substitution: MedicationKnowledgeRegulatorySubstitution | FHIRList[MedicationKnowledgeRegulatorySubstitution]
    schedule: MedicationKnowledgeRegulatorySchedule | FHIRList[MedicationKnowledgeRegulatorySchedule]
    maxDispense: Optional[MedicationKnowledgeRegulatoryMaxDispense]


class MedicationKnowledgeRegulatorySubstitution(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    allowed: Optional[Boolean] = None


class MedicationKnowledgeRegulatorySchedule(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'schedule': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    schedule: Optional[CodeableConcept]


class MedicationKnowledgeRegulatoryMaxDispense(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'quantity': 'Quantity', 'period': 'Duration'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    quantity: Optional[Quantity]
    period: Optional[Duration]


class MedicationKnowledgeKinetics(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'areaUnderCurve', 'lethalDose50'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'areaUnderCurve': 'Quantity', 'lethalDose50': 'Quantity', 'halfLifePeriod': 'Duration'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    areaUnderCurve: Quantity | FHIRList[Quantity]
    lethalDose50: Quantity | FHIRList[Quantity]
    halfLifePeriod: Optional[Duration]


class MedicationKnowledge(FHIRResource):
    _resource_type = "MedicationKnowledge"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'synonym', 'relatedMedicationKnowledge', 'associatedMedication', 'productType', 'monograph', 'ingredient', 'intendedRoute', 'cost', 'monitoringProgram', 'administrationGuidelines', 'medicineClassification', 'drugCharacteristic', 'contraindication', 'regulatory', 'kinetics'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'manufacturer': 'Reference', 'doseForm': 'CodeableConcept', 'amount': 'Quantity', 'relatedMedicationKnowledge': 'MedicationKnowledgeRelatedMedicationKnowledge', 'associatedMedication': 'Reference', 'productType': 'CodeableConcept', 'monograph': 'MedicationKnowledgeMonograph', 'ingredient': 'MedicationKnowledgeIngredient', 'intendedRoute': 'CodeableConcept', 'cost': 'MedicationKnowledgeCost', 'monitoringProgram': 'MedicationKnowledgeMonitoringProgram', 'administrationGuidelines': 'MedicationKnowledgeAdministrationGuidelines', 'medicineClassification': 'MedicationKnowledgeMedicineClassification', 'packaging': 'MedicationKnowledgePackaging', 'drugCharacteristic': 'MedicationKnowledgeDrugCharacteristic', 'contraindication': 'Reference', 'regulatory': 'MedicationKnowledgeRegulatory', 'kinetics': 'MedicationKnowledgeKinetics'}

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
    relatedMedicationKnowledge: MedicationKnowledgeRelatedMedicationKnowledge | FHIRList[MedicationKnowledgeRelatedMedicationKnowledge]
    associatedMedication: Reference | FHIRList[Reference]
    productType: CodeableConcept | FHIRList[CodeableConcept]
    monograph: MedicationKnowledgeMonograph | FHIRList[MedicationKnowledgeMonograph]
    ingredient: MedicationKnowledgeIngredient | FHIRList[MedicationKnowledgeIngredient]
    preparationInstruction: Optional[Markdown] = None
    intendedRoute: CodeableConcept | FHIRList[CodeableConcept]
    cost: MedicationKnowledgeCost | FHIRList[MedicationKnowledgeCost]
    monitoringProgram: MedicationKnowledgeMonitoringProgram | FHIRList[MedicationKnowledgeMonitoringProgram]
    administrationGuidelines: MedicationKnowledgeAdministrationGuidelines | FHIRList[MedicationKnowledgeAdministrationGuidelines]
    medicineClassification: MedicationKnowledgeMedicineClassification | FHIRList[MedicationKnowledgeMedicineClassification]
    packaging: Optional[MedicationKnowledgePackaging]
    drugCharacteristic: MedicationKnowledgeDrugCharacteristic | FHIRList[MedicationKnowledgeDrugCharacteristic]
    contraindication: Reference | FHIRList[Reference]
    regulatory: MedicationKnowledgeRegulatory | FHIRList[MedicationKnowledgeRegulatory]
    kinetics: MedicationKnowledgeKinetics | FHIRList[MedicationKnowledgeKinetics]


class MedicationRequestDispenseRequest(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'initialFill': 'MedicationRequestDispenseRequestInitialFill', 'dispenseInterval': 'Duration', 'validityPeriod': 'Period', 'quantity': 'Quantity', 'expectedSupplyDuration': 'Duration', 'performer': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    initialFill: Optional[MedicationRequestDispenseRequestInitialFill]
    dispenseInterval: Optional[Duration]
    validityPeriod: Optional[Period]
    numberOfRepeatsAllowed: Optional[UnsignedInt] = None
    quantity: Optional[Quantity]
    expectedSupplyDuration: Optional[Duration]
    performer: Optional[Reference]


class MedicationRequestDispenseRequestInitialFill(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'quantity': 'Quantity', 'duration': 'Duration'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    quantity: Optional[Quantity]
    duration: Optional[Duration]


class MedicationRequestSubstitution(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'allowedCodeableConcept': 'CodeableConcept', 'reason': 'CodeableConcept'}
    _choice_fields = {'allowed': ['allowedBoolean', 'allowedCodeableConcept']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    allowedBoolean: Optional[Boolean] = None
    allowedCodeableConcept: Optional[CodeableConcept]
    reason: Optional[CodeableConcept]


class MedicationRequest(FHIRResource):
    _resource_type = "MedicationRequest"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'supportingInformation', 'reasonCode', 'reasonReference', 'instantiatesCanonical', 'instantiatesUri', 'basedOn', 'insurance', 'note', 'dosageInstruction', 'detectedIssue', 'eventHistory'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'statusReason': 'CodeableConcept', 'category': 'CodeableConcept', 'reportedReference': 'Reference', 'medicationCodeableConcept': 'CodeableConcept', 'medicationReference': 'Reference', 'subject': 'Reference', 'encounter': 'Reference', 'supportingInformation': 'Reference', 'requester': 'Reference', 'performer': 'Reference', 'performerType': 'CodeableConcept', 'recorder': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'basedOn': 'Reference', 'groupIdentifier': 'Identifier', 'courseOfTherapyType': 'CodeableConcept', 'insurance': 'Reference', 'note': 'Annotation', 'dosageInstruction': 'Dosage', 'dispenseRequest': 'MedicationRequestDispenseRequest', 'substitution': 'MedicationRequestSubstitution', 'priorPrescription': 'Reference', 'detectedIssue': 'Reference', 'eventHistory': 'Reference'}
    _choice_fields = {'medication': ['medicationCodeableConcept', 'medicationReference'], 'reported': ['reportedBoolean', 'reportedReference']}

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
    reportedBoolean: Optional[Boolean] = None
    reportedReference: Optional[Reference]
    medicationCodeableConcept: Optional[CodeableConcept]
    medicationReference: Optional[Reference]
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
    dispenseRequest: Optional[MedicationRequestDispenseRequest]
    substitution: Optional[MedicationRequestSubstitution]
    priorPrescription: Optional[Reference]
    detectedIssue: Reference | FHIRList[Reference]
    eventHistory: Reference | FHIRList[Reference]


class MedicationStatement(FHIRResource):
    _resource_type = "MedicationStatement"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'statusReason', 'derivedFrom', 'reasonCode', 'reasonReference', 'note', 'dosage'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'statusReason': 'CodeableConcept', 'category': 'CodeableConcept', 'medicationCodeableConcept': 'CodeableConcept', 'medicationReference': 'Reference', 'subject': 'Reference', 'context': 'Reference', 'effectivePeriod': 'Period', 'informationSource': 'Reference', 'derivedFrom': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'note': 'Annotation', 'dosage': 'Dosage'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'medication': ['medicationCodeableConcept', 'medicationReference']}

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
    medicationCodeableConcept: Optional[CodeableConcept]
    medicationReference: Optional[Reference]
    subject: Optional[Reference]
    context: Optional[Reference]
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    dateAsserted: Optional[DateTime] = None
    informationSource: Optional[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    note: Annotation | FHIRList[Annotation]
    dosage: Dosage | FHIRList[Dosage]


class MedicinalProductName(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'namePart', 'countryLanguage'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'namePart': 'MedicinalProductNameNamePart', 'countryLanguage': 'MedicinalProductNameCountryLanguage'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    productName: Optional[String] = None
    namePart: MedicinalProductNameNamePart | FHIRList[MedicinalProductNameNamePart]
    countryLanguage: MedicinalProductNameCountryLanguage | FHIRList[MedicinalProductNameCountryLanguage]


class MedicinalProductNameNamePart(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    part: Optional[String] = None
    type_: Optional[Coding]


class MedicinalProductNameCountryLanguage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'country': 'CodeableConcept', 'jurisdiction': 'CodeableConcept', 'language': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    country: Optional[CodeableConcept]
    jurisdiction: Optional[CodeableConcept]
    language: Optional[CodeableConcept]


class MedicinalProductManufacturingBusinessOperation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'manufacturer'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'operationType': 'CodeableConcept', 'authorisationReferenceNumber': 'Identifier', 'confidentialityIndicator': 'CodeableConcept', 'manufacturer': 'Reference', 'regulator': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    operationType: Optional[CodeableConcept]
    authorisationReferenceNumber: Optional[Identifier]
    effectiveDate: Optional[DateTime] = None
    confidentialityIndicator: Optional[CodeableConcept]
    manufacturer: Reference | FHIRList[Reference]
    regulator: Optional[Reference]


class MedicinalProductSpecialDesignation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'identifier'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'intendedUse': 'CodeableConcept', 'indicationCodeableConcept': 'CodeableConcept', 'indicationReference': 'Reference', 'status': 'CodeableConcept', 'species': 'CodeableConcept'}
    _choice_fields = {'indication': ['indicationCodeableConcept', 'indicationReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    type_: Optional[CodeableConcept]
    intendedUse: Optional[CodeableConcept]
    indicationCodeableConcept: Optional[CodeableConcept]
    indicationReference: Optional[Reference]
    status: Optional[CodeableConcept]
    date: Optional[DateTime] = None
    species: Optional[CodeableConcept]


class MedicinalProduct(FHIRResource):
    _resource_type = "MedicinalProduct"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'specialMeasures', 'productClassification', 'marketingStatus', 'pharmaceuticalProduct', 'packagedMedicinalProduct', 'attachedDocument', 'masterFile', 'contact', 'clinicalTrial', 'name', 'crossReference', 'manufacturingBusinessOperation', 'specialDesignation'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'domain': 'Coding', 'combinedPharmaceuticalDoseForm': 'CodeableConcept', 'legalStatusOfSupply': 'CodeableConcept', 'additionalMonitoringIndicator': 'CodeableConcept', 'paediatricUseIndicator': 'CodeableConcept', 'productClassification': 'CodeableConcept', 'marketingStatus': 'MarketingStatus', 'pharmaceuticalProduct': 'Reference', 'packagedMedicinalProduct': 'Reference', 'attachedDocument': 'Reference', 'masterFile': 'Reference', 'contact': 'Reference', 'clinicalTrial': 'Reference', 'name': 'MedicinalProductName', 'crossReference': 'Identifier', 'manufacturingBusinessOperation': 'MedicinalProductManufacturingBusinessOperation', 'specialDesignation': 'MedicinalProductSpecialDesignation'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    type_: Optional[CodeableConcept]
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
    name: MedicinalProductName | FHIRList[MedicinalProductName]
    crossReference: Identifier | FHIRList[Identifier]
    manufacturingBusinessOperation: MedicinalProductManufacturingBusinessOperation | FHIRList[MedicinalProductManufacturingBusinessOperation]
    specialDesignation: MedicinalProductSpecialDesignation | FHIRList[MedicinalProductSpecialDesignation]


class MedicinalProductAuthorizationJurisdictionalAuthorization(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'identifier', 'jurisdiction'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'country': 'CodeableConcept', 'jurisdiction': 'CodeableConcept', 'legalStatusOfSupply': 'CodeableConcept', 'validityPeriod': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    country: Optional[CodeableConcept]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    legalStatusOfSupply: Optional[CodeableConcept]
    validityPeriod: Optional[Period]


class MedicinalProductAuthorizationProcedure(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'application'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'datePeriod': 'Period'}
    _choice_fields = {'date': ['datePeriod', 'dateDateTime']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Identifier]
    type_: Optional[CodeableConcept]
    datePeriod: Optional[Period]
    dateDateTime: Optional[DateTime] = None
    application: Any = None


class MedicinalProductAuthorization(FHIRResource):
    _resource_type = "MedicinalProductAuthorization"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'country', 'jurisdiction', 'jurisdictionalAuthorization'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'subject': 'Reference', 'country': 'CodeableConcept', 'jurisdiction': 'CodeableConcept', 'status': 'CodeableConcept', 'validityPeriod': 'Period', 'dataExclusivityPeriod': 'Period', 'legalBasis': 'CodeableConcept', 'jurisdictionalAuthorization': 'MedicinalProductAuthorizationJurisdictionalAuthorization', 'holder': 'Reference', 'regulator': 'Reference', 'procedure': 'MedicinalProductAuthorizationProcedure'}

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
    jurisdictionalAuthorization: MedicinalProductAuthorizationJurisdictionalAuthorization | FHIRList[MedicinalProductAuthorizationJurisdictionalAuthorization]
    holder: Optional[Reference]
    regulator: Optional[Reference]
    procedure: Optional[MedicinalProductAuthorizationProcedure]


class MedicinalProductContraindicationOtherTherapy(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'therapyRelationshipType': 'CodeableConcept', 'medicationCodeableConcept': 'CodeableConcept', 'medicationReference': 'Reference'}
    _choice_fields = {'medication': ['medicationCodeableConcept', 'medicationReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    therapyRelationshipType: Optional[CodeableConcept]
    medicationCodeableConcept: Optional[CodeableConcept]
    medicationReference: Optional[Reference]


class MedicinalProductContraindication(FHIRResource):
    _resource_type = "MedicinalProductContraindication"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'subject', 'comorbidity', 'therapeuticIndication', 'otherTherapy', 'population'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'subject': 'Reference', 'disease': 'CodeableConcept', 'diseaseStatus': 'CodeableConcept', 'comorbidity': 'CodeableConcept', 'therapeuticIndication': 'Reference', 'otherTherapy': 'MedicinalProductContraindicationOtherTherapy', 'population': 'Population'}

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
    otherTherapy: MedicinalProductContraindicationOtherTherapy | FHIRList[MedicinalProductContraindicationOtherTherapy]
    population: Population | FHIRList[Population]


class MedicinalProductIndicationOtherTherapy(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'therapyRelationshipType': 'CodeableConcept', 'medicationCodeableConcept': 'CodeableConcept', 'medicationReference': 'Reference'}
    _choice_fields = {'medication': ['medicationCodeableConcept', 'medicationReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    therapyRelationshipType: Optional[CodeableConcept]
    medicationCodeableConcept: Optional[CodeableConcept]
    medicationReference: Optional[Reference]


class MedicinalProductIndication(FHIRResource):
    _resource_type = "MedicinalProductIndication"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'subject', 'comorbidity', 'otherTherapy', 'undesirableEffect', 'population'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'subject': 'Reference', 'diseaseSymptomProcedure': 'CodeableConcept', 'diseaseStatus': 'CodeableConcept', 'comorbidity': 'CodeableConcept', 'intendedEffect': 'CodeableConcept', 'duration': 'Quantity', 'otherTherapy': 'MedicinalProductIndicationOtherTherapy', 'undesirableEffect': 'Reference', 'population': 'Population'}

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
    otherTherapy: MedicinalProductIndicationOtherTherapy | FHIRList[MedicinalProductIndicationOtherTherapy]
    undesirableEffect: Reference | FHIRList[Reference]
    population: Population | FHIRList[Population]


class MedicinalProductIngredientSpecifiedSubstance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'strength'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'group': 'CodeableConcept', 'confidentiality': 'CodeableConcept', 'strength': 'MedicinalProductIngredientSpecifiedSubstanceStrength'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    group: Optional[CodeableConcept]
    confidentiality: Optional[CodeableConcept]
    strength: MedicinalProductIngredientSpecifiedSubstanceStrength | FHIRList[MedicinalProductIngredientSpecifiedSubstanceStrength]


class MedicinalProductIngredientSpecifiedSubstanceStrength(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'country', 'referenceStrength'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'presentation': 'Ratio', 'presentationLowLimit': 'Ratio', 'concentration': 'Ratio', 'concentrationLowLimit': 'Ratio', 'country': 'CodeableConcept', 'referenceStrength': 'MedicinalProductIngredientSpecifiedSubstanceStrengthReferenceStrength'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    presentation: Optional[Ratio]
    presentationLowLimit: Optional[Ratio]
    concentration: Optional[Ratio]
    concentrationLowLimit: Optional[Ratio]
    measurementPoint: Optional[String] = None
    country: CodeableConcept | FHIRList[CodeableConcept]
    referenceStrength: MedicinalProductIngredientSpecifiedSubstanceStrengthReferenceStrength | FHIRList[MedicinalProductIngredientSpecifiedSubstanceStrengthReferenceStrength]


class MedicinalProductIngredientSpecifiedSubstanceStrengthReferenceStrength(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'country'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'substance': 'CodeableConcept', 'strength': 'Ratio', 'strengthLowLimit': 'Ratio', 'country': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    substance: Optional[CodeableConcept]
    strength: Optional[Ratio]
    strengthLowLimit: Optional[Ratio]
    measurementPoint: Optional[String] = None
    country: CodeableConcept | FHIRList[CodeableConcept]


class MedicinalProductIngredientSubstance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'strength'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    strength: Any = None


class MedicinalProductIngredient(FHIRResource):
    _resource_type = "MedicinalProductIngredient"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'manufacturer', 'specifiedSubstance'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'role': 'CodeableConcept', 'manufacturer': 'Reference', 'specifiedSubstance': 'MedicinalProductIngredientSpecifiedSubstance', 'substance': 'MedicinalProductIngredientSubstance'}

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
    specifiedSubstance: MedicinalProductIngredientSpecifiedSubstance | FHIRList[MedicinalProductIngredientSpecifiedSubstance]
    substance: Optional[MedicinalProductIngredientSubstance]


class MedicinalProductInteractionInteractant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'itemReference': 'Reference', 'itemCodeableConcept': 'CodeableConcept'}
    _choice_fields = {'item': ['itemReference', 'itemCodeableConcept']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    itemReference: Optional[Reference]
    itemCodeableConcept: Optional[CodeableConcept]


class MedicinalProductInteraction(FHIRResource):
    _resource_type = "MedicinalProductInteraction"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'subject', 'interactant'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'subject': 'Reference', 'interactant': 'MedicinalProductInteractionInteractant', 'type_': 'CodeableConcept', 'effect': 'CodeableConcept', 'incidence': 'CodeableConcept', 'management': 'CodeableConcept'}

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
    interactant: MedicinalProductInteractionInteractant | FHIRList[MedicinalProductInteractionInteractant]
    type_: Optional[CodeableConcept]
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


class MedicinalProductPackagedBatchIdentifier(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'outerPackaging': 'Identifier', 'immediatePackaging': 'Identifier'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    outerPackaging: Optional[Identifier]
    immediatePackaging: Optional[Identifier]


class MedicinalProductPackagedPackageItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'identifier', 'material', 'alternateMaterial', 'device', 'manufacturedItem', 'packageItem', 'otherCharacteristics', 'shelfLifeStorage', 'manufacturer'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'quantity': 'Quantity', 'material': 'CodeableConcept', 'alternateMaterial': 'CodeableConcept', 'device': 'Reference', 'manufacturedItem': 'Reference', 'physicalCharacteristics': 'ProdCharacteristic', 'otherCharacteristics': 'CodeableConcept', 'shelfLifeStorage': 'ProductShelfLife', 'manufacturer': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    type_: Optional[CodeableConcept]
    quantity: Optional[Quantity]
    material: CodeableConcept | FHIRList[CodeableConcept]
    alternateMaterial: CodeableConcept | FHIRList[CodeableConcept]
    device: Reference | FHIRList[Reference]
    manufacturedItem: Reference | FHIRList[Reference]
    packageItem: Any = None
    physicalCharacteristics: Optional[ProdCharacteristic]
    otherCharacteristics: CodeableConcept | FHIRList[CodeableConcept]
    shelfLifeStorage: ProductShelfLife | FHIRList[ProductShelfLife]
    manufacturer: Reference | FHIRList[Reference]


class MedicinalProductPackaged(FHIRResource):
    _resource_type = "MedicinalProductPackaged"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'subject', 'marketingStatus', 'manufacturer', 'batchIdentifier', 'packageItem'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'subject': 'Reference', 'legalStatusOfSupply': 'CodeableConcept', 'marketingStatus': 'MarketingStatus', 'marketingAuthorization': 'Reference', 'manufacturer': 'Reference', 'batchIdentifier': 'MedicinalProductPackagedBatchIdentifier', 'packageItem': 'MedicinalProductPackagedPackageItem'}

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
    batchIdentifier: MedicinalProductPackagedBatchIdentifier | FHIRList[MedicinalProductPackagedBatchIdentifier]
    packageItem: MedicinalProductPackagedPackageItem | FHIRList[MedicinalProductPackagedPackageItem]


class MedicinalProductPharmaceuticalCharacteristics(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'status': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    status: Optional[CodeableConcept]


class MedicinalProductPharmaceuticalRouteOfAdministration(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'targetSpecies'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'firstDose': 'Quantity', 'maxSingleDose': 'Quantity', 'maxDosePerDay': 'Quantity', 'maxDosePerTreatmentPeriod': 'Ratio', 'maxTreatmentPeriod': 'Duration', 'targetSpecies': 'MedicinalProductPharmaceuticalRouteOfAdministrationTargetSpecies'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    firstDose: Optional[Quantity]
    maxSingleDose: Optional[Quantity]
    maxDosePerDay: Optional[Quantity]
    maxDosePerTreatmentPeriod: Optional[Ratio]
    maxTreatmentPeriod: Optional[Duration]
    targetSpecies: MedicinalProductPharmaceuticalRouteOfAdministrationTargetSpecies | FHIRList[MedicinalProductPharmaceuticalRouteOfAdministrationTargetSpecies]


class MedicinalProductPharmaceuticalRouteOfAdministrationTargetSpecies(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'withdrawalPeriod'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'withdrawalPeriod': 'MedicinalProductPharmaceuticalRouteOfAdministrationTargetSpeciesWithdrawalPeriod'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    withdrawalPeriod: MedicinalProductPharmaceuticalRouteOfAdministrationTargetSpeciesWithdrawalPeriod | FHIRList[MedicinalProductPharmaceuticalRouteOfAdministrationTargetSpeciesWithdrawalPeriod]


class MedicinalProductPharmaceuticalRouteOfAdministrationTargetSpeciesWithdrawalPeriod(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'tissue': 'CodeableConcept', 'value': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    tissue: Optional[CodeableConcept]
    value: Optional[Quantity]
    supportingInformation: Optional[String] = None


class MedicinalProductPharmaceutical(FHIRResource):
    _resource_type = "MedicinalProductPharmaceutical"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'ingredient', 'device', 'characteristics', 'routeOfAdministration'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'administrableDoseForm': 'CodeableConcept', 'unitOfPresentation': 'CodeableConcept', 'ingredient': 'Reference', 'device': 'Reference', 'characteristics': 'MedicinalProductPharmaceuticalCharacteristics', 'routeOfAdministration': 'MedicinalProductPharmaceuticalRouteOfAdministration'}

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
    characteristics: MedicinalProductPharmaceuticalCharacteristics | FHIRList[MedicinalProductPharmaceuticalCharacteristics]
    routeOfAdministration: MedicinalProductPharmaceuticalRouteOfAdministration | FHIRList[MedicinalProductPharmaceuticalRouteOfAdministration]


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


class MessageDefinitionFocus(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    profile: Optional[Canonical] = None
    min: Optional[UnsignedInt] = None
    max: Optional[String] = None


class MessageDefinitionAllowedResponse(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    message: Optional[Canonical] = None
    situation: Optional[Markdown] = None


class MessageDefinition(FHIRResource):
    _resource_type = "MessageDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'replaces', 'contact', 'useContext', 'jurisdiction', 'parent', 'focus', 'allowedResponse', 'graph'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'eventCoding': 'Coding', 'focus': 'MessageDefinitionFocus', 'allowedResponse': 'MessageDefinitionAllowedResponse'}
    _choice_fields = {'event': ['eventCoding', 'eventUri']}

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
    eventCoding: Optional[Coding]
    eventUri: Optional[Uri] = None
    category: Optional[Code] = None
    focus: MessageDefinitionFocus | FHIRList[MessageDefinitionFocus]
    responseRequired: Optional[Code] = None
    allowedResponse: MessageDefinitionAllowedResponse | FHIRList[MessageDefinitionAllowedResponse]
    graph: Canonical | FHIRList[Canonical] = None


class MessageHeaderDestination(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'target': 'Reference', 'receiver': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[String] = None
    target: Optional[Reference]
    endpoint: Optional[Url] = None
    receiver: Optional[Reference]


class MessageHeaderSource(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'contact': 'ContactPoint'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[String] = None
    software: Optional[String] = None
    version: Optional[String] = None
    contact: Optional[ContactPoint]
    endpoint: Optional[Url] = None


class MessageHeaderResponse(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'details': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Id] = None
    code: Optional[Code] = None
    details: Optional[Reference]


class MessageHeader(FHIRResource):
    _resource_type = "MessageHeader"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'destination', 'focus'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'eventCoding': 'Coding', 'destination': 'MessageHeaderDestination', 'sender': 'Reference', 'enterer': 'Reference', 'author': 'Reference', 'source': 'MessageHeaderSource', 'responsible': 'Reference', 'reason': 'CodeableConcept', 'response': 'MessageHeaderResponse', 'focus': 'Reference'}
    _choice_fields = {'event': ['eventCoding', 'eventUri']}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    eventCoding: Optional[Coding]
    eventUri: Optional[Uri] = None
    destination: MessageHeaderDestination | FHIRList[MessageHeaderDestination]
    sender: Optional[Reference]
    enterer: Optional[Reference]
    author: Optional[Reference]
    source: Optional[MessageHeaderSource]
    responsible: Optional[Reference]
    reason: Optional[CodeableConcept]
    response: Optional[MessageHeaderResponse]
    focus: Reference | FHIRList[Reference]
    definition: Optional[Canonical] = None


class MolecularSequenceReferenceSeq(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'chromosome': 'CodeableConcept', 'referenceSeqId': 'CodeableConcept', 'referenceSeqPointer': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    chromosome: Optional[CodeableConcept]
    genomeBuild: Optional[String] = None
    orientation: Optional[Code] = None
    referenceSeqId: Optional[CodeableConcept]
    referenceSeqPointer: Optional[Reference]
    referenceSeqString: Optional[String] = None
    strand: Optional[Code] = None
    windowStart: Optional[Integer] = None
    windowEnd: Optional[Integer] = None


class MolecularSequenceVariant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'variantPointer': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    start: Optional[Integer] = None
    end: Optional[Integer] = None
    observedAllele: Optional[String] = None
    referenceAllele: Optional[String] = None
    cigar: Optional[String] = None
    variantPointer: Optional[Reference]


class MolecularSequenceQuality(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'standardSequence': 'CodeableConcept', 'score': 'Quantity', 'method': 'CodeableConcept', 'roc': 'MolecularSequenceQualityRoc'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    standardSequence: Optional[CodeableConcept]
    start: Optional[Integer] = None
    end: Optional[Integer] = None
    score: Optional[Quantity]
    method: Optional[CodeableConcept]
    truthTP: Optional[Decimal] = None
    queryTP: Optional[Decimal] = None
    truthFN: Optional[Decimal] = None
    queryFP: Optional[Decimal] = None
    gtFP: Optional[Decimal] = None
    precision: Optional[Decimal] = None
    recall: Optional[Decimal] = None
    fScore: Optional[Decimal] = None
    roc: Optional[MolecularSequenceQualityRoc]


class MolecularSequenceQualityRoc(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'score', 'numTP', 'numFP', 'numFN', 'precision', 'sensitivity', 'fMeasure'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    score: Integer | FHIRList[Integer] = None
    numTP: Integer | FHIRList[Integer] = None
    numFP: Integer | FHIRList[Integer] = None
    numFN: Integer | FHIRList[Integer] = None
    precision: Decimal | FHIRList[Decimal] = None
    sensitivity: Decimal | FHIRList[Decimal] = None
    fMeasure: Decimal | FHIRList[Decimal] = None


class MolecularSequenceRepository(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    url: Optional[Uri] = None
    name: Optional[String] = None
    datasetId: Optional[String] = None
    variantsetId: Optional[String] = None
    readsetId: Optional[String] = None


class MolecularSequenceStructureVariant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'variantType': 'CodeableConcept', 'outer': 'MolecularSequenceStructureVariantOuter', 'inner': 'MolecularSequenceStructureVariantInner'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    variantType: Optional[CodeableConcept]
    exact: Optional[Boolean] = None
    length: Optional[Integer] = None
    outer: Optional[MolecularSequenceStructureVariantOuter]
    inner: Optional[MolecularSequenceStructureVariantInner]


class MolecularSequenceStructureVariantOuter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    start: Optional[Integer] = None
    end: Optional[Integer] = None


class MolecularSequenceStructureVariantInner(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    start: Optional[Integer] = None
    end: Optional[Integer] = None


class MolecularSequence(FHIRResource):
    _resource_type = "MolecularSequence"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'variant', 'quality', 'repository', 'pointer', 'structureVariant'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'patient': 'Reference', 'specimen': 'Reference', 'device': 'Reference', 'performer': 'Reference', 'quantity': 'Quantity', 'referenceSeq': 'MolecularSequenceReferenceSeq', 'variant': 'MolecularSequenceVariant', 'quality': 'MolecularSequenceQuality', 'repository': 'MolecularSequenceRepository', 'pointer': 'Reference', 'structureVariant': 'MolecularSequenceStructureVariant'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    type_: Optional[Code] = None
    coordinateSystem: Optional[Integer] = None
    patient: Optional[Reference]
    specimen: Optional[Reference]
    device: Optional[Reference]
    performer: Optional[Reference]
    quantity: Optional[Quantity]
    referenceSeq: Optional[MolecularSequenceReferenceSeq]
    variant: MolecularSequenceVariant | FHIRList[MolecularSequenceVariant]
    observedSeq: Optional[String] = None
    quality: MolecularSequenceQuality | FHIRList[MolecularSequenceQuality]
    readCoverage: Optional[Integer] = None
    repository: MolecularSequenceRepository | FHIRList[MolecularSequenceRepository]
    pointer: Reference | FHIRList[Reference]
    structureVariant: MolecularSequenceStructureVariant | FHIRList[MolecularSequenceStructureVariant]


class NamingSystemUniqueId(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    value: Optional[String] = None
    preferred: Optional[Boolean] = None
    comment: Optional[String] = None
    period: Optional[Period]


class NamingSystem(FHIRResource):
    _resource_type = "NamingSystem"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'uniqueId'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'contact': 'ContactDetail', 'type_': 'CodeableConcept', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'uniqueId': 'NamingSystemUniqueId'}

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
    type_: Optional[CodeableConcept]
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    usage: Optional[String] = None
    uniqueId: NamingSystemUniqueId | FHIRList[NamingSystemUniqueId]


class NutritionOrderOralDiet(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'type_', 'schedule', 'nutrient', 'texture', 'fluidConsistencyType'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'schedule': 'Timing', 'nutrient': 'NutritionOrderOralDietNutrient', 'texture': 'NutritionOrderOralDietTexture', 'fluidConsistencyType': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: CodeableConcept | FHIRList[CodeableConcept]
    schedule: Timing | FHIRList[Timing]
    nutrient: NutritionOrderOralDietNutrient | FHIRList[NutritionOrderOralDietNutrient]
    texture: NutritionOrderOralDietTexture | FHIRList[NutritionOrderOralDietTexture]
    fluidConsistencyType: CodeableConcept | FHIRList[CodeableConcept]
    instruction: Optional[String] = None


class NutritionOrderOralDietNutrient(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'modifier': 'CodeableConcept', 'amount': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    modifier: Optional[CodeableConcept]
    amount: Optional[Quantity]


class NutritionOrderOralDietTexture(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'modifier': 'CodeableConcept', 'foodType': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    modifier: Optional[CodeableConcept]
    foodType: Optional[CodeableConcept]


class NutritionOrderSupplement(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'schedule'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'schedule': 'Timing', 'quantity': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    productName: Optional[String] = None
    schedule: Timing | FHIRList[Timing]
    quantity: Optional[Quantity]
    instruction: Optional[String] = None


class NutritionOrderEnteralFormula(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'administration'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'baseFormulaType': 'CodeableConcept', 'additiveType': 'CodeableConcept', 'caloricDensity': 'Quantity', 'routeofAdministration': 'CodeableConcept', 'administration': 'NutritionOrderEnteralFormulaAdministration', 'maxVolumeToDeliver': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    baseFormulaType: Optional[CodeableConcept]
    baseFormulaProductName: Optional[String] = None
    additiveType: Optional[CodeableConcept]
    additiveProductName: Optional[String] = None
    caloricDensity: Optional[Quantity]
    routeofAdministration: Optional[CodeableConcept]
    administration: NutritionOrderEnteralFormulaAdministration | FHIRList[NutritionOrderEnteralFormulaAdministration]
    maxVolumeToDeliver: Optional[Quantity]
    administrationInstruction: Optional[String] = None


class NutritionOrderEnteralFormulaAdministration(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'schedule': 'Timing', 'quantity': 'Quantity', 'rateQuantity': 'Quantity', 'rateRatio': 'Ratio'}
    _choice_fields = {'rate': ['rateQuantity', 'rateRatio']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    schedule: Optional[Timing]
    quantity: Optional[Quantity]
    rateQuantity: Optional[Quantity]
    rateRatio: Optional[Ratio]


class NutritionOrder(FHIRResource):
    _resource_type = "NutritionOrder"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'instantiatesCanonical', 'instantiatesUri', 'instantiates', 'allergyIntolerance', 'foodPreferenceModifier', 'excludeFoodModifier', 'supplement', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'patient': 'Reference', 'encounter': 'Reference', 'orderer': 'Reference', 'allergyIntolerance': 'Reference', 'foodPreferenceModifier': 'CodeableConcept', 'excludeFoodModifier': 'CodeableConcept', 'oralDiet': 'NutritionOrderOralDiet', 'supplement': 'NutritionOrderSupplement', 'enteralFormula': 'NutritionOrderEnteralFormula', 'note': 'Annotation'}

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
    oralDiet: Optional[NutritionOrderOralDiet]
    supplement: NutritionOrderSupplement | FHIRList[NutritionOrderSupplement]
    enteralFormula: Optional[NutritionOrderEnteralFormula]
    note: Annotation | FHIRList[Annotation]


class ObservationReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'low': 'Quantity', 'high': 'Quantity', 'type_': 'CodeableConcept', 'appliesTo': 'CodeableConcept', 'age': 'Range'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    low: Optional[Quantity]
    high: Optional[Quantity]
    type_: Optional[CodeableConcept]
    appliesTo: CodeableConcept | FHIRList[CodeableConcept]
    age: Optional[Range]
    text: Optional[String] = None


class ObservationComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueCodeableConcept': 'CodeableConcept', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueSampledData': 'SampledData', 'valuePeriod': 'Period', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept'}
    _choice_fields = {'value': ['valueQuantity', 'valueCodeableConcept', 'valueString', 'valueBoolean', 'valueInteger', 'valueRange', 'valueRatio', 'valueSampledData', 'valueTime', 'valueDateTime', 'valuePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueQuantity: Optional[Quantity]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueSampledData: Optional[SampledData]
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Optional[Period]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    referenceRange: Any = None


class Observation(FHIRResource):
    _resource_type = "Observation"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'effectivePeriod': 'Period', 'effectiveTiming': 'Timing', 'performer': 'Reference', 'valueQuantity': 'Quantity', 'valueCodeableConcept': 'CodeableConcept', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueSampledData': 'SampledData', 'valuePeriod': 'Period', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'ObservationReferenceRange', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'ObservationComponent'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod', 'effectiveTiming', 'effectiveInstant'], 'value': ['valueQuantity', 'valueCodeableConcept', 'valueString', 'valueBoolean', 'valueInteger', 'valueRange', 'valueRatio', 'valueSampledData', 'valueTime', 'valueDateTime', 'valuePeriod']}

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
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    effectiveTiming: Optional[Timing]
    effectiveInstant: Optional[Instant] = None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    valueQuantity: Optional[Quantity]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueSampledData: Optional[SampledData]
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Optional[Period]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: ObservationReferenceRange | FHIRList[ObservationReferenceRange]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: ObservationComponent | FHIRList[ObservationComponent]


class ObservationDefinitionQuantitativeDetails(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'customaryUnit': 'CodeableConcept', 'unit': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    customaryUnit: Optional[CodeableConcept]
    unit: Optional[CodeableConcept]
    conversionFactor: Optional[Decimal] = None
    decimalPrecision: Optional[Integer] = None


class ObservationDefinitionQualifiedInterval(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'range': 'Range', 'context': 'CodeableConcept', 'appliesTo': 'CodeableConcept', 'age': 'Range', 'gestationalAge': 'Range'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    category: Optional[Code] = None
    range: Optional[Range]
    context: Optional[CodeableConcept]
    appliesTo: CodeableConcept | FHIRList[CodeableConcept]
    gender: Optional[Code] = None
    age: Optional[Range]
    gestationalAge: Optional[Range]
    condition: Optional[String] = None


class ObservationDefinition(FHIRResource):
    _resource_type = "ObservationDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'category', 'identifier', 'permittedDataType', 'qualifiedInterval'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'identifier': 'Identifier', 'method': 'CodeableConcept', 'quantitativeDetails': 'ObservationDefinitionQuantitativeDetails', 'qualifiedInterval': 'ObservationDefinitionQualifiedInterval', 'validCodedValueSet': 'Reference', 'normalCodedValueSet': 'Reference', 'abnormalCodedValueSet': 'Reference', 'criticalCodedValueSet': 'Reference'}

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
    quantitativeDetails: Optional[ObservationDefinitionQuantitativeDetails]
    qualifiedInterval: ObservationDefinitionQualifiedInterval | FHIRList[ObservationDefinitionQualifiedInterval]
    validCodedValueSet: Optional[Reference]
    normalCodedValueSet: Optional[Reference]
    abnormalCodedValueSet: Optional[Reference]
    criticalCodedValueSet: Optional[Reference]


class OperationDefinitionParameter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'targetProfile', 'referencedFrom', 'part'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'binding': 'OperationDefinitionParameterBinding', 'referencedFrom': 'OperationDefinitionParameterReferencedFrom'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[Code] = None
    use: Optional[Code] = None
    min: Optional[Integer] = None
    max: Optional[String] = None
    documentation: Optional[String] = None
    type_: Optional[Code] = None
    targetProfile: Canonical | FHIRList[Canonical] = None
    searchType: Optional[Code] = None
    binding: Optional[OperationDefinitionParameterBinding]
    referencedFrom: OperationDefinitionParameterReferencedFrom | FHIRList[OperationDefinitionParameterReferencedFrom]
    part: Any = None


class OperationDefinitionParameterBinding(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    strength: Optional[Code] = None
    valueSet: Optional[Canonical] = None


class OperationDefinitionParameterReferencedFrom(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    source: Optional[String] = None
    sourceId: Optional[String] = None


class OperationDefinitionOverload(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'parameterName'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    parameterName: String | FHIRList[String] = None
    comment: Optional[String] = None


class OperationDefinition(FHIRResource):
    _resource_type = "OperationDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'resource', 'parameter', 'overload'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'parameter': 'OperationDefinitionParameter', 'overload': 'OperationDefinitionOverload'}

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
    type_: Optional[Boolean] = None
    instance: Optional[Boolean] = None
    inputProfile: Optional[Canonical] = None
    outputProfile: Optional[Canonical] = None
    parameter: OperationDefinitionParameter | FHIRList[OperationDefinitionParameter]
    overload: OperationDefinitionOverload | FHIRList[OperationDefinitionOverload]


class OperationOutcomeIssue(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'location', 'expression'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'details': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    severity: Optional[Code] = None
    code: Optional[Code] = None
    details: Optional[CodeableConcept]
    diagnostics: Optional[String] = None
    location: String | FHIRList[String] = None
    expression: String | FHIRList[String] = None


class OperationOutcome(FHIRResource):
    _resource_type = "OperationOutcome"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'issue'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'issue': 'OperationOutcomeIssue'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    issue: OperationOutcomeIssue | FHIRList[OperationOutcomeIssue]


class OrganizationContact(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'telecom'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'purpose': 'CodeableConcept', 'name': 'HumanName', 'telecom': 'ContactPoint', 'address': 'Address'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    purpose: Optional[CodeableConcept]
    name: Optional[HumanName]
    telecom: ContactPoint | FHIRList[ContactPoint]
    address: Optional[Address]


class Organization(FHIRResource):
    _resource_type = "Organization"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'type_', 'alias', 'telecom', 'address', 'contact', 'endpoint'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'telecom': 'ContactPoint', 'address': 'Address', 'partOf': 'Reference', 'contact': 'OrganizationContact', 'endpoint': 'Reference'}

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
    type_: CodeableConcept | FHIRList[CodeableConcept]
    name: Optional[String] = None
    alias: String | FHIRList[String] = None
    telecom: ContactPoint | FHIRList[ContactPoint]
    address: Address | FHIRList[Address]
    partOf: Optional[Reference]
    contact: OrganizationContact | FHIRList[OrganizationContact]
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


class ParametersParameter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'part'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'valueAddress': 'Address', 'valueAge': 'Age', 'valueAnnotation': 'Annotation', 'valueAttachment': 'Attachment', 'valueCodeableConcept': 'CodeableConcept', 'valueCoding': 'Coding', 'valueContactPoint': 'ContactPoint', 'valueCount': 'Count', 'valueDistance': 'Distance', 'valueDuration': 'Duration', 'valueHumanName': 'HumanName', 'valueIdentifier': 'Identifier', 'valueMoney': 'Money', 'valuePeriod': 'Period', 'valueQuantity': 'Quantity', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueReference': 'Reference', 'valueSampledData': 'SampledData', 'valueSignature': 'Signature', 'valueTiming': 'Timing', 'valueContactDetail': 'ContactDetail', 'valueContributor': 'Contributor', 'valueDataRequirement': 'DataRequirement', 'valueExpression': 'Expression', 'valueParameterDefinition': 'ParameterDefinition', 'valueRelatedArtifact': 'RelatedArtifact', 'valueTriggerDefinition': 'TriggerDefinition', 'valueUsageContext': 'UsageContext', 'valueDosage': 'Dosage', 'valueMeta': 'Meta', 'resource': 'Resource'}
    _choice_fields = {'value': ['valueBase64Binary', 'valueBoolean', 'valueCanonical', 'valueCode', 'valueDate', 'valueDateTime', 'valueDecimal', 'valueId', 'valueInstant', 'valueInteger', 'valueMarkdown', 'valueOid', 'valuePositiveInt', 'valueString', 'valueTime', 'valueUnsignedInt', 'valueUri', 'valueUrl', 'valueUuid', 'valueAddress', 'valueAge', 'valueAnnotation', 'valueAttachment', 'valueCodeableConcept', 'valueCoding', 'valueContactPoint', 'valueCount', 'valueDistance', 'valueDuration', 'valueHumanName', 'valueIdentifier', 'valueMoney', 'valuePeriod', 'valueQuantity', 'valueRange', 'valueRatio', 'valueReference', 'valueSampledData', 'valueSignature', 'valueTiming', 'valueContactDetail', 'valueContributor', 'valueDataRequirement', 'valueExpression', 'valueParameterDefinition', 'valueRelatedArtifact', 'valueTriggerDefinition', 'valueUsageContext', 'valueDosage', 'valueMeta']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[String] = None
    valueBase64Binary: Optional[Base64Binary] = None
    valueBoolean: Optional[Boolean] = None
    valueCanonical: Optional[Canonical] = None
    valueCode: Optional[Code] = None
    valueDate: Optional[Date] = None
    valueDateTime: Optional[DateTime] = None
    valueDecimal: Optional[Decimal] = None
    valueId: Optional[Id] = None
    valueInstant: Optional[Instant] = None
    valueInteger: Optional[Integer] = None
    valueMarkdown: Optional[Markdown] = None
    valueOid: Optional[Oid] = None
    valuePositiveInt: Optional[PositiveInt] = None
    valueString: Optional[String] = None
    valueTime: Optional[Time] = None
    valueUnsignedInt: Optional[UnsignedInt] = None
    valueUri: Optional[Uri] = None
    valueUrl: Optional[Url] = None
    valueUuid: Optional[Uuid] = None
    valueAddress: Optional[Address]
    valueAge: Optional[Age]
    valueAnnotation: Optional[Annotation]
    valueAttachment: Optional[Attachment]
    valueCodeableConcept: Optional[CodeableConcept]
    valueCoding: Optional[Coding]
    valueContactPoint: Optional[ContactPoint]
    valueCount: Optional[Count]
    valueDistance: Optional[Distance]
    valueDuration: Optional[Duration]
    valueHumanName: Optional[HumanName]
    valueIdentifier: Optional[Identifier]
    valueMoney: Optional[Money]
    valuePeriod: Optional[Period]
    valueQuantity: Optional[Quantity]
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueReference: Optional[Reference]
    valueSampledData: Optional[SampledData]
    valueSignature: Optional[Signature]
    valueTiming: Optional[Timing]
    valueContactDetail: Optional[ContactDetail]
    valueContributor: Optional[Contributor]
    valueDataRequirement: Optional[DataRequirement]
    valueExpression: Optional[Expression]
    valueParameterDefinition: Optional[ParameterDefinition]
    valueRelatedArtifact: Optional[RelatedArtifact]
    valueTriggerDefinition: Optional[TriggerDefinition]
    valueUsageContext: Optional[UsageContext]
    valueDosage: Optional[Dosage]
    valueMeta: Optional[Meta]
    resource: Optional[Resource]
    part: Any = None


class Parameters(FHIRResource):
    _resource_type = "Parameters"
    _list_fields = {'parameter'}
    _field_types = {'meta': 'Meta', 'parameter': 'ParametersParameter'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    parameter: ParametersParameter | FHIRList[ParametersParameter]


class PatientContact(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'relationship', 'telecom'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'relationship': 'CodeableConcept', 'name': 'HumanName', 'telecom': 'ContactPoint', 'address': 'Address', 'organization': 'Reference', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    relationship: CodeableConcept | FHIRList[CodeableConcept]
    name: Optional[HumanName]
    telecom: ContactPoint | FHIRList[ContactPoint]
    address: Optional[Address]
    gender: Optional[Code] = None
    organization: Optional[Reference]
    period: Optional[Period]


class PatientCommunication(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'language': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    language: Optional[CodeableConcept]
    preferred: Optional[Boolean] = None


class PatientLink(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'other': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    other: Optional[Reference]
    type_: Optional[Code] = None


class Patient(FHIRResource):
    _resource_type = "Patient"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'name', 'telecom', 'address', 'photo', 'contact', 'communication', 'generalPractitioner', 'link'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'name': 'HumanName', 'telecom': 'ContactPoint', 'address': 'Address', 'maritalStatus': 'CodeableConcept', 'photo': 'Attachment', 'contact': 'PatientContact', 'communication': 'PatientCommunication', 'generalPractitioner': 'Reference', 'managingOrganization': 'Reference', 'link': 'PatientLink'}
    _choice_fields = {'deceased': ['deceasedBoolean', 'deceasedDateTime'], 'multipleBirth': ['multipleBirthBoolean', 'multipleBirthInteger']}

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
    deceasedBoolean: Optional[Boolean] = None
    deceasedDateTime: Optional[DateTime] = None
    address: Address | FHIRList[Address]
    maritalStatus: Optional[CodeableConcept]
    multipleBirthBoolean: Optional[Boolean] = None
    multipleBirthInteger: Optional[Integer] = None
    photo: Attachment | FHIRList[Attachment]
    contact: PatientContact | FHIRList[PatientContact]
    communication: PatientCommunication | FHIRList[PatientCommunication]
    generalPractitioner: Reference | FHIRList[Reference]
    managingOrganization: Optional[Reference]
    link: PatientLink | FHIRList[PatientLink]


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


class PaymentReconciliationDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'predecessor': 'Identifier', 'type_': 'CodeableConcept', 'request': 'Reference', 'submitter': 'Reference', 'response': 'Reference', 'responsible': 'Reference', 'payee': 'Reference', 'amount': 'Money'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Identifier]
    predecessor: Optional[Identifier]
    type_: Optional[CodeableConcept]
    request: Optional[Reference]
    submitter: Optional[Reference]
    response: Optional[Reference]
    date: Optional[Date] = None
    responsible: Optional[Reference]
    payee: Optional[Reference]
    amount: Optional[Money]


class PaymentReconciliationProcessNote(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    text: Optional[String] = None


class PaymentReconciliation(FHIRResource):
    _resource_type = "PaymentReconciliation"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'detail', 'processNote'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'period': 'Period', 'paymentIssuer': 'Reference', 'request': 'Reference', 'requestor': 'Reference', 'paymentAmount': 'Money', 'paymentIdentifier': 'Identifier', 'detail': 'PaymentReconciliationDetail', 'formCode': 'CodeableConcept', 'processNote': 'PaymentReconciliationProcessNote'}

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
    detail: PaymentReconciliationDetail | FHIRList[PaymentReconciliationDetail]
    formCode: Optional[CodeableConcept]
    processNote: PaymentReconciliationProcessNote | FHIRList[PaymentReconciliationProcessNote]


class PersonLink(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'target': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    target: Optional[Reference]
    assurance: Optional[Code] = None


class Person(FHIRResource):
    _resource_type = "Person"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'name', 'telecom', 'address', 'link'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'name': 'HumanName', 'telecom': 'ContactPoint', 'address': 'Address', 'photo': 'Attachment', 'managingOrganization': 'Reference', 'link': 'PersonLink'}

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
    link: PersonLink | FHIRList[PersonLink]


class PlanDefinitionGoal(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'addresses', 'documentation', 'target'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'category': 'CodeableConcept', 'description': 'CodeableConcept', 'priority': 'CodeableConcept', 'start': 'CodeableConcept', 'addresses': 'CodeableConcept', 'documentation': 'RelatedArtifact', 'target': 'PlanDefinitionGoalTarget'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    category: Optional[CodeableConcept]
    description: Optional[CodeableConcept]
    priority: Optional[CodeableConcept]
    start: Optional[CodeableConcept]
    addresses: CodeableConcept | FHIRList[CodeableConcept]
    documentation: RelatedArtifact | FHIRList[RelatedArtifact]
    target: PlanDefinitionGoalTarget | FHIRList[PlanDefinitionGoalTarget]


class PlanDefinitionGoalTarget(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'measure': 'CodeableConcept', 'detailQuantity': 'Quantity', 'detailRange': 'Range', 'detailCodeableConcept': 'CodeableConcept', 'due': 'Duration'}
    _choice_fields = {'detail': ['detailQuantity', 'detailRange', 'detailCodeableConcept']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    measure: Optional[CodeableConcept]
    detailQuantity: Optional[Quantity]
    detailRange: Optional[Range]
    detailCodeableConcept: Optional[CodeableConcept]
    due: Optional[Duration]


class PlanDefinitionAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'reason', 'documentation', 'goalId', 'trigger', 'condition', 'input', 'output', 'relatedAction', 'participant', 'dynamicValue', 'action'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'reason': 'CodeableConcept', 'documentation': 'RelatedArtifact', 'subjectCodeableConcept': 'CodeableConcept', 'subjectReference': 'Reference', 'trigger': 'TriggerDefinition', 'condition': 'PlanDefinitionActionCondition', 'input': 'DataRequirement', 'output': 'DataRequirement', 'relatedAction': 'PlanDefinitionActionRelatedAction', 'timingAge': 'Age', 'timingPeriod': 'Period', 'timingDuration': 'Duration', 'timingRange': 'Range', 'timingTiming': 'Timing', 'participant': 'PlanDefinitionActionParticipant', 'type_': 'CodeableConcept', 'dynamicValue': 'PlanDefinitionActionDynamicValue'}
    _choice_fields = {'definition': ['definitionCanonical', 'definitionUri'], 'subject': ['subjectCodeableConcept', 'subjectReference'], 'timing': ['timingDateTime', 'timingAge', 'timingPeriod', 'timingDuration', 'timingRange', 'timingTiming']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    prefix: Optional[String] = None
    title: Optional[String] = None
    description: Optional[String] = None
    textEquivalent: Optional[String] = None
    priority: Optional[Code] = None
    code: CodeableConcept | FHIRList[CodeableConcept]
    reason: CodeableConcept | FHIRList[CodeableConcept]
    documentation: RelatedArtifact | FHIRList[RelatedArtifact]
    goalId: Id | FHIRList[Id] = None
    subjectCodeableConcept: Optional[CodeableConcept]
    subjectReference: Optional[Reference]
    trigger: TriggerDefinition | FHIRList[TriggerDefinition]
    condition: PlanDefinitionActionCondition | FHIRList[PlanDefinitionActionCondition]
    input: DataRequirement | FHIRList[DataRequirement]
    output: DataRequirement | FHIRList[DataRequirement]
    relatedAction: PlanDefinitionActionRelatedAction | FHIRList[PlanDefinitionActionRelatedAction]
    timingDateTime: Optional[DateTime] = None
    timingAge: Optional[Age]
    timingPeriod: Optional[Period]
    timingDuration: Optional[Duration]
    timingRange: Optional[Range]
    timingTiming: Optional[Timing]
    participant: PlanDefinitionActionParticipant | FHIRList[PlanDefinitionActionParticipant]
    type_: Optional[CodeableConcept]
    groupingBehavior: Optional[Code] = None
    selectionBehavior: Optional[Code] = None
    requiredBehavior: Optional[Code] = None
    precheckBehavior: Optional[Code] = None
    cardinalityBehavior: Optional[Code] = None
    definitionCanonical: Optional[Canonical] = None
    definitionUri: Optional[Uri] = None
    transform: Optional[Canonical] = None
    dynamicValue: PlanDefinitionActionDynamicValue | FHIRList[PlanDefinitionActionDynamicValue]
    action: Any = None


class PlanDefinitionActionCondition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    kind: Optional[Code] = None
    expression: Optional[Expression]


class PlanDefinitionActionRelatedAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'offsetDuration': 'Duration', 'offsetRange': 'Range'}
    _choice_fields = {'offset': ['offsetDuration', 'offsetRange']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    actionId: Optional[Id] = None
    relationship: Optional[Code] = None
    offsetDuration: Optional[Duration]
    offsetRange: Optional[Range]


class PlanDefinitionActionParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'role': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    role: Optional[CodeableConcept]


class PlanDefinitionActionDynamicValue(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    path: Optional[String] = None
    expression: Optional[Expression]


class PlanDefinition(FHIRResource):
    _resource_type = "PlanDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'library', 'goal', 'action'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'subjectCodeableConcept': 'CodeableConcept', 'subjectReference': 'Reference', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'goal': 'PlanDefinitionGoal', 'action': 'PlanDefinitionAction'}
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

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
    type_: Optional[CodeableConcept]
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    subjectCodeableConcept: Optional[CodeableConcept]
    subjectReference: Optional[Reference]
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
    goal: PlanDefinitionGoal | FHIRList[PlanDefinitionGoal]
    action: PlanDefinitionAction | FHIRList[PlanDefinitionAction]


class PractitionerQualification(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'identifier'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'code': 'CodeableConcept', 'period': 'Period', 'issuer': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    code: Optional[CodeableConcept]
    period: Optional[Period]
    issuer: Optional[Reference]


class Practitioner(FHIRResource):
    _resource_type = "Practitioner"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'name', 'telecom', 'address', 'photo', 'qualification', 'communication'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'name': 'HumanName', 'telecom': 'ContactPoint', 'address': 'Address', 'photo': 'Attachment', 'qualification': 'PractitionerQualification', 'communication': 'CodeableConcept'}

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
    qualification: PractitionerQualification | FHIRList[PractitionerQualification]
    communication: CodeableConcept | FHIRList[CodeableConcept]


class PractitionerRoleAvailableTime(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'daysOfWeek'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    daysOfWeek: Code | FHIRList[Code] = None
    allDay: Optional[Boolean] = None
    availableStartTime: Optional[Time] = None
    availableEndTime: Optional[Time] = None


class PractitionerRoleNotAvailable(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'during': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    description: Optional[String] = None
    during: Optional[Period]


class PractitionerRole(FHIRResource):
    _resource_type = "PractitionerRole"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'code', 'specialty', 'location', 'healthcareService', 'telecom', 'availableTime', 'notAvailable', 'endpoint'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'period': 'Period', 'practitioner': 'Reference', 'organization': 'Reference', 'code': 'CodeableConcept', 'specialty': 'CodeableConcept', 'location': 'Reference', 'healthcareService': 'Reference', 'telecom': 'ContactPoint', 'availableTime': 'PractitionerRoleAvailableTime', 'notAvailable': 'PractitionerRoleNotAvailable', 'endpoint': 'Reference'}

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
    availableTime: PractitionerRoleAvailableTime | FHIRList[PractitionerRoleAvailableTime]
    notAvailable: PractitionerRoleNotAvailable | FHIRList[PractitionerRoleNotAvailable]
    availabilityExceptions: Optional[String] = None
    endpoint: Reference | FHIRList[Reference]


class ProcedurePerformer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'function': 'CodeableConcept', 'actor': 'Reference', 'onBehalfOf': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    function: Optional[CodeableConcept]
    actor: Optional[Reference]
    onBehalfOf: Optional[Reference]


class ProcedureFocalDevice(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'action': 'CodeableConcept', 'manipulated': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    action: Optional[CodeableConcept]
    manipulated: Optional[Reference]


class Procedure(FHIRResource):
    _resource_type = "Procedure"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'instantiatesCanonical', 'instantiatesUri', 'basedOn', 'partOf', 'performer', 'reasonCode', 'reasonReference', 'bodySite', 'report', 'complication', 'complicationDetail', 'followUp', 'note', 'focalDevice', 'usedReference', 'usedCode'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'statusReason': 'CodeableConcept', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'performedPeriod': 'Period', 'performedAge': 'Age', 'performedRange': 'Range', 'recorder': 'Reference', 'asserter': 'Reference', 'performer': 'ProcedurePerformer', 'location': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'bodySite': 'CodeableConcept', 'outcome': 'CodeableConcept', 'report': 'Reference', 'complication': 'CodeableConcept', 'complicationDetail': 'Reference', 'followUp': 'CodeableConcept', 'note': 'Annotation', 'focalDevice': 'ProcedureFocalDevice', 'usedReference': 'Reference', 'usedCode': 'CodeableConcept'}
    _choice_fields = {'performed': ['performedDateTime', 'performedPeriod', 'performedString', 'performedAge', 'performedRange']}

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
    performedDateTime: Optional[DateTime] = None
    performedPeriod: Optional[Period]
    performedString: Optional[String] = None
    performedAge: Optional[Age]
    performedRange: Optional[Range]
    recorder: Optional[Reference]
    asserter: Optional[Reference]
    performer: ProcedurePerformer | FHIRList[ProcedurePerformer]
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
    focalDevice: ProcedureFocalDevice | FHIRList[ProcedureFocalDevice]
    usedReference: Reference | FHIRList[Reference]
    usedCode: CodeableConcept | FHIRList[CodeableConcept]


class ProvenanceAgent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'role'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'role': 'CodeableConcept', 'who': 'Reference', 'onBehalfOf': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    role: CodeableConcept | FHIRList[CodeableConcept]
    who: Optional[Reference]
    onBehalfOf: Optional[Reference]


class ProvenanceEntity(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'agent'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'what': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    role: Optional[Code] = None
    what: Optional[Reference]
    agent: Any = None


class Provenance(FHIRResource):
    _resource_type = "Provenance"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'target', 'policy', 'reason', 'agent', 'entity', 'signature'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'target': 'Reference', 'occurredPeriod': 'Period', 'location': 'Reference', 'reason': 'CodeableConcept', 'activity': 'CodeableConcept', 'agent': 'ProvenanceAgent', 'entity': 'ProvenanceEntity', 'signature': 'Signature'}
    _choice_fields = {'occurred': ['occurredPeriod', 'occurredDateTime']}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    target: Reference | FHIRList[Reference]
    occurredPeriod: Optional[Period]
    occurredDateTime: Optional[DateTime] = None
    recorded: Optional[Instant] = None
    policy: Uri | FHIRList[Uri] = None
    location: Optional[Reference]
    reason: CodeableConcept | FHIRList[CodeableConcept]
    activity: Optional[CodeableConcept]
    agent: ProvenanceAgent | FHIRList[ProvenanceAgent]
    entity: ProvenanceEntity | FHIRList[ProvenanceEntity]
    signature: Signature | FHIRList[Signature]


class QuestionnaireItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'enableWhen', 'answerOption', 'initial', 'item'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'Coding', 'enableWhen': 'QuestionnaireItemEnableWhen', 'answerOption': 'QuestionnaireItemAnswerOption', 'initial': 'QuestionnaireItemInitial'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    linkId: Optional[String] = None
    definition: Optional[Uri] = None
    code: Coding | FHIRList[Coding]
    prefix: Optional[String] = None
    text: Optional[String] = None
    type_: Optional[Code] = None
    enableWhen: QuestionnaireItemEnableWhen | FHIRList[QuestionnaireItemEnableWhen]
    enableBehavior: Optional[Code] = None
    required: Optional[Boolean] = None
    repeats: Optional[Boolean] = None
    readOnly: Optional[Boolean] = None
    maxLength: Optional[Integer] = None
    answerValueSet: Optional[Canonical] = None
    answerOption: QuestionnaireItemAnswerOption | FHIRList[QuestionnaireItemAnswerOption]
    initial: QuestionnaireItemInitial | FHIRList[QuestionnaireItemInitial]
    item: Any = None


class QuestionnaireItemEnableWhen(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'answerCoding': 'Coding', 'answerQuantity': 'Quantity', 'answerReference': 'Reference'}
    _choice_fields = {'answer': ['answerBoolean', 'answerDecimal', 'answerInteger', 'answerDate', 'answerDateTime', 'answerTime', 'answerString', 'answerCoding', 'answerQuantity', 'answerReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    question: Optional[String] = None
    operator: Optional[Code] = None
    answerBoolean: Optional[Boolean] = None
    answerDecimal: Optional[Decimal] = None
    answerInteger: Optional[Integer] = None
    answerDate: Optional[Date] = None
    answerDateTime: Optional[DateTime] = None
    answerTime: Optional[Time] = None
    answerString: Optional[String] = None
    answerCoding: Optional[Coding]
    answerQuantity: Optional[Quantity]
    answerReference: Optional[Reference]


class QuestionnaireItemAnswerOption(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'valueCoding': 'Coding', 'valueReference': 'Reference'}
    _choice_fields = {'value': ['valueInteger', 'valueDate', 'valueTime', 'valueString', 'valueCoding', 'valueReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    valueInteger: Optional[Integer] = None
    valueDate: Optional[Date] = None
    valueTime: Optional[Time] = None
    valueString: Optional[String] = None
    valueCoding: Optional[Coding]
    valueReference: Optional[Reference]
    initialSelected: Optional[Boolean] = None


class QuestionnaireItemInitial(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'valueAttachment': 'Attachment', 'valueCoding': 'Coding', 'valueQuantity': 'Quantity', 'valueReference': 'Reference'}
    _choice_fields = {'value': ['valueBoolean', 'valueDecimal', 'valueInteger', 'valueDate', 'valueDateTime', 'valueTime', 'valueString', 'valueUri', 'valueAttachment', 'valueCoding', 'valueQuantity', 'valueReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    valueBoolean: Optional[Boolean] = None
    valueDecimal: Optional[Decimal] = None
    valueInteger: Optional[Integer] = None
    valueDate: Optional[Date] = None
    valueDateTime: Optional[DateTime] = None
    valueTime: Optional[Time] = None
    valueString: Optional[String] = None
    valueUri: Optional[Uri] = None
    valueAttachment: Optional[Attachment]
    valueCoding: Optional[Coding]
    valueQuantity: Optional[Quantity]
    valueReference: Optional[Reference]


class Questionnaire(FHIRResource):
    _resource_type = "Questionnaire"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'derivedFrom', 'subjectType', 'contact', 'useContext', 'jurisdiction', 'code', 'item'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'code': 'Coding', 'item': 'QuestionnaireItem'}

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
    item: QuestionnaireItem | FHIRList[QuestionnaireItem]


class QuestionnaireResponseItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'answer', 'item'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'answer': 'QuestionnaireResponseItemAnswer'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    linkId: Optional[String] = None
    definition: Optional[Uri] = None
    text: Optional[String] = None
    answer: QuestionnaireResponseItemAnswer | FHIRList[QuestionnaireResponseItemAnswer]
    item: Any = None


class QuestionnaireResponseItemAnswer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'item'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'valueAttachment': 'Attachment', 'valueCoding': 'Coding', 'valueQuantity': 'Quantity', 'valueReference': 'Reference'}
    _choice_fields = {'value': ['valueBoolean', 'valueDecimal', 'valueInteger', 'valueDate', 'valueDateTime', 'valueTime', 'valueString', 'valueUri', 'valueAttachment', 'valueCoding', 'valueQuantity', 'valueReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    valueBoolean: Optional[Boolean] = None
    valueDecimal: Optional[Decimal] = None
    valueInteger: Optional[Integer] = None
    valueDate: Optional[Date] = None
    valueDateTime: Optional[DateTime] = None
    valueTime: Optional[Time] = None
    valueString: Optional[String] = None
    valueUri: Optional[Uri] = None
    valueAttachment: Optional[Attachment]
    valueCoding: Optional[Coding]
    valueQuantity: Optional[Quantity]
    valueReference: Optional[Reference]
    item: Any = None


class QuestionnaireResponse(FHIRResource):
    _resource_type = "QuestionnaireResponse"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'basedOn', 'partOf', 'item'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'subject': 'Reference', 'encounter': 'Reference', 'author': 'Reference', 'source': 'Reference', 'item': 'QuestionnaireResponseItem'}

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
    item: QuestionnaireResponseItem | FHIRList[QuestionnaireResponseItem]


class RelatedPersonCommunication(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'language': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    language: Optional[CodeableConcept]
    preferred: Optional[Boolean] = None


class RelatedPerson(FHIRResource):
    _resource_type = "RelatedPerson"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'relationship', 'name', 'telecom', 'address', 'photo', 'communication'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'patient': 'Reference', 'relationship': 'CodeableConcept', 'name': 'HumanName', 'telecom': 'ContactPoint', 'address': 'Address', 'photo': 'Attachment', 'period': 'Period', 'communication': 'RelatedPersonCommunication'}

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
    communication: RelatedPersonCommunication | FHIRList[RelatedPersonCommunication]


class RequestGroupAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'documentation', 'condition', 'relatedAction', 'participant', 'action'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'documentation': 'RelatedArtifact', 'condition': 'RequestGroupActionCondition', 'relatedAction': 'RequestGroupActionRelatedAction', 'timingAge': 'Age', 'timingPeriod': 'Period', 'timingDuration': 'Duration', 'timingRange': 'Range', 'timingTiming': 'Timing', 'participant': 'Reference', 'type_': 'CodeableConcept', 'resource': 'Reference'}
    _choice_fields = {'timing': ['timingDateTime', 'timingAge', 'timingPeriod', 'timingDuration', 'timingRange', 'timingTiming']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    prefix: Optional[String] = None
    title: Optional[String] = None
    description: Optional[String] = None
    textEquivalent: Optional[String] = None
    priority: Optional[Code] = None
    code: CodeableConcept | FHIRList[CodeableConcept]
    documentation: RelatedArtifact | FHIRList[RelatedArtifact]
    condition: RequestGroupActionCondition | FHIRList[RequestGroupActionCondition]
    relatedAction: RequestGroupActionRelatedAction | FHIRList[RequestGroupActionRelatedAction]
    timingDateTime: Optional[DateTime] = None
    timingAge: Optional[Age]
    timingPeriod: Optional[Period]
    timingDuration: Optional[Duration]
    timingRange: Optional[Range]
    timingTiming: Optional[Timing]
    participant: Reference | FHIRList[Reference]
    type_: Optional[CodeableConcept]
    groupingBehavior: Optional[Code] = None
    selectionBehavior: Optional[Code] = None
    requiredBehavior: Optional[Code] = None
    precheckBehavior: Optional[Code] = None
    cardinalityBehavior: Optional[Code] = None
    resource: Optional[Reference]
    action: Any = None


class RequestGroupActionCondition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    kind: Optional[Code] = None
    expression: Optional[Expression]


class RequestGroupActionRelatedAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'offsetDuration': 'Duration', 'offsetRange': 'Range'}
    _choice_fields = {'offset': ['offsetDuration', 'offsetRange']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    actionId: Optional[Id] = None
    relationship: Optional[Code] = None
    offsetDuration: Optional[Duration]
    offsetRange: Optional[Range]


class RequestGroup(FHIRResource):
    _resource_type = "RequestGroup"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'instantiatesCanonical', 'instantiatesUri', 'basedOn', 'replaces', 'reasonCode', 'reasonReference', 'note', 'action'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'replaces': 'Reference', 'groupIdentifier': 'Identifier', 'code': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'author': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'note': 'Annotation', 'action': 'RequestGroupAction'}

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
    action: RequestGroupAction | FHIRList[RequestGroupAction]


class ResearchDefinition(FHIRResource):
    _resource_type = "ResearchDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'comment', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'library'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'subjectCodeableConcept': 'CodeableConcept', 'subjectReference': 'Reference', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'population': 'Reference', 'exposure': 'Reference', 'exposureAlternative': 'Reference', 'outcome': 'Reference'}
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

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
    subjectCodeableConcept: Optional[CodeableConcept]
    subjectReference: Optional[Reference]
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


class ResearchElementDefinitionCharacteristic(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'usageContext'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'definitionCodeableConcept': 'CodeableConcept', 'definitionExpression': 'Expression', 'definitionDataRequirement': 'DataRequirement', 'usageContext': 'UsageContext', 'unitOfMeasure': 'CodeableConcept', 'studyEffectivePeriod': 'Period', 'studyEffectiveDuration': 'Duration', 'studyEffectiveTiming': 'Timing', 'studyEffectiveTimeFromStart': 'Duration', 'participantEffectivePeriod': 'Period', 'participantEffectiveDuration': 'Duration', 'participantEffectiveTiming': 'Timing', 'participantEffectiveTimeFromStart': 'Duration'}
    _choice_fields = {'definition': ['definitionCodeableConcept', 'definitionCanonical', 'definitionExpression', 'definitionDataRequirement'], 'participantEffective': ['participantEffectiveDateTime', 'participantEffectivePeriod', 'participantEffectiveDuration', 'participantEffectiveTiming'], 'studyEffective': ['studyEffectiveDateTime', 'studyEffectivePeriod', 'studyEffectiveDuration', 'studyEffectiveTiming']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    definitionCodeableConcept: Optional[CodeableConcept]
    definitionCanonical: Optional[Canonical] = None
    definitionExpression: Optional[Expression]
    definitionDataRequirement: Optional[DataRequirement]
    usageContext: UsageContext | FHIRList[UsageContext]
    exclude: Optional[Boolean] = None
    unitOfMeasure: Optional[CodeableConcept]
    studyEffectiveDescription: Optional[String] = None
    studyEffectiveDateTime: Optional[DateTime] = None
    studyEffectivePeriod: Optional[Period]
    studyEffectiveDuration: Optional[Duration]
    studyEffectiveTiming: Optional[Timing]
    studyEffectiveTimeFromStart: Optional[Duration]
    studyEffectiveGroupMeasure: Optional[Code] = None
    participantEffectiveDescription: Optional[String] = None
    participantEffectiveDateTime: Optional[DateTime] = None
    participantEffectivePeriod: Optional[Period]
    participantEffectiveDuration: Optional[Duration]
    participantEffectiveTiming: Optional[Timing]
    participantEffectiveTimeFromStart: Optional[Duration]
    participantEffectiveGroupMeasure: Optional[Code] = None


class ResearchElementDefinition(FHIRResource):
    _resource_type = "ResearchElementDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'comment', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'library', 'characteristic'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'subjectCodeableConcept': 'CodeableConcept', 'subjectReference': 'Reference', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'characteristic': 'ResearchElementDefinitionCharacteristic'}
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

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
    subjectCodeableConcept: Optional[CodeableConcept]
    subjectReference: Optional[Reference]
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
    type_: Optional[Code] = None
    variableType: Optional[Code] = None
    characteristic: ResearchElementDefinitionCharacteristic | FHIRList[ResearchElementDefinitionCharacteristic]


class ResearchStudyArm(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[String] = None
    type_: Optional[CodeableConcept]
    description: Optional[String] = None


class ResearchStudyObjective(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[String] = None
    type_: Optional[CodeableConcept]


class ResearchStudy(FHIRResource):
    _resource_type = "ResearchStudy"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'protocol', 'partOf', 'category', 'focus', 'condition', 'contact', 'relatedArtifact', 'keyword', 'location', 'enrollment', 'site', 'note', 'arm', 'objective'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'protocol': 'Reference', 'partOf': 'Reference', 'primaryPurposeType': 'CodeableConcept', 'phase': 'CodeableConcept', 'category': 'CodeableConcept', 'focus': 'CodeableConcept', 'condition': 'CodeableConcept', 'contact': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'keyword': 'CodeableConcept', 'location': 'CodeableConcept', 'enrollment': 'Reference', 'period': 'Period', 'sponsor': 'Reference', 'principalInvestigator': 'Reference', 'site': 'Reference', 'reasonStopped': 'CodeableConcept', 'note': 'Annotation', 'arm': 'ResearchStudyArm', 'objective': 'ResearchStudyObjective'}

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
    arm: ResearchStudyArm | FHIRList[ResearchStudyArm]
    objective: ResearchStudyObjective | FHIRList[ResearchStudyObjective]


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


class RiskAssessmentPrediction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'outcome': 'CodeableConcept', 'probabilityRange': 'Range', 'qualitativeRisk': 'CodeableConcept', 'whenPeriod': 'Period', 'whenRange': 'Range'}
    _choice_fields = {'probability': ['probabilityDecimal', 'probabilityRange'], 'when': ['whenPeriod', 'whenRange']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    outcome: Optional[CodeableConcept]
    probabilityDecimal: Optional[Decimal] = None
    probabilityRange: Optional[Range]
    qualitativeRisk: Optional[CodeableConcept]
    relativeRisk: Optional[Decimal] = None
    whenPeriod: Optional[Period]
    whenRange: Optional[Range]
    rationale: Optional[String] = None


class RiskAssessment(FHIRResource):
    _resource_type = "RiskAssessment"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'reasonCode', 'reasonReference', 'basis', 'prediction', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'parent': 'Reference', 'method': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'occurrencePeriod': 'Period', 'condition': 'Reference', 'performer': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'basis': 'Reference', 'prediction': 'RiskAssessmentPrediction', 'note': 'Annotation'}
    _choice_fields = {'occurrence': ['occurrenceDateTime', 'occurrencePeriod']}

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
    occurrenceDateTime: Optional[DateTime] = None
    occurrencePeriod: Optional[Period]
    condition: Optional[Reference]
    performer: Optional[Reference]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    basis: Reference | FHIRList[Reference]
    prediction: RiskAssessmentPrediction | FHIRList[RiskAssessmentPrediction]
    mitigation: Optional[String] = None
    note: Annotation | FHIRList[Annotation]


class RiskEvidenceSynthesisSampleSize(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    description: Optional[String] = None
    numberOfStudies: Optional[Integer] = None
    numberOfParticipants: Optional[Integer] = None


class RiskEvidenceSynthesisRiskEstimate(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'precisionEstimate'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'unitOfMeasure': 'CodeableConcept', 'precisionEstimate': 'RiskEvidenceSynthesisRiskEstimatePrecisionEstimate'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    description: Optional[String] = None
    type_: Optional[CodeableConcept]
    value: Optional[Decimal] = None
    unitOfMeasure: Optional[CodeableConcept]
    denominatorCount: Optional[Integer] = None
    numeratorCount: Optional[Integer] = None
    precisionEstimate: RiskEvidenceSynthesisRiskEstimatePrecisionEstimate | FHIRList[RiskEvidenceSynthesisRiskEstimatePrecisionEstimate]


class RiskEvidenceSynthesisRiskEstimatePrecisionEstimate(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    level: Optional[Decimal] = None
    from_: Optional[Decimal] = None
    to: Optional[Decimal] = None


class RiskEvidenceSynthesisCertainty(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'rating', 'note', 'certaintySubcomponent'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'rating': 'CodeableConcept', 'note': 'Annotation', 'certaintySubcomponent': 'RiskEvidenceSynthesisCertaintyCertaintySubcomponent'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    rating: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    certaintySubcomponent: RiskEvidenceSynthesisCertaintyCertaintySubcomponent | FHIRList[RiskEvidenceSynthesisCertaintyCertaintySubcomponent]


class RiskEvidenceSynthesisCertaintyCertaintySubcomponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'rating', 'note'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'rating': 'CodeableConcept', 'note': 'Annotation'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    rating: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]


class RiskEvidenceSynthesis(FHIRResource):
    _resource_type = "RiskEvidenceSynthesis"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'note', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'certainty'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'note': 'Annotation', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'synthesisType': 'CodeableConcept', 'studyType': 'CodeableConcept', 'population': 'Reference', 'exposure': 'Reference', 'outcome': 'Reference', 'sampleSize': 'RiskEvidenceSynthesisSampleSize', 'riskEstimate': 'RiskEvidenceSynthesisRiskEstimate', 'certainty': 'RiskEvidenceSynthesisCertainty'}

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
    sampleSize: Optional[RiskEvidenceSynthesisSampleSize]
    riskEstimate: Optional[RiskEvidenceSynthesisRiskEstimate]
    certainty: RiskEvidenceSynthesisCertainty | FHIRList[RiskEvidenceSynthesisCertainty]


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


class SearchParameterComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    definition: Optional[Canonical] = None
    expression: Optional[String] = None


class SearchParameter(FHIRResource):
    _resource_type = "SearchParameter"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'base', 'target', 'comparator', 'modifier', 'chain', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'component': 'SearchParameterComponent'}

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
    type_: Optional[Code] = None
    expression: Optional[String] = None
    xpath: Optional[String] = None
    xpathUsage: Optional[Code] = None
    target: Code | FHIRList[Code] = None
    multipleOr: Optional[Boolean] = None
    multipleAnd: Optional[Boolean] = None
    comparator: Code | FHIRList[Code] = None
    modifier: Code | FHIRList[Code] = None
    chain: String | FHIRList[String] = None
    component: SearchParameterComponent | FHIRList[SearchParameterComponent]


class ServiceRequest(FHIRResource):
    _resource_type = "ServiceRequest"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'instantiatesCanonical', 'instantiatesUri', 'basedOn', 'replaces', 'category', 'orderDetail', 'performer', 'locationCode', 'locationReference', 'reasonCode', 'reasonReference', 'insurance', 'supportingInfo', 'specimen', 'bodySite', 'note', 'relevantHistory'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'replaces': 'Reference', 'requisition': 'Identifier', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'orderDetail': 'CodeableConcept', 'quantityQuantity': 'Quantity', 'quantityRatio': 'Ratio', 'quantityRange': 'Range', 'subject': 'Reference', 'encounter': 'Reference', 'occurrencePeriod': 'Period', 'occurrenceTiming': 'Timing', 'asNeededCodeableConcept': 'CodeableConcept', 'requester': 'Reference', 'performerType': 'CodeableConcept', 'performer': 'Reference', 'locationCode': 'CodeableConcept', 'locationReference': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'insurance': 'Reference', 'supportingInfo': 'Reference', 'specimen': 'Reference', 'bodySite': 'CodeableConcept', 'note': 'Annotation', 'relevantHistory': 'Reference'}
    _choice_fields = {'asNeeded': ['asNeededBoolean', 'asNeededCodeableConcept'], 'occurrence': ['occurrenceDateTime', 'occurrencePeriod', 'occurrenceTiming'], 'quantity': ['quantityQuantity', 'quantityRatio', 'quantityRange']}

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
    quantityQuantity: Optional[Quantity]
    quantityRatio: Optional[Ratio]
    quantityRange: Optional[Range]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    occurrenceDateTime: Optional[DateTime] = None
    occurrencePeriod: Optional[Period]
    occurrenceTiming: Optional[Timing]
    asNeededBoolean: Optional[Boolean] = None
    asNeededCodeableConcept: Optional[CodeableConcept]
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


class SpecimenCollection(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'collector': 'Reference', 'collectedPeriod': 'Period', 'duration': 'Duration', 'quantity': 'Quantity', 'method': 'CodeableConcept', 'bodySite': 'CodeableConcept', 'fastingStatusCodeableConcept': 'CodeableConcept', 'fastingStatusDuration': 'Duration'}
    _choice_fields = {'collected': ['collectedDateTime', 'collectedPeriod'], 'fastingStatus': ['fastingStatusCodeableConcept', 'fastingStatusDuration']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    collector: Optional[Reference]
    collectedDateTime: Optional[DateTime] = None
    collectedPeriod: Optional[Period]
    duration: Optional[Duration]
    quantity: Optional[Quantity]
    method: Optional[CodeableConcept]
    bodySite: Optional[CodeableConcept]
    fastingStatusCodeableConcept: Optional[CodeableConcept]
    fastingStatusDuration: Optional[Duration]


class SpecimenProcessing(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'additive'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'procedure': 'CodeableConcept', 'additive': 'Reference', 'timePeriod': 'Period'}
    _choice_fields = {'time': ['timeDateTime', 'timePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    description: Optional[String] = None
    procedure: Optional[CodeableConcept]
    additive: Reference | FHIRList[Reference]
    timeDateTime: Optional[DateTime] = None
    timePeriod: Optional[Period]


class SpecimenContainer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'identifier'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'capacity': 'Quantity', 'specimenQuantity': 'Quantity', 'additiveCodeableConcept': 'CodeableConcept', 'additiveReference': 'Reference'}
    _choice_fields = {'additive': ['additiveCodeableConcept', 'additiveReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    description: Optional[String] = None
    type_: Optional[CodeableConcept]
    capacity: Optional[Quantity]
    specimenQuantity: Optional[Quantity]
    additiveCodeableConcept: Optional[CodeableConcept]
    additiveReference: Optional[Reference]


class Specimen(FHIRResource):
    _resource_type = "Specimen"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'parent', 'request', 'processing', 'container', 'condition', 'note'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'accessionIdentifier': 'Identifier', 'type_': 'CodeableConcept', 'subject': 'Reference', 'parent': 'Reference', 'request': 'Reference', 'collection': 'SpecimenCollection', 'processing': 'SpecimenProcessing', 'container': 'SpecimenContainer', 'condition': 'CodeableConcept', 'note': 'Annotation'}

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
    type_: Optional[CodeableConcept]
    subject: Optional[Reference]
    receivedTime: Optional[DateTime] = None
    parent: Reference | FHIRList[Reference]
    request: Reference | FHIRList[Reference]
    collection: Optional[SpecimenCollection]
    processing: SpecimenProcessing | FHIRList[SpecimenProcessing]
    container: SpecimenContainer | FHIRList[SpecimenContainer]
    condition: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]


class SpecimenDefinitionTypeTested(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'rejectionCriterion', 'handling'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'container': 'SpecimenDefinitionTypeTestedContainer', 'retentionTime': 'Duration', 'rejectionCriterion': 'CodeableConcept', 'handling': 'SpecimenDefinitionTypeTestedHandling'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    isDerived: Optional[Boolean] = None
    type_: Optional[CodeableConcept]
    preference: Optional[Code] = None
    container: Optional[SpecimenDefinitionTypeTestedContainer]
    requirement: Optional[String] = None
    retentionTime: Optional[Duration]
    rejectionCriterion: CodeableConcept | FHIRList[CodeableConcept]
    handling: SpecimenDefinitionTypeTestedHandling | FHIRList[SpecimenDefinitionTypeTestedHandling]


class SpecimenDefinitionTypeTestedContainer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'additive'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'material': 'CodeableConcept', 'type_': 'CodeableConcept', 'cap': 'CodeableConcept', 'capacity': 'Quantity', 'minimumVolumeQuantity': 'Quantity', 'additive': 'SpecimenDefinitionTypeTestedContainerAdditive'}
    _choice_fields = {'minimumVolume': ['minimumVolumeQuantity', 'minimumVolumeString']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    material: Optional[CodeableConcept]
    type_: Optional[CodeableConcept]
    cap: Optional[CodeableConcept]
    description: Optional[String] = None
    capacity: Optional[Quantity]
    minimumVolumeQuantity: Optional[Quantity]
    minimumVolumeString: Optional[String] = None
    additive: SpecimenDefinitionTypeTestedContainerAdditive | FHIRList[SpecimenDefinitionTypeTestedContainerAdditive]
    preparation: Optional[String] = None


class SpecimenDefinitionTypeTestedContainerAdditive(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'additiveCodeableConcept': 'CodeableConcept', 'additiveReference': 'Reference'}
    _choice_fields = {'additive': ['additiveCodeableConcept', 'additiveReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    additiveCodeableConcept: Optional[CodeableConcept]
    additiveReference: Optional[Reference]


class SpecimenDefinitionTypeTestedHandling(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'temperatureQualifier': 'CodeableConcept', 'temperatureRange': 'Range', 'maxDuration': 'Duration'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    temperatureQualifier: Optional[CodeableConcept]
    temperatureRange: Optional[Range]
    maxDuration: Optional[Duration]
    instruction: Optional[String] = None


class SpecimenDefinition(FHIRResource):
    _resource_type = "SpecimenDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'patientPreparation', 'collection', 'typeTested'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'typeCollected': 'CodeableConcept', 'patientPreparation': 'CodeableConcept', 'collection': 'CodeableConcept', 'typeTested': 'SpecimenDefinitionTypeTested'}

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
    typeTested: SpecimenDefinitionTypeTested | FHIRList[SpecimenDefinitionTypeTested]


class StructureDefinitionMapping(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identity: Optional[Id] = None
    uri: Optional[Uri] = None
    name: Optional[String] = None
    comment: Optional[String] = None


class StructureDefinitionContext(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    expression: Optional[String] = None


class StructureDefinitionSnapshot(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'element'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'element': 'ElementDefinition'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    element: ElementDefinition | FHIRList[ElementDefinition]


class StructureDefinitionDifferential(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'element'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'element': 'ElementDefinition'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    element: ElementDefinition | FHIRList[ElementDefinition]


class StructureDefinition(FHIRResource):
    _resource_type = "StructureDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'keyword', 'mapping', 'context', 'contextInvariant'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'keyword': 'Coding', 'mapping': 'StructureDefinitionMapping', 'context': 'StructureDefinitionContext', 'snapshot': 'StructureDefinitionSnapshot', 'differential': 'StructureDefinitionDifferential'}

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
    mapping: StructureDefinitionMapping | FHIRList[StructureDefinitionMapping]
    kind: Optional[Code] = None
    abstract: Optional[Boolean] = None
    context: StructureDefinitionContext | FHIRList[StructureDefinitionContext]
    contextInvariant: String | FHIRList[String] = None
    type_: Optional[Uri] = None
    baseDefinition: Optional[Canonical] = None
    derivation: Optional[Code] = None
    snapshot: Optional[StructureDefinitionSnapshot]
    differential: Optional[StructureDefinitionDifferential]


class StructureMapStructure(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Canonical] = None
    mode: Optional[Code] = None
    alias: Optional[String] = None
    documentation: Optional[String] = None


class StructureMapGroup(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'input', 'rule'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'input': 'StructureMapGroupInput', 'rule': 'StructureMapGroupRule'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[Id] = None
    extends: Optional[Id] = None
    typeMode: Optional[Code] = None
    documentation: Optional[String] = None
    input: StructureMapGroupInput | FHIRList[StructureMapGroupInput]
    rule: StructureMapGroupRule | FHIRList[StructureMapGroupRule]


class StructureMapGroupInput(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[Id] = None
    type_: Optional[String] = None
    mode: Optional[Code] = None
    documentation: Optional[String] = None


class StructureMapGroupRule(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'source', 'target', 'rule', 'dependent'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'source': 'StructureMapGroupRuleSource', 'target': 'StructureMapGroupRuleTarget', 'dependent': 'StructureMapGroupRuleDependent'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[Id] = None
    source: StructureMapGroupRuleSource | FHIRList[StructureMapGroupRuleSource]
    target: StructureMapGroupRuleTarget | FHIRList[StructureMapGroupRuleTarget]
    rule: Any = None
    dependent: StructureMapGroupRuleDependent | FHIRList[StructureMapGroupRuleDependent]
    documentation: Optional[String] = None


class StructureMapGroupRuleSource(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'defaultValueAddress': 'Address', 'defaultValueAge': 'Age', 'defaultValueAnnotation': 'Annotation', 'defaultValueAttachment': 'Attachment', 'defaultValueCodeableConcept': 'CodeableConcept', 'defaultValueCoding': 'Coding', 'defaultValueContactPoint': 'ContactPoint', 'defaultValueCount': 'Count', 'defaultValueDistance': 'Distance', 'defaultValueDuration': 'Duration', 'defaultValueHumanName': 'HumanName', 'defaultValueIdentifier': 'Identifier', 'defaultValueMoney': 'Money', 'defaultValuePeriod': 'Period', 'defaultValueQuantity': 'Quantity', 'defaultValueRange': 'Range', 'defaultValueRatio': 'Ratio', 'defaultValueReference': 'Reference', 'defaultValueSampledData': 'SampledData', 'defaultValueSignature': 'Signature', 'defaultValueTiming': 'Timing', 'defaultValueContactDetail': 'ContactDetail', 'defaultValueContributor': 'Contributor', 'defaultValueDataRequirement': 'DataRequirement', 'defaultValueExpression': 'Expression', 'defaultValueParameterDefinition': 'ParameterDefinition', 'defaultValueRelatedArtifact': 'RelatedArtifact', 'defaultValueTriggerDefinition': 'TriggerDefinition', 'defaultValueUsageContext': 'UsageContext', 'defaultValueDosage': 'Dosage', 'defaultValueMeta': 'Meta'}
    _choice_fields = {'defaultValue': ['defaultValueBase64Binary', 'defaultValueBoolean', 'defaultValueCanonical', 'defaultValueCode', 'defaultValueDate', 'defaultValueDateTime', 'defaultValueDecimal', 'defaultValueId', 'defaultValueInstant', 'defaultValueInteger', 'defaultValueMarkdown', 'defaultValueOid', 'defaultValuePositiveInt', 'defaultValueString', 'defaultValueTime', 'defaultValueUnsignedInt', 'defaultValueUri', 'defaultValueUrl', 'defaultValueUuid', 'defaultValueAddress', 'defaultValueAge', 'defaultValueAnnotation', 'defaultValueAttachment', 'defaultValueCodeableConcept', 'defaultValueCoding', 'defaultValueContactPoint', 'defaultValueCount', 'defaultValueDistance', 'defaultValueDuration', 'defaultValueHumanName', 'defaultValueIdentifier', 'defaultValueMoney', 'defaultValuePeriod', 'defaultValueQuantity', 'defaultValueRange', 'defaultValueRatio', 'defaultValueReference', 'defaultValueSampledData', 'defaultValueSignature', 'defaultValueTiming', 'defaultValueContactDetail', 'defaultValueContributor', 'defaultValueDataRequirement', 'defaultValueExpression', 'defaultValueParameterDefinition', 'defaultValueRelatedArtifact', 'defaultValueTriggerDefinition', 'defaultValueUsageContext', 'defaultValueDosage', 'defaultValueMeta']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    context: Optional[Id] = None
    min: Optional[Integer] = None
    max: Optional[String] = None
    type_: Optional[String] = None
    defaultValueBase64Binary: Optional[Base64Binary] = None
    defaultValueBoolean: Optional[Boolean] = None
    defaultValueCanonical: Optional[Canonical] = None
    defaultValueCode: Optional[Code] = None
    defaultValueDate: Optional[Date] = None
    defaultValueDateTime: Optional[DateTime] = None
    defaultValueDecimal: Optional[Decimal] = None
    defaultValueId: Optional[Id] = None
    defaultValueInstant: Optional[Instant] = None
    defaultValueInteger: Optional[Integer] = None
    defaultValueMarkdown: Optional[Markdown] = None
    defaultValueOid: Optional[Oid] = None
    defaultValuePositiveInt: Optional[PositiveInt] = None
    defaultValueString: Optional[String] = None
    defaultValueTime: Optional[Time] = None
    defaultValueUnsignedInt: Optional[UnsignedInt] = None
    defaultValueUri: Optional[Uri] = None
    defaultValueUrl: Optional[Url] = None
    defaultValueUuid: Optional[Uuid] = None
    defaultValueAddress: Optional[Address]
    defaultValueAge: Optional[Age]
    defaultValueAnnotation: Optional[Annotation]
    defaultValueAttachment: Optional[Attachment]
    defaultValueCodeableConcept: Optional[CodeableConcept]
    defaultValueCoding: Optional[Coding]
    defaultValueContactPoint: Optional[ContactPoint]
    defaultValueCount: Optional[Count]
    defaultValueDistance: Optional[Distance]
    defaultValueDuration: Optional[Duration]
    defaultValueHumanName: Optional[HumanName]
    defaultValueIdentifier: Optional[Identifier]
    defaultValueMoney: Optional[Money]
    defaultValuePeriod: Optional[Period]
    defaultValueQuantity: Optional[Quantity]
    defaultValueRange: Optional[Range]
    defaultValueRatio: Optional[Ratio]
    defaultValueReference: Optional[Reference]
    defaultValueSampledData: Optional[SampledData]
    defaultValueSignature: Optional[Signature]
    defaultValueTiming: Optional[Timing]
    defaultValueContactDetail: Optional[ContactDetail]
    defaultValueContributor: Optional[Contributor]
    defaultValueDataRequirement: Optional[DataRequirement]
    defaultValueExpression: Optional[Expression]
    defaultValueParameterDefinition: Optional[ParameterDefinition]
    defaultValueRelatedArtifact: Optional[RelatedArtifact]
    defaultValueTriggerDefinition: Optional[TriggerDefinition]
    defaultValueUsageContext: Optional[UsageContext]
    defaultValueDosage: Optional[Dosage]
    defaultValueMeta: Optional[Meta]
    element: Optional[String] = None
    listMode: Optional[Code] = None
    variable: Optional[Id] = None
    condition: Optional[String] = None
    check: Optional[String] = None
    logMessage: Optional[String] = None


class StructureMapGroupRuleTarget(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'listMode', 'parameter'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'parameter': 'StructureMapGroupRuleTargetParameter'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    context: Optional[Id] = None
    contextType: Optional[Code] = None
    element: Optional[String] = None
    variable: Optional[Id] = None
    listMode: Code | FHIRList[Code] = None
    listRuleId: Optional[Id] = None
    transform: Optional[Code] = None
    parameter: StructureMapGroupRuleTargetParameter | FHIRList[StructureMapGroupRuleTargetParameter]


class StructureMapGroupRuleTargetParameter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}
    _choice_fields = {'value': ['valueId', 'valueString', 'valueBoolean', 'valueInteger', 'valueDecimal']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    valueId: Optional[Id] = None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueDecimal: Optional[Decimal] = None


class StructureMapGroupRuleDependent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'variable'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[Id] = None
    variable: String | FHIRList[String] = None


class StructureMap(FHIRResource):
    _resource_type = "StructureMap"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'structure', 'import_', 'group'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'structure': 'StructureMapStructure', 'group': 'StructureMapGroup'}

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
    structure: StructureMapStructure | FHIRList[StructureMapStructure]
    import_: Canonical | FHIRList[Canonical] = None
    group: StructureMapGroup | FHIRList[StructureMapGroup]


class SubscriptionChannel(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'header'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    endpoint: Optional[Url] = None
    payload: Optional[Code] = None
    header: String | FHIRList[String] = None


class Subscription(FHIRResource):
    _resource_type = "Subscription"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'contact': 'ContactPoint', 'channel': 'SubscriptionChannel'}

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
    channel: Optional[SubscriptionChannel]


class SubstanceInstance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'quantity': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Identifier]
    expiry: Optional[DateTime] = None
    quantity: Optional[Quantity]


class SubstanceIngredient(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'quantity': 'Ratio', 'substanceCodeableConcept': 'CodeableConcept', 'substanceReference': 'Reference'}
    _choice_fields = {'substance': ['substanceCodeableConcept', 'substanceReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    quantity: Optional[Ratio]
    substanceCodeableConcept: Optional[CodeableConcept]
    substanceReference: Optional[Reference]


class Substance(FHIRResource):
    _resource_type = "Substance"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'instance', 'ingredient'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'instance': 'SubstanceInstance', 'ingredient': 'SubstanceIngredient'}

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
    instance: SubstanceInstance | FHIRList[SubstanceInstance]
    ingredient: SubstanceIngredient | FHIRList[SubstanceIngredient]


class SubstanceNucleicAcidSubunit(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'linkage', 'sugar'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'sequenceAttachment': 'Attachment', 'fivePrime': 'CodeableConcept', 'threePrime': 'CodeableConcept', 'linkage': 'SubstanceNucleicAcidSubunitLinkage', 'sugar': 'SubstanceNucleicAcidSubunitSugar'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    subunit: Optional[Integer] = None
    sequence: Optional[String] = None
    length: Optional[Integer] = None
    sequenceAttachment: Optional[Attachment]
    fivePrime: Optional[CodeableConcept]
    threePrime: Optional[CodeableConcept]
    linkage: SubstanceNucleicAcidSubunitLinkage | FHIRList[SubstanceNucleicAcidSubunitLinkage]
    sugar: SubstanceNucleicAcidSubunitSugar | FHIRList[SubstanceNucleicAcidSubunitSugar]


class SubstanceNucleicAcidSubunitLinkage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    connectivity: Optional[String] = None
    identifier: Optional[Identifier]
    name: Optional[String] = None
    residueSite: Optional[String] = None


class SubstanceNucleicAcidSubunitSugar(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Identifier]
    name: Optional[String] = None
    residueSite: Optional[String] = None


class SubstanceNucleicAcid(FHIRResource):
    _resource_type = "SubstanceNucleicAcid"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'subunit'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'sequenceType': 'CodeableConcept', 'oligoNucleotideType': 'CodeableConcept', 'subunit': 'SubstanceNucleicAcidSubunit'}

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
    subunit: SubstanceNucleicAcidSubunit | FHIRList[SubstanceNucleicAcidSubunit]


class SubstancePolymerMonomerSet(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'startingMaterial'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'ratioType': 'CodeableConcept', 'startingMaterial': 'SubstancePolymerMonomerSetStartingMaterial'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    ratioType: Optional[CodeableConcept]
    startingMaterial: SubstancePolymerMonomerSetStartingMaterial | FHIRList[SubstancePolymerMonomerSetStartingMaterial]


class SubstancePolymerMonomerSetStartingMaterial(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'material': 'CodeableConcept', 'type_': 'CodeableConcept', 'amount': 'SubstanceAmount'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    material: Optional[CodeableConcept]
    type_: Optional[CodeableConcept]
    isDefining: Optional[Boolean] = None
    amount: Optional[SubstanceAmount]


class SubstancePolymerRepeat(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'repeatUnit'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'repeatUnitAmountType': 'CodeableConcept', 'repeatUnit': 'SubstancePolymerRepeatRepeatUnit'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    numberOfUnits: Optional[Integer] = None
    averageMolecularFormula: Optional[String] = None
    repeatUnitAmountType: Optional[CodeableConcept]
    repeatUnit: SubstancePolymerRepeatRepeatUnit | FHIRList[SubstancePolymerRepeatRepeatUnit]


class SubstancePolymerRepeatRepeatUnit(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'degreeOfPolymerisation', 'structuralRepresentation'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'orientationOfPolymerisation': 'CodeableConcept', 'amount': 'SubstanceAmount', 'degreeOfPolymerisation': 'SubstancePolymerRepeatRepeatUnitDegreeOfPolymerisation', 'structuralRepresentation': 'SubstancePolymerRepeatRepeatUnitStructuralRepresentation'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    orientationOfPolymerisation: Optional[CodeableConcept]
    repeatUnit: Optional[String] = None
    amount: Optional[SubstanceAmount]
    degreeOfPolymerisation: SubstancePolymerRepeatRepeatUnitDegreeOfPolymerisation | FHIRList[SubstancePolymerRepeatRepeatUnitDegreeOfPolymerisation]
    structuralRepresentation: SubstancePolymerRepeatRepeatUnitStructuralRepresentation | FHIRList[SubstancePolymerRepeatRepeatUnitStructuralRepresentation]


class SubstancePolymerRepeatRepeatUnitDegreeOfPolymerisation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'degree': 'CodeableConcept', 'amount': 'SubstanceAmount'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    degree: Optional[CodeableConcept]
    amount: Optional[SubstanceAmount]


class SubstancePolymerRepeatRepeatUnitStructuralRepresentation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'attachment': 'Attachment'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    representation: Optional[String] = None
    attachment: Optional[Attachment]


class SubstancePolymer(FHIRResource):
    _resource_type = "SubstancePolymer"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'copolymerConnectivity', 'modification', 'monomerSet', 'repeat'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'class_': 'CodeableConcept', 'geometry': 'CodeableConcept', 'copolymerConnectivity': 'CodeableConcept', 'monomerSet': 'SubstancePolymerMonomerSet', 'repeat': 'SubstancePolymerRepeat'}

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
    monomerSet: SubstancePolymerMonomerSet | FHIRList[SubstancePolymerMonomerSet]
    repeat: SubstancePolymerRepeat | FHIRList[SubstancePolymerRepeat]


class SubstanceProteinSubunit(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'sequenceAttachment': 'Attachment', 'nTerminalModificationId': 'Identifier', 'cTerminalModificationId': 'Identifier'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    subunit: Optional[Integer] = None
    sequence: Optional[String] = None
    length: Optional[Integer] = None
    sequenceAttachment: Optional[Attachment]
    nTerminalModificationId: Optional[Identifier]
    nTerminalModification: Optional[String] = None
    cTerminalModificationId: Optional[Identifier]
    cTerminalModification: Optional[String] = None


class SubstanceProtein(FHIRResource):
    _resource_type = "SubstanceProtein"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'disulfideLinkage', 'subunit'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'sequenceType': 'CodeableConcept', 'subunit': 'SubstanceProteinSubunit'}

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
    subunit: SubstanceProteinSubunit | FHIRList[SubstanceProteinSubunit]


class SubstanceReferenceInformationGene(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'source'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'geneSequenceOrigin': 'CodeableConcept', 'gene': 'CodeableConcept', 'source': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    geneSequenceOrigin: Optional[CodeableConcept]
    gene: Optional[CodeableConcept]
    source: Reference | FHIRList[Reference]


class SubstanceReferenceInformationGeneElement(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'source'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'element': 'Identifier', 'source': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    element: Optional[Identifier]
    source: Reference | FHIRList[Reference]


class SubstanceReferenceInformationClassification(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'subtype', 'source'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'domain': 'CodeableConcept', 'classification': 'CodeableConcept', 'subtype': 'CodeableConcept', 'source': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    domain: Optional[CodeableConcept]
    classification: Optional[CodeableConcept]
    subtype: CodeableConcept | FHIRList[CodeableConcept]
    source: Reference | FHIRList[Reference]


class SubstanceReferenceInformationTarget(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'source'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'target': 'Identifier', 'type_': 'CodeableConcept', 'interaction': 'CodeableConcept', 'organism': 'CodeableConcept', 'organismType': 'CodeableConcept', 'amountQuantity': 'Quantity', 'amountRange': 'Range', 'amountType': 'CodeableConcept', 'source': 'Reference'}
    _choice_fields = {'amount': ['amountQuantity', 'amountRange', 'amountString']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    target: Optional[Identifier]
    type_: Optional[CodeableConcept]
    interaction: Optional[CodeableConcept]
    organism: Optional[CodeableConcept]
    organismType: Optional[CodeableConcept]
    amountQuantity: Optional[Quantity]
    amountRange: Optional[Range]
    amountString: Optional[String] = None
    amountType: Optional[CodeableConcept]
    source: Reference | FHIRList[Reference]


class SubstanceReferenceInformation(FHIRResource):
    _resource_type = "SubstanceReferenceInformation"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'gene', 'geneElement', 'classification', 'target'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'gene': 'SubstanceReferenceInformationGene', 'geneElement': 'SubstanceReferenceInformationGeneElement', 'classification': 'SubstanceReferenceInformationClassification', 'target': 'SubstanceReferenceInformationTarget'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    comment: Optional[String] = None
    gene: SubstanceReferenceInformationGene | FHIRList[SubstanceReferenceInformationGene]
    geneElement: SubstanceReferenceInformationGeneElement | FHIRList[SubstanceReferenceInformationGeneElement]
    classification: SubstanceReferenceInformationClassification | FHIRList[SubstanceReferenceInformationClassification]
    target: SubstanceReferenceInformationTarget | FHIRList[SubstanceReferenceInformationTarget]


class SubstanceSourceMaterialFractionDescription(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'materialType': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    fraction: Optional[String] = None
    materialType: Optional[CodeableConcept]


class SubstanceSourceMaterialOrganism(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'author'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'family': 'CodeableConcept', 'genus': 'CodeableConcept', 'species': 'CodeableConcept', 'intraspecificType': 'CodeableConcept', 'author': 'SubstanceSourceMaterialOrganismAuthor', 'hybrid': 'SubstanceSourceMaterialOrganismHybrid', 'organismGeneral': 'SubstanceSourceMaterialOrganismOrganismGeneral'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    family: Optional[CodeableConcept]
    genus: Optional[CodeableConcept]
    species: Optional[CodeableConcept]
    intraspecificType: Optional[CodeableConcept]
    intraspecificDescription: Optional[String] = None
    author: SubstanceSourceMaterialOrganismAuthor | FHIRList[SubstanceSourceMaterialOrganismAuthor]
    hybrid: Optional[SubstanceSourceMaterialOrganismHybrid]
    organismGeneral: Optional[SubstanceSourceMaterialOrganismOrganismGeneral]


class SubstanceSourceMaterialOrganismAuthor(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'authorType': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    authorType: Optional[CodeableConcept]
    authorDescription: Optional[String] = None


class SubstanceSourceMaterialOrganismHybrid(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'hybridType': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    maternalOrganismId: Optional[String] = None
    maternalOrganismName: Optional[String] = None
    paternalOrganismId: Optional[String] = None
    paternalOrganismName: Optional[String] = None
    hybridType: Optional[CodeableConcept]


class SubstanceSourceMaterialOrganismOrganismGeneral(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'kingdom': 'CodeableConcept', 'phylum': 'CodeableConcept', 'class_': 'CodeableConcept', 'order': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    kingdom: Optional[CodeableConcept]
    phylum: Optional[CodeableConcept]
    class_: Optional[CodeableConcept]
    order: Optional[CodeableConcept]


class SubstanceSourceMaterialPartDescription(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'part': 'CodeableConcept', 'partLocation': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    part: Optional[CodeableConcept]
    partLocation: Optional[CodeableConcept]


class SubstanceSourceMaterial(FHIRResource):
    _resource_type = "SubstanceSourceMaterial"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'parentSubstanceId', 'parentSubstanceName', 'countryOfOrigin', 'geographicalLocation', 'fractionDescription', 'partDescription'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'sourceMaterialClass': 'CodeableConcept', 'sourceMaterialType': 'CodeableConcept', 'sourceMaterialState': 'CodeableConcept', 'organismId': 'Identifier', 'parentSubstanceId': 'Identifier', 'countryOfOrigin': 'CodeableConcept', 'developmentStage': 'CodeableConcept', 'fractionDescription': 'SubstanceSourceMaterialFractionDescription', 'organism': 'SubstanceSourceMaterialOrganism', 'partDescription': 'SubstanceSourceMaterialPartDescription'}

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
    fractionDescription: SubstanceSourceMaterialFractionDescription | FHIRList[SubstanceSourceMaterialFractionDescription]
    organism: Optional[SubstanceSourceMaterialOrganism]
    partDescription: SubstanceSourceMaterialPartDescription | FHIRList[SubstanceSourceMaterialPartDescription]


class SubstanceSpecificationMoiety(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'role': 'CodeableConcept', 'identifier': 'Identifier', 'stereochemistry': 'CodeableConcept', 'opticalActivity': 'CodeableConcept', 'amountQuantity': 'Quantity'}
    _choice_fields = {'amount': ['amountQuantity', 'amountString']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    role: Optional[CodeableConcept]
    identifier: Optional[Identifier]
    name: Optional[String] = None
    stereochemistry: Optional[CodeableConcept]
    opticalActivity: Optional[CodeableConcept]
    molecularFormula: Optional[String] = None
    amountQuantity: Optional[Quantity]
    amountString: Optional[String] = None


class SubstanceSpecificationProperty(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'definingSubstanceReference': 'Reference', 'definingSubstanceCodeableConcept': 'CodeableConcept', 'amountQuantity': 'Quantity'}
    _choice_fields = {'amount': ['amountQuantity', 'amountString'], 'definingSubstance': ['definingSubstanceReference', 'definingSubstanceCodeableConcept']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    parameters: Optional[String] = None
    definingSubstanceReference: Optional[Reference]
    definingSubstanceCodeableConcept: Optional[CodeableConcept]
    amountQuantity: Optional[Quantity]
    amountString: Optional[String] = None


class SubstanceSpecificationStructure(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'isotope', 'source', 'representation'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'stereochemistry': 'CodeableConcept', 'opticalActivity': 'CodeableConcept', 'isotope': 'SubstanceSpecificationStructureIsotope', 'source': 'Reference', 'representation': 'SubstanceSpecificationStructureRepresentation'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    stereochemistry: Optional[CodeableConcept]
    opticalActivity: Optional[CodeableConcept]
    molecularFormula: Optional[String] = None
    molecularFormulaByMoiety: Optional[String] = None
    isotope: SubstanceSpecificationStructureIsotope | FHIRList[SubstanceSpecificationStructureIsotope]
    molecularWeight: Any = None
    source: Reference | FHIRList[Reference]
    representation: SubstanceSpecificationStructureRepresentation | FHIRList[SubstanceSpecificationStructureRepresentation]


class SubstanceSpecificationStructureIsotope(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'name': 'CodeableConcept', 'substitution': 'CodeableConcept', 'halfLife': 'Quantity', 'molecularWeight': 'SubstanceSpecificationStructureIsotopeMolecularWeight'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Identifier]
    name: Optional[CodeableConcept]
    substitution: Optional[CodeableConcept]
    halfLife: Optional[Quantity]
    molecularWeight: Optional[SubstanceSpecificationStructureIsotopeMolecularWeight]


class SubstanceSpecificationStructureIsotopeMolecularWeight(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'method': 'CodeableConcept', 'type_': 'CodeableConcept', 'amount': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    method: Optional[CodeableConcept]
    type_: Optional[CodeableConcept]
    amount: Optional[Quantity]


class SubstanceSpecificationStructureRepresentation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'attachment': 'Attachment'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    representation: Optional[String] = None
    attachment: Optional[Attachment]


class SubstanceSpecificationCode(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'source'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'status': 'CodeableConcept', 'source': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    status: Optional[CodeableConcept]
    statusDate: Optional[DateTime] = None
    comment: Optional[String] = None
    source: Reference | FHIRList[Reference]


class SubstanceSpecificationName(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'language', 'domain', 'jurisdiction', 'synonym', 'translation', 'official', 'source'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'status': 'CodeableConcept', 'language': 'CodeableConcept', 'domain': 'CodeableConcept', 'jurisdiction': 'CodeableConcept', 'official': 'SubstanceSpecificationNameOfficial', 'source': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[String] = None
    type_: Optional[CodeableConcept]
    status: Optional[CodeableConcept]
    preferred: Optional[Boolean] = None
    language: CodeableConcept | FHIRList[CodeableConcept]
    domain: CodeableConcept | FHIRList[CodeableConcept]
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept]
    synonym: Any = None
    translation: Any = None
    official: SubstanceSpecificationNameOfficial | FHIRList[SubstanceSpecificationNameOfficial]
    source: Reference | FHIRList[Reference]


class SubstanceSpecificationNameOfficial(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'authority': 'CodeableConcept', 'status': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    authority: Optional[CodeableConcept]
    status: Optional[CodeableConcept]
    date: Optional[DateTime] = None


class SubstanceSpecificationRelationship(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'source'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'substanceReference': 'Reference', 'substanceCodeableConcept': 'CodeableConcept', 'relationship': 'CodeableConcept', 'amountQuantity': 'Quantity', 'amountRange': 'Range', 'amountRatio': 'Ratio', 'amountRatioLowLimit': 'Ratio', 'amountType': 'CodeableConcept', 'source': 'Reference'}
    _choice_fields = {'amount': ['amountQuantity', 'amountRange', 'amountRatio', 'amountString'], 'substance': ['substanceReference', 'substanceCodeableConcept']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    substanceReference: Optional[Reference]
    substanceCodeableConcept: Optional[CodeableConcept]
    relationship: Optional[CodeableConcept]
    isDefining: Optional[Boolean] = None
    amountQuantity: Optional[Quantity]
    amountRange: Optional[Range]
    amountRatio: Optional[Ratio]
    amountString: Optional[String] = None
    amountRatioLowLimit: Optional[Ratio]
    amountType: Optional[CodeableConcept]
    source: Reference | FHIRList[Reference]


class SubstanceSpecification(FHIRResource):
    _resource_type = "SubstanceSpecification"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'source', 'moiety', 'property', 'code', 'name', 'molecularWeight', 'relationship'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'status': 'CodeableConcept', 'domain': 'CodeableConcept', 'source': 'Reference', 'moiety': 'SubstanceSpecificationMoiety', 'property': 'SubstanceSpecificationProperty', 'referenceInformation': 'Reference', 'structure': 'SubstanceSpecificationStructure', 'code': 'SubstanceSpecificationCode', 'name': 'SubstanceSpecificationName', 'relationship': 'SubstanceSpecificationRelationship', 'nucleicAcid': 'Reference', 'polymer': 'Reference', 'protein': 'Reference', 'sourceMaterial': 'Reference'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Identifier]
    type_: Optional[CodeableConcept]
    status: Optional[CodeableConcept]
    domain: Optional[CodeableConcept]
    description: Optional[String] = None
    source: Reference | FHIRList[Reference]
    comment: Optional[String] = None
    moiety: SubstanceSpecificationMoiety | FHIRList[SubstanceSpecificationMoiety]
    property: SubstanceSpecificationProperty | FHIRList[SubstanceSpecificationProperty]
    referenceInformation: Optional[Reference]
    structure: Optional[SubstanceSpecificationStructure]
    code: SubstanceSpecificationCode | FHIRList[SubstanceSpecificationCode]
    name: SubstanceSpecificationName | FHIRList[SubstanceSpecificationName]
    molecularWeight: Any = None
    relationship: SubstanceSpecificationRelationship | FHIRList[SubstanceSpecificationRelationship]
    nucleicAcid: Optional[Reference]
    polymer: Optional[Reference]
    protein: Optional[Reference]
    sourceMaterial: Optional[Reference]


class SupplyDeliverySuppliedItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'quantity': 'Quantity', 'itemCodeableConcept': 'CodeableConcept', 'itemReference': 'Reference'}
    _choice_fields = {'item': ['itemCodeableConcept', 'itemReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    quantity: Optional[Quantity]
    itemCodeableConcept: Optional[CodeableConcept]
    itemReference: Optional[Reference]


class SupplyDelivery(FHIRResource):
    _resource_type = "SupplyDelivery"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'receiver'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'patient': 'Reference', 'type_': 'CodeableConcept', 'suppliedItem': 'SupplyDeliverySuppliedItem', 'occurrencePeriod': 'Period', 'occurrenceTiming': 'Timing', 'supplier': 'Reference', 'destination': 'Reference', 'receiver': 'Reference'}
    _choice_fields = {'occurrence': ['occurrenceDateTime', 'occurrencePeriod', 'occurrenceTiming']}

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
    type_: Optional[CodeableConcept]
    suppliedItem: Optional[SupplyDeliverySuppliedItem]
    occurrenceDateTime: Optional[DateTime] = None
    occurrencePeriod: Optional[Period]
    occurrenceTiming: Optional[Timing]
    supplier: Optional[Reference]
    destination: Optional[Reference]
    receiver: Reference | FHIRList[Reference]


class SupplyRequestParameter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueCodeableConcept': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueRange': 'Range'}
    _choice_fields = {'value': ['valueCodeableConcept', 'valueQuantity', 'valueRange', 'valueBoolean']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueCodeableConcept: Optional[CodeableConcept]
    valueQuantity: Optional[Quantity]
    valueRange: Optional[Range]
    valueBoolean: Optional[Boolean] = None


class SupplyRequest(FHIRResource):
    _resource_type = "SupplyRequest"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'parameter', 'supplier', 'reasonCode', 'reasonReference'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'category': 'CodeableConcept', 'itemCodeableConcept': 'CodeableConcept', 'itemReference': 'Reference', 'quantity': 'Quantity', 'parameter': 'SupplyRequestParameter', 'occurrencePeriod': 'Period', 'occurrenceTiming': 'Timing', 'requester': 'Reference', 'supplier': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'deliverFrom': 'Reference', 'deliverTo': 'Reference'}
    _choice_fields = {'item': ['itemCodeableConcept', 'itemReference'], 'occurrence': ['occurrenceDateTime', 'occurrencePeriod', 'occurrenceTiming']}

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
    itemCodeableConcept: Optional[CodeableConcept]
    itemReference: Optional[Reference]
    quantity: Optional[Quantity]
    parameter: SupplyRequestParameter | FHIRList[SupplyRequestParameter]
    occurrenceDateTime: Optional[DateTime] = None
    occurrencePeriod: Optional[Period]
    occurrenceTiming: Optional[Timing]
    authoredOn: Optional[DateTime] = None
    requester: Optional[Reference]
    supplier: Reference | FHIRList[Reference]
    reasonCode: CodeableConcept | FHIRList[CodeableConcept]
    reasonReference: Reference | FHIRList[Reference]
    deliverFrom: Optional[Reference]
    deliverTo: Optional[Reference]


class TaskRestriction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'recipient'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'period': 'Period', 'recipient': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    repetitions: Optional[PositiveInt] = None
    period: Optional[Period]
    recipient: Reference | FHIRList[Reference]


class TaskInput(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'valueAddress': 'Address', 'valueAge': 'Age', 'valueAnnotation': 'Annotation', 'valueAttachment': 'Attachment', 'valueCodeableConcept': 'CodeableConcept', 'valueCoding': 'Coding', 'valueContactPoint': 'ContactPoint', 'valueCount': 'Count', 'valueDistance': 'Distance', 'valueDuration': 'Duration', 'valueHumanName': 'HumanName', 'valueIdentifier': 'Identifier', 'valueMoney': 'Money', 'valuePeriod': 'Period', 'valueQuantity': 'Quantity', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueReference': 'Reference', 'valueSampledData': 'SampledData', 'valueSignature': 'Signature', 'valueTiming': 'Timing', 'valueContactDetail': 'ContactDetail', 'valueContributor': 'Contributor', 'valueDataRequirement': 'DataRequirement', 'valueExpression': 'Expression', 'valueParameterDefinition': 'ParameterDefinition', 'valueRelatedArtifact': 'RelatedArtifact', 'valueTriggerDefinition': 'TriggerDefinition', 'valueUsageContext': 'UsageContext', 'valueDosage': 'Dosage', 'valueMeta': 'Meta'}
    _choice_fields = {'value': ['valueBase64Binary', 'valueBoolean', 'valueCanonical', 'valueCode', 'valueDate', 'valueDateTime', 'valueDecimal', 'valueId', 'valueInstant', 'valueInteger', 'valueMarkdown', 'valueOid', 'valuePositiveInt', 'valueString', 'valueTime', 'valueUnsignedInt', 'valueUri', 'valueUrl', 'valueUuid', 'valueAddress', 'valueAge', 'valueAnnotation', 'valueAttachment', 'valueCodeableConcept', 'valueCoding', 'valueContactPoint', 'valueCount', 'valueDistance', 'valueDuration', 'valueHumanName', 'valueIdentifier', 'valueMoney', 'valuePeriod', 'valueQuantity', 'valueRange', 'valueRatio', 'valueReference', 'valueSampledData', 'valueSignature', 'valueTiming', 'valueContactDetail', 'valueContributor', 'valueDataRequirement', 'valueExpression', 'valueParameterDefinition', 'valueRelatedArtifact', 'valueTriggerDefinition', 'valueUsageContext', 'valueDosage', 'valueMeta']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    valueBase64Binary: Optional[Base64Binary] = None
    valueBoolean: Optional[Boolean] = None
    valueCanonical: Optional[Canonical] = None
    valueCode: Optional[Code] = None
    valueDate: Optional[Date] = None
    valueDateTime: Optional[DateTime] = None
    valueDecimal: Optional[Decimal] = None
    valueId: Optional[Id] = None
    valueInstant: Optional[Instant] = None
    valueInteger: Optional[Integer] = None
    valueMarkdown: Optional[Markdown] = None
    valueOid: Optional[Oid] = None
    valuePositiveInt: Optional[PositiveInt] = None
    valueString: Optional[String] = None
    valueTime: Optional[Time] = None
    valueUnsignedInt: Optional[UnsignedInt] = None
    valueUri: Optional[Uri] = None
    valueUrl: Optional[Url] = None
    valueUuid: Optional[Uuid] = None
    valueAddress: Optional[Address]
    valueAge: Optional[Age]
    valueAnnotation: Optional[Annotation]
    valueAttachment: Optional[Attachment]
    valueCodeableConcept: Optional[CodeableConcept]
    valueCoding: Optional[Coding]
    valueContactPoint: Optional[ContactPoint]
    valueCount: Optional[Count]
    valueDistance: Optional[Distance]
    valueDuration: Optional[Duration]
    valueHumanName: Optional[HumanName]
    valueIdentifier: Optional[Identifier]
    valueMoney: Optional[Money]
    valuePeriod: Optional[Period]
    valueQuantity: Optional[Quantity]
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueReference: Optional[Reference]
    valueSampledData: Optional[SampledData]
    valueSignature: Optional[Signature]
    valueTiming: Optional[Timing]
    valueContactDetail: Optional[ContactDetail]
    valueContributor: Optional[Contributor]
    valueDataRequirement: Optional[DataRequirement]
    valueExpression: Optional[Expression]
    valueParameterDefinition: Optional[ParameterDefinition]
    valueRelatedArtifact: Optional[RelatedArtifact]
    valueTriggerDefinition: Optional[TriggerDefinition]
    valueUsageContext: Optional[UsageContext]
    valueDosage: Optional[Dosage]
    valueMeta: Optional[Meta]


class TaskOutput(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'valueAddress': 'Address', 'valueAge': 'Age', 'valueAnnotation': 'Annotation', 'valueAttachment': 'Attachment', 'valueCodeableConcept': 'CodeableConcept', 'valueCoding': 'Coding', 'valueContactPoint': 'ContactPoint', 'valueCount': 'Count', 'valueDistance': 'Distance', 'valueDuration': 'Duration', 'valueHumanName': 'HumanName', 'valueIdentifier': 'Identifier', 'valueMoney': 'Money', 'valuePeriod': 'Period', 'valueQuantity': 'Quantity', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueReference': 'Reference', 'valueSampledData': 'SampledData', 'valueSignature': 'Signature', 'valueTiming': 'Timing', 'valueContactDetail': 'ContactDetail', 'valueContributor': 'Contributor', 'valueDataRequirement': 'DataRequirement', 'valueExpression': 'Expression', 'valueParameterDefinition': 'ParameterDefinition', 'valueRelatedArtifact': 'RelatedArtifact', 'valueTriggerDefinition': 'TriggerDefinition', 'valueUsageContext': 'UsageContext', 'valueDosage': 'Dosage', 'valueMeta': 'Meta'}
    _choice_fields = {'value': ['valueBase64Binary', 'valueBoolean', 'valueCanonical', 'valueCode', 'valueDate', 'valueDateTime', 'valueDecimal', 'valueId', 'valueInstant', 'valueInteger', 'valueMarkdown', 'valueOid', 'valuePositiveInt', 'valueString', 'valueTime', 'valueUnsignedInt', 'valueUri', 'valueUrl', 'valueUuid', 'valueAddress', 'valueAge', 'valueAnnotation', 'valueAttachment', 'valueCodeableConcept', 'valueCoding', 'valueContactPoint', 'valueCount', 'valueDistance', 'valueDuration', 'valueHumanName', 'valueIdentifier', 'valueMoney', 'valuePeriod', 'valueQuantity', 'valueRange', 'valueRatio', 'valueReference', 'valueSampledData', 'valueSignature', 'valueTiming', 'valueContactDetail', 'valueContributor', 'valueDataRequirement', 'valueExpression', 'valueParameterDefinition', 'valueRelatedArtifact', 'valueTriggerDefinition', 'valueUsageContext', 'valueDosage', 'valueMeta']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[CodeableConcept]
    valueBase64Binary: Optional[Base64Binary] = None
    valueBoolean: Optional[Boolean] = None
    valueCanonical: Optional[Canonical] = None
    valueCode: Optional[Code] = None
    valueDate: Optional[Date] = None
    valueDateTime: Optional[DateTime] = None
    valueDecimal: Optional[Decimal] = None
    valueId: Optional[Id] = None
    valueInstant: Optional[Instant] = None
    valueInteger: Optional[Integer] = None
    valueMarkdown: Optional[Markdown] = None
    valueOid: Optional[Oid] = None
    valuePositiveInt: Optional[PositiveInt] = None
    valueString: Optional[String] = None
    valueTime: Optional[Time] = None
    valueUnsignedInt: Optional[UnsignedInt] = None
    valueUri: Optional[Uri] = None
    valueUrl: Optional[Url] = None
    valueUuid: Optional[Uuid] = None
    valueAddress: Optional[Address]
    valueAge: Optional[Age]
    valueAnnotation: Optional[Annotation]
    valueAttachment: Optional[Attachment]
    valueCodeableConcept: Optional[CodeableConcept]
    valueCoding: Optional[Coding]
    valueContactPoint: Optional[ContactPoint]
    valueCount: Optional[Count]
    valueDistance: Optional[Distance]
    valueDuration: Optional[Duration]
    valueHumanName: Optional[HumanName]
    valueIdentifier: Optional[Identifier]
    valueMoney: Optional[Money]
    valuePeriod: Optional[Period]
    valueQuantity: Optional[Quantity]
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueReference: Optional[Reference]
    valueSampledData: Optional[SampledData]
    valueSignature: Optional[Signature]
    valueTiming: Optional[Timing]
    valueContactDetail: Optional[ContactDetail]
    valueContributor: Optional[Contributor]
    valueDataRequirement: Optional[DataRequirement]
    valueExpression: Optional[Expression]
    valueParameterDefinition: Optional[ParameterDefinition]
    valueRelatedArtifact: Optional[RelatedArtifact]
    valueTriggerDefinition: Optional[TriggerDefinition]
    valueUsageContext: Optional[UsageContext]
    valueDosage: Optional[Dosage]
    valueMeta: Optional[Meta]


class Task(FHIRResource):
    _resource_type = "Task"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'performerType', 'insurance', 'note', 'relevantHistory', 'input', 'output'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'groupIdentifier': 'Identifier', 'partOf': 'Reference', 'statusReason': 'CodeableConcept', 'businessStatus': 'CodeableConcept', 'code': 'CodeableConcept', 'focus': 'Reference', 'for_': 'Reference', 'encounter': 'Reference', 'executionPeriod': 'Period', 'requester': 'Reference', 'performerType': 'CodeableConcept', 'owner': 'Reference', 'location': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'insurance': 'Reference', 'note': 'Annotation', 'relevantHistory': 'Reference', 'restriction': 'TaskRestriction', 'input': 'TaskInput', 'output': 'TaskOutput'}

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
    restriction: Optional[TaskRestriction]
    input: TaskInput | FHIRList[TaskInput]
    output: TaskOutput | FHIRList[TaskOutput]


class TerminologyCapabilitiesSoftware(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[String] = None
    version: Optional[String] = None


class TerminologyCapabilitiesImplementation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    description: Optional[String] = None
    url: Optional[Url] = None


class TerminologyCapabilitiesCodeSystem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'version'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'version': 'TerminologyCapabilitiesCodeSystemVersion'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    uri: Optional[Canonical] = None
    version: TerminologyCapabilitiesCodeSystemVersion | FHIRList[TerminologyCapabilitiesCodeSystemVersion]
    subsumption: Optional[Boolean] = None


class TerminologyCapabilitiesCodeSystemVersion(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'language', 'filter', 'property'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'filter': 'TerminologyCapabilitiesCodeSystemVersionFilter'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[String] = None
    isDefault: Optional[Boolean] = None
    compositional: Optional[Boolean] = None
    language: Code | FHIRList[Code] = None
    filter: TerminologyCapabilitiesCodeSystemVersionFilter | FHIRList[TerminologyCapabilitiesCodeSystemVersionFilter]
    property: Code | FHIRList[Code] = None


class TerminologyCapabilitiesCodeSystemVersionFilter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'op'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    op: Code | FHIRList[Code] = None


class TerminologyCapabilitiesExpansion(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'parameter'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'parameter': 'TerminologyCapabilitiesExpansionParameter'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    hierarchical: Optional[Boolean] = None
    paging: Optional[Boolean] = None
    incomplete: Optional[Boolean] = None
    parameter: TerminologyCapabilitiesExpansionParameter | FHIRList[TerminologyCapabilitiesExpansionParameter]
    textFilter: Optional[Markdown] = None


class TerminologyCapabilitiesExpansionParameter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[Code] = None
    documentation: Optional[String] = None


class TerminologyCapabilitiesValidateCode(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    translations: Optional[Boolean] = None


class TerminologyCapabilitiesTranslation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    needsMap: Optional[Boolean] = None


class TerminologyCapabilitiesClosure(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    translation: Optional[Boolean] = None


class TerminologyCapabilities(FHIRResource):
    _resource_type = "TerminologyCapabilities"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'codeSystem'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'software': 'TerminologyCapabilitiesSoftware', 'implementation': 'TerminologyCapabilitiesImplementation', 'codeSystem': 'TerminologyCapabilitiesCodeSystem', 'expansion': 'TerminologyCapabilitiesExpansion', 'validateCode': 'TerminologyCapabilitiesValidateCode', 'translation': 'TerminologyCapabilitiesTranslation', 'closure': 'TerminologyCapabilitiesClosure'}

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
    software: Optional[TerminologyCapabilitiesSoftware]
    implementation: Optional[TerminologyCapabilitiesImplementation]
    lockedDate: Optional[Boolean] = None
    codeSystem: TerminologyCapabilitiesCodeSystem | FHIRList[TerminologyCapabilitiesCodeSystem]
    expansion: Optional[TerminologyCapabilitiesExpansion]
    codeSearch: Optional[Code] = None
    validateCode: Optional[TerminologyCapabilitiesValidateCode]
    translation: Optional[TerminologyCapabilitiesTranslation]
    closure: Optional[TerminologyCapabilitiesClosure]


class TestReportParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    uri: Optional[Uri] = None
    display: Optional[String] = None


class TestReportSetup(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'action'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'action': 'TestReportSetupAction'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    action: TestReportSetupAction | FHIRList[TestReportSetupAction]


class TestReportSetupAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'operation': 'TestReportSetupActionOperation', 'assert_': 'TestReportSetupActionAssert'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    operation: Optional[TestReportSetupActionOperation]
    assert_: Optional[TestReportSetupActionAssert]


class TestReportSetupActionOperation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    result: Optional[Code] = None
    message: Optional[Markdown] = None
    detail: Optional[Uri] = None


class TestReportSetupActionAssert(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    result: Optional[Code] = None
    message: Optional[Markdown] = None
    detail: Optional[String] = None


class TestReportTest(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'action'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'action': 'TestReportTestAction'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[String] = None
    description: Optional[String] = None
    action: TestReportTestAction | FHIRList[TestReportTestAction]


class TestReportTestAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    operation: Any = None
    assert_: Any = None


class TestReportTeardown(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'action'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'action': 'TestReportTeardownAction'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    action: TestReportTeardownAction | FHIRList[TestReportTeardownAction]


class TestReportTeardownAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    operation: Any = None


class TestReport(FHIRResource):
    _resource_type = "TestReport"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'participant', 'test'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'testScript': 'Reference', 'participant': 'TestReportParticipant', 'setup': 'TestReportSetup', 'test': 'TestReportTest', 'teardown': 'TestReportTeardown'}

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
    participant: TestReportParticipant | FHIRList[TestReportParticipant]
    setup: Optional[TestReportSetup]
    test: TestReportTest | FHIRList[TestReportTest]
    teardown: Optional[TestReportTeardown]


class TestScriptOrigin(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'profile': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    index: Optional[Integer] = None
    profile: Optional[Coding]


class TestScriptDestination(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'profile': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    index: Optional[Integer] = None
    profile: Optional[Coding]


class TestScriptMetadata(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'link', 'capability'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'link': 'TestScriptMetadataLink', 'capability': 'TestScriptMetadataCapability'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    link: TestScriptMetadataLink | FHIRList[TestScriptMetadataLink]
    capability: TestScriptMetadataCapability | FHIRList[TestScriptMetadataCapability]


class TestScriptMetadataLink(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    description: Optional[String] = None


class TestScriptMetadataCapability(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'origin', 'link'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    required: Optional[Boolean] = None
    validated: Optional[Boolean] = None
    description: Optional[String] = None
    origin: Integer | FHIRList[Integer] = None
    destination: Optional[Integer] = None
    link: Uri | FHIRList[Uri] = None
    capabilities: Optional[Canonical] = None


class TestScriptFixture(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'resource': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    autocreate: Optional[Boolean] = None
    autodelete: Optional[Boolean] = None
    resource: Optional[Reference]


class TestScriptVariable(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[String] = None
    defaultValue: Optional[String] = None
    description: Optional[String] = None
    expression: Optional[String] = None
    headerField: Optional[String] = None
    hint: Optional[String] = None
    path: Optional[String] = None
    sourceId: Optional[Id] = None


class TestScriptSetup(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'action'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'action': 'TestScriptSetupAction'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    action: TestScriptSetupAction | FHIRList[TestScriptSetupAction]


class TestScriptSetupAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'operation': 'TestScriptSetupActionOperation', 'assert_': 'TestScriptSetupActionAssert'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    operation: Optional[TestScriptSetupActionOperation]
    assert_: Optional[TestScriptSetupActionAssert]


class TestScriptSetupActionOperation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'requestHeader'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'Coding', 'requestHeader': 'TestScriptSetupActionOperationRequestHeader'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Coding]
    resource: Optional[Code] = None
    label: Optional[String] = None
    description: Optional[String] = None
    accept: Optional[Code] = None
    contentType: Optional[Code] = None
    destination: Optional[Integer] = None
    encodeRequestUrl: Optional[Boolean] = None
    method: Optional[Code] = None
    origin: Optional[Integer] = None
    params: Optional[String] = None
    requestHeader: TestScriptSetupActionOperationRequestHeader | FHIRList[TestScriptSetupActionOperationRequestHeader]
    requestId: Optional[Id] = None
    responseId: Optional[Id] = None
    sourceId: Optional[Id] = None
    targetId: Optional[Id] = None
    url: Optional[String] = None


class TestScriptSetupActionOperationRequestHeader(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    field: Optional[String] = None
    value: Optional[String] = None


class TestScriptSetupActionAssert(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    label: Optional[String] = None
    description: Optional[String] = None
    direction: Optional[Code] = None
    compareToSourceId: Optional[String] = None
    compareToSourceExpression: Optional[String] = None
    compareToSourcePath: Optional[String] = None
    contentType: Optional[Code] = None
    expression: Optional[String] = None
    headerField: Optional[String] = None
    minimumId: Optional[String] = None
    navigationLinks: Optional[Boolean] = None
    operator: Optional[Code] = None
    path: Optional[String] = None
    requestMethod: Optional[Code] = None
    requestURL: Optional[String] = None
    resource: Optional[Code] = None
    response: Optional[Code] = None
    responseCode: Optional[String] = None
    sourceId: Optional[Id] = None
    validateProfileId: Optional[Id] = None
    value: Optional[String] = None
    warningOnly: Optional[Boolean] = None


class TestScriptTest(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'action'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'action': 'TestScriptTestAction'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[String] = None
    description: Optional[String] = None
    action: TestScriptTestAction | FHIRList[TestScriptTestAction]


class TestScriptTestAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    operation: Any = None
    assert_: Any = None


class TestScriptTeardown(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'action'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'action': 'TestScriptTeardownAction'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    action: TestScriptTeardownAction | FHIRList[TestScriptTeardownAction]


class TestScriptTeardownAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    operation: Any = None


class TestScript(FHIRResource):
    _resource_type = "TestScript"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'origin', 'destination', 'fixture', 'profile', 'variable', 'test'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'origin': 'TestScriptOrigin', 'destination': 'TestScriptDestination', 'metadata': 'TestScriptMetadata', 'fixture': 'TestScriptFixture', 'profile': 'Reference', 'variable': 'TestScriptVariable', 'setup': 'TestScriptSetup', 'test': 'TestScriptTest', 'teardown': 'TestScriptTeardown'}

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
    origin: TestScriptOrigin | FHIRList[TestScriptOrigin]
    destination: TestScriptDestination | FHIRList[TestScriptDestination]
    metadata: Optional[TestScriptMetadata]
    fixture: TestScriptFixture | FHIRList[TestScriptFixture]
    profile: Reference | FHIRList[Reference]
    variable: TestScriptVariable | FHIRList[TestScriptVariable]
    setup: Optional[TestScriptSetup]
    test: TestScriptTest | FHIRList[TestScriptTest]
    teardown: Optional[TestScriptTeardown]


class ValueSetCompose(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'include', 'exclude'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'include': 'ValueSetComposeInclude'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    lockedDate: Optional[Date] = None
    inactive: Optional[Boolean] = None
    include: ValueSetComposeInclude | FHIRList[ValueSetComposeInclude]
    exclude: Any = None


class ValueSetComposeInclude(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'concept', 'filter', 'valueSet'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'concept': 'ValueSetComposeIncludeConcept', 'filter': 'ValueSetComposeIncludeFilter'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    concept: ValueSetComposeIncludeConcept | FHIRList[ValueSetComposeIncludeConcept]
    filter: ValueSetComposeIncludeFilter | FHIRList[ValueSetComposeIncludeFilter]
    valueSet: Canonical | FHIRList[Canonical] = None


class ValueSetComposeIncludeConcept(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'designation'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'designation': 'ValueSetComposeIncludeConceptDesignation'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    display: Optional[String] = None
    designation: ValueSetComposeIncludeConceptDesignation | FHIRList[ValueSetComposeIncludeConceptDesignation]


class ValueSetComposeIncludeConceptDesignation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'use': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    language: Optional[Code] = None
    use: Optional[Coding]
    value: Optional[String] = None


class ValueSetComposeIncludeFilter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    property: Optional[Code] = None
    op: Optional[Code] = None
    value: Optional[String] = None


class ValueSetExpansion(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'parameter', 'contains'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'parameter': 'ValueSetExpansionParameter', 'contains': 'ValueSetExpansionContains'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Uri] = None
    timestamp: Optional[DateTime] = None
    total: Optional[Integer] = None
    offset: Optional[Integer] = None
    parameter: ValueSetExpansionParameter | FHIRList[ValueSetExpansionParameter]
    contains: ValueSetExpansionContains | FHIRList[ValueSetExpansionContains]


class ValueSetExpansionParameter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}
    _choice_fields = {'value': ['valueString', 'valueBoolean', 'valueInteger', 'valueDecimal', 'valueUri', 'valueCode', 'valueDateTime']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[String] = None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueDecimal: Optional[Decimal] = None
    valueUri: Optional[Uri] = None
    valueCode: Optional[Code] = None
    valueDateTime: Optional[DateTime] = None


class ValueSetExpansionContains(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'designation', 'contains'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    abstract: Optional[Boolean] = None
    inactive: Optional[Boolean] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    designation: Any = None
    contains: Any = None


class ValueSet(FHIRResource):
    _resource_type = "ValueSet"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'compose': 'ValueSetCompose', 'expansion': 'ValueSetExpansion'}

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
    compose: Optional[ValueSetCompose]
    expansion: Optional[ValueSetExpansion]


class VerificationResultPrimarySource(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'type_', 'communicationMethod', 'pushTypeAvailable'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'who': 'Reference', 'type_': 'CodeableConcept', 'communicationMethod': 'CodeableConcept', 'validationStatus': 'CodeableConcept', 'canPushUpdates': 'CodeableConcept', 'pushTypeAvailable': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    who: Optional[Reference]
    type_: CodeableConcept | FHIRList[CodeableConcept]
    communicationMethod: CodeableConcept | FHIRList[CodeableConcept]
    validationStatus: Optional[CodeableConcept]
    validationDate: Optional[DateTime] = None
    canPushUpdates: Optional[CodeableConcept]
    pushTypeAvailable: CodeableConcept | FHIRList[CodeableConcept]


class VerificationResultAttestation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'who': 'Reference', 'onBehalfOf': 'Reference', 'communicationMethod': 'CodeableConcept', 'proxySignature': 'Signature', 'sourceSignature': 'Signature'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    who: Optional[Reference]
    onBehalfOf: Optional[Reference]
    communicationMethod: Optional[CodeableConcept]
    date: Optional[Date] = None
    sourceIdentityCertificate: Optional[String] = None
    proxyIdentityCertificate: Optional[String] = None
    proxySignature: Optional[Signature]
    sourceSignature: Optional[Signature]


class VerificationResultValidator(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'organization': 'Reference', 'attestationSignature': 'Signature'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    organization: Optional[Reference]
    identityCertificate: Optional[String] = None
    attestationSignature: Optional[Signature]


class VerificationResult(FHIRResource):
    _resource_type = "VerificationResult"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'target', 'targetLocation', 'validationProcess', 'primarySource', 'validator'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'target': 'Reference', 'need': 'CodeableConcept', 'validationType': 'CodeableConcept', 'validationProcess': 'CodeableConcept', 'frequency': 'Timing', 'failureAction': 'CodeableConcept', 'primarySource': 'VerificationResultPrimarySource', 'attestation': 'VerificationResultAttestation', 'validator': 'VerificationResultValidator'}

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
    primarySource: VerificationResultPrimarySource | FHIRList[VerificationResultPrimarySource]
    attestation: Optional[VerificationResultAttestation]
    validator: VerificationResultValidator | FHIRList[VerificationResultValidator]


class VisionPrescriptionLensSpecification(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'prism', 'note'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'product': 'CodeableConcept', 'prism': 'VisionPrescriptionLensSpecificationPrism', 'duration': 'Quantity', 'note': 'Annotation'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    product: Optional[CodeableConcept]
    eye: Optional[Code] = None
    sphere: Optional[Decimal] = None
    cylinder: Optional[Decimal] = None
    axis: Optional[Integer] = None
    prism: VisionPrescriptionLensSpecificationPrism | FHIRList[VisionPrescriptionLensSpecificationPrism]
    add: Optional[Decimal] = None
    power: Optional[Decimal] = None
    backCurve: Optional[Decimal] = None
    diameter: Optional[Decimal] = None
    duration: Optional[Quantity]
    color: Optional[String] = None
    brand: Optional[String] = None
    note: Annotation | FHIRList[Annotation]


class VisionPrescriptionLensSpecificationPrism(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    amount: Optional[Decimal] = None
    base: Optional[Code] = None


class VisionPrescription(FHIRResource):
    _resource_type = "VisionPrescription"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'lensSpecification'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'patient': 'Reference', 'encounter': 'Reference', 'prescriber': 'Reference', 'lensSpecification': 'VisionPrescriptionLensSpecification'}

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
    lensSpecification: VisionPrescriptionLensSpecification | FHIRList[VisionPrescriptionLensSpecification]


class actualgroupCharacteristic(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueCodeableConcept': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueRange': 'Range', 'valueReference': 'Reference', 'period': 'Period'}
    _choice_fields = {'value': ['valueCodeableConcept', 'valueBoolean', 'valueQuantity', 'valueRange', 'valueReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueCodeableConcept: Optional[CodeableConcept]
    valueBoolean: Optional[Boolean] = None
    valueQuantity: Optional[Quantity]
    valueRange: Optional[Range]
    valueReference: Optional[Reference]
    exclude: Optional[Boolean] = None
    period: Optional[Period]


class actualgroupMember(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'entity': 'Reference', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    entity: Optional[Reference]
    period: Optional[Period]
    inactive: Optional[Boolean] = None


class actualgroup(FHIRResource):
    _resource_type = "actualgroup"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'member'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'code': 'CodeableConcept', 'managingEntity': 'Reference', 'characteristic': 'actualgroupCharacteristic', 'member': 'actualgroupMember'}

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
    type_: Optional[Code] = None
    actual: Optional[Boolean] = None
    code: Optional[CodeableConcept]
    name: Optional[String] = None
    quantity: Optional[UnsignedInt] = None
    managingEntity: Optional[Reference]
    characteristic: Optional[actualgroupCharacteristic]
    member: actualgroupMember | FHIRList[actualgroupMember]


class bmiCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Coding | FHIRList[Coding]
    text: Optional[String] = None


class bmiCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bmiCode(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Optional[Coding]
    text: Optional[String] = None


class bmiCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bmiValue[x](FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class bmiReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'low': 'Quantity', 'high': 'Quantity', 'type_': 'CodeableConcept', 'appliesTo': 'CodeableConcept', 'age': 'Range'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    low: Optional[Quantity]
    high: Optional[Quantity]
    type_: Optional[CodeableConcept]
    appliesTo: CodeableConcept | FHIRList[CodeableConcept]
    age: Optional[Range]
    text: Optional[String] = None


class bmiComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueCodeableConcept': 'CodeableConcept', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueSampledData': 'SampledData', 'valuePeriod': 'Period', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept'}
    _choice_fields = {'value': ['valueQuantity', 'valueCodeableConcept', 'valueString', 'valueBoolean', 'valueInteger', 'valueRange', 'valueRatio', 'valueSampledData', 'valueTime', 'valueDateTime', 'valuePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueQuantity: Optional[Quantity]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueSampledData: Optional[SampledData]
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Optional[Period]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    referenceRange: Any = None


class bmi(FHIRResource):
    _resource_type = "bmi"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'effectivePeriod': 'Period', 'performer': 'Reference', 'valueQuantity': 'Quantity', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'bmiReferenceRange', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'bmiComponent'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'value': ['valueQuantity']}

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
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    valueQuantity: Optional[Quantity]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: bmiReferenceRange | FHIRList[bmiReferenceRange]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: bmiComponent | FHIRList[bmiComponent]


class bodyheightCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Coding | FHIRList[Coding]
    text: Optional[String] = None


class bodyheightCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bodyheightCode(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Optional[Coding]
    text: Optional[String] = None


class bodyheightCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bodyheightValue[x](FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class bodyheightReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'low': 'Quantity', 'high': 'Quantity', 'type_': 'CodeableConcept', 'appliesTo': 'CodeableConcept', 'age': 'Range'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    low: Optional[Quantity]
    high: Optional[Quantity]
    type_: Optional[CodeableConcept]
    appliesTo: CodeableConcept | FHIRList[CodeableConcept]
    age: Optional[Range]
    text: Optional[String] = None


class bodyheightComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueCodeableConcept': 'CodeableConcept', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueSampledData': 'SampledData', 'valuePeriod': 'Period', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept'}
    _choice_fields = {'value': ['valueQuantity', 'valueCodeableConcept', 'valueString', 'valueBoolean', 'valueInteger', 'valueRange', 'valueRatio', 'valueSampledData', 'valueTime', 'valueDateTime', 'valuePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueQuantity: Optional[Quantity]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueSampledData: Optional[SampledData]
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Optional[Period]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    referenceRange: Any = None


class bodyheight(FHIRResource):
    _resource_type = "bodyheight"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'effectivePeriod': 'Period', 'performer': 'Reference', 'valueQuantity': 'Quantity', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'bodyheightReferenceRange', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'bodyheightComponent'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'value': ['valueQuantity']}

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
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    valueQuantity: Optional[Quantity]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: bodyheightReferenceRange | FHIRList[bodyheightReferenceRange]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: bodyheightComponent | FHIRList[bodyheightComponent]


class bodytempCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Coding | FHIRList[Coding]
    text: Optional[String] = None


class bodytempCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bodytempCode(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Optional[Coding]
    text: Optional[String] = None


class bodytempCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bodytempValue[x](FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class bodytempReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'low': 'Quantity', 'high': 'Quantity', 'type_': 'CodeableConcept', 'appliesTo': 'CodeableConcept', 'age': 'Range'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    low: Optional[Quantity]
    high: Optional[Quantity]
    type_: Optional[CodeableConcept]
    appliesTo: CodeableConcept | FHIRList[CodeableConcept]
    age: Optional[Range]
    text: Optional[String] = None


class bodytempComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueCodeableConcept': 'CodeableConcept', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueSampledData': 'SampledData', 'valuePeriod': 'Period', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept'}
    _choice_fields = {'value': ['valueQuantity', 'valueCodeableConcept', 'valueString', 'valueBoolean', 'valueInteger', 'valueRange', 'valueRatio', 'valueSampledData', 'valueTime', 'valueDateTime', 'valuePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueQuantity: Optional[Quantity]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueSampledData: Optional[SampledData]
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Optional[Period]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    referenceRange: Any = None


class bodytemp(FHIRResource):
    _resource_type = "bodytemp"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'effectivePeriod': 'Period', 'performer': 'Reference', 'valueQuantity': 'Quantity', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'bodytempReferenceRange', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'bodytempComponent'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'value': ['valueQuantity']}

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
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    valueQuantity: Optional[Quantity]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: bodytempReferenceRange | FHIRList[bodytempReferenceRange]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: bodytempComponent | FHIRList[bodytempComponent]


class bodyweightCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Coding | FHIRList[Coding]
    text: Optional[String] = None


class bodyweightCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bodyweightCode(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Optional[Coding]
    text: Optional[String] = None


class bodyweightCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bodyweightValue[x](FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class bodyweightReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'low': 'Quantity', 'high': 'Quantity', 'type_': 'CodeableConcept', 'appliesTo': 'CodeableConcept', 'age': 'Range'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    low: Optional[Quantity]
    high: Optional[Quantity]
    type_: Optional[CodeableConcept]
    appliesTo: CodeableConcept | FHIRList[CodeableConcept]
    age: Optional[Range]
    text: Optional[String] = None


class bodyweightComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueCodeableConcept': 'CodeableConcept', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueSampledData': 'SampledData', 'valuePeriod': 'Period', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept'}
    _choice_fields = {'value': ['valueQuantity', 'valueCodeableConcept', 'valueString', 'valueBoolean', 'valueInteger', 'valueRange', 'valueRatio', 'valueSampledData', 'valueTime', 'valueDateTime', 'valuePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueQuantity: Optional[Quantity]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueSampledData: Optional[SampledData]
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Optional[Period]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    referenceRange: Any = None


class bodyweight(FHIRResource):
    _resource_type = "bodyweight"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'effectivePeriod': 'Period', 'performer': 'Reference', 'valueQuantity': 'Quantity', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'bodyweightReferenceRange', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'bodyweightComponent'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'value': ['valueQuantity']}

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
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    valueQuantity: Optional[Quantity]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: bodyweightReferenceRange | FHIRList[bodyweightReferenceRange]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: bodyweightComponent | FHIRList[bodyweightComponent]


class bpCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Coding | FHIRList[Coding]
    text: Optional[String] = None


class bpCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bpCode(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Optional[Coding]
    text: Optional[String] = None


class bpCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bpReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'low': 'Quantity', 'high': 'Quantity', 'type_': 'CodeableConcept', 'appliesTo': 'CodeableConcept', 'age': 'Range'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    low: Optional[Quantity]
    high: Optional[Quantity]
    type_: Optional[CodeableConcept]
    appliesTo: CodeableConcept | FHIRList[CodeableConcept]
    age: Optional[Range]
    text: Optional[String] = None


class bpComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueCodeableConcept': 'CodeableConcept', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueSampledData': 'SampledData', 'valuePeriod': 'Period', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept'}
    _choice_fields = {'value': ['valueQuantity']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueQuantity: Optional[Quantity]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueSampledData: Optional[SampledData]
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Optional[Period]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    referenceRange: Any = None


class bpComponentCode(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Optional[Coding]
    text: Optional[String] = None


class bpComponentCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bpComponentValue[x](FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class bp(FHIRResource):
    _resource_type = "bp"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'effectivePeriod': 'Period', 'performer': 'Reference', 'valueQuantity': 'Quantity', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'bpReferenceRange', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'bpComponent'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'value': ['valueQuantity']}

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
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    valueQuantity: Optional[Quantity]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: bpReferenceRange | FHIRList[bpReferenceRange]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: Optional[bpComponent]


class catalogAttester(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'party': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    mode: Optional[Code] = None
    time: Optional[DateTime] = None
    party: Optional[Reference]


class catalogRelatesTo(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'targetIdentifier': 'Identifier', 'targetReference': 'Reference'}
    _choice_fields = {'target': ['targetIdentifier', 'targetReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    targetIdentifier: Optional[Identifier]
    targetReference: Optional[Reference]


class catalogEvent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'detail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'period': 'Period', 'detail': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: CodeableConcept | FHIRList[CodeableConcept]
    period: Optional[Period]
    detail: Reference | FHIRList[Reference]


class catalogSection(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'author', 'entry', 'section'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'author': 'Reference', 'focus': 'Reference', 'text': 'Narrative', 'orderedBy': 'CodeableConcept', 'entry': 'Reference', 'emptyReason': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    title: Optional[String] = None
    code: Optional[CodeableConcept]
    author: Reference | FHIRList[Reference]
    focus: Optional[Reference]
    text: Optional[Narrative]
    mode: Optional[Code] = None
    orderedBy: Optional[CodeableConcept]
    entry: Reference | FHIRList[Reference]
    emptyReason: Optional[CodeableConcept]
    section: Any = None


class catalog(FHIRResource):
    _resource_type = "catalog"
    _list_fields = {'contained', 'modifierExtension', 'author', 'attester', 'relatesTo', 'event', 'section'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'category': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'author': 'Reference', 'attester': 'catalogAttester', 'custodian': 'Reference', 'relatesTo': 'catalogRelatesTo', 'event': 'catalogEvent', 'section': 'catalogSection'}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Optional[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Identifier]
    status: Optional[Code] = None
    type_: Optional[CodeableConcept]
    category: Optional[CodeableConcept]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    date: Optional[DateTime] = None
    author: Reference | FHIRList[Reference]
    title: Optional[String] = None
    confidentiality: Optional[Code] = None
    attester: catalogAttester | FHIRList[catalogAttester]
    custodian: Optional[Reference]
    relatesTo: catalogRelatesTo | FHIRList[catalogRelatesTo]
    event: catalogEvent | FHIRList[catalogEvent]
    section: catalogSection | FHIRList[catalogSection]


class cdshooksguidanceresponse(FHIRResource):
    _resource_type = "cdshooksguidanceresponse"
    _list_fields = {'contained', 'modifierExtension', 'reasonCode', 'reasonReference', 'note', 'evaluationMessage', 'dataRequirement'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'requestIdentifier': 'Identifier', 'identifier': 'Identifier', 'subject': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'note': 'Annotation', 'evaluationMessage': 'Reference', 'outputParameters': 'Reference', 'result': 'Reference', 'dataRequirement': 'DataRequirement'}
    _choice_fields = {'module': ['moduleUri']}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Optional[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    requestIdentifier: Optional[Identifier]
    identifier: Optional[Identifier]
    moduleUri: Optional[Uri] = None
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


class cdshooksrequestgroupAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'documentation', 'condition', 'relatedAction', 'participant', 'action'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'documentation': 'RelatedArtifact', 'condition': 'cdshooksrequestgroupActionCondition', 'relatedAction': 'cdshooksrequestgroupActionRelatedAction', 'timingAge': 'Age', 'timingPeriod': 'Period', 'timingDuration': 'Duration', 'timingRange': 'Range', 'timingTiming': 'Timing', 'participant': 'Reference', 'type_': 'CodeableConcept', 'resource': 'Reference'}
    _choice_fields = {'timing': ['timingDateTime', 'timingAge', 'timingPeriod', 'timingDuration', 'timingRange', 'timingTiming']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    prefix: Optional[String] = None
    title: Optional[String] = None
    description: Optional[String] = None
    textEquivalent: Optional[String] = None
    priority: Optional[Code] = None
    code: CodeableConcept | FHIRList[CodeableConcept]
    documentation: RelatedArtifact | FHIRList[RelatedArtifact]
    condition: cdshooksrequestgroupActionCondition | FHIRList[cdshooksrequestgroupActionCondition]
    relatedAction: cdshooksrequestgroupActionRelatedAction | FHIRList[cdshooksrequestgroupActionRelatedAction]
    timingDateTime: Optional[DateTime] = None
    timingAge: Optional[Age]
    timingPeriod: Optional[Period]
    timingDuration: Optional[Duration]
    timingRange: Optional[Range]
    timingTiming: Optional[Timing]
    participant: Reference | FHIRList[Reference]
    type_: Optional[CodeableConcept]
    groupingBehavior: Optional[Code] = None
    selectionBehavior: Optional[Code] = None
    requiredBehavior: Optional[Code] = None
    precheckBehavior: Optional[Code] = None
    cardinalityBehavior: Optional[Code] = None
    resource: Optional[Reference]
    action: Any = None


class cdshooksrequestgroupActionCondition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    kind: Optional[Code] = None
    expression: Optional[Expression]


class cdshooksrequestgroupActionRelatedAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'offsetDuration': 'Duration', 'offsetRange': 'Range'}
    _choice_fields = {'offset': ['offsetDuration', 'offsetRange']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    actionId: Optional[Id] = None
    relationship: Optional[Code] = None
    offsetDuration: Optional[Duration]
    offsetRange: Optional[Range]


class cdshooksrequestgroup(FHIRResource):
    _resource_type = "cdshooksrequestgroup"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'instantiatesCanonical', 'basedOn', 'replaces', 'reasonCode', 'reasonReference', 'note', 'action'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'replaces': 'Reference', 'groupIdentifier': 'Identifier', 'code': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'author': 'Reference', 'reasonCode': 'CodeableConcept', 'reasonReference': 'Reference', 'note': 'Annotation', 'action': 'cdshooksrequestgroupAction'}

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
    action: cdshooksrequestgroupAction | FHIRList[cdshooksrequestgroupAction]


class cdshooksserviceplandefinitionGoal(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'addresses', 'documentation', 'target'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'category': 'CodeableConcept', 'description': 'CodeableConcept', 'priority': 'CodeableConcept', 'start': 'CodeableConcept', 'addresses': 'CodeableConcept', 'documentation': 'RelatedArtifact', 'target': 'cdshooksserviceplandefinitionGoalTarget'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    category: Optional[CodeableConcept]
    description: Optional[CodeableConcept]
    priority: Optional[CodeableConcept]
    start: Optional[CodeableConcept]
    addresses: CodeableConcept | FHIRList[CodeableConcept]
    documentation: RelatedArtifact | FHIRList[RelatedArtifact]
    target: cdshooksserviceplandefinitionGoalTarget | FHIRList[cdshooksserviceplandefinitionGoalTarget]


class cdshooksserviceplandefinitionGoalTarget(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'measure': 'CodeableConcept', 'detailQuantity': 'Quantity', 'detailRange': 'Range', 'detailCodeableConcept': 'CodeableConcept', 'due': 'Duration'}
    _choice_fields = {'detail': ['detailQuantity', 'detailRange', 'detailCodeableConcept']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    measure: Optional[CodeableConcept]
    detailQuantity: Optional[Quantity]
    detailRange: Optional[Range]
    detailCodeableConcept: Optional[CodeableConcept]
    due: Optional[Duration]


class cdshooksserviceplandefinitionAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'reason', 'documentation', 'goalId', 'trigger', 'condition', 'input', 'output', 'relatedAction', 'participant', 'dynamicValue', 'action'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'reason': 'CodeableConcept', 'documentation': 'RelatedArtifact', 'subjectCodeableConcept': 'CodeableConcept', 'subjectReference': 'Reference', 'trigger': 'TriggerDefinition', 'condition': 'cdshooksserviceplandefinitionActionCondition', 'input': 'DataRequirement', 'output': 'DataRequirement', 'relatedAction': 'cdshooksserviceplandefinitionActionRelatedAction', 'timingAge': 'Age', 'timingPeriod': 'Period', 'timingDuration': 'Duration', 'timingRange': 'Range', 'timingTiming': 'Timing', 'participant': 'cdshooksserviceplandefinitionActionParticipant', 'type_': 'CodeableConcept', 'dynamicValue': 'cdshooksserviceplandefinitionActionDynamicValue'}
    _choice_fields = {'definition': ['definitionCanonical', 'definitionUri'], 'subject': ['subjectCodeableConcept', 'subjectReference'], 'timing': ['timingDateTime', 'timingAge', 'timingPeriod', 'timingDuration', 'timingRange', 'timingTiming']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    prefix: Optional[String] = None
    title: Optional[String] = None
    description: Optional[String] = None
    textEquivalent: Optional[String] = None
    priority: Optional[Code] = None
    code: CodeableConcept | FHIRList[CodeableConcept]
    reason: CodeableConcept | FHIRList[CodeableConcept]
    documentation: RelatedArtifact | FHIRList[RelatedArtifact]
    goalId: Id | FHIRList[Id] = None
    subjectCodeableConcept: Optional[CodeableConcept]
    subjectReference: Optional[Reference]
    trigger: TriggerDefinition | FHIRList[TriggerDefinition]
    condition: cdshooksserviceplandefinitionActionCondition | FHIRList[cdshooksserviceplandefinitionActionCondition]
    input: DataRequirement | FHIRList[DataRequirement]
    output: DataRequirement | FHIRList[DataRequirement]
    relatedAction: cdshooksserviceplandefinitionActionRelatedAction | FHIRList[cdshooksserviceplandefinitionActionRelatedAction]
    timingDateTime: Optional[DateTime] = None
    timingAge: Optional[Age]
    timingPeriod: Optional[Period]
    timingDuration: Optional[Duration]
    timingRange: Optional[Range]
    timingTiming: Optional[Timing]
    participant: cdshooksserviceplandefinitionActionParticipant | FHIRList[cdshooksserviceplandefinitionActionParticipant]
    type_: Optional[CodeableConcept]
    groupingBehavior: Optional[Code] = None
    selectionBehavior: Optional[Code] = None
    requiredBehavior: Optional[Code] = None
    precheckBehavior: Optional[Code] = None
    cardinalityBehavior: Optional[Code] = None
    definitionCanonical: Optional[Canonical] = None
    definitionUri: Optional[Uri] = None
    transform: Optional[Canonical] = None
    dynamicValue: cdshooksserviceplandefinitionActionDynamicValue | FHIRList[cdshooksserviceplandefinitionActionDynamicValue]
    action: Any = None


class cdshooksserviceplandefinitionActionCondition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    kind: Optional[Code] = None
    expression: Optional[Expression]


class cdshooksserviceplandefinitionActionRelatedAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'offsetDuration': 'Duration', 'offsetRange': 'Range'}
    _choice_fields = {'offset': ['offsetDuration', 'offsetRange']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    actionId: Optional[Id] = None
    relationship: Optional[Code] = None
    offsetDuration: Optional[Duration]
    offsetRange: Optional[Range]


class cdshooksserviceplandefinitionActionParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'role': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    role: Optional[CodeableConcept]


class cdshooksserviceplandefinitionActionDynamicValue(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    path: Optional[String] = None
    expression: Optional[Expression]


class cdshooksserviceplandefinition(FHIRResource):
    _resource_type = "cdshooksserviceplandefinition"
    _list_fields = {'contained', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'library', 'goal', 'action'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'subjectCodeableConcept': 'CodeableConcept', 'subjectReference': 'Reference', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'goal': 'cdshooksserviceplandefinitionGoal', 'action': 'cdshooksserviceplandefinitionAction'}
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Optional[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier]
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    type_: Optional[CodeableConcept]
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    subjectCodeableConcept: Optional[CodeableConcept]
    subjectReference: Optional[Reference]
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
    goal: cdshooksserviceplandefinitionGoal | FHIRList[cdshooksserviceplandefinitionGoal]
    action: cdshooksserviceplandefinitionAction | FHIRList[cdshooksserviceplandefinitionAction]


class cholesterolValue[x](FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class cholesterolReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'low': 'Quantity', 'high': 'Quantity', 'type_': 'CodeableConcept', 'appliesTo': 'CodeableConcept', 'age': 'Range'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    low: Optional[Quantity]
    high: Optional[Quantity]
    type_: Optional[CodeableConcept]
    appliesTo: Optional[CodeableConcept]
    age: Optional[Range]
    text: Optional[String] = None


class cholesterolComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueCodeableConcept': 'CodeableConcept', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueSampledData': 'SampledData', 'valuePeriod': 'Period', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept'}
    _choice_fields = {'value': ['valueQuantity', 'valueCodeableConcept', 'valueString', 'valueBoolean', 'valueInteger', 'valueRange', 'valueRatio', 'valueSampledData', 'valueTime', 'valueDateTime', 'valuePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueQuantity: Optional[Quantity]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueSampledData: Optional[SampledData]
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Optional[Period]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    referenceRange: Any = None


class cholesterol(FHIRResource):
    _resource_type = "cholesterol"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'note', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'effectivePeriod': 'Period', 'effectiveTiming': 'Timing', 'performer': 'Reference', 'valueQuantity': 'Quantity', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'cholesterolReferenceRange', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'cholesterolComponent'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod', 'effectiveTiming', 'effectiveInstant'], 'value': ['valueQuantity']}

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
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    effectiveTiming: Optional[Timing]
    effectiveInstant: Optional[Instant] = None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    valueQuantity: Optional[Quantity]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: Optional[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: Optional[cholesterolReferenceRange]
    hasMember: Optional[Reference]
    derivedFrom: Optional[Reference]
    component: cholesterolComponent | FHIRList[cholesterolComponent]


class clinicaldocumentAttester(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'party': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    mode: Optional[Code] = None
    time: Optional[DateTime] = None
    party: Optional[Reference]


class clinicaldocumentRelatesTo(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'targetIdentifier': 'Identifier', 'targetReference': 'Reference'}
    _choice_fields = {'target': ['targetIdentifier', 'targetReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    targetIdentifier: Optional[Identifier]
    targetReference: Optional[Reference]


class clinicaldocumentEvent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'detail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'period': 'Period', 'detail': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: CodeableConcept | FHIRList[CodeableConcept]
    period: Optional[Period]
    detail: Reference | FHIRList[Reference]


class clinicaldocumentSection(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'author', 'entry', 'section'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'author': 'Reference', 'focus': 'Reference', 'text': 'Narrative', 'orderedBy': 'CodeableConcept', 'entry': 'Reference', 'emptyReason': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    title: Optional[String] = None
    code: Optional[CodeableConcept]
    author: Reference | FHIRList[Reference]
    focus: Optional[Reference]
    text: Optional[Narrative]
    mode: Optional[Code] = None
    orderedBy: Optional[CodeableConcept]
    entry: Reference | FHIRList[Reference]
    emptyReason: Optional[CodeableConcept]
    section: Any = None


class clinicaldocument(FHIRResource):
    _resource_type = "clinicaldocument"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'category', 'author', 'attester', 'relatesTo', 'event', 'section'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'category': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'author': 'Reference', 'attester': 'clinicaldocumentAttester', 'custodian': 'Reference', 'relatesTo': 'clinicaldocumentRelatesTo', 'event': 'clinicaldocumentEvent', 'section': 'clinicaldocumentSection'}

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
    type_: Optional[CodeableConcept]
    category: CodeableConcept | FHIRList[CodeableConcept]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    date: Optional[DateTime] = None
    author: Reference | FHIRList[Reference]
    title: Optional[String] = None
    confidentiality: Optional[Code] = None
    attester: clinicaldocumentAttester | FHIRList[clinicaldocumentAttester]
    custodian: Optional[Reference]
    relatesTo: clinicaldocumentRelatesTo | FHIRList[clinicaldocumentRelatesTo]
    event: clinicaldocumentEvent | FHIRList[clinicaldocumentEvent]
    section: clinicaldocumentSection | FHIRList[clinicaldocumentSection]


class computableplandefinitionGoal(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'addresses', 'documentation', 'target'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'category': 'CodeableConcept', 'description': 'CodeableConcept', 'priority': 'CodeableConcept', 'start': 'CodeableConcept', 'addresses': 'CodeableConcept', 'documentation': 'RelatedArtifact', 'target': 'computableplandefinitionGoalTarget'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    category: Optional[CodeableConcept]
    description: Optional[CodeableConcept]
    priority: Optional[CodeableConcept]
    start: Optional[CodeableConcept]
    addresses: CodeableConcept | FHIRList[CodeableConcept]
    documentation: RelatedArtifact | FHIRList[RelatedArtifact]
    target: computableplandefinitionGoalTarget | FHIRList[computableplandefinitionGoalTarget]


class computableplandefinitionGoalTarget(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'measure': 'CodeableConcept', 'detailQuantity': 'Quantity', 'detailRange': 'Range', 'detailCodeableConcept': 'CodeableConcept', 'due': 'Duration'}
    _choice_fields = {'detail': ['detailQuantity', 'detailRange', 'detailCodeableConcept']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    measure: Optional[CodeableConcept]
    detailQuantity: Optional[Quantity]
    detailRange: Optional[Range]
    detailCodeableConcept: Optional[CodeableConcept]
    due: Optional[Duration]


class computableplandefinitionAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'reason', 'documentation', 'goalId', 'trigger', 'condition', 'input', 'output', 'relatedAction', 'participant', 'dynamicValue', 'action'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'reason': 'CodeableConcept', 'documentation': 'RelatedArtifact', 'subjectCodeableConcept': 'CodeableConcept', 'subjectReference': 'Reference', 'trigger': 'TriggerDefinition', 'condition': 'computableplandefinitionActionCondition', 'input': 'DataRequirement', 'output': 'DataRequirement', 'relatedAction': 'computableplandefinitionActionRelatedAction', 'timingAge': 'Age', 'timingPeriod': 'Period', 'timingDuration': 'Duration', 'timingRange': 'Range', 'timingTiming': 'Timing', 'participant': 'computableplandefinitionActionParticipant', 'type_': 'CodeableConcept', 'dynamicValue': 'computableplandefinitionActionDynamicValue'}
    _choice_fields = {'definition': ['definitionCanonical', 'definitionUri'], 'subject': ['subjectCodeableConcept', 'subjectReference'], 'timing': ['timingDateTime', 'timingAge', 'timingPeriod', 'timingDuration', 'timingRange', 'timingTiming']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    prefix: Optional[String] = None
    title: Optional[String] = None
    description: Optional[String] = None
    textEquivalent: Optional[String] = None
    priority: Optional[Code] = None
    code: CodeableConcept | FHIRList[CodeableConcept]
    reason: CodeableConcept | FHIRList[CodeableConcept]
    documentation: RelatedArtifact | FHIRList[RelatedArtifact]
    goalId: Id | FHIRList[Id] = None
    subjectCodeableConcept: Optional[CodeableConcept]
    subjectReference: Optional[Reference]
    trigger: TriggerDefinition | FHIRList[TriggerDefinition]
    condition: computableplandefinitionActionCondition | FHIRList[computableplandefinitionActionCondition]
    input: DataRequirement | FHIRList[DataRequirement]
    output: DataRequirement | FHIRList[DataRequirement]
    relatedAction: computableplandefinitionActionRelatedAction | FHIRList[computableplandefinitionActionRelatedAction]
    timingDateTime: Optional[DateTime] = None
    timingAge: Optional[Age]
    timingPeriod: Optional[Period]
    timingDuration: Optional[Duration]
    timingRange: Optional[Range]
    timingTiming: Optional[Timing]
    participant: computableplandefinitionActionParticipant | FHIRList[computableplandefinitionActionParticipant]
    type_: Optional[CodeableConcept]
    groupingBehavior: Optional[Code] = None
    selectionBehavior: Optional[Code] = None
    requiredBehavior: Optional[Code] = None
    precheckBehavior: Optional[Code] = None
    cardinalityBehavior: Optional[Code] = None
    definitionCanonical: Optional[Canonical] = None
    definitionUri: Optional[Uri] = None
    transform: Optional[Canonical] = None
    dynamicValue: computableplandefinitionActionDynamicValue | FHIRList[computableplandefinitionActionDynamicValue]
    action: Any = None


class computableplandefinitionActionCondition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    kind: Optional[Code] = None
    expression: Optional[Expression]


class computableplandefinitionActionRelatedAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'offsetDuration': 'Duration', 'offsetRange': 'Range'}
    _choice_fields = {'offset': ['offsetDuration', 'offsetRange']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    actionId: Optional[Id] = None
    relationship: Optional[Code] = None
    offsetDuration: Optional[Duration]
    offsetRange: Optional[Range]


class computableplandefinitionActionParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'role': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    role: Optional[CodeableConcept]


class computableplandefinitionActionDynamicValue(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    path: Optional[String] = None
    expression: Optional[Expression]


class computableplandefinition(FHIRResource):
    _resource_type = "computableplandefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'goal', 'action'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'subjectCodeableConcept': 'CodeableConcept', 'subjectReference': 'Reference', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'goal': 'computableplandefinitionGoal', 'action': 'computableplandefinitionAction'}
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

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
    type_: Optional[CodeableConcept]
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    subjectCodeableConcept: Optional[CodeableConcept]
    subjectReference: Optional[Reference]
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
    goal: computableplandefinitionGoal | FHIRList[computableplandefinitionGoal]
    action: computableplandefinitionAction | FHIRList[computableplandefinitionAction]


class cqllibrary(FHIRResource):
    _resource_type = "cqllibrary"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'parameter', 'dataRequirement', 'content'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'subjectCodeableConcept': 'CodeableConcept', 'subjectReference': 'Reference', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'parameter': 'ParameterDefinition', 'dataRequirement': 'DataRequirement', 'content': 'Attachment'}
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

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
    type_: Optional[CodeableConcept]
    subjectCodeableConcept: Optional[CodeableConcept]
    subjectReference: Optional[Reference]
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


class devicemetricobservationReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'low': 'Quantity', 'high': 'Quantity', 'type_': 'CodeableConcept', 'appliesTo': 'CodeableConcept', 'age': 'Range'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    low: Optional[Quantity]
    high: Optional[Quantity]
    type_: Optional[CodeableConcept]
    appliesTo: CodeableConcept | FHIRList[CodeableConcept]
    age: Optional[Range]
    text: Optional[String] = None


class devicemetricobservationComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueCodeableConcept': 'CodeableConcept', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueSampledData': 'SampledData', 'valuePeriod': 'Period', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept'}
    _choice_fields = {'value': ['valueQuantity', 'valueCodeableConcept', 'valueString', 'valueBoolean', 'valueInteger', 'valueRange', 'valueRatio', 'valueSampledData', 'valueTime', 'valueDateTime', 'valuePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueQuantity: Optional[Quantity]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueSampledData: Optional[SampledData]
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Optional[Period]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    referenceRange: Any = None


class devicemetricobservation(FHIRResource):
    _resource_type = "devicemetricobservation"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'note', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'performer': 'Reference', 'valueQuantity': 'Quantity', 'valueCodeableConcept': 'CodeableConcept', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueSampledData': 'SampledData', 'valuePeriod': 'Period', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'devicemetricobservationReferenceRange', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'devicemetricobservationComponent'}
    _choice_fields = {'effective': ['effectiveDateTime'], 'value': ['valueQuantity', 'valueCodeableConcept', 'valueString', 'valueRange', 'valueRatio', 'valueSampledData', 'valueTime', 'valueDateTime', 'valuePeriod']}

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
    effectiveDateTime: Optional[DateTime] = None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    valueQuantity: Optional[Quantity]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueSampledData: Optional[SampledData]
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Optional[Period]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: Optional[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: Optional[devicemetricobservationReferenceRange]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: devicemetricobservationComponent | FHIRList[devicemetricobservationComponent]


class groupdefinitionCharacteristic(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueCodeableConcept': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueRange': 'Range', 'valueReference': 'Reference', 'period': 'Period'}
    _choice_fields = {'value': ['valueCodeableConcept', 'valueBoolean', 'valueQuantity', 'valueRange', 'valueReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueCodeableConcept: Optional[CodeableConcept]
    valueBoolean: Optional[Boolean] = None
    valueQuantity: Optional[Quantity]
    valueRange: Optional[Range]
    valueReference: Optional[Reference]
    exclude: Optional[Boolean] = None
    period: Optional[Period]


class groupdefinitionMember(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'entity': 'Reference', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    entity: Optional[Reference]
    period: Optional[Period]
    inactive: Optional[Boolean] = None


class groupdefinition(FHIRResource):
    _resource_type = "groupdefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'characteristic'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'code': 'CodeableConcept', 'managingEntity': 'Reference', 'characteristic': 'groupdefinitionCharacteristic', 'member': 'groupdefinitionMember'}

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
    type_: Optional[Code] = None
    actual: Optional[Boolean] = None
    code: Optional[CodeableConcept]
    name: Optional[String] = None
    quantity: Optional[UnsignedInt] = None
    managingEntity: Optional[Reference]
    characteristic: groupdefinitionCharacteristic | FHIRList[groupdefinitionCharacteristic]
    member: Optional[groupdefinitionMember]


class hdlcholesterolReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'low': 'Quantity', 'high': 'Quantity', 'type_': 'CodeableConcept', 'appliesTo': 'CodeableConcept', 'age': 'Range'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    low: Optional[Quantity]
    high: Optional[Quantity]
    type_: Optional[CodeableConcept]
    appliesTo: Optional[CodeableConcept]
    age: Optional[Range]
    text: Optional[String] = None


class hdlcholesterolComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueCodeableConcept': 'CodeableConcept', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueSampledData': 'SampledData', 'valuePeriod': 'Period', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept'}
    _choice_fields = {'value': ['valueQuantity', 'valueCodeableConcept', 'valueString', 'valueBoolean', 'valueInteger', 'valueRange', 'valueRatio', 'valueSampledData', 'valueTime', 'valueDateTime', 'valuePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueQuantity: Optional[Quantity]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueSampledData: Optional[SampledData]
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Optional[Period]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    referenceRange: Any = None


class hdlcholesterol(FHIRResource):
    _resource_type = "hdlcholesterol"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'note', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'effectivePeriod': 'Period', 'effectiveTiming': 'Timing', 'performer': 'Reference', 'valueQuantity': 'Quantity', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'hdlcholesterolReferenceRange', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'hdlcholesterolComponent'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod', 'effectiveTiming', 'effectiveInstant'], 'value': ['valueQuantity']}

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
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    effectiveTiming: Optional[Timing]
    effectiveInstant: Optional[Instant] = None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    valueQuantity: Optional[Quantity]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: Optional[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: Optional[hdlcholesterolReferenceRange]
    hasMember: Optional[Reference]
    derivedFrom: Optional[Reference]
    component: hdlcholesterolComponent | FHIRList[hdlcholesterolComponent]


class headcircumCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Coding | FHIRList[Coding]
    text: Optional[String] = None


class headcircumCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class headcircumCode(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Optional[Coding]
    text: Optional[String] = None


class headcircumCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class headcircumValue[x](FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class headcircumReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'low': 'Quantity', 'high': 'Quantity', 'type_': 'CodeableConcept', 'appliesTo': 'CodeableConcept', 'age': 'Range'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    low: Optional[Quantity]
    high: Optional[Quantity]
    type_: Optional[CodeableConcept]
    appliesTo: CodeableConcept | FHIRList[CodeableConcept]
    age: Optional[Range]
    text: Optional[String] = None


class headcircumComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueCodeableConcept': 'CodeableConcept', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueSampledData': 'SampledData', 'valuePeriod': 'Period', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept'}
    _choice_fields = {'value': ['valueQuantity', 'valueCodeableConcept', 'valueString', 'valueBoolean', 'valueInteger', 'valueRange', 'valueRatio', 'valueSampledData', 'valueTime', 'valueDateTime', 'valuePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueQuantity: Optional[Quantity]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueSampledData: Optional[SampledData]
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Optional[Period]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    referenceRange: Any = None


class headcircum(FHIRResource):
    _resource_type = "headcircum"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'effectivePeriod': 'Period', 'performer': 'Reference', 'valueQuantity': 'Quantity', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'headcircumReferenceRange', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'headcircumComponent'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'value': ['valueQuantity']}

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
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    valueQuantity: Optional[Quantity]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: headcircumReferenceRange | FHIRList[headcircumReferenceRange]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: headcircumComponent | FHIRList[headcircumComponent]


class heartrateCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Coding | FHIRList[Coding]
    text: Optional[String] = None


class heartrateCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class heartrateCode(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Optional[Coding]
    text: Optional[String] = None


class heartrateCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class heartrateValue[x](FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class heartrateReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'low': 'Quantity', 'high': 'Quantity', 'type_': 'CodeableConcept', 'appliesTo': 'CodeableConcept', 'age': 'Range'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    low: Optional[Quantity]
    high: Optional[Quantity]
    type_: Optional[CodeableConcept]
    appliesTo: CodeableConcept | FHIRList[CodeableConcept]
    age: Optional[Range]
    text: Optional[String] = None


class heartrateComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueCodeableConcept': 'CodeableConcept', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueSampledData': 'SampledData', 'valuePeriod': 'Period', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept'}
    _choice_fields = {'value': ['valueQuantity', 'valueCodeableConcept', 'valueString', 'valueBoolean', 'valueInteger', 'valueRange', 'valueRatio', 'valueSampledData', 'valueTime', 'valueDateTime', 'valuePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueQuantity: Optional[Quantity]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueSampledData: Optional[SampledData]
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Optional[Period]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    referenceRange: Any = None


class heartrate(FHIRResource):
    _resource_type = "heartrate"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'effectivePeriod': 'Period', 'performer': 'Reference', 'valueQuantity': 'Quantity', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'heartrateReferenceRange', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'heartrateComponent'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'value': ['valueQuantity']}

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
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    valueQuantity: Optional[Quantity]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: heartrateReferenceRange | FHIRList[heartrateReferenceRange]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: heartrateComponent | FHIRList[heartrateComponent]


class hlaresultMedia(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'link': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    comment: Optional[String] = None
    link: Optional[Reference]


class hlaresult(FHIRResource):
    _resource_type = "hlaresult"
    _list_fields = {'contained', 'modifierExtension', 'identifier', 'basedOn', 'category', 'performer', 'resultsInterpreter', 'specimen', 'result', 'imagingStudy', 'media', 'conclusionCode', 'presentedForm'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'effectivePeriod': 'Period', 'performer': 'Reference', 'resultsInterpreter': 'Reference', 'specimen': 'Reference', 'result': 'Reference', 'imagingStudy': 'Reference', 'media': 'hlaresultMedia', 'conclusionCode': 'CodeableConcept', 'presentedForm': 'Attachment'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod']}

    id: Optional[str] = None
    meta: Optional[Meta]
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Optional[Narrative]
    contained: Resource | FHIRList[Resource]
    extension: Optional[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Identifier | FHIRList[Identifier]
    basedOn: Reference | FHIRList[Reference]
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    encounter: Optional[Reference]
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    resultsInterpreter: Reference | FHIRList[Reference]
    specimen: Reference | FHIRList[Reference]
    result: Reference | FHIRList[Reference]
    imagingStudy: Reference | FHIRList[Reference]
    media: hlaresultMedia | FHIRList[hlaresultMedia]
    conclusion: Optional[String] = None
    conclusionCode: CodeableConcept | FHIRList[CodeableConcept]
    presentedForm: Attachment | FHIRList[Attachment]


class ldlcholesterolReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'low': 'Quantity', 'high': 'Quantity', 'type_': 'CodeableConcept', 'appliesTo': 'CodeableConcept', 'age': 'Range'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    low: Optional[Quantity]
    high: Optional[Quantity]
    type_: Optional[CodeableConcept]
    appliesTo: Optional[CodeableConcept]
    age: Optional[Range]
    text: Optional[String] = None


class ldlcholesterolComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueCodeableConcept': 'CodeableConcept', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueSampledData': 'SampledData', 'valuePeriod': 'Period', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept'}
    _choice_fields = {'value': ['valueQuantity', 'valueCodeableConcept', 'valueString', 'valueBoolean', 'valueInteger', 'valueRange', 'valueRatio', 'valueSampledData', 'valueTime', 'valueDateTime', 'valuePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueQuantity: Optional[Quantity]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueSampledData: Optional[SampledData]
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Optional[Period]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    referenceRange: Any = None


class ldlcholesterol(FHIRResource):
    _resource_type = "ldlcholesterol"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'note', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'effectivePeriod': 'Period', 'effectiveTiming': 'Timing', 'performer': 'Reference', 'valueQuantity': 'Quantity', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'ldlcholesterolReferenceRange', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'ldlcholesterolComponent'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod', 'effectiveTiming', 'effectiveInstant'], 'value': ['valueQuantity']}

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
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    effectiveTiming: Optional[Timing]
    effectiveInstant: Optional[Instant] = None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    valueQuantity: Optional[Quantity]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: Optional[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: Optional[ldlcholesterolReferenceRange]
    hasMember: Optional[Reference]
    derivedFrom: Optional[Reference]
    component: ldlcholesterolComponent | FHIRList[ldlcholesterolComponent]


class lipidprofileMedia(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'link': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    comment: Optional[String] = None
    link: Optional[Reference]


class lipidprofile(FHIRResource):
    _resource_type = "lipidprofile"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'category', 'performer', 'resultsInterpreter', 'specimen', 'imagingStudy', 'media', 'presentedForm'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'encounter': 'Reference', 'effectivePeriod': 'Period', 'performer': 'Reference', 'resultsInterpreter': 'Reference', 'specimen': 'Reference', 'result': 'Reference', 'imagingStudy': 'Reference', 'media': 'lipidprofileMedia', 'conclusionCode': 'CodeableConcept', 'presentedForm': 'Attachment'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod']}

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
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    resultsInterpreter: Reference | FHIRList[Reference]
    specimen: Reference | FHIRList[Reference]
    result: Optional[Reference]
    imagingStudy: Reference | FHIRList[Reference]
    media: lipidprofileMedia | FHIRList[lipidprofileMedia]
    conclusion: Optional[String] = None
    conclusionCode: Optional[CodeableConcept]
    presentedForm: Attachment | FHIRList[Attachment]


class oxygensatCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Coding | FHIRList[Coding]
    text: Optional[String] = None


class oxygensatCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class oxygensatCode(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Optional[Coding]
    text: Optional[String] = None


class oxygensatCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class oxygensatValue[x](FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class oxygensatReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'low': 'Quantity', 'high': 'Quantity', 'type_': 'CodeableConcept', 'appliesTo': 'CodeableConcept', 'age': 'Range'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    low: Optional[Quantity]
    high: Optional[Quantity]
    type_: Optional[CodeableConcept]
    appliesTo: CodeableConcept | FHIRList[CodeableConcept]
    age: Optional[Range]
    text: Optional[String] = None


class oxygensatComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueCodeableConcept': 'CodeableConcept', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueSampledData': 'SampledData', 'valuePeriod': 'Period', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept'}
    _choice_fields = {'value': ['valueQuantity', 'valueCodeableConcept', 'valueString', 'valueBoolean', 'valueInteger', 'valueRange', 'valueRatio', 'valueSampledData', 'valueTime', 'valueDateTime', 'valuePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueQuantity: Optional[Quantity]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueSampledData: Optional[SampledData]
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Optional[Period]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    referenceRange: Any = None


class oxygensat(FHIRResource):
    _resource_type = "oxygensat"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'effectivePeriod': 'Period', 'performer': 'Reference', 'valueQuantity': 'Quantity', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'oxygensatReferenceRange', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'oxygensatComponent'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'value': ['valueQuantity']}

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
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    valueQuantity: Optional[Quantity]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: oxygensatReferenceRange | FHIRList[oxygensatReferenceRange]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: oxygensatComponent | FHIRList[oxygensatComponent]


class picoelementCharacteristic(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'usageContext'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'definitionReference': 'Reference', 'definitionCodeableConcept': 'CodeableConcept', 'definitionExpression': 'Expression', 'definitionDataRequirement': 'DataRequirement', 'definitionTriggerDefinition': 'TriggerDefinition', 'usageContext': 'UsageContext', 'participantEffectivePeriod': 'Period', 'participantEffectiveDuration': 'Duration', 'participantEffectiveTiming': 'Timing', 'timeFromStart': 'Duration'}
    _choice_fields = {'definition': ['definitionReference', 'definitionCanonical', 'definitionCodeableConcept', 'definitionExpression', 'definitionDataRequirement', 'definitionTriggerDefinition'], 'participantEffective': ['participantEffectiveDateTime', 'participantEffectivePeriod', 'participantEffectiveDuration', 'participantEffectiveTiming']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    description: Optional[String] = None
    definitionReference: Optional[Reference]
    definitionCanonical: Optional[Canonical] = None
    definitionCodeableConcept: Optional[CodeableConcept]
    definitionExpression: Optional[Expression]
    definitionDataRequirement: Optional[DataRequirement]
    definitionTriggerDefinition: Optional[TriggerDefinition]
    usageContext: UsageContext | FHIRList[UsageContext]
    exclude: Optional[Boolean] = None
    participantEffectiveDateTime: Optional[DateTime] = None
    participantEffectivePeriod: Optional[Period]
    participantEffectiveDuration: Optional[Duration]
    participantEffectiveTiming: Optional[Timing]
    timeFromStart: Optional[Duration]
    groupMeasure: Optional[Code] = None


class picoelement(FHIRResource):
    _resource_type = "picoelement"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'note', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'characteristic'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'note': 'Annotation', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'characteristic': 'picoelementCharacteristic'}

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
    type_: Optional[Code] = None
    characteristic: picoelementCharacteristic | FHIRList[picoelementCharacteristic]


class resprateCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Coding | FHIRList[Coding]
    text: Optional[String] = None


class resprateCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class resprateCode(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Optional[Coding]
    text: Optional[String] = None


class resprateCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class resprateValue[x](FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class resprateReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'low': 'Quantity', 'high': 'Quantity', 'type_': 'CodeableConcept', 'appliesTo': 'CodeableConcept', 'age': 'Range'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    low: Optional[Quantity]
    high: Optional[Quantity]
    type_: Optional[CodeableConcept]
    appliesTo: CodeableConcept | FHIRList[CodeableConcept]
    age: Optional[Range]
    text: Optional[String] = None


class resprateComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueCodeableConcept': 'CodeableConcept', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueSampledData': 'SampledData', 'valuePeriod': 'Period', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept'}
    _choice_fields = {'value': ['valueQuantity', 'valueCodeableConcept', 'valueString', 'valueBoolean', 'valueInteger', 'valueRange', 'valueRatio', 'valueSampledData', 'valueTime', 'valueDateTime', 'valuePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueQuantity: Optional[Quantity]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueSampledData: Optional[SampledData]
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Optional[Period]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    referenceRange: Any = None


class resprate(FHIRResource):
    _resource_type = "resprate"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'effectivePeriod': 'Period', 'performer': 'Reference', 'valueQuantity': 'Quantity', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'resprateReferenceRange', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'resprateComponent'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'value': ['valueQuantity']}

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
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    valueQuantity: Optional[Quantity]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: resprateReferenceRange | FHIRList[resprateReferenceRange]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: resprateComponent | FHIRList[resprateComponent]


class shareableactivitydefinitionParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'role': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    role: Optional[CodeableConcept]


class shareableactivitydefinitionDynamicValue(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    path: Optional[String] = None
    expression: Optional[Expression]


class shareableactivitydefinition(FHIRResource):
    _resource_type = "shareableactivitydefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'library', 'participant', 'dosage', 'bodySite', 'specimenRequirement', 'observationRequirement', 'observationResultRequirement', 'dynamicValue'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'subjectCodeableConcept': 'CodeableConcept', 'subjectReference': 'Reference', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'code': 'CodeableConcept', 'timingTiming': 'Timing', 'timingAge': 'Age', 'timingPeriod': 'Period', 'timingRange': 'Range', 'timingDuration': 'Duration', 'location': 'Reference', 'participant': 'shareableactivitydefinitionParticipant', 'productReference': 'Reference', 'productCodeableConcept': 'CodeableConcept', 'quantity': 'Quantity', 'dosage': 'Dosage', 'bodySite': 'CodeableConcept', 'specimenRequirement': 'Reference', 'observationRequirement': 'Reference', 'observationResultRequirement': 'Reference', 'dynamicValue': 'shareableactivitydefinitionDynamicValue'}
    _choice_fields = {'product': ['productReference', 'productCodeableConcept'], 'subject': ['subjectCodeableConcept', 'subjectReference'], 'timing': ['timingTiming', 'timingDateTime', 'timingAge', 'timingPeriod', 'timingRange', 'timingDuration']}

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
    subjectCodeableConcept: Optional[CodeableConcept]
    subjectReference: Optional[Reference]
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
    timingTiming: Optional[Timing]
    timingDateTime: Optional[DateTime] = None
    timingAge: Optional[Age]
    timingPeriod: Optional[Period]
    timingRange: Optional[Range]
    timingDuration: Optional[Duration]
    location: Optional[Reference]
    participant: shareableactivitydefinitionParticipant | FHIRList[shareableactivitydefinitionParticipant]
    productReference: Optional[Reference]
    productCodeableConcept: Optional[CodeableConcept]
    quantity: Optional[Quantity]
    dosage: Dosage | FHIRList[Dosage]
    bodySite: CodeableConcept | FHIRList[CodeableConcept]
    specimenRequirement: Reference | FHIRList[Reference]
    observationRequirement: Reference | FHIRList[Reference]
    observationResultRequirement: Reference | FHIRList[Reference]
    transform: Optional[Canonical] = None
    dynamicValue: shareableactivitydefinitionDynamicValue | FHIRList[shareableactivitydefinitionDynamicValue]


class shareablecodesystemFilter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'operator'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    description: Optional[String] = None
    operator: Code | FHIRList[Code] = None
    value: Optional[String] = None


class shareablecodesystemProperty(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    uri: Optional[Uri] = None
    description: Optional[String] = None
    type_: Optional[Code] = None


class shareablecodesystemConcept(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'designation', 'property', 'concept'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'designation': 'shareablecodesystemConceptDesignation', 'property': 'shareablecodesystemConceptProperty'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    display: Optional[String] = None
    definition: Optional[String] = None
    designation: shareablecodesystemConceptDesignation | FHIRList[shareablecodesystemConceptDesignation]
    property: shareablecodesystemConceptProperty | FHIRList[shareablecodesystemConceptProperty]
    concept: Any = None


class shareablecodesystemConceptDesignation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'use': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    language: Optional[Code] = None
    use: Optional[Coding]
    value: Optional[String] = None


class shareablecodesystemConceptProperty(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'valueCoding': 'Coding'}
    _choice_fields = {'value': ['valueCode', 'valueCoding', 'valueString', 'valueInteger', 'valueBoolean', 'valueDateTime', 'valueDecimal']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    valueCode: Optional[Code] = None
    valueCoding: Optional[Coding]
    valueString: Optional[String] = None
    valueInteger: Optional[Integer] = None
    valueBoolean: Optional[Boolean] = None
    valueDateTime: Optional[DateTime] = None
    valueDecimal: Optional[Decimal] = None


class shareablecodesystem(FHIRResource):
    _resource_type = "shareablecodesystem"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'filter', 'property', 'concept'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'filter': 'shareablecodesystemFilter', 'property': 'shareablecodesystemProperty', 'concept': 'shareablecodesystemConcept'}

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
    filter: shareablecodesystemFilter | FHIRList[shareablecodesystemFilter]
    property: shareablecodesystemProperty | FHIRList[shareablecodesystemProperty]
    concept: shareablecodesystemConcept | FHIRList[shareablecodesystemConcept]


class shareablelibrary(FHIRResource):
    _resource_type = "shareablelibrary"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'parameter', 'dataRequirement', 'content'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'subjectCodeableConcept': 'CodeableConcept', 'subjectReference': 'Reference', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'parameter': 'ParameterDefinition', 'dataRequirement': 'DataRequirement', 'content': 'Attachment'}
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

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
    type_: Optional[CodeableConcept]
    subjectCodeableConcept: Optional[CodeableConcept]
    subjectReference: Optional[Reference]
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


class shareablemeasureGroup(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'population', 'stratifier'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'population': 'shareablemeasureGroupPopulation', 'stratifier': 'shareablemeasureGroupStratifier'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    description: Optional[String] = None
    population: shareablemeasureGroupPopulation | FHIRList[shareablemeasureGroupPopulation]
    stratifier: shareablemeasureGroupStratifier | FHIRList[shareablemeasureGroupStratifier]


class shareablemeasureGroupPopulation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'criteria': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    description: Optional[String] = None
    criteria: Optional[Expression]


class shareablemeasureGroupStratifier(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'component'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'criteria': 'Expression', 'component': 'shareablemeasureGroupStratifierComponent'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    description: Optional[String] = None
    criteria: Optional[Expression]
    component: shareablemeasureGroupStratifierComponent | FHIRList[shareablemeasureGroupStratifierComponent]


class shareablemeasureGroupStratifierComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'criteria': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    description: Optional[String] = None
    criteria: Optional[Expression]


class shareablemeasureSupplementalData(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'usage'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'usage': 'CodeableConcept', 'criteria': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    usage: CodeableConcept | FHIRList[CodeableConcept]
    description: Optional[String] = None
    criteria: Optional[Expression]


class shareablemeasure(FHIRResource):
    _resource_type = "shareablemeasure"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'library', 'type_', 'definition', 'group', 'supplementalData'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'subjectCodeableConcept': 'CodeableConcept', 'subjectReference': 'Reference', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'scoring': 'CodeableConcept', 'compositeScoring': 'CodeableConcept', 'type_': 'CodeableConcept', 'improvementNotation': 'CodeableConcept', 'group': 'shareablemeasureGroup', 'supplementalData': 'shareablemeasureSupplementalData'}
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

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
    subjectCodeableConcept: Optional[CodeableConcept]
    subjectReference: Optional[Reference]
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
    type_: CodeableConcept | FHIRList[CodeableConcept]
    riskAdjustment: Optional[String] = None
    rateAggregation: Optional[String] = None
    rationale: Optional[Markdown] = None
    clinicalRecommendationStatement: Optional[Markdown] = None
    improvementNotation: Optional[CodeableConcept]
    definition: Markdown | FHIRList[Markdown] = None
    guidance: Optional[Markdown] = None
    group: shareablemeasureGroup | FHIRList[shareablemeasureGroup]
    supplementalData: shareablemeasureSupplementalData | FHIRList[shareablemeasureSupplementalData]


class shareableplandefinitionGoal(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'addresses', 'documentation', 'target'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'category': 'CodeableConcept', 'description': 'CodeableConcept', 'priority': 'CodeableConcept', 'start': 'CodeableConcept', 'addresses': 'CodeableConcept', 'documentation': 'RelatedArtifact', 'target': 'shareableplandefinitionGoalTarget'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    category: Optional[CodeableConcept]
    description: Optional[CodeableConcept]
    priority: Optional[CodeableConcept]
    start: Optional[CodeableConcept]
    addresses: CodeableConcept | FHIRList[CodeableConcept]
    documentation: RelatedArtifact | FHIRList[RelatedArtifact]
    target: shareableplandefinitionGoalTarget | FHIRList[shareableplandefinitionGoalTarget]


class shareableplandefinitionGoalTarget(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'measure': 'CodeableConcept', 'detailQuantity': 'Quantity', 'detailRange': 'Range', 'detailCodeableConcept': 'CodeableConcept', 'due': 'Duration'}
    _choice_fields = {'detail': ['detailQuantity', 'detailRange', 'detailCodeableConcept']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    measure: Optional[CodeableConcept]
    detailQuantity: Optional[Quantity]
    detailRange: Optional[Range]
    detailCodeableConcept: Optional[CodeableConcept]
    due: Optional[Duration]


class shareableplandefinitionAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'reason', 'documentation', 'goalId', 'trigger', 'condition', 'input', 'output', 'relatedAction', 'participant', 'dynamicValue', 'action'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'reason': 'CodeableConcept', 'documentation': 'RelatedArtifact', 'subjectCodeableConcept': 'CodeableConcept', 'subjectReference': 'Reference', 'trigger': 'TriggerDefinition', 'condition': 'shareableplandefinitionActionCondition', 'input': 'DataRequirement', 'output': 'DataRequirement', 'relatedAction': 'shareableplandefinitionActionRelatedAction', 'timingAge': 'Age', 'timingPeriod': 'Period', 'timingDuration': 'Duration', 'timingRange': 'Range', 'timingTiming': 'Timing', 'participant': 'shareableplandefinitionActionParticipant', 'type_': 'CodeableConcept', 'dynamicValue': 'shareableplandefinitionActionDynamicValue'}
    _choice_fields = {'definition': ['definitionCanonical', 'definitionUri'], 'subject': ['subjectCodeableConcept', 'subjectReference'], 'timing': ['timingDateTime', 'timingAge', 'timingPeriod', 'timingDuration', 'timingRange', 'timingTiming']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    prefix: Optional[String] = None
    title: Optional[String] = None
    description: Optional[String] = None
    textEquivalent: Optional[String] = None
    priority: Optional[Code] = None
    code: CodeableConcept | FHIRList[CodeableConcept]
    reason: CodeableConcept | FHIRList[CodeableConcept]
    documentation: RelatedArtifact | FHIRList[RelatedArtifact]
    goalId: Id | FHIRList[Id] = None
    subjectCodeableConcept: Optional[CodeableConcept]
    subjectReference: Optional[Reference]
    trigger: TriggerDefinition | FHIRList[TriggerDefinition]
    condition: shareableplandefinitionActionCondition | FHIRList[shareableplandefinitionActionCondition]
    input: DataRequirement | FHIRList[DataRequirement]
    output: DataRequirement | FHIRList[DataRequirement]
    relatedAction: shareableplandefinitionActionRelatedAction | FHIRList[shareableplandefinitionActionRelatedAction]
    timingDateTime: Optional[DateTime] = None
    timingAge: Optional[Age]
    timingPeriod: Optional[Period]
    timingDuration: Optional[Duration]
    timingRange: Optional[Range]
    timingTiming: Optional[Timing]
    participant: shareableplandefinitionActionParticipant | FHIRList[shareableplandefinitionActionParticipant]
    type_: Optional[CodeableConcept]
    groupingBehavior: Optional[Code] = None
    selectionBehavior: Optional[Code] = None
    requiredBehavior: Optional[Code] = None
    precheckBehavior: Optional[Code] = None
    cardinalityBehavior: Optional[Code] = None
    definitionCanonical: Optional[Canonical] = None
    definitionUri: Optional[Uri] = None
    transform: Optional[Canonical] = None
    dynamicValue: shareableplandefinitionActionDynamicValue | FHIRList[shareableplandefinitionActionDynamicValue]
    action: Any = None


class shareableplandefinitionActionCondition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    kind: Optional[Code] = None
    expression: Optional[Expression]


class shareableplandefinitionActionRelatedAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'offsetDuration': 'Duration', 'offsetRange': 'Range'}
    _choice_fields = {'offset': ['offsetDuration', 'offsetRange']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    actionId: Optional[Id] = None
    relationship: Optional[Code] = None
    offsetDuration: Optional[Duration]
    offsetRange: Optional[Range]


class shareableplandefinitionActionParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'role': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    role: Optional[CodeableConcept]


class shareableplandefinitionActionDynamicValue(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    path: Optional[String] = None
    expression: Optional[Expression]


class shareableplandefinition(FHIRResource):
    _resource_type = "shareableplandefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'topic', 'author', 'editor', 'reviewer', 'endorser', 'relatedArtifact', 'library', 'goal', 'action'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'subjectCodeableConcept': 'CodeableConcept', 'subjectReference': 'Reference', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'effectivePeriod': 'Period', 'topic': 'CodeableConcept', 'author': 'ContactDetail', 'editor': 'ContactDetail', 'reviewer': 'ContactDetail', 'endorser': 'ContactDetail', 'relatedArtifact': 'RelatedArtifact', 'goal': 'shareableplandefinitionGoal', 'action': 'shareableplandefinitionAction'}
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

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
    type_: Optional[CodeableConcept]
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    subjectCodeableConcept: Optional[CodeableConcept]
    subjectReference: Optional[Reference]
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
    goal: shareableplandefinitionGoal | FHIRList[shareableplandefinitionGoal]
    action: shareableplandefinitionAction | FHIRList[shareableplandefinitionAction]


class shareablevaluesetCompose(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'include', 'exclude'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'include': 'shareablevaluesetComposeInclude'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    lockedDate: Optional[Date] = None
    inactive: Optional[Boolean] = None
    include: shareablevaluesetComposeInclude | FHIRList[shareablevaluesetComposeInclude]
    exclude: Any = None


class shareablevaluesetComposeInclude(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'concept', 'filter', 'valueSet'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'concept': 'shareablevaluesetComposeIncludeConcept', 'filter': 'shareablevaluesetComposeIncludeFilter'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    concept: shareablevaluesetComposeIncludeConcept | FHIRList[shareablevaluesetComposeIncludeConcept]
    filter: shareablevaluesetComposeIncludeFilter | FHIRList[shareablevaluesetComposeIncludeFilter]
    valueSet: Canonical | FHIRList[Canonical] = None


class shareablevaluesetComposeIncludeConcept(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'designation'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'designation': 'shareablevaluesetComposeIncludeConceptDesignation'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[Code] = None
    display: Optional[String] = None
    designation: shareablevaluesetComposeIncludeConceptDesignation | FHIRList[shareablevaluesetComposeIncludeConceptDesignation]


class shareablevaluesetComposeIncludeConceptDesignation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'use': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    language: Optional[Code] = None
    use: Optional[Coding]
    value: Optional[String] = None


class shareablevaluesetComposeIncludeFilter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    property: Optional[Code] = None
    op: Optional[Code] = None
    value: Optional[String] = None


class shareablevaluesetExpansion(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'parameter', 'contains'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'parameter': 'shareablevaluesetExpansionParameter', 'contains': 'shareablevaluesetExpansionContains'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Uri] = None
    timestamp: Optional[DateTime] = None
    total: Optional[Integer] = None
    offset: Optional[Integer] = None
    parameter: shareablevaluesetExpansionParameter | FHIRList[shareablevaluesetExpansionParameter]
    contains: shareablevaluesetExpansionContains | FHIRList[shareablevaluesetExpansionContains]


class shareablevaluesetExpansionParameter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}
    _choice_fields = {'value': ['valueString', 'valueBoolean', 'valueInteger', 'valueDecimal', 'valueUri', 'valueCode', 'valueDateTime']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    name: Optional[String] = None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueDecimal: Optional[Decimal] = None
    valueUri: Optional[Uri] = None
    valueCode: Optional[Code] = None
    valueDateTime: Optional[DateTime] = None


class shareablevaluesetExpansionContains(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'designation', 'contains'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    abstract: Optional[Boolean] = None
    inactive: Optional[Boolean] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    designation: Any = None
    contains: Any = None


class shareablevalueset(FHIRResource):
    _resource_type = "shareablevalueset"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'contact': 'ContactDetail', 'useContext': 'UsageContext', 'jurisdiction': 'CodeableConcept', 'compose': 'shareablevaluesetCompose', 'expansion': 'shareablevaluesetExpansion'}

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
    compose: Optional[shareablevaluesetCompose]
    expansion: Optional[shareablevaluesetExpansion]


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


class triglycerideReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'low': 'Quantity', 'high': 'Quantity', 'type_': 'CodeableConcept', 'appliesTo': 'CodeableConcept', 'age': 'Range'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    low: Optional[Quantity]
    high: Optional[Quantity]
    type_: Optional[CodeableConcept]
    appliesTo: Optional[CodeableConcept]
    age: Optional[Range]
    text: Optional[String] = None


class triglycerideComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueCodeableConcept': 'CodeableConcept', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueSampledData': 'SampledData', 'valuePeriod': 'Period', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept'}
    _choice_fields = {'value': ['valueQuantity', 'valueCodeableConcept', 'valueString', 'valueBoolean', 'valueInteger', 'valueRange', 'valueRatio', 'valueSampledData', 'valueTime', 'valueDateTime', 'valuePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueQuantity: Optional[Quantity]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueSampledData: Optional[SampledData]
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Optional[Period]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    referenceRange: Any = None


class triglyceride(FHIRResource):
    _resource_type = "triglyceride"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'note', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'effectivePeriod': 'Period', 'effectiveTiming': 'Timing', 'performer': 'Reference', 'valueQuantity': 'Quantity', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'triglycerideReferenceRange', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'triglycerideComponent'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod', 'effectiveTiming', 'effectiveInstant'], 'value': ['valueQuantity']}

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
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    effectiveTiming: Optional[Timing]
    effectiveInstant: Optional[Instant] = None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    valueQuantity: Optional[Quantity]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: Optional[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: Optional[triglycerideReferenceRange]
    hasMember: Optional[Reference]
    derivedFrom: Optional[Reference]
    component: triglycerideComponent | FHIRList[triglycerideComponent]


class vitalsignsCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Coding | FHIRList[Coding]
    text: Optional[String] = None


class vitalsignsCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class vitalsignsReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'low': 'Quantity', 'high': 'Quantity', 'type_': 'CodeableConcept', 'appliesTo': 'CodeableConcept', 'age': 'Range'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    low: Optional[Quantity]
    high: Optional[Quantity]
    type_: Optional[CodeableConcept]
    appliesTo: CodeableConcept | FHIRList[CodeableConcept]
    age: Optional[Range]
    text: Optional[String] = None


class vitalsignsComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueCodeableConcept': 'CodeableConcept', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueSampledData': 'SampledData', 'valuePeriod': 'Period', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept'}
    _choice_fields = {'value': ['valueQuantity', 'valueCodeableConcept', 'valueString', 'valueBoolean', 'valueInteger', 'valueRange', 'valueRatio', 'valueSampledData', 'valueTime', 'valueDateTime', 'valuePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueQuantity: Optional[Quantity]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueSampledData: Optional[SampledData]
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Optional[Period]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    referenceRange: Any = None


class vitalsigns(FHIRResource):
    _resource_type = "vitalsigns"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'effectivePeriod': 'Period', 'performer': 'Reference', 'valueQuantity': 'Quantity', 'valueCodeableConcept': 'CodeableConcept', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueSampledData': 'SampledData', 'valuePeriod': 'Period', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'vitalsignsReferenceRange', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'vitalsignsComponent'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'value': ['valueQuantity', 'valueCodeableConcept', 'valueString', 'valueBoolean', 'valueInteger', 'valueRange', 'valueRatio', 'valueSampledData', 'valueTime', 'valueDateTime', 'valuePeriod']}

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
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    valueQuantity: Optional[Quantity]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueSampledData: Optional[SampledData]
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Optional[Period]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: vitalsignsReferenceRange | FHIRList[vitalsignsReferenceRange]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: vitalsignsComponent | FHIRList[vitalsignsComponent]


class vitalspanelCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Coding | FHIRList[Coding]
    text: Optional[String] = None


class vitalspanelCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class vitalspanelCode(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Coding | FHIRList[Coding]
    text: Optional[String] = None


class vitalspanelCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class vitalspanelReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'low': 'Quantity', 'high': 'Quantity', 'type_': 'CodeableConcept', 'appliesTo': 'CodeableConcept', 'age': 'Range'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    low: Optional[Quantity]
    high: Optional[Quantity]
    type_: Optional[CodeableConcept]
    appliesTo: CodeableConcept | FHIRList[CodeableConcept]
    age: Optional[Range]
    text: Optional[String] = None


class vitalspanelComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueCodeableConcept': 'CodeableConcept', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueSampledData': 'SampledData', 'valuePeriod': 'Period', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept'}
    _choice_fields = {'value': ['valueQuantity', 'valueCodeableConcept', 'valueString', 'valueBoolean', 'valueInteger', 'valueRange', 'valueRatio', 'valueSampledData', 'valueTime', 'valueDateTime', 'valuePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    code: Optional[CodeableConcept]
    valueQuantity: Optional[Quantity]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueSampledData: Optional[SampledData]
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Optional[Period]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    referenceRange: Any = None


class vitalspanel(FHIRResource):
    _resource_type = "vitalspanel"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'focus', 'performer', 'interpretation', 'note', 'referenceRange', 'hasMember', 'derivedFrom', 'component'}
    _field_types = {'meta': 'Meta', 'text': 'Narrative', 'contained': 'Resource', 'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'basedOn': 'Reference', 'partOf': 'Reference', 'category': 'CodeableConcept', 'code': 'CodeableConcept', 'subject': 'Reference', 'focus': 'Reference', 'encounter': 'Reference', 'effectivePeriod': 'Period', 'performer': 'Reference', 'valueQuantity': 'Quantity', 'valueCodeableConcept': 'CodeableConcept', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueSampledData': 'SampledData', 'valuePeriod': 'Period', 'dataAbsentReason': 'CodeableConcept', 'interpretation': 'CodeableConcept', 'note': 'Annotation', 'bodySite': 'CodeableConcept', 'method': 'CodeableConcept', 'specimen': 'Reference', 'device': 'Reference', 'referenceRange': 'vitalspanelReferenceRange', 'hasMember': 'Reference', 'derivedFrom': 'Reference', 'component': 'vitalspanelComponent'}
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'value': ['valueQuantity', 'valueCodeableConcept', 'valueString', 'valueBoolean', 'valueInteger', 'valueRange', 'valueRatio', 'valueSampledData', 'valueTime', 'valueDateTime', 'valuePeriod']}

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
    category: Optional[CodeableConcept]
    code: Optional[CodeableConcept]
    subject: Optional[Reference]
    focus: Reference | FHIRList[Reference]
    encounter: Optional[Reference]
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Optional[Period]
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference]
    valueQuantity: Optional[Quantity]
    valueCodeableConcept: Optional[CodeableConcept]
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Optional[Range]
    valueRatio: Optional[Ratio]
    valueSampledData: Optional[SampledData]
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Optional[Period]
    dataAbsentReason: Optional[CodeableConcept]
    interpretation: CodeableConcept | FHIRList[CodeableConcept]
    note: Annotation | FHIRList[Annotation]
    bodySite: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    specimen: Optional[Reference]
    device: Optional[Reference]
    referenceRange: vitalspanelReferenceRange | FHIRList[vitalspanelReferenceRange]
    hasMember: Reference | FHIRList[Reference]
    derivedFrom: Reference | FHIRList[Reference]
    component: vitalspanelComponent | FHIRList[vitalspanelComponent]
