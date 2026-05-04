# Generated - do not edit
from __future__ import annotations

from typing import Any, Optional

from zato_fhir.base import FHIRElement, FHIRList
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


class BackboneElement(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]


class Address(FHIRElement):
    _list_fields = {'extension', 'line'}
    _field_types = {'extension': 'Extension', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    use: Optional[Code] = None
    type_: Optional[Code] = None
    text: Optional[String] = None
    line: String | FHIRList[String] = None
    city: Optional[String] = None
    district: Optional[String] = None
    state: Optional[String] = None
    postalCode: Optional[String] = None
    country: Optional[String] = None
    period: Optional[Period]


class Age(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class Annotation(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'authorReference': 'Reference'}
    _choice_fields = {'author': ['authorReference', 'authorString']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    authorReference: Optional[Reference] = None
    authorString: Optional[String] = None
    time: Optional[DateTime] = None
    text: Optional[Markdown] = None


class Attachment(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    contentType: Optional[Code] = None
    language: Optional[Code] = None
    data: Optional[Base64Binary] = None
    url: Optional[Url] = None
    size: Optional[UnsignedInt] = None
    hash: Optional[Base64Binary] = None
    title: Optional[String] = None
    creation: Optional[DateTime] = None


class CodeableConcept(FHIRElement):
    _list_fields = {'extension', 'coding'}
    _field_types = {'extension': 'Extension', 'coding': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Coding | FHIRList[Coding]
    text: Optional[String] = None


class Coding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class ContactDetail(FHIRElement):
    _list_fields = {'extension', 'telecom'}
    _field_types = {'extension': 'Extension', 'telecom': 'ContactPoint'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    name: Optional[String] = None
    telecom: ContactPoint | FHIRList[ContactPoint]


class ContactPoint(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    system: Optional[Code] = None
    value: Optional[String] = None
    use: Optional[Code] = None
    rank: Optional[PositiveInt] = None
    period: Optional[Period]


class Contributor(FHIRElement):
    _list_fields = {'extension', 'contact'}
    _field_types = {'extension': 'Extension', 'contact': 'ContactDetail'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    name: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail]


class Count(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class DataRequirement(FHIRElement):
    _list_fields = {'extension', 'profile', 'mustSupport', 'codeFilter', 'dateFilter', 'sort'}
    _field_types = {'extension': 'Extension', 'subjectCodeableConcept': 'CodeableConcept', 'subjectReference': 'Reference', 'codeFilter': 'Element', 'dateFilter': 'Element', 'sort': 'Element'}
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    profile: Canonical | FHIRList[Canonical] = None
    subjectCodeableConcept: Optional[CodeableConcept] = None
    subjectReference: Optional[Reference] = None
    mustSupport: String | FHIRList[String] = None
    codeFilter: Element | FHIRList[Element]
    dateFilter: Element | FHIRList[Element]
    limit: Optional[PositiveInt] = None
    sort: Element | FHIRList[Element]


class Distance(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class Dosage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'additionalInstruction', 'doseAndRate'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'additionalInstruction': 'CodeableConcept', 'timing': 'Timing', 'asNeededCodeableConcept': 'CodeableConcept', 'site': 'CodeableConcept', 'route': 'CodeableConcept', 'method': 'CodeableConcept', 'doseAndRate': 'Element', 'maxDosePerPeriod': 'Ratio', 'maxDosePerAdministration': 'Quantity', 'maxDosePerLifetime': 'Quantity'}
    _choice_fields = {'asNeeded': ['asNeededBoolean', 'asNeededCodeableConcept']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequence: Optional[Integer] = None
    text: Optional[String] = None
    additionalInstruction: CodeableConcept | FHIRList[CodeableConcept]
    patientInstruction: Optional[String] = None
    timing: Optional[Timing]
    asNeededBoolean: Optional[Boolean] = None
    asNeededCodeableConcept: Optional[CodeableConcept] = None
    site: Optional[CodeableConcept]
    route: Optional[CodeableConcept]
    method: Optional[CodeableConcept]
    doseAndRate: Element | FHIRList[Element]
    maxDosePerPeriod: Optional[Ratio]
    maxDosePerAdministration: Optional[Quantity]
    maxDosePerLifetime: Optional[Quantity]


class Duration(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class ElementDefinition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'representation', 'code', 'alias', 'type_', 'example', 'condition', 'constraint', 'mapping'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'Coding', 'slicing': 'Element', 'base': 'Element', 'type_': 'Element', 'defaultValueAddress': 'Address', 'defaultValueAge': 'Age', 'defaultValueAnnotation': 'Annotation', 'defaultValueAttachment': 'Attachment', 'defaultValueCodeableConcept': 'CodeableConcept', 'defaultValueCoding': 'Coding', 'defaultValueContactPoint': 'ContactPoint', 'defaultValueCount': 'Count', 'defaultValueDistance': 'Distance', 'defaultValueDuration': 'Duration', 'defaultValueHumanName': 'HumanName', 'defaultValueIdentifier': 'Identifier', 'defaultValueMoney': 'Money', 'defaultValuePeriod': 'Period', 'defaultValueQuantity': 'Quantity', 'defaultValueRange': 'Range', 'defaultValueRatio': 'Ratio', 'defaultValueReference': 'Reference', 'defaultValueSampledData': 'SampledData', 'defaultValueSignature': 'Signature', 'defaultValueTiming': 'Timing', 'defaultValueContactDetail': 'ContactDetail', 'defaultValueContributor': 'Contributor', 'defaultValueDataRequirement': 'DataRequirement', 'defaultValueExpression': 'Expression', 'defaultValueParameterDefinition': 'ParameterDefinition', 'defaultValueRelatedArtifact': 'RelatedArtifact', 'defaultValueTriggerDefinition': 'TriggerDefinition', 'defaultValueUsageContext': 'UsageContext', 'defaultValueDosage': 'Dosage', 'defaultValueMeta': 'Meta', 'fixedAddress': 'Address', 'fixedAge': 'Age', 'fixedAnnotation': 'Annotation', 'fixedAttachment': 'Attachment', 'fixedCodeableConcept': 'CodeableConcept', 'fixedCoding': 'Coding', 'fixedContactPoint': 'ContactPoint', 'fixedCount': 'Count', 'fixedDistance': 'Distance', 'fixedDuration': 'Duration', 'fixedHumanName': 'HumanName', 'fixedIdentifier': 'Identifier', 'fixedMoney': 'Money', 'fixedPeriod': 'Period', 'fixedQuantity': 'Quantity', 'fixedRange': 'Range', 'fixedRatio': 'Ratio', 'fixedReference': 'Reference', 'fixedSampledData': 'SampledData', 'fixedSignature': 'Signature', 'fixedTiming': 'Timing', 'fixedContactDetail': 'ContactDetail', 'fixedContributor': 'Contributor', 'fixedDataRequirement': 'DataRequirement', 'fixedExpression': 'Expression', 'fixedParameterDefinition': 'ParameterDefinition', 'fixedRelatedArtifact': 'RelatedArtifact', 'fixedTriggerDefinition': 'TriggerDefinition', 'fixedUsageContext': 'UsageContext', 'fixedDosage': 'Dosage', 'fixedMeta': 'Meta', 'patternAddress': 'Address', 'patternAge': 'Age', 'patternAnnotation': 'Annotation', 'patternAttachment': 'Attachment', 'patternCodeableConcept': 'CodeableConcept', 'patternCoding': 'Coding', 'patternContactPoint': 'ContactPoint', 'patternCount': 'Count', 'patternDistance': 'Distance', 'patternDuration': 'Duration', 'patternHumanName': 'HumanName', 'patternIdentifier': 'Identifier', 'patternMoney': 'Money', 'patternPeriod': 'Period', 'patternQuantity': 'Quantity', 'patternRange': 'Range', 'patternRatio': 'Ratio', 'patternReference': 'Reference', 'patternSampledData': 'SampledData', 'patternSignature': 'Signature', 'patternTiming': 'Timing', 'patternContactDetail': 'ContactDetail', 'patternContributor': 'Contributor', 'patternDataRequirement': 'DataRequirement', 'patternExpression': 'Expression', 'patternParameterDefinition': 'ParameterDefinition', 'patternRelatedArtifact': 'RelatedArtifact', 'patternTriggerDefinition': 'TriggerDefinition', 'patternUsageContext': 'UsageContext', 'patternDosage': 'Dosage', 'patternMeta': 'Meta', 'example': 'Element', 'minValueQuantity': 'Quantity', 'maxValueQuantity': 'Quantity', 'constraint': 'Element', 'binding': 'Element', 'mapping': 'Element'}
    _choice_fields = {'defaultValue': ['defaultValueBase64Binary', 'defaultValueBoolean', 'defaultValueCanonical', 'defaultValueCode', 'defaultValueDate', 'defaultValueDateTime', 'defaultValueDecimal', 'defaultValueId', 'defaultValueInstant', 'defaultValueInteger', 'defaultValueMarkdown', 'defaultValueOid', 'defaultValuePositiveInt', 'defaultValueString', 'defaultValueTime', 'defaultValueUnsignedInt', 'defaultValueUri', 'defaultValueUrl', 'defaultValueUuid', 'defaultValueAddress', 'defaultValueAge', 'defaultValueAnnotation', 'defaultValueAttachment', 'defaultValueCodeableConcept', 'defaultValueCoding', 'defaultValueContactPoint', 'defaultValueCount', 'defaultValueDistance', 'defaultValueDuration', 'defaultValueHumanName', 'defaultValueIdentifier', 'defaultValueMoney', 'defaultValuePeriod', 'defaultValueQuantity', 'defaultValueRange', 'defaultValueRatio', 'defaultValueReference', 'defaultValueSampledData', 'defaultValueSignature', 'defaultValueTiming', 'defaultValueContactDetail', 'defaultValueContributor', 'defaultValueDataRequirement', 'defaultValueExpression', 'defaultValueParameterDefinition', 'defaultValueRelatedArtifact', 'defaultValueTriggerDefinition', 'defaultValueUsageContext', 'defaultValueDosage', 'defaultValueMeta'], 'fixed': ['fixedBase64Binary', 'fixedBoolean', 'fixedCanonical', 'fixedCode', 'fixedDate', 'fixedDateTime', 'fixedDecimal', 'fixedId', 'fixedInstant', 'fixedInteger', 'fixedMarkdown', 'fixedOid', 'fixedPositiveInt', 'fixedString', 'fixedTime', 'fixedUnsignedInt', 'fixedUri', 'fixedUrl', 'fixedUuid', 'fixedAddress', 'fixedAge', 'fixedAnnotation', 'fixedAttachment', 'fixedCodeableConcept', 'fixedCoding', 'fixedContactPoint', 'fixedCount', 'fixedDistance', 'fixedDuration', 'fixedHumanName', 'fixedIdentifier', 'fixedMoney', 'fixedPeriod', 'fixedQuantity', 'fixedRange', 'fixedRatio', 'fixedReference', 'fixedSampledData', 'fixedSignature', 'fixedTiming', 'fixedContactDetail', 'fixedContributor', 'fixedDataRequirement', 'fixedExpression', 'fixedParameterDefinition', 'fixedRelatedArtifact', 'fixedTriggerDefinition', 'fixedUsageContext', 'fixedDosage', 'fixedMeta'], 'maxValue': ['maxValueDate', 'maxValueDateTime', 'maxValueInstant', 'maxValueTime', 'maxValueDecimal', 'maxValueInteger', 'maxValuePositiveInt', 'maxValueUnsignedInt', 'maxValueQuantity'], 'minValue': ['minValueDate', 'minValueDateTime', 'minValueInstant', 'minValueTime', 'minValueDecimal', 'minValueInteger', 'minValuePositiveInt', 'minValueUnsignedInt', 'minValueQuantity'], 'pattern': ['patternBase64Binary', 'patternBoolean', 'patternCanonical', 'patternCode', 'patternDate', 'patternDateTime', 'patternDecimal', 'patternId', 'patternInstant', 'patternInteger', 'patternMarkdown', 'patternOid', 'patternPositiveInt', 'patternString', 'patternTime', 'patternUnsignedInt', 'patternUri', 'patternUrl', 'patternUuid', 'patternAddress', 'patternAge', 'patternAnnotation', 'patternAttachment', 'patternCodeableConcept', 'patternCoding', 'patternContactPoint', 'patternCount', 'patternDistance', 'patternDuration', 'patternHumanName', 'patternIdentifier', 'patternMoney', 'patternPeriod', 'patternQuantity', 'patternRange', 'patternRatio', 'patternReference', 'patternSampledData', 'patternSignature', 'patternTiming', 'patternContactDetail', 'patternContributor', 'patternDataRequirement', 'patternExpression', 'patternParameterDefinition', 'patternRelatedArtifact', 'patternTriggerDefinition', 'patternUsageContext', 'patternDosage', 'patternMeta']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    path: Optional[String] = None
    representation: Code | FHIRList[Code] = None
    sliceName: Optional[String] = None
    sliceIsConstraining: Optional[Boolean] = None
    label: Optional[String] = None
    code: Coding | FHIRList[Coding]
    slicing: Optional[Element]
    short: Optional[String] = None
    definition: Optional[Markdown] = None
    comment: Optional[Markdown] = None
    requirements: Optional[Markdown] = None
    alias: String | FHIRList[String] = None
    min: Optional[UnsignedInt] = None
    max: Optional[String] = None
    base: Optional[Element]
    contentReference: Optional[Uri] = None
    type_: Element | FHIRList[Element]
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
    defaultValueAddress: Optional[Address] = None
    defaultValueAge: Optional[Age] = None
    defaultValueAnnotation: Optional[Annotation] = None
    defaultValueAttachment: Optional[Attachment] = None
    defaultValueCodeableConcept: Optional[CodeableConcept] = None
    defaultValueCoding: Optional[Coding] = None
    defaultValueContactPoint: Optional[ContactPoint] = None
    defaultValueCount: Optional[Count] = None
    defaultValueDistance: Optional[Distance] = None
    defaultValueDuration: Optional[Duration] = None
    defaultValueHumanName: Optional[HumanName] = None
    defaultValueIdentifier: Optional[Identifier] = None
    defaultValueMoney: Optional[Money] = None
    defaultValuePeriod: Optional[Period] = None
    defaultValueQuantity: Optional[Quantity] = None
    defaultValueRange: Optional[Range] = None
    defaultValueRatio: Optional[Ratio] = None
    defaultValueReference: Optional[Reference] = None
    defaultValueSampledData: Optional[SampledData] = None
    defaultValueSignature: Optional[Signature] = None
    defaultValueTiming: Optional[Timing] = None
    defaultValueContactDetail: Optional[ContactDetail] = None
    defaultValueContributor: Optional[Contributor] = None
    defaultValueDataRequirement: Optional[DataRequirement] = None
    defaultValueExpression: Optional[Expression] = None
    defaultValueParameterDefinition: Optional[ParameterDefinition] = None
    defaultValueRelatedArtifact: Optional[RelatedArtifact] = None
    defaultValueTriggerDefinition: Optional[TriggerDefinition] = None
    defaultValueUsageContext: Optional[UsageContext] = None
    defaultValueDosage: Optional[Dosage] = None
    defaultValueMeta: Optional[Meta] = None
    meaningWhenMissing: Optional[Markdown] = None
    orderMeaning: Optional[String] = None
    fixedBase64Binary: Optional[Base64Binary] = None
    fixedBoolean: Optional[Boolean] = None
    fixedCanonical: Optional[Canonical] = None
    fixedCode: Optional[Code] = None
    fixedDate: Optional[Date] = None
    fixedDateTime: Optional[DateTime] = None
    fixedDecimal: Optional[Decimal] = None
    fixedId: Optional[Id] = None
    fixedInstant: Optional[Instant] = None
    fixedInteger: Optional[Integer] = None
    fixedMarkdown: Optional[Markdown] = None
    fixedOid: Optional[Oid] = None
    fixedPositiveInt: Optional[PositiveInt] = None
    fixedString: Optional[String] = None
    fixedTime: Optional[Time] = None
    fixedUnsignedInt: Optional[UnsignedInt] = None
    fixedUri: Optional[Uri] = None
    fixedUrl: Optional[Url] = None
    fixedUuid: Optional[Uuid] = None
    fixedAddress: Optional[Address] = None
    fixedAge: Optional[Age] = None
    fixedAnnotation: Optional[Annotation] = None
    fixedAttachment: Optional[Attachment] = None
    fixedCodeableConcept: Optional[CodeableConcept] = None
    fixedCoding: Optional[Coding] = None
    fixedContactPoint: Optional[ContactPoint] = None
    fixedCount: Optional[Count] = None
    fixedDistance: Optional[Distance] = None
    fixedDuration: Optional[Duration] = None
    fixedHumanName: Optional[HumanName] = None
    fixedIdentifier: Optional[Identifier] = None
    fixedMoney: Optional[Money] = None
    fixedPeriod: Optional[Period] = None
    fixedQuantity: Optional[Quantity] = None
    fixedRange: Optional[Range] = None
    fixedRatio: Optional[Ratio] = None
    fixedReference: Optional[Reference] = None
    fixedSampledData: Optional[SampledData] = None
    fixedSignature: Optional[Signature] = None
    fixedTiming: Optional[Timing] = None
    fixedContactDetail: Optional[ContactDetail] = None
    fixedContributor: Optional[Contributor] = None
    fixedDataRequirement: Optional[DataRequirement] = None
    fixedExpression: Optional[Expression] = None
    fixedParameterDefinition: Optional[ParameterDefinition] = None
    fixedRelatedArtifact: Optional[RelatedArtifact] = None
    fixedTriggerDefinition: Optional[TriggerDefinition] = None
    fixedUsageContext: Optional[UsageContext] = None
    fixedDosage: Optional[Dosage] = None
    fixedMeta: Optional[Meta] = None
    patternBase64Binary: Optional[Base64Binary] = None
    patternBoolean: Optional[Boolean] = None
    patternCanonical: Optional[Canonical] = None
    patternCode: Optional[Code] = None
    patternDate: Optional[Date] = None
    patternDateTime: Optional[DateTime] = None
    patternDecimal: Optional[Decimal] = None
    patternId: Optional[Id] = None
    patternInstant: Optional[Instant] = None
    patternInteger: Optional[Integer] = None
    patternMarkdown: Optional[Markdown] = None
    patternOid: Optional[Oid] = None
    patternPositiveInt: Optional[PositiveInt] = None
    patternString: Optional[String] = None
    patternTime: Optional[Time] = None
    patternUnsignedInt: Optional[UnsignedInt] = None
    patternUri: Optional[Uri] = None
    patternUrl: Optional[Url] = None
    patternUuid: Optional[Uuid] = None
    patternAddress: Optional[Address] = None
    patternAge: Optional[Age] = None
    patternAnnotation: Optional[Annotation] = None
    patternAttachment: Optional[Attachment] = None
    patternCodeableConcept: Optional[CodeableConcept] = None
    patternCoding: Optional[Coding] = None
    patternContactPoint: Optional[ContactPoint] = None
    patternCount: Optional[Count] = None
    patternDistance: Optional[Distance] = None
    patternDuration: Optional[Duration] = None
    patternHumanName: Optional[HumanName] = None
    patternIdentifier: Optional[Identifier] = None
    patternMoney: Optional[Money] = None
    patternPeriod: Optional[Period] = None
    patternQuantity: Optional[Quantity] = None
    patternRange: Optional[Range] = None
    patternRatio: Optional[Ratio] = None
    patternReference: Optional[Reference] = None
    patternSampledData: Optional[SampledData] = None
    patternSignature: Optional[Signature] = None
    patternTiming: Optional[Timing] = None
    patternContactDetail: Optional[ContactDetail] = None
    patternContributor: Optional[Contributor] = None
    patternDataRequirement: Optional[DataRequirement] = None
    patternExpression: Optional[Expression] = None
    patternParameterDefinition: Optional[ParameterDefinition] = None
    patternRelatedArtifact: Optional[RelatedArtifact] = None
    patternTriggerDefinition: Optional[TriggerDefinition] = None
    patternUsageContext: Optional[UsageContext] = None
    patternDosage: Optional[Dosage] = None
    patternMeta: Optional[Meta] = None
    example: Element | FHIRList[Element]
    minValueDate: Optional[Date] = None
    minValueDateTime: Optional[DateTime] = None
    minValueInstant: Optional[Instant] = None
    minValueTime: Optional[Time] = None
    minValueDecimal: Optional[Decimal] = None
    minValueInteger: Optional[Integer] = None
    minValuePositiveInt: Optional[PositiveInt] = None
    minValueUnsignedInt: Optional[UnsignedInt] = None
    minValueQuantity: Optional[Quantity] = None
    maxValueDate: Optional[Date] = None
    maxValueDateTime: Optional[DateTime] = None
    maxValueInstant: Optional[Instant] = None
    maxValueTime: Optional[Time] = None
    maxValueDecimal: Optional[Decimal] = None
    maxValueInteger: Optional[Integer] = None
    maxValuePositiveInt: Optional[PositiveInt] = None
    maxValueUnsignedInt: Optional[UnsignedInt] = None
    maxValueQuantity: Optional[Quantity] = None
    maxLength: Optional[Integer] = None
    condition: Id | FHIRList[Id] = None
    constraint: Element | FHIRList[Element]
    mustSupport: Optional[Boolean] = None
    isModifier: Optional[Boolean] = None
    isModifierReason: Optional[String] = None
    isSummary: Optional[Boolean] = None
    binding: Optional[Element]
    mapping: Element | FHIRList[Element]


class Expression(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    description: Optional[String] = None
    name: Optional[Id] = None
    language: Optional[Code] = None
    expression: Optional[String] = None
    reference: Optional[Uri] = None


class Extension(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'valueAddress': 'Address', 'valueAge': 'Age', 'valueAnnotation': 'Annotation', 'valueAttachment': 'Attachment', 'valueCodeableConcept': 'CodeableConcept', 'valueCoding': 'Coding', 'valueContactPoint': 'ContactPoint', 'valueCount': 'Count', 'valueDistance': 'Distance', 'valueDuration': 'Duration', 'valueHumanName': 'HumanName', 'valueIdentifier': 'Identifier', 'valueMoney': 'Money', 'valuePeriod': 'Period', 'valueQuantity': 'Quantity', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueReference': 'Reference', 'valueSampledData': 'SampledData', 'valueSignature': 'Signature', 'valueTiming': 'Timing', 'valueContactDetail': 'ContactDetail', 'valueContributor': 'Contributor', 'valueDataRequirement': 'DataRequirement', 'valueExpression': 'Expression', 'valueParameterDefinition': 'ParameterDefinition', 'valueRelatedArtifact': 'RelatedArtifact', 'valueTriggerDefinition': 'TriggerDefinition', 'valueUsageContext': 'UsageContext', 'valueDosage': 'Dosage', 'valueMeta': 'Meta'}
    _choice_fields = {'value': ['valueBase64Binary', 'valueBoolean', 'valueCanonical', 'valueCode', 'valueDate', 'valueDateTime', 'valueDecimal', 'valueId', 'valueInstant', 'valueInteger', 'valueMarkdown', 'valueOid', 'valuePositiveInt', 'valueString', 'valueTime', 'valueUnsignedInt', 'valueUri', 'valueUrl', 'valueUuid', 'valueAddress', 'valueAge', 'valueAnnotation', 'valueAttachment', 'valueCodeableConcept', 'valueCoding', 'valueContactPoint', 'valueCount', 'valueDistance', 'valueDuration', 'valueHumanName', 'valueIdentifier', 'valueMoney', 'valuePeriod', 'valueQuantity', 'valueRange', 'valueRatio', 'valueReference', 'valueSampledData', 'valueSignature', 'valueTiming', 'valueContactDetail', 'valueContributor', 'valueDataRequirement', 'valueExpression', 'valueParameterDefinition', 'valueRelatedArtifact', 'valueTriggerDefinition', 'valueUsageContext', 'valueDosage', 'valueMeta']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    url: Optional[str] = None
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
    valueAddress: Optional[Address] = None
    valueAge: Optional[Age] = None
    valueAnnotation: Optional[Annotation] = None
    valueAttachment: Optional[Attachment] = None
    valueCodeableConcept: Optional[CodeableConcept] = None
    valueCoding: Optional[Coding] = None
    valueContactPoint: Optional[ContactPoint] = None
    valueCount: Optional[Count] = None
    valueDistance: Optional[Distance] = None
    valueDuration: Optional[Duration] = None
    valueHumanName: Optional[HumanName] = None
    valueIdentifier: Optional[Identifier] = None
    valueMoney: Optional[Money] = None
    valuePeriod: Optional[Period] = None
    valueQuantity: Optional[Quantity] = None
    valueRange: Optional[Range] = None
    valueRatio: Optional[Ratio] = None
    valueReference: Optional[Reference] = None
    valueSampledData: Optional[SampledData] = None
    valueSignature: Optional[Signature] = None
    valueTiming: Optional[Timing] = None
    valueContactDetail: Optional[ContactDetail] = None
    valueContributor: Optional[Contributor] = None
    valueDataRequirement: Optional[DataRequirement] = None
    valueExpression: Optional[Expression] = None
    valueParameterDefinition: Optional[ParameterDefinition] = None
    valueRelatedArtifact: Optional[RelatedArtifact] = None
    valueTriggerDefinition: Optional[TriggerDefinition] = None
    valueUsageContext: Optional[UsageContext] = None
    valueDosage: Optional[Dosage] = None
    valueMeta: Optional[Meta] = None


class HumanName(FHIRElement):
    _list_fields = {'extension', 'given', 'prefix', 'suffix'}
    _field_types = {'extension': 'Extension', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    use: Optional[Code] = None
    text: Optional[String] = None
    family: Optional[String] = None
    given: String | FHIRList[String] = None
    prefix: String | FHIRList[String] = None
    suffix: String | FHIRList[String] = None
    period: Optional[Period]


class Identifier(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'type_': 'CodeableConcept', 'period': 'Period', 'assigner': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    use: Optional[Code] = None
    type_: Optional[CodeableConcept]
    system: Optional[Uri] = None
    value: Optional[String] = None
    period: Optional[Period]
    assigner: Optional[Reference]


class MarketingStatus(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'country': 'CodeableConcept', 'jurisdiction': 'CodeableConcept', 'status': 'CodeableConcept', 'dateRange': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    country: Optional[CodeableConcept]
    jurisdiction: Optional[CodeableConcept]
    status: Optional[CodeableConcept]
    dateRange: Optional[Period]
    restoreDate: Optional[DateTime] = None


class Meta(FHIRElement):
    _list_fields = {'extension', 'profile', 'security', 'tag'}
    _field_types = {'extension': 'Extension', 'security': 'Coding', 'tag': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    versionId: Optional[Id] = None
    lastUpdated: Optional[Instant] = None
    source: Optional[Uri] = None
    profile: Canonical | FHIRList[Canonical] = None
    security: Coding | FHIRList[Coding]
    tag: Coding | FHIRList[Coding]


class Money(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    value: Optional[Decimal] = None
    currency: Optional[Code] = None


class MoneyQuantity(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class Narrative(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    status: Optional[Code] = None
    div: Optional[Xhtml] = None


class ParameterDefinition(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    name: Optional[Code] = None
    use: Optional[Code] = None
    min: Optional[Integer] = None
    max: Optional[String] = None
    documentation: Optional[String] = None
    type_: Optional[Code] = None
    profile: Optional[Canonical] = None


class Period(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    start: Optional[DateTime] = None
    end: Optional[DateTime] = None


class Population(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'ageRange': 'Range', 'ageCodeableConcept': 'CodeableConcept', 'gender': 'CodeableConcept', 'race': 'CodeableConcept', 'physiologicalCondition': 'CodeableConcept'}
    _choice_fields = {'age': ['ageRange', 'ageCodeableConcept']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    ageRange: Optional[Range] = None
    ageCodeableConcept: Optional[CodeableConcept] = None
    gender: Optional[CodeableConcept]
    race: Optional[CodeableConcept]
    physiologicalCondition: Optional[CodeableConcept]


class ProdCharacteristic(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'color', 'imprint', 'image'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'height': 'Quantity', 'width': 'Quantity', 'depth': 'Quantity', 'weight': 'Quantity', 'nominalVolume': 'Quantity', 'externalDiameter': 'Quantity', 'image': 'Attachment', 'scoring': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    height: Optional[Quantity]
    width: Optional[Quantity]
    depth: Optional[Quantity]
    weight: Optional[Quantity]
    nominalVolume: Optional[Quantity]
    externalDiameter: Optional[Quantity]
    shape: Optional[String] = None
    color: String | FHIRList[String] = None
    imprint: String | FHIRList[String] = None
    image: Attachment | FHIRList[Attachment]
    scoring: Optional[CodeableConcept]


class ProductShelfLife(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'specialPrecautionsForStorage'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type_': 'CodeableConcept', 'period': 'Quantity', 'specialPrecautionsForStorage': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Identifier]
    type_: Optional[CodeableConcept]
    period: Optional[Quantity]
    specialPrecautionsForStorage: CodeableConcept | FHIRList[CodeableConcept]


class Quantity(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class Range(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'low': 'Quantity', 'high': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    low: Optional[Quantity]
    high: Optional[Quantity]


class Ratio(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'numerator': 'Quantity', 'denominator': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    numerator: Optional[Quantity]
    denominator: Optional[Quantity]


class Reference(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'identifier': 'Identifier'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    reference: Optional[String] = None
    type_: Optional[Uri] = None
    identifier: Optional[Identifier]
    display: Optional[String] = None


class RelatedArtifact(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'document': 'Attachment'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    label: Optional[String] = None
    display: Optional[String] = None
    citation: Optional[Markdown] = None
    url: Optional[Url] = None
    document: Optional[Attachment]
    resource: Optional[Canonical] = None


class SampledData(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'origin': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    origin: Optional[Quantity]
    period: Optional[Decimal] = None
    factor: Optional[Decimal] = None
    lowerLimit: Optional[Decimal] = None
    upperLimit: Optional[Decimal] = None
    dimensions: Optional[PositiveInt] = None
    data: Optional[String] = None


class Signature(FHIRElement):
    _list_fields = {'extension', 'type_'}
    _field_types = {'extension': 'Extension', 'type_': 'Coding', 'who': 'Reference', 'onBehalfOf': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    type_: Coding | FHIRList[Coding]
    when: Optional[Instant] = None
    who: Optional[Reference]
    onBehalfOf: Optional[Reference]
    targetFormat: Optional[Code] = None
    sigFormat: Optional[Code] = None
    data: Optional[Base64Binary] = None


class SimpleQuantity(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class SubstanceAmount(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'amountQuantity': 'Quantity', 'amountRange': 'Range', 'amountType': 'CodeableConcept', 'referenceRange': 'Element'}
    _choice_fields = {'amount': ['amountQuantity', 'amountRange', 'amountString']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    amountQuantity: Optional[Quantity] = None
    amountRange: Optional[Range] = None
    amountString: Optional[String] = None
    amountType: Optional[CodeableConcept]
    amountText: Optional[String] = None
    referenceRange: Optional[Element]


class Timing(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'event'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'repeat': 'Element', 'code': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    event: DateTime | FHIRList[DateTime] = None
    repeat: Optional[Element]
    code: Optional[CodeableConcept]


class TriggerDefinition(FHIRElement):
    _list_fields = {'extension', 'data'}
    _field_types = {'extension': 'Extension', 'timingTiming': 'Timing', 'timingReference': 'Reference', 'data': 'DataRequirement', 'condition': 'Expression'}
    _choice_fields = {'timing': ['timingTiming', 'timingReference', 'timingDate', 'timingDateTime']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    type_: Optional[Code] = None
    name: Optional[String] = None
    timingTiming: Optional[Timing] = None
    timingReference: Optional[Reference] = None
    timingDate: Optional[Date] = None
    timingDateTime: Optional[DateTime] = None
    data: DataRequirement | FHIRList[DataRequirement]
    condition: Optional[Expression]


class UsageContext(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'code': 'Coding', 'valueCodeableConcept': 'CodeableConcept', 'valueQuantity': 'Quantity', 'valueRange': 'Range', 'valueReference': 'Reference'}
    _choice_fields = {'value': ['valueCodeableConcept', 'valueQuantity', 'valueRange', 'valueReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    code: Optional[Coding]
    valueCodeableConcept: Optional[CodeableConcept] = None
    valueQuantity: Optional[Quantity] = None
    valueRange: Optional[Range] = None
    valueReference: Optional[Reference] = None


class bodySite(FHIRElement):
    _field_types = {'extension': 'Extension', 'valueReference': 'Reference'}
    _choice_fields = {'value': ['valueReference']}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None
    valueReference: Optional[Reference] = None


class capabilities(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueCode']}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None
    valueCode: Optional[Code] = None


class designNote(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueMarkdown']}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None
    valueMarkdown: Optional[Markdown] = None


class display(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueString']}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None
    valueString: Optional[String] = None


class entryFormat(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueString']}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None
    valueString: Optional[String] = None


class geolocation(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'extension': 'Extension', 'extension': 'Extension', 'valueAddress': 'Address', 'valueAge': 'Age', 'valueAnnotation': 'Annotation', 'valueAttachment': 'Attachment', 'valueCodeableConcept': 'CodeableConcept', 'valueCoding': 'Coding', 'valueContactPoint': 'ContactPoint', 'valueCount': 'Count', 'valueDistance': 'Distance', 'valueDuration': 'Duration', 'valueHumanName': 'HumanName', 'valueIdentifier': 'Identifier', 'valueMoney': 'Money', 'valuePeriod': 'Period', 'valueQuantity': 'Quantity', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueReference': 'Reference', 'valueSampledData': 'SampledData', 'valueSignature': 'Signature', 'valueTiming': 'Timing', 'valueContactDetail': 'ContactDetail', 'valueContributor': 'Contributor', 'valueDataRequirement': 'DataRequirement', 'valueExpression': 'Expression', 'valueParameterDefinition': 'ParameterDefinition', 'valueRelatedArtifact': 'RelatedArtifact', 'valueTriggerDefinition': 'TriggerDefinition', 'valueUsageContext': 'UsageContext', 'valueDosage': 'Dosage', 'valueMeta': 'Meta'}
    _choice_fields = {'value': ['valueBase64Binary', 'valueBoolean', 'valueCanonical', 'valueCode', 'valueDate', 'valueDateTime', 'valueDecimal', 'valueId', 'valueInstant', 'valueInteger', 'valueMarkdown', 'valueOid', 'valuePositiveInt', 'valueString', 'valueTime', 'valueUnsignedInt', 'valueUri', 'valueUrl', 'valueUuid', 'valueAddress', 'valueAge', 'valueAnnotation', 'valueAttachment', 'valueCodeableConcept', 'valueCoding', 'valueContactPoint', 'valueCount', 'valueDistance', 'valueDuration', 'valueHumanName', 'valueIdentifier', 'valueMoney', 'valuePeriod', 'valueQuantity', 'valueRange', 'valueRatio', 'valueReference', 'valueSampledData', 'valueSignature', 'valueTiming', 'valueContactDetail', 'valueContributor', 'valueDataRequirement', 'valueExpression', 'valueParameterDefinition', 'valueRelatedArtifact', 'valueTriggerDefinition', 'valueUsageContext', 'valueDosage', 'valueMeta']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    extension: Optional[Extension]
    extension: Optional[Extension]
    url: Optional[str] = None
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
    valueAddress: Optional[Address] = None
    valueAge: Optional[Age] = None
    valueAnnotation: Optional[Annotation] = None
    valueAttachment: Optional[Attachment] = None
    valueCodeableConcept: Optional[CodeableConcept] = None
    valueCoding: Optional[Coding] = None
    valueContactPoint: Optional[ContactPoint] = None
    valueCount: Optional[Count] = None
    valueDistance: Optional[Distance] = None
    valueDuration: Optional[Duration] = None
    valueHumanName: Optional[HumanName] = None
    valueIdentifier: Optional[Identifier] = None
    valueMoney: Optional[Money] = None
    valuePeriod: Optional[Period] = None
    valueQuantity: Optional[Quantity] = None
    valueRange: Optional[Range] = None
    valueRatio: Optional[Ratio] = None
    valueReference: Optional[Reference] = None
    valueSampledData: Optional[SampledData] = None
    valueSignature: Optional[Signature] = None
    valueTiming: Optional[Timing] = None
    valueContactDetail: Optional[ContactDetail] = None
    valueContributor: Optional[Contributor] = None
    valueDataRequirement: Optional[DataRequirement] = None
    valueExpression: Optional[Expression] = None
    valueParameterDefinition: Optional[ParameterDefinition] = None
    valueRelatedArtifact: Optional[RelatedArtifact] = None
    valueTriggerDefinition: Optional[TriggerDefinition] = None
    valueUsageContext: Optional[UsageContext] = None
    valueDosage: Optional[Dosage] = None
    valueMeta: Optional[Meta] = None


class language(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueCode']}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None
    valueCode: Optional[Code] = None


class maxDecimalPlaces(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueInteger']}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None
    valueInteger: Optional[Integer] = None


class maxSize(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueDecimal']}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None
    valueDecimal: Optional[Decimal] = None


class maxValue(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueDate', 'valueDateTime', 'valueTime', 'valueInstant', 'valueDecimal', 'valueInteger']}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None
    valueDate: Optional[Date] = None
    valueDateTime: Optional[DateTime] = None
    valueTime: Optional[Time] = None
    valueInstant: Optional[Instant] = None
    valueDecimal: Optional[Decimal] = None
    valueInteger: Optional[Integer] = None


class mimeType(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueCode']}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None
    valueCode: Optional[Code] = None


class minLength(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueInteger']}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None
    valueInteger: Optional[Integer] = None


class minValue(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueDate', 'valueDateTime', 'valueTime', 'valueDecimal', 'valueInteger']}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None
    valueDate: Optional[Date] = None
    valueDateTime: Optional[DateTime] = None
    valueTime: Optional[Time] = None
    valueDecimal: Optional[Decimal] = None
    valueInteger: Optional[Integer] = None


class narrativeLink(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueUrl']}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None
    valueUrl: Optional[Url] = None


class ordinalValue(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueDecimal']}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None
    valueDecimal: Optional[Decimal] = None


class originalText(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueString']}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None
    valueString: Optional[String] = None


class regex(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueString']}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None
    valueString: Optional[String] = None


class replaces(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueCanonical']}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None
    valueCanonical: Optional[Canonical] = None


class translation(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'extension': 'Extension', 'extension': 'Extension', 'valueAddress': 'Address', 'valueAge': 'Age', 'valueAnnotation': 'Annotation', 'valueAttachment': 'Attachment', 'valueCodeableConcept': 'CodeableConcept', 'valueCoding': 'Coding', 'valueContactPoint': 'ContactPoint', 'valueCount': 'Count', 'valueDistance': 'Distance', 'valueDuration': 'Duration', 'valueHumanName': 'HumanName', 'valueIdentifier': 'Identifier', 'valueMoney': 'Money', 'valuePeriod': 'Period', 'valueQuantity': 'Quantity', 'valueRange': 'Range', 'valueRatio': 'Ratio', 'valueReference': 'Reference', 'valueSampledData': 'SampledData', 'valueSignature': 'Signature', 'valueTiming': 'Timing', 'valueContactDetail': 'ContactDetail', 'valueContributor': 'Contributor', 'valueDataRequirement': 'DataRequirement', 'valueExpression': 'Expression', 'valueParameterDefinition': 'ParameterDefinition', 'valueRelatedArtifact': 'RelatedArtifact', 'valueTriggerDefinition': 'TriggerDefinition', 'valueUsageContext': 'UsageContext', 'valueDosage': 'Dosage', 'valueMeta': 'Meta'}
    _choice_fields = {'value': ['valueBase64Binary', 'valueBoolean', 'valueCanonical', 'valueCode', 'valueDate', 'valueDateTime', 'valueDecimal', 'valueId', 'valueInstant', 'valueInteger', 'valueMarkdown', 'valueOid', 'valuePositiveInt', 'valueString', 'valueTime', 'valueUnsignedInt', 'valueUri', 'valueUrl', 'valueUuid', 'valueAddress', 'valueAge', 'valueAnnotation', 'valueAttachment', 'valueCodeableConcept', 'valueCoding', 'valueContactPoint', 'valueCount', 'valueDistance', 'valueDuration', 'valueHumanName', 'valueIdentifier', 'valueMoney', 'valuePeriod', 'valueQuantity', 'valueRange', 'valueRatio', 'valueReference', 'valueSampledData', 'valueSignature', 'valueTiming', 'valueContactDetail', 'valueContributor', 'valueDataRequirement', 'valueExpression', 'valueParameterDefinition', 'valueRelatedArtifact', 'valueTriggerDefinition', 'valueUsageContext', 'valueDosage', 'valueMeta']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    extension: Optional[Extension]
    extension: Optional[Extension]
    url: Optional[str] = None
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
    valueAddress: Optional[Address] = None
    valueAge: Optional[Age] = None
    valueAnnotation: Optional[Annotation] = None
    valueAttachment: Optional[Attachment] = None
    valueCodeableConcept: Optional[CodeableConcept] = None
    valueCoding: Optional[Coding] = None
    valueContactPoint: Optional[ContactPoint] = None
    valueCount: Optional[Count] = None
    valueDistance: Optional[Distance] = None
    valueDuration: Optional[Duration] = None
    valueHumanName: Optional[HumanName] = None
    valueIdentifier: Optional[Identifier] = None
    valueMoney: Optional[Money] = None
    valuePeriod: Optional[Period] = None
    valueQuantity: Optional[Quantity] = None
    valueRange: Optional[Range] = None
    valueRatio: Optional[Ratio] = None
    valueReference: Optional[Reference] = None
    valueSampledData: Optional[SampledData] = None
    valueSignature: Optional[Signature] = None
    valueTiming: Optional[Timing] = None
    valueContactDetail: Optional[ContactDetail] = None
    valueContributor: Optional[Contributor] = None
    valueDataRequirement: Optional[DataRequirement] = None
    valueExpression: Optional[Expression] = None
    valueParameterDefinition: Optional[ParameterDefinition] = None
    valueRelatedArtifact: Optional[RelatedArtifact] = None
    valueTriggerDefinition: Optional[TriggerDefinition] = None
    valueUsageContext: Optional[UsageContext] = None
    valueDosage: Optional[Dosage] = None
    valueMeta: Optional[Meta] = None


class variable(FHIRElement):
    _field_types = {'extension': 'Extension', 'valueExpression': 'Expression'}
    _choice_fields = {'value': ['valueExpression']}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None
    valueExpression: Optional[Expression] = None
