from __future__ import annotations

from typing import Optional

from zato.fhir.base import FHIRElement, FHIRList
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
    Xhtml,
)


class Element(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict


class BackboneElement(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict


class Address(FHIRElement):
    _list_fields = {'extension', 'line'}
    _field_types = {'extension': 'Extension', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    use: Optional[Code] = None
    type_: Optional[Code] = None
    text: Optional[String] = None
    line: String | FHIRList[String] | list | None = None
    city: Optional[String] = None
    district: Optional[String] = None
    state: Optional[String] = None
    postalCode: Optional[String] = None
    country: Optional[String] = None
    period: Period | dict | None


class Age(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
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
    extension: Extension | FHIRList[Extension] | list | dict
    authorReference: Reference | dict | None = None
    authorString: Optional[String] = None
    time: Optional[DateTime] = None
    text: Optional[Markdown] = None


class Attachment(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
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
    extension: Extension | FHIRList[Extension] | list | dict
    coding: Coding | FHIRList[Coding] | list | dict
    text: Optional[String] = None


class Coding(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Uri] = None
    version: Optional[String] = None
    code: Optional[Code] = None
    display: Optional[String] = None
    userSelected: Optional[Boolean] = None


class ContactDetail(FHIRElement):
    _list_fields = {'extension', 'telecom'}
    _field_types = {'extension': 'Extension', 'telecom': 'ContactPoint'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    name: Optional[String] = None
    telecom: ContactPoint | FHIRList[ContactPoint] | list | dict


class ContactPoint(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    system: Optional[Code] = None
    value: Optional[String] = None
    use: Optional[Code] = None
    rank: Optional[PositiveInt] = None
    period: Period | dict | None


class Contributor(FHIRElement):
    _list_fields = {'extension', 'contact'}
    _field_types = {'extension': 'Extension', 'contact': 'ContactDetail'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    name: Optional[String] = None
    contact: ContactDetail | FHIRList[ContactDetail] | list | dict


class Count(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class DataRequirement(FHIRElement):
    _list_fields = {'extension', 'profile', 'mustSupport', 'codeFilter', 'dateFilter', 'sort'}
    _field_types = {
        'extension': 'Extension',
        'subjectCodeableConcept': 'CodeableConcept',
        'subjectReference': 'Reference',
        'codeFilter': 'Element',
        'dateFilter': 'Element',
        'sort': 'Element',
    }
    _choice_fields = {'subject': ['subjectCodeableConcept', 'subjectReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    profile: Canonical | FHIRList[Canonical] | list | None = None
    subjectCodeableConcept: CodeableConcept | dict | None = None
    subjectReference: Reference | dict | None = None
    mustSupport: String | FHIRList[String] | list | None = None
    codeFilter: Element | FHIRList[Element] | list | dict
    dateFilter: Element | FHIRList[Element] | list | dict
    limit: Optional[PositiveInt] = None
    sort: Element | FHIRList[Element] | list | dict


class Distance(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class Dosage(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'additionalInstruction', 'doseAndRate'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'additionalInstruction': 'CodeableConcept',
        'timing': 'Timing',
        'asNeededCodeableConcept': 'CodeableConcept',
        'site': 'CodeableConcept',
        'route': 'CodeableConcept',
        'method': 'CodeableConcept',
        'doseAndRate': 'Element',
        'maxDosePerPeriod': 'Ratio',
        'maxDosePerAdministration': 'Quantity',
        'maxDosePerLifetime': 'Quantity',
    }
    _choice_fields = {'asNeeded': ['asNeededBoolean', 'asNeededCodeableConcept']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    sequence: Optional[Integer] = None
    text: Optional[String] = None
    additionalInstruction: CodeableConcept | FHIRList[CodeableConcept] | list | dict
    patientInstruction: Optional[String] = None
    timing: Timing | dict | None
    asNeededBoolean: Optional[Boolean] = None
    asNeededCodeableConcept: CodeableConcept | dict | None = None
    site: CodeableConcept | dict | None
    route: CodeableConcept | dict | None
    method: CodeableConcept | dict | None
    doseAndRate: Element | FHIRList[Element] | list | dict
    maxDosePerPeriod: Ratio | dict | None
    maxDosePerAdministration: Quantity | dict | None
    maxDosePerLifetime: Quantity | dict | None


class Duration(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class ElementDefinition(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'representation', 'code', 'alias', 'type_', 'example', 'condition', 'constraint', 'mapping'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'code': 'Coding',
        'slicing': 'Element',
        'base': 'Element',
        'type_': 'Element',
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
        'fixedAddress': 'Address',
        'fixedAge': 'Age',
        'fixedAnnotation': 'Annotation',
        'fixedAttachment': 'Attachment',
        'fixedCodeableConcept': 'CodeableConcept',
        'fixedCoding': 'Coding',
        'fixedContactPoint': 'ContactPoint',
        'fixedCount': 'Count',
        'fixedDistance': 'Distance',
        'fixedDuration': 'Duration',
        'fixedHumanName': 'HumanName',
        'fixedIdentifier': 'Identifier',
        'fixedMoney': 'Money',
        'fixedPeriod': 'Period',
        'fixedQuantity': 'Quantity',
        'fixedRange': 'Range',
        'fixedRatio': 'Ratio',
        'fixedReference': 'Reference',
        'fixedSampledData': 'SampledData',
        'fixedSignature': 'Signature',
        'fixedTiming': 'Timing',
        'fixedContactDetail': 'ContactDetail',
        'fixedContributor': 'Contributor',
        'fixedDataRequirement': 'DataRequirement',
        'fixedExpression': 'Expression',
        'fixedParameterDefinition': 'ParameterDefinition',
        'fixedRelatedArtifact': 'RelatedArtifact',
        'fixedTriggerDefinition': 'TriggerDefinition',
        'fixedUsageContext': 'UsageContext',
        'fixedDosage': 'Dosage',
        'fixedMeta': 'Meta',
        'patternAddress': 'Address',
        'patternAge': 'Age',
        'patternAnnotation': 'Annotation',
        'patternAttachment': 'Attachment',
        'patternCodeableConcept': 'CodeableConcept',
        'patternCoding': 'Coding',
        'patternContactPoint': 'ContactPoint',
        'patternCount': 'Count',
        'patternDistance': 'Distance',
        'patternDuration': 'Duration',
        'patternHumanName': 'HumanName',
        'patternIdentifier': 'Identifier',
        'patternMoney': 'Money',
        'patternPeriod': 'Period',
        'patternQuantity': 'Quantity',
        'patternRange': 'Range',
        'patternRatio': 'Ratio',
        'patternReference': 'Reference',
        'patternSampledData': 'SampledData',
        'patternSignature': 'Signature',
        'patternTiming': 'Timing',
        'patternContactDetail': 'ContactDetail',
        'patternContributor': 'Contributor',
        'patternDataRequirement': 'DataRequirement',
        'patternExpression': 'Expression',
        'patternParameterDefinition': 'ParameterDefinition',
        'patternRelatedArtifact': 'RelatedArtifact',
        'patternTriggerDefinition': 'TriggerDefinition',
        'patternUsageContext': 'UsageContext',
        'patternDosage': 'Dosage',
        'patternMeta': 'Meta',
        'example': 'Element',
        'minValueQuantity': 'Quantity',
        'maxValueQuantity': 'Quantity',
        'constraint': 'Element',
        'binding': 'Element',
        'mapping': 'Element',
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
        'fixed': [
            'fixedBase64Binary',
            'fixedBoolean',
            'fixedCanonical',
            'fixedCode',
            'fixedDate',
            'fixedDateTime',
            'fixedDecimal',
            'fixedId',
            'fixedInstant',
            'fixedInteger',
            'fixedMarkdown',
            'fixedOid',
            'fixedPositiveInt',
            'fixedString',
            'fixedTime',
            'fixedUnsignedInt',
            'fixedUri',
            'fixedUrl',
            'fixedUuid',
            'fixedAddress',
            'fixedAge',
            'fixedAnnotation',
            'fixedAttachment',
            'fixedCodeableConcept',
            'fixedCoding',
            'fixedContactPoint',
            'fixedCount',
            'fixedDistance',
            'fixedDuration',
            'fixedHumanName',
            'fixedIdentifier',
            'fixedMoney',
            'fixedPeriod',
            'fixedQuantity',
            'fixedRange',
            'fixedRatio',
            'fixedReference',
            'fixedSampledData',
            'fixedSignature',
            'fixedTiming',
            'fixedContactDetail',
            'fixedContributor',
            'fixedDataRequirement',
            'fixedExpression',
            'fixedParameterDefinition',
            'fixedRelatedArtifact',
            'fixedTriggerDefinition',
            'fixedUsageContext',
            'fixedDosage',
            'fixedMeta',
        ],
        'maxValue': [
            'maxValueDate',
            'maxValueDateTime',
            'maxValueInstant',
            'maxValueTime',
            'maxValueDecimal',
            'maxValueInteger',
            'maxValuePositiveInt',
            'maxValueUnsignedInt',
            'maxValueQuantity',
        ],
        'minValue': [
            'minValueDate',
            'minValueDateTime',
            'minValueInstant',
            'minValueTime',
            'minValueDecimal',
            'minValueInteger',
            'minValuePositiveInt',
            'minValueUnsignedInt',
            'minValueQuantity',
        ],
        'pattern': [
            'patternBase64Binary',
            'patternBoolean',
            'patternCanonical',
            'patternCode',
            'patternDate',
            'patternDateTime',
            'patternDecimal',
            'patternId',
            'patternInstant',
            'patternInteger',
            'patternMarkdown',
            'patternOid',
            'patternPositiveInt',
            'patternString',
            'patternTime',
            'patternUnsignedInt',
            'patternUri',
            'patternUrl',
            'patternUuid',
            'patternAddress',
            'patternAge',
            'patternAnnotation',
            'patternAttachment',
            'patternCodeableConcept',
            'patternCoding',
            'patternContactPoint',
            'patternCount',
            'patternDistance',
            'patternDuration',
            'patternHumanName',
            'patternIdentifier',
            'patternMoney',
            'patternPeriod',
            'patternQuantity',
            'patternRange',
            'patternRatio',
            'patternReference',
            'patternSampledData',
            'patternSignature',
            'patternTiming',
            'patternContactDetail',
            'patternContributor',
            'patternDataRequirement',
            'patternExpression',
            'patternParameterDefinition',
            'patternRelatedArtifact',
            'patternTriggerDefinition',
            'patternUsageContext',
            'patternDosage',
            'patternMeta',
        ],
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    path: Optional[String] = None
    representation: Code | FHIRList[Code] | list | None = None
    sliceName: Optional[String] = None
    sliceIsConstraining: Optional[Boolean] = None
    label: Optional[String] = None
    code: Coding | FHIRList[Coding] | list | dict
    slicing: Element | dict | None
    short: Optional[String] = None
    definition: Optional[Markdown] = None
    comment: Optional[Markdown] = None
    requirements: Optional[Markdown] = None
    alias: String | FHIRList[String] | list | None = None
    min: Optional[UnsignedInt] = None
    max: Optional[String] = None
    base: Element | dict | None
    contentReference: Optional[Uri] = None
    type_: Element | FHIRList[Element] | list | dict
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
    defaultValueAddress: Address | dict | None = None
    defaultValueAge: Age | dict | None = None
    defaultValueAnnotation: Annotation | dict | None = None
    defaultValueAttachment: Attachment | dict | None = None
    defaultValueCodeableConcept: CodeableConcept | dict | None = None
    defaultValueCoding: Coding | dict | None = None
    defaultValueContactPoint: ContactPoint | dict | None = None
    defaultValueCount: Count | dict | None = None
    defaultValueDistance: Distance | dict | None = None
    defaultValueDuration: Duration | dict | None = None
    defaultValueHumanName: HumanName | dict | None = None
    defaultValueIdentifier: Identifier | dict | None = None
    defaultValueMoney: Money | dict | None = None
    defaultValuePeriod: Period | dict | None = None
    defaultValueQuantity: Quantity | dict | None = None
    defaultValueRange: Range | dict | None = None
    defaultValueRatio: Ratio | dict | None = None
    defaultValueReference: Reference | dict | None = None
    defaultValueSampledData: SampledData | dict | None = None
    defaultValueSignature: Signature | dict | None = None
    defaultValueTiming: Timing | dict | None = None
    defaultValueContactDetail: ContactDetail | dict | None = None
    defaultValueContributor: Contributor | dict | None = None
    defaultValueDataRequirement: DataRequirement | dict | None = None
    defaultValueExpression: Expression | dict | None = None
    defaultValueParameterDefinition: ParameterDefinition | dict | None = None
    defaultValueRelatedArtifact: RelatedArtifact | dict | None = None
    defaultValueTriggerDefinition: TriggerDefinition | dict | None = None
    defaultValueUsageContext: UsageContext | dict | None = None
    defaultValueDosage: Dosage | dict | None = None
    defaultValueMeta: Meta | dict | None = None
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
    fixedAddress: Address | dict | None = None
    fixedAge: Age | dict | None = None
    fixedAnnotation: Annotation | dict | None = None
    fixedAttachment: Attachment | dict | None = None
    fixedCodeableConcept: CodeableConcept | dict | None = None
    fixedCoding: Coding | dict | None = None
    fixedContactPoint: ContactPoint | dict | None = None
    fixedCount: Count | dict | None = None
    fixedDistance: Distance | dict | None = None
    fixedDuration: Duration | dict | None = None
    fixedHumanName: HumanName | dict | None = None
    fixedIdentifier: Identifier | dict | None = None
    fixedMoney: Money | dict | None = None
    fixedPeriod: Period | dict | None = None
    fixedQuantity: Quantity | dict | None = None
    fixedRange: Range | dict | None = None
    fixedRatio: Ratio | dict | None = None
    fixedReference: Reference | dict | None = None
    fixedSampledData: SampledData | dict | None = None
    fixedSignature: Signature | dict | None = None
    fixedTiming: Timing | dict | None = None
    fixedContactDetail: ContactDetail | dict | None = None
    fixedContributor: Contributor | dict | None = None
    fixedDataRequirement: DataRequirement | dict | None = None
    fixedExpression: Expression | dict | None = None
    fixedParameterDefinition: ParameterDefinition | dict | None = None
    fixedRelatedArtifact: RelatedArtifact | dict | None = None
    fixedTriggerDefinition: TriggerDefinition | dict | None = None
    fixedUsageContext: UsageContext | dict | None = None
    fixedDosage: Dosage | dict | None = None
    fixedMeta: Meta | dict | None = None
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
    patternAddress: Address | dict | None = None
    patternAge: Age | dict | None = None
    patternAnnotation: Annotation | dict | None = None
    patternAttachment: Attachment | dict | None = None
    patternCodeableConcept: CodeableConcept | dict | None = None
    patternCoding: Coding | dict | None = None
    patternContactPoint: ContactPoint | dict | None = None
    patternCount: Count | dict | None = None
    patternDistance: Distance | dict | None = None
    patternDuration: Duration | dict | None = None
    patternHumanName: HumanName | dict | None = None
    patternIdentifier: Identifier | dict | None = None
    patternMoney: Money | dict | None = None
    patternPeriod: Period | dict | None = None
    patternQuantity: Quantity | dict | None = None
    patternRange: Range | dict | None = None
    patternRatio: Ratio | dict | None = None
    patternReference: Reference | dict | None = None
    patternSampledData: SampledData | dict | None = None
    patternSignature: Signature | dict | None = None
    patternTiming: Timing | dict | None = None
    patternContactDetail: ContactDetail | dict | None = None
    patternContributor: Contributor | dict | None = None
    patternDataRequirement: DataRequirement | dict | None = None
    patternExpression: Expression | dict | None = None
    patternParameterDefinition: ParameterDefinition | dict | None = None
    patternRelatedArtifact: RelatedArtifact | dict | None = None
    patternTriggerDefinition: TriggerDefinition | dict | None = None
    patternUsageContext: UsageContext | dict | None = None
    patternDosage: Dosage | dict | None = None
    patternMeta: Meta | dict | None = None
    example: Element | FHIRList[Element] | list | dict
    minValueDate: Optional[Date] = None
    minValueDateTime: Optional[DateTime] = None
    minValueInstant: Optional[Instant] = None
    minValueTime: Optional[Time] = None
    minValueDecimal: Optional[Decimal] = None
    minValueInteger: Optional[Integer] = None
    minValuePositiveInt: Optional[PositiveInt] = None
    minValueUnsignedInt: Optional[UnsignedInt] = None
    minValueQuantity: Quantity | dict | None = None
    maxValueDate: Optional[Date] = None
    maxValueDateTime: Optional[DateTime] = None
    maxValueInstant: Optional[Instant] = None
    maxValueTime: Optional[Time] = None
    maxValueDecimal: Optional[Decimal] = None
    maxValueInteger: Optional[Integer] = None
    maxValuePositiveInt: Optional[PositiveInt] = None
    maxValueUnsignedInt: Optional[UnsignedInt] = None
    maxValueQuantity: Quantity | dict | None = None
    maxLength: Optional[Integer] = None
    condition: Id | FHIRList[Id] | list | None = None
    constraint: Element | FHIRList[Element] | list | dict
    mustSupport: Optional[Boolean] = None
    isModifier: Optional[Boolean] = None
    isModifierReason: Optional[String] = None
    isSummary: Optional[Boolean] = None
    binding: Element | dict | None
    mapping: Element | FHIRList[Element] | list | dict


class Expression(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    description: Optional[String] = None
    name: Optional[Id] = None
    language: Optional[Code] = None
    expression: Optional[String] = None
    reference: Optional[Uri] = None


class Extension(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {
        'extension': 'Extension',
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
    valueAddress: Address | dict | None = None
    valueAge: Age | dict | None = None
    valueAnnotation: Annotation | dict | None = None
    valueAttachment: Attachment | dict | None = None
    valueCodeableConcept: CodeableConcept | dict | None = None
    valueCoding: Coding | dict | None = None
    valueContactPoint: ContactPoint | dict | None = None
    valueCount: Count | dict | None = None
    valueDistance: Distance | dict | None = None
    valueDuration: Duration | dict | None = None
    valueHumanName: HumanName | dict | None = None
    valueIdentifier: Identifier | dict | None = None
    valueMoney: Money | dict | None = None
    valuePeriod: Period | dict | None = None
    valueQuantity: Quantity | dict | None = None
    valueRange: Range | dict | None = None
    valueRatio: Ratio | dict | None = None
    valueReference: Reference | dict | None = None
    valueSampledData: SampledData | dict | None = None
    valueSignature: Signature | dict | None = None
    valueTiming: Timing | dict | None = None
    valueContactDetail: ContactDetail | dict | None = None
    valueContributor: Contributor | dict | None = None
    valueDataRequirement: DataRequirement | dict | None = None
    valueExpression: Expression | dict | None = None
    valueParameterDefinition: ParameterDefinition | dict | None = None
    valueRelatedArtifact: RelatedArtifact | dict | None = None
    valueTriggerDefinition: TriggerDefinition | dict | None = None
    valueUsageContext: UsageContext | dict | None = None
    valueDosage: Dosage | dict | None = None
    valueMeta: Meta | dict | None = None


class HumanName(FHIRElement):
    _list_fields = {'extension', 'given', 'prefix', 'suffix'}
    _field_types = {'extension': 'Extension', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    use: Optional[Code] = None
    text: Optional[String] = None
    family: Optional[String] = None
    given: String | FHIRList[String] | list | None = None
    prefix: String | FHIRList[String] | list | None = None
    suffix: String | FHIRList[String] | list | None = None
    period: Period | dict | None


class Identifier(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'type_': 'CodeableConcept', 'period': 'Period', 'assigner': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    use: Optional[Code] = None
    type_: CodeableConcept | dict | None
    system: Optional[Uri] = None
    value: Optional[String] = None
    period: Period | dict | None
    assigner: Reference | dict | None


class MarketingStatus(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'country': 'CodeableConcept',
        'jurisdiction': 'CodeableConcept',
        'status': 'CodeableConcept',
        'dateRange': 'Period',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    country: CodeableConcept | dict | None
    jurisdiction: CodeableConcept | dict | None
    status: CodeableConcept | dict | None
    dateRange: Period | dict | None
    restoreDate: Optional[DateTime] = None


class Meta(FHIRElement):
    _list_fields = {'extension', 'profile', 'security', 'tag'}
    _field_types = {'extension': 'Extension', 'security': 'Coding', 'tag': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    versionId: Optional[Id] = None
    lastUpdated: Optional[Instant] = None
    source: Optional[Uri] = None
    profile: Canonical | FHIRList[Canonical] | list | None = None
    security: Coding | FHIRList[Coding] | list | dict
    tag: Coding | FHIRList[Coding] | list | dict


class Money(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    value: Optional[Decimal] = None
    currency: Optional[Code] = None


class MoneyQuantity(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class Narrative(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    status: Optional[Code] = None
    div: Optional[Xhtml] = None


class ParameterDefinition(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
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
    extension: Extension | FHIRList[Extension] | list | dict
    start: Optional[DateTime] = None
    end: Optional[DateTime] = None


class Population(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'ageRange': 'Range',
        'ageCodeableConcept': 'CodeableConcept',
        'gender': 'CodeableConcept',
        'race': 'CodeableConcept',
        'physiologicalCondition': 'CodeableConcept',
    }
    _choice_fields = {'age': ['ageRange', 'ageCodeableConcept']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    ageRange: Range | dict | None = None
    ageCodeableConcept: CodeableConcept | dict | None = None
    gender: CodeableConcept | dict | None
    race: CodeableConcept | dict | None
    physiologicalCondition: CodeableConcept | dict | None


class ProdCharacteristic(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'color', 'imprint', 'image'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'height': 'Quantity',
        'width': 'Quantity',
        'depth': 'Quantity',
        'weight': 'Quantity',
        'nominalVolume': 'Quantity',
        'externalDiameter': 'Quantity',
        'image': 'Attachment',
        'scoring': 'CodeableConcept',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    height: Quantity | dict | None
    width: Quantity | dict | None
    depth: Quantity | dict | None
    weight: Quantity | dict | None
    nominalVolume: Quantity | dict | None
    externalDiameter: Quantity | dict | None
    shape: Optional[String] = None
    color: String | FHIRList[String] | list | None = None
    imprint: String | FHIRList[String] | list | None = None
    image: Attachment | FHIRList[Attachment] | list | dict
    scoring: CodeableConcept | dict | None


class ProductShelfLife(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'specialPrecautionsForStorage'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'identifier': 'Identifier',
        'type_': 'CodeableConcept',
        'period': 'Quantity',
        'specialPrecautionsForStorage': 'CodeableConcept',
    }

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    identifier: Identifier | dict | None
    type_: CodeableConcept | dict | None
    period: Quantity | dict | None
    specialPrecautionsForStorage: CodeableConcept | FHIRList[CodeableConcept] | list | dict


class Quantity(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class Range(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'low': 'Quantity', 'high': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    low: Quantity | dict | None
    high: Quantity | dict | None


class Ratio(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'numerator': 'Quantity', 'denominator': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    numerator: Quantity | dict | None
    denominator: Quantity | dict | None


class Reference(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'identifier': 'Identifier'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    reference: Optional[String] = None
    type_: Optional[Uri] = None
    identifier: Identifier | dict | None
    display: Optional[String] = None


class RelatedArtifact(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'document': 'Attachment'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    label: Optional[String] = None
    display: Optional[String] = None
    citation: Optional[Markdown] = None
    url: Optional[Url] = None
    document: Attachment | dict | None
    resource: Optional[Canonical] = None


class SampledData(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'origin': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    origin: Quantity | dict | None
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
    extension: Extension | FHIRList[Extension] | list | dict
    type_: Coding | FHIRList[Coding] | list | dict
    when: Optional[Instant] = None
    who: Reference | dict | None
    onBehalfOf: Reference | dict | None
    targetFormat: Optional[Code] = None
    sigFormat: Optional[Code] = None
    data: Optional[Base64Binary] = None


class SimpleQuantity(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    value: Optional[Decimal] = None
    comparator: Optional[Code] = None
    unit: Optional[String] = None
    system: Optional[Uri] = None
    code: Optional[Code] = None


class SubstanceAmount(FHIRElement):
    _list_fields = {'extension', 'modifierExtension'}
    _field_types = {
        'extension': 'Extension',
        'modifierExtension': 'Extension',
        'amountQuantity': 'Quantity',
        'amountRange': 'Range',
        'amountType': 'CodeableConcept',
        'referenceRange': 'Element',
    }
    _choice_fields = {'amount': ['amountQuantity', 'amountRange', 'amountString']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    amountQuantity: Quantity | dict | None = None
    amountRange: Range | dict | None = None
    amountString: Optional[String] = None
    amountType: CodeableConcept | dict | None
    amountText: Optional[String] = None
    referenceRange: Element | dict | None


class Timing(FHIRElement):
    _list_fields = {'extension', 'modifierExtension', 'event'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'repeat': 'Element', 'code': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    modifierExtension: Extension | FHIRList[Extension] | list | dict
    event: DateTime | FHIRList[DateTime] | list | None = None
    repeat: Element | dict | None
    code: CodeableConcept | dict | None


class TriggerDefinition(FHIRElement):
    _list_fields = {'extension', 'data'}
    _field_types = {'extension': 'Extension', 'timingTiming': 'Timing', 'timingReference': 'Reference', 'data': 'DataRequirement', 'condition': 'Expression'}
    _choice_fields = {'timing': ['timingTiming', 'timingReference', 'timingDate', 'timingDateTime']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    type_: Optional[Code] = None
    name: Optional[String] = None
    timingTiming: Timing | dict | None = None
    timingReference: Reference | dict | None = None
    timingDate: Optional[Date] = None
    timingDateTime: Optional[DateTime] = None
    data: DataRequirement | FHIRList[DataRequirement] | list | dict
    condition: Expression | dict | None


class UsageContext(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {
        'extension': 'Extension',
        'code': 'Coding',
        'valueCodeableConcept': 'CodeableConcept',
        'valueQuantity': 'Quantity',
        'valueRange': 'Range',
        'valueReference': 'Reference',
    }
    _choice_fields = {'value': ['valueCodeableConcept', 'valueQuantity', 'valueRange', 'valueReference']}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension] | list | dict
    code: Coding | dict | None
    valueCodeableConcept: CodeableConcept | dict | None = None
    valueQuantity: Quantity | dict | None = None
    valueRange: Range | dict | None = None
    valueReference: Reference | dict | None = None


class bodySite(FHIRElement):
    _field_types = {'extension': 'Extension', 'valueReference': 'Reference'}
    _choice_fields = {'value': ['valueReference']}

    id: Optional[str] = None
    extension: Extension | dict | None
    url: Optional[str] = None
    valueReference: Reference | dict | None = None


class capabilities(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueCode']}

    id: Optional[str] = None
    extension: Extension | dict | None
    url: Optional[str] = None
    valueCode: Optional[Code] = None


class designNote(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueMarkdown']}

    id: Optional[str] = None
    extension: Extension | dict | None
    url: Optional[str] = None
    valueMarkdown: Optional[Markdown] = None


class display(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueString']}

    id: Optional[str] = None
    extension: Extension | dict | None
    url: Optional[str] = None
    valueString: Optional[String] = None


class entryFormat(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueString']}

    id: Optional[str] = None
    extension: Extension | dict | None
    url: Optional[str] = None
    valueString: Optional[String] = None


class geolocation(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {
        'extension': 'Extension',
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
    valueAddress: Address | dict | None = None
    valueAge: Age | dict | None = None
    valueAnnotation: Annotation | dict | None = None
    valueAttachment: Attachment | dict | None = None
    valueCodeableConcept: CodeableConcept | dict | None = None
    valueCoding: Coding | dict | None = None
    valueContactPoint: ContactPoint | dict | None = None
    valueCount: Count | dict | None = None
    valueDistance: Distance | dict | None = None
    valueDuration: Duration | dict | None = None
    valueHumanName: HumanName | dict | None = None
    valueIdentifier: Identifier | dict | None = None
    valueMoney: Money | dict | None = None
    valuePeriod: Period | dict | None = None
    valueQuantity: Quantity | dict | None = None
    valueRange: Range | dict | None = None
    valueRatio: Ratio | dict | None = None
    valueReference: Reference | dict | None = None
    valueSampledData: SampledData | dict | None = None
    valueSignature: Signature | dict | None = None
    valueTiming: Timing | dict | None = None
    valueContactDetail: ContactDetail | dict | None = None
    valueContributor: Contributor | dict | None = None
    valueDataRequirement: DataRequirement | dict | None = None
    valueExpression: Expression | dict | None = None
    valueParameterDefinition: ParameterDefinition | dict | None = None
    valueRelatedArtifact: RelatedArtifact | dict | None = None
    valueTriggerDefinition: TriggerDefinition | dict | None = None
    valueUsageContext: UsageContext | dict | None = None
    valueDosage: Dosage | dict | None = None
    valueMeta: Meta | dict | None = None


class language(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueCode']}

    id: Optional[str] = None
    extension: Extension | dict | None
    url: Optional[str] = None
    valueCode: Optional[Code] = None


class maxDecimalPlaces(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueInteger']}

    id: Optional[str] = None
    extension: Extension | dict | None
    url: Optional[str] = None
    valueInteger: Optional[Integer] = None


class maxSize(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueDecimal']}

    id: Optional[str] = None
    extension: Extension | dict | None
    url: Optional[str] = None
    valueDecimal: Optional[Decimal] = None


class maxValue(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueDate', 'valueDateTime', 'valueTime', 'valueInstant', 'valueDecimal', 'valueInteger']}

    id: Optional[str] = None
    extension: Extension | dict | None
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
    extension: Extension | dict | None
    url: Optional[str] = None
    valueCode: Optional[Code] = None


class minLength(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueInteger']}

    id: Optional[str] = None
    extension: Extension | dict | None
    url: Optional[str] = None
    valueInteger: Optional[Integer] = None


class minValue(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueDate', 'valueDateTime', 'valueTime', 'valueDecimal', 'valueInteger']}

    id: Optional[str] = None
    extension: Extension | dict | None
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
    extension: Extension | dict | None
    url: Optional[str] = None
    valueUrl: Optional[Url] = None


class ordinalValue(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueDecimal']}

    id: Optional[str] = None
    extension: Extension | dict | None
    url: Optional[str] = None
    valueDecimal: Optional[Decimal] = None


class originalText(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueString']}

    id: Optional[str] = None
    extension: Extension | dict | None
    url: Optional[str] = None
    valueString: Optional[String] = None


class regex(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueString']}

    id: Optional[str] = None
    extension: Extension | dict | None
    url: Optional[str] = None
    valueString: Optional[String] = None


class replaces(FHIRElement):
    _field_types = {'extension': 'Extension'}
    _choice_fields = {'value': ['valueCanonical']}

    id: Optional[str] = None
    extension: Extension | dict | None
    url: Optional[str] = None
    valueCanonical: Optional[Canonical] = None


class translation(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {
        'extension': 'Extension',
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
    valueAddress: Address | dict | None = None
    valueAge: Age | dict | None = None
    valueAnnotation: Annotation | dict | None = None
    valueAttachment: Attachment | dict | None = None
    valueCodeableConcept: CodeableConcept | dict | None = None
    valueCoding: Coding | dict | None = None
    valueContactPoint: ContactPoint | dict | None = None
    valueCount: Count | dict | None = None
    valueDistance: Distance | dict | None = None
    valueDuration: Duration | dict | None = None
    valueHumanName: HumanName | dict | None = None
    valueIdentifier: Identifier | dict | None = None
    valueMoney: Money | dict | None = None
    valuePeriod: Period | dict | None = None
    valueQuantity: Quantity | dict | None = None
    valueRange: Range | dict | None = None
    valueRatio: Ratio | dict | None = None
    valueReference: Reference | dict | None = None
    valueSampledData: SampledData | dict | None = None
    valueSignature: Signature | dict | None = None
    valueTiming: Timing | dict | None = None
    valueContactDetail: ContactDetail | dict | None = None
    valueContributor: Contributor | dict | None = None
    valueDataRequirement: DataRequirement | dict | None = None
    valueExpression: Expression | dict | None = None
    valueParameterDefinition: ParameterDefinition | dict | None = None
    valueRelatedArtifact: RelatedArtifact | dict | None = None
    valueTriggerDefinition: TriggerDefinition | dict | None = None
    valueUsageContext: UsageContext | dict | None = None
    valueDosage: Dosage | dict | None = None
    valueMeta: Meta | dict | None = None


class variable(FHIRElement):
    _field_types = {'extension': 'Extension', 'valueExpression': 'Expression'}
    _choice_fields = {'value': ['valueExpression']}

    id: Optional[str] = None
    extension: Extension | dict | None
    url: Optional[str] = None
    valueExpression: Expression | dict | None = None
