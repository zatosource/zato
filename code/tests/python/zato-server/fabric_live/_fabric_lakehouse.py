# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import ACCEPTED, BAD_REQUEST, NOT_FOUND, OK

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

class LakehouseState:
    """ The lakehouse-level state of the simulated tenant - tables, load operations and Spark sessions.
    """

    def __init__(self) -> 'None':

        # All the tables, keyed by (workspace ID, lakehouse ID)
        self.tables:'anydict' = {}

        # Load operations, keyed by operation ID
        self.operations:'anydict' = {}

        # Spark sessions, keyed by session ID
        self.sessions:'anydict' = {}

        # Spark statements, keyed by (session ID, statement ID)
        self.statements:'anydict' = {}

        # How many Spark sessions were ever created - what session reuse tests read
        self.session_count = 0

        # How many objects were created so far, used to build new IDs
        self.object_counter = 0

# ################################################################################################################################

    def next_id(self, prefix:'str') -> 'str':
        """ Builds a new object ID with the given prefix.
        """
        self.object_counter += 1

        out = f'{prefix}-new-{self.object_counter:03}'
        return out

# ################################################################################################################################
# ################################################################################################################################

# The current state - replaced with a fresh one each time the simulated tenant starts.
state = LakehouseState()

# ################################################################################################################################
# ################################################################################################################################

def reset_lakehouse_state() -> 'None':
    """ Starts with a fresh lakehouse state, seeded with the table the tenant begins with.
    """
    global state

    state = LakehouseState()
    state.tables[('workspace-sales-analytics', 'item-sales-lakehouse')] = {
        'regions': {
            'type': 'Managed',
            'name': 'regions',
            'location': 'Tables/regions',
            'format': 'delta',
        },
    }

# ################################################################################################################################
# ################################################################################################################################

def _build_statement_output(statement_id:'int') -> 'anydict':
    """ Returns the output every completed statement carries - a schema and the rows that match it.
    """
    return {
        'status': 'ok',
        'execution_count': statement_id,
        'data': {
            'application/json': {
                'schema': {'fields': [{'name': 'region'}, {'name': 'total'}]},
                'data': [['EMEA', 1250.5], ['APAC', 875.25]],
            },
        },
    }

# ################################################################################################################################

def _handle_tables_request(handler:'any_', method:'str', workspace_id:'str', lakehouse_id:'str', segments:'strlist') -> 'None':
    """ Lakehouse tables - listing them and loading files into them.
    Segments are the path elements after /tables, e.g. ['daily_sales', 'load'].
    """
    table_key = (workspace_id, lakehouse_id)
    lakehouse_tables = state.tables.setdefault(table_key, {})

    segment_count = len(segments)

    # GET /tables - list all the tables of a lakehouse
    if segment_count == 0:
        if method == 'GET':
            tables = list(lakehouse_tables.values())
            handler._send_json(OK, {'data': tables})
            return

    # POST /tables/{table_name}/load - start a load operation, which is long-running,
    # so the response is an empty 202 Accepted with a Location header pointing to the operation.
    if segment_count == 2:
        if segments[1] == 'load':
            if method == 'POST':
                request_data = handler._read_json_body()

                table_name = segments[0]
                lakehouse_tables[table_name] = {
                    'type': 'Managed',
                    'name': table_name,
                    'location': f'Tables/{table_name}',
                    'format': 'delta',
                    'loadMode': request_data['mode'],
                    'loadPath': request_data['relativePath'],
                }

                operation_id = state.next_id('operation')
                state.operations[operation_id] = {'status': 'Running', 'poll_count': 0}

                location = f'/workspaces/{workspace_id}/lakehouses/{lakehouse_id}/operations/{operation_id}'
                handler._send_empty(ACCEPTED, location=location)
                return

    # Nothing above handled the request, so the path or method is not supported.
    handler._send_json(BAD_REQUEST,
        {'error': {'code': 'InvalidRequest', 'message': f'Unsupported request: {method} {handler.path}'}})

# ################################################################################################################################

def _handle_operations_request(handler:'any_', method:'str', segments:'strlist') -> 'None':
    """ Long-running operations - a load stays Running for its first status check and succeeds afterwards.
    Segments are the path elements after /operations, e.g. ['operation-new-001'].
    """
    segment_count = len(segments)

    if segment_count == 1:
        if method == 'GET':
            operation_id = segments[0]

            if operation_id not in state.operations:
                handler._send_json(NOT_FOUND,
                    {'error': {'code': 'OperationNotFound', 'message': f'Operation {operation_id} not found'}})
                return

            operation = state.operations[operation_id]

            poll_count = operation['poll_count'] + 1
            operation['poll_count'] = poll_count

            if poll_count > 1:
                operation['status'] = 'Succeeded'

            status = operation['status']
            handler._send_json(OK, {'status': status})
            return

    # Nothing above handled the request, so the path or method is not supported.
    handler._send_json(BAD_REQUEST,
        {'error': {'code': 'InvalidRequest', 'message': f'Unsupported request: {method} {handler.path}'}})

# ################################################################################################################################

def _handle_statements_request(handler:'any_', method:'str', session_id:'str', segments:'strlist') -> 'None':
    """ Statements of a Spark session - every statement completes immediately with the same fixed output.
    Segments are the path elements after /statements, e.g. ['0'].
    """
    segment_count = len(segments)

    # POST /statements - submit a new statement
    if segment_count == 0:
        if method == 'POST':
            request_data = handler._read_json_body()

            session = state.sessions[session_id]
            statement_id = session['statement_count']
            session['statement_count'] += 1

            statement = {
                'id': statement_id,
                'code': request_data['code'],
                'kind': request_data['kind'],
                'state': 'available',
                'output': _build_statement_output(statement_id),
            }
            state.statements[(session_id, statement_id)] = statement

            handler._send_json(OK, statement)
            return

    # GET /statements/{statement_id} - a single statement
    if segment_count == 1:
        if method == 'GET':
            statement_id = int(segments[0])
            statement_key = (session_id, statement_id)

            if statement_key not in state.statements:
                handler._send_json(NOT_FOUND,
                    {'error': {'code': 'StatementNotFound', 'message': f'Statement {statement_id} not found'}})
                return

            handler._send_json(OK, state.statements[statement_key])
            return

    # Nothing above handled the request, so the path or method is not supported.
    handler._send_json(BAD_REQUEST,
        {'error': {'code': 'InvalidRequest', 'message': f'Unsupported request: {method} {handler.path}'}})

# ################################################################################################################################

def _handle_sessions_request(handler:'any_', method:'str', segments:'strlist') -> 'None':
    """ Spark sessions of a lakehouse - a new session is ready to accept statements right away.
    Segments are the path elements after /sessions, e.g. ['session-new-001', 'statements'].
    """
    segment_count = len(segments)

    # POST /sessions - create a new session
    if segment_count == 0:
        if method == 'POST':
            session_id = state.next_id('session')
            session = {
                'id': session_id,
                'state': 'idle',
                'statement_count': 0,
            }

            state.sessions[session_id] = session
            state.session_count += 1

            handler._send_json(ACCEPTED, session)
            return

    # Anything below this point points to a specific session
    if segment_count >= 1:
        session_id = segments[0]

        if session_id not in state.sessions:
            handler._send_json(NOT_FOUND,
                {'error': {'code': 'SessionNotFound', 'message': f'Session {session_id} not found'}})
            return

        if segment_count == 1:

            # GET /sessions/{session_id} - a single session
            if method == 'GET':
                handler._send_json(OK, state.sessions[session_id])
                return

            # DELETE /sessions/{session_id} - close a session
            if method == 'DELETE':
                del state.sessions[session_id]
                handler._send_empty(OK)
                return

        # The session's statements live under /sessions/{session_id}/statements
        if segment_count >= 2:
            if segments[1] == 'statements':
                _handle_statements_request(handler, method, session_id, segments[2:])
                return

    # Nothing above handled the request, so the path or method is not supported.
    handler._send_json(BAD_REQUEST,
        {'error': {'code': 'InvalidRequest', 'message': f'Unsupported request: {method} {handler.path}'}})

# ################################################################################################################################

def handle_lakehouse_request(handler:'any_', method:'str', workspace_id:'str', segments:'strlist') -> 'None':
    """ Everything under /workspaces/{workspace_id}/lakehouses - tables, load operations and Spark sessions.
    Segments are the path elements after /lakehouses, e.g. ['item-sales-lakehouse', 'tables'].
    """
    segment_count = len(segments)

    if segment_count < 2:
        handler._send_json(BAD_REQUEST,
            {'error': {'code': 'InvalidRequest', 'message': f'Unsupported request: {method} {handler.path}'}})
        return

    lakehouse_id = segments[0]

    # The lakehouse's tables live under /lakehouses/{lakehouse_id}/tables
    if segments[1] == 'tables':
        _handle_tables_request(handler, method, workspace_id, lakehouse_id, segments[2:])
        return

    # Its load operations live under /lakehouses/{lakehouse_id}/operations
    if segments[1] == 'operations':
        _handle_operations_request(handler, method, segments[2:])
        return

    # Its Spark sessions live under /lakehouses/{lakehouse_id}/livyapi/versions/{version}/sessions
    if segments[1] == 'livyapi':
        if segment_count >= 4:
            if segments[3] == 'sessions':
                _handle_sessions_request(handler, method, segments[4:])
                return

    # Nothing above handled the request, so the path or method is not supported.
    handler._send_json(BAD_REQUEST,
        {'error': {'code': 'InvalidRequest', 'message': f'Unsupported request: {method} {handler.path}'}})

# ################################################################################################################################
# ################################################################################################################################
