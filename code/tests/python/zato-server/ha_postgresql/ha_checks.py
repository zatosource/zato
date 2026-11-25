# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The checks that every run of the active-standby suites applies - no acknowledged publication lost, every repeated push
# in flight during a fault, no scheduler slot run twice and nothing originating from a replaced node.

# stdlib
import time

# Zato
from scheduler_checks import get_repeated_completed_slots, get_starts_after, get_state_mismatches, read_run_log
from scheduler_jobs import ModuleCtx as SchedulerJobsCtx
from workload import get_count_mismatches, get_repeats_not_in_flight, read_rows as read_database_rows, Topic_Name, \
    wait_for_deliveries
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment
    from nodes import Node
    from workload import Workload
    from zato.common.typing_ import any_, anydict, dictlist, strlist

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How often the roles of both nodes are read while a check watches them, in seconds
    Role_Poll_Interval = 0.2

    # How long the run logs and the run state of a scheduler that still runs may disagree, in seconds,
    # as each run is recorded in both at different moments
    Scheduler_Settle_Timeout = 5.0

# ################################################################################################################################
# ################################################################################################################################

def read_run_states(env:'HAEnvironment') -> 'anydict':
    """ Returns the run state of each scheduler job as the Zato database that both nodes share holds it.
    """
    object_type = "'" + SchedulerJobsCtx.Run_State_Object_Type + "'"
    query = f'select name, data from zato_shared_object where object_type = {object_type}'
    rows = read_database_rows(cast_('any_', env), query)

    # The column is of the JSON type in PostgreSQL, which the driver returns decoded.
    out:'anydict' = {}

    for name, data in rows:
        out[name] = data

    return out

# ################################################################################################################################

def check_scheduler(env:'HAEnvironment', unrun_claims:'int'=0) -> 'dictlist':
    """ Checks that no slot completed twice or began on both nodes and that the run logs agree with the run state
    in the Zato database, returning the entries of the run logs. The run state of each job may count the given number
    of claims that a server stopped before it ran them.
    """
    deadline = time.monotonic() + ModuleCtx.Scheduler_Settle_Timeout

    while True:
        entries = read_run_log(cast_('any_', env))

        repeated = get_repeated_completed_slots(entries)
        assert not repeated, repeated

        states = read_run_states(env)
        mismatches = get_state_mismatches(entries, states, unrun_claims)

        if not mismatches:
            break

        # A disagreement that outlasts the recording of one run is a defect ..
        assert time.monotonic() < deadline, mismatches

        # .. and a shorter one is a run that one of them has not recorded yet.
        time.sleep(ModuleCtx.Role_Poll_Interval)

    out = entries
    return out

# ################################################################################################################################

def check_no_runs_after(env:'HAEnvironment', replaced:'Node', boundary:'float') -> 'None':
    """ Checks that a node that was replaced at the given time began no scheduler run afterwards.
    """
    entries = read_run_log(cast_('any_', env))
    late = get_starts_after(entries, replaced.node_name, boundary)

    assert not late, f'{replaced.node_name} ran jobs after it was replaced -> {late}'

# ################################################################################################################################

def check_no_runs_while_replaced(env:'HAEnvironment', replaced:'Node', boundary:'float', reactivated:'float') -> 'None':
    """ Checks that a node that was replaced at the given time began no scheduler run until it became active again.
    """
    entries = read_run_log(cast_('any_', env))
    late:'dictlist' = []

    for entry in get_starts_after(entries, replaced.node_name, boundary):
        if entry['time'] < reactivated:
            late.append(entry)

    assert not late, f'{replaced.node_name} ran jobs while it was replaced -> {late}'

# ################################################################################################################################

def check_publications_stored(env:'HAEnvironment', active:'Node', msg_ids:'strlist') -> 'None':
    """ Checks that the Zato database holds every publication with the given message IDs that the active node acknowledged.
    """
    query = 'select msg_id from pubsub_message'
    rows = read_database_rows(cast_('any_', env), query)

    stored:'set[str]' = set()

    for row in rows:
        stored.add(row[0])

    missing:'strlist' = []

    for msg_id in msg_ids:
        if msg_id not in stored:
            missing.append(msg_id)

    assert not missing, f'Acknowledged publications missing from {active.node_name} -> {missing}'

# ################################################################################################################################

def check_workload(env:'HAEnvironment', workload:'Workload') -> 'None':
    """ Drains the pull queue and checks that every acknowledged publication was handed out and pushed,
    that a message was pulled again only after its acknowledgment failed, that every repeated push was in flight
    during a fault and that the stored counts equal the rows.
    """
    workload.drain_pulls()

    unexpected = workload.get_unexpected_repeated_pulls()
    assert not unexpected, f'Pulled again without a failed acknowledgment -> {sorted(unexpected)}'

    _ = wait_for_deliveries(cast_('any_', env), workload.acknowledged)

    receiver = env.receivers[Topic_Name]
    records = receiver.get_request_records()
    not_in_flight = get_repeats_not_in_flight(records, workload.fault_windows)
    assert not not_in_flight, f'Repeated pushes without a fault -> {not_in_flight}'

    mismatches = get_count_mismatches(cast_('any_', env))
    assert not mismatches, mismatches

# ################################################################################################################################

def watch_roles(env:'HAEnvironment', seconds:'float') -> 'strlist':
    """ Reads the roles of both nodes for the given time and returns each moment at which both served requests.
    """
    out:'strlist' = []
    deadline = time.monotonic() + seconds

    while time.monotonic() < deadline:
        active_nodes:'strlist' = []

        for node in env.node_list:
            if node.is_active():
                active_nodes.append(node.node_name)

        if len(active_nodes) > 1:
            out.append(f'{time.time():.3f} {active_nodes}')

        time.sleep(ModuleCtx.Role_Poll_Interval)

    return out

# ################################################################################################################################
# ################################################################################################################################
