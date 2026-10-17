# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ast
from unittest import main, TestCase

# Zato
from zato.openapi.generator.io_scanner import IOVisitor

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_source = """
from dataclasses import dataclass
from zato.common.typing_ import decimal_, list_, optional
from zato.server.service import Model, Service

@dataclass(init=False)
class InvoiceItem(Model):
    description: str
    quantity: decimal_
    discount: int | float
    note: str | None
    reference: 'optional[str]'
    currency: str = 'USD'

@dataclass(init=False)
class Invoice(Model):
    invoice_number: str
    items: 'list_[InvoiceItem]'
    related: list_['Invoice']
    attributes: dict_[str, decimal_]
    tags: set_[str]
    status: Literal['draft', 'issued']
    total: decimal.Decimal

class CreateInvoice(Service):
    name = 'api.invoices.create'
    input = Invoice
    output = 'invoice_number'

class CreateInvoiceItems(Service):
    name = 'api.invoices.items.create'
    input = list_[InvoiceItem]
    output = set_[str]

class GetInvoiceTotals(Service):
    name = 'api.invoices.totals.get'
    input = optional[Invoice]
    output = dict_[str, decimal_]
"""

# ################################################################################################################################
# ################################################################################################################################

def _visit() -> 'IOVisitor':
    """ Visits the source code of the services and models above.
    """
    out = IOVisitor()
    out.visit(ast.parse(_source))

    return out

# ################################################################################################################################

def _get_service(name:'str') -> 'anydict':
    """ Returns the definition of one of the services above.
    """
    visitor = _visit()

    for service in visitor.services:
        if service['name'] == name:
            out = service
            break
    else:
        raise KeyError(name)

    return out

# ################################################################################################################################
# ################################################################################################################################

class ModelFieldAnnotationTestCase(TestCase):
    """ The fields of models in scanned source code, which is parsed and not imported.
    """

    def test_a_plain_type(self) -> 'None':
        fields = _visit().models['InvoiceItem']
        self.assertEqual(fields['description']['type'], 'str')
        self.assertEqual(fields['quantity']['type'], 'decimal_')

    def test_a_union(self) -> 'None':
        fields = _visit().models['InvoiceItem']
        self.assertEqual(fields['discount']['type'], {'type': 'union', 'container': 'union', 'union_types': ['int', 'float']})

    def test_an_optional_type_with_a_vertical_bar(self) -> 'None':
        fields = _visit().models['InvoiceItem']
        self.assertEqual(fields['note']['type'], {'type': 'str', 'optional': True})

    def test_an_optional_type_in_quotes(self) -> 'None':
        fields = _visit().models['InvoiceItem']
        self.assertEqual(fields['reference']['type'], {'type': 'str', 'optional': True})

    def test_a_list_of_models_in_quotes(self) -> 'None':
        fields = _visit().models['Invoice']
        self.assertEqual(fields['items']['type'], {'container': 'list', 'element_type': 'InvoiceItem'})

    def test_a_list_of_a_model_in_quotes(self) -> 'None':
        fields = _visit().models['Invoice']
        self.assertEqual(fields['related']['type'], {'container': 'list', 'element_type': 'Invoice'})

    def test_a_dict(self) -> 'None':
        fields = _visit().models['Invoice']
        self.assertEqual(fields['attributes']['type'], {'container': 'dict', 'element_type': 'decimal_'})

    def test_a_set(self) -> 'None':
        fields = _visit().models['Invoice']
        self.assertEqual(fields['tags']['type'], {'container': 'set', 'element_type': 'str'})

    def test_a_literal(self) -> 'None':
        fields = _visit().models['Invoice']
        self.assertEqual(fields['status']['type'], {'enum': ['draft', 'issued']})

    def test_a_qualified_name(self) -> 'None':
        fields = _visit().models['Invoice']
        self.assertEqual(fields['total']['type'], 'Decimal')

# ################################################################################################################################

    def test_a_field_without_a_default(self) -> 'None':
        fields = _visit().models['InvoiceItem']
        self.assertTrue(fields['description']['required'])

    def test_a_container_field_without_a_default(self) -> 'None':
        fields = _visit().models['Invoice']
        self.assertTrue(fields['items']['required'])

    def test_a_field_that_accepts_none(self) -> 'None':
        fields = _visit().models['InvoiceItem']
        self.assertFalse(fields['note']['required'])

    def test_a_field_with_a_default(self) -> 'None':
        fields = _visit().models['InvoiceItem']

        self.assertFalse(fields['currency']['required'])
        self.assertEqual(fields['currency']['default'], 'USD')

# ################################################################################################################################
# ################################################################################################################################

class ServiceIOAnnotationTestCase(TestCase):
    """ The input and output of services in scanned source code.
    """

    def test_a_model(self) -> 'None':
        service = _get_service('api.invoices.create')
        self.assertEqual(service['input'], {'type': 'model', 'model_name': 'Invoice'})

    def test_a_string(self) -> 'None':
        service = _get_service('api.invoices.create')
        self.assertEqual(service['output']['type'], 'string')
        self.assertEqual(service['output']['name'], 'invoice_number')

    def test_a_list_of_models(self) -> 'None':
        service = _get_service('api.invoices.items.create')
        self.assertEqual(service['input'], {'type': 'container', 'container_type': 'list', 'element_type': 'InvoiceItem'})

    def test_a_set(self) -> 'None':
        service = _get_service('api.invoices.items.create')
        self.assertEqual(service['output'], {'type': 'container', 'container_type': 'set', 'element_type': 'str'})

    def test_a_dict(self) -> 'None':
        service = _get_service('api.invoices.totals.get')
        self.assertEqual(service['output'], {'type': 'container', 'container_type': 'dict', 'element_type': 'decimal_'})

    def test_an_optional_model(self) -> 'None':
        service = _get_service('api.invoices.totals.get')
        self.assertEqual(service['input'], {'type': 'any'})

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
