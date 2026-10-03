# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from http.client import OK
from json import dumps, loads

# PyYAML
from yaml import safe_load

# Requests
import requests

# Zato
from zato.common.api import OAuth

# Zato - test helpers
import keycloak_

from bearer_outgoing_config import build_config_yaml, run_enmasse, run_enmasse_export
from bearer_outgoing_config import Call_Service_Name, EC_Outconn_Name, EC_Sec_Def_Name, Env_RSA_Rotated, FHIR_Outconn_Name, \
    FHIR_Patient_ID, FHIR_Read_Service_Name, FHIR_Sec_Def_Name, Key_ID_RSA_Primary, Key_ID_RSA_Rotated, RSA_Outconn_Name, \
    RSA_Sec_Def_Name, Unknown_Outconn_Name, Unknown_Sec_Def_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

# Timeout for HTTP requests to the server under test, in seconds
_http_timeout = 30

# The services the tests reach through the server's invoke endpoint
_get_list_service = 'zato.security.oauth.get-list'
_invoker_service  = 'zato.server.invoker'

# The cluster every quickstart environment has
_cluster_id = 1

# How much longer than the token lifespan to wait for a cached token to be dropped, in seconds
_cache_wait_extra = 1

# ################################################################################################################################
# ################################################################################################################################

def _invoke(zato_server:'stranydict', service:'str', request:'stranydict') -> 'any_':
    """ Invokes a service through the server's admin invoke endpoint and returns the decoded response.
    """
    url = f'{zato_server["base_url"]}/zato/api/invoke/{service}'
    auth = ('admin.invoke', zato_server['invoke_password'])
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, data=dumps(request), headers=headers, auth=auth, timeout=_http_timeout)

    assert response.status_code == OK, f'{service} returned {response.status_code} -> {response.text}'

    out = response.json()
    return out

# ################################################################################################################################

def _call_outconn(zato_server:'stranydict', conn_name:'str') -> 'stranydict':
    """ Asks the test service to invoke an outgoing connection and returns what the service reported.
    """
    out = _invoke(zato_server, Call_Service_Name, {'conn_name': conn_name})
    return out

# ################################################################################################################################

def _get_definitions(zato_server:'stranydict') -> 'anylist':
    """ Returns all bearer token definitions the server has.
    """
    out = _invoke(zato_server, _get_list_service, {'cluster_id': _cluster_id})
    return out

# ################################################################################################################################

def _get_definition(zato_server:'stranydict', name:'str') -> 'stranydict':
    """ Returns a bearer token definition by its name.
    """
    for item in _get_definitions(zato_server):
        if item['name'] == name:
            return item

    raise Exception(f'Definition `{name}` not found')

# ################################################################################################################################

def _get_token_through_dashboard_path(zato_server:'stranydict', security_id:'int') -> 'stranydict':
    """ Obtains a token the way the dashboard's Get token button does, by the definition's ID.
    """
    response = _invoke(zato_server, _invoker_service, {
        'func_name': 'get_bearer_token',
        'security_id': security_id,
    })

    # The invoker hands back the JSON document the token manager produced
    if isinstance(response, str):
        response = loads(response)

    return response

# ################################################################################################################################

def _wait_for_cache_to_expire() -> 'None':
    """ Sleeps for longer than a cached token stays usable, so that the next call signs a fresh assertion.
    """
    time.sleep(keycloak_.JWT_Token_Lifespan + _cache_wait_extra)

# ################################################################################################################################
# ################################################################################################################################

def test_rsa_happy_path(zato_server:'stranydict') -> 'None':

    result = _call_outconn(zato_server, RSA_Outconn_Name)

    assert result['error'] == '', result['error']
    assert result['status_code'] == OK, result

# ################################################################################################################################

def test_ec_happy_path(zato_server:'stranydict') -> 'None':

    result = _call_outconn(zato_server, EC_Outconn_Name)

    assert result['error'] == '', result['error']
    assert result['status_code'] == OK, result

# ################################################################################################################################

def test_token_is_reused_from_cache(zato_server:'stranydict') -> 'None':

    # Two calls in quick succession both succeed - the second one runs on the cached token
    first = _call_outconn(zato_server, EC_Outconn_Name)
    second = _call_outconn(zato_server, EC_Outconn_Name)

    assert first['status_code'] == OK, first
    assert second['status_code'] == OK, second

# ################################################################################################################################

def test_unknown_key_is_rejected(zato_server:'stranydict') -> 'None':

    # Keycloak has never seen this key, so the assertion fails signature lookup and no token is issued
    result = _call_outconn(zato_server, Unknown_Outconn_Name)

    assert result['status_code'] == 0, result
    assert Unknown_Sec_Def_Name in result['error'], result['error']
    assert 'could not be obtained' in result['error'], result['error']
    assert 'invalid_client' in result['error'], result['error']

# ################################################################################################################################

def test_get_token_by_definition_id(zato_server:'stranydict') -> 'None':

    definition = _get_definition(zato_server, RSA_Sec_Def_Name)
    result = _get_token_through_dashboard_path(zato_server, definition['id'])

    assert result['is_ok'] is True, result
    assert result['token'], result

# ################################################################################################################################

def test_get_token_by_definition_id_with_unknown_key(zato_server:'stranydict') -> 'None':

    definition = _get_definition(zato_server, Unknown_Sec_Def_Name)
    result = _get_token_through_dashboard_path(zato_server, definition['id'])

    assert result['is_ok'] is False, result
    assert 'invalid_client' in result['response_body'], result

# ################################################################################################################################

def test_fhir_connection_logs_in_with_an_assertion(zato_server:'stranydict') -> 'None':

    # The FHIR connection signs an assertion for the fake FHIR server's token endpoint,
    # the server issues a token for it and the read goes through with that token
    result = _invoke(zato_server, FHIR_Read_Service_Name, {
        'conn_name': FHIR_Outconn_Name,
        'resource_type': 'Patient',
        'resource_id': FHIR_Patient_ID,
    })

    assert result['error'] == '', result['error']
    assert result['resource']['id'] == FHIR_Patient_ID, result

# ################################################################################################################################

def test_private_key_is_never_listed(zato_server:'stranydict') -> 'None':

    for name in (RSA_Sec_Def_Name, EC_Sec_Def_Name, Unknown_Sec_Def_Name, FHIR_Sec_Def_Name):
        definition = _get_definition(zato_server, name)

        assert 'private_key' not in definition, definition
        assert definition['has_private_key'] is True, definition
        assert definition['client_auth_method'] == OAuth.Client_Auth_Method.Private_Key_JWT, definition

# ################################################################################################################################

def test_private_key_is_never_exported(zato_server:'stranydict') -> 'None':

    exported = run_enmasse_export(zato_server['server_directory'])

    # No PEM block leaves the server in any form ..
    assert 'PRIVATE KEY' not in exported

    # .. and no definition carries its key, which is checked on the parsed YAML because the exporter
    # quotes some values and the name of the method, private_key_jwt, contains the key's own name ..
    security = safe_load(exported)['security']
    definitions = {item['name']: item for item in security}

    for item in security:
        assert 'private_key' not in item, item['name']

    # .. while the non-secret private key JWT fields do travel with the export.
    rsa_definition = definitions[RSA_Sec_Def_Name]
    ec_definition = definitions[EC_Sec_Def_Name]

    assert rsa_definition['client_auth_method'] == OAuth.Client_Auth_Method.Private_Key_JWT
    assert rsa_definition['key_id'] == Key_ID_RSA_Primary
    assert ec_definition['client_auth_method'] == OAuth.Client_Auth_Method.Private_Key_JWT

# ################################################################################################################################

def test_key_rotation_through_reimport(zato_server:'stranydict') -> 'None':

    keys = zato_server['keys']
    server_directory = zato_server['server_directory']
    port = zato_server['port']
    fhir_server = zato_server['fhir_server']

    # Keycloak knows both RSA keys, so the rotation is a change on the Zato side only ..
    rotated_yaml = build_config_yaml(port, fhir_server, rsa_env=Env_RSA_Rotated, rsa_key_id=Key_ID_RSA_Rotated)
    run_enmasse(server_directory, rotated_yaml, keys)

    try:
        # .. the definition now carries the rotated key's ID ..
        definition = _get_definition(zato_server, RSA_Sec_Def_Name)
        assert definition['key_id'] == Key_ID_RSA_Rotated, definition
        assert definition['has_private_key'] is True, definition

        # .. and once the token obtained with the previous key is gone from the cache,
        # the next call signs with the rotated key - Keycloak picks the key by its ID,
        # so an assertion signed with the old key under the new ID would be rejected.
        _wait_for_cache_to_expire()

        result = _call_outconn(zato_server, RSA_Outconn_Name)

        assert result['error'] == '', result['error']
        assert result['status_code'] == OK, result

    finally:
        # Put the primary key back for whichever test runs next
        primary_yaml = build_config_yaml(port, fhir_server)
        run_enmasse(server_directory, primary_yaml, keys)

# ################################################################################################################################
# ################################################################################################################################
