# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sqlite3
import sys
from subprocess import Popen
from time import sleep, time
from typing import NamedTuple

# ################################################################################################################################
# ################################################################################################################################

# How often the session database is read while cosmic-ray works through the mutants.
_poll_interval_seconds = 10

# How long a read of the session database waits for cosmic-ray's own write to finish.
_sqlite_timeout_seconds = 5.0

# What is shown in place of an estimate before the first mutant has been completed.
_unknown_eta = 'n/a'

_killed_outcome = 'KILLED'
_survived_outcome = 'SURVIVED'

# ################################################################################################################################
# ################################################################################################################################

class _Counts(NamedTuple):
    total: int
    done: int
    killed: int
    survived: int

# ################################################################################################################################
# ################################################################################################################################

def _format_duration(seconds:'float') -> 'str':
    """ Renders a number of seconds as minutes and seconds.
    """
    total_seconds = int(seconds)
    minutes = total_seconds // 60
    remainder = total_seconds % 60

    out = f'{minutes}m{remainder:02d}s'
    return out

# ################################################################################################################################

def _read_counts(session_file:'str') -> '_Counts | None':
    """ Reads how far cosmic-ray has got. Returns None while the session is locked by cosmic-ray's own write.
    """
    session_uri = f'file:{session_file}?mode=ro'

    try:
        connection = sqlite3.connect(session_uri, uri=True, timeout=_sqlite_timeout_seconds)
    except sqlite3.OperationalError:
        return None

    try:

        # Every mutant that init found ..
        cursor = connection.execute('select count(*) from work_items')
        row = cursor.fetchone()
        total = row[0]

        # .. and the outcome of each one that has been tested so far.
        cursor = connection.execute('select test_outcome, count(*) from work_results group by test_outcome')
        rows = cursor.fetchall()

    except sqlite3.OperationalError:
        return None

    finally:
        connection.close()

    done = 0
    killed = 0
    survived = 0

    for outcome, count in rows:
        done += count

        if outcome == _killed_outcome:
            killed = count

        elif outcome == _survived_outcome:
            survived = count

    out = _Counts(total=total, done=done, killed=killed, survived=survived)
    return out

# ################################################################################################################################

def _report(session_file:'str', started:'float') -> 'None':
    """ Prints one progress line, unless the session has nothing to report yet.
    """
    counts = _read_counts(session_file)

    if not counts:
        return

    if not counts.total:
        return

    elapsed = time() - started
    percent = counts.done / counts.total * 100
    remaining = counts.total - counts.done
    rate = counts.done / elapsed

    if rate:
        eta = _format_duration(remaining / rate)
    else:
        eta = _unknown_eta

    elapsed_label = _format_duration(elapsed)

    counts_label = f'{counts.done}/{counts.total} ({percent:.1f}%)'
    outcome_label = f'killed={counts.killed} survived={counts.survived}'
    timing_label = f'elapsed={elapsed_label} eta={eta}'

    print(f'>>> cosmic-ray {counts_label} {outcome_label} {timing_label}', flush=True)

# ################################################################################################################################

def main() -> 'int':
    """ Runs cosmic-ray exec, reporting how far it has got while it works.
    """
    cosmic_ray = sys.argv[1]
    config_file = sys.argv[2]
    session_file = sys.argv[3]

    command = [cosmic_ray, 'exec', config_file, session_file]
    started = time()
    process = Popen(command)

    # Poll until cosmic-ray is done, printing where it has got to after each interval ..
    while True:

        return_code = process.poll()

        if return_code is not None:
            break

        sleep(_poll_interval_seconds)
        _report(session_file, started)

    # .. and say what the run ended with.
    _report(session_file, started)

    out = return_code
    return out

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)

# ################################################################################################################################
# ################################################################################################################################
