# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import glob
import logging
import os
import time
from http.client import OK

# PyYAML
import yaml

# Zato
from zato.common.crypto.api import CryptoManager

from rest_channel import deploy_service_file, edit_channel, get_channel_id, find_channel_row, open_channel_page, \
    wait_for_channel_row

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, callable_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################
#
# Console URL paths and credentials
#
# ################################################################################################################################
# ################################################################################################################################

Console_Path       = '/openapi/console'
Console_Login_Path = '/openapi/console/login'
Spec_JSON_Path     = '/openapi/console/openapi.json'
Spec_YAML_Path     = '/openapi/console/openapi.yaml'
Relay_Base_Path    = '/openapi/console/relay'

# The console's admin is the Dashboard's own admin user, with the same username and password
Admin_Username = 'admin'

# ################################################################################################################################
# ################################################################################################################################
#
# The suite's fixture services and their auto-created channels
#
# ################################################################################################################################
# ################################################################################################################################

Service_Typed      = 'api.test.openapi.typed.get-user'
Service_Untyped    = 'api.test.openapi.untyped.echo'
Service_Methods    = 'api.test.openapi.methods.multi'
Service_Prestarted = 'api.test.openapi.prestarted.ping'
Service_Diffing    = 'api.test.openapi.diffing.contract'

Path_Typed      = '/api/api/test/openapi/typed/get-user'
Path_Untyped    = '/api/api/test/openapi/untyped/echo'
Path_Methods    = '/api/api/test/openapi/methods/multi'
Path_Prestarted = '/api/api/test/openapi/prestarted/ping'
Path_Diffing    = '/api/api/test/openapi/diffing/contract'

# The file that carries all the fixture services, both at boot and during redeployments
Fixture_Services_File_Name = 'openapi_console_test_services.py'

# What a service without typed input or output is documented with - any JSON object
Any_Object_Schema = {'type': 'object', 'additionalProperties': True}

# A valid request for the typed fixture service, with all the required fields
Typed_Request = {
    'username': 'openapi.test.user',
    'max_results': 5,
    'needs_details': True,
}

# The deterministic response the typed fixture service always replies with
Typed_Expected_Response = {
    'user_name': 'openapi.test.user',
    'user_id': 123,
    'is_manager': True,
    'address': {'street': '25 Integration Street', 'city': 'Testville'},
    'role_list': ['integration', 'testing'],
}

# ################################################################################################################################
# ################################################################################################################################

# How long to wait for a console sign-in to succeed while credentials propagate to the server
_Login_Timeout = 30

# How long to wait between sign-in attempts
_Login_Poll_Interval = 1.0

# How long to wait for the caller's document to match a condition
_Spec_Timeout = 30

# How long to wait between document fetches
_Spec_Poll_Interval = 0.5

# How long to wait for a hot-deployed channel change to show up in the channel list
_Deploy_Timeout = 90

# How long to wait between channel list reloads
_Deploy_Poll_Interval = 1.0

# The pickup listener deploys a given file at most once per its 2-second debounce window,
# so consecutive writes keep a slightly longer distance from each other.
_Listener_Debounce_Interval = 3

# How long to wait for an expected line to appear in the server logs
_Log_Timeout = 90

# How long to wait between log scans
_Log_Poll_Interval = 0.5

# ################################################################################################################################
# ################################################################################################################################
#
# Console session and document access
#
# ################################################################################################################################
# ################################################################################################################################

def console_login(page:'Page', console_url:'str', username:'str', password:'str', timeout:'int'=_Login_Timeout) -> 'None':
    """ Signs in to the console through its sign-in form, retrying while newly created
    credentials propagate to the server. Returns once the console page has rendered.
    """
    deadline = time.monotonic() + timeout

    while True:

        # Open the sign-in form ..
        _ = page.goto(console_url + Console_Login_Path)

        # .. fill in the credentials ..
        page.fill('#username', username)
        page.fill('#password', password)

        # .. submit the form - a success redirects to the console page,
        # a failure re-renders the form with an error message ..
        page.click('.console-login-button')
        page.wait_for_selector('.console-header, .console-login-error', state='visible', timeout=10000)

        # .. the console header renders only after a successful sign-in ..
        if page.query_selector('.console-header'):
            return

        # .. otherwise, the credentials may not have reached the server yet, so try again.
        if time.monotonic() >= deadline:
            raise Exception(f'Could not sign in to the console as `{username}` within {timeout}s')

        time.sleep(_Login_Poll_Interval)

# ################################################################################################################################

def get_spec_response(page:'Page', console_url:'str') -> 'any_':
    """ Fetches the JSON document endpoint inside the signed-in session and returns the raw response.
    """
    out = page.request.get(console_url + Spec_JSON_Path)

    return out

# ################################################################################################################################

def get_spec_json(page:'Page', console_url:'str') -> 'anydict':
    """ Fetches the signed-in caller's document as JSON and returns it parsed.
    """
    response = get_spec_response(page, console_url)
    assert response.status == OK, f'Expected OK from the JSON document endpoint, got {response.status}: {response.text()}'

    out = response.json()

    return out

# ################################################################################################################################

def get_spec_yaml(page:'Page', console_url:'str') -> 'anydict':
    """ Fetches the signed-in caller's document as YAML and returns it parsed.
    """
    response = page.request.get(console_url + Spec_YAML_Path)
    assert response.status == OK, f'Expected OK from the YAML document endpoint, got {response.status}: {response.text()}'

    out = yaml.safe_load(response.text())

    return out

# ################################################################################################################################

def wait_for_spec(page:'Page', console_url:'str', condition:'callable_', timeout:'int'=_Spec_Timeout) -> 'anydict':
    """ Polls the JSON document endpoint until the condition holds, covering the window between
    a Dashboard change and its propagation to the servers. Returns the matching document.
    """
    deadline = time.monotonic() + timeout

    while True:
        out = get_spec_json(page, console_url)

        # The condition holds, so the change has propagated ..
        if condition(out):
            return out

        # .. otherwise, keep polling until the deadline.
        if time.monotonic() >= deadline:
            paths = sorted(out['paths'])
            raise Exception(f'Document did not match the condition within {timeout}s, last paths: {paths}')

        time.sleep(_Spec_Poll_Interval)

# ################################################################################################################################

def spec_paths(spec:'anydict') -> 'any_':
    """ Returns the set of URL paths a document describes.
    """
    out = set(spec['paths'])

    return out

# ################################################################################################################################

def spec_schema_names(spec:'anydict') -> 'any_':
    """ Returns the set of component schema names a document carries.
    """
    out = set(spec['components']['schemas'])

    return out

# ################################################################################################################################

def relay_invoke(page:'Page', console_url:'str', method:'str', url_path:'str', body:'str'='') -> 'any_':
    """ Sends a try-it request through the console's relay inside the signed-in session
    and returns the raw response.
    """
    url = console_url + Relay_Base_Path + url_path

    if body:
        out = page.request.fetch(url, method=method, data=body)
    else:
        out = page.request.fetch(url, method=method)

    return out

# ################################################################################################################################
# ################################################################################################################################
#
# Channel setup through the Dashboard
#
# ################################################################################################################################
# ################################################################################################################################

def edit_channel_by_name(page:'Page', dashboard_url:'str', name:'str', options:'anydict') -> 'str':
    """ Opens the channel list filtered down to the given name, applies the edits through
    the edit dialog and returns the channel's server-side ID.
    """
    # Navigate to the channel's row ..
    open_channel_page(page, dashboard_url, query=name)
    _ = wait_for_channel_row(page, name)

    # .. and apply the changes through the edit dialog.
    channel_id = get_channel_id(page, name)
    edit_channel(page, channel_id, options)

    out = channel_id

    return out

# ################################################################################################################################

def wait_for_channel_row_reloading(page:'Page', dashboard_url:'str', name:'str', timeout:'int'=_Deploy_Timeout) -> 'any_':
    """ Reloads the channel list until a row with the given name appears and returns that row -
    used after hot-deployments, whose completion is not observable from the UI alone.
    """
    deadline = time.monotonic() + timeout

    while True:

        # Reload the filtered channel list ..
        open_channel_page(page, dashboard_url, query=name)

        # .. and stop as soon as the row is there.
        if row := find_channel_row(page, name):
            out = row
            return out

        if time.monotonic() >= deadline:
            raise Exception(f'Channel `{name}` did not appear within {timeout}s')

        time.sleep(_Deploy_Poll_Interval)

# ################################################################################################################################
# ################################################################################################################################
#
# Hot-deployment of the fixture services
#
# ################################################################################################################################
# ################################################################################################################################

def read_fixture_services_source() -> 'str':
    """ Returns the source of the module with all the fixture services.
    """
    lib_dir = os.path.dirname(__file__)
    fixtures_path = os.path.join(lib_dir, '..', 'openapi_console', 'fixtures', 'services', Fixture_Services_File_Name)

    with open(fixtures_path) as fixtures_file:
        out = fixtures_file.read()

    return out

# ################################################################################################################################

def redeploy_fixture_services(server_dir:'str', source:'str') -> 'None':
    """ Writes the fixture services module into the pickup directory with a unique marker appended,
    so the file's content always differs and the deployment is never skipped as unchanged.
    """
    # The pickup listener debounces deployments per file and silently drops a write that lands
    # within its debounce window after the previous deployment, so the window is waited out first.
    time.sleep(_Listener_Debounce_Interval)

    marker = CryptoManager.generate_hex_string()
    source = source + f'\n# Redeploy marker {marker}\n'

    _ = deploy_service_file(server_dir, Fixture_Services_File_Name, source)

# ################################################################################################################################
# ################################################################################################################################
#
# Server log scanning
#
# ################################################################################################################################
# ################################################################################################################################

def snapshot_log_offsets(logs_dir:'str') -> 'anydict':
    """ Returns the current size of each log file in the directory, for a later scan
    to consider only the content written after this point.
    """
    out = {}

    log_files = glob.glob(os.path.join(logs_dir, '*.log'))

    for log_file in log_files:
        out[log_file] = os.path.getsize(log_file)

    return out

# ################################################################################################################################

def wait_for_log_line(logs_dir:'str', offsets:'anydict', fragment:'str', timeout:'int'=_Log_Timeout) -> 'str':
    """ Polls the log files for a line containing the fragment, considering only the content
    written after the given offsets, and returns the first matching line.
    """
    deadline = time.monotonic() + timeout

    while True:

        # Scan every log file's new content for the fragment ..
        for log_file, offset in offsets.items():

            with open(log_file, encoding='utf-8', errors='replace') as log_handle:
                _ = log_handle.seek(offset)
                new_content = log_handle.read()

            for line in new_content.splitlines():
                if fragment in line:
                    out = line
                    return out

        # .. and keep polling until the deadline.
        if time.monotonic() >= deadline:
            raise Exception(f'No log line containing `{fragment}` appeared within {timeout}s')

        time.sleep(_Log_Poll_Interval)

# ################################################################################################################################
# ################################################################################################################################
