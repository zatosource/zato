# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.soap.client import SOAPClient
from zato.common.soap.common import SOAPVersion
from zato.common.soap.message import SOAPMessage

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

from audit_toggle import assert_checkbox_exists, get_audit_row_count, get_checkbox_state
from rest_channel import open_edit_dialog
from soap_channel import create_soap_channel, edit_soap_channel, open_soap_channel_page, \
    wait_for_channel_fixture_services
from zato.common.test.playwright_pubsub import close_dialog_via_jquery, open_create_dialog

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.soap.audit.toggle.' + CryptoManager.generate_hex_string(32) + '.'

# The fixture service this suite's channels point to, deployed during server boot
_Echo_Service = 'test.soap.channel.echo'

# The SOAPAction the echo service's operation is invoked with
_Echo_Soap_Action = 'urn:cdc:iisb:2014:connectivityTest'
_Echo_Namespace   = 'urn:cdc:iisb:2014'
_Echo_Operation   = 'connectivityTest'

_Audit_Source = 'soap-channel'

# How long to keep retrying an invocation while a UI change propagates to the server
_Propagation_Timeout = 30

# How long to sleep between the attempts above
_Propagation_Poll_Interval = 1.0

# ################################################################################################################################
# ################################################################################################################################

def _invoke_echo(server_port:'int', url_path:'str', marker:'str') -> 'None':
    """ Invokes a SOAP channel once with an echoBack marker, retrying while the change
    made a moment ago in the browser propagates to the server. Until it does, the URL
    is unknown, so no invocation ever runs against a stale channel configuration.
    """

    message = SOAPMessage()
    message.namespace = _Echo_Namespace
    message.echoBack = marker

    client_config = {
        'address': f'http://127.0.0.1:{server_port}{url_path}',
        'timeout': 10,
        'soap_version': SOAPVersion.V11,
        'soap_action': _Echo_Soap_Action,
    } # type: anydict

    client = SOAPClient(client_config)

    deadline = time.monotonic() + _Propagation_Timeout
    last_error = None

    try:
        while time.monotonic() < deadline:
            try:
                response = client.invoke(_Echo_Operation, message)
            except Exception as invoke_error:
                last_error = invoke_error
                time.sleep(_Propagation_Poll_Interval)
            else:
                echoed = response.connectivityTestResponse.echoed
                assert echoed == marker, f'Expected the echo back "{marker}", got: {echoed!r}'
                return

        raise Exception(f'Could not invoke `{url_path}` within {_Propagation_Timeout}s, last error: {last_error!r}')
    finally:
        client.close()

# ################################################################################################################################
# ################################################################################################################################

class TestSOAPChannelAuditToggle:
    """ The per-channel audit log toggle of SOAP channels - the checkbox is on by default
    and turning it off stops audit events while the channel keeps serving traffic.
    """

    def test_checkbox_defaults(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        wait_for_channel_fixture_services(page, base_url)

        # The create dialog has the checkbox and it is on by default ..
        open_soap_channel_page(page, base_url)
        open_create_dialog(page)

        assert_checkbox_exists(page, '#id_is_audit_log_active')
        assert get_checkbox_state(page, '#id_is_audit_log_active') is True, \
            'Expected the audit log checkbox to be on by default in the create dialog'

        close_dialog_via_jquery(page, 'create-div')

        # .. and a channel created with the default carries it into the edit dialog.
        channel_name = _Test_Name_Prefix + 'defaults'
        channel_id = create_soap_channel(page, base_url, channel_name, _Echo_Service, '/' + channel_name, {
            'soap_action': _Echo_Soap_Action,
        })

        open_edit_dialog(page, channel_id)

        assert_checkbox_exists(page, '#id_edit-is_audit_log_active')
        assert get_checkbox_state(page, '#id_edit-is_audit_log_active') is True, \
            'Expected the audit log checkbox to be on in the edit dialog of a default channel'

        close_dialog_via_jquery(page, 'edit-div')

# ################################################################################################################################

    def test_toggle_gates_events(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)

        # Create a channel with the toggle on and invoke it once ..
        channel_name = _Test_Name_Prefix + 'gates'
        url_path_on = '/' + channel_name

        channel_id = create_soap_channel(page, base_url, channel_name, _Echo_Service, url_path_on, {
            'soap_action': _Echo_Soap_Action,
        })

        _invoke_echo(server_port, url_path_on, 'audit-on')

        # .. the invocation produced its two events ..
        row_count = get_audit_row_count(page, base_url, _Audit_Source, channel_name)
        assert row_count == 2, f'Expected 2 audit log rows with the toggle on, got {row_count}'

        # .. turn the toggle off, moving the channel to a new URL path so the first
        # invocation that succeeds on that path is guaranteed to run under the new
        # configuration - the flag and the path are applied together. The edit dialog
        # lives on the channels page, which the audit log page navigated away from ..
        open_soap_channel_page(page, base_url)

        url_path_off = url_path_on + '.off'
        edit_soap_channel(page, channel_id, {
            'is_audit_log_active': False,
            'url_path': url_path_off,
        })

        _invoke_echo(server_port, url_path_off, 'audit-off')

        # .. the traffic went through but no new events were recorded ..
        row_count = get_audit_row_count(page, base_url, _Audit_Source, channel_name)
        assert row_count == 2, f'Expected still 2 audit log rows with the toggle off, got {row_count}'

        # .. turn the toggle back on the same way ..
        open_soap_channel_page(page, base_url)

        url_path_back_on = url_path_on + '.back-on'
        edit_soap_channel(page, channel_id, {
            'is_audit_log_active': True,
            'url_path': url_path_back_on,
        })

        _invoke_echo(server_port, url_path_back_on, 'audit-back-on')

        # .. and the events resumed.
        row_count = get_audit_row_count(page, base_url, _Audit_Source, channel_name)
        assert row_count == 4, f'Expected 4 audit log rows after turning the toggle back on, got {row_count}'

# ################################################################################################################################
# ################################################################################################################################
