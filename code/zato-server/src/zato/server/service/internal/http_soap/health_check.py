# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import HTTP_SOAP, SchedulerLink, URL_TYPE
from zato.common.json_internal import dumps
from zato.server.connection.http_soap import BadRequest
from zato.server.service.internal.health_check import has_health_check_config, sync_health_check_job, sync_one_linked_job, \
    validate_run_every

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import any_
    from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

# Re-exported for the HTTPSOAP services that always imported them from here
has_health_check_config = has_health_check_config
validate_run_every = validate_run_every

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

def preserve_job_ids(input:'Bunch', opaque:'any_') -> 'None':
    """ An empty job ID on input must not overwrite the one stored previously - the authoritative values
    are written back after the linked jobs are synchronized, once this request is committed.
    """
    for field_name in (_invocation.Field_Job_ID, _health_check.Field_Job_ID):
        if not input.get(field_name):
            if previous_job_id := opaque.get(field_name):
                input[field_name] = previous_job_id

# ################################################################################################################################

def link_conn_type_for(transport:'str') -> 'str':
    """ The connection's transport decides which config store a linked job points back to.
    """
    if transport == URL_TYPE.SOAP:
        out = SchedulerLink.ConnType.SOAP_Outgoing
    else:
        out = SchedulerLink.ConnType.REST_Outgoing

    return out

# ################################################################################################################################

def sync_linked_jobs(service:'AdminService', input:'Bunch', conn_id:'int') -> 'None':
    """ Keeps the scheduled-invocation and health check jobs of an outgoing connection in sync
    with the input just committed.
    """
    link_conn_type = link_conn_type_for(input.transport)

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
        conn_id,
        link_conn_type,
        is_active=input.is_active,
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
    sync_health_check_job(service, input, conn_id, link_conn_type)

# ################################################################################################################################
# ################################################################################################################################
