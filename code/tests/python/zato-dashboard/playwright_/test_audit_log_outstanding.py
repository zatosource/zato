# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.as2.reconcile import MDNReconciler
from zato.common.crypto.api import CryptoManager
from zato.edi.reconcile import Reconciler
from audit_log_ui import get_details_value, get_row_event_types, get_row_msg_ids, get_rows, goto_audit_log, open_details

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# What the seeded events carry
_Event_Message_Sent     = 'message-sent'
_Event_Interchange_Sent = 'interchange-sent'

# ################################################################################################################################
# ################################################################################################################################

class TestAS2Outstanding:
    """ The outstanding filter of the AS2 audit log page - the sent messages whose MDN has not
    arrived, oldest first. The page itself offers no way of turning it on, it is what the ack
    report and the overdue alerts link into.
    """

# ################################################################################################################################

    def test_the_filter_narrows_the_page_to_open_exchanges(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The identities are unique per run so only this test's events show up.
        suffix = CryptoManager.generate_hex_string()
        as2_from = f'ZatoRetail.{suffix}'
        as2_to = f'PartnerCorp.{suffix}'
        pair = f'{as2_from}:{as2_to}'

        first_id = f'{suffix}-first@zato.test'
        second_id = f'{suffix}-second@zato.test'
        third_id = f'{suffix}-third@zato.test'

        # Three messages leave, in this order, and only the second one is acknowledged.
        reconciler = MDNReconciler()

        reconciler.record_message_sent(as2_from, as2_to, first_id, cid='cid-first-' + suffix)
        reconciler.record_message_sent(as2_from, as2_to, second_id, cid='cid-second-' + suffix)
        reconciler.record_message_sent(as2_from, as2_to, third_id, cid='cid-third-' + suffix)

        reconciler.record_mdn_received(second_id, cid='cid-mdn-' + suffix)

        # The page of the pair shows the complete exchange - three sends plus the MDN,
        # newest first ..
        goto_audit_log(page, base_url, 'as2', pair)

        message_ids = get_row_msg_ids(page)
        assert message_ids == [second_id, third_id, second_id, first_id], f'Unexpected rows: {message_ids}'

        # .. and the same page asked for with the filter shows the open exchanges only,
        # oldest first.
        goto_audit_log(page, base_url, 'as2', pair, status='outstanding')

        message_ids = get_row_msg_ids(page)
        assert message_ids == [first_id, third_id], f'Unexpected outstanding rows: {message_ids}'

        events = get_row_event_types(page)
        assert events == [_Event_Message_Sent, _Event_Message_Sent], f'Unexpected outstanding events: {events}'

# ################################################################################################################################

    def test_the_page_opens_prefiltered_from_the_url(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The identities are unique per run so only this test's events show up.
        suffix = CryptoManager.generate_hex_string()
        as2_from = f'ZatoRetail.{suffix}'
        as2_to = f'PartnerCorpEU.{suffix}'
        pair = f'{as2_from}:{as2_to}'

        open_id = f'{suffix}-open@zato.test'
        closed_id = f'{suffix}-closed@zato.test'

        # One message is still waiting for its MDN, the other one is reconciled.
        reconciler = MDNReconciler()

        reconciler.record_message_sent(as2_from, as2_to, open_id, cid='cid-open-' + suffix)
        reconciler.record_message_sent(as2_from, as2_to, closed_id, cid='cid-closed-' + suffix)

        reconciler.record_mdn_received(closed_id, cid='cid-mdn-' + suffix)

        # A link with the filter opens the page already narrowed down,
        # with only the open exchange shown.
        goto_audit_log(page, base_url, 'as2', pair, status='outstanding')

        message_ids = get_row_msg_ids(page)
        assert message_ids == [open_id], f'Unexpected outstanding rows: {message_ids}'

# ################################################################################################################################
# ################################################################################################################################

class TestX12Outstanding:
    """ The same outstanding filter on the X12 audit log page - the interchanges
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
        open_details(page, rows[0])

        control_number = get_details_value(page, 'Control number')
        assert control_number != '', 'Expected a control number in the pane of an X12 event'

        # .. and the filter narrows it down to the unacknowledged interchange -
        # .. control numbers are normalized, so the zero-padded ISA13 shows without its padding.
        goto_audit_log(page, base_url, 'x12', pair, status='outstanding')

        events = get_row_event_types(page)
        assert events == [_Event_Interchange_Sent], f'Unexpected outstanding events: {events}'

        rows = get_rows(page)
        open_details(page, rows[0])

        control_number = get_details_value(page, 'Control number')
        assert control_number == '2', f'Unexpected outstanding control number: {control_number}'

# ################################################################################################################################
# ################################################################################################################################
