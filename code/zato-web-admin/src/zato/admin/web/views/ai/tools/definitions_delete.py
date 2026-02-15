# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

tool_delete_security = {
    'name': 'delete_security',
    'description': 'Deletes a security definition (API key, basic auth, bearer token, or NTLM) by name.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Name of the security definition to delete'},
            'type': {'type': 'string', 'enum': ['apikey', 'basic_auth', 'bearer_token', 'ntlm'], 'description': 'Type of security definition'}
        },
        'required': ['name', 'type']
    }
}

tool_delete_channel_rest = {
    'name': 'delete_channel_rest',
    'description': 'Deletes a REST channel (HTTP endpoint) by name.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Name of the REST channel to delete'}
        },
        'required': ['name']
    }
}

tool_delete_outgoing_rest = {
    'name': 'delete_outgoing_rest',
    'description': 'Deletes an outgoing REST connection by name.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Name of the outgoing REST connection to delete'}
        },
        'required': ['name']
    }
}

tool_delete_scheduler = {
    'name': 'delete_scheduler',
    'description': 'Deletes a scheduler job by name.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Name of the scheduler job to delete'}
        },
        'required': ['name']
    }
}

tool_delete_sql = {
    'name': 'delete_sql',
    'description': 'Deletes an outgoing SQL connection by name.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Name of the SQL connection to delete'}
        },
        'required': ['name']
    }
}

tool_delete_cache = {
    'name': 'delete_cache',
    'description': 'Deletes a built-in cache by name.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Name of the cache to delete'}
        },
        'required': ['name']
    }
}

tool_delete_groups = {
    'name': 'delete_groups',
    'description': 'Deletes a security group by name.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Name of the group to delete'}
        },
        'required': ['name']
    }
}

tool_delete_email_smtp = {
    'name': 'delete_email_smtp',
    'description': 'Deletes an SMTP email connection by name.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Name of the SMTP connection to delete'}
        },
        'required': ['name']
    }
}

tool_delete_email_imap = {
    'name': 'delete_email_imap',
    'description': 'Deletes an IMAP email connection by name.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Name of the IMAP connection to delete'}
        },
        'required': ['name']
    }
}

tool_delete_odoo = {
    'name': 'delete_odoo',
    'description': 'Deletes an Odoo connection by name.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Name of the Odoo connection to delete'}
        },
        'required': ['name']
    }
}

tool_delete_elastic_search = {
    'name': 'delete_elastic_search',
    'description': 'Deletes an ElasticSearch connection by name.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Name of the ElasticSearch connection to delete'}
        },
        'required': ['name']
    }
}

tool_delete_confluence = {
    'name': 'delete_confluence',
    'description': 'Deletes a Confluence cloud connection by name.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Name of the Confluence connection to delete'}
        },
        'required': ['name']
    }
}

tool_delete_jira = {
    'name': 'delete_jira',
    'description': 'Deletes a Jira cloud connection by name.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Name of the Jira connection to delete'}
        },
        'required': ['name']
    }
}

tool_delete_ldap = {
    'name': 'delete_ldap',
    'description': 'Deletes an LDAP connection by name.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Name of the LDAP connection to delete'}
        },
        'required': ['name']
    }
}

tool_delete_microsoft_365 = {
    'name': 'delete_microsoft_365',
    'description': 'Deletes a Microsoft 365 connection by name.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Name of the Microsoft 365 connection to delete'}
        },
        'required': ['name']
    }
}

tool_delete_outgoing_soap = {
    'name': 'delete_outgoing_soap',
    'description': 'Deletes an outgoing SOAP connection by name.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Name of the SOAP connection to delete'}
        },
        'required': ['name']
    }
}

tool_delete_pubsub_topic = {
    'name': 'delete_pubsub_topic',
    'description': 'Deletes a Pub/Sub topic by name.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Name of the topic to delete'}
        },
        'required': ['name']
    }
}

tool_delete_pubsub_subscription = {
    'name': 'delete_pubsub_subscription',
    'description': 'Deletes a Pub/Sub subscription by subscription key.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'sub_key': {'type': 'string', 'description': 'Subscription key of the subscription to delete'}
        },
        'required': ['sub_key']
    }
}

tool_delete_pubsub_permission = {
    'name': 'delete_pubsub_permission',
    'description': 'Deletes a Pub/Sub permission by name.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Name of the permission to delete'}
        },
        'required': ['name']
    }
}

tool_delete_channel_openapi = {
    'name': 'delete_channel_openapi',
    'description': 'Deletes an OpenAPI channel by name.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Name of the OpenAPI channel to delete'}
        },
        'required': ['name']
    }
}

# ################################################################################################################################
# ################################################################################################################################

all_delete_tools = {
    'delete_security': tool_delete_security,
    'delete_channel_rest': tool_delete_channel_rest,
    'delete_outgoing_rest': tool_delete_outgoing_rest,
    'delete_scheduler': tool_delete_scheduler,
    'delete_sql': tool_delete_sql,
    'delete_cache': tool_delete_cache,
    'delete_groups': tool_delete_groups,
    'delete_email_smtp': tool_delete_email_smtp,
    'delete_email_imap': tool_delete_email_imap,
    'delete_odoo': tool_delete_odoo,
    'delete_elastic_search': tool_delete_elastic_search,
    'delete_confluence': tool_delete_confluence,
    'delete_jira': tool_delete_jira,
    'delete_ldap': tool_delete_ldap,
    'delete_microsoft_365': tool_delete_microsoft_365,
    'delete_outgoing_soap': tool_delete_outgoing_soap,
    'delete_pubsub_topic': tool_delete_pubsub_topic,
    'delete_pubsub_subscription': tool_delete_pubsub_subscription,
    'delete_pubsub_permission': tool_delete_pubsub_permission,
    'delete_channel_openapi': tool_delete_channel_openapi,
}

# ################################################################################################################################
# ################################################################################################################################
