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

_Audit_Source = 'mllp-channel'

# The tab labels of the message overlay when the payload carries an HL7 message
_Raw_Tab_Label    = 'Raw'
_Parsed_Tab_Label = 'Parsed'

# The overlay elements the tests look at
_Overlay_Selector    = '#zato-highlight-pane-overlay'
_Tab_Bar_Selector    = _Overlay_Selector + ' .zato-highlight-pane-overlay-tabs'
_Tab_Selector        = _Overlay_Selector + ' .zato-highlight-pane-overlay-tab'
_Active_Tab_Selector = _Overlay_Selector + ' .zato-highlight-pane-overlay-tab-active'

# The raw HL7 v2 admission the seeded event carries as its payload.
_admission_a01 = 'MSH|^~\\&|SENDAPP|SENDFAC|RECVAPP|RECVFAC|20260709120000||ADT^A01|MSG00001|P|2.5\r' + \
    'EVN|A01|20260709120000\r' + \
    'PID|1||MRN12345^^^HOSP^MR||Doe^Jane||19800101|F\r'

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
    """ The message overlay of the audit log - a payload that carries an HL7 message
    shows the raw wire format and its parsed rendering side by side, as two tabs,
    while any other payload keeps the raw view only.
    """

# ################################################################################################################################

    def test_hl7_payload_shows_raw_and_parsed_tabs(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The channel name is unique per run so only this test's events show up.
        suffix = CryptoManager.generate_hex_string().upper()
        channel_name = f'test.mllp.parsed.{suffix}'

        # Seed one event whose payload is a complete HL7 message ..
        audit_log = AuditLog('audit-log-test')
        audit_log.insert(AuditSource.MLLP_Channel, AuditEvent.Message_Received, channel_name, cid='cid-hl7-' + suffix,
            msg_id='MSG00001', size=len(_admission_a01), data=_admission_a01)

        # .. open the page pre-filtered to that channel and open the message overlay.
        goto_audit_log(page, base_url, _Audit_Source, channel_name)
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

        # .. the raw one is active first, with the complete wire payload, one segment to a line ..
        active_label = page.inner_text(_Active_Tab_Selector).strip()
        assert active_label == _Raw_Tab_Label, f'Expected the "{_Raw_Tab_Label}" tab to be active, got: "{active_label}"'

        editor_text = _get_editor_text(page)
        assert editor_text.splitlines() == _admission_a01.splitlines(), f'Expected the raw wire payload, got: "{editor_text}"'

        # .. and clicking the parsed one swaps in the human-readable message view.
        page.click(f'{_Tab_Selector}:has-text("{_Parsed_Tab_Label}")')

        active_label = page.inner_text(_Active_Tab_Selector).strip()
        assert active_label == _Parsed_Tab_Label, \
            f'Expected the "{_Parsed_Tab_Label}" tab to be active, got: "{active_label}"'

        editor_text = _get_editor_text(page)

        # The fields show with their names next to the wire values ..
        assert 'MSH-9  Message Type: ADT^A01' in editor_text, f'Expected a named message type, got: "{editor_text}"'
        assert 'PID-5  Patient Name: Doe^Jane' in editor_text, f'Expected a named patient name, got: "{editor_text}"'

        # .. and the components are indented under their fields.
        assert '\n      PID-5.1  Family Name: Doe' in editor_text, f'Expected an indented component, got: "{editor_text}"'

# ################################################################################################################################

    def test_non_hl7_payload_keeps_the_raw_view_only(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The channel name is unique per run so only this test's events show up.
        suffix = CryptoManager.generate_hex_string().upper()
        channel_name = f'test.mllp.parsed.{suffix}'

        # Seed one event whose payload is JSON, not an HL7 message.
        json_data = dumps({'status': 'accepted'})

        audit_log = AuditLog('audit-log-test')
        audit_log.insert(AuditSource.MLLP_Channel, AuditEvent.Message_Received, channel_name, cid='cid-json-' + suffix,
            size=len(json_data), data=json_data)

        # Open the page pre-filtered to that channel and open the overlay of the newest event.
        goto_audit_log(page, base_url, _Audit_Source, channel_name)
        _open_message_overlay(page)

        # A payload without an HL7 message has no tab bar at all ..
        tab_bar = page.query_selector(_Tab_Bar_Selector)
        assert tab_bar is None, 'Expected no overlay tabs for a non-HL7 payload'

        # .. and the editor holds the raw payload itself.
        editor_text = _get_editor_text(page)
        assert editor_text == json_data, f'Expected the raw JSON payload, got: "{editor_text}"'

# ################################################################################################################################
# ################################################################################################################################
