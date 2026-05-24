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

_Test_Name_Prefix = 'test.life.' + os.urandom(4).hex() + '.'

_Console_Noise_Patterns = [
    'favicon.ico',
    'ERR_CONNECTION_REFUSED',
    'live-form-updates',
    'Content-Security-Policy',
]

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

def _do_full_crud(page:'Page', base_url:'str', suffix:'str') -> 'None':
    """ Performs a full CRUD cycle: create, edit, change password, delete.
    """

    # Navigate ..
    _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
    page.wait_for_selector('#data-table', state='visible')

    # .. create ..
    name = _Test_Name_Prefix + suffix
    username = 'user.' + name
    realm = 'realm.' + name
    password = 'password.' + os.urandom(8).hex()

    page.click('#markup .page_prompt a')
    page.wait_for_selector('#create-div', state='visible')

    page.fill('#id_name', name)
    page.fill('#id_username', username)
    page.fill('#id_realm', realm)
    page.fill('#id_password', password)

    page.click('#create-div input[type="submit"]')
    page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=5000)

    # .. edit ..
    item_id = _get_item_id(page, name)
    page.evaluate(f'$.fn.zato.security.basic_auth.edit("{item_id}")')
    page.wait_for_selector('#edit-div', state='visible', timeout=5000)

    edited_name = name + '-edited'
    page.fill('#id_edit-name', '')
    page.fill('#id_edit-name', edited_name)

    page.click('#edit-div input[type="submit"]')
    page.wait_for_selector('#edit-div', state='hidden', timeout=10000)
    time.sleep(0.3)

    # .. change password ..
    page.evaluate(f'$.fn.zato.data_table.change_password("{item_id}")')
    page.wait_for_selector('#change_password-div', state='visible', timeout=5000)

    page.fill('#change_password-div #id_password', 'new-crud-pwd')
    page.click('#change_password-div input[type="submit"]')
    page.wait_for_function('!document.querySelector("#change_password-div").offsetParent')

    # .. delete.
    page.evaluate(f'$.fn.zato.security.basic_auth.delete_("{item_id}")')
    page.wait_for_selector('#popup_container', state='visible', timeout=5000)
    page.click('#popup_ok')
    time.sleep(0.5)

# ################################################################################################################################
# ################################################################################################################################

class TestBasicAuthLifecycle:
    """ Tests for console errors, HTTP 500s, full CRUD, rate limiting, and sorting.
    """

    def test_27_no_console_errors_during_crud(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Performs a full CRUD session and asserts no console.error messages appear.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Collect console errors ..
        console_errors = [] # type: list

        def _on_console(msg:'object') -> 'None':
            if msg.type == 'error':
                console_errors.append(msg.text)

        page.on('console', _on_console)

        # .. perform the full CRUD cycle ..
        _do_full_crud(page, base_url, 'console-check')

        # .. filter known noise ..
        real_errors = [] # type: list

        for error_text in console_errors:
            is_noise = False
            for noise_pattern in _Console_Noise_Patterns:
                if noise_pattern in error_text:
                    is_noise = True
                    break

            if not is_noise:
                real_errors.append(error_text)

        # .. assert no real errors.
        assert not real_errors, f'Console errors during CRUD:\n' + '\n'.join(real_errors)

# ################################################################################################################################

    def test_28_no_http_500_during_crud(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Performs a full CRUD session and asserts no HTTP 500+ responses.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Collect server errors ..
        server_errors = [] # type: list

        def _on_response(response:'object') -> 'None':
            if response.status >= 500:
                server_errors.append(f'{response.status} {response.url}')

        page.on('response', _on_response)

        # .. perform the full CRUD cycle ..
        _do_full_crud(page, base_url, 'http500-check')

        # .. assert no 500s.
        assert not server_errors, f'HTTP 500+ responses during CRUD:\n' + '\n'.join(server_errors)

# ################################################################################################################################

    def test_29_full_crud_cycle(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Create, verify, edit, verify, change password, verify, delete, verify gone.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create ..
        defn = _create_definition(page, 'crud')

        # .. verify row exists ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{defn["name"]}"))')
        assert row is not None, f'Row "{defn["name"]}" should exist after create'

        # .. edit the name ..
        item_id = _get_item_id(page, defn['name'])
        page.evaluate(f'$.fn.zato.security.basic_auth.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        edited_name = defn['name'] + '-edited'
        page.fill('#id_edit-name', '')
        page.fill('#id_edit-name', edited_name)

        page.click('#edit-div input[type="submit"]')
        page.wait_for_selector('#edit-div', state='hidden', timeout=10000)
        time.sleep(0.3)

        # .. verify old name gone, new name present ..
        old_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{defn["name"]}"))')
        assert old_row is None, f'Old name "{defn["name"]}" should be gone after edit'

        new_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{edited_name}"))')
        assert new_row is not None, f'Edited name "{edited_name}" should be present'

        # .. change password ..
        page.evaluate(f'$.fn.zato.data_table.change_password("{item_id}")')
        page.wait_for_selector('#change_password-div', state='visible', timeout=5000)

        page.fill('#change_password-div #id_password', 'new-crud-pwd')
        page.click('#change_password-div input[type="submit"]')
        page.wait_for_function('!document.querySelector("#change_password-div").offsetParent')

        # .. verify row still present after password change ..
        row_after_pwd = page.query_selector(f'#data-table tbody tr:has(td:text-is("{edited_name}"))')
        assert row_after_pwd is not None, f'Row should remain after password change'

        # .. delete ..
        page.evaluate(f'$.fn.zato.security.basic_auth.delete_("{item_id}")')
        page.wait_for_selector('#popup_container', state='visible', timeout=5000)
        page.click('#popup_ok')
        time.sleep(0.5)

        # .. verify gone.
        row_after_delete = page.query_selector(f'#data-table tbody tr:has(td:text-is("{edited_name}"))')
        assert row_after_delete is None, f'Row "{edited_name}" should be gone after delete'

# ################################################################################################################################

    def test_30_rate_limiting_link(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Clicks the rate limiting link, verifies the page loads, navigates back.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create a definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, 'rate-limit')

        # .. find the rate limiting link ..
        item_id = _get_item_id(page, defn['name'])
        link_selector = f'#data-table tbody tr:has(td:text-is("{defn["name"]}")) a[href*="rate-limiting"]'
        link = page.query_selector(link_selector)
        href = link.get_attribute('href')

        # .. verify the href pattern ..
        assert f'/zato/security/basic-auth/rate-limiting/{item_id}/' in href, \
            f'Expected rate-limiting URL with ID {item_id}, got: {href}'

        # .. click the link and wait for the rate limiting page ..
        link.click()
        page.wait_for_selector('#rate-limiting-container', state='visible', timeout=10000)

        # .. verify URL ..
        current_url = page.url
        assert f'/zato/security/basic-auth/rate-limiting/{item_id}/' in current_url, \
            f'Expected rate-limiting in URL, got: {current_url}'

        # .. verify the heading contains the definition name ..
        heading = page.query_selector('h2.zato')
        heading_text = heading.inner_text()
        assert defn['name'] in heading_text, f'Expected name in heading, got: "{heading_text}"'

        # .. navigate back ..
        page.go_back()
        page.wait_for_selector('#data-table', state='visible', timeout=10000)

        # .. verify the row is still present.
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{defn["name"]}"))')
        assert row is not None, f'Row "{defn["name"]}" should still be present after navigating back'

# ################################################################################################################################

    def test_31_sort_by_name(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates three definitions, clicks Name header to sort, verifies order.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create three definitions in non-alphabetical order ..
        name_b = _create_definition(page, 'sort-b')['name']
        name_a = _create_definition(page, 'sort-a')['name']
        name_c = _create_definition(page, 'sort-c')['name']

        sorted_asc = [name_a, name_b, name_c]
        sorted_desc = [name_c, name_b, name_a]

        # .. reload so tablesorter picks up the new rows ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. click the Name column header to trigger a sort ..
        page.click('#data-table thead th:nth-child(3)')
        time.sleep(0.3)

        # .. extract all name cells after first click ..
        cells_first = page.query_selector_all('#data-table tbody tr:not(.ignore) td:nth-child(3)')
        names_first = []
        for cell in cells_first:
            text = cell.inner_text().strip()
            if text:
                names_first.append(text)

        our_first = [name for name in names_first if name in sorted_asc]

        # .. click again to reverse the sort ..
        page.click('#data-table thead th:nth-child(3)')
        time.sleep(0.3)

        cells_second = page.query_selector_all('#data-table tbody tr:not(.ignore) td:nth-child(3)')
        names_second = []
        for cell in cells_second:
            text = cell.inner_text().strip()
            if text:
                names_second.append(text)

        our_second = [name for name in names_second if name in sorted_asc]

        # .. the two clicks must produce opposite orders ..
        assert our_first != our_second, \
            f'Clicking header twice should reverse order, got same: {our_first}'

        # .. one must be ascending, the other descending.
        assert (our_first == sorted_asc and our_second == sorted_desc) or \
               (our_first == sorted_desc and our_second == sorted_asc), \
            f'Expected one asc and one desc, got first={our_first}, second={our_second}'

# ################################################################################################################################
# ################################################################################################################################
