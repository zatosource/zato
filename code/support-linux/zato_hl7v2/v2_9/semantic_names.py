"""
Semantic component name mappings for HL7 v2.9 datatypes.
Generated from HL7 v2ig FHIR StructureDefinition files.
"""
from __future__ import annotations


SEMANTIC_NAMES: dict[str, dict[int, str]] = {
}


POSITIONAL_TO_SEMANTIC: dict[str, dict[str, str]] = {}
SEMANTIC_TO_POSITIONAL: dict[str, dict[str, int]] = {}

for dt, comps in SEMANTIC_NAMES.items():
    dt_lower = dt.lower()
    POSITIONAL_TO_SEMANTIC[dt] = {}
    SEMANTIC_TO_POSITIONAL[dt] = {}
    for pos, name in comps.items():
        positional = f"{dt_lower}_{pos}"
        POSITIONAL_TO_SEMANTIC[dt][positional] = name
        SEMANTIC_TO_POSITIONAL[dt][name] = pos
