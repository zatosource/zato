# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.util.message import has_content, Message

# ################################################################################################################################
# ################################################################################################################################

class TestVivification:
    """ Dot access builds the tree - reading a missing child creates and registers it.
    """

    def test_deep_chain_builds_the_whole_path(self):
        message = Message()
        message.order.customer.address.city = 'Reykjavik'

        assert message.order.customer.address.city == 'Reykjavik'

    def test_vivified_child_is_registered_in_the_parent(self):
        message = Message()
        child = message.order

        assert message.order is child

    def test_assignment_order_is_preserved(self):
        message = Message()
        message.customer = 'C-1001'
        message.item = 'AB-12'
        message.shipped = '2026-04-01'

        assert list(message._children) == ['customer', 'item', 'shipped']

    def test_underscore_names_raise_attribute_error(self):
        message = Message()

        with pytest.raises(AttributeError):
            _ = message._no_such_internal_field

    def test_subclass_vivifies_its_own_type(self):

        class OrderMessage(Message):
            pass

        message = OrderMessage()
        child = message.order.item

        assert isinstance(child, OrderMessage)

# ################################################################################################################################
# ################################################################################################################################

class TestContent:
    """ Content checks - nodes vivified by reads alone carry nothing.
    """

    def test_empty_message_has_no_content(self):
        message = Message()

        assert not message
        assert not has_content(message)

    def test_scalar_assignment_is_content(self):
        message = Message()
        message.customer = 'C-1001'

        assert message
        assert has_content(message)

    def test_vivified_only_node_is_not_content(self):
        message = Message()
        _ = message.order.customer

        assert not message

    def test_deep_assignment_is_content_all_the_way_up(self):
        message = Message()
        message.order.customer.name = 'Jane Doe'

        assert message
        assert message.order
        assert message.order.customer

    def test_list_with_content_counts(self):
        message = Message()
        message.item = ['first', 'second']

        assert message

    def test_list_of_empty_nodes_is_not_content(self):
        message = Message()
        message.item = [Message(), Message()]

        assert not message

# ################################################################################################################################
# ################################################################################################################################

class TestLen:
    """ Length counts only children with content.
    """

    def test_empty_message_has_length_zero(self):
        message = Message()

        assert len(message) == 0

    def test_assigned_children_count(self):
        message = Message()
        message.customer = 'C-1001'
        message.item = 'AB-12'

        assert len(message) == 2

    def test_vivified_only_children_do_not_count(self):
        message = Message()
        message.customer = 'C-1001'
        _ = message.order.item

        assert len(message) == 1

# ################################################################################################################################
# ################################################################################################################################

class TestToDict:
    """ Serialization to a plain dict - the shape assignments built, pruned of empty nodes.
    """

    def test_flat_fields(self):
        message = Message()
        message.customer = 'C-1001'
        message.quantity = 3

        assert message.to_dict() == {'customer': 'C-1001', 'quantity': 3}

    def test_nested_nodes_become_nested_dicts(self):
        message = Message()
        message.order.customer.name = 'Jane Doe'
        message.order.quantity = 3

        expected = {'order': {'customer': {'name': 'Jane Doe'}, 'quantity': 3}}
        assert message.to_dict() == expected

    def test_vivified_only_nodes_are_pruned(self):
        message = Message()
        message.customer = 'C-1001'
        _ = message.order.item

        assert message.to_dict() == {'customer': 'C-1001'}

    def test_empty_message_serializes_to_empty_dict(self):
        message = Message()

        assert message.to_dict() == {}

    def test_lists_of_scalars_pass_through(self):
        message = Message()
        message.item = ['first', 'second', 'third']

        assert message.to_dict() == {'item': ['first', 'second', 'third']}

    def test_lists_of_nodes_become_lists_of_dicts(self):
        first = Message()
        first.sku = 'AB-12'

        second = Message()
        second.sku = 'CD-34'

        message = Message()
        message.item = [first, second]

        assert message.to_dict() == {'item': [{'sku': 'AB-12'}, {'sku': 'CD-34'}]}

    def test_empty_nodes_in_lists_are_pruned(self):
        first = Message()
        first.sku = 'AB-12'

        message = Message()
        message.item = [first, Message()]

        assert message.to_dict() == {'item': [{'sku': 'AB-12'}]}

    def test_assignment_order_is_dict_order(self):
        message = Message()
        message.customer = 'C-1001'
        message.item = 'AB-12'
        message.shipped = '2026-04-01'

        assert list(message.to_dict()) == ['customer', 'item', 'shipped']

    def test_getvalue_returns_the_same_dict(self):
        message = Message()
        message.order.quantity = 3

        assert message.getvalue() == message.to_dict()

# ################################################################################################################################
# ################################################################################################################################

class TestRepr:
    """ The repr names the children without serializing them.
    """

    def test_repr_lists_child_names(self):
        message = Message()
        message.customer = 'C-1001'
        message.item = 'AB-12'

        assert repr(message) == "<Message children=['customer', 'item']>"

# ################################################################################################################################
# ################################################################################################################################

class TestImportSurface:
    """ The classes are importable from the one place user code sees.
    """

    def test_import_from_zato_common(self):
        from zato.common import Message as CommonMessage
        from zato.common import SOAPMessage as CommonSOAPMessage
        from zato.common import XMLMessage as CommonXMLMessage

        assert CommonMessage is Message
        assert issubclass(CommonXMLMessage, CommonMessage)
        assert issubclass(CommonSOAPMessage, CommonXMLMessage)

# ################################################################################################################################
# ################################################################################################################################
