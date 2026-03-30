from __future__ import annotations

import json
from enum import Enum
from typing import Any, Optional, TypeVar, Generic

T = TypeVar("T")


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
        cache = instance.__dict__
        if self.attr_name in cache:
            return cache[self.attr_name]
        raw = getattr(instance, "_raw_components", None)
        if raw is None:
            return None
        idx = self.position - 1
        if idx < len(raw):
            val = raw[idx]
            cache[self.attr_name] = val
            return val
        return None

    def __set__(self, instance: Any, value: Any) -> None:
        instance.__dict__[self.attr_name] = value


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

    def __get__(self, instance: Any, owner: type) -> Any:
        if instance is None:
            return self
        cache = instance.__dict__
        if self.attr_name in cache:
            return cache[self.attr_name]
        raw_segment = getattr(instance, "_raw_segment", None)
        if raw_segment is None:
            return None
        idx = self.position - 1
        if idx >= len(raw_segment.fields):
            return None
        field_data = raw_segment.fields[idx]
        if not field_data:
            return None
        if self.repeatable:
            result = []
            for rep in field_data:
                if rep:
                    val = self._build_value(rep)
                    if val is not None:
                        result.append(val)
            cache[self.attr_name] = result
            return result
        else:
            if field_data and field_data[0]:
                val = self._build_value(field_data[0])
                cache[self.attr_name] = val
                return val
            return None

    def _build_value(self, components: list[list[str]]) -> Any:
        if not components:
            return None
        if len(components) == 1 and len(components[0]) == 1:
            return components[0][0] if components[0][0] else None
        from zato_hl7v2 import v2_9
        dt_class = getattr(v2_9.datatypes, self.datatype, None)
        if dt_class is not None and isinstance(dt_class, type) and issubclass(dt_class, HL7DataType):
            obj = dt_class.__new__(dt_class)
            obj._raw_components = components
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
        if raw_message is None:
            return None
        from zato_hl7v2 import v2_9
        seg_class = getattr(v2_9.segments, self.segment_id, None)
        if seg_class is None:
            return None
        if self.repeatable:
            result = []
            for item in raw_message.items:
                if hasattr(item, 'segment_id') and item.segment_id == self.segment_id:
                    seg = seg_class.__new__(seg_class)
                    seg._raw_segment = item
                    result.append(seg)
            cache[self.attr_name] = result
            return result
        else:
            for item in raw_message.items:
                if hasattr(item, 'segment_id') and item.segment_id == self.segment_id:
                    seg = seg_class.__new__(seg_class)
                    seg._raw_segment = item
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

    def __init__(self, raw: Optional[str] = None, **kwargs: Any) -> None:
        if raw is not None:
            parts = raw.split("^")
            self._raw_components = [[p] for p in parts]
        else:
            self._raw_components = []
        for k, v in kwargs.items():
            setattr(self, k, v)

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


class HL7Segment:
    _segment_id: str = ""
    _raw_segment: Any = None

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
                        subcomp_strs = [s for s in comp]
                        comp_strs.append(subcomp_sep.join(subcomp_strs))
                    rep_strs.append(comp_sep.join(comp_strs))
                result += rep_sep.join(rep_strs)
            return result
        return ""

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
            return _rust_serialize(self._raw_group)
        return ""

    to_hl7 = serialize
    to_er7 = serialize

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"_group_name": self._group_name}
        if self._raw_group:
            result["segments"] = []
            for item in self._raw_group.items:
                if hasattr(item, 'segment_id'):
                    from zato_hl7v2 import v2_9
                    seg_class = getattr(v2_9.segments, item.segment_id, None)
                    if seg_class:
                        seg = seg_class.__new__(seg_class)
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
        if self._raw_message:
            return _serialize(self._raw_message)
        return ""

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
