# Tool selection

Based on the user's message, determine which Zato enmasse tools are needed. Respond with only a JSON array of tool names from this list:

- create_security (for API keys, basic auth, bearer tokens, NTLM)
- create_channel_rest (for REST API endpoints/channels)
- create_outgoing_rest (for outgoing REST connections)
- create_scheduler (for scheduled jobs)
- create_sql (for SQL database connections)
- create_cache (for cache definitions)
- create_groups (for security groups)
- create_email_smtp (for SMTP email connections)
- create_email_imap (for IMAP email connections)
- create_odoo (for Odoo ERP connections)
- create_elastic_search (for Elasticsearch connections)
- create_confluence (for Confluence connections)
- create_jira (for Jira connections)
- create_ldap (for LDAP connections)
- create_microsoft_365 (for Microsoft 365 connections)
- create_outgoing_soap (for outgoing SOAP connections)
- create_pubsub_topic (for pub/sub topics)
- create_pubsub_subscription (for pub/sub subscriptions)
- create_pubsub_permission (for pub/sub permissions)
- create_channel_openapi (for OpenAPI channel definitions)

If no tools are needed, respond with an empty array: []

Example response: ["create_security", "create_channel_rest"]
