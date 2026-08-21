# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.server.connection.mcp.connection_tools.sql import definition

# Zato - test helpers
from connection_stubs import get_tool_registry, make_gateway_wrapper, make_mcp_handler, run_tools_call, StubConfigManager, \
    StubSQLPoolItem

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def _make_config_manager(pool_item:'StubSQLPoolItem | None'=None) -> 'StubConfigManager':
    """ A config manager with one SQL pool called reporting.
    """

    if pool_item is None:
        pool_item = StubSQLPoolItem('mysql+pymysql', 'db.example.com', 'reports')

    out = StubConfigManager()
    out.sql_pool_store.wrappers['reporting'] = pool_item

    return out

# ################################################################################################################################
# ################################################################################################################################

class SQLToolShape(TestCase):
    """ Tests for the shape of SQL connection tools.
    """

# ################################################################################################################################

    def test_registry_tool(self) -> 'None':
        """ Verifies the tool's name, description and schema.
        """

        config_manager = _make_config_manager()
        wrapper = make_gateway_wrapper(config_manager, sql_connections=['reporting'])

        tool_registry = get_tool_registry(wrapper)
        tools = tool_registry.get_tools()
        self.assertEqual(len(tools), 1)

        tool = tools[0]
        self.assertEqual(tool['name'], 'sql.reporting')
        self.assertEqual(
            tool['description'],
            'Runs SQL through the outgoing connection `reporting` (mysql+pymysql at db.example.com, database reports)')
        self.assertEqual(tool['inputSchema'], definition.input_schema)

        self.assertEqual(definition.input_schema['required'], ['query'])

# ################################################################################################################################
# ################################################################################################################################

class SQLToolInvoke(TestCase):
    """ Tests for invoking SQL connection tools.
    """

# ################################################################################################################################

    def test_invoke_runs_query_with_params(self) -> 'None':
        """ Verifies that the pool's execute receives the statement and its parameters.
        """

        pool_item = StubSQLPoolItem('mysql+pymysql', 'db.example.com', 'reports')
        pool_item.execute_result = [{'customer_id': '123', 'balance': 357}]

        config_manager = _make_config_manager(pool_item)
        wrapper = make_gateway_wrapper(config_manager, sql_connections=['reporting'])

        arguments = {
            'query': 'select * from balances where customer_id = :customer_id',
            'params': {'customer_id': '123'},
        }

        response = wrapper._invoke_service('sql.reporting', arguments)

        self.assertEqual(response, [{'customer_id': '123', 'balance': 357}])

        query, params = pool_item.executed[0]
        self.assertEqual(query, 'select * from balances where customer_id = :customer_id')
        self.assertEqual(params, {'customer_id': '123'})

# ################################################################################################################################
# ################################################################################################################################

class SQLToolsCall(TestCase):
    """ Tests for SQL tools through the full tools/call path.
    """

# ################################################################################################################################

    def test_tools_call_error_is_generic(self) -> 'None':
        """ Verifies that a failing pool produces the generic refusal with isError true.
        """

        class _FailingPoolItem(StubSQLPoolItem):
            def execute(self, query:'str', params:'any_'=None) -> 'any_':
                raise Exception('Table does not exist')

        pool_item = _FailingPoolItem('mysql+pymysql', 'db.example.com', 'reports')

        config_manager = _make_config_manager(pool_item)
        wrapper = make_gateway_wrapper(config_manager, sql_connections=['reporting'])
        handler = make_mcp_handler(wrapper)

        mcp_response = run_tools_call(handler, 'sql.reporting', {'query': 'select 1'})

        result = mcp_response.body['result']
        self.assertTrue(result['isError'])

        text = result['content'][0]['text']
        self.assertEqual(text, 'Bad request')

# ################################################################################################################################
# ################################################################################################################################
