# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import subprocess
import time
from http.client import CONFLICT, CREATED, NO_CONTENT, OK

# Requests
import requests

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

# Docker details of the Keycloak instance the live tests run against
Keycloak_Image          = 'quay.io/keycloak/keycloak:26.4'
Keycloak_Container_Name = 'zato-test-keycloak'
Keycloak_Port           = 8480
Keycloak_Base_URL       = f'http://localhost:{Keycloak_Port}'

# Bootstrap admin credentials for the dev-mode container
Keycloak_Admin_Username = 'admin'
Keycloak_Admin_Password = 'admin'

# The main realm most tests use and a second one for wrong-issuer tests
Realm_Main  = 'zato-test'
Realm_Other = 'zato-test-other'

# Audiences the test clients put into their tokens
Audience_Main  = 'zato-test-audience'
Audience_Other = 'zato-other-audience'

# The claim the test clients carry and its per-client values
Claim_Department      = 'department'
Department_Accounting = 'Accounting'
Department_Sales      = 'Sales'

# A client whose tokens carry the main audience and the Accounting department claim
Client_Accounting = 'zato-test-accounting'
Secret_Accounting = 'zato-test-secret-accounting'

# A client whose tokens carry the main audience and the Sales department claim
Client_Sales = 'zato-test-sales'
Secret_Sales = 'zato-test-secret-sales'

# A client whose tokens carry a different audience
Client_Wrong_Audience = 'zato-test-wrong-audience'
Secret_Wrong_Audience = 'zato-test-secret-wrong-audience'

# A client whose tokens carry the main audience but no department claim at all
Client_No_Department = 'zato-test-no-department'
Secret_No_Department = 'zato-test-secret-no-department'

# A client whose tokens expire almost immediately, for expiry tests
Client_Short_Lived = 'zato-test-short-lived'
Secret_Short_Lived = 'zato-test-secret-short-lived'

# A client in the second realm, for wrong-issuer tests
Client_Other_Realm = 'zato-test-other-realm'
Secret_Other_Realm = 'zato-test-secret-other-realm'

# How long short-lived access tokens last, in seconds
Short_Token_Lifespan = 1

# How long to wait for the container to accept requests, in seconds
_startup_timeout = 180

# Timeout for individual HTTP requests, in seconds
_http_timeout = 30

# How often to poll for container readiness, in seconds
_readiness_poll_interval = 1.0

# Timeout for docker commands, in seconds
_docker_timeout = 120

# ################################################################################################################################
# ################################################################################################################################

def get_issuer(realm:'str'=Realm_Main) -> 'str':
    out = f'{Keycloak_Base_URL}/realms/{realm}'
    return out

# ################################################################################################################################

def get_token_url(realm:'str'=Realm_Main) -> 'str':
    issuer = get_issuer(realm)

    out = f'{issuer}/protocol/openid-connect/token'
    return out

# ################################################################################################################################

def get_jwks_url(realm:'str'=Realm_Main) -> 'str':
    issuer = get_issuer(realm)

    out = f'{issuer}/protocol/openid-connect/certs'
    return out

# ################################################################################################################################
# ################################################################################################################################

def _run_docker(arguments:'strlist') -> 'any_':
    """ Runs a docker command and returns the completed process.
    """
    command = ['docker'] + arguments

    out = subprocess.run(command, capture_output=True, text=True, timeout=_docker_timeout)
    return out

# ################################################################################################################################

def _ensure_container_running() -> 'None':
    """ Starts the Keycloak container, creating it first if it does not exist at all.
    """
    # Find out whether the container exists and whether it is running ..
    result = _run_docker(['inspect', '--format', '{{.State.Running}}', Keycloak_Container_Name])

    # .. a non-zero exit code means there is no such container, so create it ..
    if result.returncode != 0:
        result = _run_docker([
            'run', '-d',
            '--name', Keycloak_Container_Name,
            '-p', f'{Keycloak_Port}:8080',
            '-e', f'KC_BOOTSTRAP_ADMIN_USERNAME={Keycloak_Admin_Username}',
            '-e', f'KC_BOOTSTRAP_ADMIN_PASSWORD={Keycloak_Admin_Password}',
            Keycloak_Image,
            'start-dev',
        ])

        if result.returncode != 0:
            raise Exception(f'Could not start Keycloak -> {result.stderr}')

    # .. an existing but stopped container only needs to be started again.
    elif result.stdout.strip() != 'true':
        result = _run_docker(['start', Keycloak_Container_Name])

        if result.returncode != 0:
            raise Exception(f'Could not restart Keycloak -> {result.stderr}')

# ################################################################################################################################

def _wait_until_ready() -> 'None':
    """ Polls the master realm endpoint until Keycloak responds or the timeout expires.
    """
    readiness_url = f'{Keycloak_Base_URL}/realms/master'
    deadline = time.monotonic() + _startup_timeout

    while time.monotonic() < deadline:

        try:
            response = requests.get(readiness_url, timeout=_http_timeout)
        except requests.exceptions.ConnectionError:
            time.sleep(_readiness_poll_interval)
            continue

        if response.status_code == OK:
            return

        time.sleep(_readiness_poll_interval)

    raise Exception(f'Keycloak did not become ready within {_startup_timeout}s')

# ################################################################################################################################

def _get_admin_token() -> 'str':
    """ Obtains an admin token from the master realm using the bootstrap credentials.
    """
    token_url = f'{Keycloak_Base_URL}/realms/master/protocol/openid-connect/token'

    response = requests.post(token_url, data={
        'grant_type': 'password',
        'client_id': 'admin-cli',
        'username': Keycloak_Admin_Username,
        'password': Keycloak_Admin_Password,
    }, timeout=_http_timeout)

    if response.status_code != OK:
        raise Exception(f'Could not obtain a Keycloak admin token -> {response.status_code} -> {response.text}')

    data = response.json()

    out = data['access_token']
    return out

# ################################################################################################################################

def _admin_headers(admin_token:'str') -> 'stranydict':
    out = {'Authorization': f'Bearer {admin_token}'}
    return out

# ################################################################################################################################

def _ensure_realm(admin_token:'str', realm:'str') -> 'None':
    """ Creates a realm, ignoring the conflict if it already exists.
    """
    realms_url = f'{Keycloak_Base_URL}/admin/realms'
    headers = _admin_headers(admin_token)

    response = requests.post(realms_url, json={
        'realm': realm,
        'enabled': True,
    }, headers=headers, timeout=_http_timeout)

    # Anything other than created-or-already-there is an actual error
    if response.status_code not in (CREATED, CONFLICT):
        raise Exception(f'Could not create realm `{realm}` -> {response.status_code} -> {response.text}')

# ################################################################################################################################

def _get_client_internal_id(admin_token:'str', realm:'str', client_id:'str') -> 'strnone':
    """ Returns the internal ID of a client, or None if there is no such client.
    """
    clients_url = f'{Keycloak_Base_URL}/admin/realms/{realm}/clients'
    headers = _admin_headers(admin_token)

    response = requests.get(clients_url, params={'clientId': client_id}, headers=headers, timeout=_http_timeout)

    if response.status_code != OK:
        raise Exception(f'Could not look up client `{client_id}` -> {response.status_code} -> {response.text}')

    items = response.json()

    if items:
        first = items[0]
        out = first['id']
    else:
        out = None

    return out

# ################################################################################################################################

def _add_mapper(admin_token:'str', realm:'str', internal_id:'str', mapper:'stranydict') -> 'None':
    """ Adds a protocol mapper to a client, ignoring the conflict if one of that name already exists.
    """
    mappers_url = f'{Keycloak_Base_URL}/admin/realms/{realm}/clients/{internal_id}/protocol-mappers/models'
    headers = _admin_headers(admin_token)

    response = requests.post(mappers_url, json=mapper, headers=headers, timeout=_http_timeout)

    # Anything other than created-or-already-there is an actual error
    if response.status_code not in (CREATED, CONFLICT):
        raise Exception(f'Could not add mapper `{mapper["name"]}` -> {response.status_code} -> {response.text}')

# ################################################################################################################################

def _ensure_client(
    admin_token:'str',
    realm:'str',
    client_id:'str',
    secret:'str',
    audience:'str',
    department:'strnone'=None,
    token_lifespan:'int'=0,
    ) -> 'None':
    """ Creates a confidential client with the client credentials grant, an audience mapper
    and, optionally, a hardcoded department claim and a custom token lifespan.
    """
    headers = _admin_headers(admin_token)

    # Skip creation if the client is already provisioned ..
    internal_id = _get_client_internal_id(admin_token, realm, client_id)

    if not internal_id:

        # .. tokens can be given a custom lifespan through client attributes ..
        attributes:'stranydict' = {}

        if token_lifespan:
            attributes['access.token.lifespan'] = str(token_lifespan)

        clients_url = f'{Keycloak_Base_URL}/admin/realms/{realm}/clients'

        response = requests.post(clients_url, json={
            'clientId': client_id,
            'secret': secret,
            'protocol': 'openid-connect',
            'publicClient': False,
            'serviceAccountsEnabled': True,
            'standardFlowEnabled': False,
            'attributes': attributes,
        }, headers=headers, timeout=_http_timeout)

        if response.status_code != CREATED:
            raise Exception(f'Could not create client `{client_id}` -> {response.status_code} -> {response.text}')

        internal_id = _get_client_internal_id(admin_token, realm, client_id)

        if not internal_id:
            raise Exception(f'Client `{client_id}` not found after creation')

    # .. the audience mapper puts the expected aud claim into access tokens ..
    _add_mapper(admin_token, realm, internal_id, {
        'name': f'{client_id}-audience',
        'protocol': 'openid-connect',
        'protocolMapper': 'oidc-audience-mapper',
        'config': {
            'included.custom.audience': audience,
            'access.token.claim': 'true',
            'id.token.claim': 'false',
        },
    })

    # .. and the department mapper hardcodes the test claim, when one was requested.
    if department:
        _add_mapper(admin_token, realm, internal_id, {
            'name': f'{client_id}-department',
            'protocol': 'openid-connect',
            'protocolMapper': 'oidc-hardcoded-claim-mapper',
            'config': {
                'claim.name': Claim_Department,
                'claim.value': department,
                'jsonType.label': 'String',
                'access.token.claim': 'true',
                'id.token.claim': 'false',
                'userinfo.token.claim': 'false',
            },
        })

# ################################################################################################################################

def _provision(admin_token:'str') -> 'None':
    """ Creates the realms and clients the live tests expect. Safe to run repeatedly.
    """
    # The main realm holds most of the test clients ..
    _ensure_realm(admin_token, Realm_Main)

    _ensure_client(admin_token, Realm_Main, Client_Accounting, Secret_Accounting, Audience_Main,
        department=Department_Accounting)

    _ensure_client(admin_token, Realm_Main, Client_Sales, Secret_Sales, Audience_Main,
        department=Department_Sales)

    _ensure_client(admin_token, Realm_Main, Client_Wrong_Audience, Secret_Wrong_Audience, Audience_Other)

    _ensure_client(admin_token, Realm_Main, Client_No_Department, Secret_No_Department, Audience_Main)

    _ensure_client(admin_token, Realm_Main, Client_Short_Lived, Secret_Short_Lived, Audience_Main,
        department=Department_Accounting, token_lifespan=Short_Token_Lifespan)

    # .. and the second realm exists only so its tokens carry a different issuer.
    _ensure_realm(admin_token, Realm_Other)

    _ensure_client(admin_token, Realm_Other, Client_Other_Realm, Secret_Other_Realm, Audience_Main)

# ################################################################################################################################
# ################################################################################################################################

def ensure_keycloak() -> 'None':
    """ Brings up a fully provisioned Keycloak - container running, realms and clients in place.
    Safe to call from any number of test suites, all the steps are idempotent.
    """
    # First, the container itself ..
    _ensure_container_running()

    # .. then wait for it to accept requests ..
    _wait_until_ready()

    # .. and finally make sure the realms and clients exist.
    admin_token = _get_admin_token()
    _provision(admin_token)

# ################################################################################################################################

def get_token(client_id:'str', client_secret:'str', realm:'str'=Realm_Main) -> 'str':
    """ Obtains an access token for a client through the client credentials grant.
    """
    token_url = get_token_url(realm)

    response = requests.post(token_url, data={
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }, timeout=_http_timeout)

    if response.status_code != OK:
        raise Exception(f'Could not obtain a token for `{client_id}` -> {response.status_code} -> {response.text}')

    data = response.json()

    out = data['access_token']
    return out

# ################################################################################################################################

def rotate_keys(realm:'str'=Realm_Main) -> 'None':
    """ Creates a new realm signing key with the highest priority so far,
    which makes Keycloak sign all new tokens with it - real key rotation.
    """
    admin_token = _get_admin_token()
    headers = _admin_headers(admin_token)

    # The components API needs the realm's internal ID as the parent ..
    realm_url = f'{Keycloak_Base_URL}/admin/realms/{realm}'
    response = requests.get(realm_url, headers=headers, timeout=_http_timeout)

    if response.status_code != OK:
        raise Exception(f'Could not read realm `{realm}` -> {response.status_code} -> {response.text}')

    realm_data = response.json()
    realm_internal_id = realm_data['id']

    # .. the current time makes for an ever-increasing priority ..
    priority = int(time.time())

    # .. and a new active RSA key with that priority takes over the signing of new tokens.
    components_url = f'{Keycloak_Base_URL}/admin/realms/{realm}/components'

    response = requests.post(components_url, json={
        'name': f'rotated-{priority}',
        'providerId': 'rsa-generated',
        'providerType': 'org.keycloak.keys.KeyProvider',
        'parentId': realm_internal_id,
        'config': {
            'priority': [str(priority)],
            'enabled': ['true'],
            'active': ['true'],
            'keySize': ['2048'],
            'algorithm': ['RS256'],
        },
    }, headers=headers, timeout=_http_timeout)

    if response.status_code not in (CREATED, NO_CONTENT):
        raise Exception(f'Could not rotate keys in realm `{realm}` -> {response.status_code} -> {response.text}')

# ################################################################################################################################
# ################################################################################################################################
