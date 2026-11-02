# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import choose_subscriber_kind, close_dialog_via_jquery, \
    create_all_subscription_prerequisites, create_outgoing_rest, create_pull_subscription, create_push_rest_subscription, \
    get_subscription_topic_selectors, get_subscription_topics_area, get_table_row_count, navigate_to_page, \
    open_subscription_create_dialog, pick_subscription_topic, select_subscription_create_option, \
    subscription_create_field_selector, unpick_subscription_topic
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_Subscription_Page_Url = '/zato/pubsub/subscription/'

_Test_Name_Prefix = 'test.sub.' + CryptoManager.generate_hex_string(32) + '.'

_No_Client_Text = 'No API client selected'

_Services_Selector = '#pubsub-subscription-create-subscriber .pubsub-subscription-create-services'
_Submit_Selector   = '#pubsub-subscription-create-submit'

_Attention_Class = 'zato-validator-attention'

_Kind_Client  = 'client'
_Kind_Service = 'service'

_Delivery_Pull = 'pull'
_Delivery_Push = 'push'

# How long a request of the Dashboard may take, in milliseconds
_Timeout = 10000

# ################################################################################################################################
# ################################################################################################################################

def _client_row_selector(sec_name:'str') -> 'str':
    out = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
    return out

# ################################################################################################################################

def _has_attention(page:'Page', selector:'str') -> 'bool':
    """ Tells whether the form points to the element as a missing part of a submission.
    """
    class_names = page.get_attribute(selector, 'class')

    if class_names is None:
        return False

    out = _Attention_Class in class_names
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestPubSubSubscriptionCreate:
    """ Tests for the pub/sub subscription create flow, an API client as the subscriber.
    """

    def test_page_loads(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the subscriptions page ..
        navigate_to_page(page, base_url, _Subscription_Page_Url)

        # .. verify the page heading ..
        heading = cast_('any_', page.query_selector('h2.zato'))
        heading_text = heading.inner_text()
        heading_lower = heading_text.lower()
        assert 'pub/sub' in heading_lower and 'subscriptions' in heading_lower, \
            f'Expected the pub/sub subscriptions heading, got: {heading_text}'

        # .. verify the create link is present ..
        create_link = cast_('any_', page.query_selector('#markup .page_prompt a'))
        create_link_text = create_link.inner_text()
        assert 'Create a new pub/sub subscription' in create_link_text, \
            f'Expected create link text, got: {create_link_text}'

        # .. verify table headers.
        headers = page.query_selector_all('#data-table thead th')

        header_texts = [] # type: list

        for header in headers:
            raw_text = header.inner_text()
            text = raw_text.strip().lower()
            header_texts.append(text)

        assert 'security definition' in header_texts, f'Expected "security definition" in headers, got: {header_texts}'
        assert 'sub key' in header_texts, f'Expected "sub key" in headers, got: {header_texts}'

# ################################################################################################################################

    def test_create_pull_subscription(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites via the UI ..
        prereqs = create_all_subscription_prerequisites(page, base_url, _Test_Name_Prefix, 'pull1')

        sec_name = prereqs['sec_name']
        topic_name = prereqs['topic_name']

        # .. create a pull subscription ..
        create_pull_subscription(page, base_url, sec_name, topic_name)

        # .. and verify the new row appears with correct values.
        row = cast_('any_', page.wait_for_selector(_client_row_selector(sec_name), state='visible', timeout=_Timeout))

        row_text = row.inner_text()
        assert 'Pull' in row_text, f'Expected "Pull" in row, got: "{row_text}"'
        assert topic_name in row_text, f'Expected topic "{topic_name}" in row, got: "{row_text}"'

# ################################################################################################################################

    def test_create_push_rest_subscription(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites via the UI ..
        prereqs = create_all_subscription_prerequisites(page, base_url, _Test_Name_Prefix, 'push-rest1')

        sec_name = prereqs['sec_name']
        topic_name = prereqs['topic_name']

        # .. create an outgoing REST connection ..
        rest_name = create_outgoing_rest(page, base_url, _Test_Name_Prefix, 'push-rest1')

        # .. create a push subscription to it ..
        create_push_rest_subscription(page, base_url, sec_name, topic_name, rest_name)

        # .. and verify the new row appears with correct values.
        row = cast_('any_', page.wait_for_selector(_client_row_selector(sec_name), state='visible', timeout=_Timeout))

        row_text = row.inner_text()
        assert 'Push' in row_text, f'Expected "Push" in row, got: "{row_text}"'
        assert rest_name in row_text, f'Expected REST endpoint "{rest_name}" in row, got: "{row_text}"'

# ################################################################################################################################

    def test_cancel_then_reopen_form_is_empty(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        prereqs = create_all_subscription_prerequisites(page, base_url, _Test_Name_Prefix, 'cancel-reopen')
        sec_name = prereqs['sec_name']

        # .. open the subscription create dialog and select the client ..
        open_subscription_create_dialog(page, base_url)
        select_subscription_create_option(page, 'client', sec_name)

        # .. close the dialog ..
        close_dialog_via_jquery(page, 'create-div')

        # .. reopen the dialog ..
        open_subscription_create_dialog(page, base_url)

        # .. verify no client is selected and the topics area says so.
        client_value = page.input_value(subscription_create_field_selector('client'))
        assert client_value == '', f'Expected no client selected, got: "{client_value}"'

        topic_area_text = page.inner_text(get_subscription_topics_area(page))
        assert _No_Client_Text in topic_area_text, f'Expected placeholder text, got: "{topic_area_text}"'

# ################################################################################################################################

    def test_cancel_no_row_added(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        prereqs = create_all_subscription_prerequisites(page, base_url, _Test_Name_Prefix, 'cancel-norow')
        sec_name = prereqs['sec_name']
        topic_name = prereqs['topic_name']

        # .. open the create dialog, counting the rows before ..
        open_subscription_create_dialog(page, base_url)
        count_before = get_table_row_count(page)

        # .. select the client and the topic ..
        select_subscription_create_option(page, 'client', sec_name)
        pick_subscription_topic(page, topic_name)

        # .. close the dialog without submitting ..
        close_dialog_via_jquery(page, 'create-div')

        # .. verify row count is unchanged.
        count_after = get_table_row_count(page)

        assert count_after == count_before, \
            f'Expected {count_before} rows after cancel, got: {count_after}'

# ################################################################################################################################

    def test_client_selection_shows_its_topics(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        prereqs = create_all_subscription_prerequisites(page, base_url, _Test_Name_Prefix, 'sec-loads')
        sec_name = prereqs['sec_name']
        topic_name = prereqs['topic_name']

        # .. open the subscription create dialog ..
        open_subscription_create_dialog(page, base_url)

        # .. verify the placeholder is shown before selecting a client ..
        topic_area_text = page.inner_text(get_subscription_topics_area(page))
        assert _No_Client_Text in topic_area_text, \
            f'Expected placeholder before client selection, got: "{topic_area_text}"'

        # .. select the client ..
        select_subscription_create_option(page, 'client', sec_name)

        # .. and verify its only topic is shown, already picked.
        _, on_selector = get_subscription_topic_selectors(page, topic_name)
        picked = page.query_selector(on_selector)
        assert picked, f'Expected the only topic "{topic_name}" of the client to be picked'

# ################################################################################################################################

    def test_delivery_type_toggle_shows_push_fields(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        endpoint_selector = subscription_create_field_selector('endpoint')
        delivery_selector = subscription_create_field_selector('delivery')

        # .. open the subscription create dialog ..
        open_subscription_create_dialog(page, base_url)

        # .. verify the REST endpoint field is absent when Pull is selected ..
        delivery_value = page.input_value(delivery_selector)
        assert delivery_value == _Delivery_Pull, f'Expected pull delivery by default, got: "{delivery_value}"'

        endpoint = page.query_selector(endpoint_selector)
        assert endpoint is None, 'REST endpoint should be absent when Pull selected'

        # .. switch to push ..
        _ = page.select_option(delivery_selector, value=_Delivery_Push)

        # .. verify the REST endpoint field appears ..
        _ = page.wait_for_selector(endpoint_selector, state='visible', timeout=_Timeout)

        # .. and goes away again with pull.
        _ = page.select_option(delivery_selector, value=_Delivery_Pull)
        _ = page.wait_for_selector(endpoint_selector, state='detached', timeout=_Timeout)

# ################################################################################################################################

    def test_subscriber_kind_toggle_shows_correct_fields(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        client_selector = subscription_create_field_selector('client')
        delivery_selector = subscription_create_field_selector('delivery')

        # .. open the subscription create dialog, an API client being the subscriber at first ..
        open_subscription_create_dialog(page, base_url)

        assert page.is_visible(client_selector), 'API client should be visible for an API client subscriber'
        assert page.is_visible(delivery_selector), 'Delivery should be visible for an API client subscriber'
        assert page.query_selector(_Services_Selector) is None, 'Services should be absent for an API client subscriber'

        # .. switch to a service ..
        choose_subscriber_kind(page, _Kind_Service)

        # .. verify the services are visible and the fields of a client are gone ..
        assert page.is_visible(_Services_Selector), 'Services should be visible for a service subscriber'
        assert page.query_selector(client_selector) is None, 'API client should be absent for a service subscriber'
        assert page.query_selector(delivery_selector) is None, 'Delivery should be absent for a service subscriber'

        # .. and switch back.
        choose_subscriber_kind(page, _Kind_Client)
        assert page.query_selector(_Services_Selector) is None, 'Services should be absent once switched back'

# ################################################################################################################################

    def test_no_client_selected_shows_placeholder(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # .. open the subscription create dialog ..
        open_subscription_create_dialog(page, base_url)

        # .. verify the topics area shows the placeholder message.
        topic_area_text = page.inner_text(get_subscription_topics_area(page))
        assert _No_Client_Text in topic_area_text, f'Expected placeholder text, got: "{topic_area_text}"'

# ################################################################################################################################

    def test_no_client_selected_prevents_submit(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # .. open the subscription create dialog and submit it as it is ..
        open_subscription_create_dialog(page, base_url)
        page.click(_Submit_Selector)

        # .. verify the form points to the client ..
        client_selector = subscription_create_field_selector('client')
        assert _has_attention(page, client_selector), 'Expected the API client to be pointed to as missing'

        # .. and the dialog is still open.
        time.sleep(0.5)
        assert page.is_visible('#create-div'), 'Expected create dialog to still be open after rejection'

# ################################################################################################################################

    def test_no_topics_picked_prevents_submit(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        prereqs = create_all_subscription_prerequisites(page, base_url, _Test_Name_Prefix, 'no-topic')
        sec_name = prereqs['sec_name']
        topic_name = prereqs['topic_name']

        # .. open the subscription create dialog and select the client ..
        open_subscription_create_dialog(page, base_url)
        select_subscription_create_option(page, 'client', sec_name)

        # .. let go of its only topic, which the form picks on its own ..
        unpick_subscription_topic(page, topic_name)

        # .. try to submit ..
        page.click(_Submit_Selector)

        # .. verify the form points to the topics ..
        topics_area = get_subscription_topics_area(page)
        assert _has_attention(page, topics_area), 'Expected the topics to be pointed to as missing'

        # .. and the dialog is still open.
        time.sleep(0.5)
        assert page.is_visible('#create-div'), 'Expected create dialog to still be open after rejection'

# ################################################################################################################################

    def test_sub_key_displayed(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites and a pull subscription ..
        prereqs = create_all_subscription_prerequisites(page, base_url, _Test_Name_Prefix, 'subkey')
        sec_name = prereqs['sec_name']
        topic_name = prereqs['topic_name']

        create_pull_subscription(page, base_url, sec_name, topic_name)

        # .. verify the sub_key span is present in the row.
        row = cast_('any_', page.wait_for_selector(_client_row_selector(sec_name), state='visible', timeout=_Timeout))

        sub_key_span = row.query_selector('.ps-sub-key')
        assert sub_key_span, 'Expected sub_key span to be present in the row'

        sub_key_text = sub_key_span.get_attribute('data-sub-key')
        assert sub_key_text, 'Expected sub_key data attribute to be non-empty'
        assert sub_key_text.startswith('sk'), f'Expected sub_key to start with "sk", got: "{sub_key_text}"'

# ################################################################################################################################

    def test_pending_messages_link_navigates_to_queue(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites and a pull subscription ..
        prereqs = create_all_subscription_prerequisites(page, base_url, _Test_Name_Prefix, 'pending')
        sec_name = prereqs['sec_name']
        topic_name = prereqs['topic_name']

        create_pull_subscription(page, base_url, sec_name, topic_name)

        # .. find the row and click the pending messages link ..
        row = cast_('any_', page.wait_for_selector(_client_row_selector(sec_name), state='visible', timeout=_Timeout))

        # .. the pending messages link is the last visible <a> with an href to the queue page ..
        pending_link = row.query_selector('td a[href*="pubsub/subscription/queue"]')
        assert pending_link, 'Expected pending messages link in the row'

        # .. click the link ..
        pending_link.click()
        page.wait_for_load_state('networkidle')

        # .. verify we navigated to the queue browser page.
        current_url = page.url
        assert 'pubsub/subscription/queue' in current_url, \
            f'Expected queue browser URL, got: "{current_url}"'

# ################################################################################################################################

    def test_import_demo_config(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        _demo_sec_name = 'demo_pubsub.subscriber'

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the subscriptions page ..
        navigate_to_page(page, base_url, _Subscription_Page_Url)

        # .. delete any pre-existing demo subscription so the import has something to create ..
        demo_row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{_demo_sec_name}")))'
        demo_row = page.query_selector(demo_row_selector)

        if demo_row:

            # .. accept the confirmation dialog that the delete will trigger ..
            page.once('dialog', lambda dialog: dialog.accept())

            # .. click the Delete link in that row ..
            delete_link = cast_('any_', demo_row.query_selector('a:text-is("Delete")'))
            delete_link.click()
            time.sleep(1.0)

            # .. reload and confirm the row is gone ..
            navigate_to_page(page, base_url, _Subscription_Page_Url)

            gone = page.query_selector(demo_row_selector)
            assert gone is None, 'Expected demo subscription row to be deleted but it is still present'

        # .. click "Import demo config" ..
        page.click('a:text-is("Import demo config")')
        page.wait_for_load_state('networkidle')
        time.sleep(5.0)

        # .. reload to see updated data ..
        navigate_to_page(page, base_url, _Subscription_Page_Url)

        # .. verify the demo subscription was re-created.
        imported_row = page.query_selector(demo_row_selector)
        assert imported_row, f'Expected demo subscription row for "{_demo_sec_name}" after import'

# ################################################################################################################################
# ################################################################################################################################
