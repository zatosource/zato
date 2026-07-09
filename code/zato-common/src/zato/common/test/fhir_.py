# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import socket
import threading
from base64 import b64encode
from datetime import datetime, timezone
from email.utils import formatdate
from http.client import BAD_REQUEST, CREATED, GONE, NO_CONTENT, NOT_FOUND, OK, UNAUTHORIZED
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from logging import getLogger
from time import sleep, time
from typing import NamedTuple
from urllib.parse import parse_qsl, urlsplit
from uuid import uuid4

# Zato
from zato.common.api import HL7
from zato.common.typing_ import cast_
from zato.common.util.tcp import get_free_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anytuple, dictlist, stranydict, strlist, strnone, strset, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# A list of consecutive versions of one resource, oldest first
version_list = list['stranydict']

# Maps 'Type/id' keys to the version history of that resource
version_dict = dict[str, version_list]

# A list of resources matched by a search
resource_list = list['stranydict']

# Search parameters as a list of name/value pairs
search_parameter_list = list[tuple[str, str]]

# Maps issued OAuth tokens to their expiration time as a Unix timestamp
token_dict = dict[str, float]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The FHIR version this server implements
_fhir_version = '4.0.1'

# The media type for FHIR JSON, per the spec's http.html#mime-type
_fhir_content_type = 'application/fhir+json; charset=utf-8'

# The media type for OAuth token responses, per RFC 6749
_json_content_type = 'application/json; charset=utf-8'

# The version ID assigned to the first version of each resource
_first_version_id = '1'

# How long to wait for the server to start accepting connections, in seconds
_start_timeout = 10.0

# How long to sleep between connection attempts while waiting for the server, in seconds
_start_sleep_time = 0.1

# The auth types the server supports, the same IDs the FHIR outgoing connection uses
_auth_type_basic = HL7.Const.FHIR_Auth_Type.Basic_Auth.id
_auth_type_oauth = HL7.Const.FHIR_Auth_Type.OAuth.id

# Where OAuth tokens are issued, per RFC 6749's client credentials grant
_token_path = '/oauth/token'

# How long issued OAuth tokens are valid for, in seconds
_token_lifetime = 3600

# The only grant type the token endpoint implements
_grant_type_client_credentials = 'client_credentials'

# The bundle types the base-URL POST interaction accepts, per the spec's transaction interaction
_bundle_request_types = {
    'transaction': 'transaction-response',
    'batch': 'batch-response',
}

# ################################################################################################################################
# ################################################################################################################################

class _ReadResult(NamedTuple):
    """ What the store returns for a read - the resource is None if it never existed.
    """
    resource: 'stranydict | None'
    is_deleted: bool

# ################################################################################################################################
# ################################################################################################################################

def _collect_string_leaves(value:'any_', out:'strlist') -> 'None':
    """ Recursively collects all string values found in a JSON-like structure.
    """
    if isinstance(value, str):
        out.append(value)

    elif isinstance(value, list):
        for item in value:
            _collect_string_leaves(item, out)

    elif isinstance(value, dict):
        for item in value.values():
            _collect_string_leaves(item, out)

# ################################################################################################################################

def _is_resource_type(name:'str') -> 'bool':
    """ Returns True if the name has the shape of a FHIR resource type, e.g. Patient or StructureDefinition.
    """
    is_alphanumeric = name.isalnum()

    out = is_alphanumeric and name[0].isupper()
    return out

# ################################################################################################################################

def _utc_now_instant() -> 'str':
    """ Returns the current UTC time as a FHIR instant, e.g. 2026-07-04T13:33:12.123456+00:00.
    """
    now = datetime.now(timezone.utc)

    out = now.isoformat()
    return out

# ################################################################################################################################
# ################################################################################################################################

class _FHIRStore:
    """ A thread-safe, in-memory, versioned store of FHIR resources.
    """
    def __init__(self) -> 'None':

        # Maps 'Type/id' to the list of all versions of that resource, oldest first
        self._versions:'version_dict' = {}

        # Keys of resources that have been deleted - reads return 410 Gone for them
        self._deleted:'strset' = set()

        # Maps 'Type/id' to the HTTP-date of its last modification, for the Last-Modified header
        self._last_modified:'strstrdict' = {}

        # Serializes all access to the dictionaries above
        self._lock = threading.Lock()

# ################################################################################################################################

    def _store_version(self, key:'str', resource:'stranydict', version_id:'str') -> 'None':
        """ Appends a new version of a resource under the given key. Must be called under self._lock.
        """

        # Each stored version carries its own metadata, as the spec requires ..
        meta = resource.setdefault('meta', {})
        meta['versionId'] = version_id
        meta['lastUpdated'] = _utc_now_instant()

        # .. append it to the history ..
        versions = self._versions.setdefault(key, [])
        versions.append(resource)

        # .. remember when it was modified, for the Last-Modified header ..
        self._last_modified[key] = formatdate(usegmt=True)

        # .. and make sure the resource is not considered deleted anymore.
        self._deleted.discard(key)

# ################################################################################################################################

    def create(self, resource_type:'str', resource:'stranydict') -> 'stranydict':
        """ Creates a new resource, assigning it a server-side ID, per the spec's create interaction.
        """

        # The server ignores any client-supplied ID on create, as the spec recommends
        resource_id = uuid4().hex
        resource['id'] = resource_id

        key = f'{resource_type}/{resource_id}'

        with self._lock:
            self._store_version(key, resource, _first_version_id)

        return resource

# ################################################################################################################################

    def put(self, resource_type:'str', resource_id:'str', resource:'stranydict') -> 'bool':
        """ Updates a resource, or creates it if it does not exist yet (update-as-create).
        Returns True if the resource was created rather than updated.
        """
        key = f'{resource_type}/{resource_id}'

        with self._lock:

            # A deleted resource is brought back by an update, continuing its version history ..
            versions = self._versions.get(key)

            # .. if there is no history at all, this is update-as-create ..
            if not versions:
                self._store_version(key, resource, _first_version_id)
                out = True
                return out

            # .. otherwise, the new version continues the sequence.
            latest = versions[-1]
            latest_version_id = latest['meta']['versionId']
            new_version_id = str(int(latest_version_id) + 1)

            was_deleted = key in self._deleted
            self._store_version(key, resource, new_version_id)

            out = was_deleted
            return out

# ################################################################################################################################

    def read(self, resource_type:'str', resource_id:'str') -> '_ReadResult':
        """ Returns the current version of a resource, along with its deletion status.
        """
        key = f'{resource_type}/{resource_id}'

        with self._lock:

            # No history means the resource never existed ..
            versions = self._versions.get(key)
            if not versions:
                out = _ReadResult(None, False)
                return out

            # .. a deleted resource still has history but reads must say 410 Gone ..
            if key in self._deleted:
                out = _ReadResult(None, True)
                return out

            # .. otherwise, the current version is the last one stored.
            out = _ReadResult(versions[-1], False)
            return out

# ################################################################################################################################

    def vread(self, resource_type:'str', resource_id:'str', version_id:'str') -> 'stranydict | None':
        """ Returns a specific version of a resource, or None if there is no such version.
        """
        key = f'{resource_type}/{resource_id}'

        with self._lock:

            versions = self._versions.get(key)
            if not versions:
                return None

            # Historical versions remain readable even after deletion, per the spec's vread interaction
            for version in versions:
                if version['meta']['versionId'] == version_id:
                    out = version
                    break
            else:
                out = None

            return out

# ################################################################################################################################

    def delete(self, resource_type:'str', resource_id:'str') -> 'bool':
        """ Marks a resource as deleted. Returns False if the resource never existed.
        """
        key = f'{resource_type}/{resource_id}'

        with self._lock:

            versions = self._versions.get(key)
            if not versions:
                out = False
                return out

            # Deletes are idempotent - deleting an already-deleted resource succeeds too
            self._deleted.add(key)

            out = True
            return out

# ################################################################################################################################

    def get_last_modified(self, resource_type:'str', resource_id:'str') -> 'str':
        """ Returns the HTTP-date of the resource's last modification.
        """
        key = f'{resource_type}/{resource_id}'

        with self._lock:
            out = self._last_modified[key]

        return out

# ################################################################################################################################

    def _matches(self, resource:'stranydict', field_name:'str', value:'str') -> 'bool':
        """ Returns True if the resource matches one search parameter. Matching is a case-insensitive
        prefix match over string values, which covers the spec's string search (prefix match) and,
        in practice, its token search (exact match). Search parameters address nested elements,
        e.g. Patient's family parameter targets Patient.name.family, so when the parameter is not
        a top-level field, the match is evaluated over all strings in the whole resource.
        """

        # The _id parameter always matches against the logical ID exactly
        if field_name == '_id':
            out = resource['id'] == value
            return out

        # A top-level field of the same name narrows the match to that field,
        # otherwise the whole resource takes part in it ..
        field_value = resource.get(field_name)
        if field_value is None:
            field_value = resource

        # .. collect every string in whatever we match against, no matter how deeply nested ..
        leaves:'strlist' = []
        _collect_string_leaves(field_value, leaves)

        leaves_lower = [leaf.lower() for leaf in leaves]

        # A token search in the system|code form, per the spec's search.html#token,
        # matches when both the system and the code appear in the element searched.
        if '|' in value:
            system, code = value.split('|', 1)
            out = system.lower() in leaves_lower and code.lower() in leaves_lower
            return out

        # .. and checking each one for a case-insensitive prefix match.
        value_lower = value.lower()

        for leaf_lower in leaves_lower:
            if leaf_lower.startswith(value_lower):
                out = True
                break
        else:
            out = False

        return out

# ################################################################################################################################

    def search(self, resource_type:'str', parameters:'search_parameter_list') -> 'resource_list':
        """ Returns all current, non-deleted resources of the given type that match all the search parameters.
        """
        out:'resource_list' = []

        type_prefix = f'{resource_type}/'

        with self._lock:

            for key, versions in self._versions.items():

                # Only current, non-deleted resources of the requested type take part in searches ..
                if not key.startswith(type_prefix):
                    continue

                if key in self._deleted:
                    continue

                resource = versions[-1]

                # .. and each one must match every search parameter given.
                for name, value in parameters:

                    # Result parameters like _count or _sort do not take part in matching
                    if name.startswith('_'):
                        if name != '_id':
                            continue

                    # Modifiers like name:contains are matched by the base field name
                    field_name = name.split(':')[0]

                    if not self._matches(resource, field_name, value):
                        break
                else:
                    out.append(resource)

        return out

# ################################################################################################################################

    def import_resource(self, resource:'stranydict') -> 'str':
        """ Stores a resource under its own ID, assigning one if it has none. Returns the ID used.
        """
        resource_type = resource['resourceType']

        # Imported resources keep their spec-assigned IDs so tests can look them up by them
        if resource_id := resource.get('id'):
            pass
        else:
            resource_id = uuid4().hex
            resource['id'] = resource_id

        key = f'{resource_type}/{resource_id}'

        with self._lock:
            self._store_version(key, resource, _first_version_id)

        return resource_id

# ################################################################################################################################

    def get_stored_types(self) -> 'strlist':
        """ Returns the sorted list of resource types that have at least one non-deleted resource.
        """
        types:'strset' = set()

        with self._lock:

            for key in self._versions:
                if key in self._deleted:
                    continue

                resource_type = key.split('/')[0]
                types.add(resource_type)

        out = sorted(types)
        return out

# ################################################################################################################################
# ################################################################################################################################

class _OAuthTokenIssuer:
    """ Issues and validates OAuth bearer tokens for the client credentials grant of RFC 6749.
    """
    def __init__(self, client_id:'str', client_secret:'str') -> 'None':

        # The only credentials the token endpoint accepts
        self._client_id = client_id
        self._client_secret = client_secret

        # All the tokens issued so far, together with when they expire
        self._tokens:'token_dict' = {}

        # Serializes access to the token dictionary
        self._lock = threading.Lock()

# ################################################################################################################################

    def issue(self, client_id:'str', client_secret:'str') -> 'strnone':
        """ Issues a new token if the credentials are correct, otherwise returns None.
        """
        if client_id != self._client_id:
            return None

        if client_secret != self._client_secret:
            return None

        token = uuid4().hex
        expiration_time = time() + _token_lifetime

        with self._lock:
            self._tokens[token] = expiration_time

        out = token
        return out

# ################################################################################################################################

    def validate(self, token:'str') -> 'bool':
        """ Returns True if the token was issued by this server and has not expired yet.
        """
        with self._lock:
            expiration_time = self._tokens.get(token)

        if expiration_time is None:
            out = False
        else:
            out = time() < expiration_time

        return out

# ################################################################################################################################
# ################################################################################################################################

class _FHIRHTTPServer(ThreadingHTTPServer):
    """ ThreadingHTTPServer subclass that carries the store and the optional authentication configuration.
    """

    # A deep listen backlog so bursts of concurrent clients connect without resets
    request_queue_size = 128

    def __init__(
        self,
        address:'anytuple',
        handler:'type',
        store:'_FHIRStore',
        base_address:'str',
        auth_type:'str',
        auth_header:'strnone',
        token_issuer:'_OAuthTokenIssuer | None'
        ) -> 'None':
        super().__init__(address, handler)
        self.store = store
        self.base_address = base_address
        self.auth_type = auth_type
        self.auth_header = auth_header
        self.token_issuer = token_issuer

# ################################################################################################################################
# ################################################################################################################################

class _FHIRRequestHandler(BaseHTTPRequestHandler):
    """ Implements the FHIR R4 RESTful API - capabilities, create, read, vread, update, delete and search.
    """
    server: '_FHIRHTTPServer'

    # HTTP/1.1 keeps connections alive, which pooled clients expect
    protocol_version = 'HTTP/1.1'

    def log_message(self, format:'str', *arguments:'any_') -> 'None':
        """ Routes HTTP server log messages through the module logger.
        """
        message = format % arguments
        logger.debug('[FHIR test server] %s', message)

# ################################################################################################################################

    def _send_json(
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
            content_type = _fhir_content_type
        else:
            content_type = _json_content_type

        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))

        if extra_headers:
            for name, value in extra_headers.items():
                self.send_header(name, value)

        self.end_headers()
        _ = self.wfile.write(body)

# ################################################################################################################################

    def _send_outcome(self, status:'int', code:'str', diagnostics:'str') -> 'None':
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

        self._send_json(status, outcome)

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
        if path in ('/metadata', _token_path):
            out = True
            return out

        received = self.headers.get('Authorization')

        # .. Basic Auth must carry the exact expected header ..
        if auth_type == _auth_type_basic:

            if received == self.server.auth_header:
                out = True
            else:
                self._send_unauthorized('Basic')
                out = False

            return out

        # .. and OAuth must carry a bearer token this server has issued.
        else:

            # The issuer is always configured when the auth type is OAuth
            token_issuer = cast_('_OAuthTokenIssuer', self.server.token_issuer)

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

    def _read_body(self) -> 'stranydict | None':
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
            self._send_outcome(BAD_REQUEST, 'structure', f'Request body is not valid JSON -> {e}')
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
            'date': _utc_now_instant(),
            'kind': 'instance',
            'software': {
                'name': 'Zato FHIR test server',
            },
            'implementation': {
                'description': 'An in-memory FHIR server for Zato tests',
                'url': self.server.base_address,
            },
            'fhirVersion': _fhir_version,
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

        self._send_json(OK, bundle)

# ################################################################################################################################

    def _handle_read(self, resource_type:'str', resource_id:'str') -> 'None':
        """ Handles the read interaction, including 410 Gone for deleted resources.
        """
        result = self.server.store.read(resource_type, resource_id)

        # Deleted resources are reported as gone, not as never having existed ..
        if result.is_deleted:
            self._send_outcome(GONE, 'deleted', f'Resource {resource_type}/{resource_id} has been deleted')
            return

        # .. resources with no history at all were never there ..
        if result.resource is None:
            self._send_outcome(NOT_FOUND, 'not-found', f'No such resource -> {resource_type}/{resource_id}')
            return

        # .. otherwise, return the current version with its metadata headers.
        version_id = result.resource['meta']['versionId']
        last_modified = self.server.store.get_last_modified(resource_type, resource_id)

        headers = {
            'ETag': f'W/"{version_id}"',
            'Last-Modified': last_modified,
        }

        self._send_json(OK, result.resource, headers)

# ################################################################################################################################

    def _handle_vread(self, resource_type:'str', resource_id:'str', version_id:'str') -> 'None':
        """ Handles the vread interaction - historical versions stay readable even after deletion.
        """
        resource = self.server.store.vread(resource_type, resource_id, version_id)

        if resource is None:
            diagnostics = f'No such version -> {resource_type}/{resource_id}/_history/{version_id}'
            self._send_outcome(NOT_FOUND, 'not-found', diagnostics)
            return

        headers = {
            'ETag': f'W/"{version_id}"',
        }

        self._send_json(OK, resource, headers)

# ################################################################################################################################

    def do_GET(self) -> 'None': # noqa: N802
        """ Dispatches GET requests to capabilities, search, read or vread.
        """
        if not self._check_auth():
            return

        segments, parameters = self._split_path()
        segment_count = len(segments)

        # The capability statement lives under /metadata ..
        if segments == ['metadata']:
            statement = self._build_capability_statement()
            self._send_json(OK, statement)
            return

        # .. everything else starts with a resource type.
        if segment_count == 0:
            self._send_outcome(NOT_FOUND, 'not-found', 'No interaction at the base URL')
            return

        resource_type = segments[0]

        if not _is_resource_type(resource_type):
            self._send_outcome(NOT_FOUND, 'not-found', f'Not a resource type -> {resource_type}')
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
                self._send_outcome(NOT_FOUND, 'not-found', f'Unrecognized path -> {self.path}')

        # .. anything else is not an interaction this server implements.
        else:
            self._send_outcome(NOT_FOUND, 'not-found', f'Unrecognized path -> {self.path}')

# ################################################################################################################################

    def _handle_token_request(self) -> 'None':
        """ Implements the token endpoint for the client credentials grant of RFC 6749,
        accepting both form-encoded and JSON requests, which is what Zato's BearerTokenManager sends.
        """

        # The issuer is always configured when this endpoint is reachable
        token_issuer = cast_('_OAuthTokenIssuer', self.server.token_issuer)

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
                self._send_json(BAD_REQUEST, {'error': 'invalid_request'}, is_fhir=False)
                return
        else:
            request = dict(parse_qsl(body.decode('utf8')))

        # .. this grant type is the only one the server implements ..
        grant_type = request.get('grant_type')
        if grant_type != _grant_type_client_credentials:
            self._send_json(BAD_REQUEST, {'error': 'unsupported_grant_type'}, is_fhir=False)
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
            self._send_json(BAD_REQUEST, {'error': 'invalid_client'}, is_fhir=False)
            return

        # .. and return it the way RFC 6749 specifies.
        response = {
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in': _token_lifetime,
        }

        self._send_json(OK, response, is_fhir=False)

# ################################################################################################################################

    def _rewrite_references(self, node:'any_', url_map:'strstrdict') -> 'None':
        """ Replaces every urn:uuid reference in a resource with the server location it now lives at.
        """
        if isinstance(node, dict):
            for key in node:
                value = node[key]

                if key == 'reference':
                    if isinstance(value, str):
                        if value in url_map:
                            node[key] = url_map[value]
                            continue

                self._rewrite_references(value, url_map)

        elif isinstance(node, list):
            for item in node:
                self._rewrite_references(item, url_map)

# ################################################################################################################################

    def _apply_bundle_entry(self, entry:'stranydict') -> 'stranydict':
        """ Applies one bundle entry per its request method and returns its response entry.
        """
        request = entry['request']
        method = request['method']
        url = request['url']

        # A create stores the resource under the ID assigned during reference resolution ..
        if method == 'POST':
            resource = entry['resource']
            resource_type = resource['resourceType']
            resource_id = resource['id']

            _ = self.server.store.put(resource_type, resource_id, resource)

            version_id = resource['meta']['versionId']
            location = f'{resource_type}/{resource_id}/_history/{version_id}'

            out = {'response': {'status': '201 Created', 'location': location}}
            return out

        # .. an update stores the resource under the ID its URL names ..
        if method == 'PUT':
            resource = entry['resource']
            resource_type, resource_id = url.split('/', 1)

            resource['id'] = resource_id
            was_created = self.server.store.put(resource_type, resource_id, resource)

            version_id = resource['meta']['versionId']
            location = f'{resource_type}/{resource_id}/_history/{version_id}'

            if was_created:
                status = '201 Created'
            else:
                status = '200 OK'

            out = {'response': {'status': status, 'location': location}}
            return out

        # .. a delete removes what its URL names ..
        if method == 'DELETE':
            resource_type, resource_id = url.split('/', 1)
            _ = self.server.store.delete(resource_type, resource_id)

            out = {'response': {'status': '204 No Content'}}
            return out

        # .. a read returns what its URL names ..
        if method == 'GET':
            resource_type, resource_id = url.split('/', 1)
            result = self.server.store.read(resource_type, resource_id)

            if result.resource is None:
                out = {'response': {'status': '404 Not Found'}}
            else:
                out = {'response': {'status': '200 OK'}, 'resource': result.resource}

            return out

        # .. and anything else is not a method bundles may carry.
        out = {'response': {'status': '400 Bad Request'}}
        return out

# ################################################################################################################################

    def _handle_bundle(self) -> 'None':
        """ Handles the transaction and batch interactions - a Bundle posted to the base URL.
        Each entry is processed per its request method and urn:uuid fullUrl references
        resolve to the IDs the server assigns, across all the entries.
        """
        bundle = self._read_body()
        if bundle is None:
            return

        # Only bundles belong at the base URL ..
        body_type = bundle.get('resourceType')
        if body_type != 'Bundle':
            self._send_outcome(BAD_REQUEST, 'invalid', f'Expected a Bundle at the base URL, not `{body_type}`')
            return

        # .. and only the transaction and batch kinds.
        bundle_type = bundle.get('type')
        if bundle_type not in _bundle_request_types:
            diagnostics = f'Expected a transaction or batch Bundle, not `{bundle_type}`'
            self._send_outcome(BAD_REQUEST, 'invalid', diagnostics)
            return

        entries = bundle.get('entry')
        if entries is None:
            entries = []

        # First pass - assign a server ID to every resource created by the bundle,
        # so that urn:uuid references can point at the right location before anything is stored.
        url_map:'strstrdict' = {}

        for entry in entries:
            request = entry.get('request')
            if not request:
                diagnostics = 'Each entry of a transaction or batch needs a request'
                self._send_outcome(BAD_REQUEST, 'invalid', diagnostics)
                return

            if request['method'] == 'POST':
                resource = entry['resource']
                resource_type = resource['resourceType']

                resource_id = uuid4().hex
                resource['id'] = resource_id

                full_url = entry.get('fullUrl')
                if full_url:
                    if full_url.startswith('urn:uuid:'):
                        url_map[full_url] = f'{resource_type}/{resource_id}'

        # Second pass - resolve the references now that all the IDs are known ..
        for entry in entries:
            if 'resource' in entry:
                self._rewrite_references(entry['resource'], url_map)

        # .. third pass - apply each entry and collect its response.
        response_entries:'dictlist' = []

        for entry in entries:
            response_entry = self._apply_bundle_entry(entry)
            response_entries.append(response_entry)

        response = {
            'resourceType': 'Bundle',
            'id': uuid4().hex,
            'type': _bundle_request_types[bundle_type],
            'entry': response_entries,
        }

        self._send_json(OK, response)

# ################################################################################################################################

    def do_POST(self) -> 'None': # noqa: N802
        """ Handles the create and transaction interactions and, if OAuth is configured, the token endpoint.
        """
        if not self._check_auth():
            return

        # The token endpoint exists only when the server was started with OAuth
        path = urlsplit(self.path).path
        if path == _token_path:
            if self.server.token_issuer:
                self._handle_token_request()
            else:
                self._send_outcome(NOT_FOUND, 'not-found', f'Unrecognized path -> {self.path}')
            return

        segments, _ = self._split_path()
        segment_count = len(segments)

        # A POST to the base URL is a transaction or batch Bundle
        if segment_count == 0:
            self._handle_bundle()
            return

        # Otherwise, create is the POST interaction this server implements
        if segment_count != 1:
            self._send_outcome(NOT_FOUND, 'not-found', f'Unrecognized path -> {self.path}')
            return

        resource_type = segments[0]

        if not _is_resource_type(resource_type):
            self._send_outcome(NOT_FOUND, 'not-found', f'Not a resource type -> {resource_type}')
            return

        resource = self._read_body()
        if resource is None:
            return

        # The body's type must agree with the endpoint it was posted to
        body_type = resource.get('resourceType')
        if body_type != resource_type:
            diagnostics = f'Resource type mismatch -> body has `{body_type}`, endpoint is `{resource_type}`'
            self._send_outcome(BAD_REQUEST, 'invalid', diagnostics)
            return

        # Store it, letting the server assign the ID ..
        resource = self.server.store.create(resource_type, resource)

        resource_id = resource['id']
        version_id = resource['meta']['versionId']
        last_modified = self.server.store.get_last_modified(resource_type, resource_id)

        # .. and point the client at the newly created version.
        headers = {
            'Location': f'{self.server.base_address}/{resource_type}/{resource_id}/_history/{version_id}',
            'ETag': f'W/"{version_id}"',
            'Last-Modified': last_modified,
        }

        self._send_json(CREATED, resource, headers)

# ################################################################################################################################

    def do_PUT(self) -> 'None': # noqa: N802
        """ Handles the update interaction, including update-as-create.
        """
        if not self._check_auth():
            return

        segments, _ = self._split_path()
        segment_count = len(segments)

        # Update always addresses a specific resource
        if segment_count != 2:
            self._send_outcome(NOT_FOUND, 'not-found', f'Unrecognized path -> {self.path}')
            return

        resource_type = segments[0]
        resource_id = segments[1]

        if not _is_resource_type(resource_type):
            self._send_outcome(NOT_FOUND, 'not-found', f'Not a resource type -> {resource_type}')
            return

        resource = self._read_body()
        if resource is None:
            return

        # The body's type must agree with the URL ..
        body_type = resource.get('resourceType')
        if body_type != resource_type:
            diagnostics = f'Resource type mismatch -> body has `{body_type}`, endpoint is `{resource_type}`'
            self._send_outcome(BAD_REQUEST, 'invalid', diagnostics)
            return

        # .. and so must its ID, which the spec requires to be present and identical.
        body_id = resource.get('id')
        if body_id != resource_id:
            diagnostics = f'Resource ID mismatch -> body has `{body_id}`, URL has `{resource_id}`'
            self._send_outcome(BAD_REQUEST, 'invalid', diagnostics)
            return

        was_created = self.server.store.put(resource_type, resource_id, resource)

        version_id = resource['meta']['versionId']
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

        self._send_json(status, resource, headers)

# ################################################################################################################################

    def do_DELETE(self) -> 'None': # noqa: N802
        """ Handles the delete interaction - deletes are idempotent and reads afterwards return 410 Gone.
        """
        if not self._check_auth():
            return

        segments, _ = self._split_path()
        segment_count = len(segments)

        # Delete always addresses a specific resource
        if segment_count != 2:
            self._send_outcome(NOT_FOUND, 'not-found', f'Unrecognized path -> {self.path}')
            return

        resource_type = segments[0]
        resource_id = segments[1]

        was_found = self.server.store.delete(resource_type, resource_id)

        if was_found:
            self._send_no_content()
        else:
            self._send_outcome(NOT_FOUND, 'not-found', f'No such resource -> {resource_type}/{resource_id}')

# ################################################################################################################################
# ################################################################################################################################

class FHIRTestServer:
    """ An in-memory FHIR R4 server for use in tests, listening on the loopback interface only.
    It implements the spec's RESTful API - capabilities, create, read, vread, update, delete, search
    and the transaction and batch interactions with urn:uuid reference resolution -
    with resource versioning, searchset Bundles and OperationOutcome errors. Authentication is optional
    and matches what the FHIR outgoing connection supports - Basic Auth, or OAuth bearer tokens issued
    by the server's own RFC 6749 token endpoint, with the credentials acting as client_id and client_secret.
    """
    def __init__(self, username:'str'='', password:'str'='', auth_type:'str'='') -> 'None':

        # Connection details for clients
        self.host = '127.0.0.1'
        self.port = get_free_port()

        # Optional credentials - empty means the server is open. With Basic Auth they are
        # the username and password, with OAuth they are the client ID and client secret.
        self.username = username
        self.password = password

        # Credentials without an explicit auth type mean Basic Auth
        if username:
            if not auth_type:
                auth_type = _auth_type_basic

        self.auth_type = auth_type

        # Where all the resources live
        self.store = _FHIRStore()

        # The HTTP server and its thread, populated in .start
        self._server:'_FHIRHTTPServer | None' = None
        self._thread:'threading.Thread | None' = None

# ################################################################################################################################

    @property
    def address(self) -> 'str':
        """ The base URL clients connect to.
        """
        out = f'http://{self.host}:{self.port}'
        return out

# ################################################################################################################################

    @property
    def token_endpoint(self) -> 'str':
        """ The URL OAuth tokens are issued at - this is what a Bearer token security definition
        points its auth_server_url to.
        """
        out = f'{self.address}{_token_path}'
        return out

# ################################################################################################################################

    def _build_auth_header(self) -> 'strnone':
        """ Builds the exact Authorization header the server expects for Basic Auth, or None otherwise.
        """
        if self.auth_type != _auth_type_basic:
            return None

        credentials = f'{self.username}:{self.password}'
        credentials = credentials.encode('ascii')
        credentials = b64encode(credentials)
        credentials = credentials.decode('ascii')

        out = f'Basic {credentials}'
        return out

# ################################################################################################################################

    def _build_token_issuer(self) -> '_OAuthTokenIssuer | None':
        """ Builds the OAuth token issuer, or None if the server does not use OAuth.
        """
        if self.auth_type != _auth_type_oauth:
            return None

        out = _OAuthTokenIssuer(self.username, self.password)
        return out

# ################################################################################################################################

    def _wait_until_accepting_connections(self) -> 'None':

        # Keep trying until the server accepts connections or we run out of time
        attempts = int(_start_timeout / _start_sleep_time)

        for _ in range(attempts):
            try:
                with socket.create_connection((self.host, self.port), timeout=1.0):
                    return
            except OSError:
                sleep(_start_sleep_time)

        # If we are here, the server never came up
        raise Exception(f'FHIR test server did not start within {_start_timeout}s on {self.host}:{self.port}')

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the HTTP server in a daemon thread and waits until it accepts connections.
        """
        auth_header = self._build_auth_header()
        token_issuer = self._build_token_issuer()

        address = (self.host, self.port)
        server = _FHIRHTTPServer(
            address, _FHIRRequestHandler, self.store, self.address, self.auth_type, auth_header, token_issuer)

        self._server = server

        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self._thread = thread

        self._wait_until_accepting_connections()

        logger.info('FHIR test server started on %s', self.address)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Shuts down the HTTP server.
        """
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
            self._thread = None

            logger.info('FHIR test server stopped on %s', self.address)

# ################################################################################################################################

    def import_resource(self, resource:'stranydict') -> 'str':
        """ Stores a single resource, keeping its own ID if it has one. Returns the ID used.
        """
        out = self.store.import_resource(resource)
        return out

# ################################################################################################################################

    def import_directory(self, directory:'str') -> 'int':
        """ Recursively imports all FHIR resources found in JSON files under a directory,
        e.g. the StructureDefinitions, ValueSets and CodeSystems of an implementation guide.
        Returns how many resources were imported.
        """
        count = 0

        for root, _, file_names in os.walk(directory):

            for file_name in sorted(file_names):

                if not file_name.endswith('.json'):
                    continue

                file_path = os.path.join(root, file_name)

                with open(file_path, encoding='utf8') as json_file:
                    data = json_file.read()

                # Skip files that are not JSON despite their extension ..
                try:
                    parsed = json.loads(data)
                except json.JSONDecodeError:
                    continue

                # .. and files whose JSON is not a FHIR resource.
                if not isinstance(parsed, dict):
                    continue

                if 'resourceType' not in parsed:
                    continue

                _ = self.store.import_resource(parsed)
                count += 1

        logger.info('Imported %d resources from %s', count, directory)

        out = count
        return out

# ################################################################################################################################
# ################################################################################################################################
