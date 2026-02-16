# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

tool_create_security = {
    'name': 'create_security',
    'description': 'Creates or edits a security definition (API key, basic auth, bearer token, or NTLM) in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Unique name for the security definition'},
            'type': {'type': 'string', 'enum': ['apikey', 'basic_auth', 'bearer_token', 'ntlm'], 'description': 'Type of security definition'},
            'is_active': {'type': 'boolean', 'description': 'Whether the security definition is active', 'default': True},
            'username': {'type': 'string', 'description': 'Username (required for basic_auth, bearer_token, ntlm)'},
            'password': {'type': 'string', 'description': 'Password or API key value'},
            'header': {'type': 'string', 'description': 'Header name for API key (default: X-API-Key)', 'default': 'X-API-Key'},
            'auth_server_url': {'type': 'string', 'description': 'OAuth server URL (for bearer_token type)'},
            'client_id_field': {'type': 'string', 'description': 'Client ID field name (for bearer_token)', 'default': 'client_id'},
            'client_secret_field': {'type': 'string', 'description': 'Client secret field name (for bearer_token)', 'default': 'client_secret'},
            'grant_type': {'type': 'string', 'description': 'OAuth grant type (for bearer_token)', 'default': 'client_credentials'}
        },
        'required': ['name', 'type']
    }
}

tool_create_channel_rest = {
    'name': 'create_channel_rest',
    'description': 'Creates or edits a REST channel (HTTP endpoint) in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Unique name for the REST channel'},
            'url_path': {'type': 'string', 'description': 'URL path for the channel (e.g., /api/v1/customers)'},
            'service': {'type': 'string', 'description': 'Name of the service to invoke'},
            'method': {'type': 'string', 'description': 'HTTP method (GET, POST, PUT, DELETE, PATCH, or empty for any)', 'default': ''},
            'security': {'type': 'string', 'description': 'Name of security definition to use (optional)'},
            'is_active': {'type': 'boolean', 'description': 'Whether the channel is active', 'default': True},
            'data_format': {'type': 'string', 'enum': ['json', 'xml', 'form-data'], 'description': 'Data format', 'default': 'json'},
            'merge_url_params_req': {'type': 'boolean', 'description': 'Merge URL params into request', 'default': True}
        },
        'required': ['name', 'url_path', 'service']
    }
}

tool_create_outgoing_rest = {
    'name': 'create_outgoing_rest',
    'description': 'Creates or edits an outgoing REST connection in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Unique name for the outgoing connection'},
            'host': {'type': 'string', 'description': 'Target host URL (e.g., https://api.example.com)'},
            'url_path': {'type': 'string', 'description': 'URL path (e.g., /api/v1)'},
            'security': {'type': 'string', 'description': 'Name of security definition to use (optional)'},
            'is_active': {'type': 'boolean', 'description': 'Whether the connection is active', 'default': True},
            'data_format': {'type': 'string', 'enum': ['json', 'xml', 'form-data'], 'description': 'Data format', 'default': 'json'},
            'timeout': {'type': 'integer', 'description': 'Connection timeout in seconds', 'default': 60},
            'pool_size': {'type': 'integer', 'description': 'Connection pool size', 'default': 20},
            'ping_method': {'type': 'string', 'description': 'HTTP method for ping', 'default': 'HEAD'},
            'content_type': {'type': 'string', 'description': 'Content-Type header', 'default': 'application/json'}
        },
        'required': ['name', 'host', 'url_path']
    }
}

tool_create_scheduler = {
    'name': 'create_scheduler',
    'description': 'Creates or edits a scheduler job in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Unique name for the scheduler job'},
            'service': {'type': 'string', 'description': 'Name of the service to invoke'},
            'job_type': {'type': 'string', 'enum': ['interval_based', 'one_time', 'cron_style'], 'description': 'Type of scheduler job'},
            'is_active': {'type': 'boolean', 'description': 'Whether the job is active', 'default': True},
            'start_date': {'type': 'string', 'description': 'Start date/time in ISO format'},
            'weeks': {'type': 'integer', 'description': 'Interval in weeks (for interval_based)'},
            'days': {'type': 'integer', 'description': 'Interval in days (for interval_based)'},
            'hours': {'type': 'integer', 'description': 'Interval in hours (for interval_based)'},
            'minutes': {'type': 'integer', 'description': 'Interval in minutes (for interval_based)'},
            'seconds': {'type': 'integer', 'description': 'Interval in seconds (for interval_based)'},
            'repeats': {'type': 'integer', 'description': 'Number of times to repeat (null for infinite)'},
            'cron_definition': {'type': 'string', 'description': 'Cron expression (for cron_style)'},
            'extra': {'type': 'string', 'description': 'Extra data to pass to the service (JSON string)'}
        },
        'required': ['name', 'service', 'job_type']
    }
}

tool_create_sql = {
    'name': 'create_sql',
    'description': 'Creates or edits an outgoing SQL connection in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Unique name for the SQL connection'},
            'engine': {'type': 'string', 'enum': ['postgresql', 'mysql', 'oracle', 'mssql', 'sqlite'], 'description': 'Database engine'},
            'host': {'type': 'string', 'description': 'Database host'},
            'port': {'type': 'integer', 'description': 'Database port'},
            'db_name': {'type': 'string', 'description': 'Database name'},
            'username': {'type': 'string', 'description': 'Database username'},
            'password': {'type': 'string', 'description': 'Database password'},
            'is_active': {'type': 'boolean', 'description': 'Whether the connection is active', 'default': True},
            'pool_size': {'type': 'integer', 'description': 'Connection pool size', 'default': 1},
            'extra': {'type': 'string', 'description': 'Extra connection parameters'}
        },
        'required': ['name', 'engine', 'host', 'db_name', 'username']
    }
}

tool_create_cache = {
    'name': 'create_cache',
    'description': 'Creates or edits a built-in cache in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Unique name for the cache'},
            'is_active': {'type': 'boolean', 'description': 'Whether the cache is active', 'default': True},
            'is_default': {'type': 'boolean', 'description': 'Whether this is the default cache', 'default': False},
            'max_size': {'type': 'integer', 'description': 'Maximum number of items in cache', 'default': 10000},
            'max_item_size': {'type': 'integer', 'description': 'Maximum size of a single item in bytes', 'default': 10000},
            'extend_expiry_on_get': {'type': 'boolean', 'description': 'Extend expiry when item is accessed', 'default': False},
            'extend_expiry_on_set': {'type': 'boolean', 'description': 'Extend expiry when item is updated', 'default': False},
            'sync_method': {'type': 'string', 'enum': ['in-background', 'immediately'], 'description': 'How to sync cache across servers', 'default': 'in-background'},
            'persistent_storage': {'type': 'string', 'description': 'Name of SQL connection for persistence (optional)'}
        },
        'required': ['name']
    }
}

tool_create_groups = {
    'name': 'create_groups',
    'description': 'Creates or edits a security group in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Unique name for the group'},
            'is_active': {'type': 'boolean', 'description': 'Whether the group is active', 'default': True}
        },
        'required': ['name']
    }
}

tool_create_email_smtp = {
    'name': 'create_email_smtp',
    'description': 'Creates or edits an SMTP email connection in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Unique name for the SMTP connection'},
            'host': {'type': 'string', 'description': 'SMTP server host'},
            'port': {'type': 'integer', 'description': 'SMTP server port', 'default': 587},
            'username': {'type': 'string', 'description': 'SMTP username'},
            'password': {'type': 'string', 'description': 'SMTP password'},
            'mode': {'type': 'string', 'enum': ['plain', 'ssl', 'starttls'], 'description': 'Connection mode', 'default': 'starttls'},
            'is_active': {'type': 'boolean', 'description': 'Whether the connection is active', 'default': True},
            'timeout': {'type': 'integer', 'description': 'Connection timeout in seconds', 'default': 300},
            'ping_address': {'type': 'string', 'description': 'Email address to use for ping tests'}
        },
        'required': ['name', 'host', 'username']
    }
}

tool_create_email_imap = {
    'name': 'create_email_imap',
    'description': 'Creates or edits an IMAP email connection in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Unique name for the IMAP connection'},
            'host': {'type': 'string', 'description': 'IMAP server host'},
            'port': {'type': 'integer', 'description': 'IMAP server port', 'default': 993},
            'username': {'type': 'string', 'description': 'IMAP username'},
            'password': {'type': 'string', 'description': 'IMAP password'},
            'mode': {'type': 'string', 'enum': ['plain', 'ssl'], 'description': 'Connection mode', 'default': 'ssl'},
            'is_active': {'type': 'boolean', 'description': 'Whether the connection is active', 'default': True},
            'timeout': {'type': 'integer', 'description': 'Connection timeout in seconds', 'default': 300},
            'get_criteria': {'type': 'string', 'description': 'IMAP search criteria', 'default': 'UNSEEN'}
        },
        'required': ['name', 'host', 'username']
    }
}

tool_create_odoo = {
    'name': 'create_odoo',
    'description': 'Creates or edits an Odoo connection in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Unique name for the Odoo connection'},
            'host': {'type': 'string', 'description': 'Odoo server host'},
            'port': {'type': 'integer', 'description': 'Odoo server port', 'default': 8069},
            'database': {'type': 'string', 'description': 'Odoo database name'},
            'user': {'type': 'string', 'description': 'Odoo username'},
            'password': {'type': 'string', 'description': 'Odoo password or API key'},
            'protocol': {'type': 'string', 'enum': ['http', 'https', 'jsonrpc', 'jsonrpcs'], 'description': 'Protocol to use', 'default': 'jsonrpcs'},
            'is_active': {'type': 'boolean', 'description': 'Whether the connection is active', 'default': True},
            'pool_size': {'type': 'integer', 'description': 'Connection pool size', 'default': 5}
        },
        'required': ['name', 'host', 'database', 'user']
    }
}

tool_create_elastic_search = {
    'name': 'create_elastic_search',
    'description': 'Creates or edits an ElasticSearch connection in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Unique name for the ElasticSearch connection'},
            'hosts': {'type': 'string', 'description': 'Comma-separated list of hosts (e.g., host1:9200,host2:9200)'},
            'is_active': {'type': 'boolean', 'description': 'Whether the connection is active', 'default': True},
            'timeout': {'type': 'integer', 'description': 'Connection timeout in seconds', 'default': 90}
        },
        'required': ['name', 'hosts']
    }
}

tool_create_confluence = {
    'name': 'create_confluence',
    'description': 'Creates or edits a Confluence cloud connection in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Unique name for the Confluence connection'},
            'address': {'type': 'string', 'description': 'Confluence instance URL (e.g., https://yoursite.atlassian.net/wiki)'},
            'username': {'type': 'string', 'description': 'Confluence username (email)'},
            'secret': {'type': 'string', 'description': 'API token'},
            'is_active': {'type': 'boolean', 'description': 'Whether the connection is active', 'default': True}
        },
        'required': ['name', 'address', 'username', 'secret']
    }
}

tool_create_jira = {
    'name': 'create_jira',
    'description': 'Creates or edits a Jira cloud connection in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Unique name for the Jira connection'},
            'address': {'type': 'string', 'description': 'Jira instance URL (e.g., https://yoursite.atlassian.net)'},
            'username': {'type': 'string', 'description': 'Jira username (email)'},
            'secret': {'type': 'string', 'description': 'API token'},
            'is_active': {'type': 'boolean', 'description': 'Whether the connection is active', 'default': True}
        },
        'required': ['name', 'address', 'username', 'secret']
    }
}

tool_create_ldap = {
    'name': 'create_ldap',
    'description': 'Creates or edits an LDAP connection in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Unique name for the LDAP connection'},
            'server_list': {'type': 'string', 'description': 'Comma-separated list of LDAP servers'},
            'username': {'type': 'string', 'description': 'Bind DN (e.g., cn=admin,dc=example,dc=com)'},
            'secret': {'type': 'string', 'description': 'Bind password'},
            'is_active': {'type': 'boolean', 'description': 'Whether the connection is active', 'default': True},
            'connect_timeout': {'type': 'integer', 'description': 'Connection timeout in seconds', 'default': 10},
            'use_tls': {'type': 'boolean', 'description': 'Use TLS', 'default': True},
            'pool_size': {'type': 'integer', 'description': 'Connection pool size', 'default': 5}
        },
        'required': ['name', 'server_list', 'username', 'secret']
    }
}

tool_create_microsoft_365 = {
    'name': 'create_microsoft_365',
    'description': 'Creates or edits a Microsoft 365 connection in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Unique name for the Microsoft 365 connection'},
            'tenant_id': {'type': 'string', 'description': 'Azure AD tenant ID'},
            'client_id': {'type': 'string', 'description': 'Application (client) ID'},
            'secret': {'type': 'string', 'description': 'Client secret'},
            'is_active': {'type': 'boolean', 'description': 'Whether the connection is active', 'default': True},
            'scopes': {'type': 'string', 'description': 'OAuth scopes (comma-separated)', 'default': 'https://graph.microsoft.com/.default'}
        },
        'required': ['name', 'tenant_id', 'client_id', 'secret']
    }
}

tool_create_outgoing_soap = {
    'name': 'create_outgoing_soap',
    'description': 'Creates or edits an outgoing SOAP connection in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Unique name for the SOAP connection'},
            'host': {'type': 'string', 'description': 'Target host URL'},
            'url_path': {'type': 'string', 'description': 'URL path to the SOAP endpoint'},
            'soap_action': {'type': 'string', 'description': 'SOAP action'},
            'soap_version': {'type': 'string', 'enum': ['1.1', '1.2'], 'description': 'SOAP version', 'default': '1.1'},
            'security': {'type': 'string', 'description': 'Name of security definition to use (optional)'},
            'is_active': {'type': 'boolean', 'description': 'Whether the connection is active', 'default': True},
            'timeout': {'type': 'integer', 'description': 'Connection timeout in seconds', 'default': 60},
            'pool_size': {'type': 'integer', 'description': 'Connection pool size', 'default': 20}
        },
        'required': ['name', 'host', 'url_path', 'soap_action']
    }
}

tool_create_pubsub_topic = {
    'name': 'create_pubsub_topic',
    'description': 'Creates or edits a Pub/Sub topic in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Unique name for the topic (e.g., /my/topic)'},
            'is_active': {'type': 'boolean', 'description': 'Whether the topic is active', 'default': True},
            'is_api_sub_allowed': {'type': 'boolean', 'description': 'Allow API subscriptions', 'default': True},
            'max_depth_gd': {'type': 'integer', 'description': 'Max depth for guaranteed delivery', 'default': 10000},
            'max_depth_non_gd': {'type': 'integer', 'description': 'Max depth for non-guaranteed delivery', 'default': 10000},
            'depth_check_freq': {'type': 'integer', 'description': 'Depth check frequency in seconds', 'default': 5}
        },
        'required': ['name']
    }
}

tool_create_pubsub_subscription = {
    'name': 'create_pubsub_subscription',
    'description': 'Creates or edits a Pub/Sub subscription in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'topic_name': {'type': 'string', 'description': 'Name of the topic to subscribe to'},
            'endpoint_name': {'type': 'string', 'description': 'Name of the endpoint (subscriber)'},
            'is_active': {'type': 'boolean', 'description': 'Whether the subscription is active', 'default': True},
            'delivery_method': {'type': 'string', 'enum': ['notify', 'pull'], 'description': 'How messages are delivered', 'default': 'notify'},
            'delivery_batch_size': {'type': 'integer', 'description': 'Number of messages per delivery batch', 'default': 500}
        },
        'required': ['topic_name', 'endpoint_name']
    }
}

tool_create_pubsub_permission = {
    'name': 'create_pubsub_permission',
    'description': 'Creates or edits a Pub/Sub permission in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Unique name for the permission'},
            'topic_name': {'type': 'string', 'description': 'Name of the topic'},
            'client_name': {'type': 'string', 'description': 'Name of the client (security definition)'},
            'can_publish': {'type': 'boolean', 'description': 'Allow publishing', 'default': True},
            'can_subscribe': {'type': 'boolean', 'description': 'Allow subscribing', 'default': True}
        },
        'required': ['name', 'topic_name', 'client_name']
    }
}

tool_create_channel_openapi = {
    'name': 'create_channel_openapi',
    'description': 'Creates or edits an OpenAPI channel in Zato via enmasse.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Unique name for the OpenAPI channel'},
            'spec': {'type': 'string', 'description': 'OpenAPI specification (JSON or YAML string)'},
            'is_active': {'type': 'boolean', 'description': 'Whether the channel is active', 'default': True},
            'security': {'type': 'string', 'description': 'Name of security definition to use (optional)'}
        },
        'required': ['name', 'spec']
    }
}

tool_deploy_service = {
    'name': 'deploy_service',
    'description': 'Deploys Zato services to the server by writing Python files. Use for both creating new services and updating existing ones - hot-deployment handles both cases automatically.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'files': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'file_path': {'type': 'string', 'description': 'File path relative to services root (e.g., my_service.py or crm/customer.py)'},
                        'code': {'type': 'string', 'description': 'Python source code for the service'}
                    },
                    'required': ['file_path', 'code']
                },
                'description': 'List of files to deploy'
            }
        },
        'required': ['files']
    }
}

# ################################################################################################################################
# ################################################################################################################################

all_create_tools = {
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
    'deploy_service': tool_deploy_service,
}

# ################################################################################################################################
# ################################################################################################################################
