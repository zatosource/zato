# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/pubsub/topic/?cluster=1'

_Test_Name_Prefix = 'test.life.' + os.urandom(4).hex() + '.'

_Page_Size = 20

_Console_Noise_Patterns = [
    'favicon.ico',
    'ERR_CONNECTION_REFUSED',
    'live-form-updates',
    'Content-Security-Policy',
]

# ################################################################################################################################
# ################################################################################################################################

def _create_topic(page:'Page', suffix:'str', description:'str'='') -> 'dict':
    """ Creates a pub/sub topic via the UI and returns its details.
    """

    name = _Test_Name_Prefix + suffix

    # Open the create dialog ..
    page.click('#markup .page_prompt a')
    page.wait_for_selector('#create-div', state='visible')

    # .. fill in the fields ..
    page.fill('#id_name', name)
    if description:
        page.fill('#id_description', description)

    # .. submit and wait for the dialog to close ..
    page.click('#create-div input[type="submit"]')
    page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    # .. wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=5000)

    out = {
        'name': name,
        'description': description,
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
    """ Performs a full CRUD cycle: create, edit, delete.
    """

    # Navigate ..
    _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
    page.wait_for_selector('#data-table', state='visible')

    # .. create ..
    topic = _create_topic(page, suffix, 'Description for ' + suffix)

    # .. edit ..
    item_id = _get_item_id(page, topic['name'])
    page.evaluate(f'$.fn.zato.pubsub.topic.edit("{item_id}")')
    page.wait_for_selector('#edit-div', state='visible', timeout=5000)

    edited_name = topic['name'] + '-edited'
    page.fill('#id_edit-name', '')
    page.fill('#id_edit-name', edited_name)

    page.click('#edit-div input[type="submit"]')
    page.wait_for_selector('#edit-div', state='hidden', timeout=10000)
    time.sleep(0.3)

    # .. delete.
    page.evaluate(f'$.fn.zato.pubsub.topic.delete_("{item_id}")')
    page.wait_for_selector('#popup_container', state='visible', timeout=5000)
    page.click('#popup_ok')
    time.sleep(0.5)

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
        _do_full_crud(page, base_url, 'http500-check')

        # .. assert no 500s.
        assert not server_errors, f'HTTP 500+ responses during CRUD:\n' + '\n'.join(server_errors)

# ################################################################################################################################

    def test_full_crud_cycle(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create ..
        topic = _create_topic(page, 'crud', 'Original description')

        # .. verify row exists ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{topic["name"]}"))')
        assert row is not None, f'Row "{topic["name"]}" should exist after create'

        # .. edit the name and description ..
        item_id = _get_item_id(page, topic['name'])
        page.evaluate(f'$.fn.zato.pubsub.topic.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        edited_name = topic['name'] + '-edited'
        page.fill('#id_edit-name', '')
        page.fill('#id_edit-name', edited_name)
        page.fill('#id_edit-description', '')
        page.fill('#id_edit-description', 'Edited description')

        page.click('#edit-div input[type="submit"]')
        page.wait_for_selector('#edit-div', state='hidden', timeout=10000)
        time.sleep(0.3)

        # .. verify old name gone, new name present ..
        old_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{topic["name"]}"))')
        assert old_row is None, f'Old name "{topic["name"]}" should be gone after edit'

        new_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{edited_name}"))')
        assert new_row is not None, f'Edited name "{edited_name}" should be present'

        # .. delete ..
        page.evaluate(f'$.fn.zato.pubsub.topic.delete_("{item_id}")')
        page.wait_for_selector('#popup_container', state='visible', timeout=5000)
        page.click('#popup_ok')
        time.sleep(0.5)

        # .. verify gone.
        row_after_delete = page.query_selector(f'#data-table tbody tr:has(td:text-is("{edited_name}"))')
        assert row_after_delete is None, f'Row "{edited_name}" should be gone after delete'

# ################################################################################################################################

    def test_sort_by_name(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create three topics in non-alphabetical order ..
        name_b = _create_topic(page, 'sort-b')['name']
        name_a = _create_topic(page, 'sort-a')['name']
        name_c = _create_topic(page, 'sort-c')['name']

        sorted_asc = [name_a, name_b, name_c]
        sorted_desc = [name_c, name_b, name_a]

        # .. reload with query filter so our test rows are visible ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}&query={_Test_Name_Prefix}sort')
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
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create a topic with no description ..
        topic = _create_topic(page, 'edit-desc')

        # .. reload so the server renders the no-value indicator ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}&query={topic["name"]}')
        page.wait_for_selector('#data-table', state='visible')

        # .. verify the description cell shows the placeholder ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{topic["name"]}"))'
        row = page.query_selector(row_selector)
        cells = row.query_selector_all('td')
        desc_text = cells[3].inner_text().strip()
        assert desc_text == '---', f'Expected "---" for empty description, got: "{desc_text}"'

        # .. edit to add a description ..
        item_id = _get_item_id(page, topic['name'])
        page.evaluate(f'$.fn.zato.pubsub.topic.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        page.fill('#id_edit-description', 'Added description')

        page.click('#edit-div input[type="submit"]')
        page.wait_for_selector('#edit-div', state='hidden', timeout=10000)
        time.sleep(0.3)

        # .. verify the description cell is updated.
        row = page.query_selector(row_selector)
        cells = row.query_selector_all('td')
        desc_text = cells[3].inner_text().strip()
        assert desc_text == 'Added description', \
            f'Expected "Added description", got: "{desc_text}"'

# ################################################################################################################################

    def test_publish_a_message_link(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create a topic ..
        topic = _create_topic(page, 'publish-link')

        # .. click "Publish a message" ..
        item_id = _get_item_id(page, topic['name'])
        page.evaluate(f'$.fn.zato.pubsub.topic.publishMessage("{item_id}")')

        # .. verify the invoker overlay opens ..
        page.wait_for_selector('#invoker-modal-overlay', state='visible', timeout=5000)

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
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. count existing rows to determine how many more we need ..
        existing_rows = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        existing_count = len(existing_rows)
        needed = max(0, _Page_Size + 1 - existing_count)

        # .. create enough topics to exceed the page size ..
        for idx in range(needed):
            _ = _create_topic(page, f'pag-{idx:02d}')

        # .. reload so pagination kicks in ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

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
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. count existing rows to determine how many more we need for 3 pages ..
        existing_rows = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        existing_count = len(existing_rows)
        needed = max(0, (_Page_Size * 2) + 1 - existing_count)

        # .. create enough topics ..
        for idx in range(needed):
            _ = _create_topic(page, f'nav-{idx:02d}')

        # .. reload ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

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
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create 3 topics with the filter prefix ..
        created_names = []
        for idx in range(3):
            topic = _create_topic(page, f'srch-{idx}')
            created_names.append(topic['name'])

        # .. navigate with query filter ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}&query={filter_prefix}')
        page.wait_for_selector('#data-table', state='visible')

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
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. count existing rows to determine how many more we need ..
        existing_rows = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        existing_count = len(existing_rows)
        needed = max(0, _Page_Size + 1 - existing_count)

        # .. create enough topics ..
        for idx in range(needed):
            _ = _create_topic(page, f'info-{idx:02d}')

        # .. reload ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. verify info text ..
        action_panel = page.query_selector('.action-panel')
        panel_text = action_panel.inner_text()

        assert 'Page 1 of' in panel_text, f'Expected "Page 1 of" in panel, got: "{panel_text}"'
        assert 'result' in panel_text, f'Expected "result" in panel, got: "{panel_text}"'

# ################################################################################################################################

    @pytest.mark.expect_log_errors('Timeout', 'waiting for service')
    def test_import_demo_config(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. count rows before ..
        rows_before = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        count_before = len(rows_before)

        # .. click "Import demo config" ..
        page.click('a:has-text("Import demo config")')

        # .. wait for page reload ..
        page.wait_for_load_state('networkidle', timeout=30000)
        page.wait_for_selector('#data-table', state='visible')

        # .. verify topics appeared (row count increased or stayed the same if paginated,
        # .. but we know a fresh server has no topics before this test runs the import).
        rows_after = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        count_after = len(rows_after)

        assert count_after >= count_before, \
            f'Expected at least as many rows after import, got before={count_before}, after={count_after}'

        # .. verify there is at least one row in the table now.
        assert count_after > 0, 'Expected at least one topic after demo config import'

# ################################################################################################################################

    def test_topic_name_with_hash_rejected(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        bad_name = _Test_Name_Prefix + 'has#hash'

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open the create dialog and type the invalid name character by character
        # .. so the live validation fires ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

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
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open the create dialog and fill the overlong name ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

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
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open the create dialog and fill the non-ASCII name ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

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
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open the create dialog and try to submit with an empty name ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

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
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create a topic to edit ..
        topic = _create_topic(page, 'edit-invalid')

        # .. reload so the server knows about it ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}&query={topic["name"]}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open the edit dialog ..
        item_id = _get_item_id(page, topic['name'])
        page.evaluate(f'$.fn.zato.pubsub.topic.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

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
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create two topics ..
        topic_a = _create_topic(page, 'dup-a')
        topic_b = _create_topic(page, 'dup-b')

        # .. reload so the server knows about both ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}&query={_Test_Name_Prefix}dup')
        page.wait_for_selector('#data-table', state='visible')

        # .. edit topic_b to have topic_a's name ..
        item_id = _get_item_id(page, topic_b['name'])
        page.evaluate(f'$.fn.zato.pubsub.topic.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

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
