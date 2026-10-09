# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from unittest import TestCase
from unittest.mock import MagicMock

# Zato
from zato.common.marshal_.api import Model
from zato.common.marshal_.io import DataClassIO
from zato.input_output import IOProcessor
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

@dataclass(init=False)
class _PingRequest(Model):
    """ An input model with one required field.
    """
    host: str

# ################################################################################################################################

@dataclass(init=False)
class _PingResponse(Model):
    """ An output model with one field.
    """
    is_ok: bool

# ################################################################################################################################

class _ServiceDataClassOutputOnly:
    """ A service class whose I/O declaration has a dataclass output and no input attribute,
    which is what the service store builds for a service that declares only `output = Model`.
    """
    class IO:
        output = _PingResponse

_ = DataClassIO.attach_io(MagicMock(), _ServiceDataClassOutputOnly)

# ################################################################################################################################

class _ServiceDataClassInputOutput:
    """ A service class whose I/O declaration has a dataclass input and a dataclass output.
    """
    class IO:
        input = _PingRequest
        output = _PingResponse

_ = DataClassIO.attach_io(MagicMock(), _ServiceDataClassInputOutput)

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

        properties = result['properties']
        self.assertIn('name', properties)
        self.assertIn('age', properties)
        self.assertIn('email', properties)

        required = result['required']
        sorted_required = sorted(required)
        self.assertEqual(sorted_required, ['age', 'name'])

# ################################################################################################################################

    def test_io_processor_required_only(self:'any_') -> 'None':
        """ A service with only required input elems has all in required list.
        """

        result = io_to_json_schema(_ServiceIOProcessorRequiredOnly)

        self.assertEqual(result['type'], 'object')

        properties = result['properties']
        property_keys = sorted(properties.keys())
        self.assertEqual(property_keys, ['name', 'user_id'])

        required = result['required']
        sorted_required = sorted(required)
        self.assertEqual(sorted_required, ['name', 'user_id'])

# ################################################################################################################################

    def test_io_processor_optional_only(self:'any_') -> 'None':
        """ A service with only optional input elems has properties but no required key.
        """

        result = io_to_json_schema(_ServiceIOProcessorOptionalOnly)

        self.assertEqual(result['type'], 'object')

        properties = result['properties']
        property_keys = sorted(properties.keys())
        self.assertEqual(property_keys, ['bio', 'nickname'])
        self.assertNotIn('required', result)

# ################################################################################################################################

    def test_io_processor_mixed_required_optional(self:'any_') -> 'None':
        """ A service with both required and optional produces the correct split.
        """

        result = io_to_json_schema(_ServiceIOProcessorMixed)

        self.assertEqual(result['type'], 'object')

        properties = result['properties']
        property_keys = sorted(properties.keys())
        self.assertEqual(property_keys, ['age', 'email', 'name'])

        required = result['required']
        sorted_required = sorted(required)
        self.assertEqual(sorted_required, ['age', 'name'])

        # Verify types are correctly mapped
        name_schema = properties['name']
        age_schema = properties['age']
        email_schema = properties['email']
        self.assertEqual(name_schema, {'type': 'string'})
        self.assertEqual(age_schema, {'type': 'string'})
        self.assertEqual(email_schema, {'type': 'string'})

# ################################################################################################################################
# ################################################################################################################################

class TestDataClassIOToJSONSchema(TestCase):
    """ Tests for io_to_json_schema with DataClassIO-based service classes.
    """

    def test_dataclass_output_without_input(self:'any_') -> 'None':
        """ A service with a dataclass output and no input returns a plain object schema.
        """

        result = io_to_json_schema(_ServiceDataClassOutputOnly)
        self.assertEqual(result, {'type': 'object'})

# ################################################################################################################################

    def test_dataclass_input_and_output(self:'any_') -> 'None':
        """ A service with a dataclass input returns the schema of that input model.
        """

        result = io_to_json_schema(_ServiceDataClassInputOutput)
        self.assertEqual(result, {'type': 'object', 'properties': {'host': {'type': 'string'}}, 'required': ['host']})

# ################################################################################################################################
# ################################################################################################################################
