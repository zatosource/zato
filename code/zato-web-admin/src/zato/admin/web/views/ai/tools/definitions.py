# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.admin.web.views.ai.tools.definitions_create import all_create_tools
from zato.admin.web.views.ai.tools.definitions_delete import all_delete_tools
from zato.admin.web.views.ai.tools.definitions_update import all_update_tools

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

def get_all_tools() -> 'anylist':
    """ Returns all available tools (create, delete, update) for LLM integration.
    """
    all_tools = list(all_create_tools.values()) + list(all_delete_tools.values()) + list(all_update_tools.values())
    return all_tools

# ################################################################################################################################

def get_all_tool_names() -> 'anylist':
    """ Returns all available tool names.
    """
    return list(all_create_tools.keys()) + list(all_delete_tools.keys()) + list(all_update_tools.keys())

# ################################################################################################################################

def get_all_create_tools() -> 'anylist':
    """ Returns all available create tools for LLM integration.
    """
    return list(all_create_tools.values())

# ################################################################################################################################

def get_all_create_tool_names() -> 'anylist':
    """ Returns all available create tool names.
    """
    return list(all_create_tools.keys())

# ################################################################################################################################

def is_create_tool(tool_name:'str') -> 'bool':
    """ Returns True if the tool is a create tool.
    """
    return tool_name in all_create_tools

# ################################################################################################################################

def get_all_delete_tools() -> 'anylist':
    """ Returns all available delete tools for LLM integration.
    """
    return list(all_delete_tools.values())

# ################################################################################################################################

def get_all_delete_tool_names() -> 'anylist':
    """ Returns all available delete tool names.
    """
    return list(all_delete_tools.keys())

# ################################################################################################################################

def is_delete_tool(tool_name:'str') -> 'bool':
    """ Returns True if the tool is a delete tool.
    """
    return tool_name in all_delete_tools

# ################################################################################################################################

def get_all_update_tools() -> 'anylist':
    """ Returns all available update tools for LLM integration.
    """
    return list(all_update_tools.values())

# ################################################################################################################################

def get_all_update_tool_names() -> 'anylist':
    """ Returns all available update tool names.
    """
    return list(all_update_tools.keys())

# ################################################################################################################################

def is_update_tool(tool_name:'str') -> 'bool':
    """ Returns True if the tool is an update tool.
    """
    return tool_name in all_update_tools

# ################################################################################################################################
# ################################################################################################################################
