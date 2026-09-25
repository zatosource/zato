# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# SQLAlchemy
from sqlalchemy.orm.exc import DetachedInstanceError

# Zato
from zato.common.api import CHANNEL, SCHEDULER
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditSource
from zato.common.audit_log.resubmit import source_resubmit_actions, is_event_type_resubmittable
from zato.common.audit_log.scheduler import record_job_complete, record_job_start
from zato.common.ext.bunch import Bunch
from zato.common.odb.model import Job
from zato.common.typing_ import cast_
from zato.common.util.api import utcnow
from zato.server.service.internal.audit_log_scheduler import get_job_by_name, ReprocessSchedulerJob

# Test support
from audit_env import audit_db_env, events_of_type, get_events, get_parents, Server_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The name of the service the resubmit catalog points job runs at.
Reprocess_Service = 'zato.audit-log.scheduler.reprocess'

# The cid the reprocess itself runs with.
Reprocess_Cid = 'cid-scheduler-reprocess-1'

# The job whose run is repeated, as the ODB knows it.
Job_Id = 17
Job_Name = 'audit.test.scheduler.job'
Job_Service = 'audit.test.scheduler.target'
Job_Extra = 'region=us-east\nbatch_size=50'

# The run that is repeated.
Original_Cid = 'cid-scheduler-original-1'
Original_Run = 3

# What the failing target says.
Reprocess_Error = 'The target service is still down'

# ################################################################################################################################
# ################################################################################################################################

class ServerStub:
    """ Stands in for the server the reprocess service runs on - it remembers
    what the job's service was invoked with.
    """

    def __init__(self) -> 'None':
        self.name = Server_Name
        self.invoked:'anylist' = []

    def invoke(self, service_name:'str', payload:'any_', **kwargs:'any_') -> 'None':
        self.invoked.append((service_name, payload, kwargs))

# ################################################################################################################################

class FailingServerStub(ServerStub):
    """ A server whose target service is still down - every invocation fails.
    """

    def invoke(self, service_name:'str', payload:'any_', **kwargs:'any_') -> 'None':
        raise Exception(Reprocess_Error)

# ################################################################################################################################

class JobRowStub:
    """ Stands in for one ODB job row - its service is a lazy relationship, so it loads only
    while the session the row came from is still open, the way the real ORM row behaves.
    """

    def __init__(self, session:'SessionStub', extra:'any_') -> 'None':
        self.session = session
        self.id = Job_Id
        self.name = Job_Name
        self.extra = extra

    @property
    def service(self) -> 'Bunch':
        if not self.session.is_open:
            raise DetachedInstanceError('Parent instance is not bound to a Session, lazy load of `service` cannot proceed')

        if self.session.is_expunged(self):
            raise DetachedInstanceError('Parent instance was expunged, lazy load of `service` cannot proceed')

        out = Bunch(name=Job_Service)
        return out

# ################################################################################################################################

class QueryStub:
    """ Stands in for one ODB query over the job table - it answers by name.
    """

    def __init__(self, session:'SessionStub') -> 'None':
        self.session = session
        self.name = ''

    def filter_by(self, name:'str') -> 'QueryStub':
        self.name = name
        return self

    def first(self) -> 'any_':
        if self.name in self.session.jobs:
            out = JobRowStub(self.session, self.session.jobs[self.name])
        else:
            out = None

        return out

# ################################################################################################################################

class SessionStub:
    """ Stands in for one ODB session - the reprocess reads one job row through it, and a row
    the session gave out stops loading its relationships once the session is closed.
    """

    def __init__(self, jobs:'stranydict') -> 'None':
        self.jobs = jobs
        self.is_open = True
        self.expunged:'anylist' = []

    def query(self, model:'any_') -> 'QueryStub':
        out = QueryStub(self)
        return out

    def expunge(self, row:'any_') -> 'None':
        self.expunged.append(row)

    def is_expunged(self, row:'any_') -> 'bool':
        out = row in self.expunged
        return out

    def close(self) -> 'None':
        self.is_open = False

# ################################################################################################################################

class ODBStub:
    """ Stands in for the ODB - it holds the jobs by name, each with its extra data.
    """

    def __init__(self, jobs:'stranydict') -> 'None':
        self.jobs = jobs

    def session(self) -> 'SessionStub':
        out = SessionStub(self.jobs)
        return out

# ################################################################################################################################
# ################################################################################################################################

def _new_odb(extra:'any_'=Job_Extra) -> 'ODBStub':
    """ An ODB holding the one job the tests repeat.
    """
    jobs = {Job_Name: extra}
    out = ODBStub(jobs)

    return out

# ################################################################################################################################

def _seed_original_run(*, outcome:'str') -> 'int':
    """ One recorded run of the job, completed with the given outcome - what the reprocess reads back.
    """
    audit_log = AuditLog(Server_Name)

    planned_fire_time_iso = utcnow().isoformat()

    event_id = cast_('int', record_job_start(
        audit_log,
        Job_Name,
        cid=Original_Cid,
        job_id=Job_Id,
        current_run=Original_Run,
        planned_fire_time_iso=planned_fire_time_iso,
        delay_ms=5,
        service=Job_Service,
    ))

    if outcome == SCHEDULER.OUTCOME.ERROR:
        error = 'Traceback (most recent call last):\nException: The first run failed'
    else:
        error = ''

    record_job_complete(event_id, outcome=outcome, duration_ms=12, error=error)

    return event_id

# ################################################################################################################################

def _run_reprocess(event_id:'int', server:'ServerStub', odb:'ODBStub', *, actor:'str'='') -> 'stranydict':
    """ Runs the reprocess service over one stored event and returns the report it produced.
    """
    harness = Bunch()
    harness.cid = Reprocess_Cid
    harness.server = server
    harness.odb = odb
    harness.request = Bunch(input=Bunch(event_id=event_id, actor=actor))
    harness.response = Bunch(payload=Bunch())

    ReprocessSchedulerJob.handle(cast_('any_', harness))

    out = loads(harness.response.payload.response_data)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_the_catalog_offers_reprocess_for_job_runs() -> 'None':
    """ The catalog offers reprocess for job runs.
    """
    actions = source_resubmit_actions[AuditSource.Scheduler]

    assert actions[AuditEvent.Job_Executed]['service'] == Reprocess_Service
    assert is_event_type_resubmittable(AuditSource.Scheduler, AuditEvent.Job_Executed)

# ################################################################################################################################

def test_the_job_is_read_whole_while_its_session_is_open() -> 'None':
    """ The job's service is a lazy relationship - it is read inside the session and handed
    back as a plain value, so nothing is loaded off a detached row afterwards.
    """
    odb = _new_odb()

    job = get_job_by_name(odb, Job_Name)

    assert job.id == Job_Id
    assert job.name == Job_Name
    assert job.service_name == Job_Service
    assert job.extra == Job_Extra

    # A lazy load off a closed session is refused.
    session = odb.session()
    row = session.query(Job).filter_by(name=Job_Name).first()
    session.close()

    try:
        _ = row.service
    except DetachedInstanceError:
        pass
    else:
        raise Exception('A lazy load off a closed session was expected to be refused')

# ################################################################################################################################

def test_a_reprocess_runs_the_job_as_a_linked_run(tmp_path:'any_') -> 'None':
    """ A reprocess invokes the job's service with the job's extra data and leaves the new run
    as its own event linked to the original one.
    """
    with audit_db_env(tmp_path):

        original_id = _seed_original_run(outcome=SCHEDULER.OUTCOME.ERROR)

        server = ServerStub()
        report = _run_reprocess(original_id, server, _new_odb(), actor='audit.operator')

        assert report['is_ok'] is True
        assert report['is_duplicate'] is False
        assert report['cid'] == Reprocess_Cid
        assert report['action'] == 'reprocess'
        assert report['service_name'] == Job_Service

        # The job's service received the job's extra data, parsed the way a live run parses it ..
        assert len(server.invoked) == 1

        service_name, payload, kwargs = server.invoked[0]

        assert service_name == Job_Service
        assert payload == {'region': 'us-east', 'batch_size': '50'}
        assert kwargs['channel'] == CHANNEL.SCHEDULER
        assert kwargs['cid'] == Reprocess_Cid

        # .. and it learned which run it belongs to, so its log lines are captured the way a live run's are.
        zato_ctx = kwargs['zato_ctx']

        assert zato_ctx['scheduler_job_id'] == Job_Id
        assert zato_ctx['scheduler_current_run'] == 0
        assert zato_ctx['scheduler_audit_event_id'] == report['event_id']

        # The new run is its own event, sharing the original run's correlation id
        # and naming the original event as its parent ..
        events = get_events()
        job_events = events_of_type(events, AuditEvent.Job_Executed)

        assert len(job_events) == 2

        new_event = job_events[1]

        assert new_event['id'] == report['event_id']
        assert new_event['source'] == AuditSource.Scheduler
        assert new_event['object_name'] == Job_Name
        assert new_event['endpoint'] == Job_Service
        assert new_event['cid'] == Reprocess_Cid
        assert new_event['correl_id'] == Original_Cid
        assert new_event['outcome'] == SCHEDULER.OUTCOME.OK

        assert get_parents(new_event['id']) == [original_id]

        # .. while the original is left as it was.
        assert job_events[0]['id'] == original_id
        assert job_events[0]['correl_id'] == ''
        assert job_events[0]['outcome'] == SCHEDULER.OUTCOME.ERROR

# ################################################################################################################################

def test_a_failed_reprocess_is_recorded_as_an_error_run(tmp_path:'any_') -> 'None':
    """ A reprocess whose service is still down comes back as a report with the error inside,
    and the failed run is on record with the same links and the traceback.
    """
    with audit_db_env(tmp_path):

        original_id = _seed_original_run(outcome=SCHEDULER.OUTCOME.ERROR)

        report = _run_reprocess(original_id, FailingServerStub(), _new_odb())

        assert report['is_ok'] is False
        assert report['is_duplicate'] is False
        assert Reprocess_Error in report['error']

        events = get_events()
        job_events = events_of_type(events, AuditEvent.Job_Executed)

        assert len(job_events) == 2

        failed = job_events[1]

        assert failed['cid'] == Reprocess_Cid
        assert failed['correl_id'] == Original_Cid
        assert failed['outcome'] == SCHEDULER.OUTCOME.ERROR
        assert Reprocess_Error in failed['data']

        assert get_parents(failed['id']) == [original_id]

        # A failed run released its key, so the run can be asked for again ..
        server = ServerStub()
        second_report = _run_reprocess(original_id, server, _new_odb())

        assert second_report['is_ok'] is True
        assert len(server.invoked) == 1

        # .. and one that went through is not run twice.
        third_report = _run_reprocess(original_id, server, _new_odb())

        assert third_report['is_ok'] is False
        assert third_report['is_duplicate'] is True
        assert len(server.invoked) == 1

# ################################################################################################################################

def test_a_job_without_extra_hands_its_service_nothing(tmp_path:'any_') -> 'None':
    """ A job with no extra data invokes its service with what the ODB holds.
    """
    with audit_db_env(tmp_path):

        original_id = _seed_original_run(outcome=SCHEDULER.OUTCOME.OK)

        server = ServerStub()
        report = _run_reprocess(original_id, server, _new_odb(extra=None))

        assert report['is_ok'] is True

        _, payload, _ = server.invoked[0]
        assert payload is None

# ################################################################################################################################

def test_a_job_the_odb_no_longer_has_refuses(tmp_path:'any_') -> 'None':
    """ A run of a job that was deleted since cannot be repeated and the report says so.
    """
    with audit_db_env(tmp_path):

        original_id = _seed_original_run(outcome=SCHEDULER.OUTCOME.OK)

        server = ServerStub()
        report = _run_reprocess(original_id, server, ODBStub({}))

        assert report['is_ok'] is False
        assert 'was not found' in report['error']
        assert server.invoked == []

        # Nothing was recorded either.
        events = get_events()
        job_events = events_of_type(events, AuditEvent.Job_Executed)
        assert len(job_events) == 1

# ################################################################################################################################

def test_only_job_runs_can_be_reprocessed(tmp_path:'any_') -> 'None':
    """ An event of another type under the scheduler is not a run - asking to repeat one refuses.
    """
    with audit_db_env(tmp_path):

        audit_log = AuditLog(Server_Name)
        other_id = audit_log.insert(AuditSource.Scheduler, AuditEvent.Service_Request, Job_Name, cid='cid-scheduler-other')

        server = ServerStub()
        report = _run_reprocess(other_id, server, _new_odb())

        assert report['is_ok'] is False
        assert 'can be run again' in report['error']
        assert server.invoked == []

# ################################################################################################################################
# ################################################################################################################################
