# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.test.playwright_pubsub import close_dialog_via_jquery, get_table_row_count, navigate_to_page, \
    open_create_dialog, submit_create_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/pubsub/topic/?cluster=1'

_Test_Name_Prefix = 'test.pubsub.topic.' + os.urandom(4).hex() + '.'

# ################################################################################################################################
# ################################################################################################################################

class TestPubSubTopicCreate:
    """ Tests for the pub/sub topic create flow.
    """

    def test_page_loads(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the topics page ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. verify the page heading ..
        heading = page.query_selector('h2.zato')
        heading_text = heading.inner_text()
        assert 'Pub/sub topics' in heading_text, f'Expected "Pub/sub topics" in heading, got: {heading_text}'

        # .. verify the create link is present ..
        create_link = page.query_selector('#markup .page_prompt a')
        create_link_text = create_link.inner_text()
        assert 'Create a new pub/sub topic' in create_link_text, \
            f'Expected create link text, got: {create_link_text}'

        # .. verify table headers.
        headers = page.query_selector_all('#data-table thead th a')

        header_texts = [] # type: list

        for header in headers:
            raw_text = header.inner_text()
            text = raw_text.strip().lower()
            header_texts.append(text)

        assert 'name' in header_texts, f'Expected "name" in headers, got: {header_texts}'
        assert 'description' in header_texts, f'Expected "description" in headers, got: {header_texts}'

# ################################################################################################################################

    def test_create_one(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        topic_name = _Test_Name_Prefix + 'create-one'
        topic_description = 'Description for ' + topic_name

        # Navigate to the topics page ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. open the create dialog ..
        open_create_dialog(page)

        # .. fill in the form fields ..
        page.fill('#id_name', topic_name)
        page.fill('#id_description', topic_description)

        # .. submit the form ..
        submit_create_form(page)

        # .. verify the new row appears in the table ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{topic_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. extract cell texts from the row ..
        cells = row.query_selector_all('td')

        name_cell_text = cells[2].inner_text().strip()
        description_cell_text = cells[4].inner_text().strip()

        # .. verify each cell has the correct value.
        assert name_cell_text == topic_name, \
            f'Expected name "{topic_name}", got: "{name_cell_text}"'

        assert description_cell_text == topic_description, \
            f'Expected description "{topic_description}", got: "{description_cell_text}"'

# ################################################################################################################################

    def test_create_multiple(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Prepare 3 distinct topics ..
        topics = []

        for index in range(3):
            name = _Test_Name_Prefix + f'multi-{index}'
            description = f'Description {index}'
            topics.append((name, description))

        # Navigate to the topics page ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create each topic ..
        for name, description in topics:

            # .. open the create dialog ..
            open_create_dialog(page)

            # .. fill in the form fields ..
            page.fill('#id_name', name)
            page.fill('#id_description', description)

            # .. submit and wait for the dialog to close.
            submit_create_form(page)

        # .. verify all 3 rows are present with correct values.
        for name, description in topics:

            row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
            row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

            cells = row.query_selector_all('td')

            name_cell_text = cells[2].inner_text().strip()
            description_cell_text = cells[4].inner_text().strip()

            assert name_cell_text == name, \
                f'Expected name "{name}", got: "{name_cell_text}"'

            assert description_cell_text == description, \
                f'Expected description "{description}", got: "{description_cell_text}"'

# ################################################################################################################################

    def test_create_then_reopen_form_is_empty(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        topic_name = _Test_Name_Prefix + 'reopen-empty'

        # Navigate to the topics page ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. create a topic first ..
        open_create_dialog(page)

        page.fill('#id_name', topic_name)
        page.fill('#id_description', 'Some description')

        submit_create_form(page)

        # .. reopen the create dialog ..
        open_create_dialog(page)

        # .. verify all fields are empty.
        name_value = page.input_value('#id_name')
        description_value = page.input_value('#id_description')

        assert name_value == '', f'Expected empty name, got: "{name_value}"'
        assert description_value == '', f'Expected empty description, got: "{description_value}"'

# ################################################################################################################################

    def test_cancel_then_reopen_form_is_empty(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the topics page ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. open the create dialog and fill fields ..
        open_create_dialog(page)

        page.fill('#id_name', _Test_Name_Prefix + 'cancel-test')
        page.fill('#id_description', 'Cancel description')

        # .. close the dialog via jQuery UI ..
        close_dialog_via_jquery(page, 'create-div')

        # .. reopen the dialog ..
        open_create_dialog(page)

        # .. verify all fields are empty.
        name_value = page.input_value('#id_name')
        description_value = page.input_value('#id_description')

        assert name_value == '', f'Expected empty name, got: "{name_value}"'
        assert description_value == '', f'Expected empty description, got: "{description_value}"'

# ################################################################################################################################

    def test_cancel_no_row_added(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        cancelled_name = _Test_Name_Prefix + 'should-not-exist'

        # Navigate to the topics page ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. count rows before ..
        count_before = get_table_row_count(page)

        # .. open the create dialog and fill fields ..
        open_create_dialog(page)

        page.fill('#id_name', cancelled_name)
        page.fill('#id_description', 'Should not be saved')

        # .. close the dialog via jQuery UI ..
        close_dialog_via_jquery(page, 'create-div')

        # .. verify row count is unchanged ..
        count_after = get_table_row_count(page)

        assert count_after == count_before, \
            f'Expected {count_before} rows after cancel, got: {count_after}'

        # .. verify the cancelled name does not appear in the table.
        page_content = page.content()
        assert cancelled_name not in page_content, \
            f'Cancelled name "{cancelled_name}" should not be in the page'

# ################################################################################################################################

    def test_duplicate_name_shows_taken_indicator(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        existing_name = _Test_Name_Prefix + 'duplicate-check'

        # Navigate and create a topic to have a known name ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        open_create_dialog(page)

        page.fill('#id_name', existing_name)

        submit_create_form(page)

        # .. reload the page so the server's check_attr_exists picks up the new topic ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. reopen the create dialog and type the same name character by character
        # .. so that the input event handler triggers the uniqueness check ..
        open_create_dialog(page)

        name_field = page.locator('#id_name')
        name_field.click()
        name_field.press_sequentially(existing_name, delay=10)

        # .. wait for the async uniqueness check (300ms timer + network) ..
        taken_indicator = page.wait_for_selector(
            '#create-form .zato-unique-taken', state='visible', timeout=10000)

        # .. verify the indicator text.
        taken_text = taken_indicator.inner_text()
        assert 'Already taken' in taken_text, f'Expected "Already taken", got: "{taken_text}"'

# ################################################################################################################################

    def test_unique_name_shows_ok_indicator(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        unique_name = _Test_Name_Prefix + 'unique-check-' + os.urandom(4).hex()

        # Navigate to the topics page ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. open the create dialog and type a unique name character by character
        # .. so that the input event handler triggers the uniqueness check ..
        open_create_dialog(page)

        name_field = page.locator('#id_name')
        name_field.click()
        name_field.press_sequentially(unique_name, delay=10)

        # .. wait for the async uniqueness check ..
        ok_indicator = page.wait_for_selector(
            '#create-form .zato-unique-ok', state='visible', timeout=10000)

        # .. verify the checkmark is present.
        ok_text = ok_indicator.inner_text()
        assert '\u2713' in ok_text, f'Expected checkmark in indicator, got: "{ok_text}"'

# ################################################################################################################################

    def test_create_with_empty_description(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        topic_name = _Test_Name_Prefix + 'no-desc'

        # Navigate to the topics page ..
        navigate_to_page(page, base_url, _Page_Url_Pattern)

        # .. open the create dialog ..
        open_create_dialog(page)

        # .. fill in name only, leave description empty ..
        page.fill('#id_name', topic_name)

        # .. submit the form ..
        submit_create_form(page)

        # .. verify the new row appears ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{topic_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. verify description cell shows the form_hint placeholder.
        cells = row.query_selector_all('td')
        description_cell_text = cells[4].inner_text().strip()
        description_cell_html = cells[4].inner_html()

        assert description_cell_text == '---', \
            f'Expected "---" for empty description, got: "{description_cell_text}"'

        assert 'class="form_hint"' in description_cell_html, \
            f'Expected form_hint span in description cell, got: "{description_cell_html}"'

# ################################################################################################################################
# ################################################################################################################################
