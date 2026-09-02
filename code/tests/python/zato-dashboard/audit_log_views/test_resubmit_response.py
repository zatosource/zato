# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A resubmit answers display-ready - a one-line summary for the tippy, the details
# for the modal and the lexer they highlight with, all built out of the report
# the service produced. The frontend renders this as-is, without any string surgery.

# stdlib
from json import loads

# Zato
from zato.admin.web.views import Action_Message_Max_Length
from zato.admin.web.views.audit_log.views import _get_error_summary, _get_resubmit_message, _get_resubmit_response

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The traceback a failed resubmit carries in its report - the last line is the exception itself
_traceback_text = (
    'Traceback (most recent call last):\n'
    '  File "/home/user/project/audit_log.py", line 464, in handle\n'
    '    config = _find_channel_config(channels, event.object_name)\n'
    "Exception: No HL7 MLLP channel matches the name `demo.hl7.adt.main`\n"
)

_traceback_last_line = 'Exception: No HL7 MLLP channel matches the name `demo.hl7.adt.main`'

# ################################################################################################################################
# ################################################################################################################################

def _body(response:'any_') -> 'dict':
    out = loads(response.content)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestErrorSummary:

    def test_the_last_line_of_a_traceback_is_the_summary(self):
        summary = _get_error_summary(_traceback_text)

        assert summary == _traceback_last_line

# ################################################################################################################################

    def test_a_long_last_line_is_capped(self):
        long_line = 'Exception: ' + 'x' * 200
        summary = _get_error_summary(f'Traceback (most recent call last):\n{long_line}\n')

        assert summary == long_line[:Action_Message_Max_Length] + ' ..'

# ################################################################################################################################
# ################################################################################################################################

class TestResubmitMessage:

    def test_an_as2_reprocess_names_its_routing_target(self):
        report = {
            'is_ok': True,
            'target_kind': 'service',
            'target_name': 'edi.orders.intake',
            'message_count': 1,
            'error': '',
            'action': 'reprocess',
            'cid': 'cid-1',
        }

        assert _get_resubmit_message(report) == 'Resubmitted to service edi.orders.intake'

# ################################################################################################################################

    def test_a_multi_document_reprocess_says_how_many_went_out(self):
        report = {
            'is_ok': True,
            'target_kind': 'topic',
            'target_name': 'edi.inbound',
            'message_count': 3,
            'error': '',
            'action': 'reprocess',
            'cid': 'cid-2',
        }

        assert _get_resubmit_message(report) == 'Resubmitted to topic edi.inbound (3 documents)'

# ################################################################################################################################

    def test_an_hl7_reprocess_names_the_channel_service(self):
        report = {
            'is_ok': True,
            'event_id': 123,
            'control_id': 'MSG00001',
            'service_name': 'demo.hl7.ack',
            'destinations': [],
            'error': '',
            'action': 'reprocess',
            'cid': 'cid-3',
        }

        assert _get_resubmit_message(report) == 'Resubmitted to service demo.hl7.ack'

# ################################################################################################################################

    def test_an_hl7_reprocess_without_a_service_names_the_destinations(self):
        report = {
            'is_ok': True,
            'event_id': 124,
            'control_id': 'MSG00002',
            'service_name': '',
            'destinations': ['hl7.forward.ehr', 'rest.billing'],
            'error': '',
            'action': 'reprocess',
            'cid': 'cid-4',
        }

        assert _get_resubmit_message(report) == 'Resubmitted to hl7.forward.ehr, rest.billing'

# ################################################################################################################################

    def test_a_resend_is_reported_by_its_cid(self):
        report = {
            'is_ok': True,
            'event_id': 125,
            'control_id': 'MSG00003',
            'ack_status': 'AA',
            'ack_outcome': 'ok',
            'error': '',
            'action': 'resend',
            'cid': 'cid-5',
        }

        assert _get_resubmit_message(report) == 'Resubmitted; CID cid-5'

# ################################################################################################################################

    def test_a_hop_resend_carries_no_action_and_reads_as_a_resend(self):
        report = {
            'is_ok': True,
            'event_id': 126,
            'error': '',
            'cid': 'cid-6',
        }

        assert _get_resubmit_message(report) == 'Resubmitted; CID cid-6'

# ################################################################################################################################
# ################################################################################################################################

class TestResubmitResponse:

    def test_a_success_answers_with_the_message_and_the_report_as_details(self):
        report = {
            'is_ok': True,
            'event_id': 127,
            'error': '',
            'cid': 'cid-7',
        }

        body = _body(_get_resubmit_response(report))

        assert body['is_success'] is True
        assert body['message'] == 'Resubmitted; CID cid-7'
        assert body['details_lexer'] == 'json'

        # The details are the whole report, readable in the modal
        assert loads(body['details']) == report

# ################################################################################################################################

    def test_a_failure_answers_with_the_summary_and_the_traceback_as_details(self):
        report = {
            'is_ok': False,
            'event_id': None,
            'error': _traceback_text,
            'action': 'reprocess',
            'cid': 'cid-8',
        }

        body = _body(_get_resubmit_response(report))

        assert body['is_success'] is False
        assert body['message'] == f'Resubmit failed - {_traceback_last_line}'
        assert body['details'] == _traceback_text
        assert body['details_lexer'] == 'pytb'

# ################################################################################################################################

    def test_a_failure_without_a_traceback_highlights_as_python(self):
        report = {
            'is_ok': False,
            'error': 'Connection refused',
            'cid': 'cid-9',
        }

        body = _body(_get_resubmit_response(report))

        assert body['message'] == 'Resubmit failed - Connection refused'
        assert body['details_lexer'] == 'python'

# ################################################################################################################################
# ################################################################################################################################
