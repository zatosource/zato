from __future__ import annotations

from typing import Dict, Tuple, Optional

_segment_registry: Dict[str, type] = {}
_field_registry: Dict[str, Dict[str, Tuple[int, str]]] = {}
_component_registry: Dict[str, Dict[str, int]] = {}
_semantic_names_loaded: bool = False


def register_segment(segment_id: str, segment_class: type) -> None:
    _segment_registry[segment_id] = segment_class


def register_field(segment_id: str, field_name: str, position: int, datatype: str) -> None:
    if segment_id not in _field_registry:
        _field_registry[segment_id] = {}
    _field_registry[segment_id][field_name] = (position, datatype)
    _field_registry[segment_id][str(position)] = (position, datatype)


def register_component(datatype: str, comp_name: str, position: int) -> None:
    if datatype not in _component_registry:
        _component_registry[datatype] = {}
    _component_registry[datatype][comp_name] = position
    _component_registry[datatype][str(position)] = position


def get_segment_class(segment_id: str) -> Optional[type]:
    return _segment_registry.get(segment_id)


def resolve_field(segment_id: str, field_ref: str) -> Tuple[Optional[int], Optional[str]]:
    if segment_id not in _field_registry:
        return (None, None)
    field_info = _field_registry[segment_id].get(field_ref)
    if field_info:
        return field_info
    field_ref_lower = field_ref.lower()
    field_info = _field_registry[segment_id].get(field_ref_lower)
    if field_info:
        return field_info
    return (None, None)


def _load_semantic_names() -> None:
    global _semantic_names_loaded
    if _semantic_names_loaded:
        return
    _semantic_names_loaded = True
    try:
        from zato.hl7v2.v2_9.semantic_names import SEMANTIC_TO_POSITIONAL
        for dt, mappings in SEMANTIC_TO_POSITIONAL.items():
            if dt not in _component_registry:
                _component_registry[dt] = {}
            for semantic_name, position in mappings.items():
                _component_registry[dt][semantic_name] = position
    except ImportError:
        pass


def resolve_component(datatype: str, comp_ref: str) -> Optional[int]:
    _load_semantic_names()
    if datatype not in _component_registry:
        if comp_ref.isdigit():
            return int(comp_ref)
        return None
    pos = _component_registry[datatype].get(comp_ref)
    if pos:
        return pos
    comp_ref_lower = comp_ref.lower()
    pos = _component_registry[datatype].get(comp_ref_lower)
    if pos:
        return pos
    if comp_ref.isdigit():
        return int(comp_ref)
    return None
