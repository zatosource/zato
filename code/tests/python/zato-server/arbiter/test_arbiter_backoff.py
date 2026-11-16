# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os

# Zato
from arbiter_common import new_config, Region_Config
from zato.server.arbiter import Arbiter
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from pytest import LogCaptureFixture
    from zato.common.typing_ import list_
    from zato.server.arbiter_config import WorkerContext

    LogCaptureFixture = LogCaptureFixture
    Path = Path
    WorkerContext = WorkerContext

    floatlist = list_[float]

# ################################################################################################################################
# ################################################################################################################################

# The delays of the worker before its threshold, the first one doubled by each termination
_respawn_delay_initial = 0.1
_respawn_delay_max     = 10.0
_failure_count_max     = 5
_failure_window        = 60.0

_expected_delays = [0.1, 0.2, 0.4, 0.8, 1.6]

# How far apart the terminations of a test are, in seconds
_termination_interval = 1.0

# The logger of the arbiter
_arbiter_logger = 'zato.server.arbiter'

# ################################################################################################################################
# ################################################################################################################################

def _worker_main(_ctx:'WorkerContext') -> 'None':
    pass

# ################################################################################################################################

def _new_arbiter(tmp_path:'Path') -> 'Arbiter':
    """ Returns an arbiter that is not running, with the delays and the threshold of these tests.
    """
    tmp_dir = str(tmp_path)
    config = new_config(tmp_dir)

    config.respawn_delay_initial = _respawn_delay_initial
    config.respawn_delay_max     = _respawn_delay_max
    config.failure_count_max     = _failure_count_max
    config.failure_window        = _failure_window

    region = SharedRegion(Region_Config)

    out = Arbiter(region, _worker_main, config)
    return out

# ################################################################################################################################

def _close_arbiter(arbiter:'Arbiter') -> 'None':
    os.close(arbiter.wake_read)
    os.close(arbiter.wake_write)

# ################################################################################################################################

def _get_delays(arbiter:'Arbiter', start:'float', count:'int') -> 'floatlist':
    """ Records terminations of the worker, one each interval from the start, and returns the delay after each.
    """
    worker = arbiter.worker
    out:'floatlist' = []

    for index in range(count):
        now = start + index * _termination_interval
        delay = arbiter.get_respawn_delay(worker, now)
        out.append(delay)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_each_termination_within_the_window_doubles_the_delay(tmp_path:'Path') -> 'None':
    arbiter = _new_arbiter(tmp_path)

    # The delay doubles up to the threshold.
    count = len(_expected_delays)
    delays = _get_delays(arbiter, 0.0, count)

    assert delays == _expected_delays

    _close_arbiter(arbiter)

# ################################################################################################################################

def test_a_worker_above_the_threshold_waits_for_the_ceiling(tmp_path:'Path', caplog:'LogCaptureFixture') -> 'None':
    arbiter = _new_arbiter(tmp_path)
    count = len(_expected_delays)

    # The terminations up to the threshold are not reported ..
    with caplog.at_level(logging.ERROR, logger=_arbiter_logger):
        _ = _get_delays(arbiter, 0.0, count)

    assert caplog.records == []

    # .. while the next one waits for the ceiling, before the doubled delay reaches it ..
    start = count * _termination_interval

    with caplog.at_level(logging.ERROR, logger=_arbiter_logger):
        delays = _get_delays(arbiter, start, 1)

    assert delays == [_respawn_delay_max]

    # .. and it is reported at error level with its count.
    assert len(caplog.records) == 1

    record = caplog.records[0]
    message = record.getMessage()
    expected_count = count + 1

    assert record.levelno == logging.ERROR
    assert f'terminated {expected_count} times' in message

    _close_arbiter(arbiter)

# ################################################################################################################################

def test_terminations_outside_the_window_are_not_counted(tmp_path:'Path') -> 'None':
    arbiter = _new_arbiter(tmp_path)
    count = len(_expected_delays)

    # The worker reaches its threshold ..
    _ = _get_delays(arbiter, 0.0, count)

    # .. and its next termination after the window waits for the initial delay again.
    last = (count - 1) * _termination_interval
    start = last + _failure_window + _termination_interval
    delays = _get_delays(arbiter, start, 1)

    assert delays == [_respawn_delay_initial]

    assert arbiter.worker.failure_times == [start]

    _close_arbiter(arbiter)

# ################################################################################################################################
# ################################################################################################################################
