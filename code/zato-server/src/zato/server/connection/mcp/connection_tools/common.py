# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# Zato
from zato.common.util.file_system import fs_safe_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_, stranydict

    callable_ = callable_

# ################################################################################################################################
# ################################################################################################################################

# What separates a tool's group prefix from the connection part of its name
Tool_Name_Separator = '.'

# ################################################################################################################################
# ################################################################################################################################

class GroupDefinition(NamedTuple):
    """ Describes one group of connections a gateway can expose as MCP tools.
    """

    # The group's own key, e.g. 'rest' - what the registry stores in tool targets
    group: 'str'

    # The opaque-config key under which a gateway lists this group's connections
    config_key: 'str'

    # What every tool name of this group starts with
    tool_prefix: 'str'

    # Returns the config dict the group's connection names resolve in, given a ConfigManager
    get_config_dict: 'callable_'

    # The JSON schema every tool of this group advertises as its input
    input_schema: 'stranydict'

    # Returns a tool's description, given the connection's name and its config item
    build_description: 'callable_'

    # Invokes the connection behind a tool, given a CID, the config item and the call arguments
    invoke: 'callable_'

# ################################################################################################################################
# ################################################################################################################################

def build_tool_name(tool_prefix:'str', connection_name:'str') -> 'str':
    """ Returns the MCP tool name of a connection - the group's prefix plus the connection's
    filesystem-safe name, the same transformation RESTFacade applies to attribute lookups.
    """

    safe_name = fs_safe_name(connection_name)

    out = f'{tool_prefix}{Tool_Name_Separator}{safe_name}'
    return out

# ################################################################################################################################
# ################################################################################################################################
