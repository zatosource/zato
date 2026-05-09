# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from hashlib import sha256
from io import BytesIO
from typing import NamedTuple
from unittest.mock import MagicMock, patch

# hypothesis
from hypothesis import given, HealthCheck, settings as hypothesis_settings
from hypothesis import strategies as st

# Zato
from zato.common.api import CONTENT_TYPE, DATA_FORMAT, MISC, SIMPLE_IO, URL_PARAMS_PRIORITY, ZATO_NONE
from zato.common.exception import (
    BackendInvocationError, BadRequest, Forbidden, MethodNotAllowed,
    NotFound, ServiceMissingException, TooManyRequests, Unauthorized,
)
from zato.common.json_ import dumps
from zato.server.connection.http_soap.channel import (
    RequestDispatcher, RequestHandler, _RequestMeta, status_response
)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

_test_cid = 'zcid-test-0001'

# ################################################################################################################################
# ################################################################################################################################

def _make_meta(
    http_method:'str'='GET',
    http_accept:'str'='accept_any_internal',
    path_info:'str'='/test/path',
    wsgi_raw_uri:'str'='/test/path',
    wsgi_remote_port:'str'='12345',
) -> '_RequestMeta':
    """ Builds a _RequestMeta with sane defaults.
    """
    out = _RequestMeta(
        http_method=http_method,
        http_accept=http_accept,
        path_info=path_info,
        wsgi_raw_uri=wsgi_raw_uri,
        wsgi_remote_port=wsgi_remote_port,
    )
    return out

# ################################################################################################################################

def _make_channel_item(overrides:'anydict | None'=None) -> 'anydict':
    """ Builds a minimal channel_item dict.
    """
    out = {
        'name': 'test.channel',
        'is_active': True,
        'service_name': 'test.service',
        'service_impl_name': 'test.service.impl',
        'match_target': '/test/path::GET::*::*',
        'data_format': DATA_FORMAT.JSON,
        'transport': 'plain_http',
        'content_encoding': '',
        'merge_url_params_req': True,
        'url_params_pri': 'qs-over-path',
        'params_pri': 'qs-over-path',
        'security_groups_ctx': None,
    }
    if overrides:
        out.update(overrides)
    return out

# ################################################################################################################################

def _make_sec(sec_def:'any_'=ZATO_NONE) -> 'MagicMock':
    """ Builds a mock security object.
    """
    out = MagicMock()
    out.sec_def = sec_def
    return out

# ################################################################################################################################

def _make_wsgi_environ(overrides:'anydict | None'=None) -> 'anydict':
    """ Builds a minimal WSGI environ dict.
    """
    out:'anydict' = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/test/path',
        'RAW_URI': '/test/path',
        'REMOTE_PORT': '12345',
        'HTTP_ACCEPT': '*/*',
        'wsgi.input': BytesIO(b''),
        'zato.http.response.headers': {},
    }
    if overrides:
        out.update(overrides)
    return out

# ################################################################################################################################

def _make_response(
    payload:'any_'=b'{"response":"ok"}',
    content_type:'str'='application/json',
    headers:'anydict | None'=None,
    status_code:'int'=200,
) -> 'MagicMock':
    """ Builds a mock response object.
    """
    out = MagicMock()
    out.payload = payload
    out.content_type = content_type
    out.headers = headers if headers is not None else {}
    out.status_code = status_code
    return out

# ################################################################################################################################

class _DispatcherCtx(NamedTuple):
    dispatcher: 'RequestDispatcher'
    mock_url_data: 'MagicMock'
    mock_handler: 'MagicMock'
    mock_handle: 'MagicMock'
    mock_check_security: 'MagicMock'
    mock_create_channel_params: 'MagicMock'

# ################################################################################################################################

def _make_dispatcher(
    channel_item:'anydict | None'=None,
    sec:'MagicMock | None'=None,
    response:'MagicMock | None'=None,
) -> '_DispatcherCtx':
    """ Builds a RequestDispatcher with all dependencies mocked.
    """
    if channel_item is None:
        channel_item = _make_channel_item()

    if sec is None:
        sec = _make_sec()

    if response is None:
        response = _make_response()

    server = MagicMock()
    server.rest_log_ignore = set()

    url_data = MagicMock()
    url_data.match.return_value = ('/test/path', channel_item)
    url_data.url_sec = {channel_item['match_target']: sec}

    request_handler = MagicMock()
    request_handler.handle.return_value = response
    request_handler.create_channel_params.return_value = {'param1': 'value1'}

    dispatcher = RequestDispatcher(
        server=server,
        url_data=url_data,
        request_handler=request_handler,
        simple_io_config={},
        return_tracebacks=False,
        default_error_message='Internal server error',
        http_methods_allowed=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'],
    )

    out = _DispatcherCtx(
        dispatcher=dispatcher,
        mock_url_data=url_data,
        mock_handler=request_handler,
        mock_handle=request_handler.handle,
        mock_check_security=url_data.check_security,
        mock_create_channel_params=request_handler.create_channel_params,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################

class ExtractPostDataTestCase(unittest.TestCase):
    """ Tests for _extract_post_data.
    """

# ################################################################################################################################

    def test_non_form_data_format_returns_empty_dict(self) -> 'None':
        """ When data_format is not FORM_DATA, an empty dict is returned.
        """
        ctx = _make_dispatcher()
        channel_item = _make_channel_item({'data_format': DATA_FORMAT.JSON})
        wsgi_environ = _make_wsgi_environ()

        result = ctx.dispatcher._extract_post_data(channel_item, wsgi_environ)

        self.assertEqual(result, {})

# ################################################################################################################################

    def test_form_data_format_wrong_content_type_returns_empty_dict(self) -> 'None':
        """ When data_format is FORM_DATA but content type does not match, an empty dict is returned.
        """
        ctx = _make_dispatcher()
        channel_item = _make_channel_item({'data_format': SIMPLE_IO.FORMAT.FORM_DATA})
        wsgi_environ = _make_wsgi_environ({'CONTENT_TYPE': 'application/json'})

        result = ctx.dispatcher._extract_post_data(channel_item, wsgi_environ)

        self.assertEqual(result, {})

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.util_get_form_data')
    def test_form_data_format_matching_content_type_returns_parsed_data(self, mock_get_form_data:'MagicMock') -> 'None':
        """ When data_format is FORM_DATA and content type matches, parsed form data is returned.
        """
        mock_get_form_data.return_value = {'key': 'value'}
        ctx = _make_dispatcher()
        channel_item = _make_channel_item({'data_format': SIMPLE_IO.FORMAT.FORM_DATA})
        wsgi_environ = _make_wsgi_environ({'CONTENT_TYPE': 'application/x-www-form-urlencoded'})

        result = ctx.dispatcher._extract_post_data(channel_item, wsgi_environ)

        self.assertEqual(result, {'key': 'value'})

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.util_get_form_data')
    def test_form_data_sets_oauth_post_data(self, mock_get_form_data:'MagicMock') -> 'None':
        """ When form data is extracted, it is also stored in wsgi_environ under 'zato.oauth.post_data'.
        """
        mock_get_form_data.return_value = {'token': 'abc'}
        ctx = _make_dispatcher()
        channel_item = _make_channel_item({'data_format': SIMPLE_IO.FORMAT.FORM_DATA})
        wsgi_environ = _make_wsgi_environ({'CONTENT_TYPE': 'application/x-www-form-urlencoded'})

        _ = ctx.dispatcher._extract_post_data(channel_item, wsgi_environ)

        self.assertEqual(wsgi_environ['zato.oauth.post_data'], {'token': 'abc'})

# ################################################################################################################################

    def test_form_data_no_content_type_header_returns_empty_dict(self) -> 'None':
        """ When CONTENT_TYPE is missing from wsgi_environ, an empty dict is returned.
        """
        ctx = _make_dispatcher()
        channel_item = _make_channel_item({'data_format': SIMPLE_IO.FORMAT.FORM_DATA})
        wsgi_environ = _make_wsgi_environ()

        result = ctx.dispatcher._extract_post_data(channel_item, wsgi_environ)

        self.assertEqual(result, {})

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.util_get_form_data')
    def test_multipart_form_data_content_type(self, mock_get_form_data:'MagicMock') -> 'None':
        """ When content type starts with 'multipart/form-data', form data is extracted.
        """
        mock_get_form_data.return_value = {'file': 'data'}
        ctx = _make_dispatcher()
        channel_item = _make_channel_item({'data_format': SIMPLE_IO.FORMAT.FORM_DATA})
        wsgi_environ = _make_wsgi_environ({'CONTENT_TYPE': 'multipart/form-data; boundary=---abc'})

        result = ctx.dispatcher._extract_post_data(channel_item, wsgi_environ)

        self.assertEqual(result, {'file': 'data'})

# ################################################################################################################################
# ################################################################################################################################

class CheckSecurityTestCase(unittest.TestCase):
    """ Tests for _check_security.
    """

# ################################################################################################################################

    def test_sec_def_is_zato_none_skips_check(self) -> 'None':
        """ When sec_def is ZATO_NONE, check_security is not called.
        """
        ctx = _make_dispatcher(sec=_make_sec(ZATO_NONE))
        channel_item = _make_channel_item()
        meta = _make_meta()
        wsgi_environ = _make_wsgi_environ()
        worker_store = MagicMock()

        ctx.dispatcher._check_security(
            _test_cid, meta, channel_item, wsgi_environ, b'payload', {}, worker_store)

        ctx.mock_check_security.assert_not_called()

# ################################################################################################################################

    def test_sec_def_not_zato_none_calls_check_security(self) -> 'None':
        """ When sec_def is not ZATO_NONE, check_security is called with correct args.
        Uses 'APIKEY' which sorts lower than 'ZATO_NONE' to kill the > mutant.
        """
        sec = _make_sec('APIKEY')
        ctx = _make_dispatcher(sec=sec)
        channel_item = _make_channel_item()
        meta = _make_meta()
        wsgi_environ = _make_wsgi_environ()
        worker_store = MagicMock()

        ctx.dispatcher._check_security(
            _test_cid, meta, channel_item, wsgi_environ, b'payload', {}, worker_store)

        ctx.mock_check_security.assert_called_once_with(
            sec, _test_cid, channel_item, meta.path_info,
            b'payload', wsgi_environ, {}, worker_store, enforce_auth=True)

# ################################################################################################################################

    def test_check_security_raises_unauthorized_propagates(self) -> 'None':
        """ When check_security raises Unauthorized, it propagates.
        """
        sec = _make_sec('basic_auth')
        ctx = _make_dispatcher(sec=sec)
        ctx.mock_check_security.side_effect = Unauthorized(_test_cid, 'Bad creds', 'basic')
        channel_item = _make_channel_item()
        meta = _make_meta()
        wsgi_environ = _make_wsgi_environ()
        worker_store = MagicMock()

        with self.assertRaises(Unauthorized):
            ctx.dispatcher._check_security(
                _test_cid, meta, channel_item, wsgi_environ, b'payload', {}, worker_store)

# ################################################################################################################################

    def test_security_groups_ctx_none_skips_group_check(self) -> 'None':
        """ When security_groups_ctx is None, group check is skipped.
        """
        ctx = _make_dispatcher()
        mock_groups_check = MagicMock()
        ctx.dispatcher.check_security_via_groups = mock_groups_check # type: ignore
        channel_item = _make_channel_item({'security_groups_ctx': None})
        meta = _make_meta()
        wsgi_environ = _make_wsgi_environ()
        worker_store = MagicMock()

        ctx.dispatcher._check_security(
            _test_cid, meta, channel_item, wsgi_environ, b'payload', {}, worker_store)

        mock_groups_check.assert_not_called()

# ################################################################################################################################

    def test_security_groups_no_members_skips_group_check(self) -> 'None':
        """ When security_groups_ctx has no members, group check is skipped.
        """
        groups_ctx = MagicMock()
        groups_ctx.has_members.return_value = False

        ctx = _make_dispatcher()
        mock_groups_check = MagicMock()
        ctx.dispatcher.check_security_via_groups = mock_groups_check # type: ignore
        channel_item = _make_channel_item({'security_groups_ctx': groups_ctx})
        meta = _make_meta()
        wsgi_environ = _make_wsgi_environ()
        worker_store = MagicMock()

        ctx.dispatcher._check_security(
            _test_cid, meta, channel_item, wsgi_environ, b'payload', {}, worker_store)

        mock_groups_check.assert_not_called()

# ################################################################################################################################

    def test_security_groups_with_members_calls_check(self) -> 'None':
        """ When security_groups_ctx has members, check_security_via_groups is called.
        """
        groups_ctx = MagicMock()
        groups_ctx.has_members.return_value = True

        ctx = _make_dispatcher()
        mock_groups_check = MagicMock()
        ctx.dispatcher.check_security_via_groups = mock_groups_check # type: ignore
        channel_item = _make_channel_item({'security_groups_ctx': groups_ctx})
        meta = _make_meta()
        wsgi_environ = _make_wsgi_environ()
        worker_store = MagicMock()

        ctx.dispatcher._check_security(
            _test_cid, meta, channel_item, wsgi_environ, b'payload', {}, worker_store)

        mock_groups_check.assert_called_once_with(
            _test_cid, 'test.channel', groups_ctx, wsgi_environ)

# ################################################################################################################################

    def test_security_groups_raises_forbidden_propagates(self) -> 'None':
        """ When check_security_via_groups raises Forbidden, it propagates.
        """
        groups_ctx = MagicMock()
        groups_ctx.has_members.return_value = True

        ctx = _make_dispatcher()
        ctx.dispatcher.check_security_via_groups = MagicMock(side_effect=Forbidden(_test_cid, 'Denied')) # type: ignore
        channel_item = _make_channel_item({'security_groups_ctx': groups_ctx})
        meta = _make_meta()
        wsgi_environ = _make_wsgi_environ()
        worker_store = MagicMock()

        with self.assertRaises(Forbidden):
            ctx.dispatcher._check_security(
                _test_cid, meta, channel_item, wsgi_environ, b'payload', {}, worker_store)

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.logger')
    def test_needs_details_logs_debug_info(self, mock_logger:'MagicMock') -> 'None':
        """ When _needs_details is True, debug info is logged.
        """
        sec = _make_sec('basic_auth')
        ctx = _make_dispatcher(sec=sec)
        channel_item = _make_channel_item()
        meta = _make_meta()
        wsgi_environ = _make_wsgi_environ()
        worker_store = MagicMock()

        ctx.dispatcher._check_security(
            _test_cid, meta, channel_item, wsgi_environ, b'payload', {}, worker_store,
            _needs_details=True)

        self.assertTrue(mock_logger.info.called)

# ################################################################################################################################
# ################################################################################################################################

class InvokeServiceTestCase(unittest.TestCase):
    """ Tests for _invoke_service.
    """

# ################################################################################################################################

    def test_merge_url_params_true_calls_create_channel_params(self) -> 'None':
        """ When merge_url_params_req is True, create_channel_params is called.
        """
        ctx = _make_dispatcher()
        channel_item = _make_channel_item({'merge_url_params_req': True})
        meta = _make_meta()
        wsgi_environ = _make_wsgi_environ()
        worker_store = MagicMock()

        _ = ctx.dispatcher._invoke_service(
            _test_cid, meta, '/test/path', channel_item, wsgi_environ,
            b'payload', {}, worker_store, {})

        ctx.mock_create_channel_params.assert_called_once()

# ################################################################################################################################

    def test_merge_url_params_false_passes_empty_dict(self) -> 'None':
        """ When merge_url_params_req is False, empty dict is passed as channel_params.
        """
        response = _make_response()
        ctx = _make_dispatcher(response=response)
        channel_item = _make_channel_item({'merge_url_params_req': False})
        meta = _make_meta()
        wsgi_environ = _make_wsgi_environ()
        worker_store = MagicMock()

        _ = ctx.dispatcher._invoke_service(
            _test_cid, meta, '/test/path', channel_item, wsgi_environ,
            b'payload', {}, worker_store, {})

        call_args = ctx.mock_handle.call_args[0]
        channel_params_arg = call_args[9]
        self.assertEqual(channel_params_arg, {})

# ################################################################################################################################

    def test_handle_called_with_correct_args(self) -> 'None':
        """ handle is called with all the expected positional arguments.
        """
        response = _make_response()
        ctx = _make_dispatcher(response=response)
        channel_item = _make_channel_item()
        meta = _make_meta()
        wsgi_environ = _make_wsgi_environ()
        worker_store = MagicMock()
        headers_container = {'x-custom': 'val'}

        _ = ctx.dispatcher._invoke_service(
            _test_cid, meta, '/test/path', channel_item, wsgi_environ,
            b'payload', {'key': 'val'}, worker_store, headers_container)

        ctx.mock_handle.assert_called_once_with(
            _test_cid, '/test/path', channel_item, wsgi_environ,
            b'payload', worker_store, ctx.dispatcher.simple_io_config,
            {'key': 'val'}, meta.path_info, {'param1': 'value1'}, headers_container)

# ################################################################################################################################

    def test_handle_return_value_forwarded(self) -> 'None':
        """ The response from handle is returned by _invoke_service.
        """
        response = _make_response(payload=b'hello')
        ctx = _make_dispatcher(response=response)
        channel_item = _make_channel_item()
        meta = _make_meta()
        wsgi_environ = _make_wsgi_environ()
        worker_store = MagicMock()

        result = ctx.dispatcher._invoke_service(
            _test_cid, meta, '/test/path', channel_item, wsgi_environ,
            b'payload', {}, worker_store, {})

        self.assertIs(result, response)

# ################################################################################################################################

    def test_create_channel_params_called_with_correct_args(self) -> 'None':
        """ create_channel_params is called with url_match, channel_item, wsgi_environ, payload, post_data.
        """
        ctx = _make_dispatcher()
        channel_item = _make_channel_item({'merge_url_params_req': True})
        meta = _make_meta()
        wsgi_environ = _make_wsgi_environ()
        worker_store = MagicMock()

        _ = ctx.dispatcher._invoke_service(
            _test_cid, meta, '/test/path', channel_item, wsgi_environ,
            b'payload', {'post': 'data'}, worker_store, {})

        ctx.mock_create_channel_params.assert_called_once_with(
            '/test/path', channel_item, wsgi_environ, b'payload', {'post': 'data'})

# ################################################################################################################################
# ################################################################################################################################

class FormatResponseTestCase(unittest.TestCase):
    """ Tests for _format_response.
    """

# ################################################################################################################################

    def test_sets_content_type(self) -> 'None':
        """ Content-Type is set from response.content_type.
        """
        ctx = _make_dispatcher()
        response = _make_response(content_type='text/html')
        wsgi_environ = _make_wsgi_environ()

        _ = ctx.dispatcher._format_response(_make_channel_item(), wsgi_environ, response)

        self.assertEqual(wsgi_environ['zato.http.response.headers']['Content-Type'], 'text/html')

# ################################################################################################################################

    def test_merges_response_headers(self) -> 'None':
        """ Response headers are merged into wsgi_environ response headers.
        """
        ctx = _make_dispatcher()
        response = _make_response(headers={'X-Custom': 'abc'})
        wsgi_environ = _make_wsgi_environ()

        _ = ctx.dispatcher._format_response(_make_channel_item(), wsgi_environ, response)

        self.assertEqual(wsgi_environ['zato.http.response.headers']['X-Custom'], 'abc')

# ################################################################################################################################

    def test_sets_status_from_response_code(self) -> 'None':
        """ Status is set from status_response lookup.
        """
        ctx = _make_dispatcher()
        response = _make_response(status_code=200)
        wsgi_environ = _make_wsgi_environ()

        _ = ctx.dispatcher._format_response(_make_channel_item(), wsgi_environ, response)

        self.assertEqual(wsgi_environ['zato.http.response.status'], status_response[200])

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.GzipFile')
    @patch('zato.server.connection.http_soap.channel.StringIO')
    def test_gzip_encoding_sets_header(self, mock_stringio:'MagicMock', mock_gzipfile:'MagicMock') -> 'None':
        """ When content_encoding is 'gzip', Content-Encoding header is set.
        """
        mock_s = MagicMock()
        mock_s.getvalue.return_value = b'compressed'
        mock_stringio.return_value = mock_s
        mock_gzipfile.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_gzipfile.return_value.__exit__ = MagicMock(return_value=False)

        ctx = _make_dispatcher()
        channel_item = _make_channel_item({'content_encoding': 'gzip'})
        response = _make_response()
        wsgi_environ = _make_wsgi_environ()

        _ = ctx.dispatcher._format_response(channel_item, wsgi_environ, response)

        self.assertEqual(wsgi_environ['zato.http.response.headers']['Content-Encoding'], 'gzip')

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.GzipFile')
    @patch('zato.server.connection.http_soap.channel.StringIO')
    def test_gzip_encoding_compresses_payload(self, mock_stringio:'MagicMock', mock_gzipfile:'MagicMock') -> 'None':
        """ When content_encoding is 'gzip', the payload is gzip-compressed.
        """
        mock_s = MagicMock()
        mock_s.getvalue.return_value = b'compressed-bytes'
        mock_stringio.return_value = mock_s

        mock_f = MagicMock()
        mock_gzipfile.return_value.__enter__ = MagicMock(return_value=mock_f)
        mock_gzipfile.return_value.__exit__ = MagicMock(return_value=False)

        ctx = _make_dispatcher()
        channel_item = _make_channel_item({'content_encoding': 'gzip'})
        response = _make_response(payload=b'original')
        wsgi_environ = _make_wsgi_environ()

        _ = ctx.dispatcher._format_response(channel_item, wsgi_environ, response)

        mock_f.write.assert_called_once_with(b'original')

# ################################################################################################################################

    def test_non_gzip_no_content_encoding_header(self) -> 'None':
        """ When content_encoding is not 'gzip', no Content-Encoding header is set.
        """
        ctx = _make_dispatcher()
        channel_item = _make_channel_item({'content_encoding': ''})
        response = _make_response()
        wsgi_environ = _make_wsgi_environ()

        _ = ctx.dispatcher._format_response(channel_item, wsgi_environ, response)

        self.assertNotIn('Content-Encoding', wsgi_environ['zato.http.response.headers'])

# ################################################################################################################################

    def test_identity_encoding_no_gzip(self) -> 'None':
        """ When content_encoding is 'identity' (sorts higher than 'gzip'), gzip is NOT applied.
        """
        ctx = _make_dispatcher()
        channel_item = _make_channel_item({'content_encoding': 'identity'})
        response = _make_response(payload=b'not-compressed')
        wsgi_environ = _make_wsgi_environ()

        result = ctx.dispatcher._format_response(channel_item, wsgi_environ, response)

        self.assertEqual(result, b'not-compressed')
        self.assertNotIn('Content-Encoding', wsgi_environ['zato.http.response.headers'])

# ################################################################################################################################
# ################################################################################################################################

class HypothesisTestCase(unittest.TestCase):
    """ Fuzz tests for _authenticate_and_invoke sub-methods.
    """

# ################################################################################################################################

    @given(content_type=st.text(min_size=0, max_size=200))
    @hypothesis_settings(max_examples=50, suppress_health_check=[HealthCheck.differing_executors])
    def test_fuzz_extract_post_data_random_content_types(self, content_type:'str') -> 'None':
        """ _extract_post_data does not crash on random content types.
        """
        ctx = _make_dispatcher()
        channel_item = _make_channel_item({'data_format': SIMPLE_IO.FORMAT.FORM_DATA})
        wsgi_environ = _make_wsgi_environ({'CONTENT_TYPE': content_type})

        result = ctx.dispatcher._extract_post_data(channel_item, wsgi_environ)

        self.assertIsInstance(result, dict)

# ################################################################################################################################

    @given(payload_str=st.text(min_size=0, max_size=500))
    @hypothesis_settings(max_examples=50, suppress_health_check=[HealthCheck.differing_executors])
    def test_fuzz_format_response_random_payloads(self, payload_str:'str') -> 'None':
        """ _format_response does not crash on random payload strings.
        """
        ctx = _make_dispatcher()
        channel_item = _make_channel_item()
        wsgi_environ = _make_wsgi_environ()
        response = _make_response(payload=payload_str)

        result = ctx.dispatcher._format_response(channel_item, wsgi_environ, response)

        self.assertEqual(result, payload_str)

# ################################################################################################################################

    @given(path_info=st.text(min_size=1, max_size=200))
    @hypothesis_settings(max_examples=50, suppress_health_check=[HealthCheck.differing_executors])
    def test_fuzz_check_security_no_crash(self, path_info:'str') -> 'None':
        """ _check_security does not crash on random path_info values.
        """
        ctx = _make_dispatcher(sec=_make_sec(ZATO_NONE))
        channel_item = _make_channel_item()
        meta = _make_meta(path_info=path_info)
        wsgi_environ = _make_wsgi_environ()
        worker_store = MagicMock()

        ctx.dispatcher._check_security(
            _test_cid, meta, channel_item, wsgi_environ, b'', {}, worker_store)

# ################################################################################################################################
# ################################################################################################################################

class GetFlattenedTestCase(unittest.TestCase):
    """ Tests for RequestHandler._get_flattened.
    """

# ################################################################################################################################

    def _make_handler(self) -> 'RequestHandler':
        """ Builds a RequestHandler with a mocked server.
        """
        server = MagicMock()
        out = RequestHandler(server)
        return out

# ################################################################################################################################

    def test_empty_params_returns_empty_dict(self) -> 'None':
        """ When params is empty bytes, an empty dict is returned.
        """
        handler = self._make_handler()

        result = handler._get_flattened(b'')

        self.assertEqual(result, {})

# ################################################################################################################################

    def test_single_value_unwraps_from_list(self) -> 'None':
        """ Single-value query params are unwrapped from the list.
        """
        handler = self._make_handler()

        result = handler._get_flattened(b'foo=bar')

        self.assertEqual(result, {'foo': 'bar'})

# ################################################################################################################################

    def test_multi_value_keeps_list(self) -> 'None':
        """ Multi-value query params keep the list form.
        """
        handler = self._make_handler()

        result = handler._get_flattened(b'foo=bar&foo=baz')

        self.assertEqual(result, {'foo': ['bar', 'baz']})

# ################################################################################################################################

    def test_multiple_keys_single_values(self) -> 'None':
        """ Multiple distinct keys each with a single value are all unwrapped.
        """
        handler = self._make_handler()

        result = handler._get_flattened(b'a=1&b=2&c=3')

        self.assertEqual(result, {'a': '1', 'b': '2', 'c': '3'})

# ################################################################################################################################

    def test_mixed_single_and_multi(self) -> 'None':
        """ Mix of single-value and multi-value keys.
        """
        handler = self._make_handler()

        result = handler._get_flattened(b'x=1&y=2&y=3')

        self.assertEqual(result, {'x': '1', 'y': ['2', '3']})

# ################################################################################################################################
# ################################################################################################################################

class CreateChannelParamsTestCase(unittest.TestCase):
    """ Tests for RequestHandler.create_channel_params.
    """

# ################################################################################################################################

    def _make_handler(self) -> 'RequestHandler':
        """ Builds a RequestHandler with a mocked server.
        """
        server = MagicMock()
        out = RequestHandler(server)
        return out

# ################################################################################################################################

    def _make_item(self, url_params_pri:'str'=URL_PARAMS_PRIORITY.QS_OVER_PATH, data_format:'str'='json') -> 'MagicMock':
        """ Builds a mock channel_item with attribute access.
        """
        item = MagicMock()
        item.url_params_pri = url_params_pri
        item.data_format = data_format
        return item

# ################################################################################################################################

    def test_qs_over_path_qs_overrides_conflicting_path_param(self) -> 'None':
        """ In QS_OVER_PATH mode, query string values override path params on key conflict.
        """
        handler = self._make_handler()
        item = self._make_item(URL_PARAMS_PRIORITY.QS_OVER_PATH)
        wsgi_environ:'anydict' = {'QUERY_STRING': 'shared=qs_val', 'zato.http.response.headers': {}}

        result = handler.create_channel_params({'shared': 'path_val'}, item, wsgi_environ, b'', None)

        self.assertEqual(result['shared'], 'qs_val')

# ################################################################################################################################

    def test_path_over_qs_path_params_override_qs(self) -> 'None':
        """ In PATH_OVER_QS mode, path params override query string values.
        """
        handler = self._make_handler()
        item = self._make_item(URL_PARAMS_PRIORITY.PATH_OVER_QS)
        wsgi_environ:'anydict' = {'QUERY_STRING': 'key=qs_val', 'zato.http.response.headers': {}}

        result = handler.create_channel_params({'key': 'path_val'}, item, wsgi_environ, b'', None)

        self.assertEqual(result['key'], 'path_val')

# ################################################################################################################################

    def test_qs_over_path_no_query_string(self) -> 'None':
        """ In QS_OVER_PATH mode with no query string, path params are unchanged.
        """
        handler = self._make_handler()
        item = self._make_item(URL_PARAMS_PRIORITY.QS_OVER_PATH)
        wsgi_environ:'anydict' = {'QUERY_STRING': '', 'zato.http.response.headers': {}}

        result = handler.create_channel_params({'pk': 'pv'}, item, wsgi_environ, b'', None)

        self.assertEqual(result, {'pk': 'pv'})

# ################################################################################################################################

    def test_path_over_qs_no_query_string(self) -> 'None':
        """ In PATH_OVER_QS mode with no query string, path params are returned.
        """
        handler = self._make_handler()
        item = self._make_item(URL_PARAMS_PRIORITY.PATH_OVER_QS)
        wsgi_environ:'anydict' = {'QUERY_STRING': '', 'zato.http.response.headers': {}}

        result = handler.create_channel_params({'pk': 'pv'}, item, wsgi_environ, b'', None)

        self.assertEqual(result, {'pk': 'pv'})

# ################################################################################################################################

    def test_post_data_provided_uses_post_data_directly(self) -> 'None':
        """ When post_data is provided, it is used directly without calling _get_flattened.
        """
        handler = self._make_handler()
        item = self._make_item(URL_PARAMS_PRIORITY.QS_OVER_PATH)
        wsgi_environ:'anydict' = {'QUERY_STRING': '', 'zato.http.response.headers': {}}

        _ = handler.create_channel_params({}, item, wsgi_environ, b'raw', {'post_key': 'post_val'})

        self.assertEqual(wsgi_environ['zato.http.POST'], {'post_key': 'post_val'})

# ################################################################################################################################

    def test_no_data_format_calls_get_flattened_on_raw_request(self) -> 'None':
        """ When channel_item.data_format is falsy, _get_flattened is called on raw_request.
        """
        handler = self._make_handler()
        item = self._make_item(URL_PARAMS_PRIORITY.QS_OVER_PATH, data_format='')
        wsgi_environ:'anydict' = {'QUERY_STRING': '', 'zato.http.response.headers': {}}

        _ = handler.create_channel_params({}, item, wsgi_environ, b'x=hello', None)

        self.assertEqual(wsgi_environ['zato.http.POST'], {'x': 'hello'})

# ################################################################################################################################

    def test_data_format_set_no_post_data_gives_empty_post(self) -> 'None':
        """ When data_format is truthy and no post_data, POST is empty dict.
        """
        handler = self._make_handler()
        item = self._make_item(URL_PARAMS_PRIORITY.QS_OVER_PATH, data_format='json')
        wsgi_environ:'anydict' = {'QUERY_STRING': '', 'zato.http.response.headers': {}}

        _ = handler.create_channel_params({}, item, wsgi_environ, b'ignored', None)

        self.assertEqual(wsgi_environ['zato.http.POST'], {})

# ################################################################################################################################

    def test_sets_zato_http_get(self) -> 'None':
        """ wsgi_environ['zato.http.GET'] is set to the parsed query string.
        """
        handler = self._make_handler()
        item = self._make_item(URL_PARAMS_PRIORITY.QS_OVER_PATH)
        wsgi_environ:'anydict' = {'QUERY_STRING': 'k=v', 'zato.http.response.headers': {}}

        _ = handler.create_channel_params({}, item, wsgi_environ, b'', None)

        self.assertEqual(wsgi_environ['zato.http.GET'], {'k': 'v'})

# ################################################################################################################################

    def test_path_over_qs_with_qs_and_path_params(self) -> 'None':
        """ PATH_OVER_QS: qs is base, path params are applied on top.
        """
        handler = self._make_handler()
        item = self._make_item(URL_PARAMS_PRIORITY.PATH_OVER_QS)
        wsgi_environ:'anydict' = {'QUERY_STRING': 'shared=qs_val&only_qs=q', 'zato.http.response.headers': {}}

        result = handler.create_channel_params({'shared': 'path_val', 'only_path': 'p'}, item, wsgi_environ, b'', None)

        self.assertEqual(result['shared'], 'path_val')
        self.assertEqual(result['only_qs'], 'q')
        self.assertEqual(result['only_path'], 'p')

# ################################################################################################################################
# ################################################################################################################################

class GetResponseFromCacheTestCase(unittest.TestCase):
    """ Tests for RequestHandler.get_response_from_cache.
    """

# ################################################################################################################################

    def _make_handler(self) -> 'RequestHandler':
        """ Builds a RequestHandler with a mocked server.
        """
        server = MagicMock()
        out = RequestHandler(server)
        return out

# ################################################################################################################################

    def test_no_custom_hash_default_hash_computation(self) -> 'None':
        """ When service.get_request_hash is falsy, default sha256 hash is used.
        """
        handler = self._make_handler()
        handler.server.get_from_cache.return_value = None

        service = MagicMock()
        service.get_request_hash = None

        channel_item = MagicMock()
        channel_item.__getitem__ = lambda self, k: {'id': 42, 'cache_type': 'builtin', 'cache_name': 'default'}[k]

        raw_request = b'{"customer":"123"}'
        channel_params:'anydict' = {'a': '1'}
        wsgi_environ:'anydict' = {'REQUEST_METHOD': 'POST', 'PATH_INFO': '/api/v1'}

        cache_key, response = handler.get_response_from_cache(
            service, raw_request, channel_item, channel_params, wsgi_environ)

        query_string = str(sorted(channel_params.items()))
        data = '%s%s%s%s' % ('POST', '/api/v1', query_string, raw_request)
        expected_hash = sha256(data.encode('utf8')).hexdigest()
        expected_hash_dashed = '-'.join([expected_hash[i:i+8] for i in range(0, len(expected_hash), 8)])
        expected_key = 'http-channel-42-%s' % expected_hash_dashed

        self.assertEqual(cache_key, expected_key)
        self.assertIsNone(response)

# ################################################################################################################################

    def test_cache_hit_returns_cached_response(self) -> 'None':
        """ When cache returns data, a _CachedResponse is returned.
        """
        handler = self._make_handler()
        cached_data = dumps({
            'payload': 'cached-payload',
            'content_type': 'text/plain',
            'headers': {'X-Cache': 'HIT'},
            'status_code': 200,
        })
        handler.server.get_from_cache.return_value = cached_data

        service = MagicMock()
        service.get_request_hash = None

        channel_item = MagicMock()
        channel_item.__getitem__ = lambda self, k: {'id': 7, 'cache_type': 'builtin', 'cache_name': 'default'}[k]

        cache_key, response = handler.get_response_from_cache(
            service, b'body', channel_item, {}, {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/x'})

        self.assertIsNotNone(response)
        self.assertEqual(response.payload, 'cached-payload')
        self.assertEqual(response.content_type, 'text/plain')
        self.assertEqual(response.headers, {'X-Cache': 'HIT'})
        self.assertEqual(response.status_code, 200)

# ################################################################################################################################

    def test_cache_miss_returns_none_response(self) -> 'None':
        """ When cache returns nothing, response is falsy.
        """
        handler = self._make_handler()
        handler.server.get_from_cache.return_value = None

        service = MagicMock()
        service.get_request_hash = None

        channel_item = MagicMock()
        channel_item.__getitem__ = lambda self, k: {'id': 1, 'cache_type': 'builtin', 'cache_name': 'default'}[k]

        _, response = handler.get_response_from_cache(
            service, b'', channel_item, {}, {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})

        self.assertFalse(response)

# ################################################################################################################################

    def test_custom_hash_function_used(self) -> 'None':
        """ When service.get_request_hash is truthy, it is called with _HashCtx.
        """
        handler = self._make_handler()
        handler.server.get_from_cache.return_value = None

        service = MagicMock()
        service.get_request_hash = MagicMock(return_value='custom-hash-value')

        channel_item = MagicMock()
        channel_item.__getitem__ = lambda self, k: {'id': 99, 'cache_type': 'builtin', 'cache_name': 'default'}[k]

        cache_key, _ = handler.get_response_from_cache(
            service, b'data', channel_item, {'p': '1'}, {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/test'})

        self.assertEqual(cache_key, 'http-channel-99-custom-hash-value')
        service.get_request_hash.assert_called_once()

# ################################################################################################################################

    def test_cache_key_format_includes_channel_id(self) -> 'None':
        """ Cache key always starts with 'http-channel-{id}-'.
        """
        handler = self._make_handler()
        handler.server.get_from_cache.return_value = None

        service = MagicMock()
        service.get_request_hash = None

        channel_item = MagicMock()
        channel_item.__getitem__ = lambda self, k: {'id': 555, 'cache_type': 'default', 'cache_name': 'my-cache'}[k]

        cache_key, _ = handler.get_response_from_cache(
            service, b'', channel_item, {}, {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})

        self.assertTrue(cache_key.startswith('http-channel-555-'))

# ################################################################################################################################

    def test_query_params_sorted_for_hash(self) -> 'None':
        """ Query params order does not affect the hash - they are sorted.
        """
        handler = self._make_handler()
        handler.server.get_from_cache.return_value = None

        service = MagicMock()
        service.get_request_hash = None

        channel_item = MagicMock()
        channel_item.__getitem__ = lambda self, k: {'id': 1, 'cache_type': 'b', 'cache_name': 'c'}[k]

        wsgi = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/p'}

        key1, _ = handler.get_response_from_cache(service, b'', channel_item, {'a': '1', 'b': '2'}, wsgi)
        key2, _ = handler.get_response_from_cache(service, b'', channel_item, {'b': '2', 'a': '1'}, wsgi)

        self.assertEqual(key1, key2)

# ################################################################################################################################
# ################################################################################################################################

class InvokeServiceSecDefTestCase(unittest.TestCase):
    """ Tests for _invoke_service sec_def branch and query params logic.
    """

# ################################################################################################################################

    def test_merge_params_with_sec_def_truthy(self) -> 'None':
        """ When sec_def is truthy, channel_params['sec_def'] must be set by request_handler.handle.
        """
        sec = _make_sec({'username': 'admin', 'sec_type': 'basic_auth'})
        ctx = _make_dispatcher(sec=sec)
        channel_item = _make_channel_item({'merge_url_params_req': True})
        meta = _make_meta()
        wsgi_environ = _make_wsgi_environ()
        worker_store = MagicMock()

        _ = ctx.dispatcher._invoke_service(
            _test_cid, meta, '/test/path', channel_item, wsgi_environ,
            b'payload', {}, worker_store, {})

        ctx.mock_create_channel_params.assert_called_once()

# ################################################################################################################################

    def test_merge_params_false_no_create_channel_params(self) -> 'None':
        """ When merge_url_params_req is False, create_channel_params is not called.
        """
        ctx = _make_dispatcher()
        channel_item = _make_channel_item({'merge_url_params_req': False})
        meta = _make_meta()
        wsgi_environ = _make_wsgi_environ()
        worker_store = MagicMock()

        _ = ctx.dispatcher._invoke_service(
            _test_cid, meta, '/test/path', channel_item, wsgi_environ,
            b'payload', {}, worker_store, {})

        ctx.mock_create_channel_params.assert_not_called()

# ################################################################################################################################
# ################################################################################################################################

class CheckSecurityGroupsTestCase(unittest.TestCase):
    """ Tests for check_security_via_groups - both basic_auth and apikey precedence.
    """

# ################################################################################################################################

    def test_both_basic_auth_and_apikey_raises_bad_request(self) -> 'None':
        """ When both HTTP_AUTHORIZATION and apikey header are present, BadRequest is raised.
        """
        ctx = _make_dispatcher()
        ctx.dispatcher.server.api_key_header_wsgi = 'HTTP_X_API_KEY'
        ctx.dispatcher.url_data.basic_auth_get_by_id = MagicMock()
        ctx.dispatcher.url_data.apikey_get_by_id = MagicMock()

        wsgi_environ = _make_wsgi_environ({
            'HTTP_AUTHORIZATION': 'Basic dXNlcjpwYXNz',
            'HTTP_X_API_KEY': 'some-key',
        })

        groups_ctx = MagicMock()

        with self.assertRaises(BadRequest):
            ctx.dispatcher.check_security_via_groups(
                _test_cid, 'test.channel', groups_ctx, wsgi_environ)

# ################################################################################################################################

    def test_only_basic_auth_info_calls_check_basic_auth(self) -> 'None':
        """ When only HTTP_AUTHORIZATION is present, check_security_basic_auth is called.
        """
        ctx = _make_dispatcher()
        ctx.dispatcher.server.api_key_header_wsgi = 'HTTP_X_API_KEY'

        groups_ctx = MagicMock()
        groups_ctx.check_security_basic_auth.return_value = 123
        ctx.dispatcher.url_data.basic_auth_get_by_id.return_value = {'username': 'u', 'sec_type': 'basic_auth'}

        wsgi_environ = _make_wsgi_environ({
            'HTTP_AUTHORIZATION': 'Basic dXNlcjpwYXNz',
        })

        with patch('zato.server.connection.http_soap.channel.extract_basic_auth', return_value=('user', 'pass')):
            with patch('zato.server.connection.http_soap.channel.enrich_with_sec_data') as mock_enrich:
                ctx.dispatcher.check_security_via_groups(
                    _test_cid, 'test.channel', groups_ctx, wsgi_environ)

        groups_ctx.check_security_basic_auth.assert_called_once_with(_test_cid, 'test.channel', 'user', 'pass')
        mock_enrich.assert_called_once()

# ################################################################################################################################

    def test_only_basic_auth_invalid_raises_forbidden(self) -> 'None':
        """ When basic_auth check fails (returns falsy), Forbidden is raised.
        """
        ctx = _make_dispatcher()
        ctx.dispatcher.server.api_key_header_wsgi = 'HTTP_X_API_KEY'

        groups_ctx = MagicMock()
        groups_ctx.check_security_basic_auth.return_value = None

        wsgi_environ = _make_wsgi_environ({
            'HTTP_AUTHORIZATION': 'Basic dXNlcjpwYXNz',
        })

        with patch('zato.server.connection.http_soap.channel.extract_basic_auth', return_value=('user', 'pass')):
            with self.assertRaises(Forbidden):
                ctx.dispatcher.check_security_via_groups(
                    _test_cid, 'test.channel', groups_ctx, wsgi_environ)

# ################################################################################################################################

    def test_only_apikey_calls_check_apikey(self) -> 'None':
        """ When only apikey header is present, check_security_apikey is called.
        """
        ctx = _make_dispatcher()
        ctx.dispatcher.server.api_key_header_wsgi = 'HTTP_X_API_KEY'

        groups_ctx = MagicMock()
        groups_ctx.check_security_apikey.return_value = 456
        ctx.dispatcher.url_data.apikey_get_by_id.return_value = {'api_key': 'k', 'sec_type': 'apikey'}

        wsgi_environ = _make_wsgi_environ({
            'HTTP_X_API_KEY': 'my-api-key',
        })

        with patch('zato.server.connection.http_soap.channel.enrich_with_sec_data') as mock_enrich:
            ctx.dispatcher.check_security_via_groups(
                _test_cid, 'test.channel', groups_ctx, wsgi_environ)

        groups_ctx.check_security_apikey.assert_called_once_with(_test_cid, 'test.channel', 'my-api-key')
        mock_enrich.assert_called_once()

# ################################################################################################################################

    def test_only_apikey_invalid_raises_forbidden(self) -> 'None':
        """ When apikey check fails (returns falsy), Forbidden is raised.
        """
        ctx = _make_dispatcher()
        ctx.dispatcher.server.api_key_header_wsgi = 'HTTP_X_API_KEY'

        groups_ctx = MagicMock()
        groups_ctx.check_security_apikey.return_value = None

        wsgi_environ = _make_wsgi_environ({
            'HTTP_X_API_KEY': 'bad-key',
        })

        with self.assertRaises(Forbidden):
            ctx.dispatcher.check_security_via_groups(
                _test_cid, 'test.channel', groups_ctx, wsgi_environ)

# ################################################################################################################################

    def test_neither_auth_nor_apikey_raises_forbidden(self) -> 'None':
        """ When neither basic auth nor apikey is present, Forbidden is raised.
        """
        ctx = _make_dispatcher()
        ctx.dispatcher.server.api_key_header_wsgi = 'HTTP_X_API_KEY'

        groups_ctx = MagicMock()
        wsgi_environ = _make_wsgi_environ()

        with self.assertRaises(Forbidden):
            ctx.dispatcher.check_security_via_groups(
                _test_cid, 'test.channel', groups_ctx, wsgi_environ)

# ################################################################################################################################
# ################################################################################################################################

class MatchURLTestCase(unittest.TestCase):
    """ Tests for _match_url.
    """

# ################################################################################################################################

    def test_channel_item_none_sets_channel_name_to_none_string(self) -> 'None':
        """ When channel_item is falsy, channel_name is set to '(None)'.
        """
        ctx = _make_dispatcher()
        ctx.mock_url_data.match.return_value = (None, None)
        wsgi_environ = _make_wsgi_environ()

        result = ctx.dispatcher._match_url(_make_meta(), wsgi_environ)

        self.assertEqual(result.channel_name, '(None)')

# ################################################################################################################################

    def test_channel_item_truthy_uses_name(self) -> 'None':
        """ When channel_item is truthy, channel_name comes from channel_item['name'].
        """
        channel_item = _make_channel_item({'name': 'my.channel'})
        ctx = _make_dispatcher(channel_item=channel_item)
        wsgi_environ = _make_wsgi_environ()

        result = ctx.dispatcher._match_url(_make_meta(), wsgi_environ)

        self.assertEqual(result.channel_name, 'my.channel')

# ################################################################################################################################

    def test_reads_wsgi_input(self) -> 'None':
        """ The payload is read from wsgi.input.
        """
        ctx = _make_dispatcher()
        wsgi_environ = _make_wsgi_environ({'wsgi.input': BytesIO(b'request-body')})

        result = ctx.dispatcher._match_url(_make_meta(), wsgi_environ)

        self.assertEqual(result.payload, b'request-body')

# ################################################################################################################################

    def test_sets_zato_channel_item(self) -> 'None':
        """ wsgi_environ['zato.channel_item'] is set to the matched channel_item.
        """
        channel_item = _make_channel_item()
        ctx = _make_dispatcher(channel_item=channel_item)
        wsgi_environ = _make_wsgi_environ()

        _ = ctx.dispatcher._match_url(_make_meta(), wsgi_environ)

        self.assertIs(wsgi_environ['zato.channel_item'], channel_item)

# ################################################################################################################################

    def test_sets_zato_http_raw_request(self) -> 'None':
        """ wsgi_environ['zato.http.raw_request'] is set to the raw payload.
        """
        ctx = _make_dispatcher()
        wsgi_environ = _make_wsgi_environ({'wsgi.input': BytesIO(b'the-body')})

        _ = ctx.dispatcher._match_url(_make_meta(), wsgi_environ)

        self.assertEqual(wsgi_environ['zato.http.raw_request'], b'the-body')

# ################################################################################################################################
# ################################################################################################################################

class LogIncomingRequestTestCase(unittest.TestCase):
    """ Tests for _log_incoming_request.
    """

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.logger')
    def test_path_in_ignore_list_no_log(self, mock_logger:'MagicMock') -> 'None':
        """ When path_info is in rest_log_ignore, nothing is logged.
        """
        ctx = _make_dispatcher()
        ctx.dispatcher.server.rest_log_ignore = {'/health'}
        channel_item = _make_channel_item()
        meta = _make_meta(path_info='/health')

        ctx.dispatcher._log_incoming_request(
            _test_cid, meta, channel_item, 'test.channel', b'payload', 'agent', '1.2.3.4')

        mock_logger.info.assert_not_called()

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.logger')
    def test_path_not_in_ignore_list_logs(self, mock_logger:'MagicMock') -> 'None':
        """ When path_info is not in rest_log_ignore, info is logged.
        """
        ctx = _make_dispatcher()
        ctx.dispatcher.server.rest_log_ignore = set()
        channel_item = _make_channel_item()
        meta = _make_meta(path_info='/api/test')

        ctx.dispatcher._log_incoming_request(
            _test_cid, meta, channel_item, 'test.channel', b'payload', 'agent', '1.2.3.4')

        mock_logger.info.assert_called_once()

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.logger')
    def test_gzip_content_encoding_logs_payload_len(self, mock_logger:'MagicMock') -> 'None':
        """ When content_encoding is 'gzip', the logged len reflects the payload length.
        """
        ctx = _make_dispatcher()
        ctx.dispatcher.server.rest_log_ignore = set()
        channel_item = _make_channel_item({'content_encoding': 'gzip'})
        meta = _make_meta(path_info='/api/gz')
        payload = b'x' * 100

        ctx.dispatcher._log_incoming_request(
            _test_cid, meta, channel_item, 'test.channel', payload, 'agent', '1.2.3.4')

        call_args = mock_logger.info.call_args[0][0]
        self.assertIn('len=100', call_args)

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.logger')
    def test_non_gzip_content_encoding_logs_payload_len(self, mock_logger:'MagicMock') -> 'None':
        """ When content_encoding is not 'gzip', the logged len still reflects the raw payload length.
        """
        ctx = _make_dispatcher()
        ctx.dispatcher.server.rest_log_ignore = set()
        channel_item = _make_channel_item({'content_encoding': ''})
        meta = _make_meta(path_info='/api/plain')
        payload = b'y' * 50

        ctx.dispatcher._log_incoming_request(
            _test_cid, meta, channel_item, 'test.channel', payload, 'agent', '1.2.3.4')

        call_args = mock_logger.info.call_args[0][0]
        self.assertIn('len=50', call_args)

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.logger')
    def test_channel_item_falsy_logs_no_channel(self, mock_logger:'MagicMock') -> 'None':
        """ When channel_item is falsy, service_name is '<no-channel>'.
        """
        ctx = _make_dispatcher()
        ctx.dispatcher.server.rest_log_ignore = set()
        meta = _make_meta(path_info='/api/test')

        ctx.dispatcher._log_incoming_request(
            _test_cid, meta, None, 'none-channel', b'', 'agent', '1.2.3.4')  # type: ignore

        call_args = mock_logger.info.call_args[0][0]
        self.assertIn('<no-channel>', call_args)

# ################################################################################################################################
# ################################################################################################################################

class ExtractPostDataMutantKillTestCase(unittest.TestCase):
    """ Additional tests to kill _extract_post_data surviving mutants.
    """

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.util_get_form_data')
    def test_form_data_exact_content_type_match(self, mock_get_form_data:'MagicMock') -> 'None':
        """ Tests that 'application/x-www-form-urlencoded' specifically triggers form data extraction.
        """
        mock_get_form_data.return_value = {'field': 'val'}
        ctx = _make_dispatcher()
        channel_item = _make_channel_item({'data_format': SIMPLE_IO.FORMAT.FORM_DATA})
        wsgi_environ = _make_wsgi_environ({'CONTENT_TYPE': 'application/x-www-form-urlencoded'})

        result = ctx.dispatcher._extract_post_data(channel_item, wsgi_environ)

        self.assertEqual(result, {'field': 'val'})
        mock_get_form_data.assert_called_once_with(wsgi_environ)

# ################################################################################################################################

    def test_non_form_data_format_lower_does_not_extract(self) -> 'None':
        """ When data_format sorts lower than FORM_DATA ('csv' < 'form'), form data is not extracted.
        Kills the <= mutant.
        """
        ctx = _make_dispatcher()
        channel_item = _make_channel_item({'data_format': 'csv'})
        wsgi_environ = _make_wsgi_environ({'CONTENT_TYPE': 'application/x-www-form-urlencoded'})

        result = ctx.dispatcher._extract_post_data(channel_item, wsgi_environ)

        self.assertEqual(result, {})

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.util_get_form_data')
    def test_non_form_data_format_higher_does_not_extract(self, mock_get_form_data:'MagicMock') -> 'None':
        """ When data_format sorts higher than FORM_DATA ('json' > 'form') with matching content type,
        form data is still NOT extracted. Kills the >= mutant.
        """
        mock_get_form_data.return_value = {'should_not': 'be_called'}
        ctx = _make_dispatcher()
        channel_item = _make_channel_item({'data_format': DATA_FORMAT.JSON})
        wsgi_environ = _make_wsgi_environ({'CONTENT_TYPE': 'application/x-www-form-urlencoded'})

        result = ctx.dispatcher._extract_post_data(channel_item, wsgi_environ)

        self.assertEqual(result, {})
        mock_get_form_data.assert_not_called()

# ################################################################################################################################
# ################################################################################################################################

class CheckSecurityNeedsDetailsTestCase(unittest.TestCase):
    """ Tests targeting the _needs_details logging branch in _check_security.
    """

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.logger')
    def test_needs_details_true_logs_exact_separator(self, mock_logger:'MagicMock') -> 'None':
        """ When _needs_details is True, exactly '*' * 60 is logged (not 59 or 61).
        """
        sec = _make_sec('basic_auth')
        ctx = _make_dispatcher(sec=sec)
        channel_item = _make_channel_item()
        meta = _make_meta()
        wsgi_environ = _make_wsgi_environ()
        worker_store = MagicMock()

        ctx.dispatcher._check_security(
            _test_cid, meta, channel_item, wsgi_environ, b'payload', {}, worker_store,
            _needs_details=True)

        first_info_call = mock_logger.info.call_args_list[0]
        self.assertEqual(first_info_call[0][0], '*' * 60)

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.logger')
    def test_needs_details_true_logs_sorted_environ(self, mock_logger:'MagicMock') -> 'None':
        """ When _needs_details is True, sorted wsgi_environ items are logged.
        """
        sec = _make_sec('basic_auth')
        ctx = _make_dispatcher(sec=sec)
        channel_item = _make_channel_item()
        meta = _make_meta()
        wsgi_environ = _make_wsgi_environ({'AAA_KEY': 'aaa_val', 'ZZZ_KEY': 'zzz_val'})
        worker_store = MagicMock()

        ctx.dispatcher._check_security(
            _test_cid, meta, channel_item, wsgi_environ, b'payload', {}, worker_store,
            _needs_details=True)

        logged_values = [str(c) for c in mock_logger.info.call_args_list]
        aaa_idx = next(i for i, c in enumerate(logged_values) if 'AAA_KEY' in c)
        zzz_idx = next(i for i, c in enumerate(logged_values) if 'ZZZ_KEY' in c)
        self.assertLess(aaa_idx, zzz_idx)

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.logger')
    def test_needs_details_false_no_separator(self, mock_logger:'MagicMock') -> 'None':
        """ When _needs_details is False, no separator is logged.
        """
        sec = _make_sec('basic_auth')
        ctx = _make_dispatcher(sec=sec)
        channel_item = _make_channel_item()
        meta = _make_meta()
        wsgi_environ = _make_wsgi_environ()
        worker_store = MagicMock()

        ctx.dispatcher._check_security(
            _test_cid, meta, channel_item, wsgi_environ, b'payload', {}, worker_store,
            _needs_details=False)

        logged_calls = [str(c) for c in mock_logger.info.call_args_list]
        separator_found = any('*' * 60 in c for c in logged_calls)
        self.assertFalse(separator_found)

# ################################################################################################################################
# ################################################################################################################################

class HandleDispatchErrorTestCase(unittest.TestCase):
    """ Tests for _handle_dispatch_error - 100% line coverage.
    """

# ################################################################################################################################

    def _call(self, e:'Exception', channel_item:'anydict | None'=None, wsgi_environ:'anydict | None'=None) -> 'tuple':
        """ Helper that calls _handle_dispatch_error and returns (result, wsgi_environ).
        """
        ctx = _make_dispatcher()
        if channel_item is None:
            channel_item = _make_channel_item()
        if wsgi_environ is None:
            wsgi_environ = _make_wsgi_environ()
        result = ctx.dispatcher._handle_dispatch_error(_test_cid, e, channel_item, wsgi_environ)
        return result, wsgi_environ

# ################################################################################################################################

    def test_unauthorized_sets_401_status(self) -> 'None':
        result, env = self._call(Unauthorized(_test_cid, 'No auth', 'Basic realm="test"'))

        self.assertIn('401', env['zato.http.response.status'])

# ################################################################################################################################

    def test_unauthorized_with_challenge_sets_www_authenticate(self) -> 'None':
        result, env = self._call(Unauthorized(_test_cid, 'No auth', 'Basic realm="test"'))

        self.assertEqual(env['zato.http.response.headers']['WWW-Authenticate'], 'Basic realm="test"')

# ################################################################################################################################

    def test_unauthorized_without_challenge_no_www_authenticate(self) -> 'None':
        result, env = self._call(Unauthorized(_test_cid, 'No auth', ''))

        self.assertNotIn('WWW-Authenticate', env['zato.http.response.headers'])

# ################################################################################################################################

    def test_bad_request_admin_channel_returns_msg(self) -> 'None':
        channel_item = _make_channel_item({'name': MISC.DefaultAdminInvokeChannel})
        result, env = self._call(BadRequest(_test_cid, 'Admin details'), channel_item=channel_item)

        self.assertIn('Admin details', result)
        self.assertIn('400', env['zato.http.response.status'])

# ################################################################################################################################

    def test_bad_request_non_admin_needs_msg_true(self) -> 'None':
        exc = BadRequest(_test_cid, 'Visible msg')
        exc.needs_msg = True
        result, env = self._call(exc)

        self.assertIn('Visible msg', result)

# ################################################################################################################################

    def test_bad_request_non_admin_needs_msg_false(self) -> 'None':
        exc = BadRequest(_test_cid, 'Secret msg')
        exc.needs_msg = False
        result, env = self._call(exc)

        self.assertIn('Bad request', result)
        self.assertNotIn('Secret msg', result)

# ################################################################################################################################

    def test_not_found_sets_404_status(self) -> 'None':
        result, env = self._call(NotFound(_test_cid, 'Gone'))

        self.assertIn('404', env['zato.http.response.status'])

# ################################################################################################################################

    def test_method_not_allowed_sets_405_status(self) -> 'None':
        result, env = self._call(MethodNotAllowed(_test_cid, 'No PUT'))

        self.assertIn('405', env['zato.http.response.status'])

# ################################################################################################################################

    def test_forbidden_sets_403_status(self) -> 'None':
        result, env = self._call(Forbidden(_test_cid, 'Denied'))

        self.assertIn('403', env['zato.http.response.status'])

# ################################################################################################################################

    def test_too_many_requests_sets_429_status(self) -> 'None':
        result, env = self._call(TooManyRequests(_test_cid, 'Slow down'))

        self.assertIn('429', env['zato.http.response.status'])

# ################################################################################################################################

    def test_backend_invocation_error_sets_400_status(self) -> 'None':
        result, env = self._call(BackendInvocationError(_test_cid, 'Backend fail'))

        self.assertIn('400', env['zato.http.response.status'])

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.pretty_format_exception', return_value='formatted')
    def test_generic_exception_admin_channel_sets_x_zato_message(self, _mock:'MagicMock') -> 'None':
        channel_item = _make_channel_item({'name': MISC.DefaultAdminInvokeChannel})
        result, env = self._call(RuntimeError('Boom'), channel_item=channel_item)

        self.assertIn('X-Zato-Message', env['zato.http.response.headers'])
        self.assertIn('500', env['zato.http.response.status'])

# ################################################################################################################################

    def test_generic_exception_non_admin_return_tracebacks_true(self) -> 'None':
        ctx = _make_dispatcher()
        ctx.dispatcher.return_tracebacks = True
        channel_item = _make_channel_item({'transport': 'unknown', 'data_format': 'unknown'})
        wsgi_environ = _make_wsgi_environ()

        result = ctx.dispatcher._handle_dispatch_error(_test_cid, RuntimeError('details'), channel_item, wsgi_environ)

        self.assertEqual(result[0], 'details')

# ################################################################################################################################

    def test_generic_exception_non_admin_return_tracebacks_false(self) -> 'None':
        ctx = _make_dispatcher()
        ctx.dispatcher.return_tracebacks = False
        ctx.dispatcher.default_error_message = 'Oops'
        channel_item = _make_channel_item({'transport': 'unknown', 'data_format': 'unknown'})
        wsgi_environ = _make_wsgi_environ()

        result = ctx.dispatcher._handle_dispatch_error(_test_cid, RuntimeError('secret'), channel_item, wsgi_environ)

        self.assertEqual(result, 'Oops')

# ################################################################################################################################

    def test_json_data_format_sets_json_content_type(self) -> 'None':
        channel_item = _make_channel_item({'data_format': DATA_FORMAT.JSON})
        result, env = self._call(RuntimeError('err'), channel_item=channel_item)

        self.assertEqual(env['zato.http.response.headers']['Content-Type'], CONTENT_TYPE['JSON'])

# ################################################################################################################################

    def test_non_json_data_format_no_json_content_type(self) -> 'None':
        channel_item = _make_channel_item({'data_format': 'xml'})
        result, env = self._call(RuntimeError('err'), channel_item=channel_item)

        self.assertNotEqual(env['zato.http.response.headers'].get('Content-Type'), CONTENT_TYPE['JSON'])

# ################################################################################################################################

    def test_service_missing_exception_no_traceback_logged(self) -> 'None':
        with patch('zato.server.connection.http_soap.channel.logger') as mock_logger:
            mock_logger.isEnabledFor.return_value = False
            self._call(ServiceMissingException(_test_cid, 'Not deployed'))

            info_calls = [str(c) for c in mock_logger.info.call_args_list]
            traceback_logged = any('Caught an exception' in c for c in info_calls)
            self.assertFalse(traceback_logged)

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.logger')
    def test_non_service_missing_logs_traceback(self, mock_logger:'MagicMock') -> 'None':
        mock_logger.isEnabledFor.return_value = False
        self._call(RuntimeError('Crash'))

        info_calls = [str(c) for c in mock_logger.info.call_args_list]
        traceback_logged = any('Caught an exception' in c for c in info_calls)
        self.assertTrue(traceback_logged)

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.stack_format')
    @patch('zato.server.connection.http_soap.channel.logger')
    def test_stack_format_called_when_available(self, mock_logger:'MagicMock', mock_stack_format:'MagicMock') -> 'None':
        mock_logger.isEnabledFor.return_value = False
        mock_stack_format.return_value = 'formatted'
        self._call(RuntimeError('Err'))

        mock_stack_format.assert_called_once()

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.logger')
    def test_trace1_enabled_logs_no_wrapper_message(self, mock_logger:'MagicMock') -> 'None':
        mock_logger.isEnabledFor.return_value = True
        channel_item = _make_channel_item({'transport': 'unknown', 'data_format': 'unknown'})
        self._call(RuntimeError('err'), channel_item=channel_item)

        mock_logger.log.assert_called()

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.logger')
    def test_trace1_disabled_no_log(self, mock_logger:'MagicMock') -> 'None':
        mock_logger.isEnabledFor.return_value = False
        channel_item = _make_channel_item({'transport': 'unknown', 'data_format': 'unknown'})
        self._call(RuntimeError('err'), channel_item=channel_item)

        mock_logger.log.assert_not_called()

# ################################################################################################################################

    def test_error_wrapper_applied_for_json(self) -> 'None':
        channel_item = _make_channel_item({'data_format': DATA_FORMAT.JSON, 'transport': 'plain_http'})
        result, env = self._call(RuntimeError('err'), channel_item=channel_item)

        self.assertIsNotNone(result)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    unittest.main()
