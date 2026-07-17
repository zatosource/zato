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

_Tier_List_Url = '/zato/security/tier/?cluster=1'
_Tier_Create_Url = '/zato/security/tier/create/?cluster=1'
_APIKey_List_Url = '/zato/security/apikey/?cluster=1'

_Test_Name_Prefix = 'test.quota.tier.' + CryptoManager.generate_hex_string(16) + '.'

# ################################################################################################################################
# ################################################################################################################################

def _create_tier(page:'Page', base_url:'str', name:'str') -> 'None':
    """ Creates a quota tier through the tier editor.
    """

    # Open the editor ..
    _ = page.goto(f'{base_url}{_Tier_Create_Url}')
    page.wait_for_selector('#rate-limiting-container .rate-limiting-rule', state='visible')

    # .. fill in the tier's details ..
    page.fill('#tier-name', name)
    page.fill('#tier-description', 'Playwright test tier')

    # .. fill in the all-day slot's limits ..
    page.fill('#rate-limiting-container [data-field="rate"]', '100')
    page.fill('#rate-limiting-container [data-field="burst"]', '200')
    page.fill('#rate-limiting-container [data-field="limit"]', '1000')

    # .. save and wait for the redirect to the list page.
    page.click('.rate-limiting-actions input[type="submit"]')
    page.wait_for_url(f'{base_url}/zato/security/tier/', timeout=10000)

# ################################################################################################################################

def _delete_tier(page:'Page', base_url:'str', name:'str') -> 'None':
    """ Deletes a quota tier from the list page.
    """

    _ = page.goto(f'{base_url}{_Tier_List_Url}')
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible')

    # The delete link asks for confirmation through a browser dialog
    page.once('dialog', lambda dialog: dialog.accept())

    row = page.query_selector(row_selector)
    delete_link = row.query_selector('a:text("Delete")')
    delete_link.click()

    # The page reloads after a successful delete
    page.wait_for_selector(row_selector, state='detached', timeout=10000)

# ################################################################################################################################

def _create_apikey(page:'Page', base_url:'str', name:'str') -> 'str':
    """ Creates an API key definition and returns its id.
    """

    _ = page.goto(f'{base_url}{_APIKey_List_Url}')
    page.wait_for_selector('#data-table', state='visible')

    # Open the create dialog ..
    page.click('#markup .page_prompt a')
    page.wait_for_selector('#create-div', state='visible')

    # .. fill in the fields ..
    page.fill('#id_name', name)
    page.fill('#id_password', 'key.' + CryptoManager.generate_hex_string())

    # .. submit and wait for the row to appear ..
    page.click('#create-div input[type="submit"]')
    page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=5000)

    # .. and extract the new row's id.
    row = page.query_selector(row_selector)
    id_cell = row.query_selector('td[class*="item_id_"]')
    out = id_cell.inner_text().strip()

    return out

# ################################################################################################################################

def _delete_apikey(page:'Page', base_url:'str', item_id:'str') -> 'None':
    """ Deletes an API key definition by its id.
    """

    _ = page.goto(f'{base_url}{_APIKey_List_Url}')
    page.wait_for_selector('#data-table', state='visible')

    page.evaluate(f'$.fn.zato.security.apikey.delete_("{item_id}")')
    page.wait_for_selector('#popup_container', state='visible', timeout=5000)
    page.click('#popup_ok')
    time.sleep(0.5)

# ################################################################################################################################
# ################################################################################################################################

class TestQuotaTierLifecycle:
    """ Creates a tier, assigns it to an API key definition and verifies the tier vs. custom rules tabs round-trip.
    """

    def test_tier_assignment_round_trip(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        tier_name = _Test_Name_Prefix + 'gold'
        apikey_name = _Test_Name_Prefix + 'apikey'

        # Create the tier and the definition ..
        _create_tier(page, base_url, tier_name)
        apikey_id = _create_apikey(page, base_url, apikey_name)

        try:

            # .. the tier appears on the list page with its limits ..
            _ = page.goto(f'{base_url}{_Tier_List_Url}')
            tier_row_selector = f'#data-table tbody tr:has(td:text-is("{tier_name}"))'
            page.wait_for_selector(tier_row_selector, state='visible')

            tier_row = page.query_selector(tier_row_selector)
            row_text = tier_row.inner_text()
            assert '100/sec' in row_text, f'Expected "100/sec" in the tier row, got: "{row_text}"'
            assert '1000/minute' in row_text, f'Expected "1000/minute" in the tier row, got: "{row_text}"'

            # .. open the definition's rate limiting page ..
            rate_limiting_url = f'{base_url}/zato/security/apikey/rate-limiting/{apikey_id}/?cluster=1&name={apikey_name}'
            _ = page.goto(rate_limiting_url)
            page.wait_for_selector('.dashboard-tab[data-mode="tier"]', state='visible')

            # .. with no tier assigned, the custom rules tab is active and the rule builder is visible ..
            assert page.is_visible('.dashboard-tab[data-mode="custom"].dashboard-tab-active'), \
                'Custom rules tab should be active without a tier'
            assert page.is_visible('#rate-limiting-container'), 'Rule builder should be visible without a tier'

            # .. switch to the quota tier tab and pick the tier - the rule builder hides ..
            page.click('.dashboard-tab[data-mode="tier"]')
            page.wait_for_selector('#quota-tier-select', state='visible')

            _ = page.select_option('#quota-tier-select', label=tier_name)
            assert not page.is_visible('#rate-limiting-container'), 'Rule builder should hide when a tier is selected'

            # .. save and wait for the confirmation ..
            page.click('.rate-limiting-actions input[type="submit"]')
            page.wait_for_selector('#rate-limiting-status:has-text("OK, saved")', timeout=10000)

            # .. reload - the tier tab round-trips as the active one and the builder stays hidden ..
            _ = page.goto(rate_limiting_url)
            page.wait_for_selector('.dashboard-tab[data-mode="tier"].dashboard-tab-active', state='visible')
            page.wait_for_selector('#quota-tier-select', state='visible')

            selected_label = page.eval_on_selector(
                '#quota-tier-select', 'select => select.options[select.selectedIndex].text')
            assert selected_label == tier_name, f'Expected "{tier_name}" selected after a reload, got: "{selected_label}"'
            assert not page.is_visible('#rate-limiting-container'), 'Rule builder should stay hidden after a reload'

            # .. a referenced tier must not be deletable ..
            _ = page.goto(f'{base_url}{_Tier_List_Url}')
            page.wait_for_selector(tier_row_selector, state='visible')

            referent_count = page.query_selector(f'{tier_row_selector} td.text-center').inner_text().strip()
            assert referent_count == '1', f'Expected a referent count of 1, got: "{referent_count}"'

            # .. switch the definition back to custom rules ..
            _ = page.goto(rate_limiting_url)
            page.wait_for_selector('.dashboard-tab[data-mode="custom"]', state='visible')

            page.click('.dashboard-tab[data-mode="custom"]')
            assert page.is_visible('#rate-limiting-container'), 'Rule builder should show for custom rules'

            page.click('.rate-limiting-actions input[type="submit"]')
            page.wait_for_selector('#rate-limiting-status:has-text("OK, saved")', timeout=10000)

            # .. and the switch round-trips too.
            _ = page.goto(rate_limiting_url)
            page.wait_for_selector('.dashboard-tab[data-mode="custom"].dashboard-tab-active', state='visible')

            assert page.is_visible('#rate-limiting-container'), 'Rule builder should stay visible after a reload'

        finally:

            # Clean up - the definition first, the tier is unreferenced by then.
            _delete_apikey(page, base_url, apikey_id)
            _delete_tier(page, base_url, tier_name)

# ################################################################################################################################
# ################################################################################################################################
