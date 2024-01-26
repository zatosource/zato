# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# pylint: disable=attribute-defined-outside-init

# Arrow
from arrow import utcnow

# Bunch
from bunch import Bunch

# gevent
from gevent import spawn, spawn_later

# Zato
from zato.common.json_internal import loads
from zato.server.service import Service
from zato.server.pattern.invoke_retry import RetryFailed, retry_failed_msg, retry_limit_reached_msg

# ################################################################################################################################

class InvokeRetry(Service):

# ################################################################################################################################

    def _retry(self, remaining):

        try:
            response = self.invoke(self.req_bunch.target, *self.req_bunch.args, **self.req_bunch.kwargs)
        except Exception as e:
            msg = retry_failed_msg(
                (self.req_bunch.retry_repeats-remaining)+1, self.req_bunch.retry_repeats,
                self.req_bunch.target, self.req_bunch.retry_seconds, self.req_bunch.orig_cid, e)
            self.logger.info(msg)
            raise RetryFailed(remaining-1, e)
        else:
            return response

# ################################################################################################################################

    def _notify_callback(self, is_ok, response):
        callback_request = {
            'ok': is_ok,
            'orig_cid': self.req_bunch.orig_cid,
            'call_cid': self.req_bunch.call_cid,
            'source': self.req_bunch.source,
            'target': self.req_bunch.target,
            'retry_seconds': self.req_bunch.retry_seconds,
            'retry_repeats': self.req_bunch.retry_repeats,
            'context': self.req_bunch.callback_context,
            'req_ts_utc': self.req_bunch.req_ts_utc,
            'resp_ts_utc': utcnow().isoformat(),
            'response': response
        }

        self.invoke_async(self.req_bunch.callback, callback_request)

# ################################################################################################################################

    def _on_retry_finished(self, g):
        """ A callback method invoked when a retry finishes. Will decide whether it should be
        attempted to retry the invocation again or give up notifying the uses via callback
        service if retry limit is reached.
        """
        # Was there any exception caught when retrying?
        e = g.exception

        if e:
            # Can we retry again?
            if e.remaining:
                g = spawn_later(self.req_bunch.retry_seconds, self._retry, e.remaining)
                g.link(self._on_retry_finished)

            # Reached the limit, warn users in logs, notify callback service and give up.
            else:
                msg = retry_limit_reached_msg(self.req_bunch.retry_repeats,
                    self.req_bunch.target, self.req_bunch.retry_seconds, self.req_bunch.orig_cid)
                self.logger.warning(msg)
                self._notify_callback(False, None)

        # Let the callback know it's all good
        else:
            self._notify_callback(True, g.value)

# ################################################################################################################################

    def handle(self):
        # Convert to bunch so it's easier to read everything
        self.req_bunch = Bunch(loads(self.request.payload))

        # Initial retry linked to a retry callback
        g = spawn(self._retry, self.req_bunch.retry_repeats)
        g.link(self._on_retry_finished)

# ################################################################################################################################
