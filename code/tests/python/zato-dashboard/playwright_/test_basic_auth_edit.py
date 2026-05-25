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

_Test_Name_Prefix = 'test.edit.auth.' + os.urandom(4).hex() + '.'

# ################################################################################################################################
# ################################################################################################################################

def _create_definition(page:'Page', base_url:'str', suffix:'str') -> 'dict':
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
    }

    return out

# ################################################################################################################################

def _click_edit_for_row(page:'Page', name:'str') -> 'None':
    """ Finds the row with the given name and opens its edit dialog.
    """

    # Extract the row's item ID from the hidden td ..
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    row = page.query_selector(row_selector)
    id_cell = row.query_selector('td[class*="item_id_"]')
    item_id = id_cell.inner_text().strip()

    # .. call the edit function directly via JS ..
    page.evaluate(f'$.fn.zato.security.basic_auth.edit("{item_id}")')
    page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################
# ################################################################################################################################

class TestBasicAuthEdit:
    """ Tests for the basic auth edit flow.
    """

    def test_09_duplicate_name_in_edit_shows_taken(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates two definitions A and B. Opens edit for A and types B's name.
        Asserts the 'Already taken' indicator appears.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create two definitions ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn_a = _create_definition(page, base_url, 'dup-edit-a')
        defn_b = _create_definition(page, base_url, 'dup-edit-b')

        # .. reload so the server knows about both for the uniqueness check ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open edit for A ..
        _click_edit_for_row(page, defn_a['name'])

        # .. clear the name field and type B's name ..
        name_field = page.locator('#id_edit-name')
        name_field.fill('')
        name_field.click()
        name_field.press_sequentially(defn_b['name'], delay=10)

        # .. wait for the uniqueness indicator ..
        taken_indicator = page.wait_for_selector(
            '#edit-form .zato-unique-taken', state='visible', timeout=10000)

        taken_text = taken_indicator.inner_text()
        assert 'Already taken' in taken_text, f'Expected "Already taken", got: "{taken_text}"'

# ################################################################################################################################

    def test_10_edit_keep_same_name_no_indicator(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Opens edit for a definition without changing the name.
        Asserts no uniqueness indicator appears because the original value check skips it.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create a definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, base_url, 'keep-same')

        # .. reload so the server knows about it ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open edit ..
        _click_edit_for_row(page, defn['name'])

        # .. dispatch an input event on the name field without changing the value ..
        page.evaluate('document.querySelector("#id_edit-name").dispatchEvent(new Event("input"))')

        # .. wait enough time for any indicator to appear ..
        time.sleep(0.8)

        # .. assert no indicator was created.
        indicators = page.query_selector_all('#edit-form .zato-unique-indicator')
        indicator_count = len(indicators)
        assert indicator_count == 0, f'Expected 0 indicators, found: {indicator_count}'

# ################################################################################################################################

    def test_11_edit_name(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Opens edit, verifies pre-populated values, changes the name,
        submits, and verifies the table row updates.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create a definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, base_url, 'edit-name')

        # .. open edit ..
        _click_edit_for_row(page, defn['name'])

        # .. verify the fields are pre-populated ..
        assert page.input_value('#id_edit-name') == defn['name'], 'Name not pre-populated'
        assert page.input_value('#id_edit-username') == defn['username'], 'Username not pre-populated'
        assert page.input_value('#id_edit-realm') == defn['realm'], 'Realm not pre-populated'

        # .. change the name ..
        new_name = _Test_Name_Prefix + 'edit-name-new'
        page.fill('#id_edit-name', new_name)

        # .. submit ..
        page.click('#edit-div input[type="submit"]')
        page.wait_for_selector('#edit-div', state='hidden', timeout=10000)

        # .. verify the row now shows the new name ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{new_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)
        cells = row.query_selector_all('td')

        name_cell_text = cells[2].inner_text().strip()
        assert name_cell_text == new_name, f'Expected "{new_name}", got: "{name_cell_text}"'

        # .. verify the old name is gone.
        old_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{defn["name"]}"))')
        assert old_row is None, f'Old name "{defn["name"]}" should not be in the table'

# ################################################################################################################################

    def test_12_edit_username_and_realm(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Edits only username and realm, leaving name unchanged.
        Asserts the row reflects the changes while name stays the same.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create a definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, base_url, 'edit-user-realm')

        # .. open edit ..
        _click_edit_for_row(page, defn['name'])

        # .. change username and realm only ..
        new_username = 'new-user.' + defn['name']
        new_realm = 'new-realm.' + defn['name']

        page.fill('#id_edit-username', new_username)
        page.fill('#id_edit-realm', new_realm)

        # .. submit ..
        page.click('#edit-div input[type="submit"]')
        page.wait_for_selector('#edit-div', state='hidden', timeout=10000)

        # .. verify the row ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{defn["name"]}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)
        cells = row.query_selector_all('td')

        assert cells[2].inner_text().strip() == defn['name'], 'Name should be unchanged'
        assert cells[3].inner_text().strip() == new_username, \
            f'Expected username "{new_username}", got: "{cells[3].inner_text().strip()}"'
        assert cells[4].inner_text().strip() == new_realm, \
            f'Expected realm "{new_realm}", got: "{cells[4].inner_text().strip()}"'

# ################################################################################################################################

    def test_13_edit_all_fields(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Changes name, username, and realm all at once.
        Asserts all three cells update in the table row.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create a definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, base_url, 'edit-all')

        # .. open edit ..
        _click_edit_for_row(page, defn['name'])

        # .. change all fields ..
        new_name = _Test_Name_Prefix + 'edit-all-new'
        new_username = 'all-user.' + new_name
        new_realm = 'all-realm.' + new_name

        page.fill('#id_edit-name', new_name)
        page.fill('#id_edit-username', new_username)
        page.fill('#id_edit-realm', new_realm)

        # .. submit ..
        page.click('#edit-div input[type="submit"]')
        page.wait_for_selector('#edit-div', state='hidden', timeout=10000)

        # .. verify all three cells ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{new_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)
        cells = row.query_selector_all('td')

        assert cells[2].inner_text().strip() == new_name
        assert cells[3].inner_text().strip() == new_username
        assert cells[4].inner_text().strip() == new_realm

        # .. verify the old name is gone.
        old_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{defn["name"]}"))')
        assert old_row is None, f'Old name "{defn["name"]}" should not be in the table'

# ################################################################################################################################

    def test_14_edit_success_tooltip(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ After a successful edit, the row gets class 'updated'
        and a tippy tooltip with 'OK, saved' appears briefly.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create a definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, base_url, 'tooltip')

        # .. open edit and change username to trigger an actual edit ..
        _click_edit_for_row(page, defn['name'])
        page.fill('#id_edit-username', 'tooltip-user-changed')

        # .. submit ..
        page.click('#edit-div input[type="submit"]')
        page.wait_for_selector('#edit-div', state='hidden', timeout=10000)

        # .. find the row and verify it has the 'updated' class ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{defn["name"]}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)
        row_class = row.get_attribute('class')
        assert 'updated' in row_class, f'Expected "updated" in row class, got: "{row_class}"'

        # .. verify the tippy tooltip appears with 'OK, saved' ..
        tooltip = page.wait_for_selector('.tippy-content', state='visible', timeout=3000)
        tooltip_text = tooltip.inner_text()
        assert 'OK, saved' in tooltip_text, f'Expected "OK, saved" in tooltip, got: "{tooltip_text}"'

# ################################################################################################################################

    def test_15_edit_cancel_values_unchanged(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Opens edit, changes the name, cancels via dialog close,
        and verifies the table row still shows the original name.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create a definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, base_url, 'edit-cancel')

        # .. open edit and change the name ..
        _click_edit_for_row(page, defn['name'])
        changed_name = _Test_Name_Prefix + 'edit-cancel-changed'
        page.fill('#id_edit-name', changed_name)

        # .. close the dialog without submitting ..
        page.evaluate('$("#edit-div").dialog("close")')
        page.wait_for_function('!document.querySelector("#edit-div").offsetParent')

        # .. verify the row still has the original name ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{defn["name"]}"))'
        row = page.query_selector(row_selector)
        assert row is not None, f'Original name "{defn["name"]}" should still be in the table'

        cells = row.query_selector_all('td')
        assert cells[2].inner_text().strip() == defn['name']

        # .. verify the changed name is not in the table.
        changed_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{changed_name}"))')
        assert changed_row is None, f'Changed name "{changed_name}" should not be in the table'

# ################################################################################################################################

    def test_16_edit_then_reopen_shows_current_values(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Edits the name, then re-opens edit on the same row.
        Asserts the dialog shows the post-edit (new) values.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create a definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, base_url, 'reopen-edit')

        # .. open edit and change the name ..
        _click_edit_for_row(page, defn['name'])
        new_name = _Test_Name_Prefix + 'reopen-edit-new'
        page.fill('#id_edit-name', new_name)

        # .. submit ..
        page.click('#edit-div input[type="submit"]')
        page.wait_for_selector('#edit-div', state='hidden', timeout=10000)

        # .. wait for the row with the new name ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{new_name}"))'
        page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. open edit again on the same row ..
        _click_edit_for_row(page, new_name)

        # .. verify the dialog shows the new name.
        current_name = page.input_value('#id_edit-name')
        assert current_name == new_name, f'Expected "{new_name}" in edit dialog, got: "{current_name}"'

# ################################################################################################################################

    def test_17_edit_one_then_edit_another(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Opens edit for row A, closes it, then opens edit for row B.
        Asserts the dialog shows B's values, not A's.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create two definitions ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn_a = _create_definition(page, base_url, 'switch-a')
        defn_b = _create_definition(page, base_url, 'switch-b')

        # .. open edit for A ..
        _click_edit_for_row(page, defn_a['name'])
        assert page.input_value('#id_edit-name') == defn_a['name']

        # .. close A's dialog ..
        page.evaluate('$("#edit-div").dialog("close")')
        page.wait_for_function('!document.querySelector("#edit-div").offsetParent')

        # .. open edit for B ..
        _click_edit_for_row(page, defn_b['name'])

        # .. verify the dialog shows B's values.
        assert page.input_value('#id_edit-name') == defn_b['name'], \
            f'Expected B name "{defn_b["name"]}", got: "{page.input_value("#id_edit-name")}"'
        assert page.input_value('#id_edit-username') == defn_b['username'], \
            f'Expected B username "{defn_b["username"]}", got: "{page.input_value("#id_edit-username")}"'
        assert page.input_value('#id_edit-realm') == defn_b['realm'], \
            f'Expected B realm "{defn_b["realm"]}", got: "{page.input_value("#id_edit-realm")}"'

# ################################################################################################################################

    def test_18_edit_reopen_form_clean_of_indicators(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Opens edit for A, triggers a uniqueness indicator by typing B's name,
        closes the dialog, then opens edit for B.
        Asserts no leftover indicator spans remain in the edit form.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create two definitions ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn_a = _create_definition(page, base_url, 'indicator-a')
        defn_b = _create_definition(page, base_url, 'indicator-b')

        # .. reload with query filter so both test rows are visible ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}&query={_Test_Name_Prefix}indicator')
        page.wait_for_selector('#data-table', state='visible')

        # .. open edit for A and type B's name to trigger the taken indicator ..
        _click_edit_for_row(page, defn_a['name'])

        name_field = page.locator('#id_edit-name')
        name_field.fill('')
        name_field.click()
        name_field.press_sequentially(defn_b['name'], delay=10)

        page.wait_for_selector('#edit-form .zato-unique-taken', state='visible', timeout=10000)

        # .. close the dialog ..
        page.evaluate('$("#edit-div").dialog("close")')
        page.wait_for_function('!document.querySelector("#edit-div").offsetParent')

        # .. open edit for B ..
        _click_edit_for_row(page, defn_b['name'])

        # .. verify no leftover indicators.
        indicators = page.query_selector_all('#edit-form .zato-unique-indicator')
        indicator_count = len(indicators)
        assert indicator_count == 0, f'Expected 0 indicators after reopen, found: {indicator_count}'

# ################################################################################################################################
# ################################################################################################################################
