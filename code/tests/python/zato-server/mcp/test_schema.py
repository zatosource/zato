# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import dataclasses
from dataclasses import field as dc_field
from datetime import date as stdlib_date
from datetime import datetime as stdlib_datetime
from decimal import Decimal as stdlib_Decimal
from unittest import TestCase, main
from uuid import UUID as STDLIB_UUID

# Zato
from zato.cy.simpleio import AsIs, Bool, Boolean, CSV, Date, DateTime, Decimal, Dict, DictList, Elem, Float, \
    Int, Integer, InternalNotGiven, List, ListOfDicts, NotGiven, Opaque, Secret, SIODefault, SIODefinition, \
    SIOList, SIOSkipEmpty, Text, UTC, UUID, Unicode
from zato.server.connection.mcp.schema import _default_elem_schema, _elem_class_to_json_schema, \
    _get_elem_json_schema, _python_annotation_to_schema, cy_sio_to_schema, dataclass_model_to_schema, \
    sio_to_json_schema

# ################################################################################################################################
# ################################################################################################################################

_not_given = InternalNotGiven

# ################################################################################################################################
# ################################################################################################################################

class _CustomElem(Elem):
    """ A user-defined Elem subclass not in the mapping, for testing default behavior.
    """
    def __cinit__(self):
        self._type = 1_000_000

# ################################################################################################################################

class _CustomTextSubclass(Text):
    """ A custom subclass of Text, for testing MRO-based lookup.
    """

# ################################################################################################################################
# ################################################################################################################################

def _make_sio_list(elems:'list[Elem]') -> 'SIOList':
    """ Creates a SIOList and initialises it the same way __cinit__ would in Cython.
    """
    sio_list = SIOList.__new__(SIOList)
    sio_list.elems = []
    sio_list.elems_by_name = {}

    if elems:
        sio_list.set_elems(elems)

    return sio_list

# ################################################################################################################################

def _make_definition_with_elems(
    required_elems:'list[Elem]',
    optional_elems:'list[Elem]',
    ) -> 'SIODefinition':
    """ Creates a SIODefinition with the given required and optional input elems.
    """
    sio_default = SIODefault(_not_given, _not_given, _not_given)
    skip_empty = SIOSkipEmpty(NotGiven, NotGiven, set(), set(), NotGiven)
    definition = SIODefinition(sio_default, skip_empty)

    # In pure Python, __cinit__ does not run so we need to initialise fields manually
    definition._input_required = _make_sio_list(required_elems)
    definition._input_optional = _make_sio_list(optional_elems)
    definition._output_required = _make_sio_list([])
    definition._output_optional = _make_sio_list([])

    definition.has_input_required = bool(required_elems)
    definition.has_input_optional = bool(optional_elems)
    definition.has_input_declared = bool(required_elems) or bool(optional_elems)

    definition.all_input_elem_names = []
    definition.all_output_elem_names = []
    definition.all_input_elems = []

    return definition

# ################################################################################################################################
# ################################################################################################################################

class ElemToJsonSchemaMapping(TestCase):
    """ Tests for the _elem_class_to_json_schema mapping dict.
    """

# ################################################################################################################################

    def test_as_is_maps_to_string(self):
        elem = AsIs('data')
        result = _get_elem_json_schema(elem)
        self.assertEqual(result, {'type': 'string'})

# ################################################################################################################################

    def test_bool_maps_to_boolean(self):
        elem = Bool('is_active')
        result = _get_elem_json_schema(elem)
        self.assertEqual(result, {'type': 'boolean'})

# ################################################################################################################################

    def test_csv_maps_to_string(self):
        elem = CSV('tags')
        result = _get_elem_json_schema(elem)
        self.assertEqual(result, {'type': 'string'})

# ################################################################################################################################

    def test_date_maps_to_string_date(self):
        elem = Date('created')
        result = _get_elem_json_schema(elem)
        self.assertEqual(result, {'type': 'string', 'format': 'date'})

# ################################################################################################################################

    def test_datetime_maps_to_string_datetime(self):
        elem = DateTime('timestamp')
        result = _get_elem_json_schema(elem)
        self.assertEqual(result, {'type': 'string', 'format': 'date-time'})

# ################################################################################################################################

    def test_decimal_maps_to_string(self):
        elem = Decimal('amount')
        result = _get_elem_json_schema(elem)
        self.assertEqual(result, {'type': 'string'})

# ################################################################################################################################

    def test_dict_maps_to_object(self):
        elem = Dict('config')
        result = _get_elem_json_schema(elem)
        self.assertEqual(result, {'type': 'object'})

# ################################################################################################################################

    def test_dictlist_maps_to_array_of_objects(self):
        elem = DictList('items')
        result = _get_elem_json_schema(elem)
        self.assertEqual(result, {'type': 'array', 'items': {'type': 'object'}})

# ################################################################################################################################

    def test_float_maps_to_number(self):
        elem = Float('price')
        result = _get_elem_json_schema(elem)
        self.assertEqual(result, {'type': 'number'})

# ################################################################################################################################

    def test_int_maps_to_integer(self):
        elem = Int('count')
        result = _get_elem_json_schema(elem)
        self.assertEqual(result, {'type': 'integer'})

# ################################################################################################################################

    def test_list_maps_to_array(self):
        elem = List('names')
        result = _get_elem_json_schema(elem)
        self.assertEqual(result, {'type': 'array'})

# ################################################################################################################################

    def test_secret_maps_to_string(self):
        elem = Secret('password')
        result = _get_elem_json_schema(elem)
        self.assertEqual(result, {'type': 'string'})

# ################################################################################################################################

    def test_text_maps_to_string(self):
        elem = Text('name')
        result = _get_elem_json_schema(elem)
        self.assertEqual(result, {'type': 'string'})

# ################################################################################################################################

    def test_utc_maps_to_string_datetime(self):
        elem = UTC('timestamp')
        result = _get_elem_json_schema(elem)
        self.assertEqual(result, {'type': 'string', 'format': 'date-time'})

# ################################################################################################################################

    def test_uuid_maps_to_string_uuid(self):
        elem = UUID('identifier')
        result = _get_elem_json_schema(elem)
        self.assertEqual(result, {'type': 'string', 'format': 'uuid'})

# ################################################################################################################################

    def test_boolean_alias_same_as_bool(self):
        self.assertIs(Boolean, Bool)
        self.assertIn(Bool, _elem_class_to_json_schema)

# ################################################################################################################################

    def test_integer_alias_same_as_int(self):
        self.assertIs(Integer, Int)
        self.assertIn(Int, _elem_class_to_json_schema)

# ################################################################################################################################

    def test_unicode_alias_same_as_text(self):
        self.assertIs(Unicode, Text)
        self.assertIn(Text, _elem_class_to_json_schema)

# ################################################################################################################################

    def test_opaque_alias_same_as_asis(self):
        self.assertIs(Opaque, AsIs)
        self.assertIn(AsIs, _elem_class_to_json_schema)

# ################################################################################################################################

    def test_listofdicts_alias_same_as_dictlist(self):
        self.assertIs(ListOfDicts, DictList)
        self.assertIn(DictList, _elem_class_to_json_schema)

# ################################################################################################################################

    def test_unknown_elem_subclass_uses_default(self):
        elem = _CustomElem('unknown_field')
        result = _get_elem_json_schema(elem)
        self.assertEqual(result, _default_elem_schema)

# ################################################################################################################################

    def test_custom_text_subclass_uses_mro(self):
        elem = _CustomTextSubclass('custom_name')
        result = _get_elem_json_schema(elem)
        self.assertEqual(result, {'type': 'string'})

# ################################################################################################################################

    def test_returned_dict_is_a_copy(self):
        elem = Int('count')
        result_1 = _get_elem_json_schema(elem)
        result_2 = _get_elem_json_schema(elem)
        self.assertIsNot(result_1, result_2)

# ################################################################################################################################
# ################################################################################################################################

class CySIOToSchema(TestCase):
    """ Tests for cy_sio_to_schema.
    """

# ################################################################################################################################

    def test_bare_string_elems_required_and_optional(self):
        definition = _make_definition_with_elems(
            required_elems=[Text('name'), Text('identifier')],
            optional_elems=[Text('email')],
        )
        result = cy_sio_to_schema(definition)

        self.assertEqual(result['type'], 'object')
        self.assertEqual(result['properties']['name'], {'type': 'string'})
        self.assertEqual(result['properties']['identifier'], {'type': 'string'})
        self.assertEqual(result['properties']['email'], {'type': 'string'})
        self.assertEqual(sorted(result['required']), ['identifier', 'name'])

# ################################################################################################################################

    def test_typed_elems(self):
        definition = _make_definition_with_elems(
            required_elems=[Int('age'), Bool('active')],
            optional_elems=[],
        )
        result = cy_sio_to_schema(definition)

        self.assertEqual(result['properties']['age'], {'type': 'integer'})
        self.assertEqual(result['properties']['active'], {'type': 'boolean'})
        self.assertEqual(sorted(result['required']), ['active', 'age'])

# ################################################################################################################################

    def test_mixed_required_and_optional(self):
        definition = _make_definition_with_elems(
            required_elems=[Int('identifier')],
            optional_elems=[Text('note'), List('tags')],
        )
        result = cy_sio_to_schema(definition)

        self.assertEqual(result['properties']['identifier'], {'type': 'integer'})
        self.assertEqual(result['properties']['note'], {'type': 'string'})
        self.assertEqual(result['properties']['tags'], {'type': 'array'})
        self.assertEqual(result['required'], ['identifier'])

# ################################################################################################################################

    def test_only_optional_input(self):
        definition = _make_definition_with_elems(
            required_elems=[],
            optional_elems=[Text('note')],
        )
        result = cy_sio_to_schema(definition)

        self.assertEqual(result['properties']['note'], {'type': 'string'})
        self.assertNotIn('required', result)

# ################################################################################################################################

    def test_no_input_declared(self):
        definition = _make_definition_with_elems(
            required_elems=[],
            optional_elems=[],
        )
        result = cy_sio_to_schema(definition)

        self.assertEqual(result, {'type': 'object'})

# ################################################################################################################################

    def test_date_datetime_uuid_decimal_elems(self):
        definition = _make_definition_with_elems(
            required_elems=[Date('birthday'), DateTime('created_at'), UUID('request_id'), Decimal('price')],
            optional_elems=[],
        )
        result = cy_sio_to_schema(definition)

        self.assertEqual(result['properties']['birthday'], {'type': 'string', 'format': 'date'})
        self.assertEqual(result['properties']['created_at'], {'type': 'string', 'format': 'date-time'})
        self.assertEqual(result['properties']['request_id'], {'type': 'string', 'format': 'uuid'})
        self.assertEqual(result['properties']['price'], {'type': 'string'})

# ################################################################################################################################

    def test_dictlist_elem(self):
        definition = _make_definition_with_elems(
            required_elems=[DictList('line_items')],
            optional_elems=[],
        )
        result = cy_sio_to_schema(definition)

        self.assertEqual(result['properties']['line_items'], {'type': 'array', 'items': {'type': 'object'}})

# ################################################################################################################################

    def test_dict_elem(self):
        definition = _make_definition_with_elems(
            required_elems=[Dict('metadata')],
            optional_elems=[],
        )
        result = cy_sio_to_schema(definition)

        self.assertEqual(result['properties']['metadata'], {'type': 'object'})

# ################################################################################################################################
# ################################################################################################################################

class DataclassModelToSchema(TestCase):
    """ Tests for dataclass_model_to_schema.
    """

# ################################################################################################################################

    def test_basic_types_all_required(self):

        @dataclasses.dataclass(init=False)
        class TestInput:
            name: str
            age: int
            active: bool

        result = dataclass_model_to_schema(TestInput)

        self.assertEqual(result['properties']['name'], {'type': 'string'})
        self.assertEqual(result['properties']['age'], {'type': 'integer'})
        self.assertEqual(result['properties']['active'], {'type': 'boolean'})
        self.assertEqual(sorted(result['required']), ['active', 'age', 'name'])

# ################################################################################################################################

    def test_field_with_default_not_required(self):

        @dataclasses.dataclass(init=False)
        class TestInput:
            email: str = ''

        result = dataclass_model_to_schema(TestInput)

        self.assertEqual(result['properties']['email'], {'type': 'string'})
        self.assertNotIn('required', result)

# ################################################################################################################################

    def test_optional_field_not_required(self):

        @dataclasses.dataclass(init=False)
        class TestInput:
            tags: list | None = None

        result = dataclass_model_to_schema(TestInput)

        self.assertEqual(result['properties']['tags'], {'type': 'array'})
        self.assertNotIn('required', result)

# ################################################################################################################################

    def test_datetime_field(self):

        @dataclasses.dataclass(init=False)
        class TestInput:
            created: stdlib_datetime

        result = dataclass_model_to_schema(TestInput)

        self.assertEqual(result['properties']['created'], {'type': 'string', 'format': 'date-time'})
        self.assertEqual(result['required'], ['created'])

# ################################################################################################################################

    def test_date_field(self):

        @dataclasses.dataclass(init=False)
        class TestInput:
            birthday: stdlib_date

        result = dataclass_model_to_schema(TestInput)

        self.assertEqual(result['properties']['birthday'], {'type': 'string', 'format': 'date'})

# ################################################################################################################################

    def test_decimal_field(self):

        @dataclasses.dataclass(init=False)
        class TestInput:
            amount: stdlib_Decimal

        result = dataclass_model_to_schema(TestInput)

        self.assertEqual(result['properties']['amount'], {'type': 'string'})
        self.assertEqual(result['required'], ['amount'])

# ################################################################################################################################

    def test_uuid_field(self):

        @dataclasses.dataclass(init=False)
        class TestInput:
            identifier: STDLIB_UUID

        result = dataclass_model_to_schema(TestInput)

        self.assertEqual(result['properties']['identifier'], {'type': 'string', 'format': 'uuid'})
        self.assertEqual(result['required'], ['identifier'])

# ################################################################################################################################

    def test_list_of_str(self):

        @dataclasses.dataclass(init=False)
        class TestInput:
            items: list[str]

        result = dataclass_model_to_schema(TestInput)

        self.assertEqual(result['properties']['items'], {'type': 'array', 'items': {'type': 'string'}})

# ################################################################################################################################

    def test_nested_dataclass(self):

        @dataclasses.dataclass(init=False)
        class TestAddress:
            street: str
            city: str

        @dataclasses.dataclass(init=False)
        class TestInput:
            address: TestAddress

        result = dataclass_model_to_schema(TestInput)

        address_schema = result['properties']['address']
        self.assertEqual(address_schema['type'], 'object')
        self.assertEqual(address_schema['properties']['street'], {'type': 'string'})
        self.assertEqual(address_schema['properties']['city'], {'type': 'string'})
        self.assertEqual(sorted(address_schema['required']), ['city', 'street'])

# ################################################################################################################################

    def test_empty_dataclass(self):

        @dataclasses.dataclass(init=False)
        class TestInput:
            pass

        result = dataclass_model_to_schema(TestInput)

        self.assertEqual(result, {'type': 'object'})

# ################################################################################################################################

    def test_default_factory_not_required(self):

        @dataclasses.dataclass(init=False)
        class TestInput:
            items: list = dc_field(default_factory=list)

        result = dataclass_model_to_schema(TestInput)

        self.assertEqual(result['properties']['items'], {'type': 'array'})
        self.assertNotIn('required', result)

# ################################################################################################################################

    def test_float_field(self):

        @dataclasses.dataclass(init=False)
        class TestInput:
            price: float

        result = dataclass_model_to_schema(TestInput)

        self.assertEqual(result['properties']['price'], {'type': 'number'})
        self.assertEqual(result['required'], ['price'])

# ################################################################################################################################

    def test_dict_field(self):

        @dataclasses.dataclass(init=False)
        class TestInput:
            metadata: dict

        result = dataclass_model_to_schema(TestInput)

        self.assertEqual(result['properties']['metadata'], {'type': 'object'})

# ################################################################################################################################
# ################################################################################################################################

class SIOToJsonSchemaDispatcher(TestCase):
    """ Tests for sio_to_json_schema top-level dispatcher.
    """

# ################################################################################################################################

    def test_no_sio_attribute(self):

        class ServiceWithoutSIO:
            pass

        result = sio_to_json_schema(ServiceWithoutSIO)

        self.assertEqual(result, {'type': 'object'})

# ################################################################################################################################

    def test_sio_is_none(self):

        class ServiceWithNoneSIO:
            _sio = None

        result = sio_to_json_schema(ServiceWithNoneSIO)

        self.assertEqual(result, {'type': 'object'})

# ################################################################################################################################

    def test_dataclass_sio_dispatch(self):

        @dataclasses.dataclass(init=False)
        class TestInput:
            name: str
            age: int

        # Build a real DataClassSimpleIO by using its attach_sio method
        class TestService:
            class SimpleIO:
                input = TestInput

        from zato.common.marshal_.simpleio import DataClassSimpleIO
        DataClassSimpleIO.attach_sio(None, None, TestService) # pyright: ignore[reportArgumentType]

        result = sio_to_json_schema(TestService)

        self.assertEqual(result['type'], 'object')
        self.assertIn('properties', result)
        self.assertIn('name', result['properties'])
        self.assertIn('age', result['properties'])

# ################################################################################################################################

    def test_unknown_sio_type(self):

        class UnknownSIO:
            pass

        class ServiceWithUnknownSIO:
            _sio = UnknownSIO()

        result = sio_to_json_schema(ServiceWithUnknownSIO)

        self.assertEqual(result, {'type': 'object'})

# ################################################################################################################################
# ################################################################################################################################

class PythonAnnotationToSchema(TestCase):
    """ Additional tests for _python_annotation_to_schema edge cases.
    """

# ################################################################################################################################

    def test_bare_list_no_type_param(self):
        result = _python_annotation_to_schema(list)
        self.assertEqual(result, {'type': 'array'})

# ################################################################################################################################

    def test_bare_dict_no_type_param(self):
        result = _python_annotation_to_schema(dict)
        self.assertEqual(result, {'type': 'object'})

# ################################################################################################################################

    def test_unknown_type_uses_default(self):

        class SomeCustomClass:
            pass

        result = _python_annotation_to_schema(SomeCustomClass)
        self.assertEqual(result, {'type': 'string'})

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
