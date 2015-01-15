# -*- coding: utf-8 -*-

"""
Copyright (C) 2015 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Zato
from zato.common import CHANNEL, KVDB

logger = getLogger(__name__)

class FanOut(object):
    def __init__(self, source):
        self.source = source
        self.cid = source.cid

    def invoke(self, targets, on_all_done=None, on_each_done=None, cid=None):
        """ Invokes targets collecting their responses, can be both as a whole or individual ones,
        and executes callback(s).
        """
        # Can be user-provided or what our source gave us
        cid = cid or self.cid

        # Keep everything under a distributed lock
        with self.source.lock(KVDB.LOCK_FANOUT_PATTERN.format(cid)):

            # Store information how many targets there were + info on what to invoke when they complete
            self.source.kvdb.conn.set(KVDB.FANOUT_COUNTER_PATTERN.format(cid), len(targets))
            self.source.kvdb.conn.hmset(KVDB.FANOUT_DATA_PATTERN.format(cid), {
                  'on_all_done': on_all_done,
                  'on_each_done': on_each_done,
                  'timestamp_utc': self.source.time.utcnow()
                })

            # Invoke targets
            for name, payload in targets.items():
                to_json_string = False if isinstance(payload, basestring) else True
                self.source.invoke_async(name, payload, CHANNEL.FANOUT_CALL, to_json_string=to_json_string,
                    zato_ctx={'fanout_cid': cid})

    def on_call_finished(self, invoked_service, response, exception):
        cid = invoked_service.wsgi_environ['zato.request_ctx.fanout_cid']

        with invoked_service.lock(KVDB.LOCK_FANOUT_PATTERN.format(cid)):
            left = self.source.kvdb.conn.decr(KVDB.FANOUT_COUNTER_PATTERN.format(cid))
            logger.warn('333333 %r', left)
