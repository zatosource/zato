# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from traceback import format_exc

# anyjson
from anyjson import dumps

# gevent
from gevent import sleep

# Zato
from zato.common import ZatoException

logger = getLogger(__name__)

# ################################################################################################################################

def retry_failed_msg(so_far, retry_repeats, service_name, retry_seconds, orig_cid, e):
    return '({}/{}) Retry failed for:`{}`, retry_seconds:`{}`, orig_cid:`{}`, e:`{}`'.format(
        so_far, retry_repeats, service_name, retry_seconds, orig_cid, format_exc(e))

def retry_limit_reached_msg(retry_repeats, service_name, retry_seconds, orig_cid):
    return '({}/{}) Retry limit reached for:`{}`, retry_seconds:`{}`, orig_cid:`{}`'.format(
        retry_repeats, retry_repeats, service_name, retry_seconds, orig_cid)

# ################################################################################################################################

class NeedsRetry(ZatoException):
    def __init__(self, cid, inner_exc):
        self.cid = cid
        self.inner_exc = inner_exc

    def __repr__(self):
        return '<{} at {} cid:`{}` inner_exc:`{}`>'.format(self.__class__.__name__, hex(id(self)), self.cid,
            format_exc(self.inner_exc) if self.inner_exc else None)

# ################################################################################################################################

class RetryFailed(ZatoException):
    def __init__(self, remaining, inner_exc):
        self.remaining = remaining
        self.inner_exc = inner_exc

    def __repr__(self):
        return '<{} at {} remaining:`{}` inner_exc:`{}`>'.format(
            self.__class__.__name__, hex(id(self)), self.remaining, format_exc(self.inner_exc) if self.inner_exc else None)

# ################################################################################################################################

class InvokeRetry(object):
    """ Provides the invoke-retry pattern that lets one invoke a service with parametrized retries.
    """
    def __init__(self, invoking_service):
        self.invoking_service = invoking_service

# ################################################################################################################################

    def _get_retry_settings(self, target, **kwargs):
        async_fallback = kwargs.get('async_fallback')
        callback = kwargs.get('callback')
        callback_context = kwargs.get('context')
        retry_repeats = kwargs.get('repeats')
        retry_seconds = kwargs.get('seconds')
        retry_minutes = kwargs.get('minutes')

        if async_fallback:
            items = ('callback', 'repeats')
            for item in items:
                value = kwargs.get(item)
                if not value:
                    msg = 'Could not invoke `{}`, `{}` was not provided ({})'.format(target, item, value)
                    logger.error(msg)
                    raise ValueError(msg)

            if retry_seconds and retry_minutes:
                msg = 'Could not invoke `{}`, only one of seconds:`{}` and minutes:`{}` can be given'.format(
                    target, retry_seconds, retry_minutes)
                logger.error(msg)
                raise ValueError(msg)

            if not(retry_seconds or retry_minutes):
                msg = 'Could not invoke `{}`, exactly one of seconds:`{}` or minutes:`{}` must be given'.format(
                    target, retry_seconds, retry_minutes)
                logger.error(msg)
                raise ValueError(msg)

            try:
                self.invoking_service.server.service_store.name_to_impl_name[callback]
            except KeyError, e:
                msg = 'Service:`{}` does not exist, e:`{}`'.format(callback, format_exc(e))
                logger.error(msg)
                raise ValueError(msg)

        # Get rid of arguments our superclass doesn't understand
        for item in('async_fallback', 'callback', 'context', 'repeats', 'seconds', 'minutes'):
            kwargs.pop(item, True)

        # Note that internally we use seconds only.
        return async_fallback, callback, callback_context, retry_repeats, retry_seconds or retry_minutes * 60, kwargs

# ################################################################################################################################

    def _invoke_async_retry(self, target, retry_repeats, retry_seconds, orig_cid, callback, callback_context, args, kwargs):

        # Request to invoke the background service with ..
        retry_request = {
            'target': target,
            'retry_repeats': retry_repeats,
            'retry_seconds': retry_seconds,
            'orig_cid': orig_cid,
            'callback': callback,
            'callback_context': callback_context,
            'args': args,
            'kwargs': kwargs
        }

        return self.invoking_service.invoke_async('zato.pattern.invoke-retry.invoke-retry', dumps(retry_request))

# ################################################################################################################################

    def invoke_async_retry(self, target, *args, **kwargs):
        async_fallback, callback, callback_context, retry_repeats, retry_seconds, kwargs = self._get_retry_settings(
            target, **kwargs)
        return self._invoke_async_retry(
            target, retry_repeats, retry_seconds, self.invoking_service.cid, callback, callback_context, args, kwargs)

# ################################################################################################################################

    def invoke_retry(self, target, *args, **kwargs):
        async_fallback, callback, callback_context, retry_repeats, retry_seconds, kwargs = self._get_retry_settings(
            target, **kwargs)

        # Let's invoke the service and find out if it works, maybe we don't need
        # to retry anything.

        try:
            result = self.invoking_service.invoke(target, *args, **kwargs)
        except Exception, e:

            msg = 'Could not invoke:`{}`, cid:`{}`, e:`{}`'.format(target, self.invoking_service.cid, format_exc(e))
            logger.warn(msg)

            # How we handle the exception depends on whether the caller wants us
            # to block or prefers if we retry in background.
            if async_fallback:

                # .. invoke the background service and return CID to the caller.
                cid = self._invoke_async_retry(
                    target, retry_repeats, retry_seconds, self.invoking_service.cid, callback, callback_context, args, kwargs)
                raise NeedsRetry(cid, e)

            # We are to block while repeating
            else:
                # Repeat the given number of times sleeping for as many seconds as we are told
                remaining = retry_repeats
                result = None
                
                while remaining > 1:
                    try:
                        result = self.invoking_service.invoke(target, *args, **kwargs)
                    except Exception, e:
                        msg = retry_failed_msg(
                            (retry_repeats-remaining)+1, retry_repeats, target, retry_seconds, self.invoking_service.cid, e)
                        logger.info(msg)
                        sleep(retry_seconds)
                        remaining -= 1

                # OK, give up now, there's nothing more we can do
                if not result:
                    msg = retry_limit_reached_msg(retry_repeats, target, retry_seconds, self.invoking_service.cid)
                    logger.warn(msg)
                    raise ZatoException(self.invoking_service.cid, msg)
        else:
            # All good, simply return the response
            return result

# ################################################################################################################################
