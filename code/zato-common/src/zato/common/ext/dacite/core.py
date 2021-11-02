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

import copy
from dataclasses import is_dataclass
from itertools import zip_longest
from typing import TypeVar, Type, Optional, get_type_hints, Mapping, Any

from zato.common.ext.dacite.config import Config
from zato.common.ext.dacite.data import Data
from zato.common.ext.dacite.dataclasses import get_default_value_for_field, create_instance, DefaultValueNotFoundError, get_fields
from zato.common.ext.dacite.exceptions import (
    ForwardReferenceError,
    WrongTypeError,
    DaciteError,
    UnionMatchError,
    MissingValueError,
    DaciteFieldError,
    UnexpectedDataError,
    StrictUnionMatchError,
)
from zato.common.ext.dacite.types import (
    is_instance,
    is_generic_collection,
    is_union,
    extract_generic,
    is_optional,
    transform_value,
    extract_origin_collection,
    is_init_var,
    extract_init_var,
)

T = TypeVar("T")


def from_dict(data_class: Type[T], data: Data, config: Optional[Config] = None) -> T:
    """Create a data class instance from a dictionary.

    :param data_class: a data class type
    :param data: a dictionary of a input data
    :param config: a configuration of the creation process
    :return: an instance of a data class
    """
    is_class_init_false = data_class.__dataclass_params__.init is False
    init_values: Data = {}
    post_init_values: Data = {}
    config = config or Config()

    try:
        data_class_hints = get_type_hints(data_class, globalns=config.forward_references)
    except NameError as error:
        raise ForwardReferenceError(str(error))

    data_class_fields = get_fields(data_class)

    if 1:#config.strict:
        extra_fields = set(data.keys()) - {f.name for f in data_class_fields}
        if extra_fields:
            raise UnexpectedDataError(keys=extra_fields)

    print()
    for field in data_class_fields:
        print('AAA-1', field)
    print()

    for field in data_class_fields:
        field = copy.copy(field)
        field.type = data_class_hints[field.name]

        if field.name in data:

            try:
                field_data = data[field.name]
                transformed_value = transform_value(
                    type_hooks=config.type_hooks, cast=config.cast, target_type=field.type, value=field_data
                )
                value = _build_value(type_=field.type, data=transformed_value, config=config)

                print()
                print(444, value)
                print(555, field_data)
                print(666, transformed_value)
                print()

            except DaciteFieldError as error:
                error.update_path(field.name)
                raise

            #if config.check_types and not is_instance(value, field.type):
            #    raise WrongTypeError(field_path=field.name, field_type=field.type, value=value)

        else:
            try:
                value = get_default_value_for_field(field)

                print()
                print(333, value)
                print()

            except DefaultValueNotFoundError:
                if not field.init:
                    continue

                print()
                print(111, field)
                print(222, data)
                print()

                #zzz

                raise MissingValueError(field.name)

        if is_class_init_false:
            post_init_values[field.name] = value
        else:
            if field.init:
                init_values[field.name] = value
            else:
                post_init_values[field.name] = value

    return create_instance(data_class=data_class, init_values=init_values, post_init_values=post_init_values)


def _build_value(type_: Type, data: Any, config: Config) -> Any:
    if is_init_var(type_):
        type_ = extract_init_var(type_)
    if is_union(type_):
        return _build_value_for_union(union=type_, data=data, config=config)
    elif is_generic_collection(type_) and is_instance(data, extract_origin_collection(type_)):
        return _build_value_for_collection(collection=type_, data=data, config=config)
    elif is_dataclass(type_) and is_instance(data, Data):
        return from_dict(data_class=type_, data=data, config=config)
    return data


def _build_value_for_union(union: Type, data: Any, config: Config) -> Any:
    types = extract_generic(union)
    if is_optional(union) and len(types) == 2:
        return _build_value(type_=types[0], data=data, config=config)
    union_matches = {}
    for inner_type in types:
        try:
            # noinspection PyBroadException
            try:
                data = transform_value(
                    type_hooks=config.type_hooks, cast=config.cast, target_type=inner_type, value=data
                )
            except Exception:  # pylint: disable=broad-except
                continue
            value = _build_value(type_=inner_type, data=data, config=config)
            if is_instance(value, inner_type):
                if config.strict_unions_match:
                    union_matches[inner_type] = value
                else:
                    return value
        except DaciteError:
            pass
    if config.strict_unions_match:
        if len(union_matches) > 1:
            raise StrictUnionMatchError(union_matches)
        return union_matches.popitem()[1]
    if not config.check_types:
        return data
    raise UnionMatchError(field_type=union, value=data)


def _build_value_for_collection(collection: Type, data: Any, config: Config) -> Any:
    data_type = data.__class__
    if is_instance(data, Mapping):
        item_type = extract_generic(collection, defaults=(Any, Any))[1]
        return data_type((key, _build_value(type_=item_type, data=value, config=config)) for key, value in data.items())
    elif is_instance(data, tuple):
        types = extract_generic(collection)
        if len(types) == 2 and types[1] == Ellipsis:
            return data_type(_build_value(type_=types[0], data=item, config=config) for item in data)
        return data_type(
            _build_value(type_=type_, data=item, config=config) for item, type_ in zip_longest(data, types)
        )
    item_type = extract_generic(collection, defaults=(Any,))[0]
    return data_type(_build_value(type_=item_type, data=item, config=config) for item in data)
