# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from request_driver import build_request, measure_scenarios, new_scenario
from zato.common.test.perf_report import report_result, start_measurement

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from request_driver import Scenario
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the server is left to finish the imports that it runs in the background after it starts, in seconds
    Settle_Seconds = 30

    # A single client, which measures one invocation at a time, and the concurrent clients
    Sequential_Connections = 1
    Concurrent_Connections = 50

    Status_OK = 200

# ################################################################################################################################
# ################################################################################################################################

def _build_scenarios() -> 'list[Scenario]':
    """ Returns the scenarios in the order they run, each request of which invokes one outgoing connection once.
    """
    ok = ModuleCtx.Status_OK
    sequential = ModuleCtx.Sequential_Connections

    out = [
        new_scenario('get-plain', 'Outgoing GET without security',
            build_request('GET', '/test/perf/outgoing/plain', {}, b''), ok, sequential),
        new_scenario('get-basic-auth', 'Outgoing GET with Basic Auth',
            build_request('GET', '/test/perf/outgoing/basic', {}, b''), ok, sequential),
        new_scenario('get-new-connection', 'Outgoing GET with Basic Auth over a new connection each time',
            build_request('GET', '/test/perf/outgoing/new-connection', {}, b''), ok, sequential),
        new_scenario('get-basic-auth-concurrent', 'Outgoing GET with Basic Auth, 50 concurrent clients',
            build_request('GET', '/test/perf/outgoing/basic', {}, b''), ok, ModuleCtx.Concurrent_Connections),
    ]

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_rest_outgoing_cpu_per_invocation(
    zato_server:'anydict',
    zato_client:'AdminClient',
    load_client:'str',
    data_dir:'str',
    ) -> 'None':
    """ Each scenario of outgoing REST connections is answered with the status that the target endpoint returns,
    and its CPU time per invocation and invocations per second are recorded with the settings of the server.
    """
    measurement = start_measurement(zato_client, zato_server['database'])

    figures = measure_scenarios(
        load_client,
        data_dir,
        zato_server['port'],
        _build_scenarios(),
        zato_server['processes'],
        ModuleCtx.Settle_Seconds,
    )

    _ = report_result(measurement, 'rest-outgoing', figures)

# ################################################################################################################################
# ################################################################################################################################
