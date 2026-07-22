# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps, loads
from re import sub as re_sub

# Zato
from zato.common.api import FileTransfer
from zato.common.odb.model import GenericConn

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import dictlist, stranydict

    SASession = SASession

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

# ################################################################################################################################
# ################################################################################################################################

def get_schedule_list(session:'SASession', conn_id:'int') -> 'dictlist':
    """ Returns the list of file transfer schedules stored with a connection, an empty list if there are none.
    """

    # The connection may no longer exist, e.g. it was deleted concurrently
    row = session.query(GenericConn).filter_by(id=conn_id).first()
    if not row:
        return []

    # Load the current opaque attributes ..
    opaque = loads(row.opaque1) if row.opaque1 else {}

    # .. and hand back the schedules stored there, if any.
    out = opaque.get(_scheduler.Schedules_Field) or []

    return out

# ################################################################################################################################

def set_schedule_list(session:'SASession', conn_id:'int', schedules:'dictlist') -> 'None':
    """ Stores the given list of file transfer schedules with a connection, replacing what was there before.
    """

    # The connection may no longer exist, e.g. it was deleted concurrently
    row = session.query(GenericConn).filter_by(id=conn_id).first()
    if not row:
        return

    # Load the current opaque attributes ..
    opaque = loads(row.opaque1) if row.opaque1 else {}

    # .. replace the schedules stored there ..
    opaque[_scheduler.Schedules_Field] = schedules

    # .. and store the result back.
    row.opaque1 = dumps(opaque)

    session.add(row)
    session.commit()

# ################################################################################################################################

def update_schedule_job_fields(
    session,     # type: SASession
    conn_id,     # type: int
    schedule_id, # type: str
    run_every,   # type: int
    run_unit,    # type: str
    start_date,  # type: str
    job_id,      # type: int
    ) -> 'None':
    """ Writes the current state of a scheduler job back to the schedule entry it is linked to,
    e.g. after an edit made directly in the scheduler's own UI.
    """
    schedules = get_schedule_list(session, conn_id)

    # Reflect the job's current definition in the entry it belongs to ..
    for schedule in schedules:
        if schedule['id'] == schedule_id:
            schedule['run_every'] = run_every
            schedule['run_unit'] = run_unit
            schedule['start_date'] = start_date
            schedule['job_id'] = job_id
            break

    # .. the entry may be gone already, in which case there is nothing to write back ..
    else:
        return

    # .. and store the updated list.
    set_schedule_list(session, conn_id, schedules)

# ################################################################################################################################

def delete_schedule_entry(session:'SASession', conn_id:'int', schedule_id:'str') -> 'None':
    """ Removes one schedule entry from a connection, e.g. after its linked job was deleted
    directly in the scheduler's own UI - a schedule without a job would never run.
    """
    schedules = get_schedule_list(session, conn_id)

    # Keep everything except the entry whose job went away ..
    out:'dictlist' = []

    for schedule in schedules:
        if schedule['id'] != schedule_id:
            out.append(schedule)

    # .. and store the updated list.
    set_schedule_list(session, conn_id, out)

# ################################################################################################################################

def get_schedule_id(name:'str') -> 'str':
    """ Turns a schedule's name into its id - a lowercase slug that stays stable across renames of other fields,
    e.g. Invoices Hourly becomes invoices-hourly.
    """

    # Everything that is not a letter, a digit or a dot becomes a dash ..
    out = re_sub('[^a-z0-9.]+', '-', name.lower())

    # .. and the edges never carry dashes.
    out = out.strip('-')

    return out

# ################################################################################################################################

def get_job_name(conn_type:'str', conn_name:'str', schedule_name:'str') -> 'str':
    """ Returns the conventional name of the job linked to a schedule, e.g. sftp.My Connection.invoices.hourly.
    """
    prefix = _scheduler.Job_Prefix[conn_type]

    out = f'{prefix}{conn_name}.{schedule_name}'
    return out

# ################################################################################################################################

# The schedule fields that never travel in YAML - the id is derived from the name
# and the job id is a database-specific value that would not survive a move.
_non_portable_fields = ('id', 'job_id')

# The optional schedule fields next to their defaults - a value matching its default is not exported
# and a missing value on import means the default.
_optional_field_defaults = {
    'is_active': True,
    'pattern': FileTransfer.Scheduler.Default_Pattern,
    'ready_how': FileTransfer.Scheduler.ReadyHow.Stability,
    'stability_delay': FileTransfer.Scheduler.Default_Stability_Delay,
    'marker_suffix': FileTransfer.Scheduler.Default_Marker_Suffix,
    'should_claim': False,
    'on_success': FileTransfer.Scheduler.OnSuccess.Move,
    'move_directory': FileTransfer.Scheduler.Default_Move_Directory,
}

# ################################################################################################################################

def export_schedule_list(schedules:'dictlist') -> 'dictlist':
    """ Turns a connection's stored schedules into their portable YAML shape - without database-specific
    fields and without options that match the defaults.
    """

    # Our response to produce
    out:'dictlist' = []

    for schedule in schedules:
        item = {}

        for name, value in schedule.items():

            # Database-specific fields never travel ..
            if name in _non_portable_fields:
                continue

            # .. and neither do options left at their defaults.
            if name in _optional_field_defaults:
                if value == _optional_field_defaults[name]:
                    continue

            item[name] = value

        out.append(item)

    return out

# ################################################################################################################################

def schedule_from_yaml(schedule_def:'stranydict') -> 'stranydict':
    """ Turns the YAML shape of one schedule back into a full entry of a connection's list,
    filling in the defaults for everything the YAML left out. The job link is added by the caller.
    """
    name = schedule_def['name']

    out = {
        'id': get_schedule_id(name),
        'name': name,
        'directory': schedule_def['directory'],
        'service': schedule_def['service'],
        'run_every': schedule_def['run_every'],
        'run_unit': schedule_def['run_unit'],
        'start_date': schedule_def.get('start_date') or '',
        'job_id': 0,
    }

    # Everything optional means its default unless the YAML says otherwise
    for field, default in _optional_field_defaults.items():
        out[field] = schedule_def.get(field, default)

    return out

# ################################################################################################################################

def build_job_extra(conn_id:'int', conn_name:'str', conn_type:'str', schedule:'stranydict') -> 'str':
    """ Builds the extra data of a schedule's linked job - the full schedule travels along
    so a fire event is self-contained.
    """
    extra = {
        _scheduler.Extra_Conn_ID: conn_id,
        _scheduler.Extra_Conn_Name: conn_name,
        _scheduler.Extra_Conn_Type: conn_type,
        _scheduler.Extra_Schedule: schedule,
    }

    out = dumps(extra)
    return out

# ################################################################################################################################
# ################################################################################################################################
