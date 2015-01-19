# -*- coding: utf-8 -*-

"""
Copyright (C) 2015 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from bunch import Bunch
from json import dumps, loads
from logging import getLogger

# Zato
from zato.common import CHANNEL, KVDB

logger = getLogger(__name__)

JSON_KEYS = ('data', 'req_ts_utc', 'on_final', 'on_target')

class FanOut(object):
    def __init__(self, source):
        self.source = source
        self.cid = source.cid

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
        with self.source.lock(KVDB.LOCK_FANOUT_PATTERN.format(cid)):

            # Store information how many targets there were + info on what to invoke when they complete
            self.source.kvdb.conn.set(KVDB.FANOUT_COUNTER_PATTERN.format(cid), len(targets))
            self.source.kvdb.conn.hmset(KVDB.FANOUT_DATA_PATTERN.format(cid), {
                  'on_final': dumps(on_final),
                  'on_target': dumps(on_target),
                  'req_ts_utc': self.source.time.utcnow()
                })

            # Invoke targets
            for name, payload in targets.items():
                to_json_string = False if isinstance(payload, basestring) else True
                self.source.invoke_async(name, payload, CHANNEL.FANOUT_CALL, to_json_string=to_json_string,
                    zato_ctx={'fanout_cid': cid})

        return cid

    def on_call_finished(self, invoked_service, response, exception):

        now = invoked_service.time.utcnow()
        cid = invoked_service.wsgi_environ['zato.request_ctx.fanout_cid']
        data_key = KVDB.FANOUT_DATA_PATTERN.format(cid)
        counter_key = KVDB.FANOUT_COUNTER_PATTERN.format(cid)

        with invoked_service.lock(KVDB.LOCK_FANOUT_PATTERN.format(cid)):

            data = Bunch()
            data.cid = cid
            data.resp_ts_utc = now
            data.response = response
            data.exception = exception
            data.ok = False if exception else True

            # First store our response and exception (if any)
            json_data = dumps(data)
            invoked_service.kvdb.conn.hset(data_key, invoked_service.get_name(), json_data)

            # We always invoke 'on_target' callbacks, if there are any
            self.invoke_callbacks(
                invoked_service, data, loads(invoked_service.kvdb.conn.hget(data_key, 'on_target')),
                CHANNEL.FANOUT_ON_TARGET, cid)

            # Was it the last parallel call?
            if not invoked_service.kvdb.conn.decr(counter_key):

                payload = invoked_service.kvdb.conn.hgetall(data_key)
                payload['data'] = {}

                for key in (key for key in payload.keys() if key not in JSON_KEYS):
                    payload['data'][key] = loads(payload.pop(key))

                for key in JSON_KEYS:
                    if key not in ('data', 'req_ts_utc'):
                        payload[key] = loads(payload[key])

                self.invoke_callbacks(invoked_service, payload, payload['on_final'], CHANNEL.FANOUT_ON_FINAL, cid)

                invoked_service.kvdb.conn.delete(counter_key)
                invoked_service.kvdb.conn.delete(data_key)

    def invoke_callbacks(self, invoked_service, payload, cb_list, channel, cid):
        for name in cb_list:
            if name:
                invoked_service.invoke_async(name, payload, channel, to_json_string=True, zato_ctx={'fanout_cid': cid})
