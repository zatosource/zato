# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

# pytest
import pytest

# Zato
from zato.common.test import rand_string

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

from audit_toggle import assert_checkbox_exists, get_audit_row_count, get_checkbox_state
from rest_channel import create_channel, edit_channel, invoke_until_status, open_channel_page, open_edit_dialog
from zato.common.test.playwright_pubsub import close_dialog_via_jquery, open_create_dialog

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.rest.audit.toggle.' + rand_string() + '.'

_Echo_Service = 'demo.echo'

_Audit_Source = 'rest-channel'

# ################################################################################################################################
# ################################################################################################################################

def _new_url_path(name_suffix:'str') -> 'str':
    out = f'/test/rest/audit/toggle/{name_suffix}/' + rand_string()
    return out

# ################################################################################################################################

def _invoke_ok(server_port:'int', url_path:'str', payload:'str') -> 'None':
    """ Invokes a REST channel once, waiting out the short window between a change
    made in the UI and its propagation to the server. Until the change is live,
    the URL is unknown to the server, so no invocation runs against a stale channel.
    """
    response = invoke_until_status(server_port, url_path, OK, data=payload)
    assert response.status_code == OK, f'Expected OK, got {response.status_code}: {response.text}'

# ################################################################################################################################
# ################################################################################################################################

class TestRESTChannelAuditToggle:
    """ The per-channel audit log toggle of REST channels - the checkbox is on by default
    and turning it off stops audit events while the channel keeps serving traffic.
    """

    def test_checkbox_defaults(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The create dialog has the checkbox and it is on by default ..
        open_channel_page(page, base_url)
        open_create_dialog(page)

        assert_checkbox_exists(page, '#id_is_audit_log_active')
        assert get_checkbox_state(page, '#id_is_audit_log_active') is True, \
            'Expected the audit log checkbox to be on by default in the create dialog'

        close_dialog_via_jquery(page, 'create-div')

        # .. and a channel created with the default carries it into the edit dialog.
        channel_name = _Test_Name_Prefix + 'defaults'
        channel_id = create_channel(page, base_url, channel_name, _Echo_Service, _new_url_path('defaults'), {
            'data_format': 'json',
        })

        open_edit_dialog(page, channel_id)

        assert_checkbox_exists(page, '#id_edit-is_audit_log_active')
        assert get_checkbox_state(page, '#id_edit-is_audit_log_active') is True, \
            'Expected the audit log checkbox to be on in the edit dialog of a default channel'

        close_dialog_via_jquery(page, 'edit-div')

# ################################################################################################################################

    # Moving a documented endpoint to a new URL path is a breaking change the servers report on rebuild
    @pytest.mark.expect_log_errors('OpenAPI breaking change:')
    def test_toggle_gates_events(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        # Create a channel with the toggle on and invoke it once ..
        channel_name = _Test_Name_Prefix + 'gates'
        url_path_on = _new_url_path('on')

        channel_id = create_channel(page, base_url, channel_name, _Echo_Service, url_path_on, {
            'data_format': 'json',
        })

        _invoke_ok(server_port, url_path_on, '{"toggle":"audit-on"}')

        # .. the invocation produced its two events ..
        row_count = get_audit_row_count(page, base_url, _Audit_Source, channel_name)
        assert row_count == 2, f'Expected 2 audit log rows with the toggle on, got {row_count}'

        # .. turn the toggle off, moving the channel to a new URL path so the first
        # invocation that succeeds on that path is guaranteed to run under the new
        # configuration - the flag and the path are applied together. The edit dialog
        # lives on the channels page, which the audit log page navigated away from ..
        open_channel_page(page, base_url)

        url_path_off = _new_url_path('off')
        edit_channel(page, channel_id, {
            'is_audit_log_active': False,
            'url_path': url_path_off,
        })

        _invoke_ok(server_port, url_path_off, '{"toggle":"audit-off"}')

        # .. the traffic went through but no new events were recorded ..
        row_count = get_audit_row_count(page, base_url, _Audit_Source, channel_name)
        assert row_count == 2, f'Expected still 2 audit log rows with the toggle off, got {row_count}'

        # .. turn the toggle back on the same way ..
        open_channel_page(page, base_url)

        url_path_back_on = _new_url_path('back-on')
        edit_channel(page, channel_id, {
            'is_audit_log_active': True,
            'url_path': url_path_back_on,
        })

        _invoke_ok(server_port, url_path_back_on, '{"toggle":"audit-back-on"}')

        # .. and the events resumed.
        row_count = get_audit_row_count(page, base_url, _Audit_Source, channel_name)
        assert row_count == 4, f'Expected 4 audit log rows after turning the toggle back on, got {row_count}'

# ################################################################################################################################
# ################################################################################################################################
