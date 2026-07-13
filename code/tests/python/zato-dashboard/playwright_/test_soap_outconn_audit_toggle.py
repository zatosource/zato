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
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

from audit_toggle import assert_checkbox_exists, get_audit_row_count, get_checkbox_state
from http_test_server import HTTPTestServer
from soap_outconn import create_soap_outconn, edit_soap_outconn, invoke_soap_outconn_from_ide, open_edit_dialog, \
    open_soap_outconn_page, ping_soap_outconn, wait_for_soap_invoker_service
from zato.common.test.playwright_pubsub import close_dialog_via_jquery, open_create_dialog

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.soap.outconn.audit.toggle.' + CryptoManager.generate_hex_string(32) + '.'

_Audit_Source = 'soap-outgoing'

# The operation invoked and the marker the static response envelope carries back
_Operation = 'connectivityTest'
_Namespace = 'urn:cdc:iisb:2014'
_Static_Echo = 'static-toggle-response'

# The recording server answers every invocation with this bare SOAP 1.1 envelope
_Static_Envelope = f'''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <connectivityTestResponse xmlns="{_Namespace}">
      <echoed>{_Static_Echo}</echoed>
    </connectivityTestResponse>
  </soap:Body>
</soap:Envelope>'''

# How long to keep retrying while a UI change propagates to the server
_Propagation_Timeout = 30

# How long to sleep between the attempts above
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
    out = f'/test/soap/outconn/audit-toggle-{name_suffix}/' + CryptoManager.generate_hex_string()
    return out

# ################################################################################################################################

def _invoke_once(page:'Page', base_url:'str', outconn_name:'str', marker:'str') -> 'None':
    """ Invokes the connection once through the pre-deployed invoker service, retrying
    while a freshly created connection propagates to the server. Until then the service
    reports the connection as unknown without ever reaching the wrapper, so the one
    invocation that succeeds is also the only one the audit log may see.
    """

    deadline = time.monotonic() + _Propagation_Timeout
    last_error = None

    while time.monotonic() < deadline:

        result = invoke_soap_outconn_from_ide(page, base_url, outconn_name, _Operation,
            namespace=_Namespace,
            fields={'echoBack': marker},
            response_fields=['echoed'],
        )

        if 'fields' in result:
            echoed = result['fields']['echoed']
            assert echoed == _Static_Echo, f'Expected the static echo "{_Static_Echo}", got: {result}'
            return

        last_error = result
        time.sleep(_Propagation_Poll_Interval)

    raise Exception(f'Could not invoke `{outconn_name}` within {_Propagation_Timeout}s, last error: {last_error}')

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

        _ = ping_soap_outconn(page, outconn_name)

        for record in http_test_server.recorded_requests:
            if record['path'] == url_path:
                http_test_server.clear_requests()
                return

        time.sleep(_Propagation_Poll_Interval)

    raise Exception(f'The server was not pinged on `{url_path}` within {_Propagation_Timeout}s')

# ################################################################################################################################
# ################################################################################################################################

class TestSOAPOutconnAuditToggle:
    """ The per-connection audit log toggle of outgoing SOAP connections - the checkbox
    is on by default and turning it off stops audit events while traffic continues.
    """

    def test_checkbox_defaults(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The create dialog has the checkbox and it is on by default ..
        open_soap_outconn_page(page, base_url)
        open_create_dialog(page)

        assert_checkbox_exists(page, '#id_is_audit_log_active')
        assert get_checkbox_state(page, '#id_is_audit_log_active') is True, \
            'Expected the audit log checkbox to be on by default in the create dialog'

        close_dialog_via_jquery(page, 'create-div')

        # .. and a connection created with the default carries it into the edit dialog.
        outconn_name = _Test_Name_Prefix + 'defaults'
        outconn_id = create_soap_outconn(page, base_url, outconn_name, http_test_server.address, {
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

        wait_for_soap_invoker_service(page, base_url)

        # Every invocation, on any path, receives the same static response envelope
        url_path_on = _new_url_path('on')
        url_path_off = _new_url_path('off')
        url_path_back_on = _new_url_path('back-on')

        for url_path in (url_path_on, url_path_off, url_path_back_on):
            http_test_server.set_response(url_path, body=_Static_Envelope)

        # Create a connection with the toggle on and invoke it once ..
        outconn_name = _Test_Name_Prefix + 'gates'
        outconn_id = create_soap_outconn(page, base_url, outconn_name, http_test_server.address, {
            'url_path': url_path_on,
        })

        _invoke_once(page, base_url, outconn_name, 'audit-on')

        # .. the invocation produced its two events ..
        row_count = get_audit_row_count(page, base_url, _Audit_Source, outconn_name)
        assert row_count == 2, f'Expected 2 audit log rows with the toggle on, got {row_count}'

        # .. turn the toggle off, moving the connection to a new URL path and pinging
        # until the recording server sees that path, which proves the new configuration
        # is live before any audited traffic runs ..
        open_soap_outconn_page(page, base_url)

        edit_soap_outconn(page, outconn_id, {
            'is_audit_log_active': False,
            'url_path': url_path_off,
        })

        _wait_until_pinged_on(page, http_test_server, outconn_name, url_path_off)

        # .. invoke once more - the traffic goes through but no new events are recorded ..
        _invoke_once(page, base_url, outconn_name, 'audit-off')

        row_count = get_audit_row_count(page, base_url, _Audit_Source, outconn_name)
        assert row_count == 2, f'Expected still 2 audit log rows with the toggle off, got {row_count}'

        # .. turn the toggle back on the same way ..
        open_soap_outconn_page(page, base_url)

        edit_soap_outconn(page, outconn_id, {
            'is_audit_log_active': True,
            'url_path': url_path_back_on,
        })

        _wait_until_pinged_on(page, http_test_server, outconn_name, url_path_back_on)

        # .. and the events resumed.
        _invoke_once(page, base_url, outconn_name, 'audit-back-on')

        row_count = get_audit_row_count(page, base_url, _Audit_Source, outconn_name)
        assert row_count == 4, f'Expected 4 audit log rows after turning the toggle back on, got {row_count}'

# ################################################################################################################################
# ################################################################################################################################
