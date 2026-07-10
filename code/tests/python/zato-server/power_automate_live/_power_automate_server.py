# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import threading
import time
from http.client import ACCEPTED, BAD_REQUEST, NOT_FOUND, OK, UNAUTHORIZED
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

# The URL path prefix of the flow management API.
_api_prefix = '/providers/Microsoft.ProcessSimple/environments'

# The URL path prefix of HTTP request triggers.
_trigger_prefix = '/powerautomate/triggers'

# ################################################################################################################################
# ################################################################################################################################

def _build_initial_flows() -> 'anydict':
    """ Returns the flows the simulated environment starts with.
    """
    return {
        'flow-invoice-approval': {
            'name': 'flow-invoice-approval',
            'id': f'{_api_prefix}/test-environment/flows/flow-invoice-approval',
            'type': 'Microsoft.ProcessSimple/environments/flows',
            'properties': {
                'displayName': 'Invoice approval',
                'state': 'Started',
                'createdTime': '2026-01-10T09:30:00Z',
            },
        },
        'flow-customer-notifications': {
            'name': 'flow-customer-notifications',
            'id': f'{_api_prefix}/test-environment/flows/flow-customer-notifications',
            'type': 'Microsoft.ProcessSimple/environments/flows',
            'properties': {
                'displayName': 'Customer notifications',
                'state': 'Stopped',
                'createdTime': '2026-02-20T14:15:00Z',
            },
        },
    }

# ################################################################################################################################

def _build_initial_runs() -> 'anydict':
    """ Returns the run history the simulated environment starts with.
    """
    return {
        'flow-invoice-approval': {
            'run-invoice-001': {
                'name': 'run-invoice-001',
                'type': 'Microsoft.ProcessSimple/environments/flows/runs',
                'properties': {
                    'status': 'Succeeded',
                    'startTime': '2026-07-01T08:00:00Z',
                    'endTime': '2026-07-01T08:00:12Z',
                },
            },
            'run-invoice-002': {
                'name': 'run-invoice-002',
                'type': 'Microsoft.ProcessSimple/environments/flows/runs',
                'properties': {
                    'status': 'Running',
                    'startTime': '2026-07-02T10:30:00Z',
                },
            },
        },
        'flow-customer-notifications': {},
    }

# ################################################################################################################################
# ################################################################################################################################

class PowerAutomateTestHandler(BaseHTTPRequestHandler):

    # Credentials the token endpoint accepts
    expected_tenant_id:'strnone' = None
    expected_client_id:'strnone' = None
    expected_client_secret:'strnone' = None

    # The environment the flow management API serves
    environment_id:'strnone' = None

    # The port this server listens on, used to build trigger callback URLs
    port = 0

    # All the tokens issued so far, mapped to when they expire
    valid_tokens:'anydict' = {}

    # The state of the simulated environment
    flows:'anydict' = {}
    runs:'anydict' = {}

    # Payloads that HTTP request triggers received
    received_trigger_payloads = []

    # How many runs were created by triggers and resubmissions, used to build new run IDs
    run_counter = 0

    def log_message(self, format, *args) -> 'None':
        pass

# ################################################################################################################################

    @classmethod
    def invalidate_tokens(class_) -> 'None':
        """ Makes all the previously issued tokens invalid, which forces clients to obtain new ones.
        """
        class_.valid_tokens = {}

# ################################################################################################################################

    def _send_json(self, status:'int', data:'anydict') -> 'None':
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        body = json.dumps(data)
        _ = self.wfile.write(body.encode('utf-8'))

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
        """ An Azure-AD-style OAuth2 token endpoint for the client credentials grant.
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
        PowerAutomateTestHandler.valid_tokens[token] = now + _token_lifetime

        self._send_json(OK, {
            'token_type': 'Bearer',
            'expires_in': _token_lifetime,
            'access_token': token,
        })

# ################################################################################################################################

    def _handle_trigger_request(self, flow_id:'str') -> 'None':
        """ An HTTP request trigger - records the payload it received and starts a new run.
        The callback URL carries its own signature so no bearer token is expected here.
        """
        body = self._read_body()

        if body:
            payload = json.loads(body)
        else:
            payload = None

        PowerAutomateTestHandler.received_trigger_payloads.append({
            'flow_id': flow_id,
            'payload': payload,
        })

        # Each trigger invocation starts a new run of the flow.
        run_id = self._create_run(flow_id)

        self._send_json(ACCEPTED, {'run_id': run_id})

# ################################################################################################################################

    def _create_run(self, flow_id:'str') -> 'str':
        """ Adds a new, running run to a flow's history and returns its ID.
        """
        PowerAutomateTestHandler.run_counter += 1
        run_id = f'run-new-{PowerAutomateTestHandler.run_counter:03}'

        flow_runs = self.runs.setdefault(flow_id, {})
        flow_runs[run_id] = {
            'name': run_id,
            'type': 'Microsoft.ProcessSimple/environments/flows/runs',
            'properties': {
                'status': 'Running',
                'startTime': '2026-07-10T12:00:00Z',
            },
        }

        return run_id

# ################################################################################################################################

    def _handle_flows_request(self, method:'str', segments:'list') -> 'None':
        """ The flow management API - flows, runs, triggers.
        Segments are the path elements after /flows, e.g. ['flow-invoice-approval', 'start'].
        """
        segment_count = len(segments)

        # GET /flows - list all the flows
        if segment_count == 0:
            if method == 'GET':
                flows = list(self.flows.values())
                self._send_json(OK, {'value': flows})
                return

        # Anything below this point points to a specific flow
        flow_id = segments[0]

        if flow_id not in self.flows:
            self._send_json(NOT_FOUND, {'error': {'code': 'FlowNotFound', 'message': f'Flow {flow_id} not found'}})
            return

        flow = self.flows[flow_id]

        # GET /flows/{flow_id} - a single flow
        if segment_count == 1:
            if method == 'GET':
                self._send_json(OK, flow)
                return

        if segment_count == 2:

            # POST /flows/{flow_id}/start - turn the flow on
            if segments[1] == 'start':
                if method == 'POST':
                    flow['properties']['state'] = 'Started'
                    self._send_empty(OK)
                    return

            # POST /flows/{flow_id}/stop - turn the flow off
            if segments[1] == 'stop':
                if method == 'POST':
                    flow['properties']['state'] = 'Stopped'
                    self._send_empty(OK)
                    return

            # GET /flows/{flow_id}/runs - the flow's run history
            if segments[1] == 'runs':
                if method == 'GET':
                    flow_runs = self.runs[flow_id]
                    runs = list(flow_runs.values())
                    self._send_json(OK, {'value': runs})
                    return

        if segment_count == 3:

            # GET /flows/{flow_id}/runs/{run_id} - a single run
            if segments[1] == 'runs':
                if method == 'GET':
                    run_id = segments[2]
                    flow_runs = self.runs[flow_id]

                    if run_id not in flow_runs:
                        self._send_json(NOT_FOUND,
                            {'error': {'code': 'RunNotFound', 'message': f'Run {run_id} not found'}})
                        return

                    self._send_json(OK, flow_runs[run_id])
                    return

        if segment_count == 4:

            # POST /flows/{flow_id}/runs/{run_id}/cancel - cancel a run
            if segments[1] == 'runs':
                if segments[3] == 'cancel':
                    if method == 'POST':
                        run_id = segments[2]
                        flow_runs = self.runs[flow_id]

                        if run_id not in flow_runs:
                            self._send_json(NOT_FOUND,
                                {'error': {'code': 'RunNotFound', 'message': f'Run {run_id} not found'}})
                            return

                        run = flow_runs[run_id]
                        run['properties']['status'] = 'Cancelled'
                        self._send_empty(OK)
                        return

            # POST /flows/{flow_id}/triggers/{trigger_name}/listCallbackUrl - the trigger's callback URL
            if segments[1] == 'triggers':
                if segments[3] == 'listCallbackUrl':
                    if method == 'POST':
                        signature = CryptoManager.generate_hex_string()
                        callback_url = f'http://127.0.0.1:{self.port}{_trigger_prefix}/{flow_id}/invoke?sig={signature}'
                        self._send_json(OK, {'response': {'value': callback_url}})
                        return

        if segment_count == 6:

            # POST /flows/{flow_id}/triggers/{trigger_name}/histories/{run_id}/resubmit - run the flow again
            if segments[1] == 'triggers':
                if segments[3] == 'histories':
                    if segments[5] == 'resubmit':
                        if method == 'POST':
                            _ = self._create_run(flow_id)
                            self._send_empty(ACCEPTED)
                            return

        # Nothing above handled the request, so the path or method is not supported.
        self._send_json(BAD_REQUEST,
            {'error': {'code': 'InvalidRequest', 'message': f'Unsupported request: {method} {self.path}'}})

# ################################################################################################################################

    def _handle_request(self, method:'str') -> 'None':

        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # The token endpoint requires no bearer token - it is where tokens come from.
        token_path = f'/{self.expected_tenant_id}/oauth2/v2.0/token'
        if path == token_path:
            if method == 'POST':
                self._handle_token_request()
                return

        # HTTP request triggers are authorized through the signature in their URL, not through bearer tokens.
        if path.startswith(_trigger_prefix):
            if method == 'POST':
                trigger_path = path[len(_trigger_prefix):]
                flow_id = trigger_path.strip('/').split('/')[0]
                self._handle_trigger_request(flow_id)
                return

        # Everything else is the flow management API which requires a valid token ..
        if not self._check_token():
            self._send_json(UNAUTHORIZED,
                {'error': {'code': 'InvalidAuthenticationToken', 'message': 'Access token is missing or invalid'}})
            return

        # .. and it is always scoped to the environment this server simulates.
        environment_prefix = f'{_api_prefix}/{self.environment_id}/flows'

        if path.startswith(environment_prefix):
            flows_path = path[len(environment_prefix):]
            segments = []

            for segment in flows_path.split('/'):
                if segment:
                    segments.append(segment)

            self._handle_flows_request(method, segments)
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
# ################################################################################################################################

def start_power_automate_server(
    port:'int',
    tenant_id:'str',
    client_id:'str',
    client_secret:'str',
    environment_id:'str',
    ) -> 'tuple':
    """ Starts the simulated Power Automate environment in a background thread. Returns (server, thread).
    """
    PowerAutomateTestHandler.expected_tenant_id = tenant_id
    PowerAutomateTestHandler.expected_client_id = client_id
    PowerAutomateTestHandler.expected_client_secret = client_secret
    PowerAutomateTestHandler.environment_id = environment_id
    PowerAutomateTestHandler.port = port

    PowerAutomateTestHandler.valid_tokens = {}
    PowerAutomateTestHandler.flows = _build_initial_flows()
    PowerAutomateTestHandler.runs = _build_initial_runs()
    PowerAutomateTestHandler.received_trigger_payloads = []
    PowerAutomateTestHandler.run_counter = 0

    server = ThreadingHTTPServer(('127.0.0.1', port), PowerAutomateTestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    return server, thread

# ################################################################################################################################
# ################################################################################################################################
