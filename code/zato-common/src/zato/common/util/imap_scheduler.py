# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps, loads

# Zato
from zato.common.api import EMAIL
from zato.common.odb.model import IMAP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import strnone

    SASession = SASession

# ################################################################################################################################
# ################################################################################################################################

_scheduler = EMAIL.IMAP.Scheduler

# ################################################################################################################################
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
    invoke_with:'strnone',
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

    # .. the same applies to the invoke-with mode, which older jobs do not carry in their extra data ..
    if invoke_with:
        opaque[_scheduler.Field_Invoke_With] = invoke_with

    # .. and store the result back.
    row.opaque1 = dumps(opaque)

    session.add(row)
    session.commit()

# ################################################################################################################################
# ################################################################################################################################
