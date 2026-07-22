# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple
from unittest import main, TestCase
from unittest.mock import patch

# Bunch
from zato.common.ext.bunch import Bunch

# requests
from requests.exceptions import ConnectionError as RequestsConnectionError, Timeout as RequestsTimeout

# Zato
from zato.common.api import HTTP_SOAP, URL_TYPE
from zato.common.exception import BackendInvocationError
from zato.common.typing_ import cast_
from zato.server.connection.http_soap.outgoing import _resolve_retry_value, BaseHTTPSOAPWrapper
from zato.server.service import RESTAdapter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry

class ModuleCtx:
    CID = 'abc-123'
    Conn_Name = 'CRM and Billing'
    Address = 'https://example.com/api'
    Method = 'GET'

# The target of the sleep patch - invoke_http sleeps between retries through this name
_sleep_target = 'zato.server.connection.http_soap.outgoing.sleep'

# ################################################################################################################################
# ################################################################################################################################

class _FakeResponse:
    """ Stands in for a requests response - carries only what invoke_http reads.
    """
    def __init__(self, status_code:'int') -> 'None':
        self.status_code = status_code
        self.elapsed = 0
        self.text = 'Test response'

# ################################################################################################################################
# ################################################################################################################################

class _FakeSession:
    """ Stands in for a requests session - each call to .request consumes the next predefined
    result, raising it if it is an exception and returning it otherwise.
    """
    def __init__(self, results:'anylist') -> 'None':
        self.results = list(results)
        self.calls = []

# ################################################################################################################################

    def request(self, method:'str', address:'str', **kwargs:'any_') -> 'any_':
        self.calls.append((method, address, kwargs))
        result = self.results.pop(0)

        if isinstance(result, Exception):
            raise result

        return result

# ################################################################################################################################
# ################################################################################################################################

class _WrapperCtx(NamedTuple):
    wrapper: 'BaseHTTPSOAPWrapper'
    session: '_FakeSession'

# ################################################################################################################################
# ################################################################################################################################

def _get_wrapper(config_extra:'stranydict | None', results:'anylist') -> '_WrapperCtx':
    """ Builds a wrapper around a minimal connection config, with a fake session
    that will produce the given results, one per call.
    """
    config = {
        'name': ModuleCtx.Conn_Name,
        'is_internal': True,
        'timeout': 1,
        'password': '',
        'sec_type': None,
        'security_name': None,
        'content_type': '',
        'data_format': 'json',
        'transport': URL_TYPE.PLAIN_HTTP,
        'address_host': 'https://example.com',
        'address_url_path': '/api',
    }

    if config_extra:
        config.update(config_extra)

    wrapper = BaseHTTPSOAPWrapper(config)
    session = _FakeSession(results)
    wrapper.session = cast_('any_', session)

    out = _WrapperCtx(wrapper, session)
    return out

# ################################################################################################################################
# ################################################################################################################################

class RetryValueResolutionTestCase(TestCase):
    """ Tests the precedence of retry values - explicit call arguments win over the connection's
    own config, which wins over the shared defaults.
    """

    def test_kwarg_wins_over_config(self) -> 'None':
        kwargs = {'max_retries': 7}
        config = {'max_retries': 3}

        value = _resolve_retry_value(kwargs, config, _retry.Field_Max_Retries, _retry.Default_Max_Retries)

        self.assertEqual(value, 7)

        # The resolution also removes the argument so it does not propagate to the requests library
        self.assertNotIn('max_retries', kwargs)

# ################################################################################################################################

    def test_config_wins_over_default(self) -> 'None':
        kwargs = {}
        config = {'max_retries': 3}

        value = _resolve_retry_value(kwargs, config, _retry.Field_Max_Retries, _retry.Default_Max_Retries)

        self.assertEqual(value, 3)

# ################################################################################################################################

    def test_default_when_no_kwarg_and_no_config(self) -> 'None':
        kwargs = {}
        config = {}

        value = _resolve_retry_value(kwargs, config, _retry.Field_Max_Retries, _retry.Default_Max_Retries)

        self.assertEqual(value, _retry.Default_Max_Retries)

# ################################################################################################################################

    def test_explicit_zero_kwarg_is_respected(self) -> 'None':
        kwargs = {'max_retries': 0}
        config = {'max_retries': 5}

        value = _resolve_retry_value(kwargs, config, _retry.Field_Max_Retries, _retry.Default_Max_Retries)

        self.assertEqual(value, 0)

# ################################################################################################################################
# ################################################################################################################################

class RetryLoopTestCase(TestCase):
    """ Tests the retry loop in invoke_http - how many requests go out and how long each sleep is.
    """

    def _invoke(self, wrapper:'BaseHTTPSOAPWrapper', **kwargs:'any_') -> 'any_':
        out = wrapper.invoke_http(ModuleCtx.CID, ModuleCtx.Method, ModuleCtx.Address, '', {}, None, **kwargs)
        return out

# ################################################################################################################################

    def test_defaults_mean_no_retries(self) -> 'None':

        # With no config and no arguments there is exactly one request and no sleeping at all
        connection_error = RequestsConnectionError('Connection refused')
        ctx = _get_wrapper(None, [connection_error])

        with patch(_sleep_target) as mock_sleep:
            with self.assertRaises(BackendInvocationError):
                _ = self._invoke(ctx.wrapper)

        self.assertEqual(len(ctx.session.calls), 1)
        mock_sleep.assert_not_called()

# ################################################################################################################################

    def test_config_driven_retries(self) -> 'None':

        # Three retries from the connection's config - four requests in total,
        # with each sleep twice as long as the previous one.
        config_extra = {
            'max_retries': 3,
            'retry_sleep_time': 1,
            'retry_backoff_threshold': 60,
            'retry_backoff_multiplier': 2,
        }

        results = []
        for _ in range(4):
            results.append(RequestsConnectionError('Connection refused'))

        ctx = _get_wrapper(config_extra, results)

        with patch(_sleep_target) as mock_sleep:
            with self.assertRaises(BackendInvocationError):
                _ = self._invoke(ctx.wrapper)

        self.assertEqual(len(ctx.session.calls), 4)

        sleep_times = []
        for call in mock_sleep.call_args_list:
            sleep_times.append(call.args[0])

        self.assertListEqual(sleep_times, [1, 2, 4])

# ################################################################################################################################

    def test_kwargs_win_over_config(self) -> 'None':

        # The connection allows five retries but the call itself allows only one
        config_extra = {
            'max_retries': 5,
            'retry_sleep_time': 1,
        }

        results = [
            RequestsConnectionError('Connection refused'),
            RequestsConnectionError('Connection refused'),
        ]

        ctx = _get_wrapper(config_extra, results)

        with patch(_sleep_target):
            with self.assertRaises(BackendInvocationError):
                _ = self._invoke(ctx.wrapper, max_retries=1)

        self.assertEqual(len(ctx.session.calls), 2)

# ################################################################################################################################

    def test_backoff_threshold_stops_retries(self) -> 'None':

        # The threshold caps the total sleep time - retries stop once it is reached,
        # even though max_retries alone would allow many more attempts.
        results = []
        for _ in range(3):
            results.append(RequestsConnectionError('Connection refused'))

        ctx = _get_wrapper(None, results)

        with patch(_sleep_target) as mock_sleep:
            with self.assertRaises(BackendInvocationError):
                _ = self._invoke(ctx.wrapper, max_retries=10, retry_sleep_time=2, retry_backoff_threshold=4)

        # Two sleeps of two seconds each reach the four-second threshold, so there are three requests in total
        self.assertEqual(len(ctx.session.calls), 3)

        sleep_times = []
        for call in mock_sleep.call_args_list:
            sleep_times.append(call.args[0])

        self.assertListEqual(sleep_times, [2, 2])

# ################################################################################################################################

    def test_max_single_sleep_cap(self) -> 'None':

        # No single sleep is ever longer than the shared cap, no matter the multiplier
        config_extra = {
            'max_retries': 3,
            'retry_sleep_time': 3,
            'retry_backoff_threshold': 100,
            'retry_backoff_multiplier': 4,
        }

        results = []
        for _ in range(4):
            results.append(RequestsConnectionError('Connection refused'))

        ctx = _get_wrapper(config_extra, results)

        with patch(_sleep_target) as mock_sleep:
            with self.assertRaises(BackendInvocationError):
                _ = self._invoke(ctx.wrapper)

        sleep_times = []
        for call in mock_sleep.call_args_list:
            sleep_times.append(call.args[0])

        # 3 * 4 = 12 and 8 * 4 = 32, both above the cap, so every sleep after the first one is the cap itself
        self.assertListEqual(sleep_times, [3, _retry.Max_Sleep_Time, _retry.Max_Sleep_Time])

# ################################################################################################################################

    def test_success_after_failures(self) -> 'None':

        # Two failures followed by a success - the response comes back after three requests
        response = _FakeResponse(200)

        results = [
            RequestsTimeout('Read timed out'),
            RequestsConnectionError('Connection refused'),
            response,
        ]

        config_extra = {
            'max_retries': 5,
            'retry_sleep_time': 1,
        }

        ctx = _get_wrapper(config_extra, results)

        with patch(_sleep_target) as mock_sleep:
            out = self._invoke(ctx.wrapper)

        self.assertIs(out, response)
        self.assertEqual(len(ctx.session.calls), 3)

        sleep_times = []
        for call in mock_sleep.call_args_list:
            sleep_times.append(call.args[0])

        self.assertListEqual(sleep_times, [1, 2])

# ################################################################################################################################

    def test_error_responses_are_not_retried(self) -> 'None':

        # An HTTP error response is still a response - it comes back as-is, without any retries
        response = _FakeResponse(500)

        config_extra = {
            'max_retries': 5,
        }

        ctx = _get_wrapper(config_extra, [response])

        with patch(_sleep_target) as mock_sleep:
            out = self._invoke(ctx.wrapper)

        self.assertIs(out, response)
        self.assertEqual(len(ctx.session.calls), 1)
        mock_sleep.assert_not_called()

# ################################################################################################################################

    def test_other_exceptions_are_not_retried(self) -> 'None':

        # Only timeouts and connection errors are retried - anything else is raised at once
        config_extra = {
            'max_retries': 5,
        }

        ctx = _get_wrapper(config_extra, [Exception('Test error message')])

        with patch(_sleep_target) as mock_sleep:
            with self.assertRaises(Exception) as raised:
                _ = self._invoke(ctx.wrapper)

        self.assertEqual(str(raised.exception), 'Test error message')
        self.assertEqual(len(ctx.session.calls), 1)
        mock_sleep.assert_not_called()

# ################################################################################################################################
# ################################################################################################################################

class _FakeRESTWrapper:
    """ Stands in for an outgoing REST connection's wrapper - records the keyword arguments
    that rest_call receives so tests can assert on the exact values passed through.
    """
    def __init__(self) -> 'None':
        self.rest_call_kwargs:'stranydict' = {}

    def rest_call(self, **kwargs:'any_') -> 'None':
        self.rest_call_kwargs = kwargs

# ################################################################################################################################
# ################################################################################################################################

class RESTAdapterRetryTestCase(TestCase):
    """ Tests how RESTAdapter interacts with the retry config of the underlying connection.
    """

    def test_class_attributes_defer_to_connection_config(self) -> 'None':

        # The adapter does not carry any retry values of its own - with all of them being None,
        # the connection's own config applies and, failing that, the shared defaults do.
        self.assertIsNone(RESTAdapter.max_retries)
        self.assertIsNone(RESTAdapter.retry_sleep_time)
        self.assertIsNone(RESTAdapter.retry_backoff_threshold)
        self.assertIsNone(RESTAdapter.retry_backoff_multiplier)

        # The default of no retries at all comes from the shared constants
        self.assertEqual(_retry.Default_Max_Retries, 0)

# ################################################################################################################################

    def _get_adapter(self, class_:'any_', wrapper:'_FakeRESTWrapper') -> 'any_':
        """ Builds an adapter instance without the full service initialization,
        wiring in a fake outgoing REST connection.
        """
        conn_item = Bunch()
        conn_item.conn = wrapper

        out = object.__new__(class_)
        out.cid = ModuleCtx.CID
        out.out = Bunch()
        out.out.rest = {ModuleCtx.Conn_Name: conn_item}

        return out

# ################################################################################################################################

    def test_rest_call_passes_retry_values_through(self) -> 'None':

        # A subclass may still set its own values - they are passed through to the wrapper
        class _RetryingAdapter(RESTAdapter):
            max_retries        = 4
            retry_sleep_time   = 1
            retry_backoff_threshold = 30
            retry_backoff_multiplier = 3

        wrapper = _FakeRESTWrapper()
        adapter = self._get_adapter(_RetryingAdapter, wrapper)

        _ = adapter.rest_call(ModuleCtx.Conn_Name)

        kwargs = wrapper.rest_call_kwargs

        self.assertEqual(kwargs['max_retries'], 4)
        self.assertEqual(kwargs['retry_sleep_time'], 1)
        self.assertEqual(kwargs['retry_backoff_threshold'], 30)
        self.assertEqual(kwargs['retry_backoff_multiplier'], 3)

# ################################################################################################################################

    def test_rest_call_passes_none_by_default(self) -> 'None':

        # Without a subclass override, the adapter passes None so the connection's config can apply
        wrapper = _FakeRESTWrapper()
        adapter = self._get_adapter(RESTAdapter, wrapper)

        _ = adapter.rest_call(ModuleCtx.Conn_Name)

        kwargs = wrapper.rest_call_kwargs

        self.assertIsNone(kwargs['max_retries'])
        self.assertIsNone(kwargs['retry_sleep_time'])
        self.assertIsNone(kwargs['retry_backoff_threshold'])
        self.assertIsNone(kwargs['retry_backoff_multiplier'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
