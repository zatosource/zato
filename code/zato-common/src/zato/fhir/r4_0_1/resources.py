from __future__ import annotations

from typing import Any, Optional

from zato.fhir.base import FHIRResource, FHIRElement, FHIRList
from zato.fhir.r4_0_1.primitives import (
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
)
from zato.fhir.r4_0_1.datatypes import (
    Address,
    Age,
    Annotation,
    Attachment,
    CodeableConcept,
    Coding,
    ContactDetail,
    ContactPoint,
    Contributor,
    Count,
    DataRequirement,
    Distance,
    Dosage,
    Duration,
    ElementDefinition,
    Expression,
    Extension,
    HumanName,
    Identifier,
    MarketingStatus,
    Meta,
    Money,
    Narrative,
    ParameterDefinition,
    Period,
    Population,
    ProdCharacteristic,
    ProductShelfLife,
    Quantity,
    Range,
    Ratio,
    Reference,
    RelatedArtifact,
    SampledData,
    Signature,
    SubstanceAmount,
    Timing,
    TriggerDefinition,
    UsageContext,
)


class AccountCoverage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'coverage': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    coverage: Reference | dict | None
    priority: Optional[PositiveInt] = None


class AccountGuarantor(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'party': 'Reference', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    party: Reference | dict | None
    onHold: Optional[Boolean] = None
    period: Period | dict | None


class Account(FHIRResource):
    _resource_type = "Account"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'subject', 'coverage', 'guarantor'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'subject': 'Reference',
        'servicePeriod': 'Period',
        'coverage': 'AccountCoverage',
        'owner': 'Reference',
        'guarantor': 'AccountGuarantor',
        'partOf': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    type_: CodeableConcept | dict | None
    name: Optional[String] = None
    subject: Reference | FHIRList[Reference] | list | dict
    servicePeriod: Period | dict | None
    coverage: AccountCoverage | FHIRList[AccountCoverage] | list | dict
    owner: Reference | dict | None
    description: Optional[String] = None
    guarantor: AccountGuarantor | FHIRList[AccountGuarantor] | list | dict
    partOf: Reference | dict | None


class ActivityDefinitionParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'role': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    role: CodeableConcept | dict | None


class ActivityDefinitionDynamicValue(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    path: Optional[String] = None
    expression: Expression | dict | None


class ActivityDefinition(FHIRResource):
    _resource_type = "ActivityDefinition"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'contact',
        'useContext',
        'jurisdiction',
        'topic',
        'author',
        'editor',
        'reviewer',
        'endorser',
        'relatedArtifact',
        'library',
        'participant',
        'dosage',
        'bodySite',
        'specimenRequirement',
        'observationRequirement',
        'observationResultRequirement',
        'dynamicValue',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'subjectCodeableConcept': 'CodeableConcept',
        'subjectReference': 'Reference',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'topic': 'CodeableConcept',
        'author': 'ContactDetail',
        'editor': 'ContactDetail',
        'reviewer': 'ContactDetail',
        'endorser': 'ContactDetail',
        'relatedArtifact': 'RelatedArtifact',
        'code': 'CodeableConcept',
        'timingTiming': 'Timing',
        'timingAge': 'Age',
        'timingPeriod': 'Period',
        'timingRange': 'Range',
        'timingDuration': 'Duration',
        'location': 'Reference',
        'participant': 'ActivityDefinitionParticipant',
        'productReference': 'Reference',
        'productCodeableConcept': 'CodeableConcept',
        'quantity': 'Quantity',
        'dosage': 'Dosage',
        'bodySite': 'CodeableConcept',
        'specimenRequirement': 'Reference',
        'observationRequirement': 'Reference',
        'observationResultRequirement': 'Reference',
        'dynamicValue': 'ActivityDefinitionDynamicValue',
    }
    _choice_fields = {
        'product': ['productReference', 'productCodeableConcept'],
        'subject': ['subjectCodeableConcept', 'subjectReference'],
        'timing': ['timingTiming', 'timingDateTime', 'timingAge', 'timingPeriod', 'timingRange', 'timingDuration'],
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    subjectCodeableConcept: CodeableConcept | dict | None
    subjectReference: Reference | dict | None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    topic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    author: ContactDetail | FHIRList[ContactDetail] | list | dict
    editor: ContactDetail | FHIRList[ContactDetail] | list | dict
    reviewer: ContactDetail | FHIRList[ContactDetail] | list | dict
    endorser: ContactDetail | FHIRList[ContactDetail] | list | dict
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    library: Canonical | FHIRList[Canonical] | list | None = None
    kind: Optional[Code] = None
    profile: Optional[Canonical] = None
    code: CodeableConcept | dict | None
    intent: Optional[Code] = None
    priority: Optional[Code] = None
    doNotPerform: Optional[Boolean] = None
    timingTiming: Timing | dict | None
    timingDateTime: Optional[DateTime] = None
    timingAge: Age | dict | None
    timingPeriod: Period | dict | None
    timingRange: Range | dict | None
    timingDuration: Duration | dict | None
    location: Reference | dict | None
    participant: ActivityDefinitionParticipant | FHIRList[ActivityDefinitionParticipant] | list | dict
    productReference: Reference | dict | None
    productCodeableConcept: CodeableConcept | dict | None
    quantity: Quantity | dict | None
    dosage: Dosage | FHIRList[Dosage] | list | dict
    bodySite: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    specimenRequirement: Reference | FHIRList[Reference] | list | dict
    observationRequirement: Reference | FHIRList[Reference] | list | dict
    observationResultRequirement: Reference | FHIRList[Reference] | list | dict
    transform: Optional[Canonical] = None
    dynamicValue: ActivityDefinitionDynamicValue | FHIRList[ActivityDefinitionDynamicValue] | list | dict


class AdverseEventSuspectEntity(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'causality'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'instance': 'Reference', 'causality': 'AdverseEventSuspectEntityCausality'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    instance: Reference | dict | None
    causality: AdverseEventSuspectEntityCausality | FHIRList[AdverseEventSuspectEntityCausality] | list | dict


class AdverseEventSuspectEntityCausality(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'assessment': 'CodeableConcept',
        'author': 'Reference',
        'method': 'CodeableConcept',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    assessment: CodeableConcept | dict | None
    productRelatedness: Optional[String] = None
    author: Reference | dict | None
    method: CodeableConcept | dict | None


class AdverseEvent(FHIRResource):
    _resource_type = "AdverseEvent"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'category',
        'resultingCondition',
        'contributor',
        'suspectEntity',
        'subjectMedicalHistory',
        'referenceDocument',
        'study',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'category': 'CodeableConcept',
        'event': 'CodeableConcept',
        'subject': 'Reference',
        'encounter': 'Reference',
        'resultingCondition': 'Reference',
        'location': 'Reference',
        'seriousness': 'CodeableConcept',
        'severity': 'CodeableConcept',
        'outcome': 'CodeableConcept',
        'recorder': 'Reference',
        'contributor': 'Reference',
        'suspectEntity': 'AdverseEventSuspectEntity',
        'subjectMedicalHistory': 'Reference',
        'referenceDocument': 'Reference',
        'study': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | dict | None
    actuality: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    event: CodeableConcept | dict | None
    subject: Reference | dict | None
    encounter: Reference | dict | None
    date: Optional[DateTime] = None
    detected: Optional[DateTime] = None
    recordedDate: Optional[DateTime] = None
    resultingCondition: Reference | FHIRList[Reference] | list | dict
    location: Reference | dict | None
    seriousness: CodeableConcept | dict | None
    severity: CodeableConcept | dict | None
    outcome: CodeableConcept | dict | None
    recorder: Reference | dict | None
    contributor: Reference | FHIRList[Reference] | list | dict
    suspectEntity: AdverseEventSuspectEntity | FHIRList[AdverseEventSuspectEntity] | list | dict
    subjectMedicalHistory: Reference | FHIRList[Reference] | list | dict
    referenceDocument: Reference | FHIRList[Reference] | list | dict
    study: Reference | FHIRList[Reference] | list | dict


class AllergyIntoleranceReaction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'manifestation', 'note'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'substance': 'CodeableConcept',
        'manifestation': 'CodeableConcept',
        'exposureRoute': 'CodeableConcept',
        'note': 'Annotation',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    substance: CodeableConcept | dict | None
    manifestation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    description: Optional[String] = None
    onset: Optional[DateTime] = None
    severity: Optional[Code] = None
    exposureRoute: CodeableConcept | dict | None
    note: Annotation | FHIRList[Annotation] | list | dict


class AllergyIntolerance(FHIRResource):
    _resource_type = "AllergyIntolerance"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'note', 'reaction'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'clinicalStatus': 'CodeableConcept',
        'verificationStatus': 'CodeableConcept',
        'code': 'CodeableConcept',
        'patient': 'Reference',
        'encounter': 'Reference',
        'onsetAge': 'Age',
        'onsetPeriod': 'Period',
        'onsetRange': 'Range',
        'recorder': 'Reference',
        'asserter': 'Reference',
        'note': 'Annotation',
        'reaction': 'AllergyIntoleranceReaction',
    }
    _choice_fields = {'onset': ['onsetDateTime', 'onsetAge', 'onsetPeriod', 'onsetRange', 'onsetString']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    clinicalStatus: CodeableConcept | dict | None
    verificationStatus: CodeableConcept | dict | None
    type_: Optional[Code] = None
    category: Code | FHIRList[Code] | list | None = None
    criticality: Optional[Code] = None
    code: CodeableConcept | dict | None
    patient: Reference | dict | None
    encounter: Reference | dict | None
    onsetDateTime: Optional[DateTime] = None
    onsetAge: Age | dict | None
    onsetPeriod: Period | dict | None
    onsetRange: Range | dict | None
    onsetString: Optional[String] = None
    recordedDate: Optional[DateTime] = None
    recorder: Reference | dict | None
    asserter: Reference | dict | None
    lastOccurrence: Optional[DateTime] = None
    note: Annotation | FHIRList[Annotation] | list | dict
    reaction: AllergyIntoleranceReaction | FHIRList[AllergyIntoleranceReaction] | list | dict


class AppointmentParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'type_'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'actor': 'Reference', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    actor: Reference | dict | None
    required: Optional[Code] = None
    status: Optional[Code] = None
    period: Period | dict | None


class Appointment(FHIRResource):
    _resource_type = "Appointment"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'serviceCategory',
        'serviceType',
        'specialty',
        'reasonCode',
        'reasonReference',
        'supportingInformation',
        'slot',
        'basedOn',
        'participant',
        'requestedPeriod',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'cancelationReason': 'CodeableConcept',
        'serviceCategory': 'CodeableConcept',
        'serviceType': 'CodeableConcept',
        'specialty': 'CodeableConcept',
        'appointmentType': 'CodeableConcept',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'supportingInformation': 'Reference',
        'slot': 'Reference',
        'basedOn': 'Reference',
        'participant': 'AppointmentParticipant',
        'requestedPeriod': 'Period',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    cancelationReason: CodeableConcept | dict | None
    serviceCategory: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    serviceType: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    specialty: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    appointmentType: CodeableConcept | dict | None
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    priority: Optional[UnsignedInt] = None
    description: Optional[String] = None
    supportingInformation: Reference | FHIRList[Reference] | list | dict
    start: Optional[Instant] = None
    end: Optional[Instant] = None
    minutesDuration: Optional[PositiveInt] = None
    slot: Reference | FHIRList[Reference] | list | dict
    created: Optional[DateTime] = None
    comment: Optional[String] = None
    patientInstruction: Optional[String] = None
    basedOn: Reference | FHIRList[Reference] | list | dict
    participant: AppointmentParticipant | FHIRList[AppointmentParticipant] | list | dict
    requestedPeriod: Period | FHIRList[Period] | list | dict


class AppointmentResponse(FHIRResource):
    _resource_type = "AppointmentResponse"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'participantType'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'appointment': 'Reference',
        'participantType': 'CodeableConcept',
        'actor': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    appointment: Reference | dict | None
    start: Optional[Instant] = None
    end: Optional[Instant] = None
    participantType: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    actor: Reference | dict | None
    participantStatus: Optional[Code] = None
    comment: Optional[String] = None


class AuditEventAgent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'role', 'policy', 'purposeOfUse'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'role': 'CodeableConcept',
        'who': 'Reference',
        'location': 'Reference',
        'media': 'Coding',
        'network': 'AuditEventAgentNetwork',
        'purposeOfUse': 'CodeableConcept',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    role: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    who: Reference | dict | None
    altId: Optional[String] = None
    name: Optional[String] = None
    requestor: Optional[Boolean] = None
    location: Reference | dict | None
    policy: Uri | FHIRList[Uri] | list | None = None
    media: Coding | dict | None
    network: AuditEventAgentNetwork | dict | None
    purposeOfUse: CodeableConcept | FHIRList[CodeableConcept] | list | dict


class AuditEventAgentNetwork(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    address: Optional[String] = None
    type_: Optional[Code] = None


class AuditEventSource(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'type_'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'observer': 'Reference', 'type_': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    site: Optional[String] = None
    observer: Reference | dict | None
    type_: Coding | FHIRList[Coding] | list | dict


class AuditEventEntity(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'securityLabel', 'detail'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'what': 'Reference',
        'type_': 'Coding',
        'role': 'Coding',
        'lifecycle': 'Coding',
        'securityLabel': 'Coding',
        'detail': 'AuditEventEntityDetail',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    what: Reference | dict | None
    type_: Coding | dict | None
    role: Coding | dict | None
    lifecycle: Coding | dict | None
    securityLabel: Coding | FHIRList[Coding] | list | dict
    name: Optional[String] = None
    description: Optional[String] = None
    query: Optional[Base64Binary] = None
    detail: AuditEventEntityDetail | FHIRList[AuditEventEntityDetail] | list | dict


class AuditEventEntityDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}
    _choice_fields = {'value': ['valueString', 'valueBase64Binary']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[String] = None
    valueString: Optional[String] = None
    valueBase64Binary: Optional[Base64Binary] = None


class AuditEvent(FHIRResource):
    _resource_type = "AuditEvent"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'subtype', 'purposeOfEvent', 'agent', 'entity'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'Coding',
        'subtype': 'Coding',
        'period': 'Period',
        'purposeOfEvent': 'CodeableConcept',
        'agent': 'AuditEventAgent',
        'source': 'AuditEventSource',
        'entity': 'AuditEventEntity',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Coding | dict | None
    subtype: Coding | FHIRList[Coding] | list | dict
    action: Optional[Code] = None
    period: Period | dict | None
    recorded: Optional[Instant] = None
    outcome: Optional[Code] = None
    outcomeDesc: Optional[String] = None
    purposeOfEvent: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    agent: AuditEventAgent | FHIRList[AuditEventAgent] | list | dict
    source: AuditEventSource | dict | None
    entity: AuditEventEntity | FHIRList[AuditEventEntity] | list | dict


class Basic(FHIRResource):
    _resource_type = "Basic"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'author': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    created: Optional[Date] = None
    author: Reference | dict | None


class Binary(FHIRResource):
    _resource_type = "Binary"
    _field_types = {'meta': 'Meta', 'securityContext': 'Reference'}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    contentType: Optional[Code] = None
    securityContext: Reference | dict | None
    data: Optional[Base64Binary] = None


class BiologicallyDerivedProductCollection(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'collector': 'Reference', 'source': 'Reference', 'collectedPeriod': 'Period'}
    _choice_fields = {'collected': ['collectedDateTime', 'collectedPeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    collector: Reference | dict | None
    source: Reference | dict | None
    collectedDateTime: Optional[DateTime] = None
    collectedPeriod: Period | dict | None


class BiologicallyDerivedProductProcessing(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'procedure': 'CodeableConcept', 'additive': 'Reference', 'timePeriod': 'Period'}
    _choice_fields = {'time': ['timeDateTime', 'timePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    description: Optional[String] = None
    procedure: CodeableConcept | dict | None
    additive: Reference | dict | None
    timeDateTime: Optional[DateTime] = None
    timePeriod: Period | dict | None


class BiologicallyDerivedProductManipulation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'timePeriod': 'Period'}
    _choice_fields = {'time': ['timeDateTime', 'timePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    description: Optional[String] = None
    timeDateTime: Optional[DateTime] = None
    timePeriod: Period | dict | None


class BiologicallyDerivedProductStorage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'duration': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    description: Optional[String] = None
    temperature: Optional[Decimal] = None
    scale: Optional[Code] = None
    duration: Period | dict | None


class BiologicallyDerivedProduct(FHIRResource):
    _resource_type = "BiologicallyDerivedProduct"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'request', 'parent', 'processing', 'storage'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'productCode': 'CodeableConcept',
        'request': 'Reference',
        'parent': 'Reference',
        'collection': 'BiologicallyDerivedProductCollection',
        'processing': 'BiologicallyDerivedProductProcessing',
        'manipulation': 'BiologicallyDerivedProductManipulation',
        'storage': 'BiologicallyDerivedProductStorage',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    productCategory: Optional[Code] = None
    productCode: CodeableConcept | dict | None
    status: Optional[Code] = None
    request: Reference | FHIRList[Reference] | list | dict
    quantity: Optional[Integer] = None
    parent: Reference | FHIRList[Reference] | list | dict
    collection: BiologicallyDerivedProductCollection | dict | None
    processing: BiologicallyDerivedProductProcessing | FHIRList[BiologicallyDerivedProductProcessing] | list | dict
    manipulation: BiologicallyDerivedProductManipulation | dict | None
    storage: BiologicallyDerivedProductStorage | FHIRList[BiologicallyDerivedProductStorage] | list | dict


class BodyStructure(FHIRResource):
    _resource_type = "BodyStructure"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'locationQualifier', 'image'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'morphology': 'CodeableConcept',
        'location': 'CodeableConcept',
        'locationQualifier': 'CodeableConcept',
        'image': 'Attachment',
        'patient': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    active: Optional[Boolean] = None
    morphology: CodeableConcept | dict | None
    location: CodeableConcept | dict | None
    locationQualifier: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    description: Optional[String] = None
    image: Attachment | FHIRList[Attachment] | list | dict
    patient: Reference | dict | None


class BundleLink(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    relation: Optional[String] = None
    url: Optional[Uri] = None


class BundleEntry(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'link'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'resource': 'Resource',
        'search': 'BundleEntrySearch',
        'request': 'BundleEntryRequest',
        'response': 'BundleEntryResponse',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    link: Any = None
    fullUrl: Optional[Uri] = None
    resource: FHIRResource | dict | None
    search: BundleEntrySearch | dict | None
    request: BundleEntryRequest | dict | None
    response: BundleEntryResponse | dict | None


class BundleEntrySearch(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    mode: Optional[Code] = None
    score: Optional[Decimal] = None


class BundleEntryRequest(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
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
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    status: Optional[String] = None
    location: Optional[Uri] = None
    etag: Optional[String] = None
    lastModified: Optional[Instant] = None
    outcome: FHIRResource | dict | None


class Bundle(FHIRResource):
    _resource_type = "Bundle"
    _list_fields = {'link', 'entry'}
    _field_types = {'meta': 'Meta', 'identifier': 'Identifier', 'link': 'BundleLink', 'entry': 'BundleEntry', 'signature': 'Signature'}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    identifier: Identifier | dict | None
    type_: Optional[Code] = None
    timestamp: Optional[Instant] = None
    total: Optional[UnsignedInt] = None
    link: BundleLink | FHIRList[BundleLink] | list | dict
    entry: BundleEntry | FHIRList[BundleEntry] | list | dict
    signature: Signature | dict | None


class CapabilityStatementSoftware(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[String] = None
    version: Optional[String] = None
    releaseDate: Optional[DateTime] = None


class CapabilityStatementImplementation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'custodian': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    description: Optional[String] = None
    url: Optional[Url] = None
    custodian: Reference | dict | None


class CapabilityStatementRest(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'resource', 'interaction', 'searchParam', 'operation', 'compartment'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'security': 'CapabilityStatementRestSecurity',
        'resource': 'CapabilityStatementRestResource',
        'interaction': 'CapabilityStatementRestInteraction',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    mode: Optional[Code] = None
    documentation: Optional[Markdown] = None
    security: CapabilityStatementRestSecurity | dict | None
    resource: CapabilityStatementRestResource | FHIRList[CapabilityStatementRestResource] | list | dict
    interaction: CapabilityStatementRestInteraction | FHIRList[CapabilityStatementRestInteraction] | list | dict
    searchParam: Any = None
    operation: Any = None
    compartment: Canonical | FHIRList[Canonical] | list | None = None


class CapabilityStatementRestSecurity(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'service'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'service': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    cors: Optional[Boolean] = None
    service: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    description: Optional[Markdown] = None


class CapabilityStatementRestResource(FHIRElement):
    _list_fields = {
        'extension',
        'modifierExtension',
        'supportedProfile',
        'interaction',
        'referencePolicy',
        'searchInclude',
        'searchRevInclude',
        'searchParam',
        'operation',
    }
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'interaction': 'CapabilityStatementRestResourceInteraction',
        'searchParam': 'CapabilityStatementRestResourceSearchParam',
        'operation': 'CapabilityStatementRestResourceOperation',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    profile: Optional[Canonical] = None
    supportedProfile: Canonical | FHIRList[Canonical] | list | None = None
    documentation: Optional[Markdown] = None
    interaction: CapabilityStatementRestResourceInteraction | FHIRList[CapabilityStatementRestResourceInteraction] | list | dict
    versioning: Optional[Code] = None
    readHistory: Optional[Boolean] = None
    updateCreate: Optional[Boolean] = None
    conditionalCreate: Optional[Boolean] = None
    conditionalRead: Optional[Code] = None
    conditionalUpdate: Optional[Boolean] = None
    conditionalDelete: Optional[Code] = None
    referencePolicy: Code | FHIRList[Code] | list | None = None
    searchInclude: String | FHIRList[String] | list | None = None
    searchRevInclude: String | FHIRList[String] | list | None = None
    searchParam: CapabilityStatementRestResourceSearchParam | FHIRList[CapabilityStatementRestResourceSearchParam] | list | dict
    operation: CapabilityStatementRestResourceOperation | FHIRList[CapabilityStatementRestResourceOperation] | list | dict


class CapabilityStatementRestResourceInteraction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    documentation: Optional[Markdown] = None


class CapabilityStatementRestResourceSearchParam(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[String] = None
    definition: Optional[Canonical] = None
    type_: Optional[Code] = None
    documentation: Optional[Markdown] = None


class CapabilityStatementRestResourceOperation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[String] = None
    definition: Optional[Canonical] = None
    documentation: Optional[Markdown] = None


class CapabilityStatementRestInteraction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    documentation: Optional[Markdown] = None


class CapabilityStatementMessaging(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'endpoint', 'supportedMessage'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'endpoint': 'CapabilityStatementMessagingEndpoint',
        'supportedMessage': 'CapabilityStatementMessagingSupportedMessage',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    endpoint: CapabilityStatementMessagingEndpoint | FHIRList[CapabilityStatementMessagingEndpoint] | list | dict
    reliableCache: Optional[UnsignedInt] = None
    documentation: Optional[Markdown] = None
    supportedMessage: CapabilityStatementMessagingSupportedMessage | FHIRList[CapabilityStatementMessagingSupportedMessage] | list | dict


class CapabilityStatementMessagingEndpoint(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'protocol': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    protocol: Coding | dict | None
    address: Optional[Url] = None


class CapabilityStatementMessagingSupportedMessage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    mode: Optional[Code] = None
    definition: Optional[Canonical] = None


class CapabilityStatementDocument(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    mode: Optional[Code] = None
    documentation: Optional[Markdown] = None
    profile: Optional[Canonical] = None


class CapabilityStatement(FHIRResource):
    _resource_type = "CapabilityStatement"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'contact',
        'useContext',
        'jurisdiction',
        'instantiates',
        'imports',
        'format',
        'patchFormat',
        'implementationGuide',
        'rest',
        'messaging',
        'document',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'software': 'CapabilityStatementSoftware',
        'implementation': 'CapabilityStatementImplementation',
        'rest': 'CapabilityStatementRest',
        'messaging': 'CapabilityStatementMessaging',
        'document': 'CapabilityStatementDocument',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    kind: Optional[Code] = None
    instantiates: Canonical | FHIRList[Canonical] | list | None = None
    imports: Canonical | FHIRList[Canonical] | list | None = None
    software: CapabilityStatementSoftware | dict | None
    implementation: CapabilityStatementImplementation | dict | None
    fhirVersion: Optional[Code] = None
    format: Code | FHIRList[Code] | list | None = None
    patchFormat: Code | FHIRList[Code] | list | None = None
    implementationGuide: Canonical | FHIRList[Canonical] | list | None = None
    rest: CapabilityStatementRest | FHIRList[CapabilityStatementRest] | list | dict
    messaging: CapabilityStatementMessaging | FHIRList[CapabilityStatementMessaging] | list | dict
    document: CapabilityStatementDocument | FHIRList[CapabilityStatementDocument] | list | dict


class CarePlanActivity(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'outcomeCodeableConcept', 'outcomeReference', 'progress'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'outcomeCodeableConcept': 'CodeableConcept',
        'outcomeReference': 'Reference',
        'progress': 'Annotation',
        'reference': 'Reference',
        'detail': 'CarePlanActivityDetail',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    outcomeCodeableConcept: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    outcomeReference: Reference | FHIRList[Reference] | list | dict
    progress: Annotation | FHIRList[Annotation] | list | dict
    reference: Reference | dict | None
    detail: CarePlanActivityDetail | dict | None


class CarePlanActivityDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'instantiatesCanonical', 'instantiatesUri', 'reasonCode', 'reasonReference', 'goal', 'performer'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'goal': 'Reference',
        'statusReason': 'CodeableConcept',
        'scheduledTiming': 'Timing',
        'scheduledPeriod': 'Period',
        'location': 'Reference',
        'performer': 'Reference',
        'productCodeableConcept': 'CodeableConcept',
        'productReference': 'Reference',
        'dailyAmount': 'Quantity',
        'quantity': 'Quantity',
    }
    _choice_fields = {'product': ['productCodeableConcept', 'productReference'], 'scheduled': ['scheduledTiming', 'scheduledPeriod', 'scheduledString']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    kind: Optional[Code] = None
    instantiatesCanonical: Canonical | FHIRList[Canonical] | list | None = None
    instantiatesUri: Uri | FHIRList[Uri] | list | None = None
    code: CodeableConcept | dict | None
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    goal: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    statusReason: CodeableConcept | dict | None
    doNotPerform: Optional[Boolean] = None
    scheduledTiming: Timing | dict | None
    scheduledPeriod: Period | dict | None
    scheduledString: Optional[String] = None
    location: Reference | dict | None
    performer: Reference | FHIRList[Reference] | list | dict
    productCodeableConcept: CodeableConcept | dict | None
    productReference: Reference | dict | None
    dailyAmount: Quantity | dict | None
    quantity: Quantity | dict | None
    description: Optional[String] = None


class CarePlan(FHIRResource):
    _resource_type = "CarePlan"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'instantiatesCanonical',
        'instantiatesUri',
        'basedOn',
        'replaces',
        'partOf',
        'category',
        'contributor',
        'careTeam',
        'addresses',
        'supportingInfo',
        'goal',
        'activity',
        'note',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'replaces': 'Reference',
        'partOf': 'Reference',
        'category': 'CodeableConcept',
        'subject': 'Reference',
        'encounter': 'Reference',
        'period': 'Period',
        'author': 'Reference',
        'contributor': 'Reference',
        'careTeam': 'Reference',
        'addresses': 'Reference',
        'supportingInfo': 'Reference',
        'goal': 'Reference',
        'activity': 'CarePlanActivity',
        'note': 'Annotation',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    instantiatesCanonical: Canonical | FHIRList[Canonical] | list | None = None
    instantiatesUri: Uri | FHIRList[Uri] | list | None = None
    basedOn: Reference | FHIRList[Reference] | list | dict
    replaces: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    intent: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    title: Optional[String] = None
    description: Optional[String] = None
    subject: Reference | dict | None
    encounter: Reference | dict | None
    period: Period | dict | None
    created: Optional[DateTime] = None
    author: Reference | dict | None
    contributor: Reference | FHIRList[Reference] | list | dict
    careTeam: Reference | FHIRList[Reference] | list | dict
    addresses: Reference | FHIRList[Reference] | list | dict
    supportingInfo: Reference | FHIRList[Reference] | list | dict
    goal: Reference | FHIRList[Reference] | list | dict
    activity: CarePlanActivity | FHIRList[CarePlanActivity] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict


class CareTeamParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'role'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'role': 'CodeableConcept',
        'member': 'Reference',
        'onBehalfOf': 'Reference',
        'period': 'Period',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    role: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    member: Reference | dict | None
    onBehalfOf: Reference | dict | None
    period: Period | dict | None


class CareTeam(FHIRResource):
    _resource_type = "CareTeam"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'category',
        'participant',
        'reasonCode',
        'reasonReference',
        'managingOrganization',
        'telecom',
        'note',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'category': 'CodeableConcept',
        'subject': 'Reference',
        'encounter': 'Reference',
        'period': 'Period',
        'participant': 'CareTeamParticipant',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'managingOrganization': 'Reference',
        'telecom': 'ContactPoint',
        'note': 'Annotation',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    name: Optional[String] = None
    subject: Reference | dict | None
    encounter: Reference | dict | None
    period: Period | dict | None
    participant: CareTeamParticipant | FHIRList[CareTeamParticipant] | list | dict
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    managingOrganization: Reference | FHIRList[Reference] | list | dict
    telecom: ContactPoint | FHIRList[ContactPoint] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict


class CatalogEntryRelatedEntry(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'item': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    relationtype: Optional[Code] = None
    item: Reference | dict | None


class CatalogEntry(FHIRResource):
    _resource_type = "CatalogEntry"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'additionalIdentifier',
        'classification',
        'additionalCharacteristic',
        'additionalClassification',
        'relatedEntry',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'referencedItem': 'Reference',
        'additionalIdentifier': 'Identifier',
        'classification': 'CodeableConcept',
        'validityPeriod': 'Period',
        'additionalCharacteristic': 'CodeableConcept',
        'additionalClassification': 'CodeableConcept',
        'relatedEntry': 'CatalogEntryRelatedEntry',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    type_: CodeableConcept | dict | None
    orderable: Optional[Boolean] = None
    referencedItem: Reference | dict | None
    additionalIdentifier: Identifier | FHIRList[Identifier] | list | dict
    classification: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    status: Optional[Code] = None
    validityPeriod: Period | dict | None
    validTo: Optional[DateTime] = None
    lastUpdated: Optional[DateTime] = None
    additionalCharacteristic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    additionalClassification: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    relatedEntry: CatalogEntryRelatedEntry | FHIRList[CatalogEntryRelatedEntry] | list | dict


class ChargeItemPerformer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'function': 'CodeableConcept', 'actor': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    function: CodeableConcept | dict | None
    actor: Reference | dict | None


class ChargeItem(FHIRResource):
    _resource_type = "ChargeItem"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'definitionUri',
        'definitionCanonical',
        'partOf',
        'performer',
        'bodysite',
        'reason',
        'service',
        'account',
        'note',
        'supportingInformation',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'partOf': 'Reference',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'context': 'Reference',
        'occurrencePeriod': 'Period',
        'occurrenceTiming': 'Timing',
        'performer': 'ChargeItemPerformer',
        'performingOrganization': 'Reference',
        'requestingOrganization': 'Reference',
        'costCenter': 'Reference',
        'quantity': 'Quantity',
        'bodysite': 'CodeableConcept',
        'priceOverride': 'Money',
        'enterer': 'Reference',
        'reason': 'CodeableConcept',
        'service': 'Reference',
        'productReference': 'Reference',
        'productCodeableConcept': 'CodeableConcept',
        'account': 'Reference',
        'note': 'Annotation',
        'supportingInformation': 'Reference',
    }
    _choice_fields = {'occurrence': ['occurrenceDateTime', 'occurrencePeriod', 'occurrenceTiming'], 'product': ['productReference', 'productCodeableConcept']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    definitionUri: Uri | FHIRList[Uri] | list | None = None
    definitionCanonical: Canonical | FHIRList[Canonical] | list | None = None
    status: Optional[Code] = None
    partOf: Reference | FHIRList[Reference] | list | dict
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    context: Reference | dict | None
    occurrenceDateTime: Optional[DateTime] = None
    occurrencePeriod: Period | dict | None
    occurrenceTiming: Timing | dict | None
    performer: ChargeItemPerformer | FHIRList[ChargeItemPerformer] | list | dict
    performingOrganization: Reference | dict | None
    requestingOrganization: Reference | dict | None
    costCenter: Reference | dict | None
    quantity: Quantity | dict | None
    bodysite: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    factorOverride: Optional[Decimal] = None
    priceOverride: Money | dict | None
    overrideReason: Optional[String] = None
    enterer: Reference | dict | None
    enteredDate: Optional[DateTime] = None
    reason: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    service: Reference | FHIRList[Reference] | list | dict
    productReference: Reference | dict | None
    productCodeableConcept: CodeableConcept | dict | None
    account: Reference | FHIRList[Reference] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    supportingInformation: Reference | FHIRList[Reference] | list | dict


class ChargeItemDefinitionApplicability(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    description: Optional[String] = None
    language: Optional[String] = None
    expression: Optional[String] = None


class ChargeItemDefinitionPropertyGroup(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'applicability', 'priceComponent'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'priceComponent': 'ChargeItemDefinitionPropertyGroupPriceComponent'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    applicability: Any = None
    priceComponent: ChargeItemDefinitionPropertyGroupPriceComponent | FHIRList[ChargeItemDefinitionPropertyGroupPriceComponent] | list | dict


class ChargeItemDefinitionPropertyGroupPriceComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'amount': 'Money'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    code: CodeableConcept | dict | None
    factor: Optional[Decimal] = None
    amount: Money | dict | None


class ChargeItemDefinition(FHIRResource):
    _resource_type = "ChargeItemDefinition"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'derivedFromUri',
        'partOf',
        'replaces',
        'contact',
        'useContext',
        'jurisdiction',
        'instance',
        'applicability',
        'propertyGroup',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'code': 'CodeableConcept',
        'instance': 'Reference',
        'applicability': 'ChargeItemDefinitionApplicability',
        'propertyGroup': 'ChargeItemDefinitionPropertyGroup',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    title: Optional[String] = None
    derivedFromUri: Uri | FHIRList[Uri] | list | None = None
    partOf: Canonical | FHIRList[Canonical] | list | None = None
    replaces: Canonical | FHIRList[Canonical] | list | None = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    code: CodeableConcept | dict | None
    instance: Reference | FHIRList[Reference] | list | dict
    applicability: ChargeItemDefinitionApplicability | FHIRList[ChargeItemDefinitionApplicability] | list | dict
    propertyGroup: ChargeItemDefinitionPropertyGroup | FHIRList[ChargeItemDefinitionPropertyGroup] | list | dict


class ClaimRelated(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'claim': 'Reference',
        'relationship': 'CodeableConcept',
        'reference': 'Identifier',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    claim: Reference | dict | None
    relationship: CodeableConcept | dict | None
    reference: Identifier | dict | None


class ClaimPayee(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'party': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    party: Reference | dict | None


class ClaimCareTeam(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'provider': 'Reference',
        'role': 'CodeableConcept',
        'qualification': 'CodeableConcept',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sequence: Optional[PositiveInt] = None
    provider: Reference | dict | None
    responsible: Optional[Boolean] = None
    role: CodeableConcept | dict | None
    qualification: CodeableConcept | dict | None


class ClaimSupportingInfo(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'timingPeriod': 'Period',
        'valueQuantity': 'Quantity',
        'valueAttachment': 'Attachment',
        'valueReference': 'Reference',
        'reason': 'CodeableConcept',
    }
    _choice_fields = {'timing': ['timingDate', 'timingPeriod'], 'value': ['valueBoolean', 'valueString', 'valueQuantity', 'valueAttachment', 'valueReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sequence: Optional[PositiveInt] = None
    category: CodeableConcept | dict | None
    code: CodeableConcept | dict | None
    timingDate: Optional[Date] = None
    timingPeriod: Period | dict | None
    valueBoolean: Optional[Boolean] = None
    valueString: Optional[String] = None
    valueQuantity: Quantity | dict | None
    valueAttachment: Attachment | dict | None
    valueReference: Reference | dict | None
    reason: CodeableConcept | dict | None


class ClaimDiagnosis(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'type_'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'diagnosisCodeableConcept': 'CodeableConcept',
        'diagnosisReference': 'Reference',
        'type_': 'CodeableConcept',
        'onAdmission': 'CodeableConcept',
        'packageCode': 'CodeableConcept',
    }
    _choice_fields = {'diagnosis': ['diagnosisCodeableConcept', 'diagnosisReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sequence: Optional[PositiveInt] = None
    diagnosisCodeableConcept: CodeableConcept | dict | None
    diagnosisReference: Reference | dict | None
    type_: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    onAdmission: CodeableConcept | dict | None
    packageCode: CodeableConcept | dict | None


class ClaimProcedure(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'type_', 'udi'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'procedureCodeableConcept': 'CodeableConcept',
        'procedureReference': 'Reference',
        'udi': 'Reference',
    }
    _choice_fields = {'procedure': ['procedureCodeableConcept', 'procedureReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sequence: Optional[PositiveInt] = None
    type_: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    date: Optional[DateTime] = None
    procedureCodeableConcept: CodeableConcept | dict | None
    procedureReference: Reference | dict | None
    udi: Reference | FHIRList[Reference] | list | dict


class ClaimInsurance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'preAuthRef'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'coverage': 'Reference',
        'claimResponse': 'Reference',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sequence: Optional[PositiveInt] = None
    focal: Optional[Boolean] = None
    identifier: Identifier | dict | None
    coverage: Reference | dict | None
    businessArrangement: Optional[String] = None
    preAuthRef: String | FHIRList[String] | list | None = None
    claimResponse: Reference | dict | None


class ClaimAccident(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'locationAddress': 'Address',
        'locationReference': 'Reference',
    }
    _choice_fields = {'location': ['locationAddress', 'locationReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    date: Optional[Date] = None
    type_: CodeableConcept | dict | None
    locationAddress: Address | dict | None
    locationReference: Reference | dict | None


class ClaimItem(FHIRElement):
    _list_fields = {
        'extension',
        'modifierExtension',
        'careTeamSequence',
        'diagnosisSequence',
        'procedureSequence',
        'informationSequence',
        'modifier',
        'programCode',
        'udi',
        'subSite',
        'encounter',
        'detail',
    }
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'revenue': 'CodeableConcept',
        'category': 'CodeableConcept',
        'productOrService': 'CodeableConcept',
        'modifier': 'CodeableConcept',
        'programCode': 'CodeableConcept',
        'servicedPeriod': 'Period',
        'locationCodeableConcept': 'CodeableConcept',
        'locationAddress': 'Address',
        'locationReference': 'Reference',
        'quantity': 'Quantity',
        'unitPrice': 'Money',
        'net': 'Money',
        'udi': 'Reference',
        'bodySite': 'CodeableConcept',
        'subSite': 'CodeableConcept',
        'encounter': 'Reference',
        'detail': 'ClaimItemDetail',
    }
    _choice_fields = {'location': ['locationCodeableConcept', 'locationAddress', 'locationReference'], 'serviced': ['servicedDate', 'servicedPeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sequence: Optional[PositiveInt] = None
    careTeamSequence: PositiveInt | FHIRList[PositiveInt] | list | None = None
    diagnosisSequence: PositiveInt | FHIRList[PositiveInt] | list | None = None
    procedureSequence: PositiveInt | FHIRList[PositiveInt] | list | None = None
    informationSequence: PositiveInt | FHIRList[PositiveInt] | list | None = None
    revenue: CodeableConcept | dict | None
    category: CodeableConcept | dict | None
    productOrService: CodeableConcept | dict | None
    modifier: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    programCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    servicedDate: Optional[Date] = None
    servicedPeriod: Period | dict | None
    locationCodeableConcept: CodeableConcept | dict | None
    locationAddress: Address | dict | None
    locationReference: Reference | dict | None
    quantity: Quantity | dict | None
    unitPrice: Money | dict | None
    factor: Optional[Decimal] = None
    net: Money | dict | None
    udi: Reference | FHIRList[Reference] | list | dict
    bodySite: CodeableConcept | dict | None
    subSite: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    encounter: Reference | FHIRList[Reference] | list | dict
    detail: ClaimItemDetail | FHIRList[ClaimItemDetail] | list | dict


class ClaimItemDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'modifier', 'programCode', 'udi', 'subDetail'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'revenue': 'CodeableConcept',
        'category': 'CodeableConcept',
        'productOrService': 'CodeableConcept',
        'modifier': 'CodeableConcept',
        'programCode': 'CodeableConcept',
        'quantity': 'Quantity',
        'unitPrice': 'Money',
        'net': 'Money',
        'udi': 'Reference',
        'subDetail': 'ClaimItemDetailSubDetail',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sequence: Optional[PositiveInt] = None
    revenue: CodeableConcept | dict | None
    category: CodeableConcept | dict | None
    productOrService: CodeableConcept | dict | None
    modifier: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    programCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    quantity: Quantity | dict | None
    unitPrice: Money | dict | None
    factor: Optional[Decimal] = None
    net: Money | dict | None
    udi: Reference | FHIRList[Reference] | list | dict
    subDetail: ClaimItemDetailSubDetail | FHIRList[ClaimItemDetailSubDetail] | list | dict


class ClaimItemDetailSubDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'modifier', 'programCode', 'udi'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'revenue': 'CodeableConcept',
        'category': 'CodeableConcept',
        'productOrService': 'CodeableConcept',
        'modifier': 'CodeableConcept',
        'programCode': 'CodeableConcept',
        'quantity': 'Quantity',
        'unitPrice': 'Money',
        'net': 'Money',
        'udi': 'Reference',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sequence: Optional[PositiveInt] = None
    revenue: CodeableConcept | dict | None
    category: CodeableConcept | dict | None
    productOrService: CodeableConcept | dict | None
    modifier: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    programCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    quantity: Quantity | dict | None
    unitPrice: Money | dict | None
    factor: Optional[Decimal] = None
    net: Money | dict | None
    udi: Reference | FHIRList[Reference] | list | dict


class Claim(FHIRResource):
    _resource_type = "Claim"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'related',
        'careTeam',
        'supportingInfo',
        'diagnosis',
        'procedure',
        'insurance',
        'item',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'subType': 'CodeableConcept',
        'patient': 'Reference',
        'billablePeriod': 'Period',
        'enterer': 'Reference',
        'insurer': 'Reference',
        'provider': 'Reference',
        'priority': 'CodeableConcept',
        'fundsReserve': 'CodeableConcept',
        'related': 'ClaimRelated',
        'prescription': 'Reference',
        'originalPrescription': 'Reference',
        'payee': 'ClaimPayee',
        'referral': 'Reference',
        'facility': 'Reference',
        'careTeam': 'ClaimCareTeam',
        'supportingInfo': 'ClaimSupportingInfo',
        'diagnosis': 'ClaimDiagnosis',
        'procedure': 'ClaimProcedure',
        'insurance': 'ClaimInsurance',
        'accident': 'ClaimAccident',
        'item': 'ClaimItem',
        'total': 'Money',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    type_: CodeableConcept | dict | None
    subType: CodeableConcept | dict | None
    use: Optional[Code] = None
    patient: Reference | dict | None
    billablePeriod: Period | dict | None
    created: Optional[DateTime] = None
    enterer: Reference | dict | None
    insurer: Reference | dict | None
    provider: Reference | dict | None
    priority: CodeableConcept | dict | None
    fundsReserve: CodeableConcept | dict | None
    related: ClaimRelated | FHIRList[ClaimRelated] | list | dict
    prescription: Reference | dict | None
    originalPrescription: Reference | dict | None
    payee: ClaimPayee | dict | None
    referral: Reference | dict | None
    facility: Reference | dict | None
    careTeam: ClaimCareTeam | FHIRList[ClaimCareTeam] | list | dict
    supportingInfo: ClaimSupportingInfo | FHIRList[ClaimSupportingInfo] | list | dict
    diagnosis: ClaimDiagnosis | FHIRList[ClaimDiagnosis] | list | dict
    procedure: ClaimProcedure | FHIRList[ClaimProcedure] | list | dict
    insurance: ClaimInsurance | FHIRList[ClaimInsurance] | list | dict
    accident: ClaimAccident | dict | None
    item: ClaimItem | FHIRList[ClaimItem] | list | dict
    total: Money | dict | None


class ClaimResponseItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'noteNumber', 'adjudication', 'detail'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'adjudication': 'ClaimResponseItemAdjudication',
        'detail': 'ClaimResponseItemDetail',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    itemSequence: Optional[PositiveInt] = None
    noteNumber: PositiveInt | FHIRList[PositiveInt] | list | None = None
    adjudication: ClaimResponseItemAdjudication | FHIRList[ClaimResponseItemAdjudication] | list | dict
    detail: ClaimResponseItemDetail | FHIRList[ClaimResponseItemDetail] | list | dict


class ClaimResponseItemAdjudication(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'category': 'CodeableConcept', 'reason': 'CodeableConcept', 'amount': 'Money'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    category: CodeableConcept | dict | None
    reason: CodeableConcept | dict | None
    amount: Money | dict | None
    value: Optional[Decimal] = None


class ClaimResponseItemDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'noteNumber', 'adjudication', 'subDetail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'subDetail': 'ClaimResponseItemDetailSubDetail'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    detailSequence: Optional[PositiveInt] = None
    noteNumber: PositiveInt | FHIRList[PositiveInt] | list | None = None
    adjudication: Any = None
    subDetail: ClaimResponseItemDetailSubDetail | FHIRList[ClaimResponseItemDetailSubDetail] | list | dict


class ClaimResponseItemDetailSubDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'noteNumber', 'adjudication'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    subDetailSequence: Optional[PositiveInt] = None
    noteNumber: PositiveInt | FHIRList[PositiveInt] | list | None = None
    adjudication: Any = None


class ClaimResponseAddItem(FHIRElement):
    _list_fields = {
        'extension',
        'modifierExtension',
        'itemSequence',
        'detailSequence',
        'subdetailSequence',
        'provider',
        'modifier',
        'programCode',
        'subSite',
        'noteNumber',
        'adjudication',
        'detail',
    }
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'provider': 'Reference',
        'productOrService': 'CodeableConcept',
        'modifier': 'CodeableConcept',
        'programCode': 'CodeableConcept',
        'servicedPeriod': 'Period',
        'locationCodeableConcept': 'CodeableConcept',
        'locationAddress': 'Address',
        'locationReference': 'Reference',
        'quantity': 'Quantity',
        'unitPrice': 'Money',
        'net': 'Money',
        'bodySite': 'CodeableConcept',
        'subSite': 'CodeableConcept',
        'detail': 'ClaimResponseAddItemDetail',
    }
    _choice_fields = {'location': ['locationCodeableConcept', 'locationAddress', 'locationReference'], 'serviced': ['servicedDate', 'servicedPeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    itemSequence: PositiveInt | FHIRList[PositiveInt] | list | None = None
    detailSequence: PositiveInt | FHIRList[PositiveInt] | list | None = None
    subdetailSequence: PositiveInt | FHIRList[PositiveInt] | list | None = None
    provider: Reference | FHIRList[Reference] | list | dict
    productOrService: CodeableConcept | dict | None
    modifier: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    programCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    servicedDate: Optional[Date] = None
    servicedPeriod: Period | dict | None
    locationCodeableConcept: CodeableConcept | dict | None
    locationAddress: Address | dict | None
    locationReference: Reference | dict | None
    quantity: Quantity | dict | None
    unitPrice: Money | dict | None
    factor: Optional[Decimal] = None
    net: Money | dict | None
    bodySite: CodeableConcept | dict | None
    subSite: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    noteNumber: PositiveInt | FHIRList[PositiveInt] | list | None = None
    adjudication: Any = None
    detail: ClaimResponseAddItemDetail | FHIRList[ClaimResponseAddItemDetail] | list | dict


class ClaimResponseAddItemDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'modifier', 'noteNumber', 'adjudication', 'subDetail'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'productOrService': 'CodeableConcept',
        'modifier': 'CodeableConcept',
        'quantity': 'Quantity',
        'unitPrice': 'Money',
        'net': 'Money',
        'subDetail': 'ClaimResponseAddItemDetailSubDetail',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    productOrService: CodeableConcept | dict | None
    modifier: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    quantity: Quantity | dict | None
    unitPrice: Money | dict | None
    factor: Optional[Decimal] = None
    net: Money | dict | None
    noteNumber: PositiveInt | FHIRList[PositiveInt] | list | None = None
    adjudication: Any = None
    subDetail: ClaimResponseAddItemDetailSubDetail | FHIRList[ClaimResponseAddItemDetailSubDetail] | list | dict


class ClaimResponseAddItemDetailSubDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'modifier', 'noteNumber', 'adjudication'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'productOrService': 'CodeableConcept',
        'modifier': 'CodeableConcept',
        'quantity': 'Quantity',
        'unitPrice': 'Money',
        'net': 'Money',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    productOrService: CodeableConcept | dict | None
    modifier: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    quantity: Quantity | dict | None
    unitPrice: Money | dict | None
    factor: Optional[Decimal] = None
    net: Money | dict | None
    noteNumber: PositiveInt | FHIRList[PositiveInt] | list | None = None
    adjudication: Any = None


class ClaimResponseTotal(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'category': 'CodeableConcept', 'amount': 'Money'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    category: CodeableConcept | dict | None
    amount: Money | dict | None


class ClaimResponsePayment(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'adjustment': 'Money',
        'adjustmentReason': 'CodeableConcept',
        'amount': 'Money',
        'identifier': 'Identifier',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    adjustment: Money | dict | None
    adjustmentReason: CodeableConcept | dict | None
    date: Optional[Date] = None
    amount: Money | dict | None
    identifier: Identifier | dict | None


class ClaimResponseProcessNote(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'language': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    number: Optional[PositiveInt] = None
    type_: Optional[Code] = None
    text: Optional[String] = None
    language: CodeableConcept | dict | None


class ClaimResponseInsurance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'coverage': 'Reference', 'claimResponse': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sequence: Optional[PositiveInt] = None
    focal: Optional[Boolean] = None
    coverage: Reference | dict | None
    businessArrangement: Optional[String] = None
    claimResponse: Reference | dict | None


class ClaimResponseError(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    itemSequence: Optional[PositiveInt] = None
    detailSequence: Optional[PositiveInt] = None
    subDetailSequence: Optional[PositiveInt] = None
    code: CodeableConcept | dict | None


class ClaimResponse(FHIRResource):
    _resource_type = "ClaimResponse"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'item',
        'addItem',
        'adjudication',
        'total',
        'processNote',
        'communicationRequest',
        'insurance',
        'error',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'subType': 'CodeableConcept',
        'patient': 'Reference',
        'insurer': 'Reference',
        'requestor': 'Reference',
        'request': 'Reference',
        'preAuthPeriod': 'Period',
        'payeeType': 'CodeableConcept',
        'item': 'ClaimResponseItem',
        'addItem': 'ClaimResponseAddItem',
        'total': 'ClaimResponseTotal',
        'payment': 'ClaimResponsePayment',
        'fundsReserve': 'CodeableConcept',
        'formCode': 'CodeableConcept',
        'form': 'Attachment',
        'processNote': 'ClaimResponseProcessNote',
        'communicationRequest': 'Reference',
        'insurance': 'ClaimResponseInsurance',
        'error': 'ClaimResponseError',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    type_: CodeableConcept | dict | None
    subType: CodeableConcept | dict | None
    use: Optional[Code] = None
    patient: Reference | dict | None
    created: Optional[DateTime] = None
    insurer: Reference | dict | None
    requestor: Reference | dict | None
    request: Reference | dict | None
    outcome: Optional[Code] = None
    disposition: Optional[String] = None
    preAuthRef: Optional[String] = None
    preAuthPeriod: Period | dict | None
    payeeType: CodeableConcept | dict | None
    item: ClaimResponseItem | FHIRList[ClaimResponseItem] | list | dict
    addItem: ClaimResponseAddItem | FHIRList[ClaimResponseAddItem] | list | dict
    adjudication: Any = None
    total: ClaimResponseTotal | FHIRList[ClaimResponseTotal] | list | dict
    payment: ClaimResponsePayment | dict | None
    fundsReserve: CodeableConcept | dict | None
    formCode: CodeableConcept | dict | None
    form: Attachment | dict | None
    processNote: ClaimResponseProcessNote | FHIRList[ClaimResponseProcessNote] | list | dict
    communicationRequest: Reference | FHIRList[Reference] | list | dict
    insurance: ClaimResponseInsurance | FHIRList[ClaimResponseInsurance] | list | dict
    error: ClaimResponseError | FHIRList[ClaimResponseError] | list | dict


class ClinicalImpressionInvestigation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'item'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'item': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    item: Reference | FHIRList[Reference] | list | dict


class ClinicalImpressionFinding(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'itemCodeableConcept': 'CodeableConcept', 'itemReference': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    itemCodeableConcept: CodeableConcept | dict | None
    itemReference: Reference | dict | None
    basis: Optional[String] = None


class ClinicalImpression(FHIRResource):
    _resource_type = "ClinicalImpression"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'problem',
        'investigation',
        'protocol',
        'finding',
        'prognosisCodeableConcept',
        'prognosisReference',
        'supportingInfo',
        'note',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'statusReason': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'encounter': 'Reference',
        'effectivePeriod': 'Period',
        'assessor': 'Reference',
        'previous': 'Reference',
        'problem': 'Reference',
        'investigation': 'ClinicalImpressionInvestigation',
        'finding': 'ClinicalImpressionFinding',
        'prognosisCodeableConcept': 'CodeableConcept',
        'prognosisReference': 'Reference',
        'supportingInfo': 'Reference',
        'note': 'Annotation',
    }
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    statusReason: CodeableConcept | dict | None
    code: CodeableConcept | dict | None
    description: Optional[String] = None
    subject: Reference | dict | None
    encounter: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    date: Optional[DateTime] = None
    assessor: Reference | dict | None
    previous: Reference | dict | None
    problem: Reference | FHIRList[Reference] | list | dict
    investigation: ClinicalImpressionInvestigation | FHIRList[ClinicalImpressionInvestigation] | list | dict
    protocol: Uri | FHIRList[Uri] | list | None = None
    summary: Optional[String] = None
    finding: ClinicalImpressionFinding | FHIRList[ClinicalImpressionFinding] | list | dict
    prognosisCodeableConcept: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    prognosisReference: Reference | FHIRList[Reference] | list | dict
    supportingInfo: Reference | FHIRList[Reference] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict


class CodeSystemFilter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'operator'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    description: Optional[String] = None
    operator: Code | FHIRList[Code] | list | None = None
    value: Optional[String] = None


class CodeSystemProperty(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    uri: Optional[Uri] = None
    description: Optional[String] = None
    type_: Optional[Code] = None


class CodeSystemConcept(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'designation', 'property', 'concept'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'designation': 'CodeSystemConceptDesignation',
        'property': 'CodeSystemConceptProperty',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    display: Optional[String] = None
    definition: Optional[String] = None
    designation: CodeSystemConceptDesignation | FHIRList[CodeSystemConceptDesignation] | list | dict
    property: CodeSystemConceptProperty | FHIRList[CodeSystemConceptProperty] | list | dict
    concept: Any = None


class CodeSystemConceptDesignation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'use': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    language: Optional[Code] = None
    use: Coding | dict | None
    value: Optional[String] = None


class CodeSystemConceptProperty(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'valueCoding': 'Coding'}
    _choice_fields = {'value': ['valueCode', 'valueCoding', 'valueString', 'valueInteger', 'valueBoolean', 'valueDateTime', 'valueDecimal']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    valueCode: Optional[Code] = None
    valueCoding: Coding | dict | None
    valueString: Optional[String] = None
    valueInteger: Optional[Integer] = None
    valueBoolean: Optional[Boolean] = None
    valueDateTime: Optional[DateTime] = None
    valueDecimal: Optional[Decimal] = None


class CodeSystem(FHIRResource):
    _resource_type = "CodeSystem"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'filter', 'property', 'concept'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'filter': 'CodeSystemFilter',
        'property': 'CodeSystemProperty',
        'concept': 'CodeSystemConcept',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
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
    filter: CodeSystemFilter | FHIRList[CodeSystemFilter] | list | dict
    property: CodeSystemProperty | FHIRList[CodeSystemProperty] | list | dict
    concept: CodeSystemConcept | FHIRList[CodeSystemConcept] | list | dict


class CommunicationPayload(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'contentAttachment': 'Attachment', 'contentReference': 'Reference'}
    _choice_fields = {'content': ['contentString', 'contentAttachment', 'contentReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    contentString: Optional[String] = None
    contentAttachment: Attachment | dict | None
    contentReference: Reference | dict | None


class Communication(FHIRResource):
    _resource_type = "Communication"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'instantiatesCanonical',
        'instantiatesUri',
        'basedOn',
        'partOf',
        'inResponseTo',
        'category',
        'medium',
        'about',
        'recipient',
        'reasonCode',
        'reasonReference',
        'payload',
        'note',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'inResponseTo': 'Reference',
        'statusReason': 'CodeableConcept',
        'category': 'CodeableConcept',
        'medium': 'CodeableConcept',
        'subject': 'Reference',
        'topic': 'CodeableConcept',
        'about': 'Reference',
        'encounter': 'Reference',
        'recipient': 'Reference',
        'sender': 'Reference',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'payload': 'CommunicationPayload',
        'note': 'Annotation',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    instantiatesCanonical: Canonical | FHIRList[Canonical] | list | None = None
    instantiatesUri: Uri | FHIRList[Uri] | list | None = None
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    inResponseTo: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    statusReason: CodeableConcept | dict | None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    priority: Optional[Code] = None
    medium: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    subject: Reference | dict | None
    topic: CodeableConcept | dict | None
    about: Reference | FHIRList[Reference] | list | dict
    encounter: Reference | dict | None
    sent: Optional[DateTime] = None
    received: Optional[DateTime] = None
    recipient: Reference | FHIRList[Reference] | list | dict
    sender: Reference | dict | None
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    payload: CommunicationPayload | FHIRList[CommunicationPayload] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict


class CommunicationRequestPayload(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'contentAttachment': 'Attachment', 'contentReference': 'Reference'}
    _choice_fields = {'content': ['contentString', 'contentAttachment', 'contentReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    contentString: Optional[String] = None
    contentAttachment: Attachment | dict | None
    contentReference: Reference | dict | None


class CommunicationRequest(FHIRResource):
    _resource_type = "CommunicationRequest"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'basedOn',
        'replaces',
        'category',
        'medium',
        'about',
        'payload',
        'recipient',
        'reasonCode',
        'reasonReference',
        'note',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'replaces': 'Reference',
        'groupIdentifier': 'Identifier',
        'statusReason': 'CodeableConcept',
        'category': 'CodeableConcept',
        'medium': 'CodeableConcept',
        'subject': 'Reference',
        'about': 'Reference',
        'encounter': 'Reference',
        'payload': 'CommunicationRequestPayload',
        'occurrencePeriod': 'Period',
        'requester': 'Reference',
        'recipient': 'Reference',
        'sender': 'Reference',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'note': 'Annotation',
    }
    _choice_fields = {'occurrence': ['occurrenceDateTime', 'occurrencePeriod']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    replaces: Reference | FHIRList[Reference] | list | dict
    groupIdentifier: Identifier | dict | None
    status: Optional[Code] = None
    statusReason: CodeableConcept | dict | None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    priority: Optional[Code] = None
    doNotPerform: Optional[Boolean] = None
    medium: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    subject: Reference | dict | None
    about: Reference | FHIRList[Reference] | list | dict
    encounter: Reference | dict | None
    payload: CommunicationRequestPayload | FHIRList[CommunicationRequestPayload] | list | dict
    occurrenceDateTime: Optional[DateTime] = None
    occurrencePeriod: Period | dict | None
    authoredOn: Optional[DateTime] = None
    requester: Reference | dict | None
    recipient: Reference | FHIRList[Reference] | list | dict
    sender: Reference | dict | None
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict


class CompartmentDefinitionResource(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'param'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    param: String | FHIRList[String] | list | None = None
    documentation: Optional[String] = None


class CompartmentDefinition(FHIRResource):
    _resource_type = "CompartmentDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'resource'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'resource': 'CompartmentDefinitionResource',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    version: Optional[String] = None
    name: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    purpose: Optional[Markdown] = None
    code: Optional[Code] = None
    search: Optional[Boolean] = None
    resource: CompartmentDefinitionResource | FHIRList[CompartmentDefinitionResource] | list | dict


class CompositionAttester(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'party': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    mode: Optional[Code] = None
    time: Optional[DateTime] = None
    party: Reference | dict | None


class CompositionRelatesTo(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'targetIdentifier': 'Identifier', 'targetReference': 'Reference'}
    _choice_fields = {'target': ['targetIdentifier', 'targetReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    targetIdentifier: Identifier | dict | None
    targetReference: Reference | dict | None


class CompositionEvent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'detail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'period': 'Period', 'detail': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    period: Period | dict | None
    detail: Reference | FHIRList[Reference] | list | dict


class CompositionSection(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'author', 'entry', 'section'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'author': 'Reference',
        'focus': 'Reference',
        'text': 'Narrative',
        'orderedBy': 'CodeableConcept',
        'entry': 'Reference',
        'emptyReason': 'CodeableConcept',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    title: Optional[String] = None
    code: CodeableConcept | dict | None
    author: Reference | FHIRList[Reference] | list | dict
    focus: Reference | dict | None
    text: Narrative | dict | None
    mode: Optional[Code] = None
    orderedBy: CodeableConcept | dict | None
    entry: Reference | FHIRList[Reference] | list | dict
    emptyReason: CodeableConcept | dict | None
    section: Any = None


class Composition(FHIRResource):
    _resource_type = "Composition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'category', 'author', 'attester', 'relatesTo', 'event', 'section'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'category': 'CodeableConcept',
        'subject': 'Reference',
        'encounter': 'Reference',
        'author': 'Reference',
        'attester': 'CompositionAttester',
        'custodian': 'Reference',
        'relatesTo': 'CompositionRelatesTo',
        'event': 'CompositionEvent',
        'section': 'CompositionSection',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | dict | None
    status: Optional[Code] = None
    type_: CodeableConcept | dict | None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    subject: Reference | dict | None
    encounter: Reference | dict | None
    date: Optional[DateTime] = None
    author: Reference | FHIRList[Reference] | list | dict
    title: Optional[String] = None
    confidentiality: Optional[Code] = None
    attester: CompositionAttester | FHIRList[CompositionAttester] | list | dict
    custodian: Reference | dict | None
    relatesTo: CompositionRelatesTo | FHIRList[CompositionRelatesTo] | list | dict
    event: CompositionEvent | FHIRList[CompositionEvent] | list | dict
    section: CompositionSection | FHIRList[CompositionSection] | list | dict


class ConceptMapGroup(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'element'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'element': 'ConceptMapGroupElement', 'unmapped': 'ConceptMapGroupUnmapped'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    source: Optional[Uri] = None
    sourceVersion: Optional[String] = None
    target: Optional[Uri] = None
    targetVersion: Optional[String] = None
    element: ConceptMapGroupElement | FHIRList[ConceptMapGroupElement] | list | dict
    unmapped: ConceptMapGroupUnmapped | dict | None


class ConceptMapGroupElement(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'target'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'target': 'ConceptMapGroupElementTarget'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    display: Optional[String] = None
    target: ConceptMapGroupElementTarget | FHIRList[ConceptMapGroupElementTarget] | list | dict


class ConceptMapGroupElementTarget(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'dependsOn', 'product'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'dependsOn': 'ConceptMapGroupElementTargetDependsOn'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    display: Optional[String] = None
    equivalence: Optional[Code] = None
    comment: Optional[String] = None
    dependsOn: ConceptMapGroupElementTargetDependsOn | FHIRList[ConceptMapGroupElementTargetDependsOn] | list | dict
    product: Any = None


class ConceptMapGroupElementTargetDependsOn(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    property: Optional[Uri] = None
    system: Optional[Canonical] = None
    value: Optional[String] = None
    display: Optional[String] = None


class ConceptMapGroupUnmapped(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    mode: Optional[Code] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    url: Optional[Canonical] = None


class ConceptMap(FHIRResource):
    _resource_type = "ConceptMap"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'group'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'group': 'ConceptMapGroup',
    }
    _choice_fields = {'source': ['sourceUri', 'sourceCanonical'], 'target': ['targetUri', 'targetCanonical']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | dict | None
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    sourceUri: Optional[Uri] = None
    sourceCanonical: Optional[Canonical] = None
    targetUri: Optional[Uri] = None
    targetCanonical: Optional[Canonical] = None
    group: ConceptMapGroup | FHIRList[ConceptMapGroup] | list | dict


class ConditionStage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'assessment'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'summary': 'CodeableConcept',
        'assessment': 'Reference',
        'type_': 'CodeableConcept',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    summary: CodeableConcept | dict | None
    assessment: Reference | FHIRList[Reference] | list | dict
    type_: CodeableConcept | dict | None


class ConditionEvidence(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'detail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'detail': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    detail: Reference | FHIRList[Reference] | list | dict


class Condition(FHIRResource):
    _resource_type = "Condition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'bodySite', 'stage', 'evidence', 'note'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'clinicalStatus': 'CodeableConcept',
        'verificationStatus': 'CodeableConcept',
        'category': 'CodeableConcept',
        'severity': 'CodeableConcept',
        'code': 'CodeableConcept',
        'bodySite': 'CodeableConcept',
        'subject': 'Reference',
        'encounter': 'Reference',
        'onsetAge': 'Age',
        'onsetPeriod': 'Period',
        'onsetRange': 'Range',
        'abatementAge': 'Age',
        'abatementPeriod': 'Period',
        'abatementRange': 'Range',
        'recorder': 'Reference',
        'asserter': 'Reference',
        'stage': 'ConditionStage',
        'evidence': 'ConditionEvidence',
        'note': 'Annotation',
    }
    _choice_fields = {
        'abatement': ['abatementDateTime', 'abatementAge', 'abatementPeriod', 'abatementRange', 'abatementString'],
        'onset': ['onsetDateTime', 'onsetAge', 'onsetPeriod', 'onsetRange', 'onsetString'],
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    clinicalStatus: CodeableConcept | dict | None
    verificationStatus: CodeableConcept | dict | None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    severity: CodeableConcept | dict | None
    code: CodeableConcept | dict | None
    bodySite: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    subject: Reference | dict | None
    encounter: Reference | dict | None
    onsetDateTime: Optional[DateTime] = None
    onsetAge: Age | dict | None
    onsetPeriod: Period | dict | None
    onsetRange: Range | dict | None
    onsetString: Optional[String] = None
    abatementDateTime: Optional[DateTime] = None
    abatementAge: Age | dict | None
    abatementPeriod: Period | dict | None
    abatementRange: Range | dict | None
    abatementString: Optional[String] = None
    recordedDate: Optional[DateTime] = None
    recorder: Reference | dict | None
    asserter: Reference | dict | None
    stage: ConditionStage | FHIRList[ConditionStage] | list | dict
    evidence: ConditionEvidence | FHIRList[ConditionEvidence] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict


class ConsentPolicy(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    authority: Optional[Uri] = None
    uri: Optional[Uri] = None


class ConsentVerification(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'verifiedWith': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    verified: Optional[Boolean] = None
    verifiedWith: Reference | dict | None
    verificationDate: Optional[DateTime] = None


class ConsentProvision(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'actor', 'action', 'securityLabel', 'purpose', 'class_', 'code', 'data', 'provision'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'period': 'Period',
        'actor': 'ConsentProvisionActor',
        'action': 'CodeableConcept',
        'securityLabel': 'Coding',
        'purpose': 'Coding',
        'class_': 'Coding',
        'code': 'CodeableConcept',
        'dataPeriod': 'Period',
        'data': 'ConsentProvisionData',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    period: Period | dict | None
    actor: ConsentProvisionActor | FHIRList[ConsentProvisionActor] | list | dict
    action: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    securityLabel: Coding | FHIRList[Coding] | list | dict
    purpose: Coding | FHIRList[Coding] | list | dict
    class_: Coding | FHIRList[Coding] | list | dict
    code: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    dataPeriod: Period | dict | None
    data: ConsentProvisionData | FHIRList[ConsentProvisionData] | list | dict
    provision: Any = None


class ConsentProvisionActor(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'role': 'CodeableConcept', 'reference': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    role: CodeableConcept | dict | None
    reference: Reference | dict | None


class ConsentProvisionData(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'reference': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    meaning: Optional[Code] = None
    reference: Reference | dict | None


class Consent(FHIRResource):
    _resource_type = "Consent"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'performer', 'organization', 'policy', 'verification'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'scope': 'CodeableConcept',
        'category': 'CodeableConcept',
        'patient': 'Reference',
        'performer': 'Reference',
        'organization': 'Reference',
        'sourceAttachment': 'Attachment',
        'sourceReference': 'Reference',
        'policy': 'ConsentPolicy',
        'policyRule': 'CodeableConcept',
        'verification': 'ConsentVerification',
        'provision': 'ConsentProvision',
    }
    _choice_fields = {'source': ['sourceAttachment', 'sourceReference']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    scope: CodeableConcept | dict | None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    patient: Reference | dict | None
    dateTime: Optional[DateTime] = None
    performer: Reference | FHIRList[Reference] | list | dict
    organization: Reference | FHIRList[Reference] | list | dict
    sourceAttachment: Attachment | dict | None
    sourceReference: Reference | dict | None
    policy: ConsentPolicy | FHIRList[ConsentPolicy] | list | dict
    policyRule: CodeableConcept | dict | None
    verification: ConsentVerification | FHIRList[ConsentVerification] | list | dict
    provision: ConsentProvision | dict | None


class ContractContentDefinition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'subType': 'CodeableConcept',
        'publisher': 'Reference',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    subType: CodeableConcept | dict | None
    publisher: Reference | dict | None
    publicationDate: Optional[DateTime] = None
    publicationStatus: Optional[Code] = None
    copyright: Optional[Markdown] = None


class ContractTerm(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'securityLabel', 'asset', 'action', 'group'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'applies': 'Period',
        'topicCodeableConcept': 'CodeableConcept',
        'topicReference': 'Reference',
        'type_': 'CodeableConcept',
        'subType': 'CodeableConcept',
        'securityLabel': 'ContractTermSecurityLabel',
        'offer': 'ContractTermOffer',
        'asset': 'ContractTermAsset',
        'action': 'ContractTermAction',
    }
    _choice_fields = {'topic': ['topicCodeableConcept', 'topicReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | dict | None
    issued: Optional[DateTime] = None
    applies: Period | dict | None
    topicCodeableConcept: CodeableConcept | dict | None
    topicReference: Reference | dict | None
    type_: CodeableConcept | dict | None
    subType: CodeableConcept | dict | None
    text: Optional[String] = None
    securityLabel: ContractTermSecurityLabel | FHIRList[ContractTermSecurityLabel] | list | dict
    offer: ContractTermOffer | dict | None
    asset: ContractTermAsset | FHIRList[ContractTermAsset] | list | dict
    action: ContractTermAction | FHIRList[ContractTermAction] | list | dict
    group: Any = None


class ContractTermSecurityLabel(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'number', 'category', 'control'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'classification': 'Coding', 'category': 'Coding', 'control': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    number: UnsignedInt | FHIRList[UnsignedInt] | list | None = None
    classification: Coding | dict | None
    category: Coding | FHIRList[Coding] | list | dict
    control: Coding | FHIRList[Coding] | list | dict


class ContractTermOffer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'identifier', 'party', 'decisionMode', 'answer', 'linkId', 'securityLabelNumber'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'party': 'ContractTermOfferParty',
        'topic': 'Reference',
        'type_': 'CodeableConcept',
        'decision': 'CodeableConcept',
        'decisionMode': 'CodeableConcept',
        'answer': 'ContractTermOfferAnswer',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    party: ContractTermOfferParty | FHIRList[ContractTermOfferParty] | list | dict
    topic: Reference | dict | None
    type_: CodeableConcept | dict | None
    decision: CodeableConcept | dict | None
    decisionMode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    answer: ContractTermOfferAnswer | FHIRList[ContractTermOfferAnswer] | list | dict
    text: Optional[String] = None
    linkId: String | FHIRList[String] | list | None = None
    securityLabelNumber: UnsignedInt | FHIRList[UnsignedInt] | list | None = None


class ContractTermOfferParty(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'reference'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'reference': 'Reference', 'role': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    reference: Reference | FHIRList[Reference] | list | dict
    role: CodeableConcept | dict | None


class ContractTermOfferAnswer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'valueAttachment': 'Attachment',
        'valueCoding': 'Coding',
        'valueQuantity': 'Quantity',
        'valueReference': 'Reference',
    }
    _choice_fields = {
        'value': [
            'valueBoolean',
            'valueDecimal',
            'valueInteger',
            'valueDate',
            'valueDateTime',
            'valueTime',
            'valueString',
            'valueUri',
            'valueAttachment',
            'valueCoding',
            'valueQuantity',
            'valueReference',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    valueBoolean: Optional[Boolean] = None
    valueDecimal: Optional[Decimal] = None
    valueInteger: Optional[Integer] = None
    valueDate: Optional[Date] = None
    valueDateTime: Optional[DateTime] = None
    valueTime: Optional[Time] = None
    valueString: Optional[String] = None
    valueUri: Optional[Uri] = None
    valueAttachment: Attachment | dict | None
    valueCoding: Coding | dict | None
    valueQuantity: Quantity | dict | None
    valueReference: Reference | dict | None


class ContractTermAsset(FHIRElement):
    _list_fields = {
        'extension',
        'modifierExtension',
        'type_',
        'typeReference',
        'subtype',
        'context',
        'periodType',
        'period',
        'usePeriod',
        'linkId',
        'answer',
        'securityLabelNumber',
        'valuedItem',
    }
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'scope': 'CodeableConcept',
        'type_': 'CodeableConcept',
        'typeReference': 'Reference',
        'subtype': 'CodeableConcept',
        'relationship': 'Coding',
        'context': 'ContractTermAssetContext',
        'periodType': 'CodeableConcept',
        'period': 'Period',
        'usePeriod': 'Period',
        'valuedItem': 'ContractTermAssetValuedItem',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    scope: CodeableConcept | dict | None
    type_: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    typeReference: Reference | FHIRList[Reference] | list | dict
    subtype: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    relationship: Coding | dict | None
    context: ContractTermAssetContext | FHIRList[ContractTermAssetContext] | list | dict
    condition: Optional[String] = None
    periodType: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    period: Period | FHIRList[Period] | list | dict
    usePeriod: Period | FHIRList[Period] | list | dict
    text: Optional[String] = None
    linkId: String | FHIRList[String] | list | None = None
    answer: Any = None
    securityLabelNumber: UnsignedInt | FHIRList[UnsignedInt] | list | None = None
    valuedItem: ContractTermAssetValuedItem | FHIRList[ContractTermAssetValuedItem] | list | dict


class ContractTermAssetContext(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'reference': 'Reference', 'code': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    reference: Reference | dict | None
    code: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    text: Optional[String] = None


class ContractTermAssetValuedItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'linkId', 'securityLabelNumber'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'entityCodeableConcept': 'CodeableConcept',
        'entityReference': 'Reference',
        'identifier': 'Identifier',
        'quantity': 'Quantity',
        'unitPrice': 'Money',
        'net': 'Money',
        'responsible': 'Reference',
        'recipient': 'Reference',
    }
    _choice_fields = {'entity': ['entityCodeableConcept', 'entityReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    entityCodeableConcept: CodeableConcept | dict | None
    entityReference: Reference | dict | None
    identifier: Identifier | dict | None
    effectiveTime: Optional[DateTime] = None
    quantity: Quantity | dict | None
    unitPrice: Money | dict | None
    factor: Optional[Decimal] = None
    points: Optional[Decimal] = None
    net: Money | dict | None
    payment: Optional[String] = None
    paymentDate: Optional[DateTime] = None
    responsible: Reference | dict | None
    recipient: Reference | dict | None
    linkId: String | FHIRList[String] | list | None = None
    securityLabelNumber: UnsignedInt | FHIRList[UnsignedInt] | list | None = None


class ContractTermAction(FHIRElement):
    _list_fields = {
        'extension',
        'modifierExtension',
        'subject',
        'linkId',
        'contextLinkId',
        'requester',
        'requesterLinkId',
        'performerType',
        'performerLinkId',
        'reasonCode',
        'reasonReference',
        'reason',
        'reasonLinkId',
        'note',
        'securityLabelNumber',
    }
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'subject': 'ContractTermActionSubject',
        'intent': 'CodeableConcept',
        'status': 'CodeableConcept',
        'context': 'Reference',
        'occurrencePeriod': 'Period',
        'occurrenceTiming': 'Timing',
        'requester': 'Reference',
        'performerType': 'CodeableConcept',
        'performerRole': 'CodeableConcept',
        'performer': 'Reference',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'note': 'Annotation',
    }
    _choice_fields = {'occurrence': ['occurrenceDateTime', 'occurrencePeriod', 'occurrenceTiming']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    doNotPerform: Optional[Boolean] = None
    type_: CodeableConcept | dict | None
    subject: ContractTermActionSubject | FHIRList[ContractTermActionSubject] | list | dict
    intent: CodeableConcept | dict | None
    linkId: String | FHIRList[String] | list | None = None
    status: CodeableConcept | dict | None
    context: Reference | dict | None
    contextLinkId: String | FHIRList[String] | list | None = None
    occurrenceDateTime: Optional[DateTime] = None
    occurrencePeriod: Period | dict | None
    occurrenceTiming: Timing | dict | None
    requester: Reference | FHIRList[Reference] | list | dict
    requesterLinkId: String | FHIRList[String] | list | None = None
    performerType: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    performerRole: CodeableConcept | dict | None
    performer: Reference | dict | None
    performerLinkId: String | FHIRList[String] | list | None = None
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    reason: String | FHIRList[String] | list | None = None
    reasonLinkId: String | FHIRList[String] | list | None = None
    note: Annotation | FHIRList[Annotation] | list | dict
    securityLabelNumber: UnsignedInt | FHIRList[UnsignedInt] | list | None = None


class ContractTermActionSubject(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'reference'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'reference': 'Reference', 'role': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    reference: Reference | FHIRList[Reference] | list | dict
    role: CodeableConcept | dict | None


class ContractSigner(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'signature'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'Coding', 'party': 'Reference', 'signature': 'Signature'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Coding | dict | None
    party: Reference | dict | None
    signature: Signature | FHIRList[Signature] | list | dict


class ContractFriendly(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'contentAttachment': 'Attachment', 'contentReference': 'Reference'}
    _choice_fields = {'content': ['contentAttachment', 'contentReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    contentAttachment: Attachment | dict | None
    contentReference: Reference | dict | None


class ContractLegal(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'contentAttachment': 'Attachment', 'contentReference': 'Reference'}
    _choice_fields = {'content': ['contentAttachment', 'contentReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    contentAttachment: Attachment | dict | None
    contentReference: Reference | dict | None


class ContractRule(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'contentAttachment': 'Attachment', 'contentReference': 'Reference'}
    _choice_fields = {'content': ['contentAttachment', 'contentReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    contentAttachment: Attachment | dict | None
    contentReference: Reference | dict | None


class Contract(FHIRResource):
    _resource_type = "Contract"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'subject',
        'authority',
        'domain',
        'site',
        'alias',
        'subType',
        'term',
        'supportingInfo',
        'relevantHistory',
        'signer',
        'friendly',
        'legal',
        'rule',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'legalState': 'CodeableConcept',
        'instantiatesCanonical': 'Reference',
        'contentDerivative': 'CodeableConcept',
        'applies': 'Period',
        'expirationType': 'CodeableConcept',
        'subject': 'Reference',
        'authority': 'Reference',
        'domain': 'Reference',
        'site': 'Reference',
        'author': 'Reference',
        'scope': 'CodeableConcept',
        'topicCodeableConcept': 'CodeableConcept',
        'topicReference': 'Reference',
        'type_': 'CodeableConcept',
        'subType': 'CodeableConcept',
        'contentDefinition': 'ContractContentDefinition',
        'term': 'ContractTerm',
        'supportingInfo': 'Reference',
        'relevantHistory': 'Reference',
        'signer': 'ContractSigner',
        'friendly': 'ContractFriendly',
        'legal': 'ContractLegal',
        'rule': 'ContractRule',
        'legallyBindingAttachment': 'Attachment',
        'legallyBindingReference': 'Reference',
    }
    _choice_fields = {'legallyBinding': ['legallyBindingAttachment', 'legallyBindingReference'], 'topic': ['topicCodeableConcept', 'topicReference']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    url: Optional[Uri] = None
    version: Optional[String] = None
    status: Optional[Code] = None
    legalState: CodeableConcept | dict | None
    instantiatesCanonical: Reference | dict | None
    instantiatesUri: Optional[Uri] = None
    contentDerivative: CodeableConcept | dict | None
    issued: Optional[DateTime] = None
    applies: Period | dict | None
    expirationType: CodeableConcept | dict | None
    subject: Reference | FHIRList[Reference] | list | dict
    authority: Reference | FHIRList[Reference] | list | dict
    domain: Reference | FHIRList[Reference] | list | dict
    site: Reference | FHIRList[Reference] | list | dict
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    alias: String | FHIRList[String] | list | None = None
    author: Reference | dict | None
    scope: CodeableConcept | dict | None
    topicCodeableConcept: CodeableConcept | dict | None
    topicReference: Reference | dict | None
    type_: CodeableConcept | dict | None
    subType: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    contentDefinition: ContractContentDefinition | dict | None
    term: ContractTerm | FHIRList[ContractTerm] | list | dict
    supportingInfo: Reference | FHIRList[Reference] | list | dict
    relevantHistory: Reference | FHIRList[Reference] | list | dict
    signer: ContractSigner | FHIRList[ContractSigner] | list | dict
    friendly: ContractFriendly | FHIRList[ContractFriendly] | list | dict
    legal: ContractLegal | FHIRList[ContractLegal] | list | dict
    rule: ContractRule | FHIRList[ContractRule] | list | dict
    legallyBindingAttachment: Attachment | dict | None
    legallyBindingReference: Reference | dict | None


class CoverageClass(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    value: Optional[String] = None
    name: Optional[String] = None


class CoverageCostToBeneficiary(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'exception'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueMoney': 'Money',
        'exception': 'CoverageCostToBeneficiaryException',
    }
    _choice_fields = {'value': ['valueQuantity', 'valueMoney']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    valueQuantity: Quantity | dict | None
    valueMoney: Money | dict | None
    exception: CoverageCostToBeneficiaryException | FHIRList[CoverageCostToBeneficiaryException] | list | dict


class CoverageCostToBeneficiaryException(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    period: Period | dict | None


class Coverage(FHIRResource):
    _resource_type = "Coverage"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'payor', 'class_', 'costToBeneficiary', 'contract'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'policyHolder': 'Reference',
        'subscriber': 'Reference',
        'beneficiary': 'Reference',
        'relationship': 'CodeableConcept',
        'period': 'Period',
        'payor': 'Reference',
        'class_': 'CoverageClass',
        'costToBeneficiary': 'CoverageCostToBeneficiary',
        'contract': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    type_: CodeableConcept | dict | None
    policyHolder: Reference | dict | None
    subscriber: Reference | dict | None
    subscriberId: Optional[String] = None
    beneficiary: Reference | dict | None
    dependent: Optional[String] = None
    relationship: CodeableConcept | dict | None
    period: Period | dict | None
    payor: Reference | FHIRList[Reference] | list | dict
    class_: CoverageClass | FHIRList[CoverageClass] | list | dict
    order: Optional[PositiveInt] = None
    network: Optional[String] = None
    costToBeneficiary: CoverageCostToBeneficiary | FHIRList[CoverageCostToBeneficiary] | list | dict
    subrogation: Optional[Boolean] = None
    contract: Reference | FHIRList[Reference] | list | dict


class CoverageEligibilityRequestSupportingInfo(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'information': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sequence: Optional[PositiveInt] = None
    information: Reference | dict | None
    appliesToAll: Optional[Boolean] = None


class CoverageEligibilityRequestInsurance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'coverage': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    focal: Optional[Boolean] = None
    coverage: Reference | dict | None
    businessArrangement: Optional[String] = None


class CoverageEligibilityRequestItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'supportingInfoSequence', 'modifier', 'diagnosis', 'detail'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'category': 'CodeableConcept',
        'productOrService': 'CodeableConcept',
        'modifier': 'CodeableConcept',
        'provider': 'Reference',
        'quantity': 'Quantity',
        'unitPrice': 'Money',
        'facility': 'Reference',
        'diagnosis': 'CoverageEligibilityRequestItemDiagnosis',
        'detail': 'Reference',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    supportingInfoSequence: PositiveInt | FHIRList[PositiveInt] | list | None = None
    category: CodeableConcept | dict | None
    productOrService: CodeableConcept | dict | None
    modifier: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    provider: Reference | dict | None
    quantity: Quantity | dict | None
    unitPrice: Money | dict | None
    facility: Reference | dict | None
    diagnosis: CoverageEligibilityRequestItemDiagnosis | FHIRList[CoverageEligibilityRequestItemDiagnosis] | list | dict
    detail: Reference | FHIRList[Reference] | list | dict


class CoverageEligibilityRequestItemDiagnosis(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'diagnosisCodeableConcept': 'CodeableConcept',
        'diagnosisReference': 'Reference',
    }
    _choice_fields = {'diagnosis': ['diagnosisCodeableConcept', 'diagnosisReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    diagnosisCodeableConcept: CodeableConcept | dict | None
    diagnosisReference: Reference | dict | None


class CoverageEligibilityRequest(FHIRResource):
    _resource_type = "CoverageEligibilityRequest"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'purpose', 'supportingInfo', 'insurance', 'item'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'priority': 'CodeableConcept',
        'patient': 'Reference',
        'servicedPeriod': 'Period',
        'enterer': 'Reference',
        'provider': 'Reference',
        'insurer': 'Reference',
        'facility': 'Reference',
        'supportingInfo': 'CoverageEligibilityRequestSupportingInfo',
        'insurance': 'CoverageEligibilityRequestInsurance',
        'item': 'CoverageEligibilityRequestItem',
    }
    _choice_fields = {'serviced': ['servicedDate', 'servicedPeriod']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    priority: CodeableConcept | dict | None
    purpose: Code | FHIRList[Code] | list | None = None
    patient: Reference | dict | None
    servicedDate: Optional[Date] = None
    servicedPeriod: Period | dict | None
    created: Optional[DateTime] = None
    enterer: Reference | dict | None
    provider: Reference | dict | None
    insurer: Reference | dict | None
    facility: Reference | dict | None
    supportingInfo: CoverageEligibilityRequestSupportingInfo | FHIRList[CoverageEligibilityRequestSupportingInfo] | list | dict
    insurance: CoverageEligibilityRequestInsurance | FHIRList[CoverageEligibilityRequestInsurance] | list | dict
    item: CoverageEligibilityRequestItem | FHIRList[CoverageEligibilityRequestItem] | list | dict


class CoverageEligibilityResponseInsurance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'item'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'coverage': 'Reference',
        'benefitPeriod': 'Period',
        'item': 'CoverageEligibilityResponseInsuranceItem',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    coverage: Reference | dict | None
    inforce: Optional[Boolean] = None
    benefitPeriod: Period | dict | None
    item: CoverageEligibilityResponseInsuranceItem | FHIRList[CoverageEligibilityResponseInsuranceItem] | list | dict


class CoverageEligibilityResponseInsuranceItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'modifier', 'benefit', 'authorizationSupporting'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'category': 'CodeableConcept',
        'productOrService': 'CodeableConcept',
        'modifier': 'CodeableConcept',
        'provider': 'Reference',
        'network': 'CodeableConcept',
        'unit': 'CodeableConcept',
        'term': 'CodeableConcept',
        'benefit': 'CoverageEligibilityResponseInsuranceItemBenefit',
        'authorizationSupporting': 'CodeableConcept',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    category: CodeableConcept | dict | None
    productOrService: CodeableConcept | dict | None
    modifier: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    provider: Reference | dict | None
    excluded: Optional[Boolean] = None
    name: Optional[String] = None
    description: Optional[String] = None
    network: CodeableConcept | dict | None
    unit: CodeableConcept | dict | None
    term: CodeableConcept | dict | None
    benefit: CoverageEligibilityResponseInsuranceItemBenefit | FHIRList[CoverageEligibilityResponseInsuranceItemBenefit] | list | dict
    authorizationRequired: Optional[Boolean] = None
    authorizationSupporting: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    authorizationUrl: Optional[Uri] = None


class CoverageEligibilityResponseInsuranceItemBenefit(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'allowedMoney': 'Money', 'usedMoney': 'Money'}
    _choice_fields = {'allowed': ['allowedUnsignedInt', 'allowedString', 'allowedMoney'], 'used': ['usedUnsignedInt', 'usedString', 'usedMoney']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    allowedUnsignedInt: Optional[UnsignedInt] = None
    allowedString: Optional[String] = None
    allowedMoney: Money | dict | None
    usedUnsignedInt: Optional[UnsignedInt] = None
    usedString: Optional[String] = None
    usedMoney: Money | dict | None


class CoverageEligibilityResponseError(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None


class CoverageEligibilityResponse(FHIRResource):
    _resource_type = "CoverageEligibilityResponse"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'purpose', 'insurance', 'error'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'patient': 'Reference',
        'servicedPeriod': 'Period',
        'requestor': 'Reference',
        'request': 'Reference',
        'insurer': 'Reference',
        'insurance': 'CoverageEligibilityResponseInsurance',
        'form': 'CodeableConcept',
        'error': 'CoverageEligibilityResponseError',
    }
    _choice_fields = {'serviced': ['servicedDate', 'servicedPeriod']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    purpose: Code | FHIRList[Code] | list | None = None
    patient: Reference | dict | None
    servicedDate: Optional[Date] = None
    servicedPeriod: Period | dict | None
    created: Optional[DateTime] = None
    requestor: Reference | dict | None
    request: Reference | dict | None
    outcome: Optional[Code] = None
    disposition: Optional[String] = None
    insurer: Reference | dict | None
    insurance: CoverageEligibilityResponseInsurance | FHIRList[CoverageEligibilityResponseInsurance] | list | dict
    preAuthRef: Optional[String] = None
    form: CodeableConcept | dict | None
    error: CoverageEligibilityResponseError | FHIRList[CoverageEligibilityResponseError] | list | dict


class DetectedIssueEvidence(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'detail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'detail': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    detail: Reference | FHIRList[Reference] | list | dict


class DetectedIssueMitigation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'action': 'CodeableConcept', 'author': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    action: CodeableConcept | dict | None
    date: Optional[DateTime] = None
    author: Reference | dict | None


class DetectedIssue(FHIRResource):
    _resource_type = "DetectedIssue"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'implicated', 'evidence', 'mitigation'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'code': 'CodeableConcept',
        'patient': 'Reference',
        'identifiedPeriod': 'Period',
        'author': 'Reference',
        'implicated': 'Reference',
        'evidence': 'DetectedIssueEvidence',
        'mitigation': 'DetectedIssueMitigation',
    }
    _choice_fields = {'identified': ['identifiedDateTime', 'identifiedPeriod']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    code: CodeableConcept | dict | None
    severity: Optional[Code] = None
    patient: Reference | dict | None
    identifiedDateTime: Optional[DateTime] = None
    identifiedPeriod: Period | dict | None
    author: Reference | dict | None
    implicated: Reference | FHIRList[Reference] | list | dict
    evidence: DetectedIssueEvidence | FHIRList[DetectedIssueEvidence] | list | dict
    detail: Optional[String] = None
    reference: Optional[Uri] = None
    mitigation: DetectedIssueMitigation | FHIRList[DetectedIssueMitigation] | list | dict


class DeviceUdiCarrier(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
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
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[String] = None
    type_: Optional[Code] = None


class DeviceSpecialization(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'systemType': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    systemType: CodeableConcept | dict | None
    version: Optional[String] = None


class DeviceVersion(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'component': 'Identifier'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    component: Identifier | dict | None
    value: Optional[String] = None


class DeviceProperty(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'valueQuantity', 'valueCode'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueCode': 'CodeableConcept',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    valueQuantity: Quantity | FHIRList[Quantity] | list | dict
    valueCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict


class Device(FHIRResource):
    _resource_type = "Device"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'udiCarrier',
        'statusReason',
        'deviceName',
        'specialization',
        'version',
        'property',
        'contact',
        'note',
        'safety',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'definition': 'Reference',
        'udiCarrier': 'DeviceUdiCarrier',
        'statusReason': 'CodeableConcept',
        'deviceName': 'DeviceDeviceName',
        'type_': 'CodeableConcept',
        'specialization': 'DeviceSpecialization',
        'version': 'DeviceVersion',
        'property': 'DeviceProperty',
        'patient': 'Reference',
        'owner': 'Reference',
        'contact': 'ContactPoint',
        'location': 'Reference',
        'note': 'Annotation',
        'safety': 'CodeableConcept',
        'parent': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    definition: Reference | dict | None
    udiCarrier: DeviceUdiCarrier | FHIRList[DeviceUdiCarrier] | list | dict
    status: Optional[Code] = None
    statusReason: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    distinctIdentifier: Optional[String] = None
    manufacturer: Optional[String] = None
    manufactureDate: Optional[DateTime] = None
    expirationDate: Optional[DateTime] = None
    lotNumber: Optional[String] = None
    serialNumber: Optional[String] = None
    deviceName: DeviceDeviceName | FHIRList[DeviceDeviceName] | list | dict
    modelNumber: Optional[String] = None
    partNumber: Optional[String] = None
    type_: CodeableConcept | dict | None
    specialization: DeviceSpecialization | FHIRList[DeviceSpecialization] | list | dict
    version: DeviceVersion | FHIRList[DeviceVersion] | list | dict
    property: DeviceProperty | FHIRList[DeviceProperty] | list | dict
    patient: Reference | dict | None
    owner: Reference | dict | None
    contact: ContactPoint | FHIRList[ContactPoint] | list | dict
    location: Reference | dict | None
    url: Optional[Uri] = None
    note: Annotation | FHIRList[Annotation] | list | dict
    safety: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    parent: Reference | dict | None


class DeviceDefinitionUdiDeviceIdentifier(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    deviceIdentifier: Optional[String] = None
    issuer: Optional[Uri] = None
    jurisdiction: Optional[Uri] = None


class DeviceDefinitionDeviceName(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[String] = None
    type_: Optional[Code] = None


class DeviceDefinitionSpecialization(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    systemType: Optional[String] = None
    version: Optional[String] = None


class DeviceDefinitionCapability(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'description'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'description': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    description: CodeableConcept | FHIRList[CodeableConcept] | list | dict


class DeviceDefinitionProperty(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'valueQuantity', 'valueCode'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueCode': 'CodeableConcept',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    valueQuantity: Quantity | FHIRList[Quantity] | list | dict
    valueCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict


class DeviceDefinitionMaterial(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'substance': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    substance: CodeableConcept | dict | None
    alternate: Optional[Boolean] = None
    allergenicIndicator: Optional[Boolean] = None


class DeviceDefinition(FHIRResource):
    _resource_type = "DeviceDefinition"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'udiDeviceIdentifier',
        'deviceName',
        'specialization',
        'version',
        'safety',
        'shelfLifeStorage',
        'languageCode',
        'capability',
        'property',
        'contact',
        'note',
        'material',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'udiDeviceIdentifier': 'DeviceDefinitionUdiDeviceIdentifier',
        'manufacturerReference': 'Reference',
        'deviceName': 'DeviceDefinitionDeviceName',
        'type_': 'CodeableConcept',
        'specialization': 'DeviceDefinitionSpecialization',
        'safety': 'CodeableConcept',
        'shelfLifeStorage': 'ProductShelfLife',
        'physicalCharacteristics': 'ProdCharacteristic',
        'languageCode': 'CodeableConcept',
        'capability': 'DeviceDefinitionCapability',
        'property': 'DeviceDefinitionProperty',
        'owner': 'Reference',
        'contact': 'ContactPoint',
        'note': 'Annotation',
        'quantity': 'Quantity',
        'parentDevice': 'Reference',
        'material': 'DeviceDefinitionMaterial',
    }
    _choice_fields = {'manufacturer': ['manufacturerString', 'manufacturerReference']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    udiDeviceIdentifier: DeviceDefinitionUdiDeviceIdentifier | FHIRList[DeviceDefinitionUdiDeviceIdentifier] | list | dict
    manufacturerString: Optional[String] = None
    manufacturerReference: Reference | dict | None
    deviceName: DeviceDefinitionDeviceName | FHIRList[DeviceDefinitionDeviceName] | list | dict
    modelNumber: Optional[String] = None
    type_: CodeableConcept | dict | None
    specialization: DeviceDefinitionSpecialization | FHIRList[DeviceDefinitionSpecialization] | list | dict
    version: String | FHIRList[String] | list | None = None
    safety: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    shelfLifeStorage: ProductShelfLife | FHIRList[ProductShelfLife] | list | dict
    physicalCharacteristics: ProdCharacteristic | dict | None
    languageCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    capability: DeviceDefinitionCapability | FHIRList[DeviceDefinitionCapability] | list | dict
    property: DeviceDefinitionProperty | FHIRList[DeviceDefinitionProperty] | list | dict
    owner: Reference | dict | None
    contact: ContactPoint | FHIRList[ContactPoint] | list | dict
    url: Optional[Uri] = None
    onlineInformation: Optional[Uri] = None
    note: Annotation | FHIRList[Annotation] | list | dict
    quantity: Quantity | dict | None
    parentDevice: Reference | dict | None
    material: DeviceDefinitionMaterial | FHIRList[DeviceDefinitionMaterial] | list | dict


class DeviceMetricCalibration(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    state: Optional[Code] = None
    time: Optional[Instant] = None


class DeviceMetric(FHIRResource):
    _resource_type = "DeviceMetric"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'calibration'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'unit': 'CodeableConcept',
        'source': 'Reference',
        'parent': 'Reference',
        'measurementPeriod': 'Timing',
        'calibration': 'DeviceMetricCalibration',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    type_: CodeableConcept | dict | None
    unit: CodeableConcept | dict | None
    source: Reference | dict | None
    parent: Reference | dict | None
    operationalStatus: Optional[Code] = None
    color: Optional[Code] = None
    category: Optional[Code] = None
    measurementPeriod: Timing | dict | None
    calibration: DeviceMetricCalibration | FHIRList[DeviceMetricCalibration] | list | dict


class DeviceRequestParameter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueCodeableConcept': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueRange': 'Range',
    }
    _choice_fields = {'value': ['valueCodeableConcept', 'valueQuantity', 'valueRange', 'valueBoolean']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueQuantity: Quantity | dict | None
    valueRange: Range | dict | None
    valueBoolean: Optional[Boolean] = None


class DeviceRequest(FHIRResource):
    _resource_type = "DeviceRequest"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'instantiatesCanonical',
        'instantiatesUri',
        'basedOn',
        'priorRequest',
        'parameter',
        'reasonCode',
        'reasonReference',
        'insurance',
        'supportingInfo',
        'note',
        'relevantHistory',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'priorRequest': 'Reference',
        'groupIdentifier': 'Identifier',
        'codeReference': 'Reference',
        'codeCodeableConcept': 'CodeableConcept',
        'parameter': 'DeviceRequestParameter',
        'subject': 'Reference',
        'encounter': 'Reference',
        'occurrencePeriod': 'Period',
        'occurrenceTiming': 'Timing',
        'requester': 'Reference',
        'performerType': 'CodeableConcept',
        'performer': 'Reference',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'insurance': 'Reference',
        'supportingInfo': 'Reference',
        'note': 'Annotation',
        'relevantHistory': 'Reference',
    }
    _choice_fields = {'code': ['codeReference', 'codeCodeableConcept'], 'occurrence': ['occurrenceDateTime', 'occurrencePeriod', 'occurrenceTiming']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    instantiatesCanonical: Canonical | FHIRList[Canonical] | list | None = None
    instantiatesUri: Uri | FHIRList[Uri] | list | None = None
    basedOn: Reference | FHIRList[Reference] | list | dict
    priorRequest: Reference | FHIRList[Reference] | list | dict
    groupIdentifier: Identifier | dict | None
    status: Optional[Code] = None
    intent: Optional[Code] = None
    priority: Optional[Code] = None
    codeReference: Reference | dict | None
    codeCodeableConcept: CodeableConcept | dict | None
    parameter: DeviceRequestParameter | FHIRList[DeviceRequestParameter] | list | dict
    subject: Reference | dict | None
    encounter: Reference | dict | None
    occurrenceDateTime: Optional[DateTime] = None
    occurrencePeriod: Period | dict | None
    occurrenceTiming: Timing | dict | None
    authoredOn: Optional[DateTime] = None
    requester: Reference | dict | None
    performerType: CodeableConcept | dict | None
    performer: Reference | dict | None
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    insurance: Reference | FHIRList[Reference] | list | dict
    supportingInfo: Reference | FHIRList[Reference] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    relevantHistory: Reference | FHIRList[Reference] | list | dict


class DeviceUseStatement(FHIRResource):
    _resource_type = "DeviceUseStatement"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'derivedFrom', 'reasonCode', 'reasonReference', 'note'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'subject': 'Reference',
        'derivedFrom': 'Reference',
        'timingTiming': 'Timing',
        'timingPeriod': 'Period',
        'source': 'Reference',
        'device': 'Reference',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'bodySite': 'CodeableConcept',
        'note': 'Annotation',
    }
    _choice_fields = {'timing': ['timingTiming', 'timingPeriod', 'timingDateTime']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    subject: Reference | dict | None
    derivedFrom: Reference | FHIRList[Reference] | list | dict
    timingTiming: Timing | dict | None
    timingPeriod: Period | dict | None
    timingDateTime: Optional[DateTime] = None
    recordedOn: Optional[DateTime] = None
    source: Reference | dict | None
    device: Reference | dict | None
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    bodySite: CodeableConcept | dict | None
    note: Annotation | FHIRList[Annotation] | list | dict


class DiagnosticReportMedia(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'link': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    comment: Optional[String] = None
    link: Reference | dict | None


class DiagnosticReport(FHIRResource):
    _resource_type = "DiagnosticReport"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'basedOn',
        'category',
        'performer',
        'resultsInterpreter',
        'specimen',
        'result',
        'imagingStudy',
        'media',
        'conclusionCode',
        'presentedForm',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'encounter': 'Reference',
        'effectivePeriod': 'Period',
        'performer': 'Reference',
        'resultsInterpreter': 'Reference',
        'specimen': 'Reference',
        'result': 'Reference',
        'imagingStudy': 'Reference',
        'media': 'DiagnosticReportMedia',
        'conclusionCode': 'CodeableConcept',
        'presentedForm': 'Attachment',
    }
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    encounter: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference] | list | dict
    resultsInterpreter: Reference | FHIRList[Reference] | list | dict
    specimen: Reference | FHIRList[Reference] | list | dict
    result: Reference | FHIRList[Reference] | list | dict
    imagingStudy: Reference | FHIRList[Reference] | list | dict
    media: DiagnosticReportMedia | FHIRList[DiagnosticReportMedia] | list | dict
    conclusion: Optional[String] = None
    conclusionCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    presentedForm: Attachment | FHIRList[Attachment] | list | dict


class DocumentManifestRelated(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'ref': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | dict | None
    ref: Reference | dict | None


class DocumentManifest(FHIRResource):
    _resource_type = "DocumentManifest"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'author', 'recipient', 'content', 'related'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'masterIdentifier': 'Identifier',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'subject': 'Reference',
        'author': 'Reference',
        'recipient': 'Reference',
        'content': 'Reference',
        'related': 'DocumentManifestRelated',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    masterIdentifier: Identifier | dict | None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    type_: CodeableConcept | dict | None
    subject: Reference | dict | None
    created: Optional[DateTime] = None
    author: Reference | FHIRList[Reference] | list | dict
    recipient: Reference | FHIRList[Reference] | list | dict
    source: Optional[Uri] = None
    description: Optional[String] = None
    content: Reference | FHIRList[Reference] | list | dict
    related: DocumentManifestRelated | FHIRList[DocumentManifestRelated] | list | dict


class DocumentReferenceRelatesTo(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'target': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    target: Reference | dict | None


class DocumentReferenceContent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'attachment': 'Attachment', 'format': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    attachment: Attachment | dict | None
    format: Coding | dict | None


class DocumentReferenceContext(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'encounter', 'event', 'related'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'encounter': 'Reference',
        'event': 'CodeableConcept',
        'period': 'Period',
        'facilityType': 'CodeableConcept',
        'practiceSetting': 'CodeableConcept',
        'sourcePatientInfo': 'Reference',
        'related': 'Reference',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    encounter: Reference | FHIRList[Reference] | list | dict
    event: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    period: Period | dict | None
    facilityType: CodeableConcept | dict | None
    practiceSetting: CodeableConcept | dict | None
    sourcePatientInfo: Reference | dict | None
    related: Reference | FHIRList[Reference] | list | dict


class DocumentReference(FHIRResource):
    _resource_type = "DocumentReference"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'author', 'relatesTo', 'securityLabel', 'content'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'masterIdentifier': 'Identifier',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'category': 'CodeableConcept',
        'subject': 'Reference',
        'author': 'Reference',
        'authenticator': 'Reference',
        'custodian': 'Reference',
        'relatesTo': 'DocumentReferenceRelatesTo',
        'securityLabel': 'CodeableConcept',
        'content': 'DocumentReferenceContent',
        'context': 'DocumentReferenceContext',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    masterIdentifier: Identifier | dict | None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    docStatus: Optional[Code] = None
    type_: CodeableConcept | dict | None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    subject: Reference | dict | None
    date: Optional[Instant] = None
    author: Reference | FHIRList[Reference] | list | dict
    authenticator: Reference | dict | None
    custodian: Reference | dict | None
    relatesTo: DocumentReferenceRelatesTo | FHIRList[DocumentReferenceRelatesTo] | list | dict
    description: Optional[String] = None
    securityLabel: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    content: DocumentReferenceContent | FHIRList[DocumentReferenceContent] | list | dict
    context: DocumentReferenceContext | dict | None


class EffectEvidenceSynthesisSampleSize(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    description: Optional[String] = None
    numberOfStudies: Optional[Integer] = None
    numberOfParticipants: Optional[Integer] = None


class EffectEvidenceSynthesisResultsByExposure(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'variantState': 'CodeableConcept', 'riskEvidenceSynthesis': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    description: Optional[String] = None
    exposureState: Optional[Code] = None
    variantState: CodeableConcept | dict | None
    riskEvidenceSynthesis: Reference | dict | None


class EffectEvidenceSynthesisEffectEstimate(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'precisionEstimate'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'variantState': 'CodeableConcept',
        'unitOfMeasure': 'CodeableConcept',
        'precisionEstimate': 'EffectEvidenceSynthesisEffectEstimatePrecisionEstimate',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    description: Optional[String] = None
    type_: CodeableConcept | dict | None
    variantState: CodeableConcept | dict | None
    value: Optional[Decimal] = None
    unitOfMeasure: CodeableConcept | dict | None
    precisionEstimate: EffectEvidenceSynthesisEffectEstimatePrecisionEstimate | FHIRList[EffectEvidenceSynthesisEffectEstimatePrecisionEstimate] | list | dict


class EffectEvidenceSynthesisEffectEstimatePrecisionEstimate(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    level: Optional[Decimal] = None
    from_: Optional[Decimal] = None
    to: Optional[Decimal] = None


class EffectEvidenceSynthesisCertainty(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'rating', 'note', 'certaintySubcomponent'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'rating': 'CodeableConcept',
        'note': 'Annotation',
        'certaintySubcomponent': 'EffectEvidenceSynthesisCertaintyCertaintySubcomponent',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    rating: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    certaintySubcomponent: EffectEvidenceSynthesisCertaintyCertaintySubcomponent | FHIRList[EffectEvidenceSynthesisCertaintyCertaintySubcomponent] | list | dict


class EffectEvidenceSynthesisCertaintyCertaintySubcomponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'rating', 'note'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'rating': 'CodeableConcept', 'note': 'Annotation'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    rating: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict


class EffectEvidenceSynthesis(FHIRResource):
    _resource_type = "EffectEvidenceSynthesis"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'contact',
        'note',
        'useContext',
        'jurisdiction',
        'topic',
        'author',
        'editor',
        'reviewer',
        'endorser',
        'relatedArtifact',
        'resultsByExposure',
        'effectEstimate',
        'certainty',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'contact': 'ContactDetail',
        'note': 'Annotation',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'topic': 'CodeableConcept',
        'author': 'ContactDetail',
        'editor': 'ContactDetail',
        'reviewer': 'ContactDetail',
        'endorser': 'ContactDetail',
        'relatedArtifact': 'RelatedArtifact',
        'synthesisType': 'CodeableConcept',
        'studyType': 'CodeableConcept',
        'population': 'Reference',
        'exposure': 'Reference',
        'exposureAlternative': 'Reference',
        'outcome': 'Reference',
        'sampleSize': 'EffectEvidenceSynthesisSampleSize',
        'resultsByExposure': 'EffectEvidenceSynthesisResultsByExposure',
        'effectEstimate': 'EffectEvidenceSynthesisEffectEstimate',
        'certainty': 'EffectEvidenceSynthesisCertainty',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    note: Annotation | FHIRList[Annotation] | list | dict
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    topic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    author: ContactDetail | FHIRList[ContactDetail] | list | dict
    editor: ContactDetail | FHIRList[ContactDetail] | list | dict
    reviewer: ContactDetail | FHIRList[ContactDetail] | list | dict
    endorser: ContactDetail | FHIRList[ContactDetail] | list | dict
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    synthesisType: CodeableConcept | dict | None
    studyType: CodeableConcept | dict | None
    population: Reference | dict | None
    exposure: Reference | dict | None
    exposureAlternative: Reference | dict | None
    outcome: Reference | dict | None
    sampleSize: EffectEvidenceSynthesisSampleSize | dict | None
    resultsByExposure: EffectEvidenceSynthesisResultsByExposure | FHIRList[EffectEvidenceSynthesisResultsByExposure] | list | dict
    effectEstimate: EffectEvidenceSynthesisEffectEstimate | FHIRList[EffectEvidenceSynthesisEffectEstimate] | list | dict
    certainty: EffectEvidenceSynthesisCertainty | FHIRList[EffectEvidenceSynthesisCertainty] | list | dict


class EncounterStatusHistory(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    status: Optional[Code] = None
    period: Period | dict | None


class EncounterClassHistory(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'class_': 'Coding', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    class_: Coding | dict | None
    period: Period | dict | None


class EncounterParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'type_'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'period': 'Period', 'individual': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    period: Period | dict | None
    individual: Reference | dict | None


class EncounterDiagnosis(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'condition': 'Reference', 'use': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    condition: Reference | dict | None
    use: CodeableConcept | dict | None
    rank: Optional[PositiveInt] = None


class EncounterHospitalization(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'dietPreference', 'specialCourtesy', 'specialArrangement'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'preAdmissionIdentifier': 'Identifier',
        'origin': 'Reference',
        'admitSource': 'CodeableConcept',
        'reAdmission': 'CodeableConcept',
        'dietPreference': 'CodeableConcept',
        'specialCourtesy': 'CodeableConcept',
        'specialArrangement': 'CodeableConcept',
        'destination': 'Reference',
        'dischargeDisposition': 'CodeableConcept',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    preAdmissionIdentifier: Identifier | dict | None
    origin: Reference | dict | None
    admitSource: CodeableConcept | dict | None
    reAdmission: CodeableConcept | dict | None
    dietPreference: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    specialCourtesy: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    specialArrangement: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    destination: Reference | dict | None
    dischargeDisposition: CodeableConcept | dict | None


class EncounterLocation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'location': 'Reference', 'physicalType': 'CodeableConcept', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    location: Reference | dict | None
    status: Optional[Code] = None
    physicalType: CodeableConcept | dict | None
    period: Period | dict | None


class Encounter(FHIRResource):
    _resource_type = "Encounter"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'statusHistory',
        'classHistory',
        'type_',
        'episodeOfCare',
        'basedOn',
        'participant',
        'appointment',
        'reasonCode',
        'reasonReference',
        'diagnosis',
        'account',
        'location',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'statusHistory': 'EncounterStatusHistory',
        'class_': 'Coding',
        'classHistory': 'EncounterClassHistory',
        'type_': 'CodeableConcept',
        'serviceType': 'CodeableConcept',
        'priority': 'CodeableConcept',
        'subject': 'Reference',
        'episodeOfCare': 'Reference',
        'basedOn': 'Reference',
        'participant': 'EncounterParticipant',
        'appointment': 'Reference',
        'period': 'Period',
        'length': 'Duration',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'diagnosis': 'EncounterDiagnosis',
        'account': 'Reference',
        'hospitalization': 'EncounterHospitalization',
        'location': 'EncounterLocation',
        'serviceProvider': 'Reference',
        'partOf': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    statusHistory: EncounterStatusHistory | FHIRList[EncounterStatusHistory] | list | dict
    class_: Coding | dict | None
    classHistory: EncounterClassHistory | FHIRList[EncounterClassHistory] | list | dict
    type_: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    serviceType: CodeableConcept | dict | None
    priority: CodeableConcept | dict | None
    subject: Reference | dict | None
    episodeOfCare: Reference | FHIRList[Reference] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    participant: EncounterParticipant | FHIRList[EncounterParticipant] | list | dict
    appointment: Reference | FHIRList[Reference] | list | dict
    period: Period | dict | None
    length: Duration | dict | None
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    diagnosis: EncounterDiagnosis | FHIRList[EncounterDiagnosis] | list | dict
    account: Reference | FHIRList[Reference] | list | dict
    hospitalization: EncounterHospitalization | dict | None
    location: EncounterLocation | FHIRList[EncounterLocation] | list | dict
    serviceProvider: Reference | dict | None
    partOf: Reference | dict | None


class Endpoint(FHIRResource):
    _resource_type = "Endpoint"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'payloadType', 'payloadMimeType', 'header'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'connectionType': 'Coding',
        'managingOrganization': 'Reference',
        'contact': 'ContactPoint',
        'period': 'Period',
        'payloadType': 'CodeableConcept',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    connectionType: Coding | dict | None
    name: Optional[String] = None
    managingOrganization: Reference | dict | None
    contact: ContactPoint | FHIRList[ContactPoint] | list | dict
    period: Period | dict | None
    payloadType: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    payloadMimeType: Code | FHIRList[Code] | list | None = None
    address: Optional[Url] = None
    header: String | FHIRList[String] | list | None = None


class EnrollmentRequest(FHIRResource):
    _resource_type = "EnrollmentRequest"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'insurer': 'Reference',
        'provider': 'Reference',
        'candidate': 'Reference',
        'coverage': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    created: Optional[DateTime] = None
    insurer: Reference | dict | None
    provider: Reference | dict | None
    candidate: Reference | dict | None
    coverage: Reference | dict | None


class EnrollmentResponse(FHIRResource):
    _resource_type = "EnrollmentResponse"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'request': 'Reference',
        'organization': 'Reference',
        'requestProvider': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    request: Reference | dict | None
    outcome: Optional[Code] = None
    disposition: Optional[String] = None
    created: Optional[DateTime] = None
    organization: Reference | dict | None
    requestProvider: Reference | dict | None


class EpisodeOfCareStatusHistory(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    status: Optional[Code] = None
    period: Period | dict | None


class EpisodeOfCareDiagnosis(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'condition': 'Reference', 'role': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    condition: Reference | dict | None
    role: CodeableConcept | dict | None
    rank: Optional[PositiveInt] = None


class EpisodeOfCare(FHIRResource):
    _resource_type = "EpisodeOfCare"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'statusHistory', 'type_', 'diagnosis', 'referralRequest', 'team', 'account'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'statusHistory': 'EpisodeOfCareStatusHistory',
        'type_': 'CodeableConcept',
        'diagnosis': 'EpisodeOfCareDiagnosis',
        'patient': 'Reference',
        'managingOrganization': 'Reference',
        'period': 'Period',
        'referralRequest': 'Reference',
        'careManager': 'Reference',
        'team': 'Reference',
        'account': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    statusHistory: EpisodeOfCareStatusHistory | FHIRList[EpisodeOfCareStatusHistory] | list | dict
    type_: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    diagnosis: EpisodeOfCareDiagnosis | FHIRList[EpisodeOfCareDiagnosis] | list | dict
    patient: Reference | dict | None
    managingOrganization: Reference | dict | None
    period: Period | dict | None
    referralRequest: Reference | FHIRList[Reference] | list | dict
    careManager: Reference | dict | None
    team: Reference | FHIRList[Reference] | list | dict
    account: Reference | FHIRList[Reference] | list | dict


class EventDefinition(FHIRResource):
    _resource_type = "EventDefinition"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'contact',
        'useContext',
        'jurisdiction',
        'topic',
        'author',
        'editor',
        'reviewer',
        'endorser',
        'relatedArtifact',
        'trigger',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'subjectCodeableConcept': 'CodeableConcept',
        'subjectReference': 'Reference',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'topic': 'CodeableConcept',
        'author': 'ContactDetail',
        'editor': 'ContactDetail',
        'reviewer': 'ContactDetail',
        'endorser': 'ContactDetail',
        'relatedArtifact': 'RelatedArtifact',
        'trigger': 'TriggerDefinition',
    }
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    subjectCodeableConcept: CodeableConcept | dict | None
    subjectReference: Reference | dict | None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    topic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    author: ContactDetail | FHIRList[ContactDetail] | list | dict
    editor: ContactDetail | FHIRList[ContactDetail] | list | dict
    reviewer: ContactDetail | FHIRList[ContactDetail] | list | dict
    endorser: ContactDetail | FHIRList[ContactDetail] | list | dict
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    trigger: TriggerDefinition | FHIRList[TriggerDefinition] | list | dict


class Evidence(FHIRResource):
    _resource_type = "Evidence"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'contact',
        'note',
        'useContext',
        'jurisdiction',
        'topic',
        'author',
        'editor',
        'reviewer',
        'endorser',
        'relatedArtifact',
        'exposureVariant',
        'outcome',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'contact': 'ContactDetail',
        'note': 'Annotation',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'topic': 'CodeableConcept',
        'author': 'ContactDetail',
        'editor': 'ContactDetail',
        'reviewer': 'ContactDetail',
        'endorser': 'ContactDetail',
        'relatedArtifact': 'RelatedArtifact',
        'exposureBackground': 'Reference',
        'exposureVariant': 'Reference',
        'outcome': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    shortTitle: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    note: Annotation | FHIRList[Annotation] | list | dict
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    topic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    author: ContactDetail | FHIRList[ContactDetail] | list | dict
    editor: ContactDetail | FHIRList[ContactDetail] | list | dict
    reviewer: ContactDetail | FHIRList[ContactDetail] | list | dict
    endorser: ContactDetail | FHIRList[ContactDetail] | list | dict
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    exposureBackground: Reference | dict | None
    exposureVariant: Reference | FHIRList[Reference] | list | dict
    outcome: Reference | FHIRList[Reference] | list | dict


class EvidenceVariableCharacteristic(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'usageContext'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'definitionReference': 'Reference',
        'definitionCodeableConcept': 'CodeableConcept',
        'definitionExpression': 'Expression',
        'definitionDataRequirement': 'DataRequirement',
        'definitionTriggerDefinition': 'TriggerDefinition',
        'usageContext': 'UsageContext',
        'participantEffectivePeriod': 'Period',
        'participantEffectiveDuration': 'Duration',
        'participantEffectiveTiming': 'Timing',
        'timeFromStart': 'Duration',
    }
    _choice_fields = {
        'definition': [
            'definitionReference',
            'definitionCanonical',
            'definitionCodeableConcept',
            'definitionExpression',
            'definitionDataRequirement',
            'definitionTriggerDefinition',
        ],
        'participantEffective': ['participantEffectiveDateTime', 'participantEffectivePeriod', 'participantEffectiveDuration', 'participantEffectiveTiming'],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    description: Optional[String] = None
    definitionReference: Reference | dict | None
    definitionCanonical: Optional[Canonical] = None
    definitionCodeableConcept: CodeableConcept | dict | None
    definitionExpression: Expression | dict | None
    definitionDataRequirement: DataRequirement | dict | None
    definitionTriggerDefinition: TriggerDefinition | dict | None
    usageContext: UsageContext | FHIRList[UsageContext] | list | dict
    exclude: Optional[Boolean] = None
    participantEffectiveDateTime: Optional[DateTime] = None
    participantEffectivePeriod: Period | dict | None
    participantEffectiveDuration: Duration | dict | None
    participantEffectiveTiming: Timing | dict | None
    timeFromStart: Duration | dict | None
    groupMeasure: Optional[Code] = None


class EvidenceVariable(FHIRResource):
    _resource_type = "EvidenceVariable"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'contact',
        'note',
        'useContext',
        'jurisdiction',
        'topic',
        'author',
        'editor',
        'reviewer',
        'endorser',
        'relatedArtifact',
        'characteristic',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'contact': 'ContactDetail',
        'note': 'Annotation',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'topic': 'CodeableConcept',
        'author': 'ContactDetail',
        'editor': 'ContactDetail',
        'reviewer': 'ContactDetail',
        'endorser': 'ContactDetail',
        'relatedArtifact': 'RelatedArtifact',
        'characteristic': 'EvidenceVariableCharacteristic',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    shortTitle: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    note: Annotation | FHIRList[Annotation] | list | dict
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    topic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    author: ContactDetail | FHIRList[ContactDetail] | list | dict
    editor: ContactDetail | FHIRList[ContactDetail] | list | dict
    reviewer: ContactDetail | FHIRList[ContactDetail] | list | dict
    endorser: ContactDetail | FHIRList[ContactDetail] | list | dict
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    type_: Optional[Code] = None
    characteristic: EvidenceVariableCharacteristic | FHIRList[EvidenceVariableCharacteristic] | list | dict


class ExampleScenarioActor(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    actorId: Optional[String] = None
    type_: Optional[Code] = None
    name: Optional[String] = None
    description: Optional[Markdown] = None


class ExampleScenarioInstance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'version', 'containedInstance'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'version': 'ExampleScenarioInstanceVersion',
        'containedInstance': 'ExampleScenarioInstanceContainedInstance',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    resourceId: Optional[String] = None
    resourceType: Optional[Code] = None
    name: Optional[String] = None
    description: Optional[Markdown] = None
    version: ExampleScenarioInstanceVersion | FHIRList[ExampleScenarioInstanceVersion] | list | dict
    containedInstance: ExampleScenarioInstanceContainedInstance | FHIRList[ExampleScenarioInstanceContainedInstance] | list | dict


class ExampleScenarioInstanceVersion(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    versionId: Optional[String] = None
    description: Optional[Markdown] = None


class ExampleScenarioInstanceContainedInstance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    resourceId: Optional[String] = None
    versionId: Optional[String] = None


class ExampleScenarioProcess(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'step'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'step': 'ExampleScenarioProcessStep'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    title: Optional[String] = None
    description: Optional[Markdown] = None
    preConditions: Optional[Markdown] = None
    postConditions: Optional[Markdown] = None
    step: ExampleScenarioProcessStep | FHIRList[ExampleScenarioProcessStep] | list | dict


class ExampleScenarioProcessStep(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'process', 'alternative'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'operation': 'ExampleScenarioProcessStepOperation',
        'alternative': 'ExampleScenarioProcessStepAlternative',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    process: Any = None
    pause: Optional[Boolean] = None
    operation: ExampleScenarioProcessStepOperation | dict | None
    alternative: ExampleScenarioProcessStepAlternative | FHIRList[ExampleScenarioProcessStepAlternative] | list | dict


class ExampleScenarioProcessStepOperation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
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
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    title: Optional[String] = None
    description: Optional[Markdown] = None
    step: Any = None


class ExampleScenario(FHIRResource):
    _resource_type = "ExampleScenario"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'contact',
        'useContext',
        'jurisdiction',
        'actor',
        'instance',
        'process',
        'workflow',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'actor': 'ExampleScenarioActor',
        'instance': 'ExampleScenarioInstance',
        'process': 'ExampleScenarioProcess',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    copyright: Optional[Markdown] = None
    purpose: Optional[Markdown] = None
    actor: ExampleScenarioActor | FHIRList[ExampleScenarioActor] | list | dict
    instance: ExampleScenarioInstance | FHIRList[ExampleScenarioInstance] | list | dict
    process: ExampleScenarioProcess | FHIRList[ExampleScenarioProcess] | list | dict
    workflow: Canonical | FHIRList[Canonical] | list | None = None


class ExplanationOfBenefitRelated(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'claim': 'Reference',
        'relationship': 'CodeableConcept',
        'reference': 'Identifier',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    claim: Reference | dict | None
    relationship: CodeableConcept | dict | None
    reference: Identifier | dict | None


class ExplanationOfBenefitPayee(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'party': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    party: Reference | dict | None


class ExplanationOfBenefitCareTeam(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'provider': 'Reference',
        'role': 'CodeableConcept',
        'qualification': 'CodeableConcept',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sequence: Optional[PositiveInt] = None
    provider: Reference | dict | None
    responsible: Optional[Boolean] = None
    role: CodeableConcept | dict | None
    qualification: CodeableConcept | dict | None


class ExplanationOfBenefitSupportingInfo(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'timingPeriod': 'Period',
        'valueQuantity': 'Quantity',
        'valueAttachment': 'Attachment',
        'valueReference': 'Reference',
        'reason': 'Coding',
    }
    _choice_fields = {'timing': ['timingDate', 'timingPeriod'], 'value': ['valueBoolean', 'valueString', 'valueQuantity', 'valueAttachment', 'valueReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sequence: Optional[PositiveInt] = None
    category: CodeableConcept | dict | None
    code: CodeableConcept | dict | None
    timingDate: Optional[Date] = None
    timingPeriod: Period | dict | None
    valueBoolean: Optional[Boolean] = None
    valueString: Optional[String] = None
    valueQuantity: Quantity | dict | None
    valueAttachment: Attachment | dict | None
    valueReference: Reference | dict | None
    reason: Coding | dict | None


class ExplanationOfBenefitDiagnosis(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'type_'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'diagnosisCodeableConcept': 'CodeableConcept',
        'diagnosisReference': 'Reference',
        'type_': 'CodeableConcept',
        'onAdmission': 'CodeableConcept',
        'packageCode': 'CodeableConcept',
    }
    _choice_fields = {'diagnosis': ['diagnosisCodeableConcept', 'diagnosisReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sequence: Optional[PositiveInt] = None
    diagnosisCodeableConcept: CodeableConcept | dict | None
    diagnosisReference: Reference | dict | None
    type_: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    onAdmission: CodeableConcept | dict | None
    packageCode: CodeableConcept | dict | None


class ExplanationOfBenefitProcedure(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'type_', 'udi'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'procedureCodeableConcept': 'CodeableConcept',
        'procedureReference': 'Reference',
        'udi': 'Reference',
    }
    _choice_fields = {'procedure': ['procedureCodeableConcept', 'procedureReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sequence: Optional[PositiveInt] = None
    type_: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    date: Optional[DateTime] = None
    procedureCodeableConcept: CodeableConcept | dict | None
    procedureReference: Reference | dict | None
    udi: Reference | FHIRList[Reference] | list | dict


class ExplanationOfBenefitInsurance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'preAuthRef'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'coverage': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    focal: Optional[Boolean] = None
    coverage: Reference | dict | None
    preAuthRef: String | FHIRList[String] | list | None = None


class ExplanationOfBenefitAccident(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'locationAddress': 'Address',
        'locationReference': 'Reference',
    }
    _choice_fields = {'location': ['locationAddress', 'locationReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    date: Optional[Date] = None
    type_: CodeableConcept | dict | None
    locationAddress: Address | dict | None
    locationReference: Reference | dict | None


class ExplanationOfBenefitItem(FHIRElement):
    _list_fields = {
        'extension',
        'modifierExtension',
        'careTeamSequence',
        'diagnosisSequence',
        'procedureSequence',
        'informationSequence',
        'modifier',
        'programCode',
        'udi',
        'subSite',
        'encounter',
        'noteNumber',
        'adjudication',
        'detail',
    }
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'revenue': 'CodeableConcept',
        'category': 'CodeableConcept',
        'productOrService': 'CodeableConcept',
        'modifier': 'CodeableConcept',
        'programCode': 'CodeableConcept',
        'servicedPeriod': 'Period',
        'locationCodeableConcept': 'CodeableConcept',
        'locationAddress': 'Address',
        'locationReference': 'Reference',
        'quantity': 'Quantity',
        'unitPrice': 'Money',
        'net': 'Money',
        'udi': 'Reference',
        'bodySite': 'CodeableConcept',
        'subSite': 'CodeableConcept',
        'encounter': 'Reference',
        'adjudication': 'ExplanationOfBenefitItemAdjudication',
        'detail': 'ExplanationOfBenefitItemDetail',
    }
    _choice_fields = {'location': ['locationCodeableConcept', 'locationAddress', 'locationReference'], 'serviced': ['servicedDate', 'servicedPeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sequence: Optional[PositiveInt] = None
    careTeamSequence: PositiveInt | FHIRList[PositiveInt] | list | None = None
    diagnosisSequence: PositiveInt | FHIRList[PositiveInt] | list | None = None
    procedureSequence: PositiveInt | FHIRList[PositiveInt] | list | None = None
    informationSequence: PositiveInt | FHIRList[PositiveInt] | list | None = None
    revenue: CodeableConcept | dict | None
    category: CodeableConcept | dict | None
    productOrService: CodeableConcept | dict | None
    modifier: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    programCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    servicedDate: Optional[Date] = None
    servicedPeriod: Period | dict | None
    locationCodeableConcept: CodeableConcept | dict | None
    locationAddress: Address | dict | None
    locationReference: Reference | dict | None
    quantity: Quantity | dict | None
    unitPrice: Money | dict | None
    factor: Optional[Decimal] = None
    net: Money | dict | None
    udi: Reference | FHIRList[Reference] | list | dict
    bodySite: CodeableConcept | dict | None
    subSite: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    encounter: Reference | FHIRList[Reference] | list | dict
    noteNumber: PositiveInt | FHIRList[PositiveInt] | list | None = None
    adjudication: ExplanationOfBenefitItemAdjudication | FHIRList[ExplanationOfBenefitItemAdjudication] | list | dict
    detail: ExplanationOfBenefitItemDetail | FHIRList[ExplanationOfBenefitItemDetail] | list | dict


class ExplanationOfBenefitItemAdjudication(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'category': 'CodeableConcept', 'reason': 'CodeableConcept', 'amount': 'Money'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    category: CodeableConcept | dict | None
    reason: CodeableConcept | dict | None
    amount: Money | dict | None
    value: Optional[Decimal] = None


class ExplanationOfBenefitItemDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'modifier', 'programCode', 'udi', 'noteNumber', 'adjudication', 'subDetail'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'revenue': 'CodeableConcept',
        'category': 'CodeableConcept',
        'productOrService': 'CodeableConcept',
        'modifier': 'CodeableConcept',
        'programCode': 'CodeableConcept',
        'quantity': 'Quantity',
        'unitPrice': 'Money',
        'net': 'Money',
        'udi': 'Reference',
        'subDetail': 'ExplanationOfBenefitItemDetailSubDetail',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sequence: Optional[PositiveInt] = None
    revenue: CodeableConcept | dict | None
    category: CodeableConcept | dict | None
    productOrService: CodeableConcept | dict | None
    modifier: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    programCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    quantity: Quantity | dict | None
    unitPrice: Money | dict | None
    factor: Optional[Decimal] = None
    net: Money | dict | None
    udi: Reference | FHIRList[Reference] | list | dict
    noteNumber: PositiveInt | FHIRList[PositiveInt] | list | None = None
    adjudication: Any = None
    subDetail: ExplanationOfBenefitItemDetailSubDetail | FHIRList[ExplanationOfBenefitItemDetailSubDetail] | list | dict


class ExplanationOfBenefitItemDetailSubDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'modifier', 'programCode', 'udi', 'noteNumber', 'adjudication'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'revenue': 'CodeableConcept',
        'category': 'CodeableConcept',
        'productOrService': 'CodeableConcept',
        'modifier': 'CodeableConcept',
        'programCode': 'CodeableConcept',
        'quantity': 'Quantity',
        'unitPrice': 'Money',
        'net': 'Money',
        'udi': 'Reference',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sequence: Optional[PositiveInt] = None
    revenue: CodeableConcept | dict | None
    category: CodeableConcept | dict | None
    productOrService: CodeableConcept | dict | None
    modifier: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    programCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    quantity: Quantity | dict | None
    unitPrice: Money | dict | None
    factor: Optional[Decimal] = None
    net: Money | dict | None
    udi: Reference | FHIRList[Reference] | list | dict
    noteNumber: PositiveInt | FHIRList[PositiveInt] | list | None = None
    adjudication: Any = None


class ExplanationOfBenefitAddItem(FHIRElement):
    _list_fields = {
        'extension',
        'modifierExtension',
        'itemSequence',
        'detailSequence',
        'subDetailSequence',
        'provider',
        'modifier',
        'programCode',
        'subSite',
        'noteNumber',
        'adjudication',
        'detail',
    }
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'provider': 'Reference',
        'productOrService': 'CodeableConcept',
        'modifier': 'CodeableConcept',
        'programCode': 'CodeableConcept',
        'servicedPeriod': 'Period',
        'locationCodeableConcept': 'CodeableConcept',
        'locationAddress': 'Address',
        'locationReference': 'Reference',
        'quantity': 'Quantity',
        'unitPrice': 'Money',
        'net': 'Money',
        'bodySite': 'CodeableConcept',
        'subSite': 'CodeableConcept',
        'detail': 'ExplanationOfBenefitAddItemDetail',
    }
    _choice_fields = {'location': ['locationCodeableConcept', 'locationAddress', 'locationReference'], 'serviced': ['servicedDate', 'servicedPeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    itemSequence: PositiveInt | FHIRList[PositiveInt] | list | None = None
    detailSequence: PositiveInt | FHIRList[PositiveInt] | list | None = None
    subDetailSequence: PositiveInt | FHIRList[PositiveInt] | list | None = None
    provider: Reference | FHIRList[Reference] | list | dict
    productOrService: CodeableConcept | dict | None
    modifier: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    programCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    servicedDate: Optional[Date] = None
    servicedPeriod: Period | dict | None
    locationCodeableConcept: CodeableConcept | dict | None
    locationAddress: Address | dict | None
    locationReference: Reference | dict | None
    quantity: Quantity | dict | None
    unitPrice: Money | dict | None
    factor: Optional[Decimal] = None
    net: Money | dict | None
    bodySite: CodeableConcept | dict | None
    subSite: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    noteNumber: PositiveInt | FHIRList[PositiveInt] | list | None = None
    adjudication: Any = None
    detail: ExplanationOfBenefitAddItemDetail | FHIRList[ExplanationOfBenefitAddItemDetail] | list | dict


class ExplanationOfBenefitAddItemDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'modifier', 'noteNumber', 'adjudication', 'subDetail'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'productOrService': 'CodeableConcept',
        'modifier': 'CodeableConcept',
        'quantity': 'Quantity',
        'unitPrice': 'Money',
        'net': 'Money',
        'subDetail': 'ExplanationOfBenefitAddItemDetailSubDetail',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    productOrService: CodeableConcept | dict | None
    modifier: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    quantity: Quantity | dict | None
    unitPrice: Money | dict | None
    factor: Optional[Decimal] = None
    net: Money | dict | None
    noteNumber: PositiveInt | FHIRList[PositiveInt] | list | None = None
    adjudication: Any = None
    subDetail: ExplanationOfBenefitAddItemDetailSubDetail | FHIRList[ExplanationOfBenefitAddItemDetailSubDetail] | list | dict


class ExplanationOfBenefitAddItemDetailSubDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'modifier', 'noteNumber', 'adjudication'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'productOrService': 'CodeableConcept',
        'modifier': 'CodeableConcept',
        'quantity': 'Quantity',
        'unitPrice': 'Money',
        'net': 'Money',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    productOrService: CodeableConcept | dict | None
    modifier: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    quantity: Quantity | dict | None
    unitPrice: Money | dict | None
    factor: Optional[Decimal] = None
    net: Money | dict | None
    noteNumber: PositiveInt | FHIRList[PositiveInt] | list | None = None
    adjudication: Any = None


class ExplanationOfBenefitTotal(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'category': 'CodeableConcept', 'amount': 'Money'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    category: CodeableConcept | dict | None
    amount: Money | dict | None


class ExplanationOfBenefitPayment(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'adjustment': 'Money',
        'adjustmentReason': 'CodeableConcept',
        'amount': 'Money',
        'identifier': 'Identifier',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    adjustment: Money | dict | None
    adjustmentReason: CodeableConcept | dict | None
    date: Optional[Date] = None
    amount: Money | dict | None
    identifier: Identifier | dict | None


class ExplanationOfBenefitProcessNote(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'language': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    number: Optional[PositiveInt] = None
    type_: Optional[Code] = None
    text: Optional[String] = None
    language: CodeableConcept | dict | None


class ExplanationOfBenefitBenefitBalance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'financial'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'category': 'CodeableConcept',
        'network': 'CodeableConcept',
        'unit': 'CodeableConcept',
        'term': 'CodeableConcept',
        'financial': 'ExplanationOfBenefitBenefitBalanceFinancial',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    category: CodeableConcept | dict | None
    excluded: Optional[Boolean] = None
    name: Optional[String] = None
    description: Optional[String] = None
    network: CodeableConcept | dict | None
    unit: CodeableConcept | dict | None
    term: CodeableConcept | dict | None
    financial: ExplanationOfBenefitBenefitBalanceFinancial | FHIRList[ExplanationOfBenefitBenefitBalanceFinancial] | list | dict


class ExplanationOfBenefitBenefitBalanceFinancial(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'allowedMoney': 'Money', 'usedMoney': 'Money'}
    _choice_fields = {'allowed': ['allowedUnsignedInt', 'allowedString', 'allowedMoney'], 'used': ['usedUnsignedInt', 'usedMoney']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    allowedUnsignedInt: Optional[UnsignedInt] = None
    allowedString: Optional[String] = None
    allowedMoney: Money | dict | None
    usedUnsignedInt: Optional[UnsignedInt] = None
    usedMoney: Money | dict | None


class ExplanationOfBenefit(FHIRResource):
    _resource_type = "ExplanationOfBenefit"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'related',
        'preAuthRef',
        'preAuthRefPeriod',
        'careTeam',
        'supportingInfo',
        'diagnosis',
        'procedure',
        'insurance',
        'item',
        'addItem',
        'adjudication',
        'total',
        'processNote',
        'benefitBalance',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'subType': 'CodeableConcept',
        'patient': 'Reference',
        'billablePeriod': 'Period',
        'enterer': 'Reference',
        'insurer': 'Reference',
        'provider': 'Reference',
        'priority': 'CodeableConcept',
        'fundsReserveRequested': 'CodeableConcept',
        'fundsReserve': 'CodeableConcept',
        'related': 'ExplanationOfBenefitRelated',
        'prescription': 'Reference',
        'originalPrescription': 'Reference',
        'payee': 'ExplanationOfBenefitPayee',
        'referral': 'Reference',
        'facility': 'Reference',
        'claim': 'Reference',
        'claimResponse': 'Reference',
        'preAuthRefPeriod': 'Period',
        'careTeam': 'ExplanationOfBenefitCareTeam',
        'supportingInfo': 'ExplanationOfBenefitSupportingInfo',
        'diagnosis': 'ExplanationOfBenefitDiagnosis',
        'procedure': 'ExplanationOfBenefitProcedure',
        'insurance': 'ExplanationOfBenefitInsurance',
        'accident': 'ExplanationOfBenefitAccident',
        'item': 'ExplanationOfBenefitItem',
        'addItem': 'ExplanationOfBenefitAddItem',
        'total': 'ExplanationOfBenefitTotal',
        'payment': 'ExplanationOfBenefitPayment',
        'formCode': 'CodeableConcept',
        'form': 'Attachment',
        'processNote': 'ExplanationOfBenefitProcessNote',
        'benefitPeriod': 'Period',
        'benefitBalance': 'ExplanationOfBenefitBenefitBalance',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    type_: CodeableConcept | dict | None
    subType: CodeableConcept | dict | None
    use: Optional[Code] = None
    patient: Reference | dict | None
    billablePeriod: Period | dict | None
    created: Optional[DateTime] = None
    enterer: Reference | dict | None
    insurer: Reference | dict | None
    provider: Reference | dict | None
    priority: CodeableConcept | dict | None
    fundsReserveRequested: CodeableConcept | dict | None
    fundsReserve: CodeableConcept | dict | None
    related: ExplanationOfBenefitRelated | FHIRList[ExplanationOfBenefitRelated] | list | dict
    prescription: Reference | dict | None
    originalPrescription: Reference | dict | None
    payee: ExplanationOfBenefitPayee | dict | None
    referral: Reference | dict | None
    facility: Reference | dict | None
    claim: Reference | dict | None
    claimResponse: Reference | dict | None
    outcome: Optional[Code] = None
    disposition: Optional[String] = None
    preAuthRef: String | FHIRList[String] | list | None = None
    preAuthRefPeriod: Period | FHIRList[Period] | list | dict
    careTeam: ExplanationOfBenefitCareTeam | FHIRList[ExplanationOfBenefitCareTeam] | list | dict
    supportingInfo: ExplanationOfBenefitSupportingInfo | FHIRList[ExplanationOfBenefitSupportingInfo] | list | dict
    diagnosis: ExplanationOfBenefitDiagnosis | FHIRList[ExplanationOfBenefitDiagnosis] | list | dict
    procedure: ExplanationOfBenefitProcedure | FHIRList[ExplanationOfBenefitProcedure] | list | dict
    precedence: Optional[PositiveInt] = None
    insurance: ExplanationOfBenefitInsurance | FHIRList[ExplanationOfBenefitInsurance] | list | dict
    accident: ExplanationOfBenefitAccident | dict | None
    item: ExplanationOfBenefitItem | FHIRList[ExplanationOfBenefitItem] | list | dict
    addItem: ExplanationOfBenefitAddItem | FHIRList[ExplanationOfBenefitAddItem] | list | dict
    adjudication: Any = None
    total: ExplanationOfBenefitTotal | FHIRList[ExplanationOfBenefitTotal] | list | dict
    payment: ExplanationOfBenefitPayment | dict | None
    formCode: CodeableConcept | dict | None
    form: Attachment | dict | None
    processNote: ExplanationOfBenefitProcessNote | FHIRList[ExplanationOfBenefitProcessNote] | list | dict
    benefitPeriod: Period | dict | None
    benefitBalance: ExplanationOfBenefitBenefitBalance | FHIRList[ExplanationOfBenefitBenefitBalance] | list | dict


class FamilyMemberHistoryCondition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'note'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'outcome': 'CodeableConcept',
        'onsetAge': 'Age',
        'onsetRange': 'Range',
        'onsetPeriod': 'Period',
        'note': 'Annotation',
    }
    _choice_fields = {'onset': ['onsetAge', 'onsetRange', 'onsetPeriod', 'onsetString']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    outcome: CodeableConcept | dict | None
    contributedToDeath: Optional[Boolean] = None
    onsetAge: Age | dict | None
    onsetRange: Range | dict | None
    onsetPeriod: Period | dict | None
    onsetString: Optional[String] = None
    note: Annotation | FHIRList[Annotation] | list | dict


class FamilyMemberHistory(FHIRResource):
    _resource_type = "FamilyMemberHistory"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'instantiatesCanonical',
        'instantiatesUri',
        'reasonCode',
        'reasonReference',
        'note',
        'condition',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'dataAbsentReason': 'CodeableConcept',
        'patient': 'Reference',
        'relationship': 'CodeableConcept',
        'sex': 'CodeableConcept',
        'bornPeriod': 'Period',
        'ageAge': 'Age',
        'ageRange': 'Range',
        'deceasedAge': 'Age',
        'deceasedRange': 'Range',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'note': 'Annotation',
        'condition': 'FamilyMemberHistoryCondition',
    }
    _choice_fields = {
        'age': ['ageAge', 'ageRange', 'ageString'],
        'born': ['bornPeriod', 'bornDate', 'bornString'],
        'deceased': ['deceasedBoolean', 'deceasedAge', 'deceasedRange', 'deceasedDate', 'deceasedString'],
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    instantiatesCanonical: Canonical | FHIRList[Canonical] | list | None = None
    instantiatesUri: Uri | FHIRList[Uri] | list | None = None
    status: Optional[Code] = None
    dataAbsentReason: CodeableConcept | dict | None
    patient: Reference | dict | None
    date: Optional[DateTime] = None
    name: Optional[String] = None
    relationship: CodeableConcept | dict | None
    sex: CodeableConcept | dict | None
    bornPeriod: Period | dict | None
    bornDate: Optional[Date] = None
    bornString: Optional[String] = None
    ageAge: Age | dict | None
    ageRange: Range | dict | None
    ageString: Optional[String] = None
    estimatedAge: Optional[Boolean] = None
    deceasedBoolean: Optional[Boolean] = None
    deceasedAge: Age | dict | None
    deceasedRange: Range | dict | None
    deceasedDate: Optional[Date] = None
    deceasedString: Optional[String] = None
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    condition: FamilyMemberHistoryCondition | FHIRList[FamilyMemberHistoryCondition] | list | dict


class Flag(FHIRResource):
    _resource_type = "Flag"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'period': 'Period',
        'encounter': 'Reference',
        'author': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    period: Period | dict | None
    encounter: Reference | dict | None
    author: Reference | dict | None


class GoalTarget(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'measure': 'CodeableConcept',
        'detailQuantity': 'Quantity',
        'detailRange': 'Range',
        'detailCodeableConcept': 'CodeableConcept',
        'detailRatio': 'Ratio',
        'dueDuration': 'Duration',
    }
    _choice_fields = {
        'detail': ['detailQuantity', 'detailRange', 'detailCodeableConcept', 'detailString', 'detailBoolean', 'detailInteger', 'detailRatio'],
        'due': ['dueDate', 'dueDuration'],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    measure: CodeableConcept | dict | None
    detailQuantity: Quantity | dict | None
    detailRange: Range | dict | None
    detailCodeableConcept: CodeableConcept | dict | None
    detailString: Optional[String] = None
    detailBoolean: Optional[Boolean] = None
    detailInteger: Optional[Integer] = None
    detailRatio: Ratio | dict | None
    dueDate: Optional[Date] = None
    dueDuration: Duration | dict | None


class Goal(FHIRResource):
    _resource_type = "Goal"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'target', 'addresses', 'note', 'outcomeCode', 'outcomeReference'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'achievementStatus': 'CodeableConcept',
        'category': 'CodeableConcept',
        'priority': 'CodeableConcept',
        'description': 'CodeableConcept',
        'subject': 'Reference',
        'startCodeableConcept': 'CodeableConcept',
        'target': 'GoalTarget',
        'expressedBy': 'Reference',
        'addresses': 'Reference',
        'note': 'Annotation',
        'outcomeCode': 'CodeableConcept',
        'outcomeReference': 'Reference',
    }
    _choice_fields = {'start': ['startDate', 'startCodeableConcept']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    lifecycleStatus: Optional[Code] = None
    achievementStatus: CodeableConcept | dict | None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    priority: CodeableConcept | dict | None
    description: CodeableConcept | dict | None
    subject: Reference | dict | None
    startDate: Optional[Date] = None
    startCodeableConcept: CodeableConcept | dict | None
    target: GoalTarget | FHIRList[GoalTarget] | list | dict
    statusDate: Optional[Date] = None
    statusReason: Optional[String] = None
    expressedBy: Reference | dict | None
    addresses: Reference | FHIRList[Reference] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    outcomeCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    outcomeReference: Reference | FHIRList[Reference] | list | dict


class GraphDefinitionLink(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'target'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'target': 'GraphDefinitionLinkTarget'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    path: Optional[String] = None
    sliceName: Optional[String] = None
    min: Optional[Integer] = None
    max: Optional[String] = None
    description: Optional[String] = None
    target: GraphDefinitionLinkTarget | FHIRList[GraphDefinitionLinkTarget] | list | dict


class GraphDefinitionLinkTarget(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'compartment', 'link'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'compartment': 'GraphDefinitionLinkTargetCompartment'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    params: Optional[String] = None
    profile: Optional[Canonical] = None
    compartment: GraphDefinitionLinkTargetCompartment | FHIRList[GraphDefinitionLinkTargetCompartment] | list | dict
    link: Any = None


class GraphDefinitionLinkTargetCompartment(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    use: Optional[Code] = None
    code: Optional[Code] = None
    rule: Optional[Code] = None
    expression: Optional[String] = None
    description: Optional[String] = None


class GraphDefinition(FHIRResource):
    _resource_type = "GraphDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'link'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'link': 'GraphDefinitionLink',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    version: Optional[String] = None
    name: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    start: Optional[Code] = None
    profile: Optional[Canonical] = None
    link: GraphDefinitionLink | FHIRList[GraphDefinitionLink] | list | dict


class GroupCharacteristic(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueCodeableConcept': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueRange': 'Range',
        'valueReference': 'Reference',
        'period': 'Period',
    }
    _choice_fields = {'value': ['valueCodeableConcept', 'valueBoolean', 'valueQuantity', 'valueRange', 'valueReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueBoolean: Optional[Boolean] = None
    valueQuantity: Quantity | dict | None
    valueRange: Range | dict | None
    valueReference: Reference | dict | None
    exclude: Optional[Boolean] = None
    period: Period | dict | None


class GroupMember(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'entity': 'Reference', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    entity: Reference | dict | None
    period: Period | dict | None
    inactive: Optional[Boolean] = None


class Group(FHIRResource):
    _resource_type = "Group"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'characteristic', 'member'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'code': 'CodeableConcept',
        'managingEntity': 'Reference',
        'characteristic': 'GroupCharacteristic',
        'member': 'GroupMember',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    active: Optional[Boolean] = None
    type_: Optional[Code] = None
    actual: Optional[Boolean] = None
    code: CodeableConcept | dict | None
    name: Optional[String] = None
    quantity: Optional[UnsignedInt] = None
    managingEntity: Reference | dict | None
    characteristic: GroupCharacteristic | FHIRList[GroupCharacteristic] | list | dict
    member: GroupMember | FHIRList[GroupMember] | list | dict


class GuidanceResponse(FHIRResource):
    _resource_type = "GuidanceResponse"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'reasonCode',
        'reasonReference',
        'note',
        'evaluationMessage',
        'dataRequirement',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'requestIdentifier': 'Identifier',
        'identifier': 'Identifier',
        'moduleCodeableConcept': 'CodeableConcept',
        'subject': 'Reference',
        'encounter': 'Reference',
        'performer': 'Reference',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'note': 'Annotation',
        'evaluationMessage': 'Reference',
        'outputParameters': 'Reference',
        'result': 'Reference',
        'dataRequirement': 'DataRequirement',
    }
    _choice_fields = {'module': ['moduleUri', 'moduleCanonical', 'moduleCodeableConcept']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    requestIdentifier: Identifier | dict | None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    moduleUri: Optional[Uri] = None
    moduleCanonical: Optional[Canonical] = None
    moduleCodeableConcept: CodeableConcept | dict | None
    status: Optional[Code] = None
    subject: Reference | dict | None
    encounter: Reference | dict | None
    occurrenceDateTime: Optional[DateTime] = None
    performer: Reference | dict | None
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    evaluationMessage: Reference | FHIRList[Reference] | list | dict
    outputParameters: Reference | dict | None
    result: Reference | dict | None
    dataRequirement: DataRequirement | FHIRList[DataRequirement] | list | dict


class HealthcareServiceEligibility(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    comment: Optional[Markdown] = None


class HealthcareServiceAvailableTime(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'daysOfWeek'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    daysOfWeek: Code | FHIRList[Code] | list | None = None
    allDay: Optional[Boolean] = None
    availableStartTime: Optional[Time] = None
    availableEndTime: Optional[Time] = None


class HealthcareServiceNotAvailable(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'during': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    description: Optional[String] = None
    during: Period | dict | None


class HealthcareService(FHIRResource):
    _resource_type = "HealthcareService"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'category',
        'type_',
        'specialty',
        'location',
        'telecom',
        'coverageArea',
        'serviceProvisionCode',
        'eligibility',
        'program',
        'characteristic',
        'communication',
        'referralMethod',
        'availableTime',
        'notAvailable',
        'endpoint',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'providedBy': 'Reference',
        'category': 'CodeableConcept',
        'type_': 'CodeableConcept',
        'specialty': 'CodeableConcept',
        'location': 'Reference',
        'photo': 'Attachment',
        'telecom': 'ContactPoint',
        'coverageArea': 'Reference',
        'serviceProvisionCode': 'CodeableConcept',
        'eligibility': 'HealthcareServiceEligibility',
        'program': 'CodeableConcept',
        'characteristic': 'CodeableConcept',
        'communication': 'CodeableConcept',
        'referralMethod': 'CodeableConcept',
        'availableTime': 'HealthcareServiceAvailableTime',
        'notAvailable': 'HealthcareServiceNotAvailable',
        'endpoint': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    active: Optional[Boolean] = None
    providedBy: Reference | dict | None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    type_: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    specialty: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    location: Reference | FHIRList[Reference] | list | dict
    name: Optional[String] = None
    comment: Optional[String] = None
    extraDetails: Optional[Markdown] = None
    photo: Attachment | dict | None
    telecom: ContactPoint | FHIRList[ContactPoint] | list | dict
    coverageArea: Reference | FHIRList[Reference] | list | dict
    serviceProvisionCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    eligibility: HealthcareServiceEligibility | FHIRList[HealthcareServiceEligibility] | list | dict
    program: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    characteristic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    communication: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    referralMethod: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    appointmentRequired: Optional[Boolean] = None
    availableTime: HealthcareServiceAvailableTime | FHIRList[HealthcareServiceAvailableTime] | list | dict
    notAvailable: HealthcareServiceNotAvailable | FHIRList[HealthcareServiceNotAvailable] | list | dict
    availabilityExceptions: Optional[String] = None
    endpoint: Reference | FHIRList[Reference] | list | dict


class ImagingStudySeries(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'endpoint', 'specimen', 'performer', 'instance'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'modality': 'Coding',
        'endpoint': 'Reference',
        'bodySite': 'Coding',
        'laterality': 'Coding',
        'specimen': 'Reference',
        'performer': 'ImagingStudySeriesPerformer',
        'instance': 'ImagingStudySeriesInstance',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    uid: Optional[Id] = None
    number: Optional[UnsignedInt] = None
    modality: Coding | dict | None
    description: Optional[String] = None
    numberOfInstances: Optional[UnsignedInt] = None
    endpoint: Reference | FHIRList[Reference] | list | dict
    bodySite: Coding | dict | None
    laterality: Coding | dict | None
    specimen: Reference | FHIRList[Reference] | list | dict
    started: Optional[DateTime] = None
    performer: ImagingStudySeriesPerformer | FHIRList[ImagingStudySeriesPerformer] | list | dict
    instance: ImagingStudySeriesInstance | FHIRList[ImagingStudySeriesInstance] | list | dict


class ImagingStudySeriesPerformer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'function': 'CodeableConcept', 'actor': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    function: CodeableConcept | dict | None
    actor: Reference | dict | None


class ImagingStudySeriesInstance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'sopClass': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    uid: Optional[Id] = None
    sopClass: Coding | dict | None
    number: Optional[UnsignedInt] = None
    title: Optional[String] = None


class ImagingStudy(FHIRResource):
    _resource_type = "ImagingStudy"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'modality',
        'basedOn',
        'interpreter',
        'endpoint',
        'procedureCode',
        'reasonCode',
        'reasonReference',
        'note',
        'series',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'modality': 'Coding',
        'subject': 'Reference',
        'encounter': 'Reference',
        'basedOn': 'Reference',
        'referrer': 'Reference',
        'interpreter': 'Reference',
        'endpoint': 'Reference',
        'procedureReference': 'Reference',
        'procedureCode': 'CodeableConcept',
        'location': 'Reference',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'note': 'Annotation',
        'series': 'ImagingStudySeries',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    modality: Coding | FHIRList[Coding] | list | dict
    subject: Reference | dict | None
    encounter: Reference | dict | None
    started: Optional[DateTime] = None
    basedOn: Reference | FHIRList[Reference] | list | dict
    referrer: Reference | dict | None
    interpreter: Reference | FHIRList[Reference] | list | dict
    endpoint: Reference | FHIRList[Reference] | list | dict
    numberOfSeries: Optional[UnsignedInt] = None
    numberOfInstances: Optional[UnsignedInt] = None
    procedureReference: Reference | dict | None
    procedureCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    location: Reference | dict | None
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    description: Optional[String] = None
    series: ImagingStudySeries | FHIRList[ImagingStudySeries] | list | dict


class ImmunizationPerformer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'function': 'CodeableConcept', 'actor': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    function: CodeableConcept | dict | None
    actor: Reference | dict | None


class ImmunizationEducation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    documentType: Optional[String] = None
    reference: Optional[Uri] = None
    publicationDate: Optional[DateTime] = None
    presentationDate: Optional[DateTime] = None


class ImmunizationReaction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'detail': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    date: Optional[DateTime] = None
    detail: Reference | dict | None
    reported: Optional[Boolean] = None


class ImmunizationProtocolApplied(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'targetDisease'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'authority': 'Reference', 'targetDisease': 'CodeableConcept'}
    _choice_fields = {'doseNumber': ['doseNumberPositiveInt', 'doseNumberString'], 'seriesDoses': ['seriesDosesPositiveInt', 'seriesDosesString']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    series: Optional[String] = None
    authority: Reference | dict | None
    targetDisease: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    doseNumberPositiveInt: Optional[PositiveInt] = None
    doseNumberString: Optional[String] = None
    seriesDosesPositiveInt: Optional[PositiveInt] = None
    seriesDosesString: Optional[String] = None


class Immunization(FHIRResource):
    _resource_type = "Immunization"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'performer',
        'note',
        'reasonCode',
        'reasonReference',
        'subpotentReason',
        'education',
        'programEligibility',
        'reaction',
        'protocolApplied',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'statusReason': 'CodeableConcept',
        'vaccineCode': 'CodeableConcept',
        'patient': 'Reference',
        'encounter': 'Reference',
        'reportOrigin': 'CodeableConcept',
        'location': 'Reference',
        'manufacturer': 'Reference',
        'site': 'CodeableConcept',
        'route': 'CodeableConcept',
        'doseQuantity': 'Quantity',
        'performer': 'ImmunizationPerformer',
        'note': 'Annotation',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'subpotentReason': 'CodeableConcept',
        'education': 'ImmunizationEducation',
        'programEligibility': 'CodeableConcept',
        'fundingSource': 'CodeableConcept',
        'reaction': 'ImmunizationReaction',
        'protocolApplied': 'ImmunizationProtocolApplied',
    }
    _choice_fields = {'occurrence': ['occurrenceDateTime', 'occurrenceString']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    statusReason: CodeableConcept | dict | None
    vaccineCode: CodeableConcept | dict | None
    patient: Reference | dict | None
    encounter: Reference | dict | None
    occurrenceDateTime: Optional[DateTime] = None
    occurrenceString: Optional[String] = None
    recorded: Optional[DateTime] = None
    primarySource: Optional[Boolean] = None
    reportOrigin: CodeableConcept | dict | None
    location: Reference | dict | None
    manufacturer: Reference | dict | None
    lotNumber: Optional[String] = None
    expirationDate: Optional[Date] = None
    site: CodeableConcept | dict | None
    route: CodeableConcept | dict | None
    doseQuantity: Quantity | dict | None
    performer: ImmunizationPerformer | FHIRList[ImmunizationPerformer] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    isSubpotent: Optional[Boolean] = None
    subpotentReason: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    education: ImmunizationEducation | FHIRList[ImmunizationEducation] | list | dict
    programEligibility: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    fundingSource: CodeableConcept | dict | None
    reaction: ImmunizationReaction | FHIRList[ImmunizationReaction] | list | dict
    protocolApplied: ImmunizationProtocolApplied | FHIRList[ImmunizationProtocolApplied] | list | dict


class ImmunizationEvaluation(FHIRResource):
    _resource_type = "ImmunizationEvaluation"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'doseStatusReason'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'patient': 'Reference',
        'authority': 'Reference',
        'targetDisease': 'CodeableConcept',
        'immunizationEvent': 'Reference',
        'doseStatus': 'CodeableConcept',
        'doseStatusReason': 'CodeableConcept',
    }
    _choice_fields = {'doseNumber': ['doseNumberPositiveInt', 'doseNumberString'], 'seriesDoses': ['seriesDosesPositiveInt', 'seriesDosesString']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    patient: Reference | dict | None
    date: Optional[DateTime] = None
    authority: Reference | dict | None
    targetDisease: CodeableConcept | dict | None
    immunizationEvent: Reference | dict | None
    doseStatus: CodeableConcept | dict | None
    doseStatusReason: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    description: Optional[String] = None
    series: Optional[String] = None
    doseNumberPositiveInt: Optional[PositiveInt] = None
    doseNumberString: Optional[String] = None
    seriesDosesPositiveInt: Optional[PositiveInt] = None
    seriesDosesString: Optional[String] = None


class ImmunizationRecommendationRecommendation(FHIRElement):
    _list_fields = {
        'extension',
        'modifierExtension',
        'vaccineCode',
        'contraindicatedVaccineCode',
        'forecastReason',
        'dateCriterion',
        'supportingImmunization',
        'supportingPatientInformation',
    }
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'vaccineCode': 'CodeableConcept',
        'targetDisease': 'CodeableConcept',
        'contraindicatedVaccineCode': 'CodeableConcept',
        'forecastStatus': 'CodeableConcept',
        'forecastReason': 'CodeableConcept',
        'dateCriterion': 'ImmunizationRecommendationRecommendationDateCriterion',
        'supportingImmunization': 'Reference',
        'supportingPatientInformation': 'Reference',
    }
    _choice_fields = {'doseNumber': ['doseNumberPositiveInt', 'doseNumberString'], 'seriesDoses': ['seriesDosesPositiveInt', 'seriesDosesString']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    vaccineCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    targetDisease: CodeableConcept | dict | None
    contraindicatedVaccineCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    forecastStatus: CodeableConcept | dict | None
    forecastReason: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    dateCriterion: ImmunizationRecommendationRecommendationDateCriterion | FHIRList[ImmunizationRecommendationRecommendationDateCriterion] | list | dict
    description: Optional[String] = None
    series: Optional[String] = None
    doseNumberPositiveInt: Optional[PositiveInt] = None
    doseNumberString: Optional[String] = None
    seriesDosesPositiveInt: Optional[PositiveInt] = None
    seriesDosesString: Optional[String] = None
    supportingImmunization: Reference | FHIRList[Reference] | list | dict
    supportingPatientInformation: Reference | FHIRList[Reference] | list | dict


class ImmunizationRecommendationRecommendationDateCriterion(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    value: Optional[DateTime] = None


class ImmunizationRecommendation(FHIRResource):
    _resource_type = "ImmunizationRecommendation"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'recommendation'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'patient': 'Reference',
        'authority': 'Reference',
        'recommendation': 'ImmunizationRecommendationRecommendation',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    patient: Reference | dict | None
    date: Optional[DateTime] = None
    authority: Reference | dict | None
    recommendation: ImmunizationRecommendationRecommendation | FHIRList[ImmunizationRecommendationRecommendation] | list | dict


class ImplementationGuideDependsOn(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    uri: Optional[Canonical] = None
    packageId: Optional[Id] = None
    version: Optional[String] = None


class ImplementationGuideGlobal(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    profile: Optional[Canonical] = None


class ImplementationGuideDefinition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'grouping', 'resource', 'parameter', 'template'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'grouping': 'ImplementationGuideDefinitionGrouping',
        'resource': 'ImplementationGuideDefinitionResource',
        'page': 'ImplementationGuideDefinitionPage',
        'parameter': 'ImplementationGuideDefinitionParameter',
        'template': 'ImplementationGuideDefinitionTemplate',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    grouping: ImplementationGuideDefinitionGrouping | FHIRList[ImplementationGuideDefinitionGrouping] | list | dict
    resource: ImplementationGuideDefinitionResource | FHIRList[ImplementationGuideDefinitionResource] | list | dict
    page: ImplementationGuideDefinitionPage | dict | None
    parameter: ImplementationGuideDefinitionParameter | FHIRList[ImplementationGuideDefinitionParameter] | list | dict
    template: ImplementationGuideDefinitionTemplate | FHIRList[ImplementationGuideDefinitionTemplate] | list | dict


class ImplementationGuideDefinitionGrouping(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[String] = None
    description: Optional[String] = None


class ImplementationGuideDefinitionResource(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'fhirVersion'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'reference': 'Reference'}
    _choice_fields = {'example': ['exampleBoolean', 'exampleCanonical']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    reference: Reference | dict | None
    fhirVersion: Code | FHIRList[Code] | list | None = None
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
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    nameUrl: Optional[Url] = None
    nameReference: Reference | dict | None
    title: Optional[String] = None
    generation: Optional[Code] = None
    page: Any = None


class ImplementationGuideDefinitionParameter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    value: Optional[String] = None


class ImplementationGuideDefinitionTemplate(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    source: Optional[String] = None
    scope: Optional[String] = None


class ImplementationGuideManifest(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'resource', 'page', 'image', 'other'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'resource': 'ImplementationGuideManifestResource',
        'page': 'ImplementationGuideManifestPage',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    rendering: Optional[Url] = None
    resource: ImplementationGuideManifestResource | FHIRList[ImplementationGuideManifestResource] | list | dict
    page: ImplementationGuideManifestPage | FHIRList[ImplementationGuideManifestPage] | list | dict
    image: String | FHIRList[String] | list | None = None
    other: String | FHIRList[String] | list | None = None


class ImplementationGuideManifestResource(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'reference': 'Reference'}
    _choice_fields = {'example': ['exampleBoolean', 'exampleCanonical']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    reference: Reference | dict | None
    exampleBoolean: Optional[Boolean] = None
    exampleCanonical: Optional[Canonical] = None
    relativePath: Optional[Url] = None


class ImplementationGuideManifestPage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'anchor'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[String] = None
    title: Optional[String] = None
    anchor: String | FHIRList[String] | list | None = None


class ImplementationGuide(FHIRResource):
    _resource_type = "ImplementationGuide"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'fhirVersion', 'dependsOn', 'global_'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'dependsOn': 'ImplementationGuideDependsOn',
        'global_': 'ImplementationGuideGlobal',
        'definition': 'ImplementationGuideDefinition',
        'manifest': 'ImplementationGuideManifest',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    copyright: Optional[Markdown] = None
    packageId: Optional[Id] = None
    license: Optional[Code] = None
    fhirVersion: Code | FHIRList[Code] | list | None = None
    dependsOn: ImplementationGuideDependsOn | FHIRList[ImplementationGuideDependsOn] | list | dict
    global_: ImplementationGuideGlobal | FHIRList[ImplementationGuideGlobal] | list | dict
    definition: ImplementationGuideDefinition | dict | None
    manifest: ImplementationGuideManifest | dict | None


class InsurancePlanContact(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'telecom'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'purpose': 'CodeableConcept',
        'name': 'HumanName',
        'telecom': 'ContactPoint',
        'address': 'Address',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    purpose: CodeableConcept | dict | None
    name: HumanName | dict | None
    telecom: ContactPoint | FHIRList[ContactPoint] | list | dict
    address: Address | dict | None


class InsurancePlanCoverage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'network', 'benefit'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'network': 'Reference',
        'benefit': 'InsurancePlanCoverageBenefit',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    network: Reference | FHIRList[Reference] | list | dict
    benefit: InsurancePlanCoverageBenefit | FHIRList[InsurancePlanCoverageBenefit] | list | dict


class InsurancePlanCoverageBenefit(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'limit'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'limit': 'InsurancePlanCoverageBenefitLimit'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    requirement: Optional[String] = None
    limit: InsurancePlanCoverageBenefitLimit | FHIRList[InsurancePlanCoverageBenefitLimit] | list | dict


class InsurancePlanCoverageBenefitLimit(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'value': 'Quantity', 'code': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    value: Quantity | dict | None
    code: CodeableConcept | dict | None


class InsurancePlanPlan(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'identifier', 'coverageArea', 'network', 'generalCost', 'specificCost'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'coverageArea': 'Reference',
        'network': 'Reference',
        'generalCost': 'InsurancePlanPlanGeneralCost',
        'specificCost': 'InsurancePlanPlanSpecificCost',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    type_: CodeableConcept | dict | None
    coverageArea: Reference | FHIRList[Reference] | list | dict
    network: Reference | FHIRList[Reference] | list | dict
    generalCost: InsurancePlanPlanGeneralCost | FHIRList[InsurancePlanPlanGeneralCost] | list | dict
    specificCost: InsurancePlanPlanSpecificCost | FHIRList[InsurancePlanPlanSpecificCost] | list | dict


class InsurancePlanPlanGeneralCost(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'cost': 'Money'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    groupSize: Optional[PositiveInt] = None
    cost: Money | dict | None
    comment: Optional[String] = None


class InsurancePlanPlanSpecificCost(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'benefit'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'category': 'CodeableConcept',
        'benefit': 'InsurancePlanPlanSpecificCostBenefit',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    category: CodeableConcept | dict | None
    benefit: InsurancePlanPlanSpecificCostBenefit | FHIRList[InsurancePlanPlanSpecificCostBenefit] | list | dict


class InsurancePlanPlanSpecificCostBenefit(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'cost'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'cost': 'InsurancePlanPlanSpecificCostBenefitCost'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    cost: InsurancePlanPlanSpecificCostBenefitCost | FHIRList[InsurancePlanPlanSpecificCostBenefitCost] | list | dict


class InsurancePlanPlanSpecificCostBenefitCost(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'qualifiers'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'applicability': 'CodeableConcept',
        'qualifiers': 'CodeableConcept',
        'value': 'Quantity',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    applicability: CodeableConcept | dict | None
    qualifiers: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    value: Quantity | dict | None


class InsurancePlan(FHIRResource):
    _resource_type = "InsurancePlan"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'type_',
        'alias',
        'coverageArea',
        'contact',
        'endpoint',
        'network',
        'coverage',
        'plan',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'period': 'Period',
        'ownedBy': 'Reference',
        'administeredBy': 'Reference',
        'coverageArea': 'Reference',
        'contact': 'InsurancePlanContact',
        'endpoint': 'Reference',
        'network': 'Reference',
        'coverage': 'InsurancePlanCoverage',
        'plan': 'InsurancePlanPlan',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    type_: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    name: Optional[String] = None
    alias: String | FHIRList[String] | list | None = None
    period: Period | dict | None
    ownedBy: Reference | dict | None
    administeredBy: Reference | dict | None
    coverageArea: Reference | FHIRList[Reference] | list | dict
    contact: InsurancePlanContact | FHIRList[InsurancePlanContact] | list | dict
    endpoint: Reference | FHIRList[Reference] | list | dict
    network: Reference | FHIRList[Reference] | list | dict
    coverage: InsurancePlanCoverage | FHIRList[InsurancePlanCoverage] | list | dict
    plan: InsurancePlanPlan | FHIRList[InsurancePlanPlan] | list | dict


class InvoiceParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'role': 'CodeableConcept', 'actor': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    role: CodeableConcept | dict | None
    actor: Reference | dict | None


class InvoiceLineItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'priceComponent'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'chargeItemReference': 'Reference',
        'chargeItemCodeableConcept': 'CodeableConcept',
        'priceComponent': 'InvoiceLineItemPriceComponent',
    }
    _choice_fields = {'chargeItem': ['chargeItemReference', 'chargeItemCodeableConcept']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sequence: Optional[PositiveInt] = None
    chargeItemReference: Reference | dict | None
    chargeItemCodeableConcept: CodeableConcept | dict | None
    priceComponent: InvoiceLineItemPriceComponent | FHIRList[InvoiceLineItemPriceComponent] | list | dict


class InvoiceLineItemPriceComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'amount': 'Money'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    code: CodeableConcept | dict | None
    factor: Optional[Decimal] = None
    amount: Money | dict | None


class Invoice(FHIRResource):
    _resource_type = "Invoice"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'participant', 'lineItem', 'totalPriceComponent', 'note'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'subject': 'Reference',
        'recipient': 'Reference',
        'participant': 'InvoiceParticipant',
        'issuer': 'Reference',
        'account': 'Reference',
        'lineItem': 'InvoiceLineItem',
        'totalNet': 'Money',
        'totalGross': 'Money',
        'note': 'Annotation',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    cancelledReason: Optional[String] = None
    type_: CodeableConcept | dict | None
    subject: Reference | dict | None
    recipient: Reference | dict | None
    date: Optional[DateTime] = None
    participant: InvoiceParticipant | FHIRList[InvoiceParticipant] | list | dict
    issuer: Reference | dict | None
    account: Reference | dict | None
    lineItem: InvoiceLineItem | FHIRList[InvoiceLineItem] | list | dict
    totalPriceComponent: Any = None
    totalNet: Money | dict | None
    totalGross: Money | dict | None
    paymentTerms: Optional[Markdown] = None
    note: Annotation | FHIRList[Annotation] | list | dict


class Library(FHIRResource):
    _resource_type = "Library"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'contact',
        'useContext',
        'jurisdiction',
        'topic',
        'author',
        'editor',
        'reviewer',
        'endorser',
        'relatedArtifact',
        'parameter',
        'dataRequirement',
        'content',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'subjectCodeableConcept': 'CodeableConcept',
        'subjectReference': 'Reference',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'topic': 'CodeableConcept',
        'author': 'ContactDetail',
        'editor': 'ContactDetail',
        'reviewer': 'ContactDetail',
        'endorser': 'ContactDetail',
        'relatedArtifact': 'RelatedArtifact',
        'parameter': 'ParameterDefinition',
        'dataRequirement': 'DataRequirement',
        'content': 'Attachment',
    }
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    type_: CodeableConcept | dict | None
    subjectCodeableConcept: CodeableConcept | dict | None
    subjectReference: Reference | dict | None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    topic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    author: ContactDetail | FHIRList[ContactDetail] | list | dict
    editor: ContactDetail | FHIRList[ContactDetail] | list | dict
    reviewer: ContactDetail | FHIRList[ContactDetail] | list | dict
    endorser: ContactDetail | FHIRList[ContactDetail] | list | dict
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    parameter: ParameterDefinition | FHIRList[ParameterDefinition] | list | dict
    dataRequirement: DataRequirement | FHIRList[DataRequirement] | list | dict
    content: Attachment | FHIRList[Attachment] | list | dict


class LinkageItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'resource': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    resource: Reference | dict | None


class Linkage(FHIRResource):
    _resource_type = "Linkage"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'item'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'author': 'Reference',
        'item': 'LinkageItem',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    active: Optional[Boolean] = None
    author: Reference | dict | None
    item: LinkageItem | FHIRList[LinkageItem] | list | dict


class ListEntry(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'flag': 'CodeableConcept', 'item': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    flag: CodeableConcept | dict | None
    deleted: Optional[Boolean] = None
    date: Optional[DateTime] = None
    item: Reference | dict | None


class List(FHIRResource):
    _resource_type = "List"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'note', 'entry'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'encounter': 'Reference',
        'source': 'Reference',
        'orderedBy': 'CodeableConcept',
        'note': 'Annotation',
        'entry': 'ListEntry',
        'emptyReason': 'CodeableConcept',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    mode: Optional[Code] = None
    title: Optional[String] = None
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    encounter: Reference | dict | None
    date: Optional[DateTime] = None
    source: Reference | dict | None
    orderedBy: CodeableConcept | dict | None
    note: Annotation | FHIRList[Annotation] | list | dict
    entry: ListEntry | FHIRList[ListEntry] | list | dict
    emptyReason: CodeableConcept | dict | None


class LocationPosition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    longitude: Optional[Decimal] = None
    latitude: Optional[Decimal] = None
    altitude: Optional[Decimal] = None


class LocationHoursOfOperation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'daysOfWeek'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    daysOfWeek: Code | FHIRList[Code] | list | None = None
    allDay: Optional[Boolean] = None
    openingTime: Optional[Time] = None
    closingTime: Optional[Time] = None


class Location(FHIRResource):
    _resource_type = "Location"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'alias', 'type_', 'telecom', 'hoursOfOperation', 'endpoint'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'operationalStatus': 'Coding',
        'type_': 'CodeableConcept',
        'telecom': 'ContactPoint',
        'address': 'Address',
        'physicalType': 'CodeableConcept',
        'position': 'LocationPosition',
        'managingOrganization': 'Reference',
        'partOf': 'Reference',
        'hoursOfOperation': 'LocationHoursOfOperation',
        'endpoint': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    operationalStatus: Coding | dict | None
    name: Optional[String] = None
    alias: String | FHIRList[String] | list | None = None
    description: Optional[String] = None
    mode: Optional[Code] = None
    type_: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    telecom: ContactPoint | FHIRList[ContactPoint] | list | dict
    address: Address | dict | None
    physicalType: CodeableConcept | dict | None
    position: LocationPosition | dict | None
    managingOrganization: Reference | dict | None
    partOf: Reference | dict | None
    hoursOfOperation: LocationHoursOfOperation | FHIRList[LocationHoursOfOperation] | list | dict
    availabilityExceptions: Optional[String] = None
    endpoint: Reference | FHIRList[Reference] | list | dict


class MeasureGroup(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'population', 'stratifier'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'population': 'MeasureGroupPopulation',
        'stratifier': 'MeasureGroupStratifier',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    description: Optional[String] = None
    population: MeasureGroupPopulation | FHIRList[MeasureGroupPopulation] | list | dict
    stratifier: MeasureGroupStratifier | FHIRList[MeasureGroupStratifier] | list | dict


class MeasureGroupPopulation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'criteria': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    description: Optional[String] = None
    criteria: Expression | dict | None


class MeasureGroupStratifier(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'component'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'criteria': 'Expression',
        'component': 'MeasureGroupStratifierComponent',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    description: Optional[String] = None
    criteria: Expression | dict | None
    component: MeasureGroupStratifierComponent | FHIRList[MeasureGroupStratifierComponent] | list | dict


class MeasureGroupStratifierComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'criteria': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    description: Optional[String] = None
    criteria: Expression | dict | None


class MeasureSupplementalData(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'usage'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'usage': 'CodeableConcept', 'criteria': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    usage: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    description: Optional[String] = None
    criteria: Expression | dict | None


class Measure(FHIRResource):
    _resource_type = "Measure"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'contact',
        'useContext',
        'jurisdiction',
        'topic',
        'author',
        'editor',
        'reviewer',
        'endorser',
        'relatedArtifact',
        'library',
        'type_',
        'definition',
        'group',
        'supplementalData',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'subjectCodeableConcept': 'CodeableConcept',
        'subjectReference': 'Reference',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'topic': 'CodeableConcept',
        'author': 'ContactDetail',
        'editor': 'ContactDetail',
        'reviewer': 'ContactDetail',
        'endorser': 'ContactDetail',
        'relatedArtifact': 'RelatedArtifact',
        'scoring': 'CodeableConcept',
        'compositeScoring': 'CodeableConcept',
        'type_': 'CodeableConcept',
        'improvementNotation': 'CodeableConcept',
        'group': 'MeasureGroup',
        'supplementalData': 'MeasureSupplementalData',
    }
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    subjectCodeableConcept: CodeableConcept | dict | None
    subjectReference: Reference | dict | None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    topic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    author: ContactDetail | FHIRList[ContactDetail] | list | dict
    editor: ContactDetail | FHIRList[ContactDetail] | list | dict
    reviewer: ContactDetail | FHIRList[ContactDetail] | list | dict
    endorser: ContactDetail | FHIRList[ContactDetail] | list | dict
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    library: Canonical | FHIRList[Canonical] | list | None = None
    disclaimer: Optional[Markdown] = None
    scoring: CodeableConcept | dict | None
    compositeScoring: CodeableConcept | dict | None
    type_: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    riskAdjustment: Optional[String] = None
    rateAggregation: Optional[String] = None
    rationale: Optional[Markdown] = None
    clinicalRecommendationStatement: Optional[Markdown] = None
    improvementNotation: CodeableConcept | dict | None
    definition: Markdown | FHIRList[Markdown] | list | None = None
    guidance: Optional[Markdown] = None
    group: MeasureGroup | FHIRList[MeasureGroup] | list | dict
    supplementalData: MeasureSupplementalData | FHIRList[MeasureSupplementalData] | list | dict


class MeasureReportGroup(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'population', 'stratifier'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'population': 'MeasureReportGroupPopulation',
        'measureScore': 'Quantity',
        'stratifier': 'MeasureReportGroupStratifier',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    population: MeasureReportGroupPopulation | FHIRList[MeasureReportGroupPopulation] | list | dict
    measureScore: Quantity | dict | None
    stratifier: MeasureReportGroupStratifier | FHIRList[MeasureReportGroupStratifier] | list | dict


class MeasureReportGroupPopulation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'subjectResults': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    count: Optional[Integer] = None
    subjectResults: Reference | dict | None


class MeasureReportGroupStratifier(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'stratum'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'stratum': 'MeasureReportGroupStratifierStratum'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    stratum: MeasureReportGroupStratifierStratum | FHIRList[MeasureReportGroupStratifierStratum] | list | dict


class MeasureReportGroupStratifierStratum(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'component', 'population'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'value': 'CodeableConcept',
        'component': 'MeasureReportGroupStratifierStratumComponent',
        'population': 'MeasureReportGroupStratifierStratumPopulation',
        'measureScore': 'Quantity',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    value: CodeableConcept | dict | None
    component: MeasureReportGroupStratifierStratumComponent | FHIRList[MeasureReportGroupStratifierStratumComponent] | list | dict
    population: MeasureReportGroupStratifierStratumPopulation | FHIRList[MeasureReportGroupStratifierStratumPopulation] | list | dict
    measureScore: Quantity | dict | None


class MeasureReportGroupStratifierStratumComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'value': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    value: CodeableConcept | dict | None


class MeasureReportGroupStratifierStratumPopulation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'subjectResults': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    count: Optional[Integer] = None
    subjectResults: Reference | dict | None


class MeasureReport(FHIRResource):
    _resource_type = "MeasureReport"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'group', 'evaluatedResource'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'subject': 'Reference',
        'reporter': 'Reference',
        'period': 'Period',
        'improvementNotation': 'CodeableConcept',
        'group': 'MeasureReportGroup',
        'evaluatedResource': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    type_: Optional[Code] = None
    measure: Optional[Canonical] = None
    subject: Reference | dict | None
    date: Optional[DateTime] = None
    reporter: Reference | dict | None
    period: Period | dict | None
    improvementNotation: CodeableConcept | dict | None
    group: MeasureReportGroup | FHIRList[MeasureReportGroup] | list | dict
    evaluatedResource: Reference | FHIRList[Reference] | list | dict


class Media(FHIRResource):
    _resource_type = "Media"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'reasonCode', 'note'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'type_': 'CodeableConcept',
        'modality': 'CodeableConcept',
        'view': 'CodeableConcept',
        'subject': 'Reference',
        'encounter': 'Reference',
        'createdPeriod': 'Period',
        'operator': 'Reference',
        'reasonCode': 'CodeableConcept',
        'bodySite': 'CodeableConcept',
        'device': 'Reference',
        'content': 'Attachment',
        'note': 'Annotation',
    }
    _choice_fields = {'created': ['createdDateTime', 'createdPeriod']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    type_: CodeableConcept | dict | None
    modality: CodeableConcept | dict | None
    view: CodeableConcept | dict | None
    subject: Reference | dict | None
    encounter: Reference | dict | None
    createdDateTime: Optional[DateTime] = None
    createdPeriod: Period | dict | None
    issued: Optional[Instant] = None
    operator: Reference | dict | None
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    bodySite: CodeableConcept | dict | None
    deviceName: Optional[String] = None
    device: Reference | dict | None
    height: Optional[PositiveInt] = None
    width: Optional[PositiveInt] = None
    frames: Optional[PositiveInt] = None
    duration: Optional[Decimal] = None
    content: Attachment | dict | None
    note: Annotation | FHIRList[Annotation] | list | dict


class MedicationIngredient(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'itemCodeableConcept': 'CodeableConcept',
        'itemReference': 'Reference',
        'strength': 'Ratio',
    }
    _choice_fields = {'item': ['itemCodeableConcept', 'itemReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    itemCodeableConcept: CodeableConcept | dict | None
    itemReference: Reference | dict | None
    isActive: Optional[Boolean] = None
    strength: Ratio | dict | None


class MedicationBatch(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    lotNumber: Optional[String] = None
    expirationDate: Optional[DateTime] = None


class Medication(FHIRResource):
    _resource_type = "Medication"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'ingredient'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'code': 'CodeableConcept',
        'manufacturer': 'Reference',
        'form': 'CodeableConcept',
        'amount': 'Ratio',
        'ingredient': 'MedicationIngredient',
        'batch': 'MedicationBatch',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    code: CodeableConcept | dict | None
    status: Optional[Code] = None
    manufacturer: Reference | dict | None
    form: CodeableConcept | dict | None
    amount: Ratio | dict | None
    ingredient: MedicationIngredient | FHIRList[MedicationIngredient] | list | dict
    batch: MedicationBatch | dict | None


class MedicationAdministrationPerformer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'function': 'CodeableConcept', 'actor': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    function: CodeableConcept | dict | None
    actor: Reference | dict | None


class MedicationAdministrationDosage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'site': 'CodeableConcept',
        'route': 'CodeableConcept',
        'method': 'CodeableConcept',
        'dose': 'Quantity',
        'rateRatio': 'Ratio',
        'rateQuantity': 'Quantity',
    }
    _choice_fields = {'rate': ['rateRatio', 'rateQuantity']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    text: Optional[String] = None
    site: CodeableConcept | dict | None
    route: CodeableConcept | dict | None
    method: CodeableConcept | dict | None
    dose: Quantity | dict | None
    rateRatio: Ratio | dict | None
    rateQuantity: Quantity | dict | None


class MedicationAdministration(FHIRResource):
    _resource_type = "MedicationAdministration"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'instantiates',
        'partOf',
        'statusReason',
        'supportingInformation',
        'performer',
        'reasonCode',
        'reasonReference',
        'device',
        'note',
        'eventHistory',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'partOf': 'Reference',
        'statusReason': 'CodeableConcept',
        'category': 'CodeableConcept',
        'medicationCodeableConcept': 'CodeableConcept',
        'medicationReference': 'Reference',
        'subject': 'Reference',
        'context': 'Reference',
        'supportingInformation': 'Reference',
        'effectivePeriod': 'Period',
        'performer': 'MedicationAdministrationPerformer',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'request': 'Reference',
        'device': 'Reference',
        'note': 'Annotation',
        'dosage': 'MedicationAdministrationDosage',
        'eventHistory': 'Reference',
    }
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'medication': ['medicationCodeableConcept', 'medicationReference']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    instantiates: Uri | FHIRList[Uri] | list | None = None
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    statusReason: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    category: CodeableConcept | dict | None
    medicationCodeableConcept: CodeableConcept | dict | None
    medicationReference: Reference | dict | None
    subject: Reference | dict | None
    context: Reference | dict | None
    supportingInformation: Reference | FHIRList[Reference] | list | dict
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    performer: MedicationAdministrationPerformer | FHIRList[MedicationAdministrationPerformer] | list | dict
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    request: Reference | dict | None
    device: Reference | FHIRList[Reference] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    dosage: MedicationAdministrationDosage | dict | None
    eventHistory: Reference | FHIRList[Reference] | list | dict


class MedicationDispensePerformer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'function': 'CodeableConcept', 'actor': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    function: CodeableConcept | dict | None
    actor: Reference | dict | None


class MedicationDispenseSubstitution(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'reason', 'responsibleParty'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'reason': 'CodeableConcept',
        'responsibleParty': 'Reference',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    wasSubstituted: Optional[Boolean] = None
    type_: CodeableConcept | dict | None
    reason: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    responsibleParty: Reference | FHIRList[Reference] | list | dict


class MedicationDispense(FHIRResource):
    _resource_type = "MedicationDispense"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'partOf',
        'supportingInformation',
        'performer',
        'authorizingPrescription',
        'receiver',
        'note',
        'dosageInstruction',
        'detectedIssue',
        'eventHistory',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'partOf': 'Reference',
        'statusReasonCodeableConcept': 'CodeableConcept',
        'statusReasonReference': 'Reference',
        'category': 'CodeableConcept',
        'medicationCodeableConcept': 'CodeableConcept',
        'medicationReference': 'Reference',
        'subject': 'Reference',
        'context': 'Reference',
        'supportingInformation': 'Reference',
        'performer': 'MedicationDispensePerformer',
        'location': 'Reference',
        'authorizingPrescription': 'Reference',
        'type_': 'CodeableConcept',
        'quantity': 'Quantity',
        'daysSupply': 'Quantity',
        'destination': 'Reference',
        'receiver': 'Reference',
        'note': 'Annotation',
        'dosageInstruction': 'Dosage',
        'substitution': 'MedicationDispenseSubstitution',
        'detectedIssue': 'Reference',
        'eventHistory': 'Reference',
    }
    _choice_fields = {
        'medication': ['medicationCodeableConcept', 'medicationReference'],
        'statusReason': ['statusReasonCodeableConcept', 'statusReasonReference'],
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    statusReasonCodeableConcept: CodeableConcept | dict | None
    statusReasonReference: Reference | dict | None
    category: CodeableConcept | dict | None
    medicationCodeableConcept: CodeableConcept | dict | None
    medicationReference: Reference | dict | None
    subject: Reference | dict | None
    context: Reference | dict | None
    supportingInformation: Reference | FHIRList[Reference] | list | dict
    performer: MedicationDispensePerformer | FHIRList[MedicationDispensePerformer] | list | dict
    location: Reference | dict | None
    authorizingPrescription: Reference | FHIRList[Reference] | list | dict
    type_: CodeableConcept | dict | None
    quantity: Quantity | dict | None
    daysSupply: Quantity | dict | None
    whenPrepared: Optional[DateTime] = None
    whenHandedOver: Optional[DateTime] = None
    destination: Reference | dict | None
    receiver: Reference | FHIRList[Reference] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    dosageInstruction: Dosage | FHIRList[Dosage] | list | dict
    substitution: MedicationDispenseSubstitution | dict | None
    detectedIssue: Reference | FHIRList[Reference] | list | dict
    eventHistory: Reference | FHIRList[Reference] | list | dict


class MedicationKnowledgeRelatedMedicationKnowledge(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'reference'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'reference': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    reference: Reference | FHIRList[Reference] | list | dict


class MedicationKnowledgeMonograph(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'source': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    source: Reference | dict | None


class MedicationKnowledgeIngredient(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'itemCodeableConcept': 'CodeableConcept',
        'itemReference': 'Reference',
        'strength': 'Ratio',
    }
    _choice_fields = {'item': ['itemCodeableConcept', 'itemReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    itemCodeableConcept: CodeableConcept | dict | None
    itemReference: Reference | dict | None
    isActive: Optional[Boolean] = None
    strength: Ratio | dict | None


class MedicationKnowledgeCost(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'cost': 'Money'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    source: Optional[String] = None
    cost: Money | dict | None


class MedicationKnowledgeMonitoringProgram(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    name: Optional[String] = None


class MedicationKnowledgeAdministrationGuidelines(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'dosage', 'patientCharacteristics'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'dosage': 'MedicationKnowledgeAdministrationGuidelinesDosage',
        'indicationCodeableConcept': 'CodeableConcept',
        'indicationReference': 'Reference',
        'patientCharacteristics': 'MedicationKnowledgeAdministrationGuidelinesPatientCharacteristics',
    }
    _choice_fields = {'indication': ['indicationCodeableConcept', 'indicationReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    dosage: MedicationKnowledgeAdministrationGuidelinesDosage | FHIRList[MedicationKnowledgeAdministrationGuidelinesDosage] | list | dict
    indicationCodeableConcept: CodeableConcept | dict | None
    indicationReference: Reference | dict | None
    patientCharacteristics: (
        MedicationKnowledgeAdministrationGuidelinesPatientCharacteristics
        | FHIRList[MedicationKnowledgeAdministrationGuidelinesPatientCharacteristics]
        | list
        | dict
    )


class MedicationKnowledgeAdministrationGuidelinesDosage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'dosage'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'dosage': 'Dosage'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    dosage: Dosage | FHIRList[Dosage] | list | dict


class MedicationKnowledgeAdministrationGuidelinesPatientCharacteristics(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'value'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'characteristicCodeableConcept': 'CodeableConcept',
        'characteristicQuantity': 'Quantity',
    }
    _choice_fields = {'characteristic': ['characteristicCodeableConcept', 'characteristicQuantity']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    characteristicCodeableConcept: CodeableConcept | dict | None
    characteristicQuantity: Quantity | dict | None
    value: String | FHIRList[String] | list | None = None


class MedicationKnowledgeMedicineClassification(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'classification'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'classification': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    classification: CodeableConcept | FHIRList[CodeableConcept] | list | dict


class MedicationKnowledgePackaging(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'quantity': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    quantity: Quantity | dict | None


class MedicationKnowledgeDrugCharacteristic(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'valueCodeableConcept': 'CodeableConcept',
        'valueQuantity': 'Quantity',
    }
    _choice_fields = {'value': ['valueCodeableConcept', 'valueString', 'valueQuantity', 'valueBase64Binary']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueQuantity: Quantity | dict | None
    valueBase64Binary: Optional[Base64Binary] = None


class MedicationKnowledgeRegulatory(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'substitution', 'schedule'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'regulatoryAuthority': 'Reference',
        'substitution': 'MedicationKnowledgeRegulatorySubstitution',
        'schedule': 'MedicationKnowledgeRegulatorySchedule',
        'maxDispense': 'MedicationKnowledgeRegulatoryMaxDispense',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    regulatoryAuthority: Reference | dict | None
    substitution: MedicationKnowledgeRegulatorySubstitution | FHIRList[MedicationKnowledgeRegulatorySubstitution] | list | dict
    schedule: MedicationKnowledgeRegulatorySchedule | FHIRList[MedicationKnowledgeRegulatorySchedule] | list | dict
    maxDispense: MedicationKnowledgeRegulatoryMaxDispense | dict | None


class MedicationKnowledgeRegulatorySubstitution(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    allowed: Optional[Boolean] = None


class MedicationKnowledgeRegulatorySchedule(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'schedule': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    schedule: CodeableConcept | dict | None


class MedicationKnowledgeRegulatoryMaxDispense(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'quantity': 'Quantity', 'period': 'Duration'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    quantity: Quantity | dict | None
    period: Duration | dict | None


class MedicationKnowledgeKinetics(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'areaUnderCurve', 'lethalDose50'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'areaUnderCurve': 'Quantity',
        'lethalDose50': 'Quantity',
        'halfLifePeriod': 'Duration',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    areaUnderCurve: Quantity | FHIRList[Quantity] | list | dict
    lethalDose50: Quantity | FHIRList[Quantity] | list | dict
    halfLifePeriod: Duration | dict | None


class MedicationKnowledge(FHIRResource):
    _resource_type = "MedicationKnowledge"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'synonym',
        'relatedMedicationKnowledge',
        'associatedMedication',
        'productType',
        'monograph',
        'ingredient',
        'intendedRoute',
        'cost',
        'monitoringProgram',
        'administrationGuidelines',
        'medicineClassification',
        'drugCharacteristic',
        'contraindication',
        'regulatory',
        'kinetics',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'manufacturer': 'Reference',
        'doseForm': 'CodeableConcept',
        'amount': 'Quantity',
        'relatedMedicationKnowledge': 'MedicationKnowledgeRelatedMedicationKnowledge',
        'associatedMedication': 'Reference',
        'productType': 'CodeableConcept',
        'monograph': 'MedicationKnowledgeMonograph',
        'ingredient': 'MedicationKnowledgeIngredient',
        'intendedRoute': 'CodeableConcept',
        'cost': 'MedicationKnowledgeCost',
        'monitoringProgram': 'MedicationKnowledgeMonitoringProgram',
        'administrationGuidelines': 'MedicationKnowledgeAdministrationGuidelines',
        'medicineClassification': 'MedicationKnowledgeMedicineClassification',
        'packaging': 'MedicationKnowledgePackaging',
        'drugCharacteristic': 'MedicationKnowledgeDrugCharacteristic',
        'contraindication': 'Reference',
        'regulatory': 'MedicationKnowledgeRegulatory',
        'kinetics': 'MedicationKnowledgeKinetics',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    status: Optional[Code] = None
    manufacturer: Reference | dict | None
    doseForm: CodeableConcept | dict | None
    amount: Quantity | dict | None
    synonym: String | FHIRList[String] | list | None = None
    relatedMedicationKnowledge: MedicationKnowledgeRelatedMedicationKnowledge | FHIRList[MedicationKnowledgeRelatedMedicationKnowledge] | list | dict
    associatedMedication: Reference | FHIRList[Reference] | list | dict
    productType: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    monograph: MedicationKnowledgeMonograph | FHIRList[MedicationKnowledgeMonograph] | list | dict
    ingredient: MedicationKnowledgeIngredient | FHIRList[MedicationKnowledgeIngredient] | list | dict
    preparationInstruction: Optional[Markdown] = None
    intendedRoute: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    cost: MedicationKnowledgeCost | FHIRList[MedicationKnowledgeCost] | list | dict
    monitoringProgram: MedicationKnowledgeMonitoringProgram | FHIRList[MedicationKnowledgeMonitoringProgram] | list | dict
    administrationGuidelines: MedicationKnowledgeAdministrationGuidelines | FHIRList[MedicationKnowledgeAdministrationGuidelines] | list | dict
    medicineClassification: MedicationKnowledgeMedicineClassification | FHIRList[MedicationKnowledgeMedicineClassification] | list | dict
    packaging: MedicationKnowledgePackaging | dict | None
    drugCharacteristic: MedicationKnowledgeDrugCharacteristic | FHIRList[MedicationKnowledgeDrugCharacteristic] | list | dict
    contraindication: Reference | FHIRList[Reference] | list | dict
    regulatory: MedicationKnowledgeRegulatory | FHIRList[MedicationKnowledgeRegulatory] | list | dict
    kinetics: MedicationKnowledgeKinetics | FHIRList[MedicationKnowledgeKinetics] | list | dict


class MedicationRequestDispenseRequest(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'initialFill': 'MedicationRequestDispenseRequestInitialFill',
        'dispenseInterval': 'Duration',
        'validityPeriod': 'Period',
        'quantity': 'Quantity',
        'expectedSupplyDuration': 'Duration',
        'performer': 'Reference',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    initialFill: MedicationRequestDispenseRequestInitialFill | dict | None
    dispenseInterval: Duration | dict | None
    validityPeriod: Period | dict | None
    numberOfRepeatsAllowed: Optional[UnsignedInt] = None
    quantity: Quantity | dict | None
    expectedSupplyDuration: Duration | dict | None
    performer: Reference | dict | None


class MedicationRequestDispenseRequestInitialFill(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'quantity': 'Quantity', 'duration': 'Duration'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    quantity: Quantity | dict | None
    duration: Duration | dict | None


class MedicationRequestSubstitution(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'allowedCodeableConcept': 'CodeableConcept', 'reason': 'CodeableConcept'}
    _choice_fields = {'allowed': ['allowedBoolean', 'allowedCodeableConcept']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    allowedBoolean: Optional[Boolean] = None
    allowedCodeableConcept: CodeableConcept | dict | None
    reason: CodeableConcept | dict | None


class MedicationRequest(FHIRResource):
    _resource_type = "MedicationRequest"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'category',
        'supportingInformation',
        'reasonCode',
        'reasonReference',
        'instantiatesCanonical',
        'instantiatesUri',
        'basedOn',
        'insurance',
        'note',
        'dosageInstruction',
        'detectedIssue',
        'eventHistory',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'statusReason': 'CodeableConcept',
        'category': 'CodeableConcept',
        'reportedReference': 'Reference',
        'medicationCodeableConcept': 'CodeableConcept',
        'medicationReference': 'Reference',
        'subject': 'Reference',
        'encounter': 'Reference',
        'supportingInformation': 'Reference',
        'requester': 'Reference',
        'performer': 'Reference',
        'performerType': 'CodeableConcept',
        'recorder': 'Reference',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'basedOn': 'Reference',
        'groupIdentifier': 'Identifier',
        'courseOfTherapyType': 'CodeableConcept',
        'insurance': 'Reference',
        'note': 'Annotation',
        'dosageInstruction': 'Dosage',
        'dispenseRequest': 'MedicationRequestDispenseRequest',
        'substitution': 'MedicationRequestSubstitution',
        'priorPrescription': 'Reference',
        'detectedIssue': 'Reference',
        'eventHistory': 'Reference',
    }
    _choice_fields = {'medication': ['medicationCodeableConcept', 'medicationReference'], 'reported': ['reportedBoolean', 'reportedReference']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    statusReason: CodeableConcept | dict | None
    intent: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    priority: Optional[Code] = None
    doNotPerform: Optional[Boolean] = None
    reportedBoolean: Optional[Boolean] = None
    reportedReference: Reference | dict | None
    medicationCodeableConcept: CodeableConcept | dict | None
    medicationReference: Reference | dict | None
    subject: Reference | dict | None
    encounter: Reference | dict | None
    supportingInformation: Reference | FHIRList[Reference] | list | dict
    authoredOn: Optional[DateTime] = None
    requester: Reference | dict | None
    performer: Reference | dict | None
    performerType: CodeableConcept | dict | None
    recorder: Reference | dict | None
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    instantiatesCanonical: Canonical | FHIRList[Canonical] | list | None = None
    instantiatesUri: Uri | FHIRList[Uri] | list | None = None
    basedOn: Reference | FHIRList[Reference] | list | dict
    groupIdentifier: Identifier | dict | None
    courseOfTherapyType: CodeableConcept | dict | None
    insurance: Reference | FHIRList[Reference] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    dosageInstruction: Dosage | FHIRList[Dosage] | list | dict
    dispenseRequest: MedicationRequestDispenseRequest | dict | None
    substitution: MedicationRequestSubstitution | dict | None
    priorPrescription: Reference | dict | None
    detectedIssue: Reference | FHIRList[Reference] | list | dict
    eventHistory: Reference | FHIRList[Reference] | list | dict


class MedicationStatement(FHIRResource):
    _resource_type = "MedicationStatement"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'basedOn',
        'partOf',
        'statusReason',
        'derivedFrom',
        'reasonCode',
        'reasonReference',
        'note',
        'dosage',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'statusReason': 'CodeableConcept',
        'category': 'CodeableConcept',
        'medicationCodeableConcept': 'CodeableConcept',
        'medicationReference': 'Reference',
        'subject': 'Reference',
        'context': 'Reference',
        'effectivePeriod': 'Period',
        'informationSource': 'Reference',
        'derivedFrom': 'Reference',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'note': 'Annotation',
        'dosage': 'Dosage',
    }
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'medication': ['medicationCodeableConcept', 'medicationReference']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    statusReason: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    category: CodeableConcept | dict | None
    medicationCodeableConcept: CodeableConcept | dict | None
    medicationReference: Reference | dict | None
    subject: Reference | dict | None
    context: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    dateAsserted: Optional[DateTime] = None
    informationSource: Reference | dict | None
    derivedFrom: Reference | FHIRList[Reference] | list | dict
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    dosage: Dosage | FHIRList[Dosage] | list | dict


class MedicinalProductName(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'namePart', 'countryLanguage'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'namePart': 'MedicinalProductNameNamePart',
        'countryLanguage': 'MedicinalProductNameCountryLanguage',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    productName: Optional[String] = None
    namePart: MedicinalProductNameNamePart | FHIRList[MedicinalProductNameNamePart] | list | dict
    countryLanguage: MedicinalProductNameCountryLanguage | FHIRList[MedicinalProductNameCountryLanguage] | list | dict


class MedicinalProductNameNamePart(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    part: Optional[String] = None
    type_: Coding | dict | None


class MedicinalProductNameCountryLanguage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'country': 'CodeableConcept',
        'jurisdiction': 'CodeableConcept',
        'language': 'CodeableConcept',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    country: CodeableConcept | dict | None
    jurisdiction: CodeableConcept | dict | None
    language: CodeableConcept | dict | None


class MedicinalProductManufacturingBusinessOperation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'manufacturer'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'operationType': 'CodeableConcept',
        'authorisationReferenceNumber': 'Identifier',
        'confidentialityIndicator': 'CodeableConcept',
        'manufacturer': 'Reference',
        'regulator': 'Reference',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    operationType: CodeableConcept | dict | None
    authorisationReferenceNumber: Identifier | dict | None
    effectiveDate: Optional[DateTime] = None
    confidentialityIndicator: CodeableConcept | dict | None
    manufacturer: Reference | FHIRList[Reference] | list | dict
    regulator: Reference | dict | None


class MedicinalProductSpecialDesignation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'identifier'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'intendedUse': 'CodeableConcept',
        'indicationCodeableConcept': 'CodeableConcept',
        'indicationReference': 'Reference',
        'status': 'CodeableConcept',
        'species': 'CodeableConcept',
    }
    _choice_fields = {'indication': ['indicationCodeableConcept', 'indicationReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    type_: CodeableConcept | dict | None
    intendedUse: CodeableConcept | dict | None
    indicationCodeableConcept: CodeableConcept | dict | None
    indicationReference: Reference | dict | None
    status: CodeableConcept | dict | None
    date: Optional[DateTime] = None
    species: CodeableConcept | dict | None


class MedicinalProduct(FHIRResource):
    _resource_type = "MedicinalProduct"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'specialMeasures',
        'productClassification',
        'marketingStatus',
        'pharmaceuticalProduct',
        'packagedMedicinalProduct',
        'attachedDocument',
        'masterFile',
        'contact',
        'clinicalTrial',
        'name',
        'crossReference',
        'manufacturingBusinessOperation',
        'specialDesignation',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'domain': 'Coding',
        'combinedPharmaceuticalDoseForm': 'CodeableConcept',
        'legalStatusOfSupply': 'CodeableConcept',
        'additionalMonitoringIndicator': 'CodeableConcept',
        'paediatricUseIndicator': 'CodeableConcept',
        'productClassification': 'CodeableConcept',
        'marketingStatus': 'MarketingStatus',
        'pharmaceuticalProduct': 'Reference',
        'packagedMedicinalProduct': 'Reference',
        'attachedDocument': 'Reference',
        'masterFile': 'Reference',
        'contact': 'Reference',
        'clinicalTrial': 'Reference',
        'name': 'MedicinalProductName',
        'crossReference': 'Identifier',
        'manufacturingBusinessOperation': 'MedicinalProductManufacturingBusinessOperation',
        'specialDesignation': 'MedicinalProductSpecialDesignation',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    type_: CodeableConcept | dict | None
    domain: Coding | dict | None
    combinedPharmaceuticalDoseForm: CodeableConcept | dict | None
    legalStatusOfSupply: CodeableConcept | dict | None
    additionalMonitoringIndicator: CodeableConcept | dict | None
    specialMeasures: String | FHIRList[String] | list | None = None
    paediatricUseIndicator: CodeableConcept | dict | None
    productClassification: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    marketingStatus: MarketingStatus | FHIRList[MarketingStatus] | list | dict
    pharmaceuticalProduct: Reference | FHIRList[Reference] | list | dict
    packagedMedicinalProduct: Reference | FHIRList[Reference] | list | dict
    attachedDocument: Reference | FHIRList[Reference] | list | dict
    masterFile: Reference | FHIRList[Reference] | list | dict
    contact: Reference | FHIRList[Reference] | list | dict
    clinicalTrial: Reference | FHIRList[Reference] | list | dict
    name: MedicinalProductName | FHIRList[MedicinalProductName] | list | dict
    crossReference: Identifier | FHIRList[Identifier] | list | dict
    manufacturingBusinessOperation: MedicinalProductManufacturingBusinessOperation | FHIRList[MedicinalProductManufacturingBusinessOperation] | list | dict
    specialDesignation: MedicinalProductSpecialDesignation | FHIRList[MedicinalProductSpecialDesignation] | list | dict


class MedicinalProductAuthorizationJurisdictionalAuthorization(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'identifier', 'jurisdiction'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'country': 'CodeableConcept',
        'jurisdiction': 'CodeableConcept',
        'legalStatusOfSupply': 'CodeableConcept',
        'validityPeriod': 'Period',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    country: CodeableConcept | dict | None
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    legalStatusOfSupply: CodeableConcept | dict | None
    validityPeriod: Period | dict | None


class MedicinalProductAuthorizationProcedure(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'application'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'datePeriod': 'Period'}
    _choice_fields = {'date': ['datePeriod', 'dateDateTime']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | dict | None
    type_: CodeableConcept | dict | None
    datePeriod: Period | dict | None
    dateDateTime: Optional[DateTime] = None
    application: Any = None


class MedicinalProductAuthorization(FHIRResource):
    _resource_type = "MedicinalProductAuthorization"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'country', 'jurisdiction', 'jurisdictionalAuthorization'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'subject': 'Reference',
        'country': 'CodeableConcept',
        'jurisdiction': 'CodeableConcept',
        'status': 'CodeableConcept',
        'validityPeriod': 'Period',
        'dataExclusivityPeriod': 'Period',
        'legalBasis': 'CodeableConcept',
        'jurisdictionalAuthorization': 'MedicinalProductAuthorizationJurisdictionalAuthorization',
        'holder': 'Reference',
        'regulator': 'Reference',
        'procedure': 'MedicinalProductAuthorizationProcedure',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    subject: Reference | dict | None
    country: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    status: CodeableConcept | dict | None
    statusDate: Optional[DateTime] = None
    restoreDate: Optional[DateTime] = None
    validityPeriod: Period | dict | None
    dataExclusivityPeriod: Period | dict | None
    dateOfFirstAuthorization: Optional[DateTime] = None
    internationalBirthDate: Optional[DateTime] = None
    legalBasis: CodeableConcept | dict | None
    jurisdictionalAuthorization: (
        MedicinalProductAuthorizationJurisdictionalAuthorization | FHIRList[MedicinalProductAuthorizationJurisdictionalAuthorization] | list | dict
    )
    holder: Reference | dict | None
    regulator: Reference | dict | None
    procedure: MedicinalProductAuthorizationProcedure | dict | None


class MedicinalProductContraindicationOtherTherapy(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'therapyRelationshipType': 'CodeableConcept',
        'medicationCodeableConcept': 'CodeableConcept',
        'medicationReference': 'Reference',
    }
    _choice_fields = {'medication': ['medicationCodeableConcept', 'medicationReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    therapyRelationshipType: CodeableConcept | dict | None
    medicationCodeableConcept: CodeableConcept | dict | None
    medicationReference: Reference | dict | None


class MedicinalProductContraindication(FHIRResource):
    _resource_type = "MedicinalProductContraindication"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'subject', 'comorbidity', 'therapeuticIndication', 'otherTherapy', 'population'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'subject': 'Reference',
        'disease': 'CodeableConcept',
        'diseaseStatus': 'CodeableConcept',
        'comorbidity': 'CodeableConcept',
        'therapeuticIndication': 'Reference',
        'otherTherapy': 'MedicinalProductContraindicationOtherTherapy',
        'population': 'Population',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    subject: Reference | FHIRList[Reference] | list | dict
    disease: CodeableConcept | dict | None
    diseaseStatus: CodeableConcept | dict | None
    comorbidity: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    therapeuticIndication: Reference | FHIRList[Reference] | list | dict
    otherTherapy: MedicinalProductContraindicationOtherTherapy | FHIRList[MedicinalProductContraindicationOtherTherapy] | list | dict
    population: Population | FHIRList[Population] | list | dict


class MedicinalProductIndicationOtherTherapy(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'therapyRelationshipType': 'CodeableConcept',
        'medicationCodeableConcept': 'CodeableConcept',
        'medicationReference': 'Reference',
    }
    _choice_fields = {'medication': ['medicationCodeableConcept', 'medicationReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    therapyRelationshipType: CodeableConcept | dict | None
    medicationCodeableConcept: CodeableConcept | dict | None
    medicationReference: Reference | dict | None


class MedicinalProductIndication(FHIRResource):
    _resource_type = "MedicinalProductIndication"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'subject', 'comorbidity', 'otherTherapy', 'undesirableEffect', 'population'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'subject': 'Reference',
        'diseaseSymptomProcedure': 'CodeableConcept',
        'diseaseStatus': 'CodeableConcept',
        'comorbidity': 'CodeableConcept',
        'intendedEffect': 'CodeableConcept',
        'duration': 'Quantity',
        'otherTherapy': 'MedicinalProductIndicationOtherTherapy',
        'undesirableEffect': 'Reference',
        'population': 'Population',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    subject: Reference | FHIRList[Reference] | list | dict
    diseaseSymptomProcedure: CodeableConcept | dict | None
    diseaseStatus: CodeableConcept | dict | None
    comorbidity: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    intendedEffect: CodeableConcept | dict | None
    duration: Quantity | dict | None
    otherTherapy: MedicinalProductIndicationOtherTherapy | FHIRList[MedicinalProductIndicationOtherTherapy] | list | dict
    undesirableEffect: Reference | FHIRList[Reference] | list | dict
    population: Population | FHIRList[Population] | list | dict


class MedicinalProductIngredientSpecifiedSubstance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'strength'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'group': 'CodeableConcept',
        'confidentiality': 'CodeableConcept',
        'strength': 'MedicinalProductIngredientSpecifiedSubstanceStrength',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    group: CodeableConcept | dict | None
    confidentiality: CodeableConcept | dict | None
    strength: MedicinalProductIngredientSpecifiedSubstanceStrength | FHIRList[MedicinalProductIngredientSpecifiedSubstanceStrength] | list | dict


class MedicinalProductIngredientSpecifiedSubstanceStrength(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'country', 'referenceStrength'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'presentation': 'Ratio',
        'presentationLowLimit': 'Ratio',
        'concentration': 'Ratio',
        'concentrationLowLimit': 'Ratio',
        'country': 'CodeableConcept',
        'referenceStrength': 'MedicinalProductIngredientSpecifiedSubstanceStrengthReferenceStrength',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    presentation: Ratio | dict | None
    presentationLowLimit: Ratio | dict | None
    concentration: Ratio | dict | None
    concentrationLowLimit: Ratio | dict | None
    measurementPoint: Optional[String] = None
    country: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    referenceStrength: (
        MedicinalProductIngredientSpecifiedSubstanceStrengthReferenceStrength
        | FHIRList[MedicinalProductIngredientSpecifiedSubstanceStrengthReferenceStrength]
        | list
        | dict
    )


class MedicinalProductIngredientSpecifiedSubstanceStrengthReferenceStrength(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'country'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'substance': 'CodeableConcept',
        'strength': 'Ratio',
        'strengthLowLimit': 'Ratio',
        'country': 'CodeableConcept',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    substance: CodeableConcept | dict | None
    strength: Ratio | dict | None
    strengthLowLimit: Ratio | dict | None
    measurementPoint: Optional[String] = None
    country: CodeableConcept | FHIRList[CodeableConcept] | list | dict


class MedicinalProductIngredientSubstance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'strength'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    strength: Any = None


class MedicinalProductIngredient(FHIRResource):
    _resource_type = "MedicinalProductIngredient"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'manufacturer', 'specifiedSubstance'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'role': 'CodeableConcept',
        'manufacturer': 'Reference',
        'specifiedSubstance': 'MedicinalProductIngredientSpecifiedSubstance',
        'substance': 'MedicinalProductIngredientSubstance',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | dict | None
    role: CodeableConcept | dict | None
    allergenicIndicator: Optional[Boolean] = None
    manufacturer: Reference | FHIRList[Reference] | list | dict
    specifiedSubstance: MedicinalProductIngredientSpecifiedSubstance | FHIRList[MedicinalProductIngredientSpecifiedSubstance] | list | dict
    substance: MedicinalProductIngredientSubstance | dict | None


class MedicinalProductInteractionInteractant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'itemReference': 'Reference', 'itemCodeableConcept': 'CodeableConcept'}
    _choice_fields = {'item': ['itemReference', 'itemCodeableConcept']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    itemReference: Reference | dict | None
    itemCodeableConcept: CodeableConcept | dict | None


class MedicinalProductInteraction(FHIRResource):
    _resource_type = "MedicinalProductInteraction"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'subject', 'interactant'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'subject': 'Reference',
        'interactant': 'MedicinalProductInteractionInteractant',
        'type_': 'CodeableConcept',
        'effect': 'CodeableConcept',
        'incidence': 'CodeableConcept',
        'management': 'CodeableConcept',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    subject: Reference | FHIRList[Reference] | list | dict
    description: Optional[String] = None
    interactant: MedicinalProductInteractionInteractant | FHIRList[MedicinalProductInteractionInteractant] | list | dict
    type_: CodeableConcept | dict | None
    effect: CodeableConcept | dict | None
    incidence: CodeableConcept | dict | None
    management: CodeableConcept | dict | None


class MedicinalProductManufactured(FHIRResource):
    _resource_type = "MedicinalProductManufactured"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'manufacturer', 'ingredient', 'otherCharacteristics'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'manufacturedDoseForm': 'CodeableConcept',
        'unitOfPresentation': 'CodeableConcept',
        'quantity': 'Quantity',
        'manufacturer': 'Reference',
        'ingredient': 'Reference',
        'physicalCharacteristics': 'ProdCharacteristic',
        'otherCharacteristics': 'CodeableConcept',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    manufacturedDoseForm: CodeableConcept | dict | None
    unitOfPresentation: CodeableConcept | dict | None
    quantity: Quantity | dict | None
    manufacturer: Reference | FHIRList[Reference] | list | dict
    ingredient: Reference | FHIRList[Reference] | list | dict
    physicalCharacteristics: ProdCharacteristic | dict | None
    otherCharacteristics: CodeableConcept | FHIRList[CodeableConcept] | list | dict


class MedicinalProductPackagedBatchIdentifier(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'outerPackaging': 'Identifier', 'immediatePackaging': 'Identifier'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    outerPackaging: Identifier | dict | None
    immediatePackaging: Identifier | dict | None


class MedicinalProductPackagedPackageItem(FHIRElement):
    _list_fields = {
        'extension',
        'modifierExtension',
        'identifier',
        'material',
        'alternateMaterial',
        'device',
        'manufacturedItem',
        'packageItem',
        'otherCharacteristics',
        'shelfLifeStorage',
        'manufacturer',
    }
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'quantity': 'Quantity',
        'material': 'CodeableConcept',
        'alternateMaterial': 'CodeableConcept',
        'device': 'Reference',
        'manufacturedItem': 'Reference',
        'physicalCharacteristics': 'ProdCharacteristic',
        'otherCharacteristics': 'CodeableConcept',
        'shelfLifeStorage': 'ProductShelfLife',
        'manufacturer': 'Reference',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    type_: CodeableConcept | dict | None
    quantity: Quantity | dict | None
    material: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    alternateMaterial: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    device: Reference | FHIRList[Reference] | list | dict
    manufacturedItem: Reference | FHIRList[Reference] | list | dict
    packageItem: Any = None
    physicalCharacteristics: ProdCharacteristic | dict | None
    otherCharacteristics: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    shelfLifeStorage: ProductShelfLife | FHIRList[ProductShelfLife] | list | dict
    manufacturer: Reference | FHIRList[Reference] | list | dict


class MedicinalProductPackaged(FHIRResource):
    _resource_type = "MedicinalProductPackaged"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'subject', 'marketingStatus', 'manufacturer', 'batchIdentifier', 'packageItem'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'subject': 'Reference',
        'legalStatusOfSupply': 'CodeableConcept',
        'marketingStatus': 'MarketingStatus',
        'marketingAuthorization': 'Reference',
        'manufacturer': 'Reference',
        'batchIdentifier': 'MedicinalProductPackagedBatchIdentifier',
        'packageItem': 'MedicinalProductPackagedPackageItem',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    subject: Reference | FHIRList[Reference] | list | dict
    description: Optional[String] = None
    legalStatusOfSupply: CodeableConcept | dict | None
    marketingStatus: MarketingStatus | FHIRList[MarketingStatus] | list | dict
    marketingAuthorization: Reference | dict | None
    manufacturer: Reference | FHIRList[Reference] | list | dict
    batchIdentifier: MedicinalProductPackagedBatchIdentifier | FHIRList[MedicinalProductPackagedBatchIdentifier] | list | dict
    packageItem: MedicinalProductPackagedPackageItem | FHIRList[MedicinalProductPackagedPackageItem] | list | dict


class MedicinalProductPharmaceuticalCharacteristics(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'status': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    status: CodeableConcept | dict | None


class MedicinalProductPharmaceuticalRouteOfAdministration(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'targetSpecies'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'firstDose': 'Quantity',
        'maxSingleDose': 'Quantity',
        'maxDosePerDay': 'Quantity',
        'maxDosePerTreatmentPeriod': 'Ratio',
        'maxTreatmentPeriod': 'Duration',
        'targetSpecies': 'MedicinalProductPharmaceuticalRouteOfAdministrationTargetSpecies',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    firstDose: Quantity | dict | None
    maxSingleDose: Quantity | dict | None
    maxDosePerDay: Quantity | dict | None
    maxDosePerTreatmentPeriod: Ratio | dict | None
    maxTreatmentPeriod: Duration | dict | None
    targetSpecies: (
        MedicinalProductPharmaceuticalRouteOfAdministrationTargetSpecies
        | FHIRList[MedicinalProductPharmaceuticalRouteOfAdministrationTargetSpecies]
        | list
        | dict
    )


class MedicinalProductPharmaceuticalRouteOfAdministrationTargetSpecies(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'withdrawalPeriod'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'withdrawalPeriod': 'MedicinalProductPharmaceuticalRouteOfAdministrationTargetSpeciesWithdrawalPeriod',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    withdrawalPeriod: (
        MedicinalProductPharmaceuticalRouteOfAdministrationTargetSpeciesWithdrawalPeriod
        | FHIRList[MedicinalProductPharmaceuticalRouteOfAdministrationTargetSpeciesWithdrawalPeriod]
        | list
        | dict
    )


class MedicinalProductPharmaceuticalRouteOfAdministrationTargetSpeciesWithdrawalPeriod(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'tissue': 'CodeableConcept', 'value': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    tissue: CodeableConcept | dict | None
    value: Quantity | dict | None
    supportingInformation: Optional[String] = None


class MedicinalProductPharmaceutical(FHIRResource):
    _resource_type = "MedicinalProductPharmaceutical"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'ingredient', 'device', 'characteristics', 'routeOfAdministration'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'administrableDoseForm': 'CodeableConcept',
        'unitOfPresentation': 'CodeableConcept',
        'ingredient': 'Reference',
        'device': 'Reference',
        'characteristics': 'MedicinalProductPharmaceuticalCharacteristics',
        'routeOfAdministration': 'MedicinalProductPharmaceuticalRouteOfAdministration',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    administrableDoseForm: CodeableConcept | dict | None
    unitOfPresentation: CodeableConcept | dict | None
    ingredient: Reference | FHIRList[Reference] | list | dict
    device: Reference | FHIRList[Reference] | list | dict
    characteristics: MedicinalProductPharmaceuticalCharacteristics | FHIRList[MedicinalProductPharmaceuticalCharacteristics] | list | dict
    routeOfAdministration: MedicinalProductPharmaceuticalRouteOfAdministration | FHIRList[MedicinalProductPharmaceuticalRouteOfAdministration] | list | dict


class MedicinalProductUndesirableEffect(FHIRResource):
    _resource_type = "MedicinalProductUndesirableEffect"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'subject', 'population'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'subject': 'Reference',
        'symptomConditionEffect': 'CodeableConcept',
        'classification': 'CodeableConcept',
        'frequencyOfOccurrence': 'CodeableConcept',
        'population': 'Population',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    subject: Reference | FHIRList[Reference] | list | dict
    symptomConditionEffect: CodeableConcept | dict | None
    classification: CodeableConcept | dict | None
    frequencyOfOccurrence: CodeableConcept | dict | None
    population: Population | FHIRList[Population] | list | dict


class MessageDefinitionFocus(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    profile: Optional[Canonical] = None
    min: Optional[UnsignedInt] = None
    max: Optional[String] = None


class MessageDefinitionAllowedResponse(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    message: Optional[Canonical] = None
    situation: Optional[Markdown] = None


class MessageDefinition(FHIRResource):
    _resource_type = "MessageDefinition"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'replaces',
        'contact',
        'useContext',
        'jurisdiction',
        'parent',
        'focus',
        'allowedResponse',
        'graph',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'eventCoding': 'Coding',
        'focus': 'MessageDefinitionFocus',
        'allowedResponse': 'MessageDefinitionAllowedResponse',
    }
    _choice_fields = {'event': ['eventCoding', 'eventUri']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    replaces: Canonical | FHIRList[Canonical] | list | None = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    base: Optional[Canonical] = None
    parent: Canonical | FHIRList[Canonical] | list | None = None
    eventCoding: Coding | dict | None
    eventUri: Optional[Uri] = None
    category: Optional[Code] = None
    focus: MessageDefinitionFocus | FHIRList[MessageDefinitionFocus] | list | dict
    responseRequired: Optional[Code] = None
    allowedResponse: MessageDefinitionAllowedResponse | FHIRList[MessageDefinitionAllowedResponse] | list | dict
    graph: Canonical | FHIRList[Canonical] | list | None = None


class MessageHeaderDestination(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'target': 'Reference', 'receiver': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[String] = None
    target: Reference | dict | None
    endpoint: Optional[Url] = None
    receiver: Reference | dict | None


class MessageHeaderSource(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'contact': 'ContactPoint'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[String] = None
    software: Optional[String] = None
    version: Optional[String] = None
    contact: ContactPoint | dict | None
    endpoint: Optional[Url] = None


class MessageHeaderResponse(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'details': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Optional[Id] = None
    code: Optional[Code] = None
    details: Reference | dict | None


class MessageHeader(FHIRResource):
    _resource_type = "MessageHeader"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'destination', 'focus'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'eventCoding': 'Coding',
        'destination': 'MessageHeaderDestination',
        'sender': 'Reference',
        'enterer': 'Reference',
        'author': 'Reference',
        'source': 'MessageHeaderSource',
        'responsible': 'Reference',
        'reason': 'CodeableConcept',
        'response': 'MessageHeaderResponse',
        'focus': 'Reference',
    }
    _choice_fields = {'event': ['eventCoding', 'eventUri']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    eventCoding: Coding | dict | None
    eventUri: Optional[Uri] = None
    destination: MessageHeaderDestination | FHIRList[MessageHeaderDestination] | list | dict
    sender: Reference | dict | None
    enterer: Reference | dict | None
    author: Reference | dict | None
    source: MessageHeaderSource | dict | None
    responsible: Reference | dict | None
    reason: CodeableConcept | dict | None
    response: MessageHeaderResponse | dict | None
    focus: Reference | FHIRList[Reference] | list | dict
    definition: Optional[Canonical] = None


class MolecularSequenceReferenceSeq(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'chromosome': 'CodeableConcept',
        'referenceSeqId': 'CodeableConcept',
        'referenceSeqPointer': 'Reference',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    chromosome: CodeableConcept | dict | None
    genomeBuild: Optional[String] = None
    orientation: Optional[Code] = None
    referenceSeqId: CodeableConcept | dict | None
    referenceSeqPointer: Reference | dict | None
    referenceSeqString: Optional[String] = None
    strand: Optional[Code] = None
    windowStart: Optional[Integer] = None
    windowEnd: Optional[Integer] = None


class MolecularSequenceVariant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'variantPointer': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    start: Optional[Integer] = None
    end: Optional[Integer] = None
    observedAllele: Optional[String] = None
    referenceAllele: Optional[String] = None
    cigar: Optional[String] = None
    variantPointer: Reference | dict | None


class MolecularSequenceQuality(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'standardSequence': 'CodeableConcept',
        'score': 'Quantity',
        'method': 'CodeableConcept',
        'roc': 'MolecularSequenceQualityRoc',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    standardSequence: CodeableConcept | dict | None
    start: Optional[Integer] = None
    end: Optional[Integer] = None
    score: Quantity | dict | None
    method: CodeableConcept | dict | None
    truthTP: Optional[Decimal] = None
    queryTP: Optional[Decimal] = None
    truthFN: Optional[Decimal] = None
    queryFP: Optional[Decimal] = None
    gtFP: Optional[Decimal] = None
    precision: Optional[Decimal] = None
    recall: Optional[Decimal] = None
    fScore: Optional[Decimal] = None
    roc: MolecularSequenceQualityRoc | dict | None


class MolecularSequenceQualityRoc(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'score', 'numTP', 'numFP', 'numFN', 'precision', 'sensitivity', 'fMeasure'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    score: Integer | FHIRList[Integer] | list | None = None
    numTP: Integer | FHIRList[Integer] | list | None = None
    numFP: Integer | FHIRList[Integer] | list | None = None
    numFN: Integer | FHIRList[Integer] | list | None = None
    precision: Decimal | FHIRList[Decimal] | list | None = None
    sensitivity: Decimal | FHIRList[Decimal] | list | None = None
    fMeasure: Decimal | FHIRList[Decimal] | list | None = None


class MolecularSequenceRepository(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    url: Optional[Uri] = None
    name: Optional[String] = None
    datasetId: Optional[String] = None
    variantsetId: Optional[String] = None
    readsetId: Optional[String] = None


class MolecularSequenceStructureVariant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'variantType': 'CodeableConcept',
        'outer': 'MolecularSequenceStructureVariantOuter',
        'inner': 'MolecularSequenceStructureVariantInner',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    variantType: CodeableConcept | dict | None
    exact: Optional[Boolean] = None
    length: Optional[Integer] = None
    outer: MolecularSequenceStructureVariantOuter | dict | None
    inner: MolecularSequenceStructureVariantInner | dict | None


class MolecularSequenceStructureVariantOuter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    start: Optional[Integer] = None
    end: Optional[Integer] = None


class MolecularSequenceStructureVariantInner(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    start: Optional[Integer] = None
    end: Optional[Integer] = None


class MolecularSequence(FHIRResource):
    _resource_type = "MolecularSequence"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'variant', 'quality', 'repository', 'pointer', 'structureVariant'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'patient': 'Reference',
        'specimen': 'Reference',
        'device': 'Reference',
        'performer': 'Reference',
        'quantity': 'Quantity',
        'referenceSeq': 'MolecularSequenceReferenceSeq',
        'variant': 'MolecularSequenceVariant',
        'quality': 'MolecularSequenceQuality',
        'repository': 'MolecularSequenceRepository',
        'pointer': 'Reference',
        'structureVariant': 'MolecularSequenceStructureVariant',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    type_: Optional[Code] = None
    coordinateSystem: Optional[Integer] = None
    patient: Reference | dict | None
    specimen: Reference | dict | None
    device: Reference | dict | None
    performer: Reference | dict | None
    quantity: Quantity | dict | None
    referenceSeq: MolecularSequenceReferenceSeq | dict | None
    variant: MolecularSequenceVariant | FHIRList[MolecularSequenceVariant] | list | dict
    observedSeq: Optional[String] = None
    quality: MolecularSequenceQuality | FHIRList[MolecularSequenceQuality] | list | dict
    readCoverage: Optional[Integer] = None
    repository: MolecularSequenceRepository | FHIRList[MolecularSequenceRepository] | list | dict
    pointer: Reference | FHIRList[Reference] | list | dict
    structureVariant: MolecularSequenceStructureVariant | FHIRList[MolecularSequenceStructureVariant] | list | dict


class NamingSystemUniqueId(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    value: Optional[String] = None
    preferred: Optional[Boolean] = None
    comment: Optional[String] = None
    period: Period | dict | None


class NamingSystem(FHIRResource):
    _resource_type = "NamingSystem"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'uniqueId'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'contact': 'ContactDetail',
        'type_': 'CodeableConcept',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'uniqueId': 'NamingSystemUniqueId',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[String] = None
    status: Optional[Code] = None
    kind: Optional[Code] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    responsible: Optional[String] = None
    type_: CodeableConcept | dict | None
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    usage: Optional[String] = None
    uniqueId: NamingSystemUniqueId | FHIRList[NamingSystemUniqueId] | list | dict


class NutritionOrderOralDiet(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'type_', 'schedule', 'nutrient', 'texture', 'fluidConsistencyType'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'schedule': 'Timing',
        'nutrient': 'NutritionOrderOralDietNutrient',
        'texture': 'NutritionOrderOralDietTexture',
        'fluidConsistencyType': 'CodeableConcept',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    schedule: Timing | FHIRList[Timing] | list | dict
    nutrient: NutritionOrderOralDietNutrient | FHIRList[NutritionOrderOralDietNutrient] | list | dict
    texture: NutritionOrderOralDietTexture | FHIRList[NutritionOrderOralDietTexture] | list | dict
    fluidConsistencyType: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    instruction: Optional[String] = None


class NutritionOrderOralDietNutrient(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'modifier': 'CodeableConcept', 'amount': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    modifier: CodeableConcept | dict | None
    amount: Quantity | dict | None


class NutritionOrderOralDietTexture(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'modifier': 'CodeableConcept', 'foodType': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    modifier: CodeableConcept | dict | None
    foodType: CodeableConcept | dict | None


class NutritionOrderSupplement(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'schedule'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'schedule': 'Timing', 'quantity': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    productName: Optional[String] = None
    schedule: Timing | FHIRList[Timing] | list | dict
    quantity: Quantity | dict | None
    instruction: Optional[String] = None


class NutritionOrderEnteralFormula(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'administration'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'baseFormulaType': 'CodeableConcept',
        'additiveType': 'CodeableConcept',
        'caloricDensity': 'Quantity',
        'routeofAdministration': 'CodeableConcept',
        'administration': 'NutritionOrderEnteralFormulaAdministration',
        'maxVolumeToDeliver': 'Quantity',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    baseFormulaType: CodeableConcept | dict | None
    baseFormulaProductName: Optional[String] = None
    additiveType: CodeableConcept | dict | None
    additiveProductName: Optional[String] = None
    caloricDensity: Quantity | dict | None
    routeofAdministration: CodeableConcept | dict | None
    administration: NutritionOrderEnteralFormulaAdministration | FHIRList[NutritionOrderEnteralFormulaAdministration] | list | dict
    maxVolumeToDeliver: Quantity | dict | None
    administrationInstruction: Optional[String] = None


class NutritionOrderEnteralFormulaAdministration(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'schedule': 'Timing',
        'quantity': 'Quantity',
        'rateQuantity': 'Quantity',
        'rateRatio': 'Ratio',
    }
    _choice_fields = {'rate': ['rateQuantity', 'rateRatio']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    schedule: Timing | dict | None
    quantity: Quantity | dict | None
    rateQuantity: Quantity | dict | None
    rateRatio: Ratio | dict | None


class NutritionOrder(FHIRResource):
    _resource_type = "NutritionOrder"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'instantiatesCanonical',
        'instantiatesUri',
        'instantiates',
        'allergyIntolerance',
        'foodPreferenceModifier',
        'excludeFoodModifier',
        'supplement',
        'note',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'patient': 'Reference',
        'encounter': 'Reference',
        'orderer': 'Reference',
        'allergyIntolerance': 'Reference',
        'foodPreferenceModifier': 'CodeableConcept',
        'excludeFoodModifier': 'CodeableConcept',
        'oralDiet': 'NutritionOrderOralDiet',
        'supplement': 'NutritionOrderSupplement',
        'enteralFormula': 'NutritionOrderEnteralFormula',
        'note': 'Annotation',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    instantiatesCanonical: Canonical | FHIRList[Canonical] | list | None = None
    instantiatesUri: Uri | FHIRList[Uri] | list | None = None
    instantiates: Uri | FHIRList[Uri] | list | None = None
    status: Optional[Code] = None
    intent: Optional[Code] = None
    patient: Reference | dict | None
    encounter: Reference | dict | None
    dateTime: Optional[DateTime] = None
    orderer: Reference | dict | None
    allergyIntolerance: Reference | FHIRList[Reference] | list | dict
    foodPreferenceModifier: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    excludeFoodModifier: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    oralDiet: NutritionOrderOralDiet | dict | None
    supplement: NutritionOrderSupplement | FHIRList[NutritionOrderSupplement] | list | dict
    enteralFormula: NutritionOrderEnteralFormula | dict | None
    note: Annotation | FHIRList[Annotation] | list | dict


class ObservationReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'low': 'Quantity',
        'high': 'Quantity',
        'type_': 'CodeableConcept',
        'appliesTo': 'CodeableConcept',
        'age': 'Range',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    low: Quantity | dict | None
    high: Quantity | dict | None
    type_: CodeableConcept | dict | None
    appliesTo: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    age: Range | dict | None
    text: Optional[String] = None


class ObservationComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueCodeableConcept': 'CodeableConcept',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueSampledData': 'SampledData',
        'valuePeriod': 'Period',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
    }
    _choice_fields = {
        'value': [
            'valueQuantity',
            'valueCodeableConcept',
            'valueString',
            'valueBoolean',
            'valueInteger',
            'valueRange',
            'valueRatio',
            'valueSampledData',
            'valueTime',
            'valueDateTime',
            'valuePeriod',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueQuantity: Quantity | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueSampledData: SampledData | dict | None
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Period | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    referenceRange: Any = None


class Observation(FHIRResource):
    _resource_type = "Observation"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'basedOn',
        'partOf',
        'category',
        'focus',
        'performer',
        'interpretation',
        'note',
        'referenceRange',
        'hasMember',
        'derivedFrom',
        'component',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'focus': 'Reference',
        'encounter': 'Reference',
        'effectivePeriod': 'Period',
        'effectiveTiming': 'Timing',
        'performer': 'Reference',
        'valueQuantity': 'Quantity',
        'valueCodeableConcept': 'CodeableConcept',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueSampledData': 'SampledData',
        'valuePeriod': 'Period',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
        'note': 'Annotation',
        'bodySite': 'CodeableConcept',
        'method': 'CodeableConcept',
        'specimen': 'Reference',
        'device': 'Reference',
        'referenceRange': 'ObservationReferenceRange',
        'hasMember': 'Reference',
        'derivedFrom': 'Reference',
        'component': 'ObservationComponent',
    }
    _choice_fields = {
        'effective': ['effectiveDateTime', 'effectivePeriod', 'effectiveTiming', 'effectiveInstant'],
        'value': [
            'valueQuantity',
            'valueCodeableConcept',
            'valueString',
            'valueBoolean',
            'valueInteger',
            'valueRange',
            'valueRatio',
            'valueSampledData',
            'valueTime',
            'valueDateTime',
            'valuePeriod',
        ],
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    focus: Reference | FHIRList[Reference] | list | dict
    encounter: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    effectiveTiming: Timing | dict | None
    effectiveInstant: Optional[Instant] = None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference] | list | dict
    valueQuantity: Quantity | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueSampledData: SampledData | dict | None
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Period | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    bodySite: CodeableConcept | dict | None
    method: CodeableConcept | dict | None
    specimen: Reference | dict | None
    device: Reference | dict | None
    referenceRange: ObservationReferenceRange | FHIRList[ObservationReferenceRange] | list | dict
    hasMember: Reference | FHIRList[Reference] | list | dict
    derivedFrom: Reference | FHIRList[Reference] | list | dict
    component: ObservationComponent | FHIRList[ObservationComponent] | list | dict


class ObservationDefinitionQuantitativeDetails(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'customaryUnit': 'CodeableConcept', 'unit': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    customaryUnit: CodeableConcept | dict | None
    unit: CodeableConcept | dict | None
    conversionFactor: Optional[Decimal] = None
    decimalPrecision: Optional[Integer] = None


class ObservationDefinitionQualifiedInterval(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'range': 'Range',
        'context': 'CodeableConcept',
        'appliesTo': 'CodeableConcept',
        'age': 'Range',
        'gestationalAge': 'Range',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    category: Optional[Code] = None
    range: Range | dict | None
    context: CodeableConcept | dict | None
    appliesTo: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    gender: Optional[Code] = None
    age: Range | dict | None
    gestationalAge: Range | dict | None
    condition: Optional[String] = None


class ObservationDefinition(FHIRResource):
    _resource_type = "ObservationDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'category', 'identifier', 'permittedDataType', 'qualifiedInterval'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'identifier': 'Identifier',
        'method': 'CodeableConcept',
        'quantitativeDetails': 'ObservationDefinitionQuantitativeDetails',
        'qualifiedInterval': 'ObservationDefinitionQualifiedInterval',
        'validCodedValueSet': 'Reference',
        'normalCodedValueSet': 'Reference',
        'abnormalCodedValueSet': 'Reference',
        'criticalCodedValueSet': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    code: CodeableConcept | dict | None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    permittedDataType: Code | FHIRList[Code] | list | None = None
    multipleResultsAllowed: Optional[Boolean] = None
    method: CodeableConcept | dict | None
    preferredReportName: Optional[String] = None
    quantitativeDetails: ObservationDefinitionQuantitativeDetails | dict | None
    qualifiedInterval: ObservationDefinitionQualifiedInterval | FHIRList[ObservationDefinitionQualifiedInterval] | list | dict
    validCodedValueSet: Reference | dict | None
    normalCodedValueSet: Reference | dict | None
    abnormalCodedValueSet: Reference | dict | None
    criticalCodedValueSet: Reference | dict | None


class OperationDefinitionParameter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'targetProfile', 'referencedFrom', 'part'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'binding': 'OperationDefinitionParameterBinding',
        'referencedFrom': 'OperationDefinitionParameterReferencedFrom',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[Code] = None
    use: Optional[Code] = None
    min: Optional[Integer] = None
    max: Optional[String] = None
    documentation: Optional[String] = None
    type_: Optional[Code] = None
    targetProfile: Canonical | FHIRList[Canonical] | list | None = None
    searchType: Optional[Code] = None
    binding: OperationDefinitionParameterBinding | dict | None
    referencedFrom: OperationDefinitionParameterReferencedFrom | FHIRList[OperationDefinitionParameterReferencedFrom] | list | dict
    part: Any = None


class OperationDefinitionParameterBinding(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    strength: Optional[Code] = None
    valueSet: Optional[Canonical] = None


class OperationDefinitionParameterReferencedFrom(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    source: Optional[String] = None
    sourceId: Optional[String] = None


class OperationDefinitionOverload(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'parameterName'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    parameterName: String | FHIRList[String] | list | None = None
    comment: Optional[String] = None


class OperationDefinition(FHIRResource):
    _resource_type = "OperationDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'resource', 'parameter', 'overload'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'parameter': 'OperationDefinitionParameter',
        'overload': 'OperationDefinitionOverload',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    kind: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    affectsState: Optional[Boolean] = None
    code: Optional[Code] = None
    comment: Optional[Markdown] = None
    base: Optional[Canonical] = None
    resource: Code | FHIRList[Code] | list | None = None
    system: Optional[Boolean] = None
    type_: Optional[Boolean] = None
    instance: Optional[Boolean] = None
    inputProfile: Optional[Canonical] = None
    outputProfile: Optional[Canonical] = None
    parameter: OperationDefinitionParameter | FHIRList[OperationDefinitionParameter] | list | dict
    overload: OperationDefinitionOverload | FHIRList[OperationDefinitionOverload] | list | dict


class OperationOutcomeIssue(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'location', 'expression'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'details': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    severity: Optional[Code] = None
    code: Optional[Code] = None
    details: CodeableConcept | dict | None
    diagnostics: Optional[String] = None
    location: String | FHIRList[String] | list | None = None
    expression: String | FHIRList[String] | list | None = None


class OperationOutcome(FHIRResource):
    _resource_type = "OperationOutcome"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'issue'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'issue': 'OperationOutcomeIssue',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    issue: OperationOutcomeIssue | FHIRList[OperationOutcomeIssue] | list | dict


class OrganizationContact(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'telecom'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'purpose': 'CodeableConcept',
        'name': 'HumanName',
        'telecom': 'ContactPoint',
        'address': 'Address',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    purpose: CodeableConcept | dict | None
    name: HumanName | dict | None
    telecom: ContactPoint | FHIRList[ContactPoint] | list | dict
    address: Address | dict | None


class Organization(FHIRResource):
    _resource_type = "Organization"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'type_', 'alias', 'telecom', 'address', 'contact', 'endpoint'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'telecom': 'ContactPoint',
        'address': 'Address',
        'partOf': 'Reference',
        'contact': 'OrganizationContact',
        'endpoint': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    active: Optional[Boolean] = None
    type_: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    name: Optional[String] = None
    alias: String | FHIRList[String] | list | None = None
    telecom: ContactPoint | FHIRList[ContactPoint] | list | dict
    address: Address | FHIRList[Address] | list | dict
    partOf: Reference | dict | None
    contact: OrganizationContact | FHIRList[OrganizationContact] | list | dict
    endpoint: Reference | FHIRList[Reference] | list | dict


class OrganizationAffiliation(FHIRResource):
    _resource_type = "OrganizationAffiliation"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'network',
        'code',
        'specialty',
        'location',
        'healthcareService',
        'telecom',
        'endpoint',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'period': 'Period',
        'organization': 'Reference',
        'participatingOrganization': 'Reference',
        'network': 'Reference',
        'code': 'CodeableConcept',
        'specialty': 'CodeableConcept',
        'location': 'Reference',
        'healthcareService': 'Reference',
        'telecom': 'ContactPoint',
        'endpoint': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    active: Optional[Boolean] = None
    period: Period | dict | None
    organization: Reference | dict | None
    participatingOrganization: Reference | dict | None
    network: Reference | FHIRList[Reference] | list | dict
    code: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    specialty: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    location: Reference | FHIRList[Reference] | list | dict
    healthcareService: Reference | FHIRList[Reference] | list | dict
    telecom: ContactPoint | FHIRList[ContactPoint] | list | dict
    endpoint: Reference | FHIRList[Reference] | list | dict


class ParametersParameter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'part'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'valueAddress': 'Address',
        'valueAge': 'Age',
        'valueAnnotation': 'Annotation',
        'valueAttachment': 'Attachment',
        'valueCodeableConcept': 'CodeableConcept',
        'valueCoding': 'Coding',
        'valueContactPoint': 'ContactPoint',
        'valueCount': 'Count',
        'valueDistance': 'Distance',
        'valueDuration': 'Duration',
        'valueHumanName': 'HumanName',
        'valueIdentifier': 'Identifier',
        'valueMoney': 'Money',
        'valuePeriod': 'Period',
        'valueQuantity': 'Quantity',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueReference': 'Reference',
        'valueSampledData': 'SampledData',
        'valueSignature': 'Signature',
        'valueTiming': 'Timing',
        'valueContactDetail': 'ContactDetail',
        'valueContributor': 'Contributor',
        'valueDataRequirement': 'DataRequirement',
        'valueExpression': 'Expression',
        'valueParameterDefinition': 'ParameterDefinition',
        'valueRelatedArtifact': 'RelatedArtifact',
        'valueTriggerDefinition': 'TriggerDefinition',
        'valueUsageContext': 'UsageContext',
        'valueDosage': 'Dosage',
        'valueMeta': 'Meta',
        'resource': 'Resource',
    }
    _choice_fields = {
        'value': [
            'valueBase64Binary',
            'valueBoolean',
            'valueCanonical',
            'valueCode',
            'valueDate',
            'valueDateTime',
            'valueDecimal',
            'valueId',
            'valueInstant',
            'valueInteger',
            'valueMarkdown',
            'valueOid',
            'valuePositiveInt',
            'valueString',
            'valueTime',
            'valueUnsignedInt',
            'valueUri',
            'valueUrl',
            'valueUuid',
            'valueAddress',
            'valueAge',
            'valueAnnotation',
            'valueAttachment',
            'valueCodeableConcept',
            'valueCoding',
            'valueContactPoint',
            'valueCount',
            'valueDistance',
            'valueDuration',
            'valueHumanName',
            'valueIdentifier',
            'valueMoney',
            'valuePeriod',
            'valueQuantity',
            'valueRange',
            'valueRatio',
            'valueReference',
            'valueSampledData',
            'valueSignature',
            'valueTiming',
            'valueContactDetail',
            'valueContributor',
            'valueDataRequirement',
            'valueExpression',
            'valueParameterDefinition',
            'valueRelatedArtifact',
            'valueTriggerDefinition',
            'valueUsageContext',
            'valueDosage',
            'valueMeta',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
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
    valueAddress: Address | dict | None
    valueAge: Age | dict | None
    valueAnnotation: Annotation | dict | None
    valueAttachment: Attachment | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueCoding: Coding | dict | None
    valueContactPoint: ContactPoint | dict | None
    valueCount: Count | dict | None
    valueDistance: Distance | dict | None
    valueDuration: Duration | dict | None
    valueHumanName: HumanName | dict | None
    valueIdentifier: Identifier | dict | None
    valueMoney: Money | dict | None
    valuePeriod: Period | dict | None
    valueQuantity: Quantity | dict | None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueReference: Reference | dict | None
    valueSampledData: SampledData | dict | None
    valueSignature: Signature | dict | None
    valueTiming: Timing | dict | None
    valueContactDetail: ContactDetail | dict | None
    valueContributor: Contributor | dict | None
    valueDataRequirement: DataRequirement | dict | None
    valueExpression: Expression | dict | None
    valueParameterDefinition: ParameterDefinition | dict | None
    valueRelatedArtifact: RelatedArtifact | dict | None
    valueTriggerDefinition: TriggerDefinition | dict | None
    valueUsageContext: UsageContext | dict | None
    valueDosage: Dosage | dict | None
    valueMeta: Meta | dict | None
    resource: FHIRResource | dict | None
    part: Any = None


class Parameters(FHIRResource):
    _resource_type = "Parameters"
    _list_fields = {'parameter'}
    _field_types = {'meta': 'Meta', 'parameter': 'ParametersParameter'}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    parameter: ParametersParameter | FHIRList[ParametersParameter] | list | dict


class PatientContact(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'relationship', 'telecom'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'relationship': 'CodeableConcept',
        'name': 'HumanName',
        'telecom': 'ContactPoint',
        'address': 'Address',
        'organization': 'Reference',
        'period': 'Period',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    relationship: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    name: HumanName | dict | None
    telecom: ContactPoint | FHIRList[ContactPoint] | list | dict
    address: Address | dict | None
    gender: Optional[Code] = None
    organization: Reference | dict | None
    period: Period | dict | None


class PatientCommunication(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'language': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    language: CodeableConcept | dict | None
    preferred: Optional[Boolean] = None


class PatientLink(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'other': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    other: Reference | dict | None
    type_: Optional[Code] = None


class Patient(FHIRResource):
    _resource_type = "Patient"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'name',
        'telecom',
        'address',
        'photo',
        'contact',
        'communication',
        'generalPractitioner',
        'link',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'name': 'HumanName',
        'telecom': 'ContactPoint',
        'address': 'Address',
        'maritalStatus': 'CodeableConcept',
        'photo': 'Attachment',
        'contact': 'PatientContact',
        'communication': 'PatientCommunication',
        'generalPractitioner': 'Reference',
        'managingOrganization': 'Reference',
        'link': 'PatientLink',
    }
    _choice_fields = {'deceased': ['deceasedBoolean', 'deceasedDateTime'], 'multipleBirth': ['multipleBirthBoolean', 'multipleBirthInteger']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    active: Optional[Boolean] = None
    name: HumanName | FHIRList[HumanName] | list | dict
    telecom: ContactPoint | FHIRList[ContactPoint] | list | dict
    gender: Optional[Code] = None
    birthDate: Optional[Date] = None
    deceasedBoolean: Optional[Boolean] = None
    deceasedDateTime: Optional[DateTime] = None
    address: Address | FHIRList[Address] | list | dict
    maritalStatus: CodeableConcept | dict | None
    multipleBirthBoolean: Optional[Boolean] = None
    multipleBirthInteger: Optional[Integer] = None
    photo: Attachment | FHIRList[Attachment] | list | dict
    contact: PatientContact | FHIRList[PatientContact] | list | dict
    communication: PatientCommunication | FHIRList[PatientCommunication] | list | dict
    generalPractitioner: Reference | FHIRList[Reference] | list | dict
    managingOrganization: Reference | dict | None
    link: PatientLink | FHIRList[PatientLink] | list | dict


class PaymentNotice(FHIRResource):
    _resource_type = "PaymentNotice"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'request': 'Reference',
        'response': 'Reference',
        'provider': 'Reference',
        'payment': 'Reference',
        'payee': 'Reference',
        'recipient': 'Reference',
        'amount': 'Money',
        'paymentStatus': 'CodeableConcept',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    request: Reference | dict | None
    response: Reference | dict | None
    created: Optional[DateTime] = None
    provider: Reference | dict | None
    payment: Reference | dict | None
    paymentDate: Optional[Date] = None
    payee: Reference | dict | None
    recipient: Reference | dict | None
    amount: Money | dict | None
    paymentStatus: CodeableConcept | dict | None


class PaymentReconciliationDetail(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'predecessor': 'Identifier',
        'type_': 'CodeableConcept',
        'request': 'Reference',
        'submitter': 'Reference',
        'response': 'Reference',
        'responsible': 'Reference',
        'payee': 'Reference',
        'amount': 'Money',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | dict | None
    predecessor: Identifier | dict | None
    type_: CodeableConcept | dict | None
    request: Reference | dict | None
    submitter: Reference | dict | None
    response: Reference | dict | None
    date: Optional[Date] = None
    responsible: Reference | dict | None
    payee: Reference | dict | None
    amount: Money | dict | None


class PaymentReconciliationProcessNote(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    text: Optional[String] = None


class PaymentReconciliation(FHIRResource):
    _resource_type = "PaymentReconciliation"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'detail', 'processNote'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'period': 'Period',
        'paymentIssuer': 'Reference',
        'request': 'Reference',
        'requestor': 'Reference',
        'paymentAmount': 'Money',
        'paymentIdentifier': 'Identifier',
        'detail': 'PaymentReconciliationDetail',
        'formCode': 'CodeableConcept',
        'processNote': 'PaymentReconciliationProcessNote',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    period: Period | dict | None
    created: Optional[DateTime] = None
    paymentIssuer: Reference | dict | None
    request: Reference | dict | None
    requestor: Reference | dict | None
    outcome: Optional[Code] = None
    disposition: Optional[String] = None
    paymentDate: Optional[Date] = None
    paymentAmount: Money | dict | None
    paymentIdentifier: Identifier | dict | None
    detail: PaymentReconciliationDetail | FHIRList[PaymentReconciliationDetail] | list | dict
    formCode: CodeableConcept | dict | None
    processNote: PaymentReconciliationProcessNote | FHIRList[PaymentReconciliationProcessNote] | list | dict


class PersonLink(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'target': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    target: Reference | dict | None
    assurance: Optional[Code] = None


class Person(FHIRResource):
    _resource_type = "Person"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'name', 'telecom', 'address', 'link'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'name': 'HumanName',
        'telecom': 'ContactPoint',
        'address': 'Address',
        'photo': 'Attachment',
        'managingOrganization': 'Reference',
        'link': 'PersonLink',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    name: HumanName | FHIRList[HumanName] | list | dict
    telecom: ContactPoint | FHIRList[ContactPoint] | list | dict
    gender: Optional[Code] = None
    birthDate: Optional[Date] = None
    address: Address | FHIRList[Address] | list | dict
    photo: Attachment | dict | None
    managingOrganization: Reference | dict | None
    active: Optional[Boolean] = None
    link: PersonLink | FHIRList[PersonLink] | list | dict


class PlanDefinitionGoal(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'addresses', 'documentation', 'target'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'category': 'CodeableConcept',
        'description': 'CodeableConcept',
        'priority': 'CodeableConcept',
        'start': 'CodeableConcept',
        'addresses': 'CodeableConcept',
        'documentation': 'RelatedArtifact',
        'target': 'PlanDefinitionGoalTarget',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    category: CodeableConcept | dict | None
    description: CodeableConcept | dict | None
    priority: CodeableConcept | dict | None
    start: CodeableConcept | dict | None
    addresses: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    documentation: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    target: PlanDefinitionGoalTarget | FHIRList[PlanDefinitionGoalTarget] | list | dict


class PlanDefinitionGoalTarget(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'measure': 'CodeableConcept',
        'detailQuantity': 'Quantity',
        'detailRange': 'Range',
        'detailCodeableConcept': 'CodeableConcept',
        'due': 'Duration',
    }
    _choice_fields = {'detail': ['detailQuantity', 'detailRange', 'detailCodeableConcept']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    measure: CodeableConcept | dict | None
    detailQuantity: Quantity | dict | None
    detailRange: Range | dict | None
    detailCodeableConcept: CodeableConcept | dict | None
    due: Duration | dict | None


class PlanDefinitionAction(FHIRElement):
    _list_fields = {
        'extension',
        'modifierExtension',
        'code',
        'reason',
        'documentation',
        'goalId',
        'trigger',
        'condition',
        'input',
        'output',
        'relatedAction',
        'participant',
        'dynamicValue',
        'action',
    }
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'reason': 'CodeableConcept',
        'documentation': 'RelatedArtifact',
        'subjectCodeableConcept': 'CodeableConcept',
        'subjectReference': 'Reference',
        'trigger': 'TriggerDefinition',
        'condition': 'PlanDefinitionActionCondition',
        'input': 'DataRequirement',
        'output': 'DataRequirement',
        'relatedAction': 'PlanDefinitionActionRelatedAction',
        'timingAge': 'Age',
        'timingPeriod': 'Period',
        'timingDuration': 'Duration',
        'timingRange': 'Range',
        'timingTiming': 'Timing',
        'participant': 'PlanDefinitionActionParticipant',
        'type_': 'CodeableConcept',
        'dynamicValue': 'PlanDefinitionActionDynamicValue',
    }
    _choice_fields = {
        'definition': ['definitionCanonical', 'definitionUri'],
        'subject': ['subjectCodeableConcept', 'subjectReference'],
        'timing': ['timingDateTime', 'timingAge', 'timingPeriod', 'timingDuration', 'timingRange', 'timingTiming'],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    prefix: Optional[String] = None
    title: Optional[String] = None
    description: Optional[String] = None
    textEquivalent: Optional[String] = None
    priority: Optional[Code] = None
    code: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reason: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    documentation: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    goalId: Id | FHIRList[Id] | list | None = None
    subjectCodeableConcept: CodeableConcept | dict | None
    subjectReference: Reference | dict | None
    trigger: TriggerDefinition | FHIRList[TriggerDefinition] | list | dict
    condition: PlanDefinitionActionCondition | FHIRList[PlanDefinitionActionCondition] | list | dict
    input: DataRequirement | FHIRList[DataRequirement] | list | dict
    output: DataRequirement | FHIRList[DataRequirement] | list | dict
    relatedAction: PlanDefinitionActionRelatedAction | FHIRList[PlanDefinitionActionRelatedAction] | list | dict
    timingDateTime: Optional[DateTime] = None
    timingAge: Age | dict | None
    timingPeriod: Period | dict | None
    timingDuration: Duration | dict | None
    timingRange: Range | dict | None
    timingTiming: Timing | dict | None
    participant: PlanDefinitionActionParticipant | FHIRList[PlanDefinitionActionParticipant] | list | dict
    type_: CodeableConcept | dict | None
    groupingBehavior: Optional[Code] = None
    selectionBehavior: Optional[Code] = None
    requiredBehavior: Optional[Code] = None
    precheckBehavior: Optional[Code] = None
    cardinalityBehavior: Optional[Code] = None
    definitionCanonical: Optional[Canonical] = None
    definitionUri: Optional[Uri] = None
    transform: Optional[Canonical] = None
    dynamicValue: PlanDefinitionActionDynamicValue | FHIRList[PlanDefinitionActionDynamicValue] | list | dict
    action: Any = None


class PlanDefinitionActionCondition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    kind: Optional[Code] = None
    expression: Expression | dict | None


class PlanDefinitionActionRelatedAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'offsetDuration': 'Duration', 'offsetRange': 'Range'}
    _choice_fields = {'offset': ['offsetDuration', 'offsetRange']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    actionId: Optional[Id] = None
    relationship: Optional[Code] = None
    offsetDuration: Duration | dict | None
    offsetRange: Range | dict | None


class PlanDefinitionActionParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'role': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    role: CodeableConcept | dict | None


class PlanDefinitionActionDynamicValue(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    path: Optional[String] = None
    expression: Expression | dict | None


class PlanDefinition(FHIRResource):
    _resource_type = "PlanDefinition"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'contact',
        'useContext',
        'jurisdiction',
        'topic',
        'author',
        'editor',
        'reviewer',
        'endorser',
        'relatedArtifact',
        'library',
        'goal',
        'action',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'subjectCodeableConcept': 'CodeableConcept',
        'subjectReference': 'Reference',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'topic': 'CodeableConcept',
        'author': 'ContactDetail',
        'editor': 'ContactDetail',
        'reviewer': 'ContactDetail',
        'endorser': 'ContactDetail',
        'relatedArtifact': 'RelatedArtifact',
        'goal': 'PlanDefinitionGoal',
        'action': 'PlanDefinitionAction',
    }
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    type_: CodeableConcept | dict | None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    subjectCodeableConcept: CodeableConcept | dict | None
    subjectReference: Reference | dict | None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    topic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    author: ContactDetail | FHIRList[ContactDetail] | list | dict
    editor: ContactDetail | FHIRList[ContactDetail] | list | dict
    reviewer: ContactDetail | FHIRList[ContactDetail] | list | dict
    endorser: ContactDetail | FHIRList[ContactDetail] | list | dict
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    library: Canonical | FHIRList[Canonical] | list | None = None
    goal: PlanDefinitionGoal | FHIRList[PlanDefinitionGoal] | list | dict
    action: PlanDefinitionAction | FHIRList[PlanDefinitionAction] | list | dict


class PractitionerQualification(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'identifier'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'code': 'CodeableConcept',
        'period': 'Period',
        'issuer': 'Reference',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    code: CodeableConcept | dict | None
    period: Period | dict | None
    issuer: Reference | dict | None


class Practitioner(FHIRResource):
    _resource_type = "Practitioner"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'name', 'telecom', 'address', 'photo', 'qualification', 'communication'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'name': 'HumanName',
        'telecom': 'ContactPoint',
        'address': 'Address',
        'photo': 'Attachment',
        'qualification': 'PractitionerQualification',
        'communication': 'CodeableConcept',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    active: Optional[Boolean] = None
    name: HumanName | FHIRList[HumanName] | list | dict
    telecom: ContactPoint | FHIRList[ContactPoint] | list | dict
    address: Address | FHIRList[Address] | list | dict
    gender: Optional[Code] = None
    birthDate: Optional[Date] = None
    photo: Attachment | FHIRList[Attachment] | list | dict
    qualification: PractitionerQualification | FHIRList[PractitionerQualification] | list | dict
    communication: CodeableConcept | FHIRList[CodeableConcept] | list | dict


class PractitionerRoleAvailableTime(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'daysOfWeek'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    daysOfWeek: Code | FHIRList[Code] | list | None = None
    allDay: Optional[Boolean] = None
    availableStartTime: Optional[Time] = None
    availableEndTime: Optional[Time] = None


class PractitionerRoleNotAvailable(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'during': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    description: Optional[String] = None
    during: Period | dict | None


class PractitionerRole(FHIRResource):
    _resource_type = "PractitionerRole"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'code',
        'specialty',
        'location',
        'healthcareService',
        'telecom',
        'availableTime',
        'notAvailable',
        'endpoint',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'period': 'Period',
        'practitioner': 'Reference',
        'organization': 'Reference',
        'code': 'CodeableConcept',
        'specialty': 'CodeableConcept',
        'location': 'Reference',
        'healthcareService': 'Reference',
        'telecom': 'ContactPoint',
        'availableTime': 'PractitionerRoleAvailableTime',
        'notAvailable': 'PractitionerRoleNotAvailable',
        'endpoint': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    active: Optional[Boolean] = None
    period: Period | dict | None
    practitioner: Reference | dict | None
    organization: Reference | dict | None
    code: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    specialty: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    location: Reference | FHIRList[Reference] | list | dict
    healthcareService: Reference | FHIRList[Reference] | list | dict
    telecom: ContactPoint | FHIRList[ContactPoint] | list | dict
    availableTime: PractitionerRoleAvailableTime | FHIRList[PractitionerRoleAvailableTime] | list | dict
    notAvailable: PractitionerRoleNotAvailable | FHIRList[PractitionerRoleNotAvailable] | list | dict
    availabilityExceptions: Optional[String] = None
    endpoint: Reference | FHIRList[Reference] | list | dict


class ProcedurePerformer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'function': 'CodeableConcept', 'actor': 'Reference', 'onBehalfOf': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    function: CodeableConcept | dict | None
    actor: Reference | dict | None
    onBehalfOf: Reference | dict | None


class ProcedureFocalDevice(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'action': 'CodeableConcept', 'manipulated': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    action: CodeableConcept | dict | None
    manipulated: Reference | dict | None


class Procedure(FHIRResource):
    _resource_type = "Procedure"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'instantiatesCanonical',
        'instantiatesUri',
        'basedOn',
        'partOf',
        'performer',
        'reasonCode',
        'reasonReference',
        'bodySite',
        'report',
        'complication',
        'complicationDetail',
        'followUp',
        'note',
        'focalDevice',
        'usedReference',
        'usedCode',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'statusReason': 'CodeableConcept',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'encounter': 'Reference',
        'performedPeriod': 'Period',
        'performedAge': 'Age',
        'performedRange': 'Range',
        'recorder': 'Reference',
        'asserter': 'Reference',
        'performer': 'ProcedurePerformer',
        'location': 'Reference',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'bodySite': 'CodeableConcept',
        'outcome': 'CodeableConcept',
        'report': 'Reference',
        'complication': 'CodeableConcept',
        'complicationDetail': 'Reference',
        'followUp': 'CodeableConcept',
        'note': 'Annotation',
        'focalDevice': 'ProcedureFocalDevice',
        'usedReference': 'Reference',
        'usedCode': 'CodeableConcept',
    }
    _choice_fields = {'performed': ['performedDateTime', 'performedPeriod', 'performedString', 'performedAge', 'performedRange']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    instantiatesCanonical: Canonical | FHIRList[Canonical] | list | None = None
    instantiatesUri: Uri | FHIRList[Uri] | list | None = None
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    statusReason: CodeableConcept | dict | None
    category: CodeableConcept | dict | None
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    encounter: Reference | dict | None
    performedDateTime: Optional[DateTime] = None
    performedPeriod: Period | dict | None
    performedString: Optional[String] = None
    performedAge: Age | dict | None
    performedRange: Range | dict | None
    recorder: Reference | dict | None
    asserter: Reference | dict | None
    performer: ProcedurePerformer | FHIRList[ProcedurePerformer] | list | dict
    location: Reference | dict | None
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    bodySite: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    outcome: CodeableConcept | dict | None
    report: Reference | FHIRList[Reference] | list | dict
    complication: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    complicationDetail: Reference | FHIRList[Reference] | list | dict
    followUp: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    focalDevice: ProcedureFocalDevice | FHIRList[ProcedureFocalDevice] | list | dict
    usedReference: Reference | FHIRList[Reference] | list | dict
    usedCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict


class ProvenanceAgent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'role'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'role': 'CodeableConcept',
        'who': 'Reference',
        'onBehalfOf': 'Reference',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    role: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    who: Reference | dict | None
    onBehalfOf: Reference | dict | None


class ProvenanceEntity(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'agent'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'what': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    role: Optional[Code] = None
    what: Reference | dict | None
    agent: Any = None


class Provenance(FHIRResource):
    _resource_type = "Provenance"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'target', 'policy', 'reason', 'agent', 'entity', 'signature'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'target': 'Reference',
        'occurredPeriod': 'Period',
        'location': 'Reference',
        'reason': 'CodeableConcept',
        'activity': 'CodeableConcept',
        'agent': 'ProvenanceAgent',
        'entity': 'ProvenanceEntity',
        'signature': 'Signature',
    }
    _choice_fields = {'occurred': ['occurredPeriod', 'occurredDateTime']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    target: Reference | FHIRList[Reference] | list | dict
    occurredPeriod: Period | dict | None
    occurredDateTime: Optional[DateTime] = None
    recorded: Optional[Instant] = None
    policy: Uri | FHIRList[Uri] | list | None = None
    location: Reference | dict | None
    reason: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    activity: CodeableConcept | dict | None
    agent: ProvenanceAgent | FHIRList[ProvenanceAgent] | list | dict
    entity: ProvenanceEntity | FHIRList[ProvenanceEntity] | list | dict
    signature: Signature | FHIRList[Signature] | list | dict


class QuestionnaireItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'enableWhen', 'answerOption', 'initial', 'item'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'Coding',
        'enableWhen': 'QuestionnaireItemEnableWhen',
        'answerOption': 'QuestionnaireItemAnswerOption',
        'initial': 'QuestionnaireItemInitial',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    linkId: Optional[String] = None
    definition: Optional[Uri] = None
    code: Coding | FHIRList[Coding] | list | dict
    prefix: Optional[String] = None
    text: Optional[String] = None
    type_: Optional[Code] = None
    enableWhen: QuestionnaireItemEnableWhen | FHIRList[QuestionnaireItemEnableWhen] | list | dict
    enableBehavior: Optional[Code] = None
    required: Optional[Boolean] = None
    repeats: Optional[Boolean] = None
    readOnly: Optional[Boolean] = None
    maxLength: Optional[Integer] = None
    answerValueSet: Optional[Canonical] = None
    answerOption: QuestionnaireItemAnswerOption | FHIRList[QuestionnaireItemAnswerOption] | list | dict
    initial: QuestionnaireItemInitial | FHIRList[QuestionnaireItemInitial] | list | dict
    item: Any = None


class QuestionnaireItemEnableWhen(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'answerCoding': 'Coding',
        'answerQuantity': 'Quantity',
        'answerReference': 'Reference',
    }
    _choice_fields = {
        'answer': [
            'answerBoolean',
            'answerDecimal',
            'answerInteger',
            'answerDate',
            'answerDateTime',
            'answerTime',
            'answerString',
            'answerCoding',
            'answerQuantity',
            'answerReference',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    question: Optional[String] = None
    operator: Optional[Code] = None
    answerBoolean: Optional[Boolean] = None
    answerDecimal: Optional[Decimal] = None
    answerInteger: Optional[Integer] = None
    answerDate: Optional[Date] = None
    answerDateTime: Optional[DateTime] = None
    answerTime: Optional[Time] = None
    answerString: Optional[String] = None
    answerCoding: Coding | dict | None
    answerQuantity: Quantity | dict | None
    answerReference: Reference | dict | None


class QuestionnaireItemAnswerOption(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'valueCoding': 'Coding', 'valueReference': 'Reference'}
    _choice_fields = {'value': ['valueInteger', 'valueDate', 'valueTime', 'valueString', 'valueCoding', 'valueReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    valueInteger: Optional[Integer] = None
    valueDate: Optional[Date] = None
    valueTime: Optional[Time] = None
    valueString: Optional[String] = None
    valueCoding: Coding | dict | None
    valueReference: Reference | dict | None
    initialSelected: Optional[Boolean] = None


class QuestionnaireItemInitial(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'valueAttachment': 'Attachment',
        'valueCoding': 'Coding',
        'valueQuantity': 'Quantity',
        'valueReference': 'Reference',
    }
    _choice_fields = {
        'value': [
            'valueBoolean',
            'valueDecimal',
            'valueInteger',
            'valueDate',
            'valueDateTime',
            'valueTime',
            'valueString',
            'valueUri',
            'valueAttachment',
            'valueCoding',
            'valueQuantity',
            'valueReference',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    valueBoolean: Optional[Boolean] = None
    valueDecimal: Optional[Decimal] = None
    valueInteger: Optional[Integer] = None
    valueDate: Optional[Date] = None
    valueDateTime: Optional[DateTime] = None
    valueTime: Optional[Time] = None
    valueString: Optional[String] = None
    valueUri: Optional[Uri] = None
    valueAttachment: Attachment | dict | None
    valueCoding: Coding | dict | None
    valueQuantity: Quantity | dict | None
    valueReference: Reference | dict | None


class Questionnaire(FHIRResource):
    _resource_type = "Questionnaire"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'derivedFrom',
        'subjectType',
        'contact',
        'useContext',
        'jurisdiction',
        'code',
        'item',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'code': 'Coding',
        'item': 'QuestionnaireItem',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    derivedFrom: Canonical | FHIRList[Canonical] | list | None = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    subjectType: Code | FHIRList[Code] | list | None = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    code: Coding | FHIRList[Coding] | list | dict
    item: QuestionnaireItem | FHIRList[QuestionnaireItem] | list | dict


class QuestionnaireResponseItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'answer', 'item'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'answer': 'QuestionnaireResponseItemAnswer'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    linkId: Optional[String] = None
    definition: Optional[Uri] = None
    text: Optional[String] = None
    answer: QuestionnaireResponseItemAnswer | FHIRList[QuestionnaireResponseItemAnswer] | list | dict
    item: Any = None


class QuestionnaireResponseItemAnswer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'item'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'valueAttachment': 'Attachment',
        'valueCoding': 'Coding',
        'valueQuantity': 'Quantity',
        'valueReference': 'Reference',
    }
    _choice_fields = {
        'value': [
            'valueBoolean',
            'valueDecimal',
            'valueInteger',
            'valueDate',
            'valueDateTime',
            'valueTime',
            'valueString',
            'valueUri',
            'valueAttachment',
            'valueCoding',
            'valueQuantity',
            'valueReference',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    valueBoolean: Optional[Boolean] = None
    valueDecimal: Optional[Decimal] = None
    valueInteger: Optional[Integer] = None
    valueDate: Optional[Date] = None
    valueDateTime: Optional[DateTime] = None
    valueTime: Optional[Time] = None
    valueString: Optional[String] = None
    valueUri: Optional[Uri] = None
    valueAttachment: Attachment | dict | None
    valueCoding: Coding | dict | None
    valueQuantity: Quantity | dict | None
    valueReference: Reference | dict | None
    item: Any = None


class QuestionnaireResponse(FHIRResource):
    _resource_type = "QuestionnaireResponse"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'basedOn', 'partOf', 'item'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'subject': 'Reference',
        'encounter': 'Reference',
        'author': 'Reference',
        'source': 'Reference',
        'item': 'QuestionnaireResponseItem',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | dict | None
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    questionnaire: Optional[Canonical] = None
    status: Optional[Code] = None
    subject: Reference | dict | None
    encounter: Reference | dict | None
    authored: Optional[DateTime] = None
    author: Reference | dict | None
    source: Reference | dict | None
    item: QuestionnaireResponseItem | FHIRList[QuestionnaireResponseItem] | list | dict


class RelatedPersonCommunication(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'language': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    language: CodeableConcept | dict | None
    preferred: Optional[Boolean] = None


class RelatedPerson(FHIRResource):
    _resource_type = "RelatedPerson"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'relationship', 'name', 'telecom', 'address', 'photo', 'communication'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'patient': 'Reference',
        'relationship': 'CodeableConcept',
        'name': 'HumanName',
        'telecom': 'ContactPoint',
        'address': 'Address',
        'photo': 'Attachment',
        'period': 'Period',
        'communication': 'RelatedPersonCommunication',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    active: Optional[Boolean] = None
    patient: Reference | dict | None
    relationship: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    name: HumanName | FHIRList[HumanName] | list | dict
    telecom: ContactPoint | FHIRList[ContactPoint] | list | dict
    gender: Optional[Code] = None
    birthDate: Optional[Date] = None
    address: Address | FHIRList[Address] | list | dict
    photo: Attachment | FHIRList[Attachment] | list | dict
    period: Period | dict | None
    communication: RelatedPersonCommunication | FHIRList[RelatedPersonCommunication] | list | dict


class RequestGroupAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'documentation', 'condition', 'relatedAction', 'participant', 'action'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'documentation': 'RelatedArtifact',
        'condition': 'RequestGroupActionCondition',
        'relatedAction': 'RequestGroupActionRelatedAction',
        'timingAge': 'Age',
        'timingPeriod': 'Period',
        'timingDuration': 'Duration',
        'timingRange': 'Range',
        'timingTiming': 'Timing',
        'participant': 'Reference',
        'type_': 'CodeableConcept',
        'resource': 'Reference',
    }
    _choice_fields = {'timing': ['timingDateTime', 'timingAge', 'timingPeriod', 'timingDuration', 'timingRange', 'timingTiming']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    prefix: Optional[String] = None
    title: Optional[String] = None
    description: Optional[String] = None
    textEquivalent: Optional[String] = None
    priority: Optional[Code] = None
    code: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    documentation: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    condition: RequestGroupActionCondition | FHIRList[RequestGroupActionCondition] | list | dict
    relatedAction: RequestGroupActionRelatedAction | FHIRList[RequestGroupActionRelatedAction] | list | dict
    timingDateTime: Optional[DateTime] = None
    timingAge: Age | dict | None
    timingPeriod: Period | dict | None
    timingDuration: Duration | dict | None
    timingRange: Range | dict | None
    timingTiming: Timing | dict | None
    participant: Reference | FHIRList[Reference] | list | dict
    type_: CodeableConcept | dict | None
    groupingBehavior: Optional[Code] = None
    selectionBehavior: Optional[Code] = None
    requiredBehavior: Optional[Code] = None
    precheckBehavior: Optional[Code] = None
    cardinalityBehavior: Optional[Code] = None
    resource: Reference | dict | None
    action: Any = None


class RequestGroupActionCondition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    kind: Optional[Code] = None
    expression: Expression | dict | None


class RequestGroupActionRelatedAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'offsetDuration': 'Duration', 'offsetRange': 'Range'}
    _choice_fields = {'offset': ['offsetDuration', 'offsetRange']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    actionId: Optional[Id] = None
    relationship: Optional[Code] = None
    offsetDuration: Duration | dict | None
    offsetRange: Range | dict | None


class RequestGroup(FHIRResource):
    _resource_type = "RequestGroup"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'instantiatesCanonical',
        'instantiatesUri',
        'basedOn',
        'replaces',
        'reasonCode',
        'reasonReference',
        'note',
        'action',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'replaces': 'Reference',
        'groupIdentifier': 'Identifier',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'encounter': 'Reference',
        'author': 'Reference',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'note': 'Annotation',
        'action': 'RequestGroupAction',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    instantiatesCanonical: Canonical | FHIRList[Canonical] | list | None = None
    instantiatesUri: Uri | FHIRList[Uri] | list | None = None
    basedOn: Reference | FHIRList[Reference] | list | dict
    replaces: Reference | FHIRList[Reference] | list | dict
    groupIdentifier: Identifier | dict | None
    status: Optional[Code] = None
    intent: Optional[Code] = None
    priority: Optional[Code] = None
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    encounter: Reference | dict | None
    authoredOn: Optional[DateTime] = None
    author: Reference | dict | None
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    action: RequestGroupAction | FHIRList[RequestGroupAction] | list | dict


class ResearchDefinition(FHIRResource):
    _resource_type = "ResearchDefinition"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'contact',
        'comment',
        'useContext',
        'jurisdiction',
        'topic',
        'author',
        'editor',
        'reviewer',
        'endorser',
        'relatedArtifact',
        'library',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'subjectCodeableConcept': 'CodeableConcept',
        'subjectReference': 'Reference',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'topic': 'CodeableConcept',
        'author': 'ContactDetail',
        'editor': 'ContactDetail',
        'reviewer': 'ContactDetail',
        'endorser': 'ContactDetail',
        'relatedArtifact': 'RelatedArtifact',
        'population': 'Reference',
        'exposure': 'Reference',
        'exposureAlternative': 'Reference',
        'outcome': 'Reference',
    }
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    shortTitle: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    subjectCodeableConcept: CodeableConcept | dict | None
    subjectReference: Reference | dict | None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    comment: String | FHIRList[String] | list | None = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    topic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    author: ContactDetail | FHIRList[ContactDetail] | list | dict
    editor: ContactDetail | FHIRList[ContactDetail] | list | dict
    reviewer: ContactDetail | FHIRList[ContactDetail] | list | dict
    endorser: ContactDetail | FHIRList[ContactDetail] | list | dict
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    library: Canonical | FHIRList[Canonical] | list | None = None
    population: Reference | dict | None
    exposure: Reference | dict | None
    exposureAlternative: Reference | dict | None
    outcome: Reference | dict | None


class ResearchElementDefinitionCharacteristic(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'usageContext'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'definitionCodeableConcept': 'CodeableConcept',
        'definitionExpression': 'Expression',
        'definitionDataRequirement': 'DataRequirement',
        'usageContext': 'UsageContext',
        'unitOfMeasure': 'CodeableConcept',
        'studyEffectivePeriod': 'Period',
        'studyEffectiveDuration': 'Duration',
        'studyEffectiveTiming': 'Timing',
        'studyEffectiveTimeFromStart': 'Duration',
        'participantEffectivePeriod': 'Period',
        'participantEffectiveDuration': 'Duration',
        'participantEffectiveTiming': 'Timing',
        'participantEffectiveTimeFromStart': 'Duration',
    }
    _choice_fields = {
        'definition': ['definitionCodeableConcept', 'definitionCanonical', 'definitionExpression', 'definitionDataRequirement'],
        'participantEffective': ['participantEffectiveDateTime', 'participantEffectivePeriod', 'participantEffectiveDuration', 'participantEffectiveTiming'],
        'studyEffective': ['studyEffectiveDateTime', 'studyEffectivePeriod', 'studyEffectiveDuration', 'studyEffectiveTiming'],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    definitionCodeableConcept: CodeableConcept | dict | None
    definitionCanonical: Optional[Canonical] = None
    definitionExpression: Expression | dict | None
    definitionDataRequirement: DataRequirement | dict | None
    usageContext: UsageContext | FHIRList[UsageContext] | list | dict
    exclude: Optional[Boolean] = None
    unitOfMeasure: CodeableConcept | dict | None
    studyEffectiveDescription: Optional[String] = None
    studyEffectiveDateTime: Optional[DateTime] = None
    studyEffectivePeriod: Period | dict | None
    studyEffectiveDuration: Duration | dict | None
    studyEffectiveTiming: Timing | dict | None
    studyEffectiveTimeFromStart: Duration | dict | None
    studyEffectiveGroupMeasure: Optional[Code] = None
    participantEffectiveDescription: Optional[String] = None
    participantEffectiveDateTime: Optional[DateTime] = None
    participantEffectivePeriod: Period | dict | None
    participantEffectiveDuration: Duration | dict | None
    participantEffectiveTiming: Timing | dict | None
    participantEffectiveTimeFromStart: Duration | dict | None
    participantEffectiveGroupMeasure: Optional[Code] = None


class ResearchElementDefinition(FHIRResource):
    _resource_type = "ResearchElementDefinition"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'contact',
        'comment',
        'useContext',
        'jurisdiction',
        'topic',
        'author',
        'editor',
        'reviewer',
        'endorser',
        'relatedArtifact',
        'library',
        'characteristic',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'subjectCodeableConcept': 'CodeableConcept',
        'subjectReference': 'Reference',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'topic': 'CodeableConcept',
        'author': 'ContactDetail',
        'editor': 'ContactDetail',
        'reviewer': 'ContactDetail',
        'endorser': 'ContactDetail',
        'relatedArtifact': 'RelatedArtifact',
        'characteristic': 'ResearchElementDefinitionCharacteristic',
    }
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    shortTitle: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    subjectCodeableConcept: CodeableConcept | dict | None
    subjectReference: Reference | dict | None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    comment: String | FHIRList[String] | list | None = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    topic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    author: ContactDetail | FHIRList[ContactDetail] | list | dict
    editor: ContactDetail | FHIRList[ContactDetail] | list | dict
    reviewer: ContactDetail | FHIRList[ContactDetail] | list | dict
    endorser: ContactDetail | FHIRList[ContactDetail] | list | dict
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    library: Canonical | FHIRList[Canonical] | list | None = None
    type_: Optional[Code] = None
    variableType: Optional[Code] = None
    characteristic: ResearchElementDefinitionCharacteristic | FHIRList[ResearchElementDefinitionCharacteristic] | list | dict


class ResearchStudyArm(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[String] = None
    type_: CodeableConcept | dict | None
    description: Optional[String] = None


class ResearchStudyObjective(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[String] = None
    type_: CodeableConcept | dict | None


class ResearchStudy(FHIRResource):
    _resource_type = "ResearchStudy"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'protocol',
        'partOf',
        'category',
        'focus',
        'condition',
        'contact',
        'relatedArtifact',
        'keyword',
        'location',
        'enrollment',
        'site',
        'note',
        'arm',
        'objective',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'protocol': 'Reference',
        'partOf': 'Reference',
        'primaryPurposeType': 'CodeableConcept',
        'phase': 'CodeableConcept',
        'category': 'CodeableConcept',
        'focus': 'CodeableConcept',
        'condition': 'CodeableConcept',
        'contact': 'ContactDetail',
        'relatedArtifact': 'RelatedArtifact',
        'keyword': 'CodeableConcept',
        'location': 'CodeableConcept',
        'enrollment': 'Reference',
        'period': 'Period',
        'sponsor': 'Reference',
        'principalInvestigator': 'Reference',
        'site': 'Reference',
        'reasonStopped': 'CodeableConcept',
        'note': 'Annotation',
        'arm': 'ResearchStudyArm',
        'objective': 'ResearchStudyObjective',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    title: Optional[String] = None
    protocol: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    primaryPurposeType: CodeableConcept | dict | None
    phase: CodeableConcept | dict | None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    focus: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    condition: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    keyword: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    location: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    description: Optional[Markdown] = None
    enrollment: Reference | FHIRList[Reference] | list | dict
    period: Period | dict | None
    sponsor: Reference | dict | None
    principalInvestigator: Reference | dict | None
    site: Reference | FHIRList[Reference] | list | dict
    reasonStopped: CodeableConcept | dict | None
    note: Annotation | FHIRList[Annotation] | list | dict
    arm: ResearchStudyArm | FHIRList[ResearchStudyArm] | list | dict
    objective: ResearchStudyObjective | FHIRList[ResearchStudyObjective] | list | dict


class ResearchSubject(FHIRResource):
    _resource_type = "ResearchSubject"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'period': 'Period',
        'study': 'Reference',
        'individual': 'Reference',
        'consent': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    period: Period | dict | None
    study: Reference | dict | None
    individual: Reference | dict | None
    assignedArm: Optional[String] = None
    actualArm: Optional[String] = None
    consent: Reference | dict | None


class RiskAssessmentPrediction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'outcome': 'CodeableConcept',
        'probabilityRange': 'Range',
        'qualitativeRisk': 'CodeableConcept',
        'whenPeriod': 'Period',
        'whenRange': 'Range',
    }
    _choice_fields = {'probability': ['probabilityDecimal', 'probabilityRange'], 'when': ['whenPeriod', 'whenRange']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    outcome: CodeableConcept | dict | None
    probabilityDecimal: Optional[Decimal] = None
    probabilityRange: Range | dict | None
    qualitativeRisk: CodeableConcept | dict | None
    relativeRisk: Optional[Decimal] = None
    whenPeriod: Period | dict | None
    whenRange: Range | dict | None
    rationale: Optional[String] = None


class RiskAssessment(FHIRResource):
    _resource_type = "RiskAssessment"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'reasonCode', 'reasonReference', 'basis', 'prediction', 'note'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'parent': 'Reference',
        'method': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'encounter': 'Reference',
        'occurrencePeriod': 'Period',
        'condition': 'Reference',
        'performer': 'Reference',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'basis': 'Reference',
        'prediction': 'RiskAssessmentPrediction',
        'note': 'Annotation',
    }
    _choice_fields = {'occurrence': ['occurrenceDateTime', 'occurrencePeriod']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | dict | None
    parent: Reference | dict | None
    status: Optional[Code] = None
    method: CodeableConcept | dict | None
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    encounter: Reference | dict | None
    occurrenceDateTime: Optional[DateTime] = None
    occurrencePeriod: Period | dict | None
    condition: Reference | dict | None
    performer: Reference | dict | None
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    basis: Reference | FHIRList[Reference] | list | dict
    prediction: RiskAssessmentPrediction | FHIRList[RiskAssessmentPrediction] | list | dict
    mitigation: Optional[String] = None
    note: Annotation | FHIRList[Annotation] | list | dict


class RiskEvidenceSynthesisSampleSize(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    description: Optional[String] = None
    numberOfStudies: Optional[Integer] = None
    numberOfParticipants: Optional[Integer] = None


class RiskEvidenceSynthesisRiskEstimate(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'precisionEstimate'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'unitOfMeasure': 'CodeableConcept',
        'precisionEstimate': 'RiskEvidenceSynthesisRiskEstimatePrecisionEstimate',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    description: Optional[String] = None
    type_: CodeableConcept | dict | None
    value: Optional[Decimal] = None
    unitOfMeasure: CodeableConcept | dict | None
    denominatorCount: Optional[Integer] = None
    numeratorCount: Optional[Integer] = None
    precisionEstimate: RiskEvidenceSynthesisRiskEstimatePrecisionEstimate | FHIRList[RiskEvidenceSynthesisRiskEstimatePrecisionEstimate] | list | dict


class RiskEvidenceSynthesisRiskEstimatePrecisionEstimate(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    level: Optional[Decimal] = None
    from_: Optional[Decimal] = None
    to: Optional[Decimal] = None


class RiskEvidenceSynthesisCertainty(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'rating', 'note', 'certaintySubcomponent'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'rating': 'CodeableConcept',
        'note': 'Annotation',
        'certaintySubcomponent': 'RiskEvidenceSynthesisCertaintyCertaintySubcomponent',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    rating: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    certaintySubcomponent: RiskEvidenceSynthesisCertaintyCertaintySubcomponent | FHIRList[RiskEvidenceSynthesisCertaintyCertaintySubcomponent] | list | dict


class RiskEvidenceSynthesisCertaintyCertaintySubcomponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'rating', 'note'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'rating': 'CodeableConcept', 'note': 'Annotation'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    rating: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict


class RiskEvidenceSynthesis(FHIRResource):
    _resource_type = "RiskEvidenceSynthesis"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'contact',
        'note',
        'useContext',
        'jurisdiction',
        'topic',
        'author',
        'editor',
        'reviewer',
        'endorser',
        'relatedArtifact',
        'certainty',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'contact': 'ContactDetail',
        'note': 'Annotation',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'topic': 'CodeableConcept',
        'author': 'ContactDetail',
        'editor': 'ContactDetail',
        'reviewer': 'ContactDetail',
        'endorser': 'ContactDetail',
        'relatedArtifact': 'RelatedArtifact',
        'synthesisType': 'CodeableConcept',
        'studyType': 'CodeableConcept',
        'population': 'Reference',
        'exposure': 'Reference',
        'outcome': 'Reference',
        'sampleSize': 'RiskEvidenceSynthesisSampleSize',
        'riskEstimate': 'RiskEvidenceSynthesisRiskEstimate',
        'certainty': 'RiskEvidenceSynthesisCertainty',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    note: Annotation | FHIRList[Annotation] | list | dict
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    topic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    author: ContactDetail | FHIRList[ContactDetail] | list | dict
    editor: ContactDetail | FHIRList[ContactDetail] | list | dict
    reviewer: ContactDetail | FHIRList[ContactDetail] | list | dict
    endorser: ContactDetail | FHIRList[ContactDetail] | list | dict
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    synthesisType: CodeableConcept | dict | None
    studyType: CodeableConcept | dict | None
    population: Reference | dict | None
    exposure: Reference | dict | None
    outcome: Reference | dict | None
    sampleSize: RiskEvidenceSynthesisSampleSize | dict | None
    riskEstimate: RiskEvidenceSynthesisRiskEstimate | dict | None
    certainty: RiskEvidenceSynthesisCertainty | FHIRList[RiskEvidenceSynthesisCertainty] | list | dict


class Schedule(FHIRResource):
    _resource_type = "Schedule"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'serviceCategory', 'serviceType', 'specialty', 'actor'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'serviceCategory': 'CodeableConcept',
        'serviceType': 'CodeableConcept',
        'specialty': 'CodeableConcept',
        'actor': 'Reference',
        'planningHorizon': 'Period',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    active: Optional[Boolean] = None
    serviceCategory: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    serviceType: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    specialty: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    actor: Reference | FHIRList[Reference] | list | dict
    planningHorizon: Period | dict | None
    comment: Optional[String] = None


class SearchParameterComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    definition: Optional[Canonical] = None
    expression: Optional[String] = None


class SearchParameter(FHIRResource):
    _resource_type = "SearchParameter"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'contact',
        'useContext',
        'jurisdiction',
        'base',
        'target',
        'comparator',
        'modifier',
        'chain',
        'component',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'component': 'SearchParameterComponent',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    version: Optional[String] = None
    name: Optional[String] = None
    derivedFrom: Optional[Canonical] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    code: Optional[Code] = None
    base: Code | FHIRList[Code] | list | None = None
    type_: Optional[Code] = None
    expression: Optional[String] = None
    xpath: Optional[String] = None
    xpathUsage: Optional[Code] = None
    target: Code | FHIRList[Code] | list | None = None
    multipleOr: Optional[Boolean] = None
    multipleAnd: Optional[Boolean] = None
    comparator: Code | FHIRList[Code] | list | None = None
    modifier: Code | FHIRList[Code] | list | None = None
    chain: String | FHIRList[String] | list | None = None
    component: SearchParameterComponent | FHIRList[SearchParameterComponent] | list | dict


class ServiceRequest(FHIRResource):
    _resource_type = "ServiceRequest"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'instantiatesCanonical',
        'instantiatesUri',
        'basedOn',
        'replaces',
        'category',
        'orderDetail',
        'performer',
        'locationCode',
        'locationReference',
        'reasonCode',
        'reasonReference',
        'insurance',
        'supportingInfo',
        'specimen',
        'bodySite',
        'note',
        'relevantHistory',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'replaces': 'Reference',
        'requisition': 'Identifier',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'orderDetail': 'CodeableConcept',
        'quantityQuantity': 'Quantity',
        'quantityRatio': 'Ratio',
        'quantityRange': 'Range',
        'subject': 'Reference',
        'encounter': 'Reference',
        'occurrencePeriod': 'Period',
        'occurrenceTiming': 'Timing',
        'asNeededCodeableConcept': 'CodeableConcept',
        'requester': 'Reference',
        'performerType': 'CodeableConcept',
        'performer': 'Reference',
        'locationCode': 'CodeableConcept',
        'locationReference': 'Reference',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'insurance': 'Reference',
        'supportingInfo': 'Reference',
        'specimen': 'Reference',
        'bodySite': 'CodeableConcept',
        'note': 'Annotation',
        'relevantHistory': 'Reference',
    }
    _choice_fields = {
        'asNeeded': ['asNeededBoolean', 'asNeededCodeableConcept'],
        'occurrence': ['occurrenceDateTime', 'occurrencePeriod', 'occurrenceTiming'],
        'quantity': ['quantityQuantity', 'quantityRatio', 'quantityRange'],
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    instantiatesCanonical: Canonical | FHIRList[Canonical] | list | None = None
    instantiatesUri: Uri | FHIRList[Uri] | list | None = None
    basedOn: Reference | FHIRList[Reference] | list | dict
    replaces: Reference | FHIRList[Reference] | list | dict
    requisition: Identifier | dict | None
    status: Optional[Code] = None
    intent: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    priority: Optional[Code] = None
    doNotPerform: Optional[Boolean] = None
    code: CodeableConcept | dict | None
    orderDetail: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    quantityQuantity: Quantity | dict | None
    quantityRatio: Ratio | dict | None
    quantityRange: Range | dict | None
    subject: Reference | dict | None
    encounter: Reference | dict | None
    occurrenceDateTime: Optional[DateTime] = None
    occurrencePeriod: Period | dict | None
    occurrenceTiming: Timing | dict | None
    asNeededBoolean: Optional[Boolean] = None
    asNeededCodeableConcept: CodeableConcept | dict | None
    authoredOn: Optional[DateTime] = None
    requester: Reference | dict | None
    performerType: CodeableConcept | dict | None
    performer: Reference | FHIRList[Reference] | list | dict
    locationCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    locationReference: Reference | FHIRList[Reference] | list | dict
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    insurance: Reference | FHIRList[Reference] | list | dict
    supportingInfo: Reference | FHIRList[Reference] | list | dict
    specimen: Reference | FHIRList[Reference] | list | dict
    bodySite: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    patientInstruction: Optional[String] = None
    relevantHistory: Reference | FHIRList[Reference] | list | dict


class Slot(FHIRResource):
    _resource_type = "Slot"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'serviceCategory', 'serviceType', 'specialty'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'serviceCategory': 'CodeableConcept',
        'serviceType': 'CodeableConcept',
        'specialty': 'CodeableConcept',
        'appointmentType': 'CodeableConcept',
        'schedule': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    serviceCategory: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    serviceType: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    specialty: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    appointmentType: CodeableConcept | dict | None
    schedule: Reference | dict | None
    status: Optional[Code] = None
    start: Optional[Instant] = None
    end: Optional[Instant] = None
    overbooked: Optional[Boolean] = None
    comment: Optional[String] = None


class SpecimenCollection(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'collector': 'Reference',
        'collectedPeriod': 'Period',
        'duration': 'Duration',
        'quantity': 'Quantity',
        'method': 'CodeableConcept',
        'bodySite': 'CodeableConcept',
        'fastingStatusCodeableConcept': 'CodeableConcept',
        'fastingStatusDuration': 'Duration',
    }
    _choice_fields = {'collected': ['collectedDateTime', 'collectedPeriod'], 'fastingStatus': ['fastingStatusCodeableConcept', 'fastingStatusDuration']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    collector: Reference | dict | None
    collectedDateTime: Optional[DateTime] = None
    collectedPeriod: Period | dict | None
    duration: Duration | dict | None
    quantity: Quantity | dict | None
    method: CodeableConcept | dict | None
    bodySite: CodeableConcept | dict | None
    fastingStatusCodeableConcept: CodeableConcept | dict | None
    fastingStatusDuration: Duration | dict | None


class SpecimenProcessing(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'additive'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'procedure': 'CodeableConcept', 'additive': 'Reference', 'timePeriod': 'Period'}
    _choice_fields = {'time': ['timeDateTime', 'timePeriod']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    description: Optional[String] = None
    procedure: CodeableConcept | dict | None
    additive: Reference | FHIRList[Reference] | list | dict
    timeDateTime: Optional[DateTime] = None
    timePeriod: Period | dict | None


class SpecimenContainer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'identifier'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'capacity': 'Quantity',
        'specimenQuantity': 'Quantity',
        'additiveCodeableConcept': 'CodeableConcept',
        'additiveReference': 'Reference',
    }
    _choice_fields = {'additive': ['additiveCodeableConcept', 'additiveReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    description: Optional[String] = None
    type_: CodeableConcept | dict | None
    capacity: Quantity | dict | None
    specimenQuantity: Quantity | dict | None
    additiveCodeableConcept: CodeableConcept | dict | None
    additiveReference: Reference | dict | None


class Specimen(FHIRResource):
    _resource_type = "Specimen"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'parent', 'request', 'processing', 'container', 'condition', 'note'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'accessionIdentifier': 'Identifier',
        'type_': 'CodeableConcept',
        'subject': 'Reference',
        'parent': 'Reference',
        'request': 'Reference',
        'collection': 'SpecimenCollection',
        'processing': 'SpecimenProcessing',
        'container': 'SpecimenContainer',
        'condition': 'CodeableConcept',
        'note': 'Annotation',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    accessionIdentifier: Identifier | dict | None
    status: Optional[Code] = None
    type_: CodeableConcept | dict | None
    subject: Reference | dict | None
    receivedTime: Optional[DateTime] = None
    parent: Reference | FHIRList[Reference] | list | dict
    request: Reference | FHIRList[Reference] | list | dict
    collection: SpecimenCollection | dict | None
    processing: SpecimenProcessing | FHIRList[SpecimenProcessing] | list | dict
    container: SpecimenContainer | FHIRList[SpecimenContainer] | list | dict
    condition: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict


class SpecimenDefinitionTypeTested(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'rejectionCriterion', 'handling'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'container': 'SpecimenDefinitionTypeTestedContainer',
        'retentionTime': 'Duration',
        'rejectionCriterion': 'CodeableConcept',
        'handling': 'SpecimenDefinitionTypeTestedHandling',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    isDerived: Optional[Boolean] = None
    type_: CodeableConcept | dict | None
    preference: Optional[Code] = None
    container: SpecimenDefinitionTypeTestedContainer | dict | None
    requirement: Optional[String] = None
    retentionTime: Duration | dict | None
    rejectionCriterion: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    handling: SpecimenDefinitionTypeTestedHandling | FHIRList[SpecimenDefinitionTypeTestedHandling] | list | dict


class SpecimenDefinitionTypeTestedContainer(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'additive'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'material': 'CodeableConcept',
        'type_': 'CodeableConcept',
        'cap': 'CodeableConcept',
        'capacity': 'Quantity',
        'minimumVolumeQuantity': 'Quantity',
        'additive': 'SpecimenDefinitionTypeTestedContainerAdditive',
    }
    _choice_fields = {'minimumVolume': ['minimumVolumeQuantity', 'minimumVolumeString']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    material: CodeableConcept | dict | None
    type_: CodeableConcept | dict | None
    cap: CodeableConcept | dict | None
    description: Optional[String] = None
    capacity: Quantity | dict | None
    minimumVolumeQuantity: Quantity | dict | None
    minimumVolumeString: Optional[String] = None
    additive: SpecimenDefinitionTypeTestedContainerAdditive | FHIRList[SpecimenDefinitionTypeTestedContainerAdditive] | list | dict
    preparation: Optional[String] = None


class SpecimenDefinitionTypeTestedContainerAdditive(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'additiveCodeableConcept': 'CodeableConcept', 'additiveReference': 'Reference'}
    _choice_fields = {'additive': ['additiveCodeableConcept', 'additiveReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    additiveCodeableConcept: CodeableConcept | dict | None
    additiveReference: Reference | dict | None


class SpecimenDefinitionTypeTestedHandling(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'temperatureQualifier': 'CodeableConcept',
        'temperatureRange': 'Range',
        'maxDuration': 'Duration',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    temperatureQualifier: CodeableConcept | dict | None
    temperatureRange: Range | dict | None
    maxDuration: Duration | dict | None
    instruction: Optional[String] = None


class SpecimenDefinition(FHIRResource):
    _resource_type = "SpecimenDefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'patientPreparation', 'collection', 'typeTested'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'typeCollected': 'CodeableConcept',
        'patientPreparation': 'CodeableConcept',
        'collection': 'CodeableConcept',
        'typeTested': 'SpecimenDefinitionTypeTested',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | dict | None
    typeCollected: CodeableConcept | dict | None
    patientPreparation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    timeAspect: Optional[String] = None
    collection: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    typeTested: SpecimenDefinitionTypeTested | FHIRList[SpecimenDefinitionTypeTested] | list | dict


class StructureDefinitionMapping(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identity: Optional[Id] = None
    uri: Optional[Uri] = None
    name: Optional[String] = None
    comment: Optional[String] = None


class StructureDefinitionContext(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    expression: Optional[String] = None


class StructureDefinitionSnapshot(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'element'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'element': 'ElementDefinition'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    element: ElementDefinition | FHIRList[ElementDefinition] | list | dict


class StructureDefinitionDifferential(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'element'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'element': 'ElementDefinition'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    element: ElementDefinition | FHIRList[ElementDefinition] | list | dict


class StructureDefinition(FHIRResource):
    _resource_type = "StructureDefinition"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'contact',
        'useContext',
        'jurisdiction',
        'keyword',
        'mapping',
        'context',
        'contextInvariant',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'keyword': 'Coding',
        'mapping': 'StructureDefinitionMapping',
        'context': 'StructureDefinitionContext',
        'snapshot': 'StructureDefinitionSnapshot',
        'differential': 'StructureDefinitionDifferential',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    keyword: Coding | FHIRList[Coding] | list | dict
    fhirVersion: Optional[Code] = None
    mapping: StructureDefinitionMapping | FHIRList[StructureDefinitionMapping] | list | dict
    kind: Optional[Code] = None
    abstract: Optional[Boolean] = None
    context: StructureDefinitionContext | FHIRList[StructureDefinitionContext] | list | dict
    contextInvariant: String | FHIRList[String] | list | None = None
    type_: Optional[Uri] = None
    baseDefinition: Optional[Canonical] = None
    derivation: Optional[Code] = None
    snapshot: StructureDefinitionSnapshot | dict | None
    differential: StructureDefinitionDifferential | dict | None


class StructureMapStructure(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Canonical] = None
    mode: Optional[Code] = None
    alias: Optional[String] = None
    documentation: Optional[String] = None


class StructureMapGroup(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'input', 'rule'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'input': 'StructureMapGroupInput', 'rule': 'StructureMapGroupRule'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[Id] = None
    extends: Optional[Id] = None
    typeMode: Optional[Code] = None
    documentation: Optional[String] = None
    input: StructureMapGroupInput | FHIRList[StructureMapGroupInput] | list | dict
    rule: StructureMapGroupRule | FHIRList[StructureMapGroupRule] | list | dict


class StructureMapGroupInput(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[Id] = None
    type_: Optional[String] = None
    mode: Optional[Code] = None
    documentation: Optional[String] = None


class StructureMapGroupRule(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'source', 'target', 'rule', 'dependent'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'source': 'StructureMapGroupRuleSource',
        'target': 'StructureMapGroupRuleTarget',
        'dependent': 'StructureMapGroupRuleDependent',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[Id] = None
    source: StructureMapGroupRuleSource | FHIRList[StructureMapGroupRuleSource] | list | dict
    target: StructureMapGroupRuleTarget | FHIRList[StructureMapGroupRuleTarget] | list | dict
    rule: Any = None
    dependent: StructureMapGroupRuleDependent | FHIRList[StructureMapGroupRuleDependent] | list | dict
    documentation: Optional[String] = None


class StructureMapGroupRuleSource(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'defaultValueAddress': 'Address',
        'defaultValueAge': 'Age',
        'defaultValueAnnotation': 'Annotation',
        'defaultValueAttachment': 'Attachment',
        'defaultValueCodeableConcept': 'CodeableConcept',
        'defaultValueCoding': 'Coding',
        'defaultValueContactPoint': 'ContactPoint',
        'defaultValueCount': 'Count',
        'defaultValueDistance': 'Distance',
        'defaultValueDuration': 'Duration',
        'defaultValueHumanName': 'HumanName',
        'defaultValueIdentifier': 'Identifier',
        'defaultValueMoney': 'Money',
        'defaultValuePeriod': 'Period',
        'defaultValueQuantity': 'Quantity',
        'defaultValueRange': 'Range',
        'defaultValueRatio': 'Ratio',
        'defaultValueReference': 'Reference',
        'defaultValueSampledData': 'SampledData',
        'defaultValueSignature': 'Signature',
        'defaultValueTiming': 'Timing',
        'defaultValueContactDetail': 'ContactDetail',
        'defaultValueContributor': 'Contributor',
        'defaultValueDataRequirement': 'DataRequirement',
        'defaultValueExpression': 'Expression',
        'defaultValueParameterDefinition': 'ParameterDefinition',
        'defaultValueRelatedArtifact': 'RelatedArtifact',
        'defaultValueTriggerDefinition': 'TriggerDefinition',
        'defaultValueUsageContext': 'UsageContext',
        'defaultValueDosage': 'Dosage',
        'defaultValueMeta': 'Meta',
    }
    _choice_fields = {
        'defaultValue': [
            'defaultValueBase64Binary',
            'defaultValueBoolean',
            'defaultValueCanonical',
            'defaultValueCode',
            'defaultValueDate',
            'defaultValueDateTime',
            'defaultValueDecimal',
            'defaultValueId',
            'defaultValueInstant',
            'defaultValueInteger',
            'defaultValueMarkdown',
            'defaultValueOid',
            'defaultValuePositiveInt',
            'defaultValueString',
            'defaultValueTime',
            'defaultValueUnsignedInt',
            'defaultValueUri',
            'defaultValueUrl',
            'defaultValueUuid',
            'defaultValueAddress',
            'defaultValueAge',
            'defaultValueAnnotation',
            'defaultValueAttachment',
            'defaultValueCodeableConcept',
            'defaultValueCoding',
            'defaultValueContactPoint',
            'defaultValueCount',
            'defaultValueDistance',
            'defaultValueDuration',
            'defaultValueHumanName',
            'defaultValueIdentifier',
            'defaultValueMoney',
            'defaultValuePeriod',
            'defaultValueQuantity',
            'defaultValueRange',
            'defaultValueRatio',
            'defaultValueReference',
            'defaultValueSampledData',
            'defaultValueSignature',
            'defaultValueTiming',
            'defaultValueContactDetail',
            'defaultValueContributor',
            'defaultValueDataRequirement',
            'defaultValueExpression',
            'defaultValueParameterDefinition',
            'defaultValueRelatedArtifact',
            'defaultValueTriggerDefinition',
            'defaultValueUsageContext',
            'defaultValueDosage',
            'defaultValueMeta',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
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
    defaultValueAddress: Address | dict | None
    defaultValueAge: Age | dict | None
    defaultValueAnnotation: Annotation | dict | None
    defaultValueAttachment: Attachment | dict | None
    defaultValueCodeableConcept: CodeableConcept | dict | None
    defaultValueCoding: Coding | dict | None
    defaultValueContactPoint: ContactPoint | dict | None
    defaultValueCount: Count | dict | None
    defaultValueDistance: Distance | dict | None
    defaultValueDuration: Duration | dict | None
    defaultValueHumanName: HumanName | dict | None
    defaultValueIdentifier: Identifier | dict | None
    defaultValueMoney: Money | dict | None
    defaultValuePeriod: Period | dict | None
    defaultValueQuantity: Quantity | dict | None
    defaultValueRange: Range | dict | None
    defaultValueRatio: Ratio | dict | None
    defaultValueReference: Reference | dict | None
    defaultValueSampledData: SampledData | dict | None
    defaultValueSignature: Signature | dict | None
    defaultValueTiming: Timing | dict | None
    defaultValueContactDetail: ContactDetail | dict | None
    defaultValueContributor: Contributor | dict | None
    defaultValueDataRequirement: DataRequirement | dict | None
    defaultValueExpression: Expression | dict | None
    defaultValueParameterDefinition: ParameterDefinition | dict | None
    defaultValueRelatedArtifact: RelatedArtifact | dict | None
    defaultValueTriggerDefinition: TriggerDefinition | dict | None
    defaultValueUsageContext: UsageContext | dict | None
    defaultValueDosage: Dosage | dict | None
    defaultValueMeta: Meta | dict | None
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
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    context: Optional[Id] = None
    contextType: Optional[Code] = None
    element: Optional[String] = None
    variable: Optional[Id] = None
    listMode: Code | FHIRList[Code] | list | None = None
    listRuleId: Optional[Id] = None
    transform: Optional[Code] = None
    parameter: StructureMapGroupRuleTargetParameter | FHIRList[StructureMapGroupRuleTargetParameter] | list | dict


class StructureMapGroupRuleTargetParameter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}
    _choice_fields = {'value': ['valueId', 'valueString', 'valueBoolean', 'valueInteger', 'valueDecimal']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    valueId: Optional[Id] = None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueDecimal: Optional[Decimal] = None


class StructureMapGroupRuleDependent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'variable'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[Id] = None
    variable: String | FHIRList[String] | list | None = None


class StructureMap(FHIRResource):
    _resource_type = "StructureMap"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'structure', 'import_', 'group'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'structure': 'StructureMapStructure',
        'group': 'StructureMapGroup',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    structure: StructureMapStructure | FHIRList[StructureMapStructure] | list | dict
    import_: Canonical | FHIRList[Canonical] | list | None = None
    group: StructureMapGroup | FHIRList[StructureMapGroup] | list | dict


class SubscriptionChannel(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'header'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    endpoint: Optional[Url] = None
    payload: Optional[Code] = None
    header: String | FHIRList[String] | list | None = None


class Subscription(FHIRResource):
    _resource_type = "Subscription"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'contact': 'ContactPoint',
        'channel': 'SubscriptionChannel',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    status: Optional[Code] = None
    contact: ContactPoint | FHIRList[ContactPoint] | list | dict
    end: Optional[Instant] = None
    reason: Optional[String] = None
    criteria: Optional[String] = None
    error: Optional[String] = None
    channel: SubscriptionChannel | dict | None


class SubstanceInstance(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'quantity': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | dict | None
    expiry: Optional[DateTime] = None
    quantity: Quantity | dict | None


class SubstanceIngredient(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'quantity': 'Ratio',
        'substanceCodeableConcept': 'CodeableConcept',
        'substanceReference': 'Reference',
    }
    _choice_fields = {'substance': ['substanceCodeableConcept', 'substanceReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    quantity: Ratio | dict | None
    substanceCodeableConcept: CodeableConcept | dict | None
    substanceReference: Reference | dict | None


class Substance(FHIRResource):
    _resource_type = "Substance"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'category', 'instance', 'ingredient'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'instance': 'SubstanceInstance',
        'ingredient': 'SubstanceIngredient',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    code: CodeableConcept | dict | None
    description: Optional[String] = None
    instance: SubstanceInstance | FHIRList[SubstanceInstance] | list | dict
    ingredient: SubstanceIngredient | FHIRList[SubstanceIngredient] | list | dict


class SubstanceNucleicAcidSubunit(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'linkage', 'sugar'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'sequenceAttachment': 'Attachment',
        'fivePrime': 'CodeableConcept',
        'threePrime': 'CodeableConcept',
        'linkage': 'SubstanceNucleicAcidSubunitLinkage',
        'sugar': 'SubstanceNucleicAcidSubunitSugar',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    subunit: Optional[Integer] = None
    sequence: Optional[String] = None
    length: Optional[Integer] = None
    sequenceAttachment: Attachment | dict | None
    fivePrime: CodeableConcept | dict | None
    threePrime: CodeableConcept | dict | None
    linkage: SubstanceNucleicAcidSubunitLinkage | FHIRList[SubstanceNucleicAcidSubunitLinkage] | list | dict
    sugar: SubstanceNucleicAcidSubunitSugar | FHIRList[SubstanceNucleicAcidSubunitSugar] | list | dict


class SubstanceNucleicAcidSubunitLinkage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    connectivity: Optional[String] = None
    identifier: Identifier | dict | None
    name: Optional[String] = None
    residueSite: Optional[String] = None


class SubstanceNucleicAcidSubunitSugar(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | dict | None
    name: Optional[String] = None
    residueSite: Optional[String] = None


class SubstanceNucleicAcid(FHIRResource):
    _resource_type = "SubstanceNucleicAcid"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'subunit'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'sequenceType': 'CodeableConcept',
        'oligoNucleotideType': 'CodeableConcept',
        'subunit': 'SubstanceNucleicAcidSubunit',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sequenceType: CodeableConcept | dict | None
    numberOfSubunits: Optional[Integer] = None
    areaOfHybridisation: Optional[String] = None
    oligoNucleotideType: CodeableConcept | dict | None
    subunit: SubstanceNucleicAcidSubunit | FHIRList[SubstanceNucleicAcidSubunit] | list | dict


class SubstancePolymerMonomerSet(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'startingMaterial'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'ratioType': 'CodeableConcept',
        'startingMaterial': 'SubstancePolymerMonomerSetStartingMaterial',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    ratioType: CodeableConcept | dict | None
    startingMaterial: SubstancePolymerMonomerSetStartingMaterial | FHIRList[SubstancePolymerMonomerSetStartingMaterial] | list | dict


class SubstancePolymerMonomerSetStartingMaterial(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'material': 'CodeableConcept',
        'type_': 'CodeableConcept',
        'amount': 'SubstanceAmount',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    material: CodeableConcept | dict | None
    type_: CodeableConcept | dict | None
    isDefining: Optional[Boolean] = None
    amount: SubstanceAmount | dict | None


class SubstancePolymerRepeat(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'repeatUnit'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'repeatUnitAmountType': 'CodeableConcept',
        'repeatUnit': 'SubstancePolymerRepeatRepeatUnit',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    numberOfUnits: Optional[Integer] = None
    averageMolecularFormula: Optional[String] = None
    repeatUnitAmountType: CodeableConcept | dict | None
    repeatUnit: SubstancePolymerRepeatRepeatUnit | FHIRList[SubstancePolymerRepeatRepeatUnit] | list | dict


class SubstancePolymerRepeatRepeatUnit(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'degreeOfPolymerisation', 'structuralRepresentation'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'orientationOfPolymerisation': 'CodeableConcept',
        'amount': 'SubstanceAmount',
        'degreeOfPolymerisation': 'SubstancePolymerRepeatRepeatUnitDegreeOfPolymerisation',
        'structuralRepresentation': 'SubstancePolymerRepeatRepeatUnitStructuralRepresentation',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    orientationOfPolymerisation: CodeableConcept | dict | None
    repeatUnit: Optional[String] = None
    amount: SubstanceAmount | dict | None
    degreeOfPolymerisation: (
        SubstancePolymerRepeatRepeatUnitDegreeOfPolymerisation | FHIRList[SubstancePolymerRepeatRepeatUnitDegreeOfPolymerisation] | list | dict
    )
    structuralRepresentation: (
        SubstancePolymerRepeatRepeatUnitStructuralRepresentation | FHIRList[SubstancePolymerRepeatRepeatUnitStructuralRepresentation] | list | dict
    )


class SubstancePolymerRepeatRepeatUnitDegreeOfPolymerisation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'degree': 'CodeableConcept', 'amount': 'SubstanceAmount'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    degree: CodeableConcept | dict | None
    amount: SubstanceAmount | dict | None


class SubstancePolymerRepeatRepeatUnitStructuralRepresentation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'attachment': 'Attachment'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    representation: Optional[String] = None
    attachment: Attachment | dict | None


class SubstancePolymer(FHIRResource):
    _resource_type = "SubstancePolymer"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'copolymerConnectivity', 'modification', 'monomerSet', 'repeat'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'class_': 'CodeableConcept',
        'geometry': 'CodeableConcept',
        'copolymerConnectivity': 'CodeableConcept',
        'monomerSet': 'SubstancePolymerMonomerSet',
        'repeat': 'SubstancePolymerRepeat',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    class_: CodeableConcept | dict | None
    geometry: CodeableConcept | dict | None
    copolymerConnectivity: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    modification: String | FHIRList[String] | list | None = None
    monomerSet: SubstancePolymerMonomerSet | FHIRList[SubstancePolymerMonomerSet] | list | dict
    repeat: SubstancePolymerRepeat | FHIRList[SubstancePolymerRepeat] | list | dict


class SubstanceProteinSubunit(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'sequenceAttachment': 'Attachment',
        'nTerminalModificationId': 'Identifier',
        'cTerminalModificationId': 'Identifier',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    subunit: Optional[Integer] = None
    sequence: Optional[String] = None
    length: Optional[Integer] = None
    sequenceAttachment: Attachment | dict | None
    nTerminalModificationId: Identifier | dict | None
    nTerminalModification: Optional[String] = None
    cTerminalModificationId: Identifier | dict | None
    cTerminalModification: Optional[String] = None


class SubstanceProtein(FHIRResource):
    _resource_type = "SubstanceProtein"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'disulfideLinkage', 'subunit'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'sequenceType': 'CodeableConcept',
        'subunit': 'SubstanceProteinSubunit',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sequenceType: CodeableConcept | dict | None
    numberOfSubunits: Optional[Integer] = None
    disulfideLinkage: String | FHIRList[String] | list | None = None
    subunit: SubstanceProteinSubunit | FHIRList[SubstanceProteinSubunit] | list | dict


class SubstanceReferenceInformationGene(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'source'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'geneSequenceOrigin': 'CodeableConcept',
        'gene': 'CodeableConcept',
        'source': 'Reference',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    geneSequenceOrigin: CodeableConcept | dict | None
    gene: CodeableConcept | dict | None
    source: Reference | FHIRList[Reference] | list | dict


class SubstanceReferenceInformationGeneElement(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'source'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'element': 'Identifier', 'source': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    element: Identifier | dict | None
    source: Reference | FHIRList[Reference] | list | dict


class SubstanceReferenceInformationClassification(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'subtype', 'source'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'domain': 'CodeableConcept',
        'classification': 'CodeableConcept',
        'subtype': 'CodeableConcept',
        'source': 'Reference',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    domain: CodeableConcept | dict | None
    classification: CodeableConcept | dict | None
    subtype: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    source: Reference | FHIRList[Reference] | list | dict


class SubstanceReferenceInformationTarget(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'source'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'target': 'Identifier',
        'type_': 'CodeableConcept',
        'interaction': 'CodeableConcept',
        'organism': 'CodeableConcept',
        'organismType': 'CodeableConcept',
        'amountQuantity': 'Quantity',
        'amountRange': 'Range',
        'amountType': 'CodeableConcept',
        'source': 'Reference',
    }
    _choice_fields = {'amount': ['amountQuantity', 'amountRange', 'amountString']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    target: Identifier | dict | None
    type_: CodeableConcept | dict | None
    interaction: CodeableConcept | dict | None
    organism: CodeableConcept | dict | None
    organismType: CodeableConcept | dict | None
    amountQuantity: Quantity | dict | None
    amountRange: Range | dict | None
    amountString: Optional[String] = None
    amountType: CodeableConcept | dict | None
    source: Reference | FHIRList[Reference] | list | dict


class SubstanceReferenceInformation(FHIRResource):
    _resource_type = "SubstanceReferenceInformation"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'gene', 'geneElement', 'classification', 'target'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'gene': 'SubstanceReferenceInformationGene',
        'geneElement': 'SubstanceReferenceInformationGeneElement',
        'classification': 'SubstanceReferenceInformationClassification',
        'target': 'SubstanceReferenceInformationTarget',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    comment: Optional[String] = None
    gene: SubstanceReferenceInformationGene | FHIRList[SubstanceReferenceInformationGene] | list | dict
    geneElement: SubstanceReferenceInformationGeneElement | FHIRList[SubstanceReferenceInformationGeneElement] | list | dict
    classification: SubstanceReferenceInformationClassification | FHIRList[SubstanceReferenceInformationClassification] | list | dict
    target: SubstanceReferenceInformationTarget | FHIRList[SubstanceReferenceInformationTarget] | list | dict


class SubstanceSourceMaterialFractionDescription(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'materialType': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    fraction: Optional[String] = None
    materialType: CodeableConcept | dict | None


class SubstanceSourceMaterialOrganism(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'author'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'family': 'CodeableConcept',
        'genus': 'CodeableConcept',
        'species': 'CodeableConcept',
        'intraspecificType': 'CodeableConcept',
        'author': 'SubstanceSourceMaterialOrganismAuthor',
        'hybrid': 'SubstanceSourceMaterialOrganismHybrid',
        'organismGeneral': 'SubstanceSourceMaterialOrganismOrganismGeneral',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    family: CodeableConcept | dict | None
    genus: CodeableConcept | dict | None
    species: CodeableConcept | dict | None
    intraspecificType: CodeableConcept | dict | None
    intraspecificDescription: Optional[String] = None
    author: SubstanceSourceMaterialOrganismAuthor | FHIRList[SubstanceSourceMaterialOrganismAuthor] | list | dict
    hybrid: SubstanceSourceMaterialOrganismHybrid | dict | None
    organismGeneral: SubstanceSourceMaterialOrganismOrganismGeneral | dict | None


class SubstanceSourceMaterialOrganismAuthor(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'authorType': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    authorType: CodeableConcept | dict | None
    authorDescription: Optional[String] = None


class SubstanceSourceMaterialOrganismHybrid(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'hybridType': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    maternalOrganismId: Optional[String] = None
    maternalOrganismName: Optional[String] = None
    paternalOrganismId: Optional[String] = None
    paternalOrganismName: Optional[String] = None
    hybridType: CodeableConcept | dict | None


class SubstanceSourceMaterialOrganismOrganismGeneral(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'kingdom': 'CodeableConcept',
        'phylum': 'CodeableConcept',
        'class_': 'CodeableConcept',
        'order': 'CodeableConcept',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    kingdom: CodeableConcept | dict | None
    phylum: CodeableConcept | dict | None
    class_: CodeableConcept | dict | None
    order: CodeableConcept | dict | None


class SubstanceSourceMaterialPartDescription(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'part': 'CodeableConcept', 'partLocation': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    part: CodeableConcept | dict | None
    partLocation: CodeableConcept | dict | None


class SubstanceSourceMaterial(FHIRResource):
    _resource_type = "SubstanceSourceMaterial"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'parentSubstanceId',
        'parentSubstanceName',
        'countryOfOrigin',
        'geographicalLocation',
        'fractionDescription',
        'partDescription',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'sourceMaterialClass': 'CodeableConcept',
        'sourceMaterialType': 'CodeableConcept',
        'sourceMaterialState': 'CodeableConcept',
        'organismId': 'Identifier',
        'parentSubstanceId': 'Identifier',
        'countryOfOrigin': 'CodeableConcept',
        'developmentStage': 'CodeableConcept',
        'fractionDescription': 'SubstanceSourceMaterialFractionDescription',
        'organism': 'SubstanceSourceMaterialOrganism',
        'partDescription': 'SubstanceSourceMaterialPartDescription',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sourceMaterialClass: CodeableConcept | dict | None
    sourceMaterialType: CodeableConcept | dict | None
    sourceMaterialState: CodeableConcept | dict | None
    organismId: Identifier | dict | None
    organismName: Optional[String] = None
    parentSubstanceId: Identifier | FHIRList[Identifier] | list | dict
    parentSubstanceName: String | FHIRList[String] | list | None = None
    countryOfOrigin: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    geographicalLocation: String | FHIRList[String] | list | None = None
    developmentStage: CodeableConcept | dict | None
    fractionDescription: SubstanceSourceMaterialFractionDescription | FHIRList[SubstanceSourceMaterialFractionDescription] | list | dict
    organism: SubstanceSourceMaterialOrganism | dict | None
    partDescription: SubstanceSourceMaterialPartDescription | FHIRList[SubstanceSourceMaterialPartDescription] | list | dict


class SubstanceSpecificationMoiety(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'role': 'CodeableConcept',
        'identifier': 'Identifier',
        'stereochemistry': 'CodeableConcept',
        'opticalActivity': 'CodeableConcept',
        'amountQuantity': 'Quantity',
    }
    _choice_fields = {'amount': ['amountQuantity', 'amountString']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    role: CodeableConcept | dict | None
    identifier: Identifier | dict | None
    name: Optional[String] = None
    stereochemistry: CodeableConcept | dict | None
    opticalActivity: CodeableConcept | dict | None
    molecularFormula: Optional[String] = None
    amountQuantity: Quantity | dict | None
    amountString: Optional[String] = None


class SubstanceSpecificationProperty(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'definingSubstanceReference': 'Reference',
        'definingSubstanceCodeableConcept': 'CodeableConcept',
        'amountQuantity': 'Quantity',
    }
    _choice_fields = {'amount': ['amountQuantity', 'amountString'], 'definingSubstance': ['definingSubstanceReference', 'definingSubstanceCodeableConcept']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    category: CodeableConcept | dict | None
    code: CodeableConcept | dict | None
    parameters: Optional[String] = None
    definingSubstanceReference: Reference | dict | None
    definingSubstanceCodeableConcept: CodeableConcept | dict | None
    amountQuantity: Quantity | dict | None
    amountString: Optional[String] = None


class SubstanceSpecificationStructure(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'isotope', 'source', 'representation'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'stereochemistry': 'CodeableConcept',
        'opticalActivity': 'CodeableConcept',
        'isotope': 'SubstanceSpecificationStructureIsotope',
        'source': 'Reference',
        'representation': 'SubstanceSpecificationStructureRepresentation',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    stereochemistry: CodeableConcept | dict | None
    opticalActivity: CodeableConcept | dict | None
    molecularFormula: Optional[String] = None
    molecularFormulaByMoiety: Optional[String] = None
    isotope: SubstanceSpecificationStructureIsotope | FHIRList[SubstanceSpecificationStructureIsotope] | list | dict
    molecularWeight: Any = None
    source: Reference | FHIRList[Reference] | list | dict
    representation: SubstanceSpecificationStructureRepresentation | FHIRList[SubstanceSpecificationStructureRepresentation] | list | dict


class SubstanceSpecificationStructureIsotope(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'name': 'CodeableConcept',
        'substitution': 'CodeableConcept',
        'halfLife': 'Quantity',
        'molecularWeight': 'SubstanceSpecificationStructureIsotopeMolecularWeight',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | dict | None
    name: CodeableConcept | dict | None
    substitution: CodeableConcept | dict | None
    halfLife: Quantity | dict | None
    molecularWeight: SubstanceSpecificationStructureIsotopeMolecularWeight | dict | None


class SubstanceSpecificationStructureIsotopeMolecularWeight(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'method': 'CodeableConcept', 'type_': 'CodeableConcept', 'amount': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    method: CodeableConcept | dict | None
    type_: CodeableConcept | dict | None
    amount: Quantity | dict | None


class SubstanceSpecificationStructureRepresentation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'type_': 'CodeableConcept', 'attachment': 'Attachment'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
    representation: Optional[String] = None
    attachment: Attachment | dict | None


class SubstanceSpecificationCode(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'source'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'status': 'CodeableConcept', 'source': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    status: CodeableConcept | dict | None
    statusDate: Optional[DateTime] = None
    comment: Optional[String] = None
    source: Reference | FHIRList[Reference] | list | dict


class SubstanceSpecificationName(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'language', 'domain', 'jurisdiction', 'synonym', 'translation', 'official', 'source'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'status': 'CodeableConcept',
        'language': 'CodeableConcept',
        'domain': 'CodeableConcept',
        'jurisdiction': 'CodeableConcept',
        'official': 'SubstanceSpecificationNameOfficial',
        'source': 'Reference',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[String] = None
    type_: CodeableConcept | dict | None
    status: CodeableConcept | dict | None
    preferred: Optional[Boolean] = None
    language: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    domain: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    synonym: Any = None
    translation: Any = None
    official: SubstanceSpecificationNameOfficial | FHIRList[SubstanceSpecificationNameOfficial] | list | dict
    source: Reference | FHIRList[Reference] | list | dict


class SubstanceSpecificationNameOfficial(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'authority': 'CodeableConcept', 'status': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    authority: CodeableConcept | dict | None
    status: CodeableConcept | dict | None
    date: Optional[DateTime] = None


class SubstanceSpecificationRelationship(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'source'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'substanceReference': 'Reference',
        'substanceCodeableConcept': 'CodeableConcept',
        'relationship': 'CodeableConcept',
        'amountQuantity': 'Quantity',
        'amountRange': 'Range',
        'amountRatio': 'Ratio',
        'amountRatioLowLimit': 'Ratio',
        'amountType': 'CodeableConcept',
        'source': 'Reference',
    }
    _choice_fields = {
        'amount': ['amountQuantity', 'amountRange', 'amountRatio', 'amountString'],
        'substance': ['substanceReference', 'substanceCodeableConcept'],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    substanceReference: Reference | dict | None
    substanceCodeableConcept: CodeableConcept | dict | None
    relationship: CodeableConcept | dict | None
    isDefining: Optional[Boolean] = None
    amountQuantity: Quantity | dict | None
    amountRange: Range | dict | None
    amountRatio: Ratio | dict | None
    amountString: Optional[String] = None
    amountRatioLowLimit: Ratio | dict | None
    amountType: CodeableConcept | dict | None
    source: Reference | FHIRList[Reference] | list | dict


class SubstanceSpecification(FHIRResource):
    _resource_type = "SubstanceSpecification"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'source', 'moiety', 'property', 'code', 'name', 'molecularWeight', 'relationship'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'status': 'CodeableConcept',
        'domain': 'CodeableConcept',
        'source': 'Reference',
        'moiety': 'SubstanceSpecificationMoiety',
        'property': 'SubstanceSpecificationProperty',
        'referenceInformation': 'Reference',
        'structure': 'SubstanceSpecificationStructure',
        'code': 'SubstanceSpecificationCode',
        'name': 'SubstanceSpecificationName',
        'relationship': 'SubstanceSpecificationRelationship',
        'nucleicAcid': 'Reference',
        'polymer': 'Reference',
        'protein': 'Reference',
        'sourceMaterial': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | dict | None
    type_: CodeableConcept | dict | None
    status: CodeableConcept | dict | None
    domain: CodeableConcept | dict | None
    description: Optional[String] = None
    source: Reference | FHIRList[Reference] | list | dict
    comment: Optional[String] = None
    moiety: SubstanceSpecificationMoiety | FHIRList[SubstanceSpecificationMoiety] | list | dict
    property: SubstanceSpecificationProperty | FHIRList[SubstanceSpecificationProperty] | list | dict
    referenceInformation: Reference | dict | None
    structure: SubstanceSpecificationStructure | dict | None
    code: SubstanceSpecificationCode | FHIRList[SubstanceSpecificationCode] | list | dict
    name: SubstanceSpecificationName | FHIRList[SubstanceSpecificationName] | list | dict
    molecularWeight: Any = None
    relationship: SubstanceSpecificationRelationship | FHIRList[SubstanceSpecificationRelationship] | list | dict
    nucleicAcid: Reference | dict | None
    polymer: Reference | dict | None
    protein: Reference | dict | None
    sourceMaterial: Reference | dict | None


class SupplyDeliverySuppliedItem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'quantity': 'Quantity',
        'itemCodeableConcept': 'CodeableConcept',
        'itemReference': 'Reference',
    }
    _choice_fields = {'item': ['itemCodeableConcept', 'itemReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    quantity: Quantity | dict | None
    itemCodeableConcept: CodeableConcept | dict | None
    itemReference: Reference | dict | None


class SupplyDelivery(FHIRResource):
    _resource_type = "SupplyDelivery"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'receiver'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'patient': 'Reference',
        'type_': 'CodeableConcept',
        'suppliedItem': 'SupplyDeliverySuppliedItem',
        'occurrencePeriod': 'Period',
        'occurrenceTiming': 'Timing',
        'supplier': 'Reference',
        'destination': 'Reference',
        'receiver': 'Reference',
    }
    _choice_fields = {'occurrence': ['occurrenceDateTime', 'occurrencePeriod', 'occurrenceTiming']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    patient: Reference | dict | None
    type_: CodeableConcept | dict | None
    suppliedItem: SupplyDeliverySuppliedItem | dict | None
    occurrenceDateTime: Optional[DateTime] = None
    occurrencePeriod: Period | dict | None
    occurrenceTiming: Timing | dict | None
    supplier: Reference | dict | None
    destination: Reference | dict | None
    receiver: Reference | FHIRList[Reference] | list | dict


class SupplyRequestParameter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueCodeableConcept': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueRange': 'Range',
    }
    _choice_fields = {'value': ['valueCodeableConcept', 'valueQuantity', 'valueRange', 'valueBoolean']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueQuantity: Quantity | dict | None
    valueRange: Range | dict | None
    valueBoolean: Optional[Boolean] = None


class SupplyRequest(FHIRResource):
    _resource_type = "SupplyRequest"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'parameter', 'supplier', 'reasonCode', 'reasonReference'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'category': 'CodeableConcept',
        'itemCodeableConcept': 'CodeableConcept',
        'itemReference': 'Reference',
        'quantity': 'Quantity',
        'parameter': 'SupplyRequestParameter',
        'occurrencePeriod': 'Period',
        'occurrenceTiming': 'Timing',
        'requester': 'Reference',
        'supplier': 'Reference',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'deliverFrom': 'Reference',
        'deliverTo': 'Reference',
    }
    _choice_fields = {'item': ['itemCodeableConcept', 'itemReference'], 'occurrence': ['occurrenceDateTime', 'occurrencePeriod', 'occurrenceTiming']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | dict | None
    priority: Optional[Code] = None
    itemCodeableConcept: CodeableConcept | dict | None
    itemReference: Reference | dict | None
    quantity: Quantity | dict | None
    parameter: SupplyRequestParameter | FHIRList[SupplyRequestParameter] | list | dict
    occurrenceDateTime: Optional[DateTime] = None
    occurrencePeriod: Period | dict | None
    occurrenceTiming: Timing | dict | None
    authoredOn: Optional[DateTime] = None
    requester: Reference | dict | None
    supplier: Reference | FHIRList[Reference] | list | dict
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    deliverFrom: Reference | dict | None
    deliverTo: Reference | dict | None


class TaskRestriction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'recipient'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'period': 'Period', 'recipient': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    repetitions: Optional[PositiveInt] = None
    period: Period | dict | None
    recipient: Reference | FHIRList[Reference] | list | dict


class TaskInput(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'valueAddress': 'Address',
        'valueAge': 'Age',
        'valueAnnotation': 'Annotation',
        'valueAttachment': 'Attachment',
        'valueCodeableConcept': 'CodeableConcept',
        'valueCoding': 'Coding',
        'valueContactPoint': 'ContactPoint',
        'valueCount': 'Count',
        'valueDistance': 'Distance',
        'valueDuration': 'Duration',
        'valueHumanName': 'HumanName',
        'valueIdentifier': 'Identifier',
        'valueMoney': 'Money',
        'valuePeriod': 'Period',
        'valueQuantity': 'Quantity',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueReference': 'Reference',
        'valueSampledData': 'SampledData',
        'valueSignature': 'Signature',
        'valueTiming': 'Timing',
        'valueContactDetail': 'ContactDetail',
        'valueContributor': 'Contributor',
        'valueDataRequirement': 'DataRequirement',
        'valueExpression': 'Expression',
        'valueParameterDefinition': 'ParameterDefinition',
        'valueRelatedArtifact': 'RelatedArtifact',
        'valueTriggerDefinition': 'TriggerDefinition',
        'valueUsageContext': 'UsageContext',
        'valueDosage': 'Dosage',
        'valueMeta': 'Meta',
    }
    _choice_fields = {
        'value': [
            'valueBase64Binary',
            'valueBoolean',
            'valueCanonical',
            'valueCode',
            'valueDate',
            'valueDateTime',
            'valueDecimal',
            'valueId',
            'valueInstant',
            'valueInteger',
            'valueMarkdown',
            'valueOid',
            'valuePositiveInt',
            'valueString',
            'valueTime',
            'valueUnsignedInt',
            'valueUri',
            'valueUrl',
            'valueUuid',
            'valueAddress',
            'valueAge',
            'valueAnnotation',
            'valueAttachment',
            'valueCodeableConcept',
            'valueCoding',
            'valueContactPoint',
            'valueCount',
            'valueDistance',
            'valueDuration',
            'valueHumanName',
            'valueIdentifier',
            'valueMoney',
            'valuePeriod',
            'valueQuantity',
            'valueRange',
            'valueRatio',
            'valueReference',
            'valueSampledData',
            'valueSignature',
            'valueTiming',
            'valueContactDetail',
            'valueContributor',
            'valueDataRequirement',
            'valueExpression',
            'valueParameterDefinition',
            'valueRelatedArtifact',
            'valueTriggerDefinition',
            'valueUsageContext',
            'valueDosage',
            'valueMeta',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
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
    valueAddress: Address | dict | None
    valueAge: Age | dict | None
    valueAnnotation: Annotation | dict | None
    valueAttachment: Attachment | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueCoding: Coding | dict | None
    valueContactPoint: ContactPoint | dict | None
    valueCount: Count | dict | None
    valueDistance: Distance | dict | None
    valueDuration: Duration | dict | None
    valueHumanName: HumanName | dict | None
    valueIdentifier: Identifier | dict | None
    valueMoney: Money | dict | None
    valuePeriod: Period | dict | None
    valueQuantity: Quantity | dict | None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueReference: Reference | dict | None
    valueSampledData: SampledData | dict | None
    valueSignature: Signature | dict | None
    valueTiming: Timing | dict | None
    valueContactDetail: ContactDetail | dict | None
    valueContributor: Contributor | dict | None
    valueDataRequirement: DataRequirement | dict | None
    valueExpression: Expression | dict | None
    valueParameterDefinition: ParameterDefinition | dict | None
    valueRelatedArtifact: RelatedArtifact | dict | None
    valueTriggerDefinition: TriggerDefinition | dict | None
    valueUsageContext: UsageContext | dict | None
    valueDosage: Dosage | dict | None
    valueMeta: Meta | dict | None


class TaskOutput(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'CodeableConcept',
        'valueAddress': 'Address',
        'valueAge': 'Age',
        'valueAnnotation': 'Annotation',
        'valueAttachment': 'Attachment',
        'valueCodeableConcept': 'CodeableConcept',
        'valueCoding': 'Coding',
        'valueContactPoint': 'ContactPoint',
        'valueCount': 'Count',
        'valueDistance': 'Distance',
        'valueDuration': 'Duration',
        'valueHumanName': 'HumanName',
        'valueIdentifier': 'Identifier',
        'valueMoney': 'Money',
        'valuePeriod': 'Period',
        'valueQuantity': 'Quantity',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueReference': 'Reference',
        'valueSampledData': 'SampledData',
        'valueSignature': 'Signature',
        'valueTiming': 'Timing',
        'valueContactDetail': 'ContactDetail',
        'valueContributor': 'Contributor',
        'valueDataRequirement': 'DataRequirement',
        'valueExpression': 'Expression',
        'valueParameterDefinition': 'ParameterDefinition',
        'valueRelatedArtifact': 'RelatedArtifact',
        'valueTriggerDefinition': 'TriggerDefinition',
        'valueUsageContext': 'UsageContext',
        'valueDosage': 'Dosage',
        'valueMeta': 'Meta',
    }
    _choice_fields = {
        'value': [
            'valueBase64Binary',
            'valueBoolean',
            'valueCanonical',
            'valueCode',
            'valueDate',
            'valueDateTime',
            'valueDecimal',
            'valueId',
            'valueInstant',
            'valueInteger',
            'valueMarkdown',
            'valueOid',
            'valuePositiveInt',
            'valueString',
            'valueTime',
            'valueUnsignedInt',
            'valueUri',
            'valueUrl',
            'valueUuid',
            'valueAddress',
            'valueAge',
            'valueAnnotation',
            'valueAttachment',
            'valueCodeableConcept',
            'valueCoding',
            'valueContactPoint',
            'valueCount',
            'valueDistance',
            'valueDuration',
            'valueHumanName',
            'valueIdentifier',
            'valueMoney',
            'valuePeriod',
            'valueQuantity',
            'valueRange',
            'valueRatio',
            'valueReference',
            'valueSampledData',
            'valueSignature',
            'valueTiming',
            'valueContactDetail',
            'valueContributor',
            'valueDataRequirement',
            'valueExpression',
            'valueParameterDefinition',
            'valueRelatedArtifact',
            'valueTriggerDefinition',
            'valueUsageContext',
            'valueDosage',
            'valueMeta',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: CodeableConcept | dict | None
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
    valueAddress: Address | dict | None
    valueAge: Age | dict | None
    valueAnnotation: Annotation | dict | None
    valueAttachment: Attachment | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueCoding: Coding | dict | None
    valueContactPoint: ContactPoint | dict | None
    valueCount: Count | dict | None
    valueDistance: Distance | dict | None
    valueDuration: Duration | dict | None
    valueHumanName: HumanName | dict | None
    valueIdentifier: Identifier | dict | None
    valueMoney: Money | dict | None
    valuePeriod: Period | dict | None
    valueQuantity: Quantity | dict | None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueReference: Reference | dict | None
    valueSampledData: SampledData | dict | None
    valueSignature: Signature | dict | None
    valueTiming: Timing | dict | None
    valueContactDetail: ContactDetail | dict | None
    valueContributor: Contributor | dict | None
    valueDataRequirement: DataRequirement | dict | None
    valueExpression: Expression | dict | None
    valueParameterDefinition: ParameterDefinition | dict | None
    valueRelatedArtifact: RelatedArtifact | dict | None
    valueTriggerDefinition: TriggerDefinition | dict | None
    valueUsageContext: UsageContext | dict | None
    valueDosage: Dosage | dict | None
    valueMeta: Meta | dict | None


class Task(FHIRResource):
    _resource_type = "Task"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'basedOn',
        'partOf',
        'performerType',
        'insurance',
        'note',
        'relevantHistory',
        'input',
        'output',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'groupIdentifier': 'Identifier',
        'partOf': 'Reference',
        'statusReason': 'CodeableConcept',
        'businessStatus': 'CodeableConcept',
        'code': 'CodeableConcept',
        'focus': 'Reference',
        'for_': 'Reference',
        'encounter': 'Reference',
        'executionPeriod': 'Period',
        'requester': 'Reference',
        'performerType': 'CodeableConcept',
        'owner': 'Reference',
        'location': 'Reference',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'insurance': 'Reference',
        'note': 'Annotation',
        'relevantHistory': 'Reference',
        'restriction': 'TaskRestriction',
        'input': 'TaskInput',
        'output': 'TaskOutput',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    instantiatesCanonical: Optional[Canonical] = None
    instantiatesUri: Optional[Uri] = None
    basedOn: Reference | FHIRList[Reference] | list | dict
    groupIdentifier: Identifier | dict | None
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    statusReason: CodeableConcept | dict | None
    businessStatus: CodeableConcept | dict | None
    intent: Optional[Code] = None
    priority: Optional[Code] = None
    code: CodeableConcept | dict | None
    description: Optional[String] = None
    focus: Reference | dict | None
    for_: Reference | dict | None
    encounter: Reference | dict | None
    executionPeriod: Period | dict | None
    authoredOn: Optional[DateTime] = None
    lastModified: Optional[DateTime] = None
    requester: Reference | dict | None
    performerType: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    owner: Reference | dict | None
    location: Reference | dict | None
    reasonCode: CodeableConcept | dict | None
    reasonReference: Reference | dict | None
    insurance: Reference | FHIRList[Reference] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    relevantHistory: Reference | FHIRList[Reference] | list | dict
    restriction: TaskRestriction | dict | None
    input: TaskInput | FHIRList[TaskInput] | list | dict
    output: TaskOutput | FHIRList[TaskOutput] | list | dict


class TerminologyCapabilitiesSoftware(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[String] = None
    version: Optional[String] = None


class TerminologyCapabilitiesImplementation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    description: Optional[String] = None
    url: Optional[Url] = None


class TerminologyCapabilitiesCodeSystem(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'version'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'version': 'TerminologyCapabilitiesCodeSystemVersion'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    uri: Optional[Canonical] = None
    version: TerminologyCapabilitiesCodeSystemVersion | FHIRList[TerminologyCapabilitiesCodeSystemVersion] | list | dict
    subsumption: Optional[Boolean] = None


class TerminologyCapabilitiesCodeSystemVersion(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'language', 'filter', 'property'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'filter': 'TerminologyCapabilitiesCodeSystemVersionFilter'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[String] = None
    isDefault: Optional[Boolean] = None
    compositional: Optional[Boolean] = None
    language: Code | FHIRList[Code] | list | None = None
    filter: TerminologyCapabilitiesCodeSystemVersionFilter | FHIRList[TerminologyCapabilitiesCodeSystemVersionFilter] | list | dict
    property: Code | FHIRList[Code] | list | None = None


class TerminologyCapabilitiesCodeSystemVersionFilter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'op'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    op: Code | FHIRList[Code] | list | None = None


class TerminologyCapabilitiesExpansion(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'parameter'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'parameter': 'TerminologyCapabilitiesExpansionParameter'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    hierarchical: Optional[Boolean] = None
    paging: Optional[Boolean] = None
    incomplete: Optional[Boolean] = None
    parameter: TerminologyCapabilitiesExpansionParameter | FHIRList[TerminologyCapabilitiesExpansionParameter] | list | dict
    textFilter: Optional[Markdown] = None


class TerminologyCapabilitiesExpansionParameter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[Code] = None
    documentation: Optional[String] = None


class TerminologyCapabilitiesValidateCode(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    translations: Optional[Boolean] = None


class TerminologyCapabilitiesTranslation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    needsMap: Optional[Boolean] = None


class TerminologyCapabilitiesClosure(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    translation: Optional[Boolean] = None


class TerminologyCapabilities(FHIRResource):
    _resource_type = "TerminologyCapabilities"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'contact', 'useContext', 'jurisdiction', 'codeSystem'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'software': 'TerminologyCapabilitiesSoftware',
        'implementation': 'TerminologyCapabilitiesImplementation',
        'codeSystem': 'TerminologyCapabilitiesCodeSystem',
        'expansion': 'TerminologyCapabilitiesExpansion',
        'validateCode': 'TerminologyCapabilitiesValidateCode',
        'translation': 'TerminologyCapabilitiesTranslation',
        'closure': 'TerminologyCapabilitiesClosure',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    kind: Optional[Code] = None
    software: TerminologyCapabilitiesSoftware | dict | None
    implementation: TerminologyCapabilitiesImplementation | dict | None
    lockedDate: Optional[Boolean] = None
    codeSystem: TerminologyCapabilitiesCodeSystem | FHIRList[TerminologyCapabilitiesCodeSystem] | list | dict
    expansion: TerminologyCapabilitiesExpansion | dict | None
    codeSearch: Optional[Code] = None
    validateCode: TerminologyCapabilitiesValidateCode | dict | None
    translation: TerminologyCapabilitiesTranslation | dict | None
    closure: TerminologyCapabilitiesClosure | dict | None


class TestReportParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    uri: Optional[Uri] = None
    display: Optional[String] = None


class TestReportSetup(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'action'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'action': 'TestReportSetupAction'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    action: TestReportSetupAction | FHIRList[TestReportSetupAction] | list | dict


class TestReportSetupAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'operation': 'TestReportSetupActionOperation',
        'assert_': 'TestReportSetupActionAssert',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    operation: TestReportSetupActionOperation | dict | None
    assert_: TestReportSetupActionAssert | dict | None


class TestReportSetupActionOperation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    result: Optional[Code] = None
    message: Optional[Markdown] = None
    detail: Optional[Uri] = None


class TestReportSetupActionAssert(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    result: Optional[Code] = None
    message: Optional[Markdown] = None
    detail: Optional[String] = None


class TestReportTest(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'action'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'action': 'TestReportTestAction'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[String] = None
    description: Optional[String] = None
    action: TestReportTestAction | FHIRList[TestReportTestAction] | list | dict


class TestReportTestAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    operation: Any = None
    assert_: Any = None


class TestReportTeardown(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'action'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'action': 'TestReportTeardownAction'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    action: TestReportTeardownAction | FHIRList[TestReportTeardownAction] | list | dict


class TestReportTeardownAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    operation: Any = None


class TestReport(FHIRResource):
    _resource_type = "TestReport"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'participant', 'test'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'testScript': 'Reference',
        'participant': 'TestReportParticipant',
        'setup': 'TestReportSetup',
        'test': 'TestReportTest',
        'teardown': 'TestReportTeardown',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | dict | None
    name: Optional[String] = None
    status: Optional[Code] = None
    testScript: Reference | dict | None
    result: Optional[Code] = None
    score: Optional[Decimal] = None
    tester: Optional[String] = None
    issued: Optional[DateTime] = None
    participant: TestReportParticipant | FHIRList[TestReportParticipant] | list | dict
    setup: TestReportSetup | dict | None
    test: TestReportTest | FHIRList[TestReportTest] | list | dict
    teardown: TestReportTeardown | dict | None


class TestScriptOrigin(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'profile': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    index: Optional[Integer] = None
    profile: Coding | dict | None


class TestScriptDestination(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'profile': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    index: Optional[Integer] = None
    profile: Coding | dict | None


class TestScriptMetadata(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'link', 'capability'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'link': 'TestScriptMetadataLink', 'capability': 'TestScriptMetadataCapability'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    link: TestScriptMetadataLink | FHIRList[TestScriptMetadataLink] | list | dict
    capability: TestScriptMetadataCapability | FHIRList[TestScriptMetadataCapability] | list | dict


class TestScriptMetadataLink(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    description: Optional[String] = None


class TestScriptMetadataCapability(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'origin', 'link'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    required: Optional[Boolean] = None
    validated: Optional[Boolean] = None
    description: Optional[String] = None
    origin: Integer | FHIRList[Integer] | list | None = None
    destination: Optional[Integer] = None
    link: Uri | FHIRList[Uri] | list | None = None
    capabilities: Optional[Canonical] = None


class TestScriptFixture(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'resource': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    autocreate: Optional[Boolean] = None
    autodelete: Optional[Boolean] = None
    resource: Reference | dict | None


class TestScriptVariable(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
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
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    action: TestScriptSetupAction | FHIRList[TestScriptSetupAction] | list | dict


class TestScriptSetupAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'operation': 'TestScriptSetupActionOperation',
        'assert_': 'TestScriptSetupActionAssert',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    operation: TestScriptSetupActionOperation | dict | None
    assert_: TestScriptSetupActionAssert | dict | None


class TestScriptSetupActionOperation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'requestHeader'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'type_': 'Coding',
        'requestHeader': 'TestScriptSetupActionOperationRequestHeader',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Coding | dict | None
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
    requestHeader: TestScriptSetupActionOperationRequestHeader | FHIRList[TestScriptSetupActionOperationRequestHeader] | list | dict
    requestId: Optional[Id] = None
    responseId: Optional[Id] = None
    sourceId: Optional[Id] = None
    targetId: Optional[Id] = None
    url: Optional[String] = None


class TestScriptSetupActionOperationRequestHeader(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    field: Optional[String] = None
    value: Optional[String] = None


class TestScriptSetupActionAssert(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
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
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    name: Optional[String] = None
    description: Optional[String] = None
    action: TestScriptTestAction | FHIRList[TestScriptTestAction] | list | dict


class TestScriptTestAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    operation: Any = None
    assert_: Any = None


class TestScriptTeardown(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'action'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'action': 'TestScriptTeardownAction'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    action: TestScriptTeardownAction | FHIRList[TestScriptTeardownAction] | list | dict


class TestScriptTeardownAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    operation: Any = None


class TestScript(FHIRResource):
    _resource_type = "TestScript"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'contact',
        'useContext',
        'jurisdiction',
        'origin',
        'destination',
        'fixture',
        'profile',
        'variable',
        'test',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'origin': 'TestScriptOrigin',
        'destination': 'TestScriptDestination',
        'metadata': 'TestScriptMetadata',
        'fixture': 'TestScriptFixture',
        'profile': 'Reference',
        'variable': 'TestScriptVariable',
        'setup': 'TestScriptSetup',
        'test': 'TestScriptTest',
        'teardown': 'TestScriptTeardown',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | dict | None
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    origin: TestScriptOrigin | FHIRList[TestScriptOrigin] | list | dict
    destination: TestScriptDestination | FHIRList[TestScriptDestination] | list | dict
    metadata: TestScriptMetadata | dict | None
    fixture: TestScriptFixture | FHIRList[TestScriptFixture] | list | dict
    profile: Reference | FHIRList[Reference] | list | dict
    variable: TestScriptVariable | FHIRList[TestScriptVariable] | list | dict
    setup: TestScriptSetup | dict | None
    test: TestScriptTest | FHIRList[TestScriptTest] | list | dict
    teardown: TestScriptTeardown | dict | None


class ValueSetCompose(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'include', 'exclude'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'include': 'ValueSetComposeInclude'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    lockedDate: Optional[Date] = None
    inactive: Optional[Boolean] = None
    include: ValueSetComposeInclude | FHIRList[ValueSetComposeInclude] | list | dict
    exclude: Any = None


class ValueSetComposeInclude(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'concept', 'filter', 'valueSet'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'concept': 'ValueSetComposeIncludeConcept',
        'filter': 'ValueSetComposeIncludeFilter',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    concept: ValueSetComposeIncludeConcept | FHIRList[ValueSetComposeIncludeConcept] | list | dict
    filter: ValueSetComposeIncludeFilter | FHIRList[ValueSetComposeIncludeFilter] | list | dict
    valueSet: Canonical | FHIRList[Canonical] | list | None = None


class ValueSetComposeIncludeConcept(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'designation'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'designation': 'ValueSetComposeIncludeConceptDesignation'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    display: Optional[String] = None
    designation: ValueSetComposeIncludeConceptDesignation | FHIRList[ValueSetComposeIncludeConceptDesignation] | list | dict


class ValueSetComposeIncludeConceptDesignation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'use': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    language: Optional[Code] = None
    use: Coding | dict | None
    value: Optional[String] = None


class ValueSetComposeIncludeFilter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    property: Optional[Code] = None
    op: Optional[Code] = None
    value: Optional[String] = None


class ValueSetExpansion(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'parameter', 'contains'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'parameter': 'ValueSetExpansionParameter',
        'contains': 'ValueSetExpansionContains',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Optional[Uri] = None
    timestamp: Optional[DateTime] = None
    total: Optional[Integer] = None
    offset: Optional[Integer] = None
    parameter: ValueSetExpansionParameter | FHIRList[ValueSetExpansionParameter] | list | dict
    contains: ValueSetExpansionContains | FHIRList[ValueSetExpansionContains] | list | dict


class ValueSetExpansionParameter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}
    _choice_fields = {'value': ['valueString', 'valueBoolean', 'valueInteger', 'valueDecimal', 'valueUri', 'valueCode', 'valueDateTime']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
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
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
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
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'compose': 'ValueSetCompose',
        'expansion': 'ValueSetExpansion',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    immutable: Optional[Boolean] = None
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    compose: ValueSetCompose | dict | None
    expansion: ValueSetExpansion | dict | None


class VerificationResultPrimarySource(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'type_', 'communicationMethod', 'pushTypeAvailable'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'who': 'Reference',
        'type_': 'CodeableConcept',
        'communicationMethod': 'CodeableConcept',
        'validationStatus': 'CodeableConcept',
        'canPushUpdates': 'CodeableConcept',
        'pushTypeAvailable': 'CodeableConcept',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    who: Reference | dict | None
    type_: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    communicationMethod: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    validationStatus: CodeableConcept | dict | None
    validationDate: Optional[DateTime] = None
    canPushUpdates: CodeableConcept | dict | None
    pushTypeAvailable: CodeableConcept | FHIRList[CodeableConcept] | list | dict


class VerificationResultAttestation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'who': 'Reference',
        'onBehalfOf': 'Reference',
        'communicationMethod': 'CodeableConcept',
        'proxySignature': 'Signature',
        'sourceSignature': 'Signature',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    who: Reference | dict | None
    onBehalfOf: Reference | dict | None
    communicationMethod: CodeableConcept | dict | None
    date: Optional[Date] = None
    sourceIdentityCertificate: Optional[String] = None
    proxyIdentityCertificate: Optional[String] = None
    proxySignature: Signature | dict | None
    sourceSignature: Signature | dict | None


class VerificationResultValidator(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'organization': 'Reference', 'attestationSignature': 'Signature'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    organization: Reference | dict | None
    identityCertificate: Optional[String] = None
    attestationSignature: Signature | dict | None


class VerificationResult(FHIRResource):
    _resource_type = "VerificationResult"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'target', 'targetLocation', 'validationProcess', 'primarySource', 'validator'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'target': 'Reference',
        'need': 'CodeableConcept',
        'validationType': 'CodeableConcept',
        'validationProcess': 'CodeableConcept',
        'frequency': 'Timing',
        'failureAction': 'CodeableConcept',
        'primarySource': 'VerificationResultPrimarySource',
        'attestation': 'VerificationResultAttestation',
        'validator': 'VerificationResultValidator',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    target: Reference | FHIRList[Reference] | list | dict
    targetLocation: String | FHIRList[String] | list | None = None
    need: CodeableConcept | dict | None
    status: Optional[Code] = None
    statusDate: Optional[DateTime] = None
    validationType: CodeableConcept | dict | None
    validationProcess: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    frequency: Timing | dict | None
    lastPerformed: Optional[DateTime] = None
    nextScheduled: Optional[Date] = None
    failureAction: CodeableConcept | dict | None
    primarySource: VerificationResultPrimarySource | FHIRList[VerificationResultPrimarySource] | list | dict
    attestation: VerificationResultAttestation | dict | None
    validator: VerificationResultValidator | FHIRList[VerificationResultValidator] | list | dict


class VisionPrescriptionLensSpecification(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'prism', 'note'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'product': 'CodeableConcept',
        'prism': 'VisionPrescriptionLensSpecificationPrism',
        'duration': 'Quantity',
        'note': 'Annotation',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    product: CodeableConcept | dict | None
    eye: Optional[Code] = None
    sphere: Optional[Decimal] = None
    cylinder: Optional[Decimal] = None
    axis: Optional[Integer] = None
    prism: VisionPrescriptionLensSpecificationPrism | FHIRList[VisionPrescriptionLensSpecificationPrism] | list | dict
    add: Optional[Decimal] = None
    power: Optional[Decimal] = None
    backCurve: Optional[Decimal] = None
    diameter: Optional[Decimal] = None
    duration: Quantity | dict | None
    color: Optional[String] = None
    brand: Optional[String] = None
    note: Annotation | FHIRList[Annotation] | list | dict


class VisionPrescriptionLensSpecificationPrism(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    amount: Optional[Decimal] = None
    base: Optional[Code] = None


class VisionPrescription(FHIRResource):
    _resource_type = "VisionPrescription"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'lensSpecification'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'patient': 'Reference',
        'encounter': 'Reference',
        'prescriber': 'Reference',
        'lensSpecification': 'VisionPrescriptionLensSpecification',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    status: Optional[Code] = None
    created: Optional[DateTime] = None
    patient: Reference | dict | None
    encounter: Reference | dict | None
    dateWritten: Optional[DateTime] = None
    prescriber: Reference | dict | None
    lensSpecification: VisionPrescriptionLensSpecification | FHIRList[VisionPrescriptionLensSpecification] | list | dict


class actualgroupCharacteristic(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueCodeableConcept': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueRange': 'Range',
        'valueReference': 'Reference',
        'period': 'Period',
    }
    _choice_fields = {'value': ['valueCodeableConcept', 'valueBoolean', 'valueQuantity', 'valueRange', 'valueReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueBoolean: Optional[Boolean] = None
    valueQuantity: Quantity | dict | None
    valueRange: Range | dict | None
    valueReference: Reference | dict | None
    exclude: Optional[Boolean] = None
    period: Period | dict | None


class actualgroupMember(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'entity': 'Reference', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    entity: Reference | dict | None
    period: Period | dict | None
    inactive: Optional[Boolean] = None


class actualgroup(FHIRResource):
    _resource_type = "actualgroup"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'member'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'code': 'CodeableConcept',
        'managingEntity': 'Reference',
        'characteristic': 'actualgroupCharacteristic',
        'member': 'actualgroupMember',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    active: Optional[Boolean] = None
    type_: Optional[Code] = None
    actual: Optional[Boolean] = None
    code: CodeableConcept | dict | None
    name: Optional[String] = None
    quantity: Optional[UnsignedInt] = None
    managingEntity: Reference | dict | None
    characteristic: actualgroupCharacteristic | dict | None
    member: actualgroupMember | FHIRList[actualgroupMember] | list | dict


class bmiCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | FHIRList[Coding] | list | dict
    text: Optional[String] = None


class bmiCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bmiCode(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | dict | None
    text: Optional[String] = None


class bmiCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bmiValue(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class bmiReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'low': 'Quantity',
        'high': 'Quantity',
        'type_': 'CodeableConcept',
        'appliesTo': 'CodeableConcept',
        'age': 'Range',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    low: Quantity | dict | None
    high: Quantity | dict | None
    type_: CodeableConcept | dict | None
    appliesTo: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    age: Range | dict | None
    text: Optional[String] = None


class bmiComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueCodeableConcept': 'CodeableConcept',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueSampledData': 'SampledData',
        'valuePeriod': 'Period',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
    }
    _choice_fields = {
        'value': [
            'valueQuantity',
            'valueCodeableConcept',
            'valueString',
            'valueBoolean',
            'valueInteger',
            'valueRange',
            'valueRatio',
            'valueSampledData',
            'valueTime',
            'valueDateTime',
            'valuePeriod',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueQuantity: Quantity | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueSampledData: SampledData | dict | None
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Period | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    referenceRange: Any = None


class bmi(FHIRResource):
    _resource_type = "bmi"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'basedOn',
        'partOf',
        'focus',
        'performer',
        'interpretation',
        'note',
        'referenceRange',
        'hasMember',
        'derivedFrom',
        'component',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'focus': 'Reference',
        'encounter': 'Reference',
        'effectivePeriod': 'Period',
        'performer': 'Reference',
        'valueQuantity': 'Quantity',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
        'note': 'Annotation',
        'bodySite': 'CodeableConcept',
        'method': 'CodeableConcept',
        'specimen': 'Reference',
        'device': 'Reference',
        'referenceRange': 'bmiReferenceRange',
        'hasMember': 'Reference',
        'derivedFrom': 'Reference',
        'component': 'bmiComponent',
    }
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'value': ['valueQuantity']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | dict | None
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    focus: Reference | FHIRList[Reference] | list | dict
    encounter: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference] | list | dict
    valueQuantity: Quantity | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    bodySite: CodeableConcept | dict | None
    method: CodeableConcept | dict | None
    specimen: Reference | dict | None
    device: Reference | dict | None
    referenceRange: bmiReferenceRange | FHIRList[bmiReferenceRange] | list | dict
    hasMember: Reference | FHIRList[Reference] | list | dict
    derivedFrom: Reference | FHIRList[Reference] | list | dict
    component: bmiComponent | FHIRList[bmiComponent] | list | dict


class bodyheightCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | FHIRList[Coding] | list | dict
    text: Optional[String] = None


class bodyheightCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bodyheightCode(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | dict | None
    text: Optional[String] = None


class bodyheightCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bodyheightValue(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class bodyheightReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'low': 'Quantity',
        'high': 'Quantity',
        'type_': 'CodeableConcept',
        'appliesTo': 'CodeableConcept',
        'age': 'Range',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    low: Quantity | dict | None
    high: Quantity | dict | None
    type_: CodeableConcept | dict | None
    appliesTo: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    age: Range | dict | None
    text: Optional[String] = None


class bodyheightComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueCodeableConcept': 'CodeableConcept',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueSampledData': 'SampledData',
        'valuePeriod': 'Period',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
    }
    _choice_fields = {
        'value': [
            'valueQuantity',
            'valueCodeableConcept',
            'valueString',
            'valueBoolean',
            'valueInteger',
            'valueRange',
            'valueRatio',
            'valueSampledData',
            'valueTime',
            'valueDateTime',
            'valuePeriod',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueQuantity: Quantity | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueSampledData: SampledData | dict | None
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Period | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    referenceRange: Any = None


class bodyheight(FHIRResource):
    _resource_type = "bodyheight"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'basedOn',
        'partOf',
        'focus',
        'performer',
        'interpretation',
        'note',
        'referenceRange',
        'hasMember',
        'derivedFrom',
        'component',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'focus': 'Reference',
        'encounter': 'Reference',
        'effectivePeriod': 'Period',
        'performer': 'Reference',
        'valueQuantity': 'Quantity',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
        'note': 'Annotation',
        'bodySite': 'CodeableConcept',
        'method': 'CodeableConcept',
        'specimen': 'Reference',
        'device': 'Reference',
        'referenceRange': 'bodyheightReferenceRange',
        'hasMember': 'Reference',
        'derivedFrom': 'Reference',
        'component': 'bodyheightComponent',
    }
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'value': ['valueQuantity']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | dict | None
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    focus: Reference | FHIRList[Reference] | list | dict
    encounter: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference] | list | dict
    valueQuantity: Quantity | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    bodySite: CodeableConcept | dict | None
    method: CodeableConcept | dict | None
    specimen: Reference | dict | None
    device: Reference | dict | None
    referenceRange: bodyheightReferenceRange | FHIRList[bodyheightReferenceRange] | list | dict
    hasMember: Reference | FHIRList[Reference] | list | dict
    derivedFrom: Reference | FHIRList[Reference] | list | dict
    component: bodyheightComponent | FHIRList[bodyheightComponent] | list | dict


class bodytempCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | FHIRList[Coding] | list | dict
    text: Optional[String] = None


class bodytempCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bodytempCode(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | dict | None
    text: Optional[String] = None


class bodytempCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bodytempValue(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class bodytempReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'low': 'Quantity',
        'high': 'Quantity',
        'type_': 'CodeableConcept',
        'appliesTo': 'CodeableConcept',
        'age': 'Range',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    low: Quantity | dict | None
    high: Quantity | dict | None
    type_: CodeableConcept | dict | None
    appliesTo: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    age: Range | dict | None
    text: Optional[String] = None


class bodytempComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueCodeableConcept': 'CodeableConcept',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueSampledData': 'SampledData',
        'valuePeriod': 'Period',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
    }
    _choice_fields = {
        'value': [
            'valueQuantity',
            'valueCodeableConcept',
            'valueString',
            'valueBoolean',
            'valueInteger',
            'valueRange',
            'valueRatio',
            'valueSampledData',
            'valueTime',
            'valueDateTime',
            'valuePeriod',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueQuantity: Quantity | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueSampledData: SampledData | dict | None
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Period | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    referenceRange: Any = None


class bodytemp(FHIRResource):
    _resource_type = "bodytemp"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'basedOn',
        'partOf',
        'focus',
        'performer',
        'interpretation',
        'note',
        'referenceRange',
        'hasMember',
        'derivedFrom',
        'component',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'focus': 'Reference',
        'encounter': 'Reference',
        'effectivePeriod': 'Period',
        'performer': 'Reference',
        'valueQuantity': 'Quantity',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
        'note': 'Annotation',
        'bodySite': 'CodeableConcept',
        'method': 'CodeableConcept',
        'specimen': 'Reference',
        'device': 'Reference',
        'referenceRange': 'bodytempReferenceRange',
        'hasMember': 'Reference',
        'derivedFrom': 'Reference',
        'component': 'bodytempComponent',
    }
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'value': ['valueQuantity']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | dict | None
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    focus: Reference | FHIRList[Reference] | list | dict
    encounter: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference] | list | dict
    valueQuantity: Quantity | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    bodySite: CodeableConcept | dict | None
    method: CodeableConcept | dict | None
    specimen: Reference | dict | None
    device: Reference | dict | None
    referenceRange: bodytempReferenceRange | FHIRList[bodytempReferenceRange] | list | dict
    hasMember: Reference | FHIRList[Reference] | list | dict
    derivedFrom: Reference | FHIRList[Reference] | list | dict
    component: bodytempComponent | FHIRList[bodytempComponent] | list | dict


class bodyweightCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | FHIRList[Coding] | list | dict
    text: Optional[String] = None


class bodyweightCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bodyweightCode(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | dict | None
    text: Optional[String] = None


class bodyweightCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bodyweightValue(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class bodyweightReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'low': 'Quantity',
        'high': 'Quantity',
        'type_': 'CodeableConcept',
        'appliesTo': 'CodeableConcept',
        'age': 'Range',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    low: Quantity | dict | None
    high: Quantity | dict | None
    type_: CodeableConcept | dict | None
    appliesTo: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    age: Range | dict | None
    text: Optional[String] = None


class bodyweightComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueCodeableConcept': 'CodeableConcept',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueSampledData': 'SampledData',
        'valuePeriod': 'Period',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
    }
    _choice_fields = {
        'value': [
            'valueQuantity',
            'valueCodeableConcept',
            'valueString',
            'valueBoolean',
            'valueInteger',
            'valueRange',
            'valueRatio',
            'valueSampledData',
            'valueTime',
            'valueDateTime',
            'valuePeriod',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueQuantity: Quantity | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueSampledData: SampledData | dict | None
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Period | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    referenceRange: Any = None


class bodyweight(FHIRResource):
    _resource_type = "bodyweight"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'basedOn',
        'partOf',
        'focus',
        'performer',
        'interpretation',
        'note',
        'referenceRange',
        'hasMember',
        'derivedFrom',
        'component',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'focus': 'Reference',
        'encounter': 'Reference',
        'effectivePeriod': 'Period',
        'performer': 'Reference',
        'valueQuantity': 'Quantity',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
        'note': 'Annotation',
        'bodySite': 'CodeableConcept',
        'method': 'CodeableConcept',
        'specimen': 'Reference',
        'device': 'Reference',
        'referenceRange': 'bodyweightReferenceRange',
        'hasMember': 'Reference',
        'derivedFrom': 'Reference',
        'component': 'bodyweightComponent',
    }
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'value': ['valueQuantity']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | dict | None
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    focus: Reference | FHIRList[Reference] | list | dict
    encounter: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference] | list | dict
    valueQuantity: Quantity | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    bodySite: CodeableConcept | dict | None
    method: CodeableConcept | dict | None
    specimen: Reference | dict | None
    device: Reference | dict | None
    referenceRange: bodyweightReferenceRange | FHIRList[bodyweightReferenceRange] | list | dict
    hasMember: Reference | FHIRList[Reference] | list | dict
    derivedFrom: Reference | FHIRList[Reference] | list | dict
    component: bodyweightComponent | FHIRList[bodyweightComponent] | list | dict


class bpCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | FHIRList[Coding] | list | dict
    text: Optional[String] = None


class bpCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bpCode(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | dict | None
    text: Optional[String] = None


class bpCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bpReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'low': 'Quantity',
        'high': 'Quantity',
        'type_': 'CodeableConcept',
        'appliesTo': 'CodeableConcept',
        'age': 'Range',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    low: Quantity | dict | None
    high: Quantity | dict | None
    type_: CodeableConcept | dict | None
    appliesTo: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    age: Range | dict | None
    text: Optional[String] = None


class bpComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueCodeableConcept': 'CodeableConcept',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueSampledData': 'SampledData',
        'valuePeriod': 'Period',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
    }
    _choice_fields = {'value': ['valueQuantity']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueQuantity: Quantity | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueSampledData: SampledData | dict | None
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Period | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    referenceRange: Any = None


class bpComponentCode(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | dict | None
    text: Optional[String] = None


class bpComponentCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class bpComponentValue(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class bp(FHIRResource):
    _resource_type = "bp"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'basedOn',
        'partOf',
        'focus',
        'performer',
        'interpretation',
        'note',
        'referenceRange',
        'hasMember',
        'derivedFrom',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'focus': 'Reference',
        'encounter': 'Reference',
        'effectivePeriod': 'Period',
        'performer': 'Reference',
        'valueQuantity': 'Quantity',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
        'note': 'Annotation',
        'bodySite': 'CodeableConcept',
        'method': 'CodeableConcept',
        'specimen': 'Reference',
        'device': 'Reference',
        'referenceRange': 'bpReferenceRange',
        'hasMember': 'Reference',
        'derivedFrom': 'Reference',
        'component': 'bpComponent',
    }
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'value': ['valueQuantity']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | dict | None
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    focus: Reference | FHIRList[Reference] | list | dict
    encounter: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference] | list | dict
    valueQuantity: Quantity | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    bodySite: CodeableConcept | dict | None
    method: CodeableConcept | dict | None
    specimen: Reference | dict | None
    device: Reference | dict | None
    referenceRange: bpReferenceRange | FHIRList[bpReferenceRange] | list | dict
    hasMember: Reference | FHIRList[Reference] | list | dict
    derivedFrom: Reference | FHIRList[Reference] | list | dict
    component: bpComponent | dict | None


class catalogAttester(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'party': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    mode: Optional[Code] = None
    time: Optional[DateTime] = None
    party: Reference | dict | None


class catalogRelatesTo(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'targetIdentifier': 'Identifier', 'targetReference': 'Reference'}
    _choice_fields = {'target': ['targetIdentifier', 'targetReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    targetIdentifier: Identifier | dict | None
    targetReference: Reference | dict | None


class catalogEvent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'detail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'period': 'Period', 'detail': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    period: Period | dict | None
    detail: Reference | FHIRList[Reference] | list | dict


class catalogSection(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'author', 'entry', 'section'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'author': 'Reference',
        'focus': 'Reference',
        'text': 'Narrative',
        'orderedBy': 'CodeableConcept',
        'entry': 'Reference',
        'emptyReason': 'CodeableConcept',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    title: Optional[String] = None
    code: CodeableConcept | dict | None
    author: Reference | FHIRList[Reference] | list | dict
    focus: Reference | dict | None
    text: Narrative | dict | None
    mode: Optional[Code] = None
    orderedBy: CodeableConcept | dict | None
    entry: Reference | FHIRList[Reference] | list | dict
    emptyReason: CodeableConcept | dict | None
    section: Any = None


class catalog(FHIRResource):
    _resource_type = "catalog"
    _list_fields = {'contained', 'modifierExtension', 'author', 'attester', 'relatesTo', 'event', 'section'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'category': 'CodeableConcept',
        'subject': 'Reference',
        'encounter': 'Reference',
        'author': 'Reference',
        'attester': 'catalogAttester',
        'custodian': 'Reference',
        'relatesTo': 'catalogRelatesTo',
        'event': 'catalogEvent',
        'section': 'catalogSection',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | dict | None
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | dict | None
    status: Optional[Code] = None
    type_: CodeableConcept | dict | None
    category: CodeableConcept | dict | None
    subject: Reference | dict | None
    encounter: Reference | dict | None
    date: Optional[DateTime] = None
    author: Reference | FHIRList[Reference] | list | dict
    title: Optional[String] = None
    confidentiality: Optional[Code] = None
    attester: catalogAttester | FHIRList[catalogAttester] | list | dict
    custodian: Reference | dict | None
    relatesTo: catalogRelatesTo | FHIRList[catalogRelatesTo] | list | dict
    event: catalogEvent | FHIRList[catalogEvent] | list | dict
    section: catalogSection | FHIRList[catalogSection] | list | dict


class cdshooksguidanceresponse(FHIRResource):
    _resource_type = "cdshooksguidanceresponse"
    _list_fields = {'contained', 'modifierExtension', 'reasonCode', 'reasonReference', 'note', 'evaluationMessage', 'dataRequirement'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'requestIdentifier': 'Identifier',
        'identifier': 'Identifier',
        'subject': 'Reference',
        'encounter': 'Reference',
        'performer': 'Reference',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'note': 'Annotation',
        'evaluationMessage': 'Reference',
        'outputParameters': 'Reference',
        'result': 'Reference',
        'dataRequirement': 'DataRequirement',
    }
    _choice_fields = {'module': ['moduleUri']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | dict | None
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    requestIdentifier: Identifier | dict | None
    identifier: Identifier | dict | None
    moduleUri: Optional[Uri] = None
    status: Optional[Code] = None
    subject: Reference | dict | None
    encounter: Reference | dict | None
    occurrenceDateTime: Optional[DateTime] = None
    performer: Reference | dict | None
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    evaluationMessage: Reference | FHIRList[Reference] | list | dict
    outputParameters: Reference | dict | None
    result: Reference | dict | None
    dataRequirement: DataRequirement | FHIRList[DataRequirement] | list | dict


class cdshooksrequestgroupAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'documentation', 'condition', 'relatedAction', 'participant', 'action'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'documentation': 'RelatedArtifact',
        'condition': 'cdshooksrequestgroupActionCondition',
        'relatedAction': 'cdshooksrequestgroupActionRelatedAction',
        'timingAge': 'Age',
        'timingPeriod': 'Period',
        'timingDuration': 'Duration',
        'timingRange': 'Range',
        'timingTiming': 'Timing',
        'participant': 'Reference',
        'type_': 'CodeableConcept',
        'resource': 'Reference',
    }
    _choice_fields = {'timing': ['timingDateTime', 'timingAge', 'timingPeriod', 'timingDuration', 'timingRange', 'timingTiming']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    prefix: Optional[String] = None
    title: Optional[String] = None
    description: Optional[String] = None
    textEquivalent: Optional[String] = None
    priority: Optional[Code] = None
    code: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    documentation: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    condition: cdshooksrequestgroupActionCondition | FHIRList[cdshooksrequestgroupActionCondition] | list | dict
    relatedAction: cdshooksrequestgroupActionRelatedAction | FHIRList[cdshooksrequestgroupActionRelatedAction] | list | dict
    timingDateTime: Optional[DateTime] = None
    timingAge: Age | dict | None
    timingPeriod: Period | dict | None
    timingDuration: Duration | dict | None
    timingRange: Range | dict | None
    timingTiming: Timing | dict | None
    participant: Reference | FHIRList[Reference] | list | dict
    type_: CodeableConcept | dict | None
    groupingBehavior: Optional[Code] = None
    selectionBehavior: Optional[Code] = None
    requiredBehavior: Optional[Code] = None
    precheckBehavior: Optional[Code] = None
    cardinalityBehavior: Optional[Code] = None
    resource: Reference | dict | None
    action: Any = None


class cdshooksrequestgroupActionCondition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    kind: Optional[Code] = None
    expression: Expression | dict | None


class cdshooksrequestgroupActionRelatedAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'offsetDuration': 'Duration', 'offsetRange': 'Range'}
    _choice_fields = {'offset': ['offsetDuration', 'offsetRange']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    actionId: Optional[Id] = None
    relationship: Optional[Code] = None
    offsetDuration: Duration | dict | None
    offsetRange: Range | dict | None


class cdshooksrequestgroup(FHIRResource):
    _resource_type = "cdshooksrequestgroup"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'instantiatesCanonical',
        'basedOn',
        'replaces',
        'reasonCode',
        'reasonReference',
        'note',
        'action',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'replaces': 'Reference',
        'groupIdentifier': 'Identifier',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'encounter': 'Reference',
        'author': 'Reference',
        'reasonCode': 'CodeableConcept',
        'reasonReference': 'Reference',
        'note': 'Annotation',
        'action': 'cdshooksrequestgroupAction',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | dict | None
    instantiatesCanonical: Canonical | FHIRList[Canonical] | list | None = None
    instantiatesUri: Optional[Uri] = None
    basedOn: Reference | FHIRList[Reference] | list | dict
    replaces: Reference | FHIRList[Reference] | list | dict
    groupIdentifier: Identifier | dict | None
    status: Optional[Code] = None
    intent: Optional[Code] = None
    priority: Optional[Code] = None
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    encounter: Reference | dict | None
    authoredOn: Optional[DateTime] = None
    author: Reference | dict | None
    reasonCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reasonReference: Reference | FHIRList[Reference] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    action: cdshooksrequestgroupAction | FHIRList[cdshooksrequestgroupAction] | list | dict


class cdshooksserviceplandefinitionGoal(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'addresses', 'documentation', 'target'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'category': 'CodeableConcept',
        'description': 'CodeableConcept',
        'priority': 'CodeableConcept',
        'start': 'CodeableConcept',
        'addresses': 'CodeableConcept',
        'documentation': 'RelatedArtifact',
        'target': 'cdshooksserviceplandefinitionGoalTarget',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    category: CodeableConcept | dict | None
    description: CodeableConcept | dict | None
    priority: CodeableConcept | dict | None
    start: CodeableConcept | dict | None
    addresses: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    documentation: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    target: cdshooksserviceplandefinitionGoalTarget | FHIRList[cdshooksserviceplandefinitionGoalTarget] | list | dict


class cdshooksserviceplandefinitionGoalTarget(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'measure': 'CodeableConcept',
        'detailQuantity': 'Quantity',
        'detailRange': 'Range',
        'detailCodeableConcept': 'CodeableConcept',
        'due': 'Duration',
    }
    _choice_fields = {'detail': ['detailQuantity', 'detailRange', 'detailCodeableConcept']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    measure: CodeableConcept | dict | None
    detailQuantity: Quantity | dict | None
    detailRange: Range | dict | None
    detailCodeableConcept: CodeableConcept | dict | None
    due: Duration | dict | None


class cdshooksserviceplandefinitionAction(FHIRElement):
    _list_fields = {
        'extension',
        'modifierExtension',
        'code',
        'reason',
        'documentation',
        'goalId',
        'trigger',
        'condition',
        'input',
        'output',
        'relatedAction',
        'participant',
        'dynamicValue',
        'action',
    }
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'reason': 'CodeableConcept',
        'documentation': 'RelatedArtifact',
        'subjectCodeableConcept': 'CodeableConcept',
        'subjectReference': 'Reference',
        'trigger': 'TriggerDefinition',
        'condition': 'cdshooksserviceplandefinitionActionCondition',
        'input': 'DataRequirement',
        'output': 'DataRequirement',
        'relatedAction': 'cdshooksserviceplandefinitionActionRelatedAction',
        'timingAge': 'Age',
        'timingPeriod': 'Period',
        'timingDuration': 'Duration',
        'timingRange': 'Range',
        'timingTiming': 'Timing',
        'participant': 'cdshooksserviceplandefinitionActionParticipant',
        'type_': 'CodeableConcept',
        'dynamicValue': 'cdshooksserviceplandefinitionActionDynamicValue',
    }
    _choice_fields = {
        'definition': ['definitionCanonical', 'definitionUri'],
        'subject': ['subjectCodeableConcept', 'subjectReference'],
        'timing': ['timingDateTime', 'timingAge', 'timingPeriod', 'timingDuration', 'timingRange', 'timingTiming'],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    prefix: Optional[String] = None
    title: Optional[String] = None
    description: Optional[String] = None
    textEquivalent: Optional[String] = None
    priority: Optional[Code] = None
    code: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reason: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    documentation: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    goalId: Id | FHIRList[Id] | list | None = None
    subjectCodeableConcept: CodeableConcept | dict | None
    subjectReference: Reference | dict | None
    trigger: TriggerDefinition | FHIRList[TriggerDefinition] | list | dict
    condition: cdshooksserviceplandefinitionActionCondition | FHIRList[cdshooksserviceplandefinitionActionCondition] | list | dict
    input: DataRequirement | FHIRList[DataRequirement] | list | dict
    output: DataRequirement | FHIRList[DataRequirement] | list | dict
    relatedAction: cdshooksserviceplandefinitionActionRelatedAction | FHIRList[cdshooksserviceplandefinitionActionRelatedAction] | list | dict
    timingDateTime: Optional[DateTime] = None
    timingAge: Age | dict | None
    timingPeriod: Period | dict | None
    timingDuration: Duration | dict | None
    timingRange: Range | dict | None
    timingTiming: Timing | dict | None
    participant: cdshooksserviceplandefinitionActionParticipant | FHIRList[cdshooksserviceplandefinitionActionParticipant] | list | dict
    type_: CodeableConcept | dict | None
    groupingBehavior: Optional[Code] = None
    selectionBehavior: Optional[Code] = None
    requiredBehavior: Optional[Code] = None
    precheckBehavior: Optional[Code] = None
    cardinalityBehavior: Optional[Code] = None
    definitionCanonical: Optional[Canonical] = None
    definitionUri: Optional[Uri] = None
    transform: Optional[Canonical] = None
    dynamicValue: cdshooksserviceplandefinitionActionDynamicValue | FHIRList[cdshooksserviceplandefinitionActionDynamicValue] | list | dict
    action: Any = None


class cdshooksserviceplandefinitionActionCondition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    kind: Optional[Code] = None
    expression: Expression | dict | None


class cdshooksserviceplandefinitionActionRelatedAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'offsetDuration': 'Duration', 'offsetRange': 'Range'}
    _choice_fields = {'offset': ['offsetDuration', 'offsetRange']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    actionId: Optional[Id] = None
    relationship: Optional[Code] = None
    offsetDuration: Duration | dict | None
    offsetRange: Range | dict | None


class cdshooksserviceplandefinitionActionParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'role': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    role: CodeableConcept | dict | None


class cdshooksserviceplandefinitionActionDynamicValue(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    path: Optional[String] = None
    expression: Expression | dict | None


class cdshooksserviceplandefinition(FHIRResource):
    _resource_type = "cdshooksserviceplandefinition"
    _list_fields = {
        'contained',
        'modifierExtension',
        'identifier',
        'contact',
        'useContext',
        'jurisdiction',
        'topic',
        'author',
        'editor',
        'reviewer',
        'endorser',
        'relatedArtifact',
        'library',
        'goal',
        'action',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'subjectCodeableConcept': 'CodeableConcept',
        'subjectReference': 'Reference',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'topic': 'CodeableConcept',
        'author': 'ContactDetail',
        'editor': 'ContactDetail',
        'reviewer': 'ContactDetail',
        'endorser': 'ContactDetail',
        'relatedArtifact': 'RelatedArtifact',
        'goal': 'cdshooksserviceplandefinitionGoal',
        'action': 'cdshooksserviceplandefinitionAction',
    }
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | dict | None
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    type_: CodeableConcept | dict | None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    subjectCodeableConcept: CodeableConcept | dict | None
    subjectReference: Reference | dict | None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    topic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    author: ContactDetail | FHIRList[ContactDetail] | list | dict
    editor: ContactDetail | FHIRList[ContactDetail] | list | dict
    reviewer: ContactDetail | FHIRList[ContactDetail] | list | dict
    endorser: ContactDetail | FHIRList[ContactDetail] | list | dict
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    library: Canonical | FHIRList[Canonical] | list | None = None
    goal: cdshooksserviceplandefinitionGoal | FHIRList[cdshooksserviceplandefinitionGoal] | list | dict
    action: cdshooksserviceplandefinitionAction | FHIRList[cdshooksserviceplandefinitionAction] | list | dict


class cholesterolValue(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class cholesterolReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'low': 'Quantity',
        'high': 'Quantity',
        'type_': 'CodeableConcept',
        'appliesTo': 'CodeableConcept',
        'age': 'Range',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    low: Quantity | dict | None
    high: Quantity | dict | None
    type_: CodeableConcept | dict | None
    appliesTo: CodeableConcept | dict | None
    age: Range | dict | None
    text: Optional[String] = None


class cholesterolComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueCodeableConcept': 'CodeableConcept',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueSampledData': 'SampledData',
        'valuePeriod': 'Period',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
    }
    _choice_fields = {
        'value': [
            'valueQuantity',
            'valueCodeableConcept',
            'valueString',
            'valueBoolean',
            'valueInteger',
            'valueRange',
            'valueRatio',
            'valueSampledData',
            'valueTime',
            'valueDateTime',
            'valuePeriod',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueQuantity: Quantity | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueSampledData: SampledData | dict | None
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Period | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    referenceRange: Any = None


class cholesterol(FHIRResource):
    _resource_type = "cholesterol"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'note', 'component'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'focus': 'Reference',
        'encounter': 'Reference',
        'effectivePeriod': 'Period',
        'effectiveTiming': 'Timing',
        'performer': 'Reference',
        'valueQuantity': 'Quantity',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
        'note': 'Annotation',
        'bodySite': 'CodeableConcept',
        'method': 'CodeableConcept',
        'specimen': 'Reference',
        'device': 'Reference',
        'referenceRange': 'cholesterolReferenceRange',
        'hasMember': 'Reference',
        'derivedFrom': 'Reference',
        'component': 'cholesterolComponent',
    }
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod', 'effectiveTiming', 'effectiveInstant'], 'value': ['valueQuantity']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    focus: Reference | FHIRList[Reference] | list | dict
    encounter: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    effectiveTiming: Timing | dict | None
    effectiveInstant: Optional[Instant] = None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference] | list | dict
    valueQuantity: Quantity | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | dict | None
    note: Annotation | FHIRList[Annotation] | list | dict
    bodySite: CodeableConcept | dict | None
    method: CodeableConcept | dict | None
    specimen: Reference | dict | None
    device: Reference | dict | None
    referenceRange: cholesterolReferenceRange | dict | None
    hasMember: Reference | dict | None
    derivedFrom: Reference | dict | None
    component: cholesterolComponent | FHIRList[cholesterolComponent] | list | dict


class clinicaldocumentAttester(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'party': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    mode: Optional[Code] = None
    time: Optional[DateTime] = None
    party: Reference | dict | None


class clinicaldocumentRelatesTo(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'targetIdentifier': 'Identifier', 'targetReference': 'Reference'}
    _choice_fields = {'target': ['targetIdentifier', 'targetReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    targetIdentifier: Identifier | dict | None
    targetReference: Reference | dict | None


class clinicaldocumentEvent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'code', 'detail'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'period': 'Period', 'detail': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    period: Period | dict | None
    detail: Reference | FHIRList[Reference] | list | dict


class clinicaldocumentSection(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'author', 'entry', 'section'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'author': 'Reference',
        'focus': 'Reference',
        'text': 'Narrative',
        'orderedBy': 'CodeableConcept',
        'entry': 'Reference',
        'emptyReason': 'CodeableConcept',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    title: Optional[String] = None
    code: CodeableConcept | dict | None
    author: Reference | FHIRList[Reference] | list | dict
    focus: Reference | dict | None
    text: Narrative | dict | None
    mode: Optional[Code] = None
    orderedBy: CodeableConcept | dict | None
    entry: Reference | FHIRList[Reference] | list | dict
    emptyReason: CodeableConcept | dict | None
    section: Any = None


class clinicaldocument(FHIRResource):
    _resource_type = "clinicaldocument"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'category', 'author', 'attester', 'relatesTo', 'event', 'section'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'category': 'CodeableConcept',
        'subject': 'Reference',
        'encounter': 'Reference',
        'author': 'Reference',
        'attester': 'clinicaldocumentAttester',
        'custodian': 'Reference',
        'relatesTo': 'clinicaldocumentRelatesTo',
        'event': 'clinicaldocumentEvent',
        'section': 'clinicaldocumentSection',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | dict | None
    status: Optional[Code] = None
    type_: CodeableConcept | dict | None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    subject: Reference | dict | None
    encounter: Reference | dict | None
    date: Optional[DateTime] = None
    author: Reference | FHIRList[Reference] | list | dict
    title: Optional[String] = None
    confidentiality: Optional[Code] = None
    attester: clinicaldocumentAttester | FHIRList[clinicaldocumentAttester] | list | dict
    custodian: Reference | dict | None
    relatesTo: clinicaldocumentRelatesTo | FHIRList[clinicaldocumentRelatesTo] | list | dict
    event: clinicaldocumentEvent | FHIRList[clinicaldocumentEvent] | list | dict
    section: clinicaldocumentSection | FHIRList[clinicaldocumentSection] | list | dict


class computableplandefinitionGoal(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'addresses', 'documentation', 'target'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'category': 'CodeableConcept',
        'description': 'CodeableConcept',
        'priority': 'CodeableConcept',
        'start': 'CodeableConcept',
        'addresses': 'CodeableConcept',
        'documentation': 'RelatedArtifact',
        'target': 'computableplandefinitionGoalTarget',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    category: CodeableConcept | dict | None
    description: CodeableConcept | dict | None
    priority: CodeableConcept | dict | None
    start: CodeableConcept | dict | None
    addresses: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    documentation: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    target: computableplandefinitionGoalTarget | FHIRList[computableplandefinitionGoalTarget] | list | dict


class computableplandefinitionGoalTarget(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'measure': 'CodeableConcept',
        'detailQuantity': 'Quantity',
        'detailRange': 'Range',
        'detailCodeableConcept': 'CodeableConcept',
        'due': 'Duration',
    }
    _choice_fields = {'detail': ['detailQuantity', 'detailRange', 'detailCodeableConcept']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    measure: CodeableConcept | dict | None
    detailQuantity: Quantity | dict | None
    detailRange: Range | dict | None
    detailCodeableConcept: CodeableConcept | dict | None
    due: Duration | dict | None


class computableplandefinitionAction(FHIRElement):
    _list_fields = {
        'extension',
        'modifierExtension',
        'code',
        'reason',
        'documentation',
        'goalId',
        'trigger',
        'condition',
        'input',
        'output',
        'relatedAction',
        'participant',
        'dynamicValue',
        'action',
    }
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'reason': 'CodeableConcept',
        'documentation': 'RelatedArtifact',
        'subjectCodeableConcept': 'CodeableConcept',
        'subjectReference': 'Reference',
        'trigger': 'TriggerDefinition',
        'condition': 'computableplandefinitionActionCondition',
        'input': 'DataRequirement',
        'output': 'DataRequirement',
        'relatedAction': 'computableplandefinitionActionRelatedAction',
        'timingAge': 'Age',
        'timingPeriod': 'Period',
        'timingDuration': 'Duration',
        'timingRange': 'Range',
        'timingTiming': 'Timing',
        'participant': 'computableplandefinitionActionParticipant',
        'type_': 'CodeableConcept',
        'dynamicValue': 'computableplandefinitionActionDynamicValue',
    }
    _choice_fields = {
        'definition': ['definitionCanonical', 'definitionUri'],
        'subject': ['subjectCodeableConcept', 'subjectReference'],
        'timing': ['timingDateTime', 'timingAge', 'timingPeriod', 'timingDuration', 'timingRange', 'timingTiming'],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    prefix: Optional[String] = None
    title: Optional[String] = None
    description: Optional[String] = None
    textEquivalent: Optional[String] = None
    priority: Optional[Code] = None
    code: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reason: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    documentation: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    goalId: Id | FHIRList[Id] | list | None = None
    subjectCodeableConcept: CodeableConcept | dict | None
    subjectReference: Reference | dict | None
    trigger: TriggerDefinition | FHIRList[TriggerDefinition] | list | dict
    condition: computableplandefinitionActionCondition | FHIRList[computableplandefinitionActionCondition] | list | dict
    input: DataRequirement | FHIRList[DataRequirement] | list | dict
    output: DataRequirement | FHIRList[DataRequirement] | list | dict
    relatedAction: computableplandefinitionActionRelatedAction | FHIRList[computableplandefinitionActionRelatedAction] | list | dict
    timingDateTime: Optional[DateTime] = None
    timingAge: Age | dict | None
    timingPeriod: Period | dict | None
    timingDuration: Duration | dict | None
    timingRange: Range | dict | None
    timingTiming: Timing | dict | None
    participant: computableplandefinitionActionParticipant | FHIRList[computableplandefinitionActionParticipant] | list | dict
    type_: CodeableConcept | dict | None
    groupingBehavior: Optional[Code] = None
    selectionBehavior: Optional[Code] = None
    requiredBehavior: Optional[Code] = None
    precheckBehavior: Optional[Code] = None
    cardinalityBehavior: Optional[Code] = None
    definitionCanonical: Optional[Canonical] = None
    definitionUri: Optional[Uri] = None
    transform: Optional[Canonical] = None
    dynamicValue: computableplandefinitionActionDynamicValue | FHIRList[computableplandefinitionActionDynamicValue] | list | dict
    action: Any = None


class computableplandefinitionActionCondition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    kind: Optional[Code] = None
    expression: Expression | dict | None


class computableplandefinitionActionRelatedAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'offsetDuration': 'Duration', 'offsetRange': 'Range'}
    _choice_fields = {'offset': ['offsetDuration', 'offsetRange']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    actionId: Optional[Id] = None
    relationship: Optional[Code] = None
    offsetDuration: Duration | dict | None
    offsetRange: Range | dict | None


class computableplandefinitionActionParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'role': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    role: CodeableConcept | dict | None


class computableplandefinitionActionDynamicValue(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    path: Optional[String] = None
    expression: Expression | dict | None


class computableplandefinition(FHIRResource):
    _resource_type = "computableplandefinition"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'contact',
        'useContext',
        'jurisdiction',
        'topic',
        'author',
        'editor',
        'reviewer',
        'endorser',
        'relatedArtifact',
        'goal',
        'action',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'subjectCodeableConcept': 'CodeableConcept',
        'subjectReference': 'Reference',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'topic': 'CodeableConcept',
        'author': 'ContactDetail',
        'editor': 'ContactDetail',
        'reviewer': 'ContactDetail',
        'endorser': 'ContactDetail',
        'relatedArtifact': 'RelatedArtifact',
        'goal': 'computableplandefinitionGoal',
        'action': 'computableplandefinitionAction',
    }
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    type_: CodeableConcept | dict | None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    subjectCodeableConcept: CodeableConcept | dict | None
    subjectReference: Reference | dict | None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    topic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    author: ContactDetail | FHIRList[ContactDetail] | list | dict
    editor: ContactDetail | FHIRList[ContactDetail] | list | dict
    reviewer: ContactDetail | FHIRList[ContactDetail] | list | dict
    endorser: ContactDetail | FHIRList[ContactDetail] | list | dict
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    library: Optional[Canonical] = None
    goal: computableplandefinitionGoal | FHIRList[computableplandefinitionGoal] | list | dict
    action: computableplandefinitionAction | FHIRList[computableplandefinitionAction] | list | dict


class cqllibrary(FHIRResource):
    _resource_type = "cqllibrary"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'contact',
        'useContext',
        'jurisdiction',
        'topic',
        'author',
        'editor',
        'reviewer',
        'endorser',
        'relatedArtifact',
        'parameter',
        'dataRequirement',
        'content',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'subjectCodeableConcept': 'CodeableConcept',
        'subjectReference': 'Reference',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'topic': 'CodeableConcept',
        'author': 'ContactDetail',
        'editor': 'ContactDetail',
        'reviewer': 'ContactDetail',
        'endorser': 'ContactDetail',
        'relatedArtifact': 'RelatedArtifact',
        'parameter': 'ParameterDefinition',
        'dataRequirement': 'DataRequirement',
        'content': 'Attachment',
    }
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    type_: CodeableConcept | dict | None
    subjectCodeableConcept: CodeableConcept | dict | None
    subjectReference: Reference | dict | None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    topic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    author: ContactDetail | FHIRList[ContactDetail] | list | dict
    editor: ContactDetail | FHIRList[ContactDetail] | list | dict
    reviewer: ContactDetail | FHIRList[ContactDetail] | list | dict
    endorser: ContactDetail | FHIRList[ContactDetail] | list | dict
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    parameter: ParameterDefinition | FHIRList[ParameterDefinition] | list | dict
    dataRequirement: DataRequirement | FHIRList[DataRequirement] | list | dict
    content: Attachment | FHIRList[Attachment] | list | dict


class devicemetricobservationReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'low': 'Quantity',
        'high': 'Quantity',
        'type_': 'CodeableConcept',
        'appliesTo': 'CodeableConcept',
        'age': 'Range',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    low: Quantity | dict | None
    high: Quantity | dict | None
    type_: CodeableConcept | dict | None
    appliesTo: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    age: Range | dict | None
    text: Optional[String] = None


class devicemetricobservationComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueCodeableConcept': 'CodeableConcept',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueSampledData': 'SampledData',
        'valuePeriod': 'Period',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
    }
    _choice_fields = {
        'value': [
            'valueQuantity',
            'valueCodeableConcept',
            'valueString',
            'valueBoolean',
            'valueInteger',
            'valueRange',
            'valueRatio',
            'valueSampledData',
            'valueTime',
            'valueDateTime',
            'valuePeriod',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueQuantity: Quantity | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueSampledData: SampledData | dict | None
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Period | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    referenceRange: Any = None


class devicemetricobservation(FHIRResource):
    _resource_type = "devicemetricobservation"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'basedOn',
        'partOf',
        'category',
        'focus',
        'performer',
        'note',
        'hasMember',
        'derivedFrom',
        'component',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'focus': 'Reference',
        'encounter': 'Reference',
        'performer': 'Reference',
        'valueQuantity': 'Quantity',
        'valueCodeableConcept': 'CodeableConcept',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueSampledData': 'SampledData',
        'valuePeriod': 'Period',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
        'note': 'Annotation',
        'bodySite': 'CodeableConcept',
        'method': 'CodeableConcept',
        'specimen': 'Reference',
        'device': 'Reference',
        'referenceRange': 'devicemetricobservationReferenceRange',
        'hasMember': 'Reference',
        'derivedFrom': 'Reference',
        'component': 'devicemetricobservationComponent',
    }
    _choice_fields = {
        'effective': ['effectiveDateTime'],
        'value': [
            'valueQuantity',
            'valueCodeableConcept',
            'valueString',
            'valueRange',
            'valueRatio',
            'valueSampledData',
            'valueTime',
            'valueDateTime',
            'valuePeriod',
        ],
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    focus: Reference | FHIRList[Reference] | list | dict
    encounter: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference] | list | dict
    valueQuantity: Quantity | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueSampledData: SampledData | dict | None
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Period | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | dict | None
    note: Annotation | FHIRList[Annotation] | list | dict
    bodySite: CodeableConcept | dict | None
    method: CodeableConcept | dict | None
    specimen: Reference | dict | None
    device: Reference | dict | None
    referenceRange: devicemetricobservationReferenceRange | dict | None
    hasMember: Reference | FHIRList[Reference] | list | dict
    derivedFrom: Reference | FHIRList[Reference] | list | dict
    component: devicemetricobservationComponent | FHIRList[devicemetricobservationComponent] | list | dict


class groupdefinitionCharacteristic(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueCodeableConcept': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueRange': 'Range',
        'valueReference': 'Reference',
        'period': 'Period',
    }
    _choice_fields = {'value': ['valueCodeableConcept', 'valueBoolean', 'valueQuantity', 'valueRange', 'valueReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueBoolean: Optional[Boolean] = None
    valueQuantity: Quantity | dict | None
    valueRange: Range | dict | None
    valueReference: Reference | dict | None
    exclude: Optional[Boolean] = None
    period: Period | dict | None


class groupdefinitionMember(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'entity': 'Reference', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    entity: Reference | dict | None
    period: Period | dict | None
    inactive: Optional[Boolean] = None


class groupdefinition(FHIRResource):
    _resource_type = "groupdefinition"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'characteristic'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'code': 'CodeableConcept',
        'managingEntity': 'Reference',
        'characteristic': 'groupdefinitionCharacteristic',
        'member': 'groupdefinitionMember',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    active: Optional[Boolean] = None
    type_: Optional[Code] = None
    actual: Optional[Boolean] = None
    code: CodeableConcept | dict | None
    name: Optional[String] = None
    quantity: Optional[UnsignedInt] = None
    managingEntity: Reference | dict | None
    characteristic: groupdefinitionCharacteristic | FHIRList[groupdefinitionCharacteristic] | list | dict
    member: groupdefinitionMember | dict | None


class hdlcholesterolReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'low': 'Quantity',
        'high': 'Quantity',
        'type_': 'CodeableConcept',
        'appliesTo': 'CodeableConcept',
        'age': 'Range',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    low: Quantity | dict | None
    high: Quantity | dict | None
    type_: CodeableConcept | dict | None
    appliesTo: CodeableConcept | dict | None
    age: Range | dict | None
    text: Optional[String] = None


class hdlcholesterolComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueCodeableConcept': 'CodeableConcept',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueSampledData': 'SampledData',
        'valuePeriod': 'Period',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
    }
    _choice_fields = {
        'value': [
            'valueQuantity',
            'valueCodeableConcept',
            'valueString',
            'valueBoolean',
            'valueInteger',
            'valueRange',
            'valueRatio',
            'valueSampledData',
            'valueTime',
            'valueDateTime',
            'valuePeriod',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueQuantity: Quantity | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueSampledData: SampledData | dict | None
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Period | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    referenceRange: Any = None


class hdlcholesterol(FHIRResource):
    _resource_type = "hdlcholesterol"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'note', 'component'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'focus': 'Reference',
        'encounter': 'Reference',
        'effectivePeriod': 'Period',
        'effectiveTiming': 'Timing',
        'performer': 'Reference',
        'valueQuantity': 'Quantity',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
        'note': 'Annotation',
        'bodySite': 'CodeableConcept',
        'method': 'CodeableConcept',
        'specimen': 'Reference',
        'device': 'Reference',
        'referenceRange': 'hdlcholesterolReferenceRange',
        'hasMember': 'Reference',
        'derivedFrom': 'Reference',
        'component': 'hdlcholesterolComponent',
    }
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod', 'effectiveTiming', 'effectiveInstant'], 'value': ['valueQuantity']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    focus: Reference | FHIRList[Reference] | list | dict
    encounter: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    effectiveTiming: Timing | dict | None
    effectiveInstant: Optional[Instant] = None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference] | list | dict
    valueQuantity: Quantity | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | dict | None
    note: Annotation | FHIRList[Annotation] | list | dict
    bodySite: CodeableConcept | dict | None
    method: CodeableConcept | dict | None
    specimen: Reference | dict | None
    device: Reference | dict | None
    referenceRange: hdlcholesterolReferenceRange | dict | None
    hasMember: Reference | dict | None
    derivedFrom: Reference | dict | None
    component: hdlcholesterolComponent | FHIRList[hdlcholesterolComponent] | list | dict


class headcircumCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | FHIRList[Coding] | list | dict
    text: Optional[String] = None


class headcircumCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class headcircumCode(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | dict | None
    text: Optional[String] = None


class headcircumCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class headcircumValue(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class headcircumReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'low': 'Quantity',
        'high': 'Quantity',
        'type_': 'CodeableConcept',
        'appliesTo': 'CodeableConcept',
        'age': 'Range',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    low: Quantity | dict | None
    high: Quantity | dict | None
    type_: CodeableConcept | dict | None
    appliesTo: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    age: Range | dict | None
    text: Optional[String] = None


class headcircumComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueCodeableConcept': 'CodeableConcept',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueSampledData': 'SampledData',
        'valuePeriod': 'Period',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
    }
    _choice_fields = {
        'value': [
            'valueQuantity',
            'valueCodeableConcept',
            'valueString',
            'valueBoolean',
            'valueInteger',
            'valueRange',
            'valueRatio',
            'valueSampledData',
            'valueTime',
            'valueDateTime',
            'valuePeriod',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueQuantity: Quantity | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueSampledData: SampledData | dict | None
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Period | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    referenceRange: Any = None


class headcircum(FHIRResource):
    _resource_type = "headcircum"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'basedOn',
        'partOf',
        'focus',
        'performer',
        'interpretation',
        'note',
        'referenceRange',
        'hasMember',
        'derivedFrom',
        'component',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'focus': 'Reference',
        'encounter': 'Reference',
        'effectivePeriod': 'Period',
        'performer': 'Reference',
        'valueQuantity': 'Quantity',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
        'note': 'Annotation',
        'bodySite': 'CodeableConcept',
        'method': 'CodeableConcept',
        'specimen': 'Reference',
        'device': 'Reference',
        'referenceRange': 'headcircumReferenceRange',
        'hasMember': 'Reference',
        'derivedFrom': 'Reference',
        'component': 'headcircumComponent',
    }
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'value': ['valueQuantity']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | dict | None
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    focus: Reference | FHIRList[Reference] | list | dict
    encounter: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference] | list | dict
    valueQuantity: Quantity | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    bodySite: CodeableConcept | dict | None
    method: CodeableConcept | dict | None
    specimen: Reference | dict | None
    device: Reference | dict | None
    referenceRange: headcircumReferenceRange | FHIRList[headcircumReferenceRange] | list | dict
    hasMember: Reference | FHIRList[Reference] | list | dict
    derivedFrom: Reference | FHIRList[Reference] | list | dict
    component: headcircumComponent | FHIRList[headcircumComponent] | list | dict


class heartrateCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | FHIRList[Coding] | list | dict
    text: Optional[String] = None


class heartrateCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class heartrateCode(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | dict | None
    text: Optional[String] = None


class heartrateCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class heartrateValue(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class heartrateReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'low': 'Quantity',
        'high': 'Quantity',
        'type_': 'CodeableConcept',
        'appliesTo': 'CodeableConcept',
        'age': 'Range',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    low: Quantity | dict | None
    high: Quantity | dict | None
    type_: CodeableConcept | dict | None
    appliesTo: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    age: Range | dict | None
    text: Optional[String] = None


class heartrateComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueCodeableConcept': 'CodeableConcept',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueSampledData': 'SampledData',
        'valuePeriod': 'Period',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
    }
    _choice_fields = {
        'value': [
            'valueQuantity',
            'valueCodeableConcept',
            'valueString',
            'valueBoolean',
            'valueInteger',
            'valueRange',
            'valueRatio',
            'valueSampledData',
            'valueTime',
            'valueDateTime',
            'valuePeriod',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueQuantity: Quantity | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueSampledData: SampledData | dict | None
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Period | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    referenceRange: Any = None


class heartrate(FHIRResource):
    _resource_type = "heartrate"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'basedOn',
        'partOf',
        'focus',
        'performer',
        'interpretation',
        'note',
        'referenceRange',
        'hasMember',
        'derivedFrom',
        'component',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'focus': 'Reference',
        'encounter': 'Reference',
        'effectivePeriod': 'Period',
        'performer': 'Reference',
        'valueQuantity': 'Quantity',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
        'note': 'Annotation',
        'bodySite': 'CodeableConcept',
        'method': 'CodeableConcept',
        'specimen': 'Reference',
        'device': 'Reference',
        'referenceRange': 'heartrateReferenceRange',
        'hasMember': 'Reference',
        'derivedFrom': 'Reference',
        'component': 'heartrateComponent',
    }
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'value': ['valueQuantity']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | dict | None
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    focus: Reference | FHIRList[Reference] | list | dict
    encounter: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference] | list | dict
    valueQuantity: Quantity | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    bodySite: CodeableConcept | dict | None
    method: CodeableConcept | dict | None
    specimen: Reference | dict | None
    device: Reference | dict | None
    referenceRange: heartrateReferenceRange | FHIRList[heartrateReferenceRange] | list | dict
    hasMember: Reference | FHIRList[Reference] | list | dict
    derivedFrom: Reference | FHIRList[Reference] | list | dict
    component: heartrateComponent | FHIRList[heartrateComponent] | list | dict


class hlaresultMedia(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'link': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    comment: Optional[String] = None
    link: Reference | dict | None


class hlaresult(FHIRResource):
    _resource_type = "hlaresult"
    _list_fields = {
        'contained',
        'modifierExtension',
        'identifier',
        'basedOn',
        'category',
        'performer',
        'resultsInterpreter',
        'specimen',
        'result',
        'imagingStudy',
        'media',
        'conclusionCode',
        'presentedForm',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'encounter': 'Reference',
        'effectivePeriod': 'Period',
        'performer': 'Reference',
        'resultsInterpreter': 'Reference',
        'specimen': 'Reference',
        'result': 'Reference',
        'imagingStudy': 'Reference',
        'media': 'hlaresultMedia',
        'conclusionCode': 'CodeableConcept',
        'presentedForm': 'Attachment',
    }
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | dict | None
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    encounter: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference] | list | dict
    resultsInterpreter: Reference | FHIRList[Reference] | list | dict
    specimen: Reference | FHIRList[Reference] | list | dict
    result: Reference | FHIRList[Reference] | list | dict
    imagingStudy: Reference | FHIRList[Reference] | list | dict
    media: hlaresultMedia | FHIRList[hlaresultMedia] | list | dict
    conclusion: Optional[String] = None
    conclusionCode: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    presentedForm: Attachment | FHIRList[Attachment] | list | dict


class ldlcholesterolReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'low': 'Quantity',
        'high': 'Quantity',
        'type_': 'CodeableConcept',
        'appliesTo': 'CodeableConcept',
        'age': 'Range',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    low: Quantity | dict | None
    high: Quantity | dict | None
    type_: CodeableConcept | dict | None
    appliesTo: CodeableConcept | dict | None
    age: Range | dict | None
    text: Optional[String] = None


class ldlcholesterolComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueCodeableConcept': 'CodeableConcept',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueSampledData': 'SampledData',
        'valuePeriod': 'Period',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
    }
    _choice_fields = {
        'value': [
            'valueQuantity',
            'valueCodeableConcept',
            'valueString',
            'valueBoolean',
            'valueInteger',
            'valueRange',
            'valueRatio',
            'valueSampledData',
            'valueTime',
            'valueDateTime',
            'valuePeriod',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueQuantity: Quantity | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueSampledData: SampledData | dict | None
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Period | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    referenceRange: Any = None


class ldlcholesterol(FHIRResource):
    _resource_type = "ldlcholesterol"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'note', 'component'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'focus': 'Reference',
        'encounter': 'Reference',
        'effectivePeriod': 'Period',
        'effectiveTiming': 'Timing',
        'performer': 'Reference',
        'valueQuantity': 'Quantity',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
        'note': 'Annotation',
        'bodySite': 'CodeableConcept',
        'method': 'CodeableConcept',
        'specimen': 'Reference',
        'device': 'Reference',
        'referenceRange': 'ldlcholesterolReferenceRange',
        'hasMember': 'Reference',
        'derivedFrom': 'Reference',
        'component': 'ldlcholesterolComponent',
    }
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod', 'effectiveTiming', 'effectiveInstant'], 'value': ['valueQuantity']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    focus: Reference | FHIRList[Reference] | list | dict
    encounter: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    effectiveTiming: Timing | dict | None
    effectiveInstant: Optional[Instant] = None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference] | list | dict
    valueQuantity: Quantity | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | dict | None
    note: Annotation | FHIRList[Annotation] | list | dict
    bodySite: CodeableConcept | dict | None
    method: CodeableConcept | dict | None
    specimen: Reference | dict | None
    device: Reference | dict | None
    referenceRange: ldlcholesterolReferenceRange | dict | None
    hasMember: Reference | dict | None
    derivedFrom: Reference | dict | None
    component: ldlcholesterolComponent | FHIRList[ldlcholesterolComponent] | list | dict


class lipidprofileMedia(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'link': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    comment: Optional[String] = None
    link: Reference | dict | None


class lipidprofile(FHIRResource):
    _resource_type = "lipidprofile"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'basedOn',
        'category',
        'performer',
        'resultsInterpreter',
        'specimen',
        'imagingStudy',
        'media',
        'presentedForm',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'encounter': 'Reference',
        'effectivePeriod': 'Period',
        'performer': 'Reference',
        'resultsInterpreter': 'Reference',
        'specimen': 'Reference',
        'result': 'Reference',
        'imagingStudy': 'Reference',
        'media': 'lipidprofileMedia',
        'conclusionCode': 'CodeableConcept',
        'presentedForm': 'Attachment',
    }
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    encounter: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference] | list | dict
    resultsInterpreter: Reference | FHIRList[Reference] | list | dict
    specimen: Reference | FHIRList[Reference] | list | dict
    result: Reference | dict | None
    imagingStudy: Reference | FHIRList[Reference] | list | dict
    media: lipidprofileMedia | FHIRList[lipidprofileMedia] | list | dict
    conclusion: Optional[String] = None
    conclusionCode: CodeableConcept | dict | None
    presentedForm: Attachment | FHIRList[Attachment] | list | dict


class oxygensatCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | FHIRList[Coding] | list | dict
    text: Optional[String] = None


class oxygensatCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class oxygensatCode(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | dict | None
    text: Optional[String] = None


class oxygensatCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class oxygensatValue(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class oxygensatReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'low': 'Quantity',
        'high': 'Quantity',
        'type_': 'CodeableConcept',
        'appliesTo': 'CodeableConcept',
        'age': 'Range',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    low: Quantity | dict | None
    high: Quantity | dict | None
    type_: CodeableConcept | dict | None
    appliesTo: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    age: Range | dict | None
    text: Optional[String] = None


class oxygensatComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueCodeableConcept': 'CodeableConcept',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueSampledData': 'SampledData',
        'valuePeriod': 'Period',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
    }
    _choice_fields = {
        'value': [
            'valueQuantity',
            'valueCodeableConcept',
            'valueString',
            'valueBoolean',
            'valueInteger',
            'valueRange',
            'valueRatio',
            'valueSampledData',
            'valueTime',
            'valueDateTime',
            'valuePeriod',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueQuantity: Quantity | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueSampledData: SampledData | dict | None
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Period | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    referenceRange: Any = None


class oxygensat(FHIRResource):
    _resource_type = "oxygensat"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'basedOn',
        'partOf',
        'focus',
        'performer',
        'interpretation',
        'note',
        'referenceRange',
        'hasMember',
        'derivedFrom',
        'component',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'focus': 'Reference',
        'encounter': 'Reference',
        'effectivePeriod': 'Period',
        'performer': 'Reference',
        'valueQuantity': 'Quantity',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
        'note': 'Annotation',
        'bodySite': 'CodeableConcept',
        'method': 'CodeableConcept',
        'specimen': 'Reference',
        'device': 'Reference',
        'referenceRange': 'oxygensatReferenceRange',
        'hasMember': 'Reference',
        'derivedFrom': 'Reference',
        'component': 'oxygensatComponent',
    }
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'value': ['valueQuantity']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | dict | None
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    focus: Reference | FHIRList[Reference] | list | dict
    encounter: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference] | list | dict
    valueQuantity: Quantity | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    bodySite: CodeableConcept | dict | None
    method: CodeableConcept | dict | None
    specimen: Reference | dict | None
    device: Reference | dict | None
    referenceRange: oxygensatReferenceRange | FHIRList[oxygensatReferenceRange] | list | dict
    hasMember: Reference | FHIRList[Reference] | list | dict
    derivedFrom: Reference | FHIRList[Reference] | list | dict
    component: oxygensatComponent | FHIRList[oxygensatComponent] | list | dict


class picoelementCharacteristic(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'usageContext'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'definitionReference': 'Reference',
        'definitionCodeableConcept': 'CodeableConcept',
        'definitionExpression': 'Expression',
        'definitionDataRequirement': 'DataRequirement',
        'definitionTriggerDefinition': 'TriggerDefinition',
        'usageContext': 'UsageContext',
        'participantEffectivePeriod': 'Period',
        'participantEffectiveDuration': 'Duration',
        'participantEffectiveTiming': 'Timing',
        'timeFromStart': 'Duration',
    }
    _choice_fields = {
        'definition': [
            'definitionReference',
            'definitionCanonical',
            'definitionCodeableConcept',
            'definitionExpression',
            'definitionDataRequirement',
            'definitionTriggerDefinition',
        ],
        'participantEffective': ['participantEffectiveDateTime', 'participantEffectivePeriod', 'participantEffectiveDuration', 'participantEffectiveTiming'],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    description: Optional[String] = None
    definitionReference: Reference | dict | None
    definitionCanonical: Optional[Canonical] = None
    definitionCodeableConcept: CodeableConcept | dict | None
    definitionExpression: Expression | dict | None
    definitionDataRequirement: DataRequirement | dict | None
    definitionTriggerDefinition: TriggerDefinition | dict | None
    usageContext: UsageContext | FHIRList[UsageContext] | list | dict
    exclude: Optional[Boolean] = None
    participantEffectiveDateTime: Optional[DateTime] = None
    participantEffectivePeriod: Period | dict | None
    participantEffectiveDuration: Duration | dict | None
    participantEffectiveTiming: Timing | dict | None
    timeFromStart: Duration | dict | None
    groupMeasure: Optional[Code] = None


class picoelement(FHIRResource):
    _resource_type = "picoelement"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'contact',
        'note',
        'useContext',
        'jurisdiction',
        'topic',
        'author',
        'editor',
        'reviewer',
        'endorser',
        'relatedArtifact',
        'characteristic',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'contact': 'ContactDetail',
        'note': 'Annotation',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'topic': 'CodeableConcept',
        'author': 'ContactDetail',
        'editor': 'ContactDetail',
        'reviewer': 'ContactDetail',
        'endorser': 'ContactDetail',
        'relatedArtifact': 'RelatedArtifact',
        'characteristic': 'picoelementCharacteristic',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    shortTitle: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    note: Annotation | FHIRList[Annotation] | list | dict
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    topic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    author: ContactDetail | FHIRList[ContactDetail] | list | dict
    editor: ContactDetail | FHIRList[ContactDetail] | list | dict
    reviewer: ContactDetail | FHIRList[ContactDetail] | list | dict
    endorser: ContactDetail | FHIRList[ContactDetail] | list | dict
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    type_: Optional[Code] = None
    characteristic: picoelementCharacteristic | FHIRList[picoelementCharacteristic] | list | dict


class resprateCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | FHIRList[Coding] | list | dict
    text: Optional[String] = None


class resprateCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class resprateCode(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | dict | None
    text: Optional[String] = None


class resprateCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class resprateValue(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class resprateReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'low': 'Quantity',
        'high': 'Quantity',
        'type_': 'CodeableConcept',
        'appliesTo': 'CodeableConcept',
        'age': 'Range',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    low: Quantity | dict | None
    high: Quantity | dict | None
    type_: CodeableConcept | dict | None
    appliesTo: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    age: Range | dict | None
    text: Optional[String] = None


class resprateComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueCodeableConcept': 'CodeableConcept',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueSampledData': 'SampledData',
        'valuePeriod': 'Period',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
    }
    _choice_fields = {
        'value': [
            'valueQuantity',
            'valueCodeableConcept',
            'valueString',
            'valueBoolean',
            'valueInteger',
            'valueRange',
            'valueRatio',
            'valueSampledData',
            'valueTime',
            'valueDateTime',
            'valuePeriod',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueQuantity: Quantity | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueSampledData: SampledData | dict | None
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Period | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    referenceRange: Any = None


class resprate(FHIRResource):
    _resource_type = "resprate"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'basedOn',
        'partOf',
        'focus',
        'performer',
        'interpretation',
        'note',
        'referenceRange',
        'hasMember',
        'derivedFrom',
        'component',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'focus': 'Reference',
        'encounter': 'Reference',
        'effectivePeriod': 'Period',
        'performer': 'Reference',
        'valueQuantity': 'Quantity',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
        'note': 'Annotation',
        'bodySite': 'CodeableConcept',
        'method': 'CodeableConcept',
        'specimen': 'Reference',
        'device': 'Reference',
        'referenceRange': 'resprateReferenceRange',
        'hasMember': 'Reference',
        'derivedFrom': 'Reference',
        'component': 'resprateComponent',
    }
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod'], 'value': ['valueQuantity']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | dict | None
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    focus: Reference | FHIRList[Reference] | list | dict
    encounter: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference] | list | dict
    valueQuantity: Quantity | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    bodySite: CodeableConcept | dict | None
    method: CodeableConcept | dict | None
    specimen: Reference | dict | None
    device: Reference | dict | None
    referenceRange: resprateReferenceRange | FHIRList[resprateReferenceRange] | list | dict
    hasMember: Reference | FHIRList[Reference] | list | dict
    derivedFrom: Reference | FHIRList[Reference] | list | dict
    component: resprateComponent | FHIRList[resprateComponent] | list | dict


class shareableactivitydefinitionParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'role': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    role: CodeableConcept | dict | None


class shareableactivitydefinitionDynamicValue(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    path: Optional[String] = None
    expression: Expression | dict | None


class shareableactivitydefinition(FHIRResource):
    _resource_type = "shareableactivitydefinition"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'contact',
        'useContext',
        'jurisdiction',
        'topic',
        'author',
        'editor',
        'reviewer',
        'endorser',
        'relatedArtifact',
        'library',
        'participant',
        'dosage',
        'bodySite',
        'specimenRequirement',
        'observationRequirement',
        'observationResultRequirement',
        'dynamicValue',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'subjectCodeableConcept': 'CodeableConcept',
        'subjectReference': 'Reference',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'topic': 'CodeableConcept',
        'author': 'ContactDetail',
        'editor': 'ContactDetail',
        'reviewer': 'ContactDetail',
        'endorser': 'ContactDetail',
        'relatedArtifact': 'RelatedArtifact',
        'code': 'CodeableConcept',
        'timingTiming': 'Timing',
        'timingAge': 'Age',
        'timingPeriod': 'Period',
        'timingRange': 'Range',
        'timingDuration': 'Duration',
        'location': 'Reference',
        'participant': 'shareableactivitydefinitionParticipant',
        'productReference': 'Reference',
        'productCodeableConcept': 'CodeableConcept',
        'quantity': 'Quantity',
        'dosage': 'Dosage',
        'bodySite': 'CodeableConcept',
        'specimenRequirement': 'Reference',
        'observationRequirement': 'Reference',
        'observationResultRequirement': 'Reference',
        'dynamicValue': 'shareableactivitydefinitionDynamicValue',
    }
    _choice_fields = {
        'product': ['productReference', 'productCodeableConcept'],
        'subject': ['subjectCodeableConcept', 'subjectReference'],
        'timing': ['timingTiming', 'timingDateTime', 'timingAge', 'timingPeriod', 'timingRange', 'timingDuration'],
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    subjectCodeableConcept: CodeableConcept | dict | None
    subjectReference: Reference | dict | None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    topic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    author: ContactDetail | FHIRList[ContactDetail] | list | dict
    editor: ContactDetail | FHIRList[ContactDetail] | list | dict
    reviewer: ContactDetail | FHIRList[ContactDetail] | list | dict
    endorser: ContactDetail | FHIRList[ContactDetail] | list | dict
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    library: Canonical | FHIRList[Canonical] | list | None = None
    kind: Optional[Code] = None
    profile: Optional[Canonical] = None
    code: CodeableConcept | dict | None
    intent: Optional[Code] = None
    priority: Optional[Code] = None
    doNotPerform: Optional[Boolean] = None
    timingTiming: Timing | dict | None
    timingDateTime: Optional[DateTime] = None
    timingAge: Age | dict | None
    timingPeriod: Period | dict | None
    timingRange: Range | dict | None
    timingDuration: Duration | dict | None
    location: Reference | dict | None
    participant: shareableactivitydefinitionParticipant | FHIRList[shareableactivitydefinitionParticipant] | list | dict
    productReference: Reference | dict | None
    productCodeableConcept: CodeableConcept | dict | None
    quantity: Quantity | dict | None
    dosage: Dosage | FHIRList[Dosage] | list | dict
    bodySite: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    specimenRequirement: Reference | FHIRList[Reference] | list | dict
    observationRequirement: Reference | FHIRList[Reference] | list | dict
    observationResultRequirement: Reference | FHIRList[Reference] | list | dict
    transform: Optional[Canonical] = None
    dynamicValue: shareableactivitydefinitionDynamicValue | FHIRList[shareableactivitydefinitionDynamicValue] | list | dict


class shareablecodesystemFilter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'operator'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    description: Optional[String] = None
    operator: Code | FHIRList[Code] | list | None = None
    value: Optional[String] = None


class shareablecodesystemProperty(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    uri: Optional[Uri] = None
    description: Optional[String] = None
    type_: Optional[Code] = None


class shareablecodesystemConcept(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'designation', 'property', 'concept'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'designation': 'shareablecodesystemConceptDesignation',
        'property': 'shareablecodesystemConceptProperty',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    display: Optional[String] = None
    definition: Optional[String] = None
    designation: shareablecodesystemConceptDesignation | FHIRList[shareablecodesystemConceptDesignation] | list | dict
    property: shareablecodesystemConceptProperty | FHIRList[shareablecodesystemConceptProperty] | list | dict
    concept: Any = None


class shareablecodesystemConceptDesignation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'use': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    language: Optional[Code] = None
    use: Coding | dict | None
    value: Optional[String] = None


class shareablecodesystemConceptProperty(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'valueCoding': 'Coding'}
    _choice_fields = {'value': ['valueCode', 'valueCoding', 'valueString', 'valueInteger', 'valueBoolean', 'valueDateTime', 'valueDecimal']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    valueCode: Optional[Code] = None
    valueCoding: Coding | dict | None
    valueString: Optional[String] = None
    valueInteger: Optional[Integer] = None
    valueBoolean: Optional[Boolean] = None
    valueDateTime: Optional[DateTime] = None
    valueDecimal: Optional[Decimal] = None


class shareablecodesystem(FHIRResource):
    _resource_type = "shareablecodesystem"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'contact', 'useContext', 'jurisdiction', 'filter', 'property', 'concept'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'filter': 'shareablecodesystemFilter',
        'property': 'shareablecodesystemProperty',
        'concept': 'shareablecodesystemConcept',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
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
    filter: shareablecodesystemFilter | FHIRList[shareablecodesystemFilter] | list | dict
    property: shareablecodesystemProperty | FHIRList[shareablecodesystemProperty] | list | dict
    concept: shareablecodesystemConcept | FHIRList[shareablecodesystemConcept] | list | dict


class shareablelibrary(FHIRResource):
    _resource_type = "shareablelibrary"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'contact',
        'useContext',
        'jurisdiction',
        'topic',
        'author',
        'editor',
        'reviewer',
        'endorser',
        'relatedArtifact',
        'parameter',
        'dataRequirement',
        'content',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'subjectCodeableConcept': 'CodeableConcept',
        'subjectReference': 'Reference',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'topic': 'CodeableConcept',
        'author': 'ContactDetail',
        'editor': 'ContactDetail',
        'reviewer': 'ContactDetail',
        'endorser': 'ContactDetail',
        'relatedArtifact': 'RelatedArtifact',
        'parameter': 'ParameterDefinition',
        'dataRequirement': 'DataRequirement',
        'content': 'Attachment',
    }
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    type_: CodeableConcept | dict | None
    subjectCodeableConcept: CodeableConcept | dict | None
    subjectReference: Reference | dict | None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    topic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    author: ContactDetail | FHIRList[ContactDetail] | list | dict
    editor: ContactDetail | FHIRList[ContactDetail] | list | dict
    reviewer: ContactDetail | FHIRList[ContactDetail] | list | dict
    endorser: ContactDetail | FHIRList[ContactDetail] | list | dict
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    parameter: ParameterDefinition | FHIRList[ParameterDefinition] | list | dict
    dataRequirement: DataRequirement | FHIRList[DataRequirement] | list | dict
    content: Attachment | FHIRList[Attachment] | list | dict


class shareablemeasureGroup(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'population', 'stratifier'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'population': 'shareablemeasureGroupPopulation',
        'stratifier': 'shareablemeasureGroupStratifier',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    description: Optional[String] = None
    population: shareablemeasureGroupPopulation | FHIRList[shareablemeasureGroupPopulation] | list | dict
    stratifier: shareablemeasureGroupStratifier | FHIRList[shareablemeasureGroupStratifier] | list | dict


class shareablemeasureGroupPopulation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'criteria': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    description: Optional[String] = None
    criteria: Expression | dict | None


class shareablemeasureGroupStratifier(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'component'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'criteria': 'Expression',
        'component': 'shareablemeasureGroupStratifierComponent',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    description: Optional[String] = None
    criteria: Expression | dict | None
    component: shareablemeasureGroupStratifierComponent | FHIRList[shareablemeasureGroupStratifierComponent] | list | dict


class shareablemeasureGroupStratifierComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'criteria': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    description: Optional[String] = None
    criteria: Expression | dict | None


class shareablemeasureSupplementalData(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'usage'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'CodeableConcept', 'usage': 'CodeableConcept', 'criteria': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    usage: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    description: Optional[String] = None
    criteria: Expression | dict | None


class shareablemeasure(FHIRResource):
    _resource_type = "shareablemeasure"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'contact',
        'useContext',
        'jurisdiction',
        'topic',
        'author',
        'editor',
        'reviewer',
        'endorser',
        'relatedArtifact',
        'library',
        'type_',
        'definition',
        'group',
        'supplementalData',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'subjectCodeableConcept': 'CodeableConcept',
        'subjectReference': 'Reference',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'topic': 'CodeableConcept',
        'author': 'ContactDetail',
        'editor': 'ContactDetail',
        'reviewer': 'ContactDetail',
        'endorser': 'ContactDetail',
        'relatedArtifact': 'RelatedArtifact',
        'scoring': 'CodeableConcept',
        'compositeScoring': 'CodeableConcept',
        'type_': 'CodeableConcept',
        'improvementNotation': 'CodeableConcept',
        'group': 'shareablemeasureGroup',
        'supplementalData': 'shareablemeasureSupplementalData',
    }
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    subjectCodeableConcept: CodeableConcept | dict | None
    subjectReference: Reference | dict | None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    topic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    author: ContactDetail | FHIRList[ContactDetail] | list | dict
    editor: ContactDetail | FHIRList[ContactDetail] | list | dict
    reviewer: ContactDetail | FHIRList[ContactDetail] | list | dict
    endorser: ContactDetail | FHIRList[ContactDetail] | list | dict
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    library: Canonical | FHIRList[Canonical] | list | None = None
    disclaimer: Optional[Markdown] = None
    scoring: CodeableConcept | dict | None
    compositeScoring: CodeableConcept | dict | None
    type_: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    riskAdjustment: Optional[String] = None
    rateAggregation: Optional[String] = None
    rationale: Optional[Markdown] = None
    clinicalRecommendationStatement: Optional[Markdown] = None
    improvementNotation: CodeableConcept | dict | None
    definition: Markdown | FHIRList[Markdown] | list | None = None
    guidance: Optional[Markdown] = None
    group: shareablemeasureGroup | FHIRList[shareablemeasureGroup] | list | dict
    supplementalData: shareablemeasureSupplementalData | FHIRList[shareablemeasureSupplementalData] | list | dict


class shareableplandefinitionGoal(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'addresses', 'documentation', 'target'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'category': 'CodeableConcept',
        'description': 'CodeableConcept',
        'priority': 'CodeableConcept',
        'start': 'CodeableConcept',
        'addresses': 'CodeableConcept',
        'documentation': 'RelatedArtifact',
        'target': 'shareableplandefinitionGoalTarget',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    category: CodeableConcept | dict | None
    description: CodeableConcept | dict | None
    priority: CodeableConcept | dict | None
    start: CodeableConcept | dict | None
    addresses: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    documentation: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    target: shareableplandefinitionGoalTarget | FHIRList[shareableplandefinitionGoalTarget] | list | dict


class shareableplandefinitionGoalTarget(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'measure': 'CodeableConcept',
        'detailQuantity': 'Quantity',
        'detailRange': 'Range',
        'detailCodeableConcept': 'CodeableConcept',
        'due': 'Duration',
    }
    _choice_fields = {'detail': ['detailQuantity', 'detailRange', 'detailCodeableConcept']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    measure: CodeableConcept | dict | None
    detailQuantity: Quantity | dict | None
    detailRange: Range | dict | None
    detailCodeableConcept: CodeableConcept | dict | None
    due: Duration | dict | None


class shareableplandefinitionAction(FHIRElement):
    _list_fields = {
        'extension',
        'modifierExtension',
        'code',
        'reason',
        'documentation',
        'goalId',
        'trigger',
        'condition',
        'input',
        'output',
        'relatedAction',
        'participant',
        'dynamicValue',
        'action',
    }
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'reason': 'CodeableConcept',
        'documentation': 'RelatedArtifact',
        'subjectCodeableConcept': 'CodeableConcept',
        'subjectReference': 'Reference',
        'trigger': 'TriggerDefinition',
        'condition': 'shareableplandefinitionActionCondition',
        'input': 'DataRequirement',
        'output': 'DataRequirement',
        'relatedAction': 'shareableplandefinitionActionRelatedAction',
        'timingAge': 'Age',
        'timingPeriod': 'Period',
        'timingDuration': 'Duration',
        'timingRange': 'Range',
        'timingTiming': 'Timing',
        'participant': 'shareableplandefinitionActionParticipant',
        'type_': 'CodeableConcept',
        'dynamicValue': 'shareableplandefinitionActionDynamicValue',
    }
    _choice_fields = {
        'definition': ['definitionCanonical', 'definitionUri'],
        'subject': ['subjectCodeableConcept', 'subjectReference'],
        'timing': ['timingDateTime', 'timingAge', 'timingPeriod', 'timingDuration', 'timingRange', 'timingTiming'],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    prefix: Optional[String] = None
    title: Optional[String] = None
    description: Optional[String] = None
    textEquivalent: Optional[String] = None
    priority: Optional[Code] = None
    code: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    reason: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    documentation: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    goalId: Id | FHIRList[Id] | list | None = None
    subjectCodeableConcept: CodeableConcept | dict | None
    subjectReference: Reference | dict | None
    trigger: TriggerDefinition | FHIRList[TriggerDefinition] | list | dict
    condition: shareableplandefinitionActionCondition | FHIRList[shareableplandefinitionActionCondition] | list | dict
    input: DataRequirement | FHIRList[DataRequirement] | list | dict
    output: DataRequirement | FHIRList[DataRequirement] | list | dict
    relatedAction: shareableplandefinitionActionRelatedAction | FHIRList[shareableplandefinitionActionRelatedAction] | list | dict
    timingDateTime: Optional[DateTime] = None
    timingAge: Age | dict | None
    timingPeriod: Period | dict | None
    timingDuration: Duration | dict | None
    timingRange: Range | dict | None
    timingTiming: Timing | dict | None
    participant: shareableplandefinitionActionParticipant | FHIRList[shareableplandefinitionActionParticipant] | list | dict
    type_: CodeableConcept | dict | None
    groupingBehavior: Optional[Code] = None
    selectionBehavior: Optional[Code] = None
    requiredBehavior: Optional[Code] = None
    precheckBehavior: Optional[Code] = None
    cardinalityBehavior: Optional[Code] = None
    definitionCanonical: Optional[Canonical] = None
    definitionUri: Optional[Uri] = None
    transform: Optional[Canonical] = None
    dynamicValue: shareableplandefinitionActionDynamicValue | FHIRList[shareableplandefinitionActionDynamicValue] | list | dict
    action: Any = None


class shareableplandefinitionActionCondition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    kind: Optional[Code] = None
    expression: Expression | dict | None


class shareableplandefinitionActionRelatedAction(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'offsetDuration': 'Duration', 'offsetRange': 'Range'}
    _choice_fields = {'offset': ['offsetDuration', 'offsetRange']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    actionId: Optional[Id] = None
    relationship: Optional[Code] = None
    offsetDuration: Duration | dict | None
    offsetRange: Range | dict | None


class shareableplandefinitionActionParticipant(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'role': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    role: CodeableConcept | dict | None


class shareableplandefinitionActionDynamicValue(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'expression': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    path: Optional[String] = None
    expression: Expression | dict | None


class shareableplandefinition(FHIRResource):
    _resource_type = "shareableplandefinition"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'contact',
        'useContext',
        'jurisdiction',
        'topic',
        'author',
        'editor',
        'reviewer',
        'endorser',
        'relatedArtifact',
        'library',
        'goal',
        'action',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'subjectCodeableConcept': 'CodeableConcept',
        'subjectReference': 'Reference',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'topic': 'CodeableConcept',
        'author': 'ContactDetail',
        'editor': 'ContactDetail',
        'reviewer': 'ContactDetail',
        'endorser': 'ContactDetail',
        'relatedArtifact': 'RelatedArtifact',
        'goal': 'shareableplandefinitionGoal',
        'action': 'shareableplandefinitionAction',
    }
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    subtitle: Optional[String] = None
    type_: CodeableConcept | dict | None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    subjectCodeableConcept: CodeableConcept | dict | None
    subjectReference: Reference | dict | None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    purpose: Optional[Markdown] = None
    usage: Optional[String] = None
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    topic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    author: ContactDetail | FHIRList[ContactDetail] | list | dict
    editor: ContactDetail | FHIRList[ContactDetail] | list | dict
    reviewer: ContactDetail | FHIRList[ContactDetail] | list | dict
    endorser: ContactDetail | FHIRList[ContactDetail] | list | dict
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    library: Canonical | FHIRList[Canonical] | list | None = None
    goal: shareableplandefinitionGoal | FHIRList[shareableplandefinitionGoal] | list | dict
    action: shareableplandefinitionAction | FHIRList[shareableplandefinitionAction] | list | dict


class shareablevaluesetCompose(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'include', 'exclude'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'include': 'shareablevaluesetComposeInclude'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    lockedDate: Optional[Date] = None
    inactive: Optional[Boolean] = None
    include: shareablevaluesetComposeInclude | FHIRList[shareablevaluesetComposeInclude] | list | dict
    exclude: Any = None


class shareablevaluesetComposeInclude(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'concept', 'filter', 'valueSet'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'concept': 'shareablevaluesetComposeIncludeConcept',
        'filter': 'shareablevaluesetComposeIncludeFilter',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    concept: shareablevaluesetComposeIncludeConcept | FHIRList[shareablevaluesetComposeIncludeConcept] | list | dict
    filter: shareablevaluesetComposeIncludeFilter | FHIRList[shareablevaluesetComposeIncludeFilter] | list | dict
    valueSet: Canonical | FHIRList[Canonical] | list | None = None


class shareablevaluesetComposeIncludeConcept(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'designation'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'designation': 'shareablevaluesetComposeIncludeConceptDesignation'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: Optional[Code] = None
    display: Optional[String] = None
    designation: shareablevaluesetComposeIncludeConceptDesignation | FHIRList[shareablevaluesetComposeIncludeConceptDesignation] | list | dict


class shareablevaluesetComposeIncludeConceptDesignation(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'use': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    language: Optional[Code] = None
    use: Coding | dict | None
    value: Optional[String] = None


class shareablevaluesetComposeIncludeFilter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    property: Optional[Code] = None
    op: Optional[Code] = None
    value: Optional[String] = None


class shareablevaluesetExpansion(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'parameter', 'contains'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'parameter': 'shareablevaluesetExpansionParameter',
        'contains': 'shareablevaluesetExpansionContains',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Optional[Uri] = None
    timestamp: Optional[DateTime] = None
    total: Optional[Integer] = None
    offset: Optional[Integer] = None
    parameter: shareablevaluesetExpansionParameter | FHIRList[shareablevaluesetExpansionParameter] | list | dict
    contains: shareablevaluesetExpansionContains | FHIRList[shareablevaluesetExpansionContains] | list | dict


class shareablevaluesetExpansionParameter(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}
    _choice_fields = {'value': ['valueString', 'valueBoolean', 'valueInteger', 'valueDecimal', 'valueUri', 'valueCode', 'valueDateTime']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
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
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
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
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'contact': 'ContactDetail',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'compose': 'shareablevaluesetCompose',
        'expansion': 'shareablevaluesetExpansion',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    status: Optional[Code] = None
    experimental: Optional[Boolean] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    immutable: Optional[Boolean] = None
    purpose: Optional[Markdown] = None
    copyright: Optional[Markdown] = None
    compose: shareablevaluesetCompose | dict | None
    expansion: shareablevaluesetExpansion | dict | None


class synthesis(FHIRResource):
    _resource_type = "synthesis"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'contact',
        'note',
        'useContext',
        'jurisdiction',
        'topic',
        'author',
        'editor',
        'reviewer',
        'endorser',
        'relatedArtifact',
        'exposureVariant',
        'outcome',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'contact': 'ContactDetail',
        'note': 'Annotation',
        'useContext': 'UsageContext',
        'jurisdiction': 'CodeableConcept',
        'effectivePeriod': 'Period',
        'topic': 'CodeableConcept',
        'author': 'ContactDetail',
        'editor': 'ContactDetail',
        'reviewer': 'ContactDetail',
        'endorser': 'ContactDetail',
        'relatedArtifact': 'RelatedArtifact',
        'exposureBackground': 'Reference',
        'exposureVariant': 'Reference',
        'outcome': 'Reference',
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    url: Optional[Uri] = None
    identifier: Identifier | FHIRList[Identifier] | list | dict
    version: Optional[String] = None
    name: Optional[String] = None
    title: Optional[String] = None
    shortTitle: Optional[String] = None
    subtitle: Optional[String] = None
    status: Optional[Code] = None
    date: Optional[DateTime] = None
    publisher: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict
    description: Optional[Markdown] = None
    note: Annotation | FHIRList[Annotation] | list | dict
    useContext: UsageContext | FHIRList[UsageContext] | list | dict
    jurisdiction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    copyright: Optional[Markdown] = None
    approvalDate: Optional[Date] = None
    lastReviewDate: Optional[Date] = None
    effectivePeriod: Period | dict | None
    topic: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    author: ContactDetail | FHIRList[ContactDetail] | list | dict
    editor: ContactDetail | FHIRList[ContactDetail] | list | dict
    reviewer: ContactDetail | FHIRList[ContactDetail] | list | dict
    endorser: ContactDetail | FHIRList[ContactDetail] | list | dict
    relatedArtifact: RelatedArtifact | FHIRList[RelatedArtifact] | list | dict
    exposureBackground: Reference | dict | None
    exposureVariant: Reference | FHIRList[Reference] | list | dict
    outcome: Reference | FHIRList[Reference] | list | dict


class triglycerideReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'low': 'Quantity',
        'high': 'Quantity',
        'type_': 'CodeableConcept',
        'appliesTo': 'CodeableConcept',
        'age': 'Range',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    low: Quantity | dict | None
    high: Quantity | dict | None
    type_: CodeableConcept | dict | None
    appliesTo: CodeableConcept | dict | None
    age: Range | dict | None
    text: Optional[String] = None


class triglycerideComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueCodeableConcept': 'CodeableConcept',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueSampledData': 'SampledData',
        'valuePeriod': 'Period',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
    }
    _choice_fields = {
        'value': [
            'valueQuantity',
            'valueCodeableConcept',
            'valueString',
            'valueBoolean',
            'valueInteger',
            'valueRange',
            'valueRatio',
            'valueSampledData',
            'valueTime',
            'valueDateTime',
            'valuePeriod',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueQuantity: Quantity | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueSampledData: SampledData | dict | None
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Period | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    referenceRange: Any = None


class triglyceride(FHIRResource):
    _resource_type = "triglyceride"
    _list_fields = {'contained', 'extension', 'modifierExtension', 'identifier', 'basedOn', 'partOf', 'category', 'focus', 'performer', 'note', 'component'}
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'focus': 'Reference',
        'encounter': 'Reference',
        'effectivePeriod': 'Period',
        'effectiveTiming': 'Timing',
        'performer': 'Reference',
        'valueQuantity': 'Quantity',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
        'note': 'Annotation',
        'bodySite': 'CodeableConcept',
        'method': 'CodeableConcept',
        'specimen': 'Reference',
        'device': 'Reference',
        'referenceRange': 'triglycerideReferenceRange',
        'hasMember': 'Reference',
        'derivedFrom': 'Reference',
        'component': 'triglycerideComponent',
    }
    _choice_fields = {'effective': ['effectiveDateTime', 'effectivePeriod', 'effectiveTiming', 'effectiveInstant'], 'value': ['valueQuantity']}

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    focus: Reference | FHIRList[Reference] | list | dict
    encounter: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    effectiveTiming: Timing | dict | None
    effectiveInstant: Optional[Instant] = None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference] | list | dict
    valueQuantity: Quantity | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | dict | None
    note: Annotation | FHIRList[Annotation] | list | dict
    bodySite: CodeableConcept | dict | None
    method: CodeableConcept | dict | None
    specimen: Reference | dict | None
    device: Reference | dict | None
    referenceRange: triglycerideReferenceRange | dict | None
    hasMember: Reference | dict | None
    derivedFrom: Reference | dict | None
    component: triglycerideComponent | FHIRList[triglycerideComponent] | list | dict


class vitalsignsCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | FHIRList[Coding] | list | dict
    text: Optional[String] = None


class vitalsignsCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class vitalsignsReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'low': 'Quantity',
        'high': 'Quantity',
        'type_': 'CodeableConcept',
        'appliesTo': 'CodeableConcept',
        'age': 'Range',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    low: Quantity | dict | None
    high: Quantity | dict | None
    type_: CodeableConcept | dict | None
    appliesTo: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    age: Range | dict | None
    text: Optional[String] = None


class vitalsignsComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueCodeableConcept': 'CodeableConcept',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueSampledData': 'SampledData',
        'valuePeriod': 'Period',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
    }
    _choice_fields = {
        'value': [
            'valueQuantity',
            'valueCodeableConcept',
            'valueString',
            'valueBoolean',
            'valueInteger',
            'valueRange',
            'valueRatio',
            'valueSampledData',
            'valueTime',
            'valueDateTime',
            'valuePeriod',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueQuantity: Quantity | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueSampledData: SampledData | dict | None
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Period | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    referenceRange: Any = None


class vitalsigns(FHIRResource):
    _resource_type = "vitalsigns"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'basedOn',
        'partOf',
        'focus',
        'performer',
        'interpretation',
        'note',
        'referenceRange',
        'hasMember',
        'derivedFrom',
        'component',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'focus': 'Reference',
        'encounter': 'Reference',
        'effectivePeriod': 'Period',
        'performer': 'Reference',
        'valueQuantity': 'Quantity',
        'valueCodeableConcept': 'CodeableConcept',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueSampledData': 'SampledData',
        'valuePeriod': 'Period',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
        'note': 'Annotation',
        'bodySite': 'CodeableConcept',
        'method': 'CodeableConcept',
        'specimen': 'Reference',
        'device': 'Reference',
        'referenceRange': 'vitalsignsReferenceRange',
        'hasMember': 'Reference',
        'derivedFrom': 'Reference',
        'component': 'vitalsignsComponent',
    }
    _choice_fields = {
        'effective': ['effectiveDateTime', 'effectivePeriod'],
        'value': [
            'valueQuantity',
            'valueCodeableConcept',
            'valueString',
            'valueBoolean',
            'valueInteger',
            'valueRange',
            'valueRatio',
            'valueSampledData',
            'valueTime',
            'valueDateTime',
            'valuePeriod',
        ],
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | dict | None
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    focus: Reference | FHIRList[Reference] | list | dict
    encounter: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference] | list | dict
    valueQuantity: Quantity | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueSampledData: SampledData | dict | None
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Period | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    bodySite: CodeableConcept | dict | None
    method: CodeableConcept | dict | None
    specimen: Reference | dict | None
    device: Reference | dict | None
    referenceRange: vitalsignsReferenceRange | FHIRList[vitalsignsReferenceRange] | list | dict
    hasMember: Reference | FHIRList[Reference] | list | dict
    derivedFrom: Reference | FHIRList[Reference] | list | dict
    component: vitalsignsComponent | FHIRList[vitalsignsComponent] | list | dict


class vitalspanelCategory(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | FHIRList[Coding] | list | dict
    text: Optional[String] = None


class vitalspanelCategoryCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class vitalspanelCode(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | FHIRList[Coding] | list | dict
    text: Optional[String] = None


class vitalspanelCodeCoding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class vitalspanelReferenceRange(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'appliesTo'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'low': 'Quantity',
        'high': 'Quantity',
        'type_': 'CodeableConcept',
        'appliesTo': 'CodeableConcept',
        'age': 'Range',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    low: Quantity | dict | None
    high: Quantity | dict | None
    type_: CodeableConcept | dict | None
    appliesTo: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    age: Range | dict | None
    text: Optional[String] = None


class vitalspanelComponent(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'interpretation', 'referenceRange'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueCodeableConcept': 'CodeableConcept',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueSampledData': 'SampledData',
        'valuePeriod': 'Period',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
    }
    _choice_fields = {
        'value': [
            'valueQuantity',
            'valueCodeableConcept',
            'valueString',
            'valueBoolean',
            'valueInteger',
            'valueRange',
            'valueRatio',
            'valueSampledData',
            'valueTime',
            'valueDateTime',
            'valuePeriod',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    code: CodeableConcept | dict | None
    valueQuantity: Quantity | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueSampledData: SampledData | dict | None
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Period | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    referenceRange: Any = None


class vitalspanel(FHIRResource):
    _resource_type = "vitalspanel"
    _list_fields = {
        'contained',
        'extension',
        'modifierExtension',
        'identifier',
        'basedOn',
        'partOf',
        'focus',
        'performer',
        'interpretation',
        'note',
        'referenceRange',
        'hasMember',
        'derivedFrom',
        'component',
    }
    _field_types = {
        'meta': 'Meta',
        'text': 'Narrative',
        'contained': 'Resource',
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'basedOn': 'Reference',
        'partOf': 'Reference',
        'category': 'CodeableConcept',
        'code': 'CodeableConcept',
        'subject': 'Reference',
        'focus': 'Reference',
        'encounter': 'Reference',
        'effectivePeriod': 'Period',
        'performer': 'Reference',
        'valueQuantity': 'Quantity',
        'valueCodeableConcept': 'CodeableConcept',
        'valueRange': 'Range',
        'valueRatio': 'Ratio',
        'valueSampledData': 'SampledData',
        'valuePeriod': 'Period',
        'dataAbsentReason': 'CodeableConcept',
        'interpretation': 'CodeableConcept',
        'note': 'Annotation',
        'bodySite': 'CodeableConcept',
        'method': 'CodeableConcept',
        'specimen': 'Reference',
        'device': 'Reference',
        'referenceRange': 'vitalspanelReferenceRange',
        'hasMember': 'Reference',
        'derivedFrom': 'Reference',
        'component': 'vitalspanelComponent',
    }
    _choice_fields = {
        'effective': ['effectiveDateTime', 'effectivePeriod'],
        'value': [
            'valueQuantity',
            'valueCodeableConcept',
            'valueString',
            'valueBoolean',
            'valueInteger',
            'valueRange',
            'valueRatio',
            'valueSampledData',
            'valueTime',
            'valueDateTime',
            'valuePeriod',
        ],
    }

    id: Optional[str] = None
    meta: Meta | dict | None
    implicitRules: Optional[Uri] = None
    language: Optional[Code] = None
    text: Narrative | dict | None
    contained: FHIRResource | FHIRList[FHIRResource] | list | dict
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | FHIRList[Identifier] | list | dict
    basedOn: Reference | FHIRList[Reference] | list | dict
    partOf: Reference | FHIRList[Reference] | list | dict
    status: Optional[Code] = None
    category: CodeableConcept | dict | None
    code: CodeableConcept | dict | None
    subject: Reference | dict | None
    focus: Reference | FHIRList[Reference] | list | dict
    encounter: Reference | dict | None
    effectiveDateTime: Optional[DateTime] = None
    effectivePeriod: Period | dict | None
    issued: Optional[Instant] = None
    performer: Reference | FHIRList[Reference] | list | dict
    valueQuantity: Quantity | dict | None
    valueCodeableConcept: CodeableConcept | dict | None
    valueString: Optional[String] = None
    valueBoolean: Optional[Boolean] = None
    valueInteger: Optional[Integer] = None
    valueRange: Range | dict | None
    valueRatio: Ratio | dict | None
    valueSampledData: SampledData | dict | None
    valueTime: Optional[Time] = None
    valueDateTime: Optional[DateTime] = None
    valuePeriod: Period | dict | None
    dataAbsentReason: CodeableConcept | dict | None
    interpretation: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    note: Annotation | FHIRList[Annotation] | list | dict
    bodySite: CodeableConcept | dict | None
    method: CodeableConcept | dict | None
    specimen: Reference | dict | None
    device: Reference | dict | None
    referenceRange: vitalspanelReferenceRange | FHIRList[vitalspanelReferenceRange] | list | dict
    hasMember: Reference | FHIRList[Reference] | list | dict
    derivedFrom: Reference | FHIRList[Reference] | list | dict
    component: vitalspanelComponent | FHIRList[vitalspanelComponent] | list | dict
