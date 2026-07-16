# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# CSV renderers of the analytics screens - each screen's table renders as CSV too,
# with the same rows the screen itself shows.

# stdlib
import csv
from io import StringIO

# Zato
from zato.common.analytics.query import Channel_CSV_Headers, Consumer_CSV_Headers, Overview_CSV_Headers

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, stranydict, strtuple

    # Dummy assignments to satisfy type checkers
    anylist = anylist
    stranydict = stranydict
    strtuple = strtuple

# ################################################################################################################################
# ################################################################################################################################

def _rows_to_csv(headers:'strtuple', values:'anylist') -> 'str':
    """ Renders one table as CSV, headers first.
    """
    buffer = StringIO()
    writer = csv.writer(buffer)

    _ = writer.writerow(headers)

    for row_values in values:
        _ = writer.writerow(row_values)

    out = buffer.getvalue()
    return out

# ################################################################################################################################

def overview_csv(data:'stranydict') -> 'str':
    """ The overview's channel ranking as CSV - the same rows the screen renders.
    """
    values:'anylist' = []

    for row in data['top_channels']:
        values.append([
            row['name'],
            row['request_count'],
            row['error_count'],
            row['error_rate'],
            row['p95_ms'],
            row['related_count'],
        ])

    out = _rows_to_csv(Overview_CSV_Headers, values)
    return out

# ################################################################################################################################

def channel_csv(data:'stranydict') -> 'str':
    """ The per-channel consumer breakdown as CSV - the same rows the screen renders.
    """
    values:'anylist' = []

    for row in data['rows']:
        values.append([
            row['name'],
            row['request_count'],
            row['error_count'],
            row['error_rate'],
            row['p95_ms'],
            row['last_seen'],
        ])

    out = _rows_to_csv(Channel_CSV_Headers, values)
    return out

# ################################################################################################################################

def consumer_csv(data:'stranydict') -> 'str':
    """ The per-consumer channel breakdown as CSV - the same rows the screen renders.
    """
    values:'anylist' = []

    for row in data['rows']:
        values.append([
            row['name'],
            row['request_count'],
            row['error_count'],
            row['error_rate'],
            row['p95_ms'],
            row['last_seen'],
        ])

    out = _rows_to_csv(Consumer_CSV_Headers, values)
    return out

# ################################################################################################################################
# ################################################################################################################################
