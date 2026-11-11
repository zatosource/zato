# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The checks that every run of the active-standby suites applies - no acknowledged publication lost, every repeated push
# in flight during a fault, no scheduler slot run twice, nothing originating from a replaced node, the integrity
# of both copies and their equal contents once the traffic stops. Every database is read from a private copy
# of its file and its log, so that no check holds a lock that a checkpoint of a node waits for.

# stdlib
import json
import os
import shutil
import sqlite3
import time
from contextlib import contextmanager
from tempfile import TemporaryDirectory

# Zato
from checks import get_repeated_slots, get_starts_after, get_state_mismatches, read_run_log
from pair import ModuleCtx as PairCtx
from workload import get_count_mismatches, get_repeats_not_in_flight, Topic_Name, wait_for_deliveries
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment
    from nodes import Node
    from workload import Workload
    from zato.common.typing_ import any_, anydict, anylist, dictlist, strlist

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The replicated databases whose contents both nodes hold
    PubSub_DB_File = 'pubsub.db'
    Common_DB_File = 'common.db'
    Synchronous_DB_Files = (PubSub_DB_File, Common_DB_File)

    # The answer of an integrity check that found no problem
    Integrity_OK = 'ok'

    # How long the standby may take to reach the end of the logs of the active node once the traffic stops, in seconds
    Sync_Timeout = 120

    # How often the copies are compared while a check waits for them to become equal, in seconds
    Poll_Interval = 1.0

    # How often the roles of both nodes are read while a check watches them, in seconds
    Role_Poll_Interval = 0.2

    # How long the run logs and the run state of a scheduler that still runs may disagree, in seconds,
    # as each run is recorded in both at different moments
    Scheduler_Settle_Timeout = 5.0

    # The tables of SQLite itself, which are not part of the logical contents
    Internal_Table_Prefix = 'sqlite_'

    # The suffix of the log of a database file
    WAL_Suffix = '-wal'

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def open_copy(path:'str') -> 'any_':
    """ Yields a connection to a private copy of a database file and its log, which a node never waits for.
    """
    with TemporaryDirectory() as copy_dir:
        copy_path = os.path.join(copy_dir, os.path.basename(path))

        # The log is copied before the file, so that frames that a checkpoint moves into the file
        # in the meantime are still in the copied log ..
        try:
            _ = shutil.copyfile(path + ModuleCtx.WAL_Suffix, copy_path + ModuleCtx.WAL_Suffix)

        # .. a database without a log consists of its file alone ..
        except FileNotFoundError:
            pass

        # .. and SQLite rebuilds the index of the copied log, ignoring a frame that was being written.
        _ = shutil.copyfile(path, copy_path)
        connection = sqlite3.connect(copy_path)

        try:
            yield connection
        finally:
            connection.close()

# ################################################################################################################################

def query_rows(connection:'sqlite3.Connection', query:'str', params:'anylist | None'=None) -> 'anylist':
    """ Returns the rows of a query against an open database.
    """
    cursor = connection.cursor()

    if params is None:
        _ = cursor.execute(query)
    else:
        _ = cursor.execute(query, params)

    out = list(cursor.fetchall())
    return out

# ################################################################################################################################

def read_rows(path:'str', query:'str', params:'anylist | None'=None) -> 'anylist':
    """ Returns the rows of a query against a private copy of a database file.
    """
    with open_copy(path) as connection:
        out = query_rows(connection, query, params)

    return out

# ################################################################################################################################

def has_message(node:'Node', msg_id:'str') -> 'bool':
    """ Tells whether the pub/sub database of a node holds a message.
    """
    rows = read_rows(node.db_path(ModuleCtx.PubSub_DB_File), 'select 1 from pubsub_message where msg_id = ?', [msg_id])

    out = bool(rows)
    return out

# ################################################################################################################################
# ################################################################################################################################

def get_integrity_problems(env:'HAEnvironment') -> 'strlist':
    """ Returns each replicated database of each node whose integrity check reports a problem.
    """
    out:'strlist' = []

    for node in env.node_list:
        for file_name in ModuleCtx.Synchronous_DB_Files:
            rows = read_rows(node.db_path(file_name), 'pragma integrity_check')
            answer = rows[0][0]

            if answer != ModuleCtx.Integrity_OK:
                out.append(f'{node.node_name} {file_name}: {rows}')

    return out

# ################################################################################################################################

def read_contents(path:'str') -> 'anydict':
    """ Returns the rows of each table of a database, sorted, which is its logical contents.
    """
    out:'anydict' = {}

    # All the tables are read from one copy, so that they describe the same moment.
    with open_copy(path) as connection:
        tables = query_rows(connection, "select name from sqlite_master where type = 'table' order by name")

        for (table_name,) in tables:
            if table_name.startswith(ModuleCtx.Internal_Table_Prefix):
                continue

            rows = query_rows(connection, f'select * from "{table_name}"')
            rows.sort(key=repr)
            out[table_name] = rows

    return out

# ################################################################################################################################

def get_copy_differences(active:'Node', standby:'Node') -> 'strlist':
    """ Returns each table whose rows differ between the databases of the two nodes.
    """
    out:'strlist' = []

    for file_name in ModuleCtx.Synchronous_DB_Files:
        active_contents = read_contents(active.db_path(file_name))
        standby_contents = read_contents(standby.db_path(file_name))

        for table_name in sorted(set(active_contents) | set(standby_contents)):
            if table_name not in active_contents:
                out.append(f'{file_name} {table_name}: only in {standby.node_name}')
            elif table_name not in standby_contents:
                out.append(f'{file_name} {table_name}: only in {active.node_name}')
            elif active_contents[table_name] != standby_contents[table_name]:
                active_count = len(active_contents[table_name])
                standby_count = len(standby_contents[table_name])
                out.append(f'{file_name} {table_name}: {active_count} rows on {active.node_name}, ' + \
                    f'{standby_count} rows on {standby.node_name}')

    return out

# ################################################################################################################################

def wait_for_equal_copies(active:'Node', standby:'Node') -> 'None':
    """ Waits until the standby holds the logical contents of the active node, once the traffic stopped.
    """
    deadline = time.monotonic() + ModuleCtx.Sync_Timeout

    while True:
        differences = get_copy_differences(active, standby)

        if not differences:
            return

        assert time.monotonic() < deadline, f'Copies differ after {ModuleCtx.Sync_Timeout}s -> {differences}'
        time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################
# ################################################################################################################################

def read_run_states(node:'Node') -> 'anydict':
    """ Returns the run state of each scheduler job as the common database of a node holds it.
    """
    query = 'select name, data from zato_shared_object where object_type = ?'
    rows = read_rows(node.db_path(ModuleCtx.Common_DB_File), query, [PairCtx.Run_State_Object_Type])

    out:'anydict' = {}

    for name, data in rows:
        out[name] = json.loads(data)

    return out

# ################################################################################################################################

def check_scheduler(env:'HAEnvironment', active:'Node', unrun_claims:'int'=0) -> 'dictlist':
    """ Checks that no slot ran twice on the two nodes together and that the run logs agree with the run state
    of the active node, returning the entries of the run logs. The run state of each job may count the given number
    of claims that a server stopped before it ran them.
    """
    deadline = time.monotonic() + ModuleCtx.Scheduler_Settle_Timeout

    while True:
        entries = read_run_log(cast_('any_', env))

        repeated = get_repeated_slots(entries)
        assert not repeated, repeated

        states = read_run_states(active)
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

def check_publications_stored(active:'Node', msg_ids:'strlist') -> 'None':
    """ Checks that the active node holds every publication with the given message IDs.
    """
    rows = read_rows(active.db_path(ModuleCtx.PubSub_DB_File), 'select msg_id from pubsub_message')
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

def check_copies(env:'HAEnvironment', active:'Node') -> 'None':
    """ Checks the integrity of both copies and, once the standby caught up, that their contents are equal.
    """
    standby = env.get_other(active)
    wait_for_equal_copies(active, standby)

    problems = get_integrity_problems(env)
    assert not problems, problems

# ################################################################################################################################
# ################################################################################################################################
