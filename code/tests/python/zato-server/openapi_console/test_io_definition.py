# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from enum import Enum
from typing import Callable
from unittest import main, TestCase

# Zato
from zato.common.marshal_.api import Model
from zato.common.typing_ import decimal_, dict_, list_, optional, set_, strnone
from zato.server.openapi_console.spec import _io_definition

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class InvoiceStatus(Enum):
    Draft = 'draft'
    Issued = 'issued'

class Settings:
    pass

@dataclass(init=False)
class InvoiceItem(Model):
    description: str
    quantity: decimal_
    status: InvoiceStatus
    note: 'str | None' = None

@dataclass(init=False)
class Invoice(Model):
    invoice_number: str
    items: 'list_[InvoiceItem]'
    related: list_['Invoice']

# ################################################################################################################################
# ################################################################################################################################

def _get_definition(value:'any_') -> 'tuple[anydict, anydict]':
    """ Returns the definition of a service's input or output together with the models that it refers to.
    """
    models:'anydict' = {}
    definition = _io_definition(value, models)

    out = (definition, models)
    return out

# ################################################################################################################################
# ################################################################################################################################

class IODefinitionTestCase(TestCase):
    """ The input and output of deployed services, as the console's document reads them.
    """

    def test_no_input(self) -> 'None':
        definition, models = _get_definition(None)

        self.assertEqual(definition, {'type': 'any'})
        self.assertEqual(models, {})

    def test_a_model(self) -> 'None':
        definition, models = _get_definition(Invoice)

        self.assertEqual(definition, {'type': 'model', 'model_name': 'Invoice'})
        self.assertEqual(sorted(models), ['Invoice', 'InvoiceItem'])

    def test_a_model_with_a_decimal_and_an_enumeration(self) -> 'None':
        _, models = _get_definition(InvoiceItem)
        fields = models['InvoiceItem']['fields']

        self.assertEqual(fields['quantity']['type'], 'Decimal')
        self.assertEqual(fields['status']['type'], {'enum': ['draft', 'issued']})

    def test_a_model_that_refers_to_itself(self) -> 'None':
        _, models = _get_definition(Invoice)
        fields = models['Invoice']['fields']

        self.assertEqual(fields['related']['type'], {'container': 'list', 'element_type': 'Invoice'})

# ################################################################################################################################

    def test_a_list_of_models(self) -> 'None':
        definition, models = _get_definition(list_[InvoiceItem])

        self.assertEqual(definition, {'type': 'container', 'container_type': 'list', 'element_type': 'InvoiceItem'})
        self.assertIn('InvoiceItem', models)

    def test_a_list_of_optional_strings(self) -> 'None':
        definition, _ = _get_definition(list_[strnone])
        expected = {'type': 'container', 'container_type': 'list', 'element_type': {'type': 'str', 'optional': True}}

        self.assertEqual(definition, expected)

    def test_a_set_of_models(self) -> 'None':
        definition, models = _get_definition(set_[Invoice])

        self.assertEqual(definition, {'type': 'container', 'container_type': 'set', 'element_type': 'Invoice'})
        self.assertIn('Invoice', models)

    def test_a_dict_of_decimals(self) -> 'None':
        definition, _ = _get_definition(dict_[str, decimal_])
        self.assertEqual(definition, {'type': 'container', 'container_type': 'dict', 'element_type': 'Decimal'})

    def test_an_optional_model(self) -> 'None':
        definition, _ = _get_definition(optional[Invoice])
        self.assertEqual(definition, {'type': 'any'})

    def test_a_generic_other_than_a_container(self) -> 'None':
        definition, _ = _get_definition(Callable[[int], str])
        self.assertEqual(definition, {'type': 'any'})

# ################################################################################################################################

    def test_a_class_that_is_not_a_model(self) -> 'None':
        definition, models = _get_definition(Settings)

        self.assertEqual(definition, {'type': 'any'})
        self.assertEqual(models, {})

    def test_an_enumeration(self) -> 'None':
        definition, models = _get_definition(InvoiceStatus)

        self.assertEqual(definition, {'type': 'any'})
        self.assertEqual(models, {})

    def test_a_value_of_no_known_form(self) -> 'None':
        definition, _ = _get_definition(42)
        self.assertEqual(definition, {'type': 'any'})

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
