# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from as4_exchange import delete_exchange, new_exchange, send_with_retry, wait_for_invoker_service, Receiver_Service
from audit_resubmit import get_resubmit_label, is_report_ok, resubmit_until, row_selector_of_event, wait_for_marker
from audit_toggle import goto_audit_log

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.as4.resubmit.' + CryptoManager.generate_hex_string(32) + '.'

_Audit_Source = 'as4'

# What the exchange's two resubmittable events show as, by the labels their role tags carry
_Event_Message_Sent     = 'Message sent'
_Event_Message_Received = 'Message received'

# What the two row actions of an AS4 exchange are labelled - one word for both,
# the service behind each row is what tells a resend from a reprocess
_Label_Resend    = 'Resubmit'
_Label_Reprocess = 'Resubmit'

# Log lines the propagation retries of this suite can produce on the server
_AS4_Log_Patterns = ('AS4 request rejected',)

# ################################################################################################################################
# ################################################################################################################################

def _is_reprocessed_to_service(report:'anydict') -> 'bool':
    """ Tells whether a reprocess landed on the channel's own service - until the channel propagates
    to the server, it lands on the default shared topic instead.
    """
    out = report['is_ok'] and report['target_name'] == Receiver_Service
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAS4AuditLogResubmit:
    """ The resubmit actions of the AS4 audit log - a resend on the sent row, which delivers the
    stored payloads as a message of their own, and a reprocess on the received row, which routes
    them to the channel's target again. Both land as their own events linked to the original
    by CID, with a marker on the row they were made from.
    """

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_AS4_Log_Patterns)
    def test_resend_of_a_sent_message(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_invoker_service(page, base_url)

        # The parties are unique per run so only this test's events show up.
        suffix = CryptoManager.generate_hex_string()
        from_party = f'party-a-{suffix}'
        to_party = f'party-b-{suffix}'
        pair = f'{from_party}:{to_party}'

        name = _Test_Name_Prefix + 'resend'
        exchange = new_exchange(page, base_url, server_port, name, from_party, to_party)

        try:
            payload = '<Document xmlns="urn:test"><Value>' + CryptoManager.generate_hex_string() + '</Value></Document>'
            result = send_with_retry(page, base_url, name, payload)
            assert result['is_ok'], f'Expected a verified receipt, got: {result}'

            goto_audit_log(page, base_url, _Audit_Source, pair)

            # The row of the sent message carries the resend action ..
            sent_row = row_selector_of_event(_Event_Message_Sent)

            label = get_resubmit_label(page, sent_row)
            assert label == _Label_Resend, f'Expected a Resubmit link, got: "{label}"'

            # .. clicking it delivers the stored payloads through the real pipeline once more ..
            report = resubmit_until(page, sent_row, is_report_ok)

            assert report['action'] == 'resend'
            assert report['has_receipt'] is True
            assert report['error'] == ''
            assert report['cid']

            # .. under an eb:MessageId of its own, so this is a message the receiving side
            # accepted rather than one its duplicate detection turned away ..
            assert report['message_id'] != result['message_id']

            # .. and the row it was made from says so.
            wait_for_marker(page, sent_row)

        finally:
            delete_exchange(page, exchange)

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_AS4_Log_Patterns)
    def test_reprocess_of_a_received_message(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_invoker_service(page, base_url)

        suffix = CryptoManager.generate_hex_string()
        from_party = f'party-a-{suffix}'
        to_party = f'party-b-{suffix}'
        pair = f'{from_party}:{to_party}'

        name = _Test_Name_Prefix + 'reprocess'
        exchange = new_exchange(page, base_url, server_port, name, from_party, to_party)

        try:
            payload = '<Document xmlns="urn:test"><Value>' + CryptoManager.generate_hex_string() + '</Value></Document>'
            result = send_with_retry(page, base_url, name, payload)
            assert result['is_ok'], f'Expected a verified receipt, got: {result}'

            goto_audit_log(page, base_url, _Audit_Source, pair)

            # The row of the received message carries the reprocess action ..
            received_row = row_selector_of_event(_Event_Message_Received)

            label = get_resubmit_label(page, received_row)
            assert label == _Label_Reprocess, f'Expected a Resubmit link, got: "{label}"'

            # .. clicking it routes the stored payloads to the channel's target again ..
            report = resubmit_until(page, received_row, _is_reprocessed_to_service)

            assert report['action'] == 'reprocess'
            assert report['target_kind'] == 'service'
            assert report['message_count'] == 1
            assert report['error'] == ''
            assert report['cid']

            # .. and the row it was made from says so.
            wait_for_marker(page, received_row)

        finally:
            delete_exchange(page, exchange)

# ################################################################################################################################
# ################################################################################################################################
