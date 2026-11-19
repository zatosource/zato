# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re
from threading import Event, Lock, Thread
from time import monotonic, sleep

# Zato
from live_windows.docker_ import container_is_running

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_windows.session import GuestHandle
    from zato.common.typing_ import anydict, callable_, dictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long one test may take, in seconds
    Test_Timeout = 60

    # How often the control share of each guest and the server log are read, in seconds
    Poll_Interval = 0.2

    # How often the progress of a test is reported, and how often each container and agent is checked, in seconds
    Report_Every = 1

    # A heartbeat that has not changed for this long means that the agent stopped working, in seconds
    Heartbeat_Stale_After = 3

    # A guest whose control share could not be read for this long is not responding, in seconds
    Unresponsive_After = 5

    # How long the threads of a monitor may take to end, in seconds
    Join_Timeout = 10

    # What marks an error in the server log
    Error_Marker = ' - ERROR - '

    # Each entry of a server log begins with the date on which it was written
    Entry_Start = re.compile(r'\d{4}-\d{2}-\d{2}')

    # The Windows event levels that fail a test - critical and error
    Failure_Levels = 1, 2

    # The Windows logs whose every event fails a test - the logon failures
    Failure_Logs = 'Security',

    # How long a test that provokes Windows events is still watched after it ends, so that the events it provoked last,
    # which the agent forwards once a second, are matched against its own expectations and not against the next test's,
    # in seconds
    Windows_Events_Drain = 3

    # The drain also lasts until no expected Windows event has arrived for this long, because a guest that logs many events
    # forwards them with a delay, but never longer than the second value, in seconds
    Windows_Events_Quiet     = 2
    Windows_Events_Drain_Max = 20

    # How often the drain checks whether the expected Windows events stopped arriving, in seconds
    Windows_Events_Drain_Poll = 0.2

    # The kinds of agent events whose number is reported
    Counted_Kinds = 'produced', 'consumed', 'appeared', 'disappeared', 'marked-failed'

    # The server log lines that every environment without these components produces
    Server_Log_Noise = (
        'check_latest_version',
        'Could not determine version',
        'on-prem gateway hub',
        'listener loop exception',
        'queue bridge recv listener',
    )

# ################################################################################################################################
# ################################################################################################################################

class TestFailure(Exception):
    """ Raised when anything goes wrong in a guest, in its agent, in its container or in the server,
    and when a test does not reach what it waits for within its time.
    """

# ################################################################################################################################
# ################################################################################################################################

class _GuestWatch:
    """ What a monitor knows about one guest.
    """
    def __init__(self, handle:'GuestHandle') -> 'None':
        self.handle = handle
        self.events:'dictlist' = []

        self.counts:'anydict' = {}
        for kind in ModuleCtx.Counted_Kinds:
            self.counts[kind] = 0

        now = monotonic()

        self.last_poll = now
        self.last_check = now
        self.heartbeat_seq = -1
        self.heartbeat_changed = now

        # An outage of the guest is expected while it is suspended, and its container may stop once it is allowed to
        self.is_suspended = False
        self.may_stop = False
        self.is_reported_unresponsive = False

# ################################################################################################################################
# ################################################################################################################################

class Monitor:
    """ Watches the guests and the server for the duration of one test. It reports the progress every second,
    and fails the test at the first agent error, Windows error, stopped container, stale heartbeat or server error,
    and once the time of the test is up.
    """
    def __init__(self, name:'str', handles:'list[GuestHandle]', server_log_path:'str') -> 'None':
        self.name = name
        self.server_log_path = server_log_path
        self.server_log_offset = 0
        self.server_log_partial = ''

        self.watches:'dict[str, _GuestWatch]' = {}
        for handle in handles:
            self.watches[handle.version] = _GuestWatch(handle)

        self.expected_server_errors:'strlist' = list(ModuleCtx.Server_Log_Noise)
        self.expected_windows_events:'strlist' = []

        # When the most recent expected Windows event arrived, on the monotonic clock
        self.last_expected_event_at = 0.0

        self.failures:'strlist' = []
        self.raised_count = 0

        self.lock = Lock()
        self.stopping = Event()
        self.threads:'list[Thread]' = []
        self.start_time = 0.0

# ################################################################################################################################

    def start(self) -> 'None':
        self.start_time = monotonic()

        # The server log lines of earlier tests are not this test's concern
        self.server_log_offset = os.path.getsize(self.server_log_path)

        for watch in self.watches.values():
            thread = Thread(target=self._watch_guest, args=(watch,), daemon=True, name=f'monitor-win{watch.handle.version}')
            self.threads.append(thread)

        server_thread = Thread(target=self._watch_server, daemon=True, name='monitor-server')
        self.threads.append(server_thread)

        for thread in self.threads:
            thread.start()

        print(f'[SMB {self.name}] Watching {len(self.watches)} guests and the server', flush=True)

# ################################################################################################################################

    def _drain_windows_events(self) -> 'None':
        """ Keeps watching after the test ends, for at least the drain period and until the expected Windows events
        stop arriving, but never longer than the longest drain.
        """
        drain_start = monotonic()

        while True:

            now = monotonic()
            drained_for = now - drain_start
            quiet_for = now - self.last_expected_event_at

            if drained_for >= ModuleCtx.Windows_Events_Drain_Max:
                return

            if drained_for >= ModuleCtx.Windows_Events_Drain and quiet_for >= ModuleCtx.Windows_Events_Quiet:
                return

            sleep(ModuleCtx.Windows_Events_Drain_Poll)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Ends the watch, reads what the guests and the server reported last, and fails on what was not raised yet.
        """
        elapsed = self.elapsed()

        if elapsed > ModuleCtx.Test_Timeout:
            self._fail(f'The test took {elapsed:.1f}s, more than the limit of {ModuleCtx.Test_Timeout}s')

        if self.expected_windows_events:
            self._drain_windows_events()

        self.stopping.set()

        for thread in self.threads:
            thread.join(ModuleCtx.Join_Timeout)

        self._poll_server()
        self._report()

        self.raise_if_failed()

# ################################################################################################################################

    def elapsed(self) -> 'float':
        out = monotonic() - self.start_time
        return out

# ################################################################################################################################

    def _fail(self, message:'str') -> 'None':
        with self.lock:
            self.failures.append(message)

        print(f'[SMB {self.name}] Failure -> {message}', flush=True)

# ################################################################################################################################

    def raise_if_failed(self) -> 'None':
        """ Raises the failures that were not raised yet.
        """
        with self.lock:
            failures = self.failures[self.raised_count:]
            self.raised_count = len(self.failures)

        if failures:
            text = '\n'.join(failures)
            raise TestFailure(text)

# ################################################################################################################################
# ################################################################################################################################

    def expect_server_errors(self, *patterns:'str') -> 'None':
        """ Declares server log errors that the test provokes on purpose.
        """
        self.expected_server_errors.extend(patterns)

    def expect_windows_events(self, *patterns:'str') -> 'None':
        """ Declares Windows events that the test provokes on purpose, matched against their log, provider, ID and message.
        """
        self.expected_windows_events.extend(patterns)

    def suspend(self, version:'str') -> 'None':
        """ Declares that a guest is about to be unreachable, which is not a failure until it is resumed.
        """
        self.watches[version].is_suspended = True

    def resume(self, version:'str') -> 'None':
        watch = self.watches[version]
        watch.heartbeat_changed = monotonic()
        watch.last_poll = monotonic()
        watch.is_reported_unresponsive = False
        watch.is_suspended = False

    def allow_stop(self, version:'str') -> 'None':
        """ Declares that the container of a guest is about to stop, which is not a failure.
        """
        watch = self.watches[version]
        watch.may_stop = True
        watch.is_suspended = True

# ################################################################################################################################
# ################################################################################################################################

    def events(self, version:'str', kind:'str', run:'str') -> 'dictlist':
        """ Returns the events of one kind and one run that a guest reported so far.
        """
        out:'dictlist' = []
        watch = self.watches[version]

        with self.lock:
            for event in watch.events:
                if event['kind'] == kind:
                    if event['run'] == run:
                        out.append(event)

        return out

    def names(self, version:'str', kind:'str', run:'str') -> 'strlist':
        """ Returns the names of the files in the events of one kind and one run.
        """
        out:'strlist' = []

        for event in self.events(version, kind, run):
            out.append(event['name'])

        return out

    def paths(self, version:'str', kind:'str', run:'str') -> 'strlist':
        """ Returns the paths of the files that an observer reported as appeared or disappeared.
        """
        out:'strlist' = []

        for event in self.events(version, kind, run):
            out.append(event['path'])

        return out

    def has_event(self, version:'str', kind:'str', run:'str') -> 'bool':
        events = self.events(version, kind, run)

        out = len(events) > 0
        return out

# ################################################################################################################################
# ################################################################################################################################

    def wait_until(self, condition:'callable_', what:'str') -> 'None':
        """ Waits until the condition holds, raising at once on a failure and when the time of the test is up.
        """
        while True:

            self.raise_if_failed()

            if condition():
                print(f'[SMB {self.name} {self.elapsed():5.1f}s] Reached -> {what}', flush=True)
                return

            elapsed = self.elapsed()

            if elapsed > ModuleCtx.Test_Timeout:
                raise TestFailure(f'Not reached within the limit of {ModuleCtx.Test_Timeout}s -> {what}')

            sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

    def pause(self, seconds:'float') -> 'None':
        """ Lets the given time pass, raising at once on a failure.
        """
        until = monotonic() + seconds

        while monotonic() < until:
            self.raise_if_failed()
            sleep(ModuleCtx.Poll_Interval)

        self.raise_if_failed()

# ################################################################################################################################
# ################################################################################################################################

    def _watch_guest(self, watch:'_GuestWatch') -> 'None':
        while not self.stopping.is_set():
            self._poll_guest(watch)
            sleep(ModuleCtx.Poll_Interval)

        # The events that arrived while the test was finishing count too
        self._poll_guest(watch)

# ################################################################################################################################

    def _poll_guest(self, watch:'_GuestWatch') -> 'None':
        handle = watch.handle
        now = monotonic()

        # The control share is read in each poll, and the agent and the container are checked once in a while ..
        should_check = now - watch.last_check >= ModuleCtx.Report_Every

        try:
            events = handle.reader.read_events()

            if should_check:
                watch.last_check = now
                self._check_agent(watch)

        # .. a guest that is expected to be unreachable gets a new connection on the next attempt ..
        except Exception as e:
            if watch.is_suspended:
                handle.reader.client.close()
                return

            self._fail(f'{handle.prefix} The control share could not be read -> {e.__class__.__name__}: {e}')
            return

        watch.last_poll = monotonic()

        for event in events:
            self._handle_event(watch, event)

        if should_check:
            self._check_container(watch)

# ################################################################################################################################

    def _check_agent(self, watch:'_GuestWatch') -> 'None':
        """ Fails when the agent stopped or when its heartbeat stopped changing.
        """
        handle = watch.handle

        if agent_error := handle.reader.read_agent_error():
            self._fail(f'{handle.prefix} The agent stopped -> {agent_error}')
            return

        heartbeat = handle.reader.read_heartbeat()
        now = monotonic()

        if heartbeat['seq'] != watch.heartbeat_seq:
            watch.heartbeat_seq = heartbeat['seq']
            watch.heartbeat_changed = now
            return

        if watch.is_suspended:
            return

        stale_for = now - watch.heartbeat_changed

        if stale_for > ModuleCtx.Heartbeat_Stale_After:
            self._fail(f'{handle.prefix} The heartbeat of the agent has not changed for {stale_for:.1f}s')

# ################################################################################################################################

    def _check_container(self, watch:'_GuestWatch') -> 'None':
        if watch.may_stop:
            return

        handle = watch.handle

        if not container_is_running(handle.info.name):
            self._fail(f'{handle.prefix} Container {handle.info.name} stopped')

# ################################################################################################################################

    def _handle_event(self, watch:'_GuestWatch', event:'anydict') -> 'None':
        kind = event['kind']

        with self.lock:
            watch.events.append(event)
            if kind in watch.counts:
                watch.counts[kind] += 1

        if kind == 'error':
            self._fail(f'{watch.handle.prefix} Agent error -> {event}')

        elif kind == 'windows-event':
            self._handle_windows_event(watch, event)

# ################################################################################################################################

    def _handle_windows_event(self, watch:'_GuestWatch', event:'anydict') -> 'None':
        """ Fails on an error, a critical event or a logon failure, unless the test declared it, and reports the warnings.
        """
        prefix = watch.handle.prefix
        text = f'{event["log"]} {event["provider"]} {event["event_id"]} {event["message"]}'

        for pattern in self.expected_windows_events:
            if pattern in text:
                self.last_expected_event_at = monotonic()
                print(f'[SMB {self.name}] {prefix} Expected Windows event -> {text}', flush=True)
                return

        is_failure = event['level'] in ModuleCtx.Failure_Levels

        if event['log'] in ModuleCtx.Failure_Logs:
            is_failure = True

        if is_failure:
            self._fail(f'{prefix} Windows event, level {event["level"]} -> {text}')
        else:
            print(f'[SMB {self.name}] {prefix} Windows warning -> {text}', flush=True)

# ################################################################################################################################
# ################################################################################################################################

    def _watch_server(self) -> 'None':
        while not self.stopping.wait(ModuleCtx.Report_Every):
            self._poll_server()
            self._check_responsive()
            self._report()

# ################################################################################################################################

    def _poll_server(self) -> 'None':
        """ Fails on each error line that the server logged since the previous call, unless the test declared it.
        """
        with open(self.server_log_path, 'r', encoding='utf8', errors='replace') as log_file:
            _ = log_file.seek(self.server_log_offset)
            text = log_file.read()
            self.server_log_offset = log_file.tell()

        text = self.server_log_partial + text
        lines = text.split('\n')

        # The last element is either empty or a line without its end yet
        self.server_log_partial = lines.pop()

        # A line that does not begin with a timestamp continues the entry before it, e.g. as a line of a traceback
        entries:'list[strlist]' = []

        for line in lines:
            if entries and not ModuleCtx.Entry_Start.match(line):
                entries[-1].append(line)
            else:
                entries.append([line])

        for entry in entries:

            first_line = entry[0]

            if ModuleCtx.Error_Marker not in first_line:
                continue

            is_expected = False

            for pattern in self.expected_server_errors:
                if pattern in first_line:
                    is_expected = True
                    break

            if is_expected:
                print(f'[SMB {self.name}] Expected server error -> {first_line}', flush=True)
            else:
                text = '\n'.join(entry)
                self._fail(f'Server error -> {text}')

# ################################################################################################################################

    def _check_responsive(self) -> 'None':
        """ Fails when the control share of a guest has not been read for too long, e.g. because a read hangs.
        """
        now = monotonic()

        for watch in self.watches.values():

            if watch.is_suspended:
                continue

            if watch.is_reported_unresponsive:
                continue

            silent_for = now - watch.last_poll

            if silent_for > ModuleCtx.Unresponsive_After:
                watch.is_reported_unresponsive = True
                self._fail(f'{watch.handle.prefix} The guest has not responded for {silent_for:.1f}s')

# ################################################################################################################################

    def _report(self) -> 'None':
        parts:'strlist' = []

        with self.lock:
            for watch in self.watches.values():

                counts:'strlist' = []

                for kind, count in watch.counts.items():
                    if count:
                        counts.append(f'{kind} {count}')

                if not counts:
                    continue

                counts_text = ', '.join(counts)
                parts.append(f'{watch.handle.prefix} {counts_text}')

            failure_count = len(self.failures)

        if not parts:
            parts.append('no files yet')

        text = ' | '.join(parts)
        print(f'[SMB {self.name} {self.elapsed():5.1f}s] {text} | failures {failure_count}', flush=True)

# ################################################################################################################################
# ################################################################################################################################
