# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/security/basic-auth/?cluster=1'

_Test_Name_Prefix = 'test.inter.' + os.urandom(4).hex() + '.'

# ################################################################################################################################
# ################################################################################################################################

def _create_definition(page:'Page', suffix:'str') -> 'dict':
    """ Creates a basic auth definition via the UI and returns its details.
    """

    name = _Test_Name_Prefix + suffix
    username = 'user.' + name
    realm = 'realm.' + name
    password = 'password.' + os.urandom(8).hex()

    # Open the create dialog ..
    page.click('#markup .page_prompt a')
    page.wait_for_selector('#create-div', state='visible')

    # .. fill in the fields ..
    page.fill('#id_name', name)
    page.fill('#id_username', username)
    page.fill('#id_realm', realm)
    page.fill('#id_password', password)

    # .. submit and wait for the dialog to close ..
    page.click('#create-div input[type="submit"]')
    page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    # .. wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=5000)

    out = {
        'name': name,
        'username': username,
        'realm': realm,
        'password': password,
    }

    return out

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

class TestBasicAuthInteraction:
    """ Tests for keyboard shortcuts, dialog dismiss patterns, double submit, refresh, and hidden fields.
    """

    def test_40_submit_via_enter_key(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Fills the create form and presses Enter instead of clicking the submit button.
        The form should submit and a new row should appear.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'enter-key'

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open the create dialog ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        # .. fill in the fields ..
        page.fill('#id_name', name)
        page.fill('#id_username', 'user.' + name)
        page.fill('#id_realm', 'realm.' + name)
        page.fill('#id_password', 'pwd.' + os.urandom(4).hex())

        # .. press Enter on the password field to submit ..
        page.press('#id_password', 'Enter')

        # .. wait for the dialog to close and the row to appear.
        page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        row = page.wait_for_selector(
            f'#data-table tbody tr:has(td:text-is("{name}"))', state='visible', timeout=5000)
        assert row is not None, f'Row "{name}" should appear after Enter key submit'

# ################################################################################################################################

    def test_41_dialog_close_via_api(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Opens the create dialog, fills fields, closes via the jQuery dialog API.
        The dialog should close, the form should reset, and no row should be added.
        Note: the standard jQuery UI X button is removed by common.js custom titlebar code,
        so the dialog API call is the programmatic close mechanism.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'api-close'

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        count_before = len(page.query_selector_all('#data-table tbody tr:not(.ignore)'))

        # .. open the create dialog and fill fields ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        page.fill('#id_name', name)
        page.fill('#id_username', 'user.' + name)
        page.fill('#id_realm', 'realm.' + name)
        page.fill('#id_password', 'pwd123')

        # .. verify the standard X button was removed by custom code ..
        has_x_button = page.evaluate("""
        (() => {
            var wrapper = $('#create-div').closest('.ui-dialog');
            return wrapper.find('.ui-dialog-titlebar-close').length;
        })()
        """)
        assert has_x_button == 0, 'Custom titlebar removes the X button'

        # .. close via the dialog API ..
        page.evaluate('$("#create-div").dialog("close")')
        page.wait_for_function('!document.querySelector("#create-div").offsetParent', timeout=5000)

        # .. verify no row was added ..
        count_after = len(page.query_selector_all('#data-table tbody tr:not(.ignore)'))
        assert count_after == count_before, f'Expected {count_before} rows, got: {count_after}'

        # .. verify the name is not in the table.
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is None, f'Row "{name}" should not exist after close'

# ################################################################################################################################

    def test_42_dialog_close_via_escape(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Opens the create dialog, fills fields, presses Escape.
        The dialog should close, the form should reset, and no row should be added.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'escape'

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        count_before = len(page.query_selector_all('#data-table tbody tr:not(.ignore)'))

        # .. open the create dialog and fill fields ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        page.fill('#id_name', name)
        page.fill('#id_username', 'user.' + name)
        page.fill('#id_realm', 'realm.' + name)
        page.fill('#id_password', 'pwd123')

        # .. press Escape to close the dialog ..
        page.keyboard.press('Escape')

        # .. wait for the dialog to close ..
        page.wait_for_function('!document.querySelector("#create-div").offsetParent')

        # .. verify no row was added ..
        count_after = len(page.query_selector_all('#data-table tbody tr:not(.ignore)'))
        assert count_after == count_before, f'Expected {count_before} rows, got: {count_after}'

        # .. verify the name is not in the table ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is None, f'Row "{name}" should not exist after Escape'

        # .. reopen the dialog and verify the form was reset.
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        name_value = page.input_value('#id_name')
        assert name_value == '', f'Expected empty name after Escape+reopen, got: "{name_value}"'

# ################################################################################################################################

    def test_43_double_click_submit(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Fills the create form and clicks OK twice rapidly.
        Only one definition should be created.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'dbl-click'

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open the create dialog and fill fields ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        page.fill('#id_name', name)
        page.fill('#id_username', 'user.' + name)
        page.fill('#id_realm', 'realm.' + name)
        page.fill('#id_password', 'pwd.' + os.urandom(4).hex())

        # .. click submit - the overlay should disable the button immediately ..
        submit_button = page.query_selector('#create-div input[type="submit"]')
        submit_button.click()

        # .. verify the button is disabled after the first click ..
        is_disabled = page.evaluate('document.querySelector("#create-div input[type=submit]").disabled')
        assert is_disabled, 'Submit button should be disabled after first click'

        # .. attempt the second click with force=True to bypass Playwright's actionability checks ..
        submit_button.click(force=True)

        # .. wait for the dialog to close ..
        page.wait_for_selector('#create-div', state='hidden', timeout=10000)
        time.sleep(0.5)

        # .. count how many rows have this name - should be exactly 1 ..
        matching_rows = page.query_selector_all(f'#data-table tbody tr:has(td:text-is("{name}"))')
        row_count = len(matching_rows)
        assert row_count == 1, f'Expected exactly 1 row with name "{name}", got: {row_count}'

# ################################################################################################################################

    def test_44_refresh_persistence(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a definition and refreshes the page.
        The definition should still be in the table after reload.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, 'refresh')

        # .. reload with query filter so the row is visible ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}&query={defn["name"]}')
        page.wait_for_selector('#data-table', state='visible')

        # .. verify the row is still present.
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{defn["name"]}"))')
        assert row is not None, f'Row "{defn["name"]}" should persist after page refresh'

        cells = row.query_selector_all('td')
        assert cells[2].inner_text().strip() == defn['name']
        assert cells[3].inner_text().strip() == defn['username']
        assert cells[4].inner_text().strip() == defn['realm']

# ################################################################################################################################

    def test_45_no_results_to_first_row(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ On a page that may show 'No results', creates the first item
        and verifies the 'No results' placeholder is replaced by a real row.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'first-row'

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create a definition ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        page.fill('#id_name', name)
        page.fill('#id_username', 'user.' + name)
        page.fill('#id_realm', 'realm.' + name)
        page.fill('#id_password', 'pwd.' + os.urandom(4).hex())

        page.click('#create-div input[type="submit"]')
        page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        # .. wait for the new row ..
        row = page.wait_for_selector(
            f'#data-table tbody tr:has(td:text-is("{name}"))', state='visible', timeout=5000)
        assert row is not None, f'Row "{name}" should appear'

        # .. verify there is no 'No results' text in the visible rows.
        visible_cells = page.query_selector_all('#data-table tbody tr:not(.ignore) td:nth-child(3)')

        for cell in visible_cells:
            text = cell.inner_text().strip()
            assert text != 'No results', 'No results placeholder should be replaced by real data'

# ################################################################################################################################

    def test_46_hidden_is_active_sent(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Verifies that the create and edit forms contain hidden is_active and cluster_id fields.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. check the create form's hidden is_active field ..
        create_is_active = page.query_selector('#create-form input[name="is_active"][type="hidden"]')
        assert create_is_active is not None, 'Create form should have hidden is_active input'

        create_is_active_value = create_is_active.get_attribute('value')
        assert create_is_active_value == 'on', f'Expected is_active="on", got: "{create_is_active_value}"'

        # .. check the create form's hidden cluster_id field ..
        create_cluster_id = page.query_selector('#create-form input[name="cluster_id"][type="hidden"]')
        assert create_cluster_id is not None, 'Create form should have hidden cluster_id input'

        create_cluster_id_value = create_cluster_id.get_attribute('value')
        assert create_cluster_id_value == '1', f'Expected cluster_id="1", got: "{create_cluster_id_value}"'

        # .. check the edit form's hidden edit-is_active field ..
        edit_is_active = page.query_selector('#edit-form input[name="edit-is_active"][type="hidden"]')
        assert edit_is_active is not None, 'Edit form should have hidden edit-is_active input'

        edit_is_active_value = edit_is_active.get_attribute('value')
        assert edit_is_active_value == 'on', f'Expected edit-is_active="on", got: "{edit_is_active_value}"'

        # .. check the edit form's hidden cluster_id field.
        edit_cluster_id = page.query_selector('#edit-form input[name="cluster_id"][type="hidden"]')
        assert edit_cluster_id is not None, 'Edit form should have hidden cluster_id input'

        edit_cluster_id_value = edit_cluster_id.get_attribute('value')
        assert edit_cluster_id_value == '1', f'Expected cluster_id="1", got: "{edit_cluster_id_value}"'

# ################################################################################################################################
# ################################################################################################################################
