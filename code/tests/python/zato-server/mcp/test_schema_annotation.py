# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import date as stdlib_date
from datetime import datetime as stdlib_datetime
from decimal import Decimal as stdlib_Decimal
from typing import Optional, Union
from unittest import TestCase
from uuid import UUID as stdlib_UUID

# Zato
from zato.server.connection.mcp.schema import _python_annotation_to_schema

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class _NestedModel:
    """ A nested dataclass used as a type annotation.
    """
    city: str
    zip_code: str

# ################################################################################################################################

class _UnknownType:
    """ An unrecognized type not in any mapping.
    """
    pass

# ################################################################################################################################
# ################################################################################################################################

class TestPythonAnnotationToSchema(TestCase):
    """ Tests for _python_annotation_to_schema.
    """

    def test_annotation_str(self:'any_') -> 'None':
        """ str maps to string.
        """

        result = _python_annotation_to_schema(str)
        self.assertEqual(result, {'type': 'string'})

# ################################################################################################################################

    def test_annotation_int(self:'any_') -> 'None':
        """ int maps to integer.
        """

        result = _python_annotation_to_schema(int)
        self.assertEqual(result, {'type': 'integer'})

# ################################################################################################################################

    def test_annotation_float(self:'any_') -> 'None':
        """ float maps to number.
        """

        result = _python_annotation_to_schema(float)
        self.assertEqual(result, {'type': 'number'})

# ################################################################################################################################

    def test_annotation_bool(self:'any_') -> 'None':
        """ bool maps to boolean.
        """

        result = _python_annotation_to_schema(bool)
        self.assertEqual(result, {'type': 'boolean'})

# ################################################################################################################################

    def test_annotation_list_bare(self:'any_') -> 'None':
        """ Bare list maps to array.
        """

        result = _python_annotation_to_schema(list)
        self.assertEqual(result, {'type': 'array'})

# ################################################################################################################################

    def test_annotation_list_typed(self:'any_') -> 'None':
        """ list[str] maps to array with string items.
        """

        result = _python_annotation_to_schema(list[str])
        self.assertEqual(result, {'type': 'array', 'items': {'type': 'string'}})

# ################################################################################################################################

    def test_annotation_dict(self:'any_') -> 'None':
        """ dict maps to object.
        """

        result = _python_annotation_to_schema(dict)
        self.assertEqual(result, {'type': 'object'})

# ################################################################################################################################

    def test_annotation_optional(self:'any_') -> 'None':
        """ Optional[int] unwraps to integer.
        """

        result = _python_annotation_to_schema(Optional[int])
        self.assertEqual(result, {'type': 'integer'})

# ################################################################################################################################

    def test_annotation_union_multi(self:'any_') -> 'None':
        """ Union[str, int] (non-Optional multi-type) falls back to string.
        """

        result = _python_annotation_to_schema(Union[str, int])
        self.assertEqual(result, {'type': 'string'})

# ################################################################################################################################

    def test_annotation_pipe_optional(self:'any_') -> 'None':
        """ int | None (PEP 604 syntax) unwraps to integer.
        """

        result = _python_annotation_to_schema(int | None)
        self.assertEqual(result, {'type': 'integer'})

# ################################################################################################################################

    def test_annotation_date(self:'any_') -> 'None':
        """ datetime.date maps to string with date format.
        """

        result = _python_annotation_to_schema(stdlib_date)
        self.assertEqual(result, {'type': 'string', 'format': 'date'})

# ################################################################################################################################

    def test_annotation_datetime(self:'any_') -> 'None':
        """ datetime.datetime maps to string with date-time format.
        """

        result = _python_annotation_to_schema(stdlib_datetime)
        self.assertEqual(result, {'type': 'string', 'format': 'date-time'})

# ################################################################################################################################

    def test_annotation_decimal(self:'any_') -> 'None':
        """ decimal.Decimal maps to string.
        """

        result = _python_annotation_to_schema(stdlib_Decimal)
        self.assertEqual(result, {'type': 'string'})

# ################################################################################################################################

    def test_annotation_uuid(self:'any_') -> 'None':
        """ uuid.UUID maps to string with uuid format.
        """

        result = _python_annotation_to_schema(stdlib_UUID)
        self.assertEqual(result, {'type': 'string', 'format': 'uuid'})

# ################################################################################################################################

    def test_annotation_nested_dataclass(self:'any_') -> 'None':
        """ A dataclass type produces nested object schema with properties.
        """

        result = _python_annotation_to_schema(_NestedModel)

        self.assertEqual(result['type'], 'object')

        properties = result['properties']
        property_keys = sorted(properties.keys())
        self.assertEqual(property_keys, ['city', 'zip_code'])

        required = result['required']
        sorted_required = sorted(required)
        self.assertEqual(sorted_required, ['city', 'zip_code'])

# ################################################################################################################################

    def test_annotation_unknown(self:'any_') -> 'None':
        """ An unrecognized type falls back to string.
        """

        result = _python_annotation_to_schema(_UnknownType)
        self.assertEqual(result, {'type': 'string'})

# ################################################################################################################################
# ################################################################################################################################
