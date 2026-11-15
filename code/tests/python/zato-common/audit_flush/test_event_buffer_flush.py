# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import traceback
from multiprocessing import get_context
from threading import Event, Thread

# Zato
from zato.common.audit_log.buffer import EventBuffer, PendingEvent

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # A buffer that only the timed flusher empties, after a short wait
    Max_Size = 100
    Max_Wait_Ms = 10

    # How long the test waits for the timed flusher to start its write, and for the flush to return, in seconds
    Write_Timeout = 5.0

    # How long the test confirms that the flush has not returned, in seconds
    Observation = 0.3

    # How long the test waits for its forked process, in seconds
    Join_Timeout = 30.0

# ################################################################################################################################
# ################################################################################################################################

class BlockedWriter:
    """ Writes the batches of a buffer, holding the first one until the test releases it.
    """
    def __init__(self) -> 'None':
        self.first_started = Event()
        self.first_release = Event()
        self.written:'anylist' = []

    def write_batch(self, batch:'anylist') -> 'None':
        if not self.first_started.is_set():
            self.first_started.set()
            _ = self.first_release.wait()

        self.written.extend(batch)

# ################################################################################################################################
# ################################################################################################################################

def _flush_behind_the_timed_flusher() -> 'None':
    """ Runs in a process of its own, because the timed flusher of a buffer is a thread that never stops.
    """
    exit_code = 1

    try:
        _check_flush()
        exit_code = 0

    except BaseException:
        traceback.print_exc()

    finally:
        os._exit(exit_code)

# ################################################################################################################################

def _check_flush() -> 'None':
    writer = BlockedWriter()
    buffer = EventBuffer(max_size=ModuleCtx.Max_Size, max_wait_ms=ModuleCtx.Max_Wait_Ms, write_batch=writer.write_batch)

    # The timed flusher takes the first event out of the buffer and is writing it ..
    first = PendingEvent()
    buffer.add(first)

    assert writer.first_started.wait(ModuleCtx.Write_Timeout)

    # .. while another event waits in the buffer ..
    second = PendingEvent()
    buffer.add(second)

    # .. and a flush does not return until the write of the timed flusher completes ..
    flush = Thread(target=buffer.flush)
    flush.start()
    flush.join(ModuleCtx.Observation)

    assert flush.is_alive()
    assert writer.written == []

    writer.first_release.set()
    flush.join(ModuleCtx.Write_Timeout)

    # .. after which both events are written, in the order in which they were added.
    assert not flush.is_alive()
    assert writer.written == [first, second]

# ################################################################################################################################
# ################################################################################################################################

def test_a_flush_returns_after_the_batch_of_the_timed_flusher_is_written() -> 'None':
    context = get_context('fork')

    process = context.Process(target=_flush_behind_the_timed_flusher)
    process.start()
    process.join(ModuleCtx.Join_Timeout)

    assert process.exitcode == 0

# ################################################################################################################################
# ################################################################################################################################
