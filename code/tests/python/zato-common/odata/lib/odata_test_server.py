# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import shutil
import ssl
import threading
import time
from base64 import b64decode
from http.client import BAD_REQUEST, CREATED, FORBIDDEN, FOUND, METHOD_NOT_ALLOWED, NO_CONTENT, NOT_FOUND, OK, \
    PRECONDITION_FAILED, PRECONDITION_REQUIRED, UNAUTHORIZED
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from json import dumps, loads
from urllib.parse import parse_qsl, urlencode, urlsplit

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################

from certs import build_tls_material

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strdict, stranydict, strnone
    from certs import TLSMaterial

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Profile:
    """ The systems the test server can simulate.
    """
    S4HANA = 's4hana'
    SUCCESSFACTORS = 'successfactors'
    DYNAMICS_365_FO = 'dynamics-365-fo'
    BUSINESS_CENTRAL = 'business-central'

# ################################################################################################################################
# ################################################################################################################################

# The OData version each profile speaks.
Profile_Version = {
    Profile.S4HANA: '2.0',
    Profile.SUCCESSFACTORS: '2.0',
    Profile.DYNAMICS_365_FO: '4.0',
    Profile.BUSINESS_CENTRAL: '4.0',
}

# The service root path each profile serves under - the way the real systems shape their URLs.
Profile_Service_Root = {
    Profile.S4HANA: '/sap/opu/odata/sap/API_SALES_ORDER_SRV',
    Profile.SUCCESSFACTORS: '/odata/v2',
    Profile.DYNAMICS_365_FO: '/data',
    Profile.BUSINESS_CENTRAL: '/v2.0/test-tenant/sandbox/api/v2.0',
}

# The metadata document each profile serves, stored next to this module.
_metadata_file = {
    Profile.S4HANA: 's4hana.xml',
    Profile.SUCCESSFACTORS: 'successfactors.xml',
    Profile.DYNAMICS_365_FO: 'd365fo.xml',
    Profile.BUSINESS_CENTRAL: 'business_central.xml',
}

_metadata_dir = os.path.join(os.path.dirname(__file__), 'metadata')

# The Azure AD style path the Dynamics profile issues tokens under.
Token_Endpoint_Path = '/test-tenant/oauth2/v2.0/token'

# How long the issued tokens claim to live.
_token_expires_in = 3600

# The header SAP systems exchange CSRF tokens in.
_csrf_header = 'X-CSRF-Token'

# The comparison operators the in-memory filter evaluator understands.
_filter_operators = {
    'eq': '__eq__',
    'ne': '__ne__',
    'gt': '__gt__',
    'ge': '__ge__',
    'lt': '__lt__',
    'le': '__le__',
}

# ################################################################################################################################
# ################################################################################################################################

class _Rejected(Exception):
    """ Raised inside dispatching to short-circuit with a prepared error response.
    """
    def __init__(self, status:'int', body:'bytes', content_type:'str', headers:'strdict | None'=None) -> 'None':
        self.status = status
        self.body = body
        self.content_type = content_type
        self.headers = headers or {}

# ################################################################################################################################
# ################################################################################################################################

def _parse_filter_literal(text:'str') -> 'any_':
    """ Parses one OData literal as the filter evaluator's Python value.
    """
    if text.startswith("guid'"):
        out = text[len("guid'"):-1]

    elif text.startswith("'"):
        out = text[1:-1].replace("''", "'")

    elif text == 'true':
        out = True

    elif text == 'false':
        out = False

    elif text == 'null':
        out = None

    # Anything else is a number.
    else:
        if '.' in text:
            out = float(text)
        else:
            out = int(text)

    return out

# ################################################################################################################################
# ################################################################################################################################

class _Server(ThreadingHTTPServer):
    """ A threading HTTP server simulating one OData system - it holds an in-memory entity
    store, records every request, enforces the profile's authentication and headers,
    and answers with payloads shaped the way the simulated system shapes them.
    """
    daemon_threads = True

    def __init__(self, profile:'str', *args:'any_', **kwargs:'any_') -> 'None':
        super().__init__(*args, **kwargs)

        self.profile = profile
        self.odata_version = Profile_Version[profile]
        self.service_root = Profile_Service_Root[profile]

        self.recorded_requests:'anylist' = []
        self.last_request:'anydict | None' = None
        self.path_config:'anydict' = {}

        # The in-memory entity store - entity set name to a dict of key to entity.
        self.entities:'stranydict' = {}

        # The key property of each entity set.
        self.key_properties:'strdict' = {}

        # Credentials the profile enforces - None means no enforcement.
        self.expected_username:'strnone' = None
        self.expected_password:'strnone' = None

        # The OAuth2 client the token endpoint accepts.
        self.expected_client_id:'strnone' = None
        self.expected_client_secret:'strnone' = None

        # Tokens the server has issued and still accepts.
        self.issued_tokens:'anylist' = []

        # The CSRF token writes must carry - issued on demand.
        self.csrf_token:'strnone' = None

        # Query parameters every request must carry, e.g. sap-client or $format.
        self.required_query_params:'strdict' = {}

        # Server-driven paging - 0 means everything fits in one page.
        self.page_size = 0

        # A counter for ETag values and generated keys.
        self._sequence = 0

        # The base address and the $metadata document are filled in when the server starts,
        # once the ephemeral port is known.
        self.base_address = ''
        self.metadata_document = b''

# ################################################################################################################################

    def next_sequence(self) -> 'int':
        self._sequence += 1

        out = self._sequence
        return out

# ################################################################################################################################

    def new_etag(self) -> 'str':
        sequence = self.next_sequence()

        out = f'W/"etag-{sequence}"'
        return out

# ################################################################################################################################

    def add_entities(self, entity_set:'str', key_property:'str', items:'anylist') -> 'None':
        """ Loads entities into the store - V4 profiles get an ETag stamped on each one.
        """
        store = self.entities.setdefault(entity_set, {})
        self.key_properties[entity_set] = key_property

        for item in items:
            entity = dict(item)

            if self.odata_version == '4.0':
                entity['@odata.etag'] = self.new_etag()

            store[str(entity[key_property])] = entity

# ################################################################################################################################

    def reset(self) -> 'None':
        """ Clears the store, the recorded requests, the issued tokens and every
        enforcement a test configured - each test starts from a clean slate.
        """
        self.entities.clear()
        self.key_properties.clear()
        self.recorded_requests.clear()
        self.last_request = None
        self.path_config.clear()
        self.issued_tokens.clear()
        self.csrf_token = None
        self.required_query_params.clear()
        self.page_size = 0
        self.expected_username = None
        self.expected_password = None
        self.expected_client_id = None
        self.expected_client_secret = None

# ################################################################################################################################

    def error_body(self, code:'str', message:'str') -> 'bytes':
        """ Builds an error payload in the shape the profile's version prescribes -
        V2 nests the message as a language-tagged object, V4 keeps it a plain string.
        """
        if self.odata_version == '2.0':
            payload = {'error': {'code': code, 'message': {'lang': 'en', 'value': message}}}
        else:
            payload = {'error': {'code': code, 'message': message}}

        out = dumps(payload).encode('utf8')
        return out

# ################################################################################################################################

    def _reject_error(self, status:'int', code:'str', message:'str', headers:'strdict | None'=None) -> '_Rejected':
        body = self.error_body(code, message)

        out = _Rejected(status, body, 'application/json', headers)
        return out

# ################################################################################################################################

    def check_auth(self, headers:'anydict') -> 'None':
        """ Enforces the profile's authentication - basic credentials for the SAP-like
        and Business Central profiles, an issued bearer token for Dynamics.
        """

        # Dynamics accepts only tokens its own endpoint issued.
        if self.profile == Profile.DYNAMICS_365_FO:
            authorization = headers.get('Authorization') or ''

            token = authorization[len('Bearer '):] if authorization.startswith('Bearer ') else ''

            if token not in self.issued_tokens:
                raise self._reject_error(UNAUTHORIZED, 'Unauthorized', 'A valid bearer token is required')

            return

        # The remaining profiles enforce basic credentials only when a test configured them.
        if self.expected_username is None:
            return

        authorization = headers.get('Authorization') or ''

        if not authorization.startswith('Basic '):
            raise self._reject_error(UNAUTHORIZED, 'Unauthorized', 'Basic credentials are required')

        decoded = b64decode(authorization[len('Basic '):]).decode('utf8')
        username, _, password = decoded.partition(':')

        if username != self.expected_username:
            raise self._reject_error(UNAUTHORIZED, 'Unauthorized', 'Invalid username')

        if password != self.expected_password:
            raise self._reject_error(UNAUTHORIZED, 'Unauthorized', 'Invalid password')

# ################################################################################################################################

    def check_required_params(self, params:'strdict') -> 'None':
        """ Enforces the query parameters the profile insists on, e.g. sap-client=100
        for S/4HANA or $format=json for SuccessFactors.
        """
        for name, value in self.required_query_params.items():
            if params.get(name) != value:
                raise self._reject_error(BAD_REQUEST, 'MissingParameter', f'The {name} parameter is required')

# ################################################################################################################################

    def check_csrf(self, method:'str', headers:'anydict') -> 'None':
        """ Enforces the SAP CSRF exchange - writes must carry the token a prior fetch obtained.
        """
        if self.profile != Profile.S4HANA:
            return

        if method == 'GET':
            return

        token = headers.get(_csrf_header)

        if not self.csrf_token or token != self.csrf_token:
            raise self._reject_error(
                FORBIDDEN, 'CSRFTokenValidationFailed', 'CSRF token validation failed',
                headers={_csrf_header: 'Required'},
            )

# ################################################################################################################################

    def issue_csrf_token(self) -> 'str':
        self.csrf_token = 'csrf-' + CryptoManager.generate_hex_string()

        out = self.csrf_token
        return out

# ################################################################################################################################

    def issue_bearer_token(self) -> 'str':
        token = 'token-' + CryptoManager.generate_hex_string()
        self.issued_tokens.append(token)

        out = token
        return out

# ################################################################################################################################

    def _match_filter(self, entity:'anydict', filter_text:'str') -> 'bool':
        """ Evaluates a filter of comparison clauses joined with 'and' against one entity.
        """
        for clause in filter_text.split(' and '):
            property_name, operator_name, literal = clause.strip().split(' ', 2)

            expected = _parse_filter_literal(literal)
            actual = entity.get(property_name)

            comparison = getattr(actual, _filter_operators[operator_name])

            if comparison(expected) is not True:
                return False

        return True

# ################################################################################################################################

    def _apply_query(self, items:'anylist', params:'strdict') -> 'anylist':
        """ Applies the supported query options to a list of entities, in the order
        the OData specification evaluates them - filter, order, skip, top, select.
        """
        out = items

        if filter_text := params.get('$filter'):
            filtered = []
            for entity in out:
                if self._match_filter(entity, filter_text):
                    filtered.append(entity)
            out = filtered

        if orderby := params.get('$orderby'):
            parts = orderby.split(' ')
            property_name = parts[0]
            is_descending = len(parts) > 1 and parts[1] == 'desc'

            def _order_key(entity:'anydict') -> 'any_':
                return entity.get(property_name)

            out = sorted(out, key=_order_key, reverse=is_descending)

        if skip := params.get('$skip'):
            out = out[int(skip):]

        if top := params.get('$top'):
            out = out[:int(top)]

        if select := params.get('$select'):
            names = select.split(',')

            projected = []
            for entity in out:
                slimmed = {}
                for name in names:
                    if name in entity:
                        slimmed[name] = entity[name]

                # V4 entities keep announcing their ETag even when projected.
                if '@odata.etag' in entity:
                    slimmed['@odata.etag'] = entity['@odata.etag']

                projected.append(slimmed)

            out = projected

        return out

# ################################################################################################################################

    def _feed_response(self, items:'anylist', params:'strdict', path:'str') -> 'anydict':
        """ Builds a feed payload in the profile's shape, with server-driven paging
        through a skip token when the page size says so.
        """
        offset = int(params.get('$skiptoken') or 0)

        next_link = None

        # With paging on, one page's worth goes out along with a link to the next one.
        if self.page_size:
            page = items[offset:offset + self.page_size]

            if offset + self.page_size < len(items):
                next_offset = offset + self.page_size

                # The original query parameters ride along in the next link, the way
                # real servers keep sap-client and friends across pages.
                next_params = dict(params)
                next_params['$skiptoken'] = str(next_offset)

                encoded = urlencode(next_params)
                next_link = f'{self.base_address}{path}?{encoded}'

        else:
            page = items

        if self.odata_version == '2.0':
            payload:'anydict' = {'results': page}

            if '$inlinecount' in params:
                payload['__count'] = str(len(items))

            if next_link:
                payload['__next'] = next_link

            out = {'d': payload}

        else:
            out:'anydict' = {'value': page}

            if params.get('$count') == 'true':
                out['@odata.count'] = len(items)

            if next_link:
                out['@odata.nextLink'] = next_link

        return out

# ################################################################################################################################

    def _entity_response(self, entity:'anydict') -> 'anydict':
        """ Wraps a single entity the way the profile's version prescribes.
        """
        if self.odata_version == '2.0':
            out = {'d': entity}
        else:
            out = dict(entity)

        return out

# ################################################################################################################################

    def _parse_key(self, text:'str') -> 'str':
        """ Parses the key predicate of a path segment into the string form entities
        are keyed by in the store - quotes and the V2 guid prefix are stripped.
        """
        if text.startswith("guid'"):
            out = text[len("guid'"):-1]

        elif text.startswith("'"):
            out = text[1:-1].replace("''", "'")

        else:
            out = text

        return out

# ################################################################################################################################

    def _split_segment(self, segment:'str') -> 'tuple[str, strnone]':
        """ Splits one path segment into the set name and the key predicate, if any.
        """
        if segment.endswith(')'):
            name, _, rest = segment.partition('(')
            key = self._parse_key(rest[:-1])
        else:
            name = segment
            key = None

        out = (name, key)
        return out

# ################################################################################################################################

    def _find_entity(self, entity_set:'str', key:'str') -> 'anydict':
        """ Returns one entity from the store or rejects with a 404.
        """
        store = self.entities.get(entity_set)

        if store is None:
            raise self._reject_error(NOT_FOUND, 'NotFound', f'Entity set {entity_set} does not exist')

        entity = store.get(key)

        if entity is None:
            raise self._reject_error(NOT_FOUND, 'NotFound', f'No entity with key {key} in {entity_set}')

        out = entity
        return out

# ################################################################################################################################

    def _check_etag(self, entity:'anydict', headers:'anydict') -> 'None':
        """ Enforces optimistic concurrency the way Business Central does - a modifying
        request must carry an If-Match that is either the current ETag or the * wildcard.
        """
        if self.profile != Profile.BUSINESS_CENTRAL:
            return

        if_match = headers.get('If-Match')

        if not if_match:
            raise self._reject_error(PRECONDITION_REQUIRED, 'PreconditionRequired', 'An If-Match header is required')

        if if_match == '*':
            return

        if if_match != entity['@odata.etag']:
            raise self._reject_error(PRECONDITION_FAILED, 'PreconditionFailed', 'The ETag does not match')

# ################################################################################################################################

    def dispatch(
        self,
        method:'str',
        path:'str',
        params:'strdict',
        headers:'anydict',
        body:'anydict | None',
        ) -> 'tuple[int, strdict, bytes, str]':
        """ Routes one request - the main handler and batch parts both come through here.
        Returns the status, extra headers, body bytes and content type of the response.
        """

        # Canned per-path behavior a test configured comes first.
        config = self.path_config.get(path) or {}

        if delay := config.get('delay'):
            time.sleep(delay)

        if error := config.get('respond_error'):
            status, code, message = error
            raise self._reject_error(status, code, message)

        if canned := config.get('respond_json'):
            status, payload = canned
            out = (status, {}, dumps(payload).encode('utf8'), 'application/json')
            return out

        # A canned redirect points the client at another path on this server.
        if target := config.get('redirect'):
            out = (FOUND, {'Location': target}, b'', 'text/plain')
            return out

        self.check_required_params(params)

        # The path inside the service root determines what is being addressed.
        relative = path[len(self.service_root):].strip('/')

        if relative == '$metadata':
            out = (OK, {}, self.metadata_document, 'application/xml')
            return out

        segments = relative.split('/')

        # A count request addresses its set's last-but-one segment.
        wants_count = segments[-1] == '$count'
        if wants_count:
            segments = segments[:-1]

        # Walk the intermediate segments so sub-resource paths, e.g. companies(id)/customers,
        # are validated the way Business Central validates them.
        for segment in segments[:-1]:
            name, key = self._split_segment(segment)

            if key is None:
                raise self._reject_error(BAD_REQUEST, 'BadRequest', f'A key is required for {name}')

            _ = self._find_entity(name, key)

        entity_set, key = self._split_segment(segments[-1])

        # Functions and actions a test configured respond regardless of the entity store.
        if operation := config.get('operation'):
            status, payload = operation
            out = (status, {}, dumps(payload).encode('utf8'), 'application/json')
            return out

        if method == 'GET':
            out = self._handle_get(entity_set, key, params, path, wants_count)

        elif method == 'POST':
            out = self._handle_create(entity_set, body)

        elif method in ('PATCH', 'MERGE'):
            out = self._handle_update(entity_set, key, body, headers)

        elif method == 'DELETE':
            out = self._handle_delete(entity_set, key, headers)

        # .. anything else is not part of the protocol the server speaks.
        else:
            raise self._reject_error(METHOD_NOT_ALLOWED, 'MethodNotAllowed', f'Method {method} is not supported')

        return out

# ################################################################################################################################

    def _handle_get(
        self,
        entity_set:'str',
        key:'strnone',
        params:'strdict',
        path:'str',
        wants_count:'bool',
        ) -> 'tuple[int, strdict, bytes, str]':
        """ Handles reads - a whole set, one entity by key, or a count.
        """
        store = self.entities.get(entity_set)

        if store is None:
            raise self._reject_error(NOT_FOUND, 'NotFound', f'Entity set {entity_set} does not exist')

        if key is not None:
            entity = self._find_entity(entity_set, key)

            payload = self._entity_response(entity)

            extra_headers = {}

            # V4 single entities announce their ETag as a header too.
            if '@odata.etag' in entity:
                extra_headers['ETag'] = entity['@odata.etag']

            out = (OK, extra_headers, dumps(payload).encode('utf8'), 'application/json')
            return out

        items = list(store.values())

        if wants_count:
            filtered = self._apply_query(items, params)
            out = (OK, {}, str(len(filtered)).encode('utf8'), 'text/plain')
            return out

        items = self._apply_query(items, params)
        payload = self._feed_response(items, params, path)

        out = (OK, {}, dumps(payload).encode('utf8'), 'application/json')
        return out

# ################################################################################################################################

    def _handle_create(self, entity_set:'str', body:'anydict | None') -> 'tuple[int, strdict, bytes, str]':
        """ Handles creates - the entity joins the store and travels back with a 201.
        """
        if body is None:
            raise self._reject_error(BAD_REQUEST, 'BadRequest', 'A request body is required')

        store = self.entities.setdefault(entity_set, {})
        key_property = self.key_properties.setdefault(entity_set, 'id')

        entity = dict(body)

        # A missing key gets one generated, the way Business Central assigns ids.
        if key_property not in entity:
            generated = CryptoManager.generate_hex_string(128)
            entity[key_property] = f'{generated[0:8]}-{generated[8:12]}-{generated[12:16]}-{generated[16:20]}-{generated[20:32]}'

        if self.odata_version == '4.0':
            entity['@odata.etag'] = self.new_etag()

        store[str(entity[key_property])] = entity

        payload = self._entity_response(entity)

        out = (CREATED, {}, dumps(payload).encode('utf8'), 'application/json')
        return out

# ################################################################################################################################

    def _handle_update(
        self,
        entity_set:'str',
        key:'strnone',
        body:'anydict | None',
        headers:'anydict',
        ) -> 'tuple[int, strdict, bytes, str]':
        """ Handles partial updates - fields merge into the entity, whose ETag then moves on.
        """
        if key is None:
            raise self._reject_error(BAD_REQUEST, 'BadRequest', 'A key is required for updates')

        if body is None:
            raise self._reject_error(BAD_REQUEST, 'BadRequest', 'A request body is required')

        entity = self._find_entity(entity_set, key)

        self._check_etag(entity, headers)

        entity.update(body)

        if self.odata_version == '4.0':
            entity['@odata.etag'] = self.new_etag()

        out = (NO_CONTENT, {}, b'', 'application/json')
        return out

# ################################################################################################################################

    def _handle_delete(self, entity_set:'str', key:'strnone', headers:'anydict') -> 'tuple[int, strdict, bytes, str]':
        """ Handles deletes - the entity leaves the store.
        """
        if key is None:
            raise self._reject_error(BAD_REQUEST, 'BadRequest', 'A key is required for deletes')

        entity = self._find_entity(entity_set, key)

        self._check_etag(entity, headers)

        del self.entities[entity_set][key]

        out = (NO_CONTENT, {}, b'', 'application/json')
        return out

# ################################################################################################################################
# ################################################################################################################################

class _Handler(BaseHTTPRequestHandler):
    """ Parses each incoming request, records it, and hands it to the server's dispatcher -
    token requests, CSRF fetches and $batch envelopes get their own treatment first.
    """

    protocol_version = 'HTTP/1.1'

    def _read_body(self) -> 'bytes':
        if 'Content-Length' in self.headers:
            length = int(self.headers['Content-Length'])
            out = self.rfile.read(length)
        else:
            out = b''
        return out

# ################################################################################################################################

    def _record(self, path:'str', params:'strdict', raw_body:'bytes') -> 'stranydict':
        """ Builds one request record tests can assert on - the wire details plus
        the parsed JSON body when there is one.
        """
        record:'stranydict' = {
            'method': self.command,
            'path': path,
            'query': params,
            'raw_path': self.path,
            'headers': dict(self.headers.items()),
            'raw_body': raw_body,
            'json': None,
        }

        if raw_body:
            try:
                record['json'] = loads(raw_body)
            except ValueError:
                pass

        return record

# ################################################################################################################################

    def _send(self, status:'int', body:'bytes', content_type:'str', extra_headers:'strdict | None'=None) -> 'None':
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))

        if extra_headers:
            for name, value in extra_headers.items():
                self.send_header(name, value)

        self.end_headers()

        if self.command != 'HEAD':
            _ = self.wfile.write(body)

# ################################################################################################################################

    def _handle_token_request(self, raw_body:'bytes') -> 'None':
        """ Plays the Azure AD token endpoint - client credentials in, a bearer token out.
        """
        server:'any_' = self.server

        form = dict(parse_qsl(raw_body.decode('utf8')))

        grant_type_matches = form.get('grant_type') == 'client_credentials'
        client_id_matches = form.get('client_id') == server.expected_client_id
        client_secret_matches = form.get('client_secret') == server.expected_client_secret

        if grant_type_matches:
            if client_id_matches:
                if client_secret_matches:
                    token = server.issue_bearer_token()

                    payload = {
                        'access_token': token,
                        'token_type': 'Bearer',
                        'expires_in': _token_expires_in,
                    }

                    self._send(OK, dumps(payload).encode('utf8'), 'application/json')
                    return

        payload = {'error': 'invalid_client', 'error_description': 'Invalid client credentials'}
        self._send(UNAUTHORIZED, dumps(payload).encode('utf8'), 'application/json')

# ################################################################################################################################

    def _handle_batch(self, record:'stranydict', raw_body:'bytes') -> 'None':
        """ Unpacks a $batch envelope, dispatches each part, and packs the responses back
        in the same format the envelope arrived in - multipart or V4 JSON.
        """
        content_type = self.headers.get('Content-Type') or ''

        if content_type.startswith('multipart/mixed'):
            self._handle_batch_multipart(record, raw_body, content_type)
        else:
            self._handle_batch_json(record, raw_body)

# ################################################################################################################################

    def _dispatch_batch_part(self, method:'str', url:'str', body:'anydict | None') -> 'tuple[int, strdict, bytes, str]':
        """ Dispatches one batch part - its URL is relative to the service root.
        """
        server:'any_' = self.server

        split = urlsplit(url)
        params = dict(parse_qsl(split.query, keep_blank_values=True))

        path = f'{server.service_root}/{split.path.lstrip("/")}'

        try:
            out = server.dispatch(method, path, params, dict(self.headers.items()), body)
        except _Rejected as rejected:
            out = (rejected.status, rejected.headers, rejected.body, rejected.content_type)

        return out

# ################################################################################################################################

    def _handle_batch_multipart(self, record:'stranydict', raw_body:'bytes', content_type:'str') -> 'None':
        """ Handles a multipart $batch - changesets are unwrapped, each request dispatched,
        and the responses travel back in a multipart body mirroring the request structure.
        """
        boundary = _extract_multipart_boundary(content_type)
        parts = _split_multipart(raw_body.decode('utf8'), boundary)

        batch_requests = []
        response_parts = []

        for part in parts:

            part_headers = part.partition('\r\n\r\n')[0]

            # A changeset arrives as a nested multipart whose parts respond as one changeset too.
            if 'multipart/mixed' in part_headers:
                changeset_boundary = _extract_multipart_boundary(part_headers)
                changeset_parts = _split_multipart(part, changeset_boundary)

                rendered_responses = []
                for changeset_part in changeset_parts:
                    method, url, body = _parse_http_part(changeset_part)
                    batch_requests.append({'method': method, 'url': url, 'json': body})

                    status, headers, response_body, response_content_type = self._dispatch_batch_part(method, url, body)
                    rendered_responses.append(_render_http_response(status, headers, response_body, response_content_type))

                response_parts.append(_render_changeset(rendered_responses))

            else:
                method, url, body = _parse_http_part(part)
                batch_requests.append({'method': method, 'url': url, 'json': body})

                status, headers, response_body, response_content_type = self._dispatch_batch_part(method, url, body)
                response_parts.append(_render_http_response(status, headers, response_body, response_content_type))

        record['batch_requests'] = batch_requests

        response_boundary = 'batchresponse_' + CryptoManager.generate_hex_string()

        lines = []
        for response_part in response_parts:
            lines.append(f'--{response_boundary}')
            lines.append(response_part)

        lines.append(f'--{response_boundary}--')
        lines.append('')

        body_bytes = '\r\n'.join(lines).encode('utf8')

        self._send(OK, body_bytes, f'multipart/mixed; boundary={response_boundary}')

# ################################################################################################################################

    def _handle_batch_json(self, record:'stranydict', raw_body:'bytes') -> 'None':
        """ Handles a V4 JSON $batch - each request dispatches and the responses
        travel back under 'responses', in request order.
        """
        envelope = loads(raw_body)

        batch_requests = []
        responses = []

        for item in envelope['requests']:
            method = item['method']
            url = item['url']
            body = item.get('body')

            batch_requests.append({'method': method, 'url': url, 'json': body})

            status, _, response_body, _ = self._dispatch_batch_part(method, url, body)

            response:'anydict' = {'id': item['id'], 'status': status}

            if response_body:
                response['body'] = loads(response_body)

            responses.append(response)

        record['batch_requests'] = batch_requests

        payload = dumps({'responses': responses}).encode('utf8')

        self._send(OK, payload, 'application/json')

# ################################################################################################################################

    def _handle(self) -> 'None':

        server:'any_' = self.server

        raw_body = self._read_body()

        split = urlsplit(self.path)
        path = split.path
        params = dict(parse_qsl(split.query, keep_blank_values=True))

        record = self._record(path, params, raw_body)

        server.recorded_requests.append(record)
        server.last_request = record

        # The token endpoint lives outside the OData service root.
        if path == Token_Endpoint_Path:
            self._handle_token_request(raw_body)
            return

        try:
            server.check_auth(dict(self.headers.items()))

            server.check_csrf(self.command, dict(self.headers.items()))

            # A read asking for a CSRF token gets one in the response header.
            wants_csrf_token = (self.headers.get(_csrf_header) or '').lower() == 'fetch'

            csrf_response_headers = {}
            if wants_csrf_token:
                if server.profile == Profile.S4HANA:
                    csrf_response_headers[_csrf_header] = server.issue_csrf_token()

            relative = path[len(server.service_root):].strip('/')

            # A batch envelope unpacks into many dispatches.
            if relative == '$batch':
                self._handle_batch(record, raw_body)
                return

            # A bare service-root request is what pings arrive as.
            if not relative:
                self._send(OK, b'{}', 'application/json', csrf_response_headers)
                return

            body = record['json']

            status, extra_headers, response_body, content_type = server.dispatch(
                self.command, path, params, dict(self.headers.items()), body)

            extra_headers.update(csrf_response_headers)

            self._send(status, response_body, content_type, extra_headers)

        except _Rejected as rejected:
            self._send(rejected.status, rejected.body, rejected.content_type, rejected.headers)

# ################################################################################################################################

    do_GET    = _handle
    do_POST   = _handle
    do_PATCH  = _handle
    do_MERGE  = _handle
    do_DELETE = _handle
    do_HEAD   = _handle

# ################################################################################################################################

    def log_message(self, format:'str', *args:'any_') -> 'None':
        logger.info('[odata_test_server] %s', format % args)

# ################################################################################################################################
# ################################################################################################################################

def _extract_multipart_boundary(content_type:'str') -> 'str':
    """ Returns the boundary parameter of a multipart Content-Type or part header block.
    """
    for fragment in content_type.replace('\r\n', ';').split(';'):
        fragment = fragment.strip()
        if fragment.startswith('boundary='):
            out = fragment[len('boundary='):].strip('"')
            break
    else:
        raise ValueError(f'No boundary in `{content_type}`')

    return out

# ################################################################################################################################

def _split_multipart(body:'str', boundary:'str') -> 'list[str]':
    """ Splits a multipart body into its parts, dropping the preamble and the epilogue.
    """
    delimiter = f'--{boundary}'

    segments = body.split(delimiter)

    out = []
    for segment in segments[1:-1]:
        out.append(segment.strip('\r\n'))

    return out

# ################################################################################################################################

def _parse_http_part(part:'str') -> 'tuple[str, str, anydict | None]':
    """ Parses one application/http part into its method, URL and JSON body.
    """
    _, _, http_message = part.partition('\r\n\r\n')

    request_line, _, rest = http_message.partition('\r\n')

    method, url, _ = request_line.split(' ', 2)

    _, _, body_text = rest.partition('\r\n\r\n')
    body_text = body_text.strip()

    if body_text:
        body = loads(body_text)
    else:
        body = None

    out = (method, url, body)
    return out

# ################################################################################################################################

def _render_http_response(status:'int', headers:'strdict', body:'bytes', content_type:'str') -> 'str':
    """ Renders one response as the application/http payload of a multipart response part.
    """
    lines = [
        'Content-Type: application/http',
        'Content-Transfer-Encoding: binary',
        '',
        f'HTTP/1.1 {status} X',
        f'Content-Type: {content_type}',
    ]

    for name, value in headers.items():
        lines.append(f'{name}: {value}')

    lines.append('')
    lines.append(body.decode('utf8'))

    out = '\r\n'.join(lines)
    return out

# ################################################################################################################################

def _render_changeset(rendered_responses:'list[str]') -> 'str':
    """ Wraps rendered responses in one changeset part.
    """
    changeset_boundary = 'changesetresponse_' + CryptoManager.generate_hex_string()

    lines = [f'Content-Type: multipart/mixed; boundary={changeset_boundary}', '']

    for rendered in rendered_responses:
        lines.append(f'--{changeset_boundary}')
        lines.append(rendered)

    lines.append(f'--{changeset_boundary}--')

    out = '\r\n'.join(lines)
    return out

# ################################################################################################################################
# ################################################################################################################################

class ODataTestServer:
    """ A live OData server for client tests - it simulates one of four systems, records
    every request and answers per-path, over plain HTTP or HTTPS.
    """
    def __init__(self, profile:'str', tls:'bool'=False) -> 'None':
        self.profile = profile
        self.host = '127.0.0.1'
        self.port = 0
        self.tls = tls
        self.scheme = 'https' if tls else 'http'

        self.tls_material:'TLSMaterial | None' = None
        self._httpd:'any_' = None
        self._thread:'any_' = None

# ################################################################################################################################

    def start(self) -> 'None':
        """ Binds to an ephemeral port and serves in a background thread, wrapping
        the socket in TLS when configured to.
        """
        self._httpd = _Server(self.profile, (self.host, 0), _Handler)
        self.port = self._httpd.server_address[1]

        if self.tls:
            tls_material = build_tls_material(self.host)
            self.tls_material = tls_material

            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(tls_material.server_certificate_path, tls_material.server_key_path)

            self._httpd.socket = ssl_context.wrap_socket(self._httpd.socket, server_side=True)

        # The metadata document and next links need the full base address.
        self._httpd.base_address = self.address
        self._httpd.metadata_document = self._load_metadata()

        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

        logger.info('[ODataTestServer] started on %s (%s)', self.address, self.profile)

# ################################################################################################################################

    def _load_metadata(self) -> 'bytes':
        """ Reads the profile's $metadata document from the file next to this module.
        """
        path = os.path.join(_metadata_dir, _metadata_file[self.profile])

        with open(path, 'rb') as metadata_file:
            out = metadata_file.read()

        return out

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the server and removes any temporary TLS material.
        """
        self._httpd.shutdown()
        self._httpd.server_close()

        if self.tls_material:
            shutil.rmtree(self.tls_material.directory, ignore_errors=True)

        logger.info('[ODataTestServer] stopped on %s (%s)', self.address, self.profile)

# ################################################################################################################################

    @property
    def address(self) -> 'str':
        out = f'{self.scheme}://{self.host}:{self.port}'
        return out

# ################################################################################################################################

    @property
    def service_root(self) -> 'str':
        """ Returns the full URL of the profile's service root.
        """
        out = f'{self.address}{Profile_Service_Root[self.profile]}'
        return out

# ################################################################################################################################

    @property
    def token_url(self) -> 'str':
        """ Returns the full URL of the token endpoint the Dynamics profile serves.
        """
        out = f'{self.address}{Token_Endpoint_Path}'
        return out

# ################################################################################################################################

    def url(self, path:'str') -> 'str':
        """ Returns the full URL of a path on this server.
        """
        out = f'{self.address}{path}'
        return out

# ################################################################################################################################

    def configure(self, path:'str', **config:'any_') -> 'None':
        """ Sets the per-path response configuration - respond_error, respond_json,
        operation, delay, and so on. Paths are absolute, without the host part.
        """
        self._httpd.path_config[path] = config

# ################################################################################################################################

    def add_entities(self, entity_set:'str', key_property:'str', items:'anylist') -> 'None':
        self._httpd.add_entities(entity_set, key_property, items)

# ################################################################################################################################

    def reset(self) -> 'None':
        self._httpd.reset()

# ################################################################################################################################

    def set_credentials(self, username:'str', password:'str') -> 'None':
        self._httpd.expected_username = username
        self._httpd.expected_password = password

# ################################################################################################################################

    def set_oauth_client(self, client_id:'str', client_secret:'str') -> 'None':
        self._httpd.expected_client_id = client_id
        self._httpd.expected_client_secret = client_secret

# ################################################################################################################################

    def require_query_params(self, params:'strdict') -> 'None':
        self._httpd.required_query_params.update(params)

# ################################################################################################################################

    def set_page_size(self, page_size:'int') -> 'None':
        self._httpd.page_size = page_size

# ################################################################################################################################

    @property
    def entities(self) -> 'stranydict':
        out = self._httpd.entities
        return out

# ################################################################################################################################

    @property
    def issued_tokens(self) -> 'anylist':
        out = self._httpd.issued_tokens
        return out

# ################################################################################################################################

    @property
    def last_request(self) -> 'anydict':
        out = self._httpd.last_request
        return out

# ################################################################################################################################

    @property
    def recorded_requests(self) -> 'anylist':
        out = self._httpd.recorded_requests
        return out

# ################################################################################################################################

    def clear_requests(self) -> 'None':
        self._httpd.recorded_requests.clear()
        self._httpd.last_request = None

# ################################################################################################################################
# ################################################################################################################################
