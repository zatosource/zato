# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The measurement of the throughput and the latencies of one channel under a closed-loop load,
# which the processes of _load.py apply from the CPUs of the load generator.

# stdlib
import json
import logging
import os
import subprocess
import sys
import tempfile
from array import array
from dataclasses import dataclass
from time import time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intlist, list_

    popenlist = list_['subprocess.Popen[str]']

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_perf.measure')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Load_Script = os.path.join(os.path.dirname(__file__), '_load.py')

    # How long the processes of the load generator are given to start, how long the load runs before the window
    # in which it is measured, and how long the window lasts, in seconds
    Start_Delay = 2.0
    Warmup_Seconds = 5.0
    Window_Seconds = 15.0

    # How long a process of the load generator may run beyond the end of the window, in seconds
    Exit_Timeout = 60.0

    # The type code of the latencies that the processes write, signed 64-bit nanoseconds
    Latency_Type = 'q'

    Nanoseconds_Per_Millisecond = 1_000_000

    P50 = 0.50
    P99 = 0.99

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Measurement:

    # Responses per second within the window
    throughput: 'float'

    # The 50th and the 99th percentile latencies, in milliseconds
    p50_ms: 'float'
    p99_ms: 'float'

    # The responses in the window whose status was not 200
    errors: 'int'

    # The connections that the server closed and the generator opened again
    reconnects: 'int'

# ################################################################################################################################
# ################################################################################################################################

def _percentile(latencies:'array', fraction:'float') -> 'float':
    """ Returns the latency at a fraction of the sorted latencies, in milliseconds.
    """
    index = int(len(latencies) * fraction)
    out = latencies[index] / ModuleCtx.Nanoseconds_Per_Millisecond
    return out

# ################################################################################################################################

def _split(total:'int', parts:'int') -> 'intlist':
    """ Divides a number of connections among processes as evenly as possible.
    """
    out:'intlist' = []

    for index in range(parts):
        share = total // parts
        if index < total % parts:
            share += 1
        out.append(share)

    return out

# ################################################################################################################################

def measure(port:'int', path:'str', connection_count:'int', load_cpus:'intlist') -> 'Measurement':
    """ Applies a closed-loop load of a number of connections to a channel of the server and measures it.
    """
    request = f'POST {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nContent-Type: application/json\r\n' + \
        'Content-Length: 2\r\n\r\n{}'

    process_count = min(len(load_cpus), connection_count)
    shares = _split(connection_count, process_count)

    window_start = time() + ModuleCtx.Start_Delay + ModuleCtx.Warmup_Seconds
    window_end = window_start + ModuleCtx.Window_Seconds

    latency_directory = tempfile.mkdtemp(prefix='zato_multi_cpu_perf_latencies_')
    latency_paths:'list_[str]' = []
    processes:'popenlist' = []

    for index in range(process_count):
        latency_path = os.path.join(latency_directory, f'{index}.bin')
        latency_paths.append(latency_path)

        config = {
            'host': '127.0.0.1',
            'port': port,
            'request': request,
            'connections': shares[index],
            'cpu': load_cpus[index],
            'window_start': window_start,
            'window_end': window_end,
            'latency_path': latency_path,
        }

        process = subprocess.Popen([sys.executable, ModuleCtx.Load_Script, json.dumps(config)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        processes.append(process)

    latencies = array(ModuleCtx.Latency_Type)

    out = Measurement()
    out.errors = 0
    out.reconnects = 0

    for index, process in enumerate(processes):
        stdout, stderr = process.communicate(timeout=ModuleCtx.Start_Delay + ModuleCtx.Warmup_Seconds +
            ModuleCtx.Window_Seconds + ModuleCtx.Exit_Timeout)

        if process.returncode != 0:
            raise Exception(f'Load process {index} exited with {process.returncode} -> {stderr}')

        counts = json.loads(stdout)
        out.errors += counts['errors']
        out.reconnects += counts['reconnects']

        with open(latency_paths[index], 'rb') as latency_file:
            latencies.frombytes(latency_file.read())

        os.remove(latency_paths[index])

    os.rmdir(latency_directory)

    if not latencies:
        raise Exception(f'No response of {path} within the window')

    sorted_latencies = array(ModuleCtx.Latency_Type, sorted(latencies))

    out.throughput = len(sorted_latencies) / ModuleCtx.Window_Seconds
    out.p50_ms = _percentile(sorted_latencies, ModuleCtx.P50)
    out.p99_ms = _percentile(sorted_latencies, ModuleCtx.P99)

    return out

# ################################################################################################################################
# ################################################################################################################################
