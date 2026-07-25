# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# B2B reporting - aggregate tables built over the audit events the AS2 and X12 exchanges
# already record, spread over one module per table.
#
# - common  - the ranges, rows, aggregation state and the reading of the events
# - volume  - traffic counts per period, partner and document type
# - outcomes - delivered vs failed with the failures broken down by modifier
# - ack     - per-partner acknowledgment turnaround and open items
# - export  - each table as CSV

from __future__ import annotations

# Zato
from zato.common.audit_log.reports.ack import get_ack_discipline
from zato.common.audit_log.reports.common import Ack_Headers, AckDisciplineRow, Default_Range, get_range_cutoff, \
    Outcome_Headers, OutcomeRow, Range_Day, Range_Hours, Range_Month, Range_Week, Volume_Headers, VolumeRow
from zato.common.audit_log.reports.export import ack_discipline_csv, outcomes_csv, volume_csv
from zato.common.audit_log.reports.outcomes import get_outcomes
from zato.common.audit_log.reports.volume import get_volume

# ################################################################################################################################
# ################################################################################################################################

__all__ = (
    'ack_discipline_csv',
    'get_ack_discipline',
    'get_outcomes',
    'get_range_cutoff',
    'get_volume',
    'outcomes_csv',
    'volume_csv',
    'Ack_Headers',
    'AckDisciplineRow',
    'Default_Range',
    'Outcome_Headers',
    'OutcomeRow',
    'Range_Day',
    'Range_Hours',
    'Range_Month',
    'Range_Week',
    'Volume_Headers',
    'VolumeRow',
)

# ################################################################################################################################
# ################################################################################################################################
