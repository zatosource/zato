# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time

# Zato
from zato.common.test.playwright_pubsub import close_dialog_via_jquery, collect_console_errors, collect_http_errors, \
    confirm_delete, create_basic_auth, create_permission, create_permission_with_two_patterns, create_topic, \
    filter_console_noise, navigate_to_page, open_edit_dialog, submit_edit_form, trigger_delete

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Permission_Page_Url = '/zato/pubsub/permission/?cluster=1'

_Test_Name_Prefix = 'test.permission.lc.' + os.urandom(4).hex() + '.'

_Console_Noise_Patterns = [
    'favicon.ico',
    'ERR_CONNECTION_REFUSED',
    'live-form-updates',
    'Content-Security-Policy',
]

# ################################################################################################################################
# ################################################################################################################################

def _do_full_crud(page:'Page', base_url:'str', suffix:'str') -> 'None':
    """ Performs a full CRUD cycle on a permission: create, edit access type, delete.
    """

    # Create prerequisites ..
    sec_name = create_basic_auth(page, base_url, _Test_Name_Prefix, suffix)
    _ = create_topic(page, base_url, _Test_Name_Prefix + 'topic.', suffix)

    pattern_value = _Test_Name_Prefix + 'topic.' + suffix

    # .. create the permission ..
    item_id = create_permission(page, base_url, sec_name, 'publisher', 'pub', pattern_value)

    # .. edit - change access type to subscriber ..
    open_edit_dialog(page, 'permission', item_id)

    page.select_option('#id_edit-access_type', value='subscriber')
    time.sleep(0.3)

    submit_edit_form(page)
    time.sleep(0.3)

    # .. delete.
    trigger_delete(page, 'permission', item_id)
    confirm_delete(page)

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
        collect_console_errors(page, console_errors)

        # .. perform the full CRUD cycle ..
        _do_full_crud(page, base_url, 'console')

        # .. filter known noise and assert no real errors.
        real_errors = filter_console_noise(console_errors, _Console_Noise_Patterns)
        assert not real_errors, f'Console errors during CRUD:\n' + '\n'.join(real_errors)

# ################################################################################################################################

    def test_no_http_500_during_crud(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Collect server errors ..
        server_errors = [] # type: list
        collect_http_errors(page, server_errors)

        # .. perform the full CRUD cycle ..
        _do_full_crud(page, base_url, 'http500')

        # .. assert no 500s.
        assert not server_errors, f'HTTP 500+ responses during CRUD:\n' + '\n'.join(server_errors)

# ################################################################################################################################

    def test_full_crud_cycle(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        sec_name = create_basic_auth(page, base_url, _Test_Name_Prefix, 'crud')
        _ = create_topic(page, base_url, _Test_Name_Prefix + 'topic.', 'crud')

        pattern_value = _Test_Name_Prefix + 'topic.crud'

        # .. create the permission ..
        item_id = create_permission(page, base_url, sec_name, 'publisher', 'pub', pattern_value)

        # .. verify the row exists ..
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.query_selector(row_selector)
        assert row is not None, f'Row for "{sec_name}" should exist after create'

        row_text = row.inner_text()
        assert 'Publisher' in row_text, f'Expected "Publisher" in row, got: "{row_text}"'

        # .. edit - change access type to subscriber ..
        open_edit_dialog(page, 'permission', item_id)

        page.select_option('#id_edit-access_type', value='subscriber')
        time.sleep(0.3)

        submit_edit_form(page)
        time.sleep(0.3)

        # .. verify the row now shows Subscriber ..
        row = page.query_selector(row_selector)
        row_text = row.inner_text()
        assert 'Subscriber' in row_text, f'Expected "Subscriber" after edit, got: "{row_text}"'

        # .. delete ..
        trigger_delete(page, 'permission', item_id)
        confirm_delete(page)

        # .. verify the row is gone.
        row_after_delete = page.query_selector(row_selector)
        assert row_after_delete is None, f'Row for "{sec_name}" should be gone after delete'

# ################################################################################################################################

    def test_edit_access_type(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        sec_name = create_basic_auth(page, base_url, _Test_Name_Prefix, 'edit-access')
        _ = create_topic(page, base_url, _Test_Name_Prefix + 'topic.', 'edit-access')

        pattern_value = _Test_Name_Prefix + 'topic.edit-access'

        # .. create as publisher ..
        item_id = create_permission(page, base_url, sec_name, 'publisher', 'pub', pattern_value)

        # .. verify it shows Publisher ..
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.query_selector(row_selector)
        row_text = row.inner_text()
        assert 'Publisher' in row_text, f'Expected "Publisher", got: "{row_text}"'

        # .. edit to publisher-subscriber ..
        open_edit_dialog(page, 'permission', item_id)

        page.select_option('#id_edit-access_type', value='publisher-subscriber')
        time.sleep(0.3)

        submit_edit_form(page)
        time.sleep(0.3)

        # .. verify it now shows Publisher and Subscriber.
        row = page.query_selector(row_selector)
        row_text = row.inner_text()
        assert 'Publisher' in row_text, f'Expected "Publisher" in row, got: "{row_text}"'
        assert 'Subscriber' in row_text, f'Expected "Subscriber" in row, got: "{row_text}"'

# ################################################################################################################################

    def test_edit_pattern(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        sec_name = create_basic_auth(page, base_url, _Test_Name_Prefix, 'edit-pattern')
        _ = create_topic(page, base_url, _Test_Name_Prefix + 'topic.', 'edit-pattern')

        original_pattern = 'original.pattern.*'

        # .. create the permission ..
        item_id = create_permission(page, base_url, sec_name, 'publisher', 'pub', original_pattern)

        # .. verify original pattern is visible ..
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.query_selector(row_selector)
        row_text = row.inner_text()
        assert original_pattern in row_text, f'Expected "{original_pattern}" in row, got: "{row_text}"'

        # .. edit to change the pattern ..
        open_edit_dialog(page, 'permission', item_id)
        time.sleep(0.3)

        new_pattern = 'updated.pattern.*'
        page.fill('#edit-patterns-container .pattern-row:first-child .pattern-input', '')
        page.fill('#edit-patterns-container .pattern-row:first-child .pattern-input', new_pattern)

        submit_edit_form(page)
        time.sleep(0.5)

        # .. reload the page so pattern display is re-rendered ..
        navigate_to_page(page, base_url, _Permission_Page_Url)
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
        navigate_to_page(page, base_url, _Permission_Page_Url)

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
        sec_name = create_basic_auth(page, base_url, _Test_Name_Prefix, 'add-pat')
        _ = create_topic(page, base_url, _Test_Name_Prefix + 'topic.', 'add-pat')

        first_pattern = 'first.pattern.*'

        # .. create with one pattern as publisher-subscriber ..
        item_id = create_permission(page, base_url, sec_name, 'publisher-subscriber', 'pub', first_pattern)

        # .. open edit ..
        open_edit_dialog(page, 'permission', item_id)
        time.sleep(0.3)

        # .. add a second pattern row ..
        page.click('#edit-patterns-container .pattern-row:first-child .pattern-add-button')
        time.sleep(0.2)

        # .. fill the new row (prepended to top) with a sub pattern ..
        second_pattern = 'second.pattern.*'
        page.select_option('#edit-patterns-container .pattern-row:first-child .pattern-type-select', value='sub')
        page.fill('#edit-patterns-container .pattern-row:first-child .pattern-input', second_pattern)

        # .. submit ..
        submit_edit_form(page)
        time.sleep(0.5)

        # .. reload to re-render patterns ..
        navigate_to_page(page, base_url, _Permission_Page_Url)
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
        sec_name = create_basic_auth(page, base_url, _Test_Name_Prefix, 'rm-pat')
        _ = create_topic(page, base_url, _Test_Name_Prefix + 'topic.', 'rm-pat')

        pub_pattern = 'remove.pub.*'
        sub_pattern = 'remove.sub.*'

        # .. create with publisher-subscriber and two patterns ..
        item_id = create_permission_with_two_patterns(page, base_url, sec_name, pub_pattern, sub_pattern)

        # .. reload so patterns render ..
        navigate_to_page(page, base_url, _Permission_Page_Url)
        time.sleep(0.3)

        # .. verify both patterns are present ..
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.query_selector(row_selector)
        row_text = row.inner_text()
        assert pub_pattern in row_text, f'Expected "{pub_pattern}" before edit, got: "{row_text}"'
        assert sub_pattern in row_text, f'Expected "{sub_pattern}" before edit, got: "{row_text}"'

        # .. open edit and remove the first pattern row ..
        open_edit_dialog(page, 'permission', item_id)
        time.sleep(0.3)

        page.click('#edit-patterns-container .pattern-row:first-child .pattern-remove-button')
        time.sleep(0.2)

        # .. submit ..
        submit_edit_form(page)
        time.sleep(0.5)

        # .. reload ..
        navigate_to_page(page, base_url, _Permission_Page_Url)
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
        sec_name = create_basic_auth(page, base_url, _Test_Name_Prefix, 'cancel-edit')
        _ = create_topic(page, base_url, _Test_Name_Prefix + 'topic.', 'cancel-edit')

        pattern_value = 'cancel.edit.pattern.*'

        # .. create the permission as publisher ..
        item_id = create_permission(page, base_url, sec_name, 'publisher', 'pub', pattern_value)

        # .. reload so patterns are rendered ..
        navigate_to_page(page, base_url, _Permission_Page_Url)
        time.sleep(0.3)

        # .. verify the original state ..
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.query_selector(row_selector)
        row_text = row.inner_text()
        assert 'Publisher' in row_text, f'Expected "Publisher" before edit, got: "{row_text}"'

        # .. open edit and change values ..
        open_edit_dialog(page, 'permission', item_id)

        page.select_option('#id_edit-access_type', value='publisher-subscriber')
        time.sleep(0.2)
        page.fill('#edit-patterns-container .pattern-row:first-child .pattern-input', 'changed.pattern.*')

        # .. cancel without submitting ..
        close_dialog_via_jquery(page, 'edit-div')

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
        sec_name = create_basic_auth(page, base_url, _Test_Name_Prefix, 'cancel-del')
        _ = create_topic(page, base_url, _Test_Name_Prefix + 'topic.', 'cancel-del')

        pattern_value = 'cancel.delete.pattern.*'

        # .. create the permission ..
        item_id = create_permission(page, base_url, sec_name, 'publisher', 'pub', pattern_value)

        # .. trigger delete ..
        trigger_delete(page, 'permission', item_id)

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
        sec_name = create_basic_auth(page, base_url, _Test_Name_Prefix, 'prepop')
        _ = create_topic(page, base_url, _Test_Name_Prefix + 'topic.', 'prepop')

        pattern_value = 'prepopulated.pattern.*'

        # .. create as subscriber ..
        item_id = create_permission(page, base_url, sec_name, 'subscriber', 'sub', pattern_value)

        # .. open edit ..
        open_edit_dialog(page, 'permission', item_id)
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
        sec_name = create_basic_auth(page, base_url, _Test_Name_Prefix, 'readonly-sec')
        _ = create_topic(page, base_url, _Test_Name_Prefix + 'topic.', 'readonly-sec')

        pattern_value = 'readonly.sec.pattern.*'

        # .. create the permission ..
        item_id = create_permission(page, base_url, sec_name, 'publisher', 'pub', pattern_value)

        # .. open edit ..
        open_edit_dialog(page, 'permission', item_id)
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
        sec_name = create_basic_auth(page, base_url, _Test_Name_Prefix, 'grey-pat')
        _ = create_topic(page, base_url, _Test_Name_Prefix + 'topic.', 'grey-pat')

        pub_pattern = 'grey.pub.pattern.*'
        sub_pattern = 'grey.sub.pattern.*'

        # .. create with publisher-subscriber and both patterns ..
        item_id = create_permission_with_two_patterns(page, base_url, sec_name, pub_pattern, sub_pattern)

        # .. open edit and change access type to publisher only ..
        open_edit_dialog(page, 'permission', item_id)
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
        sec_name = create_basic_auth(page, base_url, _Test_Name_Prefix, 'link-row')
        _ = create_topic(page, base_url, _Test_Name_Prefix + 'topic.', 'link-row')

        pattern_value = 'link.row.pattern.*'

        # .. create the permission ..
        _ = create_permission(page, base_url, sec_name, 'publisher', 'pub', pattern_value)

        # .. reload so the page renders from the server ..
        navigate_to_page(page, base_url, _Permission_Page_Url)
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
