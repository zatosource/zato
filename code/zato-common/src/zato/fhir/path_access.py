from __future__ import annotations

from typing import Any

import zato_fhir_r4_0_1_core as _rust


def get_path(obj: Any, path: str) -> Any:
    return _rust.get_path(obj, path)


def set_path(obj: Any, path: str, value: Any) -> bool:
    return _rust.set_path(obj, path, value)


def _parse_path(path: str) -> list[dict]:
    return _rust.parse_path(path)
