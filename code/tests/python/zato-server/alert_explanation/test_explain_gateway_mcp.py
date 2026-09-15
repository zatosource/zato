# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The explanation of an MCP gateway's alert - the mcp skill explains it, the Object section is read off the gateway's
# generic row with its path, the tools it exposes and how many, the security definitions that may call it, its size cap
# and the thresholds it sets of its own, the failures of an invalid-call alert group under the tool and the error text
# with the tool and the caller on every group, and a repeated-calls alert lists the calls of the one session to the one
# tool the fact names and no other session's.

# stdlib
import json

# Zato
from zato.common.alerting.model import AlertAction
from zato.common.alerting.object_config import storage_name
from zato.common.api import GENERIC, Groups
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.common import MCPAttr
from zato.common.odb.model import Cluster, GenericConn, GenericObject, HTTPBasicAuth

# Test helpers
from explain_helpers import _cluster_id, _llm_conn_name, _new_payload, _new_service, _new_session, _object_section, \
    _server_name, _stored_explanation, _LLMFacade, LLMTestHandler

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The gateway the tests describe
_gateway_name = 'orders.gateway'
_url_path = '/mcp/orders'

# The tools the gateway exposes - two services and one REST connection, three in all
_services = ['orders.get', 'orders.list']
_rest_connections = ['billing.backend']
_tool_count = 3

# The security definitions that may call the gateway, the members of its one security group
_group_id = 77
_group_name = 'mcp.' + _gateway_name
_caller_names = ['agent.alpha', 'agent.beta']
_caller_ids = [501, 502]

# The gateway's size cap
_max_response_size = 4096
_size_cap_mode = 'truncate'

# The thresholds the gateway sets of its own
_own_repeat_calls = 30
_own_max_tools = 40

# The title line of the skill an MCP gateway is explained with
_mcp_skill_title = '# MCP gateway explanation'

# The invalid calls the agents made - two naming a tool the gateway does not expose, one passing bad arguments
_unknown_tool = 'orders.get_orderz'
_unknown_tool_text = f'Unknown tool: {_unknown_tool}'
_bad_arguments_text = 'Invalid params: customer_id is required'

_error_code_method_not_found = -32601
_error_code_invalid_params = -32602

# The sessions of the repeated-calls alert - the one in a loop and one that called the same tool once
_looping_session = 'session-loop'
_other_session = 'session-other'
_looped_tool = 'orders.list'
_loop_count = 4

# ################################################################################################################################

def _seed_gateway(session_maker:'any_', *, groups_as_names:'bool'=False) -> 'None':
    """ One MCP gateway with its tools, one security group with two members and alert settings of its own - the group
    stored under its id the way the dashboard stores it, or under its name the way enmasse does.
    """
    session = session_maker()
    cluster = session.query(Cluster).filter(Cluster.id==_cluster_id).one()

    for caller_id, caller_name in zip(_caller_ids, _caller_names):
        security = HTTPBasicAuth(caller_id, caller_name, True, caller_name, 'MCP agents', 'secret', cluster)
        session.add(security)

    group = GenericObject()
    group.id = _group_id
    group.name = _group_name
    group.type_ = Groups.Type.Group_Parent
    group.subtype = Groups.Type.API_Clients
    group.cluster = cluster
    session.add(group)

    # A member is stored as `<sec type>-<security id>-<group id>`
    for caller_id in _caller_ids:
        member = GenericObject()
        member.name = f'basic_auth-{caller_id}-{_group_id}'
        member.type_ = Groups.Type.Group_Member
        member.subtype = Groups.Type.API_Clients
        member.parent_object_id = _group_id
        member.cluster = cluster
        session.add(member)

    if groups_as_names:
        security_groups = [_group_name]
    else:
        security_groups = [_group_id]

    opaque = {
        'url_path': _url_path,
        'services': _services,
        'rest_connections': _rest_connections,
        'security_groups': security_groups,
        'is_audit_log_active': True,
        'validate_input': True,
        'max_response_size': _max_response_size,
        'size_cap_mode': _size_cap_mode,
        'safeguards_strip_nulls': True,
        storage_name('is_active'): True,
        storage_name('repeat_calls'): _own_repeat_calls,
        storage_name('max_tools'): _own_max_tools,
        storage_name('use_llm'): True,
    }

    row = GenericConn()
    row.name = _gateway_name
    row.type_ = GENERIC.CONNECTION.TYPE.GATEWAY_MCP
    row.is_active = True
    row.is_internal = False
    row.is_channel = True
    row.is_outconn = False
    row.pool_size = 1
    row.cluster = cluster
    row.opaque1 = json.dumps(opaque)

    session.add(row)
    session.commit()
    session.close()

# ################################################################################################################################

def _insert_tool_call(
    audit_log:'AuditLog',
    cid:'str',
    tool:'str',
    session_id:'str',
    caller:'str',
    outcome:'str',
    data:'dict',
    attrs:'dict',
    ) -> 'None':
    """ One tool call the way the gateway writes it - the tool as the endpoint, the session as the sub key,
    the caller as the external client and the details in the data document and the attributes alike.
    """
    _ = audit_log.insert(AuditSource.MCP, AuditEvent.MCP_Tools_Call, _gateway_name, cid=cid, endpoint=tool,
        sub_key=session_id, ext_client_id=caller, outcome=outcome, data=json.dumps(data), attrs=attrs)

# ################################################################################################################################

def _seed_invalid_calls() -> 'None':
    """ The calls that were the agents' mistake - two for a tool the gateway does not expose from one caller,
    one with bad arguments from the other, each an error row with its error code among its attributes.
    """
    audit_log = AuditLog(_server_name)

    for index in range(2):
        _insert_tool_call(audit_log, f'unknown-{index}', _unknown_tool, f'session-{index}', _caller_names[0],
            AuditOutcome.Error,
            {'error_message': _unknown_tool_text, 'error_code': _error_code_method_not_found},
            {MCPAttr.Method: 'tools/call', MCPAttr.Error_Code: _error_code_method_not_found})

    _insert_tool_call(audit_log, 'bad-args', _services[0], 'session-bad', _caller_names[1],
        AuditOutcome.Error,
        {'error_message': _bad_arguments_text, 'error_code': _error_code_invalid_params},
        {MCPAttr.Method: 'tools/call', MCPAttr.Error_Code: _error_code_invalid_params})

# ################################################################################################################################

def _seed_repeated_calls() -> 'None':
    """ One session calling one tool over and over, every call fine, and another session calling it once.
    """
    audit_log = AuditLog(_server_name)

    for index in range(_loop_count):
        _insert_tool_call(audit_log, f'loop-{index}', _looped_tool, _looping_session, _caller_names[0],
            AuditOutcome.OK, {'result_size': 120}, {MCPAttr.Method: 'tools/call'})

    _insert_tool_call(audit_log, 'once', _looped_tool, _other_session, _caller_names[1],
        AuditOutcome.OK, {'result_size': 120}, {MCPAttr.Method: 'tools/call'})

# ################################################################################################################################

def _explain(session:'any_', repo_dir:'str', llm_address:'any_', measures:'list', fact_extra:'dict') -> 'str':
    """ Explains one alert of the gateway and gives back the prompt the model saw.
    """
    payload = _new_payload(AlertAction.Email_Digest, {}, AuditSource.MCP, object_name=_gateway_name, measures=measures)
    payload['fact'].update(fact_extra)

    service = _new_service(payload, session, repo_dir, llm=_LLMFacade({_llm_conn_name: {'is_active': True}}, llm_address))
    service.handle()

    assert len(LLMTestHandler.prompts) == 1

    out = LLMTestHandler.prompts[0]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestGatewayMCP:

    def test_an_mcp_alert_is_explained_with_the_mcp_skill(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_invalid_calls()

        session = _new_session()
        _seed_gateway(session)

        prompt = _explain(session, repo_dir, llm_address, ['invalid_call_count'], {'invalid_call_count': 3})
        assert prompt.startswith(_mcp_skill_title)

        explanation = _stored_explanation(session)

        assert explanation['source'] == AuditSource.MCP
        assert explanation['is_parsed'] is True

# ################################################################################################################################

    def test_the_object_section_carries_the_tools_the_callers_and_the_cap(self, llm_address:'any_',
        repo_dir:'str') -> 'None':

        _seed_invalid_calls()

        session = _new_session()
        _seed_gateway(session)

        prompt = _explain(session, repo_dir, llm_address, ['invalid_call_count'], {'invalid_call_count': 3})
        section = _object_section(prompt)

        assert f'Name: {_gateway_name}' in section
        assert 'Type: MCP gateway' in section
        assert 'Active: yes' in section
        assert f'Path: {_url_path}' in section

        # The tools - the services by name, the connections by group, and how many in all
        assert f'Services: {", ".join(_services)}' in section
        assert f'Rest connections: {", ".join(_rest_connections)}' in section
        assert f'Tools: {_tool_count}' in section
        assert 'Skills: None' in section

        # The security definitions in the gateway's group, by name
        assert f'Callers: {", ".join(_caller_names)}' in section

        # How the gateway shapes responses
        assert 'Input validation: on' in section
        assert f'Size cap: {_max_response_size} tokens, mode {_size_cap_mode}' in section
        assert 'Safeguards: null stripping' in section
        assert 'Audit log: on' in section

        # The gateway's own thresholds are the ones that differ from the defaults
        assert 'Alerts: on' in section
        assert f'Repeated calls {_own_repeat_calls}' in section
        assert f'Max tools {_own_max_tools}' in section

# ################################################################################################################################

    def test_a_gateway_imported_through_enmasse_names_its_callers_too(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_invalid_calls()

        session = _new_session()
        _seed_gateway(session, groups_as_names=True)

        prompt = _explain(session, repo_dir, llm_address, ['invalid_call_count'], {'invalid_call_count': 3})
        section = _object_section(prompt)

        # The group is stored under its name rather than its id, and the callers are found all the same
        assert f'Callers: {", ".join(_caller_names)}' in section

# ################################################################################################################################

    def test_the_failures_group_under_the_tool_and_the_error_text(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_invalid_calls()

        session = _new_session()
        _seed_gateway(session)

        prompt = _explain(session, repo_dir, llm_address, ['invalid_call_count'], {'invalid_call_count': 3})

        # The two calls of the unknown tool are one group named by the error text and its code, with the tool
        # and the caller under it, the bad arguments another
        assert f'{_unknown_tool_text} (error_code={_error_code_method_not_found})' in prompt
        assert 'Count: 2' in prompt
        assert f'Tool: {_unknown_tool}' in prompt
        assert f'Caller: {_caller_names[0]}' in prompt

        assert f'{_bad_arguments_text} (error_code={_error_code_invalid_params})' in prompt
        assert f'Tool: {_services[0]}' in prompt
        assert f'Caller: {_caller_names[1]}' in prompt

        # The Failures section speaks of requests agents made
        assert 'request an agent made' in prompt

# ################################################################################################################################

    def test_a_repeated_calls_alert_lists_the_one_sessions_calls_to_the_one_tool(self, llm_address:'any_',
        repo_dir:'str') -> 'None':

        _seed_repeated_calls()

        session = _new_session()
        _seed_gateway(session)

        fact_extra = {
            'repeat_call_count': _loop_count,
            'repeat_call_tool': _looped_tool,
            'repeat_call_session': _looping_session,
        }
        prompt = _explain(session, repo_dir, llm_address, ['repeat_call_count'], fact_extra)

        # The Alert section names the session and the tool the fact carries ..
        assert f'repeat_call_tool = {_looped_tool}' in prompt
        assert f'repeat_call_session = {_looping_session}' in prompt

        # .. and the four calls of the looping session are the one group of the evidence, the tool and the caller under it
        failures = prompt.split('## Failures')[1].split('## Baseline')[0]

        assert f'Count: {_loop_count}' in failures
        assert f'Tool: {_looped_tool}' in failures
        assert f'Caller: {_caller_names[0]}' in failures

        # The other session's one call is not among them
        assert _caller_names[1] not in failures
        assert 'Count: 1' not in failures

# ################################################################################################################################
# ################################################################################################################################
