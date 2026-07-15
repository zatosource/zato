# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import create_basic_auth

from openapi_console_lib import console_login, edit_channel_by_name, get_spec_yaml, spec_paths, wait_for_spec, \
    Path_Typed, Service_Typed

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.openapi.schema.' + CryptoManager.generate_hex_string(32) + '.'

# What the typed service's dataclasses must be documented as - exact field names,
# types, required flags and the nested model reference.
_Expected_Request_Schema = {
    'type': 'object',
    'properties': {
        'username': {'type': 'string'},
        'max_results': {'type': 'integer', 'format': 'int32'},
        'needs_details': {'type': 'boolean'},
        'locale': {'type': ['string', 'null']},
    },
    'required': ['username', 'max_results', 'needs_details', 'locale'],
}

_Expected_Response_Schema = {
    'type': 'object',
    'properties': {
        'user_name': {'type': 'string'},
        'user_id': {'type': 'integer', 'format': 'int32'},
        'is_manager': {'type': 'boolean'},
        'address': {'$ref': '#/components/schemas/Address'},
        'role_list': {'type': 'array', 'items': {'type': 'string'}},
    },
    'required': ['user_name', 'user_id', 'is_manager', 'address', 'role_list'],
}

_Expected_Address_Schema = {
    'type': 'object',
    'properties': {
        'street': {'type': 'string'},
        'city': {'type': 'string'},
    },
    'required': ['street', 'city'],
}

# ################################################################################################################################
# ################################################################################################################################

class TestOpenAPIConsoleTypedSchema:
    """ Verifies that dataclass models turn into exact component schemas
    and that the YAML document is equivalent to the JSON one.
    """

# ################################################################################################################################

    def test_typed_service_schema(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Grants a user the typed endpoint and asserts the full schema contents in JSON and YAML.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        console_url = zato_dashboard['console_url']

        # Create a Basic Auth definition and grant it the typed endpoint,
        # which is already active from the earlier activation ..
        definition = create_basic_auth(page, base_url, _Test_Name_Prefix, 'schema')

        _ = edit_channel_by_name(page, base_url, Service_Typed, {
            'security': f'Basic Auth/{definition["name"]}',
        })

        # .. sign in to the console as that user ..
        console_login(page, console_url, definition['username'], definition['password'])

        # .. the document contains only the typed endpoint ..
        def has_only_typed_path(spec:'anydict') -> 'bool':
            out = spec_paths(spec) == {Path_Typed}
            return out

        spec = wait_for_spec(page, console_url, has_only_typed_path)

        # .. the operation references the request and response models ..
        operation = spec['paths'][Path_Typed]['post']

        request_schema = operation['requestBody']['content']['application/json']['schema']
        assert request_schema == {'$ref': '#/components/schemas/GetUserRequest'}, \
            f'Unexpected request schema: {request_schema}'

        response_schema = operation['responses']['200']['content']['application/json']['schema']
        assert response_schema == {'$ref': '#/components/schemas/GetUserResponse'}, \
            f'Unexpected response schema: {response_schema}'

        # .. only the three models the endpoint uses are present ..
        schemas = spec['components']['schemas']
        schema_names = set(schemas)
        assert schema_names == {'GetUserRequest', 'GetUserResponse', 'Address'}, \
            f'Unexpected schema names: {sorted(schema_names)}'

        # .. each model is documented with its exact fields, types and required flags ..
        assert schemas['GetUserRequest'] == _Expected_Request_Schema, \
            f'Unexpected GetUserRequest schema: {schemas["GetUserRequest"]}'

        assert schemas['GetUserResponse'] == _Expected_Response_Schema, \
            f'Unexpected GetUserResponse schema: {schemas["GetUserResponse"]}'

        assert schemas['Address'] == _Expected_Address_Schema, \
            f'Unexpected Address schema: {schemas["Address"]}'

        # .. and the YAML document is equivalent to the JSON one.
        yaml_spec = get_spec_yaml(page, console_url)
        assert yaml_spec == spec, 'Expected the YAML document to equal the JSON one'

# ################################################################################################################################
# ################################################################################################################################
