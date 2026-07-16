# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from unittest.mock import MagicMock, patch

# Zato
from zato.common.rate_limiting.cidr import SlottedCheckResult
from zato.common.rate_limiting.manager import RateLimitingManager
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
        'zato.sec_def': {'type': 'apikey', 'id': 20},
    }

    return environ

# ################################################################################################################################

def _make_url_match_result():
    """ Returns a mock URL match result that simulates a successful match.
    """
    result = MagicMock()
    result.url_match = '/test/path'
    result.channel_item = {
        'id': 1,
        'name': 'test.channel',
        'service_name': 'test.service',
        'match_target': '/test/path',
        'is_active': True,
        'is_internal': True,
        'data_format': 'json',
        'transport': 'plain_http',
    }
    result.channel_name = 'test.channel'
    result.payload = ''

    return result

# ################################################################################################################################

def _make_check_result(is_allowed, limit=100, remaining=42, retry_after_us=0):
    """ Builds a SlottedCheckResult with the given values.
    """
    out = SlottedCheckResult()
    out.is_allowed = is_allowed
    out.is_disallowed = False
    out.retry_after_us = retry_after_us
    out.matched_key = '0.0.0.0/0:0'
    out.limit = limit
    out.remaining = remaining

    return out

# ################################################################################################################################

def _dispatch(dispatcher, wsgi_environ):
    out = dispatcher.dispatch('cid123', '2026-01-01', wsgi_environ, MagicMock(), 'test-agent', '10.0.0.1')
    return out

# ################################################################################################################################
# ################################################################################################################################

class QuotaHeadersAllowedTestCase(unittest.TestCase):

    @patch.object(RequestDispatcher, '_format_response', return_value='OK')
    @patch.object(RequestDispatcher, '_invoke_service')
    @patch.object(RequestDispatcher, '_check_security')
    @patch.object(RequestDispatcher, '_match_url')
    @patch.object(RequestDispatcher, '_extract_request_meta')
    def test_headers_present_on_allowed_response(self, mock_extract_meta, mock_match_url,
            mock_check_security, mock_invoke, mock_format):
        """ An allowed request governed by a sec-def limit carries both X-RateLimit headers.
        """
        dispatcher = _make_dispatcher()

        meta = MagicMock()
        meta.http_method = 'GET'
        meta.path_info = '/test/path'
        mock_extract_meta.return_value = meta

        mock_match_url.return_value = _make_url_match_result()

        dispatcher.server.rate_limiting_manager.check_sec_def.return_value = _make_check_result(
            is_allowed=True, limit=100, remaining=42)
        dispatcher.server.rate_limiting_manager.check.return_value = None

        wsgi_environ = _make_wsgi_environ()
        result = _dispatch(dispatcher, wsgi_environ)

        self.assertEqual(result, 'OK')
        self.assertEqual(wsgi_environ['zato.http.response.headers']['X-RateLimit-Limit'], '100')
        self.assertEqual(wsgi_environ['zato.http.response.headers']['X-RateLimit-Remaining'], '42')

    @patch.object(RequestDispatcher, '_format_response', return_value='OK')
    @patch.object(RequestDispatcher, '_invoke_service')
    @patch.object(RequestDispatcher, '_check_security')
    @patch.object(RequestDispatcher, '_match_url')
    @patch.object(RequestDispatcher, '_extract_request_meta')
    def test_no_headers_without_sec_def_limits(self, mock_extract_meta, mock_match_url,
            mock_check_security, mock_invoke, mock_format):
        """ Without sec-def limits there are no X-RateLimit headers.
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
        _ = _dispatch(dispatcher, wsgi_environ)

        self.assertNotIn('X-RateLimit-Limit', wsgi_environ['zato.http.response.headers'])
        self.assertNotIn('X-RateLimit-Remaining', wsgi_environ['zato.http.response.headers'])

# ################################################################################################################################
# ################################################################################################################################

class QuotaHeadersRateLimitedTestCase(unittest.TestCase):

    @patch.object(RequestDispatcher, '_check_security')
    @patch.object(RequestDispatcher, '_match_url')
    @patch.object(RequestDispatcher, '_extract_request_meta')
    def test_headers_present_on_429(self, mock_extract_meta, mock_match_url, mock_check_security):
        """ A 429 from a sec-def limit carries the X-RateLimit headers next to Retry-After.
        """
        dispatcher = _make_dispatcher()

        meta = MagicMock()
        meta.http_method = 'GET'
        meta.path_info = '/test/path'
        mock_extract_meta.return_value = meta

        mock_match_url.return_value = _make_url_match_result()

        dispatcher.server.rate_limiting_manager.check_sec_def.return_value = _make_check_result(
            is_allowed=False, limit=100, remaining=0, retry_after_us=2_000_000)

        wsgi_environ = _make_wsgi_environ()
        result = _dispatch(dispatcher, wsgi_environ)

        self.assertIn('Too many requests', result)
        self.assertEqual(wsgi_environ['zato.http.response.status'], '429 Too Many Requests')
        self.assertIn('Retry-After', wsgi_environ['zato.http.response.headers'])
        self.assertEqual(wsgi_environ['zato.http.response.headers']['X-RateLimit-Limit'], '100')
        self.assertEqual(wsgi_environ['zato.http.response.headers']['X-RateLimit-Remaining'], '0')

    @patch.object(RequestDispatcher, '_check_security')
    @patch.object(RequestDispatcher, '_match_url')
    @patch.object(RequestDispatcher, '_extract_request_meta')
    def test_channel_429_stays_silent(self, mock_extract_meta, mock_match_url, mock_check_security):
        """ A 429 from a channel-level limit carries Retry-After but no X-RateLimit headers.
        """
        dispatcher = _make_dispatcher()

        meta = MagicMock()
        meta.http_method = 'GET'
        meta.path_info = '/test/path'
        mock_extract_meta.return_value = meta

        mock_match_url.return_value = _make_url_match_result()

        dispatcher.server.rate_limiting_manager.check_sec_def.return_value = None
        dispatcher.server.rate_limiting_manager.check.return_value = _make_check_result(
            is_allowed=False, retry_after_us=2_000_000)

        wsgi_environ = _make_wsgi_environ()
        result = _dispatch(dispatcher, wsgi_environ)

        self.assertIn('Too many requests', result)
        self.assertIn('Retry-After', wsgi_environ['zato.http.response.headers'])
        self.assertNotIn('X-RateLimit-Limit', wsgi_environ['zato.http.response.headers'])
        self.assertNotIn('X-RateLimit-Remaining', wsgi_environ['zato.http.response.headers'])

# ################################################################################################################################
# ################################################################################################################################

class QuotaHeadersDecreasingTestCase(unittest.TestCase):

    def test_remaining_decreases_across_calls(self):
        """ The remaining count reported by the engine decreases with each call.
        """
        manager = RateLimitingManager()
        manager.set_sec_def_config(20, [{
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [{
                'is_all_day': True,
                'disabled': False,
                'disallowed': False,
                'rate': 1000,
                'burst': 1000,
                'limit': 5,
                'limit_unit': 'minute',
            }],
        }])

        first = manager.check_sec_def(20, '10.0.0.1', 1_000_000, 'apikey20:')
        second = manager.check_sec_def(20, '10.0.0.1', 1_000_001, 'apikey20:')

        self.assertTrue(first.is_allowed)
        self.assertTrue(second.is_allowed)
        self.assertEqual(first.limit, 5)
        self.assertEqual(second.limit, 5)
        self.assertLess(second.remaining, first.remaining)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
