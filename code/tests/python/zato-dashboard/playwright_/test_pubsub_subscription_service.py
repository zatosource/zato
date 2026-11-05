# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import choose_subscriber_kind, close_dialog_via_jquery, confirm_delete, \
    create_service_subscription, is_subscription_service_offered, navigate_to_page, open_edit_dialog, \
    open_subscription_create_dialog, submit_edit_form, trigger_delete
from zato.common.typing_ import any_, cast_

# Zato - test helpers
from mcp_gateway_live import import_enmasse

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

_Subscription_Page_Url = '/zato/pubsub/subscription/'

# The services the fixtures deploy, see fixtures/services/pubsub_service_subscriber_test_services.py
_Service_Create  = 'test.pubsub.dashboard-service-subscriber.create-1'
_Service_Many_1  = 'test.pubsub.dashboard-service-subscriber.many-1'
_Service_Many_2  = 'test.pubsub.dashboard-service-subscriber.many-2'
_Service_Listed  = 'test.pubsub.dashboard-service-subscriber.listed'
_Service_Edit    = 'test.pubsub.dashboard-service-subscriber.edit'
_Service_Delete  = 'test.pubsub.dashboard-service-subscriber.delete'

_Topic_Prefix = 'test.sub.service.' + CryptoManager.generate_hex_string(16) + '.'

_Edit_Topics_Selector = '#id_edit-multi-select-div'

_Kind_Service = 'service'

# How long a request of the Dashboard may take, in milliseconds
_Timeout = 15000

# ################################################################################################################################
# ################################################################################################################################

def _import_topics(zato_dashboard:'anydict', topic_names:'strlist') -> 'None':
    """ Creates the topics through enmasse.
    """
    lines = ['pubsub_topic:', '']

    for topic_name in topic_names:
        lines.append(f'  - name: {topic_name}')

    lines.append('')

    yaml_content = '\n'.join(lines)
    import_enmasse(zato_dashboard, yaml_content)

# ################################################################################################################################

def _open_service_create_dialog(page:'Page', base_url:'str') -> 'None':
    """ Opens the dialog creating a subscription, with a service as the subscriber.
    """
    open_subscription_create_dialog(page, base_url)
    choose_subscriber_kind(page, _Kind_Service)

# ################################################################################################################################

def _row_selector(service_name:'str') -> 'str':
    """ Returns the selector of the rows whose subscriber column names the service.
    """
    out = f'#data-table tbody tr:has(td:nth-child(3) a:text-is("{service_name}"))'
    return out

# ################################################################################################################################

def _wait_for_service_row(page:'Page', service_name:'str') -> 'any_':
    """ Waits for the row of the service's subscription and checks that its subscriber column links to the service.
    """
    row = cast_('any_', page.wait_for_selector(_row_selector(service_name), state='visible', timeout=_Timeout))

    subscriber_link = row.query_selector('td:nth-child(3) a')
    href = subscriber_link.get_attribute('href')

    assert href.startswith('/zato/service/'), f'Expected a link to the service, got: "{href}"'

    out = row
    return out

# ################################################################################################################################

def _count_service_rows(page:'Page', service_name:'str') -> 'int':
    rows = page.query_selector_all(_row_selector(service_name))

    out = len(rows)
    return out

# ################################################################################################################################

def _get_row_id(row:'any_') -> 'str':
    id_cell = row.query_selector('td[class*="item_id_"]')

    out = id_cell.inner_text().strip()
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestPubSubSubscriptionService:
    """ Subscriptions whose subscriber is a service, without a security definition, created, edited and deleted in the Dashboard.
    """

    def test_create_one_service_subscription(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        topic_name = _Topic_Prefix + 'create'
        _import_topics(zato_dashboard, [topic_name])

        # Create the subscription ..
        create_service_subscription(page, base_url, [_Service_Create], topic_name)

        # .. its row appears at once, without a reload ..
        row = _wait_for_service_row(page, _Service_Create)
        row_text = row.inner_text()

        assert 'Push' in row_text, f'Expected "Push" in the row, got: "{row_text}"'
        assert topic_name in row_text, f'Expected the topic "{topic_name}" in the row, got: "{row_text}"'

        # .. and it is still there, once, after a reload.
        navigate_to_page(page, base_url, _Subscription_Page_Url)

        row = _wait_for_service_row(page, _Service_Create)
        row_text = row.inner_text()

        assert topic_name in row_text, f'Expected the topic "{topic_name}" in the row after reload, got: "{row_text}"'
        assert _count_service_rows(page, _Service_Create) == 1

# ################################################################################################################################

    def test_create_many_services_one_row_each(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        topic_name = _Topic_Prefix + 'many'
        _import_topics(zato_dashboard, [topic_name])

        service_names = [_Service_Many_1, _Service_Many_2]

        # Create the subscriptions of both services in one submission ..
        create_service_subscription(page, base_url, service_names, topic_name)

        # .. a row for each service appears without a reload ..
        for service_name in service_names:
            _ = _wait_for_service_row(page, service_name)

        # .. and after a reload, each service has exactly one row, with a sub_key of its own.
        navigate_to_page(page, base_url, _Subscription_Page_Url)

        sub_keys = set()

        for service_name in service_names:

            row = _wait_for_service_row(page, service_name)
            row_text = row.inner_text()

            assert topic_name in row_text, f'Expected the topic "{topic_name}" in the row of {service_name}, got: "{row_text}"'
            assert _count_service_rows(page, service_name) == 1

            sub_key_span = row.query_selector('.ps-sub-key')
            sub_key = sub_key_span.get_attribute('data-sub-key')
            sub_keys.add(sub_key)

        assert len(sub_keys) == 2, f'Expected two different sub_keys, got: {sub_keys}'

# ################################################################################################################################

    def test_subscribed_service_leaves_the_list(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        topic_name = _Topic_Prefix + 'listed'
        _import_topics(zato_dashboard, [topic_name])

        # The service is offered before it has a subscription ..
        _open_service_create_dialog(page, base_url)
        assert is_subscription_service_offered(page, _Service_Listed), f'Expected {_Service_Listed} to be offered'
        close_dialog_via_jquery(page, 'create-div')

        # .. it subscribes ..
        create_service_subscription(page, base_url, [_Service_Listed], topic_name)
        _ = _wait_for_service_row(page, _Service_Listed)

        # .. and it is no longer offered.
        _open_service_create_dialog(page, base_url)
        assert not is_subscription_service_offered(page, _Service_Listed), f'Expected {_Service_Listed} not to be offered'
        close_dialog_via_jquery(page, 'create-div')

# ################################################################################################################################

    def test_edit_service_subscription(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        first_topic = _Topic_Prefix + 'edit-first'
        second_topic = _Topic_Prefix + 'edit-second'
        _import_topics(zato_dashboard, [first_topic, second_topic])

        # Create the subscription to the first topic ..
        create_service_subscription(page, base_url, [_Service_Edit], first_topic)

        navigate_to_page(page, base_url, _Subscription_Page_Url)
        row = _wait_for_service_row(page, _Service_Edit)
        row_id = _get_row_id(row)

        # .. open its edit dialog ..
        open_edit_dialog(page, 'subscription', row_id)

        # .. which names the service as the subscriber ..
        label_text = page.inner_text('label[for="id_edit-sec_base_id"]')
        assert label_text == 'Service', f'Expected the subscriber label "Service", got: "{label_text}"'

        subscriber_link = cast_('any_', page.query_selector('#edit-sec-def-container a'))
        subscriber_text = subscriber_link.inner_text()
        subscriber_href = subscriber_link.get_attribute('href')

        assert subscriber_text == _Service_Edit, f'Expected the subscriber "{_Service_Edit}", got: "{subscriber_text}"'
        assert subscriber_href.startswith('/zato/service/'), f'Expected a link to the service, got: "{subscriber_href}"'

        # .. and lists every topic, the subscribed one checked ..
        first_checkbox_selector = f'{_Edit_Topics_Selector} input[name="topic_name"][value="{first_topic}"]'
        second_checkbox_selector = f'{_Edit_Topics_Selector} input[name="topic_name"][value="{second_topic}"]'

        _ = page.wait_for_selector(second_checkbox_selector, state='attached', timeout=_Timeout)

        assert page.is_checked(first_checkbox_selector), f'Expected {first_topic} to be checked'
        assert not page.is_checked(second_checkbox_selector), f'Expected {second_topic} not to be checked'

        # .. the second topic is added ..
        page.click(second_checkbox_selector)
        submit_edit_form(page, timeout=_Timeout)

        # .. and after a reload, the one row of the service lists both topics.
        navigate_to_page(page, base_url, _Subscription_Page_Url)

        row = _wait_for_service_row(page, _Service_Edit)
        row_text = row.inner_text()

        assert first_topic in row_text, f'Expected the topic "{first_topic}" in the row, got: "{row_text}"'
        assert second_topic in row_text, f'Expected the topic "{second_topic}" in the row, got: "{row_text}"'
        assert _count_service_rows(page, _Service_Edit) == 1

# ################################################################################################################################

    def test_delete_service_subscription(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        topic_name = _Topic_Prefix + 'delete'
        _import_topics(zato_dashboard, [topic_name])

        # Create the subscription ..
        create_service_subscription(page, base_url, [_Service_Delete], topic_name)

        navigate_to_page(page, base_url, _Subscription_Page_Url)
        row = _wait_for_service_row(page, _Service_Delete)
        row_id = _get_row_id(row)

        # .. delete it ..
        trigger_delete(page, 'subscription', row_id)

        popup_text = page.inner_text('#popup_container')
        assert f'Service: {_Service_Delete}' in popup_text, f'Expected the service in the confirmation, got: "{popup_text}"'

        confirm_delete(page)
        _ = page.wait_for_selector(_row_selector(_Service_Delete), state='detached', timeout=_Timeout)

        # .. the row stays away after a reload ..
        navigate_to_page(page, base_url, _Subscription_Page_Url)
        assert _count_service_rows(page, _Service_Delete) == 0

        # .. and the service is offered for a subscription again.
        _open_service_create_dialog(page, base_url)
        assert is_subscription_service_offered(page, _Service_Delete), f'Expected {_Service_Delete} to be offered again'
        close_dialog_via_jquery(page, 'create-div')

# ################################################################################################################################
# ################################################################################################################################
