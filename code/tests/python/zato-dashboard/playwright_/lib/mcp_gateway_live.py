# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import subprocess
import tempfile
import time
from base64 import b64encode
from http.client import OK

# requests
import requests

# Zato
from zato.common.api import Groups
from zato.common.crypto.api import CryptoManager
from zato.common.test.mcp_ import make_jsonrpc_initialize
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from requests import Response
    from zato.common.typing_ import any_, anydict, intlist, strdict, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

# The service the gateways of the live suites expose
Echo_Service = 'demo.echo'

# Gateways create their security group under this prefix followed by the gateway name
Group_Name_Prefix = 'mcp.'

# The generic connection type of MCP gateways
Gateway_Type = 'gateway-mcp'

# How long a saved change has to reach live enforcement, in seconds
Propagation_Timeout = 20
Propagation_Poll_Interval = 0.5

# How long to wait after a refused save before concluding that no redirect follows, in milliseconds
Refusal_Wait = 3000

# Timeout of the HTTP requests of the tests, in seconds
HTTP_Timeout = 10

# How long one enmasse command may run, in seconds
Enmasse_Timeout = 120

# What the server logs when it refuses a request through a security group
Group_Log_Patterns = (
    'Invalid bearer token (groups)',
    'Invalid Basic Auth credentials (groups)',
    'Received neither Basic Auth, bearer token nor API key (groups)',
)

# The group-name uniqueness probe of the groups page logs this whenever a group is edited through the UI
Group_Edit_Log_Patterns = ('nDetails: ··· Error ···',)

# What the dashboard shows a refused form submission in
_failure_message_selector = '#user-message.user-message-failure'

# ################################################################################################################################
# ################################################################################################################################
#
# Names
#
# ################################################################################################################################
# ################################################################################################################################

def make_url_path(label:'str') -> 'str':
    """ Returns a URL path no other test uses, e.g. /mcp/groups-live/rename/1a2b3c4d.
    """
    suffix = CryptoManager.generate_hex_string(8)

    out = f'/mcp/{label}/{suffix}'
    return out

# ################################################################################################################################
# ################################################################################################################################
#
# The admin API, read-only
#
# ################################################################################################################################
# ################################################################################################################################

def invoke_admin(zato_dashboard:'anydict', service_name:'str', payload:'anydict') -> 'any_':
    """ Invokes a read-only admin service and returns its response.
    """
    server_port = zato_dashboard['server_port']

    api_url = f'http://127.0.0.1:{server_port}/zato/api/invoke/{service_name}'
    api_auth = ('admin.invoke', zato_dashboard['password'])

    response = requests.post(api_url, data=json.dumps(payload), auth=api_auth, timeout=HTTP_Timeout)
    assert response.status_code == OK, f'{service_name} -> {response.status_code} -> {response.text}'

    out = response.json()
    return out

# ################################################################################################################################

def get_group_id_by_name(zato_dashboard:'anydict', group_name:'str') -> 'strnone':
    """ Returns the id of the security group of the given name, or None if there is no such group.
    """
    group_list = invoke_admin(zato_dashboard, 'zato.groups.get-list', {'group_type': Groups.Type.API_Clients})

    out:'strnone' = None

    for group in group_list:
        if group['name'] == group_name:
            out = group['id']
            break

    return out

# ################################################################################################################################

def get_group_id(zato_dashboard:'anydict', gateway_name:'str') -> 'strnone':
    """ Returns the id of the gateway's own security group, or None if there is no such group.
    """
    group_name = Group_Name_Prefix + gateway_name

    out = get_group_id_by_name(zato_dashboard, group_name)
    return out

# ################################################################################################################################

def get_group_member_names_by_name(zato_dashboard:'anydict', group_name:'str') -> 'strlist':
    """ Returns the sorted names of the security definitions in the security group of the given name.
    """
    group_id = get_group_id_by_name(zato_dashboard, group_name)
    assert group_id, f'Expected group `{group_name}` to exist'

    member_list = invoke_admin(zato_dashboard, 'zato.groups.get-member-list', {
        'group_type': Groups.Type.API_Clients,
        'group_id': group_id,
    })

    out:'strlist' = []

    for member in member_list:
        out.append(member['name'])

    out.sort()
    return out

# ################################################################################################################################

def get_group_member_names(zato_dashboard:'anydict', gateway_name:'str') -> 'strlist':
    """ Returns the sorted names of the security definitions in the gateway's own group.
    """
    group_name = Group_Name_Prefix + gateway_name

    out = get_group_member_names_by_name(zato_dashboard, group_name)
    return out

# ################################################################################################################################

def get_gateway_names(zato_dashboard:'anydict') -> 'strlist':
    """ Returns the names of all the stored MCP gateways.
    """
    gateway_list = invoke_admin(zato_dashboard, 'zato.generic.connection.get-list', {'type_': Gateway_Type})

    out:'strlist' = []

    for item in gateway_list:
        out.append(item['name'])

    return out

# ################################################################################################################################

def get_channel(zato_dashboard:'anydict', channel_name:'str') -> 'anydict':
    """ Returns the stored REST channel of the given name.
    """
    channel_list = invoke_admin(zato_dashboard, 'zato.http-soap.get-list', {
        'connection': 'channel',
        'transport': 'plain_http',
    })

    for item in channel_list:
        if item['name'] == channel_name:
            return item

    raise Exception(f'Channel `{channel_name}` not found')

# ################################################################################################################################

def get_channel_group_ids(zato_dashboard:'anydict', channel_name:'str') -> 'intlist':
    """ Returns the ids of the security groups the REST channel of the given name lists.
    """
    channel = get_channel(zato_dashboard, channel_name)

    out:'intlist' = []

    if security_groups := channel['security_groups']:
        for group_id in security_groups:
            out.append(int(group_id))

    return out

# ################################################################################################################################
# ################################################################################################################################
#
# Enmasse
#
# ################################################################################################################################
# ################################################################################################################################

def run_enmasse_import(zato_dashboard:'anydict', yaml_content:'str') -> 'subprocess.CompletedProcess':
    """ Imports the YAML content through the enmasse command and returns the completed process,
    leaving it to the caller to tell a successful import from a refused one.
    """
    server_dir = zato_dashboard['server_dir']

    zato_base_dir = os.environ['ZATO_TEST_BASE_DIR']
    zato_bin = os.path.join(zato_base_dir, 'code', 'bin', 'zato')

    enmasse_env = os.environ.copy()
    _ = enmasse_env.pop('COVERAGE_PROCESS_START', None)

    file_suffix = CryptoManager.generate_hex_string(8)
    input_path = os.path.join(tempfile.gettempdir(), f'zato-mcp-gateway-live-{os.getpid()}-{file_suffix}.yaml')

    with open(input_path, 'w') as input_file:
        _ = input_file.write(yaml_content)

    command = [zato_bin, 'enmasse', server_dir, '--verbose', '--import', '--input', input_path, '--missing-wait-time', '15']

    try:
        out = subprocess.run(command, capture_output=True, text=True, timeout=Enmasse_Timeout, env=enmasse_env)
    finally:
        os.remove(input_path)

    return out

# ################################################################################################################################

def import_enmasse(zato_dashboard:'anydict', yaml_content:'str') -> 'None':
    """ Imports the YAML content through the enmasse command and expects the import to succeed.
    """
    result = run_enmasse_import(zato_dashboard, yaml_content)
    assert result.returncode == 0, f'enmasse failed:\nstdout: {result.stdout}\nstderr: {result.stderr}'

# ################################################################################################################################
# ################################################################################################################################
#
# Calling gateways
#
# ################################################################################################################################
# ################################################################################################################################

def bearer_headers(token:'str') -> 'strdict':
    """ The Authorization header of a bearer token.
    """
    out = {'Authorization': f'Bearer {token}'}
    return out

# ################################################################################################################################

def basic_auth_headers(username:'str', password:'str') -> 'strdict':
    """ The Authorization header of Basic Auth credentials.
    """
    credentials = f'{username}:{password}'.encode('utf8')
    encoded = b64encode(credentials).decode('ascii')

    out = {'Authorization': f'Basic {encoded}'}
    return out

# ################################################################################################################################

def initialize(server_port:'int', url_path:'str', auth_headers:'strdict | None'=None) -> 'Response':
    """ Sends an MCP initialize request to the gateway, with the given credentials or with none at all.
    """
    headers = {'Content-Type': 'application/json'}

    if auth_headers:
        headers.update(auth_headers)

    url = f'http://127.0.0.1:{server_port}{url_path}'
    body = make_jsonrpc_initialize()

    out = requests.post(url, data=body, headers=headers, timeout=HTTP_Timeout)
    return out

# ################################################################################################################################

def initialize_until_status(
    server_port:'int',
    url_path:'str',
    auth_headers:'strdict | None',
    expected_status:'int',
    ) -> 'Response':
    """ Sends initialize requests until the expected status arrives, which covers the time a saved change
    takes to reach live enforcement. Returns the last response.
    """
    deadline = time.monotonic() + Propagation_Timeout

    while True:
        out = initialize(server_port, url_path, auth_headers)

        if out.status_code == expected_status:
            break

        if time.monotonic() >= deadline:
            break

        time.sleep(Propagation_Poll_Interval)

    return out

# ################################################################################################################################

def assert_status(server_port:'int', url_path:'str', auth_headers:'strdict | None', expected_status:'int') -> 'Response':
    """ Waits until the gateway answers initialize with the expected status and asserts that it did.
    """
    out = initialize_until_status(server_port, url_path, auth_headers, expected_status)
    assert out.status_code == expected_status, \
        f'Expected {expected_status} from {url_path}, got {out.status_code} -> {out.text}'

    return out

# ################################################################################################################################

def assert_channel_status(server_port:'int', url_path:'str', auth_headers:'strdict', expected_status:'int') -> 'None':
    """ Posts to a REST channel until it answers with the expected status and asserts that it did,
    which covers the time a saved change takes to reach live enforcement.
    """
    url = f'http://127.0.0.1:{server_port}{url_path}'
    deadline = time.monotonic() + Propagation_Timeout

    while True:
        response = requests.post(url, json={}, headers=auth_headers, timeout=HTTP_Timeout)

        if response.status_code == expected_status:
            break

        if time.monotonic() >= deadline:
            break

        time.sleep(Propagation_Poll_Interval)

    assert response.status_code == expected_status, \
        f'Expected {expected_status} from {url_path}, got {response.status_code} -> {response.text}'

# ################################################################################################################################

def post_session_request(
    server_port:'int',
    url_path:'str',
    auth_headers:'strdict',
    session_id:'str',
    method:'str',
    params:'anydict',
    ) -> 'Response':
    """ Sends one JSON-RPC request within an existing MCP session.
    """
    body = json.dumps({
        'jsonrpc': '2.0',
        'method': method,
        'id': 2,
        'params': params,
    })

    headers = {
        'Content-Type': 'application/json',
        'Mcp-Session-Id': session_id,
    }
    headers.update(auth_headers)

    url = f'http://127.0.0.1:{server_port}{url_path}'

    out = requests.post(url, data=body, headers=headers, timeout=HTTP_Timeout)
    return out

# ################################################################################################################################

def call_echo(server_port:'int', url_path:'str', auth_headers:'strdict') -> 'None':
    """ Opens a session with the credentials and calls the echo tool through it, asserting the arguments come back.
    """
    response = assert_status(server_port, url_path, auth_headers, OK)
    session_id = response.headers['Mcp-Session-Id']

    params = {'name': Echo_Service, 'arguments': {'customer': 'Maria Johnson'}}
    response = post_session_request(server_port, url_path, auth_headers, session_id, 'tools/call', params)
    assert response.status_code == OK, f'Expected OK for tools/call, got {response.status_code} -> {response.text}'

    content = response.json()['result']['content']
    echoed = json.loads(content[0]['text'])
    assert echoed == {'customer': 'Maria Johnson'}, echoed

# ################################################################################################################################

def list_tool_names(server_port:'int', url_path:'str', auth_headers:'strdict') -> 'strlist':
    """ Opens a session with the credentials and returns the names of the tools the gateway lists.
    """
    response = assert_status(server_port, url_path, auth_headers, OK)
    session_id = response.headers['Mcp-Session-Id']

    response = post_session_request(server_port, url_path, auth_headers, session_id, 'tools/list', {})
    assert response.status_code == OK, f'Expected OK for tools/list, got {response.status_code} -> {response.text}'

    out:'strlist' = []

    for tool in response.json()['result']['tools']:
        out.append(tool['name'])

    return out

# ################################################################################################################################
# ################################################################################################################################
#
# The dashboard
#
# ################################################################################################################################
# ################################################################################################################################

def post_from_page(page:'Page', url:'str', data:'anydict') -> 'anydict':
    """ Posts a form from within the page, with the session and the CSRF token of the page,
    and returns the status and the text of the response.
    """
    out = page.evaluate('''([url, data]) => new Promise((resolve) => {
        $.ajax({
            type: 'POST',
            url: url,
            data: data,
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            complete: (xhr) => resolve({'status': xhr.status, 'text': xhr.responseText})
        });
    })''', [url, data])

    return out

# ################################################################################################################################

def inline_edit(page:'Page', gateway_id:'str', data:'anydict') -> 'anydict':
    """ Posts one inline change of a gateway's row, as the list page does, and returns the response.
    """
    url = f'/zato/gateway/mcp/inline-edit/{gateway_id}/'

    out = post_from_page(page, url, data)
    return out

# ################################################################################################################################

def wait_for_failure_message(page:'Page') -> 'str':
    """ Waits until the dashboard shows that a form submission was refused and returns what it says.
    """
    message = page.wait_for_selector(_failure_message_selector, state='visible', timeout=HTTP_Timeout * 1000)
    message = cast_('any_', message)

    out = message.inner_text()
    return out

# ################################################################################################################################

def submit_refused_edit(page:'Page') -> 'str':
    """ Submits the edit dialog of a list page, expects the submission to be refused and returns the message.
    """
    page.click('#edit-div input[type="submit"]')

    out = wait_for_failure_message(page)
    return out

# ################################################################################################################################

def confirm_refused_delete(page:'Page') -> 'str':
    """ Confirms a delete on a list page, expects it to be refused and returns the message.
    """
    page.click('#popup_ok')

    out = wait_for_failure_message(page)
    return out

# ################################################################################################################################

def delete_gateway(page:'Page', base_url:'str', gateway_name:'str', gateway_id:'str') -> 'None':
    """ Deletes a gateway through its row on the list page.
    """
    list_url = f'/zato/gateway/mcp/?query={gateway_name}'
    _ = page.goto(base_url + list_url)

    page.evaluate(f'$.fn.zato.gateway.mcp.delete_("{gateway_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=HTTP_Timeout * 1000)

    page.click('#popup_ok')
    _ = page.wait_for_selector(f'#tr_{gateway_id}', state='detached', timeout=HTTP_Timeout * 1000)

# ################################################################################################################################

def delete_group(page:'Page', base_url:'str', group_id:'str') -> 'None':
    """ Deletes a security group through its row on the groups page.
    """
    _ = page.goto(base_url + '/zato/groups/group/zato-api-creds/')

    page.evaluate(f'$.fn.zato.groups.delete_("{group_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=HTTP_Timeout * 1000)

    page.click('#popup_ok')
    _ = page.wait_for_selector(f'#tr_{group_id}', state='detached', timeout=HTTP_Timeout * 1000)

# ################################################################################################################################
# ################################################################################################################################
