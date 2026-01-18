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
class OpenAPIPathItem:
    name: 'str'
    path: 'str'
    auth: 'str'
    content_type: 'str'

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

        # Build auth lookup from security schemes
        components = spec.get('components', {})
        security_schemes = components.get('securitySchemes', {})
        auth_lookup = {}
        for scheme_name, scheme_data in security_schemes.items():
            scheme = scheme_data.get('scheme', '')
            if scheme:
                scheme = scheme + '_auth'
            auth_lookup[scheme_name] = scheme

        # Global security requirements
        global_security = spec.get('security', [])

        # Extract paths with their methods, auth and content types
        path_items = []
        paths_data = spec.get('paths', {})

        for path_str, path_data in paths_data.items():
            if not path_str.startswith('/'):
                continue

            for method, operation in path_data.items():
                if not isinstance(operation, dict):
                    continue

                # Determine auth for this operation
                operation_security = operation.get('security', global_security)
                auth = ''
                for sec_req in operation_security:
                    for scheme_name in sec_req.keys():
                        if scheme_name in auth_lookup:
                            auth = auth_lookup[scheme_name]
                            break
                    if auth:
                        break

                # Get content type from request body
                request_body = operation.get('requestBody', {})
                content = request_body.get('content', {})
                content_type = next(iter(content.keys()), 'application/json')

                # Generate name from operationId, summary, or path
                name = operation.get('operationId', '')
                if not name:
                    summary = operation.get('summary', '')
                    if summary:
                        name = summary.lower().replace(' ', '_')
                if not name:
                    name = path_str.strip('/').replace('/', '_').replace('{', '').replace('}', '')

                path_item = OpenAPIPathItem()
                path_item.name = name
                path_item.path = path_str
                path_item.auth = auth
                path_item.content_type = content_type
                path_items.append(path_item)

        # Build the definition
        definition = OpenAPIDefinition()
        definition.servers = servers
        definition.paths = path_items

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
    for item in definition.paths:
        print(f'  {item.name}')
        print(f'    path: {item.path}')
        print(f'    auth: {item.auth}')
        print(f'    content_type: {item.content_type}')
