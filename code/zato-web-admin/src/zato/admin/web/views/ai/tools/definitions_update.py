# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

tool_update_security = {
    'name': 'update_security',
    'description': 'Updates a security definition (API key, basic auth, bearer token, or NTLM) by name. Can rename or modify properties.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Current name of the security definition to update'},
            'type': {'type': 'string', 'enum': ['apikey', 'basic_auth', 'bearer_token', 'ntlm'], 'description': 'Type of security definition'},
            'new_name': {'type': 'string', 'description': 'New name for the security definition (for rename)'},
            'is_active': {'type': 'boolean', 'description': 'Whether the security definition is active'},
            'username': {'type': 'string', 'description': 'Username for the security definition'}
        },
        'required': ['name', 'type']
    }
}

tool_update_channel_rest = {
    'name': 'update_channel_rest',
    'description': 'Updates a REST channel by name. Can rename or modify properties.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Current name of the REST channel to update'},
            'new_name': {'type': 'string', 'description': 'New name for the channel (for rename)'},
            'url_path': {'type': 'string', 'description': 'New URL path for the channel'},
            'service': {'type': 'string', 'description': 'New service name to invoke'},
            'is_active': {'type': 'boolean', 'description': 'Whether the channel is active'}
        },
        'required': ['name']
    }
}

tool_update_outgoing_rest = {
    'name': 'update_outgoing_rest',
    'description': 'Updates an outgoing REST connection by name. Can rename or modify properties.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Current name of the outgoing REST connection to update'},
            'new_name': {'type': 'string', 'description': 'New name for the connection (for rename)'},
            'host': {'type': 'string', 'description': 'New host URL'},
            'url_path': {'type': 'string', 'description': 'New URL path'},
            'is_active': {'type': 'boolean', 'description': 'Whether the connection is active'}
        },
        'required': ['name']
    }
}

tool_update_scheduler = {
    'name': 'update_scheduler',
    'description': 'Updates a scheduler job by name. Can rename or modify properties.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Current name of the scheduler job to update'},
            'new_name': {'type': 'string', 'description': 'New name for the job (for rename)'},
            'service': {'type': 'string', 'description': 'New service name to invoke'},
            'is_active': {'type': 'boolean', 'description': 'Whether the job is active'}
        },
        'required': ['name']
    }
}

tool_update_sql = {
    'name': 'update_sql',
    'description': 'Updates an outgoing SQL connection by name. Can rename or modify properties.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Current name of the SQL connection to update'},
            'new_name': {'type': 'string', 'description': 'New name for the connection (for rename)'},
            'is_active': {'type': 'boolean', 'description': 'Whether the connection is active'}
        },
        'required': ['name']
    }
}

tool_update_cache = {
    'name': 'update_cache',
    'description': 'Updates a built-in cache by name. Can rename or modify properties.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Current name of the cache to update'},
            'new_name': {'type': 'string', 'description': 'New name for the cache (for rename)'},
            'is_active': {'type': 'boolean', 'description': 'Whether the cache is active'}
        },
        'required': ['name']
    }
}

tool_update_pubsub_topic = {
    'name': 'update_pubsub_topic',
    'description': 'Updates a Pub/Sub topic by name. Can rename or modify properties.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Current name of the topic to update'},
            'new_name': {'type': 'string', 'description': 'New name for the topic (for rename)'},
            'is_active': {'type': 'boolean', 'description': 'Whether the topic is active'}
        },
        'required': ['name']
    }
}

tool_update_confluence = {
    'name': 'update_confluence',
    'description': 'Updates a Confluence cloud connection by name. Can rename or modify properties.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Current name of the Confluence connection to update'},
            'new_name': {'type': 'string', 'description': 'New name for the connection (for rename)'},
            'is_active': {'type': 'boolean', 'description': 'Whether the connection is active'}
        },
        'required': ['name']
    }
}

tool_update_jira = {
    'name': 'update_jira',
    'description': 'Updates a Jira cloud connection by name. Can rename or modify properties.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Current name of the Jira connection to update'},
            'new_name': {'type': 'string', 'description': 'New name for the connection (for rename)'},
            'is_active': {'type': 'boolean', 'description': 'Whether the connection is active'}
        },
        'required': ['name']
    }
}

# ################################################################################################################################
# ################################################################################################################################

all_update_tools = {
    'update_security': tool_update_security,
    'update_channel_rest': tool_update_channel_rest,
    'update_outgoing_rest': tool_update_outgoing_rest,
    'update_scheduler': tool_update_scheduler,
    'update_sql': tool_update_sql,
    'update_cache': tool_update_cache,
    'update_pubsub_topic': tool_update_pubsub_topic,
    'update_confluence': tool_update_confluence,
    'update_jira': tool_update_jira,
}

# ################################################################################################################################
# ################################################################################################################################
