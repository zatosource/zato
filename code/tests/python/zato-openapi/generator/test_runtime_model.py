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
from zato.common.typing_ import decimal_, list_, list_field, strlist
from zato.openapi.generator.runtime_model import extract_model_fields_recursive, read_runtime_type

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, intanydict, strnone
    intanydict = intanydict
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

class InvoiceStatus(Enum):
    Draft = 'draft'
    Issued = 'issued'
    Paid = 'paid'

class Settings:
    pass

class Address:
    street: 'str'
    city: 'strnone'

# ################################################################################################################################

class Directory:
    """ A class that holds a model, which annotations refer to by a qualified name.
    """

    @dataclass(init=False)
    class Customer(Model):
        name: str
        email: 'strnone' = None

# ################################################################################################################################

@dataclass(init=False)
class InvoiceItem(Model):
    description: str
    quantity: decimal_
    unit_price: 'decimal_'
    discount: 'int | float'
    note: 'str | None' = None

@dataclass(init=False)
class Invoice(Model):
    invoice_number: str
    status: InvoiceStatus
    items: 'list_[InvoiceItem]'
    customer: 'Directory.Customer'
    billing_address: Address
    attributes: 'intanydict'
    tags: strlist = list_field()

# ################################################################################################################################

@dataclass(init=False)
class Category(Model):
    name: str
    parent: 'Category | None'
    subcategories: list_['Category']

@dataclass(init=False)
class Department(Model):
    name: str
    manager: 'Employee'

@dataclass(init=False)
class Employee(Model):
    name: str
    department: 'Department | None' = None

# ################################################################################################################################
# ################################################################################################################################

def _read(model_class:'type') -> 'anydict':
    """ Reads a model and the models that its fields refer to.
    """
    out:'anydict' = {}
    extract_model_fields_recursive(model_class, out)
    return out

# ################################################################################################################################
# ################################################################################################################################

class RuntimeModelTestCase(TestCase):
    """ The fields of models read at runtime, as the portal's document is built out of deployed services.
    """

    def test_the_models_that_fields_refer_to_are_read(self) -> 'None':
        models = _read(Invoice)
        self.assertEqual(sorted(models), ['Address', 'Customer', 'Invoice', 'InvoiceItem'])

    def test_the_models_are_listed_as_read_at_runtime(self) -> 'None':
        models = _read(Invoice)

        for model_def in models.values():
            self.assertEqual(model_def['file_path'], 'runtime')

# ################################################################################################################################

    def test_a_decimal_field(self) -> 'None':
        fields = _read(InvoiceItem)['InvoiceItem']['fields']
        self.assertEqual(fields['quantity']['type'], 'Decimal')

    def test_a_decimal_field_in_quotes(self) -> 'None':
        fields = _read(InvoiceItem)['InvoiceItem']['fields']
        self.assertEqual(fields['unit_price']['type'], 'decimal_')

    def test_a_union_in_quotes(self) -> 'None':
        fields = _read(InvoiceItem)['InvoiceItem']['fields']
        expected = {'type': 'union', 'container': 'union', 'union_types': ['int', 'float']}
        self.assertEqual(fields['discount']['type'], expected)

    def test_an_optional_field_in_quotes(self) -> 'None':
        fields = _read(InvoiceItem)['InvoiceItem']['fields']

        self.assertEqual(fields['note']['type'], {'type': 'str', 'optional': True})
        self.assertFalse(fields['note']['required'])
        self.assertIsNone(fields['note']['default'])

    def test_a_required_field(self) -> 'None':
        fields = _read(InvoiceItem)['InvoiceItem']['fields']

        self.assertEqual(fields['description']['type'], 'str')
        self.assertTrue(fields['description']['required'])

# ################################################################################################################################

    def test_an_enumeration_field(self) -> 'None':
        fields = _read(Invoice)['Invoice']['fields']
        self.assertEqual(fields['status']['type'], {'enum': ['draft', 'issued', 'paid']})

    def test_a_list_of_models_in_quotes(self) -> 'None':
        fields = _read(Invoice)['Invoice']['fields']
        self.assertEqual(fields['items']['type'], {'container': 'list', 'element_type': 'InvoiceItem'})

    def test_a_model_by_a_qualified_name(self) -> 'None':
        models = _read(Invoice)

        self.assertEqual(models['Invoice']['fields']['customer']['type'], 'Customer')
        self.assertEqual(models['Customer']['fields']['email']['type'], 'strnone')

    def test_a_class_with_annotated_attributes(self) -> 'None':
        models = _read(Invoice)

        self.assertEqual(models['Invoice']['fields']['billing_address']['type'], 'Address')
        self.assertEqual(models['Address']['fields']['city']['type'], 'strnone')
        self.assertTrue(models['Address']['fields']['city']['required'])

    def test_a_name_imported_for_type_checkers_only(self) -> 'None':
        fields = _read(Invoice)['Invoice']['fields']
        self.assertEqual(fields['attributes']['type'], {'container': 'dict', 'element_type': 'any_'})

    def test_a_field_with_a_default_factory(self) -> 'None':
        fields = _read(Invoice)['Invoice']['fields']

        self.assertEqual(fields['tags']['type'], {'container': 'list', 'element_type': 'str'})
        self.assertFalse(fields['tags']['required'])

# ################################################################################################################################

    def test_a_model_that_refers_to_itself(self) -> 'None':
        models = _read(Category)
        fields = models['Category']['fields']

        self.assertEqual(sorted(models), ['Category'])
        self.assertEqual(fields['parent']['type'], {'type': 'Category', 'optional': True})
        self.assertEqual(fields['subcategories']['type'], {'container': 'list', 'element_type': 'Category'})

    def test_models_that_refer_to_one_another(self) -> 'None':
        models = _read(Department)

        self.assertEqual(sorted(models), ['Department', 'Employee'])
        self.assertEqual(models['Department']['fields']['manager']['type'], 'Employee')
        self.assertEqual(models['Employee']['fields']['department']['type'], {'type': 'Department', 'optional': True})

# ################################################################################################################################

    def test_a_class_that_is_not_a_model(self) -> 'None':
        self.assertEqual(_read(Settings), {})

    def test_an_enumeration_is_not_read_as_a_model(self) -> 'None':
        self.assertEqual(_read(InvoiceStatus), {})

    def test_a_model_found_in_the_source_code_is_not_read_again(self) -> 'None':
        scanned_model = {'fields': {}, 'file_path': '/opt/services/invoices.py'}
        models:'anydict' = {'InvoiceItem': scanned_model}

        extract_model_fields_recursive(Invoice, models)

        self.assertIs(models['InvoiceItem'], scanned_model)
        self.assertIn('Invoice', models)

    def test_a_model_already_visited_is_not_read(self) -> 'None':
        models:'anydict' = {}
        extract_model_fields_recursive(Invoice, models, {'Invoice'})
        self.assertEqual(models, {})

# ################################################################################################################################

    def test_the_input_of_a_service_as_a_list_of_models(self) -> 'None':
        models:'anydict' = {}
        io_type = read_runtime_type(list_[Invoice], models)

        self.assertEqual(io_type, {'container': 'list', 'element_type': 'Invoice'})
        self.assertIn('Invoice', models)
        self.assertIn('InvoiceItem', models)

    def test_the_input_of_a_service_as_a_list_of_optional_strings(self) -> 'None':
        models:'anydict' = {}
        io_type = read_runtime_type(list_['str | None'], models)

        self.assertEqual(io_type, {'container': 'list', 'element_type': {'type': 'str', 'optional': True}})
        self.assertEqual(models, {})

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
