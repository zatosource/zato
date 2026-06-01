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

_Topic_Page_Url = '/zato/pubsub/topic/?cluster=1'

_Test_Name_Prefix = 'test.pub.' + os.urandom(4).hex() + '.'

# ################################################################################################################################
# ################################################################################################################################

def _create_topic(page:'Page', base_url:'str', suffix:'str') -> 'dict':
    """ Creates a pub/sub topic via the UI and returns its name and item_id.
    """

    name = _Test_Name_Prefix + suffix

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

    # .. wait for the row to appear ..
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=5000)

    # .. extract the item_id.
    row = page.query_selector(row_selector)
    id_cell = row.query_selector('td[class*="item_id_"]')
    item_id = id_cell.inner_text().strip()

    out = {
        'name': name,
        'item_id': item_id,
    }

    return out

# ################################################################################################################################

def _open_publish_overlay(page:'Page', item_id:'str') -> 'None':
    """ Opens the publish invoker overlay for a given topic item_id.
    """

    # Call the JS function to open the overlay ..
    page.evaluate(f'$.fn.zato.pubsub.topic.publishMessage("{item_id}")')

    # .. and wait for it to become visible.
    page.wait_for_selector('#invoker-modal-overlay:not(.hidden)', state='visible', timeout=5000)

# ################################################################################################################################

def _publish_via_overlay(page:'Page', payload:'str') -> 'None':
    """ Types a payload into the request pane and clicks Publish, then waits for the response.
    """

    # Set the request pane content ..
    escaped = payload.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n')
    page.evaluate(f"$.fn.zato.invoker._request_pane.setValue('{escaped}')")

    # .. click the Publish button ..
    page.click('#invoker-modal-invoke-button')

    # .. wait for the status line to show a result (not "Invoking...").
    page.wait_for_function(
        '''() => {
            let status = document.querySelector("#invoker-modal-status");
            if (!status) return false;
            let text = status.textContent;
            return text && text.indexOf("Invoking") === -1 && text.trim().length > 0;
        }''',
        timeout=15000
    )

# ################################################################################################################################

def _open_history_panel(page:'Page') -> 'None':
    """ Opens the invoker history overlay panel.
    """

    # Click the history button ..
    page.click('#invoker-modal-history-button')

    # .. and wait for the history overlay to become visible.
    page.wait_for_selector('#invoker-modal-history-overlay:not(.hidden)', state='visible', timeout=5000)

# ################################################################################################################################
# ################################################################################################################################

class TestPubSubTopicPublish:
    """ Tests for the invoker overlay that publishes messages to pub/sub topics.
    """

    def test_overlay_opens_with_topic_name(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a topic ..
        topic = _create_topic(page, base_url, 'overlay-open')

        # .. open the publish overlay ..
        _open_publish_overlay(page, topic['item_id'])

        # .. verify the title contains the topic name ..
        title_text = page.inner_text('#invoker-modal-title')
        assert 'Publish a message' in title_text, f'Expected "Publish a message" in title, got: "{title_text}"'
        assert topic['name'] in title_text, f'Expected topic name "{topic["name"]}" in title, got: "{title_text}"'

        # .. verify the Publish button is present.
        button_text = page.inner_text('#invoker-modal-invoke-button')
        button_lower = button_text.lower()
        assert 'publish' in button_lower, f'Expected "publish" on button, got: "{button_text}"'

# ################################################################################################################################

    def test_overlay_closes_on_x(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a topic and open the overlay ..
        topic = _create_topic(page, base_url, 'close-x')
        _open_publish_overlay(page, topic['item_id'])

        # .. click the close button ..
        page.click('#invoker-modal-close')
        time.sleep(0.3)

        # .. verify the overlay is hidden.
        is_hidden = page.evaluate('document.querySelector("#invoker-modal-overlay").classList.contains("hidden")')
        assert is_hidden, 'Overlay should be hidden after clicking X'

# ################################################################################################################################

    def test_overlay_closes_on_escape(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a topic and open the overlay ..
        topic = _create_topic(page, base_url, 'close-esc')
        _open_publish_overlay(page, topic['item_id'])

        # .. press Escape ..
        page.keyboard.press('Escape')
        time.sleep(0.3)

        # .. verify the overlay is hidden.
        is_hidden = page.evaluate('document.querySelector("#invoker-modal-overlay").classList.contains("hidden")')
        assert is_hidden, 'Overlay should be hidden after pressing Escape'

# ################################################################################################################################

    def test_overlay_closes_on_backdrop_click(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a topic and open the overlay ..
        topic = _create_topic(page, base_url, 'close-backdrop')
        _open_publish_overlay(page, topic['item_id'])

        # .. click the backdrop area via JS (backdrop is behind the content div) ..
        page.evaluate('$(".invoker-modal-backdrop").trigger("click")')
        time.sleep(0.3)

        # .. verify the overlay is hidden.
        is_hidden = page.evaluate('document.querySelector("#invoker-modal-overlay").classList.contains("hidden")')
        assert is_hidden, 'Overlay should be hidden after clicking backdrop'

# ################################################################################################################################

    def test_request_editor_empty_on_first_open(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a fresh topic that has never been published to ..
        topic = _create_topic(page, base_url, 'editor-empty')

        # .. clear any localStorage state for this topic ..
        page.evaluate(f'''
            localStorage.removeItem("zato.pubsub.topic.publish.{topic['item_id']}");
            localStorage.removeItem("zato_invoker_state_zato.pubsub.topic.publish.{topic['item_id']}");
        ''')

        # .. open the overlay ..
        _open_publish_overlay(page, topic['item_id'])

        # .. verify the ACE editor content is empty.
        editor_value = page.evaluate('$.fn.zato.invoker._request_pane.getValue()')
        assert editor_value.strip() == '', f'Expected empty editor, got: "{editor_value}"'

# ################################################################################################################################

    def test_history_records_request_after_publish(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a topic and open the overlay ..
        topic = _create_topic(page, base_url, 'hist-req')
        _open_publish_overlay(page, topic['item_id'])

        # .. publish a message ..
        payload = '{"history":"request-test"}'
        _publish_via_overlay(page, payload)

        # .. open the history panel ..
        _open_history_panel(page)

        # .. verify the request text appears in history ..
        items = page.query_selector_all('#invoker-modal-history-list .invoker-history-item-wrapper')
        assert len(items) > 0, 'Expected at least one history entry'

        first_text = page.inner_text('#invoker-modal-history-list .invoker-history-item-wrapper:first-child .invoker-history-item-text')
        assert 'history' in first_text, f'Expected request payload in history, got: "{first_text}"'

        # .. verify a timestamp is present.
        first_timestamp = page.inner_text('#invoker-modal-history-list .invoker-history-item-wrapper:first-child .invoker-history-item-timestamp')
        assert first_timestamp.strip() != '', 'Expected a timestamp on the history entry'

# ################################################################################################################################

    def test_history_records_response(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a topic and open the overlay ..
        topic = _create_topic(page, base_url, 'hist-resp')
        _open_publish_overlay(page, topic['item_id'])

        # .. publish a message ..
        _publish_via_overlay(page, '{"history":"response-test"}')

        # .. open the history panel ..
        _open_history_panel(page)

        # .. click "Show response" on the first entry ..
        show_response = page.query_selector(
            '#invoker-modal-history-list .invoker-history-item-wrapper:first-child .invoker-history-item-show-response')
        show_response.click()
        time.sleep(0.3)

        # .. verify the response detail is visible and contains msg_id.
        response_detail = page.query_selector('.invoker-history-response-detail.visible')
        assert response_detail is not None, 'Expected response detail to be visible'

        response_text = response_detail.inner_text()
        assert 'msg_id' in response_text, f'Expected "msg_id" in response detail, got: "{response_text}"'

# ################################################################################################################################

    def test_multiple_publishes_in_history_order(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a topic and open the overlay ..
        topic = _create_topic(page, base_url, 'hist-order')
        _open_publish_overlay(page, topic['item_id'])

        # .. publish 3 messages with distinct payloads ..
        payloads = ['{"order":"first"}', '{"order":"second"}', '{"order":"third"}']

        for payload in payloads:
            _publish_via_overlay(page, payload)

        # .. open the history panel ..
        _open_history_panel(page)

        # .. collect all history item texts ..
        items = page.query_selector_all('#invoker-modal-history-list .invoker-history-item-wrapper .invoker-history-item-text')
        texts = [] # type: list

        for item in items:
            texts.append(item.inner_text())

        # .. verify all 3 appear and newest is first.
        # Each publish creates 2 history entries (pre-invoke and post-success),
        # so we check every other item.
        assert len(texts) >= 6, f'Expected at least 6 history entries (2 per publish), got {len(texts)}'
        assert 'third' in texts[0], f'Expected newest ("third") first, got: "{texts[0]}"'
        assert 'second' in texts[2], f'Expected "second" at index 2, got: "{texts[2]}"'
        assert 'first' in texts[4], f'Expected oldest ("first") at index 4, got: "{texts[4]}"'

# ################################################################################################################################

    def test_history_search_filters_entries(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a topic and open the overlay ..
        topic = _create_topic(page, base_url, 'hist-search')
        _open_publish_overlay(page, topic['item_id'])

        # .. publish messages with different payloads ..
        _publish_via_overlay(page, '{"fruit":"apple"}')
        _publish_via_overlay(page, '{"fruit":"banana"}')
        _publish_via_overlay(page, '{"fruit":"cherry"}')

        # .. open the history panel ..
        _open_history_panel(page)

        # .. type a search term that matches only one ..
        page.fill('#invoker-modal-history-search', 'banana')
        time.sleep(0.5)

        # .. verify only matching entries are shown.
        # Each publish creates 2 history entries, so "banana" appears twice.
        visible_items = page.query_selector_all('#invoker-modal-history-list .invoker-history-item-wrapper')
        assert len(visible_items) == 2, f'Expected 2 filtered results (2 per publish), got {len(visible_items)}'

        filtered_text = visible_items[0].inner_text()
        assert 'banana' in filtered_text, f'Expected "banana" in filtered entry, got: "{filtered_text}"'

# ################################################################################################################################

    def test_history_item_click_restores_request(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a topic and open the overlay ..
        topic = _create_topic(page, base_url, 'hist-restore')
        _open_publish_overlay(page, topic['item_id'])

        # .. publish a message ..
        original_payload = '{"restore":"this-payload"}'
        _publish_via_overlay(page, original_payload)

        # .. clear the editor ..
        page.evaluate("$.fn.zato.invoker._request_pane.setValue('')")

        # .. open history and click the entry ..
        _open_history_panel(page)

        first_text_elem = page.query_selector(
            '#invoker-modal-history-list .invoker-history-item-wrapper:first-child .invoker-history-item-text')
        first_text_elem.click()
        time.sleep(0.3)

        # .. verify the editor is populated with the original payload.
        editor_value = page.evaluate('$.fn.zato.invoker._request_pane.getValue()')
        assert 'restore' in editor_value, f'Expected restored payload in editor, got: "{editor_value}"'

# ################################################################################################################################

    def test_history_persists_across_overlay_reopen(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a topic and open the overlay ..
        topic = _create_topic(page, base_url, 'hist-persist')
        _open_publish_overlay(page, topic['item_id'])

        # .. publish a message ..
        _publish_via_overlay(page, '{"persist":"across-reopen"}')

        # .. close the overlay ..
        page.click('#invoker-modal-close')
        time.sleep(0.3)

        # .. reopen the overlay for the same topic ..
        _open_publish_overlay(page, topic['item_id'])

        # .. open history ..
        _open_history_panel(page)

        # .. verify the previous entry is still there.
        items = page.query_selector_all('#invoker-modal-history-list .invoker-history-item-wrapper')
        assert len(items) > 0, 'Expected history entries after reopen'

        first_text = page.inner_text(
            '#invoker-modal-history-list .invoker-history-item-wrapper:first-child .invoker-history-item-text')
        assert 'persist' in first_text, f'Expected persisted payload in history, got: "{first_text}"'

# ################################################################################################################################
# ################################################################################################################################
