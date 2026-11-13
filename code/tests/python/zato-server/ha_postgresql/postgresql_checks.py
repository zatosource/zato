# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The checks of the PostgreSQL suites that read the database both nodes share - the generation and the owner
# of the active server, and the containers that stop once the database lost data.

# stdlib
import time

# Zato
from postgresql_env import read_server_generation
from workload import read_rows
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment
    from nodes import Node
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How often the database and the containers are read while a check waits for them, in seconds
    Poll_Interval = 0.1

    # What the log of a node contains once the database lost data
    Data_Loss_Text = 'the referee lost data'

# ################################################################################################################################
# ################################################################################################################################

def read_active_server(env:'HAEnvironment') -> 'tuple[int, str]':
    """ Returns the pub/sub generation and the owner of the active server as the database holds them.
    """
    rows = read_rows(cast_('any_', env), 'select generation, owner from pubsub_active')
    generation, owner = rows[0]

    out = (generation, owner)
    return out

# ################################################################################################################################

def wait_for_raised_generation(env:'HAEnvironment', generation:'int', timeout:'float') -> 'float':
    """ Waits until a server raised the pub/sub generation above the given one and returns the first time,
    in seconds since the epoch, at which the database was seen holding the higher one.
    """
    deadline = time.monotonic() + timeout

    while True:
        current, _ = read_active_server(env)

        if current > generation:
            out = time.time()
            return out

        assert time.monotonic() < deadline, f'Generation {generation} not raised after {timeout}s'
        time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

def check_active_server(env:'HAEnvironment', active:'Node') -> 'None':
    """ Checks that the database names the server of the active node as the one whose writes it accepts.
    """
    in_database = read_active_server(env)
    in_file = read_server_generation(active)

    assert in_database == in_file, f'Database names {in_database}, server of {active.node_name} has {in_file}'

# ################################################################################################################################

def wait_until_stopped(nodes:'list[Node]', timeout:'float') -> 'None':
    """ Waits until the containers of the given nodes stop, each with the error of a database that lost data.
    """
    deadline = time.monotonic() + timeout

    while True:
        running:'list[str]' = []

        for node in nodes:
            if node.is_running():
                running.append(node.node_name)

        if not running:
            break

        assert time.monotonic() < deadline, f'Still running after the database lost data -> {running}'
        time.sleep(ModuleCtx.Poll_Interval)

    for node in nodes:
        logs = node.read_logs()
        assert ModuleCtx.Data_Loss_Text in logs, f'{node.node_name} stopped without the error of a lost record'

# ################################################################################################################################
# ################################################################################################################################
