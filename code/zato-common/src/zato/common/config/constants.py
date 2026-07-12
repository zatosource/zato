# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

# Section names - these match YAML keys exactly.

Security            = 'security'
Groups              = 'groups'
Channel_REST        = 'channel_rest'
Channel_SOAP        = 'channel_soap'
Channel_AMQP        = 'channel_amqp'
Channel_OpenAPI     = 'channel_openapi'
Outgoing_REST       = 'outgoing_rest'
Outgoing_SOAP       = 'outgoing_soap'
Outgoing_AMQP       = 'outgoing_amqp'
Outgoing_FTP        = 'outgoing_ftp'
SQL                 = 'sql'
Odoo                = 'odoo'
Outgoing_SAP        = 'outgoing_sap'
Cache               = 'cache'
Email_SMTP          = 'email_smtp'
Email_IMAP          = 'email_imap'
Scheduler           = 'scheduler'
LDAP                = 'ldap'
Confluence          = 'confluence'
Jira                = 'jira'
Microsoft_Cloud     = 'microsoft_cloud'
Microsoft_Fabric    = 'microsoft_fabric'
Microsoft_Power_Automate = 'microsoft_power_automate'
PubSub_Topic        = 'pubsub_topic'
PubSub_Permission   = 'pubsub_permission'
PubSub_Subscription = 'pubsub_subscription'
Elastic_Search      = 'elastic_search'
Service             = 'service'
Generic_Connection  = 'generic_connection'

# All valid section names.
All_Sections = frozenset([
    Security,
    Groups,
    Channel_REST,
    Channel_SOAP,
    Channel_AMQP,
    Channel_OpenAPI,
    Outgoing_REST,
    Outgoing_SOAP,
    Outgoing_AMQP,
    Outgoing_FTP,
    SQL,
    Odoo,
    Outgoing_SAP,
    Cache,
    Email_SMTP,
    Email_IMAP,
    Scheduler,
    LDAP,
    Confluence,
    Jira,
    Microsoft_Cloud,
    Microsoft_Fabric,
    Microsoft_Power_Automate,
    PubSub_Topic,
    PubSub_Permission,
    PubSub_Subscription,
    Elastic_Search,
    Service,
    Generic_Connection,
])

# Sections whose items are keyed by 'security' rather than 'name'.
Key_By_Security = frozenset([PubSub_Permission, PubSub_Subscription])

# ################################################################################################################################
# ################################################################################################################################
