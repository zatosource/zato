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
from zato.edi.reconcile import Reconciler

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

_Audit_Log_Url_Prefix = '/zato/audit-log/'
_Poll_Url_Path = '/zato/audit-log/poll/'

# The class the pill carries while the filter is on
_Pill_Active_Class = 'audit-log-filter-pill-active'

# AS2 column indexes: Time, CID, Event, Partner, Message id, Disposition, MIC, Size, Data preview, Actions
_AS2_Column_Event  = 2
_AS2_Column_Msg_ID = 4

# X12 column indexes: Time, CID, Event, Partner, Control number, Outcome, Size, Data preview
_X12_Column_Event          = 2
_X12_Column_Control_Number = 4

# What the seeded events carry
_Event_Message_Sent     = 'message-sent'
_Event_MDN_Received     = 'mdn-received'
_Event_Interchange_Sent = 'interchange-sent'

# ################################################################################################################################
# ################################################################################################################################

def _goto_audit_log(page:'Page', base_url:'str', source:'str', object_name:'str', status:'str'='') -> 'None':
    """ Navigates to the audit log page of one object of one source and waits
    for the first page of events to load.
    """
    encoded_name = quote(object_name)
    url = f'{base_url}{_Audit_Log_Url_Prefix}?source={source}&object_name={encoded_name}&cluster=1'

    if status:
        url += f'&status={status}'

    _ = page.goto(url)
    _wait_for_table(page)

# ################################################################################################################################

def _wait_for_table(page:'Page') -> 'None':
    """ Waits until the audit log table has finished loading its current page of events.
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

def _is_poll_response(response:'any_') -> 'bool':
    """ Matches the response of the audit log poll endpoint.
    """
    out = _Poll_Url_Path in response.url
    return out

# ################################################################################################################################

def _click_pill(page:'Page') -> 'None':
    """ Clicks the outstanding pill and waits for the page of events it fetches.
    """
    with page.expect_response(_is_poll_response, timeout=10000):
        page.click('#audit-log-outstanding-pill')

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

def _get_column_values(page:'Page', column_idx:'int') -> 'anylist':
    """ Returns the given column of every row currently shown, top to bottom.
    """
    out = [] # type: anylist

    for row in _get_rows(page):
        cells = _get_row_cells(row)
        out.append(cells[column_idx])

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAS2Outstanding:
    """ The outstanding filter pill of the AS2 audit log page - the sent messages
    whose MDN has not arrived, oldest first, toggled without leaving the page.
    """

# ################################################################################################################################

    def test_the_pill_narrows_the_page_to_open_exchanges(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

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

        # The page opens unfiltered, with the pill present but not active ..
        _goto_audit_log(page, base_url, 'as2', pair)

        pill = page.wait_for_selector('#audit-log-outstanding-pill', state='visible', timeout=10000)
        assert pill is not None

        pill_class = pill.get_attribute('class')
        assert pill_class is not None
        assert _Pill_Active_Class not in pill_class, f'Expected an inactive pill, got: "{pill_class}"'

        # .. showing the complete exchange - three sends plus the MDN, newest first ..
        message_ids = _get_column_values(page, _AS2_Column_Msg_ID)
        assert message_ids == [second_id, third_id, second_id, first_id], f'Unexpected rows: {message_ids}'

        # .. one click narrows the page down to the open exchanges, oldest first ..
        _click_pill(page)

        message_ids = _get_column_values(page, _AS2_Column_Msg_ID)
        assert message_ids == [first_id, third_id], f'Unexpected outstanding rows: {message_ids}'

        events = _get_column_values(page, _AS2_Column_Event)
        assert events == [_Event_Message_Sent, _Event_Message_Sent], f'Unexpected outstanding events: {events}'

        # .. the pill is now active and the page URL carries the filter,
        # .. so a reload or a copied link keeps it ..
        pill_class = page.get_attribute('#audit-log-outstanding-pill', 'class')
        assert pill_class is not None
        assert _Pill_Active_Class in pill_class, f'Expected an active pill, got: "{pill_class}"'
        assert 'status=outstanding' in page.url, f'Expected status=outstanding in the URL, got: "{page.url}"'

        # .. and one more click brings everything back.
        _click_pill(page)

        message_ids = _get_column_values(page, _AS2_Column_Msg_ID)
        assert message_ids == [second_id, third_id, second_id, first_id], f'Unexpected rows after toggling: {message_ids}'
        assert 'status=outstanding' not in page.url, f'Expected no status in the URL, got: "{page.url}"'

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

        # A link with the filter opens the page already narrowed down ..
        _goto_audit_log(page, base_url, 'as2', pair, status='outstanding')

        # .. with the pill already active ..
        pill_class = page.get_attribute('#audit-log-outstanding-pill', 'class')
        assert pill_class is not None
        assert _Pill_Active_Class in pill_class, f'Expected an active pill, got: "{pill_class}"'

        # .. and only the open exchange shown.
        message_ids = _get_column_values(page, _AS2_Column_Msg_ID)
        assert message_ids == [open_id], f'Unexpected outstanding rows: {message_ids}'

# ################################################################################################################################
# ################################################################################################################################

class TestX12Outstanding:
    """ The same outstanding pill on the X12 audit log page - the interchanges
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

        # The X12 page renders its own columns ..
        _goto_audit_log(page, base_url, 'x12', pair)

        header_text = page.inner_text('#audit-log-table thead')
        header_text = header_text.lower()
        assert 'control number' in header_text, f'Expected a Control number column, got: "{header_text}"'

        # .. showing the complete exchange - two sends plus the acknowledgment ..
        events = _get_column_values(page, _X12_Column_Event)
        row_count = len(events)
        assert row_count == 3, f'Expected 3 rows, got: {events}'

        # .. and the pill narrows it down to the unacknowledged interchange -
        # .. control numbers are normalized, so the zero-padded ISA13 shows without its padding.
        _click_pill(page)

        events = _get_column_values(page, _X12_Column_Event)
        assert events == [_Event_Interchange_Sent], f'Unexpected outstanding events: {events}'

        control_numbers = _get_column_values(page, _X12_Column_Control_Number)
        assert control_numbers == ['2'], f'Unexpected outstanding control numbers: {control_numbers}'

# ################################################################################################################################
# ################################################################################################################################
