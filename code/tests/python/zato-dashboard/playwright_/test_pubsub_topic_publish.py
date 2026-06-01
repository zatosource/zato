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
# ################################################################################################################################
