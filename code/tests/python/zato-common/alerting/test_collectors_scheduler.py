# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# Zato
from zato.common.alerting.collectors import collect_facts, collect_file_transfer_facts, collect_scheduler_facts, Measure_File_Runs
from zato.common.audit_log.api import get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.scheduler import Attr_Delay_Ms
from zato.common.util.api import utcnow

# Local
from conftest import backdate, Server_Name, Window_Seconds

# ################################################################################################################################
# ################################################################################################################################

class TestSchedulerFacts:

    def test_the_worst_start_delay_of_the_window_speaks(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        _ = audit_log.insert(AuditSource.Scheduler, AuditEvent.Job_Executed, 'billing.sync',
            cid='sched-1', outcome=AuditOutcome.OK, attrs={Attr_Delay_Ms: 1200})
        _ = audit_log.insert(AuditSource.Scheduler, AuditEvent.Job_Executed, 'billing.sync',
            cid='sched-2', outcome=AuditOutcome.OK, attrs={Attr_Delay_Ms: 7400})

        facts = collect_scheduler_facts(engine, Window_Seconds, now, {})

        assert len(facts) == 1
        assert facts[0]['object_name'] == 'billing.sync'
        assert facts[0]['start_delay_ms'] == 7400

# ################################################################################################################################

    def test_the_overdue_ratio_sizes_itself_against_the_jobs_own_interval(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # A job that last ran twenty minutes ago, on a five-minute interval
        event_id = audit_log.insert(AuditSource.Scheduler, AuditEvent.Job_Executed, 'billing.sync',
            cid='overdue-1', outcome=AuditOutcome.OK)
        backdate(event_id, now - timedelta(seconds=1200))

        facts = collect_scheduler_facts(engine, Window_Seconds, now, {'billing.sync': 300})

        assert len(facts) == 1
        assert facts[0]['overdue_ratio'] == 4.0

# ################################################################################################################################

    def test_a_job_without_an_interval_has_no_notion_of_being_overdue(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        event_id = audit_log.insert(AuditSource.Scheduler, AuditEvent.Job_Executed, 'one.time.job',
            cid='onetime-1', outcome=AuditOutcome.OK)
        backdate(event_id, now - timedelta(seconds=1200))

        facts = collect_scheduler_facts(engine, Window_Seconds, now, {})

        assert facts == []

# ################################################################################################################################
# ################################################################################################################################

class TestFileTransferArrivalFacts:

    # The schedules whose arrivals the tests measure
    _schedule_name = 'Daily results'
    _other_schedule_name = 'Hourly exports'

    # The connection the delivered events are written under
    _file_connection_name = 'sftp.backups'

# ################################################################################################################################

    def _seed_arrival(self, audit_log:'AuditLog', cid:'str', *, schedule:'str'='') -> 'int':
        """ Stores one delivered event of the kind a file transfer schedule writes
        when it hands a file to its target service.
        """
        if not schedule:
            schedule = self._schedule_name

        out = audit_log.insert(AuditSource.File_Outgoing, AuditEvent.Delivered, self._file_connection_name,
            cid=cid, outcome=AuditOutcome.OK, attrs={'schedule': schedule})

        return out

# ################################################################################################################################

    def test_the_time_since_the_newest_arrival_is_measured(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # An older arrival and a newer one - only the newer one sets the measure
        older_id = self._seed_arrival(audit_log, 'arrival-1')
        newer_id = self._seed_arrival(audit_log, 'arrival-2')

        backdate(older_id, now - timedelta(seconds=1200))
        backdate(newer_id, now - timedelta(seconds=600))

        # A five-minute window, so the newest arrival is twice as old as expected
        facts = collect_file_transfer_facts(engine, now, {self._schedule_name: 300})

        assert len(facts) == 1

        fact = facts[0]
        assert fact['source'] == AuditSource.File_Outgoing
        assert fact['object_name'] == self._schedule_name
        assert fact['seconds_since_last_arrival'] == 600
        assert fact['arrival_overdue_ratio'] == 2.0

# ################################################################################################################################

    def test_a_schedule_without_a_window_declares_no_expectation(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        event_id = self._seed_arrival(audit_log, 'arrival-no-window-1')
        backdate(event_id, now - timedelta(seconds=3600))

        # No window on record for this schedule, so it is never measured
        facts = collect_file_transfer_facts(engine, now, {self._other_schedule_name: 300})

        assert facts == []

# ################################################################################################################################

    def test_a_schedule_that_never_delivered_has_no_baseline(self) -> 'None':
        engine = get_audit_engine()
        now = utcnow()

        # A window is declared but nothing ever arrived - there is nothing to be overdue against
        facts = collect_file_transfer_facts(engine, now, {self._schedule_name: 300})

        assert facts == []

# ################################################################################################################################

    def test_each_schedule_measures_against_its_own_window(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # Two schedules whose newest arrivals are equally old ..
        first_id = self._seed_arrival(audit_log, 'arrival-own-1')
        second_id = self._seed_arrival(audit_log, 'arrival-own-2', schedule=self._other_schedule_name)

        backdate(first_id, now - timedelta(seconds=600))
        backdate(second_id, now - timedelta(seconds=600))

        # .. but whose windows differ, so their ratios differ too
        arrival_windows = {
            self._schedule_name: 300,
            self._other_schedule_name: 1200,
        }

        facts = collect_file_transfer_facts(engine, now, arrival_windows)
        by_name = {fact['object_name']: fact for fact in facts}

        assert len(facts) == 2
        assert by_name[self._schedule_name]['arrival_overdue_ratio'] == 2.0
        assert by_name[self._other_schedule_name]['arrival_overdue_ratio'] == 0.5

# ################################################################################################################################

    def test_the_facts_flow_through_collect_facts(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        event_id = self._seed_arrival(audit_log, 'arrival-flow-1')
        backdate(event_id, now - timedelta(seconds=900))

        facts = collect_facts(engine, {}, AuditSource.MLLP_Channel, now,
            window_seconds_by_source={AuditSource.File_Outgoing: {Measure_File_Runs: 86400}},
            arrival_windows={self._schedule_name: 300})

        by_name = {fact['object_name']: fact for fact in facts}

        assert by_name[self._schedule_name]['seconds_since_last_arrival'] == 900
        assert by_name[self._schedule_name]['arrival_overdue_ratio'] == 3.0

# ################################################################################################################################
# ################################################################################################################################
