# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import re
import shutil
import socketserver
import ssl
import struct
import threading
from hashlib import md5

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################

from certs import build_tls_material

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist
    from certs import TLSMaterial

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# The magic packet code a client sends to request a TLS upgrade.
_SSL_Request_Code = 80877103

# The PostgreSQL frontend/backend protocol version 3.0.
_Protocol_Version = 196608

# The authentication codes the simulator uses.
_Auth_MD5_Password = 5
_Auth_OK = 0

# Type OIDs for the columns canned results can carry.
_OID_Int4 = 23
_OID_Text = 25

_Type_OIDs = {
    'int': _OID_Int4,
    'text': _OID_Text,
}

_Type_Sizes = {
    'int': 4,
    'text': -1,
}

# SQLSTATE codes for the errors the simulator reports.
_SQL_State_Auth_Failed = '28P01'
_No_Match_SQL_State = '42P01'

# ################################################################################################################################
# ################################################################################################################################

def _read_exact(sock:'any_', size:'int') -> 'bytes':
    """ Reads exactly the given number of bytes from a socket, returning fewer only on EOF.
    """
    chunks = []
    remaining = size

    while remaining:
        chunk = sock.recv(remaining)
        if not chunk:
            break
        chunks.append(chunk)
        remaining -= len(chunk)

    out = b''.join(chunks)
    return out

# ################################################################################################################################

def _message(code:'bytes', payload:'bytes') -> 'bytes':
    """ Frames one backend message - the type byte plus the length-prefixed payload.
    """
    out = code + struct.pack('!i', len(payload) + 4) + payload
    return out

# ################################################################################################################################

def _cstring(value:'str') -> 'bytes':
    out = value.encode('utf-8') + b'\x00'
    return out

# ################################################################################################################################

def _error_response(severity:'str', sqlstate:'str', message:'str') -> 'bytes':
    """ Builds an ErrorResponse message with the severity, SQLSTATE and human-readable fields.
    """
    payload = b'S' + _cstring(severity) + b'C' + _cstring(sqlstate) + b'M' + _cstring(message) + b'\x00'

    out = _message(b'E', payload)
    return out

# ################################################################################################################################

def _row_description(columns:'anylist') -> 'bytes':
    """ Builds a RowDescription message for the given (name, type) column pairs, all in text format.
    """
    payload = bytearray(struct.pack('!h', len(columns)))

    for name, type_ in columns:
        payload.extend(_cstring(name))

        # Table OID and column attribute number are not meaningful for canned results.
        payload.extend(struct.pack('!ih', 0, 0))

        # The type OID, type size, type modifier and the text format code.
        payload.extend(struct.pack('!ihih', _Type_OIDs[type_], _Type_Sizes[type_], -1, 0))

    out = _message(b'T', bytes(payload))
    return out

# ################################################################################################################################

def _data_row(row:'anylist', columns:'anylist', result_formats:'anylist') -> 'bytes':
    """ Builds a DataRow message, serializing every value in the format the client asked for -
    length-prefixed text by default or big-endian binary when the Bind message requested it.
    """
    payload = bytearray(struct.pack('!h', len(row)))

    for index, value in enumerate(row):

        # A None is sent as the wire-level NULL marker ..
        if value is None:
            payload.extend(struct.pack('!i', -1))
            continue

        # .. everything else honours the per-column result format.
        if result_formats:
            if len(result_formats) == 1:
                format_code = result_formats[0]
            else:
                format_code = result_formats[index]
        else:
            format_code = 0

        type_ = columns[index][1]

        if format_code == 1 and type_ == 'int':
            wire_value = struct.pack('!i', value)
        else:
            wire_value = str(value).encode('utf-8')

        payload.extend(struct.pack('!i', len(wire_value)))
        payload.extend(wire_value)

    out = _message(b'D', bytes(payload))
    return out

# ################################################################################################################################

def _command_complete(tag:'str') -> 'bytes':
    out = _message(b'C', _cstring(tag))
    return out

# ################################################################################################################################

def _ready_for_query() -> 'bytes':
    out = _message(b'Z', b'I')
    return out

# ################################################################################################################################

def _parse_startup_parameters(payload:'bytes') -> 'anydict':
    """ Parses the key/value pairs of a StartupMessage into a dict.
    """
    out = {}

    parts = payload.split(b'\x00')

    # The pairs come as alternating key and value entries, ending with an empty terminator.
    index = 0
    while index + 1 < len(parts):
        key = parts[index].decode('utf-8')
        if not key:
            break
        out[key] = parts[index + 1].decode('utf-8')
        index += 2

    return out

# ################################################################################################################################
# ################################################################################################################################

class _ConnectionHandler(socketserver.BaseRequestHandler):
    """ Handles one client connection - the TLS upgrade, the startup exchange, MD5 authentication
    and then both the simple and the extended query protocols.
    """

    def handle(self) -> 'None':

        server:'any_' = self.server
        sock = self.request

        try:
            sock = self._startup(server, sock)
            if sock:
                self._message_loop(server, sock)
        except (ConnectionError, ssl.SSLError, struct.error) as e:
            logger.info('[redshift_test_server] connection ended: %s', e)

# ################################################################################################################################

    def _startup(self, server:'any_', sock:'any_') -> 'any_':
        """ Performs the TLS upgrade, the startup message exchange and MD5 authentication.
        Returns the socket to keep using, or None if the connection was rejected.
        """
        header = _read_exact(sock, 8)
        if len(header) < 8:
            return None

        length, code = struct.unpack('!ii', header)

        # The TLS upgrade request comes before the startup message proper ..
        if code == _SSL_Request_Code:

            # .. accept it when this server profile has TLS material ..
            if server.tls_context:
                sock.sendall(b'S')
                sock = server.tls_context.wrap_socket(sock, server_side=True)

            # .. and refuse it otherwise, which ends the exchange on the client side.
            else:
                sock.sendall(b'N')

            header = _read_exact(sock, 8)
            if len(header) < 8:
                return None

            length, code = struct.unpack('!ii', header)

        # Now the startup message with the protocol version and the key/value parameters.
        payload = _read_exact(sock, length - 8)

        if code != _Protocol_Version:
            sock.sendall(_error_response('FATAL', '08P01', f'Unsupported protocol version: {code}'))
            return None

        startup_parameters = _parse_startup_parameters(payload)
        server.record({'type': 'startup', 'parameters': startup_parameters})

        # Ask for an MD5-hashed password with a random salt ..
        salt = CryptoManager.generate_hex_string()[:4].encode('ascii')
        sock.sendall(_message(b'R', struct.pack('!i', _Auth_MD5_Password) + salt))

        # .. read the client's PasswordMessage ..
        password_code, password_payload = self._read_message(sock)
        if password_code != b'p':
            return None

        received_digest = password_payload.rstrip(b'\x00')

        # .. and verify the digest against the configured credentials.
        user = startup_parameters['user'].encode('utf-8')
        password = server.password.encode('utf-8')

        inner_digest = md5(password + user).hexdigest().encode('ascii')
        expected_digest = b'md5' + md5(inner_digest + salt).hexdigest().encode('ascii')

        is_user_ok = startup_parameters['user'] == server.user
        is_digest_ok = received_digest == expected_digest

        if not is_user_ok:
            sock.sendall(_error_response(
                'FATAL', _SQL_State_Auth_Failed, f'password authentication failed for user "{startup_parameters["user"]}"'))
            return None

        if not is_digest_ok:
            sock.sendall(_error_response(
                'FATAL', _SQL_State_Auth_Failed, f'password authentication failed for user "{startup_parameters["user"]}"'))
            return None

        # Authentication went fine - complete the startup sequence. Note that no server_protocol_version
        # parameter status is sent, which pins the client to the base text protocol.
        sock.sendall(_message(b'R', struct.pack('!i', _Auth_OK)))

        sock.sendall(_message(b'S', _cstring('server_version') + _cstring('8.0.2')))
        sock.sendall(_message(b'S', _cstring('client_encoding') + _cstring('UTF8')))
        sock.sendall(_message(b'S', _cstring('standard_conforming_strings') + _cstring('on')))

        sock.sendall(_message(b'K', struct.pack('!ii', 1, 1)))
        sock.sendall(_ready_for_query())

        return sock

# ################################################################################################################################

    def _read_message(self, sock:'any_') -> 'any_':
        """ Reads one frontend message, returning its type byte and payload.
        """
        header = _read_exact(sock, 5)
        if len(header) < 5:
            return None, b''

        code = header[:1]
        length = struct.unpack('!i', header[1:])[0]

        payload = _read_exact(sock, length - 4)

        return code, payload

# ################################################################################################################################

    def _message_loop(self, server:'any_', sock:'any_') -> 'None':
        """ Serves the simple and the extended query protocols until the client terminates.
        """
        # Prepared statements and portals this connection knows about.
        statements = {}
        portals = {}

        # Once an error was reported, everything until the next Sync is ignored.
        skip_until_sync = False

        while True:
            code, payload = self._read_message(sock)

            # EOF or an explicit Terminate ends the connection.
            if code is None:
                break

            if code == b'X':
                break

            # Sync concludes an extended-protocol exchange.
            if code == b'S':
                skip_until_sync = False
                sock.sendall(_ready_for_query())
                continue

            # Flush is a no-op because every response is written immediately.
            if code == b'H':
                continue

            if skip_until_sync:
                continue

            # Parse registers a prepared statement under its name.
            if code == b'P':
                statement_name, sql, _ = payload.split(b'\x00', 2)
                statements[statement_name] = sql.decode('utf-8')

                server.record({'type': 'parse', 'sql': statements[statement_name]})
                sock.sendall(_message(b'1', b''))

            # Describe announces the shape of a statement's result.
            elif code == b'D':
                target_kind = payload[:1]
                target_name = payload[1:].split(b'\x00', 1)[0]

                if target_kind == b'S':
                    sql = statements[target_name]
                else:
                    sql = statements[portals[target_name]['statement']]

                spec = server.find_result(sql)

                if spec['is_error']:
                    sock.sendall(_error_response('ERROR', spec['sqlstate'], spec['message']))
                    skip_until_sync = True
                else:
                    # No parameters are ever described because the tests bind values client-side.
                    sock.sendall(_message(b't', struct.pack('!h', 0)))

                    if spec['columns']:
                        sock.sendall(_row_description(spec['columns']))
                    else:
                        sock.sendall(_message(b'n', b''))

            # Bind creates a portal for a prepared statement, carrying the parameter values
            # and the per-column result format codes the data rows must honour.
            elif code == b'B':
                portal_name, statement_name, rest = payload.split(b'\x00', 2)

                parameters, result_formats = self._parse_bind_parameters(rest)
                portals[portal_name] = {'statement': statement_name, 'result_formats': result_formats}

                server.record({'type': 'bind', 'sql': statements[statement_name], 'parameters': parameters})

                sock.sendall(_message(b'2', b''))

            # Execute answers from the canned-result table.
            elif code == b'E':
                portal_name = payload.split(b'\x00', 1)[0]
                portal = portals[portal_name]
                sql = statements[portal['statement']]

                spec = server.find_result(sql)

                if spec['is_error']:
                    sock.sendall(_error_response('ERROR', spec['sqlstate'], spec['message']))
                    skip_until_sync = True
                else:
                    self._send_result(sock, sql, spec, portal['result_formats'])

            # Close drops a statement or portal.
            elif code == b'C':
                sock.sendall(_message(b'3', b''))

            # The simple query message runs the whole pipeline at once.
            elif code == b'Q':
                sql = payload.split(b'\x00', 1)[0].decode('utf-8')
                server.record({'type': 'query', 'sql': sql})

                spec = server.find_result(sql)

                if spec['is_error']:
                    sock.sendall(_error_response('ERROR', spec['sqlstate'], spec['message']))
                else:
                    if spec['columns']:
                        sock.sendall(_row_description(spec['columns']))

                    # The simple query protocol always serves text-format rows.
                    self._send_result(sock, sql, spec, [])

                sock.sendall(_ready_for_query())

            # Anything else is not part of the protocol subset the tests exercise.
            else:
                sock.sendall(_error_response('ERROR', '08P01', f'Unsupported message code: {code!r}'))
                skip_until_sync = True

# ################################################################################################################################

    def _parse_bind_parameters(self, data:'bytes') -> 'any_':
        """ Extracts the text values of the parameters a Bind message carries,
        along with the result format codes its tail requests for the data rows.
        """
        parameters = []

        # First the parameter format codes, which the base text protocol keeps all-text anyway ..
        format_code_count = struct.unpack('!h', data[:2])[0]
        offset = 2 + format_code_count * 2

        # .. then the parameter values themselves ..
        parameter_count = struct.unpack('!h', data[offset:offset + 2])[0]
        offset += 2

        for _ in range(parameter_count):
            value_length = struct.unpack('!i', data[offset:offset + 4])[0]
            offset += 4

            if value_length == -1:
                parameters.append(None)
            else:
                value = data[offset:offset + value_length].decode('utf-8')
                offset += value_length
                parameters.append(value)

        # .. and finally the per-column result format codes.
        result_formats = []

        result_format_count = struct.unpack('!h', data[offset:offset + 2])[0]
        offset += 2

        for _ in range(result_format_count):
            format_code = struct.unpack('!h', data[offset:offset + 2])[0]
            offset += 2
            result_formats.append(format_code)

        return parameters, result_formats

# ################################################################################################################################

    def _send_result(self, sock:'any_', sql:'str', spec:'anydict', result_formats:'anylist') -> 'None':
        """ Sends the data rows and the command completion tag for one canned result.
        """
        for row in spec['rows']:
            sock.sendall(_data_row(row, spec['columns'], result_formats))

        # A result with columns completes as a SELECT, anything else echoes its own verb.
        if spec['columns']:
            row_count = len(spec['rows'])
            tag = f'SELECT {row_count}'
        else:
            tag = sql.strip().split(' ')[0].upper()

        sock.sendall(_command_complete(tag))

# ################################################################################################################################
# ################################################################################################################################

class _Server(socketserver.ThreadingTCPServer):
    """ Holds the recorded requests, the credentials and the regex-keyed canned results.
    """
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, *args:'any_', **kwargs:'any_') -> 'None':
        super().__init__(*args, **kwargs)

        self.recorded_requests:'anylist' = []

        # Credentials every startup exchange is checked against.
        self.user = 'test_user'
        self.password = 'test_password'

        # An ssl.SSLContext when this profile serves TLS, None in the plain profile.
        self.tls_context:'any_' = None

        # The regex-keyed table of canned results, searched in order, first match wins.
        self.results:'anylist' = []

        self.add_default_results()

# ################################################################################################################################

    def add_default_results(self) -> 'None':
        """ Adds the on-connect queries sqlalchemy-redshift issues plus a ping query.
        """
        self.add_result(
            r'select pg_catalog\.version\(\)|select version\(\)',
            columns=[('version', 'text')],
            rows=[['PostgreSQL 8.0.2 on i686-pc-linux-gnu, compiled by GCC gcc (GCC) 3.4.2, Redshift 1.0.77467']],
        )

        self.add_result(r'select current_schema\(\)', columns=[('current_schema', 'text')], rows=[['public']])
        self.add_result(r'show standard_conforming_strings', columns=[('standard_conforming_strings', 'text')], rows=[['on']])

        self.add_result(
            r'show transaction isolation level',
            columns=[('transaction_isolation', 'text')],
            rows=[['read committed']],
        )

        self.add_result(r'^\s*select\s+1\s*;?\s*$', columns=[('?column?', 'int')], rows=[[1]])

        self.add_result(r'^\s*(begin|commit|rollback|set)\b', columns=[], rows=[])

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

    def add_error(self, pattern:'str', message:'str', sqlstate:'str'=_No_Match_SQL_State) -> 'None':
        """ Registers an error response for every SQL statement matching the pattern.
        """
        spec = {
            'is_error': True,
            'message': message,
            'sqlstate': sqlstate,
        }

        self.results.insert(0, (re.compile(pattern, re.IGNORECASE), spec))

# ################################################################################################################################

    def find_result(self, sql:'str') -> 'anydict':
        """ Returns the first canned result whose pattern matches the SQL.
        """
        for pattern, spec in self.results:
            if pattern.search(sql):
                out = spec
                break
        else:
            out = {
                'is_error': True,
                'message': f'No canned result matches SQL: {sql}',
                'sqlstate': _No_Match_SQL_State,
            }

        return out

# ################################################################################################################################

    def record(self, item:'anydict') -> 'None':
        self.recorded_requests.append(item)

# ################################################################################################################################
# ################################################################################################################################

class RedshiftTestServer:
    """ A live server speaking the PostgreSQL frontend/backend wire protocol v3 for client tests.
    It records every request and answers queries from a regex-keyed table of canned results,
    with a TLS upgrade backed by a locally generated test CA or over a plain TCP socket.
    """
    def __init__(self, tls:'bool'=True) -> 'None':
        self.host = '127.0.0.1'
        self.port = 0
        self.tls = tls

        self.tls_material:'TLSMaterial | None' = None
        self._server:'any_' = None
        self._thread:'any_' = None

# ################################################################################################################################

    def start(self) -> 'None':
        """ Binds to an ephemeral port and serves in a background thread,
        preparing the TLS material the per-connection upgrade uses when configured to.
        """
        self._server = _Server((self.host, 0), _ConnectionHandler)
        self.port = self._server.server_address[1]

        if self.tls:
            self.tls_material = build_tls_material(self.host)

            tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            tls_context.load_cert_chain(self.tls_material.server_certificate_path, self.tls_material.server_key_path)

            self._server.tls_context = tls_context

        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

        logger.info('[RedshiftTestServer] started on %s:%s (tls=%s)', self.host, self.port, self.tls)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the server and removes any temporary TLS material.
        """
        self._server.shutdown()
        self._server.server_close()

        if self.tls_material:
            shutil.rmtree(self.tls_material.directory, ignore_errors=True)

        logger.info('[RedshiftTestServer] stopped on %s:%s', self.host, self.port)

# ################################################################################################################################

    def configure(self, user:'str'='', password:'str'='') -> 'None':
        """ Sets the credentials startup exchanges are checked against.
        """
        if user:
            self._server.user = user

        if password:
            self._server.password = password

# ################################################################################################################################

    def add_result(self, pattern:'str', columns:'anylist', rows:'anylist') -> 'None':
        self._server.add_result(pattern, columns, rows)

# ################################################################################################################################

    def add_error(self, pattern:'str', message:'str', sqlstate:'str'=_No_Match_SQL_State) -> 'None':
        self._server.add_error(pattern, message, sqlstate)

# ################################################################################################################################

    @property
    def user(self) -> 'str':
        out = self._server.user
        return out

# ################################################################################################################################

    @property
    def password(self) -> 'str':
        out = self._server.password
        return out

# ################################################################################################################################

    @property
    def recorded_requests(self) -> 'anylist':
        out = self._server.recorded_requests
        return out

# ################################################################################################################################

    def clear_requests(self) -> 'None':
        self._server.recorded_requests.clear()

# ################################################################################################################################
# ################################################################################################################################
