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

# Zato
from zato.common.api import ZATO_NONE

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Subscription_Page_Url = '/zato/pubsub/subscription/?cluster=1'
_Basic_Auth_Page_Url = '/zato/security/basic-auth/?cluster=1'
_Topic_Page_Url = '/zato/pubsub/topic/?cluster=1'
_Permission_Page_Url = '/zato/pubsub/permission/?cluster=1'
_Outgoing_REST_Page_Url = '/zato/http-soap/?cluster=1&connection=outgoing&transport=plain_http'

_Test_Name_Prefix = 'test.sub.' + os.urandom(4).hex() + '.'

# ################################################################################################################################
# ################################################################################################################################

def _create_basic_auth(page:'Page', base_url:'str', suffix:'str') -> 'str':
    """ Creates a Basic Auth security definition via the UI and returns its name.
    """

    name = _Test_Name_Prefix + 'auth.' + suffix
    password = 'password.' + os.urandom(8).hex()

    # Navigate to the Basic Auth page ..
    _ = page.goto(f'{base_url}{_Basic_Auth_Page_Url}')
    page.wait_for_selector('#data-table', state='visible')

    # .. open the create dialog ..
    page.click('#markup .page_prompt a')
    page.wait_for_selector('#create-div', state='visible')

    # .. fill in the form fields ..
    page.fill('#id_name', name)
    page.fill('#id_username', 'user.' + name)
    page.fill('#id_realm', 'API')
    page.fill('#id_password', password)

    # .. submit and wait for the dialog to close ..
    page.click('#create-div input[type="submit"]')
    page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    # .. wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=5000)

    return name

# ################################################################################################################################

def _create_topic(page:'Page', base_url:'str', suffix:'str') -> 'str':
    """ Creates a pub/sub topic via the UI and returns its name.
    """

    name = _Test_Name_Prefix + 'topic.' + suffix

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

    # .. wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=5000)

    return name

# ################################################################################################################################

def _create_permission(
    page:'Page',
    base_url:'str',
    sec_name:'str',
    access_type:'str',
    pattern_type:'str',
    pattern_value:'str',
    ) -> 'None':
    """ Creates a pub/sub permission via the UI.
    """

    # Navigate to the permissions page ..
    _ = page.goto(f'{base_url}{_Permission_Page_Url}')
    page.wait_for_selector('#data-table', state='visible')

    # .. open the create dialog ..
    page.evaluate('$.fn.zato.pubsub.permission.create()')
    page.wait_for_selector('#create-div', state='visible')

    # .. wait for the security definitions dropdown to be populated via AJAX ..
    page.wait_for_function(
        'document.querySelector("#id_sec_base_id") && document.querySelector("#id_sec_base_id").options.length > 1',
        timeout=10000
    )

    # .. select the security definition by its visible text ..
    page.select_option('#id_sec_base_id', label=sec_name)

    # .. set the access type ..
    page.select_option('#id_access_type', value=access_type)
    time.sleep(0.3)

    # .. set the pattern type ..
    page.select_option('#create-patterns-container .pattern-row:first-child .pattern-type-select', value=pattern_type)

    # .. fill in the pattern value ..
    page.fill('#create-patterns-container .pattern-row:first-child .pattern-input', pattern_value)

    # .. submit the form ..
    page.click('#create-div input[type="submit"]')

    # .. wait for the dialog to close.
    page.wait_for_selector('#create-div', state='hidden', timeout=10000)

# ################################################################################################################################

def _create_outgoing_rest(page:'Page', base_url:'str', suffix:'str') -> 'str':
    """ Creates an outgoing REST connection via the UI and returns its name.
    """

    name = _Test_Name_Prefix + 'rest.' + suffix

    # Navigate to the outgoing REST page ..
    _ = page.goto(f'{base_url}{_Outgoing_REST_Page_Url}')
    page.wait_for_selector('#data-table', state='visible')

    # .. open the create dialog ..
    page.click('#markup .page_prompt a')
    page.wait_for_selector('#create-div', state='visible')

    # .. fill in the form fields ..
    page.fill('#id_name', name)
    page.fill('#id_host', 'http://localhost:17654')
    page.fill('#id_url_path', '/test/' + suffix)

    # .. select "No security definition" - the select is hidden by Chosen.js,
    # .. so we set it via JS and trigger the change event ..
    page.evaluate(f'$("#id_security").val("{ZATO_NONE}").trigger("chosen:updated").trigger("change")')

    # .. submit and wait for the dialog to close ..
    page.click('#create-div input[type="submit"]')
    page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    # .. wait for the row to appear ..
    row_selector = f'#data-table tbody tr:has(span.name-value:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=10000)

    return name

# ################################################################################################################################

def _create_all_subscription_prerequisites(page:'Page', base_url:'str', suffix:'str') -> 'dict':
    """ Creates a sec def, topic, and subscriber permission via the UI.
    Returns a dict with sec_name and topic_name.
    """

    # Create the security definition ..
    sec_name = _create_basic_auth(page, base_url, suffix)

    # .. create the topic ..
    topic_name = _create_topic(page, base_url, suffix)

    # .. create a subscriber permission linking the sec def to the topic.
    _create_permission(page, base_url, sec_name, 'subscriber', 'sub', topic_name)

    out = {
        'sec_name': sec_name,
        'topic_name': topic_name,
    }

    return out

# ################################################################################################################################

def _open_subscription_create_dialog(page:'Page', base_url:'str') -> 'None':
    """ Navigates to subscriptions page and opens the create dialog.
    """

    # Navigate to the subscriptions page ..
    _ = page.goto(f'{base_url}{_Subscription_Page_Url}')
    page.wait_for_selector('#data-table', state='visible')

    # .. open the create dialog.
    page.evaluate('$.fn.zato.pubsub.subscription.create()')
    page.wait_for_selector('#create-div', state='visible')

# ################################################################################################################################

def _select_sec_def_and_wait_for_topics(page:'Page', sec_name:'str') -> 'None':
    """ Selects a security definition in the create dialog and waits for topic checkboxes to appear.
    """

    # .. wait for the security definitions dropdown to be populated ..
    page.wait_for_function(
        'document.querySelector("#id_sec_base_id") && document.querySelector("#id_sec_base_id").options.length > 1',
        timeout=10000
    )

    # .. select the security definition ..
    page.select_option('#id_sec_base_id', label=sec_name)

    # .. trigger the change event so topics load ..
    page.evaluate('$("#id_sec_base_id").trigger("change")')

    # .. wait for topic checkboxes to appear.
    page.wait_for_function(
        'document.querySelectorAll("#multi-select-div input[name=\\"topic_name\\"]").length > 0',
        timeout=15000
    )

# ################################################################################################################################
# ################################################################################################################################

class TestPubSubSubscriptionCreate:
    """ Tests for the pub/sub subscription create flow.
    """

    def test_page_loads(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the subscriptions page ..
        _ = page.goto(f'{base_url}{_Subscription_Page_Url}')
        page.wait_for_selector('#data-table', state='visible')

        # .. verify the page heading ..
        heading = page.query_selector('h2.zato')
        heading_text = heading.inner_text()
        assert 'Pub/sub subscriptions' in heading_text, f'Expected "Pub/sub subscriptions" in heading, got: {heading_text}'

        # .. verify the create link is present ..
        create_link = page.query_selector('#markup .page_prompt a')
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
        prereqs = _create_all_subscription_prerequisites(page, base_url, 'pull1')

        sec_name = prereqs['sec_name']
        topic_name = prereqs['topic_name']

        # .. open the subscription create dialog ..
        _open_subscription_create_dialog(page, base_url)

        # .. select the sec def and wait for topics ..
        _select_sec_def_and_wait_for_topics(page, sec_name)

        # .. check the topic checkbox ..
        page.click(f'#multi-select-div input[name="topic_name"][value="{topic_name}"]')

        # .. set delivery type to pull ..
        page.select_option('#id_delivery_type', value='pull')

        # .. submit the form ..
        page.click('#create-div input[type="submit"]')
        page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        # .. verify the new row appears with correct values.
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=10000)

        row_text = row.inner_text()
        assert 'Pull' in row_text, f'Expected "Pull" in row, got: "{row_text}"'
        assert topic_name in row_text, f'Expected topic "{topic_name}" in row, got: "{row_text}"'

# ################################################################################################################################

    @pytest.mark.expect_log_errors('outgoing_rest')
    def test_create_push_rest_subscription(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites via the UI ..
        prereqs = _create_all_subscription_prerequisites(page, base_url, 'push-rest1')

        sec_name = prereqs['sec_name']
        topic_name = prereqs['topic_name']

        # .. create an outgoing REST connection ..
        rest_name = _create_outgoing_rest(page, base_url, 'push-rest1')

        # .. open the subscription create dialog ..
        _open_subscription_create_dialog(page, base_url)

        # .. select the sec def and wait for topics ..
        _select_sec_def_and_wait_for_topics(page, sec_name)

        # .. check the topic checkbox ..
        page.click(f'#multi-select-div input[name="topic_name"][value="{topic_name}"]')

        # .. set delivery type to push ..
        page.select_option('#id_delivery_type', value='push')
        time.sleep(0.3)

        # .. set push type to REST ..
        page.select_option('#id_push_type', value='rest')
        time.sleep(0.3)

        # .. wait for REST endpoint dropdown to populate ..
        page.wait_for_function(
            'document.querySelector("#id_rest_push_endpoint_id") && '
            'document.querySelector("#id_rest_push_endpoint_id").options.length > 1',
            timeout=10000
        )

        # .. select the REST endpoint - the select is hidden by Chosen.js,
        # .. so we find the option by label text and set it via JS ..
        page.evaluate(
            '(() => {'
            '  var sel = document.querySelector("#id_rest_push_endpoint_id");'
            '  for (var i = 0; i < sel.options.length; i++) {'
            '    if (sel.options[i].text === ' + repr(rest_name) + ') {'
            '      sel.value = sel.options[i].value;'
            '      $(sel).trigger("chosen:updated").trigger("change");'
            '      return true;'
            '    }'
            '  }'
            '  return false;'
            '})()'
        )

        # .. submit the form ..
        page.click('#create-div input[type="submit"]')
        page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        # .. verify the new row appears with correct values.
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=10000)

        row_text = row.inner_text()
        assert 'Push' in row_text, f'Expected "Push" in row, got: "{row_text}"'
        assert rest_name in row_text, f'Expected REST endpoint "{rest_name}" in row, got: "{row_text}"'

# ################################################################################################################################

    def test_create_push_service_subscription(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites via the UI ..
        prereqs = _create_all_subscription_prerequisites(page, base_url, 'push-svc1')

        sec_name = prereqs['sec_name']
        topic_name = prereqs['topic_name']

        # .. open the subscription create dialog ..
        _open_subscription_create_dialog(page, base_url)

        # .. select the sec def and wait for topics ..
        _select_sec_def_and_wait_for_topics(page, sec_name)

        # .. check the topic checkbox ..
        page.click(f'#multi-select-div input[name="topic_name"][value="{topic_name}"]')

        # .. set delivery type to push ..
        page.select_option('#id_delivery_type', value='push')
        time.sleep(0.3)

        # .. set push type to service ..
        page.select_option('#id_push_type', value='service')
        time.sleep(0.3)

        # .. wait for service dropdown to populate ..
        page.wait_for_function(
            'document.querySelector("#id_push_service_name") && '
            'document.querySelector("#id_push_service_name").options.length > 1',
            timeout=10000
        )

        # .. select the first available service - the select is hidden by Chosen.js,
        # .. so we pick the value via JS and set it with a Chosen trigger ..
        service_name = page.evaluate(
            'document.querySelector("#id_push_service_name option:not([value=\\"\\"])").value'
        )
        page.evaluate(
            f'$("#id_push_service_name").val("{service_name}").trigger("chosen:updated").trigger("change")'
        )

        # .. submit the form ..
        page.click('#create-div input[type="submit"]')
        page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        # .. verify the new row appears with correct values.
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=10000)

        row_text = row.inner_text()
        assert 'Push' in row_text, f'Expected "Push" in row, got: "{row_text}"'
        assert service_name in row_text, f'Expected service "{service_name}" in row, got: "{row_text}"'

# ################################################################################################################################

    def test_cancel_then_reopen_form_is_empty(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        prereqs = _create_all_subscription_prerequisites(page, base_url, 'cancel-reopen')
        sec_name = prereqs['sec_name']

        # .. open the subscription create dialog ..
        _open_subscription_create_dialog(page, base_url)

        # .. select the sec def and wait for topics ..
        _select_sec_def_and_wait_for_topics(page, sec_name)

        # .. close the dialog ..
        page.evaluate('$("#create-div").dialog("close")')
        page.wait_for_function('!document.querySelector("#create-div").offsetParent')

        # .. reopen the dialog ..
        page.evaluate('$.fn.zato.pubsub.subscription.create()')
        page.wait_for_selector('#create-div', state='visible')
        time.sleep(0.5)

        # .. verify the topics area shows the placeholder message.
        topic_area_text = page.inner_text('#multi-select-div')
        assert 'Select a security definition' in topic_area_text, \
            f'Expected placeholder text, got: "{topic_area_text}"'

# ################################################################################################################################

    def test_cancel_no_row_added(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        prereqs = _create_all_subscription_prerequisites(page, base_url, 'cancel-norow')
        sec_name = prereqs['sec_name']
        topic_name = prereqs['topic_name']

        # .. navigate to subscriptions page ..
        _ = page.goto(f'{base_url}{_Subscription_Page_Url}')
        page.wait_for_selector('#data-table', state='visible')

        # .. count rows before ..
        rows_before = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        count_before = len(rows_before)

        # .. open the create dialog ..
        page.evaluate('$.fn.zato.pubsub.subscription.create()')
        page.wait_for_selector('#create-div', state='visible')

        # .. select sec def and topics ..
        _select_sec_def_and_wait_for_topics(page, sec_name)
        page.click(f'#multi-select-div input[name="topic_name"][value="{topic_name}"]')

        # .. close the dialog without submitting ..
        page.evaluate('$("#create-div").dialog("close")')
        page.wait_for_function('!document.querySelector("#create-div").offsetParent')

        # .. verify row count is unchanged.
        rows_after = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        count_after = len(rows_after)

        assert count_after == count_before, \
            f'Expected {count_before} rows after cancel, got: {count_after}'

# ################################################################################################################################

    def test_sec_def_selection_loads_topics(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        prereqs = _create_all_subscription_prerequisites(page, base_url, 'sec-loads')
        sec_name = prereqs['sec_name']
        topic_name = prereqs['topic_name']

        # .. open the subscription create dialog ..
        _open_subscription_create_dialog(page, base_url)

        # .. verify the placeholder is shown before selecting a sec def ..
        topic_area_text = page.inner_text('#multi-select-div')
        assert 'Select a security definition' in topic_area_text, \
            f'Expected placeholder before sec def selection, got: "{topic_area_text}"'

        # .. select the sec def and wait for topics ..
        _select_sec_def_and_wait_for_topics(page, sec_name)

        # .. verify the topic checkbox appeared.
        checkbox = page.query_selector(f'#multi-select-div input[name="topic_name"][value="{topic_name}"]')
        assert checkbox, f'Expected topic checkbox for "{topic_name}" to be present'

# ################################################################################################################################

    def test_delivery_type_toggle_shows_push_fields(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # .. open the subscription create dialog ..
        _open_subscription_create_dialog(page, base_url)

        # .. verify push fields are hidden when Pull is selected ..
        is_push_type_hidden = not page.is_visible('#push-type-create')
        assert is_push_type_hidden, 'Push type span should be hidden when Pull selected'

        is_rest_hidden = not page.is_visible('#rest-endpoint-create')
        assert is_rest_hidden, 'REST endpoint should be hidden when Pull selected'

        # .. switch to push ..
        page.select_option('#id_delivery_type', value='push')
        time.sleep(0.3)

        # .. verify push type field appears.
        is_push_type_visible = page.is_visible('#push-type-create')
        assert is_push_type_visible, 'Push type span should be visible when Push selected'

# ################################################################################################################################

    def test_push_type_toggle_shows_correct_field(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # .. open the subscription create dialog ..
        _open_subscription_create_dialog(page, base_url)

        # .. switch to push ..
        page.select_option('#id_delivery_type', value='push')
        time.sleep(0.3)

        # .. set push type to REST ..
        page.select_option('#id_push_type', value='rest')
        time.sleep(0.3)

        # .. verify REST endpoint is visible and service is hidden ..
        is_rest_visible = page.is_visible('#rest-endpoint-create')
        assert is_rest_visible, 'REST endpoint should be visible for push type REST'

        is_service_hidden = not page.is_visible('#push-service-create')
        assert is_service_hidden, 'Service should be hidden for push type REST'

        # .. switch push type to service ..
        page.select_option('#id_push_type', value='service')
        time.sleep(0.3)

        # .. verify service is visible and REST is hidden.
        is_service_visible = page.is_visible('#push-service-create')
        assert is_service_visible, 'Service should be visible for push type Service'

        is_rest_hidden = not page.is_visible('#rest-endpoint-create')
        assert is_rest_hidden, 'REST endpoint should be hidden for push type Service'

# ################################################################################################################################

    def test_no_sec_def_selected_shows_placeholder(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # .. open the subscription create dialog ..
        _open_subscription_create_dialog(page, base_url)

        # .. verify the topics area shows the placeholder message.
        topic_area_text = page.inner_text('#multi-select-div')
        assert 'Select a security definition' in topic_area_text, \
            f'Expected placeholder text, got: "{topic_area_text}"'

# ################################################################################################################################

    def test_no_topics_checked_prevents_submit(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites ..
        prereqs = _create_all_subscription_prerequisites(page, base_url, 'no-topic')
        sec_name = prereqs['sec_name']

        # .. open the subscription create dialog ..
        _open_subscription_create_dialog(page, base_url)

        # .. select the sec def and wait for topics but do not check any ..
        _select_sec_def_and_wait_for_topics(page, sec_name)

        # .. set up a listener for the alert dialog ..
        alert_messages = [] # type: list

        def handle_dialog(dialog:'any_') -> 'None':
            alert_messages.append(dialog.message)
            dialog.accept()

        page.on('dialog', handle_dialog)

        # .. try to submit ..
        page.click('#create-div input[type="submit"]')
        time.sleep(1.0)

        # .. verify the alert about topics was shown ..
        assert len(alert_messages) > 0, 'Expected an alert about no topics selected'
        assert 'topic' in alert_messages[0].lower(), \
            f'Expected alert about topic, got: "{alert_messages[0]}"'

        # .. verify the dialog is still open.
        is_visible = page.is_visible('#create-div')
        assert is_visible, 'Expected create dialog to still be open after rejection'

        page.remove_listener('dialog', handle_dialog)

# ################################################################################################################################

    def test_sub_key_displayed(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites and a pull subscription ..
        prereqs = _create_all_subscription_prerequisites(page, base_url, 'subkey')
        sec_name = prereqs['sec_name']
        topic_name = prereqs['topic_name']

        _open_subscription_create_dialog(page, base_url)
        _select_sec_def_and_wait_for_topics(page, sec_name)
        page.click(f'#multi-select-div input[name="topic_name"][value="{topic_name}"]')
        page.select_option('#id_delivery_type', value='pull')
        page.click('#create-div input[type="submit"]')
        page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        # .. verify the sub_key span is present in the row.
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=10000)

        sub_key_span = row.query_selector('.ps-sub-key')
        assert sub_key_span, 'Expected sub_key span to be present in the row'

        sub_key_text = sub_key_span.get_attribute('data-sub-key')
        assert sub_key_text, f'Expected sub_key data attribute to be non-empty'
        assert sub_key_text.startswith('sk'), f'Expected sub_key to start with "sk", got: "{sub_key_text}"'

# ################################################################################################################################

    def test_pending_messages_link_navigates_to_queue(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create prerequisites and a pull subscription ..
        prereqs = _create_all_subscription_prerequisites(page, base_url, 'pending')
        sec_name = prereqs['sec_name']
        topic_name = prereqs['topic_name']

        _open_subscription_create_dialog(page, base_url)
        _select_sec_def_and_wait_for_topics(page, sec_name)
        page.click(f'#multi-select-div input[name="topic_name"][value="{topic_name}"]')
        page.select_option('#id_delivery_type', value='pull')
        page.click('#create-div input[type="submit"]')
        page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        # .. find the row and click the pending messages link ..
        row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=10000)

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
        _ = page.goto(f'{base_url}{_Subscription_Page_Url}')
        page.wait_for_selector('#data-table', state='visible')

        # .. delete any pre-existing demo subscription so the import has something to create ..
        demo_row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{_demo_sec_name}")))'
        demo_row = page.query_selector(demo_row_selector)

        if demo_row:

            # .. accept the confirmation dialog that the delete will trigger ..
            page.once('dialog', lambda dialog: dialog.accept())

            # .. click the Delete link in that row ..
            delete_link = demo_row.query_selector('a:text-is("Delete")')
            delete_link.click()
            time.sleep(1.0)

            # .. reload and confirm the row is gone ..
            _ = page.goto(f'{base_url}{_Subscription_Page_Url}')
            page.wait_for_selector('#data-table', state='visible')

            gone = page.query_selector(demo_row_selector)
            assert gone is None, f'Expected demo subscription row to be deleted but it is still present'

        # .. click "Import demo config" ..
        page.click('a:text-is("Import demo config")')
        page.wait_for_load_state('networkidle')
        time.sleep(5.0)

        # .. reload to see updated data ..
        _ = page.goto(f'{base_url}{_Subscription_Page_Url}')
        page.wait_for_selector('#data-table', state='visible')

        # .. verify the demo subscription was re-created.
        imported_row = page.query_selector(demo_row_selector)
        assert imported_row, f'Expected demo subscription row for "{_demo_sec_name}" after import'

# ################################################################################################################################
# ################################################################################################################################
