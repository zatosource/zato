# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging

# Zato
from zato.common.api import ZATO_NONE
from zato.common.test import rand_string
from zato.common.test.playwright_pubsub import close_dialog_via_jquery, navigate_to_page, open_create_dialog, \
    submit_create_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

from declarative import activate_rest_tab
from rest_outconn import fill_outconn_form, get_outconn_id, open_edit_dialog, open_outconn_page, wait_for_outconn_row

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.rest.outconn.tabsui.' + rand_string() + '.'

# Connections in this module are never invoked so the host does not need to exist
_Test_Host = 'http://127.0.0.1:1'

# The REST channels page - the same view as outgoing connections, with a different connection type
_Channel_Page_Url = '/zato/http-soap/?cluster=1&connection=channel&transport=plain_http'

# The rows of the query string parameters in the create dialog
_Query_Rows_Selector = '#request-query_string-rows-create .request-param-row'

# ################################################################################################################################
# ################################################################################################################################

def _add_query_row_as_user(page:'Page', key:'str', value:'str') -> 'None':
    """ Adds a query-string parameter row the way a user would - by clicking the add link
    and typing into the new row's inputs.
    """

    # The query string cell has the first of the request tab's add links ..
    add_link = page.locator('#http-soap-create-tab-panel-request a:has-text("Add a parameter")').first
    add_link.click()

    # .. and the new row is the last one, ready to be typed into.
    new_row = page.locator(_Query_Rows_Selector).last
    new_row.locator('.request-param-key').fill(key)
    new_row.locator('.request-param-value').fill(value)

# ################################################################################################################################
# ################################################################################################################################

class TestRESTOutconnTabsUI:
    """ Tests for the tabbed UI itself - channels keep the plain form, rows can be removed
    via their x badge and the Text/JSONata toggle is driven the way a user would.
    """

# ################################################################################################################################

    def test_channels_show_plain_form_without_tabs(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        ) -> 'None':
        """ The create dialog of REST channels has no tabs at all - the declarative
        invocation profile belongs to outgoing connections only.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Open the create dialog on the channels page ..
        navigate_to_page(page, base_url, _Channel_Page_Url)
        open_create_dialog(page)

        # .. the plain form is there ..
        name_input = page.query_selector('#create-div #id_name')
        assert name_input.is_visible(), 'Expected the plain create form on the channels page'

        # .. with no tab headers and no tab panels anywhere in the dialog.
        tabs = page.query_selector_all('#create-div .dashboard-tab')
        assert not tabs, f'Expected no tabs on the channels page, got {len(tabs)}'

        panels = page.query_selector_all('#create-div .dashboard-tab-panel')
        assert not panels, f'Expected no tab panels on the channels page, got {len(panels)}'

        close_dialog_via_jquery(page, 'create-div')

# ################################################################################################################################

    def test_row_removed_via_x_badge(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        ) -> 'None':
        """ A parameter row is removed by clicking its x badge and only the remaining
        rows are saved with the connection.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'row-removal'
        url_path = '/test/declarative/tabs-ui/' + rand_string()

        # Fill the Config tab ..
        open_outconn_page(page, base_url)
        open_create_dialog(page)

        fill_outconn_form(page, {
            'name': name,
            'host': _Test_Host,
            'url_path': url_path,
            'security_value': ZATO_NONE,
        })

        # .. add two query-string rows the way a user would ..
        activate_rest_tab(page, 'create', 'request')

        _add_query_row_as_user(page, 'dropped', 'value-1')
        _add_query_row_as_user(page, 'kept', 'value-2')

        rows = page.query_selector_all(_Query_Rows_Selector)
        assert len(rows) == 2, f'Expected two rows before removal, got {len(rows)}'

        # .. remove the first row via its x badge ..
        page.click(f'{_Query_Rows_Selector}:nth-child(1) .request-param-remove')

        # .. only the second row remains in the dialog ..
        rows = page.query_selector_all(_Query_Rows_Selector)
        assert len(rows) == 1, f'Expected one row after removal, got {len(rows)}'

        remaining_key = page.input_value(f'{_Query_Rows_Selector} .request-param-key')
        assert remaining_key == 'kept', f'Expected the second row to remain, got: "{remaining_key}"'

        # .. and only that row is saved with the connection.
        activate_rest_tab(page, 'create', 'config')
        submit_create_form(page)
        _ = wait_for_outconn_row(page, name)

        outconn_id = get_outconn_id(page, name)
        open_edit_dialog(page, outconn_id)

        query_rows = json.loads(page.input_value('#id_edit-request_query_string'))
        assert query_rows == [{'key': 'kept', 'value': 'value-2', 'mode': 'text'}], \
            f'Expected only the remaining row to be saved, got: {query_rows}'

        page.click('#edit-div button:has-text("Cancel")')
        page.wait_for_selector('#edit-div', state='hidden', timeout=5000)

# ################################################################################################################################

    def test_jsonata_toggle_flips_row_mode(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        ) -> 'None':
        """ Clicking a row's Text/JSONata toggle the way a user would flips the row's mode,
        which is then saved with the connection.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'jsonata-toggle'
        url_path = '/test/declarative/tabs-ui/' + rand_string()

        # Fill the Config tab ..
        open_outconn_page(page, base_url)
        open_create_dialog(page)

        fill_outconn_form(page, {
            'name': name,
            'host': _Test_Host,
            'url_path': url_path,
            'security_value': ZATO_NONE,
        })

        # .. add one row with a value that is a valid JSONata expression ..
        activate_rest_tab(page, 'create', 'request')
        _add_query_row_as_user(page, 'batch', '"batch" & "-" & "7"')

        # .. the row starts in text mode ..
        assert not page.is_checked(f'{_Query_Rows_Selector} .request-param-jsonata'), \
            'Expected a new row to start in text mode'

        # .. click the toggle the way a user would ..
        page.click(f'{_Query_Rows_Selector} .toggle-slider')

        assert page.is_checked(f'{_Query_Rows_Selector} .request-param-jsonata'), \
            'Expected the toggle click to flip the row to JSONata mode'

        # .. and the mode is saved with the connection.
        activate_rest_tab(page, 'create', 'config')
        submit_create_form(page)
        _ = wait_for_outconn_row(page, name)

        outconn_id = get_outconn_id(page, name)
        open_edit_dialog(page, outconn_id)

        query_rows = json.loads(page.input_value('#id_edit-request_query_string'))
        assert query_rows == [{'key': 'batch', 'value': '"batch" & "-" & "7"', 'mode': 'jsonata'}], \
            f'Expected the JSONata mode to be saved, got: {query_rows}'

        page.click('#edit-div button:has-text("Cancel")')
        page.wait_for_selector('#edit-div', state='hidden', timeout=5000)

# ################################################################################################################################
# ################################################################################################################################
