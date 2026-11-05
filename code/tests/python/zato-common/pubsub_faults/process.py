# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Runs the Zato server of one fault of a single process in a transient systemd scope of the user and applies
# the fault that the server requests, reading the outcome from the exit code of the server.

# stdlib
import os
import subprocess
import sys
import tempfile
from itertools import count
from subprocess import TimeoutExpired
from time import monotonic, time

# Zato
from expiration import Env_Clock_Anchor
from process_faults import Clock_No_Offset, Scope
from remote import FaultDriver, write_control_file
from runner import get_duration
from tools import build_faketime, build_fsfault

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from faults import Fault
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import strlist, strstrdict

    phase      = tuple[str, int]
    phase_list = list[phase]

# ################################################################################################################################
# ################################################################################################################################

_main_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'process_main.py')

# The variable of the duration of a fault and its default, in seconds.
_fault_seconds_env = 'Zato_Test_Fault_Seconds'
_default_fault_seconds = 120

# The phases of a run, which the server reads as well, in seconds.
_phases:'phase_list' = [
    ('Zato_Test_Fault_Baseline_Seconds', 60),
    (_fault_seconds_env, _default_fault_seconds),
    ('Zato_Test_Fault_Recovery_Seconds', 120),
    ('Zato_Test_Fault_Checked_Seconds', 120),
    ('Zato_Test_Fault_Drain_Seconds', 900),
]

# How long the server may run beyond its phases before it is ended, and how often it is waited for, in seconds.
_exit_margin_seconds = 600
_wait_seconds = 1

# How much of the end of the log of a failed server is reported.
_log_tail_chars = 6000

# How often libfaketime reads its timestamp file, in seconds.
_faketime_cache_seconds = '1'

_ms_per_second = 1000

# The numbers of the scopes of this test process.
_scope_numbers = count(1)

# ################################################################################################################################
# ################################################################################################################################

class ProcessEnvironment:
    """ The database of the faults of single processes - a SQLite file or a PostgreSQL container whose processes
    preload the library of the file system faults - and the control files of that library.
    """

    def __init__(self, work_dir:'str', database:'PubSubDatabase | None') -> 'None':
        self.work_dir = work_dir
        self.database = database

        # The control file and the prefix of the files of the server and its cleanup process ..
        self.server_control = os.path.join(work_dir, 'fsfault-server')
        self.server_prefix = work_dir

        # .. and those of PostgreSQL, as its container sees them.
        self.database_control = os.path.join(work_dir, 'fsfault-control', 'postgresql')
        self.database_prefix = '/var/lib/postgresql/data'

        self.timestamp_file = os.path.join(work_dir, 'faketime')

# ################################################################################################################################
# ################################################################################################################################

def get_run_seconds(fault:'Fault') -> 'float':
    """ How long the server runs its phases at most.
    """
    out = 0.0

    for name, default in _phases:
        out += get_duration(name, default)

    out += fault.min_duration
    return out

# ################################################################################################################################

def new_scope() -> 'Scope':
    number = next(_scope_numbers)
    pid = os.getpid()

    out = Scope(f'zato-pubsub-fault-{pid}-{number}')
    return out

# ################################################################################################################################

def _read_log_tail(log_path:'str') -> 'str':

    with open(log_path) as log_file:
        log = log_file.read()

    out = log[-_log_tail_chars:]
    return out

# ################################################################################################################################

def _get_server_env(environment:'ProcessEnvironment', probes_expiration:'bool') -> 'strstrdict':
    """ The environment of the server, whose processes preload both libraries, which change nothing
    until a fault is applied, after the libraries that this process preloads itself.
    """
    fsfault_path = build_fsfault()
    faketime_path = build_faketime()

    out:'strstrdict' = dict(os.environ)

    preload = f'{fsfault_path} {faketime_path}'

    if current_preload := os.environ.get('LD_PRELOAD', ''):
        preload = f'{current_preload} {preload}'

    out['LD_PRELOAD'] = preload
    out['ZATO_FSFAULT_CONTROL'] = environment.server_control
    out['FAKETIME_TIMESTAMP_FILE'] = environment.timestamp_file
    out['FAKETIME_CACHE_DURATION'] = _faketime_cache_seconds
    out['FAKETIME_DONT_FAKE_MONOTONIC'] = '1'

    # The true time, which the clock of this process keeps, and the monotonic time it was read at.
    if probes_expiration:
        now = time()
        anchor_ms = int(now * _ms_per_second)
        anchor_monotonic = monotonic()
        out[Env_Clock_Anchor] = f'{anchor_ms} {anchor_monotonic}'

    return out

# ################################################################################################################################

def run_process_fault(
    environment:'ProcessEnvironment',
    scope:'Scope',
    fault:'Fault',
    level:'int',
    label:'str',
    probes_expiration:'bool' = False,
    ) -> 'None':
    """ Runs the server in its scope through the phases of one fault, applying the fault on its request,
    and fails if the server reports a failure or does not end in time.
    """
    fault_seconds = get_duration(_fault_seconds_env, _default_fault_seconds)
    fault_seconds = max(fault_seconds, fault.min_duration)

    control_dir = tempfile.mkdtemp(prefix='control-', dir=environment.work_dir)
    log_path = os.path.join(environment.work_dir, f'{scope.unit}.log')

    # The clock of the server starts without an offset ..
    write_control_file(environment.timestamp_file, Clock_No_Offset)
    env = _get_server_env(environment, probes_expiration)

    # .. the server starts in its scope ..
    command:'strlist' = scope.get_command_prefix()
    command.extend([sys.executable, _main_path, label, fault.name, f'{level}', control_dir])

    driver = FaultDriver(fault, control_dir, fault_seconds)
    run_seconds = get_run_seconds(fault)
    timeout = run_seconds + _exit_margin_seconds

    with open(log_path, 'w') as log_file:
        process = subprocess.Popen(command, env=env, stdout=log_file, stderr=subprocess.STDOUT)

    driver.start()

    # .. and runs until it ends, with each step of the fault completed on its request.
    try:
        waited = 0.0

        while True:
            try:
                _ = process.wait(_wait_seconds)
                break
            except TimeoutExpired:
                driver.raise_failure()
                waited += _wait_seconds
                assert waited < timeout, f'{label} - the server did not end in {timeout}s\n{_read_log_tail(log_path)}'

    finally:
        driver.stop()
        scope.stop()

    assert process.returncode == 0, f'{label} - exit code {process.returncode}\n{_read_log_tail(log_path)}'

# ################################################################################################################################
# ################################################################################################################################
