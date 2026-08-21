# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.connection.mcp.connection_tools import confluence, es, microsoft, odoo, rest, sap, soap, sql
from zato.server.connection.mcp.connection_tools.common import build_tool_name, GroupDefinition

# ################################################################################################################################
# ################################################################################################################################

if 0:
    group_definition_dict = dict[str, GroupDefinition]

# ################################################################################################################################
# ################################################################################################################################

# Re-exported for callers that import them from here.
build_tool_name = build_tool_name
GroupDefinition = GroupDefinition

# ################################################################################################################################
# ################################################################################################################################

# Every group of connections a gateway can expose as MCP tools, keyed by the group's own key -
# adding a connection group means adding one entry here and nothing else in the shared code.
group_registry:'group_definition_dict' = {
    rest.definition.group: rest.definition,
    soap.definition.group: soap.definition,
    sql.definition.group: sql.definition,
    microsoft.microsoft_365_spec.group: microsoft.microsoft_365_spec,
    microsoft.teams_spec.group: microsoft.teams_spec,
    microsoft.fabric_spec.group: microsoft.fabric_spec,
    microsoft.power_automate_spec.group: microsoft.power_automate_spec,
    sap.definition.group: sap.definition,
    confluence.definition.group: confluence.definition,
    odoo.definition.group: odoo.definition,
    es.definition.group: es.definition,
}

# ################################################################################################################################
# ################################################################################################################################
