# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Each report table as CSV - the same rows the page renders, in the same order.

from __future__ import annotations

# stdlib
import csv
from io import StringIO

# Zato
from zato.common.audit_log.reports.common import Ack_Headers, Outcome_Headers, Volume_Headers

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.reports.common import ack_row_list, outcome_row_list, volume_row_list
    from zato.common.typing_ import anylist, strtuple
    ack_row_list = ack_row_list
    anylist = anylist
    outcome_row_list = outcome_row_list
    strtuple = strtuple
    volume_row_list = volume_row_list

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

def volume_csv(rows:'volume_row_list') -> 'str':
    """ The volume table as CSV - the same rows the page renders.
    """
    values:'anylist' = []

    for row in rows:
        row_values = [row.period, row.source, row.partner, row.document_type, row.sent, row.received]
        values.append(row_values)

    out = _rows_to_csv(Volume_Headers, values)
    return out

# ################################################################################################################################

def outcomes_csv(rows:'outcome_row_list') -> 'str':
    """ The outcomes table as CSV - the same rows the page renders.
    """
    values:'anylist' = []

    for row in rows:
        row_values = [row.source, row.partner, row.document_type, row.delivered, row.failed, row.failure_breakdown]
        values.append(row_values)

    out = _rows_to_csv(Outcome_Headers, values)
    return out

# ################################################################################################################################

def ack_discipline_csv(rows:'ack_row_list') -> 'str':
    """ The acknowledgment discipline table as CSV - the same rows the page renders.
    """
    values:'anylist' = []

    for row in rows:
        row_values = [row.partner, row.acknowledged, row.average_seconds, row.max_seconds, row.outstanding,
            row.rejected]
        values.append(row_values)

    out = _rows_to_csv(Ack_Headers, values)
    return out

# ################################################################################################################################
# ################################################################################################################################
