# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.test import rand_string
from zato.common.test.playwright_pubsub import close_dialog_via_jquery, create_topic, navigate_to_page, \
    open_create_dialog, open_publish_overlay, publish_via_overlay

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

from audit_toggle import assert_checkbox_exists, get_audit_row_count, get_checkbox_state

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.pubsub.audit.toggle.' + rand_string() + '.'

_Topic_Page_Url = '/zato/pubsub/topic/?cluster=1'

_Audit_Source = 'pubsub'

# How long a topic config event needs to reach every server after a form submission
_Config_Propagation_Delay = 2.0

# ################################################################################################################################
# ################################################################################################################################

def _open_edit_dialog(page:'Page', base_url:'str', topic_name:'str') -> 'None':
    """ Opens the edit dialog of one topic through its row's edit link.
    """

    navigate_to_page(page, base_url, _Topic_Page_Url)

    row_selector = f'#data-table tbody tr:has(td:text-is("{topic_name}"))'
    page.click(f'{row_selector} a:text-is("Edit")')
    _ = page.wait_for_selector('#edit-div', state='visible')

# ################################################################################################################################

def _edit_audit_flag(page:'Page', base_url:'str', topic_name:'str', is_audit_log_active:'bool') -> 'None':
    """ Sets the audit log checkbox of one topic through the edit dialog and waits
    for the config event to reach the servers - the toggle travels asynchronously
    and there is no externally observable acknowledgment, hence the fixed delay.
    """

    # Open the edit dialog ..
    _open_edit_dialog(page, base_url, topic_name)

    # .. flip the checkbox ..
    page.set_checked('#id_edit-is_audit_log_active', is_audit_log_active)

    # .. submit and wait for the dialog to close ..
    page.click('#edit-div input[type="submit"]')
    _ = page.wait_for_selector('#edit-div', state='hidden', timeout=10000)

    # .. and let the config event propagate.
    time.sleep(_Config_Propagation_Delay)

# ################################################################################################################################

def _publish_one(page:'Page', base_url:'str', item_id:'str', payload:'str') -> 'None':
    """ Publishes one message to a topic through the dashboard overlay,
    navigating back to the topic page first because the overlay lives there.
    """

    navigate_to_page(page, base_url, _Topic_Page_Url)

    open_publish_overlay(page, item_id)
    publish_via_overlay(page, payload)

# ################################################################################################################################
# ################################################################################################################################

class TestPubSubAuditToggle:
    """ The per-topic audit log toggle - the checkbox is on by default and turning it off
    stops audit events while messages continue to be published.
    """

    def test_checkbox_defaults(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The create dialog has the checkbox and it is on by default ..
        navigate_to_page(page, base_url, _Topic_Page_Url)
        open_create_dialog(page)

        assert_checkbox_exists(page, '#id_is_audit_log_active')
        assert get_checkbox_state(page, '#id_is_audit_log_active') is True, \
            'Expected the audit log checkbox to be on by default in the create dialog'

        close_dialog_via_jquery(page, 'create-div')

        # .. and a topic created with the default carries it into the edit dialog.
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'defaults')
        _open_edit_dialog(page, base_url, topic['name'])

        assert_checkbox_exists(page, '#id_edit-is_audit_log_active')
        assert get_checkbox_state(page, '#id_edit-is_audit_log_active') is True, \
            'Expected the audit log checkbox to be on in the edit dialog of a default topic'

        close_dialog_via_jquery(page, 'edit-div')

# ################################################################################################################################

    def test_toggle_gates_events(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a topic with the toggle on and publish one message ..
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'gates')
        topic_name = topic['name']
        item_id = topic['item_id']

        # .. a freshly created topic also needs its config event to arrive everywhere ..
        time.sleep(_Config_Propagation_Delay)

        _publish_one(page, base_url, item_id, '{"toggle":"audit-on"}')

        # .. the publication produced its event ..
        row_count = get_audit_row_count(page, base_url, _Audit_Source, topic_name)
        assert row_count == 1, f'Expected 1 audit log row with the toggle on, got {row_count}'

        # .. turn the toggle off and publish again - the message goes through
        # .. but no new event is recorded ..
        _edit_audit_flag(page, base_url, topic_name, False)
        _publish_one(page, base_url, item_id, '{"toggle":"audit-off"}')

        row_count = get_audit_row_count(page, base_url, _Audit_Source, topic_name)
        assert row_count == 1, f'Expected still 1 audit log row with the toggle off, got {row_count}'

        # .. turn the toggle back on ..
        _edit_audit_flag(page, base_url, topic_name, True)
        _publish_one(page, base_url, item_id, '{"toggle":"audit-back-on"}')

        # .. and the events resumed.
        row_count = get_audit_row_count(page, base_url, _Audit_Source, topic_name)
        assert row_count == 2, f'Expected 2 audit log rows after turning the toggle back on, got {row_count}'

# ################################################################################################################################
# ################################################################################################################################
