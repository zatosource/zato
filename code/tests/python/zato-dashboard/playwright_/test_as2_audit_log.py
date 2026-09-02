# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.as2.reconcile import MDNReconciler
from zato.common.crypto.api import CryptoManager
from zato.common.json_internal import dumps
from as2_outconn import create_as2_outconn, delete_as2_outconn, open_as2_outconn_page, wait_for_as2_outconn_row
from as4_keys import new_party
from audit_log_ui import get_details_value, get_row_event, get_row_time_text, get_rows, goto_audit_log, open_details, \
    wait_for_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.as2.audit.' + CryptoManager.generate_hex_string(32) + '.'

_Audit_Log_Url_Prefix = '/zato/audit-log/'

_Audit_Source = 'as2'

# The section title for the AS2 source, compared lowercase because the heading is styled with CSS
_AS2_Title = 'as2 audit log'

# What the seeded events show as, by the labels their role tags carry
_Event_Message_Sent = 'Message sent'
_Event_MDN_Received = 'MDN received'

_MIC = 'T3JkZXJzTUlDVmFsdWU=, sha-256'
_Disposition = 'processed'

# ################################################################################################################################
# ################################################################################################################################

def _seed_exchange(as2_from:'str', as2_to:'str', message_id:'str') -> 'None':
    """ Writes one complete exchange into the shared audit database - the message-sent
    half at delivery time and the mdn-received half once the receipt arrived,
    the same two events the reconciliation store records in production.
    """
    reconciler = MDNReconciler()

    reconciler.record_message_sent(as2_from, as2_to, message_id, mic=_MIC, cid='cid-sent-' + message_id)

    mdn_data = dumps({'disposition': _Disposition, 'modifier_kind': '', 'modifier': '', 'mic': _MIC})
    reconciler.record_mdn_received(message_id, cid='cid-mdn-' + message_id, data=mdn_data)

# ################################################################################################################################
# ################################################################################################################################

class TestAS2AuditLog:
    """ The audit log page as the AS2 transaction monitor - the pane's Details tab
    shows the partner pair, the MDN disposition and the MIC values, and each
    connection row links to the log pre-filtered to that partner.
    """

# ################################################################################################################################

    def test_as2_events_render_with_their_columns(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The identities are unique per run so only this test's events show up.
        suffix = CryptoManager.generate_hex_string()
        as2_from = f'ZatoRetail.{suffix}'
        as2_to = f'PartnerCorp.{suffix}'
        pair = f'{as2_from}:{as2_to}'

        message_id = f'{suffix}@zato.test'

        # Seed one complete exchange into the shared audit database ..
        _seed_exchange(as2_from, as2_to, message_id)

        # .. and open the page pre-filtered to that pair.
        goto_audit_log(page, base_url, _Audit_Source, pair)

        # The section title names the source, compared case-insensitively because of CSS styling ..
        title_text = page.inner_text('#detail-section-title')
        title_text = title_text.lower()
        assert title_text.startswith(_AS2_Title), f'Expected the title to start with "{_AS2_Title}", got: "{title_text}"'

        # .. the section title pill shows the identity pair ..
        pill_text = page.inner_text('#detail-section-title .detail-component-pill')
        pill_text = pill_text.lower()
        assert pill_text == pair.lower(), f'Expected pair "{pair}" in the pill, got: "{pill_text}"'

        # .. the exchange shows as two events ..
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. the newest one is the arrival of the MDN, with the pair, the disposition
        # .. and the MIC read in the pane's Details tab ..
        mdn_event = get_row_event(rows[0])
        assert mdn_event == _Event_MDN_Received, f'Expected event "{_Event_MDN_Received}", got: "{mdn_event}"'

        # The times are shown in the browser's locale format, not as raw ISO strings.
        mdn_time = get_row_time_text(rows[0])
        assert mdn_time != '', 'Expected a non-empty event time'
        assert '+00:00' not in mdn_time, f'Expected a locale-formatted time, got a raw ISO string: "{mdn_time}"'

        open_details(page, rows[0])

        mdn_partner = get_details_value(page, 'Partner')
        assert mdn_partner == pair, f'Expected partner "{pair}", got: "{mdn_partner}"'

        mdn_msg_id = get_details_value(page, 'Message id')
        assert mdn_msg_id == message_id, f'Expected message id "{message_id}", got: "{mdn_msg_id}"'

        mdn_disposition = get_details_value(page, 'Disposition')
        assert mdn_disposition == _Disposition, f'Expected disposition "{_Disposition}", got: "{mdn_disposition}"'

        mdn_mic = get_details_value(page, 'MIC')
        assert mdn_mic == _MIC, f'Expected MIC "{_MIC}", got: "{mdn_mic}"'

        # .. and the older one is the send itself, which carries the MIC computed
        # .. at send time and no disposition of its own.
        sent_event = get_row_event(rows[1])
        assert sent_event == _Event_Message_Sent, f'Expected event "{_Event_Message_Sent}", got: "{sent_event}"'

        open_details(page, rows[1])

        sent_partner = get_details_value(page, 'Partner')
        assert sent_partner == pair, f'Expected partner "{pair}", got: "{sent_partner}"'

        sent_msg_id = get_details_value(page, 'Message id')
        assert sent_msg_id == message_id, f'Expected message id "{message_id}", got: "{sent_msg_id}"'

        # A fact with no value at all is left out of the pane altogether.
        sent_disposition = get_details_value(page, 'Disposition')
        assert sent_disposition == '', f'Expected no disposition on the send, got: "{sent_disposition}"'

        sent_mic = get_details_value(page, 'MIC')
        assert sent_mic == _MIC, f'Expected MIC "{_MIC}", got: "{sent_mic}"'

# ################################################################################################################################

    def test_link_from_connection_list(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The identities are unique per run so only this test's events show up.
        suffix = CryptoManager.generate_hex_string()
        as2_from = f'ZatoRetail.{suffix}'
        as2_to = f'PartnerCorpEU.{suffix}'
        pair = f'{as2_from}:{as2_to}'

        message_id = f'{suffix}@zato.test'

        # Seed one complete exchange under this pair ..
        _seed_exchange(as2_from, as2_to, message_id)

        # .. and create a connection with the same identities.
        sender = new_party('as2-audit-sender')
        receiver = new_party('as2-audit-receiver')

        name = _Test_Name_Prefix + 'link'

        outconn_id = create_as2_outconn(page, base_url, name, 'https://as2.example.com/exchange', {
            'as2_from': as2_from,
            'as2_to': as2_to,
            'as2_partner_cert': receiver.certificate,
            'as2_signing_key': sender.key,
            'as2_signing_cert_chain': sender.certificate,
            'as2_decryption_key': sender.key,
        })

        try:

            # Reload so the row carries the link the server built out of the stored identities ..
            open_as2_outconn_page(page, base_url, query=name)
            _ = wait_for_as2_outconn_row(page, name)

            # .. click the audit log link in this connection's row ..
            row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
            page.click(f'{row_selector} a:text-is("Audit log")')

            # .. wait for the audit log page to load ..
            page.wait_for_url(f'**{_Audit_Log_Url_Prefix}**')
            wait_for_table(page)

            # .. the URL points to the AS2 audit log pre-filtered to this partner ..
            assert 'source=as2' in page.url, f'Expected source=as2 in the URL, got: "{page.url}"'

            pill_text = page.inner_text('#detail-section-title .detail-component-pill')
            pill_text = pill_text.lower()
            assert pill_text == pair.lower(), f'Expected pair "{pair}" in the pill, got: "{pill_text}"'

            # .. and the pair's seeded events are shown.
            rows = get_rows(page)
            row_count = len(rows)
            assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

            mdn_event = get_row_event(rows[0])
            assert mdn_event == _Event_MDN_Received, f'Expected event "{_Event_MDN_Received}", got: "{mdn_event}"'

            open_details(page, rows[0])

            mdn_msg_id = get_details_value(page, 'Message id')
            assert mdn_msg_id == message_id, f'Expected message id "{message_id}", got: "{mdn_msg_id}"'

        finally:
            delete_as2_outconn(page, outconn_id)

# ################################################################################################################################
# ################################################################################################################################
