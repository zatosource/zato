# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import NOT_FOUND, OK

# pytest
import pytest

# Zato
from zato.common.test import rand_string

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

from rest_channel import create_channel, delete_channel, edit_channel, find_channel_row, get_channel_id, \
    get_row_cell_texts, invoke_channel, open_channel_page, open_edit_dialog, submit_create_form_expect_blocked, \
    wait_for_channel_row

from zato.common.test.playwright_pubsub import open_create_dialog

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.rest.crud.' + rand_string() + '.'

_Echo_Service = 'demo.echo'

# Row cell indexes for REST channel rows
_Cell_Name = 2
_Cell_Is_Active = 3
_Cell_Url_Path = 4
_Cell_Service = 5
_Cell_Security = 6
_Cell_Security_Groups = 7
_Cell_Rate_Limiting = 25

# ################################################################################################################################
# ################################################################################################################################

class TestRESTChannelCRUD:
    """ Tests for REST channel create, edit and delete via the web admin UI.
    """

# ################################################################################################################################

    def test_page_loads(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Navigates to the REST channels page and verifies its structure.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the REST channels page ..
        open_channel_page(page, base_url)

        # .. verify the page heading ..
        heading = page.query_selector('h2.zato')
        heading_text = heading.inner_text()
        assert 'REST API endpoints' in heading_text, f'Expected "REST API endpoints" in heading, got: {heading_text}'

        # .. verify the create link is present ..
        create_link = page.query_selector('#markup .page_prompt a')
        create_link_text = create_link.inner_text()
        assert 'Create a new REST API endpoint' in create_link_text, \
            f'Expected create link text, got: {create_link_text}'

        # .. and verify the table headers.
        headers = page.query_selector_all('#data-table thead th a')

        header_texts:'anylist' = []

        for header in headers:
            raw_text = header.inner_text()
            text = raw_text.strip().lower()
            header_texts.append(text)

        for expected in ('name', 'active', 'url path', 'service', 'security', 'security groups'):
            assert expected in header_texts, f'Expected "{expected}" in headers, got: {header_texts}'

# ################################################################################################################################

    def test_create_minimal(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a REST channel with the minimal set of fields, verifies the row's columns,
        then invokes the channel and confirms the echo round trip.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'minimal'
        url_path = '/test/rest/minimal/' + rand_string()

        # Create the channel ..
        _ = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'data_format': 'json',
        })

        # .. read the row cells ..
        row = find_channel_row(page, channel_name)
        cells = get_row_cell_texts(row)

        logger.info('[test_create_minimal] cells=%s', cells)

        # .. verify the visible columns ..
        assert channel_name in cells[_Cell_Name], f'Expected name "{channel_name}", got: "{cells[_Cell_Name]}"'
        assert cells[_Cell_Is_Active] == 'Yes', f'Expected is_active "Yes", got: "{cells[_Cell_Is_Active]}"'
        assert cells[_Cell_Url_Path] == url_path, f'Expected url_path "{url_path}", got: "{cells[_Cell_Url_Path]}"'
        assert cells[_Cell_Service] == _Echo_Service, f'Expected service "{_Echo_Service}", got: "{cells[_Cell_Service]}"'
        assert cells[_Cell_Security] == '---', f'Expected no security definition, got: "{cells[_Cell_Security]}"'
        # A freshly added row renders the zero counts while a server-rendered row shows a placeholder
        assert cells[_Cell_Security_Groups] in ('---', '0 groups, 0 clients'), \
            f'Expected no security groups, got: "{cells[_Cell_Security_Groups]}"'
        assert cells[_Cell_Rate_Limiting] == 'Rate limiting', \
            f'Expected the rate limiting link, got: "{cells[_Cell_Rate_Limiting]}"'

        # .. and confirm the channel is live by echoing a message through it.
        request_payload = {'phrase': 'Hello REST channels'}
        response = invoke_channel(server_port, url_path, json_data=request_payload)

        assert response.status_code == OK, f'Expected OK, got {response.status_code}: {response.text}'
        assert response.json() == request_payload, f'Expected the request echoed back, got: {response.text}'

# ################################################################################################################################

    # Moving a documented endpoint to a new URL path is a breaking change the servers report on rebuild
    @pytest.mark.expect_log_errors('OpenAPI breaking change:')
    def test_edit_rename_and_url_path(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a channel, renames it and changes its URL path, then verifies
        the old path returns 404 while the new one works.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'edit-rename'
        new_channel_name = _Test_Name_Prefix + 'edit-renamed'

        old_url_path = '/test/rest/edit-old/' + rand_string()
        new_url_path = '/test/rest/edit-new/' + rand_string()

        # Create the channel and confirm it responds ..
        channel_id = create_channel(page, base_url, channel_name, _Echo_Service, old_url_path, {
            'data_format': 'json',
        })

        response = invoke_channel(server_port, old_url_path, data='{"before": "edit"}')
        assert response.status_code == OK, f'Expected OK before edit, got {response.status_code}'

        # .. rename it and move it to the new path ..
        edit_channel(page, channel_id, {
            'name': new_channel_name,
            'url_path': new_url_path,
        })

        # .. the row now shows the new name ..
        _ = wait_for_channel_row(page, new_channel_name)

        # .. the old path is gone ..
        response = invoke_channel(server_port, old_url_path, data='{"after": "edit"}')
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND at the old path, got {response.status_code}'

        # .. and the new path works.
        request_payload = {'after': 'edit'}
        response = invoke_channel(server_port, new_url_path, json_data=request_payload)

        assert response.status_code == OK, f'Expected OK at the new path, got {response.status_code}: {response.text}'
        assert response.json() == request_payload, f'Expected the request echoed back, got: {response.text}'

# ################################################################################################################################

    def test_edit_options_roundtrip(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a channel with every "More options" field set to a non-default value,
        then reopens the edit dialog and verifies all of them persisted.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        channel_name = _Test_Name_Prefix + 'options-roundtrip'
        url_path = '/test/rest/options/' + rand_string()

        # Create the channel with non-default options ..
        channel_id = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'data_format': 'json',
            'url_params_pri': 'path-over-qs',
            'params_pri': 'msg-over-channel-params',
            'merge_url_params_req': False,
            'match_slash': False,
            'method': 'POST',
            'http_accept': 'application/json',
        })

        # .. reopen the edit dialog ..
        open_edit_dialog(page, channel_id)

        # .. and verify each field kept its value.
        expected_values = {
            '#id_edit-name': channel_name,
            '#id_edit-url_path': url_path,
            '#id_edit-data_format': 'json',
            '#id_edit-url_params_pri': 'path-over-qs',
            '#id_edit-params_pri': 'msg-over-channel-params',
            '#id_edit-method': 'POST',
            '#id_edit-http_accept': 'application/json',
        }

        for selector, expected in expected_values.items():
            actual = page.input_value(selector)
            assert actual == expected, f'Expected {selector} to be "{expected}", got: "{actual}"'

        # Checkboxes are verified separately since they have no input value ..
        assert not page.is_checked('#id_edit-merge_url_params_req'), 'Expected merge_url_params_req to be unchecked'
        assert not page.is_checked('#id_edit-match_slash'), 'Expected match_slash to be unchecked'

        # .. and the service select still points at the echo service.
        service_value = page.eval_on_selector('#id_edit-service', 'select => select.value')
        assert service_value == _Echo_Service, f'Expected service "{_Echo_Service}", got: "{service_value}"'

# ################################################################################################################################

    def test_is_active_toggle(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an inactive channel, confirms requests get 404, then activates it
        via edit and confirms requests pass.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'inactive'
        url_path = '/test/rest/inactive/' + rand_string()

        # Create the channel as inactive ..
        channel_id = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'data_format': 'json',
            'is_active': False,
        })

        # .. the row shows it is inactive ..
        row = find_channel_row(page, channel_name)
        cells = get_row_cell_texts(row)
        assert cells[_Cell_Is_Active] == 'No', f'Expected is_active "No", got: "{cells[_Cell_Is_Active]}"'

        # .. requests to an inactive channel get 404 ..
        response = invoke_channel(server_port, url_path, data='{"check": "inactive"}')
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND for an inactive channel, got {response.status_code}'

        # .. activate the channel ..
        edit_channel(page, channel_id, {
            'is_active': True,
        })

        # .. and now requests pass.
        request_payload = {'check': 'active'}
        response = invoke_channel(server_port, url_path, json_data=request_payload)

        assert response.status_code == OK, f'Expected OK for an active channel, got {response.status_code}: {response.text}'
        assert response.json() == request_payload, f'Expected the request echoed back, got: {response.text}'

# ################################################################################################################################

    # Removing a documented endpoint is a breaking change the servers report on rebuild
    @pytest.mark.expect_log_errors('OpenAPI breaking change:')
    def test_delete(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a channel, deletes it via the UI, then verifies the row is gone
        and the URL path returns 404.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'delete'
        url_path = '/test/rest/delete/' + rand_string()

        # Create the channel and confirm it responds ..
        channel_id = create_channel(page, base_url, channel_name, _Echo_Service, url_path)

        response = invoke_channel(server_port, url_path, data='{"before": "delete"}')
        assert response.status_code == OK, f'Expected OK before delete, got {response.status_code}'

        # .. delete it ..
        delete_channel(page, channel_id)

        # .. the row is gone ..
        row = find_channel_row(page, channel_name)
        assert row is None, f'Expected the row for "{channel_name}" to be gone'

        # .. and the URL path no longer exists.
        response = invoke_channel(server_port, url_path, data='{"after": "delete"}')
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND after delete, got {response.status_code}'

# ################################################################################################################################

    def test_duplicate_name_blocked(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a channel, then tries to create another one with the same name
        and verifies the client-side uniqueness check blocks the submission.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        channel_name = _Test_Name_Prefix + 'dup-name'
        url_path = '/test/rest/dup-name/' + rand_string()

        # Create the first channel ..
        _ = create_channel(page, base_url, channel_name, _Echo_Service, url_path)

        # .. open the create dialog again with the same name but a different URL path ..
        open_create_dialog(page)

        page.fill('#id_name', channel_name)
        page.fill('#id_url_path', '/test/rest/dup-name-other/' + rand_string())

        page.evaluate(f'$("#id_service").val("{_Echo_Service}").trigger("chosen:updated").trigger("change")')
        page.evaluate('$("#id_security").val("ZATO_NONE").trigger("chosen:updated").trigger("change")')

        # .. and confirm the submission is blocked.
        submit_create_form_expect_blocked(page)

# ################################################################################################################################

    def test_duplicate_url_path_blocked(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a channel, then tries to create another one with the same URL path
        and verifies the client-side uniqueness check blocks the submission.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        channel_name = _Test_Name_Prefix + 'dup-path'
        url_path = '/test/rest/dup-path/' + rand_string()

        # Create the first channel ..
        _ = create_channel(page, base_url, channel_name, _Echo_Service, url_path)

        # .. open the create dialog again with a new name but the same URL path ..
        open_create_dialog(page)

        page.fill('#id_name', _Test_Name_Prefix + 'dup-path-other')
        page.fill('#id_url_path', url_path)

        page.evaluate(f'$("#id_service").val("{_Echo_Service}").trigger("chosen:updated").trigger("change")')
        page.evaluate('$("#id_security").val("ZATO_NONE").trigger("chosen:updated").trigger("change")')

        # .. and confirm the submission is blocked.
        submit_create_form_expect_blocked(page)

# ################################################################################################################################

    def test_unknown_url_returns_404(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Confirms that a URL path with no channel behind it returns 404.
        """

        server_port = zato_dashboard['server_port']

        url_path = '/test/rest/no-such-channel/' + rand_string()

        response = invoke_channel(server_port, url_path, data='{"check": "missing"}')

        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND for an unknown URL, got {response.status_code}'
        assert 'URL not found' in response.text, f'Expected "URL not found" in the body, got: {response.text}'

# ################################################################################################################################

    def test_get_channel_id_matches_row(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a channel and verifies the ID cell matches what the edit dialog carries.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        channel_name = _Test_Name_Prefix + 'row-id'
        url_path = '/test/rest/row-id/' + rand_string()

        # Create the channel ..
        channel_id = create_channel(page, base_url, channel_name, _Echo_Service, url_path)

        # .. re-read the ID from the row ..
        row_channel_id = get_channel_id(page, channel_name)
        assert row_channel_id == channel_id, f'Expected channel ID "{channel_id}", got: "{row_channel_id}"'

        # .. and the edit dialog carries the same ID.
        open_edit_dialog(page, channel_id)

        dialog_id = page.input_value('#id_edit-id')
        assert dialog_id == channel_id, f'Expected dialog ID "{channel_id}", got: "{dialog_id}"'

# ################################################################################################################################
# ################################################################################################################################
