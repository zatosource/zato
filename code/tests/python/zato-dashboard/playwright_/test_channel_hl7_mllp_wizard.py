# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/channel/hl7/mllp/?cluster=1&type_=channel-hl7-mllp'
_Outgoing_Url_Pattern = '/zato/outgoing/hl7/mllp/?cluster=1&type_=outconn-hl7-mllp'

_Test_Name_Prefix = 'test.mllp.wizard.' + CryptoManager.generate_hex_string(32) + '.'

# The service every channel in these tests invokes - it exists in each test environment
_Test_Service = 'demo.ping'

# Where the outgoing connection the destination points at would deliver - nothing listens there,
# the wizard only stores the destination
_Outconn_Address = '127.0.0.1:17999'

# The badge picker the wizard's destinations panel runs on
_Picker_Action = 'mllp-wizard-destinations'

# ################################################################################################################################
# ################################################################################################################################

def _navigate_to_mllp(page:'Page', base_url:'str') -> 'None':
    """ Opens the HL7 MLLP channels page and waits for the data table.
    """
    _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
    page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def _navigate_to_outgoing_mllp(page:'Page', base_url:'str') -> 'None':
    """ Opens the outgoing HL7 MLLP connections page and waits for the data table.
    """
    _ = page.goto(f'{base_url}{_Outgoing_Url_Pattern}')
    _ = page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def _create_outgoing_connection(page:'Page', base_url:'str', name:'str') -> 'None':
    """ Creates the outgoing MLLP connection a destination of the wizard points at.
    """
    _navigate_to_outgoing_mllp(page, base_url)

    page.click('#markup .page_prompt a:has-text("Create a new connection")')
    _ = page.wait_for_selector('#create-div', state='visible')

    page.fill('#id_name', name)
    page.fill('#id_address', _Outconn_Address)

    page.click('#create-div input[type="submit"]')
    _ = page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    _ = page.wait_for_selector(f'#data-table tbody tr:has(td:text-is("{name}"))', state='visible', timeout=5000)

# ################################################################################################################################

def _delete_outgoing_connection(page:'Page', base_url:'str', name:'str') -> 'None':
    """ Deletes the outgoing MLLP connection the test created.
    """
    _navigate_to_outgoing_mllp(page, base_url)

    item_id = _get_item_id(page, name)

    page.evaluate(f'$.fn.zato.outgoing.hl7.mllp.delete_("{item_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=5000)
    page.click('#popup_ok')
    time.sleep(0.5)

# ################################################################################################################################

def _get_item_id(page:'Page', name:'str') -> 'str':
    """ Extracts the server-side ID of a row by its name.
    """
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    row = page.query_selector(row_selector)
    id_cell = row.query_selector('td[class*="item_id_"]')
    out = id_cell.inner_text().strip()

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestChannelHL7MLLPWizard:
    """ Walks the MLLP channel wizard end to end - a regression check that the wizard,
    now a wizard-kit instance, still creates channels through all three steps.
    """

    def test_mllp_wizard_full_cycle(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Collect console errors along the way ..
        console_errors = [] # type: list

        def _on_console(msg:'object') -> 'None':
            if msg.type == 'error':
                console_errors.append(msg.text)

        page.on('console', _on_console)

        # .. and server errors too.
        server_errors = [] # type: list

        def _on_response(response:'object') -> 'None':
            if response.status >= 500:
                server_errors.append(f'{response.status} {response.url}')

        page.on('response', _on_response)

        # The connection the channel's destination points at has to exist before the wizard
        # opens, so the destinations panel has it to offer
        outconn_name = _Test_Name_Prefix + 'outconn'
        _create_outgoing_connection(page, base_url, outconn_name)

        _navigate_to_mllp(page, base_url)

        # Open the wizard from the list page
        page.click('#markup .page_prompt a:has-text("Create a new channel")')
        page.wait_for_selector('#mllp-wizard', state='visible')

        # Step 1 - the name, everything else keeps its defaults
        channel_name = _Test_Name_Prefix + 'channel'

        page.fill('#id_name', channel_name)

        # The header badge mirrors the name as it is typed
        badge_text = page.inner_text('#mllp-wizard-name-badge')
        assert channel_name in badge_text, f'Expected "{channel_name}" in the name badge, got: "{badge_text}"'

        page.click('#mllp-wizard-next')
        time.sleep(0.2)

        # Step 2 - the target service, picked through the underlying chosen select
        page.evaluate(f'$("#id_service").val("{_Test_Service}").trigger("chosen:updated")')

        # The destinations panel offers only the connections it has already loaded
        _ = page.wait_for_function('$.fn.zato.channel.hl7.mllp.wizard.destinations._connectionData !== null')

        # Open the destinations panel and pick the connection the test created
        page.click('#mllp-wizard-slot-destinations-chip')
        _ = page.wait_for_selector('#wizard-panel', state='visible')

        available_badge = f'#badge-zone-available-{_Picker_Action} .security-badge[data-connection="{outconn_name}"]'
        assigned_badge = f'#badge-zone-assigned-{_Picker_Action} .security-badge[data-connection="{outconn_name}"]'

        page.click(f'{available_badge} .security-badge-name')
        _ = page.wait_for_selector(assigned_badge, state='visible', timeout=5000)

        # Closing the panel is what writes the picked destination into the wizard's state
        page.click('#mllp-wizard-slot-destinations-chip')
        _ = page.wait_for_selector('#wizard-panel', state='detached')

        chip_text = page.inner_text('#mllp-wizard-slot-destinations-chip')
        assert '1 destination' in chip_text, f'Expected "1 destination" on the chip, got: "{chip_text}"'

        page.click('#mllp-wizard-next')
        time.sleep(0.2)

        # Step 3 - the review shows what was filled in, the destination included
        review_text = page.inner_text('#mllp-wizard-review')

        assert channel_name in review_text, f'Expected "{channel_name}" in the review, got: "{review_text}"'
        assert _Test_Service in review_text, f'Expected "{_Test_Service}" in the review, got: "{review_text}"'
        assert outconn_name in review_text, f'Expected "{outconn_name}" in the review, got: "{review_text}"'

        # Finish - back on the list with the new channel
        page.click('#mllp-wizard-next')
        page.wait_for_url('**/zato/channel/hl7/mllp/**', timeout=10000)
        page.wait_for_selector('#data-table', state='visible')

        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{channel_name}"))')
        assert row is not None, f'Channel "{channel_name}" should be on the list after the wizard'

        row_text = row.inner_text()
        assert _Test_Service in row_text, f'Expected the service in the row, got: "{row_text}"'

        # The created channel stores the destination - the full-page editor reads it back
        # into its hidden JSON field
        item_id = _get_item_id(page, channel_name)

        _ = page.goto(f'{base_url}/zato/channel/hl7/mllp/editor/{item_id}/?cluster=1')
        _ = page.wait_for_selector('#id_edit-destinations', state='attached')
        _ = page.wait_for_function('document.querySelector("#id_edit-destinations").value !== ""')

        stored_destinations = page.input_value('#id_edit-destinations')

        assert outconn_name in stored_destinations, \
            f'Expected "{outconn_name}" among the stored destinations, got: "{stored_destinations}"'

        assert 'hl7-mllp' in stored_destinations, \
            f'Expected the destination type among the stored destinations, got: "{stored_destinations}"'

        # Delete the channel the test created
        _navigate_to_mllp(page, base_url)
        item_id = _get_item_id(page, channel_name)

        page.evaluate(f'$.fn.zato.channel.hl7.mllp.delete_("{item_id}")')
        page.wait_for_selector('#popup_container', state='visible', timeout=5000)
        page.click('#popup_ok')
        time.sleep(0.5)

        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{channel_name}"))')
        assert row is None, f'Channel "{channel_name}" should be gone after delete'

        # Delete the outgoing connection the destination pointed at
        _delete_outgoing_connection(page, base_url, outconn_name)

        # No console or server errors along the way
        real_errors = [] # type: list

        for error_text in console_errors:
            if 'favicon.ico' in error_text or 'Content-Security-Policy' in error_text:
                continue
            real_errors.append(error_text)

        assert not real_errors, 'Console errors during the MLLP wizard cycle:\n' + '\n'.join(real_errors)
        assert not server_errors, 'HTTP 500+ responses during the MLLP wizard cycle:\n' + '\n'.join(server_errors)

# ################################################################################################################################
# ################################################################################################################################
