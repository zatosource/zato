# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode, b64encode
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from http.client import CREATED, NOT_FOUND, OK, UNAUTHORIZED
from json import dumps, loads
from unittest import main, TestCase
from unittest.mock import MagicMock, patch

# Zato
from zato.common.api import DATA_FORMAT, SEC_DEF_TYPE, URL_TYPE
from zato.common.bearer_token_identity import Identity_Key
from zato.common.marshal_.api import Model
from zato.common.util.url_dispatcher import to_internal_accept
from zato.common.webapp.auth.auth_type import ConsoleAuthType
from zato.server.connection.http_soap.channel import Console_Caller_Key, serialize_response_payload
from zato.server.openapi_console.caller import ConsoleCaller
from zato.server.openapi_console.invoke import handle_invoke

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, iterator_, intset

# ################################################################################################################################
# ################################################################################################################################

_service_name = 'api.orders.get'
_url_path = '/api/orders/get'
_correlation_id = 'correlation-0001'
_remote_addr = '10.151.12.1'
_forged_addr = '10.151.12.99'
_security_id = 17
_sec_def_name = 'orders.client'
_secret = 'password-0001'
_apikey_header_key = 'HTTP_X_API_KEY'
_groups_apikey_header_key = 'HTTP_X_GROUP_API_KEY'

_created = datetime(2026, 1, 2, 3, 4, 5)
_created_iso = '2026-01-02T03:04:05'

_amount = Decimal('1.10')
_amount_text = '1.10'

# A query string with one parameter repeated
_query_string = 'status=open&tag=red&tag=blue'

# A request body that is not JSON
_xml_body = '<order id="123"/>'

# A response body that is not UTF-8
_binary = b'\xff\xfe\x00\x01'

# The chunks of a streaming response
_chunks = [b'{"order_id":', b'1}']

# The keys that the server reads a client's address from, in the order it reads them
_client_address_headers = ['HTTP_X_ZATO_FORWARDED_FOR', 'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR']

# What the HTTP request handler responds with unless a test says otherwise
_json_content_type = 'application/json'
_default_body = b'{"order_id":1}'

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
        'service_name': _service_name,
        'data_format': DATA_FORMAT.JSON,
        'security_id': _security_id,
        'security_groups_ctx': None,
    }

    return out

# ################################################################################################################################

def _make_server(
    status:'str'='200 OK',
    headers:'anydict | None'=None,
    body:'bytes | iterator_'=_default_body,
    ) -> 'any_':
    """ A server whose REST channel matches the request and whose HTTP request handler responds
    with the given status, headers and body.
    """
    if headers is None:
        headers = {'Content-Type': _json_content_type}

    out = MagicMock()
    out.url_data.match.return_value = ({}, _make_channel_item())
    out.url_data.basic_auth_get_by_id.return_value = {'id': _security_id, 'name': _sec_def_name,
        'sec_type': SEC_DEF_TYPE.BASIC_AUTH, 'username': _sec_def_name}
    out.url_data.apikey_get_by_id.return_value = {'id': _security_id, 'name': _sec_def_name,
        'sec_type': SEC_DEF_TYPE.APIKEY, 'header': _apikey_header_key}
    out.url_data.oauth_get_by_id.return_value = {'id': _security_id, 'name': _sec_def_name,
        'sec_type': SEC_DEF_TYPE.OAUTH, 'username': _sec_def_name}
    out.client_address_headers = _client_address_headers
    out.http_request_handler.return_value = (status, headers, body)

    return out

# ################################################################################################################################

def _make_fields() -> 'anydict':
    """ What the console sends for a try-it request.
    """
    out = {
        'correlation_id': _correlation_id,
        'session_token': 'session-token-0001',
        'http_method': 'GET',
        'url_path': _url_path,
        'query_string': '',
        'headers': '{}',
        'body': '',
        'remote_addr': _remote_addr,
    }

    return out

# ################################################################################################################################

def _make_caller(is_admin:'bool', auth_type:'str', security_ids:'intset') -> 'ConsoleCaller':
    """ A signed-in caller, as the session token that the console sends identifies it.
    """
    out = ConsoleCaller()
    out.is_admin = is_admin
    out.auth_type = auth_type
    out.username = _sec_def_name
    out.secret = _secret
    out.security_ids = security_ids

    return out

# ################################################################################################################################

def _invoke(server:'any_', fields:'anydict', caller:'ConsoleCaller | None') -> 'anydict':
    """ Relays a request, as the given caller, to the given server and returns the reply.
    """
    with patch('zato.server.openapi_console.invoke.resolve_session', return_value=caller):
        out = handle_invoke(server, fields)

    return out

# ################################################################################################################################

def _invoke_as_admin(server:'any_', fields:'anydict') -> 'anydict':
    """ Relays a request, as an admin caller, to the given server and returns the reply.
    """
    caller = _make_caller(True, ConsoleAuthType.Basic_Auth, set())

    out = _invoke(server, fields, caller)
    return out

# ################################################################################################################################

def _invoke_as_client(server:'any_', fields:'anydict', auth_type:'str'=ConsoleAuthType.Basic_Auth) -> 'anydict':
    """ Relays a request, as a caller whose credentials the channel's own definition accepts, to the given server
    and returns the reply.
    """
    caller = _make_caller(False, auth_type, {_security_id})

    out = _invoke(server, fields, caller)
    return out

# ################################################################################################################################

def _get_request_ctx(server:'any_') -> 'anydict':
    """ Returns the request context that the HTTP request handler received.
    """
    call = server.http_request_handler.call_args
    out = call.args[0]
    return out

# ################################################################################################################################

def _get_headers(reply:'anydict') -> 'anydict':
    """ Returns the response headers that the reply carries.
    """
    out = dict(loads(reply['headers']))
    return out

# ################################################################################################################################
# ################################################################################################################################

class RelayRequestContextTestCase(TestCase):
    """ The relay hands the HTTP request handler a request context with the same keys that the HTTP server builds.
    """

# ################################################################################################################################

    def _relay(self, fields:'anydict') -> 'anydict':
        server = _make_server()
        _ = _invoke_as_admin(server, fields)

        out = _get_request_ctx(server)
        return out

# ################################################################################################################################

    def test_the_request_line(self) -> 'None':
        fields = _make_fields()
        fields['query_string'] = _query_string

        request_ctx = self._relay(fields)

        self.assertEqual(request_ctx['REQUEST_METHOD'], 'GET')
        self.assertEqual(request_ctx['PATH_INFO'], _url_path)
        self.assertEqual(request_ctx['QUERY_STRING'], _query_string)
        self.assertEqual(request_ctx['RAW_URI'], f'{_url_path}?{_query_string}')

# ################################################################################################################################

    def test_the_raw_uri_without_a_query_string(self) -> 'None':
        request_ctx = self._relay(_make_fields())
        self.assertEqual(request_ctx['RAW_URI'], _url_path)

# ################################################################################################################################

    def test_the_body_is_passed_as_it_is(self) -> 'None':
        fields = _make_fields()
        fields['http_method'] = 'POST'
        fields['body'] = _xml_body

        request_ctx = self._relay(fields)

        self.assertEqual(request_ctx['zato.http.raw_request'], _xml_body.encode('utf8'))
        self.assertEqual(request_ctx['CONTENT_LENGTH'], str(len(_xml_body)))

# ################################################################################################################################

    def test_the_headers_are_wsgi_keys(self) -> 'None':
        fields = _make_fields()
        fields['headers'] = dumps({'Content-Type': 'application/xml', 'X-Correlation-ID': 'abc', 'Accept': 'text/csv'})

        request_ctx = self._relay(fields)

        self.assertEqual(request_ctx['CONTENT_TYPE'], 'application/xml')
        self.assertEqual(request_ctx['HTTP_X_CORRELATION_ID'], 'abc')
        self.assertEqual(request_ctx['HTTP_ACCEPT'], 'text/csv')

# ################################################################################################################################

    def test_the_client_address_is_that_of_the_browser(self) -> 'None':
        """ A forwarding header typed into the console does not change the address that limits apply to.
        """
        fields = _make_fields()
        fields['headers'] = dumps({'X-Forwarded-For': _forged_addr})

        request_ctx = self._relay(fields)

        for key in _client_address_headers:
            with self.subTest(key=key):
                self.assertEqual(request_ctx[key], _remote_addr)

# ################################################################################################################################

    def test_an_admin_caller_has_no_security_definition(self) -> 'None':
        request_ctx = self._relay(_make_fields())

        self.assertIn(Console_Caller_Key, request_ctx)
        self.assertNotIn('zato.sec_def', request_ctx)

# ################################################################################################################################

    def test_a_basic_auth_caller_sends_its_credentials_to_the_channel(self) -> 'None':
        server = _make_server()
        _ = _invoke_as_client(server, _make_fields())

        request_ctx = _get_request_ctx(server)
        credentials = b64encode(f'{_sec_def_name}:{_secret}'.encode('utf8')).decode('ascii')

        # The channel's own security checks the request
        self.assertNotIn(Console_Caller_Key, request_ctx)
        self.assertEqual(request_ctx['HTTP_AUTHORIZATION'], f'Basic {credentials}')

# ################################################################################################################################

    def test_a_bearer_token_caller_sends_its_token_to_the_channel(self) -> 'None':
        server = _make_server()
        _ = _invoke_as_client(server, _make_fields(), ConsoleAuthType.Bearer_Token)

        request_ctx = _get_request_ctx(server)

        self.assertNotIn(Console_Caller_Key, request_ctx)
        self.assertEqual(request_ctx['HTTP_AUTHORIZATION'], f'Bearer {_secret}')

# ################################################################################################################################

    def test_an_apikey_caller_sends_its_key_in_each_header_the_channel_reads(self) -> 'None':
        server = _make_server()

        groups_ctx = MagicMock()
        groups_ctx.has_members.return_value = True
        groups_ctx.has_security_id.return_value = True
        groups_ctx.apikey_header = _groups_apikey_header_key

        channel_item = _make_channel_item()
        channel_item['security_groups_ctx'] = groups_ctx
        server.url_data.match.return_value = ({}, channel_item)

        _ = _invoke_as_client(server, _make_fields(), ConsoleAuthType.API_Key)

        request_ctx = _get_request_ctx(server)

        self.assertNotIn(Console_Caller_Key, request_ctx)
        self.assertEqual(request_ctx[_apikey_header_key], _secret)
        self.assertEqual(request_ctx[_groups_apikey_header_key], _secret)

# ################################################################################################################################

    def test_credentials_typed_into_the_console_are_replaced(self) -> 'None':
        server = _make_server()

        fields = _make_fields()
        fields['headers'] = dumps({'Authorization': 'Bearer token-value-0009'})

        _ = _invoke_as_client(server, fields, ConsoleAuthType.Bearer_Token)

        request_ctx = _get_request_ctx(server)
        self.assertEqual(request_ctx['HTTP_AUTHORIZATION'], f'Bearer {_secret}')

# ################################################################################################################################

    def test_a_bearer_client_secret_caller_is_its_security_definition(self) -> 'None':
        """ Channels do not accept the client ID and secret of a Bearer token definition, so the console's check stands in.
        """
        server = _make_server()
        server.url_data.basic_auth_get_by_id.return_value = None

        _ = _invoke_as_client(server, _make_fields())

        request_ctx = _get_request_ctx(server)

        self.assertIn(Console_Caller_Key, request_ctx)
        self.assertNotIn('HTTP_AUTHORIZATION', request_ctx)
        self.assertNotIn(Identity_Key, request_ctx)
        self.assertEqual(request_ctx['zato.sec_def']['id'], _security_id)

# ################################################################################################################################

    def test_a_bearer_client_secret_caller_of_a_group_is_identified_by_name(self) -> 'None':
        server = _make_server()
        server.url_data.basic_auth_get_by_id.return_value = None

        groups_ctx = MagicMock()
        groups_ctx.has_members.return_value = True
        groups_ctx.has_security_id.return_value = True

        channel_item = _make_channel_item()
        channel_item['security_id'] = None
        channel_item['security_groups_ctx'] = groups_ctx
        server.url_data.match.return_value = ({}, channel_item)

        _ = _invoke_as_client(server, _make_fields())

        request_ctx = _get_request_ctx(server)
        self.assertEqual(request_ctx[Identity_Key], _sec_def_name)

# ################################################################################################################################
# ################################################################################################################################

class RelayChannelMatchTestCase(TestCase):
    """ The relay matches the channel the way the HTTP dispatcher matches it and refuses what the console does not document.
    """

# ################################################################################################################################

    def _get_match_accept(self, headers:'anydict') -> 'str':
        server = _make_server()

        fields = _make_fields()
        fields['headers'] = dumps(headers)

        _ = _invoke_as_admin(server, fields)

        call = server.url_data.match.call_args
        out = call.args[2]
        return out

# ################################################################################################################################

    def test_a_request_without_an_accept_header(self) -> 'None':
        self.assertEqual(self._get_match_accept({}), to_internal_accept(None))

# ################################################################################################################################

    def test_a_request_with_an_accept_header(self) -> 'None':
        self.assertEqual(self._get_match_accept({'Accept': 'application/xml'}), to_internal_accept('application/xml'))

# ################################################################################################################################

    def test_an_unknown_path_is_not_found(self) -> 'None':
        server = _make_server()
        server.url_data.match.return_value = (None, None)

        reply = _invoke_as_admin(server, _make_fields())

        self.assertEqual(reply['status'], 'not_found')
        server.http_request_handler.assert_not_called()

# ################################################################################################################################

    def test_an_excluded_channel_is_not_found(self) -> 'None':
        server = _make_server()

        channel_item = _make_channel_item()
        channel_item['should_include_in_openapi'] = False
        server.url_data.match.return_value = ({}, channel_item)

        reply = _invoke_as_admin(server, _make_fields())

        self.assertEqual(reply['status'], 'not_found')
        server.http_request_handler.assert_not_called()

# ################################################################################################################################

    def test_a_channel_the_caller_cannot_see_is_not_found(self) -> 'None':
        server = _make_server()

        channel_item = _make_channel_item()
        channel_item['security_id'] = _security_id + 1
        server.url_data.match.return_value = ({}, channel_item)

        reply = _invoke_as_client(server, _make_fields())

        self.assertEqual(reply['status'], 'not_found')
        server.http_request_handler.assert_not_called()

# ################################################################################################################################

    def test_an_unidentified_caller_is_unauthorized(self) -> 'None':
        server = _make_server()

        reply = _invoke(server, _make_fields(), None)

        self.assertEqual(reply['status'], 'unauthorized')
        server.http_request_handler.assert_not_called()

# ################################################################################################################################
# ################################################################################################################################

class RelayReplyTestCase(TestCase):
    """ The relay replies with the status, the headers and the body that the HTTP request handler responded with.
    """

# ################################################################################################################################

    def test_the_status_code(self) -> 'None':
        for status, expected in (('200 OK', OK), ('201 Created', CREATED), ('404 Not Found', NOT_FOUND),
            ('401 Unauthorized', UNAUTHORIZED)):
            with self.subTest(status=status):
                server = _make_server(status=status)
                reply = _invoke_as_admin(server, _make_fields())

                self.assertEqual(reply['status'], 'ok')
                self.assertEqual(reply['http_status'], expected)

# ################################################################################################################################

    def test_the_content_type(self) -> 'None':
        server = _make_server(headers={'Content-Type': 'application/xml'}, body=b'<order/>')
        reply = _invoke_as_admin(server, _make_fields())

        self.assertEqual(reply['content_type'], 'application/xml')
        self.assertEqual(b64decode(reply['data']), b'<order/>')

# ################################################################################################################################

    def test_a_response_without_a_content_type(self) -> 'None':
        server = _make_server(status='404 Not Found', headers={}, body=b'')
        reply = _invoke_as_admin(server, _make_fields())

        self.assertEqual(reply['content_type'], '')

# ################################################################################################################################

    def test_the_headers(self) -> 'None':
        server = _make_server(headers={'X-Zato-CID': 'abc', 'Content-Type': _json_content_type})
        reply = _invoke_as_admin(server, _make_fields())

        headers = _get_headers(reply)

        self.assertEqual(headers['x-zato-cid'], 'abc')
        self.assertEqual(headers['content-type'], _json_content_type)
        self.assertEqual(headers['content-length'], str(len(_default_body)))
        self.assertEqual(headers['connection'], 'keep-alive')

# ################################################################################################################################

    def test_a_length_set_by_the_service_is_not_repeated(self) -> 'None':
        server = _make_server(headers={'Content-Length': str(len(_default_body))})
        reply = _invoke_as_admin(server, _make_fields())

        names = []
        for name, _ in loads(reply['headers']):
            names.append(name)

        self.assertEqual(names.count('content-length'), 1)

# ################################################################################################################################

    def test_a_request_that_closes_its_connection(self) -> 'None':
        server = _make_server()

        fields = _make_fields()
        fields['headers'] = dumps({'Connection': 'close'})

        reply = _invoke_as_admin(server, fields)

        self.assertEqual(_get_headers(reply)['connection'], 'close')

# ################################################################################################################################

    def test_a_binary_body_keeps_each_byte(self) -> 'None':
        server = _make_server(body=_binary)
        reply = _invoke_as_admin(server, _make_fields())

        self.assertEqual(b64decode(reply['data']), _binary)

# ################################################################################################################################

    def test_a_streaming_response(self) -> 'None':
        server = _make_server(body=iter(_chunks))
        reply = _invoke_as_admin(server, _make_fields())

        headers = _get_headers(reply)

        self.assertEqual(reply['status'], 'ok')
        self.assertEqual(b64decode(reply['data']), b''.join(_chunks))
        self.assertEqual(headers['transfer-encoding'], 'chunked')
        self.assertNotIn('content-length', headers)

# ################################################################################################################################

    def test_a_dropped_request(self) -> 'None':
        """ A request from an address that the channel's rules disallow is reported as no server having replied.
        """
        server = _make_server(body=b'')

        def drop(request_ctx:'anydict') -> 'any_':
            request_ctx['zato.http.rate_limit.dropped'] = True
            return '200 OK', {}, b''

        server.http_request_handler.side_effect = drop
        reply = _invoke_as_admin(server, _make_fields())

        self.assertEqual(reply['status'], 'dropped')

# ################################################################################################################################
# ################################################################################################################################

class RESTChannelBodyTestCase(TestCase):
    """ The REST channel's own bodies, which relayed requests receive through the same handler.
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

# ################################################################################################################################
# ################################################################################################################################
