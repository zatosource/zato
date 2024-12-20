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
from datetime import datetime
from json import dumps
from logging import getLogger
from time import sleep
from traceback import format_exc

# Bunch
from bunch import Bunch

# Zato
from zato.common.api import SCHEDULER
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
        response = api.invoke_service('zato.service.is-deployed', {
            'name': service_name
        })

        # .. we can return if we have a response that indicates that the service is deployed ..
        if response and response.get('is_deployed'):
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

def add_startup_jobs_to_odb_by_odb(cluster_id:'int', odb:'any_', jobs:'any_', stats_enabled:'bool') -> 'None':
    """ Uses a direction ODB connection to add initial startup jobs to the ODB.
    """
    with closing(odb.session()) as session:
        now = datetime.utcnow()
        for item in jobs:

            if item['name'].startswith('zato.stats'):
                continue

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
        _, weeks, days, hours, minutes, seconds, repeats, cron_definition) in job_list:

        # .. build its business representation ..
        job_data = Bunch({
            'id':id, 'name':name, 'is_active':is_active,
            'job_type':job_type, 'start_date':start_date,
            'extra':extra, 'service':service_name, 'weeks':weeks,
            'days':days, 'hours':hours, 'minutes':minutes,
            'seconds':seconds, 'repeats':repeats,
            'cron_definition':cron_definition
        })

        # .. and invoke a common function to add it to the scheduler.
        _add_scheduler_job(api, job_data, spawn, 'load_scheduler_jobs_by_odb')

# ################################################################################################################################

def add_startup_jobs_to_odb_by_api(api:'SchedulerAPI', jobs:'list_[Bunch]', stats_enabled:'bool') -> 'None':
    """ Uses server API calls to add initial startup jobs to the ODB.
    """

    # This can be static for all the jobs because the backend will calculate the actual start time itself
    start_date = '2023-01-02T11:22:33'

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

        if not 'is_active' in job:
            request.is_active = is_active

        if not 'job_type' in job:
            request.job_type = job_type

        if not 'start_date' in job:
            request.start_date = start_date

        if not 'should_ignore_existing' in job:
            request.should_ignore_existing = should_ignore_existing

        # .. now, we can create a new job, ignoring the fact that it may potentially already exist.
        api.invoke_service('zato.scheduler.job.create', request)

# ################################################################################################################################

def load_scheduler_jobs_by_api(api:'SchedulerAPI', spawn:'bool') -> 'None':
    """ Uses server API calls to obtain a list of all jobs that the scheduler should run.
    """

    # Get a list of all the jobs we are to run ..
    response = api.invoke_service('zato.scheduler.job.get-list')

    # .. we have some jobs to schedule ..
    if response:

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
