# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
import struct
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

# Zato
from zato.common.rate_limiting.cidr import SlottedCheckResult
from zato.server.connection.http_soap.channel import RequestDispatcher

# ################################################################################################################################
# ################################################################################################################################

def _make_dispatcher():
    """ Builds a minimal RequestDispatcher with mocked dependencies.
    """
    server = MagicMock()
    url_data = MagicMock()
    request_handler = MagicMock()

    dispatcher = RequestDispatcher(
        server=server,
        url_data=url_data,
        request_handler=request_handler,
        return_tracebacks=False,
        default_error_message='Internal error',
        http_methods_allowed=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    )

    return dispatcher

# ################################################################################################################################

def _make_wsgi_environ():
    """ Returns a minimal WSGI environ dict for testing dispatch.
    """
    environ = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/test/path',
        'HTTP_ACCEPT': '*/*',
        'wsgi.url_scheme': 'http',
        'zato.http.response.headers': {},
        'zato.http.response.status': '200 OK',
    }

    return environ

# ################################################################################################################################

def _make_url_match_result(channel_id=1, channel_name='test.channel'):
    """ Returns a mock URL match result that simulates a successful match.
    """
    result = MagicMock()
    result.url_match = '/test/path'
    result.channel_item = {
        'id': channel_id,
        'name': channel_name,
        'service_name': 'test.service',
        'match_target': '/test/path',
        'is_active': True,
        'data_format': 'json',
        'content_encoding': '',
    }
    result.channel_name = channel_name
    result.payload = ''

    return result

# ################################################################################################################################

def _make_check_result(is_allowed, is_disallowed=False, retry_after_us=0):
    """ Builds a SlottedCheckResult with the given values.
    """
    out = SlottedCheckResult()
    out.is_allowed = is_allowed
    out.is_disallowed = is_disallowed
    out.retry_after_us = retry_after_us
    out.matched_key = '0.0.0.0/0:0'

    return out

# ################################################################################################################################
# ################################################################################################################################

class DispatchPassthroughTestCase(unittest.TestCase):
    """ Tests that requests pass through when rate limiting allows them.
    Both checks (sec_def and channel) now happen inside _authenticate_and_invoke.
    """

    @patch.object(RequestDispatcher, '_format_response', return_value='OK')
    @patch.object(RequestDispatcher, '_invoke_service')
    @patch.object(RequestDispatcher, '_check_security')
    @patch.object(RequestDispatcher, '_match_url')
    @patch.object(RequestDispatcher, '_extract_request_meta')
    def test_passthrough_when_no_rate_limiting(self, mock_extract_meta, mock_match_url,
            mock_check_security, mock_invoke, mock_format):
        """ When both managers return None (no rules), the service is invoked.
        """
        dispatcher = _make_dispatcher()

        meta = MagicMock()
        meta.http_method = 'GET'
        meta.path_info = '/test/path'
        mock_extract_meta.return_value = meta

        mock_match_url.return_value = _make_url_match_result()

        dispatcher.server.rate_limiting_manager.check_sec_def.return_value = None
        dispatcher.server.rate_limiting_manager.check.return_value = None

        wsgi_environ = _make_wsgi_environ()
        config_manager = MagicMock()

        result = dispatcher.dispatch('cid123', '2025-01-01', wsgi_environ, config_manager, 'test-agent', '10.0.0.1')

        self.assertEqual(result, 'OK')
        mock_invoke.assert_called_once()

    @patch.object(RequestDispatcher, '_format_response', return_value='OK')
    @patch.object(RequestDispatcher, '_invoke_service')
    @patch.object(RequestDispatcher, '_check_security')
    @patch.object(RequestDispatcher, '_match_url')
    @patch.object(RequestDispatcher, '_extract_request_meta')
    def test_passthrough_when_allowed(self, mock_extract_meta, mock_match_url,
            mock_check_security, mock_invoke, mock_format):
        """ When channel rate limiting returns is_allowed=True, the service is invoked.
        """
        dispatcher = _make_dispatcher()

        meta = MagicMock()
        meta.http_method = 'GET'
        meta.path_info = '/test/path'
        mock_extract_meta.return_value = meta

        mock_match_url.return_value = _make_url_match_result()

        dispatcher.server.rate_limiting_manager.check_sec_def.return_value = None
        dispatcher.server.rate_limiting_manager.check.return_value = _make_check_result(is_allowed=True)

        wsgi_environ = _make_wsgi_environ()
        config_manager = MagicMock()

        result = dispatcher.dispatch('cid123', '2025-01-01', wsgi_environ, config_manager, 'test-agent', '10.0.0.1')

        self.assertEqual(result, 'OK')
        mock_invoke.assert_called_once()

# ################################################################################################################################
# ################################################################################################################################

class DispatchDisallowedTestCase(unittest.TestCase):

    @patch.object(RequestDispatcher, '_check_security')
    @patch.object(RequestDispatcher, '_match_url')
    @patch.object(RequestDispatcher, '_extract_request_meta')
    def test_channel_disallowed_drops_socket(self, mock_extract_meta, mock_match_url, mock_check_security):
        """ When the channel rate limiting manager returns is_disallowed=True,
        the raw socket gets SO_LINGER set and closed, and empty bytes are returned.
        """
        dispatcher = _make_dispatcher()

        meta = MagicMock()
        meta.http_method = 'GET'
        meta.path_info = '/test/path'
        mock_extract_meta.return_value = meta

        mock_match_url.return_value = _make_url_match_result()

        dispatcher.server.rate_limiting_manager.check_sec_def.return_value = None
        dispatcher.server.rate_limiting_manager.check.return_value = _make_check_result(
            is_allowed=False, is_disallowed=True)

        mock_socket = MagicMock()
        wsgi_environ = _make_wsgi_environ()
        wsgi_environ['gunicorn.socket'] = mock_socket

        config_manager = MagicMock()

        result = dispatcher.dispatch('cid123', '2025-01-01', wsgi_environ, config_manager, 'test-agent', '10.0.0.1')

        self.assertEqual(result, b'')

        expected_linger = struct.pack('ii', 1, 0)
        mock_socket.setsockopt.assert_called_once_with(socket.SOL_SOCKET, socket.SO_LINGER, expected_linger)
        mock_socket.close.assert_called_once()

# ################################################################################################################################
# ################################################################################################################################

class DispatchRateLimitedTestCase(unittest.TestCase):

    @patch.object(RequestDispatcher, '_check_security')
    @patch.object(RequestDispatcher, '_match_url')
    @patch.object(RequestDispatcher, '_extract_request_meta')
    def test_channel_rate_limited_returns_429(self, mock_extract_meta, mock_match_url, mock_check_security):
        """ When the channel rate limiting manager returns is_allowed=False (not disallowed),
        the response status is 429 and a JSON error payload is returned.
        """
        dispatcher = _make_dispatcher()

        meta = MagicMock()
        meta.http_method = 'GET'
        meta.path_info = '/test/path'
        mock_extract_meta.return_value = meta

        mock_match_url.return_value = _make_url_match_result()

        dispatcher.server.rate_limiting_manager.check_sec_def.return_value = None
        dispatcher.server.rate_limiting_manager.check.return_value = _make_check_result(
            is_allowed=False, retry_after_us=2_500_000)

        wsgi_environ = _make_wsgi_environ()
        config_manager = MagicMock()

        result = dispatcher.dispatch('cid123', '2025-01-01', wsgi_environ, config_manager, 'test-agent', '10.0.0.1')

        self.assertEqual(wsgi_environ['zato.http.response.status'], '429 Too Many Requests')
        self.assertIn('Too many requests', result)

# ################################################################################################################################
# ################################################################################################################################

class DispatchRetryAfterTestCase(unittest.TestCase):

    @patch('zato.server.connection.http_soap.channel._datetime_utcnow')
    @patch.object(RequestDispatcher, '_check_security')
    @patch.object(RequestDispatcher, '_match_url')
    @patch.object(RequestDispatcher, '_extract_request_meta')
    def test_retry_after_header_rounds_up(self, mock_extract_meta, mock_match_url, mock_check_security, mock_utcnow):
        """ When retry_after_us has a remainder after dividing by 1_000_000,
        the Retry-After date is now + rounded-up seconds.
        """
        mock_utcnow.return_value = datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        dispatcher = _make_dispatcher()

        meta = MagicMock()
        meta.http_method = 'GET'
        meta.path_info = '/test/path'
        mock_extract_meta.return_value = meta

        mock_match_url.return_value = _make_url_match_result()

        dispatcher.server.rate_limiting_manager.check_sec_def.return_value = None
        dispatcher.server.rate_limiting_manager.check.return_value = _make_check_result(
            is_allowed=False, retry_after_us=2_500_000)

        wsgi_environ = _make_wsgi_environ()
        config_manager = MagicMock()

        dispatcher.dispatch('cid123', '2025-01-01', wsgi_environ, config_manager, 'test-agent', '10.0.0.1')

        self.assertEqual(wsgi_environ['zato.http.response.headers']['Retry-After'], 'Sun, 15 Jun 2025 12:00:03 GMT')

    @patch('zato.server.connection.http_soap.channel._datetime_utcnow')
    @patch.object(RequestDispatcher, '_check_security')
    @patch.object(RequestDispatcher, '_match_url')
    @patch.object(RequestDispatcher, '_extract_request_meta')
    def test_retry_after_header_exact_seconds(self, mock_extract_meta, mock_match_url, mock_check_security, mock_utcnow):
        """ When retry_after_us is an exact multiple of 1_000_000,
        the Retry-After date is now + exact seconds.
        """
        mock_utcnow.return_value = datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        dispatcher = _make_dispatcher()

        meta = MagicMock()
        meta.http_method = 'GET'
        meta.path_info = '/test/path'
        mock_extract_meta.return_value = meta

        mock_match_url.return_value = _make_url_match_result()

        dispatcher.server.rate_limiting_manager.check_sec_def.return_value = None
        dispatcher.server.rate_limiting_manager.check.return_value = _make_check_result(
            is_allowed=False, retry_after_us=5_000_000)

        wsgi_environ = _make_wsgi_environ()
        config_manager = MagicMock()

        dispatcher.dispatch('cid123', '2025-01-01', wsgi_environ, config_manager, 'test-agent', '10.0.0.1')

        self.assertEqual(wsgi_environ['zato.http.response.headers']['Retry-After'], 'Sun, 15 Jun 2025 12:00:05 GMT')

# ################################################################################################################################
# ################################################################################################################################

class DispatchLoggingTestCase(unittest.TestCase):

    @patch('zato.server.connection.http_soap.channel._datetime_utcnow')
    @patch('zato.server.connection.http_soap.channel.logger')
    @patch.object(RequestDispatcher, '_check_security')
    @patch.object(RequestDispatcher, '_match_url')
    @patch.object(RequestDispatcher, '_extract_request_meta')
    def test_rate_limited_logs_429(self, mock_extract_meta, mock_match_url, mock_check_security,
            mock_logger, mock_utcnow):
        """ When traffic is rate-limited, a log message with '429' is emitted.
        """
        mock_utcnow.return_value = datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        dispatcher = _make_dispatcher()

        meta = MagicMock()
        meta.http_method = 'GET'
        meta.path_info = '/test/path'
        mock_extract_meta.return_value = meta

        mock_match_url.return_value = _make_url_match_result()

        dispatcher.server.rate_limiting_manager.check_sec_def.return_value = None
        dispatcher.server.rate_limiting_manager.check.return_value = _make_check_result(
            is_allowed=False, retry_after_us=3_000_000)

        wsgi_environ = _make_wsgi_environ()
        config_manager = MagicMock()

        dispatcher.dispatch('cid123', '2025-01-01', wsgi_environ, config_manager, 'test-agent', '10.0.0.1')

        mock_logger.info.assert_any_call(
            'Rate limiting 429; cid:%s, channel:%s, remote_addr:%s, retry_after:%s',
            'cid123', 'test.channel', '10.0.0.1', 'Sun, 15 Jun 2025 12:00:03 GMT',
        )

# ################################################################################################################################
# ################################################################################################################################

class DispatchNoMatchTestCase(unittest.TestCase):

    @patch.object(RequestDispatcher, '_match_url')
    @patch.object(RequestDispatcher, '_extract_request_meta')
    def test_no_url_match_skips_rate_limiting(self, mock_extract_meta, mock_match_url):
        """ When the URL does not match any channel (404),
        the rate limiting manager must not be called at all.
        """
        dispatcher = _make_dispatcher()

        meta = MagicMock()
        meta.http_method = 'GET'
        meta.path_info = '/nonexistent'
        mock_extract_meta.return_value = meta

        # url_match is None when no URL matches (404)
        result = MagicMock()
        result.url_match = None
        result.channel_item = None
        result.channel_name = '(None)'
        result.payload = ''
        mock_match_url.return_value = result

        wsgi_environ = _make_wsgi_environ()
        config_manager = MagicMock()

        dispatcher.dispatch('cid123', '2025-01-01', wsgi_environ, config_manager, 'test-agent', '10.0.0.1')

        dispatcher.server.rate_limiting_manager.check.assert_not_called()

# ################################################################################################################################
# ################################################################################################################################

class DispatchSecDefBeforeChannelTestCase(unittest.TestCase):
    """ Verifies that sec_def rate limiting is checked before channel rate limiting.
    """

    @patch.object(RequestDispatcher, '_check_security')
    @patch.object(RequestDispatcher, '_match_url')
    @patch.object(RequestDispatcher, '_extract_request_meta')
    def test_sec_def_denied_skips_channel_check(self, mock_extract_meta, mock_match_url, mock_check_security):
        """ When the sec_def check returns disallowed, the channel check must not be called.
        """
        dispatcher = _make_dispatcher()

        meta = MagicMock()
        meta.http_method = 'GET'
        meta.path_info = '/test/path'
        mock_extract_meta.return_value = meta

        mock_match_url.return_value = _make_url_match_result()

        # Sec def disallows the request
        dispatcher.server.rate_limiting_manager.check_sec_def.return_value = _make_check_result(
            is_allowed=False, is_disallowed=True)

        mock_socket = MagicMock()
        wsgi_environ = _make_wsgi_environ()
        wsgi_environ['gunicorn.socket'] = mock_socket
        wsgi_environ['zato.sec_def'] = {'type': 'basic_auth', 'id': 99}

        config_manager = MagicMock()

        result = dispatcher.dispatch('cid123', '2025-01-01', wsgi_environ, config_manager, 'test-agent', '10.0.0.1')

        # The request was dropped by the sec_def check
        self.assertEqual(result, b'')

        # The channel check must not have been called
        dispatcher.server.rate_limiting_manager.check.assert_not_called()

    @patch('zato.server.connection.http_soap.channel._datetime_utcnow')
    @patch.object(RequestDispatcher, '_check_security')
    @patch.object(RequestDispatcher, '_match_url')
    @patch.object(RequestDispatcher, '_extract_request_meta')
    def test_sec_def_allowed_then_channel_denied(self, mock_extract_meta, mock_match_url,
            mock_check_security, mock_utcnow):
        """ When the sec_def check allows but the channel check denies, 429 is returned.
        """
        mock_utcnow.return_value = datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        dispatcher = _make_dispatcher()

        meta = MagicMock()
        meta.http_method = 'GET'
        meta.path_info = '/test/path'
        mock_extract_meta.return_value = meta

        mock_match_url.return_value = _make_url_match_result()

        # Sec def allows
        dispatcher.server.rate_limiting_manager.check_sec_def.return_value = _make_check_result(is_allowed=True)

        # Channel denies
        dispatcher.server.rate_limiting_manager.check.return_value = _make_check_result(
            is_allowed=False, retry_after_us=1_000_000)

        wsgi_environ = _make_wsgi_environ()
        wsgi_environ['zato.sec_def'] = {'type': 'basic_auth', 'id': 99}
        config_manager = MagicMock()

        result = dispatcher.dispatch('cid123', '2025-01-01', wsgi_environ, config_manager, 'test-agent', '10.0.0.1')

        self.assertEqual(wsgi_environ['zato.http.response.status'], '429 Too Many Requests')
        self.assertIn('Too many requests', result)

        # Both checks were called
        dispatcher.server.rate_limiting_manager.check_sec_def.assert_called_once()
        dispatcher.server.rate_limiting_manager.check.assert_called_once()

    @patch.object(RequestDispatcher, '_format_response', return_value='OK')
    @patch.object(RequestDispatcher, '_invoke_service')
    @patch.object(RequestDispatcher, '_check_security')
    @patch.object(RequestDispatcher, '_match_url')
    @patch.object(RequestDispatcher, '_extract_request_meta')
    def test_both_pass_invokes_service(self, mock_extract_meta, mock_match_url,
            mock_check_security, mock_invoke, mock_format):
        """ When both sec_def and channel checks pass, the service is invoked.
        """
        dispatcher = _make_dispatcher()

        meta = MagicMock()
        meta.http_method = 'GET'
        meta.path_info = '/test/path'
        mock_extract_meta.return_value = meta

        mock_match_url.return_value = _make_url_match_result()

        # Both allow
        dispatcher.server.rate_limiting_manager.check_sec_def.return_value = _make_check_result(is_allowed=True)
        dispatcher.server.rate_limiting_manager.check.return_value = _make_check_result(is_allowed=True)

        wsgi_environ = _make_wsgi_environ()
        wsgi_environ['zato.sec_def'] = {'type': 'basic_auth', 'id': 99}
        config_manager = MagicMock()

        result = dispatcher.dispatch('cid123', '2025-01-01', wsgi_environ, config_manager, 'test-agent', '10.0.0.1')

        self.assertEqual(result, 'OK')
        mock_invoke.assert_called_once()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    unittest.main()
