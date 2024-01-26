# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import sleep

# Zato
from zato.common.exception import ZatoException
from zato.common.json_internal import dumps
from zato.common.util.api import new_cid

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.service import Service

    Service = Service

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

utcnow = datetime.utcnow

# ################################################################################################################################
# ################################################################################################################################

def retry_failed_msg(so_far, retry_repeats, service_name, retry_seconds, orig_cid, e):
    return '({}/{}) Retry failed for:`{}`, retry_seconds:`{}`, orig_cid:`{}`, {}:`{}`'.format(
        so_far, retry_repeats, service_name, retry_seconds, orig_cid, e.__class__.__name__, e.args)

def retry_limit_reached_msg(retry_repeats, service_name, retry_seconds, orig_cid):
    return '({}/{}) Retry limit reached for:`{}`, retry_seconds:`{}`, orig_cid:`{}`'.format(
        retry_repeats, retry_repeats, service_name, retry_seconds, orig_cid)

# ################################################################################################################################
# ################################################################################################################################

class NeedsRetry(ZatoException):
    def __init__(self, cid, inner_exc):
        self.cid = cid
        self.inner_exc = inner_exc

    def __repr__(self):
        return '<{} at {} cid:`{}` inner_exc:`{}`>'.format(self.__class__.__name__, hex(id(self)), self.cid,
            format_exc(self.inner_exc) if self.inner_exc else None)

# ################################################################################################################################
# ################################################################################################################################

class RetryFailed(ZatoException):
    def __init__(self, remaining, inner_exc):
        self.remaining = remaining
        self.inner_exc = inner_exc

    def __repr__(self):
        return '<{} at {} remaining:`{}` inner_exc:`{}`>'.format(
            self.__class__.__name__, hex(id(self)), self.remaining, format_exc(self.inner_exc) if self.inner_exc else None)

# ################################################################################################################################
# ################################################################################################################################

class InvokeRetry:
    """ Provides the invoke-retry pattern that lets one invoke a service with parametrized retries.
    """
    def __init__(self, invoking_service):
        # type: (Service) -> None
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
            except KeyError:
                msg = 'Service:`{}` does not exist, e:`{}`'.format(callback, format_exc())
                logger.error(msg)
                raise ValueError(msg)

        # Get rid of arguments our superclass doesn't understand
        for item in('async_fallback', 'callback', 'context', 'repeats', 'seconds', 'minutes'):
            kwargs.pop(item, True)

        # Note that internally we use seconds only.
        return async_fallback, callback, callback_context, retry_repeats, retry_seconds or retry_minutes * 60, kwargs

# ################################################################################################################################

    def _invoke_async_retry(self, target, retry_repeats, retry_seconds, orig_cid, call_cid, callback,
        callback_context, args, kwargs, _utcnow=utcnow):

        # Request to invoke the background service with ..
        retry_request = {
            'source':self.invoking_service.name,
            'target': target,
            'retry_repeats': retry_repeats,
            'retry_seconds': retry_seconds,
            'orig_cid': orig_cid,
            'call_cid': call_cid,
            'callback': callback,
            'callback_context': callback_context,
            'args': args,
            'kwargs': kwargs,
            'req_ts_utc': _utcnow()
        }

        return self.invoking_service.invoke_async('zato.pattern.invoke-retry.invoke-retry', dumps(retry_request), cid=call_cid)

# ################################################################################################################################

    def invoke_async(self, target, *args, **kwargs):
        async_fallback, callback, callback_context, retry_repeats, retry_seconds, kwargs = self._get_retry_settings(
            target, **kwargs)
        return self._invoke_async_retry(
            target, retry_repeats, retry_seconds, self.invoking_service.cid, kwargs['cid'], callback,
            callback_context, args, kwargs)

# ################################################################################################################################

    def invoke(self, target, *args, **kwargs):
        async_fallback, callback, callback_context, retry_repeats, retry_seconds, kwargs = self._get_retry_settings(
            target, **kwargs)

        # Let's invoke the service and find out if it works, maybe we don't need
        # to retry anything.

        kwargs['cid'] = kwargs.get('cid', new_cid())

        try:
            result = self.invoking_service.invoke(target, *args, **kwargs)
        except Exception:

            logger.warning('Could not invoke:`%s`, cid:`%s`, e:`%s`', target, self.invoking_service.cid, format_exc())

            # How we handle the exception depends on whether the caller wants us
            # to block or prefers if we retry in background.
            if async_fallback:

                # .. invoke the background service and return CID to the caller.
                return self._invoke_async_retry(
                    target, retry_repeats, retry_seconds, self.invoking_service.cid, kwargs['cid'], callback,
                    callback_context, args, kwargs)

            # We are to block while repeating
            else:
                # Repeat the given number of times sleeping for as many seconds as we are told
                remaining = retry_repeats
                result = None

                while remaining > 1:
                    try:
                        result = self.invoking_service.invoke(target, *args, **kwargs)
                    except Exception as e:
                        msg = retry_failed_msg(
                            (retry_repeats-remaining)+1, retry_repeats, target, retry_seconds, self.invoking_service.cid, e)
                        logger.info(msg)
                        sleep(retry_seconds)
                        remaining -= 1

                # OK, give up now, there's nothing more we can do
                if not result:
                    msg = retry_limit_reached_msg(retry_repeats, target, retry_seconds, self.invoking_service.cid)
                    raise ZatoException(self.invoking_service.cid, msg)
        else:
            # All good, simply return the response
            return result

# ################################################################################################################################
# ################################################################################################################################
