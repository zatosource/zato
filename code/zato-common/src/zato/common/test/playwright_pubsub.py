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
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_Basic_Auth_Page_Url = '/zato/security/basic-auth/?cluster=1'
_Topic_Page_Url = '/zato/pubsub/topic/?cluster=1'
_Permission_Page_Url = '/zato/pubsub/permission/?cluster=1'
_Subscription_Page_Url = '/zato/pubsub/subscription/?cluster=1'
_Outgoing_REST_Page_Url = '/zato/http-soap/?cluster=1&connection=outgoing&transport=plain_http'
_Channel_REST_Page_Url = '/zato/http-soap/?cluster=1&connection=channel&transport=plain_http'
_Outgoing_AMQP_Page_Url = '/zato/outgoing/amqp/?cluster=1'
_Channel_AMQP_Page_Url = '/zato/channel/amqp/?cluster=1'

# ################################################################################################################################
# ################################################################################################################################
#
# Navigation and page interaction helpers
#
# ################################################################################################################################
# ################################################################################################################################

def navigate_to_page(page:'Page', base_url:'str', url_path:'str') -> 'None':
    """ Navigates to a dashboard page and waits for the data table to be ready.
    """

    # Go to the URL ..
    _ = page.goto(f'{base_url}{url_path}')

    # .. and wait for the table to appear.
    page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def open_create_dialog(page:'Page') -> 'None':
    """ Opens the create dialog by clicking the page prompt link.
    """

    # Click the create link ..
    page.click('#markup .page_prompt a')

    # .. and wait for the dialog to appear.
    page.wait_for_selector('#create-div', state='visible')

# ################################################################################################################################

def open_create_dialog_via_js(page:'Page', namespace:'str') -> 'None':
    """ Opens the create dialog via the JS namespace function.
    """

    # Call the JS function ..
    page.evaluate(f'$.fn.zato.pubsub.{namespace}.create()')

    # .. and wait for the dialog to appear.
    page.wait_for_selector('#create-div', state='visible')

# ################################################################################################################################

def submit_create_form(page:'Page', timeout:'int'=10000) -> 'None':
    """ Clicks submit on the create form and waits for the dialog to close.
    """

    # Click submit ..
    page.click('#create-div input[type="submit"]')

    # .. and wait for the dialog to close.
    page.wait_for_selector('#create-div', state='hidden', timeout=timeout)

# ################################################################################################################################

def close_dialog_via_jquery(page:'Page', dialog_id:'str'='create-div') -> 'None':
    """ Closes a jQuery UI dialog and waits for it to be hidden.
    """

    # Close via jQuery ..
    page.evaluate(f'$("#{dialog_id}").dialog("close")')

    # .. and wait for it to be hidden.
    page.wait_for_function(f'!document.querySelector("#{dialog_id}").offsetParent')

# ################################################################################################################################

def wait_for_sec_def_dropdown(page:'Page') -> 'None':
    """ Waits for the security definitions AJAX dropdown to be populated.
    """

    page.wait_for_function(
        'document.querySelector("#id_sec_base_id") && document.querySelector("#id_sec_base_id").options.length > 1',
        timeout=10000
    )

# ################################################################################################################################

def select_sec_def_and_wait_for_topics(page:'Page', sec_name:'str') -> 'None':
    """ Selects a security definition in the create dialog and waits for topic checkboxes to appear.
    """

    # Wait for the security definitions dropdown to be populated ..
    wait_for_sec_def_dropdown(page)

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
#
# Edit and delete helpers
#
# ################################################################################################################################
# ################################################################################################################################

def open_edit_dialog(page:'Page', namespace:'str', item_id:'str') -> 'None':
    """ Opens the edit dialog for a given item via JS.
    """

    # Call the JS edit function ..
    page.evaluate(f'$.fn.zato.pubsub.{namespace}.edit("{item_id}")')

    # .. and wait for the dialog to appear.
    page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################

def submit_edit_form(page:'Page', timeout:'int'=10000) -> 'None':
    """ Clicks submit on the edit form and waits for the dialog to close.
    """

    # Click submit ..
    page.click('#edit-div input[type="submit"]')

    # .. and wait for the dialog to close.
    page.wait_for_selector('#edit-div', state='hidden', timeout=timeout)

# ################################################################################################################################

def trigger_delete(page:'Page', namespace:'str', item_id:'str') -> 'None':
    """ Triggers the delete confirmation popup for a given item.
    """

    # Call the JS delete function ..
    page.evaluate(f'$.fn.zato.pubsub.{namespace}.delete_("{item_id}")')

    # .. and wait for the confirmation dialog.
    page.wait_for_selector('#popup_container', state='visible', timeout=5000)

# ################################################################################################################################

def confirm_delete(page:'Page') -> 'None':
    """ Clicks OK on the delete confirmation popup and waits for the animation.
    """

    # Click OK ..
    page.click('#popup_ok')

    # .. and wait for the row removal.
    time.sleep(0.5)

# ################################################################################################################################
# ################################################################################################################################
#
# Row and table inspection helpers
#
# ################################################################################################################################
# ################################################################################################################################

def get_item_id(page:'Page', name:'str') -> 'str':
    """ Extracts the server-side ID of a row by its name.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    row = page.query_selector(row_selector)
    id_cell = row.query_selector('td[class*="item_id_"]')

    out = id_cell.inner_text().strip()
    return out

# ################################################################################################################################

def find_row_by_name(page:'Page', name:'str') -> 'any_':
    """ Returns the row element matching the given name text.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    out = page.query_selector(row_selector)
    return out

# ################################################################################################################################

def find_row_by_link_text(page:'Page', text:'str') -> 'any_':
    """ Returns the row element containing a link with the given text.
    """

    row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{text}")))'

    out = page.query_selector(row_selector)
    return out

# ################################################################################################################################

def get_table_row_count(page:'Page') -> 'int':
    """ Returns the number of data rows in the table.
    """

    rows = page.query_selector_all('#data-table tbody tr:not(.ignore)')

    out = len(rows)
    return out

# ################################################################################################################################
# ################################################################################################################################
#
# Monitoring and assertion helpers
#
# ################################################################################################################################
# ################################################################################################################################

def collect_console_errors(page:'Page', callback_list:'list') -> 'None':
    """ Registers a console event handler that appends error messages to the list.
    """

    def _on_console(msg:'object') -> 'None':
        if msg.type == 'error':
            callback_list.append(msg.text)

    page.on('console', _on_console)

# ################################################################################################################################

def filter_console_noise(errors:'list', noise_patterns:'list') -> 'list':
    """ Filters a list of error strings, removing those matching known noise patterns.
    """

    out = [] # type: list

    for error_text in errors:
        is_noise = False

        for noise_pattern in noise_patterns:
            if noise_pattern in error_text:
                is_noise = True
                break

        if not is_noise:
            out.append(error_text)

    return out

# ################################################################################################################################

def collect_http_errors(page:'Page', callback_list:'list') -> 'None':
    """ Registers a response handler that appends HTTP 500+ errors to the list.
    """

    def _on_response(response:'object') -> 'None':
        if response.status >= 500:
            callback_list.append(f'{response.status} {response.url}')

    page.on('response', _on_response)

# ################################################################################################################################

def setup_alert_handler(page:'Page') -> 'list':
    """ Registers a dialog handler that collects alert messages and auto-accepts.
    Returns the list that messages will be appended to.
    """

    alert_messages = [] # type: list

    def handle_dialog(dialog:'any_') -> 'None':
        alert_messages.append(dialog.message)
        dialog.accept()

    page.on('dialog', handle_dialog)

    return alert_messages

# ################################################################################################################################
# ################################################################################################################################
#
# Invoker overlay helpers
#
# ################################################################################################################################
# ################################################################################################################################

def open_publish_overlay(page:'Page', item_id:'str') -> 'None':
    """ Opens the publish invoker overlay for a given topic item_id.
    """

    # Call the JS function to open the overlay ..
    page.evaluate(f'$.fn.zato.pubsub.topic.publishMessage("{item_id}")')

    # .. and wait for it to become visible.
    page.wait_for_selector('#invoker-modal-overlay:not(.hidden)', state='visible', timeout=5000)

# ################################################################################################################################

def publish_via_overlay(page:'Page', payload:'str') -> 'None':
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
# ################################################################################################################################
#
# Resource creation helpers
#
# ################################################################################################################################
# ################################################################################################################################

def create_basic_auth(page:'Page', base_url:'str', name_prefix:'str', suffix:'str') -> 'dict':
    """ Creates a Basic Auth security definition via the UI and returns a dict with name, username, and password.
    """

    name = name_prefix + 'auth.' + suffix
    username = 'user.' + name
    password = 'password.' + os.urandom(8).hex()

    # Navigate to the Basic Auth page ..
    navigate_to_page(page, base_url, _Basic_Auth_Page_Url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. fill in the form fields ..
    page.fill('#id_name', name)
    page.fill('#id_username', username)
    page.fill('#id_realm', 'API')
    page.fill('#id_password', password)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=5000)

    out = {
        'name': name,
        'username': username,
        'password': password,
    }

    return out

# ################################################################################################################################

def create_topic(page:'Page', base_url:'str', name_prefix:'str', suffix:'str', description:'str'='') -> 'dict':
    """ Creates a pub/sub topic via the UI and returns a dict with name and item_id.
    """

    name = name_prefix + suffix

    # Navigate to the topics page ..
    navigate_to_page(page, base_url, _Topic_Page_Url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. fill in the fields ..
    page.fill('#id_name', name)
    if description:
        page.fill('#id_description', description)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

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
        'description': description,
    }

    return out

# ################################################################################################################################

def create_permission(
    page:'Page',
    base_url:'str',
    sec_name:'str',
    access_type:'str',
    pattern_type:'str',
    pattern_value:'str',
    ) -> 'str':
    """ Creates a pub/sub permission via the UI and returns the item_id.
    """

    # Navigate to the permissions page ..
    navigate_to_page(page, base_url, _Permission_Page_Url)

    # .. open the create dialog ..
    open_create_dialog_via_js(page, 'permission')

    # .. wait for the security definitions dropdown to be populated via AJAX ..
    wait_for_sec_def_dropdown(page)

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
    submit_create_form(page)

    # .. find the row and extract the item_id.
    row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
    row = page.wait_for_selector(row_selector, state='visible', timeout=5000)
    id_cell = row.query_selector('td[class*="item_id_"]')

    out = id_cell.inner_text().strip()
    return out

# ################################################################################################################################

def create_outgoing_rest(page:'Page', base_url:'str', name_prefix:'str', suffix:'str') -> 'str':
    """ Creates an outgoing REST connection via the UI and returns its name.
    """

    # Zato
    from zato.common.api import ZATO_NONE

    name = name_prefix + 'rest.' + suffix

    # Navigate to the outgoing REST page ..
    navigate_to_page(page, base_url, _Outgoing_REST_Page_Url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. fill in the form fields ..
    page.fill('#id_name', name)
    page.fill('#id_host', 'http://localhost:17654')
    page.fill('#id_url_path', '/test/' + suffix)

    # .. select "No security definition" - the select is hidden by Chosen.js,
    # .. so we set it via JS and trigger the change event ..
    page.evaluate(f'$("#id_security").val("{ZATO_NONE}").trigger("chosen:updated").trigger("change")')

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(span.name-value:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=10000)

    return name

# ################################################################################################################################

def create_all_subscription_prerequisites(page:'Page', base_url:'str', name_prefix:'str', suffix:'str') -> 'dict':
    """ Creates a sec def, topic, and subscriber permission via the UI.
    Returns a dict with sec_name and topic_name.
    """

    # Create the security definition ..
    sec_info = create_basic_auth(page, base_url, name_prefix, suffix)
    sec_name = sec_info['name']

    # .. create the topic ..
    topic_info = create_topic(page, base_url, name_prefix + 'topic.', suffix)
    topic_name = topic_info['name']

    # .. create a subscriber permission linking the sec def to the topic.
    _ = create_permission(page, base_url, sec_name, 'subscriber', 'sub', topic_name)

    out = {
        'sec_name': sec_name,
        'topic_name': topic_name,
    }

    return out

# ################################################################################################################################

def create_permission_with_two_patterns(
    page:'Page',
    base_url:'str',
    sec_name:'str',
    pub_pattern:'str',
    sub_pattern:'str',
    ) -> 'str':
    """ Creates a publisher-subscriber permission with both pub and sub pattern rows. Returns item_id.
    """

    # Navigate to the permissions page ..
    navigate_to_page(page, base_url, _Permission_Page_Url)

    # .. open the create dialog ..
    open_create_dialog_via_js(page, 'permission')

    # .. wait for the dropdown ..
    wait_for_sec_def_dropdown(page)

    # .. select the security definition ..
    page.select_option('#id_sec_base_id', label=sec_name)

    # .. set the access type to publisher-subscriber ..
    page.select_option('#id_access_type', value='publisher-subscriber')
    time.sleep(0.3)

    # .. first row = pub pattern ..
    page.select_option('#create-patterns-container .pattern-row:first-child .pattern-type-select', value='pub')
    page.fill('#create-patterns-container .pattern-row:first-child .pattern-input', pub_pattern)

    # .. add second row = sub pattern ..
    page.click('#create-patterns-container .pattern-row:first-child .pattern-add-button')
    time.sleep(0.2)
    page.select_option('#create-patterns-container .pattern-row:first-child .pattern-type-select', value='sub')
    page.fill('#create-patterns-container .pattern-row:first-child .pattern-input', sub_pattern)

    # .. submit ..
    submit_create_form(page)

    # .. get the item_id.
    row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{sec_name}")))'
    row = page.wait_for_selector(row_selector, state='visible', timeout=5000)
    id_cell = row.query_selector('td[class*="item_id_"]')

    out = id_cell.inner_text().strip()
    return out

# ################################################################################################################################

def set_select_value(page:'Page', selector:'str', value:'str') -> 'None':
    """ Sets a select's value via JS - needed because Chosen.js hides the underlying select element.
    """
    page.evaluate(f'$("{selector}").val("{value}").trigger("chosen:updated").trigger("change")')

# ################################################################################################################################

def create_outgoing_amqp(page:'Page', base_url:'str', name:'str', address:'str', username:'str', password:'str') -> 'str':
    """ Creates an outgoing AMQP connection via the UI and returns its item_id.
    """

    # Navigate to the outgoing AMQP page ..
    navigate_to_page(page, base_url, _Outgoing_AMQP_Page_Url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. fill in the form fields ..
    page.fill('#id_name', name)
    page.fill('#id_address', address)
    page.fill('#id_username', username)
    page.fill('#id_password', password)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. wait for the row to appear ..
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=10000)

    # .. and extract the item_id.
    out = get_item_id(page, name)
    return out

# ################################################################################################################################

def create_amqp_channel(
    page:'Page',
    base_url:'str',
    name:'str',
    address:'str',
    username:'str',
    password:'str',
    queue:'str',
    service_name:'str',
    ) -> 'str':
    """ Creates an AMQP channel via the UI and returns its item_id.
    """

    # Navigate to the AMQP channels page ..
    navigate_to_page(page, base_url, _Channel_AMQP_Page_Url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. fill in the form fields ..
    page.fill('#id_name', name)
    page.fill('#id_address', address)
    page.fill('#id_username', username)
    page.fill('#id_password', password)
    page.fill('#id_queue', queue)

    # .. pick the service the channel will invoke ..
    set_select_value(page, '#id_service', service_name)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. wait for the row to appear ..
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=10000)

    # .. and extract the item_id.
    out = get_item_id(page, name)
    return out

# ################################################################################################################################

def create_amqp_topic(
    page:'Page',
    base_url:'str',
    name:'str',
    outconn_name:'str',
    exchange:'str',
    routing_key:'str',
    channel_name:'str',
    ) -> 'str':
    """ Creates an AMQP-backed pub/sub topic via the UI and returns its item_id.
    The routing key and channel name may be empty strings.
    """

    # Navigate to the topics page ..
    navigate_to_page(page, base_url, _Topic_Page_Url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. fill in the name ..
    page.fill('#id_name', name)

    # .. switch the backend type to AMQP so the AMQP rows appear ..
    set_select_value(page, '#id_backend_type', 'amqp')
    page.wait_for_selector('.zato-topic-amqp-row-create', state='visible', timeout=5000)

    # .. select the outgoing connection ..
    set_select_value(page, '#id_amqp_outconn_name', outconn_name)

    # .. fill in the exchange ..
    page.fill('#id_amqp_exchange', exchange)

    # .. the routing key is optional ..
    if routing_key:
        page.fill('#id_amqp_routing_key', routing_key)

    # .. so is the channel ..
    if channel_name:
        set_select_value(page, '#id_amqp_channel_name', channel_name)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. wait for the row to appear ..
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=10000)

    # .. and extract the item_id.
    out = get_item_id(page, name)
    return out

# ################################################################################################################################

def open_edit_and_read_backend_fields(page:'Page', item_id:'str') -> 'dict':
    """ Opens the topic edit dialog and returns the backend fields it shows, then closes the dialog.
    """

    # Reload first - the dialog must show what the server persisted, not what the local
    # JavaScript put into the row after the last form submission.
    _ = page.reload(wait_until='networkidle')

    # Open the edit dialog ..
    open_edit_dialog(page, 'topic', item_id)

    # .. read all the backend fields ..
    out = {
        'name': page.input_value('#id_edit-name'),
        'backend_type': page.input_value('#id_edit-backend_type'),
        'amqp_outconn_name': page.input_value('#id_edit-amqp_outconn_name'),
        'amqp_exchange': page.input_value('#id_edit-amqp_exchange'),
        'amqp_routing_key': page.input_value('#id_edit-amqp_routing_key'),
        'amqp_channel_name': page.input_value('#id_edit-amqp_channel_name'),
    }

    # .. close the dialog ..
    close_dialog_via_jquery(page, 'edit-div')

    # .. and return what the form showed.
    return out

# ################################################################################################################################

def create_rest_channel(page:'Page', base_url:'str', name:'str', service_name:'str', url_path:'str') -> 'None':
    """ Creates a REST channel via the UI, pointing at the given service.
    """

    # Zato
    from zato.common.api import ZATO_NONE

    # Navigate to the REST channels page ..
    navigate_to_page(page, base_url, _Channel_REST_Page_Url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. fill in the form fields ..
    page.fill('#id_name', name)
    page.fill('#id_url_path', url_path)

    # .. pick the service the channel will invoke ..
    set_select_value(page, '#id_service', service_name)

    # .. no security definition, the channel is open for tests ..
    set_select_value(page, '#id_security', ZATO_NONE)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(span.name-value:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=10000)

# ################################################################################################################################

def select_option_by_label(page:'Page', selector:'str', label:'str') -> 'None':
    """ Selects an option by its visible label via JS - needed because Chosen.js hides the underlying select element.
    """
    page.evaluate(
        '(() => {'
        f'  var sel = document.querySelector("{selector}");'
        '  for (var i = 0; i < sel.options.length; i++) {'
        f'    if (sel.options[i].text === {label!r}) {{'
        '      sel.value = sel.options[i].value;'
        '      $(sel).trigger("chosen:updated").trigger("change");'
        '      return true;'
        '    }'
        '  }'
        '  return false;'
        '})()'
    )

# ################################################################################################################################

def create_outgoing_rest_with_address(page:'Page', base_url:'str', name:'str', host:'str', url_path:'str') -> 'None':
    """ Creates an outgoing REST connection via the UI, pointing at the given host and URL path.
    """

    # Zato
    from zato.common.api import ZATO_NONE

    # Navigate to the outgoing REST page ..
    navigate_to_page(page, base_url, _Outgoing_REST_Page_Url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. fill in the form fields ..
    page.fill('#id_name', name)
    page.fill('#id_host', host)
    page.fill('#id_url_path', url_path)

    # .. no security definition ..
    set_select_value(page, '#id_security', ZATO_NONE)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(span.name-value:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=10000)

# ################################################################################################################################

def create_push_rest_subscription(
    page:'Page',
    base_url:'str',
    sec_name:'str',
    topic_name:'str',
    rest_endpoint_name:'str',
    ) -> 'None':
    """ Creates a push subscription targeting an outgoing REST connection via the UI.
    """

    # Navigate to the subscriptions page ..
    navigate_to_page(page, base_url, _Subscription_Page_Url)

    # .. open the create dialog ..
    open_create_dialog_via_js(page, 'subscription')

    # .. select the sec def and wait for topics ..
    select_sec_def_and_wait_for_topics(page, sec_name)

    # .. check the topic checkbox ..
    page.click(f'#multi-select-div input[name="topic_name"][value="{topic_name}"]')

    # .. set delivery type to push ..
    page.select_option('#id_delivery_type', value='push')
    time.sleep(0.3)

    # .. set push type to REST ..
    page.select_option('#id_push_type', value='rest')
    time.sleep(0.3)

    # .. wait for the REST endpoints dropdown to populate ..
    page.wait_for_function(
        'document.querySelector("#id_rest_push_endpoint_id") && '
        'document.querySelector("#id_rest_push_endpoint_id").options.length > 1',
        timeout=10000
    )

    # .. select the endpoint by its visible name ..
    select_option_by_label(page, '#id_rest_push_endpoint_id', rest_endpoint_name)

    # .. submit the form.
    submit_create_form(page)

# ################################################################################################################################

def create_push_service_subscription(
    page:'Page',
    base_url:'str',
    sec_name:'str',
    topic_name:'str',
    service_name:'str',
    ) -> 'None':
    """ Creates a push subscription targeting a service via the UI.
    """

    # Navigate to the subscriptions page ..
    navigate_to_page(page, base_url, _Subscription_Page_Url)

    # .. open the create dialog ..
    open_create_dialog_via_js(page, 'subscription')

    # .. select the sec def and wait for topics ..
    select_sec_def_and_wait_for_topics(page, sec_name)

    # .. check the topic checkbox ..
    page.click(f'#multi-select-div input[name="topic_name"][value="{topic_name}"]')

    # .. set delivery type to push ..
    page.select_option('#id_delivery_type', value='push')
    time.sleep(0.3)

    # .. set push type to service ..
    page.select_option('#id_push_type', value='service')
    time.sleep(0.3)

    # .. wait for the services dropdown to populate ..
    page.wait_for_function(
        'document.querySelector("#id_push_service_name") && '
        'document.querySelector("#id_push_service_name").options.length > 1',
        timeout=10000
    )

    # .. select the service ..
    set_select_value(page, '#id_push_service_name', service_name)

    # .. submit the form.
    submit_create_form(page)

# ################################################################################################################################

def create_pull_subscription(page:'Page', base_url:'str', sec_name:'str', topic_name:'str') -> 'None':
    """ Creates a pull subscription via the UI.
    """

    # Navigate to the subscriptions page ..
    navigate_to_page(page, base_url, _Subscription_Page_Url)

    # .. open the create dialog ..
    open_create_dialog_via_js(page, 'subscription')

    # .. select the sec def and wait for topics ..
    select_sec_def_and_wait_for_topics(page, sec_name)

    # .. check the topic checkbox ..
    page.click(f'#multi-select-div input[name="topic_name"][value="{topic_name}"]')

    # .. set delivery type to pull ..
    page.select_option('#id_delivery_type', value='pull')

    # .. submit the form.
    submit_create_form(page)

# ################################################################################################################################
# ################################################################################################################################
