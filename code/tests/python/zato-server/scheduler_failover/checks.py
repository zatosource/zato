# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What the servers of the active-passive scheduler suite recorded - the run logs of the service of the jobs,
# the run state of each job in the shared database and the outcomes in the audit log of each server -
# and the checks of these records against each other.

# stdlib
import json
import os
import sqlite3
import time
from collections import Counter
from datetime import datetime

# Zato
from failover import read_audit_rows
from pair import ModuleCtx as PairCtx
from zato.common.api import SCHEDULER
from zato.common.test.pubsub_database import connect, is_postgresql_mode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pair import SchedulerPair, SchedulerServer
    from zato.common.typing_ import anydict, dictlist, strlist

    SchedulerPair = SchedulerPair
    SchedulerServer = SchedulerServer
    anydict = anydict
    dictlist = dictlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The jobs of the enmasse file.
    Job_Every_Second = 'test.scheduler.every-second'
    Job_Jitter = 'test.scheduler.jitter'
    Job_Repeats = 'test.scheduler.repeats'
    Job_Long_Run = 'test.scheduler.long-run'
    Job_One_Time_Past = 'test.scheduler.one-time-past'
    Job_One_Time_Gap = 'test.scheduler.one-time-gap'

    # How many times the job with a limited number of runs runs.
    Repeats = 20

    # How long a run of the long job takes, in seconds.
    Long_Run_Seconds = 20

    # How long after the recorded time of a takeover the replaced server may still have begun a run, in seconds -
    # the time is taken once the new generation is observed in the database.
    Takeover_Tolerance_Seconds = 1.0

    # How often the run logs are read while a test waits for runs, in seconds.
    Poll_Seconds = 0.5

    # The phases of a run in the run log.
    Phase_Start = 'start'
    Phase_End = 'end'

# ################################################################################################################################

# The interval of each interval job, in seconds.
Job_Intervals = {
    ModuleCtx.Job_Every_Second: 1,
    ModuleCtx.Job_Jitter: 5,
    ModuleCtx.Job_Repeats: 2,
    ModuleCtx.Job_Long_Run: 30,
}

_skip_outcomes = (SCHEDULER.OUTCOME.SKIPPED_ALREADY_RUN, SCHEDULER.OUTCOME.SKIPPED_NOT_ACTIVE)

_audit_skip_query = """
select outcome, count(*)
from event
where source = 'scheduler' and outcome in ('{}', '{}')
group by outcome
""".format(*_skip_outcomes)

# ################################################################################################################################
# ################################################################################################################################

def read_run_log(pair:'SchedulerPair') -> 'dictlist':
    """ Returns the entries of the run logs of all the servers, in the order of their times.
    """
    out:'dictlist' = []

    for server in pair.servers:

        # A server that has not run any job yet has no run log.
        if not os.path.exists(server.run_log_path):
            continue

        with open(server.run_log_path) as run_log:
            for line in run_log:

                # A server that was killed may have left a line without its end.
                if not line.endswith('\n'):
                    continue

                entry = json.loads(line)
                out.append(entry)

    out.sort(key=_get_entry_time)
    return out

# ################################################################################################################################

def _get_entry_time(entry:'anydict') -> 'float':
    out = entry['time']
    return out

# ################################################################################################################################

def get_starts(entries:'dictlist', job:'str'='', server_label:'str'='') -> 'dictlist':
    """ Returns the starts of runs, optionally of one job only and on one server only.
    """
    out:'dictlist' = []

    for entry in entries:
        if entry['phase'] != ModuleCtx.Phase_Start:
            continue
        if job and entry['job'] != job:
            continue
        if server_label and entry['server'] != server_label:
            continue
        out.append(entry)

    return out

# ################################################################################################################################

def wait_for_starts(pair:'SchedulerPair', job:'str', server_label:'str', count:'int', timeout_seconds:'float') -> 'dictlist':
    """ Waits until a server began at least the given number of runs of a job and returns all of its starts of that job.
    """
    deadline = time.monotonic() + timeout_seconds

    while True:
        entries = read_run_log(pair)
        out = get_starts(entries, job, server_label)

        if len(out) >= count:
            return out

        if time.monotonic() > deadline:
            raise Exception(f'Server {server_label} began {len(out)} of {count} runs of {job} in {timeout_seconds}s')

        time.sleep(ModuleCtx.Poll_Seconds)

# ################################################################################################################################
# ################################################################################################################################

def read_run_states(pair:'SchedulerPair') -> 'anydict':
    """ Returns the run state of each job, as the servers stored it in the shared database.
    """
    database = pair.database
    query = 'select name, data from zato_shared_object where object_type = '

    out:'anydict' = {}

    if is_postgresql_mode(database.mode):
        connection = connect(database)

        try:
            cursor = connection.cursor()
            cursor.execute(query + '%s', (PairCtx.Run_State_Object_Type,))
            rows = cursor.fetchall()
        finally:
            connection.close()

    else:
        connection = sqlite3.connect(database.env['Zato_PubSub_DB_Path'])

        try:
            cursor = connection.cursor()
            _ = cursor.execute(query + '?', (PairCtx.Run_State_Object_Type,))
            rows = cursor.fetchall()
        finally:
            connection.close()

    for name, data in rows:

        # SQLite returns the JSON document as text.
        if isinstance(data, str):
            data = json.loads(data)

        out[name] = data

    return out

# ################################################################################################################################

def read_skip_counts(server:'SchedulerServer') -> 'anydict':
    """ Returns how many runs of each skipped outcome the audit log of a server recorded.
    """
    out:'anydict' = dict.fromkeys(_skip_outcomes, 0)

    for outcome, count in read_audit_rows(server.server, _audit_skip_query):
        out[outcome] = count

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_repeated_slots(entries:'dictlist') -> 'strlist':
    """ Returns each nominal slot of a job that more than one run began for, across all the servers.
    """
    counter:'Counter[tuple[str, str]]' = Counter()

    for entry in get_starts(entries):
        if entry['slot']:
            counter[(entry['job'], entry['slot'])] += 1

    out:'strlist' = []

    for (job, slot), count in counter.items():
        if count > 1:
            out.append(f'{job} {slot} x{count}')

    return out

# ################################################################################################################################

def get_starts_after(entries:'dictlist', server_label:'str', boundary:'float') -> 'dictlist':
    """ Returns the runs that a server began after the given time, with the tolerance of a takeover.
    """
    limit = boundary + ModuleCtx.Takeover_Tolerance_Seconds
    out:'dictlist' = []

    for entry in get_starts(entries, server_label=server_label):
        if entry['time'] > limit:
            out.append(entry)

    return out

# ################################################################################################################################

def get_state_mismatches(entries:'dictlist', states:'anydict') -> 'strlist':
    """ Returns each job whose number of runs or latest slot in the run logs differs from its run state.
    """
    out:'strlist' = []
    jobs:'set[str]' = set()

    for entry in get_starts(entries):
        jobs.add(entry['job'])

    for job in sorted(jobs):

        starts = get_starts(entries, job)

        if job not in states:
            out.append(f'{job} has {len(starts)} runs and no run state')
            continue

        state = states[job]

        if state['run_count'] != len(starts):
            out.append(f'{job} has {len(starts)} runs and a run count of {state["run_count"]}')

        latest_slot = _get_latest_slot(starts)

        if _parse_slot(state['last_slot']) != latest_slot:
            out.append(f'{job} has the latest slot {latest_slot} and {state["last_slot"]} in its run state')

    return out

# ################################################################################################################################

def _parse_slot(slot:'str | None') -> 'datetime | None':
    if slot:
        out = datetime.fromisoformat(slot)
    else:
        out = None

    return out

# ################################################################################################################################

def _get_latest_slot(starts:'dictlist') -> 'datetime | None':
    out = None

    for entry in starts:
        slot = _parse_slot(entry['slot'])

        if slot is None:
            continue

        if out is None or slot > out:
            out = slot

    return out

# ################################################################################################################################

def get_catch_up_problems(entries:'dictlist', job:'str', old_label:'str', new_label:'str') -> 'strlist':
    """ Checks that the slots a job missed between two servers were not run, except for the latest of them,
    which the new server ran once as it started, followed by every later slot of the grid.
    """
    interval = Job_Intervals[job]

    old_slots = _get_slots(get_starts(entries, job, old_label))
    new_slots = _get_slots(get_starts(entries, job, new_label))

    out:'strlist' = []

    if not old_slots:
        out.append(f'{job} has no runs on server {old_label}')
        return out

    if not new_slots:
        out.append(f'{job} has no runs on server {new_label}')
        return out

    last_old = old_slots[-1]
    first_new = new_slots[0]
    gap = (first_new - last_old).total_seconds()

    # The new server began with a slot from after the gap, which is the one catch-up run ..
    if gap < 2 * interval:
        out.append(f'{job} missed no slots between {last_old} and {first_new}')

    # .. and from then on, it ran each slot of the grid in turn.
    for previous, current in zip(new_slots, new_slots[1:]):
        step = (current - previous).total_seconds()
        if step != interval:
            out.append(f'{job} on server {new_label} went from {previous} to {current}')

    return out

# ################################################################################################################################

def _get_slots(starts:'dictlist') -> 'list[datetime]':
    out:'list[datetime]' = []

    for entry in starts:
        slot = _parse_slot(entry['slot'])
        if slot is not None:
            out.append(slot)

    out.sort()
    return out

# ################################################################################################################################
# ################################################################################################################################

def check_run_log(pair:'SchedulerPair') -> 'dictlist':
    """ Checks that no slot ran twice and that the run logs agree with the run state, returning the entries of the logs.
    """
    entries = read_run_log(pair)
    states = read_run_states(pair)

    repeated = get_repeated_slots(entries)
    assert not repeated, repeated

    mismatches = get_state_mismatches(entries, states)
    assert not mismatches, mismatches

    return entries

# ################################################################################################################################
# ################################################################################################################################
