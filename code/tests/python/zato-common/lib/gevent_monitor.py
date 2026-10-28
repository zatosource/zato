# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys
from dataclasses import dataclass
from time import perf_counter
from traceback import format_stack
from weakref import WeakSet

# gevent
from gevent import get_hub, getcurrent, sleep, spawn
from gevent.monkey import get_original, is_module_patched

# greenlet
from greenlet import settrace

# pytest
from pytest import fail, hookimpl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent import Greenlet
    from pytest import Function
    from zato.common.typing_ import any_, anylist, callable_, intlist

    any_ = any_
    anylist = anylist
    callable_ = callable_
    Function = Function
    Greenlet = Greenlet
    intlist = intlist

    floatlist = list[float]

blocking_list = list['Blocking']

# ################################################################################################################################
# ################################################################################################################################

# A greenlet that runs longer than this without yielding blocks the event loop, in seconds.
Max_Blocking_Time = 0.1

# How long the lag greenlet sleeps between two measurements, in seconds.
Lag_Interval = 0.01

# How often the switch rate and the number of live greenlets are sampled, in seconds.
Sample_Interval = 1.0

# How often the stack thread checks whether a run of a greenlet blocks the event loop, in seconds.
Stack_Check_Interval = 0.05

# The thread and the sleep of the operating system, which the stack thread runs with while the loop is blocked.
_start_native_thread = get_original('_thread', 'start_new_thread')
_native_sleep = get_original('time', 'sleep')

# The events of the greenlet trace function that switch from one greenlet to another.
_switch_events = ('switch', 'throw')

# What a blocking reports when its greenlet ended before its stack could be captured.
_no_stack = 'The greenlet ended before its stack was captured.\n'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Blocking:
    """ One run of a greenlet that kept the event loop from running for longer than the limit.
    """
    greenlet: str
    duration: float
    stack:    str

# ################################################################################################################################

@dataclass(init=False)
class MonitorSummary:
    """ What the monitor measured since its window began.
    """
    blockings:    blocking_list
    max_blocking: float

    # The event loop lag, in seconds.
    lag_p50: float
    lag_p99: float
    lag_max: float

    switches_per_second: float
    greenlets_max:       int

# ################################################################################################################################
# ################################################################################################################################

def percentile(values:'floatlist', fraction:'float') -> 'float':
    """ Returns the nearest-rank percentile of the values, or zero when there are none.
    """
    if not values:
        out = 0.0
    else:
        ordered = sorted(values)
        last_index = len(ordered) - 1
        index = round(fraction * last_index)
        out = ordered[index]

    return out

# ################################################################################################################################
# ################################################################################################################################

class EventLoopMonitor:
    """ Measures the event loop of the hub of the main thread - each greenlet run that blocks it, how late a sleeping
    greenlet wakes up, how often greenlets switch and how many of them are alive.
    """

    def __init__(self, max_blocking_time:'float'=Max_Blocking_Time) -> 'None':
        self.max_blocking_time = max_blocking_time

        self.blockings:'blocking_list' = []
        self.lags:'floatlist' = []
        self.switch_rates:'floatlist' = []
        self.greenlet_counts:'intlist' = []
        self.switch_count = 0

        self.is_started = False

        self._hub:'any_' = None
        self._switched_at = perf_counter()
        self._window_started_at = self._switched_at
        self._previous_trace:'callable_ | None' = None

        # The greenlets that were switched to, from which the live ones are counted, and the one running now.
        self._greenlets:'WeakSet[any_]' = WeakSet()
        self._active:'any_' = None

        # The stack that the stack thread captured during the current run, and the start of that run.
        self._captured_stack = ''
        self._captured_run = 0.0

        self._workers:'list[Greenlet]' = []
        self._is_stack_thread_running = False

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the trace function, the stack thread and the greenlets that measure the event loop.
        """
        if not is_module_patched('threading'):
            raise Exception('The event loop monitor requires gevent.monkey.patch_all to run before any other import')

        self._hub = get_hub()
        self._active = getcurrent()

        # The trace function measures each run of a greenlet ..
        self._switched_at = perf_counter()
        self._previous_trace = settrace(self._on_switch)

        # .. a thread of the operating system captures the stack of a run while it blocks the loop ..
        self._is_stack_thread_running = True
        _ = _start_native_thread(self._capture_stacks, ())

        # .. and the greenlets measure the lag, the switch rate and the live greenlets.
        lag_worker = spawn(self._measure_lag)
        sample_worker = spawn(self._sample)

        self._workers.append(lag_worker)
        self._workers.append(sample_worker)

        self.is_started = True

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the measuring greenlets and the stack thread, and removes the trace function.
        """
        for worker in self._workers:
            worker.kill()

        self._is_stack_thread_running = False
        _ = settrace(self._previous_trace)

        self.is_started = False

# ################################################################################################################################

    def _on_switch(self, event:'str', args:'any_') -> 'None':
        """ Runs on each switch of the main thread, with the target as the current greenlet.
        """
        now = perf_counter()
        self.switch_count += 1

        if event in _switch_events:
            origin, target = args
            ran_for = now - self._switched_at

            # The hub runs while it waits for I/O, so only the other greenlets can block the loop.
            if ran_for > self.max_blocking_time:
                if origin is not self._hub:
                    self._add_blocking(origin, ran_for)

            self._greenlets.add(target)
            self._active = target
            self._switched_at = now

        if self._previous_trace is not None:
            self._previous_trace(event, args)

# ################################################################################################################################

    def _add_blocking(self, origin:'any_', ran_for:'float') -> 'None':
        """ Records one run that blocked the loop, with the stack the stack thread captured during it,
        or with the stack the greenlet yielded at.
        """
        if self._captured_run == self._switched_at:
            stack = self._captured_stack

        elif frame := origin.gr_frame:
            frames = format_stack(frame)
            stack = ''.join(frames)

        else:
            stack = _no_stack

        blocking = Blocking()
        blocking.greenlet = repr(origin)
        blocking.duration = ran_for
        blocking.stack = stack

        self.blockings.append(blocking)

# ################################################################################################################################

    def _capture_stacks(self) -> 'None':
        """ Runs in a thread of the operating system and captures, once per run, the stack of the main thread
        while a greenlet other than the hub runs for longer than the limit.
        """
        while self._is_stack_thread_running:
            _native_sleep(Stack_Check_Interval)

            run_started_at = self._switched_at
            ran_for = perf_counter() - run_started_at

            if ran_for > self.max_blocking_time:
                if self._active is not self._hub:
                    if self._captured_run != run_started_at:
                        frames = sys._current_frames()
                        frame = frames[self._hub.thread_ident]
                        stack = format_stack(frame)

                        # The stack is stored before its run, so that no run is paired with another stack.
                        self._captured_stack = ''.join(stack)
                        self._captured_run = run_started_at

# ################################################################################################################################

    def _measure_lag(self) -> 'None':
        """ Sleeps for the lag interval in a loop and records how late each wake-up is,
        except for a sleep that began before the current window.
        """
        while True:
            started_at = perf_counter()
            expected = started_at + Lag_Interval
            sleep(Lag_Interval)

            late_by = perf_counter() - expected
            lag = max(late_by, 0.0)

            if started_at >= self._window_started_at:
                self.lags.append(lag)

# ################################################################################################################################

    def _sample(self) -> 'None':
        """ Records the switches per second and the number of live greenlets once per sample interval,
        except for an interval that began before the current window.
        """
        last_count = self.switch_count
        last_at = perf_counter()

        while True:
            sleep(Sample_Interval)

            now = perf_counter()
            count = self.switch_count
            elapsed = now - last_at

            if last_at >= self._window_started_at:
                rate = (count - last_count) / elapsed
                live = self._count_live()

                self.switch_rates.append(rate)
                self.greenlet_counts.append(live)

            last_count = count
            last_at = now

# ################################################################################################################################

    def _count_live(self) -> 'int':
        out = 0

        for item in self._greenlets:
            if not item.dead:
                out += 1

        return out

# ################################################################################################################################

    def begin(self) -> 'None':
        """ Begins a measurement window - the current greenlet yields, so that its run starts anew,
        and everything measured so far is discarded.
        """
        sleep(0)

        self._window_started_at = perf_counter()

        self.blockings = []
        self.lags = []
        self.switch_rates = []
        self.greenlet_counts = []

# ################################################################################################################################

    def end(self) -> 'MonitorSummary':
        """ Ends a measurement window - the current greenlet yields, so that its run is measured too,
        and returns what was measured since the window began.
        """
        sleep(0)

        out = MonitorSummary()
        out.blockings = self.blockings

        out.max_blocking = 0.0

        for blocking in self.blockings:
            out.max_blocking = max(out.max_blocking, blocking.duration)

        out.lag_p50 = percentile(self.lags, 0.5)
        out.lag_p99 = percentile(self.lags, 0.99)
        out.lag_max = percentile(self.lags, 1.0)

        if self.switch_rates:
            out.switches_per_second = sum(self.switch_rates) / len(self.switch_rates)
        else:
            out.switches_per_second = 0.0

        if self.greenlet_counts:
            out.greenlets_max = max(self.greenlet_counts)
        else:
            out.greenlets_max = 0

        return out

# ################################################################################################################################
# ################################################################################################################################

def format_blockings(blockings:'blocking_list', max_blocking_time:'float') -> 'str':
    """ Describes each blocking of the event loop with the stack of its greenlet.
    """
    count = len(blockings)
    noun = 'time' if count == 1 else 'times'
    limit_ms = max_blocking_time * 1000

    lines:'anylist' = []
    lines.append(f'The event loop was blocked {count} {noun} for longer than {limit_ms:.0f} ms')

    for blocking in blockings:
        duration_ms = blocking.duration * 1000
        lines.append('')
        lines.append(f'{blocking.greenlet} blocked the event loop for {duration_ms:.0f} ms at')
        lines.append(blocking.stack)

    out = '\n'.join(lines)
    return out

# ################################################################################################################################
# ################################################################################################################################

# The monitor of this process, started by the first test that runs under it.
_monitor = EventLoopMonitor()

def get_monitor() -> 'EventLoopMonitor':
    """ Returns the monitor of this process, started.
    """
    if not _monitor.is_started:
        _monitor.start()

    return _monitor

# ################################################################################################################################

@hookimpl(wrapper=True, trylast=True)
def pytest_pyfunc_call(pyfuncitem:'Function') -> 'any_':
    """ Runs each test function in a measurement window and fails the test if a greenlet blocked the event loop
    for longer than the limit. The wrapper is the innermost one, so that the wrappers of other plugins
    are outside of the window.
    """
    monitor = get_monitor()
    monitor.begin()

    out = yield

    summary = monitor.end()

    if summary.blockings:
        report = format_blockings(summary.blockings, monitor.max_blocking_time)
        fail(report, pytrace=False)

    return out

# ################################################################################################################################
# ################################################################################################################################
