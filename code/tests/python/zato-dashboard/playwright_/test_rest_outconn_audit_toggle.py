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
from zato.common.test import rand_string

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

from audit_toggle import assert_checkbox_exists, get_audit_row_count, get_checkbox_state
from http_test_server import HTTPTestServer
from rest_outconn import create_outconn, edit_outconn, invoke_outconn_via_overlay, open_edit_dialog, \
    open_outconn_page, ping_outconn, ping_outconn_until_success
from zato.common.test.playwright_pubsub import close_dialog_via_jquery, open_create_dialog

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.rest.outconn.audit.toggle.' + rand_string() + '.'

_Audit_Source = 'rest-outgoing'

# How long to keep pinging while a UI change propagates to the server
_Propagation_Timeout = 30

# How long to sleep between the pings above
_Propagation_Poll_Interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture()
def http_test_server() -> 'any_':
    """ A live recording HTTP server for the duration of a single test.
    """

    server = HTTPTestServer()
    server.start()

    yield server

    server.stop()

# ################################################################################################################################
# ################################################################################################################################

def _new_url_path(name_suffix:'str') -> 'str':
    out = f'/test/outconn/audit-toggle-{name_suffix}/' + rand_string()
    return out

# ################################################################################################################################

def _wait_until_pinged_on(
    page:'Page',
    http_test_server:'HTTPTestServer',
    outconn_name:'str',
    url_path:'str',
    ) -> 'None':
    """ Keeps pinging a connection until the recording server sees a request on the given
    URL path, which proves an edit made a moment ago in the browser reached the server -
    the flag and the path are applied together and pings are never audited, so this
    wait itself records no events. The recorded ping traffic is forgotten at the end.
    """

    deadline = time.monotonic() + _Propagation_Timeout

    while time.monotonic() < deadline:

        _ = ping_outconn(page, outconn_name)

        for record in http_test_server.recorded_requests:
            if record['path'] == url_path:
                http_test_server.clear_requests()
                return

        time.sleep(_Propagation_Poll_Interval)

    raise Exception(f'The server was not pinged on `{url_path}` within {_Propagation_Timeout}s')

# ################################################################################################################################
# ################################################################################################################################

class TestRESTOutconnAuditToggle:
    """ The per-connection audit log toggle of outgoing REST connections - the checkbox
    is on by default and turning it off stops audit events while traffic continues.
    """

    def test_checkbox_defaults(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The create dialog has the checkbox and it is on by default ..
        open_outconn_page(page, base_url)
        open_create_dialog(page)

        assert_checkbox_exists(page, '#id_is_audit_log_active')
        assert get_checkbox_state(page, '#id_is_audit_log_active') is True, \
            'Expected the audit log checkbox to be on by default in the create dialog'

        close_dialog_via_jquery(page, 'create-div')

        # .. and a connection created with the default carries it into the edit dialog.
        outconn_name = _Test_Name_Prefix + 'defaults'
        outconn_id = create_outconn(page, base_url, outconn_name, http_test_server.address, {
            'url_path': _new_url_path('defaults'),
        })

        open_edit_dialog(page, outconn_id)

        assert_checkbox_exists(page, '#id_edit-is_audit_log_active')
        assert get_checkbox_state(page, '#id_edit-is_audit_log_active') is True, \
            'Expected the audit log checkbox to be on in the edit dialog of a default connection'

        close_dialog_via_jquery(page, 'edit-div')

# ################################################################################################################################

    def test_toggle_gates_events(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a connection with the toggle on and wait for it to propagate via ping ..
        outconn_name = _Test_Name_Prefix + 'gates'
        url_path_on = _new_url_path('on')

        outconn_id = create_outconn(page, base_url, outconn_name, http_test_server.address, {
            'url_path': url_path_on,
        })

        ping_result = ping_outconn_until_success(page, outconn_name)
        assert ping_result['is_success'], f'Expected a successful ping, got: {ping_result}'
        http_test_server.clear_requests()

        # .. invoke it once through the overlay ..
        http_test_server.set_response(url_path_on, body='{"received": "audit-on-response"}')
        result = invoke_outconn_via_overlay(page, outconn_id, request_body='{"toggle": "audit-on"}', method='POST')
        assert 'audit-on-response' in result['response'], f'Expected the server response, got: {result}'

        # .. the invocation produced its two events ..
        row_count = get_audit_row_count(page, base_url, _Audit_Source, outconn_name)
        assert row_count == 2, f'Expected 2 audit log rows with the toggle on, got {row_count}'

        # .. turn the toggle off, moving the connection to a new URL path and pinging
        # until the recording server sees that path, which proves the new configuration
        # is live before any audited traffic runs ..
        open_outconn_page(page, base_url)

        url_path_off = _new_url_path('off')
        edit_outconn(page, outconn_id, {
            'is_audit_log_active': False,
            'url_path': url_path_off,
        })

        _wait_until_pinged_on(page, http_test_server, outconn_name, url_path_off)

        # .. invoke once more - the traffic goes through but no new events are recorded ..
        http_test_server.set_response(url_path_off, body='{"received": "audit-off-response"}')
        result = invoke_outconn_via_overlay(page, outconn_id, request_body='{"toggle": "audit-off"}', method='POST')
        assert 'audit-off-response' in result['response'], f'Expected the server response, got: {result}'

        row_count = get_audit_row_count(page, base_url, _Audit_Source, outconn_name)
        assert row_count == 2, f'Expected still 2 audit log rows with the toggle off, got {row_count}'

        # .. turn the toggle back on the same way ..
        open_outconn_page(page, base_url)

        url_path_back_on = _new_url_path('back-on')
        edit_outconn(page, outconn_id, {
            'is_audit_log_active': True,
            'url_path': url_path_back_on,
        })

        _wait_until_pinged_on(page, http_test_server, outconn_name, url_path_back_on)

        # .. and the events resumed.
        http_test_server.set_response(url_path_back_on, body='{"received": "audit-back-on-response"}')
        result = invoke_outconn_via_overlay(page, outconn_id, request_body='{"toggle": "audit-back-on"}', method='POST')
        assert 'audit-back-on-response' in result['response'], f'Expected the server response, got: {result}'

        row_count = get_audit_row_count(page, base_url, _Audit_Source, outconn_name)
        assert row_count == 4, f'Expected 4 audit log rows after turning the toggle back on, got {row_count}'

# ################################################################################################################################
# ################################################################################################################################
