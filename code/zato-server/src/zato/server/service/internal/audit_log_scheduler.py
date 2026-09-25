# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The resubmit service of the scheduler - one recorded job run is run again.

# stdlib
from contextlib import closing
from dataclasses import dataclass
from time import monotonic
from traceback import format_exc

# Zato
from zato.common.api import CHANNEL, SCHEDULER
from zato.common.audit_log.api import AuditLog
from zato.common.audit_log.common import AuditEvent
from zato.common.audit_log.resubmit import load_event, require_event_type, run_once, Action_Reprocess, \
    DuplicateResubmitException, ResubmitException
from zato.common.audit_log.scheduler import record_job_complete, record_job_start
from zato.common.json_internal import dumps
from zato.common.odb.model import Job
from zato.common.util.api import parse_job_extra, utcnow
from zato.server.service import Int
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.resubmit import StoredEvent
    from zato.common.typing_ import any_, intnone, stranydict, strnone
    any_ = any_
    intnone = intnone
    stranydict = stranydict
    StoredEvent = StoredEvent
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# A run repeated by hand has no run number of its own, the way a run started by hand has none either.
_manual_run_number = 0

# A run repeated by hand fires the moment it is asked for, so it is never late.
_manual_delay_ms = 0

# What is recorded when there is no extra data or no error to record.
_empty = ''

_milliseconds_per_second = 1000

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class JobDetails:
    """ What a run needs to know about its job - read out of the ODB in one go.
    """
    id:           'int' = 0
    name:         'str' = ''
    service_name: 'str' = ''
    extra:        'strnone' = None

# ################################################################################################################################

def get_job_by_name(odb:'any_', job_name:'str') -> 'JobDetails':
    """ Returns the details of the job of the given name. The service name is read inside the session.
    """
    with closing(odb.session()) as session:
        job_row = session.query(Job).filter_by(name=job_name).first()

        if not job_row:
            raise ResubmitException(f'Job `{job_name}` was not found')

        out = JobDetails()
        out.id = job_row.id
        out.name = job_row.name
        out.service_name = job_row.service.name
        out.extra = job_row.extra

    return out

# ################################################################################################################################

def run_job(
    service:'any_',
    audit_log:'AuditLog',
    event:'StoredEvent',
    job:'JobDetails',
    payload:'any_',
    ) -> 'intnone':
    """ Runs one job's service the way the server runs it when the scheduler fires, with the run
    recorded from start to finish as its own event linked to the run it repeats. A failed run is
    recorded as one and raised.
    """
    cid = service.cid
    service_name = job.service_name
    planned_fire_time_iso = utcnow().isoformat()

    # The run's record opens now - its cid is the very cid the service runs under, so everything
    # the service touches downstream shares it and the run seeds the message flow ..
    new_event_id = record_job_start(
        audit_log,
        event.object_name,
        cid=cid,
        job_id=job.id,
        current_run=_manual_run_number,
        planned_fire_time_iso=planned_fire_time_iso,
        delay_ms=_manual_delay_ms,
        service=service_name,
        correl_id=event.cid,
        parents=[event.id],
    )

    # .. the service learns which run it belongs to ..
    zato_ctx = {
        'scheduler_job_id': job.id,
        'scheduler_current_run': _manual_run_number,
        'scheduler_audit_event_id': new_event_id,
    }

    outcome = SCHEDULER.OUTCOME.OK
    error_traceback = _empty
    invocation_start = monotonic()

    try:
        _ = service.server.invoke(service_name, payload, channel=CHANNEL.SCHEDULER, cid=cid, zato_ctx=zato_ctx)
    except Exception:
        outcome = SCHEDULER.OUTCOME.ERROR
        error_traceback = format_exc()

    elapsed_seconds = monotonic() - invocation_start
    duration_ms = int(elapsed_seconds * _milliseconds_per_second)

    # .. and the run's record closes with its outcome, duration and error.
    if new_event_id:
        record_job_complete(new_event_id, outcome=outcome, duration_ms=duration_ms, error=error_traceback)

    if outcome == SCHEDULER.OUTCOME.ERROR:
        raise ResubmitException(error_traceback)

    return new_event_id

# ################################################################################################################################
# ################################################################################################################################

class ReprocessSchedulerJob(AdminService):
    """ Runs the job recorded by a job-executed audit event once more - the job is read from the ODB
    by the name the event carries and its service is invoked with the job's extra data, the way the
    server invokes it when the scheduler fires. The run is recorded here as its own job-executed
    event linked to the original by the correlation id and the parent link.
    """
    name = 'zato.audit-log.scheduler.reprocess'
    input = Int('event_id'), '-actor'
    output = 'response_data'

    def handle(self) -> 'None':

        event_id = self.request.input.event_id

        # Who asked for the run - the empty string means the caller did not say.
        actor = self.request.input.actor

        # A failed run comes back as a report too, never as a bare exception,
        # so the caller always sees the same shape with the details inside.
        report:'stranydict' = {
            'is_ok': False,
            'is_duplicate': False,
            'event_id': None,
            'service_name': '',
            'error': '',
        }

        try:

            # The data column of a failed run holds a traceback, not a JSON document.
            event = load_event(event_id, is_raw_payload=True)
            require_event_type(event, AuditEvent.Job_Executed, 'run again')

            job = get_job_by_name(self.odb, event.object_name)

            service_name = job.service_name
            extra = job.extra

            payload = parse_job_extra(extra)

            audit_log = AuditLog(self.server.name)

            def resubmit_one() -> 'intnone':
                out = run_job(self, audit_log, event, job, payload)
                return out

            # The key covers the job and what its service is given.
            if extra is None:
                extra = _empty

            key_payload = f'{event.object_name}\n{extra}'

            new_event_id = run_once(Action_Reprocess, event_id, key_payload, self.cid, actor, resubmit_one)

            report['is_ok'] = True
            report['event_id'] = new_event_id
            report['service_name'] = service_name

        except DuplicateResubmitException as e:
            report['is_duplicate'] = True
            report['error'] = str(e)

        except Exception:
            report['error'] = format_exc()

        report['action'] = Action_Reprocess
        report['cid'] = self.cid

        self.response.payload.response_data = dumps(report)

# ################################################################################################################################
# ################################################################################################################################
