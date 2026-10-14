# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditSource
from zato.common.crypto.api import CryptoManager
from audit_log_ui import get_row_event_types, get_rows, get_summary_value, goto_audit_log, open_summary

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Audit_Source = 'mllp-outgoing'

# What the seeded events carry
_Event_Message_Sent = 'message-sent'

# ################################################################################################################################
# ################################################################################################################################

class TestMLLPOutgoingOutstanding:
    """ The outstanding filter of the outgoing MLLP audit log page - the messages
    whose ACK has not arrived.
    """

# ################################################################################################################################

    def test_messages_without_their_ack(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The identifiers are unique per run so only this test's events show up.
        suffix = CryptoManager.generate_hex_string().upper()
        connection_name = f'test.mllp.outstanding.{suffix}'

        first_control_id = f'MSG1{suffix}'
        second_control_id = f'MSG2{suffix}'

        # Two messages leave and only the first one is acknowledged.
        audit_log = AuditLog('audit-log-test')

        audit_log.insert(AuditSource.MLLP_Outgoing, AuditEvent.Message_Sent, connection_name,
            cid='cid-first-' + suffix, msg_id=first_control_id)
        audit_log.insert(AuditSource.MLLP_Outgoing, AuditEvent.Message_Sent, connection_name,
            cid='cid-second-' + suffix, msg_id=second_control_id)

        audit_log.insert(AuditSource.MLLP_Outgoing, AuditEvent.Ack_Received, connection_name,
            cid='cid-first-' + suffix, msg_id=first_control_id)

        # The page shows the complete exchange - two sends plus the acknowledgment ..
        goto_audit_log(page, base_url, _Audit_Source, connection_name)

        events = get_row_event_types(page)
        row_count = len(events)
        assert row_count == 3, f'Expected 3 rows, got: {events}'

        # .. and the filter narrows it down to the unacknowledged message.
        goto_audit_log(page, base_url, _Audit_Source, connection_name, status='outstanding')

        events = get_row_event_types(page)
        assert events == [_Event_Message_Sent], f'Unexpected outstanding events: {events}'

        rows = get_rows(page)
        open_summary(page, rows[0])

        control_id = get_summary_value(page, 'Control id')
        assert control_id == second_control_id, f'Unexpected outstanding control id: {control_id}'

# ################################################################################################################################
# ################################################################################################################################
