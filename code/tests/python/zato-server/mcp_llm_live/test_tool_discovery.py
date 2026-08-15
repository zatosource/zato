# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time

# local
import _agent
import _audit
import _constants
import _helpers

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# How long a hot-deployed schema change may take to show up in tools/list, in seconds
_hot_deploy_timeout = 60

# How often to poll for it, in seconds
_hot_deploy_poll_interval = 0.5

# The field the second build of the probe service adds to its input declaration
_probe_new_field = 'detail'

# ################################################################################################################################
# ################################################################################################################################

class TestToolDiscovery:
    """ The tools a gateway lists are exactly the services assigned to it, with schemas
    that come from the services' own input declarations.
    """

# ################################################################################################################################

    def test_tools_list_returns_exactly_the_assigned_services(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        tools = _helpers.list_tools(client, session_id)
        tool_names = _helpers.get_tool_names(tools)

        # The main gateway serves the four CRM services and nothing else -
        # no zato.* internals, no demo services and no services from other gateways.
        assert sorted(tool_names) == sorted(_constants.Service_List_CRM), tool_names

        for tool_name in tool_names:
            assert not tool_name.startswith('zato.'), tool_names

        assert _constants.Service_Deploy_Probe not in tool_names, tool_names

# ################################################################################################################################

    def test_tool_schemas_match_the_declared_input(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        tools = _helpers.list_tools(client, session_id)

        schemas = {}

        for tool in tools:
            schemas[tool['name']] = tool['inputSchema']

        # Each service declares one required string input and the schema says exactly that
        expected_fields = {
            _constants.Service_Customer_Get: 'customer_id',
            _constants.Service_Invoice_List: 'count',
            _constants.Service_Order_Status: 'order_id',
            _constants.Service_Order_Cancel: 'order_id',
        }

        for service_name, field_name in expected_fields.items():

            schema = schemas[service_name]

            assert schema['type'] == 'object', schema
            assert schema['required'] == [field_name], schema

            field_schema = schema['properties'][field_name]
            assert field_schema['type'] == 'string', schema

# ################################################################################################################################

    def test_tools_are_isolated_between_gateways(self, zato_server:'anydict') -> 'None':

        # The hot-deploy gateway serves only the probe service ..
        client = _helpers.make_client(zato_server, _constants.Path_Hotdeploy)
        session_id = _helpers.open_session(client)

        tools = _helpers.list_tools(client, session_id)
        tool_names = _helpers.get_tool_names(tools)

        assert tool_names == [_constants.Service_Deploy_Probe], tool_names

        # .. and calling a tool that only other gateways serve is an unknown-tool error there.
        body = _helpers.call_tool(client, session_id, _constants.Service_Customer_Get,
            {'customer_id': _constants.Customer_ID})

        assert body['error']['code'] == _constants.Error_Method_Not_Found, body

# ################################################################################################################################

    def test_hot_deploy_updates_the_advertised_schema(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Hotdeploy)
        session_id = _helpers.open_session(client)

        # The first build declares only the revision field ..
        tools = _helpers.list_tools(client, session_id)
        schema = tools[0]['inputSchema']

        assert tools[0]['name'] == _constants.Service_Deploy_Probe, tools
        assert _probe_new_field not in schema['properties'], schema

        # .. the second build adds one more input field and goes out through the pickup directory ..
        fixtures_directory = os.path.join(os.path.dirname(__file__), 'fixtures', 'services')
        probe_path = os.path.join(fixtures_directory, 'crm_probe.py')

        with open(probe_path) as probe_file:
            probe_source = probe_file.read()

        # The leading dash is what declares the new field optional in Zato input syntax
        new_declaration = "input = 'revision', '-{}'".format(_probe_new_field)
        probe_source = probe_source.replace("input = 'revision'", new_declaration)
        probe_source = probe_source.replace("'build': 'first'", "'build': 'second'")

        pickup_path = os.path.join(zato_server['pickup_directory'], 'crm_probe.py')

        with open(pickup_path, 'w') as pickup_file:
            _ = pickup_file.write(probe_source)

        # .. and the next tools/list reflects the new declaration once hot deploy lands.
        deadline = time.monotonic() + _hot_deploy_timeout

        while time.monotonic() < deadline:

            tools = _helpers.list_tools(client, session_id)
            schema = tools[0]['inputSchema']

            if _probe_new_field in schema['properties']:
                break

            time.sleep(_hot_deploy_poll_interval)

        else:
            raise Exception(f'Hot-deployed schema change did not show up within {_hot_deploy_timeout}s: {schema}')

        # The new field is optional, so the required list still names only the revision
        assert schema['required'] == ['revision'], schema

# ################################################################################################################################
# ################################################################################################################################

class TestToolSelectionByLLM:
    """ The model reads the gateway's tools and picks the right one for the question asked -
    the whole path from the question through the custom service to the final answer.
    """

# ################################################################################################################################

    def test_llm_picks_the_customer_tool_over_the_near_namesake(
        self,
        zato_server:'anydict',
        ollama:'anydict',
        ) -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)

        task = (
            f'What city does customer {_constants.Customer_ID} live in and what is their name? '
            'Use the tools to find out.')

        result = _agent.run_agent(client, task)

        # The model called the customer tool, not the order status near-namesake ..
        called_names = []

        for call in result.tool_calls:
            called_names.append(call.tool_name)

        assert _constants.Service_Customer_Get in called_names, result.messages
        assert _constants.Service_Order_Status not in called_names, result.messages

        # .. with schema-valid arguments ..
        for call in result.tool_calls:
            if call.tool_name == _constants.Service_Customer_Get:
                assert call.arguments['customer_id'] == _constants.Customer_ID, call.arguments

        # .. and the final answer carries the values the custom service returned.
        assert _helpers.text_contains(result.final_text, _constants.Customer_Name), result.final_text
        assert _helpers.text_contains(result.final_text, _constants.Customer_City), result.final_text

# ################################################################################################################################

    def test_llm_runs_two_tools_in_sequence(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Main)

        task = (
            f'First look up customer {_constants.Customer_ID}, then check the status of their '
            f'order {_constants.Order_ID}. Report the customer name and the order status.')

        result = _agent.run_agent(client, task)

        # Both tools ran, the customer lookup before the order status check ..
        called_names = []

        for call in result.tool_calls:
            called_names.append(call.tool_name)

        assert _constants.Service_Customer_Get in called_names, called_names
        assert _constants.Service_Order_Status in called_names, called_names

        customer_index = called_names.index(_constants.Service_Customer_Get)
        order_index = called_names.index(_constants.Service_Order_Status)
        assert customer_index < order_index, called_names

        # .. the final answer reports both results ..
        assert _helpers.text_contains(result.final_text, _constants.Customer_Name), result.final_text
        assert _helpers.text_contains(result.final_text, _constants.Order_Status), result.final_text

        # .. and each call landed as its own audit event, in the same order.
        events = _audit.wait_for_events(
            audit_db_path, 2,
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        audited_tools = []

        for event in events:
            audited_tools.append(event['endpoint'])
            assert event['outcome'] == AuditOutcome.OK, event

        customer_index = audited_tools.index(_constants.Service_Customer_Get)
        order_index = audited_tools.index(_constants.Service_Order_Status)
        assert customer_index < order_index, audited_tools

# ################################################################################################################################
# ################################################################################################################################
