# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from json import loads
from unittest import TestCase

# bunch
from bunch import Bunch

# mock
from mock import patch

# Zato
from zato.common import ZatoException
from zato.common.test import rand_int, rand_string
from zato.common.util import new_cid
from zato.server.pattern.invoke_retry import InvokeRetry, retry_failed_msg, retry_limit_reached_msg

# ################################################################################################################################

def raise_exception():
    raise Exception()

# ################################################################################################################################

class DummyTargetService(object):
    def __init__(self, callback=None, callback_impl_name=None, cid=None, result=None, raise_on_invoke=False):
        self.server = Bunch(service_store=Bunch(name_to_impl_name={callback:callback_impl_name}))
        self.cid = cid
        self.result = result
        self.raise_on_invoke = raise_on_invoke
        self.name = 'DummyTargetService'

        self.invoke_called_times = 0
        self.invoke_args = None
        self.invoke_kwargs = None

        self.invoke_async_args = None
        self.invoke_async_kwargs = None

    def invoke(self, *args, **kwargs):
        self.invoke_args = args
        self.invoke_kwargs = kwargs
        self.invoke_called_times += 1

        if self.raise_on_invoke:
            raise Exception(self.cid)

        return self.result

    def invoke_async(self, *args, **kwargs):
        self.invoke_async_args = args
        self.invoke_async_kwargs = kwargs

        return self.cid

# ################################################################################################################################

class InvokeRetryTestCase(TestCase):

# ################################################################################################################################

    def setUp(self):
        self.maxDiff = None

# ################################################################################################################################

    def test_retry_failed_msg(self):
        so_far = rand_int()
        retry_repeats = rand_int()
        service_name = rand_string()
        retry_seconds = rand_int()
        orig_cid = rand_string()

        try:
            raise_exception()
        except Exception as e:
            pass

        msg = retry_failed_msg(so_far, retry_repeats, service_name, retry_seconds, orig_cid, e)

        self.assertTrue(msg.startswith('({}/{}) Retry failed for:`{}`, retry_seconds:`{}`, orig_cid:`{}`'.format(
            so_far, retry_repeats, service_name, retry_seconds, orig_cid)))
        self.assertIn('raise_exception()', msg)
        self.assertIn('raise Exception()', msg)

# ################################################################################################################################

    def test_retry_limit_reached_msg(self):
        retry_repeats = rand_int()
        service_name = rand_string()
        retry_seconds = rand_int()
        orig_cid = rand_string()

        msg = retry_limit_reached_msg(retry_repeats, service_name, retry_seconds, orig_cid)

        self.assertEquals(msg, '({}/{}) Retry limit reached for:`{}`, retry_seconds:`{}`, orig_cid:`{}`'.format(
            retry_repeats, retry_repeats, service_name, retry_seconds, orig_cid))

# ################################################################################################################################

    def test_get_retry_settings_no_async_callback(self):

        for needs_seconds in True, False:

            callback = rand_string()

            target = rand_string()
            kwargs = {
                'async_fallback': False,
                'callback': callback,
                'context': {rand_string():rand_string(), rand_int():rand_int()},
                'repeats': rand_int(),
                'seconds': rand_int() if needs_seconds else 0,
                'minutes': rand_int() if not needs_seconds else 0,
                'custom1': 'custom1',
                'custom2': 'custom2',
                }

            kwargs_copy = deepcopy(kwargs)

            ir = InvokeRetry(None)

            async_fallback, callback, callback_context, retry_repeats, retry_seconds, kwargs = ir._get_retry_settings(
                target, **kwargs)

            self.assertFalse(async_fallback)

            self.assertNotIn('callback', kwargs)
            self.assertEquals(callback, kwargs_copy['callback'])

            self.assertNotIn('context', kwargs)
            self.assertDictEqual(callback_context, kwargs_copy['context'])

            self.assertNotIn('repeats', kwargs)
            self.assertEquals(retry_repeats, kwargs_copy['repeats'])

            if needs_seconds:
                self.assertNotIn('seconds', kwargs)
                self.assertEquals(retry_seconds, kwargs_copy['seconds'])
            else:
                self.assertNotIn('minutes', kwargs)
                self.assertEquals(retry_seconds, kwargs_copy['minutes'] * 60)

            self.assertDictEqual(kwargs, {'custom1':'custom1', 'custom2':'custom2'})

# ################################################################################################################################

    def test_get_retry_settings_has_async_callback(self):

        callback = rand_string()
        callback_impl_name = rand_string()

        invoking_service = DummyTargetService(callback, callback_impl_name)

        for needs_seconds in True, False:

            target = rand_string()
            kwargs = {
                'async_fallback': True,
                'callback': callback,
                'context': {rand_string():rand_string(), rand_int():rand_int()},
                'repeats': rand_int(),
                'seconds': rand_int() if needs_seconds else 0,
                'minutes': rand_int() if not needs_seconds else 0,
                'custom1': 'custom1',
                'custom2': 'custom2',
                }

            kwargs_copy = deepcopy(kwargs)

            ir = InvokeRetry(invoking_service)

            async_fallback, callback, callback_context, retry_repeats, retry_seconds, kwargs = ir._get_retry_settings(
                target, **kwargs)

            self.assertTrue(async_fallback)

            self.assertNotIn('callback', kwargs)
            self.assertEquals(callback, kwargs_copy['callback'])

            self.assertNotIn('context', kwargs)
            self.assertDictEqual(callback_context, kwargs_copy['context'])

            self.assertNotIn('repeats', kwargs)
            self.assertEquals(retry_repeats, kwargs_copy['repeats'])

            if needs_seconds:
                self.assertNotIn('seconds', kwargs)
                self.assertEquals(retry_seconds, kwargs_copy['seconds'])
            else:
                self.assertNotIn('minutes', kwargs)
                self.assertEquals(retry_seconds, kwargs_copy['minutes'] * 60)

            self.assertDictEqual(kwargs, {'custom1':'custom1', 'custom2':'custom2'})

# ################################################################################################################################

    def test_get_retry_settings_has_invalid_async_callback(self):

        ir = InvokeRetry(None)

        callback = [None, rand_string()]
        repeats = [None, rand_int()]

        target = rand_string()

        for callback_item in callback:
            for repeats_item in repeats:
                kwargs = {
                    'async_fallback': True,
                    'callback': callback_item,
                    'repeats': repeats_item,
                }

            try:
                ir._get_retry_settings(target, **kwargs)
            except ValueError as e:

                for name in 'callback', 'repeats':
                    if name in e.message:
                        self.assertEquals(e.message, 'Could not invoke `{}`, `{}` was not provided ({})'.format(
                            target, name, None))
            else:
                self.assertTrue(callback_item is not None)
                self.assertTrue(repeats_item is not None)

# ################################################################################################################################

    def test_get_retry_settings_has_async_callback_both_secs_mins(self):
        ir = InvokeRetry(None)
        target = rand_string()

        kwargs = {
            'async_fallback': True,
            'callback': rand_string(),
            'context': {},
            'repeats': rand_int(),
            'seconds': rand_int(),
            'minutes': rand_int(),
            }

        try:
            ir._get_retry_settings(target, **kwargs)
        except ValueError as e:
            self.assertEquals(e.message, 'Could not invoke `{}`, only one of seconds:`{}` and minutes:`{}` can be given'.format(
                target, kwargs['seconds'], kwargs['minutes']))
        else:
            self.fail('Expected a ValueError')

# ################################################################################################################################

    def test_get_retry_settings_has_async_callback_no_secs_mins(self):
        ir = InvokeRetry(None)
        target = rand_string()

        kwargs = {
            'async_fallback': True,
            'callback': rand_string(),
            'context': {},
            'repeats': rand_int(),
            'seconds': 0,
            'minutes': 0,
            }

        try:
            ir._get_retry_settings(target, **kwargs)
        except ValueError as e:
            self.assertEquals(
                e.message, 'Could not invoke `{}`, exactly one of seconds:`{}` or minutes:`{}` must be given'.format(
                    target, kwargs['seconds'], kwargs['minutes']))
        else:
            self.fail('Expected a ValueError')

# ################################################################################################################################

    def test_get_retry_settings_has_async_callback_invalid_target(self):
        ir = InvokeRetry(DummyTargetService())

        kwargs = {
            'async_fallback': True,
            'callback': rand_string(),
            'context': {},
            'repeats': rand_int(),
            'seconds': rand_int(),
            'minutes': 0,
        }

        try:
            ir._get_retry_settings(rand_string(), **kwargs)
        except ValueError as e:
            prefix = 'Service:`{}` does not exist, e:`Traceback (most recent call last):'.format(kwargs['callback'])
            self.assertTrue(e.message.startswith(prefix))
            self.assertIn("KeyError: u'{}'".format(kwargs['callback']), e.message)
        else:
            self.fail('Expected a ValueError')

# ################################################################################################################################

    def test_invoke_async_retry(self):
        target = 'target_{}'.format(rand_string())
        callback = 'callback_{}'.format(rand_string())
        callback_impl_name = 'callback_impl_name_{}'.format(rand_string())
        cid = new_cid()

        invoking_service = DummyTargetService(callback, callback_impl_name, cid)
        ir = InvokeRetry(invoking_service)

        kwargs = {
            'async_fallback': True,
            'callback': callback,
            'context': {rand_string():rand_string()},
            'repeats': rand_int(),
            'seconds': rand_int(),
            'minutes': 0,
            'cid': cid
        }

        kwargs_copy = deepcopy(kwargs)

        call_cid = ir.invoke_async(target, **kwargs)

        self.assertTrue(len(invoking_service.invoke_async_args), 2)
        self.assertEquals(invoking_service.invoke_async_kwargs, {'cid': cid})

        invoke_retry_service, retry_request = invoking_service.invoke_async_args
        self.assertEquals(invoke_retry_service, 'zato.pattern.invoke-retry.invoke-retry')

        retry_request = loads(retry_request)

        self.assertEquals(retry_request['target'], target)
        self.assertEquals(retry_request['callback'], callback)
        self.assertEquals(retry_request['args'], [])
        self.assertEquals(retry_request['retry_seconds'], kwargs_copy['seconds'])
        self.assertEquals(retry_request['kwargs'], {'cid': call_cid})
        self.assertEquals(retry_request['orig_cid'], cid)
        self.assertEquals(retry_request['retry_repeats'], kwargs_copy['repeats'])
        self.assertEquals(retry_request['callback_context'], kwargs_copy['context'])

# ################################################################################################################################

    def test_invoke_retry_ok(self):

        target = 'target_{}'.format(rand_string())
        callback = 'callback_{}'.format(rand_string())
        callback_impl_name = 'callback_impl_name_{}'.format(rand_string())
        cid = new_cid()
        expected_result = rand_string()

        invoking_service = DummyTargetService(callback, callback_impl_name, cid, expected_result)
        ir = InvokeRetry(invoking_service)

        kwargs = {
            'async_fallback': True,
            'callback': callback,
            'context': {rand_string():rand_string()},
            'repeats': rand_int(),
            'seconds': rand_int(),
            'minutes': 0,
            'cid': cid,
        }

        result = ir.invoke(target, 1, 2, 3, **kwargs)
        self.assertEquals(expected_result, result)

        self.assertTrue(len(invoking_service.invoke_args), 2)
        self.assertEquals(invoking_service.invoke_args, (target, 1, 2, 3))
        self.assertEquals(invoking_service.invoke_kwargs, {'cid':cid})

# ################################################################################################################################

    def test_invoke_retry_exception_no_async(self):

        class Sleep(object):
            def __init__(self):
                self.times_called = 0
                self.retry_seconds = []

            def __call__(self, retry_seconds):
                self.times_called += 1
                self.retry_seconds.append(retry_seconds)

        sleep = Sleep()

        with patch('zato.server.pattern.invoke_retry.sleep', sleep):

            target = 'target_{}'.format(rand_string())
            callback = 'callback_{}'.format(rand_string())
            callback_impl_name = 'callback_impl_name_{}'.format(rand_string())
            cid = new_cid()
            expected_result = rand_string()

            invoking_service = DummyTargetService(callback, callback_impl_name, cid, expected_result, raise_on_invoke=True)
            ir = InvokeRetry(invoking_service)

            kwargs = {
                'async_fallback': False,
                'callback': callback,
                'context': {rand_string():rand_string()},
                'repeats': rand_int(1, 10),
                'seconds': 0.01,
                'minutes': 0,
            }

            kwargs_copy = deepcopy(kwargs)

            try:
                ir.invoke(target, 1, 2, 3, **kwargs)
            except ZatoException as e:
                expected_msg = retry_limit_reached_msg(kwargs_copy['repeats'], target, kwargs_copy['seconds'], invoking_service.cid)
                self.assertEquals(e.cid, cid)
                self.assertEquals(e.message, expected_msg)
                self.assertEquals(invoking_service.invoke_called_times, kwargs_copy['repeats'])

                self.assertEquals(sleep.times_called, kwargs_copy['repeats']-1)
                self.assertEquals(sleep.retry_seconds, [kwargs_copy['seconds']] * (kwargs_copy['repeats']-1))

            else:
                self.fail('Expected a ZatoException')

# ################################################################################################################################

    def test_invoke_retry_exception_has_async(self):

        target = 'target_{}'.format(rand_string())
        callback = 'callback_{}'.format(rand_string())
        callback_impl_name = 'callback_impl_name_{}'.format(rand_string())
        cid = new_cid()
        expected_result = rand_string()

        invoking_service = DummyTargetService(callback, callback_impl_name, cid, expected_result, raise_on_invoke=True)
        ir = InvokeRetry(invoking_service)

        kwargs = {
            'async_fallback': True,
            'callback': callback,
            'context': {rand_string():rand_string()},
            'repeats': rand_int(1, 10),
            'seconds': 0.01,
            'minutes': 0,
        }

        result = ir.invoke(target, 1, 2, 3, **kwargs)
        self.assertEquals(result, cid)

# ################################################################################################################################
