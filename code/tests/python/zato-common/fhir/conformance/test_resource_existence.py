from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from zato.fhir.base import FHIRResource
from zato.fhir.r4_0_1 import resources as resources_module


def _load_resource_names() -> list[str]:
    path = Path(__file__).parent / "r4_resource_names.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _iter_resource_classes():
    for _, obj in inspect.getmembers(resources_module, inspect.isclass):
        if not issubclass(obj, FHIRResource) or obj is FHIRResource:
            continue
        rt = getattr(obj, "_resource_type", None)
        if not rt:
            continue
        yield obj


R4_RESOURCE_NAMES = _load_resource_names()
_RESOURCE_CLASSES = sorted(_iter_resource_classes(), key=lambda c: c.__name__)


def test_spec_names_have_python_classes():
    spec = set(R4_RESOURCE_NAMES)
    python_by_rt = {cls._resource_type: cls for cls in _RESOURCE_CLASSES}
    missing = sorted(spec - set(python_by_rt.keys()))
    assert not missing, f"missing Python classes for resource names: {missing!r}"


def test_python_classes_are_in_spec():
    spec = set(R4_RESOURCE_NAMES)
    python_rts = {cls._resource_type for cls in _RESOURCE_CLASSES}
    extra = sorted(python_rts - spec)
    assert not extra, f"Python resource classes not listed in r4_resource_names.json: {extra!r}"


@pytest.mark.parametrize("cls", _RESOURCE_CLASSES, ids=lambda c: c.__name__)
def test_resource_type_equals_class_name(cls):
    assert cls._resource_type == cls.__name__, (
        f"class {cls.__name__!r}: _resource_type is {cls._resource_type!r}, expected {cls.__name__!r}"
    )
