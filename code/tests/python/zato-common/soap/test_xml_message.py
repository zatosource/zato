# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode
from datetime import date

# lxml
from lxml import etree

# pytest
import pytest

# Zato
from zato.common.util.xml_.core import XMLException
from zato.common.util.xml_.message import parse, serialize, XMLMessage

# ################################################################################################################################
# ################################################################################################################################

# A generic, non-SOAP namespace - the base class knows nothing about envelopes.
_ns_order = 'urn:example:order'
_ns_invoice = 'urn:example:invoice'

# ################################################################################################################################
# ################################################################################################################################

def _roundtrip(message, tag, default_namespace=None):
    """ Serializes a message and parses the resulting wire bytes back.
    """
    element = serialize(message, tag, default_namespace)
    data = etree.tostring(element)

    out = parse(data)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestGenericDocuments:
    """ Plain XML documents built and read through the base class - no SOAP anywhere.
    """

    def test_build_and_roundtrip(self):
        order = XMLMessage()
        order.namespace = _ns_order

        order.customer = 'C-1001'
        order.item.sku = 'AB-12'
        order.item.quantity = 3
        order.shipped = date(2026, 4, 1)

        result = _roundtrip(order, 'order')

        assert result.customer == 'C-1001'
        assert result.item.sku == 'AB-12'
        assert result.item.quantity == '3'
        assert result.shipped == '2026-04-01'

    def test_attributes_and_text(self):
        order = XMLMessage()

        order.total['currency'] = 'EUR'
        order.total['text'] = '129.95'

        element = serialize(order, 'order')

        total = element[0]
        assert total.get('currency') == 'EUR'
        assert total.text == '129.95'

    def test_repeated_elements(self):
        order = XMLMessage()
        order.item = ['first', 'second', 'third']

        result = _roundtrip(order, 'order')

        assert result.item == ['first', 'second', 'third']

    def test_none_is_xsi_nil(self):
        order = XMLMessage()
        order.discount = None

        result = _roundtrip(order, 'order')

        assert result.discount is None

    def test_bytes_are_inline_base64(self):
        payload = b'PDF-BYTES'

        order = XMLMessage()
        order.attachment = payload

        element = serialize(order, 'order')

        assert element[0].text == b64encode(payload).decode('ascii')

    def test_unsupported_type_is_rejected(self):
        order = XMLMessage()
        order.value = object()

        with pytest.raises(XMLException):
            _ = serialize(order, 'order')

# ################################################################################################################################
# ################################################################################################################################

class TestNamespaceRules:
    """ The five per-element namespace rules the module documents.
    """

    def test_message_wide_default_is_inherited(self):
        order = XMLMessage()
        order.namespace = _ns_order
        order.item.sku = 'AB-12'

        element = serialize(order, 'order')

        assert element.tag == f'{{{_ns_order}}}order'
        assert element[0].tag == f'{{{_ns_order}}}item'
        assert element[0][0].tag == f'{{{_ns_order}}}sku'

    def test_per_element_override_reroots_the_subtree(self):
        order = XMLMessage()
        order.namespace = _ns_order

        order.customer = 'C-1001'
        order.invoice['namespace'] = _ns_invoice
        order.invoice.number = 'INV-7'

        element = serialize(order, 'order')

        # The sibling keeps inheriting while the override covers its whole subtree.
        assert element[0].tag == f'{{{_ns_order}}}customer'
        assert element[1].tag == f'{{{_ns_invoice}}}invoice'
        assert element[1][0].tag == f'{{{_ns_invoice}}}number'

    def test_serialize_time_default_applies_only_without_own(self):
        order = XMLMessage()
        order.customer = 'C-1001'

        element = serialize(order, 'order', default_namespace=_ns_order)
        assert element.tag == f'{{{_ns_order}}}order'

        # A message with its own namespace ignores the caller-provided default.
        order.namespace = _ns_invoice
        element = serialize(order, 'order', default_namespace=_ns_order)
        assert element.tag == f'{{{_ns_invoice}}}order'

    def test_no_namespace_serializes_unqualified(self):
        order = XMLMessage()
        order.customer = 'C-1001'

        element = serialize(order, 'order')

        assert element.tag == 'order'
        assert element[0].tag == 'customer'

# ################################################################################################################################
# ################################################################################################################################

class _Order(XMLMessage):
    """ A subclass standing in for what SOAPMessage is to the base class.
    """

# ################################################################################################################################
# ################################################################################################################################

class TestSubclassing:
    """ The two behaviors only a subclass can show - vivification of its own type
    and parsing into a caller-chosen node type.
    """

    def test_subclass_vivifies_its_own_type(self):
        order = _Order()

        node = order.item.details

        assert type(node) is _Order
        assert type(order.item) is _Order

    def test_parse_produces_the_requested_subclass(self):
        data = (
            b'<order>'
            b'<item code="AB-12"><quantity>3</quantity></item>'
            b'<item code="CD-34"><quantity>5</quantity></item>'
            b'</order>'
        )

        result = parse(data, message_class=_Order)

        # The subclass holds throughout the tree, including list members.
        assert type(result) is _Order
        assert type(result.item[0]) is _Order
        assert type(result.item[1]) is _Order

        assert result.item[0]['code'] == 'AB-12'
        assert result.item[1].quantity == '5'

    def test_parse_defaults_to_the_base_class(self):
        data = b'<order><customer>C-1001</customer></order>'

        result = parse(data)

        assert type(result) is XMLMessage

# ################################################################################################################################
# ################################################################################################################################
