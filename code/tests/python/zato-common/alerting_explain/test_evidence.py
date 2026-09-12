# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone

# Zato
from zato.common.alerting.explain.evidence import build_evidence_document, build_prompt, fit_to_budget, group_failures, \
    render_alert, render_baseline, render_failures, render_object, Error_Text_Head_Chars, Error_Text_Tail_Chars, \
    Evidence_Budget_Chars, Heading_Alert, Heading_Baseline, Heading_Evidence, Heading_Failures, Heading_Object, \
    Max_Files_Per_Group
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource

# ################################################################################################################################
# ################################################################################################################################

_now = datetime(2026, 9, 11, 15, 45, 0, tzinfo=timezone.utc)

_conn_name = 'partner.acme.sftp'

# ################################################################################################################################
# ################################################################################################################################

def _row(row_id:'int', time_iso:'str', text:'str', endpoint:'str'='', status:'str'='') -> 'dict':
    out = {
        'id': row_id,
        'event_time_iso': time_iso,
        'event_type': AuditEvent.Message_Sent,
        'endpoint': endpoint,
        'outcome': AuditOutcome.Error,
        'status': status,
        'duration_ms': None,
        'data': text,
    }
    return out

# ################################################################################################################################

def _rows() -> 'list':
    """ The rows of the sample - newest first, three error texts.
    """
    denied = 'Permission denied (remote path /outbox/invoices)'
    reset = 'Connection reset by peer during write'
    timed_out = 'Connection timed out after 30s (sftp.acme.example.com:22)'

    out = [
        _row(90412, '2026-09-11T15:42:10+00:00', denied, '/outbox/invoices/INV-2291.xml'),
        _row(90398, '2026-09-11T15:27:08+00:00', denied, '/outbox/invoices/INV-2290.xml'),
        _row(90371, '2026-09-11T15:12:11+00:00', denied, '/outbox/invoices/INV-2289.xml'),
        _row(89820, '2026-09-11T03:12:05+00:00', reset, '/outbox/invoices/INV-2241.xml'),
        _row(89512, '2026-09-10T21:42:33+00:00', timed_out, '/outbox/invoices/INV-2213.xml'),
        _row(89498, '2026-09-10T21:27:30+00:00', timed_out, '/outbox/invoices/INV-2212.xml'),
    ]
    return out

# ################################################################################################################################

def _alert() -> 'dict':
    out = {
        'rule': 'Transfer_Failures',
        'severity': 'warning',
        'source': AuditSource.File_Outgoing,
        'object_name': _conn_name,
        'message': f'{_conn_name} - 12 failed transfers (12 of 50 over 86400s) (SFTP outgoing)',
        'fact': {
            'source': AuditSource.File_Outgoing,
            'object_name': _conn_name,
            'error_rate': 0.24,
            'error_count': 12,
            'total_count': 50,
            'window_seconds': 86400,
            'window_seconds_by_measure': {'error_rate': 86400},
            'consecutive_failures': 4,
            'outstanding': 0,
            'quarantined_in_window': 0,
        },
        'thresholds': {'warning_failure_count': 10, 'error_failure_count': 20},
        'measures': ['error_count'],
    }
    return out

# ################################################################################################################################

def _baseline() -> 'dict':
    out = {
        'ok_count': 38,
        'last_ok': {'event_time_iso': '2026-09-11T14:42:07+00:00', 'endpoint': '/outbox/invoices/INV-2287.xml'},
        'streak_count': 4,
        'streak_start_iso': '2026-09-11T14:57:09+00:00',
        'last_ok_before_streak': {'event_time_iso': '2026-09-11T14:42:07+00:00', 'endpoint': '/outbox/invoices/INV-2287.xml'},
        'test_transfers_on': False,
        'test_transfer': None,
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestGroupFailures:

    def test_identical_texts_are_grouped_newest_group_first(self) -> 'None':
        groups = group_failures(_rows())

        assert len(groups) == 3
        assert groups[0]['text'].startswith('Permission denied')
        assert groups[1]['text'].startswith('Connection reset')
        assert groups[2]['text'].startswith('Connection timed out')

    def test_a_group_counts_its_rows_and_spans_their_times(self) -> 'None':
        group = group_failures(_rows())[0]

        assert group['count'] == 3
        assert group['first_iso'] == '2026-09-11T15:12:11+00:00'
        assert group['last_iso'] == '2026-09-11T15:42:10+00:00'

    def test_a_group_lists_the_files_it_touched_newest_first(self) -> 'None':
        group = group_failures(_rows())[0]

        assert group['files'] == [
            '/outbox/invoices/INV-2291.xml',
            '/outbox/invoices/INV-2290.xml',
            '/outbox/invoices/INV-2289.xml',
        ]
        assert group['files_total'] == 3

    def test_a_row_without_data_is_grouped_by_its_status_then_its_type(self) -> 'None':
        rows = [
            _row(1, '2026-09-11T15:00:00+00:00', '', status='503'),
            _row(2, '2026-09-11T14:00:00+00:00', ''),
        ]

        groups = group_failures(rows)

        assert groups[0]['text'] == '503'
        assert groups[1]['text'] == AuditEvent.Message_Sent

    def test_no_rows_means_no_groups(self) -> 'None':
        assert group_failures([]) == []

# ################################################################################################################################
# ################################################################################################################################

class TestRenderFailures:

    def test_the_section_reads_as_in_the_sample(self) -> 'None':
        section = render_failures(group_failures(_rows()))

        assert section.startswith(Heading_Failures)
        assert 'Newest first. Identical errors are grouped' in section
        assert '1. Permission denied (remote path /outbox/invoices)' in section
        assert '   Count: 3, first 2026-09-11T15:12:11+00:00, last 2026-09-11T15:42:10+00:00' in section
        assert '   Files: /outbox/invoices/INV-2291.xml, /outbox/invoices/INV-2290.xml, /outbox/invoices/INV-2289.xml' in section
        assert '2. Connection reset by peer during write' in section
        assert '   Count: 1, at 2026-09-11T03:12:05+00:00' in section
        assert '   File: /outbox/invoices/INV-2241.xml' in section
        assert '3. Connection timed out' in section

    def test_no_groups_says_so(self) -> 'None':
        section = render_failures([])

        assert 'No failed events in the window.' in section

    def test_many_files_list_only_the_first_and_the_last(self) -> 'None':
        rows = []

        for index in range(Max_Files_Per_Group + 1):
            rows.append(_row(index, f'2026-09-11T15:{index:02d}:00+00:00', 'same error', f'/file-{index}.xml'))

        section = render_failures(group_failures(rows))

        assert f'File: /file-0.xml ... File: /file-{Max_Files_Per_Group}.xml ({Max_Files_Per_Group + 1} in all)' in section

# ################################################################################################################################
# ################################################################################################################################

class TestFitToBudget:

    def test_a_section_within_the_budget_is_untouched(self) -> 'None':
        groups = group_failures(_rows())

        section = fit_to_budget(groups, Evidence_Budget_Chars)

        assert section == render_failures(groups)
        assert 'Left out' not in section

    def test_the_oldest_groups_go_first(self) -> 'None':
        groups = group_failures(_rows())
        full = render_failures(groups)

        section = fit_to_budget(groups, len(full) - 1)

        assert 'Permission denied' in section
        assert 'Connection reset' in section
        assert 'Connection timed out' not in section
        assert section.rstrip().endswith('Left out: 1 older group left out to fit.')

    def test_then_the_file_lists_shrink(self) -> 'None':
        rows = []

        for index in range(4):
            rows.append(_row(index, f'2026-09-11T15:{index:02d}:00+00:00', 'same error', f'/a/very/long/path/to/file-{index}.xml'))

        groups = group_failures(rows)
        full = render_failures(groups)

        # One group only, so there is nothing older to drop - the files give way
        section = fit_to_budget(groups, len(full) - 1)

        assert 'File: /a/very/long/path/to/file-0.xml ... File: /a/very/long/path/to/file-3.xml (4 in all)' in section
        assert section.rstrip().endswith('Left out: file lists shortened to their first and last entries.')

    def test_then_the_texts_are_trimmed(self) -> 'None':
        long_text = 'E' * (Error_Text_Head_Chars + Error_Text_Tail_Chars + 500)
        groups = group_failures([_row(1, '2026-09-11T15:00:00+00:00', long_text)])

        section = fit_to_budget(groups, 200)

        head = 'E' * Error_Text_Head_Chars
        assert ('1. ' + head + ' ... ') in section
        assert long_text not in section

    def test_dropping_and_shrinking_are_both_named(self) -> 'None':
        rows = _rows()

        for index in range(Max_Files_Per_Group + 2):
            rows.insert(0, _row(1000 + index, f'2026-09-11T15:5{index % 10}:00+00:00', 'newest error', f'/n/file-{index}.xml'))

        groups = group_failures(rows)
        full = render_failures(groups)

        section = fit_to_budget(groups, len(full) // 2)

        assert 'Left out:' in section
        assert 'older group' in section

# ################################################################################################################################
# ################################################################################################################################

class TestRenderAlert:

    def test_the_section_reads_as_in_the_sample(self) -> 'None':
        section = render_alert(_alert(), _now)

        assert section.startswith(Heading_Alert)
        assert 'Rule: Transfer_Failures (warning)' in section
        assert f'Object: {_conn_name} (File transfer)' in section
        assert 'Measure: error_count = 12, threshold warning_failure_count = 10, error_failure_count = 20' in section
        assert 'Window: 86400 seconds, from 2026-09-10T15:45:00+00:00 to 2026-09-11T15:45:00+00:00' in section
        assert 'Also measured: error_rate = 0.24, total_count = 50, consecutive_failures = 4' in section
        assert f'Message: {_conn_name} - 12 failed transfers' in section

    def test_zero_measures_are_not_also_measured(self) -> 'None':
        section = render_alert(_alert(), _now)

        assert 'outstanding' not in section
        assert 'quarantined_in_window' not in section

    def test_a_reading_without_a_window_says_so(self) -> 'None':
        alert = _alert()
        alert['fact']['window_seconds'] = 0
        alert['thresholds'] = {}

        section = render_alert(alert, _now)

        assert 'Window: none, the measure is a reading taken at the time of the sweep' in section
        assert 'threshold' not in section

    def test_a_measure_with_a_window_of_its_own_names_it(self) -> 'None':
        alert = _alert()
        alert['fact']['window_seconds_by_measure'] = {'error_rate': 86400, 'auth_failures': 3600, 'latency': 86400}

        section = render_alert(alert, _now)

        assert 'Window: 86400 seconds' in section
        assert 'Windows of their own: auth_failures = 3600 seconds' in section
        assert 'latency = 86400' not in section

    def test_measures_over_the_one_window_have_no_windows_of_their_own(self) -> 'None':
        section = render_alert(_alert(), _now)

        assert 'Windows of their own' not in section

# ################################################################################################################################
# ################################################################################################################################

def _channel_row(row_id:'int', time_iso:'str', status:'str', text:'str', service:'str', caller:'str') -> 'dict':
    """ One failed response a REST channel sent - the status it answered with, the service that answered
    and the caller that asked.
    """
    out = _row(row_id, time_iso, text, service, status)
    out['event_type'] = AuditEvent.Response_Sent
    out['ext_client_id'] = caller
    return out

# ################################################################################################################################

def _channel_rows() -> 'list':
    """ The rows of a channel sample - newest first, two callers rejected with a 401, one 500 from the service.
    """
    unauthorized = 'Invalid API key'
    failed = 'KeyError: customer_id'

    out = [
        _channel_row(501, '2026-09-11T15:42:10+00:00', '401 Unauthorized', unauthorized, 'orders.get', 'partner-a'),
        _channel_row(498, '2026-09-11T15:41:08+00:00', '401 Unauthorized', unauthorized, 'orders.get', 'partner-b'),
        _channel_row(471, '2026-09-11T15:40:11+00:00', '401 Unauthorized', unauthorized, 'orders.get', 'partner-a'),
        _channel_row(420, '2026-09-11T15:12:05+00:00', '500 Internal Server Error', failed, 'orders.get', 'partner-c'),
        _channel_row(419, '2026-09-11T15:11:05+00:00', '500 Internal Server Error', '', 'orders.get', 'partner-c'),
    ]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestChannelFailures:

    def test_a_channels_groups_are_keyed_by_status_and_text_together(self) -> 'None':
        groups = group_failures(_channel_rows(), AuditSource.REST_Channel)

        assert len(groups) == 3
        assert groups[0]['text'] == '401 Unauthorized - Invalid API key'
        assert groups[1]['text'] == '500 Internal Server Error - KeyError: customer_id'
        assert groups[2]['text'] == '500 Internal Server Error'

    def test_a_group_names_each_service_and_caller_once(self) -> 'None':
        group = group_failures(_channel_rows(), AuditSource.REST_Channel)[0]

        assert group['count'] == 3
        assert group['files'] == ['orders.get']
        assert group['files_total'] == 1
        assert group['callers'] == ['partner-a', 'partner-b']

    def test_the_section_speaks_of_services_and_callers(self) -> 'None':
        groups = group_failures(_channel_rows(), AuditSource.REST_Channel)
        section = render_failures(groups, source=AuditSource.REST_Channel)

        assert '1. 401 Unauthorized - Invalid API key' in section
        assert '   Count: 3, first 2026-09-11T15:40:11+00:00, last 2026-09-11T15:42:10+00:00' in section
        assert '   Service: orders.get' in section
        assert '   Callers: partner-a, partner-b' in section
        assert '   Caller: partner-c' in section
        assert 'File' not in section

    def test_two_services_are_listed_as_services(self) -> 'None':
        rows = [
            _channel_row(2, '2026-09-11T15:42:10+00:00', '500', 'boom', 'orders.get', 'partner-a'),
            _channel_row(1, '2026-09-11T15:41:10+00:00', '500', 'boom', 'orders.list', 'partner-a'),
        ]

        section = render_failures(group_failures(rows, AuditSource.REST_Channel), source=AuditSource.REST_Channel)

        assert '   Services: orders.get, orders.list' in section
        assert '   Caller: partner-a' in section

    def test_a_channels_groups_shrink_to_their_first_and_last_names(self) -> 'None':
        rows = []

        for index in range(Max_Files_Per_Group + 1):
            rows.append(_channel_row(index, f'2026-09-11T15:{index:02d}:00+00:00', '500', 'boom', f'svc-{index}', f'caller-{index}'))

        groups = group_failures(rows, AuditSource.REST_Channel)
        full = render_failures(groups, source=AuditSource.REST_Channel)

        assert f'Service: svc-0 ... Service: svc-{Max_Files_Per_Group} ({Max_Files_Per_Group + 1} in all)' in full
        assert f'Caller: caller-0 ... Caller: caller-{Max_Files_Per_Group} ({Max_Files_Per_Group + 1} in all)' in full

        section = fit_to_budget(groups, len(full) - 1, AuditSource.REST_Channel)

        assert section.rstrip().endswith('Left out: service and caller lists shortened to their first and last entries.')

    def test_a_file_transfers_groups_carry_no_callers_and_no_status_prefix(self) -> 'None':
        groups = group_failures(_rows())

        assert groups[0]['callers'] == []
        assert groups[0]['text'] == 'Permission denied (remote path /outbox/invoices)'

# ################################################################################################################################
# ################################################################################################################################

class TestRenderObject:

    def test_each_pair_is_one_line(self) -> 'None':
        section = render_object([('Name', _conn_name), ('Active', 'yes'), ('Host', 'sftp.acme.example.com')])

        assert section == f'{Heading_Object}\n\nName: {_conn_name}\nActive: yes\nHost: sftp.acme.example.com'

# ################################################################################################################################
# ################################################################################################################################

class TestRenderBaseline:

    def test_the_section_reads_as_in_the_sample(self) -> 'None':
        section = render_baseline(_baseline())

        assert section.startswith(Heading_Baseline)
        assert 'OK events in the window: 38' in section
        assert 'Last OK event: 2026-09-11T14:42:07+00:00 (/outbox/invoices/INV-2287.xml)' in section
        assert 'Current failure streak: 4, since 2026-09-11T14:57:09+00:00, last OK before it 2026-09-11T14:42:07+00:00' in section
        assert 'Test transfer result: not run, test transfers are off for this connection' in section

    def test_no_successes_and_no_streak_are_said_plainly(self) -> 'None':
        baseline = _baseline()
        baseline['ok_count'] = 0
        baseline['last_ok'] = None
        baseline['streak_count'] = 0

        section = render_baseline(baseline)

        assert 'Last OK event: none in the window' in section
        assert 'Current failure streak: none, the newest event succeeded' in section

    def test_a_test_transfer_result_is_shown_when_they_are_on(self) -> 'None':
        baseline = _baseline()
        baseline['test_transfers_on'] = True
        baseline['test_transfer'] = {'outcome': 'error', 'event_time_iso': '2026-09-11T15:30:00+00:00', 'data': 'Permission denied'}

        section = render_baseline(baseline)

        assert 'Test transfer result: error at 2026-09-11T15:30:00+00:00 (Permission denied)' in section

    def test_test_transfers_on_without_a_result_yet(self) -> 'None':
        baseline = _baseline()
        baseline['test_transfers_on'] = True

        section = render_baseline(baseline)

        assert 'Test transfer result: none on record yet' in section

# ################################################################################################################################
# ################################################################################################################################

class TestBuildEvidenceDocument:

    def test_the_four_sections_come_in_order_under_the_heading(self) -> 'None':
        document = build_evidence_document(_alert(), [('Name', _conn_name)], group_failures(_rows()), _baseline(), _now)

        assert document.startswith(Heading_Evidence + '\n\n' + Heading_Alert)

        positions = [
            document.index(Heading_Alert),
            document.index(Heading_Object),
            document.index(Heading_Failures),
            document.index(Heading_Baseline),
        ]

        assert positions == sorted(positions)
        assert len(document) <= Evidence_Budget_Chars

    def test_only_the_failures_give_way_to_the_budget(self) -> 'None':
        rows = []

        for index in range(400):
            text = f'Error number {index} ' + ('x' * 100)
            rows.append(_row(index, f'2026-09-11T{index % 24:02d}:{index % 60:02d}:00+00:00', text, f'/file-{index}.xml'))

        document = build_evidence_document(_alert(), [('Name', _conn_name)], group_failures(rows), _baseline(), _now)

        assert len(document) <= Evidence_Budget_Chars
        assert 'Left out:' in document

        # The other sections are whole
        assert 'OK events in the window: 38' in document
        assert f'Message: {_conn_name} - 12 failed transfers' in document
        assert f'Name: {_conn_name}' in document

# ################################################################################################################################
# ################################################################################################################################

class TestBuildPrompt:

    def test_the_instructions_come_first_and_the_document_after_one_blank_line(self) -> 'None':
        document = build_evidence_document(_alert(), [('Name', _conn_name)], [], _baseline(), _now)

        prompt = build_prompt('# Skill\n\nRead the evidence.\n\n', document)

        assert prompt == '# Skill\n\nRead the evidence.\n\n' + document
        assert prompt.count(Heading_Evidence) == 1

# ################################################################################################################################
# ################################################################################################################################
