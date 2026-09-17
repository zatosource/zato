# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# This module holds the half of EnmasseYAMLImporter that reads a YAML config and runs the import: from_path and
# from_string load the file, _process_includes, _merge_configs and _process_config shape it, and sync_from_yaml calls
# every sync_* wrapper in dependency order. The wrappers themselves and the attributes read here are defined on
# EnmasseYAMLImporter and OutgoingSync, this class is only ever used as one of their bases.

# stdlib
import logging
import os

# PyYAML
import yaml

# Zato
from zato.cli.enmasse.config import ModuleCtx
from zato.cli.enmasse.client import wait_for_services, Default_Service_Wait_Timeout
from zato.cli.enmasse.util import Renamed_Keys

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ################################################################################################################################
# ################################################################################################################################

def get_generic_connection_type(item:'stranydict') -> 'str':
    """ Returns the connection type of one zato_generic_connection item. The canonical key is type
    and its value is moved under type_, which is the key the per-type importers and the database column use.
    """
    if 'type' in item:
        item['type_'] = item['type']
        del item['type']
    return item['type_']

# ################################################################################################################################
# ################################################################################################################################

class ConfigSync:
    """ Reads a YAML config and synchronizes it, calling the sync_* wrappers of EnmasseYAMLImporter in dependency order.
    """

# ################################################################################################################################

    def from_path(self, path:'str') -> 'stranydict':
        """ Imports YAML configuration from a file path.
        """
        if not os.path.exists(path):
            raise ValueError(f'Path does not exist -> {path}')

        # Convert the path to an absolute path
        path = os.path.abspath(path)
        base_dir = os.path.dirname(path)

        with open(path, 'r') as f:
            yaml_content = f.read()

        # Parse the YAML content
        config = yaml.safe_load(yaml_content)

        # Process includes if present
        if 'include' in config:
            config = self._process_includes(config, base_dir)

        return self._process_config(config)

# ################################################################################################################################

    def from_string(self, yaml_string:'str') -> 'stranydict':
        """ Imports YAML configuration from a string.
        """
        # Parse YAML into Python data structure
        config = yaml.safe_load(yaml_string)

        # Process the config (without include handling since we don't have a base directory)
        return self._process_config(config)

# ################################################################################################################################

    def _process_includes(self, config:'stranydict', base_dir:'str', processed_paths:'set | None'=None) -> 'stranydict':

        # Initialize set of processed paths to prevent recursive includes
        if processed_paths is None:
            processed_paths = set()

        # Get the list of files to include
        include_files = config.get('include', [])
        if not include_files:
            return config

        # Remove the include directive since we're processing it
        merged_config = {key: value for key, value in config.items() if key != 'include'}

        # Process each included file
        for include_path in include_files:

            # Resolve the path (absolute or relative to base_dir)
            if os.path.isabs(include_path):
                resolved_path = include_path
            else:
                resolved_path = os.path.normpath(os.path.join(base_dir, include_path))

            # Check if path exists
            if not os.path.exists(resolved_path):
                raise ValueError(f'Included file does not exist -> {resolved_path}')

            # Check for recursive/circular includes
            if resolved_path in processed_paths:
                raise ValueError(f'Circular include detected -> {resolved_path}')

            # Mark this path as processed
            processed_paths.add(resolved_path)

            # Read and parse the included file
            with open(resolved_path, 'r') as f:
                include_content = f.read()

            include_config = yaml.safe_load(include_content)

            # If the included file itself has includes, process them recursively
            include_dir = os.path.dirname(resolved_path)

            if 'include' in include_config:
                include_config = self._process_includes(include_config, include_dir, processed_paths)

            # Merge the included config with our current config
            self._merge_configs(merged_config, include_config)

        return merged_config

# ################################################################################################################################

    def _merge_configs(self, target:'stranydict', source:'stranydict') -> None:
        """ Merge source config into target config.
            This combines the lists for each section rather than overwriting.
        """

        for key, items in source.items():

            # Skip if no items for this object type
            if not items:
                continue

            # A mapping-valued section, e.g. alert_notifications, is one flat mapping of fields rather than
            # a list of items - a later file's fields land over an earlier one's
            if isinstance(items, dict):
                if key not in target:
                    target[key] = {}
                target[key].update(items)
                continue

            # Initialize section if it doesn't exist
            if key not in target:
                target[key] = []

            # Add all items for this object type
            target[key].extend(items)

# ################################################################################################################################

    def _process_config(self, config:'stranydict') -> 'stranydict':
        """ Process a config dict into the expected result format.
            This is the final processing step after handling includes.
        """
        # A key that has been renamed is refused, because importing the file without it would
        # leave the objects it declares uncreated while reporting that all went well
        for key in config:
            if new_key := Renamed_Keys.get(key):
                raise ValueError(f'Key `{key}` is now called `{new_key}`')

        # Convert the raw YAML into a structured representation
        result = {}

        # Process each object type from the YAML
        for key, items in config.items():
            # Skip if no items for this object type
            if not items:
                continue

            # A mapping-valued section stays the mapping it is - extending a list with it would keep its keys alone
            if isinstance(items, dict):
                result[key] = dict(items)
                continue

            # Process all items for this object type
            if key not in result:
                result[key] = []

            # Add all items for this object type
            result[key].extend(items)

        return result

# ################################################################################################################################

    def sync_from_yaml(
        self,
        yaml_config:'stranydict',
        session:'SASession',
        server_dir:'str | None'=None,
        wait_for_services_timeout:'int | None'=None
    ) -> 'tuple':
        """ Synchronizes all objects from a YAML configuration with the database.
        """
        logger.info('Starting synchronization of YAML configuration')

        # Reset tracking dictionaries
        self.created_objects = {}
        self.updated_objects = {}

        # Wait for all services referenced in the configuration to be available
        if server_dir:
            timeout = wait_for_services_timeout or Default_Service_Wait_Timeout
            logger.info('About to call wait_for_services with timeout=%s, server_dir=%s', timeout, server_dir)

            # Log raw service names from YAML before env var resolution
            for section_name in ('channel_rest', 'channel_soap', 'scheduler'):
                if section_items := yaml_config.get(section_name):
                    for item in section_items:
                        if svc := item.get('service'):
                            logger.info('Raw service name in %s: %r', section_name, svc)

            missing_services = wait_for_services(yaml_config, server_dir, timeout_seconds=timeout)

            if missing_services:
                count = len(missing_services)
                noun = 'service' if count == 1 else 'services'
                raise Exception(f'{count} {noun} not found after {timeout}s: {sorted(missing_services)}')

        # Process quota tiers first - security definitions and groups reference them by name
        tiers_created, tiers_updated = self.sync_quota_tiers(yaml_config.get('quota_tier', []), session)
        if tiers_created:
            self.created_objects['quota_tier'] = tiers_created
        if tiers_updated:
            self.updated_objects['quota_tier'] = tiers_updated

        # Process audit retention policies
        retention_created, retention_updated = self.sync_audit_retention(yaml_config.get('audit_retention', []), session)
        if retention_created:
            self.created_objects['audit_retention'] = retention_created
        if retention_updated:
            self.updated_objects['audit_retention'] = retention_updated

        # Process attribute-extraction rule sets
        extraction_created, extraction_updated = self.sync_audit_extraction(yaml_config.get('audit_extraction', []), session)
        if extraction_created:
            self.created_objects['audit_extraction'] = extraction_created
        if extraction_updated:
            self.updated_objects['audit_extraction'] = extraction_updated

        # Process security definitions next
        sec_created, sec_updated = self.sync_security(yaml_config.get('security', []), session)
        if sec_created:
            self.created_objects['security'] = sec_created
        if sec_updated:
            self.updated_objects['security'] = sec_updated

        # Process security groups (depends on security definitions)
        groups_created, groups_updated = self.sync_groups(yaml_config.get('groups', []), session)
        if groups_created:
            self.created_objects['groups'] = groups_created
        if groups_updated:
            self.updated_objects['groups'] = groups_updated

        # Process REST channels which may depend on security definitions
        channels_created, channels_updated = self.sync_channel_rest(yaml_config.get('channel_rest', []), session)
        if channels_created:
            self.created_objects['channel_rest'] = channels_created
        if channels_updated:
            self.updated_objects['channel_rest'] = channels_updated

        # Process SOAP channels which may depend on security definitions
        channels_soap_created, channels_soap_updated = self.sync_channel_soap(yaml_config.get('channel_soap', []), session)
        if channels_soap_created:
            self.created_objects['channel_soap'] = channels_soap_created
        if channels_soap_updated:
            self.updated_objects['channel_soap'] = channels_soap_updated

        # Process AS4 channels which may depend on security definitions
        channels_as4_created, channels_as4_updated = self.sync_channel_as4(yaml_config.get('channel_as4', []), session)
        if channels_as4_created:
            self.created_objects['channel_as4'] = channels_as4_created
        if channels_as4_updated:
            self.updated_objects['channel_as4'] = channels_as4_updated

        # Process Odoo connection definitions
        odoo_created, odoo_updated = self.sync_odoo(yaml_config.get('odoo', []), session)
        if odoo_created:
            self.created_objects['odoo'] = odoo_created
        if odoo_updated:
            self.updated_objects['odoo'] = odoo_updated

        # Process SMTP connection definitions
        smtp_created, smtp_updated = self.sync_smtp(yaml_config.get('email_smtp', []), session)
        if smtp_created:
            self.created_objects['email_smtp'] = smtp_created
        if smtp_updated:
            self.updated_objects['email_smtp'] = smtp_updated

        # Process IMAP connection definitions
        imap_created, imap_updated = self.sync_imap(yaml_config.get('email_imap', []), session)
        if imap_created:
            self.created_objects['email_imap'] = imap_created
        if imap_updated:
            self.updated_objects['email_imap'] = imap_updated

        # Process SQL connection pool definitions
        sql_list = yaml_config.get('sql') or yaml_config.get('outconn_sql', [])
        sql_created, sql_updated = self.sync_sql(sql_list, session)
        if sql_created:
            self.created_objects['sql'] = sql_created
        if sql_updated:
            self.updated_objects['sql'] = sql_updated

        # Process scheduler job definitions
        job_created, job_updated = self.sync_scheduler(yaml_config.get('scheduler', []), session)
        if job_created:
            self.created_objects['scheduler'] = job_created
        if job_updated:
            self.updated_objects['scheduler'] = job_updated

        # Process Confluence connection definitions
        confluence_created, confluence_updated = self.sync_confluence(yaml_config.get('confluence', []), session)
        if confluence_created:
            self.created_objects['confluence'] = confluence_created
        if confluence_updated:
            self.updated_objects['confluence'] = confluence_updated

        # Process Jira connection definitions
        jira_list = yaml_config.get('jira', [])
        generic_list = yaml_config.get('zato_generic_connection')
        if generic_list:
            for item in generic_list:
                item_type = get_generic_connection_type(item)
                if item_type == 'cloud-jira':
                    jira_list.append(item)
        jira_created, jira_updated = self.sync_jira(jira_list, session)
        if jira_created:
            self.created_objects['jira'] = jira_created
        if jira_updated:
            self.updated_objects['jira'] = jira_updated

        # Process Salesforce connection definitions
        salesforce_list = yaml_config.get('salesforce', [])
        if generic_list:
            for item in generic_list:
                item_type = get_generic_connection_type(item)
                if item_type == 'cloud-salesforce':
                    salesforce_list.append(item)
        salesforce_created, salesforce_updated = self.sync_salesforce(salesforce_list, session)
        if salesforce_created:
            self.created_objects['salesforce'] = salesforce_created
        if salesforce_updated:
            self.updated_objects['salesforce'] = salesforce_updated

        # Process LDAP connection definitions
        ldap_list = yaml_config.get('ldap') or yaml_config.get('outgoing_ldap', [])
        ldap_created, ldap_updated = self.sync_ldap(ldap_list, session)
        if ldap_created:
            self.created_objects['ldap'] = ldap_created
        if ldap_updated:
            self.updated_objects['ldap'] = ldap_updated

        # Process LLM connection definitions
        llm_list = yaml_config.get('llm', [])
        llm_created, llm_updated = self.sync_llm(llm_list, session)
        if llm_created:
            self.created_objects['llm'] = llm_created
        if llm_updated:
            self.updated_objects['llm'] = llm_updated

        # Process OData connection definitions
        odata_list = yaml_config.get('odata') or yaml_config.get('outgoing_odata', [])
        odata_created, odata_updated = self.sync_odata(odata_list, session)
        if odata_created:
            self.created_objects['odata'] = odata_created
        if odata_updated:
            self.updated_objects['odata'] = odata_updated

        # Process SAP connection definitions
        sap_list = yaml_config.get('sap') or yaml_config.get('outgoing_sap', [])
        sap_created, sap_updated = self.sync_sap(sap_list, session)
        if sap_created:
            self.created_objects['sap'] = sap_created
        if sap_updated:
            self.updated_objects['sap'] = sap_updated

        # Process SFTP connection definitions
        sftp_list = yaml_config.get('sftp') or yaml_config.get('outgoing_sftp', [])
        sftp_created, sftp_updated = self.sync_sftp(sftp_list, session)
        if sftp_created:
            self.created_objects['sftp'] = sftp_created
        if sftp_updated:
            self.updated_objects['sftp'] = sftp_updated

        # Process SMB connection definitions
        smb_list = yaml_config.get('smb') or yaml_config.get('outgoing_smb', [])
        smb_created, smb_updated = self.sync_smb(smb_list, session)
        if smb_created:
            self.created_objects['smb'] = smb_created
        if smb_updated:
            self.updated_objects['smb'] = smb_updated

        # Process FTP connection definitions.
        ftp_list = yaml_config.get('ftp')
        if not ftp_list:
            ftp_list = yaml_config.get('outgoing_ftp')
        if not ftp_list:
            ftp_list = []
        ftp_created, ftp_updated = self.sync_ftp(ftp_list, session)
        if ftp_created:
            self.created_objects['ftp'] = ftp_created
        if ftp_updated:
            self.updated_objects['ftp'] = ftp_updated

        # Process MongoDB connection definitions
        mongodb_list = yaml_config.get('mongodb') or yaml_config.get('outgoing_mongodb', [])
        mongodb_created, mongodb_updated = self.sync_mongodb(mongodb_list, session)
        if mongodb_created:
            self.created_objects['mongodb'] = mongodb_created
        if mongodb_updated:
            self.updated_objects['mongodb'] = mongodb_updated

        # Process IBM MQ channel definitions
        channel_ibm_mq_list = yaml_config.get('channel_ibm_mq', [])
        channel_ibm_mq_created, channel_ibm_mq_updated = self.sync_channel_ibm_mq(channel_ibm_mq_list, session)
        if channel_ibm_mq_created:
            self.created_objects['channel_ibm_mq'] = channel_ibm_mq_created
        if channel_ibm_mq_updated:
            self.updated_objects['channel_ibm_mq'] = channel_ibm_mq_updated

        # Process IBM MQ outgoing definitions
        outgoing_ibm_mq_list = yaml_config.get('outgoing_ibm_mq', [])
        outgoing_ibm_mq_created, outgoing_ibm_mq_updated = self.sync_outgoing_ibm_mq(outgoing_ibm_mq_list, session)
        if outgoing_ibm_mq_created:
            self.created_objects['outgoing_ibm_mq'] = outgoing_ibm_mq_created
        if outgoing_ibm_mq_updated:
            self.updated_objects['outgoing_ibm_mq'] = outgoing_ibm_mq_updated

        # Process AMQP channel definitions
        channel_amqp_list = yaml_config.get('channel_amqp', [])
        channel_amqp_created, channel_amqp_updated = self.sync_channel_amqp(channel_amqp_list, session)
        if channel_amqp_created:
            self.created_objects['channel_amqp'] = channel_amqp_created
        if channel_amqp_updated:
            self.updated_objects['channel_amqp'] = channel_amqp_updated

        # Process AMQP outgoing definitions
        outgoing_amqp_list = yaml_config.get('outgoing_amqp', [])
        outgoing_amqp_created, outgoing_amqp_updated = self.sync_outgoing_amqp(outgoing_amqp_list, session)
        if outgoing_amqp_created:
            self.created_objects['outgoing_amqp'] = outgoing_amqp_created
        if outgoing_amqp_updated:
            self.updated_objects['outgoing_amqp'] = outgoing_amqp_updated

        # Process Azure Service Bus channel definitions
        channel_azure_list = yaml_config.get('channel_azure_service_bus', [])
        channel_azure_created, channel_azure_updated = self.sync_channel_azure_service_bus(channel_azure_list, session)
        if channel_azure_created:
            self.created_objects['channel_azure_service_bus'] = channel_azure_created
        if channel_azure_updated:
            self.updated_objects['channel_azure_service_bus'] = channel_azure_updated

        # Process Azure Service Bus outgoing definitions
        outgoing_azure_list = yaml_config.get('outgoing_azure_service_bus', [])
        outgoing_azure_created, outgoing_azure_updated = self.sync_outgoing_azure_service_bus(outgoing_azure_list, session)
        if outgoing_azure_created:
            self.created_objects['outgoing_azure_service_bus'] = outgoing_azure_created
        if outgoing_azure_updated:
            self.updated_objects['outgoing_azure_service_bus'] = outgoing_azure_updated

        # Process Kafka channel definitions
        channel_kafka_list = yaml_config.get('channel_kafka', [])
        channel_kafka_created, channel_kafka_updated = self.sync_channel_kafka(channel_kafka_list, session)
        if channel_kafka_created:
            self.created_objects['channel_kafka'] = channel_kafka_created
        if channel_kafka_updated:
            self.updated_objects['channel_kafka'] = channel_kafka_updated

        # Process MCP gateway definitions
        gateway_mcp_list = yaml_config.get('mcp_gateway', [])
        gateway_mcp_created, gateway_mcp_updated = self.sync_gateway_mcp(gateway_mcp_list, session)
        if gateway_mcp_created:
            self.created_objects['mcp_gateway'] = gateway_mcp_created
        if gateway_mcp_updated:
            self.updated_objects['mcp_gateway'] = gateway_mcp_updated

        # Process Rule engine API definitions
        rule_engine_api_list = yaml_config.get('rule_engine_api', [])
        rule_engine_api_created, rule_engine_api_updated = self.sync_rule_engine_api(rule_engine_api_list, session)
        if rule_engine_api_created:
            self.created_objects['rule_engine_api'] = rule_engine_api_created
        if rule_engine_api_updated:
            self.updated_objects['rule_engine_api'] = rule_engine_api_updated

        # Process Kafka outgoing definitions
        outgoing_kafka_list = yaml_config.get('outgoing_kafka', [])
        outgoing_kafka_created, outgoing_kafka_updated = self.sync_outgoing_kafka(outgoing_kafka_list, session)
        if outgoing_kafka_created:
            self.created_objects['outgoing_kafka'] = outgoing_kafka_created
        if outgoing_kafka_updated:
            self.updated_objects['outgoing_kafka'] = outgoing_kafka_updated

        # Process GraphQL outgoing definitions
        outgoing_graphql_list = yaml_config.get('outgoing_graphql', [])
        outgoing_graphql_created, outgoing_graphql_updated = self.sync_outgoing_graphql(outgoing_graphql_list, session)
        if outgoing_graphql_created:
            self.created_objects['outgoing_graphql'] = outgoing_graphql_created
        if outgoing_graphql_updated:
            self.updated_objects['outgoing_graphql'] = outgoing_graphql_updated

        # Process gRPC outgoing definitions - the shorter 'grpc' key is accepted as an alias
        outgoing_grpc_list = yaml_config.get('outgoing_grpc', []) + yaml_config.get('grpc', [])
        outgoing_grpc_created, outgoing_grpc_updated = self.sync_outgoing_grpc(outgoing_grpc_list, session)
        if outgoing_grpc_created:
            self.created_objects['outgoing_grpc'] = outgoing_grpc_created
        if outgoing_grpc_updated:
            self.updated_objects['outgoing_grpc'] = outgoing_grpc_updated

        # Process HL7 MLLP channel definitions
        channel_mllp_list = yaml_config.get('channel_mllp', [])
        channel_mllp_created, channel_mllp_updated = self.sync_channel_mllp(channel_mllp_list, session)
        if channel_mllp_created:
            self.created_objects['channel_mllp'] = channel_mllp_created
        if channel_mllp_updated:
            self.updated_objects['channel_mllp'] = channel_mllp_updated

        # Process outgoing HL7 MLLP definitions
        outgoing_mllp_list = yaml_config.get('outgoing_mllp', [])
        outgoing_mllp_created, outgoing_mllp_updated = self.sync_outgoing_mllp(outgoing_mllp_list, session)
        if outgoing_mllp_created:
            self.created_objects['outgoing_mllp'] = outgoing_mllp_created
        if outgoing_mllp_updated:
            self.updated_objects['outgoing_mllp'] = outgoing_mllp_updated

        # Process outgoing HL7 FHIR definitions
        outgoing_fhir_list = yaml_config.get('outgoing_fhir', [])
        outgoing_fhir_created, outgoing_fhir_updated = self.sync_outgoing_fhir(outgoing_fhir_list, session)
        if outgoing_fhir_created:
            self.created_objects['outgoing_fhir'] = outgoing_fhir_created
        if outgoing_fhir_updated:
            self.updated_objects['outgoing_fhir'] = outgoing_fhir_updated

        # Process Microsoft 365 connection definitions
        microsoft_cloud_list = yaml_config.get('microsoft_cloud', [])
        generic_list = yaml_config.get('zato_generic_connection')
        if generic_list:
            for item in generic_list:
                item_type = get_generic_connection_type(item)
                if item_type == 'cloud-microsoft-365':
                    microsoft_cloud_list.append(item)
        microsoft_cloud_created, microsoft_cloud_updated = self.sync_microsoft_cloud(microsoft_cloud_list, session)
        if microsoft_cloud_created:
            self.created_objects['microsoft_cloud'] = microsoft_cloud_created
        if microsoft_cloud_updated:
            self.updated_objects['microsoft_cloud'] = microsoft_cloud_updated

        # Process Microsoft Teams connection definitions
        microsoft_teams_list = yaml_config.get('microsoft_teams', [])
        generic_list = yaml_config.get('zato_generic_connection')
        if generic_list:
            for item in generic_list:
                item_type = get_generic_connection_type(item)
                if item_type == 'chat-microsoft-teams':
                    microsoft_teams_list.append(item)
        microsoft_teams_created, microsoft_teams_updated = self.sync_microsoft_teams(microsoft_teams_list, session)
        if microsoft_teams_created:
            self.created_objects['microsoft_teams'] = microsoft_teams_created
        if microsoft_teams_updated:
            self.updated_objects['microsoft_teams'] = microsoft_teams_updated

        # Process Slack connection definitions
        slack_list = yaml_config.get('slack', [])
        generic_list = yaml_config.get('zato_generic_connection')
        if generic_list:
            for item in generic_list:
                item_type = get_generic_connection_type(item)
                if item_type == 'chat-slack':
                    slack_list.append(item)
        slack_created, slack_updated = self.sync_slack(slack_list, session)
        if slack_created:
            self.created_objects['slack'] = slack_created
        if slack_updated:
            self.updated_objects['slack'] = slack_updated

        # Process Microsoft Fabric connection definitions
        fabric_list = yaml_config.get('microsoft_fabric', [])
        generic_list = yaml_config.get('zato_generic_connection')
        if generic_list:
            for item in generic_list:
                item_type = get_generic_connection_type(item)
                if item_type == 'cloud-microsoft-fabric':
                    fabric_list.append(item)
        fabric_created, fabric_updated = self.sync_microsoft_fabric(fabric_list, session)
        if fabric_created:
            self.created_objects['microsoft_fabric'] = fabric_created
        if fabric_updated:
            self.updated_objects['microsoft_fabric'] = fabric_updated

        # Process Microsoft Power Automate connection definitions
        power_automate_list = yaml_config.get('microsoft_power_automate', [])
        generic_list = yaml_config.get('zato_generic_connection')
        if generic_list:
            for item in generic_list:
                item_type = get_generic_connection_type(item)
                if item_type == 'cloud-microsoft-power-automate':
                    power_automate_list.append(item)
        power_automate_created, power_automate_updated = self.sync_microsoft_power_automate(power_automate_list, session)
        if power_automate_created:
            self.created_objects['microsoft_power_automate'] = power_automate_created
        if power_automate_updated:
            self.updated_objects['microsoft_power_automate'] = power_automate_updated

        # Process ElasticSearch connection definitions
        es_created, es_updated = self.sync_es(yaml_config.get('elastic_search', []), session)
        if es_created:
            self.created_objects['elastic_search'] = es_created
        if es_updated:
            self.updated_objects['elastic_search'] = es_updated

        # Process outgoing REST connection definitions
        outgoing_rest_created, outgoing_rest_updated = self.sync_outgoing_rest(yaml_config.get('outgoing_rest', []), session)
        if outgoing_rest_created:
            self.created_objects['outgoing_rest'] = outgoing_rest_created
        if outgoing_rest_updated:
            self.updated_objects['outgoing_rest'] = outgoing_rest_updated

        # Process outgoing SOAP connection definitions
        outgoing_soap_list = yaml_config.get('outgoing_soap') or yaml_config.get('outconn_soap', [])
        outgoing_soap_created, outgoing_soap_updated = self.sync_outgoing_soap(outgoing_soap_list, session)
        if outgoing_soap_created:
            self.created_objects['outgoing_soap'] = outgoing_soap_created
        if outgoing_soap_updated:
            self.updated_objects['outgoing_soap'] = outgoing_soap_updated

        # Process outgoing AS2 connection definitions
        outgoing_as2_created, outgoing_as2_updated = self.sync_outgoing_as2(yaml_config.get('outgoing_as2', []), session)
        if outgoing_as2_created:
            self.created_objects['outgoing_as2'] = outgoing_as2_created
        if outgoing_as2_updated:
            self.updated_objects['outgoing_as2'] = outgoing_as2_updated

        # Process outgoing AS4 connection definitions
        outgoing_as4_created, outgoing_as4_updated = self.sync_outgoing_as4(yaml_config.get('outgoing_as4', []), session)
        if outgoing_as4_created:
            self.created_objects['outgoing_as4'] = outgoing_as4_created
        if outgoing_as4_updated:
            self.updated_objects['outgoing_as4'] = outgoing_as4_updated

        # Process pubsub topic definitions
        pubsub_topic_created, pubsub_topic_updated = self.sync_pubsub_topic(yaml_config.get('pubsub_topic', []), session)
        if pubsub_topic_created:
            self.created_objects['pubsub_topic'] = pubsub_topic_created
        if pubsub_topic_updated:
            self.updated_objects['pubsub_topic'] = pubsub_topic_updated

        # Process pubsub permission definitions
        pubsub_permission_created, pubsub_permission_updated = self.sync_pubsub_permission(yaml_config.get('pubsub_permission', []), session)
        if pubsub_permission_created:
            self.created_objects['pubsub_permission'] = pubsub_permission_created
        if pubsub_permission_updated:
            self.updated_objects['pubsub_permission'] = pubsub_permission_updated

        # Process pubsub subscription definitions
        pubsub_subscription_created, pubsub_subscription_updated = self.sync_pubsub_subscription(yaml_config.get('pubsub_subscription', []), session)
        if pubsub_subscription_created:
            self.created_objects['pubsub_subscription'] = pubsub_subscription_created
        if pubsub_subscription_updated:
            self.updated_objects['pubsub_subscription'] = pubsub_subscription_updated

        # Process OpenAPI channel definitions (depends on REST channels)
        channel_openapi_created, channel_openapi_updated = self.sync_channel_openapi(yaml_config.get('channel_openapi', []), session)
        if channel_openapi_created:
            self.created_objects['channel_openapi'] = channel_openapi_created
        if channel_openapi_updated:
            self.updated_objects['channel_openapi'] = channel_openapi_updated

        # Process alert rule configuration - the storage is the live rule documents
        _, alert_rules_updated = self.sync_alert_rules(yaml_config.get('alert_rules', []), session)
        if alert_rules_updated:
            self.updated_objects['alert_rules'] = alert_rules_updated

        # Process alert notification targets - the storage is the sweep job's extra
        alert_notifications = yaml_config.get('alert_notifications', {})
        alert_notifications_changed = self.sync_alert_notifications(alert_notifications, session)
        if alert_notifications_changed:
            self.updated_objects['alert_notifications'] = [alert_notifications]

        # Process custom connector definitions - each top-level key with the custom_ prefix
        # holds the definitions of one connector type built with the Connector SDK.
        for yaml_key in sorted(yaml_config):
            if yaml_key.startswith(ModuleCtx.Custom_Key_Prefix):
                custom_created, custom_updated = self.sync_custom_connectors(yaml_key, yaml_config[yaml_key], session)
                if custom_created:
                    self.created_objects[yaml_key] = custom_created
                if custom_updated:
                    self.updated_objects[yaml_key] = custom_updated

        logger.info('YAML synchronization completed')

        return self.created_objects, self.updated_objects

# ################################################################################################################################
# ################################################################################################################################
