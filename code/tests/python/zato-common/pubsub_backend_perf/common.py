# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from contextlib import contextmanager
from shutil import disk_usage
from signal import SIGINT
from tempfile import gettempdir
from time import monotonic

# gevent
from gevent import getcurrent, kill, signal_handler, sleep

# humanize
from humanize import intcomma

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from live_sql.env import database_env
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.pubsub.sql.schema import topic_sub_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import callable_, stranydict

    envgen = Iterator[None]
    floatlist = list[float]

# ################################################################################################################################
# ################################################################################################################################

# The prefix all the pub/sub database environment variables share
_env_prefix = 'Zato_PubSub_DB_'

# Every user-visible operation must complete within this many seconds
Max_Operation_Seconds = 0.050

# The performance floor the whole backend must sustain
Min_Publish_Rate_Per_Second  = 100
Min_Delivery_Rate_Per_Second = 500

# How many rows per second the cleanup process must at least remove -
# a deliberately conservative floor since cleanup runs in the background
# and correctness matters more than speed there.
Min_Cleanup_Rate_Per_Second = 5_000

# The two scales the mass-drain scenario runs at - the main perf target uses
# the smaller one and the dedicated mass target the bigger one. With 100
# subscribers that is a total backlog of one million and ten million messages.
Mass_Drain_Backlog_Main = 10000
Mass_Drain_Backlog_Mass = 100000

# How long each scale may take before it is declared hung, in seconds
Mass_Drain_Deadline_Main = 600
Mass_Drain_Deadline_Mass = 3600

# The concurrent-publish floors of the two scales. The main scale holds the standard
# floor. At the mass scale publishes contend with a hundred continuously draining
# consumers for one serialized database - there the binding guarantee is the
# per-operation time bound, and the floor is what that bound implies
# for strictly serialized publishing.
Mass_Drain_Publish_Floor_Main = Min_Publish_Rate_Per_Second
Mass_Drain_Publish_Floor_Mass = int(1 / Max_Operation_Seconds)

# The two scales of the operations scenario. The main one is many mid-size queues.
# The mass one is few queues of millions of messages each, of which two are cleared
# whole - an operator removing a couple of million messages from individual queues
# in one action, under full load.
Operations_Topics_Main = 100
Operations_Cleared_Main = 20
Operations_Clear_Budget_Main = 120

Operations_Topics_Mass = 4
Operations_Backlog_Mass = 2500000
Operations_Cleared_Mass = 2
Operations_Clear_Budget_Mass = 1800

# The delivery floor of the mass operations scale, measured over the post-clear
# consume window. After the clears only two consumers remain, each against
# a millions-deep queue on one serialized database - a scale where the standard
# floor assumes a full population of consumers, not two.
Operations_Delivery_Floor_Mass = 100

# Where the backend's per-operation log records go - the console shows periodic
# progress lines and scenario summaries only, yet the full detail must survive
# an interrupted run for diagnosis, so it lives outside pytest's own directories.
Log_File_Path = os.path.join(gettempdir(), 'zato-pubsub-backend-perf.log')

# How often the console progress line is printed, in seconds
Progress_Interval_Seconds = 60

# The run stops if the temporary directory has less free space than this
Min_Free_Disk_GB = 20

# How many bytes one gigabyte has
_bytes_per_gb = 1024 ** 3

# The environment variable that says which database the run uses -
# when it is absent, no database is configured, e.g. between tests
_env_type_key = _env_prefix + 'Type'

# What the currently running scenario looks like - each scenario registers
# its shape here so the progress line can name it and report its greenlet counts
progress_context = {
    'scenario': 'starting',
    'publishers': 0,
    'consumers': 0,
}

# ################################################################################################################################
# ################################################################################################################################

def install_interrupt_handler() -> 'None':
    """ Makes Ctrl-C work - under gevent the default handling raises KeyboardInterrupt
    in the greenlet that is currently running, which kills only that greenlet while
    the run continues. This handler directs the interrupt to the main greenlet instead,
    whose unwinding runs the finally blocks that remove the databases.
    A second Ctrl-C terminates the process immediately.
    """
    main_greenlet = getcurrent()
    state = {'count': 0}

    def _on_interrupt() -> 'None':
        state['count'] += 1

        # The second interrupt means the first one could not unwind - terminate immediately
        if state['count'] > 1:
            os._exit(1)

        print('Interrupt received - stopping the run', flush=True)
        kill(main_greenlet, KeyboardInterrupt)

    _ = signal_handler(SIGINT, _on_interrupt)

# ################################################################################################################################

def set_progress_context(scenario:'str', publishers:'int', consumers:'int') -> 'None':
    """ Called by every scenario as it starts so the progress line can name it
    and report how many publisher and consumer greenlets it runs.
    """
    progress_context['scenario'] = scenario
    progress_context['publishers'] = publishers
    progress_context['consumers'] = consumers

# ################################################################################################################################
# ################################################################################################################################

class ProgressCounters(logging.Handler):
    """ Counts the backend's per-operation log records so the console can show
    periodic summaries while the records themselves go to the log file only.
    """
    def __init__(self) -> 'None':
        super().__init__()
        self.published = 0
        self.acked = 0
        self.cleared = 0

    def emit(self, record:'logging.LogRecord') -> 'None':

        # The counts key off the log formats of the backend's operations -
        # if a format changes, the progress line drifts but nothing fails.
        args = record.args

        if not isinstance(args, tuple):
            return

        if record.msg.startswith('Published message'):
            self.published += 1

        elif record.msg.startswith('ack_messages'):
            self.acked += args[1] # type: ignore[operator]

        elif record.msg.startswith('clear_queue'):
            self.cleared += args[1] # type: ignore[operator]

# ################################################################################################################################

def setup_perf_logging() -> 'ProgressCounters':
    """ Routes every log record to the log file and returns the counting handler
    the progress reporting reads - the console stays free for the periodic
    progress lines and the scenario summaries.
    """
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s')

    file_handler = logging.FileHandler(Log_File_Path)
    file_handler.setFormatter(formatter)

    counters = ProgressCounters()

    root = logging.getLogger()
    root.handlers[:] = [file_handler, counters]
    root.setLevel(logging.INFO)

    return counters

# ################################################################################################################################

def _get_subscription_count() -> 'int':
    """ How many topic subscriptions the database holds right now -
    zero when no database is configured, e.g. between tests.
    """
    if _env_type_key not in os.environ:
        return 0

    engine = get_pubsub_engine()

    with engine.connect() as connection:
        query = select(func.count()).select_from(topic_sub_table)
        out = connection.execute(query).scalar()

    return out # type: ignore[return-value]

# ################################################################################################################################

def report_progress_forever(counters:'ProgressCounters') -> 'None':
    """ Prints one console line per interval - which scenario runs, its greenlet
    counts, what moved since the last line and how much disk is free - and stops
    the whole run if free space falls below the floor.
    """
    start = monotonic()

    previous_published = 0
    previous_acked = 0
    previous_cleared = 0

    while True:
        sleep(Progress_Interval_Seconds)

        elapsed = monotonic() - start
        free_gb = disk_usage(gettempdir()).free // _bytes_per_gb

        # The rates cover the last interval only, so a busy scenario
        # does not inflate the numbers of a quiet one that follows it.
        publish_rate = (counters.published - previous_published) // Progress_Interval_Seconds
        ack_rate = (counters.acked - previous_acked) // Progress_Interval_Seconds
        clear_rate = (counters.cleared - previous_cleared) // Progress_Interval_Seconds

        previous_published = counters.published
        previous_acked = counters.acked
        previous_cleared = counters.cleared

        scenario = progress_context['scenario']
        publishers = progress_context['publishers']
        consumers = progress_context['consumers']
        subscriptions = _get_subscription_count()

        message = f'Progress {elapsed:.0f}s [{scenario}]'
        message += f' published={intcomma(counters.published)} ({intcomma(publish_rate)}/s)'
        message += f' acked={intcomma(counters.acked)} ({intcomma(ack_rate)}/s)'
        message += f' cleared={intcomma(counters.cleared)} ({intcomma(clear_rate)}/s)'
        message += f' publishers={publishers} consumers={consumers} subscriptions={intcomma(subscriptions)}'
        message += f' free_disk={free_gb} GB'
        print(message, flush=True)

        # The interrupt unwinds the main greenlet through its finally blocks,
        # which is what removes the databases that consumed the disk.
        if free_gb < Min_Free_Disk_GB:
            print(f'Free disk below {Min_Free_Disk_GB} GB - stopping the run', flush=True)
            os.kill(os.getpid(), SIGINT)

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def pubsub_backend_env(details:'stranydict') -> 'envgen':
    """ Points the Zato_PubSub_DB_* variables at one backend for the duration of a test.
    """
    with database_env(_env_prefix, details):
        yield

# ################################################################################################################################

def cleanup_sqlite_db(db_path:'str') -> 'None':
    """ Removes the SQLite database of one test run so big perf databases never
    accumulate on disk - pytest's own tmp_path retention keeps the last three runs,
    which at mass scale would hold many gigabytes.
    """

    # Release all pooled connections first so the files can be removed ..
    engine = get_pubsub_engine()
    engine.dispose()

    # .. and remove the database along with its WAL companions.
    for suffix in ('', '-wal', '-shm'):
        path = db_path + suffix

        if os.path.exists(path):
            os.remove(path)

# ################################################################################################################################

def measure_median_seconds(operation:'callable_', iterations:'int') -> 'float':
    """ Runs an operation repeatedly and returns its median duration in seconds -
    the median keeps one-off cache misses and scheduler blips out of the verdict.
    """
    timings:'floatlist' = []

    for _ in range(iterations):
        start = monotonic()
        _ = operation()
        elapsed = monotonic() - start
        timings.append(elapsed)

    timings.sort()

    middle_index = len(timings) // 2
    out = timings[middle_index]

    return out

# ################################################################################################################################
# ################################################################################################################################
