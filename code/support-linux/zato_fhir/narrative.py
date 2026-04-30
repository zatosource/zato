from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from zato_fhir_r4_0_1_core import (
    generate_narrative as _generate_narrative,
    py_pluralize as _pluralize,
    count_with_noun as _count_with_noun,
    py_to_label as _to_label,
)


@dataclass
class NarrativeTemplate:
    fields: 'list[str]' = field(default_factory=list)
    labels: 'dict[str, str]' = field(default_factory=dict)
    formatters: 'dict[str, Any]' = field(default_factory=dict)


def pluralize(word: 'str', count: 'int') -> 'str':
    return _pluralize(word, count)


def count_with_noun(count: 'int', singular: 'str') -> 'str':
    return _count_with_noun(count, singular)


def to_label(field_name: 'str') -> 'str':
    return _to_label(field_name)


def generate_narrative(
    resource: 'Any',
    template: 'NarrativeTemplate | None' = None,
) -> 'dict':
    return _generate_narrative(resource, template)
