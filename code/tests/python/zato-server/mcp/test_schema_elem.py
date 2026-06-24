# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.input_output import AsIs, Bool, CSV, Date, DateTime, Decimal, Dict, DictList, Float, Int, List, Secret, Text, UTC, UUID  # pyright: ignore[reportAttributeAccessIssue]
from zato.server.connection.mcp.schema import _get_elem_json_schema

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class _CustomElem:
    """ A custom class not in the elem mapping, simulating an unknown Elem type.
    """

    def __init__(self, name:'str') -> 'None':
        self.name = name

# ################################################################################################################################
# ################################################################################################################################

class TestGetElemJSONSchema(TestCase):
    """ Tests for _get_elem_json_schema covering all Elem subclasses.
    """

    def test_elem_schema_bool(self:'any_') -> 'None':
        """ Bool elem maps to boolean.
        """

        result = _get_elem_json_schema(Bool('is_active'))
        self.assertEqual(result, {'type': 'boolean'})

# ################################################################################################################################

    def test_elem_schema_int(self:'any_') -> 'None':
        """ Int elem maps to integer.
        """

        result = _get_elem_json_schema(Int('count'))
        self.assertEqual(result, {'type': 'integer'})

# ################################################################################################################################

    def test_elem_schema_float(self:'any_') -> 'None':
        """ Float elem maps to number.
        """

        result = _get_elem_json_schema(Float('rate'))
        self.assertEqual(result, {'type': 'number'})

# ################################################################################################################################

    def test_elem_schema_text(self:'any_') -> 'None':
        """ Text elem maps to string.
        """

        result = _get_elem_json_schema(Text('name'))
        self.assertEqual(result, {'type': 'string'})

# ################################################################################################################################

    def test_elem_schema_date(self:'any_') -> 'None':
        """ Date elem maps to string with date format.
        """

        result = _get_elem_json_schema(Date('birth_date'))
        self.assertEqual(result, {'type': 'string', 'format': 'date'})

# ################################################################################################################################

    def test_elem_schema_datetime(self:'any_') -> 'None':
        """ DateTime elem maps to string with date-time format.
        """

        result = _get_elem_json_schema(DateTime('created_at'))
        self.assertEqual(result, {'type': 'string', 'format': 'date-time'})

# ################################################################################################################################

    def test_elem_schema_uuid(self:'any_') -> 'None':
        """ UUID elem maps to string with uuid format.
        """

        result = _get_elem_json_schema(UUID('request_id'))
        self.assertEqual(result, {'type': 'string', 'format': 'uuid'})

# ################################################################################################################################

    def test_elem_schema_decimal(self:'any_') -> 'None':
        """ Decimal elem maps to string.
        """

        result = _get_elem_json_schema(Decimal('amount'))
        self.assertEqual(result, {'type': 'string'})

# ################################################################################################################################

    def test_elem_schema_csv(self:'any_') -> 'None':
        """ CSV elem maps to string.
        """

        result = _get_elem_json_schema(CSV('tags'))
        self.assertEqual(result, {'type': 'string'})

# ################################################################################################################################

    def test_elem_schema_dict(self:'any_') -> 'None':
        """ Dict elem maps to object.
        """

        result = _get_elem_json_schema(Dict('metadata'))
        self.assertEqual(result, {'type': 'object'})

# ################################################################################################################################

    def test_elem_schema_dict_list(self:'any_') -> 'None':
        """ DictList elem maps to array of objects.
        """

        result = _get_elem_json_schema(DictList('items'))
        self.assertEqual(result, {'type': 'array', 'items': {'type': 'object'}})

# ################################################################################################################################

    def test_elem_schema_list(self:'any_') -> 'None':
        """ List elem maps to array.
        """

        result = _get_elem_json_schema(List('values'))
        self.assertEqual(result, {'type': 'array'})

# ################################################################################################################################

    def test_elem_schema_secret(self:'any_') -> 'None':
        """ Secret elem maps to string.
        """

        result = _get_elem_json_schema(Secret('password'))
        self.assertEqual(result, {'type': 'string'})

# ################################################################################################################################

    def test_elem_schema_utc(self:'any_') -> 'None':
        """ UTC elem maps to string with date-time format.
        """

        result = _get_elem_json_schema(UTC('timestamp'))
        self.assertEqual(result, {'type': 'string', 'format': 'date-time'})

# ################################################################################################################################

    def test_elem_schema_as_is(self:'any_') -> 'None':
        """ AsIs elem maps to string.
        """

        result = _get_elem_json_schema(AsIs('raw_data'))
        self.assertEqual(result, {'type': 'string'})

# ################################################################################################################################

    def test_elem_schema_unknown_subclass(self:'any_') -> 'None':
        """ A custom Elem subclass not in the mapping falls back to string.
        """

        result = _get_elem_json_schema(_CustomElem('custom_field'))
        self.assertEqual(result, {'type': 'string'})

# ################################################################################################################################
# ################################################################################################################################
