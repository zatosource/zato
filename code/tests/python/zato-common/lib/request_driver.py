# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import subprocess
import time
from dataclasses import dataclass

# psutil
import psutil

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The Go programs of the tests, each in a directory of its own
    Go_Dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'go'))

    # The program that sends one fixed request over keep-alive connections for a fixed duration
    Load_Client = 'load-client'

    # The HTTP endpoint that outgoing connections invoke
    Target_Server = 'rest-target-server'

    Host = '127.0.0.1'
    Microseconds = 1_000_000

    # How long each scenario runs before anything is measured, and how long it is measured for, in seconds
    Warm_Up_Seconds = 0.3
    Measure_Seconds = 1.2

    # How long the CPU time of a server is observed while it receives no requests, in seconds
    Idle_Seconds = 0.5

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Scenario:
    """ One request that the load client sends, with the status that every response to it is expected to have.
    """
    name: 'str'
    description: 'str'
    request: 'bytes'
    expected_status: 'int'
    connections: 'int'

# ################################################################################################################################
# ################################################################################################################################

def build_go_program(name:'str', output_dir:'str') -> 'str':
    """ Compiles one of the Go programs of the tests into the given directory and returns the path of the executable.
    """
    source_dir = os.path.join(ModuleCtx.Go_Dir, name)
    out = os.path.join(output_dir, name)

    _ = subprocess.run(['go', 'build', '-o', out, '.'], cwd=source_dir, check=True)

    return out

# ################################################################################################################################

def build_request(method:'str', path:'str', headers:'strdict', body:'bytes') -> 'bytes':
    """ Returns the raw bytes of a keep-alive HTTP/1.1 request.
    """
    lines = [f'{method} {path} HTTP/1.1', f'Host: {ModuleCtx.Host}', 'User-Agent: zato-tests/1.0']

    for name, value in headers.items():
        lines.append(f'{name}: {value}')

    if body:
        lines.append(f'Content-Length: {len(body)}')

    head = '\r\n'.join(lines) + '\r\n\r\n'

    out = head.encode('latin-1') + body
    return out

# ################################################################################################################################

def new_scenario(name:'str', description:'str', request:'bytes', expected_status:'int', connections:'int') -> 'Scenario':
    """ Returns a scenario with the request and the expected status given.
    """
    out = Scenario()
    out.name = name
    out.description = description
    out.request = request
    out.expected_status = expected_status
    out.connections = connections

    return out

# ################################################################################################################################
# ################################################################################################################################

def _run_load(load_client:'str', directory:'str', port:'int', scenario:'Scenario', seconds:'float') -> 'anydict':
    """ Runs the load client with the request of a scenario and returns its result.
    """
    request_path = os.path.join(directory, f'request-{scenario.name}.http')

    with open(request_path, 'wb') as request_file:
        _ = request_file.write(scenario.request)

    command = [
        load_client,
        '-address', f'{ModuleCtx.Host}:{port}',
        '-connections', str(scenario.connections),
        '-duration', f'{seconds}s',
        '-request', request_path,
    ]

    result = subprocess.run(command, capture_output=True, text=True, check=True)

    out:'anydict' = json.loads(result.stdout)
    return out

# ################################################################################################################################

def _check_statuses(scenario:'Scenario', load_result:'anydict') -> 'None':
    """ Raises an exception if any response of a run had a status other than the scenario expects.
    """
    expected = str(scenario.expected_status)

    for status in load_result['statuses']:
        if status != expected:
            raise Exception(f'Scenario {scenario.name} expected {expected}, received {load_result["statuses"]}')

# ################################################################################################################################

def _get_cpu_seconds(processes:'list[psutil.Process]') -> 'float':
    """ Returns the CPU time that the processes of a server have used so far.
    """
    out = 0.0

    for process in processes:
        times = process.cpu_times()
        out += times.user + times.system

    return out

# ################################################################################################################################

def measure_scenarios(
    load_client:'str',
    directory:'str',
    port:'int',
    scenarios:'list[Scenario]',
    processes:'list[psutil.Process]',
    settle_seconds:'float',
    ) -> 'anydict':
    """ Measures the CPU time of the processes of a server per request, and the requests per second, of each scenario.
    """

    # Every scenario runs once before anything is measured, so caches are filled and modules are imported ..
    for scenario in scenarios:
        load_result = _run_load(load_client, directory, port, scenario, ModuleCtx.Warm_Up_Seconds)
        _check_statuses(scenario, load_result)

    # .. the server finishes the imports it runs in the background after it starts ..
    time.sleep(settle_seconds)

    # .. the CPU time the server uses when it receives no requests is subtracted from each window ..
    idle_start = _get_cpu_seconds(processes)
    time.sleep(ModuleCtx.Idle_Seconds)
    idle_rate = (_get_cpu_seconds(processes) - idle_start) / ModuleCtx.Idle_Seconds

    results:'list[anydict]' = []

    # .. and each scenario is measured over a window of its own.
    for scenario in scenarios:

        _ = _run_load(load_client, directory, port, scenario, ModuleCtx.Warm_Up_Seconds)

        cpu_start = _get_cpu_seconds(processes)
        wall_start = time.monotonic()

        load_result = _run_load(load_client, directory, port, scenario, ModuleCtx.Measure_Seconds)

        wall_elapsed = time.monotonic() - wall_start
        cpu_elapsed = _get_cpu_seconds(processes) - cpu_start - (idle_rate * wall_elapsed)

        _check_statuses(scenario, load_result)

        requests = load_result['requests']

        results.append({
            'name': scenario.name,
            'description': scenario.description,
            'connections': scenario.connections,
            'requests': requests,
            'errors': load_result['errors'],
            'requests_per_second': requests / load_result['seconds'],
            'cpu_microseconds_per_request': cpu_elapsed / requests * ModuleCtx.Microseconds,
        })

    out:'anydict' = {
        'idle_cpu_rate': idle_rate,
        'scenarios': results,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
