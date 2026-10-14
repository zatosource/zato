# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato.edi.reconcile import Reconciler
from audit_log_ui import get_row_event_types, get_rows, get_summary_value, goto_audit_log, open_summary

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# What the seeded events carry
_Event_Interchange_Sent = 'interchange-sent'

# ################################################################################################################################
# ################################################################################################################################

class TestX12Outstanding:
    """ The outstanding filter of the X12 audit log page - the interchanges
    whose 997/999 has not arrived.
    """

# ################################################################################################################################

    def test_interchanges_without_their_ack(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The identifiers are unique per run so only this test's events show up.
        suffix = CryptoManager.generate_hex_string().upper()
        sender = f'ZATORETAIL{suffix}'
        receiver = f'PARTNERCORP{suffix}'
        pair = f'{sender}:{receiver}'

        # Two interchanges leave and only the first one is acknowledged.
        reconciler = Reconciler()

        reconciler.record_interchange_sent(sender, receiver, '000000001', cid='cid-first-' + suffix)
        reconciler.record_interchange_sent(sender, receiver, '000000002', cid='cid-second-' + suffix)

        reconciler.record_ack_received(sender, receiver, '000000001', cid='cid-ack-' + suffix)

        # The X12 page shows the complete exchange - two sends plus the acknowledgment ..
        goto_audit_log(page, base_url, 'x12', pair)

        events = get_row_event_types(page)
        row_count = len(events)
        assert row_count == 3, f'Expected 3 rows, got: {events}'

        # .. an X12 event names its interchange by its control number, said in the pane ..
        rows = get_rows(page)
        open_summary(page, rows[0])

        control_number = get_summary_value(page, 'Control number')
        assert control_number != '', 'Expected a control number in the pane of an X12 event'

        # .. and the filter narrows it down to the unacknowledged interchange -
        # .. control numbers are normalized, so the zero-padded ISA13 shows without its padding.
        goto_audit_log(page, base_url, 'x12', pair, status='outstanding')

        events = get_row_event_types(page)
        assert events == [_Event_Interchange_Sent], f'Unexpected outstanding events: {events}'

        rows = get_rows(page)
        open_summary(page, rows[0])

        control_number = get_summary_value(page, 'Control number')
        assert control_number == '2', f'Unexpected outstanding control number: {control_number}'

# ################################################################################################################################
# ################################################################################################################################
