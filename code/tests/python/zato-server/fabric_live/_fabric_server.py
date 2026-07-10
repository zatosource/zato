# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import threading
import time
from http.client import ACCEPTED, BAD_REQUEST, CREATED, NOT_FOUND, OK, UNAUTHORIZED
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strnone

# ################################################################################################################################
# ################################################################################################################################

# How long the tokens this server issues remain valid, in seconds.
_token_lifetime = 3600

# The URL path prefix of the OneLake data plane this server simulates.
_onelake_prefix = '/onelake'

# ################################################################################################################################
# ################################################################################################################################

def _build_initial_workspaces() -> 'anydict':
    """ Returns the workspaces the simulated Fabric tenant starts with.
    """
    return {
        'workspace-sales-analytics': {
            'id': 'workspace-sales-analytics',
            'displayName': 'Sales analytics',
            'description': 'Sales data engineering and reporting',
            'type': 'Workspace',
            'capacityId': 'capacity-main',
        },
        'workspace-finance': {
            'id': 'workspace-finance',
            'displayName': 'Finance',
            'description': 'Finance data warehouse',
            'type': 'Workspace',
            'capacityId': 'capacity-main',
        },
    }

# ################################################################################################################################

def _build_initial_items() -> 'anydict':
    """ Returns the items each workspace starts with.
    """
    return {
        'workspace-sales-analytics': {
            'item-sales-lakehouse': {
                'id': 'item-sales-lakehouse',
                'workspaceId': 'workspace-sales-analytics',
                'displayName': 'Sales lakehouse',
                'description': 'Raw and curated sales data',
                'type': 'Lakehouse',
            },
            'item-daily-load-notebook': {
                'id': 'item-daily-load-notebook',
                'workspaceId': 'workspace-sales-analytics',
                'displayName': 'Daily load notebook',
                'description': 'Loads yesterday sales into the lakehouse',
                'type': 'Notebook',
            },
            'item-sales-pipeline': {
                'id': 'item-sales-pipeline',
                'workspaceId': 'workspace-sales-analytics',
                'displayName': 'Sales pipeline',
                'description': 'Copies sales data from the source systems',
                'type': 'DataPipeline',
            },
        },
        'workspace-finance': {},
    }

# ################################################################################################################################

def _build_initial_jobs() -> 'anydict':
    """ Returns the job history the simulated tenant starts with, keyed by (workspace ID, item ID).
    """
    return {
        ('workspace-sales-analytics', 'item-daily-load-notebook'): {
            'job-notebook-001': {
                'id': 'job-notebook-001',
                'itemId': 'item-daily-load-notebook',
                'workspaceId': 'workspace-sales-analytics',
                'jobType': 'RunNotebook',
                'status': 'Completed',
                'startTimeUtc': '2026-07-01T05:00:00Z',
                'endTimeUtc': '2026-07-01T05:04:30Z',
            },
        },
    }

# ################################################################################################################################

def _build_initial_shortcuts() -> 'anydict':
    """ Returns the OneLake shortcuts the simulated tenant starts with, keyed by (workspace ID, item ID).
    """
    return {
        ('workspace-sales-analytics', 'item-sales-lakehouse'): {
            'external-orders': {
                'name': 'external-orders',
                'path': 'Files',
                'target': {
                    'adlsGen2': {
                        'url': 'https://example.dfs.core.windows.net',
                        'subpath': '/orders',
                    },
                },
            },
        },
    }

# ################################################################################################################################

def _build_initial_onelake_files() -> 'anydict':
    """ Returns the OneLake files the simulated tenant starts with, keyed by workspace ID.
    """
    return {
        'workspace-sales-analytics': {
            'item-sales-lakehouse/Files/reference/regions.csv': b'region,name\nEMEA,Europe\nAPAC,Asia Pacific\n',
        },
        'workspace-finance': {},
    }

# ################################################################################################################################

def _build_capacities() -> 'anydict':
    """ Returns the capacities the simulated tenant has.
    """
    return {
        'capacity-main': {
            'id': 'capacity-main',
            'displayName': 'Main capacity',
            'sku': 'F64',
            'region': 'West Europe',
            'state': 'Active',
        },
    }

# ################################################################################################################################
# ################################################################################################################################

class FabricTestHandler(BaseHTTPRequestHandler):

    # Credentials the token endpoint accepts
    expected_tenant_id:'strnone' = None
    expected_client_id:'strnone' = None
    expected_client_secret:'strnone' = None

    # All the tokens issued so far, mapped to when they expire
    valid_tokens:'anydict' = {}

    # The state of the simulated tenant
    workspaces:'anydict' = {}
    items:'anydict' = {}
    jobs:'anydict' = {}
    shortcuts:'anydict' = {}
    onelake_files:'anydict' = {}
    capacities:'anydict' = {}

    # How many workspaces, items and jobs were created so far, used to build new IDs
    object_counter = 0

    def log_message(self, format, *args) -> 'None':
        pass

# ################################################################################################################################

    @classmethod
    def invalidate_tokens(class_) -> 'None':
        """ Makes all the previously issued tokens invalid, which forces clients to obtain new ones.
        """
        class_.valid_tokens = {}

# ################################################################################################################################

    @classmethod
    def _next_id(class_, prefix:'str') -> 'str':
        """ Builds a new object ID with the given prefix.
        """
        class_.object_counter += 1

        out = f'{prefix}-new-{class_.object_counter:03}'
        return out

# ################################################################################################################################

    def _send_json(self, status:'int', data:'anydict', location:'strnone'=None) -> 'None':
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        if location:
            self.send_header('Location', location)
        self.end_headers()
        body = json.dumps(data)
        _ = self.wfile.write(body.encode('utf-8'))

# ################################################################################################################################

    def _send_bytes(self, status:'int', data:'bytes') -> 'None':
        self.send_response(status)
        self.send_header('Content-Type', 'application/octet-stream')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        _ = self.wfile.write(data)

# ################################################################################################################################

    def _send_empty(self, status:'int') -> 'None':
        self.send_response(status)
        self.send_header('Content-Length', '0')
        self.end_headers()

# ################################################################################################################################

    def _read_body(self) -> 'bytes':
        content_length = int(self.headers.get('Content-Length', 0))
        out = self.rfile.read(content_length)
        return out

# ################################################################################################################################

    def _read_json_body(self) -> 'anydict':
        body = self._read_body()

        if body:
            out = json.loads(body)
        else:
            out = {}

        return out

# ################################################################################################################################

    def _check_token(self) -> 'bool':
        """ Confirms the request carries a valid, non-expired bearer token.
        """
        auth_header = self.headers.get('Authorization', '')

        # No bearer token at all
        if not auth_header.startswith('Bearer '):
            return False

        token = auth_header.split(' ', 1)[1]

        # A token we never issued, e.g. one that was invalidated in the meantime
        if token not in self.valid_tokens:
            return False

        # A token that has already expired
        now = time.time()
        expiration_time = self.valid_tokens[token]
        if now >= expiration_time:
            return False

        return True

# ################################################################################################################################

    def _handle_token_request(self) -> 'None':
        """ An Entra-style OAuth2 token endpoint for the client credentials grant.
        It serves both the Fabric API scope and the OneLake storage scope.
        """
        body = self._read_body()
        form_data = parse_qs(body.decode('utf-8'))

        client_id = form_data.get('client_id', [''])[0]
        client_secret = form_data.get('client_secret', [''])[0]

        # Reject requests whose credentials do not match ..
        if client_id != self.expected_client_id:
            self._send_json(UNAUTHORIZED, {'error': 'invalid_client'})
            return

        if client_secret != self.expected_client_secret:
            self._send_json(UNAUTHORIZED, {'error': 'invalid_client'})
            return

        # .. otherwise, issue a new token with an expiration time.
        token = 'token.' + CryptoManager.generate_hex_string()

        now = time.time()
        FabricTestHandler.valid_tokens[token] = now + _token_lifetime

        self._send_json(OK, {
            'token_type': 'Bearer',
            'expires_in': _token_lifetime,
            'access_token': token,
        })

# ################################################################################################################################

    def _handle_jobs_request(self, method:'str', workspace_id:'str', item_id:'str', segments:'list', params:'anydict') -> 'None':
        """ Job instances of an item - starting, inspecting and cancelling jobs.
        Segments are the path elements after /jobs/instances, e.g. ['job-notebook-001', 'cancel'].
        """
        job_key = (workspace_id, item_id)
        item_jobs = self.jobs.setdefault(job_key, {})

        segment_count = len(segments)

        # POST /jobs/instances?jobType=X - start a new job, which is a long-running operation,
        # so the response is 202 Accepted with a Location header pointing to the new job instance.
        if segment_count == 0:
            if method == 'POST':
                job_type = params.get('jobType', [''])[0]

                if not job_type:
                    self._send_json(BAD_REQUEST,
                        {'error': {'code': 'InvalidRequest', 'message': 'jobType is required'}})
                    return

                job_id = self._next_id('job')
                item_jobs[job_id] = {
                    'id': job_id,
                    'itemId': item_id,
                    'workspaceId': workspace_id,
                    'jobType': job_type,
                    'status': 'InProgress',
                    'startTimeUtc': '2026-07-10T12:00:00Z',
                }

                location = f'/workspaces/{workspace_id}/items/{item_id}/jobs/instances/{job_id}'
                self._send_json(ACCEPTED, item_jobs[job_id], location=location)
                return

        # Anything below this point points to a specific job
        if segment_count >= 1:
            job_id = segments[0]

            if job_id not in item_jobs:
                self._send_json(NOT_FOUND,
                    {'error': {'code': 'JobNotFound', 'message': f'Job {job_id} not found'}})
                return

            job = item_jobs[job_id]

            # GET /jobs/instances/{job_id} - a single job instance
            if segment_count == 1:
                if method == 'GET':
                    self._send_json(OK, job)
                    return

            # POST /jobs/instances/{job_id}/cancel - cancel a job instance
            if segment_count == 2:
                if segments[1] == 'cancel':
                    if method == 'POST':
                        job['status'] = 'Cancelled'
                        self._send_empty(ACCEPTED)
                        return

        # Nothing above handled the request, so the path or method is not supported.
        self._send_json(BAD_REQUEST,
            {'error': {'code': 'InvalidRequest', 'message': f'Unsupported request: {method} {self.path}'}})

# ################################################################################################################################

    def _handle_shortcuts_request(self, method:'str', workspace_id:'str', item_id:'str', segments:'list') -> 'None':
        """ OneLake shortcuts of an item.
        Segments are the path elements after /shortcuts, e.g. ['Files', 'external-orders'].
        """
        shortcut_key = (workspace_id, item_id)
        item_shortcuts = self.shortcuts.setdefault(shortcut_key, {})

        segment_count = len(segments)

        if segment_count == 0:

            # GET /shortcuts - list all the shortcuts of an item
            if method == 'GET':
                shortcuts = list(item_shortcuts.values())
                self._send_json(OK, {'value': shortcuts})
                return

            # POST /shortcuts - create a new shortcut
            if method == 'POST':
                shortcut = self._read_json_body()
                shortcut_name = shortcut['name']
                item_shortcuts[shortcut_name] = shortcut
                self._send_json(CREATED, shortcut)
                return

        # DELETE /shortcuts/{shortcut_path}/{shortcut_name} - delete a shortcut
        if segment_count == 2:
            if method == 'DELETE':
                shortcut_name = segments[1]

                if shortcut_name not in item_shortcuts:
                    self._send_json(NOT_FOUND,
                        {'error': {'code': 'ShortcutNotFound', 'message': f'Shortcut {shortcut_name} not found'}})
                    return

                del item_shortcuts[shortcut_name]
                self._send_empty(OK)
                return

        # Nothing above handled the request, so the path or method is not supported.
        self._send_json(BAD_REQUEST,
            {'error': {'code': 'InvalidRequest', 'message': f'Unsupported request: {method} {self.path}'}})

# ################################################################################################################################

    def _handle_items_request(self, method:'str', workspace_id:'str', segments:'list', params:'anydict') -> 'None':
        """ Items in a workspace - lakehouses, notebooks, pipelines and their jobs and shortcuts.
        Segments are the path elements after /items, e.g. ['item-sales-lakehouse', 'shortcuts'].
        """
        workspace_items = self.items[workspace_id]

        segment_count = len(segments)

        if segment_count == 0:

            # GET /items - list the workspace's items, optionally filtered by type
            if method == 'GET':
                item_type = params.get('type', [''])[0]

                items = []
                for item in workspace_items.values():
                    if item_type:
                        if item['type'] != item_type:
                            continue
                    items.append(item)

                self._send_json(OK, {'value': items})
                return

            # POST /items - create a new item
            if method == 'POST':
                request_data = self._read_json_body()

                item_id = self._next_id('item')
                item = {
                    'id': item_id,
                    'workspaceId': workspace_id,
                    'displayName': request_data['displayName'],
                    'description': request_data.get('description', ''),
                    'type': request_data['type'],
                }
                workspace_items[item_id] = item

                self._send_json(CREATED, item)
                return

        # Anything below this point points to a specific item
        item_id = segments[0]

        if item_id not in workspace_items:
            self._send_json(NOT_FOUND,
                {'error': {'code': 'ItemNotFound', 'message': f'Item {item_id} not found'}})
            return

        item = workspace_items[item_id]

        if segment_count == 1:

            # GET /items/{item_id} - a single item
            if method == 'GET':
                self._send_json(OK, item)
                return

            # PATCH /items/{item_id} - update an item
            if method == 'PATCH':
                request_data = self._read_json_body()
                item.update(request_data)
                self._send_json(OK, item)
                return

            # DELETE /items/{item_id} - delete an item
            if method == 'DELETE':
                del workspace_items[item_id]
                self._send_empty(OK)
                return

        # The item's job instances live under /items/{item_id}/jobs/instances
        if segment_count >= 3:
            if segments[1] == 'jobs':
                if segments[2] == 'instances':
                    self._handle_jobs_request(method, workspace_id, item_id, segments[3:], params)
                    return

        # The item's shortcuts live under /items/{item_id}/shortcuts
        if segment_count >= 2:
            if segments[1] == 'shortcuts':
                self._handle_shortcuts_request(method, workspace_id, item_id, segments[2:])
                return

        # Nothing above handled the request, so the path or method is not supported.
        self._send_json(BAD_REQUEST,
            {'error': {'code': 'InvalidRequest', 'message': f'Unsupported request: {method} {self.path}'}})

# ################################################################################################################################

    def _handle_workspaces_request(self, method:'str', segments:'list', params:'anydict') -> 'None':
        """ The workspace management API - workspaces and everything nested under them.
        Segments are the path elements after /workspaces, e.g. ['workspace-sales-analytics', 'items'].
        """
        segment_count = len(segments)

        if segment_count == 0:

            # GET /workspaces - list all the workspaces
            if method == 'GET':
                workspaces = list(self.workspaces.values())
                self._send_json(OK, {'value': workspaces})
                return

            # POST /workspaces - create a new workspace
            if method == 'POST':
                request_data = self._read_json_body()

                workspace_id = self._next_id('workspace')
                workspace = {
                    'id': workspace_id,
                    'displayName': request_data['displayName'],
                    'description': request_data.get('description', ''),
                    'type': 'Workspace',
                    'capacityId': 'capacity-main',
                }

                FabricTestHandler.workspaces[workspace_id] = workspace
                FabricTestHandler.items[workspace_id] = {}
                FabricTestHandler.onelake_files[workspace_id] = {}

                self._send_json(CREATED, workspace)
                return

        # Anything below this point points to a specific workspace
        workspace_id = segments[0]

        if workspace_id not in self.workspaces:
            self._send_json(NOT_FOUND,
                {'error': {'code': 'WorkspaceNotFound', 'message': f'Workspace {workspace_id} not found'}})
            return

        workspace = self.workspaces[workspace_id]

        if segment_count == 1:

            # GET /workspaces/{workspace_id} - a single workspace
            if method == 'GET':
                self._send_json(OK, workspace)
                return

            # DELETE /workspaces/{workspace_id} - delete a workspace
            if method == 'DELETE':
                del FabricTestHandler.workspaces[workspace_id]
                del FabricTestHandler.items[workspace_id]
                self._send_empty(OK)
                return

        # The workspace's items live under /workspaces/{workspace_id}/items
        if segment_count >= 2:
            if segments[1] == 'items':
                self._handle_items_request(method, workspace_id, segments[2:], params)
                return

        # Nothing above handled the request, so the path or method is not supported.
        self._send_json(BAD_REQUEST,
            {'error': {'code': 'InvalidRequest', 'message': f'Unsupported request: {method} {self.path}'}})

# ################################################################################################################################

    def _handle_onelake_request(self, method:'str', path:'str', params:'anydict') -> 'None':
        """ The OneLake data plane - ADLS-style file listing, reads, writes and deletes.
        The path is everything after the /onelake prefix, e.g. /workspace-sales-analytics/item-sales-lakehouse/Files/a.csv.
        """
        segments = []

        for segment in path.split('/'):
            if segment:
                segments.append(segment)

        if not segments:
            self._send_json(BAD_REQUEST,
                {'error': {'code': 'InvalidRequest', 'message': 'A workspace is required in OneLake paths'}})
            return

        workspace_id = segments[0]

        if workspace_id not in self.onelake_files:
            self._send_json(NOT_FOUND,
                {'error': {'code': 'FilesystemNotFound', 'message': f'Filesystem {workspace_id} not found'}})
            return

        workspace_files = self.onelake_files[workspace_id]
        file_path = '/'.join(segments[1:])

        # GET /{workspace}?resource=filesystem - list paths, optionally under a directory
        if params.get('resource', [''])[0] == 'filesystem':
            if method == 'GET':
                directory = params.get('directory', [''])[0]

                paths = []
                for name in sorted(workspace_files):
                    if directory:
                        if not name.startswith(directory):
                            continue
                    paths.append({'name': name, 'isDirectory': False})

                self._send_json(OK, {'paths': paths})
                return

        # PUT /{workspace}/{file_path}?resource=file - create an empty file
        if method == 'PUT':
            if params.get('resource', [''])[0] == 'file':
                workspace_files[file_path] = b''
                self._send_empty(CREATED)
                return

        if method == 'PATCH':

            action = params.get('action', [''])[0]

            # PATCH /{workspace}/{file_path}?action=append&position=N - append data to a file
            if action == 'append':
                if file_path not in workspace_files:
                    self._send_json(NOT_FOUND,
                        {'error': {'code': 'PathNotFound', 'message': f'Path {file_path} not found'}})
                    return

                body = self._read_body()
                workspace_files[file_path] = workspace_files[file_path] + body
                self._send_empty(ACCEPTED)
                return

            # PATCH /{workspace}/{file_path}?action=flush&position=N - make the appended data visible
            if action == 'flush':
                if file_path not in workspace_files:
                    self._send_json(NOT_FOUND,
                        {'error': {'code': 'PathNotFound', 'message': f'Path {file_path} not found'}})
                    return

                self._send_empty(OK)
                return

        # GET /{workspace}/{file_path} - read a file
        if method == 'GET':
            if file_path not in workspace_files:
                self._send_json(NOT_FOUND,
                    {'error': {'code': 'PathNotFound', 'message': f'Path {file_path} not found'}})
                return

            self._send_bytes(OK, workspace_files[file_path])
            return

        # DELETE /{workspace}/{file_path} - delete a file
        if method == 'DELETE':
            if file_path not in workspace_files:
                self._send_json(NOT_FOUND,
                    {'error': {'code': 'PathNotFound', 'message': f'Path {file_path} not found'}})
                return

            del workspace_files[file_path]
            self._send_empty(OK)
            return

        # Nothing above handled the request, so the path or method is not supported.
        self._send_json(BAD_REQUEST,
            {'error': {'code': 'InvalidRequest', 'message': f'Unsupported request: {method} {self.path}'}})

# ################################################################################################################################

    def _handle_request(self, method:'str') -> 'None':

        parsed_path = urlparse(self.path)
        path = parsed_path.path
        params = parse_qs(parsed_path.query)

        # The token endpoint requires no bearer token - it is where tokens come from.
        token_path = f'/{self.expected_tenant_id}/oauth2/v2.0/token'
        if path == token_path:
            if method == 'POST':
                self._handle_token_request()
                return

        # Everything else requires a valid token ..
        if not self._check_token():
            self._send_json(UNAUTHORIZED,
                {'error': {'code': 'InvalidAuthenticationToken', 'message': 'Access token is missing or invalid'}})
            return

        # .. the OneLake data plane lives under its own prefix ..
        if path.startswith(_onelake_prefix):
            onelake_path = path[len(_onelake_prefix):]
            self._handle_onelake_request(method, onelake_path, params)
            return

        # .. capacities are a small read-only API ..
        if path == '/capacities':
            if method == 'GET':
                capacities = list(self.capacities.values())
                self._send_json(OK, {'value': capacities})
                return

        # .. and everything under /workspaces is the workspace management API.
        if path.startswith('/workspaces'):
            workspaces_path = path[len('/workspaces'):]
            segments = []

            for segment in workspaces_path.split('/'):
                if segment:
                    segments.append(segment)

            self._handle_workspaces_request(method, segments, params)
            return

        # No handler matched the path.
        self._send_json(NOT_FOUND, {'error': {'code': 'ResourceNotFound', 'message': f'No such path: {path}'}})

# ################################################################################################################################

    def do_GET(self) -> 'None':
        self._handle_request('GET')

# ################################################################################################################################

    def do_POST(self) -> 'None':
        self._handle_request('POST')

# ################################################################################################################################

    def do_PATCH(self) -> 'None':
        self._handle_request('PATCH')

# ################################################################################################################################

    def do_PUT(self) -> 'None':
        self._handle_request('PUT')

# ################################################################################################################################

    def do_DELETE(self) -> 'None':
        self._handle_request('DELETE')

# ################################################################################################################################
# ################################################################################################################################

def start_fabric_server(
    port:'int',
    tenant_id:'str',
    client_id:'str',
    client_secret:'str',
    ) -> 'tuple':
    """ Starts the simulated Fabric tenant in a background thread. Returns (server, thread).
    """
    FabricTestHandler.expected_tenant_id = tenant_id
    FabricTestHandler.expected_client_id = client_id
    FabricTestHandler.expected_client_secret = client_secret

    FabricTestHandler.valid_tokens = {}
    FabricTestHandler.workspaces = _build_initial_workspaces()
    FabricTestHandler.items = _build_initial_items()
    FabricTestHandler.jobs = _build_initial_jobs()
    FabricTestHandler.shortcuts = _build_initial_shortcuts()
    FabricTestHandler.onelake_files = _build_initial_onelake_files()
    FabricTestHandler.capacities = _build_capacities()
    FabricTestHandler.object_counter = 0

    server = ThreadingHTTPServer(('127.0.0.1', port), FabricTestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    return server, thread

# ################################################################################################################################
# ################################################################################################################################
