# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from http.client import OK, TOO_MANY_REQUESTS, UNAUTHORIZED
from json import dumps

# requests
import requests

# Zato
from zato.common.audit_log.common import AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.export.api import ModuleCtx as APICtx
from zato.common.audit_log.export.config import ModuleCtx as ExportCtx
from zato.common.audit_log.export.data import ModuleCtx as DataCtx
from zato.common.audit_log.export.mapping import ModuleCtx as MappingCtx
from zato.common.model.security import BearerRefusalReason
from zato.common.rate_limiting.headers import Header_Retry_After
from zato.common.util.mcp_oauth import Server_Address_Env_Key

# Zato - test helpers
import keycloak_oauth

# Test support
from live_otel.containers import has_record, read_records, start_container, stop_container, wait_for_record

# local
from _common import bearer_caller, build_export_environment, count_lines, last_event_id, wait_for_event_of_type, \
    wait_for_line, wait_for_tools, AuditExportEnvironment, Exported_Sources, ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

# The product the people sign in through - which one does not matter here
_client = keycloak_oauth.Client_VSCode

# The arguments the echo tool is called with
_echo_arguments = {'invoice_id': 'INV-2026-0042'}

# The columns of a row every record carries when they are set
_compared_columns = ('cid', 'cid_sequence', 'source', 'event_type', 'object_name', 'msg_id', 'correl_id', 'ext_client_id',
    'pub_time_iso', 'endpoint', 'sub_key', 'size', 'priority', 'outcome', 'application_outcome', 'classification', 'status',
    'duration_ms')

# What a log line of the export starts with, with the address of the collector following
_paused_text   = 'Audit export to '
_paused_marker = ' paused - '
_resumed_marker = ' resumed'
_full_text = 'Audit export queue full at '

# ################################################################################################################################
# ################################################################################################################################

def _column(name:'str') -> 'str':
    out = f'{MappingCtx.Prefix}.{name}'
    return out

def _attr(name:'str') -> 'str':
    out = f'{MappingCtx.Attr_Prefix}.{name}'
    return out

def _data(name:'str') -> 'str':
    out = f'{DataCtx.Data_Prefix}.{name}'
    return out

def _payload(name:'str') -> 'str':
    out = f'{DataCtx.Payload_Prefix}.{name}'
    return out

# ################################################################################################################################

def _member_token() -> 'str':
    out = keycloak_oauth.get_user_token(
        _client.client_id, _client.redirect_uri, keycloak_oauth.User_Member, keycloak_oauth.Password_Member)
    return out

# ################################################################################################################################

def _outsider_token() -> 'str':
    out = keycloak_oauth.get_user_token(
        _client.client_id, _client.redirect_uri, keycloak_oauth.User_Outsider, keycloak_oauth.Password_Outsider)
    return out

# ################################################################################################################################

def _iso_to_ns(value:'str') -> 'int':
    parsed = datetime.fromisoformat(value)
    out = int(parsed.timestamp()) * 1_000_000_000 + parsed.microsecond * 1000
    return out

# ################################################################################################################################

def _flatten(prefix:'str', value:'any_', out:'anydict') -> 'None':
    """ The flattening the suite expects of a data document - the keys of nested objects joined with a dot,
    lists kept as they are, nulls and empty strings left out.
    """
    if isinstance(value, dict):
        for key, item in value.items():
            _flatten(f'{prefix}.{key}', item, out)

    elif value is None:
        pass

    elif value == '':
        pass

    else:
        out[prefix] = value

# ################################################################################################################################

def _assert_record_matches_row(record:'anydict', row:'anydict') -> 'None':
    """ One record carries its row's columns, attrs and time, and names its event.
    """
    attributes = record['attributes']

    assert attributes[MappingCtx.Event_ID] == row['id']

    # Columns, with empty strings left out ..
    for name in _compared_columns:
        value = row[name]
        key = _column(name)

        if value == '':
            assert key not in attributes, f'{key} should be absent, got `{attributes[key]}`'
        else:
            assert attributes[key] == value, f'{key}: expected `{value}`, got `{attributes.get(key)}`'

    # .. server_name and data have no column attribute ..
    assert _column('server_name') not in attributes
    assert _column('data') not in attributes

    # .. attrs as they were written ..
    for name, value in row['attrs'].items():
        key = _attr(name)
        assert attributes[key] == value, f'{key}: expected `{value}`, got `{attributes.get(key)}`'

    # .. the event name, the body and the time.
    assert record['event_name'] == f'{MappingCtx.Prefix}.' + row['event_type']
    assert record['body'] == '{} {} {} {}'.format(row['source'], row['event_type'], row['object_name'], row['outcome'])
    assert record['time_unix_nano'] == _iso_to_ns(row['event_time_iso'])
    assert record['observed_time_unix_nano'] >= record['time_unix_nano']

    if row['outcome'] == AuditOutcome.Error:
        assert record['severity_text'] == 'ERROR'
    else:
        assert record['severity_text'] == 'INFO'

    assert record['scope_name'] == APICtx.Scope_Name

# ################################################################################################################################

def _assert_data_matches_document(record:'anydict', document:'anydict') -> 'None':
    """ The whole data document arrived under the data prefix.
    """
    expected:'anydict' = {}
    _flatten(DataCtx.Data_Prefix, document, expected)

    attributes = record['attributes']

    for key, value in expected.items():
        assert attributes[key] == value, f'{key}: expected `{value}`, got `{attributes.get(key)}`'

# ################################################################################################################################

def _assert_resource(record:'anydict', live:'AuditExportEnvironment') -> 'None':
    """ The resource names the server process.
    """
    resource = record['resource']

    assert resource['service.name'] == APICtx.Service_Server
    assert resource['zato.server.name'] == ModuleCtx.Server_Name
    assert resource['service.namespace']
    assert resource['service.namespace'] == resource['zato.cluster.name']
    assert resource['service.instance.id']
    assert resource['service.version']
    assert resource['host.name']
    assert isinstance(resource['process.pid'], int)
    assert resource['process.pid'] > 0

    # Nothing of the collector's own configuration leaks into the resource
    assert live.collector.bearer_token not in str(resource)

# ################################################################################################################################

def _assert_no_data_or_payload(record:'anydict') -> 'None':
    for key in record['attributes']:
        assert not key.startswith(DataCtx.Data_Prefix), key
        assert not key.startswith(DataCtx.Payload_Prefix), key

# ################################################################################################################################

def _wait_for_one_record(live:'AuditExportEnvironment', row:'anydict', timeout:'float'=ModuleCtx.Audit_Timeout) -> 'anydict':
    """ The one record of an event that is written once.
    """
    records = wait_for_record(live.collector.output_path, row['id'], timeout=timeout)
    record_count = len(records)

    assert record_count == 1, f'Expected one record of event {row["id"]}, got {record_count}'

    out = records[0]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMCPConversation:
    """ A person signed in through the IdP runs a conversation and each of its events arrives as a record
    equal to its row.
    """

    def test_initialize_tools_list_and_tools_call(self, audit_export_live:'AuditExportEnvironment') -> 'None':

        live = audit_export_live
        min_id = last_event_id(live.audit_db_path, AuditSource.MCP, ModuleCtx.Gateway_Name)

        maria = bearer_caller(live.gateway_url, _member_token())

        initialize_result = maria.initialize()
        assert initialize_result.response.status_code == OK, initialize_result.response.text
        session_id = initialize_result.session_id
        assert session_id

        response = maria.tools_list(session_id)
        assert response.status_code == OK, response.text

        response = maria.tools_call(session_id, ModuleCtx.Echo_Service, _echo_arguments)
        assert response.status_code == OK, response.text

        expected_types = (AuditEvent.MCP_Initialize, AuditEvent.MCP_Tools_List, AuditEvent.MCP_Tools_Call)

        for event_type in expected_types:

            row = wait_for_event_of_type(live.audit_db_path, AuditSource.MCP, ModuleCtx.Gateway_Name, min_id, event_type)
            record = _wait_for_one_record(live, row)

            _assert_record_matches_row(record, row)
            _assert_data_matches_document(record, row['document'])
            _assert_resource(record, live)

            assert record['severity_text'] == 'INFO'

            # The auth block is there as it is ..
            attributes = record['attributes']
            auth = row['document']['auth']

            assert attributes[_data('auth.identity')] == keycloak_oauth.User_Member
            assert attributes[_data('auth.identity')] == auth['identity']
            assert attributes[_data('auth.definition')] == ModuleCtx.Definition_Name
            assert attributes[_data('auth.type')] == auth['type']
            assert attributes[_data('auth.issuer')] == auth['issuer']
            assert attributes[_data('auth.client')] == auth['client']
            assert attributes[_data('auth.scopes')] == auth['scopes']
            assert attributes[_data('auth.claims_matched')] == auth['claims_matched']

            # .. the person is the caller ..
            assert attributes[_column('ext_client_id')] == row['ext_client_id']
            assert keycloak_oauth.User_Member in attributes[_column('ext_client_id')]
            assert attributes[_attr('identity')] == keycloak_oauth.User_Member

            # .. the session rides in sub_key and nothing of the payloads leaves.
            assert attributes[_column('sub_key')] == session_id

            for key in attributes:
                assert not key.startswith(DataCtx.Payload_Prefix), key

        # The tool's name is the endpoint of the call
        row = wait_for_event_of_type(live.audit_db_path, AuditSource.MCP, ModuleCtx.Gateway_Name, min_id, AuditEvent.MCP_Tools_Call)
        record = _wait_for_one_record(live, row)

        assert record['attributes'][_column('endpoint')] == ModuleCtx.Echo_Service
        assert record['event_name'] == 'zato.audit.mcp-tools-call'

# ################################################################################################################################
# ################################################################################################################################

class TestRefusals:
    """ Refused callers arrive as error records naming the reason.
    """

    def test_a_person_outside_the_group(self, audit_export_live:'AuditExportEnvironment') -> 'None':

        live = audit_export_live
        min_id = last_event_id(live.audit_db_path, AuditSource.MCP, ModuleCtx.Gateway_Name)

        response = bearer_caller(live.gateway_url, _outsider_token()).tools_list_stateless()
        assert response.status_code == UNAUTHORIZED, response.text

        row = wait_for_event_of_type(live.audit_db_path, AuditSource.MCP, ModuleCtx.Gateway_Name, min_id, AuditEvent.Auth_Failed)
        record = _wait_for_one_record(live, row)

        _assert_record_matches_row(record, row)
        _assert_data_matches_document(record, row['document'])

        attributes = record['attributes']

        assert record['severity_text'] == 'ERROR'
        assert record['event_name'] == 'zato.audit.auth-failed'
        assert attributes[_data('auth.reason')] == BearerRefusalReason.Claim_Missing
        assert attributes[_data('auth.claim')] == keycloak_oauth.Claim_Groups

        # The token could be read, so the person and the client are there
        assert attributes[_data('auth.identity')] == keycloak_oauth.User_Outsider
        assert attributes[_data('auth.client')] == _client.client_id
        assert attributes[_attr('identity')] == keycloak_oauth.User_Outsider
        assert attributes[_attr('reason')] == BearerRefusalReason.Claim_Missing

# ################################################################################################################################

    def test_a_malformed_token(self, audit_export_live:'AuditExportEnvironment') -> 'None':

        live = audit_export_live
        min_id = last_event_id(live.audit_db_path, AuditSource.MCP, ModuleCtx.Gateway_Name)

        response = bearer_caller(live.gateway_url, 'not-a-token').tools_list_stateless()
        assert response.status_code == UNAUTHORIZED, response.text

        row = wait_for_event_of_type(live.audit_db_path, AuditSource.MCP, ModuleCtx.Gateway_Name, min_id, AuditEvent.Auth_Failed)
        record = _wait_for_one_record(live, row)

        _assert_record_matches_row(record, row)

        attributes = record['attributes']

        assert record['severity_text'] == 'ERROR'
        assert attributes[_data('auth.reason')] == BearerRefusalReason.Malformed

        # Nothing could be read off the token, so neither the person nor the client is there
        assert _data('auth.identity') not in attributes
        assert _data('auth.client') not in attributes
        assert _attr('identity') not in attributes
        assert _attr('client') not in attributes

# ################################################################################################################################
# ################################################################################################################################

class TestRateLimited:
    """ Calls past the daily limit arrive as rate-limited records naming the caller.
    """

    def test_a_call_over_the_limit(self, audit_export_live:'AuditExportEnvironment') -> 'None':

        live = audit_export_live
        url = live.limited_gateway_url
        min_id = last_event_id(live.audit_db_path, AuditSource.MCP, ModuleCtx.Limited_Gateway_Name)

        maria = bearer_caller(url, _member_token())

        for _ in range(ModuleCtx.Daily_Limit):
            response = maria.tools_call_stateless(ModuleCtx.Echo_Service, _echo_arguments)
            assert response.status_code == OK, response.text

        response = maria.tools_call_stateless(ModuleCtx.Echo_Service, _echo_arguments)
        assert response.status_code == TOO_MANY_REQUESTS, f'Expected 429, got {response.status_code} -> {response.text}'
        assert response.headers[Header_Retry_After]

        row = wait_for_event_of_type(
            live.audit_db_path, AuditSource.MCP, ModuleCtx.Limited_Gateway_Name, min_id, AuditEvent.Rate_Limited)
        record = _wait_for_one_record(live, row)

        _assert_record_matches_row(record, row)
        _assert_data_matches_document(record, row['document'])

        attributes = record['attributes']

        assert record['severity_text'] == 'ERROR'
        assert record['event_name'] == 'zato.audit.rate-limited'

        # The caller is in ext_client_id and the wait in the data ..
        assert keycloak_oauth.User_Member in attributes[_column('ext_client_id')]
        assert attributes[_data('retry_after_seconds')] == row['document']['retry_after_seconds']
        assert attributes[_data('retry_after_seconds')] > 0

        # .. and a rate-limited event has no auth block.
        for key in attributes:
            assert not key.startswith(_data('auth')), key

# ################################################################################################################################
# ################################################################################################################################

class TestRESTChannel:
    """ The events of a REST channel arrive with their columns, with payloads only under the channel's flag.
    """

    def test_without_the_payload_flag(self, audit_export_live:'AuditExportEnvironment') -> 'None':

        live = audit_export_live
        min_id = last_event_id(live.audit_db_path, AuditSource.REST_Channel, ModuleCtx.REST_Channel_Name)

        body = dumps({'invoice_id': 'INV-2026-0042', 'amount': 100})
        response = requests.post(live.rest_url, data=body, headers={'Content-Type': 'application/json'},
            timeout=ModuleCtx.HTTP_Timeout)
        assert response.status_code == OK, response.text

        request_row = wait_for_event_of_type(
            live.audit_db_path, AuditSource.REST_Channel, ModuleCtx.REST_Channel_Name, min_id, AuditEvent.Request_Received)
        response_row = wait_for_event_of_type(
            live.audit_db_path, AuditSource.REST_Channel, ModuleCtx.REST_Channel_Name, min_id, AuditEvent.Response_Sent)

        # The rows hold the payloads ..
        assert request_row['data'] == body
        assert response_row['data']

        for row in (request_row, response_row):

            record = _wait_for_one_record(live, row)

            _assert_record_matches_row(record, row)
            _assert_resource(record, live)

            # .. and the records do not.
            _assert_no_data_or_payload(record)

            assert record['severity_text'] == 'INFO'
            assert record['attributes'][_column('endpoint')] == ModuleCtx.Echo_Service
            assert 'INV-2026-0042' not in str(record['attributes'])

# ################################################################################################################################

    def test_with_the_payload_flag(self, audit_export_live:'AuditExportEnvironment') -> 'None':

        live = audit_export_live
        min_id = last_event_id(live.audit_db_path, AuditSource.REST_Channel, ModuleCtx.REST_Payload_Channel_Name)

        body = dumps({'invoice_id': 'INV-2026-0043', 'amount': 250})
        response = requests.post(live.rest_payload_url, data=body, headers={'Content-Type': 'application/json'},
            timeout=ModuleCtx.HTTP_Timeout)
        assert response.status_code == OK, response.text

        request_row = wait_for_event_of_type(
            live.audit_db_path, AuditSource.REST_Channel, ModuleCtx.REST_Payload_Channel_Name, min_id, AuditEvent.Request_Received)
        response_row = wait_for_event_of_type(
            live.audit_db_path, AuditSource.REST_Channel, ModuleCtx.REST_Payload_Channel_Name, min_id, AuditEvent.Response_Sent)

        request_record = _wait_for_one_record(live, request_row)
        response_record = _wait_for_one_record(live, response_row)

        _assert_record_matches_row(request_record, request_row)
        _assert_record_matches_row(response_record, response_row)

        # What was sent and what came back travel as the payload ..
        assert request_record['attributes'][_payload('data')] == body
        assert request_record['attributes'][_payload('data')] == request_row['data']

        assert response_record['attributes'][_payload('data')] == response_row['data']
        assert response_record['attributes'][_payload('data')] == response.text

        # .. neither was cut ..
        assert DataCtx.Payload_Truncated not in request_record['attributes']
        assert DataCtx.Payload_Truncated not in response_record['attributes']

        # .. and nothing goes under the data prefix, since a REST channel has no allow list.
        for record in (request_record, response_record):
            for key in record['attributes']:
                assert not key.startswith(DataCtx.Data_Prefix), key

# ################################################################################################################################
# ################################################################################################################################

class TestSourceSelection:
    """ Only the selected sources leave the server.
    """

    def test_config_events_stay_in_the_database(self, audit_export_live:'AuditExportEnvironment') -> 'None':

        live = audit_export_live

        # A quota tier created through the API writes a config event ..
        config_min_id = last_event_id(live.audit_db_path, AuditSource.Config, ModuleCtx.Tier_Name)

        _ = live.zato.client().invoke('zato.security.tier.create', {
            'name': ModuleCtx.Tier_Name,
            'rules_json': dumps(ModuleCtx.Tier_Rules),
        })

        config_row = wait_for_event_of_type(
            live.audit_db_path, AuditSource.Config, ModuleCtx.Tier_Name, config_min_id, AuditEvent.Config_Created)

        # .. a REST call made after it is exported, so the export has moved past the config event ..
        rest_min_id = last_event_id(live.audit_db_path, AuditSource.REST_Channel, ModuleCtx.REST_Channel_Name)

        response = requests.post(live.rest_url, data=dumps({'invoice_id': 'INV-2026-0044'}),
            headers={'Content-Type': 'application/json'}, timeout=ModuleCtx.HTTP_Timeout)
        assert response.status_code == OK, response.text

        rest_row = wait_for_event_of_type(
            live.audit_db_path, AuditSource.REST_Channel, ModuleCtx.REST_Channel_Name, rest_min_id, AuditEvent.Response_Sent)
        _ = _wait_for_one_record(live, rest_row)

        # .. and the config event is not among what arrived.
        assert not has_record(live.collector.output_path, config_row['id']), \
            f'Config event {config_row["id"]} should not have arrived'

        arrived = read_records(live.collector.output_path)

        for records in arrived.values():
            for record in records:
                assert record['attributes'][_column('source')] in (AuditSource.MCP, AuditSource.REST_Channel)

# ################################################################################################################################
# ################################################################################################################################

class TestOutage:
    """ With the collector away the export pauses with one log line, and when it is back the events arrive
    and one line says so.
    """

    def test_pause_and_resume(self, audit_export_live:'AuditExportEnvironment') -> 'None':

        live = audit_export_live
        log_path = live.server_log_path

        paused_before = count_lines(log_path, _paused_marker)
        resumed_before = count_lines(log_path, _resumed_marker)

        min_id = last_event_id(live.audit_db_path, AuditSource.MCP, ModuleCtx.Gateway_Name)
        maria = bearer_caller(live.gateway_url, _member_token())

        stop_container(live.collector.container_name)

        try:
            response = maria.tools_call_stateless(ModuleCtx.Echo_Service, _echo_arguments)
            assert response.status_code == OK, response.text

            row = wait_for_event_of_type(live.audit_db_path, AuditSource.MCP, ModuleCtx.Gateway_Name, min_id, AuditEvent.MCP_Tools_Call)

            # The export pauses with one line naming the collector ..
            wait_for_line(log_path, _paused_marker, ModuleCtx.Audit_Timeout)

            assert count_lines(log_path, _paused_marker) == paused_before + 1
            assert count_lines(log_path, _resumed_marker) == resumed_before

            # .. and request handling went on - the event is in the database.
            assert row['outcome'] == AuditOutcome.OK

        finally:
            start_container(live.collector.container_name)

        # The event arrives once the collector is back, with the retry backoff having grown in the meantime ..
        record = _wait_for_one_record(live, row, timeout=ModuleCtx.Resume_Timeout)
        _assert_record_matches_row(record, row)

        # .. and the resumption is one line, with nothing dropped and nothing else logged about it.
        wait_for_line(log_path, _resumed_marker, ModuleCtx.Audit_Timeout)

        assert count_lines(log_path, _paused_marker) == paused_before + 1
        assert count_lines(log_path, _resumed_marker) == resumed_before + 1
        assert count_lines(log_path, _full_text) == 0
        assert count_lines(log_path, ' dropped, ids ') == 0

        # The reason of the pause is in the paused line and the bearer token is nowhere in the log
        assert count_lines(log_path, _paused_text + live.collector.http_endpoint + _paused_marker) == paused_before + 1
        assert count_lines(log_path, live.collector.bearer_token) == 0

# ################################################################################################################################
# ################################################################################################################################

class TestGRPC:
    """ The same conversation arrives the same way over gRPC.
    """

    def test_tools_call_over_grpc(self, audit_export_live:'AuditExportEnvironment') -> 'None':

        live = audit_export_live

        environment = build_export_environment(live.collector, protocol=ExportCtx.Protocol_GRPC, sources=Exported_Sources)
        environment[Server_Address_Env_Key] = live.server_address
        live.zato.restart(environment)

        wait_for_tools(live.key_gateway_url, live.api_key)

        # The server says it exports over gRPC ..
        wait_for_line(live.server_log_path, f'Audit export to {live.collector.grpc_endpoint} is on', ModuleCtx.Audit_Timeout)

        min_id = last_event_id(live.audit_db_path, AuditSource.MCP, ModuleCtx.Gateway_Name)
        maria = bearer_caller(live.gateway_url, _member_token())

        response = maria.tools_call_stateless(ModuleCtx.Echo_Service, _echo_arguments)
        assert response.status_code == OK, response.text

        row = wait_for_event_of_type(live.audit_db_path, AuditSource.MCP, ModuleCtx.Gateway_Name, min_id, AuditEvent.MCP_Tools_Call)
        record = _wait_for_one_record(live, row)

        # .. and the record is the same as over HTTP.
        _assert_record_matches_row(record, row)
        _assert_data_matches_document(record, row['document'])
        _assert_resource(record, live)

        assert record['attributes'][_data('auth.identity')] == keycloak_oauth.User_Member
        assert record['attributes'][_column('endpoint')] == ModuleCtx.Echo_Service

# ################################################################################################################################
# ################################################################################################################################
