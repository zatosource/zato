# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal
import subprocess
import sys
from time import monotonic

# gevent
from gevent import sleep

# SQLAlchemy
from sqlalchemy import text

# Zato
from zato.common.pubsub.sql.counts import No_Publisher
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.test.pubsub_database import get_db_mode, get_runtime_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from monitor import Monitor
    from zato.common.typing_ import any_, anydict, callable_, strlist

# ################################################################################################################################
# ################################################################################################################################

# The cleanup process, started the way a server starts it.
_cleanup_module = 'zato.common.pubsub.sql.cleanup'

# How long the cleanup process may take to stop after it was asked to, in seconds.
_cleanup_stop_timeout = 120

# The raw counts and the stored counts that must equal them.
_raw_queue_query = text('select sub_key, topic_name, count(*) from pubsub_delivery group by sub_key, topic_name')
_stored_queue_query = text('select sub_key, topic_name, sum(depth) from pubsub_queue_count group by sub_key, topic_name')

_raw_topic_query = text('select topic_name, count(*) from pubsub_message group by topic_name')
_stored_topic_query = text('select topic_name, sum(total) from pubsub_topic_count group by topic_name')

_raw_publish_query = text(f"""
    select topic_name, pub_time_ms - pub_time_ms % 60000, coalesce(publisher, '{No_Publisher}'), count(*)
    from pubsub_message group by 1, 2, 3
""")
_stored_publish_query = text('select topic_name, minute_ms, publisher, sum(total) from pubsub_publish_count group by 1, 2, 3')

# ################################################################################################################################
# ################################################################################################################################

def get_duration(env_name:'str', default_seconds:'int') -> 'int':
    """ How long a suite runs, which the given variable may override, in seconds.
    """
    if value := os.environ.get(env_name, ''):
        out = int(value)
    else:
        out = default_seconds

    return out

# ################################################################################################################################

def get_report_path(label:'str') -> 'str':
    """ The file with the per-minute reports of one suite in the current database mode.
    """
    directory = os.path.join(get_runtime_dir(), 'reports')
    os.makedirs(directory, exist_ok=True)

    out = os.path.join(directory, f'{label}-{get_db_mode()}.txt')
    return out

# ################################################################################################################################

def run_for(monitor:'Monitor', duration_seconds:'float', on_tick:'callable_ | None'=None) -> 'None':
    """ Lets the traffic run for the given time, calling on_tick with the elapsed seconds once a second,
    and stops early when the disk runs low.
    """
    start = monotonic()

    while True:
        elapsed = monotonic() - start

        if elapsed >= duration_seconds or monitor.is_disk_low:
            break

        if on_tick:
            on_tick(elapsed)

        sleep(1)

# ################################################################################################################################

def start_cleanup_process(interval_seconds:'int') -> 'subprocess.Popen[bytes]':
    """ Starts the cleanup process against the pub/sub database of the environment.
    """
    command = [sys.executable, '-m', _cleanup_module, '--interval', str(interval_seconds)]

    out = subprocess.Popen(command, env=dict(os.environ))
    return out

# ################################################################################################################################

def stop_cleanup_process(process:'subprocess.Popen[bytes]') -> 'None':
    process.send_signal(signal.SIGTERM)
    _ = process.wait(timeout=_cleanup_stop_timeout)

# ################################################################################################################################

def _read_counts(connection:'any_', query:'any_') -> 'anydict':
    out:'anydict' = {}

    for row in connection.execute(query):
        key = tuple(row[:-1])
        value = int(row[-1])
        if value:
            out[key] = value

    return out

# ################################################################################################################################

def get_count_mismatches() -> 'strlist':
    """ Returns each key whose stored count differs from the number of its rows - queues, topics and publications.
    """
    out:'strlist' = []
    engine = get_pubsub_engine()

    pairs = [
        ('queue', _raw_queue_query, _stored_queue_query),
        ('topic', _raw_topic_query, _stored_topic_query),
        ('publication', _raw_publish_query, _stored_publish_query),
    ]

    with engine.connect() as connection:
        for name, raw_query, stored_query in pairs:

            raw = _read_counts(connection, raw_query)
            stored = _read_counts(connection, stored_query)

            if raw != stored:
                for key in sorted(set(raw) | set(stored)):
                    raw_value = raw.get(key, 0)
                    stored_value = stored.get(key, 0)
                    if raw_value != stored_value:
                        out.append(f'{name} {key}: {stored_value} stored, {raw_value} rows')

    return out

# ################################################################################################################################
# ################################################################################################################################
