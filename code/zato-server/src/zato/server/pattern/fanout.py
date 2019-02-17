# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import CHANNEL, KVDB
from zato.server.pattern import ParallelBase

class FanOut(ParallelBase):
    pattern_name = 'FanOut'
    lock_pattern = KVDB.LOCK_FANOUT_PATTERN
    counter_pattern = KVDB.FANOUT_COUNTER_PATTERN
    data_pattern = KVDB.FANOUT_DATA_PATTERN
    call_channel = CHANNEL.FANOUT_CALL
    on_target_channel = CHANNEL.FANOUT_ON_TARGET
    on_final_channel = CHANNEL.FANOUT_ON_FINAL
    needs_on_final = True
    request_ctx_cid_key = 'fanout_cid'
