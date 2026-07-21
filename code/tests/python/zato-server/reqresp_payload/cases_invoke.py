# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The invoke-only cases - what one service passes to another and what it receives
back, in both directions, with no wire in between.
"""

# stdlib
from datetime import datetime

# Bunch
from zato.common.ext.bunch import Bunch

# Zato
from zato.common.api import DATA_FORMAT

# Test corpus
from cases import case_list, CorpusService, FreeFormDetailsService, make_case, NoResponseService, OrderStatus, \
    OrderSubtreeService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from unittest import TestCase
    from zato.common.typing_ import any_, anydict
    anydict = anydict
    TestCase = TestCase

# ################################################################################################################################
# ################################################################################################################################

class CaptureRequestService(CorpusService):
    """ Stores what its request objects carry so the caller's side can assert on them.
    """
    _Service__service_name = 'orders.capture-request'
    _Service__service_impl_name = 'orders.api.CaptureRequestService'

    captured:'anydict' = {}

    def handle(self) -> 'None':
        captured = CaptureRequestService.captured
        captured['payload'] = self.request.payload
        captured['input'] = self.request.input
        captured['raw'] = self.request.raw

# ################################################################################################################################

class AssignedModelService(CorpusService):
    """ Assigns a whole model instance to the payload - with the JSON data format
    it is stored and returned as its dict form.
    """
    _Service__service_name = 'orders.assigned-model'
    _Service__service_impl_name = 'orders.api.AssignedModelService'

    def handle(self) -> 'None':

        order = OrderStatus.__new__(OrderStatus)
        order.customer_id = 'C-1001'
        order.status = 'confirmed'

        self.response.payload = order

# ################################################################################################################################

# A response dict with a value that would not survive JSON serialization -
# through invoke the caller receives the very same object, datetime included.
_report_response = {'name': 'quarterly-report', 'generated_at': datetime(2026, 7, 21, 9, 30, 0)}

class ReportDictService(CorpusService):
    """ Assigns a module-level dict to the payload - the caller receives that very object.
    """
    _Service__service_name = 'reports.dict-identity'
    _Service__service_impl_name = 'reports.api.ReportDictService'

    def handle(self) -> 'None':
        self.response.payload = _report_response

# ################################################################################################################################
# ################################################################################################################################

_order_request = {'customer_id': 'C-1001', 'items': [{'product_id': 'P-01', 'quantity': 2}]}
_order_request_json = '{"customer_id": "C-1001", "status": "confirmed"}'
_edifact_request = "UNB+UNOC:3+SENDER+RECIPIENT+260721:0930+REF-0002'UNZ+0+REF-0002'"

# ################################################################################################################################

def verify_dict_payload_is_the_same_object(test:'TestCase', result:'any_') -> 'None':
    """ A dict payload reaches the target as the very same object - nothing
    is serialized in between, so nested values keep their identity too.
    """
    captured = CaptureRequestService.captured

    test.assertIs(captured['payload'], _order_request)
    test.assertIs(captured['raw'], _order_request)
    test.assertEqual(captured['input']['customer_id'], 'C-1001')
    test.assertIs(captured['input']['items'], _order_request['items'])

# ################################################################################################################################

def verify_json_string_arrives_parsed(test:'TestCase', result:'any_') -> 'None':
    """ A JSON string sent with the JSON data format arrives as a parsed dict input,
    while the raw request keeps the string exactly as given.
    """
    captured = CaptureRequestService.captured

    test.assertEqual(captured['input']['customer_id'], 'C-1001')
    test.assertEqual(captured['input']['status'], 'confirmed')
    test.assertEqual(captured['raw'], _order_request_json)

# ################################################################################################################################

def verify_plain_string_stays_the_input(test:'TestCase', result:'any_') -> 'None':
    """ A plain string payload stays the input exactly as given.
    """
    captured = CaptureRequestService.captured

    test.assertEqual(captured['input'], _edifact_request)
    test.assertEqual(captured['raw'], _edifact_request)

# ################################################################################################################################

def verify_kwargs_become_the_payload(test:'TestCase', result:'any_') -> 'None':
    """ With no payload, extra keyword arguments become the payload dict.
    """
    captured = CaptureRequestService.captured

    test.assertEqual(captured['payload'], {'customer_id': 'C-1001', 'status': 'confirmed'})
    test.assertEqual(captured['input']['customer_id'], 'C-1001')
    test.assertEqual(captured['input']['status'], 'confirmed')

# ################################################################################################################################

def verify_free_form_comes_back_as_a_dict(test:'TestCase', result:'any_') -> 'None':
    """ A free-form message payload comes back to the caller as a plain dict.
    """
    test.assertIsInstance(result, dict)
    test.assertEqual(result, {'order': {'details': {'total': 123}}})

# ################################################################################################################################

def verify_subtree_comes_back_as_a_dict(test:'TestCase', result:'any_') -> 'None':
    """ A string-output subtree payload comes back to the caller as a plain dict.
    """
    test.assertIsInstance(result, dict)
    test.assertEqual(result, {'order': {'customer_id': 'C-1001', 'status': 'confirmed'}})

# ################################################################################################################################

def verify_model_comes_back_as_a_dict(test:'TestCase', result:'any_') -> 'None':
    """ A model assigned with the JSON data format comes back to the caller as a plain dict.
    """
    test.assertIsInstance(result, dict)
    test.assertEqual(result, {'customer_id': 'C-1001', 'status': 'confirmed'})

# ################################################################################################################################

def verify_as_bunch_bunchifies(test:'TestCase', result:'any_') -> 'None':
    """ With as_bunch the caller receives a Bunch with attribute access all the way down.
    """
    test.assertIsInstance(result, Bunch)
    test.assertEqual(result.order.details.total, 123)

# ################################################################################################################################

def verify_dict_identity_is_preserved(test:'TestCase', result:'any_') -> 'None':
    """ The caller receives the very dict the target assigned - values that
    would not survive JSON, e.g. a datetime, survive invoke.
    """
    test.assertIs(result, _report_response)
    test.assertIsInstance(result['generated_at'], datetime)

# ################################################################################################################################

def verify_empty_message_normalizes_to_an_empty_string(test:'TestCase', result:'any_') -> 'None':
    """ An empty free-form message normalizes to an empty string, never an empty dict.
    """
    test.assertIsInstance(result, str)
    test.assertEqual(result, '')

# ################################################################################################################################
# ################################################################################################################################

def build_invoke_cases() -> 'case_list':
    """ Returns the invoke-only cases - the request direction first, then the response direction.
    """
    out = []

    # The request direction ..
    out.append(make_case('invoke-dict-payload-is-the-same-object', CaptureRequestService,
        request=_order_request,
        verify=verify_dict_payload_is_the_same_object))

    out.append(make_case('invoke-json-string-arrives-parsed', CaptureRequestService,
        request=_order_request_json,
        data_format=DATA_FORMAT.JSON,
        verify=verify_json_string_arrives_parsed))

    out.append(make_case('invoke-plain-string-stays-the-input', CaptureRequestService,
        request=_edifact_request,
        verify=verify_plain_string_stays_the_input))

    out.append(make_case('invoke-kwargs-become-the-payload', CaptureRequestService,
        invoke_kwargs={'customer_id': 'C-1001', 'status': 'confirmed'},
        verify=verify_kwargs_become_the_payload))

    # .. and the response direction.
    out.append(make_case('invoke-free-form-comes-back-as-a-dict', FreeFormDetailsService,
        request={'customer_id': 'C-1001'},
        verify=verify_free_form_comes_back_as_a_dict))

    out.append(make_case('invoke-subtree-comes-back-as-a-dict', OrderSubtreeService,
        request={'customer_id': 'C-1001'},
        verify=verify_subtree_comes_back_as_a_dict))

    out.append(make_case('invoke-model-comes-back-as-a-dict', AssignedModelService,
        request={'customer_id': 'C-1001'},
        data_format=DATA_FORMAT.JSON,
        verify=verify_model_comes_back_as_a_dict))

    out.append(make_case('invoke-as-bunch-bunchifies', FreeFormDetailsService,
        request={'customer_id': 'C-1001'},
        as_bunch=True,
        verify=verify_as_bunch_bunchifies))

    out.append(make_case('invoke-dict-identity-is-preserved', ReportDictService,
        request={'report': 'quarterly'},
        verify=verify_dict_identity_is_preserved))

    out.append(make_case('invoke-empty-message-normalizes-to-an-empty-string', NoResponseService,
        request={'customer_id': 'C-1001'},
        verify=verify_empty_message_normalizes_to_an_empty_string))

    return out

# ################################################################################################################################
# ################################################################################################################################
