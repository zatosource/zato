# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.test import rand_string

# Test support
from audit_toggle import assert_checkbox_exists, get_checkbox_state
from outgoing_fhir import create_fhir_connection, delete_fhir_connection, get_audit_log_cell_text, get_fhir_conn_id, \
    open_create_dialog, open_edit_dialog, open_fhir_page, set_audit_log_active
from zato.common.test.playwright_pubsub import close_dialog_via_jquery

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.fhir.outconn.audit.toggle.' + rand_string() + '.'

# The FHIR server the connections point at - nothing is ever sent to it
_Address = 'http://127.0.0.1:31999/fhir/r4'

# What the Audit log cell says when the log is off
_Off_Marker = '(off)'

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingFHIRAuditToggle:
    """ The per-connection audit log box of outgoing FHIR connections - on by default,
    it can be ticked off and back on and the listing says which it is.
    """

    def test_checkbox_defaults(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The create dialog has the box and it is on by default ..
        open_fhir_page(page, base_url)
        open_create_dialog(page)

        assert_checkbox_exists(page, '#id_is_audit_log_active')
        assert get_checkbox_state(page, '#id_is_audit_log_active') is True, \
            'Expected the audit log checkbox to be on by default in the create dialog'

        close_dialog_via_jquery(page, 'create-div')

        # .. and a connection created with the default carries it into the edit dialog and the listing.
        name = _Test_Name_Prefix + 'defaults'
        create_fhir_connection(page, name, _Address)
        conn_id = get_fhir_conn_id(page, name)

        try:
            open_edit_dialog(page, conn_id)

            assert_checkbox_exists(page, '#id_edit-is_audit_log_active')
            assert get_checkbox_state(page, '#id_edit-is_audit_log_active') is True, \
                'Expected the audit log checkbox to be on in the edit dialog of a default connection'

            close_dialog_via_jquery(page, 'edit-div')

            assert _Off_Marker not in get_audit_log_cell_text(page, name)

        finally:
            delete_fhir_connection(page, conn_id)

# ################################################################################################################################

    def test_toggle_off_and_back_on(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        open_fhir_page(page, base_url)

        name = _Test_Name_Prefix + 'toggle'
        create_fhir_connection(page, name, _Address)
        conn_id = get_fhir_conn_id(page, name)

        try:

            # Ticked off, the edit dialog reads it back off and the listing says so ..
            set_audit_log_active(page, conn_id, False)

            open_edit_dialog(page, conn_id)
            assert get_checkbox_state(page, '#id_edit-is_audit_log_active') is False, \
                'Expected the audit log checkbox to be off after it was ticked off'
            close_dialog_via_jquery(page, 'edit-div')

            assert _Off_Marker in get_audit_log_cell_text(page, name)

            # .. the page reloaded still says so ..
            open_fhir_page(page, base_url)
            assert _Off_Marker in get_audit_log_cell_text(page, name)

            # .. and ticked back on, both go back to where they were.
            set_audit_log_active(page, conn_id, True)

            open_edit_dialog(page, conn_id)
            assert get_checkbox_state(page, '#id_edit-is_audit_log_active') is True, \
                'Expected the audit log checkbox to be on after it was ticked back on'
            close_dialog_via_jquery(page, 'edit-div')

            assert _Off_Marker not in get_audit_log_cell_text(page, name)

            open_fhir_page(page, base_url)
            assert _Off_Marker not in get_audit_log_cell_text(page, name)

        finally:
            delete_fhir_connection(page, conn_id)

# ################################################################################################################################
# ################################################################################################################################
