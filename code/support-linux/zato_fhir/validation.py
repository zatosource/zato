from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from zato_fhir.base import FHIRResource, FHIRElement


PYTHON_RESERVED = ('class', 'import', 'global', 'from')


@dataclass
class ValidationError:
    path: str
    code: str
    message: str


@dataclass
class ValidationResult:
    errors: list[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, path: str, code: str, message: str) -> None:
        self.errors.append(ValidationError(path=path, code=code, message=message))


def _to_py_field(name: str) -> str:
    return name + '_' if name in PYTHON_RESERVED else name


def validate(obj: Any, path: str = '') -> ValidationResult:
    from zato_fhir.r4_0_1.validation_data import REQUIRED_FIELDS
    from zato_fhir.r4_0_1.validation_extended import FIELD_INFO

    result = ValidationResult()

    if obj is None:
        return result

    if isinstance(obj, FHIRResource):
        if not path:
            path = obj._resource_type

        resource_type = obj._resource_type
        obj_vars = vars(obj)

        if resource_type in REQUIRED_FIELDS:
            for req in REQUIRED_FIELDS[resource_type]:
                field_name = req['field']
                py_field_name = _to_py_field(field_name)
                value = obj_vars.get(py_field_name)
                if value is None:
                    result.add_error(
                        f'{path}.{field_name}',
                        'required',
                        f"Required field '{field_name}' is missing"
                    )

        if resource_type in FIELD_INFO:
            info = FIELD_INFO[resource_type]

            max_card = info.get('max_cardinality', {})
            for field_name, max_val in max_card.items():
                py_field_name = _to_py_field(field_name)
                value = obj_vars.get(py_field_name)
                if isinstance(value, list) and max_val != '*' and len(value) > max_val:
                    result.add_error(
                        f'{path}.{field_name}',
                        'cardinality',
                        f"Field '{field_name}' has {len(value)} items, max is {max_val}"
                    )

            field_types = info.get('field_types', {})
            for field_name, expected_types in field_types.items():
                py_field_name = _to_py_field(field_name)
                value = obj_vars.get(py_field_name)
                if value is not None:
                    errors = _validate_type(value, expected_types, f'{path}.{field_name}')
                    result.errors.extend(errors)

            ref_targets = info.get('reference_targets', {})
            for field_name, allowed_targets in ref_targets.items():
                py_field_name = _to_py_field(field_name)
                value = obj_vars.get(py_field_name)
                if value is not None:
                    errors = _validate_reference(value, allowed_targets, f'{path}.{field_name}')
                    result.errors.extend(errors)

    for key, value in vars(obj).items():
        if key.startswith('_'):
            continue

        field_path = f'{path}.{key}' if path else key

        if isinstance(value, list):
            for i, item in enumerate(value):
                item_path = f'{field_path}[{i}]'
                if isinstance(item, (FHIRResource, FHIRElement)):
                    sub_result = validate(item, item_path)
                    result.errors.extend(sub_result.errors)
        elif isinstance(value, (FHIRResource, FHIRElement)):
            sub_result = validate(value, field_path)
            result.errors.extend(sub_result.errors)

    return result


def _validate_type(value: Any, expected_types: list[str], path: str) -> list[ValidationError]:
    errors = []

    if isinstance(value, list):
        for i, item in enumerate(value):
            item_errors = _validate_single_type(item, expected_types, f'{path}[{i}]')
            errors.extend(item_errors)
    else:
        errors = _validate_single_type(value, expected_types, path)

    return errors


def _validate_single_type(value: Any, expected_types: list[str], path: str) -> list[ValidationError]:
    if value is None:
        return []

    primitive_map = {
        'boolean': bool,
        'integer': int,
        'string': str,
        'decimal': (int, float),
        'uri': str,
        'url': str,
        'canonical': str,
        'base64Binary': str,
        'instant': str,
        'date': str,
        'dateTime': str,
        'time': str,
        'code': str,
        'oid': str,
        'id': str,
        'markdown': str,
        'unsignedInt': int,
        'positiveInt': int,
        'uuid': str,
        'xhtml': str,
        'http://hl7.org/fhirpath/System.String': str,
    }

    for expected in expected_types:
        if expected in primitive_map:
            py_type = primitive_map[expected]
            if isinstance(value, py_type):
                return []
        elif expected in ('Reference', 'CodeableConcept', 'Coding', 'Identifier', 'Period',
                         'Quantity', 'Range', 'Ratio', 'HumanName', 'Address', 'ContactPoint',
                         'Attachment', 'Annotation', 'Signature', 'Timing', 'Meta', 'Narrative',
                         'Extension', 'BackboneElement', 'Element', 'Resource', 'Dosage',
                         'ContactDetail', 'Contributor', 'DataRequirement', 'Expression',
                         'ParameterDefinition', 'RelatedArtifact', 'TriggerDefinition',
                         'UsageContext', 'Money', 'Age', 'Count', 'Distance', 'Duration',
                         'SampledData', 'Population', 'ProductShelfLife', 'ProdCharacteristic',
                         'MarketingStatus', 'SubstanceAmount'):
            if isinstance(value, (dict, FHIRElement, FHIRResource)):
                return []
        else:
            if isinstance(value, (dict, FHIRElement, FHIRResource)):
                return []

    return []


def _validate_reference(value: Any, allowed_targets: list[str], path: str) -> list[ValidationError]:
    errors = []

    if isinstance(value, list):
        for i, item in enumerate(value):
            item_errors = _validate_single_reference(item, allowed_targets, f'{path}[{i}]')
            errors.extend(item_errors)
    else:
        errors = _validate_single_reference(value, allowed_targets, path)

    return errors


def _validate_single_reference(value: Any, allowed_targets: list[str], path: str) -> list[ValidationError]:
    if value is None:
        return []

    if isinstance(value, dict):
        ref = value.get('reference', '')
        if ref and '/' in ref:
            ref_type = ref.split('/')[0]
            if ref_type and ref_type not in allowed_targets and 'Resource' not in allowed_targets:
                return [ValidationError(
                    path=path,
                    code='reference_target',
                    message=f"Reference to '{ref_type}' not allowed, expected one of: {allowed_targets}"
                )]

    return []


def validate_valueset_binding(
    obj: Any,
    path: str = '',
    include_extensible: bool = True,
) -> ValidationResult:
    from zato_fhir.r4_0_1.valueset_bindings import BINDINGS
    from zato_fhir.r4_0_1.valueset_codes import CODES

    result = ValidationResult()

    if obj is None:
        return result

    if not isinstance(obj, FHIRResource):
        return result

    if not path:
        path = obj._resource_type

    resource_type = obj._resource_type
    if resource_type not in BINDINGS:
        return result

    obj_vars = vars(obj)
    bindings = BINDINGS[resource_type]

    for binding in bindings:
        field_name = binding['field']
        strength = binding['strength']
        valueset_url = binding['valueSet']

        if strength == 'extensible' and not include_extensible:
            continue

        py_field_name = _to_py_field(field_name)
        value = obj_vars.get(py_field_name)

        if value is None:
            continue

        if valueset_url not in CODES:
            continue

        allowed_codes = CODES[valueset_url]
        errors = _validate_coded_value(value, allowed_codes, f'{path}.{field_name}', strength, valueset_url)
        result.errors.extend(errors)

    return result


def _validate_coded_value(
    value: Any,
    allowed_codes: set[str],
    path: str,
    strength: str,
    valueset_url: str,
) -> list[ValidationError]:
    errors = []

    if isinstance(value, str):
        if value not in allowed_codes:
            errors.append(ValidationError(
                path=path,
                code='valueset_binding',
                message=f"Code '{value}' not in ValueSet {valueset_url} (binding: {strength})"
            ))
    elif isinstance(value, dict):
        code = value.get('code')
        if code and code not in allowed_codes:
            errors.append(ValidationError(
                path=path,
                code='valueset_binding',
                message=f"Code '{code}' not in ValueSet {valueset_url} (binding: {strength})"
            ))

        codings = value.get('coding', [])
        for i, coding in enumerate(codings):
            coding_code = coding.get('code') if isinstance(coding, dict) else None
            if coding_code and coding_code not in allowed_codes:
                errors.append(ValidationError(
                    path=f'{path}.coding[{i}]',
                    code='valueset_binding',
                    message=f"Code '{coding_code}' not in ValueSet {valueset_url} (binding: {strength})"
                ))
    elif isinstance(value, list):
        for i, item in enumerate(value):
            item_errors = _validate_coded_value(item, allowed_codes, f'{path}[{i}]', strength, valueset_url)
            errors.extend(item_errors)

    return errors
