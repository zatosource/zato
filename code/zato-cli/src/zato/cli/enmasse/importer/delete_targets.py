# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# This module is the registry of enmasse deletions - for each top-level section it knows the field that identifies
# an item, the rows an item resolves to, the admin service that deletes such a row and the order the sections are
# deleted in. DeleteSync in importer/delete.py runs the deletions this module resolves.

# stdlib
import logging
from dataclasses import dataclass

# Zato
from zato.cli.enmasse.config import ModuleCtx
from zato.cli.enmasse.importers.custom import custom_key_to_connection_type
from zato.common.api import AMQP_Subtype_Azure_Service_Bus, AMQP_Subtype_Plain, Audit_Config, CONNECTION, GENERIC, Groups, \
    On_Prem_Gateway, Quota_Tiers, SEC_DEF_TYPE, URL_TYPE
from zato.common.odb.model import ChannelAMQP, GenericConn, GenericObject, HTTPSOAP, IMAP, Job, OutgoingAMQP, OutgoingOdoo, \
    PubSubPermission, PubSubSubscription, PubSubSubscriptionTopic, PubSubTopic, SecurityBase, SMTP, SQLConnectionPool
from zato.common.odb.query import channel_amqp_list, out_amqp_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anylist, strlist, strset

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The key that marks an item for deletion
Should_Delete_Key = 'should_delete'

# The fields that identify an item - every section uses the name, except the two pub/sub sections keyed by security
Key_Field_Name     = 'name'
Key_Field_Security = 'security'

# The sections whose items are configuration of objects that cannot be deleted
Section_Alert_Rules         = 'alert_rules'
Section_Alert_Notifications = 'alert_notifications'

# The section whose items name their own section through a type field
Section_Generic_Connection = 'zato_generic_connection'

# The services that delete the rows of each section
Service_HTTP_SOAP      = 'zato.http-soap.delete'
Service_Generic        = 'zato.generic.connection.delete'
Service_Groups         = 'zato.groups.delete'
Service_Quota_Tier     = 'zato.security.tier.delete'
Service_On_Prem        = 'zato.on-prem-gateway.delete'
Service_Scheduler      = 'zato.scheduler.job.delete'
Service_SQL            = 'zato.outgoing.sql.delete'
Service_SMTP           = 'zato.email.smtp.delete'
Service_IMAP           = 'zato.email.imap.delete'
Service_Odoo           = 'zato.outgoing.odoo.delete'
Service_Channel_AMQP   = 'zato.channel.amqp.delete'
Service_Outgoing_AMQP  = 'zato.outgoing.amqp.delete'
Service_Topic          = 'zato.pubsub.topic.delete'
Service_Permission     = 'zato.pubsub.permission.delete'
Service_Subscription   = 'zato.pubsub.subscription.delete'

# The service that deletes a security definition, by the type the row is stored under
security_services = {
    SEC_DEF_TYPE.BASIC_AUTH: 'zato.security.basic-auth.delete',
    SEC_DEF_TYPE.APIKEY:     'zato.security.apikey.delete',
    SEC_DEF_TYPE.OAUTH:      'zato.security.oauth.delete',
    SEC_DEF_TYPE.NTLM:       'zato.security.ntlm.delete',
    SEC_DEF_TYPE.MTLS:       'zato.security.mtls.delete',
    SEC_DEF_TYPE.SPNEGO:     'zato.security.spnego.delete',
    SEC_DEF_TYPE.WSS:        'zato.security.wss.delete',
}

# A row with no delete service is removed in the enmasse session
No_Service = ''

# ################################################################################################################################
# ################################################################################################################################

# What a section may also be called in a file, keyed by the alias
section_aliases = {
    'outconn_sql':      'sql',
    'outgoing_ldap':    'ldap',
    'outgoing_odata':   'odata',
    'outgoing_sap':     'sap',
    'outgoing_sftp':    'sftp',
    'outgoing_smb':     'smb',
    'outgoing_ftp':     'ftp',
    'outgoing_mongodb': 'mongodb',
    'outconn_soap':     'outgoing_soap',
    'grpc':             'outgoing_grpc',
}

# The section a zato_generic_connection item belongs to, by its type
generic_type_to_section = {
    GENERIC.CONNECTION.TYPE.CLOUD_JIRA:                     'jira',
    GENERIC.CONNECTION.TYPE.CLOUD_SALESFORCE:               'salesforce',
    GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_365:            'microsoft_cloud',
    GENERIC.CONNECTION.TYPE.CHAT_MICROSOFT_TEAMS:           'microsoft_teams',
    GENERIC.CONNECTION.TYPE.CHAT_SLACK:                     'slack',
    GENERIC.CONNECTION.TYPE.CHAT_DISCORD:                   'discord',
    GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_FABRIC:         'microsoft_fabric',
    GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_POWER_AUTOMATE: 'microsoft_power_automate',
}

# The HTTPSOAP sections, each with the connection and transport its rows are stored under
http_soap_sections = {
    'channel_rest':  (CONNECTION.CHANNEL,  URL_TYPE.PLAIN_HTTP),
    'channel_soap':  (CONNECTION.CHANNEL,  URL_TYPE.SOAP),
    'channel_as4':   (CONNECTION.CHANNEL,  URL_TYPE.AS4),
    'outgoing_rest': (CONNECTION.OUTGOING, URL_TYPE.PLAIN_HTTP),
    'outgoing_soap': (CONNECTION.OUTGOING, URL_TYPE.SOAP),
    'outgoing_as4':  (CONNECTION.OUTGOING, URL_TYPE.AS4),
}

# The generic connection sections, each with the connection type its rows are stored under
generic_sections = {
    'ldap':                     GENERIC.CONNECTION.TYPE.OUTCONN_LDAP,
    'llm':                      GENERIC.CONNECTION.TYPE.OUTCONN_LLM,
    'odata':                    GENERIC.CONNECTION.TYPE.OUTCONN_ODATA,
    'sap':                      GENERIC.CONNECTION.TYPE.OUTCONN_SAP,
    'mongodb':                  GENERIC.CONNECTION.TYPE.OUTCONN_MONGODB,
    'microsoft_cloud':          GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_365,
    'microsoft_fabric':         GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_FABRIC,
    'microsoft_power_automate': GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_POWER_AUTOMATE,
    'microsoft_teams':          GENERIC.CONNECTION.TYPE.CHAT_MICROSOFT_TEAMS,
    'slack':                    GENERIC.CONNECTION.TYPE.CHAT_SLACK,
    'discord':                  GENERIC.CONNECTION.TYPE.CHAT_DISCORD,
    'confluence':               GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE,
    'jira':                     GENERIC.CONNECTION.TYPE.CLOUD_JIRA,
    'salesforce':               GENERIC.CONNECTION.TYPE.CLOUD_SALESFORCE,
    'channel_kafka':            GENERIC.CONNECTION.TYPE.CHANNEL_KAFKA,
    'outgoing_kafka':           GENERIC.CONNECTION.TYPE.OUTCONN_KAFKA,
    'channel_ibm_mq':           GENERIC.CONNECTION.TYPE.CHANNEL_IBM_MQ,
    'outgoing_ibm_mq':          GENERIC.CONNECTION.TYPE.OUTCONN_IBM_MQ,
    'mcp_gateway':              GENERIC.CONNECTION.TYPE.GATEWAY_MCP,
    'rule_engine_api':          GENERIC.CONNECTION.TYPE.GATEWAY_RULE_ENGINE,
    'outgoing_graphql':         GENERIC.CONNECTION.TYPE.OUTCONN_GRAPHQL,
    'outgoing_grpc':            GENERIC.CONNECTION.TYPE.OUTCONN_GRPC,
    'channel_mllp':             GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP,
    'outgoing_mllp':            GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP,
    'outgoing_fhir':            GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR,
    'sftp':                     GENERIC.CONNECTION.TYPE.OUTCONN_SFTP,
    'smb':                      GENERIC.CONNECTION.TYPE.OUTCONN_SMB,
    'ftp':                      GENERIC.CONNECTION.TYPE.OUTCONN_FTP,
    'outgoing_as2':             GENERIC.CONNECTION.TYPE.OUTCONN_AS2,
    'elastic_search':           GENERIC.CONNECTION.TYPE.OUTCONN_ES,
    'channel_openapi':          GENERIC.CONNECTION.TYPE.CHANNEL_OPENAPI,
}

# The sections stored as generic objects - the type, the subtype and the delete service of each
generic_object_sections = {
    'groups':           (Groups.Type.Group_Parent,                 Groups.Type.API_Clients, Service_Groups),
    'quota_tier':       (Quota_Tiers.Type.Quota_Tier,              None,                    Service_Quota_Tier),
    'on_prem_gateway':  (On_Prem_Gateway.Type.On_Prem_Gateway,     None,                    Service_On_Prem),
    'audit_retention':  (Audit_Config.Type.Retention_Policy,       None,                    No_Service),
    'audit_extraction': (Audit_Config.Type.Extraction_Rules,       None,                    No_Service),
}

# The sections stored in a model of their own, each row found by name and cluster
model_sections = {
    'scheduler':    (Job,               Service_Scheduler),
    'sql':          (SQLConnectionPool, Service_SQL),
    'email_smtp':   (SMTP,              Service_SMTP),
    'email_imap':   (IMAP,              Service_IMAP),
    'odoo':         (OutgoingOdoo,      Service_Odoo),
    'pubsub_topic': (PubSubTopic,       Service_Topic),
}

# The AMQP sections - the list query of each, the subtype its rows are marked with and the delete service
amqp_sections = {
    'channel_amqp':               (channel_amqp_list, AMQP_Subtype_Plain,             Service_Channel_AMQP),
    'outgoing_amqp':              (out_amqp_list,     AMQP_Subtype_Plain,             Service_Outgoing_AMQP),
    'channel_azure_service_bus':  (channel_amqp_list, AMQP_Subtype_Azure_Service_Bus, Service_Channel_AMQP),
    'outgoing_azure_service_bus': (out_amqp_list,     AMQP_Subtype_Azure_Service_Bus, Service_Outgoing_AMQP),
}

# The sections keyed by a security definition rather than by a name
security_keyed_sections = ('pubsub_permission', 'pubsub_subscription')

# The sections deleted after the create and update pass - a quota tier is refused while anything references it
deferred_sections = ('quota_tier',)

# The order the sections are deleted in - dependents before what they depend on. Custom connector
# sections are placed after the generic connection sections, which is where the marker stands.
Custom_Sections_Marker = '*custom*'

delete_order = [
    'channel_openapi',
    'pubsub_subscription',
    'pubsub_permission',
    'pubsub_topic',
    'scheduler',
    'mcp_gateway',
    'rule_engine_api',
    'ldap',
    'llm',
    'odata',
    'sap',
    'mongodb',
    'microsoft_cloud',
    'microsoft_fabric',
    'microsoft_power_automate',
    'microsoft_teams',
    'slack',
    'discord',
    'confluence',
    'jira',
    'salesforce',
    'channel_kafka',
    'outgoing_kafka',
    'channel_ibm_mq',
    'outgoing_ibm_mq',
    'outgoing_graphql',
    'outgoing_grpc',
    'channel_mllp',
    'outgoing_mllp',
    'outgoing_fhir',
    'sftp',
    'smb',
    'ftp',
    'outgoing_as2',
    'elastic_search',
    Custom_Sections_Marker,
    'channel_rest',
    'channel_soap',
    'channel_as4',
    'outgoing_rest',
    'outgoing_soap',
    'outgoing_as4',
    'sql',
    'email_imap',
    'email_smtp',
    'odoo',
    'channel_amqp',
    'outgoing_amqp',
    'channel_azure_service_bus',
    'outgoing_azure_service_bus',
    'groups',
    'security',
    'on_prem_gateway',
    'audit_retention',
    'audit_extraction',
]

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DeleteTarget:
    """ One row an item marked for deletion resolves to.
    """
    section: str
    key: str
    id: int
    service: str
    model: 'any_'

# ################################################################################################################################

delete_target_list = list[DeleteTarget]

# ################################################################################################################################
# ################################################################################################################################

def is_custom_section(section:'str') -> 'bool':
    out = section.startswith(ModuleCtx.Custom_Key_Prefix)
    return out

# ################################################################################################################################

def get_key_field(section:'str') -> 'str':
    """ Returns the field that identifies an item of the section.
    """
    if section in security_keyed_sections:
        out = Key_Field_Security
    else:
        out = Key_Field_Name

    return out

# ################################################################################################################################

def is_known_section(section:'str') -> 'bool':
    """ Returns True if items of the section can be deleted.
    """
    is_in_order = section in delete_order
    is_deferred = section in deferred_sections
    out = is_in_order or is_deferred or is_custom_section(section)
    return out

# ################################################################################################################################

def get_delete_order(sections:'strset') -> 'strlist':
    """ Returns the sections present on input in the order they are deleted in, without the deferred ones.
    """
    out:'strlist' = []

    custom_sections = sorted(section for section in sections if is_custom_section(section))

    for section in delete_order:

        # The custom sections stand where the marker is ..
        if section == Custom_Sections_Marker:
            out.extend(custom_sections)

        # .. and every other section is listed if the input has it.
        elif section in sections:
            out.append(section)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _new_target(section:'str', key:'str', row_id:'int', service:'str', model:'any_') -> 'DeleteTarget':
    out = DeleteTarget()
    out.section = section
    out.key = key
    out.id = row_id
    out.service = service
    out.model = model
    return out

# ################################################################################################################################

def _resolve_http_soap(section:'str', key:'str', session:'SASession', cluster_id:'int') -> 'delete_target_list':
    connection, transport = http_soap_sections[section]
    row = session.query(HTTPSOAP).filter_by(name=key, connection=connection, transport=transport, cluster_id=cluster_id).first()

    out:'delete_target_list' = []

    if row is not None:
        out.append(_new_target(section, key, row.id, Service_HTTP_SOAP, HTTPSOAP))

    return out

# ################################################################################################################################

def _resolve_generic(section:'str', key:'str', session:'SASession', cluster_id:'int') -> 'delete_target_list':

    if is_custom_section(section):
        type_ = custom_key_to_connection_type(section)
    else:
        type_ = generic_sections[section]

    row = session.query(GenericConn).filter_by(name=key, type_=type_, cluster_id=cluster_id).first()

    out:'delete_target_list' = []

    if row is not None:
        out.append(_new_target(section, key, row.id, Service_Generic, GenericConn))

    return out

# ################################################################################################################################

def _resolve_generic_object(section:'str', key:'str', session:'SASession', cluster_id:'int') -> 'delete_target_list':
    type_, subtype, service = generic_object_sections[section]

    query = session.query(GenericObject).filter_by(name=key, type_=type_, cluster_id=cluster_id)

    if subtype is not None:
        query = query.filter_by(subtype=subtype)

    row = query.first()

    out:'delete_target_list' = []

    if row is not None:
        out.append(_new_target(section, key, row.id, service, GenericObject))

    return out

# ################################################################################################################################

def _resolve_model(section:'str', key:'str', session:'SASession', cluster_id:'int') -> 'delete_target_list':
    model, service = model_sections[section]
    row = session.query(model).filter_by(name=key, cluster_id=cluster_id).first()

    out:'delete_target_list' = []

    if row is not None:
        out.append(_new_target(section, key, row.id, service, model))

    return out

# ################################################################################################################################

def _resolve_amqp(section:'str', key:'str', session:'SASession', cluster_id:'int') -> 'delete_target_list':
    list_query, subtype, service = amqp_sections[section]

    # The list query narrows the rows down to the subtype, and the row of the name is picked out of them
    rows = list_query(session, cluster_id, subtype, False)

    out:'delete_target_list' = []

    for row in rows:
        if row.name == key:
            model = ChannelAMQP if service == Service_Channel_AMQP else OutgoingAMQP
            out.append(_new_target(section, key, row.id, service, model))

    return out

# ################################################################################################################################

def _resolve_security(section:'str', key:'str', session:'SASession', cluster_id:'int') -> 'delete_target_list':
    row = session.query(SecurityBase).filter_by(name=key, cluster_id=cluster_id).first()

    out:'delete_target_list' = []

    if row is not None:
        out.append(_new_target(section, key, row.id, security_services[row.sec_type], SecurityBase))

    return out

# ################################################################################################################################

def _resolve_security_keyed(section:'str', key:'str', session:'SASession', cluster_id:'int') -> 'delete_target_list':
    """ Resolves the pub/sub rows of the named security definition - every permission row, or the subscription row.
    """
    out:'delete_target_list' = []

    security = session.query(SecurityBase).filter_by(name=key, cluster_id=cluster_id).first()

    if security is None:
        return out

    if section == 'pubsub_permission':
        model = PubSubPermission
        service = Service_Permission
    else:
        model = PubSubSubscription
        service = Service_Subscription

    rows = session.query(model).filter_by(sec_base_id=security.id, cluster_id=cluster_id).all()

    for row in rows:
        out.append(_new_target(section, key, row.id, service, model))

    return out

# ################################################################################################################################

def resolve_targets(section:'str', key:'str', session:'SASession', cluster_id:'int') -> 'delete_target_list':
    """ Returns the rows one item marked for deletion resolves to - an empty list if there is no such object.
    """
    if section in http_soap_sections:
        out = _resolve_http_soap(section, key, session, cluster_id)

    elif section in generic_sections or is_custom_section(section):
        out = _resolve_generic(section, key, session, cluster_id)

    elif section in generic_object_sections:
        out = _resolve_generic_object(section, key, session, cluster_id)

    elif section in model_sections:
        out = _resolve_model(section, key, session, cluster_id)

    elif section in amqp_sections:
        out = _resolve_amqp(section, key, session, cluster_id)

    elif section == 'security':
        out = _resolve_security(section, key, session, cluster_id)

    elif section in security_keyed_sections:
        out = _resolve_security_keyed(section, key, session, cluster_id)

    # .. anything else is a section this registry does not know.
    else:
        raise Exception(f'Section `{section}` does not support `{Should_Delete_Key}`')

    return out

# ################################################################################################################################
# ################################################################################################################################

def _log_dependent(target:'DeleteTarget', kind:'str', name:'str') -> 'None':
    logger.info('Deleting `%s` `%s` also removes or modifies %s `%s`', target.section, target.key, kind, name)

# ################################################################################################################################

def _log_security_dependents(target:'DeleteTarget', session:'SASession', cluster_id:'int') -> 'None':

    # Every HTTPSOAP row that uses the definition goes with it ..
    for row in session.query(HTTPSOAP).filter_by(security_id=target.id, cluster_id=cluster_id).all():
        _log_dependent(target, f'{row.connection} {row.transport}', row.name)

    # .. and so do its pub/sub permissions and subscriptions.
    for row in session.query(PubSubPermission).filter_by(sec_base_id=target.id, cluster_id=cluster_id).all():
        _log_dependent(target, 'pub/sub permission', row.pattern)

    for row in session.query(PubSubSubscription).filter_by(sec_base_id=target.id, cluster_id=cluster_id).all():
        _log_dependent(target, 'pub/sub subscription', row.sub_key)

# ################################################################################################################################

def _log_group_dependents(target:'DeleteTarget', session:'SASession', cluster_id:'int') -> 'None':

    # A channel whose security groups include this one loses it
    channels = session.query(HTTPSOAP).filter_by(connection=CONNECTION.CHANNEL, cluster_id=cluster_id).all()

    for channel in channels:
        opaque = parse_instance_opaque_attr(channel)
        security_groups:'anylist' = opaque.get('security_groups') or []

        if target.id in security_groups:
            _log_dependent(target, 'channel', channel.name)

# ################################################################################################################################

def _log_topic_dependents(target:'DeleteTarget', session:'SASession', cluster_id:'int') -> 'None':

    # A subscription left with no other topic is deleted along with the topic
    links = session.query(PubSubSubscriptionTopic).filter_by(topic_id=target.id, cluster_id=cluster_id).all()

    for link in links:
        topic_count = session.query(PubSubSubscriptionTopic).filter_by(subscription_id=link.subscription_id).count()

        if topic_count == 1:
            _log_dependent(target, 'pub/sub subscription', link.subscription.sub_key)

# ################################################################################################################################

def _log_http_soap_dependents(target:'DeleteTarget', session:'SASession', cluster_id:'int') -> 'None':

    # A subscription pushing to this endpoint goes with it
    for row in session.query(PubSubSubscription).filter_by(rest_push_endpoint_id=target.id, cluster_id=cluster_id).all():
        _log_dependent(target, 'pub/sub subscription', row.sub_key)

# ################################################################################################################################

def log_dependents(target:'DeleteTarget', session:'SASession', cluster_id:'int') -> 'None':
    """ Logs each row the delete service or its cascade removes or modifies along with the target.
    """
    if target.model is SecurityBase:
        _log_security_dependents(target, session, cluster_id)

    elif target.section == 'groups':
        _log_group_dependents(target, session, cluster_id)

    elif target.model is PubSubTopic:
        _log_topic_dependents(target, session, cluster_id)

    elif target.model is HTTPSOAP:
        _log_http_soap_dependents(target, session, cluster_id)

# ################################################################################################################################
# ################################################################################################################################
