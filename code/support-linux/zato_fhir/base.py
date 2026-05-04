from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, TypeVar, Generic, Iterator, overload

T = TypeVar('T')


class FHIRList(list, Generic[T]):

    def __getattr__(self, name: str) -> Any:
        if not self:
            raise AttributeError(f'Empty list has no attribute {name}')
        return getattr(self[0], name)

    def __setattr__(self, name: str, value: Any) -> None:
        if not self:
            raise AttributeError(f'Empty list, cannot set {name}')
        setattr(self[0], name, value)


class Cardinality(Enum):
    REQUIRED = 'required'
    OPTIONAL = 'optional'


@dataclass
class FHIRField(Generic[T]):
    min: int = 0
    max: str = '1'
    type_code: str = ''
    binding_strength: Optional[str] = None
    binding_valueset: Optional[str] = None

    @property
    def is_required(self) -> bool:
        return self.min >= 1

    @property
    def is_list(self) -> bool:
        return self.max == '*' or (self.max.isdigit() and int(self.max) > 1)


class ListWrapper(FHIRList):
    pass


def _resolve_type(type_name: str) -> type:
    import zato_fhir.r4_0_1.datatypes as dt
    import zato_fhir.r4_0_1.resources as rs
    return getattr(dt, type_name, None) or getattr(rs, type_name, None)


_PY_RESERVED = frozenset({
    'class', 'import', 'from', 'global', 'return', 'for', 'in',
    'assert', 'pass', 'raise', 'del', 'yield', 'break', 'continue',
    'lambda', 'not', 'or', 'and', 'is', 'if', 'else', 'elif',
    'while', 'try', 'except', 'finally', 'with', 'as', 'def', 'type',
})


def _dict_to_typed(data: dict, type_name: str) -> Any:
    field_type = _resolve_type(type_name)
    if field_type is None:
        return data
    instance = field_type()
    for k, v in data.items():
        if k == 'resourceType':
            continue
        attr_name = k + '_' if k in _PY_RESERVED else k
        setattr(instance, attr_name, v)
    return instance


def _fhir_setattr(obj: Any, name: str, value: Any) -> None:
    if name.startswith('_'):
        object.__setattr__(obj, name, value)
        return

    if name == 'contained' and isinstance(value, list):
        import zato_fhir_r4_0_1_core as _rust
        typed = _rust.rs_deserialize_contained(value)
        object.__setattr__(obj, name, ListWrapper(list(typed)))
        return

    if name in obj._list_fields:
        if isinstance(value, list):
            object.__setattr__(obj, name, ListWrapper(value))
        elif value is None:
            object.__setattr__(obj, name, value)
        else:
            if isinstance(value, dict) and name in obj._field_types:
                value = _dict_to_typed(value, obj._field_types[name])
            object.__setattr__(obj, name, ListWrapper([value]))
    elif isinstance(value, dict) and name in obj._field_types:
        object.__setattr__(obj, name, _dict_to_typed(value, obj._field_types[name]))
    else:
        object.__setattr__(obj, name, value)


class FHIRResource:
    _resource_type: str = ''
    _list_fields: set[str] = set()
    _field_types: dict[str, str] = {}

    def __getattr__(self, name: str) -> Any:
        if name.startswith('_'):
            raise AttributeError(name)

        if name in self._field_types:
            choice_fields = getattr(type(self), '_choice_fields', None)
            if choice_fields:
                for variants in choice_fields.values():
                    if name in variants:
                        return None

            type_name = self._field_types[name]
            field_type = _resolve_type(type_name)
            if field_type:
                instance = field_type()
                setattr(self, name, instance)
                return getattr(self, name)

        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        _fhir_setattr(self, name, value)

    def to_dict(self) -> dict[str, Any]:
        from zato_fhir.json_ import to_dict
        return to_dict(self)

    def to_json(self, indent: int | None = None) -> str:
        from zato_fhir.json_ import to_json
        return to_json(self, indent=indent)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FHIRResource:
        from zato_fhir.json_ import from_dict
        return from_dict(data, cls)

    @classmethod
    def from_json(cls, raw: str) -> FHIRResource:
        from zato_fhir.json_ import from_json
        return from_json(raw, cls)

    def get(self, path: str) -> Any:
        from zato_fhir.path_access import get_path
        return get_path(self, path)

    def set(self, path: str, value: Any) -> bool:
        from zato_fhir.path_access import set_path
        return set_path(self, path, value)

    def resolve(self, ref: 'str | Any') -> 'FHIRResource | None':
        """Resolve a reference string or Reference object.

        On a plain resource, only ``#contained`` refs are supported.
        On a Bundle, also resolves relative (``Patient/123``), absolute
        (``https://...``), and logical (Reference with identifier) refs
        by searching bundle entries.
        """
        import zato_fhir_r4_0_1_core as _rust
        is_bundle = getattr(self, '_resource_type', '') == 'Bundle'
        if is_bundle:
            result = _rust.rs_resolve_bundle(self, ref)
        elif isinstance(ref, str) and ref.startswith('#'):
            result = _rust.rs_resolve_contained(self, ref[1:])
        else:
            result = None
        return result if result is not None else None


class FHIRElement:
    _list_fields: set[str] = set()
    _field_types: dict[str, str] = {}

    def __getattr__(self, name: str) -> Any:
        if name.startswith('_'):
            raise AttributeError(name)

        if name in self._field_types:
            choice_fields = getattr(type(self), '_choice_fields', None)
            if choice_fields:
                for variants in choice_fields.values():
                    if name in variants:
                        return None

            type_name = self._field_types[name]
            field_type = _resolve_type(type_name)
            if field_type:
                instance = field_type()
                setattr(self, name, instance)
                return getattr(self, name)

        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        _fhir_setattr(self, name, value)

    def to_dict(self) -> dict[str, Any]:
        from zato_fhir.json_ import to_dict
        return to_dict(self)

    def to_json(self, indent: int | None = None) -> str:
        from zato_fhir.json_ import to_json
        return to_json(self, indent=indent)

    def get(self, path: str) -> Any:
        from zato_fhir.path_access import get_path
        return get_path(self, path)

    def set(self, path: str, value: Any) -> bool:
        from zato_fhir.path_access import set_path
        return set_path(self, path, value)


class FHIRPrimitive:
    pass
