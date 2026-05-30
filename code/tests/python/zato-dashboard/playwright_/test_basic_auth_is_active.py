# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/security/basic-auth/?cluster=1'

_Test_Name_Prefix = 'test.is.active.' + os.urandom(4).hex() + '.'

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

def _find_definition_via_api(api_client:'anydict', name:'str') -> 'dict':
    """ Finds a basic auth definition by name using the get-list API.
    """

    items, _ = api_client.get_list('zato.security.basic-auth.get-list', cluster_id=1)

    for item in items:
        if item['name'] == name:
            return item

    raise AssertionError(f'Definition "{name}" not found via API')

# ################################################################################################################################
# ################################################################################################################################

class TestBasicAuthIsActive:
    """ Tests that is_active is correctly persisted as True when creating and editing via the UI.
    """

    created_names = []

    def test_90_create_is_active_true(self, logged_in_page:'Page', zato_dashboard:'anydict', api_client:'anydict') -> 'None':
        """ Creates a basic auth definition via the UI and verifies
        that is_active is True in the ODB via the API.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the basic auth page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create a definition via the UI ..
        defn = _create_definition(page, base_url, 'active-create')
        self.__class__.created_names.append(defn['name'])

        # .. verify is_active is True via the server API.
        api_defn = _find_definition_via_api(api_client, defn['name'])
        assert api_defn['is_active'] is True, \
            f'Expected is_active=True after create, got: {api_defn["is_active"]!r}'

# ################################################################################################################################

    def test_91_edit_preserves_is_active(self, logged_in_page:'Page', zato_dashboard:'anydict', api_client:'anydict') -> 'None':
        """ Creates a basic auth definition via the UI, edits the username,
        and verifies that is_active remains True in the ODB via the API.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the basic auth page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create a definition via the UI ..
        defn = _create_definition(page, base_url, 'active-edit')
        self.__class__.created_names.append(defn['name'])

        # .. the row is already visible on the current page after creation,
        # .. open the edit dialog directly ..
        _click_edit_for_row(page, defn['name'])

        # .. change the username ..
        new_username = 'edited.' + defn['username']
        page.fill('#id_edit-username', new_username)

        # .. submit the edit ..
        page.click('#edit-div input[type="submit"]')
        page.wait_for_selector('#edit-div', state='hidden', timeout=10000)

        # .. verify is_active is still True via the server API.
        api_defn = _find_definition_via_api(api_client, defn['name'])
        assert api_defn['is_active'] is True, \
            f'Expected is_active=True after edit, got: {api_defn["is_active"]!r}'

        assert api_defn['username'] == new_username, \
            f'Expected username="{new_username}", got: "{api_defn["username"]}"'

# ################################################################################################################################

    def test_99_cleanup(self, api_client:'anydict') -> 'None':
        """ Removes all definitions created during this test class.
        """
        for name in self.__class__.created_names:
            try:
                defn = _find_definition_via_api(api_client, name)
                api_client.delete('zato.security.basic-auth.delete', id=defn['id'])
            except (AssertionError, Exception):
                pass

# ################################################################################################################################
# ################################################################################################################################
