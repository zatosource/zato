# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.openapi.generator.basic_types import Any_Type_Schema, Basic_Types
from zato.openapi.generator.io_scanner import TypeConversionError, TypeMapper
from zato.openapi.generator.schemas import make_nullable

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anydictnone

# ################################################################################################################################
# ################################################################################################################################

_category_ref = {'$ref': '#/components/schemas/Category'}

# ################################################################################################################################
# ################################################################################################################################

def _map(zato_type:'any_', model_definitions:'anydictnone'=None) -> 'anydict':
    """ Maps a type with a mapper of its own.
    """
    mapper = TypeMapper()
    out = mapper.map_type(zato_type, model_definitions)
    return out

# ################################################################################################################################

def _get_category_models() -> 'anydict':
    """ Returns the definition of a model that refers to itself, as the runtime reader produces it.
    """
    out = {
        'Category': {
            'file_path': 'runtime',
            'fields': {
                'name': {'type': 'str', 'default': None, 'required': True},
                'parent': {'type': {'type': 'Category', 'optional': True}, 'default': None, 'required': False},
                'subcategories': {'type': {'container': 'list', 'element_type': 'Category'}, 'default': None, 'required': True},
            },
        },
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class NameMappingTestCase(TestCase):
    """ Names of types that the mapper knows, of models and of types defined elsewhere.
    """

    def test_a_decimal(self) -> 'None':
        self.assertEqual(_map('Decimal'), {'type': 'number'})
        self.assertEqual(_map('decimal_'), {'type': 'number'})

    def test_a_uuid(self) -> 'None':
        self.assertEqual(_map('UUID'), {'type': 'string', 'format': 'uuid'})

    def test_a_name_unknown_to_the_mapper(self) -> 'None':
        self.assertEqual(_map('LibraryClient'), Any_Type_Schema)

    def test_a_value_of_any_type(self) -> 'None':
        self.assertEqual(_map('any_'), Any_Type_Schema)

    def test_the_schemas_returned_are_copies(self) -> 'None':
        schema = _map('str')
        schema['format'] = 'email'

        self.assertEqual(Basic_Types['str'], {'type': 'string'})

    def test_a_definition_of_no_known_form(self) -> 'None':
        self.assertEqual(_map({'type': 'callable'}), Any_Type_Schema)

# ################################################################################################################################
# ################################################################################################################################

class EnumMappingTestCase(TestCase):
    """ Enumerations and literals.
    """

    def test_values_of_one_type(self) -> 'None':
        self.assertEqual(_map({'enum': ['open', 'closed']}), {'enum': ['open', 'closed'], 'type': 'string'})

    def test_values_of_several_types(self) -> 'None':
        self.assertEqual(_map({'enum': ['up', 2]}), {'enum': ['up', 2], 'type': ['string', 'integer']})

    def test_values_that_include_none(self) -> 'None':
        self.assertEqual(_map({'enum': [1, None]}), {'enum': [1, None], 'type': ['integer', 'null']})

# ################################################################################################################################
# ################################################################################################################################

class OptionalAndUnionMappingTestCase(TestCase):
    """ Optional types and unions.
    """

    def test_an_optional_decimal(self) -> 'None':
        self.assertEqual(_map({'type': 'Decimal', 'optional': True}), {'type': ['number', 'null']})

    def test_an_optional_type_that_is_nullable_already(self) -> 'None':
        self.assertEqual(_map({'type': 'strnone', 'optional': True}), {'type': ['string', 'null']})

    def test_an_optional_none(self) -> 'None':
        self.assertEqual(_map({'type': 'NoneType', 'optional': True}), {'type': 'null'})

    def test_an_optional_value_of_any_type(self) -> 'None':
        self.assertEqual(_map({'type': 'any_', 'optional': True}), {'anyOf': [Any_Type_Schema, {'type': 'null'}]})

    def test_a_union(self) -> 'None':
        union = {'type': 'union', 'container': 'union', 'union_types': ['int', 'float']}
        self.assertEqual(_map(union), {'oneOf': [Basic_Types['int'], Basic_Types['float']]})

    def test_an_optional_union(self) -> 'None':
        union = {'type': 'union', 'container': 'union', 'union_types': ['int', 'float']}
        one_of = {'oneOf': [Basic_Types['int'], Basic_Types['float']]}

        self.assertEqual(_map({'type': union, 'optional': True}), {'anyOf': [one_of, {'type': 'null'}]})

    def test_a_union_with_a_model_that_cannot_be_mapped(self) -> 'None':
        models:'anydict' = {'Invoice': {}}
        union = {'type': 'union', 'container': 'union', 'union_types': ['str', 'Invoice']}

        self.assertEqual(_map(union, models), {'oneOf': [Basic_Types['str']]})

# ################################################################################################################################
# ################################################################################################################################

class ContainerMappingTestCase(TestCase):
    """ Lists, sets, tuples and dicts.
    """

    def test_a_list(self) -> 'None':
        self.assertEqual(_map({'container': 'list', 'element_type': 'Decimal'}), {'type': 'array', 'items': {'type': 'number'}})

    def test_a_list_of_optional_elements(self) -> 'None':
        container = {'container': 'list', 'element_type': {'type': 'str', 'optional': True}}
        self.assertEqual(_map(container), {'type': 'array', 'items': {'type': ['string', 'null']}})

    def test_a_tuple(self) -> 'None':
        self.assertEqual(_map({'container': 'tuple', 'element_type': 'int'}), {'type': 'array', 'items': Basic_Types['int']})

    def test_a_set(self) -> 'None':
        expected = {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True}
        self.assertEqual(_map({'container': 'set', 'element_type': 'str'}), expected)

    def test_a_dict_of_values_of_one_type(self) -> 'None':
        expected = {'type': 'object', 'additionalProperties': {'type': 'number'}}
        self.assertEqual(_map({'container': 'dict', 'element_type': 'Decimal'}), expected)

    def test_a_dict_of_values_of_any_type(self) -> 'None':
        self.assertEqual(_map({'container': 'dict', 'element_type': 'any_'}), {'type': 'object'})

    def test_a_container_named_the_way_annotations_name_it(self) -> 'None':
        self.assertEqual(_map({'container': 'list_', 'element_type': 'str'}), {'type': 'array', 'items': {'type': 'string'}})

    def test_a_container_of_an_unknown_kind(self) -> 'None':
        self.assertEqual(_map({'container': 'deque', 'element_type': 'str'}), Any_Type_Schema)

# ################################################################################################################################
# ################################################################################################################################

class ModelMappingTestCase(TestCase):
    """ Models registered as schema components.
    """

    def test_a_model_that_refers_to_itself(self) -> 'None':
        mapper = TypeMapper()
        models = _get_category_models()

        schema = mapper.map_type('Category', models)
        components = mapper.get_schema_components()
        properties = components['Category']['properties']

        self.assertEqual(schema, _category_ref)
        self.assertEqual(properties['parent'], {'anyOf': [_category_ref, {'type': 'null'}]})
        self.assertEqual(properties['subcategories'], {'type': 'array', 'items': _category_ref})
        self.assertEqual(components['Category']['required'], ['name', 'subcategories'])

    def test_a_model_with_a_decimal_field(self) -> 'None':
        mapper = TypeMapper()
        models = {
            'InvoiceItem': {
                'file_path': 'runtime',
                'fields': {
                    'quantity': {'type': 'Decimal', 'default': None, 'required': True},
                    'currency': {'type': 'str', 'default': 'USD', 'required': False},
                },
            },
        }

        _ = mapper.map_type('InvoiceItem', models)
        properties = mapper.get_schema_components()['InvoiceItem']['properties']

        self.assertEqual(properties['quantity'], {'type': 'number'})
        self.assertEqual(properties['currency'], {'type': 'string', 'default': 'USD'})

    def test_a_model_without_a_definition_is_not_registered(self) -> 'None':
        mapper = TypeMapper()
        models:'anydict' = {'Invoice': {}}

        with self.assertRaises(TypeConversionError):
            _ = mapper.map_type('Invoice', models)

        self.assertNotIn('Invoice', mapper.registered_models)
        self.assertNotIn('Invoice', mapper.get_schema_components())

# ################################################################################################################################
# ################################################################################################################################

class NullableSchemaTestCase(TestCase):
    """ Schemas that accept null too.
    """

    def test_a_plain_schema(self) -> 'None':
        self.assertEqual(make_nullable({'type': 'string'}), {'type': ['string', 'null']})

    def test_a_schema_with_a_list_of_types(self) -> 'None':
        self.assertEqual(make_nullable({'type': ['string', 'integer']}), {'type': ['string', 'integer', 'null']})

    def test_a_schema_that_accepts_null_already(self) -> 'None':
        self.assertEqual(make_nullable({'type': ['string', 'null']}), {'type': ['string', 'null']})
        self.assertEqual(make_nullable({'type': 'null'}), {'type': 'null'})

    def test_a_reference(self) -> 'None':
        self.assertEqual(make_nullable(_category_ref), {'anyOf': [_category_ref, {'type': 'null'}]})

    def test_the_schema_given_is_not_changed(self) -> 'None':
        schema = {'type': 'string'}
        _ = make_nullable(schema)

        self.assertEqual(schema, {'type': 'string'})

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
