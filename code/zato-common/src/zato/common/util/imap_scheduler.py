# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps, loads
from typing import NamedTuple

# Zato
from zato.common.api import EMAIL
from zato.common.odb.model import IMAP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import intnone, stranydict, strnone

    SASession = SASession

# ################################################################################################################################
# ################################################################################################################################

_scheduler = EMAIL.IMAP.Scheduler

Seconds_Per_Minute = 60
Seconds_Per_Hour   = 3600
Seconds_Per_Day    = 86400
Seconds_Per_Week   = 604800

# ################################################################################################################################
# ################################################################################################################################

class RunEveryUnit(NamedTuple):
    run_every: int
    run_unit: str

# ################################################################################################################################
# ################################################################################################################################

def interval_from_unit(run_every:'int', run_unit:'str') -> 'stranydict':
    """ Maps a run-every value and its unit to the interval fields of a scheduler job.
    """
    out = {'weeks':0, 'days':0, 'hours':0, 'minutes':0, 'seconds':0}
    out[run_unit] = run_every

    return out

# ################################################################################################################################

def unit_from_interval(
    weeks:'intnone',
    days:'intnone',
    hours:'intnone',
    minutes:'intnone',
    seconds:'intnone',
    ) -> 'RunEveryUnit':
    """ Maps the interval fields of a scheduler job back to a run-every value and its unit.
    The result uses the largest unit that divides the total evenly, e.g. 120 seconds becomes 2 minutes.
    """

    # The columns are nullable in the database and a missing value means the same as zero
    if weeks is None:
        weeks = 0
    if days is None:
        days = 0
    if hours is None:
        hours = 0
    if minutes is None:
        minutes = 0
    if seconds is None:
        seconds = 0

    # Everything is normalized to seconds first ..
    total_seconds = weeks * Seconds_Per_Week + days * Seconds_Per_Day + hours * Seconds_Per_Hour + \
        minutes * Seconds_Per_Minute + seconds

    # .. and then expressed in the largest unit that divides the total evenly.
    if total_seconds % Seconds_Per_Day == 0:
        out = RunEveryUnit(total_seconds // Seconds_Per_Day, _scheduler.Unit.Days)
    elif total_seconds % Seconds_Per_Hour == 0:
        out = RunEveryUnit(total_seconds // Seconds_Per_Hour, _scheduler.Unit.Hours)
    elif total_seconds % Seconds_Per_Minute == 0:
        out = RunEveryUnit(total_seconds // Seconds_Per_Minute, _scheduler.Unit.Minutes)
    else:
        out = RunEveryUnit(total_seconds, _scheduler.Unit.Seconds)

    return out

# ################################################################################################################################

def clear_imap_scheduler_fields(session:'SASession', imap_conn_id:'int') -> 'None':
    """ Removes the scheduler-related opaque fields from an IMAP connection whose linked job was deleted.
    """

    # The connection may no longer exist, e.g. the job is being deleted because the connection itself is
    row = session.query(IMAP).filter_by(id=imap_conn_id).first()
    if not row:
        return

    # Load the current opaque attributes ..
    opaque = loads(row.opaque1) if row.opaque1 else {}

    # .. remove everything that described the linked job ..
    for name in _scheduler.FieldList:
        opaque.pop(name, None)

    # .. and store the result back.
    row.opaque1 = dumps(opaque)

    session.add(row)
    session.commit()

# ################################################################################################################################

def update_imap_scheduler_fields(
    session:'SASession',
    imap_conn_id:'int',
    run_every:'int',
    run_unit:'str',
    start_date:'str',
    service_name:'strnone',
    job_id:'int',
    ) -> 'None':
    """ Writes the current state of a scheduler job back to the opaque fields of its linked IMAP connection.
    """

    # The connection may no longer exist, e.g. the job outlived it
    row = session.query(IMAP).filter_by(id=imap_conn_id).first()
    if not row:
        return

    # Load the current opaque attributes ..
    opaque = loads(row.opaque1) if row.opaque1 else {}

    # .. reflect the job's current definition ..
    opaque[_scheduler.Field_Run_Every] = run_every
    opaque[_scheduler.Field_Run_Unit] = run_unit
    opaque[_scheduler.Field_Start_Date] = start_date
    opaque[_scheduler.Field_Job_ID] = job_id

    # .. the per-message service is written back only if the caller knows it - the job's extra data
    # .. may not describe it, in which case the field previously stored is left untouched ..
    if service_name:
        opaque[_scheduler.Field_Service] = service_name

    # .. and store the result back.
    row.opaque1 = dumps(opaque)

    session.add(row)
    session.commit()

# ################################################################################################################################
# ################################################################################################################################
