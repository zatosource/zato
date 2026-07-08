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
_Channel_Url_Pattern = '/zato/http-soap/?cluster=1&connection=channel&transport=plain_http'
_Outgoing_Url_Pattern = '/zato/http-soap/?cluster=1&connection=outgoing&transport=plain_http'
_Groups_Url_Pattern = '/zato/groups/group/zato-api-creds/?cluster=1'

_Test_Name_Prefix = 'test.xpage.' + CryptoManager.generate_hex_string(32) + '.'

# ################################################################################################################################
# ################################################################################################################################

def _create_definition_via_ui(page:'Page', base_url:'str', suffix:'str') -> 'dict':
    """ Creates a basic auth definition via the dashboard UI and returns its details.
    """

    name = _Test_Name_Prefix + suffix
    username = 'user.' + name
    realm = 'realm.' + name
    password = 'password.' + CryptoManager.generate_hex_string()

    # Navigate to basic auth page ..
    _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
    page.wait_for_selector('#data-table', state='visible')

    # .. open and fill the create dialog ..
    page.click('#markup .page_prompt a')
    page.wait_for_selector('#create-div', state='visible')

    page.fill('#id_name', name)
    page.fill('#id_username', username)
    page.fill('#id_realm', realm)
    page.fill('#id_password', password)

    # .. submit and wait ..
    page.click('#create-div input[type="submit"]')
    page.wait_for_selector('#create-div', state='hidden', timeout=10000)

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
    """ Returns the item ID of the row with the given name.
    """
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    row = page.query_selector(row_selector)
    id_cell = row.query_selector('td[class*="item_id_"]')

    out = id_cell.inner_text().strip()
    return out

# ################################################################################################################################

def _delete_definition_via_ui(page:'Page', base_url:'str', name:'str') -> 'None':
    """ Deletes a basic auth definition via the dashboard UI.
    """

    # Navigate to basic auth page with query filter so the row is visible ..
    _ = page.goto(f'{base_url}{_Page_Url_Pattern}&query={name}')
    page.wait_for_selector('#data-table', state='visible')

    # .. trigger delete ..
    item_id = _get_item_id(page, name)
    page.evaluate(f'$.fn.zato.security.basic_auth.delete_("{item_id}")')

    # .. wait for the jConfirm popup and click OK ..
    page.wait_for_selector('#popup_container', state='visible', timeout=5000)
    page.click('#popup_ok')

    # .. wait for the row to disappear.
    time.sleep(0.5)

# ################################################################################################################################

def _edit_definition_name_via_ui(page:'Page', base_url:'str', old_name:'str', new_name:'str') -> 'None':
    """ Edits a basic auth definition's name via the dashboard UI.
    """

    # Navigate to basic auth page with query filter so the row is visible ..
    _ = page.goto(f'{base_url}{_Page_Url_Pattern}&query={old_name}')
    page.wait_for_selector('#data-table', state='visible')

    # .. open edit for the row ..
    item_id = _get_item_id(page, old_name)
    page.evaluate(f'$.fn.zato.security.basic_auth.edit("{item_id}")')
    page.wait_for_selector('#edit-div', state='visible', timeout=5000)

    # .. clear and fill the new name ..
    name_field = page.locator('#id_edit-name')
    name_field.fill('')
    name_field.fill(new_name)

    # .. submit and wait for the dialog to close.
    page.click('#edit-div input[type="submit"]')
    page.wait_for_selector('#edit-div', state='hidden', timeout=10000)

# ################################################################################################################################

def _find_security_option(page:'Page', select_id:'str', name:'str') -> 'bool':
    """ Returns True if the security select contains an option matching the given name.
    """

    out = page.evaluate(f"""
    (() => {{
        var select = document.querySelector('{select_id}');
        if (!select) return false;
        var options = select.querySelectorAll('option');
        for (var idx = 0; idx < options.length; idx++) {{
            if (options[idx].textContent.indexOf('{name}') !== -1) return true;
        }}
        return false;
    }})()
    """)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestBasicAuthCrossPage:
    """ Tests for cross-page visibility of basic auth definitions in channels, outgoing, and groups.
    """

    def test_57_def_in_channel_security_dropdown(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a basic auth def, navigates to REST channels, opens create dialog,
        and verifies the security dropdown contains the def as 'Basic Auth/{name}'.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a definition via the UI ..
        defn = _create_definition_via_ui(page, base_url, 'chan-drop')

        # .. navigate to REST channels ..
        _ = page.goto(f'{base_url}{_Channel_Url_Pattern}', timeout=60000)
        page.wait_for_selector('#data-table', state='visible', timeout=15000)

        # .. open the create dialog ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        # .. wait for the security select to be populated (SSE may take a moment) ..
        time.sleep(1)

        # .. verify the security dropdown contains our definition.
        expected_label = f'Basic Auth/{defn["name"]}'
        found = _find_security_option(page, '#id_security', defn['name'])
        assert found, f'Expected "{expected_label}" in channel security dropdown'

# ################################################################################################################################

    def test_58_def_in_outgoing_security_dropdown(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a basic auth def, navigates to outgoing REST, opens create dialog,
        and verifies the security select contains the def.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a definition via the UI ..
        defn = _create_definition_via_ui(page, base_url, 'out-drop')

        # .. navigate to outgoing REST ..
        _ = page.goto(f'{base_url}{_Outgoing_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open the create dialog ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        time.sleep(1)

        # .. verify the security dropdown contains our definition.
        found = _find_security_option(page, '#id_security', defn['name'])
        assert found, f'Expected Basic Auth/{defn["name"]} in outgoing security dropdown'

# ################################################################################################################################

    def test_59_sse_live_updates_channel_dropdown(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Navigates to REST channels, opens the create dialog (starts SSE).
        Then creates a new basic auth def via the UI in a second tab.
        Verifies the new def appears in the security dropdown without closing the dialog.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to REST channels and open the create dialog ..
        _ = page.goto(f'{base_url}{_Channel_Url_Pattern}', timeout=60000)
        page.wait_for_selector('#data-table', state='visible', timeout=15000)

        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        # .. wait for SSE to connect ..
        time.sleep(2)

        # .. create a new basic auth definition in a second tab ..
        second_tab = page.context.new_page()
        defn = _create_definition_via_ui(second_tab, base_url, 'sse-create')
        second_tab.close()

        # .. wait for the SSE update to arrive (up to 15s) ..
        found = False

        for attempt in range(30):
            time.sleep(0.5)
            found = _find_security_option(page, '#id_security', defn['name'])
            print(f'[test_59] Attempt {attempt}: found={found}')

            if found:
                break

        # .. verify the new def appeared in the dropdown without dialog close.
        assert found, f'Expected "{defn["name"]}" to appear in security dropdown via SSE'

# ################################################################################################################################

    def test_60_def_in_groups_badge_picker(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a basic auth def, navigates to security groups, opens create dialog,
        and verifies the badge picker contains a badge with the def name.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a definition via the UI ..
        defn = _create_definition_via_ui(page, base_url, 'grp-badge')

        # .. navigate to security groups ..
        _ = page.goto(f'{base_url}{_Groups_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open the create dialog via the JS function ..
        page.evaluate('$.fn.zato.groups.create()')
        page.wait_for_selector('#create-div', state='visible')

        # .. wait for the badge picker to load ..
        time.sleep(2)

        # .. find a badge with our definition name in the available zone.
        found = page.evaluate(f"""
        (() => {{
            var badges = document.querySelectorAll('#badge-zone-available-create .security-badge');
            for (var idx = 0; idx < badges.length; idx++) {{
                var nameSpan = badges[idx].querySelector('.security-badge-name');
                if (nameSpan && nameSpan.textContent.indexOf('{defn["name"]}') !== -1) return true;
            }}
            return false;
        }})()
        """)

        assert found, f'Expected badge with name "{defn["name"]}" in groups badge picker'

# ################################################################################################################################

    def test_61_deleted_def_removed_from_channel_dropdown(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a def via UI, verifies it appears in the channel security dropdown,
        deletes it via UI, and verifies it is gone from the dropdown after reload.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a definition via the UI ..
        defn = _create_definition_via_ui(page, base_url, 'del-drop')

        # .. navigate to REST channels and open create dialog ..
        _ = page.goto(f'{base_url}{_Channel_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')
        time.sleep(1)

        # .. verify it is present ..
        found_before = _find_security_option(page, '#id_security', defn['name'])
        assert found_before, f'Expected "{defn["name"]}" in dropdown before delete'

        # .. close the dialog ..
        page.evaluate('$("#create-div").dialog("close")')
        page.wait_for_function('!document.querySelector("#create-div").offsetParent')

        # .. delete the definition via UI ..
        _delete_definition_via_ui(page, base_url, defn['name'])

        # .. reload the channels page and open the dialog again ..
        _ = page.goto(f'{base_url}{_Channel_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')
        time.sleep(1)

        # .. verify the def is gone.
        found_after = _find_security_option(page, '#id_security', defn['name'])
        assert not found_after, f'Expected "{defn["name"]}" removed from dropdown after delete'

# ################################################################################################################################

    def test_62_sse_live_removes_deleted_def(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a def via UI, opens the REST channel create dialog (starts SSE),
        verifies the def is present, deletes it via UI in a second tab,
        and verifies the def disappears from the dropdown without closing the dialog.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a definition via UI ..
        defn = _create_definition_via_ui(page, base_url, 'sse-del')

        # .. navigate to REST channels and open create dialog ..
        _ = page.goto(f'{base_url}{_Channel_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')
        time.sleep(1)

        # .. verify the def is present in the dropdown ..
        found_before = _find_security_option(page, '#id_security', defn['name'])
        assert found_before, f'Expected "{defn["name"]}" in dropdown before SSE delete'

        # .. delete via UI in a second tab ..
        second_tab = page.context.new_page()
        _delete_definition_via_ui(second_tab, base_url, defn['name'])
        second_tab.close()

        # .. wait for SSE to remove it (up to 10s) ..
        removed = False

        for attempt in range(20):
            time.sleep(0.5)
            still_there = _find_security_option(page, '#id_security', defn['name'])
            print(f'[test_62] Attempt {attempt}: still_there={still_there}')

            if not still_there:
                removed = True
                break

        assert removed, f'Expected "{defn["name"]}" to disappear from dropdown via SSE'

# ################################################################################################################################

    def test_63_sse_live_renames_def_in_dropdown(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a def via UI, opens the REST channel create dialog (starts SSE),
        edits the def's name via UI in a second tab,
        and verifies the option text in the dropdown changes to reflect the new name.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a definition via UI ..
        defn = _create_definition_via_ui(page, base_url, 'sse-rename')
        old_name = defn['name']
        new_name = _Test_Name_Prefix + 'sse-renamed'

        # .. navigate to REST channels and open create dialog ..
        _ = page.goto(f'{base_url}{_Channel_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')
        time.sleep(1)

        # .. verify old name is in the dropdown ..
        found_old = _find_security_option(page, '#id_security', old_name)
        assert found_old, f'Expected "{old_name}" in dropdown before rename'

        # .. edit the name via UI in a second tab ..
        second_tab = page.context.new_page()
        _edit_definition_name_via_ui(second_tab, base_url, old_name, new_name)
        second_tab.close()

        # .. wait for SSE to update (up to 10s) ..
        found_new = False

        for attempt in range(20):
            time.sleep(0.5)
            found_new = _find_security_option(page, '#id_security', new_name)
            print(f'[test_63] Attempt {attempt}: found_new={found_new}')

            if found_new:
                break

        assert found_new, f'Expected "{new_name}" to appear in dropdown via SSE after rename'

# ################################################################################################################################
# ################################################################################################################################
