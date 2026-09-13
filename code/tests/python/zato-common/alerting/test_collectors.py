# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta
from json import dumps

# Zato
from zato.common.alerting.collectors import collect_facts, collect_file_transfer_facts, Health_Window_Seconds, Measure_Error_Rate
from zato.common.audit_log.api import get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.file_transfer_run import Run_Status_Failed
from zato.common.monitoring.health import EndpointMetrics
from zato.common.util.api import utcnow

# Local
from conftest import backdate, seed_outcome, Channel_Name, Other_Channel_Name, Server_Name

# ################################################################################################################################
# ################################################################################################################################

class TestPerSourceWindows:

    def test_a_source_with_a_window_of_its_own_is_measured_over_it(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # A file transfer error older than the default window but within
        # the file transfer type's own longer one
        event_id = audit_log.insert(AuditSource.File_Outgoing, AuditEvent.Message_Sent, 'sftp.backups',
            cid='window-1', outcome=AuditOutcome.Error)
        backdate(event_id, now - timedelta(seconds=400))

        facts = collect_facts(engine, {}, AuditSource.MLLP_Channel, now,
            window_seconds=300, window_seconds_by_source={AuditSource.File_Outgoing: {Measure_Error_Rate: 600}})

        by_name = {fact['object_name']: fact for fact in facts}

        assert by_name['sftp.backups']['error_count'] == 1
        assert by_name['sftp.backups']['window_seconds'] == 600

# ################################################################################################################################

    def test_a_source_without_a_window_of_its_own_is_measured_over_the_default(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        event_id = audit_log.insert(AuditSource.File_Outgoing, AuditEvent.Message_Sent, 'sftp.default-window',
            cid='window-2', outcome=AuditOutcome.Error)
        backdate(event_id, now - timedelta(seconds=400))

        # No per-source windows at all, so every source is measured over the one default
        facts = collect_facts(engine, {}, AuditSource.MLLP_Channel, now, window_seconds=300)

        by_name = {fact['object_name']: fact for fact in facts}

        assert by_name['sftp.default-window']['error_count'] == 0
        assert by_name['sftp.default-window']['window_seconds'] == 0

# ################################################################################################################################

    def test_the_health_sources_keep_their_hour_unless_a_rule_names_them(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # A failed health check older than the default window but within the hour - a check's ping is
        # measured through its response, the way the connection's own traffic is
        event_id = audit_log.insert(AuditSource.REST_Outgoing_Health, AuditEvent.Response_Received, 'crm.health',
            cid='window-3', outcome=AuditOutcome.Error)
        backdate(event_id, now - timedelta(seconds=1800))

        facts = collect_facts(engine, {}, AuditSource.MLLP_Channel, now, window_seconds=300)

        by_name = {fact['object_name']: fact for fact in facts}

        assert by_name['crm.health']['error_count'] == 1
        assert by_name['crm.health']['window_seconds'] == Health_Window_Seconds

# ################################################################################################################################

    def test_the_run_counts_of_a_schedule_cover_the_file_transfer_window(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # A failed run half an hour back
        run_data = dumps({'schedule': 'sched.window', 'failed': 2})
        event_id = audit_log.insert(AuditSource.File_Outgoing, AuditEvent.Run_Completed, 'sftp.runs',
            cid='window-4', outcome=AuditOutcome.Error, status=Run_Status_Failed, data=run_data)
        backdate(event_id, now - timedelta(seconds=1800))

        # Over a day it counts ..
        facts = collect_file_transfer_facts(engine, now, {}, None, 86400)
        by_name = {fact['object_name']: fact for fact in facts}

        assert by_name['sched.window']['runs_failed_in_window'] == 1
        assert by_name['sched.window']['failed_files_in_window'] == 2

        # .. over ten minutes it does not, while the newest status still speaks.
        facts = collect_file_transfer_facts(engine, now, {}, None, 600)
        by_name = {fact['object_name']: fact for fact in facts}

        assert by_name['sched.window']['runs_failed_in_window'] == 0
        assert by_name['sched.window']['failed_files_in_window'] == 0
        assert by_name['sched.window']['last_run_status'] == Run_Status_Failed

# ################################################################################################################################

    def test_a_schedule_with_a_window_of_its_own_is_counted_over_it(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # A failed run half an hour back for two schedules
        for schedule_name, cid in [('sched.own-window', 'window-5'), ('sched.type-window', 'window-6')]:
            run_data = dumps({'schedule': schedule_name, 'failed': 1})
            event_id = audit_log.insert(AuditSource.File_Outgoing, AuditEvent.Run_Completed, 'sftp.runs',
                cid=cid, outcome=AuditOutcome.Error, status=Run_Status_Failed, data=run_data)
            backdate(event_id, now - timedelta(seconds=1800))

        # The type counts over ten minutes, one schedule over a day of its own
        facts = collect_file_transfer_facts(engine, now, {}, None, 600, {'sched.own-window': 86400})
        by_name = {fact['object_name']: fact for fact in facts}

        assert by_name['sched.own-window']['runs_failed_in_window'] == 1
        assert by_name['sched.type-window']['runs_failed_in_window'] == 0

        # And the other way round - the type over a day, the schedule over ten minutes
        facts = collect_file_transfer_facts(engine, now, {}, None, 86400, {'sched.own-window': 600})
        by_name = {fact['object_name']: fact for fact in facts}

        assert by_name['sched.own-window']['runs_failed_in_window'] == 0
        assert by_name['sched.type-window']['runs_failed_in_window'] == 1

# ################################################################################################################################

    def test_an_object_with_a_window_of_its_own_has_its_rate_measured_over_it(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # A failure twenty minutes back for two connections
        for object_name, cid in [('sftp.own-window', 'window-7'), ('sftp.type-window', 'window-8')]:
            event_id = audit_log.insert(AuditSource.File_Outgoing, AuditEvent.Message_Sent, object_name,
                cid=cid, outcome=AuditOutcome.Error)
            backdate(event_id, now - timedelta(seconds=1200))

        # The source is measured over ten minutes, one connection over an hour of its own
        window_seconds_by_object = {AuditSource.File_Outgoing: {'sftp.own-window': {Measure_Error_Rate: 3600}}}

        facts = collect_facts(engine, {}, AuditSource.MLLP_Channel, now, window_seconds=300,
            window_seconds_by_source={AuditSource.File_Outgoing: {Measure_Error_Rate: 600}},
            window_seconds_by_object=window_seconds_by_object)

        by_name = {fact['object_name']: fact for fact in facts}

        assert by_name['sftp.own-window']['error_count'] == 1
        assert by_name['sftp.own-window']['window_seconds'] == 3600
        assert by_name['sftp.type-window']['error_count'] == 0

# ################################################################################################################################
# ################################################################################################################################

class TestCollectFacts:

    def test_the_measures_of_one_object_merge_into_one_fact(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # The same channel errors and sits silent at the same time
        seed_outcome(audit_log, 'facts-merge-1', AuditOutcome.Error)

        metrics = EndpointMetrics()
        metrics.silence_seconds = 1200.0
        metrics_by_name = {Channel_Name: metrics}

        facts = collect_facts(engine, metrics_by_name, AuditSource.MLLP_Channel, now)

        assert len(facts) == 1

        fact = facts[0]
        assert fact['error_rate'] == 1.0
        assert fact['total_count'] == 1
        assert fact['silent_seconds'] == 1200
        assert fact['outstanding'] == 0

# ################################################################################################################################

    def test_different_objects_stay_apart(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        seed_outcome(audit_log, 'facts-apart-1', AuditOutcome.Error)

        metrics = EndpointMetrics()
        metrics.silence_seconds = 700.0
        metrics_by_name = {Other_Channel_Name: metrics}

        facts = collect_facts(engine, metrics_by_name, AuditSource.MLLP_Channel, now)
        by_name = {fact['object_name']: fact for fact in facts}

        assert len(facts) == 2
        assert by_name[Channel_Name]['error_rate'] == 1.0
        assert by_name[Channel_Name]['silent_seconds'] == 0
        assert by_name[Other_Channel_Name]['silent_seconds'] == 700
        assert by_name[Other_Channel_Name]['error_rate'] == 0.0

# ################################################################################################################################
# ################################################################################################################################
