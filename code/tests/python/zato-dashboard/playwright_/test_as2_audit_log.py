# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from urllib.parse import quote

# Zato
from zato.common.as2.reconcile import MDNReconciler
from zato.common.crypto.api import CryptoManager
from zato.common.json_internal import dumps
from as2_outconn import create_as2_outconn, delete_as2_outconn, open_as2_outconn_page, wait_for_as2_outconn_row
from as4_keys import new_party

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.as2.audit.' + CryptoManager.generate_hex_string(32) + '.'

_Audit_Log_Url_Prefix = '/zato/audit-log/'

# The section title for the AS2 source, compared lowercase because the heading is styled with CSS
_AS2_Title = 'as2 audit log'

# What the seeded events carry
_Event_Message_Sent = 'message-sent'
_Event_MDN_Received = 'mdn-received'

# How the table renders a text cell with nothing in it
_Empty_Cell = '---'

_MIC = 'T3JkZXJzTUlDVmFsdWU=, sha-256'
_Disposition = 'processed'

# Column indexes: Time, CID, Event, Partner, Message id, Disposition, MIC, Size, Data preview
_Column_Time        = 0
_Column_CID         = 1
_Column_Event       = 2
_Column_Partner     = 3
_Column_Msg_ID      = 4
_Column_Disposition = 5
_Column_MIC         = 6
_Column_Size        = 7
_Column_Data        = 8

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

def _goto_audit_log(page:'Page', base_url:'str', object_name:'str') -> 'None':
    """ Navigates to the AS2 audit log page of one identity pair and waits
    for the first page of events to load.
    """
    encoded_name = quote(object_name)
    url = f'{base_url}{_Audit_Log_Url_Prefix}?source=as2&object_name={encoded_name}&cluster=1'

    _ = page.goto(url)
    _wait_for_table(page)

# ################################################################################################################################

def _wait_for_table(page:'Page') -> 'None':
    """ Waits until the audit log table has finished loading its current page of events,
    i.e. until the table body exists, has rows and none of them is the loading placeholder.
    """
    _ = page.wait_for_function(
        '''() => {
            let body = document.querySelector('#audit-log-table-body');
            if (!body) return false;
            let rows = body.querySelectorAll('tr');
            if (!rows.length) return false;
            return !body.querySelector('tr.detail-loading-row');
        }''',
        timeout=10000)

# ################################################################################################################################

def _get_rows(page:'Page') -> 'anylist':
    """ Returns all rows currently shown in the audit log table.
    """
    out = page.query_selector_all('#audit-log-table-body tr')
    return out

# ################################################################################################################################

def _get_row_cells(row:'any_') -> 'anylist':
    """ Returns the text of each cell in one audit log row.
    """
    out = [] # type: anylist

    for cell in row.query_selector_all('td'):
        out.append(cell.inner_text().strip())

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAS2AuditLog:
    """ The audit log page as the AS2 transaction monitor - the per-source columns
    show the partner pair, the MDN disposition and the MIC values, and each
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
        _goto_audit_log(page, base_url, pair)

        # The section title names the source, compared case-insensitively because of CSS styling ..
        title_text = page.inner_text('#detail-section-title')
        title_text = title_text.lower()
        assert title_text.startswith(_AS2_Title), f'Expected the title to start with "{_AS2_Title}", got: "{title_text}"'

        # .. the section title pill shows the identity pair ..
        pill_text = page.inner_text('#detail-section-title .detail-component-pill')
        pill_text = pill_text.lower()
        assert pill_text == pair.lower(), f'Expected pair "{pair}" in the pill, got: "{pill_text}"'

        # .. the table shows the AS2 columns, compared case-insensitively
        # .. because the headers are uppercased with CSS ..
        header_text = page.inner_text('#audit-log-table thead')
        header_text = header_text.lower()
        assert 'partner' in header_text, f'Expected a Partner column, got: "{header_text}"'
        assert 'disposition' in header_text, f'Expected a Disposition column, got: "{header_text}"'
        assert 'mic' in header_text, f'Expected a MIC column, got: "{header_text}"'

        # .. the exchange shows as two events ..
        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. the newest one is the arrival of the MDN, with the disposition
        # .. and the MIC pulled out of the event data into their own columns ..
        mdn_cells = _get_row_cells(rows[0])

        assert mdn_cells[_Column_Event] == _Event_MDN_Received, \
            f'Expected event "{_Event_MDN_Received}", got: "{mdn_cells[_Column_Event]}"'
        assert mdn_cells[_Column_Partner] == pair, f'Expected partner "{pair}", got: "{mdn_cells[_Column_Partner]}"'
        assert mdn_cells[_Column_Msg_ID] == message_id, \
            f'Expected message id "{message_id}", got: "{mdn_cells[_Column_Msg_ID]}"'
        assert mdn_cells[_Column_Disposition] == _Disposition, \
            f'Expected disposition "{_Disposition}", got: "{mdn_cells[_Column_Disposition]}"'
        assert mdn_cells[_Column_MIC] == _MIC, f'Expected MIC "{_MIC}", got: "{mdn_cells[_Column_MIC]}"'

        # .. and the older one is the send itself, which carries the MIC computed
        # .. at send time and no disposition of its own.
        sent_cells = _get_row_cells(rows[1])

        assert sent_cells[_Column_Event] == _Event_Message_Sent, \
            f'Expected event "{_Event_Message_Sent}", got: "{sent_cells[_Column_Event]}"'
        assert sent_cells[_Column_Partner] == pair, f'Expected partner "{pair}", got: "{sent_cells[_Column_Partner]}"'
        assert sent_cells[_Column_Msg_ID] == message_id, \
            f'Expected message id "{message_id}", got: "{sent_cells[_Column_Msg_ID]}"'
        assert sent_cells[_Column_Disposition] == _Empty_Cell, \
            f'Expected the empty-cell placeholder, got: "{sent_cells[_Column_Disposition]}"'
        assert sent_cells[_Column_MIC] == _MIC, f'Expected MIC "{_MIC}", got: "{sent_cells[_Column_MIC]}"'

        # The times are shown in the browser's locale format, not as raw ISO strings.
        assert mdn_cells[_Column_Time] != '', 'Expected a non-empty event time'
        assert '+00:00' not in mdn_cells[_Column_Time], \
            f'Expected a locale-formatted time, got a raw ISO string: "{mdn_cells[_Column_Time]}"'

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
            _wait_for_table(page)

            # .. the URL points to the AS2 audit log pre-filtered to this partner ..
            assert 'source=as2' in page.url, f'Expected source=as2 in the URL, got: "{page.url}"'

            pill_text = page.inner_text('#detail-section-title .detail-component-pill')
            pill_text = pill_text.lower()
            assert pill_text == pair.lower(), f'Expected pair "{pair}" in the pill, got: "{pill_text}"'

            # .. and the pair's seeded events are shown.
            rows = _get_rows(page)
            row_count = len(rows)
            assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

            mdn_cells = _get_row_cells(rows[0])
            assert mdn_cells[_Column_Event] == _Event_MDN_Received, \
                f'Expected event "{_Event_MDN_Received}", got: "{mdn_cells[_Column_Event]}"'
            assert mdn_cells[_Column_Msg_ID] == message_id, \
                f'Expected message id "{message_id}", got: "{mdn_cells[_Column_Msg_ID]}"'

        finally:
            delete_as2_outconn(page, outconn_id)

# ################################################################################################################################
# ################################################################################################################################
