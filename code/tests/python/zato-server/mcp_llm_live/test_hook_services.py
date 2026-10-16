# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

# Zato
from zato.common.test import rand_string

# local
import _agent
import _constants
import _enmasse
import _helpers
import _markers
from _client_stateless import MCPStatelessClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# The generic connection type of an MCP gateway and the admin services the edit path consists of
_gateway_type        = 'gateway-mcp'
_service_get_list    = 'zato.generic.connection.get-list'
_service_get_by_id   = 'zato.generic.connection.get-by-id'
_service_edit        = 'zato.generic.connection.edit'

# The session TTL the edit sets, a field unrelated to data masking and the hook services
_edited_session_ttl = 1234

# ################################################################################################################################
# ################################################################################################################################

def _hook_lines(zato_server:'anydict', gateway_name:'str') -> 'strlist':
    out = _markers.read_hook_lines(zato_server['hook_path'], gateway_name)
    return out

# ################################################################################################################################

def _new_hook_lines(zato_server:'anydict', gateway_name:'str', line_count_before:'int') -> 'strlist':
    lines = _hook_lines(zato_server, gateway_name)

    out = lines[line_count_before:]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRequestHook:
    """ The request hook service sees every message a gateway receives, may replace it and may refuse it.
    """

# ################################################################################################################################

    def test_every_method_passes_the_request_hook(self, zato_server:'anydict') -> 'None':

        gateway_name = _constants.Gateway_Hook_Record
        line_count_before = len(_hook_lines(zato_server, gateway_name))

        client = _helpers.make_client(zato_server, _constants.Path_Hook_Record)
        session_id = _helpers.open_session(client)

        _ = _helpers.list_tools(client, session_id)
        body = _helpers.call_tool(client, session_id, _constants.Service_Order_Status, {'order_id': _constants.Order_ID})

        data = _helpers.get_result_data(body)
        assert data['status'] == _constants.Order_Status, body

        # Each message reached the hook with the caller's identity, which for Basic Auth is the name
        # of the security definition, and the call with the tool's name too
        identity = _constants.Sec_Basic
        lines = _new_hook_lines(zato_server, gateway_name, line_count_before)

        request_lines = [line for line in lines if line.startswith('request ')]

        assert request_lines == [
            f'request initialize {identity}',
            f'request tools/list {identity}',
            f'request tools/call {identity} {_constants.Service_Order_Status}',
        ], lines

# ################################################################################################################################

    def test_a_replaced_message_is_the_one_processed(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Hook_Replace)
        session_id = _helpers.open_session(client)

        # The hook rewrites the order id before the service runs ..
        body = _helpers.call_tool(client, session_id, _constants.Service_Order_Status, {'order_id': _constants.Order_ID})

        data = _helpers.get_result_data(body)
        assert data['order_id'] == _constants.Hook_Replaced_Order_ID, body

        # .. and leaves the calls of other tools as they were.
        body = _helpers.call_tool(client, session_id, _constants.Service_Customer_Get,
            {'customer_id': _constants.Customer_ID})

        data = _helpers.get_result_data(body)
        assert data['name'] == _constants.Customer_Name, body

# ################################################################################################################################

    def test_a_refused_message_is_a_json_rpc_error(self, zato_server:'anydict') -> 'None':

        marker_path = zato_server['marker_path']
        cancel_count_before = _markers.count_invocations(marker_path, _constants.Service_Order_Cancel)

        client = _helpers.make_client(zato_server, _constants.Path_Hook_Reject)
        session_id = _helpers.open_session(client)

        # The hook refuses the cancellation with an error that names no reason ..
        body = _helpers.call_tool(client, session_id, _constants.Service_Order_Cancel, {'order_id': _constants.Order_ID})

        assert body['error']['code'] == _constants.Error_Request_Rejected, body
        assert 'not permitted' not in str(body), body

        # .. the service never ran ..
        cancel_count_after = _markers.count_invocations(marker_path, _constants.Service_Order_Cancel)
        assert cancel_count_after == cancel_count_before

        # .. and the other tools of the same session keep working.
        body = _helpers.call_tool(client, session_id, _constants.Service_Order_Status, {'order_id': _constants.Order_ID})

        data = _helpers.get_result_data(body)
        assert data['status'] == _constants.Order_Status, body

# ################################################################################################################################

    def test_the_stateless_revision_passes_the_hooks(self, zato_server:'anydict') -> 'None':

        gateway_name = _constants.Gateway_Hook_Stateless
        line_count_before = len(_hook_lines(zato_server, gateway_name))

        mcp_url = zato_server['mcp_url'](_constants.Path_Hook_Stateless)
        client = MCPStatelessClient(mcp_url, auth=zato_server['basic_auth'])

        response = client.tools_call(_constants.Service_Order_Status, {'order_id': _constants.Order_ID})
        assert response.status_code == OK, response.text

        data = _helpers.get_result_data(response.json())
        assert data['status'] == _constants.Order_Status, response.text

        lines = _new_hook_lines(zato_server, gateway_name, line_count_before)

        assert lines == [
            f'request tools/call {_constants.Sec_Basic} {_constants.Service_Order_Status}',
            'response tools/call result',
        ], lines

# ################################################################################################################################
# ################################################################################################################################

class TestResponseHook:
    """ The response hook service sees every reply a gateway sends and may replace it.
    """

# ################################################################################################################################

    def test_every_reply_passes_the_response_hook(self, zato_server:'anydict') -> 'None':

        gateway_name = _constants.Gateway_Hook_Record
        line_count_before = len(_hook_lines(zato_server, gateway_name))

        client = _helpers.make_client(zato_server, _constants.Path_Hook_Record)
        session_id = _helpers.open_session(client)

        _ = _helpers.list_tools(client, session_id)
        _ = _helpers.call_tool(client, session_id, _constants.Service_Order_Status, {'order_id': _constants.Order_ID})

        # An unknown tool is an error reply, which passes the hook as well
        _ = _helpers.call_tool(client, session_id, 'crm.no-such-tool', {})

        lines = _new_hook_lines(zato_server, gateway_name, line_count_before)
        response_lines = [line for line in lines if line.startswith('response ')]

        assert response_lines == [
            'response initialize result',
            'response tools/list result',
            'response tools/call result',
            'response tools/call error',
        ], lines

# ################################################################################################################################

    def test_a_replaced_reply_is_the_one_sent(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Hook_Response)
        session_id = _helpers.open_session(client)

        # The tool result is the one the hook put in place ..
        body = _helpers.call_tool(client, session_id, _constants.Service_Customer_Get,
            {'customer_id': _constants.Customer_ID})

        data = _helpers.get_result_data(body)
        assert data == _constants.Hook_Replaced_Result, body

        # .. while the replies of other methods are the gateway's own.
        tool_names = _helpers.get_tool_names(_helpers.list_tools(client, session_id))
        assert _constants.Service_Customer_Get in tool_names, tool_names

# ################################################################################################################################
# ################################################################################################################################

class TestHooksAtRuntime:
    """ A hook service switched on and off by re-import takes effect without a restart.
    """

# ################################################################################################################################

    def test_a_reimport_switches_a_hook_on_and_off(self, zato_server:'anydict') -> 'None':

        server_directory = zato_server['server_directory']
        gateway_name = _constants.Gateway_Hook_Runtime

        client = _helpers.make_client(zato_server, _constants.Path_Hook_Runtime)

        def _call_and_count() -> 'int':
            """ One order status call on a fresh session, returning how many hook lines it produced.
            """
            line_count_before = len(_hook_lines(zato_server, gateway_name))

            session_id = _helpers.open_session(client)
            _ = _helpers.call_tool(client, session_id, _constants.Service_Order_Status, {'order_id': _constants.Order_ID})

            out = len(_hook_lines(zato_server, gateway_name)) - line_count_before
            return out

        # Without hooks, no call leaves a line ..
        assert _call_and_count() == 0

        overrides = {gateway_name: {'request_hook_service': _constants.Service_Hook_Request_Record}}

        try:
            # .. a re-import switches the request hook on ..
            _enmasse.run_import(server_directory, _enmasse.build_suite_config(gateway_overrides=overrides))
            _helpers.wait_until(lambda: _call_and_count() > 0, 'the request hook to be switched on')

        finally:
            # .. and the suite's own configuration switches it off again.
            _enmasse.run_import(server_directory, _enmasse.build_suite_config())
            _helpers.wait_until(lambda: _call_and_count() == 0, 'the request hook to be switched off')

# ################################################################################################################################
# ################################################################################################################################

class TestEditPreservation:
    """ An edit of an unrelated field through the admin edit path keeps the data masking keys and the hook services.
    """

# ################################################################################################################################

    def test_an_edit_keeps_the_masking_and_hook_keys(self, zato_server:'anydict') -> 'None':

        server_directory = zato_server['server_directory']
        suffix = rand_string()
        gateway_name = f'test.llm.edit-preservation.{suffix}'

        expected = {
            'safeguards_masking_sets': [_constants.Masking_Set],
            'safeguards_masking_excluded': [_constants.Masking_Excluded],
            'safeguards_masking_custom_fields': list(_constants.Masking_Custom_Fields),
            'safeguards_masking_custom_enabled': False,
            'request_hook_service': _constants.Service_Hook_Request_Record,
            'response_hook_service': _constants.Service_Hook_Response_Record,
        }

        gateway = {
            'name': gateway_name,
            'url_path': f'/mcp/llm/edit-preservation-{suffix}',
            'services': [_constants.Service_Order_Status],
            **expected,
        }

        # The gateway is created by an import of its own ..
        _enmasse.run_import(server_directory, {'mcp_gateway': [gateway]})

        # .. found among the gateways ..
        gateway_list = _helpers.admin_invoke(zato_server, _service_get_list, {'type_': _gateway_type})

        gateway_id = None

        for item in gateway_list:
            if item['name'] == gateway_name:
                gateway_id = item['id']

        assert gateway_id is not None, gateway_list

        # .. read, edited in one unrelated field and saved back, the way the Dashboard's inline edit does it ..
        item_dict = _helpers.admin_invoke(zato_server, _service_get_by_id, {'id': gateway_id})
        item_dict['session_ttl'] = _edited_session_ttl

        _ = _helpers.admin_invoke(zato_server, _service_edit, item_dict)

        # .. and read back with the unrelated field changed and the six keys as they were.
        edited = _helpers.admin_invoke(zato_server, _service_get_by_id, {'id': gateway_id})

        assert edited['session_ttl'] == _edited_session_ttl, edited

        for key, value in expected.items():
            assert edited[key] == value, (key, edited)

# ################################################################################################################################
# ################################################################################################################################

class TestHooksThroughModel:
    """ A conversation with the model passes every message of its own through the request hook service.
    """

# ################################################################################################################################

    def test_the_agents_calls_pass_the_request_hook(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        gateway_name = _constants.Gateway_Hook_Record
        line_count_before = len(_hook_lines(zato_server, gateway_name))

        client = _helpers.make_client(zato_server, _constants.Path_Hook_Record)

        task = f'What is the delivery status of order {_constants.Order_ID}?'
        result = _agent.run_agent(client, task)

        # The model called the order status tool and answered with what it returned ..
        tool_names = [tool_call.tool_name for tool_call in result.tool_calls]
        assert _constants.Service_Order_Status in tool_names, tool_names
        assert _helpers.text_contains(result.final_text, _constants.Order_Status), result.final_text

        # .. and every message of the conversation reached the request hook, each tool call among them.
        lines = _new_hook_lines(zato_server, gateway_name, line_count_before)
        request_lines = [line for line in lines if line.startswith('request ')]

        identity = _constants.Sec_Basic

        assert request_lines[0] == f'request initialize {identity}', lines
        assert request_lines[1] == f'request tools/list {identity}', lines

        call_line = f'request tools/call {identity} {_constants.Service_Order_Status}'
        call_line_count = request_lines.count(call_line)
        order_status_call_count = tool_names.count(_constants.Service_Order_Status)

        assert call_line_count == order_status_call_count, lines

# ################################################################################################################################
# ################################################################################################################################
