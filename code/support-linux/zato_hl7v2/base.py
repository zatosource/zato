from __future__ import annotations

import json
from enum import Enum
from typing import Any, Optional, TypeVar

from zato_hl7v2.encoding import encode_er7
from zato_hl7v2.registry import (
    register_segment,
    register_field,
    register_component,
    resolve_field,
    resolve_component,
)

T = TypeVar("T")

_datatype_classes: dict[str, type] = {}
_segment_classes: dict[str, type] = {}

# Primitive string datatypes whose values must be reconstructed by joining
# components with '^' because the tokenizer splits on that delimiter.
_Primitive_String_Datatypes = frozenset({'ST', 'FT', 'TX'})


class Usage(str, Enum):
    REQUIRED = "R"
    OPTIONAL = "O"


class HL7Component:
    def __init__(self, position: int) -> None:
        self.position = position
        self.attr_name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.attr_name = name

    def __get__(self, instance: Any, owner: type) -> Any:
        if instance is None:
            return self
        parent_msg = getattr(instance, '_parent_message', None)
        if parent_msg is not None:
            segment_id = getattr(instance, '_parent_segment_id', '')
            field_idx = getattr(instance, '_parent_field_idx', -1)
            rep_idx = getattr(instance, '_parent_rep_idx', 0)
            if segment_id and field_idx >= 0:
                raw_message = getattr(parent_msg, '_raw_message', None)
                if raw_message is not None:
                    for item in raw_message.items:
                        if hasattr(item, 'segment_id') and item.segment_id == segment_id:
                            if field_idx < len(item.fields):
                                field_data = item.fields[field_idx]
                                if rep_idx < len(field_data):
                                    rep_data = field_data[rep_idx]
                                    comp_idx = self.position - 1
                                    if comp_idx < len(rep_data):
                                        comp_data = rep_data[comp_idx]
                                        if comp_data and len(comp_data) == 1:
                                            return comp_data[0]
                                        return comp_data
                            break
                    return None
        if self.attr_name in instance.__dict__:
            return instance.__dict__[self.attr_name]
        raw = getattr(instance, "_raw_components", None)
        if raw is None:
            return None
        idx = self.position - 1
        if idx < len(raw):
            val = raw[idx]
            if val and len(val) == 1:
                return val[0]
            return val
        return None

    def __set__(self, instance: Any, value: Any) -> None:
        instance.__dict__[self.attr_name] = value
        parent_msg = getattr(instance, '_parent_message', None)
        if parent_msg is None:
            return
        segment_id = getattr(instance, '_parent_segment_id', '')
        field_idx = getattr(instance, '_parent_field_idx', -1)
        rep_idx = getattr(instance, '_parent_rep_idx', 0)
        if not segment_id or field_idx < 0:
            return
        comp_idx = self.position - 1
        raw_message = getattr(parent_msg, '_raw_message', None)
        if raw_message is None:
            return
        str_value = str(value) if value is not None else ""
        raw_message.set_segment_field(segment_id, field_idx, rep_idx, comp_idx, 0, str_value)


class HL7Field:
    def __init__(
        self,
        position: int,
        datatype: str,
        usage: Usage,
        repeatable: bool = False,
        table: Optional[str] = None,
    ) -> None:
        self.position = position
        self.datatype = datatype
        self.usage = usage
        self.repeatable = repeatable
        self.table = table
        self.attr_name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.attr_name = name
        if hasattr(owner, '_segment_id'):
            register_field(owner._segment_id, name, self.position, self.datatype)

    def __get__(self, instance: Any, owner: type) -> Any:
        if instance is None:
            return self
        cache = instance.__dict__
        if self.attr_name in cache:
            return cache[self.attr_name]
        raw_segment = getattr(instance, "_raw_segment", None)
        if raw_segment is None:
            dt_class = _datatype_classes.get(self.datatype)
            if dt_class is not None:
                obj = dt_class()
                cache[self.attr_name] = obj
                return obj
            return None
        idx = self.position - 1
        if idx >= len(raw_segment.fields):
            return None
        field_data = raw_segment.fields[idx]
        if not field_data:
            return None
        if self.repeatable:
            result = []
            for rep_idx, rep in enumerate(field_data):
                if rep:
                    val = self._build_value(rep, instance, rep_idx)
                    if val is not None:
                        result.append(val)
            cache[self.attr_name] = result
            return result
        else:
            if field_data and field_data[0]:
                val = self._build_value(field_data[0], instance, 0)
                cache[self.attr_name] = val
                return val
            return None

    def _build_value(self, components: list[list[str]], instance: Any = None, rep_idx: int = 0) -> Any:
        if not components:
            return None

        # For primitive string types (ST, FT, TX), join all components with '^'
        # to reconstruct the original value that the tokenizer split apart.
        if self.datatype in _Primitive_String_Datatypes:
            joined = '^'.join(comp[0] if comp else '' for comp in components)
            return joined if joined else None

        if len(components) == 1 and len(components[0]) == 1:
            return components[0][0] if components[0][0] else None
        dt_class = _datatype_classes.get(self.datatype)
        if dt_class is not None:
            obj = dt_class.__new__(dt_class)  # type: ignore[call-overload]
            obj._raw_components = components
            if instance is not None:
                obj._parent_message = getattr(instance, '_parent_message', None)
                obj._parent_segment_id = instance._segment_id
                obj._parent_field_idx = self.position - 1
                obj._parent_rep_idx = rep_idx
            return obj
        if components and components[0]:
            return components[0][0] if components[0][0] else None
        return None

    def __set__(self, instance: Any, value: Any) -> None:
        instance.__dict__[self.attr_name] = value


class HL7SegmentAttr:
    def __init__(
        self,
        segment_id: str,
        optional: bool = False,
        repeatable: bool = False,
    ) -> None:
        self.segment_id = segment_id
        self.optional = optional
        self.repeatable = repeatable
        self.attr_name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.attr_name = name

    def __get__(self, instance: Any, owner: type) -> Any:
        if instance is None:
            return self
        cache = instance.__dict__
        if self.attr_name in cache:
            return cache[self.attr_name]
        raw_message = getattr(instance, "_raw_message", None)
        seg_class = _segment_classes.get(self.segment_id)
        if seg_class is None:
            return None
        if raw_message is None:
            if self.repeatable:
                result: list[Any] = []
                cache[self.attr_name] = result
                return result
            else:
                seg = seg_class()
                seg._parent_message = instance
                cache[self.attr_name] = seg
                return seg
        if self.repeatable:
            result = []
            for item in raw_message.items:
                if hasattr(item, 'segment_id') and item.segment_id == self.segment_id:
                    seg = seg_class.__new__(seg_class)  # type: ignore[call-overload]
                    seg._raw_segment = item
                    seg._parent_message = instance
                    result.append(seg)
            cache[self.attr_name] = result
            return result
        else:
            for item in raw_message.items:
                if hasattr(item, 'segment_id') and item.segment_id == self.segment_id:
                    seg = seg_class.__new__(seg_class)  # type: ignore[call-overload]
                    seg._raw_segment = item
                    seg._parent_message = instance
                    cache[self.attr_name] = seg
                    return seg
            return None

    def __set__(self, instance: Any, value: Any) -> None:
        instance.__dict__[self.attr_name] = value


class HL7GroupAttr:
    def __init__(
        self,
        name: str,
        optional: bool = False,
        repeatable: bool = False,
    ) -> None:
        self.name = name
        self.optional = optional
        self.repeatable = repeatable
        self.attr_name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.attr_name = name

    def __get__(self, instance: Any, owner: type) -> Any:
        if instance is None:
            return self
        cache = instance.__dict__
        if self.attr_name in cache:
            return cache[self.attr_name]
        raw_message = getattr(instance, "_raw_message", None)
        if raw_message is None:
            return None
        if self.repeatable:
            result = []
            for item in raw_message.items:
                if hasattr(item, 'name') and item.name == self.name:
                    grp = HL7Group()
                    grp._raw_group = item
                    result.append(grp)
            cache[self.attr_name] = result
            return result
        else:
            for item in raw_message.items:
                if hasattr(item, 'name') and item.name == self.name:
                    grp = HL7Group()
                    grp._raw_group = item
                    cache[self.attr_name] = grp
                    return grp
            return None

    def __set__(self, instance: Any, value: Any) -> None:
        instance.__dict__[self.attr_name] = value


class HL7DataType:
    _raw_components: list[list[str]]
    _parent_message: Any = None
    _parent_segment_id: str = ""
    _parent_field_idx: int = -1
    _parent_rep_idx: int = 0

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        _datatype_classes[cls.__name__] = cls
        for name in dir(cls):
            attr = getattr(cls, name, None)
            if isinstance(attr, HL7Component):
                register_component(cls.__name__, name, attr.position)

    def __init__(self, raw: Optional[str] = None, **kwargs: Any) -> None:
        if raw is not None:
            parts = raw.split("^")
            self._raw_components = [[p] for p in parts]
        else:
            self._raw_components = []
        for k, v in kwargs.items():
            setattr(self, k, v)

    def _resolve_semantic(self, name: str) -> Optional[str]:
        pos = resolve_component(self.__class__.__name__, name)
        if pos is None:
            return None
        for attr_name in dir(self.__class__):
            attr = getattr(self.__class__, attr_name, None)
            if isinstance(attr, HL7Component) and attr.position == pos:
                return attr_name
        return None

    def __getattr__(self, name: str) -> Any:
        if name.startswith('_'):
            raise AttributeError(name)
        positional = self._resolve_semantic(name)
        if positional is not None and positional != name:
            return getattr(self, positional)
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_'):
            super().__setattr__(name, value)
            return
        cls = type(self)
        if hasattr(cls, name) and isinstance(getattr(cls, name), HL7Component):
            super().__setattr__(name, value)
            return
        positional = self._resolve_semantic(name)
        if positional is not None:
            setattr(self, positional, value)
            return
        super().__setattr__(name, value)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for name in dir(self.__class__):
            attr = getattr(self.__class__, name)
            if isinstance(attr, HL7Component):
                val = getattr(self, name, None)
                if val is not None:
                    if isinstance(val, HL7DataType):
                        result[name] = val.to_dict()
                    elif isinstance(val, list):
                        result[name] = [v.to_dict() if isinstance(v, HL7DataType) else v for v in val]
                    else:
                        result[name] = val
        return result

    def to_json(self, indent: Optional[int] = None) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def serialize(self) -> str:
        delimiters = ('|', '^', '~', '\\', '&')
        components: list[HL7Component] = []
        for name in dir(self.__class__):
            attr = getattr(self.__class__, name)
            if isinstance(attr, HL7Component):
                components.append(attr)
        if not components:
            return ""
        components.sort(key=lambda c: c.position)
        max_pos = components[-1].position
        parts: list[str] = []
        for pos in range(1, max_pos + 1):
            val = None
            for comp in components:
                if comp.position == pos:
                    val = getattr(self, comp.attr_name, None)
                    break
            parts.append(encode_er7(str(val), delimiters) if val is not None else "")
        while parts and parts[-1] == "":
            parts.pop()
        return "^".join(parts)


class HL7Segment:
    _segment_id: str = ""
    _raw_segment: Any = None
    _parent_message: Any = None

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if cls._segment_id:
            _segment_classes[cls._segment_id] = cls
            register_segment(cls._segment_id, cls)

    def __init__(self, raw_segment: Any = None) -> None:
        self._raw_segment = raw_segment

    @classmethod
    def from_er7(cls, raw: str) -> "HL7Segment":
        raise NotImplementedError

    def serialize(self) -> str:
        if self._raw_segment:
            field_sep = '|'
            comp_sep = '^'
            rep_sep = '~'
            esc_char = '\\'
            subcomp_sep = '&'
            delimiters = (field_sep, comp_sep, rep_sep, esc_char, subcomp_sep)

            result = self._segment_id
            for field_idx, field in enumerate(self._raw_segment.fields):
                result += field_sep
                if self._segment_id == "MSH" and field_idx == 0:
                    result += f"{comp_sep}{rep_sep}{esc_char}{subcomp_sep}"
                    continue
                rep_strs = []
                for rep in field:
                    comp_strs = []
                    for comp in rep:
                        subcomp_strs = [encode_er7(s, delimiters) for s in comp]
                        comp_strs.append(subcomp_sep.join(subcomp_strs))
                    rep_strs.append(comp_sep.join(comp_strs))
                result += rep_sep.join(rep_strs)
            return result
        return self._serialize_from_dict()

    def _serialize_from_dict(self) -> str:
        delimiters = ('|', '^', '~', '\\', '&')
        fields_by_pos: dict[int, str] = {}
        for name in dir(self.__class__):
            attr = getattr(self.__class__, name)
            if isinstance(attr, HL7Field):
                val = self.__dict__.get(attr.attr_name)
                if val is not None:
                    if isinstance(val, HL7DataType):
                        fields_by_pos[attr.position] = val.serialize()
                    elif isinstance(val, str):
                        fields_by_pos[attr.position] = encode_er7(val, delimiters)
                    elif isinstance(val, list):
                        parts_list:'list[str]' = []
                        for v in val:
                            if isinstance(v, HL7DataType):
                                parts_list.append(v.serialize())
                            else:
                                parts_list.append(encode_er7(str(v), delimiters))
                        fields_by_pos[attr.position] = "~".join(parts_list)
                    else:
                        fields_by_pos[attr.position] = encode_er7(str(val), delimiters)
        if not fields_by_pos:
            return ""
        max_pos = max(fields_by_pos.keys())
        parts = [self._segment_id]
        if self._segment_id == "MSH":
            parts.append("^~\\&")
        for pos in range(1 if self._segment_id != "MSH" else 2, max_pos + 1):
            parts.append(fields_by_pos.get(pos, ""))
        return "|".join(parts)

    to_hl7 = serialize
    to_er7 = serialize

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"_segment_id": self._segment_id}
        for name in dir(self.__class__):
            attr = getattr(self.__class__, name)
            if isinstance(attr, HL7Field):
                val = getattr(self, name, None)
                if val is not None:
                    if isinstance(val, HL7DataType):
                        result[name] = val.to_dict()
                    elif isinstance(val, list):
                        result[name] = [v.to_dict() if isinstance(v, HL7DataType) else v for v in val]
                    else:
                        result[name] = val
        return result

    def to_json(self, indent: Optional[int] = None) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class HL7Group:
    _group_name: str = ""
    _raw_group: Any = None

    def serialize(self) -> str:
        from zato_hl7v2_rs import serialize as _rust_serialize
        if self._raw_group:
            return _rust_serialize(self._raw_group)  # type: ignore[no-any-return]
        return ""

    to_hl7 = serialize
    to_er7 = serialize

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"_group_name": self._group_name}
        if self._raw_group:
            result["segments"] = []
            for item in self._raw_group.items:
                if hasattr(item, 'segment_id'):
                    seg_class = _segment_classes.get(item.segment_id)
                    if seg_class:
                        seg = seg_class.__new__(seg_class)  # type: ignore[call-overload]
                        seg._raw_segment = item
                        result["segments"].append(seg.to_dict())
        return result

    def to_json(self, indent: Optional[int] = None) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class HL7Message:
    _structure_id: str = ""
    _registry: dict[str, type] = {}
    _raw_message: Any = None

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if cls._structure_id:
            HL7Message._registry[cls._structure_id] = cls

    @classmethod
    def parse(cls, raw: str) -> "HL7Message":
        from zato_hl7v2.v2_9 import parse_message
        return parse_message(raw)

    def serialize(self) -> str:
        from zato_hl7v2.v2_9 import serialize as _serialize
        return _serialize(self)

    to_hl7 = serialize
    to_er7 = serialize

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"_structure_id": self._structure_id}
        for name in dir(self.__class__):
            attr = getattr(self.__class__, name)
            if isinstance(attr, HL7SegmentAttr):
                val = getattr(self, name, None)
                if val is not None:
                    if isinstance(val, list):
                        result[name] = [v.to_dict() for v in val]
                    else:
                        result[name] = val.to_dict()
            elif isinstance(attr, HL7GroupAttr):
                val = getattr(self, name, None)
                if val is not None:
                    if isinstance(val, list):
                        result[name] = [v.to_dict() for v in val]
                    else:
                        result[name] = val.to_dict()
        return result

    def to_json(self, indent: Optional[int] = None) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def get(self, path: str) -> Any:
        return _get_by_path(self, path)

    def set(self, path: str, value: str) -> None:
        _set_by_path(self, path, value)


def _get_by_path(msg: "HL7Message", path: str) -> Any:
    parts = path.split(".")
    if len(parts) < 2:
        return None

    segment_ref = parts[0]
    field_ref = parts[1]

    segment = _resolve_segment(msg, segment_ref)
    if segment is None:
        return None

    rep_idx = None
    if "[" in field_ref:
        field_ref, rep_part = field_ref.split("[", 1)
        rep_idx = int(rep_part.rstrip("]"))

    field_pos, field_datatype = _resolve_field(segment, field_ref)
    if field_pos is None:
        return None

    raw_segment = segment._raw_segment
    if raw_segment is None:
        return None

    field_idx = field_pos - 1
    if field_idx >= len(raw_segment.fields):
        return None

    field_data = raw_segment.fields[field_idx]
    if not field_data:
        return None

    if rep_idx is not None:
        if rep_idx >= len(field_data):
            return None
        rep_data = field_data[rep_idx]
    else:
        rep_data = field_data[0] if field_data else None

    if rep_data is None:
        return None

    if len(parts) == 2:
        if rep_data and rep_data[0]:
            return rep_data[0][0] if rep_data[0][0] else None
        return None

    comp_ref = parts[2]
    if "[" in comp_ref:
        comp_ref, _ = comp_ref.split("[", 1)

    if field_datatype is None:
        return None
    comp_pos = _resolve_component(field_datatype, comp_ref)
    if comp_pos is None:
        return None

    comp_idx = comp_pos - 1
    if comp_idx >= len(rep_data):
        return None

    comp_data = rep_data[comp_idx]
    if not comp_data:
        return None

    if len(parts) == 3:
        return comp_data[0] if comp_data[0] else None

    subcomp_ref = parts[3]
    subcomp_pos = _resolve_subcomponent(subcomp_ref)
    if subcomp_pos is None:
        return None

    subcomp_idx = subcomp_pos - 1
    if subcomp_idx >= len(comp_data):
        return None

    return comp_data[subcomp_idx] if comp_data[subcomp_idx] else None


def _resolve_segment(msg: "HL7Message", segment_ref: str) -> Any:
    segment_ref_upper = segment_ref.upper()
    for item in msg._raw_message.items:
        if hasattr(item, 'segment_id') and item.segment_id == segment_ref_upper:
            seg_class = _segment_classes.get(segment_ref_upper)
            if seg_class:
                seg = seg_class.__new__(seg_class)  # type: ignore[call-overload]
                seg._raw_segment = item
                seg._parent_message = msg
                return seg
    segment_ref_lower = segment_ref.lower()
    for name in dir(msg.__class__):
        attr = getattr(msg.__class__, name)
        if isinstance(attr, HL7SegmentAttr) and name.lower() == segment_ref_lower:
            return getattr(msg, name)
    return None


def _resolve_field(segment: "HL7Segment", field_ref: str) -> tuple[Optional[int], Optional[str]]:
    return resolve_field(segment._segment_id, field_ref)


def _resolve_component(datatype: str, comp_ref: str) -> Optional[int]:
    return resolve_component(datatype, comp_ref)


def _resolve_subcomponent(subcomp_ref: str) -> Optional[int]:
    if subcomp_ref.isdigit():
        return int(subcomp_ref)
    return None


def _set_by_path(msg: "HL7Message", path: str, value: str) -> None:
    parts = path.split(".")
    if len(parts) < 2:
        return

    segment_ref = parts[0]
    field_ref = parts[1]

    segment_id = segment_ref.upper()
    found = False
    for item in msg._raw_message.items:
        if hasattr(item, 'segment_id') and item.segment_id == segment_id:
            found = True
            break
    if not found:
        segment_ref_lower = segment_ref.lower()
        for name in dir(msg.__class__):
            attr = getattr(msg.__class__, name)
            if isinstance(attr, HL7SegmentAttr) and name.lower() == segment_ref_lower:
                segment_id = attr.segment_id
                found = True
                break
    if not found:
        return

    rep_idx = 0
    if "[" in field_ref:
        field_ref, rep_part = field_ref.split("[", 1)
        rep_idx = int(rep_part.rstrip("]"))

    field_pos, field_datatype = resolve_field(segment_id, field_ref)
    if field_pos is None:
        return

    field_idx = field_pos - 1

    if len(parts) == 2:
        msg._raw_message.set_segment_field(segment_id, field_idx, rep_idx, 0, 0, value)
        return

    comp_ref = parts[2]
    if "[" in comp_ref:
        comp_ref, _ = comp_ref.split("[", 1)

    if field_datatype is None:
        return
    comp_pos = _resolve_component(field_datatype, comp_ref)
    if comp_pos is None:
        return

    comp_idx = comp_pos - 1

    if len(parts) == 3:
        msg._raw_message.set_segment_field(segment_id, field_idx, rep_idx, comp_idx, 0, value)
        return

    subcomp_ref = parts[3]
    subcomp_pos = _resolve_subcomponent(subcomp_ref)
    if subcomp_pos is None:
        return

    subcomp_idx = subcomp_pos - 1
    msg._raw_message.set_segment_field(segment_id, field_idx, rep_idx, comp_idx, subcomp_idx, value)
