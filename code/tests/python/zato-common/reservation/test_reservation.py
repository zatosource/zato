# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import signal
import subprocess
import sys

# pytest
import pytest

# Zato
from zato.common.test.reservation import is_name_live, is_port_reserved, is_reserved_name, PortInUse, reserve_name, \
    start_on_reserved_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from subprocess import Popen
    from zato.common.typing_ import any_, intlist, list_, strlist

    popenlist = list_[Popen[str]]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many processes reserve ports at the same time, and how many ports each of them reserves
    Process_Count = 32
    Ports_Per_Process = 20

    # How long a process that holds a reservation may take to report it or to exit, in seconds
    Process_Timeout = 60

    # The purpose and the prefix of the reservations of the tests
    Purpose = 'reservation-test'
    Name_Prefix = 'zato-reservation-test'

    # The program of the processes that hold reservations
    Holder_Path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reservation_holder.py')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def reservation_dir(tmp_path:'any_', monkeypatch:'any_') -> 'str':
    """ A directory of lock files of the test alone, which the processes that the test starts inherit.
    """
    out = str(tmp_path / 'reservations')
    monkeypatch.setenv('Zato_Test_Reservation_Dir', out)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _start_holder(*arguments:'str') -> 'Popen[str]':
    """ Starts a process that holds reservations until its standard input is closed.
    """
    command = [sys.executable, ModuleCtx.Holder_Path, *arguments]

    out = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    return out

# ################################################################################################################################

def _read_report(process:'Popen[str]') -> 'any_':
    """ Returns what a holder reserved, as it reported it on its standard output.
    """
    stdout = process.stdout
    assert stdout is not None

    line = stdout.readline()

    out = json.loads(line)
    return out

# ################################################################################################################################

def _release_holder(process:'Popen[str]') -> 'None':
    """ Closes the standard input of a holder, which releases its reservations and ends it.
    """
    stdin = process.stdin
    assert stdin is not None

    stdin.close()

    exit_code = process.wait(ModuleCtx.Process_Timeout)
    assert exit_code == 0

# ################################################################################################################################
# ################################################################################################################################

def test_concurrent_processes_receive_distinct_ports() -> 'None':
    """ Processes that reserve ports at the same time never receive the same port.
    """
    port_count = f'{ModuleCtx.Ports_Per_Process}'

    processes:'popenlist' = []

    # Every process reserves its ports at the same time ..
    for _ in range(ModuleCtx.Process_Count):
        process = _start_holder('ports', port_count, ModuleCtx.Purpose)
        processes.append(process)

    # .. and holds them while the others report theirs ..
    ports:'intlist' = []

    for process in processes:
        process_ports = _read_report(process)
        ports.extend(process_ports)

    # .. after which all of them exit.
    for process in processes:
        _release_holder(process)

    expected_count = ModuleCtx.Process_Count * ModuleCtx.Ports_Per_Process
    distinct_ports = set(ports)

    assert len(ports) == expected_count
    assert len(distinct_ports) == expected_count

    for port in ports:
        assert not is_port_reserved(port)

# ################################################################################################################################

def test_port_of_killed_process_is_released() -> 'None':
    """ A port that a process killed with SIGKILL held becomes available to other processes.
    """
    process = _start_holder('ports', '1', ModuleCtx.Purpose)

    ports = _read_report(process)
    port = ports[0]

    assert is_port_reserved(port)

    process.kill()
    exit_code = process.wait(ModuleCtx.Process_Timeout)

    assert exit_code == -signal.SIGKILL
    assert not is_port_reserved(port)

# ################################################################################################################################

def test_name_of_live_process_is_live() -> 'None':
    """ A name that a process that runs holds is live, and it ceases to be once the process exits.
    """
    process = _start_holder('name', ModuleCtx.Name_Prefix)

    name = _read_report(process)

    assert is_reserved_name(name, ModuleCtx.Name_Prefix)
    assert is_name_live(name)

    _release_holder(process)

    assert not is_name_live(name)

    # A name of this process is live as well, and it is released with its reservation.
    with reserve_name(ModuleCtx.Name_Prefix) as reservation:
        assert is_name_live(reservation.name)

    assert not is_name_live(reservation.name)

# ################################################################################################################################

def test_start_is_retried_after_bind_failure() -> 'None':
    """ A start that could not bind its port is called again on another reserved port.
    """
    ports:'intlist' = []
    outcomes:'strlist' = ['Address already in use', 'Started']

    def start(port:'int') -> 'str':
        ports.append(port)
        outcome = outcomes.pop(0)

        if outcome != 'Started':
            raise PortInUse(outcome)

        out = f'Listening on {port}'
        return out

    started = start_on_reserved_port(ModuleCtx.Purpose, start)

    try:
        first_port, second_port = ports

        assert first_port != second_port
        assert started.reservation.port == second_port
        assert started.result == f'Listening on {second_port}'

        assert not is_port_reserved(first_port)
        assert is_port_reserved(second_port)

    finally:
        started.reservation.release()

    assert not is_port_reserved(second_port)

# ################################################################################################################################
# ################################################################################################################################
