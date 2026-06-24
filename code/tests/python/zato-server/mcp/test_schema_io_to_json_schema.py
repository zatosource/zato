# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.input_output import IOProcessor  # pyright: ignore[reportAttributeAccessIssue]
from zato.server.connection.mcp.schema import io_to_json_schema

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class _ServiceNoIO:
    """ A service class that has no _io attribute at all.
    """
    pass

# ################################################################################################################################

class _ServiceIONone:
    """ A service class that has _io explicitly set to None.
    """
    _io = None

# ################################################################################################################################

class _ServiceIOUnknownType:
    """ A service class with _io set to an unrecognized type.
    """
    _io = 'some-random-string'

# ################################################################################################################################

class _ServiceIOProcessorNoInput:
    """ A service class with a fresh IOProcessor that has no input declared.
    """
    _io = IOProcessor()

# ################################################################################################################################

class _ServiceIOProcessorRequiredOnly:
    """ A service class with only required input elements.
    """
    input = 'name', 'user_id'

IOProcessor.attach_io(None, _ServiceIOProcessorRequiredOnly)

# ################################################################################################################################

class _ServiceIOProcessorOptionalOnly:
    """ A service class with only optional input elements.
    """
    input = '-nickname', '-bio'

IOProcessor.attach_io(None, _ServiceIOProcessorOptionalOnly)

# ################################################################################################################################

class _ServiceIOProcessorMixed:
    """ A service class with both required and optional input elements.
    """
    input = 'name', 'age', '-email'

IOProcessor.attach_io(None, _ServiceIOProcessorMixed)

# ################################################################################################################################
# ################################################################################################################################

class TestIOToJSONSchemaDispatch(TestCase):
    """ Tests for the io_to_json_schema top-level dispatcher.
    """

    def test_no_io_returns_empty_object_schema(self:'any_') -> 'None':
        """ A service with no _io attribute returns a plain object schema.
        """

        result = io_to_json_schema(_ServiceNoIO)
        self.assertEqual(result, {'type': 'object'})

# ################################################################################################################################

    def test_io_none_returns_empty_object_schema(self:'any_') -> 'None':
        """ A service with _io = None returns a plain object schema.
        """

        result = io_to_json_schema(_ServiceIONone)
        self.assertEqual(result, {'type': 'object'})

# ################################################################################################################################

    def test_unknown_io_type_returns_empty_object_schema(self:'any_') -> 'None':
        """ A service with _io set to an unrecognized type returns a plain object schema.
        """

        result = io_to_json_schema(_ServiceIOUnknownType)
        self.assertEqual(result, {'type': 'object'})

# ################################################################################################################################

    def test_io_processor_no_input_declared(self:'any_') -> 'None':
        """ A service with a fresh IOProcessor (has_input_declared=False) returns a plain object schema.
        """

        result = io_to_json_schema(_ServiceIOProcessorNoInput)
        self.assertEqual(result, {'type': 'object'})

# ################################################################################################################################
# ################################################################################################################################

class TestIOProcessorSchema(TestCase):
    """ Tests for io_to_json_schema with real IOProcessor-based service classes.
    """

    def test_io_processor_has_input_declared_false(self:'any_') -> 'None':
        """ An IOProcessor with has_input_declared=False returns a plain object schema.
        """

        result = io_to_json_schema(_ServiceIOProcessorNoInput)
        self.assertEqual(result, {'type': 'object'})

# ################################################################################################################################

    def test_io_processor_with_get_input_required(self:'any_') -> 'None':
        """ A service with required and optional input produces correct schema.
        """

        result = io_to_json_schema(_ServiceIOProcessorMixed)

        self.assertEqual(result['type'], 'object')
        self.assertIn('name', result['properties'])
        self.assertIn('age', result['properties'])
        self.assertIn('email', result['properties'])
        self.assertEqual(sorted(result['required']), ['age', 'name'])

# ################################################################################################################################

    def test_io_processor_required_only(self:'any_') -> 'None':
        """ A service with only required input elems has all in required list.
        """

        result = io_to_json_schema(_ServiceIOProcessorRequiredOnly)

        self.assertEqual(result['type'], 'object')
        self.assertEqual(sorted(result['properties'].keys()), ['name', 'user_id'])
        self.assertEqual(sorted(result['required']), ['name', 'user_id'])

# ################################################################################################################################

    def test_io_processor_optional_only(self:'any_') -> 'None':
        """ A service with only optional input elems has properties but no required key.
        """

        result = io_to_json_schema(_ServiceIOProcessorOptionalOnly)

        self.assertEqual(result['type'], 'object')
        self.assertEqual(sorted(result['properties'].keys()), ['bio', 'nickname'])
        self.assertNotIn('required', result)

# ################################################################################################################################

    def test_io_processor_mixed_required_optional(self:'any_') -> 'None':
        """ A service with both required and optional produces the correct split.
        """

        result = io_to_json_schema(_ServiceIOProcessorMixed)

        self.assertEqual(result['type'], 'object')
        self.assertEqual(sorted(result['properties'].keys()), ['age', 'email', 'name'])
        self.assertEqual(sorted(result['required']), ['age', 'name'])

        # Verify types are correctly mapped
        self.assertEqual(result['properties']['name'], {'type': 'string'})
        self.assertEqual(result['properties']['age'], {'type': 'string'})
        self.assertEqual(result['properties']['email'], {'type': 'string'})

# ################################################################################################################################
# ################################################################################################################################
