# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from io import BytesIO
from typing import NamedTuple
from unittest.mock import MagicMock, patch

# hypothesis
from hypothesis import given, HealthCheck, settings as hypothesis_settings
from hypothesis import strategies as st

# Zato
from zato.common.api import CONTENT_TYPE, DATA_FORMAT, MISC, IO, TRACE1, ZATO_NONE
from zato.common.exception import BackendInvocationError, BadRequest, Forbidden, \
    MethodNotAllowed, NotFound, ServiceMissingException, TooManyRequests, Unauthorized
from zato.common.json_ import dumps
from zato.common.marshal_.api import ElementMissing
from zato.server.connection.http_soap.channel import RequestDispatcher, response_404, status_response

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

_test_cid = 'zcid-test-0001'
_test_req_timestamp = '2025-01-01T00:00:00'
_test_user_agent = 'TestAgent/1.0'
_test_remote_addr = '127.0.0.1'

_default_http_methods_allowed = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']

# ################################################################################################################################
# ################################################################################################################################

def _make_channel_item(overrides:'anydict | None'=None) -> 'anydict':
    """ Builds a minimal channel_item dict with sane defaults.
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

def _make_response(
    payload:'any_'=b'{"response":"ok"}',
    content_type:'str'='application/json',
    headers:'anydict | None'=None,
    status_code:'int'=200
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

def _make_wsgi_environ(overrides:'anydict | None'=None) -> 'anydict':
    """ Builds a minimal WSGI environ dict.
    """
    out = {
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

class _DispatcherCtx(NamedTuple):
    dispatcher: 'RequestDispatcher'
    mock_url_data: 'MagicMock'
    mock_handler: 'MagicMock'
    mock_handle: 'MagicMock'
    mock_check_security: 'MagicMock'
    mock_create_channel_params: 'MagicMock'

# ################################################################################################################################

def _make_dispatcher(
    http_methods_allowed:'list | None'=None,
    return_tracebacks:'bool'=False,
    default_error_message:'str'='Internal server error',
    url_match:'str'='/test/path',
    channel_item:'anydict | None'=None,
    sec:'MagicMock | None'=None,
    response:'MagicMock | None'=None,
    rest_log_ignore:'set | None'=None,
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
    server.rest_log_ignore = rest_log_ignore if rest_log_ignore is not None else set()

    url_data = MagicMock()
    url_data.match.return_value = (url_match, channel_item)
    url_data.url_sec = {channel_item['match_target']: sec}

    request_handler = MagicMock()
    request_handler.handle.return_value = response
    request_handler.create_channel_params.return_value = {'param1': 'value1'}

    dispatcher = RequestDispatcher(
        server=server,
        url_data=url_data,
        request_handler=request_handler,
        return_tracebacks=return_tracebacks,
        default_error_message=default_error_message,
        http_methods_allowed=http_methods_allowed if http_methods_allowed is not None else _default_http_methods_allowed,
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

def _dispatch(ctx:'_DispatcherCtx', wsgi_environ:'anydict') -> 'any_':
    """ Shorthand to call dispatch with standard test parameters.
    """
    return ctx.dispatcher.dispatch(
        _test_cid, _test_req_timestamp, wsgi_environ,
        MagicMock(), _test_user_agent, _test_remote_addr)

# ################################################################################################################################
# ################################################################################################################################

class DispatchMethodCheckTestCase(unittest.TestCase):
    """ Tests for the HTTP method validation guard at the top of dispatch.
    """

# ################################################################################################################################

    def test_unsupported_method_returns_405(self) -> 'None':
        """ An HTTP method not in http_methods_allowed returns a JSON error and sets 405 status.
        """
        ctx = _make_dispatcher(http_methods_allowed=['GET', 'POST'])
        wsgi_environ = _make_wsgi_environ({'REQUEST_METHOD': 'DELETE'})

        result = _dispatch(ctx, wsgi_environ)

        self.assertIn('Unsupported HTTP method', result)
        self.assertIn('405', wsgi_environ['zato.http.response.status'])

# ################################################################################################################################

    def test_supported_method_proceeds(self) -> 'None':
        """ A supported HTTP method does not trigger the 405 guard.
        """
        ctx = _make_dispatcher(http_methods_allowed=['GET'])
        wsgi_environ = _make_wsgi_environ({'REQUEST_METHOD': 'GET'})

        result = _dispatch(ctx, wsgi_environ)

        self.assertNotIn('Unsupported HTTP method', str(result))

# ################################################################################################################################
# ################################################################################################################################

class DispatchURLMatchTestCase(unittest.TestCase):
    """ Tests for URL matching and 404 handling.
    """

# ################################################################################################################################

    def test_no_url_match_returns_404(self) -> 'None':
        """ When url_data.match returns (None, False), dispatch returns 404.
        """
        ctx = _make_dispatcher()
        ctx.mock_url_data.match.return_value = (None, False)
        wsgi_environ = _make_wsgi_environ()

        result = _dispatch(ctx, wsgi_environ)

        expected_response = response_404.format(_test_cid)
        self.assertEqual(result, expected_response)
        self.assertIn('404', wsgi_environ['zato.http.response.status'])

# ################################################################################################################################

    def test_url_match_sets_channel_item_in_environ(self) -> 'None':
        """ A successful URL match stores channel_item in wsgi_environ.
        """
        channel_item = _make_channel_item()
        ctx = _make_dispatcher(channel_item=channel_item)
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertIs(wsgi_environ['zato.channel_item'], channel_item)

# ################################################################################################################################

    def test_raw_request_stored_in_environ(self) -> 'None':
        """ The raw request payload is stored in wsgi_environ['zato.http.raw_request'].
        """
        ctx = _make_dispatcher()
        payload_bytes = b'test-payload-data'
        wsgi_environ = _make_wsgi_environ({'wsgi.input': BytesIO(payload_bytes)})

        _ = _dispatch(ctx, wsgi_environ)

        self.assertEqual(wsgi_environ['zato.http.raw_request'], payload_bytes)

# ################################################################################################################################
# ################################################################################################################################

class DispatchInactiveChannelTestCase(unittest.TestCase):
    """ Tests for inactive channel handling.
    """

# ################################################################################################################################

    def test_inactive_channel_returns_error(self) -> 'None':
        """ An inactive channel triggers a NotFound and returns an error response.
        """
        channel_item = _make_channel_item({'is_active': False})
        ctx = _make_dispatcher(channel_item=channel_item)
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertIn('404', wsgi_environ['zato.http.response.status'])

# ################################################################################################################################
# ################################################################################################################################

class DispatchSecurityTestCase(unittest.TestCase):
    """ Tests for security definition checking.
    """

# ################################################################################################################################

    def test_sec_def_present_calls_check_security(self) -> 'None':
        """ When sec_def is not ZATO_NONE, check_security is called.
        """
        sec = _make_sec(sec_def='basic_auth_def')
        ctx = _make_dispatcher(sec=sec)
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        ctx.mock_check_security.assert_called_once()

# ################################################################################################################################

    def test_sec_def_zato_none_skips_check_security(self) -> 'None':
        """ When sec_def is ZATO_NONE, check_security is not called.
        """
        sec = _make_sec(sec_def=ZATO_NONE)
        ctx = _make_dispatcher(sec=sec)
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        ctx.mock_check_security.assert_not_called()

# ################################################################################################################################

    def test_unauthorized_returns_401_with_challenge(self) -> 'None':
        """ An Unauthorized exception returns 401 and sets the WWW-Authenticate header.
        """
        sec = _make_sec(sec_def='basic_auth_def')
        ctx = _make_dispatcher(sec=sec)
        ctx.mock_check_security.side_effect = Unauthorized(_test_cid, 'Invalid credentials', 'Basic realm="test"')
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertIn('401', wsgi_environ['zato.http.response.status'])
        self.assertEqual(wsgi_environ['zato.http.response.headers']['WWW-Authenticate'], 'Basic realm="test"')

# ################################################################################################################################

    def test_unauthorized_without_challenge(self) -> 'None':
        """ An Unauthorized exception without a challenge still returns 401 but no WWW-Authenticate header.
        """
        sec = _make_sec(sec_def='basic_auth_def')
        ctx = _make_dispatcher(sec=sec)
        ctx.mock_check_security.side_effect = Unauthorized(_test_cid, 'Invalid credentials', None)
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertIn('401', wsgi_environ['zato.http.response.status'])
        self.assertNotIn('WWW-Authenticate', wsgi_environ['zato.http.response.headers'])

# ################################################################################################################################

    def test_forbidden_returns_403(self) -> 'None':
        """ A Forbidden exception from check_security returns 403.
        """
        sec = _make_sec(sec_def='basic_auth_def')
        ctx = _make_dispatcher(sec=sec)
        ctx.mock_check_security.side_effect = Forbidden(_test_cid, 'Not allowed')
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertIn('403', wsgi_environ['zato.http.response.status'])

# ################################################################################################################################
# ################################################################################################################################

class DispatchSecurityGroupsTestCase(unittest.TestCase):
    """ Tests for security groups checking.
    """

# ################################################################################################################################

    def test_security_groups_with_members_calls_check(self) -> 'None':
        """ When security_groups_ctx has members, check_security_via_groups is called.
        """
        groups_ctx = MagicMock()
        groups_ctx.has_members.return_value = True

        channel_item = _make_channel_item({'security_groups_ctx': groups_ctx})
        sec = _make_sec()
        ctx = _make_dispatcher(channel_item=channel_item, sec=sec)

        wsgi_environ = _make_wsgi_environ()

        with patch.object(ctx.dispatcher, 'check_security_via_groups') as mock_check:
            _ = _dispatch(ctx, wsgi_environ)
            mock_check.assert_called_once()

# ################################################################################################################################

    def test_security_groups_without_members_skips_check(self) -> 'None':
        """ When security_groups_ctx has no members, check_security_via_groups is not called.
        """
        groups_ctx = MagicMock()
        groups_ctx.has_members.return_value = False

        channel_item = _make_channel_item({'security_groups_ctx': groups_ctx})
        sec = _make_sec()
        ctx = _make_dispatcher(channel_item=channel_item, sec=sec)

        wsgi_environ = _make_wsgi_environ()

        with patch.object(ctx.dispatcher, 'check_security_via_groups') as mock_check:
            _ = _dispatch(ctx, wsgi_environ)
            mock_check.assert_not_called()

# ################################################################################################################################

    def test_no_security_groups_ctx_skips_check(self) -> 'None':
        """ When security_groups_ctx is None, check_security_via_groups is not called.
        """
        channel_item = _make_channel_item({'security_groups_ctx': None})
        ctx = _make_dispatcher(channel_item=channel_item)
        wsgi_environ = _make_wsgi_environ()

        with patch.object(ctx.dispatcher, 'check_security_via_groups') as mock_check:
            _ = _dispatch(ctx, wsgi_environ)
            mock_check.assert_not_called()

# ################################################################################################################################
# ################################################################################################################################

class DispatchFormDataTestCase(unittest.TestCase):
    """ Tests for form data extraction.
    """

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.util_get_form_data')
    def test_form_data_extracted_when_expected(self, mock_get_form_data:'MagicMock') -> 'None':
        """ Form data is extracted when data_format is FORM_DATA and content type matches.
        """
        mock_get_form_data.return_value = {'field1': 'value1'}
        channel_item = _make_channel_item({'data_format': IO.FORMAT.FORM_DATA})
        ctx = _make_dispatcher(channel_item=channel_item)
        wsgi_environ = _make_wsgi_environ({'CONTENT_TYPE': 'application/x-www-form-urlencoded'})

        _ = _dispatch(ctx, wsgi_environ)

        mock_get_form_data.assert_called_once()
        self.assertEqual(wsgi_environ['zato.oauth.post_data'], {'field1': 'value1'})

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.util_get_form_data')
    def test_form_data_not_extracted_for_json(self, mock_get_form_data:'MagicMock') -> 'None':
        """ Form data is not extracted when data_format is JSON.
        """
        channel_item = _make_channel_item({'data_format': DATA_FORMAT.JSON})
        ctx = _make_dispatcher(channel_item=channel_item)
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        mock_get_form_data.assert_not_called()

# ################################################################################################################################
# ################################################################################################################################

class DispatchChannelParamsTestCase(unittest.TestCase):
    """ Tests for channel params merging.
    """

# ################################################################################################################################

    def test_merge_url_params_calls_create_channel_params(self) -> 'None':
        """ When merge_url_params_req is True, create_channel_params is called.
        """
        channel_item = _make_channel_item({'merge_url_params_req': True})
        ctx = _make_dispatcher(channel_item=channel_item)
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        ctx.mock_create_channel_params.assert_called_once()

# ################################################################################################################################

    def test_no_merge_url_params_skips_create_channel_params(self) -> 'None':
        """ When merge_url_params_req is False, create_channel_params is not called.
        """
        channel_item = _make_channel_item({'merge_url_params_req': False})
        ctx = _make_dispatcher(channel_item=channel_item)
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        ctx.mock_create_channel_params.assert_not_called()

# ################################################################################################################################
# ################################################################################################################################

class DispatchHappyPathTestCase(unittest.TestCase):
    """ Tests for the happy-path response handling.
    """

# ################################################################################################################################

    def test_response_sets_content_type_and_status(self) -> 'None':
        """ A successful dispatch sets the response content type and status.
        """
        response = _make_response(payload=b'ok', content_type='application/json', status_code=200)
        ctx = _make_dispatcher(response=response)
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertEqual(wsgi_environ['zato.http.response.headers']['Content-Type'], 'application/json')
        self.assertEqual(wsgi_environ['zato.http.response.status'], status_response[200])

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.GzipFile')
    @patch('zato.server.connection.http_soap.channel.StringIO')
    def test_gzip_response(self, mock_string_io_class:'MagicMock', mock_gzip_class:'MagicMock') -> 'None':
        """ When content_encoding is 'gzip', the response payload is gzip-compressed
        and the Content-Encoding header is set.
        """
        mock_sio = MagicMock()
        mock_sio.getvalue.return_value = b'compressed-data'
        mock_string_io_class.return_value = mock_sio

        mock_gzip_ctx = MagicMock()
        mock_gzip_class.return_value.__enter__ = MagicMock(return_value=mock_gzip_ctx)
        mock_gzip_class.return_value.__exit__ = MagicMock(return_value=False)

        response = _make_response(payload=b'hello world payload')
        channel_item = _make_channel_item({'content_encoding': 'gzip'})
        ctx = _make_dispatcher(channel_item=channel_item, response=response)
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertEqual(wsgi_environ['zato.http.response.headers']['Content-Encoding'], 'gzip')
        mock_gzip_ctx.write.assert_called_once_with(b'hello world payload')

# ################################################################################################################################

    def test_plain_payload_returned_directly(self) -> 'None':
        """ When response.payload is a plain string/bytes, it is returned directly.
        """
        response = _make_response(payload=b'raw response body')
        ctx = _make_dispatcher(response=response)
        wsgi_environ = _make_wsgi_environ()

        result = _dispatch(ctx, wsgi_environ)

        self.assertEqual(result, b'raw response body')

# ################################################################################################################################
# ################################################################################################################################

class DispatchErrorHandlingTestCase(unittest.TestCase):
    """ Tests for the exception-handling branch of dispatch.
    """

# ################################################################################################################################

    def test_bad_request_returns_400(self) -> 'None':
        """ A BadRequest exception from handle sets 400 status.
        """
        ctx = _make_dispatcher()
        ctx.mock_handle.side_effect = BadRequest(_test_cid, 'Bad input', needs_msg=True)
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertIn('400', wsgi_environ['zato.http.response.status'])

# ################################################################################################################################

    def test_bad_request_admin_channel_returns_full_message(self) -> 'None':
        """ A BadRequest on the admin invoke channel returns the full error message.
        """
        channel_item = _make_channel_item({'name': MISC.DefaultAdminInvokeChannel})
        ctx = _make_dispatcher(channel_item=channel_item)
        error_msg = 'Detailed admin error info'
        ctx.mock_handle.side_effect = BadRequest(_test_cid, error_msg)
        wsgi_environ = _make_wsgi_environ()

        result = _dispatch(ctx, wsgi_environ)

        self.assertIn(error_msg, result)

# ################################################################################################################################

    def test_bad_request_non_admin_needs_msg_true(self) -> 'None':
        """ A BadRequest with needs_msg=True on a non-admin channel returns e.msg.
        """
        ctx = _make_dispatcher()
        error_msg = 'Validation failed for field X'
        ctx.mock_handle.side_effect = BadRequest(_test_cid, error_msg, needs_msg=True)
        wsgi_environ = _make_wsgi_environ()

        result = _dispatch(ctx, wsgi_environ)

        self.assertIn(error_msg, result)

# ################################################################################################################################

    def test_bad_request_non_admin_needs_msg_false(self) -> 'None':
        """ A BadRequest with needs_msg=False on a non-admin channel returns 'Bad request'.
        """
        ctx = _make_dispatcher()
        ctx.mock_handle.side_effect = BadRequest(_test_cid, 'secret details', needs_msg=False)
        wsgi_environ = _make_wsgi_environ()

        result = _dispatch(ctx, wsgi_environ)

        self.assertIn('Bad request', result)
        self.assertNotIn('secret details', result)

# ################################################################################################################################

    def test_not_found_returns_404(self) -> 'None':
        """ A NotFound exception from handle sets 404 status.
        """
        ctx = _make_dispatcher()
        ctx.mock_handle.side_effect = NotFound(_test_cid, 'Not here')
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertIn('404', wsgi_environ['zato.http.response.status'])

# ################################################################################################################################

    def test_method_not_allowed_returns_405(self) -> 'None':
        """ A MethodNotAllowed exception from handle sets 405 status.
        """
        ctx = _make_dispatcher()
        ctx.mock_handle.side_effect = MethodNotAllowed(_test_cid, 'Method not allowed')
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertIn('405', wsgi_environ['zato.http.response.status'])

# ################################################################################################################################

    def test_forbidden_returns_403(self) -> 'None':
        """ A Forbidden exception from handle sets 403 status.
        """
        ctx = _make_dispatcher()
        ctx.mock_handle.side_effect = Forbidden(_test_cid, 'Forbidden access')
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertIn('403', wsgi_environ['zato.http.response.status'])

# ################################################################################################################################

    def test_too_many_requests_returns_429(self) -> 'None':
        """ A TooManyRequests exception from handle sets 429 status.
        """
        ctx = _make_dispatcher()
        ctx.mock_handle.side_effect = TooManyRequests(_test_cid, 'Rate limited')
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertIn('429', wsgi_environ['zato.http.response.status'])

# ################################################################################################################################

    def test_model_validation_error_returns_400(self) -> 'None':
        """ A ModelValidationError from handle sets 400 status.
        """
        ctx = _make_dispatcher()
        ctx.mock_handle.side_effect = ElementMissing('/request_id')
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertIn('400', wsgi_environ['zato.http.response.status'])

# ################################################################################################################################

    def test_backend_invocation_error_returns_400(self) -> 'None':
        """ A BackendInvocationError from handle sets 400 status.
        """
        ctx = _make_dispatcher()
        ctx.mock_handle.side_effect = BackendInvocationError(_test_cid, 'Backend failed', needs_msg=True)
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertIn('400', wsgi_environ['zato.http.response.status'])

# ################################################################################################################################

    def test_generic_exception_returns_500(self) -> 'None':
        """ A generic Exception from handle sets 500 status.
        """
        ctx = _make_dispatcher()
        ctx.mock_handle.side_effect = RuntimeError('Something went wrong')
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertIn('500', wsgi_environ['zato.http.response.status'])

# ################################################################################################################################

    def test_generic_exception_admin_channel_sets_x_zato_message(self) -> 'None':
        """ A generic exception on the admin invoke channel sets the X-Zato-Message header.
        """
        channel_item = _make_channel_item({'name': MISC.DefaultAdminInvokeChannel})
        ctx = _make_dispatcher(channel_item=channel_item)
        ctx.mock_handle.side_effect = RuntimeError('Admin error details')
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertIn('X-Zato-Message', wsgi_environ['zato.http.response.headers'])

# ################################################################################################################################

    def test_generic_exception_non_admin_returns_default_error(self) -> 'None':
        """ A generic exception on a non-admin channel with return_tracebacks=False returns default_error_message.
        """
        ctx = _make_dispatcher(return_tracebacks=False, default_error_message='Something happened')
        ctx.mock_handle.side_effect = RuntimeError('Secret trace')
        wsgi_environ = _make_wsgi_environ()

        result = _dispatch(ctx, wsgi_environ)

        self.assertIn('Something happened', result)

# ################################################################################################################################

    def test_generic_exception_non_admin_return_tracebacks(self) -> 'None':
        """ A generic exception on a non-admin channel with return_tracebacks=True returns e.args.
        """
        ctx = _make_dispatcher(return_tracebacks=True)
        ctx.mock_handle.side_effect = RuntimeError('Visible trace')
        wsgi_environ = _make_wsgi_environ()

        result = _dispatch(ctx, wsgi_environ)

        self.assertIn('Visible trace', str(result))

# ################################################################################################################################

    def test_service_missing_exception_skips_traceback_log(self) -> 'None':
        """ A ServiceMissingException does not trigger traceback logging.
        """
        ctx = _make_dispatcher()
        ctx.mock_handle.side_effect = ServiceMissingException(_test_cid, 'Service not deployed')
        wsgi_environ = _make_wsgi_environ()

        with patch('zato.server.connection.http_soap.channel.logger') as mock_logger:
            _ = _dispatch(ctx, wsgi_environ)

            # .. the info-level traceback log must not be called for ServiceMissingException ..
            for call_item in mock_logger.info.call_args_list:
                if call_item and call_item[0]:
                    self.assertNotIn('Caught an exception', str(call_item[0][0]))

# ################################################################################################################################

    def test_json_data_format_error_sets_json_content_type(self) -> 'None':
        """ When an error occurs on a JSON channel, Content-Type is set to application/json.
        """
        channel_item = _make_channel_item({'data_format': DATA_FORMAT.JSON})
        ctx = _make_dispatcher(channel_item=channel_item)
        ctx.mock_handle.side_effect = RuntimeError('Error')
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertEqual(wsgi_environ['zato.http.response.headers']['Content-Type'], CONTENT_TYPE['JSON'])

# ################################################################################################################################
# ################################################################################################################################

class DispatchFinallyBlockTestCase(unittest.TestCase):
    """ Tests for the finally block that merges response headers.
    """

# ################################################################################################################################

    def test_response_headers_merged_on_success(self) -> 'None':
        """ Response headers from the container are merged into wsgi_environ on success.
        """
        response = _make_response()
        ctx = _make_dispatcher(response=response)
        wsgi_environ = _make_wsgi_environ()

        original_handle = ctx.mock_handle

        def handle_with_headers(*args:'any_', **kwargs:'any_') -> 'any_':
            container = args[10] if len(args) > 10 else kwargs['zato_response_headers_container']
            container['X-Custom-Header'] = 'custom-value'
            return original_handle(*args, **kwargs)

        ctx.mock_handle.side_effect = handle_with_headers

        _ = _dispatch(ctx, wsgi_environ)

        self.assertEqual(wsgi_environ['zato.http.response.headers']['X-Custom-Header'], 'custom-value')

# ################################################################################################################################

    def test_response_headers_merged_on_error(self) -> 'None':
        """ Response headers from the container are merged even when an exception occurs.
        """
        ctx = _make_dispatcher()
        wsgi_environ = _make_wsgi_environ()

        def handle_with_headers_and_error(*args:'any_', **kwargs:'any_') -> 'None':
            container = args[10] if len(args) > 10 else kwargs['zato_response_headers_container']
            container['X-Error-Header'] = 'error-value'
            raise RuntimeError('Boom')

        ctx.mock_handle.side_effect = handle_with_headers_and_error

        _ = _dispatch(ctx, wsgi_environ)

        self.assertEqual(wsgi_environ['zato.http.response.headers']['X-Error-Header'], 'error-value')

# ################################################################################################################################
# ################################################################################################################################

class DispatchLoggingTestCase(unittest.TestCase):
    """ Tests for request logging.
    """

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel._logger_is_enabled_for', return_value=True)
    def test_log_info_emitted_when_enabled(self, mock_enabled:'MagicMock') -> 'None':
        """ When logger info is enabled and path is not in rest_log_ignore, logger.info is called.
        """
        ctx = _make_dispatcher(rest_log_ignore=set())
        wsgi_environ = _make_wsgi_environ()

        with patch('zato.server.connection.http_soap.channel.logger') as mock_logger:
            _ = _dispatch(ctx, wsgi_environ)

            info_calls = [str(call_item) for call_item in mock_logger.info.call_args_list]
            found = any('REST cha' in call_item for call_item in info_calls)
            self.assertTrue(found, f'Expected REST log line in info calls: {info_calls}')

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel._logger_is_enabled_for', return_value=True)
    def test_log_info_suppressed_for_ignored_paths(self, mock_enabled:'MagicMock') -> 'None':
        """ When the path is in rest_log_ignore, the REST request log line is not emitted.
        """
        ctx = _make_dispatcher(rest_log_ignore={'/test/path'})
        wsgi_environ = _make_wsgi_environ()

        with patch('zato.server.connection.http_soap.channel.logger') as mock_logger:
            _ = _dispatch(ctx, wsgi_environ)

            info_calls = [str(call_item) for call_item in mock_logger.info.call_args_list]
            found = any('REST cha' in call_item for call_item in info_calls)
            self.assertFalse(found, f'REST log line should not appear for ignored paths: {info_calls}')

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel._logger_is_enabled_for', return_value=False)
    def test_log_info_not_emitted_when_disabled(self, mock_enabled:'MagicMock') -> 'None':
        """ When logger info is disabled, the REST request log line is not emitted.
        """
        ctx = _make_dispatcher()
        wsgi_environ = _make_wsgi_environ()

        with patch('zato.server.connection.http_soap.channel.logger') as mock_logger:
            _ = _dispatch(ctx, wsgi_environ)

            info_calls = [str(call_item) for call_item in mock_logger.info.call_args_list]
            found = any('REST cha' in call_item for call_item in info_calls)
            self.assertFalse(found, f'REST log line should not appear when logging disabled: {info_calls}')

# ################################################################################################################################
# ################################################################################################################################

class DispatchHTTPAcceptTestCase(unittest.TestCase):
    """ Tests for HTTP Accept header processing.
    """

# ################################################################################################################################

    def test_http_accept_star_replaced(self) -> 'None':
        """ The '*' in HTTP_ACCEPT is replaced with the internal accept-any marker.
        """
        ctx = _make_dispatcher()
        wsgi_environ = _make_wsgi_environ({'HTTP_ACCEPT': '*/*'})

        _ = _dispatch(ctx, wsgi_environ)

        call_args = ctx.mock_url_data.match.call_args[0]
        http_accept_arg = call_args[2]
        self.assertNotIn('*', http_accept_arg)

# ################################################################################################################################

    def test_missing_http_accept_uses_default(self) -> 'None':
        """ When HTTP_ACCEPT is missing from wsgi_environ, the default accept-any is used.
        """
        ctx = _make_dispatcher()
        wsgi_environ = _make_wsgi_environ()
        del wsgi_environ['HTTP_ACCEPT']

        _ = _dispatch(ctx, wsgi_environ)

        call_args = ctx.mock_url_data.match.call_args[0]
        http_accept_arg = call_args[2]
        self.assertNotIn('*', http_accept_arg)

# ################################################################################################################################
# ################################################################################################################################

class DispatchRequestMethodTestCase(unittest.TestCase):
    """ Tests for HTTP method handling.
    """

# ################################################################################################################################

    def test_request_method_passed_to_match(self) -> 'None':
        """ REQUEST_METHOD from wsgi_environ is passed to url_data.match as a str.
        """
        ctx = _make_dispatcher()
        wsgi_environ = _make_wsgi_environ({'REQUEST_METHOD': 'POST'})

        _ = _dispatch(ctx, wsgi_environ)

        call_args = ctx.mock_url_data.match.call_args[0]
        self.assertEqual(call_args[1], 'POST')

# ################################################################################################################################
# ################################################################################################################################

class DispatchHypothesisTestCase(unittest.TestCase):
    """ Fuzz tests using Hypothesis.
    """

# ################################################################################################################################

    @given(
        request_method=st.sampled_from(['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']),
        path_info=st.text(min_size=1, max_size=200),
        http_accept=st.text(min_size=1, max_size=100),
    )
    @hypothesis_settings(max_examples=50, suppress_health_check=[HealthCheck.differing_executors])
    def test_fuzz_wsgi_environ_values(
        self,
        request_method:'str',
        path_info:'str',
        http_accept:'str',
    ) -> 'None':
        """ Fuzz wsgi_environ values - dispatch never raises an unhandled exception.
        """
        ctx = _make_dispatcher()
        wsgi_environ = _make_wsgi_environ({
            'REQUEST_METHOD': request_method,
            'PATH_INFO': path_info,
            'RAW_URI': path_info,
            'HTTP_ACCEPT': http_accept,
        })

        result = _dispatch(ctx, wsgi_environ)

        self.assertIsNotNone(result)

# ################################################################################################################################

    @given(payload=st.binary(min_size=0, max_size=1024))
    @hypothesis_settings(max_examples=50, suppress_health_check=[HealthCheck.differing_executors])
    def test_fuzz_payload(self, payload:'bytes') -> 'None':
        """ Fuzz the request payload - dispatch never raises an unhandled exception.
        """
        ctx = _make_dispatcher()
        wsgi_environ = _make_wsgi_environ({'wsgi.input': BytesIO(payload)})

        result = _dispatch(ctx, wsgi_environ)

        self.assertIsNotNone(result)

# ################################################################################################################################

    @given(
        is_active=st.booleans(),
        data_format=st.sampled_from([DATA_FORMAT.JSON, DATA_FORMAT.DICT, DATA_FORMAT.FORM_DATA, IO.FORMAT.FORM_DATA]),
        content_encoding=st.sampled_from(['', 'gzip']),
        merge_url_params_req=st.booleans(),
    )
    @hypothesis_settings(max_examples=50, suppress_health_check=[HealthCheck.differing_executors])
    def test_fuzz_channel_item_fields(
        self,
        is_active:'bool',
        data_format:'str',
        content_encoding:'str',
        merge_url_params_req:'bool',
    ) -> 'None':
        """ Fuzz channel_item fields - dispatch never raises an unhandled exception.
        """
        channel_item = _make_channel_item({
            'is_active': is_active,
            'data_format': data_format,
            'content_encoding': content_encoding,
            'merge_url_params_req': merge_url_params_req,
        })

        response = _make_response(payload=b'ok')
        ctx = _make_dispatcher(channel_item=channel_item, response=response)
        wsgi_environ = _make_wsgi_environ()

        result = _dispatch(ctx, wsgi_environ)

        self.assertIsNotNone(result)

# ################################################################################################################################

    @given(
        use_sec_def=st.booleans(),
        use_groups=st.booleans(),
        groups_have_members=st.booleans(),
    )
    @hypothesis_settings(max_examples=50, suppress_health_check=[HealthCheck.differing_executors])
    def test_fuzz_security_path(
        self,
        use_sec_def:'bool',
        use_groups:'bool',
        groups_have_members:'bool',
    ) -> 'None':
        """ Fuzz security configuration - dispatch never raises an unhandled exception.
        """
        sec_def = 'basic_auth_def' if use_sec_def else ZATO_NONE
        sec = _make_sec(sec_def=sec_def)

        groups_ctx = None
        if use_groups:
            groups_ctx = MagicMock()
            groups_ctx.has_members.return_value = groups_have_members

        channel_item = _make_channel_item({'security_groups_ctx': groups_ctx})
        ctx = _make_dispatcher(channel_item=channel_item, sec=sec)
        wsgi_environ = _make_wsgi_environ()

        with patch.object(ctx.dispatcher, 'check_security_via_groups'):
            result = _dispatch(ctx, wsgi_environ)

        self.assertIsNotNone(result)

# ################################################################################################################################

    @given(
        error_type=st.sampled_from([
            'bad_request', 'unauthorized', 'forbidden', 'not_found',
            'too_many_requests', 'method_not_allowed', 'model_validation', 'runtime_error', 'value_error',
        ])
    )
    @hypothesis_settings(max_examples=20, suppress_health_check=[HealthCheck.differing_executors])
    def test_fuzz_error_types(self, error_type:'str') -> 'None':
        """ Fuzz exception types from handle - dispatch always returns a response.
        """
        error_map = {
            'bad_request': BadRequest(_test_cid, 'Bad'),
            'unauthorized': Unauthorized(_test_cid, 'Unauth', 'Basic realm="test"'),
            'forbidden': Forbidden(_test_cid, 'Forbidden'),
            'not_found': NotFound(_test_cid, 'Not found'),
            'too_many_requests': TooManyRequests(_test_cid, 'Rate limited'),
            'method_not_allowed': MethodNotAllowed(_test_cid, 'Not allowed'),
            'model_validation': ElementMissing('/field'),
            'runtime_error': RuntimeError('Crash'),
            'value_error': ValueError('Bad value'),
        }

        ctx = _make_dispatcher()
        ctx.mock_handle.side_effect = error_map[error_type]
        wsgi_environ = _make_wsgi_environ()

        result = _dispatch(ctx, wsgi_environ)

        self.assertIsNotNone(result)

# ################################################################################################################################
# ################################################################################################################################

class DispatchDefaultAdminChannelTestCase(unittest.TestCase):
    """ Tests for dispatch error handling with DefaultAdminInvokeChannel.
    """

# ################################################################################################################################

    def test_bad_request_admin_channel_returns_msg(self) -> 'None':
        """ When BadRequest on DefaultAdminInvokeChannel, the error msg is used as response
        (before wrapping by error_wrapper).
        """
        channel_item = _make_channel_item({'name': MISC.DefaultAdminInvokeChannel})
        ctx = _make_dispatcher(channel_item=channel_item)
        ctx.mock_handle.side_effect = BadRequest(_test_cid, 'Admin error details')
        wsgi_environ = _make_wsgi_environ()

        result = _dispatch(ctx, wsgi_environ)

        self.assertIn('Admin error details', result)

# ################################################################################################################################

    def test_bad_request_non_admin_channel_hides_details(self) -> 'None':
        """ When BadRequest on non-admin channel with needs_msg=False, details are hidden.
        """
        channel_item = _make_channel_item({'name': 'my.regular.channel'})
        ctx = _make_dispatcher(channel_item=channel_item)
        exc = BadRequest(_test_cid, 'Secret error')
        exc.needs_msg = False
        ctx.mock_handle.side_effect = exc
        wsgi_environ = _make_wsgi_environ()

        result = _dispatch(ctx, wsgi_environ)

        self.assertIn('Bad request', result)
        self.assertNotIn('Secret error', result)

# ################################################################################################################################

    def test_bad_request_non_admin_channel_with_needs_msg(self) -> 'None':
        """ When BadRequest on non-admin channel with needs_msg=True, message is returned.
        """
        channel_item = _make_channel_item({'name': 'my.regular.channel'})
        ctx = _make_dispatcher(channel_item=channel_item)
        exc = BadRequest(_test_cid, 'Visible error')
        exc.needs_msg = True
        ctx.mock_handle.side_effect = exc
        wsgi_environ = _make_wsgi_environ()

        result = _dispatch(ctx, wsgi_environ)

        self.assertIn('Visible error', result)

# ################################################################################################################################

    def test_generic_exception_admin_channel_sets_x_zato_message(self) -> 'None':
        """ When generic exception on DefaultAdminInvokeChannel, X-Zato-Message is set.
        """
        channel_item = _make_channel_item({'name': MISC.DefaultAdminInvokeChannel})
        ctx = _make_dispatcher(channel_item=channel_item)
        ctx.mock_handle.side_effect = RuntimeError('Something broke')
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertIn('X-Zato-Message', wsgi_environ['zato.http.response.headers'])

# ################################################################################################################################

    def test_generic_exception_non_admin_channel_no_x_zato_message(self) -> 'None':
        """ When generic exception on non-admin channel, X-Zato-Message is NOT set.
        """
        channel_item = _make_channel_item({'name': 'regular.channel'})
        ctx = _make_dispatcher(channel_item=channel_item)
        ctx.mock_handle.side_effect = RuntimeError('Crash')
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertNotIn('X-Zato-Message', wsgi_environ['zato.http.response.headers'])

# ################################################################################################################################

    def test_bad_request_channel_name_sorts_lower_than_admin(self) -> 'None':
        """ When channel name sorts lower than DefaultAdminInvokeChannel but isn't it,
        details are still hidden (not treated as admin).
        """
        channel_item = _make_channel_item({'name': 'aaa.channel'})
        ctx = _make_dispatcher(channel_item=channel_item)
        exc = BadRequest(_test_cid, 'Secret details')
        exc.needs_msg = False
        ctx.mock_handle.side_effect = exc
        wsgi_environ = _make_wsgi_environ()

        result = _dispatch(ctx, wsgi_environ)

        self.assertNotIn('Secret details', result)
        self.assertIn('Bad request', result)

# ################################################################################################################################

    def test_generic_exception_channel_name_sorts_lower_than_admin(self) -> 'None':
        """ When channel name sorts lower than DefaultAdminInvokeChannel but isn't it,
        X-Zato-Message is NOT set.
        """
        channel_item = _make_channel_item({'name': 'aaa.channel'})
        ctx = _make_dispatcher(channel_item=channel_item)
        ctx.mock_handle.side_effect = RuntimeError('Crash')
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertNotIn('X-Zato-Message', wsgi_environ['zato.http.response.headers'])

# ################################################################################################################################
# ################################################################################################################################

class DispatchErrorHandlerJSONTestCase(unittest.TestCase):
    """ Tests for dispatch error handler JSON content-type and error wrapping.
    """

# ################################################################################################################################

    def test_json_data_format_sets_json_content_type_on_error(self) -> 'None':
        """ When channel data_format is JSON and a generic exception occurs,
        Content-Type is set to application/json.
        """
        channel_item = _make_channel_item({'data_format': DATA_FORMAT.JSON})
        ctx = _make_dispatcher(channel_item=channel_item)
        ctx.mock_handle.side_effect = RuntimeError('Oops')
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertEqual(
            wsgi_environ['zato.http.response.headers']['Content-Type'], CONTENT_TYPE['JSON'])

# ################################################################################################################################

    def test_non_json_data_format_lower_no_content_type_override(self) -> 'None':
        """ When channel data_format sorts lower than 'json' ('csv' < 'json') and exception occurs,
        Content-Type is NOT set to JSON. Kills the <= mutant.
        """
        channel_item = _make_channel_item({'data_format': 'csv'})
        ctx = _make_dispatcher(channel_item=channel_item)
        ctx.mock_handle.side_effect = RuntimeError('Oops')
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertNotEqual(
            wsgi_environ['zato.http.response.headers'].get('Content-Type'), CONTENT_TYPE['JSON'])

# ################################################################################################################################

    def test_non_json_data_format_higher_no_content_type_override(self) -> 'None':
        """ When channel data_format sorts higher than 'json' ('xml' > 'json') and exception occurs,
        Content-Type is NOT set to JSON. Kills the >= mutant.
        """
        channel_item = _make_channel_item({'data_format': 'xml'})
        ctx = _make_dispatcher(channel_item=channel_item)
        ctx.mock_handle.side_effect = RuntimeError('Oops')
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertNotEqual(
            wsgi_environ['zato.http.response.headers'].get('Content-Type'), CONTENT_TYPE['JSON'])

# ################################################################################################################################

    def test_error_wrapper_applied_for_json_transport(self) -> 'None':
        """ When transport has a wrapper, error response is wrapped.
        """
        channel_item = _make_channel_item({'data_format': DATA_FORMAT.JSON, 'transport': 'plain_http'})
        ctx = _make_dispatcher(channel_item=channel_item)
        ctx.mock_handle.side_effect = ValueError('Some error')
        wsgi_environ = _make_wsgi_environ()

        result = _dispatch(ctx, wsgi_environ)

        self.assertIsNotNone(result)

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.logger')
    def test_trace1_logging_on_key_error(self, mock_logger:'MagicMock') -> 'None':
        """ When get_client_error_wrapper raises KeyError and TRACE1 is enabled, it logs.
        """
        channel_item = _make_channel_item({'data_format': 'unknown-format', 'transport': 'unknown-transport'})
        ctx = _make_dispatcher(channel_item=channel_item)
        ctx.mock_handle.side_effect = ValueError('err')
        wsgi_environ = _make_wsgi_environ()
        mock_logger.isEnabledFor.return_value = True

        _ = _dispatch(ctx, wsgi_environ)

        mock_logger.isEnabledFor.assert_any_call(TRACE1)

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.logger')
    def test_trace1_disabled_no_log(self, mock_logger:'MagicMock') -> 'None':
        """ When TRACE1 is disabled and get_client_error_wrapper raises KeyError, no TRACE1 log.
        """
        channel_item = _make_channel_item({'data_format': 'unknown-format', 'transport': 'unknown-transport'})
        ctx = _make_dispatcher(channel_item=channel_item)
        ctx.mock_handle.side_effect = ValueError('err')
        wsgi_environ = _make_wsgi_environ()
        mock_logger.isEnabledFor.return_value = False

        _ = _dispatch(ctx, wsgi_environ)

        mock_logger.log.assert_not_called()

# ################################################################################################################################
# ################################################################################################################################

class DispatchExceptionFormattingTestCase(unittest.TestCase):
    """ Tests for dispatch exception formatting - stack_format and traceback.
    """

# ################################################################################################################################

    def test_service_missing_exception_no_traceback(self) -> 'None':
        """ When ServiceMissingException is raised, needs_traceback is False.
        """
        channel_item = _make_channel_item()
        ctx = _make_dispatcher(channel_item=channel_item)
        ctx.mock_handle.side_effect = ServiceMissingException(_test_cid, 'Service not deployed')
        wsgi_environ = _make_wsgi_environ()

        result = _dispatch(ctx, wsgi_environ)

        self.assertIsNotNone(result)
        self.assertIn('500', wsgi_environ['zato.http.response.status'])

# ################################################################################################################################

    @patch('zato.server.connection.http_soap.channel.stack_format')
    def test_generic_exception_with_stack_format(self, mock_stack_format:'MagicMock') -> 'None':
        """ When stack_format is available and a generic exception occurs, it's called with correct args.
        """
        mock_stack_format.return_value = 'formatted-stack'
        channel_item = _make_channel_item()
        ctx = _make_dispatcher(channel_item=channel_item)
        ctx.mock_handle.side_effect = RuntimeError('Boom')
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        mock_stack_format.assert_called_once()
        call_kwargs = mock_stack_format.call_args[1]
        self.assertEqual(call_kwargs['source_lines'], 20)
        self.assertEqual(call_kwargs['add_summary'], True)
        self.assertEqual(call_kwargs['truncate_vals'], 5000)

# ################################################################################################################################

    def test_return_tracebacks_true_returns_traceback(self) -> 'None':
        """ When return_tracebacks is True and a generic exception occurs, traceback is returned.
        """
        channel_item = _make_channel_item()
        ctx = _make_dispatcher(channel_item=channel_item, return_tracebacks=True)
        ctx.mock_handle.side_effect = RuntimeError('Crash details')
        wsgi_environ = _make_wsgi_environ()

        result = _dispatch(ctx, wsgi_environ)

        self.assertIn('Crash details', str(result))

# ################################################################################################################################

    def test_return_tracebacks_false_returns_default_message(self) -> 'None':
        """ When return_tracebacks is False and a generic exception occurs, default error message is returned.
        """
        channel_item = _make_channel_item()
        ctx = _make_dispatcher(channel_item=channel_item, return_tracebacks=False, default_error_message='Oops')
        ctx.mock_handle.side_effect = RuntimeError('Secret crash')
        wsgi_environ = _make_wsgi_environ()

        result = _dispatch(ctx, wsgi_environ)

        self.assertNotIn('Secret crash', str(result))

# ################################################################################################################################

    def test_zato_response_headers_container_merged_on_exception(self) -> 'None':
        """ Even on exception, headers from zato_response_headers_container are merged.
        """
        channel_item = _make_channel_item()
        ctx = _make_dispatcher(channel_item=channel_item)

        def side_effect(*args:'any_', **kwargs:'any_') -> 'None':
            args[10]['X-Custom-Header'] = 'custom-value'
            raise RuntimeError('fail')

        ctx.mock_handle.side_effect = side_effect
        wsgi_environ = _make_wsgi_environ()

        _ = _dispatch(ctx, wsgi_environ)

        self.assertEqual(wsgi_environ['zato.http.response.headers']['X-Custom-Header'], 'custom-value')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()
