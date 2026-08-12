# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ConcurrentLogHandler - updates stlidb's logging config on import so this needs to stay
try:
    import cloghandler # type: ignore
except ImportError:
    pass
else:
    cloghandler = cloghandler # For pyflakes

# stdlib
from contextlib import closing
from copy import deepcopy
from datetime import datetime, timezone
from json import dumps
from logging import getLogger
from time import sleep
from traceback import format_exc

# Bunch
from zato.common.ext.bunch import Bunch

# Zato
from zato.common.api import Alerting, AS2, AS4, SCHEDULER
from zato.common.odb.model import Cluster, IntervalBasedJob, Job, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, list_
    from zato.scheduler.api import SchedulerAPI

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato_scheduler')

# ################################################################################################################################
# ################################################################################################################################

# The Python path of the service the AS2 rotation job invokes - the job may be created
# before the service is deployed for the first time, in which case the service's ODB row
# is created upfront and the deployment sync finds it already in place.
_as2_rotation_service_impl_name = 'zato.server.service.internal.generic.connection.CompleteAS2Rotation'

# The Python path of the service the B2B alerting job invokes, created upfront the same way.
_b2b_alerting_service_impl_name = 'zato.server.service.internal.b2b.B2BAlerting'

# The Python path of the service the generic alerting job invokes, created upfront the same way.
_alerting_service_impl_name = 'zato.server.service.internal.alerting.AlertingRun'

# The Python paths of the three alerting probe services, created upfront the same way.
_cert_check_service_impl_name = 'zato.server.service.internal.alerting.AlertingCertCheck'
_ms_health_service_impl_name = 'zato.server.service.internal.alerting.AlertingMicrosoftHealth'
_canary_service_impl_name = 'zato.server.service.internal.alerting.AlertingCanary'

# The Python paths of the two services the AS2 reliability jobs invoke, created upfront the same way.
_as2_async_mdn_service_impl_name = 'zato.server.service.internal.as2.DeliverAsyncMDNs'
_as2_resend_service_impl_name = 'zato.server.service.internal.as2.ResendOverdueMessages'

# The Python path of the service the AS4 reception awareness job invokes, created upfront the same way.
_as4_resend_service_impl_name = 'zato.server.service.internal.as4.ResendOverdueMessages'

# Whether the AS2/AS4 jobs are created on startup
_as2_as4_jobs_enabled = False

# ################################################################################################################################
# ################################################################################################################################

def ensure_as2_rotation_job_exists(session:'any_', cluster_id:'int') -> 'bool':
    """ Checks if the interval job that completes AS2 certificate rotations exists, creates it if not.
    Returns True if created, False if already existed.
    """
    if not _as2_as4_jobs_enabled:
        return False

    existing = session.query(Job).\
        filter(Job.name==AS2.Default.Rotation_Job_Name).\
        filter(Job.cluster_id==cluster_id).\
        first()

    if existing:
        return False

    cluster = session.query(Cluster).\
        filter(Cluster.id==cluster_id).\
        one()

    service = session.query(Service).\
        filter(Service.name==AS2.Default.Rotation_Service).\
        filter(Service.cluster_id==cluster_id).\
        first()

    # On a first-ever start the service is not in ODB yet, so its row is created here
    # and the deployment sync will find it already in place.
    if not service:
        service = Service(None, AS2.Default.Rotation_Service, True, _as2_rotation_service_impl_name, True, cluster)
        session.add(service)
        session.flush()

    # The start date is only the anchor the hourly interval counts from.
    start_date = datetime.now(timezone.utc)
    start_date = start_date.replace(tzinfo=None)

    job = Job(None, AS2.Default.Rotation_Job_Name, True, SCHEDULER.JOB_TYPE.INTERVAL_BASED, start_date,
        cluster=cluster, service=service)
    interval = IntervalBasedJob(None, job, hours=AS2.Default.Rotation_Job_Interval_Hours)

    session.add(job)
    session.add(interval)

    return True

# ################################################################################################################################
# ################################################################################################################################

def _ensure_interval_job_exists(
    session:'any_',
    cluster_id:'int',
    job_name:'str',
    service_name:'str',
    service_impl_name:'str',
    minutes:'int' = 0,
    hours:'int' = 0,
    is_active:'bool' = True,
    ) -> 'bool':
    """ Checks if the given interval job exists, creates it if not.
    Returns True if created, False if already existed.
    """

    existing = session.query(Job).\
        filter(Job.name==job_name).\
        filter(Job.cluster_id==cluster_id).\
        first()

    if existing:
        return False

    cluster = session.query(Cluster).\
        filter(Cluster.id==cluster_id).\
        one()

    service = session.query(Service).\
        filter(Service.name==service_name).\
        filter(Service.cluster_id==cluster_id).\
        first()

    # On a first-ever start the service is not in ODB yet, so its row is created here
    # and the deployment sync will find it already in place.
    if not service:
        service = Service(None, service_name, True, service_impl_name, True, cluster)
        session.add(service)
        session.flush()

    # The start date is only the anchor the interval counts from.
    start_date = datetime.now(timezone.utc)
    start_date = start_date.replace(tzinfo=None)

    job = Job(None, job_name, is_active, SCHEDULER.JOB_TYPE.INTERVAL_BASED, start_date, cluster=cluster, service=service)

    if hours:
        interval = IntervalBasedJob(None, job, hours=hours)
    else:
        interval = IntervalBasedJob(None, job, minutes=minutes)

    session.add(job)
    session.add(interval)

    return True

# ################################################################################################################################
# ################################################################################################################################

def ensure_as2_async_mdn_job_exists(session:'any_', cluster_id:'int') -> 'bool':
    """ Checks if the interval job that drains the asynchronous MDN queue exists, creates it if not.
    Returns True if created, False if already existed.
    """
    if not _as2_as4_jobs_enabled:
        return False

    out = _ensure_interval_job_exists(session, cluster_id, AS2.Async_MDN.Job_Name, AS2.Async_MDN.Service,
        _as2_async_mdn_service_impl_name, AS2.Async_MDN.Job_Interval_Minutes)

    return out

# ################################################################################################################################
# ################################################################################################################################

def ensure_as2_resend_job_exists(session:'any_', cluster_id:'int') -> 'bool':
    """ Checks if the interval job that resends messages with an overdue MDN exists, creates it
    if not. Returns True if created, False if already existed.
    """
    if not _as2_as4_jobs_enabled:
        return False

    out = _ensure_interval_job_exists(session, cluster_id, AS2.Resend.Job_Name, AS2.Resend.Service,
        _as2_resend_service_impl_name, AS2.Resend.Job_Interval_Minutes)

    return out

# ################################################################################################################################
# ################################################################################################################################

def ensure_as4_resend_job_exists(session:'any_', cluster_id:'int') -> 'bool':
    """ Checks if the interval job that repeats the delivery of messages with an overdue AS4 receipt
    exists, creates it if not. Returns True if created, False if already existed.
    """
    if not _as2_as4_jobs_enabled:
        return False

    out = _ensure_interval_job_exists(session, cluster_id, AS4.Resend.Job_Name, AS4.Resend.Service,
        _as4_resend_service_impl_name, AS4.Resend.Job_Interval_Minutes)

    return out

# ################################################################################################################################
# ################################################################################################################################

def ensure_b2b_alerting_job_exists(session:'any_', cluster_id:'int') -> 'bool':
    """ Checks if the interval job that runs the B2B alerting sweep exists, creates it if not.
    Returns True if created, False if already existed.
    """

    existing = session.query(Job).\
        filter(Job.name==AS2.Alerting.Job_Name).\
        filter(Job.cluster_id==cluster_id).\
        first()

    if existing:
        return False

    cluster = session.query(Cluster).\
        filter(Cluster.id==cluster_id).\
        one()

    service = session.query(Service).\
        filter(Service.name==AS2.Alerting.Service).\
        filter(Service.cluster_id==cluster_id).\
        first()

    # On a first-ever start the service is not in ODB yet, so its row is created here
    # and the deployment sync will find it already in place.
    if not service:
        service = Service(None, AS2.Alerting.Service, True, _b2b_alerting_service_impl_name, True, cluster)
        session.add(service)
        session.flush()

    # The start date is only the anchor the hourly interval counts from.
    start_date = datetime.now(timezone.utc)
    start_date = start_date.replace(tzinfo=None)

    job = Job(None, AS2.Alerting.Job_Name, True, SCHEDULER.JOB_TYPE.INTERVAL_BASED, start_date,
        cluster=cluster, service=service)
    interval = IntervalBasedJob(None, job, hours=AS2.Alerting.Job_Interval_Hours)

    session.add(job)
    session.add(interval)

    return True

# ################################################################################################################################
# ################################################################################################################################

def ensure_alerting_job_exists(session:'any_', cluster_id:'int') -> 'bool':
    """ Checks if the interval job that runs the generic alerting sweep exists, creates it if not.
    Returns True if created, False if already existed.
    """

    existing = session.query(Job).\
        filter(Job.name==Alerting.Job_Name).\
        filter(Job.cluster_id==cluster_id).\
        first()

    if existing:
        return False

    cluster = session.query(Cluster).\
        filter(Cluster.id==cluster_id).\
        one()

    service = session.query(Service).\
        filter(Service.name==Alerting.Service).\
        filter(Service.cluster_id==cluster_id).\
        first()

    # On a first-ever start the service is not in ODB yet, so its row is created here
    # and the deployment sync will find it already in place.
    if not service:
        service = Service(None, Alerting.Service, True, _alerting_service_impl_name, True, cluster)
        session.add(service)
        session.flush()

    # The start date is only the anchor the interval counts from.
    start_date = datetime.now(timezone.utc)
    start_date = start_date.replace(tzinfo=None)

    job = Job(None, Alerting.Job_Name, True, SCHEDULER.JOB_TYPE.INTERVAL_BASED, start_date,
        cluster=cluster, service=service)
    interval = IntervalBasedJob(None, job, minutes=Alerting.Job_Interval_Minutes)

    session.add(job)
    session.add(interval)

    return True

# ################################################################################################################################
# ################################################################################################################################

def ensure_cert_check_job_exists(session:'any_', cluster_id:'int') -> 'bool':
    """ Checks if the daily job that measures TLS certificates for alerting exists, creates it
    if not. Returns True if created, False if already existed.
    """
    out = _ensure_interval_job_exists(session, cluster_id, Alerting.Cert_Job_Name, Alerting.Cert_Service,
        _cert_check_service_impl_name, hours=Alerting.Cert_Job_Interval_Hours)

    return out

# ################################################################################################################################
# ################################################################################################################################

def ensure_ms_health_job_exists(session:'any_', cluster_id:'int') -> 'bool':
    """ Checks if the job that polls Microsoft service health for alerting exists, creates it
    if not. Returns True if created, False if already existed.
    """
    out = _ensure_interval_job_exists(session, cluster_id, Alerting.Health_Job_Name, Alerting.Health_Service,
        _ms_health_service_impl_name, minutes=Alerting.Health_Job_Interval_Minutes)

    return out

# ################################################################################################################################
# ################################################################################################################################

def ensure_canary_job_exists(session:'any_', cluster_id:'int') -> 'bool':
    """ Checks if the file transfer canary job exists, creates it if not - inactive,
    because the canary writes to remote systems and activating it is the opt-in.
    Returns True if created, False if already existed.
    """
    out = _ensure_interval_job_exists(session, cluster_id, Alerting.Canary_Job_Name, Alerting.Canary_Service,
        _canary_service_impl_name, minutes=Alerting.Canary_Job_Interval_Minutes, is_active=False)

    return out

# ################################################################################################################################
# ################################################################################################################################

def set_job_active(session:'any_', cluster_id:'int', job_name:'str', is_active:'bool') -> 'bool':
    """ Flips one scheduler job's active flag in ODB - the commit stays with the caller.
    Returns whether the row actually changed.
    """
    job = session.query(Job).\
        filter(Job.name==job_name).\
        filter(Job.cluster_id==cluster_id).\
        one()

    # A job already in the desired state has nothing to change
    if job.is_active == is_active:
        return False

    job.is_active = is_active
    session.add(job)

    return True

# ################################################################################################################################
# ################################################################################################################################

def wait_for_odb_service_by_odb(session:'any_', cluster_id:'int', service_name:'str') -> 'None':

    # Assume we do not have it
    service = None

    while not service:

        # Try to look it up ..
        service = session.query(Service).\
            filter(Service.name==service_name).\
            filter(Cluster.id==cluster_id).\
            first()

        # .. if not found, sleep for a moment.
        if not service:
            sleep(1)
            logger.info('Waiting for ODB service `%s` (ODB)', service_name)

    # If we are here, it means that the service was found so we can return it
    return service

# ################################################################################################################################
# ################################################################################################################################

def wait_for_odb_service_by_api(api:'SchedulerAPI', service_name:'str') -> 'None':

    # Assume we do not have it
    is_deployed = None

    while not is_deployed:

        # Try to look it up ..
        is_deployed = api.invoke_service('zato.service.is-deployed', {
            'name': service_name
        })

        # .. we can return if we have a response that indicates that the service is deployed ..
        if is_deployed:
            return

        # .. otherwise, we sleep for a moment before the next iteration ..
        else:
            sleep(2)

# ################################################################################################################################

def _add_scheduler_job(api:'SchedulerAPI', job_data:'Bunch', spawn:'bool', source:'str') -> 'None':

    # Ignore jobs that have been removed
    if job_data.name in SCHEDULER.JobsToIgnore:
        logger.info(f'Ignoring job `{job_data.name}` ({source})`')
        return

    if job_data.is_active:
        api.create_edit('create', job_data, spawn=spawn)
    else:
        logger.info(f'Not adding an inactive job `{job_data}`')

# ################################################################################################################################

def add_startup_jobs_to_odb_by_odb(cluster_id:'int', odb:'any_', jobs:'any_') -> 'None':
    """ Uses a direction ODB connection to add initial startup jobs to the ODB.
    """
    with closing(odb.session()) as session:
        now = datetime.utcnow() # type: ignore
        for item in jobs:

            try:
                extra = item.get('extra', '')
                if isinstance(extra, str):
                    extra = extra.encode('utf-8')
                else:
                    if item.get('is_extra_list'):
                        extra = '\n'.join(extra)
                    else:
                        extra = dumps(extra)

                if extra:
                    if not isinstance(extra, bytes):
                        extra = extra.encode('utf8')

                #
                # This will block as long as this service is not available in the ODB.
                # It is required to do it because the scheduler may start before servers
                # in which case services will not be in the ODB yet and we need to wait for them.
                #
                service = wait_for_odb_service_by_odb(session, cluster_id, item['service'])

                cluster = session.query(Cluster).\
                    filter(Cluster.id==cluster_id).\
                    one()

                existing_one = session.query(Job).\
                    filter(Job.name==item['name']).\
                    filter(Job.cluster_id==cluster_id).\
                    first()

                if existing_one:
                    continue

                job = Job(None, item['name'], True, 'interval_based', now, cluster=cluster, service=service, extra=extra)

                kwargs = {}
                for name in('seconds', 'minutes'):
                    if name in item:
                        kwargs[name] = item[name]

                ib_job = IntervalBasedJob(None, job, **kwargs)

                session.add(job)
                session.add(ib_job)
                session.commit()

            except Exception:
                logger.warning(format_exc())

            else:
                logger.info('Initial job added `%s`', job.name)

# ################################################################################################################################

def load_scheduler_jobs_by_odb(api:'SchedulerAPI', odb:'any_', cluster_id:'int', spawn:'bool'=True) -> 'None':
    """ Uses ODB connections directly to obtain a list of all jobs that the scheduler should run.
    """

    # Get a list of jobs ..
    job_list = odb.get_job_list(cluster_id)

    # .. go through each of them ..
    for(id, name, is_active, job_type, start_date, extra, service_name, _,
        _, weeks, days, hours, minutes, seconds, repeats) in job_list:

        # .. build its business representation ..
        job_data = Bunch({
            'id':id, 'name':name, 'is_active':is_active,
            'job_type':job_type, 'start_date':start_date,
            'extra':extra, 'service':service_name, 'weeks':weeks,
            'days':days, 'hours':hours, 'minutes':minutes,
            'seconds':seconds, 'repeats':repeats,
        })

        # .. and invoke a common function to add it to the scheduler.
        _add_scheduler_job(api, job_data, spawn, 'load_scheduler_jobs_by_odb')

# ################################################################################################################################

def add_startup_jobs_to_odb_by_api(api:'SchedulerAPI', jobs:'list_[Bunch]') -> 'None':
    """ Uses server API calls to add initial startup jobs to the ODB.
    """

    # This can be static for all the jobs because the backend will calculate the actual start time itself
    start_date = '2025-01-02T11:22:33'

    # Jobs that we are creating will be active unless the configuration says otherwise
    is_active = True

    # All of the jobs that we are adding are interval-based
    job_type = SCHEDULER.JOB_TYPE.INTERVAL_BASED

    # We are going to ignore jobs that already exist
    should_ignore_existing = True

    # Go through each of the jobs that we are to add ..
    for job in jobs:

        # .. make sure that the service that it depends on is deployed ..
        wait_for_odb_service_by_api(api, job['service'])

        # .. build a request describing the job to be created by copying its configuration ..
        request = deepcopy(job)

        # .. fill out the remaining details ..

        if 'is_active' not in job:
            request.is_active = is_active

        if 'job_type' not in job:
            request.job_type = job_type

        if 'start_date' not in job:
            request.start_date = start_date

        if 'should_ignore_existing' not in job:
            request.should_ignore_existing = should_ignore_existing

        # .. now, we can create a new job, ignoring the fact that it may potentially already exist.
        _ = api.invoke_service('zato.scheduler.job.create', request)

# ################################################################################################################################

def load_scheduler_jobs_by_api(api:'SchedulerAPI', spawn:'bool') -> 'None':
    """ Uses server API calls to obtain a list of all jobs that the scheduler should run.
    """
    # Get a list of all the jobs we are to run ..
    response = api.invoke_service('zato.scheduler.job.get-list', needs_root_elem=True)

    # .. we have some jobs to schedule ..
    if response:

        response = response['response']

        # .. log what we are about to add ..
        items = sorted(elem['name'] for elem in response)

        logger.info('Loading jobs into scheduler -> %s', items)

        # .. go through each of the jobs received ..
        for item in response:

            # .. enrich each of them ..
            job_data = Bunch(item)
            job_data.service = job_data.service_name

            # .. and invoke a common function to add it to the scheduler.
            _add_scheduler_job(api, job_data, spawn, 'load_scheduler_jobs_by_api')

    # .. there is nothing for us to run ..
    else:
        logger.info('No jobs were received from the server')

# ################################################################################################################################
# ################################################################################################################################
