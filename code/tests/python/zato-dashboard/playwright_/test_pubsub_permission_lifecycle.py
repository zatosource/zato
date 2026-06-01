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

_Permission_Page_Url = '/zato/pubsub/permission/?cluster=1'
_Basic_Auth_Page_Url = '/zato/security/basic-auth/?cluster=1'
_Topic_Page_Url = '/zato/pubsub/topic/?cluster=1'

_Test_Name_Prefix = 'test.permission.lc.' + os.urandom(4).hex() + '.'

_Console_Noise_Patterns = [
    'favicon.ico',
    'ERR_CONNECTION_REFUSED',
    'live-form-updates',
    'Content-Security-Policy',
]

# ################################################################################################################################
# ################################################################################################################################

def _create_basic_auth(page:'Page', base_url:'str', suffix:'str') -> 'str':
    """ Creates a Basic Auth security definition via the UI and returns its name.
    """

    name = _Test_Name_Prefix + 'auth.' + suffix
    password = 'password.' + os.urandom(8).hex()

    # Navigate to the Basic Auth page ..
    _ = page.goto(f'{base_url}{_Basic_Auth_Page_Url}')
    page.wait_for_selector('#data-table', state='visible')

    # .. open the create dialog ..
    page.click('#markup .page_prompt a')
    page.wait_for_selector('#create-div', state='visible')

    # .. fill in the form fields ..
    page.fill('#id_name', name)
    page.fill('#id_username', 'user.' + name)
    page.fill('#id_realm', 'API')
    page.fill('#id_password', password)

    # .. submit and wait for the dialog to close ..
    page.click('#create-div input[type="submit"]')
    page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    # .. wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=5000)

    return name

# ################################################################################################################################

def _create_topic(page:'Page', base_url:'str', suffix:'str') -> 'str':
    """ Creates a pub/sub topic via the UI and returns its name.
    """

    name = _Test_Name_Prefix + 'topic.' + suffix

    # Navigate to the topics page ..
    _ = page.goto(f'{base_url}{_Topic_Page_Url}')
    page.wait_for_selector('#data-table', state='visible')

    # .. open the create dialog ..
    page.click('#markup .page_prompt a')
    page.wait_for_selector('#create-div', state='visible')

    # .. fill in the name ..
    page.fill('#id_name', name)

    # .. submit and wait for the dialog to close ..
    page.click('#create-div input[type="submit"]')
    page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    # .. wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=5000)

    return name

# ################################################################################################################################

def _create_permission(
    page:'Page',
    base_url:'str',
    sec_name:'str',
    access_type:'str',
    pattern_type:'str',
    pattern_value:'str',
    ) -> 'str':
    """ Creates a pub/sub permission via the UI and returns the item_id.
    """

    # Navigate to the permissions page ..
    _ = page.goto(f'{base_url}{_Permission_Page_Url}')
    page.wait_for_selector('#data-table', state='visible')

    # .. open the create dialog ..
    page.evaluate('$.fn.zato.pubsub.permission.create()')
    page.wait_for_selector('#create-div', state='visible')

    # .. wait for the security definitions dropdown to be populated via AJAX ..
    page.wait_for_function(
        'document.querySelector("#id_sec_base_id") && document.querySelector("#id_sec_base_id").options.length > 1',
        timeout=10000
    )

    # .. select the security definition by its visible text ..
    page.select_option('#id_sec_base_id', label=sec_name)

    # .. set the access type ..
    page.select_option('#id_access_type', value=access_type)
    time.sleep(0.3)

    # .. set the pattern type ..
    page.select_option('#create-patterns-container .pattern-row:first-child .pattern-type-select', value=pattern_type)

    # .. fill in the pattern value ..
    page.fill('#create-patterns-container .pattern-row:first-child .pattern-input', pattern_value)

    # .. submit the form ..
    page.click('#create-div input[type="submit"]')

    # .. wait for the dialog to close ..
    page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    # .. find the row and extract the item_id.
    row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
    row = page.wait_for_selector(row_selector, state='visible', timeout=5000)
    id_cell = row.query_selector('td[class*="item_id_"]')

    out = id_cell.inner_text().strip()
    return out

# ################################################################################################################################

def _do_full_crud(page:'Page', base_url:'str', suffix:'str') -> 'None':
    """ Performs a full CRUD cycle on a permission: create, edit access type, delete.
    """

    # Create prerequisites ..
    sec_name = _create_basic_auth(page, base_url, suffix)
    _ = _create_topic(page, base_url, suffix)

    pattern_value = _Test_Name_Prefix + 'topic.' + suffix

    # .. create the permission ..
    item_id = _create_permission(page, base_url, sec_name, 'publisher', 'pub', pattern_value)

    # .. edit - change access type to subscriber ..
    page.evaluate(f'$.fn.zato.pubsub.permission.edit("{item_id}")')
    page.wait_for_selector('#edit-div', state='visible', timeout=5000)

    page.select_option('#id_edit-access_type', value='subscriber')
    time.sleep(0.3)

    page.click('#edit-div input[type="submit"]')
    page.wait_for_selector('#edit-div', state='hidden', timeout=10000)
    time.sleep(0.3)

    # .. delete.
    page.evaluate(f'$.fn.zato.pubsub.permission.delete_("{item_id}")')
    page.wait_for_selector('#popup_container', state='visible', timeout=5000)
    page.click('#popup_ok')
    time.sleep(0.5)

# ################################################################################################################################
# ################################################################################################################################

class TestPubSubPermissionLifecycle:
    """ Tests for full CRUD, console errors, HTTP 500, edit access type, and edit pattern.
    """

    def test_no_console_errors_during_crud(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Collect console errors ..
        console_errors = [] # type: list

        def _on_console(msg:'object') -> 'None':
            if msg.type == 'error':
                console_errors.append(msg.text)

        page.on('console', _on_console)

        # .. perform the full CRUD cycle ..
        _do_full_crud(page, base_url, 'console')

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

    def test_no_http_500_during_crud(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Collect server errors ..
        server_errors = [] # type: list

        def _on_response(response:'object') -> 'None':
            if response.status >= 500:
                server_errors.append(f'{response.status} {response.url}')

        page.on('response', _on_response)

        # .. perform the full CRUD cycle ..
        _do_full_crud(page, base_url, 'http500')

        # .. assert no 500s.
        assert not server_errors, f'HTTP 500+ responses during CRUD:\n' + '\n'.join(server_errors)

# ################################################################################################################################

    def test_full_crud_cycle(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        sec_name = _create_basic_auth(page, base_url, 'crud')
        _ = _create_topic(page, base_url, 'crud')

        pattern_value = _Test_Name_Prefix + 'topic.crud'

        # .. create the permission ..
        item_id = _create_permission(page, base_url, sec_name, 'publisher', 'pub', pattern_value)

        # .. verify the row exists ..
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.query_selector(row_selector)
        assert row is not None, f'Row for "{sec_name}" should exist after create'

        row_text = row.inner_text()
        assert 'Publisher' in row_text, f'Expected "Publisher" in row, got: "{row_text}"'

        # .. edit - change access type to subscriber ..
        page.evaluate(f'$.fn.zato.pubsub.permission.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        page.select_option('#id_edit-access_type', value='subscriber')
        time.sleep(0.3)

        page.click('#edit-div input[type="submit"]')
        page.wait_for_selector('#edit-div', state='hidden', timeout=10000)
        time.sleep(0.3)

        # .. verify the row now shows Subscriber ..
        row = page.query_selector(row_selector)
        row_text = row.inner_text()
        assert 'Subscriber' in row_text, f'Expected "Subscriber" after edit, got: "{row_text}"'

        # .. delete ..
        page.evaluate(f'$.fn.zato.pubsub.permission.delete_("{item_id}")')
        page.wait_for_selector('#popup_container', state='visible', timeout=5000)
        page.click('#popup_ok')
        time.sleep(0.5)

        # .. verify the row is gone.
        row_after_delete = page.query_selector(row_selector)
        assert row_after_delete is None, f'Row for "{sec_name}" should be gone after delete'

# ################################################################################################################################

    def test_edit_access_type(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        sec_name = _create_basic_auth(page, base_url, 'edit-access')
        _ = _create_topic(page, base_url, 'edit-access')

        pattern_value = _Test_Name_Prefix + 'topic.edit-access'

        # .. create as publisher ..
        item_id = _create_permission(page, base_url, sec_name, 'publisher', 'pub', pattern_value)

        # .. verify it shows Publisher ..
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.query_selector(row_selector)
        row_text = row.inner_text()
        assert 'Publisher' in row_text, f'Expected "Publisher", got: "{row_text}"'

        # .. edit to publisher-subscriber ..
        page.evaluate(f'$.fn.zato.pubsub.permission.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        page.select_option('#id_edit-access_type', value='publisher-subscriber')
        time.sleep(0.3)

        page.click('#edit-div input[type="submit"]')
        page.wait_for_selector('#edit-div', state='hidden', timeout=10000)
        time.sleep(0.3)

        # .. verify it now shows Publisher & Subscriber.
        row = page.query_selector(row_selector)
        row_text = row.inner_text()
        assert 'Publisher' in row_text, f'Expected "Publisher" in row, got: "{row_text}"'
        assert 'Subscriber' in row_text, f'Expected "Subscriber" in row, got: "{row_text}"'

# ################################################################################################################################

    def test_edit_pattern(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        sec_name = _create_basic_auth(page, base_url, 'edit-pattern')
        _ = _create_topic(page, base_url, 'edit-pattern')

        original_pattern = 'original.pattern.*'

        # .. create the permission ..
        item_id = _create_permission(page, base_url, sec_name, 'publisher', 'pub', original_pattern)

        # .. verify original pattern is visible ..
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.query_selector(row_selector)
        row_text = row.inner_text()
        assert original_pattern in row_text, f'Expected "{original_pattern}" in row, got: "{row_text}"'

        # .. edit to change the pattern ..
        page.evaluate(f'$.fn.zato.pubsub.permission.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)
        time.sleep(0.3)

        new_pattern = 'updated.pattern.*'
        page.fill('#edit-patterns-container .pattern-row:first-child .pattern-input', '')
        page.fill('#edit-patterns-container .pattern-row:first-child .pattern-input', new_pattern)

        page.click('#edit-div input[type="submit"]')
        page.wait_for_selector('#edit-div', state='hidden', timeout=10000)
        time.sleep(0.5)

        # .. reload the page so pattern display is re-rendered ..
        _ = page.goto(f'{base_url}{_Permission_Page_Url}')
        page.wait_for_selector('#data-table', state='visible')
        time.sleep(0.3)

        # .. verify the updated pattern is visible.
        row = page.query_selector(row_selector)
        row_text = row.inner_text()
        assert new_pattern in row_text, f'Expected "{new_pattern}" in row after edit, got: "{row_text}"'
        assert original_pattern not in row_text, \
            f'Original pattern "{original_pattern}" should be gone, got: "{row_text}"'

# ################################################################################################################################

    def test_access_type_constrains_pattern_types(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the permissions page ..
        _ = page.goto(f'{base_url}{_Permission_Page_Url}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open the create dialog ..
        page.evaluate('$.fn.zato.pubsub.permission.create()')
        page.wait_for_selector('#create-div', state='visible')
        time.sleep(0.3)

        # .. set access type to Publisher and check options ..
        page.select_option('#id_access_type', value='publisher')
        time.sleep(0.3)

        pub_options = page.evaluate(
            '''() => {
                let select = document.querySelector("#create-patterns-container .pattern-row:first-child .pattern-type-select");
                let options = [];
                for (let option of select.options) {
                    if (!option.disabled) options.push(option.value);
                }
                return options;
            }'''
        )
        assert 'pub' in pub_options, f'Expected "pub" in options for Publisher, got: {pub_options}'
        assert 'sub' not in pub_options, f'Expected no "sub" in options for Publisher, got: {pub_options}'

        # .. set access type to Subscriber and check options ..
        page.select_option('#id_access_type', value='subscriber')
        time.sleep(0.3)

        sub_options = page.evaluate(
            '''() => {
                let select = document.querySelector("#create-patterns-container .pattern-row:first-child .pattern-type-select");
                let options = [];
                for (let option of select.options) {
                    if (!option.disabled) options.push(option.value);
                }
                return options;
            }'''
        )
        assert 'sub' in sub_options, f'Expected "sub" in options for Subscriber, got: {sub_options}'
        assert 'pub' not in sub_options, f'Expected no "pub" in options for Subscriber, got: {sub_options}'

        # .. set access type to Publisher and Subscriber and check options.
        page.select_option('#id_access_type', value='publisher-subscriber')
        time.sleep(0.3)

        both_options = page.evaluate(
            '''() => {
                let select = document.querySelector("#create-patterns-container .pattern-row:first-child .pattern-type-select");
                let options = [];
                for (let option of select.options) {
                    if (!option.disabled) options.push(option.value);
                }
                return options;
            }'''
        )
        assert 'pub' in both_options, f'Expected "pub" in options for Publisher-Subscriber, got: {both_options}'
        assert 'sub' in both_options, f'Expected "sub" in options for Publisher-Subscriber, got: {both_options}'

# ################################################################################################################################
# ################################################################################################################################
