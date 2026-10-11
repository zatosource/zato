# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import sys
import time
from http.client import BAD_REQUEST, FORBIDDEN, TOO_MANY_REQUESTS, UNAUTHORIZED
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# ################################################################################################################################
# ################################################################################################################################

anydict    = dict[str, Any]
strlist    = list[str]
strnone    = str | None
strstrdict = dict[str, str]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The managed identity of the virtual machine obtains its tokens from the instance metadata service.
    Token_URL        = 'http://169.254.169.254/metadata/identity/oauth2/token'
    Token_API        = '2018-02-01'
    Token_Resource   = 'https://vault.azure.net'
    Vault_URL        = 'https://{vault_name}.vault.azure.net/secrets'
    Vault_API        = '7.4'
    Request_Timeout  = 30
    Retry_Interval   = 10
    Max_Wait_Seconds = 600

    # The identity and its role assignment become effective some time after the machine first boots.
    Retryable_Codes = {BAD_REQUEST, UNAUTHORIZED, FORBIDDEN, TOO_MANY_REQUESTS}

# ################################################################################################################################
# ################################################################################################################################

class KeyVaultError(Exception):
    """ Raised when a secret of the vault cannot be written to env.ini.
    """

# ################################################################################################################################
# ################################################################################################################################

def _get_json(url:'str', headers:'strstrdict') -> 'anydict':

    request = Request(url, headers=headers)

    with urlopen(request, timeout=ModuleCtx.Request_Timeout) as response:
        data = response.read()

    out = json.loads(data)
    return out

# ################################################################################################################################

def _get_token() -> 'str':
    """ Returns an access token for Key Vault, issued to the managed identity of the virtual machine.
    """
    query = urlencode({'api-version': ModuleCtx.Token_API, 'resource': ModuleCtx.Token_Resource})
    url = f'{ModuleCtx.Token_URL}?{query}'

    response = _get_json(url, {'Metadata': 'true'})

    out = response['access_token']
    return out

# ################################################################################################################################

def _get_secret_ids(vault_name:'str', headers:'strstrdict') -> 'strlist':
    """ Returns the IDs of all the enabled secrets of the vault, other than those that back certificates.
    """
    out:'strlist' = []

    vault_url = ModuleCtx.Vault_URL.format(vault_name=vault_name)
    url:'strnone' = f'{vault_url}?api-version={ModuleCtx.Vault_API}'

    # The vault returns its secrets one page at a time ..
    while url:
        response = _get_json(url, headers)

        for item in response['value']:
            attributes = item['attributes']

            if not attributes['enabled']:
                continue

            if item.get('managed'):
                continue

            out.append(item['id'])

        # .. and the last page has no link to a next one.
        url = response['nextLink']

    return out

# ################################################################################################################################

def _read_secrets(vault_name:'str') -> 'strstrdict':
    """ Returns all the secrets of the vault, keyed by their names with dashes turned into underscores.
    """
    out:'strstrdict' = {}

    token = _get_token()
    headers = {'Authorization': f'Bearer {token}'}

    secret_ids = _get_secret_ids(vault_name, headers)

    for secret_id in secret_ids:
        url = f'{secret_id}?api-version={ModuleCtx.Vault_API}'
        response = _get_json(url, headers)

        _, _, name = secret_id.rpartition('/')
        value = response['value']

        if '\n' in value:
            raise KeyVaultError(f'Secret `{name}` has a value of more than one line, which env.ini cannot hold')

        key = name.replace('-', '_')
        out[key] = value

    return out

# ################################################################################################################################

def _is_retryable(exception:'URLError') -> 'bool':

    if isinstance(exception, HTTPError):
        out = exception.code in ModuleCtx.Retryable_Codes

    # Anything else is a network error.
    else:
        out = True

    return out

# ################################################################################################################################

def _read_secrets_when_permitted(vault_name:'str') -> 'strstrdict':
    """ Returns all the secrets of the vault, retrying for as long as the identity of the machine
    is not yet permitted to read them.
    """
    started = time.monotonic()

    while True:
        try:
            out = _read_secrets(vault_name)
        except URLError as e:

            if not _is_retryable(e):
                raise

            elapsed = time.monotonic() - started

            if elapsed > ModuleCtx.Max_Wait_Seconds:
                raise

            message = f'Key Vault {vault_name} not available yet ({e}), retrying in {ModuleCtx.Retry_Interval}s\n'
            _ = sys.stderr.write(message)

            time.sleep(ModuleCtx.Retry_Interval)
        else:
            break

    return out

# ################################################################################################################################

def main() -> 'None':
    """ Prints the secrets of the vault named on input as key=value lines.
    """
    vault_name = sys.argv[1]

    try:
        secrets = _read_secrets_when_permitted(vault_name)
    except (URLError, KeyVaultError) as e:
        _ = sys.stderr.write(f'Key Vault {vault_name} could not be read: {e}\n')
        sys.exit(1)

    lines:'strlist' = []

    for key, value in secrets.items():
        lines.append(f'{key}={value}\n')

    text = ''.join(lines)
    _ = sys.stdout.write(text)

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
