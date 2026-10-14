# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditSource
from zato.common.crypto.api import CryptoManager
from zato.common.json_internal import dumps
from audit_log_ui import click_pane_cid, get_rows, goto_audit_log, open_summary

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Audit_Source = 'x12'

# The tab labels of the message overlay when the payload carries an EDI document
_Raw_Tab_Label    = 'Raw'
_Parsed_Tab_Label = 'Parsed'

# The overlay elements the tests look at
_Overlay_Selector    = '#zato-highlight-pane-overlay'
_Tab_Bar_Selector    = _Overlay_Selector + ' .zato-highlight-pane-overlay-tabs'
_Tab_Selector        = _Overlay_Selector + ' .zato-highlight-pane-overlay-tab'
_Active_Tab_Selector = _Overlay_Selector + ' .zato-highlight-pane-overlay-tab-active'

# What the parsed view of the seeded purchase order must contain
_PO_Number = 'PO-4529'

# The raw X12 purchase order the seeded event carries as its payload.
_purchase_order_850 = 'ISA*00*          *00*          *ZZ*SENDERID       *ZZ*RECEIVERID     ' + \
    '*260709*1200*U*00401*000000905*0*P*>~' + \
    'GS*PO*SENDERGS*RECEIVERGS*20260709*1200*905*X*004010~' + \
    'ST*850*0001~' + \
    'BEG*00*SA*PO-4529**20260709~' + \
    'PO1*1*10*EA*9.75*TE*UP*012345678905~' + \
    'PID*F****Blue ceramic mug 350 ml~' + \
    'CTT*1~' + \
    'SE*6*0001~' + \
    'GE*1*905~' + \
    'IEA*1*000000905~'

# ################################################################################################################################
# ################################################################################################################################

def _open_message_overlay(page:'Page') -> 'None':
    """ Opens the message overlay of the newest event - the row is selected, its Summary tab
    opened and the CID link in the pane clicked.
    """
    rows = get_rows(page)
    open_summary(page, rows[0])
    click_pane_cid(page)

    # The overlay is only usable once its editor holds the payload.
    _ = page.wait_for_function(
        '''() => {
            let element = document.querySelector('#zato-highlight-pane-overlay .zato-highlight-pane-editor');
            if (!element) return false;
            return ace.edit(element).getValue() !== '';
        }''',
        timeout=10000)

# ################################################################################################################################

def _get_editor_text(page:'Page') -> 'str':
    """ Returns the complete text the overlay's editor holds.
    """
    out = page.evaluate(
        '''() => {
            let element = document.querySelector('#zato-highlight-pane-overlay .zato-highlight-pane-editor');
            return ace.edit(element).getValue();
        }''')

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAuditLogParsedView:
    """ The message overlay of the audit log - a payload that carries an EDI document
    shows the raw wire format and its parsed rendering side by side, as two tabs,
    while any other payload keeps the raw view only.
    """

# ################################################################################################################################

    def test_edi_payload_shows_raw_and_parsed_tabs(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The identities are unique per run so only this test's events show up.
        suffix = CryptoManager.generate_hex_string().upper()
        pair = f'ZATORETAIL{suffix}:PARTNERCORP{suffix}'

        # Seed one event whose payload is a complete X12 purchase order ..
        audit_log = AuditLog('audit-log-test')
        audit_log.insert(AuditSource.X12, AuditEvent.Interchange_Sent, pair, cid='cid-edi-' + suffix, msg_id='905',
            size=len(_purchase_order_850), data=_purchase_order_850)

        # .. open the page pre-filtered to that pair and open the message overlay.
        goto_audit_log(page, base_url, _Audit_Source, pair)
        _open_message_overlay(page)

        # The overlay shows the raw and parsed tabs ..
        _ = page.wait_for_selector(_Tab_Bar_Selector, timeout=10000)

        tabs = page.query_selector_all(_Tab_Selector)
        tab_count = len(tabs)
        assert tab_count == 2, f'Expected 2 overlay tabs, got {tab_count}'

        raw_label = tabs[0].inner_text().strip()
        parsed_label = tabs[1].inner_text().strip()
        assert raw_label == _Raw_Tab_Label, f'Expected the first tab to be "{_Raw_Tab_Label}", got: "{raw_label}"'
        assert parsed_label == _Parsed_Tab_Label, f'Expected the second tab to be "{_Parsed_Tab_Label}", got: "{parsed_label}"'

        # .. the raw one is active first, with the complete wire payload ..
        active_label = page.inner_text(_Active_Tab_Selector).strip()
        assert active_label == _Raw_Tab_Label, f'Expected the "{_Raw_Tab_Label}" tab to be active, got: "{active_label}"'

        editor_text = _get_editor_text(page)
        assert editor_text == _purchase_order_850, f'Expected the raw wire payload, got: "{editor_text}"'

        # .. and clicking the parsed one swaps in the human-readable document view.
        page.click(f'{_Tab_Selector}:has-text("{_Parsed_Tab_Label}")')

        active_label = page.inner_text(_Active_Tab_Selector).strip()
        assert active_label == _Parsed_Tab_Label, \
            f'Expected the "{_Parsed_Tab_Label}" tab to be active, got: "{active_label}"'

        editor_text = _get_editor_text(page)

        # The elements show with their dictionary names next to the wire values ..
        assert f'po_number: {_PO_Number}' in editor_text, f'Expected a named po_number element, got: "{editor_text}"'
        assert 'sender_id: SENDERID' in editor_text, f'Expected a named sender_id element, got: "{editor_text}"'

        # .. and the purchase order line loop is indented.
        assert '\n    PO1 - ' in editor_text, f'Expected an indented PO1 loop, got: "{editor_text}"'
        assert '\n        quantity: 10' in editor_text, f'Expected an indented quantity element, got: "{editor_text}"'

# ################################################################################################################################

    def test_non_edi_payload_keeps_the_raw_view_only(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The identities are unique per run so only this test's events show up.
        suffix = CryptoManager.generate_hex_string().upper()
        pair = f'ZATORETAIL{suffix}:PARTNERCORP{suffix}'

        # Seed one event whose payload is JSON, not an EDI document.
        json_data = dumps({'control_number': '905', 'status': 'accepted'})

        audit_log = AuditLog('audit-log-test')
        audit_log.insert(AuditSource.X12, AuditEvent.Ack_Received, pair, cid='cid-ack-' + suffix, msg_id='905',
            size=len(json_data), data=json_data)

        # Open the page pre-filtered to that pair and open the overlay of the newest event.
        goto_audit_log(page, base_url, _Audit_Source, pair)
        _open_message_overlay(page)

        # A payload without an EDI document has no tab bar at all ..
        tab_bar = page.query_selector(_Tab_Bar_Selector)
        assert tab_bar is None, 'Expected no overlay tabs for a non-EDI payload'

        # .. and the editor holds the raw payload itself.
        editor_text = _get_editor_text(page)
        assert editor_text == json_data, f'Expected the raw JSON payload, got: "{editor_text}"'

# ################################################################################################################################
# ################################################################################################################################
