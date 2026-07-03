from __future__ import annotations

import json
from pathlib import Path

import pytest

from zato.fhir.r4_0_1 import resources as resources_module
from zato.fhir.r4_0_1.validation_data import REQUIRED_FIELDS


def _load_cardinality() -> dict:
    path = Path(__file__).parent / "r4_cardinality.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


R4_CARDINALITY = _load_cardinality()


def _spec_list_field_names(fields: dict) -> set[str]:
    out = set()
    for name, card in fields.items():
        mx = card["max"]
        if mx == "*":
            out.add(name)
            continue
        s = str(mx)
        if s.isdigit() and int(s) > 1:
            out.add(name)
    return out


def _required_field_rows(fields: dict) -> list[tuple[str, int, str]]:
    rows = []
    for fname, card in fields.items():
        if card["min"] > 0:
            rows.append((fname, int(card["min"]), str(card["max"])))
    return rows


def _validation_field_aliases(spec_field: str) -> frozenset[str]:
    names = {spec_field}
    if len(spec_field) > 1 and spec_field.endswith("_"):
        names.add(spec_field[:-1])
    return frozenset(names)


def _required_fields_match(entries: list[dict], spec_field: str, min_v: int, max_v: str) -> bool:
    aliases = _validation_field_aliases(spec_field)
    for e in entries:
        if e["field"] in aliases and e["min"] == min_v and str(e["max"]) == max_v:
            return True
    return False


@pytest.mark.parametrize("resource_name", sorted(R4_CARDINALITY.keys()))
def test_list_fields_match_cardinality_spec(resource_name):
    data = R4_CARDINALITY[resource_name]
    cls = getattr(resources_module, resource_name, None)
    if cls is None:
        pytest.skip(f"no class {resource_name!r} in zato.fhir.r4_0_1.resources")
    spec_lists = _spec_list_field_names(data["fields"])
    class_lists = set(cls._list_fields)
    extra = sorted(class_lists - spec_lists)
    missing = sorted(spec_lists - class_lists)
    assert not extra and not missing, (
        f"resource {resource_name!r}: _list_fields vs cardinality max mismatch - "
        f"extra={extra!r}, missing={missing!r}"
    )


@pytest.mark.parametrize("resource_name", sorted(R4_CARDINALITY.keys()))
def test_required_fields_match_validation_data(resource_name):
    data = R4_CARDINALITY[resource_name]
    required_rows = _required_field_rows(data["fields"])
    if not required_rows:
        return
    if resource_name not in REQUIRED_FIELDS:
        pytest.fail(
            f"resource {resource_name!r} has required fields in r4_cardinality.json "
            f"but is absent from REQUIRED_FIELDS"
        )
    entries = REQUIRED_FIELDS[resource_name]
    for field, min_v, max_v in required_rows:
        assert _required_fields_match(entries, field, min_v, max_v), (
            f"resource {resource_name!r} field {field!r}: spec requires min={min_v} max={max_v!r} "
            f"but REQUIRED_FIELDS has no matching entry"
        )
