# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# pytest
import pytest

# Zato
from zato.common.api import ZATO_NONE
from zato.common.test import rand_string
from zato.common.test.playwright_pubsub import create_topic, open_create_dialog, submit_create_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

from declarative import fill_rest_invocation_tabs, fill_soap_invocation_tabs
from http_test_server import HTTPTestServer
from rest_outconn import fill_outconn_form, get_outconn_id, open_edit_dialog as open_rest_edit_dialog, open_outconn_page, \
    wait_for_outconn_row
from soap_outconn import fill_soap_outconn_form, get_soap_outconn_id, open_edit_dialog as open_soap_edit_dialog, \
    open_soap_outconn_page, wait_for_soap_outconn_row

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.outconn.callback.topic.select.' + rand_string() + '.'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture()
def http_test_server() -> 'any_':
    """ A live recording HTTP server the connections point at, so pings always succeed.
    """

    server = HTTPTestServer()
    server.start()

    yield server

    server.stop()

# ################################################################################################################################
# ################################################################################################################################

def _assert_topic_selects(page:'Page', prefix:'str', topic_name:'str') -> 'None':
    """ Asserts that both topic callback widgets of an open dialog are selects
    whose options include the given topic.
    """

    for field_name in ('callback_topic', 'health_check_callback_topic'):

        selector = f'#id_{prefix}{field_name}'

        # The widget is a select, not a text input ..
        tag_name = page.eval_on_selector(selector, 'element => element.tagName')
        assert tag_name == 'SELECT', f'Expected {selector} to be a select, got: {tag_name}'

        # .. and the topic is among its options.
        option_values = page.eval_on_selector_all(f'{selector} option', 'options => options.map(option => option.value)')
        assert topic_name in option_values, f'Expected topic "{topic_name}" among the options of {selector}, got: {option_values}'

# ################################################################################################################################

def _assert_edit_topic_callbacks(page:'Page', topic_name:'str') -> 'None':
    """ Asserts that an open edit dialog carries the stored topic callbacks on both tabs.
    """

    assert page.input_value('#id_edit-callback_type') == 'topic'
    assert page.input_value('#id_edit-callback_topic') == topic_name

    assert page.input_value('#id_edit-health_check_callback_type') == 'topic'
    assert page.input_value('#id_edit-health_check_callback_topic') == topic_name

# ################################################################################################################################

def _close_edit_dialog(page:'Page') -> 'None':
    """ Closes an open edit dialog without saving.
    """

    page.click('#edit-div button:has-text("Cancel")')
    _ = page.wait_for_selector('#edit-div', state='hidden', timeout=5000)

# ################################################################################################################################
# ################################################################################################################################

class TestOutconnCallbackTopicSelect:
    """ Tests that the topic callback widgets of outgoing REST and SOAP connections are selects
    populated with the pub/sub topics that exist, on both the Callback and the Health check tab.
    """

# ################################################################################################################################

    def test_rest_topic_callback_select_round_trip(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        http_test_server:'HTTPTestServer',
        ) -> 'None':
        """ The REST create form offers topics in selects, a connection created with topic
        callbacks on both tabs round-trips them back into the edit form's selects.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'rest'
        url_path = '/test/callback-topic-select/' + rand_string()

        # Create the topic the callbacks publish to ..
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'rest-topic')
        topic_name = topic['name']

        # .. a fresh page load renders the create form with the topic among the choices ..
        open_outconn_page(page, base_url)
        open_create_dialog(page)

        _assert_topic_selects(page, '', topic_name)

        # .. create a connection with topic callbacks on both tabs ..
        fill_outconn_form(page, {
            'name': name,
            'host': http_test_server.address,
            'url_path': url_path,
            'security_value': ZATO_NONE,
        })

        fill_rest_invocation_tabs(page, {
            'callback_type': 'topic',
            'callback_name': topic_name,
            'health_check_run_every': '30',
            'health_check_run_unit': 'minutes',
            'health_check_callback_type': 'topic',
            'health_check_callback_name': topic_name,
        }, 'create')

        submit_create_form(page)
        _ = wait_for_outconn_row(page, name)

        outconn_id = get_outconn_id(page, name)

        # .. reload so the row is server-rendered and reopen the edit dialog ..
        open_outconn_page(page, base_url)
        open_rest_edit_dialog(page, outconn_id)

        # .. the edit form's topic widgets are selects with the topic among their options ..
        _assert_topic_selects(page, 'edit-', topic_name)

        # .. and both tabs carry the stored topic.
        _assert_edit_topic_callbacks(page, topic_name)

        _close_edit_dialog(page)

# ################################################################################################################################

    def test_soap_topic_callback_select_round_trip(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        http_test_server:'HTTPTestServer',
        ) -> 'None':
        """ The SOAP create form offers topics in selects, a connection created with topic
        callbacks on both tabs round-trips them back into the edit form's selects.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'soap'

        # Create the topic the callbacks publish to ..
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'soap-topic')
        topic_name = topic['name']

        # .. a fresh page load renders the create form with the topic among the choices ..
        open_soap_outconn_page(page, base_url)
        open_create_dialog(page)

        _assert_topic_selects(page, '', topic_name)

        # .. create a connection with topic callbacks on both tabs ..
        fill_soap_outconn_form(page, {
            'name': name,
            'host': http_test_server.address,
            'security_value': ZATO_NONE,
        })

        fill_soap_invocation_tabs(page, {
            'callback_type': 'topic',
            'callback_name': topic_name,
            'health_check_run_every': '30',
            'health_check_run_unit': 'minutes',
            'health_check_callback_type': 'topic',
            'health_check_callback_name': topic_name,
        }, 'create')

        submit_create_form(page)
        _ = wait_for_soap_outconn_row(page, name)

        outconn_id = get_soap_outconn_id(page, name)

        # .. reload so the row is server-rendered and reopen the edit dialog ..
        open_soap_outconn_page(page, base_url)
        open_soap_edit_dialog(page, outconn_id)

        # .. the edit form's topic widgets are selects with the topic among their options ..
        _assert_topic_selects(page, 'edit-', topic_name)

        # .. and both tabs carry the stored topic.
        _assert_edit_topic_callbacks(page, topic_name)

        _close_edit_dialog(page)

# ################################################################################################################################
# ################################################################################################################################
