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
from datetime import datetime, timezone
from logging import getLogger

# Zato
from zato.common.api import Alerting, PubSub, SCHEDULER
from zato.common.odb.model import IntervalBasedJob, Job, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato_scheduler')

# ################################################################################################################################
# ################################################################################################################################

# The Python path of the service the generic alerting job invokes - the job may be created
# before the service is deployed for the first time, in which case the service's ODB row
# is created upfront and the deployment sync finds it already in place.
_alerting_service_impl_name = 'zato.server.service.internal.alerting.AlertingRun'

# The Python paths of the three alerting probe services, created upfront the same way.
_cert_check_service_impl_name = 'zato.server.service.internal.alerting.AlertingCertCheck'
_ms_health_service_impl_name = 'zato.server.service.internal.alerting.AlertingMicrosoftHealth'
_test_transfer_service_impl_name = 'zato.server.service.internal.alerting.AlertingTestTransfer'

# The Python path of the service the DLQ rule job invokes
_dlq_rule_service_impl_name = 'zato.server.service.internal.pubsub.dlq.DLQRun'

# ################################################################################################################################
# ################################################################################################################################

def _ensure_interval_job_exists(
    session:'any_',
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
        first()

    if existing:
        return False

    service = session.query(Service).\
        filter(Service.name==service_name).\
        first()

    # On a first-ever start the service is not in ODB yet, so its row is created here
    # and the deployment sync will find it already in place.
    if not service:
        service = Service(None, service_name, True, service_impl_name, True)
        session.add(service)
        session.flush()

    # The start date is only the anchor the interval counts from.
    start_date = datetime.now(timezone.utc)
    start_date = start_date.replace(tzinfo=None)

    job = Job(None, job_name, is_active, SCHEDULER.JOB_TYPE.INTERVAL_BASED, start_date, service=service)

    if hours:
        interval = IntervalBasedJob(None, job, hours=hours)
    else:
        interval = IntervalBasedJob(None, job, minutes=minutes)

    session.add(job)
    session.add(interval)

    return True

# ################################################################################################################################
# ################################################################################################################################

def ensure_alerting_job_exists(session:'any_') -> 'bool':
    """ Checks if the interval job that runs the generic alerting sweep exists, creates it if not.
    Returns True if created, False if already existed.
    """

    existing = session.query(Job).\
        filter(Job.name==Alerting.Job_Name).\
        first()

    if existing:
        return False

    service = session.query(Service).\
        filter(Service.name==Alerting.Service).\
        first()

    # On a first-ever start the service is not in ODB yet, so its row is created here
    # and the deployment sync will find it already in place.
    if not service:
        service = Service(None, Alerting.Service, True, _alerting_service_impl_name, True)
        session.add(service)
        session.flush()

    # The start date is only the anchor the interval counts from.
    start_date = datetime.now(timezone.utc)
    start_date = start_date.replace(tzinfo=None)

    job = Job(None, Alerting.Job_Name, True, SCHEDULER.JOB_TYPE.INTERVAL_BASED, start_date,
        service=service)
    interval = IntervalBasedJob(None, job, minutes=Alerting.Job_Interval_Minutes)

    session.add(job)
    session.add(interval)

    return True

# ################################################################################################################################
# ################################################################################################################################

def ensure_cert_check_job_exists(session:'any_') -> 'bool':
    """ Checks if the daily job that measures TLS certificates for alerting exists, creates it
    if not. Returns True if created, False if already existed.
    """
    out = _ensure_interval_job_exists(session, Alerting.Cert_Job_Name, Alerting.Cert_Service,
        _cert_check_service_impl_name, hours=Alerting.Cert_Job_Interval_Hours)

    return out

# ################################################################################################################################
# ################################################################################################################################

def ensure_ms_health_job_exists(session:'any_') -> 'bool':
    """ Checks if the job that polls Microsoft service health for alerting exists, creates it
    if not. Returns True if created, False if already existed.
    """
    out = _ensure_interval_job_exists(session, Alerting.Health_Job_Name, Alerting.Health_Service,
        _ms_health_service_impl_name, minutes=Alerting.Health_Job_Interval_Minutes)

    return out

# ################################################################################################################################
# ################################################################################################################################

def ensure_test_transfer_job_exists(session:'any_') -> 'bool':
    """ Checks if the test transfer job exists, creates it if not - inactive,
    because the test transfer writes to remote systems and activating it is the opt-in.
    Returns True if created, False if already existed.
    """
    out = _ensure_interval_job_exists(session, Alerting.Test_Transfer_Job_Name, Alerting.Test_Transfer_Service,
        _test_transfer_service_impl_name, minutes=Alerting.Test_Transfer_Job_Interval_Minutes, is_active=False)

    return out

# ################################################################################################################################
# ################################################################################################################################

def ensure_dlq_rule_job_exists(session:'any_') -> 'bool':
    """ Creates the DLQ rule job if it does not exist.
    """
    out = _ensure_interval_job_exists(session, PubSub.Outgoing.DLQ_Job_Name, PubSub.Outgoing.DLQ_Rule_Service,
        _dlq_rule_service_impl_name, minutes=PubSub.Outgoing.DLQ_Job_Interval_Minutes)

    return out

# ################################################################################################################################
# ################################################################################################################################

def set_job_active(session:'any_', job_name:'str', is_active:'bool') -> 'bool':
    """ Flips one scheduler job's active flag in ODB - the commit stays with the caller.
    Returns whether the row actually changed.
    """
    job = session.query(Job).\
        filter(Job.name==job_name).\
        one()

    # A job already in the desired state has nothing to change
    if job.is_active == is_active:
        return False

    job.is_active = is_active
    session.add(job)

    return True

# ################################################################################################################################
# ################################################################################################################################
