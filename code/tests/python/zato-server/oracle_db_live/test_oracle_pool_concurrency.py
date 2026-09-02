# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import subprocess
import sys

# Zato
from conftest import get_license_key_env

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sql.containers import DatabaseServer
    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

# The child script that runs the workload under gevent
_workload_script = os.path.join(os.path.dirname(__file__), '_pool_workload.py')

# How long the child process may run before it counts as hung
_child_timeout = 120

# What the child's report must show
_pool_size            = 25
_min_query_count      = 5000
_max_heartbeat_gap_ms = 500

# ################################################################################################################################
# ################################################################################################################################

def test_concurrent_queries_from_greenlets(oracle_server:'DatabaseServer') -> 'None':
    """ Concurrent queries from greenlets on a pool holding well over a dozen
    connections run to completion with the process alive afterwards.
    """
    child_env = get_license_key_env()

    command = [sys.executable, _workload_script, json.dumps(oracle_server.details)]

    result = subprocess.run(command, capture_output=True, text=True, timeout=_child_timeout, env=child_env)

    # A child that died below Python leaves its trace in stderr and nowhere else,
    # which is why the whole output goes into the failure message.
    failure_details = f'exit code: {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}'

    assert result.returncode == 0, failure_details

    # The report is the last non-empty line of the child's output
    output_lines = []

    for line in result.stdout.splitlines():
        if line.strip():
            output_lines.append(line)

    report = json.loads(output_lines[-1])

    # No worker raised ..
    assert report['errors'] == [], failure_details

    # .. the driver never left thin mode ..
    assert report['is_thin_mode'] is True, failure_details

    # .. the pool really handed out all of its connections at once ..
    assert report['distinct_session_count'] >= _pool_size, failure_details

    # .. no call froze the event loop ..
    assert report['max_heartbeat_gap_ms'] < _max_heartbeat_gap_ms, failure_details

    # .. every connection went back to the pool ..
    assert report['checked_out'] == 0, failure_details
    assert report['checked_in'] == _pool_size, failure_details

    # .. and the run did real work rather than quietly doing almost nothing.
    assert report['query_count'] >= _min_query_count, failure_details

# ################################################################################################################################
# ################################################################################################################################
