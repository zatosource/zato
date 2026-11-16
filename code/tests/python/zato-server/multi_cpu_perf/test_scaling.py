# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
from http.client import HTTPConnection
from time import monotonic, sleep

# pytest
import pytest

# Zato
from zato.common.test.conftest_base_multi_cpu import enmasse_import

# Test helpers
from _measure import measure
from _server import get_cpu_layout, PerfServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from _measure import Measurement
    from _server import CPULayout
    from zato.common.typing_ import any_, anydict, dict_, intset

    measurementdict = dict_[int, Measurement]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_perf.scaling')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Worker_Counts = (1, 2, 4, 6, 8)

    # The fraction of N times the throughput of one worker that N workers reach at least, which the environment may set
    Target_Efficiency_Env = 'Zato_Test_Multi_CPU_Scaling_Target'
    Default_Target_Efficiency = 0.9

    # How many times the 99th percentile latency of one worker the latency of N workers reaches at most
    Latency_Factor = 1.5

    # The connections of the load generator for each worker, so that each worker always has requests waiting
    Connections_Per_Worker = 16

    Service_Name = 'test.multi-cpu.perf.cpu-bound'

    Path_Audit_Off = '/test/multi-cpu/perf/cpu-bound/audit-off'
    Path_Audit_On = '/test/multi-cpu/perf/cpu-bound/audit-on'

    # How long every worker may take to serve the channels after a start, and how often they are polled, in seconds
    Serve_Deadline = 60.0
    Poll_Interval = 0.1

    Status_OK = 200

# ################################################################################################################################
# ################################################################################################################################

def _get_target_efficiency() -> 'float':
    if ModuleCtx.Target_Efficiency_Env in os.environ:
        out = float(os.environ[ModuleCtx.Target_Efficiency_Env])
    else:
        out = ModuleCtx.Default_Target_Efficiency
    return out

# ################################################################################################################################

def _get_slot(port:'int', path:'str') -> 'int':
    """ Sends one request on a new connection and returns the slot of the worker that served it, or -1 on an error.
    """
    connection = HTTPConnection('127.0.0.1', port)

    try:
        connection.request('POST', path, body='{}', headers={'Content-Type': 'application/json'})
        response = connection.getresponse()
        body = response.read()
    except OSError:
        out = -1
    else:
        if response.status == ModuleCtx.Status_OK:
            out = json.loads(body)['slot']
        else:
            out = -1
    finally:
        connection.close()

    return out

# ################################################################################################################################

def _wait_until_served(port:'int', path:'str', worker_count:'int') -> 'None':
    """ Waits until the worker of every slot served a request of the channel.
    """
    served:'intset' = set()
    deadline = monotonic() + ModuleCtx.Serve_Deadline

    while len(served) < worker_count:
        if monotonic() > deadline:
            raise Exception(f'Channel {path} served by slots {sorted(served)} of {worker_count} after {ModuleCtx.Serve_Deadline}s')

        slot = _get_slot(port, path)
        if slot >= 0:
            served.add(slot)
        else:
            sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def perf_server() -> 'any_':
    """ The environment of the measurement, with the channels of the measurement imported through a server of one worker.
    """
    layout = get_cpu_layout()
    logger.info('Server CPUs %s, load generator CPUs %s', layout.server_cpus, layout.load_cpus)

    server = PerfServer()
    server.create()
    server.start(1, layout.server_cpus[:1])

    channels:'anydict' = {
        'channel_rest': [{
            'name': 'test.multi-cpu.perf.audit-off',
            'service': ModuleCtx.Service_Name,
            'url_path': ModuleCtx.Path_Audit_Off,
            'data_format': 'json',
            'is_audit_log_active': False,
        }, {
            'name': 'test.multi-cpu.perf.audit-on',
            'service': ModuleCtx.Service_Name,
            'url_path': ModuleCtx.Path_Audit_On,
            'data_format': 'json',
        }],
    }

    try:
        enmasse_import(channels)
        server.stop()
        yield server, layout
    finally:
        server.cleanup()

# ################################################################################################################################
# ################################################################################################################################

class TestScaling:
    """ N workers reach at least the target fraction of N times the throughput of one worker,
    with the 99th percentile latency within a factor of that of one worker.
    """

    def _run(self, perf_server:'any_', path:'str') -> 'None':
        server:'PerfServer'
        layout:'CPULayout'
        server, layout = perf_server

        results:'measurementdict' = {}

        for worker_count in ModuleCtx.Worker_Counts:
            server.start(worker_count, layout.server_cpus[:worker_count])

            try:
                _wait_until_served(server.port, path, worker_count)
                connection_count = worker_count * ModuleCtx.Connections_Per_Worker
                result = measure(server.port, path, connection_count, layout.load_cpus)
            finally:
                server.stop()

            results[worker_count] = result

            logger.info('%s workers=%s throughput=%.1f/s p50=%.2fms p99=%.2fms errors=%s reconnects=%s',
                path, worker_count, result.throughput, result.p50_ms, result.p99_ms, result.errors, result.reconnects)

        baseline = results[1]
        target = _get_target_efficiency()

        for worker_count, result in results.items():
            efficiency = result.throughput / (worker_count * baseline.throughput)
            latency_factor = result.p99_ms / baseline.p99_ms

            logger.info('%s workers=%s efficiency=%.3f latency_factor=%.2f', path, worker_count, efficiency, latency_factor)

        for worker_count, result in results.items():
            efficiency = result.throughput / (worker_count * baseline.throughput)
            latency_factor = result.p99_ms / baseline.p99_ms

            assert result.errors == 0, f'{worker_count} workers: {result.errors} errors'
            assert efficiency >= target, f'{worker_count} workers: efficiency {efficiency:.3f} below {target}'
            assert latency_factor <= ModuleCtx.Latency_Factor, \
                f'{worker_count} workers: p99 {result.p99_ms:.2f}ms is {latency_factor:.2f} times that of one worker'

# ################################################################################################################################

    def test_rest_audit_off(self, perf_server:'any_') -> 'None':
        self._run(perf_server, ModuleCtx.Path_Audit_Off)

# ################################################################################################################################

    def test_rest_audit_on_sqlite(self, perf_server:'any_') -> 'None':
        self._run(perf_server, ModuleCtx.Path_Audit_On)

# ################################################################################################################################
# ################################################################################################################################
