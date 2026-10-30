# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone
from random import Random

# SQLAlchemy
from sqlalchemy import select

# Zato
from support import count_filter_sets, event_filter_sets, new_filters, populate, run_blocking, search_windows
from zato.common.audit_log.activity import count_by_bucket, get_match_window
from zato.common.audit_log.api import event_table, get_audit_engine
from zato.common.audit_log.listing import event_conditions

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.audit_log.listing import SearchFilters
    from zato.common.typing_ import anydict, anylist

    anydict = anydict
    anylist = anylist
    Connection = Connection
    SearchFilters = SearchFilters

# ################################################################################################################################
# ################################################################################################################################

# The moments of the events are compared in whole microseconds since the Unix epoch
_epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
_microsecond = timedelta(microseconds=1)

# The lengths of the buckets in milliseconds - whole minutes, ones that do not divide into minutes,
# and one shorter than a minute, which is counted from the events alone.
_bucket_sizes_ms = [60_000, 61_111, 90_000, 600_000, 3_600_000, 30_000]

# How long before the first matching event the first bucket starts
_start_shifts = [timedelta(0), timedelta(seconds=7.5)]

# The most buckets one strip has
_max_bucket_count = 80

# How many events a test writes - each search reads all the events it matches, so that many at most
_event_count = 1500

# ################################################################################################################################
# ################################################################################################################################

def _epoch_us(moment:'datetime') -> 'int':
    """ A moment in whole microseconds since the Unix epoch.
    """
    out = (moment - _epoch) // _microsecond
    return out

# ################################################################################################################################

def _matching_rows(connection:'Connection', filters:'SearchFilters') -> 'anylist':
    """ The moment and the outcome of each event a search matches, read from the events alone.
    """
    dialect_name = connection.dialect.name
    conditions = event_conditions(dialect_name, filters)

    statement = select(event_table.c.event_time, event_table.c.outcome)
    statement = statement.where(*conditions)

    result = connection.execute(statement)

    out = result.all()
    return out

# ################################################################################################################################

def _expected_buckets(rows:'anylist', start_us:'int', bucket_us:'int', bucket_count:'int') -> 'anylist':
    """ The number of events of each outcome in each bucket, with the moments past the last bucket in the last one.
    """
    out:'anylist' = []

    for _ in range(bucket_count):
        counts:'anydict' = {}
        out.append(counts)

    for event_time, outcome in rows:

        offset_us = _epoch_us(event_time) - start_us
        index = offset_us // bucket_us

        if index >= bucket_count:
            index = bucket_count - 1

        counts = out[index]

        if outcome not in counts:
            counts[outcome] = 0

        counts[outcome] += 1

    return out

# ################################################################################################################################

def _check_search(connection:'Connection', filters:'SearchFilters', label:'object') -> 'None':
    """ The window and the buckets of the strip of one search are those the events it matches give.
    """
    rows = _matching_rows(connection, filters)
    window = get_match_window(connection, filters)

    # A search that matches nothing has no window ..
    if not rows:
        assert window is None, label
        return

    # .. while any other one spans from its first matching event to its last one ..
    first_time = rows[0][0]
    last_time = rows[0][0]

    for event_time, _ in rows:

        if event_time < first_time:
            first_time = event_time

        if event_time > last_time:
            last_time = event_time

    assert window is not None, label
    assert window.first_time == first_time, label
    assert window.last_time == last_time, label

    # .. and its buckets count the same events whatever their length and wherever they start.
    for shift in _start_shifts:
        for bucket_ms in _bucket_sizes_ms:

            start_time = first_time - shift
            start_us = _epoch_us(start_time)
            bucket_us = bucket_ms * 1000

            span_us = _epoch_us(last_time) - start_us
            bucket_count = span_us // bucket_us + 1

            if bucket_count > _max_bucket_count:
                bucket_count = _max_bucket_count

            start_ms = start_us / 1000

            expected = _expected_buckets(rows, start_us, bucket_us, bucket_count)
            actual = count_by_bucket(connection, filters, start_ms, bucket_ms, bucket_count)

            assert actual == expected, (label, shift, bucket_ms)

# ################################################################################################################################

def _check_searches(filter_sets:'anylist') -> 'None':
    """ Checks the strip of each search of the filters given in each of the time windows.
    """
    engine = get_audit_engine()

    with engine.connect() as connection:
        for window in search_windows():
            for filter_set in filter_sets:

                filters = new_filters(window, filter_set)
                label = (window, filter_set)

                _check_search(connection, filters, label)

# ################################################################################################################################
# ################################################################################################################################

def _populate_and_check(seed:'int', filter_sets:'anylist') -> 'None':
    """ Writes the events of a test and checks the strip of each search of the filters given.
    """
    rng = Random(seed)
    populate(rng, _event_count)

    _check_searches(filter_sets)

# ################################################################################################################################
# ################################################################################################################################

def test_strip_from_event_counts(audit_backend:'str') -> 'None':
    """ The strip of a search the event counts answer is the strip its matching events give,
    with buckets and time windows that cut minutes.
    """
    filter_sets = count_filter_sets()
    _ = run_blocking(_populate_and_check, 20261106, filter_sets)

# ################################################################################################################################

def test_strip_from_events(audit_backend:'str') -> 'None':
    """ The strip of a search with a free-text query or the outstanding filter is the strip its matching events give.
    """
    filter_sets = event_filter_sets()
    _ = run_blocking(_populate_and_check, 20261107, filter_sets)

# ################################################################################################################################
# ################################################################################################################################
