# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What an export program reaches for when it is exercised offline - the fake FHIR server with its token endpoint,
# a stand-in for the server's deliver service recording the files it was handed, a job spec pointing at both and
# the environment that points the audit log at a throwaway database.

# stdlib
import os
import threading
from contextlib import contextmanager
from http.client import OK
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from json import dumps, loads

# SQLAlchemy
from sqlalchemy import select

# Zato
from hl7_client.ports import find_free_port
from live_sql.env import database_env
from zato.common.api import HL7
from zato.common.audit_log.api import event_attr_table, event_table, get_audit_engine
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.const import ServiceConst
from zato.common.crypto.api import CryptoManager
from zato.common.hl7.fhir.bulk_export.spec import JobSpec
from zato.common.test.fhir import FHIRTestServer
from zato.common.test.fhir.common import auth_type_basic, auth_type_oauth

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import any_, anydict, anylist, strdict, stranydict

    envgen = Iterator[None]
    anydict = anydict
    anylist = anylist
    strdict = strdict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

_bulk = HL7.BulkExport

# The server the audit events are written under
Server_Name = 'test-fhir-bulk-export-server'

# The name and id the connection under test goes by
Connection_Name = 'test.fhir.bulk.export'
Connection_ID = 11

# The credentials the fake FHIR server knows
Client_ID = 'zato-test-bulk-client'
Client_Secret = 'test.bulk.' + CryptoManager.generate_hex_string()

# What every stand-in binds to
Host = '127.0.0.1'

# The resources the fake server holds - two patients, one with an observation, one without
Patient_ID_1 = 'bulk-p1'
Patient_ID_2 = 'bulk-p2'
Observation_ID = 'bulk-o1'
Group_ID = 'bulk-group-1'

# How many files a system-level export of the resources yields - one per resource type
File_Count = 2

Resources = [
    {'resourceType': 'Patient', 'id': Patient_ID_1, 'name': [{'family': 'Smith'}]},
    {'resourceType': 'Patient', 'id': Patient_ID_2, 'name': [{'family': 'Jones'}]},
    {'resourceType': 'Observation', 'id': Observation_ID, 'subject': {'reference': f'Patient/{Patient_ID_1}'}},
]

# How the deliver stand-in is reached
Invoke_Username = 'pubapi'
Invoke_Password = 'test.invoke.' + CryptoManager.generate_hex_string()

# The prefix all the audit log database environment variables share
_env_prefix = 'Zato_Audit_Log_DB_'

_deliver_path = ServiceConst.API_Invoke_Url_Path.format(_bulk.Deliver_Service)

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def bulk_audit_env(tmp_path:'any_') -> 'envgen':
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

def get_events() -> 'anylist':
    """ Everything the audit log holds, oldest first.
    """
    engine = get_audit_engine()

    query = select(event_table)
    query = query.order_by(event_table.c.id)

    with engine.connect() as connection:
        out = [dict(row._mapping) for row in connection.execute(query)]

    return out

# ################################################################################################################################

def get_attrs(event_id:'int') -> 'strdict':
    """ The searchable attributes of one event, by name.
    """
    engine = get_audit_engine()

    query = select(event_attr_table.c.name, event_attr_table.c.value)
    query = query.where(event_attr_table.c.event_id == event_id)

    with engine.connect() as connection:
        out = {row.name: row.value for row in connection.execute(query)}

    return out

# ################################################################################################################################
# ################################################################################################################################

class _DeliverHandler(BaseHTTPRequestHandler):
    """ Answers each delivery with what the stand-in was told to answer, recording what was handed over.
    """
    server:'DeliverStandIn'

    def do_POST(self) -> 'None':

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)

        request = loads(body)
        request['path'] = self.path
        request['authorization'] = self.headers['Authorization']

        with self.server.lock:
            self.server.requests.append(request)
            response = self.server.response

        data = dumps(response).encode('utf8')

        self.send_response(OK)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        _ = self.wfile.write(data)

    def log_message(self, format:'str', *args:'any_') -> 'None':
        pass

# ################################################################################################################################

class DeliverStandIn(ThreadingHTTPServer):
    """ Stands in for the server's deliver service - what the program hands each file to.
    """
    def __init__(self) -> 'None':
        port = find_free_port()
        super().__init__((Host, port), _DeliverHandler)

        self.lock = threading.Lock()
        self.requests:'anylist' = []
        self.response:'stranydict' = {'is_ok': True, 'error': ''}
        self.thread = threading.Thread(target=self.serve_forever, daemon=True)

    @property
    def address(self) -> 'str':
        out = f'http://{Host}:{self.server_address[1]}'
        return out

    @property
    def files(self) -> 'anylist':
        """ The files handed over, in the order they arrived.
        """
        out = []
        for request in self.requests:
            out.append(request['file'])
        return out

    def refuse(self, error:'str') -> 'None':
        """ Every delivery from now on is answered as one a destination refused.
        """
        with self.lock:
            self.response = {'is_ok': False, 'error': error}

    def accept(self) -> 'None':
        with self.lock:
            self.response = {'is_ok': True, 'error': ''}

    def __enter__(self) -> 'DeliverStandIn':
        self.thread.start()
        return self

    def __exit__(self, *args:'any_') -> 'None':
        self.shutdown()
        self.server_close()

# ################################################################################################################################
# ################################################################################################################################

def new_fhir_server(auth_type:'str'=auth_type_oauth) -> 'FHIRTestServer':
    """ A fake FHIR server holding the test resources, started and ready for an export.
    """
    out = FHIRTestServer(Client_ID, Client_Secret, auth_type)
    out.start()

    for resource in Resources:
        _ = out.import_resource(resource)

    return out

# ################################################################################################################################

def new_spec(fhir_server:'FHIRTestServer', deliver:'DeliverStandIn', download_dir:'str') -> 'JobSpec':
    """ The spec of a system-level export of everything the fake server holds, delivered through the stand-in.
    """
    out = JobSpec()

    out.job_id = CryptoManager.generate_hex_string()
    out.conn_id = Connection_ID
    out.conn_name = Connection_Name
    out.server_name = Server_Name

    out.address = fhir_server.address
    out.auth_type = fhir_server.auth_type

    if fhir_server.auth_type == auth_type_basic:
        auth_header = fhir_server._build_auth_header()
        if auth_header:
            out.basic_auth_header = auth_header

    elif fhir_server.auth_type == auth_type_oauth:
        out.bearer = {
            'sec_def_name': 'test.bulk.bearer',
            'username': Client_ID,
            'password': Client_Secret,
            'scopes': '',
            'grant_type': 'client_credentials',
            'extra_fields': {},
            'auth_server_url': fhir_server.token_endpoint,
            'client_id_field': 'client_id',
            'client_secret_field': 'client_secret',
        }
        out.bearer_data_format = 'form'

    out.level = _bulk.Level.System
    out.download_dir = download_dir

    out.invoke_url = deliver.address
    out.invoke_username = Invoke_Username
    out.invoke_password = Invoke_Password

    return out

# ################################################################################################################################
# ################################################################################################################################
