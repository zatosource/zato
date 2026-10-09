# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The scheduler job of a polling SMS channel, created, updated and deleted with the channel through
# the linked-job mechanism of health checks.

# Zato
from zato.common.api import SchedulerLink, SMS
from zato.common.json_internal import dumps
from zato.common.sms.config import is_polling
from zato.common.util.api import as_bool, utcnow
from zato.server.service.internal.health_check import delete_health_check_job, sync_one_linked_job, validate_run_every

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

_scheduler = SMS.Scheduler

# ################################################################################################################################
# ################################################################################################################################

def validate_poll_schedule(service:'AdminService', data:'Bunch') -> 'None':
    """ Validates a polling channel's run-every value and unit, applying the defaults to empty fields.
    """
    if not is_polling(data):
        return

    run_every = data.get(_scheduler.Field_Run_Every)
    if not run_every:
        run_every = _scheduler.Default_Run_Every

    run_unit = data.get(_scheduler.Field_Run_Unit)
    if not run_unit:
        run_unit = _scheduler.Default_Run_Unit

    run_every = validate_run_every(service, run_every, run_unit, 'SMS polling')

    data[_scheduler.Field_Run_Every] = run_every
    data[_scheduler.Field_Run_Unit] = run_unit

# ################################################################################################################################

def sync_poll_job(service:'AdminService', data:'Bunch', channel_id:'int') -> 'None':
    """ Creates, updates or deletes the polling job of an SMS channel to match the committed input.
    A channel in webhook mode has no job.
    """
    extra = dumps({
        _scheduler.Extra_Conn_ID: channel_id,
        _scheduler.Extra_Conn_Name: data.name,
    })

    # The job starts immediately, there is no start date field
    start_date = utcnow().isoformat()

    # A channel in webhook mode has no schedule and its job is deleted
    run_unit = data.get(_scheduler.Field_Run_Unit)
    if run_unit is None:
        run_unit = _scheduler.Default_Run_Unit

    sync_one_linked_job(
        service,
        channel_id,
        SchedulerLink.ConnType.SMS_Channel,
        is_active=as_bool(data.is_active),
        kind=SchedulerLink.KindType.Scheduler,
        has_config=is_polling(data),
        job_id=data.get(_scheduler.Field_Job_ID),
        job_name=_scheduler.Job_Prefix + data.name,
        job_service=_scheduler.Dispatch_Service,
        start_date=start_date,
        run_every=data.get(_scheduler.Field_Run_Every),
        run_unit=run_unit,
        extra=extra,
    )

# ################################################################################################################################

def delete_poll_job(service:'AdminService', opaque:'Bunch') -> 'None':
    """ Deletes the polling job of a deleted SMS channel.
    """
    delete_health_check_job(service, opaque.get(_scheduler.Field_Job_ID))

# ################################################################################################################################
# ################################################################################################################################
