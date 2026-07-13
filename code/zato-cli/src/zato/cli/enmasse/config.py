# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class _object_type:

    Security = 'security'                         #

    Channel_AS4 = 'channel_as4'                   #
    Channel_REST = 'channel_rest'                 #
    Channel_SOAP = 'channel_soap'                 #
    Outgoing_AS2 = 'outgoing_as2'                 #
    Outgoing_AS4 = 'outgoing_as4'                 #
    Outgoing_REST = 'outgoing_rest'               #
    Outgoing_SOAP = 'outgoing_soap'               #

    Odoo = 'odoo'                                 #
    SQL  = 'sql'                                  #
    Scheduler = 'scheduler'                       #

    Email_IMAP = 'email_imap'                     #
    Email_SMTP = 'email_smtp'                     #

    Groups = 'groups'                             #

    LDAP = 'ldap'                                 #
    MongoDB = 'mongodb'                           #
    OData = 'odata'                               #
    SAP = 'sap'                                   #
    SFTP = 'sftp'                                 #
    SMB = 'smb'                                   #
    Confluence = 'confluence'                     #
    Jira = 'jira'                                 #
    Microsoft_Cloud = 'microsoft_cloud'           #
    Microsoft_Fabric = 'cloud_microsoft_fabric'   #
    Microsoft_Power_Automate = 'cloud_microsoft_power_automate' #
    Search_ElasticSearch = 'elastic_search'       #

    # Channel_AMQP = 'channel_amqp'               #
    # Channel_WebSockets = 'channel_websockets'   #
    # Outgoing_AMQP = 'outgoing_amqp'             #
    # Outgoing_WebSockets = 'outgoing_websockets' #
    # PubSub_Topic = 'pubsub_topic'               #

# ################################################################################################################################
# ################################################################################################################################

_object_alias = {}

_object_alias[_object_type.Channel_REST] = 'channel_plain_http'
_object_alias[_object_type.Confluence] = 'zato_generic_connection:cloud-confluence'
_object_alias[_object_type.Jira] = 'zato_generic_connection:cloud-jira'
_object_alias[_object_type.LDAP] = 'outgoing_ldap'
_object_alias[_object_type.MongoDB] = 'outgoing_mongodb'
_object_alias[_object_type.OData] = 'outgoing_odata'
_object_alias[_object_type.SAP] = 'outgoing_sap'
_object_alias[_object_type.Microsoft_Cloud] = ['zato_generic_connection:cloud-confluence', 'cloud-microsoft-365']
_object_alias[_object_type.Odoo] = 'outconn_odoo'
_object_alias[_object_type.Outgoing_SOAP] = 'outconn_soap'
_object_alias[_object_type.Search_ElasticSearch] = 'outgoing_elastic_search'
_object_alias[_object_type.Security] = ['def_sec', 'security_name']
_object_alias[_object_type.SFTP] = 'outgoing_sftp'
_object_alias[_object_type.SMB] = 'outgoing_smb'
_object_alias[_object_type.SQL] = 'outconn_sql'

# ################################################################################################################################
# ################################################################################################################################

_attr_alias = {}

_attr_alias[_object_type.SQL] = {
    'type':'engine'
}

# ################################################################################################################################
# ################################################################################################################################

_attr_default = {}

_attr_default[_object_type.Confluence] = {
    'is_active': True,
    'is_cloud': True,
    'api_version': 'v1'
}

_attr_default[_object_type.Email_IMAP] = {
    'is_active': True,
    'timeout': 30,
    'debug_level': 0,
    'mode': 'ssl',
    'get_criteria': 'ALL'
}

_attr_default[_object_type.Email_SMTP] = {
    'is_active': True,
    'timeout': 30,
    'is_debug': False,
    'mode': 'starttls',
    'ping_address': 'example@example.com'
}

_attr_default[_object_type.Jira] = {
    'is_active': True,
    'is_cloud': True,
    'api_version': 'v2'
}

_attr_default[_object_type.MongoDB] = {
    'is_active': True,
    'server_list': 'localhost:27017',
    'auth_source': 'admin',
    'app_name': 'Zato',
    'pool_size_max': 10,
    'connect_timeout': 10,
    'server_select_timeout': 5
}

_attr_default[_object_type.Search_ElasticSearch] = {
    'is_active': True,
    'address_list': 'http://127.0.0.1:9200',
    'timeout': 90
}

_attr_default[_object_type.Odoo] = {
    'is_active': True,
    'protocol': 'jsonrpc',
    'pool_size': 10
}

_attr_default[_object_type.Scheduler] = {
    'is_active': True,
    'job_type': 'interval_based',
    'weeks': 0,
    'days': 0,
    'hours': 0,
    'minutes': 1,
    'seconds': 0,
    'repeats': 0
}

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # This is always the same
    Cluster_ID = 1
    Initial_Wait_Time = 10
    Missing_Wait_Time = 1
    ignore_missing_includes = False

    ObjectType  = _object_type
    ObjectAlias = _object_alias

# ################################################################################################################################
# ################################################################################################################################
