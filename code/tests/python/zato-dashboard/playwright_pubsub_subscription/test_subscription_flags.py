# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from _support import ModuleCtx, client_publish_accepted, client_pull, create_client, create_pull_subscription_to, \
    create_topics, is_client_refused, is_queued, new_marker, new_prefix, open_subscription_edit, publish, \
    publish_accepted, queue_path, save_edit, server_url, subscription_item_id, wait_for, wait_for_not_queued, \
    wait_for_queued, wait_for_statuses

# Zato
from zato.common.test.playwright_pubsub import create_service_subscription, navigate_to_page, open_edit_dialog, \
    submit_edit_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, anylist, strlist

    any_ = any_
    anydict = anydict
    anylist = anylist
    Page = Page
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class TestCtx:

    # The service that the push subscriber to a service is, deployed by playwright_/conftest.py
    Push_Service = 'test.pubsub.dashboard-service-subscriber.listed'

    # The flags of the edit forms
    Topic_Active    = '#id_edit-is_active'
    Delivery_Active = '#id_edit-is_delivery_active'
    Pub_Active      = '#id_edit-is_pub_active'

# ################################################################################################################################
# ################################################################################################################################

class Setup:
    """ An API client subscribed to two topics, which it may publish to, whose messages it pulls through the REST API.
    """

    def __init__(self, page:'Page', zato_dashboard:'anydict', label:'str') -> 'None':
        self.page = page
        self.base_url = zato_dashboard['dashboard_url']
        self.server_url = server_url(zato_dashboard)

        prefix = new_prefix(label)

        self.client = create_client(page, self.base_url, prefix, 'client')
        topics:'anylist' = create_topics(page, self.base_url, prefix, 2)

        self.first = topics[0]
        self.second = topics[1]
        self.first_name = self.first['name']
        self.second_name = self.second['name']
        self.topic_names = [self.first_name, self.second_name]

        create_pull_subscription_to(page, self.base_url, self.client['name'], self.topic_names)
        self.item_id = subscription_item_id(page, self.base_url, self.client['name'])

        confirmed = {self.first_name: ModuleCtx.Status_Confirmed, self.second_name: ModuleCtx.Status_Confirmed}
        wait_for_statuses(page, self.base_url, self.item_id, confirmed, 'The confirmation of both pairs')

        self.pending_path = queue_path(page, self.base_url, self.item_id, ModuleCtx.Queue_State_Pending)

    def edit(self, selector:'str', is_checked:'bool') -> 'None':
        """ Sets one checkbox of the edit form of the subscription and saves the form.
        """
        open_subscription_edit(self.page, self.base_url, self.item_id, self.topic_names)
        self.page.set_checked(selector, is_checked)
        _ = save_edit(self.page)

    def wait_for_refused(self, topic_name:'str') -> 'None':
        """ Waits until the server refuses the publications of the client to a topic.
        """
        def _is_refused() -> 'bool':
            marker = new_marker('refused')

            out = is_client_refused(self.server_url, self.client, topic_name, marker)
            return out

        wait_for(_is_refused, f'The refusal of the publications of the client to {topic_name}')

    def publish_as_client(self, topic_name:'str') -> 'str':
        """ Publishes as the client to a topic and returns the marker of the accepted message.
        """
        marker = new_marker('accepted')

        client_publish_accepted(self.server_url, self.client, topic_name, marker)
        return marker

    def pull_until(self, marker:'str', pulled:'strlist') -> 'None':
        """ Pulls the messages of the client into a list until it holds the marker.
        """
        def _has_marker() -> 'bool':
            messages = client_pull(self.server_url, self.client)
            pulled.extend(messages)

            out = marker in pulled
            return out

        wait_for(_has_marker, f'The pull of {marker}')

# ################################################################################################################################
# ################################################################################################################################

def _set_topic_active(page:'Page', base_url:'str', topic_id:'str', is_active:'bool') -> 'None':
    navigate_to_page(page, base_url, ModuleCtx.Topic_Page)
    open_edit_dialog(page, 'topic', topic_id)
    page.set_checked(TestCtx.Topic_Active, is_active)
    submit_edit_form(page, ModuleCtx.Dialog_Timeout)

# ################################################################################################################################

def _set_push_delivery(page:'Page', base_url:'str', item_id:'str', topic_name:'str', is_active:'bool') -> 'None':
    open_subscription_edit(page, base_url, item_id, [topic_name])
    page.set_checked(TestCtx.Delivery_Active, is_active)
    _ = save_edit(page)

# ################################################################################################################################
# ################################################################################################################################

def test_inactive_topic(logged_in_page:'any_', zato_dashboard:'anydict') -> 'None':
    """ A topic deactivated on the topic page refuses a message published from the topic page and the publications
    of the client, while its queued messages still leave the queue of a push subscriber.
    """
    page = logged_in_page
    setup = Setup(page, zato_dashboard, 'flags.topic')
    base_url = setup.base_url
    first_id = setup.first['item_id']

    # A push subscriber to the first topic, whose delivery is off so that its messages stay queued ..
    create_service_subscription(page, base_url, [TestCtx.Push_Service], setup.first_name)

    push_id = subscription_item_id(page, base_url, TestCtx.Push_Service)
    wait_for_statuses(page, base_url, push_id, {setup.first_name: ModuleCtx.Status_Confirmed}, 'The push pair')

    _set_push_delivery(page, base_url, push_id, setup.first_name, False)
    push_path = queue_path(page, base_url, push_id, ModuleCtx.Queue_State_Pending)

    queued_marker = new_marker('queued')
    publish_accepted(page, base_url, first_id, queued_marker)
    wait_for_queued(page, base_url, push_path, queued_marker)

    # .. deactivate the topic ..
    _set_topic_active(page, base_url, first_id, False)

    # .. the client's publications to it are refused while those to the other topic are accepted ..
    setup.wait_for_refused(setup.first_name)
    second_marker = setup.publish_as_client(setup.second_name)
    wait_for_queued(page, base_url, setup.pending_path, second_marker)

    # .. a message published from the topic page is refused as well and reaches no queue ..
    refused_marker = new_marker('refused')
    status = publish(page, base_url, first_id, refused_marker)
    assert not status.startswith(ModuleCtx.Publish_Accepted), status

    assert not is_queued(page, base_url, setup.pending_path, refused_marker)
    assert not is_queued(page, base_url, push_path, refused_marker)

    # .. the message queued before the deactivation leaves the queue of the push subscriber once delivery is on ..
    _set_push_delivery(page, base_url, push_id, setup.first_name, True)
    wait_for_not_queued(page, base_url, push_path, queued_marker)

    # .. and the reactivated topic accepts publications again.
    _set_topic_active(page, base_url, first_id, True)

    def _is_accepted() -> 'bool':
        marker = new_marker('reactivated')
        is_refused = is_client_refused(setup.server_url, setup.client, setup.first_name, marker)

        out = not is_refused
        return out

    wait_for(_is_accepted, 'The acceptance of publications to the reactivated topic')

# ################################################################################################################################

def test_pub_active(logged_in_page:'any_', zato_dashboard:'anydict') -> 'None':
    """ Publications switched off on the subscription refuse the publications of the client to both topics.
    """
    setup = Setup(logged_in_page, zato_dashboard, 'flags.pub.active')

    _ = setup.publish_as_client(setup.first_name)
    _ = setup.publish_as_client(setup.second_name)

    setup.edit(TestCtx.Pub_Active, False)

    setup.wait_for_refused(setup.first_name)
    setup.wait_for_refused(setup.second_name)

# ################################################################################################################################

def test_pub_enabled(logged_in_page:'any_', zato_dashboard:'anydict') -> 'None':
    """ Publishing switched off for one topic refuses the publications of the client to that topic only.
    """
    setup = Setup(logged_in_page, zato_dashboard, 'flags.pub.enabled')

    selector = f'{ModuleCtx.Edit_Topics} input.topic-pub-enabled[data-topic="{setup.first_name}"]'
    setup.edit(selector, False)

    setup.wait_for_refused(setup.first_name)
    _ = setup.publish_as_client(setup.second_name)

# ################################################################################################################################

def test_delivery_enabled(logged_in_page:'any_', zato_dashboard:'anydict') -> 'None':
    """ Delivery switched off for one topic keeps its messages in the queue browser while those of the other topic
    leave it, and switching it on lets them leave.
    """
    page = logged_in_page
    setup = Setup(page, zato_dashboard, 'flags.delivery')
    base_url = setup.base_url

    selector = f'{ModuleCtx.Edit_Topics} input.topic-delivery-enabled[data-topic="{setup.first_name}"]'
    setup.edit(selector, False)

    withheld_marker = setup.publish_as_client(setup.first_name)
    delivered_marker = setup.publish_as_client(setup.second_name)

    # The client receives the message of the other topic only ..
    pulled:'strlist' = []
    setup.pull_until(delivered_marker, pulled)

    assert withheld_marker not in pulled

    # .. and the queue browser still shows the withheld one ..
    wait_for_queued(page, base_url, setup.pending_path, withheld_marker)
    assert not is_queued(page, base_url, setup.pending_path, delivered_marker)

    # .. until delivery is switched on again, after which the client receives it and it leaves the queue.
    setup.edit(selector, True)

    setup.pull_until(withheld_marker, pulled)
    wait_for_not_queued(page, base_url, setup.pending_path, withheld_marker)

# ################################################################################################################################
# ################################################################################################################################
