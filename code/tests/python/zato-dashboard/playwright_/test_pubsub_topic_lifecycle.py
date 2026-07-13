# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import collect_console_errors, collect_http_errors, confirm_delete, create_topic, \
    filter_console_noise, get_item_id, get_table_row_count, navigate_to_page, open_create_dialog, open_edit_dialog, \
    open_publish_overlay, submit_create_form, submit_edit_form, trigger_delete

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/pubsub/topic/?cluster=1'

_Test_Name_Prefix = 'test.life.' + CryptoManager.generate_hex_string(32) + '.'

_Page_Size = 20

_Console_Noise_Patterns = [
    'favicon.ico',
    'ERR_CONNECTION_REFUSED',
    'live-form-updates',
    'Content-Security-Policy',
]

# ################################################################################################################################
# ################################################################################################################################

def _do_full_crud(page:'Page', base_url:'str', suffix:'str') -> 'None':
    """ Performs a full CRUD cycle: create, edit, delete.
    """

    # Navigate ..
    navigate_to_page(page, base_url, _Page_Url_Pattern)

    # .. create ..
    topic = create_topic(page, base_url, _Test_Name_Prefix, suffix, 'Description for ' + suffix)

    # .. edit ..
    open_edit_dialog(page, 'topic', topic['item_id'])

    edited_name = topic['name'] + '-edited'
    page.fill('#id_edit-name', '')
    page.fill('#id_edit-name', edited_name)

    submit_edit_form(page)
    time.sleep(0.3)

    # .. delete.
    trigger_delete(page, 'topic', topic['item_id'])
    confirm_delete(page)

# ################################################################################################################################
# ################################################################################################################################

class TestPubSubTopicLifecycle:
    """ Tests for console errors, HTTP 500s, full CRUD, sorting, editing, pagination, and validation.
    """

    def test_no_console_errors_during_crud(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Collect console errors ..
        console_errors = [] # type: list
        collect_console_errors(page, console_errors)

        # .. perform the full CRUD cycle ..
        _do_full_crud(page, base_url, 'console-check')

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
        _do_full_crud(page, base_url, 'http500-check')

        # .. assert no 500s.
        assert not server_errors, f'HTTP 500+ responses during CRUD:\n' + '\n'.join(server_errors)

# ################################################################################################################################

    def test_full_crud_cycle(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create ..
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'crud', 'Original description')

        # .. verify row exists ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{topic["name"]}"))')
        assert row is not None, f'Row "{topic["name"]}" should exist after create'

        # .. edit the name and description ..
        open_edit_dialog(page, 'topic', topic['item_id'])

        edited_name = topic['name'] + '-edited'
        page.fill('#id_edit-name', '')
        page.fill('#id_edit-name', edited_name)
        page.fill('#id_edit-description', '')
        page.fill('#id_edit-description', 'Edited description')

        submit_edit_form(page)
        time.sleep(0.3)

        # .. verify old name gone, new name present ..
        old_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{topic["name"]}"))')
        assert old_row is None, f'Old name "{topic["name"]}" should be gone after edit'

        new_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{edited_name}"))')
        assert new_row is not None, f'Edited name "{edited_name}" should be present'

        # .. delete ..
        trigger_delete(page, 'topic', topic['item_id'])
        confirm_delete(page)

        # .. verify gone.
        row_after_delete = page.query_selector(f'#data-table tbody tr:has(td:text-is("{edited_name}"))')
        assert row_after_delete is None, f'Row "{edited_name}" should be gone after delete'

# ################################################################################################################################

    def test_sort_by_name(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create three topics in non-alphabetical order ..
        name_b = create_topic(page, base_url, _Test_Name_Prefix, 'sort-b')['name']
        name_a = create_topic(page, base_url, _Test_Name_Prefix, 'sort-a')['name']
        name_c = create_topic(page, base_url, _Test_Name_Prefix, 'sort-c')['name']

        sorted_asc = [name_a, name_b, name_c]
        sorted_desc = [name_c, name_b, name_a]

        # .. reload with query filter so our test rows are visible ..
        navigate_to_page(page, base_url, f'{_Page_Url_Pattern}&query={_Test_Name_Prefix}sort')

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

        # .. the two clicks must produce opposite orders.
        assert our_first != our_second, \
            f'Clicking header twice should reverse order, got same: {our_first}'

        assert (our_first == sorted_asc and our_second == sorted_desc) or \
               (our_first == sorted_desc and our_second == sorted_asc), \
            f'Expected one asc and one desc, got first={our_first}, second={our_second}'

# ################################################################################################################################

    def test_edit_description_only(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create a topic with no description ..
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'edit-desc')

        # .. reload so the server renders the no-value indicator ..
        navigate_to_page(page, base_url, f'{_Page_Url_Pattern}&query={topic["name"]}')

        # .. verify the description cell shows the placeholder ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{topic["name"]}"))'
        row = page.query_selector(row_selector)
        cells = row.query_selector_all('td')
        desc_text = cells[4].inner_text().strip()
        assert desc_text == '---', f'Expected "---" for empty description, got: "{desc_text}"'

        # .. edit to add a description ..
        open_edit_dialog(page, 'topic', topic['item_id'])

        page.fill('#id_edit-description', 'Added description')

        submit_edit_form(page)
        time.sleep(0.3)

        # .. verify the description cell is updated.
        row = page.query_selector(row_selector)
        cells = row.query_selector_all('td')
        desc_text = cells[4].inner_text().strip()
        assert desc_text == 'Added description', \
            f'Expected "Added description", got: "{desc_text}"'

# ################################################################################################################################

    def test_edit_description_to_empty_shows_placeholder(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create a topic with a description ..
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'edit-desc-clear', 'Has a description')

        # .. reload so the server renders the row ..
        navigate_to_page(page, base_url, f'{_Page_Url_Pattern}&query={topic["name"]}')

        # .. verify the description is shown ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{topic["name"]}"))'
        row = page.query_selector(row_selector)
        cells = row.query_selector_all('td')
        desc_text = cells[4].inner_text().strip()
        assert desc_text == 'Has a description', \
            f'Expected "Has a description", got: "{desc_text}"'

        # .. open the edit dialog and clear the description ..
        open_edit_dialog(page, 'topic', topic['item_id'])

        page.fill('#id_edit-description', '')

        submit_edit_form(page)
        time.sleep(0.3)

        # .. verify the description cell now shows the form_hint placeholder.
        row = page.query_selector(row_selector)
        cells = row.query_selector_all('td')
        desc_text = cells[4].inner_text().strip()
        desc_html = cells[4].inner_html()

        assert desc_text == '---', \
            f'Expected "---" for cleared description, got: "{desc_text}"'

        assert 'class="form_hint"' in desc_html, \
            f'Expected form_hint span in description cell, got: "{desc_html}"'

# ################################################################################################################################

    def test_publish_a_message_link(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create a topic ..
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'publish-link')

        # .. click "Publish a message" ..
        open_publish_overlay(page, topic['item_id'])

        # .. verify the title contains the topic name.
        title_elem = page.query_selector('#invoker-modal-title')
        title_text = title_elem.inner_text()
        assert topic['name'] in title_text, \
            f'Expected topic name "{topic["name"]}" in overlay title, got: "{title_text}"'

# ################################################################################################################################

    def test_pagination_controls_visible(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. count existing rows to determine how many more we need ..
        existing_count = get_table_row_count(page)
        needed = max(0, _Page_Size + 1 - existing_count)

        # .. create enough topics to exceed the page size ..
        for idx in range(needed):
            _ = create_topic(page, base_url, _Test_Name_Prefix, f'pag-{idx:02d}')

        # .. reload so pagination kicks in ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. verify pagination controls exist ..
        action_panel = page.query_selector('.action-panel')
        assert action_panel is not None, 'Pagination action-panel should be visible with 21+ items'

        # .. verify result count text ..
        panel_text = action_panel.inner_text()
        assert 'result' in panel_text, f'Expected "result" in panel text, got: "{panel_text}"'
        assert 'Page' in panel_text, f'Expected "Page" in panel text, got: "{panel_text}"'

        # .. verify the "Next" link is present.
        next_link = page.query_selector('.action-panel a:has-text("Next")')
        assert next_link is not None, 'Next page link should be present'

# ################################################################################################################################

    def test_pagination_navigate_forward_and_back(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. count existing rows to determine how many more we need for 3 pages ..
        existing_count = get_table_row_count(page)
        needed = max(0, (_Page_Size * 2) + 1 - existing_count)

        # .. create enough topics ..
        for idx in range(needed):
            _ = create_topic(page, base_url, _Test_Name_Prefix, f'nav-{idx:02d}')

        # .. reload ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. collect page 1 names ..
        cells_p1 = page.query_selector_all('#data-table tbody tr:not(.ignore) td:nth-child(3)')
        names_p1 = [cell.inner_text().strip() for cell in cells_p1 if cell.inner_text().strip()]

        # .. click Next to page 2 ..
        page.click('.action-panel a:has-text("Next")')
        page.wait_for_selector('#data-table', state='visible')
        time.sleep(0.3)

        cells_p2 = page.query_selector_all('#data-table tbody tr:not(.ignore) td:nth-child(3)')
        names_p2 = [cell.inner_text().strip() for cell in cells_p2 if cell.inner_text().strip()]

        # .. page 1 and page 2 must differ ..
        assert set(names_p1) != set(names_p2), 'Page 1 and page 2 should show different rows'

        # .. click Next to page 3 ..
        page.click('.action-panel a:has-text("Next")')
        page.wait_for_selector('#data-table', state='visible')
        time.sleep(0.3)

        cells_p3 = page.query_selector_all('#data-table tbody tr:not(.ignore) td:nth-child(3)')
        names_p3 = [cell.inner_text().strip() for cell in cells_p3 if cell.inner_text().strip()]

        assert set(names_p2) != set(names_p3), 'Page 2 and page 3 should show different rows'

        # .. click Previous back to page 2 ..
        page.click('.action-panel a:has-text("Previous")')
        page.wait_for_selector('#data-table', state='visible')
        time.sleep(0.3)

        cells_back = page.query_selector_all('#data-table tbody tr:not(.ignore) td:nth-child(3)')
        names_back = [cell.inner_text().strip() for cell in cells_back if cell.inner_text().strip()]

        # .. should match page 2.
        assert set(names_back) == set(names_p2), \
            f'Going back should show page 2 rows, got: {names_back}'

# ################################################################################################################################

    def test_search_filters(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        filter_prefix = _Test_Name_Prefix + 'srch'

        # Navigate ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create 3 topics with the filter prefix ..
        created_names = []
        for idx in range(3):
            topic = create_topic(page, base_url, _Test_Name_Prefix, f'srch-{idx}')
            created_names.append(topic['name'])

        # .. navigate with query filter ..
        navigate_to_page(page, base_url, f'{_Page_Url_Pattern}&query={filter_prefix}')

        # .. collect all visible names ..
        cells = page.query_selector_all('#data-table tbody tr:not(.ignore) td:nth-child(3)')
        visible_names = [cell.inner_text().strip() for cell in cells if cell.inner_text().strip()]

        # .. all 3 created names must be in the filtered results.
        for name in created_names:
            assert name in visible_names, f'Expected "{name}" in filtered results, got: {visible_names}'

# ################################################################################################################################

    def test_pagination_info_text(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. count existing rows to determine how many more we need ..
        existing_count = get_table_row_count(page)
        needed = max(0, _Page_Size + 1 - existing_count)

        # .. create enough topics ..
        for idx in range(needed):
            _ = create_topic(page, base_url, _Test_Name_Prefix, f'info-{idx:02d}')

        # .. reload ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. verify info text ..
        action_panel = page.query_selector('.action-panel')
        panel_text = action_panel.inner_text()

        assert 'Page 1 of' in panel_text, f'Expected "Page 1 of" in panel, got: "{panel_text}"'
        assert 'result' in panel_text, f'Expected "result" in panel, got: "{panel_text}"'

# ################################################################################################################################

    def test_import_demo_config(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. count rows before ..
        count_before = get_table_row_count(page)

        # .. click "Import demo config" and wait for the import GET itself - the import runs
        # .. a synchronous enmasse subprocess server-side, so it needs a generous timeout,
        # .. and on success the page calls window.location.reload(), hence the navigation wait ..
        with page.expect_navigation(wait_until='load', timeout=150000):
            with page.expect_response('**/zato/pubsub/import-demo-config', timeout=120000) as response_info:
                page.click('a:has-text("Import demo config")')

        response = response_info.value
        assert response.status == 200, f'Import demo config returned {response.status}'

        page.wait_for_selector('#data-table', state='visible')

        # .. verify topics appeared.
        count_after = get_table_row_count(page)

        assert count_after >= count_before, \
            f'Expected at least as many rows after import, got before={count_before}, after={count_after}'

        assert count_after > 0, 'Expected at least one topic after demo config import'

# ################################################################################################################################

    def test_topic_name_with_hash_rejected(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        bad_name = _Test_Name_Prefix + 'has#hash'

        # Navigate ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. open the create dialog and type the invalid name character by character
        # .. so the live validation fires ..
        open_create_dialog(page)

        name_field = page.locator('#id_name')
        name_field.click()
        name_field.press_sequentially(bad_name, delay=10)

        # .. wait for the inline validation indicator ..
        indicator = page.wait_for_selector(
            '#create-form .zato-name-invalid', state='visible', timeout=10000)

        indicator_text = indicator.inner_text()
        assert 'Name cannot be used' in indicator_text, \
            f'Expected "Name cannot be used", got: "{indicator_text}"'

        # .. try to submit and verify the dialog stays open.
        page.click('#create-div input[type="submit"]')
        time.sleep(0.5)

        is_visible = page.evaluate('!!document.querySelector("#create-div").offsetParent')
        assert is_visible, 'Create dialog should stay open when name is invalid'

# ################################################################################################################################

    def test_topic_name_max_length_rejected(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        bad_name = 'a' * 201

        # Navigate ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. open the create dialog and fill the overlong name ..
        open_create_dialog(page)

        page.fill('#id_name', bad_name)

        # .. try to submit - the before_submit_hook will call the backend and block it ..
        page.click('#create-div input[type="submit"]')
        time.sleep(0.5)

        # .. verify the inline indicator appeared ..
        indicator = page.wait_for_selector(
            '#create-form .zato-name-invalid', state='visible', timeout=10000)

        indicator_text = indicator.inner_text()
        assert 'Name cannot be used' in indicator_text, \
            f'Expected "Name cannot be used", got: "{indicator_text}"'

        # .. and the dialog stays open.
        is_visible = page.evaluate('!!document.querySelector("#create-div").offsetParent')
        assert is_visible, 'Create dialog should stay open when name is too long'

# ################################################################################################################################

    def test_topic_name_with_non_ascii_rejected(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        bad_name = _Test_Name_Prefix + '\u017e\u0161\u010d'

        # Navigate ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. open the create dialog and fill the non-ASCII name ..
        open_create_dialog(page)

        page.fill('#id_name', bad_name)

        # .. try to submit - the before_submit_hook will call the backend and block it ..
        page.click('#create-div input[type="submit"]')
        time.sleep(0.5)

        # .. verify the inline indicator appeared ..
        indicator = page.wait_for_selector(
            '#create-form .zato-name-invalid', state='visible', timeout=10000)

        indicator_text = indicator.inner_text()
        assert 'Name cannot be used' in indicator_text, \
            f'Expected "Name cannot be used", got: "{indicator_text}"'

        # .. and the dialog stays open.
        is_visible = page.evaluate('!!document.querySelector("#create-div").offsetParent')
        assert is_visible, 'Create dialog should stay open when name has non-ASCII characters'

# ################################################################################################################################

    def test_create_with_empty_name_rejected(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. open the create dialog and try to submit with an empty name ..
        open_create_dialog(page)

        page.click('#create-div input[type="submit"]')
        time.sleep(0.5)

        # .. verify the dialog stays open.
        is_visible = page.evaluate('!!document.querySelector("#create-div").offsetParent')
        assert is_visible, 'Create dialog should stay open when name is empty'

# ################################################################################################################################

    def test_edit_topic_name_to_invalid_rejected(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create a topic to edit ..
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'edit-invalid')

        # .. reload so the server knows about it ..
        navigate_to_page(page, base_url, f'{_Page_Url_Pattern}&query={topic["name"]}')

        # .. open the edit dialog ..
        open_edit_dialog(page, 'topic', topic['item_id'])

        # .. clear the name and type an invalid one with # ..
        name_field = page.locator('#id_edit-name')
        name_field.fill('')
        name_field.press_sequentially('invalid#name', delay=10)

        # .. wait for the inline validation indicator ..
        indicator = page.wait_for_selector(
            '#edit-form .zato-name-invalid', state='visible', timeout=10000)

        indicator_text = indicator.inner_text()
        assert 'Name cannot be used' in indicator_text, \
            f'Expected "Name cannot be used", got: "{indicator_text}"'

        # .. try to submit and verify the dialog stays open.
        page.click('#edit-div input[type="submit"]')
        time.sleep(0.5)

        is_visible = page.evaluate('!!document.querySelector("#edit-div").offsetParent')
        assert is_visible, 'Edit dialog should stay open when name is invalid'

# ################################################################################################################################

    def test_edit_topic_name_to_duplicate_rejected(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create two topics ..
        topic_a = create_topic(page, base_url, _Test_Name_Prefix, 'dup-a')
        topic_b = create_topic(page, base_url, _Test_Name_Prefix, 'dup-b')

        # .. reload so the server knows about both ..
        navigate_to_page(page, base_url, f'{_Page_Url_Pattern}&query={_Test_Name_Prefix}dup')

        # .. edit topic_b to have topic_a's name ..
        item_id = get_item_id(page, topic_b['name'])
        open_edit_dialog(page, 'topic', item_id)

        name_field = page.locator('#id_edit-name')
        name_field.fill('')
        name_field.press_sequentially(topic_a['name'], delay=10)

        # .. wait for the uniqueness indicator ..
        taken_indicator = page.wait_for_selector(
            '#edit-form .zato-unique-taken', state='visible', timeout=10000)

        taken_text = taken_indicator.inner_text()
        assert 'Already taken' in taken_text, f'Expected "Already taken", got: "{taken_text}"'

# ################################################################################################################################
# ################################################################################################################################
