# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass

# requests
import requests

# PyYAML
import yaml

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class OpenAPIAuth:
    type: 'str'
    scheme: 'str'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class OpenAPIPathItem:
    path: 'str'
    method: 'str'
    auth: 'OpenAPIAuth | None'
    content_types: 'list[str]'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class OpenAPIDefinition:
    servers: 'list[str]'
    paths: 'list[OpenAPIPathItem]'

# ################################################################################################################################
# ################################################################################################################################

class Parser:

    def from_data(self, data:'str') -> 'OpenAPIDefinition':

        # Parse the yaml/json data
        spec = yaml.safe_load(data)

        # Extract servers
        servers = []
        for server_data in spec.get('servers', []):
            servers.append(server_data.get('url', ''))

        # Extract paths
        paths = [p for p in spec.get('paths', {}).keys() if p.startswith('/')]

        # Extract authentication
        auth_list = []
        components = spec.get('components', {})
        security_schemes = components.get('securitySchemes', {})
        for _, scheme_data in security_schemes.items():
            auth = OpenAPIAuth()
            auth.type = scheme_data.get('type', '')
            auth.scheme = scheme_data.get('scheme', '')
            auth_list.append(auth)

        # Extract content types
        content_types_set = set()
        paths_data = spec.get('paths', {})
        for _, path_item in paths_data.items():
            for _, operation in path_item.items():
                if not isinstance(operation, dict):
                    continue

                # Check request body
                request_body = operation.get('requestBody', {})
                content = request_body.get('content', {})
                for ct in content.keys():
                    content_types_set.add(ct)

                # Check responses
                responses = operation.get('responses', {})
                for _, response_data in responses.items():
                    if not isinstance(response_data, dict):
                        continue
                    response_content = response_data.get('content', {})
                    for ct in response_content.keys():
                        content_types_set.add(ct)

        content_types = sorted(content_types_set)

        # Build the definition
        definition = OpenAPIDefinition()
        definition.servers = servers
        definition.paths = paths
        definition.auth = auth_list
        definition.content_types = content_types

        return definition

# ################################################################################################################################

    def from_url(self, url:'str') -> 'OpenAPIDefinition':
        response = requests.get(url)
        _ = response.raise_for_status()
        return self.from_data(response.text)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # Find the yaml file by walking up directories
    current_dir = os.path.dirname(os.path.abspath(__file__))
    search_dir = current_dir

    while True:
        parent = os.path.dirname(search_dir)
        if parent == search_dir:
            raise Exception('Could not find zato-server directory')
        search_dir = parent
        candidate = os.path.join(search_dir, 'zato-server')
        if os.path.isdir(candidate):
            break

    yaml_path = os.path.join(
        candidate,
        'src', 'zato', 'server', 'service', 'internal', 'pubsub', 'openapi.yaml'
    )

    with open(yaml_path, 'r') as f:
        data = f.read()

    parser = Parser()
    definition = parser.from_data(data)

    print('Servers:')
    for server in definition.servers:
        print(f'  {server}')

    print('\nPaths:')
    for path in definition.paths:
        print(f'  {path}')

    print('\nAuth:')
    for auth in definition.auth:
        print(f'  type={auth.type}, scheme={auth.scheme}')

    print('\nContent types:')
    for ct in definition.content_types:
        print(f'  {ct}')
