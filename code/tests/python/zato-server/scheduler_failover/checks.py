# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What the servers of the active-standby suites recorded in the run logs of the service of the jobs,
# and the checks of these records against each other and against the run state of each job.

# stdlib
import json
import os
from collections import Counter
from datetime import datetime

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, dictlist, strlist

    any_ = any_
    anydict = anydict
    dictlist = dictlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long after the recorded time of a takeover the replaced server may still have begun a run, in seconds -
    # the time is taken once the new generation is observed in the database.
    Takeover_Tolerance_Seconds = 1.0

    # The phases of a run in the run log.
    Phase_Start = 'start'
    Phase_End = 'end'

# ################################################################################################################################
# ################################################################################################################################

def read_run_log(env:'any_') -> 'dictlist':
    """ Returns the entries of the run logs of all the servers of an environment, in the order of their times.
    """
    out:'dictlist' = []

    for server in env.servers:

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
# ################################################################################################################################

def get_repeated_completed_slots(entries:'dictlist') -> 'strlist':
    """ Returns each nominal slot of a job that more than one run completed for, or that more than one server began.
    A run that its server stopped before the run ended has no end, and the same server runs that slot again
    when the fire stream delivers its entry again, so such a run is not a repeat.
    """
    completed:'Counter[tuple[str, str]]' = Counter()
    servers:'dict[tuple[str, str], set[str]]' = {}

    for entry in entries:
        if not entry['slot']:
            continue

        key = (entry['job'], entry['slot'])

        if entry['phase'] == ModuleCtx.Phase_End:
            completed[key] += 1
        else:
            slot_servers = servers.setdefault(key, set())
            slot_servers.add(entry['server'])

    out:'strlist' = []

    for key, slot_servers in servers.items():
        job, slot = key
        count = completed[key]

        if count > 1:
            out.append(f'{job} {slot} completed x{count}')

        if len(slot_servers) > 1:
            server_names = sorted(slot_servers)
            out.append(f'{job} {slot} began on {server_names}')

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

def get_state_mismatches(entries:'dictlist', states:'anydict', unrun_claims:'int'=0) -> 'strlist':
    """ Returns each job whose number of runs or latest slot in the run logs differs from its run state.
    The run count of each job may exceed its runs by the given number of claims that a stopped server did not run,
    and the latest slot of its run state may then be one of these claims.
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

        run_count = state['run_count']
        run_count_matches = len(starts) <= run_count <= len(starts) + unrun_claims

        if not run_count_matches:
            out.append(f'{job} has {len(starts)} runs and a run count of {run_count}')

        latest_slot = _get_latest_slot(starts)
        state_slot = _parse_slot(state['last_slot'])

        # A claim that a stopped server did not run may hold a slot later than every run in the run logs.
        has_unrun_claim = run_count > len(starts)

        if state_slot == latest_slot:
            slot_matches = True
        elif has_unrun_claim and state_slot and latest_slot:
            slot_matches = state_slot > latest_slot
        else:
            slot_matches = False

        if not slot_matches:
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
# ################################################################################################################################
