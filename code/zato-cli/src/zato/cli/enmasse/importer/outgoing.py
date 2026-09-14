# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# This module holds the sync_* wrappers of EnmasseYAMLImporter for outgoing connections. Each one logs, delegates to
# the per-type importer built in EnmasseYAMLImporter.__init__ and copies the *_defs back onto self, and they are called
# from ConfigSync.sync_from_yaml in dependency order. This class is only ever used as a base of EnmasseYAMLImporter.

# stdlib
import logging

# Zato
from zato.cli.enmasse.importers.amqp import OutgoingAMQPImporter
from zato.cli.enmasse.importers.odata import ODataImporter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import anylist, anytuple

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ################################################################################################################################
# ################################################################################################################################

class OutgoingSync:
    """ The sync_* wrappers for outgoing connections, one per connection type.
    """

# ################################################################################################################################

    def sync_odoo(self, odoo_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes Odoo connection definitions from a YAML configuration with the database.
        """
        if not odoo_list:
            return [], []

        count = len(odoo_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} Odoo connection {noun}')

        # Examine each Odoo item
        for idx, item in enumerate(odoo_list):
            logger.info('Odoo connection item %d: %s', idx, item)

        odoo_created, odoo_updated = self.odoo_importer.sync_odoo_definitions(odoo_list, session)

        # Get Odoo definitions from the Odoo importer
        self.odoo_defs = self.odoo_importer.odoo_defs
        logger.info('Processed Odoo connection definitions: created=%d updated=%d', len(odoo_created), len(odoo_updated))

        return odoo_created, odoo_updated

# ################################################################################################################################

    def sync_smtp(self, smtp_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes SMTP connection definitions from a YAML configuration with the database.
        """
        if not smtp_list:
            return [], []

        count = len(smtp_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} SMTP connection {noun}')

        # Examine each SMTP item
        for idx, item in enumerate(smtp_list):
            logger.info('SMTP connection item %d: %s', idx, item)

        smtp_created, smtp_updated = self.smtp_importer.sync_smtp_definitions(smtp_list, session)

        # Get SMTP definitions from the SMTP importer
        self.smtp_defs = self.smtp_importer.smtp_defs
        logger.info('Processed SMTP connection definitions: created=%d updated=%d', len(smtp_created), len(smtp_updated))

        return smtp_created, smtp_updated

# ################################################################################################################################

    def sync_imap(self, imap_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes IMAP connection definitions from a YAML configuration with the database.
        """
        if not imap_list:
            return [], []

        count = len(imap_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} IMAP connection {noun}')

        # Examine each IMAP item
        for idx, item in enumerate(imap_list):
            logger.info('IMAP connection item %d: %s', idx, item)

        imap_created, imap_updated = self.imap_importer.sync_imap_definitions(imap_list, session)

        # Get IMAP definitions from the IMAP importer
        self.imap_defs = self.imap_importer.imap_defs
        logger.info('Processed IMAP connection definitions: created=%d updated=%d', len(imap_created), len(imap_updated))

        return imap_created, imap_updated

# ################################################################################################################################

    def sync_sql(self, sql_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes SQL connection pool definitions from a YAML configuration with the database.
        """
        if not sql_list:
            return [], []

        count = len(sql_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} SQL connection pool {noun}')

        # Examine each SQL connection pool item
        for idx, item in enumerate(sql_list):
            logger.info('SQL connection pool item %d: %s', idx, item)

        sql_created, sql_updated = self.sql_importer.sync_sql_definitions(sql_list, session)

        # Get SQL definitions from the SQL importer
        self.sql_defs = self.sql_importer.sql_definitions
        logger.info('Processed SQL connection pool definitions: created=%d updated=%d', len(sql_created), len(sql_updated))

        return sql_created, sql_updated

# ################################################################################################################################

    def sync_confluence(self, confluence_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes Confluence connection definitions from a YAML configuration with the database.
        """
        if not confluence_list:
            return [], []

        count = len(confluence_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} Confluence connection {noun}')

        # Examine each Confluence connection item
        for idx, item in enumerate(confluence_list):
            logger.info('Confluence connection item %d: %s', idx, item)

        confluence_created, confluence_updated = self.confluence_importer.sync_definitions(confluence_list, session)

        # Get Confluence definitions from the Confluence importer
        self.confluence_defs = self.confluence_importer.connection_defs
        logger.info('Processed Confluence connection definitions: created=%d updated=%d', len(confluence_created), len(confluence_updated))

        return confluence_created, confluence_updated

# ################################################################################################################################

    def sync_jira(self, jira_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes Jira connection definitions from a YAML configuration with the database.
        """
        if not jira_list:
            return [], []

        count = len(jira_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} Jira connection {noun}')

        # Examine each Jira connection item
        for idx, item in enumerate(jira_list):
            logger.info('Jira connection item %d: %s', idx, item)

        jira_created, jira_updated = self.jira_importer.sync_definitions(jira_list, session)

        # Get Jira definitions from the Jira importer
        self.jira_defs = self.jira_importer.connection_defs
        logger.info('Processed Jira connection definitions: created=%d updated=%d', len(jira_created), len(jira_updated))

        return jira_created, jira_updated

# ################################################################################################################################

    def sync_salesforce(self, salesforce_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes Salesforce connection definitions from a YAML configuration with the database.
        """
        if not salesforce_list:
            return [], []

        count = len(salesforce_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} Salesforce connection {noun}')

        # Examine each Salesforce connection item
        for idx, item in enumerate(salesforce_list):
            logger.info('Salesforce connection item %d: %s', idx, item)

        salesforce_created, salesforce_updated = self.salesforce_importer.sync_definitions(salesforce_list, session)

        # Get Salesforce definitions from the Salesforce importer
        self.salesforce_defs = self.salesforce_importer.connection_defs
        logger.info('Processed Salesforce connection definitions: created=%d updated=%d',
            len(salesforce_created), len(salesforce_updated))

        return salesforce_created, salesforce_updated

# ################################################################################################################################

    def sync_ldap(self, ldap_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes LDAP connection definitions from a YAML configuration with the database.
        """
        if not ldap_list:
            return [], []

        count = len(ldap_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} LDAP connection {noun}')

        # Examine each LDAP connection item
        for idx, item in enumerate(ldap_list):
            logger.info('LDAP connection item %d: %s', idx, item)

        ldap_created, ldap_updated = self.ldap_importer.sync_definitions(ldap_list, session)

        # Get LDAP definitions from the LDAP importer
        self.ldap_defs = self.ldap_importer.connection_defs
        logger.info('Processed LDAP connection definitions: created=%d updated=%d', len(ldap_created), len(ldap_updated))

        return ldap_created, ldap_updated

# ################################################################################################################################

    def sync_llm(self, llm_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes LLM connection definitions from a YAML configuration with the database.
        """
        if not llm_list:
            return [], []

        count = len(llm_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} LLM connection {noun}')

        # Examine each LLM connection item
        for idx, item in enumerate(llm_list):
            logger.info('LLM connection item %d: %s', idx, item)

        llm_created, llm_updated = self.llm_importer.sync_definitions(llm_list, session)

        # Get LLM definitions from the LLM importer
        self.llm_defs = self.llm_importer.connection_defs
        logger.info('Processed LLM connection definitions: created=%d updated=%d', len(llm_created), len(llm_updated))

        return llm_created, llm_updated

# ################################################################################################################################

    def sync_outgoing_as2(self, as2_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes outgoing AS2 connection definitions from a YAML configuration with the database.
        """
        if not as2_list:
            return [], []

        count = len(as2_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} outgoing AS2 connection {noun}')

        # Examine each outgoing AS2 connection item
        for idx, item in enumerate(as2_list):
            logger.info('Outgoing AS2 connection item %d: %s', idx, item)

        as2_created, as2_updated = self.as2_importer.sync_definitions(as2_list, session)

        # Get outgoing AS2 definitions from the AS2 importer
        self.outgoing_as2_defs = self.as2_importer.connection_defs
        logger.info('Processed outgoing AS2 connection definitions: created=%d updated=%d', len(as2_created), len(as2_updated))

        return as2_created, as2_updated

# ################################################################################################################################

    def _sync_odata_impl(self, item_list:'list', session:'SASession', importer:'ODataImporter') -> 'tuple':
        """ Synchronizes connection definitions of one OData subtype from a YAML configuration with the database.
        """
        if not item_list:
            return [], []

        label = importer.subtype['label']

        count = len(item_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} {label} connection {noun}')

        # Examine each connection item
        for idx, item in enumerate(item_list):
            logger.info('%s connection item %d: %s', label, idx, item)

        items_created, items_updated = importer.sync_definitions(item_list, session)

        logger.info('Processed %s connection definitions: created=%d updated=%d',
            label, len(items_created), len(items_updated))

        return items_created, items_updated

# ################################################################################################################################

    def sync_odata(self, odata_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes OData connection definitions from a YAML configuration with the database.
        """
        odata_created, odata_updated = self._sync_odata_impl(odata_list, session, self.odata_importer)

        # Get OData definitions from the OData importer
        self.odata_defs = self.odata_importer.connection_defs

        return odata_created, odata_updated

# ################################################################################################################################

    def sync_sap(self, sap_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes SAP connection definitions from a YAML configuration with the database.
        """
        sap_created, sap_updated = self._sync_odata_impl(sap_list, session, self.sap_importer)

        # Get SAP definitions from the SAP importer
        self.sap_defs = self.sap_importer.connection_defs

        return sap_created, sap_updated

# ################################################################################################################################

    def _sync_outgoing_amqp_impl(self, item_list:'list', session:'SASession', importer:'OutgoingAMQPImporter') -> 'tuple':
        """ Synchronizes outgoing connection definitions of one AMQP subtype from a YAML configuration with the database.
        """
        if not item_list:
            return [], []

        items_created, items_updated = importer.sync_connection_definitions(item_list, session)

        return items_created, items_updated

# ################################################################################################################################

    def sync_outgoing_amqp(self, item_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes outgoing AMQP connection definitions from a YAML configuration with the database.
        """
        items_created, items_updated = self._sync_outgoing_amqp_impl(item_list, session, self.outgoing_amqp_importer)
        return items_created, items_updated

# ################################################################################################################################

    def sync_outgoing_azure_service_bus(self, item_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes outgoing Azure Service Bus connection definitions from a YAML configuration with the database.
        """
        items_created, items_updated = self._sync_outgoing_amqp_impl(
            item_list, session, self.outgoing_azure_service_bus_importer)
        return items_created, items_updated

# ################################################################################################################################

    def sync_sftp(self, sftp_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes SFTP connection definitions from a YAML configuration with the database.
        """
        if not sftp_list:
            return [], []

        count = len(sftp_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} SFTP connection {noun}')

        # Examine each SFTP connection item
        for idx, item in enumerate(sftp_list):
            logger.info('SFTP connection item %d: %s', idx, item)

        sftp_created, sftp_updated = self.sftp_importer.sync_definitions(sftp_list, session)

        # Get SFTP definitions from the SFTP importer
        self.sftp_defs = self.sftp_importer.connection_defs
        logger.info('Processed SFTP connection definitions: created=%d updated=%d', len(sftp_created), len(sftp_updated))

        return sftp_created, sftp_updated

# ################################################################################################################################

    def sync_smb(self, smb_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes SMB connection definitions from a YAML configuration with the database.
        """
        if not smb_list:
            return [], []

        count = len(smb_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} SMB connection {noun}')

        # Examine each SMB connection item
        for idx, item in enumerate(smb_list):
            logger.info('SMB connection item %d: %s', idx, item)

        smb_created, smb_updated = self.smb_importer.sync_definitions(smb_list, session)

        # Get SMB definitions from the SMB importer
        self.smb_defs = self.smb_importer.connection_defs
        logger.info('Processed SMB connection definitions: created=%d updated=%d', len(smb_created), len(smb_updated))

        return smb_created, smb_updated

# ################################################################################################################################

    def sync_ftp(self, ftp_list:'anylist', session:'SASession') -> 'anytuple':
        """ Synchronizes FTP connection definitions from a YAML configuration with the database.
        """

        # Our response to produce
        out = ([], [])

        if not ftp_list:
            return out

        count = len(ftp_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} FTP connection {noun}')

        # Examine each FTP connection item.
        for idx, item in enumerate(ftp_list):
            logger.info('FTP connection item %d: %s', idx, item)

        ftp_created, ftp_updated = self.ftp_importer.sync_definitions(ftp_list, session)

        # Get FTP definitions from the FTP importer.
        self.ftp_defs = self.ftp_importer.connection_defs
        logger.info('Processed FTP connection definitions: created=%d updated=%d', len(ftp_created), len(ftp_updated))

        out = (ftp_created, ftp_updated)
        return out

# ################################################################################################################################

    def sync_mongodb(self, mongodb_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes MongoDB connection definitions from a YAML configuration with the database.
        """
        if not mongodb_list:
            return [], []

        count = len(mongodb_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} MongoDB connection {noun}')

        # Examine each MongoDB connection item
        for idx, item in enumerate(mongodb_list):
            logger.info('MongoDB connection item %d: %s', idx, item)

        mongodb_created, mongodb_updated = self.mongodb_importer.sync_definitions(mongodb_list, session)

        # Get MongoDB definitions from the MongoDB importer
        self.mongodb_defs = self.mongodb_importer.connection_defs
        logger.info('Processed MongoDB connection definitions: created=%d updated=%d',
            len(mongodb_created), len(mongodb_updated))

        return mongodb_created, mongodb_updated

# ################################################################################################################################

    def sync_outgoing_mllp(self, outgoing_mllp_list:'list', session:'SASession') -> 'tuple':
        if not outgoing_mllp_list:
            return [], []

        count = len(outgoing_mllp_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} outgoing HL7 MLLP {noun}')

        for idx, item in enumerate(outgoing_mllp_list):
            logger.info('Outgoing HL7 MLLP item %d: %s', idx, item)

        created, updated = self.outgoing_mllp_importer.sync_definitions(outgoing_mllp_list, session)
        self.outgoing_mllp_defs = self.outgoing_mllp_importer.connection_defs

        created_count = len(created)
        updated_count = len(updated)
        logger.info('Processed outgoing HL7 MLLP definitions: created=%d updated=%d', created_count, updated_count)

        return created, updated

# ################################################################################################################################

    def sync_outgoing_fhir(self, outgoing_fhir_list:'list', session:'SASession') -> 'tuple':
        if not outgoing_fhir_list:
            return [], []

        count = len(outgoing_fhir_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} outgoing HL7 FHIR {noun}')

        for idx, item in enumerate(outgoing_fhir_list):
            logger.info('Outgoing HL7 FHIR item %d: %s', idx, item)

        created, updated = self.outgoing_fhir_importer.sync_definitions(outgoing_fhir_list, session)
        self.outgoing_fhir_defs = self.outgoing_fhir_importer.connection_defs

        created_count = len(created)
        updated_count = len(updated)
        logger.info('Processed outgoing HL7 FHIR definitions: created=%d updated=%d', created_count, updated_count)

        return created, updated

# ################################################################################################################################

    def sync_outgoing_ibm_mq(self, outgoing_ibm_mq_list:'list', session:'SASession') -> 'tuple':
        if not outgoing_ibm_mq_list:
            return [], []

        count = len(outgoing_ibm_mq_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} IBM MQ outgoing {noun}')

        for idx, item in enumerate(outgoing_ibm_mq_list):
            logger.info('IBM MQ outgoing item %d: %s', idx, item)

        created, updated = self.outgoing_ibm_mq_importer.sync_definitions(outgoing_ibm_mq_list, session)
        self.outgoing_ibm_mq_defs = self.outgoing_ibm_mq_importer.connection_defs
        logger.info('Processed IBM MQ outgoing definitions: created=%d updated=%d', len(created), len(updated))

        return created, updated

# ################################################################################################################################

    def sync_outgoing_kafka(self, outgoing_kafka_list:'list', session:'SASession') -> 'tuple':
        if not outgoing_kafka_list:
            return [], []

        count = len(outgoing_kafka_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} Kafka outgoing {noun}')

        for idx, item in enumerate(outgoing_kafka_list):
            logger.info('Kafka outgoing item %d: %s', idx, item)

        created, updated = self.outgoing_kafka_importer.sync_definitions(outgoing_kafka_list, session)
        self.outgoing_kafka_defs = self.outgoing_kafka_importer.connection_defs
        logger.info('Processed Kafka outgoing definitions: created=%d updated=%d', len(created), len(updated))

        return created, updated

# ################################################################################################################################

    def sync_outgoing_graphql(self, outgoing_graphql_list:'list', session:'SASession') -> 'tuple':
        if not outgoing_graphql_list:
            return [], []

        count = len(outgoing_graphql_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} GraphQL outgoing {noun}')

        for idx, item in enumerate(outgoing_graphql_list):
            logger.info('GraphQL outgoing item %d: %s', idx, item)

        created, updated = self.outgoing_graphql_importer.sync_definitions(outgoing_graphql_list, session)
        self.outgoing_graphql_defs = self.outgoing_graphql_importer.connection_defs
        logger.info('Processed GraphQL outgoing definitions: created=%d updated=%d', len(created), len(updated))

        return created, updated

# ################################################################################################################################

    def sync_outgoing_grpc(self, outgoing_grpc_list:'list', session:'SASession') -> 'tuple':
        if not outgoing_grpc_list:
            return [], []

        count = len(outgoing_grpc_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} gRPC outgoing {noun}')

        for idx, item in enumerate(outgoing_grpc_list):
            logger.info('gRPC outgoing item %d: %s', idx, item)

        created, updated = self.outgoing_grpc_importer.sync_definitions(outgoing_grpc_list, session)
        self.outgoing_grpc_defs = self.outgoing_grpc_importer.connection_defs
        logger.info('Processed gRPC outgoing definitions: created=%d updated=%d', len(created), len(updated))

        return created, updated

# ################################################################################################################################

    def sync_microsoft_cloud(self, microsoft_cloud_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes Microsoft 365 connection definitions from a YAML configuration with the database.
        """
        if not microsoft_cloud_list:
            return [], []

        count = len(microsoft_cloud_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} Microsoft 365 connection {noun}')

        # Examine each Microsoft 365 connection item
        for idx, item in enumerate(microsoft_cloud_list):
            logger.info('Microsoft 365 connection item %d: %s', idx, item)

        microsoft_cloud_created, microsoft_cloud_updated = self.microsoft_cloud_importer.sync_definitions(
            microsoft_cloud_list, session)

        # Get Microsoft 365 definitions from the Microsoft 365 importer
        self.microsoft_cloud_defs = self.microsoft_cloud_importer.connection_defs
        logger.info('Processed Microsoft 365 connection definitions: created=%d updated=%d',
            len(microsoft_cloud_created), len(microsoft_cloud_updated))

        return microsoft_cloud_created, microsoft_cloud_updated

# ################################################################################################################################

    def sync_microsoft_teams(self, microsoft_teams_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes Microsoft Teams connection definitions from a YAML configuration with the database.
        """
        if not microsoft_teams_list:
            return [], []

        count = len(microsoft_teams_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} Microsoft Teams connection {noun}')

        # Examine each Microsoft Teams connection item
        for idx, item in enumerate(microsoft_teams_list):
            logger.info('Microsoft Teams connection item %d: %s', idx, item)

        microsoft_teams_created, microsoft_teams_updated = self.microsoft_teams_importer.sync_definitions(
            microsoft_teams_list, session)

        # Get Microsoft Teams definitions from the Microsoft Teams importer
        self.microsoft_teams_defs = self.microsoft_teams_importer.connection_defs
        logger.info('Processed Microsoft Teams connection definitions: created=%d updated=%d',
            len(microsoft_teams_created), len(microsoft_teams_updated))

        return microsoft_teams_created, microsoft_teams_updated

# ################################################################################################################################

    def sync_slack(self, slack_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes Slack connection definitions from a YAML configuration with the database.
        """
        if not slack_list:
            return [], []

        count = len(slack_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} Slack connection {noun}')

        # Examine each Slack connection item
        for idx, item in enumerate(slack_list):
            logger.info('Slack connection item %d: %s', idx, item)

        slack_created, slack_updated = self.slack_importer.sync_definitions(slack_list, session)

        # Get Slack definitions from the Slack importer
        self.slack_defs = self.slack_importer.connection_defs
        logger.info('Processed Slack connection definitions: created=%d updated=%d',
            len(slack_created), len(slack_updated))

        return slack_created, slack_updated

# ################################################################################################################################

    def sync_microsoft_fabric(self, microsoft_fabric_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes Microsoft Fabric connection definitions from a YAML configuration with the database.
        """
        if not microsoft_fabric_list:
            return [], []

        count = len(microsoft_fabric_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} Microsoft Fabric connection {noun}')

        # Examine each Microsoft Fabric connection item
        for idx, item in enumerate(microsoft_fabric_list):
            logger.info('Microsoft Fabric connection item %d: %s', idx, item)

        created, updated = self.microsoft_fabric_importer.sync_definitions(microsoft_fabric_list, session)

        # Get Microsoft Fabric definitions from the Microsoft Fabric importer
        self.microsoft_fabric_defs = self.microsoft_fabric_importer.connection_defs
        logger.info('Processed Microsoft Fabric connection definitions: created=%d updated=%d',
            len(created), len(updated))

        return created, updated

# ################################################################################################################################

    def sync_microsoft_power_automate(self, microsoft_power_automate_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes Microsoft Power Automate connection definitions from a YAML configuration with the database.
        """
        if not microsoft_power_automate_list:
            return [], []

        count = len(microsoft_power_automate_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} Microsoft Power Automate connection {noun}')

        # Examine each Microsoft Power Automate connection item
        for idx, item in enumerate(microsoft_power_automate_list):
            logger.info('Microsoft Power Automate connection item %d: %s', idx, item)

        created, updated = self.microsoft_power_automate_importer.sync_definitions(microsoft_power_automate_list, session)

        # Get Microsoft Power Automate definitions from the Microsoft Power Automate importer
        self.microsoft_power_automate_defs = self.microsoft_power_automate_importer.connection_defs
        logger.info('Processed Microsoft Power Automate connection definitions: created=%d updated=%d',
            len(created), len(updated))

        return created, updated

# ################################################################################################################################

    def sync_es(self, es_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes Elasticsearch connection definitions from a YAML configuration with the database.
        """
        if not es_list:
            return [], []

        count = len(es_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} Elasticsearch connection {noun}')

        # Examine each Elasticsearch connection item
        for idx, item in enumerate(es_list):
            logger.info('Elasticsearch connection item %d: %s', idx, item)

        es_created, es_updated = self.es_importer.sync_definitions(es_list, session)

        # Get Elasticsearch definitions from the Elasticsearch importer
        self.es_defs = self.es_importer.connection_defs
        logger.info('Processed Elasticsearch connection definitions: created=%d updated=%d', len(es_created), len(es_updated))

        return es_created, es_updated

# ################################################################################################################################

    def sync_outgoing_rest(self, outgoing_list:'list', session:'SASession') -> 'tuple':
        """Synchronizes outgoing REST connection definitions from a YAML configuration with the database.
        """
        return self.outgoing_rest_importer.sync_outgoing_rest(outgoing_list, session)

# ################################################################################################################################

    def sync_outgoing_soap(self, outgoing_list:'list', session:'SASession') -> 'tuple':
        """Synchronizes outgoing SOAP connection definitions from a YAML configuration with the database.
        """
        return self.outgoing_soap_importer.sync_outgoing_soap(outgoing_list, session)

# ################################################################################################################################

    def sync_outgoing_as4(self, outgoing_list:'list', session:'SASession') -> 'tuple':
        """Synchronizes outgoing AS4 connection definitions from a YAML configuration with the database.
        """
        if not outgoing_list:
            return [], []

        return self.outgoing_as4_importer.sync_outgoing_as4(outgoing_list, session)

# ################################################################################################################################
# ################################################################################################################################
