# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.test import rand_string

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

from rest_outconn import create_outconn, delete_outconn, edit_outconn, find_outconn_row, get_outconn_id, \
    get_row_cell_texts, get_row_hidden_cell_texts, open_edit_dialog, open_outconn_page, \
    submit_create_form_expect_blocked, wait_for_outconn_row

from zato.common.test.playwright_pubsub import open_create_dialog

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.rest.outconn.crud.' + rand_string() + '.'

# Fake hosts for CRUD tests - nothing connects to them since pings are never clicked here
_Test_Host = 'http://rest-crud.example.com:8080'
_Test_Host_Edited = 'http://rest-crud-edited.example.com:8181'

# Row cell indexes for outgoing REST connection rows
_Cell_Name = 2
_Cell_Is_Active = 3
_Cell_Host = 4
_Cell_Url_Path = 5
_Cell_Security = 6
_Cell_Data_Format = 11
_Cell_Timeout = 12
_Cell_Validate_TLS = 13
_Cell_Ping_Method = 14
_Cell_Pool_Size = 15
_Cell_Content_Type = 17
_Cell_Audit_Log = 18
_Cell_Edit = 19
_Cell_Delete = 20
_Cell_Ping = 21
_Cell_Invoke = 22

# Defaults the create form arrives with
_Default_Ping_Method = 'HEAD'
_Default_Pool_Size = '20'
_Default_Timeout = '10'

# ################################################################################################################################
# ################################################################################################################################

class TestRESTOutconnCRUD:
    """ Tests for outgoing REST connection create, edit and delete via the web admin UI.
    """

# ################################################################################################################################

    def test_page_loads(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Navigates to the outgoing REST connections page and verifies its structure.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the outgoing REST connections page ..
        open_outconn_page(page, base_url)

        # .. verify the page heading ..
        heading = page.query_selector('h2.zato')
        heading_text = heading.inner_text()
        assert 'REST outgoing connections' in heading_text, \
            f'Expected "REST outgoing connections" in heading, got: {heading_text}'

        # .. verify the create link is present ..
        create_link = page.query_selector('#markup .page_prompt a')
        create_link_text = create_link.inner_text()
        assert 'Create a new REST outgoing connection' in create_link_text, \
            f'Expected create link text, got: {create_link_text}'

        # .. the OpenAPI import link is specific to this page ..
        openapi_link = page.query_selector('#openapi-import-link')
        assert openapi_link is not None, 'Expected the OpenAPI import link on the outgoing REST page'

        # .. and verify the table headers.
        headers = page.query_selector_all('#data-table thead th a')

        header_texts:'anylist' = []

        for header in headers:
            raw_text = header.inner_text()
            text = raw_text.strip().lower()
            header_texts.append(text)

        for expected in ('name', 'active', 'host', 'url path', 'security'):
            assert expected in header_texts, f'Expected "{expected}" in headers, got: {header_texts}'

# ################################################################################################################################

    def test_create_minimal(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an outgoing connection with the minimal set of fields, then verifies
        the row's visible columns and the defaults stored in the hidden ones.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'minimal'
        url_path = '/test/outconn/minimal/' + rand_string()

        # Create the connection ..
        _ = create_outconn(page, base_url, outconn_name, _Test_Host, {
            'url_path': url_path,
        })

        # .. reload the page so the row is server-rendered ..
        open_outconn_page(page, base_url)

        # .. read the row cells ..
        row = find_outconn_row(page, outconn_name)
        cells = get_row_cell_texts(row)
        hidden_cells = get_row_hidden_cell_texts(row)

        logger.info('[test_create_minimal] cells=%s hidden_cells=%s', cells, hidden_cells)

        # .. verify the visible columns ..
        assert cells[_Cell_Name] == outconn_name, f'Expected name "{outconn_name}", got: "{cells[_Cell_Name]}"'
        assert cells[_Cell_Is_Active] == 'Yes', f'Expected is_active "Yes", got: "{cells[_Cell_Is_Active]}"'
        assert cells[_Cell_Host] == _Test_Host, f'Expected host "{_Test_Host}", got: "{cells[_Cell_Host]}"'
        assert cells[_Cell_Url_Path] == url_path, f'Expected url_path "{url_path}", got: "{cells[_Cell_Url_Path]}"'
        assert cells[_Cell_Security] == '---', f'Expected no security definition, got: "{cells[_Cell_Security]}"'
        assert cells[_Cell_Edit] == 'Edit', f'Expected the edit link, got: "{cells[_Cell_Edit]}"'
        assert cells[_Cell_Delete] == 'Delete', f'Expected the delete link, got: "{cells[_Cell_Delete]}"'
        assert cells[_Cell_Ping] == 'Ping', f'Expected the ping link, got: "{cells[_Cell_Ping]}"'
        assert cells[_Cell_Invoke] == 'Invoke', f'Expected the invoke link, got: "{cells[_Cell_Invoke]}"'

        # .. and the hidden columns carry the defaults the create form arrived with.
        assert hidden_cells[_Cell_Timeout] == _Default_Timeout, \
            f'Expected timeout "{_Default_Timeout}", got: "{hidden_cells[_Cell_Timeout]}"'
        assert hidden_cells[_Cell_Validate_TLS] == 'True', \
            f'Expected validate_tls "True", got: "{hidden_cells[_Cell_Validate_TLS]}"'
        assert hidden_cells[_Cell_Ping_Method] == _Default_Ping_Method, \
            f'Expected ping_method "{_Default_Ping_Method}", got: "{hidden_cells[_Cell_Ping_Method]}"'
        assert hidden_cells[_Cell_Pool_Size] == _Default_Pool_Size, \
            f'Expected pool_size "{_Default_Pool_Size}", got: "{hidden_cells[_Cell_Pool_Size]}"'

# ################################################################################################################################

    def test_create_full_roundtrip(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a connection with every field set to a non-default value, then reopens
        the edit dialog and verifies all of them persisted.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'full-roundtrip'
        url_path = '/test/outconn/full/' + rand_string()

        # Create the connection with non-default options ..
        outconn_id = create_outconn(page, base_url, outconn_name, _Test_Host, {
            'url_path': url_path,
            'data_format': 'json',
            'ping_method': 'GET',
            'pool_size': '5',
            'timeout': '3',
            'content_type': 'application/json',
            'validate_tls': 'False',
        })

        # .. reopen the edit dialog ..
        open_edit_dialog(page, outconn_id)

        # .. and verify each field kept its value.
        expected_values = {
            '#id_edit-name': outconn_name,
            '#id_edit-host': _Test_Host,
            '#id_edit-url_path': url_path,
            '#id_edit-data_format': 'json',
            '#id_edit-ping_method': 'GET',
            '#id_edit-pool_size': '5',
            '#id_edit-timeout': '3',
            '#id_edit-content_type': 'application/json',
            '#id_edit-validate_tls': 'False',
        }

        for selector, expected in expected_values.items():
            actual = page.input_value(selector)
            assert actual == expected, f'Expected {selector} to be "{expected}", got: "{actual}"'

# ################################################################################################################################

    def test_edit(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a connection, edits every editable field and verifies the row
        and the edit dialog both reflect the changes.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'edit'
        new_outconn_name = _Test_Name_Prefix + 'edit-renamed'

        old_url_path = '/test/outconn/edit-old/' + rand_string()
        new_url_path = '/test/outconn/edit-new/' + rand_string()

        # Create the connection ..
        outconn_id = create_outconn(page, base_url, outconn_name, _Test_Host, {
            'url_path': old_url_path,
        })

        # .. apply the changes ..
        edit_outconn(page, outconn_id, {
            'name': new_outconn_name,
            'host': _Test_Host_Edited,
            'url_path': new_url_path,
            'ping_method': 'POST',
            'timeout': '30',
            'validate_tls': 'False',
        })

        # .. the row now shows the new name ..
        _ = wait_for_outconn_row(page, new_outconn_name)

        # .. and the old name is gone ..
        old_row = find_outconn_row(page, outconn_name)
        assert old_row is None, f'Expected the row for "{outconn_name}" to be gone after the rename'

        # .. the row reflects the new host and path ..
        row = find_outconn_row(page, new_outconn_name)
        cells = get_row_cell_texts(row)

        assert cells[_Cell_Host] == _Test_Host_Edited, f'Expected host "{_Test_Host_Edited}", got: "{cells[_Cell_Host]}"'
        assert cells[_Cell_Url_Path] == new_url_path, f'Expected url_path "{new_url_path}", got: "{cells[_Cell_Url_Path]}"'

        # .. and the edit dialog round-trips every change.
        open_edit_dialog(page, outconn_id)

        expected_values = {
            '#id_edit-name': new_outconn_name,
            '#id_edit-host': _Test_Host_Edited,
            '#id_edit-url_path': new_url_path,
            '#id_edit-ping_method': 'POST',
            '#id_edit-timeout': '30',
            '#id_edit-validate_tls': 'False',
        }

        for selector, expected in expected_values.items():
            actual = page.input_value(selector)
            assert actual == expected, f'Expected {selector} to be "{expected}", got: "{actual}"'

# ################################################################################################################################

    def test_is_active_toggle(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an inactive connection, verifies the row shows it as such,
        then activates it via edit and verifies the change.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'inactive'
        url_path = '/test/outconn/inactive/' + rand_string()

        # Create the connection as inactive ..
        outconn_id = create_outconn(page, base_url, outconn_name, _Test_Host, {
            'url_path': url_path,
            'is_active': False,
        })

        # .. the row shows it is inactive ..
        row = find_outconn_row(page, outconn_name)
        cells = get_row_cell_texts(row)
        assert cells[_Cell_Is_Active] == 'No', f'Expected is_active "No", got: "{cells[_Cell_Is_Active]}"'

        # .. activate the connection ..
        edit_outconn(page, outconn_id, {
            'is_active': True,
        })

        # .. and the row now shows it is active.
        row = find_outconn_row(page, outconn_name)
        cells = get_row_cell_texts(row)
        assert cells[_Cell_Is_Active] == 'Yes', f'Expected is_active "Yes", got: "{cells[_Cell_Is_Active]}"'

# ################################################################################################################################

    def test_delete(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a connection, deletes it via the UI and verifies the row is gone,
        also after a page reload.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'delete'
        url_path = '/test/outconn/delete/' + rand_string()

        # Create the connection ..
        outconn_id = create_outconn(page, base_url, outconn_name, _Test_Host, {
            'url_path': url_path,
        })

        # .. delete it ..
        delete_outconn(page, outconn_id)

        # .. the row is gone ..
        row = find_outconn_row(page, outconn_name)
        assert row is None, f'Expected the row for "{outconn_name}" to be gone'

        # .. and it stays gone after a reload.
        open_outconn_page(page, base_url)

        row = find_outconn_row(page, outconn_name)
        assert row is None, f'Expected the row for "{outconn_name}" to be gone after a reload'

# ################################################################################################################################

    def test_duplicate_name_blocked(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a connection, then tries to create another one with the same name
        and verifies the client-side uniqueness check blocks the submission.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'dup-name'
        url_path = '/test/outconn/dup-name/' + rand_string()

        # Create the first connection ..
        _ = create_outconn(page, base_url, outconn_name, _Test_Host, {
            'url_path': url_path,
        })

        # .. open the create dialog again with the same name but a different URL path ..
        open_create_dialog(page)

        page.fill('#id_name', outconn_name)
        page.fill('#id_host', _Test_Host)
        page.fill('#id_url_path', '/test/outconn/dup-name-other/' + rand_string())

        page.evaluate('$("#id_security").val("ZATO_NONE").trigger("chosen:updated").trigger("change")')

        # .. and confirm the submission is blocked.
        submit_create_form_expect_blocked(page)

# ################################################################################################################################

    def test_empty_url_path_allowed(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a connection with an empty URL path, which outgoing connections allow,
        and verifies the row appears.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'no-url-path'

        # Create the connection with the URL path cleared ..
        _ = create_outconn(page, base_url, outconn_name, _Test_Host, {
            'url_path': '',
        })

        # .. and the row is there.
        row = find_outconn_row(page, outconn_name)
        assert row is not None, f'Expected a row for "{outconn_name}" despite the empty URL path'

# ################################################################################################################################

    def test_get_outconn_id_matches_row(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a connection and verifies the ID cell matches what the edit dialog carries.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'row-id'
        url_path = '/test/outconn/row-id/' + rand_string()

        # Create the connection ..
        outconn_id = create_outconn(page, base_url, outconn_name, _Test_Host, {
            'url_path': url_path,
        })

        # .. re-read the ID from the row ..
        row_outconn_id = get_outconn_id(page, outconn_name)
        assert row_outconn_id == outconn_id, f'Expected connection ID "{outconn_id}", got: "{row_outconn_id}"'

        # .. and the edit dialog carries the same ID.
        open_edit_dialog(page, outconn_id)

        dialog_id = page.input_value('#id_edit-id')
        assert dialog_id == outconn_id, f'Expected dialog ID "{outconn_id}", got: "{dialog_id}"'

# ################################################################################################################################
# ################################################################################################################################
