# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import CHANNEL, KVDB
from zato.server.pattern import ParallelBase

class ParallelExec(ParallelBase):
    pattern_name = 'ParallelExec'
    lock_pattern = KVDB.LOCK_PARALLEL_EXEC_PATTERN
    counter_pattern = KVDB.PARALLEL_EXEC_COUNTER_PATTERN
    data_pattern = KVDB.PARALLEL_EXEC_DATA_PATTERN
    call_channel = CHANNEL.PARALLEL_EXEC_CALL
    on_target_channel = CHANNEL.PARALLEL_EXEC_ON_TARGET
    request_ctx_cid_key = 'parallel_exec_cid'

    def invoke(self, targets, on_target, cid=None):
        return super(ParallelExec, self).invoke(targets, None, on_target, cid)
