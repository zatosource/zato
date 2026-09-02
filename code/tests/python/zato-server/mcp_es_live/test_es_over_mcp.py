# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile

# Elasticsearch
from elasticsearch import Elasticsearch

# PyYAML
from yaml import safe_load

# Zato - test helpers
from _agent import run_agent
from _client import MCPClient
from conftest import Article_First, Article_Second, Connection_Name, Gateway_Name, Index_Name, Tool_Name
from mcp_connections import harness

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The document the agent indexes and where it lands
Agent_Document_ID = 'article-agent-1'
Agent_Document_Title = 'Observability for integration platforms'

# ################################################################################################################################
# ################################################################################################################################

class TestESToolDiscovery:
    """ The gateway lists the Elasticsearch connection as a tool.
    """

# ################################################################################################################################

    def test_tool_listed(self, zato_server:'anydict') -> 'None':

        tool_names = harness.get_tool_names(zato_server['mcp_url'], zato_server['auth'])

        assert Tool_Name in tool_names, tool_names

# ################################################################################################################################
# ################################################################################################################################

class TestESEnmasseRoundTrip:
    """ The gateway's Elasticsearch allow list survives an export and a reimport.
    """

# ################################################################################################################################

    def test_round_trip(self, zato_server:'anydict') -> 'None':

        environment = zato_server['environment']
        server_directory = environment.server_directory

        export_path = os.path.join(tempfile.gettempdir(), 'zato-mcp-connections-es-export.yaml')

        try:
            # The export brings the gateway back out with its allow list ..
            harness.run_enmasse_export(server_directory, export_path, 'mcp_gateway')

            with open(export_path) as export_file:
                exported = safe_load(export_file.read())

            gateway_by_name = {}

            for gateway in exported['mcp_gateway']:
                gateway_by_name[gateway['name']] = gateway

            gateway = gateway_by_name[Gateway_Name]
            assert gateway['es_connections'] == [Connection_Name], gateway

            # .. the export is a clean input of its own ..
            harness.run_enmasse_import(server_directory, exported)

            # .. and the gateway still lists the tool afterwards.
            tool_names = harness.get_tool_names(zato_server['mcp_url'], zato_server['auth'])
            assert Tool_Name in tool_names, tool_names

        finally:
            if os.path.isfile(export_path):
                os.remove(export_path)

# ################################################################################################################################
# ################################################################################################################################

class TestESAgentEndToEnd:
    """ A real model discovers the Elasticsearch tool through MCP, indexes
    a document with it and searches the real server through it.
    """

# ################################################################################################################################

    def test_agent_indexes_and_searches(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = MCPClient(zato_server['mcp_url'], auth=zato_server['auth'])

        task = (
            f'First index a document into the {Index_Name} index through the Elasticsearch tool - '
            f'the method is index, the index_name is {Index_Name} and the arguments are '
            f'{{"id": "{Agent_Document_ID}", "document": {{"title": "{Agent_Document_Title}"}}}}. '
            f'Then search the same index - the method is search, the index_name is {Index_Name} '
            f'and the arguments are {{"query": {{"match_all": {{}}}}}} - '
            f'and tell me the titles of every document you find.')

        result = run_agent(client, task)

        # The model called the Elasticsearch tool ..
        called_tools = []

        for call in result.tool_calls:
            called_tools.append(call.tool_name)

        assert Tool_Name in called_tools, result.messages

        # .. the document it indexed really is in the server ..
        es_client = Elasticsearch(hosts=[zato_server['es_address']])

        document = es_client.get(index=Index_Name, id=Agent_Document_ID)
        document_source = document['_source']
        assert document_source['title'] == Agent_Document_Title, document.body

        es_client.close()

        # .. and the seeded articles made it into the final answer through the search.
        assert Article_First in result.final_text, result.final_text
        assert Article_Second in result.final_text, result.final_text

# ################################################################################################################################
# ################################################################################################################################
