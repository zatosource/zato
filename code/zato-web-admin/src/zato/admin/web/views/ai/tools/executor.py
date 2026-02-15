# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# PyYAML
import yaml

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_tool_to_enmasse_key = {
    'create_security': 'security',
    'create_channel_rest': 'channel_rest',
    'create_outgoing_rest': 'outgoing_rest',
    'create_scheduler': 'scheduler',
    'create_sql': 'sql',
    'create_cache': 'cache',
    'create_groups': 'groups',
    'create_email_smtp': 'email_smtp',
    'create_email_imap': 'email_imap',
    'create_odoo': 'odoo',
    'create_elastic_search': 'elastic_search',
    'create_confluence': 'confluence',
    'create_jira': 'jira',
    'create_ldap': 'ldap',
    'create_microsoft_365': 'microsoft_365',
    'create_outgoing_soap': 'outgoing_soap',
    'create_pubsub_topic': 'pubsub_topic',
    'create_pubsub_subscription': 'pubsub_subscription',
    'create_pubsub_permission': 'pubsub_permission',
    'create_channel_openapi': 'channel_openapi',
}

# ################################################################################################################################
# ################################################################################################################################

def execute_enmasse_tool(tool_name:'str', arguments:'anydict', zato_client:'any_') -> 'anydict':
    """ Executes a single enmasse tool via the Zato server invoker.
    """
    logger.info('Executing tool: %s with arguments: %s', tool_name, arguments)

    enmasse_key = _tool_to_enmasse_key.get(tool_name)
    if not enmasse_key:
        return {
            'success': False,
            'error': f'Unknown tool: {tool_name}'
        }

    try:
        yaml_config = {enmasse_key: [arguments]}
        file_content = yaml.dump(yaml_config)

        response = zato_client.invoke('zato.server.invoker', {
            'func_name': 'import_enmasse',
            'file_content': file_content,
            'file_name': 'ai-tool.yaml'
        })

        response_str = str(response.data) if response.data else ''
        is_ok = 'Enmasse OK' in response_str

        if is_ok:
            return {
                'success': True,
                'message': f'Created {enmasse_key} object successfully'
            }
        else:
            return {
                'success': False,
                'error': 'Enmasse import failed'
            }

    except Exception:
        error_msg = format_exc()
        logger.warning('Tool execution failed: %s', error_msg)
        return {
            'success': False,
            'error': error_msg
        }

# ################################################################################################################################
# ################################################################################################################################
