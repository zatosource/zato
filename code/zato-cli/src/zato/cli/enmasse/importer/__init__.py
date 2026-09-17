# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import sys

# Zato
from zato.cli.enmasse.config import ModuleCtx
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.cli.enmasse.importers.channel_rest import ChannelImporter
from zato.cli.enmasse.importers.channel_as4 import ChannelAS4Importer
from zato.cli.enmasse.importers.channel_soap import ChannelSOAPImporter
from zato.cli.enmasse.importers.group import GroupImporter
from zato.cli.enmasse.importers.quota_tier import QuotaTierImporter
from zato.cli.enmasse.importers.alert_config import AlertConfigImporter
from zato.cli.enmasse.importers.audit_retention import AuditRetentionImporter
from zato.cli.enmasse.importers.audit_extraction import AuditExtractionImporter
from zato.cli.enmasse.importers.email_smtp import SMTPImporter
from zato.cli.enmasse.importers.email_imap import IMAPImporter
from zato.cli.enmasse.importers.es import ElasticSearchImporter
from zato.cli.enmasse.importers.ftp import FTPImporter
from zato.cli.enmasse.importers.odoo import OdooImporter
from zato.cli.enmasse.importers.scheduler import SchedulerImporter
from zato.cli.enmasse.importers.sql import SQLImporter
from zato.cli.enmasse.importers.confluence import ConfluenceImporter
from zato.cli.enmasse.importers.jira import JiraImporter
from zato.cli.enmasse.importers.salesforce import SalesforceImporter
from zato.cli.enmasse.importers.channel_mllp import ChannelMLLPImporter
from zato.cli.enmasse.importers.outgoing_mllp import OutgoingMLLPImporter
from zato.cli.enmasse.importers.outgoing_fhir import OutgoingFHIRImporter
from zato.cli.enmasse.importers.graphql import OutgoingGraphQLImporter
from zato.cli.enmasse.importers.grpc import OutgoingGRPCImporter
from zato.cli.enmasse.importers.amqp import ChannelAMQPImporter, OutgoingAMQPImporter
from zato.cli.enmasse.importers.ibm_mq import ChannelIBMMQImporter, OutgoingIBMMQImporter
from zato.cli.enmasse.importers.kafka import ChannelKafkaImporter, OutgoingKafkaImporter
from zato.cli.enmasse.importers.mcp import GatewayMCPImporter
from zato.cli.enmasse.importers.rule_engine_api import RuleEngineAPIImporter
from zato.cli.enmasse.importers.as2 import AS2Importer
from zato.cli.enmasse.importers.custom import CustomConnectorImporter
from zato.cli.enmasse.importers.ldap import LDAPImporter
from zato.cli.enmasse.importers.llm import LLMImporter
from zato.cli.enmasse.importers.microsoft_cloud import MicrosoftCloudImporter
from zato.cli.enmasse.importers.microsoft_fabric import MicrosoftFabricImporter
from zato.cli.enmasse.importers.microsoft_power_automate import MicrosoftPowerAutomateImporter
from zato.cli.enmasse.importers.microsoft_teams import MicrosoftTeamsImporter
from zato.cli.enmasse.importers.slack import SlackImporter
from zato.cli.enmasse.importers.mongodb import MongoDBImporter
from zato.cli.enmasse.importers.odata import ODataImporter
from zato.cli.enmasse.importers.sftp import SFTPImporter
from zato.cli.enmasse.importers.smb import SMBImporter
from zato.cli.enmasse.importers.outgoing_as4 import OutgoingAS4Importer
from zato.cli.enmasse.importers.outgoing_rest import OutgoingRESTImporter
from zato.cli.enmasse.importers.outgoing_soap import OutgoingSOAPImporter
from zato.cli.enmasse.importers.pubsub_topic import PubSubTopicImporter
from zato.cli.enmasse.importers.pubsub_permission import PubSubPermissionImporter
from zato.cli.enmasse.importers.pubsub_subscription import PubSubSubscriptionImporter
from zato.cli.enmasse.importers.channel_openapi import ChannelOpenAPIImporter
from zato.cli.enmasse.importer.config import ConfigSync
from zato.cli.enmasse.importer.outgoing import OutgoingSync
from zato.cli.enmasse.util.secrets import Known_Secret_Keys, redact_secrets
from zato.common.odb.model import Cluster

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

for importer_module in ['zato.cli.enmasse.importers.security', 'zato.cli.enmasse.importers.channel_rest',
                        'zato.cli.enmasse.importers.channel_soap',
                        'zato.cli.enmasse.importers.channel_as4', 'zato.cli.enmasse.importers.outgoing_as4',
                        'zato.cli.enmasse.importers.group',
                        'zato.cli.enmasse.importers.email_smtp', 'zato.cli.enmasse.importers.email_imap',
                        'zato.cli.enmasse.importers.es', 'zato.cli.enmasse.importers.odoo',
                        'zato.cli.enmasse.importers.scheduler', 'zato.cli.enmasse.importers.sql',
                        'zato.cli.enmasse.importers.confluence', 'zato.cli.enmasse.importers.jira',
                        'zato.cli.enmasse.importers.salesforce',
                        'zato.cli.enmasse.importers.channel_mllp',
                        'zato.cli.enmasse.importers.outgoing_mllp',
                        'zato.cli.enmasse.importers.outgoing_fhir',
                        'zato.cli.enmasse.importers.graphql',
                        'zato.cli.enmasse.importers.grpc',
                        'zato.cli.enmasse.importers.amqp',
                        'zato.cli.enmasse.importers.ibm_mq',
                        'zato.cli.enmasse.importers.kafka',
                        'zato.cli.enmasse.importers.as2',
                        'zato.cli.enmasse.importers.ldap', 'zato.cli.enmasse.importers.llm',
                        'zato.cli.enmasse.importers.microsoft_cloud',
                        'zato.cli.enmasse.importers.microsoft_fabric',
                        'zato.cli.enmasse.importers.microsoft_power_automate',
                        'zato.cli.enmasse.importers.microsoft_teams',
                        'zato.cli.enmasse.importers.slack',
                        'zato.cli.enmasse.importers.mongodb',
                        'zato.cli.enmasse.importers.odata',
                        'zato.cli.enmasse.importers.ftp',
                        'zato.cli.enmasse.importers.sftp', 'zato.cli.enmasse.importers.smb',
                        'zato.cli.enmasse.importers.outgoing_rest', 'zato.cli.enmasse.importers.outgoing_soap',
                        'zato.cli.enmasse.importers.pubsub_topic', 'zato.cli.enmasse.importers.pubsub_permission',
                        'zato.cli.enmasse.importers.pubsub_subscription', 'zato.cli.enmasse.util']:
    importer_logger = logging.getLogger(importer_module)
    importer_logger.setLevel(logging.INFO)
    importer_logger.addHandler(handler)

# ################################################################################################################################
# ################################################################################################################################

class EnmasseYAMLImporter(ConfigSync, OutgoingSync):
    """ Imports enmasse YAML configuration files and builds an in-memory representation.
    """
    def __init__(self) -> 'None':

        # This is always the same
        self.cluster_id = ModuleCtx.Cluster_ID

        self.object_type = ModuleCtx.ObjectType
        self.object_alias = ModuleCtx.ObjectAlias

        self.sec_defs = {}
        self.group_defs = {}
        self.quota_tier_defs = {}
        self.audit_retention_defs = {}
        self.audit_extraction_defs = {}
        self.odoo_defs = {}
        self.smtp_defs = {}
        self.imap_defs = {}
        self.es_defs = {}
        self.sql_defs = {}
        self.job_defs = {}
        self.confluence_defs = {}
        self.jira_defs = {}
        self.salesforce_defs = {}
        self.channel_mllp_defs = {}
        self.outgoing_mllp_defs = {}
        self.outgoing_fhir_defs = {}
        self.channel_ibm_mq_defs = {}
        self.channel_kafka_defs = {}
        self.gateway_mcp_defs = {}
        self.rule_engine_api_defs = {}
        self.outgoing_graphql_defs = {}
        self.outgoing_grpc_defs = {}
        self.outgoing_ibm_mq_defs = {}
        self.outgoing_kafka_defs = {}
        self.ldap_defs = {}
        self.llm_defs = {}
        self.mongodb_defs = {}
        self.odata_defs = {}
        self.sap_defs = {}
        self.sftp_defs = {}
        self.smb_defs = {}
        self.ftp_defs = {}
        self.microsoft_cloud_defs = {}
        self.microsoft_fabric_defs = {}
        self.microsoft_power_automate_defs = {}
        self.microsoft_teams_defs = {}
        self.slack_defs = {}
        self.outgoing_rest_defs = {}
        self.outgoing_soap_defs = {}
        self.outgoing_as2_defs = {}
        self.outgoing_as4_defs = {}
        self.pubsub_topic_defs = {}
        self.pubsub_permission_defs = {}
        self.pubsub_subscription_defs = {}
        self.channel_openapi_defs = {}
        self.objects = {}
        self.cluster = None

        # Track created and updated objects for reporting
        self.created_objects = {}
        self.updated_objects = {}

        # Initialize importers
        self.security_importer = SecurityImporter(self)
        self.channel_importer = ChannelImporter(self)
        self.channel_soap_importer = ChannelSOAPImporter(self)
        self.channel_as4_importer = ChannelAS4Importer(self)
        self.group_importer = GroupImporter(self)
        self.quota_tier_importer = QuotaTierImporter(self)
        self.audit_retention_importer = AuditRetentionImporter(self)
        self.audit_extraction_importer = AuditExtractionImporter(self)
        self.alert_config_importer = AlertConfigImporter(self)
        self.odoo_importer = OdooImporter(self)
        self.smtp_importer = SMTPImporter(self)
        self.imap_importer = IMAPImporter(self)
        self.es_importer = ElasticSearchImporter(self)
        self.sql_importer = SQLImporter(self)
        self.scheduler_importer = SchedulerImporter(self)
        self.confluence_importer = ConfluenceImporter(self)
        self.jira_importer = JiraImporter(self)
        self.salesforce_importer = SalesforceImporter(self)
        self.channel_mllp_importer = ChannelMLLPImporter(self)
        self.outgoing_mllp_importer = OutgoingMLLPImporter(self)
        self.outgoing_fhir_importer = OutgoingFHIRImporter(self)
        self.channel_ibm_mq_importer = ChannelIBMMQImporter(self)
        self.channel_amqp_importer = ChannelAMQPImporter(self, 'amqp')
        self.outgoing_amqp_importer = OutgoingAMQPImporter(self, 'amqp')
        self.channel_azure_service_bus_importer = ChannelAMQPImporter(self, 'azure-service-bus')
        self.outgoing_azure_service_bus_importer = OutgoingAMQPImporter(self, 'azure-service-bus')
        self.channel_kafka_importer = ChannelKafkaImporter(self)
        self.gateway_mcp_importer = GatewayMCPImporter(self)
        self.rule_engine_api_importer = RuleEngineAPIImporter(self)
        self.outgoing_graphql_importer = OutgoingGraphQLImporter(self)
        self.outgoing_grpc_importer = OutgoingGRPCImporter(self)
        self.outgoing_ibm_mq_importer = OutgoingIBMMQImporter(self)
        self.outgoing_kafka_importer = OutgoingKafkaImporter(self)
        self.ldap_importer = LDAPImporter(self)
        self.llm_importer = LLMImporter(self)
        self.mongodb_importer = MongoDBImporter(self)
        self.odata_importer = ODataImporter(self, 'odata')
        self.sap_importer = ODataImporter(self, 'sap')
        self.sftp_importer = SFTPImporter(self)
        self.smb_importer = SMBImporter(self)
        self.ftp_importer = FTPImporter(self)
        self.microsoft_cloud_importer = MicrosoftCloudImporter(self)
        self.microsoft_fabric_importer = MicrosoftFabricImporter(self)
        self.microsoft_power_automate_importer = MicrosoftPowerAutomateImporter(self)
        self.microsoft_teams_importer = MicrosoftTeamsImporter(self)
        self.slack_importer = SlackImporter(self)
        self.outgoing_rest_importer = OutgoingRESTImporter(self)
        self.outgoing_soap_importer = OutgoingSOAPImporter(self)
        self.as2_importer = AS2Importer(self)
        self.outgoing_as4_importer = OutgoingAS4Importer(self)
        self.pubsub_topic_importer = PubSubTopicImporter(self)
        self.pubsub_permission_importer = PubSubPermissionImporter(self)
        self.pubsub_subscription_importer = PubSubSubscriptionImporter(self)
        self.channel_openapi_importer = ChannelOpenAPIImporter(self)

        # Importers for custom connector types are built on demand, one per top-level custom_ key.
        self.custom_importers = {}

# ################################################################################################################################

    def get_cluster(self, session:'SASession') -> 'any_':
        """ Returns the cluster instance, retrieving it from the database if needed.
        """
        if not self.cluster:
            logger.info('Getting cluster by id=%s', self.cluster_id)
            self.cluster = session.query(Cluster).filter_by(id=self.cluster_id).one()
        return self.cluster

# ################################################################################################################################

    def sync_quota_tiers(self, tier_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes quota tiers from a YAML configuration with the database.
        """
        if not tier_list:
            return [], []

        count = len(tier_list)
        noun = 'tier' if count == 1 else 'tiers'
        logger.info(f'Processing {count} quota {noun}')

        tiers_created, tiers_updated = self.quota_tier_importer.sync_quota_tiers(tier_list, session)

        # Get tier definitions from the tier importer and store them in our instance
        self.quota_tier_defs = self.quota_tier_importer.tier_defs

        created_count = len(tiers_created)
        updated_count = len(tiers_updated)
        logger.info(f'Processed quota tiers: created={created_count} updated={updated_count}')

        return tiers_created, tiers_updated

# ################################################################################################################################

    def sync_audit_retention(self, policy_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes audit retention policies from a YAML configuration with the database.
        """
        if not policy_list:
            return [], []

        count = len(policy_list)
        noun = 'policy' if count == 1 else 'policies'
        logger.info(f'Processing {count} retention {noun}')

        policies_created, policies_updated = self.audit_retention_importer.sync_retention_policies(policy_list, session)

        # Get policy definitions from the policy importer and store them in our instance
        self.audit_retention_defs = self.audit_retention_importer.policy_defs

        created_count = len(policies_created)
        updated_count = len(policies_updated)
        logger.info(f'Processed retention policies: created={created_count} updated={updated_count}')

        return policies_created, policies_updated

# ################################################################################################################################

    def sync_alert_rules(self, rule_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes alert rule configuration from a YAML configuration with the rule store.
        """
        if not rule_list:
            return [], []

        count = len(rule_list)
        noun = 'entry' if count == 1 else 'entries'
        logger.info(f'Processing {count} alert rule {noun}')

        rules_created, rules_updated = self.alert_config_importer.sync_alert_rules(rule_list)

        updated_count = len(rules_updated)
        logger.info(f'Processed alert rules: updated={updated_count}')

        return rules_created, rules_updated

# ################################################################################################################################

    def sync_alert_notifications(self, values:'dict', session:'SASession') -> 'bool':
        """ Synchronizes alert notification targets from a YAML configuration with the sweep job's extra.
        """
        if not values:
            return False

        changed = self.alert_config_importer.sync_alert_notifications(values, session)

        logger.info('Processed alert notifications: changed=%s', changed)

        return changed

# ################################################################################################################################

    def sync_audit_extraction(self, extraction_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes attribute-extraction rule sets from a YAML configuration with the database.
        """
        if not extraction_list:
            return [], []

        count = len(extraction_list)
        noun = 'set' if count == 1 else 'sets'
        logger.info(f'Processing {count} extraction rule {noun}')

        extraction_created, extraction_updated = self.audit_extraction_importer.sync_extraction_rules(extraction_list, session)

        # Get set definitions from the extraction importer and store them in our instance
        self.audit_extraction_defs = self.audit_extraction_importer.extraction_defs

        created_count = len(extraction_created)
        updated_count = len(extraction_updated)
        logger.info(f'Processed extraction rule sets: created={created_count} updated={updated_count}')

        return extraction_created, extraction_updated

# ################################################################################################################################

    def sync_security(self, security_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes security definitions from a YAML configuration with the database.
        """

        # A file without a security block may still name definitions that exist already,
        # so what the database has is known to every importer that resolves security by name.
        if not security_list:
            self.security_importer.populate_sec_defs_from_db(session)
            return [], []

        count = len(security_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} security {noun}')
        security_created, security_updated = self.security_importer.sync_security_definitions(security_list, session)

        created_count = len(security_created)
        updated_count = len(security_updated)
        logger.info(f'Processed security definitions: created={created_count} updated={updated_count}')

        return security_created, security_updated

# ################################################################################################################################

    def sync_groups(self, group_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes security groups from a YAML configuration with the database.
        """
        if not group_list:
            return [], []

        count = len(group_list)
        noun = 'group' if count == 1 else 'groups'
        logger.info(f'Processing {count} security {noun}')

        # Process each group item
        for idx, item in enumerate(group_list):
            logger.info('Group item %d: %s', idx, redact_secrets(item, Known_Secret_Keys))

        processed_groups = self.group_importer.sync_groups(group_list, session)

        # Get group definitions from the group importer and store them in our instance
        self.group_defs = self.group_importer.group_defs

        logger.info('Processed security groups: %d', len(processed_groups))

        return processed_groups

# ################################################################################################################################

    def sync_channel_rest(self, channel_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes REST channels from a YAML configuration with the database.
        """
        if not channel_list:
            return [], []

        count = len(channel_list)
        noun = 'channel' if count == 1 else 'channels'
        logger.info(f'Processing {count} REST {noun}')
        channels_created, channels_updated = self.channel_importer.sync_channel_rest(channel_list, session)
        created_count = len(channels_created)
        updated_count = len(channels_updated)
        logger.info(f'Processed REST channels: created={created_count} updated={updated_count}')

        return channels_created, channels_updated

# ################################################################################################################################

    def sync_channel_soap(self, channel_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes SOAP channels from a YAML configuration with the database.
        """
        if not channel_list:
            return [], []

        count = len(channel_list)
        noun = 'channel' if count == 1 else 'channels'
        logger.info(f'Processing {count} SOAP {noun}')
        channels_created, channels_updated = self.channel_soap_importer.sync_channel_soap(channel_list, session)
        created_count = len(channels_created)
        updated_count = len(channels_updated)
        logger.info(f'Processed SOAP channels: created={created_count} updated={updated_count}')

        return channels_created, channels_updated

# ################################################################################################################################

    def sync_channel_as4(self, channel_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes AS4 channels from a YAML configuration with the database.
        """
        if not channel_list:
            return [], []

        count = len(channel_list)
        noun = 'channel' if count == 1 else 'channels'
        logger.info(f'Processing {count} AS4 {noun}')
        channels_created, channels_updated = self.channel_as4_importer.sync_channel_as4(channel_list, session)
        created_count = len(channels_created)
        updated_count = len(channels_updated)
        logger.info(f'Processed AS4 channels: created={created_count} updated={updated_count}')

        return channels_created, channels_updated

# ################################################################################################################################

    def sync_scheduler(self, job_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes scheduler job definitions from a YAML configuration with the database.
        """
        if not job_list:
            return [], []

        count = len(job_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} scheduler job {noun}')

        # Examine each scheduler job item
        for idx, item in enumerate(job_list):
            logger.info('Scheduler job item %d: %s', idx, redact_secrets(item, Known_Secret_Keys))

        job_created, job_updated = self.scheduler_importer.sync_job_definitions(job_list, session)

        # Get scheduler job definitions from the scheduler importer
        self.job_defs = self.scheduler_importer.job_defs
        logger.info('Processed scheduler job definitions: created=%d updated=%d', len(job_created), len(job_updated))

        return job_created, job_updated

# ################################################################################################################################

    def _sync_channel_amqp_impl(self, item_list:'list', session:'SASession', importer:'ChannelAMQPImporter') -> 'tuple':
        """ Synchronizes channel definitions of one AMQP subtype from a YAML configuration with the database.
        """
        if not item_list:
            return [], []

        items_created, items_updated = importer.sync_channel_definitions(item_list, session)

        return items_created, items_updated

# ################################################################################################################################

    def sync_channel_amqp(self, item_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes AMQP channel definitions from a YAML configuration with the database.
        """
        items_created, items_updated = self._sync_channel_amqp_impl(item_list, session, self.channel_amqp_importer)
        return items_created, items_updated

# ################################################################################################################################

    def sync_channel_azure_service_bus(self, item_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes Azure Service Bus channel definitions from a YAML configuration with the database.
        """
        items_created, items_updated = self._sync_channel_amqp_impl(item_list, session, self.channel_azure_service_bus_importer)
        return items_created, items_updated

# ################################################################################################################################

    def sync_channel_mllp(self, channel_mllp_list:'list', session:'SASession') -> 'tuple':
        if not channel_mllp_list:
            return [], []

        count = len(channel_mllp_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} HL7 MLLP channel {noun}')

        for idx, item in enumerate(channel_mllp_list):
            logger.info('HL7 MLLP channel item %d: %s', idx, redact_secrets(item, Known_Secret_Keys))

        created, updated = self.channel_mllp_importer.sync_definitions(channel_mllp_list, session)
        self.channel_mllp_defs = self.channel_mllp_importer.connection_defs

        created_count = len(created)
        updated_count = len(updated)
        logger.info('Processed HL7 MLLP channel definitions: created=%d updated=%d', created_count, updated_count)

        return created, updated

# ################################################################################################################################

    def sync_channel_ibm_mq(self, channel_ibm_mq_list:'list', session:'SASession') -> 'tuple':
        if not channel_ibm_mq_list:
            return [], []

        count = len(channel_ibm_mq_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} IBM MQ channel {noun}')

        for idx, item in enumerate(channel_ibm_mq_list):
            logger.info('IBM MQ channel item %d: %s', idx, redact_secrets(item, Known_Secret_Keys))

        created, updated = self.channel_ibm_mq_importer.sync_definitions(channel_ibm_mq_list, session)
        self.channel_ibm_mq_defs = self.channel_ibm_mq_importer.connection_defs
        logger.info('Processed IBM MQ channel definitions: created=%d updated=%d', len(created), len(updated))

        return created, updated

# ################################################################################################################################

    def sync_channel_kafka(self, channel_kafka_list:'list', session:'SASession') -> 'tuple':
        if not channel_kafka_list:
            return [], []

        count = len(channel_kafka_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} Kafka channel {noun}')

        for idx, item in enumerate(channel_kafka_list):
            logger.info('Kafka channel item %d: %s', idx, redact_secrets(item, Known_Secret_Keys))

        created, updated = self.channel_kafka_importer.sync_definitions(channel_kafka_list, session)
        self.channel_kafka_defs = self.channel_kafka_importer.connection_defs
        logger.info('Processed Kafka channel definitions: created=%d updated=%d', len(created), len(updated))

        return created, updated

# ################################################################################################################################

    def sync_gateway_mcp(self, gateway_mcp_list:'list', session:'SASession') -> 'tuple':
        if not gateway_mcp_list:
            return [], []

        count = len(gateway_mcp_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} MCP gateway {noun}')

        for idx, item in enumerate(gateway_mcp_list):
            logger.info('MCP gateway item %d: %s', idx, redact_secrets(item, Known_Secret_Keys))

        created, updated = self.gateway_mcp_importer.sync_definitions(gateway_mcp_list, session)
        self.gateway_mcp_defs = self.gateway_mcp_importer.connection_defs
        logger.info('Processed MCP gateway definitions: created=%d updated=%d', len(created), len(updated))

        return created, updated

# ################################################################################################################################

    def sync_rule_engine_api(self, rule_engine_api_list:'list', session:'SASession') -> 'tuple':
        if not rule_engine_api_list:
            return [], []

        count = len(rule_engine_api_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} Rule engine API {noun}')

        for idx, item in enumerate(rule_engine_api_list):
            logger.info('Rule engine API item %d: %s', idx, redact_secrets(item, Known_Secret_Keys))

        created, updated = self.rule_engine_api_importer.sync_definitions(rule_engine_api_list, session)
        self.rule_engine_api_defs = self.rule_engine_api_importer.connection_defs
        logger.info('Processed Rule engine API definitions: created=%d updated=%d', len(created), len(updated))

        return created, updated

# ################################################################################################################################

    def sync_pubsub_topic(self, topic_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes pubsub topic definitions from a YAML configuration with the database.
        """
        if not topic_list:
            return [], []

        count = len(topic_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} pubsub topic {noun}')

        # Examine each pubsub topic item
        for idx, item in enumerate(topic_list):
            logger.info('Pubsub topic item %d: %s', idx, redact_secrets(item, Known_Secret_Keys))

        topic_created, topic_updated = self.pubsub_topic_importer.sync_pubsub_topic_definitions(topic_list, session)

        # Get pubsub topic definitions from the pubsub topic importer
        self.pubsub_topic_defs = self.pubsub_topic_importer.pubsub_topic_defs
        logger.info('Processed pubsub topic definitions: created=%d updated=%d', len(topic_created), len(topic_updated))

        return topic_created, topic_updated

# ################################################################################################################################

    def sync_pubsub_permission(self, permission_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes pubsub permission definitions from a YAML configuration with the database.
        """
        if not permission_list:
            return [], []

        count = len(permission_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} pubsub permission {noun}')

        # Examine each pubsub permission item
        for idx, item in enumerate(permission_list):
            logger.info('Pubsub permission item %d: %s', idx, redact_secrets(item, Known_Secret_Keys))

        permission_created, permission_updated = self.pubsub_permission_importer.sync_pubsub_permission_definitions(permission_list, session)

        # Get pubsub permission definitions from the pubsub permission importer
        self.pubsub_permission_defs = self.pubsub_permission_importer.pubsub_permission_defs
        logger.info('Processed pubsub permission definitions: created=%d updated=%d', len(permission_created), len(permission_updated))

        return permission_created, permission_updated

# ################################################################################################################################

    def sync_pubsub_subscription(self, subscription_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes pubsub subscription definitions from a YAML configuration with the database.
        """
        if not subscription_list:
            return [], []

        count = len(subscription_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} pubsub subscription {noun}')

        # Examine each pubsub subscription item
        for idx, item in enumerate(subscription_list):
            logger.info('Pubsub subscription item %d: %s', idx, redact_secrets(item, Known_Secret_Keys))

        subscription_created, subscription_updated = self.pubsub_subscription_importer.sync_pubsub_subscription_definitions(subscription_list, session)

        # Get pubsub subscription definitions from the pubsub subscription importer
        self.pubsub_subscription_defs = self.pubsub_subscription_importer.pubsub_subscription_defs
        logger.info('Processed pubsub subscription definitions: created=%d updated=%d', len(subscription_created), len(subscription_updated))

        return subscription_created, subscription_updated

# ################################################################################################################################

    def sync_custom_connectors(self, yaml_key:'str', conn_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes definitions of one custom connector type, e.g. custom_crm, with the database.
        """
        if not conn_list:
            return [], []

        count = len(conn_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} custom connector {noun} ({yaml_key})')

        # Build the importer for this connector type if the key is seen for the first time.
        if yaml_key not in self.custom_importers:
            self.custom_importers[yaml_key] = CustomConnectorImporter(self, yaml_key)

        custom_importer = self.custom_importers[yaml_key]
        created, updated = custom_importer.sync_definitions(conn_list, session)

        logger.info('Processed custom connector definitions (%s): created=%d updated=%d', yaml_key, len(created), len(updated))

        return created, updated

# ################################################################################################################################

    def sync_channel_openapi(self, channel_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes OpenAPI channel definitions from a YAML configuration with the database.
        """
        if not channel_list:
            return [], []

        count = len(channel_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} OpenAPI channel {noun}')

        channel_created, channel_updated = self.channel_openapi_importer.sync_channel_openapi(channel_list, session)

        logger.info('Processed OpenAPI channel definitions: created=%d updated=%d', len(channel_created), len(channel_updated))

        return channel_created, channel_updated

# ################################################################################################################################
# ################################################################################################################################
