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

_Permission_Page_Url = '/zato/pubsub/permission/?cluster=1'
_Basic_Auth_Page_Url = '/zato/security/basic-auth/?cluster=1'
_Topic_Page_Url = '/zato/pubsub/topic/?cluster=1'

_Test_Name_Prefix = 'test.perm.' + os.urandom(4).hex() + '.'

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
# ################################################################################################################################

class TestPubSubPermissionCreate:
    """ Tests for the pub/sub permission create flow.
    """

    def test_page_loads(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the permissions page ..
        _ = page.goto(f'{base_url}{_Permission_Page_Url}')
        page.wait_for_selector('#data-table', state='visible')

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
        sec_name = _create_basic_auth(page, base_url, 'pub1')
        _ = _create_topic(page, base_url, 'pub1')

        pattern_value = 'test.pub1.*'

        # .. create the permission ..
        _create_permission(page, base_url, sec_name, 'publisher', 'pub', pattern_value)

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
        sec_name = _create_basic_auth(page, base_url, 'sub1')
        _ = _create_topic(page, base_url, 'sub1')

        pattern_value = 'test.sub1.*'

        # .. create the permission ..
        _create_permission(page, base_url, sec_name, 'subscriber', 'sub', pattern_value)

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
        sec_name = _create_basic_auth(page, base_url, 'pubsub1')
        _ = _create_topic(page, base_url, 'pubsub1')

        pub_pattern = 'test.pubsub1.pub.*'
        sub_pattern = 'test.pubsub1.sub.*'

        # Navigate to the permissions page ..
        _ = page.goto(f'{base_url}{_Permission_Page_Url}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open the create dialog ..
        page.evaluate('$.fn.zato.pubsub.permission.create()')
        page.wait_for_selector('#create-div', state='visible')

        # .. wait for the security definitions dropdown ..
        page.wait_for_function(
            'document.querySelector("#id_sec_base_id") && document.querySelector("#id_sec_base_id").options.length > 1',
            timeout=10000
        )

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
        page.click('#create-div input[type="submit"]')
        page.wait_for_selector('#create-div', state='hidden', timeout=10000)

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
        sec_name = _create_basic_auth(page, base_url, 'cancel-reopen')

        # Navigate to the permissions page ..
        _ = page.goto(f'{base_url}{_Permission_Page_Url}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open the create dialog ..
        page.evaluate('$.fn.zato.pubsub.permission.create()')
        page.wait_for_selector('#create-div', state='visible')

        # .. wait for the security definitions dropdown ..
        page.wait_for_function(
            'document.querySelector("#id_sec_base_id") && document.querySelector("#id_sec_base_id").options.length > 1',
            timeout=10000
        )

        # .. fill in the form fields ..
        page.select_option('#id_sec_base_id', label=sec_name)
        page.select_option('#id_access_type', value='publisher')
        time.sleep(0.2)
        page.fill('#create-patterns-container .pattern-row:first-child .pattern-input', 'test.cancel.*')

        # .. close the dialog ..
        page.evaluate('$("#create-div").dialog("close")')
        page.wait_for_function('!document.querySelector("#create-div").offsetParent')

        # .. reopen the dialog ..
        page.evaluate('$.fn.zato.pubsub.permission.create()')
        page.wait_for_selector('#create-div', state='visible')
        time.sleep(0.5)

        # .. verify the pattern input is empty.
        pattern_value = page.input_value('#create-patterns-container .pattern-row:first-child .pattern-input')
        assert pattern_value == '', f'Expected empty pattern, got: "{pattern_value}"'

# ################################################################################################################################

    def test_cancel_no_row_added(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a sec def ..
        sec_name = _create_basic_auth(page, base_url, 'cancel-norow')

        # Navigate to the permissions page ..
        _ = page.goto(f'{base_url}{_Permission_Page_Url}')
        page.wait_for_selector('#data-table', state='visible')

        # .. count rows before ..
        rows_before = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        count_before = len(rows_before)

        # .. open the create dialog ..
        page.evaluate('$.fn.zato.pubsub.permission.create()')
        page.wait_for_selector('#create-div', state='visible')

        # .. wait for dropdown ..
        page.wait_for_function(
            'document.querySelector("#id_sec_base_id") && document.querySelector("#id_sec_base_id").options.length > 1',
            timeout=10000
        )

        # .. fill in fields ..
        page.select_option('#id_sec_base_id', label=sec_name)
        page.select_option('#id_access_type', value='publisher')
        time.sleep(0.2)
        page.fill('#create-patterns-container .pattern-row:first-child .pattern-input', 'test.norow.*')

        # .. close the dialog without submitting ..
        page.evaluate('$("#create-div").dialog("close")')
        page.wait_for_function('!document.querySelector("#create-div").offsetParent')

        # .. verify row count is unchanged.
        rows_after = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        count_after = len(rows_after)

        assert count_after == count_before, \
            f'Expected {count_before} rows after cancel, got: {count_after}'

# ################################################################################################################################

    def test_add_and_remove_pattern_rows(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the permissions page ..
        _ = page.goto(f'{base_url}{_Permission_Page_Url}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open the create dialog ..
        page.evaluate('$.fn.zato.pubsub.permission.create()')
        page.wait_for_selector('#create-div', state='visible')
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
        sec_name = _create_basic_auth(page, base_url, 'empty-pat')

        # Navigate to the permissions page ..
        _ = page.goto(f'{base_url}{_Permission_Page_Url}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open the create dialog ..
        page.evaluate('$.fn.zato.pubsub.permission.create()')
        page.wait_for_selector('#create-div', state='visible')

        # .. wait for the security definitions dropdown ..
        page.wait_for_function(
            'document.querySelector("#id_sec_base_id") && document.querySelector("#id_sec_base_id").options.length > 1',
            timeout=10000
        )

        # .. select the sec def and access type, but leave pattern empty ..
        page.select_option('#id_sec_base_id', label=sec_name)
        page.select_option('#id_access_type', value='publisher')
        time.sleep(0.2)

        # .. set up a listener for the alert dialog ..
        alert_messages = [] # type: list

        def handle_dialog(dialog:'any_') -> 'None':
            alert_messages.append(dialog.message)
            dialog.accept()

        page.on('dialog', handle_dialog)

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

        page.remove_listener('dialog', handle_dialog)

# ################################################################################################################################
# ################################################################################################################################
