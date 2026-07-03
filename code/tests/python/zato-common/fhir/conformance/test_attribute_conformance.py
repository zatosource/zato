from __future__ import annotations

import json
from pathlib import Path

import pytest

from zato.fhir.r4_0_1 import resources as resources_module


def _load_field_info() -> dict:
    path = Path(__file__).parent / "r4_field_info.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


R4_FIELD_INFO = _load_field_info()


def _public_resource_field_names(cls) -> set[str]:
    names = set()
    for key in getattr(cls, "__annotations__", {}):
        if key.startswith("_"):
            continue
        names.add(key)
    inst = cls()
    for key in getattr(inst, "__dict__", {}):
        if not key.startswith("_"):
            names.add(key)
    return names


@pytest.mark.parametrize("resource_name", sorted(R4_FIELD_INFO.keys()))
def test_field_names_match_spec(resource_name):
    spec_fields = set(R4_FIELD_INFO[resource_name]["field_types"].keys())
    cls = getattr(resources_module, resource_name, None)
    if cls is None:
        pytest.skip(f"no class {resource_name!r} in zato.fhir.r4_0_1.resources")
    class_fields = _public_resource_field_names(cls)
    extra = sorted(class_fields - spec_fields)
    missing = sorted(spec_fields - class_fields)
    assert not extra and not missing, (
        f"resource {resource_name!r}: field set mismatch - extra={extra!r}, missing={missing!r}"
    )


@pytest.mark.parametrize("resource_name", sorted(R4_FIELD_INFO.keys()))
def test_list_fields_match_spec(resource_name):
    spec_list = set(R4_FIELD_INFO[resource_name]["list_fields"])
    cls = getattr(resources_module, resource_name, None)
    if cls is None:
        pytest.skip(f"no class {resource_name!r} in zato.fhir.r4_0_1.resources")
    class_list = set(cls._list_fields)
    extra = sorted(class_list - spec_list)
    missing = sorted(spec_list - class_list)
    assert not extra and not missing, (
        f"resource {resource_name!r}: _list_fields mismatch - extra={extra!r}, missing={missing!r}"
    )
