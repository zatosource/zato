from __future__ import annotations

import json
from pathlib import Path

import pytest

from zato.fhir.r4_0_1 import resources as resources_module


def _load_choice_fields() -> dict:
    path = Path(__file__).parent / "r4_choice_fields.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


R4_CHOICE_FIELDS = _load_choice_fields()


@pytest.mark.parametrize("resource_name", sorted(R4_CHOICE_FIELDS.keys()))
def test_choice_fields_exist_on_class(resource_name):
    cls = getattr(resources_module, resource_name, None)
    if cls is None:
        pytest.fail(f"no class {resource_name!r} in zato.fhir.r4_0_1.resources")
    spec_choices = R4_CHOICE_FIELDS[resource_name]
    for base_name, suffixed_names in spec_choices.items():
        for suffixed in suffixed_names:
            instance = cls()
            assert hasattr(instance, suffixed), (
                f"{resource_name}.{suffixed} (from {base_name}[x]) is missing"
            )


@pytest.mark.parametrize("resource_name", sorted(R4_CHOICE_FIELDS.keys()))
def test_choice_fields_class_attribute_matches_spec(resource_name):
    cls = getattr(resources_module, resource_name, None)
    if cls is None:
        pytest.fail(f"no class {resource_name!r} in zato.fhir.r4_0_1.resources")
    class_choices = getattr(cls, '_choice_fields', None)
    if class_choices is None:
        pytest.fail(f"{resource_name} has no _choice_fields attribute")
    spec_choices = R4_CHOICE_FIELDS[resource_name]
    for base_name, expected_suffixed in spec_choices.items():
        assert base_name in class_choices, (
            f"{resource_name}._choice_fields missing base name {base_name!r}"
        )
        actual = class_choices[base_name]
        extra = sorted(set(actual) - set(expected_suffixed))
        missing = sorted(set(expected_suffixed) - set(actual))
        assert not extra and not missing, (
            f"{resource_name}._choice_fields[{base_name!r}] mismatch: "
            f"extra={extra!r}, missing={missing!r}"
        )


@pytest.mark.parametrize("resource_name", sorted(R4_CHOICE_FIELDS.keys()))
def test_choice_fields_default_to_none(resource_name):
    cls = getattr(resources_module, resource_name, None)
    if cls is None:
        pytest.fail(f"no class {resource_name!r} in zato.fhir.r4_0_1.resources")
    instance = cls()
    spec_choices = R4_CHOICE_FIELDS[resource_name]
    for base_name, suffixed_names in spec_choices.items():
        for suffixed in suffixed_names:
            assert getattr(instance, suffixed) is None, (
                f"{resource_name}.{suffixed} should default to None"
            )
