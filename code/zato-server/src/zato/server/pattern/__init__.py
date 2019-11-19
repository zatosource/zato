# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from bunch import Bunch
from json import loads
from logging import DEBUG, getLogger

# Python 2/3 compatibility
from past.builtins import basestring

# Zato
from zato.common.util.json_ import dumps

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

JSON_KEYS = ('source', 'on_final', 'on_target', 'data', 'req_ts_utc')

# ################################################################################################################################
# ################################################################################################################################

class ParallelBase(object):
    """ Base class containing code common across both fan-out/fan-in and parallel execution features.
    """
    pattern_name = None
    lock_pattern = None
    counter_pattern = None
    data_pattern = None
    call_channel = None
    on_target_channel = None
    on_final_channel = None
    needs_on_final = False
    request_ctx_cid_key = None

    def __init__(self, source):
        self.source = source
        self.cid = source.cid

# ################################################################################################################################

    def invoke(self, targets, on_final, on_target=None, cid=None):
        """ Invokes targets collecting their responses, can be both as a whole or individual ones,
        and executes callback(s).
        """
        # Can be user-provided or what our source gave us
        cid = cid or self.cid

        on_final = [on_final] if isinstance(on_final, basestring) else on_final
        on_target = [on_target] if isinstance(on_target, basestring) else on_target

        on_final = on_final or ''
        on_target = on_target or ''

        # Keep everything under a distributed lock
        with self.source.lock(self.lock_pattern.format(cid)):

            # Store information how many targets there were + info on what to invoke when they complete
            self.source.kvdb.conn.set(self.counter_pattern.format(cid), len(targets))
            self.source.kvdb.conn.hmset(self.data_pattern.format(cid), {
                  'source': self.source.name,
                  'on_final': dumps(on_final),
                  'on_target': dumps(on_target),
                  'req_ts_utc': self.source.time.utcnow()
                })

            # Invoke targets
            for name, payload in targets.items():
                to_json_string = False if isinstance(payload, basestring) else True
                self.source.invoke_async(name, payload, self.call_channel, to_json_string=to_json_string,
                    zato_ctx={self.request_ctx_cid_key: cid})

        return cid

# ################################################################################################################################

    def _log_before_callbacks(self, cb_type, cb_list, invoked_service):
        logger.debug('(%s) Before %s callbacks `%s` after `%s`', self.pattern_name, cb_type, cb_list, invoked_service.name)

# ################################################################################################################################

    def on_call_finished(self, invoked_service, response, exception):

        now = invoked_service.time.utcnow()
        cid = invoked_service.wsgi_environ['zato.request_ctx.{}'.format(self.request_ctx_cid_key)]
        data_key = self.data_pattern.format(cid)
        counter_key = self.counter_pattern.format(cid)
        source, req_ts_utc, on_target = invoked_service.kvdb.conn.hmget(data_key, 'source', 'req_ts_utc', 'on_target')

        with invoked_service.lock(self.lock_pattern.format(cid)):

            data = Bunch()
            data.cid = cid
            data.resp_ts_utc = now
            data.response = response
            data.exception = exception
            data.ok = False if exception else True
            data.source = source
            data.target = invoked_service.name
            data.req_ts_utc = req_ts_utc

            # First store our response and exception (if any)
            json_data = dumps(data)
            invoked_service.kvdb.conn.hset(data_key, invoked_service.get_name(), json_data)

            on_target = loads(on_target)

            if logger.isEnabledFor(DEBUG):
                self._log_before_callbacks('on_target', on_target, invoked_service)

            # We always invoke 'on_target' callbacks, if there are any
            self.invoke_callbacks(invoked_service, data, on_target, self.on_target_channel, cid)

            # Was it the last parallel call?
            if not invoked_service.kvdb.conn.decr(counter_key):

                # Not every subclass will need final callbacks
                if self.needs_on_final:

                    payload = invoked_service.kvdb.conn.hgetall(data_key)
                    payload['data'] = {}

                    for key in (key for key in payload.keys() if key not in JSON_KEYS):
                        payload['data'][key] = loads(payload.pop(key))

                    for key in JSON_KEYS:
                        if key not in ('source', 'data', 'req_ts_utc'):
                            payload[key] = loads(payload[key])

                    on_final = payload['on_final']

                    if logger.isEnabledFor(DEBUG):
                        self._log_before_callbacks('on_final', on_final, invoked_service)

                    self.invoke_callbacks(invoked_service, payload, on_final, self.on_final_channel, cid)

                    invoked_service.kvdb.conn.delete(counter_key)
                    invoked_service.kvdb.conn.delete(data_key)

# ################################################################################################################################

    def invoke_callbacks(self, invoked_service, payload, cb_list, channel, cid):
        for name in cb_list:
            if name:
                invoked_service.invoke_async(name, payload, channel, to_json_string=True, zato_ctx={'fanout_cid': cid})

# ################################################################################################################################
# ################################################################################################################################
