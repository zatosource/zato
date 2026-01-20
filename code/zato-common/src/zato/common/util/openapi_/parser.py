# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
import json
import os
import traceback
from dataclasses import asdict, dataclass

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
    auth_server_url: 'str'
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

        # Parse the yaml/json data - sanitize non-printable characters first
        sanitized = ''.join(c if c.isprintable() or c in '\n\r\t' else '_' for c in data)
        try:
            spec = yaml.safe_load(sanitized)
        except yaml.YAMLError as e:
            try:
                spec = json.loads(sanitized)
            except json.JSONDecodeError:
                raise Exception(f'Failed to parse as yaml: {e}')

        if not isinstance(spec, dict):
            preview = str(spec)[:500] if spec else '(empty)'
            raise Exception(f'Invalid OpenAPI spec: expected dict, got {type(spec).__name__}\n\nContent:\n{preview}')

        # Extract servers
        servers = []
        for server_data in spec.get('servers', []):
            servers.append(server_data.get('url', ''))

        # Build auth lookup from security schemes
        components = spec.get('components', {})
        security_schemes = components.get('securitySchemes', {})
        auth_lookup = {}
        token_url_lookup = {}
        for scheme_name, scheme_data in security_schemes.items():
            auth_type = scheme_data.get('type', '')
            scheme = scheme_data.get('scheme', '')
            if scheme == 'basic':
                auth_lookup[scheme_name] = 'basic_auth'
            elif scheme == 'bearer':
                auth_lookup[scheme_name] = 'bearer_token'
            elif auth_type == 'oauth2':
                auth_lookup[scheme_name] = 'oauth2'
                flows = scheme_data.get('flows', {})
                for flow_data in flows.values():
                    token_url = flow_data.get('tokenUrl', '')
                    if token_url:
                        token_url_lookup[scheme_name] = token_url
                        break
            elif auth_type == 'apiKey':
                in_location = scheme_data.get('in', 'header')
                if in_location == 'header':
                    auth_lookup[scheme_name] = 'api_key'
                else:
                    auth_lookup[scheme_name] = f'unsupported-apikey-{in_location}'
            elif auth_type == 'mutualTLS':
                auth_lookup[scheme_name] = 'unsupported-mutualTLS'
            else:
                auth_lookup[scheme_name] = f'unsupported-{auth_type}'

        # Global security requirements
        global_security = spec.get('security', [])

        # Extract paths with their methods, auth and content types
        path_items = []
        paths_data = spec.get('paths', {})

        for path_str, path_data in paths_data.items():
            if not path_str.startswith('/'):
                continue

            for _, operation in path_data.items():
                if not isinstance(operation, dict):
                    continue

                # Determine auth for this operation
                operation_security = operation.get('security', global_security)
                auth = ''
                auth_server_url = ''
                for sec_req in operation_security:
                    for scheme_name in sec_req.keys():
                        if scheme_name in auth_lookup:
                            auth = auth_lookup[scheme_name]
                            auth_server_url = token_url_lookup.get(scheme_name, '')
                            break
                    if auth:
                        break

                # Get content type from request body
                request_body = operation.get('requestBody', {})
                content = request_body.get('content', {})
                content_type = next(iter(content.keys()), 'application/json')

                # Generate name from summary, operationId, or path
                name = operation.get('summary', '')
                if not name:
                    name = operation.get('operationId', '')
                if not name:
                    name = path_str.strip('/').replace('/', ' ').replace('{', '').replace('}', '').replace('_', ' ').title()

                # Fix grammar: "a" -> "an" before vowels
                name = name.replace(' a A', ' an A').replace(' a E', ' an E').replace(' a I', ' an I').replace(' a O', ' an O').replace(' a U', ' an U')
                name = name.replace(' a a', ' an a').replace(' a e', ' an e').replace(' a i', ' an i').replace(' a o', ' an o').replace(' a u', ' an u')

                path_item = OpenAPIPathItem()
                path_item.name = name
                path_item.path = path_str
                path_item.auth = auth
                path_item.auth_server_url = auth_server_url
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

def _print_definition(name:'str', definition:'OpenAPIDefinition') -> 'None':
    print(f'\n{"=" * 60}')
    print(f'{name}')
    print('=' * 60)

    print('\nServers:')
    for server in definition.servers:
        print(f'  {server}')

    print('\nPaths:')
    for item in definition.paths:
        print(f'  {item.name}')
        print(f'    path: {item.path}')
        print(f'    auth: {item.auth}')
        print(f'    content_type: {item.content_type}')

# ################################################################################################################################
# ################################################################################################################################

def _run_demo() -> 'None':

    current_dir = os.path.dirname(os.path.abspath(__file__))
    samples_dir = os.path.join(current_dir, 'samples')

    # Find zato-server directory
    search_dir = current_dir
    while True:
        parent = os.path.dirname(search_dir)
        if parent == search_dir:
            raise Exception('Could not find zato-server directory')
        search_dir = parent
        candidate = os.path.join(search_dir, 'zato-server')
        if os.path.isdir(candidate):
            break

    parser = Parser()

    # Parse Zato pub/sub OpenAPI
    yaml_path = os.path.join(
        candidate,
        'src', 'zato', 'server', 'service', 'internal', 'pubsub', 'openapi.yaml'
    )
    with open(yaml_path, 'r') as f:
        data = f.read()
    definition = parser.from_data(data)
    _print_definition('Zato pub/sub', definition)

    # Parse sample files
    for filename in sorted(os.listdir(samples_dir)):
        filepath = os.path.join(samples_dir, filename)
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            data = f.read()
        try:
            definition = parser.from_data(data)
        except Exception as e:
            print(f'\nFailed to parse: {filepath}')
            print(f'Error: {e}')
            print(f'Traceback:\n{traceback.format_exc()}')
            continue
        name = os.path.splitext(filename)[0].replace('_', ' ').title()
        _print_definition(name, definition)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(description='Parse OpenAPI definitions')
    group = arg_parser.add_mutually_exclusive_group(required=False)
    _ = group.add_argument('--from-url', dest='from_url', help='URL to fetch OpenAPI definition from')
    _ = group.add_argument('--from-file', dest='from_file', help='Path to OpenAPI definition file')
    _ = group.add_argument('--demo', action='store_true', help='Run demo with sample files')

    args = arg_parser.parse_args()

    parser = Parser()

    if args.from_url:
        definition = parser.from_url(args.from_url)
        print(json.dumps(asdict(definition), indent=2))
    elif args.from_file:
        with open(args.from_file, 'r', encoding='utf-8', errors='ignore') as f:
            data = f.read()
        definition = parser.from_data(data)
        print(json.dumps(asdict(definition), indent=2))
    else:
        _run_demo()

# ################################################################################################################################
# ################################################################################################################################
