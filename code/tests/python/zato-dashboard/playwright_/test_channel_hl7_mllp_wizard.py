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

_Test_Name_Prefix = 'test.mllp.wizard.' + CryptoManager.generate_hex_string(32) + '.'

# The service every channel in these tests invokes - it exists in each test environment
_Test_Service = 'demo.ping'

# ################################################################################################################################
# ################################################################################################################################

def _navigate_to_mllp(page:'Page', base_url:'str') -> 'None':
    """ Opens the HL7 MLLP channels page and waits for the data table.
    """
    _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
    page.wait_for_selector('#data-table', state='visible')

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

        page.click('#mllp-wizard-next')
        time.sleep(0.2)

        # Step 3 - the review shows what was filled in
        review_text = page.inner_text('#mllp-wizard-review')

        assert channel_name in review_text, f'Expected "{channel_name}" in the review, got: "{review_text}"'
        assert _Test_Service in review_text, f'Expected "{_Test_Service}" in the review, got: "{review_text}"'

        # Finish - back on the list with the new channel
        page.click('#mllp-wizard-next')
        page.wait_for_url('**/zato/channel/hl7/mllp/**', timeout=10000)
        page.wait_for_selector('#data-table', state='visible')

        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{channel_name}"))')
        assert row is not None, f'Channel "{channel_name}" should be on the list after the wizard'

        row_text = row.inner_text()
        assert _Test_Service in row_text, f'Expected the service in the row, got: "{row_text}"'

        # Delete the channel the test created
        item_id = _get_item_id(page, channel_name)

        page.evaluate(f'$.fn.zato.channel.hl7.mllp.delete_("{item_id}")')
        page.wait_for_selector('#popup_container', state='visible', timeout=5000)
        page.click('#popup_ok')
        time.sleep(0.5)

        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{channel_name}"))')
        assert row is None, f'Channel "{channel_name}" should be gone after delete'

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
