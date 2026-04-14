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


class Address(FHIRElement):
    _list_fields = {'extension', 'line'}
    _field_types = {'extension': 'Extension', 'period': 'Period'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    use: Optional[Code] = None
    type: Optional[Code] = None
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
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
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
    _coding_fields = frozenset({'system', 'version', 'code', 'display', 'userSelected'})

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    coding: Coding | FHIRList[Coding]
    text: Optional[String] = None

    def __getattr__(self, name: 'str'):
        if name in self._coding_fields:
            return getattr(self.coding, name)
        return super().__getattr__(name)

    def __setattr__(self, name: 'str', value):
        if name in self._coding_fields:
            setattr(self.coding, name, value)
        else:
            super().__setattr__(name, value)


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
    type: Optional[Code] = None
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
    _field_types = {'extension': 'Extension', 'codeFilter': 'Element', 'dateFilter': 'Element', 'sort': 'Element'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    type: Optional[Code] = None
    profile: Canonical | FHIRList[Canonical] = None
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
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'additionalInstruction': 'CodeableConcept', 'timing': 'Timing', 'site': 'CodeableConcept', 'route': 'CodeableConcept', 'method': 'CodeableConcept', 'doseAndRate': 'Element', 'maxDosePerPeriod': 'Ratio', 'maxDosePerAdministration': 'Quantity', 'maxDosePerLifetime': 'Quantity'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    sequence: Optional[Integer] = None
    text: Optional[String] = None
    additionalInstruction: CodeableConcept | FHIRList[CodeableConcept]
    patientInstruction: Optional[String] = None
    timing: Optional[Timing]
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
    _list_fields = {'extension', 'modifierExtension', 'representation', 'code', 'alias', 'type', 'example', 'condition', 'constraint', 'mapping'}
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'code': 'Coding', 'slicing': 'Element', 'base': 'Element', 'type': 'Element', 'example': 'Element', 'constraint': 'Element', 'binding': 'Element', 'mapping': 'Element'}

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
    type: Element | FHIRList[Element]
    meaningWhenMissing: Optional[Markdown] = None
    orderMeaning: Optional[String] = None
    example: Element | FHIRList[Element]
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
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    url: Optional[str] = None


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
    _field_types = {'extension': 'Extension', 'type': 'CodeableConcept', 'period': 'Period', 'assigner': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    use: Optional[Code] = None
    type: Optional[CodeableConcept]
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
    type: Optional[Code] = None
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
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'gender': 'CodeableConcept', 'race': 'CodeableConcept', 'physiologicalCondition': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
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
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'identifier': 'Identifier', 'type': 'CodeableConcept', 'period': 'Quantity', 'specialPrecautionsForStorage': 'CodeableConcept'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
    identifier: Optional[Identifier]
    type: Optional[CodeableConcept]
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
    type: Optional[Uri] = None
    identifier: Optional[Identifier]
    display: Optional[String] = None


class RelatedArtifact(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'document': 'Attachment'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    type: Optional[Code] = None
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
    _list_fields = {'extension', 'type'}
    _field_types = {'extension': 'Extension', 'type': 'Coding', 'who': 'Reference', 'onBehalfOf': 'Reference'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    type: Coding | FHIRList[Coding]
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
    _field_types = {'extension': 'Extension', 'modifierExtension': 'Extension', 'amountType': 'CodeableConcept', 'referenceRange': 'Element'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    modifierExtension: Extension | FHIRList[Extension]
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
    _field_types = {'extension': 'Extension', 'data': 'DataRequirement', 'condition': 'Expression'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    type: Optional[Code] = None
    name: Optional[String] = None
    data: DataRequirement | FHIRList[DataRequirement]
    condition: Optional[Expression]


class UsageContext(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'code': 'Coding'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    code: Optional[Coding]


class bodySite(FHIRElement):
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None


class capabilities(FHIRElement):
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None


class designNote(FHIRElement):
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None


class display(FHIRElement):
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None


class entryFormat(FHIRElement):
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None


class geolocation(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'extension': 'Extension', 'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    extension: Optional[Extension]
    extension: Optional[Extension]
    url: Optional[str] = None


class language(FHIRElement):
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None


class maxDecimalPlaces(FHIRElement):
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None


class maxSize(FHIRElement):
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None


class maxValue(FHIRElement):
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None


class mimeType(FHIRElement):
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None


class minLength(FHIRElement):
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None


class minValue(FHIRElement):
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None


class narrativeLink(FHIRElement):
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None


class ordinalValue(FHIRElement):
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None


class originalText(FHIRElement):
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None


class regex(FHIRElement):
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None


class replaces(FHIRElement):
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None


class translation(FHIRElement):
    _list_fields = {'extension'}
    _field_types = {'extension': 'Extension', 'extension': 'Extension', 'extension': 'Extension'}

    id: Optional[str] = None
    extension: Extension | FHIRList[Extension]
    extension: Optional[Extension]
    extension: Optional[Extension]
    url: Optional[str] = None


class variable(FHIRElement):
    _field_types = {'extension': 'Extension'}

    id: Optional[str] = None
    extension: Optional[Extension]
    url: Optional[str] = None
