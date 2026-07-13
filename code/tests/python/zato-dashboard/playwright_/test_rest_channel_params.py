# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from http.client import NOT_FOUND, OK

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

from rest_channel import Introspection_Service_Name, Introspection_Service_Source, create_channel, \
    deploy_service_file, edit_channel, invoke_channel, open_edit_dialog, wait_for_service_in_dialog

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.rest.params.' + rand_string() + '.'

_JSON_Headers = {'Content-Type': 'application/json'}

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def introspection_service(zato_dashboard:'anydict') -> 'any_':
    """ Hot-deploys the introspection service for the duration of this module.
    """

    server_dir = zato_dashboard['server_dir']
    file_path = deploy_service_file(server_dir, 'test_rest_introspect.py', Introspection_Service_Source)

    yield Introspection_Service_Name

    os.remove(file_path)

# ################################################################################################################################
# ################################################################################################################################

def _create_introspection_channel(
    page:'Page',
    zato_dashboard:'anydict',
    name_suffix:'str',
    url_path:'str',
    options:'anydict | None'=None,
    ) -> 'str':
    """ Waits for the introspection service to be deployed and creates a channel pointing at it.
    """

    base_url = zato_dashboard['dashboard_url']

    # Make sure the hot-deployed service is already selectable ..
    wait_for_service_in_dialog(page, base_url, Introspection_Service_Name)

    # .. and create the channel.
    channel_name = _Test_Name_Prefix + name_suffix

    out = create_channel(page, base_url, channel_name, Introspection_Service_Name, url_path, options)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRESTChannelParams:
    """ Tests for data formats and parameter handling of REST channels.
    """

# ################################################################################################################################

    def test_data_format_json(
        self, logged_in_page:'Page', zato_dashboard:'anydict', introspection_service:'str') -> 'None':
        """ A channel with data_format=json hands the service a parsed dict.
        """

        page = logged_in_page
        server_port = zato_dashboard['server_port']

        url_path = '/test/rest/format-json/' + rand_string()

        _ = _create_introspection_channel(page, zato_dashboard, 'format-json', url_path, {
            'data_format': 'json',
        })

        # POST a JSON document ..
        response = invoke_channel(server_port, url_path, data='{"phrase": "Parsed as JSON"}', headers=_JSON_Headers)
        assert response.status_code == OK, f'Expected OK, got {response.status_code}: {response.text}'

        # .. and the service saw it as a dict.
        details = response.json()
        assert details['payload'] == {'phrase': 'Parsed as JSON'}, f'Expected a parsed dict, got: {details["payload"]}'

# ################################################################################################################################

    def test_data_format_form_data(
        self, logged_in_page:'Page', zato_dashboard:'anydict', introspection_service:'str') -> 'None':
        """ A channel with data_format=form hands the service the parsed form fields.
        """

        page = logged_in_page
        server_port = zato_dashboard['server_port']

        url_path = '/test/rest/format-form/' + rand_string()

        _ = _create_introspection_channel(page, zato_dashboard, 'format-form', url_path, {
            'data_format': 'form',
        })

        # POST a form-encoded body ..
        form_fields = {'phrase': 'Sent as a form', 'customer': 'CRM-123'}
        response = invoke_channel(server_port, url_path, data=form_fields)
        assert response.status_code == OK, f'Expected OK, got {response.status_code}: {response.text}'

        # .. and the service saw the parsed fields.
        details = response.json()
        form_data = details['form_data']

        logger.info('[test_data_format_form_data] form_data=%s', form_data)

        for field_name, field_value in form_fields.items():
            assert field_name in form_data, f'Expected "{field_name}" in the form data, got: {form_data}'

            # Form parsers may return values as single-element lists
            parsed_value = form_data[field_name]
            if isinstance(parsed_value, list):
                parsed_value = parsed_value[0]

            assert parsed_value == field_value, f'Expected "{field_value}" for "{field_name}", got: {parsed_value}'

# ################################################################################################################################

    def test_no_data_format_raw_passthrough(
        self, logged_in_page:'Page', zato_dashboard:'anydict', introspection_service:'str') -> 'None':
        """ A channel without a data format hands the service the raw request body.
        """

        page = logged_in_page
        server_port = zato_dashboard['server_port']

        url_path = '/test/rest/format-raw/' + rand_string()

        _ = _create_introspection_channel(page, zato_dashboard, 'format-raw', url_path)

        # POST a plain text body ..
        request_body = 'A plain text payload, not JSON at all'
        response = invoke_channel(server_port, url_path, data=request_body, headers={'Content-Type': 'text/plain'})
        assert response.status_code == OK, f'Expected OK, got {response.status_code}: {response.text}'

        # .. and the service saw the raw text unchanged.
        details = response.json()
        assert details['payload'] == request_body, f'Expected the raw body, got: {details["payload"]}'

# ################################################################################################################################

    def test_merge_url_params_on(
        self, logged_in_page:'Page', zato_dashboard:'anydict', introspection_service:'str') -> 'None':
        """ With merge_url_params_req on, which is the default, query string parameters
        show up in the channel params the service receives.
        """

        page = logged_in_page
        server_port = zato_dashboard['server_port']

        url_path = '/test/rest/merge-on/' + rand_string()

        _ = _create_introspection_channel(page, zato_dashboard, 'merge-on', url_path, {
            'data_format': 'json',
        })

        # Send a query string parameter ..
        response = invoke_channel(server_port, url_path, data='{}', params={'customer': 'CRM-123'})
        assert response.status_code == OK, f'Expected OK, got {response.status_code}: {response.text}'

        # .. and it shows up both in the query string and in the channel params.
        details = response.json()
        assert details['query_string_params']['customer'] == 'CRM-123', \
            f'Expected the query string parameter, got: {details["query_string_params"]}'
        assert details['channel_params']['customer'] == 'CRM-123', \
            f'Expected the merged channel parameter, got: {details["channel_params"]}'

# ################################################################################################################################

    def test_merge_url_params_off(
        self, logged_in_page:'Page', zato_dashboard:'anydict', introspection_service:'str') -> 'None':
        """ With merge_url_params_req off, query string parameters do not reach the channel params.
        """

        page = logged_in_page
        server_port = zato_dashboard['server_port']

        url_path = '/test/rest/merge-off/' + rand_string()

        _ = _create_introspection_channel(page, zato_dashboard, 'merge-off', url_path, {
            'data_format': 'json',
            'merge_url_params_req': False,
        })

        # Send a query string parameter ..
        response = invoke_channel(server_port, url_path, data='{}', params={'customer': 'CRM-123'})
        assert response.status_code == OK, f'Expected OK, got {response.status_code}: {response.text}'

        # .. and the channel params stay empty.
        details = response.json()
        assert details['channel_params'] == {}, f'Expected empty channel params, got: {details["channel_params"]}'

# ################################################################################################################################

    def test_path_params(
        self, logged_in_page:'Page', zato_dashboard:'anydict', introspection_service:'str') -> 'None':
        """ Parameters embedded in the URL path populate the channel params.
        """

        page = logged_in_page
        server_port = zato_dashboard['server_port']

        url_prefix = '/test/rest/path-params/' + rand_string()
        url_path = url_prefix + '/{phrase}'

        _ = _create_introspection_channel(page, zato_dashboard, 'path-params', url_path, {
            'data_format': 'json',
        })

        # Request with a concrete path segment ..
        response = invoke_channel(server_port, url_prefix + '/hello-from-path', data='{}')
        assert response.status_code == OK, f'Expected OK, got {response.status_code}: {response.text}'

        # .. and the segment shows up as a path parameter and a channel parameter.
        details = response.json()
        assert details['path_params'] == {'phrase': 'hello-from-path'}, \
            f'Expected the path parameter, got: {details["path_params"]}'
        assert details['channel_params']['phrase'] == 'hello-from-path', \
            f'Expected the channel parameter, got: {details["channel_params"]}'

# ################################################################################################################################

    def test_url_params_priority_qs_over_path(
        self, logged_in_page:'Page', zato_dashboard:'anydict', introspection_service:'str') -> 'None':
        """ With the default qs-over-path priority, a query string value overrides
        a path parameter of the same name.
        """

        page = logged_in_page
        server_port = zato_dashboard['server_port']

        url_prefix = '/test/rest/priority-qs/' + rand_string()
        url_path = url_prefix + '/{phrase}'

        _ = _create_introspection_channel(page, zato_dashboard, 'priority-qs', url_path, {
            'data_format': 'json',
            'url_params_pri': 'qs-over-path',
        })

        # Send conflicting values in the path and in the query string ..
        response = invoke_channel(server_port, url_prefix + '/from-path', data='{}', params={'phrase': 'from-query-string'})
        assert response.status_code == OK, f'Expected OK, got {response.status_code}: {response.text}'

        # .. and the query string value wins.
        details = response.json()
        assert details['channel_params']['phrase'] == 'from-query-string', \
            f'Expected the query string value to win, got: {details["channel_params"]}'

# ################################################################################################################################

    def test_url_params_priority_path_over_qs(
        self, logged_in_page:'Page', zato_dashboard:'anydict', introspection_service:'str') -> 'None':
        """ With the path-over-qs priority, a path parameter overrides a query string
        value of the same name.
        """

        page = logged_in_page
        server_port = zato_dashboard['server_port']

        url_prefix = '/test/rest/priority-path/' + rand_string()
        url_path = url_prefix + '/{phrase}'

        _ = _create_introspection_channel(page, zato_dashboard, 'priority-path', url_path, {
            'data_format': 'json',
            'url_params_pri': 'path-over-qs',
        })

        # Send conflicting values in the path and in the query string ..
        response = invoke_channel(server_port, url_prefix + '/from-path', data='{}', params={'phrase': 'from-query-string'})
        assert response.status_code == OK, f'Expected OK, got {response.status_code}: {response.text}'

        # .. and the path value wins.
        details = response.json()
        assert details['channel_params']['phrase'] == 'from-path', \
            f'Expected the path value to win, got: {details["channel_params"]}'

# ################################################################################################################################

    def test_params_priority_roundtrip(
        self, logged_in_page:'Page', zato_dashboard:'anydict', introspection_service:'str') -> 'None':
        """ Both params_pri values are accepted by the form and persist across edits.
        """

        page = logged_in_page

        url_path = '/test/rest/params-pri/' + rand_string()

        # Create the channel with the non-default priority ..
        channel_id = _create_introspection_channel(page, zato_dashboard, 'params-pri', url_path, {
            'params_pri': 'msg-over-channel-params',
        })

        # .. and verify it persisted.
        open_edit_dialog(page, channel_id)
        actual = page.input_value('#id_edit-params_pri')
        assert actual == 'msg-over-channel-params', f'Expected "msg-over-channel-params", got: "{actual}"'

        # Switch back to the default priority via edit ..
        page.evaluate('$("#edit-div").dialog("close")')
        page.wait_for_function('!document.querySelector("#edit-div").offsetParent')

        edit_channel(page, channel_id, {
            'params_pri': 'channel-params-over-msg',
        })

        # .. and verify that persisted too.
        open_edit_dialog(page, channel_id)
        actual = page.input_value('#id_edit-params_pri')
        assert actual == 'channel-params-over-msg', f'Expected "channel-params-over-msg", got: "{actual}"'

# ################################################################################################################################

    def test_match_slash_on(
        self, logged_in_page:'Page', zato_dashboard:'anydict', introspection_service:'str') -> 'None':
        """ With match_slash on, which is the default, a path parameter value may contain slashes.
        """

        page = logged_in_page
        server_port = zato_dashboard['server_port']

        url_prefix = '/test/rest/slash-on/' + rand_string()
        url_path = url_prefix + '/{phrase}'

        _ = _create_introspection_channel(page, zato_dashboard, 'slash-on', url_path, {
            'data_format': 'json',
            'match_slash': True,
        })

        # Request with a slash inside the path parameter ..
        response = invoke_channel(server_port, url_prefix + '/customers/CRM-123', data='{}')
        assert response.status_code == OK, f'Expected OK, got {response.status_code}: {response.text}'

        # .. and the whole remainder is the parameter value.
        details = response.json()
        assert details['path_params'] == {'phrase': 'customers/CRM-123'}, \
            f'Expected the multi-segment value, got: {details["path_params"]}'

# ################################################################################################################################

    def test_match_slash_off(
        self, logged_in_page:'Page', zato_dashboard:'anydict', introspection_service:'str') -> 'None':
        """ With match_slash off, a path parameter value with slashes no longer matches.
        """

        page = logged_in_page
        server_port = zato_dashboard['server_port']

        url_prefix = '/test/rest/slash-off/' + rand_string()
        url_path = url_prefix + '/{phrase}'

        _ = _create_introspection_channel(page, zato_dashboard, 'slash-off', url_path, {
            'data_format': 'json',
            'match_slash': False,
        })

        # A single-segment value matches ..
        response = invoke_channel(server_port, url_prefix + '/single-segment', data='{}')
        assert response.status_code == OK, f'Expected OK for a single segment, got {response.status_code}: {response.text}'

        details = response.json()
        assert details['path_params'] == {'phrase': 'single-segment'}, \
            f'Expected the single-segment value, got: {details["path_params"]}'

        # .. while a value with a slash does not.
        response = invoke_channel(server_port, url_prefix + '/customers/CRM-123', data='{}')
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND for a multi-segment value, got {response.status_code}'

# ################################################################################################################################

    def test_method_restriction(
        self, logged_in_page:'Page', zato_dashboard:'anydict', introspection_service:'str') -> 'None':
        """ A channel restricted to POST accepts POST requests only.
        """

        page = logged_in_page
        server_port = zato_dashboard['server_port']

        url_path = '/test/rest/method-post/' + rand_string()

        _ = _create_introspection_channel(page, zato_dashboard, 'method-post', url_path, {
            'data_format': 'json',
            'method': 'POST',
        })

        # POST matches ..
        response = invoke_channel(server_port, url_path, data='{}')
        assert response.status_code == OK, f'Expected OK for POST, got {response.status_code}: {response.text}'

        details = response.json()
        assert details['http_method'] == 'POST', f'Expected the POST method reported, got: {details["http_method"]}'

        # .. while GET does not.
        response = invoke_channel(server_port, url_path, method='GET')
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND for GET, got {response.status_code}'

# ################################################################################################################################

    def test_no_method_restriction(
        self, logged_in_page:'Page', zato_dashboard:'anydict', introspection_service:'str') -> 'None':
        """ A channel without a method restriction accepts any verb.
        """

        page = logged_in_page
        server_port = zato_dashboard['server_port']

        url_path = '/test/rest/method-any/' + rand_string()

        _ = _create_introspection_channel(page, zato_dashboard, 'method-any', url_path, {
            'data_format': 'json',
        })

        # Every common verb matches and the service sees the right method.
        for method in ('GET', 'POST', 'PUT', 'PATCH', 'DELETE'):
            response = invoke_channel(server_port, url_path, method=method, data='{}')
            assert response.status_code == OK, f'Expected OK for {method}, got {response.status_code}: {response.text}'

            details = response.json()
            assert details['http_method'] == method, f'Expected {method} reported, got: {details["http_method"]}'

# ################################################################################################################################

    def test_http_accept_restriction(
        self, logged_in_page:'Page', zato_dashboard:'anydict', introspection_service:'str') -> 'None':
        """ A channel with a concrete http_accept value serves only clients sending
        a matching Accept header.
        """

        page = logged_in_page
        server_port = zato_dashboard['server_port']

        url_path = '/test/rest/accept-json/' + rand_string()

        _ = _create_introspection_channel(page, zato_dashboard, 'accept-json', url_path, {
            'data_format': 'json',
            'http_accept': 'application/json',
        })

        # A matching Accept header works ..
        response = invoke_channel(server_port, url_path, data='{}', headers={'Accept': 'application/json'})
        assert response.status_code == OK, f'Expected OK for a matching Accept, got {response.status_code}: {response.text}'

        # .. while a different one does not ..
        response = invoke_channel(server_port, url_path, data='{}', headers={'Accept': 'text/plain'})
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND for a non-matching Accept, got {response.status_code}'

        # .. and neither does the catch-all Accept sent by generic clients.
        response = invoke_channel(server_port, url_path, data='{}', headers={'Accept': '*/*'})
        assert response.status_code == NOT_FOUND, f'Expected NOT_FOUND for a wildcard Accept, got {response.status_code}'

# ################################################################################################################################

    def test_http_accept_default_matches_all(
        self, logged_in_page:'Page', zato_dashboard:'anydict', introspection_service:'str') -> 'None':
        """ A channel without an http_accept value serves clients regardless of their Accept header.
        """

        page = logged_in_page
        server_port = zato_dashboard['server_port']

        url_path = '/test/rest/accept-any/' + rand_string()

        _ = _create_introspection_channel(page, zato_dashboard, 'accept-any', url_path, {
            'data_format': 'json',
        })

        # Any Accept header works, including none at all.
        for accept in ('application/json', 'text/plain', '*/*'):
            response = invoke_channel(server_port, url_path, data='{}', headers={'Accept': accept})
            assert response.status_code == OK, f'Expected OK for Accept "{accept}", got {response.status_code}'

# ################################################################################################################################
# ################################################################################################################################
