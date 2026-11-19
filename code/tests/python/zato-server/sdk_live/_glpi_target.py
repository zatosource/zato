# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import threading
from http.client import BAD_REQUEST, CREATED, NOT_FOUND, OK, UNAUTHORIZED
from http.server import BaseHTTPRequestHandler

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, intanydict, stranydict, strset

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.sdk_live.glpi')

# ################################################################################################################################
# ################################################################################################################################

# The prefix of every path of the GLPI REST API
_api_prefix = '/apirest.php/'

# The prefix of the paths that address a single ticket
_ticket_prefix = 'Ticket/'

# The ID the first stored ticket receives
_first_ticket_id = 1

# ################################################################################################################################
# ################################################################################################################################

class GLPIState:
    """ What the GLPI mode shares with tests - the tokens it accepts, the sessions it opened,
    how many sessions were opened and closed, and the tickets it stores.
    """
    def __init__(self) -> 'None':
        self.lock = threading.Lock()

        # The tokens initSession accepts.
        self.app_token = 'glpi.app.' + CryptoManager.generate_hex_string()
        self.user_token = 'glpi.user.' + CryptoManager.generate_hex_string()

        # The tokens of the sessions that are open.
        self.sessions:'strset' = set()

        # How many times initSession and killSession succeeded.
        self.init_count = 0
        self.kill_count = 0

        # The tickets by their IDs.
        self.tickets:'intanydict' = {}
        self.next_ticket_id = _first_ticket_id

# ################################################################################################################################

    def add_ticket(self, fields:'stranydict') -> 'int':
        """ Stores a new ticket and returns its ID.
        """
        with self.lock:
            out = self.next_ticket_id
            self.next_ticket_id += 1
            self.tickets[out] = {'id': out, **fields}

        return out

# ################################################################################################################################

    def end_sessions(self) -> 'None':
        """ Makes every open session invalid, as GLPI does when sessions expire.
        """
        with self.lock:
            self.sessions.clear()

glpi_state = GLPIState()

# ################################################################################################################################
# ################################################################################################################################

class GLPIHandler(BaseHTTPRequestHandler):
    """ The GLPI mode of the suite's target server - it stands in for the GLPI REST API, opening sessions
    in initSession, closing them in killSession and answering with GLPI's error codes when a token is wrong.
    """
    def log_message(self, format:'str', *args:'any_') -> 'None':
        logger.debug(format, *args)

# ################################################################################################################################

    def _send_json(self, status:'int', data:'any_') -> 'None':
        body = json.dumps(data).encode('utf8')

        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()

        _ = self.wfile.write(body)

# ################################################################################################################################

    def _send_error(self, status:'int', error_code:'str', error_message:'str') -> 'None':
        self._send_json(status, [error_code, error_message])

# ################################################################################################################################

    def _get_path(self) -> 'str':
        out = self.path.removeprefix(_api_prefix)
        return out

# ################################################################################################################################

    def _has_app_token(self) -> 'bool':
        out = self.headers['App-Token'] == glpi_state.app_token
        return out

# ################################################################################################################################

    def _has_session(self) -> 'bool':
        with glpi_state.lock:
            out = self.headers['Session-Token'] in glpi_state.sessions
        return out

# ################################################################################################################################

    def _init_session(self) -> 'None':

        # The user token must be the one the test configured ..
        if self.headers['Authorization'] != f'user_token {glpi_state.user_token}':
            self._send_error(UNAUTHORIZED, 'ERROR_GLPI_LOGIN_USER_TOKEN', 'parameter user_token seems invalid')

        # .. in which case a new session is opened.
        else:
            session_token = CryptoManager.generate_hex_string()

            with glpi_state.lock:
                glpi_state.sessions.add(session_token)
                glpi_state.init_count += 1

            self._send_json(OK, {'session_token': session_token})

# ################################################################################################################################

    def _kill_session(self) -> 'None':

        with glpi_state.lock:
            glpi_state.sessions.discard(self.headers['Session-Token'])
            glpi_state.kill_count += 1

        self._send_json(OK, True)

# ################################################################################################################################

    def _get_ticket(self, path:'str') -> 'None':

        ticket_id = int(path.removeprefix(_ticket_prefix))

        with glpi_state.lock:
            ticket = glpi_state.tickets.get(ticket_id)

        # A ticket that does not exist is reported as such ..
        if ticket is None:
            self._send_error(NOT_FOUND, 'ERROR_ITEM_NOT_FOUND', 'Item not found')

        # .. and an existing one is returned as it is.
        else:
            self._send_json(OK, ticket)

# ################################################################################################################################

    def do_GET(self) -> 'None':

        path = self._get_path()

        # Every request must include the application token ..
        if not self._has_app_token():
            self._send_error(BAD_REQUEST, 'ERROR_WRONG_APP_TOKEN_PARAMETER', 'parameter app_token seems wrong')

        # .. a session is opened without a session token ..
        elif path == 'initSession':
            self._init_session()

        # .. and everything else requires one.
        elif not self._has_session():
            self._send_error(UNAUTHORIZED, 'ERROR_SESSION_TOKEN_INVALID', 'session_token seems invalid')

        elif path == 'getFullSession':
            self._send_json(OK, {'session': {'glpiname': 'zato'}})

        elif path == 'killSession':
            self._kill_session()

        elif path.startswith(_ticket_prefix):
            self._get_ticket(path)

        # Anything else is not a resource this mode serves.
        else:
            self._send_error(BAD_REQUEST, 'ERROR_RESOURCE_NOT_FOUND_NOR_COMMONDBTM', f'resource {path} not found')

# ################################################################################################################################

    def do_POST(self) -> 'None':

        path = self._get_path()

        # Read the request body ..
        content_length = int(self.headers['Content-Length'])
        body = json.loads(self.rfile.read(content_length))

        # .. the same tokens are required as with GET requests ..
        if not self._has_app_token():
            self._send_error(BAD_REQUEST, 'ERROR_WRONG_APP_TOKEN_PARAMETER', 'parameter app_token seems wrong')

        elif not self._has_session():
            self._send_error(UNAUTHORIZED, 'ERROR_SESSION_TOKEN_INVALID', 'session_token seems invalid')

        # .. a new ticket is stored with the fields under the input key ..
        elif path == 'Ticket':
            ticket_id = glpi_state.add_ticket(body['input'])
            self._send_json(CREATED, {'id': ticket_id, 'message': ''})

        # .. and anything else is not a resource this mode serves.
        else:
            self._send_error(BAD_REQUEST, 'ERROR_RESOURCE_NOT_FOUND_NOR_COMMONDBTM', f'resource {path} not found')

# ################################################################################################################################
# ################################################################################################################################
