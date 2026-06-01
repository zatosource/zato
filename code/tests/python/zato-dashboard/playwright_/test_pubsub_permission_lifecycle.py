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

    def test_edit_adds_second_pattern(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        sec_name = _create_basic_auth(page, base_url, 'add-pat')
        _ = _create_topic(page, base_url, 'add-pat')

        first_pattern = 'first.pattern.*'

        # .. create with one pattern as publisher-subscriber ..
        item_id = _create_permission(page, base_url, sec_name, 'publisher-subscriber', 'pub', first_pattern)

        # .. open edit ..
        page.evaluate(f'$.fn.zato.pubsub.permission.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)
        time.sleep(0.3)

        # .. add a second pattern row ..
        page.click('#edit-patterns-container .pattern-row:first-child .pattern-add-button')
        time.sleep(0.2)

        # .. fill the new row (prepended to top) with a sub pattern ..
        second_pattern = 'second.pattern.*'
        page.select_option('#edit-patterns-container .pattern-row:first-child .pattern-type-select', value='sub')
        page.fill('#edit-patterns-container .pattern-row:first-child .pattern-input', second_pattern)

        # .. submit ..
        page.click('#edit-div input[type="submit"]')
        page.wait_for_selector('#edit-div', state='hidden', timeout=10000)
        time.sleep(0.5)

        # .. reload to re-render patterns ..
        _ = page.goto(f'{base_url}{_Permission_Page_Url}')
        page.wait_for_selector('#data-table', state='visible')
        time.sleep(0.3)

        # .. verify both patterns are visible.
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.query_selector(row_selector)
        row_text = row.inner_text()

        assert first_pattern in row_text, f'Expected "{first_pattern}" in row, got: "{row_text}"'
        assert second_pattern in row_text, f'Expected "{second_pattern}" in row, got: "{row_text}"'

# ################################################################################################################################

    def test_edit_removes_a_pattern(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        sec_name = _create_basic_auth(page, base_url, 'rm-pat')
        _ = _create_topic(page, base_url, 'rm-pat')

        pub_pattern = 'remove.pub.*'
        sub_pattern = 'remove.sub.*'

        # .. create with publisher-subscriber and two patterns ..
        _ = page.goto(f'{base_url}{_Permission_Page_Url}')
        page.wait_for_selector('#data-table', state='visible')

        page.evaluate('$.fn.zato.pubsub.permission.create()')
        page.wait_for_selector('#create-div', state='visible')

        page.wait_for_function(
            'document.querySelector("#id_sec_base_id") && document.querySelector("#id_sec_base_id").options.length > 1',
            timeout=10000
        )

        page.select_option('#id_sec_base_id', label=sec_name)
        page.select_option('#id_access_type', value='publisher-subscriber')
        time.sleep(0.3)

        # .. first row = pub pattern ..
        page.select_option('#create-patterns-container .pattern-row:first-child .pattern-type-select', value='pub')
        page.fill('#create-patterns-container .pattern-row:first-child .pattern-input', pub_pattern)

        # .. add second row = sub pattern ..
        page.click('#create-patterns-container .pattern-row:first-child .pattern-add-button')
        time.sleep(0.2)
        page.select_option('#create-patterns-container .pattern-row:first-child .pattern-type-select', value='sub')
        page.fill('#create-patterns-container .pattern-row:first-child .pattern-input', sub_pattern)

        page.click('#create-div input[type="submit"]')
        page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        # .. get the item_id ..
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)
        id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = id_cell.inner_text().strip()

        # .. reload so patterns render ..
        _ = page.goto(f'{base_url}{_Permission_Page_Url}')
        page.wait_for_selector('#data-table', state='visible')
        time.sleep(0.3)

        # .. verify both patterns are present ..
        row = page.query_selector(row_selector)
        row_text = row.inner_text()
        assert pub_pattern in row_text, f'Expected "{pub_pattern}" before edit, got: "{row_text}"'
        assert sub_pattern in row_text, f'Expected "{sub_pattern}" before edit, got: "{row_text}"'

        # .. open edit and remove the first pattern row ..
        page.evaluate(f'$.fn.zato.pubsub.permission.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)
        time.sleep(0.3)

        # .. remove the first row (which should be one of the patterns) ..
        page.click('#edit-patterns-container .pattern-row:first-child .pattern-remove-button')
        time.sleep(0.2)

        # .. submit ..
        page.click('#edit-div input[type="submit"]')
        page.wait_for_selector('#edit-div', state='hidden', timeout=10000)
        time.sleep(0.5)

        # .. reload ..
        _ = page.goto(f'{base_url}{_Permission_Page_Url}')
        page.wait_for_selector('#data-table', state='visible')
        time.sleep(0.3)

        # .. verify only one pattern remains.
        row = page.query_selector(row_selector)
        row_text = row.inner_text()

        pattern_count = 0
        if pub_pattern in row_text:
            pattern_count += 1
        if sub_pattern in row_text:
            pattern_count += 1

        assert pattern_count == 1, \
            f'Expected exactly 1 pattern after removing one, got {pattern_count} in: "{row_text}"'

# ################################################################################################################################

    def test_cancel_edit_preserves_original(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        sec_name = _create_basic_auth(page, base_url, 'cancel-edit')
        _ = _create_topic(page, base_url, 'cancel-edit')

        pattern_value = 'cancel.edit.pattern.*'

        # .. create the permission as publisher ..
        item_id = _create_permission(page, base_url, sec_name, 'publisher', 'pub', pattern_value)

        # .. reload so patterns are rendered ..
        _ = page.goto(f'{base_url}{_Permission_Page_Url}')
        page.wait_for_selector('#data-table', state='visible')
        time.sleep(0.3)

        # .. verify the original state ..
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.query_selector(row_selector)
        row_text = row.inner_text()
        assert 'Publisher' in row_text, f'Expected "Publisher" before edit, got: "{row_text}"'

        # .. open edit and change values ..
        page.evaluate(f'$.fn.zato.pubsub.permission.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        page.select_option('#id_edit-access_type', value='publisher-subscriber')
        time.sleep(0.2)
        page.fill('#edit-patterns-container .pattern-row:first-child .pattern-input', 'changed.pattern.*')

        # .. cancel without submitting ..
        page.evaluate('$("#edit-div").dialog("close")')
        page.wait_for_function('!document.querySelector("#edit-div").offsetParent')

        # .. verify the row is unchanged.
        row = page.query_selector(row_selector)
        row_text = row.inner_text()
        assert 'Publisher' in row_text, f'Expected "Publisher" still after cancel, got: "{row_text}"'
        assert pattern_value in row_text, f'Expected original pattern after cancel, got: "{row_text}"'

# ################################################################################################################################

    def test_cancel_delete_leaves_row_intact(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        sec_name = _create_basic_auth(page, base_url, 'cancel-del')
        _ = _create_topic(page, base_url, 'cancel-del')

        pattern_value = 'cancel.delete.pattern.*'

        # .. create the permission ..
        item_id = _create_permission(page, base_url, sec_name, 'publisher', 'pub', pattern_value)

        # .. trigger delete ..
        page.evaluate(f'$.fn.zato.pubsub.permission.delete_("{item_id}")')
        page.wait_for_selector('#popup_container', state='visible', timeout=5000)

        # .. dismiss the confirmation (click Cancel) ..
        page.click('#popup_cancel')
        time.sleep(0.5)

        # .. verify the row is still present.
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.query_selector(row_selector)
        assert row is not None, f'Row for "{sec_name}" should still exist after cancelling delete'

# ################################################################################################################################

    def test_edit_form_pre_populates_patterns(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        sec_name = _create_basic_auth(page, base_url, 'prepop')
        _ = _create_topic(page, base_url, 'prepop')

        pattern_value = 'prepopulated.pattern.*'

        # .. create as subscriber ..
        item_id = _create_permission(page, base_url, sec_name, 'subscriber', 'sub', pattern_value)

        # .. open edit ..
        page.evaluate(f'$.fn.zato.pubsub.permission.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)
        time.sleep(0.3)

        # .. verify the pattern input is pre-populated ..
        input_value = page.input_value('#edit-patterns-container .pattern-row:first-child .pattern-input')
        assert input_value == pattern_value, \
            f'Expected pattern input "{pattern_value}", got: "{input_value}"'

        # .. verify the pattern type select shows "sub".
        select_value = page.evaluate(
            'document.querySelector("#edit-patterns-container .pattern-row:first-child .pattern-type-select").value'
        )
        assert select_value == 'sub', f'Expected pattern type "sub", got: "{select_value}"'

# ################################################################################################################################

    def test_edit_form_shows_sec_def_as_readonly(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        sec_name = _create_basic_auth(page, base_url, 'readonly-sec')
        _ = _create_topic(page, base_url, 'readonly-sec')

        pattern_value = 'readonly.sec.pattern.*'

        # .. create the permission ..
        item_id = _create_permission(page, base_url, sec_name, 'publisher', 'pub', pattern_value)

        # .. open edit ..
        page.evaluate(f'$.fn.zato.pubsub.permission.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)
        time.sleep(0.3)

        # .. verify the sec def container shows a link, not a dropdown ..
        container_html = page.inner_html('#edit-form .security-definition-container')
        assert f'>{sec_name}</a>' in container_html, \
            f'Expected link with sec def name "{sec_name}" in container, got: "{container_html}"'

        # .. verify there is no visible select dropdown.
        select_visible = page.evaluate(
            '''() => {
                let select = document.querySelector("#id_edit-sec_base_id");
                if (!select) return false;
                return select.offsetParent !== null && select.tagName === "SELECT";
            }'''
        )
        assert not select_visible, 'Security definition should not be an editable dropdown in edit form'

# ################################################################################################################################

    def test_incompatible_pattern_greyed_out(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        sec_name = _create_basic_auth(page, base_url, 'grey-pat')
        _ = _create_topic(page, base_url, 'grey-pat')

        pub_pattern = 'grey.pub.pattern.*'
        sub_pattern = 'grey.sub.pattern.*'

        # .. create with publisher-subscriber and both patterns ..
        _ = page.goto(f'{base_url}{_Permission_Page_Url}')
        page.wait_for_selector('#data-table', state='visible')

        page.evaluate('$.fn.zato.pubsub.permission.create()')
        page.wait_for_selector('#create-div', state='visible')

        page.wait_for_function(
            'document.querySelector("#id_sec_base_id") && document.querySelector("#id_sec_base_id").options.length > 1',
            timeout=10000
        )

        page.select_option('#id_sec_base_id', label=sec_name)
        page.select_option('#id_access_type', value='publisher-subscriber')
        time.sleep(0.3)

        page.select_option('#create-patterns-container .pattern-row:first-child .pattern-type-select', value='pub')
        page.fill('#create-patterns-container .pattern-row:first-child .pattern-input', pub_pattern)

        page.click('#create-patterns-container .pattern-row:first-child .pattern-add-button')
        time.sleep(0.2)
        page.select_option('#create-patterns-container .pattern-row:first-child .pattern-type-select', value='sub')
        page.fill('#create-patterns-container .pattern-row:first-child .pattern-input', sub_pattern)

        page.click('#create-div input[type="submit"]')
        page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        # .. get the item_id ..
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)
        id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = id_cell.inner_text().strip()

        # .. open edit and change access type to publisher only ..
        page.evaluate(f'$.fn.zato.pubsub.permission.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)
        time.sleep(0.3)

        page.select_option('#id_edit-access_type', value='publisher')
        time.sleep(0.5)

        # .. verify that the sub pattern row's inputs are disabled.
        disabled_inputs = page.evaluate(
            '''() => {
                let rows = document.querySelectorAll("#edit-patterns-container .pattern-row");
                let disabled_count = 0;
                for (let row of rows) {
                    let input = row.querySelector(".pattern-input");
                    let select = row.querySelector(".pattern-type-select");
                    if (input && input.disabled && select && select.disabled) {
                        disabled_count++;
                    }
                }
                return disabled_count;
            }'''
        )
        assert disabled_inputs >= 1, \
            f'Expected at least 1 disabled pattern row (incompatible sub), got: {disabled_inputs}'

# ################################################################################################################################

    def test_security_definition_link_in_row(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        sec_name = _create_basic_auth(page, base_url, 'link-row')
        _ = _create_topic(page, base_url, 'link-row')

        pattern_value = 'link.row.pattern.*'

        # .. create the permission ..
        _ = _create_permission(page, base_url, sec_name, 'publisher', 'pub', pattern_value)

        # .. reload so the page renders from the server ..
        _ = page.goto(f'{base_url}{_Permission_Page_Url}')
        page.wait_for_selector('#data-table', state='visible')
        time.sleep(0.3)

        # .. find the row and verify the sec def link ..
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.query_selector(row_selector)
        link = row.query_selector(f'a:text-is("{sec_name}")')

        assert link is not None, f'Expected a link with text "{sec_name}" in row'

        href = link.get_attribute('href')
        assert '/zato/security/basic-auth/' in href, \
            f'Expected link to basic auth page, got: "{href}"'
        assert sec_name in href, \
            f'Expected sec def name in link href, got: "{href}"'

# ################################################################################################################################
# ################################################################################################################################
