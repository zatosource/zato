# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

tool_create_security = {
    'name': 'create_security',
    'description': 'Creates or edits a security definition (API key, basic auth, bearer token, or NTLM) in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'description': 'Unique name for the security definition'
            },
            'type': {
                'type': 'string',
                'enum': ['apikey', 'basic_auth', 'bearer_token', 'ntlm'],
                'description': 'Type of security definition'
            },
            'is_active': {
                'type': 'boolean',
                'description': 'Whether the security definition is active',
                'default': True
            },
            'username': {
                'type': 'string',
                'description': 'Username (required for basic_auth, bearer_token, ntlm)'
            },
            'password': {
                'type': 'string',
                'description': 'Password or API key value'
            },
            'header': {
                'type': 'string',
                'description': 'Header name for API key (default: X-API-Key)',
                'default': 'X-API-Key'
            },
            'auth_server_url': {
                'type': 'string',
                'description': 'OAuth server URL (for bearer_token type)'
            },
            'client_id_field': {
                'type': 'string',
                'description': 'Client ID field name (for bearer_token)',
                'default': 'client_id'
            },
            'client_secret_field': {
                'type': 'string',
                'description': 'Client secret field name (for bearer_token)',
                'default': 'client_secret'
            },
            'grant_type': {
                'type': 'string',
                'description': 'OAuth grant type (for bearer_token)',
                'default': 'client_credentials'
            }
        },
        'required': ['name', 'type']
    }
}

# ################################################################################################################################

tool_create_channel_rest = {
    'name': 'create_channel_rest',
    'description': 'Creates or edits a REST channel (HTTP endpoint) in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'description': 'Unique name for the REST channel'
            },
            'url_path': {
                'type': 'string',
                'description': 'URL path for the channel (e.g., /api/v1/customers)'
            },
            'service': {
                'type': 'string',
                'description': 'Name of the service to invoke'
            },
            'method': {
                'type': 'string',
                'description': 'HTTP method (GET, POST, PUT, DELETE, PATCH, or empty for any)',
                'default': ''
            },
            'security': {
                'type': 'string',
                'description': 'Name of security definition to use (optional)'
            },
            'groups': {
                'type': 'array',
                'items': {'type': 'string'},
                'description': 'List of security group names (optional)'
            },
            'is_active': {
                'type': 'boolean',
                'description': 'Whether the channel is active',
                'default': True
            },
            'data_format': {
                'type': 'string',
                'enum': ['json', 'xml', 'form', ''],
                'description': 'Expected data format',
                'default': 'json'
            }
        },
        'required': ['name', 'url_path', 'service']
    }
}

# ################################################################################################################################

tool_create_outgoing_rest = {
    'name': 'create_outgoing_rest',
    'description': 'Creates or edits an outgoing REST connection via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'description': 'Unique name for the outgoing connection'
            },
            'host': {
                'type': 'string',
                'description': 'Target host URL (e.g., https://api.example.com)'
            },
            'url_path': {
                'type': 'string',
                'description': 'URL path to append to host',
                'default': '/'
            },
            'security': {
                'type': 'string',
                'description': 'Name of security definition to use (optional)'
            },
            'is_active': {
                'type': 'boolean',
                'description': 'Whether the connection is active',
                'default': True
            },
            'ping_method': {
                'type': 'string',
                'description': 'HTTP method for ping checks',
                'default': 'GET'
            },
            'pool_size': {
                'type': 'integer',
                'description': 'Connection pool size',
                'default': 20
            },
            'timeout': {
                'type': 'integer',
                'description': 'Request timeout in seconds',
                'default': 60
            },
            'data_format': {
                'type': 'string',
                'enum': ['json', 'xml', 'form', ''],
                'description': 'Data format for requests'
            },
            'validate_tls': {
                'type': 'boolean',
                'description': 'Whether to validate TLS certificates',
                'default': True
            }
        },
        'required': ['name', 'host']
    }
}

# ################################################################################################################################

tool_create_scheduler = {
    'name': 'create_scheduler',
    'description': 'Creates or edits a scheduler job via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'description': 'Unique name for the scheduler job'
            },
            'service': {
                'type': 'string',
                'description': 'Name of the service to invoke'
            },
            'job_type': {
                'type': 'string',
                'enum': ['interval_based'],
                'description': 'Type of scheduler job',
                'default': 'interval_based'
            },
            'start_date': {
                'type': 'string',
                'description': 'Start date/time in ISO format (e.g., 2025-01-01T00:00:00)'
            },
            'is_active': {
                'type': 'boolean',
                'description': 'Whether the job is active',
                'default': True
            },
            'weeks': {
                'type': 'integer',
                'description': 'Interval in weeks',
                'default': 0
            },
            'days': {
                'type': 'integer',
                'description': 'Interval in days',
                'default': 0
            },
            'hours': {
                'type': 'integer',
                'description': 'Interval in hours',
                'default': 0
            },
            'minutes': {
                'type': 'integer',
                'description': 'Interval in minutes',
                'default': 0
            },
            'seconds': {
                'type': 'integer',
                'description': 'Interval in seconds',
                'default': 0
            },
            'repeats': {
                'type': 'integer',
                'description': 'Number of times to repeat (0 for infinite)',
                'default': 0
            },
            'extra': {
                'type': 'string',
                'description': 'Extra data to pass to the service (JSON string)'
            }
        },
        'required': ['name', 'service', 'start_date']
    }
}

# ################################################################################################################################

tool_create_sql = {
    'name': 'create_sql',
    'description': 'Creates or edits an SQL connection pool via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'description': 'Unique name for the SQL connection'
            },
            'type': {
                'type': 'string',
                'enum': ['postgresql', 'mysql', 'oracle', 'mssql', 'sqlite'],
                'description': 'Database type'
            },
            'host': {
                'type': 'string',
                'description': 'Database host'
            },
            'port': {
                'type': 'integer',
                'description': 'Database port'
            },
            'db_name': {
                'type': 'string',
                'description': 'Database name'
            },
            'username': {
                'type': 'string',
                'description': 'Database username'
            },
            'password': {
                'type': 'string',
                'description': 'Database password'
            },
            'pool_size': {
                'type': 'integer',
                'description': 'Connection pool size',
                'default': 5
            },
            'is_active': {
                'type': 'boolean',
                'description': 'Whether the connection is active',
                'default': True
            },
            'extra': {
                'type': 'string',
                'description': 'Extra connection parameters'
            }
        },
        'required': ['name', 'type', 'host', 'port', 'db_name', 'username']
    }
}

# ################################################################################################################################

tool_create_cache = {
    'name': 'create_cache',
    'description': 'Creates or edits a cache definition via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'description': 'Unique name for the cache'
            },
            'is_active': {
                'type': 'boolean',
                'description': 'Whether the cache is active',
                'default': True
            },
            'is_default': {
                'type': 'boolean',
                'description': 'Whether this is the default cache',
                'default': False
            },
            'max_size': {
                'type': 'integer',
                'description': 'Maximum number of items in cache',
                'default': 10000
            },
            'max_item_size': {
                'type': 'integer',
                'description': 'Maximum size of a single item in bytes',
                'default': 1000000
            },
            'extend_expiry_on_get': {
                'type': 'boolean',
                'description': 'Extend expiry when item is retrieved',
                'default': True
            },
            'extend_expiry_on_set': {
                'type': 'boolean',
                'description': 'Extend expiry when item is updated',
                'default': False
            },
            'sync_method': {
                'type': 'string',
                'enum': ['in-background', 'immediately'],
                'description': 'How to sync cache to persistent storage',
                'default': 'in-background'
            },
            'persistent_storage': {
                'type': 'string',
                'enum': ['sqlite', 'none'],
                'description': 'Persistent storage backend',
                'default': 'sqlite'
            }
        },
        'required': ['name']
    }
}

# ################################################################################################################################

tool_create_groups = {
    'name': 'create_groups',
    'description': 'Creates or edits a security group via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'description': 'Unique name for the security group'
            },
            'members': {
                'type': 'array',
                'items': {'type': 'string'},
                'description': 'List of security definition names to include in the group'
            }
        },
        'required': ['name']
    }
}

# ################################################################################################################################

tool_create_email_smtp = {
    'name': 'create_email_smtp',
    'description': 'Creates or edits an SMTP email connection via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'description': 'Unique name for the SMTP connection'
            },
            'host': {
                'type': 'string',
                'description': 'SMTP server host'
            },
            'port': {
                'type': 'integer',
                'description': 'SMTP server port',
                'default': 587
            },
            'username': {
                'type': 'string',
                'description': 'SMTP username'
            },
            'password': {
                'type': 'string',
                'description': 'SMTP password'
            },
            'mode': {
                'type': 'string',
                'enum': ['plain', 'ssl', 'starttls'],
                'description': 'Connection mode',
                'default': 'starttls'
            },
            'is_active': {
                'type': 'boolean',
                'description': 'Whether the connection is active',
                'default': True
            },
            'timeout': {
                'type': 'integer',
                'description': 'Connection timeout in seconds',
                'default': 300
            },
            'ping_address': {
                'type': 'string',
                'description': 'Email address for ping checks'
            }
        },
        'required': ['name', 'host', 'username']
    }
}

# ################################################################################################################################

tool_create_email_imap = {
    'name': 'create_email_imap',
    'description': 'Creates or edits an IMAP email connection via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'description': 'Unique name for the IMAP connection'
            },
            'host': {
                'type': 'string',
                'description': 'IMAP server host'
            },
            'port': {
                'type': 'integer',
                'description': 'IMAP server port',
                'default': 993
            },
            'username': {
                'type': 'string',
                'description': 'IMAP username'
            },
            'password': {
                'type': 'string',
                'description': 'IMAP password'
            },
            'mode': {
                'type': 'string',
                'enum': ['plain', 'ssl'],
                'description': 'Connection mode',
                'default': 'ssl'
            },
            'is_active': {
                'type': 'boolean',
                'description': 'Whether the connection is active',
                'default': True
            },
            'timeout': {
                'type': 'integer',
                'description': 'Connection timeout in seconds',
                'default': 300
            }
        },
        'required': ['name', 'host', 'username']
    }
}

# ################################################################################################################################

tool_create_odoo = {
    'name': 'create_odoo',
    'description': 'Creates or edits an Odoo ERP connection via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'description': 'Unique name for the Odoo connection'
            },
            'host': {
                'type': 'string',
                'description': 'Odoo server host URL'
            },
            'database': {
                'type': 'string',
                'description': 'Odoo database name'
            },
            'user': {
                'type': 'string',
                'description': 'Odoo username'
            },
            'password': {
                'type': 'string',
                'description': 'Odoo password or API key'
            },
            'is_active': {
                'type': 'boolean',
                'description': 'Whether the connection is active',
                'default': True
            },
            'pool_size': {
                'type': 'integer',
                'description': 'Connection pool size',
                'default': 5
            },
            'protocol': {
                'type': 'string',
                'enum': ['xmlrpc', 'jsonrpc'],
                'description': 'Protocol to use',
                'default': 'xmlrpc'
            }
        },
        'required': ['name', 'host', 'database', 'user']
    }
}

# ################################################################################################################################

tool_create_elastic_search = {
    'name': 'create_elastic_search',
    'description': 'Creates or edits an ElasticSearch connection via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'description': 'Unique name for the ElasticSearch connection'
            },
            'hosts': {
                'type': 'string',
                'description': 'Comma-separated list of ElasticSearch hosts'
            },
            'is_active': {
                'type': 'boolean',
                'description': 'Whether the connection is active',
                'default': True
            },
            'timeout': {
                'type': 'integer',
                'description': 'Connection timeout in seconds',
                'default': 90
            }
        },
        'required': ['name', 'hosts']
    }
}

# ################################################################################################################################

tool_create_confluence = {
    'name': 'create_confluence',
    'description': 'Creates or edits a Confluence connection via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'description': 'Unique name for the Confluence connection'
            },
            'address': {
                'type': 'string',
                'description': 'Confluence server URL'
            },
            'username': {
                'type': 'string',
                'description': 'Confluence username'
            },
            'password': {
                'type': 'string',
                'description': 'Confluence password or API token'
            },
            'is_active': {
                'type': 'boolean',
                'description': 'Whether the connection is active',
                'default': True
            },
            'is_cloud': {
                'type': 'boolean',
                'description': 'Whether this is Confluence Cloud',
                'default': True
            }
        },
        'required': ['name', 'address', 'username']
    }
}

# ################################################################################################################################

tool_create_jira = {
    'name': 'create_jira',
    'description': 'Creates or edits a Jira connection via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'description': 'Unique name for the Jira connection'
            },
            'address': {
                'type': 'string',
                'description': 'Jira server URL'
            },
            'username': {
                'type': 'string',
                'description': 'Jira username'
            },
            'password': {
                'type': 'string',
                'description': 'Jira password or API token'
            },
            'is_active': {
                'type': 'boolean',
                'description': 'Whether the connection is active',
                'default': True
            },
            'is_cloud': {
                'type': 'boolean',
                'description': 'Whether this is Jira Cloud',
                'default': True
            }
        },
        'required': ['name', 'address', 'username']
    }
}

# ################################################################################################################################

tool_create_ldap = {
    'name': 'create_ldap',
    'description': 'Creates or edits an LDAP connection via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'description': 'Unique name for the LDAP connection'
            },
            'server_list': {
                'type': 'string',
                'description': 'Comma-separated list of LDAP servers'
            },
            'username': {
                'type': 'string',
                'description': 'Bind DN or username'
            },
            'password': {
                'type': 'string',
                'description': 'Bind password'
            },
            'is_active': {
                'type': 'boolean',
                'description': 'Whether the connection is active',
                'default': True
            },
            'use_tls': {
                'type': 'boolean',
                'description': 'Whether to use TLS',
                'default': True
            },
            'pool_size': {
                'type': 'integer',
                'description': 'Connection pool size',
                'default': 5
            }
        },
        'required': ['name', 'server_list', 'username']
    }
}

# ################################################################################################################################

tool_create_microsoft_365 = {
    'name': 'create_microsoft_365',
    'description': 'Creates or edits a Microsoft 365 connection via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'description': 'Unique name for the Microsoft 365 connection'
            },
            'tenant_id': {
                'type': 'string',
                'description': 'Azure AD tenant ID'
            },
            'client_id': {
                'type': 'string',
                'description': 'Azure AD application (client) ID'
            },
            'client_secret': {
                'type': 'string',
                'description': 'Azure AD client secret'
            },
            'is_active': {
                'type': 'boolean',
                'description': 'Whether the connection is active',
                'default': True
            },
            'scopes': {
                'type': 'string',
                'description': 'OAuth scopes (space-separated)',
                'default': 'https://graph.microsoft.com/.default'
            }
        },
        'required': ['name', 'tenant_id', 'client_id']
    }
}

# ################################################################################################################################

tool_create_outgoing_soap = {
    'name': 'create_outgoing_soap',
    'description': 'Creates or edits an outgoing SOAP connection via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'description': 'Unique name for the outgoing SOAP connection'
            },
            'host': {
                'type': 'string',
                'description': 'Target host URL'
            },
            'url_path': {
                'type': 'string',
                'description': 'URL path to the SOAP endpoint'
            },
            'soap_action': {
                'type': 'string',
                'description': 'SOAP action header value'
            },
            'soap_version': {
                'type': 'string',
                'enum': ['1.1', '1.2'],
                'description': 'SOAP version',
                'default': '1.1'
            },
            'security': {
                'type': 'string',
                'description': 'Name of security definition to use (optional)'
            },
            'is_active': {
                'type': 'boolean',
                'description': 'Whether the connection is active',
                'default': True
            },
            'pool_size': {
                'type': 'integer',
                'description': 'Connection pool size',
                'default': 20
            },
            'timeout': {
                'type': 'integer',
                'description': 'Request timeout in seconds',
                'default': 60
            }
        },
        'required': ['name', 'host', 'url_path']
    }
}

# ################################################################################################################################

tool_create_pubsub_topic = {
    'name': 'create_pubsub_topic',
    'description': 'Creates or edits a publish/subscribe topic via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'description': 'Unique name for the topic (e.g., /my/topic)'
            },
            'description': {
                'type': 'string',
                'description': 'Description of the topic'
            },
            'is_active': {
                'type': 'boolean',
                'description': 'Whether the topic is active',
                'default': True
            }
        },
        'required': ['name']
    }
}

# ################################################################################################################################

tool_create_pubsub_subscription = {
    'name': 'create_pubsub_subscription',
    'description': 'Creates or edits a topic subscription via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'topic_name': {
                'type': 'string',
                'description': 'Name of the topic to subscribe to'
            },
            'endpoint_name': {
                'type': 'string',
                'description': 'Name of the endpoint (security definition)'
            },
            'is_active': {
                'type': 'boolean',
                'description': 'Whether the subscription is active',
                'default': True
            },
            'delivery_method': {
                'type': 'string',
                'enum': ['notify', 'pull'],
                'description': 'How messages are delivered',
                'default': 'notify'
            }
        },
        'required': ['topic_name', 'endpoint_name']
    }
}

# ################################################################################################################################

tool_create_pubsub_permission = {
    'name': 'create_pubsub_permission',
    'description': 'Creates or edits a topic permission via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'topic_name': {
                'type': 'string',
                'description': 'Name of the topic'
            },
            'endpoint_name': {
                'type': 'string',
                'description': 'Name of the endpoint (security definition)'
            },
            'permission': {
                'type': 'string',
                'enum': ['publish', 'subscribe', 'publish-subscribe'],
                'description': 'Permission type'
            }
        },
        'required': ['topic_name', 'endpoint_name', 'permission']
    }
}

# ################################################################################################################################

tool_create_channel_openapi = {
    'name': 'create_channel_openapi',
    'description': 'Creates or edits REST channels from OpenAPI spec via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'description': 'Unique name for the OpenAPI channel group'
            },
            'spec': {
                'type': 'string',
                'description': 'OpenAPI specification content (JSON or YAML)'
            },
            'service_prefix': {
                'type': 'string',
                'description': 'Prefix for generated service names'
            },
            'security': {
                'type': 'string',
                'description': 'Name of security definition to use for all channels'
            },
            'is_active': {
                'type': 'boolean',
                'description': 'Whether the channels are active',
                'default': True
            }
        },
        'required': ['name', 'spec']
    }
}

# ################################################################################################################################
# ################################################################################################################################

_all_tools = {
    'create_security': tool_create_security,
    'create_channel_rest': tool_create_channel_rest,
    'create_outgoing_rest': tool_create_outgoing_rest,
    'create_scheduler': tool_create_scheduler,
    'create_sql': tool_create_sql,
    'create_cache': tool_create_cache,
    'create_groups': tool_create_groups,
    'create_email_smtp': tool_create_email_smtp,
    'create_email_imap': tool_create_email_imap,
    'create_odoo': tool_create_odoo,
    'create_elastic_search': tool_create_elastic_search,
    'create_confluence': tool_create_confluence,
    'create_jira': tool_create_jira,
    'create_ldap': tool_create_ldap,
    'create_microsoft_365': tool_create_microsoft_365,
    'create_outgoing_soap': tool_create_outgoing_soap,
    'create_pubsub_topic': tool_create_pubsub_topic,
    'create_pubsub_subscription': tool_create_pubsub_subscription,
    'create_pubsub_permission': tool_create_pubsub_permission,
    'create_channel_openapi': tool_create_channel_openapi,
}

# ################################################################################################################################
# ################################################################################################################################

def get_all_tools() -> 'anylist':
    """ Returns all available enmasse tools for LLM integration.
    """
    return list(_all_tools.values())

# ################################################################################################################################

def get_tools_by_name(tool_names:'anylist') -> 'anylist':
    """ Returns only the tools matching the given names.
    """
    out = []
    for name in tool_names:
        tool = _all_tools.get(name)
        if tool:
            out.append(tool)
    return out

# ################################################################################################################################

def get_all_tool_names() -> 'anylist':
    """ Returns all available tool names.
    """
    return list(_all_tools.keys())

# ################################################################################################################################
# ################################################################################################################################
