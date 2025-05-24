# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class _object_type:
    Cache = 'cache'
    Confluence = 'confluence'
    Channel_AMQP = 'channel_amqp'
    Channel_REST = 'channel_rest'
    Channel_WebSockets = 'channel_websockets'
    Email_IMAP = 'email_imap'
    Email_SMTP = 'email_smtp'
    Jira = 'jira'
    LDAP = 'ldap'
    Microsoft_365 = 'cloud_microsoft_365'
    Odoo = 'odoo'
    Outgoing_AMQP = 'outgoing_amqp'
    Outgoing_REST = 'outgoing_rest'
    Outgoing_SOAP = 'outgoing_soap'
    Outgoing_WebSockets = 'outgoing_websockets'
    Search_ElasticSearch = 'elastic_search'
    SOAP = 'soap'
    SQL  = 'sql'
    Scheduler = 'scheduler'
    Security = 'security'

# ################################################################################################################################
# ################################################################################################################################

_object_alias = {}
_object_alias[_object_type.Channel_REST] = 'channel_plain_http'
_object_alias[_object_type.Confluence] = 'zato_generic_connection:cloud-microsoft-365'
_object_alias[_object_type.Jira] = 'zato_generic_connection:cloud-jira'
_object_alias[_object_type.LDAP] = 'outgoing_ldap'
_object_alias[_object_type.Outgoing_SOAP] = 'outconn_soap'
_object_alias[_object_type.Security] = ['def_sec', 'security_name']
_object_alias[_object_type.SQL] = 'outconn_sql'

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    ObjectType  = _object_type
    ObjectAlias = _object_alias

# ################################################################################################################################
# ################################################################################################################################
