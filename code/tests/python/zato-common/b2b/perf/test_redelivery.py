# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.test.b2b_perf import new_perf_settings, PerfRun
from zato.common.test.b2b_perf_common import FaultType, MessageKind, Steady_Rate
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

# The share of the deliveries of the host the partner refuses, of those whose acknowledgment it discards,
# and of its own messages it posts twice, in percent.
_refuse_percent    = 5.0
_drop_ack_percent  = 2.0
_duplicate_percent = 5.0

# The kinds of message the host sends, whose deliveries the partner refuses or does not acknowledge.
_host_kinds = (MessageKind.Response, MessageKind.Notification)

# The faults after which the host delivers a message again.
_resend_faults = (FaultType.Refused, FaultType.Ack_Dropped)

# ################################################################################################################################
# ################################################################################################################################

def test_redelivery_under_load(database:'PerfDatabase', tmp_path:'Path', record_property:'callable_') -> 'None':
    """ With a partner that refuses some deliveries of the host, discards some acknowledgments and posts some of its
    own messages twice, each resend reads the stored message with one select, each message is delivered as many times
    as its faults require, and each one reaches the application of its receiver once.
    """
    work_dir = str(tmp_path)
    half_rate = Steady_Rate / 2

    settings = new_perf_settings(work_dir, database.env, half_rate, half_rate)
    settings.refuse_percent = _refuse_percent
    settings.drop_ack_percent = _drop_ack_percent
    settings.duplicate_percent = _duplicate_percent

    run = PerfRun(settings)
    result = run.run()

    properties = result_properties(result)

    for name, value in properties.items():
        record_property(name, value)

    assert result.resends > 0
    assert result.body_selects == result.resends

    assert not result.lost, result.lost
    assert not result.duplicated, result.duplicated

    for trace in result.traces.values():

        assert trace.started_at, trace
        assert trace.deliveries == 1, trace
        assert trace.redeliveries == 0, trace

        # Each fault of a delivery of the host is followed by one more delivery ..
        if trace.kind in _host_kinds:
            resend_faults = 0

            for fault in trace.faults:
                if fault in _resend_faults:
                    resend_faults += 1

            expected_attempts = 1 + resend_faults

        # .. while the second post of a message of the partner is answered as a duplicate and not delivered again.
        else:
            expected_attempts = 1

        assert trace.attempts == expected_attempts, trace

# ################################################################################################################################
# ################################################################################################################################
