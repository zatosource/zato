# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from http.client import INTERNAL_SERVER_ERROR, OK
from json import dumps, loads
from unittest import main, TestCase
from unittest.mock import MagicMock, patch

# Zato
from zato.common.api import DATA_FORMAT, URL_TYPE
from zato.common.marshal_.api import Model
from zato.server.connection.http_soap.channel import serialize_response_payload
from zato.server.openapi_console.invoke import handle_invoke

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

_service_name = 'api.orders.get'
_url_path = '/api/orders/get'
_correlation_id = 'correlation-0001'
_remote_addr = '10.151.12.1'
_default_error_message = 'An internal error occurred'

_created = datetime(2026, 1, 2, 3, 4, 5)
_created_iso = '2026-01-02T03:04:05'

_amount = Decimal('1.10')
_amount_text = '1.10'

# Bytes that are not UTF-8, which no JSON document can carry
_binary = b'\xff\xfe\x00\x01'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class _Order(Model):
    order_id: int
    created: datetime

# ################################################################################################################################
# ################################################################################################################################

def _make_order(order_id:'int') -> '_Order':
    out = _Order()
    out.order_id = order_id
    out.created = _created
    return out

# ################################################################################################################################

def _make_channel_item() -> 'anydict':
    """ A REST channel the relay matches the request to.
    """
    out = {
        'id': 1,
        'name': 'api.orders.get',
        'connection': 'channel',
        'transport': URL_TYPE.PLAIN_HTTP,
        'is_active': True,
        'is_internal': False,
        'is_audit_log_active': False,
        'service_name': _service_name,
        'data_format': DATA_FORMAT.JSON,
    }

    return out

# ################################################################################################################################

def _make_server(response:'any_') -> 'any_':
    """ A server whose REST channel matches the request and whose service responds with the given response.
    """
    out = MagicMock()

    out.url_data.match.return_value = ({}, _make_channel_item())
    out.invoke.return_value = response

    out.needs_x_zato_cid = False
    out.return_tracebacks = False
    out.default_error_message = _default_error_message

    # No limit applies to this channel or to the caller
    out.rate_limiting_manager.check.return_value = None
    out.config_manager.request_dispatcher.check_sec_def_rate_limiting.return_value = None

    return out

# ################################################################################################################################

def _make_fields() -> 'anydict':
    """ What the console sends for a try-it request.
    """
    out = {
        'correlation_id': _correlation_id,
        'auth_type': 'basic_auth',
        'http_method': 'GET',
        'url_path': _url_path,
        'query_string': '',
        'headers': '{}',
        'body': '',
        'remote_addr': _remote_addr,
    }

    return out

# ################################################################################################################################

def _invoke(response:'any_') -> 'anydict':
    """ Relays a request, as an admin caller, to a service that responds with the given response, and returns the reply.
    """
    server = _make_server(response)

    with patch('zato.server.openapi_console.invoke.resolve_caller', return_value=(None, True)):
        out = handle_invoke(server, _make_fields())

    return out

# ################################################################################################################################

def _get_content_length(reply:'anydict') -> 'str':
    """ Returns the content length that the reply's headers announce.
    """
    headers = dict(loads(reply['headers']))
    out = headers['content-length']
    return out

# ################################################################################################################################
# ################################################################################################################################

class RelayResponseBodyTestCase(TestCase):
    """ The relay replies to the console with the body that the service's REST channel responds with,
    including responses that the standard library's JSON encoder cannot serialize.
    """

# ################################################################################################################################

    def test_a_dict_with_a_date_and_a_decimal(self) -> 'None':
        reply = _invoke({'created': _created, 'amount': _amount})

        self.assertEqual(reply['http_status'], OK)
        self.assertEqual(loads(reply['data']), {'created': _created_iso, 'amount': _amount_text})

# ################################################################################################################################

    def test_a_model_with_a_date(self) -> 'None':
        reply = _invoke(_make_order(1))

        self.assertEqual(reply['http_status'], OK)
        self.assertEqual(loads(reply['data']), {'order_id': 1, 'created': _created_iso})

# ################################################################################################################################

    def test_a_list_of_models(self) -> 'None':
        reply = _invoke([_make_order(1), _make_order(2)])

        expected = [
            {'order_id': 1, 'created': _created_iso},
            {'order_id': 2, 'created': _created_iso},
        ]

        self.assertEqual(reply['http_status'], OK)
        self.assertEqual(loads(reply['data']), expected)

# ################################################################################################################################

    def test_a_string_is_passed_through(self) -> 'None':
        reply = _invoke('plain text')

        self.assertEqual(reply['http_status'], OK)
        self.assertEqual(reply['data'], 'plain text')

# ################################################################################################################################

    def test_no_response_is_an_empty_body(self) -> 'None':
        reply = _invoke(None)

        self.assertEqual(reply['http_status'], OK)
        self.assertEqual(reply['data'], '')

# ################################################################################################################################

    def test_an_empty_dict_is_an_empty_object(self) -> 'None':
        reply = _invoke({})

        self.assertEqual(reply['http_status'], OK)
        self.assertEqual(reply['data'], '{}')

# ################################################################################################################################

    def test_the_body_is_the_rest_channels_body(self) -> 'None':
        """ Each kind of response is relayed exactly as the REST channel serializes it.
        """
        responses = [
            {'created': _created, 'amount': _amount},
            [_make_order(1), _make_order(2)],
            'plain text',
            {},
            [],
            None,
        ]

        for response in responses:
            with self.subTest(response=response):
                reply = _invoke(response)
                expected = serialize_response_payload(response, DATA_FORMAT.JSON)
                self.assertEqual(reply['data'], expected)

# ################################################################################################################################

    def test_a_model_body_is_the_rest_channels_body(self) -> 'None':
        """ A model renders itself to bytes on the wire, and the relay carries the same document as a string.
        """
        order = _make_order(1)

        reply = _invoke(order)
        expected = serialize_response_payload(order, DATA_FORMAT.JSON)

        self.assertEqual(reply['data'].encode('utf8'), expected)

# ################################################################################################################################

    def test_the_content_length_is_that_of_the_body(self) -> 'None':
        reply = _invoke({'created': _created, 'amount': _amount, 'label': 'Zürich'})

        expected = str(len(reply['data'].encode('utf8')))
        self.assertEqual(_get_content_length(reply), expected)

# ################################################################################################################################
# ################################################################################################################################

class RelayUnserializableResponseTestCase(TestCase):
    """ A response that cannot be serialized is reported the way its REST channel reports it,
    instead of failing the relay as a whole.
    """

# ################################################################################################################################

    def test_binary_bytes_are_a_server_error(self) -> 'None':
        reply = _invoke(_binary)

        self.assertEqual(reply['status'], 'ok')
        self.assertEqual(reply['http_status'], INTERNAL_SERVER_ERROR)
        self.assertEqual(reply['data'], _default_error_message)

# ################################################################################################################################

    def test_the_error_reply_carries_its_headers(self) -> 'None':
        reply = _invoke(_binary)

        expected = str(len(_default_error_message.encode('utf8')))
        self.assertEqual(_get_content_length(reply), expected)

# ################################################################################################################################

    def test_the_rest_channel_cannot_serialize_it_either(self) -> 'None':
        with self.assertRaises(UnicodeDecodeError):
            _ = serialize_response_payload(_binary, DATA_FORMAT.JSON)

# ################################################################################################################################
# ################################################################################################################################

class RESTChannelBodyTestCase(TestCase):
    """ The REST channel's own bodies, which the relay reproduces.
    """

# ################################################################################################################################

    def test_a_dict_on_a_json_channel(self) -> 'None':
        out = serialize_response_payload({'created': _created, 'amount': _amount}, DATA_FORMAT.JSON)
        self.assertEqual(loads(out), {'created': _created_iso, 'amount': _amount_text})

# ################################################################################################################################

    def test_an_empty_dict_depends_on_the_data_format(self) -> 'None':
        self.assertEqual(serialize_response_payload({}, DATA_FORMAT.JSON), '{}')
        self.assertEqual(serialize_response_payload({}, ''), '')

# ################################################################################################################################

    def test_a_model_renders_itself(self) -> 'None':
        out = serialize_response_payload(_make_order(1), DATA_FORMAT.JSON)
        self.assertEqual(out, dumps({'order_id': 1, 'created': _created_iso}, separators=(',', ':')).encode('utf8'))

# ################################################################################################################################

    def test_a_string_is_left_as_it_is(self) -> 'None':
        self.assertEqual(serialize_response_payload('plain text', DATA_FORMAT.JSON), 'plain text')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
