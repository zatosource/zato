# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
import base64
import json
import logging
import sys
from dataclasses import dataclass

# requests
import requests

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strdict, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SetupResult:
    access_policy_id: 'str'
    token: 'str'
    encoded_credentials: 'str'
    policy_response: 'strdict'
    token_response: 'strdict'
    error: 'strnone' = None
    error_response: 'strdict | None' = None

# ################################################################################################################################
# ################################################################################################################################

class AutoSetup:

    def __init__(self, main_token:'str', instance_id:'str', region:'str | None'=None) -> 'None':
        self.main_token = main_token
        self.instance_id = instance_id
        self.region = region or self._extract_region_from_token(main_token)
        self.base_url = 'https://www.grafana.com/api/v1'

# ################################################################################################################################

    def _extract_region_from_token(self, token:'str') -> 'str':

        token_parts = token.split('_')
        if len(token_parts) < 2:
            raise ValueError('Invalid token format: cannot extract region')

        encoded_payload = token_parts[1]

        decoded_bytes = base64.b64decode(encoded_payload)
        decoded_str = decoded_bytes.decode('utf-8')
        payload = json.loads(decoded_str)

        metadata = payload.get('m')
        if not metadata:
            raise ValueError('Token metadata missing')

        region = metadata.get('r')
        if not region:
            raise ValueError('Region not found in token metadata')

        return region

# ################################################################################################################################

    def _make_request(self, method:'str', url:'str', data:'strdict | None'=None) -> 'strdict':

        headers = {
            'Authorization': f'Bearer {self.main_token}',
            'Content-Type': 'application/json'
        }

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data
        )

        return response.json()

# ################################################################################################################################

    def create_access_policy(self, name:'str', display_name:'str', scopes:'strlist') -> 'strdict':

        url = f'{self.base_url}/accesspolicies?region={self.region}'

        realm = {}
        realm['type'] = 'stack'
        realm['identifier'] = self.instance_id

        data = {}
        data['name'] = name
        data['displayName'] = display_name
        data['scopes'] = scopes
        data['realms'] = [realm]

        return self._make_request('POST', url, data)

# ################################################################################################################################

    def create_token(self, access_policy_id:'str', name:'str', display_name:'str') -> 'strdict':

        url = f'{self.base_url}/tokens?region={self.region}'

        data = {}
        data['accessPolicyId'] = access_policy_id
        data['name'] = name
        data['displayName'] = display_name

        return self._make_request('POST', url, data)

# ################################################################################################################################

    def encode_credentials(self, token:'str') -> 'str':

        credentials = f'{self.instance_id}:{token}'
        credentials_bytes = credentials.encode('utf-8')
        encoded_bytes = base64.b64encode(credentials_bytes)
        encoded = encoded_bytes.decode('utf-8')

        return encoded

# ################################################################################################################################

    def setup_complete(self, policy_name:'str', token_name:'str') -> 'SetupResult':

        scopes = ['metrics:write', 'logs:write', 'traces:write']

        policy_response = self.create_access_policy(
            name=policy_name,
            display_name='Zato OTLP',
            scopes=scopes
        )

        access_policy_id = policy_response.get('id')

        if not access_policy_id:
            result = SetupResult()
            result.error = 'Failed to create access policy'
            result.error_response = policy_response
            return result

        token_response = self.create_token(
            access_policy_id=access_policy_id,
            name=token_name,
            display_name='Zato Token'
        )

        token = token_response.get('token')

        if not token:
            result = SetupResult()
            result.error = 'Failed to create token'
            result.error_response = token_response
            return result

        encoded = self.encode_credentials(token)

        result = SetupResult()
        result.access_policy_id = access_policy_id
        result.token = token
        result.encoded_credentials = encoded
        result.policy_response = policy_response
        result.token_response = token_response

        return result

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class CLI:

    def __init__(self) -> 'None':
        self.parser = self._create_parser()

# ################################################################################################################################

    def _create_parser(self) -> 'argparse.ArgumentParser':
        parser = argparse.ArgumentParser(
            description='Automate Grafana Cloud access policy and token creation'
        )

        _ = parser.add_argument(
            '--main-token',
            required=True,
            help='Bootstrap access token with accesspolicies:write scope'
        )

        _ = parser.add_argument(
            '--instance-id',
            required=True,
            help='Grafana Cloud instance ID'
        )

        _ = parser.add_argument(
            '--policy-name',
            default='zato-otlp',
            help='Access policy name (default: zato-otlp)'
        )

        _ = parser.add_argument(
            '--token-name',
            default='zato-token',
            help='Token name (default: zato-token)'
        )

        return parser

# ################################################################################################################################

    def run(self, args:'strlist | None'=None) -> 'int':

        logging.basicConfig(level=logging.INFO, format='%(message)s')

        parsed_args = self.parser.parse_args(args)

        setup = AutoSetup(
            main_token=parsed_args.main_token,
            instance_id=parsed_args.instance_id
        )

        result = setup.setup_complete(
            policy_name=parsed_args.policy_name,
            token_name=parsed_args.token_name
        )

        if result.error:
            logger.error(f'Error: {result.error}')
            if result.error_response:
                err_msg = json.dumps(result.error_response, indent=2)
                logger.error(err_msg)
            return 1

        logger.info(f'Access Policy ID: {result.access_policy_id}')
        logger.info(f'Token: {result.token}')
        logger.info(f'Encoded Credentials: {result.encoded_credentials}')

        return 0

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    cli = CLI()
    exit_code = cli.run()
    sys.exit(exit_code)

# ################################################################################################################################
# ################################################################################################################################
