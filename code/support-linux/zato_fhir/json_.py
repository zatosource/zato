from __future__ import annotations

import json
from typing import Any, Type, TypeVar

import zato_fhir_r4_0_1_core as _rust

T = TypeVar('T')


def to_dict(obj: Any) -> dict[str, Any]:
    return _rust.to_dict(obj)


def to_json(obj: Any, indent: int | None = None) -> str:
    return json.dumps(to_dict(obj), indent=indent)


def from_dict(data: dict[str, Any], cls: Type[T]) -> T:
    return _rust.from_dict(data, cls)


def from_json(raw: str, cls: Type[T]) -> T:
    data = json.loads(raw)
    return from_dict(data, cls)
