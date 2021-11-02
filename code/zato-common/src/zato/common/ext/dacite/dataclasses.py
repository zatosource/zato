"""
This module is a modified vendor copy of the dacite package from https://pypi.org/project/dacite/

MIT License

Copyright (c) 2018 Konrad Hałas

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# flake8: noqa

from dataclasses import Field, MISSING, _FIELDS, _FIELD, _FIELD_INITVAR  # type: ignore
from typing import Type, Any, TypeVar, List

from zato.common.ext.dacite.data import Data
from zato.common.ext.dacite.types import is_optional

T = TypeVar("T", bound=Any)


class DefaultValueNotFoundError(Exception):
    pass


def get_default_value_for_field(field: Field) -> Any:
    if field.default != MISSING:
        return field.default
    elif field.default_factory != MISSING:  # type: ignore
        return field.default_factory()  # type: ignore
    elif is_optional(field.type):
        return None
    raise DefaultValueNotFoundError()


def create_instance(data_class: Type[T], init_values: Data, post_init_values: Data) -> T:
    instance = data_class(**init_values)
    for key, value in post_init_values.items():
        setattr(instance, key, value)
    return instance


def get_fields(data_class: Type[T]) -> List[Field]:
    fields = getattr(data_class, _FIELDS)
    return [f for f in fields.values() if f._field_type is _FIELD or f._field_type is _FIELD_INITVAR]
