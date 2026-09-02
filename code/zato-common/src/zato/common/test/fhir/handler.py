# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from http.client import BAD_REQUEST, CREATED, GONE, NO_CONTENT, NOT_FOUND, OK, UNAUTHORIZED
from http.server import BaseHTTPRequestHandler
from logging import getLogger
from urllib.parse import parse_qsl, urlsplit
from uuid import uuid4

# Zato
from zato.common.test.fhir.bundles import handle_bundle
from zato.common.test.fhir.common import auth_type_basic, fhir_content_type, fhir_version, grant_type_client_credentials, \
    json_content_type, token_lifetime, token_path
from zato.common.test.fhir.store import search_parameter_list, utc_now_instant
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.fhir.common import FHIRHTTPServer, OAuthTokenIssuer
    from zato.common.typing_ import any_, dictlist, stranydict, strlist, strstrdict
    OAuthTokenIssuer = OAuthTokenIssuer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def is_resource_type(name:'str') -> 'bool':
    """ Returns True if the name has the shape of a FHIR resource type, e.g. Patient or StructureDefinition.
    """
    is_alphanumeric = name.isalnum()

    out = is_alphanumeric and name[0].isupper()
    return out

# ################################################################################################################################
# ################################################################################################################################

class FHIRRequestHandler(BaseHTTPRequestHandler):
    """ Implements the FHIR R4 RESTful API - capabilities, create, read, vread, update, patch, delete and search.
    """
    server: 'FHIRHTTPServer'

    # HTTP/1.1 keeps connections alive, which pooled clients expect
    protocol_version = 'HTTP/1.1'

    def log_message(self, format:'str', *arguments:'any_') -> 'None':
        """ Routes HTTP server log messages through the module logger.
        """
        message = format % arguments
        logger.debug('[FHIR test server] %s', message)

# ################################################################################################################################

    def send_json(
        self,
        status:'int',
        payload:'stranydict',
        extra_headers:'strstrdict | None'=None,
        is_fhir:'bool'=True
        ) -> 'None':
        """ Sends a JSON payload with the FHIR media type, or the plain JSON one for OAuth responses,
        and any extra headers.
        """
        body = json.dumps(payload)
        body = body.encode('utf8')

        if is_fhir:
            content_type = fhir_content_type
        else:
            content_type = json_content_type

        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))

        if extra_headers:
            for name, value in extra_headers.items():
                self.send_header(name, value)

        self.end_headers()
        _ = self.wfile.write(body)

# ################################################################################################################################

    def send_outcome(self, status:'int', code:'str', diagnostics:'str') -> 'None':
        """ Sends an OperationOutcome, which is how the spec reports all errors.
        """
        outcome = {
            'resourceType': 'OperationOutcome',
            'issue': [{
                'severity': 'error',
                'code': code,
                'diagnostics': diagnostics,
            }]
        }

        self.send_json(status, outcome)

# ################################################################################################################################

    def _send_no_content(self) -> 'None':
        """ Sends an empty 204 response, which is what a successful delete returns.
        """
        self.send_response(NO_CONTENT)
        self.send_header('Content-Length', '0')
        self.end_headers()

# ################################################################################################################################

    def _send_unauthorized(self, scheme:'str') -> 'None':
        """ Sends a 401 response with the challenge for the given scheme.
        """
        self.send_response(UNAUTHORIZED)
        self.send_header('WWW-Authenticate', f'{scheme} realm="Zato FHIR test server"')
        self.send_header('Content-Length', '0')
        self.end_headers()

# ################################################################################################################################

    def _check_auth(self) -> 'bool':
        """ Verifies Basic Auth or an OAuth bearer token, depending on how the server was started.
        The capabilities interaction and the token endpoint are exempt - the spec recommends
        the former be accessible without authorization and the latter is where tokens come from.
        """

        # No authentication configured means everything is open ..
        auth_type = self.server.auth_type
        if not auth_type:
            out = True
            return out

        # .. the capability statement and the token endpoint are always open ..
        path = urlsplit(self.path).path
        if path in ('/metadata', token_path):
            out = True
            return out

        received = self.headers.get('Authorization')

        # .. Basic Auth must carry the exact expected header ..
        if auth_type == auth_type_basic:

            if received == self.server.auth_header:
                out = True
            else:
                self._send_unauthorized('Basic')
                out = False

            return out

        # .. and OAuth must carry a bearer token this server has issued.
        else:

            # The issuer is always configured when the auth type is OAuth
            token_issuer = cast_('OAuthTokenIssuer', self.server.token_issuer)

            if received:
                if received.startswith('Bearer '):
                    token = received.split(' ', 1)[1]

                    if token_issuer.validate(token):
                        out = True
                        return out

            self._send_unauthorized('Bearer')

            out = False
            return out

# ################################################################################################################################

    def read_body(self) -> 'stranydict | None':
        """ Reads and parses the JSON request body, sending a 400 OperationOutcome if it is invalid.
        """

        # An absent Content-Length means an empty body, which is invalid for create and update
        content_length = self.headers.get('Content-Length')
        if content_length is None:
            content_length = '0'
        content_length = int(content_length)

        body = self.rfile.read(content_length)

        try:
            out = json.loads(body)
        except json.JSONDecodeError as e:
            self.send_outcome(BAD_REQUEST, 'structure', f'Request body is not valid JSON -> {e}')
            out = None

        return out

# ################################################################################################################################

    def _split_path(self) -> 'tuple[strlist, search_parameter_list]':
        """ Splits the request path into its segments and parses the query string.
        """
        parsed = urlsplit(self.path)

        segments:'strlist' = []

        for part in parsed.path.split('/'):
            if part:
                segments.append(part)

        parameters = parse_qsl(parsed.query)

        out = (segments, parameters)
        return out

# ################################################################################################################################

    def _build_capability_statement(self) -> 'stranydict':
        """ Builds a CapabilityStatement for this running instance, per the spec's capabilities interaction.
        """

        # The spec requires kind=instance statements to describe the implementation they document
        out = {
            'resourceType': 'CapabilityStatement',
            'id': 'zato-fhir-test-server',
            'status': 'active',
            'date': utc_now_instant(),
            'kind': 'instance',
            'software': {
                'name': 'Zato FHIR test server',
            },
            'implementation': {
                'description': 'An in-memory FHIR server for Zato tests',
                'url': self.server.base_address,
            },
            'fhirVersion': fhir_version,
            'format': ['json'],
            'rest': [{
                'mode': 'server',
            }]
        }

        return out

# ################################################################################################################################

    def _handle_search(self, resource_type:'str', parameters:'search_parameter_list') -> 'None':
        """ Handles the search interaction, returning a searchset Bundle.
        """

        # Find everything that matches ..
        matches = self.server.store.search(resource_type, parameters)

        # .. the total reflects all the matches, even if _count truncates the entries below ..
        total = len(matches)

        # .. honor _count, which limits how many entries are returned ..
        for name, value in parameters:
            if name == '_count':
                count = int(value)
                matches = matches[:count]

        # .. build the entries, each pointing back to its resource ..
        entries:'dictlist' = []

        for resource in matches:
            resource_id = resource['id']
            entry = {
                'fullUrl': f'{self.server.base_address}/{resource_type}/{resource_id}',
                'resource': resource,
                'search': {
                    'mode': 'match',
                }
            }
            entries.append(entry)

        # .. and wrap them all in a searchset Bundle.
        bundle = {
            'resourceType': 'Bundle',
            'id': uuid4().hex,
            'type': 'searchset',
            'total': total,
            'link': [{
                'relation': 'self',
                'url': f'{self.server.base_address}{self.path}',
            }],
            'entry': entries,
        }

        self.send_json(OK, bundle)

# ################################################################################################################################

    def _handle_read(self, resource_type:'str', resource_id:'str') -> 'None':
        """ Handles the read interaction, including 410 Gone for deleted resources.
        """
        result = self.server.store.read(resource_type, resource_id)

        # Deleted resources are reported as gone, not as never having existed ..
        if result.is_deleted:
            self.send_outcome(GONE, 'deleted', f'Resource {resource_type}/{resource_id} has been deleted')
            return

        # .. resources with no history at all were never there ..
        if result.resource is None:
            self.send_outcome(NOT_FOUND, 'not-found', f'No such resource -> {resource_type}/{resource_id}')
            return

        # .. otherwise, return the current version with its metadata headers.
        meta = result.resource['meta']
        version_id = meta['versionId']
        last_modified = self.server.store.get_last_modified(resource_type, resource_id)

        headers = {
            'ETag': f'W/"{version_id}"',
            'Last-Modified': last_modified,
        }

        self.send_json(OK, result.resource, headers)

# ################################################################################################################################

    def _handle_vread(self, resource_type:'str', resource_id:'str', version_id:'str') -> 'None':
        """ Handles the vread interaction - historical versions stay readable even after deletion.
        """
        resource = self.server.store.vread(resource_type, resource_id, version_id)

        if resource is None:
            diagnostics = f'No such version -> {resource_type}/{resource_id}/_history/{version_id}'
            self.send_outcome(NOT_FOUND, 'not-found', diagnostics)
            return

        headers = {
            'ETag': f'W/"{version_id}"',
        }

        self.send_json(OK, resource, headers)

# ################################################################################################################################

    def do_GET(self) -> 'None': # noqa: N802
        """ Dispatches GET requests to capabilities, search, read or vread.
        """
        if not self._check_auth():
            return

        segments, parameters = self._split_path()
        segment_count = len(segments)

        # The capability statement is served under /metadata ..
        if segments == ['metadata']:
            statement = self._build_capability_statement()
            self.send_json(OK, statement)
            return

        # .. everything else starts with a resource type.
        if segment_count == 0:
            self.send_outcome(NOT_FOUND, 'not-found', 'No interaction at the base URL')
            return

        resource_type = segments[0]

        if not is_resource_type(resource_type):
            self.send_outcome(NOT_FOUND, 'not-found', f'Not a resource type -> {resource_type}')
            return

        # A bare type is a search over that type ..
        if segment_count == 1:
            self._handle_search(resource_type, parameters)

        # .. a type and an ID is a read ..
        elif segment_count == 2:
            self._handle_read(resource_type, segments[1])

        # .. and a _history path is a vread.
        elif segment_count == 4:
            if segments[2] == '_history':
                self._handle_vread(resource_type, segments[1], segments[3])
            else:
                self.send_outcome(NOT_FOUND, 'not-found', f'Unrecognized path -> {self.path}')

        # .. anything else is not an interaction this server implements.
        else:
            self.send_outcome(NOT_FOUND, 'not-found', f'Unrecognized path -> {self.path}')

# ################################################################################################################################

    def _handle_token_request(self) -> 'None':
        """ Implements the token endpoint for the client credentials grant of RFC 6749,
        accepting both form-encoded and JSON requests, which is what Zato's BearerTokenManager sends.
        """

        # The issuer is always configured when this endpoint is reachable
        token_issuer = cast_('OAuthTokenIssuer', self.server.token_issuer)

        # Read the raw body ..
        content_length = self.headers.get('Content-Length')
        if content_length is None:
            content_length = '0'
        content_length = int(content_length)

        body = self.rfile.read(content_length)

        # .. parse it according to its content type ..
        content_type = self.headers.get('Content-Type')
        if content_type is None:
            content_type = ''

        if 'json' in content_type:
            try:
                request = json.loads(body)
            except json.JSONDecodeError:
                self.send_json(BAD_REQUEST, {'error': 'invalid_request'}, is_fhir=False)
                return
        else:
            request = dict(parse_qsl(body.decode('utf8')))

        # .. this grant type is the only one the server implements ..
        grant_type = request.get('grant_type')
        if grant_type != grant_type_client_credentials:
            self.send_json(BAD_REQUEST, {'error': 'unsupported_grant_type'}, is_fhir=False)
            return

        # .. issue a token if the client credentials are correct ..
        client_id = request.get('client_id')
        client_secret = request.get('client_secret')

        if client_id is None:
            client_id = ''

        if client_secret is None:
            client_secret = ''

        token = token_issuer.issue(client_id, client_secret)

        if token is None:
            self.send_json(BAD_REQUEST, {'error': 'invalid_client'}, is_fhir=False)
            return

        # .. and return it the way RFC 6749 specifies.
        response = {
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in': token_lifetime,
        }

        self.send_json(OK, response, is_fhir=False)

# ################################################################################################################################

    def do_POST(self) -> 'None': # noqa: N802
        """ Handles the create and transaction interactions and, if OAuth is configured, the token endpoint.
        """
        if not self._check_auth():
            return

        # The token endpoint exists only when the server was started with OAuth
        path = urlsplit(self.path).path
        if path == token_path:
            if self.server.token_issuer:
                self._handle_token_request()
            else:
                self.send_outcome(NOT_FOUND, 'not-found', f'Unrecognized path -> {self.path}')
            return

        segments, _ = self._split_path()
        segment_count = len(segments)

        # A POST to the base URL is a transaction or batch Bundle
        if segment_count == 0:
            handle_bundle(self)
            return

        # Otherwise, create is the POST interaction this server implements
        if segment_count != 1:
            self.send_outcome(NOT_FOUND, 'not-found', f'Unrecognized path -> {self.path}')
            return

        resource_type = segments[0]

        if not is_resource_type(resource_type):
            self.send_outcome(NOT_FOUND, 'not-found', f'Not a resource type -> {resource_type}')
            return

        resource = self.read_body()
        if resource is None:
            return

        # The body's type must agree with the endpoint it was posted to
        body_type = resource.get('resourceType')
        if body_type != resource_type:
            diagnostics = f'Resource type mismatch -> body has `{body_type}`, endpoint is `{resource_type}`'
            self.send_outcome(BAD_REQUEST, 'invalid', diagnostics)
            return

        # Store it, letting the server assign the ID ..
        resource = self.server.store.create(resource_type, resource)

        resource_id = resource['id']
        meta = resource['meta']
        version_id = meta['versionId']
        last_modified = self.server.store.get_last_modified(resource_type, resource_id)

        # .. and point the client at the newly created version.
        headers = {
            'Location': f'{self.server.base_address}/{resource_type}/{resource_id}/_history/{version_id}',
            'ETag': f'W/"{version_id}"',
            'Last-Modified': last_modified,
        }

        self.send_json(CREATED, resource, headers)

# ################################################################################################################################

    def do_PUT(self) -> 'None': # noqa: N802
        """ Handles the update interaction, including update-as-create.
        """
        if not self._check_auth():
            return

        segments, _ = self._split_path()
        segment_count = len(segments)

        # Update always addresses a specific resource.
        if segment_count != 2:
            self.send_outcome(NOT_FOUND, 'not-found', f'Unrecognized path -> {self.path}')
            return

        resource_type = segments[0]
        resource_id   = segments[1]

        if not is_resource_type(resource_type):
            self.send_outcome(NOT_FOUND, 'not-found', f'Not a resource type -> {resource_type}')
            return

        resource = self.read_body()
        if resource is None:
            return

        # The body's type must agree with the URL ..
        body_type = resource.get('resourceType')
        if body_type != resource_type:
            diagnostics = f'Resource type mismatch -> body has `{body_type}`, endpoint is `{resource_type}`'
            self.send_outcome(BAD_REQUEST, 'invalid', diagnostics)
            return

        # .. and so must its ID, which the spec requires to be present and identical.
        body_id = resource.get('id')
        if body_id != resource_id:
            diagnostics = f'Resource ID mismatch -> body has `{body_id}`, URL has `{resource_id}`'
            self.send_outcome(BAD_REQUEST, 'invalid', diagnostics)
            return

        was_created = self.server.store.put(resource_type, resource_id, resource)

        meta = resource['meta']
        version_id = meta['versionId']
        last_modified = self.server.store.get_last_modified(resource_type, resource_id)

        headers = {
            'Location': f'{self.server.base_address}/{resource_type}/{resource_id}/_history/{version_id}',
            'ETag': f'W/"{version_id}"',
            'Last-Modified': last_modified,
        }

        # Update-as-create reports 201, a plain update reports 200
        if was_created:
            status = CREATED
        else:
            status = OK

        self.send_json(status, resource, headers)

# ################################################################################################################################

    def do_PATCH(self) -> 'None': # noqa: N802
        """ Handles the patch interaction - a JSON body with the fields to change,
        merged into the current version of the resource.
        """
        if not self._check_auth():
            return

        segments, _ = self._split_path()
        segment_count = len(segments)

        # Patch always addresses a specific resource.
        if segment_count != 2:
            self.send_outcome(NOT_FOUND, 'not-found', f'Unrecognized path -> {self.path}')
            return

        resource_type = segments[0]
        resource_id   = segments[1]

        # There must be a current version to merge into.
        read_result = self.server.store.read(resource_type, resource_id)
        if read_result.resource is None:
            self.send_outcome(NOT_FOUND, 'not-found', f'No such resource -> {resource_type}/{resource_id}')
            return

        changes = self.read_body()
        if changes is None:
            return

        # The merged resource keeps its stored type and ID no matter what the body says.
        resource = dict(read_result.resource)
        resource.update(changes)
        resource['resourceType'] = resource_type
        resource['id'] = resource_id

        _ = self.server.store.put(resource_type, resource_id, resource)

        meta = resource['meta']
        version_id = meta['versionId']
        last_modified = self.server.store.get_last_modified(resource_type, resource_id)

        headers = {
            'Location': f'{self.server.base_address}/{resource_type}/{resource_id}/_history/{version_id}',
            'ETag': f'W/"{version_id}"',
            'Last-Modified': last_modified,
        }

        self.send_json(OK, resource, headers)

# ################################################################################################################################

    def do_DELETE(self) -> 'None': # noqa: N802
        """ Handles the delete interaction - deletes are idempotent and reads afterwards return 410 Gone.
        """
        if not self._check_auth():
            return

        segments, _ = self._split_path()
        segment_count = len(segments)

        # Delete always addresses a specific resource.
        if segment_count != 2:
            self.send_outcome(NOT_FOUND, 'not-found', f'Unrecognized path -> {self.path}')
            return

        resource_type = segments[0]
        resource_id   = segments[1]

        was_found = self.server.store.delete(resource_type, resource_id)

        if was_found:
            self._send_no_content()
        else:
            self.send_outcome(NOT_FOUND, 'not-found', f'No such resource -> {resource_type}/{resource_id}')

# ################################################################################################################################
# ################################################################################################################################
