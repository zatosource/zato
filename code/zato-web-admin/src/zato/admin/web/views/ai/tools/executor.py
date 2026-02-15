# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.admin.settings import DATABASES
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.common.odb.api import SQLConnectionPool

if 0:
    from zato.common.typing_ import anydict

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

class EnmasseToolExecutor:
    """ Executes enmasse tools called by the LLM.
    """

    def __init__(self) -> 'None':
        self.session = None

# ################################################################################################################################

    def _get_session(self):
        """ Returns a database session for enmasse operations.
        """
        if self.session:
            return self.session

        db_config = DATABASES.get('default', {})

        engine_type = db_config.get('ENGINE', '')
        if 'postgresql' in engine_type:
            engine = 'postgresql'
        elif 'mysql' in engine_type:
            engine = 'mysql'
        elif 'sqlite' in engine_type:
            engine = 'sqlite'
        else:
            engine = 'postgresql'

        host = db_config.get('HOST', 'localhost')
        port = db_config.get('PORT', 5432)
        db_name = db_config.get('NAME', 'zato')
        username = db_config.get('USER', 'zato')
        password = db_config.get('PASSWORD', '')

        pool = SQLConnectionPool(
            engine,
            host,
            port,
            db_name,
            username,
            password,
            pool_size=1,
            extra=None
        )
        pool.init()

        self.session = pool.session()
        return self.session

# ################################################################################################################################

    def execute_tool(self, tool_name:'str', arguments:'anydict') -> 'anydict':
        """ Executes a single tool and returns the result.
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
            result = self._run_enmasse_import(yaml_config)
            return result

        except Exception:
            error_msg = format_exc()
            logger.warning('Tool execution failed: %s', error_msg)
            return {
                'success': False,
                'error': error_msg
            }

# ################################################################################################################################

    def _run_enmasse_import(self, yaml_config:'anydict') -> 'anydict':
        """ Runs the enmasse import with the given YAML configuration.
        """
        session = self._get_session()

        importer = EnmasseYAMLImporter()
        created, updated = importer.sync_from_yaml(yaml_config, session)

        created_summary = {}
        for obj_type, items in created.items():
            created_summary[obj_type] = len(items)

        updated_summary = {}
        for obj_type, items in updated.items():
            updated_summary[obj_type] = len(items)

        return {
            'success': True,
            'created': created_summary,
            'updated': updated_summary
        }

# ################################################################################################################################

    def execute_multiple_tools(self, tool_calls:'list') -> 'list':
        """ Executes multiple tool calls and returns results for each.
        """
        results = []

        for tool_call in tool_calls:
            tool_name = tool_call.get('name', '')
            arguments = tool_call.get('input', {})
            tool_id = tool_call.get('id', '')

            result = self.execute_tool(tool_name, arguments)
            result['tool_id'] = tool_id
            result['tool_name'] = tool_name
            results.append(result)

        return results

# ################################################################################################################################

    def close(self) -> 'None':
        """ Closes the database session.
        """
        if self.session:
            self.session.close()
            self.session = None

# ################################################################################################################################
# ################################################################################################################################

def execute_enmasse_tool(tool_name:'str', arguments:'anydict') -> 'anydict':
    """ Convenience function to execute a single enmasse tool.
    """
    executor = EnmasseToolExecutor()
    try:
        result = executor.execute_tool(tool_name, arguments)
        return result
    finally:
        executor.close()

# ################################################################################################################################

def execute_enmasse_tools(tool_calls:'list') -> 'list':
    """ Convenience function to execute multiple enmasse tools.
    """
    executor = EnmasseToolExecutor()
    try:
        results = executor.execute_multiple_tools(tool_calls)
        return results
    finally:
        executor.close()

# ################################################################################################################################
# ################################################################################################################################
