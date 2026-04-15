# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from datetime import datetime, timedelta, timezone

# Zato
from zato.cli.enmasse.util import preprocess_item
from zato.common.util.api import parse_datetime

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def compute_next_start_date(start_date, job_def):
    """ Compute the next run time for a job based on its start date and interval settings.
    """

    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)

    current_time = datetime.now(timezone.utc)

    if start_date > current_time:
        return start_date

    seconds = job_def.get('seconds', 0)
    minutes = job_def.get('minutes', 0)
    hours = job_def.get('hours', 0)
    days = job_def.get('days', 0)

    interval_seconds = seconds + (minutes * 60) + (hours * 3600) + (days * 86400)

    if interval_seconds == 0:
        return start_date

    time_elapsed = (current_time - start_date).total_seconds()
    intervals_passed = max(0, int(time_elapsed / interval_seconds))

    next_start = start_date + timedelta(seconds=intervals_passed * interval_seconds)

    if next_start <= current_time:
        next_start += timedelta(seconds=interval_seconds)

    return next_start

# ################################################################################################################################
# ################################################################################################################################

class SchedulerImporter:

    @staticmethod
    def preprocess(items:'anylist') -> 'anylist':

        out = []

        for item in items:
            item = preprocess_item(item)

            if 'start_date' in item:
                start_date_value = item['start_date']
                if isinstance(start_date_value, datetime):
                    original_start_date = start_date_value
                else:
                    original_start_date = parse_datetime(start_date_value)
                item['start_date'] = str(compute_next_start_date(original_start_date, item))

            if 'extra' in item:
                extra = item['extra']
                if isinstance(extra, list):
                    item['extra'] = '\n'.join(str(elem) for elem in extra if elem)

            out.append(item)

        return out

# ################################################################################################################################
# ################################################################################################################################
