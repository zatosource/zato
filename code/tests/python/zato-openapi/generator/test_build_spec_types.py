# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from enum import Enum
from unittest import main, TestCase

# Zato
from zato.common.marshal_.api import Model
from zato.common.typing_ import decimal_, list_
from zato.openapi.generator import io_scanner, openapi_
from zato.openapi.generator.io_scanner import TypeConversionError, TypeMapper
from zato.openapi.generator.openapi_ import OpenAPIGenerator
from zato.openapi.generator.runtime_model import extract_model_fields_recursive

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from http.client import HTTPConnection
    from zato.common.typing_ import any_, anydict, anydictnone
    HTTPConnection = HTTPConnection

# ################################################################################################################################
# ################################################################################################################################

_json_media_type = 'application/json'

# The name of a model that the mapper below cannot map
_unmappable_model_name = 'Unmappable'

# ################################################################################################################################
# ################################################################################################################################

class InvoiceStatus(Enum):
    Draft = 'draft'
    Issued = 'issued'

@dataclass(init=False)
class InvoiceItem(Model):
    description: str
    quantity: decimal_
    status: InvoiceStatus
    connection: 'HTTPConnection'
    discount: 'int | float | None' = None

@dataclass(init=False)
class Category(Model):
    name: str
    parent: 'Category | None'
    subcategories: list_['Category']

# ################################################################################################################################
# ################################################################################################################################

class _UnmappableModelTypeMapper(TypeMapper):
    """ A mapper that cannot map one of the models, the way a model with an unsupported field is not mapped.
    """

    def map_type(self, zato_type:'any_', model_definitions:'anydictnone'=None) -> 'anydict':
        if zato_type == _unmappable_model_name:
            raise TypeConversionError(f'Model {_unmappable_model_name} cannot be mapped')

        out = super().map_type(zato_type, model_definitions)
        return out

# ################################################################################################################################
# ################################################################################################################################

def _get_entry(name:'str', url_path:'str', **entry_fields:'any_') -> 'anydict':
    """ Returns the entry of one service, as the console's document lists it.
    """
    out:'anydict' = {
        'name': name,
        'url_path': url_path,
        'http_method': 'post',
    }
    out.update(entry_fields)

    return out

# ################################################################################################################################

def _get_model_input(model_name:'str') -> 'anydict':
    """ Returns the definition of input that is a model.
    """
    out = {'type': 'model', 'model_name': model_name}
    return out

# ################################################################################################################################

def _get_container_io(container_type:'str', element_type:'any_') -> 'anydict':
    """ Returns the definition of input or output that is a container.
    """
    out = {'type': 'container', 'container_type': container_type, 'element_type': element_type}
    return out

# ################################################################################################################################

def _build_spec(entries:'any_', models:'anydict', type_mapper:'TypeMapper | None'=None) -> 'anydict':
    """ Builds a document out of the entries of services and the definitions of models.
    """
    if type_mapper is None:
        type_mapper = TypeMapper()

    generator = OpenAPIGenerator(type_mapper)
    out = generator.build_spec({'services': entries, 'models': models})

    return out

# ################################################################################################################################

def _read_models(*model_classes:'type') -> 'anydict':
    """ Reads models at runtime, the way the console's document reads the models of deployed services.
    """
    out:'anydict' = {}

    for model_class in model_classes:
        extract_model_fields_recursive(model_class, out)

    return out

# ################################################################################################################################
# ################################################################################################################################

class ServiceSkippedTestCase(TestCase):
    """ A service whose input cannot be mapped does not stop the document from being built.
    """

    def test_the_generator_catches_the_mapper_s_error(self) -> 'None':
        self.assertIs(openapi_.TypeConversionError, io_scanner.TypeConversionError)

    def test_the_other_services_are_documented(self) -> 'None':
        entries = [
            _get_entry('api.invoices.create', '/api/invoices', input=_get_model_input(_unmappable_model_name)),
            _get_entry('api.categories.create', '/api/categories', input=_get_model_input('Category')),
        ]

        models = _read_models(Category)
        spec = _build_spec(entries, models, _UnmappableModelTypeMapper())

        self.assertNotIn('requestBody', spec['paths']['/api/invoices']['post'])
        self.assertIn('requestBody', spec['paths']['/api/categories']['post'])

    def test_output_that_cannot_be_mapped(self) -> 'None':
        entries = [
            _get_entry('api.invoices.get', '/api/invoices/get', output=_get_model_input(_unmappable_model_name)),
        ]

        spec = _build_spec(entries, {}, _UnmappableModelTypeMapper())
        response = spec['paths']['/api/invoices/get']['post']['responses']['200']

        self.assertNotIn('content', response)

# ################################################################################################################################
# ################################################################################################################################

class ContainerIOTestCase(TestCase):
    """ Input and output of services that are containers of any kind that the mapper knows.
    """

    def test_a_list_of_models(self) -> 'None':
        models = _read_models(InvoiceItem)
        entries = [_get_entry('api.invoices.items', '/api/invoices/items', input=_get_container_io('list', 'InvoiceItem'))]

        spec = _build_spec(entries, models)
        content = spec['paths']['/api/invoices/items']['post']['requestBody']['content'][_json_media_type]

        self.assertEqual(content['schema'], {'type': 'array', 'items': {'$ref': '#/components/schemas/InvoiceItem'}})

    def test_a_set_of_strings(self) -> 'None':
        entries = [_get_entry('api.invoices.tags', '/api/invoices/tags', output=_get_container_io('set', 'str'))]

        spec = _build_spec(entries, {})
        content = spec['paths']['/api/invoices/tags']['post']['responses']['200']['content'][_json_media_type]

        self.assertEqual(content['schema'], {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True})

    def test_a_dict_of_decimals(self) -> 'None':
        entries = [_get_entry('api.invoices.totals', '/api/invoices/totals', output=_get_container_io('dict', 'Decimal'))]

        spec = _build_spec(entries, {})
        content = spec['paths']['/api/invoices/totals']['post']['responses']['200']['content'][_json_media_type]

        self.assertEqual(content['schema'], {'type': 'object', 'additionalProperties': {'type': 'number'}})

# ################################################################################################################################
# ################################################################################################################################

class RuntimeModelSpecTestCase(TestCase):
    """ Models read at runtime, documented end to end.
    """

    def _get_invoice_item_spec(self) -> 'anydict':
        """ Builds a document with one service whose input is an invoice item.
        """
        models = _read_models(InvoiceItem)
        entries = [_get_entry('api.invoices.items.create', '/api/invoices/items/create', input=_get_model_input('InvoiceItem'))]

        out = _build_spec(entries, models)
        return out

    def test_a_decimal_field(self) -> 'None':
        spec = self._get_invoice_item_spec()
        properties = spec['components']['schemas']['InvoiceItem']['properties']

        self.assertEqual(properties['quantity'], {'type': 'number'})

    def test_an_enumeration_field(self) -> 'None':
        spec = self._get_invoice_item_spec()
        properties = spec['components']['schemas']['InvoiceItem']['properties']

        self.assertEqual(properties['status'], {'enum': ['draft', 'issued'], 'type': 'string'})

    def test_the_example_of_an_enumeration_field_is_one_of_its_values(self) -> 'None':
        spec = self._get_invoice_item_spec()
        content = spec['paths']['/api/invoices/items/create']['post']['requestBody']['content'][_json_media_type]

        self.assertEqual(content['example']['status'], 'draft')

    def test_a_field_of_a_type_unknown_to_the_mapper(self) -> 'None':
        spec = self._get_invoice_item_spec()
        properties = spec['components']['schemas']['InvoiceItem']['properties']

        self.assertEqual(properties['connection'], {'description': 'Any type'})

    def test_an_optional_union_field(self) -> 'None':
        spec = self._get_invoice_item_spec()
        properties = spec['components']['schemas']['InvoiceItem']['properties']

        self.assertIn('anyOf', properties['discount'])
        self.assertEqual(properties['discount']['anyOf'][1], {'type': 'null'})

    def test_a_model_that_refers_to_itself(self) -> 'None':
        models = _read_models(Category)
        entries = [_get_entry('api.categories.create', '/api/categories', input=_get_model_input('Category'))]

        spec = _build_spec(entries, models)
        content = spec['paths']['/api/categories']['post']['requestBody']['content'][_json_media_type]
        properties = spec['components']['schemas']['Category']['properties']

        self.assertEqual(content['schema'], {'$ref': '#/components/schemas/Category'})
        self.assertEqual(properties['subcategories'], {'type': 'array', 'items': {'$ref': '#/components/schemas/Category'}})
        self.assertEqual(content['example']['subcategories'], [{}])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
