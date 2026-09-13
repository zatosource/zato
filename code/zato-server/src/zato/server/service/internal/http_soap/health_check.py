# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing

# Zato
from zato.common.api import HTTP_SOAP, SCHEDULER, SchedulerLink, URL_TYPE
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

def has_scheduler_config(service:'AdminService', input:'Bunch') -> 'bool':
    """ Returns True if the scheduler fields were given on input, raising an error if only some of them were.
    """
    run_every = input.scheduler_run_every
    start_date = input.scheduler_start_date

    # Collect the core fields that were actually filled in
    given = []

    for value in (run_every, start_date):
        if value:
            given.append(value)

    given_count = len(given)

    # Nothing was given, which means that no job is expected to exist
    if not given_count:
        return False

    # Only some of the fields were given, which we cannot accept
    if given_count != 2:
        raise BadRequest(service.cid, 'Scheduler options require both run-every and start date to be given')

    return True

# ################################################################################################################################

def has_health_check_config(input:'Bunch') -> 'bool':
    """ Returns True if a health check was asked for on input - its run-every is the one thing that says so,
    the check's outcome reaching people through the connection's alerts rather than through a callback of its own.
    """
    out = bool(input.health_check_run_every)
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

def preserve_job_ids(input:'Bunch', opaque:'any_') -> 'None':
    """ An empty job ID on input must not overwrite the one stored previously - the authoritative values
    are written back after the linked jobs are synchronized, once this request is committed.
    """
    for field_name in (_invocation.Field_Job_ID, _health_check.Field_Job_ID):
        if not input.get(field_name):
            if previous_job_id := opaque.get(field_name):
                input[field_name] = previous_job_id

# ################################################################################################################################

def sync_one_linked_job(
    service,       # type: AdminService
    input,         # type: Bunch
    conn_id,       # type: int
    kind,          # type: str
    has_config,    # type: bool
    job_id,        # type: intnone
    job_name,      # type: str
    job_service,   # type: str
    start_date,    # type: str
    run_every,     # type: any_
    run_unit,      # type: str
    extra,         # type: str
    ) -> 'None':
    """ Creates, updates or deletes one scheduler job linked to a connection, based on the input just committed.
    """

    # The job the connection points to may or may not still exist,
    # e.g. it could have been deleted from the scheduler's own UI.
    job = None
    if job_id:
        job = get_linked_job(service, job_id)

    # We are to keep a job in sync with what was given on input ..
    if has_config:

        # The connection's transport decides which config store the job's link points back to
        if input.transport == URL_TYPE.SOAP:
            link_conn_type = SchedulerLink.ConnType.SOAP_Outgoing
        else:
            link_conn_type = SchedulerLink.ConnType.REST_Outgoing

        request = {
            'cluster_id': default_cluster_id,
            'is_active': input.is_active,
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
            update_linked_job_fields(session, conn_id, kind, run_every, run_unit, start_date, new_job_id)

    # There is no configuration on input ..
    else:

        # .. so a job that still exists is deleted, which also clears the connection's linked-job fields.
        if job:
            _ = service.invoke('zato.scheduler.job.delete', {'id': job.id})

# ################################################################################################################################

def sync_linked_jobs(service:'AdminService', input:'Bunch', conn_id:'int') -> 'None':
    """ Keeps the scheduled-invocation and health check jobs of an outgoing connection in sync
    with the input just committed.
    """

    # The declarative invocation job runs the connection through the shared dispatch service ..
    if input.transport == URL_TYPE.SOAP:
        job_prefix = _invocation.Job_Prefix_SOAP
    else:
        job_prefix = _invocation.Job_Prefix_REST

    scheduler_extra = dumps({
        _invocation.Extra_Conn_ID: conn_id,
        _invocation.Extra_Conn_Name: input.name,
        _invocation.Extra_Transport: input.transport,
    })

    sync_one_linked_job(
        service,
        input,
        conn_id,
        kind=SchedulerLink.KindType.Scheduler,
        has_config=has_scheduler_config(service, input),
        job_id=input.get(_invocation.Field_Job_ID),
        job_name=job_prefix + input.name,
        job_service=_invocation.Dispatch_Service,
        start_date=input.scheduler_start_date,
        run_every=input.scheduler_run_every,
        run_unit=input.scheduler_run_unit,
        extra=scheduler_extra,
    )

    # .. and the health check job pings the connection, each ping writing its outcome to the audit log
    # .. under the connection's health source, where the connection's alerts read it.
    if input.transport == URL_TYPE.SOAP:
        health_check_conn_type = SchedulerLink.ConnType.SOAP_Outgoing
    else:
        health_check_conn_type = SchedulerLink.ConnType.REST_Outgoing

    health_check_extra = dumps({
        _health_check.Extra_Conn_ID: conn_id,
        _health_check.Extra_Conn_Name: input.name,
        _health_check.Extra_Conn_Type: health_check_conn_type,
    })

    # Health check jobs have no user-facing start date so they start right away
    health_check_start_date = utcnow().isoformat()

    sync_one_linked_job(
        service,
        input,
        conn_id,
        kind=SchedulerLink.KindType.HealthCheck,
        has_config=has_health_check_config(input),
        job_id=input.get(_health_check.Field_Job_ID),
        job_name=_health_check.Job_Prefix + input.name,
        job_service=_health_check.Dispatch_Service,
        start_date=health_check_start_date,
        run_every=input.health_check_run_every,
        run_unit=input.health_check_run_unit,
        extra=health_check_extra,
    )

# ################################################################################################################################
# ################################################################################################################################
