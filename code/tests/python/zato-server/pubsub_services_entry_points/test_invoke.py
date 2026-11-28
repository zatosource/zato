# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The reference of every other entry point is what self.invoke produces, so its records and responses are checked
# here against the values that the canonical requests must lead to.

# Zato
from zato.common.api import CHANNEL
from zato.common.test.service_entry_points.models import RecordKey

# Service entry points
from service_entry_points.compare import assert_same_invocation, normalize
from service_entry_points.requests import All_Targets, Free_Form_Target, HL7, HL7_Target, Kind, Model_Target, new_request_id, \
    Typed_Target

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import Suite
    from service_entry_points.compare import references_dict

    Suite = Suite

# ################################################################################################################################
# ################################################################################################################################

# The request ID in a normalized record or response
_request_id = '{request_id}'

_address_snapshot = {
    'city': ['str', 'Springfield'],
    'postal_code': ['str', '62701'],
    'street': ['str', '100 Main Street'],
}

_tags_snapshot = [['str', 'express'], ['str', 'fragile']]

# ################################################################################################################################

_typed_input = {
    'request_id': ['str', _request_id],
    'quantity': ['int', '3'],
    'is_priority': ['bool', 'True'],
    'weight': ['float', '2.5'],
    'unit_price': ['Decimal', '19.99'],
    'ship_date': ['str', '2026-12-01'],
    'ordered_at': ['str', '2026-11-28T10:15:00'],
    'order_id': ['str', '7c9e6679-7425-40de-944b-e07fc1f90ae7'],
    'tags': _tags_snapshot,
    'address': _address_snapshot,
    'customer_name': ['str', 'John Smith'],
    'has_gift_wrap': ['bool', 'False'],
    'item_count': ['int', '2'],
    'notes': ['NoneType', 'None'],
}

_typed_result = {
    'order_id': '7c9e6679-7425-40de-944b-e07fc1f90ae7',
    'customer_name': 'John Smith',
    'total': '59.97',
    'shipping_weight': '7.5',
    'is_priority': 'True',
    'has_gift_wrap': 'False',
    'item_count': '2',
    'ship_date': '2026-12-01',
    'ordered_at': '2026-11-28T10:15:00',
    'tags': 'express fragile',
    'city': 'Springfield',
    'notes': 'None',
}

# ################################################################################################################################

_model_input = {
    'model': 'Order',
    'fields': {
        'request_id': ['str', _request_id],
        'order_number': ['str', 'PO-2026-0042'],
        'priority': ['int', '2'],
        'ship_date': ['date', '2026-12-01'],
        'ordered_at': ['datetime', '2026-11-28 10:15:00'],
        'address': {
            'model': 'Address',
            'fields': _address_snapshot,
        },
        'items': [
            {'model': 'OrderItem', 'fields': {'sku': ['str', 'SKU-BOOK-001'], 'quantity': ['int', '2']}},
            {'model': 'OrderItem', 'fields': {'sku': ['str', 'SKU-TONER-007'], 'quantity': ['int', '5']}},
        ],
        'notes': ['NoneType', 'None'],
    },
}

_model_result = {
    'order_number': 'PO-2026-0042',
    'priority': '2',
    'ship_date': '2026-12-01',
    'ordered_at': '2026-11-28T10:15:00',
    'city': 'Springfield',
    'skus': 'SKU-BOOK-001 SKU-TONER-007',
    'total_quantity': '7',
    'notes': 'None',
}

# ################################################################################################################################

_free_form_input = {
    'request_id': ['str', _request_id],
    'customer_name': ['str', 'John Smith'],
    'segment': ['str', 'enterprise'],
    'address': _address_snapshot,
    'tags': _tags_snapshot,
}

_free_form_result = {
    'customer_name': 'John Smith',
    'segment': 'enterprise',
    'city': 'Springfield',
    'tags': 'express fragile',
    'field_count': '5',
}

# ################################################################################################################################

# The sender and the receiver of the message change places in the acknowledgment
_hl7_result = HL7.Segment_Separator.join([
    f'MSH|^~\\&|LAB_SYSTEM|CENTRAL_LAB|{HL7.Sending_App}|GENERAL_HOSPITAL|20261128101500||ACK|{_request_id}|P|2.5',
    f'MSA|AA|{_request_id}',
])

# ################################################################################################################################

_expected = {
    Kind.Typed: (_typed_input, _typed_result),
    Kind.Model: (_model_input, _model_result),
    Kind.Free_Form: (_free_form_input, _free_form_result),
}

# ################################################################################################################################
# ################################################################################################################################

def _assert_reference(references:'references_dict', kind:'str') -> 'None':
    """ Fails unless the reference of a service holds what its canonical request must lead to.
    """
    expected_input, expected_result = _expected[kind]
    reference = references[kind]

    record = normalize(reference.record, reference.request_id)
    response = normalize(reference.response, reference.request_id)

    assert record[RecordKey.Channel_Type] == CHANNEL.INVOKE, record
    assert record[RecordKey.Input] == expected_input, record
    assert record[RecordKey.Result] == expected_result, record
    assert response == expected_result, response

# ################################################################################################################################
# ################################################################################################################################

def test_typed(references:'references_dict') -> 'None':
    """ Every declared type of the typed service converts the value that the request carries.
    """
    _assert_reference(references, Typed_Target.kind)

# ################################################################################################################################

def test_model(references:'references_dict') -> 'None':
    """ The model service receives its request as a model with a nested model and a list of models.
    """
    _assert_reference(references, Model_Target.kind)

# ################################################################################################################################

def test_free_form(references:'references_dict') -> 'None':
    """ The free-form service receives its request as it was sent.
    """
    _assert_reference(references, Free_Form_Target.kind)

# ################################################################################################################################

def test_hl7(references:'references_dict') -> 'None':
    """ The HL7 service acknowledges the message it parsed.
    """
    reference = references[HL7_Target.kind]

    record = normalize(reference.record, reference.request_id)
    response = normalize(reference.response, reference.request_id)

    assert record[RecordKey.Channel_Type] == CHANNEL.INVOKE, record
    assert record[RecordKey.Result] == _hl7_result, record
    assert response == _hl7_result, response

# ################################################################################################################################

def test_repeated(suite:'Suite', references:'references_dict') -> 'None':
    """ A second invocation of each service through self.invoke equals the first one.
    """
    for target in All_Targets:
        request_id = new_request_id()
        response = suite.invoke(target, request_id)

        assert_same_invocation(references[target.kind], suite.client, request_id, response, 'self.invoke')

# ################################################################################################################################
# ################################################################################################################################
