# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from typing import Optional
from unittest import TestCase

# Zato
from zato.server.connection.mcp.schema import dataclass_model_to_schema

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class _RequestRequired:
    """ All fields are required - no defaults, no Optional.
    """
    name: str
    age: int

# ################################################################################################################################

@dataclass
class _RequestOptional:
    """ All fields are optional via Optional type or defaults.
    """
    email: Optional[str] = None
    priority: int = 0

# ################################################################################################################################

@dataclass
class _RequestMixed:
    """ Some fields required, some optional.
    """
    name: str
    age: int
    email: Optional[str] = None
    nickname: str = 'anon'

# ################################################################################################################################

@dataclass
class _Address:
    """ A nested dataclass used as a field type.
    """
    street: str
    city: str

# ################################################################################################################################

@dataclass
class _RequestNested:
    """ Has a field whose type is another dataclass.
    """
    name: str
    address: _Address

# ################################################################################################################################

@dataclass
class _RequestListOfType:
    """ Has a field annotated as list[int].
    """
    name: str
    scores: list[int]

# ################################################################################################################################

@dataclass
class _RequestDictField:
    """ Has a field annotated as dict.
    """
    name: str
    metadata: dict

# ################################################################################################################################

@dataclass
class _RequestEmpty:
    """ A dataclass with no fields at all.
    """
    pass

# ################################################################################################################################
# ################################################################################################################################

class TestDataClassIOSchema(TestCase):
    """ Tests for dataclass_model_to_schema.
    """

    def test_dataclass_io_required_fields(self:'any_') -> 'None':
        """ A dataclass with only required fields has all in required list.
        """

        result = dataclass_model_to_schema(_RequestRequired)

        self.assertEqual(result['type'], 'object')
        self.assertEqual(sorted(result['properties'].keys()), ['age', 'name'])
        self.assertEqual(result['properties']['name'], {'type': 'string'})
        self.assertEqual(result['properties']['age'], {'type': 'integer'})
        self.assertEqual(sorted(result['required']), ['age', 'name'])

# ################################################################################################################################

    def test_dataclass_io_optional_fields(self:'any_') -> 'None':
        """ A dataclass with only optional fields has properties but no required key.
        """

        result = dataclass_model_to_schema(_RequestOptional)

        self.assertEqual(result['type'], 'object')
        self.assertEqual(sorted(result['properties'].keys()), ['email', 'priority'])
        self.assertNotIn('required', result)

# ################################################################################################################################

    def test_dataclass_io_mixed(self:'any_') -> 'None':
        """ A dataclass with both required and optional fields produces correct split.
        """

        result = dataclass_model_to_schema(_RequestMixed)

        self.assertEqual(result['type'], 'object')
        self.assertEqual(sorted(result['properties'].keys()), ['age', 'email', 'name', 'nickname'])
        self.assertEqual(sorted(result['required']), ['age', 'name'])

# ################################################################################################################################

    def test_dataclass_io_nested(self:'any_') -> 'None':
        """ A dataclass with a nested dataclass field produces a nested object schema.
        """

        result = dataclass_model_to_schema(_RequestNested)

        self.assertEqual(result['type'], 'object')
        self.assertIn('address', result['properties'])

        address_schema = result['properties']['address']
        self.assertEqual(address_schema['type'], 'object')
        self.assertEqual(sorted(address_schema['properties'].keys()), ['city', 'street'])
        self.assertEqual(sorted(address_schema['required']), ['city', 'street'])

# ################################################################################################################################

    def test_dataclass_io_list_of_type(self:'any_') -> 'None':
        """ A field annotated list[int] produces array with items schema.
        """

        result = dataclass_model_to_schema(_RequestListOfType)

        self.assertEqual(result['properties']['scores'], {'type': 'array', 'items': {'type': 'integer'}})

# ################################################################################################################################

    def test_dataclass_io_dict_field(self:'any_') -> 'None':
        """ A field annotated dict produces object schema.
        """

        result = dataclass_model_to_schema(_RequestDictField)

        self.assertEqual(result['properties']['metadata'], {'type': 'object'})

# ################################################################################################################################

    def test_dataclass_io_no_fields(self:'any_') -> 'None':
        """ A dataclass with no fields returns a plain object schema.
        """

        result = dataclass_model_to_schema(_RequestEmpty)

        self.assertEqual(result, {'type': 'object'})

# ################################################################################################################################
# ################################################################################################################################
