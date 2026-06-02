# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time

# Zato
from zato.common.test.playwright_pubsub import close_dialog_via_jquery, create_basic_auth, create_permission, \
    create_topic, get_table_row_count, navigate_to_page, open_create_dialog, open_create_dialog_via_js, \
    setup_alert_handler, submit_create_form, wait_for_sec_def_dropdown

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Permission_Page_Url = '/zato/pubsub/permission/?cluster=1'
_Topic_Page_Url = '/zato/pubsub/topic/?cluster=1'

_Test_Name_Prefix = 'test.permission.' + os.urandom(4).hex() + '.'

# ################################################################################################################################
# ################################################################################################################################

class TestPubSubPermissionCreate:
    """ Tests for the pub/sub permission create flow.
    """

    def test_page_loads(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the permissions page ..
        navigate_to_page(page, base_url, _Permission_Page_Url)

        # .. verify the page heading ..
        heading = page.query_selector('h2.zato')
        heading_text = heading.inner_text()
        assert 'Pub/sub permissions' in heading_text, f'Expected "Pub/sub permissions" in heading, got: {heading_text}'

        # .. verify the create link is present ..
        create_link = page.query_selector('#markup .page_prompt a')
        create_link_text = create_link.inner_text()
        assert 'Create a new permission' in create_link_text, \
            f'Expected create link text, got: {create_link_text}'

        # .. verify table headers.
        headers = page.query_selector_all('#data-table thead th a')

        header_texts = [] # type: list

        for header in headers:
            raw_text = header.inner_text()
            text = raw_text.strip().lower()
            header_texts.append(text)

        assert 'security definition' in header_texts, f'Expected "security definition" in headers, got: {header_texts}'
        assert 'patterns' in header_texts, f'Expected "patterns" in headers, got: {header_texts}'
        assert 'access type' in header_texts, f'Expected "access type" in headers, got: {header_texts}'

# ################################################################################################################################

    def test_create_one_publisher(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites via the UI ..
        sec_name = create_basic_auth(page, base_url, _Test_Name_Prefix, 'pub1')
        _ = create_topic(page, base_url, _Test_Name_Prefix + 'topic.', 'pub1')

        pattern_value = 'test.pub1.*'

        # .. create the permission ..
        _ = create_permission(page, base_url, sec_name, 'publisher', 'pub', pattern_value)

        # .. verify the new row appears with correct values.
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        row_text = row.inner_text()
        assert 'Publisher' in row_text, f'Expected "Publisher" in row, got: "{row_text}"'
        assert pattern_value in row_text, f'Expected pattern "{pattern_value}" in row, got: "{row_text}"'

# ################################################################################################################################

    def test_create_one_subscriber(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites via the UI ..
        sec_name = create_basic_auth(page, base_url, _Test_Name_Prefix, 'sub1')
        _ = create_topic(page, base_url, _Test_Name_Prefix + 'topic.', 'sub1')

        pattern_value = 'test.sub1.*'

        # .. create the permission ..
        _ = create_permission(page, base_url, sec_name, 'subscriber', 'sub', pattern_value)

        # .. verify the new row appears with correct values.
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        row_text = row.inner_text()
        assert 'Subscriber' in row_text, f'Expected "Subscriber" in row, got: "{row_text}"'
        assert pattern_value in row_text, f'Expected pattern "{pattern_value}" in row, got: "{row_text}"'

# ################################################################################################################################

    def test_create_publisher_and_subscriber(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites via the UI ..
        sec_name = create_basic_auth(page, base_url, _Test_Name_Prefix, 'pubsub1')
        _ = create_topic(page, base_url, _Test_Name_Prefix + 'topic.', 'pubsub1')

        pub_pattern = 'test.pubsub1.pub.*'
        sub_pattern = 'test.pubsub1.sub.*'

        # Navigate to the permissions page ..
        navigate_to_page(page, base_url, _Permission_Page_Url)

        # .. open the create dialog ..
        open_create_dialog_via_js(page, 'permission')

        # .. wait for the security definitions dropdown ..
        wait_for_sec_def_dropdown(page)

        # .. select the security definition ..
        page.select_option('#id_sec_base_id', label=sec_name)

        # .. set the access type to publisher-subscriber ..
        page.select_option('#id_access_type', value='publisher-subscriber')
        time.sleep(0.3)

        # .. set the first pattern row to pub ..
        page.select_option('#create-patterns-container .pattern-row:first-child .pattern-type-select', value='pub')
        page.fill('#create-patterns-container .pattern-row:first-child .pattern-input', pub_pattern)

        # .. add a second pattern row ..
        page.click('#create-patterns-container .pattern-row:first-child .pattern-add-button')
        time.sleep(0.2)

        # .. set the second (newly added, prepended to top) row to sub ..
        page.select_option('#create-patterns-container .pattern-row:first-child .pattern-type-select', value='sub')
        page.fill('#create-patterns-container .pattern-row:first-child .pattern-input', sub_pattern)

        # .. submit the form ..
        submit_create_form(page)

        # .. verify the new row appears with correct values.
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        row_text = row.inner_text()
        assert 'Publisher' in row_text, f'Expected "Publisher" in row, got: "{row_text}"'
        assert 'Subscriber' in row_text, f'Expected "Subscriber" in row, got: "{row_text}"'
        assert pub_pattern in row_text, f'Expected pub pattern "{pub_pattern}" in row, got: "{row_text}"'
        assert sub_pattern in row_text, f'Expected sub pattern "{sub_pattern}" in row, got: "{row_text}"'

# ################################################################################################################################

    def test_cancel_then_reopen_form_is_empty(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a sec def so the dropdown has something to select ..
        sec_name = create_basic_auth(page, base_url, _Test_Name_Prefix, 'cancel-reopen')

        # Navigate to the permissions page ..
        navigate_to_page(page, base_url, _Permission_Page_Url)

        # .. open the create dialog ..
        open_create_dialog_via_js(page, 'permission')

        # .. wait for the security definitions dropdown ..
        wait_for_sec_def_dropdown(page)

        # .. fill in the form fields ..
        page.select_option('#id_sec_base_id', label=sec_name)
        page.select_option('#id_access_type', value='publisher')
        time.sleep(0.2)
        page.fill('#create-patterns-container .pattern-row:first-child .pattern-input', 'test.cancel.*')

        # .. close the dialog ..
        close_dialog_via_jquery(page, 'create-div')

        # .. reopen the dialog ..
        open_create_dialog_via_js(page, 'permission')
        time.sleep(0.5)

        # .. verify the pattern input is empty.
        pattern_value = page.input_value('#create-patterns-container .pattern-row:first-child .pattern-input')
        assert pattern_value == '', f'Expected empty pattern, got: "{pattern_value}"'

# ################################################################################################################################

    def test_cancel_no_row_added(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a sec def ..
        sec_name = create_basic_auth(page, base_url, _Test_Name_Prefix, 'cancel-norow')

        # Navigate to the permissions page ..
        navigate_to_page(page, base_url, _Permission_Page_Url)

        # .. count rows before ..
        count_before = get_table_row_count(page)

        # .. open the create dialog ..
        open_create_dialog_via_js(page, 'permission')

        # .. wait for dropdown ..
        wait_for_sec_def_dropdown(page)

        # .. fill in fields ..
        page.select_option('#id_sec_base_id', label=sec_name)
        page.select_option('#id_access_type', value='publisher')
        time.sleep(0.2)
        page.fill('#create-patterns-container .pattern-row:first-child .pattern-input', 'test.norow.*')

        # .. close the dialog without submitting ..
        close_dialog_via_jquery(page, 'create-div')

        # .. verify row count is unchanged.
        count_after = get_table_row_count(page)

        assert count_after == count_before, \
            f'Expected {count_before} rows after cancel, got: {count_after}'

# ################################################################################################################################

    def test_add_and_remove_pattern_rows(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the permissions page ..
        navigate_to_page(page, base_url, _Permission_Page_Url)

        # .. open the create dialog ..
        open_create_dialog_via_js(page, 'permission')
        time.sleep(0.3)

        # .. set access type so pattern options are available ..
        page.select_option('#id_access_type', value='publisher-subscriber')
        time.sleep(0.2)

        # .. verify there is initially one pattern row ..
        rows = page.query_selector_all('#create-patterns-container .pattern-row')
        assert len(rows) == 1, f'Expected 1 initial pattern row, got: {len(rows)}'

        # .. click the + button to add a row ..
        page.click('#create-patterns-container .pattern-row:first-child .pattern-add-button')
        time.sleep(0.2)

        rows = page.query_selector_all('#create-patterns-container .pattern-row')
        assert len(rows) == 2, f'Expected 2 pattern rows after add, got: {len(rows)}'

        # .. add another row ..
        page.click('#create-patterns-container .pattern-row:first-child .pattern-add-button')
        time.sleep(0.2)

        rows = page.query_selector_all('#create-patterns-container .pattern-row')
        assert len(rows) == 3, f'Expected 3 pattern rows after second add, got: {len(rows)}'

        # .. click the - button on the first row to remove it ..
        page.click('#create-patterns-container .pattern-row:first-child .pattern-remove-button')
        time.sleep(0.2)

        rows = page.query_selector_all('#create-patterns-container .pattern-row')
        assert len(rows) == 2, f'Expected 2 pattern rows after remove, got: {len(rows)}'

# ################################################################################################################################

    def test_empty_pattern_rejected(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a sec def ..
        sec_name = create_basic_auth(page, base_url, _Test_Name_Prefix, 'empty-pat')

        # Navigate to the permissions page ..
        navigate_to_page(page, base_url, _Permission_Page_Url)

        # .. open the create dialog ..
        open_create_dialog_via_js(page, 'permission')

        # .. wait for the security definitions dropdown ..
        wait_for_sec_def_dropdown(page)

        # .. select the sec def and access type, but leave pattern empty ..
        page.select_option('#id_sec_base_id', label=sec_name)
        page.select_option('#id_access_type', value='publisher')
        time.sleep(0.2)

        # .. set up a listener for the alert dialog ..
        alert_messages = setup_alert_handler(page)

        # .. try to submit ..
        page.click('#create-div input[type="submit"]')
        time.sleep(1.0)

        # .. verify the alert about patterns was shown ..
        assert len(alert_messages) > 0, 'Expected an alert about empty pattern'
        assert 'pattern' in alert_messages[0].lower(), \
            f'Expected alert about pattern, got: "{alert_messages[0]}"'

        # .. verify the dialog is still open (submission was prevented).
        is_visible = page.is_visible('#create-div')
        assert is_visible, 'Expected create dialog to still be open after rejection'

# ################################################################################################################################

    def test_show_matches_wildcard(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create multiple topics that share a common prefix ..
        suffix = os.urandom(3).hex()
        topic_prefix = _Test_Name_Prefix + 'wc.' + suffix

        topic_name_1 = topic_prefix + '.orders'
        topic_name_2 = topic_prefix + '.invoices'
        topic_name_3 = topic_prefix + '.refunds'

        for topic_name in (topic_name_1, topic_name_2, topic_name_3):

            navigate_to_page(page, base_url, _Topic_Page_Url)

            open_create_dialog(page)

            page.fill('#id_name', topic_name)
            submit_create_form(page)

        # .. create a sec def ..
        sec_name = create_basic_auth(page, base_url, _Test_Name_Prefix, 'wc.' + suffix)

        # .. use a wildcard pattern that should match all 3 topics ..
        pattern_value = topic_prefix + '.*'

        # .. create the permission ..
        _ = create_permission(page, base_url, sec_name, 'publisher', 'pub', pattern_value)

        # .. reload the page so pattern tables are rendered ..
        navigate_to_page(page, base_url, _Permission_Page_Url)
        time.sleep(0.5)

        # .. find the "Show matches" link for our pattern ..
        link_selector = f'.pattern-link[data-pattern="pub={pattern_value}"]'
        show_matches_link = page.wait_for_selector(link_selector, state='visible', timeout=5000)

        # .. click it ..
        show_matches_link.click()

        # .. wait for the popup dialog to appear ..
        page.wait_for_selector('[id^="topic-matches-popup-"]', state='visible', timeout=10000)

        # .. wait for loading to finish ..
        page.wait_for_function(
            '''() => {
                let popup = document.querySelector("[id^='topic-matches-popup-']");
                if (!popup) return false;
                let content = popup.querySelector(".topic-popup-content");
                if (!content) return false;
                return content.textContent.indexOf("Loading") === -1 && content.textContent.trim().length > 0;
            }''',
            timeout=10000
        )

        # .. verify the popup shows all 3 matching topics.
        popup = page.query_selector('[id^="topic-matches-popup-"]')
        popup_text = popup.inner_text()

        assert topic_name_1 in popup_text, \
            f'Expected "{topic_name_1}" in popup, got: "{popup_text}"'
        assert topic_name_2 in popup_text, \
            f'Expected "{topic_name_2}" in popup, got: "{popup_text}"'
        assert topic_name_3 in popup_text, \
            f'Expected "{topic_name_3}" in popup, got: "{popup_text}"'

        # .. verify the count header shows 3 matches.
        assert '3 match' in popup_text, f'Expected "3 match" in popup, got: "{popup_text}"'

# ################################################################################################################################

    def test_show_matches_no_results(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a sec def ..
        sec_name = create_basic_auth(page, base_url, _Test_Name_Prefix, 'no-match')

        # .. create a permission with a pattern that matches nothing ..
        pattern_value = 'nonexistent.topic.that.will.never.match'
        _ = create_permission(page, base_url, sec_name, 'publisher', 'pub', pattern_value)

        # .. reload the page ..
        navigate_to_page(page, base_url, _Permission_Page_Url)
        time.sleep(0.5)

        # .. find the "Show matches" link ..
        link_selector = f'.pattern-link[data-pattern="pub={pattern_value}"]'
        show_matches_link = page.wait_for_selector(link_selector, state='visible', timeout=5000)

        # .. click it ..
        show_matches_link.click()

        # .. wait for the popup ..
        page.wait_for_selector('[id^="topic-matches-popup-"]', state='visible', timeout=10000)

        # .. wait for loading to finish ..
        page.wait_for_function(
            '''() => {
                let popup = document.querySelector("[id^='topic-matches-popup-']");
                if (!popup) return false;
                let content = popup.querySelector(".topic-popup-content");
                if (!content) return false;
                return content.textContent.indexOf("Loading") === -1 && content.textContent.trim().length > 0;
            }''',
            timeout=10000
        )

        # .. verify the popup shows "No matching topics found".
        popup = page.query_selector('[id^="topic-matches-popup-"]')
        popup_text = popup.inner_text()
        assert 'No matching topics' in popup_text, \
            f'Expected "No matching topics" in popup, got: "{popup_text}"'

# ################################################################################################################################
# ################################################################################################################################
