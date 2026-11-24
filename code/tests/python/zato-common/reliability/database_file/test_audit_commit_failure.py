# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The commit of the audit event of the response of an audited REST channel fails after its service completed,
# with every sync of the SQLite files of the Zato database failing under a preloaded fault library. The client
# receives the response of the invocation, the side effects of the service are committed exactly once,
# and the server logs the audit event that could not be written.

# stdlib
import json
import os
import shutil
from http.client import INTERNAL_SERVER_ERROR, OK

# pytest
import pytest

# Zato
from environment import DatabaseFileEnvironment, HTTPTextResult, wait_until
from tools import build_fsfault
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
from zato.common.test.sql_conformance.disk import get_disk_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The directory of the tests
    Dir_Name = 'database-file-audit-commit'

    # The name of the server
    Server_Name = 'database-file-audit'

    # The control file of the fault library, in the directory of the tests
    Control_File_Name = 'fsfault-control'

    # The variables of the fault library
    Env_Preload = 'LD_PRELOAD'
    Env_Control = 'ZATO_FSFAULT_CONTROL'

    # The channels whose services make the commits fail, and the audited channel whose service does not
    OK_Channel_Name    = 'test.reliability.database-file.audit-failure.ok'
    Error_Channel_Name = 'test.reliability.database-file.audit-failure.error'
    Echo_Channel_Name  = 'test.reliability.database-file.audited'

    # The paths of the channels whose services make the commits fail
    OK_Path    = '/test/reliability/database-file/audit-failure/ok'
    Error_Path = '/test/reliability/database-file/audit-failure/error'

    # The topic that the services publish to
    Topic_Name = 'reliability.database-file.audit-failure'

    # The result that the service of a successful invocation returns, and the result of an error response
    Result_Published = 'published'
    Result_Error     = 'Error'

    # The message that the server logs when the audit event of a response cannot be written
    Log_Text_Prefix = 'Audit event of the response could not be written, cid:`'

    # How long the log of the server may take to record the event, in seconds
    Log_Timeout = 10

# ################################################################################################################################
# ################################################################################################################################

def _get_server_env(control_path:'str') -> 'strstrdict':
    """ Returns the variables under which every process of the server preloads the fault library.
    """
    fsfault_path = build_fsfault()

    if current_preload := os.environ.get(ModuleCtx.Env_Preload, ''):
        preload = f'{fsfault_path} {current_preload}'
    else:
        preload = fsfault_path

    out = {
        ModuleCtx.Env_Preload: preload,
        ModuleCtx.Env_Control: control_path,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def environment() -> 'any_':
    """ A running server on SQLite that preloads the fault library, with no fault configured.
    """
    base_dir = get_disk_dir(ModuleCtx.Dir_Name)
    shutil.rmtree(base_dir)
    os.makedirs(base_dir)

    control_path = os.path.join(base_dir, ModuleCtx.Control_File_Name)

    with open(control_path, 'w'):
        pass

    server_env = _get_server_env(control_path)

    out = DatabaseFileEnvironment(ModuleCtx.Server_Name, base_dir, extra_server_env=server_env)

    try:
        out.start()
        yield out
    finally:
        out.stop()
        shutil.rmtree(base_dir)

# ################################################################################################################################
# ################################################################################################################################

def _call_with_fault(environment:'DatabaseFileEnvironment', path:'str') -> 'HTTPTextResult':
    """ Invokes a channel whose service makes the commits fail, and clears the fault once the response arrives.
    """
    try:
        out = environment.call_channel(path)
    finally:
        environment.disarm_fault()

    return out

# ################################################################################################################################

def _parse_body(result:'HTTPTextResult') -> 'anydict':
    """ Returns the JSON object of the body of a response, failing the test if the body is not JSON.
    """
    try:
        out = json.loads(result.text)
    except json.JSONDecodeError:
        pytest.fail(f'The body of the response is not JSON -> {result}')

    return out

# ################################################################################################################################

def _get_channel_events(environment:'DatabaseFileEnvironment', cid:'str', channel_name:'str') -> 'anylist':
    """ Returns the audit events that one REST channel recorded for the correlation ID of one invocation, oldest first.
    The audit events of its service have the name of the channel too, under a source of their own.
    """
    out:'anylist' = []

    for event in environment.get_audit_events(cid):
        if event['source'] == AuditSource.REST_Channel:
            if event['object_name'] == channel_name:
                out.append(event)

    return out

# ################################################################################################################################

def _get_event_types(events:'anylist') -> 'strlist':
    """ Returns the types of audit events, in their order.
    """
    out:'strlist' = []

    for event in events:
        out.append(event['event_type'])

    return out

# ################################################################################################################################

def _wait_for_log_count(environment:'DatabaseFileEnvironment', cid:'str') -> 'int':
    """ Waits until the log of the server records the audit event that could not be written for a correlation ID
    and returns how many times it does.
    """
    log_text = f'{ModuleCtx.Log_Text_Prefix}{cid}`'

    def is_logged() -> 'bool':
        count = environment.count_log_lines(log_text)
        out = count > 0
        return out

    wait_until(is_logged, ModuleCtx.Log_Timeout, f'the log of the audit event of {cid}')

    out = environment.count_log_lines(log_text)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_response_audit_failure_returns_service_response(environment:'DatabaseFileEnvironment') -> 'None':
    """ A failed commit of the audit event of a successful response leaves the response unchanged, the message
    that the service published is stored once, and the server logs the event that could not be written.
    """
    result = _call_with_fault(environment, ModuleCtx.OK_Path)

    # The client receives the response of the service ..
    assert result.status_code == OK, result

    body = _parse_body(result)
    assert body['result'] == ModuleCtx.Result_Published, body

    cid = body['cid']

    # .. the message of the service is stored once ..
    message_count = environment.count_topic_messages(ModuleCtx.Topic_Name, cid)
    assert message_count == 1, message_count

    # .. the request is in the audit log and the response is not ..
    events = _get_channel_events(environment, cid, ModuleCtx.OK_Channel_Name)
    event_types = _get_event_types(events)

    assert event_types == [AuditEvent.Request_Received], event_types

    # .. and the server logs the event that could not be written.
    log_count = _wait_for_log_count(environment, cid)
    assert log_count == 1, log_count

# ################################################################################################################################

def test_error_audit_failure_returns_error_response(environment:'DatabaseFileEnvironment') -> 'None':
    """ A failed commit of the audit event of an error response leaves the error response of the dispatcher unchanged,
    the message that the service published is stored once, and the server logs the event that could not be written.
    """
    result = _call_with_fault(environment, ModuleCtx.Error_Path)

    # The client receives the error response of the dispatcher, with the correlation ID of the invocation ..
    assert result.status_code == INTERNAL_SERVER_ERROR, result

    body = _parse_body(result)
    assert body['result'] == ModuleCtx.Result_Error, body

    cid = body['cid']

    # .. the message of the service is stored once ..
    message_count = environment.count_topic_messages(ModuleCtx.Topic_Name, cid)
    assert message_count == 1, message_count

    # .. the request is in the audit log and the response is not ..
    events = _get_channel_events(environment, cid, ModuleCtx.Error_Channel_Name)
    event_types = _get_event_types(events)

    assert event_types == [AuditEvent.Request_Received], event_types

    # .. and the server logs the event that could not be written.
    log_count = _wait_for_log_count(environment, cid)
    assert log_count == 1, log_count

# ################################################################################################################################

def test_response_audit_written_without_fault(environment:'DatabaseFileEnvironment') -> 'None':
    """ Without the fault, an audited channel records the request and the successful response of an invocation.
    """
    result = environment.call_audited()
    assert result.status_code == OK, result

    cid = result.body['cid']

    events = _get_channel_events(environment, cid, ModuleCtx.Echo_Channel_Name)
    event_types = _get_event_types(events)

    assert event_types == [AuditEvent.Request_Received, AuditEvent.Response_Sent], event_types

    response_event = events[1]
    assert response_event['outcome'] == AuditOutcome.OK, response_event

# ################################################################################################################################
# ################################################################################################################################
