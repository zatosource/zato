# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import time

# requests
import requests

# Zato
from zato.common.api import API_Key, ZATO_NONE
from zato.common.test.playwright_pubsub import navigate_to_page, open_create_dialog, select_option_by_label, \
    set_select_value, submit_create_form, submit_edit_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from requests import Response
    from zato.common.typing_ import any_, anydict, strlistnone

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

Channel_Page_Url = '/zato/http-soap/?cluster=1&connection=channel&transport=plain_http'

# How long to wait for a hot-deployed service to appear in the service select
_Service_Deploy_Timeout = 60

# How long to wait between the polling attempts above
_Service_Poll_Interval = 1.0

# Text fields inside the "More options" block, keyed by option name
_More_Options_Text_Fields = ('method', 'http_accept')

# Select fields inside the "More options" block
_More_Options_Select_Fields = ('url_params_pri', 'params_pri')

# Checkbox fields inside the "More options" block
_More_Options_Checkbox_Fields = ('merge_url_params_req', 'match_slash')

# ################################################################################################################################
# ################################################################################################################################
#
# Page navigation and row lookup
#
# ################################################################################################################################
# ################################################################################################################################

def open_channel_page(page:'Page', base_url:'str', query:'str'='') -> 'None':
    """ Navigates to the REST channels page, optionally filtering by a query.
    """

    url_path = Channel_Page_Url
    if query:
        url_path += f'&query={query}'

    navigate_to_page(page, base_url, url_path)

# ################################################################################################################################

def find_channel_row(page:'Page', name:'str') -> 'any_':
    """ Returns the table row for a channel of the given name or None if there is no such row.
    """

    # The name cell wraps the actual name in a span so the GW badge does not interfere with matching.
    row_selector = f'#data-table tbody tr:has(span.name-value:text-is("{name}"))'

    out = page.query_selector(row_selector)
    return out

# ################################################################################################################################

def wait_for_channel_row(page:'Page', name:'str') -> 'any_':
    """ Waits for the row of a channel with the given name to appear and returns it.
    """

    row_selector = f'#data-table tbody tr:has(span.name-value:text-is("{name}"))'

    out = page.wait_for_selector(row_selector, state='visible', timeout=10000)
    return out

# ################################################################################################################################

def get_channel_id(page:'Page', name:'str') -> 'str':
    """ Returns the server-side ID of a channel row identified by name.
    """

    row = find_channel_row(page, name)
    id_cell = row.query_selector('td[class*="item_id_"]')

    out = id_cell.inner_text().strip()
    return out

# ################################################################################################################################

def get_row_cell_texts(row:'any_') -> 'list':
    """ Returns the stripped text of every cell in a row.
    """

    out = [] # type: list

    cells = row.query_selector_all('td')
    for cell in cells:
        text = cell.inner_text().strip()
        out.append(text)

    return out

# ################################################################################################################################
# ################################################################################################################################
#
# Form filling
#
# ################################################################################################################################
# ################################################################################################################################

def _ensure_block_visible(page:'Page', dialog_id:'str', toggler_fragment:'str', probe_selector:'str') -> 'None':
    """ Makes sure a collapsible options block inside a dialog is visible, clicking its toggler if needed.
    """

    probe = page.query_selector(probe_selector)

    # The block may have been toggled by a previous dialog interaction, only click when it is hidden.
    if not probe.is_visible():
        page.click(f'#{dialog_id} a[href*="{toggler_fragment}"]')
        page.wait_for_selector(probe_selector, state='visible', timeout=5000)

# ################################################################################################################################

def check_security_group(page:'Page', dialog_id:'str', group_name:'str', should_check:'bool'=True) -> 'None':
    """ Checks or unchecks a security group checkbox in the create or edit dialog.
    """

    # The multi-select div is populated asynchronously so wait for the checkboxes first ..
    suffix = 'create' if dialog_id == 'create-div' else 'edit'
    container = f'#multi-select-div-{suffix}'
    page.wait_for_selector(f'{container} input[type="checkbox"]', state='attached', timeout=10000)

    # .. the block with the checkboxes starts out collapsed ..
    _ensure_block_visible(page, dialog_id, 'api-client-groups-options-block', f'{container} input[type="checkbox"]')

    # .. find the row whose link carries the group name and toggle its checkbox.
    checkbox_selector = f'{container} tr:has(a:text-is("{group_name}")) input[type="checkbox"]'
    page.set_checked(checkbox_selector, should_check)

# ################################################################################################################################

def fill_channel_form(page:'Page', options:'anydict', prefix:'str'='') -> 'None':
    """ Fills the REST channel create or edit form. An empty prefix means the create form,
    the 'edit-' prefix means the edit form. Only the fields present in options are touched.
    """

    dialog_id = 'edit-div' if prefix else 'create-div'

    # Basic text fields ..
    if 'name' in options:
        page.fill(f'#id_{prefix}name', options['name'])

    if 'url_path' in options:
        page.fill(f'#id_{prefix}url_path', options['url_path'])

    # .. the service select, hidden behind Chosen.js ..
    if 'service' in options:
        set_select_value(page, f'#id_{prefix}service', options['service'])

    # .. the security select, selected by its visible label, e.g. "Basic Auth/My def" ..
    if 'security' in options:
        select_option_by_label(page, f'#id_{prefix}security', options['security'])

    # .. the security select, selected by its raw value, e.g. ZATO_NONE ..
    if 'security_value' in options:
        set_select_value(page, f'#id_{prefix}security', options['security_value'])

    # .. the data format select ..
    if 'data_format' in options:
        set_select_value(page, f'#id_{prefix}data_format', options['data_format'])

    # .. the active checkbox ..
    if 'is_active' in options:
        page.set_checked(f'#id_{prefix}is_active', options['is_active'])

    # .. the OpenAPI inclusion checkbox, shown for REST channels only ..
    if 'should_include_in_openapi' in options:
        page.set_checked(f'#id_{prefix}should_include_in_openapi', options['should_include_in_openapi'])

    # .. the deprecation checkbox, shown for REST channels only ..
    if 'is_deprecated' in options:
        page.set_checked(f'#id_{prefix}is_deprecated', options['is_deprecated'])

    # .. the day the deprecated channel will be retired - set via JS because focusing
    # the field would pop up its date-time picker over the rest of the form ..
    if 'deprecation_sunset' in options:
        sunset_date = options['deprecation_sunset']
        _ = page.evaluate(f'$("#id_{prefix}deprecation_sunset").val("{sunset_date}")')

    # .. and the URL path of its replacement.
    if 'deprecation_successor' in options:
        page.fill(f'#id_{prefix}deprecation_successor', options['deprecation_successor'])

    # .. the audit log checkbox ..
    if 'is_audit_log_active' in options:
        page.set_checked(f'#id_{prefix}is_audit_log_active', options['is_audit_log_active'])

    # .. the gateway service list textarea, visible only for the gateway trigger service ..
    if 'gateway_service_list' in options:
        page.fill(f'#id_{prefix}gateway_service_list', options['gateway_service_list'])

    # .. security groups, given as a list of group names to check ..
    if 'security_groups' in options:
        for group_name in options['security_groups']:
            check_security_group(page, dialog_id, group_name)

    # .. and security groups to uncheck.
    if 'security_groups_uncheck' in options:
        for group_name in options['security_groups_uncheck']:
            check_security_group(page, dialog_id, group_name, should_check=False)

    # .. and everything under "More options".
    _fill_more_options(page, options, prefix, dialog_id)

# ################################################################################################################################

def _fill_more_options(page:'Page', options:'anydict', prefix:'str', dialog_id:'str') -> 'None':
    """ Fills the fields hidden in the "More options" block if any of them is present in options.
    """

    # Check whether any of the block's fields was requested at all ..
    needs_block = False

    for field_name in _More_Options_Text_Fields + _More_Options_Select_Fields + _More_Options_Checkbox_Fields:
        if field_name in options:
            needs_block = True
            break

    if not needs_block:
        return

    # .. reveal the block so Playwright can interact with the fields ..
    _ensure_block_visible(page, dialog_id, 'more-options-block', f'#id_{prefix}http_accept')

    # .. plain text inputs ..
    for field_name in _More_Options_Text_Fields:
        if field_name in options:
            page.fill(f'#id_{prefix}{field_name}', options[field_name])

    # .. selects ..
    for field_name in _More_Options_Select_Fields:
        if field_name in options:
            set_select_value(page, f'#id_{prefix}{field_name}', options[field_name])

    # .. and checkboxes.
    for field_name in _More_Options_Checkbox_Fields:
        if field_name in options:
            page.set_checked(f'#id_{prefix}{field_name}', options[field_name])

# ################################################################################################################################
# ################################################################################################################################
#
# Channel CRUD
#
# ################################################################################################################################
# ################################################################################################################################

def create_channel(
    page:'Page',
    base_url:'str',
    name:'str',
    service:'str',
    url_path:'str',
    options:'anydict | None'=None,
    ) -> 'str':
    """ Creates a REST channel via the UI and returns its server-side ID.
    """

    # Navigate to the REST channels page ..
    open_channel_page(page, base_url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. combine the base fields with any extra options ..
    form_data = {
        'name': name,
        'url_path': url_path,
        'service': service,
    } # type: anydict

    if options:
        form_data.update(options)

    # .. default to no security definition unless the caller chose one ..
    if 'security' not in form_data:
        if 'security_value' not in form_data:
            form_data['security_value'] = ZATO_NONE

    # .. fill the form ..
    fill_channel_form(page, form_data)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. wait for the row and return the channel's ID.
    _ = wait_for_channel_row(page, name)

    out = get_channel_id(page, name)
    return out

# ################################################################################################################################

def open_edit_dialog(page:'Page', channel_id:'str') -> 'None':
    """ Opens the edit dialog for a channel of the given ID.
    """

    # Call the page's JS edit function ..
    page.evaluate(f'$.fn.zato.http_soap.edit("{channel_id}")')

    # .. and wait for the dialog to appear.
    page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################

def edit_channel(page:'Page', channel_id:'str', options:'anydict') -> 'None':
    """ Opens the edit dialog for a channel, applies the given changes and submits the form.
    """

    # Open the dialog ..
    open_edit_dialog(page, channel_id)

    # .. apply the changes ..
    fill_channel_form(page, options, 'edit-')

    # .. and submit.
    submit_edit_form(page)

# ################################################################################################################################

def delete_channel(page:'Page', channel_id:'str') -> 'None':
    """ Deletes a channel via the UI confirmation dialog.
    """

    # Trigger the delete confirmation ..
    page.evaluate(f'$.fn.zato.http_soap.delete_("{channel_id}")')
    page.wait_for_selector('#popup_container', state='visible', timeout=5000)

    # .. confirm ..
    page.click('#popup_ok')

    # .. and wait for the row removal animation.
    page.wait_for_selector(f'#tr_{channel_id}', state='detached', timeout=5000)

# ################################################################################################################################

def submit_create_form_expect_blocked(page:'Page') -> 'None':
    """ Clicks submit on the create form and asserts the dialog stays open,
    which is what happens when client-side validation blocks the submission.
    """

    # Click submit ..
    page.click('#create-div input[type="submit"]')

    # .. give the synchronous uniqueness check a moment to complete ..
    page.wait_for_timeout(1000)

    # .. and confirm the dialog is still there.
    dialog = page.query_selector('#create-div')
    assert dialog.is_visible(), 'Expected the create dialog to remain open after a blocked submission'

# ################################################################################################################################
# ################################################################################################################################
#
# REST client
#
# ################################################################################################################################
# ################################################################################################################################

def invoke_channel(
    server_port:'int',
    url_path:'str',
    *,
    method:'str'='POST',
    data:'any_'=None,
    json_data:'anydict | None'=None,
    params:'anydict | None'=None,
    headers:'anydict | None'=None,
    auth:'any_'=None,
    ) -> 'Response':
    """ Invokes a REST channel over HTTP and returns the raw response.
    """

    url = f'http://127.0.0.1:{server_port}{url_path}'

    out = requests.request(
        method,
        url,
        data=data,
        json=json_data,
        params=params,
        headers=headers,
        auth=auth,
        timeout=10,
    )

    logger.info('[invoke_channel] %s %s -> status=%d', method, url_path, out.status_code)

    return out

# ################################################################################################################################

def invoke_until_status(
    server_port:'int',
    url_path:'str',
    expected_status:'int',
    *,
    timeout:'int'=10,
    **invoke_kwargs:'any_',
    ) -> 'Response':
    """ Invokes a REST channel until it returns the expected status code, which covers
    the short window between a UI change and its propagation to the server.
    Returns the last response, letting the caller assert on the status themselves.
    """

    deadline = time.monotonic() + timeout

    while True:
        out = invoke_channel(server_port, url_path, **invoke_kwargs)

        # Stop as soon as we see the expected status ..
        if out.status_code == expected_status:
            break

        # .. or when the deadline passes, in which case the caller's assertion will fail with details.
        if time.monotonic() >= deadline:
            break

        time.sleep(0.5)

    return out

# ################################################################################################################################
# ################################################################################################################################
#
# Hot deployment
#
# ################################################################################################################################
# ################################################################################################################################

# The introspection service reports everything a channel passed to it, which lets tests
# assert data formats, URL parameter handling and priorities precisely.
Introspection_Service_Name = 'test.rest.introspect'

Introspection_Service_Source = '''
# -*- coding: utf-8 -*-

# stdlib
from json import dumps

# Zato
from zato.server.service import Service

class Introspect(Service):
    """ Returns the details of the incoming request as JSON for REST channel tests.
    """

    name = 'test.rest.introspect'

    def handle(self):

        payload = self.request.payload
        if isinstance(payload, bytes):
            payload = payload.decode('utf-8')

        out = {
            'payload': payload,
            'form_data': self.request.http.get_form_data(),
            'http_method': self.request.http.method,
            'query_string_params': dict(self.request.http.GET),
            'path_params': dict(self.request.http.params),
            'channel_params': dict(self.request.channel_params),
        }

        self.response.payload = dumps(out)
        self.response.content_type = 'application/json'
'''.lstrip()

# ################################################################################################################################

def deploy_service_file(server_dir:'str', file_name:'str', source:'str') -> 'str':
    """ Writes a service module into the server's hot-deploy pickup directory and returns its path.
    """

    pickup_directory = os.path.join(server_dir, 'pickup', 'incoming', 'services')
    file_path = os.path.join(pickup_directory, file_name)

    with open(file_path, 'w') as service_file:
        _ = service_file.write(source)

    logger.info('[deploy_service_file] wrote %s', file_path)

    out = file_path
    return out

# ################################################################################################################################

def wait_for_service_in_dialog(page:'Page', base_url:'str', service_name:'str') -> 'None':
    """ Polls the create dialog's service select until a hot-deployed service appears in it.
    """

    deadline = time.monotonic() + _Service_Deploy_Timeout

    while time.monotonic() < deadline:

        # Reload the page so the select is rebuilt with the latest services ..
        open_channel_page(page, base_url)
        open_create_dialog(page)

        # .. check whether the service is now among the options ..
        found = page.evaluate(f'''
        (() => {{
            var select = document.querySelector('#id_service');
            for (var idx = 0; idx < select.options.length; idx++) {{
                if (select.options[idx].value === '{service_name}') {{
                    return true;
                }}
            }}
            return false;
        }})()
        ''')

        # .. close the dialog either way ..
        page.evaluate('$("#create-div").dialog("close")')
        page.wait_for_function('!document.querySelector("#create-div").offsetParent')

        if found:
            logger.info('[wait_for_service_in_dialog] found %s', service_name)
            return

        time.sleep(_Service_Poll_Interval)

    raise Exception(f'Service `{service_name}` did not appear in the service select within {_Service_Deploy_Timeout}s')

# ################################################################################################################################
# ################################################################################################################################
#
# Security definitions and groups
#
# ################################################################################################################################
# ################################################################################################################################

def _create_definition_on_page(page:'Page', base_url:'str', page_url:'str', fields:'anydict') -> 'None':
    """ Creates a security definition through the standard list-page create dialog.
    """

    # Navigate to the definition list page ..
    navigate_to_page(page, base_url, page_url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. fill in the fields ..
    for field_name, value in fields.items():
        page.fill(f'#id_{field_name}', value)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. and wait for the row to appear.
    name = fields['name']
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=5000)

# ################################################################################################################################

def create_apikey_definition(page:'Page', base_url:'str', name:'str', header:'str'=API_Key.Default_Header) -> 'anydict':
    """ Creates an API key security definition via the UI and returns its details.
    """

    key = 'key.' + os.urandom(8).hex()

    fields = {
        'name': name,
        'header': header,
        'password': key,
    }

    _create_definition_on_page(page, base_url, '/zato/security/apikey/?cluster=1', fields)

    out = {
        'name': name,
        'header': header,
        'key': key,
    }

    return out

# ################################################################################################################################

def create_ntlm_definition(page:'Page', base_url:'str', name:'str') -> 'anydict':
    """ Creates an NTLM security definition via the UI and returns its details.
    """

    username = 'DOMAIN\\\\user.' + name
    password = 'password.' + os.urandom(8).hex()

    fields = {
        'name': name,
        'username': username,
        'password': password,
    }

    _create_definition_on_page(page, base_url, '/zato/security/ntlm/?cluster=1', fields)

    out = {
        'name': name,
        'username': username,
        'password': password,
    }

    return out

# ################################################################################################################################

def create_bearer_token_definition(page:'Page', base_url:'str', name:'str') -> 'anydict':
    """ Creates a Bearer token security definition via the UI and returns its details.
    """

    username = 'client.' + os.urandom(8).hex()
    secret = 'secret.' + os.urandom(8).hex()

    # The client ID is required by the form's client-side validation
    fields = {
        'name': name,
        'username': username,
        'secret': secret,
    }

    _create_definition_on_page(page, base_url, '/zato/security/oauth/outconn/client-credentials/?cluster=1', fields)

    out = {
        'name': name,
        'username': username,
        'secret': secret,
    }

    return out

# ################################################################################################################################

def create_security_group(page:'Page', base_url:'str', name:'str', member_names:'strlistnone'=None) -> 'None':
    """ Creates an API clients security group via the UI, assigning the given members through the badge picker.
    """

    # Navigate to the groups page ..
    navigate_to_page(page, base_url, '/zato/groups/group/zato-api-creds/?cluster=1')

    # .. open the create dialog ..
    page.evaluate('$.fn.zato.groups.create()')
    page.wait_for_selector('#create-div', state='visible', timeout=5000)

    # .. fill in the name ..
    page.fill('#id_name', name)

    # .. assign the requested members via the badge picker ..
    if member_names:

        # Wait for the badges to load first ..
        page.wait_for_function(
            'document.querySelectorAll("#badge-zone-available-create .badge-zone-body .security-badge").length >= 1',
            timeout=10000
        )

        # .. and click each requested badge to move it to the assigned zone.
        for member_name in member_names:
            badge_selector = f'#badge-zone-available-create .badge-zone-body .security-badge[data-name="{member_name}"]'
            badge = page.query_selector(badge_selector)
            assert badge is not None, f'Could not find badge for member `{member_name}`'
            badge.click()

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. and wait for the group's row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=5000)

# ################################################################################################################################
# ################################################################################################################################
