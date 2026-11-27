# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Runs a suite of the Windows guests in shards, one pytest process per shard, each with guests of its own.
Usage: python -m live_windows.shards <pytest arguments>
"""

# stdlib
import os
import signal
import subprocess
import sys
from threading import Lock, Thread
from time import monotonic, sleep

# pytest
import pytest

# Zato
from live_windows.containers import discard_instance, prepare_guests
from live_windows.session import missing_guest_requirements
from live_windows.settings import Instance, Shards, Versions
from resume_first_failure import ModuleCtx as Resume_Ctx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The prefix of the name of the instance of the guests of each shard, followed by the index of the shard
    Instance_Prefix = 's'

    # How long an interrupted shard may take to remove its guests and end, in seconds
    Interrupt_Timeout = 30

    # How often the shards are checked, in seconds
    Poll_Interval = 0.2

    # The prefix of the lines of the driver itself
    Prefix = '[Shards]'

    # The exit codes of pytest that do not fail a shard - a shard whose tests all passed, and one without tests
    Success_Codes = pytest.ExitCode.OK, pytest.ExitCode.NO_TESTS_COLLECTED

# ################################################################################################################################
# ################################################################################################################################

_print_lock = Lock()

def _print(line:'str') -> 'None':
    with _print_lock:
        print(line, flush=True)

# ################################################################################################################################
# ################################################################################################################################

class _Shard:
    """ One pytest process, which runs the tests of its shard against guests of its own.
    """
    def __init__(self, index:'int', count:'int', pytest_arguments:'strlist') -> 'None':
        self.instance = f'{ModuleCtx.Instance_Prefix}{index}'
        self.prefix = f'[{self.instance}]'

        shard = f'{index}{Shards.Separator}{count}'

        # Each shard resumes on its own after a failed run of the goal, because all of them have the same arguments
        environment = dict(os.environ)
        environment[Shards.Variable] = shard
        environment[Resume_Ctx.Env_Identity] = shard
        environment[Instance.Variable] = self.instance
        environment['PYTHONUNBUFFERED'] = '1'

        command = [sys.executable, '-m', 'pytest', *pytest_arguments]

        # Each shard runs in a session of its own, so that an interrupt of the terminal reaches the driver only,
        # which then interrupts each shard and waits until it removed its guests
        self.start = monotonic()
        self.end = 0.0

        self.process = subprocess.Popen(
            command,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors='replace',
            start_new_session=True,
        )

        self.output_thread = Thread(target=self._print_output, daemon=True, name=f'shard-{self.instance}')
        self.output_thread.start()

    def _print_output(self) -> 'None':
        stdout = self.process.stdout
        if stdout:
            for line in stdout:
                line = line.rstrip()
                _print(f'{self.prefix} {line}')

    def poll(self) -> 'int | None':
        out = self.process.poll()

        if out is not None:
            if not self.end:
                self.end = monotonic()

        return out

    def interrupt(self) -> 'None':
        if self.poll() is None:
            self.process.send_signal(signal.SIGINT)

    def kill(self) -> 'None':
        if self.poll() is None:
            self.process.kill()

# ################################################################################################################################
# ################################################################################################################################

def _shard_count() -> 'int':

    if value := os.environ.get(Shards.Count_Variable):
        out = int(value)
    else:
        out = Shards.Default_Count

    version_count = len(Versions.All)

    if out % version_count:
        raise Exception(f'{Shards.Count_Variable}={out} is not a multiple of the number of versions {version_count}')

    return out

# ################################################################################################################################

def _wait_for_all(shards:'list[_Shard]') -> 'int':
    """ Waits until every shard ends, a failed one included, and returns the exit code of the first one that failed, or 0.
    """
    out = 0
    reported:'set[str]' = set()

    while True:

        running = 0

        for shard in shards:

            code = shard.poll()

            if code is None:
                running += 1

            elif code not in ModuleCtx.Success_Codes:
                if shard.instance not in reported:
                    reported.add(shard.instance)
                    _print(f'{ModuleCtx.Prefix} {shard.prefix} failed with exit code {code}, the other shards continue')
                    if not out:
                        out = code

        if not running:
            return out

        sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

def _stop(shards:'list[_Shard]') -> 'None':
    """ Interrupts each shard that still runs, so that it removes its guests, and kills those that do not end in time,
    removing their guests on their behalf.
    """
    for shard in shards:
        shard.interrupt()

    deadline = monotonic() + ModuleCtx.Interrupt_Timeout

    for shard in shards:
        while shard.poll() is None:
            if monotonic() > deadline:
                _print(f'{ModuleCtx.Prefix} {shard.prefix} did not end within {ModuleCtx.Interrupt_Timeout}s, killing it')
                shard.kill()
                _ = shard.process.wait()
                discard_instance(shard.instance)
                break
            sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

def run(pytest_arguments:'strlist') -> 'int':
    """ Runs every shard and returns the exit code of the first one that failed, or 0 if none did.
    """
    count = _shard_count()
    versions = list(Versions.All)

    # The ready states are saved once, before the shards start, because every shard resumes its guests from them.
    # Without what the guests require, the shards themselves report what is missing.
    if not missing_guest_requirements(versions):
        prepare_guests(versions)

    _print(f'{ModuleCtx.Prefix} Starting {count} shards')

    shards:'list[_Shard]' = []

    try:
        for index in range(count):
            shard = _Shard(index, count, pytest_arguments)
            shards.append(shard)

        out = _wait_for_all(shards)

    except KeyboardInterrupt:
        _print(f'{ModuleCtx.Prefix} Interrupted, stopping the shards')
        out = pytest.ExitCode.INTERRUPTED

    finally:
        _stop(shards)

        for shard in shards:
            shard.output_thread.join()

    for shard in shards:
        elapsed = shard.end - shard.start
        _print(f'{ModuleCtx.Prefix} {shard.prefix} exit code {shard.process.returncode} after {elapsed:.1f}s')

    return out

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    exit_code = run(sys.argv[1:])
    sys.exit(exit_code)

# ################################################################################################################################
# ################################################################################################################################
