# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone
from unittest import main, TestCase
from unittest.mock import MagicMock, patch

# Zato
from zato.common.api import DATA_FORMAT, URL_TYPE, ZATO_NONE
from zato.common.exception import Forbidden
from zato.server.connection.http_soap.channel import Portal_Caller_Key, RequestDispatcher, status_response
from zato.server.api_portal.invoke import _build_request_ctx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

_cid = 'zcid-portal-0001'
_url_path = '/api/orders'
_match_target = '/api/orders::POST::*::*'
_remote_addr = '10.151.12.1'
_request_body = '<order id="123"/>'
_response_body = b'{"order_id":123}'
_socket_fd = 41

# ################################################################################################################################
# ################################################################################################################################

def _make_channel_item(security_groups_ctx:'any_'=None) -> 'anydict':
    """ A REST channel with a security definition of its own.
    """
    out = {
        'id': 1,
        'name': 'api.orders',
        'connection': 'channel',
        'transport': URL_TYPE.PLAIN_HTTP,
        'is_active': True,
        'is_internal': False,
        'is_audit_log_active': False,
        'service_name': 'api.orders.create',
        'service_impl_name': 'api.orders.create.impl',
        'match_target': _match_target,
        'data_format': DATA_FORMAT.JSON,
        'merge_url_params_req': True,
        'security_groups_ctx': security_groups_ctx,
    }

    return out

# ################################################################################################################################

def _make_dispatcher(channel_item:'anydict', sec_def:'any_') -> 'RequestDispatcher':
    """ A dispatcher whose only channel is the given one and whose service responds with a JSON document.
    """
    server = MagicMock()
    server.rest_log_ignore = set()
    server.rate_limiting_manager.check.return_value = None

    service_class = MagicMock()
    service_class.handles_auth_rejection = False
    server.service_store.name_to_impl_name = {channel_item['service_name']: channel_item['service_impl_name']}
    server.service_store.services = {channel_item['service_impl_name']: {'service_class': service_class}}

    sec = MagicMock()
    sec.sec_def = sec_def

    url_data = MagicMock()
    url_data.match.return_value = ({}, channel_item)
    url_data.url_sec = {_match_target: sec}

    response = MagicMock()
    response.payload = _response_body
    response.content_type = 'application/json'
    response.headers = {}
    response.status_code = 200

    request_handler = MagicMock()
    request_handler.handle.return_value = response

    out = RequestDispatcher(
        server=server,
        url_data=url_data,
        request_handler=request_handler,
        return_tracebacks=False,
        default_error_message='Internal server error',
        http_methods_allowed=['GET', 'POST'],
    )

    return out

# ################################################################################################################################

def _check_security(dispatcher:'RequestDispatcher', channel_item:'anydict', request_ctx:'anydict') -> 'None':
    meta = MagicMock()
    meta.path_info = _url_path
    dispatcher._check_security(_cid, meta, channel_item, request_ctx, b'', {}, MagicMock())

# ################################################################################################################################
# ################################################################################################################################

class PortalCallerSecurityTestCase(TestCase):
    """ A request that the API portal relays is not authenticated again by the channel.
    """

# ################################################################################################################################

    def test_a_relayed_request_is_not_checked_against_the_definition(self) -> 'None':
        channel_item = _make_channel_item()
        dispatcher = _make_dispatcher(channel_item, {'sec_type': 'basic_auth'})

        _check_security(dispatcher, channel_item, {Portal_Caller_Key: True})

        dispatcher.url_data.check_security.assert_not_called()

# ################################################################################################################################

    def test_a_request_over_http_is_checked_against_the_definition(self) -> 'None':
        channel_item = _make_channel_item()
        dispatcher = _make_dispatcher(channel_item, {'sec_type': 'basic_auth'})

        _check_security(dispatcher, channel_item, {})

        dispatcher.url_data.check_security.assert_called_once()

# ################################################################################################################################

    def test_a_relayed_request_is_not_checked_against_the_groups(self) -> 'None':
        security_groups_ctx = MagicMock()
        security_groups_ctx.has_members.return_value = True

        channel_item = _make_channel_item(security_groups_ctx)
        dispatcher = _make_dispatcher(channel_item, ZATO_NONE)

        with patch.object(dispatcher, 'check_security_via_groups') as check_security_via_groups:
            _check_security(dispatcher, channel_item, {Portal_Caller_Key: True})

        check_security_via_groups.assert_not_called()

# ################################################################################################################################

    def test_groups_without_members_refuse_a_request_over_http(self) -> 'None':
        security_groups_ctx = MagicMock()
        security_groups_ctx.has_members.return_value = False

        channel_item = _make_channel_item(security_groups_ctx)
        dispatcher = _make_dispatcher(channel_item, ZATO_NONE)

        with self.assertRaises(Forbidden):
            _check_security(dispatcher, channel_item, {})

# ################################################################################################################################
# ################################################################################################################################

class DisallowedAddressTestCase(TestCase):
    """ The connection of a disallowed address is dropped, and a relayed request, which has no connection, is marked as dropped.
    """

# ################################################################################################################################

    def _handle(self, request_ctx:'anydict') -> 'tuple[any_, MagicMock]':
        channel_item = _make_channel_item()
        dispatcher = _make_dispatcher(channel_item, ZATO_NONE)

        rate_limit_result = MagicMock()
        rate_limit_result.is_disallowed = True

        with patch('zato.server.connection.http_soap.channel.socket') as socket_module, \
             patch('zato.server.connection.http_soap.channel.os'):
            out = dispatcher._handle_rate_limit_result(_cid, rate_limit_result, request_ctx, _remote_addr, channel_item)

        return out, socket_module

# ################################################################################################################################

    def test_a_relayed_request(self) -> 'None':
        request_ctx = {}
        response, socket_module = self._handle(request_ctx)

        self.assertEqual(response, b'')
        self.assertTrue(request_ctx['zato.http.rate_limit.dropped'])
        socket_module.fromfd.assert_not_called()

# ################################################################################################################################

    def test_a_request_over_http(self) -> 'None':
        request_ctx:'anydict' = {'zato.socket_fd': _socket_fd}
        response, socket_module = self._handle(request_ctx)

        self.assertEqual(response, b'')
        self.assertTrue(request_ctx['zato.http.rate_limit.dropped'])
        self.assertEqual(socket_module.fromfd.call_args.args[0], _socket_fd)

# ################################################################################################################################
# ################################################################################################################################

class RelayedRequestDispatchTestCase(TestCase):
    """ The request context that the relay builds goes through the dispatcher the same way as one built by the HTTP server.
    """

# ################################################################################################################################

    def _dispatch(self) -> 'tuple[any_, anydict, RequestDispatcher]':

        server = MagicMock()
        server.client_address_headers = ['REMOTE_ADDR']

        fields = {
            'http_method': 'POST',
            'url_path': _url_path,
            'query_string': '',
            'headers': '{"Content-Type": "application/xml"}',
            'body': _request_body,
            'remote_addr': _remote_addr,
        }

        # The relay builds the request context and the HTTP layer adds the response headers to it ..
        request_ctx = _build_request_ctx(server, fields)
        request_ctx[Portal_Caller_Key] = True
        request_ctx['zato.http.response.headers'] = {}

        # .. on a channel with a definition of its own, which the portal has already checked the caller against.
        channel_item = _make_channel_item()
        dispatcher = _make_dispatcher(channel_item, {'sec_type': 'basic_auth'})

        timestamp = datetime.now(timezone.utc).isoformat()
        out = dispatcher.dispatch(_cid, timestamp, request_ctx, MagicMock(), 'portal', _remote_addr)

        return out, request_ctx, dispatcher

# ################################################################################################################################

    def test_the_service_responds(self) -> 'None':
        response, request_ctx, dispatcher = self._dispatch()

        self.assertEqual(response, _response_body)
        self.assertEqual(request_ctx['zato.http.response.status'], status_response[200])
        self.assertEqual(request_ctx['zato.http.response.headers']['Content-Type'], 'application/json')
        dispatcher.url_data.check_security.assert_not_called()

# ################################################################################################################################

    def test_the_service_receives_the_body_as_it_is(self) -> 'None':
        _, _, dispatcher = self._dispatch()

        request_handler:'any_' = dispatcher.request_handler
        call = request_handler.handle.call_args
        raw_request = call.args[4]

        self.assertEqual(raw_request, _request_body.encode('utf8'))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
