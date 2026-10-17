# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum, IntEnum
from typing import Any, Annotated, Callable, ClassVar, Literal, NewType, Optional, TypeVar, Union
from unittest import main, TestCase
from uuid import UUID

# Zato
from zato.common.typing_ import anylist, dict_, intanydict, list_, set_, strnone, strsetdict, tuple_
from zato.openapi.generator.annotation import get_io_container, get_runtime_type, is_model_class, NameResolver

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_resolver = NameResolver()

# ################################################################################################################################
# ################################################################################################################################

class OrderStatus(Enum):
    Open = 'open'
    Closed = 'closed'

class Priority(IntEnum):
    Low = 1
    High = 2

class Rounding(Enum):
    Up = 'up'
    Places = 2

class Coordinates(Enum):
    Origin = (0, 0)

class NoMembers(Enum):
    pass

class Attributes(dict):
    pass

class Amount(Decimal):
    pass

class Settings:
    pass

class Address:
    street: 'str'
    city: 'strnone'

@dataclass(init=False)
class Customer:
    name: 'str'

@dataclass(init=False)
class NoFields:
    pass

InvoiceNumber = NewType('InvoiceNumber', str)

ItemType = TypeVar('ItemType')

# ################################################################################################################################
# ################################################################################################################################

def _get(type_hint:'any_') -> 'any_':
    """ Returns the type that the mapper documents for a runtime annotation.
    """
    out = get_runtime_type(type_hint, _resolver)
    return out

# ################################################################################################################################
# ################################################################################################################################

class RuntimeTypeTestCase(TestCase):
    """ Annotations as the interpreter has them at runtime, e.g. in the models of hot-deployed services.
    """

    def test_types_known_to_the_mapper(self) -> 'None':
        self.assertEqual(_get(str), 'str')
        self.assertEqual(_get(int), 'int')
        self.assertEqual(_get(bool), 'bool')
        self.assertEqual(_get(Decimal), 'Decimal')
        self.assertEqual(_get(datetime), 'datetime')
        self.assertEqual(_get(date), 'date')
        self.assertEqual(_get(UUID), 'UUID')

    def test_a_subclass_of_a_type_known_to_the_mapper(self) -> 'None':
        self.assertEqual(_get(Attributes), 'dict')
        self.assertEqual(_get(Amount), 'Decimal')

    def test_a_class_unknown_to_the_mapper(self) -> 'None':
        self.assertEqual(_get(Settings), 'object')

    def test_none(self) -> 'None':
        self.assertEqual(_get(None), 'NoneType')
        self.assertEqual(_get(type(None)), 'NoneType')

    def test_any(self) -> 'None':
        self.assertEqual(_get(Any), 'any_')

    def test_text(self) -> 'None':
        self.assertEqual(_get('int | None'), {'type': 'int', 'optional': True})

# ################################################################################################################################

    def test_an_optional_type(self) -> 'None':
        self.assertEqual(_get(Optional[Decimal]), {'type': 'Decimal', 'optional': True})

    def test_an_optional_type_with_a_vertical_bar(self) -> 'None':
        self.assertEqual(_get(Decimal | None), {'type': 'Decimal', 'optional': True})

    def test_a_union(self) -> 'None':
        expected = {'type': 'union', 'container': 'union', 'union_types': ['int', 'float']}
        self.assertEqual(_get(int | float), expected)
        self.assertEqual(_get(Union[int, float]), expected)

    def test_a_union_with_none(self) -> 'None':
        union = {'type': 'union', 'container': 'union', 'union_types': ['str', 'int']}
        self.assertEqual(_get(str | int | None), {'type': union, 'optional': True})

# ################################################################################################################################

    def test_a_list(self) -> 'None':
        self.assertEqual(_get(list_[int]), {'container': 'list', 'element_type': 'int'})
        self.assertEqual(_get(list[Decimal]), {'container': 'list', 'element_type': 'Decimal'})

    def test_a_list_of_an_element_in_quotes(self) -> 'None':
        self.assertEqual(_get(list_['Customer']), {'container': 'list', 'element_type': 'Customer'})
        self.assertEqual(_get(list_['int | None']), {'container': 'list', 'element_type': {'type': 'int', 'optional': True}})

    def test_a_list_of_optional_elements(self) -> 'None':
        expected = {'container': 'list', 'element_type': {'type': 'str', 'optional': True}}
        self.assertEqual(_get(list_[strnone]), expected)

    def test_a_dict(self) -> 'None':
        self.assertEqual(_get(dict_[str, Decimal]), {'container': 'dict', 'element_type': 'Decimal'})
        self.assertEqual(_get(dict[str, int]), {'container': 'dict', 'element_type': 'int'})

    def test_a_set(self) -> 'None':
        self.assertEqual(_get(set_[str]), {'container': 'set', 'element_type': 'str'})
        self.assertEqual(_get(frozenset[int]), {'container': 'set', 'element_type': 'int'})

    def test_a_tuple(self) -> 'None':
        self.assertEqual(_get(tuple_[int, ...]), {'container': 'tuple', 'element_type': 'int'})
        self.assertEqual(_get(tuple[int, str]), {'container': 'tuple', 'element_type': 'any_'})

    def test_a_generic_other_than_a_container(self) -> 'None':
        self.assertEqual(_get(Callable[[int], str]), 'any_')

# ################################################################################################################################

    def test_a_literal(self) -> 'None':
        self.assertEqual(_get(Literal['open', 'closed']), {'enum': ['open', 'closed']})

    def test_an_enumeration_of_strings(self) -> 'None':
        self.assertEqual(_get(OrderStatus), {'enum': ['open', 'closed']})

    def test_an_enumeration_of_integers(self) -> 'None':
        self.assertEqual(_get(Priority), {'enum': [1, 2]})

    def test_an_enumeration_of_mixed_values(self) -> 'None':
        self.assertEqual(_get(Rounding), {'enum': ['up', 2]})

    def test_an_enumeration_of_values_without_an_openapi_form(self) -> 'None':
        self.assertEqual(_get(Coordinates), 'any_')

    def test_an_enumeration_without_members(self) -> 'None':
        self.assertEqual(_get(NoMembers), 'any_')

# ################################################################################################################################

    def test_qualifiers(self) -> 'None':
        self.assertEqual(_get(Annotated[int, 'Order count']), 'int')
        self.assertEqual(_get(ClassVar[str]), 'str')

    def test_a_new_type(self) -> 'None':
        self.assertEqual(_get(InvoiceNumber), 'str')

    def test_a_type_variable(self) -> 'None':
        self.assertEqual(_get(ItemType), 'any_')

    def test_zato_aliases(self) -> 'None':
        self.assertEqual(_get(strnone), {'type': 'str', 'optional': True})
        self.assertEqual(_get(anylist), {'container': 'list', 'element_type': 'any_'})
        self.assertEqual(_get(intanydict), {'container': 'dict', 'element_type': 'any_'})
        self.assertEqual(_get(strsetdict), {'container': 'dict', 'element_type': {'container': 'set', 'element_type': 'any_'}})

# ################################################################################################################################

    def test_a_model(self) -> 'None':
        self.assertEqual(_get(Customer), 'Customer')
        self.assertEqual(_get(Address), 'Address')
        self.assertEqual(_get(list_[Customer]), {'container': 'list', 'element_type': 'Customer'})

    def test_a_dataclass_without_fields_is_a_model(self) -> 'None':
        self.assertTrue(is_model_class(NoFields))

    def test_a_class_without_annotations_is_not_a_model(self) -> 'None':
        self.assertFalse(is_model_class(Settings))

    def test_an_enumeration_is_not_a_model(self) -> 'None':
        self.assertFalse(is_model_class(OrderStatus))

# ################################################################################################################################
# ################################################################################################################################

class IOContainerTestCase(TestCase):
    """ A service's input or output given as a subscripted type.
    """

    def test_a_list_of_models(self) -> 'None':
        io_type = _get(list_[Customer])
        expected = {'type': 'container', 'container_type': 'list', 'element_type': 'Customer'}
        self.assertEqual(get_io_container(io_type), expected)

    def test_a_set(self) -> 'None':
        io_type = _get(set_[str])
        expected = {'type': 'container', 'container_type': 'set', 'element_type': 'str'}
        self.assertEqual(get_io_container(io_type), expected)

    def test_a_dict(self) -> 'None':
        io_type = _get(dict_[str, Customer])
        expected = {'type': 'container', 'container_type': 'dict', 'element_type': 'Customer'}
        self.assertEqual(get_io_container(io_type), expected)

    def test_an_optional_model(self) -> 'None':
        io_type = _get(Optional[Customer])
        self.assertEqual(get_io_container(io_type), {'type': 'any'})

    def test_a_generic_other_than_a_container(self) -> 'None':
        io_type = _get(Callable[[int], str])
        self.assertEqual(get_io_container(io_type), {'type': 'any'})

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
