# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The number of messages per push request of a subscription - set in the create dialog of a REST push subscription,
# changed in its edit form, and not offered to a pull subscription.

# Local
from _support import ModuleCtx, create_client, create_pull_subscription_to, create_topics, new_prefix, \
    open_subscription_edit, save_edit, subscription_item_id

# Zato
from zato.common.test.playwright_pubsub import create_outgoing_rest, open_subscription_create_dialog, \
    pick_subscription_topic, select_subscription_create_option, submit_subscription_create_dialog, \
    subscription_create_field_selector

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

    any_ = any_
    anydict = anydict
    Page = Page

# ################################################################################################################################
# ################################################################################################################################

class TestCtx:

    # The delivery of a subscription whose messages are pushed to a REST endpoint
    Delivery_Push = 'push'

    # The field of the create dialog with the number of messages per push request
    Create_Batch_Size = '#create-div input[data-key="batchSize"]'

    # The row and the field of the edit form with the number of messages per push request
    Edit_Batch_Size_Row = '#push-batch-size-edit'
    Edit_Batch_Size     = '#id_edit-push_batch_size'

    # The number of messages per push request given in the create dialog and then in the edit form
    Created_Batch_Size = '25'
    Edited_Batch_Size  = '40'

# ################################################################################################################################
# ################################################################################################################################

def _create_push_rest_subscription(page:'Page', base_url:'str', sec_name:'str', topic_name:'str', rest_name:'str') -> 'None':
    """ Creates a REST push subscription of an API client with the number of messages per request of the test.
    """
    open_subscription_create_dialog(page, base_url)
    select_subscription_create_option(page, 'client', sec_name)

    # Push delivery adds the REST endpoint and the number of messages per request to the form ..
    delivery_selector = subscription_create_field_selector('delivery')
    _ = page.select_option(delivery_selector, value=TestCtx.Delivery_Push)

    endpoint_selector = subscription_create_field_selector('endpoint')
    _ = page.wait_for_selector(endpoint_selector, state='visible', timeout=ModuleCtx.Dialog_Timeout)
    select_subscription_create_option(page, 'endpoint', rest_name)

    # .. whose default is one message ..
    batch_size = page.input_value(TestCtx.Create_Batch_Size)
    assert batch_size == '1', batch_size

    # .. and which the test changes before it submits the form.
    page.fill(TestCtx.Create_Batch_Size, TestCtx.Created_Batch_Size)
    page.dispatch_event(TestCtx.Create_Batch_Size, 'change')

    pick_subscription_topic(page, topic_name)
    submit_subscription_create_dialog(page)

# ################################################################################################################################
# ################################################################################################################################

def test_push_batch_size_of_rest_push(logged_in_page:'any_', zato_dashboard:'anydict') -> 'None':
    """ A REST push subscription created with a number of messages per request shows it in its edit form,
    and an edit of the number is saved.
    """
    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    prefix = new_prefix('batch.rest')

    client = create_client(page, base_url, prefix, 'client')
    topic = create_topics(page, base_url, prefix, 1)[0]
    topic_name = topic['name']
    rest_name = create_outgoing_rest(page, base_url, prefix, 'push')

    _create_push_rest_subscription(page, base_url, client['name'], topic_name, rest_name)
    item_id = subscription_item_id(page, base_url, client['name'])

    # The edit form shows the number given in the create dialog ..
    open_subscription_edit(page, base_url, item_id, [topic_name])
    _ = page.wait_for_selector(TestCtx.Edit_Batch_Size_Row, state='visible', timeout=ModuleCtx.Dialog_Timeout)

    batch_size = page.input_value(TestCtx.Edit_Batch_Size)
    assert batch_size == TestCtx.Created_Batch_Size, batch_size

    # .. it is changed and saved ..
    page.fill(TestCtx.Edit_Batch_Size, TestCtx.Edited_Batch_Size)
    _ = save_edit(page)

    # .. and the edit form shows the new number.
    open_subscription_edit(page, base_url, item_id, [topic_name])

    batch_size = page.input_value(TestCtx.Edit_Batch_Size)
    assert batch_size == TestCtx.Edited_Batch_Size, batch_size

# ################################################################################################################################

def test_push_batch_size_not_offered_to_pull(logged_in_page:'any_', zato_dashboard:'anydict') -> 'None':
    """ The edit form of a pull subscription has no number of messages per push request.
    """
    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    prefix = new_prefix('batch.pull')

    client = create_client(page, base_url, prefix, 'client')
    topic = create_topics(page, base_url, prefix, 1)[0]
    topic_name = topic['name']

    create_pull_subscription_to(page, base_url, client['name'], [topic_name])
    item_id = subscription_item_id(page, base_url, client['name'])

    open_subscription_edit(page, base_url, item_id, [topic_name])

    is_visible = page.is_visible(TestCtx.Edit_Batch_Size_Row)
    assert not is_visible

# ################################################################################################################################
# ################################################################################################################################
