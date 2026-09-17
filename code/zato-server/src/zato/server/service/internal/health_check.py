# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The scheduler jobs linked to a connection of any type - the one place that creates, updates and deletes them,
# and the health check job in particular, which pings a connection on a schedule and writes each ping to the
# audit log under the connection's health source. Outgoing REST and SOAP connections and outgoing FHIR
# connections all keep their health check job in sync through here.

# stdlib
from contextlib import closing

# Zato
from zato.common.api import HTTP_SOAP, SCHEDULER, SchedulerLink
from zato.common.defaults import default_cluster_id
from zato.common.json_internal import dumps
from zato.common.odb.model import Job
from zato.common.util.api import utcnow
from zato.common.util.interval import interval_from_unit
from zato.common.util.rest_invocation import update_linked_job_fields
from zato.server.connection.http_soap import BadRequest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import any_, intnone
    from zato.server.service.internal import AdminService
    intnone = intnone

# ################################################################################################################################
# ################################################################################################################################

_invocation = HTTP_SOAP.Invocation
_health_check = HTTP_SOAP.HealthCheck

# ################################################################################################################################
# ################################################################################################################################

def has_health_check_config(input:'Bunch') -> 'bool':
    """ Returns True if a health check was asked for on input - its run-every is the one thing that says so,
    the check's outcome reaching people through the connection's alerts rather than through a callback of its own.
    """
    out = bool(input.get(_health_check.Field_Run_Every))
    return out

# ################################################################################################################################

def validate_run_every(service:'AdminService', run_every:'any_', run_unit:'str', label:'str') -> 'int':
    """ Makes sure a run-every value and its unit describe a job interval that can be created.
    """
    run_every = int(run_every)

    if run_every < 1:
        raise BadRequest(service.cid, f'{label} run-every must be a positive integer instead of `{run_every}`')

    if run_unit not in _invocation.UnitList:
        raise BadRequest(service.cid, f'{label} unit `{run_unit}` is not one of `{_invocation.UnitList}`')

    return run_every

# ################################################################################################################################

def get_linked_job(service:'AdminService', job_id:'int') -> 'any_':
    """ Returns the Job row of the given ID or None if it no longer exists.
    """
    with closing(service.odb.session()) as session:
        out = session.query(Job).filter_by(id=job_id).first()
        if out:
            session.expunge(out)

    return out

# ################################################################################################################################

def sync_one_linked_job(
    service,        # type: AdminService
    conn_id,        # type: int
    link_conn_type, # type: str
    is_active,      # type: bool
    kind,           # type: str
    has_config,     # type: bool
    job_id,         # type: intnone
    job_name,       # type: str
    job_service,    # type: str
    start_date,     # type: str
    run_every,      # type: any_
    run_unit,       # type: str
    extra,          # type: str
    ) -> 'None':
    """ Creates, updates or deletes one scheduler job linked to a connection, based on the input just committed.
    The link's connection type says which config store the job points back to.
    """

    # The job the connection points to may or may not still exist,
    # e.g. it could have been deleted from the scheduler's own UI.
    job = None
    if job_id:
        job = get_linked_job(service, job_id)

    # We are to keep a job in sync with what was given on input ..
    if has_config:

        request = {
            'cluster_id': default_cluster_id,
            'is_active': is_active,
            'job_type': SCHEDULER.JOB_TYPE.INTERVAL_BASED,
            'service': job_service,
            'start_date': start_date,
            'extra': extra,
            SchedulerLink.Conn_Type: link_conn_type,
            SchedulerLink.Conn_ID: conn_id,
            SchedulerLink.Kind: kind,
        }

        interval = interval_from_unit(run_every, run_unit)
        request.update(interval)

        # .. the job exists so it is updated in place, keeping its current name to honor renames done in the scheduler ..
        if job:
            request['id'] = job.id
            request['name'] = job.name
            _ = service.invoke('zato.scheduler.job.edit', request)
            new_job_id = job.id

        # .. otherwise, a new job is created for this connection ..
        else:
            request['name'] = job_name
            response = service.invoke('zato.scheduler.job.create', request)
            if 'id' not in response:
                response = response['zato_scheduler_job_create_response']
            new_job_id = response['id']

        # .. either way, the connection's opaque attributes now reflect the job's current state.
        with closing(service.odb.session()) as session:
            update_linked_job_fields(session, conn_id, link_conn_type, kind, run_every, run_unit, start_date, new_job_id)

    # There is no configuration on input ..
    else:

        # .. so a job that still exists is deleted, which also clears the connection's linked-job fields.
        if job:
            _ = service.invoke('zato.scheduler.job.delete', {'id': job.id})

# ################################################################################################################################

def sync_health_check_job(service:'AdminService', input:'Bunch', conn_id:'int', link_conn_type:'str') -> 'None':
    """ Keeps the health check job of a connection in sync with the input just committed - the job pings
    the connection, each ping writing its outcome to the audit log under the connection's health source,
    where the connection's alerts read it.
    """
    health_check_extra = dumps({
        _health_check.Extra_Conn_ID: conn_id,
        _health_check.Extra_Conn_Name: input.name,
        _health_check.Extra_Conn_Type: link_conn_type,
    })

    # Health check jobs have no user-facing start date so they start right away
    health_check_start_date = utcnow().isoformat()

    sync_one_linked_job(
        service,
        conn_id,
        link_conn_type,
        is_active=input.is_active,
        kind=SchedulerLink.KindType.HealthCheck,
        has_config=has_health_check_config(input),
        job_id=input.get(_health_check.Field_Job_ID),
        job_name=_health_check.Job_Prefix + input.name,
        job_service=_health_check.Dispatch_Service,
        start_date=health_check_start_date,
        run_every=input.get(_health_check.Field_Run_Every),
        run_unit=input.get(_health_check.Field_Run_Unit),
        extra=health_check_extra,
    )

# ################################################################################################################################

def delete_health_check_job(service:'AdminService', job_id:'intnone') -> 'None':
    """ Deletes the health check job of a connection that is itself being deleted, so the job does not outlive it.
    """
    if not job_id:
        return

    job = get_linked_job(service, job_id)

    if job:
        _ = service.invoke('zato.scheduler.job.delete', {'id': job.id})

# ################################################################################################################################
# ################################################################################################################################
