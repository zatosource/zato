# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.test.b2b_perf import new_perf_settings, PerfRun
from zato.common.test.b2b_perf_common import MessageKind, Steady_Rate
from zato.common.test.b2b_perf_results import result_properties

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from perf_db import PerfDatabase
    from zato.common.typing_ import callable_
    callable_ = callable_
    Path = Path
    PerfDatabase = PerfDatabase

# ################################################################################################################################
# ################################################################################################################################

# The kinds of message the partner sends, which the host acknowledges.
_partner_kinds = (MessageKind.Request, MessageKind.Signal)

# ################################################################################################################################
# ################################################################################################################################

def test_restart_under_load(database:'PerfDatabase', tmp_path:'Path', record_property:'callable_') -> 'None':
    """ The host is killed in the middle of the measurement and started again. Every message it acknowledged before
    the kill reaches its application, no message reaches an application twice without the flag of a possible
    duplicate, every message is acknowledged in the end, and the signals received after the restart are matched
    against the business transactions recovered from the audit log.
    """
    work_dir = str(tmp_path)
    half_rate = Steady_Rate / 2

    settings = new_perf_settings(work_dir, database.env, half_rate, half_rate)
    settings.kill_after_seconds = settings.duration_seconds / 2

    run = PerfRun(settings)
    result = run.run()
    restart = run.restart

    first_ack_at = 0.0

    for trace in result.traces.values():

        # A message whose record was committed right before the kill was recovered and delivered
        # without the line that says when it was handed over.
        if not trace.started_at:
            assert trace.is_delivered, trace
            continue

        assert trace.acked_at is not None, trace
        assert not trace.is_failed, trace
        assert trace.deliveries <= 1, trace

        if trace.kind in _partner_kinds:

            # A message the host acknowledged before the kill was received by its application ..
            if trace.acked_at < restart.killed_at:
                assert trace.is_delivered, trace

            # .. and the first acknowledgment after the restart is the end of the time the restart takes.
            elif trace.acked_at >= restart.started_at:
                if not first_ack_at:
                    first_ack_at = trace.acked_at
                else:
                    first_ack_at = min(first_ack_at, trace.acked_at)

        # A signal delivered after the restart moves the business transaction recovered from the audit log.
        if trace.kind == MessageKind.Signal:
            if trace.delivered_at is not None:
                if trace.delivered_at >= restart.ready_at:
                    assert trace.match_state, trace

    assert first_ack_at, 'No message was acknowledged after the restart'

    restart_seconds = first_ack_at - restart.started_at
    ready_seconds = restart.ready_at - restart.started_at

    properties = result_properties(result)
    properties['restart_to_ready_seconds'] = round(ready_seconds, 2)
    properties['restart_to_first_ack_seconds'] = round(restart_seconds, 2)

    for name, value in properties.items():
        record_property(name, value)

    assert not result.lost, result.lost
    assert not result.duplicated, result.duplicated

# ################################################################################################################################
# ################################################################################################################################
