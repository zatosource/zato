# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import gzip
import json
import logging
import re
import shutil
import ssl
import threading
from http.client import OK
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################

from certs import build_tls_material

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict
    from certs import TLSMaterial

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# The Snowflake wire protocol identifies a SELECT statement with this type ID.
_Statement_Type_Select = 4096

# Error details for SQL that no configured result matches.
_No_Match_Error_Code = '002003'
_No_Match_SQL_State = '42S02'

# Error details for a login with wrong credentials.
_Login_Error_Code = '390100'

# The authorization scheme the connector uses for session tokens.
_Token_Header_Pattern = re.compile(r'Snowflake Token="(?P<token>[^"]+)"')

# ################################################################################################################################
# ################################################################################################################################

def _column(name:'str', type_:'str') -> 'stranydict':
    """ Builds one Snowflake column description in the shape the connector's result metadata expects.
    """
    if type_ == 'fixed':
        scale = 0
        precision = 19
    else:
        scale = None
        precision = None

    out = {
        'name': name,
        'type': type_,
        'length': None,
        'precision': precision,
        'scale': scale,
        'nullable': True,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class _Handler(BaseHTTPRequestHandler):
    """ Implements the subset of the Snowflake HTTPS REST protocol that snowflake-connector-python
    speaks - login, query execution, token renewal, heartbeat, logout and query aborting.
    """

    protocol_version = 'HTTP/1.1'

    def _read_body(self) -> 'bytes':
        if 'Content-Length' in self.headers:
            length = int(self.headers['Content-Length'])
            out = self.rfile.read(length)
        else:
            out = b''

        # The connector compresses request bodies, so transparently expand them here.
        if self.headers.get('Content-Encoding') == 'gzip':
            out = gzip.decompress(out)

        return out

# ################################################################################################################################

    def _send_json(self, payload:'anydict') -> 'None':
        body = json.dumps(payload).encode('utf-8')

        self.send_response(OK)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()

        _ = self.wfile.write(body)

# ################################################################################################################################

    def _record(self, path:'str', body:'anydict', query_params:'anydict') -> 'None':
        server:'any_' = self.server

        record = {
            'path': path,
            'method': self.command,
            'headers': dict(self.headers.items()),
            'body': body,
            'query_params': query_params,
        }

        server.recorded_requests.append(record)
        server.last_request = record

# ################################################################################################################################

    def _session_token_from_headers(self) -> 'str':
        """ Extracts the session token from the Authorization header, returning an empty string if there is none.
        """
        authorization = self.headers.get('Authorization', '')

        if match := _Token_Header_Pattern.search(authorization):
            out = match.group('token')
        else:
            out = ''

        return out

# ################################################################################################################################

    def do_POST(self) -> 'None':

        server:'any_' = self.server

        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        raw_body = self._read_body()

        if raw_body:
            body = json.loads(raw_body)
        else:
            body = {}

        self._record(path, body, query_params)

        # Dispatch on the request path ..
        if path == '/session/v1/login-request':
            response = server.build_login_response(body, query_params)

        elif path == '/queries/v1/query-request':
            token = self._session_token_from_headers()
            response = server.build_query_response(body, token)

        elif path == '/session/token-request':
            response = server.build_token_renewal_response()

        elif path == '/session/heartbeat':
            response = {'success': True, 'message': None, 'data': None}

        elif path == '/session':
            server.forget_token(self._session_token_from_headers())
            response = {'success': True, 'message': None, 'data': None}

        elif path == '/queries/v1/abort-request':
            response = {'success': True, 'message': None, 'data': None}

        elif path == '/telemetry/send':
            response = {'success': True, 'message': None, 'data': None}

        # .. anything else is not part of the protocol subset the tests exercise.
        else:
            response = {
                'success': False,
                'message': f'Unknown path `{path}`',
                'code': _No_Match_Error_Code,
                'data': {'sqlState': _No_Match_SQL_State},
            }

        self._send_json(response)

# ################################################################################################################################

    def log_message(self, format:'str', *args:'any_') -> 'None':
        logger.info('[snowflake_test_server] %s', format % args)

# ################################################################################################################################
# ################################################################################################################################

class _Server(ThreadingHTTPServer):
    """ Holds the recorded requests, the credentials and the regex-keyed canned results,
    plus the response-building logic for each protocol message.
    """
    daemon_threads = True

    def __init__(self, *args:'any_', **kwargs:'any_') -> 'None':
        super().__init__(*args, **kwargs)

        self.recorded_requests:'anylist' = []
        self.last_request:'anydict | None' = None

        # Credentials every login is checked against.
        self.user = 'test_user'
        self.password = 'test_password'
        self.account = 'testaccount'

        # What the current session's database and schema are, as captured from the login request.
        self.session_database = 'TESTDB'
        self.session_schema = 'PUBLIC'

        # Session tokens issued by logins and renewals.
        self.tokens:'anydict' = {}

        # The regex-keyed table of canned results, searched in order, first match wins.
        self.results:'anylist' = []

        self.add_default_results()

# ################################################################################################################################

    def add_default_results(self) -> 'None':
        """ Adds the on-connect queries snowflake-sqlalchemy issues plus a ping query.
        """
        self.add_result(r'select current_version\(\)', columns=[('CURRENT_VERSION()', 'text')], rows=[['8.45.0']])

        self.add_result(
            r'select current_database\(\), current_schema\(\)',
            columns=[('CURRENT_DATABASE()', 'text'), ('CURRENT_SCHEMA()', 'text')],
            rows=[[self.session_database, self.session_schema]],
        )

        self.add_result(r'^\s*select\s+1\s*;?\s*$', columns=[('1', 'fixed')], rows=[[1]])

        self.add_result(
            r'^\s*(alter\s+session|commit|rollback|begin)',
            columns=[('status', 'text')],
            rows=[['Statement executed successfully.']],
        )

# ################################################################################################################################

    def add_result(self, pattern:'str', columns:'anylist', rows:'anylist') -> 'None':
        """ Registers a canned result for every SQL statement matching the pattern.
        """
        spec = {
            'is_error': False,
            'columns': columns,
            'rows': rows,
        }

        self.results.insert(0, (re.compile(pattern, re.IGNORECASE), spec))

# ################################################################################################################################

    def add_error(
        self,
        pattern:'str',
        message:'str',
        code:'str'=_No_Match_Error_Code,
        sqlstate:'str'=_No_Match_SQL_State,
        ) -> 'None':
        """ Registers an error response for every SQL statement matching the pattern.
        """
        spec = {
            'is_error': True,
            'message': message,
            'code': code,
            'sqlstate': sqlstate,
        }

        self.results.insert(0, (re.compile(pattern, re.IGNORECASE), spec))

# ################################################################################################################################

    def new_token(self) -> 'str':
        out = 'session.token.' + CryptoManager.generate_hex_string()
        self.tokens[out] = True

        return out

# ################################################################################################################################

    def forget_token(self, token:'str') -> 'None':
        _ = self.tokens.pop(token, None)

# ################################################################################################################################

    def build_login_response(self, body:'anydict', query_params:'anydict') -> 'anydict':
        """ Validates the credentials from the login request and issues session tokens.
        """
        data = body['data']

        login_name = data.get('LOGIN_NAME', '')
        password = data.get('PASSWORD', '')
        account_name = data.get('ACCOUNT_NAME', '')

        is_user_ok = login_name.lower() == self.user.lower()
        is_password_ok = password == self.password
        is_account_ok = account_name.lower() == self.account.lower()

        # Reject a login whose credentials do not match what the test configured ..
        if not (is_user_ok and is_password_ok and is_account_ok):
            out = {
                'success': False,
                'message': 'Incorrect username or password was specified.',
                'code': _Login_Error_Code,
                'data': {'authnMethod': 'USERNAME_PASSWORD'},
            }
            return out

        # .. capture the session's database and schema for the on-connect queries ..
        if database_name := query_params.get('databaseName'):
            self.session_database = database_name[0].upper()

        if schema_name := query_params.get('schemaName'):
            self.session_schema = schema_name[0].upper()

        # .. and issue the session tokens the connector will use from now on.
        token = self.new_token()
        master_token = 'master.token.' + CryptoManager.generate_hex_string()

        out = {
            'success': True,
            'message': None,
            'code': None,
            'data': {
                'token': token,
                'masterToken': master_token,
                'sessionId': 1,
                'parameters': [
                    {'name': 'TIMEZONE', 'value': 'UTC'},
                    {'name': 'PYTHON_CONNECTOR_QUERY_RESULT_FORMAT', 'value': 'JSON'},
                ],
            },
        }

        return out

# ################################################################################################################################

    def build_query_response(self, body:'anydict', token:'str') -> 'anydict':
        """ Answers one query request from the regex-keyed table of canned results.
        """
        # A query request without a valid session token is rejected outright ..
        if token not in self.tokens:
            out = {
                'success': False,
                'message': 'Session token is invalid.',
                'code': _Login_Error_Code,
                'data': {'sqlState': '08001'},
            }
            return out

        sql_text = body['sqlText']

        # .. find the first canned result whose pattern matches the SQL ..
        for pattern, spec in self.results:
            if pattern.search(sql_text):
                break
        else:
            spec = {
                'is_error': True,
                'message': f'No canned result matches SQL: {sql_text}',
                'code': _No_Match_Error_Code,
                'sqlstate': _No_Match_SQL_State,
            }

        query_id = 'query.' + CryptoManager.generate_hex_string()

        # .. errors are reported in the Snowflake error shape ..
        if spec['is_error']:
            out = {
                'success': False,
                'message': spec['message'],
                'code': spec['code'],
                'data': {
                    'sqlState': spec['sqlstate'],
                    'errorCode': spec['code'],
                    'queryId': query_id,
                },
            }
            return out

        # .. and everything else in the JSON result shape - column metadata plus string rows.
        rowtype = []
        for name, type_ in spec['columns']:
            rowtype.append(_column(name, type_))

        rowset = []
        for row in spec['rows']:
            wire_row = []
            for value in row:
                wire_row.append(str(value))
            rowset.append(wire_row)

        out = {
            'success': True,
            'message': None,
            'code': None,
            'data': {
                'parameters': [],
                'rowtype': rowtype,
                'rowset': rowset,
                'total': len(rowset),
                'returned': len(rowset),
                'queryId': query_id,
                'queryResultFormat': 'json',
                'finalDatabaseName': self.session_database,
                'finalSchemaName': self.session_schema,
                'sqlState': '00000',
                'statementTypeId': _Statement_Type_Select,
            },
        }

        return out

# ################################################################################################################################

    def build_token_renewal_response(self) -> 'anydict':
        """ Issues a fresh session token in exchange for the old one.
        """
        token = self.new_token()
        master_token = 'master.token.' + CryptoManager.generate_hex_string()

        out = {
            'success': True,
            'message': None,
            'code': None,
            'data': {
                'sessionToken': token,
                'masterToken': master_token,
            },
        }

        return out

# ################################################################################################################################
# ################################################################################################################################

class SnowflakeTestServer:
    """ A live server speaking the Snowflake HTTPS REST protocol for client tests.
    It records every request and answers queries from a regex-keyed table of canned results,
    over HTTPS with a locally generated test CA or over plain HTTP.
    """
    def __init__(self, tls:'bool'=True) -> 'None':
        self.host = '127.0.0.1'
        self.port = 0
        self.tls = tls
        self.scheme = 'https' if tls else 'http'

        self.tls_material:'TLSMaterial | None' = None
        self._httpd:'any_' = None
        self._thread:'any_' = None

# ################################################################################################################################

    def start(self) -> 'None':
        """ Binds to an ephemeral port and serves in a background thread,
        wrapping the socket in TLS when configured to.
        """
        self._httpd = _Server((self.host, 0), _Handler)
        self.port = self._httpd.server_address[1]

        if self.tls:
            self.tls_material = build_tls_material(self.host)

            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(self.tls_material.server_certificate_path, self.tls_material.server_key_path)

            self._httpd.socket = ssl_context.wrap_socket(self._httpd.socket, server_side=True)

        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

        logger.info('[SnowflakeTestServer] started on %s://%s:%s', self.scheme, self.host, self.port)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the server and removes any temporary TLS material.
        """
        self._httpd.shutdown()
        self._httpd.server_close()

        if self.tls_material:
            shutil.rmtree(self.tls_material.directory, ignore_errors=True)

        logger.info('[SnowflakeTestServer] stopped on %s://%s:%s', self.scheme, self.host, self.port)

# ################################################################################################################################

    def configure(
        self,
        user:'str'='',
        password:'str'='',
        account:'str'='',
        ) -> 'None':
        """ Sets the credentials logins are checked against.
        """
        if user:
            self._httpd.user = user

        if password:
            self._httpd.password = password

        if account:
            self._httpd.account = account

# ################################################################################################################################

    def add_result(self, pattern:'str', columns:'anylist', rows:'anylist') -> 'None':
        self._httpd.add_result(pattern, columns, rows)

# ################################################################################################################################

    def add_error(
        self,
        pattern:'str',
        message:'str',
        code:'str'=_No_Match_Error_Code,
        sqlstate:'str'=_No_Match_SQL_State,
        ) -> 'None':
        self._httpd.add_error(pattern, message, code, sqlstate)

# ################################################################################################################################

    @property
    def user(self) -> 'str':
        out = self._httpd.user
        return out

# ################################################################################################################################

    @property
    def password(self) -> 'str':
        out = self._httpd.password
        return out

# ################################################################################################################################

    @property
    def account(self) -> 'str':
        out = self._httpd.account
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
