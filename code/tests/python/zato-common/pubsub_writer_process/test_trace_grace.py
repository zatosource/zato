# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time

# Zato
from writer_common import get_message_ids, new_message_values, run_in_child
from zato.common.pubsub.sql.cleanup import PubSubCleanup
from zato.common.pubsub.sql.config import ModuleCtx
from zato.common.pubsub.sql.writes import new_pending_publication, PubSubWriter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from pytest import MonkeyPatch

    MonkeyPatch = MonkeyPatch
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

# How long a trace is kept at least after its message was received, and how long ago the old message was received
_grace_seconds = 600
_old_age_seconds = 700

# How long the test waits so that the messages received last are older than the time of the next sweep
_clock_step_seconds = 0.05

# ################################################################################################################################
# ################################################################################################################################

def _sweep_traces() -> 'None':

    # Three messages without subscribers are traces at once, one of them received before the grace period ..
    writer = PubSubWriter()
    writer.publish(new_pending_publication(new_message_values('msg-old', _old_age_seconds)))
    writer.publish(new_pending_publication(new_message_values('msg-new-1')))
    writer.publish(new_pending_publication(new_message_values('msg-new-2')))

    time.sleep(_clock_step_seconds)

    # .. each of them is past the retention age and the two older ones are above the cap of one,
    # .. yet the sweeps remove only the one received before the grace period ..
    swept = PubSubCleanup().sweep_once()

    assert swept['aged'] == 1
    assert swept['over_cap'] == 0
    assert get_message_ids('msg-old') == []
    assert len(get_message_ids('msg-new-1')) == 1
    assert len(get_message_ids('msg-new-2')) == 1

    # .. and without a grace period, the age alone decides, as with one worker.
    os.environ[ModuleCtx.Env_Trace_Grace_Seconds] = '0'

    swept = PubSubCleanup().sweep_once()

    assert swept['aged'] == 2
    assert get_message_ids('msg-new-1') == []
    assert get_message_ids('msg-new-2') == []

# ################################################################################################################################
# ################################################################################################################################

def test_a_trace_within_its_grace_period_is_kept_by_both_sweeps(tmp_path:'Path', monkeypatch:'MonkeyPatch') -> 'None':
    monkeypatch.setenv(ModuleCtx.Env_Path, str(tmp_path / 'pubsub.db'))
    monkeypatch.setenv(ModuleCtx.Env_Delivered_Max_Days, '0')
    monkeypatch.setenv(ModuleCtx.Env_Delivered_Max_Messages, '1')
    monkeypatch.setenv(ModuleCtx.Env_Trace_Grace_Seconds, str(_grace_seconds))

    run_in_child(_sweep_traces, ())

# ################################################################################################################################
# ################################################################################################################################
