# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import close_dialog_via_jquery, create_pull_subscription, \
    create_push_rest_subscription, create_service_subscription, open_subscription_create_dialog, pick_subscription_topic, \
    select_subscription_create_option, submit_subscription_create_dialog, subscription_create_field_selector

# Zato - test helpers
from http_test_server import HTTPTestServer
from pubsub_subscription_live import count_rows, delete_subscription, delete_topic, get_row_text, has_request_with_marker, \
    has_service_received, import_client_objects, import_topics, is_edit_topic_on, new_marker, No_Delivery_Wait, \
    open_subscription_edit, open_subscription_page, publish_to_topic, set_edit_delivery_active, set_edit_pull, \
    set_edit_push_rest, set_edit_topic, submit_subscription_edit, Timeout, wait_for_pending_count, wait_for_rest_delivery, \
    wait_for_row, wait_for_service_delivery

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, anytuple

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.sub.lifecycle.' + CryptoManager.generate_hex_string(16) + '.'

_Service_Delivery = 'test.pubsub.dashboard-service-subscriber.delivery'

_No_Topics_Alert = 'At least one topic is required'

_Delivery_Disabled_Class = 'ps-badge-deliv-disabled'
_Delivery_Enabled_Class  = 'ps-badge-deliv-enabled'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def rest_receivers() -> 'any_':
    """ Two live HTTP servers that record what the REST push subscriptions deliver to them.
    """
    first = HTTPTestServer()
    second = HTTPTestServer()

    first.start()
    second.start()

    yield first, second

    first.stop()
    second.stop()

# ################################################################################################################################
# ################################################################################################################################

def _client_names(suffix:'str') -> 'anytuple':
    """ Returns the names of an API client and of two topics, unique to one test.
    """
    base = _Test_Name_Prefix + suffix + '.'

    sec_name = base + 'client'
    first_topic = base + 'topic.first'
    second_topic = base + 'topic.second'

    out = sec_name, first_topic, second_topic
    return out

# ################################################################################################################################

def _endpoint_name(suffix:'str', role:'str') -> 'str':
    out = _Test_Name_Prefix + suffix + '.endpoint.' + role
    return out

# ################################################################################################################################

def _row_html(page:'Page', subscriber_name:'str') -> 'str':
    row = wait_for_row(page, subscriber_name)

    out = row.inner_html()
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestPubSubSubscriptionLifecycle:
    """ Subscriptions created, edited and deleted in the Dashboard, each step checked by publishing messages to them.
    """

    def test_pull_subscription_receives_and_follows_topic_edits(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        ) -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        sec_name, first_topic, second_topic = _client_names('pull-topics')
        import_client_objects(zato_dashboard, sec_name, [first_topic, second_topic], {})

        # Subscribe the client to the first topic ..
        create_pull_subscription(page, base_url, sec_name, first_topic)

        row_text = get_row_text(page, base_url, sec_name)
        assert 'Pull' in row_text, f'Expected "Pull" in the row, got: "{row_text}"'
        assert first_topic in row_text, f'Expected {first_topic} in the row, got: "{row_text}"'
        assert second_topic not in row_text, f'Expected no {second_topic} in the row, got: "{row_text}"'

        # .. a message published to it waits in the client's queue ..
        publish_to_topic(page, base_url, first_topic, new_marker())
        wait_for_pending_count(page, base_url, sec_name, 1)

        # .. the edit form shows the subscribed topic checked and the other one not ..
        open_subscription_edit(page, base_url, sec_name)

        assert is_edit_topic_on(page, first_topic), f'Expected {first_topic} to be checked'
        assert not is_edit_topic_on(page, second_topic), f'Expected {second_topic} not to be checked'

        # .. the second topic is added ..
        set_edit_topic(page, second_topic, True)
        submit_subscription_edit(page)

        row_text = get_row_text(page, base_url, sec_name)
        assert first_topic in row_text, f'Expected {first_topic} in the row, got: "{row_text}"'
        assert second_topic in row_text, f'Expected {second_topic} in the row, got: "{row_text}"'
        assert count_rows(page, sec_name) == 1

        # .. and its messages reach the same queue ..
        publish_to_topic(page, base_url, second_topic, new_marker())
        wait_for_pending_count(page, base_url, sec_name, 2)

        # .. after which the first topic is removed.
        open_subscription_edit(page, base_url, sec_name)
        set_edit_topic(page, first_topic, False)
        submit_subscription_edit(page)

        row_text = get_row_text(page, base_url, sec_name)
        assert first_topic not in row_text, f'Expected no {first_topic} in the row, got: "{row_text}"'
        assert second_topic in row_text, f'Expected {second_topic} in the row, got: "{row_text}"'

# ################################################################################################################################

    def test_pull_switched_to_push_and_back(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rest_receivers:'anytuple',
        ) -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        receiver, _ = rest_receivers

        sec_name, topic_name, _ = _client_names('pull-push')
        endpoint_name = _endpoint_name('pull-push', 'first')
        import_client_objects(zato_dashboard, sec_name, [topic_name], {endpoint_name: receiver.address})

        # Subscribe the client with pull delivery ..
        create_pull_subscription(page, base_url, sec_name, topic_name)

        # .. switch it to push delivery to the REST endpoint ..
        open_subscription_edit(page, base_url, sec_name)
        set_edit_push_rest(page, endpoint_name)
        submit_subscription_edit(page)

        # .. the row shows the endpoint at once and after a reload ..
        row = wait_for_row(page, sec_name)
        row_text = row.inner_text()
        assert endpoint_name in row_text, f'Expected {endpoint_name} in the row before a reload, got: "{row_text}"'

        row_text = get_row_text(page, base_url, sec_name)
        assert 'Push' in row_text, f'Expected "Push" in the row, got: "{row_text}"'
        assert endpoint_name in row_text, f'Expected {endpoint_name} in the row, got: "{row_text}"'

        # .. a message published now is pushed to the endpoint ..
        pushed_marker = new_marker()
        publish_to_topic(page, base_url, topic_name, pushed_marker)
        wait_for_rest_delivery(receiver, pushed_marker)

        # .. the subscription goes back to pull delivery ..
        open_subscription_edit(page, base_url, sec_name)
        set_edit_pull(page)
        submit_subscription_edit(page)

        row_text = get_row_text(page, base_url, sec_name)
        assert 'Pull' in row_text, f'Expected "Pull" in the row, got: "{row_text}"'
        assert endpoint_name not in row_text, f'Expected no {endpoint_name} in the row, got: "{row_text}"'

        # .. and the next message waits in the queue instead of being pushed.
        pulled_marker = new_marker()
        publish_to_topic(page, base_url, topic_name, pulled_marker)
        wait_for_pending_count(page, base_url, sec_name, 1)

        time.sleep(No_Delivery_Wait)
        assert not has_request_with_marker(receiver.recorded_requests, pulled_marker), \
            'Expected the message published after the switch to pull not to be pushed'

# ################################################################################################################################

    def test_push_endpoint_changed(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rest_receivers:'anytuple',
        ) -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        first_receiver, second_receiver = rest_receivers

        sec_name, topic_name, _ = _client_names('endpoint-change')
        first_endpoint = _endpoint_name('endpoint-change', 'first')
        second_endpoint = _endpoint_name('endpoint-change', 'second')

        endpoints = {
            first_endpoint: first_receiver.address,
            second_endpoint: second_receiver.address,
        }

        import_client_objects(zato_dashboard, sec_name, [topic_name], endpoints)

        # Subscribe the client with push delivery to the first endpoint ..
        create_push_rest_subscription(page, base_url, sec_name, topic_name, first_endpoint)

        first_marker = new_marker()
        publish_to_topic(page, base_url, topic_name, first_marker)
        wait_for_rest_delivery(first_receiver, first_marker)

        # .. point it to the second endpoint ..
        open_subscription_edit(page, base_url, sec_name)
        set_edit_push_rest(page, second_endpoint)
        submit_subscription_edit(page)

        row_text = get_row_text(page, base_url, sec_name)
        assert second_endpoint in row_text, f'Expected {second_endpoint} in the row, got: "{row_text}"'
        assert first_endpoint not in row_text, f'Expected no {first_endpoint} in the row, got: "{row_text}"'

        # .. and the next message reaches the second endpoint only.
        second_marker = new_marker()
        publish_to_topic(page, base_url, topic_name, second_marker)
        wait_for_rest_delivery(second_receiver, second_marker)

        assert not has_request_with_marker(first_receiver.recorded_requests, second_marker), \
            'Expected the message published after the change not to reach the first endpoint'

# ################################################################################################################################

    def test_paused_delivery_keeps_messages(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rest_receivers:'anytuple',
        ) -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        receiver, _ = rest_receivers

        sec_name, topic_name, _ = _client_names('paused')
        endpoint_name = _endpoint_name('paused', 'first')
        import_client_objects(zato_dashboard, sec_name, [topic_name], {endpoint_name: receiver.address})

        # Subscribe the client with push delivery ..
        create_push_rest_subscription(page, base_url, sec_name, topic_name, endpoint_name)

        # .. pause the delivery ..
        open_subscription_edit(page, base_url, sec_name)
        set_edit_delivery_active(page, False)
        submit_subscription_edit(page)

        open_subscription_page(page, base_url)
        row_html = _row_html(page, sec_name)
        assert _Delivery_Disabled_Class in row_html, f'Expected the delivery to be shown as disabled, got: "{row_html}"'

        # .. a message published now stays in the queue ..
        marker = new_marker()
        publish_to_topic(page, base_url, topic_name, marker)
        wait_for_pending_count(page, base_url, sec_name, 1)

        time.sleep(No_Delivery_Wait)
        assert not has_request_with_marker(receiver.recorded_requests, marker), \
            'Expected no message to be pushed while the delivery is paused'

        # .. and it is pushed once the delivery resumes.
        open_subscription_edit(page, base_url, sec_name)
        set_edit_delivery_active(page, True)
        submit_subscription_edit(page)

        wait_for_rest_delivery(receiver, marker)
        wait_for_pending_count(page, base_url, sec_name, 0)

        row_html = _row_html(page, sec_name)
        assert _Delivery_Enabled_Class in row_html, f'Expected the delivery to be shown as enabled, got: "{row_html}"'

# ################################################################################################################################

    def test_edit_without_topics_is_rejected(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        sec_name, topic_name, _ = _client_names('no-topics')
        import_client_objects(zato_dashboard, sec_name, [topic_name], {})

        create_pull_subscription(page, base_url, sec_name, topic_name)

        # Let go of the only topic in the edit form ..
        open_subscription_edit(page, base_url, sec_name)
        set_edit_topic(page, topic_name, False)

        alert_messages = [] # type: list

        def handle_dialog(dialog:'any_') -> 'None':
            alert_messages.append(dialog.message)
            dialog.accept()

        page.on('dialog', handle_dialog)

        # .. the submission is refused ..
        page.click('#edit-div input[type="submit"]')
        page.wait_for_timeout(500)

        page.remove_listener('dialog', handle_dialog)

        assert alert_messages == [_No_Topics_Alert], f'Expected the alert "{_No_Topics_Alert}", got: {alert_messages}'
        assert page.is_visible('#edit-div'), 'Expected the edit dialog to stay open'

        close_dialog_via_jquery(page, 'edit-div')

        # .. and the subscription is unchanged.
        row_text = get_row_text(page, base_url, sec_name)
        assert topic_name in row_text, f'Expected {topic_name} in the row, got: "{row_text}"'

# ################################################################################################################################

    def test_delete_client_subscription(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        sec_name, topic_name, _ = _client_names('delete')
        import_client_objects(zato_dashboard, sec_name, [topic_name], {})

        client_selector = subscription_create_field_selector('client')
        client_option_selector = f'{client_selector} option:text-is("{sec_name}")'

        # Subscribe the client, with one message waiting in its queue ..
        create_pull_subscription(page, base_url, sec_name, topic_name)

        publish_to_topic(page, base_url, topic_name, new_marker())
        wait_for_pending_count(page, base_url, sec_name, 1)

        # .. while subscribed, the client is not offered for another subscription ..
        open_subscription_create_dialog(page, base_url)
        assert page.query_selector(client_option_selector) is None, f'Expected {sec_name} not to be offered'
        close_dialog_via_jquery(page, 'create-div')

        # .. delete the subscription ..
        popup_text = delete_subscription(page, base_url, sec_name)
        assert f'Security definition: {sec_name}' in popup_text, f'Expected the client in the confirmation, got: "{popup_text}"'

        # .. the row stays away after a reload ..
        open_subscription_page(page, base_url)
        assert count_rows(page, sec_name) == 0

        # .. the client is offered again ..
        open_subscription_create_dialog(page, base_url)
        _ = page.wait_for_selector(client_option_selector, state='attached', timeout=Timeout)
        close_dialog_via_jquery(page, 'create-div')

        # .. and a new subscription starts with an empty queue, which then receives new messages.
        create_pull_subscription(page, base_url, sec_name, topic_name)
        wait_for_pending_count(page, base_url, sec_name, 0)

        publish_to_topic(page, base_url, topic_name, new_marker())
        wait_for_pending_count(page, base_url, sec_name, 1)

# ################################################################################################################################

    def test_service_subscription_delivery_edit_and_delete(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        ) -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _, first_topic, second_topic = _client_names('service')
        import_topics(zato_dashboard, [first_topic, second_topic])

        # Subscribe the service to the first topic ..
        create_service_subscription(page, base_url, [_Service_Delivery], first_topic)

        first_marker = new_marker()
        publish_to_topic(page, base_url, first_topic, first_marker)
        wait_for_service_delivery(zato_dashboard, _Service_Delivery, first_marker)

        # .. add the second topic ..
        open_subscription_edit(page, base_url, _Service_Delivery)
        set_edit_topic(page, second_topic, True)
        submit_subscription_edit(page)

        second_marker = new_marker()
        publish_to_topic(page, base_url, second_topic, second_marker)
        wait_for_service_delivery(zato_dashboard, _Service_Delivery, second_marker)

        # .. delete the subscription ..
        _ = delete_subscription(page, base_url, _Service_Delivery)

        # .. and the service receives nothing more.
        deleted_marker = new_marker()
        publish_to_topic(page, base_url, first_topic, deleted_marker)

        time.sleep(No_Delivery_Wait)
        assert not has_service_received(zato_dashboard, _Service_Delivery, deleted_marker), \
            'Expected the service not to receive a message after its subscription was deleted'

# ################################################################################################################################

    def test_deleted_topic_leaves_the_subscription(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        sec_name, first_topic, second_topic = _client_names('topic-delete')
        import_client_objects(zato_dashboard, sec_name, [first_topic, second_topic], {})

        # Subscribe the client to both topics ..
        open_subscription_create_dialog(page, base_url)
        select_subscription_create_option(page, 'client', sec_name)
        pick_subscription_topic(page, first_topic)
        pick_subscription_topic(page, second_topic)
        submit_subscription_create_dialog(page)

        row_text = get_row_text(page, base_url, sec_name)
        assert first_topic in row_text, f'Expected {first_topic} in the row, got: "{row_text}"'
        assert second_topic in row_text, f'Expected {second_topic} in the row, got: "{row_text}"'

        # .. delete the first topic ..
        delete_topic(page, base_url, first_topic)

        # .. the subscription keeps the second one only ..
        row_text = get_row_text(page, base_url, sec_name)
        assert first_topic not in row_text, f'Expected no {first_topic} in the row, got: "{row_text}"'
        assert second_topic in row_text, f'Expected {second_topic} in the row, got: "{row_text}"'

        # .. and still receives its messages.
        publish_to_topic(page, base_url, second_topic, new_marker())
        wait_for_pending_count(page, base_url, sec_name, 1)

# ################################################################################################################################
# ################################################################################################################################
