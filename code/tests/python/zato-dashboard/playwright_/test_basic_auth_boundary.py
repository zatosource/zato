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

_Page_Url_Pattern = '/zato/security/basic-auth/?cluster=1'

_Test_Name_Prefix = 'test.bnd.' + CryptoManager.generate_hex_string(32) + '.'

# ################################################################################################################################
# ################################################################################################################################

def _create_definition(page:'Page', name:'str') -> 'dict':
    """ Creates a basic auth definition via the UI with a given name.
    """

    username = 'user.' + name
    realm = 'realm.' + name
    password = 'password.' + CryptoManager.generate_hex_string()

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

def _create_definition_with_realm(page:'Page', name:'str', realm:'str') -> 'dict':
    """ Creates a basic auth definition via the UI with a given name and realm.
    """

    username = 'user.' + name
    password = 'password.' + CryptoManager.generate_hex_string()

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

def _count_data_rows(page:'Page') -> 'int':
    """ Returns the number of data rows, excluding the 'No results' placeholder.
    """

    rows = page.query_selector_all('#data-table tbody tr:not(.ignore)')
    count = 0

    for row in rows:
        first_cell = row.query_selector('td')
        text = first_cell.inner_text().strip()
        if text != 'No results':
            count += 1

    return count

# ################################################################################################################################
# ################################################################################################################################

class TestBasicAuthBoundary:
    """ Tests for boundary values, validation, special characters, and XSS.
    """

    def test_32_create_empty_name_rejected(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Submits create form with name empty. The form stays open,
        the name field gets the attention CSS class, and no row is added.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        count_before = _count_data_rows(page)

        # .. open the create dialog and fill all fields except name ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        page.fill('#id_username', 'user.empty-name')
        page.fill('#id_realm', 'realm.empty-name')
        page.fill('#id_password', 'pwd123')

        # .. click submit ..
        page.click('#create-div input[type="submit"]')
        time.sleep(0.3)

        # .. assert the dialog is still open ..
        is_visible = page.evaluate('!!document.querySelector("#create-div").offsetParent')
        assert is_visible, 'Create dialog should still be open when name is empty'

        # .. assert the name field has the attention CSS class ..
        attention_field = page.query_selector('#id_name.zato-validator-attention')
        assert attention_field is not None, 'Name field should have zato-validator-attention class'

        # .. close the dialog ..
        page.evaluate('$("#create-div").dialog("close")')

        # .. assert no row was added.
        count_after = _count_data_rows(page)
        assert count_after == count_before, \
            f'Expected {count_before} rows, got: {count_after}'

# ################################################################################################################################

    def test_33_create_empty_username_rejected(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Submits create form with username empty. The form stays open,
        the username field gets the attention CSS class, and no row is added.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        count_before = _count_data_rows(page)

        # .. open the create dialog and fill all fields except username ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        page.fill('#id_name', _Test_Name_Prefix + 'empty-username')
        page.fill('#id_realm', 'realm.empty-username')
        page.fill('#id_password', 'pwd123')

        # .. click submit ..
        page.click('#create-div input[type="submit"]')
        time.sleep(0.3)

        # .. assert the dialog is still open ..
        is_visible = page.evaluate('!!document.querySelector("#create-div").offsetParent')
        assert is_visible, 'Create dialog should still be open when username is empty'

        # .. assert the username field has the attention CSS class ..
        attention_field = page.query_selector('#id_username.zato-validator-attention')
        assert attention_field is not None, 'Username field should have zato-validator-attention class'

        # .. close the dialog ..
        page.evaluate('$("#create-div").dialog("close")')

        # .. assert no row was added.
        count_after = _count_data_rows(page)
        assert count_after == count_before, \
            f'Expected {count_before} rows, got: {count_after}'

# ################################################################################################################################

    def test_34_create_with_special_chars(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a definition with HTML special chars in the name.
        After reload, the name is rendered as text, not HTML (Django auto-escaping).
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + '<b>"and"&apos;</b>'

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create the definition ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        page.fill('#id_name', name)
        page.fill('#id_username', 'user.special')
        page.fill('#id_realm', 'realm.special')
        page.fill('#id_password', 'pwd123')

        page.click('#create-div input[type="submit"]')
        page.wait_for_selector('#create-div', state='hidden', timeout=10000)
        time.sleep(0.5)

        # .. reload so Django template escaping applies ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. find the row by text content using JS since the name breaks CSS selectors ..
        js_find = """
        (name) => {
            const rows = document.querySelectorAll('#data-table tbody tr:not(.ignore)');
            for (const row of rows) {
                const cells = row.querySelectorAll('td');
                if (cells.length > 2 && cells[2].innerText.trim() === name) {
                    return {
                        text: cells[2].innerText.trim(),
                        html: cells[2].innerHTML.trim()
                    };
                }
            }
            return null;
        }
        """

        result = page.evaluate(js_find, name)
        assert result is not None, f'Row with special chars name should be present after reload'

        cell_text = result['text']
        cell_html = result['html']

        # .. the text should be the raw name ..
        assert cell_text == name, f'Expected text "{name}", got: "{cell_text}"'

        # .. the HTML should contain escaped entities, not raw tags.
        assert '&lt;' in cell_html, f'Expected escaped HTML, got: "{cell_html}"'
        assert '&gt;' in cell_html, f'Expected escaped HTML, got: "{cell_html}"'

# ################################################################################################################################

    def test_35_create_with_unicode(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a definition with unicode characters in the name.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'zażółć-gęślą-jaźń'

        # Navigate and create ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        _create_definition(page, name)

        # .. verify the row is present with correct text.
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is not None, f'Row with unicode name should be present'

        cells = row.query_selector_all('td')
        cell_text = cells[2].inner_text().strip()
        assert cell_text == name, f'Expected "{name}", got: "{cell_text}"'

# ################################################################################################################################

    def test_36_create_with_long_name(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a definition with a 200-character name. The name is not truncated.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'x' * 180

        # Navigate and create ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        _create_definition(page, name)

        # .. verify the row is present ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is not None, 'Row with long name should be present'

        # .. verify the name is not truncated.
        cells = row.query_selector_all('td')
        cell_text = cells[2].inner_text().strip()
        text_len = len(cell_text)
        assert text_len >= 190, f'Expected name length >= 190, got: {text_len}'

# ################################################################################################################################

    def test_37_create_with_whitespace_name(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Fills the create form with a whitespace-only name and clicks submit.
        The client-side validation should reject it with a "This field is required"
        indicator on the name field, and the form should remain open without
        making a server round-trip.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open and fill the form with spaces-only name ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        page.fill('#id_name', '   ')
        page.fill('#id_username', 'user.whitespace')
        page.fill('#id_realm', 'realm.whitespace')
        page.fill('#id_password', 'pwd123')

        page.click('#create-div input[type="submit"]')
        time.sleep(0.5)

        # .. the dialog must still be open because client-side validation rejected the form ..
        dialog_visible = page.evaluate('document.querySelector("#create-div").offsetParent !== null')
        assert dialog_visible, 'Create dialog should remain open after whitespace-only name submission'

        # .. the name field should have the attention CSS class ..
        has_attention = page.evaluate("""
            document.querySelector('#id_name').classList.contains('zato-validator-attention')
        """)
        assert has_attention, 'Name field should have zato-validator-attention class'

        # .. close dialog.
        page.evaluate('$("#create-div").dialog("close")')

# ################################################################################################################################

    def test_38_realm_with_special_chars(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a definition with special characters in the realm field.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'realm-special'
        realm = 'realm/with spaces.and-special&chars'

        # Navigate and create ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        _create_definition_with_realm(page, name, realm)

        # .. find the row ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is not None, 'Row should be present'

        # .. extract the realm cell (5th td: numbering, selection, name, username, realm) ..
        cells = row.query_selector_all('td')
        realm_text = cells[4].inner_text().strip()

        # .. verify the realm value.
        assert realm_text == realm, f'Expected realm "{realm}", got: "{realm_text}"'

# ################################################################################################################################

    def test_39_password_not_visible_in_dom(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a definition with a known password. The password does not appear
        anywhere in the page HTML or table cell text.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'pwd-hidden'
        password = 'secret-pw-' + CryptoManager.generate_hex_string(32)

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create with the known password ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        page.fill('#id_name', name)
        page.fill('#id_username', 'user.' + name)
        page.fill('#id_realm', 'realm.' + name)
        page.fill('#id_password', password)

        page.click('#create-div input[type="submit"]')
        page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
        page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. get the full page HTML ..
        page_html = page.content()

        # .. assert the password does not appear in the HTML ..
        assert password not in page_html, \
            f'Password "{password}" should not appear in page HTML'

        # .. also check all table cells.
        all_cells = page.query_selector_all('#data-table tbody tr td')
        for cell in all_cells:
            cell_text = cell.inner_text()
            assert password not in cell_text, \
                f'Password "{password}" should not appear in any table cell'

# ################################################################################################################################
# ################################################################################################################################
