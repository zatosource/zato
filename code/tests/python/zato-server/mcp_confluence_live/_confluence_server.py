# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import threading
from base64 import b64decode
from http.client import BAD_REQUEST, NOT_FOUND, OK, UNAUTHORIZED
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from json import dumps, loads
from urllib.parse import parse_qs, urlparse

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, anytuple, strnone

# ################################################################################################################################
# ################################################################################################################################

def _build_initial_spaces() -> 'anylist':
    """ Returns the spaces the simulated Confluence site starts with.
    """
    return [
        {
            'id': 100001,
            'key': 'ENG',
            'name': 'Engineering wiki',
            'type': 'global',
            'status': 'current',
        },
        {
            'id': 100002,
            'key': 'PROD',
            'name': 'Product documentation',
            'type': 'global',
            'status': 'current',
        },
    ]

# ################################################################################################################################

def _build_initial_pages() -> 'anydict':
    """ Returns the pages the simulated Confluence site starts with.
    """
    return {
        '200001': {
            'id': '200001',
            'type': 'page',
            'status': 'current',
            'title': 'Deployment runbook',
            'space': {'key': 'ENG'},
            'body': {'storage': {'value': '<p>How we deploy to production</p>', 'representation': 'storage'}},
            'version': {'number': 3},
        },
        '200002': {
            'id': '200002',
            'type': 'page',
            'status': 'current',
            'title': 'Release notes',
            'space': {'key': 'PROD'},
            'body': {'storage': {'value': '<p>What changed in each release</p>', 'representation': 'storage'}},
            'version': {'number': 1},
        },
    }

# ################################################################################################################################
# ################################################################################################################################

class ConfluenceTestHandler(BaseHTTPRequestHandler):
    """ Simulates the Confluence REST paths the curated MCP tool methods use -
    spaces, content by ID, content queries, page creation and updates, and CQL search.
    """

    # Credentials every request must carry as basic auth
    expected_username:'strnone' = None
    expected_token:'strnone' = None

    # The state of the simulated site
    spaces:'anylist' = []
    pages:'anydict' = {}

    # How many pages were created so far, used to build new IDs
    page_counter = 0

    def log_message(self, format:'any_', *args:'any_') -> 'None':
        pass

# ################################################################################################################################

    def _send_json(self, status:'int', data:'anydict') -> 'None':
        body = dumps(data).encode('utf8')

        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        _ = self.wfile.write(body)

# ################################################################################################################################

    def _read_json_body(self) -> 'anydict':
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)

        out = loads(body.decode('utf8'))
        return out

# ################################################################################################################################

    def _check_auth(self) -> 'bool':
        """ Every request must carry the basic credentials the site was started with.
        """

        authorization = self.headers.get('Authorization')

        if not authorization:
            return False

        if not authorization.startswith('Basic '):
            return False

        decoded = b64decode(authorization[len('Basic '):]).decode('utf8')
        username, _, token = decoded.partition(':')

        if username != self.expected_username:
            return False

        if token != self.expected_token:
            return False

        return True

# ################################################################################################################################

    def _handle_space_list(self) -> 'None':
        """ GET /rest/api/space - all the spaces of the site.
        """
        self._send_json(OK, {
            'results': self.spaces,
            'start': 0,
            'limit': 50,
            'size': len(self.spaces),
        })

# ################################################################################################################################

    def _handle_content_query(self, params:'anydict') -> 'None':
        """ GET /rest/api/content - pages filtered by space key and title,
        the query get_page_by_title sends.
        """

        if space_key_values := params.get('spaceKey'):
            space_key = space_key_values[0]
        else:
            space_key = ''

        if title_values := params.get('title'):
            title = title_values[0]
        else:
            title = ''

        results = []

        for page in self.pages.values():

            if space_key:
                page_space = page['space']
                if page_space['key'] != space_key:
                    continue

            if title:
                if page['title'] != title:
                    continue

            results.append(page)

        self._send_json(OK, {'results': results, 'size': len(results)})

# ################################################################################################################################

    def _handle_content_create(self) -> 'None':
        """ POST /rest/api/content - a new page.
        """

        request_data = self._read_json_body()

        ConfluenceTestHandler.page_counter += 1
        page_id = str(300000 + self.page_counter)

        page = {
            'id': page_id,
            'type': request_data['type'],
            'status': 'current',
            'title': request_data['title'],
            'space': request_data['space'],
            'body': request_data['body'],
            'version': {'number': 1},
        }

        ConfluenceTestHandler.pages[page_id] = page

        self._send_json(OK, page)

# ################################################################################################################################

    def _handle_content_update(self, page_id:'str') -> 'None':
        """ PUT /rest/api/content/{page_id} - a page update with a version bump.
        """

        page = self.pages[page_id]
        request_data = self._read_json_body()

        page['title'] = request_data['title']

        if 'body' in request_data:
            page['body'] = request_data['body']

        page['version'] = request_data['version']

        self._send_json(OK, page)

# ################################################################################################################################

    def _handle_search(self, params:'anydict') -> 'None':
        """ GET /rest/api/search - a CQL query, answered with every page wrapped
        the way the real search endpoint shapes its results.
        """

        if cql_values := params.get('cql'):
            cql_text = cql_values[0]
        else:
            self._send_json(BAD_REQUEST, {'message': 'The cql parameter is required'})
            return

        results = []

        for page in self.pages.values():
            results.append({
                'content': page,
                'title': page['title'],
                'excerpt': '',
                'url': f'/pages/{page["id"]}',
            })

        self._send_json(OK, {
            'results': results,
            'start': 0,
            'limit': 25,
            'size': len(results),
            'cqlQuery': cql_text,
        })

# ################################################################################################################################

    def _handle_request(self, method:'str') -> 'None':

        parsed_path = urlparse(self.path)
        path = parsed_path.path
        params = parse_qs(parsed_path.query)

        # Every path requires valid credentials ..
        if not self._check_auth():
            self._send_json(UNAUTHORIZED, {'message': 'Basic credentials are required'})
            return

        # .. GET /rest/api/space - the space list ..
        if path == '/rest/api/space':
            if method == 'GET':
                self._handle_space_list()
                return

        # .. GET /rest/api/search - a CQL query ..
        if path == '/rest/api/search':
            if method == 'GET':
                self._handle_search(params)
                return

        # .. /rest/api/content - queries and page creation ..
        if path == '/rest/api/content':

            if method == 'GET':
                self._handle_content_query(params)
                return

            if method == 'POST':
                self._handle_content_create()
                return

        # .. /rest/api/content/{page_id} - a single page, or its history,
        # which update_page reads to compute the next version number.
        if path.startswith('/rest/api/content/'):

            page_id = path[len('/rest/api/content/'):]

            wants_history = page_id.endswith('/history')

            if wants_history:
                page_id = page_id[:-len('/history')]

            if page_id not in self.pages:
                self._send_json(NOT_FOUND, {'message': f'No content with ID {page_id}'})
                return

            if wants_history:
                if method == 'GET':
                    page = self.pages[page_id]
                    page_version = page['version']
                    self._send_json(OK, {'lastUpdated': {'number': page_version['number']}})
                    return

            if method == 'GET':
                self._send_json(OK, self.pages[page_id])
                return

            if method == 'PUT':
                self._handle_content_update(page_id)
                return

        # No handler matched the path.
        self._send_json(NOT_FOUND, {'message': f'No such path: {method} {path}'})

# ################################################################################################################################

    def do_GET(self) -> 'None':
        self._handle_request('GET')

    def do_POST(self) -> 'None':
        self._handle_request('POST')

    def do_PUT(self) -> 'None':
        self._handle_request('PUT')

# ################################################################################################################################
# ################################################################################################################################

def start_confluence_server(port:'int', username:'str', token:'str') -> 'anytuple':
    """ Starts the simulated Confluence site in a background thread. Returns (server, thread).
    """

    ConfluenceTestHandler.expected_username = username
    ConfluenceTestHandler.expected_token = token

    ConfluenceTestHandler.spaces = _build_initial_spaces()
    ConfluenceTestHandler.pages = _build_initial_pages()
    ConfluenceTestHandler.page_counter = 0

    server = ThreadingHTTPServer(('127.0.0.1', port), ConfluenceTestHandler)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    return server, thread

# ################################################################################################################################
# ################################################################################################################################
