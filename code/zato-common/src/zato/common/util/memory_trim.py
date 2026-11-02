# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The release of free heap memory to the operating system. The C allocator retains the memory that a process freed
# for reuse, so after a burst of large payloads the resident size of the process stays at the size of the burst.
# Two settings address this. A fixed mmap threshold keeps every large payload in a mapping of its own, which
# returns to the operating system when the payload is freed - by default, the allocator raises the threshold
# after each large free, up to 32 MB, and large payloads then remain on the heap. malloc_trim, run in a thread
# of its own, returns the free pages of every arena of the allocator.

# stdlib
from ctypes import CDLL
from logging import getLogger
from threading import Event, Thread

# gevent
from gevent import get_hub
from gevent.monkey import is_module_patched

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How often the free heap memory is released, in seconds.
Trim_Interval_Seconds = 60

# Allocations of at least this many bytes receive a mapping of their own.
Mmap_Threshold_Bytes = 128 * 1024

# The mallopt parameter of the mmap threshold in the GNU C library.
_m_mmap_threshold = -3

# The C library of the process, which provides malloc_trim and mallopt with the GNU C library only.
_libc = CDLL(None)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The trimmer of this process, once started.
    Trimmer:'MemoryTrimmer | None' = None

# ################################################################################################################################
# ################################################################################################################################

class MemoryTrimmer:
    """ Releases the free heap memory of the process at each interval, in a thread of its own.
    """

    def __init__(self, interval_seconds:'float' = Trim_Interval_Seconds) -> 'None':
        self.interval_seconds = interval_seconds
        self._stop_event = Event()
        self._thread = Thread(target=self._run, name='memory-trim', daemon=True)

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts releasing the free memory.
        """
        self._thread.start()

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops releasing the free memory after the release in progress, if any.
        """
        self._stop_event.set()

# ################################################################################################################################

    def trim(self) -> 'None':
        """ Returns the free pages of every arena of the allocator to the operating system.
        """
        _ = _libc.malloc_trim(0)

# ################################################################################################################################

    def _trim_off_loop(self) -> 'None':
        """ Runs one release, in the thread pool of the gevent hub under gevent, because malloc_trim
        walks the whole heap in C without yielding to the event loop.
        """
        if is_module_patched('threading'):
            hub = get_hub()
            _ = hub.threadpool.apply(self.trim)
        else:
            self.trim()

# ################################################################################################################################

    def _run(self) -> 'None':
        """ Releases the free memory at each interval, until the trimmer is stopped.
        """
        while not self._stop_event.wait(self.interval_seconds):
            try:
                self._trim_off_loop()
            except Exception:
                logger.exception('Memory trim failed')

# ################################################################################################################################
# ################################################################################################################################

def start_memory_trimmer() -> 'None':
    """ Fixes the mmap threshold and starts the trimmer of this process, unless it is running already
    or the C library has no malloc_trim.
    """
    if ModuleCtx.Trimmer:
        return

    if not hasattr(_libc, 'malloc_trim'):
        return

    _ = _libc.mallopt(_m_mmap_threshold, Mmap_Threshold_Bytes)

    ModuleCtx.Trimmer = MemoryTrimmer()
    ModuleCtx.Trimmer.start()

# ################################################################################################################################
# ################################################################################################################################
