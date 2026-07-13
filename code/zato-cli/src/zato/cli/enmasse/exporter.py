# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.cli.enmasse.config import ModuleCtx
from zato.cli.enmasse.exporters.email_imap import IMAPExporter
from zato.cli.enmasse.exporters.email_smtp import SMTPExporter
from zato.cli.enmasse.exporters.group import GroupExporter
from zato.cli.enmasse.exporters.odoo import OdooExporter
from zato.cli.enmasse.exporters.scheduler import SchedulerExporter
from zato.cli.enmasse.exporters.security import SecurityExporter
from zato.cli.enmasse.exporters.sql import SQLExporter
from zato.cli.enmasse.exporters.channel_as4 import ChannelAS4Exporter
from zato.cli.enmasse.exporters.channel_rest import ChannelExporter
from zato.cli.enmasse.exporters.channel_soap import ChannelSOAPExporter
from zato.cli.enmasse.exporters.channel_openapi import ChannelOpenAPIExporter
from zato.cli.enmasse.exporters.jira import JiraExporter
from zato.cli.enmasse.exporters.ldap import LDAPExporter
from zato.cli.enmasse.exporters.microsoft_cloud import MicrosoftCloudExporter
from zato.cli.enmasse.exporters.microsoft_fabric import MicrosoftFabricExporter
from zato.cli.enmasse.exporters.microsoft_power_automate import MicrosoftPowerAutomateExporter
from zato.cli.enmasse.exporters.mongodb import MongoDBExporter
from zato.cli.enmasse.exporters.odata import ODataExporter
from zato.cli.enmasse.exporters.sftp import SFTPExporter
from zato.cli.enmasse.exporters.smb import SMBExporter
from zato.cli.enmasse.exporters.confluence import ConfluenceExporter
from zato.cli.enmasse.exporters.channel_hl7_mllp import ChannelHL7MLLPExporter
from zato.cli.enmasse.exporters.outgoing_hl7_mllp import OutgoingHL7MLLPExporter
from zato.cli.enmasse.exporters.es import ElasticSearchExporter
from zato.cli.enmasse.exporters.graphql import OutgoingGraphQLExporter
from zato.cli.enmasse.exporters.ibm_mq import ChannelIBMMQExporter, OutgoingIBMMQExporter
from zato.cli.enmasse.exporters.kafka import ChannelKafkaExporter, OutgoingKafkaExporter
from zato.cli.enmasse.exporters.mcp import ChannelMCPExporter
from zato.cli.enmasse.exporters.as2 import AS2Exporter
from zato.cli.enmasse.exporters.outgoing_as4 import OutgoingAS4Exporter
from zato.cli.enmasse.exporters.outgoing_rest import OutgoingRESTExporter
from zato.cli.enmasse.exporters.outgoing_soap import OutgoingSOAPExporter
from zato.cli.enmasse.exporters.pubsub_topic import PubSubTopicExporter
from zato.cli.enmasse.exporters.pubsub_permission import PubSubPermissionExporter
from zato.cli.enmasse.exporters.pubsub_subscription import PubSubSubscriptionExporter
from zato.common.odb.model import Cluster

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class EnmasseYAMLExporter:
    """ Exports Zato objects to a YAML-compatible dictionary structure.
    """
    def __init__(self) -> 'None':

        # This is always the same
        self.cluster_id = ModuleCtx.Cluster_ID
        self.cluster:'any_' = None # To store the cluster object, similar to importer

        # Initialize exporters
        self.email_imap_exporter = IMAPExporter(self)
        self.email_smtp_exporter = SMTPExporter(self)
        self.group_exporter = GroupExporter(self)
        self.odoo_exporter = OdooExporter(self)
        self.scheduler_exporter = SchedulerExporter(self)
        self.security_exporter = SecurityExporter(self)
        self.sql_exporter = SQLExporter(self)
        self.channel_exporter = ChannelExporter(self)
        self.channel_soap_exporter = ChannelSOAPExporter(self)
        self.channel_as4_exporter = ChannelAS4Exporter(self)
        self.channel_hl7_mllp_exporter = ChannelHL7MLLPExporter(self)
        self.outgoing_hl7_mllp_exporter = OutgoingHL7MLLPExporter(self)
        self.outgoing_graphql_exporter = OutgoingGraphQLExporter(self)
        self.channel_ibm_mq_exporter = ChannelIBMMQExporter(self)
        self.outgoing_ibm_mq_exporter = OutgoingIBMMQExporter(self)
        self.channel_kafka_exporter = ChannelKafkaExporter(self)
        self.channel_mcp_exporter = ChannelMCPExporter(self)
        self.outgoing_kafka_exporter = OutgoingKafkaExporter(self)
        self.jira_exporter = JiraExporter(self)
        self.ldap_exporter = LDAPExporter(self)
        self.mongodb_exporter = MongoDBExporter(self)
        self.odata_exporter = ODataExporter(self, 'odata')
        self.sap_exporter = ODataExporter(self, 'sap')
        self.sftp_exporter = SFTPExporter(self)
        self.smb_exporter = SMBExporter(self)
        self.microsoft_cloud_exporter = MicrosoftCloudExporter(self)
        self.microsoft_fabric_exporter = MicrosoftFabricExporter(self)
        self.microsoft_power_automate_exporter = MicrosoftPowerAutomateExporter(self)
        self.confluence_exporter = ConfluenceExporter(self)
        self.elastic_search_exporter = ElasticSearchExporter(self)
        self.outgoing_rest_exporter = OutgoingRESTExporter(self)
        self.outgoing_soap_exporter = OutgoingSOAPExporter(self)
        self.as2_exporter = AS2Exporter(self)
        self.outgoing_as4_exporter = OutgoingAS4Exporter(self)
        self.pubsub_topic_exporter = PubSubTopicExporter(self)
        self.pubsub_permission_exporter = PubSubPermissionExporter(self)
        self.pubsub_subscription_exporter = PubSubSubscriptionExporter(self)
        self.channel_openapi_exporter = ChannelOpenAPIExporter(self)

# ################################################################################################################################

    def get_cluster(self, session:'SASession') -> 'any_':
        """ Returns the cluster instance, retrieving it from the database if needed.
        """
        if not self.cluster:
            logger.info('Getting cluster by id=%s', self.cluster_id)
            self.cluster = session.query(Cluster).filter(Cluster.id == self.cluster_id).one() # type: ignore
        return self.cluster

# ################################################################################################################################

    def export_odoo(self, session:'SASession') -> 'list':
        """ Exports Odoo connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded if needed by exporter
        odoo_list = self.odoo_exporter.export(session, self.cluster_id)
        return odoo_list

# ################################################################################################################################

    def export_scheduler(self, session:'SASession') -> 'list':
        """ Exports scheduler job definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded if needed by exporter
        scheduler_list = self.scheduler_exporter.export(session, self.cluster_id)
        return scheduler_list

# ################################################################################################################################

    def export_sql(self, session:'SASession') -> 'list':
        """ Exports SQL connection pool definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded if needed by exporter
        sql_list = self.sql_exporter.export(session, self.cluster_id)
        return sql_list

# ################################################################################################################################

    def export_security(self, session:'SASession') -> 'list':
        """ Exports security definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded if needed by exporter
        security_list = self.security_exporter.export(session, self.cluster_id)
        return security_list

# ################################################################################################################################

    def export_email_imap(self, session:'SASession') -> 'list':
        """ Exports email IMAP connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded if needed by exporter
        imap_list = self.email_imap_exporter.export(session, self.cluster_id)
        return imap_list

# ################################################################################################################################

    def export_email_smtp(self, session:'SASession') -> 'list':
        """ Exports email SMTP connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded if needed by exporter
        smtp_list = self.email_smtp_exporter.export(session, self.cluster_id)
        return smtp_list

# ################################################################################################################################

    def export_groups(self, session:'SASession') -> 'list':
        """ Exports security group definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded if needed by exporter
        group_list = self.group_exporter.export(session, self.cluster_id)
        return group_list

# ################################################################################################################################

    def export_channel_rest(self, session:'SASession') -> 'list':
        """ Exports REST Channel definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        channel_list = self.channel_exporter.export(session, self.cluster_id)
        return channel_list

# ################################################################################################################################

    def export_channel_soap(self, session:'SASession') -> 'list':
        """ Exports SOAP channel definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        channel_list = self.channel_soap_exporter.export(session, self.cluster_id)
        return channel_list

# ################################################################################################################################

    def export_channel_hl7_mllp(self, session:'SASession') -> 'list':
        """ Exports HL7 MLLP channel definitions.
        """
        _ = self.get_cluster(session)
        channel_hl7_mllp_list = self.channel_hl7_mllp_exporter.export(session, self.cluster_id)
        return channel_hl7_mllp_list

# ################################################################################################################################

    def export_outgoing_hl7_mllp(self, session:'SASession') -> 'list':
        """ Exports outgoing HL7 MLLP definitions.
        """
        _ = self.get_cluster(session)
        outgoing_hl7_mllp_list = self.outgoing_hl7_mllp_exporter.export(session, self.cluster_id)
        return outgoing_hl7_mllp_list

# ################################################################################################################################

    def export_outgoing_graphql(self, session:'SASession') -> 'list':
        """ Exports GraphQL outgoing definitions.
        """
        _ = self.get_cluster(session)
        outgoing_graphql_list = self.outgoing_graphql_exporter.export(session, self.cluster_id)
        return outgoing_graphql_list

# ################################################################################################################################

    def export_channel_ibm_mq(self, session:'SASession') -> 'list':
        """ Exports IBM MQ channel definitions.
        """
        _ = self.get_cluster(session)
        channel_ibm_mq_list = self.channel_ibm_mq_exporter.export(session, self.cluster_id)
        return channel_ibm_mq_list

# ################################################################################################################################

    def export_outgoing_ibm_mq(self, session:'SASession') -> 'list':
        """ Exports IBM MQ outgoing definitions.
        """
        _ = self.get_cluster(session)
        outgoing_ibm_mq_list = self.outgoing_ibm_mq_exporter.export(session, self.cluster_id)
        return outgoing_ibm_mq_list

# ################################################################################################################################

    def export_channel_kafka(self, session:'SASession') -> 'list':
        """ Exports Kafka channel definitions.
        """
        _ = self.get_cluster(session)
        channel_kafka_list = self.channel_kafka_exporter.export(session, self.cluster_id)
        return channel_kafka_list

# ################################################################################################################################

    def export_channel_mcp(self, session:'SASession') -> 'list':
        """ Exports MCP channel definitions.
        """
        _ = self.get_cluster(session)
        channel_mcp_list = self.channel_mcp_exporter.export(session, self.cluster_id)
        return channel_mcp_list

# ################################################################################################################################

    def export_outgoing_kafka(self, session:'SASession') -> 'list':
        """ Exports Kafka outgoing definitions.
        """
        _ = self.get_cluster(session)
        outgoing_kafka_list = self.outgoing_kafka_exporter.export(session, self.cluster_id)
        return outgoing_kafka_list

# ################################################################################################################################

    def export_outgoing_rest(self, session:'SASession') -> 'list':
        """ Exports outgoing REST connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        outgoing_rest_list = self.outgoing_rest_exporter.export(session, self.cluster_id)
        return outgoing_rest_list

# ################################################################################################################################

    def export_outgoing_soap(self, session:'SASession') -> 'list':
        """ Exports outgoing SOAP connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        outgoing_soap_list = self.outgoing_soap_exporter.export(session, self.cluster_id)
        return outgoing_soap_list

# ################################################################################################################################

    def export_outgoing_as2(self, session:'SASession') -> 'list':
        """ Exports outgoing AS2 connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        outgoing_as2_list = self.as2_exporter.export(session, self.cluster_id)
        return outgoing_as2_list

# ################################################################################################################################

    def export_outgoing_as4(self, session:'SASession') -> 'list':
        """ Exports outgoing AS4 connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        outgoing_as4_list = self.outgoing_as4_exporter.export(session, self.cluster_id)
        return outgoing_as4_list

# ################################################################################################################################

    def export_channel_as4(self, session:'SASession') -> 'list':
        """ Exports AS4 channel definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        channel_as4_list = self.channel_as4_exporter.export(session, self.cluster_id)
        return channel_as4_list

# ################################################################################################################################

    def export_jira(self, session:'SASession') -> 'list':
        """ Exports JIRA connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        jira_list = self.jira_exporter.export(session, self.cluster_id)
        return jira_list

# ################################################################################################################################

    def export_ldap(self, session:'SASession') -> 'list':
        """ Exports LDAP connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        ldap_list = self.ldap_exporter.export(session, self.cluster_id)
        return ldap_list

# ################################################################################################################################

    def export_odata(self, session:'SASession') -> 'list':
        """ Exports OData connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        odata_list = self.odata_exporter.export(session, self.cluster_id)
        return odata_list

# ################################################################################################################################

    def export_sap(self, session:'SASession') -> 'list':
        """ Exports SAP connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        sap_list = self.sap_exporter.export(session, self.cluster_id)
        return sap_list

# ################################################################################################################################

    def export_sftp(self, session:'SASession') -> 'list':
        """ Exports SFTP connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        sftp_list = self.sftp_exporter.export(session, self.cluster_id)
        return sftp_list

# ################################################################################################################################

    def export_smb(self, session:'SASession') -> 'list':
        """ Exports SMB connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        smb_list = self.smb_exporter.export(session, self.cluster_id)
        return smb_list

# ################################################################################################################################

    def export_mongodb(self, session:'SASession') -> 'list':
        """ Exports MongoDB connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        mongodb_list = self.mongodb_exporter.export(session, self.cluster_id)
        return mongodb_list

# ################################################################################################################################

    def export_microsoft_cloud(self, session:'SASession') -> 'list':
        """ Exports Microsoft 365 connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        microsoft_cloud_list = self.microsoft_cloud_exporter.export(session, self.cluster_id)
        return microsoft_cloud_list

# ################################################################################################################################

    def export_microsoft_fabric(self, session:'SASession') -> 'list':
        """ Exports Microsoft Fabric connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        microsoft_fabric_list = self.microsoft_fabric_exporter.export(session, self.cluster_id)
        return microsoft_fabric_list

# ################################################################################################################################

    def export_microsoft_power_automate(self, session:'SASession') -> 'list':
        """ Exports Microsoft Power Automate connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        microsoft_power_automate_list = self.microsoft_power_automate_exporter.export(session, self.cluster_id)
        return microsoft_power_automate_list

# ################################################################################################################################

    def export_confluence(self, session:'SASession') -> 'list':
        """ Exports Confluence connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        confluence_list = self.confluence_exporter.export(session, self.cluster_id)
        return confluence_list

# ################################################################################################################################

    def export_elastic_search(self, session:'SASession') -> 'list':
        """ Exports Elasticsearch connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        elastic_search_list = self.elastic_search_exporter.export(session, self.cluster_id)
        return elastic_search_list

# ################################################################################################################################

    def export_pubsub_topic(self, session:'SASession') -> 'list':
        """ Exports pub/sub topic definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        pubsub_topic_list = self.pubsub_topic_exporter.export(session, self.cluster_id)
        return pubsub_topic_list

# ################################################################################################################################

    def export_pubsub_permission(self, session:'SASession') -> 'list':
        """ Exports pub/sub permission definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        pubsub_permission_list = self.pubsub_permission_exporter.export(session, self.cluster_id)
        return pubsub_permission_list

# ################################################################################################################################

    def export_pubsub_subscription(self, session:'SASession') -> 'list':
        """ Exports pub/sub subscription definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        pubsub_subscription_list = self.pubsub_subscription_exporter.export(session, self.cluster_id)
        return pubsub_subscription_list

# ################################################################################################################################

    def export_channel_openapi(self, session:'SASession') -> 'list':
        """ Exports OpenAPI channel definitions.
        """
        _ = self.get_cluster(session)
        channel_openapi_list = self.channel_openapi_exporter.export(session, self.cluster_id)
        return channel_openapi_list

# ################################################################################################################################

    def export_to_dict(self, session:'SASession') -> 'stranydict':
        """ Exports all configured Zato objects to a dictionary.
            This dictionary can then be serialized to YAML.
        """
        logger.info('Starting export of Zato objects to dictionary format')

        output_dict: 'stranydict' = {}

        # Export Odoo connection definitions
        odoo_defs = self.export_odoo(session)
        if odoo_defs:
            output_dict['odoo'] = odoo_defs

        # Export SQL connection pool definitions
        sql_defs = self.export_sql(session)
        if sql_defs:
            output_dict['sql'] = sql_defs

        # Export scheduler job definitions
        scheduler_defs = self.export_scheduler(session)
        if scheduler_defs:
            output_dict['scheduler'] = scheduler_defs

        # Export security definitions
        security_defs = self.export_security(session)
        if security_defs:
            output_dict['security'] = security_defs

        # Export email IMAP connection definitions
        email_imap_defs = self.export_email_imap(session)
        if email_imap_defs:
            output_dict['email_imap'] = email_imap_defs

        # Export email SMTP connection definitions
        email_smtp_defs = self.export_email_smtp(session)
        if email_smtp_defs:
            output_dict['email_smtp'] = email_smtp_defs

        # Export security group definitions
        group_defs = self.export_groups(session)
        if group_defs:
            output_dict['groups'] = group_defs

        # Export REST Channel definitions
        channel_rest_defs = self.export_channel_rest(session)
        if channel_rest_defs:
            output_dict['channel_rest'] = channel_rest_defs

        # Export SOAP channel definitions
        channel_soap_defs = self.export_channel_soap(session)
        if channel_soap_defs:
            output_dict['channel_soap'] = channel_soap_defs

        # Export AS4 channel definitions
        channel_as4_defs = self.export_channel_as4(session)
        if channel_as4_defs:
            output_dict['channel_as4'] = channel_as4_defs

        # Export HL7 MLLP channel definitions
        channel_hl7_mllp_defs = self.export_channel_hl7_mllp(session)
        if channel_hl7_mllp_defs:
            output_dict['channel_hl7_mllp'] = channel_hl7_mllp_defs

        # Export outgoing HL7 MLLP definitions
        outgoing_hl7_mllp_defs = self.export_outgoing_hl7_mllp(session)
        if outgoing_hl7_mllp_defs:
            output_dict['outgoing_hl7_mllp'] = outgoing_hl7_mllp_defs

        # Export IBM MQ channel definitions
        channel_ibm_mq_defs = self.export_channel_ibm_mq(session)
        if channel_ibm_mq_defs:
            output_dict['channel_ibm_mq'] = channel_ibm_mq_defs

        # Export IBM MQ outgoing definitions
        outgoing_ibm_mq_defs = self.export_outgoing_ibm_mq(session)
        if outgoing_ibm_mq_defs:
            output_dict['outgoing_ibm_mq'] = outgoing_ibm_mq_defs

        # Export Kafka channel definitions
        channel_kafka_defs = self.export_channel_kafka(session)
        if channel_kafka_defs:
            output_dict['channel_kafka'] = channel_kafka_defs

        # Export MCP channel definitions
        channel_mcp_defs = self.export_channel_mcp(session)
        if channel_mcp_defs:
            output_dict['channel_mcp'] = channel_mcp_defs

        # Export GraphQL outgoing definitions
        outgoing_graphql_defs = self.export_outgoing_graphql(session)
        if outgoing_graphql_defs:
            output_dict['outgoing_graphql'] = outgoing_graphql_defs

        # Export Kafka outgoing definitions
        outgoing_kafka_defs = self.export_outgoing_kafka(session)
        if outgoing_kafka_defs:
            output_dict['outgoing_kafka'] = outgoing_kafka_defs

        # Export outgoing REST connection definitions
        outgoing_rest_defs = self.export_outgoing_rest(session)
        if outgoing_rest_defs:
            output_dict['outgoing_rest'] = outgoing_rest_defs

        # Export outgoing SOAP connection definitions
        outgoing_soap_defs = self.export_outgoing_soap(session)
        if outgoing_soap_defs:
            output_dict['outgoing_soap'] = outgoing_soap_defs

        # Export outgoing AS2 connection definitions
        outgoing_as2_defs = self.export_outgoing_as2(session)
        if outgoing_as2_defs:
            output_dict['outgoing_as2'] = outgoing_as2_defs

        # Export outgoing AS4 connection definitions
        outgoing_as4_defs = self.export_outgoing_as4(session)
        if outgoing_as4_defs:
            output_dict['outgoing_as4'] = outgoing_as4_defs

        # Export JIRA connection definitions
        jira_defs = self.export_jira(session)
        if jira_defs:
            output_dict['jira'] = jira_defs

        # Export LDAP connection definitions
        ldap_defs = self.export_ldap(session)
        if ldap_defs:
            output_dict['ldap'] = ldap_defs

        # Export OData connection definitions
        odata_defs = self.export_odata(session)
        if odata_defs:
            output_dict['odata'] = odata_defs

        # Export SAP connection definitions
        sap_defs = self.export_sap(session)
        if sap_defs:
            output_dict['sap'] = sap_defs

        # Export SFTP connection definitions
        sftp_defs = self.export_sftp(session)
        if sftp_defs:
            output_dict['sftp'] = sftp_defs

        # Export SMB connection definitions
        smb_defs = self.export_smb(session)
        if smb_defs:
            output_dict['smb'] = smb_defs

        # Export MongoDB connection definitions
        mongodb_defs = self.export_mongodb(session)
        if mongodb_defs:
            output_dict['mongodb'] = mongodb_defs

        # Export Microsoft 365 connection definitions
        microsoft_cloud_defs = self.export_microsoft_cloud(session)
        if microsoft_cloud_defs:
            output_dict['microsoft_cloud'] = microsoft_cloud_defs

        # Export Microsoft Fabric connection definitions
        microsoft_fabric_defs = self.export_microsoft_fabric(session)
        if microsoft_fabric_defs:
            output_dict['microsoft_fabric'] = microsoft_fabric_defs

        # Export Microsoft Power Automate connection definitions
        microsoft_power_automate_defs = self.export_microsoft_power_automate(session)
        if microsoft_power_automate_defs:
            output_dict['microsoft_power_automate'] = microsoft_power_automate_defs

        # Export Confluence connection definitions
        confluence_defs = self.export_confluence(session)
        if confluence_defs:
            output_dict['confluence'] = confluence_defs

        # Export ElasticSearch connection definitions
        elastic_search_defs = self.export_elastic_search(session)
        if elastic_search_defs:
            output_dict['elastic_search'] = elastic_search_defs

        # Export pub/sub topic definitions
        pubsub_topic_defs = self.export_pubsub_topic(session)
        if pubsub_topic_defs:
            output_dict['pubsub_topic'] = pubsub_topic_defs

        # Export pub/sub permission definitions
        pubsub_permission_defs = self.export_pubsub_permission(session)
        if pubsub_permission_defs:
            output_dict['pubsub_permission'] = pubsub_permission_defs

        # Export pub/sub subscription definitions
        pubsub_subscription_defs = self.export_pubsub_subscription(session)
        if pubsub_subscription_defs:
            output_dict['pubsub_subscription'] = pubsub_subscription_defs

        # Export OpenAPI channel definitions
        channel_openapi_defs = self.export_channel_openapi(session)
        if channel_openapi_defs:
            output_dict['channel_openapi'] = channel_openapi_defs

        logger.info('Successfully exported objects to dictionary format: %s', output_dict)
        return output_dict

# ################################################################################################################################
# ################################################################################################################################
