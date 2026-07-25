# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from json import dumps
from unittest.mock import MagicMock

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.soap.message import SOAPMessage
from zato.server.connection.facade import SOAPFacade, SOAPInvoker
from zato.server.connection.http_soap.invocation import build_soap_jsonata_context, dict_to_soap_message, \
    evaluate_soap_headers, maybe_run_fault_callback, maybe_run_soap_callback, merge_declarative_soap_request, \
    soap_message_to_dict

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

_invocation = HTTP_SOAP.Invocation
_value_mode = _invocation.ValueMode
_map_mode = _invocation.ResponseMapMode
_callback_type = _invocation.CallbackType

_test_cid = 'zcid-test-0001'

_test_operation = 'submitSingleMessage'
_declarative_operation = 'connectivityTest'

# ################################################################################################################################
# ################################################################################################################################

def _rows(*pairs) -> 'str':
    """ Builds the stored JSON of parameter rows - each entry is a key, a value and a mode.
    """
    out:'anylist' = []

    for key, value, mode in pairs:
        out.append({'key': key, 'value': value, 'mode': mode})

    return dumps(out)

# ################################################################################################################################

def _text_rows(*pairs) -> 'str':
    """ Builds rows whose values are all sent exactly as typed, which is the common case.
    """
    out = _rows(*[(key, value, _value_mode.Text) for key, value in pairs])
    return out

# ################################################################################################################################
# ################################################################################################################################

class SOAPMessageConversionTestCase(unittest.TestCase):
    """ Converting between a dot-accessed SOAP message and a plain dict.

    Both directions matter for declarative connections - a dict is what a JSONata expression can be
    evaluated against and what a callback can be handed, and a message is what actually goes on the
    wire, so a value that does not survive the round trip is a value a declarative connection cannot
    carry.
    """

# ################################################################################################################################

    def test_a_flat_message_becomes_a_flat_dict(self) -> 'None':
        message = SOAPMessage()
        message.facilityID = 'FAC-01'
        message.hl7Message = 'MSH|^~\\&|MYAPP'

        out = soap_message_to_dict(message)

        self.assertEqual(out, {'facilityID': 'FAC-01', 'hl7Message': 'MSH|^~\\&|MYAPP'})

# ################################################################################################################################

    def test_a_nested_message_becomes_a_nested_dict(self) -> 'None':
        message = SOAPMessage()
        message.order.customer_id = 'CUST-01'
        message.order.total = '99.50'

        out = soap_message_to_dict(message)

        self.assertEqual(out, {'order': {'customer_id': 'CUST-01', 'total': '99.50'}})

# ################################################################################################################################

    def test_repeated_elements_become_a_list(self) -> 'None':
        first = SOAPMessage()
        first.sku = 'SKU-1'

        second = SOAPMessage()
        second.sku = 'SKU-2'

        message = SOAPMessage()
        message.line = [first, second]

        out = soap_message_to_dict(message)

        self.assertEqual(out, {'line': [{'sku': 'SKU-1'}, {'sku': 'SKU-2'}]})

# ################################################################################################################################

    def test_a_dot_path_builds_a_subtree(self) -> 'None':
        out = dict_to_soap_message({'order.customer.id': 'CUST-01'})

        self.assertEqual(out.order.customer.id, 'CUST-01')

# ################################################################################################################################

    def test_a_nested_dict_builds_a_subtree(self) -> 'None':
        out = dict_to_soap_message({'order': {'customer': {'id': 'CUST-01'}}})

        self.assertEqual(out.order.customer.id, 'CUST-01')

# ################################################################################################################################

    def test_a_list_of_dicts_becomes_repeated_nodes(self) -> 'None':
        out = dict_to_soap_message({'line': [{'sku': 'SKU-1'}, {'sku': 'SKU-2'}]})

        self.assertEqual(len(out.line), 2)
        self.assertEqual(out.line[0].sku, 'SKU-1')
        self.assertEqual(out.line[1].sku, 'SKU-2')

# ################################################################################################################################

    def test_a_nested_structure_survives_the_round_trip(self) -> 'None':
        # The property that matters. A declarative connection converts in both directions on every
        # call, so anything lost on the way out or the way back is silently dropped data.
        data:'stranydict' = {
            'facilityID': 'FAC-01',
            'order': {'customer': {'id': 'CUST-01'}, 'total': '99.50'},
            'line': [{'sku': 'SKU-1'}, {'sku': 'SKU-2'}],
        }

        message = dict_to_soap_message(data)
        out = soap_message_to_dict(message)

        self.assertEqual(out, data)

# ################################################################################################################################
# ################################################################################################################################

class JSONataContextTestCase(unittest.TestCase):
    """ What a declarative SOAP connection's expressions are evaluated against.

    A scheduled call passes no message at all, so the context has to be something an expression can
    run against rather than None - otherwise every scheduled declarative connection fails on its
    first expression.
    """

# ################################################################################################################################

    def test_a_message_becomes_its_dict_form(self) -> 'None':
        message = SOAPMessage()
        message.facilityID = 'FAC-01'

        out = build_soap_jsonata_context(message)

        self.assertEqual(out, {'facilityID': 'FAC-01'})

# ################################################################################################################################

    def test_a_dict_is_its_own_context(self) -> 'None':
        data = {'facilityID': 'FAC-01'}

        out = build_soap_jsonata_context(data)

        self.assertEqual(out, data)

# ################################################################################################################################

    def test_a_scheduled_call_gets_an_empty_context(self) -> 'None':
        out = build_soap_jsonata_context(None)

        self.assertEqual(out, {})

# ################################################################################################################################

    def test_a_scalar_gets_an_empty_context(self) -> 'None':
        # A string is not something an expression can select fields out of, so it is no more usable
        # as a context than nothing at all.
        out = build_soap_jsonata_context('just a string')

        self.assertEqual(out, {})

# ################################################################################################################################
# ################################################################################################################################

class MergeDeclarativeRequestTestCase(unittest.TestCase):
    """ Filling in what the caller did not pass from the connection's declarative profile.

    The rule throughout is that an explicit argument always wins - a declarative profile covers the
    blanks, it does not override a service that said what it wanted.
    """

# ################################################################################################################################

    def test_an_explicit_operation_wins(self) -> 'None':
        config = {_invocation.Field_Request_Operation: _declarative_operation}

        operation, _ = merge_declarative_soap_request(config, _test_operation, SOAPMessage(), {})

        self.assertEqual(operation, _test_operation)

# ################################################################################################################################

    def test_an_empty_operation_takes_the_declarative_one(self) -> 'None':
        config = {_invocation.Field_Request_Operation: _declarative_operation}

        operation, _ = merge_declarative_soap_request(config, '', SOAPMessage(), {})

        self.assertEqual(operation, _declarative_operation)

# ################################################################################################################################

    def test_an_empty_operation_with_nothing_configured_stays_empty(self) -> 'None':
        operation, _ = merge_declarative_soap_request({}, '', SOAPMessage(), {})

        self.assertEqual(operation, '')

# ################################################################################################################################

    def test_an_explicit_message_wins_over_the_rows(self) -> 'None':
        config = {_invocation.Field_Request_Message: _text_rows(('facilityID', 'FROM-CONFIG'))}

        message = SOAPMessage()
        message.facilityID = 'FROM-CALLER'

        _, out = merge_declarative_soap_request(config, _test_operation, message, {})

        self.assertEqual(out.facilityID, 'FROM-CALLER')

# ################################################################################################################################

    def test_the_message_rows_build_the_message(self) -> 'None':
        config = {
            _invocation.Field_Request_Message: _text_rows(
                ('facilityID', 'FAC-01'),
                ('order.customer.id', 'CUST-01'),
            ),
        }

        _, out = merge_declarative_soap_request(config, _test_operation, None, {})

        self.assertEqual(out.facilityID, 'FAC-01')
        self.assertEqual(out.order.customer.id, 'CUST-01')

# ################################################################################################################################

    def test_a_jsonata_row_is_evaluated_against_the_context(self) -> 'None':
        config = {
            _invocation.Field_Request_Message: _rows(('facilityID', 'facility', _value_mode.JSONata)),
        }

        _, out = merge_declarative_soap_request(config, _test_operation, None, {'facility': 'FAC-99'})

        self.assertEqual(out.facilityID, 'FAC-99')

# ################################################################################################################################

    def test_the_message_map_builds_the_whole_message(self) -> 'None':
        config = {_invocation.Field_Request_Message_Map: '{"facilityID": facility}'}

        _, out = merge_declarative_soap_request(config, _test_operation, None, {'facility': 'FAC-99'})

        self.assertEqual(out.facilityID, 'FAC-99')

# ################################################################################################################################

    def test_the_message_map_wins_over_the_rows(self) -> 'None':
        # Both are configured, which the dashboard allows, so which one applies has to be decided
        # rather than left to whichever happens to be read first.
        config = {
            _invocation.Field_Request_Message_Map: '{"facilityID": "FROM-MAP"}',
            _invocation.Field_Request_Message: _text_rows(('facilityID', 'FROM-ROWS')),
        }

        _, out = merge_declarative_soap_request(config, _test_operation, None, {})

        self.assertEqual(out.facilityID, 'FROM-MAP')

# ################################################################################################################################

    def test_nothing_configured_sends_an_empty_body(self) -> 'None':
        _, out = merge_declarative_soap_request({}, _test_operation, None, {})

        self.assertIsInstance(out, SOAPMessage)
        self.assertEqual(soap_message_to_dict(out), {})

# ################################################################################################################################

    def test_a_dict_from_the_caller_is_accepted(self) -> 'None':
        # Passing a dict is a convenience a service is entitled to use, so it converts rather than
        # travelling as an opaque value the serializer would not know what to do with.
        _, out = merge_declarative_soap_request({}, _test_operation, {'facilityID': 'FAC-01'}, {})

        self.assertIsInstance(out, SOAPMessage)
        self.assertEqual(out.facilityID, 'FAC-01')

# ################################################################################################################################
# ################################################################################################################################

class SOAPHeadersTestCase(unittest.TestCase):
    """ The custom header elements a declarative connection injects into every envelope.
    """

# ################################################################################################################################

    def test_no_rows_configured_means_no_headers(self) -> 'None':
        # None rather than an empty dict, because the caller distinguishes "no headers configured"
        # from "headers configured and they evaluated to nothing".
        out = evaluate_soap_headers({}, {})

        self.assertIsNone(out)

# ################################################################################################################################

    def test_text_rows_are_sent_as_typed(self) -> 'None':
        config = {_invocation.Field_Request_SOAP_Headers: _text_rows(('ClientVersion', '4.1'))}

        out = evaluate_soap_headers(config, {})

        self.assertEqual(out, {'ClientVersion': '4.1'})

# ################################################################################################################################

    def test_a_jsonata_row_is_evaluated_at_call_time(self) -> 'None':
        config = {
            _invocation.Field_Request_SOAP_Headers: _rows(('Tenant', 'tenant', _value_mode.JSONata)),
        }

        out = evaluate_soap_headers(config, {'tenant': 'ACME'})

        self.assertEqual(out, {'Tenant': 'ACME'})

# ################################################################################################################################
# ################################################################################################################################

class SOAPCallbackTestCase(unittest.TestCase):
    """ Delivering a response or a fault to a connection's configured callback.

    Delivery happens in a spawned greenlet so the caller is not held up by it, which is why these
    tests assert on what was handed to the spawn rather than waiting for a delivery.
    """

# ################################################################################################################################

    def _response(self) -> 'SOAPMessage':
        out = SOAPMessage()
        out.status = 'Success'
        out.receipt.id = 'RCP-01'

        return out

# ################################################################################################################################

    def _spawned(self, config:'anydict', response:'any_', is_fault:'bool'=False) -> 'anydict':
        """ Runs a callback delivery with the spawn patched out and returns what it was called with.
        """
        import zato.server.connection.http_soap.invocation as invocation

        calls:'anylist' = []

        original_spawn = invocation.spawn
        invocation.spawn = lambda *args: calls.append(args)

        try:
            if is_fault:
                maybe_run_fault_callback(MagicMock(), config, _test_cid, response)
            else:
                maybe_run_soap_callback(MagicMock(), config, _test_cid, response)
        finally:
            invocation.spawn = original_spawn

        out:'anydict' = {'calls': calls}
        return out

# ################################################################################################################################

    def test_no_callback_configured_is_a_no_op(self) -> 'None':
        result = self._spawned({}, self._response())

        self.assertEqual(result['calls'], [])

# ################################################################################################################################

    def test_a_callback_type_without_a_name_is_a_no_op(self) -> 'None':
        # A half-configured callback would otherwise be delivered to a connection or topic named by
        # the empty string, which is a lookup failure logged once per invocation.
        config = {_invocation.Field_Callback_Type: _callback_type.Service}

        result = self._spawned(config, self._response())

        self.assertEqual(result['calls'], [])

# ################################################################################################################################

    def test_the_response_is_delivered_as_a_dict(self) -> 'None':
        config = {
            _invocation.Field_Callback_Type: _callback_type.Service,
            _invocation.Field_Callback_Name: 'my.callback.service',
        }

        result = self._spawned(config, self._response())

        self.assertEqual(len(result['calls']), 1)

        # The spawn arguments are the delivery function and then what it is called with, so the
        # data is the last of them.
        data = result['calls'][0][-1]

        self.assertEqual(data, {'status': 'Success', 'receipt': {'id': 'RCP-01'}})

# ################################################################################################################################

    def test_a_jsonata_map_reshapes_the_response(self) -> 'None':
        config = {
            _invocation.Field_Callback_Type: _callback_type.Service,
            _invocation.Field_Callback_Name: 'my.callback.service',
            _invocation.Field_Response_Map: '{"outcome": status}',
            _invocation.Field_Response_Map_Mode: _map_mode.JSONata,
        }

        result = self._spawned(config, self._response())
        data = result['calls'][0][-1]

        self.assertEqual(data, {'outcome': 'Success'})

# ################################################################################################################################

    def test_a_map_with_no_mode_defaults_to_jsonata(self) -> 'None':
        # The mode is an opaque attribute, so a connection configured before the field existed has
        # a map and no mode, and treating that as XPath would run a JSONata expression as XPath.
        config = {
            _invocation.Field_Callback_Type: _callback_type.Service,
            _invocation.Field_Callback_Name: 'my.callback.service',
            _invocation.Field_Response_Map: '{"outcome": status}',
        }

        result = self._spawned(config, self._response())
        data = result['calls'][0][-1]

        self.assertEqual(data, {'outcome': 'Success'})

# ################################################################################################################################

    def test_an_xpath_map_runs_against_the_response_xml(self) -> 'None':
        config = {
            _invocation.Field_Callback_Type: _callback_type.Service,
            _invocation.Field_Callback_Name: 'my.callback.service',
            _invocation.Field_Response_Map: '//status/text()',
            _invocation.Field_Response_Map_Mode: _map_mode.XPath,
        }

        result = self._spawned(config, self._response())
        data = result['calls'][0][-1]

        self.assertIn('Success', data)

# ################################################################################################################################

    def test_a_fault_is_delivered_with_its_flag(self) -> 'None':
        # A fault is not a response, so the response map does not apply to it - what a callback
        # needs to know first is that this was a fault at all.
        config = {
            _invocation.Field_Callback_Type: _callback_type.Service,
            _invocation.Field_Callback_Name: 'my.callback.service',
            _invocation.Field_Response_Map: '{"outcome": status}',
        }

        fault = MagicMock()
        fault.code = 'soap:Sender'
        fault.reason = 'facilityID is required'
        fault.detail = SOAPMessage()

        result = self._spawned(config, fault, is_fault=True)
        data = result['calls'][0][-1]

        self.assertTrue(data['is_fault'])
        self.assertEqual(data['code'], 'soap:Sender')
        self.assertEqual(data['reason'], 'facilityID is required')

# ################################################################################################################################

    def test_a_fault_without_a_callback_is_a_no_op(self) -> 'None':
        fault = MagicMock()
        fault.detail = SOAPMessage()

        result = self._spawned({}, fault, is_fault=True)

        self.assertEqual(result['calls'], [])

# ################################################################################################################################
# ################################################################################################################################

class SOAPFacadeTestCase(unittest.TestCase):
    """ The self.soap facade a service reaches outgoing SOAP connections through.
    """

# ################################################################################################################################

    def _facade(self, connections:'anydict') -> 'SOAPFacade':
        out_soap = MagicMock()
        out_soap.__getitem__ = lambda _, name: connections[name]

        facade = SOAPFacade()
        facade.init(_test_cid, out_soap)

        return facade

# ################################################################################################################################

    def test_a_connection_comes_back_as_an_invoker(self) -> 'None':
        item = MagicMock()
        facade = self._facade({'my.connection': item})

        out = facade['my.connection']

        self.assertIsInstance(out, SOAPInvoker)
        self.assertIs(out.conn, item.conn)

# ################################################################################################################################

    def test_the_invoker_carries_the_request_cid(self) -> 'None':
        # Everything the invoker does is logged and audited against the cid of the request that
        # caused it, so an invoker that made up its own would break the trail through the system.
        facade = self._facade({'my.connection': MagicMock()})

        out = facade['my.connection']

        self.assertEqual(out.cid, _test_cid)

# ################################################################################################################################

    def test_an_unknown_connection_raises_a_key_error(self) -> 'None':
        facade = self._facade({})

        with self.assertRaises(KeyError):
            _ = facade['no.such.connection']

# ################################################################################################################################

    def test_invoke_passes_the_cid_through(self) -> 'None':
        conn = MagicMock()
        invoker = SOAPInvoker(conn, _test_cid)

        _ = invoker.invoke(_test_operation, None)

        conn.invoke.assert_called_once_with(_test_cid, _test_operation, None)

# ################################################################################################################################

    def test_invoke_with_no_arguments_leaves_them_to_the_profile(self) -> 'None':
        # An empty operation and no message is what a declarative connection is invoked with, and
        # the wrapper is what resolves them - so the facade must pass the blanks along rather than
        # substituting anything of its own.
        conn = MagicMock()
        invoker = SOAPInvoker(conn, _test_cid)

        _ = invoker.invoke()

        conn.invoke.assert_called_once_with(_test_cid, '', None)

# ################################################################################################################################

    def test_the_invoker_names_its_connection(self) -> 'None':
        conn = MagicMock()
        conn.config = {'name': 'my.connection'}

        invoker = SOAPInvoker(conn, _test_cid)

        self.assertIn('my.connection', repr(invoker))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
