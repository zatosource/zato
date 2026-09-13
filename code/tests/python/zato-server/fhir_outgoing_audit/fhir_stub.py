# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What an outgoing FHIR call reaches for when it is exercised offline - a stand-in FHIR server on a local port
# answering whatever a test tells it to, a client pointing at it and the environment that points the audit log
# at a throwaway database.

# stdlib
import os
import threading
import time
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Zato
from hl7_client.ports import find_free_port
from live_sql.env import database_env
from zato.common.api import HL7
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.json_internal import dumps
from zato.common.typing_ import cast_
from zato.server.generic.api.outconn_hl7_fhir import _HL7FHIRConnection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import any_, anylist, stranydict

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

# The server the audit events are written under
Server_Name = 'test-fhir-audit-server'

# The name and id the connection under test goes by
Connection_Name = 'test.fhir.audit'
Connection_ID = 7

# What every stand-in binds to
Host = '127.0.0.1'

# How long the client waits for a response before it gives up, in seconds
Client_Timeout = 0.5

# How long a stalling stand-in sits on a request - past the client's patience
Stall_Seconds = 2

# The content type a FHIR server answers with
_content_type = 'application/fhir+json'

# The prefix all the audit log database environment variables share
_env_prefix = 'Zato_Audit_Log_DB_'

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def fhir_audit_env(tmp_path:'any_') -> 'envgen':
    """ Points the audit log at a throwaway SQLite database for the duration of a test.
    """
    db_path = os.path.join(str(tmp_path), 'audit.db')

    details = {
        'type': AuditLogCtx.Type_SQLite,
        'name': db_path,
    }

    with database_env(_env_prefix, details):
        yield

# ################################################################################################################################
# ################################################################################################################################

def operation_outcome(code:'str', diagnostics:'str') -> 'str':
    """ The body of an OperationOutcome resource with one issue of the given code.
    """
    out = dumps({
        'resourceType': 'OperationOutcome',
        'issue': [{'severity': 'error', 'code': code, 'diagnostics': diagnostics}],
    })
    return out

# ################################################################################################################################
# ################################################################################################################################

class _FHIRHandler(BaseHTTPRequestHandler):
    """ Answers every request with what the stand-in was told to answer, recording what was asked.
    """

    def _answer(self) -> 'None':
        server = cast_('any_', self.server)
        stand_in = server.stand_in

        content_length = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(content_length).decode('utf-8')
        stand_in.requests.append((self.command, self.path, body))

        # A stalling stand-in outlasts the client's patience, so the client sees a timeout
        if stand_in.is_stalling:
            time.sleep(Stall_Seconds)

        response_body = stand_in.body.encode('utf-8')

        self.send_response(stand_in.status)
        self.send_header('Content-Type', _content_type)
        self.send_header('Content-Length', str(len(response_body)))
        self.end_headers()
        _ = self.wfile.write(response_body)

    do_GET = _answer
    do_POST = _answer
    do_PUT = _answer
    do_DELETE = _answer

    def log_message(self, message_format:'str', *args:'object') -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

class FHIRStandIn:
    """ A FHIR server on a local port that answers with the one status and body it is given.
    """

    def __init__(self, status:'int', body:'str', *, is_stalling:'bool'=False) -> 'None':
        self.status = status
        self.body = body
        self.is_stalling = is_stalling
        self.port = find_free_port()
        self.requests:'anylist' = []

        self._server:'any_' = None
        self._thread:'threading.Thread | None' = None

# ################################################################################################################################

    @property
    def address(self) -> 'str':
        out = f'http://{Host}:{self.port}'
        return out

# ################################################################################################################################

    def __enter__(self) -> 'FHIRStandIn':
        server = cast_('any_', ThreadingHTTPServer((Host, self.port), _FHIRHandler))

        # The handler reads its stand-in off the server it runs on
        server.stand_in = self
        self._server = server

        self._thread = threading.Thread(target=server.serve_forever, daemon=True)
        self._thread.start()

        return self

# ################################################################################################################################

    def __exit__(self, *args:'any_') -> 'None':
        self._server.shutdown()
        self._server.server_close()
        self._server = None

# ################################################################################################################################
# ################################################################################################################################

class _ServerStub:
    """ Stands in for the Zato server a client writes its audit events under - the name is all the client reads off it.
    """

    def __init__(self) -> 'None':
        self.name = Server_Name

# ################################################################################################################################
# ################################################################################################################################

def new_fhir_client(address:'str', *, is_audit_log_active:'bool'=True) -> '_HL7FHIRConnection':
    """ The FHIR connection under test, pointing at the given address - real in every respect.
    """
    config:'stranydict' = {
        'id': Connection_ID,
        'name': Connection_Name,
        'address': address,
        'is_audit_log_active': is_audit_log_active,
        'security_id': 0,
        'auth_type': HL7.Const.FHIR_Auth_Type.No_Auth.id,
        'server': _ServerStub(),
    }

    out = _HL7FHIRConnection(config)

    # A client that waits forever would turn a stalling stand-in into a hanging test
    out.requests_config = {'timeout': Client_Timeout}

    return out

# ################################################################################################################################

def unreached_address() -> 'str':
    """ An address nothing listens on, so a connection to it is refused.
    """
    out = f'http://{Host}:{find_free_port()}'
    return out

# ################################################################################################################################
# ################################################################################################################################
